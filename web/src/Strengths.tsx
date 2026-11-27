import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api, currentSettings, saveSettings, type Birth, type Strengths as S, type Table, type TransitVisit, type YogaBasis, type YogaListRow, type YogaRow } from "./api";
import { Modal } from "./ChartDialogs";
import { TableView } from "./Panels";
import { pageScale, useKept, useSaved, useShape, useTopVarga, useView } from "./hooks";
import { Icon } from "./Icons";
import { useMenu } from "./Menu";
import { SouthGrid } from "./SouthGrid";
import { useChart } from "./store";
import { CopyButton, Dignity, Loaded, Retro, SubTabs, supOrd, tableText } from "./ui";
import { Meter } from "./Lab";
import { AV_SCORE, VAI, avName, avScore, avWord, spread, toneStyle, vaiCount, vaiTone } from "./tone";
import { DIVISIONS, DivisionSelect } from "./Windows";
import { SIGNS, formatLon } from "./format";
import { ord } from "./Calculations";
import { nameAnka } from "./nameAnka";

export const ROWS = ["As", "Su", "Mo", "Ma", "Me", "Ju", "Ve", "Sa"];
const f2 = (x: number) => x.toFixed(2);
/** A graha's shadbala against its minimum: 80% of it reads weak, 150% strong. */
const grahaTone = (p: { rupas: number; required: number }) => (p.rupas / p.required - 0.8) / 0.7;
/** Bindus: a SAV of 22 reads weak and 34 strong (28 is the average); a BAV of 1 weak and 7 strong (4 is the middle). */
export const savTone = (v: number) => (v - 22) / 12;
export const bavTone = (v: number) => (v - 1) / 6;
// each graha's moolatrikona sign (0 = Aries)
const MOOLATRIKONA: Record<string, number> = { Sun: 4, Moon: 1, Mars: 0, Mercury: 5, Jupiter: 8, Venus: 6, Saturn: 10 };
// the nodes own no house by lordship: Rahu's own sign is Aquarius, Ketu's Scorpio
const NODE_SIGN: Record<string, number> = { Rahu: 10, Ketu: 7 };
const ORDINAL = ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th", "10th", "11th", "12th"];

