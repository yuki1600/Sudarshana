import { useEffect, useState, type ComponentType } from "react";
import { useQueries, useQuery } from "@tanstack/react-query";
import { api, currentSettings, type DasaLevel, type DasaPeriod } from "./api";
import { ChartGrid } from "./ChartGrid";
import { Modal } from "./ChartDialogs";
import { formatDuration, formatLon, SIGN_NAMES, SIGNS } from "./format";
import { useBasics, useKept, useView } from "./hooks";
import { ToneLegend } from "./Lab";
import { ABBR_NAME, ChartHighlights, MAIN_SET } from "./Panels";
import { SouthGrid } from "./SouthGrid";
import { Bars, bavTone, ROWS, savTone, Shadbala, Vimsopaka } from "./Strengths";
import { DEFAULT_PRINT, useChart } from "./store";
import { toneStyle } from "./tone";
import { Loaded, Retro, SubTabs, supOrd } from "./ui";
import { AspectTableView } from "./Windows";

/** One thing the report can show. ``bare``: the body brings its own heading (a pane of another screen). */
interface Section { id: string; label: string; hint: string; group: string; Body: ComponentType; bare?: boolean; wide?: boolean }

const ms = (iso: string) => Date.parse(iso.slice(0, 19));
const day = (iso: string) => iso.slice(0, 10);
const runs = (p: DasaPeriod, now = Date.now()) => ms(p.start) <= now && now < ms(p.end);
const grahaColour = (label: string) => `var(--g-${label.slice(0, 2)})`;
const PLANET_LABEL: Record<string, string> = { Sat: "Saturn", Merc: "Mercury", Ket: "Ketu", Ven: "Venus", Sun: "Sun", Moon: "Moon", Mars: "Mars", Rah: "Rahu", Jup: "Jupiter" };
const full = (label: string) => PLANET_LABEL[label] ?? label;

function useDasaChart() {
  const { birth, natal, mode } = useChart();
  return { chart: birth!, natal: natal!, event: mode?.event };
}

function useDasa(key: string, path: number[] = [], enabled = true) {
  const { chart, natal, event } = useDasaChart();
  return useQuery({ queryKey: ["dasa", chart, key, path, event], queryFn: () => api.dasa(chart, key, path, event, natal), enabled });
}

// ---- Person

function Identity() {
  const b = useBasics();
  return <Loaded q={b}>{(d) => <dl className="pr-core">{d.core.filter(([k]) => k !== "Altitude").map(([k, v]) => <div key={k}><dt>{k}</dt><dd>{v}</dd></div>)}</dl>}</Loaded>;
}

function Planets() {
  const b = useBasics();
  return <Loaded q={b}>{(d) => (
    <table className="points pr-table">
      <thead><tr><th>Body</th><th>Longitude</th><th>Sign</th><th>Nakshatra</th><th>Navamsa</th><th>Karaka</th></tr></thead>
      <tbody>{d.points.filter((p) => (p as { group?: string }).group === "planets").map((p) => (
        <tr key={p.name}>
          <td><i className="pr-dot" style={{ background: p.name === "Lagna" ? "var(--lagna)" : grahaColour(p.name) }} /><strong>{p.name}{p.retrograde && <> <Retro /></>}</strong></td>
          <td className="num mono">{formatLon(p.lon)}</td><td>{SIGN_NAMES[p.rasi]}</td><td>{p.nakshatra} {p.pada}</td><td>{SIGN_NAMES[p.navamsa]}</td><td>{p.karaka ?? ""}</td>
        </tr>
      ))}</tbody>
    </table>
  )}</Loaded>;
}

function Highlights() {
  const birth = useChart((s) => s.birth)!;
  const q = useQuery({ queryKey: ["keyInfo", birth, 1], queryFn: () => api.keyInfo(birth, 1) });
  return <Loaded q={q}>{(rows) => <ChartHighlights rows={rows.filter((r) => MAIN_SET.has(r.name))} />}</Loaded>;
}

// ---- Charts

