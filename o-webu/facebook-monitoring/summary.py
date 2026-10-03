#!/usr/bin/env python3
"""Po zápisu měsíčního souboru spustit: python3 o-webu/facebook-monitoring/summary.py

1. Přepočítá blok "summary" ve všech o-webu/facebook-monitoring/*/yyyy-mm.json
   (kontrola úplnosti měsíce; summary nikdy nerozcházelo s polem "posts").
2. Vygeneruje content/fbmonitoring.html — rozbalovací tabulka sesbíraných
   měsíců (měsíc, počet; po rozkliknutí rozpad podle typu a seznam příspěvků
   s krátkým výňatkem a odkazem na Facebook) pro veřejnou stránku
   /o-webu/facebook-monitoring/facebook-mestopecky/
   (registrace v scripts/build.py -> EXTRA_PAGES['fbmonitoring']).
   JSON soubory jsou v .gitignore, proto je tabulka statický HTML snímek;
   po spuštění pustit `python3 scripts/build.py` a podle potřeby přepsat
   lastmod v EXTRA_PAGES['fbmonitoring'].
"""
import glob, json, os
from collections import Counter
from html import escape

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(BASE))
SOURCE = 'facebook-mestopecky'
SOURCE_URL = 'https://www.facebook.com/mestopecky'

MONTHS = ['Leden', 'Únor', 'Březen', 'Duben', 'Květen', 'Červen',
          'Červenec', 'Srpen', 'Září', 'Říjen', 'Listopad', 'Prosinec']
MONTHS_GEN = ['ledna', 'února', 'března', 'dubna', 'května', 'června', 'července',
              'srpna', 'září', 'října', 'listopadu', 'prosince']
TYPE_LABELS = {
    'sdílený příspěvek': 'sdílení', 'odkaz': 'odkazy', 'text': 'texty',
    'album': 'alba', 'foto': 'foto', 'video': 'video',
    'změna úvodní fotky': 'změny úvodní fotky', 'událost': 'události',
}


def update_summaries():
    out = {}
    for path in sorted(glob.glob(os.path.join(BASE, '*', '????-??.json'))):
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
        posts = data['posts']
        dates = sorted(p['published'] for p in posts)
        data['summary'] = {
            'posts': len(posts),
            'by_type': dict(Counter(p['type'] for p in posts).most_common()),
            'shared_from_other_pages': sum(
                1 for p in posts
                if p.get('shared_from') and p['shared_from'].get('page') != 'mestopecky'),
            'first_published': dates[0] if dates else None,
            'last_published': dates[-1] if dates else None,
        }
        # summary hned za metadata, před posts
        ordered = {k: v for k, v in data.items() if k not in ('summary', 'posts')}
        ordered['summary'] = data['summary']
        ordered['posts'] = posts
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(ordered, f, ensure_ascii=False, indent=2)
            f.write('\n')
        out.setdefault(os.path.basename(os.path.dirname(path)), []).append(
            (data['month'], data['summary'], posts, data.get('counts_as_of')))
        print(os.path.relpath(path, BASE), data['summary'])
    return out


def month_label(ym):
    y, m = ym.split('-')
    return f'{y} {MONTHS[int(m) - 1]}'


# Milníky profilu, které nejsou příspěvky (nezapočítávají se do počtů).
# Klíč = měsíc yyyy-mm; hodnota = [(datum ISO, text)]. Zobrazí se v detailu měsíce.
EVENTS = {
    'facebook-mestopecky': {
        '2018-11': [('2018-11-20', 'Založení facebooku města')],
    },
}

TYPE_ORDER = ['text', 'odkaz', 'foto', 'album', 'video', 'sdílený příspěvek',
              'událost', 'změna úvodní fotky']  # pevné pořadí v rozpadu podle typu
def cz_date(iso):
    d, t = iso.split('T')
    y, m, dd = d.split('-')
    return f'{int(dd)}. {int(m)}. {y}'


