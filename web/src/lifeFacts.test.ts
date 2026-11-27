import assert from "node:assert/strict";
import { test } from "node:test";
import { answerText, chartKey, SECTIONS, visible } from "./lifeFacts.ts";

test("chartKey keeps the name and birth date, not the time", () => {
  assert.equal(chartKey("Asha", { year: 1990, month: 3, day: 2 }), "Asha|1990-03-02");
  assert.equal(chartKey("", { year: 2001, month: 11, day: 25 }), "(untitled)|2001-11-25");
});

test("a year is asked only once its answer calls for it", () => {
  const ids = (a: Record<string, string | number>) => visible(SECTIONS, a).map((q) => q.id);
  assert.ok(!ids({}).includes("father.year"));
  assert.ok(!ids({ father: "Alive" }).includes("father.year"));
  assert.ok(ids({ father: "Passed" }).includes("father.year"));
  assert.ok(!ids({ sons: 0, daughters: 0 }).includes("children.year"));
  assert.ok(ids({ sons: 0, daughters: 1 }).includes("children.year"));
});

test("an answer reads as words, with the text typed for Other", () => {
  const a = { gender: "Other", "gender.other": "Non-binary", father: "Passed", "father.year": 1884, "father.year.approx": true, youngerBrothers: "Other", "youngerBrothers.other": "5", "education.field": "Other" };
  const got = visible(SECTIONS, a).map((q) => answerText(q, a)).filter((t) => t !== undefined);
  assert.deepEqual(got, ["Non-binary", "Passed", "≈ 1884", "5", "Other"]);
});
