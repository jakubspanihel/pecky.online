#!/usr/bin/env python3
"""Rozdělení velkého snímku usneseni.cz (archive-*.json) na jeden soubor
na jednání a zpět.

Struktura snímku: {export, meetings[], validation, anomalies[]}. Po rozdělení:

  jednani/archive/
    index.json                         export, validation, anomalies + seznam jednání
                                       (pořadí = pořadí v původním souboru)
    RRRR-MM-DD-{rada|zastupitelstvo}-{uuid8}.json   jedno jednání, beze změny obsahu

Použití:
  python3 jednani/scripts/archive_split.py split  jednani/archive-2026-08-04.json jednani/archive
  python3 jednani/scripts/archive_split.py join   jednani/archive vystup.json
  python3 jednani/scripts/archive_split.py verify jednani/archive-2026-08-04.json jednani/archive

Původní jediný soubor `archive-2026-08-04.json` je v historii gitu.
`verify` poskládá složku zpět a porovná ji s původním souborem (obsah 1:1).
Jiné skripty načítají archiv přes `load_archive(cesta)` — ta umí soubor
i složku, takže se jim cesta v příkazu dá nechat stejná nebo nahradit složkou.
"""
import json
import sys
from pathlib import Path

TYPY = {'rada': 'rada', 'zastupitelstvo': 'zastupitelstvo'}


def _typ(m):
    raw = (m.get('body_type_raw') or '').lower()
    for k in TYPY:
        if k in raw:
            return k
    return 'jine'


def nazev_souboru(m):
    return f"{m['date_iso']}-{_typ(m)}-{m['uuid'][:8]}.json"


def _dump(obj, path):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')


def split(src, dst):
    d = json.load(open(src, encoding='utf-8'))
    dst = Path(dst)
    dst.mkdir(parents=True, exist_ok=True)
    seznam = []
    for m in d['meetings']:
        jm = nazev_souboru(m)
        if (dst / jm).exists():
            raise SystemExit(f'CHYBA: soubor {jm} už existuje (dvě jednání se stejným datem/typem/uuid?).')
        _dump(m, dst / jm)
        seznam.append({'file': jm, 'uuid': m['uuid'], 'date': m['date_iso'], 'type': _typ(m)})
    idx = {k: v for k, v in d.items() if k != 'meetings'}
    idx['meetings'] = seznam
    _dump(idx, dst / 'index.json')
    print(f'Rozděleno: {len(seznam)} jednání -> {dst}/')


def load_archive(cesta):
    """Načte archiv ze souboru (původní tvar) nebo ze složky (po rozdělení)."""
    p = Path(cesta)
    if p.is_file():
        return json.load(open(p, encoding='utf-8'))
    idx = json.load(open(p / 'index.json', encoding='utf-8'))
    out = {k: v for k, v in idx.items() if k != 'meetings'}
    out['meetings'] = [json.load(open(p / x['file'], encoding='utf-8')) for x in idx['meetings']]
    # původní pořadí klíčů: export, meetings, validation, anomalies
    return {k: out[k] for k in ('export', 'meetings', 'validation', 'anomalies') if k in out} | {
        k: v for k, v in out.items() if k not in ('export', 'meetings', 'validation', 'anomalies')}


def join(src, dst):
    _dump(load_archive(src), dst)
    print(f'Složeno -> {dst}')


def verify(orig, folder):
    a = json.load(open(orig, encoding='utf-8'))
    b = load_archive(folder)
    ok = (json.dumps(a, sort_keys=True, ensure_ascii=False) == json.dumps(b, sort_keys=True, ensure_ascii=False)
          and [m['uuid'] for m in a['meetings']] == [m['uuid'] for m in b['meetings']])
    print('SHODA 1:1' if ok else 'ROZDÍL')
    if not ok:
        sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) != 4 or sys.argv[1] not in ('split', 'join', 'verify'):
        raise SystemExit(__doc__)
    {'split': split, 'join': join, 'verify': verify}[sys.argv[1]](sys.argv[2], sys.argv[3])
