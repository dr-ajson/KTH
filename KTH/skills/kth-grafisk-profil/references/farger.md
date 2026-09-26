# Färger

Källa: KTH Grafisk manual v1.2 (2024), s. 10–17. Maskinläsbara värden finns i `assets/kth-farger.json`.

## Primärfärger

Den primära färgskalan bygger på olika nyanser av blått, där marinblå är logotypens färg. B = bestruket papper, O = obestruket papper.

| Färg | Hex | RGB | CMYK B | CMYK O | PMS B / O | NCS |
|---|---|---|---|---|---|---|
| Vit | #FFFFFF | 255, 255, 255 | 0, 0, 0, 0 | 0, 0, 0, 0 | – | – |
| Sand | #EBE5E0 | 235, 229, 224 | 9, 9, 12, 0 | 9, 9, 12, 0 | Warm Grey 1C / 1U | S 1000-N |
| KTH-blå | #004791 | 0, 71, 145 | 100, 70, 0, 12 | 100, 70, 0, 12 | 7686 C / 287 U | S 4050-R80B |
| Himmelsblå | #6298D2 | 98, 152, 210 | 54, 14, 0, 0 | 42, 10, 0, 2 | 284 C / 284 U | S 1040-R80B |
| Marinblå | #000061 | 0, 0, 97 | 100, 95, 0, 43 | 100, 90, 0, 35 | 2757 C / 2757 U | S 5540-R70B |
| Ljusblå | #DEF0FF | 222, 240, 255 | 15, 0, 0, 0 | 15, 0, 0, 0 | 2707 C / 2707 U | S 0515-R80B |
| Digitalblå | #0029ED | 0, 41, 237 | – | – | – | – |

Digitalblå kan inte tryckas. I tryck används KTH-blå i stället. I kontrasttabellen kallas Digitalblå för Accentblå.

Pantone-biblioteken finns inte längre i Adobes program, så i Adobe arbetar man i CMYK. Tryckeriet kan konvertera till Pantone vid behov.

### Fördelning

Manualen visar en ungefärlig fördelning av hur mycket de olika primärfärgerna används i KTH:s produktioner. Sand, KTH-blå och Marinblå dominerar ungefär lika mycket, därefter Vit och sedan Ljusblå, medan Himmelsblå och Digitalblå bara förekommer som små inslag. Alla färger behöver inte finnas i varje enskilt uttag.

## Funktionsfärger

Funktionsfärgerna kompletterar primärfärgerna och används till exempel i diagram, rapporter och presentationer. Logotypen placeras aldrig mot en funktionsfärg.

| Serie | Mörk | Mellan | Ljus |
|---|---|---|---|
| Grön | Mörkgrön #0D4A21 | Grön #4DA060 | Ljusgrön #C7EBBA |
| Turkos | Mörk turkos #1C434C | Turkos #339C9C | Ljus turkos #B2E0E0 |
| Tegel | Mörk tegel #78001A | Tegel #E86A58 | Ljus tegel #FFCCC4 |
| Gul | Mörkgul #A65900 | Gul #FFBE00 | Ljusgul #FFF0B0 |
| Grå | Mörkgrå #323232 | Grå #A5A5A5 | Ljusgrå #E6E6E6 |

Bruten svart #212121 och bruten vit #FCFCFC används enbart som textfärg på webb, för bättre läsbarhet på skärm. CMYK-värden för funktionsfärgerna finns i JSON-filen.

## Färgordning i diagram och infografik

Använd alltid denna ordning (s. 16):

1. KTH-blå #004791
2. Himmelsblå #6298D2
3. Marinblå #000061
4. Röd (= Tegel) #E86A58
5. Mörkröd (= Mörk tegel) #78001A
6. Turkos #339C9C
7. Mörk turkos #1C434C
8. Grön #4DA060
9. Mörkgrön #0D4A21
10. Gul #FFBE00
11. Mörkgul #A65900

Man får börja var som helst i ordningen. Funktionsfärgerna (från nr 4) får byta plats med varandra så länge varannan färg är ljus och varannan mörk. Ordningen är framtagen för kontrast mot vit bakgrund och mellan dataserier. I manualens exempel använder staplade diagram de blå tonerna, och linjediagram med fyra serier använder Tegel, Mörk tegel, Grön och Mörkgrön.

## Kontrast och tillgänglighet

Kraven följer WCAG: minst 4,5:1 för all text, minst 3:1 för stor text (minst 18 pt / 24 px, eller fet och minst 14 pt / 18,5 px). Under 3:1 är inte godkänt för text mot bakgrund. Beräkna valfritt par med `scripts/kontrast.py`.

Godkända textkombinationer bland primärfärgerna (≥ 4,5:1), enligt manualens tabell:

| Bakgrund | Textfärger som klarar all text |
|---|---|
| Vit | KTH-blå (9:1), Marinblå (17,9:1), Digitalblå (8,3:1), Svart |
| Sand | KTH-blå (7,2:1), Marinblå (14,3:1), Digitalblå (6,6:1), Svart |
| Ljusblå | KTH-blå (7,7:1), Marinblå (15,4:1), Digitalblå (7,1:1), Svart |
| KTH-blå | Vit, Sand, Ljusblå |
| Marinblå | Vit, Sand, Ljusblå, Himmelsblå (5,9:1) |
| Himmelsblå | Marinblå, Svart |
| Digitalblå | Vit, Sand, Ljusblå |

Endast stor text (3:1): Himmelsblå mot Vit, Himmelsblå mot KTH-blå.

Inte godkänt för text: KTH-blå mot Marinblå (2:1), KTH-blå mot Himmelsblå för liten text, Sand/Vit/Ljusblå mot varandra, Digitalblå mot KTH-blå eller Marinblå.

Bland funktionsfärgerna fungerar de mörka tonerna (Mörkgrön, Mörk turkos, Mörk tegel, Mörkgrå) bra mot Vit, Sand och den egna ljusa tonen. Mellantonerna Grön, Turkos, Tegel klarar bara stor text mot vitt (ca 3:1), Grå och Gul klarar inte text mot vitt alls. Kontrollera med skriptet innan du lägger text på en funktionsfärg.
