#!/usr/bin/env python3
"""Validera och paketera skills för uppladdning.

    python tools/paketera.py                  # alla skills
    python tools/paketera.py kth-ordlista     # en skill

Skapar i dist/:
  <skill>.zip               – för Claude (Inställningar > Skills) och ChatGPT Skills.
                               Båda använder samma öppna SKILL.md-format.
  custom-gpt/<skill>/       – reservform för ChatGPT-konton utan Skills: instruktioner.md
                               att klistra in i en Custom GPT, plus kunskapsfiler att ladda upp.
"""
import re
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
DIST = ROOT / "dist"
IGNORERA = {"__pycache__", ".DS_Store"}
GPT_INSTRUKTION_MAX = 8000  # teckengräns för instruktioner i en Custom GPT


def frontmatter(skill_md: Path):
    text = skill_md.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        raise ValueError("saknar YAML-frontmatter")
    meta = dict(re.findall(r"^(\w+):\s*(.+)$", m.group(1), re.M))
    return meta, m.group(2).strip()


def validera(skill: Path):
    fel = []
    meta, body = frontmatter(skill / "SKILL.md")
    namn, beskr = meta.get("name", ""), meta.get("description", "")
    if namn != skill.name:
        fel.append(f"name '{namn}' matchar inte mappnamnet")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", namn) or len(namn) > 64:
        fel.append("name får bara innehålla a–z, 0–9 och bindestreck (max 64 tecken)")
    if not beskr or len(beskr) > 1024:
        fel.append(f"description måste finnas och vara högst 1024 tecken (är {len(beskr)})")
    if "<" in beskr or ">" in beskr:
        fel.append("description får inte innehålla < eller >")
    for ref in re.findall(r"`((?:references|scripts|assets)/[^`\s]+)`", body):
        if not (skill / ref).exists():
            fel.append(f"SKILL.md hänvisar till {ref} som inte finns")
    return meta, body, fel


def filer(skill: Path):
    for p in sorted(skill.rglob("*")):
        if p.is_file() and not (set(p.parts) & IGNORERA):
            yield p


def paketera(skill: Path):
    meta, body, fel = validera(skill)
    if fel:
        print(f"✗ {skill.name}")
        for f in fel:
            print(f"    {f}")
        return False
    DIST.mkdir(exist_ok=True)
    zip_path = DIST / f"{skill.name}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for p in filer(skill):
            z.write(p, Path(skill.name) / p.relative_to(skill))

    gpt = DIST / "custom-gpt" / skill.name
    if gpt.exists():
        shutil.rmtree(gpt)
    gpt.mkdir(parents=True)
    kunskap = [p for p in filer(skill) if p.name != "SKILL.md"]
    for p in kunskap:
        shutil.copy2(p, gpt / p.name)  # Custom GPT har ingen mappstruktur
    instr = (
        f"# {meta['name']}\n\n{meta['description']}\n\n"
        "Kunskapsfilerna i denna GPT motsvarar mapparna references/, scripts/ och assets/ nedan; "
        "de ligger platt i /mnt/data när kodtolken körs. Skript körs med kodtolken, "
        "t.ex. `python /mnt/data/sok.py term`.\n\n" + body
    )
    (gpt / "instruktioner.md").write_text(instr, encoding="utf-8")
    varning = ""
    if len(instr) > GPT_INSTRUKTION_MAX:
        varning = f"  OBS: instruktionerna är {len(instr)} tecken, Custom GPT tillåter {GPT_INSTRUKTION_MAX}"
    if len(kunskap) > 20:
        varning += f"  OBS: {len(kunskap)} kunskapsfiler, Custom GPT tillåter 20"
    print(f"✓ {skill.name}: {zip_path.relative_to(ROOT)} ({zip_path.stat().st_size // 1024} kB){varning}")
    return True


def main():
    valda = sys.argv[1:] or [p.name for p in sorted(SKILLS.iterdir()) if (p / "SKILL.md").exists()]
    ok = all([paketera(SKILLS / namn) for namn in valda])
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
