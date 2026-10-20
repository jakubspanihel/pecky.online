#!/usr/bin/env python3
"""Označí procedurální a rutinní body programu příznakem `"routine": true`.

Spouští se po přidání nového jednání (idempotentní — příznak jen doplní/odebere
podle názvu bodu). Na webu se rutinní bod vykreslí netučně, ostatní tučně.
Použití: python3 jednani/scripts/oznac-rutinni-body.py [--dry]
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# (soubor, odsazení JSON)
FILES = [("pecky-jednani.json", 2), ("komise.json", 1), ("skolska-rada.json", 1), ("vybory.json", 2)]

ROUTINE = re.compile(
    r"^(zahájení( jednání)?|přivítání\b.*|úvodní informace|kontrola zápisu z minulého jednání|určení (zapisovatel|ověřovatel).*|volba (zapisovatel|ověřovatel).*"
    r"|schválení programu( jednání)?( - schválení programu jednání)?"
    r"|kontrola (plnění usnesení|úkolů|průběhu investičních akcí)\b.*"
    r"|úkoly vyplývající z jednání (rady|zastupitelstva) města"
    r"|(aktuální )?informace vedení města( o aktuální situaci ve městě)?"
    r"|probíhající investiční akce ve městě"
    r"|informativní schůzka s (ředitel\w+|ředitl\w+) příspěvkových organizací"
    r"|((různé|diskuse|diskuze|další informace|dotazy a připomínky( občanů)?|závěr)(,| a )? ?)+"
    r")\.?$"
)
# kombinace „různé, úkoly vyplývající…“ apod.
PARTS = re.compile(r"\s*(,| a )\s*")


def is_routine(t: str) -> bool:
    t = re.sub(r"\s+", " ", t.strip().lower())
    if ROUTINE.match(t):
        return True
    parts = [p for p in PARTS.split(t) if p not in (",", " a ", "")]
    return len(parts) > 1 and all(ROUTINE.match(p) for p in parts)


def main(dry=False):
    for name, indent in FILES:
        p = ROOT / name
        if not p.exists():
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        ms = d["meetings"] if isinstance(d, dict) and "meetings" in d else d
        n = changed = 0
        for m in ms:
            for a in m.get("agenda") or []:
                r = is_routine(a.get("t", ""))
                if r:
                    n += 1
                if r != bool(a.get("routine")):
                    changed += 1
                    if r:
                        a["routine"] = True
                    else:
                        a.pop("routine", None)
        print(f"{name}: rutinních {n}, změněno {changed}")
        if changed and not dry:
            p.write_text(json.dumps(d, ensure_ascii=False, indent=indent) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main("--dry" in sys.argv)
