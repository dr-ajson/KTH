#!/usr/bin/env python3
"""Bygg ett Word-dokument i någon av KTH:s officiella mallar.

    python bygg_word.py spec.json -o dokument.docx

spec.json beskriver mall och innehåll (se references/spec-format.md). Innehållet skrivs
i enkel markdown och formateras med mallens egna formatmallar, så att rubriker,
listor och tabeller blir tillgänglighetsanpassade på det sätt mallen är byggd för.

Kräver python-docx (pip install python-docx).
"""
import argparse
import copy
import json
import re
import sys
import tempfile
import zipfile
from pathlib import Path

from docx import Document
from lxml import etree
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def _hitta(rel):
    """Filen i skillens mappstruktur, eller platt bredvid skriptet (Custom GPT: /mnt/data)."""
    here = Path(__file__).resolve().parent
    for p in (here.parent / rel, here / Path(rel).name, Path("/mnt/data") / Path(rel).name):
        if p.exists():
            return p
    return here.parent / rel



MALLAR = {
    "grundmall": "KTH_Grundmall.dotx",
    "rapport": "KTH_Rapportmall.dotx",
    "beslut": "KTH_Beslutsmall.dotx",
}
STIL = {
    "h1": "Heading 1", "h2": "Heading 2", "h3": "Heading 3",
    "text": "Body Text", "titel": "KTH Titel", "underrubrik": "Subtitle",
    "punkt": ["KTH Punktlista  (Punktlista)", "KTH Punktlista 2  (Punktlista 2)", "KTH Punktlista 3  (Punktlista 3)"],
    "nummer": ["KTH Numrerad lista  (Numrerad lista)", "KTH Numrerad lista 2  (Numrerad lista 2)", "KTH Numrerad lista 3  (Numrerad lista 3)"],
    "tabell": "Table Grid",
}


# ---------------------------------------------------------------- öppna mall

def oppna_mall(namn):
    """Word vägrar spara en .dotx som dokument; byt innehållstyp och öppna som .docx."""
    src = _hitta("assets/" + MALLAR[namn])
    tmp = Path(tempfile.mkdtemp()) / "mall.docx"
    with zipfile.ZipFile(src) as zi, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zo:
        for item in zi.infolist():
            data = zi.read(item.filename)
            if item.filename == "[Content_Types].xml":
                data = data.replace(b"wordprocessingml.template.main+xml",
                                    b"wordprocessingml.document.main+xml")
            zo.writestr(item, data)
    return Document(str(tmp))


# ---------------------------------------------------------------- xml-hjälp

def body_barn(doc):
    return [el for el in doc.element.body if el.tag != qn("w:sectPr")]


def packa_upp_sdt(el):
    """Ersätt innehållskontroller (grå platshållare) inuti ett element med sitt innehåll."""
    for sdt in [x for x in el.iter(qn("w:sdt")) if x is not el]:
        parent = sdt.getparent()
        if parent is None:
            continue
        idx = parent.index(sdt)
        content = sdt.find(qn("w:sdtContent"))
        for child in list(content) if content is not None else []:
            parent.insert(idx, child)
            idx += 1
        parent.remove(sdt)


def satt_text(el, text):
    """Sätt text i ett stycke och behåll formatet på första körningen.
    Tar bort fält (FILLIN, FORMTEXT m.fl.), innehållskontroller och platshållarformat."""
    if el.tag == qn("w:sdt"):  # innehållskontroll på styckenivå
        paras = list(el.find(qn("w:sdtContent")).iter(qn("w:p")))
        el.addprevious(paras[0])
        el.getparent().remove(el)
        el = paras[0]
    packa_upp_sdt(el)
    for r in list(el.iter(qn("w:r"))):
        if r.find(qn("w:fldChar")) is not None or r.find(qn("w:instrText")) is not None:
            r.getparent().remove(r)
    runs = [r for r in el.iter(qn("w:r")) if r.find(qn("w:t")) is not None]
    if not runs:
        r = OxmlElement("w:r")
        el.append(r)
        runs = [r]
    first = runs[0]
    for r in runs[1:]:
        r.getparent().remove(r)
    for t in first.findall(qn("w:t")):
        first.remove(t)
    rpr = first.find(qn("w:rPr"))
    if rpr is not None:
        for rs in rpr.findall(qn("w:rStyle")):
            rpr.remove(rs)
    t = OxmlElement("w:t")
    t.text = text
    t.set(qn("xml:space"), "preserve")
    first.append(t)


