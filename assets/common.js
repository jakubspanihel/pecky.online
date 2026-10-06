// ===== assets/common.js — sdílená JS logika, načtená na každé stránce =====
// Vzniklo migrací z jednosouborového index.html (ARCHITEKTURA-MIGRACE.md).
// Obsahuje jen to, co je opravdu napříč sekcemi společné:
// responzivní tabulky, podzáložky (+ jejich odkaz na URL hash), kartičky
// volebních programů, rozbalovací bloky. Logika specifická pro jednu sekci
// (Jednání, Pečecké noviny, Lidé) žije přímo v příslušném content/<sekce>.html.

// ===== Hamburger (info-fab) + overlay-menu =====
// Hamburger je vidět jen když lišta menu v hlavičce není na obrazovce.
(function () {
  const fab = document.getElementById('infoFab');
  const tabs = document.getElementById('tabs');
  const overlay = document.getElementById('overlayMenu');
  const links = document.getElementById('overlayLinks');
  const closeBtn = document.getElementById('overlayClose');
  if (!fab || !tabs || !overlay || !links) return;
  const home = document.createElement('a');
  home.className = 'navlink';
  home.href = '/';
  home.textContent = '🤖 Do Peček';
  links.appendChild(home);
  document.querySelectorAll('#tabs .navlink, #tabsSecondary .navlink').forEach(a => {
    const clone = a.cloneNode(true);
    if (a.closest('#tabsSecondary')) clone.classList.add('secondary');
    links.appendChild(clone);
  });
  const open = () => { overlay.hidden = false; document.body.style.overflow = 'hidden'; };
  const close = () => { overlay.hidden = true; document.body.style.overflow = ''; };
  fab.addEventListener('click', open);
  closeBtn.addEventListener('click', close);
  overlay.addEventListener('click', e => { if (e.target === overlay) close(); });
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && !overlay.hidden) close(); });
  // výška sticky lišty (jen desktop) — odsazení pro sticky nadpisy sekcí
  const mq = window.matchMedia('(min-width:768px)');
  const setNavH = () => document.documentElement.style.setProperty('--nav-h', mq.matches ? tabs.offsetHeight + 'px' : '0px');
  setNavH();
  window.addEventListener('resize', setNavH);
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(([en]) => { fab.hidden = en.isIntersecting; }).observe(tabs);
  } else {
    fab.hidden = false;
  }
})();

// ===== Responzivní tabulky: zabalit register tabulky do scrollovatelného obalu =====
document.querySelectorAll('table.register').forEach(t => {
  if (t.parentElement.classList.contains('table-scroll')) return;
  const wrap = document.createElement('div');
  wrap.className = 'table-scroll';
  t.parentNode.insertBefore(wrap, t);
  wrap.appendChild(t);
});

