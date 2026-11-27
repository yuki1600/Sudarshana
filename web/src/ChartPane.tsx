import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api, currentSettings, saveSettings, type Birth, type ChartSpec, type SettingGroup } from "./api";
import { ChartGrid } from "./ChartGrid";
import { DivisionDialog, CustomDialog, SubDialog } from "./ChartDialogs";
import { useMenu, type MenuEntry, type MenuItem } from "./Menu";
import { copyBitmap, type Bitmap } from "./bitmap";
import { signName } from "./names";
import { SIGNS } from "./format";
import { useChart, type PanelState } from "./store";
import { useKept, useSettings } from "./hooks";
import { bhavaOfBox } from "./chartGeometry";

const PLANETS = ["Su", "Mo", "Ma", "Me", "Ju", "Ve", "Sa", "Ra", "Ke"];
const NAMES: Record<string, string> = { As: "Lagna", Su: "Sun", Mo: "Moon", Ma: "Mars", Me: "Mercury", Ju: "Jupiter", Ve: "Venus", Sa: "Saturn", Ra: "Rahu", Ke: "Ketu" };
const BHAVA_D = [1, 9, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 16, 20, 24, 27, 30, 40, 45, 60, 81, 108, 144];
const VARGA_MENU: [number, string][] = [[9, "navamsa (D-9)"], [2, "hora (D-2)"], [3, "drekkana (D-3)"], [4, "chaturthamsa (D-4)"], [5, "panchamsa (D-5)"], [6, "Shashthamsa (D-6)"], [7, "saptamsa (D-7)"], [8, "ashtamsa (D-8)"],
  [10, "dasamsa (D-10)"], [11, "D-11"], [12, "dwadasamsa (D-12)"], [16, "shodasamsa (D-16)"], [20, "vimsamsa (D-20)"], [24, "siddhamsa (D-24)"], [27, "nakshatramsa (D-27)"], [30, "trimsamsa (D-30)"]];
const HIGHER: [number, string][] = [[40, "Khavedamsa (D-40)"], [45, "Akshavedamsa (D-45)"], [60, "shashtyamsa (D-60)"], [81, "nava-navamsa (D-81)"], [108, "Ashtottaramsa (D-108)"], [144, "Dwadasamsa-Dwadasamsa (D-144)"]];
const VIEWS: [string, string][] = [["standard", "Standard view"], ["with_graha_arudhas", "Standard view with graha arudhas"], ["upagraha", "Upagraha view"], ["graha_arudha", "Graha arudha view"], ["dual_graha_arudha", "Dual graha arudha view"],
  ["chandra_arudha", "Chandra arudha view (from Moon)"], ["surya_arudha", "Surya arudha view (from Sun)"], ["varnada", "Varnada view"], ["chara_karaka", "Chara Karaka view"], ["special_lagna", "Special lagna view"]];
export const OPTIONAL: [string, string, boolean][] = [["nodes", "Nodes (Rahu and Ketu)", true], ["outer", "Uranus, Neptune and Pluto", false], ["al", "Arudha Lagna", true], ["arudhas", "Other Arudhas", true], ["hl", "Hora Lagna", true],
  ["gl", "Ghati Lagna (Ghatika Lagna)", true], ["sl", "Sree Lagna", true], ["bb", "Bhrigu Bindu", true], ["pp", "Pranapada Lagna", true], ["md", "Maandi", true], ["gk", "Gulika", true]];
/** Starlight's optional bodies: Uranus, Neptune and Pluto drawn (with their degrees) unless turned off. */
export const starOptional = (o: Record<string, boolean>): Record<string, boolean> => ({ outer: true, ...o });
// a bhava chart's reference (bhava_ref: 0 lagna, 1 sun .. 9 ketu), lagna and moon first as on Home's bhava chart
const REF_MENU: [number, string][] = [[0, "Lagna"], [2, "Moon"], [1, "Sun"], [3, "Mars"], [4, "Mercury"], [5, "Jupiter"], [6, "Venus"], [7, "Saturn"], [8, "Rahu"], [9, "Ketu"]];
const refAbbr = (r: number) => (r === 0 ? "As" : PLANETS[r - 1]);
const RELATION_NOTE = "Relationship colours: green friend, grey neutral, red enemy; darker for great friend and great enemy.";
const planetIndex = (label?: string) => (label ? PLANETS.indexOf(label.slice(0, 2)) + 1 : 0);

