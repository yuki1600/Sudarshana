/** The Starlight layout theme's Home: four charts in a 2×2 grid, tabs on top of the right half, the birth details beside Overview, and the tab's view below. */
import { Icon } from "./Icons";
import { useEffect, useState } from "react";
import { useQueries, useQuery, useQueryClient } from "@tanstack/react-query";
import { api, currentSettings, nowMoment, saveSettings, type Basics, type ChartPanel, type ChartSpec } from "./api";
import { degText } from "./chartGeometry";
import { CELL } from "./SouthGrid";
import { ChartPanelView, type ChartPick } from "./ChartPane";
import { ABBR_NAME, ChartHighlights, KeyInfo, NATAL_VIEWS, TableView } from "./Panels";
import { Yogas } from "./Strengths";
import { AvakahadaView } from "./Chakras";
import { AmsaRulers, Houses, Kp } from "./Views";
import { AspectTableView } from "./Windows";
import { openLore } from "./Lore";
import { StarSettings } from "./StarSettings";
import { SIGNS, SIGN_NAMES } from "./format";
import { useKept, useSaved, useSettings, useTopVarga } from "./hooks";
import { useChart, type PanelState } from "./store";
import { useMenu, type MenuEntry } from "./Menu";
import { retroMark } from "./names";
import { OneRowTabs, supOrd } from "./ui";

const GRAHAS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"];
// the four charts on the left, until changed from a chart's own menu: rasi and its bhava (chalit) chart side by side, navamsa and dasamsa below
// all sixteen vargas as one-click buttons in the centre of the rasi, navamsa and dasamsa charts, in place of their titles; the rasi's set
// the top pair (that varga on the left, its bhava (chalit) chart on the right), and the bhava chart has its reference buttons instead. Every varga is still in a chart's menu.
const VARGAS: [number, string][] = [[1, "Rasi"], [2, "Hora"], [3, "Drekkana"], [4, "Chaturthamsa"], [7, "Saptamsa"], [9, "Navamsa"], [10, "Dasamsa"], [12, "Dwadasamsa"],
  [16, "Shodasamsa"], [20, "Vimsamsa"], [24, "Siddhamsa"], [27, "Nakshatramsa"], [30, "Trimsamsa"], [40, "Khavedamsa"], [45, "Akshavedamsa"], [60, "Shashtyamsa"]];
// the bhava chart's reference (the bhava_ref setting: 0 lagna, 1 sun .. 9 ketu), lagna and moon first, then the other eight grahas
export const REFS: [number, string, string][] = [[0, "As", "Lagna"], [2, "Mo", "Moon"], [1, "Su", "Sun"], [3, "Ma", "Mars"], [4, "Me", "Mercury"], [5, "Ju", "Jupiter"],
  [6, "Ve", "Venus"], [7, "Sa", "Saturn"], [8, "Ra", "Rahu"], [9, "Ke", "Ketu"]];
// rasi and its bhava (chalit) chart on top, navamsa and dasamsa below
const CHARTS: PanelState[] = [{ spec: { kind: "varga", d: 1 }, view: "standard" }, { spec: { kind: "bhava", d: 1 }, view: "standard" },
  { spec: { kind: "varga", d: 9 }, view: "standard" }, { spec: { kind: "varga", d: 10 }, view: "standard" }];
const TABS = [{ id: "overview", name: "Overview" }, { id: "planets", name: "Grahas" }, { id: "houses", name: "Bhavas" },
  { id: "aspects", name: "Aspects" }, { id: "yogas", name: "Yogas" }, { id: "kp", name: "KP" }, { id: "amsas", name: "Amsas" }, { id: "speeds", name: "Speeds" },
  { id: "settings", name: "Options" }] as const;
