import { useEffect, useRef } from "react";
import { useQuery } from "@tanstack/react-query";
import { api, type Birth, type Festival, type FestivalDate, type FestivalDay, type FestivalTime, type LunarSystem, type MuhurtaEvent, type MuhurtaJudged } from "./api";
import { useKept, useSaved } from "./hooks";
import { clockText, type Clock } from "./muhurtaMath";
import { useChart } from "./store";
import { Loaded } from "./ui";

export type ListMode = "ceremonies" | "festivals";
export interface Count { text: string; title?: string }
const WEEK = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
const grade = (score: number | null) => (score === null ? "none" : score >= 85 ? "excellent" : score >= 72 ? "good" : "fair");
const GRADE_TEXT = { excellent: "Excellent", good: "Good", fair: "Fair", none: "" };
const words = (date: string, o: Intl.DateTimeFormatOptions) => new Date(date + "T00:00:00Z").toLocaleDateString("en-GB", { ...o, timeZone: "UTC" });
const dayLong = (date: string) => words(date, { weekday: "long", day: "numeric", month: "long" });
const dayMonth = (date: string) => words(date, { day: "numeric", month: "short" });
const plural = (n: number, one: string) => `${n} ${one}${n === 1 ? "" : "s"}`;

/** The month's observances as {f, d} in date order (within a day, in the list's group order). */
const ofMonth = (items: Festival[], month: string) =>
  items.flatMap((f) => f.dates.filter((d) => d.date.startsWith(month)).map((d) => ({ f, d }))).sort((a, b) => a.d.date.localeCompare(b.d.date));

function EventList({ events, value, onChange }: { events: MuhurtaEvent[]; value: string; onChange: (id: string) => void }) {
  const groups = [...new Set(events.map((e) => e.group))];
  return (
    <nav className="mu-events-list" aria-label="Event">
      {groups.map((g) => (
        <div key={g} className="mu-event-group">
          <h4>{g}</h4>
          <ul>
            {events.filter((e) => e.group === g).map((e) => (
              <li key={e.id}><button type="button" aria-pressed={e.id === value} onClick={() => onChange(e.id)}>{e.name}</button></li>
            ))}
          </ul>
        </div>
      ))}
    </nav>
  );
}

