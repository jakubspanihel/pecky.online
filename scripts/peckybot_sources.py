"""Další zdroje do znalostního indexu PečkyBota (kalendář, komise, výbory, školská rada,
organizace, noviny, Na oběd, absence). Každý zdroj je funkce vracející seznam úryvků
{'u': url, 't': titulek, 'x': text}; chunks_extra() je spojí. Volá se z build_peckybot_index.py.

Fakta jsou jen z datových souborů v repu. Tokenizace je slovní (TF-IDF), proto texty
obsahují datum ve více tvarech (5. 10. 2026, 5. října 2026, pondělí) a přirozená slova
(„kdy“, „kde“, „kdo“), která lidé v dotazech používají.
"""
import json
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

MAX = 700          # cílová délka textu úryvku
MIN = 60

DNY = ['pondělí', 'úterý', 'středa', 'čtvrtek', 'pátek', 'sobota', 'neděle']
DNY_KRATCE = ['po', 'út', 'st', 'čt', 'pá', 'so', 'ne']
DNY_4P = ['v pondělí', 'v úterý', 've středu', 've čtvrtek', 'v pátek', 'v sobotu', 'v neděli']
MESICE_2P = ['ledna', 'února', 'března', 'dubna', 'května', 'června', 'července', 'srpna',
             'září', 'října', 'listopadu', 'prosince']
MESICE_1P = ['leden', 'únor', 'březen', 'duben', 'květen', 'červen', 'červenec', 'srpen',
             'září', 'říjen', 'listopad', 'prosinec']


def _load(rel):
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))


def _clip(text, n):
    text = re.sub(r'\s+', ' ', text or '').strip()
    if len(text) <= n:
        return text
    return text[:n].rsplit(' ', 1)[0] + '…'


def _d(iso):
    y, m, d = (int(x) for x in iso.split('-'))
    return date(y, m, d)


def cz(iso):
    """5. 10. 2026"""
    d = _d(iso)
    return f'{d.day}. {d.month}. {d.year}'


def datum_tvary(iso):
    """'pondělí 5. 10. 2026 (5. října 2026, říjen 2026, 2026-10-05)'"""
    d = _d(iso)
    return (f'{DNY[d.weekday()]} {d.day}. {d.month}. {d.year} '
            f'({d.day}. {MESICE_2P[d.month - 1]} {d.year}, {MESICE_1P[d.month - 1]} {d.year})')


def rozsah(iso, iso_end=None):
    if not iso_end or iso_end == iso:
        return datum_tvary(iso)
    return f'od {datum_tvary(iso)} do {cz(iso_end)} ({_d(iso_end).day}. {MESICE_2P[_d(iso_end).month - 1]} {_d(iso_end).year})'


def _cas(a, b=None):
    if not a:
        return ''
    return f'{a}–{b}' if b else a


def _pack(prefix, pieces, limit=MAX):
    """Složí kousky textu do úryvků do délky limit; každý úryvek začíná prefixem."""
    out, buf = [], ''
    for p in pieces:
        p = _clip(p, limit - len(prefix) - 1)
        if not p:
            continue
        if buf and len(prefix) + len(buf) + len(p) + 2 > limit:
            out.append(prefix + ' ' + buf)
            buf = ''
        buf = (buf + ' ' + p).strip()
    if buf:
        out.append(prefix + ' ' + buf)
    return out


# ---------------------------------------------------------------- 1. komise, výbory, školská rada

def _ucast(a):
    if not a:
        return ''
    parts = []
    if a.get('present') is not None and a.get('total'):
        parts.append(f"Přítomno {a['present']} z {a['total']} členů.")
    if a.get('present_names'):
        parts.append('Přítomni: ' + ', '.join(a['present_names']) + '.')
    ab = a.get('absent_names') or []
    if ab:
        parts.append('Nepřítomni: ' + ', '.join(
            f"{x['name']} ({x['note']})" if x.get('note') else x['name'] for x in ab) + '.')
    if a.get('guests'):
        parts.append('Hosté: ' + ', '.join(
            f"{x['name']} ({x['note']})" if x.get('note') else x['name'] for x in a['guests']) + '.')
    return ' '.join(parts)


def _hlasy(r):
    if r.get('pro') is None:
        return ''
    return f" (pro {r['pro']}, proti {r.get('proti') or 0}, zdrželo se {r.get('zdrzel') or 0})"


