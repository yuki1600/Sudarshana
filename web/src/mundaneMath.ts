// The Mundane tab's pure helpers: records to birth data, the filter, and the observed-against-control tables of Patterns.
import type { Birth } from "./api";

export type DatasetName = "disasters" | "elections" | "sports" | "nations" | "events" | "finance";
export const DATASETS: { id: DatasetName; name: string }[] = [
  { id: "disasters", name: "Disasters" }, { id: "elections", name: "Elections" }, { id: "sports", name: "Sports" }, { id: "nations", name: "Nations" },
  { id: "events", name: "Events" }, { id: "finance", name: "Finance" },
];
export type Confidence = "exact" | "reported" | "approx" | "date" | "month";

/** A record of any of the sets: the shared moment block, and the set's own fields. Only a company (finance) may have no moment: no date. */
export interface MRecord {
  id: string; date: string; time?: string | null; tz_east: number; gregorian?: boolean; time_confidence: Confidence;
  place?: string; country?: string; iso2?: string; lat: number; lon: number; source: string; notes?: string;
  [k: string]: unknown;
}
export interface Tagged extends MRecord { set: DatasetName }

/** A database's Overview card, from the server without its records: size, span, top kinds and countries, five notable records whole. */
export interface MSummary {
  count: number; countries: number; top_countries: [string, number][]; kinds: [string, number][]; first: string | null; last: string | null;
  notable: MRecord[]; status: Record<string, number> | null;
}

/** The year of a record's date, BCE negative. */
export const yearOf = (r: { date: string }) => (r.date.startsWith("-") ? -Number(r.date.slice(1, 5)) : Number(r.date.slice(0, 4)));

/** The birth data a record casts: a record without a time is its local noon. */
export function toBirth(r: MRecord): Birth {
  const neg = r.date.startsWith("-");
  const [y, m, d] = (neg ? r.date.slice(1) : r.date).split("-").map(Number);
  let hour = 12;
  if (r.time) {
    const [h, mi, s = 0] = r.time.split(":").map(Number);
    hour = h + mi / 60 + s / 3600;
  }
  return {
    year: neg ? -y : y, month: m, day: d, hour_local: hour, tz_east_hours: r.tz_east, longitude_east: r.lon, latitude: r.lat,
    altitude_m: 0, gregorian: r.gregorian ?? true, place: String(r.place ?? r.country ?? ""), pressure_hpa: 1013.25, temperature_c: 20,
  };
}

const str = (v: unknown) => (typeof v === "string" ? v : "");

/** What a record is called in lists and on its chart. */
export function titleOf(r: Tagged): string {
  switch (r.set) {
    case "disasters": {
      const kind = str(r.type);
      const where = str(r.name) || [str(r.place), str(r.country)].filter(Boolean).join(", ");
      return str(r.name) ? where : `${kind[0]?.toUpperCase() ?? ""}${kind.slice(1)}, ${where}`;
    }
    case "elections": return `${str(r.country)}: ${str(r.winner) || "election"} sworn in (${str(r.office)})`;
    case "sports": return `${str(r.competition)} ${str(r.stage)}: ${str(r.team_a)} v ${str(r.team_b)}`;
    case "nations": return `${str(r.country)}: ${str(r.chart_name)}`;
    case "events": return str(r.name) || [str(r.place), str(r.country)].filter(Boolean).join(", ");
    case "finance": return `${str(r.name)}: ${r.chart === "founding" ? "founded" : `listed (${str(r.exchange)})`}`;
  }
}

/** The set's kind of record, for the type filter and the table: a disaster's or event's type, a match's sport, an election's office, a nation chart's event, a company's sector. */
export function kindOf(r: Tagged): string {
  return str(r.set === "disasters" || r.set === "events" ? r.type : r.set === "sports" ? r.sport : r.set === "elections" ? r.office : r.set === "finance" ? r.sector : r.event);
}

/** A company's founding day as a record of its own, to cast: local noon at the founding place. */
export function foundingOf(r: Tagged): Tagged | null {
  const at = r.founded_at as { place: string; lat: number; lon: number; tz_east: number } | undefined;
  return at ? { ...r, date: String(r.founded), time: null, tz_east: at.tz_east, lat: at.lat, lon: at.lon, place: at.place, place_country: r.country, time_confidence: "date", chart: "founding" } : null;
}