/** The schemes of a division, from the Settings table: the menu's "Choose navamsa (D-9)". */
function schemes(groups: SettingGroup[] | undefined, d: number) {
  return groups?.find((g) => g.name === "Divisional charts")?.options.find((o) => o.key === `d${d}`);
}

/** What a left click on a chart picked: the body label under the pointer (if any) and the sign of its box. */
/** ``bhava``: on a bhava chart of the rasi, the bhava the box holds, counted from ``ref`` (0 Lagna, 1 Sun .. 9 Ketu); ``d``: the varga drawn. */
export type ChartPick = { body: string | null; sign: number | null; bhava?: number; ref?: number; d?: number };


export function ChartPanelView({ i, state, single, onChange, onPick, picked, hideNatal, markBody, focus, degrees, starlight, starMenu, onDegrees, bare, chart: other, centre }: { i: number; state: PanelState; single?: boolean; degrees?: boolean; starlight?: boolean; starMenu?: boolean; onDegrees?: (on: boolean) => void; bare?: boolean; chart?: Birth; onChange?: (p: Partial<PanelState>) => void; onPick?: (p: ChartPick) => void; picked?: string | null; hideNatal?: boolean; markBody?: string; focus?: string; centre?: React.ReactNode }) {
  const { tab, natal, birth, mode, display, setDisplay, optional, setOptional, setPanel, setAllPanels, charts, setCharts, say, openWindow, changeBirth, undo, undoLatest, undoAll, setAvVarga, go } = useChart();
  const client = useQueryClient();
  const settings = useSettings();
  const chart = other ?? (state.natalOnly ? natal! : birth!);   // another person's chart (Matching) instead of the open one
  const opts = starlight ? starOptional(optional) : optional;
  const ref = state.spec.kind === "bhava" ? state.ref : undefined;
  const q = useQuery({ queryKey: ["panel", chart, state.spec, state.view, opts, ref], queryFn: () => api.panel(chart, state.spec, state.view, opts, undefined, ref), placeholderData: (p) => p });
  const groups = useQuery({ queryKey: ["settingsSchema"], queryFn: api.settingsSchema, staleTime: Infinity });
  const [shaded, setShaded] = useState<number[]>([]);
  const [classes, setClasses] = useState<Record<string, number> | null>(null);
  const [selected, setSelected] = useState<string | null>(null);
  const [form, setForm] = useKept<"custom" | "sub" | "bhava_ref" | null>(`panel.form.${tab}.${i}`, null);
  const { open, node } = useMenu();
  const set = (p: Partial<PanelState>) => (onChange ? onChange(p) : setPanel(i, p));

  const scheme = (key: string, value: number | boolean | string) => {
    saveSettings({ ...currentSettings(), [key]: value });
    client.invalidateQueries();
  };
  const ask = async (question: string, o: { kind?: string; planet?: number; rasi?: number }, title: string) => {
    try {
      const r = await api.ask(chart, state.spec, question, o, ref);
      if (r.signs) { setShaded(r.signs); setClasses(null); }
      if (r.classes) { setClasses(r.classes); setShaded([]); }
      if (r.text !== undefined) say(title, r.text);
    } catch (e) { say(title, (e as Error).message); }
  };
  const copyText = async (kind: string) => {
    const r = await api.ask(chart, state.spec, "text", { kind }, ref);
    try { await navigator.clipboard.writeText(r.text ?? ""); say("Copy chart", "Copied as text."); } catch { say("Copy chart", r.text ?? ""); }
  };
  const bitmap = async (b: Bitmap, dpi: 1 | 2) => {
    try { await copyBitmap(b, chart, state, opts, dpi); say("Copy chart", "Copied as a bitmap."); } catch (e) { say("Copy chart", (e as Error).message); }
  };

  const items = (rasi: number | null, label: string | null): MenuEntry[] => {
    const p = planetIndex(label ?? undefined);
    const isPlanet = p > 0;
    const pl = label ? NAMES[label.slice(0, 2)] ?? label : "";
    const chartMenu: MenuItem[] = VARGA_MENU.map(([d, n]) => {
      const o = schemes(groups.data, d);
      const pick = { label: o && o.choices ? `Show ${n}` : `${n[0].toUpperCase()}${n.slice(1)}`, checked: state.spec.kind === "varga" && state.spec.d === d, onClick: () => set({ spec: { kind: "varga", d } }) };
      return o?.choices ? { label: `Choose ${n}`, items: [pick, ...o.choices.map((c) => ({ label: c.label, checked: (currentSettings()[o.key] ?? o.default) === c.value, onClick: () => { scheme(o.key, c.value); set({ spec: { kind: "varga", d } }); } }))] } : pick;
    });
    const higher: MenuItem[] = HIGHER.map(([d, n]) => {
      const o = schemes(groups.data, d);
      const pick = { label: o?.choices ? `Show ${n}` : n, checked: state.spec.kind === "varga" && state.spec.d === d, onClick: () => set({ spec: { kind: "varga", d } }) };
      return o?.choices ? { label: `Choose ${n}`, items: [pick, ...o.choices.map((c) => ({ label: c.label, checked: (currentSettings()[o.key] ?? o.default) === c.value, onClick: () => { scheme(o.key, c.value); set({ spec: { kind: "varga", d } }); } }))] } : pick;
    });
    const whenLagna: MenuItem = { label: `When will lagna change sign in ${q.data?.title ?? "this chart"}?`, onClick: () => ask("when", { planet: 0 }, "When will lagna change?") };
    const moveLagna: MenuItem = { label: "Change birthtime to move lagna to", items: [
      { label: "The previous sign", onClick: async () => changeBirth((await api.moveLagna(natal!, false)).birth) },
      { label: "The next sign", onClick: async () => changeBirth((await api.moveLagna(natal!, true)).birth) },
      { label: "Undo the latest change", disabled: !undo.length, onClick: undoLatest },
      { label: "Undo all changes", disabled: !undo.length, onClick: undoAll }] };
    const whenPlanet: MenuItem = { label: isPlanet ? `When will ${pl} change sign in ${q.data?.title}?` : "When will this graha change sign in this chart?", disabled: !isPlanet, onClick: () => ask("when", { planet: p }, `When will ${pl} change?`) };
    const custom: MenuItem = { label: "Custom divisional chart for research (cyclical or non-cyclical D-n)", onClick: () => setForm("custom") };
    const subDiv: MenuItem = { label: "Sub-divisional chart for research (D-mxn, i.e. D-n of D-m)", onClick: () => setForm("sub") };
    const relations: MenuItem = { label: "Relationships", items: [
      { label: "Permanent relationships of this graha", disabled: !isPlanet, onClick: () => { setSelected(label); ask("relationships", { kind: "permanent", planet: p }, ""); } },
      { label: "Temporary relationships of this graha", disabled: !isPlanet, onClick: () => { setSelected(label); ask("relationships", { kind: "temporary", planet: p }, ""); } },
      { label: "Compound relationships of this graha", disabled: !isPlanet, onClick: () => { setSelected(label); ask("relationships", { kind: "compound", planet: p }, ""); } },
      { label: "Pachakadi relationships of this graha", disabled: !(p >= 1 && p <= 7), onClick: () => ask("pachakadi", { planet: p }, `${pl}: Pachakadi Relationships`) },
      { label: "Pachakadi relationships of this rasi", disabled: rasi === null, onClick: () => ask("pachakadi", { rasi: rasi! }, "Rasi: Pachakadi Relationships") }] };
    const highlight: MenuItem = { label: "Highlight rasi(s)", items: [
      { label: "having argala on this rasi", disabled: rasi === null, onClick: () => ask("highlight", { kind: "argala", rasi: rasi! }, "") },
      { label: "having virodhargala on this rasi", disabled: rasi === null, onClick: () => ask("highlight", { kind: "virodhargala", rasi: rasi! }, "") },
      { label: "aspected by this graha (graha drishti)", disabled: !isPlanet, onClick: () => { setSelected(label); ask("highlight", { kind: "graha_drishti", planet: p }, ""); } },
      { label: "aspected by this graha (rasi drishti)", disabled: !isPlanet, onClick: () => { setSelected(label); ask("highlight", { kind: "rasi_drishti", planet: p }, ""); } },
      { label: "aspected by this rasi (rasi drishti)", disabled: rasi === null, onClick: () => ask("highlight", { kind: "rasi_drishti_of_rasi", rasi: rasi! }, "") },
      { label: "owned by this graha", disabled: !isPlanet, onClick: () => { setSelected(label); ask("highlight", { kind: "owned", planet: p }, ""); } },
      { label: "which is moolatrikona of this graha", disabled: !isPlanet, onClick: () => { setSelected(label); ask("highlight", { kind: "moolatrikona", planet: p }, ""); } },
      { label: "where this graha is exalted", disabled: !isPlanet, onClick: () => { setSelected(label); ask("highlight", { kind: "exalted", planet: p }, ""); } },
      { label: "where this graha is debilitated", disabled: !isPlanet, onClick: () => { setSelected(label); ask("highlight", { kind: "debilitated", planet: p }, ""); } },
      "-", { label: "Clear highlights and colours", disabled: !shaded.length && !classes, onClick: () => { setShaded([]); setClasses(null); setSelected(null); } }] };
    const copy: MenuItem = { label: "Copy chart", items: [
      { label: "as text to clipboard (current chart style)", onClick: () => copyText(useChart.getState().chartStyle) },
      { label: "as text to clipboard (south-north-east styles)", onClick: () => copyText("all") },
      { label: "as bitmap (as it is on the screen now)", onClick: () => bitmap("screen", 1) },
      { label: "as bitmap (south-north styles)", onClick: () => bitmap("south-north", 1) },
      { label: "as bitmap (Rasi-Navamsa)", onClick: () => bitmap("rasi-navamsa", 1) },
      { label: "as a 300 dpi bitmap (as it is on the screen now)", onClick: () => bitmap("screen", 2) },
      { label: "as a 300 dpi bitmap for books (south-north styles)", onClick: () => bitmap("south-north", 2) },
      { label: "as a 300 dpi bitmap for books (Rasi-Navamsa)", onClick: () => bitmap("rasi-navamsa", 2) }] };
    const views = VIEWS.map(([v, n]): MenuItem => ({ label: n, checked: state.view === v, onClick: () => set({ view: v }) }));
    const displayMode: MenuItem = { label: "Chart display mode", items: [
      { label: "Automatic (Natal, Tajaka etc)", checked: !state.natalOnly, onClick: () => set({ natalOnly: false }) },
      { label: "Natal chart only", checked: !!state.natalOnly, onClick: () => set({ natalOnly: true }) }] };
    // charts drawn without degrees (Many Vargas) get no toggle
    const longitudes: MenuItem[] = degrees === undefined ? [] : [{ label: degrees ? "Turn off longitudes" : "Turn on longitudes", onClick: () => (onDegrees ? onDegrees(!degrees) : setDisplay({ degrees: !degrees })) }];

    if (starlight || starMenu) {
      // Starlight's charts have the vargas, the bhava chart and its reference on their own buttons, ashtakavarga and aspects on their tabs and the
      // optional bodies in Options: the menu keeps what is about this chart (its varga's varieties first) and what was right-clicked in it
      const d = state.spec.d ?? 1;
      const o = schemes(groups.data, d);
      const name = [...VARGA_MENU, ...HIGHER].find(([x]) => x === d)?.[1];
      const varieties: MenuEntry[] = o?.choices ? [{ label: `${name ? name[0].toUpperCase() + name.slice(1) : `D-${d}`}:`, disabled: true },
        ...o.choices.map((c) => ({ label: c.label, checked: (currentSettings()[o.key] ?? o.default) === c.value, onClick: () => scheme(o.key, c.value) })), "-"] : [];
      // only the items that apply to what is under the pointer
      const usable = (m: MenuItem): MenuItem[] => {
        const kept = m.items!.filter((x) => x !== "-" && !x.disabled);
        return kept.length ? [{ ...m, items: kept }] : [];
      };
      const here: MenuItem[] = label?.startsWith("As") ? (other ? [whenLagna] : [whenLagna, moveLagna])   // moving the lagna edits the open chart
        : isPlanet ? [whenPlanet] : [];
      const highlighted = shaded.length || classes ? [{ label: "Clear highlights and colours", onClick: () => { setShaded([]); setClasses(null); setSelected(null); } }] : [];
      // Many Vargas: a bhava chart's own reference (lagna unless changed); Rasi / Bhava are buttons in a South chart's centre, so only North and East have them here
      const k = state.spec.kind, own = state.ref ?? 0;
      const { chartStyle, display: dp } = useChart.getState();
      const south = (i % 2 === 1 && dp.twoStyles ? dp.style2 : chartStyle) === "south";
      const kinds: MenuEntry[] = !starMenu || (k !== "varga" && k !== "bhava") ? [] : [
        ...(south ? [] : [{ label: "Rasi chart", checked: k === "varga", onClick: () => set({ spec: { kind: "varga", d } }) },
          { label: "Bhava chart", checked: k === "bhava", onClick: () => set({ spec: { kind: "bhava", d }, ref: own }) }]),
        // on a rasi chart too: picking a reference turns it into that bhava chart
        { label: "Bhava with reference to", items: REF_MENU.map(([r, n]) => ({ label: n, checked: k === "bhava" && own === r, onClick: () => set({ spec: { kind: "bhava", d }, ref: r }) })) }];
      // Many Vargas: the chart's switches first, then its kind and its varga's varieties; D-81 .. D-144 are charts of their own there
      if (starMenu) return ([...longitudes, { label: "Bodies shown", items: views }, { label: "Research charts", items: [custom, subDiv] }, "-",
        ...kinds, ...(kinds.length ? ["-" as const] : []), ...varieties, ...here, ...usable(highlight), ...highlighted] as MenuEntry[])
        .filter((x, n, a) => x !== "-" || (n < a.length - 1 && a[n + 1] !== "-"));     // no separator last or doubled
      return [
        ...varieties,
        ...here, ...usable(highlight), ...highlighted,
        "-",
        ...longitudes,
        { label: "Bodies shown", items: views },
        { label: "Research charts", items: [...higher.slice(3), "-", custom, subDiv] },   // D-81, D-108, D-144: past the D buttons
      ];
    }
    return [
      ...longitudes,
      whenLagna,
      moveLagna,
      { label: "Show ashtakavarga of this chart", disabled: state.spec.kind !== "varga", onClick: () => { setAvVarga(state.spec.d ?? 1); go("Strengths", ["strengths", "av"]); } },
      { label: "Rasi chakra", checked: state.spec.kind === "varga" && state.spec.d === 1, onClick: () => set({ spec: { kind: "varga", d: 1 } }) },
      { label: "Bhava chakra or Chalit chakra", items: [...BHAVA_D.map((d) => ({ label: `Based on ${d === 1 ? "rasi (D-1)" : `D-${d}`}`, checked: state.spec.kind === "bhava" && state.spec.d === d, onClick: () => set({ spec: { kind: "bhava", d } }) })),
        "-" as const, { label: "Choose reference used for bhava/chalit chakra", onClick: () => setForm("bhava_ref") }] },
      ...chartMenu,
      { label: "Higher divisions", items: higher },
      custom,
      subDiv,
      "-",
      whenPlanet,
      relations,
      highlight,
      { label: "Aspect table with relationships", onClick: () => openWindow({ kind: "aspects", division: state.spec.kind === "varga" ? state.spec.d : 1 }) },
      copy,
      { label: "Choose a view (which bodies to show)", items: [...views, "-" as const,
        { label: "Optional bodies in standard view", items: OPTIONAL.map(([k, n, on]) => ({ label: n, checked: opts[k] ?? on, onClick: () => setOptional(k, !(opts[k] ?? on)) })) }] },
      displayMode,
      ...(single ? [] : [{ label: "Charts shown", items: ([2, 4, 6] as const).map((n) => ({ label: `${n} charts`, checked: charts === n, onClick: () => setCharts(n) })) }]),
      ...(single ? [] : [{ label: "Apply this view to every chart panel", onClick: () => setAllPanels({ view: state.view }) }]),
    ];
  };

  const onMenu = (e: React.MouseEvent) => {
    e.preventDefault();
    const t = e.target as Element;
    const rasi = t.closest("[data-sign]")?.getAttribute("data-sign");
    const label = t.closest("[data-body]")?.getAttribute("data-body") ?? null;
    // Starlight's North and East charts show their buttons in the centre on a right-click: the menu goes right beside them, level with their top
    const { chartStyle, display: dp } = useChart.getState();
    const style = i % 2 === 1 && dp.twoStyles ? dp.style2 : chartStyle;
    const r = (e.currentTarget.closest(".star-chart") ?? e.currentTarget).getBoundingClientRect();
    const at = starlight && (style === "north" || style === "east") ? { clientX: r.left + r.width * 0.73 + 4, clientY: r.top + r.height * 0.27 } : e;   // .star-quick: 46cqw by 46cqh, centred
    open(at, items(rasi == null ? null : Number(rasi), label), `${q.data?.title ?? "Chart"} menu`);
  };
  const onClick = (e: React.MouseEvent) => {
    if (!onPick) return;
    const t = e.target as Element;
    const at = t.closest("[data-sign]")?.getAttribute("data-sign");
    const sign = at == null ? null : Number(at);
    // the rasi's bhava chart: its box is a bhava, counted from the box that holds the chart's reference (the lagna's, or a graha's)
    const d = state.spec.kind === "varga" || state.spec.kind === "bhava" ? state.spec.d ?? 1 : undefined;
    const refNo = state.ref ?? Number(settings.bhava_ref ?? 2);      // 2 (moon) is the server's default
    const first = q.data && (markBody ? Number(Object.entries(q.data.boxes).find(([, v]) => v.some((x) => x.slice(0, 2) === markBody))?.[0] ?? q.data.lagna) : q.data.lagna);
    const bhava = state.spec.kind === "bhava" && d === 1 && sign != null && first != null ? bhavaOfBox(sign, first, !!settings.bhava_nodes_reversed && (refNo === 8 || refNo === 9)) : undefined;
    onPick({ body: t.closest("[data-body]")?.getAttribute("data-body") ?? null, sign, bhava, ref: bhava ? refNo : undefined, d });
  };
  // the box marked as the first house: the caller's body (a bhava chart's reference), else the lagna's
  const markLabel = markBody;
  const fromSign = markLabel && q.data ? Number(Object.entries(q.data.boxes).find(([, v]) => v.some((x) => x.slice(0, 2) === markLabel))?.[0] ?? q.data.lagna) : null;
  const focusBox = focus && q.data ? Object.entries(q.data.boxes).find(([, v]) => v.some((x) => x.slice(0, 2) === focus))?.[0] : undefined;     // "Sa" is in "SaR"
  // a bhava chart's grahas: degrees from the start of their box's sign, under 0° in the sign before it, 30° on in the one after
  // (Leo 2° in Cancer's box is 32°), so a box lists them in zodiac order; degText still shows the degrees in their own sign
  const fromBox = state.spec.kind === "bhava" && q.data?.longitudes ? Object.fromEntries(Object.entries(q.data.boxes).flatMap(([box, labels]) =>
    labels.flatMap((l) => { const t = l.replace(/R$/, ""), lon = q.data!.longitudes![t]; return lon == null || q.data!.degrees?.[t] == null ? [] : [[t, ((lon - 30 * Number(box) + 540) % 360) - 180]]; }))) : undefined;
  // Starlight's bhava chart: a graha whose house box is not its own sign says the sign after its degrees ("Ma 2°12' Ar")
  const moved = starlight && fromBox ? Object.fromEntries(Object.entries(fromBox).filter(([, d]) => d < 0 || d >= 30).map(([t]) => { const s = Math.floor(q.data!.longitudes![t] / 30) % 12; return [t, signName(s, SIGNS[s], display)]; })) : undefined;
  // a retrograde graha carries its R in every chart, not only the rasi (the server marks the rasi's); an arudha is not retrograde
  const withR = (t: string) => (q.data && !q.data.arudha_view && q.data.retro?.includes(t) ? t + "R" : t);
  return (
    <div className={"chart-panel" + (q.isPlaceholderData ? " stale" : "") + (onPick ? " pickable" : "")} onContextMenu={onMenu} onClick={onClick}>
      {!starMenu && <button className="panel-menu" aria-label={`${q.data?.title ?? "Chart"} menu`} onClick={(e) => open(e, items(null, null), "Chart menu")}>⋯</button>}
      {q.isError ? <p role="alert" className="error banner">{q.error.message}</p> : q.data && (
        <ChartGrid second={i % 2 === 1} title={starMenu && q.data.title === "Rasi" ? "Rasi D-1" : q.data.title} chartName={state.natalOnly || !mode ? (hideNatal ? undefined : "Natal Chart") : mode.title} note={q.data.arudha_view ? "Arudhas of Grahas" : undefined}
          lagnaSign={fromSign ?? q.data.lagna} cell={(s) => (q.data!.boxes[s] ?? []).map(withR)} shaded={new Set(shaded)} classes={classes} selected={selected ?? picked} interactive degrees={degrees || starlight ? (fromBox ? { ...q.data.degrees, ...fromBox } : q.data.degrees) : undefined} plain={starlight && !degrees} moved={moved} retro={starlight && display.retroRed ? q.data.retro : undefined} each={starlight} bare={bare} muntha={q.data.muntha} focus={focusBox === undefined ? undefined : Number(focusBox)} top={centre} />
      )}
      {classes && <p className="muted hint">{RELATION_NOTE}</p>}
      {node}
      {form === "custom" && <CustomDialog spec={state.spec} onClose={() => setForm(null)} onOk={(spec) => { set({ spec }); setForm(null); }} />}
      {form === "sub" && <SubDialog spec={state.spec} onClose={() => setForm(null)} onOk={(spec) => { set({ spec }); setForm(null); }} />}
      {form === "bhava_ref" && <DivisionDialog spec={state.spec} onClose={() => setForm(null)} onOk={(spec: ChartSpec, ref: number, rev: boolean, middle: boolean) => {
        saveSettings({ ...currentSettings(), bhava_ref: ref, bhava_nodes_reversed: rev, house_cusp_in_middle: middle });
        client.invalidateQueries();
        set({ spec });
        setForm(null);
      }} />}
    </div>
  );
}

