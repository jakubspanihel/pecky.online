#!/usr/bin/env python3
"""
Vygeneruje znalostní index pro PečkyBota: peckybot/index.json.

Index čte Cloudflare Worker (peckybot/worker/), který z něj vybírá úryvky
k dotazu návštěvníka. Zdroje jsou jen data, která už na webu jsou:

  - jednání zastupitelstva a rady (jednani/pecky-jednani.json) — bod programu
    + důvodová zpráva + usnesení
  - lidé s životopisem nebo kontaktem (lide/people.json)
  - statické texty sekcí (content/<sekce>.html)

Formát (verze 1) — rozdělený na malý rejstřík a dávky s texty, aby Worker při
studeném startu parsoval jen rejstřík (limit CPU na volání) a texty úryvků
stahoval jen pro nejlepší zásahy:
  peckybot/index.json:
    {"v": 1, "shard": 100,
     "chunks": [{"u": url, "t": titulek}, ...],
     "post":   {token: [idx, tf, idx, tf, ...], ...}}
  peckybot/chunks/<k>.json: pole textů úryvků s indexy k*100 … k*100+99

Pořadí úryvků je chronologické (nejstarší první), takže nová jednání přibývají
na konec a mění se jen poslední dávky. Soubory se přepíšou jen při změně obsahu.

Tokenizace MUSÍ být shodná s peckybot/worker/src/search.ts (funkce tokenize):
malá písmena, bez diakritiky, slova od 3 znaků, zkrácená na prvních 6 znaků
(hrubý stemmer pro češtinu), bez stopslov.

Spouští ho scripts/build.py; samostatně: python3 scripts/build_peckybot_index.py
"""
import html
import json
import math
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'peckybot' / 'index.json'
SHARD_DIR = ROOT / 'peckybot' / 'chunks'

STEM_LEN = 6
MAX_CHUNK = 700          # znaků textu jednoho úryvku
SHARD = 100              # úryvků v jedné dávce peckybot/chunks/<k>.json
MIN_CHUNK = 110          # kratší úryvky (jen název bodu) se neindexují
MAX_DF_RATIO = 0.25      # tokeny ve víc než čtvrtině úryvků se neindexují
STOPWORDS = {
    'aby', 'ale', 'ani', 'jak', 'jako', 'jsou', 'jeho', 'jejich', 'kde', 'kdy',
    'kteri', 'ktery', 'ktera', 'ktere', 'nebo', 'pri', 'pro', 'proc', 'tak',
    'ten', 'the', 'toho', 'tom', 'tato', 'tyto', 'byl', 'byla', 'bylo', 'byt',
    'bude', 'jsem', 'jste', 'jsme', 'mesto', 'mesta', 'mestem', 'pecky', 'pecek',
    'peckach', 'cislo', 'cisl', 'dle', 'ode', 'ani', 'napr', 'tzn', 'atd',
}


def tokenize(text):
    s = unicodedata.normalize('NFD', text.lower())
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    out = []
    for w in re.findall(r'[a-z0-9]+', s):
        if len(w) < 3 or w in STOPWORDS:
            continue
        out.append(w[:STEM_LEN])
    return out


def clip(text, n):
    text = re.sub(r'\s+', ' ', text or '').strip()
    if len(text) <= n:
        return text
    return text[:n].rsplit(' ', 1)[0] + '…'


def meeting_ref(m):
    """('ZM 6/2026', '/jednani/#zastupitelstvo-2026-09-16')"""
    zm = m['type'] == 'Zastupitelstvo'
    short = ('ZM ' if zm else 'RM ') + f"{m['number']}/{m['year']}"
    anchor = ('zastupitelstvo-' if zm else 'rada-') + m['date']
    return short, f'/jednani/#{anchor}'


def cz_date(iso):
    y, m, d = iso.split('-')
    return f'{int(d)}. {int(m)}. {y}'


