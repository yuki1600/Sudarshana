import assert from "node:assert/strict";
import { test } from "node:test";
import { applyFilter, categoryOf, cellMatches, chiSquareP, compare, countBy, NO_FILTER, titleOf, toBirth, yearBins, yearOf, type FactorRow, type Tagged } from "./mundaneMath.ts";

const quake: Tagged = { set: "disasters", id: "ea5823", type: "earthquake", date: "2004-12-26", time: "00:58:53", tz_east: 0, time_confidence: "exact",
  place: "Sumatra", country: "Indonesia", iso2: "ID", lat: 3.295, lon: 95.982, magnitude: 9.1, deaths: 227899, source: "x" };
const vesuvius: Tagged = { set: "disasters", id: "vo1348", type: "volcano", name: "Vesuvius", date: "0079-08-25", tz_east: 0.96, gregorian: false,
  time_confidence: "date", country: "Italy", lat: 40.8, lon: 14.4, magnitude: 5, source: "x" };
const india: Tagged = { set: "nations", id: "na-in", chart_name: "Independence", event: "independence", country: "India", iso2: "IN", date: "1947-08-15",
  time: "00:00", tz_east: 5.5, time_confidence: "exact", lat: 28.6, lon: 77.2, source: "x" };
const bce: Tagged = { ...quake, id: "ea1", date: "-2150-01-01", time: null, time_confidence: "date" };

test("a record casts at its own moment, an untimed one at local noon, BCE and Julian kept", () => {
  const b = toBirth(quake);
  assert.equal(b.year, 2004); assert.equal(b.month, 12); assert.equal(b.day, 26);
  assert.ok(Math.abs(b.hour_local - (58 / 60 + 53 / 3600)) < 1e-9);
  assert.equal(b.tz_east_hours, 0); assert.equal(b.longitude_east, 95.982);
  const v = toBirth(vesuvius);
  assert.equal(v.hour_local, 12); assert.equal(v.gregorian, false); assert.equal(v.year, 79);
  assert.equal(toBirth(bce).year, -2150);
  assert.equal(yearOf(bce), -2150);
});

test("titles name the event", () => {
  assert.equal(titleOf(vesuvius), "Vesuvius");
  assert.equal(titleOf(quake), "Earthquake, Sumatra, Indonesia");
  assert.equal(titleOf(india), "India: Independence");
});

test("the filter keeps by set, words and any of the chosen countries", () => {
  const all = [quake, vesuvius, india, bce];
  assert.equal(applyFilter(all, NO_FILTER).length, 4);
  assert.deepEqual(applyFilter(all, { ...NO_FILTER, sets: ["nations"] }).map((r) => r.id), ["na-in"]);
  assert.deepEqual(applyFilter(all, { ...NO_FILTER, text: "vesuv" }).map((r) => r.id), ["vo1348"]);
  assert.deepEqual(applyFilter(all, { ...NO_FILTER, country: ["IN"] }).map((r) => r.id), ["na-in"]);
  assert.deepEqual(applyFilter(all, { ...NO_FILTER, country: ["IN", "Italy"] }).map((r) => r.id), ["vo1348", "na-in"]);
});

test("year bins cover the span and count every record", () => {
  const bins = yearBins([quake, india, vesuvius], 10);
  assert.equal(bins[0][0], 79);
  assert.equal(bins.reduce((a, [, c]) => a + c, 0), 3);
});

const row = (sun: number, house: number | null, tithi?: number): FactorRow =>
  ({ jd: 0, timed: house !== null, lagna: house === null ? null : 0, weekday: 0, tithi, p: { Sun: [sun, sun * 2, 0, house] } });

test("categories: a house needs a time, a tithi needs the Moon", () => {
  assert.equal(categoryOf(row(3, 4), { kind: "house", body: "Sun" }), 3);
  assert.equal(categoryOf(row(3, null), { kind: "house", body: "Sun" }), null);
  assert.equal(categoryOf(row(3, null), { kind: "tithi" }), null);
  assert.equal(categoryOf(row(3, null, 16), { kind: "paksha" }), 1);
});

test("observed against the control's shares, with a chi-square p", () => {
  const events = [...Array(30)].map((_, i) => ({ ...row(0, null), id: `e${i}` }));
  const control = [...Array(120)].map((_, i) => row(i % 12, null));
  const t = compare(events, control, { kind: "sign", body: "Sun" });
  assert.equal(t.n, 30);
  assert.equal(t.cells[0].observed, 30);
  assert.equal(t.cells[0].expected, 2.5);
  assert.equal(t.cells[0].ratio, 12);
  assert.equal(t.cells[0].ids.length, 30);
  assert.ok(t.p < 1e-6);
  const even = compare(control.slice(0, 24).map((r, i) => ({ ...r, id: String(i) })), control, { kind: "sign", body: "Sun" });
  assert.ok(even.p > 0.9);
});

test("chi-square tail matches the table", () => {
  assert.ok(Math.abs(chiSquareP(3.841, 1) - 0.05) < 0.006);
  assert.ok(Math.abs(chiSquareP(19.675, 11) - 0.05) < 0.003);
});

const unsworn: Tagged = { set: "elections", id: "el-1", country: "India", iso2: "IN", office: "Prime Minister", winner: "X", oath_known: false,
  date: "1984-12-28", tz_east: 5.14, time_confidence: "date", lat: 28.6, lon: 77.2, source: "x" };
const draw: Tagged = { set: "sports", id: "sp-1", competition: "FIFA World Cup", sport: "Football", team_a: "A", team_b: "B", winner: null, iso2: "IT",
  date: "1934-06-01", time: "16:30", tz_east: 1, time_confidence: "exact", lat: 43.8, lon: 11.2, source: "x" };
const womens: Tagged = { ...draw, id: "sp-2", competition: "FIFA Women's World Cup", winner: "A" };

test("the competition filter is exact, and countBy counts largest first", () => {
  assert.deepEqual(applyFilter([draw, womens], { ...NO_FILTER, competition: ["FIFA World Cup"] }).map((r) => r.id), ["sp-1"]);
  assert.deepEqual(countBy([quake, vesuvius, india, unsworn], (r) => String(r.country)), [["India", 2], ["Indonesia", 1], ["Italy", 1]]);
});

test("a column filter is a substring, or a comparison with the number in the cell", () => {
  assert.ok(cellMatches("Earthquake", "quake"));
  assert.ok(cellMatches("1990-05-12", ">1989") && !cellMatches("1990-05-12", "<1990"));
  assert.ok(cellMatches("M 7.4", ">=7.4") && cellMatches("12,500", ">10000"));
  assert.ok(!cellMatches("", ">1"));
});
