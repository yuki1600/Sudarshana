import { useQuery } from "@tanstack/react-query";
import { Component, type ReactNode } from "react";
import { api, type TraditionExtra, type TraditionPart } from "./api";
import { ChartGrid } from "./ChartGrid";
import { formatDateOrdinal, formatTime12, SIGN_NAMES, SIGNS } from "./format";
import { useKept, useSaved } from "./hooks";
import { KEYS, shown, signName } from "./names";
import { useChart, type Display } from "./store";
import { Loaded, OneRowTabs, Retro } from "./ui";
import * as M from "./traditionsMath";

/* The Traditions tab: what the XALEN Ephemeris engine offers beyond Jyotish (server/traditions.py). Starlight only: its left
   half (TraditionsLeft) draws the chart of the sub tab and view open, its right half (Traditions) the tables. */

const TABS = [{ id: "western", name: "Western" }, { id: "chinese", name: "Chinese" }, { id: "world", name: "World" },
  { id: "iching", name: "I Ching" }, { id: "numerology", name: "Numerology" }, { id: "lalkitab", name: "Lal Kitab" }] as const;
type Tab = (typeof TABS)[number]["id"];
const PINNED = new Set<string>(TABS.map((t) => t.id));

const VIEWS = {
  western: [["positions", "Positions"], ["aspects", "Aspects"], ["dignities", "Dignities"], ["lots", "Lots"], ["timelords", "Time lords"],
    ["midpoints", "Midpoints"], ["declinations", "Declinations"], ["progressions", "Progressions"], ["harmonics", "Harmonics"], ["stars", "Stars and points"]],
  chinese: [["bazi", "BaZi"], ["ziwei", "Zi Wei Dou Shu"], ["flying", "Flying Stars"], ["bazhai", "Ba Zhai"], ["qimen", "Qi Men Dun Jia"]],
  world: [["saju", "Saju (Korea)"], ["ninestar", "Nine Star Ki (Japan)"], ["mahabote", "Mahabote (Burma)"], ["tibetan", "Tibetan year"],
    ["maya", "Maya calendar"], ["aztec", "Aztec day sign"], ["egyptian", "Egyptian decans"], ["celtic", "Celtic tree"], ["persian", "Persian periods"]],
} as const;
type Viewed = keyof typeof VIEWS;

/* eslint-disable @typescript-eslint/no-explicit-any */
type J = any;

const ABBR: Record<string, string> = { Sun: "Su", Moon: "Mo", Mercury: "Me", Venus: "Ve", Mars: "Ma", Jupiter: "Ju", Saturn: "Sa", Uranus: "Ur",
  Neptune: "Ne", Pluto: "Pl", "North Node": "Ra", Chiron: "Ch", Lilith: "Li", Asc: "As", MC: "Mc" };
const HOUSE_NAMES: Record<string, string> = { placidus: "Placidus", koch: "Koch", whole_sign: "Whole sign", equal: "Equal", porphyry: "Porphyry",
  regiomontanus: "Regiomontanus", campanus: "Campanus", morinus: "Morinus", alcabitius: "Alcabitius", topocentric: "Topocentric (Polich-Page)",
  meridian: "Meridian", vehlow: "Vehlow", sripati: "Sripati", krusinski: "Krusinski-Pisa", sunshine: "Sunshine (Makransky)" };
const BA_ZHAI = [["sheng_qi", "Sheng Qi", "prosperity"], ["tian_yi", "Tian Yi", "health"], ["yan_nian", "Yan Nian", "relationships"], ["fu_wei", "Fu Wei", "stability"],
  ["huo_hai", "Huo Hai", "mishaps"], ["liu_sha", "Liu Sha", "six killings"], ["wu_gui", "Wu Gui", "five ghosts"], ["jue_ming", "Jue Ming", "total loss"]] as const;

/** 23°51′ Ge */
const deg = (lon: number) => {
  const x = ((lon % 360) + 360) % 360, s = Math.floor(x / 30), d = Math.floor(x % 30), m = Math.floor(((x % 30) - d) * 60);
  return `${d}°${String(m).padStart(2, "0")}′ ${SIGNS[s]}`;
};
/** "1990-06-15T10:30" -> 15th June 1990, with the time when ``time`` */
const when = (iso: string, time = false) => {
  const [y, m, d] = iso.slice(0, 10).split("-").map(Number), [hh, mm] = iso.slice(11, 16).split(":").map(Number);
  return formatDateOrdinal(y, m, d) + (time ? `, ${formatTime12(hh + mm / 60)}` : "");
};
const yesNo = (v: boolean) => (v ? "✓" : "");
/** Now as a year and its fraction, as the Persian periods' bounds are given (1869.75). */
const nowYear = () => 1970 + Date.now() / (365.2425 * 864e5);
/** A table's mark for a period, as the Dasas tree marks its own: "running" for one that holds now, "now" for the deepest of them. */
const runningNow = (start: string, end: string, deepest: boolean, at = new Date().toISOString().slice(0, 16)) =>
  start <= at && at < end ? (deepest ? "now" : "running") : undefined;

function useOptions() {
  const meta = useChart((s) => s.meta), chartName = useChart((s) => s.name);
  const [system, setSystem] = useKept<string>("traditions.houses", "placidus");
  const [male, setMale] = useKept<boolean | null>("traditions.male", null);     // null: the chart's gender, male when unknown
  const [person, setPerson] = useKept<string | null>("traditions.person", null);   // null: the chart's name
  const [chaldean, setChaldean] = useKept<boolean>("traditions.chaldean", false);
  return { system, setSystem, male: male ?? meta?.gender !== 2, setMale, person: person ?? chartName, setPerson, chaldean, setChaldean };
}

/** One sub tab's data, shared by the two halves (one query for both). */
function useData(part: TraditionPart) {
  const birth = useChart((s) => s.birth);
  const o = useOptions();
  const extra: TraditionExtra = part === "western" ? { house_system: o.system } : part === "chinese" || part === "world" ? { male: o.male }
    : part === "numerology" ? { person: o.person, chaldean: o.chaldean } : {};
  // the last result stays up only while the same sub tab recalculates (a new house system, a time step): another sub tab's
  // data is a different shape, and drawing the Chinese chart from the Western one's blanked the page
  return useQuery({ queryKey: ["traditions", part, birth, extra], queryFn: () => api.traditions<J>(birth!, part, extra), enabled: !!birth,
    placeholderData: (prev, prevQuery) => (prevQuery?.queryKey[1] === part ? prev : undefined) });
}

