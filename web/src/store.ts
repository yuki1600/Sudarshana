import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { Birth, ChartSpec, CloudChart, DasaEvent, Meta, Recast } from "./api";
import type { BarOrder } from "./barOrder";
import { languageOf } from "./translate";

/** A cast chart standing in for the natal one (a transit, Tajaka, Tithi Pravesha, an eclipse ...): every tab treats it as the natal chart,
 *  its balas, dasas and the rest its own, until Back to Natal Chart. */
export interface Mode {
  title: string;
  lines: [string, string][];   // facts about the chart: its period, the Muntha ...
  event?: DasaEvent;           // the span its dasas fit into; none: its dasas are a birth chart's
  recast?: Recast;             // how it was cast: cast again when the calculation options change (Modes.recastMode)
  base?: Birth;                // a transit's: the chart the Transits tab reads it against, when not the natal one (a Tajaka year in use when it was cast)
}

/** The chart the Transits tab (and the transit chakras) read the transits against: a transit's base, else the chart in use as the natal one. */
export const transitBase = (s: Pick<State, "natal" | "birth" | "mode">) => (s.mode?.title === "Transit" ? s.mode.base ?? s.natal : s.birth);

/** What a chart panel shows: which chart, which bodies, and whether it stays on the natal chart. Chosen on its menu. */
export interface PanelState { spec: ChartSpec; view: string; natalOnly?: boolean; ref?: number }     // ref: a bhava chart's own reference (Many Vargas), else the bhava_ref setting
const DEFAULT_PANELS: PanelState[] = [1, 9, 30, 3, 10, 60].map((d) => ({ spec: { kind: "varga", d }, view: "standard" }));
// A window off the main tree, or a message box
export type Window = { kind: "matching" | "seeds" | "about" | "notes" | "print" | "colors" | "timezone" | "ini" | "pages" | "address" | "fonts" | "style" | "bodies" }
  | { kind: "aspects"; division?: number } | { kind: "copy_all"; complete: boolean } | { kind: "settings"; group?: string }
  | { kind: "transit_correlation"; key: string; path: number[]; title: string } | { kind: "message"; title: string; text: string } | { kind: "mixed_big" };

/** Preferences > Related to Display: how the app shows things, none of it in a calculation. */
export interface Display {
  planets: "english" | "sanskrit"; signs: "english" | "sanskrit";
  language: string;                         // Settings > Language: the app's (translate.ts LANGUAGES), "English" or one of the ten Indian languages
  twoStyles: boolean; style2: ChartStyle;
  listFont: number; chartFont: number;      // font size factors
  colors: Record<string, string>;           // key -> #rrggbb, only those changed
  printSections: string[]; blackAndWhite: boolean; address: string; timeAmPm: boolean;   // printSections: ids of Print.tsx SECTIONS
  split: number | null;
  layout: "windows" | "starlight";            // the layout theme: the four charts and the Key Info windows, or the Starlight redesign
  brand: "sudarshana" | "praajna";          // Starlight's colours: black, white, purple and gold, or the Praajna Jyotisha Institute's saffron, gold and maroon
  degrees: boolean; retroRed: boolean; signLabels: boolean;   // Starlight's charts: degrees beside the grahas, retrograde ones in red, the signs' names in the boxes
  transitsTogether: boolean;                // Tajaka and Tithi Pravesha as sub tabs of Transits, not pages of their own
  bar: BarOrder | null;                     // Starlight's top bar as the user rearranged it (press and hold an icon); null: as shipped
  barHidden: string[];                      // Starlight's top bar: the ids of the pieces the user hid (right-click one; right-click the bar, or Settings, to bring it back)
  linkCharts: boolean;                      // Starlight: the two lower charts are their varga of the top chart's (D-9 of D-24), not of the rasi
}
/** The print report's sections shown until others are chosen (ids of Print.tsx SECTIONS). */
export const DEFAULT_PRINT = ["identity", "planets", "highlights", "rasi", "bhava", "d9", "d10", "houses", "vimsottari", "shadbala", "bhavabala", "ashtakavarga", "aspects", "friendships", "avasthas"];
export const FONT_FACTORS = [0.7, 0.8, 0.9, 1, 1.15, 1.25, 1.35, 1.5];
const DEFAULT_DISPLAY: Display = { planets: "english", signs: "english", language: "English", twoStyles: false, style2: "east", listFont: 3, chartFont: 3, colors: {}, printSections: DEFAULT_PRINT, blackAndWhite: false,
  address: "Please enter your name and address", timeAmPm: false, split: null, layout: "starlight", brand: "sudarshana",
  degrees: true, retroRed: true, signLabels: true, transitsTogether: true, bar: null, barHidden: [], linkCharts: false };
