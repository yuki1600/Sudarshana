import { useEffect, useRef, useState, type ReactNode } from "react";
import { useQueries, useQuery } from "@tanstack/react-query";
import { api, type AvView, type Basics, type Strengths, type DasaPeriod, type GrahaInsight, type KeyRow, type Table } from "./api";
import { FormButtons, Modal } from "./ChartDialogs";
import { keep, useKept, useSaved, useSettings, useTopVarga } from "./hooks";
import { useMenu, type MenuEntry } from "./Menu";
import { Loaded, supOrd } from "./ui";
import { DIVISIONS, DivisionSelect } from "./Windows";
import { SouthGrid } from "./SouthGrid";
import { Icon, type IconName } from "./Icons";
import { SIGNS, SIGN_NAMES, formatLon, formatMoment, timeLeft } from "./format";
import { useChart } from "./store";
import { Meter, Stat } from "./Lab";
import { VAI, avScore, avWord, toneStyle, vaiCount } from "./tone";
import { lordsOf } from "./calcMath";
import { openLore } from "./Lore";
import { tr, useLanguage } from "./language";

/** Grahas used for Highlights (Lagna through Ketu); the table above still lists every body. */
const MAIN_BODIES = ["Lagna", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"] as const;
export const MAIN_SET = new Set<string>(MAIN_BODIES);

/** A list view picked by key: the Key Info modes and the Strengths lists. */
export function TableView({ view, chart, varga = 1, options, cell }: { view: string; chart?: Parameters<typeof api.table>[0]; varga?: number; options?: Record<string, unknown>; cell?: (row: string[], k: number) => ReactNode }) {
  const current = useChart((s) => s.birth)!;
  const birth = chart ?? current;
  const q = useQuery({ queryKey: ["table", birth, view, varga, options], queryFn: () => api.table(birth, view, varga, options), placeholderData: (p) => p });
  return (
    <Loaded q={q}>{(t) => <div className="scroll tall"><Rows t={t} cell={cell} /></div>}</Loaded>
  );
}

function Rows({ t, next, cell }: { t: Table; next?: boolean; cell?: (row: string[], k: number) => ReactNode }) {
  return (
    <table className={next ? "points wrap aspect-next" : "points wrap"}>
      <thead><tr>{t.columns.map((c) => <th key={c}>{c}</th>)}</tr></thead>
      <tbody>{t.rows.map((r, i) => <tr key={i}>{r.map((c, k) => <td key={k}>{cell?.(r, k) ?? supOrd(c)}</td>)}</tr>)}</tbody>
    </table>
  );
}

// Starlight's Taras: the four Key Info tables, each with its first column naming it
const TARAS = [["nava_moon", "Tara from Moon"], ["nava_lagna", "Tara from Lagna"], ["special_moon", "Special tara from Moon"], ["special_lagna", "Special tara from Lagna"]] as const;
// which star from the point each special tara is, on the 28-star wheel its star is counted on (core_logic/key_info.py SPECIAL_TARAS, steps + 1)
const SPECIAL_COUNT: Partial<Record<string, number>> = { Janma: 1, Karma: 10, Samudayika: 18, Sanghatika: 16, Jaati: 4, Naidhana: 7, Desa: 12, Abhisheka: 28, Aadhaana: 19, Vainasika: 22, Maanasa: 25 };
/** A tara's name with its count: Janma (1st); the nava taras run 1st to 9th down the table. */
const counted = (t: Table, special: boolean): Table => ({ ...t, rows: t.rows.map((r, i) => {
  const n = special ? SPECIAL_COUNT[r[0]] : i + 1;
  return n ? [`${r[0]} (${nth(n)})`, ...r.slice(1)] : r;
}) });

/** Starlight's Taras from Moon and Lagna: the nava taras, then the special taras, from each, one under another in one box that scrolls as one. */
function Taras({ chart }: { chart: Parameters<typeof api.table>[0] }) {
  const qs = useQueries({ queries: TARAS.map(([view]) => ({ queryKey: ["table", chart, view, 1, undefined], queryFn: () => api.table(chart, view, 1), placeholderData: (p?: Table) => p })) });
  const failed = qs.find((q) => q.isError);
  const all = qs.every((q) => q.data) ? qs.map((q) => q.data!) : undefined;
  return (
    <Loaded q={{ data: all, isError: !!failed, error: failed?.error ?? null }}>{(ts) => (
      <div className="scroll tall">{ts.map((t, i) => <Rows key={TARAS[i][0]} t={{ ...counted(t, i > 1), columns: [TARAS[i][1], ...t.columns.slice(1)] }} next={i > 0} />)}</div>
    )}</Loaded>
  );
}

/** Starlight's Pushkara and Mrityu Bhagas: the two Key Info lists as one table, a row green when the body is in its pushkara bhaga, red when in its mrityu bhaga;
 *  the pushkaramsa column as the server sends it, then the distance from each centre. */
function Bhagas({ chart }: { chart: Parameters<typeof api.table>[0] }) {
  const qs = useQueries({ queries: ["pushkaras", "mrityu"].map((view) => ({ queryKey: ["table", chart, view, 1, undefined], queryFn: () => api.table(chart, view, 1), placeholderData: (p?: Table) => p })) });
  const failed = qs.find((q) => q.isError);
  const both = qs[0].data && qs[1].data ? [qs[0].data, qs[1].data] as const : undefined;
  return (
    <Loaded q={{ data: both, isError: !!failed, error: failed?.error ?? null }}>{([p, m]) => (
      <div className="scroll tall">
        <table className="points wrap bhagas">
          <thead><tr><th>Body</th><th>In Pushkaramsa?</th><th>From Pushkara Bhaga Center</th><th>From Mrityu Bhaga Center</th></tr></thead>
          <tbody>{p.rows.map((r, i) => {
            const mr = m.rows.find((x) => x[0] === r[0]);     // both lists run over the same bodies and cusps, in one order
            const tone = mr?.[2] === "Yes" ? "bad" : r[2] === "Yes" ? "good" : undefined;
            return (
              <tr key={i} className={tone} data-tip={tone && (tone === "good" ? "In its Pushkara bhaga" : "In its Mrityu bhaga")}>
                <td>{tone && <i className="hl-tone" />}{supOrd(r[0])}</td><td>{r[1]}</td><td>{r[3]}</td><td>{mr?.[1] ?? "-"}</td>
              </tr>
            );
          })}</tbody>
        </table>
      </div>
    )}</Loaded>
  );
}

const BASIC = "longitudes";
// Select the bodies to show ([BodiesToShow]); the outer planets are off, the rest on. The arudhas are shown only when asked for.
const BODY_BOXES: [string, string, boolean][] = [["planets", "Grahas", true], ["outer", "Outer grahas", false], ["lagnas", "Bhava, Hora, Ghati Lagnas", true], ["vighati", "Vighati Lagna", true], ["varnada", "Varnada Lagna", true], ["sree", "Sree Lagna", true], ["pranapada", "Pranapada Lagna", true], ["indu", "Indu Lagna", true], ["bb", "Bhrigu Bindu", true],
  ["mandi", "Mandi", true], ["gulika", "Gulika", true], ["upagrahas", "Other Upagrahas", true], ["sphutas", "Sphutas of Prasna Marga", true], ["al", "Arudha Lagna", false], ["bhava_arudhas", "Bhava Arudhas", false], ["graha_arudhas", "Graha Arudhas", false], ["varnadas", "Varnadas", true], ["kunda", "Kunda", true], ["yoga", "Yoga and Avayoga Sphuta", true]];
const BODY_DEFAULTS = Object.fromEntries(BODY_BOXES.map(([k, , on]) => [k, on]));

export function useBodies() {
  const [json, setJson] = useSaved<string>("bodies", JSON.stringify(BODY_DEFAULTS));
  const bodies: Record<string, boolean> = { ...BODY_DEFAULTS, ...JSON.parse(json) };
  return { bodies, setBodies: (b: Record<string, boolean>) => setJson(JSON.stringify(b)) };
}

export function BodiesDialog({ bodies, onOk, onClose }: { bodies: Record<string, boolean>; onOk: (b: Record<string, boolean>) => void; onClose: () => void }) {
  const [b, setB] = useState(bodies);
  return (
    <Modal title="Select the bodies to show" onClose={onClose}>
      <form method="dialog" onSubmit={(e) => { e.preventDefault(); onOk(b); onClose(); }}>
        <p className="muted">Use this to suppress bodies you don't care about!</p>
        <div className="check-columns">{BODY_BOXES.map(([k, n]) => <label key={k} className="check"><input type="checkbox" checked={b[k]} onChange={(e) => setB({ ...b, [k]: e.target.checked })} /> {n}</label>)}</div>
        <FormButtons />
      </form>
    </Modal>
  );
}

function AspectOptions({ o, onOk, onClose }: { o: AspectOpts; onOk: (o: AspectOpts) => void; onClose: () => void }) {
  const [f, setF] = useState(o);
  return (
    <Modal title="Graha Aspect Evaluation Options" onClose={onClose}>
      <form method="dialog" onSubmit={(e) => { e.preventDefault(); onOk(f); onClose(); }}>
        <p className="muted">Graha aspects on various positions will be evaluated using Parasara's formulas. You can choose the chart (natal vs transit etc) and the divisional chart of each side.</p>
        <fieldset className="mode-group wide"><legend>Aspecting Grahas</legend>
          <label className="check"><input type="checkbox" checked={f.aspecting_natal} onChange={(e) => setF({ ...f, aspecting_natal: e.target.checked })} /> Force natal chart even when displaying Tajaka/TP/Transit etc</label>
          <label>The divisional chart to be used for positions<DivisionSelect value={f.aspecting_varga} onChange={(d) => setF({ ...f, aspecting_varga: d })} /></label>
        </fieldset>
        <fieldset className="mode-group wide"><legend>Aspected Positions</legend>
          <label className="check"><input type="checkbox" checked={f.aspected_natal} onChange={(e) => setF({ ...f, aspected_natal: e.target.checked })} /> Force natal chart even when displaying Tajaka/TP/Transit etc</label>
          <label>The divisional chart to be used for positions<DivisionSelect value={f.aspected_varga} onChange={(d) => setF({ ...f, aspected_varga: d })} /></label>
        </fieldset>
        <FormButtons />
      </form>
    </Modal>
  );
}
interface AspectOpts { aspecting_varga: number; aspected_varga: number; aspecting_natal: boolean; aspected_natal: boolean }

export const ABBR_NAME: Record<string, string> = { As: "Lagna", Su: "Sun", Mo: "Moon", Ma: "Mars", Me: "Mercury", Ju: "Jupiter", Ve: "Venus", Sa: "Saturn", Ra: "Rahu", Ke: "Ketu" };
const CONJ_ORB = 3;   // degrees: close yuti for the Highlights list (war uses 1° on the server)

const lonSep = (a: number, b: number) => { const d = Math.abs(((a - b) % 360 + 360) % 360); return Math.min(d, 360 - d); };
/** Water–fire junctions: within 3°20′ of 0°/120°/240° (same rule as longevity’s Moon gandanta). */
const inGandanta = (lon: number) => { const x = ((lon % 120) + 120) % 120; return x < 10 / 3 || x >= 120 - 10 / 3; };
const arc = (x: number) => `${Math.floor(x)}°${String(Math.floor((x % 1) * 60)).padStart(2, "0")}′`;     // 12.5 → 12°30′
const degIn = (lon: number) => arc(((lon % 30) + 30) % 30);
const gandantaLabel = (r: KeyRow) => `${r.name} in ${SIGN_NAMES[r.rasi]} (${degIn(r.lon)})`;
// exaltation sign and deepest degree (core_logic natal_chart.EXALTATION); the nodes by sign only (Gemini / Sagittarius)
const EXALT: Record<string, [number, number?]> = { Sun: [0, 10], Moon: [1, 3], Mars: [9, 28], Mercury: [5, 15], Jupiter: [3, 5], Venus: [11, 27], Saturn: [6, 20], Rahu: [2], Ketu: [8] };
// Surya Siddhanta orbs, direct / retrograde (natal_chart.CLASSICAL_COMBUSTION)
const COMBUST_ORB: Record<string, [number, number]> = { Moon: [12, 12], Mars: [17, 17], Mercury: [14, 12], Jupiter: [11, 11], Venus: [10, 8], Saturn: [15, 15] };
const ahead = (a: number, b: number) => ((a - b) % 360 + 360) % 360;     // how far a is past b
export const nth = (n: number) => (n % 10 === 1 && n !== 11 ? `${n}st` : n % 10 === 2 && n !== 12 ? `${n}nd` : n % 10 === 3 && n !== 13 ? `${n}rd` : `${n}th`);
/** Same rasi in D-1 and D-9 (navamsa column of Key Info). */
const isVargottama = (r: KeyRow) => r.rasi === r.navamsa;

/** A body's own colour (the grahas' --g-*), gold for the lagna, grey for the rest. */
export const dotColor = (name: string) => !MAIN_SET.has(name) ? "var(--chart-line)" : name === "Lagna" ? "var(--lagna)" : `var(--g-${name.slice(0, 2)})`;

type Chip = { text: string; who?: string; tone?: "good" | "bad"; title?: string };
// Starlight: each fact's one dot, green for a strength, hollow for a mixed or neutral one, red for the rest
const GOOD_FACTS = new Set(["Exalted", "Vargottama", "Pushkara bhaga"]), MIXED_FACTS = new Set(["Graha war", `Yuti ≤${CONJ_ORB}°`]);
// and names grahas and signs short: "Ketu in Sagittarius (1°27′)" reads "Ke in Sg (1°27′)"; "from Moon", the reference, stays whole
const LONG_NAMES = new RegExp(`(?<!from )\\b(${[...MAIN_BODIES.slice(1), ...SIGN_NAMES].join("|")})\\b`, "g");
const shortNames = (t: string) => t.replace(LONG_NAMES, (w) => { const s = SIGN_NAMES.indexOf(w); return s < 0 ? w.slice(0, 2) : SIGNS[s]; });
// marana karaka sthana: the house from the lagna that is death to each graha (server/charts.py marana); Ketu has none
// BPHS 34.19-44 (Santhanam): the killers Parasara names for each lagna, Aries to Pisces. Primary: named a killer outright; secondary: the "etc." /
// "other malefics" of the verse, or a graha that kills only by association. The verse is the chip's tooltip.
const MARAKAS: [string[], string[], string][] = [
  [["Venus"], ["Saturn", "Mercury"], "34.19-22: Venus is a direct (independent) killer. Saturn etc. will also inflict death if associated with an adverse graha (Venus)."],
  [["Jupiter", "Mars"], ["Venus", "Moon"], "34.23-24: Jupiter etc. and Mars will inflict death; Jupiter, Venus and the Moon are malefics."],
  [["Moon"], [], "34.25-26: The Moon is the prime killer, but it is dependent on her association."],
  [["Saturn", "Sun"], [], "34.27-28: Saturn and the Sun are killers and give effects according to association."],
  [["Saturn", "Moon"], [], "34.29-30: Saturn and the Moon are killers who will give effects according to association."],
  [["Venus"], ["Mars", "Jupiter", "Moon"], "34.31-32: Venus is a killer as well (with the malefics Mars, Jupiter and the Moon); the Sun's role depends on his association."],
  [["Mars"], ["Jupiter", "Sun"], "34.33-34: Mars is a killer. Jupiter and other malefics will also acquire a disposition to inflict death."],
  [["Venus"], ["Mercury", "Saturn"], "34.35-36: Venus and other malefics (Mercury, Saturn) acquire the quality of causing death."],
  [["Saturn"], ["Venus"], "34.37-38: Saturn is a killer. Venus acquires killing powers."],
  [["Mars"], ["Jupiter", "Moon", "Saturn"], "34.39-40: Saturn will not be a killer of his own. Mars and other malefics (Jupiter, the Moon) will inflict death."],
  [["Jupiter", "Sun", "Mars"], [], "34.41-42: Jupiter, the Sun and Mars are killers."],
  [["Saturn", "Mercury"], ["Mars"], "34.43-44: Saturn and Mercury are killers. Though Mars is a killer, he will not kill the native independently."],
];
// dagdha (burnt) rasis by tithi, Pratipada to Chaturdashi, either paksha (Vidya Madhaviyam); Purnima and Amavasya have none
const DAGDHA = [[6, 9], [8, 11], [4, 9], [1, 10], [2, 5], [0, 4], [3, 8], [2, 5], [4, 7], [4, 7], [8, 11], [6, 9], [1, 4], [2, 5, 8, 11]];
const TITHIS = ["Pratipada", "Dvitiya", "Tritiya", "Chaturthi", "Panchami", "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami", "Ekadashi", "Dvadashi", "Trayodashi", "Chaturdashi"];

/** Starlight: a graha clicked in the charts or the Overview opens on Home's Grahas tab, its row open. */
export const openGraha = (g: string) => { keep("grahaOpen", g); useChart.getState().go("Home", ["starTab", "planets"]); };

/** Compact read of what stands out — dignity, combustion, war, yuti, gandanta. */
/** ``division``: the varga the rows are in (Starlight's top left chart); dignities and lordships are read there, combustion, war and strengths in the rasi. */
export function ChartHighlights({ rows, sensitive, division = 1 }: { rows: KeyRow[]; sensitive?: boolean; division?: number }) {
  useLanguage();     // the pieces below put into it as one ("in 12th": 12 में), not word by word
  const birth = useChart((s) => s.birth)!;
  const classical = useSettings().combustion_classical !== false;
  const go = useChart((s) => s.go);
  const toBalas = () => go("Strengths", ["strengths", "shadbala"]);     // the four cards open the shadbala they come from     // the server's default is the classical orbs
  // Starlight's Overview only: the Pushkara / Mrityu bhaga lists and the 64th navamsa / 22nd drekkana lords
  const extra = (view: string) => ({ queryKey: ["table", birth, view, 1, undefined], queryFn: () => api.table(birth, view), placeholderData: (p?: Table) => p, enabled: !!sensitive });
  const [pushkara, mrityu, malicious] = useQueries({ queries: ["pushkaras", "mrityu", "malicious"].map(extra) });
  // marana karaka sthana is by the bhava a graha occupies, not its sign from the lagna (server/insights.py)
  const insights = useQuery({ queryKey: ["grahaInsights", birth, division], queryFn: () => api.grahaInsights(birth, division), placeholderData: (p) => p, enabled: !!sensitive });
  const lagna = rows.find((r) => r.name === "Lagna");
  // the cards: the houses a graha rules from the lagna, and a house's lord (Starlight only)
  // Starlight: "Mars (1st & 8th) in 12th": the houses it rules small and grey, the bhava it occupies from the lagna (the house system's, server/insights.py) full size
  const graha = (g: string) => {
    const r = insights.data?.find((x) => x.name === g);
    if (!sensitive || !lagna) return g;
    const hs = [...Array(12).keys()].filter((h) => lordsOf((lagna.rasi + h) % 12).includes(g)).map((h) => h + 1);
    return <>{g}{hs.length > 0 && <small> ({hs.map((h, i) => <span key={h}>{i > 0 && " & "}{supOrd(nth(h))}</span>)})</small>}{r && <span className="stat-in"> {supOrd(tr(`in ${nth(r.bhava)}`))}</span>}</>;
  };
  const lordOf = (h?: number) => sensitive && lagna && h ? ` (${lordsOf((lagna.rasi + h - 1) % 12).map((n) => n.slice(0, 2)).join(", ")})` : "";
  const sun = rows.find((r) => r.name === "Sun"), moon = rows.find((r) => r.name === "Moon");
  const tithi = sun && moon ? Math.floor((((moon.lon - sun.lon) % 360) + 360) % 360 / 12) % 15 : -1;     // 0..13 Pratipada..Chaturdashi, 14 Purnima/Amavasya
  const strengths = useQuery({ queryKey: ["strengths", birth], queryFn: () => api.strengths(birth), placeholderData: (p) => p });
  const aspects = useQuery({ queryKey: ["aspectTable", birth, division, 0], queryFn: () => api.aspectTable(birth, division, 0), placeholderData: (p) => p });
  const yuddha = useQuery({ queryKey: ["table", birth, "yuddha", 1, undefined], queryFn: () => api.table(birth, "yuddha"), placeholderData: (p) => p });
  const byPct = [...(strengths.data?.shadbala.planets ?? [])].sort((a, b) => b.percent - a.percent);
  const byHouse = [...(strengths.data?.shadbala.bhavas ?? [])].sort((a, b) => b.rupas - a.rupas);
  const weakG = byPct.length > 1 ? byPct[byPct.length - 1] : undefined, weakH = byHouse.length > 1 ? byHouse[byHouse.length - 1] : undefined;
  const exalted: Chip[] = [], debilitated: Chip[] = [], combust: Chip[] = [];
  for (const r of aspects.data?.rows ?? []) {
    const name = ABBR_NAME[r.body] ?? r.body;
    if (r.marks.includes("exalted")) exalted.push({ text: name, who: name, tone: "good" });
    if (r.marks.includes("debilitated")) debilitated.push({ text: name, who: name, tone: "bad" });
    if (r.combust && division === 1) combust.push({ text: name, who: name, tone: "bad" });
  }
  if (division !== 1) for (const g of insights.data ?? []) if (g.combust) combust.push({ text: g.name, who: g.name, tone: "bad" });   // combustion is the rasi's: the varga's degrees don't make it
  const war: Chip[] = [];
  for (const [planet, w, l] of yuddha.data?.rows ?? []) {
    if (w === "Yes") war.unshift({ text: `${planet} wins`, who: planet, tone: "good" });
    if (l === "Yes") war.push({ text: `${planet} loses`, who: planet, tone: "bad" });
  }
  const pairs: { sep: number; text: string }[] = [];
  for (let i = 0; i < rows.length; i++) {
    for (let j = i + 1; j < rows.length; j++) {
      const sep = lonSep(rows[i].lon, rows[j].lon);
      if (sep <= CONJ_ORB) pairs.push({ sep, text: `${rows[i].name}–${rows[j].name} ${sep.toFixed(1)}°` });
    }
  }
  pairs.sort((a, b) => a.sep - b.sep);
  const inBhaga = (t: Table | undefined, tone: Chip["tone"]): Chip[] => (t?.rows ?? []).filter((r) => r[0] !== "Maandi" && r[2] === "Yes").map((r) => ({ text: r[0], who: r[0], tone }));
  const lords = (re: RegExp): Chip[] => (malicious.data?.rows ?? []).filter(([n]) => re.test(n))     // the Parasara drekkana, as most texts use
    .map(([n, lord]) => ({ text: `${lord} · from ${n.endsWith("Moon") ? "Moon" : "Lagna"}`, who: lord.split(" ")[0], tone: "bad" as const }));
  const facts: [string, Chip[]][] = [
    ["Exalted", exalted],
    ["Debilitated", debilitated],
    ["Vargottama", rows.filter(isVargottama).map((r) => ({ text: sensitive ? r.name : `${r.name} · ${SIGN_NAMES[r.rasi]}`, who: r.name }))],     // Starlight: the chart shows its sign
    ["Combust", combust],
    ["Graha war", war],
    [`Yuti ≤${CONJ_ORB}°`, pairs],
    ["Gandanta", rows.filter((r) => inGandanta(r.lon)).map((r) => ({ text: gandantaLabel(r), who: r.name }))],
    ...(sensitive ? [
      ["Pushkara bhaga", inBhaga(pushkara.data, "good")],
      ["Mrityu bhaga", inBhaga(mrityu.data, "bad")],
      ["64th navamsa lord", lords(/^The 64th navamsa/)],
      ["22nd drekkana lord", lords(/^The 22nd Para?r?sara drekkana/)],
      ...(["Primary marakas", "Secondary marakas"] as const).map((label, k): [string, Chip[]] => {
        const m = lagna && MARAKAS[lagna.rasi];
        return [label, m ? (m[k] as string[]).map((p) => ({ text: p, who: p, tone: "bad", title: m[2] })) : []];
      }),
      ["Dagdha rasis", (DAGDHA[tithi] ?? []).map((g) => ({ text: SIGN_NAMES[g], tone: "bad", title: `Burnt on ${TITHIS[tithi]}` }))],
      ["Marana karaka sthana", (insights.data ?? []).filter((g) => g.mks).map((g) => ({ text: `${g.name} · ${nth(g.bhava)}`, who: g.name, tone: "bad" }))],
    ] as [string, Chip[]][] : []),
  ];
  // the ⓘ beside each fact: its rule, then why each graha of this chart is in it
  const row = (n: string) => rows.find((r) => r.name === n);
  const dignity = (c: Chip, sign: (e: number) => number, what: string) => {
    const r = row(c.who ?? ""), e = EXALT[c.who ?? ""];
    if (!r || !e) return "";
    return `${r.name} at ${degIn(r.lon)} ${SIGN_NAMES[r.rasi]}: ${SIGN_NAMES[sign(e[0])]} is its ${what} sign${e[1] !== undefined ? `, deepest at ${e[1]}°` : ""}.`;
  };
  const combustWhy = (c: Chip) => {
    const r = row(c.who ?? "");
    if (!r || !sun) return "";
    const orb = COMBUST_ORB[r.name];
    return `${r.name} is ${lonSep(r.lon, sun.lon).toFixed(1)}° from the Sun${classical && orb ? ` (orb ${orb[r.retrograde ? 1 : 0]}°${r.retrograde ? ", retrograde" : ""})` : ""}.`;
  };
  const warWhy = (c: Chip) => {
    const r = row(c.who ?? "");
    if (!r) return "";
    const wins = c.tone === "good";
    const o = rows.find((x) => x !== r && x.name !== "Lagna" && (wins ? ahead(r.lon, x.lon) : ahead(x.lon, r.lon)) <= 1);
    return o ? `${r.name} is ${(wins ? ahead(r.lon, o.lon) : ahead(o.lon, r.lon)).toFixed(2)}° ${wins ? "ahead of" : "behind"} ${o.name}.` : "";
  };
  const ABOUT: Record<string, [string, (c: Chip) => string]> = {
    Exalted: ["A graha in its sign of exaltation is at its strongest (BPHS by degree: past the exaltation span, Moon in Taurus and Mercury in Virgo are moolatrikona).", (c) => dignity(c, (e) => e, "exaltation")],
    Debilitated: ["A graha in the sign opposite its exaltation is debilitated (neecha) and weakest.", (c) => dignity(c, (e) => (e + 6) % 12, "debilitation")],
    Vargottama: ["A graha in the same sign in the rasi (D1) and navamsa (D9) charts; this strengthens it.", (c) => { const r = row(c.who ?? ""); return r ? `${r.name} is in ${SIGN_NAMES[r.rasi]} in both D1 and D9.` : ""; }],
    Combust: [classical ? "A graha too close to the Sun loses strength. Classical orbs: Mo 12°, Ma 17°, Me 14° (12° retrograde), Ju 11°, Ve 10° (8° retrograde), Sa 15°."
      : "Fixed orb: Ma, Me, Ju, Ve, Sa within 6° of the Sun (Me not when retrograde, Ve only when retrograde).", combustWhy],
    "Graha war": ["Two grahas within 1° of each other are at war; the one further ahead in longitude wins.", warWhy],
    [`Yuti ≤${CONJ_ORB}°`]: [`Grahas within ${CONJ_ORB}° of each other in longitude (a close conjunction).`, () => ""],
    Gandanta: ["Within 3°20′ of a water–fire junction: the end of Cancer, Scorpio, Pisces or the start of Leo, Sagittarius, Aries.", () => ""],
    "Pushkara bhaga": ["A graha on the pushkara (nourishing) degree of its sign; auspicious.", () => ""],
    "Mrityu bhaga": ["A graha on the mrityu (death) degree of its sign; it gives troubled results.", () => ""],
    "64th navamsa lord": ["Lord of the sign holding the 64th navamsa from the Lagna or the Moon; a sensitive lord for danger and health.", () => ""],
    "22nd drekkana lord": ["Lord of the 22nd drekkana from the Lagna or the Moon (the 8th house's drekkana, Parasara's scheme); a sensitive lord for danger and health.", () => ""],
    "Primary marakas": ["The killers BPHS ch. 34 names for this lagna" + (lagna ? ` (${SIGN_NAMES[lagna.rasi]}): ${MARAKAS[lagna.rasi][2]}` : "."), () => ""],
    "Secondary marakas": ["Grahas that kill only with the 'etc.' / 'other malefics' of the verse, or by association with a killer (BPHS ch. 34).", () => ""],
    "Dagdha rasis": [`Signs burnt by the birth tithi${TITHIS[tithi] ? ` (${TITHIS[tithi]})` : ""}; grahas and houses there give weak results. Purnima and Amavasya burn none.`, () => ""],
    "Marana karaka sthana": ["The bhava where a graha suffers, by the bhava it occupies (not its sign from the Lagna): Su 12th, Mo 8th, Ma 7th, Me 7th, Ju 3rd, Ve 6th, Sa 1st, Ra 9th, Ke 4th.",
      (c) => { const g = insights.data?.find((x) => x.name === c.who); return g ? `${g.name} occupies the ${nth(g.bhava)} bhava.` : ""; }],
  };
  const about = (label: string, chips: Chip[]) => {
    const a = ABOUT[label];
    return a ? [a[0], ...chips.map(a[1]).filter(Boolean)].join("\n") : "";
  };
  const pending = (strengths.isPending && !strengths.data) || (aspects.isPending && !aspects.data) || (yuddha.isPending && !yuddha.data)
    || (!!sensitive && [pushkara, mrityu, malicious, insights].some((q) => q.isPending && !q.data));
  // Starlight lists every fact, an empty one with "-"; Key Info gathers the empty ones on a "None:" line
  const clear = pending || sensitive ? [] : facts.filter(([, c]) => !c.length).map(([l]) => l);
  return (
    <div className="chart-highlights">
      <div className="stat-strip hl-stats" aria-label="Highlights">
        <Stat onClick={toBalas} label="Strongest graha" t={1} value={byPct[0] ? graha(byPct[0].name) : "…"} sub={byPct[0] && `${byPct[0].percent.toFixed(0)}% shadbala`} />
        <Stat onClick={toBalas} label="Weakest graha" t={0} value={weakG ? graha(weakG.name) : "…"} sub={weakG && `${weakG.percent.toFixed(0)}% shadbala`} />
        <Stat onClick={toBalas} label="Strongest bhava" t={1} value={byHouse[0] ? `${nth(byHouse[0].house)} house${lordOf(byHouse[0].house)}` : "…"} sub={byHouse[0] && `${byHouse[0].rupas.toFixed(1)} rupas`} />
        <Stat onClick={toBalas} label="Weakest bhava" t={0} value={weakH ? `${nth(weakH.house)} house${lordOf(weakH.house)}` : "…"} sub={weakH && `${weakH.rupas.toFixed(1)} rupas`} />
      </div>
      <dl className="hl-rows">
        {facts.filter(([, c]) => c.length || (sensitive && !pending)).map(([label, chips]) => (
          <div key={label} className={sensitive ? `${GOOD_FACTS.has(label) ? "hl-good" : MIXED_FACTS.has(label) ? "hl-mixed" : "hl-bad"}${label === "Pushkara bhaga" ? " hl-break" : ""}` : undefined}><dt>{sensitive && <i className="hl-tone" />}{label}{about(label, chips) && <button type="button" className="hl-info" aria-label={`About ${label}`} data-tip={about(label, chips)}><Icon name="info" /></button>}</dt><dd>{!chips.length && "-"}{chips.map((c, i) => {
            if (!sensitive) return <span key={i} className={`hl-chip ${c.tone ?? ""}`} title={c.title}>{supOrd(c.text)}</span>;
            const [name, q] = shortNames(c.text).split(" · ");     // "Saturn · Aquarius": the detail in grey
            const text = <>{supOrd(name)}{q && <small>{supOrd(q)}</small>}</>;
            return c.who && MAIN_SET.has(c.who) && c.who !== "Lagna"
              ? <button key={i} type="button" className="hl-val" title={c.title} onClick={() => openGraha(c.who!)}>{text}</button>
              : <span key={i} className="hl-val" title={c.title}>{text}</span>;
          })}</dd></div>
        ))}
      </dl>
      {clear.length > 0 && <p className="muted hl-clear">None: {clear.join(" · ")}</p>}
      {pending && <p className="muted pad">Loading…</p>}
    </div>
  );
}

/** A body's first three cells as the Grahas tab draws them: its name in the colour of its relation to its sign's lord, retrograde, that relation, exalted or
 *  debilitated, combust; its chara karaka; moolatrikona or own sign. ``g`` (a graha's insights) is absent for the lagnas and points. */
export function GrahaCells({ r, g }: { r: Pick<KeyRow, "name" | "retrograde" | "karaka" | "dignity">; g?: GrahaInsight }) {
  const dig = g?.dignity ?? r.dignity;     // Uranus, Neptune and Pluto have no insights: theirs comes with the row, by the exaltations chosen in Options
  return (
    <>
      <td><span className={g ? "graha-name rel-" + g.relation.toLowerCase().replace(" ", "-") : "graha-name"} title={g && `In a ${g.relation === "Self" ? "sign it owns" : g.relation.toLowerCase() + "'s sign"}`}>{r.name}</span>
        {r.retrograde && <span className="retro-r" title="Retrograde"> (R)</span>}
        {g && g.relation !== "Self" && <span className={"kp-rel rel-" + g.relation.toLowerCase().replace(" ", "-")}>{g.relation}</span>}
        {dig === "Exalted" && <span className="kp-dig up" title="Exalted">↑</span>}
        {dig === "Debilitated" && <span className="kp-dig down" title="Debilitated">↓</span>}
        {g?.combust && <span className="kp-combust" title="Combust" />}
  </td>
      <td className="kp-tags">{r.karaka && <span className="kp-tag" title="Chara karaka">{r.karaka}</span>}</td>
      <td className="kp-tags">{g?.dignity === "Moolatrikona" && <span className="kp-tag moola" title="Moolatrikona">Moola</span>}
        {((g?.relation === "Self" && g.dignity !== "Moolatrikona") || dig === "Own") && <span className="kp-tag own" title="Own sign">Own</span>}</td>
    </>
  );
}

/** Key Info's views beyond the server's list (api.tables key_info). */
export const NATAL_VIEWS = [{ key: "natal_longitudes", name: "Natal Longitudes" }, { key: "natal_sahams", name: "Natal Sahamas" }];

/** Key Info. Everything it offers is on the right mouse button; in Starlight (``bare``) the views are picked
 *  on the tab row's More and come in as ``show``, the Grahas tab itself being the longitudes. */
export function KeyInfo({ bare, show, onPick, picked }: { b: Basics; bare?: boolean; show?: string; onPick?: (name: string) => void; picked?: string | null }) {
  const [saved, setView] = useSaved<string>("keyInfo", BASIC);
  const view = bare ? show ?? BASIC : saved;
  const [chosen, setDivision] = useState(1);
  const top = useTopVarga();
  const division = bare ? top : chosen;   // Starlight: the top left chart's varga
  const [form, setForm] = useState<"bodies" | "aspects" | null>(null);
  const [aspect, setAspect] = useState<AspectOpts>({ aspecting_varga: 1, aspected_varga: 1, aspecting_natal: false, aspected_natal: false });
  const { bodies, setBodies } = useBodies();
  const { open, node } = useMenu();
  const list = useQuery({ queryKey: ["tables"], queryFn: api.tables });
  const { birth, natal } = useChart();
  const chart = view === "natal_longitudes" || view === "natal_sahams" ? natal! : birth!;
  const keyRows = useQuery({ queryKey: ["keyInfo", chart, division], queryFn: () => api.keyInfo(chart, division), enabled: view === BASIC || view === "natal_longitudes", placeholderData: (p) => p });
  const isList = view === BASIC || view === "natal_longitudes";
  // Starlight's Planets tab: a graha's row opens to its insights
  const [opened, setOpened] = useKept<string>("grahaOpen", "");
  const insights = useQuery({ queryKey: ["grahaInsights", chart, division], queryFn: () => api.grahaInsights(chart, division), enabled: !!bare && isList, placeholderData: (p) => p });
  // the opened graha's row goes to the top of the box, its card under it, so neither needs scrolling to
  const table = useRef<HTMLTableElement>(null);
  const av = useQuery({ queryKey: ["ashtakavarga", chart, division, null], queryFn: () => api.ashtakavarga(chart, division, null), enabled: !!bare && isList, placeholderData: (p) => p });
  const balas = useQuery({ queryKey: ["strengths", chart], queryFn: () => api.strengths(chart), enabled: !!bare && isList, placeholderData: (p) => p });
  const vai = useQuery({ queryKey: ["table", chart, "vaiseshikamsa", 1, undefined], queryFn: () => api.table(chart, "vaiseshikamsa", 1), enabled: !!bare && isList, placeholderData: (p) => p });
  useEffect(() => {
    const row = bare && opened ? table.current?.querySelector<HTMLElement>("tr.opened") : null;
    if (!row) return;
    row.style.scrollMarginTop = `${table.current!.tHead?.offsetHeight ?? 0}px`;     // the header row sticks over the box's top: stop just under it, not behind it
    row.scrollIntoView({ block: "start", behavior: "smooth" });
  }, [bare, opened, !!insights.data]); // eslint-disable-line react-hooks/exhaustive-deps
  // Starlight: Uranus, Neptune and Pluto always, straight after Ketu (the server lists them last)
  const listed = (keyRows.data ?? []).filter((r) => bodies[r.group] !== false || (bare && r.group === "outer"));
  const outer = bare ? listed.filter((r) => r.group === "outer") : [], rest = listed.filter((r) => !outer.includes(r)), ketu = rest.findIndex((r) => r.name === "Ketu") + 1;
  const rows: KeyRow[] = [...rest.slice(0, ketu), ...outer, ...rest.slice(ketu)];
  const highlightRows = rows.filter((r) => MAIN_SET.has(r.name));
  const aspectOptions = view === "aspects" && (aspect.aspecting_varga !== 1 || aspect.aspected_varga !== 1 || aspect.aspecting_natal || aspect.aspected_natal) ? { ...aspect, natal } : undefined;
  const tableView = view === "natal_sahams" ? "sahams" : view;
  const chooser: { key: string; name: string }[] = [...(list.data?.key_info ?? []), ...NATAL_VIEWS];
  const bodiesItem: MenuEntry = { label: "Select bodies to be shown", onClick: () => setForm("bodies") };
  const divisionItem: MenuEntry = { label: "Divisional chart for longitudes", disabled: !isList, items: DIVISIONS.map((d) => ({ label: d === 1 ? "Rasi (D-1)" : `D-${d}`, checked: division === d, onClick: () => setDivision(d) })) };
  // Starlight: the bodies themselves, ticked, the menu staying open while they are toggled
  const bodyItems = (b: Record<string, boolean>, at: { clientX: number; clientY: number }): MenuEntry[] => BODY_BOXES.filter(([k]) => k !== "outer").map(([k, n]) => ({     // the outer grahas are always shown
    label: n, checked: b[k] !== false, keep: true,
    onClick: () => { const next = { ...b, [k]: b[k] === false }; setBodies(next); open(at, bodyItems(next, at), "Bodies shown"); },
  }));
  const menu: MenuEntry[] = bare ? [] : [
    bodiesItem,
    { label: "Longitudes & Basic Info", checked: view === BASIC, onClick: () => setView(BASIC) },
    { label: "Options for Graha Aspect Evaluation", onClick: () => setForm("aspects") },
    divisionItem,
    "-",
    ...chooser.map((v) => ({ label: v.name, checked: view === v.key, onClick: () => setView(v.key) })),
  ];
  return (
    <section className="pane key-stack" onContextMenu={(e) => { e.preventDefault(); if (bare && isList) { const at = { clientX: e.clientX, clientY: e.clientY }; open(at, bodyItems(bodies, at), "Bodies shown"); } else if (menu.length) open(e, menu, "Key Info menu"); }}>
      {!isList ? (bare && view === "nava_moon" ? <Taras chart={chart} /> : bare && view === "pushkaras" ? <Bhagas chart={chart} /> :<TableView view={tableView} chart={chart} options={aspectOptions} />) : <>
        <div className="scroll key-points">
          <table className="points" ref={table}>
            <thead><tr><th colSpan={3}>Body{bare && <> <small className="muted">(as per D-{division})</small></>}</th><th>Longitude</th><th>Nakshatra</th><th>{division === 1 ? "Navamsa" : `D9 of D${division}`}</th></tr></thead>
            <tbody>
              {rows.map((r) => {
                const [deg, sign, min, sec] = formatLon(r.lon).trim().split(/\s+/);
                const g = bare ? insights.data?.find((x) => x.name === r.name) : undefined, open = !!g && opened === r.name;
                const toggle = g && (() => setOpened(open ? "" : r.name));
                return [
                  <tr key={r.name} className={[r.name === "Lagna" && "lagna", picked === r.name && "picked", (onPick || g) && "pickable", open && "opened"].filter(Boolean).join(" ") || undefined}
                    onClick={onPick ? () => onPick(r.name) : toggle} aria-expanded={g ? open : undefined} tabIndex={g ? 0 : undefined}
                    onKeyDown={toggle && ((e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); toggle(); } })}>
                    <GrahaCells r={r} g={g} />
                    {/* Starlight: the sign opens the rashi's pop-up, read in this varga; the navamsa sign the navamsa's */}
                    <td className="num kp-deg">{deg}°{min.replace("'", "′")}<small>{sec.replace('"', "″")}</small> {bare
                      ? <button type="button" className="kp-sign nak-link" data-tip="What this rashi signifies" onClick={(e) => { e.stopPropagation(); openLore({ kind: "rashi", n: Math.floor((((r.lon % 360) + 360) % 360) / 30) + 1, d: division }); }}>{sign}</button>
                      : <span className="kp-sign">{sign}</span>}</td>
                    {/* Starlight: anywhere in the cell, its name or its pada pips, opens the nakshatra's pop-up (the Lagna's as "La", so its reading is marked) */}
                    <td className={bare ? "nak-cell" : undefined} onClick={bare ? (e) => { e.stopPropagation(); openLore({ kind: "nakshatra", n: Math.floor((((r.lon % 360) + 360) % 360) / (360 / 27)) + 1, from: r.name === "Lagna" ? "La" : MAIN_SET.has(r.name) ? r.name.slice(0, 2) : undefined }); } : undefined}>
                      {bare ? <button type="button" className="nak-link" data-tip="What this nakshatra signifies">{r.nakshatra}</button> : r.nakshatra}<span className="pips" role="img" aria-label={`pada ${r.pada}`} title={`Pada ${r.pada}`}>{[1, 2, 3, 4].map((p) => <i key={p} className={p <= r.pada ? "on" : undefined} />)}</span></td>
                    <td className={isVargottama(r) ? "kp-varga same" : "kp-varga"} title={isVargottama(r) ? "Vargottama: same sign as the longitude" : undefined}>{bare
                      ? <button type="button" className="nak-link" data-tip="What this rashi signifies" onClick={(e) => { e.stopPropagation(); openLore({ kind: "rashi", n: r.navamsa + 1, d: division === 1 ? 9 : 0 }); }}>{SIGN_NAMES[r.navamsa]}</button>
                      : SIGN_NAMES[r.navamsa]}</td>
                  </tr>,
                  open && <tr key={r.name + "+"} className="graha-more"><td colSpan={6}><GrahaCard g={g} all={insights.data!} onGo={setOpened} ak={av.data}
                    cusp={balas.data?.cusp_bala.find((c) => c.name === r.name)} vai={vai.data?.rows.find((x) => x[0] === r.name)} /></td></tr>,
                ];
              })}
            </tbody>
          </table>
        </div>
        {!bare && <ChartHighlights rows={highlightRows} />}
      </>}
      {node}
      {form === "bodies" && <BodiesDialog bodies={bodies} onOk={setBodies} onClose={() => setForm(null)} />}
      {form === "aspects" && <AspectOptions o={aspect} onOk={setAspect} onClose={() => setForm(null)} />}
    </section>
  );
}

