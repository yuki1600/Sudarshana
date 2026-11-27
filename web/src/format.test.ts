import assert from "node:assert/strict";
import { test } from "node:test";
import { brief, formatDuration, formatLon, formatMoment, fromDms, joinHours, nameAndGloss, splitHours, timeLeft, toDms } from "./format.ts";

test("formatLon writes degrees, sign, minutes and seconds", () => {
  assert.equal(formatLon(266.000418711547), "26 Sg 00' 01.51\"");   // Swami Vivekananda's lagna
  assert.equal(formatLon(6.340444), " 6 Ar 20' 25.60\"");
  assert.equal(formatLon(359.99999999), " 0 Ar 00' 00.00\"");        // rounds up across the 360 boundary
  assert.equal(formatLon(-0.5), "29 Pi 30' 00.00\"");
});

test("hours split and join", () => {
  assert.deepEqual(splitHours(6.55), [6, 33, 0]);
  assert.ok(Math.abs(joinHours(...splitHours(17.506667)) - 17.506667) < 1e-3);
});

test("geographic degrees round-trip through DMS", () => {
  assert.deepEqual(toDms(13.083333), { deg: 13, min: 5, sec: 0, hemi: 1 });
  assert.deepEqual(toDms(-74.006), { deg: 74, min: 0, sec: 22, hemi: -1 });
  assert.ok(Math.abs(fromDms(toDms(80.283333)) - 80.283333) < 1e-4);
  assert.equal(fromDms({ deg: 12, min: 17, sec: 45, hemi: 1 }), 12 + 17 / 60 + 45 / 3600);
});

test("dates read in 12-hour form", () => {
  assert.equal(formatMoment("1857-06-09T10:12:16.196516"), "1857-06-09 (10:12:16 AM)");
  assert.equal(formatMoment("1867-06-09T09:05:59.999"), "1867-06-09 (9:05:59 AM)");
  assert.equal(formatMoment("1867-06-09T21:05:01"), "1867-06-09 (9:05:01 PM)");
});

test("a period's length reads in years, months and days", () => {
  const years = (y: number) => formatDuration({ years: y, start: "2000-01-01T00:00:00", end: "2001-01-01T00:00:00" });
  assert.equal(years(0.3), "3mo 18d");         // the Sun's antardasa of its own mahadasa, in every Vimsottari table
  assert.equal(years(0.35), "4mo 6d");
  assert.equal(years(10), "10y");
  assert.equal(years(3 + 1 / 3), "3y 4mo");
  assert.equal(years(0.015), "5d");            // 5.4 days
  assert.equal(years(0.99999), "1y");          // rounding carries, never 11mo 30d
});

test("under a day, and in a chart fitted to its span, the dates give the length", () => {
  const dates = (start: string, end: string, fitted = false) => formatDuration({ years: 10, start, end }, fitted);
  assert.equal(dates("2000-01-01T00:00:00.5", "2000-01-01T06:31:12.9"), "6h 31min 12s");
  assert.equal(dates("2000-01-01T23:59:30", "2000-01-02T00:00:29"), "59s");
  assert.equal(dates("2000-01-01T00:00:00", "2000-01-01T00:00:00"), "0d");    // Padanaathaamsa's empty signs
  assert.equal(dates("2000-01-01T00:00:00", "2000-01-31T10:00:00", true), "1mo");   // 10 nominal years, a month on the calendar
  assert.equal(dates("1890-01-01T00:00:00", "1891-01-01T06:00:00", true), "1y");
});

test("timeLeft says what is left of a period", () => {
  const day = 86400000;
  assert.equal(timeLeft(9 * day), "9d");
  assert.equal(timeLeft(130 * day), "4m 8d");
  assert.equal(timeLeft(3 * 365.25 * day + 61 * day), "3y 2m");
  assert.equal(timeLeft(-5), "0d");
});

test("a long passage is cut to its first sentence", () => {
  const rohini = "'Rohini' is the wife of Moon who is said to have been fond of fine dress. This is Star of Abundance and Prosperity.";
  assert.equal(brief(rohini), "'Rohini' is the wife of Moon who is said to have been fond of fine dress.");
  assert.equal(brief(rohini, 2), rohini);                          // nothing cut: the text itself
  assert.equal(brief("Muhurta Chintamani (2.15) lists them. Then more."), "Muhurta Chintamani (2.15) lists them.");   // 2.15 is no sentence end
  const long = "word ".repeat(80).trim();
  assert.ok(brief(long).endsWith("…") && brief(long).length <= 221);
});

test("a value's name comes apart from its gloss", () => {
  assert.deepEqual(nameAndGloss("Moksha (Spiritual Liberation/ Emancipation)"), ["Moksha", "Spiritual Liberation / Emancipation"]);
  assert.deepEqual(nameAndGloss("Rohana Shakti (The Power to “Make things Grow”)"), ["Rohana Shakti", "The Power to “Make things Grow”"]);
  assert.deepEqual(nameAndGloss("White"), ["White", ""]);
});