export interface Recent { name: string; birth: Birth; meta: Meta }

/** One open chart document — the flat store fields mirror the active one. */
export interface ChartDoc {
  id: string;
  name: string;
  natal: Birth;
  birth: Birth;
  meta: Meta;
  mode: Mode | null;
  undo: Birth[];
  birthZone: number | null;
}

interface State {
  name: string;
  natal: Birth | null;     // what was entered or opened
  birth: Birth | null;     // what the views show: the natal chart, or the derived chart of a mode
  meta: Meta;
  mode: Mode | null;
  openCharts: ChartDoc[];
  activeChartId: string | null;
  /** ``of``: the chart is a mode's (a transit) of this natal chart: it opens with that natal chart and the mode in use, not as a birth chart of its own. */
  openChart: (name: string, birth: Birth, meta?: Partial<Meta>, of?: { natal: Birth; mode: Mode }) => void;
  addChart: (name: string, birth: Birth, meta?: Partial<Meta>) => void;   // into the open charts, staying on the one shown
  notice: { text: string; at: number } | null;   // a brief note at the foot of the window, e.g. "Chart is already open"
  clearNotice: () => void;
  activateChart: (id: string) => void;
  closeChart: (id: string) => void;
  tab: string;
  setTab: (tab: string) => void;
  chartStyle: ChartStyle;
  setChartStyle: (s: ChartStyle) => void;
  setChart: (name: string, birth: Birth, meta?: Partial<Meta>) => void;
  enterMode: (birth: Birth, mode: Mode | null) => void;
  backToNatal: () => void;
  panels: PanelState[];
  setPanel: (i: number, p: Partial<PanelState>) => void;
  setAllPanels: (p: Partial<PanelState>) => void;
  charts: 2 | 4 | 6;                       // how many chart panels the left column shows
  setCharts: (n: 2 | 4 | 6) => void;
  optional: Record<string, boolean>;       // the optional bodies of the standard view
  setOptional: (k: string, v: boolean) => void;
  window: Window | null;
  openWindow: (w: Window | null) => void;
  say: (title: string, text: string) => void;
  undo: Birth[];                           // birth-time changes, latest last
  changeBirth: (b: Birth) => void;         // a change of birth time that Undo can take back
  undoLatest: () => void;
  undoAll: () => void;
  history: string[];                       // Navigate Backward / Forward: the screens visited
  at: number;
  navigate: (step: number) => void;
  avVarga: number;                         // "Show ashtakavarga of this chart"
  setAvVarga: (d: number) => void;
  jump: { name: string; value: string; n: number } | null;   // a command that opens a sub-tab
  go: (tab: string, sub?: [string, string]) => void;
  display: Display;
  setDisplay: (d: Partial<Display>) => void;
  recent: Recent[];
  notes: Record<string, string>;
  setNotes: (name: string, text: string) => void;
  shifts: Record<string, number>;           // Shift dasa dates, minutes by dasa
  setShift: (key: string, minutes: number) => void;
  birthZone: number | null;                 // Change timezone: the zone of birth, while another shows
  setBirthZone: (z: number | null) => void;
}

export type ChartStyle = "south" | "north" | "east";

const noMeta: Meta = { city: "", country: "", dst: false, tz_standard_east: 0, tz_dst_east: 0 };
const newId = () => (crypto.randomUUID?.() ?? `c-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`);

