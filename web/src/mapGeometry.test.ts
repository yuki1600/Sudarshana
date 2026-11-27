import assert from "node:assert/strict";
import { test } from "node:test";
import { bhavaOf, drawn, HALF_HEIGHT, latAt, lonAt, mapY, spread, wrap } from "./mapGeometry.ts";

test("a height on the map turns back into its latitude", () => {
  for (const lat of [-90, -66.5, -20, 0, 35, 80, 90]) assert.ok(Math.abs(latAt(mapY(lat))! - lat) < 1e-6, String(lat));
});

test("a path in degrees keeps its longitudes and takes the map's heights", () => {
  assert.equal(drawn("M-12.5 0L20 90L-180 -90ZM1 2"), `M-12.5 0.0000L20 ${(-HALF_HEIGHT).toFixed(4)}L-180 ${HALF_HEIGHT.toFixed(4)}ZM1 ${(-mapY(2)).toFixed(4)}`);
});

test("off the map is nowhere", () => {
  assert.equal(latAt(HALF_HEIGHT + .01), null);
  assert.equal(latAt(-HALF_HEIGHT - .01), null);
});

test("the polar regions are drawn in", () => {
  assert.ok(mapY(90) - mapY(66) < (mapY(66) - mapY(42)) * .9);
});

test("a curve's longitude at a latitude", () => {
  const curve = [[10, -60], [20, 0], [40, 60]];
  assert.equal(lonAt(curve, -30), 15);
  assert.equal(lonAt(curve, 30), 30);
  assert.equal(wrap(190), -170);
  assert.equal(wrap(-190), 170);
});

test("labels spread apart only as far as they must, and stay on the map", () => {
  assert.deepEqual(spread([0, 100, 200], 44, 700), [0, 100, 200]);
  assert.deepEqual(spread([0, 1, 2, 300], 44, 700), [-43, 1, 45, 300]);
  assert.deepEqual(spread([690, 695, 699], 44, 700), [612, 656, 700]);
  assert.deepEqual(spread([-699, -695, -690], 44, 700), [-700, -656, -612]);
});

test("a place takes the bhava of the band it lies in, across the date line too", () => {
  const line = (lon: number) => [[lon, -70], [lon, 70]];
  // twelve bands 30° wide from 170°E, the last curve closing the first band a turn later
  const bands = Array.from({ length: 13 }, (_, i) => ({ house: (i % 12) + 1, curve: line(170 + 30 * i) }));
  assert.equal(bhavaOf(bands, 175, 10), 1);
  assert.equal(bhavaOf(bands, -175, 10), 1);
  assert.equal(bhavaOf(bands, -155, 10), 2);
  assert.equal(bhavaOf(bands, 165, 10), 12);
  assert.equal(bhavaOf(bands, 165, 80), 0);
});