function Chart({ d, bhava }: { d: number; bhava?: boolean }) {
  const birth = useChart((s) => s.birth)!;
  const spec = { kind: bhava ? "bhava" : "varga", d } as const;
  const q = useQuery({ queryKey: ["panel", birth, spec, "standard", {}], queryFn: () => api.panel(birth, spec, "standard", {}) });
  const schema = useQuery({ queryKey: ["settingsSchema"], queryFn: api.settingsSchema, staleTime: Infinity, enabled: !!bhava });
  const system = schema.data?.flatMap((g) => g.options).find((o) => o.key === "house_type");
  const chosen = system?.choices?.find((c) => c.value === (currentSettings().house_type ?? system.default))?.label;
  const title = bhava ? `Bhava${chosen ? ` · ${chosen.replace(/ \(.*\)$/, "")}` : ""}` : q.data?.title ?? "";
  return q.data ? <ChartGrid title={title} lagnaSign={q.data.lagna} cell={(s) => q.data!.boxes[s] ?? []} /> : <p className="empty small">Calculating…</p>;
}

function Houses() {
  const q = useView("houses");
  return <Loaded q={q}>{(rows) => (
    <table className="points pr-table">
      <thead><tr><th>Bhava</th><th>Starts</th><th>Cusp</th><th>Ends</th><th>Occupants</th></tr></thead>
      <tbody>{rows.map((h) => <tr key={h.house}><td><strong>{h.house}</strong></td>{[h.start, h.cusp, h.end].map((x, i) => <td key={i} className="num mono">{formatLon(x)}</td>)}<td>{h.occupants.map((o) => ABBR_NAME[o] ?? o).join(", ")}</td></tr>)}</tbody>
    </table>
  )}</Loaded>;
}

const vargas = (ds: number[]) => () => <div className="pr-six">{ds.map((d) => <Chart key={d} d={d} />)}</div>;

// ---- Dasas

/** Vimsottari: the mahadasas on a line (click one for its antardasas on a second line), then every antardasa by mahadasa. */
function Vimsottari() {
  const md = useDasa("vimsottari_dasa");
  const { chart, natal, event } = useDasaChart();
  const ads = useQueries({ queries: (md.data?.periods ?? []).map((_, i) => ({ queryKey: ["dasa", chart, "vimsottari_dasa", [i], event], queryFn: () => api.dasa(chart, "vimsottari_dasa", [i], event, natal) })) });
  const running = md.data?.periods.findIndex((p) => runs(p)) ?? -1;
  const [picked, setPicked] = useState<number | null>(null);
  const open = picked ?? (running >= 0 ? running : null);
  return <Loaded q={md}>{(lvl) => (
    <>
      <div className="bands pr-bands">
        <Band lvl={lvl} tag="MD" picked={open} onPick={(i) => setPicked(i)} />
        {open !== null && ads[open]?.data && <Band lvl={ads[open].data!} tag="AD" />}
      </div>
      <p className="muted pr-note">{lvl.years}. Click a mahadasa to see its antardasas above; the running periods are marked.</p>
      <div className="pr-dasa-grid">
        {lvl.periods.map((p, i) => (
          <table key={i} className={`points pr-table pr-ad${i === open ? " picked" : ""}`}>
            <thead><tr><th colSpan={3}><i className="pr-dot" style={{ background: grahaColour(p.label) }} />{full(p.label)} <span className="muted">{day(p.start)} – {day(p.end)}</span></th></tr></thead>
            <tbody>{(ads[i]?.data?.periods ?? []).map((a, k) => (
              <tr key={k} className={runs(a) ? "running" : undefined}><td>{full(a.label)}</td><td className="num">{day(a.start)}</td><td className="num muted">{formatDuration(a)}</td></tr>
            ))}</tbody>
          </table>
        ))}
      </div>
    </>
  )}</Loaded>;
}

function Band({ lvl, tag, picked, onPick }: { lvl: DasaLevel; tag: string; picked?: number | null; onPick?: (i: number) => void }) {
  const t0 = ms(lvl.periods[0].start), span = ms(lvl.periods[lvl.periods.length - 1].end) - t0, now = (Date.now() - t0) / span;
  return (
    <div className="band">
      <span className="level-tag">{tag}</span>
      <div className="band-track" role="group" aria-label={`${tag} periods`}>
        {lvl.periods.map((p, i) => {
          const w = ((ms(p.end) - ms(p.start)) / span) * 100;
          return (
            <button key={i} type="button" className={runs(p) ? "running" : undefined} aria-pressed={picked === i} disabled={!onPick} onClick={() => onPick?.(i)}
              style={{ width: `${w}%`, boxShadow: `inset 0 -4px 0 ${grahaColour(p.label)}` }} title={`${full(p.label)}: ${day(p.start)} to ${day(p.end)}`}>{w > 6 ? p.label : ""}</button>
          );
        })}
        {now > 0 && now < 1 && <i className="band-now" style={{ left: `${now * 100}%` }} title="Today" />}
      </div>
    </div>
  );
}

