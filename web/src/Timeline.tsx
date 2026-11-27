import { useQuery } from "@tanstack/react-query";
import { useLayoutEffect, useRef, useState } from "react";
import { api, type SkyPlace, type TimeSpan, type TimelineYear } from "./api";
import { useKept, useSaved } from "./hooks";
import { Icon } from "./Icons";
import { useMenu } from "./Menu";
import { useChart } from "./store";
import { SubTabs } from "./ui";

const ORDER = ["Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Rahu", "Ketu", "Uranus", "Neptune", "Pluto"];   // the strip, fast to slow
const PICKS = ["Moon", ...ORDER];   // the right-click list; the Moon only if asked for, as it would swamp the year
const FIRST = ORDER.slice(0, ORDER.indexOf("Ketu") + 1);   // Sun to Ketu, filling the page
const NINE = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"];
const FULL = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"];
const ABBR = ["Ar", "Ta", "Ge", "Cn", "Le", "Vi", "Li", "Sc", "Sg", "Cp", "Aq", "Pi"];
const ab = (sign: string) => ABBR[SIGNS.indexOf(sign)];
const two = (graha: string) => graha.slice(0, 2);   // Ju, Ke: a capital and a small letter
const LANES = ["18%", "50%", "82%"];   // a row's top, middle and bottom: a dot goes in the first with room
const CH = 6.6;                        // px a label's letter takes, near enough to keep labels apart
const VIEWS = [{ id: "timeline", name: "Timeline" }, { id: "tables", name: "Tables" }] as const;

/** "YYYY-MM-DDTHH:MM" in the chart's zone, as a plain number to place on the year (no zone of the browser's in it). */
const ms = (s: string) => { const [y, m, d, h, mi] = s.split(/[-T:]/).map(Number); return Date.UTC(y, m - 1, d, h, mi); };
const date = (s: string) => { const [, m, d] = s.split(/[-T]/).map(Number); return `${d} ${MONTHS[m - 1]}`; };
const when = (s: string) => `${date(s)}, ${s.slice(11)}`;
// the year stops at its own ends: a span that began before it shows 1 Jan, one that runs on shows 31 Dec
const from = (t: TimeSpan) => (t.from ? date(t.from) : "1 Jan");
const to = (t: TimeSpan) => (t.to ? date(t.to) : "31 Dec");
const dms = (deg: number) => `${Math.floor(deg)}°${String(Math.floor((deg % 1) * 60)).padStart(2, "0")}′`;
const place = (p: SkyPlace) => `${ab(p.sign)} ${dms(p.deg)} · ${p.nakshatra}`;
const Gandanta = ({ on }: { on: boolean }) => (on ? <span className="tl-badge">Gandanta</span> : null);

/** The Timeline tab: a calendar year of the sky, from the Barhaspatya samvatsara to every graha's signs, retrogressions,
 *  gandanta passages, combustion, conjunctions and eclipses. Times are in the open chart's zone, with its ayanamsa. */
