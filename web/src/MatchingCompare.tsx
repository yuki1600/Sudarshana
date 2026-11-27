import { type ReactNode } from "react";
import { useQueries } from "@tanstack/react-query";
import { api, type Birth, type MatchCompare, type MatchKuja, type MatchSide } from "./api";
import { ChartPanelView } from "./ChartPane";
import { ChartGrid } from "./ChartGrid";
import { REFS, useBhavaRef } from "./Starlight";
import { SIGN_NAMES, SIGNS } from "./format";
import { signName } from "./names";
import { useSaved } from "./hooks";
import { useChart } from "./store";
import { AspectGrid } from "./Windows";
import { house, nakshatraOf, natural, SIGN_LORD } from "./calcMath";
import { Dignity, SubTabs, supOrd, WhoAge } from "./ui";
import { type Focus, KUTA_LABEL, KUTA_ORDER, type Kind, type Side } from "./matchingShared";
import { Strength, toneWord } from "./MatchingFactors";
import { num, toneA, toneD } from "./MatchingKutas";
import { ABBR_NAME } from "./Panels";
import { PartnerName } from "./MatchingPartners";

const ordinal = (n: number) => `${n}${n % 100 >= 11 && n % 100 <= 13 ? "th" : ["th", "st", "nd", "rd"][n % 10] ?? "th"}`;
const placeClass = (h: number) => ([6, 8, 12].includes(h) ? "dusthana" : [1, 4, 5, 7, 9, 10].includes(h) ? "kendra/trikona" : "neutral");
const both = (p: string): Focus => ({ girl: p.slice(0, 2), boy: p.slice(0, 2) });   // "Mars" -> "Ma", as the charts write it
const hoverProps = (f: Focus, onFocus: (f: Focus) => void) => ({
  onMouseEnter: () => onFocus(f), onMouseLeave: () => onFocus(null), onFocus: () => onFocus(f), onBlur: () => onFocus(null),
});

/** graha drishti: houses counted from the graha that it looks at in full (Rahu and Ketu left out) */
const DRISHTI: Record<string, number[]> = { Sun: [7], Moon: [7], Mercury: [7], Venus: [7], Mars: [4, 7, 8], Jupiter: [5, 7, 9], Saturn: [3, 7, 10] };

/** Mars, Jupiter and Saturn's extra virupas in their special-aspect arcs, as core_logic's _SPECIAL_ASPECT_BONUS */
const SPECIAL: Record<string, [number, [number, number][]]> = {
  Mars: [15, [[90, 120], [210, 240]]], Jupiter: [30, [[120, 150], [240, 270]]], Saturn: [45, [[60, 90], [270, 300]]],
};
/** sphuta drishti in % (BPHS 26, as core_logic's compute_parasara_drik_virupas): how fully graha q at `from` looks at `to` */
function drishti(q: string, from: number, to: number) {
  const d = (((to - from) % 360) + 360) % 360;
  let v = d < 30 || d >= 300 ? 0 : d < 60 ? (d - 30) / 2 : d < 90 ? d - 45 : d < 120 ? (120 - d) / 2 + 30 : d < 150 ? 150 - d : d < 180 ? (d - 150) * 2 : (300 - d) / 2;
  const [bonus, arcs] = SPECIAL[q] ?? [0, []];
  if (arcs.some(([lo, hi]) => lo <= d && d < hi)) v += bonus;
  return Math.round((Math.min(60, v) / 60) * 100);
}
const ab = (p: string) => p.slice(0, 2);     // "Mars" -> "Ma"
const ords = (hs: number[]) => hs.map(ordinal).join(", ");

/** One fact of a partner's graha (or bhava): its category, what it is, what the category means (on hover) and whether it is
 *  good, middling or bad for the graha; null when there is nothing to say.
 *  Both partners' lists come from the same function, so the i-th fact of each is the same category. */
type Tone = "good" | "mid" | "bad" | undefined;
type Fact = [string, ReactNode, string?, Tone?] | null;

/** a placement: a kendra or trikona good, a dusthana bad, the rest plain */
const placeTone = (h: number): Tone => (placeClass(h) === "dusthana" ? "bad" : placeClass(h) === "neutral" ? undefined : "good");
/** a dignity: exalted, moolatrikona, own sign (or vargottama) good, debilitated bad */
const dignityTone = (d?: string, vargottama?: boolean): Tone => (d === "Debilitated" ? "bad" : d || vargottama ? "good" : undefined);
/** the avasthas (BPHS 45.3-10): young and adolescent good, infant middling, old and dead bad (as BPHS 11.14-16 reads them);
 *  awake good, dreaming middling, asleep bad; the moods of an exalted, own, great friend's or friend's sign good, the rest bad */
const AGE: Record<string, Tone> = { Yuva: "good", Kumara: "good", Baala: "mid", Vriddha: "bad", Mrita: "bad" };
const ALERT: Record<string, Tone> = { Jaagrita: "good", Swapna: "mid", Sushupta: "bad" };
const GOOD_MOOD = ["Deepta", "Swastha", "Pramudita", "Saanta"];
const moodTone = (m: string): Tone => {
  const ms = m.split(", ").map((x) => x.split(" (")[0]), n = ms.filter((x) => GOOD_MOOD.includes(x)).length;
  return n === ms.length ? "good" : n ? "mid" : "bad";
};
/** a lord by its functional nature for the lagna (Laghu Parasari; BPHS 34): benefic or yogakaraka good, malefic bad. The 8th
 *  lord is evil unless it is also the lagna lord, the Sun and the Moon free of it: bad, or middling beside a trikona's good. */
