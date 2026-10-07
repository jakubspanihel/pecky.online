#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vytáhne text ze stažených příloh (Data/) do Text/<rok>/<složka>/<soubor>.txt.

Lokální index pro fulltext (Data/, Text/ a text-manifest.json jsou v .gitignore).
Typ souboru se pozná podle prvních bajtů, ne přípony:
  PDF   -> pdftotext -layout; bez textové vrstvy (<100 znaků) OCR: pdftoppm + tesseract (ces),
           nejvýš OCR_MAX_PAGES stran
  DOCX  -> word/document.xml (zipfile),  XLSX -> sharedStrings + listy (zipfile)
  DOC/RTF -> macOS textutil,  ZIP -> rozbalí a zpracuje členy (jedna úroveň)
  TIFF/JPEG/PNG -> tesseract,  XLS -> nepodporováno (označeno v manifestu)
Použití: python3 o-webu/uredni-deska-monitoring/extract.py [rok …]
Opakované spuštění přeskočí soubory, jejichž velikost a čas změny se nezměnily.
"""
import json, os, re, shutil, subprocess, sys, tempfile, threading, zipfile
from concurrent.futures import ThreadPoolExecutor
from xml.etree import ElementTree as ET

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, 'Data')
TEXT = os.path.join(BASE, 'Text')
MANIFEST = os.path.join(BASE, 'text-manifest.json')
OCR_MAX_PAGES = 40
OCR_DPI = 200
ENV = dict(os.environ, OMP_THREAD_LIMIT='1')
LOCK = threading.Lock()


def run(cmd, timeout, **kw):
    return subprocess.run(cmd, capture_output=True, timeout=timeout, env=ENV, **kw)


def kind(path):
    with open(path, 'rb') as f:
        h = f.read(8)
    if h.startswith(b'%PDF'):
        return 'pdf'
    if h.startswith(b'PK'):
        try:
            names = zipfile.ZipFile(path).namelist()
        except Exception:
            return 'zip?'
        if any(n.startswith('word/') for n in names):
            return 'docx'
        if any(n.startswith('xl/') for n in names):
            return 'xlsx'
        return 'zip'
    if h.startswith(b'\xd0\xcf\x11\xe0'):
        return 'xls' if path.lower().endswith('.xls') else 'doc'
    if h.startswith(b'{\\rtf'):
        return 'rtf'
    if h[:4] in (b'II*\x00', b'MM\x00*') or h[:3] == b'\xff\xd8\xff' or h.startswith(b'\x89PNG'):
        return 'img'
    return 'neznamy'


def ocr_image(path):
    r = run(['tesseract', path, '-', '-l', 'ces', '--psm', '3'], 180)
    return r.stdout.decode('utf-8', 'replace')


def pdf_text(path):
    try:
        r = run(['pdftotext', '-layout', path, '-'], 90)
        txt = r.stdout.decode('utf-8', 'replace')
    except subprocess.TimeoutExpired:
        txt = ''
    if len(txt.strip()) >= 100:
        return txt, 'pdftotext', ''
    tmp = tempfile.mkdtemp(prefix='ocr_')
    try:
        try:
            run(['pdftoppm', '-r', str(OCR_DPI), '-gray', '-png', '-l', str(OCR_MAX_PAGES), path, os.path.join(tmp, 'p')], 300)
        except subprocess.TimeoutExpired:
            return txt, 'ocr', 'časový limit při renderu'
        pages = sorted(f for f in os.listdir(tmp) if f.endswith('.png'))
        out = []
        for p in pages:
            try:
                out.append(ocr_image(os.path.join(tmp, p)))
            except subprocess.TimeoutExpired:
                out.append('')
        note = f'OCR {len(pages)} stran' + (f' (nejvýš {OCR_MAX_PAGES})' if len(pages) >= OCR_MAX_PAGES else '')
        return '\n\f'.join(out), 'ocr', note
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def docx_text(path):
    z = zipfile.ZipFile(path)
    xml = z.read('word/document.xml').decode('utf-8', 'replace')
    xml = re.sub(r'</w:p>', '\n', xml)
    xml = re.sub(r'<w:tab/>', '\t', xml)
    return re.sub(r'<[^>]+>', '', xml)


def xlsx_text(path):
    z = zipfile.ZipFile(path)
    names = z.namelist()
    strings = []
    if 'xl/sharedStrings.xml' in names:
        root = ET.fromstring(z.read('xl/sharedStrings.xml'))
        for si in root.iter():
            if si.tag.endswith('}si'):
                strings.append(''.join(t.text or '' for t in si.iter() if t.tag.endswith('}t')))
    out = []
    for n in sorted(x for x in names if re.match(r'xl/worksheets/sheet\d+\.xml', x)):
        root = ET.fromstring(z.read(n))
        out.append(f'--- {n.split("/")[-1]} ---')
        for row in root.iter():
            if not row.tag.endswith('}row'):
                continue
            cells = []
            for c in row:
                v = next((x.text for x in c if x.tag.endswith('}v')), None)
                inline = ''.join(t.text or '' for t in c.iter() if t.tag.endswith('}t'))
                if c.get('t') == 's' and v is not None and v.isdigit() and int(v) < len(strings):
                    cells.append(strings[int(v)])
                elif inline:
                    cells.append(inline)
                elif v is not None:
                    cells.append(v)
            if cells:
                out.append('\t'.join(cells))
    return '\n'.join(out)


def textutil(path):
    tmp = tempfile.mkdtemp(prefix='tu_')
    try:
        dst = os.path.join(tmp, 'o.txt')
        r = run(['textutil', '-convert', 'txt', '-encoding', 'UTF-8', '-output', dst, path], 120)
        return open(dst, encoding='utf-8', errors='replace').read() if os.path.exists(dst) else ''
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def extract(path, depth=0):
    """-> (text, method, note)"""
    k = kind(path)
    if k == 'pdf':
        return pdf_text(path)
    if k == 'docx':
        return docx_text(path), 'docx', ''
    if k == 'xlsx':
        return xlsx_text(path), 'xlsx', ''
    if k in ('doc', 'rtf'):
        return textutil(path), 'textutil', ''
    if k == 'img':
        return ocr_image(path), 'ocr', 'obrázek'
    if k == 'zip' and depth == 0:
        tmp = tempfile.mkdtemp(prefix='zip_')
        try:
            z = zipfile.ZipFile(path)
            parts = []
            for i, n in enumerate(z.namelist()):
                if n.endswith('/'):
                    continue
                dst = os.path.join(tmp, f'{i}_' + re.sub(r'[^\w.\-]', '_', os.path.basename(n)))
                with z.open(n) as src, open(dst, 'wb') as out:
                    shutil.copyfileobj(src, out)
                try:
                    t, m, _ = extract(dst, 1)
                except Exception:
                    t = ''
                if t.strip():
                    parts.append(f'=== {n} ===\n{t}')
            return '\n\n'.join(parts), 'zip', f'{len(parts)} členů s textem'
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    return '', k, 'nepodporováno'


def one(job):
    rel, size, mtime = job
    src = os.path.join(DATA, rel)
    try:
        text, method, note = extract(src)
        status = 'ok' if text.strip() else 'bez textu'
    except Exception as e:
        text, method, note, status = '', kind(src), f'{type(e).__name__}: {e}'[:200], 'chyba'
    dst = os.path.join(TEXT, rel + '.txt')
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    text = re.sub(r'[ \t]+\n', '\n', text.replace('\r', ''))
    with open(dst, 'w', encoding='utf-8') as f:
        f.write(text)
    return rel, {'size': size, 'mtime': mtime, 'chars': len(text.strip()), 'method': method,
                 'status': status, 'note': note}


def main():
    years = sys.argv[1:]
    man = json.load(open(MANIFEST, encoding='utf-8')) if os.path.exists(MANIFEST) else {}
    jobs = []
    for root, _, files in os.walk(DATA):
        for fn in files:
            if fn.startswith('.'):
                continue
            p = os.path.join(root, fn)
            rel = os.path.relpath(p, DATA)
            if years and rel.split(os.sep)[0] not in years:
                continue
            st = os.stat(p)
            m = man.get(rel)
            if m and m.get('size') == st.st_size and m.get('mtime') == int(st.st_mtime) and m.get('status') != 'chyba':
                continue
            jobs.append((rel, st.st_size, int(st.st_mtime)))
    jobs.sort(key=lambda j: j[0])
    print(f'k zpracování: {len(jobs)} souborů', flush=True)
    done = 0
    with ThreadPoolExecutor(max_workers=8) as ex:
        for rel, val in ex.map(one, jobs):
            with LOCK:
                man[rel] = val
                done += 1
                if done % 100 == 0 or done == len(jobs):
                    with open(MANIFEST, 'w', encoding='utf-8') as f:
                        json.dump(dict(sorted(man.items())), f, ensure_ascii=False, indent=0)
                    print(f'{done}/{len(jobs)}', flush=True)
    import collections
    c = collections.Counter(v['status'] for v in man.values())
    m = collections.Counter(v['method'] for v in man.values())
    print('hotovo:', dict(c), '| metody:', dict(m), '| znaků celkem', round(sum(v['chars'] for v in man.values()) / 1e6, 1), 'M')


if __name__ == '__main__':
    main()