const ORD = ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th", "10th", "11th", "12th"];

const short = (v: string) => v.replace(/\s*\([^)]*\)/g, "");          // "Baala (infant)" → "Baala"
const gloss = (v: string) => /\(([^)]*)\)/.exec(v)?.[1] ?? "";
const parts = (v: string) => (v && v !== "-" ? v.split(/,\s*(?![^(]*\))/) : []);     // "Swastha (comfortable), Vikala (crippled)" → its two moods
const BALA_NAMES: Record<string, string> = { sthana: "Sthana", kala: "Kaala", dig: "Dig", cheshta: "Cheshta", naisargika: "Naisargika", drig: "Drik", ishta: "Ishta", kashta: "Kashta (least)" };

const SEVEN = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"];     // the ashtakavarga's rows after the lagna's

/** A graha's insights, under its row in Starlight's Planets tab. ``onGo`` opens another graha's card: the stepper, or a graha named in this one. */
/** A share of its scale's top in quarters, q0 (red) to q3 (dark green), each quarter's top in it: 5 of 20 is red, 6 yellow; Shadbala's top is 200%, so above 100% is light green. */
const quarter = (f: number) => `q${Math.min(3, Math.max(0, Math.ceil(f * 4 - 1e-9) - 1))}`;

function GrahaCard({ g, all, onGo, ak, cusp, vai, inLore }: { g: GrahaInsight; all: GrahaInsight[]; onGo: (name: string) => void; ak?: AvView;
  cusp?: Strengths["cusp_bala"][number]; vai?: string[]; inLore?: boolean }) {
  useLanguage();     // its small lines are put into it whole (tr below)
  const flags: [string, boolean, string][] = [
    ["Maraka", g.maraka.length > 0, g.maraka.join(" · ")],
    [g.war === "Loses" ? "Lost a graha war" : "Won a graha war", !!g.war, "Within a degree of another graha."],
    ["Combust", g.combust, "Within combustion distance of the Sun."],
    ["Marana karaka sthana", g.mks, `In the ${ORD[g.bhava - 1]} bhava, where its significations suffer.`],
    ["Mrityu bhaga", g.mrityu, "On the degree of death of its sign."],
    ["64th navamsa / 22nd drekkana lord", g.malicious.length > 0, g.malicious.join(" · ")],
    ["Vargottama", g.vargottama, "The same sign in rasi and navamsa."],
    ["Pushkara bhaga", g.pushkara_bhaga, "On the nourishing degree of its sign."],
    ["Pushkaramsa", g.pushkara_amsa, "In a nourishing navamsa."],
  ];
  const good = new Set(["Vargottama", "Pushkara bhaga", "Pushkaramsa"]);
  const lit = flags.filter((f) => f[1]), clear = flags.filter((f) => !f[1]).map((f) => (f[0].startsWith("Won") ? "Graha war" : f[0]));
  const i = all.indexOf(g), step = (d: number) => onGo(all[(i + d + all.length) % all.length].name);
  const sb = g.shadbala;
  const row = SEVEN.indexOf(g.name) + 1, bav = row && ak ? ak.bav[row]?.[g.sign_no] : undefined, sav = ak?.sav[g.sign_no];     // the nodes have no BAV
  const savL = sav !== undefined && ak ? sav + ak.bav[0][g.sign_no] : undefined;     // the sarva with the lagna's own row added: 8 rows, 64 at most
  const vn = vai ? vaiCount(vai[VAI[0].col]) : 0, v16 = VAI[0];     // the shodasa varga scheme's rank
  const av = g.avasthas;
  const AV: [string, string][] = [["Age", "Baaladi (age)"], ["Alertness", "Jaagradadi (alertness)"], ["Mood", "Deeptaadi (mood)"], ["Activity", "Sayanadi (activity)"], ["Lajjitadi", "Lajjitadi"]];
  return (
    <article className={inLore ? "graha-card in-lore" : "graha-card"} style={{ ["--g" as string]: dotColor(g.name) }} tabIndex={-1} aria-label={`${g.name}: insights`} onClick={(e) => e.stopPropagation()}
      onKeyDown={(e) => { if (e.key === "ArrowLeft" || e.key === "ArrowRight") { e.preventDefault(); step(e.key === "ArrowLeft" ? -1 : 1); } }}>
      <div className="g-top">
        <div className="g-stats">
          <div className={sb ? quarter(Math.round(sb.percent) / 200) : undefined}>
            <span className="g-kicker">Shadbala</span>
            {sb ? <><b>{Math.round(sb.percent)}<small>%</small></b>
              <Meter t={0} fill={sb.percent / 200} mark={0.5} />
              <small>{tr(`${sb.rupas.toFixed(2)} of ${sb.required.toFixed(2)} rupas`)}</small></> : <><b className="muted">—</b><small>none for the nodes</small></>}
          </div>
          <div className={quarter(Number(g.vimsopaka.toFixed(1)) / 20)}>
            <span className="g-kicker">Vimsopaka</span>
            <b>{g.vimsopaka.toFixed(1)}<small>/20</small></b>
            <Meter t={0} fill={g.vimsopaka / 20} />
            <small>in the 16 vargas</small>
          </div>
          <div>
            <span className="g-kicker">Rules</span>
            <b>{supOrd(g.owns.length ? g.owns.map((h) => ORD[h - 1]).join(", ") : "—")}</b>
            <small>{g.owns.length && (g.name === "Rahu" || g.name === "Ketu") ? "as co-lord · " : ""}{supOrd(tr(`placed in ${ORD[g.house - 1]} bhava`))}{g.bhava !== g.house && supOrd(` (${ORD[g.bhava - 1]} by cusp)`)}</small>
          </div>
          <div className={bav !== undefined ? quarter(bav / 8) : undefined}>
            <span className="g-kicker">Ashtakavarga</span>
            {bav !== undefined ? <><b>{bav}<small>/8</small></b>
              <Meter t={0} fill={bav / 8} />
              <small>{tr(`its bindus in ${SIGN_NAMES[g.sign_no]}`)}</small></> : <><b className="muted">—</b><small>{row ? "…" : "none for the nodes"}</small></>}
          </div>
          <div className={savL !== undefined ? quarter(savL / 64) : undefined}>
            <span className="g-kicker">Sarva</span>
            {savL !== undefined ? <><b>{savL}<small>/32 avg · with Lagna</small></b>
              <Meter t={0} fill={savL / 64} mark={32 / 64} />
              <small>without Lagna {sav}/28 avg</small></> : <><b className="muted">—</b><small>…</small></>}
          </div>
          <div className={vn ? quarter(vn / v16.of) : undefined}>
            <span className="g-kicker">Vaiseshikamsa</span>
            {vn ? <><b>{v16.steps[vn - 2]}</b><Meter t={0} fill={vn / v16.of} /><small>good in {vn} of {v16.of} vargas</small></>
              : <><b className="muted">{vai ? "No rank" : "—"}</b><small>{vai ? "good in fewer than 2 of 16 vargas" : "…"}</small></>}
          </div>
        </div>
      </div>
      <dl className="g-avasthas" aria-label="Avasthas">
        {AV.map(([label, key]) => {
          const ps = parts(av[key]), t = ps.length ? ps.reduce((a, x) => a + avScore(x), 0) / ps.length : 0.5;     // as the Avasthas tab marks its cards
          return <div key={key} className={ps.length ? "tone" : undefined} style={ps.length ? toneStyle(t) : undefined}><dt>{label}{ps.length > 0 && <b>{avWord(t)}</b>}</dt>
            <dd>{ps.map((v) => <span key={v} title={gloss(v)}>{short(v)}<small>{gloss(v).split(" / ")[0]}</small></span>)}{!ps.length && "—"}</dd></div>;
        })}
      </dl>
      <div className="g-cols">
        <section aria-label="Aspects on it">
          <h4 className="g-kicker">Aspects on it <span>virupas of {g.aspect_full}</span></h4>
          {g.aspects_on.length ? <ul className="g-bars">{g.aspects_on.map((a) => (
            <li key={a.from} className={a.benefic ? "good" : "bad"}>
              <button type="button" className="g-who bare" title={`Open ${a.from}`} onClick={() => onGo(a.from)}>{a.from}</button>
              <span className="g-bar"><i style={{ width: `${Math.min(100, (a.value / g.aspect_full) * 100)}%` }} /></span>
              <b>{a.value}</b>
            </li>
          ))}</ul> : <p className="muted">No graha aspects it.</p>}
          {g.aspects_on.length > 0 && <p className="g-foot">
            <span className="good">Benefic {g.aspects_on.filter((a) => a.benefic).reduce((x, a) => x + a.value, 0)}</span>
            <span className="bad">Malefic {g.aspects_on.filter((a) => !a.benefic).reduce((x, a) => x + a.value, 0)}</span></p>}
        </section>
        <section aria-label="Its aspects on the bhavas">
          <h4 className="g-kicker">Its aspects on the bhavas</h4>
          <ol className="g-houses-bars">{g.aspects_houses.map((v, i) => (
            <li key={i} data-tip={`${ORD[i]} bhava cusp: ${Math.round((v / g.aspect_full) * 100)}%`} className={v >= g.aspect_full * 0.75 ? "full" : undefined}>
              <span><i style={{ height: `${Math.min(100, (v / g.aspect_full) * 100)}%` }} /></span>{i + 1}
            </li>
          ))}</ol>
          <p className="g-foot">{(() => { const top = g.aspects_houses.map((v, i) => [v, i] as const).filter(([v]) => v >= g.aspect_full * 0.75).map(([, i]) => ORD[i]);
            return top.length ? <>Strongest on the {supOrd(top.join(", "))}</> : <>No full aspect on any bhava</>; })()}</p>
          <div className={`g-cusp ${cusp ? quarter(Math.round(cusp.percent) / 100) : ""}`}>
            <span className="g-kicker">Bala WRT bhava cusp</span>
            {cusp ? <><b>{Math.round(cusp.percent)}<small>%</small></b>
              <Meter t={0} fill={cusp.percent / 100} />
              <small>{arc(Math.abs(cusp.from_cusp))} {cusp.from_cusp < 0 ? "before" : "past"} the {supOrd(ORD[cusp.house - 1])} cusp</small></> : <><b className="muted">—</b><small>…</small></>}
          </div>
        </section>
        {sb && <section aria-label="Shadbala make-up">
          <h4 className="g-kicker">Shadbala make-up <span>rank among the 7 grahas</span></h4>
          <ul className="g-parts">{sb.parts.map((x) => {
            const r = x.key === "kashta" ? 8 - x.rank : x.rank;     // the least kashta is the best
            return (
              <li key={x.key}><span>{BALA_NAMES[x.key]}</span><b>{x.value.toFixed(1)}</b>
                <span className="g-rank tone" style={toneStyle((7 - r) / 6)} title={x.key === "kashta" ? `${ORD[x.rank - 1]} highest kashta` : `${ORD[x.rank - 1]} of the seven`}>{supOrd(ORD[r - 1])}</span></li>
            );
          })}</ul>
        </section>}
      </div>
      <section className="g-conditions" aria-label="Conditions">
        {lit.length ? <ul>{lit.map(([label, , why]) => (
          <li key={label} className={good.has(label) ? "good" : "bad"}><b>{supOrd(label)}</b>{why && <span>{supOrd(why)}</span>}</li>
        ))}</ul> : <p className="g-none">No affliction or special condition.</p>}
        <p className="g-clear"><span>Not</span> {supOrd(clear.join(" · "))}</p>
      </section>
      {!inLore && <p className="g-lore"><button type="button" className="nak-link" onClick={() => openLore({ kind: "graha", n: Object.keys(ABBR_NAME).find((k) => ABBR_NAME[k] === g.name) ?? g.name })}>All about {g.name === "Sun" || g.name === "Moon" ? `the ${g.name}` : g.name}: its nature, significations and readings</button></p>}
    </article>
  );
}

