#!/usr/bin/env python3
"""Stažení zápisů z jednání komisí Rady města z pecky.cz.

Obdoba vybory-check.py pro výbory ZM. Projde stránku Komise RM
(pecky.cz → Rada města → Komise RM), najde podstránky jednotlivých komisí,
u každé stránky „Zápisy …“ (případně PDF přímo na stránce komise) a každý
dosud nestažený zápis uloží do

    jednani/Data/{datum}-{komise}/zapis.pdf

kde {komise} je slug stránky komise na pecky.cz (např.
`komise-pro-zivotni-prostredi`). Přípona je vždy, i bez kolize data —
stejně jako u výborů jde o jiný orgán než Rada/ZM.

Datum složky se bere z názvu souboru; když v něm není, z prvního data
v textu PDF (`pdftotext`, jen PDF s textovou vrstvou). Obojí je nutné
**ověřit proti textu zápisu** — u výborů byl název souboru dvakrát
chybný. Zápis bez zjistitelného data jde do
`Data/_bez-data/{komise}/{původní název}` a je potřeba ho zařadit ručně.

Co už stažené je, se pozná podle lokálního `Data/komise-stazene.json`
(URL → cesta, MD5). `Data/` je v .gitignore, takže evidence je jen
lokální; až bude obsah vytěžený do gitu (obdoba vybory.json), přejde
kontrola na `links.minutes` stejně jako u výborů.

Struktura webu komisí zatím nebyla ověřena (skript vznikl v prostředí,
kde byl pecky.cz nedostupný). Proto nejdřív spustit s `--dry-run`:
vypíše nalezené komise, stránky se zápisy a PDF. Pokud komisi nenajde
(slug stránky neobsahuje „komise“), stačí ji přidat přes `--stranka`
nebo do seznamu DALSI_STRANKY níže.

Použití:
  python3 jednani/scripts/komise-check.py --dry-run
  python3 jednani/scripts/komise-check.py
  python3 jednani/scripts/komise-check.py --stranka https://pecky.cz/default/default/NNNNN_slug
"""
import hashlib
import json
import re
import shutil
import subprocess
import sys
from html import unescape
from pathlib import Path
from urllib.parse import unquote, urljoin

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'jednani' / 'Data'
MANIFEST = DATA / 'komise-stazene.json'
BASE = 'https://pecky.cz'
UA = 'Mozilla/5.0'
KOMISE_RM = BASE + '/default/default/21179_komise-rm'
# Stránky komisí, které autodetekce nenajde (slug bez „komise“), např.
# '/default/default/NNNNN_redakcni-rada'.
DALSI_STRANKY = []

STRANKA_RE = re.compile(r'href="((?:https://pecky\.cz)?/default/default/(\d+)_([a-z0-9-]+))"[^>]*>(.*?)</a>', re.S)
PDF_RE = re.compile(r'href="([^"]+\.pdf)"', re.I)
PRILOHA_RE = re.compile(r'href="([^"]*/files/[^"]+\.(?:docx?|odt|rtf))"', re.I)


def get(url):
    r = subprocess.run(['curl', '-sSfL', '-A', UA, url], capture_output=True)
    if r.returncode:
        raise RuntimeError(f'{url}: {r.stderr.decode(errors="replace").strip()}')
    return r.stdout


def text_odkazu(html):
    return re.sub(r'\s+', ' ', unescape(re.sub(r'<[^>]+>', ' ', html))).strip()


def stranky(html):
    """[(absolutní url, id, slug, text odkazu)] bez duplicit, v pořadí na stránce."""
    out, videno = [], set()
    for href, pid, slug, txt in STRANKA_RE.findall(html):
        url = urljoin(BASE, href)
        if url not in videno:
            videno.add(url)
            out.append((url, pid, slug, text_odkazu(txt)))
    return out


def pdfka(html, url_stranky):
    return sorted({urljoin(url_stranky, unescape(h)) for h in PDF_RE.findall(html)})


def datum_z_textu(s):
    """První datum v řetězci: 10.5.2022, 17_6_2026, 2024-03-12, 5. 3. 2020."""
    m = re.search(r'(\d{4})-(\d{1,2})-(\d{1,2})', s)
    if m:
        y, mo, d = map(int, m.groups())
    else:
        m = re.search(r'(?<!\d)(\d{1,2})\s*[-._]\s*(\d{1,2})\s*[-._]\s*(\d{4})(?!\d)', s)
        if not m:
            return None
        d, mo, y = map(int, m.groups())
    if not (1 <= d <= 31 and 1 <= mo <= 12 and 2000 <= y <= 2100):
        return None
    return f'{y}-{mo:02d}-{d:02d}'


def datum_z_pdf(obsah, tmp):
    if not shutil.which('pdftotext'):
        return None
    tmp.write_bytes(obsah)
    r = subprocess.run(['pdftotext', '-l', '2', str(tmp), '-'], capture_output=True)
    tmp.unlink(missing_ok=True)
    return datum_z_textu(r.stdout.decode('utf-8', errors='replace')) if r.returncode == 0 else None


