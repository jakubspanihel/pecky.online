#!/usr/bin/env python3
"""
Aktualizace všech odkazů na katastrální parcely na webu pecky.online —
jediný skript pro dvě navazující věci:

A) Sekce Pozemky (panel-pozemky v content/pozemky.html): tabulky
   Nákup/Prodej sestavené z usnesení o prodeji/nákupu pozemku, s klikacím
   sloupcem Parcela.
B) Obecné prolinkování zmínek "parc. NNNN" kdekoli v textu usnesení
   a bodů programu v sekci Jednání (jLinkParcely() v content/jednani.html) —
   dřív jednani/katastr-odkazy.json, teď parcely-odkazy.json
   generovaný tímhle skriptem.

DŮLEŽITÉ (od migrace na vícestránkový web, ARCHITEKTURA-MIGRACE.md):
tenhle skript edituje content/pozemky.html, ne přímo veřejnou stránku —
po jeho běhu je vždy potřeba ještě spustit `python3 scripts/build.py`,
ať se změna promítne i do vygenerovaného pozemky/index.html.

Co dělá (v pořadí):
1. Načte/aktualizuje jednani/parcely-pozemky.json — katastr-přesnou
   cache "katastr|číslo parcely" -> RUIAN ID (zdroj pravdy pro obě části A i B).
2. (A) Projde usnesení o prodeji/nákupu pozemku, vytáhne parcelní číslo,
   katastr, cenu, klasifikuje nákup/prodej, dohledá chybějící RUIAN ID
   a přegeneruje obě HTML tabulky přímo v content/pozemky.html. Ověří
   balanci HTML tagů po zásahu.
3. (B) Projde úplně všechna usnesení a body programu (ne jen ty
   o pozemcích), najde všechny zmínky "parc. NNNN", pro každé číslo
   zjistí katastr ze všech míst, kde se objevuje — pokud se katastr
   napříč výskyty shoduje, dohledá RUIAN ID a přidá do ploché mapy
   parcely-odkazy.json; pokud koliduje (stejné číslo, různý katastr —
   viz POZOR níže), číslo se záměrně nepodlinkuje.

POZOR — proč katastr-odkazy.json (do 23. 8. 2026) obsahoval chybu a byl smazán:
Byl to globální mapa "číslo parcely -> URL" bez rozlišení katastrálního
území, ale číslo parcely je unikátní jen v rámci jednoho katastru —
různé katastry mají běžně stejná čísla. Potvrzený příklad: parcela
"254" existuje jak v k.ú. Pečky (362 m²), tak jako 254/1 a 254/2 v k.ú.
Velké Chvalovice (483 a 36 m²) — stará mapa měla pro klíč "254" jen
jednu z nich, špatnou pro usnesení, které mluvilo o té druhé. Tenhle
skript už tuhle třídu chyby nemůže zopakovat — u kolidujících čísel
raději nepodlinkuje (viz build_general_links), než aby odkázal na
špatnou parcelu.

Spouštět: `python3 jednani/scripts/update-pozemky.py`
(z kořene repa; síťové dohledávání běží jen pro nová čísla, jinak rychlé).
"""
import datetime
import json
import re
import sys
import time
import html
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
JEDNANI_JSON = ROOT / 'jednani' / 'pecky-jednani.json'
CACHE_JSON = ROOT / 'jednani' / 'parcely-pozemky.json'
POZEMKY_CONTENT = ROOT / 'content' / 'pozemky.html'
TODAY = datetime.date.today().isoformat()

# katastrální území použitá v tabulkách Pozemky a jejich kód (kodKuDr na vdp.cuzk.gov.cz)
# POZOR: u víceznačných názvů (např. "Radim" existuje jako "Radim", "Radim u Jičína",
# "Radim u Kolína" atd.) vybrat konkrétní kód ručně přes vdp.cuzk.gov.cz/vdp/ruian/parcely
# (vyhledání dle katastrálního území) — needit hádat podle prvního našeptaného výsledku.
KAT_CODES = {
    'Pečky': '718823',
    'Velké Chvalovice': '778842',
    'Dobřichov': '627801',
    'Plaňany': '721387',
    'Blinka': '721361',
    'Tatce': '765171',
    'Radim': '737780',  # = "Radim u Kolína" (NE plain "Radim", to je jiné k.ú. jinde v ČR)
}

