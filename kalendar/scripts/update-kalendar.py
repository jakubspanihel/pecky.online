#!/usr/bin/env python3
"""
Aktualizace dat sekce Kalendář (panel-kalendar v content/kalendar.html).

Sesbírá události ze všech zdrojů do jednoho společného schématu a zapíše:
- kalendar/udalosti.json — data pro klientské vykreslení mřížky (fetch()
  v content/kalendar.html)
- kalendar/kalendar.ics  — stejné události ve formátu iCalendar (RFC 5545),
  ke stažení/přihlášení (webcal) v Google/Apple/Outlook kalendáři

Zdroje (další se dopisují jako další build_*_events() funkce a přidají
do seznamu v main()):
A) Jednání rady a zastupitelstva — z jednani/pecky-jednani.json (stejný
   zdroj jako sekce Jednání a jednani/scripts/update-pozemky.py).
B) Kulturní a společenské akce — z kalendar/akce.json, které plní
   skill DoPecek-kalendar-plakat z plakátů Kulturního střediska
   města Pečky (kategorie 'akce' a 'kurz').
C) Volby — z kalendar/udalosti-volby.json, ručně psaný soubor bez
   vlastního scraperu (termín voleb se nemění často). Datum vždy ověřit
   proti volby.gov.cz (sources.json -> volby-gov-cz; viz
   kalendar/README.md -> "Volby").
D) Zápasy AFK Pečky — z kalendar/afk-zapasy.json, které stahuje
   kalendar/scripts/fetch-afk-zapasy.py z afkpecky.cz (do kalendáře jen
   zápasy hrané v Pečkách, všech týmů). Tenhle skript sám nic nestahuje -
   pracuje s posledním uloženým souborem, viz kalendar/README.md ->
   "Zápasy AFK Pečky".
F) Pravidelné provozní doby — kalendar/sberny-dvur.json, otevírací doba
   bez konce (rozepisuje se na horizont meta.horizon), kategorie 'svoz'.
E) Svoz odpadů — z kalendar/svoz-odpadu.json (harmonogram města, vytěžený
   z PDF skriptem kalendar/scripts/extract-svoz-odpadu.py), kategorie
   'svoz', jedna celodenní událost na typ svozu a den.

Spouštět po každé aktualizaci jednani/pecky-jednani.json nebo
kalendar/akce.json (stejně jako jednani/scripts/update-pozemky.py). Po běhu tohoto skriptu je potřeba
i scripts/build.py, aby se případná změna `content/kalendar.html`
promítla do veřejné stránky (samotná data v kalendar/udalosti.json
a kalendar/kalendar.ics build.py nekopíruje ani neupravuje, jen je
scripts/serve.py / GitHub Pages servíruje přímo ze složky kalendar/).

Po vygenerování rovnou spustí kalendar/scripts/sync-google.py (promítnutí
do veřejného Google Kalendáře), viz sync_google() níže; bez klíče nebo
knihovny sync jen přeskočí s varováním.

Použití:
    python3 kalendar/scripts/update-kalendar.py              # vygenerovat + synchronizovat
    python3 kalendar/scripts/update-kalendar.py --no-sync    # jen vygenerovat
"""
import json
import os
import re
import sys
import unicodedata
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
VYBORY_JSON = ROOT / 'jednani' / 'vybory.json'
KOMISE_JSON = ROOT / 'jednani' / 'komise.json'
SKOLSKA_RADA_JSON = ROOT / 'jednani' / 'skolska-rada.json'
AKCE_JSON = ROOT / 'kalendar' / 'akce.json'
SOURCES_JSON = ROOT / 'sources.json'
LIDE_SOURCES_JSON = ROOT / 'lide' / 'sources.json'
VOLBY_JSON = ROOT / 'kalendar' / 'udalosti-volby.json'
AFK_JSON = ROOT / 'kalendar' / 'afk-zapasy.json'
SVOZ_JSON = ROOT / 'kalendar' / 'svoz-odpadu.json'
HALA_JSON = ROOT / 'kalendar' / 'sportovni-hala.json'
PROVOZNI_DOBY_JSON = [ROOT / 'kalendar' / 'sberny-dvur.json',
                      ROOT / 'kalendar' / 'zkouska-siren.json']