def chunks_jednani():
    data = json.loads((ROOT / 'jednani/pecky-jednani.json').read_text(encoding='utf-8'))
    out = []
    for m in sorted(data['meetings'], key=lambda x: x['date']):
        short, url = meeting_ref(m)
        kdy = cz_date(m['date'])
        head = f"{short} ({kdy})"
        used = set()
        # usnesení podle názvu bodu
        by_item = {}
        for r in m.get('resolutions', []):
            by_item.setdefault(r['item'], []).append(r)
        for a in m.get('agenda', []):
            parts = [f"{head}, bod {a['n']}: {a['t']}."]
            if a.get('predkladatel'):
                parts.append(f"Předkládá: {a['predkladatel']}.")
            if a.get('duvodova_zprava'):
                parts.append('Důvodová zpráva: ' + clip(a['duvodova_zprava'], 320))
            for r in by_item.get(a['t'], []):
                used.add(a['t'])
                hlasy = ''
                if r.get('pro') is not None:
                    hlasy = f" (pro {r['pro']}, proti {r.get('proti', 0)}, zdrželo se {r.get('zdrzel', 0)})"
                parts.append(f"Usnesení {r['n']}: {clip(r['text'], 380)}{hlasy}")
            text = clip(' '.join(parts), MAX_CHUNK)
            if len(text) < MIN_CHUNK:
                continue
            out.append({'u': url, 't': f'{short} — {a["t"]}', 'x': text})
        for item, rs in by_item.items():
            if item in used:
                continue
            parts = [f"{head}, bod: {item}."]
            for r in rs:
                parts.append(f"Usnesení {r['n']}: {clip(r['text'], 380)}")
            out.append({'u': url, 't': f'{short} — {item}', 'x': clip(' '.join(parts), MAX_CHUNK)})
    return out


ROLE_TAGY = {
    'vedeni-mesta': 'vedení města', 'zastupitel': 'člen zastupitelstva', 'rada': 'člen rady města',
    'komise': 'člen komise', 'urednik': 'zaměstnanec městského úřadu', 'vedeni-uradu': 'vedení úřadu',
    'skolstvi': 'školství', 'kultura': 'kultura', 'sport': 'sport', 'spolky': 'spolky',
    'socialni-sluzby': 'sociální služby', 'zdravotnictvi': 'zdravotnictví',
}


def chunks_lide():
    data = json.loads((ROOT / 'lide/people.json').read_text(encoding='utf-8'))
    out = []
    for p in data['people']:
        bio = (p.get('bio') or '').strip()
        email = (p.get('email') or '').strip()
        phone = (p.get('phone') or '').strip()
        # kontakty jsou v indexu i u lidí bez životopisu
        if not (bio or email or phone):
            continue
        jmeno = ' '.join(x for x in (p.get('title_before'), p.get('first_name'), p.get('last_name'),
                                     p.get('title_after')) if x).strip()
        parts = [f'{jmeno}.']
        if bio:
            parts.append(clip(bio, 600))
        role = [ROLE_TAGY[t] for t in p.get('tags', []) if t in ROLE_TAGY]
        if role:
            parts.append(f"Působení: {', '.join(role)}.")
        occ = sorted(p.get('occupations') or [], key=lambda o: o.get('year', 0), reverse=True)
        if occ and not bio:
            parts.append(f"Zaměstnání: {occ[0]['value']}.")
        if email or phone:
            parts.append('Kontakt:')
        if email:
            parts.append(f'E-mail: {email}.')
        if phone:
            parts.append(f'Telefon: {phone}.')
        out.append({'u': '/lide/', 't': f'Lidé — {jmeno}', 'x': ' '.join(parts)})
    return out