const lordTone = (q: string, nature: string | null, rules: number[]): Tone => {
  const eighth = rules.includes(8) && !rules.includes(1) && q !== "Sun" && q !== "Moon";
  if (nature === "Functional Malefic") return "bad";
  if (nature === "Functional Benefic" || nature === "Yogakaraka") return eighth ? "mid" : "good";
  return eighth ? "bad" : undefined;
};
/** a graha in a nakshatra: its own good, its natural friend's good, its natural enemy's bad (BPHS 3.55); Rahu and Ketu have none */
const STAR_REL: Record<number, [string, Tone]> = { 1: ["a friend's", "good"], 0: ["a neutral's", undefined], [-1]: ["an enemy's", "bad"] };
const starOf = (q: string, lord: string): [string, Tone] =>
  q === lord ? ["its own", "good"] : [q, lord].some((x) => x === "Rahu" || x === "Ketu") ? [`${lord}'s`, undefined] : STAR_REL[natural(q, lord)];

type Births = { girl: Birth; boy: Birth };

/** "the 3rd & 8th" bhavas a graha rules from its lagna */
const rulesOf = (lagna: number, q: string) => SIGN_LORD.flatMap((l, x) => (l === q ? [house(lagna, x)] : [])).sort((x, y) => x - y);

/** Lagna or a graha in one partner's rasi or navamsa: its cells for the table, and its longitude there for the aspects. */
function place(p: string, s: MatchSide, nav: boolean) {
  const lagna = nav ? s.d9_lagna : s.lagna;
  const signOf = (q: string) => (q === "Lagna" ? lagna : nav ? s.planets[q].d9_sign : s.planets[q].sign);
  // shortcut: the navamsa longitude as the plain 9-fold one; no % where that misses the chart's own D-9 sign (another navamsa option)
  const lonOf = (q: string) => {
    const l = q === "Lagna" ? s.lagna_lon : s.planets[q].lon;
    if (!nav) return l;
    const l9 = (l * 9) % 360;
    return Math.floor(l9 / 30) === signOf(q) ? l9 : null;
  };
  const sign = signOf(p), others = Object.keys(s.planets).filter((q) => q !== p);
  const with_ = others.filter((q) => signOf(q) === sign);
  const looks = (q: string) => { const from = lonOf(q), to = lonOf(p); return from != null && to != null ? drishti(q, from, to) : null; };
  // the lagna is a point: every graha whose sphuta drishti reaches its degree, strongest first; a graha, those that look at its sign in full
  const point = p === "Lagna" && lonOf(p) != null;
  const seen = point ? others.filter((q) => DRISHTI[q] && looks(q)! > 0).sort((x, y) => looks(y)! - looks(x)!)
    : others.filter((q) => DRISHTI[q]?.includes(house(signOf(q), sign)));
  const me = p === "Lagna" ? null : s.planets[p];
  const dignity = me && (nav ? me.d9_dignity : me.dignity);
  const rules = p === "Lagna" ? [] : rulesOf(lagna, p);
  const n = nakshatraOf(p === "Lagna" ? s.lagna_lon : me!.lon), star = me ? starOf(p, n.lord) : null;
  const nature = me && (nav ? me.d9_nature : me.nature);
  const aspect = (q: string, i: number) => {
    const v = looks(q), hs = rulesOf(lagna, q);
    return (
      <span key={q} className="mc-asp" title={`${q}'s ${ordinal(house(signOf(q), sign))} house aspect${hs.length ? `, lord of the ${ords(hs)}` : ""}`}>
        <b>{ab(q)}</b>{v != null && <> ({v}%)</>}{i < seen.length - 1 && ","}
      </span>
    );
  };
  return {
    sign, house: p === "Lagna" ? 1 : nav ? me!.d9_house : me!.house, lon: lonOf(p),
    cells: [
      ["Bhava", <b>{supOrd(ordinal(p === "Lagna" ? 1 : nav ? me!.d9_house : me!.house))}</b>, undefined, me ? placeTone(nav ? me.d9_house : me.house) : undefined],
      ["Sign", <>{SIGN_NAMES[sign]}<Dignity d={dignity} vg={!!(nav && me && me.sign === me.d9_sign)} /></>, undefined,
        me ? dignityTone(dignity ?? undefined, nav && me.sign === me.d9_sign) : undefined],
      rules.length ? ["Lord of", <span title={nature ?? undefined}>{supOrd(ords(rules))}</span>,
        "The bhavas it rules from its lagna: green a functional benefic or yogakaraka, red a functional malefic or the 8th lord", lordTone(p, nature, rules)] : null,
      nav ? null : ["Star", <span title={star ? `In ${star[0]} nakshatra` : undefined}>{n.name} {n.pada} <small>{ab(n.lord)}</small></span>,
        "Nakshatra, its pada and its lord: green its own or a friend's, red an enemy's", star?.[1]],
      with_.length ? ["With", with_.map(ab).join(" "), "Grahas in the same sign"] : null,
      seen.length ? ["Aspected by", <span className="mc-asps">{seen.map(aspect)}</span>, point
        ? "Every graha whose sphuta drishti reaches the lagna's degree, and how fully; on hover, which of its aspects it is"
        : "Who looks at its sign (graha drishti), and how fully its sphuta drishti reaches it; on hover, which of its aspects it is"] : null,
    ] as Fact[],
  };
}

/** the navamsa's bhava and sign of a graha (or the lagna), labelled apart from the rasi's */
const navCells = (cells: Fact[]): Fact[] => cells.slice(0, 2).map((f) => (f ? [`D-9 ${f[0].toLowerCase()}`, f[1], f[2], f[3]] : null));

