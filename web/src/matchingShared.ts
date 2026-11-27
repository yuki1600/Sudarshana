import { type Birth, type MatchPart, type Meta } from "./api";

export const KUTA_ORDER = ["varna", "vashya", "tara", "yoni", "graha_maitri", "gana", "bhakoota", "nadi"] as const;
export const KUTA_LABEL: Record<string, string> = { varna: "Varna", vashya: "Vashya", tara: "Tara", yoni: "Yoni", graha_maitri: "Graha Maitri", gana: "Gana", bhakoota: "Bhakoota", nadi: "Nadi" };

export type Side = { name: string; birth: Birth; meta: Meta };
export type Tab = "matrix" | "charts";
export type Kind = "varga" | "bhava";
/** The areas of life, a sub tab each (Mind & Health the doshas, the mind and health; Marriage & Family both of those areas), then graha by graha and bhava by bhava */
export type Area = "mind" | "marriage" | "timing";
export type View = "overview" | Area | "grahas" | "bhavas" | "shortlist";
export const AREAS: { id: Area; name: string }[] = [{ id: "mind", name: "Mind & Health" }, { id: "marriage", name: "Marriage & Family" }, { id: "timing", name: "Timing" }];
export const DETAILS: { id: "grahas" | "bhavas"; name: string }[] = [{ id: "grahas", name: "Grahas" }, { id: "bhavas", name: "Bhavas" }];
/** a sub tab saved by an older build: the Rasi, Navamsa and Bala tabs are now Grahas, Houses is Bhavas, Family is in Marriage & Family, Health in Mind & Health */
export const OLD_VIEW: Record<string, View> = { rasi: "grahas", navamsa: "grahas", strength: "grahas", houses: "bhavas", comparison: "overview", family: "marriage", health: "mind" };
export type EditWho = "boy" | "girl" | null;
/** the graha the pointer is on in the comparison, marked in each partner's charts (a house's lord differs between them) */
export type Focus = { girl?: string; boy?: string } | null;
export type RankFocus = { who: "girl" | "boy"; index: number };

export const RANK_BANDS: { id: "ex" | "gd" | "av" | "lo"; name: string; range: string; fill: string; test: (s: number) => boolean }[] = [
  { id: "ex", name: "Excellent", range: "30–36", fill: "#3cb371", test: (s) => s >= 30 },
  { id: "gd", name: "Good", range: "24–29", fill: "#b8d96a", test: (s) => s >= 24 && s < 30 },
  { id: "av", name: "Average", range: "18–23", fill: "#f4a460", test: (s) => s >= 18 && s < 24 },
  { id: "lo", name: "Low", range: "under 18", fill: "#e08080", test: (s) => s < 18 },
];

export const partPada = (p: MatchPart) =>
  p.padas.length === 1 ? String(p.padas[0]) : `${p.padas[0]}–${p.padas[p.padas.length - 1]}`;
export const partFull = (p: MatchPart) => `${p.nakshatra_name} · ${p.rasi_name} · pada ${partPada(p)}`;

const MATCH_SIDES_KEY = "match.sides";

/** The saved partners; on the first open (nothing saved) the open chart goes to its gender's side. */
export function loadSides(open?: Side): { boy: Side | null; girl: Side | null } {
  try {
    const raw = JSON.parse(localStorage.getItem(MATCH_SIDES_KEY) ?? "null");
    if (raw === null && open) return { boy: open.meta?.gender === 1 ? open : null, girl: open.meta?.gender === 2 ? open : null };
    if (!raw || typeof raw !== "object") return { boy: null, girl: null };
    return { boy: raw.boy ?? null, girl: raw.girl ?? null };
  } catch {
    return { boy: null, girl: null };
  }
}

export function saveSides(boy: Side | null, girl: Side | null) {
  try { localStorage.setItem(MATCH_SIDES_KEY, JSON.stringify({ boy, girl })); } catch { /* private window */ }
}

export const tone = (score: number) => (score >= 30 ? "ex" : score >= 24 ? "gd" : score >= 18 ? "av" : "lo");
export const partOf = (parts: MatchPart[], nak: number, pada: number) =>
  parts.find((p) => p.nakshatra === nak && p.padas.includes(pada + 1))?.index ?? 0;
export const nakShort = (name: string) => name.replace("Purva ", "P.").replace("Uttara ", "U.").replace("Poorva ", "P.").replace("Ashadha", "Ash.").replace("Phalguni", "Phal.").replace("Bhadrapada", "Bhad.");
