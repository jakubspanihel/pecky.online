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


def render_chart(months):
    """Statický SVG sloupcový graf: počet příspěvků po měsících (osa x čas, osa y počet).
    months: [(yyyy-mm, summary, posts, counts_as_of)] libovolně seřazené."""
    data = sorted((ym, sm['posts']) for ym, sm, _, _ in months)
    W, H, L, R, T, B = 960, 300, 44, 10, 22, 30
    ymax = max(10, -(-max(n for _, n in data) // 10) * 10)
    pw, ph = W - L - R, H - T - B
    slot = pw / len(data)
    bw = max(2.0, slot * 0.78)
    peak = max(n for _, n in data)
    parts = []
    for v in range(0, ymax + 1, 10):
        y = T + ph - ph * v / ymax
        parts.append(f'<line x1="{L}" x2="{W - R}" y1="{y:.1f}" y2="{y:.1f}" stroke="var(--line)" stroke-width="1"/>')
        parts.append(f'<text x="{L - 6}" y="{y + 4:.1f}" text-anchor="end" font-size="11" fill="var(--ink-soft)">{v}</text>')
    parts.append(f'<text x="2" y="12" text-anchor="start" font-size="11" fill="var(--ink-soft)">příspěvků</text>')
    for i, (ym, n) in enumerate(data):
        x = L + i * slot + (slot - bw) / 2
        h = ph * n / ymax
        y = T + ph - h
        fill = 'var(--burgundy)' if n == peak else 'var(--slate)'
        y_, m_ = ym.split('-')
        tip = f'{MONTHS[int(m_) - 1].lower()} {y_}: {n} {plural(n)}'
        parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{h:.1f}" fill="{fill}"><title>{escape(tip)}</title></rect>')
        if n == peak:
            parts.append(f'<text x="{x + bw / 2:.1f}" y="{y - 4:.1f}" text-anchor="middle" font-size="11" font-weight="600" fill="var(--burgundy)">{n}</text>')
        if m_ == '01':
            cx = x + bw / 2
            parts.append(f'<line x1="{cx:.1f}" x2="{cx:.1f}" y1="{T + ph}" y2="{T + ph + 4}" stroke="var(--ink-soft)"/>')
            parts.append(f'<text x="{cx:.1f}" y="{H - 10}" text-anchor="middle" font-size="11" fill="var(--ink-soft)">{y_}</text>')
    pk = [ym for ym, n in data if n == peak][0]
    pk_txt = f'{MONTHS[int(pk[5:]) - 1].lower()} {pk[:4]}'
    svg = '\n      '.join(parts)
    return f'''    <figure class="fb-chart">
      <svg viewBox="0 0 {W} {H}" width="100%" role="img" aria-labelledby="fb-chart-t fb-chart-d">
      <title id="fb-chart-t">Počet příspěvků po měsících</title>
      <desc id="fb-chart-d">Sloupcový graf: osa x čas po měsících, osa y počet příspěvků. Nejvíc příspěvků vyšlo v měsíci {pk_txt} ({peak}).</desc>
      {svg}
      </svg>
      <figcaption class="meta-note">Počet příspěvků po měsících. Nejvíc jich vyšlo v měsíci {pk_txt} ({peak}), zvýrazněno. Po najetí na sloupec se zobrazí měsíc a počet.</figcaption>
    </figure>
'''


def render_month(idx, ym, s, posts, counts_as_of, events=()):
    typy = ' · '.join(f'{TYPE_LABELS.get(t, t)} {s["by_type"][t]}'
                      for t in TYPE_ORDER if s['by_type'].get(t))
    extra = [t for t in s['by_type'] if t not in TYPE_ORDER]  # neznámý typ nesmí zmizet
    typy += ''.join(f' · {t} {s["by_type"][t]}' for t in extra)
    rows = []
    for p in sorted(posts, key=lambda x: x['published'], reverse=True):
        meta = (f'👍 {num(p["reactions"])} 💬 {num(p["comments"])} ♺ {num(p["shares"])} '
                f'typ: {escape(p["type"])}')
        rows.append(
            f'            <tr><td>{cz_date(p["published"])}</td><td>'
            f'<a href="{escape(p["url"], quote=True)}" target="_blank" rel="noopener">{escape(popis(p))}</a>'
            f'<br><span class="fb-meta">{meta}</span></td></tr>')
    for d, text in events:  # milník = nejstarší řádek měsíce, bez odkazu a bez počtů
        rows.append(
            f'            <tr class="fb-event"><td>{cz_date(d + "T00:00")}</td><td>'
            f'<strong>{escape(text)}</strong><br><span class="fb-meta">událost profilu, není příspěvek</span></td></tr>')
    rows = '\n'.join(rows)
    return f'''        <tr class="fb-row" tabindex="0" role="button" aria-expanded="false" aria-controls="fb-m{idx}"><td><span class="fb-chev" aria-hidden="true">▸</span> {month_label(ym)}</td><td>{s["posts"]}</td></tr>
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
        bloky.append(f'''    <h3 class="display fb-year">{rok} ({n} {plural(n)})</h3>
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
  </style>
  <section class="panel active" id="panel-fbmonitoring">
    <h2 class="title display">Monitoring Facebooku: Město Pečky</h2>
    <p class="lede">Příspěvky z oficiálního facebookového profilu Města Pečky od {od_txt} po měsících. U každého měsíce je počet příspěvků, po rozkliknutí rozpad podle typu a seznam příspěvků s odkazy na Facebook.</p>

{render_chart(months)}
{body}

    <p class="fb-total"><strong>Celkem {total} {plural(total)}</strong> ve {len(months)} měsících.</p>

    <p class="meta-note">Data pocházejí z veřejného profilu <a href="{SOURCE_URL}" target="_blank" rel="noopener">facebook.com/mestopecky</a> a řadí se podle data zveřejnění. Počítají se všechny příspěvky profilu v daném měsíci, včetně sdílení příspěvků jiných profilů a změn úvodní fotky. U každého příspěvku je jen krátký popis s odkazem na originál na Facebooku; počty reakcí (👍), komentářů (💬) a sdílení (♺) jsou stav k {counts_cz}. Přehled pokrývá období od {od_txt} do {do_txt}. Dřívější a pozdější měsíce v něm zatím nejsou. Zpět na <a href="/o-webu/#owebu-socialni">Sociální sítě</a>. <span class="stamp">ověřeno</span></p>
    <script>
    document.querySelectorAll('#panel-fbmonitoring .fb-row').forEach(function (tr) {{
      function toggle() {{
        var d = document.getElementById(tr.getAttribute('aria-controls'));
        var open = tr.getAttribute('aria-expanded') === 'true';
        tr.setAttribute('aria-expanded', String(!open));
        tr.querySelector('.fb-chev').textContent = open ? '▸' : '▾';
        d.hidden = open;
      }}
      tr.addEventListener('click', function (e) {{ if (!e.target.closest('a')) toggle(); }});
      tr.addEventListener('keydown', function (e) {{
        if (e.key === 'Enter' || e.key === ' ') {{ e.preventDefault(); toggle(); }}
      }});
    }});
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
