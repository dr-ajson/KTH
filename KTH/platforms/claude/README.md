# Installera i Claude

1. Kör `python tools/paketera.py` i repots rot.
2. I Claude (webb eller desktop): Inställningar → Capabilities → Skills → ladda upp `dist/<skill>.zip`. Kodkörning måste vara påslagen för skills som har skript.
3. Skillen används automatiskt när en fråga matchar dess `description`. Du kan också be om den med namn.

Uppdatering: ladda upp en ny zip med samma namn; den ersätter den gamla.

I Claude Code kan mappen `skills/<skill>` i stället kopieras eller länkas till `~/.claude/skills/`.
