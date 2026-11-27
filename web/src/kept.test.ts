import assert from "node:assert/strict";
import { test } from "node:test";
import { plan } from "./kept.ts";

test("the first sign-in sends up what only this browser has", () => {
  assert.deepEqual(plan({ theme: "dark", "chart.v2": "{}" }, {}, null, "1"), { clear: false, set: {}, upload: { theme: "dark", "chart.v2": "{}" } });
});

test("the account's values win, and keys only here go up", () => {
  const p = plan({ theme: "dark", "kept.owner": "1", "view.x": "a", same: "s" }, { theme: "light", same: "s" }, "1", "1");
  assert.deepEqual(p, { clear: false, set: { theme: "light" }, upload: { "view.x": "a" } });
});

test("a browser that was another account's is wiped, and nothing of it goes up", () => {
  const p = plan({ "chart.v2": "theirs", "kept.owner": "2" }, { theme: "light" }, "2", "1");
  assert.deepEqual(p, { clear: true, set: { theme: "light" }, upload: {} });
});
