#!/usr/bin/env python3
"""
Vygeneruje kompaktní předpočítané soubory pro nástroje PečkyBota: peckybot/data/*.json.

Worker (Cloudflare Free, 10 ms CPU) nesmí parsovat velké zdrojové JSONy, proto z nich
tenhle skript předem spočítá malé soubory (formát viz peckybot/data/SCHEMA.md):
osoby.json, slozeni.json, kalendar.json, jednani.json, statistiky.json.

Logika (funkce, složení, uskupení, ústředna) se přebírá z build_peckybot_index.py,
aby si index a nástroje neodporovaly. Soubory se přepisují jen při změně obsahu,
výstup je deterministický (žádné časové razítko ani dnešní datum).

Spouští ho scripts/build.py; samostatně: python3 scripts/build_peckybot_tools.py
"""
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_peckybot_index import (  # noqa: E402
    FUNKCNI, ROLE_TAGY, _d_from, _d_to, _full_name, _lide_data, _party, clean_phone, clip,
    cz_date, meeting_ref,
)
from peckybot_sources import _load, _org_names, _vzorec_serie  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / 'peckybot' / 'data'
KALENDAR_OD = '2025-01-01'
MAX_BODY = 160
MAX_BYTES = 500_000


def dump(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(',', ':'))


def write_if_changed(path, obj):
    data = dump(obj)
    if len(data.encode('utf-8')) > MAX_BYTES:
        raise SystemExit(f'{path.name}: {len(data.encode("utf-8"))} B překračuje strop {MAX_BYTES} B')
    if path.exists() and path.read_text(encoding='utf-8') == data:
        return False
    path.write_text(data, encoding='utf-8')
    return True


def slug(text):
    t = unicodedata.normalize('NFD', text.lower())
    t = ''.join(c for c in t if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z0-9]+', '-', t).strip('-')


# ---------------------------------------------------------------- osoby

def build_osoby():
    people, orgs, aff = _lide_data()
    mine = defaultdict(list)
    for a in aff:
        mine[a['person_id']].append(a)
    out = []
    for p in people.values():
        funkce, videno = [], set()
        for a in mine.get(p['id'], []):
            if not a['current'] or a['role_type'] not in FUNKCNI:
                continue
            r = 'člen zastupitelstva' if a['role_type'] == 'zastupitel' else (
                'radní' if a['role_type'] == 'rada' else a['role'])
            if r not in videno:
                videno.add(r)
                funkce.append(r)
        if not funkce:
            funkce = [ROLE_TAGY[t] for t in p.get('tags', []) if t in ROLE_TAGY]
        strany = []
        for a in mine.get(p['id'], []):
            o = orgs.get(a['organization_id'], {})
            if o.get('type') == 'politicke' and o['name'] not in strany:
                strany.append(o['name'])
        bio = clip((p.get('bio') or '').strip(), 400)
        out.append({
            'id': p['id'], 'jmeno': _full_name(p), 'prijmeni': p.get('last_name') or '',
            'funkce': funkce[:8], 'uskupeni': '; '.join(strany),
            'tagy': list(p.get('tags') or []),
            'email': (p.get('email') or '').strip(),
            'telefon': clean_phone((p.get('phone') or '').strip()),
            'bio': bio,
        })
    out.sort(key=lambda o: o['id'])
    return {'v': 1, 'osoby': out}


# ---------------------------------------------------------------- složení

def _clen(pid, role, at, people, orgs, aff):
    return {'jmeno': _full_name(people[pid]), 'funkce': role, 'uskupeni': _party(pid, at, orgs, aff)}


