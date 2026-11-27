import assert from "node:assert/strict";
import { test } from "node:test";
import { GHATAKA, ghatakaHits, SHALAKA, shalakaPartner, SYLLABLES } from "./chakraTables.ts";

test("Sapta Shalaka: each star pierces the one at the other end of its line, both ways", () => {
  assert.deepEqual(["Krit", "Rohi", "Magh", "PPha", "Visa"].map(shalakaPartner), ["Srav", "Abhi", "Bhar", "Aswi", "Dhan"]);
  for (const s of SHALAKA) assert.equal(shalakaPartner(shalakaPartner(s)), s);
});

test("a syllable for every pada, and every Ghataka column for all twelve Moon signs", () => {
  assert.equal(SYLLABLES.length, 108);
  assert.deepEqual([SYLLABLES[0], SYLLABLES[50], SYLLABLES[107]], ["Chu", "Na", "Chi"]);     // Ashwini 1, Hasta 3, Revati 4
  for (const col of Object.values(GHATAKA)) assert.equal(col.length, 12);
});

test("Ghataka: a Scorpio Moon is hurt by a Friday, a Nanda tithi, Revati and the Moon in Taurus", () => {
  // Ashwina (6), Krishna Ekadashi (25), Friday, Revati (26), Moon in Taurus (1)
  assert.deepEqual(ghatakaHits(7, { month: 6, tithi: 25, weekday: 5, nakshatra: 26, moon_sign: 1 }), [true, true, true, true, true]);
  assert.deepEqual(ghatakaHits(7, { month: 0, tithi: 1, weekday: 0, nakshatra: 0, moon_sign: 0 }), [false, false, false, false, false]);
});
