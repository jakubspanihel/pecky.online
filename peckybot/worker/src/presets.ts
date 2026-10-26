// Předpřipravené otázky ze stránky /peckybot/ (content/peckybot.html, .pb-chip). Opakují se nejčastěji
// a stojí nejvíc (více kol s nástroji), proto se jejich odpovědi kešují i tehdy, když obsahují částečné
// „nevím“ (běžná odpověď typu „většinu vím, tohle zdroje neuvádějí“). Test hlídá shodu se stránkou.
import { normalizeQuery } from "./log.ts";

export const PRESETS = [
  "Jak to vypadá se stavbou tělocvičny?",
  "Co naposledy řešila Rada města?",
  "O čem se mluvilo na posledním zastupitelstvu?",
  "Jak se vyvíjí cena vodného a stočného?",
  "Co je nového na úřední desce?",
];

const NORMALIZED = new Set(PRESETS.map(normalizeQuery));

export function isPreset(query: string): boolean {
  return NORMALIZED.has(normalizeQuery(query));
}

/** Odpověď předpřipravené otázky se kešuje, i když je částečně „nevím“, ale jen když je věcná (ne krátké odmítnutí). */
export const PRESET_MIN_ANSWER_CHARS = 300;
