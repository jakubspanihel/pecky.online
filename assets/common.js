// ===== assets/common.js — sdílená JS logika, načtená na každé stránce =====
// Vzniklo migrací z jednosouborového index.html (ARCHITEKTURA-MIGRACE.md).
// Obsahuje jen to, co je opravdu napříč sekcemi společné:
// responzivní tabulky, podzáložky (+ jejich odkaz na URL hash), kartičky
// volebních programů, rozbalovací bloky. Logika specifická pro jednu sekci
// (Jednání, Pečecké noviny, Lidé) žije přímo v příslušném content/<sekce>.html.

// ===== Floating info tlačítko v hlavičce: odscrolluje na konec stránky (patička) =====
const infoFab = document.getElementById('infoFab');
const siteFooter = document.querySelector('footer.site');
if (infoFab && siteFooter) {
  infoFab.addEventListener('click', () => {
    siteFooter.scrollIntoView({behavior: 'smooth', block: 'end'});
  });
}

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

  // 1 den / 2-4 dny / 5+ dní
  function dny(n) {
    if (n === 1) return '1 den';
    if (n >= 2 && n <= 4) return n + ' dny';
    return n + ' dní';
  }

  if (n === 0) return 'dnes';
  if (n === 1) return 'včera';
  if (n < 0) return 'plánováno';          // datum v budoucnu (např. ohlášené jednání)
  return 'před ' + dny(n);
}

// ===== Stav sekcí: absolutní datum -> relativní stáří =====
// Zdroj pravdy je tabulka "Stav sekcí" v kořenovém README.md, která drží
// absolutní datumy. Build je vysype do data-date (ISO) a jako viditelný
// text nechá původní datum.
(function () {
  const cells = document.querySelectorAll('.stav-sekci td[data-date]');
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
  document.querySelectorAll('.dash-list [data-date]').forEach(el => {
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
  const items = document.querySelectorAll('.dash-list li[data-until]');
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
    a.insertAdjacentHTML('afterend',
      ` <span class="tag ${tag === 'DNES' ? 'kal-dnes' : 'kal-blizko'}">${tag}</span>`);
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
  const VICE = 'do|na|po|za|od|ve|ke|se|ze|že|či|pro|při|nad|pod|před|přes|bez|což|aby|když|atd\\.';
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
