/** The Muhurta tab's arithmetic: clock text, the day dial's geometry, and reading the day at one moment.
 * Times are hours since midnight of the day's date (past midnight runs on as 24+), read from local ISO strings. */
export type Clock = "12" | "24" | "vedic";

/** Hours (0..24+) since midnight of `day` ("YYYY-MM-DD"), reading the ISO time as written; past midnight gives 24+. */
export function hoursOn(iso: string, day: string): number {
  const days = Math.round((Date.parse(iso.slice(0, 10) + "T00:00:00Z") - Date.parse(day + "T00:00:00Z")) / 86_400_000);
  return days * 24 + Number(iso.slice(11, 13)) + Number(iso.slice(14, 16)) / 60 + Number(iso.slice(17, 19) || 0) / 3600;
}

/** "6:39 AM", "06:39" or "4:12" (ghati:pala since sunrise, 60 ghati to a day); another day than the date carries "+1". */
export function hourText(h: number, rise: number, clock: Clock): string {
  if (clock === "vedic") {
    const pala = Math.round((h - rise) * 150);                 // 1 hour = 2.5 ghati = 150 pala
    return `${Math.floor(pala / 60)}:${String(pala % 60).padStart(2, "0")}`;
  }
  const mins = Math.floor(h * 60 + 1e-3);           // a tenth of a second of slack, so 13:59:59.99 reads 14:00
  const shift = Math.floor(mins / 1440), m = mins - shift * 1440;
  const hh = Math.floor(m / 60), mm = String(m % 60).padStart(2, "0");
  const text = clock === "24" ? `${String(hh).padStart(2, "0")}:${mm}` : `${hh % 12 || 12}:${mm} ${hh < 12 ? "AM" : "PM"}`;
  return shift === 0 ? text : `${text} ${shift > 0 ? "+" : "-"}${Math.abs(shift)}`;
}

export const vedic = (iso: string, sunrise: string) => hourText(hoursOn(iso, sunrise.slice(0, 10)), hoursOn(sunrise, sunrise.slice(0, 10)), "vedic");
export const clockText = (iso: string, day: string, sunrise: string, clock: Clock) => hourText(hoursOn(iso, day), hoursOn(sunrise, day), clock);

/** Sunrise, sunset and the next sunrise of the day, in hours. */
export interface Frame { rise: number; set: number; next: number }

/** The dial puts sunrise on the left horizon, the day over the top and the night under the bottom, so the eight
 * Choghadiyas (or Gowri parts) of day and of night each fill equal sectors. Degrees, counter-clockwise from the right. */
export function angleAt(h: number, f: Frame): number {
  if (h <= f.set) return 180 - (180 * (h - f.rise)) / (f.set - f.rise);
  return (-180 * (h - f.set)) / (f.next - f.set);
}

/** The moment at an angle of the dial (-180..180, as Math.atan2 gives it). */
export function hourAt(deg: number, f: Frame): number {
  if (deg >= 0) return f.rise + ((180 - deg) / 180) * (f.set - f.rise);
  return f.set + (-deg / 180) * (f.next - f.set);
}

export function polar(cx: number, cy: number, r: number, deg: number): [number, number] {
  const a = (deg * Math.PI) / 180;
  return [cx + r * Math.cos(a), cy - r * Math.sin(a)];
}

/** An SVG path for the ring sector between radii r0 < r1 from angle a down to angle b (clockwise on screen). */
export function sector(cx: number, cy: number, r0: number, r1: number, a: number, b: number): string {
  const large = a - b > 180 ? 1 : 0;
  const p = (r: number, d: number) => polar(cx, cy, r, d).map((v) => v.toFixed(2)).join(" ");
  return `M${p(r1, a)}A${r1} ${r1} 0 ${large} 1 ${p(r1, b)}L${p(r0, b)}A${r0} ${r0} 0 ${large} 0 ${p(r0, a)}Z`;
}