/** A graha's card as it opens under its row on the Grahas tab, read in the rasi: the lore panel's Strengths tab. ``onGo`` opens another graha. */
export function GrahaStrengths({ name, onGo }: { name: string; onGo: (name: string) => void }) {
  const birth = useChart((s) => s.birth)!;
  const insights = useQuery({ queryKey: ["grahaInsights", birth, 1], queryFn: () => api.grahaInsights(birth, 1) });
  const av = useQuery({ queryKey: ["ashtakavarga", birth, 1, null], queryFn: () => api.ashtakavarga(birth, 1, null) });
  const balas = useQuery({ queryKey: ["strengths", birth], queryFn: () => api.strengths(birth) });
  const vai = useQuery({ queryKey: ["table", birth, "vaiseshikamsa", 1, undefined], queryFn: () => api.table(birth, "vaiseshikamsa", 1) });
  return <Loaded q={insights}>{(all) => {
    const g = all.find((x) => x.name === name);
    return g ? <GrahaCard g={g} all={all} onGo={onGo} ak={av.data} cusp={balas.data?.cusp_bala.find((c) => c.name === name)}
      vai={vai.data?.rows.find((x) => x[0] === name)} inLore /> : <p className="muted">Not read for {name}.</p>;
  }}</Loaded>;
}

