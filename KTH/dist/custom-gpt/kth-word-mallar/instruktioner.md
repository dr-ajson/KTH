# kth-word-mallar

Skapar Word-dokument (.docx) i KTH:s officiella mallar – Grundmall, Rapportmall och Beslutsmall – med mallens logotyp, sidhuvud, formatmallar och tillgänglighetsanpassning. Använd när användaren vill ha ett KTH-dokument, PM, promemoria, rapport, utredning, underlag, beslut, beslutsförslag eller annat Word-dokument för KTH, även om mallen inte nämns. Use whenever a Word document for KTH is requested (memo, report, decision), including when converting existing text into KTH format.

Kunskapsfilerna i denna GPT motsvarar mapparna references/, scripts/ och assets/ nedan; de ligger platt i /mnt/data när kodtolken körs. Skript körs med kodtolken, t.ex. `python /mnt/data/sok.py term`.

# KTH:s Word-mallar

KTH kräver att Word-leveranser byggs i de officiella mallarna. Mallarna innehåller logotyp och sidhuvuden, rätt typsnitt (Arial i rubriker, Georgia i brödtext, eftersom Figtree inte finns i Office) och formatmallar som gör dokumenten tillgängliga för skärmläsare. Ett dokument som bara ser likt ut men är byggt från ett tomt Word-dokument saknar allt det, så använd alltid mallfilerna i `assets/` via skriptet nedan.

## Välj mall

| Mall | Använd för |
|---|---|
| `grundmall` | PM, promemorior, underlag, sammanställningar, omvärldsbevakning, allt som inte är rapport eller beslut |
| `rapport` | Längre rapporter med sammanfattning och innehållsförteckning, t.ex. arbetsgruppsrapporter och utredningar |
| `beslut` | Beslut och beslutsförslag som ska diarieföras |

Är det oklart, fråga. En utredning som leder fram till ett beslut blir ofta två dokument: en rapport och ett beslut.

## Arbetsgång

1. Skriv innehållet först, i markdown. Håll rubriknivåerna logiska (kapitel `#`, avsnitt `##`), eftersom rubrikerna styr både innehållsförteckning och skärmläsarnavigering.
2. Skriv en JSON-specifikation enligt `references/spec-format.md`.
3. Bygg dokumentet:
   ```bash
   python scripts/bygg_word.py spec.json -o Dokumentnamn.docx
   ```
4. Kontrollera resultatet. Konvertera gärna till PDF (`soffice --headless --convert-to pdf`) och titta på första sidan. LibreOffice klipper ibland texten i rapportmallens sidhuvudtabell; det gör även originalmallen och det ser rätt ut i Word.
5. Leverera .docx-filen och berätta vad användaren behöver göra i Word, se nedan.

Kräver `python-docx`. Om det saknas: `pip install python-docx`.

## Innehåll och språk

KTH-dokument skrivs i klarspråk. Beslutstexter följer mallens form: själva beslutet under "Beslutet", bakgrund under "Ärendet", och standardmeningen om beslutsfattare och föredragande byggs av skriptet. Engelska dokument ska följa KTH:s terminologi – använd skillen `kth-ordlista` om den finns.

Filnamn: undvik å, ä, ö, understreck och mellanslag i namn på filer som ska publiceras som PDF, som mallens egen instruktion säger. Använd bindestreck.

## Efter leverans – säg detta till användaren

Rapport: Word frågar om fälten ska uppdateras när filen öppnas. Svara ja, då fylls innehållsförteckningen i.

Beslut: vattenstämpeln FÖRSLAG ligger kvar tills beslutet är fattat. Bygg om med `"vattenstampel": false` och `expeditionsdatum`, eller ta bort den i Word.

Alla mallar: KTH kräver Titel och Ämne i dokumentegenskaperna för att dokumentet ska vara tillgängligt. Skriptet sätter båda om du fyller i `titel` och `amne` (1–2 meningar om innehållet), så gör alltid det. Bilder behöver alternativtext. Vid PDF-export: Arkiv > Spara som > PDF, välj Standard, klicka på Alternativ och kontrollera att Visa taggar för dokumentstruktur är markerad.

## När skriptet inte räcker

Behövs bilder, fotnoter eller specialformat, bygg först med skriptet och öppna sedan resultatet med python-docx för tillägg. Använd mallens formatmallar (se namnen i `STIL` överst i skriptet) i stället för direktformatering, så att dokumentet förblir tillgängligt.