# ruční přepisy pro parcely, které se v mezičase rozdělily (kmenové číslo bez
# poddělení už v aktuální evidenci neexistuje, ale usnesení jej tak uvádí) —
# vybrané sub-parcely odpovídají výměře/kontextu v textu usnesení, viz
# katastr-parcely-v-usneseních.md / poznámka u "531" a "254" v tomto skriptu.
MANUAL_OVERRIDES = {
    ('Dobřichov', '164'): '34411757010',       # pozemková (ne "st. 164" stavební)
    ('Pečky', '531'): '98114311010',            # 531/1 — původní 531 (12 345 m2) se rozdělila na 531/1+531/2
    ('Velké Chvalovice', '254'): '103482869010',  # 254/2 (36 m2) — odpovídá "prodej části pozemku cca 36 m2"
}

SALE_KW = re.compile(r'prodej|prodat|prodává|prodeji|koup[ei]|odkoup|výkup|nákup|nakoupit', re.I)
PARC_ITEM_RE = re.compile(r'č\.?\s*p(?:arc)?\.?\s*(\d+(?:/\d+)?)', re.I)
KATASTR_RE = re.compile(r'k\.?\s*ú\.?\s*([A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ][\wÁ-ž]*(?:\s+[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ][\wÁ-ž]*)*)')
# fallback pro případy, kdy text zmiňuje obec/katastr jen skloněně a bez "k.ú." prefixu
# (např. "ve Velkých Chvalovicích") — porovnání podle neměnného slovního základu, ne přesné shody
KATASTR_STEM_FALLBACK = [
    ('Chvalovic', 'Velké Chvalovice'),
    ('Dobřichov', 'Dobřichov'),
    ('Plaňan', 'Plaňany'),
    ('Tatc', 'Tatce'),
    ('Blink', 'Blinka'),
]
LV_RE = re.compile(r'LV\s*\d+', re.I)
CELK_RE = re.compile(r'celkov\w*\s+(?:kupní\s+)?cen\w*[^.]*?([\d][\d\s.,]*\d)\s*,?-?\s*Kč(\s*bez DPH)?', re.I)
PERSQM_RE = re.compile(r'([\d][\d\s.,]{0,10}\d)\s*,?-?\s*Kč\s*/{1,2}\s*m\s*2', re.I)
ANYPRICE_RE = re.compile(r'([\d][\d\s.,]{0,12}\d)\s*,?-?\s*Kč', re.I)

# usnesení, která obsahují klíčová slova, ale nejsou skutečný nákup/prodej
# (společné položky programu sdílející item-label se skutečným usnesením) —
# doplňovat ručně, pokud se objeví další podobný případ.
EXCLUDE_N = {'UZ-38-5/21'}  # mandát k přípravě projektu na už koupených pozemcích, ne nová koupě


def classify(item):
    return 'prodej' if re.search(r'prodej|prodat|prodává', item.lower()) else 'nákup'


def detect_katastr(*texts):
    """Zkusí určit katastrální území z jednoho nebo více textů (typicky item + text
    usnesení, nebo jen text bodu programu). Vrací '' pokud se nepodaří — needit hádat."""
    for t in texts:
        if not t:
            continue
        if 'V.Ch' in t:
            # zkratka "k.ú. V.Ch." by generický regex níže matchnul jen jako "V" (zastaví se na tečce)
            return 'Velké Chvalovice'
        kat_m = KATASTR_RE.search(t)
        if kat_m:
            return kat_m.group(1).strip()
    for t in texts:
        if not t:
            continue
        for stem, name in KATASTR_STEM_FALLBACK:
            if stem in t:
                return name
    return ''


def norm_num(s):
    s = s.strip().rstrip('.,').replace(' ', '')
    prev = None
    while prev != s:
        prev = s
        s = re.sub(r'[.,](?=\d{3}(\D|$))', '', s)
    s = re.sub(r'[.,]\d{1,2}$', '', s)
    try:
        return int(s)
    except ValueError:
        return None


