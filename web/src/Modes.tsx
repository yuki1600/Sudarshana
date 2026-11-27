import { ZoneInput } from "./Zone";
import { browserZone } from "./zones";
import { useEffect, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { api, type Birth, type ModeResult, type Moment } from "./api";
import { useBasics, useKept } from "./hooks";
import { castName, Icon } from "./Icons";
import { SubTabs, supOrd } from "./ui";
import { Inspector } from "./Starlight";
import { formatLon, formatMoment } from "./format";
import { MixedChart } from "./Mixed";
import { CoreInfo, KeyInfo, SmallAv } from "./Panels";
import { useChart, type Mode } from "./store";

const BODIES = ["Lagna", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"];
const DIVISIONS = ["Rasi", "Nakshatra", "Navamsa", ...[2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 16, 20, 24, 27, 30, 40, 45, 60, 108, 144].map((n) => `D-${n}`)];
const ANGLES: [string, number][] = [["Conjunction (yuti)", 0], ["Opposition (samasaptaka)", 180], ["Trine (5th)", 120], ["Trine (9th)", 240],
  ["Quadrant (4th)", 90], ["Quadrant (10th)", 270], ["2nd", 30], ["3rd", 60], ["6th", 150], ["8th", 210], ["11th", 300], ["12th", 330]];

const pad = (n: number) => String(n).padStart(2, "0");

const clock = (now: Date) => [`${String(now.getFullYear()).padStart(4, "0")}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`,
  `${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`];

/** The date, time and zone fields of a mode's form. Until the date or time is changed by hand (or stepped), each press reads the clock to the second. */
export function useMoment(zone?: number, withZone = true, name?: string) {
  // named: a date and time set by hand are kept (leaving the tab or a refresh), until Now goes back to the clock
  const [held, hold] = useKept<string[] | null>("moment." + (name ?? "unnamed"), null);
  const start = (name && held) || clock(new Date());
  const [date, setDate] = useState(start[0]);
  const [time, setTime] = useState(start[1]);
  const [live, setLive] = useState(!(name && held));
  useEffect(() => { if (name) hold(live ? null : [date, time]); }, [date, time, live]); // eslint-disable-line react-hooks/exhaustive-deps
  // no zone given: the one last set (shared by these forms, kept over a refresh), at first this computer's own
  const own = zone === undefined;
  const local = String(-new Date().getTimezoneOffset() / 60);
  const [keptTz, setKeptTz] = useKept("moment.tz", local);
  const [keptZone, setKeptZone] = useKept<string | null>("moment.zone", browserZone());
  const [givenTz, setGivenTz] = useState(String(zone));
  const [tz, setTz] = own ? [keptTz, setKeptTz] : [givenTz, setGivenTz];
  const [named, setNamed] = useState<string | null>(null);
  const [tzName, setTzName] = own ? [keptZone, setKeptZone] : [named, setNamed];
  const fields = (
    <>
      <label>Date<input type="date" value={date} onChange={(e) => { setLive(false); setDate(e.target.value); }} required /></label>
      <label>Time<input type="time" step={1} value={time} onChange={(e) => { setLive(false); setTime(e.target.value); }} required /></label>
      {withZone && <ZoneInput value={tz} onChange={setTz} zone={tzName} onZone={setTzName} required at={(() => { const [y, mo, d] = date.split("-").map(Number); const [h, mi, s = 0] = time.split(":").map(Number); return { y, mo, d, hour: h + mi / 60 + s / 3600 }; })()} />}
    </>
  );
  const moment = (): Moment => {
    const [dNow, tNow] = live ? clock(new Date()) : [date, time];
    if (live) { setDate(dNow); setTime(tNow); }
    const [y, mo, d] = dNow.split("-").map(Number);
    const [h, mi, s = 0] = tNow.split(":").map(Number);
    return { year: y, month: mo, day: d, hour_local: h + mi / 60 + s / 3600, tz_east_hours: Number(tz) };
  };
  /** The << and >> of a form: move the fields on. */
  const shift = async (chart: Birth, seconds: number, months: number) => {
    const m = moment();
    const r = await api.step({ ...chart, ...m }, seconds, months);
    const [dd, tt] = r.start.split("T");
    setLive(false);
    setDate(dd);
    setTime(tt.slice(0, 8));
  };
  /** Put the fields at a found chart's moment, so Previous or Next steps on from it. */
  const put = (b: Moment) => {
    const sec = Math.round(b.hour_local * 3600);
    setLive(false);
    setDate(`${String(b.year).padStart(4, "0")}-${pad(b.month)}-${pad(b.day)}`);
    setTime(`${pad(Math.floor(sec / 3600) % 24)}:${pad(Math.floor(sec / 60) % 60)}:${pad(sec % 60)}`);
    setTz(String(b.tz_east_hours));
  };
  /** Back to the current time, following the clock again until a field is edited. */
  const now = () => {
    const [d, t] = clock(new Date());
    setLive(true); setDate(d); setTime(t);
    setTz(own ? local : String(zone));
    if (own) setTzName(browserZone());
  };
  return { fields, moment, shift, put, now };
}

/** A mutation that finds a derived chart and makes it the current chart. */
/** A cast chart as the chart in use: its title, span (or moment), a Tajaka year's Muntha, and how to cast it again. */
export const modeOf = (r: ModeResult): Mode => ({
  title: r.title, event: r.event, recast: r.recast,
  lines: [...(r.end ? [["From", formatMoment(r.start)], ["To", formatMoment(r.end)]] as [string, string][] : [["At", formatMoment(r.start)]] as [string, string][]),
    ...(r.muntha ? [["Muntha", formatLon(r.muntha.lon)]] as [string, string][] : [])],
});

/** After the calculation options change: the chart in use cast again with them (its search may find another moment: a Tajaka year moves
 *  with the ayanamsa), still the chart on screen; a chart of a fixed moment stays as it is, every view recalculating. Back to the natal
 *  chart only if it can no longer be cast. */
export async function recastMode() {
  const { mode, activeChartId } = useChart.getState();
  if (!mode?.recast) return;
  try {
    const r = await api.recast(mode.recast);
    const s = useChart.getState();
    if (s.activeChartId === activeChartId && s.mode === mode) s.enterMode(r.birth, modeOf(r));     // not if another chart or cast came meanwhile
  } catch { useChart.getState().backToNatal(); }
}

export function useFind<A>(find: (a: A) => Promise<ModeResult>, found?: (r: ModeResult) => void) {
  const enterMode = useChart((s) => s.enterMode);
  return useMutation({
    mutationFn: find,
    onSuccess: (r) => {
      found?.(r);
      enterMode(r.birth, modeOf(r));
    },
  });
}

/** What the form's search says: its error, the chart it found, and the reminder that it stays until Back to Natal Chart. */
export function ModeFacts({ error, empty }: { error?: Error | null; empty?: string }) {
  const mode = useChart((s) => s.mode);
  return (
    <div className="mode-result">
      {error && <p role="alert" className="error banner">{error.message}</p>}
      {mode ? (
        <>
          <p className="mode-title"><span className="live-dot" aria-hidden="true" />{mode.title}</p>
          {mode.lines.length > 0 && <dl className="mode-stats">{mode.lines.map(([k, v]) => <div key={k}><dt>{k}</dt><dd>{v}</dd></div>)}</dl>}
        </>
      ) : <p className="muted">{empty ?? "No chart found yet. The chart a search finds replaces the natal chart on every tab until you go back."}</p>}
    </div>
  );
}

/** The card beside a finder's form: the chart in use, the way back, and where to look at it. */
export function ModeCard({ error, empty, children }: { error?: Error | null; empty: string; children?: React.ReactNode }) {
  const star = useChart((s) => s.display.layout === "starlight");     // Starlight: no heading; the top bar's natal icon goes back
  return (
    <section className="pane finder-result">
      {!star && <header className="pane-head"><h2>Chart in use</h2><BackToNatal /></header>}
      <ModeFacts error={error} empty={empty} />
      {children}
    </section>
  );
}

export function BackToNatal() {
  const { mode, backToNatal } = useChart();
  return <button type="button" onClick={backToNatal} disabled={!mode}>Back to Natal Chart</button>;
}

/** The Key Info, Core Info and small ashtakavarga of the current chart, under every mode form. */
export function ChartPanes() {
  const b = useBasics();
  const star = useChart((s) => s.display.layout === "starlight");   // Starlight shows only the two chart panes; its charts carry the rest
  return b.data && !star ? <><KeyInfo b={b.data} /><div className="lower"><CoreInfo b={b.data} /><SmallAv b={b.data} /></div></> : null;
}

/** The form's quick links to the views of the chart it found ("Links"). */
export function ModeLinks({ links, mixed }: { links: [string, string, string?][]; mixed?: string }) {
  const { go, mode, natal, birth } = useChart();
  const [big, setBig] = useKept(`modes.mixedBig.${mixed}`, false);
  return (
    <div className="mode-links">
      <h3>Look at it in</h3>
      <div className="link-tiles">
        {links.map(([name, tab, sub]) => (
          <button key={name} type="button" className="tile" title={`Opens ${tab}`} onClick={() => go(tab, sub ? (sub.includes(":") ? sub.split(":") as [string, string] : ["strengths", sub]) : undefined)}>
            {name}<span className="tile-sub" aria-hidden="true">{tab}</span>
          </button>
        ))}
        {mixed && <button type="button" className="tile" disabled={!mode} aria-pressed={big} onClick={() => setBig(!big)}>Show Mixed {mixed}-Natal Chart!<span className="tile-sub" aria-hidden="true">{big ? "Shown below" : "Both charts in one"}</span></button>}
      </div>
      {big && mode && <div className="pad mixed"><MixedChart outerBirth={birth!} outerName={mode.title} innerBirth={natal!} innerName="Natal Chart" /></div>}
    </div>
  );
}

const ORDINALS = ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th", "10th", "11th", "12th", "13th"];   // a Tithi Pravesha year holds 12 lunar months, 13 with an Adhika month

/** head: Transits' sub tabs, when Tithi Pravesha is one of them; else the page's own title. */
export function TithiPravesha({ head }: { head?: React.ReactNode }) {
  const natal = useChart((s) => s.natal)!;
  const openSettings = useChart((s) => s.openWindow);
  const star = useChart((s) => s.display.layout === "starlight");
  const mode = useChart((s) => s.mode);
  const [by, setBy] = useKept<"year" | "date">("tp.by", "year");
  const [year, setYear] = useKept("tp.year", new Date().getFullYear());
  const kept = { windows: useKept("tp.month", 0), star: useKept("tp.starMonth", 1) };   // Starlight opens on the 1st month, the birth's own lunar month
  const [month, setMonth] = star ? kept.star : kept.windows;
  const [daily, setDaily] = useKept("tp.daily", false);
  const [day, setDay] = useKept("tp.day", 1);
  const [kind, setKind] = useKept<"tithi" | "nakshatra" | "yoga">("tp.kind", "tithi");
  const [period, setPeriod] = useKept<"annual" | "monthly" | "fortnightly" | "daily">("tp.period", "annual");
  const [before, setBefore] = useState(false);
  const { fields, moment, put } = useMoment();
  const byYear = useFind((y: number) => api.tithiPravesha(natal, y, month, daily && month ? day : 0));
  // Starlight: Previous and Next search a minute either side of the date, which then moves to the chart found, so a click steps on
  const byDate = useFind((back: boolean) => {
    const m = moment();
    return api.pravesha(natal, star ? { ...m, hour_local: m.hour_local + (back ? -1 : 1) / 60 } : m, kind, period, back);
  }, (r) => star && put(r.birth));
  const stepYear = (back: boolean) => { const y = year + (back ? -1 : 1); setYear(y); byYear.mutate(y); };
  const links = <ModeLinks mixed="TP" links={[["Tithi Ashtottari dasa", "Dasas", "dasaGroup:other"], ["Yoga Vimsottari dasa", "Dasas", "dasaGroup:other"], ["Vimsottari dasa", "Dasas", "dasaGroup:nakshatra"], ["Narayana dasa", "Dasas", "dasaGroup:rasi"]]} />;
  const error = byYear.error ?? byDate.error;
  // Starlight names each month of the year by its lunar month; the numbers stand in until the names come
  const months = useQuery({ queryKey: ["tpMonths", natal, year], queryFn: () => api.tithiPraveshaMonths(natal, year), enabled: star && year >= natal.year, placeholderData: (p) => p });
  const md = months.data;
  // a 13-month year with no Adhika: the year's chart fell a month early, so its 1st month's name comes again as the 13th
  const again = md?.length === 13 && md[12] === md[0];
  const names = md?.map((n, i) => `${ORDINALS[i]} · ${n}${again && i === 12 ? " (again)" : ""}`) ?? ORDINALS;
  // the year's Adhika or Kshaya months (or none) are named under the form, so a change of year that brings one is seen
  const odd = md?.filter((n) => n.includes("Adhika") || n.includes("Kshaya")) ?? [];
  const note = md && `${year}: ${md.length} months, ` + (odd.length ? `with ${odd.join(", ")}` : "no Adhika or Kshaya month")
    + (again ? `; ${md[0]} comes twice, as the 1st and the 13th` : "");
  useEffect(() => { if (months.data && month > months.data.length) setMonth(months.data.length); }, [months.data, month, setMonth]);
  useEffect(() => { if (star && month < 1) setMonth(1); }, [star, month, setMonth]);   // Starlight has no annual choice: a kept 0 becomes the 1st
  const yearFields = <>
    <label>Month
      <select value={month} onChange={(e) => setMonth(Number(e.target.value))}>{names.map((n, i) => <option key={i} value={i + 1}>{n}</option>)}</select>
    </label>
    <label className="check"><input type="checkbox" checked={daily} disabled={!month} onChange={(e) => setDaily(e.target.checked)} /> Daily chart</label>
    {daily && !!month && <label>Day (1-30)<input type="number" min={1} max={30} value={day} onChange={(e) => setDay(Number(e.target.value))} /></label>}
    {note && <p className="mf-note muted">{supOrd(note)}</p>}
  </>;
  const pickFields = <>
    <label>Which Pravesha
      <select value={kind} onChange={(e) => setKind(e.target.value as typeof kind)}>
        <option value="tithi">Tithi Pravesha</option><option value="nakshatra">Nakshatra Pravesha</option><option value="yoga">Yoga Pravesha</option>
      </select>
    </label>
    <label>Chart
      <select value={period} onChange={(e) => setPeriod(e.target.value as typeof period)}>
        <option value="annual">Annual chart</option><option value="monthly">Monthly chart</option>
        <option value="fortnightly">Fortnightly chart</option><option value="daily">Daily chart</option>
      </select>
    </label>
  </>;
  if (star) {
    const busy = byYear.isPending || byDate.isPending;
    // no bar on top: the year or date choice sits beside the form's title, the year with the month below
    const byRow = <div className="mf-by">
      <h3>Pravesha chart</h3>
      <div className="seg" role="tablist" aria-label="Find by">
        <button type="button" role="tab" aria-selected={by === "year"} onClick={() => setBy("year")}>By year</button>
        <button type="button" role="tab" aria-selected={by === "date"} onClick={() => setBy("date")}>From a date</button>
      </div>
    </div>;
    return <StarFinder head={head} links={links}
      form={by === "year" ? (
        <form className="mf-detail" onSubmit={(e) => { e.preventDefault(); byYear.mutate(year); }}>
          {byRow}<div className="mf-options">
            <label>Year<input type="number" value={year} onChange={(e) => setYear(Number(e.target.value))} min={natal.year} max={9000} required /></label>
            {yearFields}
          </div>
          <div className="mf-go">
            <PrevNext busy={busy} first={year <= natal.year} go={stepYear} cast={mode?.event?.kind === 2} />
            <CastButton busy={busy} kind="Tithi Pravesha" cast={(keep) => byYear.mutate(year, { onSuccess: keep })} />
            <BackToNatal />
            {busy && <span className="muted">Searching…</span>}
          </div>
          {error && <p role="alert" className="error banner">{error.message}</p>}
        </form>
      ) : (
        <form className="mf-detail" onSubmit={(e) => { e.preventDefault(); byDate.mutate(false); }}>
          {byRow}<div className="mf-options">{pickFields}{fields}</div>
          <div className="mf-go">
            <PrevNext busy={busy} go={(back) => byDate.mutate(back)} />
            <button type="button" onClick={() => openSettings({ kind: "settings", group: "Tithi Pravesha" })}>Options</button>
            <BackToNatal />
            {busy && <span className="muted">Searching…</span>}
          </div>
          {error && <p role="alert" className="error banner">{error.message}</p>}
        </form>
      )} />;
  }
  return (
    <div className="right lab">
      <header className="lab-head">
        {head ?? <><h1>Tithi Pravesha</h1>
        <p className="muted">The chart for the return of the birth tithi, nakshatra or yoga</p></>}
      </header>
      <div className="finder">
        <section className="pane finder-form">
          <header className="pane-head"><h2>Find a return</h2>
            <div className="seg" role="tablist" aria-label="Find by">
              <button role="tab" aria-selected={by === "year"} onClick={() => setBy("year")}>By year</button>
              <button role="tab" aria-selected={by === "date"} onClick={() => setBy("date")}>From a date</button>
            </div>
          </header>
          {by === "year" ? (
            <form className="mode-form" onSubmit={(e) => { e.preventDefault(); byYear.mutate(year); }}>
              <label className="big-field">Year<input type="number" value={year} onChange={(e) => setYear(Number(e.target.value))} min={natal.year} max={9000} required /></label>
              <p className="field-note muted">Year {year - natal.year + 1} of life</p>
              <label>Month
                <select value={month} onChange={(e) => setMonth(Number(e.target.value))}><option value={0}>None</option>{ORDINALS.map((n, i) => <option key={n} value={i + 1}>{n}</option>)}</select>
              </label>
              <label className="check"><input type="checkbox" checked={daily} disabled={!month} onChange={(e) => setDaily(e.target.checked)} /> Daily chart: Enter 1-30</label>
              {daily && !!month && <label>Day<input type="number" min={1} max={30} value={day} onChange={(e) => setDay(Number(e.target.value))} /></label>}
              <div className="mode-buttons">
                <button type="submit" className="primary" disabled={byYear.isPending}>Find Tithi Pravesha Chart</button>
              </div>
            </form>
          ) : (
            <form className="mode-form" onSubmit={(e) => { e.preventDefault(); byDate.mutate(before); }}>
              {pickFields}
              <label>The chart<select value={String(before)} onChange={(e) => setBefore(e.target.value === "true")}><option value="false">After</option><option value="true">Before</option></select></label>
              {fields}
              <div className="mode-buttons"><button type="submit" className="primary" disabled={byDate.isPending}>Find {before ? "last chart before" : "first chart after"} this date</button>
                <button type="button" onClick={() => openSettings({ kind: "settings", group: "Tithi Pravesha" })}>Options</button></div>
            </form>
          )}
        </section>
        <ModeCard error={error} empty="No return chart yet. Choose a year, or a date to search from, and find its chart.">{links}</ModeCard>
      </div>
      <ChartPanes />
    </div>
  );
}

export function AngularReturn() {
  // the "before" and "after" of the angular return form; the form keeps the same links as Tithi Pravesha
  const natal = useChart((s) => s.natal)!;
  const [a, setA] = useState(1);
  const [b, setB] = useState(2);
  const [backward, setBackward] = useState(false);
  const { fields, moment } = useMoment();
  const find = useFind(() => api.angularReturn(natal, moment(), a, b, backward));
  const planets = BODIES.slice(1).map((n, i) => <option key={n} value={i + 1}>{n}</option>);
  const star = useChart((s) => s.display.layout === "starlight");     // Starlight: the sub tab already names the view
  return (
    <>
      <section className="pane">
        {!star && <header className="pane-head"><h2>Angular Return</h2><span className="muted">When two bodies are again as far apart as at birth</span></header>}
        <form className="mode-form" onSubmit={(e) => { e.preventDefault(); find.mutate(undefined); }}>
          <label>Between<select value={a} onChange={(e) => setA(Number(e.target.value))}>{planets}</select></label>
          <label>And<select value={b} onChange={(e) => setB(Number(e.target.value))}>{planets}</select></label>
          <label>Direction
            <select value={String(backward)} onChange={(e) => setBackward(e.target.value === "true")}>
              <option value="true">Before</option><option value="false">After</option>
            </select>
          </label>
          {fields}
          <div className="mode-buttons">
            <button type="submit" className="primary" disabled={find.isPending}>Find Angular Return Chart</button>
            {!star && <BackToNatal />}
          </div>
        </form>
        <ModeFacts error={find.error} />
        <ModeLinks mixed="Angular Return" links={[["Vimsottari dasa", "Dasas", "dasaGroup:nakshatra"], ["Narayana dasa", "Dasas", "dasaGroup:rasi"]]} />
      </section>
      <ChartPanes />
    </>
  );
}

const CALENDAR: { group: string; items: [string, string][] }[] = [
  { group: "Solar charts", items: [["solar_year", "Solar New Year"], ["solar_month", "Solar New Month"], ["ardra", "Ardra Pravesha"]] },
  { group: "Lunar charts", items: [["lunar_year", "Lunar New Year"], ["lunar_month", "Lunar New Month"], ["lunar_day", "New Lunar Day"], ["fortnight", "Fortnight Chart"]] },
];

/** The Mundane tab's Mundane charts: the calendar, eclipse, conjunction, transit, station and swearing-in charts found from the current chart. */
export function MundaneFinders() {
  const { birth, natal, mode, openWindow } = useChart();
  const [backward, setBackward] = useState(true);
  const [ecl, setEcl] = useState({ eclipse: "lunar", at_max: false });
  const [conj, setConj] = useState({ body: 5, other: 7, angle: 0 });
  const [walk, setWalk] = useState({ body: 1, division: "Rasi" });
  const [station, setStation] = useState(5);
  const [effect, setEffect] = useState({ years: 1, days: 0 });
  const find = useFind((o: Record<string, unknown>) => api.mundane(birth!, { backward, in_mode: !!mode, ...o }));
  const other = useFind((f: () => Promise<ModeResult>) => f());
  const busy = find.isPending || other.isPending;
  const bodies = BODIES.map((n, i) => <option key={n} value={i}>{n}</option>);
  return (
    <div className="right">
      <section className="pane">
        <header className="pane-head"><h2>Mundane charts</h2><span className="muted">Searches run from the current chart's date</span></header>
        <div className="mode-form">
          <label>Find the
            <select value={String(backward)} onChange={(e) => setBackward(e.target.value === "true")}>
              <option value="true">Previous</option><option value="false">Next</option>
            </select>
          </label>
          <div className="mode-buttons"><BackToNatal /><button type="button" onClick={() => openWindow({ kind: "settings", group: "Calendars" })}>Solar and Lunar Calendar Options</button></div>
          {CALENDAR.map((g) => (
            <fieldset key={g.group} className="mode-group"><legend>{g.group}</legend>
              {g.items.map(([kind, name]) => <button key={kind} type="button" disabled={busy} onClick={() => find.mutate({ kind })}>{name}</button>)}
            </fieldset>
          ))}
          <fieldset className="mode-group"><legend>Eclipse</legend>
            <label>Kind
              <select value={ecl.eclipse} onChange={(e) => setEcl({ ...ecl, eclipse: e.target.value })}>
                <option value="lunar">Lunar</option><option value="solar">Global Solar</option><option value="local">Local Solar</option>
              </select>
            </label>
            <label>Make a chart at
              <select value={String(ecl.at_max)} onChange={(e) => setEcl({ ...ecl, at_max: e.target.value === "true" })}>
                <option value="false">Start</option><option value="true">Maximum</option>
              </select>
            </label>
            <button type="button" disabled={busy} onClick={() => find.mutate({ kind: "eclipse", ...ecl })}>Eclipse Mode</button>
          </fieldset>
          <fieldset className="mode-group"><legend>Conjunction / opposition</legend>
            <label>Graha<select value={conj.body} onChange={(e) => setConj({ ...conj, body: Number(e.target.value) })}>{bodies}</select></label>
            <label>And<select value={conj.other} onChange={(e) => setConj({ ...conj, other: Number(e.target.value) })}>{bodies}</select></label>
            <label>Angle
              <select value={conj.angle} onChange={(e) => setConj({ ...conj, angle: Number(e.target.value) })}>
                {ANGLES.map(([n, v]) => <option key={v} value={v}>{n}</option>)}
              </select>
            </label>
            <button type="button" disabled={busy} onClick={() => find.mutate({ kind: "conjunction", ...conj })}>Conjunction/Opposition Mode</button>
          </fieldset>
          <fieldset className="mode-group"><legend>Graha transit</legend>
            <label>Graha<select value={walk.body} onChange={(e) => setWalk({ ...walk, body: Number(e.target.value) })}>{bodies}</select></label>
            <label>Changes
              <select value={walk.division} onChange={(e) => setWalk({ ...walk, division: e.target.value })}>
                {DIVISIONS.map((d) => <option key={d}>{d}</option>)}
              </select>
            </label>
            <button type="button" disabled={busy} onClick={() => find.mutate({ kind: "planet_transit", ...walk })}>Graha Transit Mode</button>
          </fieldset>
          <fieldset className="mode-group"><legend>Stationary transit</legend>
            <label>Graha
              <select value={station} onChange={(e) => setStation(Number(e.target.value))}>
                {BODIES.slice(3).map((n, i) => <option key={n} value={i + 3}>{n}</option>)}
              </select>
            </label>
            <button type="button" disabled={busy} onClick={() => find.mutate({ kind: "stationary", body: station })}>Stationary Transit Mode</button>
          </fieldset>
          <fieldset className="mode-group"><legend>Treat the current chart as a mundane chart in effect for</legend>
            <label>Years (of 365.24219 days)<input type="number" step="any" min={0} value={effect.years} onChange={(e) => setEffect({ ...effect, years: Number(e.target.value) })} /></label>
            <label>Plus days<input type="number" step="any" min={0} value={effect.days} onChange={(e) => setEffect({ ...effect, days: Number(e.target.value) })} /></label>
            <button type="button" disabled={busy} onClick={() => find.mutate({ kind: "swearing_in", ...effect })}>Swearing-in Chart Mode</button>
          </fieldset>
          <fieldset className="mode-group"><legend>From the natal chart</legend>
            <button type="button" disabled={busy} onClick={() => other.mutate(() => api.nisheka(natal!))}>Nisheka / Aadhana chart</button>
            <button type="button" disabled={busy} onClick={() => other.mutate(() => api.lifecycle(natal!, -1))}>Previous lifecycle</button>
            <button type="button" disabled={busy} onClick={() => other.mutate(() => api.lifecycle(natal!, 1))}>Next lifecycle</button>
          </fieldset>
        </div>
        {busy && <p className="muted pad">Searching…</p>}
        <ModeFacts error={find.error ?? other.error} />
      </section>
      <ChartPanes />
    </div>
  );
}

type Finder = { id: string; chip: string; name: string; note: string; once?: true };
const FINDERS: { group: string; items: Finder[] }[] = [
  { group: "Solar", items: [
    { id: "solar_year", chip: "New Year", name: "Solar New Year", note: "The Sun enters the year's first sign; in effect until it next does." },
    { id: "solar_month", chip: "New Month", name: "Solar New Month", note: "The Sun enters a sign; in effect until it enters the next." },
    { id: "ardra", chip: "Ardra Pravesha", name: "Ardra Pravesha", note: "The Sun enters Ardra (6°40′ Gemini): the meteorological year." }] },
  { group: "Lunar", items: [
    { id: "lunar_year", chip: "New Year", name: "Lunar New Year", note: "The lunar year's first month begins; in effect for the year." },
    { id: "lunar_month", chip: "New Month", name: "Lunar New Month", note: "A lunar month begins; in effect until the next one." },
    { id: "lunar_day", chip: "New Lunar Day", name: "New Lunar Day", note: "A tithi begins; in effect until the next tithi." },
    { id: "fortnight", chip: "Fortnight", name: "Fortnight Chart", note: "A paksha begins at a new or full moon." }] },
  { group: "Eclipse", items: [
    { id: "eclipse", chip: "Eclipse", name: "Eclipse", note: "A lunar or solar eclipse, cast at its start or its maximum." }] },
  { group: "Events", items: [
    { id: "conjunction", chip: "Conjunction", name: "Conjunction / opposition", note: "Two bodies reach the chosen angle; in effect until they next do." },
    { id: "planet_transit", chip: "Graha transit", name: "Graha transit", note: "A graha changes sign in the chosen varga." },
    { id: "stationary", chip: "Station", name: "Stationary transit", note: "A graha turns retrograde or direct; in effect until its next station." },
    { id: "swearing_in", chip: "Swearing-in", name: "Swearing-in chart", note: "The current chart taken as a mundane chart, its dasas fitted to the period it is in effect.", once: true },
    { id: "nisheka", chip: "Nisheka", name: "Nisheka / Aadhana", note: "The conception chart of the natal chart.", once: true },
    { id: "lifecycle", chip: "Lifecycle", name: "Lifecycle", note: "The natal chart one lifecycle (144 years by default) earlier or later." }] },
];

/** The New Year finders' year list: 1800 to 2200, and the chart's own year if it lies outside. */
const YEARS = (y: number) => Array.from({ length: Math.max(2200, y) - Math.min(1800, y) + 1 }, (_, i) => Math.min(1800, y) + i);

/** Starlight's Mundane charts: Solar, Lunar, Eclipse and Events on top, the group's charts under them, then the chosen one's options,
 *  Previous and Next, and the chart in use in one line. */
export function StarMundaneFinders() {
  const { birth, natal, mode, openWindow } = useChart();
  const [group, setGroup] = useKept("mundane.group", "Solar");
  const [picks, setPicks] = useKept<Record<string, string>>("mundane.picks", {});   // the chart last chosen in each group
  const g = FINDERS.find((x) => x.group === group) ?? FINDERS[0];
  const f = g.items.find((x) => x.id === picks[g.group]) ?? g.items[0];
  const kind = f.id;
  const [ecl, setEcl] = useKept("mundane.eclipse", { eclipse: "lunar", at_max: false });
  const [conj, setConj] = useKept("mundane.conjunction", { body: 5, other: 7, angle: 0 });
  const [walk, setWalk] = useKept("mundane.transit", { body: 1, division: "Rasi" });
  const [station, setStation] = useKept("mundane.station", 5);
  const [effect, setEffect] = useKept("mundane.effect", { years: 1, days: 0 });
  // a number is a year to jump to: the first new year found from its 1st of January
  const find = useFind((backward: boolean | number) => {
    if (typeof backward === "number") return api.mundane({ ...birth!, year: backward, month: 1, day: 1, hour_local: 0 }, { backward: false, in_mode: !!mode, kind });
    if (kind === "nisheka") return api.nisheka(natal!);
    if (kind === "lifecycle") return api.lifecycle(natal!, backward ? -1 : 1);
    const o = { eclipse: ecl, conjunction: conj, planet_transit: walk, stationary: { body: station }, swearing_in: effect }[kind] ?? {};
    return api.mundane(birth!, { backward, in_mode: !!mode, kind, ...o });
  });
  const bodies = BODIES.map((n, i) => <option key={n} value={i}>{n}</option>);
  const options = kind === "eclipse" ? <>
    <label>Kind
      <select value={ecl.eclipse} onChange={(e) => setEcl({ ...ecl, eclipse: e.target.value })}>
        <option value="lunar">Lunar</option><option value="solar">Global Solar</option><option value="local">Local Solar</option>
      </select>
    </label>
    <label>Cast at
      <select value={String(ecl.at_max)} onChange={(e) => setEcl({ ...ecl, at_max: e.target.value === "true" })}>
        <option value="false">Start</option><option value="true">Maximum</option>
      </select>
    </label>
  </> : kind === "conjunction" ? <>
    <label>Graha<select value={conj.body} onChange={(e) => setConj({ ...conj, body: Number(e.target.value) })}>{bodies}</select></label>
    <label>And<select value={conj.other} onChange={(e) => setConj({ ...conj, other: Number(e.target.value) })}>{bodies}</select></label>
    <label>Angle<select value={conj.angle} onChange={(e) => setConj({ ...conj, angle: Number(e.target.value) })}>{ANGLES.map(([n, v]) => <option key={v} value={v}>{n}</option>)}</select></label>
  </> : kind === "planet_transit" ? <>
    <label>Graha<select value={walk.body} onChange={(e) => setWalk({ ...walk, body: Number(e.target.value) })}>{bodies}</select></label>
    <label>Changes sign in<select value={walk.division} onChange={(e) => setWalk({ ...walk, division: e.target.value })}>{DIVISIONS.map((d) => <option key={d}>{d}</option>)}</select></label>
  </> : kind === "stationary" ? (
    <label>Graha<select value={station} onChange={(e) => setStation(Number(e.target.value))}>{BODIES.slice(3).map((n, i) => <option key={n} value={i + 3}>{n}</option>)}</select></label>
  ) : kind === "swearing_in" ? <>
    <label>In effect for years<input type="number" step="any" min={0} value={effect.years} onChange={(e) => setEffect({ ...effect, years: Number(e.target.value) })} /></label>
    <label>Plus days<input type="number" step="any" min={0} value={effect.days} onChange={(e) => setEffect({ ...effect, days: Number(e.target.value) })} /></label>
  </> : null;
  return (
    <div className="right lab mf">
      <header className="lab-head">
        <SubTabs tabs={FINDERS.map((x) => ({ id: x.group, name: x.group }))} value={g.group} onChange={setGroup} label="Mundane charts" />
        <button type="button" onClick={() => openWindow({ kind: "settings", group: "Calendars" })}>Solar and Lunar Calendar Options</button>
      </header>
      <section className="pane mf-find">
        {g.items.length > 1 && (
          <div className="mf-chips" role="group" aria-label={`${g.group} charts`}>
            {g.items.map((x) => <button key={x.id} type="button" aria-pressed={x.id === kind} onClick={() => setPicks({ ...picks, [g.group]: x.id })}>{x.chip}</button>)}
          </div>
        )}
        <form className="mf-detail" onSubmit={(e) => { e.preventDefault(); find.mutate(false); }}>
          {g.items.length > 1 && <h2>{f.name}</h2>}
          <p className="muted">{f.note}</p>
          {options && <div className="mf-options">{options}</div>}
          <div className="mf-go">
            {f.once ? <button type="submit" className="primary" disabled={find.isPending}>Cast chart</button> : <PrevNext busy={find.isPending} go={(back) => find.mutate(back)} />}
            {(kind === "solar_year" || kind === "lunar_year") && birth && (
              <select aria-label="Year" value={birth.year} disabled={find.isPending} onChange={(e) => find.mutate(Number(e.target.value))}>
                {YEARS(birth.year).map((y) => <option key={y} value={y}>{y}</option>)}
              </select>
            )}
            <BackToNatal />
            {find.isPending && <span className="muted">Searching…</span>}
          </div>
          <p className="muted hint">{kind === "nisheka" || kind === "lifecycle" ? "Found from the natal chart." : "Found from the current chart's date, so Previous or Next again steps on to the one after."}</p>
          {find.error && <p role="alert" className="error banner">{find.error.message}</p>}
        </form>
      </section>
      <ChartInUse />
    </div>
  );
}

/** The casts whose + opens the chart as the natal chart's (its natal chart and the cast in use), not as a birth chart of its own. */
const ofNatal = (kind: string) => kind === "Transit";

/** Starlight's Cast, with a + beside it that casts the chart and opens it on its own as "Tajaka-2026-Name" (drawn "☉-2026-Name"), the chart it was
 *  cast from left as it was (the cast enters it first, so its birth and mode are put back before the new one opens). A transit opens as the
 *  natal chart's transit, still read against it, "Transit-2026-Name" even when cast from another transit of that chart. */
export function CastButton({ busy, kind, cast }: { busy: boolean; kind: string; cast: (keep: (r: ModeResult) => void) => void }) {
  const { name, enterMode, openChart } = useChart();
  const castOpen = () => {
    const { birth, mode } = useChart.getState();
    cast((r) => {
      // a transit opens as the natal chart's transit (its Transit Calendar and every transit view working); the others as charts of their own
      const now = useChart.getState();
      const of = ofNatal(kind) && now.natal && now.mode ? { natal: now.natal, mode: now.mode } : undefined;
      if (birth) enterMode(birth, mode);
      openChart(castName(kind, r.birth.year, (of ? name.replace(/^Transit-\d+-/, "") : name) || "Chart"), r.birth, of && now.meta, of);
    });
  };
  return (
    <span className="cast-combo">
      <button type="submit" disabled={busy}>Cast</button>
      <button type="button" disabled={busy} aria-label="Cast and open as its own chart" data-tip="Cast and open as its own chart"
        onClick={castOpen}><Icon name="plus" /></button>
    </span>
  );
}

/** Previous and Next of a Starlight finder. With `cast` false (no chart of this finder in use yet) they do nothing: hovering or
 *  pressing one shows the hover label "Cast a chart first" just below it. */
export function PrevNext({ go, busy, first, cast = true }: { go: (back: boolean) => void; busy: boolean; first?: boolean; cast?: boolean }) {
  const [tip, setTip] = useState<{ x: number; y: number } | null>(null);
  const show = (e: React.PointerEvent | React.MouseEvent) => {
    if (cast) return;
    const r = e.currentTarget.getBoundingClientRect();
    setTip({ x: r.left + r.width / 2, y: r.bottom + 6 });
  };
  const hide = () => setTip(null);
  const press = (back: boolean) => (e: React.MouseEvent) => (cast ? go(back) : show(e));
  return <>
    <button type="button" className="primary step" disabled={busy || first} onPointerEnter={show} onPointerLeave={hide} onClick={press(true)}><Icon name="prev" />Previous</button>
    <button type="button" className="primary step" disabled={busy} onPointerEnter={show} onPointerLeave={hide} onClick={press(false)}>Next<Icon name="next" /></button>
    {tip && !cast && <span className="bar-tip" role="tooltip" style={{ left: tip.x, top: tip.y }}>Cast a chart first</span>}
  </>;
}

/** The chart in use, as Starlight's finders show it: its title, when it holds, and its birth details. */
function ChartInUse() {
  const mode = useChart((s) => s.mode);
  const b = useBasics();
  return (
    <section className="pane star-inspector mf-chart" aria-live="polite">
      <header className="pane-head">
        <h2 className="mode-title">{mode ? <><span className="live-dot" aria-hidden="true" />{mode.title}</> : "Natal Chart"}</h2>
      </header>
      {b.data ? <Inspector b={b.data} lead={mode?.lines ?? []} /> : <p className="muted pad">Calculating…</p>}
      {!mode && <p className="muted hint pad">The chart found replaces the natal chart on every tab until you go back.</p>}
    </section>
  );
}

/** Starlight's Tajaka and Tithi Pravesha in three: the form top left, the dasas and views to open top right, the chart in use below. */
export function StarFinder({ head, form, links }: { head?: React.ReactNode; form: React.ReactNode; links: React.ReactNode }) {
  return (
    <div className="right lab mf mp">
      {head && <header className="lab-head">{head}</header>}
      <section className="pane mf-find">{form}</section>
      <section className="pane mp-links">{links}</section>
      <ChartInUse />
    </div>
  );
}

/** The Mundane tab: the charts of the year, month, eclipse and other events found from the current chart. */
export function MundaneCharts() {
  return useChart((s) => s.display.layout) === "starlight" ? <StarMundaneFinders /> : <MundaneFinders />;
}

const PROGRESSIONS: [string, string][] = [["solar", "Solar Progression (1 sign per year)"], ["nakshatra", "Nakshatra Dasa Progression"],
  ["bhrigu", "Bhrigu Pada Progression"], ["sudarsana", "Sudarsana Chakra Dasa Progression"]];

const PROG_DIVISIONS = [1, 9, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 16, 20, 24, 27, 30, 40, 45, 60, 108];
const NAK_DASAS: [string, string][] = [["vimsottari_dasa", "Vimsottari"], ["ashtottari_dasa", "Ashtottari"], ["yogini_dasa", "Yogini"], ["dwi_saptati_sama_dasa", "Dwisaptati sama"], ["shat_trimsa_sama_dasa", "Shattrimsa sama"], ["dwadasottari_dasa", "Dwadasottari"], ["chaturaseeti_sama_dasa", "Chaturaseeti sama"], ["sataabdika_dasa", "Satabdika"], ["shodasottari_dasa", "Shodasottari"], ["panchottari_dasa", "Panchottari"], ["shashti_hayani_dasa", "Shashtisama"]];

export function Progressions() {
  const { natal, birth, mode, display } = useChart();
  const { fields, moment } = useMoment(natal!.tz_east_hours, false);
  const [division, setDivision] = useState(1);
  const [dasa, setDasa] = useState("vimsottari_dasa");
  const [seed, setSeed] = useState(2);
  const find = useFind((kind: string) => api.progression(natal!, kind, moment(), division, dasa, seed));
  const shown = !!mode?.title.startsWith("Prog");
  return (
    <>
      <section className="pane">
        {display.layout !== "starlight" && <header className="pane-head"><h2>Progressions</h2><span className="muted">Of the Rasi; the nakshatra one by Vimsottari from the Moon</span></header>}
        <form className="mode-form" onSubmit={(e) => e.preventDefault()}>
          <label>Choose varga<select value={division} onChange={(e) => setDivision(Number(e.target.value))}>{PROG_DIVISIONS.map((d) => <option key={d} value={d}>{d === 1 ? "Rasi" : `D-${d}`}</option>)}</select></label>
          <label>Choose nakshatra dasa<select value={dasa} onChange={(e) => setDasa(e.target.value)}>{NAK_DASAS.map(([k, n]) => <option key={k} value={k}>{n}</option>)}</select></label>
          <label>Nakshatra dasa seed<select value={seed} onChange={(e) => setSeed(Number(e.target.value))}>{BODIES.map((n, i) => <option key={n} value={i}>{n}</option>)}</select></label>
          {fields}
          <div className="mode-buttons">
            {PROGRESSIONS.map(([kind, name]) => <button key={kind} type="button" disabled={find.isPending} onClick={() => find.mutate(kind)}>{name}</button>)}
            {display.layout !== "starlight" && <BackToNatal />}
          </div>
        </form>
        <ModeFacts error={find.error} />
      </section>
      {shown && <section className="pane"><header className="pane-head"><h2>Mixed Progressed-Natal Chart</h2></header>
        <div className="pad mixed"><MixedChart outerBirth={birth!} outerName={mode!.title} innerBirth={natal!} innerName="Natal Chart" /></div></section>}
      <ChartPanes />
    </>
  );
}

const PRASNA: { kind: string; name: string; top: number; note: string }[] = [
  { kind: "108", name: "Prasna-108 Mode", top: 108, note: "Fixes the rasi and navamsa of the Prasna Lagna." },
  { kind: "249", name: "Prasna-249 Mode (KP)", top: 249, note: "Fixes the rasi, nakshatra and sub of the Prasna Lagna." },
  { kind: "nadi", name: "Nadi Prasna Mode", top: 1800, note: "Fixes the rasi and nadi of the Prasna Lagna." }];

export function Prasna() {
  const natal = useChart((s) => s.natal)!;
  const [numbers, setNumbers] = useState<Record<string, number>>({ "108": 1, "249": 1, nadi: 1 });
  const [replace, setReplace] = useState(false);
  const [compress, setCompress] = useState(false);
  const [span, setSpan] = useState({ years: 1, days: 0 });
  const star = useChart((s) => s.display.layout === "starlight");
  const find = useFind((kind: string) => api.prasna(natal, kind, numbers[kind], replace, compress ? span.years : 0, compress ? span.days : 0));
  return (
    <>
      <section className="pane">
        {!star && <header className="pane-head"><h2>Prasna (Horary)</h2><span className="muted">The chart keeps its moment; a number gives the lagna</span></header>}
        <form className="mode-form" onSubmit={(e) => e.preventDefault()}>
          <label>Which lagna
            <select value={String(replace)} onChange={(e) => setReplace(e.target.value === "true")}>
              <option value="false">Show Prasna Lagna (PLag) as a separate body</option>
              <option value="true">Replace the lagna with the Prasna Lagna</option>
            </select>
          </label>
          <fieldset className="mode-group wide"><legend>Dasa Compression</legend>
            <label className="check"><input type="checkbox" checked={compress} onChange={(e) => setCompress(e.target.checked)} /> Compress dasas of the prasna chart to the following duration</label>
            <label>Years (of 365.24219 days)<input type="number" step="any" min={0} value={span.years} disabled={!compress} onChange={(e) => setSpan({ ...span, years: Number(e.target.value) })} /></label>
            <label>Plus days<input type="number" step="any" min={0} value={span.days} disabled={!compress} onChange={(e) => setSpan({ ...span, days: Number(e.target.value) })} /></label>
          </fieldset>
          {!star && <div className="mode-buttons"><BackToNatal /></div>}
          {PRASNA.map((p) => (
            <fieldset key={p.kind} className="mode-group"><legend>{p.note}</legend>
              <label>Number (1 to {p.top})
                <input type="number" min={1} max={p.top} value={numbers[p.kind]} onChange={(e) => setNumbers({ ...numbers, [p.kind]: Number(e.target.value) })} />
              </label>
              <button type="button" disabled={find.isPending} onClick={() => find.mutate(p.kind)}>{p.name}</button>
            </fieldset>
          ))}
        </form>
        <ModeFacts error={find.error} />
      </section>
      <ChartPanes />
    </>
  );
}