def ta_bort(els):
    for el in els:
        if el.getparent() is not None:
            el.getparent().remove(el)


def stil(doc, namn):
    try:
        return doc.styles[namn]
    except KeyError:
        norm = re.sub(r"\s+", " ", namn).casefold()
        for s in doc.styles:
            if re.sub(r"\s+", " ", s.name or "").casefold() == norm:
                return s
    raise KeyError(f"Formatmallen '{namn}' finns inte i mallen")


def sidhuvuden_och_fotter(doc):
    """Alla header-/footer-delar, utan att skapa nya (python-docx skapar annars tomma)."""
    for rel in doc.part.rels.values():
        if rel.reltype in (RT.HEADER, RT.FOOTER):
            yield rel.target_part.element


def ersatt_i_delar(doc, ersattningar):
    """Ersätt platshållartext i sidhuvuden och sidfötter. Nyckeln 'FIELD:X' matchar fältkod X."""
    for part in sidhuvuden_och_fotter(doc):
        for p in part.iter(qn("w:p")):
            txt = "".join(t.text or "" for t in p.iter(qn("w:t")))
            instr = "".join(t.text or "" for t in p.iter(qn("w:instrText")))
            for gammal, ny in ersattningar.items():
                if gammal.startswith("FIELD:"):
                    if gammal[6:] in instr:
                        satt_text(p, ny)
                        break
                elif gammal in txt:
                    satt_text(p, txt.replace(gammal, ny))
                    break


# ---------------------------------------------------------------- markdown

INLINE = re.compile(r"(\*\*[^*]+\*\*|\*[^*]+\*|\[[^\]]+\]\([^)]+\))")


def lagg_till_inline(doc, p, text):
    for del_ in INLINE.split(text):
        if not del_:
            continue
        if del_.startswith("**"):
            p.add_run(del_[2:-2]).bold = True
        elif del_.startswith("*"):
            p.add_run(del_[1:-1]).italic = True
        elif del_.startswith("["):
            m = re.match(r"\[([^\]]+)\]\(([^)]+)\)", del_)
            lank(doc, p, m.group(1), m.group(2))
        else:
            p.add_run(del_)


def lank(doc, p, text, url):
    r_id = doc.part.relate_to(url, RT.HYPERLINK, is_external=True)
    h = OxmlElement("w:hyperlink")
    h.set(qn("r:id"), r_id)
    r = OxmlElement("w:r")
    rpr = OxmlElement("w:rPr")
    rs = OxmlElement("w:rStyle")
    rs.set(qn("w:val"), "Hyperlink")
    rpr.append(rs)
    u = OxmlElement("w:u")
    u.set(qn("w:val"), "single")
    rpr.append(u)
    r.append(rpr)
    t = OxmlElement("w:t")
    t.text = text
    t.set(qn("xml:space"), "preserve")
    r.append(t)
    h.append(r)
    p._p.append(h)


class NumreringsStart:
    """Ger varje numrerad lista egen numrering som börjar på 1."""

    def __init__(self, doc):
        self.doc = doc
        base = stil(doc, STIL["nummer"][0]).element.pPr.numPr.numId.val
        numbering = doc.part.numbering_part.element
        self.numbering = numbering
        num = [n for n in numbering.findall(qn("w:num")) if n.get(qn("w:numId")) == str(base)][0]
        self.abstract = num.find(qn("w:abstractNumId")).get(qn("w:val"))

    def ny(self):
        ids = [int(n.get(qn("w:numId"))) for n in self.numbering.findall(qn("w:num"))]
        nid = max(ids) + 1
        num = OxmlElement("w:num")
        num.set(qn("w:numId"), str(nid))
        a = OxmlElement("w:abstractNumId")
        a.set(qn("w:val"), self.abstract)
        num.append(a)
        ov = OxmlElement("w:lvlOverride")
        ov.set(qn("w:ilvl"), "0")
        so = OxmlElement("w:startOverride")
        so.set(qn("w:val"), "1")
        ov.append(so)
        num.append(ov)
        self.numbering.append(num)
        return nid


