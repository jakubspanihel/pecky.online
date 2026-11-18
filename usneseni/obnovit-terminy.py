#!/usr/bin/env python3
"""Obnova „Zodpovídá / Termín / Ukončeno“ u otevřených usnesení (usneseni/terminy.json).

Otevřené usnesení = termín jiný než „IHNED“ a zatím bez data ukončení. U nich se při každé kontrole Jednání
znovu stáhne detail z usneseni.cz (údaj „Ukončeno“ může přibýt kdykoli, termín i osoba se mohou změnit).
Ukončená usnesení se znovu nestahují.

  python3 usneseni/obnovit-terminy.py seznam     # otevřená usnesení jako „číslo:id:mod“ pro usneseni/terminy-capture.js
  python3 usneseni/obnovit-terminy.py import [složka]   # zpracuje ~/Downloads/terminy-capture-*.json, vypíše změny

import zapíše stažené údaje do usneseni/terminy-stazene.json (mají přednost před archivem), přegeneruje
usneseni/terminy.json a smaže zpracované soubory. Postup: usneseni/README.md → „Zodpovídá, termín, ukončeno“.
"""
import glob
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TERM = ROOT / 'usneseni' / 'terminy.json'
STAZENE = ROOT / 'usneseni' / 'terminy-stazene.json'


def _iso(raw):
    m = re.search(r'(\d{1,2})\.\s*(\d{1,2})\.\s*(\d{4})', raw or '')
    return f'{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}' if m else None


def otevrena():
    terminy = json.loads(TERM.read_text(encoding='utf-8'))['terminy']
    d = json.loads((ROOT / 'jednani' / 'pecky-jednani.json').read_text(encoding='utf-8'))
    out = []
    for m in d['meetings']:
        if m['type'] not in ('Rada', 'Zastupitelstvo'):
            continue
        for r in m.get('resolutions') or []:
            t = terminy.get(r['n'])
            u = re.search(r'/usneseni/(\d+)\?mod=(\w+)', r.get('url') or '')
            if u and (not t or (not t.get('i') and not t.get('u'))):
                out.append((r['n'], u.group(1), u.group(2)))
    return out


def pole(f):
    rec = {}
    if (f.get('Zodpovídá') or '').strip():
        rec['z'] = f['Zodpovídá'].strip()
    tr = (f.get('Termín') or '').strip()
    if _iso(tr):
        rec['t'] = _iso(tr)
        if tr.upper().startswith('IHNED'):
            rec['i'] = 1
    if _iso(f.get('Ukončeno')):
        rec['u'] = _iso(f['Ukončeno'])
    return rec


def importovat(slozka):
    soubory = sorted(glob.glob(str(Path(slozka).expanduser() / 'terminy-capture-*.json')))
    if not soubory:
        sys.exit(f'Ve složce {slozka} není žádný terminy-capture-*.json')
    stare = json.loads(TERM.read_text(encoding='utf-8'))['terminy']
    stazene = json.loads(STAZENE.read_text(encoding='utf-8'))['terminy'] if STAZENE.exists() else {}
    dnes = str(date.today())
    zmeny, beze, zastaveno = [], 0, []
    for f in soubory:
        d = json.load(open(f, encoding='utf-8'))
        if d.get('stopped'):
            zastaveno.append(d['stopped'])
        for it in d['items']:
            n, fields = it['n'], it['fields']
            if (fields.get('Číslo usnesení') or n).strip().upper() != n.upper():
                print(f'POZOR: {n} – detail má číslo {fields.get("Číslo usnesení")}, přeskočeno')
                continue
            novy = pole(fields)
            puvodni = stare.get(n, {})
            if novy != puvodni:
                for k, nm in (('z', 'zodpovídá'), ('t', 'termín'), ('u', 'ukončeno')):
                    if novy.get(k) != puvodni.get(k):
                        zmeny.append(f'{n}: {nm} {puvodni.get(k) or "–"} → {novy.get(k) or "–"}')
            else:
                beze += 1
            novy['s'] = dnes
            stazene[n] = novy
    STAZENE.write_text(json.dumps({'meta': {'note': 'Údaje stažené z detailu usnesení na usneseni.cz (s = datum stažení). '
                                            'Mají přednost před archivem jednani/archive.'}, 'terminy': stazene},
                                  ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    for f in soubory:
        Path(f).unlink()
    subprocess.run([sys.executable, str(ROOT / 'usneseni' / 'update-hlasovani.py')], check=True, stdout=subprocess.DEVNULL)
    print(f'Zpracováno {len(soubory)} souborů; beze změny {beze}, změn {len(zmeny)}:')
    for z in zmeny:
        print('  ' + z)
    if zastaveno:
        print('ZASTAVENO: ' + '; '.join(zastaveno) + ' – zbytek stáhnout při dalším běhu')


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'seznam':
        o = otevrena()
        print(len(o), 'otevřených usnesení', file=sys.stderr)
        print(json.dumps([f'{n}:{i}:{m}' for n, i, m in o], ensure_ascii=False))
    elif len(sys.argv) > 1 and sys.argv[1] == 'import':
        importovat(sys.argv[2] if len(sys.argv) > 2 else '~/Downloads')
    else:
        sys.exit(__doc__)
