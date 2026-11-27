import { useEffect, useLayoutEffect, useMemo, useRef, useState, type ReactNode } from "react";
import { useQueries, useQuery } from "@tanstack/react-query";
import { api } from "./api";
import { Icon } from "./Icons";
import { useKept, useSaved } from "./hooks";
import { useMenu, type MenuEntry } from "./Menu";
import { MixedChart } from "./Mixed";
import {
  applyFilter, cellMatches, countBy, DATASETS, deathsOf, foundingOf, indicesOf, kindOf, magnitudeOf, NO_FILTER, titleOf, toBirth, yearOf,
  type DatasetName, type Filter, type MRecord, type MSummary, type Tagged,
} from "./mundaneMath";
import { useChart } from "./store";
import { SubTabs } from "./ui";

const VIEWS = [{ id: "overview", name: "Overview" }, { id: "disasters", name: "Disasters" }, { id: "elections", name: "Elections" }, { id: "nations", name: "Nations" }, { id: "sports", name: "Sports" }, { id: "events", name: "Events" }, { id: "finance", name: "Finance" }] as const;
type View = typeof VIEWS[number]["id"];
const PAGE = 300;
const ABOUT: Record<DatasetName, string> = {
  disasters: "Earthquakes and tsunamis from NOAA's catalogues, 1900 on, at the instrument-timed moment of the shock, with the Rodden AA and A charts of eruptions, crashes, fires and other disasters.",
  elections: "Presidents and prime ministers at the minute their oath was recorded.",
  nations: "Founding and constitutional charts timed to the minute, some from the Rodden library.",
  sports: "Finals and deciding games at their recorded start.",
  events: "The Rodden AA and A charts of other events: TV shows, space flights, attacks, UFO sightings, foundings, celestial events and more.",
  finance: "The world's listed companies by market value, at their first trading day, timed at the exchange's opening bell, with the startups valued at a billion dollars or more and the largest unlisted companies, at their founding.",
};

/** One date order across the sets: year, month, day, then the hour (an untimed day sorts at noon); a company with no date sorts last. */
const when = (r: MRecord) => (!r.date ? Infinity
  : yearOf(r) * 1e4 + Number(r.date.slice(-5, -3)) * 100 + Number(r.date.slice(-2)) + (r.time ? Number(r.time.slice(0, 2)) / 100 : 0.12));

/** The databases a tab needs, each record tagged with its set: one is fetched the first time a tab asks for it, then kept. */
function useRecords(sets: DatasetName[]) {
  const qs = useQueries({ queries: sets.map((id) => ({ queryKey: ["mundane", id], queryFn: () => api.mundaneData(id), staleTime: Infinity })) });
  const ready = qs.every((q) => q.data);
  const records = useMemo<Tagged[]>(() => {
    if (!ready) return [];
    return qs.flatMap((q) => q.data!.records.map((r) => ({ ...r, set: q.data!.name }))).sort((a, b) => when(a) - when(b));
  }, [ready, sets.join()]); // eslint-disable-line react-hooks/exhaustive-deps
  const error = qs.find((q) => q.error)?.error as Error | undefined;
  return { records, ready, error };
}

/** What a database's tab loads with it: Nations its swearing-ins and disasters (its card lists them), every other set the nation
 * charts its card compares with. */
const needs = (set: DatasetName): DatasetName[] => (set === "nations" ? ["nations", "elections", "disasters"] : [set, "nations"]);

const fmtDate = (r: MRecord) => {
  if (!r.date) return "—";
  const y = yearOf(r);
  return `${y < 0 ? `${-y} BCE` : String(y)}-${r.date.slice(-5)}`;
};
/** A name short enough for the middle of a mixed chart. */
const shortName = (r: Tagged) => (r.set === "elections" ? "Oath" : r.set === "sports" ? "Match" : r.set === "nations" ? String(r.chart_name) : r.set === "finance" ? String(r.name) : String(r.type ?? "Event"));
const fmtTime = (r: MRecord) => (!r.time ? "—" : r.tz_east === 0 ? `${r.time} UTC` : `${r.time} UTC${r.tz_east > 0 ? "+" : "−"}${Math.abs(r.tz_east)}`);
const num = (v: unknown) => (typeof v === "number" ? v.toLocaleString() : "");
/** US dollars short: $5.14 tn, $23.6 bn, $370 m. */
const money = (v: unknown) => (typeof v !== "number" || !v ? "" : v >= 1e12 ? `$${(v / 1e12).toFixed(2)} tn` : v >= 1e9 ? `$${(v / 1e9).toFixed(v >= 1e11 ? 0 : 1)} bn` : `$${Math.round(v / 1e6)} m`);
/** A company's worth: its market value, or a startup's last valuation. */
const worth = (r: Tagged) => (typeof r.market_cap === "number" ? r.market_cap : typeof r.valuation === "number" ? r.valuation : null);
const cap = (t: string) => t.charAt(0).toUpperCase() + t.slice(1);
const str = (r: Tagged, k: string) => (r[k] === undefined || r[k] === null ? "" : String(r[k]));
/** "Incumbent held", "Changed"…, or "First president" for the office's first holder. */
const outcomeOf = (r: Tagged) => (r.outcome === "first" ? `First ${str(r, "office").toLowerCase()}` : cap(str(r, "outcome").replace("_", " ")));

