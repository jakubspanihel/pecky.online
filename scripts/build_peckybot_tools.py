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


def build_jednani():
    if 'j' in _cache:
        return _cache['j']
    out = []
    for m in _load('jednani/pecky-jednani.json')['meetings']:
        zm = m['type'] == 'Zastupitelstvo'
        short, _ = meeting_ref(m)
        out.append({'id': ('zastupitelstvo-' if zm else 'rada-') + m['date'],
                    'typ': 'zastupitelstvo' if zm else 'rada',
                    'organ': 'Zastupitelstvo města' if zm else 'Rada města',
                    'oznaceni': short, 'datum': m['date'],
                    'body': [clip(a['t'], MAX_BODY) for a in m.get('agenda', [])]})
    for m in _load('jednani/starsi-jednani.json')['meetings']:
        zm = m['type'] == 'Zastupitelstvo'
        out.append({'id': m.get('id') or (('zastupitelstvo-' if zm else 'rada-') + m['date']),
                    'typ': 'zastupitelstvo' if zm else 'rada',
                    'organ': 'Zastupitelstvo města' if zm else 'Rada města',
                    'oznaceni': m['label'].split(' (')[0], 'datum': m['date'], 'body': []})
    for fn, typ in (('komise', 'komise'), ('vybory', 'vybor'), ('skolska-rada', 'skolska-rada')):
        for m in _load(f'jednani/{fn}.json')['meetings']:
            out.append({'id': m['id'], 'typ': typ, 'organ': m['type'], 'oznaceni': m['type'],
                        'datum': m['date'],
                        'body': [clip(a['t'], MAX_BODY) for a in m.get('agenda', [])]})
    out.sort(key=lambda j: (j['datum'], j['typ'], j['id']))
    _cache['j'] = {'v': 1, 'jednani': out}
    return _cache['j']


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


SCHEMA_NOTE = 'peckybot/data/SCHEMA.md'


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    soubory = (('osoby.json', build_osoby()), ('slozeni.json', build_slozeni()),
               ('kalendar.json', build_kalendar()), ('jednani.json', build_jednani()),
               ('statistiky.json', build_statistiky()))
    zmeneno, popis = False, []
    for name, obj in soubory:
        zmeneno |= write_if_changed(OUT_DIR / name, obj)
        popis.append(f'{name} {(OUT_DIR / name).stat().st_size / 1024:.0f} kB')
    print(f'PečkyBot nástroje: {", ".join(popis)} ({"přepsáno" if zmeneno else "beze změny"})')


if __name__ == '__main__':
    main()
