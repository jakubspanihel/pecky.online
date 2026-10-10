#!/usr/bin/env python3
"""Jednání Rady a Zastupitelstva přetištěná v Pečeckých novinách (2001–7/2015).

Vstup:  noviny/Data/PN RRRR/*.pdf (vrstva textu, 2001–2011) a noviny/pecky-noviny.json
        (OCR skenů 2012–2015, `pages`).
Výstup: jednani/noviny-jednani.json — tvar záznamu jako starsi-jednani.json,
        group "noviny", text = přepis zápisu / usnesení z novin.
Spuštění:  python3 jednani/scripts/noviny-jednani.py [--review]
"""
import json, re, subprocess, sys, os, glob

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..'))
NOV = os.path.join(ROOT, 'noviny')
OUT = os.path.join(ROOT, 'jednani', 'noviny-jednani.json')
CUTOFF = '2015-06-08'          # od tohoto dne jsou zápisy na úřední desce (starsi-jednani.json)
LAST_ISSUE = '2015-07'         # poslední číslo novin, ze kterého se berou jednání před CUTOFF

DATE_OVERRIDE = {   # datum v nadpisu je v novinách chybně; správné vyplývá z textu (zápis dozorčí rady 18. 2., komise 20. 2., schůzka 17. 3. 2014)
    ('2014-04', '2014-02-03'): '2014-03-03',
}
MONTHS = 'ledna února března dubna května června července srpna září října listopadu prosince'.split()
FIX_GLYPH = str.maketrans({'!': 'ř', '"': 'ě', '%': 'š', '(': 'ý'})   # vadný font 2001–2006


def mon(s):
    s = s.lower()
    if s.startswith('červenc') or s.startswith('července'):
        return 7
    if s.startswith('červ'):
        return 6
    for i, m in enumerate(MONTHS):
        if i not in (5, 6) and s.startswith(m[:4]):
            return i + 1
    return None


_CACHE = os.environ.get('NOVINY_CACHE')   # volitelná mezipaměť extrakce textu (urychluje ladění)


def issue_pages(slug):
    """Seznam stran vydání (text každé strany, v pořadí čtení)."""
    if _CACHE:
        cf = os.path.join(_CACHE, slug + '.json')
        if os.path.exists(cf):
            return json.load(open(cf))
    pages = _issue_pages(slug)
    if _CACHE:
        os.makedirs(_CACHE, exist_ok=True)
        json.dump(pages, open(os.path.join(_CACHE, slug + '.json'), 'w'), ensure_ascii=False)
    return pages


def _issue_pages(slug):
    y = int(slug[:4])
    if y <= 2011 and slug != '2001-06':      # 2001-06: textová vrstva PDF má špatné kódování znaků → text z pecky-noviny.json
        pdf = os.path.join(NOV, 'Data', 'PN %d' % y, slug + '.pdf')
        n = int(re.search(r'Pages:\s+(\d+)', subprocess.run(['pdfinfo', pdf], capture_output=True, text=True).stdout).group(1))
        pages = []
        for p in range(1, n + 1):
            t = subprocess.run(['pdftotext', '-f', str(p), '-l', str(p), pdf, '-'], capture_output=True, text=True).stdout
            if y <= 2006:
                t = t.translate(FIX_GLYPH).replace('Peřk', 'Pečk').replace('Peřek', 'Peček')
            if slug == '2009-08':      # zdrojové PDF má text zrcadlově po znacích (viz noviny/README.md)
                t = '\n'.join(l[::-1] for l in t.split('\n'))
            pages.append(t)
        return pages
    global _J
    try:
        _J
    except NameError:
        _J = {e['slug']: e for e in json.load(open(os.path.join(NOV, 'pecky-noviny.json')))['editions']}
    return [p if isinstance(p, str) else p.get('text', '') for p in _J[slug]['pages']]


JUNK = re.compile(r'^(\d{1,2}|\d{1,2} ?/ ?20\d\d|Pečecké noviny|PN \d+\.pmd.*|=== str.*)\s*$')
BULLET = re.compile(r'^\s*[–—\-•]\s')


