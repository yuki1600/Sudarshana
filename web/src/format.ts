export const SIGNS = ["Ar", "Ta", "Ge", "Cn", "Le", "Vi", "Li", "Sc", "Sg", "Cp", "Aq", "Pi"];
export const SIGN_NAMES = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius",
  "Capricorn", "Aquarius", "Pisces"];

/** The longitude text: ` 6 Ar 20' 25.60"`, rounded to 0.01 arc second. */
export function formatLon(lon: number): string {
  const unit = 3600 * 100; // hundredths of an arc second per degree
  const t = Math.round((((lon % 360) + 360) % 360) * unit) % (360 * unit);
  const sign = Math.floor(t / (30 * unit));
  const r = t % (30 * unit);
  const deg = Math.floor(r / unit);
  const min = Math.floor((r % unit) / 6000);
  const sec = (r % 6000) / 100;
  return `${String(deg).padStart(2, " ")} ${SIGNS[sign]} ${String(min).padStart(2, "0")}' ${sec.toFixed(2).padStart(5, "0")}"`;
}

/** Decimal hours -> h, m, s (seconds rounded, as the dialog shows them). */
export function splitHours(hours: number): [number, number, number] {
  const s = Math.round(hours * 3600);
  return [Math.floor(s / 3600), Math.floor((s % 3600) / 60), s % 60];
}

export const joinHours = (h: number, m: number, s: number) => h + m / 60 + s / 3600;

const MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

/** `16th March 2000`. */
export function formatDateOrdinal(year: number, month: number, day: number): string {
  const n = day % 100;
  const suf = n >= 11 && n <= 13 ? "th" : ({ 1: "st", 2: "nd", 3: "rd" } as Record<number, string>)[day % 10] ?? "th";
  return `${day}${suf} ${MONTHS[month - 1]} ${year}`;
}

/** Local clock in 12-hour form: `9:45:00 AM`. */
export function formatTime12(hours: number): string {
  const [h24, m, s] = splitHours(hours);
  const ap = h24 >= 12 ? "PM" : "AM";
  return `${h24 % 12 || 12}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")} ${ap}`;
}

/** Geographic degrees ↔ deg/min/sec with hemisphere (N/S or E/W). */
export type Dms = { deg: number; min: number; sec: number; hemi: 1 | -1 };
export function toDms(dec: number): Dms {
  const hemi: 1 | -1 = dec < 0 ? -1 : 1;
  const t = Math.round(Math.abs(dec) * 3600);
  return { deg: Math.floor(t / 3600), min: Math.floor((t % 3600) / 60), sec: t % 60, hemi };
}
export const fromDms = (d: Dms) => d.hemi * (d.deg + d.min / 60 + d.sec / 3600);

/** East-positive hours → `UTC+5:30`. With a different DST offset → `UTC-8 / UTC-7 DST`. */
export function formatTz(std: number, dst = std): string {
  const one = (hours: number) => {
    const sign = hours >= 0 ? "+" : "-";
    const a = Math.abs(hours);
    const h = Math.floor(a + 1e-9);
    const m = Math.round((a - h) * 60);
    return m ? `UTC${sign}${h}:${String(m).padStart(2, "0")}` : `UTC${sign}${h}`;
  };
  return dst === std ? one(std) : `${one(std)} / ${one(dst)} DST`;
}

/** Date text for an ISO local time in 12-hour form: `1857-06-09 (10:12:16 AM)`. Seconds are cut, never rounded up. */
export function formatMoment(iso: string): string {
  const [d, t] = iso.split("T");
  const h24 = Number(t.slice(0, 2));
  const ap = h24 >= 12 ? "PM" : "AM";
  return `${d} (${h24 % 12 || 12}:${t.slice(3, 5)}:${t.slice(6, 8)} ${ap})`;
}

const units = (parts: [number, string][]) => parts.filter(([n]) => n).map(([n, u]) => `${n}${u}`).join(" ") || "0d";

/** A dasa period's length in the dasa tables' units, where 0.3 years is 3 months 18 days: 12 months to a year, 30 days to a month.
 *  Under a day only the dates can say. ``fitted``: an event chart's period is scaled to its span, so its ``years`` are nominal and its dates decide too. */
export function formatDuration(p: { start: string; end: string; years: number }, fitted = false): string {
  const seconds = (Date.parse(p.end.slice(0, 19) + "Z") - Date.parse(p.start.slice(0, 19) + "Z")) / 1000;
  if (seconds < 86400) return units([[Math.floor(seconds / 3600), "h"], [Math.floor(seconds / 60) % 60, "min"], [seconds % 60, "s"]]);
  const days = Math.round((fitted ? seconds / 86400 / 365.2564 : p.years) * 360);
  return units([[Math.floor(days / 360), "y"], [Math.floor((days % 360) / 30), "mo"], [days % 30, "d"]]);
}

/** What is left of a running period, roughly: "3y 2m", "4m 12d", "9d". */
export function timeLeft(ms: number): string {
  const days = Math.max(0, ms) / 86400000;
  const years = Math.floor(days / 365.25), months = Math.floor((days % 365.25) / 30.44), rest = Math.floor((days % 365.25) % 30.44);
  return years ? `${years}y ${months}m` : months ? `${months}m ${rest}d` : `${Math.floor(days)}d`;
}

/** A passage cut to its first ``n`` sentences, and to about ``max`` letters at a word if even those run long ("…" after a cut): the
 *  books' long paragraphs at a glance. A sentence ends at . ! or ? before a capital or a quote; the text itself when nothing is cut. */
export function brief(text: string, n = 1, max = 220): string {
  const ends = /[.!?]["”’)]?\s+(?=[A-Z“"‘'(])/g;
  let end = text.length;       // fewer than n sentences: all of them
  for (let i = 0, m; i < n && (m = ends.exec(text)); i++) end = i === n - 1 ? m.index + m[0].trimEnd().length : text.length;
  let cut = text.slice(0, end);
  if (cut.length > max) {
    const at = cut.lastIndexOf(" ", max);
    cut = cut.slice(0, at > max * 0.6 ? at : max).replace(/[\s,;:–-]+$/, "") + "…";
  }
  return cut.length < text.length ? cut : text;
}

/** "Moksha (Spiritual Liberation/ Emancipation)" is ["Moksha", "Spiritual Liberation / Emancipation"]: a name and its gloss in brackets. */
export function nameAndGloss(v: string): [string, string] {
  const m = /^(.+?)\s*\((.+)\)\s*$/.exec(v.trim());
  return m ? [m[1], m[2].replace(/\s*\/\s*/g, " / ")] : [v.trim(), ""];
}
