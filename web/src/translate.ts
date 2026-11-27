/** The app's English shown in one of the ten Indian languages of Settings > Language. The word tables (languageWords.ts) are
 *  built into one language's lookup here, and a piece of text is put into the language from it: a whole label as the tables
 *  have it, else word by word (a graha, a sign, a nakshatra ... in a table cell or a short label), with the few joins Indian
 *  languages put after the word ("Sun in Aries": सूर्य मेष में). A sentence with English the tables don't have stays English
 *  as a whole. Pure: no DOM and no store, so the tests run it; language.ts puts it on the page. */

export const LANGUAGES = [
  { id: "English", native: "English", code: "en" },
  { id: "Hindi", native: "हिन्दी", code: "hi" },
  { id: "Gujarati", native: "ગુજરાતી", code: "gu" },
  { id: "Marathi", native: "मराठी", code: "mr" },
  { id: "Odia", native: "ଓଡ଼ିଆ", code: "or" },
  { id: "Bengali", native: "বাংলা", code: "bn" },
  { id: "Assamese", native: "অসমীয়া", code: "as" },
  { id: "Kannada", native: "ಕನ್ನಡ", code: "kn" },
  { id: "Tamil", native: "தமிழ்", code: "ta" },
  { id: "Telugu", native: "తెలుగు", code: "te" },
  { id: "Punjabi", native: "ਪੰਜਾਬੀ", code: "pa" },
] as const;
export type LanguageId = (typeof LANGUAGES)[number]["id"];
/** The columns of languageWords.ts after the English, in the order of the list above. */
export const CODES = ["hi", "gu", "mr", "or", "bn", "as", "kn", "ta", "te", "pa"] as const;
export type Code = (typeof CODES)[number];

/** A kept language as one of the list: "Oriya" is Odia; one no longer offered (Malayalam) is English. */
export const languageOf = (id?: string): LanguageId => (id === "Oriya" ? "Odia" : LANGUAGES.find((l) => l.id === id)?.id ?? "English");
export const codeOf = (id: LanguageId) => LANGUAGES.find((l) => l.id === id)!.code;

/** How a language puts "in", "from" and "of" after a word (``num``: after a number), and says "and" and "or"; ``joined``: a name as it
 *  stands before another in a compound (Tamil நட்சத்திரம் + தசை: நட்சத்திர தசை). */
export interface Grammar { in: (w: string, num: boolean) => string; from: (w: string, num: boolean) => string; of: (w: string, num: boolean) => string; and: string; or: string; joined?: (w: string) => string }

interface Entry { key: string; lower: string; value: string; cased: boolean }
export interface Words {
  code: Code;
  cased: Map<string, string>;      // short or mixed-case keys (Su, Ar, PPha, AmK): matched as written
  whole: Map<string, string>;      // the rest, by lower case
  first: Map<string, Entry[]>;     // every key by its first word in lower case, the longest first
  literal: [string, string][];     // keys that start with no letter ("(R)", "% left"), put in before the words are read
  verbs: Map<string, string>;      // "Show", "Choose" ...: an English label's first word, which an Indian language says last
  grammar: Grammar;
}

const LETTER = /[A-Za-zÀ-ɏḀ-ỿ]/;
const WORD = /^[A-Za-zÀ-ɏḀ-ỿ]+/;
const norm = (s: string) => s.toLowerCase().replace(/\s+/g, " ").trim();
// two letters are an abbreviation (Su, Ar), and so is a capital inside a word (PPha, AmK): "As" is the lagna, "as" a word;
// the rows after a "#!cased" line are all abbreviations (Mon, Jan), the rows after "#!any" are not
const isCased = (key: string, section: boolean) => section || key.length <= 2 || /[a-z][A-Z]/.test(key);
// English that stays as it is without making a label English: units, zones, short forms
const NEUTRAL = new Set(["AU", "GMT", "UTC", "IST", "KP", "AM", "PM", "BPHS", "Rx", "km", "mi", "hrs", "Rao", "Rangacharya", "Raman"]);
// English the languages have no word for: "its bindus in Leo" is बिंदु सिंह में
const DROP = new Set(["the", "its", "a", "an"]);

