#!/usr/bin/env python3
"""
Aktualizace dat sekce Kalendář (panel-kalendar v content/kalendar.html).

Sesbírá události ze všech zdrojů do jednoho společného schématu a zapíše:
- kalendar/udalosti.json — data pro klientské vykreslení mřížky (fetch()
  v content/kalendar.html)
- kalendar/kalendar.ics  — stejné události ve formátu iCalendar (RFC 5545),
  ke stažení/přihlášení (webcal) v Google/Apple/Outlook kalendáři

Zdroje (zatím jen A, další se dopisují jako další build_*_events() funkce
a přidají do seznamu v main()):
A) Jednání rady a zastupitelstva — z jednani/pecky-jednani.json (stejný
   zdroj jako sekce Jednání a jednani/scripts/update-pozemky.py).
B) (budoucí) Volby — zatím nikde strukturovaně, ruční záznam.
C) (budoucí) Kalendář akcí na webu města — vyžaduje vlastní scraper.

Spouštět po každé aktualizaci jednani/pecky-jednani.json (stejně jako
jednani/scripts/update-pozemky.py). Po běhu tohoto skriptu je potřeba
i scripts/build.py, aby se případná změna `content/kalendar.html`
promítla do veřejné stránky (samotná data v kalendar/udalosti.json
a kalendar/kalendar.ics build.py nekopíruje ani neupravuje, jen je
scripts/serve.py / GitHub Pages servíruje přímo ze složky kalendar/).

Použití:
    python3 kalendar/scripts/update-kalendar.py
"""
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.build import SITE_DOMAIN  # noqa: E402 - zdroj pravdy pro absolutní URL v .ics
# POZOR: SITE_DOMAIN už v sobě nese GitHub Pages subcestu
# (https://jakubspanihel.github.io/pecky.online), SITE_BASE_PATH se sem
# navíc nepřidává - to je jen pro přepis href/src/fetch() uvnitř HTML
# (scripts/build.py -> apply_base_path), na absolutní URL se nepoužívá.

JEDNANI_JSON = ROOT / 'jednani' / 'pecky-jednani.json'
OUT_JSON = ROOT / 'kalendar' / 'udalosti.json'
OUT_ICS = ROOT / 'kalendar' / 'kalendar.ics'

PRAGUE = ZoneInfo('Europe/Prague')


def build_jednani_events():
    """Rada + Zastupitelstvo z jednani/pecky-jednani.json -> společné schéma.

    Řadové jednání nemá v datech přesný čas (jen datum) - je to konání,
    které web dosud nezapsal jako 'time'; ten se u záznamu objevuje jen
    dokud je dostupná pouze Pozvánka (viz jednani/README.md). Takové
    jednání jde do kalendáře jako 'all_day'; jakmile scraper doplní zápis,
    'time' zmizí a další běh tohohle skriptu ho zpětně převede na celodenní
    - to je v pořádku, přesný čas zahájení web jinak nedrží.
    """
    data = json.loads(JEDNANI_JSON.read_text(encoding='utf-8'))
    events = []
    for m in data['meetings']:
        cat = m['type'].lower()  # 'rada' / 'zastupitelstvo' - shoduje se se slugem v odkazu
        time_val = m.get('time')
        agenda_n = len(m.get('agenda') or [])
        events.append({
            'id': f'jednani-{cat}-{m["date"]}',
            'title': f'{m["type"]} {m["number"]}/{m["year"]}',
            'date': m['date'],
            'date_end': None,
            'time': time_val,
            'all_day': time_val is None,
            'category': cat,
            'link': f'/jednani/#{cat}-{m["date"]}',
            'description': f'{agenda_n} bodů programu' if agenda_n else None,
            'image': None,
            'note': None,
            'source_ref': m['uuid'],
        })
    return events


# ---------------------------------------------------------------- iCalendar

def ics_escape(text):
    return (text.replace('\\', '\\\\').replace(';', '\\;')
                .replace(',', '\\,').replace('\n', '\\n'))


def ics_fold(line):
    """RFC 5545 §3.1: řádky delší než 75 oktetů se skládají pokračovacím
    řádkem začínajícím mezerou. Bez toho striktnější klienty (Outlook)
    dlouhé SUMMARY/DESCRIPTION/URL ořežou nebo odmítnou celý soubor."""
    if len(line.encode('utf-8')) <= 75:
        return line
    out, rest = line[:75], line[75:]
    while rest:
        out += '\r\n ' + rest[:74]
        rest = rest[74:]
    return out


def event_to_vevent(ev, dtstamp):
    lines = ['BEGIN:VEVENT', f'UID:{ev["source_ref"] or ev["id"]}@pecky.online',
              f'DTSTAMP:{dtstamp}']
    if ev['all_day']:
        start = datetime.strptime(ev['date'], '%Y-%m-%d').date()
        end = datetime.strptime(ev['date_end'] or ev['date'], '%Y-%m-%d').date() + timedelta(days=1)
        lines.append(f'DTSTART;VALUE=DATE:{start.strftime("%Y%m%d")}')
        lines.append(f'DTEND;VALUE=DATE:{end.strftime("%Y%m%d")}')
    else:
        local = datetime.strptime(f'{ev["date"]} {ev["time"]}', '%Y-%m-%d %H:%M').replace(tzinfo=PRAGUE)
        start_utc = local.astimezone(timezone.utc)
        lines.append(f'DTSTART:{start_utc.strftime("%Y%m%dT%H%M%SZ")}')
    lines.append(ics_fold(f'SUMMARY:{ics_escape(ev["title"])}'))
    if ev['description']:
        lines.append(ics_fold(f'DESCRIPTION:{ics_escape(ev["description"])}'))
    if ev['link']:
        lines.append(ics_fold(f'URL:{SITE_DOMAIN}{ev["link"]}'))
    lines.append(f'CATEGORIES:{ev["category"].upper()}')
    lines.append('END:VEVENT')
    return lines


def build_ics(events):
    dtstamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    lines = [
        'BEGIN:VCALENDAR',
        'VERSION:2.0',
        'PRODID:-//pecky.online//Kalendar//CS',
        'CALSCALE:GREGORIAN',
        'METHOD:PUBLISH',
        'X-WR-CALNAME:Pečky online — Kalendář',
        'X-WR-TIMEZONE:Europe/Prague',
    ]
    for ev in events:
        lines += event_to_vevent(ev, dtstamp)
    lines.append('END:VCALENDAR')
    return '\r\n'.join(lines) + '\r\n'


def main():
    events = build_jednani_events()
    # (budoucí zdroje: events += build_volby_events(); events += build_akce_events(); ...)
    events.sort(key=lambda e: (e['date'], e['time'] or ''))

    OUT_JSON.write_text(json.dumps({
        'meta': {
            'generated_from': f'jednani/pecky-jednani.json ({len(events)} jednání)',
            'updated': datetime.now(PRAGUE).strftime('%Y-%m-%d'),
        },
        'events': events,
    }, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')

    OUT_ICS.write_text(build_ics(events), encoding='utf-8')

    by_cat = {}
    for e in events:
        by_cat[e['category']] = by_cat.get(e['category'], 0) + 1
    print(f'Vygenerováno {len(events)} událostí ({", ".join(f"{v} {k}" for k, v in by_cat.items())}) '
          f'-> {OUT_JSON.relative_to(ROOT)}, {OUT_ICS.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
