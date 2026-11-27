import { ZoneInput } from "./Zone";
import { guessZone } from "./zones";
import { useEffect, useRef, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api, type Birth, type Home, type Meta, type Place } from "./api";
import { backdropClose } from "./ChartDialogs";
import { formatTz, fromDms, joinHours, splitHours, toDms, type Dms } from "./format";
import { useChart } from "./store";

const num = (v: string) => (v.trim() === "" ? NaN : Number(v));
const COORD_KEY = "birthCoordFormat";
type CoordFmt = "decimal" | "dms";
type Fields = { name: string; y: string; mo: string; d: string; h: string; mi: string; s: string; lat: string; lon: string; tz: string; alt: string };

function loadCoordFmt(): CoordFmt {
  try { return localStorage.getItem(COORD_KEY) === "dms" ? "dms" : "decimal"; } catch { return "decimal"; }
}

type Clock = "am" | "pm" | "24";

const WHEN: (keyof Fields)[] = ["y", "mo", "d", "h", "mi", "s"];

function clockFields(hourLocal: number): { h: string; mi: string; s: string; clock: Clock } {
  const [h24, mi, s] = splitHours(hourLocal);
  return { h: String(h24 % 12 || 12), mi: String(mi), s: String(s), clock: h24 >= 12 ? "pm" : "am" };
}

/** where new charts start until the account picks a default place of its own (Settings > Display) */
export const MYSURU: Home = { lat: 12.29791, lon: 76.63925, tz: 5.5, alt: 757,
  meta: { city: "Mysuru", country: "IN", state: "Karnataka", dst: false, tz_standard_east: 5.5, tz_dst_east: 5.5, timezone: "Asia/Kolkata" } };

function blankFields(): { f: Fields; query: string; country: string; stateName: string; meta?: Meta; clock: Clock } {
  const now = new Date();
  const home = keptHome() ?? MYSURU;
  const t = clockFields(now.getHours() + now.getMinutes() / 60);
  return {
    f: { name: "", y: String(now.getFullYear()), mo: String(now.getMonth() + 1), d: String(now.getDate()), h: t.h, mi: t.mi, s: String(now.getSeconds()),
      lat: home.lat === undefined ? "" : String(home.lat), lon: home.lon === undefined ? "" : String(home.lon), tz: String(home.tz ?? -now.getTimezoneOffset() / 60), alt: String(home.alt ?? 0) },
    query: home.meta?.city ?? "", country: home.meta?.country ?? "", stateName: home.meta?.state ?? "", meta: home.meta, clock: t.clock,
  };
}

// the default place for new charts (Settings > Display); without one, new charts start at Mysuru. It belongs to
// the account (saved on the server, so it follows the login to any browser); this browser keeps a copy so a new chart
// opens without waiting on the network
export function saveHome(b: Birth | null, meta?: Meta) {
  const home = b && { lat: b.latitude, lon: b.longitude_east, tz: b.tz_east_hours, alt: b.altitude_m, meta };
  keepHome(home);
  api.saveHome(home).catch(() => { /* offline: this browser still has it */ });
}

/** the browser's copy of the account's default place; App sets it on every sign-in and clears it on sign-out */
export function keepHome(home: Home | null) {
  try {
    if (home) localStorage.setItem("defaultLocation", JSON.stringify(home));
    else localStorage.removeItem("defaultLocation");
  } catch { /* private window */ }
}

/** the browser's copy, for an account that has none yet: a place chosen here before places belonged to accounts */
export function keptHome(): Home | null {
  try { return JSON.parse(localStorage.getItem("defaultLocation") ?? "null"); } catch { return null; }
}

// New chart opens at this moment at the default place, the clock read in that place's zone (not the browser's)
export function nowChart(): { birth: Birth; meta: Partial<Meta> } {
  const { f, meta } = blankFields();
  const tz = num(f.tz);
  const at = new Date(Date.now() + tz * 3_600_000);   // the place's wall clock, read with the UTC getters
  const city = meta?.city ?? "";
  return {
    birth: { year: at.getUTCFullYear(), month: at.getUTCMonth() + 1, day: at.getUTCDate(), hour_local: joinHours(at.getUTCHours(), at.getUTCMinutes(), at.getUTCSeconds()),
      tz_east_hours: tz, longitude_east: num(f.lon), latitude: num(f.lat), altitude_m: num(f.alt) || 0, gregorian: true, place: city, pressure_hpa: 1013.25, temperature_c: 20 },
    meta: { ...meta, city, country: meta?.country ?? "", dst: meta?.dst ?? false, tz_standard_east: meta?.tz_standard_east ?? tz, tz_dst_east: meta?.tz_dst_east ?? tz },
  };
}

