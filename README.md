# Bakalari Rewards

Rozšíření pro LNbits, které pravidelně kontroluje známky žáků v systému Bakaláři a podle nastavených pravidel vyplácí odměny v satoshi přes LNbits.

## Co rozšíření dělá

- Přihlašuje se do Bakalářů přes rodičovské API.
- Pravidelně načítá známky vybraných studentů.
- Filtruje nové známky od posledního zpracování nebo od zvoleného data při backtestu.
- Spočítá odměnu podle počtu a typu známek.
- Odešle jednu souhrnnou platbu přes LNbits withdraw link nebo interní LNbits platbu.
- Eviduje zpracované známky, aby nedocházelo k duplicitnímu proplacení mimo backtest režim.

## Aktuální stav

Rozšíření je v aktuálně testované verzi funkční včetně těchto částí:

- načtení seznamu studentů,
- načtení a uložení nastavení,
- ruční úprava studenta,
- spuštění pravidelné kontroly známek,
- výpočet odměny,
- odeslání LNbits platby,
- backtest režim se znovuzpracováním historických známek.

V testovaném prostředí proběhly opakovaně úspěšné interní platby a UI se načítá korektně včetně tabulky studentů, badge backtest režimu a settings dialogu.

## Známé chování

### Fiat měna v LNbits

Původní problém `Currency 'null' not allowed` byl odstraněn nastavením fiat měny v LNbits. Prakticky se osvědčilo přidat podporovanou měnu jako `USD` a neponechat účet bez výchozí měny.

Pokud je jako výchozí měna nastavena pouze `CZK`, mohou se v logu objevovat warningy od providerů, kteří CZK nepodporují. Nejde o problém Bakalari Rewards, ale o chování kurzových providerů v LNbits.

### `/undefined` 404 ve frontendu

Při načítání frontendové části se stále může objevovat požadavek na `/undefined`, který končí `404`. Aktuálně to nevypadá na funkční problém:

- API endpointy fungují,
- šablona se načítá,
- routy se načítají,
- UI je použitelné,
- platby probíhají správně.

Jde tedy zatím o kosmetický frontendový glitch, který je vhodné dohledat později.

## Doporučené nasazení

- Pro stabilní logy a funkční fiat přepočet nastavit v LNbits výchozí měnu účtu na `USD`.
- `CZK` ponechat mezi povolenými měnami pouze pokud je potřeba v UI nebo administraci.
- Backtest používat opatrně, protože může znovu proplatit historické známky.
- Před ostrým provozem zkontrolovat nastavení cílové LN adresy nebo withdraw linku.

## Poznámky k bezpečnosti a provozu

- Backtest režim maže záznamy o dříve zpracovaných známkách od zvoleného času a může vést k opakovanému payoutu.
- Při použití `FakeWallet` jsou platby vhodné jen pro vývojové a testovací prostředí.
- Pro produkci je potřeba použít reálný funding source a ověřit limity plateb v LNbits.