def build_slozeni():
    people, orgs, aff = _lide_data()
    mp = [a for a in aff if a['organization_id'] == 'mesto-pecky']
    organy = []
    starts = sorted({a['from'] for a in mp if a['role_type'] == 'rada'})
    terms = [(_d_from(st), starts[i + 1] if i + 1 < len(starts) else None) for i, st in enumerate(starts)]
    order = {'starosta': 0, 'mistostarosta': 1, 'rada': 2}
    for st, end in reversed(terms):
        cur = end is None

        def covers(a, st=st):
            if not a['from'] and a['to'] is None:  # neznámé období (nedoložený začátek i konec)
                return False
            return _d_from(a['from']) <= st and (_d_to(a['to']) is None or _d_to(a['to']) > st)
        roles = [a for a in mp if a['role_type'] in order and covers(a)]
        roles.sort(key=lambda a: (order[a['role_type']], a['role']))
        seen, cl = set(), []
        for a in roles:
            if a['person_id'] in seen:
                continue
            seen.add(a['person_id'])
            cl.append(_clen(a['person_id'], a['role'] if a['role_type'] != 'rada' else 'radní', st,
                            people, orgs, aff))
        if not cl:
            continue
        od = cz_date(st) if len(st) > 4 else st
        od = od.replace('1. 1. ', '')
        if cur:
            organy.append({'id': 'rada-soucasna', 'nazev': 'Rada města', 'obdobi': f'od {od}',
                           'aktualni': True, 'pocet': len(cl), 'clenove': cl})
        else:
            do = cz_date(end) if len(end) > 4 else end
            organy.append({'id': f'rada-{st[:4]}-{end[:4]}', 'nazev': 'Rada města',
                           'obdobi': f'{od} – {do}', 'aktualni': False, 'pocet': len(cl), 'clenove': cl})
        if cur:
            zs = [a for a in mp if a['role_type'] == 'zastupitel' and a['current']]
            zc = [_clen(a['person_id'], 'zastupitel', st, people, orgs, aff)
                  for a in sorted(zs, key=lambda a: (people[a['person_id']]['last_name'], a['person_id']))]
            organy.append({'id': 'zastupitelstvo-soucasne', 'nazev': 'Zastupitelstvo města',
                           'obdobi': f'od {od}', 'aktualni': True, 'pocet': len(zc), 'clenove': zc})
    # výbory, komise, školské rady (aktuální členové)
    funkce = re.compile(r'^(člen|členka|předseda|předsedkyně|místopředseda|místopředsedkyně)\s+', re.I)
    groups = {}
    for a in aff:
        if a['role_type'] != 'komise' or not a['current']:
            continue
        m = funkce.match(a['role'])
        body = a['role'][m.end():] if m else a['role']
        fn = m.group(1).lower() if m else 'člen'
        groups.setdefault((a['organization_id'], body[0].lower() + body[1:]), []).append((fn, a['person_id'], a['from']))
    ids = set()
    for (oid, body), mem in sorted(groups.items()):
        if len(mem) < 2:
            continue
        mem.sort(key=lambda m: (m[0] in ('člen', 'členka'), people[m[1]]['last_name'], m[1]))
        org = orgs.get(oid, {}).get('name', '')
        kde = f' ({org})' if oid != 'mesto-pecky' and org else ''
        at = max(_d_from(m[2]) for m in mem)
        cl = [_clen(pid, fn, at, people, orgs, aff) for fn, pid, _ in mem]
        i = slug(f'{body} {oid}')
        while i in ids:
            i += '-2'
        ids.add(i)
        organy.append({'id': i, 'nazev': (body[0].upper() + body[1:]) + kde, 'obdobi': 'současné složení',
                       'aktualni': True, 'pocet': len(cl), 'clenove': cl})
    # starostové a místostarostové
    rows = sorted((a for a in mp if a['role_type'] in ('starosta', 'mistostarosta')),
                  key=lambda a: (_d_from(a['from']), a['role_type'], a['person_id']))
    cl = []
    for a in rows:
        cl.append({'jmeno': _full_name(people[a['person_id']]), 'funkce': a['role'], 'uskupeni': '',
                   'od': a['from'], 'do': a['to']})
    organy.append({'id': 'starostove', 'nazev': 'Starostové a místostarostové', 'obdobi': '1990–dosud',
                   'aktualni': False, 'pocet': len(cl), 'clenove': cl})
    return {'v': 1, 'organy': organy}


