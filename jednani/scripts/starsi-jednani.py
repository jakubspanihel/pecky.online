#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Starší jednání z úřední desky (před začátkem archivu usneseni.cz, tj. před 4/2021).

Z dokumentů úřední desky (o-webu/uredni-deska-monitoring/<rok>.txt) vybere
  - zápisy z jednání rady města (RM) z let 2015–2016 ("Zápis RM dne …"),
  - usnesení zastupitelstva (ZM) z let 2015 až 4/2021 ("Usnesení ZM č. N/RRRR …"),
ke každému jednání zkopíruje JEDEN soubor do jednani/Data/<datum>-<rada|zastupitelstvo>/
(zapis.* / usneseni.*; Data/ je v .gitignore) a zapíše jednani/starsi-jednani.json
(úroveň A: metadata, odkaz na zdroj, text z OCR/PDF; bez parsování hlasování).
Stránka /jednani/ ho načítá jen do vlastního bloku „Starší jednání“ — do
pecky-jednani.json, docházky ani žebříčků nevstupuje.

Použití: python3 jednani/scripts/starsi-jednani.py   (z kořene repa)
"""
import json, os, re, shutil, sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MON = os.path.join(ROOT, 'o-webu', 'uredni-deska-monitoring')
sys.path.insert(0, MON)
import summary as S  # noqa: E402

OUT = os.path.join(ROOT, 'jednani', 'starsi-jednani.json')
DATA_OUT = os.path.join(ROOT, 'jednani', 'Data')
ZM_LAST = '2021-05-31'   # ZM od 6/2021 (16. 6. 2021) už archiv z usneseni.cz má
RX_ZM = re.compile(r'usnesení\s+(?:ze\s+)?zm\b', re.I)
RX_RM = re.compile(r'^zápis\s+rm\b', re.I)
RX_DATE = re.compile(r'(\d{1,2})\.\s*(\d{1,2})\.\s*(\d{4})')
RX_NUM = re.compile(r'č\.?\s*(\d+)\s*/\s*(\d{4})')
MONTHS = ['ledna', 'února', 'března', 'dubna', 'května', 'června', 'července', 'srpna', 'září', 'října', 'listopadu', 'prosince']
PREF = ['.pdf', '.docx', '.doc', '.rtf']


def cz(d):
    y, m, dd = d.split('-')
    return f'{int(dd)}. {int(m)}. {y}'


def doc_dir(x):
    key = ('as4u-' + x['slug'][5:]) if x['as4u'] else x['slug'].split('_')[0]
    return os.path.join(MON, 'Data', x['from'][:4], key), os.path.join(MON, 'Text', x['from'][:4], key), key


def pick(dirpath):
    if not os.path.isdir(dirpath):
        return None
    fs = [f for f in sorted(os.listdir(dirpath)) if not f.startswith('.')]
    for ext in PREF:
        c = [f for f in fs if f.lower().endswith(ext)]
        if c:
            return c[0]
    return fs[0] if fs else None


def read_text(tdir, fn):
    if not fn:
        return ''
    p = os.path.join(tdir, fn + '.txt')
    return open(p, encoding='utf-8', errors='replace').read() if os.path.exists(p) else ''


def meeting_date(title, text):
    m = RX_DATE.search(title)
    if not m:
        m = re.search(r'konan\w+\s+dne\s+(\d{1,2})\.\s*(\d{1,2})\.\s*(\d{4})', text)
    if not m:
        return None
    d, mo, y = map(int, m.groups())
    return f'{y:04d}-{mo:02d}-{d:02d}'


def main():
    global TM
    TM = json.load(open(os.path.join(MON, 'text-manifest.json'), encoding='utf-8'))
    docs = S.load()
    cand = []
    for x in docs:
        t = x['title']
        if RX_RM.match(t) and x['from'] <= '2016-12-31':
            cand.append(('Rada', x))
        elif RX_ZM.search(t) and x['from'] <= ZM_LAST:
            cand.append(('Zastupitelstvo', x))
    out, seen, problems = [], {}, []
    for typ, x in sorted(cand, key=lambda c: c[1]['from']):
        ddir, tdir, key = doc_dir(x)
        fn = pick(ddir)
        text = read_text(tdir, fn)
        d = meeting_date(x['title'], text)
        if not d:
            problems.append(f'bez data: {x["title"]}')
            continue
        num = None
        m = RX_NUM.search(x['title'])
        if m and typ == 'Zastupitelstvo':
            num = int(m.group(1))
        ident = (typ, d)
        if ident in seen:
            # duplicitní záznam téhož jednání na desce — nechá se ten, který má soubor (jinak první)
            prev = seen[ident]
            if not prev['file'] and fn:
                out.remove(prev); 
            else:
                problems.append(f'duplicita {typ} {d}: {x["title"]} (vyvěšeno {x["from"]})')
                continue
        kind = 'zápis' if typ == 'Rada' else 'usnesení'
        folder = f'{d}-{"rada" if typ == "Rada" else "zastupitelstvo"}'
        local = None
        if fn:
            ext = os.path.splitext(fn)[1].lower() or '.pdf'
            dst_dir = os.path.join(DATA_OUT, folder)
            os.makedirs(dst_dir, exist_ok=True)
            dst = os.path.join(dst_dir, ('zapis' if typ == 'Rada' else 'usneseni') + ext)
            if not os.path.exists(dst):
                shutil.copy2(os.path.join(ddir, fn), dst)
            local = f'Data/{folder}/{os.path.basename(dst)}'
        lab = (f'ZM {num}/{d[:4]} ({cz(d)})' if num else f'ZM ({cz(d)})') if typ == 'Zastupitelstvo' else f'Rada ({cz(d)})'
        rec = {
            'id': f'{"rada" if typ == "Rada" else "zastupitelstvo"}-{d}',
            'uuid': None, 'type': typ, 'group': 'starsi', 'number': num, 'year': int(d[:4]),
            'date': d, 'label': lab,
            'doc_kind': kind, 'doc_title': x['title'], 'posted': x['from'],
            'source': 'úřední deska ' + ('města (starý web pecky.as4u.cz)' if x['as4u'] else 'města (pecky.cz)'),
            'links': {'minutes': x['url']},
            'file': local,
            'ocr': bool(fn and TM.get(f'{x["from"][:4]}/{key}/{fn}', {}).get('method') == 'ocr'),
            'text': re.sub(r'[ \t]{3,}', '  ', re.sub(r'\n{3,}', '\n\n', text.replace('\f', '\n'))).strip(),
        }
        seen[ident] = rec
        out.append(rec)
    out.sort(key=lambda r: r['date'], reverse=True)
    # mezery v číslování ZM
    gaps = {}
    for y in sorted({r['year'] for r in out if r['type'] == 'Zastupitelstvo' and r['number']}):
        nums = sorted(r['number'] for r in out if r['type'] == 'Zastupitelstvo' and r['year'] == y and r['number'])
        miss = [n for n in range(1, max(nums) + 1) if n not in nums]
        if miss:
            gaps[str(y)] = miss
    meta = {
        'updated': date.today().isoformat(),
        'source': 'úřední deska města Pečky (pecky.cz, starý web pecky.as4u.cz) — viz o-webu/uredni-deska-monitoring/',
        'note': ('Zápisy rady města z let 2015–2016 a usnesení zastupitelstva z let 2015 až 4/2021, která byla vyvěšena '
                 'na úřední desce. Starší než 6/2021 archiv usneseni.cz nemá. U zastupitelstva jde jen o usnesení '
                 '(bez hlasování a rozpravy). Rada: na desce jsou zápisy jen od června 2015 do prosince 2016.'),
        'counts': {'Rada': sum(1 for r in out if r['type'] == 'Rada'),
                   'Zastupitelstvo': sum(1 for r in out if r['type'] == 'Zastupitelstvo')},
        'zm_missing_numbers': gaps,
        'without_file': [r['id'] for r in out if not r['file']],
    }
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump({'meta': meta, 'meetings': out}, f, ensure_ascii=False, indent=1)
        f.write('\n')
    print(meta['counts'], 'mezery ZM:', gaps, 'bez souboru:', meta['without_file'])
    for p in problems:
        print('!', p)
    print('->', os.path.relpath(OUT, ROOT), f'{os.path.getsize(OUT) / 1e6:.2f} MB')


if __name__ == '__main__':
    main()