ORGANIZACE_JSON = ROOT / 'lide' / 'organizations.json'
OUT_JSON = ROOT / 'kalendar' / 'udalosti.json'
OUT_ICS = ROOT / 'kalendar' / 'kalendar.ics'

PRAGUE = ZoneInfo('Europe/Prague')


def nazvy_organizaci():
    """id -> zobrazovaný název z lide/organizations.json.

    Rejstřík organizací je jeden pro celý web (sekce Lidé) - kalendář si
    vlastní seznam pořadatelů nedrží, jen si odtud bere jméno k id, aby ho
    klient nemusel dohledávat druhým fetchem.
    """
    data = json.loads(ORGANIZACE_JSON.read_text(encoding='utf-8'))
    return {o['id']: (o.get('short_name') or o['name']) for o in data['organizations']}


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
    org = nazvy_organizaci()
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
            'place': None,
            'organizer': 'mesto-pecky',
            'organizer_name': org.get('mesto-pecky', 'Město Pečky'),
            'image': None,
            'note': None,
            'source_ref': m['uuid'],
        })
    return events


def build_vybory_events():
    """Výbory ZM, komise RM a školská rada -> společné schéma (kategorie 'vybor').

    Zdroje: jednani/vybory.json (finanční a kontrolní výbor),
    jednani/komise.json (komise rady města a pracovní skupina pro oslavy)
    a jednani/skolska-rada.json (školská rada ZŠ Pečky; pořadatelem je
    škola). Všechny mají stejný tvar záznamu (viz jednani/README.md).

    Jednání se nečíslují, takže titulek je název orgánu (u společného
    jednání dvou orgánů oba názvy). Čas a místo jen tam, kde je zápis
    uvádí (jinak celodenní). Do kalendáře jdou jen jednání se zveřejněným
    zápisem — ohlášená nemají v datech samostatný záznam. Kategorie
    'vybor' (barva v mřížce i v Google Kalendáři viz styles.css
    a sync-google.py).
    """
    org = nazvy_organizaci()
    zdroje = [(VYBORY_JSON, 'mesto-pecky'), (KOMISE_JSON, 'mesto-pecky'), (SKOLSKA_RADA_JSON, 'zs-pecky')]
    events = []
    for cesta, poradatel in zdroje:
        if not cesta.exists():
            continue
        data = json.loads(cesta.read_text(encoding='utf-8'))
        for m in data['meetings']:
            agenda_n = len(m.get('agenda') or [])
            body = 'bod' if agenda_n == 1 else 'body' if 2 <= agenda_n <= 4 else 'bodů'
            bodies = m.get('bodies') or [m['type']]
            title = ' a '.join(bodies) if len(bodies) > 1 else m['type']
            events.append({
                'id': f'jednani-{m["id"]}',
                'title': title,
                'date': m['date'],
                'date_end': None,
                'time': m.get('time'),
                'all_day': m.get('time') is None,
                'category': 'vybor',
                'link': f'/jednani/#{m["id"]}',
                'description': f'{agenda_n} {body} programu' if agenda_n else None,
                'place': m.get('venue'),
                'organizer': poradatel,
                'organizer_name': org.get(poradatel, 'Město Pečky'),
                'image': None,
                'note': None,
                'source_ref': m['id'],
            })
    return events


def je_profil(sid):
    return sid.startswith(('facebook-', 'instagram-')) and not sid.startswith(('facebook-group-', 'facebook-event-'))


def majitele_profilu(pocty):
    """source id profilu na síti -> pořadatel, u něhož je v evidenci akcí nejčastější.

    Kdo plakát jen sdílí (město přeposílá akci spolku, kulturní středisko akci města),
    profil nevlastní: jeho odkaz se u cizího pořadatele nepovažuje za zdroj pořadatele.
    `pocty` = {id pořadatele: {source id: počet dokladů}}.
    """
    nej = {}
    for org_id, podle in pocty.items():
        for sid, n in podle.items():
            if je_profil(sid) and n > nej.get(sid, (None, 0))[1]:
                nej[sid] = (org_id, n)
    return {sid: v[0] for sid, v in nej.items()}


