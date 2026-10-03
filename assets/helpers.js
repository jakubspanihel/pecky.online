// ===== assets/helpers.js — čisté pomocné funkce sdílené napříč sekcemi =====
// Vzniklo migrací z jednosouborového index.html: tyhle funkce byly původně
// definované jen jednou (protože celý web běžel na jedné stránce) a používaly
// je zároveň sekce Jednání, Pečecké noviny i Lidé. Načíst PŘED
// content/jednani.html, content/noviny.html a content/lide.html.

function jStripDiacritics(s){
  return (s || '').toString().normalize('NFD').replace(/[̀-ͯ]/g, '');
}
function jNorm(s){ return jStripDiacritics(s).toLowerCase(); }

function jEscapeHtml(s){
  return (s || '').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
}

function jHighlight(text, rawQuery){
  let html = jEscapeHtml(text || '');
  const words = (rawQuery || '').trim().split(/\s+/).filter(w => w.length > 1);
  words.forEach(w => {
    const esc = w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    if (!esc) return;
    try { html = html.replace(new RegExp('(' + esc + ')', 'gi'), '<mark>$1</mark>'); } catch (e) {}
  });
  return html;
}

const J_TITLE_RE = /^(Ing\.|Mgr\.|Bc\.|MUDr\.|PhDr\.|JUDr\.|RNDr\.|MgA\.|PaedDr\.|Ph\.D\.|CSc\.|DiS\.|MSc\.|M\.Sc\.|MBA|MPA|arch\.|doc\.|prof\.)$/i;
function jInitials(name){
  const parts = (name || '').split(/[\s,]+/).filter(p => p && !J_TITLE_RE.test(p));
  if (!parts.length) return '?';
  const first = parts[0][0] || '';
  const last = parts.length > 1 ? parts[parts.length - 1][0] : '';
  return (first + last).toUpperCase();
}

// normalizovaný klíč "jméno příjmení" bez titulů/diakritiky/velikosti písmen -
// pro spárování jmen napříč zdroji, které titul zapisují jinak (s/bez čárky
// před titulem za jménem apod.), viz jednani/README.md "Jmenovité obsazení"
function jNameKey(name){
  const parts = (name || '').split(/[\s,]+/).filter(p => p && !J_TITLE_RE.test(p));
  return jNorm(parts.join(' '));
}

// kořenově-absolutní interní odkaz (z JSON dat, ne ze statického HTML) na
// nasazení, které běží na GitHub Pages subcestě (viz SITE_BASE_PATH ve
// scripts/build.py, window.SITE_BASE_PATH injektováno v templates/page.html)
function jWithBase(url){
  return (url && url.charAt(0) === '/') ? (window.SITE_BASE_PATH || '') + url : (url || '');
}

// ===== Vizitka osoby (person-detail) — sdílená komponenta =====
// Vznikla vytažením z content/lide.html (detail osoby v sekci Lidé), aby ji
// šlo znovu použít i mimo tu sekci — např. u jména v tabulce Jednání →
// Absence. Data (lide/people.json, organizations.json, affiliations.json)
// a rozhodnutí, kdy kartu otevřít/zavřít, zůstávají na volajícím; tady jen
// čisté formátování a vykreslení. Vstupem je vždy záznam osoby z people.json
// s dopočítaným `_timeline` (viz pcBuildTimeline níže).

const PC_TL_ORDER = ['starosta', 'mistostarosta', 'rada', 'vedeni-urad', 'vedeni-organizace', 'komise', 'zastupitel', 'zamestnanec', 'ucitel', 'vychovatel', 'asistent-pedagoga', 'provozni', 'trener', 'clen', 'kandidatka'];
// váha funkce v timeline detailu — od nejvýznamnější po nejobecnější
function pcTlRank(t){
  const i = PC_TL_ORDER.indexOf(t);
  return i === -1 ? PC_TL_ORDER.length : i;
}

