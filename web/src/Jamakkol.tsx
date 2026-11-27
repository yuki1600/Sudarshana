import { useQuery } from "@tanstack/react-query";
import { degText } from "./chartGeometry";
import { api, type Birth, type Jamakkol as JamakkolData, type JamakkolPoint, type Moment } from "./api";
import { useKept } from "./hooks";
import { CastButton, useMoment } from "./Modes";
import { shown, signName } from "./names";
import { formatLon, SIGN_NAMES, SIGNS } from "./format";
import { SouthGrid } from "./SouthGrid";
import { Inspector } from "./Starlight";
import { Icon } from "./Icons";
import { Stepper } from "./TopBar";
import { useChart } from "./store";
import { Loaded } from "./ui";

// Where each Jama box sits outside the South Indian square (row, column of a 6 x 6 grid whose middle 4 x 4 is the chart):
// a corner sign's box off its corner, the box after it off that sign's outer side
const RING: Record<number, [number, number]> = { 11: [1, 1], 0: [1, 3], 2: [1, 6], 3: [3, 6], 5: [6, 6], 6: [6, 4], 8: [6, 1], 9: [4, 1] };

const dm = (lon: number) => { const x = ((lon % 30) + 30) % 30, d = Math.floor(x), m = Math.floor((x - d) * 60); return `${d}°${String(m).padStart(2, "0")}′`; };
const at = (lon: number) => `${dm(lon)} ${SIGN_NAMES[Math.floor((((lon % 360) + 360) % 360) / 30)]}`;

/** The chart cast (kept over a refresh): the moment set on the form, at the open chart's place. The form and Starlight's left half share it. */
function useCast() {
  const natal = useChart((s) => s.natal)!;
  const [cast, setCast] = useKept<Moment | null>("transit.jamakkol.cast", null);
  const [kind, setKind] = useKept<Kind>("transit.jamakkol.kind", "rasi");
  const { adjust: _, ...place } = natal;
  const at = (m: Moment): Birth => ({ ...place, ...m });     // a moment at the open chart's place
  const birth: Birth | null = cast && at(cast);
  const q = useQuery({ queryKey: ["jamakkol", birth, kind], queryFn: () => api.jamakkol(birth!, kind), enabled: !!birth, placeholderData: (p) => p });
  return { natal, birth, at, q, setCast, kind, setKind };
}

type Kind = "rasi" | "bhava";

/** The chart: the South Indian square with the eight Jama grahas round it, Rasi or Bhava in its centre (the bhavas from the lagna, not from Udayam). */
function JamakkolChart({ j, kind, setKind }: { j: JamakkolData; kind: Kind; setKind: (k: Kind) => void }) {
  const display = useChart((s) => s.display);
  // as a bhava chart elsewhere (ChartPane): a body's degrees from the start of its box's sign, so a box lists them in zodiac order,
  // and one whose house box is not its own sign says the sign after its degrees ("Ma 2°12' Ar")
  const fromBox = kind === "bhava" ? Object.fromEntries(Object.entries(j.boxes).flatMap(([b, labels]) => labels.map((l) => {
    const t = l.replace(/R$/, "");
    return [t, ((j.longitudes[t] - 30 * Number(b) + 540) % 360) - 180];
  }))) : undefined;
  const moved = fromBox && Object.fromEntries(Object.entries(fromBox).filter(([, d]) => d < 0 || d >= 30).map(([t]) => { const s = Math.floor(j.longitudes[t] / 30) % 12; return [t, signName(s, SIGNS[s], display)]; }));
  // Rasi | Bhava atop the chart's centre, the title under it, as the Divisional charts' toggle
  const toggle = (
    <div className="mv-kind" role="group" aria-label="Rasi or bhava chart">
      {(["rasi", "bhava"] as const).map((k) => <button key={k} type="button" aria-pressed={kind === k} onClick={() => setKind(k)}
        data-tip={k === "bhava" ? "The houses from the lagna, by your house type" : "The signs"}>{k === "rasi" ? "Rasi" : "Bhava"}</button>)}
    </div>
  );
  return (
    <div className="jamakkol">
      {j.jama.map((g) => (
        <div key={g.box} className="jama-box" style={{ gridRow: RING[g.box][0], gridColumn: RING[g.box][1] }} data-tip={`Jama ${g.name}: ${at(g.lon)}`}>
          {/* as a chart writes a graha: "Su 22°31'", and its sign after the degrees when that isn't its box's (a bhava chart's moved graha) */}
          <span><strong>{shown(g.abbr, display)}</strong> {degText(g.lon)}{Math.floor(g.lon / 30) !== g.box ? ` ${SIGNS[Math.floor(g.lon / 30)]}` : ""}</span>
        </div>
      ))}
      <div className="jamakkol-chart">
        <SouthGrid title="Jamakkol" cell={(s) => j.boxes[s] ?? []} lagnaSign={j.lagna} degrees={fromBox ? { ...j.degrees, ...fromBox } : j.degrees} moved={moved}
          retro={j.grahas.filter((g) => g.retrograde).map((g) => g.abbr)} top={toggle} />
      </div>
    </div>
  );
}

/** Starlight's left half on the Jamakkol sub tab, once a chart is cast (Transits.tsx TransitsLeft). */
export function JamakkolLeft() {
  const { q, kind, setKind } = useCast();
  return <div className="star-chart jamakkol-left"><Loaded q={q}>{(j) => <JamakkolChart j={j} kind={kind} setKind={setKind} />}</Loaded></div>;
}
/** Whether a Jamakkol chart is cast, for TransitsLeft. */
export const useJamakkolCast = () => useKept<Moment | null>("transit.jamakkol.cast", null)[0] !== null;