export function Timeline() {
  const natal = useChart((s) => s.birth)!;     // the chart in use: its zone and place
  const [year, setYear] = useKept("timeline.year", new Date().getFullYear());
  const q = useQuery({ queryKey: ["timeline", natal, year], queryFn: () => api.timeline(natal, year), placeholderData: (p) => p });
  const d = q.data;
  const y0 = `${year}-01-01T00:00`, y1 = `${year + 1}-01-01T00:00`;
  const [view, setView] = useSaved<(typeof VIEWS)[number]["id"]>("timeline", "timeline");
  const [month, setMonth] = useKept<number | null>("timeline.month", null);   // a month zoomed into, or the whole year
  const [bodies, setBodies] = useKept("timeline.bodies", FIRST);
  const { open, node } = useMenu();
  const items = (on: string[], at: { clientX: number; clientY: number }) => PICKS.map((b) => ({
    label: b, checked: on.includes(b), keep: true,
    onClick: () => { const next = on.includes(b) ? on.filter((x) => x !== b) : [...on, b]; setBodies(next); open(at, items(next, at), "Bodies shown"); },
  }));
  return (
    <section className="pane tl">
      <header className="pane-head tl-head">
        <SubTabs tabs={[...VIEWS]} value={view} onChange={setView} label="Timeline views" />
        <span className="tl-year">
          <button aria-label="Previous year" data-tip="Previous year" onClick={() => setYear(year - 1)}><Icon name="prev" /></button>
          <input type="number" aria-label="Year" value={year} min={1800} max={2400} onChange={(e) => e.target.value && setYear(Number(e.target.value))} />
          <button aria-label="Next year" data-tip="Next year" onClick={() => setYear(year + 1)}><Icon name="next" /></button>
        </span>
        {d && d.year === year && (
          <span className="tl-samvat" data-tip="Barhaspatya samvatsara: a 30° step of Jupiter's mean motion (Surya Siddhanta)">
            {d.samvatsaras.map((s) => (
              <span key={s.number}><b>{s.name}</b> <span className="muted">({s.number}) {s.start < y0 ? `until ${date(s.end)}` : s.end >= y1 ? `from ${date(s.start)}` : `${date(s.start)} – ${date(s.end)}`}</span></span>
            ))}
          </span>
        )}
        {q.isFetching && <span className="muted">Calculating…</span>}
        {view === "timeline" && <span className="tl-legend muted">
          {month !== null && <button className="tl-back" aria-label={`Back to ${year}`} data-tip={`Back to ${year}`} onClick={() => setMonth(null)}><Icon name="undo" />Back</button>}
          <span><i className="tl-key retro" /> Retrograde</span><span data-tip="The last 3°20′ of a water sign and the first 3°20′ of the fire sign after it: Cancer 26°40′ – Leo 3°20′, Scorpio 26°40′ – Sagittarius 3°20′, Pisces 26°40′ – Aries 3°20′"><i className="tl-key gandanta" /> Gandanta (26°40′ – 3°20′)</span>
          <span><i className="tl-key combust" /><i className="tl-key conj sun" /> Combust</span><span><i className="tl-key conj" /> Conjunction</span><span><i className="tl-key solar" /> Solar</span>
          <span><i className="tl-key lunar" /> Lunar</span>
        </span>}
      </header>
      {q.isError ? <p role="alert" className="error banner">{q.error.message}</p>
        : !d ? <p className="empty">Calculating…</p>
          : (
            <div className="tl-body" onContextMenu={view === "timeline" ? (e) => { e.preventDefault(); const at = { clientX: e.clientX, clientY: e.clientY }; open(at, items(bodies, at), "Bodies shown"); } : undefined}>
              {view === "timeline" ? <Strip d={d} month={month} onMonth={setMonth} bodies={bodies} /> : (
                <div className="tl-lists">
                  <Conjunctions d={d} />
                  <Signs d={d} />
                  <Retrogressions d={d} />
                  <Gandantas d={d} />
                </div>
              )}
            </div>
          )}
      {node}
    </section>
  );
}

/** The year at a glance: the eclipses on a row of their own, then a row per graha with its signs as bands, retrogression
 *  shading the box in purple, gandanta over them in red, and the major conjunctions as dots. Nothing goes past 31 December. */
