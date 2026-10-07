#!/usr/bin/env python3
"""
Vygeneruje znalostní index pro PečkyBota: peckybot/index.json.

Index čte Cloudflare Worker (peckybot/worker/), který z něj vybírá úryvky
k dotazu návštěvníka. Zdroje jsou jen data, která už na webu jsou:

  - jednání zastupitelstva a rady (jednani/pecky-jednani.json) — bod programu
    + důvodová zpráva + usnesení
  - lidé s životopisem nebo kontaktem (lide/people.json)
  - statické texty sekcí (content/<sekce>.html)

Formát (verze 1) — rozdělený na malý rejstřík a dávky s texty, aby Worker při
studeném startu parsoval jen rejstřík (limit CPU na volání) a texty úryvků
stahoval jen pro nejlepší zásahy:
  peckybot/index.json:
    {"v": 1, "shard": 100,
     "chunks": [{"u": url, "t": titulek}, ...],
     "post":   {token: [idx, tf, idx, tf, ...], ...}}
  peckybot/chunks/<k>.json: pole textů úryvků s indexy k*100 … k*100+99

Pořadí úryvků je chronologické (nejstarší první), takže nová jednání přibývají
na konec a mění se jen poslední dávky. Soubory se přepíšou jen při změně obsahu.

Tokenizace MUSÍ být shodná s peckybot/worker/src/search.ts (funkce tokenize):
malá písmena, bez diakritiky, slova od 3 znaků, zkrácená na prvních 6 znaků
(hrubý stemmer pro češtinu), bez stopslov.

Spouští ho scripts/build.py; samostatně: python3 scripts/build_peckybot_index.py
"""
import hashlib
import html
import json
import math
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'peckybot' / 'index.json'
SHARD_DIR = ROOT / 'peckybot' / 'chunks'

STEM_LEN = 6
MAX_CHUNK = 700          # znaků textu jednoho úryvku
SHARD = 100              # úryvků v jedné dávce peckybot/chunks/<k>.json
MIN_CHUNK = 110          # kratší úryvky (jen název bodu) se neindexují
MAX_DF_RATIO = 0.25      # tokeny ve víc než čtvrtině úryvků se neindexují
STOPWORDS = {
    'aby', 'ale', 'ani', 'jak', 'jako', 'jsou', 'jeho', 'jejich', 'kde', 'kdy',
    'kteri', 'ktery', 'ktera', 'ktere', 'nebo', 'pri', 'pro', 'proc', 'tak',
    'ten', 'the', 'toho', 'tom', 'tato', 'tyto', 'byl', 'byla', 'bylo', 'byt',
    'bude', 'jsem', 'jste', 'jsme', 'mesto', 'mesta', 'mestem', 'pecky', 'pecek',
    'peckach', 'cislo', 'cisl', 'dle', 'ode', 'ani', 'napr', 'tzn', 'atd',
}


from peckybot_sources import chunks_extra  # noqa: E402


def tokenize(text):
    s = unicodedata.normalize('NFD', text.lower())
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    out = []
    for w in re.findall(r'[a-z0-9]+', s):
        if len(w) < 3 or w in STOPWORDS:
            continue
        out.append(w[:STEM_LEN])
    return out


def clip(text, n):
    text = re.sub(r'\s+', ' ', text or '').strip()
    if len(text) <= n:
        return text
    return text[:n].rsplit(' ', 1)[0] + '…'


def meeting_ref(m):
    """('ZM 6/2026', '/jednani/#zastupitelstvo-2026-09-16')"""
    zm = m['type'] == 'Zastupitelstvo'
    short = ('ZM ' if zm else 'RM ') + f"{m['number']}/{m['year']}"
    anchor = ('zastupitelstvo-' if zm else 'rada-') + m['date']
    return short, f'/jednani/#{anchor}'


def cz_date(iso):
    y, m, d = iso.split('-')
    return f'{int(d)}. {int(m)}. {y}'


MESIC_NOM = ['', 'leden', 'únor', 'březen', 'duben', 'květen', 'červen', 'červenec', 'srpen',
             'září', 'říjen', 'listopad', 'prosinec']
