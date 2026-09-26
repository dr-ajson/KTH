---
name: kth-grafisk-profil
description: KTH:s grafiska profil (grafisk manual v1.2, 2024) – färger med hex/RGB/CMYK/Pantone, kontrastkrav, färgordning för diagram, typografi (Figtree, Georgia, Arial), logotypregler, linjemönster och bildmanér. Använd när något ska se ut som KTH: diagram, infografik, webbsidor, HTML, affischer, sociala medier-bilder, omslag, visuell granskning av material, eller frågor om KTH:s färger, typsnitt och logotyp. Use for any KTH-branded visual output or brand compliance question, even if the user just says "in KTH style".
---

# KTH:s grafiska profil

KTH:s grafiska profil finns för att allt KTH ger ut ska kännas igen som KTH och vara tillgängligt. Den här skillen innehåller manualens regler i en form som går att använda direkt i kod och design.

## Snabbfakta

Primärfärger: KTH-blå #004791, Marinblå #000061 (logotypens färg), Himmelsblå #6298D2, Ljusblå #DEF0FF, Sand #EBE5E0, Vit #FFFFFF, samt Digitalblå #0029ED som bara får användas på skärm.

Typsnitt: Figtree (rubriker, ingresser, korta texter), Georgia (längre brödtext), Arial som reserv.

Diagramfärger i ordning: KTH-blå, Himmelsblå, Marinblå, Tegel #E86A58, Mörk tegel #78001A, Turkos #339C9C, Mörk turkos #1C434C, Grön #4DA060, Mörkgrön #0D4A21, Gul #FFBE00, Mörkgul #A65900.

## Var detaljerna finns

| Fil | Innehåll | Läs när |
|---|---|---|
| `references/farger.md` | Alla färgvärden, fördelning, funktionsfärger, diagramordning, kontrasttabell | Färgval, diagram, text på färgad bakgrund |
| `references/typografi.md` | Typsnitt, hierarki, radavstånd, textplattor | Layout av text, webbsidor, affischer |
| `references/logotyp.md` | Varianter, frizon, minsta storlek, placering, samprofilering | Allt som innehåller logotypen |
| `references/grafiska-element.md` | Linjemönster, bildmanér (blåton), film, profilprodukter, uttagsexempel | Affischer, sociala medier, omslag, film |
| `assets/kth-farger.json` | Maskinläsbara färgvärden | Kod |
| `assets/kth-tokens.css` | CSS-variabler och grundtypografi | HTML och webb |
| `assets/kth.mplstyle` | Matplotlib-stil med KTH:s diagramfärger | Diagram i Python |
| `scripts/kontrast.py` | Kontrastkontroll enligt WCAG för valfritt färgpar | Innan text läggs på färg |

## Viktigaste reglerna

Kontrast först. Text ska ha minst 4,5:1 mot bakgrunden, eller 3:1 om den är stor (minst 18 pt/24 px, eller fet och minst 14 pt). Kör `python scripts/kontrast.py "KTH-blå" Sand` när du är osäker. Himmelsblå på vitt och de mellanstarka funktionsfärgerna klarar bara stor text; gul och grå klarar inte text på vitt alls.

Logotypen ska aldrig ritas eller genereras. Den finns i KTH:s mallar och som originalfiler på intranätet. Om ett uttag behöver logotypen och du inte har filen, lämna en tydligt markerad plats för den och säg till användaren var den hämtas. Den placeras centrerad i över- eller underkant, med en frizon lika bred som kronan, aldrig mot funktionsfärger.

Funktionsfärger är för diagram, rapporter och presentationer, inte för att färgsätta hela uttag. Grundtonen i allt KTH-material är blå, sand och vit.

Linjemönstret ritas inte fritt. Använd KTH:s färdiga mönsterfiler eller PowerPoint-mallen, och lägg det aldrig bakom text eller logotyp.

## Office-dokument

Word-, PowerPoint- och Excelfiler ska byggas i KTH:s mallar, inte formateras för hand efter profilen. Använd skillarna `kth-word-mallar`, `kth-powerpoint` och `kth-excel`.

## Diagram

Följ färgordningen ovan och börja med de blå. Vid fler än tre serier får funktionsfärgerna byta plats så länge varannan är ljus och varannan mörk. I Python: `plt.style.use("assets/kth.mplstyle")`. Vit bakgrund, lätta stödlinjer, rubrik i Marinblå.

## Granskning av material

När användaren ber dig granska om något följer profilen: gå igenom färger (exakta värden, kontrast), typsnitt, logotyp (variant, frizon, placering, storlek), linjemönster (inte bakom text/logotyp, inte över både bild och platta) och bildmanér. Redovisa avvikelser med hänvisning till rätt avsnitt och sida i manualen. Frågor som manualen inte besvarar hänvisas till grafiskprofil@kth.se.