const BASIC_CORE = ["Date", "Time", "Place", "Tithi"];

/** The few facts of the chart; hovering or focusing the card drops the rest of them over what is below. */
export function CoreInfo({ b }: { b: Basics }) {
  const { mode, meta } = useChart();
  const place = [meta.city, meta.state, meta.country].filter(Boolean).join(", ");
  const list = (rows: [string, string][], city?: boolean) => (
    <dl className="core">
      {rows.map(([k, v]) => (
        <div key={k}><dt>{k}</dt><dd>{supOrd(v)}{city && k === "Place" && place && <><br />{place}</>}</dd></div>
      ))}
    </dl>
  );
  const rest = b.core.filter(([k]) => !BASIC_CORE.includes(k));
  return (
    <section className="pane core-card" tabIndex={0} aria-label="Chart details">
      <header className="pane-head core-head"><h2>{b.name || "Core Info"}</h2><span className="core-mode">{mode?.title ?? "Natal Chart"}</span></header>
      {list(b.core.filter(([k]) => BASIC_CORE.includes(k)), true)}
      {rest.length > 0 && <div className="core-more pane">{list(rest)}</div>}
    </section>
  );
}

const LEVEL_TAGS = ["MD", "AD", "PD"];
const AV_ROWS = ["As", "Su", "Mo", "Ma", "Me", "Ju", "Ve", "Sa"];

