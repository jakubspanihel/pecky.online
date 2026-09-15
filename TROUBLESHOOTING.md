# Troubleshooting

Známé bugy a obejití konkrétního provozního prostředí (sandbox, mounty
připojené složky, `preview_start`) — na rozdíl od trvalých konvencí
k datům v `CLAUDE.md` → „Poznámky k datům" jde o věci vázané na
konkrétní stroj nebo relaci, ne na projekt samotný. Nemusí platit na
každém stroji ani v každé relaci — u každé položky je datum diagnózy.

- Velké soubory v `jednani/` (`archive-*.json`) čtené přímo z cesty
  přes připojenou složku občas skončí `OSError: [Errno 35] Resource
  deadlock avoided` (Python `open()`, `cat`, `head`...). Obejití: nejdřív
  `cp soubor /tmp/kopie.json`, pak pracovat s kopií — `cp` samo selhání
  nemělo. Pozn. 9. 9. 2026: při kontrolním testu se chyba nezopakovala
  (3/3 přímá načtení `archive-2026-08-04.json` prošla), ale protože šlo
  vždy o občasnou chybu, postup přes kopii zůstává doporučený.
- ~~Git přes připojenou složku je nespolehlivý na čtení objektů~~ —
  **VYŘEŠENO 9. 9. 2026.** Příčinou nebyl git, ale to, že připojená
  složka odmítala `unlink` („Operation not permitted"): git po sobě
  nemohl uklidit `.git/index.lock` ani rozepsané `.git/objects/tmp_obj_*`,
  takže každý další příkaz spadl na „Another git process seems to be
  running" nebo na `Bus error`. Mazání se zapíná nástrojem
  `allow_cowork_file_delete` (stačí jednou, platí pro celou složku) —
  **narazíš-li na „Operation not permitted" při `rm`, zavolej ho místo
  hlášení, že to nejde.** Po zapnutí ověřeno, že funguje `git log --
  cesta/k/souboru`, `git show <commit>:<soubor>` i `git diff HEAD~1 --stat`.
  Zbytek staré poznámky ale platí dál: **historie repa sahá jen ke
  23. 8. 2026**, starší změny v ní nejsou vůbec — na dohledání, kdy co
  vzniklo před tímto datem, použij mtime souborů (`ls -la`, `stat`),
  datumy uvnitř dat (`meta.generated_at`) a `CHANGELOG.md`.
  Nouzové obejití, kdyby se blokované mazání někdy vrátilo: zámky
  nemazat, ale přejmenovat (`mv .git/index.lock .git/index.lock.bak.$(date +%s%N)`)
  — rename mount povoluje i tehdy, když unlink ne.
- **`preview_start` s `name` (spuštění dev serveru podle `.claude/launch.json`)
  na tomhle stroji spolehlivě padá na `[Errno 1] Operation not permitted`
  při otevírání `scripts/serve.py`.** Diagnostikováno 14. 9. 2026: jde
  o macOS sandbox/TCC omezení konkrétního launcher procesu, který
  `preview_start` interně používá — ne chybu v `serve.py` ani v repu
  (stejný soubor se bez problému spustí ručně přes Bash tool). Neřeší se
  úpravou skriptu/configu. **Obejití:** spustit server ručně přes Bash
  (`python3 scripts/serve.py`, typicky na pozadí), pak zavolat
  `preview_start` s `url` (`http://localhost:8000`) místo `name` — Browser
  pane se tak napojí na už běžící server, aniž by ho sám spouštěl. `serve.py`
  vždy defaultuje na port 8000 a od 14. 9. 2026 je idempotentní — když je
  port už obsazený (typicky server z předchozí relace), vypíše hlášku
  a skončí čistě (exit 0) místo pádu na traceback, takže "jen to spusť" je
  vždy bezpečné zavolat znovu bez kontroly předem.
