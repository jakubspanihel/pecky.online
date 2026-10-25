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
    do = date.fromordinal(date.today().toordinal() + 14).isoformat()
    bl = [e for e in data if e['category'] in ('akce', 'volby', 'zastupitelstvo', 'rada')
          and dnes <= (e.get('date_end') or e['date']) and e['date'] <= do]
    bl.sort(key=lambda e: (e['date'], e.get('time') or ''))
    if bl:
        r = []
        for e in bl[:20]:
            x = f"{DNY[_d(e['date']).weekday()]} {_d(e['date']).day}. {_d(e['date']).month}."
            if e.get('date_end') and e['date_end'] != e['date']:
                x += f"–{cz(e['date_end'])}"
            if e.get('time'):
                x += f" {e['time']}"
            x += f" {e['title']}"
            if e.get('place'):
                x += f" ({e['place']})"
            r.append(x)
        out.append({'u': '/kalendar/', 't': 'Kalendář — Nejbližší akce',
                    'x': _clip('Nejbližší akce, co se děje v Pečkách, co nového, program na příští dva týdny, '
                               'kulturní a společenské akce, víkend, tento týden: ' + '; '.join(r) + '.', 1800)})
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


SVOZ_LOKALITY = [
    {'id': 'sever', 'nazev': 'Pečky sever a Velké Chvalovice', 'kom': 'komunalni-sever',
     'kom_nazev': 'Komunální odpad'},
    {'id': 'jih', 'nazev': 'Pečky jih', 'kom': 'komunalni-jih', 'kom_nazev': 'Komunální odpad'},
    {'id': 'sidliste', 'nazev': 'Pečky sídliště', 'kom': 'komunalni-sidliste', 'kom_nazev': 'Komunální odpad'},
]
SVOZ_PRAVIDLO = {
    'komunalni-sever': 'každé druhé pondělí, od června do srpna každé pondělí.',
    'komunalni-jih': 'každé druhé úterý, od června do srpna každé úterý.',
    'komunalni-sidliste': 'každé pondělí.',
    'bio': 'každé úterý podle rozpisu (v lednu a únoru jen jednou měsíčně).',
    'plast': 'vždy první pátek v měsíci.',
    'papir': 'vždy první pátek v měsíci.',
}


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
    typy = {t['id']: t for t in sv['types']}
    rok = sv['meta']['year']

    def mesice(ty):
        by_m = defaultdict(list)
        for iso in ty['dates']:
            d = _d(iso)
            by_m[d.month].append(str(d.day) + '.')
        return '; '.join(f"{MESICE_1P[m - 1]} {' '.join(ds)}" for m, ds in sorted(by_m.items()))

    URL = '/kalendar/svoz.html'
    for lok in SVOZ_LOKALITY:
        # krátké úryvky (hledání je citlivé na délku): pravidla lokality + termíny komunálního odpadu
        t = (f"Svoz odpadu {lok['nazev']} — harmonogram svozu odpadů z domácností {rok}, kdy se odpad vyváží "
             f"(popelnice, odvoz): komunální odpad {SVOZ_PRAVIDLO[lok['kom']]} BIO odpad {SVOZ_PRAVIDLO['bio']} "
             f"Plast a papír {SVOZ_PRAVIDLO['plast']} Harmonogram neuvádí, které ulice patří do které lokality. "
             f"Přehled k vytištění: {URL}.")
        out.append({'u': URL, 't': f"Kalendář — svoz odpadu: {lok['nazev']}", 'x': _clip(t, MAX + 200)})
        t = (f"Svoz komunálního odpadu {lok['nazev']} {rok}, kdy jedou popelnice: {SVOZ_PRAVIDLO[lok['kom']]} "
             f"Termíny podle měsíců: {mesice(typy[lok['kom']])}.")
        out.append({'u': URL, 't': f"Kalendář — svoz odpadu: komunální odpad, {lok['nazev']}", 'x': _clip(t, MAX + 350)})
    t = (f"Svoz BIO odpadu Pečky a Velké Chvalovice {rok}, kdy jede bioodpad (hnědá popelnice, zahradní odpad): "
         f"{SVOZ_PRAVIDLO['bio']} Termíny podle měsíců: {mesice(typy['bio'])}.")
    out.append({'u': URL, 't': 'Kalendář — svoz odpadu: BIO odpad', 'x': _clip(t, MAX + 350)})
    t = (f"Svoz plastu a papíru Pečky a Velké Chvalovice {rok}, kdy jedou plasty a papír (žlutý a modrý kontejner): "
         f"{SVOZ_PRAVIDLO['plast']} Termíny podle měsíců: {mesice(typy['plast'])}.")
    out.append({'u': URL, 't': 'Kalendář — svoz odpadu: plast a papír', 'x': _clip(t, MAX + 350)})
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
     'restaurace, hospoda, hostinec, kavárna, kde se najíst, kde se dobře najíst, jídlo, oběd, pivo, na pivo, bar, občerstvení',
     'Restaurace, hospody a kavárny — kde si dát pivo, oběd a jídlo'),
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
        if 'pivo' in nazev:
            jm = '; '.join(_radek_jidlo(o) for o in lst)
            out.append({'u': '/lide/', 't': f'Organizace — {nazev}',
                        'x': _clip(f'{nazev}. Kde se najíst, kam na pivo, hospoda, restaurace, hostinec, kavárna, jídlo, '
                                   f'oběd, otevírací doba, adresa. Podniky: {jm}.', 1500)})
            continue
        jm = '; '.join(o['name'] + (f" ({o['address']})" if o.get('address') and k_adr(nazev) else '') for o in lst)
        out.append({'u': '/lide/', 't': f'Organizace — {nazev}',
                    'x': _clip(f'{nazev}. Přehled, seznam, jaké existují, kdo působí: {slova}. Organizace: {jm}.', MAX + 400)})
    return out


