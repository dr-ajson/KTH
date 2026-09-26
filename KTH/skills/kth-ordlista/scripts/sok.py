#!/usr/bin/env python3
"""Sök i KTH:s svensk-engelska ordbok.

Användning:
    python sok.py <term>              svensk term -> engelska (exakt, sedan delträff)
    python sok.py --en <term>         engelsk term -> svenska
    python sok.py --fuzzy <term>      närliggande stavningar om inget hittas
    python sok.py --scan <fil>        lista alla ordbokstermer som förekommer i en svensk text
    python sok.py --json ...          maskinläsbar utdata

Hänvisningar av typen "se X" i anmärkningen följs automatiskt.
"""
import argparse
import csv
import difflib
import json
import re
import sys
from pathlib import Path

def _hitta(rel):
    """Filen i skillens mappstruktur, eller platt bredvid skriptet (Custom GPT: /mnt/data)."""
    here = Path(__file__).resolve().parent
    for p in (here.parent / rel, here / Path(rel).name, Path("/mnt/data") / Path(rel).name):
        if p.exists():
            return p
    return here.parent / rel


CSV_PATH = _hitta("references/ordlista.csv")


def load():
    with open(CSV_PATH, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def norm(s):
    return re.sub(r"\s+", " ", s).strip().casefold()


def see_target(entry):
    m = re.match(r"^se (?:även )?(.+)$", entry["anmarkning"].strip(), re.I)
    return m.group(1).strip() if m else None


def lookup_sv(rows, term, fuzzy=False):
    t = norm(term)
    exact = [r for r in rows if norm(r["svensk_term"]) == t]
    results = list(exact)
    # följ "se X"-hänvisningar för poster utan egen översättning
    for r in exact:
        target = see_target(r)
        if target and not r["engelsk_oversattning"]:
            results += [x for x in rows if norm(x["svensk_term"]) == norm(target)]
    if not results:
        results = [r for r in rows if t in norm(r["svensk_term"])][:25]
    if not results and fuzzy:
        names = sorted({r["svensk_term"] for r in rows})
        close = difflib.get_close_matches(term, names, n=8, cutoff=0.7)
        results = [r for r in rows if r["svensk_term"] in close]
    return results


def lookup_en(rows, term, fuzzy=False):
    t = norm(term)
    def fields(r):
        return norm(r["engelsk_oversattning"] + " | " + r["synonymer"])
    exact = [r for r in rows if t in [norm(x) for x in re.split(r"[|,;]", fields(r))]]
    results = exact or [r for r in rows if t in fields(r)][:25]
    if not results and fuzzy:
        names = sorted({r["engelsk_oversattning"] for r in rows if r["engelsk_oversattning"]})
        close = difflib.get_close_matches(term, names, n=8, cutoff=0.7)
        results = [r for r in rows if r["engelsk_oversattning"] in close]
    return results


def scan(rows, text):
    """Hitta ordbokstermer i en svensk text. Längsta träff först, ord­gränser respekteras."""
    low = text.casefold()
    by_key = {}
    for r in rows:
        key = norm(re.sub(r"\s*\(.*?\)", "", r["svensk_term"]))
        if len(key) >= 3:
            by_key.setdefault(key, []).append(r)
    # Längsta termer först; en träff som redan täcks av en längre term räknas inte
    # (så "lärande" inte räknas inuti "livslångt lärande", "behörig" inte i "behörighet").
    claimed = []
    hits = {}
    for key in sorted(by_key, key=len, reverse=True):
        pattern = r"(?<![\w])" + re.escape(key) + r"\w{0,4}(?![\w])"
        n = 0
        for m in re.finditer(pattern, low):
            s, e = m.span()
            if any(s < ce and e > cs for cs, ce in claimed):
                continue
            claimed.append((s, e))
            n += 1
        if n:
            hits[by_key[key][0]["svensk_term"]] = {"antal": n, "poster": by_key[key]}
    return hits


def fmt(r):
    parts = [f"{r['svensk_term']}  →  {r['engelsk_oversattning'] or '(ingen egen översättning)'}"]
    for label, key in [("synonymer", "synonymer"), ("anmärkning", "anmarkning"),
                       ("definition", "definition"), ("källa", "kalla"),
                       ("ändrad", "senast_andrad")]:
        if r[key]:
            parts.append(f"    {label}: {r[key]}")
    return "\n".join(parts)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("term", nargs="?")
    p.add_argument("--en", action="store_true", help="sök engelsk term")
    p.add_argument("--fuzzy", action="store_true", help="föreslå närliggande stavningar")
    p.add_argument("--scan", metavar="FIL", help="skanna en svensk textfil ('-' = stdin)")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()
    rows = load()

    if a.scan:
        text = sys.stdin.read() if a.scan == "-" else Path(a.scan).read_text(encoding="utf-8")
        hits = scan(rows, text)
        if a.json:
            print(json.dumps(hits, ensure_ascii=False, indent=2))
        else:
            for term, h in hits.items():
                print(f"### {term} ({h['antal']}×)")
                print("\n".join(fmt(r) for r in h["poster"]) + "\n")
            print(f"\n{len(hits)} ordbokstermer hittade.")
        return

    if not a.term:
        p.error("ange en term eller --scan")
    res = lookup_en(rows, a.term, a.fuzzy) if a.en else lookup_sv(rows, a.term, a.fuzzy)
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    elif res:
        print("\n".join(fmt(r) for r in res))
    else:
        print(f"Ingen träff för '{a.term}'. Prova --fuzzy, eller termen saknas i KTH-ordboken.")
        sys.exit(1)


if __name__ == "__main__":
    main()