const snap = (s: Pick<State, "activeChartId" | "name" | "natal" | "birth" | "meta" | "mode" | "undo" | "birthZone">): ChartDoc | null =>
  s.activeChartId && s.natal && s.birth
    ? { id: s.activeChartId, name: s.name, natal: s.natal, birth: s.birth, meta: s.meta, mode: s.mode, undo: s.undo, birthZone: s.birthZone }
    : null;

const apply = (doc: ChartDoc): Pick<State, "activeChartId" | "name" | "natal" | "birth" | "meta" | "mode" | "undo" | "birthZone"> =>
  ({ activeChartId: doc.id, name: doc.name, natal: doc.natal, birth: doc.birth, meta: doc.meta, mode: doc.mode, undo: doc.undo, birthZone: doc.birthZone });

/** The same person's chart: the name and the birth moment and place (a file re-read may differ in other fields). */
const sameMoment = (a: Birth, b: Birth) => (["year", "month", "day", "hour_local", "latitude", "longitude_east"] as const).every((k) => a[k] === b[k]);
const sameChart = (c: ChartDoc, name: string, b: Birth) => c.name === name && sameMoment(c.natal, b);

/** Hours since 1970 UT: the same moment whatever zone it's shown in (Change time zone saves it at the birth zone). */
const utHours = (y: number, m: number, d: number, h: number, tz: number) => Date.UTC(y, m - 1, d) / 3.6e6 + h - tz;
/** Saved in the cloud as it is now: one of that name with the same birth moment, place, details and notes; any edit since makes it unsaved. */
export const inCloud = (cloud: CloudChart[] | undefined, c: Pick<ChartDoc, "name" | "natal" | "meta">, notes: Record<string, string>) => {
  const b = c.natal, m = c.meta;
  return !!cloud?.some((s) => s.name === (c.name || "chart") && s.year != null && s.hour != null
    && Math.abs(utHours(s.year, s.month!, s.day!, s.hour, s.tz ?? 0) - utHours(b.year, b.month, b.day, b.hour_local, b.tz_east_hours)) < 1 / 7200
    && Math.abs((s.lat ?? NaN) - b.latitude) < 1e-6 && Math.abs((s.lon ?? NaN) - b.longitude_east) < 1e-6
    && s.city === (m.city || "") && s.state === (m.state || "") && s.country === (m.country || "") && s.dst === !!m.dst && s.gender === (m.gender || 0)
    && s.noteText === (notes[c.name] ?? "").trim());
};

const upsert = (charts: ChartDoc[], doc: ChartDoc) => {
  const i = charts.findIndex((c) => c.id === doc.id);
  return i < 0 ? [...charts, doc] : charts.map((c, k) => (k === i ? doc : c));
};

/** Keep the active tab's snapshot in sync when flat chart fields change. */
const withActive = (s: State, patch: Partial<ChartDoc> & Partial<Pick<State, "name" | "natal" | "birth" | "meta" | "mode" | "undo" | "birthZone">>) => {
  const next = { ...patch };
  if (!s.activeChartId || !s.natal) return next;
  const cur = snap(s)!;
  const doc = { ...cur, ...patch, id: s.activeChartId } as ChartDoc;
  if (!doc.natal || !doc.birth) return { ...next, openCharts: s.openCharts.filter((c) => c.id !== s.activeChartId) };
  return { ...next, openCharts: upsert(s.openCharts, doc) };
};

const makeMeta = (birth: Birth, meta?: Partial<Meta>): Meta =>
  ({ ...noMeta, tz_standard_east: birth.tz_east_hours, tz_dst_east: birth.tz_east_hours, ...meta });

const pushRecent = (recent: Recent[], name: string, birth: Birth, meta: Meta) =>
  [{ name, birth, meta }, ...recent.filter((r) => r.name !== name)].slice(0, 8);

const clearActive = {
  activeChartId: null as string | null, name: "", natal: null as Birth | null, birth: null as Birth | null,
  mode: null as Mode | null, undo: [] as Birth[], birthZone: null as number | null, meta: noMeta,
};