/** A named span of the day in hours; `good` is null where it has no quality (a sign, a tithi). */
export interface Span { name: string; from: number; to: number; good: boolean | null; parts?: Span[] }   // parts: what a merged span is made of

export function spansOf(rows: { name: string; start: string; end: string | null; good?: boolean | null }[], day: string, next: number): Span[] {
  return rows.map((r) => ({ name: r.name, from: hoursOn(r.start, day), to: r.end ? hoursOn(r.end, day) : next, good: r.good ?? null }));
}

export const spanAt = (spans: Span[], h: number) => spans.find((s) => s.from <= h && h < s.to);
export const spansAt = (spans: Span[], h: number) => spans.filter((s) => s.from <= h && h < s.to);

/** The spans every start avoids; Ganda Moola and Panchak only call for care, for some events. */
export const HARD_AVOID = new Set(["Rahu Kalam", "Yamaganda", "Gulika Kalam", "Dur Muhurta", "Varjyam", "Bhadra (Vishti)"]);

export interface Verdict { tone: "excellent" | "good" | "avoid"; because: string[]; until: number | null }

/** How the moment `h` reads: an avoid span wins, then the quality slot (Choghadiya or Gowri), lifted by an auspicious span. */
export function verdict(h: number, lens: Span[], avoid: Span[], auspicious: Span[]): Verdict {
  const bad = spansAt(avoid, h).filter((s) => HARD_AVOID.has(s.name));
  if (bad.length) return { tone: "avoid", because: bad.map((s) => s.name), until: Math.max(...bad.map((s) => s.to)) };
  const slot = spanAt(lens, h);
  if (slot && slot.good === false) return { tone: "avoid", because: [slot.name], until: slot.to };
  const lift = spansAt(auspicious, h);
  return { tone: lift.length ? "excellent" : "good", because: [...(slot ? [slot.name] : []), ...lift.map((s) => s.name)], until: null };
}

export interface Window { from: number; to: number; names: string[]; best: boolean }

/** The good stretches of the day: good quality slots with the hard avoid spans cut out, neighbours merged, at least
 * `min` hours long; `best` where an auspicious span (Abhijit, Amrit Siddhi ..) falls inside. */
export function goodWindows(lens: Span[], avoid: Span[], auspicious: Span[], min = 0.25): Window[] {
  const cuts = avoid.filter((s) => HARD_AVOID.has(s.name));
  const pieces: Window[] = [];
  for (const s of lens.filter((x) => x.good)) {
    let parts: [number, number][] = [[s.from, s.to]];
    for (const c of cuts) {
      parts = parts.flatMap(([a, b]): [number, number][] => (c.to <= a || c.from >= b ? [[a, b]] : [...(a < c.from ? [[a, c.from] as [number, number]] : []), ...(c.to < b ? [[c.to, b] as [number, number]] : [])]));
    }
    for (const [a, b] of parts) {
      const last = pieces[pieces.length - 1];
      if (last && Math.abs(last.to - a) < 1e-9) { last.to = b; if (!last.names.includes(s.name)) last.names.push(s.name); }
      else pieces.push({ from: a, to: b, names: [s.name], best: false });
    }
  }
  return pieces.filter((w) => w.to - w.from >= min - 1e-9).map((w) => ({ ...w, best: auspicious.some((x) => x.from < w.to && w.from < x.to) }));
}

/** A tick of the dial's clock: every quarter hour (or ghati), the whole hours (or every fifth ghati) major and labelled. */
export interface Tick { h: number; major: boolean; label: string | null }

export function ticks(f: Frame, clock: Clock): Tick[] {
  const out: Tick[] = [];
  if (clock === "vedic") {
    for (let g = 0; g < 60; g++) out.push({ h: f.rise + g * 0.4, major: g % 5 === 0, label: g % 5 === 0 ? String(g) : null });
    return out.filter((t) => t.h < f.next);
  }
  for (let q = Math.ceil(f.rise * 4); q / 4 < f.next; q++) {
    const h = q / 4, whole = q % 4 === 0, hh = ((h % 24) + 24) % 24;
    const label = !whole ? null : clock === "24" ? String(hh).padStart(2, "0") : hh === 12 ? "Noon" : hh === 0 ? "Midnight" : String(hh % 12);
    out.push({ h, major: whole, label });
  }
  return out;
}

