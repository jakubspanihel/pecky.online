#!/usr/bin/env python3
"""Doplní do jednani/pecky-jednani.json pole attendance.changes — příchody,
odchody a distanční připojení zaznamenané v průběhu jednání.

Zdroj: minutes.full_text ve velkém archive-*.json. Zápis vede vedle úvodní
prezence i každou změnu během jednání ("V 15:45:53 přišel Ing. Petr Dürr,
přítomno 7 z 7 radních."); bez těchhle vět vypadá pozdní příchod jako
celodenní absence. Viz jednani/INSTRUKCE-absence.md §3.

Jednání novější než snímek archivu skript neumí — ta se doplňují ručně
podle jednani/automation-kontrola-usneseni-cz.md, krok 4.

Použití:
    python3 jednani/scripts/doplnit-prubeznou-prezenci.py \
        jednani/archive-2026-08-04.json jednani/pecky-jednani.json [--zapsat]

Bez --zapsat jen vypíše, co by se změnilo.
"""
import json, re, sys, unicodedata

UDALOST = re.compile(
    r'V (\d{1,2}:\d{2}:\d{2}) '
    r'(přišel|přišla|odešel|odešla|se zúčastnil distančně|se zúčastnila distančně) '
    r'(.+?), přítomno (\d+)(?: z (\d+))? (?:zastupitelů|radních)\.'
)
UDALOST_ALT = re.compile(
    r'V (\d{1,2}:\d{2}:\d{2}) se (zúčastnil|zúčastnila) distančně '
    r'(.+?), přítomno (\d+)(?: z (\d+))? (?:zastupitelů|radních)\.'
)
NAZEV = {'přišel': 'přišel', 'přišla': 'přišel', 'odešel': 'odešel',
         'odešla': 'odešel', 'zúčastnil': 'distančně', 'zúčastnila': 'distančně',
         'se zúčastnil distančně': 'distančně',
         'se zúčastnila distančně': 'distančně'}

TITUL = re.compile(r'^(ing|mgr|bc|mudr|judr|phdr|rndr|mga|ph\.?d|csc|dis|msc|doc|prof)\.?,?$', re.I)


def uklidit(jmeno):
    """Verbatim jméno ze zápisu bez nezlomitelných mezer a bez poznámky
    přilepené za pomlčku (viz INSTRUKCE-absence.md §5)."""
    jmeno = jmeno.replace('\xa0', ' ')
    jmeno = re.split(r'\s+-\s+', jmeno)[0]
    return ' '.join(jmeno.split())


def klic(jmeno):
    """Normalizovaný klíč 'jméno příjmení' — protějšek jNameKey() v assets/helpers.js."""
    j = uklidit(jmeno)
    j = unicodedata.normalize('NFD', j)
    j = ''.join(c for c in j if unicodedata.category(c) != 'Mn')
    return ' '.join(p for p in j.replace(',', ' ').split() if not TITUL.match(p)).lower()


def zmeny_ze_zapisu(full_text):
    """Seznam změn prezence seřazený podle času, bez duplicit."""
    nalezy = {}
    for regex in (UDALOST, UDALOST_ALT):
        for cas, sloveso, jmeno, po, celkem in regex.findall(full_text or ''):
            zaznam = {
                'time': cas,
                'event': NAZEV[sloveso],
                'name': uklidit(jmeno),
                'present_after': int(po),
            }
            nalezy[(cas, zaznam['event'], klic(zaznam['name']))] = zaznam
    return [nalezy[k] for k in sorted(nalezy, key=lambda k: k[0])]


def main(cesta_archiv, cesta_data, zapsat):
    archiv = json.load(open(cesta_archiv, encoding='utf-8'))
    data = json.load(open(cesta_data, encoding='utf-8'))

    ze_zapisu = {}
    for m in archiv['meetings']:
        zmeny = zmeny_ze_zapisu((m.get('minutes') or {}).get('full_text'))
        if zmeny:
            ze_zapisu[m['uuid']] = zmeny

    doplneno = prepsano = 0
    bez_pokryti = []
    for m in data['meetings']:
        att = m.get('attendance')
        if not att or not att.get('present_names'):
            continue
        if m['uuid'] not in ze_zapisu:
            if m['uuid'] not in {x['uuid'] for x in archiv['meetings']}:
                bez_pokryti.append(f"{m['type']} {m['label']} ({m['date']})")
            continue
        nove = ze_zapisu[m['uuid']]
        if att.get('changes') == nove:
            continue
        if 'changes' in att:
            prepsano += 1
        else:
            doplneno += 1
        att['changes'] = nove
        print(f"{m['date']}  {m['type']:14} {m['label']:22} {len(nove)} změn: "
              + ', '.join(f"{z['time']} {z['event']} {z['name']}" for z in nove[:3])
              + (' …' if len(nove) > 3 else ''))

    print(f"\nDoplněno {doplneno} jednání, přepsáno {prepsano}.")
    if bez_pokryti:
        print(f"Mimo snímek archivu ({len(bez_pokryti)}) — doplnit ručně podle "
              f"automation-kontrola-usneseni-cz.md, krok 4:")
        for x in bez_pokryti:
            print('   ' + x)

    if not zapsat:
        print("\nZkušební běh, nic se nezapsalo. Spusť znovu s --zapsat.")
        return
    # Bez zálohy vedle dat — repozitář je v gitu, `git diff` / `git checkout`
    # je spolehlivější a nezanáší do složky sekce soubory navíc.
    with open(cesta_data, 'w', encoding='utf-8') as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    print(f"\nZapsáno do {cesta_data}. Změny zkontroluj přes `git diff` —"
          f" v diffu smí přibýt jen bloky `changes`.")


if __name__ == '__main__':
    argv = [a for a in sys.argv[1:] if a != '--zapsat']
    if len(argv) != 2:
        sys.exit(__doc__)
    main(argv[0], argv[1], '--zapsat' in sys.argv)
