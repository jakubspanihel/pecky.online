#!/usr/bin/env python3
"""Vygeneruje content/dotace.html (stránka „Dotace od města“) z dotace/dotace.json.

Spouštět z kořene repa, potom `python3 scripts/build.py`.
Sloupcový graf je statické SVG (bez knihoven); barvy příjemců s organizací
v lide/organizations.json berou proměnnou --org-<id> (generuje build),
ostatní mají barvu v poli `barva` v dotace.json (proměnná z assets/styles.css).
"""
import json
from collections import defaultdict
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = json.loads((ROOT / 'dotace/dotace.json').read_text(encoding='utf-8'))
P = DOC['prijemci']
NBSP = ' '

MESICE = ['', 'ledna', 'února', 'března', 'dubna', 'května', 'června', 'července',
          'srpna', 'září', 'října', 'listopadu', 'prosince']
YEARS = list(range(2016, 2027))

# pořadí a seskupení segmentů grafu (zdola nahoru)
SERIES = ['tj-sokol-pecky', 'afk-pecky', 'tj-spartak-pecky', 'oddil-vodni-turistiky',
          'zimni-turisti', 'dc-glow', 'szm-pecky', 'ostatni']
OSTATNI_COLOR = 'color-mix(in srgb, var(--ink-soft) 40%, var(--white))'
INV_ID = 'tj-sokol-pecky'


def kc(v, plus=False):
    s = f'{abs(round(v)):,}'.replace(',', NBSP)
    if round(v) != v:
        s = f'{abs(v):,.2f}'.replace(',', NBSP).replace('.', ',')
    return ('+' if plus and v > 0 else '') + s + NBSP + 'Kč'


def mil(v):
    return f'{v / 1_000_000:.2f}'.replace('.', ',') + NBSP + 'mil.'


def datum(iso):
    y, m, d = iso.split('-')
    return f'{int(d)}. {int(m)}. {y}'


def barva(pid):
    if pid == 'ostatni':
        return OSTATNI_COLOR
    p = P[pid]
    return f'var(--org-{p["org"]}, var(--ink-soft))' if p.get('org') and not p.get('barva') else p['barva']


def jednani_odkaz(j):
    typ = 'zastupitelstvo' if j['typ'] == 'Zastupitelstvo' else 'rada'
    return f'<a href="/jednani/#{typ}-{j["datum"]}">{escape(j["text"])}</a>'


# ---- agregace -------------------------------------------------------
cells = defaultdict(lambda: defaultdict(float))     # [rok][série] -> Kč
inv = defaultdict(float)                            # investiční dotace (Sokol) po letech
detail = defaultdict(lambda: defaultdict(list))     # [rok][série] -> řádky do tooltipu
for s in DOC['smlouvy']:
    sid = s['prijemce'] if s['prijemce'] in SERIES else 'ostatni'
    if s.get('investicni'):
        inv[s['rok']] += s['castka']
        detail[s['rok']]['inv'].append(f'{P[s["prijemce"]]["nazev"]} – investiční dotace: {kc(s["castka"])}')
    else:
        cells[s['rok']][sid] += s['castka']
        detail[s['rok']][sid].append(f'{P[s["prijemce"]]["nazev"]}: {kc(s["castka"])}')
for d in DOC['dodatky']:
    if d['typ'] != 'navyseni':
        continue
    sid = d['prijemce'] if d['prijemce'] in SERIES else 'ostatni'
    cells[d['rok']][sid] += d['castka']
    detail[d['rok']][sid].append(f'{P[d["prijemce"]]["nazev"]} – dodatek č. {d["dodatek"]} ke smlouvě č. {d["smlouva"]}: {kc(d["castka"], True)}')

total_by_year = {y: sum(cells[y].values()) + inv[y] for y in YEARS}
celkem = sum(total_by_year.values())
n_smlouvy, n_dodatky = len(DOC['smlouvy']), len(DOC['dodatky'])
n_prijemci = len({s['prijemce'] for s in DOC['smlouvy']})
POSLEDNI = max(YEARS)
s_posl = [s for s in DOC['smlouvy'] if s['rok'] == POSLEDNI]
n_posl, n_prijemci_posl = len(s_posl), len({s['prijemce'] for s in s_posl})
top_posl = max(s_posl, key=lambda s: s['castka'])
navyseni = [d for d in DOC['dodatky'] if d['typ'] == 'navyseni']