def _hodiny_kratce(oh):
    if not oh or not oh.get('hours'):
        return ''
    h = oh['hours']
    c = Counter(v for v in h.values() if v)
    if not c:
        return ''
    typ, _ = c.most_common(1)[0]
    zav = [DNY[i] for i, k in enumerate(['po', 'ut', 'st', 'ct', 'pa', 'so', 'ne']) if not h[k]]
    return 'otevřeno ' + typ.replace('-', '–') + (f', zavřeno {", ".join(zav)}' if zav else '')


def _radek_jidlo(o):
    x = o['name']
    det = [d for d in (o.get('address'), _hodiny_kratce(o.get('opening_hours'))) if d]
    return x + (f" ({'; '.join(det)})" if det else '')


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
        mm = re.match(r'\d{4}-(\d{2})', e['slug'])
        cis = f" Označení čísla {int(mm.group(1))}/{e['year']}." if mm else ''
        t = [f"Pečecké noviny, číslo {e['label']} (rok {e['year']}).{cis}"]
        if e.get('page_count'):
            t.append(f"Počet stran: {e['page_count']}.")
        if titulni:
            t.append('Úvodní strana čísla (text z PDF): ' + _clip(titulni, 260))
        url = f"/noviny/Data/PN%20{e['year']}/{e['slug']}.pdf"
        out.append({'u': url, 't': f"Pečecké noviny {e['label']}", 'x': _clip(' '.join(t), MAX)})
    return out


def chunks_noviny_pravidla():
    """Pravidla pro vydávání měsíčníku Pečecké noviny (čl. I–X) — po článcích.
    Zdroj: noviny/Data/pravidla_pro_vydavani_PN (2026).pdf; text z PDF leží vedle
    (pdftotext, stejný název s příponou .txt)."""
    txt = (ROOT / 'noviny/Data/pravidla_pro_vydavani_PN (2026).txt').read_text(encoding='utf-8')
    txt = txt.replace('\x0c', '\n')
    url = '/noviny/Data/pravidla_pro_vydavani_PN%20(2026).pdf'
    casti = re.split(r'\n\s*(Článek [IVX]+)\s*\n', txt)
    out = []
    for i in range(1, len(casti) - 1, 2):
        cislo, telo = casti[i], casti[i + 1].strip()
        nazev, _, rest = telo.partition('\n')
        nazev = nazev.strip()
        odst = [re.sub(r'\s+', ' ', x).strip() for x in re.split(r'\n\s*\n|\n(?=\d+\. )', rest)]
        zahlavi = (f'Pravidla pro vydávání měsíčníku Pečecké noviny (Rada města, UR-263-31/23, účinná od 12. 9. 2023),'
                   f' {cislo} — {nazev}.')
        for x in _pack(zahlavi, [o for o in odst if o]):
            out.append({'u': url, 't': f'Pečecké noviny — pravidla vydávání, {cislo} ({nazev})', 'x': x})
    return out


