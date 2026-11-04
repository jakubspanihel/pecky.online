// Sběr jednání z usneseni.cz do souboru ke stažení (Claude in Chrome).
// Vložit do javascript_tool v kartě https://mesto-pecky.usneseni.cz/verejne/ (cf_clearance cookie musí být platná),
// pak: await archCapture('<uuid>')  → Chrome uloží ~/Downloads/archive-capture-<uuid8>.json
//      await archListing()          → ~/Downloads/archive-capture-listing.json (řádky výpisu s odkazy)
// Zpracování: python3 jednani/scripts/archive_capture_import.py <složka se staženými soubory>
// Proč soubor: výstup javascript_tool je zkrácen na ~1 kB, zápis jednání má desítky kB.
(() => {
  const BASE = location.origin;
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  const download = (obj, name) => {
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([JSON.stringify(obj)], { type: 'application/json' }));
    a.download = name;
    document.body.appendChild(a); a.click(); a.remove();
  };
  // innerText vyžaduje vykreslený element -> vložíme HTML do odsunutého divu
  const renderedText = html => {
    const d = document.createElement('div');
    d.style.cssText = 'position:absolute;left:-99999px;top:0;width:900px';
    d.innerHTML = html;
    document.body.appendChild(d);
    const t = d.innerText;
    const tables = [...d.querySelectorAll('table')];
    const out = { text: t, tables };
    return { d, out, t };
  };
  const getDoc = async url => new DOMParser().parseFromString(await (await fetch(url, { credentials: 'include' })).text(), 'text/html');

  window.archListing = async () => {
    const rows = [];
    for (let p = 1; p <= 3; p++) {
      const doc = await getDoc(`${BASE}/verejne/?page=${p}`);
      doc.querySelectorAll('table tr').forEach(tr => {
        const tds = [...tr.children];
        if (tds.length < 2) return;
        rows.push({ page: p, cells: tds.map(c => c.textContent.replace(/\s+/g, ' ').trim()),
          links: [...tr.querySelectorAll('a')].map(a => ({ text: a.textContent.trim(), href: a.getAttribute('href') })) });
      });
    }
    download({ rows }, 'archive-capture-listing.json');
    return rows.length;
  };

  // archCapture(uuid, {expectMinutes: true}) — u jednání, které už má zápis, se prázdná odpověď serveru
  // (po rychlé sérii požadavků) opakuje až 3×; u jednání jen s Pozvánkou dát {expectMinutes: false}
  window.archCapture = async (uuid, opts = {}, attempt = 1) => {
    await sleep(attempt === 1 ? 4000 : 10000);
    const expect = opts.expectMinutes !== false;
    const res = { uuid, captured_at: new Date().toISOString() };
    // zápis
    const zdoc = await getDoc(`${BASE}/verejne/${uuid}/zapis/`);
    const rep = zdoc.querySelector('#report');
    if (rep) {
      const { d, t } = renderedText(rep.outerHTML);
      res.minutes = { url: `${BASE}/verejne/${uuid}/zapis/`, text: t };
      d.remove();
    } else res.minutes = null;
    // usnesení + detaily
    const rdoc = await getDoc(`${BASE}/verejne/${uuid}/usneseni/`);
    const tbl = [...rdoc.querySelectorAll('table')].find(x => /Číslo usnesení/.test(x.textContent));
    res.resolutions = { url: `${BASE}/verejne/${uuid}/usneseni/`, items: [] };
    if (tbl) {
      const mod = /\/usneseni\/\d+\?mod=(\w+)/.exec(rdoc.documentElement.innerHTML);
      for (const tr of [...tbl.querySelectorAll('tr')].slice(1)) {
        const tds = [...tr.children];
        if (tds.length < 6) continue;
        const html = [tr, ...tr.querySelectorAll('*')].map(e => e.getAttribute('onclick') || '').join(' ');
        const m = /usneseni\/(\d+)(\?mod=\w+)?/.exec(html);
        const item = { cells: tds.map(c => c.innerHTML.replace(/<br\s*\/?>/g, '\n').replace(/<[^>]+>/g, '').replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&').replace(/&quot;/g, '"').replace(/&lt;/g, '<').replace(/&gt;/g, '>').trim()),
          detail_id: m ? +m[1] : null, detail_mod: m && m[2] ? m[2] : null };
        if (item.detail_id) {
          await sleep(400);
          const ddoc = await getDoc(`${BASE}/verejne/usneseni/${item.detail_id}${item.detail_mod || ''}`);
          const dt = [...ddoc.querySelectorAll('table')].find(x => /Číslo usnesení/.test(x.textContent));
          item.detail_fields = dt ? [...dt.querySelectorAll('tr')].map(r => [...r.children].map(c => c.textContent.replace(/ /g, ' ').trim())) : null;
        }
        res.resolutions.items.push(item);
      }
    }
    if (expect && (!res.minutes || !res.resolutions.items.length) && attempt < 3) return window.archCapture(uuid, opts, attempt + 1);
    // pozvánka (PDF) -> text přes pdf.js
    try {
      if (!window.pdfjsLib) {
        await new Promise((ok, ko) => { const s = document.createElement('script'); s.src = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js'; s.onload = ok; s.onerror = ko; document.head.appendChild(s); });
        pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
      }
      const r = await fetch(`${BASE}/verejne/?uuid=${uuid}&do=printPublicInvitation`, { credentials: 'include' });
      if (r.ok && /pdf/i.test(r.headers.get('content-type') || '')) {
        const pdf = await pdfjsLib.getDocument({ data: await r.arrayBuffer() }).promise;
        const pages = [];
        for (let i = 1; i <= pdf.numPages; i++) {
          const tc = await (await pdf.getPage(i)).getTextContent();
          let y = null, line = '', lines = [];
          for (const it of tc.items) {
            const yy = Math.round(it.transform[5]);
            if (y !== null && Math.abs(yy - y) > 2) { lines.push(line); line = ''; }
            y = yy; line += it.str;
            if (it.hasEOL) { lines.push(line); line = ''; y = null; }
          }
          if (line) lines.push(line);
          pages.push(lines.join('\n'));
        }
        res.invitation = { status: 'ok', pages: pdf.numPages, text: pages.join('\n') };
      } else res.invitation = { status: 'site_error', http: r.status };
    } catch (e) { res.invitation = { status: 'error', error: String(e) }; }
    download(res, `archive-capture-${uuid.slice(0, 8)}.json`);
    return { uuid: uuid.slice(0, 8), min: res.minutes ? res.minutes.text.length : 0, res: res.resolutions.items.length, inv: res.invitation.status };
  };
  return 'archCapture ready';
})();
