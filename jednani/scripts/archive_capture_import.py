#!/usr/bin/env python3
"""Z dávky souborů stažených skriptem `archive-capture.js` (Chrome → ~/Downloads) sestaví
záznamy jednání v `jednani/archive/` ve stejném tvaru jako u původního exportu.

Použití:
  python3 jednani/scripts/archive_capture_import.py [složka_se_staženými_soubory]   # výchozí ~/Downloads

Čte `archive-capture-<uuid8>.json` (jedno jednání) a `archive-capture-listing.json`
(řádky výpisu s odkazy, label a typ jednání). Zapíše `archive/<datum>-<typ>-<uuid8>.json`,
doplní `archive/index.json` (nahoře, sestupně podle data) a do `index.json → supplements`
poznamená, co a kdy přibylo. Už existující soubor se přepíše jen s `--force`.
Zápis se parsuje přes `archive_parse.py` (otestovaný proti zápisům 2025–2026 z původního exportu).
"""
import glob
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from archive_parse import UR, _list, parse_minutes  # noqa: E402

ARCH = Path(__file__).resolve().parent.parent / 'archive'
ORIGIN = 'https://mesto-pecky.usneseni.cz'
LINK_KEYS = {'Pozvánka': 'invitation', 'zápis': 'minutes', 'podepsaný zápis': 'signed_minutes_pdf',
             'přijatá usnesení': 'resolutions', 'Zvukový záznam': 'audio'}


def date_iso(raw):
    m = re.search(r'(\d+)\. (\d+)\. (\d{4})', raw or '')
    return f'{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}' if m else None


def parse_vote_cell(raw):
    flat = re.sub(r'\s+', ' ', raw or '').strip()
    v = {'raw_text': flat}
    for key, label, nxt in (('pro', r'pro:', r'(?=\s*proti)'), ('proti', r'proti:?', r'(?=\s*zdržel se)'), ('zdrzel_se', r'zdržel se:?', r'(?=\s*nehlasoval|\s*$)')):
        m = re.search(label + r'\s*(\(\d+\).*?|\d+)' + nxt, flat)
        if not m:
            v[key] = {'count': None, 'names': None, 'raw': ''}
        elif m.group(1).startswith('('):
            v[key] = _list(m.group(1))
        else:
            v[key] = {'count': int(m.group(1)), 'names': None, 'raw': m.group(1)}
    return v


def build_item(it, fetched_at):
    cells = it['cells']
    cell = cells[1]
    ag = re.search(r'Bod programu:\s*(.*?)\s*\n\s*\n?\s*Text přijatého usnesení:', cell, re.S)
    tx = re.search(r'Text přijatého usnesení:\s*(.*)$', cell, re.S)
    fields = {}
    for row in it.get('detail_fields') or []:
        if len(row) == 2:
            fields[row[0]] = row[1]
    det = None
    if fields:
        pr = fields.get('Přijato', '')
        ul = fields.get('Ukončeno', '')
        lab = re.search(r'jednání č\. (\d+/\d{4})', pr)
        det = {
            'number_raw': fields.get('Číslo usnesení'),
            'text_verbatim': fields.get('Text usnesení'),
            'typ_raw': fields.get('Typ usnesení'),
            'zodpovida_raw': fields.get('Zodpovídá', ''),
            'prijato_raw': pr, 'prijato_date_iso': date_iso(pr),
            'prijato_meeting_label': lab.group(1) if lab else None,
            'termin_raw': fields.get('Termín', ''),
            'ukonceno_raw': ul, 'ukonceno_date_iso': date_iso(ul),
            'fields_raw': fields,
        }
    mod = it.get('detail_mod') or ''
    return {
        'number_raw': cells[0], 'detail_id': it.get('detail_id'),
        'detail_url': f"{ORIGIN}/verejne/usneseni/{it['detail_id']}{mod}" if it.get('detail_id') else None,
        'agenda_item_raw': ag.group(1) if ag else None,
        'text_verbatim': tx.group(1).strip() if tx else None,
        'cell_text_raw': cell,
        'date_raw': cells[2], 'date_iso': date_iso(cells[2]),
        'responsible_raw': cells[3], 'deadline_raw': cells[4],
        'vote': parse_vote_cell(cells[5]),
        'detail': det,
    }


def listing_info(listing, uuid):
    for row in (listing or {}).get('rows', []):
        if any(uuid in (a.get('href') or '') for a in row['links']):
            return row
    return None


