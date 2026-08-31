#!/usr/bin/env node
/**
 * Validátor datové sady sekce „Lidé" — pecky.online
 *
 * Spuštění z kořene repa:   node lide/validate.mjs
 * Exit code 0 = čisté, 1 = nalezeny chyby.
 *
 * Bez závislostí, čistý Node (>= 18). Pouštět před každým commitem
 * datové změny v lide/.
 */

import { readFileSync, existsSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const DIR = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(DIR, '..');

const ORG_TYPES = ['urad', 'prispevkova', 'firma', 'spolek', 'politicke', 'skola', 'jine'];
const ROLE_TYPES = [
  'zastupitel', 'rada', 'starosta', 'mistostarosta', 'vedeni',
  'zamestnanec', 'clen', 'komise', 'kandidatka', 'jine',
];

const SLUG = /^[a-z0-9-]+$/;
const DATE_FULL = /^\d{4}-\d{2}-\d{2}$/;
const DATE_YEAR = /^\d{4}$/;
const HEX = /^#[0-9A-Fa-f]{6}$/;

const errors = [];
const warnings = [];
const err = (where, msg) => errors.push(`${where}: ${msg}`);
const warn = (where, msg) => warnings.push(`${where}: ${msg}`);

/* ---------- načtení ---------- */

function load(name) {
  const path = join(DIR, name);
  if (!existsSync(path)) {
    console.error(`CHYBA: chybí soubor lide/${name}`);
    process.exit(1);
  }
  try {
    return JSON.parse(readFileSync(path, 'utf8'));
  } catch (e) {
    console.error(`CHYBA: ${name} není platný JSON — ${e.message}`);
    process.exit(1);
  }
}

const peopleDoc = load('people.json');
const orgsDoc = load('organizations.json');
const affsDoc = load('affiliations.json');

const people = peopleDoc.people ?? [];
const orgs = orgsDoc.organizations ?? [];
const affs = affsDoc.affiliations ?? [];

/* ---------- pomocné ---------- */

const dateOk = (v) => v === null || DATE_FULL.test(v) || DATE_YEAR.test(v);

// porovnání v mixu YYYY / YYYY-MM-DD — holý rok se doplní na hranici intervalu
const cmp = (v, edge) => {
  if (v === null) return null;
  if (DATE_YEAR.test(v)) return edge === 'start' ? `${v}-01-01` : `${v}-12-31`;
  return v;
};

function checkUniqueIds(list, label) {
  const seen = new Map();
  list.forEach((item, i) => {
    const id = item.id;
    if (typeof id !== 'string' || !id) return err(`${label}[${i}]`, 'chybí id');
    if (!SLUG.test(id)) err(`${label} ${id}`, 'id není platný slug (povoleno a-z, 0-9, pomlčka)');
    if (seen.has(id)) err(`${label} ${id}`, `duplicitní id (už použito na indexu ${seen.get(id)})`);
    else seen.set(id, i);
  });
}

function checkMeta(doc, list, file) {
  if (doc.meta?.count !== undefined && doc.meta.count !== list.length) {
    warn(file, `meta.count = ${doc.meta.count}, ale záznamů je ${list.length}`);
  }
  if (doc.meta?.updated && !DATE_FULL.test(doc.meta.updated)) {
    err(file, `meta.updated "${doc.meta.updated}" není ve formátu YYYY-MM-DD`);
  }
  if (doc.meta?.example === true) {
    warn(file, 'meta.example: true — soubor obsahuje ukázková, nikoli ověřená data');
  }
}

/* ---------- kontroly ---------- */

checkUniqueIds(people, 'osoba');
checkUniqueIds(orgs, 'organizace');
checkUniqueIds(affs, 'vazba');

checkMeta(peopleDoc, people, 'people.json');
checkMeta(orgsDoc, orgs, 'organizations.json');
checkMeta(affsDoc, affs, 'affiliations.json');

const personIds = new Set(people.map((p) => p.id));
const orgIds = new Set(orgs.map((o) => o.id));
const affCount = new Map();

// --- osoby ---
for (const p of people) {
  const where = `osoba ${p.id}`;
  if (!p.first_name) err(where, 'chybí first_name');
  if (!p.last_name) err(where, 'chybí last_name');
  if (!Array.isArray(p.tags)) err(where, 'tags musí být pole');
  if (!Array.isArray(p.sources)) err(where, 'sources musí být pole');
  if (p.verified !== null && !DATE_FULL.test(p.verified ?? '')) {
    err(where, `verified musí být null nebo YYYY-MM-DD (je "${p.verified}")`);
  }
  if (p.verified === null) warn(where, 'neověřeno (verified: null) — v UI se nezobrazí stamp');
  if (p.email && !p.email.includes('@')) err(where, `e-mail "${p.email}" nevypadá platně`);
  if (p.photo) {
    if (!existsSync(join(ROOT, p.photo))) err(where, `fotka ${p.photo} neexistuje`);
    if (!p.photo_source) warn(where, 'má fotku, ale prázdné photo_source — doplnit původ');
  }
  for (const s of p.sources ?? []) if (!s?.url) err(where, 'zdroj bez url');
}

// --- organizace ---
for (const o of orgs) {
  const where = `organizace ${o.id}`;
  if (!o.name) err(where, 'chybí name');
  if (!ORG_TYPES.includes(o.type)) err(where, `type "${o.type}" není v číselníku (${ORG_TYPES.join(', ')})`);
  if (o.ico !== null && o.ico !== undefined && o.ico !== '') {
    if (typeof o.ico !== 'string') err(where, 'ico musí být string (kvůli vedoucím nulám)');
    else if (!/^\d{8}$/.test(o.ico)) err(where, `ico "${o.ico}" nemá 8 číslic`);
  }
  if (o.web && !/^https?:\/\//.test(o.web)) err(where, `web "${o.web}" musí začínat http:// nebo https://`);
  if (!Array.isArray(o.former_names)) err(where, 'former_names musí být pole');
  if (o.type === 'politicke') {
    if (!HEX.test(o.color ?? '')) err(where, `uskupení musí mít color jako #RRGGBB (je "${o.color}") — paleta v volby/README.md`);
    if (!o.css_class) err(where, 'uskupení musí mít css_class (party-*) kvůli barvě kartiček');
  }
}

// barvy uskupení nesmí kolidovat — jedna barva = jedno uskupení
const byColor = new Map();
for (const o of orgs.filter((x) => x.type === 'politicke' && x.color)) {
  const prev = byColor.get(o.color.toUpperCase());
  if (prev) err(`organizace ${o.id}`, `barvu ${o.color} už má ${prev}`);
  else byColor.set(o.color.toUpperCase(), o.id);
}

// --- vazby ---
for (const a of affs) {
  const where = `vazba ${a.id}`;

  if (!personIds.has(a.person_id)) err(where, `person_id "${a.person_id}" neexistuje v people.json`);
  else affCount.set(a.person_id, (affCount.get(a.person_id) ?? 0) + 1);

  if (!orgIds.has(a.organization_id)) err(where, `organization_id "${a.organization_id}" neexistuje v organizations.json`);

  if (!a.role) err(where, 'chybí role');
  if (!ROLE_TYPES.includes(a.role_type)) err(where, `role_type "${a.role_type}" není v číselníku (${ROLE_TYPES.join(', ')})`);

  if (!dateOk(a.from)) err(where, `from "${a.from}" musí být YYYY-MM-DD, YYYY nebo null`);
  if (!dateOk(a.to)) err(where, `to "${a.to}" musí být YYYY-MM-DD, YYYY nebo null`);

  const f = cmp(a.from, 'start');
  const t = cmp(a.to, 'end');
  if (f && t && f > t) err(where, `from (${a.from}) je po to (${a.to})`);

  if (typeof a.current !== 'boolean') err(where, 'current musí být true/false');
  if (a.current === true && a.to !== null) err(where, `current: true, ale to je vyplněné ("${a.to}") — buď jedno, nebo druhé`);
  if (a.current === false && a.to === null) warn(where, 'current: false a to je null — ukončená vazba bez data konce');

  if (a.verified !== null && !DATE_FULL.test(a.verified ?? '')) {
    err(where, `verified musí být null nebo YYYY-MM-DD (je "${a.verified}")`);
  }
  if (a.verified === null && !a.note) warn(where, 'neověřeno a bez poznámky — přiznat mezeru v note');

  const expected = `${a.person_id}--${a.organization_id}--`;
  if (typeof a.id === 'string' && !a.id.startsWith(expected)) {
    warn(where, 'id neodpovídá konvenci {person_id}--{organization_id}--{pořadí}');
  }
}

// --- křížové kontroly ---
for (const p of people) {
  if (!affCount.has(p.id)) warn(`osoba ${p.id}`, 'nemá žádnou vazbu — na webu se zobrazí bez funkce');
}

// jen jeden starosta a jedna sada aktuálních funkcí v radě
const currentRada = affs.filter((a) => a.current && ['starosta', 'mistostarosta', 'rada'].includes(a.role_type));
const starostove = currentRada.filter((a) => a.role_type === 'starosta');
if (starostove.length > 1) err('rada', `aktuálních starostů je ${starostove.length}, má být jeden`);
if (currentRada.length !== 7 && currentRada.length !== 0) {
  warn('rada', `aktuálních členů rady je ${currentRada.length}, Pečky mají sedmičlennou radu`);
}

const currentZM = affs.filter((a) => a.current && a.role_type === 'zastupitel');
if (currentZM.length !== 21 && currentZM.length !== 0) {
  warn('zastupitelstvo', `aktuálních zastupitelů je ${currentZM.length}, Pečky mají 21 mandátů`);
}

// každý aktuální zastupitel má být zvolen za nějakou kandidátku
for (const a of currentZM) {
  const hasList = affs.some((x) => x.person_id === a.person_id && x.role_type === 'kandidatka');
  if (!hasList) warn(`osoba ${a.person_id}`, 'je zastupitel, ale nemá vazbu na žádnou kandidátku');
}

/* ---------- výstup ---------- */

const line = `${people.length} osob · ${orgs.length} organizací · ${affs.length} vazeb (${affs.filter((a) => a.current).length} aktuálních)`;
console.log(`\nlide — ${line}`);
console.log(`  zastupitelstvo: ${currentZM.length}/21 · rada: ${currentRada.length}/7\n`);

if (warnings.length) {
  console.log(`VAROVÁNÍ (${warnings.length}):`);
  warnings.forEach((w) => console.log(`  ! ${w}`));
  console.log('');
}

if (errors.length) {
  console.log(`CHYBY (${errors.length}):`);
  errors.forEach((e) => console.log(`  ✗ ${e}`));
  console.log('');
  process.exit(1);
}

console.log('✓ Bez chyb.\n');
