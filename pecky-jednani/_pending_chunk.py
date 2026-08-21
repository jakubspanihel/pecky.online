#!/usr/bin/env python3
"""Print the next N pending meetings for one document kind, as a JSON list
of {date, number, year, type, url} -- drives the batch download process.
See README "Stahovani pozvanek a podepsanych zapisu".

Usage: _pending_chunk.py <pozvanka|zapis> <n>
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
kind_arg = sys.argv[1] if len(sys.argv) > 1 else "zapis"
n = int(sys.argv[2]) if len(sys.argv) > 2 else 15

KIND_MAP = {
    "pozvanka": ("pozvanka.pdf", "invitation"),
    "zapis": ("podepsany-zapis.pdf", "pdf"),
}
filename, link_key = KIND_MAP[kind_arg]

data = json.loads((ROOT / "pecky-jednani.json").read_text())
meetings = data["meetings"]
by_date = {}
for m in meetings:
    by_date.setdefault(m["date"], []).append(m)
collisions = {d for d, ms in by_date.items() if len(ms) > 1}


def folder_for(m):
    return f"{m['date']}-{m['type'].lower()}" if m["date"] in collisions else m["date"]


pending = []
for m in meetings:
    f = ROOT / "Data" / folder_for(m)
    if not (f / filename).exists():
        pending.append(m)

pending.sort(key=lambda m: m["date"])
chunk = pending[:n]
out = [
    {
        "date": m["date"],
        "number": m["number"],
        "year": m["year"],
        "type": m["type"],
        "url": m["links"][link_key],
    }
    for m in chunk
]
print(json.dumps(out, ensure_ascii=False))
print(f"# kind={kind_arg} remaining after this chunk: {len(pending) - len(chunk)}", file=sys.stderr)