def _chunks_orgán(path, popis):
    out = []
    data = _load(path)
    for m in sorted(data['meetings'], key=lambda x: x['date']):
        typ = m['type']
        url = f"/jednani/#{m['id']}"
        kdy = datum_tvary(m['date'])
        cas = _cas(m.get('time'), m.get('time_end'))
        pre = f"{typ}, {cz(m['date'])}:"
        titul = f"{typ} — zápis {cz(m['date'])}"
        # 1) hlavička: kdy, kdo vedl, program
        h = [f"Jednání — {typ} — {kdy}" + (f', čas {cas}' if cas else '') + '.']
        if m.get('chair'):
            h.append(f"Předseda/předsedkyně, kdo vedl jednání: {m['chair']}.")
        if m.get('recorded_by'):
            h.append(f"Zapisoval/a: {m['recorded_by']}.")
        prog = '; '.join(f"{a['n']}. {a['t']}" for a in m.get('agenda', []))
        if prog:
            h.append('Program jednání: ' + prog + '.')
        out.append({'u': url, 't': f'{titul} — program a vedení', 'x': _clip(' '.join(h), MAX + 150)})
        # 2) docházka
        uc = _ucast(m.get('attendance'))
        if uc:
            out.append({'u': url, 't': f'{titul} — účast, členové, kdo byl přítomen',
                        'x': _clip(f"{typ}, {kdy}. Docházka, přítomnost a absence členů. {uc}", MAX + 250)})
        # 3) shrnutí a usnesení
        pieces = list(m.get('summary') or [])
        for r in m.get('resolutions', []):
            t = ('Usnesení' + (f" {r['n']}" if r.get('n') else '') + ': ' + (r.get('text') or '') + _hlasy(r))
            if r.get('note'):
                t += ' Poznámka: ' + r['note']
            pieces.append(t)
        for i, x in enumerate(_pack(pre, pieces)):
            out.append({'u': url, 't': f'{titul} — obsah jednání, usnesení a doporučení', 'x': x})
    return out, data


def chunks_komise():
    out, _ = _chunks_orgán('jednani/komise.json', 'komise rady města')
    return out


def chunks_vybory():
    out, _ = _chunks_orgán('jednani/vybory.json', 'výbor zastupitelstva')
    return out


def chunks_skolska_rada():
    out, d = _chunks_orgán('jednani/skolska-rada.json', 'školská rada')
    er = d.get('election_rules')
    if er:
        out.append({'u': '/jednani/', 't': 'Školská rada — volební řád, složení, počet členů',
                    'x': _clip(f"Školská rada ZŠ Pečky. {er['text']} Zdroj: {er['source']}.", MAX + 200)})
    for e in d.get('elections', []):
        t = f"Školská rada, volby a složení, {cz(e['date'])}: {e['kind']}. {e.get('note') or ''}"
        if e.get('elected'):
            t += ' Zvoleni: ' + ', '.join(e['elected']) + '.'
        out.append({'u': '/jednani/', 't': f"Školská rada — volby {cz(e['date'])}", 'x': _clip(t, MAX + 100)})
    for o in d.get('other_decisions', []):
        out.append({'u': '/jednani/', 't': f"Školská rada — rozhodnutí {cz(o['date'])}",
                    'x': _clip(f"Školská rada, {cz(o['date'])}: {o['text']}", MAX)})
    return out


# ---------------------------------------------------------------- 2. kalendář

def _org_names():
    return {o['id']: o.get('short_name') or o['name'] for o in _load('lide/organizations.json')['organizations']}


def _vzorec_serie(evs):
    """'každé pondělí 14:45, středa 16:00' z opakujících se termínů."""
    c = Counter((_d(e['date']).weekday(), e.get('time') or '') for e in evs)
    nejc = sorted(c.items(), key=lambda kv: (kv[0][0], kv[0][1]))
    out = []
    for (wd, cas), n in nejc:
        if n < max(2, 0.15 * max(c.values())):
            continue
        out.append(f"{DNY_4P[wd]}" + (f' v {cas}' if cas else ''))
    return ', '.join(out)


