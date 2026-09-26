#!/usr/bin/env python3
"""Bygg en Excel-arbetsbok från KTH:s mall (KTH.xltx) med KTH:s färger.

    python bygg_excel.py spec.json -o arbetsbok.xlsx

Mallen KTH.xltx ger Arial som typsnitt, men dess temafärger är en äldre, icke-KTH-palett.
Skriptet byter därför temat till KTH:s primär- och funktionsfärger, så att diagram och
färgväljaren i Excel följer den grafiska profilen. Se references/spec-format.md.
Kräver openpyxl.
"""
import argparse
import json
import re
import tempfile
import zipfile
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.chart import BarChart, LineChart, PieChart, Reference
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo

def _hitta(rel):
    """Filen i skillens mappstruktur, eller platt bredvid skriptet (Custom GPT: /mnt/data)."""
    here = Path(__file__).resolve().parent
    for p in (here.parent / rel, here / Path(rel).name, Path("/mnt/data") / Path(rel).name):
        if p.exists():
            return p
    return here.parent / rel


MALL = _hitta("assets/KTH.xltx")

# Infografikordningen i KTH:s grafiska manual
SERIEFARGER = ["004791", "6298D2", "000061", "E86A58", "78001A", "339C9C",
               "1C434C", "4DA060", "0D4A21", "FFBE00", "A65900"]
TEMA = {  # samma temafärger som KTH:s Word- och PowerPoint-mallar använder
    "dk2": "000061", "lt2": "EBE5E0", "accent1": "004791", "accent2": "6198D2",
    "accent3": "000061", "accent4": "DEF0FF", "accent5": "EBE5DF", "accent6": "0028ED",
    "hlink": "3878C2",
}
RUBRIK_FYLL = PatternFill("solid", fgColor="004791")
RUBRIK_FONT = Font(name="Arial", bold=True, color="FFFFFF")


def oppna_mall():
    tmp = Path(tempfile.mkdtemp()) / "mall.xlsx"
    with zipfile.ZipFile(MALL) as zi, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zo:
        for item in zi.infolist():
            data = zi.read(item.filename)
            if item.filename == "[Content_Types].xml":
                data = data.replace(b"spreadsheetml.template.main+xml", b"spreadsheetml.sheet.main+xml")
            if item.filename == "xl/theme/theme1.xml":
                text = data.decode("utf-8")
                for slot, hex_ in TEMA.items():
                    text = re.sub(rf"(<a:{slot}>\s*<a:(?:srgbClr val|sysClr [^>]*lastClr)=\")[0-9A-Fa-f]{{6}}",
                                  rf"\g<1>{hex_}", text)
                data = text.encode("utf-8")
            zo.writestr(item, data)
    wb = load_workbook(tmp)
    wb.template = False
    return wb


def skriv_blad(ws, blad):
    rader = blad["rader"]
    kolumner = blad["kolumner"]
    ws.append(kolumner)
    for rad in rader:
        ws.append(rad)
    n_rad, n_kol = len(rader) + 1, len(kolumner)
    for c in ws[1]:
        c.fill, c.font = RUBRIK_FYLL, RUBRIK_FONT
        c.alignment = Alignment(vertical="center", wrap_text=True)
    ref = f"A1:{get_column_letter(n_kol)}{n_rad}"
    namn = re.sub(r"\W", "_", blad.get("tabellnamn", ws.title))[:250] or "Tabell"
    t = Table(displayName=namn if namn[0].isalpha() else "T_" + namn, ref=ref)
    t.tableStyleInfo = TableStyleInfo(name="TableStyleLight1", showRowStripes=True)
    ws.add_table(t)
    ws.freeze_panes = "A2"
    for i, kol in enumerate(kolumner, 1):
        bredd = max([len(str(kol))] + [len(str(r[i - 1])) for r in rader if i - 1 < len(r)])
        ws.column_dimensions[get_column_letter(i)].width = min(max(10, bredd + 2), 60)
    for kol, fmt in (blad.get("format") or {}).items():
        idx = kolumner.index(kol) + 1
        for row in ws.iter_rows(min_row=2, min_col=idx, max_col=idx):
            row[0].number_format = fmt
    if blad.get("diagram"):
        diagram(ws, blad["diagram"], kolumner, n_rad)


def diagram(ws, d, kolumner, n_rad):
    typ = d.get("typ", "stapel")
    ch = {"stapel": BarChart, "linje": LineChart, "cirkel": PieChart}[typ]()
    ch.title = d.get("titel")
    x = kolumner.index(d["x"]) + 1
    for i, serie in enumerate(d["y"]):
        y = kolumner.index(serie) + 1
        ch.add_data(Reference(ws, min_col=y, min_row=1, max_row=n_rad), titles_from_data=True)
    ch.set_categories(Reference(ws, min_col=x, min_row=2, max_row=n_rad))
    if typ != "cirkel":
        for i, s in enumerate(ch.series):
            farg = SERIEFARGER[i % len(SERIEFARGER)]
            s.graphicalProperties.solidFill = farg
            s.graphicalProperties.line.solidFill = farg
        ch.y_axis.title = d.get("y_titel")
        ch.x_axis.title = d.get("x_titel")
    ch.width, ch.height = 18, 9
    ws.add_chart(ch, f"{get_column_letter(len(kolumner) + 2)}2")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec")
    ap.add_argument("-o", "--ut", required=True)
    a = ap.parse_args()
    spec = json.loads(Path(a.spec).read_text(encoding="utf-8"))
    wb = oppna_mall()
    forsta = wb.active
    for i, blad in enumerate(spec["blad"]):
        ws = forsta if i == 0 else wb.create_sheet()
        ws.title = blad["namn"][:31]
        skriv_blad(ws, blad)
    wb.properties.title = spec.get("titel", spec["blad"][0]["namn"])
    wb.save(a.ut)
    print(f"Skrev {a.ut}")


if __name__ == "__main__":
    main()
