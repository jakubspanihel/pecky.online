#!/usr/bin/env python3
"""Render every PDF page as a small preview JPEG for search-result thumbnails.

Requires poppler (pdftoppm) — same package family as pdftotext, used
elsewhere in this project for the fulltext extraction.
"""
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_JSON = ROOT / "pecky-noviny.json"
PDF_DIR = ROOT / "Data"
OUT_DIR = ROOT / "pages"
DPI = 40
QUALITY = 60


def render_edition(slug, pdf_path, page_count):
    out_dir = OUT_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    missing = [p for p in range(1, page_count + 1) if not (out_dir / f"{p}.jpg").exists()]
    if not missing:
        return 0

    tmp_prefix = out_dir / "_tmp"
    subprocess.run(
        ["pdftoppm", "-jpeg", "-r", str(DPI), "-jpegopt", f"quality={QUALITY}",
         str(pdf_path), str(tmp_prefix)],
        check=True, capture_output=True,
    )

    count = 0
    for f in sorted(out_dir.glob("_tmp-*.jpg")):
        m = re.search(r"_tmp-0*(\d+)\.jpg$", f.name)
        page_num = int(m.group(1))
        f.rename(out_dir / f"{page_num}.jpg")
        count += 1
    return count


def main():
    with open(DATA_JSON, encoding="utf-8") as f:
        d = json.load(f)

    total = 0
    for e in d["editions"]:
        slug = e["slug"]
        pdf_path = PDF_DIR / f"PN {e['year']}" / f"{slug}.pdf"
        if not pdf_path.exists():
            print(f"skip {slug}: PDF missing in Data/PN {e['year']}/")
            continue
        n = render_edition(slug, pdf_path, e["page_count"])
        if n:
            print(f"{slug}: rendered {n} pages")
        total += n

    print(f"\nDone. {total} new page images rendered into pages/.")


if __name__ == "__main__":
    main()
