#!/usr/bin/env python3
"""Parser textu zápisu z usneseni.cz do struktury `minutes` velkého archivu (`jednani/archive/`).

Vstup je text elementu #report (innerText z prohlížeče, tabulátory nahrazené novými řádky).
Vystup má stejný tvar jako u starších jednání z původního scraperu (viz README.md → Struktura
archivu). Správnost parseru hlídá `python3 jednani/scripts/archive_parse.py --test`, který
ho spustí nad `minutes.full_text` všech jednání v archivu a porovná výsledek s uloženým.
"""
import json
import re
import sys
from pathlib import Path

UR = re.compile(r'U[RZ]-\d+-\d+/\d+')
HEAD = re.compile(r'^(\d+)\. (.+?) \(bod číslo (\d+)\)$')


def norm(text):
    return text.replace('\t', '\n')


def _list(raw):
    """'(6) A, B, C' -> {'count': 6, 'names': [...], 'raw': '(6) A, B, C'}"""
    raw = raw.strip()
    m = re.match(r'^\((\d+)\)\s*(.*)$', raw, re.S)
    if not m:
        return {'count': None, 'names': None, 'raw': raw}
    names = [x.strip() for x in re.split(r',\s*(?=[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ])', m.group(2)) if x.strip()] if m.group(2).strip() else []
    return {'count': int(m.group(1)), 'names': names, 'raw': raw}


def parse_presence(text):
    """Úvodní prezence — od 'Úvodní prezence:' po řádek 'Jednání zahájeno …' (včetně)."""
    m = re.search(r'Úvodní prezence:.*?Jednání zahájeno[^\n]*', text, re.S)
    if not m:
        return None, None
    block = m.group(0)
    p = {'raw_text': block}

    def grp(label, nxt):
        mm = re.search(label + r'\s*\n?(\(\d+\)[^\n]*)', block)
        return _list(mm.group(1)) if mm else None
    p['pritomni'] = grp('Přítomni:', None)
    p['omluveni'] = grp('Omluveni:', None)
    p['nepritomni'] = grp('Nepřítomni:', None)
    pr = re.search(r'Předsedající:\s*\n?([^\n]+)', block)
    p['predsedajici'] = pr.group(1).strip() if pr else None
    q = re.search(r'(Přítomno je[^\n]*)', block)
    p['quorum_raw'] = q.group(1).strip() if q else None
    return p, block


VOTE = re.compile(r'Hlasování\n(pro:.*?nehlasoval:\n?[^\n]*)\n([^\n]*)', re.S)


def _vote_block(m):
    """Hlasování (match VOTE) -> vote dict."""
    raw, result = m.group(1), m.group(2).strip()
    v = {'raw_text': raw}
    flat = raw.replace('\n', ' ')
    for key, label in (('pro', 'pro:'), ('proti', 'proti:?'), ('zdrzel_se', 'zdržel se:'), ('nehlasoval', 'nehlasoval:')):
        mm = re.search(label + r'\s*(\(\d+\)[^\n]*?|\d+)(?=\s*(?:proti|zdržel se|nehlasoval)|\s*$)', flat)
        if not mm:
            v[key] = {'count': None, 'names': None, 'raw': ''}
            continue
        val = mm.group(1).strip()
        if val.startswith('('):
            v[key] = _list(val)
        else:
            v[key] = {'count': int(val), 'names': None, 'raw': val}
    v['result_raw'] = result
    n = UR.search(result)
    v['adopted_resolution_number'] = n.group(0) if n else None
    return v


def _find_heads(lines):
    """Nadpis bodu může být zalomený do víc řádků ('17. Název …\n(bod číslo 17)')."""
    heads = []
    i = 0
    while i < len(lines):
        if re.match(r'^\d+\. ', lines[i].strip()):
            for span in range(1, 5):
                if i + span > len(lines):
                    break
                if span > 1 and re.match(r'^(\d+\. |Projednávání|Předkladatel)', lines[i + span - 1].strip()):
                    break
                joined = ' '.join(x.strip() for x in lines[i:i + span])
                m = HEAD.match(joined)
                if m:
                    heads.append((i, span, joined, m))
                    i += span - 1
                    break
        i += 1
    return heads


