# Kontrola sociálních sítí (Claude in Chrome)

Lehký, poloautomatický postup pro pravidelnou aktualizaci dvou údajů u
všech odkazů na sociální sítě v sekci [O webu](README.md) → „Sociální
sítě" (`content/owebu.html`, druhý blok `div.quicklinks`): **počet
sledujících/členů/odběratelů** a **datum posledního příspěvku/videa na
dané síti** (ukazatel, jak moc je účet aktivní — NE datum, kdy jsme si
údaje naposledy ověřili). Sedm z těchto odkazů se navíc opakuje na
stránce [Volby 2026](../volby/2026/README.md) (tabulka „Volební
uskupení", sloupeček „Poznámka" → `.socials-cell`) — ty se zapisují na
obě místa najednou, viz krok 4. Nemá vlastní datový soubor — údaje se
zapisují přímo do HTML.

## Kdy spustit

V rámci týdenní rutiny, spolu s ostatními sekcemi v režimu „týdně" (viz
`README.md` → „Stav sekcí"). Počty sledujících se u malých místních
účtů mění pomalu, ale požadavek je aktualizovat je každý běh, ne jen
příležitostně.

## Postup

### 1. Projdi všechny odkazy v seznamu

V `content/owebu.html`, sekce „Sociální sítě", je `div.quicklinks`
s jedním `<a class="qlink">` na účet. Aktuálně (1. 9. 2026) jde o 14
odkazů: Facebook Město Pečky, Facebook Pečky-Virtuálně, Instagram
streetpeopleofpecky, Facebook NAŠE PEČKY, Facebook Kulturní středisko
města Pečky, Facebook Alena Švejnohová, Facebook Městská knihovna
Svatopluka Čecha, Facebook Pečky NEXT, Facebook Pečky Pečákům,
Facebook ODS a nezávislí Pečky, Instagram Pečky NEXT, YouTube Město
Pečky, Facebook Pečky srdcem, FB skupina Lidé pro Pečky s podporou SPD.

### 2. Zjisti počet sledujících a datum poslední aktivity (Claude in Chrome)

Pro každý odkaz naviguj na URL a přečti `get_page_text`. Zjišťují se
dva nezávislé údaje:

**a) Počet sledujících/členů/odběratelů:**
- **Facebook stránka**: číslo je v textu „sledující (N)" hned pod
  názvem stránky. Facebook u větších čísel zaokrouhluje (např. „1 tis.")
  — zapsat jako „cca 1 000"/„1,4 tis." podle toho, jak to ukazuje
  platforma, nedopočítávat si přesné číslo.
- **Facebook skupina** (Lidé pro Pečky s podporou SPD): skupiny nemají
  „sledující", ale „N členů" — zapsat s jednotkou „členů", ne
  „sledujících", je to jiná metrika.
- **Instagram**: číslo je v textu „Sledující (N)" na profilu.
- **YouTube**: číslo je v textu „N odběratelů" na kanálu (`@handle`,
  ne playlist). Vyžaduje `mcp__claude-in-chrome__*` nástroje (skutečná
  přihlášená Chrome relace), ne `mcp__Claude_Browser__*` (izolovaný
  in-app prohlížeč) — YouTube ho opakovaně zasekne na
  `consent.youtube.com` a kliknutí na „Odmítnout vše" se tam neprojeví.
  Viz i poznámka v kořenovém `CLAUDE.md` → „Poznámky k datům".

