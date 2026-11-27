import assert from "node:assert/strict";
import { test } from "node:test";
import { clamp01, spread, verdict } from "./tone.ts";

test("verdict reads good and bad transit results", () => {
  assert.equal(verdict("5th (good)"), "good");
  assert.equal(verdict("8th (vedha)"), "bad");
  assert.equal(verdict("Mitra (Friend)"), "good");
  assert.equal(verdict("Naidhana (Death)"), "bad");
  assert.equal(verdict("Inauspicious"), "bad");     // not read as "auspicious"
  assert.equal(verdict("Janma"), "");
});

test("spread and clamp place values on 0..1", () => {
  const at = spread([2, 4, 6]);
  assert.equal(at(2), 0);
  assert.equal(at(6), 1);
  assert.equal(spread([3, 3])(3), 0.5);
  assert.equal(clamp01(7), 1);
  assert.equal(clamp01(NaN), 0.5);
});
