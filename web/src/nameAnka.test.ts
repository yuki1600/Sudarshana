import assert from "node:assert/strict";
import { test } from "node:test";
import { nameAnka } from "./nameAnka.ts";

test("nameAnka reads the first syllable's number (BPHS 45)", () => {
  assert.deepEqual(nameAnka("Krishna"), { syllable: "k", n: 1 });
  assert.equal(nameAnka("Kharavela")?.n, 2);
  assert.equal(nameAnka("Shiva")?.n, 2);        // sha, not sa
  assert.equal(nameAnka("Sita")?.n, 4);
  assert.equal(nameAnka("Chandra")?.n, 1);      // cha, not ka
  assert.equal(nameAnka("Bharat")?.n, 1);       // bha, not ba
  assert.equal(nameAnka("Balaji")?.n, 5);
  assert.equal(nameAnka("Ishaan")?.n, 2);
  assert.equal(nameAnka("Aarav")?.n, 1);
  assert.equal(nameAnka("Omkar")?.n, 5);
  assert.equal(nameAnka("Lakshmi")?.n, 5);
  assert.equal(nameAnka("  ravi")?.n, 4);
  assert.equal(nameAnka("Ravi")?.syllable, "ra");
  assert.equal(nameAnka("123"), null);
  assert.equal(nameAnka(""), null);
});
