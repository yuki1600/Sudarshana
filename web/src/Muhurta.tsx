import { useEffect, useMemo, useRef, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api, type Birth, type Festival, type FestivalCalendar, type LunarSystem, type MuhurtaDay, type Place } from "./api";
import { pageScale, useKept, useSaved } from "./hooks";
import { Dial, type Pick, type PopInfo, type Readout, type Ring } from "./MuhurtaDial";
import { CHOGHADIYA, GOWRI, HORA, LIMBS, NAK_LORDS, SIGN_TYPE, SPANS, tithiGroup, WEEKDAY_LORD } from "./muhurtaInfo";
import { ord } from "./Calculations";
import { FindMuhurta, type ListMode } from "./MuhurtaFind";
import { goodWindows, HARD_AVOID, hourText, hoursOn, spanAt, spansOf, ticks, verdict, type Clock, type Span } from "./muhurtaMath";
import { useMenu } from "./Menu";
import { Icon } from "./Icons";
import { useChart } from "./store";
import { Loaded, SubTabs, supOrd } from "./ui";

interface Spot { name: string; latitude: number; longitude: number; tz: number; place?: Place; altitude?: number }
export interface Prefs { lunar: LunarSystem; clock: Clock; lens: "choghadiya" | "gowri"; view: "muhurta" | "panchanga" }
const NEW_DELHI: Spot = { name: "New Delhi, India", latitude: 28.6139, longitude: 77.209, tz: 5.5 };
const OWN = "muhurta.place", PREFS = "muhurta.prefs";
const VIEWS = [{ id: "day", name: "Panchanga" }, { id: "find", name: "Muhurta" }] as const;

const load = <T,>(key: string, fallback: T): T => { try { return { ...fallback, ...JSON.parse(localStorage.getItem(key) ?? "{}") }; } catch { return fallback; } };
const save = (key: string, v: unknown) => { try { localStorage.setItem(key, JSON.stringify(v)); } catch { /* private window: this page only */ } };
const iso = (d: Date) => d.toISOString().slice(0, 10);
/** Today's date at a place, from its zone. */
const todayAt = (tz: number) => iso(new Date(Date.now() + tz * 3_600_000));
/** The clock reading at a place now, as a local ISO string. */
const nowAt = (tz: number) => new Date(Date.now() + tz * 3_600_000).toISOString().slice(0, 19);
/** A calendar's hover tip: where it is followed. */
const calTip = (c: FestivalCalendar) => c.places;
const SYSTEMS = [["purnimanta", "Purnimanta"], ["amanta", "Amanta"], ["solar", "Sauramana"]] as const;
/** "Purnimanta", or "Amanta · Telugu" where the month system has several regional calendars. */
const calLabel = (c: FestivalCalendar, all: FestivalCalendar[]) => {
  const label = SYSTEMS.find(([m]) => m === c.months)![1];
  return all.filter((x) => x.months === c.months).length > 1 ? `${label} · ${c.name}` : label;
};
const reduced = () => typeof matchMedia === "function" && matchMedia("(prefers-reduced-motion: reduce)").matches;

/** Split a sentence into lines of about `n` characters, for the dial's readout. */
function wrap(text: string, n = 28): string[] {
  const out: string[] = [];
  for (const w of text.split(" ")) {
    if (out.length && (out[out.length - 1] + " " + w).length <= n) out[out.length - 1] += " " + w;
    else out.push(w);
  }
  return out;
}