const PINNED = new Set<string>(["amsas"]);     // stays on the row, just before "More", when the rest do not fit
// Key Info's views go under "More" (as "ki:<view>"), but not these: Starlight has them on the Speeds and Aspects tabs and on the graha's row and card,
// or not at all (Natal Longitudes); the other tara views are in the Moon's nava taras, which shows all four (Panels.tsx Taras), and the Mrityu Bhaga
// distances in the Pushkara list, which shows both (Panels.tsx Bhagas)
const TARA_VIEWS = new Set(["nava_lagna", "special_moon", "special_lagna"]);
// the temporary and compound friendships are under the natural ones (Panels.tsx Friendships); the sahamas are the shown chart's, a mode's (Tajaka …) when one is on, so no natal ones
const FOLDED: Partial<Record<string, string>> = { friends_temporal: "friends_natural", friends_compound: "friends_natural", natal_sahams: "sahams" };
// the chara karakas are the Grahas tab's karaka tags (the same scheme, server/basics.py), so they have no view of their own
const ELSEWHERE = new Set(["latitudes", "aspects", "combustion", "yuddha", "natal_longitudes", "mrityu", "karakas", ...TARA_VIEWS, ...Object.keys(FOLDED)]);
const RENAMED: Partial<Record<string, string>> = { nava_moon: "Taras from Moon and Lagna", pushkaras: "Pushkara and Mrityu Bhagas", friends_natural: "Friendships" };

// average daily motion, deg/day: in longitude the traditional figures (core_logic/mundane.py MEAN_DAILY_SPEEDS; the node's is backwards),
// in latitude the mean of its size over 1900-2100 (Swiss Ephemeris; the Sun and the true node stay on the ecliptic)
const MEAN_SPEED: [string, number, number][] = [["Sun", 0.9856, 0], ["Moon", 13.1764, 0.7564], ["Mars", 0.524, 0.0148], ["Mercury", 1.3833, 0.1294],
  ["Jupiter", 0.0831, 0.0021], ["Venus", 1.2, 0.0552], ["Saturn", 0.0335, 0.0021], ["Rahu", -0.0529, 0]];
const MEAN_LON = new Map(MEAN_SPEED.map(([n, lon]) => [n, lon]));
type Pace = "fast" | "slow" | "still";
/** Faster than its average longitude speed, slower, or stationary; by size alone, so a graha retrograde at more than its average is faster. */
function pace(name: string, speed: number): Pace | undefined {
  const mean = MEAN_LON.get(name);
  if (mean === undefined) return undefined;
  // shortcut: "stationary" is under a tenth of the average daily motion; no text gives a rule, tune if it marks too many or too few
  if (Math.abs(speed) < Math.abs(mean) / 10) return "still";
  return Math.abs(speed) > Math.abs(mean) ? "fast" : "slow";
}
const PaceMark = ({ p }: { p: Pace }) => <span className={`speed-mark pace ${p}`}>{p === "still" ? <i className="speed-dot" /> : <Icon name={p} />}</span>;
/** Speeds tab: the graha in bold, (R) when retrograde, with how far above (+) or below (−) its average it moves, and its Lon Speed with two arrow tips up (faster),
 *  down (slower) or a dot (stationary), both in the pace's colour; the other cells as the server sends them. */
const speedCell = (r: string[], k: number) => {
  const speed = parseFloat(r[2]), p = pace(r[0], speed), mean = MEAN_LON.get(r[0]);
  if (!p || mean === undefined || (k !== 0 && k !== 2)) return undefined;
  const pct = Math.round((Math.abs(speed / mean) - 1) * 100);
  const retro = speed < 0 && r[0] !== "Rahu" && r[0] !== "Ketu";     // the nodes always go backwards: no (R), as on the Grahas tab
  return k === 0
    ? <span className="speed-graha"><span className={`graha-name pace ${p}`}>{r[0]}</span>{retro && <span className="retro-r">(R)</span>}<span className={`speed-pct pace ${p}`}>{pct > 0 ? "+" : pct < 0 ? "−" : ""}{Math.abs(pct)}%</span></span>
    : <><span className={`pace ${p}`}>{r[2]}</span><PaceMark p={p} /></>;
};

