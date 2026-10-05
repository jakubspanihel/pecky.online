import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { search, tokenize, type Index } from "../src/search.ts";

const index: Index = JSON.parse(readFileSync(new URL("../../index.json", import.meta.url), "utf8"));

test("tokenize: bez diakritiky, zkrácení na 6 znaků, bez stopslov", () => {
  assert.deepEqual(tokenize("Dostavba učeben a tělocvičny v ZŠ Pečky"), ["dostav", "uceben", "telocv", "zs".length >= 3 ? "zs" : ""].filter(Boolean).slice(0, 3));
});

test("tokenize je shodná s Pythonem (scripts/build_peckybot_index.py)", () => {
  const samples = ["Rekonstrukce místních komunikací a vodovodní řad v části Bačov", "Piloty tělocvična — statické zajištění", "Zastupitelé: Paluska, Hubená"];
  const py = execFileSync(
    "python3",
    ["-c", "import sys,json;sys.path.insert(0,'../../scripts');from build_peckybot_index import tokenize;print(json.dumps([tokenize(s) for s in json.loads(sys.argv[1])]))", JSON.stringify(samples)],
    { cwd: new URL("..", import.meta.url).pathname },
  ).toString();
  assert.deepEqual(samples.map(tokenize), JSON.parse(py));
});

test("vyhledávání: tělocvična vrátí úryvky o tělocvičně", () => {
  const hits = search(index, "Co je nového s tělocvičnou a piloty?", 8);
  assert.ok(hits.length > 0);
  const text = hits.map((h) => index.chunks[h.id].t).join(" | ").toLowerCase();
  assert.match(text, /tělocvi|telocvi|dostavba/);
});

test("vyhledávání: neznámý dotaz nevrátí nic", () => {
  assert.equal(search(index, "xqzvwk", 8).length, 0);
});
