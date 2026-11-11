#!/usr/bin/env python3
"""Přehled účtů ze sekce „Sociální sítě“ v content/owebu.html.

Vypíše u každého účtu odkaz, dosavadní počet sledujících a datum poslední
aktivity (stav před kontrolou). Jen čte, nic nezapisuje.
Použití: python3 o-webu/socialni-site-prehled.py
"""
import re
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "content" / "owebu.html"

html = SRC.read_text(encoding="utf-8")
start = html.find('id="subpanel-owebu-socialni"')
if start < 0:
    sys.exit("CHYBA: v content/owebu.html chybí id=\"subpanel-owebu-socialni\"")
end = html.find('class="footer-note"', start)
blok = html[start:end if end > 0 else len(html)]

radky = []
for m in re.finditer(r'<a class="qlink" href="([^"]*)".*?</a>', blok, re.S):
    a = m.group(0)
    href = m.group(1)
    if href.startswith("/"):  # interní stránky (monitoring) se neprocházejí
        continue
    pocet = re.search(r'follower-count">([^<]*)', a)
    datum = re.search(r'data-date="([^"]*)"', a)
    radky.append((href, pocet.group(1) if pocet else "—",
                  datum.group(1) if datum else "—"))

for href, pocet, datum in radky:
    print(f"{pocet:<22} {datum:<11} {href}")
print(f"\nÚčtů: {len(radky)}")
