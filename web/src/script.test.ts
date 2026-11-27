import assert from "node:assert/strict";
import { test } from "node:test";
import { toDevanagari, transliterate } from "./script.ts";

test("IAST to Devanāgarī: conjuncts, final virama, daṇḍas, avagraha, compounds", () => {
  assert.equal(toDevanagari("na māṃ karmāṇi limpanti |"), "न मां कर्माणि लिम्पन्ति ।");
  assert.equal(toDevanagari("karma-phale spṛhā ||"), "कर्मफले स्पृहा ॥");
  assert.equal(toDevanagari("yo 'bhijānāti"), "योऽभिजानाति");
  assert.equal(toDevanagari("mām upetya"), "मामुपेत्य");               // a final consonant joins the next word
  assert.equal(toDevanagari("vidham |"), "विधम् ।");
  assert.equal(toDevanagari("oṃ hrāṃ hrīṃ hrauṃ saḥ sūryāya namaḥ"), "ॐ ह्रां ह्रीं ह्रौं सः सूर्याय नमः");
  assert.equal(transliterate("oṃ namaḥ", "telugu"), "ఓం నమః");          // no ॐ sign in Telugu
  assert.equal(toDevanagari("jñānāgniḥ sarva-karmāṇi"), "ज्ञानाग्निः सर्वकर्माणि");
  assert.equal(toDevanagari("kṛṣṇa caitanya"), "कृष्ण चैतन्य");
});

test("other scripts by offset, with their fix-ups", () => {
  assert.equal(transliterate("rāma", "telugu"), "రామ");
  assert.equal(transliterate("kṛṣṇa", "kannada"), "ಕೃಷ್ಣ");
  assert.equal(transliterate("viṣṇu", "bengali"), "বিষ্ণু");         // Bengali writes va as ba
  assert.equal(transliterate("bhagavān", "tamil"), "ப⁴க³வாந்");      // superscripts after the vowel sign
  assert.equal(transliterate("kṛṣṇa", "tamil"), "க்ருஷ்ண");
  assert.equal(transliterate("dharma |", "malayalam"), "ധര്മ ।");
});

test("Roman, and romanised Tamil, stay as written", () => {
  assert.equal(transliterate("na māṃ", "iast"), "na māṃ");
  assert.equal(transliterate("ciṟṟañ ciṟu kāle", "deva"), "ciṟṟañ ciṟu kāle");
});