/** One language's lookup from the rows ``English[;alias...]|hi|gu|mr|or|bn|as|kn|ta|te|pa``. An empty cell: Marathi takes
 *  the Hindi, Assamese the Bengali (its র as ৰ), and the others the Hindi in their own script (fromDevanagari), which suits
 *  the Sanskrit names that make up most of the tables. A row with no Hindi has nothing to fall back on. */
export function build(code: Code, rows: string, grammar: Grammar, verbs: string): Words {
  const w: Words = { code, cased: new Map(), whole: new Map(), first: new Map(), literal: [], verbs: new Map(), grammar };
  const col = CODES.indexOf(code);
  const valueOf = (cells: string[]) => {
    // a key or a value may start with a space (" deg" is "°", so 269.4 deg reads 269.4°): only the ends are trimmed
    const own = cells[col]?.trimEnd();
    if (own) return own;
    const hi = cells[0]?.trimEnd();
    if (code === "as" && cells[4]?.trimEnd()) return cells[4].trimEnd().replace(/র/g, "ৰ");
    return hi ? fromDevanagari(hi, code) : "";
  };
  // "#!whole": the rows after it are whole labels alone ("From", a column's heading), never read inside a longer one
  let mode = "#!any";
  for (const line of rows.split("\n")) {
    if (line.startsWith("#!")) mode = line.trim();
    if (!line.trim() || line.startsWith("#")) continue;
    const [en, ...cells] = line.split("|");
    const value = valueOf(cells).normalize("NFC");     // one spelling of each letter (ਸ਼ is ਸ and its dot), as typed or derived
    if (!value) continue;
    for (const key of en.split(";")) if (mode === "#!whole") w.cased.set(key.trimEnd(), value); else add(w, key.trimEnd(), value, mode === "#!cased");
  }
  for (const line of verbs.split("\n")) {
    if (!line.trim() || line.startsWith("#")) continue;
    const [en, ...cells] = line.split("|");
    const value = valueOf(cells);
    if (value) w.verbs.set(en.trim().toLowerCase(), value);
  }
  return w;
}

/** A key and its value into the lookup; ``section``: the key is an abbreviation, matched only as written. A later key
 *  of the same text replaces the earlier one. */
export function add(w: Words, key: string, value: string, section = false) {
  if (!key) return;
  const cased = isCased(key, section);
  if (cased) w.cased.set(key, value); else w.whole.set(norm(key), value);
  const first = WORD.exec(key)?.[0];
  // the longest first, so "Poorva Phalguni" is read before a "Poorva" alone
  const into = <T,>(list: T[], item: T, len: (t: T) => number, same: (t: T) => boolean) => {
    const at = list.findIndex(same);
    if (at >= 0) list.splice(at, 1);
    const i = list.findIndex((t) => len(t) < len(item));
    list.splice(i < 0 ? list.length : i, 0, item);
  };
  if (!first) return into(w.literal, [key, value] as [string, string], (t) => t[0].length, (t) => t[0] === key);
  const list = w.first.get(first.toLowerCase()) ?? [];
  into(list, { key, lower: key.toLowerCase(), value, cased }, (e) => e.key.length, (e) => e.key === key);
  w.first.set(first.toLowerCase(), list);
}

type Tok = { t: "term" | "word" | "num" | "sep"; s: string; post?: boolean };     // post: "in" or "from" went after it

/** The text as terms the tables have, English words they don't, numbers and the rest. */
function tokens(s: string, w: Words): Tok[] {
  const out: Tok[] = [];
  let i = 0;
  while (i < s.length) {
    const c = s[i];
    if (LETTER.test(c)) {
      const word = WORD.exec(s.slice(i))![0];
      const hit = (w.first.get(word.toLowerCase()) ?? []).find((e) => {
        const end = i + e.key.length, piece = s.slice(i, end);
        return end <= s.length && !LETTER.test(s[end] ?? "") && (e.cased ? piece === e.key : piece.toLowerCase() === e.lower);
      });
      if (hit) { out.push({ t: "term", s: hit.value }); i += hit.key.length; } else { out.push({ t: "word", s: word }); i += word.length; }
    } else if (/\d/.test(c)) {
      // an ordinal's ending goes: the languages write the number alone (12th house: 12 भाव), as supOrd's raised one
      const m = /^\d+(?:[.:,]\d+)*(st|nd|rd|th)?(?![A-Za-z])/.exec(s.slice(i)) ?? /^\d+/.exec(s.slice(i))!;
      out.push({ t: "num", s: m[1] ? m[0].slice(0, -2) : m[0] });
      i += m[0].length;
    } else {
      let j = i + 1;
      while (j < s.length && !LETTER.test(s[j]) && !/\d/.test(s[j])) j++;
      out.push({ t: "sep", s: s.slice(i, j) });
      i = j;
    }
  }
  return out;
}