const PAV_NAMES = ["Lagna", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"];
const ZODIAC = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"];

const AV_TABS = [{ id: "av", name: "Ashtakavarga" }, { id: "points", name: "Nakshatras & rasis" }];
const POINTS_HELP = "By multiplying the sodhya pinda of a graha and the score in its ashtakavarga in a rasi, we get a number. By dividing it with 27 and 12, we get a nakshatra or rasi. Transit of Jupiter/Saturn in it is good/bad for the matters signified by the relevant bhava from the graha. For example, use Sun's sodhya pinda and the 9th from Sun for father. Highlighted: 9th from Sun (father), 4th from Moon (mother), 3rd from Mars (siblings), 5th from Jupiter (children), 7th from Venus (spouse) and 10th from Saturn (work).";
// the four-letter stars of the Sarvatobhadra chakra (wheelGeometry.ts SBC), Aswini first
const STAR4 = ["Aswi", "Bhar", "Krit", "Rohi", "Mrig", "Ardr", "Puna", "Push", "Asre", "Magh", "PPha", "UPha", "Hast", "Chit", "Swat", "Visa", "Anu", "Jye", "Mool", "PSha", "USha", "Srav", "Dhan", "Sata", "PBha", "UBha", "Reva"];
// the house from a planet that speaks of a relative: 9th from the Sun for father .. (index into ROWS)
const KIN: Record<number, [number, string]> = { 1: [9, "Father"], 2: [4, "Mother"], 3: [3, "Siblings"], 5: [5, "Children"], 6: [7, "Spouse"], 7: [10, "Work"] };
const vargaName = (d: number) => (d === 1 ? "Rasi (D-1)" : `D-${d}`);

/** The Ashtakavarga view: of any varga, of the natal or the derived chart, in each of its presentations;
 *  the nakshatras and rasis from the sodhya pindas are a sub-tab of their own. */
function Ashtakavarga() {
  const { birth, natal, mode, avVarga, setAvVarga } = useChart();
  const [sub, setSub] = useKept("avSub", "av");
  const [kept, setShow] = useKept("avShow", "bav");
  const points = sub === "points";
  const show = points ? "points" : kept === "points" ? "bav" : kept;     // "points" kept from before it had its own sub-tab
  const [useNatal, setUseNatal] = useKept("avUseNatal", false);
  const { open, node } = useMenu();
  const [kinAt, setKinAt] = useKept<{ planet: number; star: number; sign: number; nakshatra: string } | null>("av.kinAt", null);     // the highlighted cell clicked
  const chart = useNatal ? natal! : birth!;
  // another sign taken as lagna: for the chart it was picked on only, so another chart opens on its own lagna
  const [lagnaAt, setLagnaAt] = useKept<{ of: string; sign: number } | null>("av.lagna", null);
  const lagna = lagnaAt && lagnaAt.of === JSON.stringify(chart) ? lagnaAt.sign : null;
  const q = useQuery({ queryKey: ["ashtakavarga", chart, avVarga, lagna], queryFn: () => api.ashtakavarga(chart, avVarga, lagna), placeholderData: (p) => p });
  const av = q.data;
  const shades = (i: number | "sav") => {
    const signs = av!.signs;
    return new Set(i === "sav" ? signs.slice(1) : [signs[i]]);
  };
  return (
    // the nakshatras and rasis: the varga is picked by right-click, not a dropdown
    <section className="pane" onContextMenu={points ? (e) => { e.preventDefault(); open(e, DIVISIONS.map((d) => ({ label: vargaName(d), checked: d === avVarga, onClick: () => setAvVarga(d) })), "Varga"); } : undefined}>
      <header className="pane-head">
        <span className="row wrap">
          <SubTabs label="Ashtakavarga views" tabs={AV_TABS} value={sub} onChange={setSub} />
          {points && <span className="muted">{vargaName(avVarga)} · right-click to change the varga</span>}
          {points && <span className="info-tip"><button className="icon-btn" aria-label="About this table" aria-describedby="points-help"><Icon name="info" /></button><span role="tooltip" id="points-help">{POINTS_HELP}</span></span>}
        </span>
        {points && mode && <label className="check"><input type="checkbox" checked={useNatal} onChange={(e) => setUseNatal(e.target.checked)} /> Natal chart</label>}
      </header>
      {!points && <header className="pane-head">
        <span className="row wrap">
          <select aria-label="What to show" value={show} onChange={(e) => setShow(e.target.value)}>
            <option value="bav">BAVs and SAV</option><option value="reduced">Reduced (SoAV)</option>
            {PAV_NAMES.map((n, i) => <option key={n} value={`pav${i}`}>PAV of {n}</option>)}
            <option value="pindas">Sodhya pindas</option>
          </select>
          <DivisionSelect value={avVarga} onChange={setAvVarga} label="Show AV of this divisional chart" />
          <select aria-label="Lagna" value={lagna ?? ""} data-tip="Recompute taking another sign as lagna"
            onChange={(e) => setLagnaAt(e.target.value === "" ? null : { of: JSON.stringify(chart), sign: Number(e.target.value) })}>
            <option value="">Actual lagna</option>
            {ZODIAC.map((z, i) => <option key={z} value={i}>{z} as lagna</option>)}
          </select>
          {mode && <label className="check"><input type="checkbox" checked={useNatal} onChange={(e) => setUseNatal(e.target.checked)} /> Natal chart</label>}
        </span>
      </header>}
      <Loaded q={q}>{(a) => {
        if (show === "pindas") return (
          <div className="scroll"><table className="points">
            <thead><tr><th>Graha</th><th>Sodhya Pinda</th><th>Rasi Pinda</th><th>Graha Pinda</th></tr></thead>
            <tbody>{a.pindas.map((p, i) => <tr key={i}><td>{ROWS[i]}</td><td className="num">{p[0]}</td><td className="num">{p[1]}</td><td className="num">{p[2]}</td></tr>)}</tbody>
          </table></div>
        );
        if (show === "points") return (
          <div className="scroll tall">
            <table className="points pinda-points">
              <thead><tr><th></th>{ZODIAC.map((z, i) => <th key={z} title={z}>{SIGNS[i]}</th>)}</tr></thead>
              <tbody>{a.pinda_points.map((row, i) => {
                const kin = KIN[i], at = kin && (a.signs[i] + kin[0] - 1) % 12;     // the house from the planet, in this varga
                return <tr key={i}><th scope="row">{ROWS[i]}</th>{row.map((c, s) => {
                  const hit = kin && s === at;
                  const text = <>{STAR4[c.star]} <span className="muted">{c.rasi}</span>{hit && <span className="kin-tag">{kin[1]}</span>}</>;
                  return <td key={s} className={hit ? "kin" : undefined} title={`${c.nakshatra}, ${c.rasi}${hit ? ` (${ord(kin[0])} from ${ROWS[i]}: ${kin[1]}). Click for Jupiter's and Saturn's transits` : ""}`}>
                    {hit ? <button className="kin-btn" onClick={() => setKinAt({ planet: i, star: c.star, sign: c.sign, nakshatra: c.nakshatra })}>{text}</button> : text}
                  </td>;
                })}</tr>;
              })}</tbody>
            </table>
          </div>
        );
        if (show.startsWith("pav")) {
          const o = Number(show.slice(3));
          return (
            <div className="scroll"><p className="muted pad">Prastara (spread-out) ashtakavarga of {PAV_NAMES[o]}. A 1 is a bindu from that reference in that sign.</p>
              <table className="points">
                <thead><tr><th>Reference</th>{ZODIAC.map((z, i) => <th key={z} title={z}>{SIGNS[i]}</th>)}<th>Total</th></tr></thead>
                <tbody>{a.pav[o].map((row, c) => <tr key={c}><td>{PAV_NAMES[c]}</td>{row.map((v, s) => <td key={s} className="num">{v}</td>)}<td className="num">{row.reduce((x, y) => x + y, 0)}</td></tr>)}
                  <tr><td><strong>BAV</strong></td>{a.bav[o].map((v, s) => <td key={s} className="num"><strong>{v}</strong></td>)}<td className="num"><strong>{a.bav[o].reduce((x, y) => x + y, 0)}</strong></td></tr></tbody>
              </table></div>
          );
        }
        const reduced = show === "reduced";
        const bav = reduced ? a.reduced : a.bav;
        // SAV of the reduced rows: the sum of the seven planets' rows, sign by sign
        const sav = reduced ? Array.from({ length: 12 }, (_, s) => a.reduced.slice(1).reduce((t, r) => t + r[s], 0)) : a.sav;
        // reduced counts have no fixed scale, so each grid is toned against its own lowest and highest
        const withAsc = sav.map((v, s) => v + bav[0][s]);   // the lagna's own bindus added in
        const grids = [{ t: "SAV", note: "W/ Asc", f: (s: number) => withAsc[s], shade: shades("sav"), tone: reduced ? spread(withAsc) : (v: number) => savTone(v - 4) },   // lagna adds 49 bindus, about 4 a sign
          { t: "SAV", note: "W/o Asc", f: (s: number) => sav[s], shade: shades("sav"), tone: reduced ? spread(sav) : savTone },
          ...ROWS.map((t, i) => ({ t, note: undefined, f: (s: number) => bav[i][s], shade: shades(i), tone: reduced ? spread(bav[i]) : bavTone }))];
        return (
          <>
            <div className="av-room"><div className="av-big">{grids.map((g) => <SouthGrid key={g.t + g.note} title={g.t} note={g.note} compact shaded={g.shade} cell={(s) => [String(g.f(s))]} tone={(s) => g.tone(g.f(s))} />)}</div></div>
            <div className="scroll"><table className="points">
              <thead><tr><th>Sodhya pinda</th><th>Sodhya</th><th>Rasi</th><th>Graha</th></tr></thead>
              <tbody>{a.pindas.map((p, i) => <tr key={i}><td>{ROWS[i]}</td><td className="num">{p[0]}</td><td className="num">{p[1]}</td><td className="num">{p[2]}</td></tr>)}</tbody>
            </table></div>
          </>
        );
      }}</Loaded>
      {node}
      {kinAt && <KinTransits {...kinAt} birth={chart} onClose={() => setKinAt(null)} />}
    </section>
  );
}

/** ``only``: the grahas' table or the houses' alone (the print report has them as two sections). */
export function Shadbala({ s, only, cusp }: { s: S["shadbala"]; only?: "graha" | "bhava"; cusp?: S["cusp_bala"] }) {
  const [mode, setMode] = useKept<"summary" | "break">("shadbalaMode", "summary");
  const most = Math.max(...s.planets.map((p) => Math.max(p.rupas, p.required)));
  const parts = ["sthana", "kala", "dig", "cheshta", "naisargika", "drig", "total"] as const;
  const at = Object.fromEntries(parts.map((k) => [k, spread(s.planets.map((p) => p[k]))]));
  // a house of 7 rupas is the line: above it reads good, below weak (5 weak, 9 strong)
  const house = (r: number) => (r - 7) / 4 + 0.5;
  const mostHouse = Math.max(7, ...s.bhavas.map((b) => b.rupas));
  // the houses each graha rules, from the bhavas' lords, side by side beside its name; the moolatrikona one in green
  const rules = (name: string) => {
    const hs = s.bhavas.filter((b) => name in NODE_SIGN ? b.sign === NODE_SIGN[name] : b.lord === name);
    return hs.length ? <span className="rules">{hs.map((b) => {
      const o = ORDINAL[b.house - 1], mt = MOOLATRIKONA[name] === b.sign;
      return <span key={b.house} className={mt ? "good-text" : "muted"} data-tip={`${o} bhava: ${mt ? "moolatrikona" : "own sign"} (${ZODIAC[b.sign]})`}>{o.slice(0, -2)}<sup>{o.slice(-2)}</sup></span>;
    })}</span> : null;
  };
  const { open, node } = useMenu();
  // two boxes, the grahas' then the houses'; the grahas' view is picked by right-click, not a toggle
  return (
    <>
      {only !== "bhava" && <section className="pane shadbala graha" onContextMenu={(e) => { e.preventDefault(); open(e, [{ label: "Summary", checked: mode === "summary", onClick: () => setMode("summary") }, { label: "Break-up", checked: mode === "break", onClick: () => setMode("break") }], "Shadbala view"); }}>
        {node}
        {only && <header className="pane-head"><h2>Shadbala</h2></header>}
        <div className="scroll"><table className="points strength">
          {mode === "summary" ? (
            <><thead><tr><th><strong>Graha</strong><span className="rules-head">Lord</span></th><th className="meter-col">Shadbala</th><th>% Bala</th><th>Rupas</th><th>Total</th><th>Min</th><th>Ishta</th><th>Kashta</th></tr></thead>
              <tbody>{s.planets.map((p) => (
                <tr key={p.name} className="tone" style={toneStyle(grahaTone(p))}>
                  <td><strong>{p.name}</strong>{rules(p.name)}</td>
                  <td className="meter-col"><Meter t={grahaTone(p)} fill={p.rupas / most} mark={p.required / most} /></td>
                  <td className="num tone-text">{f2(p.percent)}</td>
                  <td className="num tone-text">{f2(p.rupas)}</td><td className="num">{f2(p.total)}</td>
                  <td className="num muted">{p.required.toFixed(2)}</td>
                  <td className="num good-text">{f2(p.ishta)}</td><td className="num bad-text">{f2(p.kashta)}</td>
                </tr>
              ))}</tbody></>
          ) : (
            <><thead><tr><th>Graha</th><th>Sthana</th><th>Kaala</th><th>Dig</th><th>Cheshta</th><th>Naisargika</th><th>Drik</th><th>Total</th></tr></thead>
              <tbody>{s.planets.map((p) => <tr key={p.name}><td><strong>{p.name}</strong></td>{parts
                .map((k) => <td key={k} className="num heat tone" style={toneStyle(at[k](p[k]))}>{f2(p[k])}</td>)}</tr>)}</tbody></>
          )}
        </table></div>
      </section>}
      {cusp && <section className="pane shadbala cusp">
        <div className="scroll"><table className="points strength">
          <thead><tr><th><strong>Graha</strong><span className="rules-head">Lord</span></th><th className="meter-col">Bala wrt Cusp</th><th>% Bala</th><th>Bhava</th><th>Cusp</th><th>Longitude</th></tr></thead>
          <tbody>{cusp.map((c) => (
            <tr key={c.name} className="tone" style={toneStyle(c.percent / 100)}>
              <td><strong>{c.name}</strong>{rules(c.name)}</td>
              <td className="meter-col"><Meter t={c.percent / 100} fill={c.percent / 100} /></td>
              <td className="num tone-text">{c.percent.toFixed(1)}</td>
              <td>{supOrd(ORDINAL[c.house - 1])}</td>
              <td className="num">{formatLon(c.cusp)}</td><td className="num">{formatLon(c.lon)}</td>
            </tr>
          ))}</tbody>
        </table></div>
      </section>}
      {only !== "graha" && <section className="pane shadbala bhava">
        <div className="scroll"><table className="points strength">
          <thead><tr><th><strong>Bhava</strong><span className="rules-head">Lord</span></th><th className="meter-col">Min. 7 Rupas</th><th>% Bala</th><th>Rupas</th><th>Bhava</th><th>Lord's</th><th>Dig</th><th>Drik</th></tr></thead>
          <tbody>{s.bhavas.map((b) => (
            <tr key={b.house} className="tone" style={toneStyle(house(b.rupas))}>
              <td><strong>{supOrd(ORDINAL[b.house - 1] ?? b.house)}</strong> <span className="muted">({b.lord})</span></td>
              <td className="meter-col"><Meter t={house(b.rupas)} fill={b.rupas / mostHouse} mark={7 / mostHouse} /></td>
              <td className="num tone-text">{f2(b.rupas / 7 * 100)}</td><td className="num tone-text">{f2(b.rupas)}</td>
              {[b.total, b.lord_bala, b.dig, b.drig].map((x, i) => <td key={i} className="num">{f2(x)}</td>)}
            </tr>
          ))}</tbody>
        </table></div>
      </section>}
    </>
  );
}

/** ``titled``: the print report, where the pane brings its own heading. */
export function Vimsopaka({ rows, titled }: { rows: S["vimsopaka"]; titled?: boolean }) {
  return (
    <section className="pane">
      {titled && <header className="pane-head"><h2>Vimsopaka bala</h2><CopyButton text={tableText(["Graha", "Shodasa varga", "Dasa varga", "Sapta varga", "Shad varga"], rows.map((r) => [r.name, f2(r.shodasa), f2(r.dasa), f2(r.sapta), f2(r.shad)]))} /></header>}
      <div className="scroll"><table className="points strength">
        <thead><tr><th>Graha</th><th>Shodasa varga</th><th>Dasa varga</th><th>Sapta varga</th><th>Shad varga</th></tr></thead>
        <tbody>{rows.map((r) => <tr key={r.name}><td><strong>{r.name}</strong></td>{[r.shodasa, r.dasa, r.sapta, r.shad].map((x, i) => (
          <td key={i} className="num"><span className="cell-meter">{f2(x)}<Meter t={(x - 5) / 12} fill={x / 20} /></span></td>
        ))}</tr>)}</tbody>
      </table></div>
    </section>
  );
}

const YOGA_GROUPS = ["All yogas", "Pancha maha purusha yogas", "Solar yogas", "Lunar yogas", "Naabhasa yogas", "Other popular yogas", "Raja yogas", "Raja sambandha yogas", "Dhana yogas", "Daridra yogas", "Parivraja yogas"];

/** Yogas: of any varga, by group, or the catalogue; Starlight has its own view. */
export function Yogas() {
  return useChart((s) => s.display.layout) === "starlight" ? <StarYogas /> : <WindowsYogas />;
}

const YOGA_TYPES = ["Mahapurusha", "Solar", "Lunar", "Naabhasa", "Other popular", "Raja", "Raja Sambandha", "Dhana", "Daridra", "Parivraja/Pravrajya"];
const BASIS_CLASS: Record<YogaBasis, string> = { Rasi: "rasi", Bhava: "bhava", "Rasi + Bhava": "both" };
const BASIS_HINT: Record<YogaBasis, string> = {
  Rasi: "Read from signs: conjunctions, own and exaltation signs, rasi aspects, counts from the Moon, Sun, AL or a lord",
  Bhava: "Read from bhavas by longitude: bhava placements, occupancy and bhava lords (the sign on each cusp)",
  "Rasi + Bhava": "Bhavas for placement and lordship, signs for the sign relations",
};

/** Starlight's yogas: the D-1 read by bhavas (houses by longitude) where a yoga is about houses, by rasis where it is about signs;
 *  grouped by kind, each with what it reads and where its givers sit. */
function StarYogas() {
  const birth = useChart((s) => s.birth)!;
  const [kind, setKind] = useKept("starYogaKind", "All");
  const division = useTopVarga();   // the top left chart's varga
  const [catalogue, setCatalogue] = useKept("yogaCatalogue", false);
  const q = useQuery({ queryKey: ["yogas", birth, 0, division, true], queryFn: () => api.yogas(birth, 0, division, true), enabled: !catalogue, placeholderData: (p) => p });
  const list = useQuery({ queryKey: ["yogaList"], queryFn: api.yogaList, enabled: catalogue, staleTime: Infinity });
  const [basis, setBasis] = useKept<YogaBasis | "">("starYogaBasis", "");
  const all: (YogaRow | YogaListRow)[] = (catalogue ? list.data : q.data) ?? [];
  // the two filters narrow each other: kind counts within the picked basis, basis counts within the picked kind
  const rows = basis ? all.filter((y) => y.basis === basis) : all;
  const count = (t: string) => rows.filter((y) => y.type === t).length;
  const kinds = YOGA_TYPES.filter((t) => count(t) > 0 || t === kind);
  const shown = kind === "All" ? kinds : kinds.filter((t) => t === kind);
  const ofKind = kind === "All" ? all : all.filter((y) => y.type === kind);
  const bases = (["Rasi", "Bhava", "Rasi + Bhava"] as YogaBasis[]).map((b) => [b, ofKind.filter((y) => y.basis === b).length] as const);
  const { open, node } = useMenu();
  return (
    // a right-click picks the kind of yoga, each with its count, and switches to the catalogue of all the supported ones; the header keeps only the basis filters
    <section className="pane star-yogas" onContextMenu={(e) => { e.preventDefault(); open(e, [
      { label: `All yogas (${rows.length})`, checked: kind === "All", onClick: () => setKind("All") },
      ...kinds.map((t) => ({ label: `${t} (${count(t)})`, checked: kind === t, onClick: () => setKind(t) })),
      "-",
      { label: "All supported yogas", checked: catalogue, onClick: () => setCatalogue(!catalogue) },
    ], "Yogas shown"); }}>
      {node}
      <header className="pane-head">
        <span className="row wrap">
          <span className="sy-legend" role="group" aria-label="Filter by what the yoga reads">
            {bases.map(([b, n]) => (
              <button key={b} type="button" title={`${BASIS_HINT[b]}. Click to show only these, again to show all.`} aria-pressed={basis === b}
                onClick={() => setBasis(basis === b ? "" : b)}><i className={`sy-basis ${BASIS_CLASS[b]}`}>{b}</i> {n}</button>
            ))}
            {!catalogue && division !== 1 && <span className="muted">Bhavas in a varga are its signs</span>}
          </span>
        </span>
      </header>
      <Loaded<unknown> q={catalogue ? list : q}>{() => (
        <div className="scroll tall">
          {shown.map((t) => (
            <section key={t} className="sy-group">
              <h3>{t} <span className="muted">{count(t)}</span></h3>
              <ul className="sy-cards">{rows.filter((y) => y.type === t).map((y, i) => (
                <li key={i} className="sy-card">
                  <header><h4>{y.name}</h4><i className={`sy-basis ${BASIS_CLASS[y.basis]}`} title={BASIS_HINT[y.basis]}>{y.basis}</i></header>
                  <p className="sy-result">{supOrd(y.result)}</p>
                  {"places" in y && (y.places.length > 0 ? (
                    <ul className="sy-givers" aria-label="Formed by">{y.places.filter((p, k) => y.places.findIndex((x) => x[0] === p[0]) === k).map(([g, h, s]) => (
                      <li key={g}><strong>{g}</strong> {supOrd(ord(h))} · {SIGNS[s]}</li>
                    ))}</ul>
                  ) : y.type === "Naabhasa" && <p className="muted small">Naabhasa yoga, felt throughout life</p>)}
                  <p className="sy-rule">{supOrd(y.definition)}</p>
                </li>
              ))}</ul>
            </section>
          ))}
          {rows.length === 0 && <p className="empty small">{basis && all.length ? `No ${basis} yogas here. Click ${basis} again to show all.` : `No yogas in this chart${division !== 1 ? " for this varga" : ""}.`}</p>}
        </div>
      )}</Loaded>
    </section>
  );
}

function WindowsYogas() {
  const birth = useChart((s) => s.birth)!;
  const [group, setGroup] = useKept("yogaGroup", 0);
  const [division, setDivision] = useKept("yogaDivision", 1);
  const [catalogue, setCatalogue] = useKept("yogaCatalogue", false);
  const q = useQuery({ queryKey: ["yogas", birth, group, division], queryFn: () => api.yogas(birth, group, division), enabled: !catalogue, placeholderData: (p) => p });
  const list = useQuery({ queryKey: ["yogaList"], queryFn: api.yogaList, enabled: catalogue, staleTime: Infinity });
  const text = catalogue ? tableText(["Index & Type", "Yoga", "Brief definition of yoga", "Results ascribed to yoga"], (list.data ?? []).map((y) => [`${y.index} ${y.type}`, y.name, y.definition, y.result]))
    : tableText(["Yoga", "Varga", "Yoga givers", "Results ascribed to yoga", "Brief definition of yoga"], (q.data ?? []).map((y) => [y.name, y.varga, y.givers_text, y.result, y.definition]));
  return (
    <section className="pane">
      <header className="pane-head">
        <span className="row wrap">
          <select aria-label="Kind of yoga" value={group} disabled={catalogue} onChange={(e) => setGroup(Number(e.target.value))}>{YOGA_GROUPS.map((t, i) => <option key={t} value={i}>{t}</option>)}</select>
          <DivisionSelect value={division} onChange={setDivision} label="Select a varga" />
          <label className="check"><input type="checkbox" checked={catalogue} onChange={(e) => setCatalogue(e.target.checked)} /> Just show a list of supported yogas</label>
          <CopyButton text={text} />
        </span>
      </header>
      {catalogue ? <Loaded q={list}>{(rows) => (
        <div className="scroll tall"><ul className="yoga-list">{rows.map((y, i) => (
          <li key={i} className="yoga">
            <header><h3>{y.name}</h3><span className="chip">{y.type}</span><span className="chip muted">No. {y.index}</span></header>
            <p>{supOrd(y.result)}</p><p className="muted">{supOrd(y.definition)}</p>
          </li>
        ))}</ul></div>
      )}</Loaded> : <Loaded q={q}>{(rows) => (
        <div className="scroll tall">
          {rows.length > 0 && <p className="yoga-count muted pad">{rows.length} {rows.length === 1 ? "yoga" : "yogas"} in this chart</p>}
          <ul className="yoga-list">{rows.map((y, i) => (
            <li key={i} className="yoga">
              <header><h3>{y.name}</h3><span className="chip">{y.varga}</span>{y.type && <span className="chip muted">{y.type}</span>}</header>
              <p>{supOrd(y.result)}</p>
              <dl><div><dt>Formed by</dt><dd>{supOrd(y.givers_text)}</dd></div><div><dt>Rule</dt><dd>{supOrd(y.definition)}</dd></div></dl>
            </li>
          ))}</ul>
          {rows.length === 0 && <p className="empty small">No yogas of this kind in this chart. Try another kind or varga.</p>}
        </div>
      )}</Loaded>}
    </section>
  );
}

/** The last three stays of Saturn (red) and Jupiter (green) in a highlighted cell's nakshatra and rasi, each with the MD-ADs then. */
function KinTransits({ planet, star, sign, nakshatra, birth, onClose }: { planet: number; star: number; sign: number; nakshatra: string; birth: Birth; onClose: () => void }) {
  const q = useQuery({ queryKey: ["pindaTransits", birth, star, sign], queryFn: () => api.pindaTransits(birth, star, sign) });
  const [n, who] = KIN[planet];
  const list = (vs: TransitVisit[]) => vs.length === 0 ? <p className="muted small">None since birth</p> : (
    <ol className="kin-visits">{vs.map((v) => (
      <li key={v.start}>
        <span className="kin-head"><span className="kin-dates">{v.start} → {v.end ?? "…"}</span> <span className="kin-dasas">{v.dasas.join(", ") || "—"}</span></span>
        <table className="kin-passes"><tbody>{v.passes.flatMap((p, n) => [
          <tr key={`i${n}`}><th scope="row">In</th><td>{v.born_in && n === 0 ? "at birth" : p.in}{p.in_r && <> <Retro /></>}</td><td>{p.in_dasa ?? ""}</td></tr>,
          <tr key={`o${n}`}><th scope="row">Out</th><td>{p.out ?? "still in"}{p.out_r && <> <Retro /></>}</td><td>{p.out_dasa ?? ""}</td></tr>,
        ])}</tbody></table>
      </li>
    ))}</ol>
  );
  return (
    <Modal wide title={`${who}: ${ord(n)} from ${["Lagna", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"][planet]}`} onClose={onClose}>
      <p className="muted">The last three times Saturn and Jupiter transited {nakshatra} and {ZODIAC[sign]}: each stay with the Vimsottari MD-ADs it fell in, then every entry and exit (R: retrograde, which can take it out and back in) with the MD-AD-PD then.</p>
      <Loaded q={q}>{(t) => (
        <div className="kin-grid">
          {(["saturn", "jupiter"] as const).map((p) => (
            <section key={p} className={`kin-col ${p}`}>
              <h3>{p === "saturn" ? "Saturn" : "Jupiter"}</h3>
              <div className="kin-pair">
                <div><h4>In {nakshatra}</h4>{list(t[p].star)}</div>
                <div><h4>In {ZODIAC[sign]}</h4>{list(t[p].sign)}</div>
              </div>
            </section>
          ))}
        </div>
      )}</Loaded>
      <menu><button className="primary" onClick={onClose}>Close</button></menu>
    </Modal>
  );
}

/** One bar graph: a single measure per planet, its own scale from zero, each value printed as the tables print it. */
/** `ranked` prints each bar's place, 1st for the highest value, inside the bar. */
/** `fill`: drawn at the size of the box it is given (Starlight), so the bars and the text grow with it. */
export function Bars({ p, wide, ranked, fill }: { p: S["bars"][number]; wide?: boolean; ranked?: boolean; fill?: boolean }) {
  const [ref, k, px] = useShape();
  const s = fill ? pageScale() : 1;     // filled, drawn in the page's px over its scale, so the labels grow with the page
  const W = fill ? px / s : wide ? 600 : 300, H = fill ? Math.max(px * k / s, 120) : 170, BASE = H - (fill ? 34 : 30), TOP = 22;
  const max = Math.max(...p.values, 1e-9);
  const slot = (W - 8) / p.values.length;
  const rank = spread(p.values);
  const place = p.values.map((v, i) => 1 + p.values.filter((u, j) => u > v || (u === v && j < i)).length);
  const at = (v: number) => (/kashta/i.test(p.title) ? 1 - rank(v) : rank(v));   // more kashta is worse
  return (
    <figure className={"bars" + (wide ? " wide" : "") + (fill ? " fill" : "")}>
      <figcaption>{p.title}</figcaption>
      <svg ref={ref} viewBox={`0 0 ${W} ${H}`} role="img" aria-label={`${p.title}: ${p.labels.map((l, i) => `${l} ${p.values[i].toFixed(p.digits)}`).join(", ")}`}>
        <line x1={2} x2={W - 2} y1={BASE} y2={BASE} className="bar-base" />
        {p.values.map((v, i) => {
          const h = (Math.max(v, 0) / max) * (BASE - TOP), x = 4 + i * slot, w = fill ? Math.min(slot * 0.62, 64) : Math.min(slot - 2, 34), mid = x + (slot - 2) / 2, left = mid - w / 2;
          const r = Math.min(4, h);
          return (
            <g key={i}>
              <title>{p.labels[i]}: {v.toFixed(Math.max(p.digits, 2))}</title>
              <rect x={x} y={TOP - 18} width={slot} height={H - TOP + 18} fill="transparent" />
              {h > 0 && <path className="bar tone" style={toneStyle(at(v))} d={`M${left} ${BASE} V${BASE - h + r} Q${left} ${BASE - h} ${left + r} ${BASE - h} H${left + w - r} Q${left + w} ${BASE - h} ${left + w} ${BASE - h + r} V${BASE} Z`} />}
              {ranked && h > 16 && <text x={mid} y={BASE - h + 13} textAnchor="middle" className="bar-rank">{ord(place[i])}</text>}
              <text x={mid} y={BASE - h - 5} textAnchor="middle" className="bar-value">{v.toFixed(p.digits)}</text>
              <text x={mid} y={H - (fill ? 10 : 12)} textAnchor="middle" className="bar-label">{p.labels[i]}</text>
            </g>
          );
        })}
      </svg>
      {p.note && <p className="bar-note muted">{p.note}</p>}
    </figure>
  );
}

const BAR_KINDS = [{ id: "graha", name: "Graha" }, { id: "bhava", name: "Bhava" }, { id: "breakup", name: "Shadbala breakup" }, { id: "vimsopaka", name: "Vimsopaka" }, { id: "vaiseshikamsa", name: "Vaiseshikamsa" }, { id: "rashmis", name: "Rashmis & Ishta phala" }];

/** Bar graphs. */
function BarGraphs() {
  const birth = useChart((s) => s.birth)!;
  const [kind, setKind] = useKept("barKind", "graha");
  const q = useQuery({ queryKey: ["bars", birth, kind], queryFn: () => api.bars(birth, kind, 1), placeholderData: (p) => p });
  const fill = useChart((s) => s.display.layout) === "starlight";
  return (
    <section className={fill ? "pane bars-pane" : "pane"}>
      <header className="pane-head">
        <SubTabs label="Which graphs" tabs={BAR_KINDS} value={kind} onChange={setKind} />
      </header>
      <Loaded q={q}>{(bars) => <div className="bar-grid">{bars.map((p) => <Bars key={p.title} p={p} wide={p.values.length > 9} ranked={kind === "bhava"} fill={fill} />)}</div>}</Loaded>
    </section>
  );
}


// Starlight's Avasthas tab, one sub-tab a kind
const AVASTHA_TABS = [{ id: "age", name: "Age" }, { id: "alertness", name: "Alertness" }, { id: "mood", name: "Mood" }, { id: "activity", name: "Activity" }, { id: "lajjitadi", name: "Lajjitadi" }] as const;
type AvasthaTab = (typeof AVASTHA_TABS)[number]["id"];
const avMeaning = (v: string) => /\(([^)]*)\)/.exec(v)?.[1] ?? "";
const avParts = (v: string) => (v && v !== "-" ? v.split(/,\s*(?![^(]*\))/) : []);
// BPHS 45.38: the sub-state says how fully the activity's results come, good or bad alike
const FELT: Record<string, [number, string]> = { Cheshta: [3, "Felt fully"], Drishti: [2, "Felt halfway"], Vicheshta: [1, "Felt a little"] };
// the letters of each anka, as BPHS 45 lists them
const ANKA_LETTERS = ["a, ka, cha, ḍa, dha, bha, va", "i, kha, ja, ḍha, na, ma, sha", "u, ga, jha, ta, pa, ya, ṣa", "e, gha, ṭa, tha, pha, ra, sa", "o, ṅa, ṭha, da, ba, la, ha"];
const AV_SCALES: Partial<Record<AvasthaTab, string[]>> = { age: ["Baala", "Kumara", "Yuva", "Vriddha", "Mrita"], alertness: ["Jaagrita", "Swapna", "Sushupta"] };