# statické sekce -> (URL, název); dynamické sekce (jednání, noviny, kalendář)
# mají v content/*.html jen kostru, data jsou v JSON
STATICKE = {
    'plan': ('/plan/', 'Strategický plán'),
    'telocvicna': ('/telocvicna/', 'Tělocvična'),
    'pozemky': ('/pozemky/', 'Pozemky'),
    'pokladna': ('/pokladna/', 'Pokladna'),
    'smlouvy': ('/smlouvy/', 'Smlouvy'),
    'zakazky': ('/zakazky/', 'Zakázky'),
    'volby': ('/volby/', 'Volby'),
    'volby2018': ('/volby/2018/', 'Volby 2018'),
    'volby2022': ('/volby/2022/', 'Volby 2022'),
    'volby2026': ('/volby/2026/', 'Volby 2026'),
    'owebu': ('/o-webu/', 'O webu'),
}


def html_to_text(src):
    src = re.sub(r'<(script|style)\b.*?</\1>', ' ', src, flags=re.S | re.I)
    src = re.sub(r'\{\{[^}]*\}\}', ' ', src)
    src = re.sub(r'<br\s*/?>|</(p|li|tr|div|h[1-6]|section)>', '\n', src, flags=re.I)
    src = re.sub(r'</t[dh]>', ' | ', src, flags=re.I)
    src = re.sub(r'<[^>]+>', '', src)
    src = html.unescape(src).replace('\xa0', ' ')
    return [re.sub(r'[ \t]+', ' ', ln).strip() for ln in src.splitlines() if ln.strip()]


def chunks_stranky():
    out = []
    for slug, (url, nazev) in STATICKE.items():
        path = ROOT / 'content' / f'{slug}.html'
        if not path.exists():
            continue
        buf = ''
        for ln in html_to_text(path.read_text(encoding='utf-8')):
            if len(ln) < 3:
                continue
            if buf and len(buf) + len(ln) > MAX_CHUNK:
                out.append({'u': url, 't': f'Web — {nazev}', 'x': buf.strip()})
                buf = ''
            buf += ln + '\n'
        if buf.strip():
            out.append({'u': url, 't': f'Web — {nazev}', 'x': buf.strip()})
    return out


def build_index(chunks):
    n = len(chunks)
    post = {}
    for i, c in enumerate(chunks):
        toks = tokenize(c['t']) * 2 + tokenize(c['x'])  # titulek má dvojnásobnou váhu
        tf = {}
        for t in toks:
            tf[t] = tf.get(t, 0) + 1
        for t, k in sorted(tf.items()):
            post.setdefault(t, []).extend([i, k])
    max_df = max(20, int(n * MAX_DF_RATIO))
    post = {t: v for t, v in sorted(post.items()) if len(v) // 2 <= max_df}
    meta = [{'u': c['u'], 't': c['t']} for c in chunks]
    return {'v': 1, 'shard': SHARD, 'chunks': meta, 'post': post}


def write_if_changed(path, obj):
    data = json.dumps(obj, ensure_ascii=False, separators=(',', ':'))
    if path.exists() and path.read_text(encoding='utf-8') == data:
        return False
    path.write_text(data, encoding='utf-8')
    return True


def main():
    chunks = chunks_jednani() + chunks_lide() + chunks_stranky()
    idx = build_index(chunks)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    SHARD_DIR.mkdir(exist_ok=True)
    zmeneno = write_if_changed(OUT, idx)
    pocet = math.ceil(len(chunks) / SHARD)
    for k in range(pocet):
        texty = [c['x'] for c in chunks[k * SHARD:(k + 1) * SHARD]]
        zmeneno |= write_if_changed(SHARD_DIR / f'{k}.json', texty)
    for stary in SHARD_DIR.glob('*.json'):
        if int(stary.stem) >= pocet:
            stary.unlink()
            zmeneno = True
    kb = OUT.stat().st_size / 1024
    print(f'PečkyBot index: {len(chunks)} úryvků v {pocet} dávkách, {len(idx["post"])} tokenů, '
          f'rejstřík {kb:.0f} kB ({"přepsáno" if zmeneno else "beze změny"})')


if __name__ == '__main__':
    main()
