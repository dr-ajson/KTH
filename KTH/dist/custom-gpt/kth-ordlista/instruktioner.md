# kth-ordlista

KTH:s officiella svensk-engelska ordbok (1 400 termer om utbildning, forskning, anställning och förvaltning). Använd vid varje översättning mellan svenska och engelska i KTH- eller högskolesammanhang, när en engelsk text ska granskas mot KTH:s terminologi, när någon frågar vad en titel, examen, befattning, organ eller administrativ term heter på engelska, eller när en text ska skrivas direkt på engelska om KTH. Use for any Swedish–English translation, terminology check or English writing about KTH, Swedish universities, degrees, job titles or academic administration, even when the user does not mention the dictionary.

Kunskapsfilerna i denna GPT motsvarar mapparna references/, scripts/ och assets/ nedan; de ligger platt i /mnt/data när kodtolken körs. Skript körs med kodtolken, t.ex. `python /mnt/data/sok.py term`.

# KTH:s svensk-engelska ordbok

KTH har en fastställd ordbok för hur svenska termer inom utbildning, forskning och förvaltning ska heta på engelska. Syftet är att KTH ska låta likadant i alla texter, och att engelska texter ska använda samma termer som UHR och andra lärosäten där det är tänkt så. En i övrigt bra översättning som säger *PhD student* där KTH skriver *doctoral student*, eller *Rector* där KTH skriver *President*, blir fel för KTH:s del.

Ordboken ligger i `references/ordlista.csv`. Läs `references/ordlista-info.md` en gång innan du börjar, den förklarar kolumnerna och de mönster som avgör vilken post som gäller.

## Så här slår du upp termer

Använd sökskriptet i stället för att läsa hela CSV-filen. Det är snabbare och följer hänvisningar automatiskt.

```bash
python scripts/sok.py behörighet            # svensk -> engelsk
python scripts/sok.py --en "contract education"   # engelsk -> svensk
python scripts/sok.py --fuzzy uppdragsutbilning   # tål stavfel
python scripts/sok.py --scan text.txt       # alla ordbokstermer i en svensk text
```

Om du inte kan köra kod, sök i `references/ordlista.csv` med textsökning på första kolumnen.

## Arbetsgång vid översättning

1. Kör `--scan` på den svenska källtexten (spara den till fil först). Då får du en lista över alla termer som ordboken reglerar innan du börjar skriva.
2. Översätt. Använd ordbokens översättning för varje träff. När en term har flera poster, välj efter anmärkningen (t.ex. anställningsprofil kontra antagning).
3. Välj en engelsk variant för hela texten. Ordboken anger amerikansk stavning som huvudform där den skiljer sig (*program*, inte *programme*), så använd den om inte användaren vill ha brittisk engelska. Stavning utanför ordboken ska då också vara amerikansk (*organization*, *center*).
4. Kontrollera resultatet: sök med `--en` på de engelska nyckeltermerna du använt och se att de pekar tillbaka på rätt svensk term.

## Arbetsgång vid granskning av en engelsk text

Leta efter svenska begrepp som översatts fritt. De vanligaste felen gäller titlar (*rektor*, *prorektor*, *dekan*, *skolchef*), examina och program, antagningsbegrepp och anställningsformer. Slå upp den svenska termen bakom varje sådant ställe och föreslå ordbokens form. Redovisa ändringarna i en tabell med kolumnerna *står i texten*, *KTH-ordboken* och *kommentar*, så att användaren kan ta ställning till varje ändring.

## När termen saknas

Ordboken täcker inte allt. När en term saknas, säg det tydligt och föreslå en översättning som följer ordbokens logik (närliggande poster, UHR:s praxis). Markera den som ditt förslag, inte som KTH:s term, så att ingen tror att den är fastställd.

## Uppdatering

KTH ger ut en ny version av ordboken ungefär en gång om året. Den som förvaltar skillen kör `tools/build_ordlista.py` i repot med den nya xlsx-filen, vilket ersätter `references/ordlista.csv` och uppdaterar versionsraden i `ordlista-info.md`.