# ---------------------------------------------------------------- 5. Na oběd

def chunks_naobed():
    d = _load('naobed/restaurace.json')
    orgs = {o['id']: o for o in _load('lide/organizations.json')['organizations']}
    out = []
    for skup, hlavni in (('restaurace', True), ('dalsi', False)):
        for r in d.get(skup, []):
            t = [f"{r['name']} — restaurace, hospoda, kde se najíst, pivo, jídlo, oběd v Pečkách" + (f" ({r['note']})" if r.get('note') else '') + '.']
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


# ---------------------------------------------------------------- shrnutí jednání (jednani/shrnuti/)

def _md_plain(t):
    return re.sub(r'\s+', ' ', re.sub(r'\*+', '', t)).strip()


def shrnuti_jednani(jid):
    """Shrnutí jednání z jednani/shrnuti/{datum}-{typ}.md (postup:
    jednani/INSTRUKCE-shrnuti-schuzky.md) jako {'temata': [...], 'shrnuti': [...]}
    v čistém textu; None, když soubor neexistuje. jid = hash jednání (rada-2026-10-12,
    kontrolni-vybor-2026-08-28)."""
    m = re.match(r'^(.*)-(\d{4}-\d{2}-\d{2})$', jid)
    if not m:
        return None
    path = ROOT / 'jednani' / 'shrnuti' / f'{m.group(2)}-{m.group(1)}.md'
    if not path.exists():
        return None
    out, sekce = {'temata': [], 'shrnuti': []}, None
    for line in path.read_text(encoding='utf-8').splitlines():
        h = re.match(r'^##\s+(.+)', line)
        if h:
            sekce = 'temata' if h.group(1).startswith('Nejdůležitější') else 'shrnuti'
            continue
        t = re.sub(r'^(\d+\.|-)\s+', '', line.strip())
        # závěrečná kurzívní poznámka o zdroji je určena čtenáři webu, ne odpovědím
        if t and sekce and not (line.strip().startswith('*') and not line.strip().startswith('**')):
            out[sekce].append(_md_plain(t))
    return out if out['temata'] or out['shrnuti'] else None


def chunks_shrnuti():
    """Úryvky se shrnutím jednání (nejdůležitější témata + shrnutí) pro fulltext."""
    out = []
    meetings = []
    for fn in ('pecky-jednani', 'komise', 'vybory', 'skolska-rada'):
        for m in _load(f'jednani/{fn}.json')['meetings']:
            if m.get('id'):
                jid, kde = m['id'], m['type']
            else:
                jid = ('zastupitelstvo-' if m['type'] == 'Zastupitelstvo' else 'rada-') + m['date']
                kde = 'Zastupitelstvo města' if m['type'] == 'Zastupitelstvo' else 'Rada města'
            meetings.append((m['date'], jid, f"{kde} {m.get('label', '')}".strip()))
    for datum, jid, nazev in sorted(meetings):
        s = shrnuti_jednani(jid)
        if not s:
            continue
        zahlavi = f"Shrnutí jednání: {nazev}. Nejdůležitější témata, o čem se jednalo, co se projednalo."
        kusy = (['Nejdůležitější témata: ' + ' '.join(s['temata'])] if s['temata'] else []) + s['shrnuti']
        for x in _pack(zahlavi, kusy, MAX + 150):
            out.append({'u': f'/jednani/#{jid}', 't': f'Shrnutí jednání — {nazev}', 'x': x})
    return out


# ---------------------------------------------------------------- 7. voda

def _cz_m(iso):
    return cz(iso) if iso.count('-') == 2 else f"{MESICE_1P[int(iso[5:7]) - 1]} {iso[:4]}"


