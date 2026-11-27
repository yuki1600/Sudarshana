import { test } from "node:test";
import assert from "node:assert/strict";
import { branchIndex, flyStars, mayaIndex, spaced, spread, stemIndex, wheelAngle, ZIWEI_RING } from "./traditionsMath.ts";

test("the ascendant sits on the left of the wheel, the MC near the top", () => {
  assert.equal(wheelAngle(100, 100), 180);
  assert.equal(wheelAngle(10, 100), 90);       // 90 degrees before the ascendant: the top, where the MC usually is
  assert.equal(wheelAngle(190, 100), 270);     // 90 after: the bottom
});

test("labels too close are moved apart, in their order", () => {
  const out = spread([10, 11, 12, 200], 6);
  assert.ok((out[1] - out[0] + 360) % 360 >= 5.99 && (out[2] - out[1] + 360) % 360 >= 5.99);
  assert.equal(out[3], 200);
  assert.deepEqual(spread([100, 200], 6), [100, 200]);
});

test("the Lo Shu square flies from its centre", () => {
  assert.deepEqual(flyStars(5), [[4, 9, 2], [3, 5, 7], [8, 1, 6]]);
  assert.deepEqual(flyStars(9), [[8, 4, 6], [7, 9, 2], [3, 5, 1]]);    // XALEN's period-9 chart for 2024
});

test("every branch has its own box round the Zi Wei square", () => {
  const boxes = new Set(Object.values(ZIWEI_RING).map(([r, c]) => r * 4 + c));
  assert.equal(boxes.size, 12);
  assert.deepEqual(ZIWEI_RING[0], [3, 2]);     // Zi at the bottom, Wu above it at the top
  assert.deepEqual(ZIWEI_RING[6], [0, 1]);
});

test("names", () => {
  assert.equal(stemIndex("Gui"), 9);
  assert.equal(branchIndex("Sin_", true), 8);
  assert.equal(spaced("TianLiang"), "Tian Liang");
  assert.equal(spaced("Wood3"), "Wood 3");
  assert.equal(mayaIndex("Men"), 14);
  assert.equal(mayaIndex("Ik'"), 1);
  assert.equal(mayaIndex("Ahau"), 19);
  assert.equal(mayaIndex("Chicchan"), 4);
});
