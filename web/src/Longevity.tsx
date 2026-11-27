import { Fragment, useEffect, useRef, type CSSProperties, type ReactNode } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api, saveSettings, type Ages, type Choice, type SettingOption, type Birth, type LgBody, type LongevityData, type LongevityHeadline, type LongevitySection } from "./api";
import { useDeath, useKept, useSaved, useSettings } from "./hooks";
import { Control } from "./Settings";
import { Meter } from "./Lab";
import { useChart } from "./store";
import { Icon } from "./Icons";
import { CopyButton, Loaded, OneRowTabs, supOrd, tableText } from "./ui";

const sectionText = (s: LongevitySection) => [s.name, s.verdict, ...s.tables.flatMap((t) => [t.title, tableText(t.columns, t.rows)]), ...s.notes].join("\n\n");

const classTone = (c: string) =>
  /Very short|Short/.test(c) ? "short" : /Medium/.test(c) ? "medium" : /Extreme|supreme/i.test(c) ? "extreme" : "long";

function ClassChip({ value }: { value: string }) {
  return <span className={`longevity-chip ${classTone(value)}`}>{value}</span>;
}

function Metric({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="longevity-metric">
      <span className="muted">{label}</span>
      <div>{children}</div>
    </div>
  );
}

function SummaryHero({ h, onGo }: { h: LongevityHeadline; onGo: (id: string) => void }) {
  const years = h.rectified != null ? `${h.pairSpan} (rectified ${h.rectified.toFixed(2)})` : h.pairSpan;
  const marakaNames = h.marakas.map((m) => m.planet).join(", ") || "none";
  const niryana = h.niryana.length ? h.niryana.map((c) => `${c.sign} (${c.age})`).join("; ") : "none in class window";
  return (
    <div className="longevity-hero">
      <p className="best-banner">
        <span aria-hidden="true">★</span>{" "}
        <ClassChip value={h.class} />
        <span className="match-score"> {years} years from the three pairs</span>
        <span className="muted"> · Chosen span {h.span.chosen.join(" + ")} {h.span.years.toFixed(2)} y</span>
        {" "}
        <button type="button" className="link" onClick={() => onGo("pairs")}>Pairs</button>
        {" · "}
        <button type="button" className="link" onClick={() => onGo("marakas")}>Marakas</button>
        {" · "}
        <button type="button" className="link" onClick={() => onGo("rudra")}>Niryana</button>
      </p>
      <div className="longevity-metrics">
        <Metric label="Life class"><ClassChip value={h.class} /></Metric>
        <Metric label="Pair years"><strong>{years}</strong></Metric>
        <Metric label="Marakas"><strong>{marakaNames}</strong></Metric>
        <Metric label="Niryana MD"><strong>{niryana}</strong></Metric>
        <Metric label="Preferred AD"><strong>{h.preferredAds.slice(0, 3).join("; ") || "—"}</strong></Metric>
        <Metric label="Class agreement">
          <strong>{h.corroboration.agree.length}/{h.corroboration.total}</strong>
          <span className="muted"> match pairs</span>
        </Metric>
      </div>
      {h.niryana.length > 0 && (
        <table className="points wrap longevity-primary">
          <thead><tr><th>Niryana candidate</th><th>Age</th><th>Marks</th><th>Preferred antardasas</th></tr></thead>
          <tbody>
            {h.niryana.map((c) => (
              <tr key={c.sign + c.age} className="best">
                <td>{c.sign}</td>
                <td className="short">{c.age}</td>
                <td>{c.marks.join(", ") || "—"}</td>
                <td>{c.preferredAds.join("; ") || "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

function SectionTables({ s }: { s: LongevitySection }) {
  return (
    <>
      {s.tables.map((t) => {
        const dropWeight = t.columns[t.columns.length - 1] === "Weight";
        const columns = dropWeight ? t.columns.slice(0, -1) : t.columns;
        const markCol = columns.findIndex((c) => /Chosen|Candidate|Preferred/.test(c));
        return (
          <div key={t.title}>
            <header className="pane-head sub"><h2>{t.title}</h2></header>
            <table className="points wrap">
              <thead><tr>{columns.map((c, i) => <th key={i}>{c}</th>)}</tr></thead>
              <tbody>
                {t.rows.map((r, i) => {
                  const weight = dropWeight ? r[r.length - 1] : "";
                  const cells = dropWeight ? r.slice(0, -1) : r;
                  const chosen = markCol >= 0 && cells[markCol] === "Yes";
                  const primary = weight === "primary" || chosen;
                  return (
                    <tr key={i} className={primary ? "best" : weight === "secondary" ? "longevity-secondary" : undefined}>
                      {cells.map((c, k) => <td key={k} className={c.length < 18 ? "short" : undefined}>{supOrd(c)}</td>)}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        );
      })}
    </>
  );
}

/** Every method of the texts on the birth chart, whatever mode is on: longevity belongs to the birth. Starlight has its own view. */
export function Longevity() {
  return useChart((s) => s.display.layout) === "starlight" ? <StarLongevity /> : <WindowsLongevity />;
}

function WindowsLongevity() {
  const chart = useChart((s) => s.birth)!;     // the chart in use (a cast one too)
  const [tab, setTab] = useSaved<string>("longevity", "summary");
  const q = useQuery({ queryKey: ["longevity", chart], queryFn: () => api.longevity(chart), placeholderData: (p) => p });
  return (
    <div className="right">
      <Loaded q={q}>{(sections) => {
        const s = sections.find((x) => x.id === tab) ?? sections[0];
        const headline = s.id === "summary" ? s.headline : undefined;
        return (<>
          <header className="lab-head">
            <OneRowTabs tabs={sections} value={s.id} onChange={setTab} label="Longevity methods" />
          </header>
          <section className="pane longevity">
            <header className="pane-head">
              <h2>{s.name}</h2>
              <span className="muted">{s.source}</span>
              {s.primary && <span className="longevity-chip primary-tag">Primary</span>}
              <CopyButton text={sectionText(s)} />
            </header>
            {headline ? <SummaryHero h={headline} onGo={setTab} /> : <p className="best-banner"><strong>{s.verdict}</strong></p>}
            <div className="scroll tall">
              <SectionTables s={s} />
              <div className="pad">
                {s.notes.map((n) => <p key={n} className="muted hint">{n}</p>)}
                <p className="muted hint">Classical calculations for study, not medical predictions. The text itself says longevity cannot be fixed before age 20 (BPHS 44.10-14).</p>
              </div>
            </div>
          </section>
        </>);
      }}</Loaded>
    </div>
  );
}

/* ---------- Starlight: the same methods, the results first and each one's working in a few rows, no notes ---------- */

const yr = (x: number) => String(Math.round(x * 10) / 10);
const ages = (a: Ages) => `${yr(a[0])}–${yr(a[1])}`;
const nth = (n: number) => `${n}${n % 100 >= 11 && n % 100 <= 13 ? "th" : ["th", "st", "nd", "rd"][n % 10] ?? "th"}`;
const MODE = ["movable", "fixed", "dual"];
const Verse = ({ v }: { v: string }) => <span className="lg-verse">{v}</span>;
/** The class's band on the age ruler: short to 32, medium to 64, long beyond (44.10-14; the user keeps three, supreme counted as long). */
const band = (c: string) => (/Very short|Short/.test(c) ? 0 : /Medium/.test(c) ? 1 : 2);
const BANDS: [number, number][] = [[0, 32], [32, 64], [64, 120]];
const TONE = ["short", "medium", "long"];     // the bars' colours: red, yellow, dark green
const at = (x: number) => `${Math.min(Math.max(x, 0), 120) / 1.2}%`;

const UNDER_MORE = ["marakas", "yogas"];     // the sub tabs always under "More"; the other six stay on the row

function StarLongevity() {
  const natal = useChart((s) => s.natal)!, chart = useChart((s) => s.birth)!;     // the chart in use (a cast one too); a death is the native's
  const [tab, setTab] = useSaved<string>("longevity", "summary");
  const q = useQuery({ queryKey: ["longevity", chart], queryFn: () => api.longevity(chart), placeholderData: (p) => p });
  return (
    <div className="right lab">
      <Loaded q={q}>{(sections) => {
        const s = sections.find((x) => x.id === tab) ?? sections[0];
        const d = s.data as never;
        const row = sections.filter((x) => !UNDER_MORE.includes(x.id)), more = sections.filter((x) => UNDER_MORE.includes(x.id));
        return (<>
          <header className="lab-head"><OneRowTabs tabs={row} more={more} pinned={new Set(row.map((x) => x.id))} value={s.id} onChange={setTab} label="Longevity methods" /></header>
          <div className={s.id === "summary" ? "star-stack lg lg-fit" : "star-stack lg"}>
            {s.id === "summary" ? <Summary h={s.headline!} go={setTab} birth={natal} />
              : s.id === "pairs" ? <Pairs d={d} />
              : s.id === "marakas" ? <Marakas d={d} />
              : s.id === "rudra" ? <Rudra d={d} natal={natal} />
              : s.id === "spans" ? <Spans d={d} />
              : s.id === "eighth" ? <Eighth d={d} />
              : s.id === "ashtakavarga" ? <AvYears d={d} />
              : <Rules d={d} />}
          </div>
        </>);
      }}</Loaded>
    </div>
  );
}

const bandOfYears = (y: number) => (y < 32 ? 0 : y < 64 ? 1 : 2);
/** Years from the birth to ``until`` (ms) — now, or the death: setUTCFullYear, not Date.UTC, so a year below 100 is not read as 19xx. */
function ageAt(b: Birth, until = Date.now()): number {
  const born = new Date(0);
  born.setUTCFullYear(b.year, b.month - 1, b.day);
  return (until - born.getTime() - (b.hour_local - b.tz_east_hours) * 3.6e6) / (365.2425 * 864e5);
}

/** The Summary's options: the Longevity group of Settings, changed in place; open stays open across a reload. */
function LongevityOptions() {
  const [open, setOpen] = useKept("lgOptions", false);
  const box = useRef<HTMLDivElement>(null);
  // a click anywhere outside (the button is inside, so it still toggles) or Escape closes it
  useEffect(() => {
    if (!open) return;
    const down = (e: PointerEvent) => { if (!box.current?.contains(e.target as Node)) setOpen(false); };
    const esc = (e: KeyboardEvent) => { if (e.key === "Escape") setOpen(false); };
    document.addEventListener("pointerdown", down, true);
    document.addEventListener("keydown", esc);
    return () => { document.removeEventListener("pointerdown", down, true); document.removeEventListener("keydown", esc); };
  }, [open, setOpen]);
  const client = useQueryClient();
  const schema = useQuery({ queryKey: ["settingsSchema"], queryFn: api.settingsSchema, staleTime: Infinity });
  const saved = useSettings();
  const options = schema.data?.find((g) => g.name === "Longevity")?.options ?? [];
  const set = (o: SettingOption, v: Choice["value"]) => {     // only what differs from the default is kept, as in the dialog
    const { [o.key]: _, ...rest } = saved;
    saveSettings(v === o.default ? rest : { ...rest, [o.key]: v });
    client.invalidateQueries();
  };
  return (
    <div className="lg-options" ref={box}>
      <button type="button" className="icon-btn" aria-label="Longevity options" aria-expanded={open} onClick={() => setOpen(!open)}><Icon name="spanner" /></button>
      {open && (
        <div className="lg-options-pop" role="dialog" aria-label="Longevity options">
          <p className="lg-options-note">These readings only make sense for someone who has lived past 20.</p>
          {options.map((o) => (
            <label key={o.key} className={o.kind === "bool" ? "lg-option check" : "lg-option"}>
              {o.kind === "bool" && <Control o={o} value={o.key in saved ? saved[o.key] : o.default} set={(v) => set(o, v)} />}
              <span>{o.label}</span>
              {o.kind !== "bool" && <Control o={o} value={o.key in saved ? saved[o.key] : o.default} set={(v) => set(o, v)} />}
            </label>
          ))}
        </div>
      )}
    </div>
  );
}

function Summary({ h, go, birth }: { h: LongevityHeadline; go: (tab: string) => void; birth: Birth }) {
  const died = useDeath(birth);   // a death gives the age it came at
  const mine = band(h.class);
  // only methods that give years are averaged: Pindayu, Amsayu and Nisargayu once, as the span the strongest picks (43.30-32);
  // the rules that give only a class (43.71-73) show their class, as votes, not years
  const others = h.methods.filter((m) => m.tab !== "spans" && m.years != null), count = others.length + 1;
  const average = (others.reduce((t, m) => t + m.years!, 0) + h.span.years) / count;
  const row = (m: LongevityHeadline["methods"][number]) => (
    <div key={m.name} className={m.chosen ? "lg-rule-row chosen" : "lg-rule-row"}>
      <button type="button" className="lg-method" onClick={() => go(m.tab)}>{m.name}<span aria-hidden="true">›</span></button>
      <div className="lg-track lg-lane">
        {[32, 64].map((t) => <span key={t} className="lg-sep" style={{ left: at(t) }} />)}
        {/* years: a bar from birth to them; a class without years: from birth to the end of its class */}
        <span className={`lg-fill ${TONE[band(m.class)]}`} style={{ left: 0, width: at(m.years ?? BANDS[band(m.class)][1]) }} />
      </div>
      <span className={m.agrees ? "lg-val" : "lg-val muted"}>{m.years == null ? m.class.split(" (")[0] : yr(m.years)}</span>
    </div>
  );
  const spans = h.methods.filter((m) => m.tab === "spans");
  return (<>
    <section className="pane lg-verdict">
      <strong className="lg-class">{["Short (Alpayu)", "Medium (Madhyayu)", "Long (Purnayu)"][bandOfYears(average)]}</strong>
      <span className="lg-years">Average of {count} methods: <strong>{yr(average)} years</strong></span>
      {died ? <span className="lg-years">Died at: <strong>{yr(ageAt(birth, died.at))} years</strong></span>
        : <span className="lg-years">Current age: <strong>{yr(ageAt(birth))} years</strong></span>}
      <LongevityOptions />
    </section>
    <section className="pane lg-ruler lg-grow" aria-label="Each method's span of life">
      <div className="lg-rule-row lg-axis"><span />
        <div className="lg-track">
          {["Short", "Medium", "Long"].map((name, i) => <span key={name} className={`lg-band-name${i === mine ? " mine" : ""}`} style={{ left: at(BANDS[i][0]), width: at(BANDS[i][1] - BANDS[i][0]) }}>{name}</span>)}
          {[0, 32, 64, 120].map((t) => <span key={t} className="lg-tick" style={{ left: at(t) }}>{t}</span>)}
        </div><span />
      </div>
      {h.methods.map((m) => m.tab !== "spans" ? row(m)
        : m === spans[0] && <div key="spans" className="lg-span-group" style={{ gridRow: `span ${spans.length}` }}>{spans.map(row)}</div>)}
    </section>
    <section className="pane lg-cards lg-grow">
      <div className="lg-card">
        <button type="button" className="link" onClick={() => go("marakas")}>Prime marakas</button>
        <div className="lg-chips">{h.primeMarakas.map((g) => <span key={g} className="lg-chip lg-big"><strong>{g}</strong></span>)}</div>
      </div>
      <div className="lg-card">
        <button type="button" className="link" onClick={() => go("rudra")}>Niryana Shoola</button>
        {h.niryana.length ? h.niryana.map((c) => (
          <p key={c.sign + c.age}><strong>{c.sign}</strong> <span className="muted">age {c.age.replace(" to ", "–")}</span>{" "}
            {c.marks.map((m) => <span key={m} className="lg-chip">{m}</span>)}
            {c.preferredAds.length > 0 && <span className="muted"> · antardasa {c.preferredAds.map((a) => a.split(" (")[0].split(" / ")[1]).join(", ")}</span>}</p>
        )) : <p className="muted">No period in the ages of this class</p>}
      </div>
      <div className="lg-card">
        <button type="button" className="link" onClick={() => go("marakas")}>Vimsottari of two prime marakas</button>
        <div className="lg-chips">{h.periods.length ? h.periods.map((p) => <span key={p.from} className="lg-chip"><strong>{p.md}/{p.ad}</strong> {ages(p.age)}</span>)
          : <span className="muted">None in these ages</span>}</div>
      </div>
      <div className="lg-card">
        <button type="button" className="link" onClick={() => go("yogas")}>Yogas and Arishta</button>
        <dl className="lg-counts">
          {([["Long life", h.yogas.long], ["Short life", h.yogas.short], ["Balarishta", h.yogas.balarishta], ["Antidotes", h.yogas.antidotes]] as const).map(([k, v]) => (
            <div key={k}><dt>{k}</dt><dd>{v}</dd></div>
          ))}
        </dl>
      </div>
    </section>
  </>);
}

const SHORT_BODY: Record<string, string> = { Saturn: "Sa", Moon: "Mo", Lagna: "As", "Hora Lagna": "HL" };
const Body = ({ b }: { b: LgBody }) => <><strong>{b.graha ?? SHORT_BODY[b.label] ?? b.label}</strong> {b.sign} <span className="muted">{MODE[b.mode]}</span></>;
// 43.33-40: the class of a pair by the two modes (movable, fixed, dual); 43.41-44: its years when 3, 2 or 1 pairs agree
const GRID = [["Long", "Medium", "Short"], ["Medium", "Short", "Long"], ["Short", "Long", "Medium"]];
const YEARS: Record<string, number[]> = { Long: [120, 108, 96], Medium: [80, 72, 64], Short: [32, 36, 40] };

function Pairs({ d }: { d: LongevityData["pairs"] }) {
  const here = (r: number, c: number) => d.pairs.map((p, i) => [p, i + 1] as const).filter(([p]) => p.a.mode === r && p.b.mode === c);
  const base = d.base.split(" (")[0], final = d.class.split(" (")[0];
  const saturnIn = d.saturn.startsWith("Contributor");     // three_pairs: Saturn, or a lord that is Saturn, among the contributors
  const sum = d.degrees.reduce((t, x) => t + x.deg, 0);
  return (<>
    <section className="pane">
      <table className="points"><thead><tr><th>#</th><th>Pair</th><th>First</th><th>Second</th><th>Class</th></tr></thead>
        <tbody>{d.pairs.map((p, i) => (
          <tr key={p.name} className={p.contributes ? "lg-on" : undefined}>
            <td>{i + 1}</td><td>{p.name}</td><td><Body b={p.a} /></td><td><Body b={p.b} /></td><td>{p.class.split(" (")[0]}</td>
          </tr>
        ))}</tbody>
      </table>
    </section>
    <section className="pane lg-pairs-work lg-grow">
      <table className="lg-matrix" aria-label="The class by the modes of the first and second, and its years when 3, 2 or 1 pairs agree">
        <thead><tr>
          <th className="lg-corner" />
          {MODE.map((m) => <th key={m}>{m}</th>)}
        </tr></thead>
        <tbody>{MODE.map((m, r) => (
          <tr key={m}><th>{m}</th>{MODE.map((_, c) => {
            const cls = GRID[r][c], placed = here(r, c), on = placed.some(([p]) => p.contributes);
            return (
              <td key={c} className={on ? "lg-on" : undefined}>
                <span className="lg-cell-head"><strong>{cls}</strong>{placed.map(([, n]) => <i key={n}>{n}</i>)}</span>
                <span className="lg-cell-years">{YEARS[cls].map((y, k) => <span key={k} className={on && 3 - k === d.votes ? "lg-pick" : undefined}>{y}</span>)}</span>
              </td>
            );
          })}</tr>
        ))}</tbody>
      </table>
      <ol className="lg-steps">
        <li><span>Class</span><div><strong>{base}</strong> · {d.decided.toLowerCase()}<Verse v="43.33-40" /></div></li>
        <li><span>Sa and Ju</span><div>{d.falls ? "Sa contributes: the class falls" : saturnIn ? "Sa contributes, but own, exalted or only with malefics" : "Sa does not contribute"}
          {" · "}{d.rises ? "Ju in the 1st or 7th with only benefics: the class rises" : "Ju: no change"}
          {final !== base && <> → <strong>{final}</strong></>}<Verse v="43.47-50" /></div></li>
        <li><span>Span</span><div>{d.years != null ? <><strong>{d.years}</strong> years: {final}, {d.votes} of 3 pairs</> : <strong>{d.span}</strong>}<Verse v="43.41-44" /></div></li>
        {d.rectified != null && d.years != null && <>
          <li><span>Average</span><div className="lg-math">
            {d.degrees.map((x, i) => <Fragment key={x.label}>{i > 0 && " + "}{x.graha ?? SHORT_BODY[x.label] ?? x.label} {x.deg.toFixed(2)}°</Fragment>)}
            {" "}= {sum.toFixed(2)}° ÷ {d.degrees.length} = <strong>{d.average.toFixed(2)}°</strong><Verse v="43.45-46" /></div></li>
          <li><span>Rectified</span><div className="lg-math">
            {yr(d.floor ?? 0)} + ({d.years} − {yr(d.floor ?? 0)}) × (1 − {d.average.toFixed(2)} ÷ 30) = <strong className="lg-result-years">{yr(d.rectified)} years</strong>
            <div className="lg-scale">
              <div className="lg-track"><span className="lg-band" style={{ left: 0, width: "100%" }} /><span className="lg-dot" style={{ left: `${(d.average / 30) * 100}%` }} /></div>
              <div className="lg-scale-ends"><span>0° · {d.years}</span><span>15°</span><span>30° · {yr(d.floor ?? 0)}</span></div>
            </div>
          </div></li>
        </>}
      </ol>
    </section>
  </>);
}

function Marakas({ d }: { d: LongevityData["marakas"] }) {
  const tier = (prime: boolean) => d.grahas.filter((g) => g.prime === prime);
  return (<>
    <section className="pane lg-tiers">
      {([[true, "Prime"], [false, "Can also kill"]] as const).map(([prime, name]) => (
        <table key={name} className="lg-marakas"><thead><tr className="lg-group"><th colSpan={2}>{name}</th></tr></thead>
          <tbody>{tier(prime).map((g) => (
            <tr key={g.graha}><td><strong>{g.graha}</strong></td>
              <td><span className="lg-chips">{g.reasons.map((r) => <span key={r.label} className="lg-chip">{supOrd(r.label)} <Verse v={r.verse} /></span>)}</span></td></tr>
          ))}
            {tier(prime).length === 0 && <tr><td colSpan={2} className="muted">None</td></tr>}
          </tbody>
        </table>
      ))}
    </section>
    <section className="pane">
      <dl className="lg-kv">
        <div><dt>Stars</dt><dd className="lg-chips">{d.stars.map((x) => (
          <span key={x.name} className={x.current ? "lg-chip lg-here" : "lg-chip"}>{x.name} {supOrd(nth(x.count))} · {x.nakshatra} <strong>{x.lord}</strong></span>
        ))}<Verse v="44.15-21" /></dd></div>
        {d.readings.map(([k, v]) => <div key={k}><dt>{supOrd(k)}</dt><dd>{supOrd(v)}</dd></div>)}
        <div><dt>Divisions</dt><dd>{d.divisions.map(([k, v]) => <span key={k} className="lg-pair">{supOrd(k)} <strong>{v}</strong></span>)}</dd></div>
      </dl>
    </section>
    <section className="pane">
      <table className="points"><thead><tr><th>Vimsottari MD / AD</th><th>From</th><th>To</th><th>Age ({d.window[0]}–{d.window[1]})</th></tr></thead>
        <tbody>{d.periods.map((p) => (
          <tr key={p.from} className={p.prime ? "lg-on" : undefined}><td><strong>{p.md}</strong> / <strong>{p.ad}</strong></td><td>{p.from}</td><td>{p.to}</td><td>{ages(p.age)}</td></tr>
        ))}
          {d.periods.length === 0 && <tr><td colSpan={4} className="muted">No period of two marakas in these ages</td></tr>}
        </tbody>
      </table>
    </section>
  </>);
}

function Rudra({ d, natal }: { d: LongevityData["rudra"]; natal: Birth }) {
  const [which, setWhich] = useKept("lgDasa", "niryana");
  const [openRow, setOpen] = useKept<string | null>("lgOpen", null);
  const dasa = d.dasas.find((x) => x.id === which) ?? d.dasas[0];
  const died = useDeath(natal), today = died?.date ?? new Date().toISOString().slice(0, 10);   // with a death, the periods it came in
  return (<>
    <section className="pane">
      <div className="lg-chips lg-who">
        {d.who.map((w) => <span key={w.name} className="lg-chip">{w.name} <strong>{w.graha ?? w.sign}</strong>{w.graha && ` ${w.sign}`} {supOrd(nth(w.house))}</span>)}
        <span className="lg-chip">Trishoola <strong>{d.trishoola.join(" ")}</strong></span>
        {d.rudraYoga.length > 0 && <span className="lg-chip">Rudra yoga on <strong>{d.rudraYoga.join(" ")}</strong></span>}
      </div>
    </section>
    <section className="pane">
      <header className="pane-head lg-dasa-head">
        <div className="seg" role="tablist" aria-label="Ayur dasa">
          {d.dasas.map((x) => <button key={x.id} role="tab" aria-selected={x.id === dasa.id} onClick={() => setWhich(x.id)}>{x.name}</button>)}
        </div>
      </header>
      <div className="scroll"><table className={died ? "points lg-dasa dasa-tree died" : "points lg-dasa dasa-tree"}>
        <thead><tr><th>Rasi</th><th>Age</th><th>From</th><th>To</th><th>Marks</th></tr></thead>
        <tbody>{dasa.periods.map((p) => {
          // the Dashas tab's tree: a click anywhere on a row opens its antardasas; what runs today (or ran at the death) is purple, the antardasa solid
          const key = `${dasa.id}:${p.from}`, open = openRow === key, running = p.from <= today && today < p.to;
          const toggle = () => setOpen(open ? null : key);
          return (
            <Fragment key={p.from}>
              <tr data-depth={0} style={{ "--level": 0, "--band": "var(--b0)" } as CSSProperties} tabIndex={0} aria-expanded={open}
                onClick={toggle} onKeyDown={(e) => { if (e.key === "Enter") toggle(); }}
                className={["split", running && "running", running && !open && "now", p.inWindow && "lg-window", p.guarded && "lg-guarded", p.candidate && "lg-cand"].filter(Boolean).join(" ")}>
                <td><span className="twisty" aria-hidden="true">{open ? "▾" : "▸"}</span>{p.sign}</td>
                <td>{ages(p.age)}</td><td>{p.from}</td><td>{p.to}</td>
                <td><span className="lg-chips">{p.marks.map((m) => <span key={m} className="lg-chip">{m}</span>)}{p.guarded && <span className="lg-chip">AK or Ju protects</span>}
                  {p.candidate && dasa.id === "varnada" && <span className="lg-chip lg-here">The limit</span>}</span></td>
              </tr>
              {open && p.ads.map((a) => {
                const now = a.from <= today && today < a.to;
                return (
                  <tr key={a.from} data-depth={1} style={{ "--level": 1, "--band": "var(--b1)" } as CSSProperties} className={[now && "running now", a.preferred && "lg-on"].filter(Boolean).join(" ") || undefined}>
                    <td>{a.sign}</td><td>{ages(a.age)}</td><td>{a.from}</td><td>{a.to}</td>
                    <td><span className="lg-chips">{a.fromDasa && <span className="lg-chip">{supOrd(nth(a.fromDasa))} from dasa</span>}{a.aspects && <span className="lg-chip">aspects D-9 of 8th lord</span>}</span></td>
                  </tr>
                );
              })}
            </Fragment>
          );
        })}</tbody>
      </table></div>
    </section>
  </>);
}

const pct = (x: number) => (x ? `−${Math.round(x * 100)}%` : "");

function Spans({ d }: { d: LongevityData["spans"] }) {
  const chosen = d.judges.find((j) => j.chosen)!.id;
  const [pick, setPick] = useKept<string | null>("lgSpan", null);
  const id = pick && d.spans[pick] ? pick : chosen;
  const span = d.spans[id], amsa = id === "amsa";
  return (<>
    <section className="pane lg-judges">
      {d.judges.map((j) => (
        <button key={j.id} type="button" aria-pressed={j.id === id} className={j.chosen ? "lg-judge chosen" : "lg-judge"} onClick={() => setPick(j.id)}>
          <span className="muted">{j.judge} {j.rupas.toFixed(2)} rupas · {Math.round(j.percent)}%</span>
          <strong>{j.span}</strong>
          <span>{yr(j.years)} years · {j.class.split(" (")[0]}</span>
        </button>
      ))}
    </section>
    <section className="pane">
      <div className="scroll"><table className="points lg-span">
        <thead><tr><th>Graha</th><th>Longitude</th><th>{amsa ? "Navamsa years" : "By arc"}</th>{amsa && <th>×</th>}<th>Visible half</th><th>Combust / enemy</th>{!amsa && <th>Malefic in lagna</th>}<th>Net</th></tr></thead>
        <tbody>
          {span.rows.map((r) => (
            <tr key={r.graha}>
              <td><strong>{r.graha}</strong></td><td>{r.lon}</td><td className="num">{r.gross.toFixed(2)}{r.full != null && <span className="muted"> /{r.full}</span>}</td>
              {amsa && <td>{r.factor > 1 ? `×${r.factor}` : ""}</td>}
              <td className="num">{pct(r.visible)}</td>
              <td>{r.combust ? "½ combust" : r.enemy ? "⅓ enemy sign" : ""}</td>
              {!amsa && <td className="num">{r.lagnaCut ? `−${r.lagnaCut.toFixed(2)}` : ""}</td>}
              <td className="num"><strong>{r.net.toFixed(2)}</strong></td>
            </tr>
          ))}
          <tr><td><strong>As</strong></td><td>{span.lagnaLon}</td><td className="muted" colSpan={4}>by {span.basis}</td><td className="num"><strong>{span.lagna.toFixed(2)}</strong></td></tr>
          <tr className="lg-total"><td colSpan={6}>Total</td><td className="num"><strong>{span.total.toFixed(2)}</strong></td></tr>
        </tbody>
      </table></div>
    </section>
  </>);
}

const tone = (c: string | null) => (c ?? "").split(" ")[0].toLowerCase();    // "Long (Purnayu)" -> long, as the ruler's bars
type Side = { name: string; value: string; n: number | null };
/** Two sides of a rule face to face, the tug bar under them: the left's share, the centre tick is even. */
function Duel({ k, a, b }: { k: string; a: Side; b: Side }) {
  const share = a.n != null && b.n != null && a.n + b.n > 0 ? a.n / (a.n + b.n) : null;
  const win = (x: Side, y: Side) => x.n != null && y.n != null && x.n > y.n ? "win" : undefined;
  return (
    <div className="lg-duel">
      <small>{k}</small>
      <div className="lg-duel-ends">
        <span className={win(a, b)}>{a.name}<b>{a.value}</b></span><em>vs</em><span className={win(b, a)}>{b.name}<b>{b.value}</b></span>
      </div>
      {share != null && <span className="lg-tug" aria-hidden="true"><i style={{ width: `${share * 100}%` }} /></span>}
    </div>
  );
}

function Eighth({ d }: { d: LongevityData["eighth"] }) {
  const p = d.placement;
  const pc = (x: number | null) => x == null ? "-" : `${Math.round(x)}%`;
  const outcome = d.outcome.startsWith("Supports") ? "long" : d.outcome.startsWith("Shortens") ? "short" : "medium";
  const rules = [
    { rule: "Lagna lord vs 8th lord", v: "43.71-72", cls: tone(p.class), body: <>
      <Duel k="Shadbala" a={{ name: p.lagnaLord, value: pc(p.lagnaBala), n: p.lagnaBala }} b={{ name: p.eighthLord, value: pc(p.eighthBala), n: p.eighthBala }} />
      <p className="lg-e-then">{p.stronger} is in the <strong>{supOrd(nth(p.house))} bhava</strong>, a <strong>{p.kind.toLowerCase()}</strong></p></> },
    { rule: "Lagna lord vs Su", v: "43.72-73", cls: tone(d.sun.class), body:
      <div className="lg-duel"><small>{d.sun.lord} towards Su</small><strong className="lg-e-big">{d.sun.class ? d.sun.relation : "Is the Sun"}</strong></div> },
    { rule: "Life vs death", v: "44.2-5", cls: outcome, word: outcome === "medium" ? "Mixed" : undefined, body: <>
      <Duel k="Bhava Bala" a={{ name: "3rd + 8th", value: d.life.toFixed(2), n: d.life }} b={{ name: "2nd + 7th", value: d.death.toFixed(2), n: d.death }} />
      {d.lifeLords != null && d.deathLords != null && <Duel k="Their lords' Shadbala, average"
        a={{ name: "Life", value: pc(d.lifeLords), n: d.lifeLords }} b={{ name: "Death", value: pc(d.deathLords), n: d.deathLords }} />}</> },
  ];
  return (<>
    <section className="pane lg-eighth">
      {rules.map((r) => (
        <div key={r.rule} className="lg-e-col">
          <span className="lg-e-rule">{r.rule}<Verse v={r.v} /></span>
          {r.body}
          <span className={`lg-e-gives ${r.cls}`}>{r.word ?? (r.cls ? r.cls[0].toUpperCase() + r.cls.slice(1) : "No reading")}</span>
        </div>
      ))}
    </section>
    <section className="pane lg-snug">
      <div className="scroll"><table className="points">
        <thead><tr><th>Bhava</th><th>Sign</th><th>Lord</th><th>Lord in</th><th>Lord's bala</th><th>Bhava bala</th><th>Occupants</th><th>Aspected by</th><th>SAV</th></tr></thead>
        <tbody>{[...d.houses].sort((a, b) => Number(b.life) - Number(a.life) || a.house - b.house).map((h) => (
          <tr key={h.house} className={h.life ? "lg-on" : undefined}>
            <td><strong>{supOrd(nth(h.house))}</strong> <span className="muted">{h.life ? "life" : "death"}</span></td><td>{h.sign}</td><td>{h.lord}</td><td>{supOrd(nth(h.lordIn))}</td>
            <td className="num">{h.lordBala != null && <span className="cell-meter">{Math.round(h.lordBala)}%<Meter t={(h.lordBala - 100) / 50 + .5} fill={h.lordBala / 200} mark={.5} /></span>}</td>
            <td className="num"><span className="cell-meter">{h.rupas.toFixed(2)}<Meter t={(h.rupas - 7) / 4 + .5} fill={h.rupas / 14} mark={.5} /></span></td>
            <td>{h.occupants.join(" ")}</td><td>{h.aspects.join(" ")}</td><td className="num">{h.sav}</td>
          </tr>
        ))}</tbody>
      </table></div>
    </section>
  </>);
}

const RASIS = ["Ar", "Ta", "Ge", "Cn", "Le", "Vi", "Li", "Sc", "Sg", "Cp", "Aq", "Pi"];

function AvYears({ d }: { d: LongevityData["ashtakavarga"] }) {
  const [a, b, total] = d.distress, s = d.saturn;
  return (<>
    <section className="pane">
      <dl className="lg-kv">
        <div><dt>Years</dt><dd><strong>{d.years.toFixed(2)}</strong> · {d.class}<Verse v="71.1-4" /></dd></div>
        <div><dt>Ages of distress</dt><dd><strong>{a}</strong>, <strong>{b}</strong> and <strong>{total}</strong> <span className="muted">(rekhas of Sa's ashtakavarga from the lagna to Sa, back, and both)</span><Verse v="70.37-40" /></dd></div>
        <div><dt>Saturn's transits</dt><dd>{s.product ? <>{s.pinda} × {s.rekhas} = {s.product} → <strong>{s.stars.join(", ")}</strong> · <strong>{s.signs.join(" ")}</strong></>
          : <span className="muted">No rekhas in the 8th from Sa</span>}<Verse v="70.41-42" /></dd></div>
      </dl>
    </section>
    <section className="pane">
      <div className="scroll"><table className="points lg-av">
        <thead><tr><th />{RASIS.map((r) => <th key={r}>{r}</th>)}<th>Years</th></tr></thead>
        <tbody>{d.rows.map((r) => (
          <tr key={r.name}><td><strong>{r.name}</strong></td>{r.rekhas.map((x, i) => <td key={i} className={x >= 5 ? "num lg-gives" : "num muted"}>{x}</td>)}<td className="num">{r.years.toFixed(2)}</td></tr>
        ))}
          <tr className="lg-total"><td colSpan={13}>Half of the sum</td><td className="num"><strong>{d.years.toFixed(2)}</strong></td></tr>
        </tbody>
      </table></div>
    </section>
  </>);
}

/** As the Yogas tab: the groups as filters with their counts, each rule present a card; "All rules" adds the absent ones, faded. */
function Rules({ d }: { d: LongevityData["yogas"] }) {
  const [group, setGroup] = useKept("lgRuleGroup", "");
  const [all, setAll] = useKept("lgRulesAll", false);
  const shown = d.groups.filter((g) => !group || g.id === group);
  const count = (g: (typeof d.groups)[number]) => g.rules.filter((r) => r.present).length;
  return (
    <section className="pane star-yogas">
      <header className="pane-head">
        <span className="sy-legend" role="group" aria-label="Filter by kind of rule">
          {d.groups.map((g) => (
            <button key={g.id} type="button" aria-pressed={group === g.id} onClick={() => setGroup(group === g.id ? "" : g.id)}>{g.name} <strong>{count(g)}</strong></button>
          ))}
          <button type="button" className="lg-all" aria-pressed={all} onClick={() => setAll(!all)}>All rules</button>
        </span>
      </header>
      <div className="scroll tall">
        {shown.map((g) => {
          const rules = all ? [...g.rules].sort((a, b) => Number(b.present) - Number(a.present)) : g.rules.filter((r) => r.present);
          return (
            <section key={g.id} className="sy-group">
              <h3>{g.name} <span className="muted">{count(g)}</span></h3>
              {rules.length > 0 ? <ul className="sy-cards">{rules.map((r, i) => (
                <li key={i} className={r.present ? "sy-card" : "sy-card lg-absent"}>
                  <header><h4>{r.gives}</h4><i className={r.present ? "sy-basis rasi" : "sy-basis lg-off"}>{r.verse}</i></header>
                  <p className="sy-rule">{supOrd(r.condition)}</p>
                </li>
              ))}</ul> : <p className="empty small">None in this chart.</p>}
            </section>
          );
        })}
      </div>
    </section>
  );
}
