#!/usr/bin/env python3
"""
Generátor sekce Prostory (content/prostory.html, /prostory/).

Zdroj: prostory/prostory.json (ručně vedený seznam prostorů; každá událost
odkazuje na usnesení rady přes jeho číslo `n` a/nebo na dokument úřední desky
přes `deska`) + jednani/pecky-jednani.json (datum a typ jednání, ze kterých se
dopočítá odkaz /jednani/#rada-RRRR-MM-DD) + o-webu/uredni-deska-monitoring/
<rok>.txt (datum vyvěšení a sejmutí, odkaz na detail dokumentu).

`deska` = číselné id dokumentu na pecky.cz (např. 382845) nebo `as4u:<id>`
(starý web). Událost s `n` i `deska` je záměr schválený radou a vyvěšený na
desce; událost jen s `deska` je záměr, ke kterému usnesení v datech není.

Přepíše jen část content/prostory.html mezi značkami
<!-- PROSTORY:START --> a <!-- PROSTORY:END -->. Perex a calloutu kolem nich
jsou psané ručně. Po běhu vždy spustit `python3 scripts/build.py`.

Použití: python3 prostory/update-prostory.py
"""
import json
import re
import sys
from datetime import date
from html import escape as esc
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
START, END = '<!-- PROSTORY:START -->', '<!-- PROSTORY:END -->'

ICO_KAL = ('<svg class="kal-ico" viewBox="0 0 16 16" width="16" height="16" fill="none" stroke="currentColor" '
           'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
           '<rect x="2" y="3" width="12" height="11" rx="1.5"/><path d="M2 6.5h12M5 1.5v3M11 1.5v3"/></svg>')
ICO_PIN = ('<svg class="kal-ico" viewBox="0 0 16 16" width="16" height="16" fill="none" stroke="currentColor" '
           'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
           '<path d="M8 14.5s4.5-4.2 4.5-7.8a4.5 4.5 0 0 0-9 0C3.5 10.3 8 14.5 8 14.5z"/><circle cx="8" cy="6.7" r="1.6"/></svg>')

# pořadí skupin v přehledu a CSS třída štítku stavu
STAV = {
    'zamer':     (0, 'tag probiha'),
    'volne':     (1, 'tag papir'),
    'pronajato': (2, 'tag hotovo'),
    'vypujceno': (3, 'tag hotovo'),
    'ukonceno':  (4, 'tag'),
    'neznamy':   (5, 'tag'),
}
TYP_TAG = {
    'zamer': 'tag probiha', 'zamer_vyp': 'tag probiha', 'smlouva': 'tag hotovo',
    'vypujcka': 'tag hotovo', 'dodatek': 'tag papir', 'ukonceni': 'tag zamitnuto',
    'podnajem': 'tag papir',
}


def cz(iso):
    y, m, d = iso.split('-')
    return f'{int(d)}. {int(m)}. {y}'


def load_resolutions():
    """n -> (datum jednání, id jednání v /jednani/)"""
    meetings = json.loads((ROOT / 'jednani/pecky-jednani.json').read_text(encoding='utf-8'))['meetings']
    out = {}
    for m in meetings:
        prefix = 'zastupitelstvo' if m['type'] == 'Zastupitelstvo' else 'rada'
        for r in m['resolutions']:
            out[r['n']] = (m['date'], f'{prefix}-{m["date"]}')
    return out


def load_deska():
    """id (číslo nebo as4u:<id>) -> dict(vyveseno, sejmuto, typ, nazev, url)"""
    out = {}
    for f in sorted((ROOT / 'o-webu/uredni-deska-monitoring').glob('[0-9][0-9][0-9][0-9].txt')):
        for line in f.read_text(encoding='utf-8').splitlines():
            if not line or line.startswith('#') or '|' not in line:
                continue
            parts = line.split('|')
            if len(parts) < 5:
                continue
            slug, vyv, sej, typ, nazev = parts[0], parts[1], parts[2], parts[3], '|'.join(parts[4:])
            d, m, y = vyv.split('.')
            if slug.startswith('as4u:'):
                key = slug
                url = ('https://pecky.as4u.cz/redakce/index.php?lanG=cs&clanek=106922&slozka=106925'
                       f'&detail_claim={slug[5:]}')
            else:
                key = slug.split('_')[0]
                url = f'https://pecky.cz/default/report/{slug}'
            iso = f'{y}-{m}-{d}'
            sej_iso = None
            if re.fullmatch(r'\d\d\.\d\d\.\d{4}', sej):
                sd, sm, sy = sej.split('.')
                sej_iso = f'{sy}-{sm}-{sd}'
            out[key] = {'vyveseno': iso, 'sejmuto': sej_iso, 'typ': typ, 'nazev': nazev, 'url': url}
    return out