def zdroje_poradatelu():
    """id pořadatele -> zdroje, ze kterých jsou jeho akce zapsané (nejčastější první).

    Počítá se z `evidence[].source` v kalendar/akce.json; název a adresa zdroje
    z `sources.json` (profil na síti jen u pořadatele, u něhož je nejčastější). Za ně se řadí profily pořadatele na Facebooku a Instagramu
    z `lide/organizations.json` → `sources` (adresy z `lide/sources.json`),
    které v evidenci akcí zatím nejsou (`n` = 0; skupiny a odkazy na jednotlivé
    příspěvky se nepřebírají). Klient (Kalendář, řádek nad tabulkou při jediném vybraném
    pořadateli) z toho skládá větu „Další zdroje“. Do `udalosti.json` jde jako
    samostatný klíč `org_sources`, ne do každé události (stovky opakování).
    """
    if not AKCE_JSON.exists():
        return {}
    zdroje = {z['id']: z for z in json.loads(SOURCES_JSON.read_text(encoding='utf-8')).get('sources', [])}
    pocty = {}
    for a in json.loads(AKCE_JSON.read_text(encoding='utf-8')).get('events', []):
        org_id = a.get('organizer')
        if not org_id:
            continue
        for ev in a.get('evidence') or []:
            pocty.setdefault(org_id, {}).setdefault(ev['source'], 0)
            pocty[org_id][ev['source']] += 1
    majitel = majitele_profilu(pocty)
    for org_id, podle in pocty.items():
        for sid in [s for s in podle if s in majitel and majitel[s] != org_id]:
            del podle[sid]
    lide_zdroje = json.loads(LIDE_SOURCES_JSON.read_text(encoding='utf-8')).get('sources', {})
    orgs = {o['id']: o for o in json.loads(ORGANIZACE_JSON.read_text(encoding='utf-8'))['organizations']}
    norm = lambda u: u.lower().rstrip('/')
    vystup = {}
    for org_id, podle in pocty.items():
        radek = []
        for sid, n in sorted(podle.items(), key=lambda x: (-x[1], x[0])):
            z = zdroje.get(sid)
            if z and z.get('url'):
                radek.append({'name': z['name'], 'url': z['url'], 'n': n})
        videno = {norm(x['url']) for x in radek}
        for sid in orgs.get(org_id, {}).get('sources', []):
            z = lide_zdroje.get(sid)
            if not z or not re.search(r'//(www\.)?(facebook|instagram)\.com/', z['url']):
                continue
            if '/groups/' in z['url'] or '/posts/' in z['url'] or norm(z['url']) in videno:
                continue
            videno.add(norm(z['url']))
            nazev = next((x['name'] for x in zdroje.values() if norm(x.get('url') or '') == norm(z['url'])), z['label'])
            radek.append({'name': nazev, 'url': z['url'], 'n': 0})
        if radek:
            vystup[org_id] = radek
    return vystup


