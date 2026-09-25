#!/usr/bin/env python3
"""
Promítnutí sekce Kalendář do Google kalendáře „Co se děje v Pečkách".

Bere hotový výstup `kalendar/udalosti.json` (generuje ho
`kalendar/scripts/update-kalendar.py`) a srovná s ním obsah Google kalendáře:
co je nové založí, co se změnilo přepíše, co ze zdroje zmizelo smaže. Vlastní
zdroje ani schéma události skript nezná — čte až ten společný výstup, takže
nový zdroj se do Googlu dostane sám, jakmile ho umí generátor.

Běh je idempotentní: ID události v Googlu je sha1 ze `source_ref`, který podle
`kalendar/README.md` musí zůstat stabilní napříč přegenerováními. Druhé
spuštění tedy událost přepíše, nezaloží ji podruhé.

Přístup drží servisní účet (`pecky-kalendar-sync@…`), kterému je kalendář
nasdílený s právem „Provádět změny v událostech". Klíč leží v
`.google-calendar-api-key.json` v kořeni repozitáře, je v `.gitignore`
a do gitu nepatří — cestu jde přebít proměnnou `PECKY_GOOGLE_KEY`.

Smaže jen událost, kterou sám založil (pozná ji podle
`extendedProperties.private.pecky`). Co si do kalendáře přidá člověk ručně,
nechá být.

Závislost: `pip3 install google-api-python-client google-auth` — jediná externí
závislost v celém repu, ostatní skripty jedou na standardní knihovně.

Použití:
    python3 kalendar/scripts/sync-google.py --dry-run    # jen vypíše plán
    python3 kalendar/scripts/sync-google.py --limit 20   # opatrný první běh
    python3 kalendar/scripts/sync-google.py              # ostrý zápis
"""
import argparse
import hashlib
import json
import os
import random
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.build import SITE_DOMAIN  # noqa: E402 - zdroj pravdy pro absolutní URL

UDALOSTI_JSON = ROOT / 'kalendar' / 'udalosti.json'
DEFAULT_KEY = ROOT / '.google-calendar-api-key.json'

CALENDAR_ID = ('a81de8fe68a5e6d118ceeea3614ba159febf695e65b164cade86b682d58ef726'
               '@group.calendar.google.com')
SCOPES = ['https://www.googleapis.com/auth/calendar']
PRAGUE = ZoneInfo('Europe/Prague')

# Událost bez uvedeného konce (zdroje ho nedrží) dostane v Googlu tuhle délku.
# Na rozdíl od .ics Google událost bez konce nepřijme.
DEFAULT_DURATION_MIN = 120

# Barvy podle kategorie, ať je kalendář čitelný podobně jako mřížka na webu.
BARVY = {
    'rada': '10',            # Basil — zelená jako --field v mřížce
    'zastupitelstvo': '11',  # Tomato — nejblíž bordó --burgundy
    'akce': '9',             # Blueberry
    'kurz': '8',             # Graphite — tlumená, kurzů je řádově nejvíc
    'volby': '5',            # Banana
    'svoz': '3',             # Grape — nejblíž vínové barvě Pečeckých služeb v mřížce
}

# Značka v extendedProperties, podle které skript pozná vlastní události.
MARKER = 'pecky-online-kalendar'

# Prodleva mezi zápisy. Google na jeden kalendář zápisy škrtí; 0,1 s stačí,
# aby první plný běh neskončil na rate limitu (ověřeno 22. 9. 2026 na 1317
# událostech, ani jeden pokus se neopakoval).
PRODLEVA_S = 0.1

# Naměřená doba jednoho zápisu i s odezvou Googlu (0,1 s prodleva + ~0,65 s
# round trip) — jen pro odhad vypisovaný před během.
ZAPIS_S = 0.75


def rozsah(ev):
    """`start`/`end` pro Google API. Celodenní akce má konec vylučující
    (stejně jako DTEND v .ics), u akce s časem se konec dopočítá."""
    if ev['all_day']:
        zacatek = datetime.strptime(ev['date'], '%Y-%m-%d').date()
        konec = datetime.strptime(ev['date_end'] or ev['date'], '%Y-%m-%d').date() + timedelta(days=1)
        return {'date': zacatek.isoformat()}, {'date': konec.isoformat()}
    zacatek = datetime.strptime(f'{ev["date"]} {ev["time"]}', '%Y-%m-%d %H:%M').replace(tzinfo=PRAGUE)
    konec = zacatek + timedelta(minutes=DEFAULT_DURATION_MIN)
    return ({'dateTime': zacatek.isoformat(), 'timeZone': 'Europe/Prague'},
            {'dateTime': konec.isoformat(), 'timeZone': 'Europe/Prague'})


