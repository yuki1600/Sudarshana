import { ZoneInput } from "./Zone";
import { useEffect, useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api, currentSettings, saveSettings, type AspectTable, type DasaEvent, type Settings } from "./api";
import { FormButtons, Modal } from "./ChartDialogs";
import { LANGUAGES, languageOf } from "./translate";
import { PrintPicker } from "./Print";
import { SettingsScreen } from "./Settings";
import { FONT_FACTORS, useChart, type ChartStyle } from "./store";
import { CopyButton, Loaded, Retro, tableText } from "./ui";

export const DIVISIONS = [1, 9, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 16, 20, 24, 27, 30, 40, 45, 60, 81, 108, 144];
const REFS = ["Lagna", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"];
export const STARS = ["Aswini", "Bharani", "Krittika", "Rohini", "Mrigasira", "Ardra", "Punarvasu", "Pushyami", "Asresha", "Magha", "Poorva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swaati", "Visaakha", "Anooradha", "Jyeshtha", "Moola", "Poorvashadha", "Uttarashadha", "Sravanam", "Dhanishtha", "Satabhisham", "Poorvabhadra", "Uttarabhadra", "Revati"];
const CLASS_COLOUR = ["own", "rel1", "rel2", "rel3", "rel4", "rel5"];
const CLASS_WORDS = ["Own sign", "Good friend's", "Friend's", "Neutral", "Enemy's", "Bad enemy's"];     // the legend's words: whose sign a planet is in

export function DivisionSelect({ value, onChange, label = "Divisional chart", list = DIVISIONS }: { value: number; onChange: (d: number) => void; label?: string; list?: number[] }) {
  return <select aria-label={label} value={value} onChange={(e) => onChange(Number(e.target.value))}>{list.map((d) => <option key={d} value={d}>{d === 1 ? "Rasi (D-1)" : `D-${d}`}</option>)}</select>;
}

/** Aspect Table with Relationships. */
function AspectWindow({ division, onClose }: { division?: number; onClose: () => void }) {
  return <Modal title="Aspect Table with Relationships" onClose={onClose} wide><AspectTableView division={division} /></Modal>;
}

type AspectRow = AspectTable["rows"][number];
/** An aspect table's cells: the aspecting graha (its relation's colour, its marks) and its values on the grahas and on the houses;
 *  ``split`` as Starlight draws them (marks as symbols and words, the cells shaded by their share of a full aspect). */
function aspectCells(t: AspectTable, split: boolean) {
  // in its own sign, moolatrikona or exalted says it all (BPHS: by degree, only one of the three)
  const dignified = (r: AspectRow) => t.names.indexOf(r.relation) === 0 && r.marks.some((m) => m === "moolatrikona" || m === "exalted");
  const who = (r: AspectRow) => split ? (     // exalted, debilitated and combust as symbols on the name; whose sign and moolatrikona in words
    <td><span className={CLASS_COLOUR[t.names.indexOf(r.relation)]}>{r.body}{r.retro && <Retro />}</span>
      {r.marks.includes("exalted") && <span className="mark" title="Exalted">↑</span>}
      {r.marks.includes("debilitated") && <span className="mark low" title="Debilitated">↓</span>}
      {r.combust && <span className="mark dot" title="Combust">●</span>}
      <span className="aspect-notes">{[...(dignified(r) ? [] : [CLASS_WORDS[t.names.indexOf(r.relation)]]), ...r.marks.filter((m) => m === "moolatrikona")].join(" · ").replace(/^./, (c) => c.toUpperCase())}</span></td>
  ) : (
    <td title={r.relation}><span className={CLASS_COLOUR[t.names.indexOf(r.relation)]}>{r.body}</span>{r.marks.map((m) => <span key={m} className="mark" title={m}>{m === "exalted" ? "▲" : m === "debilitated" ? "▼" : "●"}</span>)}{r.combust && <span className="mark combust" title="Combust">☼</span>}</td>
  );
  // Starlight's heatmap: the cell shaded by its share of a full aspect; capped at 45% so the relation colours stay readable
  const heat = (v: number) => split && v > 0 ? { background: `color-mix(in srgb, var(--accent) ${Math.round(45 * Math.min(1, v / t.full))}%, transparent)` } : undefined;
  const onGrahas = (r: AspectRow) => r.cells.map((c, i) => <td key={`g${i}`} className="num" style={heat(c ?? 0)}>{c ?? (split ? 0 : "")}</td>)     /* a graha on itself: 0 in Starlight, blank in the Windows layout */;
  const onHouses = (r: AspectRow) => r.houses.map((h, i) => <td key={`h${i}`} className={`num ${CLASS_COLOUR[r.lord_class[i]]}`} style={heat(h)}>{h}</td>);
  return { who, onGrahas, onHouses };
}

/** Starlight's Aspects tab, one half: the aspecting grahas on the grahas (``part`` 0) or on the houses (1), then the benefics'
 *  and malefics' totals on each; ``head`` and ``total`` name the two sides (Matching: "Girl's aspects", "Total on boy's"). */
export function AspectGrid({ t, part, next, head = "Aspecting graha", total = "Total aspect on" }: { t: AspectTable; part: 0 | 1; next?: boolean; head?: string; total?: string }) {
  const { who, onGrahas, onHouses } = aspectCells(t, true);
  const cols = part ? t.houses : t.bodies;
  return (
    <>
      <table className={`points aspect-table${next ? " aspect-next" : ""}`}>
        <thead><tr><th>{head}</th>{cols.map((c) => <th key={c}>{c}</th>)}</tr></thead>
        <tbody>{t.rows.map((r) => <tr key={r.body}>{who(r)}{part ? onHouses(r) : onGrahas(r)}</tr>)}</tbody>
      </table>
      <table className="points aspect-table aspect-next">
        <thead><tr><th>{total}</th>{cols.map((c) => <th key={c}>{c}</th>)}</tr></thead>
        <tbody>{[true, false].map((good) => (
          <tr key={String(good)}><td className={good ? "good-text" : "bad-text"}>{good ? "Benefics" : "Malefics"}</td>
            {cols.map((c, i) => <td key={c} className="num">{t.rows.filter((r) => r.benefic === good).reduce((x, r) => x + ((part ? r.houses[i] : r.cells[i]) ?? 0), 0)}</td>)}</tr>
        ))}</tbody>
      </table>
    </>
  );
}

/** The aspect table with relationships: the window's body, and Starlight's Aspects tab (``split``: the grahas' table, then the house cusps' below it). */
export function AspectTableView({ division: first, split }: { division?: number; split?: boolean }) {
  const birth = useChart((s) => s.birth)!;
  const client = useQueryClient();
  const [division, setDivision] = useState(first ?? 1);
  const [ref, setRef] = useState(0);
  const [version, setVersion] = useState(0);
  const q = useQuery({ queryKey: ["aspectTable", birth, division, ref, version], queryFn: () => api.aspectTable(birth, division, ref) });
  const set = (k: string, v: number | boolean) => { saveSettings({ ...currentSettings(), [k]: v }); client.invalidateQueries(); setVersion(version + 1); };
  const s = currentSettings();
  const text = q.data ? tableText(["Aspecting graha", ...q.data.bodies, ...q.data.houses], q.data.rows.map((r) => [r.body, ...r.cells.map((c) => (c === null ? "" : String(c))), ...r.houses.map(String)])) : "";
  return (
    <>
      <div className={`row bottom-gap ${split ? "one-line" : "wrap"}`}>
        <DivisionSelect value={division} onChange={setDivision} label="Chart used" />
        <label className="row">{!split && "Bhavas from"}<select title="Bhavas from" value={ref} onChange={(e) => setRef(Number(e.target.value))}>{REFS.map((n, i) => <option key={n} value={i}>{n}</option>)}</select></label>
        <label className="row">{split ? "Value" : "Full aspect value"}<select value={Number(s.aspect_full ?? 100)} onChange={(e) => set("aspect_full", Number(e.target.value))}><option>60</option><option>100</option></select></label>
        <label className="row">{split ? "Aspects of Ma, Ju & Sa" : "Aspects of Mars, Jupiter and Saturn"}<select value={String(s.aspect_parasara !== false)} onChange={(e) => set("aspect_parasara", e.target.value === "true")}><option value="true">{split ? "Parasara's teachings" : "As per Parasara's teachings"}</option><option value="false">{split ? "Dr Raman's teachings" : "As per Dr Raman's teachings"}</option></select></label>
        <CopyButton text={text} />
      </div>
      <Loaded q={q}>{(t) => {
        const { who, onGrahas, onHouses } = aspectCells(t, !!split);
        return (
        <div className="scroll">
          {split ? (
            <>
              <AspectGrid t={t} part={0} />
              <AspectGrid t={t} part={1} next />
            </>
          ) : (
          <table className="points aspect-table">
            <thead><tr><th>Aspecting graha</th>{t.bodies.map((b) => <th key={b}>{b}</th>)}{t.houses.map((h) => <th key={h}>{h}</th>)}</tr></thead>
            <tbody>{t.rows.map((r) => <tr key={r.body}>{who(r)}{onGrahas(r)}{onHouses(r)}</tr>)}</tbody>
          </table>
          )}
          {!split && <><p className="muted hint">Chart used: {t.title}. Full aspect value: {t.full}. Bhavas from {t.reference}. A graha's colour is its relation to the lord of its sign; a bhava's value, its relation to that bhava's lord.</p>
          <p className="legend"><span className="own">Own sign</span> <span className="rel1">Good friend's</span> <span className="rel2">Friend's</span> <span className="rel3">Neutral</span> <span className="rel4">Enemy's</span> <span className="rel5">Bad enemy's</span> ▲ exalted ▼ debilitated ● moolatrikona ☼ combust</p></>}
        </div>
        );
      }}</Loaded>
    </>
  );
}

/** Horoscope Matching Score. */
function MatchingWindow({ onClose }: { onClose: () => void }) {
  const birth = useChart((s) => s.birth)!;
  const [bride, setBride] = useState(true);
  const [nak, setNak] = useState(0);
  const [pada, setPada] = useState(0);
  const q = useQuery({ queryKey: ["matching", birth, bride, nak, pada], queryFn: () => api.matching(birth, bride, nak, pada) });
  const text = q.data ? tableText(["Nakshatra", "Pada", "Score", "Level"], q.data.rows.map((r) => [r.nakshatra, String(r.pada), String(r.score), r.level])) : "";
  return (
    <Modal title="Horoscope Matching for Marriage" onClose={onClose} wide>
      <div className="row bottom-gap wrap">
        <label className="row">Consider a<select value={String(bride)} onChange={(e) => setBride(e.target.value === "true")}><option value="true">Bride</option><option value="false">Bridegroom</option></select></label>
        <label className="row">with the following nakshatra<select value={nak} onChange={(e) => setNak(Number(e.target.value))}>{STARS.map((n, i) => <option key={n} value={i}>{n}</option>)}</select></label>
        <label className="row">and pada (quarter)<select value={pada} onChange={(e) => setPada(Number(e.target.value))}>{["First", "Second", "Third", "Fourth"].map((n, i) => <option key={n} value={i}>{n}</option>)}</select></label>
        <CopyButton text={text} />
      </div>
      <Loaded q={q}>{(m) => (
        <>
          <p className="match-score"><strong>{m.score}</strong> of 36: <strong>{m.level}</strong> <span className="muted">(the native's Moon: {m.native})</span></p>
          <div className="scroll tall"><table className="points">
            <thead><tr><th>{m.partner}'s nakshatra</th><th>Pada</th><th>Score</th><th>Level</th></tr></thead>
            <tbody>{m.rows.map((r, i) => <tr key={i} className={i === nak * 4 + pada ? "picked" : ""}><td>{r.nakshatra}</td><td className="num">{r.pada}</td><td className="num">{r.score}</td><td>{r.level}</td></tr>)}</tbody>
          </table></div>
        </>
      )}</Loaded>
    </Modal>
  );
}

/** Vimsottari seed comparison. */
function SeedsWindow({ onClose }: { onClose: () => void }) {
  const { birth, go } = useChart();
  const client = useQueryClient();
  const [pada, setPada] = useState(false);
  const q = useQuery({ queryKey: ["seeds", birth, pada], queryFn: () => api.seeds(birth!, pada) });
  const accept = (index: number) => {
    saveSettings({ ...currentSettings(), dasa_seed: index });
    client.invalidateQueries();
    go("Dasas", ["dasaGroup", "nakshatra"]);
    onClose();
  };
  return (
    <Modal title="Vimsottari Seed Bala Comparison" onClose={onClose} wide>
      <label>Bhavas from a seed
        <select value={String(pada)} onChange={(e) => setPada(e.target.value === "true")}><option value="false">Sign containing the nakshatra pada is the first bhava</option><option value="true">Pada and 4 padas on either side form the first bhava</option></select>
      </label>
      <Loaded q={q}>{(rows) => (
        <div className="scroll"><table className="points wrap">
          <thead><tr><th>Seed</th><th>Star</th><th>Grahas in quadrants from it</th><th>Count</th><th /></tr></thead>
          <tbody>{rows.map((r) => <tr key={r.seed}><td>{r.seed}</td><td>{r.star}</td><td>{r.planets.join(", ") || "-"}</td><td className="num">{r.count}</td><td><button onClick={() => accept(r.index)}>Accept this seed and cast Vimsottari dasa</button></td></tr>)}</tbody>
        </table></div>
      )}</Loaded>
    </Modal>
  );
}

/** Dasa-Transit Correlation. */
function TransitCorrelationWindow({ dasa, path, onClose }: { dasa: string; path: number[]; onClose: () => void }) {
  const { birth, natal, mode } = useChart();
  const event: DasaEvent | undefined = mode?.event;
  const chart = birth!;
  const q = useQuery({ queryKey: ["dasaTransit", chart, dasa, path, event], queryFn: () => api.dasaTransit(chart, dasa, path, event, natal!) });
  const text = q.data ? q.data.rows.flatMap((r) => [`Transits in ${r.house} during ${q.data!.title}:`, "", ...Object.entries(r.cells).flatMap(([p, spans]) => [`  ${p}`, ...(spans.length ? spans : ["None"]).map((s) => `    ${s}`), ""])]).join("\n") : "";
  return (
    <Modal title="Dasa-Transit Correlation" onClose={onClose} wide>
      <div className="row bottom-gap"><CopyButton text={text} /></div>
      <Loaded q={q}>{(t) => (
        <div className="scroll tall">
          {t.rows.map((r) => (
            <section key={r.house} className="day">
              <h3>Transits in {r.house} during {t.title}</h3>
              <div className="transit-spans">{Object.entries(r.cells).map(([p, spans]) => <div key={p}><strong>{p}</strong>{spans.length ? spans.map((s) => <div key={s} className="muted">{s}</div>) : <div className="muted">None</div>}</div>)}</div>
            </section>
          ))}
        </div>
      )}</Loaded>
    </Modal>
  );
}

function About({ onClose }: { onClose: () => void }) {
  return (
    <Modal title="About" onClose={onClose}>
      <p><strong>Sudarshana</strong>: Vedic astrology charts and calculations, on the Swiss Ephemeris.</p>
    </Modal>
  );
}

function Notes({ onClose }: { onClose: () => void }) {
  const { name, notes, setNotes } = useChart();
  const [text, setText] = useState(notes[name] ?? "");
  return (
    <Modal title={`Chart notes: ${name || "this chart"}`} onClose={onClose} wide>
      <form method="dialog" onSubmit={(e) => { e.preventDefault(); setNotes(name, text); onClose(); }}>
        <textarea aria-label="Chart notes" rows={14} value={text} onChange={(e) => setText(e.target.value)} />
        <p className="muted hint">Kept in this browser, under the chart's name.</p>
        <FormButtons ok="Save" />
      </form>
    </Modal>
  );
}

function Timezone({ onClose }: { onClose: () => void }) {
  const { natal, birthZone, setBirthZone, changeBirth } = useChart();
  const [use, setUse] = useState(birthZone !== null);
  const [zone, setZone] = useState(natal?.tz_east_hours ?? 0);
  const convert = useMutation({ mutationFn: (z: number) => api.timezone(natal!, z), onSuccess: (r, z) => {
    const original = birthZone ?? natal!.tz_east_hours;
    changeBirth(r.birth);
    setBirthZone(z === original ? null : original);
    onClose();
  } });
  return (
    <Modal title="Enter the time zone to be used" onClose={onClose}>
      <p className="muted">If the native lives away from the birthplace, you may want the timezone of the place of residence when displaying dates and times in dasas, TP charts etc. The birthdata is not changed: the birthtime is converted to another timezone, and all calculations come out the same.</p>
      <form method="dialog" onSubmit={(e) => { e.preventDefault(); convert.mutate(use ? zone : birthZone ?? natal!.tz_east_hours); }}>
        <label>Calculation display timezone
          <select value={String(use)} onChange={(e) => setUse(e.target.value === "true")}><option value="false">Use the timezone of birth</option><option value="true">Use the timezone entered below</option></select>
        </label>
        <ZoneInput value={String(zone)} onChange={(z) => setZone(Number(z))} disabled={!use} at={natal && { y: natal.year, mo: natal.month, d: natal.day, hour: natal.hour_local }} />
        {convert.error && <p role="alert" className="error">{convert.error.message}</p>}
        <FormButtons />
      </form>
    </Modal>
  );
}

function IniView({ onClose }: { onClose: () => void }) {
  const q = useQuery({ queryKey: ["iniText", currentSettings()], queryFn: api.iniExport });
  return (
    <Modal title="Preferences file" onClose={onClose} wide>
      <Loaded q={q}>{(r) => <div className="scroll tall"><pre className="help-text">{r.content}</pre></div>}</Loaded>
      <menu>{q.data && <CopyButton text={q.data.content} />}</menu>
    </Modal>
  );
}

function Address({ onClose }: { onClose: () => void }) {
  const { display, setDisplay } = useChart();
  const [t, setT] = useState(display.address);
  return (
    <Modal title="Astrologer's name and address (for printouts)" onClose={onClose}>
      <form method="dialog" onSubmit={(e) => { e.preventDefault(); setDisplay({ address: t }); onClose(); }}>
        <textarea aria-label="Name and address" rows={4} value={t} onChange={(e) => setT(e.target.value)} />
        <FormButtons />
      </form>
    </Modal>
  );
}

export const SIZES = ["70%", "80%", "90%", "100%", "115%", "125%", "135%", "150%"];

function Fonts({ onClose }: { onClose: () => void }) {
  const { display, setDisplay } = useChart();
  const pick = (k: "listFont" | "chartFont", label: string) => <label>{label}<select value={display[k]} onChange={(e) => setDisplay({ [k]: Number(e.target.value) })}>{SIZES.map((n, i) => <option key={n} value={i}>{n}</option>)}</select></label>;
  return (
    <Modal title="Size of the fonts used" onClose={onClose}>
      {pick("listFont", "Lists and text")}{pick("chartFont", "Charts")}
    </Modal>
  );
}

function ChartStyleWindow({ onClose }: { onClose: () => void }) {
  const { chartStyle, setChartStyle, display, setDisplay } = useChart();
  const styles: [ChartStyle, string][] = [["south", "South Indian"], ["north", "North Indian"], ["east", "East Indian"]];
  const opts = styles.map(([v, t]) => <option key={v} value={v}>{t}</option>);
  return (
    <Modal title="Chart style and language" onClose={onClose}>
      <label>Chart style<select value={chartStyle} onChange={(e) => setChartStyle(e.target.value as ChartStyle)}>{opts}</select></label>
      <label className="check"><input type="checkbox" checked={display.twoStyles} onChange={(e) => setDisplay({ twoStyles: e.target.checked })} /> Use two chart styles: alternate panels in the second style</label>
      <label>Second chart style<select value={display.style2} disabled={!display.twoStyles} onChange={(e) => setDisplay({ style2: e.target.value as ChartStyle })}>{opts}</select></label>
      <label>Language<select translate="no" value={languageOf(display.language)} onChange={(e) => setDisplay({ language: e.target.value })}>{LANGUAGES.map((l) => <option key={l.id} value={l.id}>{l.native === l.id ? l.id : `${l.native} (${l.id})`}</option>)}</select></label>
      <label>Graha names<select value={display.planets} onChange={(e) => setDisplay({ planets: e.target.value as "english" | "sanskrit" })}><option value="english">English</option><option value="sanskrit">Sanskrit</option></select></label>
      <label>Sign names<select value={display.signs} onChange={(e) => setDisplay({ signs: e.target.value as "english" | "sanskrit" })}><option value="english">English</option><option value="sanskrit">Sanskrit</option></select></label>
      <p className="muted hint">The whole app's language, as Settings, Language has it: in another language the charts name the grahas and signs in it, and the Sanskrit names here are for English.</p>
    </Modal>
  );
}

/** Colors to be used: the groups and items. */
function Colors({ onClose }: { onClose: () => void }) {
  const q = useQuery({ queryKey: ["colors"], queryFn: api.colors, staleTime: Infinity });
  const { display, setDisplay } = useChart();
  const [group, setGroup] = useState("Chart frames");
  const all = q.data?.colours ?? [];
  const groups = Array.from(new Set(all.map((c) => c.group)));
  const set = (key: string, v: string | null) => {
    const { [key]: _, ...rest } = display.colors;
    setDisplay({ colors: v ? { ...rest, [key]: v } : rest });
  };
  return (
    <Modal title="Choose colors" onClose={onClose} wide>
      <div className="row bottom-gap wrap">
        <label className="row">Frame<select value={group} onChange={(e) => setGroup(e.target.value)}>{groups.map((g) => <option key={g}>{g}</option>)}</select></label>
        <button onClick={() => setDisplay({ colors: Object.fromEntries(all.map((c) => [c.key, c.default_rgb])) })}>Use the preset colors</button>
        <button onClick={() => setDisplay({ colors: {} })} disabled={!Object.keys(display.colors).length}>Back to this app's theme</button>
      </div>
      <div className="scroll tall colors">
        {all.filter((c) => c.group === group).map((c) => (
          <label key={c.key} className="color-row">
            <input type="color" aria-label={c.label} value={display.colors[c.key] ?? c.default_rgb} onChange={(e) => set(c.key, e.target.value)} />
            <span>{c.label}</span>
            {display.colors[c.key] && <button type="button" onClick={() => set(c.key, null)}>Reset</button>}
          </label>
        ))}
      </div>
    </Modal>
  );
}

function CopyAll({ complete, onClose }: { complete: boolean; onClose: () => void }) {
  const { birth, name, mode, meta } = useChart();
  const place = [meta.city, meta.state, meta.country].filter(Boolean).join(", ");
  const q = useQuery({ queryKey: ["report", birth, name, complete, mode?.title, place], queryFn: () => api.report(birth!, name, mode?.title ?? "Natal Chart", complete, place) });
  return (
    <Modal title={complete ? "Copy complete calculations" : "Copy basic calculations"} onClose={onClose} wide>
      <Loaded q={q}>{(r) => <div className="scroll tall"><pre className="help-text mono">{r.text}</pre></div>}</Loaded>
      <menu>{q.data && <CopyButton text={q.data.text} />}</menu>
    </Modal>
  );
}


/** The window off the tree that is open, or a message box. */
function SettingsWindow({ group, onClose }: { group?: string; onClose: () => void }) {
  return <SettingsScreen open group={group ?? ""} onClose={onClose} />;
}

export function Windows() {
  const { window: w, openWindow } = useChart();
  const close = () => openWindow(null);
  if (!w) return null;
  switch (w.kind) {
    case "aspects": return <AspectWindow division={w.division} onClose={close} />;
    case "matching": return <MatchingWindow onClose={close} />;
    case "seeds": return <SeedsWindow onClose={close} />;
    case "transit_correlation": return <TransitCorrelationWindow dasa={w.key} path={w.path} onClose={close} />;
    case "about": return <About onClose={close} />;
    case "notes": return <Notes onClose={close} />;
    case "timezone": return <Timezone onClose={close} />;
    case "ini": return <IniView onClose={close} />;
    case "pages": return <PrintPicker onClose={close} />;
    case "address": return <Address onClose={close} />;
    case "fonts": return <Fonts onClose={close} />;
    case "style": return <ChartStyleWindow onClose={close} />;
    case "colors": return <Colors onClose={close} />;
    case "copy_all": return <CopyAll complete={w.complete} onClose={close} />;
    case "settings": return <SettingsWindow group={w.group} onClose={close} />;
    case "message": return <Modal title={w.title} onClose={close}><pre className="message">{w.text}</pre><menu><button onClick={close}>OK</button></menu></Modal>;
    default: return null;
  }
}

/** Save a text file through the browser. */
export function download(name: string, content: string) {
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([content], { type: "text/plain" }));
  a.download = name;
  a.click();
  URL.revokeObjectURL(a.href);
}

/** The chosen colours as CSS variables on the page; the theme fills in the others. */
export function useDisplayStyles() {
  const display = useChart((s) => s.display);
  const applied = useRef<string[]>([]);
  useEffect(() => {
    const el = document.documentElement;
    const name = (k: string) => `--c-${k.replace(/^Color/, "")}`;     // the ini's keys start with Color
    applied.current.forEach((k) => el.style.removeProperty(name(k)));
    Object.entries(display.colors).forEach(([k, v]) => el.style.setProperty(name(k), v));
    applied.current = Object.keys(display.colors);
    el.style.setProperty("--list-scale", String(FONT_FACTORS[display.listFont]));
    el.style.setProperty("--chart-scale", String(FONT_FACTORS[display.chartFont]));
    if (display.split) el.style.setProperty("--split", `${display.split}px`); else el.style.removeProperty("--split");
    el.toggleAttribute("data-bw", display.blackAndWhite);
    el.dataset.layout = display.layout;
    el.dataset.brand = display.brand;     // styles/praajna.css, Starlight only     // the Windows layout keeps the 16px root (styles/base.css)
  }, [display]);
}

export type { Settings };