def parse_agenda(text):
    lines = text.split('\n')
    heads = _find_heads(lines)
    items = []
    for k, (i, span, joined, m) in enumerate(heads):
        end = heads[k + 1][0] if k + 1 < len(heads) else len(lines)
        body = '\n'.join(lines[i + span:end]).strip('\n')
        pk = re.search(r'Předkladatel:\s*\n?([^\n]*)', body)
        votes = [_vote_block(vm) for vm in VOTE.finditer(body)]
        items.append({
            'number': int(m.group(3)),
            'title_raw': m.group(2),
            'heading_raw': joined,
            'predkladatel': pk.group(1).strip() if pk else None,
            'votes': votes,
            'resolution_numbers_mentioned': sorted(set(UR.findall(body))),
            'raw_text': body,
        })
    return items


def parse_minutes(text, url=None, fetched_at=None):
    t = norm(text)
    title = re.search(r'ZÁPIS[^\n]*\n[^\n]*\ndatum:[^\n]*', t)
    dm = re.search(r'datum:\s*(\d+)\. (\d+)\. (\d{4})(?:, čas:\s*([\d:]+))?', t)
    pres, block = parse_presence(t)
    return {
        'status': 'ok', 'url': url, 'fetched_at': fetched_at,
        'title_raw': re.sub(r'\s+', ' ', title.group(0)).strip() if title else None,
        'date_raw': f'{int(dm.group(1))}. {int(dm.group(2))}. {dm.group(3)}' if dm else None,
        'date_iso': f'{dm.group(3)}-{int(dm.group(2)):02d}-{int(dm.group(1)):02d}' if dm else None,
        'time_raw': dm.group(4) if dm and dm.group(4) else None,
        'presence': pres,
        'header_raw': block,
        'agenda_items': parse_agenda(t),
        'full_text': t,
    }


def _test(od='2025-07'):
    """Porovná parser s uloženými záznamy od `od` (novější šablona zápisu). Starší zápisy 2021–2024
    mají jinou šablonu (bez řádku Předkladatel apod.) a parser na ně není stavěný. Rozdíly jen
    v nezlomitelných/neviditelných znacích (anonymizační bloky) se ignorují; hlasování, kde starý
    scraper chybně spojil text bodu s hlasováním (slovo „pro“ v textu), je známá chyba původních dat."""
    arch = Path(__file__).resolve().parent.parent / 'archive'
    z = lambda x: x.replace('\u200b', '') if isinstance(x, str) else x
    bad = {'presence': 0, 'agenda': 0, 'votes': 0, 'mentioned': 0, 'text': 0}
    n = 0
    for f in sorted(arch.glob('20*.json')):
        if f.name[:7] < od:
            continue
        a = json.load(open(f, encoding='utf-8'))
        m = a.get('minutes') or {}
        if not m.get('full_text'):
            continue
        n += 1
        p = parse_minutes(m['full_text'])
        if (p['presence'] or {}).get('pritomni') != (m.get('presence') or {}).get('pritomni'):
            bad['presence'] += 1
        old, new = m['agenda_items'], p['agenda_items']
        if [x['number'] for x in old] != [x['number'] for x in new]:
            bad['agenda'] += 1
            continue
        for o, w in zip(old, new):
            bad['votes'] += o['votes'] != w['votes']
            bad['mentioned'] += o['resolution_numbers_mentioned'] != w['resolution_numbers_mentioned']
            bad['text'] += (z(o['raw_text']), o['title_raw'], o['predkladatel']) != (z(w['raw_text']), w['title_raw'], w['predkladatel'])
    print(f'otestováno {n} jednání od {od}; neshody: {bad}')


if __name__ == '__main__':
    if '--test' in sys.argv:
        _test()