TEXT_FIXES = {   # poškozená data nadpisů, ověřeno v PDF (viz noviny/rada-zastupitelstvo-pred-2015-06.md)
    '2012-01': [('ze dne 1%. prosince 2011', 'ze dne 14. prosince 2011'), ('ze dne 1\u00bb. prosince 2011', 'ze dne 14. prosince 2011')],
    '2014-05': [('konaná dne 1%. dubna', 'konaná dne 14. dubna')],
    '2013-03': [('konaného dne ž. 2. 2013', 'konaného dne 4. 2. 2013'), ('konaná dne %. února 2013', 'konaná dne 4. února 2013')],   # ověřeno v PDF
    '2012-06': [('konaná dne 1%. května 2012', 'konaná dne 14. května 2012')],
    '2013-07-08': [('konaná dne 2%. června 2013', 'konaná dne 24. června 2013')],
    '2015-01': [('konaná dne 2%. istopadu 201%', 'konaná dne 24. listopadu 2014')],   # ověřeno v PDF
    '2014-04': [('konaná dne 8. února 2014', 'konaná dne 3. února 2014')],   # OCR; v novinách chybně „února“ — viz DATE_OVERRIDE
}


def clean_lines(pages, slug=None):
    """[(strana, řádek)] — bez čísel stran a patiček, rozdělená slova slepená zpět."""
    out = []
    for pg, t in enumerate(pages, 1):
        for a, b in TEXT_FIXES.get(slug, []):
            t = t.replace(a, b)
        for l in t.replace('\f', '').split('\n'):
            l = l.rstrip()
            if JUNK.match(l.strip()):
                continue
            out.append((pg, l))
    return out


def dehyphenate(lines):
    res = []
    for pg, l in lines:
        if res and res[-1][1] and re.search(r'[a-zěščřžýáíéúůňťďó][−\-‑–]$', res[-1][1]) and l and l[0].islower():
            res[-1] = (res[-1][0], res[-1][1][:-1] + l)
        else:
            res.append((pg, l))
    return res


DATE = re.compile(r'(\d{1,2})\s*\.?\s*(?:(\d{1,2})\s*\.|([^\W\d_]{4,10}))\s*(\S{3,5})?')
RMH = re.compile(r'^(Mimořádná\s+)?Rad[ay]\s+m\S+\s+Pe\S+\s*$')


def parse_date(s, slug):
    m = DATE.search(s)
    if not m:
        return None
    d = int(m.group(1))
    mo = int(m.group(2)) if m.group(2) else mon(m.group(3))
    if not mo or not 1 <= mo <= 12 or not 1 <= d <= 31:
        return None
    iy, im = int(slug[:4]), int(slug[5:7])
    y = m.group(4) or ''
    y = int(y) if re.fullmatch(r'20\d\d', y) else None
    if y is not None and not 0 <= (iy * 12 + im) - (y * 12 + mo) <= 8:
        y = None   # rok ve zdroji nesedí k číslu vydání (překlep / OCR)
    if y is None:
        # rok se nepodařilo přečíst (OCR „201%“) nebo je v novinách překlep → podle čísla vydání
        y = iy if mo <= im else iy - 1
    return '%04d-%02d-%02d' % (y, mo, d), bool(m.group(4) and re.fullmatch(r'20\d\d', m.group(4)))