/** Other dasas: each one's first level as a table. */
const dasas = (keys: string[]) => () => <div className="pr-dasa-grid">{keys.map((k) => <DasaTable key={k} k={k} />)}</div>;
function DasaTable({ k }: { k: string }) {
  const q = useDasa(k);
  return <Loaded q={q}>{(lvl) => (
    <table className="points pr-table">
      <thead><tr><th colSpan={3}>{lvl.title} <span className="muted">{lvl.level}</span></th></tr></thead>
      <tbody>{lvl.periods.map((p, i) => <tr key={i} className={runs(p) ? "running" : undefined}><td>{p.label}</td><td className="num">{day(p.start)}</td><td className="num muted">{formatDuration(p)}</td></tr>)}</tbody>
    </table>
  )}</Loaded>;
}

// ---- Strengths

function ShadbalaSection() {
  const q = useView("strengths");
  return <Loaded q={q}>{(s) => (
    <>
      <div className="pr-bars"><Bars p={{ title: "Shadbala in rupas", labels: s.shadbala.planets.map((p) => p.name.slice(0, 2)), values: s.shadbala.planets.map((p) => p.rupas), digits: 2 }} />
        <Bars p={{ title: "% of the minimum needed", labels: s.shadbala.planets.map((p) => p.name.slice(0, 2)), values: s.shadbala.planets.map((p) => p.percent), digits: 0 }} /></div>
      <Shadbala s={s.shadbala} only="graha" />
    </>
  )}</Loaded>;
}

function BhavaBala() {
  const q = useView("strengths");
  return <Loaded q={q}>{(s) => (
    <>
      <div className="pr-bars one"><Bars p={{ title: "Bhava bala in rupas", labels: s.shadbala.bhavas.map((b) => String(b.house)), values: s.shadbala.bhavas.map((b) => b.rupas), digits: 1 }} /></div>
      <Shadbala s={s.shadbala} only="bhava" />
    </>
  )}</Loaded>;
}

function Ashtakavarga() {
  const birth = useChart((s) => s.birth)!;
  const q = useQuery({ queryKey: ["ashtakavarga", birth, 1, null], queryFn: () => api.ashtakavarga(birth, 1, null) });
  return <Loaded q={q}>{(a) => (
    <>
      <div className="pr-bars one"><Bars p={{ title: "Sarvashtakavarga by sign (28 is average)", labels: SIGNS, values: a.sav, digits: 0 }} /></div>
      <div className="pr-av">
        <SouthGrid title="SAV" compact shaded={new Set(a.signs.slice(1))} cell={(s) => [String(a.sav[s])]} tone={(s) => savTone(a.sav[s])} />
        {ROWS.map((t, i) => <SouthGrid key={t} title={t} compact shaded={new Set([a.signs[i]])} cell={(s) => [String(a.bav[i][s])]} tone={(s) => bavTone(a.bav[i][s])} />)}
      </div>
      <div className="row pr-legend"><ToneLegend weak="Fewer bindus" strong="More" /><span className="muted">A shaded box holds the graha itself.</span></div>
      <table className="points pr-table">
        <thead><tr><th>Pindas</th>{ROWS.map((r) => <th key={r}>{r}</th>)}</tr></thead>
        <tbody>{["Sodhya", "Rasi", "Graha"].map((n, k) => <tr key={n}><td>{n}</td>{a.pindas.map((p, i) => <td key={i} className="num">{p[k]}</td>)}</tr>)}</tbody>
      </table>
    </>
  )}</Loaded>;
}

function VimsopakaSection() {
  const q = useView("strengths");
  return <Loaded q={q}>{(s) => <Vimsopaka rows={s.vimsopaka} titled />}</Loaded>;
}

function Yogas() {
  const birth = useChart((s) => s.birth)!;
  const q = useQuery({ queryKey: ["yogas", birth, 0, 1], queryFn: () => api.yogas(birth, 0, 1) });
  return <Loaded q={q}>{(rows) => rows.length ? (
    <ul className="pr-yogas">{rows.map((y, i) => <li key={i}><strong>{y.name}</strong> <span className="chip">{y.varga}</span><p>{supOrd(y.result)}</p><p className="muted">Formed by {y.givers_text}</p></li>)}</ul>
  ) : <p className="muted">No yogas found in the rasi chart.</p>}</Loaded>;
}