function Strip({ d, month, onMonth, bodies }: { d: TimelineYear; month: number | null; onMonth: (m: number) => void; bodies: string[] }) {
  const ref = useRef<HTMLDivElement>(null);
  const [w, setW] = useState(1200);   // a track's width in px, to keep labels from running into each other
  useLayoutEffect(() => {
    setW(ref.current!.clientWidth);
    const ro = new ResizeObserver(([e]) => setW(e.contentRect.width));
    ro.observe(ref.current!);
    return () => ro.disconnect();
  }, []);
  const zoomed = month !== null;
  const y0 = Date.UTC(d.year, month ?? 0, 1), y1 = month === null ? Date.UTC(d.year + 1, 0, 1) : Date.UTC(d.year, month + 1, 1);
  // only what touches the shown range; null ends run past the year
  const shown = (t: TimeSpan) => (!t.from || ms(t.from) < y1) && (!t.to || ms(t.to) > y0);
  const at = (s: string) => ms(s) >= y0 && ms(s) < y1;
  const tick = (t: number) => `${((t - y0) / (y1 - y0)) * 100}%`;
  const x = (s: string | null, end: boolean) => (s ? Math.min(100, Math.max(0, ((ms(s) - y0) / (y1 - y0)) * 100)) : end ? 100 : 0);
  const span = (t: TimeSpan) => { const a = x(t.from, false); return { left: `${a}%`, width: `${x(t.to, true) - a}%` }; };
  const now = new Date(), today = ((Date.UTC(now.getFullYear(), now.getMonth(), now.getDate(), now.getHours()) - y0) / (y1 - y0)) * 100;
  return (
    <div className="tl-strip">
      <div className="tl-row tl-months">
        <span />
        <div className="tl-track" ref={ref}>{!zoomed
          ? MONTHS.map((m, i) => <button key={m} style={{ left: tick(Date.UTC(d.year, i, 1)), width: `calc(${tick(Date.UTC(d.year, i + 1, 1))} - ${tick(Date.UTC(d.year, i, 1))})` }}
              aria-label={`Zoom into ${FULL[i]}`} onClick={() => onMonth(i)}>{FULL[i]}</button>)
          : Array.from({ length: Math.round((y1 - y0) / 864e5) }, (_, i) => <span key={i} style={{ left: tick(y0 + i * 864e5) }}>{i + 1}</span>)}</div>
      </div>
      <div className="tl-row tl-eclipses">
        <span className="tl-name">Eclipses</span>
        <div className="tl-track">
          {d.eclipses.filter((e) => at(e.at)).map((e) => {
            const label = zoomed ? `${e.type} ${e.kind} eclipse, ${when(e.at)} · ${place(e)}, with ${e.node}` : date(e.at);
            const flip = (x(e.at, false) * w) / 100 + label.length * CH + 20 > w;
            return (
            <span key={e.at} className={`tl-eclipse ${e.kind}${flip ? " flip" : ""}`} style={{ left: `${x(e.at, false)}%` }}
              data-tip={`${e.type} ${e.kind} eclipse, ${when(e.at)}, ${place(e)}, with ${e.node}${e.gandanta ? ", in gandanta" : ""}`}>
              <i />{label}
            </span>
            );
          })}
        </div>
      </div>
      {PICKS.filter((b) => bodies.includes(b)).map((b) => {
        // each dot takes the first of the row's three lanes free of bars, sign names and other labels; px spans per lane
        const px = (s: string | null, end: boolean) => (x(s, end) * w) / 100;
        const busy: [number, number][][] = [
          [...(d.gandanta[b] ?? []), ...(d.combustion[b] ?? [])].filter(shown).map((t) => [px(t.from, false), px(t.to, true)]),
          d.signs[b].filter(shown).map((s) => [px(s.from, false), px(s.from, false) + 26]),
          [],   // retrogression fills the whole box now, so it blocks no lane
        ];
        const conj = d.conjunctions.filter((c) => c.major && c.bodies.includes(b) && at(c.at)).map((c) => {
          const pos = x(c.at, false), p = (pos * w) / 100;
          const label = zoomed ? `${c.bodies.map(two).join("–")} conjunction, ${when(c.at)} · ${place(c)}` : two(c.bodies.find((o) => o !== b)!);
          const len = label.length * CH + 12, flip = p + len > w;   // near the right edge the name goes to the dot's left
          const a = flip ? p - len : p - 7, z = flip ? p + 7 : p + len;
          const k = [0, 1, 2].find((k) => busy[k].every(([q0, q1]) => z <= q0 || a >= q1)) ?? 1;
          busy[k].push([a, z]);
          return { c, pos, k, label, flip };
        });
        return (
        <div className="tl-row" key={b}>
          <span className="tl-name">{b}</span>
          <div className="tl-track">
            {d.signs[b].filter(shown).map((s, i) => (
              <span key={i} className={`tl-sign s${SIGNS.indexOf(s.sign) % 2}`} style={span(s)} data-tip={`${b} in ${s.sign}${s.retrograde ? " (entered retrograde)" : ""}: ${from(s)} – ${to(s)}`}>{ab(s.sign)}</span>
            ))}
            {(d.retrograde[b] ?? []).filter(shown).map((r, i) => <span key={`r${i}`} className="tl-retro" style={span(r)} data-tip={`${b} retrograde: ${from(r)} – ${to(r)}`} />)}
            {(d.gandanta[b] ?? []).filter(shown).map((g, i) => <span key={`g${i}`} className="tl-gandanta" style={span(g)} data-tip={`${b} in ${g.where} gandanta: ${from(g)} – ${to(g)}`} />)}
            {(d.combustion[b] ?? []).filter(shown).map((c, i) => <span key={`c${i}`} className="tl-combust" style={span(c)} data-tip={`${b} combust: ${from(c)} – ${to(c)}`} />)}
            {conj.map(({ c, pos, k, label, flip }) => (
              <span key={c.at + c.bodies} className={`tl-conj${c.gandanta ? " in-gandanta" : c.bodies.includes("Sun") ? " sun" : ""}${flip ? " flip" : ""}`} style={{ left: `${pos}%`, top: LANES[k] }}
                data-tip={`${c.bodies.join(" – ")} conjunction, ${when(c.at)}, ${place(c)}${c.gandanta ? ", in gandanta" : ""}`}>
                <b>{label}</b>
              </span>
            ))}
          </div>
        </div>
        );
      })}
      <div className="tl-lines" aria-hidden>
        {today >= 0 && today <= 100 && <span className="tl-line today" style={{ left: `${today}%` }}><b>Now</b></span>}
      </div>
    </div>
  );
}