# ---- podíl na výdajích města -----------------------------------------
ROZ = DOC['rozpocet']['mil_kc']
roky_podil = [y for y in YEARS if y != 2017 and y != POSLEDNI]       # 2017 bez smluv, poslední rok neuzavřený
inv_celkem = sum(inv.values())
podil_prumer = (sum(total_by_year[y] for y in roky_podil) - inv_celkem) / (sum(ROZ[str(y)][1] for y in roky_podil) * 1e6) * 100
def pct(v):
    return f'{v:.2f}'.replace('.', ',') + '\u00a0%'
PODIL = f'{podil_prumer:.1f}'.replace('.', ',')

# ---- graf -----------------------------------------------------------
W, H = 960, 380
X0, X1, Y0, Y1 = 56, 950, 24, 316        # plocha grafu
YMAX = 5_000_000
slot = (X1 - X0) / len(YEARS)
bw = 46


def ypos(v):
    return Y1 - (Y1 - Y0) * v / YMAX


svg = [f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-labelledby="dot-t dot-d">',
       '<title id="dot-t">Dotace města Pečky podle let a příjemců</title>',
       f'<desc id="dot-d">Skládaný sloupcový graf: osa x roky 2016 až 2026, osa y součet dotací ze smluv a dodatků v Kč. '
       f'Nejvyšší sloupec je rok 2019 ({kc(total_by_year[2019])}), z toho investiční dotace TJ Sokol Pečky '
       f'{kc(inv[2019])}. V roce 2017 není na úřední desce žádná smlouva.</desc>',
       '<defs><pattern id="dot-hatch" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
       '<rect width="7" height="7" fill="none"/><line x1="0" y1="0" x2="0" y2="7" stroke="var(--white)" stroke-width="3" stroke-opacity="0.55"/></pattern></defs>']
for t in range(0, YMAX + 1, 1_000_000):
    y = ypos(t)
    svg.append(f'<line x1="{X0}" x2="{X1}" y1="{y:.1f}" y2="{y:.1f}" stroke="var(--line)" stroke-width="1"/>')
    svg.append(f'<text x="{X0 - 6}" y="{y + 4:.1f}" text-anchor="end" font-size="11" fill="var(--ink-soft)">{t // 1_000_000 if t else 0}</text>')
svg.append(f'<text x="2" y="12" font-size="11" fill="var(--ink-soft)">mil. Kč</text>')
for i, yr in enumerate(YEARS):
    cx = X0 + slot * i + slot / 2
    x = cx - bw / 2
    svg.append(f'<text x="{cx:.1f}" y="{Y1 + 18}" text-anchor="middle" font-size="12" fill="var(--ink)">{yr}</text>')
    if total_by_year[yr] == 0:
        svg.append(f'<text x="{cx:.1f}" y="{Y1 - 8}" text-anchor="middle" font-size="10" fill="var(--ink-soft)">bez smluv</text>')
        svg.append(f'<text x="{cx:.1f}" y="{Y1 + 31}" text-anchor="middle" font-size="10" fill="var(--ink-soft)">na desce</text>')
        continue
    acc = 0.0
    for sid in SERIES:
        v = cells[yr].get(sid, 0)
        if v:
            y_top, y_bot = ypos(acc + v), ypos(acc)
            tip = '\n'.join(detail[yr][sid])
            svg.append(f'<rect x="{x:.1f}" y="{y_top:.1f}" width="{bw}" height="{y_bot - y_top:.1f}" fill="{barva(sid)}" stroke="var(--white)" stroke-width="1">'
                       f'<title>{escape(str(yr) + " – " + (P[sid]["nazev"] if sid != "ostatni" else "ostatní příjemci") + ": " + kc(v) + chr(10) + tip)}</title></rect>')
            acc += v
        if sid == INV_ID and inv[yr]:
            v = inv[yr]
            y_top, y_bot = ypos(acc + v), ypos(acc)
            tip = '\n'.join(detail[yr]['inv'])
            svg.append(f'<rect x="{x:.1f}" y="{y_top:.1f}" width="{bw}" height="{y_bot - y_top:.1f}" fill="{barva(INV_ID)}" stroke="var(--white)" stroke-width="1"/>')
            svg.append(f'<rect x="{x:.1f}" y="{y_top:.1f}" width="{bw}" height="{y_bot - y_top:.1f}" fill="url(#dot-hatch)">'
                       f'<title>{escape(str(yr) + " – investiční akce Sokola: " + kc(v) + chr(10) + tip)}</title></rect>')
            acc += v
    svg.append(f'<text x="{cx:.1f}" y="{ypos(acc) - 6:.1f}" text-anchor="middle" font-size="11" font-weight="600" fill="var(--ink)">{mil(total_by_year[yr])}</text>')
