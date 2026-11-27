import { useEffect, useLayoutEffect, useRef, useState } from "react";
import { angleAt, besidePlace, hourAt, lanes, mergeSpans, polar, sector, type Frame, type Span, type Tick } from "./muhurtaMath";

export interface Ring { key: string; label: string; spans: Span[]; kind: "quality" | "planet" | "sign" | "limb" }
export interface Readout { time: string; tone: "excellent" | "good" | "avoid" | "plain"; word: string; lines: string[] }
export interface Pick { ring: string; span: Span }
export interface PopInfo { title: string; tone: "good" | "bad" | "plain"; time: string; lines: string[] }

const CORE = 130, OUTER = 290;                          // the readout's disc; the rings fill the space between
const AVOID_BAND: [number, number] = [294, 309], GOOD_BAND: [number, number] = [311, 322];   // overlapping spans split into lanes
const TICK = 326, TICK_END = 336, HOURS = 351;           // the clock: ticks and hour numbers outside the bands
const HALF = HOURS + 38;                                 // the canvas: a square just round the clock (and the sunrise times)
const PLANET: Record<string, string> = { Sun: "Su", Moon: "Mo", Mars: "Ma", Mercury: "Me", Jupiter: "Ju", Venus: "Ve", Saturn: "Sa" };
const SIGN: Record<string, string> = { Aries: "Ar", Taurus: "Ta", Gemini: "Ge", Cancer: "Cn", Leo: "Le", Virgo: "Vi", Libra: "Li", Scorpio: "Sc", Sagittarius: "Sg", Capricorn: "Cp", Aquarius: "Aq", Pisces: "Pi" };
const CX = HALF, CY = HALF;

const short = (r: Ring, name: string) => (r.kind === "planet" ? PLANET[name] ?? name : r.kind === "sign" ? SIGN[name] ?? name : name);
const bandsOf = (n: number): [number, number][] => {
  const gap = 2, w = (OUTER - CORE - 4 - gap * (n - 1)) / n;
  return Array.from({ length: n }, (_, k) => [OUTER - (k + 1) * w - k * gap, OUTER - k * w - k * gap]);
};

interface Hit extends Pick { r0: number; r1: number }

/** The day as a dial: sunrise on the left horizon, the day over the top, the night under it, a clock around the rim.
 * Hover a slot for its details; drag the hand, click, or use the arrow keys (shift for an hour) to read any moment;
 * Enter (or a tap on a touch screen) opens the details of the slot at the hand. */