const AND = "\u0000and", OR = "\u0000or";     // "and" and "or" while the joins are worked out; the language's words for them at the end
const isSpace = (t?: Tok) => !!t && t.t === "sep" && /^ +$/.test(t.s);
const joins = (t?: Tok) => t?.s === AND || t?.s === OR;
const named = (t?: Tok) => !!t && (t.t === "term" || t.t === "num") && !joins(t);

/** Where the words from ``k`` end that "in" or "from" govern: names joined by spaces, commas, "&" or "and" (Moon and Lagna). */
function groupEnd(ts: Tok[], k: number): number {
  let end = k;
  for (;;) {
    const j = end + 1, join = ts[j];
    if ((isSpace(join) || (join?.t === "sep" && /^\s*[,&]\s*$/.test(join.s))) && named(ts[j + 1])) { end = j + 1; continue; }
    if (isSpace(join) && joins(ts[j + 1]) && isSpace(ts[j + 2]) && named(ts[j + 3])) { end = j + 3; continue; }
    return end;
  }
}

/** ``s`` in the language, or ``s`` itself when the tables don't have enough of it. */
export function translate(w: Words, s: string): string {
  if (!/[A-Za-z]/.test(s)) return s;
  const lead = /^\s*/.exec(s)![0], trail = /\s*$/.exec(s)![0], core = s.trim();
  const r = read(w, core);
  return r ? lead + r.text + trail : s;
}

/** ``core`` (trimmed) in the language, with how many English words were left in it; null when it can't be put into it. */
function read(w: Words, core: string): { text: string; unknown: number } | null {
  const whole = w.cased.get(core) ?? w.whole.get(norm(core));
  if (whole !== undefined) return { text: whole, unknown: 0 };
  // a lunar year and month ("Dundubhi - Pushya"): the month is a month, though a nakshatra shares its name
  const ym = /^([A-Z][A-Za-z-]+) - (Nija |Adhika )?([A-Z][A-Za-z]+)$/.exec(core);
  if (ym && (w.cased.get(ym[1]) ?? w.whole.get(norm(ym[1])))) {
    const month = w.whole.get(norm("month:" + ym[3])) ?? w.cased.get(ym[3]) ?? w.whole.get(norm(ym[3]));
    if (month) return { text: `${translate(w, ym[1])} - ${ym[2] ? translate(w, ym[2].trim()) + " " : ""}${month}`, unknown: 0 };
  }
  // a label that starts with a verb ("Save chart", "Show navamsa"): the verb last, as these languages say it
  const lead = /^([A-Za-z]+) (.+)$/.exec(core), verb = lead && w.verbs.get(lead[1].toLowerCase());
  if (verb) {
    const rest = read(w, lead[2]);
    if (rest && !rest.unknown) return { text: `${rest.text} ${verb}`, unknown: 0 };
  }
  // "5.20 of 6.50" and "5 (out of 12)" as 5.20/6.50 and 5/12
  let text = core.replace(/(\d) (?:of|\(out of) (\d+(?:\.\d+)?)\)?/g, "$1/$2"), literal = text !== core;
  for (const [en, value] of w.literal) if (text.includes(en)) { text = text.split(en).join(value); literal = true; }
  const ts = tokens(text, w);
  // "and" is a word in its own place; "in" and "from" go after the words they govern
  for (const t of ts) if (t.t === "word" && (t.s.toLowerCase() === "and" || t.s === "or")) { t.s = t.s === "or" ? OR : AND; t.t = "term"; }
  for (let k = ts.length - 1; k >= 0; k--) if (ts[k].t === "word" && DROP.has(ts[k].s.toLowerCase())) ts.splice(k, isSpace(ts[k + 1]) ? 2 : 1);
  for (let k = 0; k < ts.length; k++) {
    const t = ts[k];
    if (t.t !== "word" || (t.s !== "in" && t.s !== "from") || !isSpace(ts[k + 1]) || !named(ts[k + 2])) continue;
    const end = groupEnd(ts, k + 2), last = ts[end];
    last.s = (t.s === "in" ? w.grammar.in : w.grammar.from)(last.s, last.t === "num");
    last.t = "term";
    last.post = true;
    const group = ts.slice(k + 2, end + 1);
    // "2nd from Lagna": a name, "from" and its place, and nothing more: the place first, as these languages say it
    if (t.s === "from" && k === 2 && named(ts[0]) && isSpace(ts[1]) && end === ts.length - 1) { ts.splice(0, ts.length, ...group, { t: "sep", s: " " }, ts[0]); break; }
    ts.splice(k, end - k + 1, ...group);
  }
  // "Kind of yoga", "Lords of the 64th navamsa and ...": names, "of", names, and nothing more: the second first, then the first (योग का प्रकार)
  const of = ts.findIndex((t) => t.t === "word" && t.s === "of");
  if (of > 1 && isSpace(ts[of - 1]) && isSpace(ts[of + 1]) && named(ts[of + 2]) && groupEnd(ts, of + 2) === ts.length - 1 && named(ts[0]) && groupEnd(ts, 0) === of - 2) {
    const owner = ts.slice(of + 2), last = owner[owner.length - 1];
    last.s = w.grammar.of(last.s, last.t === "num");
    last.t = "term";
    last.post = true;
    ts.splice(0, ts.length, ...owner, { t: "sep", s: " " }, ...ts.slice(0, of - 1));
  }
  // a name before another name is the first part of a compound (Tamil and Telugu drop its ending): not before "and", nor before a place
  const joined = w.grammar.joined;
  if (joined) for (let k = 0; k + 2 < ts.length; k++) {
    const a = ts[k], b = ts[k + 2];
    if (a.t === "term" && !a.post && !joins(a) && isSpace(ts[k + 1]) && b.t === "term" && !b.post && !joins(b)) a.s = joined(a.s);
  }
  for (const t of ts) if (t.s === AND) t.s = w.grammar.and; else if (t.s === OR) t.s = w.grammar.or;
  const unknown = ts.filter((t) => t.t === "word" && t.s.length > 1 && !NEUTRAL.has(t.s)).length;
  if (!literal && !ts.some((t) => t.t === "term")) return null;
  // a word the tables don't have, in a sentence or a name ("Ravi Kumar", a place): English as a whole, never half and half
  if (unknown) return null;
  return { text: ts.map((t) => t.s).join(""), unknown };
}