/** The facts worth a line in the detail card and the size column, per set. */
function facts(r: Tagged): [string, string][] {
  const s = (k: string) => (r[k] === undefined || r[k] === null || r[k] === "" ? "" : String(r[k]));
  const rows: [string, string][] = [];
  if (r.set === "disasters") rows.push(["Type", s("type")], ["Magnitude / size", s("magnitude") || s("intensity")], ["Deaths", num(r.deaths) || s("deaths_text")], ["Damage ($M)", num(r.damage_musd)], ["Depth (km)", s("depth_km")], ["Ended", s("end_date")]);
  if (r.set === "elections") {
    const cands = (r.candidates as { name?: string; party?: string; seats?: string; votes_pct?: string }[] | undefined) ?? [];
    rows.push(["Election", s("election")], ["Polling day", s("poll_date")], ["Winner", [s("winner"), s("winner_party") && `(${s("winner_party")})`].filter(Boolean).join(" ")],
      ["Before", [s("incumbent"), s("incumbent_party") && `(${s("incumbent_party")})`].filter(Boolean).join(" ")], ["Outcome", outcomeOf(r)], ["Turnout", s("turnout")],
      ...cands.slice(0, 3).map((c, i): [string, string] => [`Candidate ${i + 1}`, [c.name, c.party && `(${c.party})`, c.seats && `${c.seats} seats`, c.votes_pct].filter(Boolean).join(" ")]),
      ["Oath date from", s("oath_source")], ["Oath time from", s("oath_time_source")]);
  }
  if (r.set === "sports") rows.push(["Competition", `${s("competition")} — ${s("stage")}`], ["Teams", `${s("team_a")} v ${s("team_b")}`], ["Score", s("score")], ["Winner", s("winner") || "none (draw or replayed)"], ["Decided by", s("decided_by")], ["Result", s("result")]);
  if (r.set === "nations") rows.push(["Event", s("event")], ["Primary chart", r.primary ? "yes" : "alternate"]);
  if (r.set === "events") rows.push(["Type", s("type")]);
  if (r.set === "finance") {
    const list = (k: string) => (Array.isArray(r[k]) ? (r[k] as string[]).join(", ") : "");
    rows.push(["Status", r.status === "startup" ? `Startup (private)${r.valuation ? `, valued at ${money(r.valuation)}` : ""}` : r.status === "private" ? "Not listed: state-owned or private" : "Listed"],
      ["Revenue", r.revenue ? `${money(r.revenue)} a year (${s("revenue_from").replace("List of ", "Wikipedia: ")})` : ""],
      ["Legal name", s("legal_name") !== s("name") ? s("legal_name") : ""], ["Ticker", s("symbol")],
      ["First listing", r.listed ? `${s("listed")} on the ${s("exchange")}` : ""],
      ["Market value", r.market_cap ? `${money(r.market_cap)}, #${num(r.rank)} in the world` : ""],
      ["A unicorn since", s("unicorn_since")], ["Investors", s("investors")], ["Indices", list("indices")],
      ["Founded", r.founded ? [s("founded"), s("founded_place")].filter(Boolean).join(", ") : r.status === "startup" ? "Not available: a startup" : ""],
      ["Founders", list("founders")], ["Headquarters", [s("hq"), s("country")].filter(Boolean).join(", ")],
      ["Sector", [s("sector"), s("industry")].filter(Boolean).join(" · ")], ["Employees", num(r.employees)], ["About", s("about")]);
  }
  rows.push(["Time from", s("time_source")], ["Place", [s("place"), s("place_country") || s("country")].filter(Boolean).join(", ")], ["Notes", s("notes")]);
  return rows.filter(([, v]) => v);
}


function Badge({ c }: { c: MRecord["time_confidence"] }) {
  return <span className="mn-badge" title={c === "exact" ? "The time is recorded to the minute or second" : "The time is as reported"}>{c}</span>;
}

/** Open a record's chart among the open charts, staying on Research; going on to a tab is optional. */
function useOpen() {
  const { openChart, go } = useChart();
  return (r: Tagged, tab?: string) => {
    if (!r.date) return;   // a startup with no known founding day
    openChart(titleOf(r), toBirth(r), { city: String(r.place ?? ""), country: String(r.place_country ?? r.country ?? "") });
    if (tab) go(tab);
  };
}

/** Add a record's chart to the open charts without leaving Research or changing the chart shown. */
function useAdd() {
  const { addChart } = useChart();
  return (r: Tagged) => {
    const had = useChart.getState().openCharts.length;
    addChart(titleOf(r), toBirth(r), { city: String(r.place ?? ""), country: String(r.place_country ?? r.country ?? "") });
    useChart.setState({ notice: { text: useChart.getState().openCharts.length > had ? `Added ${titleOf(r)} to the open charts` : "Chart is already open", at: Date.now() } });
  };
}

const list = (v: unknown): string[] => (Array.isArray(v) ? v : v ? [String(v)] : []);   // filters kept before the multi-selects held one value

/** The Research tab: an overview of the event databases and a tab for each; a database's filters sit in the tab row. Nothing
 * loads until it is shown: the overview fetches only its cards' figures, a tab only its own database (and what its card uses). */