svg.append('</svg>')

legend = ''.join(
    f'<li><span class="fb-sw" style="background:{barva(sid)}"></span>{escape(P[sid]["nazev"] if sid != "ostatni" else "Ostatní příjemci")}</li>'
    for sid in SERIES)
legend += ('<li><span class="fb-sw" style="background:var(--org-tj-sokol-pecky); background-image:repeating-linear-gradient(45deg,'
           'rgba(255,255,255,.55) 0 2px,transparent 2px 5px)"></span>Investiční akce Sokola 2019</li>')

ostatni_nazvy = sorted({P[s['prijemce']]['nazev'] for s in DOC['smlouvy'] if s['prijemce'] not in SERIES})

# ---- tabulka součtů po příjemcích (sbalitelná) -----------------------
tab_rows = []
by_p = defaultdict(lambda: defaultdict(float))
for s in DOC['smlouvy']:
    by_p[s['prijemce']][s['rok']] += s['castka']
for d in DOC['dodatky']:
    if d['typ'] == 'navyseni':
        by_p[d['prijemce']][d['rok']] += d['castka']
for pid in sorted(by_p, key=lambda k: -sum(by_p[k].values())):
    cs = ''.join(f'<td style="text-align:right; white-space:nowrap;">{kc(by_p[pid][y]) if by_p[pid].get(y) else "–"}</td>' for y in reversed(YEARS))
    tab_rows.append(f'<tr><td>{escape(P[pid]["nazev"])}</td>{cs}<td style="text-align:right; white-space:nowrap;"><b>{kc(sum(by_p[pid].values()))}</b></td></tr>')
tab_head = ''.join(f'<th style="text-align:right;">{y}</th>' for y in reversed(YEARS))
tab_sum = ''.join(f'<td style="text-align:right; white-space:nowrap;"><b>{kc(total_by_year[y]) if total_by_year[y] else "–"}</b></td>' for y in reversed(YEARS))

# ---- dodatky -----------------------------------------------------------
TYP = {'navyseni': ('papir', 'navýšení'), 'ucel': ('probiha', 'změna účelu'), 'termin': ('vybor', 'přesun termínu')}
dod_rows = []
for d in sorted(DOC['dodatky'], key=lambda d: d['vyvesen']):
    cls, lbl = TYP[d['typ']]
    dod_rows.append(
        f'<tr><td style="white-space:nowrap;">{datum(d["vyvesen"])}</td>'
        f'<td>{escape(P[d["prijemce"]]["nazev"])}<span class="meta-note">dodatek č. {d["dodatek"]} ke smlouvě č. {d["smlouva"]}</span></td>'
        f'<td><span class="tag {cls}">{lbl}</span></td>'
        f'<td>{escape(d["popis"])}</td>'
        f'<td>{jednani_odkaz(d["schvaleno"])}</td>'
        f'<td><a href="{escape(d["odkaz"])}" target="_blank" rel="noopener">dokument</a></td></tr>')

