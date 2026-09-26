# Om KTH-ordboken

Version: 2026-07-01 (1396 poster)
Källa: KTH:s svensk-engelska ordbok, exporterad från KTH:s intranät som xlsx.
Konverteras till `ordlista.csv` med `tools/build_ordlista.py` i repot.

## Kolumner i ordlista.csv

| Kolumn | Innehåll |
|---|---|
| svensk_term | Uppslagsordet. Samma term kan förekomma flera gånger med olika betydelse. |
| engelsk_oversattning | Rekommenderad översättning. Tom när posten bara hänvisar vidare ("se X"). |
| synonymer | Godtagbara alternativ, ibland med kommentar ("använd hellre ..."). |
| kalla | Varifrån översättningen kommer, t.ex. UHR, KTH, THS, UHRFS 2026:1. Tom för många poster. |
| anmarkning | Kontext eller hänvisning. Styr vilken post som gäller när en term har flera betydelser. |
| definition | Förklaring av den svenska termen (finns för ett fåtal poster). |
| senast_andrad | Datum då posten senast ändrades. |

## Mönster att känna till

Flera betydelser. Samma svenska term kan ha flera poster där anmärkningen anger sammanhanget. Exempel: "behörighet" är *eligibility* i anställningsprofiler men *entry requirements* i antagningssammanhang. Välj post efter textens sammanhang och säg vilken du valde om det är tvetydigt.

Hänvisningar. Poster som "KPU" eller "hemtenta" saknar översättning och har anmärkningen "se ...". Sökskriptet följer hänvisningen automatiskt.

Föredragen form. När en synonym är markerad med "använd hellre ..." eller anmärkningen säger "använd hellre X" är det huvudformen som gäller. Exempel: "doktorand" ska bli *doctoral student*, inte *Ph.D. student*.

Stavningsvarianter. Ett 40-tal poster anger amerikansk stavning som huvudöversättning och brittisk som synonym (program/programme). Använd den amerikanska formen om inte användaren uttryckligen vill ha brittisk engelska, och håll dig till en variant genom hela texten.

Versaler. Titlar och funktioner som hör till KTH:s egen organisation skrivs ofta med versal i ordboken (*President*, *Deputy President*, *Head of Administration*, *Adjunct Professor*). Behåll versaleringen som ordboken anger. Där samma titel finns både med och utan versal (t.ex. *University Director* från KTH och *university director* från UHR) gäller KTH:s variant för KTH:s egna befattningar.

Avsiktliga avvikelser. Vissa poster har anmärkningar som "Skiljer sig avsiktligt från rektorsbeslut KTH" eller "Översättningen följer inte UHR". Följ ordboken, den är den senare och mer genomtänkta källan.
