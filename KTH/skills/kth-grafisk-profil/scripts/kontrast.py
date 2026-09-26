#!/usr/bin/env python3
"""Kontrollera kontrast mellan två färger enligt WCAG 2.x (samma metod som KTH:s kontrasttabeller).

    python kontrast.py "KTH-blå" Vit
    python kontrast.py "#004791" "#EBE5E0"
    python kontrast.py --lista                   # alla KTH-färger med namn och hex

Utdata anger kontrastkvot och vilken textstorlek kombinationen klarar:
  >= 4.5:1  all text
  >= 3:1    bara stor text (minst 18 pt / 24 px, eller fet och minst 14 pt / 18,5 px)
  <  3:1    inte godkänd för text mot bakgrund
"""
import json
import sys
import unicodedata
from pathlib import Path

def _hitta(rel):
    """Filen i skillens mappstruktur, eller platt bredvid skriptet (Custom GPT: /mnt/data)."""
    here = Path(__file__).resolve().parent
    for p in (here.parent / rel, here / Path(rel).name, Path("/mnt/data") / Path(rel).name):
        if p.exists():
            return p
    return here.parent / rel


COLORS = _hitta("assets/kth-farger.json")


def key(s):
    s = unicodedata.normalize("NFKD", s.casefold())
    return "".join(c for c in s if c.isalnum())


def palette():
    data = json.loads(COLORS.read_text(encoding="utf-8"))
    out = {"svart": ("Svart", "#000000")}
    for group in ("primarfarger", "funktionsfarger"):
        for k, v in data[group].items():
            out[key(v["namn"])] = (v["namn"], v["hex"])
            out[key(k)] = (v["namn"], v["hex"])
    out[key("Accentblå")] = out[key("Digitalblå")]
    out[key("Röd")] = out[key("Tegel")]
    out[key("Mörkröd")] = out[key("Mörk tegel")]
    return out


def resolve(arg, pal):
    if arg.startswith("#") and len(arg) == 7:
        return arg.upper(), arg.upper()
    hit = pal.get(key(arg))
    if not hit:
        sys.exit(f"Okänd färg: {arg}. Kör --lista för att se namnen.")
    return hit


def luminance(hex_):
    rgb = [int(hex_[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def ratio(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def main():
    pal = palette()
    if len(sys.argv) == 2 and sys.argv[1] == "--lista":
        seen = set()
        for name, hex_ in pal.values():
            if name not in seen:
                seen.add(name)
                print(f"{name:14} {hex_}")
        return
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    (na, ha), (nb, hb) = resolve(sys.argv[1], pal), resolve(sys.argv[2], pal)
    r = ratio(ha, hb)
    if r >= 4.5:
        verdict = "godkänd för all text"
    elif r >= 3:
        verdict = "bara stor text (≥18 pt/24 px, eller fet ≥14 pt/18,5 px)"
    else:
        verdict = "INTE godkänd för text – använd bara dekorativt"
    print(f"{na} ({ha}) mot {nb} ({hb}): {r:.1f}:1 – {verdict}")


if __name__ == "__main__":
    main()