def _kc(x):
    return f'{x:.2f}'.replace('.', ',') if x is not None else None


def _vod_blok(d, nazev, url, tema):
    """Úpravna vody / vodojem: fakta, text, mezery a časová osa (nejnovější první)."""
    out = []
    zahl = f'Voda, vodní hospodářství — {nazev}.'
    kusy = [f"{f['label']}: {f['value']}." for f in d['summary']['facts']]
    kusy += d['summary']['text']
    for x in _pack(zahl, kusy, MAX + 150):
        out.append({'u': url, 't': f'Voda — {nazev}', 'x': x})
    gaps = d['summary'].get('gaps') or []
    for x in _pack(f'{zahl} Co ve zdrojích chybí:', gaps, MAX + 150):
        out.append({'u': url, 't': f'Voda — {nazev} — mezery ve zdrojích', 'x': x})
    kusy = []
    for e in sorted(d['events'], key=lambda e: e['date'], reverse=True):
        zdroje = ', '.join(z['label'] for z in e.get('sources', []))
        kusy.append(f"{e['date']}: {e['title']}. {e['text']}" + (f' ({zdroje})' if zdroje else ''))
    for x in _pack(f'Voda — {nazev} — historie, časová osa, co se kdy stalo:', kusy, MAX + 150):
        out.append({'u': url, 't': f'Voda — {nazev} — časová osa', 'x': x})
    return out


def chunks_voda():
    out = []
    ceny = _load('voda/ceny.json')
    roky = ceny['years']
    nej = roky[0]
    it = nej['items']
    out.append({'u': '/voda/', 't': 'Voda — cena vodného a stočného', 'x': (
        f"Kolik stojí voda v Pečkách: cena vodného a stočného, ceník, cena za metr krychlový (m3), "
        f"kolik platí domácnost. Od 1. 1. {nej['year']} vodné {_kc(it['vodne']['s_dph'])} Kč/m³ s DPH "
        f"({_kc(it['vodne']['bez_dph'])} bez DPH), stočné {_kc(it['stocne']['s_dph'])} Kč/m³ s DPH "
        f"({_kc(it['stocne']['bez_dph'])} bez DPH), celkem {_kc(it['celkem']['s_dph'])} Kč/m³ s DPH "
        f"({_kc(it['celkem']['bez_dph'])} bez DPH), DPH {nej['vat_rate']} %. "
        f"{nej.get('note', '')} Provozovatel: Pečecké služby, s.r.o.")})
    radky = []
    for y in roky:
        i = y['items']
        s_dph = (f"s DPH vodné {_kc(i['vodne']['s_dph'])}, stočné {_kc(i['stocne']['s_dph'])}, celkem {_kc(i['celkem']['s_dph'])} Kč/m³, "
                 if i['celkem']['s_dph'] is not None else '')
        radky.append(f"Rok {y['year']}: {s_dph}bez DPH vodné {_kc(i['vodne']['bez_dph'])}, stočné "
                     f"{_kc(i['stocne']['bez_dph'])}, celkem {_kc(i['celkem']['bez_dph'])} Kč/m³."
                     + (f" {y['note']}" if y.get('note') else '') + f" Zdroj: {y['source']['label']}.")
    for x in _pack('Historie ceny vodného a stočného podle let, vývoj ceny vody, ceník (Kč za m³):', radky, MAX + 250):
        out.append({'u': '/voda/', 't': 'Voda — historie ceníku vodného a stočného', 'x': x})
    if ceny.get('gaps'):
        out.append({'u': '/voda/', 't': 'Voda — ceník: chybějící roky',
                    'x': _clip('Ceník vodného a stočného, chybějící roky: ' + ceny['gaps'], MAX + 150)})
    out += _vod_blok(_load('voda/upravna.json'), 'Úpravna vody Pečky, zdroj Tatce', '/voda/#upravna', 'upravna')
    out += _vod_blok(_load('voda/vodojem.json'), 'Věžový vodojem Pečky (vodárna)', '/voda/#vodojem', 'vodojem')
    vz = _load('voda/rozbory.json')['samples']
    vz = sorted(vz, key=lambda v: v['date'])
    nej_v = vz[-1]
    zahl = (f"Rozbory pitné vody, kvalita vody v Pečkách, laboratorní protokoly: {len(vz)} protokolů od {_cz_m(vz[0]['date'])} "
            f"do {_cz_m(nej_v['date'])}, laboratoř Vodohospodářská společnost Vrchlice – Maleč, objednatel Pečecké služby.")
    out.append({'u': '/voda/#rozbory', 't': 'Voda — rozbory pitné vody', 'x': zahl})
    kusy = []
    for v in reversed(vz):
        pr = v['params']
        mimo = [k for k, p in pr.items() if p.get('ok') is False]
        zn = lambda k: (f"{k} {str(pr[k]['v']).replace('.', ',')} {pr[k].get('u', '')}" if k in pr else None)
        klic = ', '.join(x for x in (zn('Dusičnany'), zn('Sírany'), zn('Suma vápníku a hořčíku'), zn('pH')) if x)
        kusy.append(f"{_cz_m(v['date'])}, {v['misto']} (protokol {v['protokol']}): {klic or 'viz PDF'}; "
                    + (f"mimo limit: {', '.join(mimo)}." if mimo else 'všechny hodnocené ukazatele v limitu.'))
    for x in _pack('Rozbory pitné vody podle data odběru, od nejnovějšího (tvrdost, dusičnany, sírany, limity):', kusy, MAX + 250):
        out.append({'u': '/voda/#rozbory', 't': 'Voda — rozbory pitné vody podle data', 'x': x})
    return out


