#!/usr/bin/env python3
"""Vygeneruje voda/rozbory.json z PDF protokolů o zkoušce pitné vody.

Vstup: voda/rozbory/*.pdf (stažené z pecky.as4u.cz, seznam a popisy v
_WORKING/voda-rozbory/index.json), text se čte přes `pdftotext -layout`.
Naskenované protokoly (bez textové vrstvy) se berou z ručně přepsaného
voda/rozbory-sken.json. Spuštění: python3 voda/update-rozbory.py
"""
import json, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INDEX = ROOT.parent / '_WORKING' / 'voda-rozbory' / 'index.json'
SKEN = ROOT / 'rozbory-sken.json'

METHOD = re.compile(r'^(SOP \S+|subdodávka)$')
LIM = re.compile(r'^(?:max\.|min\.)?\s*[\d,]+(?:\s*-\s*[\d,]+)?(?:\s+(?:NMH|MH|DH))?$')


def num(v):
    m = re.match(r'^(<|>)?\s*(-?\d+(?:,\d+)?)$', v.strip())
    if not m:
        return None, None
    return float(m.group(2).replace(',', '.')), m.group(1)


def norm_misto(m):
    k = m.replace(',', ' ').lower().split()
    s = ' '.join(k)
    if s in ('pečky vdj upravená', 'pečky vdj', 'pečky vd'):
        return 'Pečky – vodojem (VDJ)'
    if s in ('pečky zš',):
        return 'Pečky – ZŠ'
    if s.startswith('zdroj tatce'):
        return 'Zdroj Tatce'
    if s == 'ou':
        return 'OU (úpravna)'
    if s.startswith('mš'):
        return 'Pečky – MŠ, J. Švermy 825'
    if s.startswith('187'):
        return 'Velké Chválovice – 187, Klaro'
    if s.startswith('pečky pečecké služby') or s == 'pečky':
        return 'Pečky – Pečecké služby'
    return m


def parse(txt):
    flat = txt.replace('\f', '\n')
    g = lambda pat: (re.search(pat, flat) or [None, None])[1]
    datum = g(r'Datum odběru:\s*(\d+)\.(\d+)\.(\d+)')
    m = re.search(r'Datum odběru:\s*(\d+)\.\s*(\d+)\.\s*(\d+)', flat)
    d = f'{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}'
    misto = ' '.join(re.search(r'Místo odběru:\s*\n?\s*(.+?)\n\s*\n', flat, re.S).group(1).split())
    # druhý řádek místa (např. „Pečky / Pečecké služby“)
    misto = misto.replace('Stanovení Jednotka', '').strip()
    obec = (re.search(r'Obec:\s*(.+)', flat) or [None, 'Pečky'])[1].strip()
    protokol = re.search(r'Protokol o zkoušce číslo:\s*(\S+)', flat).group(1)
    params = {}
    for line in flat.split('\n'):
        parts = re.split(r'\s{2,}', line.strip())
        mi = next((i for i, p in enumerate(parts) if METHOD.match(p)), None)
        if mi is None or mi < 2:
            continue
        name = parts[0].lstrip('#*').strip()
        if name.startswith('Datum '):
            continue
        name = {'CHSKMn': 'CHSK - Mn'}.get(name, name)
        val = parts[mi - 1]
        unit = parts[1] if mi - 1 > 1 else ''
        rest = parts[mi + 1:]
        ok = None
        if rest and rest[-1] in ('+', '-', '*'):
            ok = {'+': True, '-': False}.get(rest[-1])
            rest = rest[:-1]
        elif rest and re.search(r'\s[+-]$', rest[-1]):
            ok = rest[-1][-1] == '+'
            rest = rest[:-1] + [rest[-1][:-2]]
        limit = ' '.join(rest).strip()
        n, op = num(val)
        p = {'u': unit, 'v': n if n is not None else val}
        if op:
            p['op'] = op
        if limit:
            p['limit'] = limit
        if ok is not None:
            p['ok'] = ok
        params[name] = p
    return {'date': d, 'obec': obec, 'misto_orig': misto, 'misto': norm_misto(misto),
            'protokol': protokol, 'params': params}


def main():
    index = {x['id']: x for x in json.load(open(INDEX))}
    sken = json.load(open(SKEN)) if SKEN.exists() else {}
    out = []
    for pdf in sorted((ROOT / 'rozbory').glob('*.pdf')):
        i = pdf.stem
        txt = subprocess.run(['pdftotext', '-layout', str(pdf), '-'], capture_output=True, text=True).stdout
        if len(txt.strip()) > 200:
            s = parse(txt)
            s['zdroj_text'] = 'pdf'
        elif i in sken:
            s = dict(sken[i])
            s['misto'] = norm_misto(s['misto_orig'])
            s['zdroj_text'] = 'sken'
        else:
            print('CHYBÍ přepis skenu:', i, file=sys.stderr)
            continue
        s['id'] = i
        s['pdf'] = f'/voda/rozbory/{i}.pdf'
        s['pdf_zdroj'] = index[i]['url']
        s['popis'] = index[i]['popis']
        out.append(s)
    out.sort(key=lambda s: (s['date'], s['misto']), reverse=True)
    json.dump({'generated': 'RRRR', 'samples': out}, open(ROOT / 'rozbory.json', 'w'), ensure_ascii=False, indent=1)
    print(len(out), 'protokolů')

main()