def chunks_kalendar():
    data = _load('kalendar/udalosti.json')['events']
    org = _org_names()
    out = []
    meet_ids = set()
    for fn, key in (('jednani/pecky-jednani.json', 'meetings'),):
        for m in _load(fn)[key]:
            if m.get('agenda') or m.get('resolutions'):
                meet_ids.add((m['type'], m['date']))
    kurzy = defaultdict(list)
    for e in sorted(data, key=lambda x: (x['date'], x.get('time') or '')):
        cat = e['category']
        poradatel = e.get('organizer_name') or org.get(e.get('organizer')) or ''
        if cat == 'akce':
            kdy = rozsah(e['date'], e.get('date_end'))
            t = [f"Akce v Pečkách: {e['title']}. Kdy, datum: {kdy}."]
            wk = _d(e['date']).weekday()
            if wk >= 5 or (e.get('date_end') and _d(e['date_end']).weekday() >= 5 and wk >= 4):
                t.append('Koná se o víkendu (sobota, neděle).')
            if e.get('time'):
                t.append(f"Začátek v {e['time']}.")
            elif e.get('all_day'):
                t.append('Celodenní akce.')
            if e.get('place'):
                t.append(f"Kde, místo konání: {e['place']}.")
            if poradatel:
                t.append(f"Pořadatel: {poradatel}.")
            if e.get('description') and e['description'] not in (e.get('place') or ''):
                t.append(_clip(e['description'], 260))
            out.append({'u': '/kalendar/', 't': f"Kalendář — {e['title']} ({cz(e['date'])})",
                        'x': _clip(' '.join(t), MAX + 100)})
        elif cat in ('rada', 'zastupitelstvo', 'volby'):
            # už proběhlá jednání s programem jsou v indexu z Jednání; tady jen plánované termíny
            typ = {'rada': 'Rada', 'zastupitelstvo': 'Zastupitelstvo'}.get(cat)
            if typ and (typ, e['date']) in meet_ids:
                continue
            if e['date'] < '2026-09-01':
                continue
            nazev = e['title']
            kdy = rozsah(e['date'], e.get('date_end'))
            t = f"Termín: {nazev}. Kdy, datum: {kdy}."
            if e.get('time'):
                t += f" Začátek v {e['time']}."
            if e.get('description'):
                t += ' ' + e['description'] + '.'
            url = e['link'] if (e.get('link') or '').startswith('/') else '/kalendar/'
            out.append({'u': url, 't': f"Kalendář — {nazev} ({cz(e['date'])})", 'x': _clip(t, MAX)})
        elif cat == 'kurz':
            kurzy[(e['title'], e.get('organizer'))].append(e)
    # pravidelné kurzy a kroužky: jeden úryvek na sérii
    for (titul, o), evs in kurzy.items():
        evs.sort(key=lambda x: x['date'])
        e0 = evs[0]
        poradatel = e0.get('organizer_name') or org.get(o) or ''
        t = [f"Pravidelný kurz, kroužek nebo cvičení: {titul}."]
        if poradatel:
            t.append(f"Pořádá: {poradatel}.")
        v = _vzorec_serie(evs)
        if v:
            t.append(f"Kdy se koná: {v}.")
        t.append(f"Termíny od {cz(evs[0]['date'])} do {cz(evs[-1]['date'])}, celkem {len(evs)} lekcí.")
        if e0.get('place'):
            t.append(f"Kde, místo: {e0['place']}.")
        if e0.get('description') and e0['description'] != e0.get('place'):
            t.append(_clip(e0['description'], 160))
        out.append({'u': '/kalendar/', 't': f"Kalendář — kurz {titul}" + (f' ({poradatel})' if poradatel else ''),
                    'x': _clip(' '.join(t), MAX)})
    out += _chunks_pristi(data)
    out += _chunks_provoz()
    return out


def _chunks_pristi(data):
    """Příští jednání po dnešku (podle data sestavení indexu)."""
    dnes = date.today().isoformat()
    jedn = [e for e in data if e['category'] in ('rada', 'zastupitelstvo', 'vybor') and e['date'] >= dnes]
    jedn.sort(key=lambda e: (e['date'], e['title']))
    out = []
    if jedn:
        kusy = [f"{e['title']} — {datum_tvary(e['date'])}" + (f", od {e['time']}" if e.get('time') else '')
                for e in jedn[:10]]
        out.append({'u': '/jednani/', 't': 'Kalendář — Příští jednání',
                    'x': _clip('Příští jednání, kdy je další zasedání zastupitelstva, rady, komise nebo výboru: '
                               + '; '.join(kusy) + '.', MAX + 400)})
    for cat, nazev in (('zastupitelstvo', 'zastupitelstva'), ('rada', 'rady města')):
        z = [e for e in jedn if e['category'] == cat]
        if z:
            e = z[0]
            out.append({'u': e['link'] if e.get('link', '').startswith('/') else '/jednani/',
                        't': f"Kalendář — Příští zasedání {nazev} ({e['title']}, {cz(e['date'])})",
                        'x': f"Příští zasedání {nazev}: {e['title']}, kdy: {datum_tvary(e['date'])}"
                             + (f", začátek v {e['time']}" if e.get('time') else '')
                             + ". Další jednání, příští schůze, termín."})
    return out


