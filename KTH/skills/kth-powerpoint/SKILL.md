---
name: kth-powerpoint
description: Skapar PowerPoint-presentationer (.pptx) i KTH:s officiella mall KTH.potx, med mallens layouter, färger, Figtree-typografi, linjemönster och logotyp. Använd när användaren vill ha en presentation, bildspel, slides eller PowerPoint för KTH, eller vill göra om text, en rapport eller anteckningar till KTH-bilder. Use for any KTH slide deck or PowerPoint request, even if the template is not mentioned.
---

# KTH:s PowerPoint-mall

KTH:s mall innehåller 47 layouter byggda enligt den grafiska profilen: titelbilder i KTH-blå och marinblå, kapitelbilder, innehållsbilder, jämförelser, bildsidor och avslutande logobilder. Färger, typsnitt (Figtree) och logotypens placering sitter i layouterna. Därför ska presentationer alltid byggas från `assets/KTH.potx` och inte från en tom presentation, och man ska inte lägga egna färger eller textrutor ovanpå layouterna.

## Arbetsgång

1. Planera bildspelet innan du skriver kod. En bild ska bära ett budskap; rubriken säger vad bilden visar. Sikta på få punkter per bild och korta punkter.
2. Välj layout per bild. Vanligt upplägg: `titel` → `kapitel` per avsnitt → `innehall`, `tva-delar`, `jamforelse` eller `text-och-bild` → avslut med `logga` eller `logga-marin`.
3. Skriv specifikationen enligt `references/spec-format.md` och bygg:
   ```bash
   python scripts/bygg_presentation.py spec.json -o Presentation.pptx
   ```
4. Kontrollera visuellt: `soffice --headless --convert-to pdf Presentation.pptx` och titta på bilderna. Kontrollera särskilt att ingen text flödar över platshållarna. Korta texten hellre än att minska teckenstorleken.
5. Leverera .pptx-filen.

Kräver `python-pptx`.

## Regler från mallen och den grafiska profilen

Använd bara mallens färger. Mallens egen instruktion säger uttryckligen att PowerPoints autogenererade färgvarianter inte är godkända. Diagram och grafik ska följa färgordningen för infografik (KTH-blå, Himmelsblå, Marinblå, sedan funktionsfärgerna) – se skillen `kth-grafisk-profil` om den finns.

Logotypen sitter redan i layouterna. Lägg aldrig till en extra logotyp.

Bilder ska ha alternativtext (fältet `alt`). Egna objekt som läggs till utanför platshållarna måste få rätt läsordning, vilket skriptet undviker genom att bara fylla platshållare.

Diagram: skapa diagrammet som bild med KTH-färgerna (t.ex. matplotlib med `kth.mplstyle` från `kth-grafisk-profil`) och lägg in på en `bild`-layout, eller lägg ett inbyggt python-pptx-diagram på en `rubrik`-layout och sätt seriefärgerna manuellt.

## Engelska presentationer

Mallens layouter är språkneutrala. Sätt `"sprak": "en-US"` och följ KTH:s engelska terminologi (skillen `kth-ordlista`).
