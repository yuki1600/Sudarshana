import { useEffect, useMemo, useRef, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api, type AstroBand, type AstroLine, type Birth, type Meta, type Place } from "./api";
import { BirthDialog, PlaceHits, placeKeys } from "./BirthDialog";
import { formatLon, SIGNS } from "./format";
import { Icon } from "./Icons";
import { useKept, useSaved, useShape } from "./hooks";
import { bhavaOf, drawn, HALF_HEIGHT, latAt, lonAt, mapY, wrap } from "./mapGeometry";
import { shown, signName } from "./names";
import { useChart } from "./store";
import { SYSTEMS } from "./Views";
import { BORDERS, CITIES, DISPUTED, LAKES, LAND, STATES } from "./worldMap";

const GRAHAS: [string, string][] = [["Su", "Sun"], ["Mo", "Moon"], ["Ma", "Mars"], ["Me", "Mercury"], ["Ju", "Jupiter"], ["Ve", "Venus"], ["Sa", "Saturn"], ["Ra", "Rahu"], ["Ke", "Ketu"]];
const NAME = Object.fromEntries(GRAHAS);
const LAYERS: [string, string][] = [["signs", "Signs"], ["bhavas", "Bhavas"]];
const X = 4;                           // the viewBox's units per degree of longitude: the world fills its width
const COPIES = [-360, 0, 360];         // a curve that runs past the map's edge comes back in from the other one
const BHAVA_ROW = -52;                 // the latitude of the numbers on the whole world, mostly open ocean and short of where the curves bunch at the south ecliptic pole
const ROW_GAP = 32;                    // the sign names stand this far above them
const BIRTH_ZOOM = 3, FOUND_ZOOM = 5, MAX_ZOOM = 8;
const MAJOR_CITIES = 70;               // the whole world shows only these, the biggest; each step of zoom doubles them
const FAMOUS = 300;                    // the biggest of them may put their name beside or below the dot, the others only above it
const NAME_SPOTS = [[0, -4], [1, 3], [-1, 3], [0, 12]];    // above, right, left, below: half a name's width out, and points down
const LABEL = { width: 52, height: 14 };
const BOX = 22;                         // a graha's name box and the gap under it
const AREAS: [string, number[]][] = [["Career", [10]], ["Travel abroad", [9]], ["Settling abroad", [12]], ["Education", [4, 5]], ["Spouse and partners", [7]]];
const NTH = ["", "1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th", "10th", "11th", "12th"];
const AREA_COUNTRIES = 8, AREA_CITIES = 4;
const WORLD = { land: drawn(LAND), lakes: drawn(LAKES), borders: drawn(BORDERS), disputed: drawn(DISPUTED), states: drawn(STATES) };

/** What the page shows: units per unit of mapY, the page's height, the longitude and mapY at its middle, the zoom. */
interface Frame { sy: number; height: number; center: number; my: number; z: number }

/** On the page; ``lon`` is already measured from the centre. */
const xy = (f: Frame, lon: number, lat: number) => [lon * X * f.z, (f.my - mapY(lat)) * f.sy * f.z];
/** A place on the map, whichever way the map is turned. */
const place = (f: Frame, lon: number, lat: number) => xy(f, wrap(lon - f.center), lat);
const viewTop = (f: Frame) => Math.max(-f.height / 2, (f.my - HALF_HEIGHT) * f.sy * f.z);
const viewBottom = (f: Frame) => Math.min(f.height / 2, (f.my + HALF_HEIGHT) * f.sy * f.z);
const latOn = (f: Frame, y: number) => latAt(f.my - y / (f.sy * f.z));
const points = (sy: number, curve: number[][], lon0: number) => curve.map(([lon, lat]) => `${((lon - lon0) * X).toFixed(1)},${(-mapY(lat) * sy).toFixed(1)}`).join(" ");
const path = (sy: number, curve: number[][]) => `M${points(sy, curve, 0).replaceAll(" ", "L")}`;
/** A curve in its three copies around the world at the middle of the strip; turning the map only slides the strip. */
const copies = (sy: number, curve: number[][]) => {
  const lon0 = 360 * Math.round(curve[curve.length >> 1][0] / 360);
  return COPIES.map((c) => points(sy, curve, lon0 + c));
};
const toggled = (list: string, id: string) => { const l = list.split(",").filter(Boolean); return (l.includes(id) ? l.filter((x) => x !== id) : [...l, id]).join(","); };