def build_akce_events():
    """Kulturní a společenské akce z kalendar/akce.json -> společné schéma.

    Zdrojový soubor plní skill DoPecek-kalendar-plakat přepisem plakátů
    a příspěvků pořadatelů. Pořadatel (`organizer`) a zdroj (`evidence[].source`)
    jsou dvě různé věci: akci může pořádat spolek a ohlásit ji facebook města.
    Do kalendáře jde pořadatel (filtr i tooltip). Akce bez uvedeného času
    (plakát ho neuvádí, např. „po setmění") jdou do kalendáře jako celodenní.
    Odkaz vede přímo na zdroj, ze kterého akce vznikla — první doklad
    v `evidence[]` (nejsilnější zdroj, podle kterého jsou zapsané údaje, viz
    „Schéma jedné události" v kalendar/README.md), ne na interní kotvu na
    webu. Od 24. 9. 2026 na žádost uživatele — dřív šlo o `/kalendar/#<id>`.
    """
    if not AKCE_JSON.exists():
        return []
    data = json.loads(AKCE_JSON.read_text(encoding='utf-8'))
    org = nazvy_organizaci()
    pocty = {}
    for a in data.get('events', []):
        for ev in a.get('evidence') or []:
            p = pocty.setdefault(a.get('organizer'), {})
            p[ev['source']] = p.get(ev['source'], 0) + 1
    majitel = majitele_profilu(pocty)
    events = []
    for a in data.get('events', []):
        time_val = a.get('time')
        # pořadatel mimo rejstřík organizací (cizí soubor, soukromý pořadatel)
        # má jen jméno v organizer_name - do mřížky patří i tak
        org_id = a.get('organizer')
        org_name = org.get(org_id) if org_id else None
        org_name = org_name or a.get('organizer_name')
        evidence = a.get('evidence') or []
        sdileno = bool(evidence) and majitel.get(evidence[0]['source'], org_id) != org_id
        events.append({
            'id': a['id'],
            'title': a['title'],
            'date': a['date'],
            'date_end': a.get('date_end'),
            'time': time_val,
            **({'time_end': a['time_end']} if a.get('time_end') else {}),
            'all_day': time_val is None,
            'category': a['category'],  # 'akce' / 'kurz'
            'link': evidence[0]['url'] if evidence else None,
            'description': a.get('description') or a.get('place'),
            'place': a.get('place'),
            'organizer': org_id,
            'organizer_name': org_name,
            'image': a.get('image'),
            'note': a.get('note'),
            'source_ref': a['id'],  # id v akce.json je stabilní -> drží UID v .ics
            # první doklad je cizí profil, který akci jen sdílel -> klient z něj neodvozuje zdroj pořadatele
            **({'link_sdileno': True} if sdileno else {}),
        })
    return events


def build_hala_events():
    """Rezervace sportovní haly (ParkHala) z kalendar/sportovni-hala.json -> společné schéma.

    Soubor se stahuje ručně z rezervačního systému na pecky.cz (postup v
    kalendar/README.md -> „Rezervace sportovní haly“). Nepotvrzená rezervace
    dostane za název „ (nepotvrzeno)“ (zadání uživatele 11. 10. 2026); id ani
    source_ref stav neobsahují, takže potvrzení jen přepíše titulek téže události.
    """
    if not HALA_JSON.exists():
        return []
    data = json.loads(HALA_JSON.read_text(encoding='utf-8'))
    meta = data['meta']
    org = nazvy_organizaci()
    events = []
    for r in data['events']:
        org_id = r.get('organizer') or meta.get('organizer')  # výjimka na úrovni rezervace (např. FBC Charisma)
        slug = re.sub(r'[^a-z0-9]+', '-', unicodedata.normalize('NFKD', r['title']).encode('ascii', 'ignore').decode().lower()).strip('-')
        eid = f'hala-{r["date"]}-{r["time"].replace(":", "")}-{slug}'
        events.append({
            'id': eid,
            'title': r['title'] + (' (nepotvrzeno)' if r.get('status') == 'nepotvrzeno' else ''),
            'date': r['date'],
            'date_end': None,
            'time': r['time'],
            'time_end': r.get('time_end'),
            'all_day': False,
            'category': r['category'],  # 'akce' / 'kurz'
            'link': meta['evidence']['url'],
            'description': meta['place'],
            'place': meta['place'],
            'organizer': org_id,
            'organizer_name': org.get(org_id) if org_id else None,
            'image': None,
            'note': None,
            'source_ref': eid,
        })
    return events