# ---------------------------------------------------------------- kalendář

def build_kalendar():
    events = _load('kalendar/udalosti.json')['events']
    org = _org_names()
    # jednání, která už jsou v jednani.json, se v kalendáři neopakují
    mtg = {(m['typ'], m['datum']) for m in build_jednani()['jednani']}
    ud, kurzy = [], defaultdict(list)
    for e in sorted(events, key=lambda x: (x['date'], x.get('time') or '', x['id'])):
        if e['date'] < KALENDAR_OD:
            continue
        cat = e['category']
        porad = e.get('organizer_name') or org.get(e.get('organizer')) or ''
        if cat == 'kurz':
            kurzy[(e['title'], porad)].append(e)
            continue
        if cat in ('rada', 'zastupitelstvo') and (cat, e['date']) in mtg:
            continue
        if cat == 'vybor' and any((t, e['date']) in mtg for t in ('vybor', 'skolska-rada', 'komise')):
            continue
        link = e.get('link') or ''
        ud.append({'datum': e['date'], 'datum_do': e.get('date_end') or None, 'cas': e.get('time') or '',
                   'nazev': e['title'], 'misto': e.get('place') or '', 'poradatel': porad, 'typ': cat,
                   'url': link})
    serie = []
    for (titul, porad), evs in sorted(kurzy.items()):
        e0 = evs[0]
        v = _vzorec_serie(evs)
        popis = ' '.join(x for x in (f'Pořádá {porad}.' if porad else '', f'Koná se {v}.' if v else '',
                                      f'Místo: {e0["place"]}.' if e0.get('place') else '') if x)
        serie.append({'nazev': titul, 'popis': popis, 'od': evs[0]['date'], 'do': evs[-1]['date']})
    return {'v': 1, 'udalosti': ud, 'serie': serie}


# ---------------------------------------------------------------- jednání

_ORGAN_VYBOR = {'Finanční výbor', 'Kontrolní výbor'}
_cache = {}

# dokumenty jednání (peckybot/data/jednani/<id>.json)
DOC_DIR = OUT_DIR / 'jednani'
MAX_ZPRAVA = 900
MAX_USNESENI = 500
MAX_DOC_BYTES = 25_000
MAX_STARE_TEXT = 3000
POZVANKA_POZNAMKA = ('K jednání je zveřejněna jen pozvánka s programem; zápis a usnesení zatím nevyšly. '
                     'Výsledky hlasování ani přijatá usnesení tedy nejsou k dispozici.')
BEZ_PROGRAMU_POZNAMKA = 'Program ani zápis k tomuto jednání zatím nejsou zveřejněné.'


def _hlasovani(r):
    cast = []
    for klic, popis in (('pro', 'pro'), ('proti', 'proti'), ('zdrzel', 'zdržel se')):
        if r.get(klic) is not None:
            cast.append(f'{popis} {r[klic]}')
    return ', '.join(cast)


def _usneseni(r, n_max=MAX_USNESENI):
    out = {'cislo': r.get('n') or '', 'text': clip(r.get('text'), n_max)}
    h = _hlasovani(r)
    if h:
        out['hlasovani'] = h
    if r.get('adopted') is False:
        out['neprijato'] = True
    if r.get('note'):
        out['poznamka'] = clip(r['note'], 200)
    return out


def _odkazy(links):
    links = links or {}
    o = {}
    for klic, zdroj in (('zapis', 'minutes'), ('usneseni', 'resolutions'), ('pozvanka', 'invitation'),
                        ('pdf', 'pdf')):
        if links.get(zdroj):
            o[klic] = links[zdroj]
    return o


