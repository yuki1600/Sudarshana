import { useMutation } from "@tanstack/react-query";
import { api, type TajakaPeriod } from "./api";
import { BackToNatal, CastButton, ChartPanes, ModeCard, ModeLinks, modeOf, PrevNext, StarFinder } from "./Modes";
import { useKept } from "./hooks";
import { useChart } from "./store";

const MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
const ORD = Array.from({ length: 12 }, (_, i) => i + 1);
const FINER: { key: "d25" | "h5" | "m25" | "m2"; name: string }[] = [
  { key: "d25", name: "Sixty-hour period" }, { key: "h5", name: "Five-hour period" },
  { key: "m25", name: "25-minute period" }, { key: "m2", name: "2-minute period" }];
// Starlight's periods: how short a period to cast; each needs every one above it
const LEVELS = [{ key: "year", name: "Year" }, { key: "month", name: "Month" }, { key: "d25", name: "60 hours" }, { key: "h5", name: "5 hours" },
  { key: "m25", name: "25 minutes" }, { key: "m2", name: "2 minutes" }] as const;

/** head: Transits' sub tabs, when Tajaka is one of them; else the page's own title. */
export function Tajaka({ head }: { head?: React.ReactNode }) {
  const { natal, mode, enterMode } = useChart();
  const star = useChart((s) => s.display.layout === "starlight");
  const [p, setP] = useKept<TajakaPeriod>("tajaka.when", { year: new Date().getFullYear(), month: 0, d25: 0, h5: 0, m25: 0, m2: 0 });
  const find = useMutation({
    mutationFn: ({ q = p, sunrise = false }: { q?: TajakaPeriod; sunrise?: boolean }) => api.tajaka(natal!, { ...q, sunrise }),
    onSuccess: (r) => enterMode(r.birth, modeOf(r)),
  });
  const set = (k: keyof TajakaPeriod) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => setP({ ...p, [k]: Number(e.target.value) });
  const links = <ModeLinks mixed="Tajaka" links={[["Patyayini dasa", "Dasas", "dasaGroup:other"], ["Mudda dasa", "Dasas", "dasaGroup:nakshatra"], ["Narayana dasa", "Dasas", "dasaGroup:rasi"], ["Pancha-vargeeya Bala", "Strengths", "other"], ["Dwadasa-vargeeya Bala (12)", "Strengths", "other"], ["Harsha Bala", "Strengths", "other"]]} />;

  if (star) {
    const level = LEVELS.reduce((at, l, i) => (i && p[l.key] > 0 ? i : at), 0);
    // a shorter period needs every longer one: picking it fills a "-" above with 1, and "-" clears the shorter ones below
    const pick = (i: number) => (e: React.ChangeEvent<HTMLSelectElement>) => {
      const v = Number(e.target.value);
      const q = { ...p, [LEVELS[i].key]: v };
      LEVELS.forEach((l, k) => { if (l.key === "year") return; if (k < i && v && !q[l.key]) q[l.key] = 1; if (k > i && !v) q[l.key] = 0; });
      setP(q);
    };
    // Previous and Next step the shortest period chosen, carrying into the one above past 12 (or 1)
    const step = (back: boolean) => {
      const q = { ...p };
      for (let i = level; i >= 0; i--) {
        const k = LEVELS[i].key;
        if (i === 0) { q.year += back ? -1 : 1; break; }
        const v = q[k] + (back ? -1 : 1);
        q[k] = ((v + 11) % 12) + 1;
        if (v >= 1 && v <= 12) break;
      }
      setP(q); find.mutate({ q });
    };
    return <StarFinder head={head} links={links} form={
      <form className="mf-detail" onSubmit={(e) => { e.preventDefault(); find.mutate({}); }}>
        <h3>Varshaphala chart</h3>
        <div className="mf-options tight">
          <label>Year<input type="number" value={p.year} onChange={set("year")} min={natal?.year} max={9000} required /></label>
          {LEVELS.slice(1).map((l, j) => (
            <label key={l.key}>{l.name}
              <select value={p[l.key]} onChange={pick(j + 1)}>
                <option value={0}>-</option>{(j ? ORD : MONTHS).map((n, i) => <option key={n} value={i + 1}>{n}</option>)}
              </select>
            </label>
          ))}
        </div>
        <div className="mf-go">
          <PrevNext busy={find.isPending} first={!level && !!natal && p.year <= natal.year} go={step} cast={mode?.event?.kind === 1} />
          <CastButton busy={find.isPending} kind="Tajaka" cast={(keep) => find.mutate({}, { onSuccess: keep })} />
          <button type="button" disabled={find.isPending} onClick={() => find.mutate({ sunrise: true })}>Sunrise chart</button>
          <BackToNatal />
          {find.isPending && <span className="muted">Searching…</span>}
        </div>
        {find.error && <p role="alert" className="error banner">{find.error.message}</p>}
      </form>} />;
  }

  return (
    <div className="right lab">
      <header className="lab-head">
        {head ?? <><h1>Tajaka</h1>
        <p className="muted">The annual (Varshaphal) chart, cast when the Sun returns to its natal tropical longitude</p></>}
      </header>
      <div className="finder">
        <section className="pane finder-form">
          <header className="pane-head"><h2>Find the year's chart</h2></header>
          <form className="mode-form" onSubmit={(e) => { e.preventDefault(); find.mutate({}); }}>
            <label className="big-field">Year<input type="number" value={p.year} onChange={set("year")} min={natal?.year} max={9000} required /></label>
            {natal && <p className="field-note muted">Year {p.year - natal.year + 1} of life</p>}
            <label>Month
              <select value={p.month} onChange={set("month")}><option value={0}>None</option>{MONTHS.map((m, i) => <option key={m} value={i + 1}>{m}</option>)}</select>
            </label>
            <details className="finer" open={FINER.some((f) => p[f.key] > 0) || undefined}>
              <summary>Shorter periods</summary>
              <div className="mode-form">
                {FINER.map((f) => (
                  <label key={f.key}>{f.name}
                    <select value={p[f.key]} onChange={set(f.key)}><option value={0}>None</option>{ORD.map((n) => <option key={n} value={n}>{n}</option>)}</select>
                  </label>
                ))}
              </div>
            </details>
            <div className="mode-buttons">
              <button type="submit" className="primary" disabled={find.isPending}>Find Tajaka Chart</button>
              <button type="button" disabled={find.isPending} onClick={() => find.mutate({ sunrise: true })}>Find Tajaka Sunrise Chart</button>
            </div>
          </form>
        </section>
        <ModeCard error={find.error} empty="No annual chart yet. Choose a year and find its chart.">{links}</ModeCard>
      </div>
      <ChartPanes />
    </div>
  );
}
