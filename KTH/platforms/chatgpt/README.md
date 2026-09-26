# Installera i ChatGPT

## Om kontot har Skills

Skills finns i ChatGPT Business, Enterprise, Healthcare och Edu (beroende på arbetsytans inställningar). De använder samma `SKILL.md`-format som Claude, så samma zip fungerar:

1. Kör `python tools/paketera.py`.
2. I ChatGPT: öppna Skills och välj att ladda upp från datorn. Välj `dist/<skill>.zip`.
3. Använd skillen via skill-väljaren eller genom att skriva `@` och skillens namn.

## Om kontot saknar Skills – Custom GPT

`paketera.py` skapar en reservform i `dist/custom-gpt/<skill>/`:

1. Skapa en ny GPT (Utforska GPT:er → Skapa → Konfigurera).
2. Klistra in innehållet i `instruktioner.md` i fältet Instruktioner.
3. Ladda upp övriga filer i mappen som Kunskap.
4. Slå på Kodtolk (Code Interpreter) så att skripten kan köras.

Begränsningar: instruktionerna får vara högst 8 000 tecken och en GPT får ha högst 20 kunskapsfiler. `paketera.py` varnar om en skill går över gränserna. En Custom GPT läser inte in skillen automatiskt i andra chattar – du måste öppna just den GPT:n.