def _doc_meeting(jid, oznaceni, m, typ):
    """Dokument jednání z položky pecky-jednani/komise/vybory/skolska-rada.json."""
    links = m.get('links') or {}
    agenda = m.get('agenda') or []
    res = m.get('resolutions') or []
    dostupne = []
    if links.get('invitation') and agenda:
        dostupne.append('pozvanka')
    if links.get('minutes'):
        dostupne.append('zapis')
    if res:
        dostupne.append('usneseni')
    body = []
    used = set()
    for a in agenda:
        b = {'n': a['n'], 'nazev': clip(a['t'], MAX_BODY)}
        if a.get('predkladatel'):
            b['predkladatel'] = a['predkladatel']
        if a.get('duvodova_zprava'):
            b['zprava'] = clip(a['duvodova_zprava'], MAX_ZPRAVA)
        us = []
        for i, r in enumerate(res):
            if i not in used and r.get('item') and r['item'] == a['t']:
                us.append(_usneseni(r))
                used.add(i)
        if us:
            b['usneseni'] = us
        body.append(b)
    doc = {'v': 1, 'id': jid, 'oznaceni': oznaceni, 'datum': m['date'], 'typ': typ}
    if m.get('time'):
        doc['cas'] = m['time']
    if m.get('venue'):
        doc['misto'] = m['venue']
    doc['odkazy'] = _odkazy(links)
    doc['dostupne'] = dostupne
    if dostupne == ['pozvanka']:
        doc['poznamka'] = POZVANKA_POZNAMKA
    elif not dostupne:
        doc['poznamka'] = BEZ_PROGRAMU_POZNAMKA
    doc['body'] = body
    zbyla = [_usneseni(r) for i, r in enumerate(res) if i not in used]
    if zbyla:
        doc['usneseni_ostatni'] = zbyla
    return doc


def _doc_size(doc):
    return len(dump(doc).encode('utf-8'))


def _fit_doc(doc):
    """Zkrátí nejdelší texty (zprávy, pak usnesení), dokud soubor nevejde do MAX_DOC_BYTES."""
    for pole, spodek in (('zprava', 150), ('text', 150)):
        while _doc_size(doc) > MAX_DOC_BYTES:
            polozky = []
            if pole == 'zprava':
                polozky = [b for b in doc['body'] if len(b.get('zprava', '')) > spodek]
                klic = 'zprava'
            else:
                polozky = [u for b in doc['body'] for u in b.get('usneseni', []) if len(u['text']) > spodek]
                polozky += [u for u in doc.get('usneseni_ostatni', []) if len(u['text']) > spodek]
                klic = 'text'
            if not polozky:
                break
            nejdelsi = max(polozky, key=lambda x: len(x[klic]))
            nejdelsi[klic] = clip(nejdelsi[klic], max(spodek, int(len(nejdelsi[klic]) * 0.7)))
    # poslední záchrana: odříznout zprávy úplně od konce
    for b in reversed(doc['body']):
        if _doc_size(doc) <= MAX_DOC_BYTES:
            break
        b.pop('zprava', None)
    if _doc_size(doc) > MAX_DOC_BYTES:
        raise SystemExit(f"jednani/{doc['id']}.json: {_doc_size(doc)} B překračuje strop {MAX_DOC_BYTES} B")
    return doc


