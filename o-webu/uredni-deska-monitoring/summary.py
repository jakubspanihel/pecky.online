#!/usr/bin/env python3
"""Po doplnění dokumentů do 2026.txt (nebo dalšího roku) spustit:
    python3 o-webu/uredni-deska-monitoring/summary.py

Vygeneruje content/udmonitoring.html — veřejnou stránku Monitoring úřední desky
(/o-webu/uredni-deska-monitoring/, registrace EXTRA_PAGES['udmonitoring']
ve scripts/build.py): graf počtu dokumentů po měsících (a za posledních 30
dní) podle tématu a seznam dokumentů po měsících, každý s odkazem na detail
na webu města (https://pecky.cz/default/report/<id_slug>).

Zdrojová data: <rok>.txt vedle skriptu (formát v hlavičce souboru).
Stránka je statický snímek — po spuštění pustit `python3 scripts/build.py`
a přepsat lastmod v EXTRA_PAGES['udmonitoring'].
"""
import glob, os, re
from collections import Counter
from datetime import date, timedelta
from html import escape

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(BASE))
DETAIL = 'https://pecky.cz/default/report/'
BOARD_URL = 'https://pecky.cz/office/board'

MONTHS = ['Leden', 'Únor', 'Březen', 'Duben', 'Květen', 'Červen',
          'Červenec', 'Srpen', 'Září', 'Říjen', 'Listopad', 'Prosinec']
MONTHS_GEN = ['ledna', 'února', 'března', 'dubna', 'května', 'června', 'července',
              'srpna', 'září', 'října', 'listopadu', 'prosince']

# Témata (zespodu nahoru ve sloupci): (popisek, regulární výraz na název, barva).
# Zařazení podle prvního shodného pravidla, orientační (podle názvu dokumentu).
GROUPS = [
    ('Zastupitelstvo', r'zasedání zastupitelstva|zasedání zm|usnesení zm', 'var(--burgundy)'),
    ('Volby', r'volby|voleb|volebn|kandidátní|ovk|hlasování', 'var(--gold)'),
    ('Výběrová řízení', r'výběrov|vyhlášení vř|oznámení o vyhlášení vr|\bvř\b|konkurz|konkurs', 'var(--gold-deep)'),
    ('Doprava', r'provozu|dopravního značení|uzavírka', 'var(--slate)'),
    ('Dotace a rozpočet', r'dotace|rozpočt|závěrečného účtu|závěrečný účet|250/2000|daň z nemovit', 'var(--field)'),
    ('Majetek města', r'záměr|pronájem|výpůjčka|práva stavby', 'color-mix(in srgb, var(--field) 45%, var(--parchment))'),
    ('Stavby a pozemky', r'povolení stavby|odstranění stavby|kopú|kpú|pozemkov|územního|zjišťovac|podklady rozhodnutí|kabelov', 'var(--ink-soft)'),
    ('Ostatní', r'', 'var(--line)'),
]


def group_of(title):
    t = title.lower()
    for i, (_, rx, _) in enumerate(GROUPS):
        if rx and re.search(rx, t):
            return i
    return len(GROUPS) - 1


def iso(cz):
    d, m, y = cz.split('.')
    return f'{y}-{m}-{d}'


def cz_date(iso_d):
    y, m, d = iso_d.split('-')
    return f'{int(d)}. {int(m)}. {y}'


def load():
    docs = []
    for path in sorted(glob.glob(os.path.join(BASE, '????.txt'))):
        with open(path, encoding='utf-8') as f:
            for line in f:
                line = line.rstrip('\n')
                if not line or line.startswith('#'):
                    continue
                slug, v, s, typ, name = line.split('|')
                docs.append({'slug': slug, 'from': iso(v), 'to': iso(s) if s else None,
                             'type': typ or 'Úřední deska', 'title': name,
                             'group': group_of(name)})
    docs.sort(key=lambda d: (d['from'], d['slug']), reverse=True)
    return docs


