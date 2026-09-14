#!/usr/bin/env python3
"""Spočítá absenci členů zastupitelstva a rady a zapíše ji do jednani/absence.json.

Postup, který skript implementuje, i zdůvodnění jednotlivých kroků popisuje
jednani/INSTRUKCE-absence.md. Stručně:

- Rada a Zastupitelstvo se počítají zvlášť, uvnitř zvlášť po volebních obdobích.
- Jmenovatel je mandát dané osoby (jednání mezi jejím prvním a posledním
  výskytem v prezenci), ne počet všech jednání období — §2.
- Absence se počítá z úvodní prezence **opravené o zaznamenané příchody**
  (`attendance.changes`); samotná úvodní prezence je jen stav při zahájení
  a bez opravy nadhodnocuje absenci skoro na dvojnásobek — §3.
- Odchody se vykazují zvlášť, do absence se nemíchají — §4.

Použití:
    python3 jednani/scripts/absence.py            # zapíše jednani/absence.json
    python3 jednani/scripts/absence.py --vypsat   # jen vypíše tabulky na terminál
"""
import json
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

KOREN = Path(__file__).resolve().parent.parent.parent
DATA = KOREN / 'jednani' / 'pecky-jednani.json'
VYSTUP = KOREN / 'jednani' / 'absence.json'

# Hranice volebních období = první jednání nového složení orgánu. Zastupitelstvo
# se obměnilo na ustavujícím zasedání 20. 10. 2022 (viz jednani/volebni-obdobi.json),
# rada zvolená na témže zasedání poprvé jednala 31. 10. 2022.
OBDOBI = {
    'Zastupitelstvo': [('2018–2022', '0000-00-00', '2022-10-20'),
                       ('2022–2026', '2022-10-20', '9999-99-99')],
    'Rada': [('2018–2022', '0000-00-00', '2022-10-31'),
             ('2022–2026', '2022-10-31', '9999-99-99')],
}

# Jedna osoba pod dvěma příjmeními — Bc. Iveta Minaříková se v srpnu 2022
# v prezencích mění na Bc. Ivetu Dvořákovou. Normalizace jmen tuhle dvojici
# nespojí, párování je ruční přes lide/people.json (záznam `dvorakovai`).
SLOUCIT = {'iveta minarikova': 'iveta dvorakova'}

# Vadný záznam u zdroje: Rada 27/2021 vede Jiřího Katrnošku zároveň mezi
# přítomnými i nepřítomnými. Surový zápis uvádí, že se účastnil distančně,
# takže se počítá jako přítomný. Viz INSTRUKCE-absence.md §1.
VYRADIT_ABSENCI = {('Rada', '2021-11-22', 'jiri katrnoska')}

# Kontext, který z prezencí vyčíst nejde a bez kterého kratší mandát vypadá
# jako chyba. Zdroj: životopisy v lide/people.json, ověřené proti zápisům
# ustavujícího zasedání a zasedání, na kterých náhradníci složili slib.
POZNAMKY = {
    ('Zastupitelstvo', '2022–2026', 'ondrej schulz'): 'náhradník, slib 26. 2. 2025',
    ('Zastupitelstvo', '2022–2026', 'jaroslava vosecka'): 'náhradnice, slib 11. 9. 2024',
    ('Zastupitelstvo', '2022–2026', 'lenka triskova'): 'mandát skončil 19. 6. 2024',
    ('Zastupitelstvo', '2022–2026', 'iveta dvorakova'): 'mandát skončil 26. 2. 2025; dříve Minaříková',
    ('Rada', '2018–2022', 'blanka kozakova'): 'v radě do 13. 9. 2021',
    ('Rada', '2018–2022', 'viktorie janackova'): 'v radě od 20. 9. 2021',
    ('Rada', '2018–2022', 'iveta dvorakova'): 'dříve Minaříková',
    ('Zastupitelstvo', '2018–2022', 'iveta dvorakova'): 'dříve Minaříková',
}