// ===== Podzáložky uvnitř sekce (např. Volby 2022, Pozemky) =====
// Rozšířeno o trvalý odkaz na konkrétní záložku: pecky.online/pozemky/#prodej
// (viz ARCHITEKTURA-MIGRACE.md 2.2). Dřív (na jednostránkovém webu) neexistovalo
// vůbec — přepínání jen měnilo CSS třídy, hash se netýkal.
document.querySelectorAll('.subtabs').forEach(nav => {
  const links = nav.querySelectorAll('.subtablink');
  const panels = nav.parentElement.querySelectorAll(':scope > .subpanel');

  function activate(subpanelName, opts){
    opts = opts || {};
    const link = Array.from(links).find(l => l.dataset.subpanel === subpanelName);
    if (!link) return false;
    links.forEach(l => l.classList.remove('active'));
    panels.forEach(p => p.classList.remove('active'));
    link.classList.add('active');
    const target = nav.parentElement.querySelector('#subpanel-' + subpanelName);
    if (target) target.classList.add('active');
    if (opts.scroll) nav.scrollIntoView({behavior: 'smooth', block: 'start'});
    return true;
  }

  links.forEach(link => {
    link.addEventListener('click', () => {
      activate(link.dataset.subpanel, {scroll: true});
      // zapsat do URL, ať jde záložka nasdílet / uložit do záložek prohlížeče
      history.replaceState(null, '', '#' + link.dataset.subpanel);
    });
  });

  // úvodní stav podle hashe v URL (funguje i přímý odkaz na #prodej)
  const initialHash = window.location.hash.replace(/^#/, '');
  if (initialHash) activate(initialHash, {scroll: false});

  // ruční změna hashe v adresním řádku / tlačítko Zpět-Vpřed
  window.addEventListener('hashchange', () => {
    const h = window.location.hash.replace(/^#/, '');
    if (h) activate(h, {scroll: false});
  });
});

// ===== Rozbalovací bloky (tlačítko "Více informací") =====
document.querySelectorAll('.toggle-details').forEach(btn => {
  btn.addEventListener('click', () => {
    const target = document.getElementById(btn.getAttribute('aria-controls'));
    if (!target) return;
    const expanded = btn.getAttribute('aria-expanded') === 'true';
    btn.setAttribute('aria-expanded', String(!expanded));
    target.hidden = expanded;
    btn.textContent = expanded ? 'Více informací (rozbalit)' : 'Méně informací (sbalit)';
  });
});

// ===== Sdílený převod absolutní datum (data-date, ISO) -> relativní stáří =====
// Zdroj pravdy je vždy absolutní datum v HTML (kdyby JS neběžel, čtenář
// pořád vidí to). Stáří se počítá až tady, proti hodinám návštěvníka, takže
// text nezastará mezi buildy. Používá tabulka "Stav sekcí" i sloupeček
// "sledujících" u sociálních sítí (Volby 2026).
function relDatum(iso) {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso || '');
  if (!m) return null;                    // nečitelné datum radši nechat být
  const d = new Date(+m[1], +m[2] - 1, +m[3]);
  if (isNaN(d)) return null;
  const dnes = new Date();
  dnes.setHours(0, 0, 0, 0);
  const n = Math.round((dnes - d) / 86400000);

  if (n === 0) return 'dnes';
  if (n === 1) return 'včera';
  if (n < 0) return 'plánováno';          // datum v budoucnu (např. ohlášené jednání)

  // detail klesá se stářím: dny -> týdny -> měsíce -> roky (7. pád po "před")
  if (n < 14) return 'před ' + n + ' dny';
  if (n < 28) return 'před ' + Math.floor(n / 7) + ' týdny';
  if (n < 60) return 'před měsícem';
  if (n < 365) return 'před ' + Math.max(2, Math.floor(n / 30.4)) + ' měsíci';
  if (n < 730) return 'před rokem';
  return 'před ' + Math.max(2, Math.floor(n / 365.25)) + ' lety';
}

// ===== Budoucí datum -> chip "dnes/zítra/pozítří/za N dní" =====
// Pravidlo: v tabulkách a výpisech vždy vedle budoucího data chip
// <span class="tag probiha fut-chip" data-date="YYYY-MM-DD">plánováno</span>
// (text uvnitř je jen záloha bez JS). Výrazný (kal-dnes) je jen dnešek, jinak třída `probiha` jako u Jednání.
function relBudouci(iso) {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso || '');
  if (!m) return null;
  const d = new Date(+m[1], +m[2] - 1, +m[3]);
  if (isNaN(d)) return null;
  const dnes = new Date();
  dnes.setHours(0, 0, 0, 0);
  const n = Math.round((d - dnes) / 86400000);
  if (n < 0) return null;                 // už proběhlo — chip se skryje
  if (n === 0) return 'dnes';
  if (n === 1) return 'zítra';
  if (n === 2) return 'pozítří';
  if (n < 14) return 'za ' + n + (n < 5 ? ' dny' : ' dní');
  if (n < 60) return 'za ' + Math.floor(n / 7) + (n < 35 ? ' týdny' : ' týdnů');
  return 'za ' + Math.floor(n / 30.4) + (n < 152 ? ' měsíce' : ' měsíců');
}
(function () {
  document.querySelectorAll('.fut-chip[data-date]').forEach(el => {
    const t = relBudouci(el.getAttribute('data-date'));
    if (t === null) { el.hidden = true; return; }
    el.title = el.getAttribute('data-date');
    el.textContent = t;
    if (t === 'dnes') el.classList.replace('probiha', 'kal-dnes');
  });
})();

