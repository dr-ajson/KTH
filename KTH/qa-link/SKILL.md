---
name: qa-link
description: Kvalitetskontroll av länkar och källhänvisningar. Kontrollerar att varje länk fungerar och att texten bara påstår det som den länkade källan faktiskt säger, och justerar formuleringar som källan inte stöder. Använd alltid som sista steg innan text med länkar eller källhänvisningar levereras (rapporter, omvärldsbevakning, sammanfattningar, research, nyhetsbrev, PM), och när användaren ber om faktakoll, källgranskning, länkkontroll eller QA. Use as a final check on any output that cites URLs as sources, even if the user does not ask for it.
---

# qa-link – kontroll av länkar och källstöd

En länk i en text är ett löfte till läsaren: följ den här så ser du att det stämmer. Löftet bryts på två sätt – länken fungerar inte, eller källan säger inte det texten påstår. Det andra är allvarligare och vanligare i AI-genererad text, där siffror, datum och slutsatser lätt glider bort från källan. Den här skillen kontrollerar båda och rättar det som inte håller.

Grundregel: ett påstående är styrkt bara om källan på länken själv säger det. Det räcker inte att det är sant, att det står i en annan källa eller att du minns det. Bedömningen görs mot källans faktiska text, som du har läst i den här kontrollen.

## Arbetsgång

Sökvägarna till skript och referenser nedan är relativa till skillens mapp. Skripten kräver Python och `requests`.

### 1. Inventera länkar och påståenden

Gå igenom texten som ska levereras och de källor som använts under arbetet och som texten bygger på. För varje länk: notera vilket eller vilka påståenden den ska styrka. Om texten finns som fil:

```bash
python scripts/qa_lankar.py extrahera dokument.md    # även .txt, .html, .docx
```

Skriptet listar varje länk med meningen den står i. Kontrollera sedan manuellt att påståendet är rätt avgränsat – ett stycke kan ha flera påståenden som hänger på samma länk, och en källhänvisning i slutet av ett stycke kan avse hela stycket.

### 2. Kontrollera att länkarna fungerar

```bash
python scripts/qa_lankar.py kontrollera dokument.md
python scripts/qa_lankar.py kontrollera --url https://a.se/x https://b.se/y
```

Statusvärdena förklaras överst i skriptet. Slutkod 2 betyder att trasiga länkar hittades, inte att skriptet kraschade. Viktigast: `BLOCKERAD` betyder att sajten eller nätverket stoppar automatiska anrop, inte att länken är trasig. Försök då med plattformens webbverktyg (web fetch, sökning, webbläsare), eller en annan kanal från samma utgivare som visar samma innehåll (t.ex. utgivarens API eller PDF-versionen av sidan). Klassa länken som trasig först när den verkligen svarar 404/410, domänen inte finns eller sidan är en felsida. `OMDIRIGERAD` och `TROLIG_404` kräver att du tittar på vart länken faktiskt leder.

Kan du inte köra skript: öppna varje länk med webbverktyget och bedöm samma sak.

### 3. Kontrollera att källan stöder texten

Hämta källans innehåll – helst med plattformens webbverktyg, annars `python scripts/qa_lankar.py hamta <url>` (klarar HTML och PDF). Läs det avsnitt som påståendet bygger på och jämför punkt för punkt. Innehåller en mening flera påståenden, bedöm dem var för sig; meningen får den sämsta bedömningen och alla problem redovisas. Bedöm varje påstående enligt skalan i `references/bedomning.md`:

| Bedömning | Betyder | Åtgärd |
|---|---|---|
| Stöds | Källan säger detta | Ingen |
| Stöds delvis | Kärnan stämmer men något är överdrivet, generaliserat, fel siffra/datum eller saknar förbehåll | Justera formuleringen |
| Stöds inte | Källan säger inte detta (men motsäger det inte heller) | Justera, byt källa eller ta bort |
| Motsägs | Källan säger något annat | Rätta enligt källan |
| Kan inte verifieras | Länken fungerar inte eller innehållet går inte att läsa | Påtala, åtgärda länken eller markera påståendet |

Läs `references/bedomning.md` första gången, och när en bedömning är svår. Där finns de vanligaste felmönstren (siffror, tidsangivelser, generaliseringar, orsakssamband, citat, fel källtyp).

### 4. Åtgärda

Korrekta påståenden lämnas orörda – ändra inget som redan stämmer.

För övriga: skriv om så att texten säger det källan faktiskt stöder, med samma stil och språk som resten av texten. Välj den minsta ändring som gör texten korrekt. Om det som återstår inte längre bär stycket, fråga eller föreslå att påståendet stryks.

Byt aldrig till en ny källa utan att ha kontrollerat den på samma sätt. Hitta aldrig på en ersättningslänk. För trasiga länkar: ta reda på rätt adress – sidans nya adress hos samma utgivare, eller den adress som andra kontrollerade källor i texten själva hänvisar till – och kontrollera den på samma sätt. Hittas ingen, säg det och låt påståendet stå som "Kan inte verifieras".

### 5. Rapportera

Om allt stämmer: en rad – "QA: alla N länkar fungerar och stöder texten." Mer behövs inte.

Annars, i den här ordningen:

1. **Sammanfattning**: antal unika länkadresser, hur många som fungerar, antal påståenden som justerats.
2. **Avvikelser** – bara de som inte är OK:

   | # | Påstående (före) | Länk | Problem | Källan säger | Ändring (efter) |
   |---|---|---|---|---|---|

   I kolumnen "Källan säger" återger du det relevanta stället kort, med citat om det är avgörande, så att användaren kan se varför. Gäller avvikelsen bara länken, skriv länkens status där (t.ex. "404, sidan finns inte").
3. **Den justerade texten** i sin helhet, eller den justerade filen om underlaget var en fil.

Kontrollera de ändrade formuleringarna en gång till mot källan innan du levererar – en rättelse ska inte själv innehålla ett nytt fel.

## Avgränsning

Skillen gäller påståenden som hänvisar till en länk. Påståenden utan källa i texten granskas inte här, men om du ser uppenbara faktafel i dem, nämn det kort. Källans egen trovärdighet bedöms inte heller här; däremot ska det påtalas om en länk pekar på fel typ av källa för påståendet (t.ex. en nyhetsartikel om ett förslag som texten beskriver som fattat beslut).