function gridPath(sy: number) {
  const meridians = Array.from({ length: 25 }, (_, i) => path(sy, [[-360 + 30 * i, -90], [-360 + 30 * i, 90]]));
  const parallels = [-60, -30, 0, 30, 60].map((lat) => path(sy, [[-360, lat], [360, lat]]));
  return [...meridians, ...parallels].join("");
}

/** The tinted bands, their borders, a bhava's cusp where it has its own. Band i lies between curves i and i + 1. */
function Bands({ bands, kind, tint, cusps, sy }: { bands: AstroBand[]; kind: string; tint: boolean; cusps?: boolean; sy: number }) {
  return useMemo(() => {
    const zones = bands.slice(0, -1);
    const areas = zones.map((b, i) => (tint && i % 2 === 1 ? copies(sy, b.area!) : []));
    const edges = zones.map((b) => copies(sy, b.curve));
    const middles = zones.map((b) => (cusps && b.cusp ? copies(sy, b.cusp) : []));
    return (
      <>
        {COPIES.map((x, c) => (
          <g key={x} className={`astro-band ${kind}`}>
            {areas.map((a, i) => a.length > 0 && <polygon key={i} points={a[c]} />)}
            {edges.map((e, i) => <polyline key={i} points={e[c]}>{kind === "bhava" && <title>{`Border of bhavas ${zones[(i + 11) % 12].house} and ${zones[i].house}`}</title>}</polyline>)}
            {middles.map((e, i) => e.length > 0 && <polyline key={`c${i}`} className="cusp" points={e[c]}><title>{`Cusp of bhava ${zones[i].house}`}</title></polyline>)}
          </g>
        ))}
      </>
    );
  }, [bands, kind, tint, cusps, sy]);
}

/** A rising line run on into its setting half from where the graha grazes the horizon, so it goes round unbroken as the band borders do. */
function horizon(l: AstroLine, all: AstroLine[]) {
  const set = all.find((m) => m.body === l.body && m.angle === "DSC");
  if (!set) return l.curve;
  const shift = 360 * Math.round((l.curve[l.curve.length - 1][0] - set.curve[set.curve.length - 1][0]) / 360);
  return [...l.curve, ...set.curve.slice(0, -1).reverse().map(([lon, lat]) => [lon + shift, lat])];
}

function Lines({ lines, all, sy }: { lines: AstroLine[]; all: AstroLine[]; sy: number }) {
  return useMemo(() => {
    const drawn = lines.map((l) => copies(sy, horizon(l, all)));
    return (
      <>
        {COPIES.map((x, c) => (
          <g key={x}>
            {lines.map((l, i) => (
              <g key={l.body + l.angle} className={`astro-line ${l.angle}`} style={{ "--g": `var(--g-${l.body})` } as React.CSSProperties}>
                <title>{`${NAME[l.body]} rising, on the Lagna, then past where it grazes the horizon setting, on the 7th`}</title>
                <polyline points={drawn[i][c]} />
                <polyline className="hit" points={drawn[i][c]} />
              </g>
            ))}
          </g>
        ))}
      </>
    );
  }, [lines, all, sy]);
}

/** The label rows' latitudes, grahas, signs then bhavas: in the southern ocean, or along the bottom of a view that stops short of it. Every curve reaches the polar circles. */
function rowLats(f: Frame) {
  const bhava = Math.max(viewTop(f) + 3 * ROW_GAP, Math.min(viewBottom(f) - 26, xy(f, 0, BHAVA_ROW)[1]));
  const row = (y: number) => Math.max(-66, Math.min(66, latOn(f, y) ?? 0));
  return [row(bhava - 2 * ROW_GAP), row(bhava - ROW_GAP), row(bhava)];
}

/** One label a band in view, in the middle of what shows of it on the row of latitude. */
function bandSpots(bands: AstroBand[], row: number, f: Frame) {
  const y = xy(f, 0, row)[1];
  return bands.slice(0, -1).flatMap((b, i) => {
    const west = lonAt(b.curve, row), width = lonAt(bands[i + 1].curve, row) - west;
    const [lo, hi] = [wrap(west - f.center), wrap(west - f.center) - 360].map((lon) => [Math.max(lon * X * f.z, -708), Math.min((lon + width) * X * f.z, 708)]).sort((p, q) => (q[1] - q[0]) - (p[1] - p[0]))[0];
    return hi - lo < 20 ? [] : [{ band: b, x: (lo + hi) / 2, y }];
  });
}