def najdi_komise(extra):
    html = get(KOMISE_RM).decode('utf-8', errors='replace')
    vlastni_id = re.search(r'/(\d+)_', KOMISE_RM).group(1)
    komise = {}
    for url, pid, slug, txt in stranky(html):
        if pid != vlastni_id and 'komise' in slug and slug != 'komise-rm':
            komise[slug] = (txt or slug, url)
    for cesta in DALSI_STRANKY + extra:
        url = urljoin(BASE, cesta)
        m = re.search(r'/\d+_([a-z0-9-]+)', url)
        if m:
            komise.setdefault(m.group(1), (m.group(1), url))
    primo = pdfka(html, KOMISE_RM)
    if not komise:
        print('! Na stránce Komise RM nenalezena žádná podstránka se slugem „komise“.')
        print('  Všechny odkazy na podstránky (vyber komise a přidej přes --stranka / DALSI_STRANKY):')
        for url, _, slug, txt in stranky(html):
            print(f'     {txt[:50]:50} {url}')
    return komise, primo


def zapisy_komise(url):
    """PDF přímo na stránce komise + na jejích podstránkách se zápisy."""
    html = get(url).decode('utf-8', errors='replace')
    nalezeno = {p: url for p in pdfka(html, url)}
    ostatni = set(PRILOHA_RE.findall(html))
    podstranky = [(u, s) for u, _, s, _ in stranky(html) if s.startswith('zapis') or '-zapis' in s]
    for u, _ in podstranky:
        if u == url:
            continue
        sub = get(u).decode('utf-8', errors='replace')
        for p in pdfka(sub, u):
            nalezeno.setdefault(p, u)
        ostatni |= set(PRILOHA_RE.findall(sub))
    return list(nalezeno.items()), podstranky, sorted(ostatni)


def main():
    dry = '--dry-run' in sys.argv
    extra = [a.split('=', 1)[1] for a in sys.argv[1:] if a.startswith('--stranka=')]
    for i, a in enumerate(sys.argv[:-1]):
        if a == '--stranka':
            extra.append(sys.argv[i + 1])
    manifest = json.loads(MANIFEST.read_text(encoding='utf-8')) if MANIFEST.exists() else {}
    known_md5 = {v['md5'] for v in manifest.values()}

    komise, primo = najdi_komise(extra)
    if primo:
        print(f'\n! Přímo na stránce Komise RM je {len(primo)} PDF (není jasné, ke které komisi patří):')
        for p in primo:
            print(f'     {p}')
    nove = []
    for slug, (nazev, url) in komise.items():
        pdf, podstranky, ostatni = zapisy_komise(url)
        print(f'\n== {nazev}  [{slug}]  {url}')
        for u, s in podstranky:
            print(f'   stránka zápisů: {s}  {u}')
        print(f'   PDF celkem: {len(pdf)}, z toho už staženo: {sum(p in manifest for p, _ in pdf)}')
        for p in ostatni:
            print(f'   ! příloha, která není PDF (nestahuje se): {p}')
        nove += [(slug, p, zdroj) for p, zdroj in pdf if p not in manifest]

    if not nove:
        print('\nŽádný nový zápis.')
        return
    print(f'\nNOVÉ ZÁPISY ({len(nove)}):')
    tmp = DATA / '.komise-tmp.pdf'
    for slug, url, zdroj in nove:
        nazev_souboru = unquote(url.rsplit('/', 1)[-1])
        datum = datum_z_textu(nazev_souboru)
        puvod = 'z názvu souboru'
        print(f'   {slug:40} {datum or "?":10}  {nazev_souboru}')
        if dry:
            continue
        obsah = get(url)
        if not obsah.startswith(b'%PDF'):
            print('      ! stažený soubor není PDF — přeskočeno')
            continue
        md5 = hashlib.md5(obsah).hexdigest()
        if md5 in known_md5:
            print('      ! stejný soubor (MD5) už je stažený pod jinou URL — přeskočeno')
            continue
        if not datum:
            DATA.mkdir(parents=True, exist_ok=True)
            datum, puvod = datum_z_pdf(obsah, tmp), 'z textu PDF'
        if datum:
            slozka = DATA / f'{datum}-{slug}'
            cil = slozka / 'zapis.pdf'
            n = 2
            while cil.exists():
                cil = slozka / f'zapis-{n}.pdf'
                n += 1
        else:
            cil = DATA / '_bez-data' / slug / nazev_souboru
            puvod = 'datum nezjištěno — zařadit ručně'
        cil.parent.mkdir(parents=True, exist_ok=True)
        cil.write_bytes(obsah)
        known_md5.add(md5)
        manifest[url] = {'komise': slug, 'soubor': str(cil.relative_to(ROOT)), 'md5': md5,
                         'datum': datum, 'datum_zdroj': puvod, 'stranka': zdroj}
        print(f'      -> {cil.relative_to(ROOT)} ({puvod}; MD5 {md5[:12]}…)')
        MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding='utf-8')
    print('\nDalší krok: ověřit datum každé složky proti textu zápisu (jednani/README.md → „Zápisy komisí RM“).')


if __name__ == '__main__':
    main()