export function Dial({ f, rings, avoid, auspicious, ticks, h, onH, now, readout, valueText, describe, riseText, setText }: {
  f: Frame; rings: Ring[]; avoid: Span[]; auspicious: Span[]; ticks: Tick[]; h: number; onH: (h: number) => void;
  now: number | null; readout: Readout; valueText: string; describe: (p: Pick) => PopInfo; riseText: string; setText: string;
}) {
  const svg = useRef<SVGSVGElement>(null), box = useRef<HTMLDivElement>(null), pop = useRef<HTMLDivElement>(null);
  const drag = useRef<{ x: number; y: number; moved: boolean } | null>(null);
  const [open, setOpen] = useState<Hit | null>(null);       // kept open: keyboard, touch
  const [hover, setHover] = useState<Hit | null>(null);     // follows the mouse
  const [size, setSize] = useState({ w: 302, h: 150 });     // the popup's, measured once drawn
  const bands = bandsOf(rings.length);
  // the times to avoid that overlap or follow one another show as one red stretch (its popup lists the parts);
  // the amber "take care" spans and the auspicious ones keep a lane each where they overlap
  const avoidLanes = lanes([...mergeSpans(avoid.filter((x) => x.good === false)), ...avoid.filter((x) => x.good !== false)], ...AVOID_BAND);
  const goodLanes = lanes(auspicious, ...GOOD_BAND);
  const clamp = (x: number) => Math.min(f.next - 1 / 120, Math.max(f.rise, x));

  // a click outside the popup (or Escape) closes it
  useEffect(() => {
    if (!open) return;
    const down = (e: PointerEvent) => { if (!pop.current?.contains(e.target as Node)) setOpen(null); };
    const esc = (e: KeyboardEvent) => { if (e.key === "Escape") setOpen(null); };
    document.addEventListener("pointerdown", down, true);
    document.addEventListener("keydown", esc);
    return () => { document.removeEventListener("pointerdown", down, true); document.removeEventListener("keydown", esc); };
  }, [open]);
  useEffect(() => { setOpen(null); setHover(null); }, [rings.length, f.rise]);       // another view or another day

  const toSvg = (cx: number, cy: number) => new DOMPoint(cx, cy).matrixTransform(svg.current!.getScreenCTM()!.inverse());
  const timeAt = (x: number, y: number) => hourAt((Math.atan2(-(y - CY), x - CX) * 180) / Math.PI, f);
  /** What lies under a point of the dial: a ring's slot, or a span of the outer bands (the shortest, where they overlap). */
  const hitAt = (x: number, y: number): Hit | null => {
    const r = Math.hypot(x - CX, y - CY), t = timeAt(x, y);
    // a span wholly before sunrise is drawn just under the left horizon, a day later on the dial's clock
    const inside = (s: Span) => { const k = s.to <= f.rise ? f.next - f.rise : 0; return s.from + k <= t && t < s.to + k; };
    const k = bands.findIndex(([r0, r1]) => r >= r0 - 1 && r <= r1 + 1);
    if (k >= 0) { const s = rings[k].spans.find(inside); return s ? { ring: rings[k].label, span: s, r0: bands[k][0], r1: bands[k][1] } : null; }
    const lane = [...avoidLanes, ...goodLanes].find((x) => r >= x.r0 - 0.5 && r <= x.r1 + 0.5 && inside(x.span));
    return lane ? { ring: "Span", ...lane } : null;
  };

  const down = (e: React.PointerEvent) => {
    const p = toSvg(e.clientX, e.clientY), r = Math.hypot(p.x - CX, p.y - CY);
    if (r < CORE || r > TICK_END + 6) return;
    drag.current = { x: e.clientX, y: e.clientY, moved: false };
    svg.current!.setPointerCapture(e.pointerId);
    onH(clamp(timeAt(p.x, p.y)));
  };
  const move = (e: React.PointerEvent) => {
    const p = toSvg(e.clientX, e.clientY);
    const d = drag.current;
    if (d) {
      if (Math.hypot(e.clientX - d.x, e.clientY - d.y) > 4) d.moved = true;
      if (Math.hypot(p.x - CX, p.y - CY) >= CORE) onH(clamp(timeAt(p.x, p.y)));
    }
    if (e.pointerType !== "mouse") return;
    const hit = hitAt(p.x, p.y);
    setHover(hit);
  };
  const up = (e: React.PointerEvent) => {
    const d = drag.current;
    drag.current = null;
    if (!d || d.moved || e.pointerType === "mouse") return;        // the mouse already has its hover popup
    const p = toSvg(e.clientX, e.clientY), hit = hitAt(p.x, p.y);
    setOpen(hit);
  };
  const key = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      const s = rings[0].spans.find((x) => x.from <= h && h < x.to);
      return setOpen(s ? { ring: rings[0].label, span: s, r0: bands[0][0], r1: bands[0][1] } : null);
    }
    const step = (e.shiftKey ? 60 : 5) / 60;
    const to = { ArrowRight: h + step, ArrowUp: h + step, ArrowLeft: h - step, ArrowDown: h - step, Home: f.rise, End: f.next }[e.key];
    if (to === undefined) return;
    e.preventDefault();
    setOpen(null);
    onH(clamp(to));
  };

  // a span wholly before sunrise (Brahma Muhurta) keeps its true place, just under the left horizon
  const ends = (s: Span): [number, number] => [angleAt(s.to <= f.rise ? s.from : Math.max(s.from, f.rise), f), angleAt(Math.min(s.to, f.next), f)];
  const arc = (s: Span, r0: number, r1: number) => sector(CX, CY, r0, r1, ...ends(s));
  const label = (text: string, s: Span, r0: number, r1: number, size: number) => {
    const [a, b] = ends(s), r = (r0 + r1) / 2;
    if ((r * (a - b) * Math.PI) / 180 < text.length * size * 0.58 + 6) return null;    // no room: hovering still names it
    const mid = (a + b) / 2, [x, y] = polar(CX, CY, r, mid);
    const turn = mid >= 0 ? 90 - mid : -90 - mid;      // along the ring, never upside down
    return <text x={x} y={y} transform={`rotate(${turn.toFixed(1)} ${x.toFixed(1)} ${y.toFixed(1)})`} className="mu-ring-label" style={{ fontSize: size }}>{text}</text>;
  };
  const hasBands = avoid.length + auspicious.length > 0;
  const handA = angleAt(h, f);
  const [hx0, hy0] = polar(CX, CY, CORE, handA), [hx1, hy1] = polar(CX, CY, TICK_END, handA), [kx, ky] = polar(CX, CY, TICK, handA);
  const ringSize = rings.length > 4 ? 14 : 15;
  // the readout: "1:12" large, "AM" and a next-day "+1" small; the font shrinks for long strings, the block centres in the disc
  const m = /^(.*?)(?: (AM|PM))?(?: ([+-]\d+))?$/.exec(readout.time)!;
  const clock = { main: m[1], half: m[2] ?? "", shift: m[3] ?? "" };
  const face = (() => {
    const ems = clock.main.length * 0.52 + clock.half.length * 0.36 + clock.shift.length * 0.3 + (clock.half ? 0.15 : 0);
    const size = Math.min(44, (2 * (CORE - 22)) / ems), n = Math.min(3, readout.lines.length);
    const cap = size * 0.7, total = cap + 30 + n * 19;
    const time = CY - total / 2 + cap;
    return { size, time, word: time + 30, lines: Array.from({ length: n }, (_, i) => time + 30 + 22 + i * 19) };
  })();
  /** The popup sits beside the segment (on screen, outside the dial where there is room), never over it. */
  const place = (hit: Hit): React.CSSProperties => {
    const m = svg.current?.getScreenCTM();
    if (!m) return { visibility: "hidden" };
    const [a, b] = ends(hit.span);
    const pts = Array.from({ length: 13 }, (_, i) => a + ((b - a) * i) / 12).flatMap((d) => [hit.r0 - 1, hit.r1 + 1].map((r) => new DOMPoint(...polar(CX, CY, r, d)).matrixTransform(m)));
    const xs = pts.map((p) => p.x), ys = pts.map((p) => p.y);
    const seg = { x: Math.min(...xs), y: Math.min(...ys), w: Math.max(...xs) - Math.min(...xs), h: Math.max(...ys) - Math.min(...ys) };
    const mid = (((a + b) / 2) * Math.PI) / 180;
    const p = besidePlace(seg, [Math.cos(mid), -Math.sin(mid)], size.w, size.h, { x: 8, y: 8, w: innerWidth - 16, h: innerHeight - 16 });
    return { position: "fixed", left: p.x, top: p.y };
  };
  const popEl = useRef<HTMLDivElement | null>(null);
  useLayoutEffect(() => {
    const r = popEl.current?.getBoundingClientRect();
    if (r && (Math.abs(r.width - size.w) > 1 || Math.abs(r.height - size.h) > 1)) setSize({ w: r.width, h: r.height });
  });
  const card = (info: PopInfo) => (<>
    <div className="mu-pop-head">
      <b>{info.title}</b>
      {info.tone !== "plain" && <span className="mu-pop-tag">{info.tone === "good" ? "Good" : "Avoid"}</span>}
    </div>
    <p className="mu-pop-time">{info.time}</p>
    {info.lines.map((l, i) => <p key={i}>{l}</p>)}
  </>);
  const sun = (text: string, when: string, left: boolean) => (
    <g className="mu-sun">
      <text x={CX + (left ? -1 : 1) * (HOURS + 10)} y={CY - 8} className="mu-sun-name">{text}</text>
      <text x={CX + (left ? -1 : 1) * (HOURS + 10)} y={CY + 11} className="mu-sun-time">{when}</text>
    </g>
  );

  return (
    <div className="mu-dial-box" ref={box}>
      <svg ref={svg} viewBox={`0 0 ${2 * HALF} ${2 * HALF}`} className="mu-dial" role="slider" tabIndex={0} aria-label="Moment of the day"
        aria-valuemin={f.rise} aria-valuemax={f.next} aria-valuenow={h} aria-valuetext={valueText} onKeyDown={key}
        onPointerDown={down} onPointerMove={move} onPointerUp={up} onPointerLeave={() => setHover(null)} onPointerCancel={() => { drag.current = null; }}>
        <path d={sector(CX, CY, CORE, GOOD_BAND[1] + 2, 180, 0)} className="mu-sky day" />
        <path d={sector(CX, CY, CORE, GOOD_BAND[1] + 2, 0, -180)} className="mu-sky night" />
        {rings.map((r, k) => {
          const [r0, r1] = bands[k];
          return (
            <g key={r.key} className={`mu-ring mu-${r.kind} mu-r${k}`}>
              {r.spans.filter((s) => s.to > f.rise && s.from < f.next).map((s, i) => (
                <g key={i}>
                  <path d={arc(s, r0, r1)} className={s.good === true ? "q-good" : s.good === false ? "q-bad" : `q-none alt${i % 2}`}
                    style={r.kind === "planet" ? { fill: `color-mix(in srgb, var(--g-${PLANET[s.name] ?? "Ke"}) 30%, var(--panel))` } : undefined} />
                  {label(short(r, s.name), s, r0, r1, ringSize)}
                </g>
              ))}
            </g>
          );
        })}
        <path d={sector(CX, CY, bands[rings.length - 1][0], OUTER, 0, -180)} className="mu-shade" />
        <g className="mu-dividers">
          {[...bands.map(([, r1]) => r1 + 1), bands[rings.length - 1][0] - 1].map((r, i) => <circle key={i} cx={CX} cy={CY} r={r} />)}
        </g>
        {hasBands && <g className="mu-events">
          {goodLanes.map((x, i) => <path key={"g" + i} d={arc(x.span, x.r0, x.r1)} className="ev-good" />)}
          {avoidLanes.map((x, i) => <path key={"a" + i} d={arc(x.span, x.r0, x.r1)} className={x.span.good === null ? "ev-care" : "ev-avoid"} />)}
        </g>}
        {/* where every slot starts and ends: a dark line across its ring */}
        <g className="mu-bounds" aria-hidden="true">
          {rings.flatMap((r, k) => r.spans.filter((x) => x.from > f.rise + 1e-6 && x.from < f.next - 1e-6).map((x, i) => {
            const a = angleAt(x.from, f), [x0, y0] = polar(CX, CY, bands[k][0], a), [x1, y1] = polar(CX, CY, bands[k][1], a);
            return <line key={k + "-" + i} x1={x0} y1={y0} x2={x1} y2={y1} />;
          }))}
        </g>

        <g className="mu-clock" aria-hidden="true">
          {ticks.map((t, i) => {
            const a = angleAt(t.h, f), [x0, y0] = polar(CX, CY, t.major ? TICK : TICK + 3.5, a), [x1, y1] = polar(CX, CY, TICK_END, a);
            const [lx, ly] = polar(CX, CY, HOURS, a);
            return <g key={i}><line x1={x0} y1={y0} x2={x1} y2={y1} className={t.major ? "major" : "minor"} />
              {t.label && Math.abs(Math.sin((a * Math.PI) / 180)) > 0.1 && <text x={lx} y={ly} className="mu-hour">{t.label}</text>}</g>;
          })}
          {sun("Sunrise", riseText, true)}
          {sun("Sunset", setText, false)}
        </g>

        {(open ?? hover) && <path d={arc((open ?? hover)!.span, (open ?? hover)!.r0 - 1, (open ?? hover)!.r1 + 1)} className="mu-hot" />}
        {now !== null && now >= f.rise && now < f.next && (() => { const [x, y] = polar(CX, CY, TICK_END + 4, angleAt(now, f)); return <circle cx={x} cy={y} r={4} className="mu-now" />; })()}
        <line x1={hx0} y1={hy0} x2={hx1} y2={hy1} className="mu-hand" />
        <circle cx={kx} cy={ky} r={8} className="mu-knob" />
        <circle cx={CX} cy={CY} r={CORE - 4} className="mu-core" />
        <text x={CX} y={face.time} className="mu-time" style={{ fontSize: face.size }}>
          {clock.main}
          {clock.half && <tspan className="mu-time-half" dx={face.size * 0.12}>{clock.half}</tspan>}
          {clock.shift && <tspan className="mu-time-shift" dx={face.size * 0.08} dy={-face.size * 0.36}>{clock.shift}</tspan>}
        </text>
        <text x={CX} y={face.word} className={`mu-word ${readout.tone}`}>{readout.word}</text>
        {face.lines.map((y, i) => <text key={i} x={CX} y={y} className="mu-why">{readout.lines[i]}</text>)}
      </svg>
      {hover && !open && (() => { const info = describe(hover); return <div ref={popEl} className={`mu-pop hover ${info.tone}`} aria-hidden="true" style={place(hover)}>{card(info)}</div>; })()}
      {open && (() => {
        const info = describe(open);
        return (
          <div ref={(el) => { pop.current = el; popEl.current = el; }} className={`mu-pop ${info.tone}`} role="dialog" aria-label={info.title} style={place(open)}>
            {card(info)}
          </div>
        );
      })()}
    </div>
  );
}
