#!/usr/bin/env python3
"""
Kontrola odkazů na doklady u nadcházejících akcí (kalendar/akce.json).

Odkaz, na který vede karta akce v Kalendáři, je `evidence[0].url`. Facebook
i jiné zdroje ho umí smazat, nahradit novým příspěvkem nebo omezit — odkaz pak
visí v datech dál a nikdo si toho nevšimne (stalo se 21. 10. 2026 u plakátu
„Program KD Pečky 9–12/2026“, 50 akcí). Tenhle skript je součástí týdenní
kontroly Kalendáře (kalendar/README.md, krok 3d).

Co dělá:
- vezme unikátní `evidence[0].url` akcí s dnešním nebo pozdějším datem
  (`date_end`, je-li) a u každého uvede, kolik akcí na něj ukazuje,
- běžné weby (ne Facebook/Instagram) zkontroluje HTTP požadavkem
  (kód 4xx/5xx nebo výpadek = PROBLÉM),
- Facebook a Instagram vypíše jako seznam k otevření v claude-in-chrome:
  tam se HTTP kontrola nedá použít (vrací 200 i pro nedostupný obsah) a ověřuje
  se podle textu stránky, viz kalendar/README.md, krok 3d.

Použití:
    python3 kalendar/scripts/kontrola-odkazu-dokladu.py          # vše
    python3 kalendar/scripts/kontrola-odkazu-dokladu.py --json   # seznam FB/IG odkazů jako JSON
Kód výstupu 1, nalezl-li PROBLÉM u běžných webů.
"""
import json
import sys
import urllib.request
import urllib.error
from collections import OrderedDict
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
AKCE = ROOT / 'kalendar' / 'akce.json'
SOCIAL = ('facebook.com', 'instagram.com', 'fb.com', 'fb.me')
UA = 'Mozilla/5.0 (pecky.online kontrola odkazu)'


def je_social(url):
    host = urlparse(url).netloc.lower().removeprefix('www.')
    return any(host == s or host.endswith('.' + s) for s in SOCIAL)


def nacti_odkazy():
    data = json.loads(AKCE.read_text(encoding='utf-8'))
    akce = data['events'] if isinstance(data, dict) else data
    dnes = date.today().isoformat()
    odkazy = OrderedDict()
    for e in akce:
        if (e.get('date_end') or e['date']) < dnes:
            continue
        ev = e.get('evidence') or []
        url = ev[0].get('url') if ev else None
        if not url or not url.startswith('http'):
            continue
        odkazy.setdefault(url, []).append(f'{e["date"]} {e["title"]}')
    return odkazy


def zkontroluj_http(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, None
    except urllib.error.HTTPError as ex:
        return ex.code, str(ex)
    except Exception as ex:  # výpadek DNS, timeout, certifikát …
        return None, str(ex)


def main():
    odkazy = nacti_odkazy()
    soc = [(u, a) for u, a in odkazy.items() if je_social(u)]
    web = [(u, a) for u, a in odkazy.items() if not je_social(u)]
    if '--json' in sys.argv:
        print(json.dumps([{'url': u, 'akce': a} for u, a in soc], ensure_ascii=False, indent=1))
        return 0
    problemy = 0
    print(f'Nadcházející akce: {sum(len(a) for a in odkazy.values())}, unikátních odkazů na doklad: {len(odkazy)}'
          f' (web {len(web)}, Facebook/Instagram {len(soc)})\n')
    print('== Běžné weby (HTTP)')
    for url, akce in web:
        kod, chyba = zkontroluj_http(url)
        ok = kod is not None and kod < 400
        problemy += not ok
        print(f'  {"OK     " if ok else "PROBLÉM"} {kod or "—"}  {url}  ({len(akce)} akcí)' + ('' if ok else f'  {chyba}'))
    if not web:
        print('  (žádné)')
    print('\n== Facebook / Instagram — otevřít v claude-in-chrome a ověřit podle textu stránky')
    for url, akce in soc:
        print(f'  {url}  ({len(akce)} akcí, např. {akce[0]})')
    if not soc:
        print('  (žádné)')
    print(f'\nPROBLÉMY u běžných webů: {problemy}')
    return 1 if problemy else 0


if __name__ == '__main__':
    sys.exit(main())
