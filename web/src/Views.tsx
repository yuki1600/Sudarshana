import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api, currentSettings, saveSettings } from "./api";
import { useBasics, useKept, useSaved, useSettings, useTopVarga, useView } from "./hooks";
import { formatLon } from "./format";
import { BodiesDialog, CoreInfo, GrahaCells, KeyInfo, SmallAv, useBodies } from "./Panels";
import { useChart } from "./store";
import { openLore } from "./Lore";
import { CopyButton, Loaded, SubTabs, supOrd, tableText } from "./ui";

export const SYSTEMS: [number, string][] = [[0, "Each rasi is a bhava"], [1, "Equal bhavas (30 deg each)"], [2, "Equal bhavas based on nakshatra padas (9 padas each)"], [3, "Porphyry bhavas (Sripathi)"], [4, "Placidus bhavas (KP/Krishnamoorthy)"], [5, "Koch bhavas"], [6, "Regiomontanus bhavas"], [7, "Campanus bhavas"], [8, "Axial rotation system bhavas"], [9, "Polich/Page (topocentric system) bhavas"], [10, "Alcabitus bhavas"]];
const REFS = ["Lagna", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"];

/** Houses. */
/** ``shared``: the reference is the bhava chart's (Starlight, where that chart is beside it), else its own. A graha's houses have their own system, equal unless changed. */
export function Houses({ shared }: { shared?: boolean }) {
  const birth = useChart((s) => s.birth)!;
  const client = useQueryClient();
  const s = useSettings();
  const set = (k: string, v: number | boolean) => { saveSettings({ ...currentSettings(), [k]: v }); client.invalidateQueries(); };
  const [own, setOwn] = useState(0);
  const ref = shared ? Number(s.bhava_ref ?? 2) : own;     // 2 (moon) is the server's default
  const setRef = (r: number) => (shared ? set("bhava_ref", r) : setOwn(r));
  const system = ref ? "house_type_graha" : "house_type";
  const q = useQuery({ queryKey: ["houses", birth, ref], queryFn: () => api.houses(birth, ref), placeholderData: (p) => p });
  const cols = ["Bhava", "Start", "Cusp", "End", "Grahas in it"];
  return (
    <section className="pane"><header className="pane-head"><h2>Bhavas</h2>
      <span className="row wrap">
        <select aria-label={ref ? "Bhava system from a graha" : "Bhava system"} value={Number(s[system] ?? (ref ? 1 : 3))} onChange={(e) => set(system, Number(e.target.value))}>{SYSTEMS.map(([v, n]) => <option key={v} value={v}>{n}</option>)}</select>
        <label className="row">Ref:<select value={ref} onChange={(e) => setRef(Number(e.target.value))}>{REFS.map((n, i) => <option key={n} value={i}>{n}</option>)}</select></label>
        <SubTabs label="Where the reference falls in the first bhava" value={s.house_cusp_in_middle !== false ? "middle" : "start"} onChange={(v) => set("house_cusp_in_middle", v === "middle")}
          tabs={[{ id: "middle", name: "Middle" }, { id: "start", name: "Start" }]} />
        <CopyButton text={tableText(cols, (q.data ?? []).map((r) => [r.house, formatLon(r.start), formatLon(r.cusp), formatLon(r.end), r.occupants.join(", ")]))} />
      </span></header>
      <Loaded q={q}>{(rows) => (
        <div className="scroll"><table className="points">
          <thead><tr><th>Bhava</th><th>Start</th><th>Cusp</th><th>End</th><th>Grahas in it</th></tr></thead>
          {/* Starlight: a bhava's row opens its reading, counted from the bhava chart's reference */}
          <tbody>{rows.map((r, i) => (
            <tr key={r.house} className={shared ? "pickable" : undefined} onClick={shared ? () => openLore({ kind: "bhava", n: i + 1, ref }) : undefined}>
              <td>{shared ? <button type="button" className="nak-link" data-tip="Read this bhava">{supOrd(r.house)}</button> : supOrd(r.house)}</td><td className="num">{formatLon(r.start)}</td><td className="num">{formatLon(r.cusp)}</td>
              <td className="num">{formatLon(r.end)}</td><td>{r.occupants.join(", ")}</td></tr>
          ))}</tbody>
        </table></div>
      )}</Loaded>
    </section>
  );
}

const KP_COLUMNS = ["Nakshatra lord", "Sub lord", "Prati-sub", "Sookshma-sub", "Praana-sub", "Deha-sub"];
const KP_VIEWS: [string, string][] = [["lords", "Nakshatra and sub lords of each graha (upto 5 levels)"], ["0", "Grahas occupying each graha's nakshatra"], ["1", "Grahas occupying each graha's sub"], ["2", "Grahas occupying each graha's prati-sub (2nd level)"], ["3", "Grahas occupying each graha's sookshma-sub (3rd level)"], ["4", "Grahas occupying each graha's praana-sub (4th level)"], ["5", "Grahas occupying each graha's deha-sub (5th level)"]];
const KP_LORDS = ["Su", "Mo", "Ma", "Me", "Ju", "Ve", "Sa", "Ra", "Ke"];

/** KP. */
export function Kp() {
  const q = useView("kp");
  const [view, setView] = useKept("kp.view", "lords");
  const occupied = (rows: { label: string; lords: string[] }[], level: number) => KP_LORDS.map((p) => [p, rows.filter((r) => !r.label.endsWith("bhava") && r.lords[level] === p).map((r) => r.label).join(", ") || "-"]);
  const text = q.data ? (view === "lords" ? tableText(["Body / Cusp", ...KP_COLUMNS], q.data.map((r) => [r.label, ...r.lords])) : tableText(["Graha", "Occupied by"], occupied(q.data, Number(view)))) : "";
  return (
    <section className="pane"><header className="pane-head"><h2>KP</h2>
      <span className="row wrap"><select aria-label="KP list" value={view} onChange={(e) => setView(e.target.value)}>{KP_VIEWS.map(([v, n]) => <option key={v} value={v}>{n}</option>)}</select><CopyButton text={text} /></span></header>
      <Loaded q={q}>{(rows) => view === "lords" ? (
        <div className="scroll"><table className="points">
          <thead><tr><th>Body / Cusp</th>{KP_COLUMNS.map((c) => <th key={c}>{c}</th>)}</tr></thead>
          <tbody>{rows.map((r) => (<tr key={r.label}><td>{supOrd(r.label)}</td>{r.lords.map((l, i) => <td key={i}>{supOrd(l)}</td>)}</tr>))}</tbody>
        </table></div>
      ) : (
        <div className="scroll"><table className="points">
          <thead><tr><th>Graha</th><th>Bodies in its {KP_COLUMNS[Number(view)].replace(" lord", "").toLowerCase()}</th></tr></thead>
          <tbody>{occupied(rows, Number(view)).map(([p, b]) => <tr key={p}><td>{supOrd(p)}</td><td>{supOrd(b)}</td></tr>)}</tbody>
        </table></div>
      )}</Loaded>
    </section>
  );
}

const AMSA_DIVISIONS = [9, 2, 3, 4, 7, 10, 12, 16, 20, 24, 27, 30, 40, 45, 60, 150];

export function AmsaRulers() {
  const birth = useChart((s) => s.birth)!;
  const [chosen, setDivision] = useKept("amsaRulers.division", 10);
  const starlight = useChart((s) => s.display.layout) === "starlight", top = useTopVarga();
  const division = !starlight ? chosen : AMSA_DIVISIONS.includes(top) ? top : 60;   // Starlight: the top left chart's varga; the rasi, which has no amsa rulers, the D-60's
  const { bodies, setBodies } = useBodies();
  const [picking, setPicking] = useKept("amsaRulers.picking", false);
  const q = useQuery({ queryKey: ["amsa", birth, division], queryFn: () => api.amsa(birth, division), placeholderData: (p) => p });
  const cols = ["Body", "Division", "Index", `In whose amsa in D-${division}`];
  const groups = useQuery({ queryKey: ["keyInfo", birth, 1], queryFn: () => api.keyInfo(birth, 1) });
  const groupOf = new Map((groups.data ?? []).map((r) => [r.name, r.group]));
  const kept = (q.data ?? []).filter((r) => bodies[groupOf.get(r.name) ?? ""] !== false);
  const rows = kept.map((r) => [r.name, String(r.division), String(r.index), r.meaning ? `${r.ruler} (${r.meaning})` : r.ruler]);
  const tone = (i: number) => (kept[i].tone ? `amsa-${kept[i].tone}` : "");   // green kind, yellow mixed, red harsh (D-60: BPHS's benefic and cruel shashtyamsas)
  // Starlight: each body drawn as the Grahas tab draws it, in the top left chart's varga (the same queries, so they're shared)
  const points = useQuery({ queryKey: ["keyInfo", birth, top], queryFn: () => api.keyInfo(birth, top), enabled: starlight, placeholderData: (p) => p });
  const insights = useQuery({ queryKey: ["grahaInsights", birth, top], queryFn: () => api.grahaInsights(birth, top), enabled: starlight, placeholderData: (p) => p });
  if (starlight) return (
    <section className="pane key-stack">
      <Loaded q={q}>{() => (
        <div className="scroll key-points"><table className="points amsa-table">
          <thead><tr><th colSpan={3}>Body <small className="muted">(as per D-{top})</small></th><th>Division</th><th>Index</th><th>{cols[3]}</th></tr></thead>
          <tbody>{kept.map((r, k) => {
            const g = insights.data?.find((x) => x.name === r.name);
            return (
              <tr key={r.name} className={r.name === "Lagna" ? "lagna" : undefined}>
                <GrahaCells r={points.data?.find((x) => x.name === r.name) ?? { name: r.name, retrograde: false, karaka: null }} g={g} />
                <td className="num">{r.division}</td><td className="num">{r.index}</td>
                <td className={tone(k)}>{rows[k][3]}</td>
              </tr>
            );
          })}</tbody>
        </table></div>
      )}</Loaded>
    </section>
  );
  return (
    <section className="pane"><header className="pane-head"><h2>Amsa rulers</h2>
      <span className="row">
        <select aria-label="Division" value={division} onChange={(e) => setDivision(Number(e.target.value))}>
          {AMSA_DIVISIONS.map((d) => <option key={d} value={d}>{d === 150 ? "Nadyamsa (D-150)" : `D-${d}`}</option>)}
        </select>
        <button onClick={() => setPicking(true)}>Bodies</button>
        <CopyButton text={tableText(cols, rows)} />
      </span></header>
      {picking && <BodiesDialog bodies={bodies} onOk={setBodies} onClose={() => setPicking(false)} />}
      <Loaded q={q}>{() => (
        <div className="scroll tall"><table className="points amsa-table">
          <thead><tr>{cols.map((c) => <th key={c}>{c}</th>)}</tr></thead>
          <tbody>{rows.map((r, k) => <tr key={r[0]}>{r.map((c, i) => <td key={i} className={i === 1 || i === 2 ? "num" : i === 3 ? tone(k) : ""}>{supOrd(c)}</td>)}</tr>)}</tbody>
        </table></div>
      )}</Loaded>
    </section>
  );
}

const TABS = [{ id: "key", name: "Key Info" }, { id: "houses", name: "Bhavas" }, { id: "amsa", name: "Amsa rulers" }, { id: "kp", name: "KP" }] as const;

/** The pane on the right of the Home screen. */
export function BasicsPane() {
  const [tab, setTab] = useSaved<(typeof TABS)[number]["id"]>("basics", "key");
  const b = useBasics();
  return (
    <div className="right">
      <header className="lab-head"><SubTabs tabs={[...TABS]} value={tab} onChange={setTab} label="Home views" /></header>
      {tab === "houses" ? <Houses /> : tab === "amsa" ? <AmsaRulers /> : tab === "kp" ? <Kp /> : b.data && (
        <div className="key-layout">
          <KeyInfo b={b.data} />
          <div className="side"><CoreInfo b={b.data} /><SmallAv b={b.data} /></div>
        </div>
      )}
    </div>
  );
}
