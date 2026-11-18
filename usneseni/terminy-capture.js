// Obnovení „Zodpovídá / Termín / Ukončeno“ u otevřených usnesení z usneseni.cz (Claude in Chrome).
// Vložit do javascript_tool v kartě https://mesto-pecky.usneseni.cz/verejne/ (cf_clearance cookie musí být platná),
// pak: await terminyCapture(['UR-339-39/26:152798:rada', 'UZ-45-6/26:153471:zastupitelstvo', …])
//   → Chrome uloží ~/Downloads/terminy-capture-<čas>.json, vrátí „stažených/celkem“.
// Seznam „číslo:id:mod“ vypíše `python3 usneseni/obnovit-terminy.py seznam`.
// Zpracování: `python3 usneseni/obnovit-terminy.py import`.
// Mezi stránkami je pauza 3 s (bez ní Cloudflare zobrazí ověření). Při ověření / prázdné stránce se běh zastaví,
// uloží to, co už je stažené, a nepokračuje — ověření se neobchází, zbytek se stáhne při dalším běhu.
// Proč soubor: výstup javascript_tool blokuje adresy s parametry a je zkrácený.
(() => {
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  window.terminyCapture = async items => {
    const out = [];
    let stop = null;
    for (const it of items) {
      const [n, id, mod] = it.split(':');
      await sleep(3000);
      const html = await (await fetch(`${location.origin}/verejne/usneseni/${id}?mod=${mod}`, { credentials: 'include' })).text();
      const doc = new DOMParser().parseFromString(html, 'text/html');
      const tbl = [...doc.querySelectorAll('table')].find(x => /Číslo usnesení/.test(x.textContent));
      if (!tbl) { stop = `bez detailu u ${n} (ověření nebo prázdná stránka)`; break; }
      const f = {};
      [...tbl.querySelectorAll('tr')].forEach(r => {
        const c = [...r.children].map(x => x.textContent.replace(/ /g, ' ').replace(/\s+/g, ' ').trim());
        if (c.length >= 2) f[c[0]] = c[1];
      });
      out.push({ n, id, fields: f });
    }
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([JSON.stringify({ captured_at: new Date().toISOString(), items: out, stopped: stop })], { type: 'application/json' }));
    a.download = `terminy-capture-${Date.now()}.json`;
    document.body.appendChild(a); a.click(); a.remove();
    return `${out.length}/${items.length}` + (stop ? ' — ZASTAVENO: ' + stop : '');
  };
})();