def find_blocks(slug):
    lines = dehyphenate(clean_lines(issue_pages(slug), slug))
    if slug == '2009-08':   # sloupce zrcadlově obráceného čísla jsou ve špatném pořadí: nadpis RM 29. 6. 2009 (řádky 88–130) předchází pokračování (43–71)
        lines = lines[:43] + lines[88:131] + lines[43:72] + lines[72:88] + lines[131:]
    if slug == '2010-08':   # mezi nadpisem RM 1. 7. 2010 a jeho textem je vložený článek „Poděkování a omluva“
        a = next(i for i, x in enumerate(lines) if x[1].strip() == 'Poděkování a omluva')
        b = next(i for i, x in enumerate(lines) if x[1].startswith('Jednání rady města zahájil') and i > a)
        keep = [x for x in lines[a:b] if x[1].startswith('konaná dne')]
        lines = lines[:a] + keep + lines[b:]
    starts = []   # (index, type, date, number)
    for i, (pg, l) in enumerate(lines):
        s = l.strip()
        if RMH.match(s):
            ctx = ' '.join(x[1] for x in lines[i + 1:i + 5])
            m = re.search(r'kon\S+\s+dne\s+(.{0,40})', ctx)
            if m and parse_date(m.group(1), slug):
                starts.append((i, 'Rada', parse_date(m.group(1), slug)[0], None, pg))
        elif (re.match(r'^Usnesení\b', s) or re.match(r'^z\s+veřejného\s+zasedání\s+[Zz]astupitelstva', s)) \
                and not re.match(r'^Usnesení\s+(z|ze)\b.*Rad', s) and not (starts and starts[-1][0] >= i - 4 and starts[-1][1] == 'Zastupitelstvo'):
            ctx = ' '.join(x[1] for x in lines[i:i + 6])
            if re.search(r'[Zz]astupitelstv', ctx) and re.search(r'přijímá\s*toto', ' '.join(x[1] for x in lines[i:i + 12])):
                m = re.search(r'(?:kon\S+\s+(?:dne\s+)?|ze\s+dne\s+|\bdne:?\s+)(\d.{0,40})', ctx)
                nm = re.search(r'Usnesení\s+(?:[čř]\.\s*)?(\d{1,2})\b', ctx) or re.search(r'č\.\s*(\d{1,2})\s*/\s*20\d\d', ctx)
                if m and parse_date(m.group(1), slug):
                    starts.append((i, 'Zastupitelstvo', parse_date(m.group(1), slug)[0],
                                   int(nm.group(1)) if nm else None, pg))
    if slug == '2001-06':       # článek „Z jednání Rady města Peček“ (bez nadpisu „konaná dne“)
        i = next(k for k, x in enumerate(lines) if x[1].startswith('Z jednání Rady'))
        starts.append((i, 'Rada', '2001-06-04', None, lines[i][0]))
    return lines, starts


STRUCT = re.compile(r'^(?:[IVX]+\.\s*)?(Rada|Zastupitelstvo)\s+(města\s+)?(bere|schvaluje|neschvaluje|ukládá|doporučuje|pověřuje|souhlasí|revokuje|'
                    r'konstatuje|ruší|odkládá|rozhodla|projednala|stanovuje|vyhlašuje|jmenuje|volí|zamítá|bere na vědomí|ukládá|přijímá)', re.I)


ABBR = re.compile(r'(?:\b(?:Ing|Mgr|Bc|JUDr|MUDr|RNDr|PhDr|Ing\.arch|p|pí|pí\.|č|čp|tj|tzn|resp|popř|ul|Tř|sv|Sb|odst|písm|parc|k\.ú|k\. ú|a|s|r|o|č\.j|cca|např|apod|atd|Kč|m|tel|J|M|P|V|Z|K)\.|[,(–—/-])$')
END_MARK = re.compile(r'[.;)"“”:]\s+[=mBL®■]\s*$')   # OCR značky konce článku (■ čtené jako = m > B L)
FOOT = re.compile(r'^\d{1,2}\.\d{1,2}\.20\d\d, \d{1,2}:\d\d$')


SIG = re.compile(r'^(Ověřovatelé|Milan Urban,? starosta|Milan Urban$)', re.I)


def zm_end(lines, a, nxt):
    """Usnesení ZM končí podpisy (Ověřovatelé / starosta, místostarostové); jinak se vrací None."""
    last_struct = a
    for j in range(a, nxt):
        if STRUCT.match(lines[j][1].strip()):
            last_struct = j
    for j in range(last_struct, min(nxt, last_struct + 400)):
        if SIG.match(lines[j][1].strip()):
            e = j + 1
            while e < nxt and e < j + 6:
                t = lines[e][1].strip()
                if t and (len(t) <= 48 or re.search(r'starosta|Tvrz|Krištoufek', t)) and not STRUCT.match(t):
                    e += 1
                elif not t:
                    e += 1
                else:
                    break
            while not lines[e - 1][1].strip():
                e -= 1
            return e
    return None


def block_end(lines, a, nxt, raw=False):
    """Konec bloku: další nadpis, ■ (u skenů) nebo první odstavec, který už zjevně není zápis."""
    last_struct = a
    for j in range(a, nxt):
        if STRUCT.match(lines[j][1].strip()):
            last_struct = j
    mark = None
    for j in range(last_struct, nxt):
        if '■' in lines[j][1] or (not raw and END_MARK.search(lines[j][1])):
            mark = j + 1
            break
    h = _heur_end(lines, a, nxt, raw, last_struct)
    e = h if mark is None else (mark if (mark <= h or mark - h <= 25) else h)
    if mark is None and nxt - e <= 40:      # zbytek do dalšího nadpisu je krátký → patří k témuž jednání
        e = nxt
    return e