def build_jednani():
    if 'j' in _cache:
        return _cache['j']
    out, docs = [], {}

    def add(entry, doc):
        entry['dostupne'] = doc['dostupne']
        out.append(entry)
        docs[entry['id']] = _fit_doc(doc)

    for m in _load('jednani/pecky-jednani.json')['meetings']:
        zm = m['type'] == 'Zastupitelstvo'
        short, _ = meeting_ref(m)
        jid = ('zastupitelstvo-' if zm else 'rada-') + m['date']
        typ = 'zastupitelstvo' if zm else 'rada'
        doc = _doc_meeting(jid, short, m, typ)
        add({'id': jid, 'typ': typ, 'organ': 'Zastupitelstvo města' if zm else 'Rada města',
             'oznaceni': short, 'datum': m['date'],
             'body': [clip(a['t'], MAX_BODY) for a in m.get('agenda', [])]}, doc)
    for m in _load('jednani/starsi-jednani.json')['meetings']:
        zm = m['type'] == 'Zastupitelstvo'
        jid = m.get('id') or (('zastupitelstvo-' if zm else 'rada-') + m['date'])
        typ = 'zastupitelstvo' if zm else 'rada'
        oznaceni = m['label'].split(' (')[0]
        druh = 'usneseni' if m.get('doc_kind') == 'usnesení' else 'zapis'
        doc = {'v': 1, 'id': jid, 'oznaceni': oznaceni, 'datum': m['date'], 'typ': typ,
               'odkazy': {druh: (m.get('links') or {}).get('minutes')} if (m.get('links') or {}).get('minutes') else {},
               'dostupne': [druh],
               'poznamka': 'Starší jednání z úřední desky: k dispozici je jen text dokumentu '
                           f'({m.get("doc_title") or druh}), bez rozdělení na body.',
               'body': []}
        text = clip(m.get('text'), MAX_STARE_TEXT)
        if text:
            doc['text_dokumentu'] = text
        add({'id': jid, 'typ': typ, 'organ': 'Zastupitelstvo města' if zm else 'Rada města',
             'oznaceni': oznaceni, 'datum': m['date'], 'body': []}, doc)
    for fn, typ in (('komise', 'komise'), ('vybory', 'vybor'), ('skolska-rada', 'skolska-rada')):
        for m in _load(f'jednani/{fn}.json')['meetings']:
            doc = _doc_meeting(m['id'], m['type'], m, typ)
            # u komisí a výborů je zápis jediný zdroj; pozvánka neexistuje
            add({'id': m['id'], 'typ': typ, 'organ': m['type'], 'oznaceni': m['type'],
                 'datum': m['date'],
                 'body': [clip(a['t'], MAX_BODY) for a in m.get('agenda', [])]}, doc)
    out.sort(key=lambda j: (j['datum'], j['typ'], j['id']))
    posledni = {}
    for j in out:
        posledni[j['typ']] = j['id']
    for j in out:
        if posledni[j['typ']] == j['id']:
            j['je_posledni'] = True
            docs[j['id']]['je_posledni'] = True
    _cache['j'] = {'v': 1, 'jednani': out}
    _cache['docs'] = docs
    return _cache['j']


def build_jednani_docs():
    build_jednani()
    return _cache['docs']


def write_jednani_docs():
    """Zapíše data/jednani/<id>.json, smaže zastaralé. Vrací (změněno, počet, celková velikost)."""
    docs = build_jednani_docs()
    DOC_DIR.mkdir(parents=True, exist_ok=True)
    zmeneno, total = False, 0
    for jid, doc in docs.items():
        if not re.fullmatch(r'[a-z0-9-]{3,80}', jid):
            raise SystemExit(f'Neplatné id jednání: {jid!r}')
        path = DOC_DIR / f'{jid}.json'
        data = dump(doc)
        total += len(data.encode('utf-8'))
        if not (path.exists() and path.read_text(encoding='utf-8') == data):
            path.write_text(data, encoding='utf-8')
            zmeneno = True
    for f in DOC_DIR.glob('*.json'):
        if f.stem not in docs:
            f.unlink()
            zmeneno = True
    return zmeneno, len(docs), total


# ---------------------------------------------------------------- statistiky