/** The cities that belong at this zoom and have room for their name, clear of the labels and of the bigger cities' names. */
function cityMarks(taken: { x: number; y: number }[], f: Frame) {
  const placed = taken.map((l) => ({ x: l.x, y: l.y, w: LABEL.width }));
  return CITIES.slice(0, Math.round(MAJOR_CITIES * 2 ** (f.z - 1))).flatMap(([name, country, lat, lon], i) => {
    const [x, y] = place(f, lon, lat);
    const w = name.length * 5.6;
    const label = NAME_SPOTS.slice(0, i < FAMOUS ? 4 : 1).map(([out, down]) => [out * (w / 2 + 4), down]).find(([dx, dy]) => Math.abs(x + dx) + w / 2 < 716 && Math.abs(y + dy) < f.height / 2 - 8
      && placed.every((l) => Math.abs(l.x - x - dx) >= (l.w + w) / 2 || Math.abs(l.y - y - dy) >= LABEL.height - 2));
    if (!label) return [];
    placed.push({ x: x + label[0], y: y + label[1], w });
    return [{ name, country, lat, lon, x, y, label }];
  });
}

/** A graha's name wherever its line, the rising half and the setting half, crosses the row of latitude in view, as the sign names sit; one on another goes a row up. */
function lineLabels(lines: AstroLine[], all: AstroLine[], taken: { x: number; y: number }[], row: number, f: Frame) {
  const placed: { line?: AstroLine; x: number; y: number }[] = [...taken];
  const clear = (px: number, py: number) => placed.every((l) => Math.abs(l.x - px) >= LABEL.width || Math.abs(l.y - py) >= BOX);
  const y0 = xy(f, 0, row)[1];
  for (const line of lines.filter((l) => l.curve.length > 2)) {
    const set = all.find((m) => m.body === line.body && m.angle === "DSC");
    for (const half of set ? [line.curve, set.curve] : [line.curve]) {
      const turn = wrap(lonAt(half, row) - f.center) - lonAt(half, row);   // the whole turns that bring the crossing into view
      for (const copy of [-360, 0, 360]) {
        const at = (y: number) => (lonAt(half, latOn(f, y) ?? row) + turn + copy) * X * f.z;
        if (Math.abs(at(y0)) >= 690) continue;
        const y = [0, 1, 2, 3].map((k) => y0 - k * BOX).find((py) => clear(at(py), py)) ?? y0;
        placed.push({ line, x: at(y), y });
      }
    }
  }
  return placed.filter((l) => l.line) as { line: AstroLine; x: number; y: number }[];
}

function Inspector({ at, spot, birth, name }: { at: { lon: number; lat: number; name?: string; alt?: number | null }; spot: { left: number; top: number }; birth: Birth; name: string }) {
  const { display } = useChart();
  // the new place's own height (a searched place), not the birth place's; a point on the map has none known
  const moved: Birth = { ...birth, latitude: at.lat, longitude_east: at.lon, place: at.name ?? "", altitude_m: at.alt ?? 0 };
  const basics = useQuery({ queryKey: ["basics", moved, name], queryFn: () => api.basics(moved, name) });
  const houses = useQuery({ queryKey: ["houses", moved], queryFn: () => api.houses(moved) });
  const lagna = basics.data?.points.find((p) => p.name === "Lagna");
  const error = basics.error ?? houses.error;
  const coords = `${Math.abs(at.lat).toFixed(1)}°${at.lat < 0 ? "S" : "N"} ${Math.abs(at.lon).toFixed(1)}°${at.lon < 0 ? "W" : "E"}`;
  return (
    <aside className={`astro-inspect${spot.left > 50 ? " west" : ""}${spot.top > 50 ? " north" : ""}`} style={{ left: `${spot.left}%`, top: `${spot.top}%` }}
      aria-label="This place" aria-live="polite">
      <header>
        <strong>{at.name ?? coords}</strong>
      </header>
      {at.name && <p className="muted">{coords}</p>}
      {error ? <p role="alert" className="error">{error.message}</p> : !lagna || !houses.data ? <p className="muted">Calculating…</p> : (
        <>
          <p>Lagna <strong>{formatLon(lagna.lon).trim().replace(SIGNS[lagna.rasi], signName(lagna.rasi, SIGNS[lagna.rasi], display))}</strong></p>
          <dl>{houses.data.filter((r) => r.occupants.length).map((r) => <div key={r.house}><dt>{r.house}</dt><dd>{r.occupants.map((o) => shown(o, display)).join(" ")}</dd></div>)}</dl>
        </>
      )}
    </aside>
  );
}