/** The size of a record for the map and the minimum filter: magnitude, VEI or water height for disasters (deaths when there is none). */
export const magnitudeOf = (r: MRecord): number | null => (typeof r.magnitude === "number" ? r.magnitude : null);
export const deathsOf = (r: MRecord): number | null => (typeof r.deaths === "number" ? r.deaths : null);

/** What a database keeps: words, any of the chosen kinds, countries, competitions and indices (a company in any of them), and per column (``cols``, by label) a search or the values ticked. */
export interface Filter {
  sets: DatasetName[]; text: string; kind: string[]; country: string[]; competition: string[]; index: string[]; cols: Record<string, string | string[]>;
}
export const NO_FILTER: Filter = { sets: ["disasters", "elections", "sports", "nations"], text: "", kind: [], country: [], competition: [], index: [], cols: {} };
export const indicesOf = (r: MRecord): string[] => (Array.isArray(r.indices) ? r.indices.map(String) : []);

/** The records a filter keeps, in date order; the column filters need the table's columns, so the table applies them (``cellMatches``). */
export function applyFilter(records: Tagged[], f: Filter): Tagged[] {
  const words = f.text.toLowerCase().split(/\s+/).filter(Boolean);
  return records.filter((r) => {
    if (!f.sets.includes(r.set)) return false;
    if (f.kind.length && !f.kind.includes(kindOf(r))) return false;
    if (f.competition.length && !f.competition.includes(String(r.competition ?? ""))) return false;
    if (f.country.length && !f.country.includes(String(r.country ?? "")) && !f.country.includes(String(r.iso2 ?? ""))) return false;
    if (f.index?.length && !f.index.some((i) => indicesOf(r).includes(i))) return false;
    if (words.length) {
      const hay = `${titleOf(r)} ${r.place ?? ""} ${r.country ?? ""} ${kindOf(r)} ${r.date ?? ""} ${r.symbol ?? ""} ${r.legal_name ?? ""} ${r.industry ?? ""}`.toLowerCase();
      if (!words.every((w) => hay.includes(w))) return false;
    }
    return true;
  });
}

/** A column filter against a cell's text: ">7" or "<1950" compare the number in it, anything else is a case-blind substring. */
export function cellMatches(text: string, q: string): boolean {
  const m = q.trim().match(/^([<>]=?)\s*(-?[\d.]+)$/);
  if (!m) return text.toLowerCase().includes(q.trim().toLowerCase());
  const v = parseFloat(text.replace(/,/g, "").replace(/^[^\d-]+/, ""));
  if (Number.isNaN(v)) return false;
  const n = Number(m[2]);
  return m[1] === ">" ? v > n : m[1] === ">=" ? v >= n : m[1] === "<" ? v < n : v <= n;
}

