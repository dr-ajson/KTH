#!/usr/bin/env python3
"""Konverterar KTH:s svensk-engelska ordbok (xlsx) till den CSV som skillen använder.

Kör när KTH publicerar en ny version av ordboken:

    python tools/build_ordlista.py source/kth-ordbok-2027-07-01.xlsx

Skriver skills/kth-ordlista/references/ordlista.csv och uppdaterar versionsraden
i skills/kth-ordlista/references/ordlista-info.md.
"""
import csv
import re
import sys
from datetime import datetime
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "skills" / "kth-ordlista" / "references"
HEADERS = ["svensk_term", "engelsk_oversattning", "synonymer", "kalla",
           "anmarkning", "definition", "senast_andrad"]
EXPECTED = ["Svensk term", "Engelsk översättning", "Synonymer", "Källa",
            "Anmärkning", "Definition", "Senast ändrat"]


def clean(value):
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d")
    return re.sub(r"\s+", " ", str(value)).strip()


def main(xlsx_path: str) -> None:
    wb = openpyxl.load_workbook(xlsx_path, read_only=True)
    ws = wb.worksheets[0]
    rows = ws.iter_rows(values_only=True)
    header = [clean(c) for c in next(rows)][:7]
    if header != EXPECTED:
        sys.exit(f"Oväntade kolumner: {header}\nFörväntade: {EXPECTED}")

    records = []
    for row in rows:
        values = [clean(c) for c in row[:7]]
        if values[0]:
            records.append(values)
    records.sort(key=lambda r: r[0].casefold())

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUT_DIR / "ordlista.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(HEADERS)
        writer.writerows(records)

    version = re.search(r"(\d{4}-\d{2}-\d{2})", ws.title or Path(xlsx_path).name)
    version = version.group(1) if version else "okänd"
    info = OUT_DIR / "ordlista-info.md"
    if info.exists():
        text = info.read_text(encoding="utf-8")
        text = re.sub(r"Version: .*", f"Version: {version} ({len(records)} poster)", text)
        info.write_text(text, encoding="utf-8")
    print(f"Skrev {len(records)} poster, version {version}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