const useTab = () => useSaved<Tab>("traditions", "western");
/** Lal Kitab: the natal chart or the year's (Varshphal) on the left, picked on the right. */
const useAnnual = () => useKept<boolean>("traditions.lalkitab.annual", false);
function useView<K extends Viewed>(tab: K) {
  return useKept<string>("traditions." + tab, VIEWS[tab][0][0]);
}

/** A view that cannot be drawn says so in its own half, instead of taking the page down with it; ``key`` it by the view. */
class Guard extends Component<{ children: ReactNode }, { error: Error | null }> {
  state = { error: null as Error | null };
  static getDerivedStateFromError(error: Error) { return { error }; }
  render() {
    return this.state.error ? <p role="alert" className="error banner">This view could not be drawn: {this.state.error.message}</p> : this.props.children;
  }
}

// ---------------------------------------------------------------------------------------------------------------------
// Small pieces
// ---------------------------------------------------------------------------------------------------------------------

/** ``mark``: a row's class, "running" or "now" for the period running now. */
function Table({ head, rows, wrap, mark }: { head: string[]; rows: ReactNode[][]; wrap?: boolean; mark?: (i: number) => string | undefined }) {
  return (
    <table className={wrap ? "points wrap" : "points"}>
      <thead><tr>{head.map((h, i) => <th key={i}>{h}</th>)}</tr></thead>
      <tbody>{rows.map((r, i) => <tr key={i} className={mark?.(i)} aria-current={mark?.(i) ? true : undefined}>{r.map((c, k) => <td key={k}>{c}</td>)}</tr>)}</tbody>
    </table>
  );
}

function Facts({ rows }: { rows: [string, ReactNode][] }) {
  return <table className="points wrap trad-facts"><tbody>{rows.map(([k, v]) => <tr key={k}><td>{k}</td><td>{v}</td></tr>)}</tbody></table>;
}

function Box({ title, note, children }: { title?: string; note?: ReactNode; children: ReactNode }) {
  return (
    <section className="pane trad-box">
      {title && <header className="pane-head"><h2>{title}</h2>{note && <span className="muted">{note}</span>}</header>}
      <div className="scroll">{children}</div>
    </section>
  );
}

function Tiles<K extends Viewed>({ tab, extra }: { tab: K; extra?: ReactNode }) {
  const [view, setView] = useView(tab);
  return (
    <section className="pane trad-tiles">
      <div className="view-tiles" role="group" aria-label="Views">
        {VIEWS[tab].map(([k, label]) => <button key={k} type="button" aria-pressed={view === k} onClick={() => setView(k)}>{label}</button>)}
      </div>
      {extra && <div className="trad-options">{extra}</div>}
    </section>
  );
}

function GenderPick() {
  const o = useOptions();
  return (
    <div className="mv-kind" role="group" aria-label="Gender" data-tip="The luck periods run forward or back by gender, and Ba Zhai's Kua number takes it">
      <button type="button" aria-pressed={o.male} onClick={() => o.setMale(true)}>Male</button>
      <button type="button" aria-pressed={!o.male} onClick={() => o.setMale(false)}>Female</button>
    </div>
  );
}

// ---------------------------------------------------------------------------------------------------------------------
// The charts (left half)
// ---------------------------------------------------------------------------------------------------------------------

/** Retrograde, as the app marks it; never the node, whose mean motion is always backward (the charts leave Rahu unmarked too). */
const retro = (b: { name: string; retrograde: boolean }) => b.retrograde && b.name !== "North Node";
/** A body's label in a chart: the app's grahas as every chart writes them (names.ts shown), the rest (Chiron, Lilith) by their two letters. */
const bodyLabel = (name: string, retro: boolean, display: Display) => {
  const ab = ABBR[name] ?? name.slice(0, 2);
  return KEYS.includes(ab) ? shown(ab + (retro ? "R" : ""), display) : ab + (retro ? "(R)" : "");
};

const MAJOR: Record<string, string> ={ Opposition: "hard", Square: "hard", Trine: "soft", Sextile: "soft" };