def _cz(iso):
    try:
        y, m, dd = iso.split('-')
        return f'{int(dd)}. {int(m)}. {y}'
    except ValueError:
        return iso


def chunks_okolo():
    """Sekce /okolo/ (Pro přespolní): obce správního obvodu Peček, popisy znaků a vlajek z registru symbolů."""
    p = ROOT / 'okolo/vesnice-okolo.json'
    if not p.exists():
        return []
    d = json.loads(p.read_text(encoding='utf-8'))
    obce = d.get('obce') or []
    out = []
    if obce:
        names = ', '.join(o['nazev'] for o in obce)
        first = obce[0]
        out.append({
            'u': '/okolo/',
            't': 'Okolo — Obce ve správním obvodu Peček',
            'x': (f"Obce ve správním obvodu obce s pověřeným obecním úřadem Pečky (okres {first.get('okres', 'Kolín')}, "
                  f"{first.get('kraj', 'Středočeský')} kraj): {names}. Obce v okolí Peček, vesnice kolem Peček, "
                  f"sousední obce. Stránka Okolo (Pro přespolní) zobrazuje mapu těchto {len(obce)} obcí se znaky a vlajkami. "
                  f"Zdroj: registr komunálních symbolů (rekos.psp.cz), stav k {_cz(d.get('stazeno', ''))}."),
        })
    for o in obce:
        parts = [f"{o['nazev']} — obec ve správním obvodu Peček (okres {o.get('okres', '')}, pověřený úřad {o.get('pou', '')})."]
        for klic, nazev in (('znak', 'Znak'), ('vlajka', 'Vlajka')):
            sym = o.get(klic) or {}
            if sym.get('popis'):
                rozh = f" Rozhodnutí Poslanecké sněmovny č. {sym['cislo_rozhodnuti']} ze dne {sym['datum_rozhodnuti']}." \
                    if sym.get('cislo_rozhodnuti') and sym.get('datum_rozhodnuti') else ''
                parts.append(f"{nazev} obce {o['nazev']}: {sym['popis']}{rozh}")
        if o.get('rekos_url'):
            parts.append(f"Registr symbolů: {o['rekos_url']}.")
        out.append({'u': '/okolo/', 't': f"Okolo — {o['nazev']}", 'x': ' '.join(parts)})
    return out


def chunks_extra():
    out = []
    for fn in (chunks_komise, chunks_vybory, chunks_skolska_rada, chunks_kalendar, chunks_organizace,
               chunks_noviny, chunks_noviny_pravidla, chunks_naobed, chunks_absence, chunks_shrnuti, chunks_voda, chunks_okolo):
        out += fn()
    return out