// ---- Relations

const FRIEND_KINDS = [{ id: "compound", name: "Compound" }, { id: "natural", name: "Natural" }, { id: "temporal", name: "Temporary" }] as const;
const CLASSES = ["Self", "Great friend", "Friend", "Neutral", "Enemy", "Great enemy"];
const CLASS_SHORT = ["–", "GF", "F", "N", "E", "GE"];

/** Who is friend to whom: each row is how that planet feels about the planet of the column. */
function Friendships() {
  const birth = useChart((s) => s.birth)!;
  const [kind, setKind] = useState<(typeof FRIEND_KINDS)[number]["id"]>("compound");
  const q = useQuery({ queryKey: ["table", birth, `friends_${kind}`, 1, undefined], queryFn: () => api.table(birth, `friends_${kind}`) });
  return (
    <>
      <div className="row pr-controls"><SubTabs label="Kind of relationship" tabs={[...FRIEND_KINDS]} value={kind} onChange={setKind} /><ToneLegend weak="Great enemy" strong="Great friend" /></div>
      <p className="muted pr-note pr-print-only">{FRIEND_KINDS.find((k) => k.id === kind)!.name} relationships. GF great friend, F friend, N neutral, E enemy, GE great enemy.</p>
      <Loaded q={q}>{(t) => (
        <table className="points pr-table pr-matrix">
          <thead><tr><th>Of ↓ towards →</th>{t.columns.slice(1).map((c) => <th key={c}>{c}</th>)}</tr></thead>
          <tbody>{t.rows.map(([p, ...cells]) => (
            <tr key={p}><td><strong>{p}</strong></td>{cells.map((c, i) => {
              const k = CLASSES.indexOf(c);
              return k <= 0 ? <td key={i} className="num muted">–</td> : <td key={i} className="num heat tone" style={toneStyle((5 - k) / 4)} title={`${p} → ${t.columns[i + 1]}: ${c}`}>{CLASS_SHORT[k]}</td>;
            })}</tr>
          ))}</tbody>
        </table>
      )}</Loaded>
    </>
  );
}

function Avasthas() {
  const birth = useChart((s) => s.birth)!;
  const basic = useQuery({ queryKey: ["table", birth, "avasthas", 1, undefined], queryFn: () => api.table(birth, "avasthas") });
  const sayana = useQuery({ queryKey: ["table", birth, "sayanadi", 1, undefined], queryFn: () => api.table(birth, "sayanadi") });
  return <Loaded q={basic}>{(t) => (
    <div className="pr-avasthas">{t.rows.map(([p, age, alert, mood], i) => (
      <div key={p} className="pr-avastha">
        <h4><i className="pr-dot" style={{ background: grahaColour(p) }} />{p}</h4>
        <dl>
          <div><dt>Age</dt><dd>{age}</dd></div><div><dt>Alertness</dt><dd>{alert}</dd></div><div><dt>Mood</dt><dd>{mood}</dd></div>
          {sayana.data && <div><dt>Activity</dt><dd>{sayana.data.rows[i]?.[1]}</dd></div>}
        </dl>
      </div>
    ))}</div>
  )}</Loaded>;
}

const Aspects = () => <AspectTableView split />;

// ---- The list