/** The Western wheel: the ascendant on the left, the signs round the rim, the house cusps, the bodies and the major aspects. */
function WesternWheel({ w }: { w: J }) {
  const display = useChart((s) => s.display);
  const C = 200, asc: number = w.houses.ascendant, mc: number = w.houses.mc;
  const ang = (l: number) => M.wheelAngle(l, asc);
  const line = (a: number, r1: number, r2: number) => { const [x1, y1] = M.polar(C, C, r1, a), [x2, y2] = M.polar(C, C, r2, a); return { x1, y1, x2, y2 }; };
  const bodies: J[] = w.bodies;
  const at = M.spread(bodies.map((b) => ang(b.lon)), 8);
  const lon = Object.fromEntries(bodies.map((b) => [b.name, b.lon]));
  const aspects = (w.aspects as J[]).filter((a) => MAJOR[a.aspect_type] && lon[a.body1] !== undefined && lon[a.body2] !== undefined);
  return (
    // the viewBox runs past the rim, so the As and Mc outside it are drawn whole (the ascendant sits at the far left)
    <svg className="trad-wheel" viewBox="-16 -16 432 432" role="img" aria-label="Western chart wheel">
      <circle cx={C} cy={C} r={190} className="rim" /><circle cx={C} cy={C} r={162} className="rim" /><circle cx={C} cy={C} r={72} className="rim" />
      {SIGNS.map((s, i) => {
        const [x, y] = M.polar(C, C, 176, ang(i * 30 + 15));
        return <g key={s}><line {...line(ang(i * 30), 162, 190)} className="cut" />
          <text x={x} y={y} className="sign" textAnchor="middle" dominantBaseline="central">{signName(i, s, display)}<title>{SIGN_NAMES[i]}</title></text></g>;
      })}
      {(w.houses.cusps as number[]).map((c, i) => {
        const next = w.houses.cusps[(i + 1) % 12], mid = c + (((next - c) % 360) + 360) % 360 / 2;
        const [x, y] = M.polar(C, C, 82, ang(mid));
        return <g key={i}><line {...line(ang(c), 72, 162)} className={i % 3 === 0 ? "axis" : "cusp"} />
          <text x={x} y={y} className="house" textAnchor="middle" dominantBaseline="central">{i + 1}</text></g>;
      })}
      {[["As", asc], ["Mc", mc]].map(([n, l]) => { const [x, y] = M.polar(C, C, 202, ang(l as number)); return <text key={n} x={x} y={y} className="angle" textAnchor="middle" dominantBaseline="central">{shown(n as string, display)}</text>; })}
      {aspects.map((a, i) => { const [x1, y1] = M.polar(C, C, 70, ang(lon[a.body1])), [x2, y2] = M.polar(C, C, 70, ang(lon[a.body2]));
        return <line key={i} x1={x1} y1={y1} x2={x2} y2={y2} className={"aspect " + MAJOR[a.aspect_type]}><title>{`${a.body1} ${a.aspect_type.toLowerCase()} ${a.body2}`}</title></line>; })}
      {bodies.map((b, i) => {
        const [x, y] = M.polar(C, C, 142, at[i]);
        return <g key={b.name}><line {...line(ang(b.lon), 156, 162)} className="tick" />
          {/* as the charts write a graha: its short name in Settings > Language's, a retrograde one red with its (R) */}
          <text x={x} y={y} className={retro(b) ? "body retro" : "body"} textAnchor="middle" dominantBaseline="central">{bodyLabel(b.name, retro(b), display)}
            <title>{`${b.name} ${deg(b.lon)}${retro(b) ? ", retrograde" : ""}`}</title></text></g>;
      })}
    </svg>
  );
}

/** Four pillars, the year on the right as they are read: each its stem over its branch. */
function Pillars({ pillars, korean }: { pillars: { label: string; stem: string; branch: string; stemEl?: string; branchEl?: string }[]; korean?: boolean }) {
  return (
    <div className="trad-pillars">
      {pillars.map((p) => {
        const s = M.stemIndex(p.stem, korean), b = M.branchIndex(p.branch, korean);
        return (
          <div key={p.label} className="pillar">
            <span className="muted">{p.label}</span>
            <strong className="glyph" translate="no">{M.STEM_HANZI[s] ?? "?"}</strong>
            <span>{korean ? `${M.SAJU_STEM_HANGUL[s] ?? ""} ${p.stem}` : p.stem}{p.stemEl ? ` · ${p.stemEl}` : ""}</span>
            <strong className="glyph" translate="no">{M.BRANCH_HANZI[b] ?? "?"}</strong>
            <span>{korean ? `${M.SAJU_BRANCH_HANGUL[b] ?? ""} ${p.branch.replace(/_$/, "")}` : p.branch}{p.branchEl ? ` · ${p.branchEl}` : ""}</span>
            <span className="muted">{M.BRANCH_ANIMALS[b] ?? ""}</span>
          </div>
        );
      })}
    </div>
  );
}

/** A Lo Shu square, South at the top: each cell's text, its direction, and which one is marked. */
function LoShu({ cell, here, centre }: { cell: (row: number, col: number) => ReactNode; here?: (row: number, col: number) => boolean; centre?: ReactNode }) {
  return (
    <div className="trad-loshu">
      {M.LO_SHU.map((row, r) => row.map((_, c) => (
        <div key={`${r}${c}`} className={here?.(r, c) ? "cell here" : "cell"}>
          <span className="dir">{M.LO_SHU_DIRECTIONS[r][c] || (centre ? "" : "Centre")}</span>
          {r === 1 && c === 1 && centre ? centre : cell(r, c)}
        </div>
      )))}
    </div>
  );
}

/** The twelve palaces of Zi Wei Dou Shu round a 4 x 4 square, the Life palace marked; the centre names the chart. */
function ZiWei({ z }: { z: J }) {
  const minor: Record<number, string[]> = {};
  for (const [star, at] of z.minor as [string, number][]) (minor[at] ??= []).push(M.spaced(star));
  return (
    <div className="trad-ziwei">
      {(z.chart.palaces as J[]).map((p) => {
        const b = M.branchIndex(p.branch), [r, c] = M.ZIWEI_RING[b] ?? [1, 1];
        return (
          <div key={p.branch} className={p.palace === "Life" ? "cell here" : "cell"} style={{ gridRow: r + 1, gridColumn: c + 1 }}>
            <span className="palace">{M.spaced(p.palace)}</span>
            <span className="stars">{(p.major_stars as string[]).map(M.spaced).join(", ")}</span>
            <span className="minor muted">{(minor[b] ?? []).join(", ")}</span>
            <span className="branch" translate="no">{M.BRANCH_HANZI[b]} {p.branch}</span>
          </div>
        );
      })}
      <div className="centre">
        <strong>Zi Wei Dou Shu</strong>
        <span>{M.spaced(z.chart.wu_xing_ju)} bureau</span>
        <span>Life {z.chart.ming_gong_branch}, Body {z.chart.shen_gong_branch}</span>
        <span className="muted">Lunar {z.lunar_month}/{z.lunar_day}</span>
      </div>
    </div>
  );
}