def satt_numpr(p, num_id, niva):
    ppr = p._p.get_or_add_pPr()
    for old in ppr.findall(qn("w:numPr")):
        ppr.remove(old)
    numpr = OxmlElement("w:numPr")
    il = OxmlElement("w:ilvl")
    il.set(qn("w:val"), str(niva))
    ni = OxmlElement("w:numId")
    ni.set(qn("w:val"), str(num_id))
    numpr.append(il)
    numpr.append(ni)
    ppr.insert(1 if ppr.find(qn("w:pStyle")) is not None else 0, numpr)


def tabell(doc, rader, fore):
    celler = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rader
              if not re.match(r"^\s*\|?\s*:?-{2,}", r)]
    ncol = max(len(r) for r in celler)
    t = doc.add_table(rows=len(celler), cols=ncol)
    t.style = stil(doc, STIL["tabell"])
    for i, rad in enumerate(celler):
        for j in range(ncol):
            cell = t.cell(i, j)
            cell.paragraphs[0].style = stil(doc, STIL["text"])
            lagg_till_inline(doc, cell.paragraphs[0], rad[j] if j < len(rad) else "")
            if i == 0:
                for r in cell.paragraphs[0].runs:
                    r.bold = True
    # rubrikrad som upprepas och läses som rubrik av skärmläsare
    trpr = t.rows[0]._tr.get_or_add_trPr()
    th = OxmlElement("w:tblHeader")
    trpr.append(th)
    flytta_fore(t._tbl, fore)


def flytta_fore(el, fore):
    if fore is not None:
        fore.addprevious(el)