TITUL = re.compile(r'^(ing|mgr|bc|mudr|judr|phdr|rndr|mga|ph\.?d|csc|dis|msc|doc|prof)\.?,?$', re.I)


def uklidit(jmeno):
    """Verbatim jméno bez nezlomitelných mezer a bez poznámky za pomlčkou."""
    jmeno = jmeno.replace('\xa0', ' ')
    jmeno = re.split(r'\s+-\s+', jmeno)[0]
    return ' '.join(jmeno.split())


def klic(jmeno):
    """Normalizovaný klíč 'jméno příjmení' — protějšek jNameKey() v assets/helpers.js."""
    j = unicodedata.normalize('NFD', uklidit(jmeno))
    j = ''.join(c for c in j if unicodedata.category(c) != 'Mn')
    k = ' '.join(p for p in j.replace(',', ' ').split() if not TITUL.match(p)).lower()
    return SLOUCIT.get(k, k)


def jednani_orgánu(data, typ):
    """Jednání daného orgánu, která mají jmennou prezenci, seřazená podle data."""
    ms = [m for m in data['meetings']
          if m['type'] == typ and (m.get('attendance') or {}).get('present_names')]
    return sorted(ms, key=lambda m: m['date'])


def absence_v_obdobi(typ, jednani):
    osoby = defaultdict(lambda: {
        'pritomen': 0, 'omluven': 0, 'nepritomen': 0, 'dorazil': 0,
        'nebyl': 0, 'odesel': 0, 'od': None, 'do': None, 'jmeno': '', 'jmeno_datum': '',
    })
    for m in jednani:
        a = m['attendance']
        absentni = [x for x in (a.get('absent_names') or [])
                    if (typ, m['date'], klic(x['name'])) not in VYRADIT_ABSENCI]
        zmeny = a.get('changes') or []
        # Příchod započítat jako opravu jen u toho, kdo v úvodní prezenci chybí —
        # kdo během jednání odejde a vrátí se, má příchod taky (§3).
        prisli = {klic(z['name']) for z in zmeny if z['event'] in ('přišel', 'distančně')}
        odesli = {klic(z['name']) for z in zmeny if z['event'] == 'odešel'}

        for jmeno in a['present_names'] + [x['name'] for x in absentni]:
            o = osoby[klic(jmeno)]
            if m['date'] >= o['jmeno_datum']:      # ve výpisu novější tvar jména
                o['jmeno'], o['jmeno_datum'] = uklidit(jmeno), m['date']
            o['od'] = o['od'] or m['date']
            o['do'] = m['date']

        for jmeno in a['present_names']:
            o = osoby[klic(jmeno)]
            o['pritomen'] += 1
            if klic(jmeno) in odesli:
                o['odesel'] += 1

        for x in absentni:
            o = osoby[klic(x['name'])]
            o['omluven' if x['note'] == 'omluven' else 'nepritomen'] += 1
            if klic(x['name']) in prisli:
                o['dorazil'] += 1
            else:
                o['nebyl'] += 1

    radky = []
    for k, o in osoby.items():
        mandat = sum(1 for m in jednani if o['od'] <= m['date'] <= o['do'])
        radky.append({
            'klic': k,
            'jmeno': o['jmeno'],
            'mandat': mandat,
            'chybel': o['omluven'] + o['nepritomen'],
            'omluven': o['omluven'],
            'nepritomen': o['nepritomen'],
            'dorazil': o['dorazil'],
            'nebyl': o['nebyl'],
            'podil': round(100 * o['nebyl'] / mandat, 1),
            'odesel': o['odesel'],
            'mandat_od': o['od'],
            'mandat_do': o['do'],
        })
    # Nahoře nejkratší mandáty — právě u nich procento klame nejvíc (§4).
    radky.sort(key=lambda r: (r['mandat'], -r['nebyl'], r['jmeno']))
    return radky


