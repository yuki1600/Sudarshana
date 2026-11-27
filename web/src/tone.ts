/** Weak-to-strong tones for the analysis tabs: plain functions, so the tests can run them. */

export const clamp01 = (x: number) => (Number.isFinite(x) ? Math.min(1, Math.max(0, x)) : 0.5);

/** 0 is weak (red), 1 is strong (green): the custom property the .tone rules mix the colour from. */
export const toneStyle = (t: number) => ({ "--tone": `${Math.round(clamp01(t) * 100)}%` }) as Record<string, string>;

/** Where a value sits between the lowest and the highest of its set, 0 to 1. */
export const spread = (xs: number[]) => {
  const lo = Math.min(...xs), hi = Math.max(...xs);
  return (x: number) => (hi > lo ? (x - lo) / (hi - lo) : 0.5);
};

// shortcut: reads the server's words for a transit result (houses, taras, murthis); a new list's wording may need adding here
const BAD = /\(vedha\)|vipat|pratyak|naidhana|vainasika|destructi|taamra|loha|inauspicious|death|enemy|obstacle|danger/i;
const GOOD = /\(good\)|sampat|kshema|sa+dhana|mitra|swarna|rajata|auspicious|friend|achievement|wealth|prosperity/i;

/** "good", "bad" or "" for a line of a transit result. */
export const verdict = (text: string) => (BAD.test(text) ? "bad" : GOOD.test(text) ? "good" : "");

// Avasthas: a state's name without its gloss ("Baala (infant)" is Baala)
export const avName = (v: string) => v.replace(/\s*\([^)]*\)/g, "");
// how well each state lets a graha give its results, 0 nil to 1 full; activities split as SayanadiBadInAmsaBala does (shadbala/ _BAD_SAYANADI)
export const AV_SCORE: Record<string, number> = {
  Baala: 0.25, Kumara: 0.5, Yuva: 1, Vriddha: 0.12, Mrita: 0,
  Jaagrita: 1, Swapna: 0.5, Sushupta: 0,
  Deepta: 1, Swastha: 0.85, Garvita: 0.8, Pramudita: 0.75, Mudita: 0.75, Saanta: 0.6, Shanta: 0.5, Deena: 0.3, Lajjita: 0.25, Trushita: 0.25, Duhkhita: 0.15, Kshudhita: 0.15, Kopa: 0.1, Khala: 0.05, Kshobhita: 0.1, Vikala: 0.05,
  Prakasana: 0.85, Sabha: 0.85, Aagama: 0.75, Bhojana: 0.75, NrityaLipsa: 0.85, Kautuka: 0.85,
  Sayana: 0.2, Upavesana: 0.2, Netrapani: 0.2, Gamana: 0.2, Aagamana: 0.2, Nidra: 0.1,
  Cheshta: 1, Drishti: 0.5, Vicheshta: 0.1,
};
export const avScore = (v: string) => AV_SCORE[avName(v).split(/[\s/]/)[0]] ?? 0.5;
export const avWord = (t: number) => (t >= 0.7 ? "Good" : t >= 0.4 ? "Mixed" : "Weak");

// each scheme's names for 2, 3 .. of its vargas good for the graha (string_tables.json vaiseshikamsa_*); col: its column in the table
export const VAI = [
  { col: 2, name: "Shodasa varga", of: 16, steps: ["Bhedaka", "Kusuma", "Nagapurusha", "Kanduka", "Kerala", "Kalpavriksha", "ChandanaVana", "PurnaChandra", "Uchchaisrava", "Dhanvantari", "Suryakanta", "Vidruma", "Indraasana", "Goloka", "Srivallabha"] },
  { col: 1, name: "Dasa varga", of: 10, steps: ["Paarijaata", "Uttama", "Gopura", "Simhasana", "Paaraavata", "Devaloka", "Brahmaloka", "Airaavata", "Sreedhaama"] },
  { col: 3, name: "Sapta varga", of: 7, steps: ["Kimshuka", "Vyanjana", "Chaamara", "Chatra", "Kundala", "Mukuta"] },
  { col: 4, name: "Shad varga", of: 6, steps: ["Kimshuka", "Vyanjana", "Chaamara", "Chatra", "Kundala"] },
];
export const vaiCount = (c: string) => parseInt(c) || 0;     // "3-Uttama": 3; "" is no rank (fewer than 2 good vargas)
export const vaiTone = (n: number, of: number) => 0.5 + (0.5 * (n - 2)) / (of - 2);     // the lowest rank is still a good one: middling up to strong