/** Any dasa of the chart at a glance (the best one to begin with): three columns, mahadasa to pratyantardasa, each period with its start. */
export function BestDasaGlance() {
  const birth = useChart((s) => s.birth)!;
  const best = useQuery({ queryKey: ["bestDasa", birth], queryFn: () => api.bestDasa(birth) });
  const list = useQuery({ queryKey: ["dasaList"], queryFn: api.dasaList });
  const [picked, setPicked] = useSaved<string>("glanceDasa", "");   // "": the best one
  const [sel, setSel] = useState<number[] | null>(null);           // the branch opened by hand, else the running one
  const key = picked || best.data?.best[0];
  const now = useQuery({
    queryKey: ["dasaRunning", birth, key],
    queryFn: () => {
      const t = new Date();
      return api.locate(birth, key!, { year: t.getUTCFullYear(), month: t.getUTCMonth() + 1, day: t.getUTCDate(), hour_local: t.getUTCHours() + t.getUTCMinutes() / 60, tz_east_hours: 0 }, 3);
    },
    enabled: !!key, staleTime: 0,
  });
  useEffect(() => setSel(null), [birth, key]);
  const run = now.data?.path ?? [];
  const open = sel ?? (run.length ? run.slice(0, -1) : [0, 0]);   // no period running now (an old chart): open the first branch
  const levels = useQueries({
    queries: [[], ...open.map((_, n) => open.slice(0, n + 1))].map((p) => ({
      queryKey: ["dasa", birth, key, p, undefined, 0], queryFn: () => api.dasa(birth, key!, p), enabled: !!key && !!now.data,
    })),
  });
  const isBest = (k: string) => !!best.data?.best.includes(k);
  // the deepest running period whose level is on screen (all of them, unless another branch was opened by hand)
  let cur: { d: number; p: DasaPeriod } | undefined;
  for (let d = run.length - 1; d >= 0 && !cur; d--) {
    const p = levels[d]?.data?.periods[run[d]];
    if (p && run.slice(0, d).every((x, k) => x === open[k])) cur = { d, p };
  }
  const t = Date.now(), ms = (iso: string) => new Date(iso).getTime();   // the chart's local dates; the viewer's clock is near enough for a bar
  return (
    <div className="best-glance">
      {!!run.length && <div className="glance-now">
        <span className="glance-now-label">Now</span>
        <strong>{now.data!.labels.join(" › ")}</strong>
        {cur && <span className="muted" title={`${LEVEL_TAGS[cur.d]} ${cur.p.label}: ${cur.p.start.slice(0, 10)} to ${cur.p.end.slice(0, 10)}`}>{LEVEL_TAGS[cur.d]} · {timeLeft(ms(cur.p.end) - t)} left</span>}
        {cur && <span className="progress" aria-hidden="true"><i style={{ width: `${Math.min(100, Math.max(0, (t - ms(cur.p.start)) / (ms(cur.p.end) - ms(cur.p.start)) * 100))}%` }} /></span>}
      </div>}
      <select aria-label="Dasa" value={key ?? ""} onChange={(e) => setPicked(e.target.value)}>
        {(["nakshatra", "rasi", "other"] as const).map((g) => (
          <optgroup key={g} label={{ nakshatra: "Nakshatra dasas", rasi: "Rasi dasas", other: "Other dasas" }[g]}>
            {list.data?.filter((d) => d.group === g).map((d) => <option key={d.key} value={d.key}>{isBest(d.key) ? "★ " : ""}{d.title}</option>)}
          </optgroup>
        ))}
      </select>
      <div className="glance-cols">
        {levels.map((q, d) => (
          <div key={d} className="glance-col">
            <span className="glance-tag">{LEVEL_TAGS[d]}</span>
            {q.data?.periods.map((p, i) => (
              <button key={i} className={[open[d] === i && "open", run[d] === i && run.slice(0, d).every((x, k) => x === open[k]) && "on"].filter(Boolean).join(" ")}
                disabled={!q.data!.can_split || d > 1} title={`${formatMoment(p.start)} - ${formatMoment(p.end)}`}
                onClick={() => setSel([...open.slice(0, d), i])}>
                <b>{p.label}</b><span>{p.start.slice(0, 10)}</span>
              </button>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}

const AV_VIEWS: { id: "av" | "best"; name: string; icon: IconName }[] = [{ id: "av", name: "Ashtakavarga", icon: "charts4" }, { id: "best", name: "Best dasa", icon: "star" }];

/** The small ashtakavarga: SAV and the eight BAVs, each shading the signs of its graha. */
export function AvGrids({ b }: { b: Basics }) {
  const { signs, bav, sav } = b.av;
  const grids = [{ t: "SAV", f: (s: number) => sav[s], shade: new Set(signs.slice(1)) },
    ...AV_ROWS.map((t, i) => ({ t, f: (s: number) => bav[i][s], shade: new Set([signs[i]]) }))];
  return (
    <div className="av-fit"><div className="av-grids">
      {grids.map((g) => <SouthGrid key={g.t} title={g.t} compact shaded={g.shade} cell={(s) => [String(g.f(s))]} />)}
    </div></div>
  );
}

export function SmallAv({ b }: { b: Basics }) {
  const [view, setView] = useSaved<"av" | "best">("avPane", "av");
  const event = useChart((s) => s.mode?.event);
  // the best-dasa method is about a birth chart, as on the Dasas screen
  const showBest = view === "best" && !event;
  return (
    <section className="pane">
      <header className="pane-head"><h2>{showBest ? "Best dasa" : "Ashtakavarga"}</h2>
        {!event && <span className="seg" role="tablist" aria-label="Ashtakavarga or best dasa">
          {AV_VIEWS.map((v) => (
            <button key={v.id} role="tab" aria-selected={showBest === (v.id === "best")} aria-label={v.name} title={v.name} onClick={() => setView(v.id)}><Icon name={v.icon} /></button>
          ))}
        </span>}
      </header>
      {showBest ? <BestDasaGlance /> : <AvGrids b={b} />}
    </section>
  );
}
