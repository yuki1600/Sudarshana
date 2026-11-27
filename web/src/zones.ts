/** Time zones: the world's IANA zones, their offset on a date (DST included), and how the time zone field writes them. */

import { ZONE_COUNTRY } from "./zoneCountries.ts";

/** A local date and time, the moment a named zone's offset (and so its DST) is read at. */
export type ZoneAt = { y: number; mo: number; d: number; hour: number };

const valid = (z: string) => { try { new Intl.DateTimeFormat("en-US", { timeZone: z }); return true; } catch { return false; } };
/** The world's zones (the tz database's, each with its country), less any this browser does not know yet. */
export const ZONES = ["UTC", ...Object.keys(ZONE_COUNTRY).filter(valid)];
// the browser may name a zone by its old name (Chrome's Asia/Calcutta); the tz database's current one is in the list
const OLD: Record<string, string> = { "Africa/Asmera": "Africa/Asmara", "America/Buenos_Aires": "America/Argentina/Buenos_Aires", "America/Catamarca": "America/Argentina/Catamarca",
  "America/Cordoba": "America/Argentina/Cordoba", "America/Jujuy": "America/Argentina/Jujuy", "America/Mendoza": "America/Argentina/Mendoza", "America/Godthab": "America/Nuuk",
  "America/Indianapolis": "America/Indiana/Indianapolis", "America/Louisville": "America/Kentucky/Louisville", "America/Coral_Harbour": "America/Panama", "Asia/Calcutta": "Asia/Kolkata",
  "Asia/Katmandu": "Asia/Kathmandu", "Asia/Rangoon": "Asia/Yangon", "Asia/Saigon": "Asia/Ho_Chi_Minh", "Atlantic/Faeroe": "Atlantic/Faroe", "Europe/Kiev": "Europe/Kyiv",
  "Pacific/Enderbury": "Pacific/Kanton", "Pacific/Ponape": "Pacific/Pohnpei", "Pacific/Truk": "Pacific/Chuuk" };
/** This computer's own zone, as the list names it (null when the browser does not say). */
export const browserZone = (): string | null => {
  const z = Intl.DateTimeFormat().resolvedOptions().timeZone;
  const n = OLD[z] ?? z;
  return z && ZONES.includes(n) ? n : null;
};

/** Every half hour from -12 to +14, so an offset no zone has today can still be picked from the list. */
export const HALF_HOURS = Array.from({ length: 53 }, (_, i) => i / 2 - 12);

const offsetOf = (fmt: Intl.DateTimeFormat, t: number) => {
  const s = fmt.formatToParts(t).find((p) => p.type === "timeZoneName")?.value ?? "GMT";   // "GMT+05:30", "GMT-04:00", "GMT"
  const m = /GMT([+-])(\d+)(?::(\d+))?(?::(\d+))?/.exec(s);
  return m ? (m[1] === "-" ? -1 : 1) * (Number(m[2]) + Number(m[3] ?? 0) / 60 + Number(m[4] ?? 0) / 3600) : 0;
};

/** Hours east of GMT in ``zone`` at that local date and time, its DST included. */
export function zoneOffset(zone: string, at: ZoneAt): number {
  const fmt = new Intl.DateTimeFormat("en-US", { timeZone: zone, timeZoneName: "longOffset" });
  const d = new Date(0);
  d.setUTCFullYear(at.y, at.mo - 1, at.d);           // not Date.UTC: it reads years below 100 as 19xx
  const wall = d.getTime() + at.hour * 3600e3;       // the local wall clock, read as if it were GMT
  const first = offsetOf(fmt, wall);
  return offsetOf(fmt, wall - first * 3600e3);       // again at the true instant, so a DST change between the two is caught
}

export const round = (h: number) => Math.round(h * 10000) / 10000;
/** +5.5, -4, +0 */
export const signed = (v: string | number) => (v === "" || Number.isNaN(Number(v)) ? String(v) : `${Number(v) < 0 ? "-" : "+"}${Math.abs(round(Number(v)))}`);
/** "+5.5", "-4", "5:30", "-3:30", "+2 hrs" as hours, else null (a zone's name being typed) */
export const parse = (s: string) => {
  const m = /^\s*([+-])?\s*(\d+(?:\.\d*)?|\.\d+)(?::(\d{1,2}))?\s*(?:h|hr|hrs|hours)?\s*$/i.exec(s);
  return m ? (m[1] === "-" ? -1 : 1) * (Number(m[2]) + Number(m[3] ?? 0) / 60) : null;
};

const REGIONS = new Intl.DisplayNames(["en"], { type: "region" });
/** A zone's country: India, USA, United Kingdom ("" for UTC). */
export const countryOf = (z: string) => { const c = ZONE_COUNTRY[z]; return c === "US" ? "USA" : c ? REGIONS.of(c) ?? c : ""; };
/** A zone as the list shows it: USA/New York for the USA's, the rest of the Americas by their city alone (as "America/" is long),
 *  others as they are: Asia/Kolkata. */
export const zoneName = (z: string) => (ZONE_COUNTRY[z] === "US" ? `USA/${z.slice(z.indexOf("/") + 1)}` : z.startsWith("America/") ? z.slice(8) : z).replace(/_/g, " ");
/** Its country, then its name: India · Asia/Kolkata, Canada · Toronto, USA/New York (whose name already says it). */
export const zoneLabel = (z: string) => { const c = countryOf(z), n = zoneName(z); return c && !n.startsWith(c) ? `${c} · ${n}` : n; };
/** A country's one zone at those hours on that date (India's +5.5: Asia/Kolkata), or null when it has none or several. */
export const guessZone = (country: string | undefined, hours: number, at: ZoneAt): string | null => {
  if (!country || !Number.isFinite(hours) || ![at.y, at.mo, at.d, at.hour].every(Number.isFinite)) return null;
  const fit = ZONES.filter((z) => ZONE_COUNTRY[z] === country && round(zoneOffset(z, at)) === round(hours));
  return fit.length === 1 ? fit[0] : null;
};