def build_volby_events():
    """Termíny voleb z kalendar/udalosti-volby.json -> společné schéma.

    Na rozdíl od Jednání a Akcí nemá tenhle zdroj vlastní scraper - termín
    voleb se nemění často, soubor se aktualizuje ručně po ověření proti
    volby.gov.cz (sources.json -> volby-gov-cz; viz kalendar/README.md
    -> "Volby"). Schéma je společné s ostatními zdroji, ne zvláštní
    volební pole.
    """
    if not VOLBY_JSON.exists():
        return []
    data = json.loads(VOLBY_JSON.read_text(encoding='utf-8'))
    org = nazvy_organizaci()
    events = []
    for a in data.get('events', []):
        time_val = a.get('time')
        org_id = a.get('organizer')
        org_name = org.get(org_id) if org_id else None
        org_name = org_name or a.get('organizer_name')
        events.append({
            'id': a['id'],
            'title': a['title'],
            'date': a['date'],
            'date_end': a.get('date_end'),
            'time': time_val,
            'all_day': time_val is None,
            'category': a['category'],
            'link': a.get('link'),
            'description': a.get('description'),
            'place': a.get('place'),
            'organizer': org_id,
            'organizer_name': org_name,
            'image': a.get('image'),
            'note': a.get('note'),
            'source_ref': a['id'],
        })
    return events


def build_afk_events():
    """Zápasy AFK Pečky hrané v Pečkách z kalendar/afk-zapasy.json -> společné schéma.

    Soubor plní kalendar/scripts/fetch-afk-zapasy.py (všechny zápasy všech
    týmů, doma i venku). Do kalendáře jdou jen ty s `in_pecky` - hřiště
    v Pečkách podle webu klubu, i když je soupeř vedený jako domácí.
    Kategorie `akce`: zápas je veřejná jednorázová událost pro diváky,
    ne kurz/trénink. Odehrané zápasy zůstávají s výsledkem v popisu.
    """
    if not AFK_JSON.exists():
        return []
    data = json.loads(AFK_JSON.read_text(encoding='utf-8'))
    org = nazvy_organizaci()
    events = []
    for t in data['teams']:
        # týž zápas může být v rozpisu klubu dvakrát (např. starší žáci 23. 8. 2026,
        # jednou bez výsledku a jednou s ním) - platí ten s výsledkem, jinak první
        nejlepsi = {}
        for m in t['matches']:
            k = (m['date'], (m.get('home_team') or '').strip(), (m.get('away_team') or '').strip())
            if k not in nejlepsi or (m.get('score') and not nejlepsi[k].get('score')):
                nejlepsi[k] = m
        for m in t['matches']:
            if not m['in_pecky']:
                continue
            if nejlepsi[(m['date'], (m.get('home_team') or '').strip(), (m.get('away_team') or '').strip())] is not m:
                continue
            # záznam bez soupeřů (prázdný řádek v rozpisu klubu) není zápas
            if not (m.get('home_team') or '').strip() or not (m.get('away_team') or '').strip():
                continue
            # "Mistrovská utkání" (nadpis tabulky) -> "mistrovské utkání"
            soutez = {'Mistrovská utkání': 'mistrovské utkání',
                      'Přátelská utkání': 'přátelské utkání'}.get(m['competition'], m['competition'])
            popis = [t.get('league'), soutez]
            if m.get('score'):
                popis.append(f'výsledek {m["score"]}')
            events.append({
                'id': m['id'],
                'title': f'{m["home_team"]} – {m["away_team"]} ({t["name"]})',
                'date': m['date'],
                'date_end': None,
                'time': m['time'],
                'all_day': m['time'] is None,
                'category': 'akce',
                'link': t['url'],
                'description': ' · '.join(p for p in popis if p),
                'place': 'Fotbalové hřiště AFK Pečky, Barákova ul., Pečky',
                'organizer': 'afk-pecky',
                'organizer_name': org.get('afk-pecky', 'AFK Pečky'),
                'image': None,
                'note': (None if m['home'] else
                         'Domácím týmem je soupeř, hraje se ale na hřišti AFK Pečky (podle webu klubu).'),
                'source_ref': m['id'],
            })
    return events


