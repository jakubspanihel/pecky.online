#!/usr/bin/env python3
"""Doplní do pecky-jednani.json jmenovité hlasování zastupitelstva (`resolutions[].vote_names`).

Zdroj: velký archiv `jednani/archive/*zastupitelstvo*.json` — u každého usnesení
`vote.pro/proti/zdrzel_se.names`, `nehlasoval` z `minutes.agenda_items[].votes[]`
(spárováno podle `adopted_resolution_number`). Jednání, která v archivu nejsou
(novější než snímek), se doplňují ručně ze stránky zápisu — viz README.md.

Tvar: {"pro": [...], "proti": [...], "zdrzel": [...], "nehlasoval": [...]}.
Počty jmen musí sedět s `pro`/`proti`/`zdrzel` u usnesení, jinak se usnesení přeskočí
a vypíše. Spuštění je idempotentní.
"""
import glob
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'pecky-jednani.json'


def names(v, key):
    x = (v or {}).get(key) or {}
    return list(x.get('names') or []), x.get('count')


def main():
    raw = SRC.read_text(encoding='utf-8')
    indent = 2 if raw.startswith('{\n  ') else 1
    data = json.loads(raw)
    zm = {m['date']: m for m in data['meetings'] if m['type'] == 'Zastupitelstvo'}
    done = skipped = 0
    for f in sorted(glob.glob(str(ROOT / 'archive' / '*zastupitelstvo*.json'))):
        a = json.load(open(f, encoding='utf-8'))
        a = a['meetings'][0] if 'meetings' in a else a
        m = zm.get(a['date_iso'])
        if not m:
            continue
        neh = {}
        for ag in (a.get('minutes') or {}).get('agenda_items') or []:
            for v in ag.get('votes') or []:
                n = v.get('adopted_resolution_number')
                if n:
                    neh[n] = names(v, 'nehlasoval')[0]
        items = {it['number_raw']: it for it in (a.get('resolutions') or {}).get('items') or []}
        for r in m['resolutions']:
            it = items.get(r['n'])
            if not it:
                skipped += 1
                print('bez zdroje:', m['date'], r['n'])
                continue
            v = it['vote']
            pro, cp = names(v, 'pro')
            proti, cx = names(v, 'proti')
            zd, cz = names(v, 'zdrzel_se')
            if (len(pro), len(proti), len(zd)) != (r['pro'], r['proti'], r['zdrzel']) or \
               (cp, cx, cz) != (r['pro'], r['proti'], r['zdrzel']):
                skipped += 1
                print('nesedí počty:', m['date'], r['n'], len(pro), len(proti), len(zd), 'vs', r['pro'], r['proti'], r['zdrzel'])
                continue
            r['vote_names'] = {'pro': pro, 'proti': proti, 'zdrzel': zd, 'nehlasoval': neh.get(r['n'], [])}
            done += 1
    SRC.write_text(json.dumps(data, ensure_ascii=False, indent=indent), encoding='utf-8')
    print(f'doplněno {done}, přeskočeno {skipped}')
    chybi = [(m['date'], r['n']) for m in zm.values() for r in m['resolutions'] if 'vote_names' not in r]
    print('bez jmen zbývá:', len(chybi), sorted({d for d, _ in chybi}))


if __name__ == '__main__':
    sys.exit(main())
