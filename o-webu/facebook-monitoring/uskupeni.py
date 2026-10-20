#!/usr/bin/env python3
"""Vygeneruje content/fbuskupeni.html — veřejnou stránku „Politická uskupení
Peček na Facebooku“ (/o-webu/facebook-monitoring/uskupeni/, registrace
EXTRA_PAGES['fbuskupeni'] ve scripts/build.py).

Zdrojem jsou měsíční soubory o-webu/facebook-monitoring/<zdroj>/yyyy-mm.json
(formát viz README.md; jsou v .gitignore, stránka je proto statický snímek).
Pro každý účet uskupení je jeden adresář (seznam SOURCES níže). Postup:
    python3 o-webu/facebook-monitoring/summary.py     # přepočítá summary v JSON
    python3 o-webu/facebook-monitoring/uskupeni.py    # vygeneruje content/fbuskupeni.html
    python3 scripts/build.py
Vzhled karet, grafu a filtru sdílí CSS s profilem města (summary.py).
"""
import glob, json, os, sys
from collections import Counter, defaultdict
from datetime import date, timedelta
from html import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from summary import (BASE, ROOT, MONTHS, MONTHS_GEN, TYPE_GROUPS, VOLBY, cz_date,
                     num, plural, popis, volby_marks)

# Účty uskupení (pořadí = pořadí v tabulce, grafu a seznamech).
# color = barva z lide/organizations.json přes assets/org-colors.css (hex se jinde nepíše).
SOURCES = [
    dict(id='facebook-nasepecky', key='nasepecky', name='NAŠE PEČKY', org='NAŠE PEČKY a Pečky NEXT',
         kind='stránka', url='https://www.facebook.com/nasepecky', followers='cca 1 000 sledujících',
         color='var(--org-nasepecky)'),
    dict(id='facebook-peckynext', key='peckynext', name='Pečky NEXT', org='NAŠE PEČKY a Pečky NEXT',
         kind='stránka', url='https://www.facebook.com/profile.php?id=61581314026896', followers='328 sledujících',
         color='color-mix(in srgb, var(--org-nasepecky) 45%, #fff)'),
    dict(id='facebook-odspecky', key='odspecky', name='ODS a nezávislí Pečky', org='ODS a nezávislí',
         kind='stránka', url='https://www.facebook.com/odspecky.cz', followers='265 sledujících',
         color='var(--org-ods)'),
    dict(id='facebook-peckypecakum', key='peckypecakum', name='Pečky Pečákům', org='Sdružení nezávislých kandidátů Pečky Pečákům',
         kind='stránka', url='https://www.facebook.com/peckypecakum', followers='254 sledujících',
         color='var(--org-snk-pecky-pecakum)'),
    dict(id='facebook-peckysrdcem', key='peckysrdcem', name='Pečky srdcem', org='Pečky srdcem',
         kind='stránka', url='https://www.facebook.com/profile.php?id=61590557991395', followers='122 sledujících',
         color='var(--org-pecky-srdcem)'),
    dict(id='facebook-lide-pro-pecky', key='lide-pro-pecky', name='Lidé pro Pečky a Velké Chvalovice', org='Lidé pro Pečky a Velké Chvalovice s podporou SPD',
         kind='skupina', url='https://www.facebook.com/groups/1080849193521600', followers='54 členů', created='2024-11-30',
         color='var(--org-lide-pro-pecky-spd)'),
]
# Volby, vůči kterým se počítá aktivita před volbami: (rok, první den okna, poslední den voleb)
PREDVOLEBNI = [('2022', date(2022, 6, 25), date(2022, 9, 24)), ('2026', date(2026, 7, 11), date(2026, 10, 10))]


def load():
    for s in SOURCES:
        s['months'] = {}
        s['posts'] = []
        for path in sorted(glob.glob(os.path.join(BASE, s['id'], '????-??.json'))):
            with open(path, encoding='utf-8') as f:
                d = json.load(f)
            s['months'][d['month']] = sorted(d['posts'], key=lambda p: p['published'], reverse=True)
            s['posts'] += d['posts']
        s['posts'].sort(key=lambda p: p['published'], reverse=True)
        s['counts_as_of'] = max((json.load(open(p, encoding='utf-8')).get('counts_as_of') or ''
                                 for p in glob.glob(os.path.join(BASE, s['id'], '????-??.json'))), default='')
    return [s for s in SOURCES if s['posts']]


def gi_of(p):
    return next((i for i, (_, types, _) in enumerate(TYPE_GROUPS) if p['type'] in types), len(TYPE_GROUPS) - 1)