def build_svoz_events():
    """Harmonogram svozu odpadů z kalendar/svoz-odpadu.json -> společné schéma.

    Zdrojový soubor drží jeden záznam na typ svozu se seznamem dat (tak ho
    vytěží extract-svoz-odpadu.py z PDF). Sem se rozepíše na jednu celodenní
    událost na typ a den - v mřížce se tak dá poznat, co ten den jede,
    a filtr/checkbox "Svoz odpadu" je schová najednou. Odkaz vede na stránku
    /kalendar/svoz.html (harmonogram dle lokality, PDF ke stažení je tam).
    """
    if not SVOZ_JSON.exists():
        return []
    data = json.loads(SVOZ_JSON.read_text(encoding='utf-8'))
    meta = data['meta']
    org = nazvy_organizaci()
    org_id = meta.get('organizer')
    events = []
    for t in data['types']:
        # zrušený / přesunutý svoz zůstává v dates[] (v PDF harmonogramu je),
        # jen dostane předponu a text zprávy Pečeckých služeb v poznámce;
        # zpráva se zmínkou jen části lokality (`upozorneni: true`) dostane
        # místo „[zrušeno!]“ předponu ⚠️
        zruseno = t.get('zruseno') or {}
        for d in t['dates']:
            eid = f'svoz-{t["id"]}-{d}'
            zr = zruseno.get(d)
            events.append({
                'id': eid,
                'title': (('⚠️ ' if zr.get('upozorneni') else '[zrušeno!] ') if zr else '') + t['title'],
                'date': d,
                'date_end': None,
                'time': meta.get('time'),
                'time_end': meta.get('time_end'),
                'all_day': not meta.get('time'),
                'category': 'svoz',
                'link': '/kalendar/svoz.html',
                'description': t['place'],
                'place': t['place'],
                'organizer': org_id,
                'organizer_name': org.get(org_id) if org_id else None,
                'image': None,
                'note': zr['zprava'] if zr else None,
                'source_ref': eid,
            })
    return events


def build_provozni_doby_events():
    """Pravidelné provozní doby (sběrný dvůr, městský úřad) -> společné schéma.

    Každý soubor z PROVOZNI_DOBY_JSON má pravidla (den v týdnu + od-do), která
    platí od meta.from bez konce; rozepisují se po meta.horizon (ISO datum),
    horizont se čas od času posouvá a generátor se spouští znovu. Událost nese
    'time_end' (volitelné pole schématu -> DTEND v .ics a konec v Google
    Kalendáři) a 'tag' (štítek v Seznamu, jinak se použije štítek kategorie).
    """
    org = nazvy_organizaci()
    events = []
    for path in PROVOZNI_DOBY_JSON:
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding='utf-8'))
        meta = data['meta']
        org_id = meta.get('organizer')
        d = datetime.strptime(meta['from'], '%Y-%m-%d').date()
        last = datetime.strptime(meta['horizon'], '%Y-%m-%d').date()
        while d <= last:
            for r in data['rules']:
                # volitelné 'nth' = pořadí dne v měsíci (1 = první středa apod.)
                if d.weekday() == r['weekday'] and ('nth' not in r or (d.day - 1) // 7 + 1 == r['nth']):
                    eid = f'{meta["id"]}-{d.isoformat()}' + (f'-{r["from"].replace(":", "")}' if meta.get('id_s_casem') else '')
                    events.append({
                        'id': eid,
                        'title': meta['title'],
                        'tag': meta.get('tag', ''),  # '' = bez štítku (ne štítek kategorie)
                        'date': d.isoformat(),
                        'date_end': None,
                        'time': r['from'],
                        'time_end': r.get('to'),
                        'all_day': False,
                        'category': meta.get('category', 'svoz'),
                        'link': meta['evidence']['url'],
                        'description': f'{meta["description_prefix"]} {r["from"]}–{r["to"]}' if r.get('to') else meta['description_prefix'],
                        'place': meta['place'],
                        'organizer': org_id,
                        'organizer_name': org.get(org_id) if org_id else None,
                        'image': None,
                        'note': None,
                        'source_ref': eid,
                    })
            d += timedelta(days=1)
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


def abs_url(link):
    """`link` je buď absolutní URL na externí zdroj (akce/kurz od 24. 9. 2026
    míří rovnou na doklad, ne na web samotný), nebo cesta uvnitř webu
    (jednání/volby) — ty jediné potřebují SITE_DOMAIN dopsat."""
    if not link:
        return None
    if link.startswith('http://') or link.startswith('https://'):
        return link
    return f'{SITE_DOMAIN}{link}'


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
        if ev.get('time_end'):
            end_local = datetime.strptime(f'{ev["date"]} {ev["time_end"]}', '%Y-%m-%d %H:%M').replace(tzinfo=PRAGUE)
            lines.append(f'DTEND:{end_local.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")}')
    lines.append(ics_fold(f'SUMMARY:{ics_escape(ev["title"])}'))
    popis = [t for t in (ev.get('description'),
                         f'Pořádá {ev["organizer_name"]}' if ev.get('organizer_name') else None)
             if t]
    if popis:
        lines.append(ics_fold(f'DESCRIPTION:{ics_escape(". ".join(popis))}'))
    if ev.get('place'):
        lines.append(ics_fold(f'LOCATION:{ics_escape(ev["place"])}'))
    url = abs_url(ev['link'])
    if url:
        lines.append(ics_fold(f'URL:{url}'))
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
        'X-WR-CALNAME:Do Peček . cz — Kalendář',
        'X-WR-TIMEZONE:Europe/Prague',
    ]
    for ev in events:
        lines += event_to_vevent(ev, dtstamp)
    lines.append('END:VCALENDAR')
    return '\r\n'.join(lines) + '\r\n'


