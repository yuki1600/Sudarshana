import type { Panel } from "./SouthGrid";
import type { DatasetName, FactorRow, MRecord, MSummary } from "./mundaneMath";
import type { Facts } from "./lifeFacts";

export interface Birth {
  year: number;
  month: number;
  day: number;
  hour_local: number;
  tz_east_hours: number;
  longitude_east: number;
  latitude: number;
  altitude_m: number;
  gregorian: boolean;
  place: string;
  pressure_hpa: number;
  temperature_c: number;
  adjust?: unknown;     // a mode's moved bodies; sent back unchanged, so every view shows them
}

/** The options that differ from the defaults, by the keys of /api/settings/schema; sent with every request. */
export type Settings = Record<string, Choice["value"]>;
/** ``table``: the degrees the choice follows, a row per graha, a degree per sign from Aries (Settings shows the chosen one's) */
export interface Choice { value: string | number | boolean; label: string; table?: { name: string; degrees: number[] }[] }
export interface SettingOption {
  key: string; label: string; kind: "choice" | "bool" | "number" | "text"; default: Choice["value"]; choices: Choice[] | null; help: string | null;
  ge?: number; gt?: number; le?: number; lt?: number; max_length?: number;
}
export interface SettingGroup { name: string; options: SettingOption[] }

const STORED = "settings.v2";
/** Always applied under the user's saved deltas (Pushya-paksha ayanamsa, Sripati houses). */
const PLATFORM: Settings = { ayanamsa: "PUSHYA_PAKSHA", house_type: 3 };
let settings: Settings = { ...PLATFORM };
/** An option saved under an earlier name of swisseph_202 takes today's. */
const renamed = (s: Settings): Settings => {
  const old = Object.keys(s).find((k) => k.endsWith("_se202"));
  if (old === undefined) return s;
  const { [old]: value, ...rest } = s as Record<string, unknown>;
  return { swisseph_202: value, ...rest } as Settings;
};
try { settings = { ...PLATFORM, ...renamed(JSON.parse(localStorage.getItem(STORED) ?? "{}")) }; } catch { /* private window: the defaults */ }

export const currentSettings = () => settings;
export const perDasa = (key: string): PerDasa => ((settings as unknown as { per_dasa?: Record<string, PerDasa> }).per_dasa ?? {})[key] ?? {};
export function savePerDasa(key: string, p: PerDasa) {
  const all = { ...((settings as unknown as { per_dasa?: Record<string, PerDasa> }).per_dasa ?? {}) };
  if (Object.keys(p).length) all[key] = p; else delete all[key];
  const { per_dasa: _, ...rest } = settings as unknown as { per_dasa?: unknown } & Settings;
  saveSettings(Object.keys(all).length ? ({ ...rest, per_dasa: all } as unknown as Settings) : (rest as Settings));
}
export function saveSettings(s: Settings) {
  s = renamed(s);
  settings = { ...PLATFORM, ...s };
  try { localStorage.setItem(STORED, JSON.stringify(s)); } catch { /* private window: this session only */ }
  listeners.forEach((f) => f());
}
const listeners = new Set<() => void>();
/** Calls ``f`` after every saveSettings, for useSettings. */
export const onSettings = (f: () => void) => { listeners.add(f); return () => { listeners.delete(f); }; };

export type ChartFormat = "jhd" | "vs";
/** The chart files Open reads (.s: a .vs file saved before 2026-11-26); the name without one of these is the chart's name. */
export const CHART_FILES = ".jhd,.vs,.s";
export const chartName = (file: string) => file.replace(/\.(jhd|vs|s)$/i, "");

/** What a .jhd file carries beyond the birth moment; sent back unchanged when saving. */
export interface Meta {
  city: string;
  country: string;
  state?: string;        // GeoNames admin1 name, when known
  dst: boolean;
  tz_standard_east: number;
  tz_dst_east: number;
  gender?: number;       // line 18 of a .jhd file
  timezone?: string;     // the picked place's IANA zone, e.g. Asia/Kolkata
}

export interface PointRow {
  name: string;
  lon: number;
  nakshatra: string;
  pada: number;
  rasi: number;
  navamsa: number;
  retrograde: boolean;
  karaka: string | null;
  group?: string;
}

/** The box of "Select the bodies to show" a row answers to. */
export interface KeyRow extends PointRow { group: string; dignity?: "Exalted" | "Debilitated" | "Own" | null }     // dignity: the outer grahas' (server/basics.py outer_dignity)

/** What the Planets tab shows when a graha's row is opened (server/insights.py). */
export interface GrahaInsight {
  name: string; sign: string; sign_no: number; house: number; bhava: number; dignity: string; owns: number[]; with: string[]; aspected_by: string[];
  natural: "Benefic" | "Malefic"; functional: { label: string; why: string }; vimsopaka: number;
  shadbala?: { rupas: number; required: number; percent: number; parts: { key: string; value: number; rank: number }[] };
  aspects_on: { from: string; value: number; benefic: boolean }[]; aspects_houses: number[]; aspect_full: number;
  avasthas: Record<string, string>; maraka: string[]; mks: boolean; mks_house?: number;
  combust: boolean; relation: "Self" | "Great friend" | "Friend" | "Neutral" | "Enemy" | "Great enemy"; vargottama: boolean; war: "Wins" | "Loses" | null; mrityu: boolean; pushkara_amsa: boolean; pushkara_bhaga: boolean;
  drekkana: string; malicious: string[];
}

export interface Basics {
  name: string;
  points: PointRow[];
  core: [string, string][];
  av: { signs: number[]; bav: number[][]; sav: number[] };
  rasi: Record<string, string[]>;
  navamsa: Record<string, string[]>;
}

/** Which chart a panel shows (server/charts.py ChartSpec). */
export interface ChartSpec { kind: "varga" | "bhava" | "custom" | "sub"; d?: number; m?: number; n?: number; cyclic?: boolean; from_sign?: boolean; reverse_even?: boolean; start?: number }
export interface ChartPanel extends Panel { arudha_view: boolean; degrees?: Record<string, number>; longitudes?: Record<string, number>; retro?: string[]; muntha?: number }
/** The Traditions tab's sub tabs and their options (server/app/tradition_routes.py TraditionReq). */
export type TraditionPart = "western" | "chinese" | "world" | "iching" | "numerology" | "lalkitab";
export interface TraditionExtra { house_system?: string; male?: boolean; person?: string; chaldean?: boolean }

