import assert from "node:assert/strict";
import { test } from "node:test";
import { pack, rowsOf, SBC, vedhaLines } from "./wheelGeometry.ts";

test("rowsOf puts natal names before transit ones, per to a row", () => {
  assert.deepEqual(rowsOf(["Su", "Mo", "Ma"], ["Ju"], 2), [["Su Mo", false], ["Ma", false], ["Ju", true]]);
  assert.deepEqual(rowsOf(["Su", "Mo"], undefined, Infinity), [["Su Mo", false]]);
});

test("pack picks the rows that let the names run largest", () => {
  const box = (w: number, h: number) => (a: number, b: number) => Math.min(w / a, h / b);
  assert.equal(pack(["Su", "Mo", "Ma"], [], box(66, 39), 24).rows.length, 2);   // a Shoola slot: two rows beat one cramped row
  assert.equal(pack(["Su", "Mo", "Ma"], [], box(30, 100), 24).rows.length, 3);  // tall and narrow: one to a row
  assert.equal(pack(["Su"], [], box(200, 200), 24).size, 24);                       // never past the largest
  assert.deepEqual(pack(["Su", "Mo"], [], box(200, 200), 24).rows, [["Su Mo", false]]);   // room to spare: fewest rows
  assert.deepEqual(pack([], undefined, box(66, 39), 24).rows, []);
});

test("vedhaLines: Krittika's front vedha reaches Shravana, its right Bharani, its left Vishakha; a retrograde graha's right falls the way it moves", () => {
  const box = (star: string) => { for (let r = 0; r < 9; r++) for (let c = 0; c < 9; c++) if (SBC[r][c] === `*${star}`) return `${r}-${c}`; throw new Error(star); };
  const of = (star: string) => { const [r, c] = box(star).split("-").map(Number); return vedhaLines(r, c)!; };
  const k = of("Krit");
  assert.ok(k.front.has(box("Srav")) && k.right.has(box("Bhar")) && k.left.has(box("Visa")));
  // Ketu in Magha, going back to Ashlesha: its right (its main vedha, retrograde) is the diagonal onto Ashlesha
  assert.ok(of("Magh").right.has(box("Asre")));
  // each line runs from side to side: Vishakha's right reaches Krittika again, Shravana's front Krittika
  assert.ok(of("Visa").right.has(box("Krit")) && of("Srav").front.has(box("Krit")));
  assert.equal(vedhaLines(0, 0), null);     // a corner is a vowel, not a star
  assert.equal(vedhaLines(4, 4), null);
});
