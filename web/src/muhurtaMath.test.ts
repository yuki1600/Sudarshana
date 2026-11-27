import assert from "node:assert/strict";
import { test } from "node:test";
import { angleAt, clockText, goodWindows, hourAt, hoursOn, besidePlace, hourText, lanes, mergeSpans, sector, ticks, verdict, vedic, type Span } from "./muhurtaMath.ts";

const DAY = "2026-11-05", RISE = "2026-11-05T06:00:00";

test("12 and 24 hour text, with a day shift past midnight", () => {
  assert.equal(clockText("2026-11-05T06:39:52", DAY, RISE, "12"), "6:39 AM");
  assert.equal(clockText("2026-11-05T13:25:00", DAY, RISE, "12"), "1:25 PM");
  assert.equal(clockText("2026-11-05T00:05:00", DAY, RISE, "12"), "12:05 AM");
  assert.equal(clockText("2026-11-05T13:25:00", DAY, RISE, "24"), "13:25");
  assert.equal(clockText("2026-11-06T03:54:23", DAY, RISE, "24"), "03:54 +1");
  assert.equal(hourText(13.999999, 6, "24"), "14:00");
});

test("hours past midnight count on from the day", () => {
  assert.equal(hoursOn("2026-11-06T01:30:00", DAY), 25.5);
  assert.equal(hoursOn("2026-12-01T00:00:00", "2026-11-30"), 24);
});

test("vedic clock is ghati:pala since sunrise", () => {
  assert.equal(vedic("2026-11-05T06:24:00", RISE), "1:00");      // 24 minutes = 1 ghati
  assert.equal(vedic("2026-11-05T12:00:00", RISE), "15:00");     // 6 hours = 15 ghati
  assert.equal(vedic("2026-11-05T06:00:24", RISE), "0:01");      // 24 seconds = 1 pala
});

const F = { rise: 6, set: 17, next: 30.5 };

test("the dial: sunrise left, the middle of the day on top, the middle of the night at the bottom", () => {
  assert.equal(angleAt(6, F), 180);
  assert.equal(angleAt(11.5, F), 90);
  assert.equal(angleAt(17, F), 0);
  assert.equal(angleAt(23.75, F), -90);
  for (const h of [6.2, 9, 16.9, 17.1, 25, 30.4]) assert.ok(Math.abs(hourAt(angleAt(h, F), F) - h) < 1e-9, String(h));
});

test("a sector path is closed and takes the long arc only past 180 degrees", () => {
  assert.match(sector(0, 0, 1, 2, 180, 90), /^M.*A2 2 0 0 1 .*A1 1 0 0 0 .*Z$/);
  assert.match(sector(0, 0, 1, 2, 180, -10), /A2 2 0 1 1/);
});

const span = (name: string, from: number, to: number, good: boolean | null = null): Span => ({ name, from, to, good });
const LENS = [span("Shubha", 6, 7.5, true), span("Labha", 7.5, 9, true), span("Roga", 9, 10.5, false), span("Amrita", 10.5, 12, true)];
const AVOID = [span("Rahu Kalam", 7, 7.5), span("Ganda Moola", 6, 12)];
const GOOD = [span("Abhijit Muhurta", 11.2, 12)];

test("an avoid span wins over a good slot; an auspicious span lifts a good one", () => {
  assert.deepEqual(verdict(7.2, LENS, AVOID, GOOD), { tone: "avoid", because: ["Rahu Kalam"], until: 7.5 });
  assert.equal(verdict(9.5, LENS, AVOID, GOOD).tone, "avoid");
  assert.equal(verdict(8, LENS, AVOID, GOOD).tone, "good");          // Ganda Moola only calls for care
  assert.deepEqual(verdict(11.5, LENS, AVOID, GOOD), { tone: "excellent", because: ["Amrita", "Abhijit Muhurta"], until: null });
});