/** Transits > Jamakkol (server/jamakkol.py): the grahas and points in their boxes, the eight Jama grahas round the outside. */
export interface JamakkolPoint { name: string; abbr: string; lon: number; nakshatra: string; pada: number }
export interface Jamakkol {
  boxes: Record<string, string[]>; degrees: Record<string, number>; longitudes: Record<string, number>; lagna: number; udayam: number;
  jama: (JamakkolPoint & { box: number })[]; points: JamakkolPoint[]; grahas: (JamakkolPoint & { retrograde: boolean })[]; facts: [string, string][];
}
export interface AskResult { signs?: number[]; classes?: Record<string, number>; names?: string[]; text?: string }
export interface AspectTable {
  title: string; full: number; reference: string; houses: string[]; bodies: string[]; names: string[];
  rows: { body: string; marks: string[]; relation: string; benefic: boolean; retro: boolean; combust: boolean; cells: (number | null)[]; houses: number[]; lord_class: number[] }[];
}
export interface MatchRow { nakshatra: string; pada: number; score: number; level: string }
export interface Matching { native: string; partner: string; score: number; level: string; rows: MatchRow[]; native_nak?: number; native_pada?: number }
export interface MatchPart {
  index: number; nakshatra: number; nakshatra_name: string; pada: number; padas: number[];
  rasi: number; rasi_name: string; rasi_abbr: string; label: string;
}
export interface MatchMatrix { parts: MatchPart[]; scores: number[][]; stars: string[] }
export interface KutaFactor { kuta?: string; obtained_points: number; max_points: number; status?: string; [k: string]: unknown }
export interface MatchDetail {
  gunanka_score: number; max_score: number; match_level: string;
  pada_score: number; pada_level: string;
  bride: { name: string; moon_rasi: string; nakshatra: string }; groom: { name: string; moon_rasi: string; nakshatra: string };
  bride_pada?: number; groom_pada?: number;
  ashta_kuta_breakdown: Record<string, KutaFactor>;
  ancillary_kootas: Record<string, unknown>;
  dashakoota: { score: number; max_score: number; level: string; rajju_dosha: boolean; vedha_dosha: boolean; kutas: { kuta: string; grade: "Uttama" | "Madhyama" | "Adhama"; points: number; status: string; girl: string; boy: string }[] };
  kuja_dosha: { bride: Record<string, unknown>; groom: Record<string, unknown>; balance_status: string };
}
/** One partner's Kuja dosha: Mars's bhava from each reference (by the cusps when basis is "bhava"), what afflicts, what cancels. */
export interface MatchKuja { has_kuja_dosha: boolean; is_cancelled: boolean; houses: Record<"Lagna" | "Moon" | "Venus", number>; basis: "bhava" | "sign"; affliction_sources: string[]; cancellations: string[]; cancel: { kind: "dignity" | "sign" | "yuti" | "drishti"; text: string; dig?: string; deg?: number; aspect?: number; pct?: number }[] }
export interface MatchSide {
  lagna: number; lagna_lon: number; d9_lagna: number; kuja: MatchKuja;
  planets: Record<string, { lon: number; sign: number; house: number; d9_sign: number; d9_house: number; dignity: string; d9_dignity: string; rupas: number | null;
    nature: string | null; d9_nature: string | null; age?: string; alertness?: string; mood?: string; vimsopaka?: number; activity?: string; lajjitadi?: string; vaiseshikamsa?: { dasa: string; shodasa: string; dasa_n: number; shodasa_n: number } }>;
  houses: { house: number; lord: string; lord_house: number; holds: string[]; rank: number | null; rupas: number | null; cusp?: number; sav?: number }[];
}
/** One factor of the matching: each partner's value and how the two go together; tone good, mid, bad or none. */
export type MatchTone = "good" | "mid" | "bad" | null;
/** A graha's or a bhava's cell also has its parts: graha, bhava, dignity, vargottama, strength (% of its minimum), occupants, lord. */
export interface MatchCell { text: string; tone: MatchTone; hint: string; g?: string; h?: number; s?: string; dig?: string; vg?: boolean; pct?: number | null; holds?: string[]; lord?: { g: string; h: number }; parts?: { text: string; tone: MatchTone; dig?: string }[] }
export interface MatchFactor { key: string; factor: string; about?: string; girl: MatchCell; boy: MatchCell; together: MatchCell; pair: boolean; rule: string }
export interface MatchArea { id: "doshas" | "mind" | "marriage" | "family" | "health" | "timing"; name: string; tone: MatchTone; rows: MatchFactor[] }
/** One partner's Vimsottari periods, each lord's ties to marriage; an antardasa likely or possible for marriage. */
export interface MatchPeriod { lord: string; start: string; end: string; tags: string[] }
export interface MatchDasas { tags: Record<string, string[]>; periods: (MatchPeriod & { now: boolean; ads: (MatchPeriod & { level: "likely" | "possible" | null })[] })[] }
export interface MatchCompare {
  factors: MatchArea[];
  dasas: { girl: MatchDasas; boy: MatchDasas };
  match: MatchDetail & { bride_nak: number; bride_pada: number; groom_nak: number; groom_pada: number };
  areas: Record<"rasi" | "navamsa" | "houses" | "strength", { same: string[]; diff: string[]; key: { text: string; same: boolean }[] }>;
  grid: { bodies: string[]; girl: MatchSide; boy: MatchSide; need: Record<string, number>; about: string[]; karakas: string[][] };
  /** each partner's grahas on the other's grahas and bhava cusps, as the Aspects tab's table ("girl": her grahas on his) */
  cross: { girl: AspectTable; boy: AspectTable };
  similarities: string[]; differences: string[]; notes: unknown[];
  bride_moon: { nakshatra: number; pada: number; name: string };
  groom_moon: { nakshatra: number; pada: number; name: string };
}
export interface SeedRow { seed: string; index: number; star: string; planets: string[]; count: number }
export interface DasaTransit { title: string; rows: { house: string; cells: Record<string, string[]> }[] }
export interface AvView { signs: number[]; bav: number[][]; reduced: number[][]; pindas: number[][]; sav: number[]; pav: number[][][]; pinda_points: { rasi: string; nakshatra: string; star: number; sign: number }[][] }
/** basis: what the yoga reads (signs, houses by longitude, or both); places: each giver, its house (1-12) and sign (0-11) */
export type YogaBasis = "Rasi" | "Bhava" | "Rasi + Bhava";
export interface YogaRow { type: string; name: string; varga: string; givers_text: string; result: string; definition: string; basis: YogaBasis; places: [string, number, number][] }
export interface YogaListRow { index: number; type: string; name: string; definition: string; result: string; basis: YogaBasis }
export interface ColorDef { index: number; key: string; label: string; group: string; group_index: number; default_rgb: string; preview_kind: string }
export interface ChakraOptions { show?: string[]; planet_varga?: number; base_point?: number | null; base_division?: number; base_star?: number | null; chart_kind?: number | null }
export interface SpecialPoint { stars?: string[]; signs?: string[]; tithi?: string; text?: string }
export interface PerDasa { seed?: number; shift?: number; ad_method?: number; reverse?: boolean; tribhagi?: boolean; option?: number; varga?: number; tajaka_seed?: string; typed?: Typed | null; [k: string]: unknown }
export interface Typed { aq?: number | null; sc?: number | null; start?: number | null; start_exception?: number | null; stronger?: (number | null)[] | null; exception?: (number | null)[] | null }

export interface Place {
  country_code: string;
  name: string;
  latitude: number;
  longitude: number;
  tz_standard: number;
  tz_dst: number;
  a: number;
  b: number;
  admin1_code?: string;
  admin1_name?: string;
  timezone?: string;     // IANA name from GeoNames, e.g. Asia/Kolkata
  altitude?: number | null;     // metres above sea level, GeoNames; null when unknown
}

/** The conditional nakshatra dasas weighed for one chart (core_logic/conditional_dasas.py). */
export interface BestDasa {
  best: string[];
  rows: { key: string; planet: string; condition: string; met: boolean; score: number; dignity: string; notes: string[] }[];
}

export interface DasaItem {
  key: string;
  title: string;
  group: "nakshatra" | "rasi" | "other";
  strengths: boolean;      // has the Strengths box in its options
}

export interface DasaPeriod {
  label: string;
  start: string;   // ISO local time, no zone
  end: string;
  years: number;
}

export interface DasaLevel {
  title: string;
  years: string;      // the year definition its dates use
  key: string;
  path: number[];
  level: string;
  periods: DasaPeriod[];
  can_split: boolean;
}

