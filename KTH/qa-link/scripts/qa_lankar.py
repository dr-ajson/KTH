#!/usr/bin/env python3
"""Kvalitetskontroll av länkar och källhänvisningar i en text.

    python qa_lankar.py extrahera dokument.md     # alla länkar + meningen de står i
    python qa_lankar.py kontrollera dokument.md   # extrahera och testa att länkarna fungerar
    python qa_lankar.py kontrollera --url https://exempel.se/a https://exempel.se/b
    python qa_lankar.py hamta https://exempel.se/sida   # läsbar text från källan

Indata: .md, .txt, .html eller .docx (även hyperlänkar som bara syns som länktext).
Lägg till --json för maskinläsbar utdata.

Slutkoder: 0 = inga fel, 2 = `kontrollera` hittade TRASIG/TROLIG_404 (rapporten skrivs ändå
ut; det är inte en krasch), 3 = `hamta` kunde inte hämta en eller flera källor.

Status från `kontrollera`:
  OK            svarar 2xx (efter ev. omdirigering)
  OMDIRIGERAD   fungerar men landar på en annan adress – kontrollera att det är rätt sida
  TROLIG_404    svarar 200 men sidan ser ut som en felsida ("sidan finns inte" o.d.)
  TRASIG        404, 410 eller DNS-fel – länken fungerar inte
  SERVERFEL     5xx – kan vara tillfälligt, prova igen
  BLOCKERAD     401/403/429 eller anslutningen stoppades – sajten eller nätverket stoppar
                automatiska anrop. Det betyder INTE att länken är trasig; kontrollera på
                annat sätt (webbverktyg, webbläsare) innan du drar slutsatser.
"""
import argparse
import html
import json
import re
import sys
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlparse

try:
    import requests
except ImportError:  # pragma: no cover
    sys.exit("Kräver requests: pip install requests")

UTMANING = re.compile(
    r"(client challenge|just a moment|checking your browser|enable javascript to (proceed|continue)|"
    r"captcha|are you a robot|access denied|attention required)", re.I)
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36 qa-link/1.0")
URL_RE = re.compile(r"https?://[^\s<>\"'\)\]]+", re.I)
MD_LINK = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")
FELSIDA = re.compile(
    r"(sidan (du söker )?(kunde inte hittas|finns inte)|page (was )?not found|404 not found|"
    r"the page you (are looking for|requested) (does not|doesn't|could not)|hittades inte)", re.I)


# ------------------------------------------------------------------ extrahera

def las_text(path: Path):
    """Returnerar (text, [(länktext, url)]) för filen."""
    suf = path.suffix.lower()
    if suf == ".docx":
        return las_docx(path)
    raw = path.read_text(encoding="utf-8", errors="replace")
    lankar = []
    if suf in (".html", ".htm"):
        for m in re.finditer(r'<a\s[^>]*href="(https?://[^"]+)"[^>]*>(.*?)</a>', raw, re.I | re.S):
            lankar.append((re.sub(r"<[^>]+>", "", m.group(2)).strip(), html.unescape(m.group(1))))
        raw = html.unescape(re.sub(r"<[^>]+>", " ", raw))
    return raw, lankar