def kontrola(typ, obdobi, jednani, radky):
    """Součet absencí přes osoby se musí rovnat součtu (total − present) přes
    jednání; rozdíl smí zůstat jen tam, kde ho vysvětluje vadný záznam (§1, §7)."""
    pres_osoby = sum(r['chybel'] for r in radky)
    pres_jednani = sum(m['attendance']['total'] - m['attendance']['present'] for m in jednani)
    vadne = []
    for m in jednani:
        a = m['attendance']
        if len(a['present_names']) != a['present'] or \
                len(a['present_names']) + len(a.get('absent_names') or []) != a['total']:
            vadne.append(f"{m['type']} {m['label']}")
    return {
        'soucet_pres_osoby': pres_osoby,
        'soucet_pres_jednani': pres_jednani,
        'rozdil': pres_osoby - pres_jednani,
        'vadne_zaznamy': vadne,
    }


def main(vypsat_jen):
    data = json.load(open(DATA, encoding='utf-8'))
    vysledek = {'meta': {}, 'obdobi': []}
    vsechna = []

    for typ, obdobi_seznam in OBDOBI.items():
        ms = jednani_orgánu(data, typ)
        vsechna += ms
        for nazev, od, do in obdobi_seznam:
            vyber = [m for m in ms if od <= m['date'] < do]
            if not vyber:
                continue
            radky = absence_v_obdobi(typ, vyber)
            for r in radky:
                p = POZNAMKY.get((typ, nazev, r['klic']))
                if p:
                    r['poznamka'] = p
            vysledek['obdobi'].append({
                'organ': typ,
                'obdobi': nazev,
                'jednani': len(vyber),
                'od': vyber[0]['date'],
                'do': vyber[-1]['date'],
                'radky': radky,
                'kontrola': kontrola(typ, nazev, vyber, radky),
            })

    s_prubeznou = [m for m in vsechna if (m.get('attendance') or {}).get('changes')]
    vysledek['meta'] = {
        'popis': 'Absence členů zastupitelstva a rady města Pečky, spočítaná z jmenné '
                 'prezence v zápisech na usneseni.cz. Postup: jednani/INSTRUKCE-absence.md.',
        'generoval': 'jednani/scripts/absence.py',
        'zdroj': 'jednani/pecky-jednani.json',
        'jednani_celkem': len(vsechna),
        'jednani_s_prubeznou_prezenci': len(s_prubeznou),
        'data_do': max(m['date'] for m in vsechna),
    }

    if vypsat_jen:
        for blok in vysledek['obdobi']:
            print(f"\n### {blok['organ']} {blok['obdobi']} — {blok['jednani']} jednání "
                  f"({blok['od']} … {blok['do']})  kontrola: {blok['kontrola']['rozdil']:+d}")
            for r in blok['radky']:
                print(f"{r['jmeno']:30}{r['mandat']:5}{r['chybel']:5}{r['dorazil']:5}"
                      f"{r['nebyl']:5}{r['podil']:7}%{r['odesel']:5}  {r.get('poznamka','')}")
        return

    VYSTUP.write_text(json.dumps(vysledek, ensure_ascii=False, indent=2) + '\n',
                      encoding='utf-8')
    print(f"Zapsáno do {VYSTUP.relative_to(KOREN)} — "
          f"{len(vysledek['obdobi'])} bloků, "
          f"{sum(len(b['radky']) for b in vysledek['obdobi'])} řádků.")
    for blok in vysledek['obdobi']:
        k = blok['kontrola']
        stav = 'OK' if k['rozdil'] == 0 else f"ROZDÍL {k['rozdil']:+d}"
        vadne = f" (vadné záznamy: {', '.join(k['vadne_zaznamy'])})" if k['vadne_zaznamy'] else ''
        print(f"  {blok['organ']:14} {blok['obdobi']}  {stav}{vadne}")


if __name__ == '__main__':
    main('--vypsat' in sys.argv)