/** A ring of named parts with some marked: the Egyptian decans, the Celtic trees, the Aztec and Maya day signs. */
function Ring({ names, marks, title }: { names: string[]; marks: Record<number, string>; title: string }) {
  const C = 200, n = names.length, step = 360 / n;
  return (
    <svg className="trad-ring" viewBox="0 0 400 400" role="img" aria-label={title}>
      <circle cx={C} cy={C} r={190} className="rim" /><circle cx={C} cy={C} r={120} className="rim" />
      {names.map((name, i) => {
        const a = 90 - i * step, mid = a - step / 2;
        const [x1, y1] = M.polar(C, C, 120, a), [x2, y2] = M.polar(C, C, 190, a), [tx, ty] = M.polar(C, C, 155, mid);
        const big = n <= 20, [ax, ay] = M.polar(C, C, 190, a - step), [bx, by] = M.polar(C, C, 120, a - step);
        return (
          <g key={i} className={marks[i] !== undefined ? "part here" : "part"}>
            {/* the part's band, tinted where it is the native's own */}
            <path d={`M${x1} ${y1}L${x2} ${y2}A190 190 0 0 1 ${ax} ${ay}L${bx} ${by}A120 120 0 0 0 ${x1} ${y1}Z`} className="band" />
            <line x1={x1} y1={y1} x2={x2} y2={y2} className="cut" />
            <text x={tx} y={ty} textAnchor="middle" dominantBaseline="central" className={big ? "name" : "name small"}
              transform={`rotate(${90 - mid > 90 && 90 - mid < 270 ? 270 - mid : 90 - mid} ${tx} ${ty})`}>{big ? name : String(i + 1)}</text>
            {marks[i] !== undefined && (() => { const [mx, my] = M.polar(C, C, 104, mid); return <text x={mx} y={my} textAnchor="middle" dominantBaseline="central" className="mark">{marks[i]}</text>; })()}
          </g>
        );
      })}
      <text x={C} y={C} textAnchor="middle" dominantBaseline="central" className="title">{title}</text>
    </svg>
  );
}

function Hexagram({ lines, changing, label }: { lines: string[]; changing?: number; label: string }) {
  return (
    <svg className="trad-hexagram" viewBox="0 0 120 132" role="img" aria-label={label}>
      {lines.map((l, i) => {
        const y = 112 - i * 20, on = changing === i;
        return l === "Yang" ? <rect key={i} x={10} y={y} width={100} height={12} className={on ? "line here" : "line"} />
          : <g key={i} className={on ? "here" : undefined}><rect x={10} y={y} width={42} height={12} className="line" /><rect x={68} y={y} width={42} height={12} className="line" /></g>;
      })}
    </svg>
  );
}

function Count({ parts }: { parts: [string, ReactNode][] }) {
  return <div className="trad-count">{parts.map(([k, v]) => <div key={k}><strong>{v}</strong><span className="muted">{k}</span></div>)}</div>;
}

const TIBETAN_ANIMALS = ["Mouse", "Ox", "Tiger", "Hare", "Dragon", "Snake", "Horse", "Sheep", "Monkey", "Bird", "Dog", "Pig"];
const TIBETAN_ELEMENTS = ["Wood", "Fire", "Earth", "Iron", "Water"];
const same = (a: string, b: string) => a.toLowerCase().startsWith(b.toLowerCase().slice(0, 3)) || ({ rat: "mouse", rabbit: "hare", goat: "sheep", rooster: "bird", metal: "iron", boar: "pig" } as Record<string, string>)[a.toLowerCase()] === b.toLowerCase();

function WorldChart({ view, d }: { view: string; d: J }) {
  if (view === "saju") {
    const s = d.saju, P = (label: string, p: [string, string]) => ({ label, stem: p[0], branch: p[1] });
    return <Pillars korean pillars={[P("Hour", s.hour_pillar), P("Day", s.day_pillar), P("Month", s.month_pillar), P("Year", s.year_pillar)]} />;
  }
  if (view === "ninestar") {
    const grid = M.flyStars(d.nine_star_ki.year_star);
    return <LoShu cell={(r, c) => <strong className="star">{grid[r][c]}</strong>} here={(r, c) => grid[r][c] === d.nine_star_ki.month_star} />;
  }
  if (view === "mahabote") {
    return <div className="trad-seats">{(d.mahabote_square.seats as J[]).map((s) => (
      <div key={s.house} className={s.from_weekday === d.mahabote.birth_day ? "cell here" : "cell"}><strong>{s.house}</strong><span>{s.is_rahu ? "Rahu" : s.planet}</span><span className="muted">{s.from_weekday}</span></div>))}</div>;
  }
  if (view === "tibetan") {
    const t = d.tibetan;
    return <div className="trad-cycle">{TIBETAN_ELEMENTS.map((el) => <div key={el} className="row"><span className="muted">{el}</span>{TIBETAN_ANIMALS.map((an) => (
      <span key={an} className={same(t.element, el) && same(t.animal, an) ? "here" : undefined} title={`${el} ${an}`}>{an.slice(0, 2)}</span>))}</div>)}</div>;
  }
  if (view === "maya") {
    const lc = d.mayan.long_count, r = d.mayan.round;
    return <div className="trad-stack"><Count parts={[["baktun", lc.baktun], ["katun", lc.katun], ["tun", lc.tun], ["winal", lc.uinal], ["kin", lc.kin]]} />
      <Ring names={M.MAYA_SIGNS} marks={{ [M.mayaIndex(r.tzolkin.day_name)]: String(r.tzolkin.number) }} title={`${r.tzolkin.number} ${r.tzolkin.day_name}`} /></div>;
  }
  if (view === "aztec") return <Ring names={M.AZTEC_SIGNS} marks={{ [d.aztec.day_sign_index]: String(d.aztec.day_number) }} title={`${d.aztec.day_number} ${d.aztec.day_sign}`} />;
  if (view === "egyptian") {
    const marks: Record<number, string> = {};
    marks[d.egyptian.asc.number - 1] = "As";
    marks[d.egyptian.sun.number - 1] = marks[d.egyptian.sun.number - 1] ? "As Su" : "Su";
    return <Ring names={(d.egyptian.all as J[]).map((x) => x.name)} marks={marks} title="The 36 decans" />;
  }
  if (view === "celtic") {
    const m = d.celtic.month;
    return <Ring names={["Birch", "Rowan", "Ash", "Alder", "Willow", "Hawthorn", "Oak", "Holly", "Hazel", "Vine", "Ivy", "Reed", "Elder"]}
      marks={m ? { [m.number - 1]: m.ogham_letter } : {}} title={m ? m.tree_name : "No tree month"} />;
  }
  const total = (d.persian as J[]).reduce((a, p) => a + p.years, 0);
  const now = nowYear();
  return <div className="trad-bars">{(d.persian as J[]).map((p) => (
    <div key={p.planet} className={p.start_year <= now && now < p.end_year ? "bar here" : "bar"} style={{ flexGrow: p.years / total }}>
      <strong>{p.planet}</strong><span className="muted">{Math.floor(p.start_year)}–{Math.floor(p.end_year)}</span></div>))}</div>;
}