def las_docx(path: Path):
    with zipfile.ZipFile(path) as z:
        doc = z.read("word/document.xml").decode("utf-8")
        rels = z.read("word/_rels/document.xml.rels").decode("utf-8")
    mal = dict(re.findall(r'Id="([^"]+)"[^>]*Target="([^"]+)"', rels))
    mal.update({a: b for b, a in re.findall(r'Target="([^"]+)"[^>]*Id="([^"]+)"', rels)})
    lankar = []
    for rid, inner in re.findall(r'<w:hyperlink[^>]*r:id="([^"]+)"[^>]*>(.*?)</w:hyperlink>', doc, re.S):
        url = mal.get(rid, "")
        if url.startswith("http"):
            lankar.append(("".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", inner)), html.unescape(url)))
    stycken = ["".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", p))
               for p in re.findall(r"<w:p[ >].*?</w:p>", doc, re.S)]
    return html.unescape("\n".join(stycken)), lankar


def meningar(text):
    text = re.sub(r"(?m)^\s*(#{1,6}|[-*]|\d+[.)])\s+", "", text)  # markdownrubriker och listmarkörer
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", text) if s.strip()]


def extrahera(path: Path):
    text, html_lankar = las_text(path)
    poster, sedda = [], set()

    def lagg_till(url, lanktext, kontext):
        url = url.rstrip(".,;:")
        poster.append({"nr": len(poster) + 1, "url": url, "lanktext": lanktext, "kontext": kontext})
        sedda.add(url)

    stycken = meningar(text)
    for lanktext, url in html_lankar:
        kontext = next((s for s in stycken if lanktext and lanktext in s), lanktext)
        lagg_till(url, lanktext, kontext)
    for s in stycken:
        for m in MD_LINK.finditer(s):
            lagg_till(m.group(2), m.group(1), MD_LINK.sub(r"\1", s))
        rest = MD_LINK.sub("", s)
        for m in URL_RE.finditer(rest):
            lagg_till(m.group(0), "", rest)
    return poster


# ------------------------------------------------------------------ kontrollera

def testa(url, timeout=15):
    res = {"url": url, "status": None, "kod": None, "slutadress": None, "anmarkning": ""}
    s = requests.Session()
    s.headers.update({"User-Agent": UA, "Accept-Language": "sv,en;q=0.8"})
    try:
        r = s.head(url, allow_redirects=True, timeout=timeout)
        if r.status_code in (403, 405, 400, 501) or r.status_code >= 500:
            r = s.get(url, allow_redirects=True, timeout=timeout, stream=True)
        kod = r.status_code
        res["kod"], res["slutadress"] = kod, r.url
        if kod in (404, 410):
            res["status"] = "TRASIG"
        elif kod in (401, 403, 429):
            res["status"] = "BLOCKERAD"
            res["anmarkning"] = "Sajten nekar automatiska anrop; verifiera manuellt."
        elif kod >= 500:
            res["status"] = "SERVERFEL"
        elif 200 <= kod < 400:
            omdir = _norm(r.url) != _norm(url)
            res["status"] = "OMDIRIGERAD" if omdir else "OK"
            if omdir:
                res["anmarkning"] = f"Landar på {r.url}"
            ctype = r.headers.get("content-type", "")
            if "html" in ctype:
                body = r.text[:200000] if r.request.method == "GET" else s.get(url, timeout=timeout).text[:200000]
                titel = re.search(r"<title[^>]*>(.*?)</title>", body, re.I | re.S)
                res["titel"] = html.unescape(titel.group(1).strip()) if titel else ""
                synlig = re.sub(r"<[^>]+>", " ", body)[:5000]
                if UTMANING.search(res["titel"] or "") or UTMANING.search(synlig):
                    res["status"] = "BLOCKERAD"
                    res["anmarkning"] = "Sajten visar en robotspärr i stället för innehållet; verifiera manuellt."
                    return res
                if FELSIDA.search(res["titel"] or "") or FELSIDA.search(re.sub(r"<[^>]+>", " ", body)[:5000]):
                    res["status"] = "TROLIG_404"
                    res["anmarkning"] = "Svarar 200 men innehållet ser ut som en felsida."
                if urlparse(r.url).path in ("", "/") and urlparse(url).path not in ("", "/"):
                    res["status"] = "TROLIG_404"
                    res["anmarkning"] = f"Djuplänk omdirigeras till startsidan ({r.url})."
        else:
            res["status"] = "TRASIG"
    except requests.exceptions.SSLError as e:
        res["status"], res["anmarkning"] = "TRASIG", f"Certifikatfel: {e.__class__.__name__}"
    except requests.exceptions.ConnectionError as e:
        msg = str(e)
        if "NameResolution" in msg or "getaddrinfo" in msg or "Name or service not known" in msg:
            res["status"], res["anmarkning"] = "TRASIG", "Domänen finns inte (DNS-fel)."
        else:
            res["status"] = "BLOCKERAD"
            res["anmarkning"] = "Ingen anslutning (nätverk/proxy stoppar, eller sajten svarar inte). Verifiera på annat sätt."
    except requests.exceptions.Timeout:
        res["status"], res["anmarkning"] = "SERVERFEL", "Tidsgräns överskriden."
    except requests.exceptions.RequestException as e:
        res["status"], res["anmarkning"] = "TRASIG", e.__class__.__name__
    return res


def _norm(u):
    p = urlparse(u)
    return (p.netloc.lower().removeprefix("www."), p.path.rstrip("/"), p.query)


def kontrollera(poster):
    unika = list(dict.fromkeys(p["url"] for p in poster))
    with ThreadPoolExecutor(max_workers=8) as ex:
        resultat = dict(zip(unika, ex.map(testa, unika)))
    for p in poster:
        p.update({k: v for k, v in resultat[p["url"]].items() if k != "url"})
    return poster


# ------------------------------------------------------------------ hämta text

def hamta(url, max_tecken=60000):
    r = requests.get(url, headers={"User-Agent": UA}, timeout=20)
    r.raise_for_status()
    ctype = r.headers.get("content-type", "")
    if "pdf" in ctype or url.lower().endswith(".pdf"):
        tmp = Path("/tmp/qa_link_kalla.pdf")
        tmp.write_bytes(r.content)
        try:
            import subprocess
            return subprocess.run(["pdftotext", "-layout", str(tmp), "-"], capture_output=True,
                                  text=True).stdout[:max_tecken]
        except FileNotFoundError:
            return f"[PDF sparad i {tmp}; installera pdftotext eller läs filen med annat verktyg]"
    body = r.text
    synlig = re.sub(r"<[^>]+>", " ", body)[:5000]
    if UTMANING.search(synlig):
        raise RuntimeError("Sajten visar en robotspärr i stället för innehållet. "
                           "Hämta källan med plattformens webbverktyg eller en webbläsare.")
    body = re.sub(r"(?is)<(script|style|nav|footer|header|noscript)[^>]*>.*?</\1>", " ", body)
    main = re.search(r"(?is)<(main|article)[^>]*>(.*?)</\1>", body)
    body = main.group(2) if main else body
    body = re.sub(r"(?i)<(br|/p|/h\d|/li|/tr)[^>]*>", "\n", body)
    text = html.unescape(re.sub(r"<[^>]+>", " ", body))
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text).strip()
    return text[:max_tecken]


# ------------------------------------------------------------------ utdata

def skriv_tabell(poster):
    print("| # | Status | Länk | Påstående/kontext | Anmärkning |")
    print("|---|---|---|---|---|")
    for p in poster:
        kontext = (p.get("kontext") or "").replace("|", "/").replace("\n", " ")
        if len(kontext) > 140:
            kontext = kontext[:137] + "…"
        print(f"| {p['nr']} | {p.get('status', '–')} | {p['url']} | {kontext} | {p.get('anmarkning', '')} |")
    if any("status" in p for p in poster):
        from collections import Counter
        c = Counter(p["status"] for p in poster)
        print("\n" + ", ".join(f"{k}: {v}" for k, v in c.most_common()))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("kommando", choices=["extrahera", "kontrollera", "hamta"])
    ap.add_argument("mal", nargs="*", help="fil, eller URL:er med --url / för hamta")
    ap.add_argument("--url", action="store_true", help="målen är URL:er, inte en fil")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_intermixed_args()
    if not a.mal:
        ap.error("ange en fil eller URL")

    if a.kommando == "hamta":
        fel = 0
        for u in a.mal:
            try:
                print(f"===== {u}\n{hamta(u)}\n")
            except Exception as e:  # visa felet tydligt i stället för en felsida som innehåll
                print(f"===== {u}\nKUNDE INTE HÄMTAS: {e}\n", file=sys.stderr)
                fel = 3
        sys.exit(fel)
    if a.url:
        poster = [{"nr": i, "url": u, "lanktext": "", "kontext": ""} for i, u in enumerate(a.mal, 1)]
    else:
        poster = extrahera(Path(a.mal[0]))
    if a.kommando == "kontrollera":
        kontrollera(poster)
    if a.json:
        print(json.dumps(poster, ensure_ascii=False, indent=2))
    else:
        skriv_tabell(poster)
    if a.kommando == "kontrollera" and any(p["status"] in ("TRASIG", "TROLIG_404") for p in poster):
        sys.exit(2)


if __name__ == "__main__":
    main()