export function Research() {
  const [saved, setView] = useSaved<View>("mundaneView", "overview");
  const view = VIEWS.some((v) => v.id === saved) ? saved : "overview";   // "explore" and "patterns" were retired
  const [filters, setFilters] = useKept<Partial<Record<DatasetName, Partial<Filter>>>>("research.filters", {});
  const go = useChart((s) => s.go);
  const db = view === "overview" ? null : view;
  const data = useRecords(db ? needs(db) : []);
  const summary = useQuery({ queryKey: ["mundane-summary"], queryFn: api.mundaneSummary, staleTime: Infinity, enabled: !db });
  const filterOf = (set: DatasetName): Filter => {
    const f = filters[set] ?? {};
    return { ...NO_FILTER, text: f.text ?? "", kind: list(f.kind), country: list(f.country), competition: list(f.competition), index: list(f.index), cols: f.cols ?? {}, sets: [set] };
  };
  const setFilterOf = (set: DatasetName) => (f: Partial<Filter>) => setFilters({ ...filters, [set]: { ...filterOf(set), ...f, sets: [set] } });
  const error = db ? data.error : (summary.error as Error | null);
  return (
    <section className="pane mn">
      <header className="pane-head mn-head tab-head">
        <SubTabs tabs={[...VIEWS]} value={view} onChange={setView} label="Research views" />
        {db && data.ready && <Filters key={db} set={db} records={data.records} filter={filterOf(db)} setFilter={setFilterOf(db)} />}
      </header>
      {error ? <p role="alert" className="error banner">{error.message}</p>
        : db ? (!data.ready ? <p className="empty">Loading {VIEWS.find((v) => v.id === db)!.name}…</p>
          : <Database key={db} set={db} records={data.records} filter={filterOf(db)} setFilter={setFilterOf(db)} onBase={() => go("Mundane")} />)
          : !summary.data ? <p className="empty">Loading the databases…</p>
            : <Overview summary={summary.data} onPick={(set, f) => { setFilters({ ...filters, [set]: { ...NO_FILTER, ...f, sets: [set] } }); setView(set); }} />}
    </section>
  );
}

// --- Overview ---------------------------------------------------------------------------------------------------

/** A card per database, filling the page two by two; an odd last one spans the row. */
function Overview({ summary, onPick }: { summary: Record<DatasetName, MSummary>; onPick: (set: DatasetName, f: Partial<Filter>) => void }) {
  return (
    <div className="mn-overview">
      <div className="mn-cards">
        {DATASETS.filter((d) => summary[d.id]).map((d) => <Card key={d.id} set={d.id} name={d.name} s={summary[d.id]} onPick={(f) => onPick(d.id, f)} />)}
      </div>
    </div>
  );
}

/** Every part a way in: the button opens the tab, a kind or country opens it filtered, an event opens its chart and the tab with it
 * chosen (its chart opens only from its card's buttons). Its figures come from the server's summary, so the overview loads no database. */
function Card({ set, name, s, onPick }: { set: DatasetName; name: string; s: MSummary; onPick: (f: Partial<Filter>) => void }) {
  const [, select] = useKept<string | null>(`research.${set}.selected`, null);
  const finance = set === "finance";
  const notable = s.notable.map((r): Tagged => ({ ...r, set }));
  const label = (r: Tagged) => (set === "disasters" || set === "events" || finance ? str(r, "name") || str(r, "place") : set === "elections" ? `${str(r, "winner")}, ${str(r, "country")}`
    : set === "sports" ? `${str(r, "team_a")} v ${str(r, "team_b")}` : `${str(r, "country")}: ${str(r, "chart_name")}`);
  const meta = (r: Tagged) => (set === "disasters" ? `${num(deathsOf(r))} dead` : finance ? money(worth(r)) : fmtYear(yearOf(r)));
  return (
    <article className="mn-card">
      <header>
        <h3>{name}</h3>
        <button type="button" className="mn-card-open" onClick={() => onPick({})}>Open all →</button>
      </header>
      <p className="mn-card-about" title={ABOUT[set]}>{ABOUT[set]}</p>
      <dl className="mn-card-stats">
        <div><dt>{finance ? "Companies" : "Events"}</dt><dd>{s.count.toLocaleString()}</dd></div>
        {finance ? <>
          <div><dt>Listed</dt><dd>{(s.status?.listed ?? 0).toLocaleString()}</dd></div>
          <div><dt>Startups</dt><dd>{(s.status?.startup ?? 0).toLocaleString()}</dd></div>
        </> : <div><dt>Years</dt><dd>{s.first && s.last ? `${fmtYear(yearOf({ date: s.first }))}–${fmtYear(yearOf({ date: s.last }))}` : "—"}</dd></div>}
        <div><dt>Countries</dt><dd>{s.countries.toLocaleString()}</dd></div>
        {!finance && <div><dt>Latest</dt><dd>{s.last ? fmtDate({ date: s.last } as MRecord) : "—"}</dd></div>}
      </dl>
      <div className="mn-card-lists">
        <Top title={KIND[set]} rows={s.kinds.map(([k, n]) => [cap(k), n.toLocaleString(), () => onPick({ kind: [k] })])} />
        <Top title="Countries" rows={s.top_countries.map(([c, n]) => [c, n.toLocaleString(), () => onPick({ country: [c] })])} />
        <Top title={set === "disasters" ? "Deadliest" : finance ? "Largest" : "Latest"} rows={notable.map((r) => [label(r), meta(r), () => { select(r.id); onPick({}); }])} wide />
      </div>
    </article>
  );
}