/** Type a city; picking one sets the place the whole tab calculates for. */
function PlacePicker({ spot, onPick }: { spot: Spot; onPick: (s: Spot) => void }) {
  const [text, setText] = useState(spot.name);
  const [typing, setTyping] = useState(false);
  const [active, setActive] = useState(0);
  useEffect(() => { setText(spot.name); }, [spot.name]);
  const hits = useQuery({ queryKey: ["places", text, "", ""], queryFn: () => api.places(text), enabled: typing && text.length >= 2 });
  const list = (hits.data ?? []).slice(0, 8);
  const choose = (p: Place) => { setTyping(false); onPick({ name: [p.name, p.admin1_name, p.country_code].filter(Boolean).join(", "), latitude: p.latitude, longitude: p.longitude, tz: p.tz_standard, place: p, altitude: p.altitude ?? 0 }); };
  return (
    <label className="mu-place">
      <span className="mu-label">Place</span>
      <input value={text} onChange={(e) => { setText(e.target.value); setTyping(true); setActive(0); }} onFocus={(e) => e.target.select()}
        onBlur={() => setTimeout(() => { setTyping(false); setText(spot.name); }, 150)}
        onKeyDown={(e) => {
          if (e.key === "ArrowDown") { e.preventDefault(); setActive((i) => Math.min(i + 1, list.length - 1)); }
          else if (e.key === "ArrowUp") { e.preventDefault(); setActive((i) => Math.max(i - 1, 0)); }
          else if (e.key === "Enter" && list[active]) { e.preventDefault(); choose(list[active]); }
          else if (e.key === "Escape") { setTyping(false); setText(spot.name); }
        }}
        placeholder="Type a city" autoComplete="off" role="combobox" aria-expanded={typing && list.length > 0} aria-controls="mu-hits" />
      {typing && text.length >= 2 && (
        <ul className="hits mu-hits" id="mu-hits" role="listbox">
          {list.map((p, i) => (
            <li key={p.country_code + p.name + p.latitude} role="option" aria-selected={i === active}>
              <button type="button" className={i === active ? "active" : undefined} onMouseDown={(e) => e.preventDefault()} onClick={() => choose(p)}>
                {p.name}{p.admin1_name ? `, ${p.admin1_name}` : ""} <span className="muted">{p.country_code}</span>
              </button>
            </li>
          ))}
          {hits.isFetched && !list.length && <li className="muted mu-nohit">No place by that name</li>}
        </ul>
      )}
    </label>
  );
}

/** One line of the day sheet: a span you can click to move the hand there. */
function SpanButton({ s, h, onH, text, note, tone }: { s: Span; h: number; onH: (h: number) => void; text: string; note?: string; tone?: string }) {
  const on = s.from <= h && h < s.to;
  return (
    <li>
      <button type="button" className={`mu-span ${tone ?? ""}`} aria-current={on || undefined} onClick={() => onH(s.from + 1 / 120)}>
        <span className="mu-span-name">{s.name}{note && <span className="muted"> {note}</span>}</span>
        <span className="mu-span-time">{text}</span>
      </button>
    </li>
  );
}

const ViewIcon = ({ v }: { v: "muhurta" | "panchanga" }) => (
  <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" aria-hidden="true">
    {v === "muhurta"
      ? <path d="M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18zM12 7.5a4.5 4.5 0 1 0 0 9 4.5 4.5 0 0 0 0-9zM12 3v4.5M21 12h-4.5M12 21v-4.5M3 12h4.5" />
      : <><path d="M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18z" /><path d="M12 3a9 9 0 0 1 0 18z" fill="currentColor" stroke="none" /></>}
  </svg>
);