function pcFullName(p){
  return [p.title_before, p.first_name, p.last_name, p.title_after].filter(Boolean).join(' ');
}
// Vizitky: u osob s `censor_surname` jen iniciála příjmení + chip „cenzura";
// data zůstávají celá, mění se jen vizuální výpis. Vrací HTML.
function pcDisplayNameHtml(p){
  if (!p.censor_surname) return jEscapeHtml(pcFullName(p));
  const ini = (p.last_name || '').trim().charAt(0);
  return jEscapeHtml([p.first_name, ini ? ini + '.' : ''].filter(Boolean).join(' ')) +
    ' <span class="stamp stamp-sm stamp-plain">cenzura</span>';
}
function pcPlainName(p){
  return [p.first_name, p.last_name].filter(Boolean).join(' ');
}
// Gramaticky správný tvar podle rodu osoby (přítomen/přítomna,
// zvolen/zvolena…) — jediné místo na webu, které vybírá mezi mužským
// a ženským tvarem, ať se nepíšou natvrdo mužské tvary jinde (viz
// lide/README.md § „České skloňování osob (gender)"). `p.gender` je
// "m"/"f" z people.json (SPEC.md §3.2); bez záznamu osoby (p je null/
// undefined, jméno se nepodařilo spárovat) padá na mužský tvar jako
// dosavadní výchozí chování.
function pcGendered(p, masc, fem){
  return (p && p.gender === 'f') ? fem : masc;
}
// "1. místostarosta (uvolněný)" → "1. místostarosta"; první písmeno velké
function pcRoleLabel(role){
  const t = (role || '').replace(/\s*\((?:ne)?uvolněný\)\s*$/i, '').trim();
  return t ? t.charAt(0).toUpperCase() + t.slice(1) : '';
}
function pcFormatDate(iso){
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso || '');
  if (m) return `${Number(m[3])}. ${Number(m[2])}. ${m[1]}`;
  return /^\d{4}$/.test(iso || '') ? iso : (iso || '');
}
// řadicí klíč z data v mixu YYYY / YYYY-MM-DD; prázdné datum až nakonec
function pcDateKey(v){
  if (!v) return '0000-00-00';
  return /^\d{4}$/.test(v) ? v + '-01-01' : v;
}
// Kandidatura je jednorázová událost, ne trvající stav. V datech má
// current: true a to: null, takže by se v timeline vykreslila jako
// „– dosud" a vyskočila nad skutečné, dávno ukončené funkce. Pro zobrazení
// a řazení ji proto za aktivní nepovažujeme.
function pcActive(a){
  return !!a.current && a.role_type !== 'kandidatka';
}
// období vazby lidsky; rozlišuje „trvá" od „konec neznámý"
function pcRange(a){
  const from = a.from ? pcFormatDate(a.from) : '';
  if (a.role_type === 'kandidatka') return from ? `volby ${from}` : 'termín voleb neznámý';
  if (a.current) return from ? `${from} – dosud` : 'trvá, začátek neznámý';
  if (a.to) return from ? `${from} – ${pcFormatDate(a.to)}` : `do ${pcFormatDate(a.to)}`;
  return from ? `od ${from}, konec neznámý` : 'období neznámé';
}
// Telefon může nést víc čísel (kancelář a služební mobil), oddělovač „ · ".
// Každé dostane vlastní odkaz tel:, v href bez mezer.
function pcPhoneLinks(phone){
  return (phone || '').split('·').map(x => x.trim()).filter(Boolean)
    .map(num => `<a href="tel:${jEscapeHtml(num.replace(/[^\d+]/g, ''))}">${jEscapeHtml(num)}</a>`)
    .join(' · ');
}
// Zdroje osob, vazeb a organizací jsou v datech jen id z lide/sources.json
// (SPEC §3.8). Číselník se načte jednou přes pcLoadSources() — stránka ho
// přidá do svého Promise.all s people/affiliations/organizations.
const PC_SOURCES = {};
let PC_SOURCES_LOADING = null;
function pcLoadSources(){
  if (!PC_SOURCES_LOADING) {
    PC_SOURCES_LOADING = Promise.all([
      fetch('/lide/sources.json')
        .then(r => { if (!r.ok) throw new Error('sources.json: HTTP ' + r.status); return r.json(); })
        .then(doc => { Object.assign(PC_SOURCES, doc.sources || {}); }),
      jLoadRefs()
    ]).then(() => PC_SOURCES);
  }
  return PC_SOURCES_LOADING;
}