const fmtYear = (y: number) => (y < 0 ? `${-y} BCE` : String(y));
const KIND: Record<DatasetName, string> = { disasters: "Type", elections: "Office", sports: "Sport", nations: "Event", events: "Type", finance: "Sector" };

/** A short list of rows to click: a name and a figure each. */
function Top({ title, rows, wide }: { title: string; rows: [string, string, () => void][]; wide?: boolean }) {
  return (
    <section className={wide ? "mn-top wide" : "mn-top"} aria-label={title}>
      <h4>{title}</h4>
      {rows.map(([k, n, go]) => (
        <button key={k} type="button" onClick={go} title={k}>
          <span className="mn-top-k">{k}</span><span className="mn-top-n">{n}</span>
        </button>
      ))}
    </section>
  );
}

/** A dropdown of ticks: any number of values, the menu staying open while they are picked. */
function MultiPick({ label, options, value, onChange, show = (k) => k }: { label: string; options: [string, number][]; value: string[]; onChange: (v: string[]) => void; show?: (k: string) => string }) {
  const { open, node } = useMenu();
  type At = { clientX: number; clientY: number };
  const items = (on: string[], at: At): MenuEntry[] => [
    ...(on.length ? [{ label: "Any", onClick: () => onChange([]) }, "-" as const] : []),
    ...options.map(([k, n]) => ({
      label: show(k), hint: n.toLocaleString(), checked: on.includes(k), keep: true,
      onClick: () => { const next = on.includes(k) ? on.filter((x) => x !== k) : [...on, k]; onChange(next); open(at, items(next, at), label); },
    })),
  ];
  return (
    <>
      <button type="button" className="mn-drop" aria-haspopup="menu" aria-pressed={value.length > 0}
        onClick={(e) => { const b = e.currentTarget.getBoundingClientRect(), at = { clientX: b.left, clientY: b.bottom + 4 }; open(at, items(value, at), label); }}>
        {value.length === 0 ? label : value.length === 1 ? show(value[0]) : `${label} · ${value.length}`}<span aria-hidden>▾</span>
      </button>
      {node}
    </>
  );
}

type ListKey = "kind" | "country" | "competition" | "index";

/** A database's filters, in the tab row: the chosen values as tags, the count, words, and multi-selects for kind, competition (sports), index (finance) and country. */
function Filters({ set, records, filter, setFilter }: { set: DatasetName; records: Tagged[]; filter: Filter; setFilter: (f: Partial<Filter>) => void }) {
  const mine = useMemo(() => records.filter((r) => r.set === set), [records, set]);
  const kinds = useMemo(() => countBy(mine, kindOf), [mine]);
  const countries = useMemo(() => countBy(mine.filter((r) => r.country), (r) => String(r.country)).sort((a, b) => a[0].localeCompare(b[0])), [mine]);
  const competitions = useMemo(() => countBy(mine, (r) => str(r, "competition")), [mine]);
  const indices = useMemo(() => countBy(mine.flatMap(indicesOf), (i) => i), [mine]);
  const shown = useMemo(() => tableRows(set, applyFilter(mine, filter), filter.cols).length, [set, mine, filter]);
  const tags: [ListKey, string][] = (["kind", "competition", "index", "country"] as const).flatMap((k) => filter[k].map((v): [ListKey, string] => [k, v]));
  const narrowed = shown !== mine.length;
  return (
    <div className="mn-tools" role="search" aria-label={`Filter the ${set}`}>
      {tags.map(([k, v]) => (
        <button key={k + v} type="button" className="mn-tag" title="Remove this filter" onClick={() => setFilter({ [k]: filter[k].filter((x) => x !== v) })}>
          {k === "kind" ? cap(v) : v}<span aria-hidden>×</span>
        </button>
      ))}
      <span className="mn-count">{narrowed ? `${shown.toLocaleString()} of ${mine.length.toLocaleString()}` : `${mine.length.toLocaleString()} ${set === "finance" ? "companies" : "events"}`}
        {narrowed && <button type="button" className="link" onClick={() => setFilter(NO_FILTER)}>Clear all</button>}</span>
      <input type="search" className="mn-search" aria-label="Search" value={filter.text} placeholder="Search…" onChange={(e) => setFilter({ text: e.target.value })} />
      {kinds.length > 1 && <MultiPick label={KIND[set]} options={kinds} value={filter.kind} onChange={(kind) => setFilter({ kind })} show={cap} />}
      {set === "sports" && <MultiPick label="Competition" options={competitions} value={filter.competition} onChange={(competition) => setFilter({ competition })} />}
      {indices.length > 0 && <MultiPick label="Index" options={indices} value={filter.index} onChange={(index) => setFilter({ index })} />}
      {countries.length > 1 && <MultiPick label="Country" options={countries} value={filter.country} onChange={(country) => setFilter({ country })} />}
    </div>
  );
}

// --- One database -------------------------------------------------------------------------------------------------

type Pick = { key: ListKey | "text"; value: string };
/** A column; ``pick`` makes its cells a filter: clicking one keeps only the events that share it. */
interface Col { label: string; cell: (r: Tagged) => ReactNode; sort?: (r: Tagged) => string | number; num?: boolean; pick?: (r: Tagged) => Pick | null; wide?: boolean }   // wide: hidden while the chosen event's card is open, so the table still fits
type Sort = { col: string; desc: boolean };

