import { startTransition, useEffect, useMemo, useRef, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api, type FinanceBar, type FinanceEvent, type FinanceEventKind, type FinanceSuggest } from "./api";
import { useSaved } from "./hooks";
import { Icon } from "./Icons";
import { useChart } from "./store";

/** Preset window → Yahoo/CCXT range + interval; `ms` is the fixed span pan keeps while sliding. */
const RANGES: { id: string; label: string; range: string; interval: string; ms: number }[] = [
  { id: "H", label: "H", range: "1d", interval: "5m", ms: 86_400_000 },
  { id: "D", label: "D", range: "5d", interval: "15m", ms: 5 * 86_400_000 },
  { id: "W", label: "W", range: "1mo", interval: "60m", ms: 30 * 86_400_000 },
  { id: "M", label: "M", range: "1mo", interval: "1d", ms: 30 * 86_400_000 },
  { id: "3M", label: "3M", range: "3mo", interval: "1d", ms: 90 * 86_400_000 },
  { id: "6M", label: "6M", range: "6mo", interval: "1d", ms: 180 * 86_400_000 },
  { id: "Y", label: "Y", range: "1y", interval: "1d", ms: 365 * 86_400_000 },
];
/** How many timeframe-lengths to prefetch so pan slides locally without waiting on the network. */
const PAN_BUFFER = 3;
/** Distinct finance colours + stroke patterns (Rahu/Ketu share a tint elsewhere in the app). */
const GRAHAS: { id: string; abbr: string; color: string; dash: string }[] = [
  { id: "Sun", abbr: "Su", color: "#e8590c", dash: "" },
  { id: "Moon", abbr: "Mo", color: "#1c7ed6", dash: "2 3" },
  { id: "Mars", abbr: "Ma", color: "#e03131", dash: "6 3" },
  { id: "Mercury", abbr: "Me", color: "#2f9e44", dash: "1 2.5" },
  { id: "Jupiter", abbr: "Ju", color: "#f59f00", dash: "8 3 2 3" },
  { id: "Venus", abbr: "Ve", color: "#d6336c", dash: "4 2 1 2" },
  { id: "Saturn", abbr: "Sa", color: "#5f3dc4", dash: "10 4" },
  { id: "Rahu", abbr: "Ra", color: "#0c8599", dash: "3 2 3 5" },
  { id: "Ketu", abbr: "Ke", color: "#868e96", dash: "1 1.5" },
  { id: "Uranus", abbr: "Ur", color: "#15aabf", dash: "5 3 1 3" },
  { id: "Neptune", abbr: "Ne", color: "#4c6ef5", dash: "2 4" },
  { id: "Pluto", abbr: "Pl", color: "#ae3ec9", dash: "7 2 1 2" },
];
const EVENT_KINDS: { id: FinanceEventKind; label: string; mark: string }[] = [
  { id: "ingress", label: "Sign entry", mark: "▸" },
  { id: "station", label: "Retrograde", mark: "↺" },
  { id: "combustion", label: "Combustion", mark: "☼" },
  { id: "conjunction", label: "Conjunction", mark: "☌" },
  { id: "opposition", label: "Opposition", mark: "☍" },
  { id: "eclipse", label: "Eclipse", mark: "●" },
];
/** Top strip reserved for zodiac / graha markers — price plot starts below it. */
const BAND = 58;
const PAD = { t: BAND + 8, r: 56, b: 28, l: 10 };

function grahaStyle(id: string) {
  return GRAHAS.find((g) => g.id === id) ?? GRAHAS[0];
}

function kindMeta(kind: string) {
  return EVENT_KINDS.find((k) => k.id === kind) ?? EVENT_KINDS[0];
}

function fmtPrice(n: number | null | undefined, currency?: string | null) {
  if (n == null || Number.isNaN(n)) return "—";
  const abs = Math.abs(n);
  const digits = abs >= 1000 ? 2 : abs >= 1 ? 2 : 4;
  const s = n.toLocaleString(undefined, { maximumFractionDigits: digits, minimumFractionDigits: digits });
  return currency ? `${s} ${currency}` : s;
}