function ChineseChart({ view, d }: { view: string; d: J }) {
  if (view === "bazi") {
    const b = d.bazi, el = d.elements as J[];
    const P = (label: string, p: J, e: J) => ({ label, stem: p.stem, branch: p.branch, stemEl: e.stem, branchEl: e.branch });
    return <Pillars pillars={[P("Hour", b.hour, el[3]), P("Day", b.day, el[2]), P("Month", b.month, el[1]), P("Year", b.year, el[0])]} />;
  }
  if (view === "ziwei") return <ZiWei z={d.ziwei} />;
  if (view === "flying") {
    const f = d.flying_stars;
    return <LoShu cell={(r, c) => <><strong className="star">{f.grid[r][c]}</strong><span className="pair"><span title="Mountain (sitting)">{f.sitting_star[r][c]}</span><span title="Water (facing)">{f.facing_star[r][c]}</span></span></>}
      centre={<><strong className="star">{f.grid[1][1]}</strong><span className="muted">Period {f.period}</span></>} />;
  }
  if (view === "bazhai") {
    const z = d.ba_zhai, by: Record<string, string> = {};
    for (const [k, name] of BA_ZHAI) by[z[k]] = name;
    return <LoShu cell={(r, c) => <strong>{by[M.LO_SHU_DIRECTIONS[r][c]]}</strong>} here={(r, c) => M.LO_SHU_DIRECTIONS[r][c] === z.sheng_qi}
      centre={<><strong className="star">{z.gua}</strong><span className="muted">Kua, {z.group} group</span></>} />;
  }
  const q = d.qimen, at = (r: number, c: number) => (q.palaces as J[]).find((p) => p.number === M.LO_SHU[r][c]);
  return <LoShu cell={(r, c) => { const p = at(r, c); return p && <><strong>{M.spaced(p.star)}</strong><span>{M.spaced(p.door)}</span><span className="muted">{M.spaced(p.deity)} · {p.stem}</span></>; }} />;
}

/** Starlight's left half on the Traditions tab: the chart of the sub tab and view open. */
export function TraditionsLeft() {
  const [tab] = useTab();
  const [cv] = useView("chinese"), [ov] = useView("world");
  const [annual] = useAnnual();
  const q = useData(tab);
  return (
    <div className={`star-chart trad-left trad-${tab}`}>
      <Guard key={`${tab}.${cv}.${ov}.${annual}`}><Loaded q={q}>{(d: J) => tab === "western" ? <WesternWheel w={d} />
        : tab === "chinese" ? <ChineseChart view={cv} d={d} />
        : tab === "world" ? <WorldChart view={ov} d={d} />
        : tab === "iching" ? <div className="trad-stack"><Hexagram lines={d.primary.hexagram.lines} changing={d.changing_line} label={d.primary.hexagram.name_en} />
          <strong className="glyph" translate="no">{d.primary.hexagram.name_zh}</strong><span>{d.primary.hexagram.number}. {d.primary.hexagram.name_en}</span>
          <span className="muted">becoming {d.relating.hexagram.number}. {d.relating.hexagram.name_en}</span></div>
        : tab === "numerology" ? <div className="trad-numbers">{(d.numbers as J[]).map((n) => <div key={n.name} className="cell"><strong>{n.number}</strong><span className="muted">{n.name}</span></div>)}</div>
        // in the chart style of Preferences, as every other chart; the houses are fixed, Aries the first
        : <div className="trad-grid"><ChartGrid title={annual ? `Varshphal ${d.year_of_life}` : "Lal Kitab"} lagnaSign={0}
            cell={(sign) => ((annual ? d.annual.chart : d.chart).placements[sign] as string[]).map((p) => ABBR[p] ?? (p === "Rahu" ? "Ra" : p === "Ketu" ? "Ke" : p))} /></div>}
      </Loaded></Guard>
    </div>
  );
}

// ---------------------------------------------------------------------------------------------------------------------
// The tables (right half)
// ---------------------------------------------------------------------------------------------------------------------