function fromBirth(name: string, birth: Birth, meta: Meta): { f: Fields; query: string; country: string; stateName: string; meta: Meta; clock: Clock } {
  const t = clockFields(birth.hour_local);
  return {
    f: { name, y: String(birth.year), mo: String(birth.month), d: String(birth.day), h: t.h, mi: t.mi, s: t.s,
      lat: String(birth.latitude), lon: String(birth.longitude_east), tz: String(birth.tz_east_hours), alt: String(birth.altitude_m) },
    query: meta.city, country: meta.country ?? "", stateName: meta.state ?? "", meta, clock: t.clock,
  };
}

export function BirthDialog({ open, blank, onClose, onSave, title, inline, seed, defaultGender, placeOnly, noName }: {
  open: boolean; blank?: boolean; onClose: () => void;
  onSave?: (name: string, birth: Birth, meta: Meta) => void; title?: string;
  inline?: boolean; seed?: { name: string; birth: Birth; meta: Meta } | null;
  defaultGender?: number;   // 0 unknown, 1 male, 2 female — used when blank / no seed
  placeOnly?: boolean;      // just the place: no name, gender, date or time
  noName?: boolean;         // the date, time and place of a chart already named: no name or gender
}) {
  const ref = useRef<HTMLDialogElement>(null);
  const nameRef = useRef<HTMLInputElement>(null);
  const { name: curName, natal: cur, meta: curMeta, setChart, openChart } = useChart();
  const withGender = (m?: Meta): Meta => ({ ...(m ?? curMeta), gender: m?.gender ?? defaultGender ?? 0 });
  const start = blank ? blankFields() : seed ? fromBirth(seed.name, seed.birth, seed.meta) : cur ? fromBirth(curName, cur, curMeta) : blankFields();
  const [f, setF] = useState(start.f);
  const [query, setQuery] = useState(start.query);
  const [country, setCountry] = useState(start.country);
  const [state, setState] = useState("");       // admin1 code
  const [stateName, setStateName] = useState(start.stateName);
  const [picked, setPicked] = useState<Place | null>(null);
  const [meta, setMeta] = useState<Meta>(blank || !start.meta ? withGender(start.meta) : start.meta);
  const [error, setError] = useState("");
  const [clock, setClock] = useState<Clock>(start.clock);
  const [live, setLive] = useState(!!blank || (!seed && !cur));   // a blank form's time is the clock's until the date or time is typed
  const [calendar, setCalendar] = useState<"gregorian" | "julian">(seed?.birth.gregorian === false || (!seed && cur?.gregorian === false) ? "julian" : "gregorian");
  const [coordFmt, setCoordFmt] = useState<CoordFmt>(loadCoordFmt);
  const [active, setActive] = useState(-1);
  const [typingPlace, setTypingPlace] = useState(false);
  const set = (k: keyof Fields) => (e: React.ChangeEvent<HTMLInputElement>) => { if (WHEN.includes(k)) setLive(false); setF({ ...f, [k]: e.target.value }); };

  const fill = (blankMode: boolean, fromSeed?: { name: string; birth: Birth; meta: Meta } | null) => {
    const next = blankMode ? blankFields() : fromSeed ? fromBirth(fromSeed.name, fromSeed.birth, fromSeed.meta)
      : cur ? fromBirth(curName, cur, curMeta) : blankFields();
    setF(next.f); setQuery(next.query); setCountry(next.country); setState(""); setStateName(next.stateName);
    setMeta(blankMode || !fromSeed ? withGender(next.meta) : next.meta!);
    setClock(next.clock); setLive(blankMode || (!fromSeed && !cur)); setPicked(null); setTypingPlace(false); setError("");
  };

  useEffect(() => {
    if (inline) { if (open) fill(!!blank, seed); return; }
    const d = ref.current;
    if (!d) return;
    // the name comes up selected, so typing replaces it (a new account's first chart is just "Prashna")
    if (open && !d.open) { fill(!!blank, seed); d.showModal(); requestAnimationFrame(() => { nameRef.current?.focus(); nameRef.current?.select(); }); }
    else if (!open && d.open) d.close();
  }, [open, inline, seed?.name, seed?.birth]); // eslint-disable-line react-hooks/exhaustive-deps

  const countries = useQuery({ queryKey: ["countries"], queryFn: api.countries, enabled: open, staleTime: Infinity });
  const states = useQuery({
    queryKey: ["states", country],
    queryFn: ({ queryKey }) => api.states(queryKey[1]),
    enabled: open && !!country,
    staleTime: Infinity,
  });

  // Resolve a saved state name to its admin1 code once the country list loads
  useEffect(() => {
    if (!stateName || state || !states.data?.length) return;
    const hit = states.data.find((s) => s.name === stateName || s.code === stateName);
    if (hit) setState(hit.code);
  }, [states.data, stateName, state]);

  const q = query.trim();
  const hits = useQuery({
    queryKey: ["places", q, country, state],
    queryFn: ({ queryKey }) => api.places(queryKey[1], queryKey[2], queryKey[3]),
    enabled: open && typingPlace && !picked && q.length >= 2,
    staleTime: 60_000,
    retry: 1,
  });
  const list = (typingPlace && !picked && hits.data) || [];

  useEffect(() => { setActive(-1); }, [q, country, state, hits.dataUpdatedAt]);

  // Zone and DST follow the date once a place is picked
  useEffect(() => {
    if (!picked) return;
    const [y, mo, d, hr] = [num(f.y), num(f.mo), num(f.d), joinHours(num(f.h) || 0, num(f.mi) || 0, num(f.s) || 0)];
    if ([y, mo, d].some(Number.isNaN)) return;
    api.zone(picked, y, mo, d, hr).then((z) => {
      setF((p) => ({ ...p, tz: String(z.tz_east_hours) }));
      setMeta((m) => ({ ...m,   // the gender (and the rest) stay: only the place's own fields change
        city: picked.name, country: picked.country_code, state: picked.admin1_name || stateName,
        dst: z.dst, tz_standard_east: picked.tz_standard, tz_dst_east: picked.tz_dst, timezone: picked.timezone || undefined,
      }));
    }).catch((e) => setError(e.message));
  }, [picked, f.y, f.mo, f.d, f.h, f.mi, f.s]); // eslint-disable-line react-hooks/exhaustive-deps

  const pick = (p: Place) => {
    setPicked(p);
    setTypingPlace(false);
    setQuery(p.name);
    setCountry(p.country_code);
    setState(p.admin1_code ?? "");
    setStateName(p.admin1_name ?? "");
    setActive(-1);
    setF((q) => ({ ...q, lat: String(p.latitude), lon: String(p.longitude), tz: String(p.tz_standard), alt: String(p.altitude ?? 0) }));
  };

  const zoneAt = { y: num(f.y), mo: num(f.mo), d: num(f.d), hour: joinHours(num(f.h) || 0, num(f.mi) || 0, num(f.s) || 0) };
  const onPlaceKey = placeKeys(list, active, setActive, pick, () => { setQuery(""); setPicked(null); });

  const changeCountry = (code: string) => {
    setCountry(code);
    setState("");
    setStateName("");
    setPicked(null);
  };

  const changeState = (code: string) => {
    setState(code);
    setStateName(states.data?.find((s) => s.code === code)?.name ?? "");
    setPicked(null);
  };

  const changeCoordFmt = (fmt: CoordFmt) => {
    setCoordFmt(fmt);
    try { localStorage.setItem(COORD_KEY, fmt); } catch { /* private window */ }
  };

  const setAxis = (axis: "lat" | "lon", dms: Dms) => {
    setF((p) => ({ ...p, [axis]: String(fromDms(dms)) }));
  };

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    const now = live ? blankFields() : null;   // untouched: cast at the second Save is pressed
    const t = now ? now.f : f, at = now ? now.clock : clock;
    const v = { y: num(t.y), mo: num(t.mo), d: num(t.d), h: num(t.h), mi: num(t.mi), s: num(t.s), lat: num(f.lat), lon: num(f.lon), tz: num(f.tz), alt: num(f.alt) };
    if (Object.values(v).some(Number.isNaN)) return setError("Every field needs a number.");
    const hour = at === "24" ? v.h : v.h % 12 + (at === "pm" ? 12 : 0);
    const birth: Birth = { year: v.y, month: v.mo, day: v.d, hour_local: joinHours(hour, v.mi, v.s), tz_east_hours: v.tz,
      longitude_east: v.lon, latitude: v.lat, altitude_m: v.alt, gregorian: calendar === "gregorian", place: query, pressure_hpa: 1013.25, temperature_c: 20 };
    const st = stateName || states.data?.find((s) => s.code === state)?.name || meta.state;
    const next = { ...meta, city: query || meta.city, country: country || meta.country, state: st };
    const label = f.name.trim() || "Chart";
    if (onSave) onSave(label, birth, next); else if (blank) openChart(label, birth, next); else setChart(label, birth, next);
    onClose();
  };

  const latN = num(f.lat);
  const lonN = num(f.lon);
  const latDms = Number.isFinite(latN) ? toDms(latN) : { deg: 0, min: 0, sec: 0, hemi: 1 as const };
  const lonDms = Number.isFinite(lonN) ? toDms(lonN) : { deg: 0, min: 0, sec: 0, hemi: 1 as const };

  const form = (
      <form onSubmit={submit} className={inline ? "birth-inline-form" : undefined}>
        {title !== "" && <h2>{title ?? "Birth data"}</h2>}
        {!placeOnly && <>
        {!noName && <label>Name<input ref={nameRef} value={f.name} onChange={set("name")} autoFocus={!inline} /></label>}
        {!noName && <label>Gender<select value={meta.gender ?? 0} onChange={(e) => setMeta({ ...meta, gender: Number(e.target.value) })}><option value={0}>Unknown</option><option value={1}>Male</option><option value={2}>Female</option></select></label>}
        <fieldset>
          <legend>Date and time (local)</legend>
          <label>Year<input type="number" value={f.y} onChange={set("y")} required /></label>
          <label>Month<input type="number" min={1} max={12} value={f.mo} onChange={set("mo")} required /></label>
          <label>Day<input type="number" min={1} max={31} value={f.d} onChange={set("d")} required /></label>
          <label>Calendar<select value={calendar} onChange={(e) => setCalendar(e.target.value as "gregorian" | "julian")}><option value="gregorian">Gregorian</option><option value="julian">Julian</option></select></label>
          <label>Hour<input type="number" min={0} max={clock === "24" ? 23 : 12} value={f.h} onChange={set("h")} required /></label>
          <label>Min<input type="number" min={0} max={59} value={f.mi} onChange={set("mi")} required /></label>
          <label>Sec<input type="number" min={0} max={59} value={f.s} onChange={set("s")} required /></label>
          <label>Clock<select value={clock} onChange={(e) => { setLive(false); setClock(e.target.value as typeof clock); }}><option value="am">am</option><option value="pm">pm</option><option value="24">0-24 hrs</option></select></label>
        </fieldset>
        </>}
        <div className="place">
          <div className="place-row">
            <label>Country
              <select value={country} onChange={(e) => changeCountry(e.target.value)}>
                <option value="">All countries</option>
                {(countries.data ?? []).map((c) => (
                  <option key={c.code} value={c.code}>{c.name}</option>
                ))}
              </select>
            </label>
            <label>State / Province
              <select value={state} onChange={(e) => changeState(e.target.value)} disabled={!country}>
                <option value="">{country ? "All states" : "Select a country first"}</option>
                {(states.data ?? []).map((s) => (
                  <option key={s.code} value={s.code}>{s.name}</option>
                ))}
              </select>
            </label>
            <ZoneInput value={f.tz} onChange={(tz) => setF((p) => ({ ...p, tz }))} placeholder="Fills when you pick a place" required
              named={picked?.timezone || meta.timezone || guessZone(meta.country, num(f.tz), zoneAt) || undefined}   /* a chart saved before zones were kept: its country's one zone at those hours */
              at={zoneAt}
              note={meta.dst && picked ? <span className="muted"> DST</span> : null} />
            <label className="place-name">Place
              <input value={query} onChange={(e) => { setQuery(e.target.value); setPicked(null); setTypingPlace(true); }}
                onKeyDown={onPlaceKey} placeholder="Type a city, e.g. Chennai" autoComplete="off"
                role="combobox" aria-expanded={list.length > 0} aria-controls="place-hits"
                aria-autocomplete="list" aria-activedescendant={active >= 0 ? `place-hit-${active}` : undefined} />
            </label>
          </div>
          {typingPlace && !picked && q.length >= 2 && (
            <PlaceHits hits={hits} active={active} onActive={setActive} onPick={pick} />
          )}
        </div>
        <fieldset>
          <legend>
            Location
            <span className="seg coord-fmt" role="group" aria-label="Coordinate format">
              <button type="button" aria-selected={coordFmt === "decimal"} onClick={() => changeCoordFmt("decimal")}>Decimal</button>
              <button type="button" aria-selected={coordFmt === "dms"} onClick={() => changeCoordFmt("dms")}>DMS</button>
            </span>
          </legend>
          {coordFmt === "decimal" ? (
            <>
              <label>Latitude (N+)<input type="number" step="any" value={f.lat} onChange={set("lat")} required /></label>
              <label>Longitude (E+)<input type="number" step="any" value={f.lon} onChange={set("lon")} required /></label>
            </>
          ) : (
            <>
              <DmsFields label="Latitude" dms={latDms} pos="N" neg="S" onChange={(d) => setAxis("lat", d)} />
              <DmsFields label="Longitude" dms={lonDms} pos="E" neg="W" onChange={(d) => setAxis("lon", d)} />
            </>
          )}
          <label>Altitude (m)<input type="number" step="any" value={f.alt} onChange={set("alt")} required /></label>
        </fieldset>
        {error && <p role="alert" className="error">{error}</p>}
        <menu>
          <button type="submit" className="primary">{inline ? "Use this chart" : placeOnly ? "Save" : "Save & cast"}</button>
        </menu>
      </form>
  );

  if (inline) return open ? <div className="birth-inline">{form}</div> : null;
  return <dialog ref={ref} onClose={onClose} onClick={backdropClose} className="dialog">{form}</dialog>;
}