def title_caps(l):
    letters = [c for c in l if c.isalpha()]
    return len(letters) >= 6 and sum(c.isupper() for c in letters) / len(letters) > 0.6


def _heur_end(lines, a, nxt, raw, last_struct):
    # po poslední skupině „Rada ukládá:“ jde seznam odrážek; končí prvním neodrážkovým odstavcem
    j = last_struct + 1
    items = 0
    last = last_struct
    while j < nxt:
        l = lines[j][1].strip()
        if not l or len(l) <= 2 or FOOT.match(l):
            if not l and items and raw:      # u textové vrstvy značí prázdný řádek konec sloupce nebo článku
                k = j + 1
                while k < nxt and not lines[k][1].strip():
                    k += 1
                if k < nxt:
                    nl = lines[k][1].strip()
                    pl = lines[last][1].strip()
                    if re.search(r'[.;)"“”!?]$', pl) and not ABBR.search(pl) and not BULLET.match(nl) \
                            and not STRUCT.match(nl) and not re.match(r'^([a-z]\)|\d+[.)]|[IVX]+\.)\s', nl):
                        return last + 1
            j += 1
            continue
        if BULLET.match(l) or re.match(r'^([a-z]\)|\d+[.)]|[IVX]+\.)\s', l):
            items += 1
        elif items and l[0].isupper() and re.search(r'[.;)"“”]$', lines[last][1].strip()) \
                and not ABBR.search(lines[last][1].strip()) and not re.match(r'^(\d+\.|[a-z]\))', l) and not STRUCT.match(l) \
                and ((len(l) <= 55 and not re.search(r'[.,;:]$', l)) or title_caps(l)):
            return last + 1       # nový nadpis / článek
        last = j
        j += 1
    return last + 1 if last > a else nxt


CUT = {   # id → text posledního řádku zápisu (ruční oříznutí tam, kde za zápisem následuje jiný článek; ověřeno v PDF)
    'rada-2001-06-04': 'ulici „V Kaštánkách“.',
    'zastupitelstvo-2014-11-05': 'Marcela, členka.',
    'zastupitelstvo-2013-02-04': 'Rozpočtová opatření č. 9/2012',
    'rada-2008-03-03': 'z účtu FRB na vkladovém účtu u České spořitelny',
    'rada-2008-07-07': 'soukromému zemědělci Ing. Bartákovi prodat.',
    'rada-2009-02-02': 'včetně členů komisí.',
    'rada-2011-06-06': 'do konce září 2011.',
    'rada-2012-02-06': 'oblast vzdělávání MŠ Pečky.',
    'rada-2012-06-11': 'předložit min. 3 nabídky.',
    'rada-2012-12-03': 'záměru od 1. 1. 2013 na dobu neurčitou.',
    'rada-2013-07-15': 'tovní haly.',
    'rada-2013-12-09': 'Tajemníkovi zjistit cenu opravy',
    'zastupitelstvo-2010-04-21': 'prioritní osy č. 4.',
    'zastupitelstvo-2011-06-22': 'Kmochova, Grégrova).',
    'zastupitelstvo-2011-12-14': 'své působnosti.',
    'zastupitelstvo-2012-04-25': 'stavebního zákona.',
    'zastupitelstvo-2012-09-05': 'o výměře 97m.',
    'zastupitelstvo-2012-10-31': 'V Horkách a Hellichova parku v Pečkách.',
    'zastupitelstvo-2013-03-13': 'uhradí strana kupující.',
    'zastupitelstvo-2013-09-11': 'Ing. Jiřímu',
    'zastupitelstvo-2014-03-12': 'mezi obcí Radim a městem Pečky.',
    'zastupitelstvo-2014-07-07': 'Rozpočtová opatření č. 4/2014.',
    'zastupitelstvo-2014-09-17': 'Bažantnici čp. 400.',
    'zastupitelstvo-2015-03-11': 'Tř. 5. května 215, Pečky.',
}
EXT = {   # id → text posledního řádku, když automatické ukončení zápis předčasně utne
}
DROP = {  # id → podřetězce řádků vsunutých z okolních článků (reklamní rámečky apod.)
    'rada-2001-06-04': ['První z obou koncepcí představi', 'lo sdružení stavebních firem CMKS', 'Z jednání Rady', 'města Peček'],
    'zastupitelstvo-2013-03-13': ['svoz BIO ODPADU', 'jde BIO odpad', 'áždé pondělí', '25. 11. 2013.', 'obec Radim nevyváží', 'fie odpad', 'Za vedení města Pěčky',
                                  'Město Pečky', 'nabízí k pronájmu', 'byt ve Velkých Chvalovicích', 'o celkové výměře 36', 'Byt je určen pro osoby', 'se sníženou soběstačností'],
}
TRIM = {   # id → text, za kterým se přepis ořízne i uvnitř řádku (vsuvka ve stejném řádku OCR)
    'zastupitelstvo-2013-02-04': 'Rozpočtová opatření č. 9/2012',
}
PARTIAL = {   # id → poznámka: text v novinách pokračuje, strojový přepis se na tomto místě přerušuje
    'rada-2007-12-03': 'Sloupce stránky jsou v textové vrstvě PDF promíchané, konec zápisu je nekompletní.',
    'rada-2009-10-05': 'Konec zápisu může být neúplný.',
    'rada-2012-12-03': 'Text zápisu pokračuje na stránce za vsunutým článkem; přepis je zkrácený.',
    'rada-2014-02-03': 'Konec zápisu může být neúplný.',
    'rada-2015-04-13': 'Konec zápisu může být neúplný.',
    'zastupitelstvo-2013-09-11': 'Text usnesení pokračuje za vsunutým článkem; přepis je zkrácený.',
}


