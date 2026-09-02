#!/usr/bin/env python3
"""
Generovací skript pro pecky.online (viz ARCHITEKTURA-MIGRACE.md).

Skládá finální statické stránky ze sdílené šablony (templates/page.html),
sdílené navigace (assets/nav.html), patičky (assets/footer.html) a obsahu
jednotlivých sekcí (content/<sekce>.html). Výstup jsou čisté statické
soubory, které GitHub Pages servíruje bez jakékoli další konfigurace.

Spouštět ručně před publikací, kdykoli se změní obsah nějaké sekce
(content/*.html) nebo sdílené části (templates/, assets/nav.html,
assets/footer.html). Nahrazuje ruční editaci vygenerovaných
<sekce>/index.html souborů - ty se needí přímo, jen se přegenerují.

Použití:
    python3 scripts/build.py            # vygeneruje všechny stránky + validace
    python3 scripts/build.py --no-check # bez HTML/JS validace (rychlejší, pro ladění)
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Nasazení: repo zatím nemá vlastní doménu (pecky.online drží někdo jiný,
# viz ARCHITEKTURA-MIGRACE.md), takže běží na GitHub Pages subcestě.
# Až bude vlastní doména na kořeni, přepnout na SITE_BASE_PATH = '' a
# SITE_DOMAIN = 'https://pecky.online' - jediné dvě řádky ke změně.
SITE_BASE_PATH = '/pecky.online'
SITE_DOMAIN = 'https://jakubspanihel.github.io/pecky.online'

# slug -> (výstupní cesta, title, meta description, potřebuje assets/helpers.js)
MANIFEST = {
    'domu': (
        '/', 'pecky.online — Pečky pohledem umělé inteligence',
        'Neoficiální občanský transparentní web o městě Pečky (okres Kolín): '
        'zastupitelstvo, rada, smlouvy, zakázky a Pečecké noviny na jednom místě.',
        False),
    'jednani': (
        '/jednani/', 'Jednání zastupitelstva a rady — pecky.online',
        'Archiv jednání zastupitelstva a rady města Pečky s usneseními, '
        'docházkou a odkazy na videozáznam — s fulltextovým vyhledáváním.',
        True),
    'zpravodaj': (
        '/noviny/', 'Pečecké noviny — pecky.online',
        'Archiv Pečeckých novin (městského zpravodaje) s fulltextovým '
        'vyhledáváním napříč všemi vydáními.',
        True),
    'lide': (
        '/lide/', 'Lidé — zastupitelstvo a rada — pecky.online',
        'Adresář zastupitelů a radních města Pečky: kdo je kdo, za jaké '
        'uskupení kandidoval a jakou má aktuální funkci.',
        True),
    'plan': (
        '/plan/', 'Strategický plán města — pecky.online',
        'Co si město Pečky předsevzalo ve strategickém a akčním plánu '
        'rozvoje — a co se z toho reálně podařilo dohledat jako splněné.',
        False),
    'telocvicna': (
        '/telocvicna/', 'Tělocvična — pecky.online',
        'Stavba nové tělocvičny a učeben u ZŠ Pečky (205 mil. Kč) byla '
        'v srpnu 2026 částečně zastavena kvůli problému s piloty — '
        'časová osa, ověřená fakta ze zápisu zastupitelstva a veřejná '
        'výzva k transparentnímu řešení.',
        False),
    'volby2018': (
        '/volby/2018/', 'Volby 2018 — pecky.online',
        'Komunální volby 2018 v Pečkách: volební uskupení, předvolební '
        'sliby a výsledky.',
        False),
    'volby2022': (
        '/volby/2022/', 'Volby 2022 — pecky.online',
        'Komunální volby 2022 v Pečkách: volební uskupení, předvolební '
        'sliby, výsledky a rozbor povolební koalice.',
        False),
    'volby2026': (
        '/volby/2026/', 'Volby 2026 — pecky.online',
        'Komunální volby 2026 v Pečkách: registrovaná uskupení a aktuální '
        'stav příprav.',
        False),
    'smlouvy': (
        '/smlouvy/', 'Smlouvy — pecky.online',
        'Veřejné smlouvy města Pečky podle registru smluv, přes Hlídače '
        'státu.',
        False),
    'zakazky': (
        '/zakazky/', 'Veřejné zakázky — pecky.online',
        'Veřejné zakázky zadané městem Pečky.',
        False),
    'pozemky': (
        '/pozemky/', 'Pozemky — pecky.online',
        'Pozemky, které město Pečky kupuje nebo prodává, s odkazy na '
        'katastr nemovitostí.',
        False),
    'pokladna': (
        '/pokladna/', 'Pokladna — pecky.online',
        'Na co město Pečky utrácí: rozpočet a hospodaření srozumitelně.',
        False),
    'owebu': (
        '/o-webu/', 'O webu — pecky.online',
        'Co je pecky.online, kdo a jak ho dělá, a odkazy na oficiální '
        'zdroje a otevřená data o městě Pečky.',
        False),
}


# cesta k README sekce (jak je zapsaná v tabulce "Stav sekcí") -> slug v MANIFEST
README_TO_SLUG = {
    'domu': 'domu',
    'jednani': 'jednani',
    'lide': 'lide',
    'noviny': 'zpravodaj',
    'o-webu': 'owebu',
    'plan': 'plan',
    'telocvicna': 'telocvicna',
    'pokladna': 'pokladna',
    'pozemky': 'pozemky',
    'smlouvy': 'smlouvy',
    'zakazky': 'zakazky',
    'volby/2018': 'volby2018',
    'volby/2022': 'volby2022',
    'volby/2026': 'volby2026',
}


def read(path):
    return (ROOT / path).read_text(encoding='utf-8')


def esc(s):
    return (s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
             .replace('"', '&quot;'))


def parse_stav_sekci():
    """Vytáhne tabulku "Stav sekcí" z kořenového README.md.

    README je jediný zdroj pravdy a drží absolutní datumy (klasický formát
    "30. 8. 2026") - relativní stáří ("před 6 dny") se nikam neukládá,
    dopočítá ho až JS v prohlížeči proti hodinám návštěvníka. Díky tomu
    tabulka nezastará ani bez denního běhu buildu.

    Vrací seznam dictů se surovými datumy v ISO (pro data-atributy) i
    v původním zápisu (fallback, když JS neběží).
    """
    readme = read('README.md')
    try:
        block = readme.split('## Stav sekcí')[1].split('\n## ')[0]
    except IndexError:
        raise SystemExit('CHYBA: v README.md chybí sekce "## Stav sekcí".')

    rows = []
    for line in block.splitlines():
        if not line.startswith('| ['):
            continue
        cells = [c.strip() for c in line.split('|')[1:-1]]
        if len(cells) != 5:
            raise SystemExit(f'CHYBA: řádek tabulky "Stav sekcí" nemá 5 sloupců: {line}')
        name_m = re.match(r'\[([^\]]+)\]\(([^)]+)\)', cells[0])
        if not name_m:
            raise SystemExit(f'CHYBA: nečitelný odkaz v tabulce "Stav sekcí": {cells[0]}')
        name, readme_path = name_m.group(1), name_m.group(2)
        key = readme_path.rsplit('/README.md', 1)[0]
        slug = README_TO_SLUG.get(key)
        if slug is None:
            raise SystemExit(f'CHYBA: sekci "{name}" ({key}) neznám, doplň ji do README_TO_SLUG.')

        rows.append({
            'name': name,
            'url': MANIFEST[slug][0],
            'rezim': cells[1],
            'kontrola': parse_cz_date(cells[2]),
            'zmena': parse_cz_date(cells[3]),
            'co': cells[4],
        })

    if not rows:
        raise SystemExit('CHYBA: tabulka "Stav sekcí" v README.md je prázdná.')
    return rows


def parse_cz_date(cell):
    """'30. 8. 2026' -> {'iso': '2026-08-30', 'raw': '30. 8. 2026', 'odhad': False}

    Pomlčka = sekce nemá co kontrolovat. Otazník za datem = nedoložený odhad.
    """
    if cell in ('—', '-', ''):
        return None
    odhad = cell.rstrip().endswith('?')
    text = cell.rstrip().rstrip('?').strip()
    m = re.match(r'^(\d{1,2})\.\s*(\d{1,2})\.\s*(\d{4})$', text)
    if not m:
        raise SystemExit(f'CHYBA: nečitelné datum v tabulce "Stav sekcí": {cell!r}')
    d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
    return {'iso': f'{y:04d}-{mo:02d}-{d:02d}', 'raw': text, 'odhad': odhad}


def render_stav_sekci(rows):
    """Vyrenderuje tabulku do HTML. Buňky s datem nesou data-date (ISO);
    text uvnitř je absolutní datum jako fallback, JS ho přepíše na stáří."""
    out = ['<table class="register stav-sekci">',
           '<thead><tr><th>Sekce</th><th>Režim</th><th>Kontrola</th>'
           '<th>Změna</th><th>Co naposledy</th></tr></thead>',
           '<tbody>']
    for r in rows:
        cells = [f'<td><a href="{r["url"]}">{esc(r["name"])}</a></td>',
                 f'<td><span class="tag">{esc(r["rezim"])}</span></td>']
        for key in ('kontrola', 'zmena'):
            d = r[key]
            if d is None:
                cells.append('<td class="stav-none" title="tahle sekce nemá '
                             'externí zdroj ke kontrole">—</td>')
            else:
                odhad = ' data-odhad="1"' if d['odhad'] else ''
                title = (' title="odhad, přesné datum nedoloženo"' if d['odhad'] else '')
                cells.append(f'<td data-date="{d["iso"]}"{odhad}{title}>'
                             f'{esc(d["raw"])}{"&nbsp;?" if d["odhad"] else ""}</td>')
        cells.append(f'<td>{esc(r["co"])}</td>')
        out.append('<tr>' + ''.join(cells) + '</tr>')
    out += ['</tbody>', '</table>']
    return '\n'.join(out)


def apply_base_path(html):
    """Přepíše kořenově-absolutní interní odkazy (href="/...", src="/...",
    fetch('/...')) tak, aby fungovaly i při nasazení na GitHub Pages
    subcestě (SITE_BASE_PATH). Cíleně jen tyhle dva kontexty - ne plošně
    "každá uvozovka za lomítkem", to by rozbilo např. self-closing SVG
    tagy (rx="1.5"/><line .../>, kde "/" hned za uvozovkou není odkaz).
    Beze změny, pokud SITE_BASE_PATH == '' (vlastní doména na kořeni).
    """
    if not SITE_BASE_PATH:
        return html
    html = re.sub(
        r'\b(href|src)="(/(?!/)[^"]*)"',
        lambda m: f'{m.group(1)}="{SITE_BASE_PATH}{m.group(2)}"', html)
    html = re.sub(
        r"fetch\('(/(?!/)[^']*)'",
        lambda m: f"fetch('{SITE_BASE_PATH}{m.group(1)}'", html)
    return html


def apply_active(html, current_slug):
    """Nahradí {{ACTIVE:slug}} placeholdery (navlinky žijí v assets/footer.html)."""
    def repl(m):
        slug = m.group(1)
        return ' active' if slug == current_slug else ''
    return re.sub(r'\{\{ACTIVE:([a-z0-9]+)\}\}', repl, html)


def build_nav(current_slug):
    return apply_active(read('assets/nav.html'), current_slug)


def out_file_for(path):
    """'/' -> index.html; '/jednani/' -> jednani/index.html"""
    if path == '/':
        return ROOT / 'index.html'
    return ROOT / path.strip('/') / 'index.html'


def build_all():
    page_tpl = read('templates/page.html')
    footer_tpl = read('assets/footer.html')
    stav_sekci = render_stav_sekci(parse_stav_sekci())
    written = []

    for slug, (path, title, desc, needs_helpers) in MANIFEST.items():
        content = read(f'content/{slug}.html')
        content = content.replace('{{STAV_SEKCI}}', stav_sekci)
        nav = build_nav(slug)
        footer = apply_active(footer_tpl, slug)
        head_scripts = '<script src="/assets/helpers.js"></script>' if needs_helpers else ''

        html = page_tpl
        html = html.replace('{{TITLE}}', title)
        html = html.replace('{{DESCRIPTION}}', desc)
        html = html.replace('{{PATH}}', path)
        html = html.replace('{{SITE_DOMAIN}}', SITE_DOMAIN)
        html = html.replace('{{HEAD_SCRIPTS}}', head_scripts)
        html = html.replace('{{NAV}}', nav)
        html = html.replace('{{CONTENT}}', content)
        html = html.replace('{{FOOTER}}', footer)
        html = html.replace('{{SITE_BASE_PATH}}', SITE_BASE_PATH)
        html = apply_base_path(html)

        out_path = out_file_for(path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(html, encoding='utf-8')
        written.append((slug, out_path, path))

    return written


def build_sitemap(written):
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for slug, out_path, path in written:
        lines.append(f'  <url><loc>{SITE_DOMAIN}{path}</loc></url>')
    lines.append('</urlset>')
    (ROOT / 'sitemap.xml').write_text('\n'.join(lines) + '\n', encoding='utf-8')

    robots = f"User-agent: *\nAllow: /\nSitemap: {SITE_DOMAIN}/sitemap.xml\n"
    (ROOT / 'robots.txt').write_text(robots, encoding='utf-8')


# ---------------------------------------------------------------- validace

TAG_RE = re.compile(r'<(/?)([a-zA-Z][a-zA-Z0-9]*)([^>]*)>')
VOID_TAGS = {'area','base','br','col','embed','hr','img','input','link',
             'meta','param','source','track','wbr'}


def strip_noise(html):
    html = re.sub(r'<!--.*?-->', '', html, flags=re.S)
    html = re.sub(r'<script\b.*?</script>', '', html, flags=re.S)
    html = re.sub(r'<style\b.*?</style>', '', html, flags=re.S)
    return html


def check_tag_balance(html, label):
    stack = []
    for m in TAG_RE.finditer(strip_noise(html)):
        closing, name, attrs = m.group(1), m.group(2).lower(), m.group(3)
        if name in VOID_TAGS or attrs.rstrip().endswith('/'):
            continue
        if closing:
            if not stack or stack[-1] != name:
                print(f'  CHYBA tag balance ({label}): neočekávaný </{name}>, '
                      f'zásobník: {stack[-3:]}')
                return False
            stack.pop()
        else:
            stack.append(name)
    if stack:
        print(f'  CHYBA tag balance ({label}): nezavřené tagy: {stack}')
        return False
    return True


def check_js_syntax(html, label):
    ok = True
    for i, m in enumerate(re.finditer(r'<script\b[^>]*>(.*?)</script>', html, flags=re.S)):
        body = m.group(1)
        if not body.strip():
            continue
        # externí <script src="..."></script> nemá tělo ke kontrole
        result = __import__('subprocess').run(
            ['node', '-e', f'new Function({body!r})'],
            capture_output=True, text=True)
        if result.returncode != 0:
            print(f'  CHYBA JS syntaxe ({label}, blok {i}): {result.stderr.strip()[:300]}')
            ok = False
    return ok


def validate(written):
    all_ok = True
    for slug, out_path, path in written:
        html = out_path.read_text(encoding='utf-8')
        ok1 = check_tag_balance(html, slug)
        ok2 = check_js_syntax(html, slug)
        if ok1 and ok2:
            print(f'  OK  {slug:12s} {path}')
        all_ok = all_ok and ok1 and ok2
    return all_ok


if __name__ == '__main__':
    written = build_all()
    build_sitemap(written)
    print(f'Vygenerováno {len(written)} stránek + sitemap.xml + robots.txt.')
    if '--no-check' not in sys.argv:
        print('Validace (tag balance + JS syntax):')
        ok = validate(written)
        if not ok:
            print('NĚKTERÉ STRÁNKY MAJÍ CHYBU — viz výš.')
            sys.exit(1)
        print('Vše OK.')