// Saved in the browser, so a refresh comes back to the same chart (a mode's derived chart too), screen and style
export const useChart = create<State>()(persist((set) => ({
  name: "",
  natal: null,
  birth: null,
  meta: noMeta,
  mode: null,
  openCharts: [],
  activeChartId: null,
  tab: "Home",
  setTab: (tab) => set((s) => (tab === s.tab ? {} : { tab, history: [...s.history.slice(Math.max(0, s.at - 98), s.at + 1), tab], at: Math.min(s.at, 98) + 1 })),
  history: ["Home"],
  at: 0,
  navigate: (step) => set((s) => { const at = s.at + step; return at < 0 || at >= s.history.length ? {} : { at, tab: s.history[at] }; }),
  panels: DEFAULT_PANELS,
  setPanel: (i, p) => set((s) => ({ panels: s.panels.map((x, k) => (k === i ? { ...x, ...p } : x)) })),
  setAllPanels: (p) => set((s) => ({ panels: s.panels.map((x) => ({ ...x, ...p })) })),
  charts: 4,
  setCharts: (charts) => set({ charts }),
  optional: {},
  setOptional: (k, v) => set((s) => ({ optional: { ...s.optional, [k]: v } })),
  window: null,
  openWindow: (window) => set({ window }),
  say: (title, text) => set({ window: { kind: "message", title, text } }),
  undo: [],
  // a transit of the natal chart stays at its moment, read against the moved natal chart (cast again from it, should the options change); any
  // other cast goes
  changeBirth: (b) => set((s) => {
    const transit = s.mode?.title === "Transit" && !s.mode.base ? s.mode : null;
    const mode = transit && { ...transit, recast: transit.recast && { ...transit.recast, body: { ...transit.recast.body, birth: b } } };
    return withActive(s, { undo: [...s.undo.slice(-99), s.natal!], natal: b, birth: transit ? s.birth! : b, mode });
  }),
  undoLatest: () => set((s) => (s.undo.length ? withActive(s, { natal: s.undo[s.undo.length - 1], birth: s.undo[s.undo.length - 1], undo: s.undo.slice(0, -1), mode: null }) : {})),
  undoAll: () => set((s) => (s.undo.length ? withActive(s, { natal: s.undo[0], birth: s.undo[0], undo: [], mode: null }) : {})),
  avVarga: 1,
  setAvVarga: (avVarga) => set({ avVarga }),
  jump: null,
  go: (tab, sub) => set((s) => ({ ...(tab === s.tab ? {} : { tab, history: [...s.history.slice(Math.max(0, s.at - 98), s.at + 1), tab], at: Math.min(s.at, 98) + 1 }), jump: sub ? { name: sub[0], value: sub[1], n: (s.jump?.n ?? 0) + 1 } : s.jump })),
  display: DEFAULT_DISPLAY,
  setDisplay: (d) => set((s) => ({ display: { ...s.display, ...d } })),
  recent: [],
  notes: {},
  setNotes: (name, text) => set((s) => ({ notes: { ...s.notes, [name]: text } })),
  shifts: {},
  setShift: (key, minutes) => set((s) => { const { [key]: _, ...rest } = s.shifts; return { shifts: minutes ? { ...rest, [key]: minutes } : rest }; }),
  birthZone: null,
  setBirthZone: (birthZone) => set((s) => withActive(s, { birthZone })),
  chartStyle: "south",
  setChartStyle: (chartStyle) => set({ chartStyle }),
  setChart: (name, birth, meta) =>
    set((s) => {
      const m = makeMeta(birth, meta);
      const id = s.activeChartId ?? newId();
      const doc: ChartDoc = { id, name, natal: birth, birth, meta: m, mode: null, undo: [], birthZone: null };
      return { ...apply(doc), openCharts: upsert(s.openCharts, doc), recent: pushRecent(s.recent, name, birth, m) };
    }),
  openChart: (name, birth, meta, of) =>
    set((s) => {
      const m = makeMeta(of?.natal ?? birth, meta);
      const doc: ChartDoc = { id: newId(), name, natal: of?.natal ?? birth, birth, meta: m, mode: of?.mode ?? null, undo: [], birthZone: null };
      const saved = snap(s);
      const base = saved ? upsert(s.openCharts, saved) : s.openCharts;
      // a new chart goes at the top of the open charts (newest first); opened again: show the one already open, and say so (a mode's: the same natal chart and moment)
      const open = base.find((c) => sameChart(c, name, doc.natal) && (!of || sameMoment(c.birth, birth)));
      if (open) return { openCharts: base, ...apply(open), notice: { text: "Chart is already open", at: Date.now() } };
      return { ...apply(doc), openCharts: [doc, ...base], recent: of ? s.recent : pushRecent(s.recent, name, birth, m) };
    }),
  addChart: (name, birth, meta) =>
    set((s) => {
      const saved = snap(s);
      const base = saved ? upsert(s.openCharts, saved) : s.openCharts;
      if (base.some((c) => sameChart(c, name, birth))) return {};   // already open
      return { openCharts: [{ id: newId(), name, natal: birth, birth, meta: makeMeta(birth, meta), mode: null, undo: [], birthZone: null }, ...base] };
    }),
  notice: null,
  clearNotice: () => set({ notice: null }),
  activateChart: (id) =>
    set((s) => {
      if (id === s.activeChartId) return {};
      const target = s.openCharts.find((c) => c.id === id);
      if (!target) return {};
      const saved = snap(s);
      return { openCharts: saved ? upsert(s.openCharts, saved) : s.openCharts, ...apply(target) };
    }),
  closeChart: (id) =>
    set((s) => {
      const i = s.openCharts.findIndex((c) => c.id === id);
      if (i < 0) return {};
      const charts = s.openCharts.filter((c) => c.id !== id);
      if (id !== s.activeChartId) return { openCharts: charts };
      const next = charts[Math.min(i, charts.length - 1)];
      return next ? { openCharts: charts, ...apply(next) } : { openCharts: charts, ...clearActive };
    }),
  // a transit is read against the chart in use when it was cast (another transit's base, else the natal chart or the cast in use)
  enterMode: (birth, mode) => set((s) => {
    const base = mode?.title === "Transit" ? mode.base ?? transitBase(s) : null;
    return withActive(s, { birth, mode: base && JSON.stringify(base) !== JSON.stringify(s.natal) ? { ...mode!, base } : mode });
  }),
  backToNatal: () => set((s) => (s.natal ? withActive(s, { birth: s.natal, mode: null }) : {})),
}), {
  name: "chart.v2",
  partialize: ({ jump: _j, notice: _n, ...keep }) => keep,
  merge: (saved, cur) => {
    const s = (saved ?? {}) as Partial<State>;
    const merged = { ...cur, ...s, display: { ...DEFAULT_DISPLAY, ...s.display } } as State;
    if (merged.display.layout !== "starlight") merged.display.layout = "windows";     // an earlier name of the Windows layout
    merged.display.language = languageOf(merged.display.language);     // "Oriya" is Odia; one no longer offered (Malayalam) is English
    // The Basics tab was renamed Home; Calculations is hidden for now, so a saved one opens Home; Miscellany's views moved to Transits
    const home = (t: string) => (t === "Basics" || t === "Calculations" ? "Home" : t === "Miscellany" ? "Transits" : t) as State["tab"];
    merged.tab = home(merged.tab); merged.history = merged.history.map(home);
    // Migrate pre-tabs saves that only had the flat active chart
    if ((!merged.openCharts || merged.openCharts.length === 0) && merged.natal && merged.birth) {
      const id = merged.activeChartId || newId();
      merged.openCharts = [{ id, name: merged.name, natal: merged.natal, birth: merged.birth, meta: merged.meta ?? noMeta, mode: merged.mode, undo: merged.undo ?? [], birthZone: merged.birthZone ?? null }];
      merged.activeChartId = id;
    }
    return merged;
  },
  onRehydrateStorage: () => (state) => {
    // After hydrate, seed a tab if an older session had a chart but no openCharts list
    if (!state?.natal || !state.birth || (state.openCharts?.length ?? 0) > 0) return;
    const id = state.activeChartId || newId();
    useChart.setState({
      activeChartId: id,
      openCharts: [{ id, name: state.name, natal: state.natal, birth: state.birth, meta: state.meta, mode: state.mode, undo: state.undo, birthZone: state.birthZone }],
    });
  },
}));