def reflow(txt):
    """Slepí zalomené řádky sloupců do odstavců; odrážky, nadpisy a výčty zůstávají na samostatných řádcích."""
    out = []
    for l in txt.split('\n'):
        t = l.strip()
        if not t:
            if out and out[-1] != '':
                out.append('')
            continue
        new_item = bool(BULLET.match(t) or STRUCT.match(t) or re.match(r'^([a-z]\)|\d+[.)/]|[IVX]+\.)\s', t)
                        or re.match(r'^(Rada|Rady|Zastupitelstv\w+|Mimořádná|Usnesení|Přítomn|Omluv|Nepřítomn|Ověřovatel|Zapsal|Jednání|konan|Pro:|Proti:|Zdržel)', t)
                        or (title_caps(t) and len(t) < 60))
        if out and out[-1] != '' and not new_item:
            prev = out[-1]
            if not re.search(r'[.;:!?)“”"]$', prev) or ABBR.search(prev) or t[0].islower():
                out[-1] = prev + ' ' + t
                continue
        out.append(t)
    return '\n'.join(out).strip()


def build():
    meetings = {}
    problems = []
    for pdf in sorted(glob.glob(os.path.join(NOV, 'Data', 'PN *', '*.pdf'))):
        slug = os.path.basename(pdf)[:-4]
        if slug > LAST_ISSUE:
            continue
        lines, starts = find_blocks(slug)
        for k, (i, typ, date, num, pg) in enumerate(starts):
            if date >= CUTOFF:
                continue
            nxt = starts[k + 1][0] if k + 1 < len(starts) else len(lines)
            end = block_end(lines, i, nxt, int(slug[:4]) <= 2011)
            if typ == 'Zastupitelstvo':
                end = nxt if nxt - i < 250 else (zm_end(lines, i, nxt) or end)
            _id = ('rada-' if typ == 'Rada' else 'zastupitelstvo-') + DATE_OVERRIDE.get((slug, date), date)
            if _id in CUT:
                hit = [j for j in range(i, nxt) if CUT[_id] in lines[j][1]]
                if hit:
                    end = hit[0] + 1
                else:
                    problems.append('CUT nenalezen: ' + _id)
            if _id in EXT:
                hit = [j for j in range(end, nxt) if EXT[_id] in lines[j][1]]
                if hit:
                    end = hit[0] + 1
                else:
                    problems.append('EXT nenalezen: ' + _id)
            body = [l for _, l in lines[i:end] if not any(d in l for d in DROP.get(_id, []))]
            txt = reflow('\n'.join(body))
            if _id in TRIM:
                txt = txt[:txt.index(TRIM[_id]) + len(TRIM[_id])]
            txt = re.sub(r'(?<=[.;)"“”:\d])\s+[=mBL®■]\s*$', '', txt)
            txt = re.sub(r'\n{3,}', '\n\n', txt).strip()
            date = DATE_OVERRIDE.get((slug, date), date)
            mid = ('rada-' if typ == 'Rada' else 'zastupitelstvo-') + date
            rec = dict(partial=PARTIAL.get(_id), _after=' ⏎ '.join(l for _, l in lines[end:end + 4] if l.strip()), slug=slug, page=pg, type=typ, date=date, number=num, text=txt, nlines=end - i, nxt_gap=nxt - end)
            if mid in meetings:      # totéž jednání otištěno ve dvou číslech — ponechat první, druhé uvést jako `also`
                meetings[mid].setdefault('also', []).append((slug, pg))
                continue
            meetings[mid] = rec
    return meetings, problems