/** The calendar's festivals by group, each with when it falls in the year. */
function FestivalList({ items, value, onChange }: { items: Festival[]; value: string; onChange: (f: Festival) => void }) {
  const groups = [...new Set(items.map((f) => f.group))];
  // the picked festival scrolls into view: after a refresh, the Now button, or a click on the calendar
  const nav = useRef<HTMLElement>(null);
  useEffect(() => { nav.current?.querySelector('[aria-pressed="true"]')?.scrollIntoView({ block: "center", inline: "nearest" }); }, [value]);
  return (
    <nav className="mu-events-list" aria-label="Festival" ref={nav}>
      {groups.map((g) => (
        <div key={g} className="mu-event-group">
          <h4>{g}</h4>
          <ul>
            {items.filter((f) => f.group === g).map((f) => (
              <li key={f.id}>
                <button type="button" className="fe-item" aria-pressed={f.id === value} onClick={() => onChange(f)}>
                  <span>{f.name}</span>
                  <span className="fe-when">{f.dates.length > 2 ? plural(f.dates.length, "day") : f.dates.map((d) => dayMonth(d.date)).join(", ")}</span>
                </button>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </nav>
  );
}

function DayDetail({ d, clock, lunar, onShow, next, onPick, count }: { d: MuhurtaJudged; clock: Clock; lunar: LunarSystem; onShow: (day: string, start: string) => void; next: MuhurtaJudged | undefined; onPick: (date: string) => void; count: Count }) {
  // with no sunrise at hand here the Vedic clock reads as 24 hour
  const t = (iso: string) => clockText(iso, d.date, d.date + "T06:00:00", clock === "vedic" ? "24" : clock);
  return (
    <section className="mu-detail" aria-live="polite">
      <h3><span>{dayLong(d.date)}, <span className="mu-detail-month">{d.month[lunar]} Maasa{d.month.adhika && lunar !== "saura" ? " (Adhika)" : ""}{d.month.kshaya && lunar === "amanta" ? ` (Kshaya ${d.month.kshaya})` : ""}</span></span> <span className="mu-count" title={count.title}>{count.text}</span></h3>
      <p className="muted">{d.tithi} at sunrise, Moon in {d.nakshatra}</p>
      {d.reason ? (
        <div className="mu-reject">
          <p>{d.reason}.</p>
          {next && <button type="button" onClick={() => onPick(next.date)}>Next good day: {dayLong(next.date)}</button>}
        </div>
      ) : (
        <ol className="mu-windows">
          {d.windows.map((w, i) => (
            <li key={i} className={`mu-window ${grade(w.score)}`}>
              <div className="mu-window-head">
                <span className="mu-window-time">{t(w.start)} – {t(w.end)}</span>
                <span className="mu-score" aria-label={`${GRADE_TEXT[grade(w.score)]}, score ${w.score} of 100`}><span className="mu-meter"><i style={{ width: `${w.score}%` }} /></span>{GRADE_TEXT[grade(w.score)]} {w.score}</span>
              </div>
              <ul className="mu-chips">
                {w.reasons.map((r, k) => <li key={k} className={r.good ? "good" : "bad"}>{r.label}</li>)}
              </ul>
              <button type="button" className="mu-quiet" onClick={() => onShow(d.date, w.start)}>Show on the day dial</button>
            </li>
          ))}
        </ol>
      )}
    </section>
  );
}

/** A time of a festival date as the clock reads it: one moment, or a range; another day than ``date`` carries "+1". */
function timeText(x: FestivalTime | { from: string; to: string }, date: string, clock: Clock) {
  const t = (iso: string) => clockText(iso, date, date + "T06:00:00", clock === "vedic" ? "24" : clock);
  return x.from === x.to ? t(x.from) : `${t(x.from)} – ${t(x.to)}`;
}
const stamp = (iso: string, clock: Clock) => `${dayMonth(iso.slice(0, 10))} ${clockText(iso, iso.slice(0, 10), iso.slice(0, 10) + "T06:00:00", clock === "vedic" ? "24" : clock)}`;
/** Where the day dial should point for a date: the deciding time, or sunrise for one before it. */
const dialAt = (d: FestivalDate) => (d.at && d.at.label !== "Arunodaya" && d.at.from.startsWith(d.date) ? d.at.from : d.date + "T12:00:00");

/** One festival on a date: its rule, its note and the times that decided the day. */
function FestivalCard({ f, d, clock, onShow, onPick }: { f: Festival; d: FestivalDate; clock: Clock; onShow: (day: string, start: string) => void; onPick?: () => void }) {
  return (
    <div className="mu-window fe-card">
      <div className="mu-window-head">
        <span className="mu-window-time">{onPick ? <button type="button" className="fe-link" onClick={onPick}>{f.name}</button> : f.name}</span>
        <span className="mu-score">{f.group}</span>
      </div>
      <p className="fe-criteria">{f.criteria}.</p>
      {f.note && <p className="muted fe-note">{f.note}</p>}
      {d.span && <p className="muted">{d.span.label}: {stamp(d.span.from, clock)} to {stamp(d.span.to, clock)}</p>}
      {d.at && <p>{d.at.label}: {timeText(d.at, d.date, clock)}</p>}
      {d.parana && <p>Parana (breaking the fast): {timeText(d.parana, d.date, clock)} <span className="muted">after Hari Vasara ends at {stamp(d.parana.hari_vasara_end, clock)}</span></p>}
      <button type="button" className="mu-quiet" onClick={() => onShow(d.date, dialAt(d))}>Show on the day dial</button>
    </div>
  );
}

/** The picked day, as the ceremonies show one: its date, tithi at sunrise and Maasa on top, then every observance of the
 * day (the picked one first, with when else it falls), how each day was found. */
function FestivalDetail({ f, date, day, clock, onShow, also, onFest, onDate, next }: {
  f: Festival | undefined; date: string; day: FestivalDay | undefined; clock: Clock; onShow: (day: string, start: string) => void;
  also: Festival[]; onFest: (id: string) => void; onDate: (date: string) => void; next: { f: Festival; d: FestivalDate } | undefined;
}) {
  const d = f?.dates.find((x) => x.date === date);
  const masa = day ?? d;
  return (
    <section className="mu-detail" aria-live="polite">
      <h3><span>{dayLong(date)}{day && `, ${day.tithi}`}{masa && <>, <span className="mu-detail-month">{masa.masa} Maasa{masa.adhika ? " (Adhika)" : ""}</span></>}</span></h3>
      {!f || !d ? (
        <div className="mu-reject">
          <p>No festival or observance on this day.</p>
          {next && <button type="button" onClick={() => { onFest(next.f.id); onDate(next.d.date); }}>Next: {next.f.name}, {dayLong(next.d.date)}</button>}
        </div>
      ) : (<>
        <FestivalCard f={f} d={d} clock={clock} onShow={onShow} />
        {also.map((x) => <FestivalCard key={x.id} f={x} d={x.dates.find((y) => y.date === date)!} clock={clock} onShow={onShow} onPick={() => onFest(x.id)} />)}
        {f.dates.length > 1 && (
          <div className="fe-else">
            <h4>{f.name} this year</h4>
            <ul className="fe-year">
              {f.dates.map((x) => <li key={x.date}><button type="button" aria-pressed={x.date === date} onClick={() => onDate(x.date)}>{dayMonth(x.date)}</button></li>)}
            </ul>
          </div>
        )}
        {f.elsewhere.length > 0 && (
          <div className="fe-else">
            <h4>{f.name} in other calendars</h4>
            <dl>
              {f.elsewhere.map((e) => (
                <div key={e.calendar}>
                  <dt>{e.calendar}</dt>
                  <dd>{e.name !== f.name && `${e.name}: `}{e.dates.length ? e.dates.map(dayMonth).join(", ") : "not this year"}
                    {e.dates.join() === f.dates.map((x) => x.date).join() && <span className="muted"> (the same)</span>}</dd>
                </div>
              ))}
            </dl>
          </div>
        )}
      </>)}
    </section>
  );
}

/** Pick an event, read the month: each day judged by Panchang Shuddhi, and for the open chart's person when asked.
 * Or pick a festival of the chosen regional calendar and see when it falls; under the month, its observances either way. */
export function FindMuhurta({ at, clock, lunar, nowAsk, today, enabled, personal, onShow, list, setList, festivals, festDays, calendarName, onMonth }: {
  at: Birth; clock: Clock; lunar: LunarSystem; nowAsk: number; today: string; enabled: boolean; personal: boolean; onShow: (day: string, start: string) => void;
  list: ListMode; setList: (l: ListMode) => void; festivals: Festival[] | undefined; festDays: Record<string, FestivalDay>; calendarName: string; onMonth: (date: string) => void;
}) {
  const natal = useChart((s) => s.birth), name = useChart((s) => s.name);
  const events = useQuery({ queryKey: ["muhurta-events"], queryFn: api.muhurtaEvents, staleTime: Infinity });
  const [event, setEvent] = useSaved<string>("muhurta.event", "vivah");
  const [festId, setFestId] = useSaved<string>("muhurta.festival", "");
  const ceremonies = list === "ceremonies";
  const q = useQuery({
    queryKey: ["muhurta-find", at, event, personal ? natal : null],
    queryFn: () => api.muhurtaFind(at, event, personal ? natal! : undefined),
    enabled: enabled && ceremonies, placeholderData: (p) => p,
  });
  const [sel, setSel] = useKept<string | null>("muhurta.day", null);
  const month = `${at.year}-${String(at.month).padStart(2, "0")}`;
  useEffect(() => { if (sel && !sel.startsWith(month)) setSel(null); }, [month]); // eslint-disable-line react-hooks/exhaustive-deps
  const monthName = new Date(Date.UTC(at.year, at.month - 1, 1)).toLocaleDateString("en-GB", { month: "long", year: "numeric", timeZone: "UTC" });
  const t = (iso: string, date: string) => clockText(iso, date, date + "T06:00:00", clock === "vedic" ? "24" : clock);

  const items = festivals ?? [];
  const rows = ofMonth(items, month);
  const byDate = new Map<string, typeof rows>();
  rows.forEach((r) => byDate.set(r.d.date, [...(byDate.get(r.d.date) ?? []), r]));
  const fest = items.find((f) => f.id === festId) ?? rows[0]?.f ?? items[0];
  // the Now button picks today, and in the festival list the month's observance nearest after it
  useEffect(() => {
    if (!nowAsk) return;
    setSel(today);
    const near = rows.find((x) => x.d.date >= today) ?? rows[rows.length - 1];
    if (!ceremonies && near) setFestId(near.f.id);
  }, [nowAsk]); // eslint-disable-line react-hooks/exhaustive-deps
  const r = ceremonies ? q.data : undefined;
  const good = r?.days.filter((d) => d.windows.length) ?? [];
  const chosen = r && (r.days.find((d) => d.date === sel) ?? good.find((d) => d.date >= today) ?? good[0] ?? r.days[0]);
  const picked = ceremonies ? chosen?.date : sel ?? fest?.dates.find((d) => d.date.startsWith(month))?.date;
  const shown = picked ?? (today.startsWith(month) ? today : month + "-01");

  // the month's good days, beside the lunar month in the day's heading, where the sentence over the calendar used to be
  const count: Count = r ? { text: r.good_days ? plural(r.good_days, "good day") : "No good days", title: `${r.event.name} in ${monthName}${r.personal ? ` for ${name || "this chart"}` : ""}, at ${at.place}` } : { text: "" };

  const chooseFest = (f: Festival) => {
    setFestId(f.id);
    if (f.dates.some((d) => d.date.startsWith(month))) { setSel(f.dates.find((d) => d.date.startsWith(month))!.date); return; }
    const d = f.dates.find((x) => x.date >= today) ?? f.dates[0];
    setSel(d.date);
    onMonth(d.date);
  };
  const goTo = (date: string) => { setSel(date); if (!date.startsWith(month)) onMonth(date); };
  const pickDay = (date: string) => {
    setSel(date);
    const here = byDate.get(date) ?? [];
    if (!ceremonies && here.length) setFestId(here[(here.findIndex((x) => x.f.id === fest?.id) + 1) % here.length].f.id);   // clicking again moves to the day's next one
  };

  const first = (new Date(Date.UTC(at.year, at.month - 1, 1)).getUTCDay() + 6) % 7;   // Monday first
  const days = Array.from({ length: new Date(Date.UTC(at.year, at.month, 0)).getUTCDate() }, (_, i) => `${month}-${String(i + 1).padStart(2, "0")}`);
  const judged = new Map(r?.days.map((d) => [d.date, d]));

  return (
    <div className="mu-find">
      <div className="mu-find-left">
        <div className="seg mu-toggle mu-list-mode" role="radiogroup" aria-label="List">
          {(["ceremonies", "festivals"] as const).map((v) => (
            <button key={v} type="button" role="radio" aria-checked={list === v} aria-selected={list === v} onClick={() => setList(v)}
              title={v === "ceremonies" ? "Find good times for a ceremony" : `The festivals of the ${calendarName} calendar`}>{v === "ceremonies" ? "Ceremonies" : "Festivals"}</button>
          ))}
        </div>
        {ceremonies
          ? <Loaded q={events}>{(evs) => <EventList events={evs} value={event} onChange={setEvent} />}</Loaded>
          : festivals ? <FestivalList items={items} value={fest?.id ?? ""} onChange={chooseFest} /> : <p className="muted">Loading…</p>}
      </div>
      <div className="mu-find-main">
        <div className="mu-find-cal">
          <div className="mu-cal" role="grid" aria-label={ceremonies ? `${r?.event.name ?? ""} in ${monthName}` : `${calendarName} festivals in ${monthName}`}>
            {WEEK.map((w) => <div key={w} className="mu-cal-head" role="columnheader">{w}</div>)}
            {Array.from({ length: first }, (_, i) => <div key={"x" + i} aria-hidden="true" />)}
            {days.map((date) => {
              const here = byDate.get(date) ?? [], names = here.map((x) => x.f.name).join(", ");
              const d = judged.get(date), g = ceremonies && d ? grade(d.best) : "none";
              const when = ceremonies && d ? (d.windows.length ? `${GRADE_TEXT[g]}, from ${t(d.windows[0].start, date)}` : `not suitable, ${d.short}`) : "";
              return (
                <button key={date} type="button" role="gridcell" aria-selected={date === picked} onClick={() => pickDay(date)}
                  className={`mu-cell ${g}${!ceremonies && here.length ? " fe" : ""}${date < today ? " past" : ""}${date === today ? " today" : ""}`}
                  aria-label={[dayLong(date), when, names].filter(Boolean).join(": ")}>
                  <span className="mu-cell-n">{Number(date.slice(8))}{ceremonies && here.length > 0 && <i className="fe-dot" aria-hidden="true" />}</span>
                  {ceremonies
                    ? d && (d.windows.length ? <span className="mu-cell-best">{t(d.windows[0].start, date)}</span> : <span className="mu-cell-why">{d.short}</span>)
                    : here.length > 0 && <span className="fe-cell-name">{here[0].f.name}{here.length > 1 && <span className="muted"> +{here.length - 1}</span>}</span>}
                </button>
              );
            })}
          </div>
          <section className="fe-month" aria-label={`Observances in ${monthName}`}>
            <h4>{festivals ? (rows.length ? plural(rows.length, "observance") : "No observances") : "Observances"} <span className="muted">{calendarName} calendar</span></h4>
            {rows.length ? (
              <ol>
                {rows.map(({ f, d }) => (
                  <li key={f.id + d.date}>
                    <button type="button" className="fe-row" aria-pressed={!ceremonies && f.id === fest?.id && d.date === picked}
                      onClick={() => { setSel(d.date); if (!ceremonies) setFestId(f.id); }}>
                      <span className="fe-row-date">{words(d.date, { weekday: "short", day: "numeric" })}</span>
                      <span className="fe-row-name">{f.name}</span>
                      <span className="fe-row-time">{d.at ? `${d.at.label} ${timeText(d.at, d.date, clock)}` : ""}</span>
                    </button>
                  </li>
                ))}
              </ol>
            ) : <p className="muted">{festivals ? "None this month." : "Loading…"}</p>}
          </section>
        </div>
        <div className="mu-find-side">
          {ceremonies
            ? <Loaded q={q}>{() => chosen && <DayDetail d={chosen} clock={clock} lunar={lunar} onShow={onShow} next={good.find((x) => x.date > chosen.date)} onPick={setSel} count={count} />}</Loaded>
            : festivals && <FestivalDetail f={fest} date={shown} day={festDays[shown]} clock={clock} onShow={onShow} onFest={setFestId} onDate={goTo}
                also={(byDate.get(picked ?? "") ?? []).map((x) => x.f).filter((x) => x.id !== fest?.id)} next={rows.find((x) => x.d.date > (picked ?? ""))} />}
          <p className="mu-note">{ceremonies
            ? "These dates follow the common rules of Panchang Shuddhi. Traditions differ, so confirm an important date with your family priest or astrologer."
            : `Each date follows the ${calendarName} rule shown with it, for this place. Temples and local panchangs can keep a festival a day apart; confirm an important date with your family priest.`}</p>
        </div>
      </div>
    </div>
  );
}