def markdown(doc, md, fore=None, h_offset=0):
    """Lägg till markdown-innehåll före elementet `fore` (eller sist i dokumentet)."""
    if not md:
        return
    nummer = NumreringsStart(doc)
    lines = md.strip("\n").split("\n")
    i = 0
    stycke = []
    aktiv_lista = None

    def ny_p(stilnamn):
        p = doc.add_paragraph(style=stil(doc, stilnamn))
        flytta_fore(p._p, fore)
        return p

    def toma_stycke():
        if stycke:
            lagg_till_inline(doc, ny_p(STIL["text"]), " ".join(s.strip() for s in stycke))
            stycke.clear()

    while i < len(lines):
        line = lines[i]
        rubrik = re.match(r"^(#{1,3})\s+(.*)", line)
        punkt = re.match(r"^(\s*)[-*]\s+(.*)", line)
        num = re.match(r"^(\s*)\d+[.)]\s+(.*)", line)
        if not line.strip():
            toma_stycke()
            aktiv_lista = None
        elif rubrik:
            toma_stycke()
            aktiv_lista = None
            niva = min(len(rubrik.group(1)) + h_offset, 3)
            lagg_till_inline(doc, ny_p(STIL[f"h{niva}"]), rubrik.group(2))
        elif line.lstrip().startswith("|"):
            toma_stycke()
            aktiv_lista = None
            rader = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                rader.append(lines[i])
                i += 1
            tabell(doc, rader, fore)
            continue
        elif punkt or num:
            toma_stycke()
            m = punkt or num
            niva = min(len(m.group(1).replace("\t", "  ")) // 2, 2)
            if punkt:
                if niva == 0:
                    aktiv_lista = None
                lagg_till_inline(doc, ny_p(STIL["punkt"][niva]), m.group(2))
            else:
                if aktiv_lista is None:
                    aktiv_lista = nummer.ny()
                p = ny_p(STIL["nummer"][niva])
                satt_numpr(p, aktiv_lista, niva)
                lagg_till_inline(doc, p, m.group(2))
        else:
            aktiv_lista = None
            stycke.append(line)
        i += 1
    toma_stycke()


# ---------------------------------------------------------------- mallarna

def grundmall(doc, s):
    barn = body_barn(doc)
    titel_p, under_p = barn[2], barn[3]
    satt_text(titel_p, s["titel"])
    if s.get("underrubrik"):
        satt_text(under_p, s["underrubrik"])
        ta_bort(barn[4:])
    else:
        ta_bort(barn[3:])
    markdown(doc, s.get("innehall", ""))


def rapport(doc, s):
    barn = body_barn(doc)
    body = doc.element.body
    # sidhuvudtabellen på första sidan
    for p in barn[0].iter(qn("w:p")):
        st = p.find(".//" + qn("w:pStyle"))
        st = st.get(qn("w:val")) if st is not None else ""
        if st == "Rapportnamn":
            satt_text(p, s.get("rapportnamn", s["titel"]))
        elif st == "DatumArial7":
            satt_text(p, s.get("datum", ""))
        elif st == "Arial7":
            satt_text(p, s.get("diarienummer", ""))
    for p in barn[1].iter(qn("w:p")):
        if "Namn på nämnd" in "".join(t.text or "" for t in p.iter(qn("w:t"))):
            satt_text(p, s.get("skapat_av", ""))
    ersatt_i_delar(doc, {
        "Namn på rapport": s.get("rapportnamn", s["titel"]),
        '"Namn på nämnd/råd/dylikt"': s.get("skapat_av", ""),
        "FIELD:STYLEREF": s.get("datum", ""),
    })
    satt_text(barn[3], s["titel"])
    if s.get("underrubrik"):
        satt_text(barn[4], s["underrubrik"])
    else:
        ta_bort([barn[4]])
    toc = next((el for el in barn if el.tag == qn("w:sdt")), None)
    ta_bort([el for el in barn[5:] if el is not toc])
    if toc is not None and s.get("innehallsforteckning", True):
        # Mallens förteckning innehåller inaktuella exempelrader. Ersätt dem med ett tomt
        # TOC-fält som Word fyller i (och räknar sidnummer för) när dokumentet öppnas.
        content = toc.find(qn("w:sdtContent"))
        instr = "".join(t.text or "" for t in toc.iter(qn("w:instrText"))) or ' TOC \\o "1-3" \\h \\z \\u '
        for p in list(content):
            if p.find(".//" + qn("w:pStyle")) is None or \
               p.find(".//" + qn("w:pStyle")).get(qn("w:val")) != "TOCHeading":
                content.remove(p)
        p = OxmlElement("w:p")
        for kind, text in (("begin", None), ("instr", instr), ("separate", None),
                           ("text", "Innehållsförteckningen uppdateras när dokumentet öppnas i Word "
                                    "(eller högerklicka här och välj Uppdatera fält)."),
                           ("end", None)):
            r = OxmlElement("w:r")
            if kind in ("begin", "separate", "end"):
                fc = OxmlElement("w:fldChar")
                fc.set(qn("w:fldCharType"), kind)
                if kind == "begin":
                    fc.set(qn("w:dirty"), "true")
                r.append(fc)
            else:
                t = OxmlElement("w:instrText" if kind == "instr" else "w:t")
                t.set(qn("xml:space"), "preserve")
                t.text = text
                r.append(t)
            p.append(r)
        content.append(p)
        settings = doc.settings.element
        uf = OxmlElement("w:updateFields")
        uf.set(qn("w:val"), "true")
        efter = ("hdrShapeDefaults", "footnotePr", "endnotePr", "compat", "docVars", "rsids",
                 "mathPr", "attachedSchema", "themeFontLang", "clrSchemeMapping",
                 "doNotIncludeSubdocsInStats", "doNotAutoCompressPictures", "forceUpgrade",
                 "captions", "readModeInkLockDown", "smartTagType", "schemaLibrary",
                 "shapeDefaults", "doNotEmbedSmartTags", "decimalSymbol", "listSeparator")
        nasta = next((c for c in settings if etree.QName(c).localname in efter), None)
        if nasta is not None:
            nasta.addprevious(uf)  # schemat kräver en bestämd ordning i settings.xml
        else:
            settings.append(uf)
    elif toc is not None:
        ta_bort([toc])
        toc = None
    if s.get("sammanfattning"):
        p = doc.add_paragraph("Sammanfattning", style=stil(doc, STIL["h2"]))
        flytta_fore(p._p, toc)
        markdown(doc, s["sammanfattning"], fore=toc)
    markdown(doc, s.get("innehall", ""))


def beslut(doc, s):
    barn = body_barn(doc)
    idx = {}
    for i, el in enumerate(barn):
        st = el.find(".//" + qn("w:pStyle"))
        st = st.get(qn("w:val")) if st is not None else ""
        idx.setdefault(st, i)
        if "".join(t.text or "" for t in el.iter(qn("w:t"))).strip() == "Sändlista":
            idx["sandlista"] = i
    satt_text(barn[idx["beslutsdatum"]], s.get("beslutsdatum", ""))
    satt_text(barn[idx["diarienummer"]], s.get("diarienummer", ""))
    satt_text(barn[idx["KTHTitel"]], f"Beslut om {s['arendemening']}")
    ersatt_i_delar(doc, {
        "Klicka eller tryck här för att ange datum.": s.get("beslutsdatum", ""),
        "Skriv diarienummer och ks.kod så här: HS-2026-1234 1.2.": s.get("diarienummer", ""),
    })
    sandlista_mall = copy.deepcopy(barn[idx["sandlista"]])
    ta_bort(barn[idx["KTHTitel"] + 1:])

    def rubrik1(text):
        doc.add_paragraph(text, style=stil(doc, STIL["h1"]))

    def text(t):
        p = doc.add_paragraph(style=stil(doc, STIL["text"]))
        lagg_till_inline(doc, p, t)

    rubrik1("Beslutet")
    markdown(doc, s["beslutet"])
    rubrik1("Ärendet")
    markdown(doc, s["arendet"])
    mening = f"Detta beslut har fattats av {s['beslutsfattare']} efter föredragning av {s['foredragande']}."
    if s.get("narvarande"):
        mening += f" Närvarande vid beslutet var {s['narvarande']}."
    text(mening)
    text("Denna handling har hanterats digitalt och är därför inte undertecknad.")
    for n, bilaga in enumerate(s.get("bilagor", []), 1):
        text(f"Bilaga {n}: {bilaga}")
    if s.get("sandlista"):
        doc.add_paragraph()
        doc.element.body.find(qn("w:sectPr")).addprevious(sandlista_mall)
        for mottagare in s["sandlista"]:
            text(mottagare)
    doc.add_paragraph()
    text(f"Expeditionsdatum: {s.get('expeditionsdatum', '')}".rstrip())
    if not s.get("vattenstampel", True):
        for part in sidhuvuden_och_fotter(doc):
            for r in list(part.iter(qn("w:r"))):
                if b"PowerPlusWaterMarkObject" in etree.tostring(r):
                    r.getparent().remove(r)


KRAV = {
    "grundmall": ["titel"],
    "rapport": ["titel"],
    "beslut": ["arendemening", "beslutet", "arendet", "beslutsfattare", "foredragande"],
}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec", help="JSON-fil med mall och innehåll")
    ap.add_argument("-o", "--ut", required=True, help="utfil (.docx)")
    a = ap.parse_args()
    s = json.loads(Path(a.spec).read_text(encoding="utf-8"))
    mall = s.get("mall")
    if mall not in MALLAR:
        sys.exit(f"'mall' måste vara en av {', '.join(MALLAR)}")
    saknas = [k for k in KRAV[mall] if not s.get(k)]
    if saknas:
        sys.exit(f"Saknade fält för {mall}: {', '.join(saknas)}")
    doc = oppna_mall(mall)
    {"grundmall": grundmall, "rapport": rapport, "beslut": beslut}[mall](doc, s)
    doc.core_properties.title = s.get("titel") or f"Beslut om {s.get('arendemening', '')}"
    if s.get("amne"):
        doc.core_properties.subject = s["amne"]
    if s.get("forfattare"):
        doc.core_properties.author = s["forfattare"]
    doc.core_properties.language = s.get("sprak", "sv-SE")
    doc.save(a.ut)
    print(f"Skrev {a.ut}")


if __name__ == "__main__":
    main()