**b) Datum poslední aktivity** — NE datum, kdy jsme se dívali, ale
datum posledního skutečného příspěvku/videa (ukazuje, jak je účet
živý):
- **Facebook stránka/skupina**: první/nejvyšší příspěvek ve feedu
  `get_page_text` ukazuje relativní čas hned pod jménem autora („6 h",
  „4 d", nebo starší jako datum „5. červen"). Přepočítej na absolutní
  datum vůči dni kontroly (např. „4 d" a kontrola 1. 9. → 28. 8. 2026).
  Pozor na sdílené příspěvky — řádek „Jméno stránky … [datum] · Jiné
  jméno … [jiné datum] · text" znamená, že stránka teď sdílela starší
  příspěvek jiné stránky; rozhoduje **první** (vlastní) datum stránky,
  ne datum sdíleného obsahu (viz Pečky Pečákům, kde vlastní sdílení je
  z 5. 6., ale sdílený příspěvek Města Pečky je ze 4. 6.).
- **Facebook — zamíchaný (obfuskovaný) timestamp**: od 2. 9. 2026 Facebook
  u části stránek nevypisuje datum příspěvku jako prostý text, ale rozsype
  ho do desítek jednoznakových `<span>` promíchaných s návnadovými znaky
  (v `get_page_text` to vypadá jako `S͏n͏d͏t͏o͏o͏p͏s͏e͏r͏4͏h͏…`).
  Prosté čtení textu pak vrátí nesmysl, nebo — hůř — časovou značku
  **komentáře** místo příspěvku. Spolehlivé je přečíst znaky v pořadí, v
  jakém se skutečně vykreslí, tedy podle jejich pozice na obrazovce
  (`javascript_tool`):
  ```js
  function dec(c){
    const s=Array.from(c.querySelectorAll('span')).filter(x=>x.children.length===0);
    const i=s.map(x=>{const r=x.getBoundingClientRect(),cs=getComputedStyle(x);
      return {t:x.textContent.replace(/[͏​]/g,''),x:r.left,y:r.top,w:r.width,d:cs.display};})
      .filter(o=>o.t&&o.d!=='none'&&o.w>0);
    i.sort((a,b)=>(a.y-b.y)||(a.x-b.x));
    return i.map(o=>o.t).join('');
  }
  const st=[];
  for(const el of document.querySelectorAll('span')){
    if(el.children.length>8 && /͏/.test(el.textContent) && el.textContent.length<250){
      st.push(dec(el).slice(0,22));
    }
  }
  st;
  ```
  Vrátí řetězce jako `"31. srpna v 18:45sptre"` nebo `"17 h…"` — platná je
  jen ta část na začátku, zbytek je vata z návnadových znaků. Nesetřídit
  podle CSS `order` (vrací jinou, špatnou permutaci) — jen podle
  `getBoundingClientRect()`. Vrátí-li skript víc značek, ta první v pořadí
  DOM nemusí být nejnovější příspěvek (připíchnuté příspěvky navrchu, viz
  Městská knihovna: `["24. července…","31. srpna v 10:56…"]`) — brát
  **nejnovější** datum, ne první.
- **Facebook — absolutní datum je přesnější než relativní**: kde skript
  vrátí tvar „31. srpna v 18:45", zapisovat to datum. Dopočet z relativního
  tvaru („4 d") se snadno splete o den — při běhu 2. 9. 2026 se takhle
  ukázalo, že u tří účtů (Kulturní středisko, Pečky srdcem, FB skupina SPD)
  bylo datum z předchozího dne o den novější, než jaké má poslední skutečný
  příspěvek.
- **Instagram**: příspěvky v mřížce mívají 1–3 připíchnuté (pinned)
  navrchu, takže mřížka NENÍ spolehlivě chronologická a otevření
  jednotlivého příspěvku přes odkaz `/p/<kód>/` po pár kliknutích
  narazí na přihlašovací stěnu. Spolehlivější je přečíst atribut `alt`
  obrázků v mřížce přes `javascript_tool` — Instagram do něj vkládá
  přesné datum:
  ```js
  Array.from(document.querySelectorAll('img[alt]')).map(img => img.alt)
  ```
  Vrátí řetězce typu `"Photo by Jméno on September 01, 2026."` — najdi
  mezi nimi nejnovější datum (nemusí to být první v poli kvůli
  připíchnutým příspěvkům).

  **POZOR, od 2. 9. 2026 tohle přestalo fungovat**: v české lokalizaci
  Instagram plní `alt` popiskem příspěvku („Propanbutan final boss pro max
  #street #pecky…“), ne datem. `?hl=en` na tom nic nezmění, `time[datetime]`
  ani odkazy `a[href^="/p/"]` se v odhlášené relaci nevykreslí, ve
  `<script>` tazích není žádný `taken_at`/`taken_at_timestamp` a
  `/api/v1/users/web_profile_info/?username=…` (i s hlavičkou
  `x-ig-app-id`) vrací HTML místo JSON. Dokud se nenajde jiná cesta, u
  obou instagramových účtů **aktualizuj jen počet sledujících** (ten je
  v `document.body.innerText` jako „Sledující (N)“) a datum poslední
  aktivity nech na hodnotě z posledního úspěšného čtení — nikdy ho
  nedopočítávej ani neodhaduj podle Facebooku téhož uskupení.
- **YouTube**: kanálová záložka „Videa" u tohoto kanálu NEODPOVÍDÁ
  skutečné poslední aktivitě — zasedání zastupitelstva se nahrávají
  jako „neveřejné" a v ní se neobjeví (naposledy zobrazovala video staré
  8 měsíců, zatímco playlist měl novější). Zjišťuj datum posledního
  videa z playlistu „Zasedání ZM"
  (`https://www.youtube.com/playlist?list=PL1KVT2dbyIKSTFRv7tfDqrfk5gkTSnoyu`,
  stejný postup jako v `jednani/automation-kontrola-usneseni-cz.md`
  krok 6) — poslední položka v seznamu ukazuje „Vysíláno před N dny/
  týdny/měsíci" u nejnovějšího videa.

`WebFetch`/curl na Facebook, Instagram a YouTube nefunguje (přihlašovací
stěna/JS rendering) — jen skutečná navigace v prohlížeči. Bez přihlášení
jde přečíst jen zaokrouhlené/veřejné číslo sledujících, ne podrobné
Přehledy stránky (to nevadí, píšeme jen souhrnné číslo).

### 3. Zapiš do `content/owebu.html`

Každý `<a class="qlink">` má `<span class="url">` se dvěma řádky:

```html
<span class="url"><span class="follower-count">N sledujících</span><span class="url-meta">poslední příspěvek <span data-date="RRRR-MM-DD">D. M. RRRR</span></span></span>
```

`follower-count` obsahuje jen samotné číslo s jednotkou (žádný handle/URL,
žádná šipka ↗) — na rozdíl od bloku „Odkazy" výše, kde `.url` pořád nese
plnou doménu/handle a šipku, tady je to jen holé číslo. (U YouTube
„odběratelů" a „poslední video" místo „sledujících"/„poslední příspěvek";
u FB skupiny „členů".) `data-date`/
viditelné datum je datum **poslední aktivity** zjištěné v kroku 2b —
u aktivního účtu se bude měnit skoro každý den, u neaktivního zůstane
stát na stejném datu klidně týdny/měsíce. Text „poslední příspěvek:
dnes/včera/před X dny" se pak dopočítává sám za běhu v prohlížeči
(`assets/common.js`, funkce `relDatum()`, stejný princip jako u tabulky
„Stav sekcí" na Domů). Neupravuj text ručně na „dnes"/„včera" — stačí
zapsat absolutní datum, JS zbytek dopočítá.

Seznam je seřazený sestupně podle počtu sledujících — pokud se pořadím
dvou položek po aktualizaci prohodí, přesuň řádek `<a class="qlink">`
na správné místo (ne nutně po každé kontrole, jen když se pořadí
skutečně změní).

### 4. Promítni na Volby 2026 (jen 7 překrývajících se odkazů)

Těchto 7 odkazů se objevuje i v tabulce „Volební uskupení" na
`/volby/2026/` (`content/volby2026.html`, `.socials-cell`): Facebook
NAŠE PEČKY, Facebook Pečky NEXT, Instagram Pečky NEXT, Facebook Pečky
Pečákům, Facebook ODS a nezávislí Pečky, Facebook Pečky srdcem, FB
skupina Lidé pro Pečky s podporou SPD. Zapiš tam stejné číslo i stejné
datum poslední aktivity, ve tvaru:

```html
<span class="social-meta">(N sledujících, poslední příspěvek: <span data-date="RRRR-MM-DD">D. M. RRRR</span>)</span>
```

Zbylých 7 odkazů (Město Pečky, Pečky-Virtuálně, streetpeopleofpecky,
Kulturní středisko, Alena Švejnohová, Městská knihovna, YouTube) na
Volby 2026 nepatří — nejsou volební uskupení.

### 5. Přegeneruj a ověř

Spusť `python3 scripts/build.py`, otevři `/o-webu/` a (pokud se
aktualizovaly i překrývající se odkazy) `/volby/2026/`, zkontroluj, že
se u každého odkazu zobrazuje aktualizované číslo a datum poslední
aktivity (najetím myší na text se zobrazí přesné datum v tooltipu).

### 6. Nahlaš uživateli

Stručně: u kterých účtů se počet sledujících změnil (a o kolik), které
mají novou aktivitu, které zůstávají dlouhodobě neaktivní. Nic
nevymýšlet — číslo/datum, které web nezobrazí (např. stránka
nedostupná), nechat beze změny a nahlásit jako mezeru.

## Další rizika

- **Zaokrouhlení u větších čísel** — Facebook od cca 1 000 sledujících
  zobrazuje zkrácený tvar („1 tis.", „12 tis."). Zapisovat vždy ve
  stejném zaokrouhleném tvaru, nedopočítávat si přesné číslo.
- **Skupina vs. stránka** — skupina (`facebook.com/groups/...`) ukazuje
  „členů", ne „sledujících". Nezaměňovat jednotku.
- **Sdílené příspěvky na Facebooku** — když stránka sdílí cizí příspěvek,
  `get_page_text` ukáže dvě jména a dvě data za sebou. Datum posledního
  příspěvku = datum **vlastního** sdílení (první jméno/datum ve dvojici),
  ne datum původního sdíleného obsahu.
- **Připíchnuté příspěvky na Instagramu** — mřížka profilu není
  spolehlivě chronologická (1–3 pinned příspěvky navrchu). Nespoléhat na
  pořadí v mřížce, číst `alt` text obrázků (krok 2b) a vzít z něj
  nejnovější datum.
- **Instagram vyžaduje přihlášení na jednotlivé příspěvky** — otevření
  `/p/<kód>/` po pár kliknutích v rámci jedné session narazí na
  přihlašovací stěnu (`Prohlédněte si příspěvek → Zaregistrujte se`).
  Technika s `img[alt]` (krok 2b) tuhle stěnu obchází, protože čte data
  přímo z profilové mřížky bez otevírání detailu.
- **YouTube a `mcp__Claude_Browser__*`** — v izolovaném in-app
  prohlížeči se `consent.youtube.com` opakovaně zasekává i po kliknutí
  na „Odmítnout vše" (ověřeno 1. 9. 2026, více pokusů). Přepnout na
  `mcp__claude-in-chrome__*` (skutečná Chrome relace) — tam projde na
  první pokus, stejně jako u kroku 6/7 v
  `jednani/automation-kontrola-usneseni-cz.md`.
- **YouTube kanálová záložka „Videa" je zavádějící** — nejnovější
  zasedání zastupitelstva se do ní nedostanou (nahrána jako neveřejná,
  viditelná jen přes playlist). Vždy číst datum poslední aktivity
  z playlistu „Zasedání ZM", ne ze záložky „Videa".
- **Křížené příspěvky mezi propojenými stránkami** — NAŠE PEČKY, Pečky
  NEXT (Facebook i Instagram) a Alena Švejnohová sdílí část
  administrátorů a občas zveřejní identický příspěvek na všech najednou
  (ověřeno 1. 9. 2026, příspěvek „Pojďme se potkat!" na čtyřech účtech
  zároveň). Přesto ověřovat datum zvlášť u každého odkazu, ne kopírovat
  mezi nimi automaticky — shoda je náhoda dne, ne pravidlo.
- **Nový/zaniklý účet** — pokud na webu přibude zmínka o dalším účtu
  (nebo některý zanikne), doplnit/odebrat řádek podle aktuálního stavu
  `content/owebu.html`, ne podle seznamu v kroku 1 — ten je jen momentka
  k 1. 9. 2026.
