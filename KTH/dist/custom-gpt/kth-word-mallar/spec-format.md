# Specifikation för bygg_word.py

Skriptet tar en JSON-fil. Fältet `mall` väljer mall, resten beskriver innehållet. Text som kan bli längre än en mening skrivs i markdown (se längst ned).

## Fält som gäller alla mallar

| Fält | Innehåll |
|---|---|
| amne | 1–2 meningar som beskriver dokumentet. Sätts som Ämne i dokumentegenskaperna; KTH kräver Titel och Ämne för tillgänglighet |
| forfattare | Sätts som författare i dokumentegenskaperna |
| sprak | Språkkod, standard sv-SE. Använd en-US för engelska dokument |

## Grundmall (`"mall": "grundmall"`)

Neutralt KTH-dokument: PM, promemoria, underlag, sammanställning, omvärldsbevakning.

| Fält | Krav | Innehåll |
|---|---|---|
| titel | ja | Hamnar i formatmallen KTH Titel |
| underrubrik | nej | Tas bort om den saknas |
| innehall | nej | Markdown |

## Rapport (`"mall": "rapport"`)

Rapporter med sidhuvudtabell, sammanfattning och innehållsförteckning.

| Fält | Krav | Innehåll |
|---|---|---|
| titel | ja | Rubrik på första sidan |
| underrubrik | nej | |
| rapportnamn | nej | Kort namn i sidhuvudet (standard: titeln) |
| datum | nej | Dokumentdatum i sidhuvudet, ÅÅÅÅ-MM-DD |
| diarienummer | nej | T.ex. V-2025-2607 |
| skapat_av | nej | Nämnd, råd, arbetsgrupp eller liknande |
| sammanfattning | nej | Markdown; placeras före innehållsförteckningen under rubriken Sammanfattning |
| innehallsforteckning | nej | true (standard) eller false |
| innehall | nej | Markdown. Använd `#` för kapitel så att förteckningen blir rätt |

Innehållsförteckningen fylls i av Word när dokumentet öppnas (Word frågar om fält ska uppdateras – svara ja). I LibreOffice eller förhandsgranskning syns en förklarande rad i stället.

## Beslut (`"mall": "beslut"`)

KTH:s beslutsmall med sidhuvud för beslutsdatum och diarienummer, och vattenstämpeln FÖRSLAG.

| Fält | Krav | Innehåll |
|---|---|---|
| arendemening | ja | Rubriken blir "Beslut om <arendemening>" |
| beslutet | ja | Markdown. Själva beslutet, kort och i presens ("Rektor beslutar att ...") |
| arendet | ja | Markdown. Bakgrund och motivering |
| beslutsfattare | ja | "titel Förnamn Efternamn", t.ex. "rektor Anna Andersson" |
| foredragande | ja | "titel Förnamn Efternamn" |
| narvarande | nej | Övriga närvarande vid beslutet |
| beslutsdatum | nej | ÅÅÅÅ-MM-DD, skrivs både på första sidan och i sidhuvudet |
| diarienummer | nej | Diarienummer och klassificeringskod: "HS-2026-1234 1.2" |
| bilagor | nej | Lista med bilagornas namn, numreras automatiskt |
| sandlista | nej | Lista med mottagare, en per rad |
| expeditionsdatum | nej | Fylls normalt i först när beslutet expedieras |
| vattenstampel | nej | true (standard) behåller FÖRSLAG. Sätt false först när beslutet är fattat |

Mallens egen instruktion gäller efter beslut: inga ändringar utöver beslutsfattarens, ta bort vattenstämpeln, ange expeditionsdatum, spara som PDF och expediera PDF-filen.

## Markdown som stöds

```
# Rubrik 1            ## Rubrik 2            ### Rubrik 3
Vanligt stycke. Rader utan tomrad emellan slås ihop till ett stycke.
**fet**, *kursiv*, [länktext](https://www.kth.se)
- punkt               (två mellanslag in = nivå 2, fyra = nivå 3)
1. numrerad punkt     (varje ny lista börjar om på 1)
| Kolumn | Kolumn |   (första raden blir rubrikrad som upprepas på varje sida)
|---|---|
| cell | cell |
```

Bilder, fotnoter och sidbrytningar stöds inte av skriptet. Lägg till dem i Word efteråt, eller redigera den färdiga .docx-filen med python-docx.
