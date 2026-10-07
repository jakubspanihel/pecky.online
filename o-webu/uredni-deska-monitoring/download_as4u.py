#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Stáhne přílohy dokumentů ze starého webu města (pecky.as4u.cz) do
Data/<rok>/as4u-<detail_claim>/<soubor> a doplní prilohy-manifest.json.

Vstup:  as4u-<rok>.txt (řádek: <detail_claim>|<vyvěšeno>|<název>)
Postup: u každého dokumentu stáhne detail (HTML, běžný curl), vyčte odkazy
        https://pecky.as4u.cz/filemanager/files/file.php?file=<id>, soubor stáhne
        a pojmenuje podle hlavičky Content-Disposition (jinak podle textu odkazu).
Použití: python3 o-webu/uredni-deska-monitoring/download_as4u.py [rok …]
Opakované spuštění už zpracované dokumenty přeskočí (manifest: klíč
"<rok>/as4u-<id>" = seznam souborů). Starý web se od března 2026 neaktualizuje.
"""
import glob, hashlib, html, json, os, re, subprocess, sys, threading
from concurrent.futures import ThreadPoolExecutor

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, 'Data')
MANIFEST = os.path.join(BASE, 'prilohy-manifest.json')
DETAIL = ('https://pecky.as4u.cz/redakce/index.php?lanG=cs&clanek=106922&slozka=106925'
          '&detail_claim={id}')
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15'
LOCK = threading.Lock()


def curl(url, out=None, timeout=120):
    cmd = ['curl', '-sSL', '-f', '--max-time', str(timeout), '-A', UA, '-D', '-']
    cmd += ['-o', out or '-', url]
    return subprocess.run(cmd, capture_output=True)


def safe(name):
    name = re.sub(r'[\\/:*?"<>|\x00-\x1f]', '_', name).strip(' .') or 'soubor'
    return name[:150]


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()


def doc_files(did):
    r = curl(DETAIL.format(id=did), timeout=60)
    if r.returncode != 0:
        return None, f'detail: curl {r.returncode}'
    raw = r.stdout
    start = max(raw.rfind(b'\r\nHTTP/') + 2, 0)  # poslední blok hlaviček (po přesměrování)
    body = raw[start:].split(b'\r\n\r\n', 1)[-1].decode('utf-8', 'replace')
    out = []
    for m in re.finditer(r'<a href="https://pecky\.as4u\.cz/filemanager/files/file\.php\?file=(\d+)"[^>]*title="([^"]*)"[^>]*>(.*?)</a>', body, flags=re.S):
        text = html.unescape(re.sub(r'<[^>]+>', '', m.group(3))).strip()
        out.append((m.group(1), html.unescape(m.group(2)), re.sub(r'\s+', ' ', text)))
    return out, ''


def one(job):
    year, did = job
    key = f'{year}/as4u-{did}'
    files, err = doc_files(did)
    if files is None:
        return key, {'status': 'chyba', 'error': err}
    res, used = [], set()
    for fid, title, text in files:
        tmp = os.path.join(DATA, year, f'as4u-{did}', f'.{fid}.part')
        os.makedirs(os.path.dirname(tmp), exist_ok=True)
        r = curl(f'https://pecky.as4u.cz/filemanager/files/file.php?file={fid}', out=tmp, timeout=300)
        if r.returncode != 0 or not os.path.exists(tmp) or os.path.getsize(tmp) == 0:
            if os.path.exists(tmp):
                os.remove(tmp)
            res.append({'file_id': fid, 'status': 'chyba', 'error': f'curl {r.returncode}'})
            continue
        hdr = r.stdout.decode('latin-1')
        m = re.search(r'(?im)^content-filename:\s*(.+?)\s*$', hdr) or re.search(r'(?im)^content-disposition:.*filename=(.+?)\s*$', hdr)
        name = safe(m.group(1).strip('"') if m else (text or f'soubor-{fid}'))
        if name in used:
            name = f'{fid}-{name}'
        used.add(name)
        dest = os.path.join(DATA, year, f'as4u-{did}', name)
        os.replace(tmp, dest)
        res.append({'file_id': fid, 'name': name, 'size': os.path.getsize(dest), 'sha256': sha256(dest), 'status': 'ok'})
    return key, {'files': res, 'status': 'ok' if all(x['status'] == 'ok' for x in res) else 'částečně'}


def main():
    years = sys.argv[1:]
    man = json.load(open(MANIFEST, encoding='utf-8')) if os.path.exists(MANIFEST) else {}
    jobs = []
    for f in sorted(glob.glob(os.path.join(BASE, 'as4u-????.txt'))):
        y = re.search(r'as4u-(\d{4})\.txt', f).group(1)
        if years and y not in years:
            continue
        for l in open(f, encoding='utf-8'):
            if l.strip() and not l.startswith('#'):
                did = l.split('|')[0]
                if man.get(f'{y}/as4u-{did}', {}).get('status') != 'ok':
                    jobs.append((y, did))
    print(f'k zpracování: {len(jobs)} dokumentů', flush=True)
    done = 0
    with ThreadPoolExecutor(max_workers=4) as ex:
        for key, val in ex.map(one, jobs):
            with LOCK:
                man[key] = val
                done += 1
                if done % 25 == 0 or done == len(jobs):
                    with open(MANIFEST, 'w', encoding='utf-8') as f:
                        json.dump(dict(sorted(man.items())), f, ensure_ascii=False, indent=1)
                        f.write('\n')
                    print(f'{done}/{len(jobs)}', flush=True)
    nf = sum(len(v.get('files', [])) for k, v in man.items() if 'as4u-' in k)
    bad = [k for k, v in man.items() if v.get('status') != 'ok']
    size = sum(x.get('size', 0) for v in man.values() for x in v.get('files', []) if isinstance(x, dict))
    print(f'hotovo: as4u dokumentů {sum(1 for k in man if "as4u-" in k)}, souborů {nf}, {size/1e6:.0f} MB, nedokončených {len(bad)}')
    for k in bad[:20]:
        print('  ', k, man[k].get('error') or man[k].get('status'))


if __name__ == '__main__':
    main()