def extract_rows(data):
    rows = []
    for m in data['meetings']:
        for r in m['resolutions']:
            item = r.get('item', '')
            if r['n'] in EXCLUDE_N:
                continue
            if not (SALE_KW.search(item) and re.search(r'pozemk|parc', item, re.I)):
                continue
            text = re.sub(r'\s+', ' ', r.get('text', '') or '')

            parcs = PARC_ITEM_RE.findall(item) or PARC_ITEM_RE.findall(text)
            parc_list = list(dict.fromkeys(parcs))
            if len(parc_list) > 4:
                parc = ', '.join(parc_list[:4]) + f' + {len(parc_list) - 4} dalších'
            else:
                parc = ', '.join(parc_list)
            if not parc:
                lvs = LV_RE.findall(item) or LV_RE.findall(text)
                parc = ', '.join(dict.fromkeys(lvs)) if lvs else ''

            kat = detect_katastr(item, text)

            celk_m = CELK_RE.search(text)
            persqm_m = PERSQM_RE.search(text)
            price_disp, price_num = '', None
            if celk_m:
                num = norm_num(celk_m.group(1))
                price_num = num
                if num:
                    price_disp = f'{num:,}'.replace(',', ' ') + ' Kč' + (' bez DPH' if celk_m.group(2) else '')
            else:
                any_m = ANYPRICE_RE.search(text)
                if persqm_m and (not any_m or persqm_m.start() <= (any_m.start() if any_m else 1 << 30)):
                    num = norm_num(persqm_m.group(1))
                    if num:
                        price_disp = f'{num:,}'.replace(',', ' ') + ' Kč/m2'
                elif any_m:
                    num = norm_num(any_m.group(1))
                    price_num = num
                    if num:
                        price_disp = f'{num:,}'.replace(',', ' ') + ' Kč'

            rows.append(dict(
                date=m['date'], typ=r['n'][1] if False else ('Zastupitelstvo' if r['n'].startswith('UZ') else 'Rada'),
                n=r['n'], item=item, parc=parc, kat=kat, cls=classify(item),
                price_disp=price_disp, price_num=price_num, url=r.get('url', ''),
                meeting_uuid=m.get('uuid', ''), meeting_number=m.get('number'),
            ))
    rows.sort(key=lambda x: x['date'], reverse=True)

    # dedup: "kanonický" řádek = zastupitelstvo, pokud ke stejnému (cls,parc,kat,price) existuje,
    # jinak rada (viz metodika v odpovědi z 23. 8. 2026 — dřívější schvalovací krok se nepočítá dvakrát)
    from collections import defaultdict
    groups = defaultdict(list)
    for r in rows:
        groups[(r['cls'], r['parc'], r['kat'], r['price_disp'])].append(r)
    canonical_ids = set()
    for grp in groups.values():
        zm = [r for r in grp if r['typ'] == 'Zastupitelstvo']
        canonical_ids.add(id(zm[0] if zm else grp[0]))
    for r in rows:
        r['canonical'] = id(r) in canonical_ids
    return rows


def lookup_ruian(kat, parcelnum):
    if (kat, parcelnum) in MANUAL_OVERRIDES:
        return MANUAL_OVERRIDES[(kat, parcelnum)], None
    kod = KAT_CODES.get(kat)
    if not kod:
        return None, f'neznámý katastr kód pro "{kat}" — doplnit do KAT_CODES'
    km, pod = (parcelnum.split('/', 1) + [''])[:2] if '/' in parcelnum else (parcelnum, '')
    url = (f'https://vdp.cuzk.gov.cz/vdp/ruian/parcely?kodKuDr={kod}&druhCislovaniPa='
           f'&kmCisPa={km}&podCisPa={pod}&sort=PARCELA1&search=')
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode('utf-8', errors='ignore')
    except Exception as e:  # noqa: BLE001
        return None, str(e)
    ids = list(dict.fromkeys(re.findall(r'/vdp/ruian/parcely/(\d+)', body)))
    if len(ids) == 1:
        return ids[0], None
    if not ids:
        return None, 'nenalezeno (zkontrolovat kmenové číslo/poddělení/katastr ručně)'
    return None, f'nejednoznačné, vyžaduje ruční MANUAL_OVERRIDES: {ids}'


def load_cache():
    if CACHE_JSON.exists():
        return json.loads(CACHE_JSON.read_text(encoding='utf-8')).get('parcely', {})
    return {}


