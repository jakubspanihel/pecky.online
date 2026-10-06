#!/usr/bin/env python3
"""Přepíše naobed/jidelna.json z jídelníčku školní jídelny na zspecky.cz.

Použití (z kořene repa):
    python3 naobed/scripts/update-jidelna.py          # stáhne a zapíše
    python3 naobed/scripts/update-jidelna.py --check  # jen řekne, jestli je potřeba

--check skončí kódem 0, když jidelna.json obsahuje dnešek (pracovní den)
nebo nejbližší další pracovní den, jinak kódem 1.

Dny z webu se sloučí s dosavadními (web má přednost), dny starší než
7 dní se zahodí. Pole `checked` = dnešní datum.
"""
import datetime as dt
import html
import json
import re
import sys
import urllib.request
from pathlib import Path

URL = "https://www.zspecky.cz/jidelna/jidelnicek/"
PATH = Path(__file__).resolve().parent.parent / "jidelna.json"
KEEP_DAYS = 7

DAY_RE = re.compile(r"^(Po|Út|St|Čt|Pá)\s+(\d{1,2})\.\s*(\d{1,2})\.\s*$")
SOUP_RE = re.compile(r"^Polévka\s*:\s*(.*)$", re.I)
MEAL_RE = re.compile(r"^\d\)\s*(.*)$")


def clean(s):
    s = re.sub(r"\s+", " ", s).strip()
    # alergeny „( 1a, 3,7 )“ → „(1a, 3, 7)“, „( 1a, )“ → „(1a)“
    def fix(m):
        parts = [p.strip() for p in m.group(1).split(",") if p.strip()]
        return "(" + ", ".join(parts) + ")" if parts else ""
    s = re.sub(r"\(([^()]*)\)", fix, s)
    s = re.sub(r"\s+", " ", s).strip(" ,")
    s = re.sub(r"\s+,", ",", s)
    return s


def fetch_text():
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0 pecky.online"})
    raw = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    raw = re.sub(r"<script.*?</script>|<style.*?</style>", "", raw, flags=re.S)
    text = html.unescape(re.sub(r"<[^>]+>", "\n", raw)).replace("​", "")
    return [l.strip() for l in text.splitlines() if l.strip()]


def parse(lines, today):
    dny, cur = [], None
    for line in lines:
        m = DAY_RE.match(line)
        if m:
            d, mth = int(m.group(2)), int(m.group(3))
            year = today.year
            # přelom roku: prosincový den v lednu → loni, lednový v prosinci → příští rok
            if today.month == 1 and mth == 12:
                year -= 1
            elif today.month == 12 and mth == 1:
                year += 1
            cur = {"date": dt.date(year, mth, d).isoformat(), "polevka": "", "jidla": []}
            dny.append(cur)
            continue
        if cur is None:
            continue
        m = SOUP_RE.match(line)
        if m and not cur["polevka"]:
            cur["polevka"] = clean(m.group(1))
            continue
        m = MEAL_RE.match(line)
        if m and len(cur["jidla"]) < 2:
            cur["jidla"].append(clean(m.group(1)))
            continue
        if cur["polevka"] and len(cur["jidla"]) >= 2:
            cur = None  # konec bloku dne
    return [d for d in dny if d["polevka"] or d["jidla"]]


def next_workday(today):
    d = today
    while d.weekday() >= 5:
        d += dt.timedelta(days=1)
    return d


def main():
    today = dt.date.today()
    data = json.loads(PATH.read_text(encoding="utf-8")) if PATH.exists() else {}
    have = {d["date"] for d in data.get("dny", [])}
    need = next_workday(today).isoformat()

    if "--check" in sys.argv:
        ok = need in have
        print(f"jidelna.json {'má' if ok else 'nemá'} {need}")
        sys.exit(0 if ok else 1)

    web = parse(fetch_text(), today)
    if not web:
        print("Na webu se nenašel žádný den jídelníčku — nic nezměněno.", file=sys.stderr)
        sys.exit(2)

    merged = {d["date"]: d for d in data.get("dny", [])}
    merged.update({d["date"]: d for d in web})
    cutoff = (today - dt.timedelta(days=KEEP_DAYS)).isoformat()
    dny = [merged[k] for k in sorted(merged) if k >= cutoff]

    new = {"source": URL, "checked": today.isoformat(), "dny": dny}
    PATH.write_text(json.dumps(new, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    added = sorted(set(d["date"] for d in web) - have)
    print(f"Na webu {len(web)} dní ({web[0]['date']} – {web[-1]['date']}), "
          f"nové: {', '.join(added) if added else 'žádné'}; v souboru {len(dny)} dní.")


if __name__ == "__main__":
    main()