function DmsFields({ label, dms, pos, neg, onChange }: {
  label: string; dms: Dms; pos: string; neg: string; onChange: (d: Dms) => void;
}) {
  const set = (patch: Partial<Dms>) => onChange({ ...dms, ...patch });
  return (
    <label className="dms">{label}
      <span className="dms-row">
        <input type="number" min={0} max={180} value={dms.deg} aria-label={`${label} degrees`}
          onChange={(e) => set({ deg: Math.max(0, Number(e.target.value) || 0) })} required />
        <span aria-hidden>°</span>
        <input type="number" min={0} max={59} value={dms.min} aria-label={`${label} minutes`}
          onChange={(e) => set({ min: Math.min(59, Math.max(0, Number(e.target.value) || 0)) })} required />
        <span aria-hidden>′</span>
        <input type="number" min={0} max={59.999} step="any" value={dms.sec} aria-label={`${label} seconds`}
          onChange={(e) => set({ sec: Math.min(59.999, Math.max(0, Number(e.target.value) || 0)) })} required />
        <span aria-hidden>″</span>
        <select value={dms.hemi} aria-label={`${label} hemisphere`}
          onChange={(e) => set({ hemi: Number(e.target.value) as 1 | -1 })}>
          <option value={1}>{pos}</option>
          <option value={-1}>{neg}</option>
        </select>
      </span>
    </label>
  );
}