// Devanagari to the other scripts, for the Sanskrit terms the tables give in Hindi alone: Bengali, Gurmukhi, Gujarati, Odia,
// Telugu and Kannada are Devanagari's letters at a fixed offset (script.ts does the same for the verses); Tamil, short of
// most of them, is written the way Tamil writes Sanskrit names
const STOPS: [string, string][] = [["कखगघ", "ङ"], ["चछजझ", "ञ"], ["टठडढ", "ण"], ["तथदध", "न"], ["पफबभ", "म"]];
/** ं before a stop as that stop's own nasal (कुंभ → कुम्भ), as Bengali, Odia and Tamil write it. */
const nasalsJoined = (s: string) => STOPS.reduce((a, [cls, n]) => a.replace(new RegExp(`ं(?=[${cls}])`, "g"), n + "्"), s);
/** A nasal joined to its stop as ं (कुम्भ → कुंभ), as Gujarati, Telugu, Kannada and Gurmukhi write it. */
const nasalsDotted = (s: string) => STOPS.reduce((a, [cls, n]) => a.replace(new RegExp(`${n}्(?=[${cls}])`, "g"), "ं"), s);
const OFFSET: Partial<Record<Code, number>> = { bn: 0x80, as: 0x80, pa: 0x100, gu: 0x180, or: 0x200, te: 0x300, kn: 0x380 };
const ASPIRATE: Record<string, string> = { ਕ: "ਖ", ਗ: "ਘ", ਚ: "ਛ", ਜ: "ਝ", ਟ: "ਠ", ਡ: "ਢ", ਤ: "ਥ", ਦ: "ਧ", ਪ: "ਫ", ਬ: "ਭ" };
const shift = (s: string, off: number) => [...s].map((ch) => {
  const c = ch.codePointAt(0)!;
  return c >= 0x0900 && c <= 0x097f && c !== 0x0964 && c !== 0x0965 ? String.fromCodePoint(c + off) : ch;
}).join("");

