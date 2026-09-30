"""České pevné mezery (NBSP) — pravidla viz TYPOGRAFIE.md.

`nbsp_html(html)` upraví jen textové uzly uvnitř <body>; značky, atributy,
<script>, <style>, <pre>, <code>, <textarea> a <title> nechá být.
JS obdoba pro dynamicky generovaný text: assets/common.js (`peckyNbsp`).
Pravidla držet v obou souborech shodná.
"""
import re

NBSP = ' '
MESICE = 'ledna|února|března|dubna|května|června|července|srpna|září|října|listopadu|prosince'
JEDNOTKY = (r'km|m|cm|mm|kg|g|t|l|ha|m²|m³|m2|m3|%|°C|Kč|Kc|EUR|CZK|ks|'
            r'tis\.|mil\.|mld\.|hod\.|min\.|let')
TITULY = (r'Ing|Bc|Mgr|MUDr|JUDr|PhDr|RNDr|MVDr|Ph\.D|MBA|DiS|doc|prof|arch|'
          r'MgA|BcA|ThDr|PaedDr|CSc|mjr|plk|kpt|por|npor|gen|pplk')
VICE = r'do|na|po|za|od|ve|ke|se|ze|že|či|pro|při|nad|pod|před|přes|bez|což|aby|když'
ZKRATKY = r'str|obr|tab|č|čl|odst|písm|příl|kap|čp|ev|pozn'

# (regulární výraz, náhrada) — aplikují se postupně
PRAVIDLA = [
    # 1. jednopísmenné předložky a spojky
    (re.compile(r'(?<!\w)([KkSsVvZzOoUuAaIi]) (?=\S)'), r'\1' + NBSP),
    # 1b. vícepísmenné předložky a spojky (estetické)
    (re.compile(r'(?<!\w)((?:' + VICE + r'|atd\.)) (?=\S)', re.I), r'\1' + NBSP),
    # 2. číslo + jednotka
    (re.compile(r'(\d) (?=(?:' + JEDNOTKY + r')(?![\w]))'), r'\1' + NBSP),
    (re.compile(r'\b(tis\.|mil\.|mld\.) (?=Kč)'), r'\1' + NBSP),
    # tisícové oddělovače: 4 500, 1 234 567
    (re.compile(r'(?<![\d.,])(\d{1,3}) (?=\d{3}(?!\d))'), r'\1' + NBSP),
    (re.compile(r'(?<=\d' + NBSP + r'\d{3}) (?=\d{3}(?!\d))'), NBSP),
    # 3. data: 24. prosince, 1. 5. 2026
    (re.compile(r'\b(\d{1,2}\.) (?=(?:\d{1,2}\.|\d{4}|' + MESICE + r')(?!\w))'), r'\1' + NBSP),
    # 4. tituly a oslovení před jménem
    (re.compile(r'\b((?:' + TITULY + r')\.) (?=[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ])'), r'\1' + NBSP),
    (re.compile(r'\b(pan|pana|panu|paní) (?=[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ])'), r'\1' + NBSP),
    # 5. zkratky + číslo, č. j., §
    (re.compile(r'\b((?:' + ZKRATKY + r')\.) (?=\d)'), r'\1' + NBSP),
    (re.compile(r'\b(č\.) (?=j\.)'), r'\1' + NBSP),
    (re.compile(r'\b(j\.) (?=\d)'), r'\1' + NBSP),
    (re.compile(r'(§) (?=\d)'), r'\1' + NBSP),
]

_SKIP = r'script|style|pre|code|textarea|title'
_TOKENY = re.compile(
    r'(<!--.*?-->|<(' + _SKIP + r')\b[^>]*>.*?</\2\s*>|<[^>]+>)', re.S | re.I)


def nbsp_text(text):
    for rx, nahrada in PRAVIDLA:
        text = rx.sub(nahrada, text)
    return text


def nbsp_html(html):
    m = re.search(r'<body\b[^>]*>', html, re.I)
    start = m.end() if m else 0
    hlava, telo = html[:start], html[start:]
    casti = _TOKENY.split(telo)
    # split s 2 skupinami vrací [text, celá značka, název, text, ...]
    out = []
    for i, cast in enumerate(casti):
        if i % 3 == 0:
            out.append(nbsp_text(cast))
        elif i % 3 == 1:
            out.append(cast)
    return hlava + ''.join(out)