// ===== Chip s relativním stářím minulého data (karty událostí) =====
// <span class="tag rel-chip" data-date="YYYY-MM-DD"></span> — text dopočítá
// relDatum() v prohlížeči; bez JS (nebo u budoucího data) chip zůstane prázdný a skrytý.
(function () {
  document.querySelectorAll('.rel-chip[data-date]').forEach(el => {
    const iso = el.getAttribute('data-date');
    let t = relDatum(iso);
    if (t === null || t === 'plánováno') return;
    // relDatum() od 4 týdnů zaokrouhluje na „před měsícem“ — u karet je detail týdnů čitelnější
    const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso);
    const n = Math.round((new Date().setHours(0, 0, 0, 0) - new Date(+m[1], +m[2] - 1, +m[3])) / 86400000);
    if (n >= 28 && n < 90) t = 'před ' + Math.floor(n / 7) + ' týdny';
    el.title = iso;
    el.textContent = t;
  });
})();

// ===== Stav sekcí: absolutní datum -> relativní stáří =====
// Zdroj pravdy je tabulka "Stav sekcí" v kořenovém README.md, která drží
// absolutní datumy. Build je vysype do data-date (ISO) a jako viditelný
// text nechá původní datum.
(function () {
  const cells = document.querySelectorAll('.stav-sekci [data-date]');
  if (!cells.length) return;
  cells.forEach(td => {
    const stari = relDatum(td.getAttribute('data-date'));
    if (stari === null) return;
    const odhad = td.hasAttribute('data-odhad');
    // absolutní datum se neztrácí — přesune se do tooltipu
    td.title = (odhad ? 'odhad, přesné datum nedoloženo — ' : '') + td.textContent.replace(/\s*\?$/, '').trim();
    td.textContent = stari + (odhad ? ' ?' : '');
  });
})();

// ===== "Aktualizováno" pod nadpisem sekce: absolutní datum -> relativní stáří =====
// Datum je totéž co sloupec "Změna" tabulky Stav sekcí pro danou sekci (viz
// scripts/build.py, apply_lastmod) - jen jiný viditelný text, stejný přepočet.
(function () {
  const els = document.querySelectorAll('p.lastmod[data-date]');
  if (!els.length) return;
  els.forEach(el => {
    const stari = relDatum(el.getAttribute('data-date'));
    if (stari === null) return;
    el.title = el.textContent.trim();
    el.textContent = 'Aktualizováno ' + stari;
    // semafor: do 7 dní zelená, do 31 dní žlutá, starší červená
    const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(el.getAttribute('data-date'));
    const dnes = new Date(); dnes.setHours(0, 0, 0, 0);
    const n = Math.round((dnes - new Date(+m[1], +m[2] - 1, +m[3])) / 86400000);
    if (n >= 0) el.classList.add(n <= 7 ? 'age-fresh' : n <= 31 ? 'age-month' : 'age-old');
  });
})();

// ===== Sociální sítě (Volby 2026 i O webu): absolutní datum -> relativní stáří =====
// Datum posledního příspěvku se doplňuje ručně/rutinou (viz
// o-webu/automation-socialni-site.md), ale zobrazený text "poslední
// příspěvek: dnes/včera/před X dny" se dopočítává stejně jako u Stavu sekcí.
(function () {
  const els = document.querySelectorAll('.socials-cell [data-date], .quicklinks [data-date]');
  if (!els.length) return;
  els.forEach(el => {
    const stari = relDatum(el.getAttribute('data-date'));
    if (stari === null) return;
    el.title = el.textContent.trim();
    el.textContent = stari;
  });
})();