/** Conjunctions, eclipses or combustion, a button for each. */
function Conjunctions({ d }: { d: TimelineYear }) {
  const [all, setAll] = useKept("timeline.allConj", false);
  const [show, setShow] = useKept<"conj" | "eclipses" | "combust">("timeline.events", "conj");
  const combust = ORDER.flatMap((b) => (d.combustion[b] ?? []).map((c) => ({ b, ...c })));
  return (
    <section className="tl-card">
      <header>
        <div className="tl-grahas" role="tablist" aria-label="Events">
          <button role="tab" aria-selected={show === "conj"} onClick={() => setShow("conj")}>Conjunctions</button>
          <button role="tab" aria-selected={show === "eclipses"} onClick={() => setShow("eclipses")}>Eclipses</button>
          <button role="tab" aria-selected={show === "combust"} onClick={() => setShow("combust")}>Combustion</button>
        </div>
        {show === "conj" && <label className="check"><input type="checkbox" checked={all} onChange={(e) => setAll(e.target.checked)} /> All {d.conjunctions.length}, not only the major</label>}
      </header>
      <div className="tl-scroll">
        {show === "conj" ? (
          <table className="tl-table"><tbody>{d.conjunctions.filter((c) => all || c.major).map((c) => (
            <tr key={c.at + c.bodies}><td className="tl-when">{when(c.at)}</td><td><b>{c.bodies.join(" – ")}</b></td><td>{place(c)} <Gandanta on={c.gandanta} /></td></tr>
          ))}</tbody></table>
        ) : show === "combust" ? (
          <table className="tl-table"><tbody>{combust.map((c) => (
            <tr key={c.b + c.from}><td><b>{c.b}</b></td><td className="tl-when">{from(c)} – {to(c)}</td><td>{c.sign_from === c.sign_to ? `in ${ab(c.sign_from)}` : `${ab(c.sign_from)} → ${ab(c.sign_to)}`}</td></tr>
          ))}</tbody></table>
        ) : (
          <table className="tl-table"><tbody>{d.eclipses.map((e) => (
            <tr key={e.at}><td className="tl-when">{when(e.at)}</td><td><b className="cap"><i className={`tl-key ${e.kind}`} /> {e.type} {e.kind}</b></td><td>{place(e)}, with {e.node} <Gandanta on={e.gandanta} /></td></tr>
          ))}</tbody></table>
        )}
      </div>
    </section>
  );
}

/** One graha's signs through the year; the graha buttons as two letters so they stay on one line. */
function Signs({ d }: { d: TimelineYear }) {
  const [graha, setGraha] = useKept("timeline.graha", "Sun");
  return (
    <section className="tl-card">
      <header><h3>Sign changes</h3>
        <div className="tl-grahas" role="tablist" aria-label="Graha">
          {NINE.map((g) => <button key={g} role="tab" aria-label={g} data-tip={g} aria-selected={graha === g} onClick={() => setGraha(g)}>{g.slice(0, 2)}</button>)}
        </div>
      </header>
      <div className="tl-scroll">
        <table className="tl-table"><tbody>{(d.signs[graha] ?? []).map((s) => (
          <tr key={s.from ?? "start"}><td><b data-tip={s.sign}>{ab(s.sign)}</b>{s.retrograde && <span className="tl-r" data-tip="Entered retrograde">(R)</span>}</td>
            <td className="tl-when">{s.from ? when(s.from) : "1 Jan"}</td><td className="tl-when">{s.to ? when(s.to) : "31 Dec"}</td></tr>
        ))}</tbody></table>
      </div>
    </section>
  );
}

function Retrogressions({ d }: { d: TimelineYear }) {
  const rows = ORDER.flatMap((b) => (d.retrograde[b] ?? []).map((r) => ({ b, ...r })));
  return (
    <section className="tl-card">
      <header><h3>Retrogressions</h3></header>
      <div className="tl-scroll">
        <table className="tl-table"><tbody>{rows.map((r) => (
          <tr key={r.b + r.from}><td><b>{r.b}</b></td><td className="tl-when">{from(r)} – {to(r)}</td><td>{r.sign_from === r.sign_to && r.nak_from === r.nak_to ? `in ${ab(r.sign_from)} · ${r.nak_from}` : `${ab(r.sign_from)} · ${r.nak_from} → ${ab(r.sign_to)} · ${r.nak_to}`}</td></tr>
        ))}</tbody></table>
      </div>
    </section>
  );
}

function Gandantas({ d }: { d: TimelineYear }) {
  const rows = ORDER.flatMap((b) => (d.gandanta[b] ?? []).map((g) => ({ b, ...g })));
  return (
    <section className="tl-card">
      <header><h3>Gandanta</h3><span className="muted">Cancer 26°40′ – Leo 3°20′, and the same in Scorpio – Sagittarius, Pisces – Aries</span></header>
      <div className="tl-scroll">
        {rows.length ? <table className="tl-table"><tbody>{rows.map((g) => (
          <tr key={g.b + g.from}><td><b>{g.b}</b></td><td className="tl-when">{from(g)} – {to(g)}</td><td>{g.where.split("–").map(ab).join("–")} junction</td></tr>
        ))}</tbody></table> : <p className="muted pad">No graha crosses a gandanta this year.</p>}
      </div>
    </section>
  );
}