# Sjednocení různých zápisů téhož místa (zdroje je píšou pokaždé jinak) — klíč je
# zápis ze zdroje, hodnota jednotný název. Místa, o kterých není jisté, že jde
# o totéž (sály ZUŠ), se neslučují.
MISTA = {
    'Sokolovna Pečky': 'Sokolovna',
    'Sokolovna (Sokolská 330)': 'Sokolovna',
    'Sokolovna Pečky (galerie)': 'Sokolovna (galerie)',
    'Sokolovna Pečky (klubovna)': 'Sokolovna (klubovna)',
    'Sportovní hala': 'Hala',
    'Hala (Barákova 1039)': 'Hala',
    'Park Hala Pečky (sportovní hala)': 'Hala',
    'Městská knihovna Svatopluka Čecha Pečky': 'Knihovna',
    'Městská knihovna Svatopluka Čecha v Pečkách': 'Knihovna',
    'Městská knihovna Svatopluka Čecha v Pečkách, tř. 5. května 241': 'Knihovna',
    'Městská knihovna Svatopluka Čecha, 5. května 241, Pečky': 'Knihovna',
    'Kulturní dům Pečky': 'Kulturní dům',
    'Kulturní dům, Pečky': 'Kulturní dům',
    'Kulturní středisko Pečky': 'Kulturní dům',
    'Městský úřad Pečky': 'Městský úřad',
    'MěÚ Pečky': 'Městský úřad',
    'Fotbalové hřiště AFK Pečky': 'Hřiště (fotbalové)',
    'Fotbalové hřiště AFK Pečky, Barákova ul., Pečky': 'Hřiště (fotbalové)',
    'Základní škola Pečky, okres Kolín, Tř. Jana Švermy 342, Pečky': 'Základní škola',
    'ZŠ Pečky': 'Základní škola',
    'Mateřská škola MAŠINKA Pečky, Tř. Jana Švermy 825, Pečky': 'Mateřská škola',
    'MŠ MAŠINKA Pečky': 'Mateřská škola',
    'U rybníka Benešák, Pečky': 'U Benešáku',
    'Minigolfové hřiště u rybníka Benešáku, Pečky': 'Minigolfové hřiště',
}


def sjednot_mista(events):
    for e in events:
        puvodni = e.get('place')
        if puvodni in MISTA:
            e['place'] = MISTA[puvodni]
            if e.get('description') == puvodni:
                e['description'] = e['place']