/** Records counted by a key, largest first: [key, count][]. */
export function countBy<T>(records: T[], key: (r: T) => string): [string, number][] {
  const m = new Map<string, number>();
  for (const r of records) { const k = key(r) || "—"; m.set(k, (m.get(k) ?? 0) + 1); }
  return [...m.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
}

/** Counts per bin of years across the records' span: [start year, count][]. */
export function yearBins(records: { date: string }[], bins = 60): [number, number][] {
  if (!records.length) return [];
  const ys = records.map(yearOf);
  const lo = Math.min(...ys), hi = Math.max(...ys);
  const width = Math.max(1, Math.ceil((hi - lo + 1) / bins));
  const out: [number, number][] = [];
  for (let s = lo; s <= hi; s += width) out.push([s, 0]);
  for (const y of ys) out[Math.min(out.length - 1, Math.floor((y - lo) / width))][1]++;
  return out;
}

// --- Patterns -----------------------------------------------------------------------------------------------------

export const GRAHAS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"] as const;
export const SIGN_NAMES = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"];
export const NAKSHATRAS = ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha", "P. Phalguni", "U. Phalguni",
  "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Moola", "P. Ashadha", "U. Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "P. Bhadrapada", "U. Bhadrapada", "Revati"];
export const WEEKDAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
const TITHIS = ["Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi"];
export const TITHI_NAMES = [...TITHIS.map((t) => `S ${t}`), "Purnima", ...TITHIS.map((t) => `K ${t}`), "Amavasya"];

/** One event's (or control moment's) factors from /api/mundane/patterns: per graha [sign, nakshatra, retrograde, house from Lagna]. */
export interface FactorRow {
  id?: string; jd: number; timed: boolean; lagna: number | null; weekday: number; tithi?: number; phase?: number;
  p: Record<string, [number, number, number, number | null]>; solar?: number | null; lunar?: number | null;
}

export type Factor =
  | { kind: "sign" | "nakshatra" | "house" | "retrograde"; body: string }
  | { kind: "lagna" | "tithi" | "paksha" | "weekday" }
  | { kind: "eclipse"; eclipse: "solar" | "lunar"; days: number };

/** The categories a factor sorts moments into. */
export function categories(f: Factor): string[] {
  switch (f.kind) {
    case "sign": case "lagna": return SIGN_NAMES;
    case "nakshatra": return NAKSHATRAS;
    case "house": return Array.from({ length: 12 }, (_, i) => `${i + 1}`);
    case "retrograde": return ["Direct", "Retrograde"];
    case "tithi": return TITHI_NAMES;
    case "paksha": return ["Shukla", "Krishna"];
    case "weekday": return WEEKDAYS;
    case "eclipse": return [`Within ${f.days} days`, "Further away"];
  }
}

/** A moment's category under a factor, or null when the moment cannot say (no time for a house, no Moon for a month-only date). */
export function categoryOf(row: FactorRow, f: Factor): number | null {
  switch (f.kind) {
    case "sign": return row.p[f.body]?.[0] ?? null;
    case "nakshatra": return row.p[f.body]?.[1] ?? null;
    case "retrograde": return row.p[f.body] ? row.p[f.body][2] : null;
    case "house": { const h = row.p[f.body]?.[3]; return h ? h - 1 : null; }
    case "lagna": return row.lagna;
    case "tithi": return row.tithi ? row.tithi - 1 : null;
    case "paksha": return row.tithi ? (row.tithi <= 15 ? 0 : 1) : null;
    case "weekday": return row.weekday;
    case "eclipse": { const d = row[f.eclipse]; return d === null || d === undefined ? null : Math.abs(d) <= f.days ? 0 : 1; }
  }
}

export interface Cell { label: string; observed: number; expected: number; share: number; ratio: number | null; ids: string[] }
export interface Table { cells: Cell[]; n: number; chi2: number; df: number; p: number }

/** Events against control for one factor: each category's count, the count the control's shares predict, and a chi-square test of the difference. */
export function compare(events: FactorRow[], control: FactorRow[], f: Factor): Table {
  const labels = categories(f);
  const obs = labels.map(() => 0), ctl = labels.map(() => 0);
  const ids: string[][] = labels.map(() => []);
  for (const e of events) { const c = categoryOf(e, f); if (c !== null) { obs[c]++; if (e.id) ids[c].push(e.id); } }
  for (const e of control) { const c = categoryOf(e, f); if (c !== null) ctl[c]++; }
  const n = obs.reduce((a, b) => a + b, 0), m = ctl.reduce((a, b) => a + b, 0);
  let chi2 = 0, df = -1;
  const cells = labels.map((label, i) => {
    const expected = m ? (n * ctl[i]) / m : 0;
    if (expected > 0) { chi2 += (obs[i] - expected) ** 2 / expected; df++; }
    return { label, observed: obs[i], expected, share: n ? obs[i] / n : 0, ratio: expected > 0 ? obs[i] / expected : null, ids: ids[i] };
  });
  df = Math.max(df, 1);
  return { cells, n, chi2, df, p: n ? chiSquareP(chi2, df) : 1 };
}

/** The upper tail of the chi-square distribution, by the Wilson–Hilferty cube-root normal approximation. */
export function chiSquareP(x: number, k: number): number {
  if (x <= 0) return 1;
  const z = (Math.cbrt(x / k) - (1 - 2 / (9 * k))) / Math.sqrt(2 / (9 * k));
  return 1 - normalCdf(z);
}

function normalCdf(z: number): number {
  // Abramowitz & Stegun 26.2.17
  const t = 1 / (1 + 0.2316419 * Math.abs(z));
  const d = 0.3989423 * Math.exp(-z * z / 2);
  const p = d * t * (0.3193815 + t * (-0.3565638 + t * (1.781478 + t * (-1.821256 + t * 1.330274))));
  return z > 0 ? 1 - p : p;
}
