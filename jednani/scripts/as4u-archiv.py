#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Archiv zápisů RM a usnesení ZM ze starého webu pecky.as4u.cz (2013 – 4/2021).

Stáhne obě stránky archivu
  - https://pecky.as4u.cz/cs/mesto/rada-mesta/archiv-zapisu-rm.html
  - https://pecky.as4u.cz/cs/mesto/zastupitelstvo-mesta/archiv-zapisu-jednani-zm.html
a PDF jednání, která ještě nejsou v pecky-jednani.json ani v noviny-jednani.json,
uloží do jednani/Data/as4u-cache/<id>.pdf (Data/ je v .gitignore), vytěží text
(pdftotext, bez textové vrstvy OCR tesseract) a zapíše jednani/as4u-archiv.json.
Ten pak načítá jednani/scripts/starsi-jednani.py a doplní jím mezery ve starších
jednáních (jednání, která už starsi-jednani.json z úřední desky má, nechá být).

Použití: python3 jednani/scripts/as4u-archiv.py   (z kořene repa)
"""
import html, json, os, re, shutil, subprocess, sys, tempfile, urllib.request
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
J = os.path.join(ROOT, 'jednani')
CACHE = os.path.join(J, 'Data', 'as4u-cache')
OUT = os.path.join(J, 'as4u-archiv.json')
PAGES = [('Rada', 'https://pecky.as4u.cz/cs/mesto/rada-mesta/archiv-zapisu-rm.html'),
         ('Zastupitelstvo', 'https://pecky.as4u.cz/cs/mesto/zastupitelstvo-mesta/archiv-zapisu-jednani-zm.html')]
SOURCE = 'archiv zápisů na starém webu města (pecky.as4u.cz)'
RX_LINK = re.compile(r'<a[^>]*href="([^"]*filemanager/files/[^"]+)"[^>]*>(.*?)</a>', re.S)
RX_DATE = re.compile(r'(\d{1,2})\s*\.\s*(\d{1,2})\s*\.\s*(\d{4})')
RX_DATE_TXT = re.compile(r'konan\w+\s+dne:?\s*(\d{1,2})\s*\.\s*(\d{1,2}|\w+)\s*\.?\s*(\d{4})', re.I)
RX_NUM = re.compile(r'č\.?\s*(\d+)\s*/\s*(\d{4})')
MONTHS = {m: i + 1 for i, m in enumerate(['ledna', 'února', 'března', 'dubna', 'května', 'června', 'července',
                                           'srpna', 'září', 'října', 'listopadu', 'prosince'])}


def get(url, binary=False):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    b = urllib.request.urlopen(req, timeout=90).read()
    return b if binary else b.decode('utf-8', 'replace')


def iso(d, m, y):
    return f'{int(y):04d}-{int(m):02d}-{int(d):02d}'


def text_date(text):
    m = RX_DATE_TXT.search(text)
    if not m:
        return None
    d, mo, y = m.groups()
    if mo.isdigit():
        return iso(d, mo, y)
    mo = MONTHS.get(mo.lower().rstrip('.')) or MONTHS.get(mo.lower())
    return iso(d, mo, y) if mo else None


def pdf_text(path):
    t = subprocess.run(['pdftotext', '-layout', path, '-'], capture_output=True, text=True).stdout
    if len(t.strip()) >= 100:
        return t, False
    tmp = tempfile.mkdtemp(prefix='ocr_')
    try:
        subprocess.run(['pdftoppm', '-r', '200', '-gray', '-png', '-l', '40', path, os.path.join(tmp, 'p')], timeout=300)
        out = []
        for f in sorted(os.listdir(tmp)):
            r = subprocess.run(['tesseract', os.path.join(tmp, f), '-', '-l', 'ces'], capture_output=True, text=True)
            out.append(r.stdout)
        return '\n\f'.join(out), True
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def existing_dates():
    have = {'Rada': set(), 'Zastupitelstvo': set()}
    for f in ('pecky-jednani.json', 'noviny-jednani.json', 'starsi-jednani.json'):
        p = os.path.join(J, f)
        if not os.path.exists(p):
            continue
        d = json.load(open(p, encoding='utf-8'))
        for m in (d['meetings'] if isinstance(d, dict) else d):
            if m.get('source') == SOURCE:
                continue   # vlastní záznamy z minulého běhu
            have[m['type']].add(m['date'])
    return have


def main():
    os.makedirs(CACHE, exist_ok=True)
    have = existing_dates()
    out, seen = [], {}
    for typ, url in PAGES:
        page = get(url)
        for href, label in RX_LINK.findall(page):
            label = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', html.unescape(label))).strip()
            fid = href.rsplit('/', 1)[-1].rsplit('.', 1)[0]
            if not label.lower().startswith(('usnesení', 'usneseni', 'zápis', 'zapis')) and typ == 'Zastupitelstvo' \
                    and not RX_NUM.search(label):
                print('! přeskočeno (není jednání):', label)
                continue
            d = None
            if typ == 'Rada':
                m = RX_DATE.search(label)
                d = iso(m[1], m[2], m[3]) if m else None
                # datum v odkazu bývá datum vyvěšení; pokud se liší od data v textu, platí text
                if d and d in have[typ]:
                    continue
            dst = os.path.join(CACHE, fid + '.pdf')
            if not os.path.exists(dst):
                open(dst, 'wb').write(get(urllib.request.urljoin(url, href), True))
            text, ocr = pdf_text(dst)
            td = text_date(text)
            if not d or (typ == 'Rada' and td and td != d):
                d = td or d
            if not d:
                print('! bez data:', typ, label, href)
                continue
            if d in have[typ] or (typ, d) in seen:
                continue
            m = RX_NUM.search(label)
            num = int(m[1]) if m and typ == 'Zastupitelstvo' else None
            lab = (f'ZM {num}/{d[:4]} ({d})' if num else f'ZM ({d})') if typ == 'Zastupitelstvo' else f'Rada ({d})'
            rec = {'type': typ, 'date': d, 'number': num, 'label_hint': lab, 'doc_title': label,
                   'url': urllib.request.urljoin(url, href), 'cache': f'Data/as4u-cache/{fid}.pdf', 'ocr': ocr,
                   'text': re.sub(r'[ \t]{3,}', '  ', re.sub(r'\n{3,}', '\n\n', text.replace('\f', '\n'))).strip()}
            seen[(typ, d)] = rec
            out.append(rec)
    out.sort(key=lambda r: r['date'], reverse=True)
    meta = {'updated': date.today().isoformat(), 'source': SOURCE,
            'counts': {t: sum(1 for r in out if r['type'] == t) for t in ('Rada', 'Zastupitelstvo')}}
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump({'meta': meta, 'meetings': out}, f, ensure_ascii=False, indent=1)
        f.write('\n')
    print(meta['counts'], '->', os.path.relpath(OUT, ROOT), f'{os.path.getsize(OUT) / 1e6:.2f} MB')


if __name__ == '__main__':
    main()
