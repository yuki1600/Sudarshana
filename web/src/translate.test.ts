import assert from "node:assert/strict";
import { test } from "node:test";
import { fromDevanagari, languageOf, translate } from "./translate.ts";
import { wordsFor } from "./languageWords.ts";
import { shown, signName } from "./names.ts";

const hi = wordsFor("hi"), ta = wordsFor("ta"), te = wordsFor("te"), kn = wordsFor("kn"), bn = wordsFor("bn"), gu = wordsFor("gu"), mr = wordsFor("mr"), pa = wordsFor("pa");

test("names, by every spelling the server and the client use", () => {
  assert.equal(translate(hi, "Sun"), "सूर्य");
  assert.equal(translate(hi, "Aswini"), "अश्विनी");
  assert.equal(translate(hi, "Ashwini"), "अश्विनी");
  assert.equal(translate(hi, "Aswi"), "अश्विनी");
  assert.equal(translate(ta, "Sagittarius"), "தனுசு");
  assert.equal(translate(te, "Sg"), "ధనుస్సు");
  assert.equal(translate(hi, "SaR"), "श(व)");          // a retrograde graha: vakri
  assert.equal(translate(hi, "  Lagna "), "  लग्न ");    // the spaces round it stay
});

test("an abbreviation is matched only as written; a word only whole", () => {
  assert.equal(translate(hi, "As"), "ल");
  assert.equal(translate(hi, "as"), "as");
  assert.equal(translate(hi, "Sundays"), "Sundays");
  assert.equal(translate(hi, "Sunday"), "रविवार");
});

test("the server's Core Info lines, word by word", () => {
  assert.equal(translate(hi, "Krishna Sapthami (Sa) (49.89% left)"), "कृष्ण सप्तमी (श) (49.89% शेष)");
  assert.equal(translate(gu, "Sukla Panchami (Ve) (10.00% left)"), "સુદ પાંચમ (શુ) (10.00% બાકી)");
  assert.equal(translate(hi, "Mercury (5 min sign: Pi)"), "बुध (5 मिनट राशि: मीन)");
  assert.equal(translate(hi, "5:54:00 (East of GMT)"), "5:54:00 (GMT से पूर्व)");
  assert.equal(translate(hi, "26 Sg 00' 01.51\""), "26 धनु 00' 01.51\"");
  assert.equal(translate(hi, "269.443 deg"), "269.443°");
  assert.equal(translate(hi, "12th January 1863"), "12 जनवरी 1863");     // an ordinal's ending goes
  assert.equal(translate(hi, "6:33:00 AM"), "6:33:00 AM");                // nothing to put into Hindi
});

test("the lunar year's month is a month, though a nakshatra has its name", () => {
  assert.equal(translate(hi, "Dundubhi - Pushya"), "दुन्दुभि - पौष");
  assert.equal(translate(hi, "Pushya"), "पुष्य");
  assert.equal(translate(ta, "Prabhava - Adhika Magha"), "ப்ரபவ - அதிக மாசி");
});

test("in, from and and go where each language puts them", () => {
  assert.equal(translate(hi, "Sun in Aries"), "सूर्य मेष में");
  assert.equal(translate(ta, "Sun in Aries"), "சூரியன் மேஷத்தில்");
  assert.equal(translate(te, "Ke in Sg (1°27′)"), "కే ధనుస్సులో (1°27′)");
  assert.equal(translate(kn, "Sun in Aries"), "ಸೂರ್ಯ ಮೇಷದಲ್ಲಿ");
  assert.equal(translate(bn, "Sun in Aries"), "সূর্য মেষে");
  assert.equal(translate(mr, "Sun in Aries"), "सूर्य मेषात");
  assert.equal(translate(hi, "2nd from Lagna"), "लग्न से 2");
  assert.equal(translate(hi, "Taras from Moon and Lagna"), "चन्द्र और लग्न से तारा");
  assert.equal(translate(hi, "7th in Darker half"), "7 कृष्ण पक्ष में");
  assert.equal(translate(hi, "in the 16 vargas"), "16 वर्ग में");
});