def build_statistiky():
    ab = []
    for ob in _load('jednani/absence.json')['obdobi']:
        cl = [{'jmeno': r['jmeno'], 'mandatu': r['mandat'], 'absence_podil': r['podil']}
              for r in sorted(ob['radky'], key=lambda r: (-r['podil'], r['jmeno'])) if r['mandat'] >= 3]
        if cl:
            ab.append({'organ': ob['organ'], 'obdobi': ob['obdobi'], 'clenove': cl})
    c = defaultdict(Counter)
    for j in build_jednani()['jednani']:
        c[j['typ']][j['datum'][:4]] += 1
    pocty = {t: dict(sorted(c[t].items())) for t in sorted(c)}
    return {'v': 1, 'absence': ab, 'pocty': {'jednani_podle_typu_a_roku': pocty}}


# ---------------------------------------------------------------- úřední deska

UD_DIR = ROOT / 'o-webu' / 'uredni-deska-monitoring'
UD_OUT = OUT_DIR / 'uredni-deska'
_UD_DATE = re.compile(r'^(\d{2})\.(\d{2})\.(\d{4})$')


def _ud_iso(v):
    m = _UD_DATE.match(v.strip())
    return f'{m.group(3)}-{m.group(2)}-{m.group(1)}' if m else ''


def build_uredni_deska():
    """rok → {v, rok, d:[[vyvěšeno, sejmuto, typ, název, id]]}; id = jen číslo, je-li zbytek
    odvoditelný z názvu (slug), jinak celé id_slug; as4u:<id> beze změny."""
    out = {}
    for f in sorted(UD_DIR.glob('20??.txt')):
        rows = []
        for line in f.read_text(encoding='utf-8').splitlines():
            if not line.strip() or line.startswith('#'):
                continue
            r = line.split('|')
            if len(r) != 5:
                continue
            rid, od, do, typ, nazev = (x.strip() for x in r)
            num, _, sl = rid.partition('_')
            if not rid.startswith('as4u:') and sl == slug(nazev) and len(nazev) <= 200:
                rid = num
            rows.append([_ud_iso(od), _ud_iso(do), '' if typ == '-----' else typ, clip(nazev, 200), rid])
        rows.sort(key=lambda x: (x[0], x[4]), reverse=True)
        out[f.stem] = {'v': 1, 'rok': int(f.stem), 'd': rows}
    return out


def write_uredni_deska():
    docs = build_uredni_deska()
    UD_OUT.mkdir(parents=True, exist_ok=True)
    zmeneno, total = False, 0
    for rok, doc in docs.items():
        data = dump(doc)
        total += len(data.encode('utf-8'))
        path = UD_OUT / f'{rok}.json'
        if not (path.exists() and path.read_text(encoding='utf-8') == data):
            path.write_text(data, encoding='utf-8')
            zmeneno = True
    for f in UD_OUT.glob('*.json'):
        if f.stem not in docs:
            f.unlink()
            zmeneno = True
    return zmeneno, len(docs), total


SCHEMA_NOTE = 'peckybot/data/SCHEMA.md'


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    soubory = (('osoby.json', build_osoby()), ('slozeni.json', build_slozeni()),
               ('kalendar.json', build_kalendar()), ('jednani.json', build_jednani()),
               ('statistiky.json', build_statistiky()))
    zmeneno, popis = False, []
    zm_doc, pocet, velikost = write_jednani_docs()
    zmeneno |= zm_doc
    zm_ud, n_ud, vel_ud = write_uredni_deska()
    zmeneno |= zm_ud
    popis.append(f'uredni-deska/*.json {n_ud} souborů, {vel_ud / 1024:.0f} kB')
    popis.append(f'jednani/*.json {pocet} souborů, {velikost / 1024 / 1024:.1f} MB')
    for name, obj in soubory:
        zmeneno |= write_if_changed(OUT_DIR / name, obj)
        popis.append(f'{name} {(OUT_DIR / name).stat().st_size / 1024:.0f} kB')
    print(f'PečkyBot nástroje: {", ".join(popis)} ({"přepsáno" if zmeneno else "beze změny"})')


if __name__ == '__main__':
    main()