def _chunks_provoz():
    """Úřední hodiny, sběrný dvůr a svoz odpadu — z pravidel/harmonogramu, ne z tisíců dat."""
    out = []
    for fn, nazev, dopl in (
            ('kalendar/sberny-dvur.json', 'Sběrný dvůr Pečecké služby — otevírací doba', 'Kdy je otevřeno, sběrný dvůr'),):
        d = _load(fn)
        meta = d['meta']
        dny = defaultdict(list)
        for r in d['rules']:
            dny[r['weekday']].append(f"{r['from']}–{r['to']}")
        popis = '; '.join(f"{DNY[w]} {', '.join(h)}" for w, h in sorted(dny.items()))
        t = (f"{nazev}. {dopl}. {meta.get('place', '')}. Otevírací doba podle dne: {popis}. "
             f"Platí od {cz(meta['from'])}. Zdroj: {meta['evidence']['label']}.")
        out.append({'u': '/kalendar/', 't': 'Kalendář — ' + nazev, 'x': _clip(t, MAX + 100)})
    sv = _load('kalendar/svoz-odpadu.json')
    for ty in sv['types']:
        by_m = defaultdict(list)
        for iso in ty['dates']:
            d = _d(iso)
            by_m[d.month].append(str(d.day) + '.')
        mesice = '; '.join(f"{MESICE_1P[m - 1]} {' '.join(ds)}" for m, ds in sorted(by_m.items()))
        t = (f"{ty['title']} — harmonogram svozu odpadu {sv['meta']['year']}, kdy se odpad vyváží (popelnice, kontejner, "
             f"odvoz). Místo: {ty.get('place', '')}. Pravidlo: {ty.get('rule', '')}. "
             f"Termíny svozu podle měsíců: {mesice}.")
        out.append({'u': '/kalendar/', 't': f"Kalendář — svoz odpadu: {ty['title']}", 'x': _clip(t, MAX + 350)})
    return out


# ---------------------------------------------------------------- 3. organizace

TYP_SLOVA = {
    'urad': 'úřad, radnice, městský úřad, instituce města',
    'spolek': 'spolek, spolky, kluby, sdružení, zájmový kroužek, volnočasové aktivity',
    'politicke': 'politické uskupení, strana, hnutí, kandidátka, volby, uskupení, sdružení kandidátů',
    'prispevkova': 'příspěvková organizace, organizace města, zřizovatel město',
    'firma': 'firma, podnik, služby, společnost',
    'jine': 'organizace, instituce',
}
PODKAT = [  # (klíč, regex nad jménem+poznámkou, slova, přehledový titulek)
    ('jidlo', r'hospod|hostinec|restaurac|kebab|pizz|wok|saloon|kavárn|bar\b|siňorit|marka|stříkačk',
     'restaurace, hospoda, hostinec, kavárna, kde se najíst, kde se dobře najíst, jídlo, oběd, pivo, bar, občerstvení',
     'Restaurace, hospody a kavárny — kde se najíst'),
    ('skola', r'(?<!ní )škol|mašink|vzdělávací',
     'škola, školka, mateřská škola, základní škola, vzdělávání, děti, žáci, školní jídelna, kroužky',
     'Školy, školky a vzdělávání'),
    ('sport', r'fotbal|volejbal|sokol|minigolf|bk pečky|dsa|glow|fit|tělocvičn|hasič',
     'sport, sportovní klub, sportovní kluby, oddíl, trénink, cvičení, tanec',
     'Sportovní kluby a oddíly'),
    ('kultura', r'knihovn|kulturní|umělecká|okrašlovací|modelář',
     'kultura, knihovna, kulturní dům, kulturní středisko, umění, akce, zájmové spolky',
     'Kultura, knihovna a zájmové spolky'),
]


def _podkat(o):
    hay = (o['name'] + ' ' + (o.get('note') or '')).lower()
    return [k for k in PODKAT if re.search(k[1], hay) and not (o['type'] == 'politicke')]