test("a label's verb last; Tamil and Telugu compounds", () => {
  assert.equal(translate(hi, "Save chart"), "कुंडली सहेजें");
  assert.equal(translate(hi, "Show navamsa (D-9)"), "नवांश (D-9) दिखाएँ");
  assert.equal(translate(hi, "placed in 1st bhava"), "1 भाव में स्थित");
  assert.equal(translate(ta, "Nakshatra dasas"), "நட்சத்திர தசை");
  assert.equal(translate(te, "Graha special lagna"), "గ్రహ ప్రత్యేక లగ్నం");
});

test("a sentence the tables don't have stays English as a whole", () => {
  const s = "A graha in its sign of exaltation is at its strongest.";
  assert.equal(translate(hi, s), s);
  assert.equal(translate(hi, "Natal chart (back to the saved time)"), "Natal chart (back to the saved time)");
});

test("the Sanskrit names given in Hindi alone, in each script", () => {
  assert.equal(fromDevanagari("नवांश", "te"), "నవాంశ");
  assert.equal(fromDevanagari("कुम्भ", "kn"), "ಕುಂಭ");
  assert.equal(fromDevanagari("कुंभ", "bn"), "কুম্ভ");
  assert.equal(fromDevanagari("स्वस्थ", "or"), "ସ୍ୱସ୍ଥ");
  assert.equal(fromDevanagari("गर्वित", "or"), "ଗର୍ବିତ");
  assert.equal(fromDevanagari("राशि", "as"), "ৰাশি");
  assert.equal(fromDevanagari("नवांश", "pa"), "ਨਵਾਂਸ਼");
  assert.equal(fromDevanagari("कृत्तिका", "pa"), "ਕ੍ਰਿੱਤਿਕਾ");
  assert.equal(fromDevanagari("योगिनी", "kn"), "ಯೋಗಿನಿ");
  assert.equal(fromDevanagari("चन्द्र", "ta"), "சந்த்ர");
  assert.equal(translate(pa, "Swastha (comfortable)"), "ਸਵਸਥ");
});

test("the charts' labels in the language, English and Sanskrit as before", () => {
  const d = (language: string, planets: "english" | "sanskrit" = "english") => ({ language, planets, signs: planets }) as Parameters<typeof shown>[1];
  assert.equal(shown("Su", d("Hindi")), "सू");
  assert.equal(shown("SaR", d("Tamil")), "சனி(வ)");
  assert.equal(shown("Md", d("Kannada")), "ಮಾಂ");
  assert.equal(shown("HL", d("Hindi")), "HL");           // the other points stay Latin
  assert.equal(shown("SaR", d("English")), "Sa(R)");
  assert.equal(shown("Su", d("English", "sanskrit")), "Sy");
  assert.equal(signName(8, "Sg", d("Telugu")), "ధనుస్సు");
  assert.equal(signName(8, "Sg", d("English")), "Sg");
  assert.equal(shown("Mo", d("Oriya")), "ଚ");            // the older name for Odia still opens in Odia
  assert.equal(languageOf("Malayalam"), "English");      // no longer offered
});

test("a person's or a place's name is not half translated", () => {
  assert.equal(translate(hi, "Ravi Kumar"), "Ravi Kumar");
  assert.equal(translate(hi, "Rohini Sharma"), "Rohini Sharma");
  assert.equal(translate(hi, "Krishna, Andhra Pradesh, India"), "Krishna, Andhra Pradesh, India");
  assert.equal(translate(hi, "The 64th navamsa"), "64 नवांश");
  assert.equal(translate(hi, "Chara (K.N. Rao)"), "चर (K.N. Rao)");
});

test("A of B, the whole label: B's A, as these languages say it", () => {
  assert.equal(translate(hi, "Kind of yoga"), "योग का प्रकार");
  assert.equal(translate(ta, "Kind of yoga"), "யோகத்தின் வகை");
  assert.equal(translate(kn, "Lord of Aquarius"), "ಕುಂಭದ ಅಧಿಪತಿ");
  assert.equal(translate(hi, "Arudha of Sun"), "सूर्य का आरूढ");
  assert.equal(translate(hi, "Lords of the 64th navamsa and 22nd drekkana"), "64 नवांश और 22 द्रेष्काण का स्वामी");
});