MESIC_GEN = ['', 'ledna', 'února', 'března', 'dubna', 'května', 'června', 'července', 'srpna',
             'září', 'října', 'listopadu', 'prosince']


def meeting_context(m, short):
    """Úvod úryvku: druh jednání slovy + datum ve více zápisech (dotazy typu
    „zasedání zastupitelstva 26. srpna“ musí najít slova přímo v textu)."""
    y, mo, d = m['date'].split('-')
    mo_i, d_i = int(mo), int(d)
    kdy = f"{d_i}. {mo_i}. {y}"
    if m['type'] == 'Zastupitelstvo':
        druh = f"Zasedání zastupitelstva města, {short}"
    else:
        druh = f"Schůze rady města, {short}"
    return (f"{druh}, konané {kdy} ({d_i}. {MESIC_GEN[mo_i]} {y}, {MESIC_NOM[mo_i]} {y})")


def chunks_jednani():
    data = json.loads((ROOT / 'jednani/pecky-jednani.json').read_text(encoding='utf-8'))
    out = []
    for m in sorted(data['meetings'], key=lambda x: x['date']):
        short, url = meeting_ref(m)
        head = meeting_context(m, short)
        used = set()
        # přehled jednání: kdy, kde, co je na programu
        ag = m.get('agenda', [])
        pr = [head + '.']
        if m.get('venue'):
            pr.append(f"Místo: {clip(m['venue'], 70)}.")
        if m.get('time'):
            pr.append(f"Začátek: {m['time']}.")
        if ag:
            pr.append(f"Program ({len(ag)} bodů): " + clip('; '.join(f"{a['n']}. {a['t']}" for a in ag), 380))
        out.append({'u': url, 't': f'{short} — přehled jednání', 'x': clip(' '.join(pr), 560)})
        # usnesení podle názvu bodu
        by_item = {}
        for r in m.get('resolutions', []):
            by_item.setdefault(r['item'], []).append(r)
        for a in ag:
            parts = [f"{head}, bod {a['n']}: {a['t']}."]
            if a.get('predkladatel'):
                parts.append(f"Předkládá: {a['predkladatel']}.")
            if a.get('duvodova_zprava'):
                parts.append('Důvodová zpráva: ' + clip(a['duvodova_zprava'], 300))
            for r in by_item.get(a['t'], []):
                used.add(a['t'])
                hlasy = ''
                if r.get('pro') is not None:
                    hlasy = f" (pro {r['pro']}, proti {r.get('proti', 0)}, zdrželo se {r.get('zdrzel', 0)})"
                parts.append(f"Usnesení {r['n']}: {clip(r['text'], 360)}{hlasy}")
            text = clip(' '.join(parts), MAX_CHUNK + 90)
            if len(text) < MIN_CHUNK + 90:
                continue
            out.append({'u': url, 't': f'{short} — {a["t"]}', 'x': text})
        for item, rs in by_item.items():
            if item in used:
                continue
            parts = [f"{head}, bod: {item}."]
            for r in rs:
                parts.append(f"Usnesení {r['n']}: {clip(r['text'], 360)}")
            out.append({'u': url, 't': f'{short} — {item}', 'x': clip(' '.join(parts), MAX_CHUNK + 90)})
    return out


ROLE_TAGY = {
    'vedeni-mesta': 'vedení města', 'zastupitel': 'člen zastupitelstva', 'rada': 'člen rady města',
    'komise': 'člen komise', 'urednik': 'zaměstnanec městského úřadu', 'vedeni-uradu': 'vedení úřadu',
    'skolstvi': 'školství', 'kultura': 'kultura', 'sport': 'sport', 'spolky': 'spolky',
    'socialni-sluzby': 'sociální služby', 'zdravotnictvi': 'zdravotnictví',
}