def stack_svg(slots, accs, uid, title, desc, marks=(), peak_label=True):
    """slots: [(popisek osy x | None, tooltip slotu, {acc_key: (n, href)})]; sloupec je skládaný po účtech."""
    W, H, L, R, T, B = 960, 300, 44, 10, 22, 30
    totals = [sum(n for n, _ in sl[2].values()) for sl in slots]
    mx = max(totals) or 1
    step = next(st for st in (1, 2, 5, 10, 20, 50, 100) if mx / st <= 8)
    ymax = max(step * 2, -(-mx // step) * step)
    pw, ph = W - L - R, H - T - B
    slot = pw / len(slots)
    bw = min(max(2.0, slot * 0.78), 60.0)
    parts = []
    for v in range(0, ymax + 1, step):
        y = T + ph - ph * v / ymax
        parts.append(f'<line x1="{L}" x2="{W - R}" y1="{y:.1f}" y2="{y:.1f}" stroke="var(--line)" stroke-width="1"/>')
        parts.append(f'<text x="{L - 6}" y="{y + 4:.1f}" text-anchor="end" font-size="11" fill="var(--ink-soft)">{v}</text>')
    parts.append('<text x="2" y="12" text-anchor="start" font-size="11" fill="var(--ink-soft)">příspěvků</text>')
    peak = max(totals)
    gap = 'stroke="#fff" stroke-width="0.6"' if bw >= 6 else ''
    for i, (xl, tip, per) in enumerate(slots):
        x = L + i * slot + (slot - bw) / 2
        yy = T + ph
        rects = []
        for a in accs:
            n, href = per.get(a['key'], (0, None))
            if not n:
                continue
            hh = ph * n / ymax
            yy -= hh
            rects.append(f'<a class="fb-bar" href="{href}"><title>{escape(a["name"])}: {n}</title>'
                         f'<rect x="{x:.1f}" y="{yy:.1f}" width="{bw:.1f}" height="{hh:.1f}" fill="{a["color"]}" {gap}/></a>')
        parts.append(f'<g><title>{escape(tip)}</title>' + ''.join(rects) + '</g>')
        if totals[i] == peak and peak_label:
            parts.append(f'<text x="{x + bw / 2:.1f}" y="{yy - 4:.1f}" text-anchor="middle" font-size="11" font-weight="600" fill="var(--burgundy)">{peak}</text>')
        if xl:
            cx = x + bw / 2
            parts.append(f'<line x1="{cx:.1f}" x2="{cx:.1f}" y1="{T + ph}" y2="{T + ph + 4}" stroke="var(--ink-soft)"/>')
            parts.append(f'<text x="{cx:.1f}" y="{H - 10}" text-anchor="middle" font-size="11" fill="var(--ink-soft)">{escape(xl)}</text>')
    for pos, lab, yr in marks:
        mx_ = L + pos * slot
        parts.append(f'<g class="fb-volby"><title>{escape(lab)}</title><line x1="{mx_:.1f}" x2="{mx_:.1f}" y1="{T - 6}" y2="{T + ph}" stroke="#d1242f" stroke-width="1"/>'
                     f'<text x="{mx_ + 3:.1f}" y="{T + 2}" font-size="10" fill="#d1242f">volby</text>'
                     f'<text x="{mx_ + 3:.1f}" y="{T + 13}" font-size="10" fill="#d1242f">{yr}</text></g>')
    body = '\n        '.join(parts)
    return (f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-labelledby="{uid}-t {uid}-d">\n'
            f'        <title id="{uid}-t">{escape(title)}</title>\n        <desc id="{uid}-d">{escape(desc)}</desc>\n        {body}\n      </svg>')


def render_chart(accs):
    allm = sorted({ym for a in accs for ym in a['months']})
    y0, m0 = map(int, allm[0].split('-'))
    y1, m1 = map(int, allm[-1].split('-'))
    keys = []
    y, m = y0, m0
    while (y, m) <= (y1, m1):
        keys.append(f'{y}-{m:02d}')
        m += 1
        if m == 13:
            y, m = y + 1, 1
    slots = []
    for ym in keys:
        yy, mm = ym.split('-')
        per = {a['key']: (len(a['months'][ym]), f'#u-{a["key"]}-{ym}') for a in accs if ym in a['months']}
        tot = sum(n for n, _ in per.values())
        det = ', '.join(f'{a["name"]} {per[a["key"]][0]}' for a in accs if a['key'] in per)
        slots.append((yy if mm == '01' else None, f'{MONTHS[int(mm) - 1].lower()} {yy}: {tot} {plural(tot)}' + (f' ({det})' if det else ''), per))
    totm = [(sum(n for n, _ in s[2].values()), k) for s, k in zip(slots, keys)]
    pk_n, pk_k = max(totm)
    pk_txt = f'{MONTHS[int(pk_k[5:]) - 1].lower()} {pk_k[:4]}'
    v1 = stack_svg(slots, accs, 'fbu1', 'Počet příspěvků uskupení po měsících',
                   f'Skládaný sloupcový graf: osa x čas po měsících, osa y počet příspěvků, sloupce rozdělené podle účtů. Nejvíc příspěvků vyšlo v měsíci {pk_txt} ({pk_n}).',
                   marks=volby_marks('m', keys))
    cap1 = (f'Počet příspěvků všech sledovaných účtů po měsících, sloupec je rozdělený podle účtů. Nejvíc jich vyšlo v měsíci {pk_txt} ({pk_n}), počet je nad sloupcem. '
            'Po najetí na sloupec se zobrazí rozpad, kliknutí na barevný díl otevře příspěvky účtu v daném měsíci. Tenká červená čára označuje komunální volby.')
    allp = [p for a in accs for p in a['posts']]
    end = date.fromisoformat(max(p['published'][:10] for p in allp))
    days = [end - timedelta(days=29 - i) for i in range(30)]
    slots3 = []
    for i, d in enumerate(days):
        per, det = {}, []
        for a in accs:
            n = sum(1 for p in a['posts'] if p['published'][:10] == d.isoformat())
            if n:
                per[a['key']] = (n, f'#u-{a["key"]}-{d.isoformat()[:7]}')
                det.append(f'{a["name"]} {n}')
        tot = sum(n for n, _ in per.values())
        slots3.append((f'{d.day}. {d.month}.' if i % 5 == 0 or i == 29 else None,
                       f'{d.day}. {d.month}. {d.year}: {tot} {plural(tot)}' + (f' ({", ".join(det)})' if det else ''), per))
    v3 = stack_svg(slots3, accs, 'fbu3', 'Počet příspěvků uskupení po dnech za posledních 30 dní',
                   f'Skládaný sloupcový graf: osa x dny od {days[0].day}. {days[0].month}. do {end.day}. {end.month}. {end.year}, osa y počet příspěvků za den.',
                   marks=volby_marks('d', [d.isoformat() for d in days]))
    cap3 = f'Počet příspěvků po dnech za 30 dní do posledního zachyceného příspěvku: {days[0].day}. {days[0].month}. – {end.day}. {end.month}. {end.year}. Červená čára označuje den voleb, pokud do období spadá.'
    legend = '\n'.join(f'        <li><span class="fb-sw" style="background:{a["color"]}"></span>{escape(a["name"])}</li>' for a in accs)
    return f'''    <figure class="fb-chart" id="fb-chart">
      <div class="fb-chart-head">
        <h3 class="display fb-chart-title">Počet příspěvků po měsících</h3>
        <div class="segmented-control fb-chart-ctl">
          <span class="segmented-label">Rozsah</span>
          <div class="segmented-group" role="group" aria-label="Rozsah dat grafu">
            <button type="button" class="segmented-btn active" data-fbc="1" aria-pressed="true">Od začátku</button>
            <button type="button" class="segmented-btn" data-fbc="3" aria-pressed="false">Posledních 30 dní</button>
          </div>
        </div>
      </div>
      <ul class="fb-legend" aria-label="Účty">
{legend}
      </ul>
      <div class="fb-chart-view" data-fbc-view="1">
      {v1}
      <figcaption class="meta-note">{cap1}</figcaption>
      </div>
      <div class="fb-chart-view" data-fbc-view="3" hidden>
      {v3}
      <figcaption class="meta-note">{cap3}</figcaption>
      </div>
    </figure>
'''


ZDROJE = {  # profil, ze kterého je příspěvek sdílený -> název (soukromé profily se nejmenují)
    'mestopecky': 'Město Pečky', 'pececkesluzby': 'Pečecké služby', 'kspecky': 'Kulturní středisko města Pečky',
    'knihovnapecky': 'Městská knihovna', 'Pececkadesitka': 'Pečecká desítka', 'tomio.cz': 'Tomio Okamura',
    'TomasDolezalSPD': 'Tomáš Doležal (SPD)', 'rajchl.jindrich': 'Jindřich Rajchl', 'svejnohova': 'Alena Švejnohová',
    'alena.svejnohova.9': 'Alena Švejnohová', 'martin.kupka1': 'Martin Kupka', 'odspecky.cz': 'ODS a nezávislí Pečky',
    'zuzanamajerova.cz': 'Zuzana Majerová Zahradníková', 'radimfiala.cz': 'Radim Fiala', 'stranaPRO': 'strana PRO',
    'odsceskybrod': 'ODS Český Brod', 'ODSPodebrady': 'ODS Poděbrady',
}
ZDROJE_OBECNE = {'reel': 'videa (reels)', 'photo': 'fotografie', 'groups': 'příspěvky ze skupin'}
REF = date(2026, 10, 20)  # den sběru (counts_as_of)


def cz_n(n, one, few, many):
    return f'{n} ' + (one if n == 1 else few if 2 <= n <= 4 else many)


def cz_age(d0, d1):
    months = (d1.year - d0.year) * 12 + d1.month - d0.month - (1 if d1.day < d0.day else 0)
    y, m = divmod(months, 12)
    if y and m:
        return f'{cz_n(y, "rok", "roky", "let")} a {cz_n(m, "měsíc", "měsíce", "měsíců")}'
    if y:
        return cz_n(y, 'rok', 'roky', 'let')
    if months:
        return cz_n(months, 'měsíc', 'měsíce', 'měsíců')
    return cz_n((d1 - d0).days, 'den', 'dny', 'dnů')


def pct(n, tot):
    return round(100 * n / tot) if tot else 0


def analyze(a):
    ps = a['posts']
    ds = sorted(p['published'][:10] for p in ps)
    first = date.fromisoformat(ds[0])
    body = [p for p in ps if p['type'] != 'změna úvodní fotky']
    shared = [p for p in body if p['type'] == 'sdílený příspěvek']
    orig = [p for p in body if p['type'] != 'sdílený příspěvek']
    r = dict(n=len(ps), first=first, body=len(body), shared=len(shared), orig=len(orig))
    r['p_shared'] = pct(len(shared), len(body))
    r['p_orig'] = 100 - r['p_shared']
    oc = Counter(p['type'] for p in orig)
    r['orig_mix'] = [(lab, pct(sum(oc[t] for t in ts), len(orig)))
                     for lab, ts in (('foto a alba', ('foto', 'album')), ('video', ('video',)),
                                     ('texty a odkazy', ('text', 'odkaz')), ('události', ('událost',)))
                     if orig and sum(oc[t] for t in ts)]
    src = Counter()
    for p in shared:
        pg = (p.get('shared_from') or {}).get('page')
        src[ZDROJE.get(pg) or ZDROJE_OBECNE.get(pg) or 'ostatní profily'] += 1
    skip = set(ZDROJE_OBECNE.values()) | {'ostatní profily'}
    r['src'] = [(k, n) for k, n in src.most_common() if k not in skip][:3]
    r['src_city'] = src.get('Město Pečky', 0)
    rc = [p['reactions'] for p in orig if p.get('reactions') is not None]
    cc = [p['comments'] for p in orig if p.get('comments') is not None]
    r['avg_r'] = round(sum(rc) / len(rc)) if rc else None
    r['avg_c'] = round(sum(cc) / len(cc)) if cc else None
    r['y26'] = sum(1 for d in ds if d.startswith('2026'))
    r['last90'] = sum(1 for d in ds if date.fromisoformat(d) > REF - timedelta(days=90))
    ym, n = Counter(d[:7] for d in ds).most_common(1)[0]
    r['peak'] = (f'{MONTHS[int(ym[5:]) - 1].lower()} {ym[:4]}', n)
    r['last'] = ds[-1]
    r['pre'] = []
    for yr, od, do in PREDVOLEBNI:
        k = sum(1 for d in ds if od.isoformat() <= d <= do.isoformat())
        r['pre'].append((yr, k if (k or first <= do) else None))
    return r


def headline(r):
    if r['p_shared'] >= 70:
        return f'Převážně sdílí cizí příspěvky ({r["p_shared"]} %).'
    if r['p_shared'] >= 35:
        return f'Smíšený obsah: {r["p_orig"]} % původních a {r["p_shared"]} % sdílených příspěvků.'
    if r['p_shared'] == 0:
        return 'Výhradně původní obsah, žádné sdílení.'
    return f'Převážně původní obsah ({r["p_orig"]} %).'


def render_cards(accs):
    out = []
    for a in accs:
        r = analyze(a)
        if a.get('created'):
            age = (f'<li><strong>Stáří:</strong> {cz_age(date.fromisoformat(a["created"]), REF)} '
                   f'(skupina vytvořena {cz_date(a["created"] + "T0")}).</li>')
        else:
            age = (f'<li><strong>Stáří:</strong> nejméně {cz_age(r["first"], REF)} (nejstarší zachycený příspěvek '
                   f'{cz_date(r["first"].isoformat() + "T0")}; datum založení Facebook u stránky nezobrazuje).</li>')
        pre = ' · '.join(f'{yr}: {k if k is not None else "účet ještě neměl příspěvky"}' for yr, k in r['pre'])
        bar = ''
        if r['p_orig']:
            bar += f'<span class="o" style="width:{r["p_orig"]}%">{r["p_orig"]} %</span>'
        if r['p_shared']:
            bar += f'<span class="s" style="width:{r["p_shared"]}%">{r["p_shared"]} %</span>'
        mix = ', '.join(f'{lab} {p} %' for lab, p in r['orig_mix'])
        facts = [age,
                 f'<li><strong>Aktivita:</strong> {cz_n(r["n"], "příspěvek", "příspěvky", "příspěvků")} celkem, '
                 f'{r["y26"]} v roce 2026, {r["last90"]} za posledních 90 dní do {cz_date(REF.isoformat() + "T0")}. '
                 f'Nejvíc v měsíci {r["peak"][0]} ({r["peak"][1]}), poslední příspěvek {cz_date(r["last"] + "T0")}.</li>',
                 f'<li><strong>Před volbami</strong> (3 měsíce, příspěvků): {pre}.</li>']
        if r['orig']:
            facts.append(f'<li><strong>Původní obsah</strong> ({r["orig"]}): {mix}.' +
                         (f' Průměrně {r["avg_r"]} reakcí a {r["avg_c"]} komentářů na příspěvek.' if r['avg_r'] is not None else '') + '</li>')
        if r['shared']:
            top = ', '.join(f'{k} ({n}×)' for k, n in r['src'])
            facts.append(f'<li><strong>Sdílené příspěvky</strong> ({r["shared"]}): ' +
                         (f'nejčastěji z profilů {top}' if top else 'z různých profilů') +
                         (f'; z oficiálního profilu města je {pct(r["src_city"], r["shared"])} % z nich.' if r['src_city'] else '.') + '</li>')
        facts_html = '\n          '.join(facts)
        out.append(f'''      <article class="fb-ucard">
        <h4><span class="fb-sw" style="background:{a["color"]}"></span> {escape(a["name"])}</h4>
        <p class="fb-meta">{escape(a["org"])} · <a href="{escape(a["url"], quote=True)}" target="_blank" rel="noopener">{a["kind"]} na Facebooku ↗</a> · {a["followers"]}</p>
        <p class="fb-uhead">{headline(r)}</p>
        <div class="fb-ubar" role="img" aria-label="Původní obsah {r["p_orig"]} %, sdílené příspěvky {r["p_shared"]} %">{bar}</div>
        <p class="fb-ubar-lab"><span class="fb-sw fb-sw-o"></span> původní obsah &nbsp;<span class="fb-sw fb-sw-s"></span> sdílené příspěvky &nbsp;<span class="fb-meta">(podíl z {r["body"]} příspěvků bez změn úvodní fotky)</span></p>
        <ul class="fb-ufacts">
          {facts_html}
        </ul>
      </article>''')
    return '\n'.join(out)


def card(p, a):
    day = p['published'][:10]
    meta = f'👍 {num(p["reactions"])} 💬 {num(p["comments"])} ♺ {num(p["shares"])}'
    gi = gi_of(p)
    return (f'            <li class="fb-card" data-date="{day}" data-g="{gi}" data-a="{a["key"]}">'
            f'<span class="fb-head"><time class="fb-date" datetime="{day}">{cz_date(p["published"])}</time>'
            f'<span class="fb-chip fb-t{gi}">{escape(p["type"])}</span>'
            f'<span class="fb-ac" style="color:{a["color"]}">{escape(a["name"])}</span></span>'
            f'<a class="fb-title" href="{escape(p["url"], quote=True)}" target="_blank" rel="noopener">{escape(popis(p))}</a>'
            f'<span class="fb-meta">{meta}</span></li>')


def render_account(a):
    years = defaultdict(list)
    for ym in sorted(a['months'], reverse=True):
        years[ym[:4]].append(ym)
    blocks = []
    for y, yms in years.items():
        n = sum(len(a['months'][ym]) for ym in yms)
        mons = []
        for ym in yms:
            ps = a['months'][ym]
            cards = '\n'.join(card(p, a) for p in ps)
            mons.append(f'''          <details class="fb-mon" id="u-{a["key"]}-{ym}">
            <summary>{MONTHS[int(ym[5:]) - 1]} {y} <span class="fb-tn">{len(ps)}</span></summary>
            <ul class="fb-cards">
{cards}
            </ul>
          </details>''')
        blocks.append(f'''        <details class="fb-yr" id="u-{a["key"]}-y{y}">
          <summary>{y} <span class="fb-tn">{n} {plural(n)}</span></summary>
{chr(10).join(mons)}
        </details>''')
    tot = len(a['posts'])
    return f'''    <details class="fb-acc" id="u-{a["key"]}">
      <summary><span class="fb-sw" style="background:{a["color"]}"></span> <strong>{escape(a["name"])}</strong> <span class="fb-tn">{tot} {plural(tot)}</span> <span class="collapsible-arrow" aria-hidden="true">▾</span></summary>
      <div class="fb-acc-body">
{chr(10).join(blocks)}
      </div>
    </details>'''


CSS = '''  <style>
    .fb-sw{display:inline-block; width:12px; height:12px; border-radius:2px; vertical-align:-1px;}
    .fb-meta{font-size:12px; color:var(--ink-soft);}
    #panel-fbuskupeni .table-scroll table.register{min-width:0;}
    #panel-fbuskupeni td.num,#panel-fbuskupeni th.num{text-align:right; white-space:nowrap;}
    #panel-fbuskupeni h3.display{margin:30px 0 8px;}
    .fb-cards{list-style:none; margin:0; padding:0; display:grid; grid-template-columns:minmax(0,1fr); gap:12px;}
    .fb-card{display:flex; flex-direction:column; gap:6px; padding:12px 14px; border:1px solid var(--line); border-radius:8px; background:rgba(255,255,255,0.5);}
    .fb-head{display:flex; flex-wrap:wrap; align-items:center; gap:6px;}
    .fb-chip{display:inline-block; font-size:11px; line-height:1.5; padding:0 7px; border-radius:9px; color:#fff; white-space:nowrap;}
@@CHIPCSS@@
    .fb-card .fb-date{font-size:12px; color:var(--ink-soft); font-weight:600;}
    .fb-card .fb-ac{font-size:11.5px; font-weight:600;}
    .fb-acc .fb-ac{display:none;}
    .fb-card .fb-title{line-height:1.35; overflow-wrap:anywhere;}
    .fb-card .fb-meta{margin-top:auto;}
    .fb-card.fb-hit{background:rgba(173,122,42,0.22) !important;}
    .fb-tn{font-size:12.5px; color:var(--ink-soft); font-weight:400; margin-left:6px;}
    details.fb-acc{border:1px solid var(--line); border-radius:8px; margin:12px 0; background:rgba(255,255,255,0.35);}
    details.fb-acc > summary{cursor:pointer; list-style:none; padding:12px 14px; font-size:1.05em;}
    details.fb-acc > summary::-webkit-details-marker{display:none;}
    details.fb-acc .collapsible-arrow{display:inline-block; color:var(--burgundy); font-size:0.8em; margin-left:4px; transition:transform .15s;}
    details.fb-acc:not([open]) .collapsible-arrow{transform:rotate(-90deg);}
    .fb-acc-body{padding:0 14px 14px;}
    details.fb-yr > summary,details.fb-mon > summary{cursor:pointer; padding:7px 0; font-weight:600;}
    details.fb-yr > summary{font-family:var(--font-display,inherit); font-size:1.02em; border-top:1px solid var(--line);}
    details.fb-mon{margin-left:14px;}
    details.fb-mon > summary{font-weight:500;}
    details.fb-mon .fb-cards{margin:6px 0 14px;}
    .fb-chart{margin:18px 0 4px;}
    .fb-chart svg{display:block; max-width:100%; height:auto;}
    .fb-chart figcaption{margin-top:4px;}
    .fb-chart-head{display:flex; flex-wrap:wrap; align-items:center; justify-content:space-between; gap:8px 16px; margin-bottom:6px;}
    .fb-chart-title{margin:0 !important;}
    .fb-chart-ctl{margin:0;}
    .fb-legend{list-style:none; margin:0 0 6px; padding:0; display:flex; flex-wrap:wrap; gap:4px 16px; font-size:12.5px; color:var(--ink-soft);}
    .fb-legend li{display:inline-flex; align-items:center; gap:6px;}
    .fb-chart-view[hidden]{display:none;}
    .fb-bar{cursor:pointer;}
    .fb-bar:hover rect,.fb-bar:focus-visible rect{opacity:.78;}
    #panel-fbuskupeni details[id]{scroll-margin-top:190px;}
    #fb-filter{margin:22px 0 14px;}
    #panel-fbuskupeni.fb-filtering .fb-accs{display:none !important;}
    .fb-found{margin:0 0 12px; font-size:13.5px; color:var(--ink-soft);}
    .fb-more-btn{font-family:var(--font-mono); font-size:11.5px; padding:8px 14px; border:1px solid var(--burgundy); border-radius:3px; background:none; color:var(--burgundy); cursor:pointer; margin:14px 0 0;}
    .fb-ucards{display:grid; grid-template-columns:minmax(0,1fr); gap:16px; margin-top:10px;}
    @media (min-width:900px){ .fb-ucards{grid-template-columns:repeat(2,minmax(0,1fr));} }
    .fb-ucard{border:1px solid var(--line); border-radius:8px; padding:var(--space-4,16px); background:rgba(255,255,255,0.5);}
    .fb-ucard h4{margin:0 0 2px; font-size:1.1em;}
    .fb-ucard .fb-uhead{margin:10px 0 8px; font-weight:600;}
    .fb-ubar{display:flex; height:26px; border-radius:4px; overflow:hidden; background:var(--line);}
    .fb-ubar span{display:flex; align-items:center; justify-content:center; font-size:12px; font-weight:600; color:#fff; min-width:0; overflow:hidden;}
    .fb-ubar .o{background:var(--slate);}
    .fb-ubar .s{background:var(--field);}
    .fb-ubar-lab{margin:6px 0 10px; font-size:12.5px; color:var(--ink-soft);}
    .fb-sw-o{background:var(--slate);}
    .fb-sw-s{background:var(--field);}
    .fb-ufacts{margin:0; padding-left:18px; font-size:13.5px;}
    .fb-ufacts li{margin:0 0 6px;}
  </style>
'''


POCET = {6: 'šesti', 5: 'pěti', 4: 'čtyř', 3: 'tří', 2: 'dvou', 1: 'jednoho'}


def render_page(accs):
    chipcss = '\n'.join('    .fb-t%d{background:%s;%s}' % (i, c, ' color:var(--ink);' if i == len(TYPE_GROUPS) - 1 else '')
                        for i, (_, _, c) in enumerate(TYPE_GROUPS))
    total = sum(len(a['posts']) for a in accs)
    allds = [p['published'] for a in accs for p in a['posts']]
    od, do = min(allds), max(allds)
    counts = max(a['counts_as_of'] for a in accs)
    counts_cz = cz_date(counts + 'T00:00')
    acc_btn = '\n'.join(f'          <button type="button" class="segmented-btn" data-a="{a["key"]}">{escape(a["name"])}</button>' for a in accs)
    typ_btn = '\n'.join(f'          <button type="button" class="segmented-btn" data-g="{i}">{g}</button>' for i, (g, _, _) in enumerate(TYPE_GROUPS))
    sections = '\n'.join(render_account(a) for a in accs)
    links = ', '.join(f'<a href="{escape(a["url"], quote=True)}" target="_blank" rel="noopener">{escape(a["name"])}</a>' for a in accs)
    html = f'''{CSS.replace('@@CHIPCSS@@', chipcss)}  <section class="panel active" id="panel-fbuskupeni">
    <h2 class="title display">Politická uskupení Peček na Facebooku</h2>
    <p class="lede">Příspěvky z {POCET[len(accs)]} facebookových účtů uskupení, která kandidovala v komunálních volbách v Pečkách. Graf ukazuje počet příspěvků po měsících. U každého uskupení je shrnutí (stáří účtu, aktivita, podíl původního a sdíleného obsahu) a seznam příspěvků s krátkým popisem a odkazem na originál.</p>

{render_chart(accs)}
    <h3 class="display">Uskupení a jejich účty</h3>
    <div class="fb-ucards">
{render_cards(accs)}
    </div>
    <p class="meta-note">Původní obsah jsou všechny příspěvky kromě sdílených příspěvků a změn úvodní fotky; procenta jsou podíl z těchto příspěvků. Zdroj sdílení se určuje podle profilu, z něhož je příspěvek převzatý. Stáří stránky je spodní odhad: Facebook datum založení stránky nezobrazuje, proto se počítá od nejstaršího příspěvku, který na profilu zůstal. U skupiny je uvedené datum vytvoření. Aktivita před volbami je počet příspěvků za tři měsíce před posledním dnem voleb (23.–24. 9. 2022 a 9.–10. 10. 2026).</p>

    <h3 class="display">Příspěvky podle účtů</h3>
    <div class="list-control" id="fb-filter">
      <div class="search-bar">
        <input type="search" id="fb-search" placeholder="Hledat v popisech příspěvků" autocomplete="off" aria-label="Hledat v příspěvcích">
      </div>
      <div class="segmented-control">
        <div class="segmented-group" role="group" aria-label="Účet">
          <button type="button" class="segmented-btn active" data-a="">Všechny účty</button>
{acc_btn}
        </div>
      </div>
      <div class="segmented-control">
        <div class="segmented-group" role="group" aria-label="Typ příspěvku">
          <button type="button" class="segmented-btn active" data-g="">Vše</button>
{typ_btn}
        </div>
      </div>
    </div>
    <div id="fb-results" hidden>
      <p class="fb-found" id="fb-found" aria-live="polite"></p>
      <ul class="fb-cards" id="fb-rlist"></ul>
      <p><button type="button" class="fb-more-btn" id="fb-rmore" hidden>Zobrazit dalších</button></p>
    </div>
    <div class="fb-accs">
{sections}
    </div>

    <p class="meta-note"><strong>Celkem {total} {plural(total)}</strong> na {len(accs)} účtech od {cz_date(od)} do {cz_date(do)}. Data pocházejí z veřejných facebookových profilů a skupiny uskupení ({links}) a řadí se podle data zveřejnění. Počítají se všechny příspěvky, které účet na Facebooku zobrazuje, včetně sdílení příspěvků jiných profilů a změn úvodní fotky; starší nebo smazané příspěvky v přehledu nejsou. U každého příspěvku je jen krátký popis s odkazem na originál; počty reakcí (👍), komentářů (💬) a sdílení (♺) jsou stav k {counts_cz}. U skupiny se sledujícími myslí členové. Profil samotného města je na stránce <a href="/o-webu/facebook-monitoring/facebook-mestopecky/">Facebook města Pečky</a>. Zpět na <a href="/o-webu/#owebu-socialni">Sociální sítě</a>. <span class="stamp">ověřeno</span></p>

    <script>
    (function () {{
      var FBC = {{ '1': 'mesice', '3': '30dni' }};
      function fbView(k, store) {{
        document.querySelectorAll('#fb-chart [data-fbc]').forEach(function (x) {{
          var on = x.getAttribute('data-fbc') === k;
          x.classList.toggle('active', on); x.setAttribute('aria-pressed', String(on));
        }});
        document.querySelectorAll('#fb-chart [data-fbc-view]').forEach(function (v) {{ v.hidden = v.getAttribute('data-fbc-view') !== k; }});
        if (store) {{
          var q = new URLSearchParams(location.search);
          if (k === '1') q.delete('graf'); else q.set('graf', FBC[k]);
          var qs = q.toString();
          history.replaceState(null, '', location.pathname + (qs ? '?' + qs : '') + location.hash);
        }}
      }}
      document.querySelectorAll('#fb-chart [data-fbc]').forEach(function (b) {{ b.addEventListener('click', function () {{ fbView(b.getAttribute('data-fbc'), true); }}); }});
      var g = new URLSearchParams(location.search).get('graf');
      Object.keys(FBC).forEach(function (k) {{ if (FBC[k] === g) fbView(k, false); }});

      function norm(x) {{ return x.toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g, ''); }}
      var all = Array.prototype.map.call(document.querySelectorAll('.fb-accs .fb-card'), function (el) {{
        return {{ el: el, g: el.getAttribute('data-g'), a: el.getAttribute('data-a'), t: norm(el.textContent) }};
      }});
      var panel = document.getElementById('panel-fbuskupeni'), inp = document.getElementById('fb-search');
      var res = document.getElementById('fb-results'), list = document.getElementById('fb-rlist');
      var found = document.getElementById('fb-found'), moreBtn = document.getElementById('fb-rmore');
      var fg = '', fa = '', hits = [], shown = 0, timer = null;
      function pl(n) {{ return n === 1 ? 'příspěvek' : (n >= 2 && n <= 4 ? 'příspěvky' : 'příspěvků'); }}
      function more() {{
        var n = Math.min(hits.length, shown + 100);
        for (var i = shown; i < n; i++) {{
          var c = hits[i].el.cloneNode(true); c.classList.remove('fb-hit'); c.removeAttribute('data-date');
          c.querySelector('.fb-ac').style.display = 'inline';
          list.appendChild(c);
        }}
        shown = n; moreBtn.hidden = n >= hits.length;
        moreBtn.textContent = 'Zobrazit dalších ' + Math.min(100, hits.length - n);
        found.textContent = hits.length ? 'Nalezeno ' + hits.length + ' ' + pl(hits.length) + (n < hits.length ? ' (zobrazeno ' + n + ')' : '') + '.' : 'Nic nenalezeno.';
      }}
      function filt() {{
        var terms = norm(inp.value.trim()).split(/\\s+/).filter(Boolean);
        var active = terms.length > 0 || fg !== '' || fa !== '';
        panel.classList.toggle('fb-filtering', active);
        res.hidden = !active;
        if (!active) {{ list.textContent = ''; return; }}
        hits = all.filter(function (x) {{
          return (fg === '' || x.g === fg) && (fa === '' || x.a === fa) && terms.every(function (t) {{ return x.t.indexOf(t) !== -1; }});
        }});
        hits.sort(function (p, q) {{ return q.el.getAttribute('data-date') < p.el.getAttribute('data-date') ? -1 : (q.el.getAttribute('data-date') > p.el.getAttribute('data-date') ? 1 : 0); }});
        list.textContent = ''; shown = 0; more();
      }}
      function reset() {{
        inp.value = ''; fg = ''; fa = '';
        document.querySelectorAll('#fb-filter .segmented-btn').forEach(function (b) {{ b.classList.toggle('active', (b.hasAttribute('data-a') && b.getAttribute('data-a') === '') || (b.hasAttribute('data-g') && b.getAttribute('data-g') === '')); }});
        filt();
      }}
      inp.addEventListener('input', function () {{ clearTimeout(timer); timer = setTimeout(filt, 150); }});
      document.querySelectorAll('#fb-filter .segmented-btn').forEach(function (b) {{
        b.addEventListener('click', function () {{
          var isA = b.hasAttribute('data-a');
          if (isA) fa = b.getAttribute('data-a'); else fg = b.getAttribute('data-g');
          b.parentNode.querySelectorAll('.segmented-btn').forEach(function (x) {{ x.classList.toggle('active', x === b); }});
          filt();
        }});
      }});
      moreBtn.addEventListener('click', more);

      function go(id) {{
        var m = /^u-(.+?)-(\\d{{4}}-\\d{{2}})$/.exec(id);
        var el = document.getElementById(id);
        if (!el) return false;
        if (panel.classList.contains('fb-filtering')) reset();
        var d = el;
        while (d) {{ if (d.tagName === 'DETAILS') d.open = true; d = d.parentElement; }}
        if (m) {{ var y = document.getElementById('u-' + m[1] + '-y' + m[2].slice(0, 4)); if (y) y.open = true; }}
        el.scrollIntoView({{ block: 'start', behavior: 'smooth' }});
        return true;
      }}
      document.querySelectorAll('#fb-chart a.fb-bar').forEach(function (a) {{
        a.addEventListener('click', function (e) {{
          var id = a.getAttribute('href').slice(1);
          if (go(id)) {{ e.preventDefault(); history.replaceState(null, '', location.pathname + location.search + '#' + id); }}
        }});
      }});
      window.addEventListener('hashchange', function () {{ go(location.hash.slice(1)); }});
      if (location.hash) setTimeout(function () {{ go(location.hash.slice(1)); }}, 50);
    }})();
    </script>
  </section>
'''
    return html


if __name__ == '__main__':
    accs = load()
    out = os.path.join(ROOT, 'content', 'fbuskupeni.html')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(render_page(accs))
    print('->', os.path.relpath(out, ROOT), f'({len(accs)} účtů, {sum(len(a["posts"]) for a in accs)} příspěvků)')