def _titul_dopl(o, typy):
    dop = [typy.get(o['type'], 'organizace').split(' (')[0]]
    sn = o.get('short_name')
    if sn and sn != o['name'] and sn.lower() not in o['name'].lower():
        dop.append(sn)
    if re.search('mateřsk', o['name'], re.I):
        dop.append('školka')
    return ' (' + ', '.join(dop) + ')'


def chunks_organizace():
    orgs = _load('lide/organizations.json')['organizations']
    people = {p['id']: p for p in _load('lide/people.json')['people']}
    aff = _load('lide/affiliations.json')['affiliations']
    by_org = defaultdict(list)
    for a in aff:
        by_org[a['organization_id']].append(a)
    typy = {'urad': 'úřad', 'spolek': 'spolek', 'politicke': 'politické uskupení (strana, hnutí, sdružení)',
            'prispevkova': 'příspěvková organizace', 'firma': 'firma', 'jine': 'organizace'}
    out = []
    for o in orgs:
        t = [f"Organizace: {o['name']}."]
        if o.get('short_name') and o['short_name'] != o['name']:
            t.append(f"Zkratka, krátký název: {o['short_name']}.")
        t.append(f"Typ: {typy.get(o['type'], o['type'])}. Kategorie: {TYP_SLOVA.get(o['type'], '')}.")
        for k in _podkat(o):
            t.append(k[2] + '.')
        if o.get('address'):
            t.append(f"Adresa, sídlo: {o['address']}.")
        if o.get('ico'):
            t.append(f"IČO: {o['ico']}.")
        if o.get('web'):
            t.append(f"Web: {o['web']}.")
        if o.get('former_names'):
            t.append('Dřívější názvy: ' + '; '.join(o['former_names']) + '.')
        if o.get('note'):
            t.append(_clip(o['note'].replace('`', ''), 330))
        oh = o.get('opening_hours')
        if oh and oh.get('hours'):
            h = '; '.join(f"{DNY_KRATCE[i]} {oh['hours'][k] or 'zavřeno'}"
                          for i, k in enumerate(['po', 'ut', 'st', 'ct', 'pa', 'so', 'ne']))
            t.append(f"Otevírací doba: {h}.")
        # lidé: nejdřív funkce (ne pouhé kandidatury), pak ostatní, jen když je jich málo
        links = sorted(by_org.get(o['id'], []),
                       key=lambda a: (a.get('role_type') == 'kandidatka', not a.get('current'), a.get('from') or ''))
        jm, videno = [], set()
        for a in links:
            p = people.get(a['person_id'])
            if not p or a['person_id'] in videno:
                continue
            videno.add(a['person_id'])
            jmeno = ' '.join(x for x in (p.get('title_before'), p.get('first_name'), p.get('last_name'),
                                         p.get('title_after')) if x)
            jm.append(f"{jmeno} ({a['role']})")
            if len(jm) >= 10:
                break
        if jm:
            t.append('Spojení lidé, členové a funkce: ' + ', '.join(jm) + (' a další.' if len(videno) < len(by_org.get(o['id'], [])) else '.'))
        out.append({'u': '/lide/', 't': f"Organizace — {o['name']}" + _titul_dopl(o, typy), 'x': _clip(' '.join(t), MAX + 250)})
    out += _prehledy_organizaci(orgs, typy)
    return out


def _prehledy_organizaci(orgs, typy):
    out = []
    skupiny = []
    skupiny.append(('Spolky a kluby v Pečkách', TYP_SLOVA['spolek'], [o for o in orgs if o['type'] == 'spolek']))
    skupiny.append(('Politická uskupení a strany v Pečkách', TYP_SLOVA['politicke'],
                    [o for o in orgs if o['type'] == 'politicke']))
    skupiny.append(('Příspěvkové organizace města Pečky', TYP_SLOVA['prispevkova'],
                    [o for o in orgs if o['type'] == 'prispevkova']))
    skupiny.append(('Firmy a podniky v Pečkách', TYP_SLOVA['firma'], [o for o in orgs if o['type'] == 'firma']))
    for k in PODKAT:
        skupiny.append((k[3], k[2], [o for o in orgs if k in _podkat(o)]))
    for nazev, slova, lst in skupiny:
        if not lst:
            continue
        jm = '; '.join(o['name'] + (f" ({o['address']})" if o.get('address') and k_adr(nazev) else '') for o in lst)
        out.append({'u': '/lide/', 't': f'Organizace — {nazev}',
                    'x': _clip(f'{nazev}. Přehled, seznam, jaké existují, kdo působí: {slova}. Organizace: {jm}.', MAX + 400)})
    return out