const ORDER = ["Su", "Mo", "Ma", "Me", "Ju", "Ve", "Sa", "Ra", "Ke"];
type Row = JamakkolPoint & { retrograde?: boolean; jama?: boolean };

/** One row as Key Info writes a body: its name, (R) when retrograde (Rahu and Ketu too, by their own motion), the longitude "6°20′25″ Ar",
 *  the nakshatra and its pada. */
function BodyRow({ r }: { r: Row }) {
  const [deg, sign, min, sec] = formatLon(r.lon).trim().split(/\s+/);
  return (
    <tr className={r.jama ? "jama-row" : undefined} data-tip={r.jama ? "Jama graha" : undefined}>
      <td><span className="graha-name">{r.name}</span>{r.retrograde && <span className="retro-r" title="Retrograde"> (R)</span>}</td>
      <td className="num kp-deg">{deg}°{min.replace("'", "′")}<small>{sec.replace('"', "″")}</small> <span className="kp-sign">{sign}</span></td>
      <td>{r.nakshatra}<span className="pips" role="img" aria-label={`pada ${r.pada}`} title={`Pada ${r.pada}`}>{[1, 2, 3, 4].map((p) => <i key={p} className={p <= r.pada ? "on" : undefined} />)}</span></td>
    </tr>
  );
}

/** Every body of the chart in one table: the grahas, the points, then the Jama grahas in purple. */
function Tables({ j }: { j: JamakkolData }) {
  const order = (g: JamakkolPoint) => ORDER.indexOf(g.abbr);     // the Jama grahas Sun, Moon .. Saturn, Rahu, not by their boxes
  const rows: Row[] = [...j.grahas, ...j.points, ...[...j.jama].sort((a, b) => order(a) - order(b)).map((g) => ({ ...g, jama: true }))];
  return (
    <div className="scroll tall">
      <table className="points jamakkol-table">
        <thead><tr><th>Body</th><th>Longitude</th><th>Nakshatra</th></tr></thead>
        <tbody>{rows.map((r) => <BodyRow key={(r.jama ? "j" : "") + r.abbr} r={r} />)}</tbody>
      </table>
    </div>
  );
}

/** Starlight's box beside the form: the cast moment's birth details as the natal chart's (Inspector), then Jamakkol's own Jamam and Veethi. */
function CastDetails({ birth, q }: { birth: Birth; q: ReturnType<typeof useCast>["q"] }) {
  const name = useChart((s) => s.name);
  const b = useQuery({ queryKey: ["basics", birth, name], queryFn: () => api.basics(birth, name), placeholderData: (p) => p });
  const own = (q.data?.facts ?? []).filter(([k]) => k === "Jamam" || k === "Veethi");
  return <Loaded q={b}>{(d) => <Inspector b={d} tail={own} />}</Loaded>;
}

/** Transits > Jamakkol: a Jamakkol Prasanam chart for the moment of the question, at the open chart's place. Starlight draws the chart
 *  in its left half (JamakkolLeft), the Windows layout here beside the tables. */
export function Jamakkol() {
  const { natal, birth, at, q, setCast, kind, setKind } = useCast();
  const star = useChart((s) => s.display.layout === "starlight");
  const { fields, moment, now, put } = useMoment(undefined, true, "transit.jamakkol");
  // the stepper: the cast moment on by a step, the fields following it
  const move = (b: Birth) => { const m = { year: b.year, month: b.month, day: b.day, hour_local: b.hour_local, tz_east_hours: b.tz_east_hours }; setCast(m); put(m); };
  return (
    <>
      <div className="finder">
        <section className="pane finder-form">
          <form className="mode-form" onSubmit={(e) => { e.preventDefault(); setCast(moment()); }}>
            {fields}
            <div className="mode-buttons">
              {/* Starlight: Cast, its + opening the chart on its own as "Jamakkol-2026-Name", as the Transits form's */}
              {star ? <CastButton busy={false} kind="Jamakkol" cast={(keep) => { const m = moment(); setCast(m); keep({ title: "Jamakkol", birth: at(m), start: "" }); }} />
                : <button type="submit" className="primary">Cast Jamakkol</button>}
              <button type="button" className="now-btn" onClick={now} aria-label="Now" data-tip="Set the date and time to now"><Icon name="now" /></button>
              {/* cast: step its moment */}
              {birth && <Stepper cast={{ name: "Jamakkol", birth, move }} />}
            </div>
          </form>
          <p className="muted pad">At {natal.place || "the open chart's place"}. Udayam follows your sunrise setting, and its degree your ayanamsa.</p>
        </section>
        <section className="pane finder-result">
          {/* Starlight: headed as the Transit page's Natal Chart and Transit Chart columns, the moment cast for, then the facts one below the other */}
          {star && <header className="pane-head"><h2>Jamakkol Chart</h2></header>}
          {!birth ? <p className="muted pad">Cast a chart for the moment of the question.</p> : star ? <CastDetails birth={birth} q={q} /> : <Loaded q={q}>{(j) => (
            <table className="points wrap"><tbody>{j.facts.map(([k, v]) => <tr key={k}><td>{k}</td><td>{v}</td></tr>)}</tbody></table>
          )}</Loaded>}
        </section>
      </div>
      {birth && (star ? <section className="pane"><Loaded q={q}>{(j) => <Tables j={j} />}</Loaded></section>
        : <Loaded q={q}>{(j) => (
          <div className="finder">
            <section className="pane"><JamakkolChart j={j} kind={kind} setKind={setKind} /></section>
            <section className="pane"><Tables j={j} /></section>
          </div>
        )}</Loaded>)}
    </>
  );
}
