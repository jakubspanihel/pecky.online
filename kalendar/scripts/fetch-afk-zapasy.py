#!/usr/bin/env python3
"""
Stáhne rozpis zápasů všech týmů fotbalového klubu AFK Pečky z afkpecky.cz
a uloží ho do kalendar/afk-zapasy.json (zdroj pro Kalendář, viz
kalendar/README.md -> "Zápasy AFK Pečky").

Web klubu běží na platformě webyprokluby.cz; každý tým má stránku
/<tým>/zapasy/ s tabulkou utkání aktuální sezóny (datum, čas výkopu,
domácí, hosté, skóre nebo "--:--") a ke každému zápasu modální okno
"Utkání se hraje na hřišti: ...". Export iCal web nemá - stránky
/<tým>/kalendar/ jen v prohlížeči překreslují stejnou tabulku.

Ukládá VŠECHNY zápasy (doma i venku) s příznakem `home` - výběr jen
domácích dělá až kalendar/scripts/update-kalendar.py (build_afk_events),
ať jde rozsah změnit bez nového stahování.

Odehrané zápasy z minulého souboru, které na webu už nejsou (typicky po
přepnutí webu na novou sezónu v létě), se ponechávají - kalendář o historii
nepřijde. Nadcházející zápas, který z webu zmizí, se nepřenáší (zrušení),
jen se vypíše.

Skript zastaví zápis, když se u některého týmu nenašel ani jeden zápas
(změna HTML, výpadek webu) - po ručním ověření na webu klubu jde přebít
přepínačem --force.

Na konci vypíše změny oproti minulému souboru (nové zápasy, přeložené
termíny, zmizelé nadcházející zápasy, nově zapsané výsledky) - podklad
pro výpis změn týdenní kontroly (kalendar/README.md -> "Pracovní postup:
týdenní kontrola").

Použití:
    python3 kalendar/scripts/fetch-afk-zapasy.py [--force]
    python3 kalendar/scripts/update-kalendar.py
"""
import html
import json
import re
import sys
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / 'kalendar' / 'afk-zapasy.json'
BASE = 'https://www.afkpecky.cz'
PRAGUE = ZoneInfo('Europe/Prague')

# slug na webu klubu -> zobrazovaný název týmu (pořadí = pořadí v menu webu)
TEAMS = {
    'a-tym': 'A tým',
    'b-tym': 'B tým',
    'starsi-dorost': 'Starší dorost',
    'starsi-zaci': 'Starší žáci',
    'mladsi-zaci': 'Mladší žáci',
    'starsi-pripravka': 'Starší přípravka',
    'mladsi-pripravka': 'Mladší přípravka',
}

ROW_RE = re.compile(r'<tr>(.*?)</tr>', re.S)
TD_RE = re.compile(r'<td([^>]*)>(.*?)</td>', re.S)
VENUE_RE = re.compile(r'Utkání se hraje na hřišti:\s*([^<]*?)\s*<')


def text(fragment):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', fragment))).strip()


def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (pecky.online kalendar)'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode('utf-8')


def parse_team(slug, page):
    # <h1>A tým <span>|</span> Zápasy   Muži 7. liga skupina C</h1>
    league_m = re.search(r'Zápasy\s+([^<]+?)\s*</h1>', page)
    league = text(league_m.group(1)) if league_m else None
    # modální okna "Info o hřišti" po jednom - okno bez údaje o hřišti nesmí
    # převzít hřiště z následujícího okna
    venues = {}
    for block in page.split('<div class="modal fade" id="ModalInfoHriste')[1:]:
        v = VENUE_RE.search(block.split('<div class="modal fade"')[0])
        if v:
            venues[block.split('"')[0]] = text(v.group(1))

    matches = []
    # jen tabulky utkání (nadpis <p> nad tabulkou = typ soutěže, typicky
    # "Mistrovská utkání"); tabulky "vzájemných zápasů" v modálech mají
    # jinou třídu (table-bordered) a přeskakují se
    for label, table in re.findall(
            r'<p[^>]*>\s*([^<]+?)\s*</p>\s*<table class="table text-center align-middle">(.*?)</table>',
            page, re.S):
        for row in ROW_RE.findall(table):
            tds = TD_RE.findall(row)
            if len(tds) < 6:
                continue
            date_s, time_s = text(tds[0][1]), text(tds[1][1])
            if not re.fullmatch(r'\d\d\.\d\d\.\d{4}', date_s):
                continue
            home_attrs, home_name = tds[3]
            away_name = tds[4][1]
            score = text(tds[5][1])
            modal = re.search(r"ModalInfoHriste(\w+)", home_attrs)
            date_iso = datetime.strptime(date_s, '%d.%m.%Y').strftime('%Y-%m-%d')
            matches.append({
                # číslo modálu je id zápasu v systému klubu - zůstává stejné i po
                # přeložení termínu, takže UID v .ics se při změně data nemění
                'id': f'afk-{slug}-{modal.group(1)}' if modal else f'afk-{slug}-{date_iso}',
                'competition': label,
                'date': date_iso,
                'time': time_s if re.fullmatch(r'\d\d:\d\d', time_s) else None,
                # AFK Pečky je domácí podle pořadí týmů (první buňka). Třída
                # "hometeam" se na to použít nedá - u B týmu ("AFK Pečky B") chybí.
                'home': text(home_name).startswith('AFK Pečky'),
                'home_team': text(home_name),
                'away_team': text(away_name),
                # "--:--" = nehráno, ":" = odehráno bez zapsaného výsledku
                'score': score if re.fullmatch(r'\d+:\d+', score) else None,
                'venue': venues.get(modal.group(1)) if modal else None,
            })
            m = matches[-1]
            # Hraje se v Pečkách? Rozhoduje hřiště, ne pořadí týmů - domácí
            # soupeř občas hraje na hřišti AFK (15. 9. 2026 Tuklaty : AFK
            # Pečky, mladší přípravka, "Barákova ul., Pečky"). Bez údaje
            # o hřišti se bere pořadí týmů.
            m['in_pecky'] = bool(re.search(r'Pečk', m['venue'])) if m['venue'] else m['home']
    # pojistka pro fallback id podle data (dva zápasy v jeden den)
    seen = {}
    for m in matches:
        n = seen.get(m['id'], 0) + 1
        seen[m['id']] = n
        if n > 1:
            m['id'] += f'-{n}'
    return league, matches