/** A place as the box shows it: its name, state and country, and its zone. */
const SHORT: Record<string, string> = { US: "USA", GB: "UK", AE: "UAE", CD: "DR Congo" };   // long names known better short
type Where = { city: string; state?: string; country?: string; tz: number };
const where = ({ city, state, country, tz }: Where, countries: Map<string, string>, stateShown = state) =>
  `${[city, stateShown, country && (countries.get(country) ?? country)].filter(Boolean).join(", ")} · GMT${tz < 0 ? "−" : "+"}${Math.abs(tz)}`;

function useCountryNames() {
  const countries = useQuery({ queryKey: ["countries"], queryFn: api.countries, staleTime: Infinity });
  return useMemo(() => new Map((countries.data ?? []).map((c) => [c.code, SHORT[c.code] ?? c.name.trim()])), [countries.data]);
}

/** The biggest cities of each life area's bhavas, by country: where the Lagna falls in that bhava, so its matters come forward. */
function Insights({ bhavas, onPick }: { bhavas: AstroBand[]; onPick: (lon: number, lat: number, name: string) => void }) {
  const names = useCountryNames();
  const house = useMemo(() => CITIES.map(([, , lat, lon]) => bhavaOf(bhavas, lon, lat)), [bhavas]);
  return (
    <aside className="astro-insights" aria-label="Places by life area">
      {AREAS.map(([area, hs]) => {
        const by = new Map<string, (typeof CITIES)[number][]>();   // CITIES runs biggest first, so the first countries met have the biggest cities
        CITIES.forEach((c, i) => {
          if (!hs.includes(house[i])) return;
          const got = by.get(c[1]);
          if (got) { if (got.length < AREA_CITIES) got.push(c); } else if (by.size < AREA_COUNTRIES) by.set(c[1], [c]);
        });
        return (
          <section key={area}>
            <h4>{area} <span className="muted">{hs.map((h) => NTH[h]).join(" and ")}</span></h4>
            {by.size === 0 ? <p className="muted">No major city</p> : (
              <dl>{[...by].map(([cc, cs]) => (
                <div key={cc}><dt>{names.get(cc) ?? cc}</dt><dd>{cs.map(([n, , lat, lon]) => <button key={n} className="link" onClick={() => onPick(lon, lat, n)}>{n}</button>)}</dd></div>
              ))}</dl>
            )}
          </section>
        );
      })}
    </aside>
  );
}

/** The birth data's place search: the same atlas, list and keys. */
function PlaceSearch({ found, onPick }: { found: Where | null; onPick: (p: Place) => void }) {
  const [query, setQuery] = useState<string | null>(null);     // null: not typing, so it shows the place found
  const names = useCountryNames();
  const box = useRef<HTMLInputElement>(null);
  const [room, setRoom] = useState(0);
  useEffect(() => {
    const el = box.current!;
    const seen = new ResizeObserver(() => { const cs = getComputedStyle(el); setRoom(el.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight)); });
    seen.observe(el);
    return () => seen.disconnect();
  }, []);
  // the whole name when it fits; else the state cut short, the country always whole
  const shown = useMemo(() => {
    if (!found) return "";
    const full = where(found, names);
    const el = box.current, ctx = el && document.createElement("canvas").getContext("2d");
    if (!ctx || !found.state || !room) return full;
    ctx.font = getComputedStyle(el).font;
    const fits = (t: string) => ctx.measureText(t).width <= room;
    if (fits(full)) return full;
    for (let n = found.state.length - 1; n > 0; n--) {
      const t = where(found, names, `${found.state.slice(0, n).trimEnd()}…`);
      if (fits(t)) return t;
    }
    return where(found, names, "");
  }, [found, names, room]);
  const [active, setActive] = useState(-1);
  const q = (query ?? "").trim();
  const hits = useQuery({ queryKey: ["places", q, "", ""], queryFn: () => api.places(q), enabled: q.length >= 2, staleTime: 60_000, retry: 1 });
  const list = hits.data ?? [];
  useEffect(() => setActive(-1), [q, hits.dataUpdatedAt]);
  const go = (p: Place) => { onPick(p); setQuery(null); };
  return (
    <div className="astro-search">
      <input ref={box} value={query ?? shown} aria-label="Find a place" placeholder="Find a place" autoComplete="off" onChange={(e) => setQuery(e.target.value)}
        onFocus={(e) => e.currentTarget.select()} onBlur={() => { if (!q) setQuery(null); }}
        onKeyDown={placeKeys(list, active, setActive, go, () => setQuery(null))}
        role="combobox" aria-expanded={list.length > 0} aria-controls="place-hits" aria-autocomplete="list" aria-activedescendant={active >= 0 ? `place-hit-${active}` : undefined} />
      {q.length >= 2 && <PlaceHits hits={hits} active={active} onActive={setActive} onPick={go} />}
    </div>
  );
}