/** Arrows move through the places found, Enter takes the highlighted one (or the top one), Escape clears what was typed. */
export function placeKeys(list: Place[], active: number, setActive: React.Dispatch<React.SetStateAction<number>>, pick: (p: Place) => void, clear: () => void) {
  return (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!list.length) return;
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setActive((i) => (i + 1) % list.length);
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setActive((i) => (i <= 0 ? list.length - 1 : i - 1));
    } else if (e.key === "Enter") {   // none highlighted: the top one, as the form would submit otherwise
      e.preventDefault();
      pick(list[Math.max(0, active)]);
    } else if (e.key === "Escape") {
      e.preventDefault();
      setActive(-1);
      clear();
    }
  };
}

/** The atlas's places for what is typed, under the birth data's Place field and the map's place search alike. */
export function PlaceHits({ hits, active, onActive, onPick }: {
  hits: { isError: boolean; error: unknown; isFetching: boolean; data?: Place[] }; active: number; onActive: (i: number) => void; onPick: (p: Place) => void;
}) {
  const ref = useRef<HTMLUListElement>(null);
  useEffect(() => {
    if (active >= 0) ref.current?.children[active]?.scrollIntoView({ block: "nearest" });
  }, [active]);
  const list = hits.data ?? [];
  return hits.isError ? <p className="hits-note error" role="alert">{(hits.error as Error).message}</p>
    : hits.isFetching && !hits.data ? <p className="hits-note muted">Searching…</p>
    : list.length > 0 ? (
      <ul className="hits" id="place-hits" role="listbox" ref={ref}>
        {list.map((p, i) => (
          <li key={p.country_code + p.name + p.latitude + p.longitude} id={`place-hit-${i}`} role="option" aria-selected={i === active}>
            <button type="button" className={i === active ? "active" : undefined}
              onMouseEnter={() => onActive(i)} onClick={() => onPick(p)}>
              <span className="hit-main">
                <span className="hit-name">{p.name}{p.admin1_name ? `, ${p.admin1_name}` : ""} <span className="muted">{p.country_code}</span></span>
                <span className="muted hit-meta">
                  {p.latitude.toFixed(2)}°, {p.longitude.toFixed(2)}°
                  {" · "}
                  {formatTz(p.tz_standard, p.tz_dst)}
                  {p.timezone ? ` · ${p.timezone}` : ""}
                </span>
              </span>
            </button>
          </li>
        ))}
      </ul>
    ) : hits.data ? <p className="hits-note muted">No matching place</p> : null;
}