function fmtWhen(ms: number, intraday: boolean) {
  const d = new Date(ms);
  return intraday
    ? d.toLocaleString(undefined, { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" })
    : d.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
}

function niceTicks(lo: number, hi: number, n = 5) {
  const span = hi - lo || 1;
  const step = 10 ** Math.floor(Math.log10(span / n));
  const err = n / (span / step);
  const mult = err <= 0.15 ? 10 : err <= 0.35 ? 5 : err <= 0.75 ? 2 : 1;
  const s = step * mult;
  const start = Math.ceil(lo / s) * s;
  const ticks: number[] = [];
  for (let v = start; v <= hi + s * 1e-9; v += s) ticks.push(v);
  return ticks;
}

function nearestBar(bars: FinanceBar[], t: number) {
  let best = bars[0], bestD = Infinity;
  for (const b of bars) {
    const d = Math.abs(b.t - t);
    if (d < bestD) { best = b; bestD = d; }
  }
  return best;
}

/** Body the event is “about” — combustion is the planet, not the Sun. */
function eventActor(e: FinanceEvent, grahas: Set<string>) {
  if (e.kind === "combustion") return e.bodies.find((b) => b !== "Sun") ?? e.bodies[0];
  return e.bodies.find((b) => grahas.has(b)) ?? e.bodies[0];
}

function eventMatches(e: FinanceEvent, grahas: Set<string>) {
  if (e.kind === "combustion") return grahas.has(e.bodies.find((b) => b !== "Sun") ?? "");
  return e.bodies.some((b) => grahas.has(b));
}

function eventColor(e: FinanceEvent, grahas: Set<string>) {
  return grahaStyle(eventActor(e, grahas)).color;
}

function eventAbbr(e: FinanceEvent, grahas: Set<string>) {
  return grahaStyle(eventActor(e, grahas)).abbr;
}

/** Glyph in the top band: shape encodes event kind, colour + letters encode the graha. */
function EventMark({ x, bandY, e, grahas, focus, guideY }: {
  x: number; bandY: number; e: FinanceEvent; grahas: Set<string>; focus: boolean; guideY: number;
}) {
  const g = grahaStyle(eventActor(e, grahas));
  const meta = kindMeta(e.kind);
  const cy = bandY + 28;
  const label = e.kind === "ingress" && e.sign ? e.sign.slice(0, 2)
    : e.kind === "station" ? (e.retrograde ? "(R)" : "(D)")
    : meta.mark;
  return (
    <g className={`finance-event kind-${e.kind}${focus ? " focus" : ""}`} style={{ "--ev": g.color } as React.CSSProperties}>
      <line className="finance-event-guide" x1={x} x2={x} y1={cy + 14} y2={guideY} strokeDasharray={g.dash || undefined} />
      {e.kind === "ingress" && (
        <>
          <polygon className="finance-event-shape" points={`${x},${cy - 13} ${x + 12},${cy + 8} ${x - 12},${cy + 8}`} />
          <text className="finance-event-sign" x={x} y={cy + 3} textAnchor="middle">{label}</text>
        </>
      )}
      {e.kind === "station" && (
        <>
          <rect className="finance-event-shape" x={x - 12} y={cy - 12} width={24} height={24} rx={4} />
          <text className="finance-event-glyph station" x={x} y={cy} dy=".35em" textAnchor="middle">{label}</text>
        </>
      )}
      {e.kind === "combustion" && (
        <>
          <circle className="finance-event-shape ring" cx={x} cy={cy} r={13} />
          <circle className="finance-event-shape" cx={x} cy={cy} r={6} />
          <text className="finance-event-glyph dark" x={x} y={cy} dy=".35em" textAnchor="middle">☼</text>
        </>
      )}
      {e.kind === "conjunction" && (
        <>
          <circle className="finance-event-shape" cx={x - 5} cy={cy} r={9} />
          <circle className="finance-event-shape ghost" cx={x + 5} cy={cy} r={9} />
          <text className="finance-event-glyph" x={x} y={cy} dy=".35em" textAnchor="middle">☌</text>
        </>
      )}
      {e.kind === "opposition" && (
        <>
          <line className="finance-event-shape-stroke" x1={x - 13} y1={cy} x2={x + 13} y2={cy} />
          <circle className="finance-event-shape" cx={x - 10} cy={cy} r={6} />
          <circle className="finance-event-shape hollow" cx={x + 10} cy={cy} r={6} />
        </>
      )}
      {e.kind === "eclipse" && (
        <>
          <circle className="finance-event-shape eclipse" cx={x} cy={cy} r={12} />
          <circle className="finance-event-shape eclipse-core" cx={x + 3} cy={cy} r={12} />
        </>
      )}
      <rect className="finance-event-badge" x={x - 15} y={bandY + 2} width={30} height={16} rx={4} />
      <text className="finance-event-abbr" x={x} y={bandY + 10} dy=".35em" textAnchor="middle">{g.abbr}</text>
    </g>
  );
}

function PriceChart({
  bars, fullBars, events, style, tool, grahas, kinds, hoverBar, setHoverBar, selection, setSelection,
  view, setView, windowMs, onSlide, width, height, intraday,
}: {
  bars: FinanceBar[];
  fullBars: FinanceBar[];
  events: FinanceEvent[];
  style: "line" | "candle";
  tool: "pan" | "measure";
  grahas: Set<string>;
  kinds: Set<string>;
  hoverBar: FinanceBar | null;
  setHoverBar: (b: FinanceBar | null) => void;
  selection: { a: number; b: number } | null;
  setSelection: (s: { a: number; b: number } | null) => void;
  view: { a: number; b: number } | null;
  setView: (v: { a: number; b: number } | null) => void;
  /** Fixed timeframe length (ms) — pan slides this window without changing its size. */
  windowMs: number;
  /** Commit a slide: positive dtMs moves the window later, negative earlier. */
  onSlide: (dtMs: number) => void;
  width: number;
  height: number;
  intraday: boolean;
}) {
  const svg = useRef<SVGSVGElement>(null);
  const drag = useRef<
    | { mode: "pan"; pointerId: number; lastX: number; moved: boolean }
    | { mode: "sel"; pointerId: number; startT: number }
    | null
  >(null);
  const [panning, setPanning] = useState(false);
  const plotW = Math.max(40, width - PAD.l - PAD.r);
  const plotH = Math.max(40, height - PAD.t - PAD.b);
  const t0 = bars[0].t, t1 = bars[bars.length - 1].t;
  const highs = bars.map((b) => b.h ?? b.c);
  const lows = bars.map((b) => b.l ?? b.c);
  const lo = Math.min(...lows), hi = Math.max(...highs);
  const pad = (hi - lo) * 0.06 || hi * 0.02 || 1;
  const y0 = lo - pad, y1 = hi + pad;
  const xAt = (t: number) => PAD.l + ((t - t0) / (t1 - t0 || 1)) * plotW;
  const yAt = (c: number) => PAD.t + (1 - (c - y0) / (y1 - y0 || 1)) * plotH;
  const tAt = (x: number) => t0 + ((x - PAD.l) / plotW) * (t1 - t0);
  const yTicks = niceTicks(y0, y1);
  const candleW = Math.max(2, Math.min(10, (plotW / Math.max(bars.length, 1)) * 0.65));
  const baseY = PAD.t + plotH;

  const line = bars.map((b, i) => `${i ? "L" : "M"}${xAt(b.t).toFixed(1)},${yAt(b.c).toFixed(1)}`).join("");
  const area = `${line} L${xAt(t1).toFixed(1)},${baseY.toFixed(1)} L${xAt(t0).toFixed(1)},${baseY.toFixed(1)} Z`;

  const shown = useMemo(
    () => events.filter((e) => e.t >= t0 && e.t <= t1 && kinds.has(e.kind) && eventMatches(e, grahas)),
    [events, t0, t1, grahas, kinds],
  );

  const pick = (clientX: number, el: Element) => {
    const rect = el.getBoundingClientRect();
    const x = ((clientX - rect.left) / rect.width) * width;
    return nearestBar(bars, tAt(x));
  };

  // Keep latest inputs in a ref so pointer handlers never go stale mid-drag.
  const panRef = useRef({ tool, windowMs, plotW, width, onSlide, setView });
  panRef.current = { tool, windowMs, plotW, width, onSlide, setView };

  const endDrag = () => { drag.current = null; setPanning(false); };

  const onPointerDown = (e: React.PointerEvent<SVGSVGElement>) => {
    if (e.button !== 0) return;
    const bar = pick(e.clientX, e.currentTarget);
    setHoverBar(bar);
    e.currentTarget.setPointerCapture(e.pointerId);
    if (panRef.current.tool === "measure") {
      drag.current = { mode: "sel", pointerId: e.pointerId, startT: bar.t };
      setSelection({ a: bar.t, b: bar.t });
      return;
    }
    drag.current = { mode: "pan", pointerId: e.pointerId, lastX: e.clientX, moved: false };
    setPanning(true);
    setSelection(null);
    panRef.current.setView(null);
  };
  const onPointerMove = (e: React.PointerEvent<SVGSVGElement>) => {
    const d = drag.current;
    if (d?.mode === "pan" && d.pointerId === e.pointerId) {
      const dxPx = e.clientX - d.lastX;
      if (Math.abs(dxPx) < 1) return;
      d.moved = true;
      d.lastX = e.clientX;
      const { windowMs: wms, plotW: pw, width: w, onSlide: slide } = panRef.current;
      const rect = e.currentTarget.getBoundingClientRect();
      const dxView = (dxPx / rect.width) * w;
      // Drag right → earlier data; visible span stays windowMs (slides inside the prefetch buffer).
      slide(-(dxView / pw) * wms);
      return;
    }
    const bar = pick(e.clientX, e.currentTarget);
    setHoverBar(bar);
    if (d?.mode === "sel" && d.pointerId === e.pointerId) {
      setSelection({ a: d.startT, b: bar.t });
    }
  };
  const onPointerUp = (e: React.PointerEvent<SVGSVGElement>) => {
    const d = drag.current;
    if (!d || d.pointerId !== e.pointerId) return;
    endDrag();
    if (d.mode === "sel") {
      const bar = pick(e.clientX, e.currentTarget);
      if (Math.abs(d.startT - bar.t) < (t1 - t0) * 0.002) setSelection(null);
      else setSelection({ a: d.startT, b: bar.t });
    }
  };

  // Native wheel listener (React's is passive — can't preventDefault). Scroll down = zoom in, up = out.
  const zoomRef = useRef({ fullBars, view, setView, setSelection, width, plotW });
  zoomRef.current = { fullBars, view, setView, setSelection, width, plotW };
  useEffect(() => {
    const el = svg.current;
    if (!el) return;
    let acc = 1, anchorX = 0, frame = 0;
    const wheel = (e: WheelEvent) => {
      e.preventDefault();
      acc *= Math.exp(e.deltaY * (e.ctrlKey ? 0.012 : 0.003));
      anchorX = e.clientX;
      frame ||= requestAnimationFrame(() => {
        const { fullBars: all, view: v, setView: setV, setSelection: setSel, width: w, plotW: pw } = zoomRef.current;
        const scale = acc; acc = 1; frame = 0;
        if (all.length < 2 || !(scale > 1.0001 || scale < 0.9999)) return;
        const full0 = all[0].t, full1 = all[all.length - 1].t;
        const fullSpan = full1 - full0 || 1;
        const cur0 = v ? Math.min(v.a, v.b) : full0;
        const cur1 = v ? Math.max(v.a, v.b) : full1;
        const curSpan = cur1 - cur0 || fullSpan;
        const minSpan = Math.max(fullSpan * 0.02, (fullSpan / Math.max(all.length - 1, 1)) * 4);
        const nextSpan = Math.min(fullSpan, Math.max(minSpan, curSpan / scale));
        const rect = el.getBoundingClientRect();
        const x = ((anchorX - rect.left) / rect.width) * w;
        const frac = pw > 0 ? Math.max(0, Math.min(1, (x - PAD.l) / pw)) : 0.5;
        const pivot = cur0 + frac * curSpan;
        let a = pivot - nextSpan * frac;
        let b = a + nextSpan;
        if (a < full0) { a = full0; b = Math.min(full1, a + nextSpan); }
        if (b > full1) { b = full1; a = Math.max(full0, b - nextSpan); }
        setV(a <= full0 + 1 && b >= full1 - 1 ? null : { a, b });
        setSel(null);
      });
    };
    el.addEventListener("wheel", wheel, { passive: false });
    return () => { el.removeEventListener("wheel", wheel); cancelAnimationFrame(frame); };
  }, []);

  const sel = selection && (() => {
    const left = Math.min(selection.a, selection.b), right = Math.max(selection.a, selection.b);
    const from = nearestBar(bars, left), to = nearestBar(bars, right);
    const pct = from.c ? ((to.c - from.c) / from.c) * 100 : 0;
    const slice = bars.filter((b) => b.t >= from.t && b.t <= to.t);
    if (slice.length < 2) return null;
    const path = slice.map((b, i) => `${i ? "L" : "M"}${xAt(b.t).toFixed(1)},${yAt(b.c).toFixed(1)}`).join("");
    const under = `${path} L${xAt(slice[slice.length - 1].t).toFixed(1)},${baseY.toFixed(1)} L${xAt(slice[0].t).toFixed(1)},${baseY.toFixed(1)} Z`;
    return { x1: xAt(from.t), x2: xAt(to.t), from, to, pct, under, midX: (xAt(from.t) + xAt(to.t)) / 2 };
  })();

  const focus = hoverBar && (() => {
    const tol = (t1 - t0) * 0.012 + (intraday ? 20 * 60_000 : 18 * 3600_000);
    const near = shown.filter((e) => Math.abs(e.t - hoverBar.t) <= tol).sort((a, b) => Math.abs(a.t - hoverBar.t) - Math.abs(b.t - hoverBar.t));
    return near[0] ?? null;
  })();

  return (
    <>
      <svg ref={svg} className={`finance-svg tool-${tool}${panning ? " panning" : ""}`} width={width} height={height} viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Price chart"
        onPointerDown={onPointerDown} onPointerMove={onPointerMove} onPointerUp={onPointerUp}
        onPointerCancel={endDrag} onLostPointerCapture={endDrag}
        onPointerLeave={() => { if (!drag.current) setHoverBar(null); }}>
        <defs>
          <linearGradient id="finance-fill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="var(--accent)" stopOpacity="0.18" />
            <stop offset="100%" stopColor="var(--accent)" stopOpacity="0" />
          </linearGradient>
          <clipPath id="finance-plot-clip">
            <rect x={PAD.l} y={0} width={plotW} height={height} />
          </clipPath>
        </defs>

        {yTicks.map((v) => (
          <g key={v}>
            <line className="finance-grid" x1={PAD.l} x2={PAD.l + plotW} y1={yAt(v)} y2={yAt(v)} />
            <text className="finance-axis" x={width - 6} y={yAt(v)} dy=".35em" textAnchor="end">{fmtPrice(v)}</text>
          </g>
        ))}

        <g clipPath="url(#finance-plot-clip)">
          <rect className="finance-band" x={PAD.l} y={4} width={plotW} height={BAND} rx={4} />
          <line className="finance-band-rule" x1={PAD.l} x2={PAD.l + plotW} y1={PAD.t - 4} y2={PAD.t - 4} />
          <text className="finance-axis" x={PAD.l} y={height - 8}>{fmtWhen(t0, intraday)}</text>
          <text className="finance-axis" x={PAD.l + plotW} y={height - 8} textAnchor="end">{fmtWhen(t1, intraday)}</text>

          {style === "line" ? (
            <>
              <path className="finance-area" d={area} />
              <path className="finance-line" d={line} />
            </>
          ) : (
            <g className="finance-candles">
              {bars.map((b) => {
                const o = b.o ?? b.c, h = b.h ?? b.c, l = b.l ?? b.c, up = b.c >= o;
                const x = xAt(b.t);
                return (
                  <g key={b.t} className={up ? "up" : "down"}>
                    <line x1={x} x2={x} y1={yAt(h)} y2={yAt(l)} />
                    <rect x={x - candleW / 2} y={yAt(Math.max(o, b.c))} width={candleW} height={Math.max(1, Math.abs(yAt(o) - yAt(b.c)))} />
                  </g>
                );
              })}
            </g>
          )}

          {sel && (
            <g className={`finance-sel ${sel.pct >= 0 ? "up" : "down"}`}>
              <path className="finance-sel-area" d={sel.under} />
              <text x={sel.midX} y={PAD.t + 16} textAnchor="middle">
                {sel.pct >= 0 ? "+" : ""}{sel.pct.toFixed(2)}%
              </text>
            </g>
          )}

          {shown.map((e, i) => (
            <EventMark key={`${e.kind}-${e.t}-${i}`} x={xAt(e.t)} bandY={4} e={e} grahas={grahas}
              focus={!!focus && focus.t === e.t && focus.kind === e.kind} guideY={baseY} />
          ))}

          {hoverBar && (
            <g className="finance-cross">
              <line x1={xAt(hoverBar.t)} x2={xAt(hoverBar.t)} y1={PAD.t} y2={baseY} />
              <circle cx={xAt(hoverBar.t)} cy={yAt(hoverBar.c)} r={3.5} />
            </g>
          )}
        </g>
      </svg>
      {focus && hoverBar && (
        <div className="finance-callout" style={{
          left: Math.min(Math.max(xAt(focus.t), 8), width - 200),
          top: Math.min(Math.max(BAND + 8, yAt(hoverBar.c) + 12), height - 72),
          "--ev": eventColor(focus, grahas),
        } as React.CSSProperties}>
          <strong>{eventAbbr(focus, grahas)} · {kindMeta(focus.kind).mark} {focus.label}</strong>
          <span>{focus.detail || focus.label}</span>
          <span className="muted">{fmtWhen(focus.t, intraday)}</span>
        </div>
      )}
    </>
  );
}

function SymbolField({ value, onChange, onPick }: { value: string; onChange: (v: string) => void; onPick: (s: string) => void }) {
  const [open, setOpen] = useState(false);
  const [hi, setHi] = useState(0);
  const [q, setQ] = useState(value.trim());
  const box = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const t = setTimeout(() => setQ(value.trim()), 180);
    return () => clearTimeout(t);
  }, [value]);
  const search = useQuery({
    queryKey: ["finance-search", q],
    queryFn: () => api.financeSearch(q),
    enabled: open && q.length >= 1,
    staleTime: 60_000,
  });
  const hits = search.data ?? [];
  useEffect(() => { setHi(0); }, [hits]);
  useEffect(() => {
    const hide = (e: MouseEvent) => { if (box.current && !box.current.contains(e.target as Node)) setOpen(false); };
    document.addEventListener("mousedown", hide);
    return () => document.removeEventListener("mousedown", hide);
  }, []);
  const pick = (s: FinanceSuggest | string) => {
    const sym = typeof s === "string" ? s : s.symbol;
    onChange(sym);
    onPick(sym);
    setOpen(false);
  };
  return (
    <div className="finance-symbol" ref={box}>
      <input value={value} aria-label="Symbol" placeholder="AAPL or BTC/USDT" spellCheck={false} autoComplete="off"
        aria-autocomplete="list" aria-expanded={open && hits.length > 0}
        onChange={(e) => { onChange(e.target.value); setOpen(true); }}
        onFocus={() => setOpen(true)}
        onKeyDown={(e) => {
          if (!open || !hits.length) return;
          if (e.key === "ArrowDown") { e.preventDefault(); setHi((i) => Math.min(i + 1, hits.length - 1)); }
          else if (e.key === "ArrowUp") { e.preventDefault(); setHi((i) => Math.max(i - 1, 0)); }
          else if (e.key === "Enter" && hits[hi]) { e.preventDefault(); pick(hits[hi]); }
          else if (e.key === "Escape") setOpen(false);
        }} />
      {open && q.length >= 1 && (hits.length > 0 || search.isFetching) && (
        <ul className="finance-suggest" role="listbox">
          {search.isFetching && !hits.length && <li className="muted">Searching…</li>}
          {hits.map((h, i) => (
            <li key={h.symbol} role="option" aria-selected={i === hi} className={i === hi ? "hi" : undefined}
              onMouseEnter={() => setHi(i)} onMouseDown={(e) => { e.preventDefault(); pick(h); }}>
              <strong>{h.symbol}</strong>
              <span>{h.name}</span>
              <em>{h.exchange || h.source}</em>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export function Finance() {
  const { birth } = useChart();
  const [symbol, setSymbol] = useSaved<string>("financeSymbol", "AAPL");
  const [draft, setDraft] = useState(symbol);
  const [rangeId, setRangeId] = useSaved<string>("financeRangeId", "Y");
  const [style, setStyle] = useSaved<string>("financeStyle", "line");
  const [tool, setTool] = useSaved<string>("financeTool", "pan");
  // empty grahas by default — chart stays readable until the user picks some
  const [shownGrahas, setShownGrahas] = useSaved<string>("financeGrahas", "");
  const [shownKinds, setShownKinds] = useSaved<string>("financeEventKinds", EVENT_KINDS.map((k) => k.id).join(","));
  const grahas = useMemo(() => new Set(shownGrahas.split(",").filter(Boolean)), [shownGrahas]);
  const kinds = useMemo(() => new Set(shownKinds.split(",").filter(Boolean)), [shownKinds]);
  const preset = RANGES.find((r) => r.id === rangeId) ?? RANGES[RANGES.length - 1];
  const box = useRef<HTMLDivElement>(null);
  const [size, setSize] = useState({ width: 0, height: 0 });
  const [hoverBar, setHoverBar] = useState<FinanceBar | null>(null);
  const [selection, setSelection] = useState<{ a: number; b: number } | null>(null);
  /** Zoom window inside the visible timeframe; null = show the full selected timeframe. */
  const [view, setView] = useState<{ a: number; b: number } | null>(null);
  /** End of the prefetch buffer (ms); null = live. Refetch only when pan nears a buffer edge. */
  const [bufferEndMs, setBufferEndMs] = useState<number | null>(null);
  /** End of the visible fixed-length window inside the buffer. */
  const [windowEnd, setWindowEnd] = useState<number | null>(null);
  const prefetchTimer = useRef(0);

  useEffect(() => {
    const el = box.current;
    if (!el) return;
    const ro = new ResizeObserver(([e]) => {
      const { width, height } = e.contentRect;
      if (width && height) setSize({ width: Math.round(width), height: Math.round(height) });
    });
    ro.observe(el);
    return () => ro.disconnect();
  }, []);
  const { width, height } = size;

  useEffect(() => { setDraft(symbol); }, [symbol]);
  useEffect(() => {
    setSelection(null); setHoverBar(null); setView(null);
    setBufferEndMs(null); setWindowEnd(null);
  }, [symbol, rangeId, style]);

  const ohlc = useQuery({
    queryKey: ["finance-ohlc", symbol, preset.range, preset.interval, bufferEndMs, PAN_BUFFER],
    queryFn: () => api.financeOhlc(symbol, preset.range, preset.interval, undefined, bufferEndMs, PAN_BUFFER),
    enabled: !!symbol.trim(),
    staleTime: 120_000,
    placeholderData: (prev) => prev,
  });

  const bars = ohlc.data?.bars ?? [];
  const intraday = ["5m", "15m", "60m", "1m", "1h"].includes(preset.interval);

  // Keep the visible window pinned to the latest bar until the user pans.
  useEffect(() => {
    if (bars.length < 2) return;
    const buf0 = bars[0].t, buf1 = bars[bars.length - 1].t;
    setWindowEnd((cur) => {
      if (cur == null) return buf1;
      const minEnd = buf0 + Math.min(preset.ms, buf1 - buf0);
      return Math.min(buf1, Math.max(minEnd, cur));
    });
  }, [bars, preset.ms]);

  const slideWindow = (dtMs: number) => {
    if (bars.length < 2) return;
    const live = Date.now();
    const buf0 = bars[0].t, buf1 = bars[bars.length - 1].t;
    const cur = windowEnd ?? buf1;
    const minEnd = buf0 + Math.min(preset.ms, buf1 - buf0);
    const next = Math.min(live, buf1, Math.max(minEnd, cur + dtMs));
    startTransition(() => {
      setWindowEnd(next);
      setView(null);
    });

    // Prefetch a recentered buffer before the visible window hits either edge.
    const margin = preset.ms * 0.35;
    const nearLeft = next - preset.ms <= buf0 + margin;
    const nearRight = next >= buf1 - margin * 0.25;
    if (!nearLeft && !nearRight) return;
    const bufEnd = Math.min(live, Math.round(next + preset.ms * 0.5));
    const keyed = live - bufEnd < 60_000 ? null : bufEnd;
    window.clearTimeout(prefetchTimer.current);
    prefetchTimer.current = window.setTimeout(() => {
      setBufferEndMs((prev) => (prev === keyed ? prev : keyed));
    }, 160);
  };

  /** Fixed-length timeframe slice inside the prefetch buffer (what pan keeps constant). */
  const frameBars = useMemo(() => {
    if (bars.length < 2) return bars;
    const end = windowEnd ?? bars[bars.length - 1].t;
    const start = end - preset.ms;
    const slice = bars.filter((b) => b.t >= start && b.t <= end);
    return slice.length >= 2 ? slice : bars;
  }, [bars, windowEnd, preset.ms]);

  const shownBars = useMemo(() => {
    if (!view || frameBars.length < 2) return frameBars;
    const lo = Math.min(view.a, view.b), hi = Math.max(view.a, view.b);
    const zoomed = frameBars.filter((b) => b.t >= lo && b.t <= hi);
    return zoomed.length >= 2 ? zoomed : frameBars;
  }, [frameBars, view]);

  // Events cover the whole prefetch buffer so pan doesn't refetch on every drag frame.
  const bufferSpan = bars.length >= 2 ? { start: bars[0].t, end: bars[bars.length - 1].t } : null;
  const span = shownBars.length >= 2
    ? { start: shownBars[0].t, end: shownBars[shownBars.length - 1].t }
    : null;

  const kindList = useMemo(() => [...kinds] as FinanceEventKind[], [kinds]);
  const eventsQ = useQuery({
    queryKey: ["finance-events", birth, bufferSpan?.start, bufferSpan?.end, shownKinds],
    queryFn: () => api.financeEvents(birth!, bufferSpan!.start, bufferSpan!.end, kindList),
    enabled: !!birth && !!bufferSpan && grahas.size > 0 && kinds.size > 0,
    staleTime: 300_000,
    placeholderData: (prev) => prev,
  });

  const events = eventsQ.data ?? [];
  const last = frameBars[frameBars.length - 1] ?? bars[bars.length - 1];
  const first = frameBars[0] ?? bars[0];
  const change = last && first ? last.c - first.c : 0;
  const pct = last && first && first.c ? (change / first.c) * 100 : 0;
  const active = hoverBar ?? shownBars[shownBars.length - 1] ?? last;

  const nearEvents = useMemo(() => {
    if (!active || !span || grahas.size === 0 || kinds.size === 0) return [];
    const tol = (span.end - span.start) * 0.01 + (intraday ? 30 * 60_000 : 12 * 3600_000);
    return events.filter((e) => kinds.has(e.kind) && eventMatches(e, grahas) && Math.abs(e.t - active.t) <= tol).slice(0, 3);
  }, [active, events, grahas, kinds, span, intraday]);

  const toggleCsv = (value: string, set: (v: string) => void, id: string) => {
    const next = new Set(value.split(",").filter(Boolean));
    if (next.has(id)) next.delete(id); else next.add(id);
    set([...next].join(","));
  };

  const selPct = selection && shownBars.length ? (() => {
    const from = nearestBar(shownBars, Math.min(selection.a, selection.b));
    const to = nearestBar(shownBars, Math.max(selection.a, selection.b));
    return from.c ? ((to.c - from.c) / from.c) * 100 : 0;
  })() : null;

  return (
    <section className="pane">
      <div className="finance">
        <div className="finance-head">
          <form className="finance-symbol-form" onSubmit={(e) => { e.preventDefault(); const s = draft.trim(); if (s) setSymbol(s); }}>
            <SymbolField value={draft} onChange={setDraft} onPick={(s) => setSymbol(s)} />
            <button type="submit" className="primary">Load</button>
          </form>
          <div role="group" aria-label="Range" className="finance-seg">
            {RANGES.map((r) => (
              <button key={r.id} type="button" aria-pressed={rangeId === r.id} onClick={() => setRangeId(r.id)}>{r.label}</button>
            ))}
          </div>
          <div role="group" aria-label="Chart style" className="finance-seg">
            <button type="button" aria-pressed={style === "line"} onClick={() => setStyle("line")}>Line</button>
            <button type="button" aria-pressed={style === "candle"} onClick={() => setStyle("candle")}>Candles</button>
          </div>
          <div role="group" aria-label="Drag tool" className="finance-seg finance-tool">
            <button type="button" aria-pressed={tool === "pan"} aria-label="Pan" title="Pan"
              onClick={() => { setTool("pan"); setSelection(null); }}><Icon name="hand" /></button>
            <button type="button" aria-pressed={tool === "measure"} aria-label="Measure %" title="Measure %"
              onClick={() => setTool("measure")}><Icon name="percent" /></button>
          </div>
          <div className="finance-meta">
            {ohlc.isPending ? <span className="muted">Loading…</span>
              : ohlc.isError ? <span role="alert" className="error">{ohlc.error.message}</span>
              : ohlc.data && last ? (
                <>
                  <strong>{ohlc.data.name || ohlc.data.symbol}</strong>
                  <span className="finance-price">{fmtPrice(last.c, ohlc.data.currency)}</span>
                  <span className={change >= 0 ? "up" : "down"}>{change >= 0 ? "+" : ""}{pct.toFixed(2)}%</span>
                  <span className="muted">{ohlc.data.source === "ccxt" ? `CCXT · ${ohlc.data.exchange}` : `Yahoo · ${ohlc.data.exchange || "equity"}`}</span>
                </>
              ) : null}
            {selPct != null && Math.abs(selection!.a - selection!.b) > 0 && (
              <span className={selPct >= 0 ? "up" : "down"}>Selection {selPct >= 0 ? "+" : ""}{selPct.toFixed(2)}%</span>
            )}
          </div>
        </div>

        <div ref={box} className="finance-chart">
          {shownBars.length >= 2 && width > 0 && height > 0 ? (
            <PriceChart
              bars={shownBars} fullBars={frameBars} events={events} style={style === "candle" ? "candle" : "line"}
              tool={tool === "measure" ? "measure" : "pan"} grahas={grahas} kinds={kinds}
              hoverBar={hoverBar} setHoverBar={setHoverBar} selection={selection} setSelection={setSelection}
              view={view} setView={setView} windowMs={preset.ms} onSlide={slideWindow}
              width={width} height={height} intraday={intraday}
            />
          ) : (
            <p className="empty">{ohlc.isPending ? "Fetching prices…" : "Enter a Yahoo ticker (AAPL, RELIANCE.NS) or a CCXT pair (BTC/USDT)."}</p>
          )}
          {eventsQ.isError && <p role="alert" className="error banner finance-error">{eventsQ.error.message}</p>}
        </div>

        <div className="finance-ohlc" aria-live="polite">
          {active ? (
            <>
              <span className="muted">{fmtWhen(active.t, intraday)}</span>
              <span>O <strong>{fmtPrice(active.o ?? active.c)}</strong></span>
              <span>H <strong>{fmtPrice(active.h ?? active.c)}</strong></span>
              <span>L <strong>{fmtPrice(active.l ?? active.c)}</strong></span>
              <span>C <strong>{fmtPrice(active.c)}</strong></span>
              {active.v != null && <span className="muted">Vol {active.v.toLocaleString()}</span>}
              {nearEvents.map((e, i) => (
                <span key={i} className="finance-tag" style={{ "--ev": eventColor(e, grahas) } as React.CSSProperties}
                  title={e.detail || e.label}>{eventAbbr(e, grahas)}: {e.detail || e.label}</span>
              ))}
            </>
          ) : <span className="muted">Hover for OHLC · drag to {tool === "measure" ? "measure %" : "slide timeframe"} · scroll to zoom</span>}
          <div role="group" aria-label="Event types" className="astro-chips finance-kinds">
            {EVENT_KINDS.map((k) => (
              <button key={k.id} type="button" aria-pressed={kinds.has(k.id)} title={k.label}
                onClick={() => toggleCsv(shownKinds, setShownKinds, k.id)}>
                {k.label}
              </button>
            ))}
          </div>
          {eventsQ.isFetching && <span className="muted">Overlays…</span>}
        </div>
        <div className="finance-grahas-row">
          <div role="group" aria-label="Graha overlays" className="astro-chips finance-grahas">
            {GRAHAS.map((g) => (
              <button key={g.id} type="button" aria-pressed={grahas.has(g.id)} title={g.id}
                onClick={() => toggleCsv(shownGrahas, setShownGrahas, g.id)} style={{ "--g": g.color } as React.CSSProperties}>
                <i className="swatch" />{g.abbr}
              </button>
            ))}
          </div>
          {grahas.size === 0 && <span className="muted">Select grahas to overlay events</span>}
        </div>
      </div>
    </section>
  );
}
