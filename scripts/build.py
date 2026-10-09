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
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from typografie import nbsp_html  # noqa: E402
from build_peckybot_index import main as build_peckybot_index  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

# Nasazení: vlastní doména dopecek.cz na kořeni (CNAME, přes GitHub Pages),
# viz ARCHITEKTURA-MIGRACE.md. Dřív web běžel na GitHub Pages subcestě
# (https://jakubspanihel.github.io/pecky.online/) bez vlastní domény —
# proto SITE_BASE_PATH pořád existuje jako přepínač pro tenhle stav.
SITE_BASE_PATH = ''
SITE_DOMAIN = 'https://dopecek.cz'

# Google Analytics 4 (gtag.js), vkládá se do templates/page.html na každé stránce.
GA_MEASUREMENT_ID = 'G-1CW9XK1VJY'

# Slogan webu: jediný zdroj pravdy. Použije se jako <title>/og:title homepage
# i jako podtitulek v hlavičce homepage (viz build_nav). Změna se projeví na obou místech.
SLOGAN = 'Abyste vždycky věděli, co se v Pečkách děje'

# slug -> (výstupní cesta, title, meta description, potřebuje assets/helpers.js)
MANIFEST = {
    'domu': (
        '/', f'Do Peček . cz — {SLOGAN}',
        'Neoficiální občanský transparentní web o městě Pečky (okres Kolín): '
        'zastupitelstvo, rada, smlouvy, zakázky a Pečecké noviny na jednom místě.',
        False),
    'jednani': (
        '/jednani/', 'Jednání zastupitelstva a rady — Do Peček . cz',
        'Archiv jednání zastupitelstva a rady města Pečky s usneseními, '
        'docházkou a odkazy na videozáznam — s fulltextovým vyhledáváním.',
        True),
    'zpravodaj': (
        '/noviny/', 'Pečecké noviny — Do Peček . cz',
        'Archiv Pečeckých novin (městského zpravodaje) s fulltextovým '
        'vyhledáváním napříč všemi vydáními.',
        True),
    'lide': (
        '/lide/', 'Lidé města Pečky — Do Peček . cz',
        'Adresář lidí ve veřejných funkcích města Pečky — zastupitelstvo, '
        'rada, vedení a zaměstnanci úřadu i ředitelé městských organizací. '
        'U každého funkce, kontakt a zdroj.',
        True),
    'plan': (
        '/plan/', 'Strategický plán města — Do Peček . cz',
        'Co si město Pečky předsevzalo ve strategickém a akčním plánu '
        'rozvoje — a co se z toho reálně podařilo dohledat jako splněné.',
        False),
    'telocvicna': (
        '/telocvicna/', 'Tělocvična — Do Peček . cz',
        'Stavba nové tělocvičny a učeben u ZŠ Pečky (205 mil. Kč) byla '
        'v srpnu 2026 částečně zastavena kvůli problému s piloty — '
        'časová osa, ověřená fakta ze zápisu zastupitelstva a veřejná '
        'výzva k transparentnímu řešení.',
        False),
    'volby': (
        '/volby/', 'Volby do zastupitelstva — Do Peček . cz',
        'Přehled komunálních voleb do zastupitelstva města Pečky: '
        'ročníky 2018, 2022 a 2026.',
        False),
    'volby2018': (
        '/volby/2018/', 'Volby 2018 — Do Peček . cz',
        'Komunální volby 2018 v Pečkách: volební uskupení, předvolební '
        'sliby a výsledky.',
        False),
    'volby2022': (
        '/volby/2022/', 'Volby 2022 — Do Peček . cz',
        'Komunální volby 2022 v Pečkách: volební uskupení, předvolební '
        'sliby, výsledky a rozbor povolební koalice.',
        False),
    'volby2026': (
        '/volby/2026/', 'Volby 2026 — Do Peček . cz',
        'Komunální volby 2026 v Pečkách: registrovaná uskupení a aktuální '
        'stav příprav.',
        False),
    'smlouvy': (
        '/smlouvy/', 'Smlouvy — Do Peček . cz',
        'Veřejné smlouvy města Pečky podle registru smluv, přes Hlídače '
        'státu.',
        False),
    'zakazky': (
        '/zakazky/', 'Veřejné zakázky — Do Peček . cz',
        'Veřejné zakázky zadané městem Pečky.',
        False),
    'pozemky': (
        '/pozemky/', 'Pozemky — Do Peček . cz',
        'Pozemky, které město Pečky kupuje nebo prodává, s odkazy na '
        'katastr nemovitostí.',
        False),
    'prostory': (
        '/prostory/', 'Prostory k pronájmu — Do Peček . cz',
        'Nebytové prostory města Pečky: záměry pronájmu, smlouvy a jejich '
        'ukončení podle usnesení rady města.',
        False),
    'pokladna': (
        '/pokladna/', 'Pokladna — Do Peček . cz',
        'Na co město Pečky utrácí: rozpočet a hospodaření srozumitelně.',
        False),
    'kalendar': (
        '/kalendar/', 'Co se děje v Pečkách — Do Peček . cz',
        'Kalendář termínů týkajících se města Pečky.',
        False),
    'naobed': (
        '/naobed/', 'Kam na oběd v Pečkách? — Do Peček . cz',
        'Poslední denní menu pečeckých restaurací U Marka, Siňorita a '
        'Hostinec U Stříkačky podle jejich facebookových stránek.',
        False),
    'peckybot': (
        '/peckybot/', 'PečkyBot — Do Peček . cz',
        'Chatbot, který odpovídá na otázky z dat na webu — jednání '
        'zastupitelstva a rady, lidé ve veřejných funkcích a texty sekcí — '
        'a u každé odpovědi uvádí odkaz na zdroj.',
        False),
    'owebu': (
        '/o-webu/', 'O webu — Do Peček . cz',
        'Co je Do Peček . cz, kdo a jak ho dělá, a odkazy na oficiální '
        'zdroje a otevřená data o městě Pečky.',
        False),
}

