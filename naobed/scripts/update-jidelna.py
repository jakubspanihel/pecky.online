#!/usr/bin/env python3
"""Stáhne jídelníček školní jídelny z zspecky.cz a uloží dny do měsíčního
archivu naobed/data/skolni-jidelna-pecky/RRRR-MM.json.

Použití (z kořene repa):
    python3 naobed/scripts/update-jidelna.py          # stáhne a zapíše
    python3 naobed/scripts/update-jidelna.py --check  # jen řekne, jestli je potřeba

--check skončí kódem 0, když archiv obsahuje dnešek (pracovní den)
nebo nejbližší další pracovní den, jinak kódem 1.

Dny z webu přepisují stejná data v archivu, ostatní dny zůstanou.
"""
import datetime as dt
import html
import json
import re
import sys
import urllib.request
from pathlib import Path

URL = "https://www.zspecky.cz/jidelna/jidelnicek/"
ARCHIVE = Path(__file__).resolve().parent.parent / "data" / "skolni-jidelna-pecky"

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


def load_archive():
    """Vrátí dny ze všech měsíčních souborů jako {datum: den}."""
    dny = {}
    for path in ARCHIVE.glob("*.json"):
        for d in json.loads(path.read_text(encoding="utf-8"))["dny"]:
            dny[d["date"]] = d
    return dny


def save_archive(dny):
    """Upíše dny do měsíčních souborů; den se stejným datem se přepíše, ostatní zůstanou."""
    by_month = {}
    for d in dny:
        by_month.setdefault(d["date"][:7], []).append(d)
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    for ym, ds in by_month.items():
        path = ARCHIVE / (ym + ".json")
        if path.exists():
            month = json.loads(path.read_text(encoding="utf-8"))
        else:
            month = {"schema": 1, "restaurace": "skolni-jidelna-pecky", "zdroj": URL, "dny": []}
        upd = {d["date"]: d for d in month["dny"]}
        upd.update({d["date"]: d for d in ds})
        month["dny"] = [upd[k] for k in sorted(upd)]
        path.write_text(json.dumps(month, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def main():
    today = dt.date.today()
    have = load_archive()
    need = next_workday(today).isoformat()

    if "--check" in sys.argv:
        ok = need in have
        print(f"archiv {'má' if ok else 'nemá'} {need}")
        sys.exit(0 if ok else 1)

    web = parse(fetch_text(), today)
    if not web:
        print("Na webu se nenašel žádný den jídelníčku — nic nezměněno.", file=sys.stderr)
        sys.exit(2)

    save_archive(web)
    added = sorted(set(d["date"] for d in web) - set(have))
    print(f"Na webu {len(web)} dní ({web[0]['date']} – {web[-1]['date']}), "
          f"nové: {', '.join(added) if added else 'žádné'}; v archivu celkem {len(load_archive())} dní.")


if __name__ == "__main__":
    main()