USTREDNA = re.sub(r'\D', '', '+420 321 785 051')
# role_type -> slova, která lidé hledají (doplňují text role z affiliations.json)
ROLE_SLOVA = {
    'starosta': 'starosta města, starostka',
    'mistostarosta': 'místostarosta, místostarostka',
    'rada': 'radní, člen rady města',
    'zastupitel': 'zastupitel, zastupitelka, člen zastupitelstva města',
    'vedeni-organizace': 'vedení organizace, ředitel, ředitelka',
    'vedeni-urad': 'vedení městského úřadu, tajemník, vedoucí odboru',
}
FUNKCNI = {'starosta', 'mistostarosta', 'rada', 'zastupitel', 'komise', 'vedeni-organizace',
           'vedeni-urad', 'clen'}


def clean_phone(phone):
    """Ústředna úřadu není osobní kontakt (lide/SPEC.md §3.6b)."""
    nums = [x.strip() for x in phone.split('·')]
    return ' · '.join(x for x in nums if x and re.sub(r'\D', '', x) != USTREDNA)


def chunks_lide():
    data = json.loads((ROOT / 'lide/people.json').read_text(encoding='utf-8'))
    orgs = {o['id']: o for o in json.loads(
        (ROOT / 'lide/organizations.json').read_text(encoding='utf-8'))['organizations']}
    aff = {}
    for a in json.loads((ROOT / 'lide/affiliations.json').read_text(encoding='utf-8'))['affiliations']:
        aff.setdefault(a['person_id'], []).append(a)
    out = []
    for p in data['people']:
        bio = (p.get('bio') or '').strip()
        email = (p.get('email') or '').strip()
        phone = clean_phone((p.get('phone') or '').strip())
        mine = aff.get(p['id'], [])
        funkce = [a for a in mine if a['current'] and a['role_type'] in FUNKCNI]
        # každý člověk má aspoň jméno (hledání podle jména); kontakty a funkce i bez životopisu
        jmeno = ' '.join(x for x in (p.get('title_before'), p.get('first_name'), p.get('last_name'),
                                     p.get('title_after')) if x).strip()
        parts = [f'{jmeno}.']
        stare = list(p.get('former_last_names') or [])
        if stare:
            parts.append(f"Dříve příjmením {', '.join(stare)}.")
        if bio:
            parts.append(clip(bio, 600))
        # funkce: text role + hledaná slova + název organizace
        fl, slova, videno = [], [], set()
        for a in funkce:
            org = orgs.get(a['organization_id'], {}).get('name', '')
            key = (a['role'], org)
            if key in videno:
                continue
            videno.add(key)
            fl.append(f"{a['role']} ({org})" if org else a['role'])
            slova.append(ROLE_SLOVA.get(a['role_type'], ''))
        if fl:
            parts.append('Funkce: ' + '; '.join(fl[:6]) + '.')
            sl = ', '.join(sorted({w for x in slova for w in x.split(', ') if w}))
            if sl:
                parts.append(f'({sl}).')
        else:
            role = [ROLE_TAGY[t] for t in p.get('tags', []) if t in ROLE_TAGY]
            if role:
                parts.append(f"Působení: {', '.join(role)}.")
        strany = []
        for a in mine:
            o = orgs.get(a['organization_id'], {})
            if o.get('type') == 'politicke' and o['name'] not in strany:
                strany.append(o['name'])
        if strany:
            parts.append('Politické uskupení: ' + '; '.join(strany) + '.')
        occ = sorted(p.get('occupations') or [], key=lambda o: o.get('year', 0), reverse=True)
        if occ and not bio:
            parts.append(f"Zaměstnání: {occ[0]['value']}.")
        if len(parts) == 1 + bool(stare) and not mine:
            parts.append('Osoba evidovaná v sekci Lidé.')
        if email or phone:
            parts.append('Kontakt:')
        if email:
            parts.append(f'E-mail: {email}.')
        if phone:
            parts.append(f'Telefon: {phone}.')
        t = f'Lidé — {jmeno}'
        out.append({'u': '/lide/', 't': t, 'x': ' '.join(parts)})
    return out


