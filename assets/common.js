// ===== assets/common.js — sdílená JS logika, načtená na každé stránce =====
// Vzniklo migrací z jednosouborového index.html (ARCHITEKTURA-MIGRACE.md).
// Obsahuje jen to, co je opravdu napříč sekcemi společné: mobilní menu,
// responzivní tabulky, podzáložky (+ jejich odkaz na URL hash), kartičky
// volebních programů, rozbalovací bloky. Logika specifická pro jednu sekci
// (Jednání, Pečecké noviny, Lidé) žije přímo v příslušném content/<sekce>.html.

// ===== Mobilní menu (hamburger) =====
const navToggle = document.getElementById('navToggle');
const tabsNav = document.getElementById('tabs');

function closeMobileNav(){
  tabsNav.classList.remove('open');
  navToggle.setAttribute('aria-expanded', 'false');
}
function openMobileNav(){
  tabsNav.classList.add('open');
  navToggle.setAttribute('aria-expanded', 'true');
}

navToggle.addEventListener('click', () => {
  if (tabsNav.classList.contains('open')) closeMobileNav(); else openMobileNav();
});
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') closeMobileNav();
});
document.addEventListener('click', (e) => {
  if (!tabsNav.classList.contains('open')) return;
  if (tabsNav.contains(e.target) || navToggle.contains(e.target)) return;
  closeMobileNav();
});
// odkazy v nav jsou teď normální <a href>, ale ať se menu po kliknutí
// na mobilu samo zavře (odkaz stejně provede navigaci na novou stránku)
tabsNav.querySelectorAll('.navlink').forEach(link => {
  link.addEventListener('click', closeMobileNav);
});

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

// ===== Stav sekcí: absolutní datum -> relativní stáří =====
// Zdroj pravdy je tabulka "Stav sekcí" v kořenovém README.md, která drží
// absolutní datumy. Build je vysype do data-date (ISO) a jako viditelný
// text nechá původní datum — kdyby JS neběžel, čtenář pořád vidí datum.
// Stáří se počítá až tady, proti hodinám návštěvníka, takže tabulka
// nezastará mezi buildy.
(function () {
  const cells = document.querySelectorAll('.stav-sekci td[data-date]');
  if (!cells.length) return;

  const DEN = 86400000;
  const dnes = new Date();
  dnes.setHours(0, 0, 0, 0);

  // 1 den / 2-4 dny / 5+ dní
  function dny(n) {
    if (n === 1) return '1 den';
    if (n >= 2 && n <= 4) return n + ' dny';
    return n + ' dní';
  }

  function stari(n) {
    if (n === 0) return 'dnes';
    if (n === 1) return 'včera';
    if (n < 0) return 'plánováno';       // datum v budoucnu (např. ohlášené jednání)
    return 'před ' + dny(n);
  }

  cells.forEach(td => {
    const iso = td.getAttribute('data-date');
    const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso || '');
    if (!m) return;                       // nečitelné datum radši nechat být
    const d = new Date(+m[1], +m[2] - 1, +m[3]);
    if (isNaN(d)) return;
    const n = Math.round((dnes - d) / DEN);
    const odhad = td.hasAttribute('data-odhad');
    // absolutní datum se neztrácí — přesune se do tooltipu
    td.title = (odhad ? 'odhad, přesné datum nedoloženo — ' : '') + td.textContent.replace(/\s*\?$/, '').trim();
    td.textContent = stari(n) + (odhad ? ' ?' : '');
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