function Speeds() {
  return (
    <section className="pane speeds">
      <TableView view="latitudes" cell={speedCell} />
      <div className="scroll tall">
        <ul className="speed-key">
          <li><PaceMark p="fast" /> Faster than average</li>
          <li><PaceMark p="slow" /> Slower than average</li>
          <li><PaceMark p="still" /> Stationary</li>
          <li className="muted">(longitude speed only)</li>
        </ul>
        <table className="points wrap speed-means">
          <thead><tr><th>Graha</th><th>Average Lon Speed</th><th>Average Lat Speed</th></tr></thead>
          <tbody>{MEAN_SPEED.map(([n, lon, lat]) => <tr key={n}><td><span className="graha-name">{n}</span></td><td>{lon.toFixed(4)} deg/day</td><td>{lat.toFixed(4)} deg/day</td></tr>)}</tbody>
        </table>
      </div>
    </section>
  );
}

/** The bhava chart's reference (the bhava_ref setting), shared by Home's bhava chart, the Houses tab and the transit chart. */
export function useBhavaRef() {
  const client = useQueryClient();
  const ref = Number(useSettings().bhava_ref ?? 2);   // 2 (moon) is the server's default
  const setRef = (r: number) => { saveSettings({ ...currentSettings(), bhava_ref: r }); client.invalidateQueries(); };
  return [ref, setRef] as const;
}

/** The four charts' picks, shared live: the right half's tabs follow the top left chart's varga. */
function useCharts() {
  const [saved, save] = useKept<PanelState[]>("starCharts3", CHARTS);
  return [Array.isArray(saved) && saved.length === CHARTS.length ? saved : CHARTS, save] as const;
}

/** The four charts two by two, each with its quick varga picker: the left half of Home and of every chart tab in Starlight; the choices are shared. */
export function StarCharts({ onPick, picked, focus }: { onPick?: (p: ChartPick) => void; picked?: string | null; focus?: string }) {
  const [panels, save] = useCharts();
  const display = useChart((s) => s.display);
  const change = (i: number, p: Partial<PanelState>) => save(panels.map((x, k) => (k === i ? { ...x, ...p } : x)));
  const [ref, setRef] = useBhavaRef();
  const setTop = (d: number) => save([{ ...panels[0], spec: { kind: "varga", d } }, { ...panels[1], spec: { kind: "bhava", d } }, ...panels.slice(2)]);
  // North and East charts have no empty centre box: their buttons come up there only on a right-click, along with the chart's menu
  const chartStyle = useChart((s) => s.chartStyle);
  const hidden = (i: number) => ["north", "east"].includes(i % 2 === 1 && display.twoStyles ? display.style2 : chartStyle);
  const [shown, setShown] = useState<number | null>(null);
  useEffect(() => {
    if (shown === null) return;
    const away = (e: MouseEvent) => { if (!(e.target as Element).closest?.(".star-quick")) setShown(null); };
    const key = (e: KeyboardEvent) => { if (e.key === "Escape") setShown(null); };
    document.addEventListener("mousedown", away);
    document.addEventListener("keydown", key);
    return () => { document.removeEventListener("mousedown", away); document.removeEventListener("keydown", key); };
  }, [shown]);
  // a right-click anywhere on a chart (its D buttons, its edge) brings up the chart's own menu
  // linked: a lower chart is its varga of the top chart's (D-9 of D-24, the Grahas tab's "D9 of D24"); its own pick stays as chosen
  const top = panels[0].spec;
  const shownAs = (p: PanelState, i: number): PanelState => display.linkCharts && i >= 2 && p.spec.kind === "varga" && top.kind === "varga" && top.d && top.d !== 1 && p.spec.d
    ? { ...p, spec: { kind: "sub", m: top.d, n: p.spec.d } } : p;
  const menuHere = (e: React.MouseEvent<HTMLDivElement>, i: number) => {
    if (hidden(i)) setShown(i);
    if ((e.target as Element).closest(".chart-panel")) return;     // the chart's menu came up already
    e.preventDefault();
    e.currentTarget.querySelector(".chart-panel")?.dispatchEvent(new MouseEvent("contextmenu", { bubbles: true, cancelable: true, clientX: e.clientX, clientY: e.clientY }));
  };
  return (
    <div className={display.signLabels ? "star-charts" : "star-charts no-signs"}>
      {panels.map((p, i) => (
        <div key={i} className={hidden(i) ? "star-chart pop" : "star-chart bare"} onContextMenu={(e) => menuHere(e, i)}>
          {hidden(i) && shown !== i ? null : i === 1 ? (
            <div className="star-quick star-ref" role="group" aria-label="Reference of the bhava chart">
              <b>Bhava/Chalit</b>
              {REFS.map(([r, a, n]) => (
                <button key={r} type="button" title={`Bhavas from ${n}`} aria-pressed={ref === r} onClick={() => { setRef(r); setShown(null); }}>{a}</button>
              ))}
            </div>
          ) : (
            <div className="star-quick" role="group" aria-label={i === 0 ? "Varga of the top two charts" : `Chart ${i + 1} varga`}>
              {VARGAS.map(([d, n]) => (
                <button key={d} type="button" title={n} aria-pressed={p.spec.d === d && (p.spec.kind === "varga" || p.spec.kind === "bhava")}
                  onClick={() => { if (i === 0) setTop(d); else change(i, { spec: { kind: "varga", d } }); setShown(null); }}>D{d}</button>
              ))}
            </div>
          )}
          <ChartPanelView i={i} single hideNatal degrees={display.degrees} starlight markBody={p.spec.kind === "bhava" ? REFS.find(([r]) => r === ref)?.[1] : undefined} state={shownAs(p, i)} onChange={(x) => change(i, x)} onPick={onPick} picked={picked} focus={focus} />
        </div>
      ))}
    </div>
  );
}