export interface Strengths {
  av: { signs: number[]; bav: number[][]; reduced: number[][]; pindas: number[][]; sav: number[] };
  shadbala: {
    planets: { name: string; sthana: number; kala: number; dig: number; cheshta: number; naisargika: number; drig: number;
      total: number; rupas: number; required: number; percent: number; ishta: number; kashta: number }[];
    bhavas: { house: number; lord: string; sign: number; total: number; rupas: number; lord_bala: number; dig: number; drig: number }[];
  };
  /** each graha's strength by its place in its house: 100 on the cusp, 0 at the edge */
  cusp_bala: { name: string; house: number; lon: number; cusp: number; from_cusp: number; percent: number }[];
  vimsopaka: { name: string; dasa: number; shodasa: number; sapta: number; shad: number }[];
  yogas: YogaRow[];
  bars: BarPanel[];
}

export interface HouseRow { house: string; start: number; cusp: number; end: number; occupants: string[] }
export interface KpRow { label: string; lon: number; lords: string[] }

export interface TajakaPeriod { year: number; month: number; d25: number; h5: number; m25: number; m2: number; sunrise?: boolean }
/** How the dasas of a derived chart fit into its span; sent back unchanged when asking for them. */
export interface DasaEvent { kind: 1 | 2 | 5; name: string; span_days: number; counts?: number[] }
/** The request that cast a mode's chart, sent again when the calculation options change (its search may find another moment). */
export interface Recast { url: string; body: object }
export interface ModeResult { title: string; birth: Birth; start: string; end?: string; event?: DasaEvent; natal_dasas?: boolean; muntha?: { lon: number; sign: number }; recast?: Recast }
export interface TajakaResult extends ModeResult { end: string; muntha: { lon: number; sign: number } }
export interface Moment { year: number; month: number; day: number; hour_local: number; tz_east_hours: number }
/** This moment on the browser's clock, in its zone. */
export const nowMoment = (): Moment => {
  const n = new Date();
  return { year: n.getFullYear(), month: n.getMonth() + 1, day: n.getDate(), hour_local: n.getHours() + n.getMinutes() / 60 + n.getSeconds() / 3600, tz_east_hours: -n.getTimezoneOffset() / 60 };
};
export interface TransitView { key: string; name: string; columns: string[]; rows: string[][]; note?: string }
export interface PanchangaDay { date: string; lines: string[]; horas: [string, string][]; gouri: [string, string][] }
/** One span of the Muhurta day: local ISO times; `end` is null where it runs past the next sunrise. */
export interface MuhurtaSpan { name: string; start: string; end: string | null; good?: boolean | null }
export type LunarSystem = "purnimanta" | "amanta" | "saura";
export interface MuhurtaDay {
  date: string; weekday: string; sunrise: string; sunset: string; next_sunrise: string; moonrise: string | null; moonset: string | null;
  month: { name: string; amanta: string; purnimanta: string; saura: string; adhika: boolean; kshaya: string; paksha: string; vikram: number; shaka: number; gujarati: number };
  tithi: MuhurtaSpan[]; nakshatra: MuhurtaSpan[]; yoga: MuhurtaSpan[]; karana: MuhurtaSpan[]; moon_sign: MuhurtaSpan[];
  avoid: MuhurtaSpan[]; auspicious: MuhurtaSpan[];
  choghadiya: { day: MuhurtaSpan[]; night: MuhurtaSpan[] }; hora: MuhurtaSpan[]; gowri: MuhurtaSpan[]; lagna: MuhurtaSpan[];
}
export interface MuhurtaEvent { id: string; name: string; group: string }
export interface MuhurtaWindow { start: string; end: string; score: number; lagna: string; nakshatra: string; tithi: string; reasons: { label: string; good: boolean }[] }
export interface MuhurtaJudged { date: string; weekday: string; tithi: string; nakshatra: string; month: { amanta: string; purnimanta: string; saura: string; adhika: boolean; kshaya: string }; windows: MuhurtaWindow[]; reason: string | null; short: string | null; best: number | null }
export interface MuhurtaFind { event: { id: string; name: string }; personal: boolean; good_days: number; days: MuhurtaJudged[] }
/** A regional festival calendar of the Muhurta tab (data/festivals.json). */
export interface FestivalCalendar { id: string; name: string; places: string; about: string; months: "purnimanta" | "amanta" | "solar" }
export interface FestivalTime { label: string; from: string; to: string }
/** One date of an observance: the part of the day that decided it (`at`), the tithi or nakshatra (`span`), an Ekadasi's parana. */
export interface FestivalDate { date: string; masa: string; adhika?: boolean; at?: FestivalTime; span?: FestivalTime; parana?: { from: string; to: string; hari_vasara_end: string } }
export interface Festival { id: string; key: string; name: string; group: string; criteria: string; note: string | null; dates: FestivalDate[]; elsewhere: { calendar: string; name: string; dates: string[] }[] }
/** A day of the year: its tithi at sunrise and its month in the chosen calendar. */
export interface FestivalDay { tithi: string; masa: string; adhika?: boolean }
export interface Festivals { year: number; calendar: string; items: Festival[]; days: Record<string, FestivalDay> }
export interface LaghuRow { label: string; cells: [string, number][] }
export type VargaPanel = Panel;
export interface WheelSlot { star: string; bodies: string[] }
/** The Avakahada's reading of a Moon in pada ``pada`` (0..107): what its star and sign make of the native. */
export interface AvakahadaReading { pada: number; rasi_lord: string; nak_lord: string; varna: string; vashya: string; yoni: string; gana: string; nadi: string; tatva: string }

export interface Chakras {
  kalachakra: WheelSlot[]; surya_kalanala: WheelSlot[]; chandra_kalanala: WheelSlot[]; shoola: WheelSlot[];
  kota: { slots: WheelSlot[]; swami: string; pala: string };
  sarvatobhadra: { stars: Record<string, string[]>; special: string[][]; latta: Record<string, string[]>; aspect: Record<string, string[]>;
    refs: { moon_star: string; lagna_sign: string; tithi_group: string; weekday: string } };
  sudarsana: { from: string; sectors: { sign: string; bodies: string[] }[] }[];
  tripataki: { sign: string; bodies: string[] }[];
  kurma: { regions: { dir: string; stars: string[]; bodies: string[] }[]; janma: number };
  /** the bodies in each of the 108 padas, and the natal Moon's pada (0..107) and what it makes of the native */
  avakahada: { padas: string[][]; native: AvakahadaReading; every: AvakahadaReading[] };
  /** Su .. Ke: how each moves (the Sarvatobhadra's main vedha: retro the right, fast the left, normal the front). */
  motion: Record<string, "retro" | "fast" | "normal">;
  /** the natal Moon's sign, and the chart's moment: weekday 0 Sunday, tithi 0..29, the Moon's star 0..26 and sign, Amanta month 0 Chaitra */
  ghataka: { moon_sign: number; day: { weekday: number; tithi: number; tithi_name: string; nakshatra: number; moon_sign: number; month: number; month_name: string } };
  retro: string[];
}
export interface CorrelationRow { planet: string; lon: number; speed: number; point: string; percent: number; natal_lon: number }
type Tone = "good" | "bad" | "mixed";
type Instant = { when: string; past: boolean };
/** A graha's stay in its varga sign (local ISO times): when it is on its house's cusp, and its contacts with the domain, each with its exact moments. */
export type DomainRow = { graha: string; house: string; key: boolean; role: string; tone: Tone | null; entry: string; exit: string; retro: boolean;
  rules: number[]; karaka: boolean; flags: string[]; next: string; nakshatra: { n: number; pada: number };
  moon: { house: string; good: number; vedha: string[] }; info: LoreNote[];
  cusps: Instant[]; contacts: { kind: "on" | "opposite" | "aspect"; what: string; natal: boolean; domain: boolean; tone: Tone; exact: Instant[] }[] };
