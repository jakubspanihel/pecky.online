#!/usr/bin/env python3
"""Ke každé parcele z jednani/parcely-pozemky.json dohledá číslo jejího listu vlastnictví (LV)
přes REST API KN ČÚZK (https://api-kn.cuzk.gov.cz, ApiKey v souboru .katastr-api-key, limit
500 volání za den). Výstup jednani/parcely-lv.json se používá na stránce PečkyBot k tomu, aby
zmínka „LV 228“ ukázala na konkrétní parcely (API samo parcely podle LV nevrací, proto jen parcely,
které web zná z usnesení). Je inkrementální: znovu se volají jen nové parcely.

Spuštění z kořene repa:  python3 jednani/scripts/parcely-lv.py [--max N]
"""
import json
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SRC = ROOT / 'jednani/parcely-pozemky.json'
OUT = ROOT / 'jednani/parcely-lv.json'
API = 'https://api-kn.cuzk.gov.cz/api/v1/Parcely/{}'


def fetch(rid, key):
    req = urllib.request.Request(API.format(rid), headers={'ApiKey': key, 'Accept': 'application/json'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def main():
    key = (ROOT / '.katastr-api-key').read_text().strip()
    parcely = json.loads(SRC.read_text(encoding='utf-8'))['parcely']
    old = json.loads(OUT.read_text(encoding='utf-8')) if OUT.exists() else {}
    cache = old.get('parcely', {})
    limit = int(sys.argv[sys.argv.index('--max') + 1]) if '--max' in sys.argv else 400
    todo = [(k, rid) for k, rid in parcely.items() if k not in cache or cache[k].get('rid') != rid]
    print(f'parcel celkem {len(parcely)}, k dohledání {len(todo)} (max {limit} volání)', file=sys.stderr)
    done = 0
    for k, rid in todo[:limit]:
        try:
            d = fetch(rid, key).get('data') or {}
        except Exception as e:  # 404 apod. — zapsat jako bez LV, ať se příště nevolá znovu zbytečně
            print(f'  {k}: {e}', file=sys.stderr)
            cache[k] = {'rid': rid, 'lv': None}
            continue
        lv = d.get('lv') or {}
        cache[k] = {'rid': rid, 'lv': lv.get('cislo'), 'lv_katastr': (lv.get('katastralniUzemi') or {}).get('nazev')}
        done += 1
        time.sleep(0.15)
    cache = {k: cache[k] for k in sorted(cache) if k in parcely}
    OUT.write_text(json.dumps({
        '_comment': 'Parcela (katastr|číslo) -> číslo LV z REST API KN ČÚZK. Generuje jednani/scripts/parcely-lv.py; '
                    'LV je jednoznačné jen spolu s katastrálním územím (lv_katastr).',
        'count': len(cache),
        'parcely': cache,
    }, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(f'dohledáno {done}, v souboru {len(cache)}', file=sys.stderr)


if __name__ == '__main__':
    main()
