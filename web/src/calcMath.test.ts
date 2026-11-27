import assert from "node:assert/strict";
import { test } from "node:test";
import {
  antardasas, aprakasha, arcYears, arudha, ascendant, charaKarakas, clockHours, ghatis, gocara, gulikaPart, jaiminiClass,
  kpLords, nakshatraOf, navamsaSign, obliquity, panchanga, trikonaReduce, vimsottariBalance,
} from "./calcMath.ts";

// Mahatma Gandhi's chart as the engine gives it (Pushya-paksha): the numbers the tab works through.
const SUN = 168.0408277, MOON = 119.1474475, LAGNA = 187.5842504;
const near = (a: number, b: number, tol: number) => assert.ok(Math.abs(a - b) <= tol, `${a} vs ${b}`);

test("nakshatra, pada and the Vimśottarī balance", () => {
  assert.equal(nakshatraOf(214.28).name, "Anurādhā");
  assert.equal(nakshatraOf(0).pada, 1);
  const b = vimsottariBalance(MOON);
  assert.equal(b.name, "Āśleṣā");
  assert.equal(b.lord, "Mercury");
  near(b.left, 0.0639, 1e-4);            // core: Aasresha (6.39% left)
  near(b.balance, 1.0862, 2e-3);          // the engine's Mercury daśā ends 396.8 days after birth
  near(vimsottariBalance(0).balance, 7, 1e-9);
  near(vimsottariBalance(40 / 3 - 1e-9).balance, 0, 1e-6);
  assert.equal(antardasas("Venus")[0].months, 40);   // 20 × 20 ÷ 10
});

test("navāṃśa by element", () => {
  assert.equal(navamsaSign(0), 0);           // fire from Aries
  assert.equal(navamsaSign(30), 9);          // earth from Capricorn
  assert.equal(navamsaSign(64), 7);          // air from Libra, 2nd part
  assert.equal(navamsaSign(119.99), 11);     // water from Cancer, last part
  assert.equal(navamsaSign(LAGNA), 8);
});

test("pañcāṅga and its shares left", () => {
  const p = panchanga(SUN, MOON);
  assert.equal(p.tithiName, "Kṛṣṇa Ekādaśī");
  near(p.tithiLeft, 0.0744, 1e-4);
  assert.equal(p.yogaName, "Sādhya");
  near(p.yogaLeft, 0.4609, 1e-4);
  assert.equal(p.karanaName, "Bālava");
  near(p.karanaLeft, 0.1489, 1e-4);
});

test("shadow points from the Sun", () => {
  const a = aprakasha(SUN);
  near(a.Dhooma, 301.3742, 1e-3);
  near(a.Vyatipata, 58.6258, 1e-3);
  near(a.Upaketu, SUN - 30, 1e-9);
});

test("eight chara kārakas", () => {
  const k = charaKarakas({ Sun: SUN, Moon: MOON, Mars: 207.5146, Mercury: 192.8785, Jupiter: 29.2733, Venus: 205.5505, Saturn: 231.4694, Rahu: 103.2837 });
  assert.deepEqual(k.map((x) => x.planet), ["Jupiter", "Moon", "Mars", "Venus", "Saturn", "Sun", "Rahu", "Mercury"]);
});

test("ārūḍha and its two exceptions", () => {
  assert.equal(arudha(6, 6).pada, 3);       // lord in the house: 10th from it (Gandhi's AL, Cancer)
  assert.equal(arudha(0, 6).pada, 9);       // lord in the 7th: pada in the house, so the 10th
  assert.equal(arudha(0, 3).pada, 3);       // lord in the 4th: pada in the 7th, so the 4th
  assert.equal(arudha(0, 2).pada, 4);       // 3rd from Aries, 3rd again: Leo
});

test("KP lords", () => {
  assert.deepEqual(kpLords(LAGNA).lords, ["Rahu", "Rahu", "Mercury"]);
  assert.deepEqual(kpLords(SUN).lords, ["Moon", "Mercury", "Mercury"]);
  assert.deepEqual(kpLords(MOON).lords, ["Mercury", "Saturn", "Moon"]);
});

test("trikoṇa reduction", () => {
  assert.deepEqual(trikonaReduce([3, 4, 3, 5, 6, 3, 4, 4, 6, 4, 4, 3]), [0, 1, 0, 2, 3, 0, 1, 1, 3, 1, 1, 0]);
  assert.deepEqual(trikonaReduce([0, 2, 2, 2, 5, 2, 2, 2, 3, 2, 2, 2]).slice(0, 4), [0, 0, 0, 0]);
});

test("piṇḍāyu years by arc", () => {
  near(arcYears("Sun", 10).years, 19, 1e-9);           // deep exaltation: full
  near(arcYears("Sun", 190).years, 9.5, 1e-9);         // deep debility: half
  near(arcYears("Sun", SUN).years, 10.66, 5e-3);       // the Longevity tab's "By arc"
  near(arcYears("Saturn", 231.4694).years, 18.25, 5e-3);
});

test("Jaimini pairs", () => {
  assert.equal(jaiminiClass(6, 6), "long");      // Libra, Libra
  assert.equal(jaiminiClass(7, 3), "medium");    // Scorpio, Cancer
  assert.equal(jaiminiClass(1, 7), "short");     // two fixed
  assert.equal(jaiminiClass(2, 5), "medium");    // two dual
});

test("time of day", () => {
  near(clockHours("5:55:02 AM")!, 5.91722, 1e-4);
  near(clockHours("5:43:22 PM (Oct 1)")!, 17.7228, 1e-4);
  near(ghatis(7 + 20 / 60, clockHours("5:55:02 AM")!), 3.5405, 1e-3);
  assert.equal(gulikaPart(6, false), 1);   // Saturday by day: Saturn's own part first
  assert.equal(gulikaPart(0, false), 7);   // Sunday by day: the seventh
  assert.equal(gulikaPart(0, true), 3);    // Sunday night starts from Jupiter
});

test("ascendant from sidereal time", () => {
  const asc = ascendant(8 + 3 / 60 + 26 / 3600, 21 + 37 / 60, obliquity(1869.75));
  near(asc.lon - (20 + 54 / 60 + 5.56 / 3600), LAGNA, 0.05);
});

test("gocara and vedha", () => {
  const g = gocara("Sun", 0, { Sun: 2, Moon: 8, Saturn: 8 });
  assert.equal(g.house, 3);
  assert.deepEqual(g.blockers, ["Moon"]);   // Saturn in the 9th does not block the Sun
});
