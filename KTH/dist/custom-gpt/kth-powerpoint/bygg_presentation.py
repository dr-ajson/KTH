#!/usr/bin/env python3
"""Bygg en PowerPoint-presentation i KTH:s officiella mall (KTH.potx).

    python bygg_presentation.py spec.json -o presentation.pptx
    python bygg_presentation.py --layouter        # lista alla layouter i mallen

Se references/spec-format.md för specifikationen. Kräver python-pptx.
"""
import argparse
import copy
import json
import re
import sys
import tempfile
import zipfile
from pathlib import Path

from pptx import Presentation
from pptx.oxml.ns import qn

def _hitta(rel):
    """Filen i skillens mappstruktur, eller platt bredvid skriptet (Custom GPT: /mnt/data)."""
    here = Path(__file__).resolve().parent
    for p in (here.parent / rel, here / Path(rel).name, Path("/mnt/data") / Path(rel).name):
        if p.exists():
            return p
    return here.parent / rel


MALL = _hitta("assets/KTH.potx")

# Korta namn -> layoutnamn i KTH.potx
LAYOUT = {
    "titel": "Title, KTH blue",
    "titel-marin": "Title, navy blue",
    "titel-bild": "Title, image",
    "kapitel": "Title/chapter, light blue",
    "kapitel-sand": "Title/chapter, sand",
    "kapitel-kthbla": "Title/chapter, KTH blue",
    "kapitel-marin": "Title/chapter, navy blue",
    "kapitel-bild": "Title/chapter, image, light blue",
    "kapitel-bild-sand": "Title/chapter, image, sand",
    "kapitel-bild-kthbla": "Title/chapter, image, KTH blue",
    "kapitel-bild-marin": "Title/chapter, image, navy blue",
    "innehall": "Headline and content",
    "innehall-bla-linjer": "Headline and content, blue lines",
    "innehall-sand-linjer": "Headline and content, sand lines",
    "innehall-ljusbla": "Headline and content, light blue ",
    "innehall-sand": "Headline and content, sand",
    "innehall-topp": "Headline and content, top",
    "tva-delar": "Two parts",
    "tva-delar-underrubrik": "Two parts, subheader",
    "text-och-bild": "Text and image",
    "jamforelse": "Comparison, light blue",
    "jamforelse-sand": "Comparison, sand",
    "jamforelse-kthbla": "Comparison, KTH blue",
    "jamforelse-marin": "Comparison, navy blue",
    "jamforelse-gron": "Comparison, green",
    "jamforelse-turkos": "Comparison, teal",
    "jamforelse-rod": "Comparison, red",
    "jamforelse-gul": "Comparison, yellow",
    "bild": "Headline and 1 image",
    "tva-bilder": "Headline and 2 images",
    "tre-bilder": "Headline and 3 images",
    "fyra-bilder": "Headline and 4 images",
    "rubrik": "Headline only",
    "rubrik-ljusbla": "Headline only, light blue",
    "rubrik-sand": "Headline only, sand",
    "tom": "Empty",
    "logga": "Logo",
    "logga-marin": "Logo, navy blue",
}


def oppna_mall():
    tmp = Path(tempfile.mkdtemp()) / "mall.pptx"
    with zipfile.ZipFile(MALL) as zi, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zo:
        for item in zi.infolist():
            data = zi.read(item.filename)
            if item.filename == "[Content_Types].xml":
                data = data.replace(b"presentationml.template.main+xml",
                                    b"presentationml.presentation.main+xml")
            zo.writestr(item, data)
    prs = Presentation(str(tmp))
    # ta bort mallens exempelbilder (instruktioner och tomma exempel)
    sldIdLst = prs.slides._sldIdLst
    for sldId in list(sldIdLst):
        prs.part.drop_rel(sldId.rId)
        sldIdLst.remove(sldId)
    return prs


def hitta_layout(prs, namn):
    namn = LAYOUT.get(namn, namn)
    for layout in prs.slide_masters[0].slide_layouts:
        if layout.name.strip().casefold() == namn.strip().casefold():
            return layout
    sys.exit(f"Okänd layout '{namn}'. Kör --layouter för att se alternativen.")


def ph(slide, idx):
    for p in slide.placeholders:
        if p.placeholder_format.idx == idx:
            return p
    return None


INLINE = re.compile(r"(\*\*[^*]+\*\*|\*[^*]+\*)")


