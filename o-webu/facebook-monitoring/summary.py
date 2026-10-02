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


def num(v):
    return '–' if v is None else str(v)


def render_month(idx, ym, s, posts, counts_as_of):
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
    body = '\n'.join(render_month(i, ym, s, posts, c) for i, (ym, s, posts, c) in enumerate(months))
    total = sum(s['posts'] for _, s, _, _ in months)
    counts = max((c for *_, c in months if c), default=None)
    counts_cz = cz_date(counts + 'T00:00') if counts else 'neuvedeno'
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
  </style>
  <section class="panel active" id="panel-fbmonitoring">
    <h2 class="title display">Monitoring Facebooku: Město Pečky</h2>
    <p class="lede">Archiv příspěvků oficiálního facebookového profilu města. Tabulka ukazuje, které měsíce máme sesbírané a kolik příspěvků v nich vyšlo. Kliknutím na měsíc se rozbalí rozpad podle typu a seznam příspěvků.</p>

    <div class="table-scroll">
    <table class="register">
      <thead><tr><th>Měsíc</th><th>Příspěvků</th></tr></thead>
      <tbody>
{body}
        <tr><td><strong>Celkem</strong></td><td><strong>{total}</strong></td></tr>
      </tbody>
    </table>
    </div>

    <p class="meta-note">Příspěvky se sbírají ručně z veřejného profilu <a href="{SOURCE_URL}" target="_blank" rel="noopener">facebook.com/mestopecky</a> a řadí se podle data zveřejnění. Počítají se všechny příspěvky profilu v daném měsíci, včetně sdílení příspěvků jiných profilů a změn úvodní fotky. U každého příspěvku je jen krátký popis s odkazem na originál na Facebooku; počty reakcí (👍), komentářů (💬) a sdílení (♺) jsou stav k {counts_cz}. Měsíce, které v tabulce nejsou, zatím nejsou sesbírané. Zpět na <a href="/o-webu/#owebu-socialni">Sociální sítě</a>. <span class="stamp">ověřeno</span></p>
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
