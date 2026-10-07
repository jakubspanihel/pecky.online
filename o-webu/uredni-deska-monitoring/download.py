#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Stáhne přílohy dokumentů úřední desky do Data/<rok>/<číslo dokumentu>/<soubor>.

Vstup:  prilohy-<rok>.txt  (řádek: <číslo dokumentu>|<soubor>|<soubor>|…)
Výstup: Data/ (v .gitignore) + prilohy-manifest.json (v gitu: velikost, SHA-256, stav).

Použití:  python3 o-webu/uredni-deska-monitoring/download.py [rok …]
Bez argumentu zpracuje všechny prilohy-*.txt. Opakované spuštění už stažené soubory
přeskočí; chybějící/selhané zkusí znovu. Soubory na pecky.cz jdou stáhnout běžným
curl (chráněné proti botům jsou jen HTML stránky, ne /files/).
"""
import glob, hashlib, json, os, re, subprocess, sys, urllib.parse

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, 'Data')
MANIFEST = os.path.join(BASE, 'prilohy-manifest.json')
URL = 'https://pecky.cz/files/pecky/attachments/{id}/{name}'
UA = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 '
      '(KHTML, like Gecko) Version/17.0 Safari/605.1.15')


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def fetch(url, dest):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    tmp = dest + '.part'
    r = subprocess.run(['curl', '-sSL', '-f', '--max-time', '180', '-A', UA, '-o', tmp, url],
                       capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(tmp) or os.path.getsize(tmp) == 0:
        if os.path.exists(tmp):
            os.remove(tmp)
        return False, (r.stderr.strip() or f'curl {r.returncode}')[:200]
    os.replace(tmp, dest)
    return True, ''


def main():
    years = sys.argv[1:]
    man = json.load(open(MANIFEST, encoding='utf-8')) if os.path.exists(MANIFEST) else {}
    files = sorted(glob.glob(os.path.join(BASE, 'prilohy-*.txt')))
    if years:
        files = [f for f in files if re.search(r'prilohy-(\d{4})\.txt', f).group(1) in years]
    new = skip = bad = 0
    for pf in files:
        year = re.search(r'prilohy-(\d{4})\.txt', pf).group(1)
        for line in open(pf, encoding='utf-8'):
            line = line.rstrip('\n')
            if not line or line.startswith('#'):
                continue
            did, *names = line.split('|')
            for name in names:
                rel = f'{year}/{did}/{name}'
                dest = os.path.join(DATA, year, did, name)
                if os.path.exists(dest) and os.path.getsize(dest) > 0:
                    if rel not in man:
                        man[rel] = {'size': os.path.getsize(dest), 'sha256': sha256(dest), 'status': 'ok'}
                    skip += 1
                    continue
                url = URL.format(id=did, name=urllib.parse.quote(name, safe='().-_'))
                ok, err = fetch(url, dest)
                if ok:
                    man[rel] = {'size': os.path.getsize(dest), 'sha256': sha256(dest), 'status': 'ok'}
                    new += 1
                else:
                    man[rel] = {'status': 'chyba', 'error': err}
                    bad += 1
                    print('CHYBA', rel, err)
    with open(MANIFEST, 'w', encoding='utf-8') as f:
        json.dump(dict(sorted(man.items())), f, ensure_ascii=False, indent=1)
        f.write('\n')
    tot = sum(v.get('size', 0) for v in man.values())
    print(f'nově {new}, přeskočeno {skip}, chyb {bad}; v manifestu {len(man)} souborů, {tot / 1e6:.1f} MB')


if __name__ == '__main__':
    main()