/** The left half of Starlight's chart tabs: the four charts, or the one transit square while a transit chart is cast. ``focus``: the
 *  abbreviation of the graha open on the Grahas tab, whose box each chart tints. */
export function LeftCharts({ focus }: { focus?: string }) {
  const { mode, activeChartId } = useChart();
  // a graha clicked in a chart (Su to Ke; "SaR" is Saturn) opens in the lore panel, its Strengths the Grahas tab's card; a box (the lagna's
  // label too) opens its rashi, read in that chart's varga, and a box of the rasi's bhava chart the bhava it holds
  const pick = ({ body, sign, bhava, ref, d }: ChartPick) => {
    const ab = body?.replace(/R$/, "") ?? "", g = ABBR_NAME[ab];
    if (g && g !== "Lagna") return openLore({ kind: "graha", n: ab });
    if (sign == null) return;
    openLore(bhava ? { kind: "bhava", n: bhava, ref } : { kind: "rashi", n: sign + 1, d: d ?? 0 });     // d 0: a custom or sub chart, read in no varga
  };
  return mode?.title === "Transit" ? <TransitChart key={activeChartId} /> : <StarCharts onPick={pick} focus={focus} />;
}

const pc = (v: number) => `${v / 10}%`;   // the transit square is worked out on a 1000-unit side

/** Starlight's Transits tab: one South Indian square, natal grahas (ink) and transit grahas (purple) side by side in each box, every graha (outer ones, maandi and gulika too)
 *  with its degrees, the other points small at the foot; today's sky until a transit moment is shown. In the centre: rasi or bhava, the varga, and the bhava chart's reference. */