/** One part of a Domain row's info pop-up (server/lore.py transit_info): the house it transits, the classical result from the natal Moon,
 *  a lordship it carries there (BPHS 24), its karaka role, the nakshatra it is in (``n`` opens that one's own pop-up). */
export type LoreNote = { kind: "house" | "moon" | "lord" | "karaka" | "nakshatra"; head: string; text: string; notes: string[]; source: string;
  tone?: Tone | null; verdict?: string; n?: number };
type LoreList = { items: string[]; notes: string[] };
/** A nakshatra as Dr. Pai's Cosmic Insights gives it (data/lore/nakshatras.json), with its padas worked out. */
export type NakshatraLore = { n: number; name: string; range: string;
  padas: { signs: string[]; exalted: string[]; debilitated: string[] };
  pada_facts: { pada: number; sign: string; lord: string; aim: string; vargottama: boolean; pushkara: boolean }[];
  ruler: string; motivation: string; dosha: string; gana: string; orientation: string; quality: string; caste: string; guna: string; shakti: string;
  yoni: string; body: string; activity: string; element: string; direction: string; color: string; symbol: string; sounds: string;
  tree: { botanical: string; names: string; alt: string }; lunar_month: string; tithi: string;
  dignities: { graha: string; kind: "exalted" | "debilitated"; pada: number }[]; myths: { title: string; text: string }[];
  root: string; other_names: string[]; meaning: string; stars: string; key_points: string[]; scriptures: { text: string; source: string }[];
  deity: { name: string; text: string }; animal: { name: string; text: string }; symbol_text: { name: string; text: string } | null;
  ganesha: { form: string; text: string }; strengths: LoreList; weaknesses: LoreList; moon_good: LoreList; moon_bad: LoreList; careers: LoreList;
  themes: string[]; famous: { placement: string; people: string[] }[]; places: LoreList; grahas: Record<string, string[]>;
  abhijit?: { name: string; text: string[] };
  /** data/lore/nakshatra_readings.json: what it is, and how it reads as the Lagna's, the Moon's (janma) and the Sun's nakshatra. */
  reading: { about: string; lagna: string; moon: string; sun: string; source: string };
  significations: LoreSide[]; on_bhava: JivaAjiva[]; grahas_in: { graha: string; text: string }[] };
/** What a graha, rashi, bhava or nakshatra signifies, one side each: Jiva (the living) and Ajiva (the non-living), in named parts. */
export type LoreSide = { id: "jiva" | "ajiva"; name: string; gloss: string; parts: { id: string; name: string; items: string[] }[] };
/** Facts in groups, each a key, a value ("Fire (tejas)": a name and its gloss) and the classic it comes from; ``tile``: shown at a glance. */
export type LoreFacts = { name: string; rows: { k: string; v: string; src: string; tile?: boolean }[] }[];
export type LoreQuote = { head: string; text: string; source: string };
export type JivaAjiva = { jiva: string; ajiva: string };
/** What a lore pop-up opens: a graha by its abbreviation, a rashi, bhava or nakshatra by number. */
export type LoreLink = { kind: "graha" | "rashi" | "nakshatra" | "bhava"; n: number | string };
/** A graha as the classics give it (server/lore.py graha), with its row of each combination table. */
export type GrahaLore = { id: string; name: string; sanskrit: string; names: string[]; about: string; facts: LoreFacts; significations: LoreSide[];
  reading: { strong: string; weak: string; atmakaraka: string }; relations: { friends: string[]; neutral: string[]; enemies: string[] };
  rules: { signs: number[]; nakshatras: number[] }; karaka_of: { bphs: number[]; phaladeepika: number[] };
  classics: LoreQuote[]; classics_all: LoreQuote[]; aspects_note: string; source: string;
  in_bhava: { text: string; source: string }[]; bhava_note: string; aspect_on: string[]; aspect_note: string;
  in_rashi: { text: string; source: string }[]; in_nakshatra: string[] };
export type RashiLore = { n: number; name: string; sanskrit: string; symbol: string; about: string; facts: LoreFacts; significations: LoreSide[];
  strengths: string[]; shadows: string[]; reading: { lagna: string; moon: string; sun: string }; lord: string;
  nakshatras: { n: number; name: string; padas: number[]; lord: string }[];
  dignities: { graha: string; kind: "exalted" | "debilitated" | "moolatrikona" | "own"; deg: number | number[] | null }[];
  classics: LoreQuote[]; classics_all: LoreQuote[]; source: string; on_bhava: JivaAjiva[]; grahas_in: { graha: string; text: string; source: string }[] };
export type BhavaLore = { n: number; name: string; gloss: string; names: string[]; about: string; kinds: string[]; purushartha: string;
  karakas: { bphs: string[]; phaladeepika: string[] }; limb: string; relatives: string[]; significations: LoreSide[];
  reading: { strong: string; weak: string }; facts: LoreFacts; classics: LoreQuote[]; judge: LoreQuote[]; karaka_slokas: LoreQuote[];
  lords: { from: { house: number; text: string; source: string }[]; into: { lord: number; text: string; source: string }[] };
  on_cusp: { rashis: JivaAjiva[]; nakshatras: JivaAjiva[] }; grahas_in: { graha: string; text: string; source: string }[];
  aspects_on: { graha: string; text: string }[]; source: string };
/** Where a graha stands in the chart a bhava is read in: its bhava (from that reading's reference), its sign and dignity. */
export type LoreWhere = { graha: string; bhava: number; sign: number; sign_name: string; dignity: string; retro: boolean; combust: boolean };
/** A bhava read for the chart (server/lore.py bhava_reading): its facts, BPHS 11.14-16's tests, and the reading part by part. */
export type BhavaReading = { house: number; ref: number; from: string; name: string; gloss: string; cusp: number; start: number; end: number;
  sign: number; sign_name: string;
  nakshatra: { n: number; name: string; pada: number; lord: string; lord_bhava: number; sub_lord: string; sub_bhava: number };
  span: { sign: number; name: string; percent: number }[]; lord: LoreWhere & { co: string | null }; occupants: LoreWhere[];
  aspects: { graha: string; value: number; benefic: boolean }[]; full: number; bala: { rupas: number; percent: number } | null; sav: number;
  karakas: (LoreWhere & { in_it: boolean })[]; checks: { good: boolean; text: string; source: string }[];
  verdict: { good: number; bad: number; word: string };
  parts: { kind: "rashi" | "nakshatra" | "lord" | "occupant" | "aspect" | "karaka"; head: string; text?: string; jiva?: string; ajiva?: string;
    notes: string[]; source: string; link: LoreLink; tone?: "good" | "bad" }[];
  significations: LoreSide[]; about: string };
/** A domain of life (its varga): what it covers, what it is read from, and the grahas in and aspecting its key houses. */
export type DomainTile = { d: number; name: string; meaning: string; houses: string[]; karakas: string[];
  occupants: { graha: string; tone: Tone }[]; aspecting: { graha: string; tone: Tone }[] };