const GROUPS = ["Charts", "Person", "More charts", "Dasas", "Balas", "Relations"];
export const SECTIONS: Section[] = [
  { id: "identity", group: "Person", label: "Birth details & panchanga", hint: "Date, time, place, tithi, nakshatra, yoga, sunrise", Body: Identity, wide: true },
  { id: "planets", group: "Person", label: "Graha positions", hint: "Longitude, sign, nakshatra and pada, navamsa, karaka", Body: Planets, wide: true },
  { id: "highlights", group: "Person", label: "Chart highlights", hint: "Strongest and weakest, exalted, combust, vargottama", Body: Highlights, wide: true },
  { id: "rasi", group: "Charts", label: "Rasi (D-1)", hint: "The birth chart", Body: () => <Chart d={1} />, bare: true },
  { id: "bhava", group: "Charts", label: "Bhava", hint: "Bhavas in the bhava system from Preferences", Body: () => <Chart d={1} bhava />, bare: true },
  { id: "d9", group: "Charts", label: "Navamsa (D-9)", hint: "Marriage, dharma, inner bala", Body: () => <Chart d={9} />, bare: true },
  { id: "d10", group: "Charts", label: "Dasamsa (D-10)", hint: "Career and standing", Body: () => <Chart d={10} />, bare: true },
  { id: "houses", group: "More charts", label: "Bhava cusps", hint: "Where each bhava starts, peaks and ends", Body: Houses, wide: true },
  { id: "standing", group: "More charts", label: "Charts of standing", hint: "D-10, D-2, D-4, D-16, D-5, D-40", Body: vargas([10, 2, 4, 16, 5, 40]), wide: true },
  { id: "family", group: "More charts", label: "Charts of family and background", hint: "D-12, D-3, D-7, D-20, D-24, D-27", Body: vargas([12, 3, 7, 20, 24, 27]), wide: true },
  { id: "karma", group: "More charts", label: "Charts of misfortune and karma", hint: "D-6, D-8, D-11, D-30, D-45, D-60", Body: vargas([6, 8, 11, 30, 45, 60]), wide: true },
  { id: "vimsottari", group: "Dasas", label: "Vimsottari dasa", hint: "Timeline, mahadasas and every antardasa", Body: Vimsottari, wide: true },
  { id: "keydasas", group: "Dasas", label: "Moola, Ashtottari, Kalachakra", hint: "Other key nakshatra dasas", Body: dasas(["moola_dasa", "ashtottari_dasa", "kalachakra_dasa"]), wide: true },
  { id: "rasidasas", group: "Dasas", label: "Narayana dasa, Sudasa", hint: "Key rasi dasas", Body: dasas(["narayana_dasa_of_d_1_chart", "sudasa"]), wide: true },
  { id: "otherrasi", group: "Dasas", label: "Lagna kendradi, Drigdasa", hint: "Other rasi dasas", Body: dasas(["lagna_kendradi_rasi_dasa_of_d_1", "drigdasa_of_d_1"]), wide: true },
  { id: "ayur", group: "Dasas", label: "Shoola, Niryana shoola", hint: "Ayur dasas", Body: dasas(["shoola_dasa", "niryana_shoola_dasa"]), wide: true },
  { id: "yogini", group: "Dasas", label: "Yogini dasa", hint: "Eight yoginis, 36 years", Body: dasas(["yogini_dasa"]), wide: true },
  { id: "shadbala", group: "Balas", label: "Shadbala", hint: "Six-fold bala of the grahas, with graphs", Body: ShadbalaSection, wide: true, bare: true },
  { id: "bhavabala", group: "Balas", label: "Bhava bala", hint: "Bala of the twelve bhavas, with a graph", Body: BhavaBala, wide: true, bare: true },
  { id: "ashtakavarga", group: "Balas", label: "Ashtakavarga", hint: "SAV graph, every BAV, sodhya pindas", Body: Ashtakavarga, wide: true },
  { id: "vimsopaka", group: "Balas", label: "Vimsopaka bala", hint: "Out of 20 in four varga schemes", Body: VimsopakaSection, wide: true, bare: true },
  { id: "yogas", group: "Balas", label: "Yogas", hint: "Yogas found in the rasi chart", Body: Yogas, wide: true },
  { id: "aspects", group: "Relations", label: "Aspects", hint: "Graha drishti on grahas and bhava cusps", Body: Aspects, wide: true },
  { id: "friendships", group: "Relations", label: "Friendships", hint: "Natural, temporary and compound, as a matrix", Body: Friendships, wide: true },
  { id: "avasthas", group: "Relations", label: "Avasthas", hint: "Age, alertness, mood and activity of each graha", Body: Avasthas, wide: true },
];