function Western() {
  const [view] = useView("western");
  const o = useOptions();
  const q = useData("western");
  const pick = <select value={o.system} aria-label="House system" onChange={(e) => o.setSystem(e.target.value)}>
    {(q.data?.systems ?? [o.system]).map((s: string) => <option key={s} value={s}>{HOUSE_NAMES[s] ?? s}</option>)}</select>;
  return (
    <>
      <Tiles tab="western" extra={<label className="trad-label">Houses {pick}</label>} />
      <Guard key={view}><Loaded q={q}>{(w: J) => {
        if (view === "positions") return <Box title="Tropical positions" note={`${HOUSE_NAMES[w.system]} houses`}>
          <Table head={["Body", "Longitude", "House", "Speed / day", "Declination"]} rows={(w.bodies as J[]).map((b) => [<>{b.name}{retro(b) && <> <Retro /></>}</>, deg(b.lon), b.house,
            `${b.speed.toFixed(3)}°`, `${b.declination.toFixed(2)}°`])} />
          <Table head={["Point", "Longitude"]} rows={[["Ascendant", deg(w.houses.ascendant)], ["Midheaven", deg(w.houses.mc)], ["Vertex", deg(w.houses.vertex)],
            ...(w.houses.cusps as number[]).map((c, i) => [`House ${i + 1}`, deg(c)])]} /></Box>;
        if (view === "aspects") return <Box title="Patterns and aspects" note={`${w.aspects.length}, and ${w.patterns.length} patterns`}>
          <Table head={["Pattern", "Bodies"]} rows={(w.patterns as J[]).map((p) => [M.spaced(p.pattern), p.bodies.join(", ")])} />
          <Table head={["Body", "Aspect", "Body", "Orb", ""]} rows={(w.aspects as J[]).map((a) => [a.body1, M.spaced(a.aspect_type), a.body2,
            `${a.orb_deg.toFixed(2)}°`, a.direction])} /></Box>;
        if (view === "dignities") return <Box title="Essential dignities" note={`${w.sect} chart`}>
          <Table head={["Planet", "Score", "Domicile", "Exalted", "Detriment", "Fall", "Triplicity", "Term", "Face", "Sun"]}
            rows={(w.dignities as J[]).map((d) => [d.body, d.score, yesNo(d.domicile), yesNo(d.exaltation), yesNo(d.detriment), yesNo(d.fall),
              yesNo(d.triplicity), yesNo(d.term), yesNo(d.face), d.combustion])} /></Box>;
        if (view === "lots") return <Box title="Arabic lots" note={`${w.lots.length}, ${w.is_day ? "day" : "night"} formulas`}>
          <Table head={["Lot", "Longitude"]} rows={(w.lots as J[]).map((l) => [l.name, deg(l.lon)])} /></Box>;
        if (view === "timelords") {
          // the periods running now marked as the Dasas tree marks its own: the major one tinted, the deepest solid with NOW
          const h = w.hellenistic, zr = (rows: J[]) => rows.map((p) => [p.level === 1 ? SIGN_NAMES[p.sign_index] : `· ${SIGN_NAMES[p.sign_index]}`,
            p.years.toFixed(p.level === 1 ? 0 : 2), when(p.start), when(p.end)]);
          const deepest = (rows: J[], sub: (p: J) => boolean) => (i: number) => {
            const p = rows[i], subs = rows.some((r) => sub(r) && runningNow(r.start, r.end, true));
            return runningNow(p.start, p.end, sub(p) || !subs);
          };
          const subZr = (p: J) => p.level > 1, subFird = (p: J) => !!p.sub_ruler;
          return <Box title="Hellenistic time lords" note={`Fortune ${deg(h.fortune)}, Spirit ${deg(h.spirit)}`}>
            <Facts rows={[["Sect", w.sect], ["Annual profection", `Age ${h.profection.age}: ${SIGN_NAMES[h.profection.sign_index]}, lord ${h.profection.time_lord}`]]} />
            <h3 className="trad-sub">Zodiacal releasing from Spirit</h3><Table head={["Sign", "Years", "From", "To"]} rows={zr(h.zr_spirit)} mark={deepest(h.zr_spirit, subZr)} />
            <h3 className="trad-sub">Zodiacal releasing from Fortune</h3><Table head={["Sign", "Years", "From", "To"]} rows={zr(h.zr_fortune)} mark={deepest(h.zr_fortune, subZr)} />
            <h3 className="trad-sub">Firdaria</h3><Table head={["Ruler", "With", "From", "To"]} rows={(h.firdaria as J[]).map((p) => [p.ruler, p.sub_ruler ?? "", when(p.start), when(p.end)])} mark={deepest(h.firdaria, subFird)} />
            <h3 className="trad-sub">Decennials</h3><Table head={["Lord", "Years", "From", "To"]} rows={(h.decennials as J[]).map((p) => [p.lord, p.years.toFixed(1), when(p.start), when(p.end)])}
              mark={(i) => runningNow(h.decennials[i].start, h.decennials[i].end, true)} /></Box>;
        }
        if (view === "midpoints") return <Box title="Bodies on midpoints" note="Within 1.5°, and the 90° dial's pictures">
          <Table head={["Body", "On the midpoint of", "By", "Orb"]} rows={(w.midpoints as J[]).map((m) => [m.planet, m.pair, `${m.contact_angle}°`, `${m.orb.toFixed(2)}°`])} />
          <Table head={["Picture (90° dial)", "Orb"]} rows={(w.cosmobiology.planetary_pictures as J[]).map((p) => [p.formula, `${p.orb_90.toFixed(2)}°`])} /></Box>;
        if (view === "declinations") return <Box title="Declinations and antiscia" note="Within 1°">
          <Table head={["Body", "Aspect", "Body", "Orb"]} rows={(w.declinations as J[]).map((d) => [d.body1, M.spaced(d.aspect), d.body2, `${d.orb_deg.toFixed(2)}°`])} />
          <Table head={["Body", "Contact", "Body", "Orb"]} rows={(w.antiscia as J[]).map((a) => [a.body1, M.spaced(a.kind), a.body2, `${a.orb_deg.toFixed(2)}°`])} /></Box>;
        if (view === "progressions") return <Box title="Secondary progressions" note={`to now: the sky of ${when(w.progressed.moment, true)}`}>
          <Table head={["Body", "Progressed", "Solar arc directed"]} rows={(w.progressed.bodies as J[]).map((b) => [<>{b.name}{retro(b) && <> <Retro /></>}</>, deg(b.lon),
            deg((w.solar_arc.directed_positions as [string, number][]).find(([n]) => n === b.name)?.[1] ?? NaN)])} />
          <Facts rows={[["Solar arc", `${w.solar_arc.arc.toFixed(2)}°`], ["This year's solar return", when(w.returns.solar, true)], ["Next lunar return", when(w.returns.lunar, true)]]} /></Box>;
        if (view === "harmonics") return <Box title="Harmonic charts">
          <Table head={["Body", ...(w.harmonics as J[]).map((h) => `H${h.harmonic}`)]}
            rows={(w.harmonics[0].positions as J[]).map((p, i) => [p.body, ...(w.harmonics as J[]).map((h) => deg(h.positions[i].harmonic_longitude))])} /></Box>;
        return <Box title="Fixed stars, Uranian points, the Moon" note={`Moon ${(w.moon_phase.illumination * 100).toFixed(0)}% lit`}>
          <Table head={["Body", "Star", "Magnitude", "Orb"]} rows={(w.fixed_stars as J[]).map((s) => [s.body, s.star, s.magnitude.toFixed(2), `${s.orb.toFixed(2)}°`])} />
          <Table head={["Uranian point", "Longitude"]} rows={(w.uranian as J[]).map((u) => [u.name, deg(u.lon)])} /></Box>;
      }}</Loaded></Guard>
    </>
  );
}