/** ``systems``: the house systems From Asc and From Moon count by (D-1: the Bhava systems set; a varga: its signs). */
export type DomainTimeline = { d: number; name: string; houses: string[]; lagna: string; systems: [string, string]; now: string; rows: DomainRow[] };
/** One thing coming in a graha's transit (server/transits.py _ahead): a stay in a varga sign (``to`` null: still in it at the search's reach),
 *  a retrograde spell (``from`` null: retrograde now), or the moment it is exact on, opposite or aspecting a natal graha. Local ISO times. */
export type AheadEvent =
  | { kind: "stay"; from: string; to: string | null; house: string; key: boolean; moon: string; good: number; aspects: string[]; note: string; tone: Tone | null }
  | { kind: "retro"; from: string | null; to: string | null }
  | { kind: "on" | "opposite" | "aspect"; what: string; when: string; domain: boolean; tone: Tone };
/** The Transit Calendar's "Coming up": each graha's events in the domain's chart, and how far its list reaches. */
export type DomainAhead = { d: number; name: string; years: number; now: string; grahas: { graha: string; events: AheadEvent[]; reach: string }[] };
export interface CalendarRow { when: string; cells: Record<string, Record<string, string>> }
export interface Table { columns: string[]; rows: string[][] }
export interface LongevityHeadline {
  class: string;
  pairYears: number | null;
  pairSpan: string;
  rectified: number | null;
  marakas: { planet: string; why: string[] }[];
  niryana: { sign: string; age: string; from: string; to: string; marks: string[]; preferredAds: string[] }[];
  preferredAds: string[];
  span: { chosen: string[]; years: number; class: string; judges: { judge: string; rupas: number; percent: number; span: string; years: number; chosen: boolean }[] };
  lifeDeath: { life: number; death: number };
  corroboration: { agree: string[]; total: number; methods: { name: string; class: string }[] };
  yogas: { long: number; short: number; balarishta: number; antidotes: number };
  methods: { name: string; class: string; years: number | null; tab: string; agrees: boolean; chosen: boolean }[];
  primeMarakas: string[];
  periods: { md: string; ad: string; from: string; to: string; age: Ages; prime: boolean }[];   // Vimsottari periods of two prime marakas in the class's ages
}
/** The Longevity sections' results as values, for the Starlight view; ``data`` of the section with that id. Ages are [from, to] in years. */
export type Ages = [number, number];
export interface LgPeriod { sign: string; from: string; to: string; age: Ages; inWindow: boolean; marks: string[]; guarded: boolean; candidate: boolean;
  ads: { sign: string; from: string; to: string; age: Ages; fromDasa: number | null; aspects: boolean; preferred: boolean }[] }
export interface LgBody { label: string; graha: string | null; sign: string; mode: number }
export interface LgSpanRow { graha: string; lon: string; full: number | null; gross: number; factor: number; visible: number; combust: boolean; enemy: boolean; lagnaCut: number; net: number }
export interface LongevityData {
  pairs: { pairs: { name: string; a: LgBody; b: LgBody; class: string; contributes: boolean }[]; decided: string; votes: number; base: string; saturn: string; jupiter: string;
    falls: boolean; rises: boolean; class: string; years: number | null; span: string; floor: number | null; rectified: number | null; average: number; contributors: string[];
    degrees: { label: string; graha: string | null; deg: number }[] };
  marakas: { grahas: { graha: string; prime: boolean; reasons: { label: string; verse: string }[] }[]; class: string; window: [number, number];
    periods: { md: string; ad: string; from: string; to: string; age: Ages; prime: boolean }[];
    stars: { name: string; count: number; nakshatra: string; lord: string; current: boolean }[]; readings: [string, string][]; divisions: [string, string][] };
  rudra: { who: { name: string; graha: string | null; sign: string; house: number }[]; trishoola: string[]; class: string; rudraYoga: string[];
    dasas: { id: string; name: string; periods: LgPeriod[] }[] };
  spans: { judges: { id: string; judge: string; rupas: number; percent: number; span: string; years: number; class: string; chosen: boolean }[]; years: number; class: string;
    spans: Record<string, { rows: LgSpanRow[]; lagna: number; lagnaLon: string; basis: string; total: number }> };
  eighth: { placement: { lagnaLord: string; eighthLord: string; lagnaBala: number | null; eighthBala: number | null; lagnaIn: number; eighthIn: number; stronger: string; house: number; kind: string; class: string };
    sun: { lord: string; relation: string; class: string | null };
    houses: { house: number; life: boolean; sign: string; lord: string; lordIn: number; lordBala: number | null; rupas: number; occupants: string[]; aspects: string[]; sav: number }[];
    life: number; death: number; lifeLords: number | null; deathLords: number | null; outcome: string };
  ashtakavarga: { rows: { name: string; rekhas: number[]; years: number }[]; years: number; class: string; distress: [number, number, number];
    saturn: { pinda: number; rekhas: number; product: number; stars: string[]; signs: string[] } };
  yogas: { groups: { id: string; name: string; rules: { verse: string; gives: string; condition: string; present: boolean }[] }[] };
}
export interface LongevitySection {
  id: string; name: string; source: string; verdict: string;
  tables: (Table & { title: string })[]; notes: string[];
  primary?: boolean; headline?: LongevityHeadline; data: Record<string, unknown>;
}
export interface TableListing { key_info: { key: string; name: string }[]; strengths: { key: string; name: string }[] }
export interface AmsaRow { name: string; division: number; index: number; ruler: string; tone?: "good" | "middling" | "bad" | null; meaning?: string }   // how kind the ruler is, and what its name means
/** One stay of Jupiter or Saturn in a nakshatra or rasi: dates as YYYY-MM-DD (``end`` null: still there), the vimsottari MD-ADs it fell in,
 *  and each pass in it (retrogression can take it out and back in): entry and exit, whether retrograde then, and the MD-AD-PD then.
 *  ``born_in``: already there at birth (the first entry is the birth). */
export interface TransitPass { in: string; in_r: boolean; in_dasa: string | null; out: string | null; out_r: boolean; out_dasa: string | null }
export interface TransitVisit { start: string; end: string | null; dasas: string[]; born_in: boolean; passes: TransitPass[] }
export type PindaTransits = Record<"jupiter" | "saturn", { star: TransitVisit[]; sign: TransitVisit[] }>;
export interface BarPanel { title: string; labels: string[]; values: number[]; digits: number; note?: string }

export interface RemedyVerseEntry {
  id: string; title: string; source: string; citation: string;
  sanskrit?: string; translation: string; note?: string;
}
export interface RemedyVaishnavaTopic {
  id: string; title: string; intro?: string; highlight?: boolean; entries: RemedyVerseEntry[];
}
export interface RemedyBphsEntry {
  id: string; scope: string; planet: string | null; condition: string | null;
  source: string; chapter: number; verses: string; title: string; translation: string;
}
export interface RemediesTopics {
  vaishnava: { topics: RemedyVaishnavaTopic[] };
  bphs: { banner: string; general: RemedyBphsEntry[]; conditional: RemedyBphsEntry[] };
}
export interface RemediesChartFlags {
  flags: Record<string, boolean>;
  applicable: string[];
  panchanga: Record<string, number>;
}
export interface CalcTopic {
  id: string; chapter: string; title: string; lede: string; source: string; tab: string;
  sections: { id: string; heading: string; body: string; formula: string | null }[];
}