export function TransitChart() {
  const { natal, birth, mode, optional, activeChartId } = useChart();
  const [now] = useState(() => ({ ...natal!, ...nowMoment(), adjust: undefined }));
  const transit = mode?.title === "Transit" ? birth! : now;
  // each open chart keeps its own varga and rasi/bhava pick (App remounts this per chart, so the keys are read afresh)
  const [saved, save] = useSaved<string>(`transitWheelD.${activeChartId}`, "1");
  const d = Number(saved) || 1;
  const [kind, setKind] = useSaved<"varga" | "bhava">(`transitKind.${activeChartId}`, "bhava");
  const [ref, setRef] = useBhavaRef();
  const qs = useQueries({ queries: [natal!, transit].map((chart, i) => {
    const spec: ChartSpec = { kind, d }, houses = kind === "bhava" && i ? natal! : undefined;   // transit grahas go in the natal houses
    return { queryKey: ["panel", chart, spec, "standard", optional, houses], queryFn: () => api.panel(chart, spec, "standard", optional, houses), placeholderData: (p?: ChartPanel) => p };
  }) });
  const failed = qs.find((q) => q.isError);
  const square = qs.map((q) => q.data);
  const W = 250;   // a box's side, on a 1000-unit square
  return (
    <div className={"star-chart transit-square" + (qs.some((q) => q.isPlaceholderData) ? " stale" : "")}>
      <div className="ts-square">
        <div className="ts-centre">
          <div className="seg ts-kind" role="tablist" aria-label="Rasi or bhava">
            {(["varga", "bhava"] as const).map((k) => <button key={k} type="button" role="tab" aria-selected={kind === k} onClick={() => setKind(k)}>{k === "varga" ? "Rasi" : "Bhava"}</button>)}
          </div>
          <div className="star-quick" role="group" aria-label="Varga">
            {VARGAS.map(([v, n]) => <button key={v} type="button" title={n} aria-pressed={d === v} onClick={() => save(String(v))}>D{v}</button>)}
          </div>
          <hr className="ts-rule" />
          {/* always there, so the centre keeps its shape; only the bhava chart has a reference */}
          <div className="star-quick ts-refs" role="group" aria-label="Reference of the bhava chart">
            {REFS.map(([r, a, n]) => <button key={r} type="button" title={kind === "bhava" ? `Bhavas from ${n}` : "Choose Bhava to count the bhavas from a graha"} disabled={kind !== "bhava"} aria-pressed={ref === r} onClick={() => setRef(r)}>{a}</button>)}
          </div>
        </div>
        {failed && <p role="alert" className="error banner">{failed.error!.message}</p>}
        <svg width="100%" height="100%" className="grid" role="img" aria-label={`Transit chart, ${kind === "bhava" ? "bhava" : "rasi"} D-${d}: natal grahas on the left of each box, transit grahas on the right`}>
          {CELL.map(([r, c], sign) => {
            const x = c * W, y = r * W;
            return (
              <g key={sign}>
                <rect x={pc(x)} y={pc(y)} width={pc(W)} height={pc(W)} className="ts-box"><title>{SIGN_NAMES[sign]}</title></rect>
                <text x={pc(x + W - 12)} y={pc(y + 38)} textAnchor="end" className="ts-sign">{SIGNS[sign]}</text>
                {square.map((p, i) => {
                  const all = p?.boxes[sign] ?? [], main = all.filter((t) => p?.longitudes?.[t.replace(/R$/, "")] != null), rest = all.filter((t) => !main.includes(t));
                  const strip = Array.from({ length: Math.ceil(rest.length / 3) }, (_, j) => rest.slice(j * 3, j * 3 + 3).join(" "));   // the other points, three to a line at the foot
                  const step = Math.min(34, (W - 84 - strip.length * 24) / Math.max(1, main.length));   // a crowded box packs its lines closer
                  const tone = i ? "ts-transit" : "ts-natal", cx = pc(i ? x + W - 10 : x + 10), anchor = i ? "end" : "start";   // natal flush left, transit flush right
                  return [...main.map((t, k) => {
                    const lon = p!.longitudes![t.replace(/R$/, "")], own = Math.floor(lon / 30);
                    const away = own !== sign ? ` ${SIGNS[own]}` : "";   // a bhava box holding a graha of another sign names its sign
                    return <text key={`${i}${t}`} x={cx} y={pc(y + 76 + k * step)} textAnchor={anchor} className={`ts-body ${tone}`}>{retroMark(t)}<tspan className="deg"> {degText(lon % 30)}{away}</tspan></text>;
                  }), ...strip.map((line, j) => <text key={`${i}s${j}`} x={cx} textAnchor={anchor} y={pc(y + W - 16 - (strip.length - 1 - j) * 24)} className={`ts-body ts-point ${tone}`}>{line}</text>)];
                })}
              </g>
            );
          })}
          {square[0] && (() => {     // the natal lagna's box; a bhava chart's, its reference's, as Home's bhava chart
            const mark = kind === "bhava" ? REFS.find(([r]) => r === ref)?.[1] : undefined;
            const at = Number(Object.entries(square[0].boxes).find(([, v]) => v.some((x) => x.slice(0, 2) === mark))?.[0] ?? square[0].lagna);
            const [r, c] = CELL[at];
            return <rect x={pc(c * W + 2)} y={pc(r * W + 2)} width={pc(W - 4)} height={pc(W - 4)} className="lagna-box" />;
          })()}
          <rect x={pc(W)} y={pc(W)} width={pc(2 * W)} height={pc(2 * W)} className="ts-hub" />
        </svg>
      </div>
    </div>
  );
}

