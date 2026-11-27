import assert from "node:assert/strict";
import { test } from "node:test";
import { bhavaOfBox, bodySizes, degText, fitted, fittedEach, flow } from "./chartGeometry.ts";

test("a bhava box lists a graha from the next sign after its own sign's grahas, one from the sign before first", () => {
  const deg = { Ju: 20, Ke: 25, Ma: 32.2, Sa: -2 };     // Ma in the next sign at 2°12', Sa in the sign before at 28°
  assert.deepEqual(flow(["Ma", "Ju", "Ke", "Sa"], 200, bodySizes(300), deg).map((r) => r.t), ["Sa", "Ju", "Ke", "Ma"]);
  assert.deepEqual([degText(32.2), degText(-2), degText(12.1)], ["2°12'", "28°00'", "12°06'"]);
});

test("text sizes are fixed in chart units so they stay proportional to the frame", () => {
  assert.equal(bodySizes(100).major, bodySizes(504).major);   // same chart units at every screen width
  assert.equal(bodySizes(100).major, 20);
  assert.equal(bodySizes(504, 1.5).major, 30);                 // the Charts font size goes on top
  assert.equal(bodySizes(207, 1.5).sign, bodySizes(207).sign * 1.5);
  // on screen, larger charts read larger — not locked to a constant pixel size
  const onScreen = (px: number) => bodySizes(px).major * px / 400;
  assert.ok(onScreen(400) > onScreen(200));
});

test("bodies flow without touching, planets first, wrapping at the box's edge", () => {
  for (const px of [207, 287, 504]) {
    const z = bodySizes(px);
    const all = flow(["HL", "Su", "AmK", "Mo", "MaR", "Me", "Ju", "Ve", "SaR", "Ra", "Ke"], 100, z);
    assert.equal(all[0].t, "Su");
    assert.equal(all[all.length - 1].t, "HL");
    for (let i = 1; i < all.length; i++) {
      const [a, b] = [all[i - 1], all[i]];
      assert.ok(b.y > a.y || b.x > a.x + z.major * 0.9, `${a.t} and ${b.t} at ${px}px`);
      assert.ok(b.x === 8 || b.y === a.y);           // a new row starts at the left
    }
  }
});

test("a body wider than the box still gets a row of its own", () => {
  const rows = flow(["AmK", "AmK"], 30, bodySizes(207));
  assert.deepEqual(rows.map((r) => r.x), [8, 8]);
  assert.ok(rows[1].y > rows[0].y);
});

test("a chart shrinks only as far as its most crowded box needs, and no further than its first size", () => {
  const z = bodySizes(207);
  const planets = ["As", "Su", "Mo", "Ma", "Me", "Ju", "Ve", "Sa", "Ra", "Ke"];
  assert.equal(fitted(z, [{ labels: ["Su"], w: 100, h: 176 }]).major, z.major);      // room to spare: untouched
  const crowded = fitted(z, [{ labels: planets, w: 100, h: 100 }]);
  assert.ok(crowded.major < z.major && crowded.major >= 17);
  const last = flow(planets, 100, crowded).at(-1)!;
  assert.ok(last.y + crowded.major * 0.25 <= 100);
  assert.equal(fitted(z, [{ labels: planets, w: 100, h: 40 }]).major, 17);           // hopeless: the first size, not smaller
  const big = bodySizes(207, 1.5);
  assert.equal(fitted(big, [{ labels: planets, w: 100, h: 40 }], 1.5).major, 25.5);  // floor goes up with the Charts font size
  const strips = ["A1", "A2", "A3", "A4", "A5", "A6"];                               // a strip along the bottom takes room from the flow
  assert.ok(fitted(z, [{ labels: [...strips, "Su", "Mo", "Ma", "Me"], w: 100, h: 90, stripAlong: true }]).major < z.major);
  assert.equal(fitted(z, [{ labels: [...strips, "Su"], w: 100, h: 176, stripAlong: true }]).major, z.major);
});

test("with degrees: grahas down the left by degree, the rest down the right, and a crowded chart shrinks until both columns fit", () => {
  const deg = { Su: 12.9, Me: 0.5, Ve: 8.2 };
  const rows = flow(["HL", "Su", "A10", "Me", "Ve", "Md"], 100, bodySizes(207), deg, true);
  assert.deepEqual(rows.filter((r) => !r.end).map((r) => r.t), ["Me", "Ve", "Su"]);
  const up = flow(["HL", "Su", "A10", "Me", "Ve", "Md"], 100, bodySizes(207), deg, true, undefined, true);     // Sagittarius .. Pisces: lowest at the bottom
  assert.deepEqual(up.filter((r) => !r.end).map((r) => r.t), ["Su", "Ve", "Me"]);
  assert.deepEqual(rows.filter((r) => r.end).map((r) => r.t), ["HL", "A10", "Md"]);
  const z = bodySizes(207);
  assert.ok(fitted(z, [{ labels: ["Su", "Me", "A10"], w: 100, h: 140, deg, beside: true }]).major < z.major);
});