function DayView({ d, prefs, setPref, tz, jump, nowAsk, festivals }: { d: MuhurtaDay; prefs: Prefs; setPref: (k: keyof Prefs, v: string) => void; tz: number; jump: number | null; nowAsk: number; festivals: Festival[] }) {
  const day = d.date;
  const f = useMemo(() => ({ rise: hoursOn(d.sunrise, day), set: hoursOn(d.sunset, day), next: hoursOn(d.next_sunrise, day) }), [d, day]);
  const S = (rows: Parameters<typeof spansOf>[0]) => spansOf(rows, day, f.next);
  const cho = S([...d.choghadiya.day, ...d.choghadiya.night]), gowri = S(d.gowri), hora = S(d.hora), lagna = S(d.lagna).map((s) => ({ ...s, good: null }));
  const avoid = S(d.avoid).map((s) => ({ ...s, good: HARD_AVOID.has(s.name) ? false : null }));
  const good = S(d.auspicious);
  const limbs: [string, Span[]][] = [["Tithi", S(d.tithi)], ["Nakshatra", S(d.nakshatra)], ["Yoga", S(d.yoga)], ["Karana", S(d.karana)], ["Moon in", S(d.moon_sign)]];
  const lens = prefs.lens === "gowri" ? gowri : cho;
  const lensName = prefs.lens === "gowri" ? "Gowri" : "Choghadiya";
  const windows = goodWindows(lens, avoid, good);
  const t = (x: number) => hourText(x, f.rise, prefs.clock);
  const range = (a: number, b: number) => {
    const x = t(a), y = b >= f.next ? "next sunrise" : t(b);
    const tail = (z: string) => z.slice(-2);
    return prefs.clock === "12" && /M$/.test(x) && /M$/.test(y) && tail(x) === tail(y) && !x.includes("+") ? `${x.slice(0, -3)}–${y}` : `${x}–${y}`;
  };

  // the clock now at the place, ticking each half minute
  const [nowIso, setNow] = useState(() => nowAt(tz));
  useEffect(() => { const id = setInterval(() => setNow(nowAt(tz)), 30_000); return () => clearInterval(id); }, [tz]);
  const now = hoursOn(nowIso, day);
  const nowInDay = now >= f.rise && now < f.next ? now : null;

  // the hand: now on today, midday otherwise, or where "Find a muhurta" pointed; it sweeps there from sunrise once
  const target = jump ?? nowInDay ?? (f.rise + f.set) / 2;
  const [h, setH] = useState(target);
  const raf = useRef(0);
  useEffect(() => {
    cancelAnimationFrame(raf.current);
    if (reduced()) { setH(target); return; }
    const t0 = performance.now(), from = f.rise;
    const step = (ts: number) => {
      const k = Math.min(1, (ts - t0) / 700), e = 1 - (1 - k) ** 3;
      setH(from + (target - from) * e);
      if (k < 1) raf.current = requestAnimationFrame(step);
    };
    raf.current = requestAnimationFrame(step);
    return () => cancelAnimationFrame(raf.current);
  }, [day, d.sunrise, jump]); // eslint-disable-line react-hooks/exhaustive-deps
  const move = (x: number) => { cancelAnimationFrame(raf.current); setH(x); };
  useEffect(() => { if (nowAsk && nowInDay !== null) move(nowInDay); }, [nowAsk]); // eslint-disable-line react-hooks/exhaustive-deps

  // the dial's column is as wide as the dial at the column's height, so the dial sits at the left with no blank beside it
  // and the panel takes the rest (narrow screens keep the stylesheet's single column)
  const dayBox = useRef<HTMLDivElement>(null);
  const aspect = 1;                            // the dial is drawn on a square
  const [box, setBox] = useState({ w: 0, h: 0 });
  useEffect(() => {
    const ro = new ResizeObserver(([e]) => setBox({ w: e.contentRect.width, h: e.contentRect.height }));
    ro.observe(dayBox.current!);
    return () => ro.disconnect();
  }, []);
  const s = pageScale();
  const wide = box.w > 900 * s && !matchMedia("(max-width: 960px)").matches;
  const cols = wide ? `${Math.round(Math.min((box.h - 4) * aspect, box.w - 470 * s))}px minmax(27.5rem, 1fr)` : undefined;
  const panchangaView = prefs.view === "panchanga";
  let rings: Ring[], readout: Readout, why = "";
  if (panchangaView) {
    rings = limbs.map(([k, spans]) => ({ key: k, label: k, spans: spans.map((s) => ({ ...s, good: s.good === false || /Rikta/.test(tithiGroup(s.name)) && k === "Tithi" || /Amavasya/.test(s.name) ? false : null })), kind: "limb" as const }));
    const at = (k: number) => spanAt(limbs[k][1], h)?.name ?? "";
    readout = { time: t(h), tone: "plain", word: at(0), lines: [`${at(1)} nakshatra`, `${at(2)} yoga`] };
  } else {
    rings = [
      { key: "cho", label: "Choghadiya", spans: cho, kind: "quality" },
      { key: "gowri", label: "Gowri", spans: gowri, kind: "quality" },
      { key: "hora", label: "Hora", spans: hora, kind: "planet" },
      { key: "lagna", label: "Lagna", spans: lagna, kind: "sign" },
    ];
    const v = verdict(h, lens, avoid, good), slot = spanAt(lens, h);
    why = v.tone === "avoid"
      ? `${v.because.map((n) => (n === slot?.name ? `${n} ${lensName.toLowerCase()}` : n)).join(", ")} until ${t(v.until!)}`
      : [slot && `${slot.name} ${lensName.toLowerCase()}`, ...v.because.filter((n) => n !== slot?.name)].filter(Boolean).join(", ");
    readout = { time: t(h), tone: v.tone, word: { excellent: "Excellent time", good: "Good time", avoid: "Avoid" }[v.tone], lines: wrap(why) };
  }

  const duration = (a: number, b: number) => { const m = Math.round((b - a) * 60); return m >= 60 ? `${Math.floor(m / 60)} h ${m % 60} min` : `${m} min`; };
  const describe = ({ ring, span: s }: Pick): PopInfo => {
    const time = s.from === s.to ? t(s.from) : `${t(Math.max(s.from, s.to <= f.rise ? s.from : f.rise))} to ${s.to > f.next + 1 / 60 ? "past the next sunrise" : t(Math.min(s.to, f.next))}, ${duration(s.from, Math.min(s.to, f.next))}`;
    const tone = s.good === true ? "good" : s.good === false ? "bad" : "plain";
    switch (ring) {
      case "Choghadiya": { const [lord, text] = CHOGHADIYA[s.name] ?? ["", ""]; return { title: `${s.name} choghadiya`, tone, time, lines: [text, `Ruled by ${lord}.`] }; }
      case "Gowri": return { title: `${s.name} (Gowri)`, tone, time, lines: [GOWRI[s.name] ?? ""] };
      case "Hora": return { title: `${s.name} hora`, tone, time, lines: [`Good for ${HORA[s.name]?.charAt(0).toLowerCase()}${HORA[s.name]?.slice(1)}`, s.good ? "One of the four Shubha horas." : ""].filter(Boolean) };
      case "Lagna": { const [type, text] = SIGN_TYPE[s.name] ?? ["", ""]; return { title: `${s.name} rising`, tone, time, lines: [`${type} sign. ${text}`] }; }
      case "Tithi": return { title: s.name, tone, time, lines: [tithiGroup(s.name), LIMBS.Tithi] };
      case "Nakshatra": return { title: `${s.name} nakshatra`, tone, time, lines: [`Ruled by ${NAK_LORDS[s.name] ?? "?"}.`, LIMBS.Nakshatra] };
      case "Yoga": return { title: `${s.name} yoga`, tone, time, lines: [s.good === false ? "Inauspicious; avoid good starts." : "Auspicious.", LIMBS.Yoga] };
      case "Karana": return { title: `${s.name} karana`, tone, time, lines: [s.name.startsWith("Vishti") ? SPANS["Bhadra (Vishti)"] : LIMBS.Karana] };
      case "Moon in": return { title: `Moon in ${s.name}`, tone, time, lines: [LIMBS["Moon sign"]] };
      default:
        if (s.parts && s.parts.length > 1) return { title: "Times to avoid", tone: "bad", time, lines: [...s.parts.map((x) => `${x.name}: ${range(x.from, x.to)}`), "Do not begin anything new in this whole stretch."] };
        return { title: s.name, tone, time, lines: SPANS[s.name] ? [SPANS[s.name]] : [] };
    }
  };

  const m = d.month;
  const hard = avoid.filter((s) => s.good === false).sort((a, b) => a.from - b.from);
  const care = avoid.filter((s) => s.good === null);

  return (
    <div className="mu-day" ref={dayBox} style={cols ? { gridTemplateColumns: cols } : undefined}>
      <div className="mu-dial-col">
        <div className="seg mu-dial-toggle" role="radiogroup" aria-label="Dial">
          {(["muhurta", "panchanga"] as const).map((v) => (
            <button key={v} type="button" role="radio" aria-checked={prefs.view === v} aria-selected={prefs.view === v} onClick={() => setPref("view", v)}
              aria-label={v === "muhurta" ? "Muhurtas" : "Panchanga"}
              title={v === "muhurta" ? "Muhurtas: choghadiya, gowri, hora and lagna" : "Panchanga: tithi, nakshatra, yoga, karana and Moon sign"}>
              <ViewIcon v={v} />
            </button>
          ))}
        </div>
        <Dial f={f} rings={rings} avoid={panchangaView ? [] : avoid} auspicious={panchangaView ? [] : good} ticks={ticks(f, prefs.clock)}
          h={h} onH={move} now={nowInDay} readout={readout} describe={describe} riseText={t(f.rise)} setText={t(f.set)}
          valueText={`${readout.time}, ${readout.word}${why ? ": " + why : ""}`} />
      </div>

      <div className="mu-sheet">
        <section className="mu-block first">
          <div className="mu-block-head">
            <h4>Panchanga</h4>
            <span className="mu-dayname">{m.name}{m.adhika && prefs.lunar !== "saura" ? " (Adhika)" : ""}{m.kshaya && prefs.lunar === "amanta" ? ` (Kshaya ${m.kshaya})` : ""}, {m.paksha} paksha</span>
          </div>
          <dl className="mu-limbs">
            <div><dt>Vara</dt><dd><span className="mu-limb static">{d.weekday} <span className="muted">ruled by {WEEKDAY_LORD[d.weekday]}</span></span></dd></div>
            {festivals.some((x) => x.dates.some((y) => y.date === day)) && (
              <div><dt>Festivals</dt><dd>{festivals.filter((x) => x.dates.some((y) => y.date === day)).map((x) => <span key={x.id} className="mu-limb static" title={x.criteria}>{x.name}</span>)}</dd></div>
            )}
            {limbs.map(([k, rows], n) => (
              <div key={k}>
                <dt><i className={`mu-key-dot mu-r${n}`} aria-hidden="true" />{k}</dt>
                <dd>{rows.map((s, i) => (
                  <button key={i} type="button" className="mu-limb" aria-current={(s.from <= h && h < s.to) || undefined} onClick={() => move(Math.max(s.from, f.rise) + 1 / 120)}>
                    {s.name}<span className="muted"> {s.to >= f.next ? "past next sunrise" : `until ${t(s.to)}`}</span>
                  </button>
                ))}</dd>
              </div>
            ))}
          </dl>
        </section>

        <section className="mu-block">
          <div className="mu-block-head">
            <h4>Good windows</h4>
            <div className="seg mu-lens" role="radiogroup" aria-label="Judge the windows by">
              {(["choghadiya", "gowri"] as const).map((k) => (
                <button key={k} type="button" role="radio" aria-checked={prefs.lens === k} aria-selected={prefs.lens === k} onClick={() => setPref("lens", k)}>{k === "gowri" ? "Gowri" : "Choghadiya"}</button>
              ))}
            </div>
          </div>
          {windows.length ? (
            <ol className="mu-list">
              {windows.map((w, i) => (
                <SpanButton key={i} s={{ name: w.names.join(", "), from: w.from, to: w.to, good: true }} h={h} onH={move} text={range(w.from, w.to)}
                  tone={w.best ? "best" : "good"} note={w.best ? "with " + good.filter((x) => x.from < w.to && w.from < x.to).map((x) => x.name).join(", ") : w.from >= f.set ? "after sunset" : undefined} />
              ))}
            </ol>
          ) : <p className="mu-hint">No {lensName} window today is free of the spans to avoid.</p>}
        </section>

        <section className="mu-block">
          <h4>Avoid</h4>
          <ol className="mu-list">{hard.map((s, i) => <SpanButton key={i} s={s} h={h} onH={move} text={range(s.from, s.to)} tone="bad" />)}</ol>
          {care.length > 0 && <>
            <h5>Take care</h5>
            <ol className="mu-list">{care.map((s, i) => <SpanButton key={i} s={s} h={h} onH={move} text={range(s.from, s.to)} tone="care"
              note={s.name === "Panchak" ? "(travel south, building, firewood)" : "(for child ceremonies)"} />)}</ol>
          </>}
        </section>

        <section className="mu-block">
          <h4>Calendar</h4>
          <dl className="mu-facts">
            <div className={prefs.lunar === "amanta" ? "on" : undefined}><dt>Amanta month</dt><dd>{m.amanta}{m.adhika ? " (Adhika)" : ""}{m.kshaya ? ` (Kshaya ${m.kshaya})` : ""}</dd></div>
            <div className={prefs.lunar === "purnimanta" ? "on" : undefined}><dt>Purnimanta month</dt><dd>{m.purnimanta}</dd></div>
            <div className={prefs.lunar === "saura" ? "on" : undefined}><dt>Saura month</dt><dd>{m.saura}</dd></div>
            <div><dt>Vikram Samvat</dt><dd>{m.vikram}</dd></div>
            <div><dt>Shaka Samvat</dt><dd>{m.shaka}</dd></div>
            <div><dt>Gujarati Samvat</dt><dd>{m.gujarati}</dd></div>
          </dl>
        </section>
      </div>
    </div>
  );
}