const DATE: Col = { label: "Date", cell: fmtDate, sort: when, num: true };
const TIME: Col = { label: "Time", cell: fmtTime, num: true };
const text = (label: string, get: (r: Tagged) => string, pick?: Col["pick"]): Col => ({ label, cell: get, sort: get, pick });
const amount = (label: string, get: (r: Tagged) => number | null, show: (r: Tagged) => string = (r) => num(get(r))): Col => ({ label, cell: show, sort: (r) => get(r) ?? -Infinity, num: true });
const byCountry = (r: Tagged): Pick | null => (r.country ? { key: "country", value: String(r.country) } : null);
const byKind = (r: Tagged): Pick => ({ key: "kind", value: kindOf(r) });

/** Each database's own columns; the first, frozen at the left, names the event. */
const COLS: Record<DatasetName, Col[]> = {
  disasters: [
    text("Event", (r) => str(r, "name") || str(r, "place")), DATE, TIME,
    text("Type", (r) => cap(str(r, "type")), byKind),
    amount("Size", magnitudeOf, (r) => (magnitudeOf(r) === null ? "" : r.type === "tsunami" ? `${magnitudeOf(r)} m` : `M ${magnitudeOf(r)}`)),
    amount("Deaths", deathsOf), amount("Depth (km)", (r) => (typeof r.depth_km === "number" ? r.depth_km : null)),
    text("Country", (r) => str(r, "country"), byCountry),
  ],
  elections: [
    text("Sworn in", (r) => str(r, "winner") || "—"), text("Country", (r) => str(r, "country"), byCountry), text("Office", (r) => str(r, "office"), byKind),
    { ...DATE, label: "Oath" }, TIME, text("Party", (r) => str(r, "winner_party")),
    text("Outcome", outcomeOf), text("Polling day", (r) => str(r, "poll_date")),
  ],
  sports: [
    text("Match", (r) => `${str(r, "team_a")} v ${str(r, "team_b")}`), DATE, { ...TIME, label: "Start" },
    text("Sport", (r) => str(r, "sport"), byKind), text("Competition", (r) => str(r, "competition"), (r) => ({ key: "competition", value: str(r, "competition") })), text("Stage", (r) => str(r, "stage")),
    text("Score", (r) => str(r, "score")), text("Winner", (r) => str(r, "winner") || "Draw", (r) => (r.winner ? { key: "text", value: str(r, "winner") } : null)),
    text("Venue", (r) => [str(r, "place"), str(r, "country")].filter(Boolean).join(", "), byCountry),
  ],
  nations: [
    text("Country", (r) => str(r, "country")), { ...text("Chart", (r) => str(r, "chart_name")), cell: (r) => <>{str(r, "chart_name")}{r.primary ? <span className="mn-badge">primary</span> : null}</> },
    text("Event", (r) => cap(str(r, "event")), byKind), DATE, TIME, text("Place", (r) => str(r, "place")),
  ],
  events: [
    text("Event", (r) => str(r, "name") || str(r, "place")), DATE, TIME, text("Type", (r) => cap(str(r, "type")), byKind),
    text("Place", (r) => str(r, "place")), text("Country", (r) => str(r, "country"), byCountry),
  ],
  finance: [
    text("Company", (r) => str(r, "name")), text("Ticker", (r) => str(r, "symbol")), { ...text("Exchange", (r) => str(r, "exchange")), wide: true },
    { label: "Listed", cell: (r) => str(r, "listed") || "—", sort: (r) => str(r, "listed") || "0", num: true },
    { ...TIME, cell: (r) => (r.chart === "listing" ? fmtTime(r) : "—"), wide: true },
    { label: "Founded", cell: (r) => str(r, "founded") || "—", sort: (r) => str(r, "founded") || "0", num: true, wide: true },
    text("Country", (r) => str(r, "country"), byCountry), text("Sector", (r) => str(r, "sector"), byKind),
    amount("Value", worth, (r) => money(worth(r))), { ...text("Status", (r) => cap(str(r, "status"))), wide: true },
  ],
};

/** A cell as text, for the column filters. */
const cellText = (c: Col, r: Tagged) => { const v = c.cell(r); return typeof v === "string" ? v : c.sort ? String(c.sort(r)) : ""; };
/** The rows the column filters keep. */
const colActive = (q: string | string[] | undefined) => (Array.isArray(q) ? q.length > 0 : !!q?.trim());
function tableRows(set: DatasetName, rows: Tagged[], cols: Filter["cols"]): Tagged[] {
  const on = COLS[set].filter((c) => colActive(cols[c.label]));
  const keep = (c: Col, r: Tagged) => { const q = cols[c.label]!, t = cellText(c, r); return Array.isArray(q) ? q.includes(t) : cellMatches(t, q); };
  return on.length ? rows.filter((r) => on.every((c) => keep(c, r))) : rows;
}