def google_id(ev):
    """Stabilní ID události v Googlu.

    Google přijímá jen znaky base32hex (0-9, a-v) a délku 5–1024 — sha1 v hex
    zápisu se do toho vejde celý, na rozdíl od `source_ref`, který bývá UUID
    s pomlčkami nebo textový slug.
    """
    return hashlib.sha1((ev.get('source_ref') or ev['id']).encode('utf-8')).hexdigest()


def abs_url(link):
    """`link` je buď absolutní URL na externí zdroj (akce/kurz od 24. 9. 2026
    míří rovnou na doklad, ne na web samotný), nebo cesta uvnitř webu
    (jednání/volby) — ty jediné potřebují SITE_DOMAIN dopsat."""
    if not link:
        return None
    if link.startswith('http://') or link.startswith('https://'):
        return link
    return f'{SITE_DOMAIN}{link}'


def telo_udalosti(ev):
    """Jedna událost společného schématu -> tělo pro Google API."""
    zacatek, konec = rozsah(ev)
    url = abs_url(ev.get('link'))
    # "Do Peček . cz" jako název zdroje dává smysl jen u interních odkazů
    # (jednání/volby) — u akcí/kurzů teď url míří na cizí web, tam ať si
    # Google název domény odvodí sám.
    url_je_nas = bool(url) and url.startswith(SITE_DOMAIN)
    popis = [t for t in (
        ev.get('description'),
        f'Pořádá {ev["organizer_name"]}' if ev.get('organizer_name') else None,
        f'Podrobnosti: {url}' if url else None,
    ) if t]

    telo = {
        'id': google_id(ev),
        'summary': ev['title'],
        'start': zacatek,
        'end': konec,
        'description': '\n'.join(popis) or None,
        'location': ev.get('place') or None,
        'colorId': BARVY.get(ev['category']),
        # Kalendář je veřejný k odběru — událost města nemá odběrateli
        # blokovat jeho vlastní čas jako obsazený.
        'transparency': 'transparent',
        # Bez tohohle by Google k 1300 událostem rozesílal výchozí upomínky.
        'reminders': {'useDefault': False},
        'extendedProperties': {'private': {
            'pecky': MARKER,
            'peckyRef': (ev.get('source_ref') or ev['id'])[:1024],
            'peckyCat': ev['category'],
        }},
    }
    if url:
        telo['source'] = {'url': url, **({'title': 'Do Peček . cz'} if url_je_nas else {})}
    telo = {k: v for k, v in telo.items() if v is not None}

    # Otisk obsahu, aby další běh poznal, co se od minule opravdu změnilo,
    # a nepřepisoval všech 1300 událostí zbytečně.
    otisk = hashlib.sha1(json.dumps(telo, sort_keys=True, ensure_ascii=False).encode('utf-8')).hexdigest()
    telo['extendedProperties']['private']['peckyHash'] = otisk
    return telo


# ------------------------------------------------------------------ Google API

def sluzba(cesta_klice):
    from google.oauth2 import service_account
    from googleapiclient.discovery import build

    klic = Path(cesta_klice)
    if not klic.exists():
        sys.exit(
            f'Klíč servisního účtu nenalezen: {klic}\n'
            'Cestu jde přebít proměnnou PECKY_GOOGLE_KEY.\n'
            'Běžíš-li mimo autorův počítač (cloudový checkout klíč nemá, je\n'
            'v .gitignore), tohle není chyba k obcházení: synchronizaci vynech,\n'
            'pokračuj zbytkem kontroly a do shrnutí napiš, že Google kalendář\n'
            'čeká na ruční spuštění tohohle skriptu.')
    creds = service_account.Credentials.from_service_account_file(str(klic), scopes=SCOPES)
    return build('calendar', 'v3', credentials=creds, cache_discovery=False)


def zkus(volani, popis, pokusu=5):
    """Google při dávkovém zápisu občas vrátí 403 rateLimitExceeded nebo 5xx.
    Exponenciální čekání s náhodným rozptylem, ať se opakované pokusy
    nesejdou v jednom okamžiku."""
    from googleapiclient.errors import HttpError

    for pokus in range(pokusu):
        try:
            return volani.execute()
        except HttpError as e:
            if e.resp.status in (403, 429, 500, 502, 503) and pokus < pokusu - 1:
                cekat = 2 ** pokus + random.random()
                print(f'  ! {popis}: HTTP {e.resp.status}, další pokus za {cekat:.1f} s')
                time.sleep(cekat)
                continue
            raise


def nacti_existujici(svc, cal_id):
    """Všechny události v kalendáři (i minulé) jako {id: událost}."""
    existujici, token = {}, None
    while True:
        odpoved = zkus(svc.events().list(
            calendarId=cal_id, maxResults=2500, showDeleted=False,
            singleEvents=False, pageToken=token), 'výpis událostí')
        for e in odpoved.get('items', []):
            existujici[e['id']] = e
        token = odpoved.get('nextPageToken')
        if not token:
            return existujici