/** The chart pane on the left of most screens: 2, 4 or 6 panels. */
export function ChartPane() {
  const { panels, charts, display } = useChart();
  return (
    <div className={`charts c${charts}`}>
      {panels.slice(0, charts).map((p, i) => <ChartPanelView key={i} i={i} state={p} degrees={display.degrees} />)}
    </div>
  );
}

// the sixteen in ascending order of the division, then the three higher ones past the Shashtyamsa
const MANY: PanelState[] = [1, 2, 3, 4, 7, 9, 10, 12, 16, 20, 24, 27, 30, 40, 45, 60, 81, 108, 144].map((d) => ({ spec: { kind: "varga", d }, view: "standard" }));

/** Chakras > Many Vargas: nineteen panels, each with its own picks (kept over a refresh); in Starlight Home's chart menu and a Rasi / Bhava toggle. */
export function ManyVargas() {
  const [saved, setPanels] = useKept<PanelState[]>("manyVargas", MANY);
  const panels = Array.isArray(saved) && saved.length === MANY.length ? saved : MANY;
  const { display, chartStyle } = useChart();
  const star = display.layout === "starlight";
  const [deg, setDeg] = useKept("manyVargas.degrees", false);     // its own longitudes switch: twenty small charts are off by default
  const change = (i: number, x: Partial<PanelState>) => setPanels(panels.map((q, k) => (k === i ? { ...q, ...x } : q)));
  return (
    <div className="many-vargas">
      {panels.map((p, i) => {
        const { kind, d } = p.spec;
        // the toggle sits atop the South chart's empty centre, the chart's name and title under it; North and East have none, so theirs is in the menu only
        const south = (i % 2 === 1 && display.twoStyles ? display.style2 : chartStyle) === "south";
        const toggle = star && south && (kind === "varga" || kind === "bhava") ? (
          <div className="mv-kind" role="group" aria-label="Rasi or bhava chart">
            <button type="button" aria-pressed={kind === "varga"} onClick={() => change(i, { spec: { kind: "varga", d } })}>Rasi</button>
            <button type="button" aria-pressed={kind === "bhava"} onClick={() => change(i, { spec: { kind: "bhava", d }, ref: p.ref ?? 0 })}>Bhava</button>
          </div>
        ) : undefined;
        return (
          <div key={i} className="mv-chart">
            {/* longitudes on: drawn as Home's charts are; off: the bodies in rows from the top */}
            <ChartPanelView i={i} centre={toggle} state={p} single starMenu={star} hideNatal={star} starlight={star && deg} degrees={star ? deg : undefined} onDegrees={setDeg} markBody={kind === "bhava" ? refAbbr(p.ref ?? 0) : undefined} onChange={(x) => change(i, x)} />
          </div>
        );
      })}
    </div>
  );
}