// ===== Dashboard na homepage: proběhlé položky pryč, datum změny -> stáří =====
// Build (render_dashboard ve scripts/build.py) vypíše budoucích položek víc,
// než je vidět (nadbytečné mají hidden). Tady se skryjí ty, jejichž
// data-until už je v minulosti, a zbylé se odkryjí až do data-max seznamu.
(function () {
  const lists = document.querySelectorAll('.dash-list');
  if (!lists.length) return;
  const d = new Date();
  const dnes = d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
  lists.forEach(ul => {
    const max = parseInt(ul.getAttribute('data-max'), 10);
    const items = ul.querySelectorAll('li[data-until]');
    if (!items.length) return;
    let shown = 0;
    items.forEach(li => {
      const ok = li.getAttribute('data-until') >= dnes && (isNaN(max) || shown < max);
      li.hidden = !ok;
      if (ok) shown++;
    });
    const empty = ul.querySelector('.dash-empty');
    if (empty) empty.hidden = shown > 0;
    // seznam bez jediné budoucí položky (a bez hlášky) schovat i s nadpisem
    if (!shown && !empty) {
      ul.hidden = true;
      const h = ul.previousElementSibling;
      if (h && h.tagName === 'H4') h.hidden = true;
    }
  });
  document.querySelectorAll('.dash-list .rel-date[data-date]').forEach(el => {
    const stari = relDatum(el.getAttribute('data-date'));
    if (stari === null) return;
    el.title = el.textContent.trim();
    el.textContent = stari;
  });
  document.querySelectorAll('.dash-list [data-date]:not(.rel-date)').forEach(el => {
    const stari = relDatum(el.getAttribute('data-date'));
    if (stari === null) return;
    el.title = el.textContent.trim();
    el.textContent = 'aktualizováno ' + stari;
  });
})();

// ===== Dashboard: štítek DNES/ZÍTRA/POZÍTŘÍ u nadcházejících položek =====
// Stejná logika jako kalRelTag() v content/kalendar.html (Kalendář → Seznam),
// jen se počítá v prohlížeči místo při buildu, ať zůstane platná i dny po
// buildu (viz komentář nad render_dashboard() ve scripts/build.py). Platí
// pro "Nadcházející akce" i "Příště" v kartě Jednání — obě sdílí stejnou
// značku li[data-until]. data-until je poslední den, kdy je položka ještě
// aktuální (u vícedenní akce konec, jinak totéž co začátek); data-from se
// píše jen tam, kde se od data-until liší.
(function () {
  const items = document.querySelectorAll('.dash-list li[data-until]:not(.dash-zm li)');
  if (!items.length) return;
  const d = new Date();
  const pad = n => String(n).padStart(2, '0');
  const toStr = dt => dt.getFullYear() + '-' + pad(dt.getMonth() + 1) + '-' + pad(dt.getDate());
  const dnes = toStr(d);
  const zitra = toStr(new Date(d.getFullYear(), d.getMonth(), d.getDate() + 1));
  const pozitri = toStr(new Date(d.getFullYear(), d.getMonth(), d.getDate() + 2));
  items.forEach(li => {
    const until = li.getAttribute('data-until');
    const from = li.getAttribute('data-from') || until;
    let tag = null;
    if (dnes >= from && dnes <= until) tag = 'DNES';
    else if (zitra >= from && zitra <= until) tag = 'ZÍTRA';
    else if (pozitri >= from && pozitri <= until) tag = 'POZÍTŘÍ';
    if (!tag) return;
    const a = li.querySelector('a');
    if (!a) return;
    const span = `<span class="tag ${tag === 'DNES' ? 'kal-dnes' : 'kal-blizko'}">${tag}</span>`;
    a.insertAdjacentHTML('beforebegin', span + ' ');  // štítek před názvem
  });
})();

// ===== Rozklikávací řádky tabulky (např. Pokladna: na co město utrácí) =====
document.querySelectorAll('.exp-row').forEach(row => {
  row.addEventListener('click', () => {
    const detail = row.nextElementSibling;
    if (!detail || !detail.classList.contains('exp-detail')) return;
    const toggle = row.querySelector('.exp-toggle');
    const isHidden = detail.hasAttribute('hidden');
    if (isHidden) { detail.removeAttribute('hidden'); if (toggle) toggle.textContent = '−'; }
    else { detail.setAttribute('hidden', ''); if (toggle) toggle.textContent = '+'; }
  });
});

