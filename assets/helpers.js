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

const J_TITLE_RE = /^(Ing\.|Mgr\.|Bc\.|MUDr\.|PhDr\.|JUDr\.|RNDr\.|MgA\.|Ph\.D\.|CSc\.|DiS\.|MSc\.|doc\.|prof\.)$/i;
function jInitials(name){
  const parts = (name || '').split(/\s+/).filter(p => p && !J_TITLE_RE.test(p));
  if (!parts.length) return '?';
  const first = parts[0][0] || '';
  const last = parts.length > 1 ? parts[parts.length - 1][0] : '';
  return (first + last).toUpperCase();
}

// normalizovaný klíč "jméno příjmení" bez titulů/diakritiky/velikosti písmen -
// pro spárování jmen napříč zdroji, které titul zapisují jinak (s/bez čárky
// před titulem za jménem apod.), viz jednani/README.md "Jmenovité obsazení"
function jNameKey(name){
  const parts = (name || '').split(/\s+/).filter(p => p && !J_TITLE_RE.test(p));
  return jNorm(parts.join(' '));
}

// kořenově-absolutní interní odkaz (z JSON dat, ne ze statického HTML) na
// nasazení, které běží na GitHub Pages subcestě (viz SITE_BASE_PATH ve
// scripts/build.py, window.SITE_BASE_PATH injektováno v templates/page.html)
function jWithBase(url){
  return (url && url.charAt(0) === '/') ? (window.SITE_BASE_PATH || '') + url : (url || '');
}