def usn_link(n, hash_id):
    return f'<span class="tag"><a href="/jednani/#{hash_id}">{esc(n)}</a></span>'


def deska_link(dk):
    vyv = cz(dk['vyveseno'])
    sej = f' – {cz(dk["sejmuto"])}' if dk.get('sejmuto') else ''
    return (f'<span class="tag"><a href="{esc(dk["url"])}" target="_blank" rel="noopener" '
            f'title="Úřední deska: vyvěšeno {vyv}{sej}">úřední deska</a></span>')


def odkazy(e):
    out = []
    if e.get('n'):
        out.append(usn_link(e['n'], e['hash']))
    if e.get('dk'):
        out.append(deska_link(e['dk']))
    return '<br>'.join(out)


def render(data, res, desky, dnes):
    typy = data['typy']
    prem = data['premises']
    problems = []
    for p in prem:
        evs = []
        for e in p['events']:
            if e['typ'] not in typy:
                problems.append(f'{p["id"]}: neznámý typ {e["typ"]}')
            if not e.get('n') and not e.get('deska'):
                problems.append(f'{p["id"]}: událost nemá ani n, ani deska')
                continue
            d = hid = None
            if e.get('n'):
                if e['n'] not in res:
                    problems.append(f'{p["id"]}: usnesení {e["n"]} není v pecky-jednani.json')
                    continue
                d, hid = res[e['n']]
            dk = None
            if e.get('deska'):
                dk = desky.get(e['deska'])
                if not dk:
                    problems.append(f'{p["id"]}: dokument úřední desky {e["deska"]} není v seznamech <rok>.txt')
                    continue
                if d is None:
                    d = dk['vyveseno']
                elif not (-1 <= (date.fromisoformat(dk['vyveseno']) - date.fromisoformat(d)).days <= 21):
                    print(f'POZOR: {p["id"]} {e["n"]}: vyvěšeno {dk["vyveseno"]}, usnesení {d} — zkontrolovat spárování')
            evs.append({**e, 'date': d, 'hash': hid, 'dk': dk})
        evs.sort(key=lambda x: (x['date'], x.get('n') or x.get('deska')), reverse=True)
        p['_ev'] = evs
        if p['stav'] not in STAV:
            problems.append(f'{p["id"]}: neznámý stav {p["stav"]}')
    if problems:
        sys.exit('CHYBA:\n  ' + '\n  '.join(problems))

    prem = sorted(prem, key=lambda p: p['_ev'][0]['date'], reverse=True)  # podle data posledního usnesení/záměru, nejnovější nahoře
    out = []

    # --- banner: právě vyhlášené záměry
    aktivni = [p for p in prem if p['stav'] == 'zamer' and p.get('uzaverka', '') >= dnes]
    for p in aktivni:
        ev = next((e for e in p['_ev'] if e['typ'] == 'zamer' and e.get('n')), p['_ev'][0])
        kdy = f'{cz(p["uzaverka"])}' + (f' v {p["uzaverka_cas"]}' if p.get('uzaverka_cas') else '')
        out.append(
            '<aside class="banner" aria-label="Právě vyhlášený záměr pronájmu">'
            '<div class="banner-body">'
            f'<h3 class="banner-title">Záměr pronájmu: {esc(p["nazev"].lower())}</h3>'
            f'<p class="banner-meta"><span class="banner-meta-item">{ICO_PIN}<span>{esc(p["budova"])}, {esc(p["plocha"])}</span></span>'
            f'<span class="banner-meta-item">{ICO_KAL}<span>Nabídky nejpozději do {esc(kdy)} '
            f'<span class="tag probiha fut-chip" data-date="{p["uzaverka"]}">plánováno</span></span></span></p>'
            f'<p class="banner-text">{esc(p["podminky"][0].upper() + p["podminky"][1:])}.'
            + (f' {esc(p["nabidka"])}' if p.get('nabidka') else '') + '</p>'
            f'<div class="banner-actions"><a class="banner-cta" href="/jednani/#{ev["hash"]}">Usnesení rady {esc(ev["n"])}</a>'
            + (f'<a class="banner-link" href="{esc(ev["dk"]["url"])}" target="_blank" rel="noopener">Záměr na úřední desce</a>' if ev.get('dk') else '')
            + f'<a class="banner-link" href="#prostor-{p["id"]}">Historie prostoru</a></div>'
            '</div></aside>')

    # --- souhrn
    pocty = {k: sum(1 for p in prem if p['stav'] == k) for k in STAV}
    obsazeno = pocty['pronajato'] + pocty['vypujceno']
    budovy = len({p['budova'] for p in prem})
    out.append(
        '<div class="stat-grid">'
        f'<div class="stat-card"><div class="stat-num">{len(prem)}</div><div class="stat-label">prostorů v přehledu<br>v {budovy} objektech</div></div>'
        f'<div class="stat-card"><div class="stat-num">{pocty["zamer"]}</div><div class="stat-label">se zveřejněným záměrem<br>nabídky se ještě přijímají</div></div>'
        f'<div class="stat-card"><div class="stat-num">{obsazeno}</div><div class="stat-label">pronajato nebo vypůjčeno<br>podle posledního usnesení</div></div>'
        f'<div class="stat-card"><div class="stat-num">{pocty["volne"] + pocty["ukonceno"] + pocty["neznamy"]}</div><div class="stat-label">bez nájemce<br>nebo bez známého výsledku záměru</div></div>'
        '</div>')

    # --- přehledová tabulka; historie prostoru se rozbaluje pod řádkem
    out.append('<h3 class="display" style="margin:30px 0 4px;">Přehled prostorů</h3>')
    out.append('<p class="meta-note">Kliknutím na řádek se pod ním zobrazí všechna nalezená usnesení rady a záměry z úřední desky k danému prostoru, od nejnovějšího.</p>')
    out.append('<div class="table-scroll"><table class="register prostory-tabulka">'
               '<thead><tr><th>Prostor</th><th>Plocha</th><th>Forma</th><th>Stav</th><th>Podmínky</th><th>Poslední usnesení</th></tr></thead><tbody>')
    for p in prem:
        cls = STAV[p['stav']][1]
        stav = f'<span class="{cls}">{esc(p["stav_text"])}</span>'
        if p['stav'] == 'zamer' and p.get('uzaverka', '') >= dnes:
            stav += f' <span class="tag probiha fut-chip" data-date="{p["uzaverka"]}">plánováno</span>'
        najemce = f'<br><span class="muted-note">{esc(p["najemce"])}</span>' if p.get('najemce') else ''
        e0 = p['_ev'][0]
        out.append(
            f'<tr class="prostor-row" id="prostor-{p["id"]}" tabindex="0" role="button" aria-expanded="false" aria-controls="prostor-{p["id"]}-detail">'
            f'<td><span class="prostor-toggle" aria-hidden="true">+</span><strong>{esc(p["nazev"])}</strong>'
            f'<span class="muted-note prostor-budova">{esc(p["budova"])}</span></td>'
            f'<td style="white-space:nowrap;">{esc(p["plocha"])}</td><td>{esc(p["forma"])}</td>'
            f'<td>{stav}{najemce}</td><td>{esc(p["podminky"])}</td>'
            f'<td style="white-space:nowrap;">{cz(e0["date"])}<br>{odkazy(e0)}</td></tr>')
        det = []
        if p.get('poznamka_stav'):
            det.append(f'<p class="meta-note">{esc(p["poznamka_stav"])}</p>')
        det.append('<div class="table-scroll"><table class="register"><thead><tr><th>Datum</th><th>Co se stalo</th><th>Zdroj</th></tr></thead><tbody>')
        for e in p['_ev']:
            det.append(
                f'<tr><td style="white-space:nowrap;">{cz(e["date"])}</td>'
                f'<td><span class="{TYP_TAG[e["typ"]]}">{esc(typy[e["typ"]])}</span> {esc(e["pozn"])}'
                + (f' <span class="muted-note">(na desce {cz(e["dk"]["vyveseno"])}–{cz(e["dk"]["sejmuto"])})</span>' if e.get('dk') and e['dk'].get('sejmuto') else '')
                + '</td>'
                f'<td style="white-space:nowrap;">{odkazy(e)}</td></tr>')
        det.append('</tbody></table></div>')
        out.append(f'<tr class="prostor-detail" id="prostor-{p["id"]}-detail" hidden><td colspan="6">' + ''.join(det) + '</td></tr>')
    out.append('</tbody></table></div>')
    return '\n'.join(out)


def main():
    data = json.loads((ROOT / 'prostory/prostory.json').read_text(encoding='utf-8'))
    dnes = date.today().isoformat()
    html = render(data, load_resolutions(), load_deska(), dnes)
    path = ROOT / 'content/prostory.html'
    text = path.read_text(encoding='utf-8')
    if START not in text or END not in text:
        sys.exit(f'CHYBA: v {path.name} chybí značky {START} / {END}.')
    head, rest = text.split(START, 1)
    _, tail = rest.split(END, 1)
    path.write_text(f'{head}{START}\n{html}\n{END}{tail}', encoding='utf-8')
    print(f'content/prostory.html: {len(data["premises"])} prostorů, '
          f'{sum(len(p["events"]) for p in data["premises"])} událostí.')


if __name__ == '__main__':
    main()