def save_cache(cache):
    CACHE_JSON.write_text(json.dumps({
        '_comment': ('Katastr-přesná mapa "katastr|číslo parcely" -> RUIAN ID. Zdroj pravdy '
                     'pro odkazy na parcely na celém webu (tabulky Pozemky i obecné prolinkování '
                     'v Jednání, viz parcely-odkazy.json). Generuje a doplňuje '
                     'jednani/scripts/update-pozemky.py.'),
        'count': len(cache),
        'parcely': dict(sorted(cache.items())),
    }, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')


def update_cache(rows, cache):
    needed = set()
    for r in rows:
        if r['kat'] not in KAT_CODES or not r['parc']:
            continue
        for token in r['parc'].split(', '):
            token = token.strip()
            if not token or token.startswith('LV') or 'dalších' in token:
                continue
            needed.add((r['kat'], token))

    new_count = 0
    errors = []
    for kat, num in sorted(needed):
        key = f'{kat}|{num}'
        if key in cache:
            continue
        rid, err = lookup_ruian(kat, num)
        if rid:
            cache[key] = rid
            new_count += 1
        else:
            errors.append((key, err))
        time.sleep(0.15)

    save_cache(cache)

    if errors:
        print(f'POZOR: {len(errors)} parcel se nepodařilo dohledat automaticky:', file=sys.stderr)
        for key, err in errors:
            print(f'  {key}: {err}', file=sys.stderr)
        print('Doplň je ručně do MANUAL_OVERRIDES v tomto skriptu a spusť znovu.', file=sys.stderr)

    return cache


# ===== Obecné prolinkování zmínek "parc. NNNN" v celém Jednání (nahrazuje katastr-odkazy.json) =====
# Na rozdíl od tabulek Pozemky (kde katastr u řádku už známe) tady skenujeme VŠechna usnesení
# i body programu v celém pecky-jednani.json — číslo parcely bez katastru je nejednoznačné,
# takže pro každé číslo sesbíráme katastr ze VŠECH míst, kde se objeví, a:
#  - pokud se katastr napříč všemi výskyty shoduje (nebo ho neznáme jen u části z nich) → dohledáme
#    a přidáme do finální ploché mapy (GENERAL_LINKS_JSON), kterou používá jLinkParcely() v content/jednani.html,
#  - pokud se katastr u různých výskytů LIŠÍ (kolize, viz případ parcely "254" — Pečky vs.
#    Velké Chvalovice) → číslo se do mapy vůbec nepřidá (raději nepodlinkovat, než odkázat špatně).
GENERAL_LINKS_JSON = ROOT / 'jednani' / 'parcely-odkazy.json'
GENERAL_PARC_RE = re.compile(r'parc\.?\s*(\d{1,5}(?:/\d{1,3})?)', re.I)


def scan_general_mentions(data):
    """Vrátí dict {parcelové číslo: set(katastr nebo '' pokud nezjištěno)} ze všech
    usnesení (item+text) a bodů programu (t) v celém datasetu."""
    mentions = {}
    for m in data['meetings']:
        for r in m['resolutions']:
            item = r.get('item', '') or ''
            text = re.sub(r'\s+', ' ', r.get('text', '') or '')
            nums = set(GENERAL_PARC_RE.findall(item)) | set(GENERAL_PARC_RE.findall(text))
            if not nums:
                continue
            kat = detect_katastr(item, text)
            for num in nums:
                mentions.setdefault(num, set()).add(kat)
        for a in m['agenda']:
            t = a.get('t', '') or ''
            nums = set(GENERAL_PARC_RE.findall(t))
            if not nums:
                continue
            kat = detect_katastr(t)
            for num in nums:
                mentions.setdefault(num, set()).add(kat)
    return mentions


def build_general_links(mentions, cache):
    """Pro každé číslo s jednoznačným (nekolidujícím) katastrem dohledá/použije RUIAN ID
    a uloží plochou mapu číslo->URL do GENERAL_LINKS_JSON. Číslo bez jednoznačného katastru
    (buď nezjištěn nikde, nebo kolize více katastrů) se do mapy nepřidá."""
    links = {}
    skipped_unknown = []
    skipped_collision = []
    new_count = 0

    for num, kats in sorted(mentions.items()):
        known = {k for k in kats if k}
        if len(known) == 0:
            skipped_unknown.append(num)
            continue
        if len(known) > 1:
            skipped_collision.append((num, sorted(known)))
            continue
        kat = next(iter(known))
        if kat not in KAT_CODES:
            skipped_unknown.append(num)
            continue
        key = f'{kat}|{num}'
        rid = cache.get(key)
        if not rid:
            rid, err = lookup_ruian(kat, num)
            if rid:
                cache[key] = rid
                new_count += 1
            else:
                skipped_unknown.append(num)
                time.sleep(0.15)
                continue
            time.sleep(0.15)
        links[num] = f'https://vdp.cuzk.gov.cz/vdp/ruian/parcely/{rid}'

    GENERAL_LINKS_JSON.write_text(json.dumps({
        '_comment': ('Plochá mapa "číslo parcely" -> URL detailu na vdp.cuzk.gov.cz pro obecné '
                     'prolinkování zmínek "parc. NNNN" v textu usnesení a bodů programu kdekoli '
                     'na webu (jLinkParcely() v content/jednani.html, fetch v loadJednani()). Nahrazuje '
                     'dřívější katastr-odkazy.json (smazaný 23. 8. 2026 — obsahoval prokázanou '
                     'chybu u kolidujících čísel, viz AUTOMATION.md). Číslo, u kterého se '
                     'katastr nepodařilo jednoznačně určit nebo koliduje mezi více katastry, '
                     'se sem záměrně nepřidává — raději nepodlinkovat, než odkázat na špatnou '
                     'parcelu. Generuje jednani/scripts/update-pozemky.py.'),
        'count': len(links),
        'skipped_unknown_katastr': len(skipped_unknown),
        'skipped_collision': [{'cislo': n, 'katastry': k} for n, k in skipped_collision],
        'parcely': dict(sorted(links.items())),
    }, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')

    print(f'Obecné odkazy (Jednání): {len(links)} čísel, {new_count} nově dohledáno, '
          f'{len(skipped_unknown)} bez zjištěného katastru, {len(skipped_collision)} kolizí.')
    if skipped_collision:
        print('Kolize (víc katastrů pro stejné číslo — nepodlinkováno):', file=sys.stderr)
        for n, k in skipped_collision:
            print(f'  {n}: {k}', file=sys.stderr)

    if new_count:
        save_cache(cache)
    return cache


def esc(s):
    return html.escape(s or '', quote=True)


def fmt_date(d):
    y, m, dd = d.split('-')
    return f'{dd}. {int(m)}. {y}'


def parcela_cell(r, cache):
    if not r['parc']:
        return '–'
    parts = []
    for token in r['parc'].split(', '):
        token = token.strip()
        if not token:
            continue
        key = f'{r["kat"]}|{token}'
        rid = cache.get(key)
        if rid:
            url = f'https://vdp.cuzk.gov.cz/vdp/ruian/parcely/{rid}'
            parts.append(f'<a href="{url}" target="_blank" rel="noopener">{esc(token)}</a>')
        else:
            parts.append(esc(token))
    return ', '.join(parts)


def meeting_genitive(typ):
    return 'rady' if typ == 'Rada' else 'zastupitelstva'


def row_html(r, cache):
    kat = esc(r['kat'] or 'neuvedeno')
    price = esc(r['price_disp'] or '–')
    item = esc(r['item'])
    typ_tag = 'ZM' if r['typ'] == 'Zastupitelstvo' else 'RM'
    note = '' if r['canonical'] else f' <span style="color:var(--ink-soft); font-size:12px;">({typ_tag} — dřívější krok schvalování)</span>'
    n_esc = esc(r['n'])
    item_link = f'<a href="{esc(r["url"])}" target="_blank" rel="noopener">{item}</a>' if r['url'] else item
    parc_html = parcela_cell(r, cache)
    meeting_link = ''
    if r.get('meeting_uuid') and r.get('meeting_number'):
        meeting_label = f'Jednání {meeting_genitive(r["typ"])} č. {r["meeting_number"]}'
        is_future = r['date'] > TODAY
        prefix = 'bude se řešit na: ' if is_future else 'řešilo se na: '
        chip = ' <span class="tag" style="margin-left:4px;">PLÁNOVÁNO</span>' if is_future else ''
        meeting_link = (f'<br><span class="pozemek-jednani-meta">{prefix}'
                         f'<a href="#" class="pozemek-jednani-link" data-jednani-uuid="{esc(r["meeting_uuid"])}">{esc(meeting_label)}</a>{chip}</span>')
    return (f'        <tr><td>{fmt_date(r["date"])}</td><td>{parc_html}</td><td>{kat}</td>'
            f'<td>{item_link}{note} <span class="tag" style="margin-left:4px;">{n_esc}</span>{meeting_link}</td>'
            f'<td style="white-space:nowrap;">{price}</td></tr>')


def build_table(rows, cls, cache):
    subset = [r for r in rows if r['cls'] == cls]
    lines = ['    <table class="register">',
             '      <thead><tr><th>Datum</th><th>Parcela č.</th><th>Katastr obce</th>'
             '<th>Název bodu jednání</th><th>Cena</th></tr></thead>',
             '      <tbody>']
    lines += [row_html(r, cache) for r in subset]
    lines += ['      </tbody>', '    </table>']
    total = sum(r['price_num'] for r in subset if r['canonical'] and r['price_num'])
    n_known = sum(1 for r in subset if r['canonical'] and r['price_num'])
    n_tot = sum(1 for r in subset if r['canonical'])
    total_fmt = f'{total:,}'.replace(',', ' ')
    lines.append(f'    <p class="program-note" style="margin-top:10px;"><strong>Součet '
                 f'({n_known} z {n_tot} unikátních obchodů se známou celkovou cenou v Kč): '
                 f'{total_fmt} Kč</strong></p>')
    return '\n'.join(lines)


def splice_into_index(nakup_html, prodej_html):
    content = POZEMKY_CONTENT.read_text(encoding='utf-8')

    pat_nakup = re.compile(
        r'(<div class="subpanel active" id="subpanel-pozemky-nakup">\n)(.*?)'
        r'(\n    </div>\n\n    <div class="subpanel" id="subpanel-pozemky-prodej">)', re.S)
    m = pat_nakup.search(content)
    if not m:
        raise SystemExit('subpanel-pozemky-nakup nenalezen v content/pozemky.html — zkontroluj strukturu panelu Pozemky')
    content = content[:m.start()] + m.group(1) + nakup_html + m.group(3) + content[m.end():]

    pat_prodej = re.compile(
        r'(<div class="subpanel" id="subpanel-pozemky-prodej">\n)(.*?)'
        r'(\n    </div>\n\n    <div class="callout" style="margin-top:26px;">)', re.S)
    m2 = pat_prodej.search(content)
    if not m2:
        raise SystemExit('subpanel-pozemky-prodej nenalezen v content/pozemky.html — zkontroluj strukturu panelu Pozemky')
    content = content[:m2.start()] + m2.group(1) + prodej_html + m2.group(3) + content[m2.end():]

    POZEMKY_CONTENT.write_text(content, encoding='utf-8')


def check_tag_balance():
    content = POZEMKY_CONTENT.read_text(encoding='utf-8')
    clean = re.sub(r'<script\b[^>]*>.*?</script>', '', content, flags=re.S)
    clean = re.sub(r'<style\b[^>]*>.*?</style>', '', clean, flags=re.S)
    clean = re.sub(r'<!--.*?-->', '', clean, flags=re.S)
    void_tags = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
                 'link', 'meta', 'param', 'source', 'track', 'wbr'}
    stack, errors = [], []
    for m in re.finditer(r'<(/?)([a-zA-Z0-9]+)([^>]*)>', clean):
        closing, name, attrs = m.groups()
        name = name.lower()
        if name in void_tags or attrs.strip().endswith('/'):
            continue
        if not closing:
            stack.append(name)
        elif stack and stack[-1] == name:
            stack.pop()
        else:
            errors.append(f'mismatch at </{name}>')
    if errors or stack:
        raise SystemExit(f'HTML tag balance selhala po zásahu — errors={errors[:5]} zbylo otevřených={stack[:5]}')
    print('HTML tag balance OK.')


def main():
    data = json.loads(JEDNANI_JSON.read_text(encoding='utf-8'))
    cache = load_cache()

    rows = extract_rows(data)
    print(f'Nalezeno {len(rows)} usnesení o prodeji/nákupu pozemku '
          f'({sum(1 for r in rows if r["cls"]=="nákup")} nákup, '
          f'{sum(1 for r in rows if r["cls"]=="prodej")} prodej).')
    cache = update_cache(rows, cache)

    nakup_html = build_table(rows, 'nákup', cache)
    prodej_html = build_table(rows, 'prodej', cache)
    splice_into_index(nakup_html, prodej_html)
    check_tag_balance()
    print('Hotovo — content/pozemky.html aktualizován. Teď spustit `python3 scripts/build.py`, ať se to promítne i do pozemky/index.html.')

    mentions = scan_general_mentions(data)
    build_general_links(mentions, cache)


if __name__ == '__main__':
    main()