inv_s = next(s for s in DOC['smlouvy'] if s.get('investicni'))
lede = (f'Přehled dotací, které město Pečky poskytlo spolkům a dalším příjemcům podle smluv a dodatků vyvěšených na úřední desce. '
        f'Obsahuje {n_smlouvy} smluv a {n_dodatky} dodatků z let 2016 až 2026, dohromady {kc(celkem)} pro {n_prijemci} příjemců. V letech 2016 a 2018 až 2025 tvořily dotace bez investiční dotace Sokola z roku 2019 v průměru {PODIL}&nbsp;% ročních výdajů města (podle Monitoru Státní pokladny).')

html = f'''  <style>
    .fb-chart{{margin:18px 0 4px;}}
    .fb-chart svg{{display:block; max-width:100%; height:auto;}}
    .fb-legend{{list-style:none; margin:0 0 6px; padding:0; display:flex; flex-wrap:wrap; gap:4px 16px; font-size:12.5px; color:var(--ink-soft);}}
    .fb-legend li{{display:inline-flex; align-items:center; gap:6px;}}
    .fb-sw{{display:inline-block; width:12px; height:12px; border-radius:2px;}}
    .dot-tabulka{{font-size:var(--fs-5);}}
    .dot-tabulka th,.dot-tabulka td{{padding:8px var(--space-3);}}
    .dot-tabulka th:first-child,.dot-tabulka td:first-child{{position:sticky; left:0; z-index:1; background:var(--material); box-shadow:1px 0 0 var(--line);}}
    .dot-tabulka tr:hover td:first-child{{background:color-mix(in srgb, var(--burgundy) 3.5%, var(--material));}}
  </style>
  <section class="panel active" id="panel-dotace">
    <h2 class="title display">Dotace od města</h2>
    <p class="lede perex">{lede}</p>

    <div class="stat-grid">
      <div class="stat-card"><div class="stat-num">{mil(total_by_year[POSLEDNI])}</div><div class="stat-label">Kč v roce {POSLEDNI}<br>podle smluv na desce</div></div>
      <div class="stat-card"><div class="stat-num">{n_posl}</div><div class="stat-label">smluv o poskytnutí<br>dotace v roce {POSLEDNI}</div></div>
      <div class="stat-card"><div class="stat-num">{n_prijemci_posl}</div><div class="stat-label">příjemců<br>spolků a organizací</div></div>
      <div class="stat-card"><div class="stat-num">{kc(top_posl["castka"])}</div><div class="stat-label">nejvyšší dotace<br>{escape(P[top_posl["prijemce"]]["nazev"])}</div></div>
    </div>

    <h3 class="display" style="margin:30px 0 4px;">Dotace po letech a příjemcích</h3>
    <figure class="fb-chart">
      <ul class="fb-legend" aria-label="Legenda grafu">{legend}</ul>
      {chr(10).join(svg)}
    </figure>
    <p class="meta-note">Rok odpovídá roku, na který smlouva platí (podle čísla smlouvy). V součtech jsou smlouvy i dodatky s navýšením dotace. Do ostatních příjemců patří {escape(", ".join(ostatni_nazvy))}. Částky jsou z textů smluv a dodatků na úřední desce; po najetí na sloupec se zobrazí rozpis.</p>

    <details class="collapsible" style="margin-top:20px;">
      <summary style="cursor:pointer; list-style:none;"><h4 class="display" style="margin:0 0 4px; display:inline;">Součty podle příjemců a let <span class="collapsible-arrow" aria-hidden="true">▾</span></h4></summary>
      <div class="table-scroll"><table class="register dot-tabulka">
        <thead><tr><th>Příjemce</th>{tab_head}<th style="text-align:right;">Celkem</th></tr></thead>
        <tbody>{"".join(tab_rows)}
        <tr><td><b>Celkem</b></td>{tab_sum}<td style="text-align:right; white-space:nowrap;"><b>{kc(celkem)}</b></td></tr></tbody>
      </table></div>
    </details>

    <details class="collapsible" id="sokol-2019" style="margin-top:36px;">
      <summary style="cursor:pointer; list-style:none;"><h3 class="display" style="margin:0 0 4px; display:inline;">Investiční akce Sokola 2019 <span class="collapsible-arrow" aria-hidden="true">▾</span></h3></summary>
    <p>V roce 2019 uzavřelo město s TJ Sokol Pečky smlouvu č. 30/2019 o investiční dotaci <b>{kc(inv_s["castka"])}</b>, kterou schválilo <a href="/jednani/#zastupitelstvo-2019-05-22">ZM 22. 5. 2019</a>. Peníze šly na projekt <b>Energeticky úsporná opatření objektu sokolovny</b> čp. 330, který spolufinancovalo Ministerstvo školství, mládeže a tělovýchovy. Příslib částečného spolufinancování „ve výši minimálně 1/3 spoluúčasti žadatele“ dalo zastupitelstvo už na <a href="/jednani/#zastupitelstvo-2018-09-19">ZM 19. 9. 2018</a> s podmínkami: Sokol uspěje se žádostí o dotaci, dva zástupci města budou členy výběrové komise na dodavatele stavby a po dobu udržitelnosti projektu (10 let) se nezmění vlastnictví sokolovny, s výjimkou přednostní nabídky odkupu městu. Sokol se také zavázal poskytovat prostory základní škole, sportovním oddílům, spolkům a dalším zájemcům.</p>
    <p>Podle <a href="{escape(inv_s["odkaz"])}" target="_blank" rel="noopener">smlouvy vyvěšené 13. 6. 2019</a> se dotace vyplácí ve třech splátkách po 1&nbsp;200&nbsp;000&nbsp;Kč (29. 8., 30. 9. a 30. 10. 2019) a podmínkou výplaty je doložené rozhodnutí nebo smlouva o dotaci z ministerstva. Použít ji bylo možné do 30. 5. 2020. Stejným usnesením schválilo zastupitelstvo Sokolu i bezúročnou půjčku 1&nbsp;500&nbsp;000&nbsp;Kč na 15 let (splátky 100&nbsp;000&nbsp;Kč ročně) na stejný projekt. Půjčka je návratná, proto se do přehledu dotací nepočítá. Investiční dotace je na grafu vyznačena šrafováním a sama tvoří {round(inv_s["castka"] / total_by_year[2019] * 100)}&nbsp;% součtu za rok 2019.</p>
    </details>

    <details class="collapsible" id="dodatky" style="margin-top:36px;">
      <summary style="cursor:pointer; list-style:none;"><h3 class="display" style="margin:0 0 4px; display:inline;">Dodatky ke smlouvám <span class="collapsible-arrow" aria-hidden="true">▾</span></h3></summary>
    <p>Na úřední desce je {n_dodatky} dodatků ke smlouvám o poskytnutí dotace. Dotaci navyšují dva: AFK Pečky v roce 2018 o {kc(20000)} a TJ Sokol Pečky v roce 2025 o {kc(110000)}. Ostatní mění účel, na který lze část dotace použít, nebo prodlužují termín pro použití nevyčerpané částky; výši dotace nemění a v grafu se nepočítají.</p>
    <div class="table-scroll"><table class="register">
      <thead><tr><th>Vyvěšeno</th><th>Příjemce</th><th>Změna</th><th>Co dodatek upravuje</th><th>Schválil</th><th>Zdroj</th></tr></thead>
      <tbody>{"".join(dod_rows)}</tbody>
    </table></div>
    </details>

    <div class="callout">
      <p>Zdroj: smlouvy a dodatky vyvěšené na úřední desce města Pečky (<a href="/o-webu/uredni-deska-monitoring/">Monitoring úřední desky</a>), částky z textů příloh. Na desce nejsou smlouvy z roku 2017 a smlouvy č. 17/2020 a č. 18/2020 (k nim jsou jen dodatky); dotace z těchto smluv v přehledu chybí.</p>
    </div>
  </section>
'''
(ROOT / 'content/dotace.html').write_text(html, encoding='utf-8')
print('content/dotace.html:', len(html), 'znaků;', n_smlouvy, 'smluv,', n_dodatky, 'dodatků, celkem', celkem)