/** One graha's card: its state(s) marked red weak to green strong, with the whole scale for age and alertness. */
function AvCard({ name, value, scale, felt, dignity, why }: { name: string; value: string; scale?: string[]; felt?: string; dignity?: string; why?: string }) {
  const parts = avParts(value), t = parts.length ? parts.reduce((a, x) => a + avScore(x), 0) / parts.length : 0.5;
  const at = parts.map(avName);
  return (
    <article className="av-card tone" style={toneStyle(t)}>
      <header><strong>{name}<Dignity d={dignity} /></strong><span className="av-verdict">{parts.length ? avWord(t) : "-"}</span></header>
      <ul className="av-chips">{parts.map((x) => <li key={x} className="tone" style={toneStyle(avScore(x))}><b>{avName(x)}</b> <small>{avMeaning(x)}</small></li>)}</ul>
      {why && <ul className="av-why" aria-label="Why">{why.split("; ").map((x) => <li key={x}>{x}</li>)}</ul>}
      {scale && <ol className="av-scale" aria-label="Where it sits">{scale.map((x) => <li key={x} className={at.includes(x) ? "tone on" : "tone"} style={toneStyle(AV_SCORE[x])}>{x}</li>)}</ol>}
      {felt !== undefined && (felt ? (
        <p className="av-felt" title={felt}><span aria-hidden="true">{[1, 2, 3].map((k) => <i key={k} className={k <= FELT[avName(felt)][0] ? "on" : ""} />)}</span>{FELT[avName(felt)][1]} <small>{avName(felt)}</small></p>
      ) : <p className="av-felt muted">Pick the name's first syllable above</p>)}
    </article>
  );
}

/** Starlight's Avasthas tab: each kind of avastha in a sub-tab of its own. */
function Avasthas() {
  const birth = useChart((s) => s.birth)!;
  const [sub, setSub] = useKept<AvasthaTab>("avasthaSub", "age");
  const [varga, setVarga] = useKept("strengthListVarga", 1);
  const basic = useQuery({ queryKey: ["table", birth, "avasthas_parashara", varga, undefined], queryFn: () => api.table(birth, "avasthas_parashara", varga), placeholderData: (p) => p });
  const chartName = useChart((s) => s.name);
  const [namePick, setNamePick] = useKept("avNameNo", "auto");
  const fromName = nameAnka(chartName);
  const nameNo = namePick === "auto" ? fromName?.n : Number(namePick);
  const sayana = useQuery({ queryKey: ["table", birth, "sayanadi", 1, undefined], queryFn: () => api.table(birth, "sayanadi"), placeholderData: (p) => p, enabled: sub === "activity" });
  const laj = useQuery({ queryKey: ["grahaInsights", birth], queryFn: () => api.grahaInsights(birth), placeholderData: (p) => p, enabled: sub === "lajjitadi" });
  const byVarga = sub === "alertness" || sub === "mood";
  const rasiDignity: Record<string, string> = Object.fromEntries(basic.data?.rows.map((r) => [r[0], r[4]]) ?? []);
  return (
    <section className="pane avastha-pane">
      <header className="pane-head">
        <span className="row wrap">
          <SubTabs label="Kinds of avastha" tabs={[...AVASTHA_TABS]} value={sub} onChange={setSub} />
        </span>
        {byVarga && <DivisionSelect value={varga} onChange={setVarga} label="Varga for alertness and mood" />}
        {sub === "activity" && <label className="row av-name" title="BPHS 45: how fully the activity is felt depends on the first syllable of the native's name">Name's first syllable<select value={namePick} onChange={(e) => setNamePick(e.target.value)}>
            <option value="auto">{fromName ? `"${chartName}": ${fromName.syllable[0].toUpperCase() + fromName.syllable.slice(1)} = ${fromName.n}` : "No name to read"}</option>
            {ANKA_LETTERS.map((x, i) => <option key={i} value={i + 1}>{i + 1}: {x}</option>)}
          </select></label>}
      </header>
      {sub === "activity" ? <Loaded q={sayana}>{(t) => (
        <div className="av-cards">{t.rows.map(([p, act, ...ints]) => <AvCard key={p} name={p} value={act} felt={nameNo ? ints[nameNo - 1] : ""} dignity={rasiDignity[p]} />)}</div>
      )}</Loaded> : sub === "lajjitadi" ? <Loaded q={laj}>{(rows) => (
        <div className="av-cards">{rows.map((r) => <AvCard key={r.name} name={r.name} value={r.avasthas.Lajjitadi} dignity={rasiDignity[r.name]} />)}</div>
      )}</Loaded> : <Loaded q={basic}>{(t) => {
        // columns: planet, age, alertness, mood, dignity in the rasi, in the varga, then why age, alertness and mood
        const col = { age: 1, alertness: 2, mood: 3 }[sub];
        return <div className="av-cards">{t.rows.map((r) => <AvCard key={r[0]} name={r[0]} value={r[col]} scale={AV_SCALES[sub]} dignity={r[sub === "age" ? 4 : 5]} why={r[col + 5]} />)}</div>;
      }}</Loaded>}
    </section>
  );
}

const LOW_IS_GOOD = /kashta|asubha/i;

/** Starlight's strengths lists, like the Shadbala break-up: each number toned weak to strong against its column, a word after
 *  a number in that number's tone. */
function TonedTable({ t }: { t: Table }) {
  const at = t.columns.map((c, k) => {
    const xs = t.rows.map((r) => parseFloat(r[k]));
    if (k === 0 || !xs.length || !xs.every(Number.isFinite)) return null;
    const f = spread(xs);
    return (i: number) => (LOW_IS_GOOD.test(c) ? 1 - f(xs[i]) : f(xs[i]));
  });
  const tone = at.map((f, k) => f ?? at.slice(1, k).reverse().find((g) => g) ?? null);
  return (
    <div className="scroll tall"><table className={t.columns.length <= 6 ? "points strength even-cols" : "points strength planet-col"}>
      <thead><tr>{t.columns.map((c) => <th key={c}>{c}</th>)}</tr></thead>
      <tbody>{t.rows.map((r, i) => <tr key={i}>{r.map((c, k) => {
        const f = tone[k];
        return k === 0 ? <td key={k}><strong>{supOrd(c)}</strong></td>
          : f ? <td key={k} className={at[k] ? "num heat tone" : "heat tone"} style={toneStyle(f(i))}>{c}</td> : <td key={k}>{supOrd(c)}</td>;
      })}</tr>)}</tbody>
    </table></div>
  );
}


/** Starlight's Vaiseshikamsa tab: each graha's rank in each scheme out of its vargas; then each scheme's ranks, top
 *  down, with the grahas on the rank they reach. */
function Vaiseshikamsas() {
  const birth = useChart((s) => s.birth)!;
  const q = useQuery({ queryKey: ["table", birth, "vaiseshikamsa", 1, undefined], queryFn: () => api.table(birth, "vaiseshikamsa", 1), placeholderData: (p) => p });
  const chips = (rows: string[][]) => <span className="vai-who">{rows.map((r) => <b key={r[0]} title={r[0]}>{r[0].slice(0, 2)}</b>)}</span>;
  return (
    <Loaded q={q}>{(t) => (
      <>
        <section className="pane vai-top">
          <div className="scroll"><table className="points strength vai-table">
            <thead><tr><th>Graha</th>{VAI.map((v) => <th key={v.col}>{v.name} <span className="muted">({v.of})</span></th>)}</tr></thead>
            <tbody>{t.rows.map((r) => <tr key={r[0]}><td><strong>{r[0]}</strong></td>{VAI.map((v) => {
              const n = vaiCount(r[v.col]);
              return <td key={v.col} className={n ? "heat tone" : undefined} style={n ? toneStyle(vaiTone(n, v.of)) : undefined}>
                <span className="vai-cell">
                  {n ? <b>{v.steps[n - 2]}</b> : <span className="muted">No rank</span>}
                  {n > 0 && <span className="vai-of">{n}<span className="muted">/{v.of}</span></span>}
                </span>
              </td>;
            })}</tr>)}</tbody>
          </table></div>
        </section>
        <section className="pane vai-ranks">{VAI.map((v) => {
          const at = (n: number) => t.rows.filter((r) => vaiCount(r[v.col]) === n), none = at(0);
          return (
            <div key={v.col} className="vai-rank">
              <h3>{v.name} <span className="muted">ranks</span></h3>
              <ol>{v.steps.map((name, i) => ({ n: i + 2, name })).reverse().map(({ n, name }) => {
                const who = at(n);
                return <li key={n} className={who.length ? "tone on" : undefined} style={who.length ? toneStyle(vaiTone(n, v.of)) : undefined}>
                  <span className="vai-n">{n}</span><span className="vai-step">{name}</span>{who.length > 0 && chips(who)}
                </li>;
              })}</ol>
              {none.length > 0 && <p className="vai-none" title={`Good in fewer than 2 of the ${v.of} vargas`}><span>No rank</span>{chips(none)}</p>}
            </div>
          );
        })}</section>
      </>
    )}</Loaded>
  );
}

// Starlight's Others: the shadbala's parts, the rashmis' table in two, and the three Tajika balas under one "Tajika" dropdown
const STAR_OTHERS = [{ id: "sthana", name: "Sthana" }, { id: "kaala", name: "Kala" }, { id: "dig", name: "Dig" }, { id: "cheshta", name: "Cheshta" }, { id: "drig", name: "Drik" },
  { id: "naisargika", name: "Naisargika" }, { id: "ishta", name: "Ishta & Kashta" }, { id: "rashmis", name: "Rashmis" }];
const TAJAKA = [{ id: "pancha", name: "5-vargeeya" }, { id: "dwadasa", name: "12-vargeeya" }, { id: "harsha", name: "Harsha" }];
const RASHMI_COLS: Record<string, number[]> = { ishta: [0, 5, 6], rashmis: [0, 1, 2, 3, 4] };

function StarOthers() {
  const birth = useChart((s) => s.birth)!;
  const [saved, setTab] = useSaved<string>("starOthers", "sthana");
  const [taj, setTaj] = useSaved<string>("starTajaka", "pancha");
  const tab = saved === "tajaka" || STAR_OTHERS.some((x) => x.id === saved) ? saved : "sthana";
  const view = tab === "tajaka" ? taj : tab === "ishta" ? "rashmis" : tab;
  const q = useQuery({ queryKey: ["table", birth, view, 1, undefined], queryFn: () => api.table(birth, view, 1), placeholderData: (p) => p });
  const cols = RASHMI_COLS[tab];
  return (
    <section className="pane">
      <header className="pane-head star-others-head">
        <SubTabs label="Balas lists" tabs={STAR_OTHERS} value={tab} onChange={setTab} />
        <select aria-label="Tajika" className={tab === "tajaka" ? "tajaka-pick on" : "tajaka-pick"} value={tab === "tajaka" ? taj : ""} onChange={(e) => { setTaj(e.target.value); setTab("tajaka"); }}>
          <option value="" disabled hidden>Tajika</option>
          {TAJAKA.map((x) => <option key={x.id} value={x.id}>{x.name}</option>)}
        </select>
      </header>
      <Loaded q={q}>{(x) => <TonedTable t={cols ? { columns: cols.map((k) => x.columns[k]), rows: x.rows.map((r) => cols.map((k) => r[k])) } : x} />}</Loaded>
    </section>
  );
}

function OtherLists() {
  const list = useQuery({ queryKey: ["tables"], queryFn: api.tables });
  const birth = useChart((s) => s.birth)!;
  const [view, setView] = useSaved<string>("strengthList", "sthana");
  const [varga, setVarga] = useKept("strengthListVarga", 1);
  const client = useQueryClient();
  const s = currentSettings();
  const set = (k: string, v: boolean) => { saveSettings({ ...s, [k]: v }); client.invalidateQueries(); };
  const avastha = view === "avasthas";
  const t = useQuery({ queryKey: ["table", birth, view, varga, undefined], queryFn: () => api.table(birth, view, varga) });
  return (
    <section className="pane">
      <header className="pane-head">
        <span className="row wrap">
          <select aria-label="Balas list" value={view} onChange={(e) => setView(e.target.value)}>
            {list.data?.strengths.map((v) => <option key={v.key} value={v.key}>{v.name}</option>)}
          </select>
          {avastha && <DivisionSelect value={varga} onChange={setVarga} label="Varga for alertness and mood" />}
          {avastha && <label className="row">Relationships<select value={String(!!s.avastha_compound)} onChange={(e) => set("avastha_compound", e.target.value === "true")}><option value="false">Permanent</option><option value="true">Compound</option></select></label>}
          {t.data && <CopyButton text={tableText(t.data.columns, t.data.rows)} />}
        </span>
      </header>
      <TableView view={view} varga={varga} />
    </section>
  );
}

const TABS = [{ id: "shadbala", name: "Shadbala & Bhava bala" }, { id: "av", name: "Ashtakavarga" }, { id: "vim", name: "Vimsopaka" }, { id: "vai", name: "Vaiseshikamsa" }, { id: "yogas", name: "Yogas" }, { id: "avasthas", name: "Avasthas" }, { id: "other", name: "Other balas" }, { id: "bars", name: "Bar graphs" }] as const;

export function Strengths() {
  const starlight = useChart((s) => s.display.layout) === "starlight";
  // Starlight: Avasthas and Vaiseshikamsa tabs of their own, and some tabs' names cut short
  const short: Partial<Record<string, string>> = { shadbala: "Shad & Bhava", other: "Others", bars: "Charts" };
  const tabs = TABS.filter((t) => starlight || (t.id !== "avasthas" && t.id !== "vai")).map((t) => (starlight && short[t.id] ? { ...t, name: short[t.id]! } : t));
  const [saved, setTab] = useSaved<(typeof TABS)[number]["id"]>("strengths", "shadbala");
  const tab = tabs.some((t) => t.id === saved) ? saved : "shadbala";
  const q = useView("strengths");
  return (
    <div className="right lab">
      <header className="lab-head">
        <h1>Balas</h1>
        <SubTabs tabs={tabs} value={tab} onChange={setTab} label="Balas views" />
      </header>
      {tab === "av" ? <Ashtakavarga /> : tab === "yogas" ? <Yogas /> : tab === "avasthas" ? <Avasthas /> : tab === "vai" ? <Vaiseshikamsas /> : tab === "other" ? (starlight ? <StarOthers /> : <OtherLists />) : tab === "bars" ? <BarGraphs />
        : <Loaded q={q}>{(s) => tab !== "shadbala" ? <Vimsopaka rows={s.vimsopaka} />
          : starlight ? <div className="star-stack"><Shadbala s={s.shadbala} cusp={s.cusp_bala} /></div>     // Starlight: the three tables at full height, one scroll under the sub tabs
          : <Shadbala s={s.shadbala} cusp={s.cusp_bala} />}</Loaded>}
    </div>
  );
}