def main():
    jednani = build_jednani_events()
    vybory = build_vybory_events()
    akce = build_akce_events()
    volby = build_volby_events()
    afk = build_afk_events()
    svoz = build_svoz_events()
    sberny = build_provozni_doby_events()
    hala = build_hala_events()
    # Rezervace haly, kterou už pokrývá akce z akce.json (stejné datum a název), se
    # nezobrazuje podruhé — akce je potvrzená silnějším zdrojem, rezervace je jen doklad.
    klic_akci = {(a['date'], a['title'].strip().lower()) for a in akce}
    hala = [h for h in hala
            if (h['date'], h['title'].replace(' (nepotvrzeno)', '').strip().lower()) not in klic_akci]
    events = jednani + vybory + akce + volby + afk + svoz + sberny + hala
    sjednot_mista(events)
    events.sort(key=lambda e: (e['date'], e['time'] or ''))

    OUT_JSON.write_text(json.dumps({
        'meta': {
            'generated_from': (f'jednani/pecky-jednani.json ({len(jednani)} jednání), '
                               f'jednani/vybory.json + komise.json + skolska-rada.json ({len(vybory)} jednání výborů, komisí a školské rady), '
                               f'kalendar/akce.json ({len(akce)} akcí), '
                               f'kalendar/udalosti-volby.json ({len(volby)} termínů), '
                               f'kalendar/afk-zapasy.json ({len(afk)} zápasů v Pečkách), '
                               f'kalendar/svoz-odpadu.json ({len(svoz)} svozů), '
                               f'kalendar/sberny-dvur.json ({len(sberny)} termínů provozních dob), '
                               f'kalendar/sportovni-hala.json ({len(hala)} rezervací sportovní haly)'),
            'updated': datetime.now(PRAGUE).strftime('%Y-%m-%d'),
        },
        'org_sources': zdroje_poradatelu(),
        'events': events,
    }, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')

    OUT_ICS.write_text(build_ics(events), encoding='utf-8')

    by_cat, by_org = {}, {}
    for e in events:
        by_cat[e['category']] = by_cat.get(e['category'], 0) + 1
        if e['category'] in ('akce', 'kurz'):
            k = e.get('organizer_name') or 'bez pořadatele'
            by_org[k] = by_org.get(k, 0) + 1
    print(f'Vygenerováno {len(events)} událostí ({", ".join(f"{v} {k}" for k, v in by_cat.items())}) '
          f'-> {OUT_JSON.relative_to(ROOT)}, {OUT_ICS.relative_to(ROOT)}')
    if by_org:
        print('  pořadatelé akcí: ' + ', '.join(f'{v}x {k}' for k, v in sorted(by_org.items())))

    if '--no-sync' in sys.argv:
        print('Synchronizace do Google Kalendáře vynechána (--no-sync).')
    else:
        sync_google()


def sync_google():
    """Hned po vygenerování promítne udalosti.json do Google Kalendáře.

    Od 29. 9. 2026 na pokyn autora webu: generování a synchronizace jsou
    jeden krok, aby Google nezůstával pozadu (předtím se sync ručně
    zapomínal a nahromadilo se přes 1 700 nepropsaných změn). Chybí-li
    klíč nebo knihovna (cloudový checkout, jiný stroj), synchronizaci jen
    přeskočí s varováním — generování tím neselže. Vypnout jde přepínačem
    --no-sync (např. při přegenerování z čistých vstupů v commit skillu).
    """
    import importlib.util
    import subprocess
    key = Path(os.environ.get('PECKY_GOOGLE_KEY', ROOT / '.google-calendar-api-key.json'))
    if not key.exists():
        print(f'!! SYNCHRONIZACE PŘESKOČENA: chybí klíč {key.name} — Google Kalendář zůstává pozadu, '
              'spusť `python3 kalendar/scripts/sync-google.py` na stroji s klíčem a napiš to do shrnutí.')
        return
    if importlib.util.find_spec('googleapiclient') is None:
        print('!! SYNCHRONIZACE PŘESKOČENA: chybí knihovna (pip3 install google-api-python-client google-auth).')
        return
    print('Synchronizuji do Google Kalendáře (kalendar/scripts/sync-google.py)…', flush=True)
    r = subprocess.run([sys.executable, str(ROOT / 'kalendar' / 'scripts' / 'sync-google.py')])
    if r.returncode:
        print(f'!! SYNCHRONIZACE SELHALA (návratový kód {r.returncode}) — udalosti.json je vygenerovaný, '
              'Google Kalendář ne; napiš to do shrnutí.')


if __name__ == '__main__':
    main()