/** The chart's moment over the world: where each sign and bhava is on the Lagna, where each graha is on an angle. North up; it opens on the birth place, and zooming stays where it is. */
export function Astrocartography() {
  const { birth: natal, name, display, meta } = useChart();
  // another date, time and place for this chart's map, kept for the chart it was made for
  const [kept, setKept] = useKept<[string, Birth, Meta] | null>("astroMoment", null);
  const [editing, setEditing] = useKept("astroEditing", false);
  const [insights, setInsights] = useKept("astroInsights", false);
  const mine = !!kept && !!natal && kept[0] === JSON.stringify(natal);
  const birth = mine ? kept[1] : natal;
  const m = mine ? kept[2] : meta;
  const city = (m.city || birth?.place || "").trim(), cc = m.country?.length === 2 ? m.country : "";
  // a chart saved without its state: that of the atlas's place of the name nearest the chart's coordinates
  const atlas = useQuery({ queryKey: ["places", city, cc, ""], queryFn: () => api.places(city, cc), enabled: !!birth && !m.state && city.length >= 2, staleTime: 60_000 });
  const near = birth && atlas.data?.map((p) => ({ p, d: Math.hypot(p.latitude - birth.latitude, wrap(p.longitude - birth.longitude_east)) })).filter((x) => x.d < 0.5).sort((x, y) => x.d - y.d)[0]?.p;
  const here: Where | null = birth && city ? { city, state: m.state || near?.admin1_name || undefined, country: m.country, tz: birth.tz_east_hours } : null;   // the chart's own place
  const [layers, setLayers] = useSaved<string>("astroShown", "signs,bhavas,grahas,places");
  const [hidden, setHidden] = useSaved<string>("astroOff", "");
  const [of, setOf] = useSaved<string>("astroBhavaOf", "Lagna");
  const [system, setSystem] = useSaved<string>("astroBhavaSystem", "3");
  const [at, setAt] = useState<{ lon: number; lat: number; name?: string; alt?: number | null } | null>(null);
  const [found, setFound] = useKept<[string, Where] | null>("astroPlace", null);   // the place last searched on this map, with its zone
  const [view, setView] = useState<"birth" | { lon: number; my: number; z: number }>("birth");
  // a press outside the place card closes it; the map and its zoom keep it, since a click there picks another place
  useEffect(() => {
    if (!at) return;
    const down = (e: PointerEvent) => { if (!(e.target as Element).closest?.(".astro-map, .astro-nav")) setAt(null); };
    const esc = (e: KeyboardEvent) => { if (e.key === "Escape") setAt(null); };
    document.addEventListener("pointerdown", down, true);
    document.addEventListener("keydown", esc);
    return () => { document.removeEventListener("pointerdown", down, true); document.removeEventListener("keydown", esc); };
  }, [at]);
  const grab = useRef<{ x: number; y: number; lon: number; my: number; moved: boolean } | null>(null);
  const anchor = useRef([0, 0]);
  const on = (id: string) => layers.split(",").includes(id);
  const off = (id: string) => hidden.split(",").includes(id);
  const map = useQuery({ queryKey: ["astro", birth, of, system], queryFn: () => api.astrocartography(birth!, of, Number(system)), enabled: !!birth, placeholderData: (p) => p });
  const d = map.data;
  const [svg, k] = useShape();
  const height = 1440 * k;
  const sy = Math.min(height / 2 / HALF_HEIGHT, 1.5 * X * 180 / Math.PI);   // fills the page, short of stretching a tall one past half as much again
  const edge = HALF_HEIGHT * sy;
  const v = typeof view === "object" ? view : birth ? { lon: birth.longitude_east, my: mapY(birth.latitude), z: BIRTH_ZOOM } : { lon: 0, my: 0, z: 1 };
  const room = Math.max(0, HALF_HEIGHT - height / 2 / (sy * v.z));           // a view stays on the map
  const f = useMemo(() => ({ sy, height, center: wrap(v.lon), my: Math.max(-room, Math.min(room, v.my)), z: v.z }), [sy, height, v.lon, v.my, v.z, room]);
  const grid = useMemo(() => gridPath(sy), [sy]);
  const bhavas = on("bhavas") ? d?.bhavas ?? null : null;
  const lines = useMemo(() => (d ? d.lines.filter((l) => l.angle === "ASC" && !off(l.body)) : []), [d, hidden]); // eslint-disable-line react-hooks/exhaustive-deps
  const [lineRow, signRow, bhavaRow] = useMemo(() => rowLats(f), [f]);
  const signSpots = useMemo(() => (d && on("signs") ? bandSpots(d.signs, signRow, f) : []), [d, layers, signRow, f]); // eslint-disable-line react-hooks/exhaustive-deps
  const bhavaSpots = useMemo(() => (bhavas ? bandSpots(bhavas, bhavaRow, f) : []), [bhavas, bhavaRow, f]);
  const birthXY = birth && place(f, birth.longitude_east, birth.latitude);
  const fixed = useMemo(() => [...signSpots, ...bhavaSpots, ...(birthXY ? [{ x: birthXY[0] + 22, y: birthXY[1] }] : [])], [signSpots, bhavaSpots, birthXY?.[0], birthXY?.[1]]); // eslint-disable-line react-hooks/exhaustive-deps
  const labels = useMemo(() => lineLabels(lines, d?.lines ?? [], fixed, lineRow, f), [lines, d, fixed, lineRow, f]);
  const cities = useMemo(() => cityMarks([...labels, ...fixed], f), [labels, fixed, f]);
  const atXY = at && place(f, at.lon, at.lat);

  useEffect(() => setView("birth"), [birth?.latitude, birth?.longitude_east]);

  /** Zoom about a point of the page, in viewBox units from its middle. That point stays put, and zooming back from the same point retraces the way: the middle
   * kept in the view may be off the map when zoomed out, where the frame holds it in. A new point starts from what the page shows. */
  const zoom = (by: number, px = 0, py = 0) => {
    const z = Math.max(1, Math.min(MAX_ZOOM, f.z * by));
    const my = anchor.current[0] === px && anchor.current[1] === py ? v.my : f.my;
    anchor.current = [px, py];
    setView({ lon: wrap(f.center + px / (X * f.z) - px / (X * z)), my: my - py / (sy * f.z) + py / (sy * z), z });
  };
  const latestZoom = useRef(zoom);
  latestZoom.current = zoom;
  useEffect(() => {
    const el = svg.current!;
    let by = 1, x = 0, y = 0, frame = 0;
    const wheel = (e: WheelEvent) => {
      e.preventDefault();
      const p = new DOMPoint(e.clientX, e.clientY).matrixTransform(el.getScreenCTM()!.inverse());
      by *= Math.exp(-e.deltaY * (e.ctrlKey ? .01 : .002));             // a trackpad's pinch comes as a wheel with ctrl, in small steps
      [x, y] = [p.x, p.y];
      frame ||= requestAnimationFrame(() => { latestZoom.current(by, x, y); by = 1; frame = 0; });   // wheels come faster than the page draws, and none may be lost
    };
    el.addEventListener("wheel", wheel, { passive: false });           // React's own listener could not keep the page from zooming
    return () => { el.removeEventListener("wheel", wheel); cancelAnimationFrame(frame); };
  }, [svg]);

  const down = (e: React.PointerEvent<SVGSVGElement>) => { grab.current = e.button === 0 ? { x: e.clientX, y: e.clientY, lon: f.center, my: f.my, moved: false } : null; };
  const move = (e: React.PointerEvent<SVGSVGElement>) => {
    const g = grab.current;
    if (!g || !e.buttons || (!g.moved && Math.hypot(e.clientX - g.x, e.clientY - g.y) < 4)) return;   // a shorter move is a click
    if (!g.moved) { g.moved = true; e.currentTarget.setPointerCapture(e.pointerId); }
    const unit = 1440 / e.currentTarget.getBoundingClientRect().width / f.z;
    setView({ lon: wrap(g.lon - (e.clientX - g.x) * unit / X), my: g.my + (e.clientY - g.y) * unit / sy, z: f.z });
  };
  // only a shown city opens the popup (it stops the click); the bare map just closes it
  const click = () => { if (!grab.current?.moved) setAt(null); };

  return (
    <section className="pane">
      <div className="astro">
        <div className="astro-scroll">
          <div className="astro-map">
            <svg ref={svg} className={f.z > 1.5 ? "near" : undefined} viewBox={`-720 ${-height / 2} 1440 ${height}`} onPointerDown={down} onPointerMove={move} onClick={click} role="img" aria-label={`World map of ${name}'s chart: the signs and bhavas on the Lagna and the grahas on the angles by place`}>
              <g transform={`translate(${-f.center * X * f.z},${f.my * sy * f.z}) scale(${f.z})`}>
                <rect className="astro-sea" x={-2160} y={-edge} width={4320} height={2 * edge} />
                <g id="astro-world" transform={`scale(${X},${sy})`}>
                  <path className="astro-land" d={WORLD.land} />
                  <path className="astro-lakes" d={WORLD.lakes} />
                  <path className="astro-states" d={WORLD.states} />
                  <path className="astro-borders" d={WORLD.borders} />
                  <path className="astro-borders disputed" d={WORLD.disputed} />
                </g>
                <use href="#astro-world" x={-1440} />
                <use href="#astro-world" x={1440} />
                <path className="astro-grid" d={grid} />
                {d && on("signs") && <Bands bands={d.signs} kind="sign" tint sy={sy} />}
                {bhavas && <Bands bands={bhavas} kind="bhava" tint={!on("signs")} cusps={!off("cusps")} sy={sy} />}
                <Lines lines={lines} all={d?.lines ?? []} sy={sy} />
              </g>
              {cities.map(({ name: city, country, lat, lon, x, y, label }) => (
                <g key={`${city} ${lat} ${lon}`} className="astro-city" transform={`translate(${x},${y})`} onClick={(e) => { e.stopPropagation(); setFound(null); setAt({ lon, lat, name: city }); }}>
                  <title>{`${city}, ${country}`}</title>
                  <circle r={1.8} />
                  <text className="astro-label city" textAnchor="middle" x={label[0]} y={label[1]}>{city}</text>
                </g>
              ))}
              {signSpots.map(({ band, x, y }) => <text key={band.sign} className="astro-label sign" textAnchor="middle" x={x} y={y} dy=".35em">{signName(band.sign!, SIGNS[band.sign!], display)}</text>)}
              {bhavaSpots.map(({ band, x, y }) => (
                <g key={band.house} className="astro-badge" transform={`translate(${x},${y})`}>
                  <circle r={10} />
                  <text className="astro-label bhava" textAnchor="middle" dy=".35em">{band.house}</text>
                </g>
              ))}
              {labels.map((l, i) => {
                const name = shown(l.line.body, display), w = Math.max(20, name.length * 7 + 6);   // square for two letters, wider for a longer name
                return (
                  <g key={i} className="astro-badge graha" transform={`translate(${l.x},${l.y})`} style={{ "--g": `var(--g-${l.line.body})` } as React.CSSProperties}>
                    <rect x={-w / 2} y={-10} width={w} height={20} />
                    <text className="astro-label line" textAnchor="middle" dy=".35em">{name}</text>
                  </g>
                );
              })}
              {d?.poles.map(([lon, lat]) => {
                const [x, y] = place(f, lon, lat);
                return (
                  <g key={lat} className="astro-pole" transform={`translate(${x},${y})`}>
                    <title>The ecliptic pole is overhead here, so every Lagna line meets here. Between this point and the geographic pole the Lagna flips to the opposite band: click a place there to read it.</title>
                    <circle r={3.5} />
                  </g>
                );
              })}
              {birthXY && (
                <g className="astro-birth" transform={`translate(${birthXY[0]},${birthXY[1]})`}>
                  <title>{mine ? birth.place : `Birth place of ${name}`}</title>
                  <circle r={5} />
                  <text className="astro-label" x={8} y={4}>{mine ? birth.place || "Here" : "Birth"}</text>
                </g>
              )}
              {atXY && <circle className="astro-at" r={6} cx={atXY[0]} cy={atXY[1]} />}
            </svg>
            {map.isError && <p role="alert" className="error banner astro-error">{map.error.message}</p>}
            {insights && d?.bhavas && <Insights bhavas={d.bhavas} onPick={(lon, lat, n) => { setFound(null); setAt({ lon, lat, name: n }); setView({ lon, my: mapY(lat), z: Math.max(f.z, FOUND_ZOOM) }); }} />}
            {at && atXY && birth && <Inspector at={at} spot={{ left: (atXY[0] + 720) / 14.4, top: (atXY[1] + height / 2) / height * 100 }} birth={birth}  name={name} />}
          </div>
        </div>
        <div role="group" aria-label="Zoom" className="astro-nav">
          <button aria-label="Zoom in" title="Zoom in (or scroll on the map)" disabled={f.z >= MAX_ZOOM} onClick={() => zoom(1.5)}><Icon name="plus" /></button>
          <button aria-label="Zoom out" title="Zoom out (or scroll on the map)" disabled={f.z <= 1} onClick={() => zoom(1 / 1.5)}><Icon name="minus" /></button>
          <button aria-label="Birth place" title="Back to the birth place" disabled={view === "birth"} onClick={() => setView("birth")}><Icon name="pin" /></button>
          <button aria-label="Another date, time and place" title="Map this chart for another date, time and place" aria-pressed={mine} onClick={() => setEditing(true)}><Icon name="edit" /></button>
          <button aria-label="Places by life area" title="Countries and cities for career, travel, settling abroad, education and partners" className="sparkle" aria-pressed={insights} onClick={() => setInsights(!insights)}><Icon name="insights" /></button>
          {mine && <button aria-label="Back to the birth chart" title="Back to the birth date, time and place" onClick={() => setKept(null)}><Icon name="natal" /></button>}
        </div>
        {editing && natal && birth && (
          <BirthDialog open noName title="Map for another date, time and place" seed={{ name, birth, meta: mine ? kept[2] : meta }}
            onClose={() => setEditing(false)} onSave={(_, b, m) => setKept([JSON.stringify(natal), { ...natal, ...b }, m])} />
        )}
        <div className="astro-controls">
          <div role="group" aria-label="Layers" className="astro-chips">
            {LAYERS.map(([id, n]) => (
              <button key={id} aria-pressed={on(id)} title={id === "bhavas" && bhavas && !bhavas[0].cusp ? "Each border is also a cusp, with the Lagna at the start of the first bhava" : undefined} onClick={() => setLayers(toggled(layers, id))}>
                <svg className={`dash ${id}`} width="18" height="6" aria-hidden><line x1="0" x2="18" y1="3" y2="3" /></svg>{n}
              </button>
            ))}
            {bhavas?.[0].cusp && (
              <button aria-pressed={!off("cusps")} disabled={f.z <= 1.5} title={f.z <= 1.5 ? "Zoom in to see the bhava cusps" : "The middle of each bhava"} onClick={() => setHidden(toggled(hidden, "cusps"))}>
                <svg className="dash cusps" width="18" height="6" aria-hidden><line x1="0" x2="18" y1="3" y2="3" /></svg>Cusps
              </button>
            )}
          </div>
          {on("bhavas") && (
            <>
              <label>
                <select className="astro-system" aria-label="Bhava system" value={system} onChange={(e) => setSystem(e.target.value)}>{SYSTEMS.map(([v, n]) => <option key={v} value={v}>{n}</option>)}</select>
              </label>
              <label title={of === "Lagna" ? "Bhava numbers: the natal bhava the Lagna there falls in" : `Bhava numbers: ${of}'s bhava in the chart cast there`}>Ref
                <select value={of} onChange={(e) => setOf(e.target.value)}>
                  <option value="Lagna">Lagna</option>
                  {GRAHAS.map(([k, n]) => <option key={k} value={n}>{n}</option>)}
                </select>
              </label>
            </>
          )}
          <div role="group" aria-label="Grahas" className="astro-chips">
            {GRAHAS.map(([k, n]) => (
              <button key={k} aria-pressed={!off(k)} title={n} onClick={() => setHidden(toggled(hidden, k))} style={{ "--g": `var(--g-${k})` } as React.CSSProperties}>
                <i className="swatch" />{shown(k, display)}
              </button>
            ))}
            {(() => {
              const any = GRAHAS.some(([k]) => !off(k));
              const rest = hidden.split(",").filter((x) => x && !NAME[x]);   // the cusps toggle stays as it was
              return <button onClick={() => setHidden([...rest, ...(any ? GRAHAS.map(([k]) => k) : [])].join(","))}>{any ? "Unselect all" : "Select all"}</button>;
            })()}
          </div>
          <PlaceSearch found={found && found[0] === JSON.stringify(birth) ? found[1] : here} onPick={(p) => { setFound([JSON.stringify(birth), { city: p.name, state: p.admin1_name ?? undefined, country: p.country_code, tz: p.tz_standard }]); setAt({ lon: p.longitude, lat: p.latitude, name: p.name, alt: p.altitude }); setView({ lon: p.longitude, my: mapY(p.latitude), z: Math.max(f.z, FOUND_ZOOM) }); }} />
        </div>
      </div>
    </section>
  );
}