def plural(n):
    return 'dokument' if n == 1 else 'dokumenty' if 2 <= n <= 4 else 'dokumentů'


def seg(docs):
    c = Counter(d['group'] for d in docs)
    return [c[i] for i in range(len(GROUPS))]


def seg_tip(segs):
    return ', '.join(f'{g[0].lower()} {n}' for g, n in zip(GROUPS, segs) if n)


def bar_svg(items, uid, title, desc):
    """Skládaný sloupcový graf. items: [(tooltip, hodnota, popisek osy x | None, kotva, počty po tématech)]."""
    W, H, L, R, T, B = 960, 300, 44, 10, 22, 30
    mx = max(n for _, n, _, _, _ in items)
    step = next(st for st in (1, 2, 5, 10, 20, 50) if mx / st <= 8)
    ymax = max(step * 2, -(-mx // step) * step)
    pw, ph = W - L - R, H - T - B
    slot = pw / len(items)
    bw = min(max(2.0, slot * 0.78), 60.0)
    parts = []
    for v in range(0, ymax + 1, step):
        y = T + ph - ph * v / ymax
        parts.append(f'<line x1="{L}" x2="{W - R}" y1="{y:.1f}" y2="{y:.1f}" stroke="var(--line)" stroke-width="1"/>')
        parts.append(f'<text x="{L - 6}" y="{y + 4:.1f}" text-anchor="end" font-size="11" fill="var(--ink-soft)">{v}</text>')
    parts.append('<text x="2" y="12" text-anchor="start" font-size="11" fill="var(--ink-soft)">dokumentů</text>')
    for i, (tip, n, xl, href, segs) in enumerate(items):
        x = L + i * slot + (slot - bw) / 2
        y = T + ph - ph * n / ymax
        gap = 'stroke="#fff" stroke-width="1"' if bw >= 6 else ''
        rects, yy = [], T + ph
        for (_, _, colr), k in zip(GROUPS, segs):
            if not k:
                continue
            hh = ph * k / ymax
            yy -= hh
            rects.append(f'<rect x="{x:.1f}" y="{yy:.1f}" width="{bw:.1f}" height="{hh:.1f}" fill="{colr}" {gap}/>')
        parts.append(f'<a class="ud-bar" href="{href}"><title>{escape(tip)}</title>' + ''.join(rects) +
                     f'<rect x="{x - (slot - bw) / 2:.1f}" y="{T}" width="{slot:.1f}" height="{ph}" fill="transparent"/></a>')
        if n:
            col = 'var(--burgundy)' if n == mx else 'var(--ink-soft)'
            parts.append(f'<text x="{x + bw / 2:.1f}" y="{y - 4:.1f}" text-anchor="middle" font-size="11" font-weight="600" fill="{col}">{n}</text>')
        if xl:
            cx = x + bw / 2
            parts.append(f'<line x1="{cx:.1f}" x2="{cx:.1f}" y1="{T + ph}" y2="{T + ph + 4}" stroke="var(--ink-soft)"/>')
            parts.append(f'<text x="{cx:.1f}" y="{H - 10}" text-anchor="middle" font-size="11" fill="var(--ink-soft)">{escape(xl)}</text>')
    body = '\n        '.join(parts)
    return (f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-labelledby="{uid}-t {uid}-d">\n'
            f'        <title id="{uid}-t">{escape(title)}</title>\n        <desc id="{uid}-d">{escape(desc)}</desc>\n        {body}\n      </svg>')


def month_range(first, last):
    """Souvislá řada měsíců yyyy-mm od first do last včetně (osa grafu bez mezer)."""
    y, m = int(first[:4]), int(first[5:])
    out = []
    while f'{y:04d}-{m:02d}' <= last:
        out.append(f'{y:04d}-{m:02d}')
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def render_chart(docs, months):
    have = set(months)
    months = month_range(months[0], months[-1])
    mdocs = {ym: [d for d in docs if d['from'][:7] == ym] for ym in months}
    mx_ym = max(months, key=lambda ym: len(mdocs[ym]))
    items = []
    for ym in months:
        n, sg = len(mdocs[ym]), seg(mdocs[ym])
        items.append((f'{MONTHS[int(ym[5:]) - 1].lower()} {ym[:4]}: {n} {plural(n)} ({seg_tip(sg)})',
                      n, (MONTHS[int(ym[5:]) - 1][:3].lower() + (f' {ym[2:4]}' if ym[5:] == '01' else '') if len(months) <= 36 else (ym[:4] if ym[5:] == '01' else None)), (f'#ud-{ym}' if ym in have else '#ud-chart'), sg))
    v1 = bar_svg(items, 'udc1', 'Počet dokumentů na úřední desce po měsících',
                 f'Sloupcový graf: osa x měsíce, osa y počet vyvěšených dokumentů, sloupce rozdělené podle tématu. '
                 f'Nejvíc dokumentů bylo vyvěšeno v měsíci {MONTHS[int(mx_ym[5:]) - 1].lower()} {mx_ym[:4]} ({len(mdocs[mx_ym])}).')
    cap1 = (f'Počet dokumentů vyvěšených v jednotlivých měsících. Nejvíc jich bylo vyvěšeno v měsíci '
            f'{MONTHS[int(mx_ym[5:]) - 1].lower()} {mx_ym[:4]} ({len(mdocs[mx_ym])}). Sloupec je rozdělený podle tématu dokumentu; '
            f'po najetí na něj se zobrazí rozpad, kliknutím se otevře seznam měsíce.')
    yitems = []
    for y in sorted({ym[:4] for ym in months}):
        yd = [d for d in docs if d['from'][:4] == y]
        n, sg = len(yd), seg(yd)
        yitems.append((f'{y}: {n} {plural(n)} ({seg_tip(sg)})', n, y, f'#ud-{max(m for m in months if m[:4] == y)}', sg))
    vy = bar_svg(yitems, 'udcy', 'Počet dokumentů na úřední desce po letech',
                 'Sloupcový graf: osa x roky, osa y počet vyvěšených dokumentů, sloupce rozdělené podle tématu.')
    capy = ('Počet dokumentů vyvěšených v jednotlivých letech. Rok ' + months[-1][:4] + ' je započtený do ' +
            cz_date(max(d['from'] for d in docs)) + '. Kliknutím na sloupec se otevře nejnovější měsíc roku.')
    last = max(d['from'] for d in docs)
    end = date.fromisoformat(last)
    days = [end - timedelta(days=29 - i) for i in range(30)]
    cnt = Counter(d['from'] for d in docs)
    items = []
    for i, d in enumerate(days):
        ds = d.isoformat()
        n = cnt.get(ds, 0)
        sg = seg([x for x in docs if x['from'] == ds])
        href = f'#ud-d-{ds}' if n else f'#ud-{ds[:7]}'
        items.append((f'{d.day}. {d.month}. {d.year}: {n} {plural(n)}' + (f' ({seg_tip(sg)})' if n else ''),
                      n, f'{d.day}. {d.month}.' if i % 5 == 0 or i == 29 else None, href, sg))
    v2 = bar_svg(items, 'udc2', 'Počet dokumentů na úřední desce po dnech za posledních 30 dní',
                 f'Sloupcový graf: osa x dny od {days[0].day}. {days[0].month}. do {end.day}. {end.month}. {end.year}, osa y počet dokumentů vyvěšených v daný den.')
    cap2 = (f'Počet dokumentů vyvěšených po dnech za 30 dní do posledního zachyceného dokumentu: '
            f'{days[0].day}. {days[0].month}. – {end.day}. {end.month}. {end.year}.')
    legend = '\n'.join(f'        <li><span class="ud-sw" style="background:{c}"></span>{g}</li>' for g, _, c in GROUPS)
    return f'''    <figure class="ud-chart" id="ud-chart">
      <div class="ud-chart-head">
        <h3 class="display ud-chart-title">Dokumenty vyvěšené na úřední desce</h3>
        <div class="segmented-control ud-chart-ctl">
          <span class="segmented-label">Rozsah</span>
          <div class="segmented-group" role="group" aria-label="Rozsah dat grafu">
            <button type="button" class="segmented-btn active" data-udc="1" aria-pressed="true">Po měsících</button>
            <button type="button" class="segmented-btn" data-udc="2" aria-pressed="false">Po letech</button>
            <button type="button" class="segmented-btn" data-udc="3" aria-pressed="false">Poslední měsíc</button>
          </div>
        </div>
      </div>
      <ul class="ud-legend" aria-label="Témata dokumentů">
{legend}
      </ul>
      <div class="ud-chart-view" data-udc-view="1">
      {v1}
      <figcaption class="meta-note">{cap1}</figcaption>
      </div>
      <div class="ud-chart-view" data-udc-view="2" hidden>
      {vy}
      <figcaption class="meta-note">{capy}</figcaption>
      </div>
      <div class="ud-chart-view" data-udc-view="3" hidden>
      {v2}
      <figcaption class="meta-note">{cap2}</figcaption>
      </div>
    </figure>
'''


def render_month(ym, docs):
    n = len(docs)
    gi = Counter(d['group'] for d in docs)
    sumtxt = ' · '.join(f'{GROUPS[i][0].lower()} {gi[i]}' for i in range(len(GROUPS)) if gi[i])
    seen, cards = set(), []
    for d in docs:
        did = '' if d['from'] in seen else f' id="ud-d-{d["from"]}"'
        seen.add(d['from'])
        typ = '' if d['type'] == 'Úřední deska' else f' · {escape(d["type"])}'
        sejmuto = f'sejmuto {cz_date(d["to"])}' if d['to'] else 'sejmutí neuvedeno'
        cards.append(
            f'        <li class="ud-card" data-date="{d["from"]}"{did}>'
            f'<span class="ud-head"><time class="ud-date" datetime="{d["from"]}">{cz_date(d["from"])}</time>'
            f'<span class="ud-chip ud-t{d["group"]}">{GROUPS[d["group"]][0]}</span></span>'
            f'<a class="ud-title" href="{DETAIL}{escape(d["slug"], quote=True)}" target="_blank" rel="noopener">{escape(d["title"])}</a>'
            f'<span class="ud-meta">{sejmuto}{typ}</span></li>')
    cards = '\n'.join(cards)
    return f'''    <details class="collapsible ud-month" id="ud-{ym}">
    <summary style="cursor:pointer; list-style:none;"><h3 class="display" style="margin:0 0 4px; display:inline;">{MONTHS[int(ym[5:]) - 1]} {ym[:4]} ({n}) <span class="collapsible-arrow" aria-hidden="true">▾</span></h3></summary>
      <div class="ud-body" id="ud-b-{ym}">
      <p class="ud-sum"><strong>Podle tématu:</strong> {escape(sumtxt)}</p>
      <ul class="ud-cards">
{cards}
      </ul>
      </div>
    </details>'''


def render_page(docs):
    months = sorted({d['from'][:7] for d in docs})
    total = len(docs)
    first_m, last_m = months[0], months[-1]
    od_txt = f'{MONTHS_GEN[int(first_m[5:]) - 1]} {first_m[:4]}'
    do_txt = f'{MONTHS_GEN[int(last_m[5:]) - 1]} {last_m[:4]}'
    last_day = max(d['from'] for d in docs)
    blocks = '\n'.join(render_month(ym, [d for d in docs if d['from'][:7] == ym]) for ym in reversed(months))
    years = sorted({ym[:4] for ym in months}, reverse=True)
    tree = []
    for k, y in enumerate(years):
        ms = [ym for ym in reversed(months) if ym[:4] == y]
        n = sum(1 for d in docs if d['from'][:4] == y)
        items = '\n'.join(
            f'            <li><button type="button" class="ud-tm" data-ym="{ym}" data-label="{MONTHS[int(ym[5:]) - 1].lower()} {ym[:4]}">'
            f'<span>{MONTHS[int(ym[5:]) - 1]}</span><span class="ud-tn">{sum(1 for d in docs if d["from"][:7] == ym)}</span></button></li>'
            for ym in ms)
        tree.append(f'''        <details class="ud-ty" data-year="{y}"{' open' if k == 0 else ''}>
          <summary>{y} <span class="ud-tn">{n}</span></summary>
          <ul>
{items}
          </ul>
        </details>''')
    tree = '\n'.join(tree)
    body = f'''    <div class="ud-months">
{blocks}
    </div>

    <div class="ud-split">
      <nav class="ud-tree" id="ud-tree" aria-label="Měsíce podle let">
{tree}
      </nav>
      <div class="ud-pane" id="ud-pane" aria-live="polite"></div>
    </div>'''
    chipcss = '\n'.join('    .ud-t%d{background:%s;%s}' % (i, c, ' color:var(--ink);' if i == len(GROUPS) - 1 else '')
                        for i, (_, _, c) in enumerate(GROUPS))
    return f'''  <style>
    .ud-month{{margin-top:22px;}}
    .ud-sum{{margin:6px 0 12px; font-size:13.5px;}}
    .ud-cards{{list-style:none; margin:0; padding:0; display:grid; grid-template-columns:minmax(0,1fr); gap:12px;}}
    .ud-split{{display:none;}}
    @media (min-width:768px){{
      #panel-udmonitoring .ud-months{{display:none;}}
      .ud-split{{display:grid; grid-template-columns:minmax(190px,250px) minmax(0,1fr); gap:28px; align-items:start; margin-top:22px;}}
      .ud-tree{{position:sticky; top:calc(var(--nav-h,0px) + var(--title-h,0px) + var(--lc-h,0px) + 8px); max-height:calc(100vh - var(--nav-h,0px) - var(--title-h,0px) - var(--lc-h,0px) - 24px); overflow-y:auto;}}
      .ud-ty summary{{cursor:pointer; font-family:var(--font-display,inherit); font-weight:700; padding:6px 0; list-style:none; display:flex; justify-content:space-between; gap:8px;}}
      .ud-ty summary::-webkit-details-marker{{display:none;}}
      .ud-ty summary::after{{content:'▸'; order:3; color:var(--ink-soft);}}
      .ud-ty[open] summary::after{{content:'▾';}}
      .ud-ty summary .ud-tn{{margin-left:auto;}}
      .ud-ty ul{{list-style:none; margin:0 0 8px; padding:0;}}
      .ud-tm{{all:unset; box-sizing:border-box; width:100%; display:flex; justify-content:space-between; gap:8px; padding:4px 8px; cursor:pointer; border-radius:3px; font-size:14px;}}
      .ud-tm:hover{{background:var(--parchment-deep);}}
      .ud-tm:focus-visible{{outline:2px solid var(--gold); outline-offset:1px;}}
      .ud-tm.active{{background:var(--burgundy); color:#fff;}}
      .ud-tn{{font-size:12.5px; color:var(--ink-soft); font-weight:400;}}
      .ud-tm.active .ud-tn{{color:#fff;}}
      .ud-pane h3{{margin:0 0 4px;}}
      .ud-pane .ud-sum{{margin-left:0;}}
      .ud-pane .ud-card[id]{{scroll-margin-top:calc(var(--nav-h,0px) + var(--title-h,0px) + var(--lc-h,0px) + 16px);}}
    }}
    .ud-card{{display:flex; flex-direction:column; gap:6px; padding:12px 14px; border:1px solid var(--line); border-radius:8px; background:rgba(255,255,255,0.5);}}
    .ud-head{{display:flex; flex-wrap:wrap; align-items:center; gap:6px;}}
    .ud-chip{{display:inline-block; font-size:11px; line-height:1.5; padding:0 7px; border-radius:9px; color:#fff; white-space:nowrap;}}
{chipcss}
    .ud-card .ud-date{{font-size:12px; color:var(--ink-soft); font-weight:600;}}
    .ud-card .ud-title{{line-height:1.35; overflow-wrap:anywhere;}}
    .ud-meta{{margin-top:auto; font-size:12px; color:var(--ink-soft);}}
    .ud-total{{margin:22px 0 0;}}
    .ud-chart{{margin:18px 0 4px;}}
    .ud-chart svg{{display:block; max-width:100%; height:auto;}}
    .ud-chart figcaption{{margin-top:4px;}}
    .ud-chart-head{{display:flex; flex-wrap:wrap; align-items:center; justify-content:space-between; gap:8px 16px; margin-bottom:6px;}}
    .ud-chart-title{{margin:0;}}
    .ud-chart-ctl{{margin:0;}}
    .ud-legend{{list-style:none; margin:0 0 6px; padding:0; display:flex; flex-wrap:wrap; gap:4px 16px; font-size:12.5px; color:var(--ink-soft);}}
    .ud-legend li{{display:inline-flex; align-items:center; gap:6px;}}
    .ud-sw{{display:inline-block; width:12px; height:12px; border-radius:2px;}}
    .ud-chart-view[hidden]{{display:none;}}
    .ud-bar{{cursor:pointer;}}
    .ud-bar:hover rect,.ud-bar:focus-visible rect{{opacity:.78;}}
    .ud-bar:focus-visible{{outline:2px solid var(--gold); outline-offset:1px;}}
    #panel-udmonitoring .ud-month,#panel-udmonitoring .ud-card[id]{{scroll-margin-top:190px;}}
    #panel-udmonitoring .ud-hit{{background:rgba(173,122,42,0.22) !important;}}
  </style>
  <section class="panel active" id="panel-udmonitoring">
    <h2 class="title display">Monitoring úřední desky</h2>
    <p class="lede">Dokumenty vyvěšené na úřední desce města Pečky od {od_txt} do {do_txt} po měsících a po letech. U každého dokumentu je datum vyvěšení, téma, datum sejmutí a odkaz na jeho detail na webu města.</p>

{render_chart(docs, months)}
{body}

    <p class="ud-total"><strong>Celkem {total} {plural(total)}</strong> v {len(months)} měsících.</p>

    <p class="meta-note">Data pocházejí z archivu <a href="{BOARD_URL}" target="_blank" rel="noopener">úřední desky na pecky.cz</a> (Hledání / Archiv, dokumenty vyvěšené od 1. 1. {months[0][:4]}), stav k {cz_date(last_day)}. Řadí se podle data vyvěšení. Téma dokumentu je určené podle názvu, zařazení je orientační. Do přehledu patří i oznámení jiných úřadů, která město vyvěšuje na svou desku (např. Městský úřad Poděbrady, Středočeský kraj). Dokumenty vyvěšené před rokem {months[0][:4]} přehled neobsahuje. Archiv není za všechny roky stejně úplný: za roky 2016 až 2018 a 2021 až 2022 obsahuje jen několik až několik desítek dokumentů (hlavně smlouvy o dotacích) a pozvánky na zasedání zastupitelstva jsou v něm jen z let 2019, 2020 a 2026. Počty dokumentů a témat proto nejsou mezi roky srovnatelné.</p>

    <script>
    function udView(k) {{
      document.querySelectorAll('#ud-chart [data-udc]').forEach(function (x) {{
        var on = x.getAttribute('data-udc') === k;
        x.classList.toggle('active', on);
        x.setAttribute('aria-pressed', String(on));
      }});
      document.querySelectorAll('#ud-chart [data-udc-view]').forEach(function (v) {{
        v.hidden = v.getAttribute('data-udc-view') !== k;
      }});
    }}
    document.querySelectorAll('#ud-chart [data-udc]').forEach(function (b) {{
      b.addEventListener('click', function () {{ udView(b.getAttribute('data-udc')); }});
    }});
    var udMq = window.matchMedia('(min-width:768px)');
    var udCur = null;
    function udBack() {{
      if (!udCur) return;
      var pane = document.getElementById('ud-pane'), box = document.getElementById('ud-b-' + udCur);
      while (pane.firstChild) {{ if (pane.firstChild.tagName === 'H3') pane.removeChild(pane.firstChild); else box.appendChild(pane.firstChild); }}
      udCur = null;
    }}
    function udSelect(btn, store) {{
      var pane = document.getElementById('ud-pane'), ym = btn.getAttribute('data-ym');
      udBack();
      var box = document.getElementById('ud-b-' + ym);
      var h = document.createElement('h3');
      h.className = 'display';
      h.textContent = btn.getAttribute('data-label').replace(/^./, function (c) {{ return c.toUpperCase(); }}) + ' (' + btn.querySelector('.ud-tn').textContent + ')';
      pane.appendChild(h);
      while (box.firstChild) pane.appendChild(box.firstChild);
      udCur = ym;
      document.querySelectorAll('#ud-tree .ud-tm').forEach(function (x) {{ x.classList.toggle('active', x === btn); }});
      btn.closest('details').open = true;
      if (store) history.replaceState(null, '', location.pathname + location.search + '#ud-' + ym);
    }}
    function udSplit() {{
      if (!udMq.matches) {{ udBack(); return; }}
      if (!udCur) udSelect(document.querySelector('#ud-tree .ud-tm'), false);
    }}
    document.querySelectorAll('#ud-tree .ud-tm').forEach(function (b) {{
      b.addEventListener('click', function () {{ udSelect(b, true); }});
    }});
    udMq.addEventListener('change', udSplit);
    function udGo(id) {{
      var m = /^ud-(?:d-)?(\d{{4}}-\d{{2}})/.exec(id);
      if (!m) return false;
      var desk = udMq.matches;
      if (desk) udSelect(document.querySelector('#ud-tree .ud-tm[data-ym="' + m[1] + '"]'), false);
      var el = document.getElementById(id);
      if (!el) return false;
      if (desk && !el.closest('#ud-pane')) el = document.querySelector('#ud-pane h3');
      if (!desk) {{ var det = el.closest('details.ud-month') || el; if (det.tagName === 'DETAILS') det.open = true; }}
      document.querySelectorAll('#panel-udmonitoring .ud-hit').forEach(function (x) {{ x.classList.remove('ud-hit'); }});
      if (el.classList.contains('ud-card')) el.classList.add('ud-hit');
      el.scrollIntoView({{ block: 'start', behavior: 'smooth' }});
      return true;
    }}
    document.querySelectorAll('#ud-chart a.ud-bar').forEach(function (a) {{
      a.addEventListener('click', function (e) {{
        var id = a.getAttribute('href').slice(1);
        if (udGo(id)) {{ e.preventDefault(); history.replaceState(null, '', location.pathname + location.search + '#' + id); }}
      }});
    }});
    window.addEventListener('hashchange', function () {{ udGo(location.hash.slice(1)); }});
    udSplit();
    if (location.hash) setTimeout(function () {{ udGo(location.hash.slice(1)); }}, 50);
    </script>
  </section>
'''


if __name__ == '__main__':
    docs = load()
    out = os.path.join(ROOT, 'content', 'udmonitoring.html')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(render_page(docs))
    c = Counter(GROUPS[d['group']][0] for d in docs)
    print('->', os.path.relpath(out, ROOT), f'({len(docs)} dokumentů)', dict(c))