def issue_label(slug):
    y, m = slug[:4], slug[5:]
    if '-' in m:
        a, b = m.split('-')
        return '%d–%d/%s' % (int(a), int(b), y)
    return '%d/%s' % (int(m), y)


def cz(d):
    y, m, dd = d.split('-')
    return '%d. %d. %s' % (int(dd), int(m), y)


def main():
    meetings, problems = build()
    out = []
    for mid, r in sorted(meetings.items(), key=lambda kv: (kv[1]['date'], kv[1]['type'])):
        zm = r['type'] == 'Zastupitelstvo'
        num = r['number']
        label = ('ZM č. %d/%s (%s)' % (num, r['date'][:4], cz(r['date']))) if (zm and num) else \
                (('ZM (%s)' if zm else 'Rada (%s)') % cz(r['date']))
        out.append({
            'id': mid, 'uuid': None, 'type': r['type'], 'group': 'noviny',
            'number': num if zm else None, 'year': int(r['date'][:4]), 'date': r['date'], 'label': label,
            'doc_kind': 'usnesení' if zm else 'zápis',
            'doc_title': (('Usnesení ZM č. %d/%s' % (num, r['date'][:4]) if num else 'Usnesení ZM') if zm else 'Zápis z jednání RM') + ' v Pečeckých novinách %s, s. %d' % (issue_label(r['slug']), r['page']),
            'posted': None,
            'source': 'Pečecké noviny %s, s. %d' % (issue_label(r['slug']), r['page']),
            'links': {'minutes': '/noviny/Data/PN%%20%s/%s.pdf#page=%d' % (r['slug'][:4], r['slug'], r['page'])},
            'file': None, 'ocr': int(r['slug'][:4]) >= 2012,
            'text': r['text'],
            'text_note': r['partial'],
            '_after': r['_after'],
        })
    rada = sum(1 for x in out if x['type'] == 'Rada')
    data = {
        'meta': {
            'updated': __import__('datetime').date.today().isoformat(),
            'source': 'Pečecké noviny (Město Pečky) — viz noviny/',
            'note': 'Zápisy Rady a usnesení Zastupitelstva, která vyšla v Pečeckých novinách 2001–7/2015 (před začátkem zápisů na úřední desce, 8. 6. 2015). Text je strojový přepis stránky novin (u skenů 2012–2015 po OCR), odkaz vede na tu stranu PDF.',
            'counts': {'Rada': rada, 'Zastupitelstvo': len(out) - rada},
        },
        'meetings': out,
    }
    for x in out:
        x.pop('_after', None) if '--review' not in sys.argv else None
    json.dump(data, open(OUT, 'w'), ensure_ascii=False, indent=1)
    print(len(out), 'jednání,', rada, 'RM')
    for p in problems:
        print('!', p)
    if '--review' in sys.argv:
        for x in out:
            t = x['text'].split('\n')
            print('=' * 8, x['id'], x['source'], len(t), 'řádků')
            print('   ', ' ⏎ '.join(t[:2])[:140]); print('   …', ' ⏎ '.join(t[-3:])[:260]); print('   >>', x.get('_after', '')[:200])


def tail(mid, n=25):
    meetings, _ = build_all()
    r = meetings[mid]
    L = r['text'].split('\n')
    for k, l in enumerate(L[-n:], len(L) - min(n, len(L))):
        print(k, l[:170])
    print('>> after:', r['_after'][:300])


if __name__ == '__main__':
    if '--tail' in sys.argv:
        i = sys.argv.index('--tail')
        meetings, _ = build()
        n = int(sys.argv[i + 1])
        for mid in sys.argv[i + 2:]:
            print('####', mid)
            L = meetings[mid]['text'].split('\n')
            for k in range(max(0, len(L) - n), len(L)):
                print(k, L[k][:190])
            print('>> after:', meetings[mid]['_after'][:260])
    else:
        main()