// ===== České pevné mezery (NBSP) v dynamicky generovaném textu =====
// Obdoba scripts/typografie.py (pravidla viz TYPOGRAFIE.md, držet shodná).
// Statický HTML text řeší build; tohle dořeší text vložený skriptem později.
(function(){
  const NB = ' ';
  const MES = 'ledna|února|března|dubna|května|června|července|srpna|září|října|listopadu|prosince';
  const JED = 'km|m|cm|mm|kg|g|t|l|ha|m²|m³|m2|m3|%|°C|Kč|Kc|EUR|CZK|ks|tis\\.|mil\\.|mld\\.|hod\\.|min\\.|let';
  const TIT = 'Ing|Bc|Mgr|MUDr|JUDr|PhDr|RNDr|MVDr|Ph\\.D|MBA|DiS|doc|prof|arch|MgA|BcA|ThDr|PaedDr|CSc|mjr|plk|kpt|por|npor|gen|pplk';
  const VICE = 'do|na|po|za|od|ve|ke|se|ze|že|či|co|ku|by|ať|ač|pro|při|nad|pod|před|přes|bez|což|aby|když|atd\\.';
  const ZKR = 'str|obr|tab|č|čl|odst|písm|příl|kap|čp|ev|pozn';
  const VELKE = '[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ]';
  const P = [
    [/(?<![\p{L}\p{N}_])([KkSsVvZzOoUuAaIi]) (?=\S)/gu, '$1' + NB],
    [new RegExp('(?<![\\p{L}\\p{N}_])((?:' + VICE + ')) (?=\\S)', 'giu'), '$1' + NB],
    [new RegExp('(\\d) (?=(?:' + JED + ')(?![\\p{L}\\p{N}_]))', 'gu'), '$1' + NB],
    [/\b(tis\.|mil\.|mld\.) (?=Kč)/g, '$1' + NB],
    [/(?<![\d.,])(\d{1,3}) (?=\d{3}(?!\d))/g, '$1' + NB],
    [new RegExp('(\\d' + NB + '\\d{3}) (?=\\d{3}(?!\\d))', 'g'), '$1' + NB],
    [new RegExp('\\b(\\d{1,2}\\.) (?=(?:\\d{1,2}\\.|\\d{4}|' + MES + ')(?![\\p{L}\\d]))', 'gu'), '$1' + NB],
    [new RegExp('(?<![\\p{L}])((?:' + TIT + ')\\.) (?=' + VELKE + ')', 'gu'), '$1' + NB],
    [new RegExp('(?<![\\p{L}])(pan|pana|panu|paní) (?=' + VELKE + ')', 'gu'), '$1' + NB],
    [new RegExp('(?<![\\p{L}])((?:' + ZKR + ')\\.) (?=\\d)', 'gu'), '$1' + NB],
    [/(?<![\p{L}])(č\.) (?=j\.)/gu, '$1' + NB],
    [/(?<![\p{L}])(j\.) (?=\d)/gu, '$1' + NB],
    [/(§) (?=\d)/g, '$1' + NB],
  ];
  function peckyNbsp(t){ return P.reduce((s, [rx, r]) => s.replace(rx, r), t); }
  window.peckyNbsp = peckyNbsp;

  const SKIP = new Set(['SCRIPT','STYLE','PRE','CODE','TEXTAREA','TITLE','INPUT']);
  function fixNode(n){
    if (n.nodeType === 3) {
      const p = n.parentNode;
      if (p && !SKIP.has(p.nodeName) && n.nodeValue.indexOf(' ') !== -1) {
        const v = peckyNbsp(n.nodeValue);
        if (v !== n.nodeValue) n.nodeValue = v;
      }
    } else if (n.nodeType === 1 && !SKIP.has(n.nodeName)) {
      const w = document.createTreeWalker(n, NodeFilter.SHOW_TEXT);
      const txt = [];
      while (w.nextNode()) txt.push(w.currentNode);
      txt.forEach(fixNode);
    }
  }
  if (document.body) {
    new MutationObserver(ms => ms.forEach(m => m.addedNodes.forEach(fixNode)))
      .observe(document.body, {childList: true, subtree: true});
  }
})();