# Podstránky, které se generují stejně jako sekce z MANIFEST, ale nemají
# řádek v tabulce „Stav sekcí" (žádné pravidelné kontroly odtamtud). Šesté
# pole (lastmod) rozhoduje o viditelnosti pro vyhledávače i o datu
# "Aktualizováno" na stránce: None = stránka je jen přímým odkazem, dostane
# noindex, do sitemapy nejde a datum na stránce nemá; ISO datum = stránka je
# odněkud odkázaná, noindex odpadá, jde do sitemapy s tímhle datem a stejné
# datum se vypíše i pod nadpisem stránky (ruční — bez vlastního řádku v
# "Stav sekcí" nemá odkud se dopočítat samo, na rozdíl od stránek z MANIFEST).
# slug -> (výstupní cesta, title, meta description, helpers.js, sekce pro navigaci, lastmod)
EXTRA_PAGES = {
    'absence': (
        '/jednani/absence.html', 'Jak vás zastupitelé zastupují — Do Peček . cz',
        'Docházka zastupitelů, radních a členů výborů zastupitelstva města '
        'Pečky na jednání v aktuálním volebním období — spočítáno z jmenné '
        'prezence v zápisech, opravené o pozdní příchody.',
        # helpers.js: stránka od 19. 9. 2026 používá sdílenou vizitku osoby
        # (pcAvatarHtml/pcDetailHtml) napojenou na lide/people.json
        # Odkázaná z /jednani/ (odstavec "Kontrola docházky") od 19. 9. 2026 —
        # proto má lastmod a jde do sitemapy, viz komentář výše.
        True, 'jednani', '2026-09-19'),
    'nejdelsi': (
        '/jednani/nejdelsi.html', 'Nejdelší body jednání zastupitelstva — Do Peček . cz',
        'Deset bodů jednání zastupitelstva města Pečky s nejdelší dobou '
        'projednávání v aktuálním volebním období, dopočítané z časových '
        'značek videozáznamů na YouTube.',
        # Odkázaná z /jednani/ (odstavec hned za "Kontrola docházky") od
        # 23. 9. 2026 — proto má lastmod a jde do sitemapy, viz komentář výše.
        # Statická tabulka (snímek k datu lastmod) — na rozdíl od absence.html
        # se nefetchuje z JSON, ať se při ohlédnutí na starší žebříček neplete
        # čtenář s průběžně rostoucím zdrojem dat.
        False, 'jednani', '2026-09-23'),
    'odpracovano': (
        '/jednani/odpracovano.html', 'Kolik času zastupitelé odpracovali — Do Peček . cz',
        'Žebříček zastupitelů města Pečky za volební období 2022–2026 podle '
        'počtu jednání rady, zastupitelstva, výborů a komisí a součtu '
        'odpracovaných hodin — spočítáno z jmenné prezence v zápisech.',
        # Odkázaná z /jednani/ (odstavec "Související") od 30. 9. 2026 —
        # proto má lastmod a jde do sitemapy. Statický snímek k datu lastmod.
        # helpers.js: avatary a vizitka osoby (pcAvatarHtml/pcDetailHtml)
        True, 'jednani', '2026-09-30'),
    'youtube': (
        '/jednani/youtube.html', 'Zhlédnutí záznamů zastupitelstva — Do Peček . cz',
        'Počet zhlédnutí videozáznamů jednání zastupitelstva města Pečky '
        'na YouTube od roku 2022, s vyznačeným ustavujícím zasedáním.',
        # Odkázaná z /jednani/ (odstavec "Související") od 8. 10. 2026.
        # Statický snímek k datu lastmod.
        False, 'jednani', '2026-10-09'),
    'fbmonitoring': (
        '/o-webu/facebook-monitoring/facebook-mestopecky/',
        'Monitoring Facebooku města Pečky — Do Peček . cz',
        'Které měsíce z oficiálního facebookového profilu Města Pečky máme '
        'sesbírané a kolik příspěvků v nich vyšlo.',
        # Odkázaná z O webu -> Sociální sítě (u položky "Facebook — Město Pečky")
        # od 2. 10. 2026 — proto má lastmod a jde do sitemapy. Obsah
        # content/fbmonitoring.html GENERUJE o-webu/facebook-monitoring/summary.py
        # (statický snímek tabulky; zdrojová JSON jsou v .gitignore). Po každém
        # novém měsíci: pustit summary.py, build a přepsat lastmod níže.
        False, 'owebu', '2026-10-04'),
    'udmonitoring': (
        '/o-webu/uredni-deska-monitoring/',
        'Monitoring úřední desky města Pečky — Do Peček . cz',
        'Dokumenty vyvěšené na úřední desce města Pečky od roku 2015 po '
        'měsících: téma, datum vyvěšení a sejmutí, odkaz na detail na webu města.',
        # Odkázaná z O webu -> Odkazy (u položky "Oficiální web města") od
        # 6. 10. 2026 — proto má lastmod a jde do sitemapy. Obsah
        # content/udmonitoring.html GENERUJE o-webu/uredni-deska-monitoring/summary.py
        # ze souboru <rok>.txt (statický snímek). Po každé kontrole desky:
        # doplnit dokumenty do .txt, pustit summary.py, build a přepsat lastmod níže.
        False, 'owebu', '2026-10-06'),
    'redakce': (
        '/noviny/redakce.html', 'Kdo vede Pečecké noviny? — Do Peček . cz',
        'Kdo vedl redakci Pečeckých novin a kdo seděl v redakční radě '
        'od roku 2006 — podle tiráže jednotlivých čísel.',
        # Odkázaná z /noviny/ (odstavec "Související") od 8. 10. 2026 —
        # proto má lastmod a jde do sitemapy. Statická tabulka z tiráží novin.
        False, 'zpravodaj', '2026-10-08'),
    'changelog': (
        '/o-webu/changelog.html', 'Historie změn na webu — Do Peček . cz',
        'Přehled sekcí webu Do Peček . cz: kdy byl u každé naposledy '
        'zkontrolován zdroj a kdy se změnil obsah.',
        # Odkázaná z patičky každé stránky. Obsah content/changelog.html je
        # tabulka {{STAV_SEKCI}} (generuje build z README.md -> "Stav sekcí").
        # lastmod 'auto' = nejnovější datum "Změna" ze "Stav sekcí" (dopočítá
        # build_all), takže se nepíše ručně.
        False, 'owebu', 'auto'),
}


# cesta k README sekce (jak je zapsaná v tabulce "Stav sekcí") -> slug v MANIFEST
README_TO_SLUG = {
    'domu': 'domu',
    'jednani': 'jednani',
    'lide': 'lide',
    'noviny': 'zpravodaj',
    'o-webu': 'owebu',
    'peckybot': 'peckybot',
    'plan': 'plan',
    'telocvicna': 'telocvicna',
    'pokladna': 'pokladna',
    'kalendar': 'kalendar',
    'naobed': 'naobed',
    'pozemky': 'pozemky',
    'prostory': 'prostory',
    'smlouvy': 'smlouvy',
    'zakazky': 'zakazky',
    'volby': 'volby',
    'volby/2018': 'volby2018',
    'volby/2022': 'volby2022',
    'volby/2026': 'volby2026',
}


def read(path):
    return (ROOT / path).read_text(encoding='utf-8')


def esc(s):
    return (s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
             .replace('"', '&quot;'))