def _lide_data():
    people = {p['id']: p for p in json.loads((ROOT / 'lide/people.json').read_text(encoding='utf-8'))['people']}
    orgs = {o['id']: o for o in json.loads(
        (ROOT / 'lide/organizations.json').read_text(encoding='utf-8'))['organizations']}
    aff = json.loads((ROOT / 'lide/affiliations.json').read_text(encoding='utf-8'))['affiliations']
    return people, orgs, aff


def _full_name(p):
    return ' '.join(x for x in (p.get('title_before'), p.get('first_name'), p.get('last_name'),
                                p.get('title_after')) if x).strip()


def _d_from(v):
    """'2014' -> '2014-01-01' (začátek), plná data beze změny."""
    return v if v and len(v) > 4 else (f'{v}-01-01' if v else '0000-00-00')


def _d_to(v):
    return v if v is None or len(v) > 4 else f'{v}-12-31'


def _party(pid, at, orgs, aff):
    """Politické uskupení, za které osoba kandidovala naposledy před datem `at`."""
    best = None
    for a in aff:
        o = orgs.get(a['organization_id'], {})
        if a['person_id'] == pid and o.get('type') == 'politicke' and _d_from(a['from']) <= at:
            if best is None or _d_from(a['from']) > best[0]:
                best = (_d_from(a['from']), o['name'])
    return best[1] if best else ''


def _entry(pid, role, at, people, orgs, aff):
    party = _party(pid, at, orgs, aff)
    return f"{_full_name(people[pid])} ({role}{', ' + party if party else ''})"