// ===== Zmínky jednání a Pečeckých novin v textu -> odkazy =====
// Pravidlo webu: zmínka je vždy odkaz přímo na text ve větě. jLinkRefs()
// bere už escapovaný HTML text a obalí: "ZM 6/2026", "RM 14. 11. 2022",
// "Pečecké noviny 12/2018[, s. 3]", "UR-288-32/26" (usnesení -> jednání). Mapy se načtou v jLoadRefs() (volá ji
// pcLoadSources); co se nenajde, zůstane prostým textem.
const J_REFS = {meet: {}, dates: {}, issues: {}};   // meet['ZM 6/2026'] = ISO; dates['RM 2022-11-14'] = true
let J_REFS_LOADING = null;
function jLoadRefs(){
  if (!J_REFS_LOADING) {
    const pre = {Zastupitelstvo: 'ZM', Rada: 'RM'};
    J_REFS_LOADING = Promise.all([
      fetch('/jednani/pecky-jednani.json').then(r => r.ok ? r.json() : null).catch(() => null),
      fetch('/noviny/issues.json').then(r => r.ok ? r.json() : null).catch(() => null)
    ]).then(([jed, nov]) => {
      ((jed && jed.meetings) || []).forEach(m => {
        const k = pre[m.type];
        if (!k) return;
        if (m.number) J_REFS.meet[k + ' ' + m.number + '/' + m.date.slice(0, 4)] = m.date;
        J_REFS.dates[k + ' ' + m.date] = true;
      });
      ((nov && nov.issues) || []).forEach(e => {
        const [y, a, b] = e.slug.split('-').map(Number);
        for (let mo = a; mo <= (b || a); mo++) J_REFS.issues[mo + '/' + y] = e.slug;
      });
    });
  }
  return J_REFS_LOADING;
}
const J_REF_RE = /\b(?:(ZM|RM) (?:(\d{1,2})\/(20\d\d)|(\d{1,2})\. (\d{1,2})\. (20\d\d))|Pečecké noviny (\d{1,2})\/((?:19|20)\d\d)(?:, (?:s|str)\. (\d+))?|(U[RZ])-\d+-(\d{1,2})\/(\d{2}))/g;
function jLinkRefs(html){
  return (html || '').replace(J_REF_RE, (all, kind, n, y, d, mo, y2, issue, iy, page, ures, un, uy) => {
    const meetHref = iso => `${jWithBase('/jednani/')}#${kind === 'ZM' || ures === 'UZ' ? 'zastupitelstvo' : 'rada'}-${iso}`;
    if (ures) {
      // usnesení UR-288-32/26 / UZ-35-6/26 -> jednání, na kterém bylo přijato
      kind = ures === 'UZ' ? 'ZM' : 'RM';
      const iso = J_REFS.meet[kind + ' ' + un + '/20' + uy];
      return iso ? `<a href="${meetHref(iso)}">${all}</a>` : all;
    }
    if (kind) {
      const iso = n ? J_REFS.meet[kind + ' ' + n + '/' + y]
        : (y2 + '-' + String(mo).padStart(2, '0') + '-' + String(d).padStart(2, '0'));
      if (!iso || (!n && !J_REFS.dates[kind + ' ' + iso])) return all;
      return `<a href="${meetHref(iso)}">${all}</a>`;
    }
    const slug = J_REFS.issues[issue + '/' + iy];
    if (!slug) return all;
    return `<a href="${jWithBase('/noviny/Data/PN%20' + iy + '/' + slug + '.pdf')}${page ? '#page=' + page : ''}" target="_blank" rel="noopener">${all}</a>`;
  });
}
function pcSourceLinks(sources){
  return (sources || []).map(s => typeof s === 'string' ? PC_SOURCES[s] : s)
    .filter(s => s && s.url)
    .map(s => `<a href="${jEscapeHtml(s.url)}" target="_blank" rel="noopener">${jEscapeHtml(s.label || s.url)} ↗</a>`)
    .join('');
}

// vazby dané osoby (affiliations) seřazené pro timeline v detailu — aktuální
// nahoru, uvnitř podle váhy funkce a pak od nejnovější; každá vazba dostane
// rozvinutou organizaci (`_org`)
function pcBuildTimeline(personId, affs, orgById){
  return (affs || [])
    .filter(a => a.person_id === personId)
    .map(a => Object.assign({}, a, {_org: (orgById && orgById[a.organization_id]) || a._org || null}))
    .sort((x, y) =>
      (Number(pcActive(y)) - Number(pcActive(x))) ||
      (pcTlRank(x.role_type) - pcTlRank(y.role_type)) ||
      pcDateKey(y.from).localeCompare(pcDateKey(x.from)));
}

// avatar osoby (fotka, nebo barevný kroužek s iniciálami) — pro kartičku
// v sekci Lidé (opts.ring = barva obrysu dle uskupení) i pro jednotlivý odkaz na osobu jinde na webu (menší, opts.size)
function pcAvatarHtml(p, opts){
  opts = opts || {};
  const size = opts.size || 64;
  const cls = opts.cls ? ' ' + opts.cls : '';
  const name = pcPlainName(p);
  // photos je řazené nejnovější první (lide/SPEC.md §3.7) — vždy ta aktuální
  const ring = opts.ring ? ` --ring:${jEscapeHtml(opts.ring)};` : '';
  const photo = (p.photos && p.photos.length) ? p.photos[0] : null;
  if (photo) {
    const url = jWithBase(photo.url);
    return `<img class="avatar${cls}" style="width:${size}px; height:${size}px;${ring}" src="${jEscapeHtml(url)}" alt="${jEscapeHtml(name)}" loading="lazy" width="${size}" height="${size}">`;
  }
  const color = '#5B5347';
  return `<div class="avatar-fallback${cls}" style="width:${size}px; height:${size}px; background:${jEscapeHtml(color)};${ring}" aria-hidden="true">${jInitials(pcFullName(p))}</div>`;
}