const TAMIL: Record<string, string> = {
  अ: "அ", आ: "ஆ", इ: "இ", ई: "ஈ", उ: "உ", ऊ: "ஊ", ऋ: "ரு", ए: "ஏ", ऐ: "ஐ", ओ: "ஓ", औ: "ஔ",
  "ा": "ா", "ि": "ி", "ी": "ீ", "ु": "ு", "ू": "ூ", "ृ": "்ரு", "े": "ே", "ै": "ை", "ो": "ோ", "ौ": "ௌ", "्": "்", "ः": "", "़": "", "ॐ": "ஓம்",
  क: "க", ख: "க", ग: "க", घ: "க", ङ: "ங", च: "ச", छ: "ச", ज: "ஜ", झ: "ஜ", ञ: "ஞ", ट: "ட", ठ: "ட", ड: "ட", ढ: "ட", ण: "ண",
  त: "த", थ: "த", द: "த", ध: "த", प: "ப", फ: "ப", ब: "ப", भ: "ப", म: "ம", य: "ய", र: "ர", ल: "ல", ळ: "ள", व: "வ", श: "ச", ष: "ஷ", स: "ஸ", ह: "ஹ",
};

/** Devanagari ``deva`` in the script of ``code``, in Unicode's composed form (NFC). */
export const fromDevanagari = (deva: string, code: Code): string => inScript(deva, code).normalize("NFC");

function inScript(deva: string, code: Code): string {
  if (code === "hi" || code === "mr") return deva;
  if (code === "ta") {
    const s = nasalsJoined(deva.replace(/ी(?=$|[\s,.;:)\-/])/g, "ि"));
    let out = "";
    for (let i = 0; i < s.length; i++) {
      const c = s[i];
      // na is dental at a word's start and before t, th, d, dh, alveolar elsewhere
      if (c === "न") out += !s[i - 1] || /[\s-]/.test(s[i - 1]) || /^्[तथदध]/.test(s.slice(i + 1, i + 3)) ? "ந" : "ன";
      else if (c === "ं") out += "ம்";
      else out += TAMIL[c] ?? c;
    }
    return out;
  }
  if (code === "pa") {
    let s = nasalsDotted(deva.replace(/ष/g, "श").replace(/ऋ/g, "रि").replace(/ृ/g, "्रि").replace(/ॐ/g, "ओं").replace(/ः/g, ""));
    return shift(s, 0x100)
      .replace(/([ਕ-ਹ])੍(?=\1)/g, "ੱ")     // a doubled consonant (tt): the addak, then the consonant
      .replace(/([ਕਗਚਜਟਡਤਦਪਬ])੍([ਖਘਛਝਠਢਥਧਫਭ])/g, (m, a: string, b: string) => (ASPIRATE[a] === b ? "ੱ" + b : m))     // tth, ddh
      .replace(/੍(?!ਰ)/g, "")                              // Gurmukhi joins only ra below (ਪ੍ਰ); the rest are written apart
      .replace(/([ਕ-ਹਿੁੂ])ਂ/g, "$1ੰ");   // tippi after a short vowel, bindi after a long one
  }
  // Kannada and Telugu end a Sanskrit name in a short i (योगिनी: ಯೋಗಿನಿ, యోగిని), as Tamil does
  let s = code === "kn" || code === "te" ? deva.replace(/ी(?=$|[\s,.;:)\-/])/g, "ि") : deva;
  if (code === "bn" || code === "as") s = nasalsJoined(s.replace(/व/g, "ब").replace(/ॐ/g, "ओं"));
  else if (code === "or") s = nasalsJoined(s.replace(/ॐ/g, "ओं"));
  else s = nasalsDotted(s);
  let out = shift(s, OFFSET[code]!);
  if (code === "as") out = out.replace(/র/g, "ৰ");
  // Odia: va is ବ, but ୱ below another letter (ସ୍ୱ, not after ର୍: ଗର୍ବିତ); ya is ଯ only where a word starts
  if (code === "or") out = out.replace(/(?<!\u0B30)\u0B4D\u0B35/g, "\u0B4D\u0B71").replace(/\u0B35/g, "\u0B2C").replace(/(?<=\S)ଯ/g, "ୟ");
  return out;
}
