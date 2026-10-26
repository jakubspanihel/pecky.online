#!/usr/bin/env python3
"""Zapíše denní menu restaurace do naobed/data/<id>/RRRR-MM.json a aktualizuje naobed/menu.json.

Použití (z kořene repa):
    python3 naobed/scripts/zapis-menu.py <restaurace-id> <record.json>
    python3 naobed/scripts/zapis-menu.py <restaurace-id> --checked

<record.json> je záznam dne (popis polí v naobed/README.md, sekce „Záznam dne“).
Den se zapíše do měsíčního souboru podle pole `date`; záznam se stejným datem
se přepíše, ostatní dny zůstanou. V menu.json se nastaví `date` (jen pokud je
den stejný nebo novější než dosavadní) a `checked` = dnešní datum. Fotografie
se neukládají, záznam je jediný výstup.
`--checked` nastaví jen `checked` (restaurace bez nového menu).
Oznámení (`notice`) se nemění.
"""
import datetime as dt
import json
import re
import sys
from pathlib import Path

NAOBED = Path(__file__).resolve().parent.parent
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def fail(msg):
    sys.exit("zapis-menu: " + msg)


def check_record(rec, rest_id):
    date = rec.get("date", "")
    if not DATE_RE.match(date):
        fail("pole `date` musí být RRRR-MM-DD, je %r" % date)
    if not rec.get("jidla") and not rec.get("menu"):
        fail("záznam nemá žádná jídla ani `menu`")
    return date


def main(argv):
    if len(argv) != 3:
        fail("použití: zapis-menu.py <restaurace-id> <record.json> | --checked")
    rest_id, arg = argv[1], argv[2]
    today = dt.date.today().isoformat()

    restaurace = load(NAOBED / "restaurace.json")["restaurace"]
    if rest_id not in [r["id"] for r in restaurace]:
        fail("restaurace %r není v naobed/restaurace.json (v seznamu „restaurace“)" % rest_id)

    menu_path = NAOBED / "menu.json"
    menu = load(menu_path)
    entry = menu.setdefault("restaurace", {}).setdefault(rest_id, {"checked": today})

    if arg == "--checked":
        entry["checked"] = today
        save(menu_path, menu)
        print("%s: checked %s" % (rest_id, today))
        return

    rec = load(Path(arg))
    date = check_record(rec, rest_id)

    month_path = NAOBED / "data" / rest_id / (date[:7] + ".json")
    if month_path.exists():
        month = load(month_path)
    else:
        month = {"schema": 1, "restaurace": rest_id, "dny": []}
    month["dny"] = [d for d in month["dny"] if d.get("date") != date] + [rec]
    month["dny"].sort(key=lambda d: d["date"])
    save(month_path, month)

    if not entry.get("date") or date >= entry["date"]:
        entry["date"] = date
    entry["checked"] = today
    save(menu_path, menu)
    print("%s: %s zapsáno do %s, menu.json: date %s" % (
        rest_id, date, month_path.relative_to(NAOBED.parent), entry["date"]))


if __name__ == "__main__":
    main(sys.argv)