export function Starlight({ b }: { b: Basics }) {
  const birth = useChart((s) => s.birth)!;
  const meta = useChart((s) => s.meta);
  const [saved, setTab] = useSaved<string>("starTab", "overview");
  // a tab saved before Dasa, Ashtakavarga and Strengths left Home, or a view no longer under More, opens Overview; a tara view, all the taras; Mrityu Bhaga, the Pushkara list;
  // a folded friendship or the natal sahamas, the box that holds them; the chara karakas, the Grahas tab
  const tab = TABS.some((t) => t.id === saved) || saved === "avakahada" || (saved.startsWith("ki:") && !ELSEWHERE.has(saved.slice(3))) ? saved : TARA_VIEWS.has(saved.slice(3)) ? "ki:nava_moon" : saved === "ki:mrityu" ? "ki:pushkaras" : saved === "ki:karakas" ? "planets"
    : FOLDED[saved.slice(3)] ? "ki:" + FOLDED[saved.slice(3)] : "overview";
  const tables = useQuery({ queryKey: ["tables"], queryFn: api.tables });
  const more = [...(tables.data?.key_info ?? []), ...NATAL_VIEWS].filter((v) => !ELSEWHERE.has(v.key)).map((v) => ({ id: "ki:" + v.key, name: RENAMED[v.key] ?? v.name }))
    .concat({ id: "avakahada", name: "Avakahada" });     // the Moon's pada and its name syllable (once the Chakras page's)
  const varga = useTopVarga();
  const keyRows = useQuery({ queryKey: ["keyInfo", birth, varga], queryFn: () => api.keyInfo(birth, varga), placeholderData: (p) => p });
  const rows = keyRows.data ?? [];
  const [opened] = useKept<string>("grahaOpen", "");     // kept in step with the Grahas tab (keep in hooks.ts)
  return (
    <div className="star">
      <div className="star-main">
        <LeftCharts focus={tab === "planets" && opened ? opened.slice(0, 2) : undefined} />
        <div className="star-right">
          <div className="star-tabbar">
            <OneRowTabs tabs={TABS} pinned={PINNED} more={more} value={tab} onChange={setTab} label="Chart views" />
          </div>
          <section className="star-bottom">
        <div className="star-body" data-tab={tab}>
          {/* birth details belong to Overview and scroll with it */}
          {tab === "overview" ? (
            <>
              <section className="pane"><ChartHighlights sensitive division={varga} rows={rows.filter((r) => r.name === "Lagna" || GRAHAS.includes(r.name))} /></section>
              <aside className="pane star-inspector" aria-label="Inspector">
                <Inspector b={b} place={[meta.city, meta.state, meta.country].filter(Boolean).join(", ")} />
              </aside>
            </>
          ) : tab === "planets" || tab.startsWith("ki:") ? <KeyInfo b={b} bare show={tab.startsWith("ki:") ? tab.slice(3) : undefined} />
            : tab === "houses" ? <Houses shared />
                : tab === "aspects" ? <section className="pane pad"><AspectTableView key={varga} division={varga} split /></section>
                    : tab === "yogas" ? <Yogas />
                      : tab === "kp" ? <Kp />
                      : tab === "amsas" ? <AmsaRulers />
                        : tab === "settings" ? <StarSettings /> : tab === "avakahada" ? <AvakahadaView /> : <Speeds />}
        </div>
          </section>
        </div>
      </div>
    </div>
  );
}