def je_nase(udalost):
    return (udalost.get('extendedProperties', {}).get('private', {}).get('pecky') == MARKER)


# ------------------------------------------------------------------------ běh

def main():
    ap = argparse.ArgumentParser(description='Promítne kalendar/udalosti.json do Google kalendáře.')
    ap.add_argument('--dry-run', action='store_true', help='jen vypíše plán, nic nezapíše')
    ap.add_argument('--limit', type=int, help='provede nejvýš N zápisů (opatrný první běh)')
    ap.add_argument('--no-delete', action='store_true', help='nemaže události, které ze zdroje zmizely')
    ap.add_argument('--calendar-id', default=os.environ.get('PECKY_GOOGLE_CALENDAR', CALENDAR_ID))
    ap.add_argument('--key', default=os.environ.get('PECKY_GOOGLE_KEY', str(DEFAULT_KEY)))
    args = ap.parse_args()

    data = json.loads(UDALOSTI_JSON.read_text(encoding='utf-8'))
    zdroj = {}
    for ev in data['events']:
        telo = telo_udalosti(ev)
        zdroj[telo['id']] = telo
    print(f'Zdroj: {UDALOSTI_JSON.relative_to(ROOT)} — {len(zdroj)} událostí '
          f'(aktualizováno {data["meta"]["updated"]})')

    svc = sluzba(args.key)
    kalendar = zkus(svc.calendars().get(calendarId=args.calendar_id), 'načtení kalendáře')
    print(f'Kalendář: {kalendar.get("summary")} ({kalendar.get("timeZone")})')

    existujici = nacti_existujici(svc, args.calendar_id)
    nase = {k: v for k, v in existujici.items() if je_nase(v)}
    print(f'V kalendáři teď: {len(existujici)} událostí, z toho {len(nase)} od tohohle skriptu')

    k_zalozeni = [i for i in zdroj if i not in existujici]
    k_uprave = [i for i in zdroj if i in existujici
                and existujici[i].get('extendedProperties', {}).get('private', {}).get('peckyHash')
                != zdroj[i]['extendedProperties']['private']['peckyHash']]
    ke_smazani = [] if args.no_delete else [i for i in nase if i not in zdroj]

    print(f'\nPlán: {len(k_zalozeni)} založit, {len(k_uprave)} upravit, {len(ke_smazani)} smazat')
    for nadpis, ids in (('založit', k_zalozeni), ('upravit', k_uprave)):
        for i in ids[:3]:
            t = zdroj[i]
            kdy = t['start'].get('date') or t['start'].get('dateTime')
            print(f'  {nadpis}: {kdy}  {t["summary"]}')
        if len(ids) > 3:
            print(f'  {nadpis}: … a dalších {len(ids) - 3}')
    for i in ke_smazani[:3]:
        print(f'  smazat: {existujici[i].get("summary")}')
    if len(ke_smazani) > 3:
        print(f'  smazat: … a dalších {len(ke_smazani) - 3}')

    if args.dry_run:
        print('\n--dry-run: nic se nezapisovalo.')
        return

    zapisu = len(k_zalozeni) + len(k_uprave) + len(ke_smazani)
    if args.limit:
        zapisu = min(zapisu, args.limit)
    if not zapisu:
        print('\nNení co dělat.')
        return
    print(f'\nZapisuji ({zapisu} operací, odhadem {zapisu * ZAPIS_S / 60:.1f} min)…')

    from googleapiclient.errors import HttpError
    hotovo = 0

    def limit_vycerpan():
        return args.limit is not None and hotovo >= args.limit

    for i in k_zalozeni:
        if limit_vycerpan():
            break
        try:
            zkus(svc.events().insert(calendarId=args.calendar_id, body=zdroj[i]), f'insert {i}')
        except HttpError as e:
            if e.resp.status == 409:
                # ID je obsazené dřív smazanou událostí — update ji oživí.
                zkus(svc.events().update(calendarId=args.calendar_id, eventId=i, body=zdroj[i]),
                     f'update po 409 {i}')
            else:
                raise
        hotovo += 1
        time.sleep(PRODLEVA_S)

    for i in k_uprave:
        if limit_vycerpan():
            break
        zkus(svc.events().update(calendarId=args.calendar_id, eventId=i, body=zdroj[i]), f'update {i}')
        hotovo += 1
        time.sleep(PRODLEVA_S)

    for i in ke_smazani:
        if limit_vycerpan():
            break
        zkus(svc.events().delete(calendarId=args.calendar_id, eventId=i), f'delete {i}')
        hotovo += 1
        time.sleep(PRODLEVA_S)

    print(f'Hotovo: {hotovo} operací.')
    if args.limit and hotovo >= args.limit:
        print('Limit vyčerpán — zbytek dokončí další běh.')


if __name__ == '__main__':
    main()