test("good windows cut out avoid spans, merge neighbours and keep only the long ones", () => {
  const w = goodWindows(LENS, AVOID, GOOD);
  assert.deepEqual(w.map((x) => [x.from, x.to, x.names, x.best]), [[6, 7, ["Shubha"], false], [7.5, 9, ["Labha"], false], [10.5, 12, ["Amrita"], true]]);
  assert.deepEqual(goodWindows(LENS, [span("Rahu Kalam", 6, 7.4)], []).map((x) => [x.from, x.to]), [[7.4, 9], [10.5, 12]]);
});

test("clock ticks: quarter hours, whole hours labelled; Vedic ghatis every fifth labelled", () => {
  const t = ticks({ rise: 6.5, set: 17.5, next: 30.5 }, "12");
  assert.equal(t[0].h, 6.5);
  assert.deepEqual(t.filter((x) => x.label).slice(0, 7).map((x) => x.label), ["7", "8", "9", "10", "11", "Noon", "1"]);
  assert.ok(t.some((x) => x.label === "Midnight"));
  assert.equal(ticks({ rise: 6.5, set: 17.5, next: 30.5 }, "24").find((x) => x.h === 24)!.label, "00");
  const g = ticks({ rise: 6, set: 18, next: 30 }, "vedic");
  assert.equal(g.length, 60);
  assert.deepEqual(g.filter((x) => x.label).map((x) => x.label).slice(0, 3), ["0", "5", "10"]);
});


test("a popup goes beside the segment, the way it faces, never on it", () => {
  const view = { x: 0, y: 0, w: 1000, h: 800 };
  const seg = { x: 600, y: 200, w: 80, h: 60 };
  assert.deepEqual(besidePlace(seg, [1, -0.2], 300, 150, view), { x: 692, y: 155 });          // faces right: to its right
  assert.deepEqual(besidePlace(seg, [0.1, -1], 300, 150, view), { x: 490, y: 38 });           // faces up: above it
  // no room on the right: the next choice, and never overlapping
  const edge = { x: 900, y: 300, w: 80, h: 60 };
  const p = besidePlace(edge, [1, 0], 300, 150, view);
  assert.ok(p.x + 300 <= edge.x || p.y + 150 <= edge.y || p.y >= edge.y + edge.h, JSON.stringify(p));
});

test("overlapping spans get their own lanes; spans end to end share one", () => {
  const rahu = span("Rahu Kalam", 13.42, 14.77), d1 = span("Dur Muhurta", 14.6, 15.32), d2 = span("Dur Muhurta", 15.32, 16.03);
  const l = lanes([d2, rahu, d1], 0, 10);
  const of = (s: Span) => l.find((x) => x.span === s)!;
  assert.deepEqual([of(rahu).r0, of(rahu).r1], [5, 10]);       // two lanes: Rahu outside
  assert.deepEqual([of(d1).r0, of(d1).r1], [0, 5]);            // the first Dur Muhurta inside it
  assert.deepEqual([of(d2).r0, of(d2).r1], [5, 10]);           // the second follows Rahu in the outer lane
  assert.equal(lanes([rahu], 0, 10)[0].r0, 0);                 // alone: the whole band
});

test("overlapping and back-to-back spans merge, keeping their parts", () => {
  const rahu = span("Rahu Kalam", 13.42, 14.77, false), d1 = span("Dur Muhurta", 14.6, 15.32, false), d2 = span("Dur Muhurta", 15.32, 16.03, false), y = span("Yamaganda", 6.6, 8, false);
  const m = mergeSpans([d2, y, rahu, d1]);
  assert.equal(m.length, 2);
  assert.deepEqual([m[1].from, m[1].to, m[1].name], [13.42, 16.03, "Rahu Kalam + Dur Muhurta"]);
  assert.deepEqual(m[1].parts, [rahu, d1, d2]);
  assert.deepEqual(m[0].parts, [y]);
});