def popis(p):
    """Krátký ručně psaný popis příspěvku (pole "popis" v JSON; píše se při
    sběru, bez jmen a telefonů). Chybí-li, použije se neutrální popis podle typu —
    text příspěvku se do veřejné stránky záměrně nepřenáší."""
    if p.get('popis'):
        return p['popis']
    sh = p.get('shared_from') or {}
    typ = p['type']
    if typ == 'sdílený příspěvek':
        return 'Sdílený příspěvek' + (f' profilu {sh["page"]}' if sh.get('page') else '')
    return {'album': 'Album', 'foto': 'Foto', 'video': 'Video', 'odkaz': 'Odkaz',
            'text': 'Příspěvek', 'událost': 'Událost',
            'změna úvodní fotky': 'Změna úvodní fotky'}.get(typ, 'Příspěvek')


def plural(n):
    return 'příspěvek' if n == 1 else 'příspěvky' if 2 <= n <= 4 else 'příspěvků'


def num(v):
    return '–' if v is None else str(v)


def bar_svg(items, uid, title, desc, labels_on_bars=False):
    """Statický SVG sloupcový graf. items: [(tooltip, hodnota, popisek osy x | None, kotva "#id")].
    Sloupec je odkaz na kotvu v tabulkách pod grafem (rozbalení + posun řeší skript stránky)."""
    W, H, L, R, T, B = 960, 300, 44, 10, 22, 30
    mx = max(n for _, n, _, _ in items)
    step = next(st for st in (1, 2, 5, 10, 20, 50, 100) if mx / st <= 8)  # nejvýš ~8 dílků osy y
    ymax = max(step * 2, -(-mx // step) * step)
    pw, ph = W - L - R, H - T - B
    slot = pw / len(items)
    bw = min(max(2.0, slot * 0.78), 60.0)
    peak = max(n for _, n, _, _ in items)
    parts = []
    for v in range(0, ymax + 1, step):
        y = T + ph - ph * v / ymax
        parts.append(f'<line x1="{L}" x2="{W - R}" y1="{y:.1f}" y2="{y:.1f}" stroke="var(--line)" stroke-width="1"/>')
        parts.append(f'<text x="{L - 6}" y="{y + 4:.1f}" text-anchor="end" font-size="11" fill="var(--ink-soft)">{v}</text>')
    parts.append('<text x="2" y="12" text-anchor="start" font-size="11" fill="var(--ink-soft)">příspěvků</text>')
    for i, (tip, n, xl, href) in enumerate(items):
        x = L + i * slot + (slot - bw) / 2
        h = ph * n / ymax
        y = T + ph - h
        fill = 'var(--burgundy)' if n == peak else 'var(--slate)'
        parts.append(f'<a class="fb-bar" href="{href}"><rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{max(h, 0):.1f}" fill="{fill}"><title>{escape(tip)}</title></rect>'
                     f'<rect x="{x - (slot - bw) / 2:.1f}" y="{T}" width="{slot:.1f}" height="{ph}" fill="transparent"/></a>')
        if n == peak or labels_on_bars:
            col = 'var(--burgundy)' if n == peak else 'var(--ink-soft)'
            parts.append(f'<text x="{x + bw / 2:.1f}" y="{y - 4:.1f}" text-anchor="middle" font-size="11" font-weight="600" fill="{col}">{n}</text>')
        if xl:
            cx = x + bw / 2
            parts.append(f'<line x1="{cx:.1f}" x2="{cx:.1f}" y1="{T + ph}" y2="{T + ph + 4}" stroke="var(--ink-soft)"/>')
            parts.append(f'<text x="{cx:.1f}" y="{H - 10}" text-anchor="middle" font-size="11" fill="var(--ink-soft)">{escape(xl)}</text>')
    body = '\n        '.join(parts)
    return (f'<svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-labelledby="{uid}-t {uid}-d">\n'
            f'        <title id="{uid}-t">{escape(title)}</title>\n        <desc id="{uid}-d">{escape(desc)}</desc>\n        {body}\n      </svg>')


def render_chart(months):
    """Graf za perexem se segmentovým přepínačem rozsahu: Od začátku (měsíce) /
    Po letech / Posledních 30 dní (dny do posledního zachyceného příspěvku).
    Všechny tři SVG jsou předrenderované; přepínač (JS) jen ukazuje/skrývá."""
    mc = sorted((ym, sm['posts']) for ym, sm, _, _ in months)
    allposts = [p for _, _, ps, _ in months for p in ps]
    pk_ym, pk_n = max(mc, key=lambda t: t[1])
    pk_txt = f'{MONTHS[int(pk_ym[5:]) - 1].lower()} {pk_ym[:4]}'
    # 1) po měsících
    items = []
    for ym, n in mc:
        y_, m_ = ym.split('-')
        items.append((f'{MONTHS[int(m_) - 1].lower()} {y_}: {n} {plural(n)}', n, y_ if m_ == '01' else None, f'#fb-{ym}'))
    v1 = bar_svg(items, 'fbc1', 'Počet příspěvků po měsících',
                 f'Sloupcový graf: osa x čas po měsících, osa y počet příspěvků. Nejvíc příspěvků vyšlo v měsíci {pk_txt} ({pk_n}).')
    cap1 = f'Počet příspěvků po měsících. Nejvíc jich vyšlo v měsíci {pk_txt} ({pk_n}), zvýrazněno. Po najetí na sloupec se zobrazí měsíc a počet.'
    # 2) po letech
    ys = {}
    for ym, n in mc:
        ys[ym[:4]] = ys.get(ym[:4], 0) + n
    first = min(p['published'] for p in allposts)
    last = max(p['published'] for p in allposts)
    items = [(f'{y}: {n} {plural(n)}', n, y, f'#fb-y-{y}') for y, n in sorted(ys.items())]
    ypk = max(ys.items(), key=lambda t: t[1])
    v2 = bar_svg(items, 'fbc2', 'Počet příspěvků po letech',
                 f'Sloupcový graf: osa x roky, osa y počet příspěvků. Nejvíc příspěvků vyšlo v roce {ypk[0]} ({ypk[1]}).', labels_on_bars=True)
    cap2 = (f'Počet příspěvků v jednotlivých letech. Rok {first[:4]} je započtený od {cz_date(first)}, rok {last[:4]} do {cz_date(last)}.')
    # 3) posledních 30 dní (do posledního zachyceného příspěvku)
    from datetime import date, timedelta
    end = date.fromisoformat(last[:10])
    days = [end - timedelta(days=29 - i) for i in range(30)]
    cnt = Counter(p['published'][:10] for p in allposts)
    items = []
    for i, d in enumerate(days):
        n = cnt.get(d.isoformat(), 0)
        href = f'#fb-d-{d.isoformat()}' if n else f'#fb-{d.isoformat()[:7]}'
        items.append((f'{d.day}. {d.month}. {d.year}: {n} {plural(n)}', n, f'{d.day}. {d.month}.' if i % 5 == 0 or i == 29 else None, href))
    v3 = bar_svg(items, 'fbc3', 'Počet příspěvků po dnech za posledních 30 dní',
                 f'Sloupcový graf: osa x dny od {days[0].day}. {days[0].month}. do {end.day}. {end.month}. {end.year}, osa y počet příspěvků za den.')
    cap3 = (f'Počet příspěvků po dnech za 30 dní do posledního zachyceného příspěvku: {days[0].day}. {days[0].month}. – {end.day}. {end.month}. {end.year}.')
    return f'''    <figure class="fb-chart" id="fb-chart">
      <div class="fb-chart-view" data-fbc-view="1">
      {v1}
      <figcaption class="meta-note">{cap1}</figcaption>
      </div>
      <div class="fb-chart-view" data-fbc-view="2" hidden>
      {v2}
      <figcaption class="meta-note">{cap2}</figcaption>
      </div>
      <div class="fb-chart-view" data-fbc-view="3" hidden>
      {v3}
      <figcaption class="meta-note">{cap3}</figcaption>
      </div>

      <div class="segmented-control fb-chart-ctl">
        <span class="segmented-label">Rozsah</span>
        <div class="segmented-group" role="group" aria-label="Rozsah dat grafu">
          <button type="button" class="segmented-btn active" data-fbc="1" aria-pressed="true">Od začátku</button>
          <button type="button" class="segmented-btn" data-fbc="2" aria-pressed="false">Po letech</button>
          <button type="button" class="segmented-btn" data-fbc="3" aria-pressed="false">Posledních 30 dní</button>
        </div>
      </div>
    </figure>
'''


def render_month(idx, ym, s, posts, counts_as_of, events=()):
    typy = ' · '.join(f'{TYPE_LABELS.get(t, t)} {s["by_type"][t]}'
                      for t in TYPE_ORDER if s['by_type'].get(t))
    extra = [t for t in s['by_type'] if t not in TYPE_ORDER]  # neznámý typ nesmí zmizet
    typy += ''.join(f' · {t} {s["by_type"][t]}' for t in extra)
    rows = []
    seen_days = set()
    for p in sorted(posts, key=lambda x: x['published'], reverse=True):
        day = p['published'][:10]
        did = '' if day in seen_days else f' id="fb-d-{day}"'
        seen_days.add(day)
        meta = (f'👍 {num(p["reactions"])} 💬 {num(p["comments"])} ♺ {num(p["shares"])} '
                f'typ: {escape(p["type"])}')
        rows.append(
            f'            <tr data-date="{day}"{did}><td>{cz_date(p["published"])}</td><td>'
            f'<a href="{escape(p["url"], quote=True)}" target="_blank" rel="noopener">{escape(popis(p))}</a>'
            f'<br><span class="fb-meta">{meta}</span></td></tr>')
    for d, text in events:  # milník = nejstarší řádek měsíce, bez odkazu a bez počtů
        rows.append(
            f'            <tr class="fb-event"><td>{cz_date(d + "T00:00")}</td><td>'
            f'<strong>{escape(text)}</strong><br><span class="fb-meta">událost profilu, není příspěvek</span></td></tr>')
    rows = '\n'.join(rows)
    return f'''        <tr class="fb-row" id="fb-{ym}" tabindex="0" role="button" aria-expanded="false" aria-controls="fb-m{idx}"><td><span class="fb-chev" aria-hidden="true">▸</span> {month_label(ym)}</td><td>{s["posts"]}</td></tr>
        <tr class="fb-detail" id="fb-m{idx}" hidden><td colspan="2">
          <p class="fb-sum"><strong>Podle typu:</strong> {escape(typy)}<br><strong>Sdílení z cizích profilů:</strong> {s["shared_from_other_pages"]}</p>
          <table class="register fb-posts">
            <thead><tr><th>Datum</th><th>Obsah</th></tr></thead>
            <tbody>
{rows}
            </tbody>
          </table>
        </td></tr>'''


def render_page(months):
    """months: [(yyyy-mm, summary, posts, counts_as_of)] -> obsah panelu."""
    months = sorted(months, key=lambda x: x[0], reverse=True)  # nejnovější nahoře
    ev = EVENTS.get(SOURCE, {})
    ev = EVENTS.get(SOURCE, {})
    total = sum(s['posts'] for _, s, _, _ in months)
    roky = []  # [(rok, [(idx, měsíc, ...)])] sestupně
    for i, m in enumerate(months):
        if not roky or roky[-1][0] != m[0][:4]:
            roky.append((m[0][:4], []))
        roky[-1][1].append((i, m))
    bloky = []
    for rok, ms in roky:
        n = sum(m[1]['posts'] for _, m in ms)
        radky = '\n'.join(render_month(i, ym, sm, posts, c, ev.get(ym, ())) for i, (ym, sm, posts, c) in ms)
        bloky.append(f'''    <h3 class="display fb-year" id="fb-y-{rok}">{rok} ({n} {plural(n)})</h3>
    <div class="table-scroll">
    <table class="register">
      <thead><tr><th>Měsíc</th><th>Příspěvků</th></tr></thead>
      <tbody>
{radky}
      </tbody>
    </table>
    </div>''')
    body = '\n\n'.join(bloky)
    counts = max((c for *_, c in months if c), default=None)
    counts_cz = cz_date(counts + 'T00:00') if counts else 'neuvedeno'
    prvni, posledni = months[-1][0], months[0][0]  # months jsou sestupně
    od_txt = f'{MONTHS_GEN[int(prvni[5:]) - 1]} {prvni[:4]}'
    do_txt = f'{MONTHS_GEN[int(posledni[5:]) - 1]} {posledni[:4]}'
    return f'''  <style>
    .fb-row{{cursor:pointer;}}
    .fb-row:hover td,.fb-row:focus-visible td{{background:var(--parchment-deep);}}
    #panel-fbmonitoring .fb-detail:hover td,#panel-fbmonitoring .fb-detail tr:hover td{{background:none;}}
    .fb-row .fb-chev{{display:inline-block; width:1em; color:var(--ink-soft);}}
    .fb-detail td{{padding:6px 0 18px;}}
    .fb-detail[hidden]{{display:none;}}
    .fb-sum{{margin:8px 10px 12px; font-size:13.5px;}}
    .fb-posts{{margin:0;}}
    .fb-meta{{font-size:12px; color:var(--ink-soft);}}
    .fb-event td{{background:var(--parchment-deep);}}
    #panel-fbmonitoring h3.fb-year{{position:sticky; top:calc(var(--title-h,0px) + var(--lc-h,0px)); z-index:8; background:var(--parchment); padding:6px 0; margin:26px 0 0;}}
    @media (min-width:768px){{ #panel-fbmonitoring h3.fb-year{{top:calc(var(--nav-h,0px) + var(--title-h,0px) + var(--lc-h,0px));}} }}
    .fb-total{{margin:16px 0 0;}}
    .fb-chart{{margin:18px 0 4px;}}
    .fb-chart svg{{display:block; max-width:100%; height:auto;}}
    .fb-chart figcaption{{margin-top:4px;}}
    .fb-chart-ctl{{margin:12px 0 4px;}}
    .fb-chart-view[hidden]{{display:none;}}
    .fb-bar{{cursor:pointer;}}
    .fb-bar:hover rect,.fb-bar:focus-visible rect{{opacity:.78;}}
    .fb-bar:focus-visible{{outline:2px solid var(--gold); outline-offset:1px;}}
    #panel-fbmonitoring .fb-row,#panel-fbmonitoring h3.fb-year,#panel-fbmonitoring .fb-detail tr[id]{{scroll-margin-top:190px;}}
    #panel-fbmonitoring .fb-hit td{{background:rgba(173,122,42,0.22) !important;}}
    #panel-fbmonitoring h3.fb-hit{{color:var(--burgundy);}}
  </style>
  <section class="panel active" id="panel-fbmonitoring">
    <h2 class="title display">Monitoring Facebooku: Město Pečky</h2>
    <p class="lede">Příspěvky z oficiálního facebookového profilu Města Pečky od {od_txt} po měsících. U každého měsíce je počet příspěvků, po rozkliknutí rozpad podle typu a seznam příspěvků s odkazy na Facebook.</p>

{render_chart(months)}
{body}

    <p class="fb-total"><strong>Celkem {total} {plural(total)}</strong> ve {len(months)} měsících.</p>

    <p class="meta-note">Data pocházejí z veřejného profilu <a href="{SOURCE_URL}" target="_blank" rel="noopener">facebook.com/mestopecky</a> a řadí se podle data zveřejnění. Počítají se všechny příspěvky profilu v daném měsíci, včetně sdílení příspěvků jiných profilů a změn úvodní fotky. U každého příspěvku je jen krátký popis s odkazem na originál na Facebooku; počty reakcí (👍), komentářů (💬) a sdílení (♺) jsou stav k {counts_cz}. Přehled pokrývá období od {od_txt} do {do_txt}. Dřívější a pozdější měsíce v něm zatím nejsou. Zpět na <a href="/o-webu/#owebu-socialni">Sociální sítě</a>. <span class="stamp">ověřeno</span></p>
    <script>
    var FBC = {{ '1': 'mesice', '2': 'roky', '3': '30dni' }};
    function fbView(k, store) {{
      document.querySelectorAll('#fb-chart [data-fbc]').forEach(function (x) {{
        var on = x.getAttribute('data-fbc') === k;
        x.classList.toggle('active', on);
        x.setAttribute('aria-pressed', String(on));
      }});
      document.querySelectorAll('#fb-chart [data-fbc-view]').forEach(function (v) {{
        v.hidden = v.getAttribute('data-fbc-view') !== k;
      }});
      if (store) {{
        var q = new URLSearchParams(location.search);
        if (k === '1') q.delete('graf'); else q.set('graf', FBC[k]);
        var qs = q.toString();
        history.replaceState(null, '', location.pathname + (qs ? '?' + qs : '') + location.hash);
      }}
    }}
    document.querySelectorAll('#fb-chart [data-fbc]').forEach(function (b) {{
      b.addEventListener('click', function () {{ fbView(b.getAttribute('data-fbc'), true); }});
    }});
    (function () {{
      var g = new URLSearchParams(location.search).get('graf');
      Object.keys(FBC).forEach(function (k) {{ if (FBC[k] === g) fbView(k, false); }});
    }})();
    function fbSet(tr, open) {{
      var d = document.getElementById(tr.getAttribute('aria-controls'));
      tr.setAttribute('aria-expanded', String(open));
      tr.querySelector('.fb-chev').textContent = open ? '▾' : '▸';
      d.hidden = !open;
    }}
    document.querySelectorAll('#panel-fbmonitoring .fb-row').forEach(function (tr) {{
      function toggle() {{ fbSet(tr, tr.getAttribute('aria-expanded') !== 'true'); }}
      tr.addEventListener('click', function (e) {{ if (!e.target.closest('a')) toggle(); }});
      tr.addEventListener('keydown', function (e) {{
        if (e.key === 'Enter' || e.key === ' ') {{ e.preventDefault(); toggle(); }}
      }});
    }});
    function fbGo(id) {{
      var el = document.getElementById(id);
      if (!el || id.indexOf('fb-') !== 0) return false;
      var row = el.classList.contains('fb-row') ? el : null;
      if (!row && el.closest('.fb-detail')) row = el.closest('.fb-detail').previousElementSibling;
      if (row && row.classList.contains('fb-row')) fbSet(row, true);
      document.querySelectorAll('#panel-fbmonitoring .fb-hit').forEach(function (x) {{ x.classList.remove('fb-hit'); }});
      el.classList.add('fb-hit');
      el.scrollIntoView({{ block: 'start', behavior: 'smooth' }});
      return true;
    }}
    document.querySelectorAll('#fb-chart a.fb-bar').forEach(function (a) {{
      a.addEventListener('click', function (e) {{
        var id = a.getAttribute('href').slice(1);
        if (fbGo(id)) {{ e.preventDefault(); history.replaceState(null, '', location.pathname + location.search + '#' + id); }}
      }});
    }});
    window.addEventListener('hashchange', function () {{ fbGo(location.hash.slice(1)); }});
    if (location.hash) setTimeout(function () {{ fbGo(location.hash.slice(1)); }}, 50);
    </script>
  </section>
'''


if __name__ == '__main__':
    result = update_summaries()
    months = result.get(SOURCE, [])
    if months:
        out = os.path.join(ROOT, 'content', 'fbmonitoring.html')
        with open(out, 'w', encoding='utf-8') as f:
            f.write(render_page(months))
        print('->', os.path.relpath(out, ROOT), f'({len(months)} měsíců)')
