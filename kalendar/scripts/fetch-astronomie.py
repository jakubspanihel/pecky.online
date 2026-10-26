#!/usr/bin/env python3
"""Stáhne úplňky a začátky ročních období z kalendar.beda.cz do kalendar/astronomie.json.

Jednorázový skript (rozsah se dá prodloužit přepsáním konstant níže):
- úplňky: https://kalendar.beda.cz/mesicni-faze-v-roce?year=RRRR (jedna tabulka
  na rok, úplněk je v buňkách s ikonou moonFM.png),
- rovnodennosti a slunovraty: https://kalendar.beda.cz/kdy-zacina-jaro-leto-podzim-zima
  (jedna tabulka pro všechny roky).

Časy na obou stránkách jsou místní (SEČ/SELČ), tak se zapisují i sem.
Do souboru jdou jen termíny od FROM; řádek aktuálního roku má v tabulce
`<tr class='current'>`, parser s tím počítá.

Stránky se předem stáhnou obyčejným `curl` (web odmítá klienty s upraveným
User-Agentem, ten se proto nemění) do jednoho adresáře:

    for r in $(seq 2026 2036); do curl -sL "https://kalendar.beda.cz/mesicni-faze-v-roce?year=$r" -o DIR/faze-$r.html; done
    curl -sL https://kalendar.beda.cz/kdy-zacina-jaro-leto-podzim-zima -o DIR/obdobi.html
    python3 kalendar/scripts/fetch-astronomie.py DIR

Po spuštění: python3 kalendar/scripts/update-kalendar.py a python3 scripts/build.py.
"""
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
OUT = ROOT / 'kalendar' / 'astronomie.json'

FROM = '2026-10-26'          # první den, který se zapisuje (úplněk 26. 10. 2026 v 05:12)
UPLNKY_DO = '2036-10-26'     # 10 let dopředu
OBDOBI_DO_ROK = 2032         # rovnodennosti a slunovraty včetně roku 2032

URL_FAZE = 'https://kalendar.beda.cz/mesicni-faze-v-roce?year={rok}'
URL_OBDOBI = 'https://kalendar.beda.cz/kdy-zacina-jaro-leto-podzim-zima'

MESICE = ['Leden', 'Únor', 'Březen', 'Duben', 'Květen', 'Červen', 'Červenec',
          'Srpen', 'Září', 'Říjen', 'Listopad', 'Prosinec']
OBDOBI = [  # pořadí sloupců v tabulce
    ('jaro', 'Jarní rovnodennost', 'rovnodennost'),
    ('leto', 'Letní slunovrat', 'slunovrat'),
    ('podzim', 'Podzimní rovnodennost', 'rovnodennost'),
    ('zima', 'Zimní slunovrat', 'slunovrat'),
]
MES_OBDOBI = {'březen': 3, 'červen': 6, 'září': 9, 'prosinec': 12}


CACHE = None   # adresář se staženými stránkami (argument skriptu)


def stahni(jmeno):
    """Vrátí HTML stránky uložené v CACHE (faze-RRRR.html, obdobi.html)."""
    return (CACHE / jmeno).read_text(encoding='utf-8')


def uplnky(rok):
    html = stahni(f'faze-{rok}.html')
    out = []
    for radek in re.findall(r"<tr[^>]*><td class='right'>(.*?)</tr>", html, re.S):
        mesic = MESICE.index(radek.split('</td>')[0]) + 1
        for den, cas in re.findall(r"moonFM\.png.*?<strong>(?:&nbsp;)*(\d+)\.</strong>\s*(\d\d:\d\d)", radek):
            out.append((f'{rok}-{mesic:02d}-{int(den):02d}', cas))
    return out


def obdobi():
    html = stahni('obdobi.html')
    out = []
    for rok, radek in re.findall(r'<tr[^>]*><td>(\d{4})</td>(.*?)</tr>', html, re.S):
        bunky = re.findall(r'(\d+)\.&nbsp;(\w+)</a> (\d\d:\d\d)', radek)
        if len(bunky) != 4:
            continue
        for (klic, nazev, druh), (den, mesic, cas) in zip(OBDOBI, bunky):
            out.append((int(rok), klic, nazev, druh,
                        f'{rok}-{MES_OBDOBI[mesic]:02d}-{int(den):02d}', cas))
    return out


def main():
    global CACHE
    if len(sys.argv) != 2:
        sys.exit('Použití: fetch-astronomie.py ADRESAR_SE_STAZENYMI_STRANKAMI')
    CACHE = Path(sys.argv[1])
    events = []
    for rok in range(int(FROM[:4]), int(UPLNKY_DO[:4]) + 1):
        for d, cas in uplnky(rok):
            if FROM <= d <= UPLNKY_DO:
                events.append({'id': f'astronomie-uplnek-{d}', 'title': 'Úplněk', 'type': 'uplnek',
                               'date': d, 'time': cas, 'source': 'faze'})
    for rok, klic, nazev, druh, d, cas in obdobi():
        if FROM <= d and rok <= OBDOBI_DO_ROK:
            events.append({'id': f'astronomie-{klic}-{d}', 'title': nazev, 'type': druh,
                           'date': d, 'time': cas, 'source': 'obdobi'})
    events = list({e['id']: e for e in events}.values())   # tabulka období je na stránce dvakrát
    events.sort(key=lambda e: (e['date'], e['time']))
    dnes = date.today().isoformat()
    data = {
        'meta': {
            'description': ('Astronomické úkazy: úplňky (10 let dopředu) a začátky ročních období, '
                            'tedy rovnodennosti a slunovraty (do roku 2032). Časy jsou místní (SEČ/SELČ). '
                            'Zdroj: kalendar.beda.cz. Do kalendáře je promítá kalendar/scripts/update-kalendar.py; '
                            'soubor vzniká skriptem kalendar/scripts/fetch-astronomie.py.'),
            'organizer': 'vesmir',
            'category': 'astronomie',
            'from': FROM,
            'uplnky_do': UPLNKY_DO,
            'obdobi_do': f'{OBDOBI_DO_ROK}-12-31',
            'updated': dnes,
            'evidence': {
                'faze': {'source': 'kalendar-beda', 'kind': 'web',
                         'url': 'https://kalendar.beda.cz/mesicni-faze-v-roce',
                         'label': 'Měsíční fáze v roce (Kalendář Beda)',
                         'published': None, 'retrieved': dnes},
                'obdobi': {'source': 'kalendar-beda', 'kind': 'web',
                           'url': URL_OBDOBI,
                           'label': 'Kdy začíná jaro, léto, podzim, zima (Kalendář Beda)',
                           'published': None, 'retrieved': dnes},
            },
        },
        'events': events,
    }
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    n_u = sum(e['type'] == 'uplnek' for e in events)
    print(f'{OUT.relative_to(ROOT)}: {n_u} úplňků, {len(events) - n_u} rovnodenností a slunovratů')


if __name__ == '__main__':
    main()