function Chinese() {
  const [view] = useView("chinese");
  const q = useData("chinese");
  return (
    <>
      <Tiles tab="chinese" extra={<GenderPick />} />
      <Guard key={view}><Loaded q={q}>{(d: J) => {
        if (view === "bazi") {
          const b = d.bazi, el = d.elements as J[], rows = [["Year", b.year, el[0]], ["Month", b.month, el[1]], ["Day", b.day, el[2]], ["Hour", b.hour, el[3]]] as [string, J, J][];
          return <Box title="BaZi, the four pillars" note={`Day master ${b.day_master}`}>
            <Table head={["Pillar", "Stem", "Branch", "Animal"]} rows={rows.map(([k, p, e]) => [k, `${p.stem} (${e.stem_yang ? "yang" : "yin"} ${e.stem})`, `${p.branch} (${e.branch})`,
              M.BRANCH_ANIMALS[M.branchIndex(p.branch)]])} />
            <p className="muted pad">The year turns at Li Chun and the month at each solar term, by the Sun of NASA JPL's DE442; the day at local midnight.</p></Box>;
        }
        if (view === "ziwei") {
          const z = d.ziwei, palaces = z.chart.palaces as J[];
          return <Box title="The twelve palaces" note={`Lunar date ${z.lunar_month}/${z.lunar_day}${d.lunar_date.leap ? " (leap month)" : ""}, ${M.spaced(z.chart.wu_xing_ju)} bureau`}>
            <Table head={["Palace", "Branch", "Major stars"]} rows={palaces.map((p) => [M.spaced(p.palace), p.branch, (p.major_stars as string[]).map(M.spaced).join(", ")])} />
            <h3 className="trad-sub">Da Xian, the ten-year periods</h3>
            <Table head={["Ages", "Palace"]} rows={(z.da_xian as J[]).map((x) => [`${x.start_age}–${x.end_age}`, M.spaced(palaces[x.palace_idx]?.palace ?? "")])} /></Box>;
        }
        if (view === "flying") return <Box title="The nine stars" note={`Period ${d.flying_stars.period}; this year's centre ${d.annual_center}, this month's ${d.monthly_center}`}>
          <Table head={["Star", "Element", "Meaning"]} rows={(d.star_meanings as J[]).map((s) => [s.star, s.element, s.meaning])} wrap /></Box>;
        if (view === "bazhai") return <Box title="Ba Zhai, the eight mansions" note={`Kua ${d.ba_zhai.gua}, ${d.ba_zhai.group} group`}>
          <Table head={["Direction", "Star", "For"]} rows={BA_ZHAI.map(([k, name, gloss]) => [d.ba_zhai[k], name, gloss])} /></Box>;
        const qm = d.qimen;
        return <Box title="The nine palaces" note={`${qm.is_yang_dun ? "Yang" : "Yin"} Dun ${qm.ju_number > 9 ? qm.ju_number - 9 : qm.ju_number}; XALEN marks it experimental`}>
          <Table head={["Palace", "Star", "Door", "Deity", "Stem"]} rows={(qm.palaces as J[]).map((p) => [p.number, M.spaced(p.star), M.spaced(p.door), M.spaced(p.deity), p.stem])} /></Box>;
      }}</Loaded></Guard>
    </>
  );
}

function World() {
  const [view] = useView("world");
  const q = useData("world");
  return (
    <>
      <Tiles tab="world" extra={<GenderPick />} />
      <Guard key={view}><Loaded q={q}>{(d: J) => {
        if (view === "saju") return <Box title="Saju, the four pillars of Korea" note={`Day master ${d.saju.day_master} (${d.saju.day_master_element})`}>
          <h3 className="trad-sub">Daeun, the ten-year luck periods</h3>
          <Table head={["Ages", "Stem", "Branch"]} rows={(d.daeun as J[]).map((p) => [`${p.start_age}–${p.end_age}`, p.stem, p.branch.replace(/_$/, "")])} /></Box>;
        if (view === "ninestar") { const n = d.nine_star_ki;
          return <Box title="The birth stars"><Facts rows={[["Year star", n.year_star], ["Month star", n.month_star], ["Element", n.element], ["Direction", n.direction],
            ["Trigram", n.trigram], ["Compatible stars", (d.nine_star_compatible as number[]).join(", ")]]} /></Box>; }
        if (view === "mahabote") { const m = d.mahabote;
          return <Box title="The birth day and its seven houses"><Facts rows={[["Born on", `${m.birth_day}${m.is_wednesday_pm ? " (afternoon: Rahu's day)" : ""}`], ["Ruling planet", m.ruling_planet],
            ["Animal", m.animal], ["Direction", m.direction], ["Element", m.element], ["Favourable days", m.favorable_days.join(", ")], ["Unfavourable days", m.unfavorable_days.join(", ")]]} />
            <Table head={["House", "Planet", "Weekday"]} rows={(d.mahabote_square.seats as J[]).map((s) => [s.house, s.is_rahu ? "Rahu" : s.planet, s.from_weekday])} /></Box>; }
        if (view === "tibetan") { const t = d.tibetan;
          return <Box title="The Tibetan year"><Facts rows={[["Year", `${t.gender} ${t.element} ${t.animal}`], ["Rabjung (60-year cycle)", t.rabjung_cycle], ["Year of the cycle", t.year_in_cycle]]} /></Box>; }
        if (view === "maya") { const lc = d.mayan.long_count, r = d.mayan.round;
          return <Box title="The Maya calendar"><Facts rows={[["Long Count", [lc.baktun, lc.katun, lc.tun, lc.uinal, lc.kin].join(".")], ["Tzolk'in", `${r.tzolkin.number} ${r.tzolkin.day_name}`],
            ["Haab'", `${r.haab.day} ${r.haab.month}`]]} /></Box>; }
        if (view === "aztec") { const a = d.aztec;
          return <Box title="The Aztec tonalpohualli"><Facts rows={[["Day sign", `${a.day_number} ${a.day_sign} (${a.day_sign_english})`], ["Trecena ruler", a.trecena_ruler]]} /></Box>; }
        if (view === "egyptian") return <Box title="The Egyptian decans" note={`Sun ${deg(d.sun)}, ascendant ${deg(d.asc)}`}>
          <Facts rows={[["The Sun's decan", `${d.egyptian.sun.number}. ${d.egyptian.sun.name}, ruled by ${d.egyptian.sun.ruling_planet} (${d.egyptian.sun.star_group})`],
            ["The ascendant's", `${d.egyptian.asc.number}. ${d.egyptian.asc.name}, ruled by ${d.egyptian.asc.ruling_planet} (${d.egyptian.asc.star_group})`]]} />
          <Table head={["Decan", "From", "Ruler", "Stars"]} rows={(d.egyptian.all as J[]).map((x) => [`${x.number}. ${x.name}`, deg(x.start_degree), x.ruling_planet, x.star_group])} /></Box>;
        if (view === "celtic") { const m = d.celtic.month, y = d.celtic.year;
          return <Box title="The Celtic tree calendar"><Facts rows={[["Birth tree", m ? `${m.tree_name} (ogham ${m.ogham_letter}), ${m.element}, the ${m.animal}` : "None: 23 December falls between the months"],
            ["The year's tree", `${y.tree_name} (ogham ${y.ogham_letter})`]]} /></Box>; }
        return <Box title="Jarbakhtar, the Persian periods" note={`From the almuten, ${d.almuten}`}>
          <Table head={["Planet", "Years", "From", "To"]} rows={(d.persian as J[]).map((p) => [p.planet, p.years, Math.floor(p.start_year), Math.floor(p.end_year)])}
            mark={(i) => { const p = d.persian[i], y = nowYear(); return p.start_year <= y && y < p.end_year ? "now" : undefined; }} /></Box>;
      }}</Loaded></Guard>
    </>
  );
}