// ===== Nadpis sekce (h2.title / h2.dash-title na Domů, sticky) = odkaz "nahoru" =====
(function () {
  const reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  document.querySelectorAll('h2.title, h2.dash-title').forEach(h => {
    h.setAttribute('role', 'button');
    h.setAttribute('tabindex', '0');
    h.setAttribute('title', 'Nahoru');
    const up = () => window.scrollTo({top: 0, behavior: reduce ? 'auto' : 'smooth'});
    h.addEventListener('click', up);
    h.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); up(); } });
  });
})();

// ===== Widget "Příští zastupitelstvo" (+ volby): titulek s odpočtem =====
(function () {
  const d = new Date();
  const dnes = Date.UTC(d.getFullYear(), d.getMonth(), d.getDate());
  const utc = iso => { const [y, m, dd] = iso.split('-').map(Number); return Date.UTC(y, m - 1, dd); };
  const dnu = iso => Math.round((utc(iso) - dnes) / 86400000);
  const sklon = n => `${n} ${n < 5 ? 'dny' : 'dní'}`;

  // stejná logika jako _kdy_za() ve scripts/build.py
  const kdyZa = dny => dny <= 0 ? 'už dnes' : dny === 1 ? 'už zítra' : dny === 2 ? 'pozítří'
    : dny < 14 ? `za ${sklon(dny)}`
    : `za ${Math.floor(dny / 7)} ${dny < 35 ? 'týdny' : 'týdnů'}`;

  const zmKdy = document.querySelector('.dash-zm li:not([hidden]) .dash-zm-kdy');
  if (zmKdy) {
    const dny = dnu(zmKdy.closest('li').getAttribute('data-until'));
    if (dny >= 0) zmKdy.innerHTML = `Zasedání zastupitelstva <mark class="banner-hl">${kdyZa(dny)}</mark>`;
  }

  // volby: odpočet k prvnímu dni, během hlasování "právě probíhají"
  const vKdy = document.querySelector('.dash-zm li:not([hidden]) .dash-volby-kdy');
  if (vKdy) {
    const li = vKdy.closest('li');
    const dny = dnu(li.getAttribute('data-from'));
    if (dnu(li.getAttribute('data-until')) >= 0)
      vKdy.innerHTML = dny < 0
        ? 'Volby do zastupitelstva města <mark class="banner-hl">právě probíhají</mark>'
        : `Volby do zastupitelstva města budou <mark class="banner-hl">${kdyZa(dny)}</mark>`;
  }

  // widget bez jediné viditelné položky schovat celý
  document.querySelectorAll('.dash-zm').forEach(z => {
    z.hidden = !z.querySelector('li:not([hidden])');
  });
})();

// ===== Menu v hlavičce: aktivní položku dorolovat do viditelné části lišty =====
(function () {
  document.querySelectorAll('nav.tabs').forEach(tabs => {
  const act = tabs.querySelector('.navlink.active');
  if (act) tabs.scrollLeft = Math.max(0, act.offsetLeft - (tabs.clientWidth - act.offsetWidth) / 2);
  });
})();

// ===== Výška sticky nadpisu sekce (--title-h) — sticky ovládací prvky se lepí pod něj =====
(function () {
  const h = document.querySelector('.panel.active h2.title');
  if (!h) return;
  const set = () => document.documentElement.style.setProperty('--title-h', h.offsetHeight + 'px');
  set();
  window.addEventListener('resize', set);
})();

// ===== Výška sticky lišty hledání (--lc-h) — sticky podnadpisy se lepí pod ni =====
(function () {
  const lc = document.querySelector('.panel.active .list-control');
  if (!lc) return;
  const set = () => document.documentElement.style.setProperty('--lc-h', lc.offsetHeight + 'px');
  set();
  window.addEventListener('resize', set);
})();