/** The overview atop the Grahas and Bhavas tabs: a row each, the girl's columns, the graha (or bhava) in the middle, the boy's columns in the same order. */
function SumTable({ label, births, cols, rows, onFocus }: {
  label: string; births: Births; cols: [string, string][]; onFocus: (f: Focus) => void;
  rows: { key: string; head: ReactNode; girl: [ReactNode, Tone?][]; boy: [ReactNode, Tone?][]; focus: Focus }[];
}) {
  const side = (cells: [ReactNode, Tone?][], who: string) => cells.map(([v, t], i) => <td key={`${who}${i}`} className={who}><span className={`mc-box${t ? ` ${t}` : ""}`}>{v ?? <small>–</small>}</span></td>);
  const heads = (who: string) => cols.map(([n, hint]) => <th key={`${who}${n}`} scope="col" className={who} data-tip={hint}>{n}</th>);
  return (
    <div className="mc-tablewrap">
      <table className="mc-sum" aria-label={label}>
        <thead>
          <tr><th scope="colgroup" colSpan={cols.length} className="girl"><WhoAge who="Girl" birth={births.girl} /></th><th /><th scope="colgroup" colSpan={cols.length} className="boy"><WhoAge who="Boy" birth={births.boy} /></th></tr>
          <tr className="mc-sum-cols">{heads("girl")}<th />{heads("boy")}</tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.key} tabIndex={0} {...hoverProps(r.focus, onFocus)}>
              {side(r.girl, "girl")}<th scope="row">{r.head}</th>{side(r.boy, "boy")}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

const AMSA_TONE = (vai?: MatchSide["planets"][string]["vaiseshikamsa"]): Tone => (!vai ? undefined : vai.dasa_n >= 4 || vai.shodasa_n >= 7 ? "good" : vai.dasa || vai.shodasa ? "mid" : "bad");
const VIM_TONE = { strong: "good", middling: "mid", weak: "bad" } as const;

/** The grahas' strengths at a glance: Shadbala against what each needs, Vimsopaka (of 20) and the vaiseshikamsa reached (of the 10 vargas, the 16 on hover). */
function GrahaSum({ c, births, onFocus }: { c: MatchCompare; births: Births; onFocus: (f: Focus) => void }) {
  const g = c.grid;
  const cells = (p: string, s: MatchSide): [ReactNode, Tone?][] => {
    const x = s.planets[p], need = g.need[p], v = x.vimsopaka, vai = x.vaiseshikamsa;
    return [
      x.rupas != null && need != null ? [<Strength kind="graha" pct={pct(x.rupas, need)} tip={`${p}'s Shadbala: ${x.rupas.toFixed(2)} of the ${need} rupas it needs`} />] : [null],
      v != null ? [<>{v.toFixed(1)}<small>/20</small></>, VIM_TONE[band(v)]] : [null],
      vai ? [<span data-tip={[`In its own or exalted sign in ${vai.shodasa_n} of the 16 vargas`, vai.shodasa && `${vai.shodasa} (of the 16)`, vai.dasa && `${vai.dasa} (of the 10)`].filter(Boolean).join(": ")}>{vai.shodasa_n}/16</span>, AMSA_TONE(vai)] : [null],
    ];
  };
  const shown = g.bodies.filter((p) => [g.girl, g.boy].some((s) => s.planets[p]?.rupas != null || s.planets[p]?.vimsopaka != null));
  return (
    <SumTable label="Strengths of the grahas" births={births} onFocus={onFocus}
      cols={[["Shadbala", "The graha's rupas as a share of what it needs: the ring closes at the minimum (100%), a darker second lap past it"], ["Vimsopaka", "Of 20 by the 16 vargas: strong from 15, weak under 10"],
        ["Vaiseshikamsa", "Of the 16 vargas, how many have it in a good sign (own, exalted and the like); its name on hover; good from 7"]]}
      rows={shown.map((p) => ({ key: p, head: ab(p), girl: cells(p, g.girl), boy: cells(p, g.boy), focus: both(p) }))} />
  );
}

/** The bhavas at a glance: Bhava Bala against its 7 rupas, the cusp's sign and degree, the lord, who is in it. */
function BhavaSum({ c, births, onFocus }: { c: MatchCompare; births: Births; onFocus: (f: Focus) => void }) {
  const g = c.grid, display = useChart((s) => s.display);
  const cells = (h: MatchSide["houses"][number], s: MatchSide): [ReactNode, Tone?][] => {
    const cs = h.cusp != null ? Math.floor(h.cusp / 30) % 12 : null;
    return [
      h.rupas != null ? [<Strength kind="bhava" pct={pct(h.rupas, 7)} tip={`The ${ordinal(h.house)} bhava's Bhava Bala: ${h.rupas.toFixed(2)} of the 7 rupas it needs, ${ordinal(h.rank!)} strongest of 12`} />] : [null],
      cs != null ? [<span data-tip={`Cusp at ${Math.floor(h.cusp! % 30)}° ${SIGN_NAMES[cs]}`}>{signName(cs, SIGNS[cs], display)} {Math.floor(h.cusp! % 30)}°</span>] : [null],
      [<b data-tip={`${h.lord} in the ${ordinal(h.lord_house)}`}>{ab(h.lord)} <small>{supOrd(ordinal(h.lord_house))}</small></b>, lordTone(h.lord, s.planets[h.lord]?.nature ?? null, rulesOf(s.lagna, h.lord))],
    ];
  };
  return (
    <SumTable label="The bhavas at a glance" births={births} onFocus={onFocus}
      cols={[["Bhava Bala", "The bhava's rupas as a share of the 7 it needs: the house fills to the eaves at the minimum (100%), into the roof past it"], ["Cusp", "The cusp's sign and degree in the chosen house system"],
        ["Lord", "The bhava's lord and the bhava it sits in: green a functional benefic or yogakaraka for the lagna, red a functional malefic or the 8th lord"]]}
      rows={g.girl.houses.map((a, i) => ({ key: String(a.house), head: supOrd(ordinal(a.house)), girl: cells(a, g.girl), boy: cells(g.boy.houses[i], g.boy),
        focus: { girl: ab(a.lord), boy: ab(g.boy.houses[i].lord) } }))} />
  );
}

/** A table of a pair of lines per graha (or bhava): its name once at the left, the girl's values on the first line, the boy's
 *  on the second, a column per category (what it reads on its head's hover); the table's name in the corner. */
type Cell = [ReactNode, Tone?, string?];     // the value, its tone, the whole of it on hover
function DuoTable({ label, cols, rows, onFocus }: {
  label: string; cols: [string, string][]; onFocus: (f: Focus) => void;
  rows: { key: string; head: ReactNode; girl: Cell[]; boy: Cell[]; focus: Focus }[];
}) {
  const line = (cells: Cell[]) => cells.map(([v, t, tip], i) => (
    <td key={i}><span className={`mc-box${t ? ` ${t}` : ""}`} data-tip={tip}>{v ?? <small>–</small>}</span></td>
  ));
  return (
    <div className="mc-tablewrap">
      <table className="mc-sum mc-duo" aria-label={label}>
        <thead>
          <tr className="mc-sum-cols"><th scope="col" colSpan={2} className="mc-duo-name" />{cols.map(([n, hint]) => <th key={n} scope="col" data-tip={hint}>{n}</th>)}</tr>
        </thead>
        {rows.map((r) => (
          <tbody key={r.key} tabIndex={0} {...hoverProps(r.focus, onFocus)}>
            <tr><th scope="rowgroup" rowSpan={2}>{r.head}</th><td className="mc-who">Girl</td>{line(r.girl)}</tr>
            <tr><td className="mc-who">Boy</td>{line(r.boy)}</tr>
          </tbody>
        ))}
      </table>
    </div>
  );
}

/** Each partner's grahas aspecting the other's grahas (``part`` 0) or bhavas (1), drawn as the Home tab's Aspects: the girl's
 *  table and its totals, then the boy's. */
const CrossAspects = ({ c, part }: { c: MatchCompare; part: 0 | 1 }) => (
  <div className="mc-tablewrap mc-aspects">
    <div><AspectGrid t={c.cross.girl} part={part} head="Girl's aspects" total="Total on boy's" /></div>
    <div><AspectGrid t={c.cross.boy} part={part} head="Boy's aspects" total="Total on girl's" /></div>
  </div>
);

/** One group of tables in the Grahas or Bhavas tab, boxed apart from the next, its name small above; ``tabs`` on the same rule, at the right. */
const Section = ({ name, tabs, cls, children }: { name: string; tabs?: ReactNode; cls?: string; children: ReactNode }) => (
  <section className={`mc-section${cls ? ` ${cls}` : ""}`} aria-label={name}>
    {tabs ? <div className="mc-section-head"><h5 className="mc-section-name">{name}</h5>{tabs}</div> : <h5 className="mc-section-name">{name}</h5>}
    {children}
  </section>
);

/** a fact of place() as a cell: its value and tone, or none */
const factCell = (cells: Fact[], label: string): Cell => { const f = cells.find((x) => x?.[0] === label); return f ? [f[1], f[3]] : [null]; };
/** several names ("Deena (sad), Vikala (crippled)") as their first words, the whole on hover */
const firsts = (v?: string) => (v ? v.split(", ").map(short).join(", ") : null);
/** Lajjitadi (BPHS 45.11-18): proud and delighted good; ashamed, starved, thirsty and agitated bad; both middling; peaceful plain */
const LAJ_GOOD = ["Garvita", "Mudita"], LAJ_BAD = ["Lajjita", "Kshudhita", "Trushita", "Kshobhita"];
const lajTone = (v?: string): Tone => {
  const ns = (v ?? "").split(", ").map(short), good = ns.some((n) => LAJ_GOOD.includes(n)), bad = ns.some((n) => LAJ_BAD.includes(n));
  return good && bad ? "mid" : good ? "good" : bad ? "bad" : undefined;
};

/** The five avasthas of a graha (BPHS 45): age, alertness and mood by Parashara, activity (Sayanadi) and Lajjitadi. */
function avasthaCells(p: string, s: MatchSide): Cell[] {
  const x = s.planets[p];
  return [
    [x.age ? short(x.age) : null, AGE[short(x.age)], x.age],
    [x.alertness ? short(x.alertness) : null, ALERT[short(x.alertness)], x.alertness],
    [firsts(x.mood), x.mood ? moodTone(x.mood) : undefined, x.mood],
    [x.activity ? short(x.activity) : null, undefined, x.activity],
    [firsts(x.lajjitadi), lajTone(x.lajjitadi), x.lajjitadi],
  ];
}

/** Graha by graha, each a table: the strengths (Shadbala, Vimsopaka, Vaiseshikamsa), the five avasthas, the place in the rasi
 *  and navamsa (bhava, sign, lordship, star), between, each partner's grahas aspecting the other's. */
export function GrahaGrid({ c, births, onFocus }: { c: MatchCompare; births: Births; onFocus: (f: Focus) => void }) {
  const g = c.grid;
  const facts = (p: string, s: MatchSide) => [...place(p, s, false).cells, ...navCells(place(p, s, true).cells)];
  const pointRows = (fn: (p: string, s: MatchSide) => Cell[]) => ["Lagna", ...g.bodies].map((p) => ({
    key: p, head: p === "Lagna" ? "Lagna" : ab(p), girl: fn(p, g.girl), boy: fn(p, g.boy), focus: p === "Lagna" ? null : both(p),
  }));
  return (
    <>
    <Section name="Strengths"><GrahaSum c={c} births={births} onFocus={onFocus} /></Section>
    <Section name="Aspects"><CrossAspects c={c} part={0} /></Section>
    <Section name="Avasthas"><DuoTable label="Avasthas" onFocus={onFocus}
      cols={[["Age", "Baaladi (BPHS 45.3-4): young and adolescent good, infant middling, old and dead bad"], ["Alertness", "Jaagradadi (BPHS 45.5): awake good, dreaming middling, asleep bad"],
        ["Mood", "Deeptadi (BPHS 45.8-10): glowing, comfortable, delighted or peaceful good; sad, crippled, distressed, mischievous or angry bad"],
        ["Activity", "Sayanadi (BPHS 45.19-37): what the graha is doing, its meaning on hover"], ["Lajjitadi", "BPHS 45.11-18: proud or delighted good; ashamed, starved, thirsty or agitated bad"]]}
      rows={g.bodies.map((p) => ({ key: p, head: ab(p), girl: avasthaCells(p, g.girl), boy: avasthaCells(p, g.boy), focus: both(p) }))} /></Section>
    <Section name="Placement"><DuoTable label="Placement" onFocus={onFocus}
      cols={[["Bhava", "The bhava it is in: green a kendra or trikona, red a dusthana"], ["Sign", "Its sign and dignity: green exalted, moolatrikona or own, red debilitated"],
        ["Lord of", "The bhavas it rules from its lagna: green a functional benefic or yogakaraka, red a functional malefic or the 8th lord"],
        ["Star", "Nakshatra, its pada and its lord: green its own or a friend's, red an enemy's"], ["D-9 bhava", "Its bhava in the navamsa"], ["D-9 sign", "Its navamsa sign and dignity; vargottama good"]]}
      rows={pointRows((p, s) => { const f = facts(p, s); return ["Bhava", "Sign", "Lord of", "Star", "D-9 bhava", "D-9 sign"].map((l) => factCell(f, l)); })} /></Section>
    </>
  );
}

/** The twelve bhavas beyond the overview's Bala, cusp and lord: who is in each and who looks at it, its Sarvashtakavarga bindus
 *  and where its karaka sits. */
export function HouseGrid({ c, births, onFocus }: { c: MatchCompare; births: Births; onFocus: (f: Focus) => void }) {
  const g = c.grid;
  const MALEFIC = ["Sun", "Mars", "Saturn", "Rahu", "Ketu"];
  const company = (ps: string[]): Tone => (!ps.length ? undefined : ps.every((p) => MALEFIC.includes(p)) ? "bad" : ps.some((p) => MALEFIC.includes(p)) ? "mid" : "good");
  const cells = (h: MatchSide["houses"][number], s: MatchSide, i: number): Cell[] => {
    const sign = (s.lagna + h.house - 1) % 12;
    const by = Object.keys(DRISHTI).filter((q) => s.planets[q] && DRISHTI[q].includes(house(s.planets[q].sign, sign)));
    return [
      [h.holds.length ? h.holds.map(ab).join(" ") : null, company(h.holds)],
      [by.length ? by.map(ab).join(" ") : null, company(by), by.map((q) => `${q} (its ${ordinal(house(s.planets[q].sign, sign))} house aspect)`).join(", ") || undefined],
      [h.sav ?? null, h.sav == null ? undefined : h.sav >= 32 ? "good" : h.sav < 29 ? "bad" : "mid", h.sav != null ? `${h.sav} bindus in ${SIGN_NAMES[sign]}, the lagna's own row included` : undefined],
      ...(g.karakas?.[i] ?? []).slice(0, 1).map((k): Cell => {
        const q = s.planets[ABBR_NAME[k] ?? k];
        return q ? [<>{k} <small>{supOrd(ordinal(q.house))}</small></>, placeTone(q.house), `${ABBR_NAME[k] ?? k}, the karaka of the ${ordinal(h.house)}, in the ${ordinal(q.house)}`] : [k];
      }),
    ];
  };
  return (
    <>
    <Section name="Bhava Bala"><BhavaSum c={c} births={births} onFocus={onFocus} /></Section>
    <Section name="Aspects"><CrossAspects c={c} part={1} /></Section>
    <Section name="Occupants & karakas"><DuoTable label="Occupants & karakas" onFocus={onFocus}
      cols={[["Holds", "The grahas in it: benefics only good, malefics only bad, both middling"], ["Aspected by", "The grahas whose full graha drishti falls on its sign: benefics good, malefics bad, both middling"],
        ["SAV", "Its sign's Sarvashtakavarga bindus with the lagna's row: good from 32 (about the average), weak under 29"], ["Karaka", "Its karaka (BPHS 32) and the bhava it sits in: green a kendra or trikona, red a dusthana"]]}
      rows={g.girl.houses.map((a, i) => ({ key: String(a.house), head: <span className="mc-duo-bhava">{supOrd(ordinal(a.house))}<small>{g.about[i]}</small></span>,
        girl: cells(a, g.girl, i), boy: cells(g.boy.houses[i], g.boy, i), focus: { girl: ab(a.lord), boy: ab(g.boy.houses[i].lord) } }))} /></Section>
    </>
  );
}

const pct = (rupas: number, need: number) => Math.round((rupas / need) * 100);

const short = (s?: string) => s?.split(" (")[0] ?? "";
const band = (v: number) => (v >= 15 ? "strong" : v >= 10 ? "middling" : "weak");

/** One of the four charts, drawn as Home's: in its centre the name, Rasi or Bhava (linked across the row), the bhava reference, and on the D-1 charts the partner's buttons. */
export function MatchChart({ label, side, d, kind, onKind, onPick, second, actions, picked }: {
  label: string; side: Side | null; d: 1 | 9; kind: Kind; onKind: (k: Kind) => void; onPick: (s: Side) => void; second?: boolean; actions?: ReactNode; picked?: string;
}) {
  const display = useChart((s) => s.display);
  const chartStyle = useChart((s) => s.chartStyle);
  const [ref, setRef] = useBhavaRef();
  // North and East charts have no empty centre box: the controls come up over it on hover
  const style = second && display.twoStyles ? display.style2 : chartStyle;
  const pop = !!side && (style === "north" || style === "east");
  return (
    <div className={`star-chart bare match-chart ${label.toLowerCase()}${pop ? " pop" : ""}${side ? "" : " unpicked"}`}>
      <div className="match-centre">
        <PartnerName label={label} side={side} onPick={onPick} />
        <div className="row match-kind">
          <b>D{d}</b>
          <div className="seg" role="tablist" aria-label="Rasi or bhava">
            {(["varga", "bhava"] as const).map((k) => <button key={k} type="button" role="tab" aria-selected={kind === k} onClick={() => onKind(k)}>{k === "varga" ? "Rasi" : "Bhava"}</button>)}
          </div>
        </div>
        <div className="match-refs" role="group" aria-label="Reference of the bhava chart">
          {REFS.map(([r, a, n]) => <button key={r} type="button" title={kind === "bhava" ? `Bhavas from ${n}` : "Choose Bhava to count the bhavas from a graha"} disabled={kind !== "bhava"} aria-pressed={ref === r} onClick={() => setRef(r)}>{a}</button>)}
        </div>
        {actions}
      </div>
      {side ? <ChartPanelView i={second ? 1 : 0} chart={side.birth} single hideNatal starlight bare degrees={display.degrees} picked={picked}
        markBody={kind === "bhava" ? REFS.find(([r]) => r === ref)?.[1] : undefined} state={{ spec: { kind, d }, view: "standard" }} />
        : <div className="chart-panel"><ChartGrid second={second} title={`${label} · pick a chart`} cell={() => []} /></div>}
    </div>
  );
}

export const sameSide = (a: Side, b: Side) => a.name === b.name && JSON.stringify(a.birth) === JSON.stringify(b.birth);

/** The shortlist's order: by the Ashtakuta score, the Dashakuta's breaking a tie, or the other way round. */
type RankBy = "ashta" | "dasha";
type Ranked = { s: Side; c: MatchCompare };
/** a kuta's points: three quarters of its most or more good, none bad (as the Overview's rows) */
const kutaTone = (got: number, max: number): Tone => (got >= 0.75 * max ? "good" : got > 0 ? "mid" : "bad");
const GRADE: Record<string, Tone> = { Uttama: "good", Madhyama: "mid", Adhama: "bad" };
const AREA_COLS = [["doshas", "Doshas"], ["mind", "Mind"], ["marriage", "Marriage"], ["family", "Family"], ["health", "Health"], ["timing", "Timing"]] as const;
/** the Domain box's tabs: every domain's verdict, the eight kutas, the ten poruthams, or one area's factors */
type AreaId = (typeof AREA_COLS)[number][0];
type DomainTab = "all" | "ashta" | "dasha" | AreaId;
const DOMAIN_TABS: { id: DomainTab; name: string }[] = [{ id: "all", name: "All" }, { id: "ashta", name: "Ashtakuta" }, { id: "dasha", name: "Dashakuta" },
  ...AREA_COLS.map(([id, name]) => ({ id, name }))];
/** a score's band (toneA, toneD) as a verdict's dot: Excellent and Good green, Average amber, Low red */
const BAND_TONE: Record<string, Tone> = { ex: "good", gd: "good", av: "mid", lo: "bad" };
const upFirst = (s: string) => s && s[0].toUpperCase() + s.slice(1);
const kujaOwn = (k?: MatchKuja) => (!k ? "" : !k.has_kuja_dosha ? "free of it" : k.is_cancelled ? "has it, cancelled" : "has it");

/** The gravest faults of the kutas left standing: Nadi and Bhakoota at none and not cancelled, Rajju and Vedha; each with why. */
function graveDoshas(c: MatchCompare): [string, string][] {
  const b = c.match.ashta_kuta_breakdown, k = c.match.dashakoota;
  const why = (n: string) => k.kutas.find((x) => x.kuta === n)?.status ?? "";
  return [
    ...(["nadi", "bhakoota"] as const).filter((x) => b[x] && b[x].obtained_points === 0 && !b[x].is_cancelled).map((x): [string, string] => [KUTA_LABEL[x], String(b[x].status ?? "")]),
    ...(k.rajju_dosha ? [["Rajju", why("Rajju")] as [string, string]] : []),
    ...(k.vedha_dosha ? [["Vedha", why("Vedha")] as [string, string]] : []),
  ];
}

/** A score in its band's colour (the Overview's cards, small): the points of the most, the level under it. */
const Score = ({ got, max, level, band }: { got: number; max: number; level: string; band: string }) => (
  <span className={`ms-score ${band}`}><b>{num(got)}<small>/{max}</small></b><small>{level}</small></span>
);

/** One chart against every starred partner, best first by the chosen score: the ranking (Ashtakuta, Dashakuta, Kuja and the
 *  gravest kuta doshas), then one Domain box filling the rest, its tabs every domain's verdict, the eight kutas, the ten
 *  poruthams and each area's factors, a row per partner in the same order so a column reads straight down. The pair shown
 *  in the charts is marked; a name shows that pair. */
export function Shortlist({ who, fixed, list, shown, onShow, onDrop }: {
  who: "girl" | "boy"; fixed: Side; list: Side[]; shown: Side | null; onShow: (s: Side) => void; onDrop: (s: Side) => void;
}) {
  const display = useChart((s) => s.display);
  const [by, setBy] = useSaved<RankBy>("matchShortlistBy", "ashta");
  const [area, setArea] = useSaved<DomainTab>("matchShortlistArea", "all");
  const qs = useQueries({ queries: list.map((s) => {
    const [girl, boy] = who === "girl" ? [fixed, s] : [s, fixed];
    return { queryKey: ["matchCompare", boy.birth, girl.birth, boy.name, girl.name], queryFn: () => api.matchingCompare(girl.birth, boy.birth, girl.name, boy.name) };
  }) });
  const done = list.map((s, i) => ({ s, c: qs[i].data })).filter((x): x is Ranked => !!x.c);
  const ashta = (x: Ranked) => x.c.match.gunanka_score, dasha = (x: Ranked) => x.c.match.dashakoota.score;
  const [first, then] = by === "ashta" ? [ashta, dasha] : [dasha, ashta];
  const rows = [...done].sort((a, b) => first(b) - first(a) || then(b) - then(a));
  const pending = qs.filter((q) => q.isLoading).length, failed = qs.filter((q) => q.isError).length;
  const them = who === "girl" ? "boy" : "girl";
  const sign = (s: string) => { const i = SIGN_NAMES.indexOf(s); return i >= 0 ? signName(i, SIGN_NAMES[i], display) : s; };
  const moon = (c: MatchCompare, w: "girl" | "boy") => {
    const m = w === "girl" ? c.bride_moon : c.groom_moon;
    return `${m.name} ${m.pada} · ${sign((w === "girl" ? c.match.bride : c.match.groom).moon_rasi)}`;
  };
  const here = (s: Side) => !!shown && sameSide(s, shown);
  const name = (s: Side) => <button type="button" className="ms-name" translate="no" title="Show this pair in the charts" onClick={() => onShow(s)}>{s.name}</button>;
  /** a table of a row per partner: the name, then a cell per column */
  const table = (label: string, cols: [ReactNode, string?][], cells: (x: Ranked) => Cell[], cls = "") => (
    <div className="ms-wrap">
      <table className={`ms-table${cls ? ` ${cls}` : ""}`} aria-label={label}>
        <thead><tr><th scope="col" />{cols.map(([h, tip], i) => <th key={i} scope="col" data-tip={tip}>{h}</th>)}</tr></thead>
        <tbody>
          {rows.map((x) => (
            <tr key={x.s.name + JSON.stringify(x.s.birth)} className={here(x.s) ? "here" : undefined}>
              <th scope="row">{name(x.s)}</th>
              {cells(x).map(([v, t, tip], i) => <td key={i}><span className={`mc-box${t ? ` ${t}` : ""}`} data-tip={tip}>{v ?? <small>–</small>}</span></td>)}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
  /** one area's factors, a column each: how the two read on it (the partner's own value where the pair is not judged, Kuja
   *  from Ve Mo As), the area's verdict last; the partner's value, the fixed chart's and why, on hover */
  const areaTable = (id: AreaId) => {
    const name = AREA_COLS.find(([a]) => a === id)?.[1] ?? id;
    const of = (x: Ranked) => x.c.factors.find((f) => f.id === id);
    const keys = rows.map(of).find((a) => a?.rows.length)?.rows ?? [];
    if (!keys.length) return <p className="muted">No {name} factors for these charts.</p>;
    return table(`The ${name} factors`, [...keys.map((r): [ReactNode, string] => [r.factor, `${r.about ? `${upFirst(r.about)}. ` : ""}${r.rule}`]), ["Verdict", `The ${name} factors' verdict`]],
      (x) => {
        const a = of(x);
        return [...keys.map((k): Cell => {
          const r = a?.rows.find((y) => y.key === k.key);
          if (!r) return [null];
          const own = r[them], mine = r[who], t = r.together;
          const tip = [`${x.s.name}: ${own.hint || own.text}`, `${fixed.name}: ${mine.hint || mine.text}`, t.text ? t.hint : ""].filter(Boolean).join("\n");
          if (t.text) return [t.text, t.tone ?? undefined, tip];
          if (own.parts) return [<span className="mc-box mc-parts">{own.parts.map((p, i) => <span key={i} className={`mc-box mc-part${p.tone ? ` ${p.tone}` : ""}`}>{p.text}</span>)}</span>, undefined, tip];
          return [own.text || null, own.tone ?? undefined, tip];
        }), a ? [toneWord(a.tone, id === "doshas") || null, a.tone ?? undefined] : [null]];
      }, "ms-area");
  };
  const c0 = done[0]?.c;
  const ref = c0 && <>Moon in {moon(c0, who)} · Kuja: {kujaOwn(c0.grid[who].kuja)}</>;
  return (
    <section className="match-shortlist">
      <header className="ms-head">
        <div>
          <h3><span translate="no">{fixed.name}</span> with {list.length} {them === "boy" ? (list.length === 1 ? "boy" : "boys") : (list.length === 1 ? "girl" : "girls")}</h3>
          {ref && <small className="muted">{ref}</small>}
        </div>
        <div className="row ms-by">
          <span className="muted">Rank by</span>
          <div className="seg" role="tablist" aria-label="Rank by">
            {([["ashta", "Ashtakuta"], ["dasha", "Dashakuta"]] as const).map(([id, n]) => <button key={id} type="button" role="tab" aria-selected={by === id} onClick={() => setBy(id)}>{n}</button>)}
          </div>
        </div>
      </header>
      {(pending > 0 || failed > 0) && <p className="muted">{pending > 0 && `Matching ${pending}…`} {failed > 0 && `${failed} could not be matched.`}</p>}
      {rows.length > 0 && (
        <>
          <Section name="Ranking">
            <div className="ms-wrap">
              <table className="ms-table ms-rank" aria-label={`${fixed.name} against the shortlist`}>
                <thead>
                  <tr>
                    <th scope="col" /><th scope="col" className="ms-who">{them === "boy" ? "Boy" : "Girl"}</th>
                    <th scope="col" data-tip="The eight kutas of the two Moons, of 36: Excellent from 31, Very Good from 21, Middling from 17">Ashtakuta</th>
                    <th scope="col" data-tip="The ten poruthams, of 10: Uttama 1, Madhyama ½, Adhama 0">Dashakuta</th>
                    <th scope="col" data-tip={`Kuja dosha of the two together: balanced when both have it, fine when neither does, a fault when only one does. Under it, the ${them}'s own.`}>Kuja</th>
                    <th scope="col" data-tip="The gravest faults of the kutas left standing: Nadi or Bhakoota at none and not cancelled, Rajju, Vedha">Doshas</th>
                    <th scope="col" />
                  </tr>
                </thead>
                <tbody>
                  {rows.map((x, n) => {
                    const m = x.c.match, k = m.dashakoota, grave = graveDoshas(x.c);
                    const kuja = x.c.factors.find((a) => a.id === "doshas")?.rows.find((r) => r.key === "kuja")?.together;
                    return (
                      <tr key={x.s.name + JSON.stringify(x.s.birth)} className={here(x.s) ? "here" : undefined}>
                        <td className="ms-n">{n + 1}</td>
                        <th scope="row" className="ms-who">
                          <span className="ms-line">{name(x.s)}<WhoAge who="" birth={x.s.birth} /></span>
                          <small className="muted">{moon(x.c, them)}</small>
                        </th>
                        <td><Score got={m.gunanka_score} max={36} level={m.match_level} band={toneA(m.gunanka_score)} /></td>
                        <td><Score got={k.score} max={10} level={k.level} band={toneD(k.score)} /></td>
                        <td>
                          <span className={`mc-box ms-kuja${kuja?.tone ? ` ${kuja.tone}` : ""}`} data-tip={kuja?.hint || undefined}>{kuja?.text || "–"}</span>
                          <small className="muted">{kujaOwn(x.c.grid[them].kuja)}</small>
                        </td>
                        <td><span className={`mc-box ${grave.length ? "bad" : "good"}`} data-tip={grave.map(([d, w]) => `${d}: ${w}`).join("; ") || "None of Nadi, Bhakoota, Rajju or Vedha"}>{grave.length ? grave.map(([d]) => d).join(" · ") : "none"}</span></td>
                        <td><button type="button" className="ms-drop" aria-label={`Take ${x.s.name} off the shortlist`} title="Take off the shortlist" onClick={() => onDrop(x.s)}>×</button></td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </Section>
          <Section name="Domain" cls="ms-domain" tabs={<SubTabs label="Domain" tabs={DOMAIN_TABS} value={area} onChange={setArea} />}>
            {area === "all" ? table("Every domain's verdict", [
              ["Ashtakuta", "The eight kutas' level: its tab shows them"], ["Dashakuta", "The ten poruthams' level: its tab shows them"],
              ...AREA_COLS.map(([, n]): [ReactNode, string] => [n, `The verdict of the ${n} factors: its tab shows them`])],
              (x) => {
                const m = x.c.match, k = m.dashakoota;
                return [[m.match_level, BAND_TONE[toneA(m.gunanka_score)], `${num(m.gunanka_score)} of 36`], [k.level, BAND_TONE[toneD(k.score)], `${num(k.score)} of 10`],
                  ...AREA_COLS.map(([id]): Cell => {
                    const a = x.c.factors.find((f) => f.id === id);
                    return a ? [toneWord(a.tone, id === "doshas") || null, a.tone ?? undefined, a.rows.filter((r) => r.together.text).map((r) => `${r.factor}: ${r.together.text}`).join("\n") || undefined] : [null];
                  })];
              })
            : area === "ashta" ? table("The eight kutas", [...KUTA_ORDER.map((k): [ReactNode, string] => {
              const max = rows[0].c.match.ashta_kuta_breakdown[k]?.max_points;
              return [<>{KUTA_LABEL[k]}<small>of {max}</small></>, `${KUTA_LABEL[k]}, of ${max}: green three quarters or more, red none`];
            }), [<>Total<small>of 36</small></>]],
            (x) => [...KUTA_ORDER.map((k): Cell => { const f = x.c.match.ashta_kuta_breakdown[k]; return f ? [num(f.obtained_points), kutaTone(f.obtained_points, f.max_points), String(f.status ?? "")] : [null]; }),
              [<b>{num(x.c.match.gunanka_score)}</b>]])
            : area === "dasha" ? table("The ten poruthams", [...rows[0].c.match.dashakoota.kutas.map((p): [ReactNode, string] => [p.kuta, `${p.kuta}: Uttama 1 (green), Madhyama ½, Adhama 0 (red)`]), [<>Total<small>of 10</small></>]],
              (x) => [...x.c.match.dashakoota.kutas.map((p): Cell => [num(p.points), GRADE[p.grade], `${p.grade}: ${p.status}`]), [<b>{num(x.c.match.dashakoota.score)}</b>]])
            : areaTable(area)}
          </Section>
        </>
      )}
      <p className="muted mc-note">Ranked by the {by === "ashta" ? "Ashtakuta, the Dashakuta breaking a tie" : "Dashakuta, the Ashtakuta breaking a tie"}. A name shows that pair in the charts; why each value is what it is, on its hover.</p>
    </section>
  );
}