def chunks_slozeni():
    """Složení rady, zastupitelstva, výborů a komisí a přehled starostů — z lide/*.json."""
    people, orgs, aff = _lide_data()
    mp = [a for a in aff if a['organization_id'] == 'mesto-pecky']
    out = []
    # volební období podle začátku mandátu rady
    starts = sorted({a['from'] for a in mp if a['role_type'] == 'rada'})
    terms = []
    for i, st in enumerate(starts):
        terms.append((_d_from(st), starts[i + 1] if i + 1 < len(starts) else None))
    for st, end in reversed(terms):
        cur = end is None
        at = st
        def covers(a, st=st, end=end):
            return _d_from(a['from']) <= st and (_d_to(a['to']) is None or _d_to(a['to']) > st)
        roles = [a for a in mp if a['role_type'] in ('starosta', 'mistostarosta', 'rada') and covers(a)]
        order = {'starosta': 0, 'mistostarosta': 1, 'rada': 2}
        roles.sort(key=lambda a: (order[a['role_type']], a['role']))
        seen, names = set(), []
        for a in roles:
            if a['person_id'] in seen:
                continue
            seen.add(a['person_id'])
            role = a['role'] if a['role_type'] != 'rada' else 'radní'
            names.append(_entry(a['person_id'], role, at, people, orgs, aff))
        if not names:
            continue
        od = cz_date(st) if len(st) > 4 else st
        od = od.replace('1. 1. ', '')
        if cur:
            x = (f"Složení rady města (současná rada, od {od}): počet členů: {len(names)}. Kdo je v radě města, "
                 f"kdo je starosta, místostarosta a radní: " + '; '.join(names) + '.')
            t = 'Složení rady města — současné'
        else:
            do = cz_date(end) if len(end) > 4 else end
            x = (f"Složení rady města v období {od} – {do} (v datech uvedeno {len(names)} osob): "
                 + '; '.join(names) + '.')
            t = f'Složení rady města — {od[-4:] if len(st) > 4 else od}–{do[-4:]}'
        out.append({'u': '/lide/', 't': t, 'x': clip(x, 900)})
        # zastupitelstvo: jen aktuální období (starší období nejsou v datech úplná)
        if cur:
            zs = [a for a in mp if a['role_type'] == 'zastupitel' and a['current']]
            zn = []
            for a in sorted(zs, key=lambda a: people[a['person_id']]['last_name']):
                zn.append(_entry(a['person_id'], 'zastupitel', at, people, orgs, aff))
            by_party = {}
            for a in zs:
                by_party[_party(a['person_id'], at, orgs, aff) or 'bez uvedení'] = \
                    by_party.get(_party(a['person_id'], at, orgs, aff) or 'bez uvedení', 0) + 1
            sp = ', '.join(f'{k} {v}' for k, v in sorted(by_party.items(), key=lambda kv: -kv[1]))
            x1 = (f"Složení zastupitelstva města (současné období od {od}): počet zastupitelů: {len(zs)}. "
                  f"Kolik je zastupitelů a kdo v zastupitelstvu sedí. Podle uskupení: {sp}. "
                  + '; '.join(zn) + '.')
            out.append({'u': '/lide/', 't': 'Složení zastupitelstva města — současné', 'x': clip(x1, 1400)})
    # starostové a místostarostové v čase
    for rt, titul, slovo in (('starosta', 'Starostové', 'starosta'), ('mistostarosta', 'Místostarostové', 'místostarosta')):
        rows = sorted((a for a in mp if a['role_type'] == rt), key=lambda a: _d_from(a['from']))
        if not rows:
            continue
        parts = []
        for a in rows:
            f = cz_date(a['from']) if len(a['from']) > 4 else a['from']
            to = 'dosud' if a['to'] is None else (cz_date(a['to']) if len(a['to']) > 4 else a['to'])
            parts.append(f"{f} – {to}: {_full_name(people[a['person_id']])} ({a['role']})")
        out.append({'u': '/lide/', 't': 'Starostové a místostarostové' if rt == 'starosta' else 'Místostarostové Peček v čase',
                    'x': clip(f"{titul} Peček v čase (od roku {rows[0]['from'][:4]}), kdo byl {slovo}: "
                              + '; '.join(parts) + '.', 900)})
    # výbory a komise (aktuální členové)
    funkce = re.compile(r'^(člen|členka|předseda|předsedkyně|místopředseda|místopředsedkyně)\s+', re.I)
    groups = {}
    for a in aff:
        if a['role_type'] != 'komise' or not a['current']:
            continue
        m = funkce.match(a['role'])
        body = a['role'][m.end():] if m else a['role']
        fn = m.group(1).lower() if m else 'člen'
        key = (a['organization_id'], body[0].lower() + body[1:])
        groups.setdefault(key, []).append((fn, a['person_id']))
    for (oid, body), mem in sorted(groups.items()):
        if len(mem) < 2:
            continue
        mem.sort(key=lambda m: (m[0] == 'člen' or m[0] == 'členka', people[m[1]]['last_name']))
        org = orgs.get(oid, {}).get('name', '')
        zast = ' zastupitelstva města' if 'výbor' in body else ''
        kde = f" ({org})" if oid != 'mesto-pecky' and org else ''
        nm = '; '.join(f"{_full_name(people[pid])} ({fn})" for fn, pid in mem)
        out.append({'u': '/lide/', 't': f'Složení — {body}{kde}',
                    'x': clip(f"Složení {body}{zast}{kde}: počet členů: {len(mem)}, kdo je členem, předseda. " + nm + '.', 800)})
    return out


# Číselné údaje ze statických stránek: (sekce, štítek, otázkové fráze, regulární výraz řádku, jen věta?)
# Text úryvku se doslova přebírá ze stránky; když se řádek nenajde, úryvek se nevytvoří.
FAKTA = [
    ('telocvicna', 'cena dostavby školy a tělocvičny', 'Kolik stojí dostavba školy a tělocvičny? Cena, částka, rozpočet stavby.',
     r'^Stavba nové tělocvičny a učeben .* rozpočtem [\d,]+ mil\. Kč', 1),
    ('telocvicna', 'cena díla po dodatku', 'Kolik stojí tělocvična? Cena díla, aktuální cena, částka.',
     r'^\d+\. \d+\. \d{4} \| [\d,]+ mil\. Kč bez DPH \([\d,]+ mil\. Kč s DPH\) \| Cena díla', 1),
    ('telocvicna', 'úvěr na dostavbu', 'Úvěr na stavbu tělocvičny, výše úvěru, půjčka, dluh města.',
     r'^\d+\. \d+\. 2026 \| (Zastupitelstvo|Rada) \(.*úvěr', 3),
    ('pokladna', 'dluh, úvěr a přebytek města', 'Má město dluhy nebo úvěr? Dluh, úvěr, hospodaření, přebytek.',
     r'^Stručně: ', 1),
    ('pokladna', 'rozpočet a výdaje města', 'Kolik město utrácí? Rozpočet, výdaje, částka, investice.',
     r'^(Na co město utrácí \(rok \d+, celkem|z toho \d+ % \([\d,]+ mil\. Kč\) běžný provoz)', 2),
    ('pokladna', 'zůstatek na účtech', 'Kolik má město peněz na účtech? Zůstatek, částka, fondy.',
     r'^Souhrnný zůstatek na všech účtech', 1),
]


