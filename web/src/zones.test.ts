import assert from "node:assert/strict";
import { test } from "node:test";
import { HALF_HOURS, ZONES, browserZone, guessZone, parse, signed, zoneLabel, zoneName, zoneOffset } from "./zones.ts";

test("typed hours", () => {
  assert.equal(parse("+5.5"), 5.5);
  assert.equal(parse("-3:30"), -3.5);
  assert.equal(parse("+2 hrs"), 2);
  assert.equal(parse("new york"), null);
  assert.equal(signed(-4), "-4");
  assert.equal(signed("5.5"), "+5.5");
});

test("names: USA, the rest of the Americas by city, others as they are", () => {
  assert.equal(zoneName("America/New_York"), "USA/New York");
  assert.equal(zoneName("America/Indiana/Knox"), "USA/Indiana/Knox");
  assert.equal(zoneName("Pacific/Honolulu"), "USA/Honolulu");
  assert.equal(zoneName("America/Sao_Paulo"), "Sao Paulo");
  assert.equal(zoneName("Asia/Kolkata"), "Asia/Kolkata");
  assert.equal(zoneLabel("Asia/Kolkata"), "India · Asia/Kolkata");
  assert.equal(zoneLabel("America/Toronto"), "Canada · Toronto");
  assert.equal(zoneLabel("America/New_York"), "USA/New York");
  assert.equal(zoneLabel("UTC"), "UTC");
});

test("the list: Kolkata is there, and every half hour", () => {
  assert.ok(ZONES.includes("Asia/Kolkata") && ZONES.length > 400);
  assert.ok(HALF_HOURS.includes(5.5) && HALF_HOURS.includes(-12) && HALF_HOURS.includes(14) && HALF_HOURS.length === 53);
});

test("DST follows the date", () => {
  assert.equal(zoneOffset("America/New_York", { y: 2026, mo: 1, d: 15, hour: 12 }), -5);
  assert.equal(zoneOffset("America/New_York", { y: 2026, mo: 7, d: 15, hour: 12 }), -4);
  assert.equal(zoneOffset("Asia/Kolkata", { y: 2026, mo: 7, d: 15, hour: 12 }), 5.5);
  assert.equal(zoneOffset("Europe/London", { y: 2026, mo: 3, d: 29, hour: 3 }), 1);   // the morning the clocks went forward
});

test("this computer's zone is one in the list", () => {
  const z = browserZone();
  assert.ok(z === null || ZONES.includes(z));
});

test("a saved chart's zone from its country", () => {
  const at = { y: 2026, mo: 7, d: 1, hour: 12 };
  assert.equal(guessZone("IN", 5.5, at), "Asia/Kolkata");
  assert.equal(guessZone("JP", 9, at), "Asia/Tokyo");
  assert.equal(guessZone("US", -4, at), null);   // several zones keep -4 there
  assert.equal(guessZone("IN", 3, at), null);
});