def main():
    force = '--force' in sys.argv
    today = datetime.now(PRAGUE).strftime('%Y-%m-%d')
    old = {}
    if OUT_JSON.exists():
        for t in json.loads(OUT_JSON.read_text(encoding='utf-8'))['teams']:
            old[t['slug']] = t['matches']

    teams, problems, changes = [], [], []
    for slug, name in TEAMS.items():
        url = f'{BASE}/{slug}/zapasy/'
        league, matches = parse_team(slug, fetch(url))
        if not matches:
            problems.append(f'{name}: žádný zápas nenalezen ({url})')
        prev = {m['id']: m for m in old.get(slug, [])}
        ids = {m['id'] for m in matches}
        for m in matches:
            p = prev.get(m['id'])
            popis = f'{name} {m["home_team"]} – {m["away_team"]}'
            if not p:
                changes.append(f'nový: {popis}, {m["date"]} {m["time"] or ""}')
            elif (p['date'], p['time']) != (m['date'], m['time']):
                changes.append(f'přeloženo: {popis}, {p["date"]} {p["time"] or ""} -> {m["date"]} {m["time"] or ""}')
            elif m['score'] and not p['score']:
                changes.append(f'výsledek: {popis} {m["score"]}')
        for mid, p in prev.items():
            if mid in ids:
                continue
            if p['date'] < today:
                matches.append(p)  # odehraný zápas z minulé sezóny - ponechat
            else:
                changes.append(f'ZMIZEL z webu (nepřenášen): {name} {p["home_team"]} – '
                               f'{p["away_team"]}, {p["date"]} {p["time"] or ""}')
        matches.sort(key=lambda m: (m['date'], m['time'] or ''))
        teams.append({'slug': slug, 'name': name, 'league': league, 'url': url,
                      'matches': matches})

    if problems and not force:
        print('ZASTAVENO, soubor nepřepsán — ověř ručně na webu klubu, pak případně --force:')
        for p in problems:
            print('  - ' + p)
        sys.exit(1)

    OUT_JSON.write_text(json.dumps({
        'meta': {
            'description': ('Rozpis zápasů všech týmů AFK Pečky z afkpecky.cz/<tým>/zapasy/ '
                            '(doma i venku; odehrané zápasy minulých sezón se ponechávají). '
                            'Generuje kalendar/scripts/fetch-afk-zapasy.py, do Kalendáře promítá '
                            'kalendar/scripts/update-kalendar.py (jen zápasy hrané v Pečkách). '
                            'Needitovat ručně — přepíše ho příští běh.'),
            'source': 'web-afkpecky-cz',
            'retrieved': today,
        },
        'teams': teams,
    }, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')

    total = sum(len(t['matches']) for t in teams)
    in_pecky = sum(1 for t in teams for m in t['matches'] if m['in_pecky'])
    print(f'Uloženo {total} zápasů ({in_pecky} v Pečkách) -> {OUT_JSON.relative_to(ROOT)}')
    for t in teams:
        h = sum(1 for m in t['matches'] if m['in_pecky'])
        print(f'  {t["name"]}: {len(t["matches"])} zápasů, {h} v Pečkách — {t["league"]}')
    if not old:
        print('Změny: první běh, není s čím srovnávat.')
    elif changes:
        print(f'Změny oproti minulému běhu ({len(changes)}):')
        for c in changes:
            print('  - ' + c)
    else:
        print('Změny oproti minulému běhu: žádné.')
    for p in problems:
        print('  VAROVÁNÍ (přebito --force): ' + p)


if __name__ == '__main__':
    main()