test("Starlight: each box sized for its own bodies, the other points along its bottom right with a gap", () => {
  const deg = { Su: 12.9, Me: 0.5, Ve: 8.2, Ju: 20, Ma: 3, Sa: 1 };
  const z = bodySizes(300);
  const quiet = { labels: ["Su"], w: 100, h: 100, deg, beside: true, low: true };
  const busy = { labels: ["Su", "Me", "Ve", "Ju", "Ma", "Sa", "HL", "GL"], w: 100, h: 100, deg, beside: true, low: true };
  const [a, b] = fittedEach(z, [quiet, busy]);
  assert.ok(a.major > b.major);                                   // the crowded box shrinks alone
  const four = { labels: ["Su", "Me", "Ve", "Ju", "HL", "GL"], w: 80, h: 100, deg, beside: true };
  assert.ok(fittedEach(z, [{ ...four, low: true }])[0].major > fitted(z, [four]).major);   // points out of the top corner leave the grahas more room
  const rows = flow(["HL", "Su", "GL"], 100, z, deg, true, 100);
  const [hl, gl] = rows.filter((r) => r.end);
  assert.deepEqual([hl.t, gl.t, hl.y, gl.y, gl.x], ["HL", "GL", 94, 94, 96]);   // one row on the bottom, in order, flush right
  assert.ok(gl.x - hl.x >= z.minor * 1.3 + z.minor * 0.7);                     // with a gap between
});

test("a bhava box with a long row shrinks all its grahas together, not that row alone", () => {
  const z = bodySizes(400), deg = { Su: 12.1, Mo: 3.5, Sa: 20.2 };
  const box = { labels: ["Su", "Mo", "SaR"], w: 100, h: 200, deg, beside: true, low: true };
  const [plain, moved] = fittedEach(z, [box, { ...box, moved: { Sa: "Ar" } }]);
  assert.ok(moved.major < plain.major);
});

test("Starlight: a box of one graha is no larger than one of three; a crowded one still shrinks", () => {
  const deg = { Su: 12.9, Me: 0.5, Ve: 8.2, Ju: 20, Ma: 3, Sa: 1 };
  const b = (labels: string[]) => ({ labels, w: 100, h: 100, deg, beside: true, low: true });
  const [one, three, six] = fittedEach(bodySizes(300), [b(["Su"]), b(["Su", "Me", "Ve", "HL"]), b(["Su", "Me", "Ve", "Ju", "Ma", "Sa", "HL"])]);
  assert.equal(one.major, three.major);
  assert.ok(six.major < three.major);
});

test("Starlight: a box's grahas sit midway between the sign's name and its bottom, or the points along it", () => {
  const z = bodySizes(300), deg = { Su: 12.9 };
  const [su] = flow(["Su"], 100, z, deg, true, 100);
  const below = su.y - z.major * 0.25 - (z.sign + 3 + 96) / 2;
  assert.ok(below > 0 && below < z.major * 0.1);                                 // the letters' middle just under the box's: a little more room on top
  const [withPoint] = flow(["Su", "HL"], 100, z, deg, true, 100);
  assert.ok(withPoint.y < su.y);                                                 // a row of points below lifts it
});

test("flow: with the sign's name, the first row rises beside it and stops short of it", () => {
  const z = bodySizes(0);
  const top = flow(["Su", "Mo", "Ma", "Ju", "Sa"], 100, z, undefined, false, undefined, false, "Ar");
  const old = flow(["Su", "Mo", "Ma", "Ju", "Sa"], 100, z);
  assert.ok(top[0].y < old[0].y);
  const nameLeft = 100 - 4 - 1.22 * z.sign;     // "Ar" is 1.22 em, as is each two-letter graha
  const first = top.filter((p) => p.y === top[0].y);
  assert.deepEqual(first.map((p) => p.t), ["Su", "Mo"]);
  for (const p of first) assert.ok(p.x + 1.22 * z.major < nameLeft);
});

test("a bhava chart's box is the bhava counted from the reference's box, backward for the nodes when reversed", () => {
  assert.deepEqual([bhavaOfBox(4, 4), bhavaOfBox(8, 4), bhavaOfBox(3, 4), bhavaOfBox(0, 11)], [1, 5, 12, 2]);     // the 1st in its own box; on round the zodiac
  assert.deepEqual([bhavaOfBox(3, 4, true), bhavaOfBox(5, 4, true)], [2, 12]);                                   // from a node, counted back
});