def build_meeting(cap, listing):
    uuid = cap['uuid']
    fetched = cap['captured_at']
    mi = parse_minutes(cap['minutes']['text'], cap['minutes']['url'], fetched) if cap.get('minutes') else None
    row = listing_info(listing, uuid)
    links = {k: None for k in ('invitation', 'minutes', 'signed_minutes_pdf', 'resolutions', 'audio')}
    link_texts = {}
    label = None
    btype = None
    if row:
        for a in row['links']:
            k = LINK_KEYS.get(a['text'])
            if k:
                links[k] = a['href'] if a['href'].startswith('http') else ORIGIN + a['href']
                link_texts[k] = a['text']
        btype = row['cells'][0]
        label = row['cells'][1]
    else:
        links['minutes'] = f'{ORIGIN}/verejne/{uuid}/zapis/'
        links['resolutions'] = f'{ORIGIN}/verejne/{uuid}/usneseni/'
        links['invitation'] = f'{ORIGIN}/verejne/?uuid={uuid}&do=printPublicInvitation'
    if not (btype and label) and mi:
        t = mi['title_raw'] or ''
        btype = 'Rada' if 'rady' in t else 'Zastupitelstvo'
        n = re.search(r'č\. (\d+/\d{4})', t)
        label = f"{n.group(1)} ({mi['date_raw']})" if n else None
    m = re.search(r'(\d+)/(\d{4}) \((.*)\)', label or '')
    inv = cap.get('invitation') or {}
    rec = {
        'uuid': uuid, 'body_type_raw': btype, 'label_raw': label,
        'number': int(m.group(1)) if m else None, 'year': int(m.group(2)) if m else None,
        'date_iso': date_iso(m.group(3)) if m else (mi or {}).get('date_iso'),
        'links': links, 'link_texts': link_texts, 'status': 'ok',
        'invitation': {'status': inv.get('status', 'missing_on_site'), 'url': links['invitation'], 'fetched_at': fetched,
                       'pages': inv.get('pages'), 'full_text': inv.get('text')},
        'minutes': mi if mi else {'status': 'missing_on_site', 'url': links['minutes'], 'fetched_at': fetched},
        'resolutions': {'status': 'ok', 'url': cap['resolutions']['url'], 'fetched_at': fetched,
                        'items': [build_item(i, fetched) for i in cap['resolutions']['items']]},
    }
    return rec


def typ_slug(rec):
    raw = (rec['body_type_raw'] or '').lower()
    return 'zastupitelstvo' if 'zastup' in raw else 'rada' if 'rada' in raw else 'jine'


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    force = '--force' in sys.argv
    src = Path(args[0]).expanduser() if args else Path.home() / 'Downloads'
    lp = src / 'archive-capture-listing.json'
    listing = json.load(open(lp, encoding='utf-8')) if lp.exists() else None
    if not listing:
        print('POZOR: chybí archive-capture-listing.json — label a odkazy se dopočítají jen ze zápisu')
    idx = json.load(open(ARCH / 'index.json', encoding='utf-8'))
    done = []
    for f in sorted(glob.glob(str(src / 'archive-capture-*.json'))):
        if f.endswith('listing.json'):
            continue
        cap = json.load(open(f, encoding='utf-8'))
        rec = build_meeting(cap, listing)
        name = f"{rec['date_iso']}-{typ_slug(rec)}-{rec['uuid'][:8]}.json"
        out = ARCH / name
        if out.exists() and not force:
            print('přeskočeno (už existuje):', name)
            continue
        out.write_text(json.dumps(rec, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
        entry = {'file': name, 'uuid': rec['uuid'], 'date': rec['date_iso'], 'type': typ_slug(rec)}
        idx['meetings'] = [e for e in idx['meetings'] if e['uuid'] != rec['uuid']]
        idx['meetings'].append(entry)
        done.append(name)
        mi = rec['minutes']
        print(f"{name}: body {len(mi.get('agenda_items', []))}, usnesení {len(rec['resolutions']['items'])}, "
              f"pozvánka {rec['invitation']['status']}")
    if done:
        idx['meetings'].sort(key=lambda e: e['date'], reverse=True)
        idx.setdefault('supplements', []).append({
            'added_at': datetime.now(timezone.utc).isoformat(timespec='seconds'),
            'tool': 'archive-capture.js + archive_capture_import.py',
            'meetings': done})
        (ARCH / 'index.json').write_text(json.dumps(idx, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(f'přidáno {len(done)} jednání')


if __name__ == '__main__':
    main()