def chunks_fakta():
    out = []
    cache = {}
    for slug, stitek, lead, pat, kolik in FAKTA:
        url, nazev = STATICKE[slug]
        if slug not in cache:
            path = ROOT / 'content' / f'{slug}.html'
            cache[slug] = [ln.lstrip(HEAD_MARK) for ln in html_to_lines(path.read_text(encoding='utf-8'))] \
                if path.exists() else []
        hits = []
        for ln in cache[slug]:
            if re.search(pat, ln):
                if kolik == 0:   # jen věta s údajem
                    m = re.search(r'[^.]*?' + pat + r'[^.]*\.', ln)
                    ln = m.group(0).strip() if m else ln
                hits.append(ln)
        if not hits:
            continue
        body = ' '.join(clip(h, 250) for h in hits[:max(kolik, 1)])
        out.append({'u': url, 't': f'Web — {nazev} — shrnutí: {stitek}',
                    'x': clip(f'{nazev} — shrnutí: {stitek}. {lead} {body}', 760)})
    return out


# statické sekce -> (URL, název); dynamické sekce (jednání, noviny, kalendář)
# mají v content/*.html jen kostru, data jsou v JSON
STATICKE = {
    'plan': ('/plan/', 'Strategický plán'),
    'telocvicna': ('/telocvicna/', 'Tělocvična'),
    'pozemky': ('/pozemky/', 'Pozemky'),
    'prostory': ('/prostory/', 'Prostory'),
    'pokladna': ('/pokladna/', 'Pokladna'),
    'smlouvy': ('/smlouvy/', 'Smlouvy'),
    'zakazky': ('/zakazky/', 'Zakázky'),
    'volby': ('/volby/', 'Volby'),
    'volby2018': ('/volby/2018/', 'Volby 2018'),
    'volby2022': ('/volby/2022/', 'Volby 2022'),
    'volby2026': ('/volby/2026/', 'Volby 2026'),
    'owebu': ('/o-webu/', 'O webu'),
}


HEAD_MARK = '\x01'


def html_to_lines(src):
    """Text stránky po řádcích; nadpisy (h2–h4, summary bez nadpisu uvnitř) mají prefix HEAD_MARK."""
    src = re.sub(r'<(script|style)\b.*?</\1>', ' ', src, flags=re.S | re.I)
    src = re.sub(r'\{\{[^}]*\}\}', ' ', src)

    def summary(m):
        inner = m.group(1)
        return m.group(0) if re.search(r'<h[1-6]', inner, re.I) else f'<h4>{inner}</h4>'
    src = re.sub(r'<summary\b[^>]*>(.*?)</summary>', summary, src, flags=re.S | re.I)
    src = re.sub(r'<h([2-4])\b[^>]*>(.*?)</h\1>', lambda m: '\n' + HEAD_MARK + re.sub(r'<[^>]+>', '', m.group(2)) + '\n',
                 src, flags=re.S | re.I)
    src = re.sub(r'<br\s*/?>|</(p|li|tr|div|section)>', '\n', src, flags=re.I)
    src = re.sub(r'</t[dh]>', ' | ', src, flags=re.I)
    src = re.sub(r'<[^>]+>', '', src)
    src = html.unescape(src).replace('\xa0', ' ')
    out = []
    for ln in src.splitlines():
        head = ln.startswith(HEAD_MARK)
        ln = re.sub(r'\s+', ' ', ln.lstrip(HEAD_MARK)).strip(' |')
        if ln:
            out.append((HEAD_MARK if head else '') + ln)
    return out


