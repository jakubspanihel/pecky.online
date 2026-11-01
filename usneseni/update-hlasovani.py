#!/usr/bin/env python3
"""Jmenovitá hlasování zastupitelstva pro stránku /usneseni/.

Vezme z archivu usneseni.cz (jednani/archive/*zastupitelstvo*.json,
minutes.agenda_items[].votes[]) u každého přijatého usnesení jména
zastupitelů, kteří hlasovali pro / proti / zdrželi se / nehlasovali, a uloží je
do usneseni/hlasovani.json (klíč = číslo usnesení, např. "UZ-18-4/26").
Jména jsou verbatim ze zápisu. Rada jména neuvádí (na usneseni.cz jen počty).

Navíc uloží návrhy, které při hlasování neprošly (v archivu výsledek „Návrh nebyl
přijat“, bez čísla usnesení), do usneseni/neprijata.json — rada i zastupitelstvo,
u zastupitelstva i se jmény. Hlasování z jednání novějších než archiv (pole
`rejected_vote` v jednani/pecky-jednani.json) načítá přímo stránka.

Použití: python3 usneseni/update-hlasovani.py
Po spuštění: python3 scripts/build.py (stránka data jen načítá, build je nemění).
"""
import glob
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'jednani' / 'scripts'))

KLICE = (('pro', 'pro'), ('proti', 'proti'), ('zdrzel_se', 'zdrzel'), ('nehlasoval', 'nehlasoval'))


def neprijata():
    out = []
    for f in sorted(glob.glob(str(ROOT / 'jednani' / 'archive' / '*.json'))):
        typ = 'Zastupitelstvo' if 'zastupitelstvo' in f else 'Rada'
        d = json.load(open(f, encoding='utf-8'))
        date = d.get('date_iso')
        for ai in ((d.get('minutes') or {}).get('agenda_items') or []):
            for i, v in enumerate(ai.get('votes') or [], 1):
                if (v.get('result_raw') or '').strip() != 'Návrh nebyl přijat' or v.get('adopted_resolution_number'):
                    continue
                rec = {'n': f"NP-{date}-{'ZM' if typ == 'Zastupitelstvo' else 'RM'}-{ai.get('number')}-{i}",
                       'date': date, 'type': typ, 'number': d.get('number'), 'year': d.get('year'),
                       'bod': ai.get('number'), 'item': (ai.get('title_raw') or '').strip(),
                       'pro': (v.get('pro') or {}).get('count', 0),
                       'proti': (v.get('proti') or {}).get('count', 0),
                       'zdrzel': (v.get('zdrzel_se') or {}).get('count', 0)}
                if ai.get('predkladatel'):
                    rec['predkladatel'] = ai['predkladatel']
                names = {dst: (v.get(src) or {}).get('names') for src, dst in KLICE}
                names = {k: x for k, x in names.items() if x}
                if names:
                    rec['jmena'] = names
                out.append(rec)
    (ROOT / 'usneseni' / 'neprijata.json').write_text(
        json.dumps({'meta': {'source': 'jednani/archive (usneseni.cz)', 'count': len(out)},
                    'navrhy': out}, ensure_ascii=False, separators=(',', ':')) + '\n',
        encoding='utf-8')
    print(f'{len(out)} nepřijatých návrhů')


def main():
    out = {}
    for f in sorted(glob.glob(str(ROOT / 'jednani' / 'archive' / '*zastupitelstvo*.json'))):
        d = json.load(open(f, encoding='utf-8'))
        for ai in ((d.get('minutes') or {}).get('agenda_items') or []):
            for v in ai.get('votes') or []:
                n = (v.get('adopted_resolution_number') or '').strip()
                if not n:
                    continue
                rec = {}
                for src, dst in KLICE:
                    names = (v.get(src) or {}).get('names') or []
                    if names:
                        rec[dst] = names
                if rec:
                    out[n] = rec
    # jednání novější než snímek archivu: jména ručně přepsaná ze zápisů na usneseni.cz
    rucne = ROOT / 'usneseni' / 'hlasovani-rucne.json'
    if rucne.exists():
        for n, rec in json.loads(rucne.read_text(encoding='utf-8'))['hlasovani'].items():
            out.setdefault(n, rec)   # archiv má přednost
    (ROOT / 'usneseni' / 'hlasovani.json').write_text(
        json.dumps({'meta': {'source': 'jednani/archive (usneseni.cz)', 'count': len(out)},
                    'hlasovani': out}, ensure_ascii=False, separators=(',', ':')) + '\n',
        encoding='utf-8')
    print(f'{len(out)} usnesení zastupitelstva se jmény')
    neprijata()


if __name__ == '__main__':
    main()
