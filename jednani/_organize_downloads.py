#!/usr/bin/env python3
"""Organize jednani PDFs downloaded into ~/Downloads by the browser-driven
archive process (see README "Stahovani pozvanek a podepsanych zapisu").

Chrome auto-downloads both document types directly (no inline PDF viewer,
no click needed) once configured per that README section. Two facts drive
the matching logic here:

  - "Podepsany zapis" downloads reliably for every meeting.
  - "Pozvanka" (invitation) only succeeds for a subset of meetings -- for
    many (mostly older) meetings the site itself errors out generating it
    (a real server-side gap, not an automation bug). A failed request
    produces NO file at all, so pending count and download count can
    legitimately differ.

Given that, matching is done per single kind (one pass = one kind), not
by raw download order: downloaded files are matched to the requested
chunk by the (number, year) parsed from the filename. Rada and
Zastupitelstvo each restart numbering at 1 every year, so the same
(number, year) can appear twice in one chunk -- those rare collisions are
disambiguated by relative order *within that (number, year) group only*
(download order preserves request order for same-key items).

Usage:
  _pending_chunk.py zapis 15 > /tmp/chunk.json
  ... browser_batch navigates each meeting's zapis url in chunk order ...
  _organize_downloads.py zapis /tmp/chunk.json

  _pending_chunk.py pozvanka 15 > /tmp/chunk.json
  ... browser_batch navigates each meeting's invitation url in chunk order ...
  _organize_downloads.py pozvanka /tmp/chunk.json
"""
import hashlib
import json
import re
import shutil
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

DOWNLOADS = Path.home() / "Downloads"
ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "Data"
JSON_PATH = ROOT / "pecky-jednani.json"

ZAPIS_RE = re.compile(r"[Zz]ápis z jednání č\.\s*(\d+)-(\d+)")
POZVANKA_RE = re.compile(r"Pozvanka-na-jednani-anonymizov[^-]*-(\d+)-(\d+)")
KIND_FILENAME = {"zapis": "podepsany-zapis.pdf", "pozvanka": "pozvanka.pdf"}
KIND_RE = {"zapis": ZAPIS_RE, "pozvanka": POZVANKA_RE}


def normalize(s):
    # macOS stores filenames in NFD (decomposed) form; normalize to NFC so
    # the accented literals in the regexes above match reliably.
    return unicodedata.normalize("NFC", s)


def classify(path, kind):
    m = KIND_RE[kind].search(normalize(path.name))
    return (int(m.group(1)), int(m.group(2))) if m else None


def collisions_by_date():
    data = json.loads(JSON_PATH.read_text())
    by_date = {}
    for m in data["meetings"]:
        by_date.setdefault(m["date"], []).append(m)
    return {d for d, ms in by_date.items() if len(ms) > 1}


def folder_for(m, collisions):
    return f"{m['date']}-{m['type'].lower()}" if m["date"] in collisions else m["date"]


def organize(kind, chunk_path, dry_run=False):
    chunk = json.loads(Path(chunk_path).read_text())
    collisions = collisions_by_date()
    dest_filename = KIND_FILENAME[kind]

    candidates = [p for p in DOWNLOADS.glob("*.pdf") if classify(p, kind) is not None]
    candidates.sort(key=lambda p: p.stat().st_mtime)

    exp_groups = defaultdict(list)
    for m in chunk:
        exp_groups[(m["number"], m["year"])].append(m)
    cand_groups = defaultdict(list)
    for p in candidates:
        cand_groups[classify(p, kind)].append(p)

    moved, missing, problems = 0, 0, 0
    for key, exp_list in exp_groups.items():
        cand_list = cand_groups.get(key, [])
        if len(cand_list) < len(exp_list):
            missing += len(exp_list) - len(cand_list)
        elif len(cand_list) > len(exp_list):
            print(f"WARNING: {key} has {len(cand_list)} downloaded but only {len(exp_list)} requested -- extra/stale files?")
            problems += 1
        for m, path in zip(exp_list, cand_list):
            dest_dir = DATA_DIR / folder_for(m, collisions)
            dest = dest_dir / dest_filename
            if dest.exists():
                print(f"skip (exists), deleting duplicate: {dest.relative_to(ROOT)}  <- {path.name}")
                if not dry_run:
                    path.unlink()
                continue
            if dry_run:
                print(f"[dry-run] {dest.relative_to(ROOT)}  <- {path.name}")
                continue
            dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(path), str(dest))
            size_kb = dest.stat().st_size / 1024
            print(f"{dest.relative_to(ROOT)}  ({size_kb:.0f} KB)  <- {path.name}")
            moved += 1

    unresolved = sum(len(v) for v in cand_groups.values()) - sum(
        min(len(exp_groups.get(k, [])), len(v)) for k, v in cand_groups.items()
    )
    print(f"\nkind={kind} moved={moved} missing(no file produced)={missing} problems={problems} unresolved_extra_files={unresolved}")

    if not dry_run:
        check_duplicate_content(dest_filename)


def check_duplicate_content(dest_filename):
    """The site occasionally serves the WRONG document for a request under
    rapid sequential navigation (confirmed: two different meetings, same
    number but different type/date, ended up byte-identical). Flag any
    archived files sharing content across different meeting folders so the
    affected pair can be re-fetched individually."""
    hashes = defaultdict(list)
    for f in DATA_DIR.glob(f"*/{dest_filename}"):
        hashes[hashlib.md5(f.read_bytes()).hexdigest()].append(f)
    dupes = {h: paths for h, paths in hashes.items() if len(paths) > 1}
    if dupes:
        print(f"\n*** DATA INTEGRITY WARNING: duplicate {dest_filename} content across meetings ***")
        for paths in dupes.values():
            print("  " + "  ==  ".join(str(p.relative_to(ROOT)) for p in paths))
        print("  -> delete both and re-fetch each individually (one navigation at a time, no batching)")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--dry-run"]
    if len(args) < 2:
        print("usage: _organize_downloads.py <zapis|pozvanka> <chunk.json> [--dry-run]")
        sys.exit(1)
    organize(args[0], args[1], dry_run="--dry-run" in sys.argv)