/** The popup listing everything the report can show, opened with the report and from the Display menu. */
export function PrintPicker({ onClose }: { onClose: () => void }) {
  const { display, setDisplay } = useChart();
  const [on, setOn] = useState(() => new Set(display.printSections));
  const [bw, setBw] = useState(display.blackAndWhite);
  const [address, setAddress] = useState(display.address);
  const set = (ids: string[], yes: boolean) => setOn((cur) => { const n = new Set(cur); ids.forEach((id) => (yes ? n.add(id) : n.delete(id))); return n; });
  return (
    <Modal title="What to include in the printout" onClose={onClose} wide>
      <form method="dialog" className="pr-picker" onSubmit={(e) => { e.preventDefault(); setDisplay({ printSections: SECTIONS.filter((s) => on.has(s.id)).map((s) => s.id), blackAndWhite: bw, address }); onClose(); }}>
        <div className="pr-picker-groups">
          {GROUPS.map((g) => {
            const ids = SECTIONS.filter((s) => s.group === g).map((s) => s.id);
            return (
              <fieldset key={g}>
                <legend>{g}<span className="pr-picker-all"><button type="button" className="link" onClick={() => set(ids, true)}>All</button><button type="button" className="link" onClick={() => set(ids, false)}>None</button></span></legend>
                {SECTIONS.filter((s) => s.group === g).map((s) => (
                  <label key={s.id} className="check pr-pick"><input type="checkbox" checked={on.has(s.id)} onChange={(e) => set([s.id], e.target.checked)} /><span>{s.label}<small className="muted">{s.hint}</small></span></label>
                ))}
              </fieldset>
            );
          })}
        </div>
        <div className="pr-picker-foot">
          <label className="pr-address">Astrologer's name and address<textarea rows={2} value={address} onChange={(e) => setAddress(e.target.value)} /></label>
          <label className="check"><input type="checkbox" checked={bw} onChange={(e) => setBw(e.target.checked)} /> Black and white (no colour printer)</label>
          <span className="muted">{on.size} of {SECTIONS.length} sections</span>
          <menu><button type="button" onClick={() => setOn(new Set(DEFAULT_PRINT))}>Defaults</button><button type="button" onClick={onClose}>Cancel</button><button type="submit" className="primary" disabled={!on.size}>Show report</button></menu>
        </div>
      </form>
    </Modal>
  );
}

/** File > Print: the report of the chosen sections, opened with the list to choose them from; the browser does the printing. */
export function PrintView({ onClose }: { onClose: () => void }) {
  const { name, mode, meta, display } = useChart();
  const basics = useBasics();
  const [title, setTitle] = useState(name);
  const [picking, setPicking] = useKept("print.picking", true);
  useEffect(() => { document.documentElement.toggleAttribute("data-printing", true); return () => document.documentElement.removeAttribute("data-printing"); }, []);
  const chosen = SECTIONS.filter((s) => display.printSections.includes(s.id));
  const place = [meta.city, meta.state, meta.country].filter(Boolean).join(", ");
  const core = Object.fromEntries(basics.data?.core ?? []);
  return (
    <div className={`print-report${display.blackAndWhite ? " bw" : ""}`}>
      <div className="print-bar">
        <label className="row">Title<input value={title} onChange={(e) => setTitle(e.target.value)} /></label>
        <button onClick={() => setPicking(true)}>Sections ({chosen.length})</button>
        <span className="grow" />
        <button className="primary" onClick={() => window.print()}>Print</button>
        <button onClick={onClose}>Close</button>
      </div>
      <nav className="pr-toc" aria-label="Sections">{chosen.map((s) => <a key={s.id} href={`#pr-${s.id}`} className="chip">{s.label}</a>)}</nav>
      <article className="pr-sheet">
        <header className="pr-cover">
          <div><h1>{title || "Birth chart"}</h1><p className="pr-kind">{mode?.title ?? "Natal chart"}</p></div>
          <dl className="pr-facts">
            {["Date", "Time", "Time Zone"].map((k) => core[k] && <div key={k}><dt>{k}</dt><dd>{core[k]}</dd></div>)}
            <div><dt>Place</dt><dd>{place || core.Place}</dd></div>
          </dl>
          {display.address && !display.address.startsWith("Please enter") && <address>{display.address}</address>}
        </header>
        {GROUPS.map((g) => {
          const here = chosen.filter((s) => s.group === g);
          return here.length > 0 && (
            <section key={g} className="pr-group">
              <h2>{g}</h2>
              <div className="pr-cards">{here.map(({ id, label, Body, bare, wide }) => (
                <section key={id} id={`pr-${id}`} className={`pr-card${wide ? " wide" : ""}${bare ? " bare" : ""}`}>
                  {!bare && <h3>{label}</h3>}
                  <Body />
                </section>
              ))}</div>
            </section>
          );
        })}
        {!chosen.length && <p className="empty">Nothing chosen. Use Sections to pick what the report shows.</p>}
        <footer className="pr-foot muted">Prepared {new Date().toLocaleDateString(undefined, { day: "numeric", month: "long", year: "numeric" })}{core.Ayanamsa ? ` · Ayanamsa ${core.Ayanamsa}` : ""} · {chosen.length} sections</footer>
      </article>
      {picking && <PrintPicker onClose={() => setPicking(false)} />}
    </div>
  );
}