function Database({ set, records, filter, setFilter, onBase }: { set: DatasetName; records: Tagged[]; filter: Filter; setFilter: (f: Partial<Filter>) => void; onBase: () => void }) {
  const [selected, select] = useKept<string | null>(`research.${set}.selected`, null);
  const [sort, setSort] = useKept<Sort>(`research.${set}.sort`, set === "nations" ? { col: "Country", desc: false } : set === "finance" ? { col: "Value", desc: true } : { col: "Date", desc: true });
  const mine = useMemo(() => records.filter((r) => r.set === set), [records, set]);
  const base = useMemo(() => applyFilter(mine, filter), [mine, filter]);
  const shown = useMemo(() => tableRows(set, base, filter.cols), [set, base, filter.cols]);
  const current = selected ? mine.find((r) => r.id === selected) ?? null : null;
  const onlyUS = filter.country.length === 1 && filter.country[0] === "United States";
  const isOn = ({ key, value }: Pick) => (key === "text" ? filter.text === value : filter[key].includes(value));
  // a second click on a value in use lets it go
  const toggle = (p: Pick) => setFilter(p.key === "text" ? { text: isOn(p) ? "" : p.value }
    : { [p.key]: isOn(p) ? filter[p.key].filter((x) => x !== p.value) : [...filter[p.key], p.value] });
  return (
    <div className={current ? "mn-db with-side" : "mn-db"}>
      <DataTable cols={COLS[set]} rows={shown} base={base} sort={[sort, setSort]} selected={selected} onRow={(r) => select(r.id)}
        pick={{ isOn, toggle }} colFilter={[filter.cols, (cols) => setFilter({ cols })]} rowClass={set === "elections" && onlyUS ? partyRow : undefined}
        empty={mine.length ? "No event matches these filters." : "No events."} />
      {current && (
        <aside className="mn-side" aria-label="The chosen event">
          <Detail key={current.id} r={current} records={records} onClose={() => select(null)} onBase={onBase} />
        </aside>
      )}
    </div>
  );
}

/** A US swearing-in's row in its party's colour: Democrats blue, Republicans red. */
const partyRow = (r: Tagged) => ({ Democratic: "mn-dem", Republican: "mn-rep" } as Record<string, string>)[str(r, "winner_party")];

/** A table whose header row and first column stay put while it scrolls; a row click opens that event, a pickable cell filters by it. */
function DataTable({ cols, rows, base = rows, sort, selected, onRow, pick, colFilter, rowClass, empty }: {
  cols: Col[]; rows: Tagged[]; base?: Tagged[]; sort?: [Sort, (s: Sort) => void]; selected?: string | null; onRow: (r: Tagged) => void; rowClass?: (r: Tagged) => string | undefined;
  pick?: { isOn: (p: Pick) => boolean; toggle: (p: Pick) => void }; colFilter?: [Filter["cols"], (c: Filter["cols"]) => void]; empty: string;
}) {
  const [count, setCount] = useState(PAGE);
  const [by, setBy] = sort ?? [null, null];
  const sorted = useMemo(() => {
    const col = by && cols.find((c) => c.label === by.col);
    if (!col?.sort) return rows;
    const key = col.sort, k = by!.desc ? -1 : 1;
    return [...rows].sort((a, b) => { const x = key(a), y = key(b); return (x < y ? -1 : x > y ? 1 : 0) * k; });
  }, [rows, by, cols]);
  const cell = (c: Col, r: Tagged) => {
    const p = pick && c.pick?.(r);
    if (!p) return c.cell(r);
    const on = pick!.isOn(p);
    return <button type="button" className="mn-pick" aria-pressed={on} title={on ? "Show all again" : `Show only these`}
      onClick={(e) => { e.stopPropagation(); pick!.toggle(p); }}>{c.cell(r)}</button>;
  };
  const cls = (c: Col) => [c.num && "num", c.wide && "mn-wide"].filter(Boolean).join(" ") || undefined;
  const [colQ, setColQ]: [Filter["cols"], ((c: Filter["cols"]) => void) | null] = colFilter ?? [{}, null];
  const [menu, setMenu] = useState<{ col: Col; x: number; y: number } | null>(null);
  return (
    <div className="mn-table-wrap">
      <table className="mn-table">
        <thead><tr>{cols.map((c) => (
          <th key={c.label} className={cls(c)} aria-sort={by?.col === c.label ? (by.desc ? "descending" : "ascending") : undefined}>
            <button type="button" aria-haspopup="dialog" aria-expanded={menu?.col.label === c.label} className={colActive(colQ[c.label]) ? "on" : undefined}
              title={`Sort or filter by ${c.label}`}
              onClick={(e) => { const b = (e.currentTarget.closest("th") as HTMLElement).getBoundingClientRect(); setMenu(menu?.col.label === c.label ? null : { col: c, x: b.left, y: b.bottom }); }}>
              {c.label}{by?.col === c.label && <span className="mn-arrow">{by.desc ? "↓" : "↑"}</span>}
              {colActive(colQ[c.label]) && <span className="mn-funnel" aria-label="filtered">●</span>}<span className="mn-caret" aria-hidden>▾</span>
            </button>
          </th>
        ))}</tr></thead>
        <tbody>{sorted.slice(0, count).map((r) => (
          <tr key={r.id} className={rowClass?.(r)} aria-selected={r.id === selected} onClick={() => onRow(r)}>
            {cols.map((c) => <td key={c.label} className={cls(c)}>{cell(c, r)}</td>)}
          </tr>
        ))}</tbody>
      </table>
      {!rows.length && <p className="empty small">{empty}</p>}
      {menu && <ColMenu key={menu.col.label} col={menu.col} x={menu.x} y={menu.y} rows={base} close={() => setMenu(null)}
        sort={setBy && menu.col.sort ? [by?.col === menu.col.label ? by.desc : null, (desc) => setBy({ col: menu.col.label, desc })] : undefined}
        value={colQ[menu.col.label]} onChange={setColQ ? (v) => setColQ({ ...colQ, [menu.col.label]: v }) : undefined} />}
      {rows.length > count && <button type="button" className="mn-more" onClick={() => setCount(count + PAGE * 4)}>Show more ({(rows.length - count).toLocaleString()} left)</button>}
    </div>
  );
}

