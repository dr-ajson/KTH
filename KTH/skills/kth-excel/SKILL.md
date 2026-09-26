---
name: kth-excel
description: Skapar Excel-arbetsböcker (.xlsx) från KTH:s mall KTH.xltx med KTH:s färger på rubrikrader och diagram. Använd när användaren vill ha ett kalkylark, en tabell som Excel-fil, en sammanställning, budget eller ett diagram i Excel för KTH-bruk. Use for any Excel/spreadsheet deliverable in a KTH context.
---

# KTH:s Excel-mall

`assets/KTH.xltx` är KTH:s officiella Excel-mall. Den innehåller i praktiken bara typsnittet (Arial) och ett färgtema, och temat är en äldre palett som inte följer dagens grafiska profil. Skriptet `scripts/bygg_excel.py` utgår från mallen men byter temat till samma KTH-färger som Word- och PowerPoint-mallarna använder, och formaterar tabeller och diagram enligt profilen:

- rubrikrad i KTH-blå med vit fet text, fryst överst och definierad som Excel-tabell (sorterbar, filtrerbar och läsbar för skärmläsare)
- diagramserier i infografikordningen: KTH-blå, Himmelsblå, Marinblå, Tegel, Mörk tegel, Turkos, Mörk turkos, Grön, Mörkgrön, Gul, Mörkgul

## Arbetsgång

1. Strukturera datat som en tabell per blad: en rubrikrad och sedan en rad per post. Inga sammanslagna celler och inga tomma rader inuti tabellen – det bryter både filtrering och tillgänglighet.
2. Skriv specifikationen:
   ```json
   {
     "titel": "Arbetsbokens titel",
     "blad": [{
       "namn": "Intäkter",
       "kolumner": ["År", "Skola A", "Skola B"],
       "rader": [[2025, 1350000, 900000], [2026, 1500000, 950000]],
       "format": {"Skola A": "# ##0", "Skola B": "# ##0"},
       "diagram": {"typ": "stapel", "titel": "Intäkter per skola", "x": "År",
                   "y": ["Skola A", "Skola B"], "y_titel": "kr"}
     }]
   }
   ```
   `typ` kan vara `stapel`, `linje` eller `cirkel`. `format` tar Excels talformat (`# ##0` för tusental med mellanslag, `0.0%` för procent och `yyyy-mm-dd` för datum; formatkoderna skrivs alltid med engelsk syntax och visas sedan enligt användarens språkinställning i Excel).
3. Bygg: `python scripts/bygg_excel.py spec.json -o Arbetsbok.xlsx`
4. Behövs formler, villkorsstyrd formatering eller fler blad, öppna resultatet med openpyxl och fortsätt där. Skriv formler som formler (`=SUMMA` blir `=SUM` i openpyxl) i stället för att räkna ut värden i Python, så att arbetsboken går att uppdatera.

Kräver `openpyxl`.