def build_noviny_issues():
    """Vygeneruje noviny/issues.json (slug + rok vydání) z pecky-noviny.json.
    Malý číselník pro odkazy typu „Pečecké noviny 12/2018“ (assets/helpers.js,
    jLinkRefs) — samotný pecky-noviny.json je kvůli textu stránek příliš velký."""
    import json
    src = json.loads((ROOT / 'noviny/pecky-noviny.json').read_text(encoding='utf-8'))
    issues = [{'slug': e['slug'], 'year': e['year']} for e in src.get('editions', []) if e.get('slug')]
    (ROOT / 'noviny/issues.json').write_text(
        json.dumps({'issues': issues}, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')


def build_org_colors():
    """Vygeneruje assets/org-colors.css z lide/organizations.json.

    Jediný zdroj barev organizací (politická uskupení, pořadatelé akcí…)
    jsou pole `color` a `color_bg` v organizations.json. Tady z nich
    vzniknou CSS proměnné --org-<id> a --org-<id>-bg; organizace
    s `css_class` (uskupení, party-*) dostanou navíc alias --<css_class>
    a --<css_class>-bg, na který se odkazují starší pravidla v styles.css.
    Organizace bez barvy proměnnou nemá — kód si drží fallback
    (var(--org-x, var(--ink-soft)) apod.).
    """
    doc = json.loads(read('lide/organizations.json'))
    hex_re = re.compile(r'^#[0-9A-Fa-f]{6}$')
    lines = ['/* VYGENEROVÁNO scripts/build.py z lide/organizations.json — NEEDITOVAT.',
             '   Barvu organizace měnit v organizations.json (pole color / color_bg),',
             '   pak spustit python3 scripts/build.py. */',
             ':root{']
    for o in doc.get('organizations', []):
        color, bg = o.get('color'), o.get('color_bg')
        if not color:
            continue
        for val in (color, bg):
            if val and not hex_re.match(val):
                raise SystemExit(f'CHYBA: organizace {o["id"]} má neplatnou barvu {val!r}.')
        name = o.get('short_name') or o.get('name') or o['id']
        lines.append(f'  /* {name} */')
        lines.append(f'  --org-{o["id"]}:{color};')
        if bg:
            lines.append(f'  --org-{o["id"]}-bg:{bg};')
        if o.get('css_class'):
            lines.append(f'  --{o["css_class"]}:var(--org-{o["id"]});')
            if bg:
                lines.append(f'  --{o["css_class"]}-bg:var(--org-{o["id"]}-bg);')
    lines.append('}')
    (ROOT / 'assets/org-colors.css').write_text('\n'.join(lines) + '\n', encoding='utf-8')


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
    """Vyrenderuje „Stav sekcí“ jako karty (details). Ve složeném stavu je vidět
    název sekce a stáří poslední změny, po rozbalení kontrola, režim, text
    „Co naposledy“ a odkaz do sekce. Datumy nesou data-date (ISO); text uvnitř
    je absolutní datum jako fallback, JS ho přepíše na stáří."""
    def datum(d, popisek):
        if d is None:
            return (f'<span class="stav-none" title="tahle sekce nemá externí '
                    f'zdroj ke kontrole">{popisek}: —</span>')
        odhad = ' data-odhad="1"' if d['odhad'] else ''
        title = ' title="odhad, přesné datum nedoloženo"' if d['odhad'] else ''
        return (f'{popisek}: <span data-date="{d["iso"]}"{odhad}{title}>'
                f'{esc(d["raw"])}{"&nbsp;?" if d["odhad"] else ""}</span>')

    out = ['<div class="stav-sekci">']
    for r in rows:
        out.append(
            '<details class="card stav-card">'
            f'<summary><span class="stav-name">{esc(r["name"])}</span>'
            f'<span class="stav-zmena">{datum(r["zmena"], "Změna")}</span>'
            '<span class="collapsible-arrow" aria-hidden="true">▾</span></summary>'
            '<div class="stav-body">'
            f'<p class="stav-meta"><span class="tag">{esc(r["rezim"])}</span> '
            f'{datum(r["kontrola"], "Kontrola")}</p>'
            f'<p class="stav-co">{esc(r["co"])}</p>'
            f'<p class="stav-link"><a href="{r["url"]}">Otevřít sekci →</a></p>'
            '</div></details>')
    out.append('</div>')
    return '\n'.join(out)


def lastmod_map(stav_rows):
    """{url: {'iso', 'raw', 'odhad'}} pro sekce, co mají datum "Změna" v
    tabulce Stav sekcí. Sdílený zdroj pro <lastmod> v sitemapě (build_sitemap)
    i pro viditelné "Aktualizováno" na stránce samotné (apply_lastmod) -
    jedno datum, dvě použití, žádné ruční psaní do content/<sekce>.html."""
    return {row['url']: row['zmena'] for row in stav_rows if row['zmena'] is not None}


TITLE_RE = re.compile(r'(<h2 class="title[^"]*">.*?</h2>)')


def iso_to_cz(iso):
    """'2026-09-20' -> '20. 9. 2026' (stejný zápis jako ve "Stav sekcí")."""
    y, m, d = iso.split('-')
    return f'{int(d)}. {int(m)}. {y}'


def apply_lastmod(content, lastmod):
    """Vloží "Aktualizováno: ..." hned před nadpis sekce (<h2 class="title">).
    Beze změny, pokud sekce nemá datum "Změna" v Stav sekcí (typicky Domů,
    která nemá vlastní <h2 class="title"> - nechybí tam co nahradit) nebo
    podstránky z EXTRA_PAGES (nemají řádek v tabulce vůbec)."""
    if lastmod is None:
        return content
    tag = (f'<p class="lastmod" data-date="{lastmod["iso"]}">'
           f'Aktualizováno: {lastmod["raw"]}</p>\n    ')
    new_content, n = TITLE_RE.subn(lambda m: tag + m.group(1), content, count=1)
    return new_content if n else content


# ===== Dashboard na homepage (Domů) =====
# Blok {{DASHBOARD}} v content/domu.html. Skládá se při buildu z dat, která
# už ověřily jednotlivé sekce - nic nového nevymýšlí, jen vybírá nejnovější
# položky a odkazuje zpátky do sekce. Budoucí položky (ohlášená jednání,
# nadcházející akce) nesou data-until: build jich vypíše víc, než je vidět
# (nadbytečné mají hidden), a common.js v prohlížeči skryje ty, co mezitím
# proběhly, a doplní další v pořadí - homepage tak nezastará mezi buildy.
DASH_KALENDAR_KATEGORIE = ('akce', 'volby', 'svoz', 'zastupitelstvo')  # kurzy by výpis zahltily
DASH_AKCE_VIDET, DASH_AKCE_REZERVA = 20, 25  # rezerva ~ týden bez buildu
DASH_AKCE_MIN = 5  # aspoň tolik karet celkem (jinak se přidávají další dny do Dalších akcí)
DASH_AKCE_BEZI = 5  # max. míst z DASH_AKCE_VIDET pro probíhající vícedenní akce
DASH_JEDNANI_PROBEHLA = 3
DASH_ZM_PO_DNI = 5  # pruh „Zastupitelstvo proběhlo“ visí na Domů tolik dní po konání
DNY_CZ = ['po', 'út', 'st', 'čt', 'pá', 'so', 'ne']


def _den_cz(iso):
    """'2026-10-07' -> 'st 7. 10.' (krátký zápis do výpisu)."""
    from datetime import date
    y, m, d = (int(x) for x in iso.split('-'))
    return f'{DNY_CZ[date(y, m, d).weekday()]} {d}. {m}.'


def _dash_card(title, href, link_text, body, key, head_link=None):
    # key = název dlaždice v bento mřížce (grid-area v assets/styles.css)
    title_html = esc(title).replace('\n', '<br>')  # \n v titulku = konec řádku
    h3 = f'<h3 class="display"><a href="{href}">{title_html}</a></h3>'
    if head_link:  # odkaz vpravo na řádku s nadpisem
        h3 = (f'<div class="dash-card-head">{h3}'
              f'<a class="dash-head-link" href="{href}">{esc(head_link)} →</a></div>')
    return (f'<div class="card dash-card dash-card--{key}">\n'
            f'  {h3}\n'
            f'{body}\n'
            + (f'  <a class="dash-more" href="{href}">{esc(link_text)} →</a>\n' if link_text else '') +
            f'</div>')


def _dash_jednani(dnes):
    meetings = json.loads(read('jednani/pecky-jednani.json'))['meetings']
    # jednání výborů ZM (jednani/vybory.json) — nečíslovaná, jen proběhlá;
    # slug stejný jako trvalý odkaz na stránce Jednání (#financni-vybor-…)
    vybory = json.loads(read('jednani/vybory.json'))['meetings']
    VYBOR_SLUG = {'Finanční výbor': 'financni-vybor', 'Kontrolní výbor': 'kontrolni-vybor'}
    # komise rady a pracovní skupina (komise.json), školská rada (skolska-rada.json)
    komise = (json.loads(read('jednani/komise.json'))['meetings']
              + json.loads(read('jednani/skolska-rada.json'))['meetings'])
    KOMISE_SLUG = {'Sportovní komise': 'sportovni-komise', 'Kulturní komise': 'kulturni-komise',
                   'Stavebně-dopravní komise': 'stavebni-komise',
                   'Pracovní skupina pro oslavy 100 let': 'pracovni-skupina',
                   'Sbor pro občanské záležitosti': 'sbor', 'Školská rada': 'skolska-rada'}
    VYBOR_SLUG.update(KOMISE_SLUG)
    vybory = vybory + komise
    def slug(m):
        return f'{VYBOR_SLUG.get(m["type"]) or m["type"].lower()}-{m["date"]}'
    def nazev(m):
        return m['type'] if m.get('number') is None else f'{m["type"]} {m["number"]}/{m["year"]}'

    probehla = sorted((m for m in meetings if m['date'] < dnes),
                      key=lambda m: m['date'], reverse=True)[:DASH_JEDNANI_PROBEHLA]
    if not probehla:
        raise SystemExit('CHYBA: dashboard - v jednani/pecky-jednani.json není žádné proběhlé jednání.')

    out = []
    out.append('  <h4>Poslední zveřejněné zápisy</h4>\n  <ul class="dash-list">')
    for m in probehla:
        bez_zapisu = '' if (m.get('links') or {}).get('minutes') else ' <span class="meta-note">zápis zatím nezveřejněn</span>'
        out.append(f'    <li><span><a href="/jednani/#{slug(m)}">{esc(nazev(m))}</a>{bez_zapisu}</span>'
                   f'<span class="rel-date" data-date="{m["date"]}">{esc(iso_to_cz(m["date"]))}</span></li>')
    out.append('  </ul>')
    # výbory zveřejňují zápisy se zpožděním, mezi nejnovějšími jednáními
    # Rady/ZM by se téměř neobjevily — proto poslední jednání každého zvlášť
    posledni_vybory = [max((m for m in vybory if m['type'] == t and m['date'] < dnes),
                           key=lambda m: m['date'], default=None) for t in VYBOR_SLUG]
    posledni_vybory = [m for m in posledni_vybory if m]
    if posledni_vybory:
        posledni_vybory.sort(key=lambda m: m['date'], reverse=True)
        out.append('  <h4>Výbory a komise</h4>\n  <ul class="dash-list">')
        for m in posledni_vybory:
            out.append(f'    <li><span><a href="/jednani/#{slug(m)}">{esc(nazev(m))}</a></span>'
                       f'<span class="rel-date" data-date="{m["date"]}">{esc(iso_to_cz(m["date"]))}</span></li>')
        out.append('  </ul>')
    return _dash_card('Poslední proběhlá jednání.\nRady, zastupitelstva i výborů', '/jednani/', 'Všechna jednání', '\n'.join(out), 'jednani')


ZM_DEN_CZ = ['v pondělí', 'v úterý', 've středu', 've čtvrtek', 'v pátek', 'v sobotu', 'v neděli']  # weekday() 0 = po


def _kdy_za(dny):
    """Doba do události: už dnes / už zítra / pozítří / za N dní / za N týdny.
    Stejná logika je v assets/common.js (přepočet v prohlížeči)."""
    if dny <= 0:
        return 'už dnes'
    if dny == 1:
        return 'už zítra'
    if dny == 2:
        return 'pozítří'
    if dny < 14:
        return f'za {dny} {"dny" if dny < 5 else "dní"}'
    return f'za {dny // 7} {"týdny" if dny < 35 else "týdnů"}'


def _zm_kdy(dny, weekday):
    """Titulek banneru zasedání: "Zasedání zastupitelstva už zítra" (doba zvýrazněná)."""
    return f'Zasedání zastupitelstva <mark class="banner-hl">{_kdy_za(dny)}</mark>'


def _volby_kdy(dny, probiha):
    """Titulek banneru voleb: "Volby do zastupitelstva města budou už zítra"
    (doba zvýrazněná), během hlasování "… právě probíhají"."""
    if probiha:
        return 'Volby do zastupitelstva města <mark class="banner-hl">právě probíhají</mark>'
    return f'Volby do zastupitelstva města budou <mark class="banner-hl">{_kdy_za(dny)}</mark>'


ICO_KAL = ('<svg class="kal-ico" viewBox="0 0 16 16" width="16" height="16" fill="none" stroke="currentColor" '
           'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
           '<rect x="2" y="3" width="12" height="11" rx="1.5"/><path d="M2 6.5h12M5 1.5v3M11 1.5v3"/></svg>')
ICO_PIN = ('<svg class="kal-ico" viewBox="0 0 16 16" width="16" height="16" fill="none" stroke="currentColor" '
           'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
           '<path d="M8 14.5s4.5-4.2 4.5-7.8a4.5 4.5 0 0 0-9 0C3.5 10.3 8 14.5 8 14.5z"/><circle cx="8" cy="6.7" r="1.6"/></svg>')
ICO_LUPA = ('<svg class="kal-ico" viewBox="0 0 16 16" width="16" height="16" fill="none" stroke="currentColor" '
            'stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><circle cx="6.8" cy="6.8" r="4.6"/><path d="M10.3 10.3L14 14"/></svg>')
ICO_YT = ('<svg class="kal-ico" viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">'
          '<path fill="#FF0000" d="M23.5 6.2a3 3 0 0 0-2.1-2.1C19.5 3.6 12 3.6 12 3.6s-7.5 0-9.4.5A3 3 0 0 0 .5 6.2C0 8.1 0 12 0 12s0 3.9.5 5.8a3 3 0 0 0 2.1 2.1c1.9.5 9.4.5 9.4.5s7.5 0 9.4-.5a3 3 0 0 0 2.1-2.1c.5-1.9.5-5.8.5-5.8s0-3.9-.5-5.8z"/>'
          '<path fill="#fff" d="M9.6 15.6V8.4l6.2 3.6z"/></svg>')


def _zm_avatary():
    """Blok avatarů 21 současných zastupitelů do banneru: starosta, ostatní
    radní (místostarostové, pak radní), nakonec zbylí zastupitelé. Zdroj:
    lide/people.json + affiliations.json (current = zdroj pravdy). Bez fotky
    iniciálový kroužek; každý avatar odkazuje na kartu osoby v Lidech."""
    people = {p['id']: p for p in json.loads(read('lide/people.json'))['people']}
    aff = json.loads(read('lide/affiliations.json'))['affiliations']
    poradi = {'starosta': 0, 'mistostarosta': 1, 'rada': 2}
    role = {}
    for a in aff:
        if a.get('current') and a['person_id'] in people:
            if a['role_type'] in poradi:
                role[a['person_id']] = min(role.get(a['person_id'], 9), poradi[a['role_type']])
            elif a['role_type'] == 'zastupitel':
                role.setdefault(a['person_id'], 3)
    lide = sorted(role, key=lambda pid: (role[pid], people[pid]['last_name'], people[pid]['first_name']))
    if not lide:
        return ''
    out = []
    for pid in lide:
        p = people[pid]
        jmeno = f'{p["first_name"]} {p["last_name"]}'
        popis = {0: 'starosta', 1: 'místostarosta', 2: 'radní', 3: 'zastupitel'}[role[pid]]
        if p['gender'] == 'f':
            popis = {'starosta': 'starostka', 'místostarosta': 'místostarostka', 'radní': 'radní',
                     'zastupitel': 'zastupitelka'}[popis]
        foto = (p.get('photos') or [{}])[0].get('url')
        if foto:
            vnitrek = f'<img src="{esc(foto)}" alt="{esc(jmeno)}" loading="lazy" width="56" height="56">'
        else:
            vnitrek = f'<span class="banner-av-init" aria-hidden="true">{esc(p["first_name"][0] + p["last_name"][0])}</span>'
        cls = ' banner-av--rada' if role[pid] < 3 else ''
        out.append(f'<a class="banner-av{cls}" href="/lide/#lide/osoba/{esc(pid)}" '
                   f'title="{esc(jmeno)} — {popis}" aria-label="{esc(jmeno)}, {popis}">{vnitrek}</a>')
    return ('<div class="banner-side"><p class="banner-side-title">Zastupitelstvo města</p>'
            f'<div class="banner-avatars">{"".join(out)}</div></div>')


# Témata, o kterých se na zastupitelstvu historicky jedná nejdéle (medián/průměr
# délky bodu z jednani/pecky-jednani.json, zasedání s videozáznamem). Slouží
# k výběru bodů do řádku "Bude se jednat o …" v banneru: (regex nad názvem bodu,
# fráze ve 6. pádu, váha ~ průměrná délka v minutách). Procedurální body
# (volba komisí, program, kontrola usnesení, diskuse, úkoly) se vynechávají.
ZM_TEMATA = [
    (r'tělocvičn', 'tělocvičně', 27),
    (r'úvěr', 'úvěru', 25),
    (r'^rozpočet \d{4}', None, 25),          # fráze se doplní z roku
    (r'\b(dodatek|dodatku|sod|smlouv)', 'dodatku ke smlouvě', 9),
    (r'rozpočtov\w+ opatření', 'rozpočtových opatřeních', 8),
    (r'pozemk', 'pozemcích', 6),
    (r'dotac', 'dotacích', 4),
]


def _zm_hot(m):
    """Řádek "🔥 Bude se jednat o …" z nejdelších témat na programu (max. 3,
    od nejdelšího) nebo '' když pozvánka žádné takové téma neobsahuje."""
    nalezeno = {}
    for a in m.get('agenda') or []:
        t = a['t'].lower()
        for rx, fraze, vaha in ZM_TEMATA:
            hit = re.search(rx, t)
            if not hit:
                continue
            if fraze is None:
                fraze = f'rozpočtu na rok {hit.group(0)[-4:]}'
            nalezeno[fraze] = max(nalezeno.get(fraze, 0), vaha)
    temata = sorted(nalezeno, key=lambda f: -nalezeno[f])[:3]
    if not temata:
        return ''
    text = ', '.join(temata[:-1]) + (' a ' if len(temata) > 1 else '') + temata[-1]
    return f'<p class="banner-hot">🔥 Bude se jednat o {esc(text)}</p>'


def _zm_akce(m, odkaz):
    """Tlačítka banneru: hlavní CTA "Živé vysílání…" (jen je-li známý odkaz na
    livestream) a vedle něj odkaz na program jednání (jen je-li znám z pozvánky)."""
    out = []
    live = (m.get('links') or {}).get('livestream')
    if live:
        out.append(f'<a class="banner-cta" href="{esc(live)}" target="_blank" rel="noopener">'
                   f'{ICO_YT}Živé vysílání{" od " + esc(m["time"]) if m.get("time") else ""}</a>')
    if m.get('agenda'):
        out.append(f'<a class="banner-link" href="{odkaz}">Program jednání</a>')
    return f'<div class="banner-actions">{"".join(out)}</div>' if out else ''


def _dash_zastupitelstvo(dnes):
    """Samostatný widget na úplném začátku Domů: ohlášené zastupitelstvo
    (jen ZM, ne Rada) a nejbližší volby z kalendáře. Vrací dvojici
    (banner zasedání, banner voleb); banner voleb se vkládá do bento mřížky.
    Chybějící část je ''.
    Budoucí ZM se vypíše víc (rezerva), common.js ukáže první, které ještě
    neproběhlo, a nezbyde-li žádná položka, schová celý widget - neshnije
    mezi buildy."""
    from datetime import date as _date
    meetings = json.loads(read('jednani/pecky-jednani.json'))['meetings']
    zm = sorted((m for m in meetings if m['type'] == 'Zastupitelstvo' and m['date'] >= dnes),
                key=lambda m: m['date'])[:3]
    events = json.loads(read('kalendar/udalosti.json'))['events']
    volby = sorted((e for e in events if e['category'] == 'volby'
                    and (e.get('date_end') or e['date']) >= dnes), key=lambda e: e['date'])[:1]
    po = _dash_zm_po(meetings, dnes)
    if not zm and not volby and not po:
        return '', ''
    avatary = _zm_avatary()
    out = ['<div class="dash-zm">'] if zm else []
    out_v = []
    if zm:
        out.append('  <ul class="dash-list banner" data-max="1">')
    for i, m in enumerate(zm):
        den = ['Pondělí', 'Úterý', 'Středa', 'Čtvrtek', 'Pátek', 'Sobota', 'Neděle'][_date.fromisoformat(m['date']).weekday()]
        kdy = f'{den}, {iso_to_cz(m["date"])}' + (f' v {m["time"]}' if m.get('time') else '')
        odkaz = f'/jednani/#zastupitelstvo-{m["date"]}'
        dny = (_date.fromisoformat(m['date']) - _date.fromisoformat(dnes)).days
        # výchozí text z doby buildu; common.js ho v prohlížeči přepočítá
        za = _zm_kdy(dny, _date.fromisoformat(m['date']).weekday())
        misto = (f'<span class="banner-meta-item">{ICO_PIN}<span>{esc(m["venue"].split(",")[0].strip())}</span></span>'
                 if m.get('venue') else '')
        out.append(f'    <li data-until="{m["date"]}"{" hidden" if i else ""}>'
                   f'<div class="banner-body">'
                   f'<h3 class="banner-title"><span class="dash-zm-kdy">{za}</span></h3>'
                   f'<p class="banner-meta"><span class="banner-meta-item">{ICO_KAL}<span>{esc(kdy)}</span></span>{misto}</p>'
                   f'{_zm_hot(m)}{_zm_akce(m, odkaz)}</div>'
                   f'{avatary}'
                   f'<p class="banner-note">Jednání je veřejné. Ze zasedání bude dostupný audio i video záznam.</p></li>')
    if zm:
        out.append('  </ul>')
        out.append('</div>')
    for e in volby:
        konec = e.get('date_end') or e['date']
        dny = (_date.fromisoformat(e['date']) - _date.fromisoformat(dnes)).days
        rozsah = (f'{int(e["date"][8:])}.–{iso_to_cz(konec)}' if konec != e['date'] else iso_to_cz(e['date']))
        dnu = ['Pondělí', 'Úterý', 'Středa', 'Čtvrtek', 'Pátek', 'Sobota', 'Neděle']
        d1, d2 = _date.fromisoformat(e['date']), _date.fromisoformat(konec)
        dny_txt = (dnu[d1.weekday()] if d1 == d2 else
                   f'{dnu[d1.weekday()]} a {dnu[d2.weekday()].lower()}' if (d2 - d1).days == 1 else
                   f'{dnu[d1.weekday()]} až {dnu[d2.weekday()].lower()}')
        out_v.append(f'<div class="dash-zm dash-zm--volby">\n  <ul class="dash-list banner banner--slate">\n    <li data-from="{e["date"]}" data-until="{konec}">'
                   f'<div class="banner-body"><h3 class="banner-title">'
                   f'<span class="dash-volby-kdy">{_volby_kdy(dny, dny < 0)}</span></h3>'
                   f'<p class="banner-meta"><span class="banner-meta-item">{ICO_KAL}<span>{dny_txt}, {esc(rozsah)}</span></span></p>'
                   f'<div class="banner-actions"><a class="banner-cta" href="/volby/">Jak se volí v Pečkách?</a></div>'
                   f'</div></li>\n  </ul>\n</div>')
    return '\n'.join(out + ([po] if po else [])), '\n'.join(out_v)


def _zm_po_kdy(dny):
    """„proběhlo včera / předevčírem / před N dny“ (dny = kolik dní je po zasedání)."""
    if dny <= 0:
        return 'proběhlo dnes'
    if dny == 1:
        return 'proběhlo včera'
    if dny == 2:
        return 'proběhlo předevčírem'
    return f'proběhlo před {dny} dny'


def _dash_zm_po(meetings, dnes):
    """Pruh pod bannerem zasedání: po konání zastupitelstva visí DASH_ZM_PO_DNI dní
    a odkazuje na detail jednání (zápis a usnesení). Vypíše se každé ZM, které
    bylo nebo teprve bude v tomto okně; common.js ukáže jen to, jehož okno
    (data-od až data-do) zahrnuje dnešek, takže pruh nezastará mezi buildy."""
    from datetime import date as _date, timedelta
    d0 = _date.fromisoformat(dnes)
    kand = sorted((m for m in meetings if m['type'] == 'Zastupitelstvo'
                   and _date.fromisoformat(m['date']) >= d0 - timedelta(days=DASH_ZM_PO_DNI)),
                  key=lambda m: m['date'])[:4]
    if not kand:
        return ''
    out = ['<div class="dash-zmpo" hidden>', '  <ul class="dash-zmpo-list">']
    for m in kand:
        dm = _date.fromisoformat(m['date'])
        od, do = dm + timedelta(days=1), dm + timedelta(days=DASH_ZM_PO_DNI)
        links = m.get('links') or {}
        if links.get('minutes'):
            stav = 'zápis je zveřejněný'
        elif m.get('resolutions'):
            stav = f'přijato {len(m["resolutions"])} usnesení'
        else:
            stav = 'zápis zatím nezveřejněn'
        # po konání je záznam na YouTube (odkaz 'youtube', případně původní livestream)
        if m['date'] < dnes and (links.get('youtube') or links.get('livestream')):
            stav += ' · video ze zasedání je k dispozici'
        nazev = f'Zastupitelstvo {m["number"]}/{m["year"]}'
        out.append(
            f'    <li data-date="{m["date"]}" data-od="{od.isoformat()}" data-do="{do.isoformat()}" hidden>'
            f'<a class="dash-zmpo-link" href="/jednani/#zastupitelstvo-{m["date"]}">'
            f'<span class="zmpo-text"><strong>{esc(nazev)}</strong> <span class="zmpo-kdy">{_zm_po_kdy((d0 - dm).days)}</span>'
            f' · <span class="zmpo-stav">{stav}</span></span>'
            f'<span class="zmpo-sipka" aria-hidden="true">→</span></a></li>')
    out += ['  </ul>', '</div>']
    return '\n'.join(out)


def _dash_akce_li(e, i, hidden=False):
    vicedenni = e.get('date_end') and e['date_end'] != e['date']
    cas = e['time'] if e.get('time') and not e.get('all_day') else ''
    cas_txt = f'{cas}–{e["time_end"]}' if cas and e.get('time_end') else cas  # např. sběrný dvůr 13:00–16:00
    kdy = (f'{_den_cz(e["date"])} – {_den_cz(e["date_end"])}' if vicedenni else _den_cz(e['date']))
    if cas_txt:
        kdy += f' {cas_txt}'
    kdo = f'<span class="ev-org">{esc(e["organizer_name"])}</span>' if e.get('organizer_name') else ''
    # odkaz vede na originální zdroj události; bez něj na kalendář
    zdroj = e.get('link') or f'/kalendar/#{e["date"][:7]}/seznam'
    cizi = ' target="_blank" rel="noopener"' if zdroj.startswith('http') else ''
    data_from = f' data-from="{e["date"]}"' if vicedenni else ''
    data_cas = f' data-time="{esc(cas)}" data-time-text="{esc(cas_txt)}"' if cas else ''
    # chip (dnes 17:00 / zítra / za N dní) a text data (trvá do …) složí common.js
    # podle dnešního dne; popisky dnů předává build (jediný zdroj českých zkratek)
    popisky = f' data-den="{_den_cz(e["date"])}" data-den-end="{_den_cz(e["date_end"]) if vicedenni else ""}"'
    org = e.get('organizer')
    # barva podle pořadatele (--org-<id> z assets/org-colors.css); bez barvy fallback v CSS
    barva = f' style="--org-c:var(--org-{org});--org-c-bg:var(--org-{org}-bg)"' if org else ''
    return (f'    <li class="dash-event"{barva} data-until="{e.get("date_end") or e["date"]}"'
            f'{data_from}{data_cas}{popisky}{" hidden" if hidden else ""}>'
            f'<a class="card" href="{esc(zdroj)}"{cizi}>'
            f'<span class="ev-when"><span class="tag probiha fut-chip" data-date="{e["date"]}">plánováno</span>'
            f'<span class="ev-date">{esc(kdy)}</span></span>'
            f'<span class="ev-what"><span class="ev-title">{esc(e["title"])}</span>{kdo}</span></a></li>')


def _dash_kalendar(dnes):
    events = json.loads(read('kalendar/udalosti.json'))['events']
    budouci = [e for e in events if e['category'] in DASH_KALENDAR_KATEGORIE
               and (e.get('date_end') or e['date']) >= dnes]
    def probiha(e):
        return bool(e.get('date_end')) and e['date'] < dnes
    def cas(e):
        return e['time'] if e.get('time') and not e.get('all_day') else ''
    # pořadí: akce dnešního dne (s přesným časem napřed), pak "Probíhající" vícedenní
    # (začaly před dneškem), pak další dny; common.js řadí stejně podle dne v prohlížeči
    nove = sorted((e for e in budouci if not probiha(e)),
                  key=lambda e: (e['date'] > dnes, e['date'], not cas(e), cas(e)))
    bezi = sorted((e for e in budouci if probiha(e)),
                  key=lambda e: (e['date_end'], e['date'], not cas(e), cas(e)))
    nove = nove[:DASH_AKCE_VIDET + DASH_AKCE_REZERVA]
    bezi = bezi[:DASH_AKCE_REZERVA]
    dnesni = [e for e in nove if e['date'] <= dnes]
    pozdeji = [e for e in nove if e['date'] > dnes]
    pool = dnesni + bezi + pozdeji
    # z celkových 20 míst jich má "Probíhající" vyhrazeno až DASH_AKCE_BEZI (jinak by je
    # akce s časem vždy vytlačily); common.js počítá stejně
    mist_nove = DASH_AKCE_VIDET - min(len(bezi), DASH_AKCE_BEZI)
    # "Další akce" jen z jediného dne (nejbližšího po dnešku, kde něco je); je-li
    # dohromady míň než DASH_AKCE_MIN karet, přidávají se další dny (celé), dokud
    # jich není aspoň tolik. common.js počítá stejně.
    povolene_dny, pocet = set(), len(dnesni) + min(len(bezi), DASH_AKCE_BEZI)
    for den in sorted({e['date'] for e in pozdeji}):
        if povolene_dny and pocet >= DASH_AKCE_MIN:
            break
        povolene_dny.add(den)
        pocet += sum(1 for e in pozdeji if e['date'] == den)
    out = [f'  <ul class="dash-akce" data-max="{DASH_AKCE_VIDET}" data-max-bezi="{DASH_AKCE_BEZI}">']
    n_nove = n_bezi = n_pozdeji = 0
    for i, e in enumerate(pool):
        je_bezi = probiha(e)
        if je_bezi and n_bezi == 0:
            out.append('    <li class="dash-group dash-group--bezi">Probíhající</li>')
        if e['date'] > dnes and not je_bezi and not n_pozdeji:
            out.append('    <li class="dash-group dash-group--dalsi">Další akce</li>')
        n_pozdeji += e['date'] > dnes
        if je_bezi:
            skryt = n_bezi >= DASH_AKCE_BEZI
            n_bezi += 1
        else:
            skryt = n_nove >= mist_nove or (e['date'] > dnes and e['date'] not in povolene_dny)
            n_nove += 1
        out.append(_dash_akce_li(e, i, hidden=skryt))
    out.append('    <li class="dash-empty"' + ('' if not pool else ' hidden') +
               '>Žádná nadcházející akce zatím není v kalendáři zapsaná.</li>')
    out.append('  </ul>')
    out.append('  <a class="dash-more dash-more--center" href="/kalendar/">Další ...</a>')
    return _dash_card('Aktuality', '/kalendar/', None, '\n'.join(out), 'kalendar', head_link='📅 Celý kalendář')


def _dash_noviny():
    """Zelený banner Pečeckých novin na Domů: obálka posledního čísla vlevo,
    počet vydání v archivu, tlačítko do vyhledávání a odkaz na redakci."""
    editions = json.loads(read('noviny/pecky-noviny.json'))['editions']
    ed = max(editions, key=lambda e: e['slug'])
    pdf = ed['url'] or f'/noviny/Data/PN%20{ed["year"]}/{ed["slug"]}.pdf'
    obalka = f'noviny/pages/{ed["slug"]}/1.jpg'
    img = (f'<a class="banner-media" href="{pdf}" title="Nejnovější číslo: {esc(ed["label"])}">'
           f'<img src="/{obalka}" alt="Titulní strana Pečeckých novin {esc(ed["label"])}" loading="lazy"></a>'
           if (ROOT / obalka).exists() else '')
    return ('<div class="banner banner--green banner--media dash-card--noviny">\n'
            f'  {img}\n'
            '  <div class="banner-body">\n'
            f'    <h3 class="banner-title"><span class="banner-hl">{len(editions)} vydání</span> novin v archivu</h3>\n'
            '    <p class="banner-text">který se dá prohledávat</p>\n'
            '    <div class="banner-actions">'
            f'<a class="banner-cta" href="/noviny/">{ICO_LUPA}Hledat v novinách</a>'
            '<a class="banner-link" href="/noviny/redakce.html">Redakce</a></div>\n'
            '  </div>\n'
            '</div>')


def _dash_zmeny():
    # Banner "Nově na webu" (#flashnews) se spravuje plně ručně v
    # domu/flashnews.json: [{"emoji", "text" (3-4 slova), "url"}], pořadí = pořadí
    # střídání. Nic se neodvozuje z jiných dat - odkazy vybírá vlastník webu.
    items = json.loads(read('domu/flashnews.json'))
    out = ['<div id="flashnews" class="banner banner--yellow dash-nove dash-card--zmeny">',
           '  <h3 class="dash-nove-title"><button type="button" class="dash-nove-toggle" aria-expanded="false" title="Zobrazit všechny novinky">Nově na webu</button></h3>',
           '  <ul class="dash-nove-list">']
    for it in items:
        out.append(f'    <li><a href="{it["url"]}">{it["emoji"]} {esc(it["text"])}</a></li>')
    out += ['  </ul>',
            '  <svg class="dash-nove-chevron" viewBox="0 0 24 24" width="20" height="20" aria-hidden="true">'
            '<path d="M6 9l6 6 6-6" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg>',
            '</div>']
    return '\n'.join(out)


def render_dashboard(stav_rows):
    from datetime import date
    dnes = date.today().isoformat()
    zm, volby = _dash_zastupitelstvo(dnes)
    # dva samostatné sloupce (vlevo banner voleb + jednání + noviny, vpravo flashnews, akce): sloupce se nenatahují podle sebe, takže mezi bloky nevznikají mezery;
    # na užších displejích se sloupce rozpustí do mřížky (grid-area v styles.css)
    levy = ([volby] if volby else []) + [_dash_noviny(), _dash_jednani(dnes)]
    pravy = [_dash_zmeny(), _dash_kalendar(dnes)]
    sloupec = lambda karty: '<div class="dash-col">\n' + '\n'.join(karty) + '\n</div>'
    return (zm + '\n'
            + f'<div class="dash-grid dash-bento{" dash-bento--volby" if volby else ""}">\n'
            + sloupec(levy) + '\n' + sloupec(pravy) + '\n</div>')


# Znovupoužitelná komponenta "rozcestník volebních ročníků" - řádek buttonů,
# od nejnovějšího po nejstarší. Používá se jak na rozcestníku /volby/ (bez
# nadpisu, mezi perexem a grafem účasti), tak nad nadpisem každé jednotlivé
# stránky ročníku (/volby/2018/, /volby/2022/, /volby/2026/), kde navíc
# zvýrazní aktivní rok. Zdroj pravdy pro seznam ročníků je tenhle slovník -
# při založení dalšího ročníku (po 2026) přidat sem, do MANIFEST i do
# volby/README.md.
VOLBY_ROCNIKY = ['2026', '2022', '2018']  # nejnovější -> nejstarší
VOLBY_SLUG_TO_ROK = {'volby2026': '2026', 'volby2022': '2022', 'volby2018': '2018'}


def render_volby_rocniky(current_slug):
    current_rok = VOLBY_SLUG_TO_ROK.get(current_slug)
    items = []
    # První položka je popisek/odkaz zpět na rozcestník /volby/ - na
    # samotném rozcestníku není kam odkazovat, takže tam není klikací.
    if current_slug == 'volby':
        items.append('<span class="year-btn year-btn-label" aria-current="page">Volby:</span>')
    else:
        items.append('<a class="year-btn year-btn-label" href="/volby/">Volby:</a>')
    for rok in VOLBY_ROCNIKY:
        cls = 'year-btn active' if rok == current_rok else 'year-btn'
        items.append(f'<a class="{cls}" href="/volby/{rok}/">{rok}</a>')
    return ('<nav class="year-nav" aria-label="Volební ročníky">\n  '
            + '\n  '.join(items) + '\n</nav>')


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
        is_election_page = current_slug in {'volby', 'volby2018', 'volby2022', 'volby2026'}
        return ' active' if slug == current_slug or (slug == 'volby' and is_election_page) else ''
    return re.sub(r'\{\{ACTIVE:([a-z0-9]+)\}\}', repl, html)


def build_nav(current_slug):
    # Slogan v hlavičce jen na homepage
    tagline = (f'    <p class="tagline">{SLOGAN}</p>\n'
               if current_slug == 'domu' else '')
    return apply_active(read('assets/nav.html').replace('{{TAGLINE}}', tagline), current_slug)


def out_file_for(path):
    """'/' -> index.html; '/jednani/' -> jednani/index.html;
    '/jednani/absence.html' -> jednani/absence.html (podstránka, ne adresář)"""
    if path == '/':
        return ROOT / 'index.html'
    if path.endswith('.html'):
        return ROOT / path.lstrip('/')
    return ROOT / path.strip('/') / 'index.html'


def build_all(stav_rows=None):
    page_tpl = read('templates/page.html')
    footer_tpl = read('assets/footer.html')
    rows = stav_rows or parse_stav_sekci()
    stav_sekci = render_stav_sekci(rows)
    lastmods = lastmod_map(rows)
    written = []
    extra_written = []
    extra_indexed = []  # podstránky z EXTRA_PAGES s lastmod (odkázané -> patří do sitemapy)

    stranky = [(slug, path, title, desc, helpers, slug, False, None)
               for slug, (path, title, desc, helpers) in MANIFEST.items()]
    stranky += [(slug, path, title, desc, helpers, nav_slug, True, lastmod)
                for slug, (path, title, desc, helpers, nav_slug, lastmod) in EXTRA_PAGES.items()]

    nejnovejsi_zmena = max((r['zmena']['iso'] for r in rows if r['zmena'] is not None), default=None)

    for slug, path, title, desc, needs_helpers, nav_slug, je_extra, extra_lastmod in stranky:
        if extra_lastmod == 'auto':
            extra_lastmod = nejnovejsi_zmena
        content = read(f'content/{slug}.html')
        content = content.replace('{{STAV_SEKCI}}', stav_sekci)
        if je_extra:
            if extra_lastmod is not None:
                content = apply_lastmod(
                    content, {'iso': extra_lastmod, 'raw': iso_to_cz(extra_lastmod), 'odhad': False})
        else:
            content = apply_lastmod(content, lastmods.get(path))
        if '{{DASHBOARD}}' in content:
            content = content.replace('{{DASHBOARD}}', render_dashboard(rows))
        if slug in VOLBY_SLUG_TO_ROK or slug == 'volby':
            content = content.replace('{{VOLBY_ROCNIKY}}', render_volby_rocniky(slug))
        nav = build_nav(nav_slug)
        footer = apply_active(footer_tpl, nav_slug)
        head_scripts = '<script src="/assets/helpers.js"></script>' if needs_helpers else ''
        if je_extra and extra_lastmod is None:
            head_scripts = '<meta name="robots" content="noindex">\n' + head_scripts

        html = page_tpl
        html = html.replace('{{TITLE}}', title)
        html = html.replace('{{DESCRIPTION}}', desc)
        html = html.replace('{{PATH}}', path)
        html = html.replace('{{SITE_DOMAIN}}', SITE_DOMAIN)
        html = html.replace('{{GA_MEASUREMENT_ID}}', GA_MEASUREMENT_ID)
        html = html.replace('{{HEAD_SCRIPTS}}', head_scripts)
        html = html.replace('{{NAV}}', nav)
        html = html.replace('{{CONTENT}}', content)
        html = html.replace('{{FOOTER}}', footer)
        html = html.replace('{{SITE_BASE_PATH}}', SITE_BASE_PATH)
        html = nbsp_html(html)  # české pevné mezery, viz TYPOGRAFIE.md
        html = apply_base_path(html)

        out_path = out_file_for(path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(html, encoding='utf-8')
        (extra_written if je_extra else written).append((slug, out_path, path))
        if je_extra and extra_lastmod is not None:
            extra_indexed.append((slug, out_path, path, extra_lastmod))

    return written, extra_written, extra_indexed


def build_sitemap(written, stav_rows, extra_indexed=None):
    """Vygeneruje sitemapu s datem poslední obsahové změny sekce.

    Tabulka „Stav sekcí“ v README je projektový changelog a její sloupec
    „Změna“ je zdroj pravdy pro <lastmod>. Datum kontroly sem nepatří:
    kontrola bez změny obsahu nemění stránku, kterou má vyhledávač indexovat.
    """
    lastmod_by_path = {url: d['iso'] for url, d in lastmod_map(stav_rows).items()}
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for slug, out_path, path in written:
        lastmod = lastmod_by_path.get(path)
        if lastmod is None:
            raise SystemExit(f'CHYBA: pro sitemapu chybí datum změny sekce {slug}.')
        lines.extend([
            '  <url>',
            f'    <loc>{SITE_DOMAIN}{path}</loc>',
            f'    <lastmod>{lastmod}</lastmod>',
            '  </url>',
        ])
    for slug, out_path, path, lastmod in (extra_indexed or []):
        lines.extend([
            '  <url>',
            f'    <loc>{SITE_DOMAIN}{path}</loc>',
            f'    <lastmod>{lastmod}</lastmod>',
            '  </url>',
        ])
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
    build_org_colors()
    build_noviny_issues()
    build_peckybot_index()
    stav_rows = parse_stav_sekci()
    written, extra_written, extra_indexed = build_all(stav_rows)
    build_sitemap(written, stav_rows, extra_indexed)
    indexed_slugs = {slug for slug, *_ in extra_indexed}
    hidden_count = len([e for e in extra_written if e[0] not in indexed_slugs])
    print(f'Vygenerováno {len(written)} stránek '
          f'(+ {len(extra_written)} podstránek z EXTRA_PAGES, '
          f'z toho {hidden_count} neprolinkovaných) '
          f'+ sitemap.xml + robots.txt.')
    if '--no-check' not in sys.argv:
        print('Validace (tag balance + JS syntax):')
        ok = validate(written + extra_written)
        if not ok:
            print('NĚKTERÉ STRÁNKY MAJÍ CHYBU — viz výš.')
            sys.exit(1)
        print('Vše OK.')
