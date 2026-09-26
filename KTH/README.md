# KTH-skills

Skills för arbete med KTH-material i Claude och ChatGPT. Varje skill är en mapp med en `SKILL.md` och de filer den behöver (skript, referenser, mallar).

| Skill | Gör |
|---|---|
| [kth-ordlista](skills/kth-ordlista) | KTH:s svensk-engelska ordbok (1 396 termer, version 2026-07-01) med sökskript och granskningsstöd |
| [kth-grafisk-profil](skills/kth-grafisk-profil) | Färger, kontrast, typografi, logotyp, linjemönster och bildmanér enligt grafisk manual v1.2 |
| [kth-word-mallar](skills/kth-word-mallar) | Word-dokument i Grundmall, Rapportmall och Beslutsmall |
| [kth-powerpoint](skills/kth-powerpoint) | Presentationer i KTH.potx |
| [kth-excel](skills/kth-excel) | Arbetsböcker från KTH.xltx med KTH-färger |

## En källa, två plattformar

Claude och ChatGPT använder numera samma öppna skill-format (Agent Skills, `SKILL.md` med `name` och `description` i frontmatter). Därför finns varje skill bara i en version, under `skills/`. Det som skiljer är hur den installeras:

- **Claude**: ladda upp `dist/<skill>.zip`. Se [platforms/claude](platforms/claude/README.md).
- **ChatGPT med Skills** (Business, Enterprise, Edu): ladda upp samma zip. Se [platforms/chatgpt](platforms/chatgpt/README.md).
- **ChatGPT utan Skills** (t.ex. Plus): använd reservformen i `dist/custom-gpt/<skill>/` som en Custom GPT.

Om en skill någon gång behöver bete sig olika på plattformarna, lägg det plattformsspecifika i `platforms/<plattform>/<skill>/` och låt `skills/` förbli den gemensamma källan.

## Struktur

```
KTH/
├── skills/            en mapp per skill – det enda som redigeras för hand
├── platforms/         installationsanvisningar per plattform
├── source/            originalfiler som skills byggs från (ordbokens xlsx m.m.)
├── tools/
│   ├── paketera.py        validerar och bygger dist/
│   └── build_ordlista.py  ny version av ordboken -> skills/kth-ordlista
└── dist/              genereras, checkas inte in
```

## Arbetsflöde

```bash
python tools/paketera.py                 # validera och paketera alla skills
python tools/paketera.py kth-ordlista    # bara en
```

Ny version av ordboken: lägg xlsx-filen i `source/` och kör `python tools/build_ordlista.py source/<fil>.xlsx`, sedan `paketera.py`.

Nya versioner av Office-mallarna: ersätt filerna i `skills/<skill>/assets/` med samma filnamn och testa att skripten fortfarande bygger dokument (mallarnas struktur kan ändras mellan versioner). Källan är Drive-mappen Mallar; KTH:s officiella mallbibliotek (OneDrive, kth_assets – OfficeTemplateLibrary) har fler mallar, bland annat engelska versioner, brevmall och protokollmall.

Skripten kräver Python 3.10+ med `python-docx`, `python-pptx` och `openpyxl` (`pip install -r requirements.txt`).

## Sekretess

Repot innehåller KTH:s interna mallar och material från intranätet. Håll det privat.