def k_adr(nazev):
    return 'najíst' in nazev or 'Školy' in nazev


# ---------------------------------------------------------------- 4. Pečecké noviny

def chunks_noviny():
    src = _load('noviny/pecky-noviny.json')
    out = []
    for e in src['editions']:
        if not e.get('slug'):
            continue
        # 1. strana = obálka s tématy čísla (verbatim text z PDF)
        titulni = ''
        pages = e.get('pages') or []
        if pages:
            titulni = re.sub(r'\s+', ' ', pages[0]).strip()
        t = [f"Pečecké noviny, číslo {e['label']} (rok {e['year']})."]
        if e.get('page_count'):
            t.append(f"Počet stran: {e['page_count']}.")
        if titulni:
            t.append('Úvodní strana čísla (text z PDF): ' + _clip(titulni, 260))
        url = f"/noviny/Data/PN%20{e['year']}/{e['slug']}.pdf"
        out.append({'u': url, 't': f"Pečecké noviny {e['label']}", 'x': _clip(' '.join(t), MAX)})
    return out


# ---------------------------------------------------------------- 5. Na oběd

def chunks_naobed():
    d = _load('naobed/restaurace.json')
    orgs = {o['id']: o for o in _load('lide/organizations.json')['organizations']}
    out = []
    for skup, hlavni in (('restaurace', True), ('dalsi', False)):
        for r in d.get(skup, []):
            t = [f"{r['name']} — restaurace, hospoda, jídlo v Pečkách" + (f" ({r['note']})" if r.get('note') else '') + '.']
            if hlavni:
                t.append('Denní menu, polední menu, co dnes k obědu, je na stránce Na oběd.')
            if r.get('address'):
                t.append(f"Kde, adresa: {r['address']}.")
            if r.get('phone'):
                t.append(f"Telefon: {r['phone']}.")
            if r.get('web') or (r.get('link') and r.get('linkLabel') == 'Web'):
                t.append(f"Web: {r.get('web') or r['link']}.")
            fb = r.get('facebook') or (r.get('link') if r.get('linkLabel', '').startswith('Facebook') else '')
            if fb:
                t.append(f"Facebook: {fb}.")
            oh = (orgs.get(r['id']) or {}).get('opening_hours')
            if oh and oh.get('hours'):
                h = '; '.join(f"{DNY[i]} {oh['hours'][k] or 'zavřeno'}"
                              for i, k in enumerate(['po', 'ut', 'st', 'ct', 'pa', 'so', 'ne']))
                t.append(f"Otevírací doba: {h}.")
                if oh.get('note'):
                    t.append(_clip(oh['note'], 160))
            out.append({'u': '/naobed/', 't': f"Na oběd — {r['name']}", 'x': _clip(' '.join(t), MAX + 150)})
    return out


# ---------------------------------------------------------------- 6. absence

def chunks_absence():
    d = _load('jednani/absence.json')
    meta = d['meta']
    out = []
    for ob in d['obdobi']:
        radky = [r for r in ob['radky'] if r['mandat'] >= 3]
        if not radky:
            continue
        radky.sort(key=lambda r: (-r['podil'], r['jmeno']))
        organ, per = ob['organ'], ob['obdobi']
        zahlavi = (f"Absence, docházka, kdo chyběl: {organ}, období {per}. Podle jmenné prezence v zápisech z "
                   f"{ob['jednani']} jednání ({cz(ob['od'])} až {cz(ob['do'])}). Podíl nepřítomnosti, od nejvyššího: ")
        kusy = [f"{r['jmeno']} {str(r['podil']).replace('.', ',')} % (chyběl/a {r['chybel']} z {r['mandat']}, "
                f"omluven/a {r['omluven']}, neomluven/a {r['nepritomen']})." for r in radky]
        for i, x in enumerate(_pack(zahlavi, kusy, MAX + 150)):
            out.append({'u': '/jednani/absence.html', 't': f"Absence — {organ} {per}", 'x': x})
    return out


def chunks_extra():
    out = []
    for fn in (chunks_komise, chunks_vybory, chunks_skolska_rada, chunks_kalendar, chunks_organizace,
               chunks_noviny, chunks_naobed, chunks_absence):
        out += fn()
    return out