/** App sets this: a 401 outside /api/auth means the session ended, so it shows the sign-in page again. */
export const auth = { onUnauthorized: () => {} };

async function call<T>(url: string, init?: RequestInit): Promise<T> {
  const r = await fetch(url, init);
  if (r.status === 401 && !url.startsWith("/api/auth/")) auth.onUnauthorized();
  if (!r.ok) {
    const body = await r.json().catch(() => null);
    throw new Error(typeof body?.detail === "string" ? body.detail : `${url}: ${r.status}`);
  }
  return r.json();
}

const withRef = (ref?: number) => (ref === undefined ? {} : { settings: { ...settings, bhava_ref: ref } });     // the body's settings win over post's
const post = <T,>(url: string, body: object) =>
  call<T>(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ settings, ...body }) });
/** A mode's chart, carrying the request that cast it (``recast``). */
const postMode = <T extends ModeResult,>(url: string, body: object) => post<T>(url, body).then((r): T => ({ ...r, recast: { url, body } }));

export interface AstroBand { sign?: number; house?: number; curve: number[][]; area: number[][] | null; cusp?: number[][] }
export interface AstroLine { body: string; angle: "ASC" | "DSC" | "MC" | "IC"; curve: number[][] }
export interface Astro { poles: number[][]; lines: AstroLine[]; signs: AstroBand[]; bhavas: AstroBand[] | null }

/** The Timeline tab's year: times are "YYYY-MM-DDTHH:MM" in the chart's zone; from/to null run past the year's ends. */
export interface TimeSpan { from: string | null; to: string | null }
export interface SkyPlace { sign: string; deg: number; nakshatra: string; gandanta: boolean }
export interface TimelineYear {
  year: number;
  samvatsaras: { name: string; number: number; start: string; end: string }[];
  signs: Record<string, (TimeSpan & { sign: string; retrograde: boolean })[]>;
  retrograde: Record<string, (TimeSpan & { sign_from: string; sign_to: string; nak_from: string; nak_to: string })[]>;
  gandanta: Record<string, (TimeSpan & { where: string })[]>;
  combustion: Record<string, (TimeSpan & { sign_from: string; sign_to: string })[]>;
  conjunctions: (SkyPlace & { at: string; bodies: [string, string]; major: boolean })[];
  eclipses: (SkyPlace & { at: string; kind: "solar" | "lunar"; type: string; node: "Rahu" | "Ketu" })[];
}

export interface FinanceBar { t: number; o: number | null; h: number | null; l: number | null; c: number; v: number | null }
export interface FinanceOhlc {
  source: "yahoo" | "ccxt";
  symbol: string;
  name: string;
  currency?: string | null;
  exchange?: string | null;
  range: string;
  interval: string;
  bars: FinanceBar[];
}
export interface FinanceSuggest {
  symbol: string;
  name: string;
  exchange: string;
  type: string;
  source: "yahoo" | "ccxt";
}
export type FinanceEventKind = "ingress" | "conjunction" | "opposition" | "station" | "eclipse" | "combustion";
export interface FinanceEvent {
  kind: FinanceEventKind;
  jd: number;
  t: number;
  iso: string;
  bodies: string[];
  sign: string | null;
  label: string;
  detail?: string;
  retrograde?: boolean;
  eclipse?: string;
  type?: string;
}

/** the default place for new charts, kept with the account (and copied into this browser, see BirthDialog's saveHome) */
export interface Home { lat: number; lon: number; tz: number; alt: number; meta?: Meta }
/** A chart saved in the cloud, as the Open chart list shows it; the birth details are missing for a file the server can't read. */
export interface CloudChart { name: string; updated: number; year?: number; month?: number; day?: number; hour?: number | null; tz?: number; place?: string; state?: string; country?: string; notes?: boolean;
  lat?: number; lon?: number; city?: string; dst?: boolean; gender?: number; noteText?: string; category?: string }
/** A chart another account shared with this one: a copy, with the sender's username. */
export interface SharedChart extends CloudChart { id: number; from: string }
/** A Rodden library chart in Open chart's list (server/rodden.py): id, name, rating (AA or A), birth date, local hour, place. */
export type RoddenChart = [number, string, string, number, number, number, number, string];
export interface Account { name: string; email: string; username: string; home: Home | null; hasPassword: boolean; termsAccepted: boolean; admin: boolean; avatar: string | null; themes: SavedTheme[] }
/** A theme the user made from their settings and saved with the account (Settings > Create theme). */
export interface SavedTheme { name: string; settings: Settings; chartStyle: string; display: Record<string, unknown> }
const authPost = <T,>(url: string, body: object) =>
  call<T>(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });

export const api = {
  me: () => call<Account | null>("/api/auth/me"),
  signUp: (name: string, email: string, password: string, username: string, terms: number) => authPost<Account>("/api/auth/signup", { name, email, password, username, terms }),
  signIn: (email: string, password: string) => authPost<Account>("/api/auth/login", { email, password }),
  ownerLogin: () => call<{ email: string; password: string } | null>("/api/auth/owner-login"),
  signOut: () => authPost<object>("/api/auth/logout", {}),
  signOutEverywhere: () => authPost<object>("/api/auth/logout-all", {}),
  saveAccount: (name: string, username: string) =>
    call<Account>("/api/auth/account", { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ name, username }) }),
  changePassword: (current: string, next: string) =>
    call<Account>("/api/auth/password", { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ current, new: next }) }),
  deleteAccount: (password: string) =>
    call<object>("/api/auth/account", { method: "DELETE", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ password }) }),
  saveAvatar: (avatar: string | null) =>
    call<Account>("/api/auth/avatar", { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ avatar }) }),
  saveThemes: (themes: SavedTheme[]) =>
    call<Account>("/api/auth/themes", { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ themes }) }),
  saveHome: (home: Home | null) =>
    call<{ home: Home | null }>("/api/auth/home", { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ home }) }),
  facts: (key: string) => call<{ data: Facts | null }>(`/api/auth/facts?key=${encodeURIComponent(key)}`),
  saveFacts: (key: string, data: Facts) =>
    call<{ data: Facts }>("/api/auth/facts", { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ key, data }) }),
  /** charts saved in the cloud, with the account: each a .vs file's text under its name */
  cloudCharts: () => call<CloudChart[]>("/api/auth/charts"),
  renameCloudChart: (old: string, name: string) => authPost<{ name: string }>("/api/auth/chart/rename", { old, new: name }),
  cloudChart: (name: string) => call<{ name: string; content: string }>(`/api/auth/chart?name=${encodeURIComponent(name)}`),
  saveCloudChart: (name: string, content: string) =>
    call<{ name: string }>("/api/auth/chart", { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ name, content }) }),
  /** accounts whose username starts with q, to share a chart with */
  findUsers: (q: string) => call<{ username: string; name: string }[]>(`/api/auth/users?q=${encodeURIComponent(q)}`),
  shareChart: (name: string, to: string) => authPost<{ name: string; to: string }>("/api/auth/chart/share", { name, to }),
  sharedCharts: () => call<SharedChart[]>("/api/auth/shared"),
  sharedChart: (id: number) => call<{ name: string; content: string }>(`/api/auth/shared/${id}`),
  deleteShared: (id: number) => call<object>(`/api/auth/shared/${id}`, { method: "DELETE" }),
  deleteCloudChart: (name: string) => call<{ name: string }>(`/api/auth/chart?name=${encodeURIComponent(name)}`, { method: "DELETE" }),
  sky: () => call<Record<string, { lon: number; retrograde: boolean }>>("/api/sky"),
  basics: (birth: Birth, name: string) => post<Basics>("/api/basics", { birth, name }),
  parseJhd: (content: string) =>
    post<{ birth: Birth; parsed: Record<string, any> }>("/api/jhd/parse", { content }),
  /** A chart file: a .jhd, or Sudarshana's .vs (JSON, which also keeps the name, state and notes). */
  exportChart: (birth: Birth, meta: Meta, format: ChartFormat = "jhd", name = "", notes = "") =>
    post<{ content: string }>("/api/jhd/export", { birth, city: meta.city, country: meta.country, dst: meta.dst,
      tz_standard_east: meta.tz_standard_east, tz_dst_east: meta.tz_dst_east, gender: meta.gender ?? 0,
      format, name, notes, state: meta.state ?? "" }),
  strengths: (birth: Birth) => post<Strengths>("/api/strengths", { birth }),
  houses: (birth: Birth, ref = 0) => post<HouseRow[]>("/api/houses", { birth, ref }),
  kp: (birth: Birth, ref = 0) => post<KpRow[]>("/api/kp", { birth, ref }),
  grahaInsights: (birth: Birth, division = 1) => post<GrahaInsight[]>("/api/graha_insights", { birth, division }),
  keyInfo: (birth: Birth, division: number) => post<KeyRow[]>("/api/key_info", { birth, division }),
  ashtakavarga: (birth: Birth, division: number, lagna: number | null) => post<AvView>("/api/ashtakavarga", { birth, division, lagna }),
  pindaTransits: (birth: Birth, star: number, sign: number) => post<PindaTransits>("/api/pinda-transits", { birth, star, sign }),
  yogas: (birth: Birth, group: number, division: number, bhava = false) => post<YogaRow[]>("/api/yogas", { birth, group, division, bhava }),
  yogaList: () => call<YogaListRow[]>("/api/yogas/list"),
  bars: (birth: Birth, kind: string, division: number) => post<BarPanel[]>("/api/bars", { birth, kind, division }),
  aspectTable: (birth: Birth, division: number, ref: number) => post<AspectTable>("/api/aspect_table", { birth, division, ref }),
  matching: (birth: Birth, bride: boolean, nakshatra: number, pada: number) => post<Matching>("/api/matching", { birth, bride, nakshatra, pada }),
  matchingMatrix: () => call<MatchMatrix>("/api/matching/matrix"),
  matchingDetail: (bride_nakshatra: number, bride_pada: number, groom_nakshatra: number, groom_pada: number) =>
    post<MatchDetail>("/api/matching/detail", { bride_nakshatra, bride_pada, groom_nakshatra, groom_pada }),
  matchingCompare: (bride: Birth, groom: Birth, bride_name = "Bride", groom_name = "Groom") =>
    post<MatchCompare>("/api/matching/compare", { bride, groom, bride_name, groom_name }),
  seeds: (birth: Birth, pada_houses: boolean) => post<SeedRow[]>("/api/seeds", { birth, pada_houses }),
  dasaTransit: (birth: Birth, key: string, path: number[], event?: DasaEvent, natal?: Birth) => post<DasaTransit>("/api/dasa/transit_correlation", { birth, key, path, event, natal }),
  sumOfLongitudes: (birth: Birth, key: string, path: number[], event?: DasaEvent, natal?: Birth) => post<{ text: string }>("/api/dasa/sum_of_longitudes", { birth, key, path, event, natal }),
  entryChart: (birth: Birth, key: string, path: number[], event?: DasaEvent, natal?: Birth) => postMode<ModeResult>("/api/dasa/entry_chart", { birth, key, path, event, natal }),
  locate: (birth: Birth, key: string, when: Moment, depth: number, event?: DasaEvent, natal?: Birth) => post<{ path: number[]; labels: string[] }>("/api/dasa/locate", { birth, key, when, depth, event, natal }),
  report: (birth: Birth, name: string, title: string, complete: boolean, place: string) => post<{ text: string }>("/api/report", { birth, name, title, complete, place }),
  timezone: (birth: Birth, zone: number) => post<{ birth: Birth; start: string }>("/api/timezone", { birth, zone }),
  iniParse: (content: string) => call<Settings>("/api/ini/parse", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ content }) }),
  iniExport: () => post<{ content: string }>("/api/ini/export", {}),
  colors: () => call<{ groups: unknown; colours: ColorDef[] }>("/api/colors"),
  specialPoint: (birth: Birth, o: { kind: string; value?: number; division?: number; point?: string; star?: string }) => post<SpecialPoint>("/api/chakras/special_point", { birth, ...o }),
  panchangaText: (birth: Birth, kind: string, year: number, month: number, day: number, days: number) => post<{ text: string }>("/api/panchanga/text", { birth, kind, year, month, day, days }),
  tajaka: (birth: Birth, p: TajakaPeriod) => postMode<TajakaResult>("/api/modes/tajaka", { birth, ...p }),
  dasaList: () => call<DasaItem[]>("/api/dasas"),
  bestDasa: (birth: Birth) => post<BestDasa>("/api/dasa/best", { birth }),
  tithiPravesha: (birth: Birth, year: number, month = 0, day = 0) => postMode<ModeResult>("/api/modes/tithi_pravesha", { birth, year, month, day }),
  tithiPraveshaMonths: (birth: Birth, year: number) => post<string[]>("/api/modes/tithi_pravesha/months", { birth, year }),
  pravesha: (birth: Birth, when: Moment, kind: string, period: string, before = false) => postMode<ModeResult>("/api/modes/pravesha", { birth, when, kind, period, before }),
  angularReturn: (birth: Birth, when: Moment, a: number, b: number, backward: boolean) =>
    postMode<ModeResult>("/api/modes/angular_return", { birth, when, a, b, backward }),
  mundane: (birth: Birth, options: Record<string, unknown>) => postMode<ModeResult>("/api/modes/mundane", { birth, ...options }),
  step: (birth: Birth, seconds: number, months = 0) => post<{ birth: Birth; start: string }>("/api/step", { birth, seconds, months }),
  recast: (r: Recast) => postMode<ModeResult>(r.url, r.body),
  transitMode: (birth: Birth, when: Moment) => postMode<ModeResult>("/api/modes/transit", { birth, when }),
  progression: (birth: Birth, kind: string, when: Moment, division = 1, dasa = "vimsottari_dasa", seed = 2) => postMode<ModeResult>("/api/modes/progression", { birth, kind, when, division, dasa, seed }),
  prasna: (birth: Birth, kind: string, n: number, replace: boolean, years = 0, days = 0) => postMode<ModeResult>("/api/modes/prasna", { birth, kind, n, replace, years, days }),
  nisheka: (birth: Birth) => postMode<ModeResult>("/api/modes/nisheka", { birth }),
  lifecycle: (birth: Birth, n: number) => postMode<ModeResult>("/api/modes/lifecycle", { birth, n }),
  specialSearch: (birth: Birth, o: Record<string, unknown>) => postMode<ModeResult>("/api/modes/special_search", { birth, ...o }),
  sahams: () => call<string[]>("/api/sahams"),
  correlation: (natal: Birth, birth: Birth, threshold: number, rule = 0, orb = 1, division = 1) => post<CorrelationRow[]>("/api/transit/correlation", { natal, birth, threshold, rule, orb, division }),
  calendar: (natal: Birth, birth: Birth, step: number, count: number, items: string[], natal_varga = 1, transit_varga = 1, offset = 0) =>
    post<CalendarRow[]>("/api/transit/calendar", { natal, birth, step, count, items, natal_varga, transit_varga, offset }),
  chakras: (natal: Birth, birth: Birth, options: ChakraOptions = {}) => post<Chakras>("/api/chakras", { natal, birth, options }),
  amsa: (birth: Birth, division: number) => post<AmsaRow[]>("/api/amsa", { birth, division }),
  table: (birth: Birth, view: string, varga = 1, options?: Record<string, unknown>) => post<Table>("/api/table", { birth, view, varga, options }),
  tables: () => call<TableListing>("/api/tables"),
  longevity: (birth: Birth) => post<LongevitySection[]>("/api/longevity", { birth }),
  settingsSchema: () => call<SettingGroup[]>("/api/settings/schema"),
  transitDomains: (natal: Birth, birth: Birth) => post<DomainTile[]>("/api/transit/domains", { natal, birth }),
  transitDomain: (natal: Birth, birth: Birth, division: number) => post<DomainTimeline>("/api/transit/domain", { natal, birth, division }),
  transitAhead: (natal: Birth, birth: Birth, division: number, years: number) => post<DomainAhead>("/api/transit/ahead", { natal, birth, division, years }),
  nakshatraLore: (n: number) => call<NakshatraLore>(`/api/lore/nakshatra/${n}`),
  grahaLore: (ab: string) => call<GrahaLore>(`/api/lore/graha/${ab}`),
  rashiLore: (n: number) => call<RashiLore>(`/api/lore/rashi/${n}`),
  bhavaLore: (n: number) => call<BhavaLore>(`/api/lore/bhava/${n}`),
  /** ``ref``: the bhavas counted from the Lagna (0) or a graha (1 Sun .. 9 Ketu), as the bhava chart's reference */
  bhavaReading: (birth: Birth, house: number, ref = 0) => post<BhavaReading>("/api/lore/bhava_reading", { birth, house, ref }),
  transit: (natal: Birth, birth: Birth, reference = 0, natal_varga = 1, transit_varga = 1) => post<TransitView[]>("/api/transit", { natal, birth, reference, natal_varga, transit_varga }),
  muhurtaEvents: () => call<MuhurtaEvent[]>("/api/muhurta/events"),
  muhurtaFind: (birth: Birth, event: string, natal?: Birth) => post<MuhurtaFind>("/api/muhurta/find", { birth, event, natal }),
  muhurtaDay: (birth: Birth, lunar: LunarSystem) => post<MuhurtaDay>("/api/muhurta/day", { birth, lunar }),
  festivalCalendars: () => call<FestivalCalendar[]>("/api/festivals/calendars"),
  festivals: (birth: Birth, calendar: string) => post<Festivals>("/api/festivals", { birth, calendar }),
  panchanga: (birth: Birth, offset: number, days: number) => post<PanchangaDay[]>("/api/panchanga", { birth, offset, days }),
  laghuParasari: (birth: Birth, mode: number, added: string | null, span_days?: number, division = 1, count_signs = true, one_cycle = false) =>
    post<LaghuRow[]>("/api/laghu_parasari", { birth, mode, added, span_days, division, count_signs, one_cycle }),
  astrocartography: (birth: Birth, bhava_of: string | null, bhava_system: number) => post<Astro>("/api/astrocartography", { birth, bhava_of, bhava_system }),
  financeOhlc: (symbol: string, range = "1y", interval = "1d", exchange?: string, end_ms?: number | null, buffer = 1) =>
    post<FinanceOhlc>("/api/finance/ohlc", { symbol, range, interval, exchange, end_ms: end_ms ?? undefined, buffer }),
  financeSearch: (q: string, limit = 8) =>
    call<FinanceSuggest[]>(`/api/finance/search?q=${encodeURIComponent(q)}&limit=${limit}`),
  timeline: (birth: Birth, year: number) => post<TimelineYear>("/api/timeline", { birth, year }),
  financeEvents: (birth: Birth, start_ms: number, end_ms: number, kinds?: FinanceEventKind[]) =>
    post<FinanceEvent[]>("/api/finance/events", { birth, start_ms, end_ms, kinds }),
  vargas: (birth: Birth, divisions?: number[]) => post<VargaPanel[]>("/api/vargas", { birth, divisions }),
  // ``ref``: a bhava chart's own reference (0 lagna, 1 sun .. 9 ketu) in place of the bhava_ref setting
  panel: (birth: Birth, spec: ChartSpec, view: string, optional: Record<string, boolean>, natal?: Birth, ref?: number) => post<ChartPanel>("/api/panel", { birth, spec, view, optional, natal, ...withRef(ref) }),
  jamakkol: (birth: Birth, kind: "rasi" | "bhava") => post<Jamakkol>("/api/jamakkol", { birth, kind }),
  /** Traditions > one sub tab (server/traditions.py): what the XALEN Ephemeris engine offers beyond Jyotish. */
  traditions: <T,>(birth: Birth, part: TraditionPart, extra: TraditionExtra = {}) => post<T>("/api/traditions", { birth, part, ...extra }),
  ask: (birth: Birth, spec: ChartSpec, question: string, o: { kind?: string; planet?: number; rasi?: number } = {}, ref?: number) => post<AskResult>("/api/chart/ask", { birth, spec, question, ...o, ...withRef(ref) }),
  moveLagna: (birth: Birth, forward: boolean) => post<{ birth: Birth; start: string }>("/api/chart/move_lagna", { birth, forward }),
  dasa: (birth: Birth, key: string, path: number[], event?: DasaEvent, natal?: Birth, shift_minutes = 0) =>
    post<DasaLevel>("/api/dasa", { birth, key, path, event, natal, shift_minutes }),
  countries: () => call<{ code: string; name: string }[]>("/api/countries"),
  states: (country: string) => call<{ code: string; name: string }[]>(`/api/states?country=${encodeURIComponent(country)}`),
  places: (q: string, country = "", state = "") => {
    const p = new URLSearchParams({ q });
    if (country) p.set("country", country);
    if (state) p.set("state", state);
    return call<Place[]>(`/api/places?${p}`);
  },
  zone: (place: Place, y: number, m: number, d: number, hour: number) =>
    post<{ tz_east_hours: number; dst: boolean }>("/api/zone", { place, year: y, month: m, day: d, hour }),
  samples: () => call<string[]>("/api/samples"),
  sample: (name: string) => call<{ name: string; content: string }>(`/api/samples/${encodeURIComponent(name)}`),
  rodden: () => call<RoddenChart[]>("/api/rodden"),
  roddenChart: (id: number) => call<{ name: string; content: string }>(`/api/rodden/${id}`),
  remediesTopics: () => call<RemediesTopics>("/api/remedies/topics"),
  remediesChart: (birth: Birth) => post<RemediesChartFlags>("/api/remedies/chart", { birth }),
  calculationTopics: () => call<{ topics: CalcTopic[] }>("/api/calculations/topics"),
  mundaneData: (name: DatasetName) => call<{ name: DatasetName; about: Record<string, string>; records: MRecord[]; removed: Record<string, number> }>(`/api/mundane/data/${name}`),
  mundaneSummary: () => call<Record<DatasetName, MSummary>>("/api/mundane/summary"),
  mundanePatterns: (ids: string[]) => post<{ events: FactorRow[]; control: FactorRow[]; capped: boolean; unknown: number }>("/api/mundane/patterns", { ids }),
};