function IChing() {
  const q = useData("iching");
  return <Guard key={"iching"}><Loaded q={q}>{(d: J) => {
    const h = d.primary.hexagram, line = (n: number) => ["first", "second", "third", "fourth", "fifth", "top"][n];
    return <Box title={`${h.number}. ${h.name_en}`} note={`cast by the birth's date and hour (Mei Hua Yi Shu); ${line(d.changing_line)} line changing`}>
      <Facts rows={[["Judgement", h.judgment], ["Image", h.image], ["The changing line", d.line_text], ["Becoming", `${d.relating.hexagram.number}. ${d.relating.hexagram.name_en}`],
        ["Nuclear", `${d.nuclear.hexagram.number}. ${d.nuclear.hexagram.name_en}`], ["Opposite", `${d.opposite.hexagram.number}. ${d.opposite.hexagram.name_en}`]]} />
      <h3 className="trad-sub">The six lines</h3>
      <Table head={["Line", "Text"]} rows={(d.primary.lines as string[]).map((t, i) => [line(i), t])} wrap />
      <p className="muted pad">James Legge's translation (1882).</p></Box>;
  }}</Loaded></Guard>;
}

function Numerology() {
  const o = useOptions();
  const q = useData("numerology");
  return (
    <>
      <section className="pane trad-tiles">
        <form className="trad-options" onSubmit={(e) => e.preventDefault()}>
          <label className="trad-label">Name <input value={o.person} onChange={(e) => o.setPerson(e.target.value)} maxLength={120} /></label>
          <div className="mv-kind" role="group" aria-label="Letter values">
            <button type="button" aria-pressed={!o.chaldean} onClick={() => o.setChaldean(false)}>Pythagorean</button>
            <button type="button" aria-pressed={o.chaldean} onClick={() => o.setChaldean(true)}>Chaldean</button>
          </div>
        </form>
      </section>
      <Guard key={"numerology"}><Loaded q={q}>{(d: J) => <Box title="Core numbers" note={d.name || "No name"}>
        <Table head={["Number", "Value", "Karmic debt"]} rows={(d.numbers as J[]).map((n) => [n.name, n.number, yesNo(n.karmic_debt)])} />
        <p className="muted pad">The personal year is for {d.year}.</p></Box>}</Loaded></Guard>
    </>
  );
}

function LalKitab() {
  const q = useData("lalkitab");
  const [annual, setAnnual] = useAnnual();
  return <>
    <section className="pane trad-tiles">
      <div className="trad-options">
        <div className="mv-kind" role="group" aria-label="Natal or annual chart">
          <button type="button" aria-pressed={!annual} onClick={() => setAnnual(false)}>Natal chart</button>
          <button type="button" aria-pressed={annual} onClick={() => setAnnual(true)} data-tip="The chart of this year of life, by Lal Kitab's table">Varshphal</button>
        </div>
      </div>
    </section>
    <Guard key={"lalkitab"}><Loaded q={q}>{(d: J) => <>
    <Box title="Grahas in the houses" note="The lagna is always the first house, Aries its sign">
      <Table head={["Graha", "House", "Effect", "Dormant"]} rows={(d.planets as J[]).map((p) => [p.planet, p.house, p.effect, yesNo(p.dormant)])} />
      <h3 className="trad-sub">Debts (rin)</h3>
      {d.debts.length ? <Table head={["Debt", "From", "House", "With a malefic"]} rows={(d.debts as J[]).map((x) => [M.spaced(x.kind), x.trigger_planet, x.house, yesNo(x.malefic_conjunction)])} />
        : <p className="muted pad">None.</p>}
      <h3 className="trad-sub">Varshphal, year {d.year_of_life} of life</h3>
      <Table head={["House", "Grahas this year"]} rows={(d.annual.chart.placements as string[][]).map((ps, i) => [i + 1, ps.join(", ")])} />
    </Box>
  </>}</Loaded></Guard>
  </>;
}

/** The Traditions tab's right half: its sub tabs, then the sub tab. */
export function Traditions() {
  const [tab, setTab] = useTab();
  return (
    <div className="right lab traditions">
      <header className="lab-head"><OneRowTabs tabs={TABS} pinned={PINNED} value={tab} onChange={setTab} label="Traditions" /></header>
      {tab === "western" ? <Western /> : tab === "chinese" ? <Chinese /> : tab === "world" ? <World /> : tab === "iching" ? <IChing />
        : tab === "numerology" ? <Numerology /> : <LalKitab />}
    </div>
  );
}