// plná vizitka osoby — stejná karta jako v detailu sekce Lidé.
// opts:
//   id            - DOM id kořenového elementu (výchozí `person-detail-<id>`)
//   closeAttr     - data-atribut na tlačítku „zavřít", který si přečte volající JS
//   orgHrefPrefix - prefix před `#lide/uskupeni/<id>` v odkazu na uskupení;
//                   mimo stránku /lide/ musí vést celou cestou (jWithBase('/lide/'))
// Vazba může nést předvykreslené `_extraHtml` (už escapované HTML), které se
// vloží pod poznámku — Lidé tam dávají účast na jednáních výborů.
function pcDetailHtml(p, opts){
  opts = opts || {};
  const closeAttr = opts.closeAttr || 'data-person-detail-close';
  const orgHrefPrefix = opts.orgHrefPrefix || '';
  const timeline = p._timeline || [];

  const items = timeline.map(a => {
    const org = a._org;
    const orgHtml = org
      ? `<a href="${orgHrefPrefix}#lide/uskupeni/${encodeURIComponent(org.id)}">${jEscapeHtml(org.name)}</a>`
      : '—';
    const src = pcSourceLinks(a.sources);
    return `
        <li class="tl-item ${pcActive(a) ? 'tl-item--current' : 'tl-item--past'}">
          <span class="tl-role">${jEscapeHtml(pcRoleLabel(a.role))}</span>
          <span class="tl-org">· ${orgHtml}</span>
          <span class="tl-range">${jEscapeHtml(pcRange(a))}${a.verified ? '' : ' · neověřeno'}</span>
          ${a.note ? `<p class="tl-note">${jLinkRefs(jEscapeHtml(a.note))}</p>` : ''}
          ${a._extraHtml || ''}
          ${src ? `<p class="tl-src">${src}</p>` : ''}
        </li>`;
  }).join('');

  // Povolání je sebedeklarace z volebních podkladů, ne ověřený současný stav —
  // proto pole s ročníkem u každé položky (lide/SPEC.md §3.6c).
  const occupation = (p.occupations || []).length
    ? `<p class="detail-bio"><span class="occ-label">Povolání</span> ` +
      p.occupations.map(o =>
        `${jEscapeHtml(o.value)} <span class="occ-note">(${jEscapeHtml(String(o.year))})</span>`
      ).join(' · ') +
      ` <span class="occ-note">— podle volebních podkladů daného roku</span></p>`
    : '';

  const contacts = [
    p.email ? `<a href="mailto:${jEscapeHtml(p.email)}">${jEscapeHtml(p.email)}</a>` : '',
    pcPhoneLinks(p.phone)
  ].filter(Boolean).join(' · ');

  const meta = [
    p.verified ? `<span class="stamp">ověřeno</span> ${jEscapeHtml(pcFormatDate(p.verified))}` : '',
    pcSourceLinks(p.sources)
  ].filter(Boolean).join(' · ');

  // víc fotek na osobu (lide/SPEC.md §3.7) — všechny, ne jen ta aktuální na kartičce
  const photosHtml = (p.photos || []).length
    ? `<p class="detail-meta">Fotografie: ${p.photos.map(ph =>
        `${jEscapeHtml(String(ph.year))} — ${jLinkRefs(jEscapeHtml(ph.photo_source || ''))}`
      ).join(' · ')}</p>`
    : '';

  return `
      <div class="person-detail" id="${jEscapeHtml(opts.id || ('person-detail-' + p.id))}">
        <div class="detail-head">
          <span class="detail-name">${pcDisplayNameHtml(p)}${
            (p.former_last_names || []).length
              ? ` <span class="occ-note">dříve ${jEscapeHtml(p.former_last_names.join(', '))}</span>`
              : ''}</span>
          <button type="button" class="detail-close" ${closeAttr}>zavřít ✕</button>
        </div>
        ${p.bio ? `<p class="detail-bio">${jLinkRefs(jEscapeHtml(p.bio))}</p>` : ''}
        ${occupation}
        ${contacts ? `<p class="detail-bio">${contacts}</p>` : ''}
        <ul class="timeline">${items || '<li class="tl-item tl-item--past">Žádná doložená vazba.</li>'}</ul>
        ${meta ? `<p class="detail-meta">${meta}</p>` : ''}
        ${photosHtml}
      </div>`;
}