def skriv(tf, text, punktstil=False):
    """Skriv text eller markdownpunkter ('- ', indrag = nivå) i en textram."""
    if isinstance(text, list):
        text = "\n".join(f"- {t}" for t in text)
    rader = [r for r in str(text).split("\n") if r.strip()]
    tf.clear()
    for i, rad in enumerate(rader):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        m = re.match(r"^(\s*)[-*]\s+(.*)", rad)
        if m:
            p.level = min(len(m.group(1).replace("\t", "  ")) // 2, 4)
            rad = m.group(2)
        elif punktstil:
            # löptext utan punkt i en platshållare som annars har punkter
            pPr = p._p.get_or_add_pPr()
            pPr.set("marL", "0")
            pPr.set("indent", "0")
            pPr.insert(0, pPr.makeelement(qn("a:buNone"), {}))
        for del_ in INLINE.split(rad.strip()):
            if not del_:
                continue
            r = p.add_run()
            if del_.startswith("**"):
                r.text, r.font.bold = del_[2:-2], True
            elif del_.startswith("*"):
                r.text, r.font.italic = del_[1:-1], True
            else:
                r.text = del_


def satt(slide, idx, varde):
    if varde is None:
        return
    p = ph(slide, idx)
    if p is None:
        return
    if p.placeholder_format.type is not None and "PICTURE" in str(p.placeholder_format.type):
        bild = p.insert_picture(str(varde["fil"] if isinstance(varde, dict) else varde))
        if isinstance(varde, dict) and varde.get("alt"):
            bild._element.xpath("./p:nvPicPr/p:cNvPr")[0].set("descr", varde["alt"])
        return
    skriv(p.text_frame, varde, punktstil="OBJECT" in str(p.placeholder_format.type))


def rensa_tomma(slide):
    """Tomma platshållare syns som 'Klicka för att lägga till text' – ta bort dem."""
    for p in list(slide.placeholders):
        if p.has_text_frame and not p.text_frame.text.strip():
            p._element.getparent().remove(p._element)


def sidfot(slide, text, nummer):
    """Kopiera layoutens sidfot och bildnummer till bilden (motsvarar Infoga > Sidhuvud och sidfot)."""
    for lp in slide.slide_layout.placeholders:
        idx = lp.placeholder_format.idx
        if (idx == 11 and text) or (idx == 12 and nummer):
            el = copy.deepcopy(lp._element)
            slide.shapes._spTree.append(el)
            if idx == 11:
                shape = [s for s in slide.placeholders if s.placeholder_format.idx == 11][-1]
                shape.text_frame.text = text


FALT = {
    # nyckel i spec -> platshållarindex, per typ av layout
    "rubrik": 0, "underrubrik": 1, "text": 1, "vanster": 1, "hoger": 2,
    "bild": 13, "bild2": 14, "bild3": 15, "bild4": 16,
}


def bygg(spec, ut):
    prs = oppna_mall()
    for n, b in enumerate(spec["bilder"], 1):
        layout = hitta_layout(prs, b.get("layout", "innehall"))
        slide = prs.slides.add_slide(layout)
        namn = layout.name
        satt(slide, 0, b.get("rubrik"))
        if namn.startswith("Title,"):
            satt(slide, 1, b.get("underrubrik"))
        elif namn.startswith("Title/chapter"):
            satt(slide, 1, b.get("underrubrik") or b.get("text"))
            satt(slide, 13, b.get("bild"))
        elif namn.startswith("Two parts, subheader"):
            satt(slide, 1, b.get("vanster_rubrik"))
            satt(slide, 2, b.get("vanster"))
            satt(slide, 3, b.get("hoger_rubrik"))
            satt(slide, 4, b.get("hoger"))
        elif namn.startswith("Two parts"):
            satt(slide, 1, b.get("vanster"))
            satt(slide, 2, b.get("hoger"))
        elif namn.startswith("Comparison"):
            satt(slide, 1, b.get("vanster") or b.get("text"))
            satt(slide, 14, b.get("hoger_rubrik"))
            satt(slide, 13, b.get("hoger"))
        elif "image" in namn:
            satt(slide, 1, b.get("text"))
            bilder = b.get("bilder") or ([b["bild"]] if b.get("bild") else [])
            texter = b.get("bildtexter", [])
            bild_ph = sorted(p.placeholder_format.idx for p in slide.placeholders
                             if "PICTURE" in str(p.placeholder_format.type))
            text_ph = sorted(p.placeholder_format.idx for p in slide.placeholders
                             if p.placeholder_format.idx >= 16 and "BODY" in str(p.placeholder_format.type))
            for idx, bild in zip(bild_ph, bilder):
                satt(slide, idx, bild)
            for idx, t in zip(text_ph, texter):
                satt(slide, idx, t)
        else:
            satt(slide, 1, b.get("text"))
        if b.get("anteckningar"):
            slide.notes_slide.notes_text_frame.text = b["anteckningar"]
        rensa_tomma(slide)
        forsta = n == 1 or namn.startswith(("Title,", "Logo"))
        if not forsta:
            sidfot(slide, spec.get("sidfot"), spec.get("bildnummer", True))
    prs.core_properties.title = spec.get("titel") or spec["bilder"][0].get("rubrik", "")
    if spec.get("forfattare"):
        prs.core_properties.author = spec["forfattare"]
    prs.core_properties.language = spec.get("sprak", "sv-SE")
    prs.save(ut)
    print(f"Skrev {ut} ({len(spec['bilder'])} bilder)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec", nargs="?")
    ap.add_argument("-o", "--ut")
    ap.add_argument("--layouter", action="store_true")
    a = ap.parse_args()
    if a.layouter:
        for kort, lang in LAYOUT.items():
            print(f"{kort:24} {lang}")
        return
    if not (a.spec and a.ut):
        ap.error("ange spec.json och -o utfil.pptx")
    bygg(json.loads(Path(a.spec).read_text(encoding="utf-8")), a.ut)


if __name__ == "__main__":
    main()