export function Muhurta() {
  const natal = useChart((s) => s.natal), name = useChart((s) => s.name);
  const [who, setWho] = useSaved<"all" | "me">("muhurta.who", "all");
  const personal = who === "me" && !!natal;
  const [view, setView] = useSaved<"day" | "find">("muhurta", "day");
  const meta = useChart((s) => s.meta);
  // the place: the open chart's, unless the user picked another for this chart (a new chart follows its own place again)
  const chartKey = natal ? `${natal.latitude.toFixed(4)},${natal.longitude_east.toFixed(4)}` : "";
  const [own, setOwn] = useState<{ spot: Spot; chart: string } | null>(() => { try { return JSON.parse(localStorage.getItem(OWN) ?? "null"); } catch { return null; } });
  // the chart keeps only its city, so find its atlas row: the zone then follows the date shown, daylight saving included
  const atlas = useQuery({ queryKey: ["places", meta?.city ?? "", meta?.country ?? "", ""], queryFn: () => api.places(meta.city, meta.country), enabled: !!natal && !!meta?.city, staleTime: Infinity });
  const chartSpot: Spot | null = natal ? {
    name: natal.place || [meta?.city, meta?.country].filter(Boolean).join(", ") || "Chart's place", latitude: natal.latitude, longitude: natal.longitude_east, altitude: natal.altitude_m,
    tz: meta?.tz_standard_east ?? natal.tz_east_hours,
    place: atlas.data?.find((r) => Math.abs(r.latitude - natal.latitude) < 0.25 && Math.abs(r.longitude - natal.longitude_east) < 0.25),
  } : null;
  const spot: Spot = own && (!natal || own.chart === chartKey) ? own.spot : chartSpot ?? own?.spot ?? NEW_DELHI;
  const [date, setDate] = useKept("muhurta.date", todayAt(-new Date().getTimezoneOffset() / 60));
  const [list, setList] = useSaved<ListMode>("muhurta.list", "ceremonies");
  const [calendar, setCalendar] = useSaved<string>("muhurta.calendar", "north");
  const calendars = useQuery({ queryKey: ["festival-calendars"], queryFn: api.festivalCalendars, staleTime: Infinity });
  const cal = calendars.data?.find((c) => c.id === calendar);
  const { open: openMenu, node: menuNode } = useMenu();
  const [jump, setJump] = useState<{ date: string; h: number } | null>(null);
  const [nowAsk, setNowAsk] = useState(0);     // the Now button: today, with the hand at this moment
  const [prefs, setPrefs] = useState<Prefs>(() => load(PREFS, { lunar: "purnimanta", clock: "12", lens: "choghadiya", view: "muhurta" } as Prefs));
  const pick = (s: Spot) => { const o = { spot: s, chart: chartKey }; setOwn(o); save(OWN, o); };
  const setPref = (k: keyof Prefs, v: string) => { const n = { ...prefs, [k]: v }; setPrefs(n); save(PREFS, n); };
  // the calendar names the months: Purnimanta, Amanta or solar; the stored pick stands in until the calendars load
  const lunar: LunarSystem = cal ? (cal.months === "solar" ? "saura" : cal.months) : prefs.lunar;
  const [y, mo, dd] = date.split("-").map(Number);

  // the zone of the place on that date (daylight saving included), else the place's standard zone
  const zone = useQuery({ queryKey: ["zone", spot.name, spot.latitude, date], queryFn: () => api.zone(spot.place!, y, mo, dd, 12), enabled: !!spot.place && !!y });
  const tz = zone.data?.tz_east_hours ?? spot.tz;
  const at = (day: number): Birth => ({ year: y, month: mo, day, hour_local: 12, tz_east_hours: tz, longitude_east: spot.longitude, latitude: spot.latitude,
    altitude_m: spot.altitude ?? spot.place?.altitude ?? 0, gregorian: true, place: spot.name, pressure_hpa: 1013.25, temperature_c: 20 });
  // the festivals of the year shown, in the chosen regional calendar (the server works out the year once per place)
  const fest = useQuery({ queryKey: ["festivals", spot.latitude, spot.longitude, tz, y, calendar], queryFn: () => api.festivals(at(1), calendar), enabled: !!y && !zone.isFetching, staleTime: Infinity });
  const q = useQuery({ queryKey: ["muhurta-day", at(dd), lunar], queryFn: () => api.muhurtaDay(at(dd), lunar), enabled: view === "day" && !!y && !zone.isFetching, placeholderData: (p) => p });

  const step = (n: number) => {
    const x = view === "find" ? new Date(Date.UTC(y, mo - 1 + n, 1)) : new Date(Date.UTC(y, mo - 1, dd + n));
    setJump(null);
    setDate(iso(x));
  };
  const today = todayAt(tz);
  const monthName = new Date(Date.UTC(y, mo - 1, 1)).toLocaleDateString("en-GB", { month: "long", year: "numeric", timeZone: "UTC" });

  return (
    <section className="pane muhurta">
      <header className="mu-bar tab-head">
        <SubTabs tabs={[...VIEWS]} value={view} onChange={setView} label="Muhurta views" />
        {view === "find" && list === "ceremonies" && (
          <div className="seg mu-views" role="radiogroup" aria-label="Judge for">
            <button type="button" role="radio" aria-checked={!personal} aria-selected={!personal} onClick={() => setWho("all")}
              title="Panchang only: the day's tithi, nakshatra, weekday and lagna">General</button>
            <button type="button" role="radio" aria-checked={personal} aria-selected={personal} disabled={!natal} onClick={() => setWho("me")}
              title={natal ? "Adds tarabala and chandrabala from the birth Moon" : "Open a chart to judge times for a person"}>{natal ? name || "This chart" : "Chart"}</button>
          </div>
        )}
        <div className="mu-controls">
          <button type="button" className="now-btn mu-now-btn" aria-label="Now" title={view === "find" ? "Now: this month, with today picked" : "Now: today, with the hand at this moment"}
            onClick={() => { setJump(null); setDate(todayAt(tz)); setNowAsk((n) => n + 1); }}>
            <Icon name="now" />
          </button>
          <div className="mu-stepper" role="group" aria-label={view === "find" ? "Month" : "Date"}>
            <button type="button" aria-label={view === "find" ? "Previous month" : "Previous day"} onClick={() => step(-1)}>‹</button>
            {/* the same date calendar as the platform's other date fields; in the month view any day picks its month */}
            <label className="mu-month mu-date">{view === "find" ? monthName : supOrd(`${ord(dd)} ${monthName}`)}
              <input type="date" value={date} onClick={(e) => e.currentTarget.showPicker?.()} onChange={(e) => { if (e.target.value) { setJump(null); setDate(e.target.value); } }} aria-label={view === "find" ? "Month" : "Date"} />
            </label>
            <button type="button" aria-label={view === "find" ? "Next month" : "Next day"} onClick={() => step(1)}>›</button>
          </div>
          <button type="button" className="mu-calendar" aria-haspopup="menu" title={cal ? calTip(cal) : "Festival calendar"}
            onClick={(e) => {
              const r = e.currentTarget.getBoundingClientRect();
              const item = (c: FestivalCalendar) => ({ label: c.name, checked: c.id === calendar, title: calTip(c),
                onClick: () => { setCalendar(c.id); setPref("lunar", c.months === "solar" ? "saura" : c.months); } });
              // the three month systems; one kept differently from region to region opens on its regional calendars
              openMenu({ clientX: r.left, clientY: r.bottom + 4 }, SYSTEMS.map(([m, label]) => {
                const group = (calendars.data ?? []).filter((c) => c.months === m);
                return group.length === 1 ? item(group[0]) : { label, checked: cal?.months === m, title: group.map((c) => c.places).join(", "), items: group.map(item) };
              }), "Festival calendar");
            }}>
            {cal ? calLabel(cal, calendars.data ?? []) : "Calendar"} <span aria-hidden="true">▾</span>
          </button>
          {menuNode}
          <PlacePicker spot={spot} onPick={pick} />
          <button type="button" className="mu-quiet" onClick={() => { setJump(null); setDate(today); }} disabled={view === "find" ? date.slice(0, 7) === today.slice(0, 7) : date === today}>Today</button>
          <div className="seg mu-toggle" role="radiogroup" aria-label="Clock">
            {(["12", "24"] as const).map((v) => (
              <button key={v} type="button" role="radio" aria-checked={prefs.clock === v} aria-selected={prefs.clock === v} onClick={() => setPref("clock", v)}
                title={`${v} hour clock`}>{v}h</button>
            ))}
          </div>
        </div>
      </header>
      {view === "day"
        ? <Loaded q={q}>{(d) => <DayView d={d} prefs={{ ...prefs, lunar }} setPref={setPref} tz={tz} jump={jump?.date === d.date ? jump.h : null} nowAsk={nowAsk} festivals={fest.data?.items ?? []} />}</Loaded>
        : <FindMuhurta at={at(1)} clock={prefs.clock} lunar={lunar} nowAsk={nowAsk} today={today} enabled={!zone.isFetching} personal={personal}
            list={list} setList={setList} festivals={fest.data?.year === y ? fest.data.items : undefined} festDays={fest.data?.days ?? {}} calendarName={cal?.name ?? ""} onMonth={(d) => { setJump(null); setDate(d); }}
            onShow={(day, start) => { setJump({ date: day, h: hoursOn(start, day) }); setDate(day); setView("day"); }} />}
    </section>
  );
}
