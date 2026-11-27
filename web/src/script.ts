/** IAST Sanskrit shown in the reader's script: Devanāgarī first, then the other Brahmic scripts,
 *  which share Devanāgarī's Unicode layout at a fixed offset. */

const VOWELS: Record<string, [string, string]> = { // [independent letter, sign after a consonant]
  a: ["अ", ""], "ā": ["आ", "ा"], i: ["इ", "ि"], "ī": ["ई", "ी"], u: ["उ", "ु"], "ū": ["ऊ", "ू"],
  "ṛ": ["ऋ", "ृ"], "ṝ": ["ॠ", "ॄ"], e: ["ए", "े"], ai: ["ऐ", "ै"], o: ["ओ", "ो"], au: ["औ", "ौ"],
};
const CONSONANTS: Record<string, string> = {
  k: "क", kh: "ख", g: "ग", gh: "घ", "ṅ": "ङ", c: "च", ch: "छ", j: "ज", jh: "झ", "ñ": "ञ",
  "ṭ": "ट", "ṭh": "ठ", "ḍ": "ड", "ḍh": "ढ", "ṇ": "ण", t: "त", th: "थ", d: "द", dh: "ध", n: "न",
  p: "प", ph: "फ", b: "ब", bh: "भ", m: "म", y: "य", r: "र", l: "ल", "ḷ": "ळ", v: "व",
  "ś": "श", "ṣ": "ष", s: "स", h: "ह",
};
const MARKS: Record<string, string> = { "ṃ": "ं", "ṁ": "ं", "ḥ": "ः", "'": "ऽ", "||": "॥", "|": "।" };
const TOKENS = [...Object.keys(VOWELS), ...Object.keys(CONSONANTS), ...Object.keys(MARKS)].sort((a, b) => b.length - a.length);
const VIRAMA = "्";

export function toDevanagari(iast: string): string {
  const s = iast.normalize("NFC").toLowerCase().replace(/’/g, "'").replace(/ '/g, "'").replace(/-/g, "")
    .replace(/(^|\s)oṃ(?=\s|$)/g, "$1ॐ");
  let out = "";
  let open = false; // the last letter was a consonant still waiting for its vowel
  for (let i = 0; i < s.length;) {
    // as printed, a word ending in a consonant joins the next word: mām upetya → मामुपेत्य
    if (open && s[i] === " " && TOKENS.some((t) => !(t in MARKS) && s.startsWith(t, i + 1))) { i++; continue; }
    const tok = TOKENS.find((t) => s.startsWith(t, i));
    if (tok && tok in VOWELS) out += open ? VOWELS[tok][1] : VOWELS[tok][0];
    else if (tok && tok in CONSONANTS) out += (open ? VIRAMA : "") + CONSONANTS[tok];
    else out += (open ? VIRAMA : "") + (tok ? MARKS[tok] : s[i]);
    open = !!tok && tok in CONSONANTS;
    i += tok ? tok.length : 1;
  }
  return open ? out + VIRAMA : out;
}

export const SCRIPTS = [
  { id: "deva", name: "देवनागरी (Devanāgarī)" },
  { id: "iast", name: "Roman (IAST)" },
  { id: "telugu", name: "తెలుగు (Telugu)" },
  { id: "tamil", name: "தமிழ் (Tamil)" },
  { id: "kannada", name: "ಕನ್ನಡ (Kannada)" },
  { id: "malayalam", name: "മലയാളം (Malayalam)" },
  { id: "bengali", name: "বাংলা (Bengali)" },
  { id: "gujarati", name: "ગુજરાતી (Gujarati)" },
  { id: "odia", name: "ଓଡ଼ିଆ (Odia)" },
] as const;
export type Script = (typeof SCRIPTS)[number]["id"];

const OFFSET: Partial<Record<Script, number>> = { bengali: 0x80, gujarati: 0x180, odia: 0x200, tamil: 0x280, telugu: 0x300, kannada: 0x380, malayalam: 0x400 };

/** Letters a script lacks, written the way that script's Sanskrit books write them. */
const BEFORE: Partial<Record<Script, [RegExp, string][]>> = {
  bengali: [[/व/g, "ब"], [/ळ/g, "ल"], [/ॐ/g, "ओं"]],
  telugu: [[/ॐ/g, "ओं"]], kannada: [[/ॐ/g, "ओं"]], malayalam: [[/ॐ/g, "ओं"]], odia: [[/ॐ/g, "ओं"]],
  // Tamil: ṛ as ru, and the missing stops as the nearest letter with a superscript 2, 3 or 4 (– for now)
  tamil: [
    [/ऋ/g, "रु"], [/ृ/g, "्रु"], [/ॠ/g, "रू"], [/ॄ/g, "्रू"], [/ऽ/g, "'"],
    [/[खछठथफ]/g, (c: string) => "कचटतप"["खछठथफ".indexOf(c)] + ""],
    [/[गडदब]/g, (c: string) => "कटतप"["गडदब".indexOf(c)] + ""],
    [/[घझढधभ]/g, (c: string) => "कजटतप"["घझढधभ".indexOf(c)] + ""],
  ] as unknown as [RegExp, string][],
};

/** Romanised Tamil (Divya Prabandham) is not Sanskrit, so it stays in Roman. */
const NOT_SANSKRIT = /[ṟṉḻēō]/;

export function transliterate(iast: string, script: Script): string {
  if (script === "iast" || NOT_SANSKRIT.test(iast)) return iast;
  let deva = toDevanagari(iast);
  if (script === "deva") return deva;
  for (const [re, to] of BEFORE[script] ?? []) deva = deva.replace(re, to);
  const off = OFFSET[script]!;
  let out = [...deva].map((ch) => {
    const c = ch.codePointAt(0)!;
    return c >= 0x0900 && c <= 0x097f && c !== 0x0964 && c !== 0x0965 ? String.fromCodePoint(c + off) : ch;
  }).join("");
  if (script === "tamil") {
    // the superscript follows the whole syllable, after any vowel sign or virama
    out = out.replace(/([-])([ா-்]*)/g, "$2$1").replace(/[-]/g, (m) => "²³⁴"[m.charCodeAt(0) - 0xE002]);
  }
  return out;
}