export interface Rect { x: number; y: number; w: number; h: number }

/** Where a w×h popup goes so it never covers `seg`: beside it on the side `dir` points to (the way the segment faces
 * out of the dial), else on another side, kept inside `view`; if no side fits, the side that covers least. */
export function besidePlace(seg: Rect, dir: [number, number], w: number, h: number, view: Rect, gap = 12): { x: number; y: number } {
  const clamp = (v: number, lo: number, hi: number) => Math.max(lo, Math.min(v, Math.max(lo, hi)));
  const cx = seg.x + seg.w / 2, cy = seg.y + seg.h / 2;
  const at = {
    right: { x: seg.x + seg.w + gap, y: clamp(cy - h / 2, view.y, view.y + view.h - h) },
    left: { x: seg.x - gap - w, y: clamp(cy - h / 2, view.y, view.y + view.h - h) },
    above: { x: clamp(cx - w / 2, view.x, view.x + view.w - w), y: seg.y - gap - h },
    below: { x: clamp(cx - w / 2, view.x, view.x + view.w - w), y: seg.y + seg.h + gap },
  };
  const [hx, vy] = [dir[0] >= 0 ? "right" : "left", dir[1] <= 0 ? "above" : "below"] as const;
  const [ox, oy] = [hx === "right" ? "left" : "right", vy === "above" ? "below" : "above"] as const;
  const order = Math.abs(dir[0]) >= Math.abs(dir[1]) ? [hx, vy, oy, ox] : [vy, hx, ox, oy];
  const inside = (p: { x: number; y: number }) => p.x >= view.x && p.y >= view.y && p.x + w <= view.x + view.w && p.y + h <= view.y + view.h;
  const overlap = (p: { x: number; y: number }) =>
    Math.max(0, Math.min(p.x + w, seg.x + seg.w) - Math.max(p.x, seg.x)) * Math.max(0, Math.min(p.y + h, seg.y + seg.h) - Math.max(p.y, seg.y));
  const fit = order.map((k) => at[k]).find(inside);
  if (fit) return fit;
  // nothing fits whole: pull each choice into view and take the one covering the segment least
  const pulled = order.map((k) => ({ x: clamp(at[k].x, view.x, view.x + view.w - w), y: clamp(at[k].y, view.y, view.y + view.h - h) }));
  return pulled.reduce((best, p) => (overlap(p) < overlap(best) ? p : best));
}

/** Spans that overlap get their own lane within a band (r0..r1), so each shows separately: the first that ends first
 * keeps the outer lane, a span starting before it ends goes inside. */
export function lanes(spans: Span[], r0: number, r1: number): { span: Span; r0: number; r1: number }[] {
  const ends: number[] = [];
  const placed = [...spans].sort((a, b) => a.from - b.from || b.to - a.to).map((span) => {
    let k = ends.findIndex((e) => e <= span.from + 1e-6);
    if (k < 0) { k = ends.length; ends.push(0); }
    ends[k] = span.to;
    return { span, k };
  });
  const w = (r1 - r0) / Math.max(1, ends.length);
  return placed.map(({ span, k }) => ({ span, r0: r1 - (k + 1) * w, r1: r1 - k * w }));
}

/** Spans that overlap or run end to end merge into one, which keeps them as its `parts` (in time order). */
export function mergeSpans(spans: Span[]): Span[] {
  const out: Span[] = [];
  for (const s of [...spans].sort((a, b) => a.from - b.from)) {
    const last = out[out.length - 1];
    if (last && s.from <= last.to + 1e-6) {
      last.to = Math.max(last.to, s.to);
      last.parts!.push(s);
      last.name = [...new Set(last.parts!.map((p) => p.name))].join(" + ");
    } else out.push({ ...s, parts: [s] });
  }
  return out;
}

