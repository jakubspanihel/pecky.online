#!/usr/bin/env python3
"""Download all Pečecké noviny PDFs from pecky-noviny.json into Data/."""
import json
import re
import subprocess
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_JSON = ROOT / "pecky-noviny.json"
OUT_DIR = ROOT / "Data"

MONTHS = {
    "leden": "01", "únor": "02", "březen": "03", "duben": "04",
    "květen": "05", "červen": "06", "červenec": "07", "srpen": "08",
    "září": "09", "říjen": "10", "listopad": "11", "prosinec": "12",
}

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"


def slugify_label(label: str, year: int) -> str:
    label = label.lower().replace("–", "-")
    parts = re.split(r"[\s-]+", label)
    month_nums = []
    for p in parts:
        p = p.strip()
        if p in MONTHS:
            month_nums.append(MONTHS[p])
    if not month_nums:
        return f"{year}-{unicodedata.normalize('NFKD', label).encode('ascii','ignore').decode()}"
    return f"{year}-" + "-".join(month_nums)


def main():
    with open(DATA_JSON) as f:
        d = json.load(f)
    editions = d["editions"]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    ok, skipped, failed = 0, 0, 0
    for e in editions:
        name = slugify_label(e["label"], e["year"]) + ".pdf"
        year_dir = OUT_DIR / f"PN {e['year']}"
        year_dir.mkdir(parents=True, exist_ok=True)
        dest = year_dir / name
        if dest.exists() and dest.stat().st_size > 0:
            skipped += 1
            continue
        print(f"Downloading {e['label']:25s} -> {name}")
        r = subprocess.run(
            ["curl", "-sS", "-f", "-L", "-A", UA, "-o", str(dest), e["url"]],
            capture_output=True, text=True,
        )
        if r.returncode != 0 or not dest.exists() or dest.stat().st_size == 0:
            print(f"  FAILED: {r.stderr.strip()}")
            failed += 1
            if dest.exists():
                dest.unlink()
        else:
            ok += 1

    print(f"\nDone. downloaded={ok} skipped(existing)={skipped} failed={failed} total={len(editions)}")


if __name__ == "__main__":
    main()