/** Which rows of a list of birth details show, kept under ``key`` (``init`` hidden at first): a right-click on the list opens a
 *  menu of every name in ``names`` to tick, several at once (the menu stays open); ``menu`` entries head it. */
export function useShownRows(key: string, init: string[], names: string[], menu: MenuEntry[] = []) {
  const [saved, save] = useSaved<string>(key, JSON.stringify(init));
  const hiddenOf = (v: string): string[] => { try { const h = JSON.parse(v); return Array.isArray(h) ? h : []; } catch { return []; } };
  const hidden = hiddenOf(saved);
  const { open, node } = useMenu();
  const items = (h: string[], at: { clientX: number; clientY: number }): MenuEntry[] => [...menu, "-", ...names.map((k): MenuEntry => ({
    label: k, checked: !h.includes(k), keep: true,
    onClick: () => { const next = h.includes(k) ? h.filter((x) => x !== k) : [...h, k]; save(JSON.stringify(next)); open(at, items(next, at), "Birth details shown"); },
  }))];
  const onContextMenu = (e: React.MouseEvent) => { e.preventDefault(); const at = { clientX: e.clientX, clientY: e.clientY }; open(at, items(hidden, at), "Birth details shown"); };
  return { hidden, onContextMenu, node };
}

/** The birth details, beside Overview; a right-click picks which of them show (several at once, the menu stays open). ``lead`` rows come first, always shown;
 *  ``menu`` entries head the right-click menu; ``tail`` rows come last, always shown. */
export function Inspector({ b, lead = [], tail = [], place, menu = [] }: { b: Basics; lead?: [string, string][]; tail?: [string, string][]; place?: string; menu?: MenuEntry[] }) {
  const { hidden, onContextMenu, node } = useShownRows("starInspectorHidden", ["Altitude"], b.core.map(([k]) => k), menu);
  // the ayanamsa's name beside its value, as the A button of the top bar names it
  const settings = useSettings();
  const schema = useQuery({ queryKey: ["settingsSchema"], queryFn: api.settingsSchema, staleTime: Infinity });
  const ay = schema.data?.flatMap((g) => g.options).find((o) => o.key === "ayanamsa");
  const ayName = ay?.choices?.find((c) => c.value === (settings.ayanamsa ?? ay.default))?.label.replace(/\s*ayanamsa/gi, "").replace(/\s*\([^)]{12,}\)/, "");     // the row already says ayanamsa; a long aside like "(Spica in the middle ...)" goes
  return (
    <>
      <dl className="core" aria-label="Birth details"
        onContextMenu={onContextMenu}>
        {lead.map(([k, v]) => <div key={k} className="lead"><dt>{k}</dt><dd>{supOrd(v)}</dd></div>)}
        {b.core.filter(([k]) => !hidden.includes(k)).map(([k, v]) => <div key={k}><dt>{k}</dt><dd>{supOrd(k === "Ayanamsa" && ayName ? `${v} (${ayName})` : v)}{k === "Place" && place && <><br /><span translate="no">{place}</span></>}</dd></div>)}
        {tail.map(([k, v]) => <div key={k} className="lead"><dt>{k}</dt><dd>{v}</dd></div>)}
      </dl>
      {node}
    </>
  );
}
