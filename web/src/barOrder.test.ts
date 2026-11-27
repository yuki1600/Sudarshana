import assert from "node:assert/strict";
import { test } from "node:test";
import { moveTo, reconcile } from "./barOrder.ts";

const def = { left: ["new", "open", "chart"], right: ["Home", "Tajaka", "Dasas", "settings"] };

test("no saved order is the default", () => assert.deepEqual(reconcile(null, def), def));

test("a saved order drops ids the bar lost and slots new ones after their default neighbour", () => {
  const saved = { left: ["open", "settings", "new", "chart", "Gone"], right: ["Dasas", "Home"] };
  assert.deepEqual(reconcile(saved, def), { left: ["open", "settings", "new", "chart"], right: ["Dasas", "Home", "Tajaka"] });
});

test("moveTo crosses halves and reorders within one", () => {
  assert.deepEqual(moveTo(def, "open", "right", "Dasas"), { left: ["new", "chart"], right: ["Home", "Tajaka", "open", "Dasas", "settings"] });
  assert.deepEqual(moveTo(def, "new", "left", null), { left: ["open", "chart", "new"], right: def.right });
});