def split_long(ln, n):
    """Dlouhý řádek rozdělí na věty, aby žádný úryvek nezačínal uprostřed věty."""
    if len(ln) <= n:
        return [ln]
    res, cur = [], ''
    for sent in re.split(r'(?<=[.!?])\s+', ln):
        if cur and len(cur) + len(sent) + 1 > n:
            res.append(cur)
            cur = ''
        cur = (cur + ' ' + sent).strip()
    if cur:
        res.append(cur)
    return res


def chunks_stranky():
    out = []
    for slug, (url, nazev) in STATICKE.items():
        path = ROOT / 'content' / f'{slug}.html'
        if not path.exists():
            continue
        h2 = ''          # hlavní nadpis stránky
        sekce = ''       # aktuální podnadpis
        buf = []

        def flush():
            body = '\n'.join(buf).strip()
            buf.clear()
            if len(body) < 40:
                return
            kde = nazev + (f' — {sekce}' if sekce and sekce != nazev else '')
            t = f'Web — {kde}'
            out.append({'u': url, 't': t, 'x': f'{kde}: {body}'})

        size = 0
        for ln in html_to_lines(path.read_text(encoding='utf-8')):
            if ln.startswith(HEAD_MARK):
                flush()
                size = 0
                sekce = clip(ln[1:].replace('▾', '').replace('▸', ''), 90).strip()
                continue
            if len(ln) < 3:
                continue
            for part in split_long(ln, MAX_CHUNK):
                if buf and size + len(part) > MAX_CHUNK:
                    flush()
                    size = 0
                buf.append(part)
                size += len(part) + 1
        flush()
    return out


def build_index(chunks):
    n = len(chunks)
    post = {}
    for i, c in enumerate(chunks):
        toks = tokenize(c['t']) * 2 + tokenize(c['x'])  # titulek má dvojnásobnou váhu
        tf = {}
        for t in toks:
            tf[t] = tf.get(t, 0) + 1
        for t, k in sorted(tf.items()):
            post.setdefault(t, []).extend([i, k])
    max_df = max(20, int(n * MAX_DF_RATIO))
    post = {t: v for t, v in sorted(post.items()) if len(v) // 2 <= max_df}
    meta = [{'u': c['u'], 't': c['t']} for c in chunks]
    # otisk obsahu: Worker s ním stahuje dávky textů, takže se nikdy nespojí nový rejstřík se starými texty
    h = hashlib.sha1(json.dumps([c['x'] for c in chunks], ensure_ascii=False).encode('utf-8')).hexdigest()[:12]
    return {'v': 1, 'h': h, 'shard': SHARD, 'chunks': meta, 'post': post}


def write_if_changed(path, obj):
    data = json.dumps(obj, ensure_ascii=False, separators=(',', ':'))
    if path.exists() and path.read_text(encoding='utf-8') == data:
        return False
    path.write_text(data, encoding='utf-8')
    return True


def main():
    chunks = chunks_jednani() + chunks_lide() + chunks_slozeni() + chunks_stranky() + chunks_fakta() + chunks_extra()
    idx = build_index(chunks)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    SHARD_DIR.mkdir(exist_ok=True)
    zmeneno = write_if_changed(OUT, idx)
    pocet = math.ceil(len(chunks) / SHARD)
    for k in range(pocet):
        texty = [c['x'] for c in chunks[k * SHARD:(k + 1) * SHARD]]
        zmeneno |= write_if_changed(SHARD_DIR / f'{k}.json', texty)
    for stary in SHARD_DIR.glob('*.json'):
        if int(stary.stem) >= pocet:
            stary.unlink()
            zmeneno = True
    kb = OUT.stat().st_size / 1024
    print(f'PečkyBot index: {len(chunks)} úryvků v {pocet} dávkách, {len(idx["post"])} tokenů, '
          f'rejstřík {kb:.0f} kB ({"přepsáno" if zmeneno else "beze změny"})')


if __name__ == '__main__':
    main()