const LIST_MAX = 200;   // values shown at once; the search narrows the rest

/** A column's dropdown: sort either way, then tick any of its values (a search narrows the list); a number column also takes >/< in the search. */
function ColMenu({ col, x, y, rows, sort, value, onChange, close }: {
  col: Col; x: number; y: number; rows: Tagged[]; sort?: [boolean | null, (desc: boolean) => void];
  value?: string | string[]; onChange?: (v: string | string[]) => void; close: () => void;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const [at, setAt] = useState({ x, y });
  // each value once, with its count, in the column's own order: dates and sizes as numbers, the rest a to z
  const values = useMemo(() => {
    const m = new Map<string, { n: number; key: string | number }>();
    for (const r of rows) {
      const t = cellText(col, r);
      if (!t || t === "—") continue;
      const e = m.get(t);
      if (e) e.n++; else m.set(t, { n: 1, key: col.num && col.sort ? col.sort(r) : t });
    }
    return [...m].sort(([a, x], [b, y]) => (col.num ? (x.key < y.key ? -1 : x.key > y.key ? 1 : 0) : a.localeCompare(b))).map(([k, e]): [string, number] => [k, e.n]);
  }, [rows, col]);
  const ticked = Array.isArray(value) ? value : [];
  const [find, setFind] = useState(Array.isArray(value) ? "" : value ?? "");
  const compare = !!col.num && /^\s*[<>]/.test(find);   // ">1990", "<7": a range, not a value to tick
  useLayoutEffect(() => { const r = ref.current!.getBoundingClientRect(); setAt({ x: Math.max(4, Math.min(x, innerWidth - r.width - 4)), y: Math.max(4, Math.min(y, innerHeight - r.height - 4)) }); }, [x, y]);
  useEffect(() => {
    const away = (e: MouseEvent) => { if (!ref.current?.contains(e.target as Node) && !(e.target as Element).closest?.(".mn-table th")) close(); };
    const key = (e: KeyboardEvent) => { if (e.key === "Escape") close(); };
    document.addEventListener("mousedown", away); document.addEventListener("keydown", key);
    return () => { document.removeEventListener("mousedown", away); document.removeEventListener("keydown", key); };
  }, [close]);
  const words = find.trim().toLowerCase();
  const matching = compare ? [] : values.filter(([k]) => k.toLowerCase().includes(words));
  const shown = matching.slice(0, LIST_MAX);
  const tick = (k: string) => onChange?.(ticked.includes(k) ? ticked.filter((t) => t !== k) : [...ticked, k]);
  return (
    <div ref={ref} className="mn-colmenu" role="dialog" aria-label={`${col.label}: sort and filter`} style={{ left: at.x, top: at.y }}>
      {sort && (
        <div className="mn-colmenu-sort">
          <button type="button" aria-pressed={sort[0] === false} onClick={() => sort[1](false)}>↑ {col.num ? "Low to high" : "A to Z"}</button>
          <button type="button" aria-pressed={sort[0] === true} onClick={() => sort[1](true)}>↓ {col.num ? "High to low" : "Z to A"}</button>
        </div>
      )}
      {onChange && <>
        <input type="search" autoFocus value={find} aria-label={`Search ${col.label}`}
          placeholder={col.num ? `Find, or >1990, <7…` : `Find a ${col.label.toLowerCase()}…`}
          onChange={(e) => { const q = e.target.value; setFind(q); if (col.num && /^\s*[<>]/.test(q)) onChange(q); else if (!Array.isArray(value) && value) onChange([]); }} />
        {!compare && (
          <ul className="mn-colmenu-list">
            {shown.map(([k, n]) => (
              <li key={k}><label><input type="checkbox" checked={ticked.includes(k)} onChange={() => tick(k)} /><span>{k}</span><small>{n.toLocaleString()}</small></label></li>
            ))}
            {!shown.length && <li className="muted small">Nothing matches.</li>}
            {matching.length > shown.length && <li className="muted small">{(matching.length - shown.length).toLocaleString()} more: type to narrow</li>}
          </ul>
        )}
        {colActive(value) && <button type="button" className="link mn-colmenu-clear" onClick={() => { setFind(""); onChange([]); }}>Clear this filter</button>}
      </>}
    </div>
  );
}

/** One of a company's listings: [exchange, ticker, first trading day or year, source, ended]. */
type Listing = [string, string | null, string | null, string | null, string | null];

function Detail({ r, records, onClose, onBase }: { r: Tagged; records: Tagged[]; onClose: () => void; onBase: () => void }) {
  const open = useOpen(), add = useAdd();
  const goTab = useChart((s) => s.go);
  const fin = r.set === "finance";
  const founding = fin && r.chart !== "founding" ? foundingOf(r) : null;
  const listings = fin && Array.isArray(r.listings) ? (r.listings as Listing[]) : [];
  const [compare, setCompare] = useKept("mundane.detail.compare", false);
  const [against, setAgainst] = useKept<string | null>("mundane.nation.compare", null);
  const nation = r.set === "nations" ? null : records.find((n) => n.set === "nations" && n.primary && n.iso2 && n.iso2 === r.iso2) ?? null;
  const here = r.set === "nations" ? records.filter((x) => x.set !== "nations" && x.iso2 && x.iso2 === r.iso2) : [];
  const oaths = here.filter((x) => x.set === "elections").reverse();
  const deadliest = here.filter((x) => x.set === "disasters" && deathsOf(x)).sort((a, b) => deathsOf(b)! - deathsOf(a)!).slice(0, 10);
  const other = against ? here.find((x) => x.id === against) ?? null : null;
  const related = (title: string, list: Tagged[]) => list.length > 0 && (
    <section className="mn-related">
      <h4>{title} <small>{list.length}</small></h4>
      <ul>{list.map((x) => (
        <li key={x.id}><button type="button" aria-pressed={x.id === against} onClick={() => setAgainst(x.id === against ? null : x.id)} title="Show it outside this chart">
          <span>{x.set === "elections" ? `${str(x, "winner")} (${str(x, "office")})` : str(x, "name") || str(x, "place")}</span>
          <small>{fmtDate(x)}{x.set === "disasters" ? ` · ${num(x.deaths)} dead` : ""}</small>
        </button></li>
      ))}</ul>
    </section>
  );
  return (
    <article className="mn-detail">
      <header>
        <h3>{titleOf(r)}</h3>
        <button type="button" className="mn-x" aria-label="Close" onClick={onClose}>×</button>
      </header>
      <p className="mn-when">{!r.date ? (r.status === "startup" ? "Startup: founding date not available" : "No listing or founding day known")
        : <>{fin && (r.chart === "founding" ? "Founded " : "Listed ")}{fmtDate(r)} · {fmtTime(r)} <Badge c={r.time_confidence} /></>}</p>
      <div className="mn-actions">
        {r.date && <span className="cast-combo">
          <button type="button" className="primary" onClick={() => open(r, "Home")}>{fin ? (r.chart === "founding" ? "Founding chart" : "Listing chart") : "Show chart"}</button>
          <button type="button" className="mn-add" aria-label="Add chart" data-tip="Add chart to the open charts" onClick={() => add(r)}><Icon name="plus" /></button>
        </span>}
        {founding && <span className="cast-combo">
          <button type="button" onClick={() => open(founding, "Home")}>Founding chart</button>
          <button type="button" className="mn-add" aria-label="Add founding chart" data-tip="Add chart to the open charts" onClick={() => add(founding)}><Icon name="plus" /></button>
        </span>}
        {fin && !!r.yahoo && <button type="button" onClick={() => goTab("Finance", ["financeSymbol", String(r.symbol)])}>Price chart</button>}
        {r.date && <button type="button" onClick={() => open(r, "Astrocartography")}>Astrocartography</button>}
        {r.set === "nations" && <button type="button" onClick={() => { open(r); onBase(); }}>Use as base chart</button>}
      </div>
      <dl>{facts(r).map(([k, v]) => <div key={k}><dt>{k}</dt><dd>{v}</dd></div>)}</dl>
      {listings.length > 0 && (
        <section className="mn-related mn-listings">
          <h4>Listings <small>{listings.length}</small></h4>
          <ul>{listings.map(([ex, ticker, day, src, ended], i) => (
            <li key={i}>
              <span>{ex}{ticker ? ` · ${ticker}` : ""}</span>
              <small>{day ?? "first trading day not known"}{src ? ` · ${src}` : ""}{ended ? ` · until ${ended}` : ""}</small>
            </li>
          ))}</ul>
        </section>
      )}
      <p className="mn-links">
        <a href={r.source} target="_blank" rel="noreferrer">Source</a>
        {typeof r.article === "string" && <a href={r.article} target="_blank" rel="noreferrer">Article</a>}
        {typeof r.wikipedia === "string" && <a href={r.wikipedia} target="_blank" rel="noreferrer">Wikipedia</a>}
        {typeof r.listed_ref === "string" && <a href={r.listed_ref} target="_blank" rel="noreferrer">Listing source</a>}
        {typeof r.website === "string" && <a href={r.website} target="_blank" rel="noreferrer">Website</a>}
        {typeof r.rodden_source === "string" && <a href={r.rodden_source} target="_blank" rel="noreferrer">Rodden chart</a>}
      </p>
      {nation && r.date && <>
        <button type="button" className="mn-compare-btn" aria-pressed={compare} onClick={() => setCompare(!compare)}>Compare with {String(nation.country)}'s {String(nation.chart_name)} chart</button>
        {compare && <div className="mn-mixed mixed"><MixedChart outerBirth={toBirth(r)} outerName={shortName(r)} innerBirth={toBirth(nation)} innerName={String(nation.chart_name)} /></div>}
      </>}
      {r.set === "nations" && <>
        {related("Swearing-ins", oaths)}
        {related("Deadliest disasters", deadliest)}
        {other && <div className="mn-mixed mixed"><MixedChart outerBirth={toBirth(other)} outerName={shortName(other)} innerBirth={toBirth(r)} innerName={String(r.chart_name)} /></div>}
      </>}
    </article>
  );
}
