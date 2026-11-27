// A chart's text: how big it is in the chart's own units, and where each body goes in its box.
const MAJOR = new Set(["As", "Su", "Mo", "Ma", "Me", "Ju", "Ve", "Sa", "Ra", "Ke", "Ur", "Ne", "Pl", "AK", "AmK", "BK", "MK", "PiK", "PK", "GK", "DK", "PLag", "Mu"]);     // the outer grahas drawn as the others
const STRIP = /^(A\d+|UL|V\d+)$/;
/** The chart's three kinds of body: planets large, other points small, house arudhas and varnadas in a strip along the bottom. */
export const bodyKind = (t: string) => (MAJOR.has(t.replace(/R$/, "")) ? "major" : STRIP.test(t) ? "strip" : "minor");

export interface BodySizes { major: number; minor: number; strip: number; sign: number; sub: number }

/** Text sizes in chart units: scale with the SVG (and the Charts font of Preferences). ``fitted`` still shrinks crowded boxes.
 *  ``px`` is kept for callers; size is no longer inverse to screen width, so planets, titles and the frame stay in proportion. */
export function bodySizes(_px: number, factor = 1): BodySizes {
  return { major: 20 * factor, minor: 14 * factor, strip: 12 * factor, sign: 12 * factor, sub: 14 * factor };
}

// Mixed charts draw every body at one small size in tight boxes: the spacing they were laid out with
const MIXED: BodySizes = { major: 17, minor: 11, strip: 10, sign: 10, sub: 13 };

/** A label's width in ems, near enough to space by: a body's name is two or three letters, or its Unicode in a chart language. */
// a degree's space, °, ' and brackets are narrow; a graha's R is drawn "(R)" (names.ts retroMark)
const ems = (t: string) => [...t.replace(/^([A-Z][a-z])R$/, "$1(R)")].reduce((w, c) => w + (/[MWmw]/.test(c) ? 0.88 : /[A-Z0-9]/.test(c) ? 0.66 : /[ °'()]/.test(c) ? 0.32 : 0.56), 0);
export const stripPitch = (z: BodySizes) => z.strip * 2.1;
export const stripColumns = (z: BodySizes, W: number) => Math.max(1, Math.floor((W - 6) / stripPitch(z)));
export const stripRowHeight = (z: BodySizes) => z.strip * 1.2;

/** A graha's degrees in its sign as the chart shows them: 12°05'. A bhava chart counts from its box's sign (-2 or 32): shown in the graha's own. */
export const degText = (d: number) => { d = ((d % 30) + 30) % 30; return `${Math.floor(d)}°${String(Math.floor((d % 1) * 60)).padStart(2, "0")}'`; };
/** The degrees of label ``t`` (a retrograde "R" aside), if the chart shows them. */
export const degOf = (t: string, deg?: Record<string, number>) => deg?.[t.replace(/R$/, "")];
/** A label's width: a graha with degrees has bold letters between the minor and major sizes, and its degrees at the major (styles.css .graha-deg). */
const labelWidth = (t: string, z: BodySizes, deg?: Record<string, number>, moved?: Record<string, string>) => {
  const d = degOf(t, deg), m = moved?.[t.replace(/R$/, "")];
  return d === undefined ? ems(t) * z[bodyKind(t)] : ems(t) * ((z.minor + z.major) / 2) * 1.08 + ems(` ${degText(d)}${m ? ` ${m}` : ""}`) * z.major;
};

/** Left-to-right placement of a box's bodies, wrapping at its edge, below the line with the sign's name.
 *  ``deg``: the grahas' degrees, and the box is laid out by ``columns`` instead. */
export function flow(labels: string[], W: number, z: BodySizes = MIXED, deg?: Record<string, number>, beside = false, low?: number, up = false, name?: string): Placed[] {
  if (deg) return columns(labels, W, z, deg, beside, low, up);
  const size = (t: string) => z[bodyKind(t)];
  // ``name``: the sign's name at the top right; the first row goes up beside it, stopping short of it (Starlight)
  const besideName = name !== undefined && z.sign > 0;
  let x = 8, y = besideName ? z.major * 0.8 + 3 : z.sign + 3 + z.major, edge = besideName ? W - 4 - ems(name) * z.sign - z.sign * 0.6 : W - 2;
  const row: Placed[] = [];
  const order = [...labels.filter((t) => bodyKind(t) === "major"), ...labels.filter((t) => bodyKind(t) !== "major")];
  for (const t of order) {
    const wide = ems(t) * size(t);
    if (x > 8 && x + wide > edge) { x = 8; y += size(t) * 1.12; edge = W - 2; }
    row.push({ t, x, y });
    x += wide + size(t) * 0.18;
  }
  return row;
}

/** A body placed in its box; ``end``: ``x`` is where its text ends (the right-hand column). */
export interface Placed { t: string; x: number; y: number; end?: boolean }

/** The chart with degrees: grahas down the left, lowest degree at the top; every other body (lagnas, upagrahas, arudhas)
 *  ``beside`` them down the right, under the sign's name (the South chart's square boxes), else in rows under them (North and East's narrow ones).
 *  ``low``: the box's height, and the other bodies go along its bottom instead, right-aligned with a gap between them, wrapping upward (Starlight). */
function columns(labels: string[], W: number, z: BodySizes, deg: Record<string, number>, beside: boolean, low?: number, up = false): Placed[] {
  // ``up``: the lowest degree at the bottom, for boxes the zodiac climbs through (the South chart's left column)
  const grahas = labels.filter((t) => degOf(t, deg) !== undefined).sort((a, b) => (up ? -1 : 1) * (degOf(a, deg)! - degOf(b, deg)!));
  // the first row a little more than an em under the sign's name
  const out: Placed[] = grahas.map((t, i) => ({ t, x: 8, y: z.sign + 3 + z.major * (1.05 + i * 1.12) }));
  const rest = labels.filter((t) => degOf(t, deg) === undefined);
  if (!beside) return [...out, ...flow(rest, W, z).map((r) => ({ ...r, y: r.y + grahas.length * z.major * 1.12 }))];
  if (low !== undefined) {
    let x = W - 4, y = low - 6;
    const row: Placed[] = [];
    for (const t of [...rest].reverse()) {     // from the right, so they still read in order
      const w = labelWidth(t, z), gap = z[bodyKind(t)] * 0.7;
      if (x < W - 4 && x - w < 8) { x = W - 4; y -= z.minor * 1.3; }
      row.unshift({ t, x, y, end: true });
      x -= w + gap;
    }
    // the grahas centred between the sign's name and the points along the bottom (or the box's bottom), if there is room to spare
    const floor = row.length ? Math.min(...row.map((r) => r.y - z[bodyKind(r.t)] * 0.8)) - 4 : low - 4;
    const last = out.at(-1), spare = last ? (floor - (last.y + z.major * 0.25) - z.major * 0.15) / 2 : 0;
    return [...out.map((r) => ({ ...r, y: r.y + Math.max(0, spare) })), ...row];
  }
  let y = z.sign + 3;
  for (const t of rest) {
    y += z[bodyKind(t)] * 1.12;
    out.push({ t, x: W - 4, y, end: true });
  }
  return out;
}

/** A box to fit: its bodies, its width, its height below where ``flow`` starts; ``stripAlong``: its strip runs along the bottom, not in the flow;
 *  ``low``: the right-hand column stands on the bottom (``flow``'s ``low``, the box's height); ``plain``: laid out by ``deg`` but the degrees not drawn. */
export interface Box { labels: string[]; w: number; h: number; stripAlong?: boolean; deg?: Record<string, number>; beside?: boolean; low?: boolean; moved?: Record<string, string>; plain?: boolean; name?: string }

/** Where placed body ``a`` must end: the box's edge, or where the right-hand bodies level with it begin. */
function roomRight(b: Box, z: BodySizes, rows: Placed[], a: Placed) {
  const size = (r: Placed) => z[bodyKind(r.t)];
  const level = (o: Placed) => !b.low || (o.y - size(o) * 0.8 < a.y + size(a) * 0.25 && a.y - size(a) * 0.8 < o.y + size(o) * 0.25);     // a bottom column only meets the rows beside it
  return Math.min(b.w, ...rows.filter((o) => o.end && level(o)).map((o) => o.x - labelWidth(o.t, z) - 4)) + 2;
}

// the reference box for ``fittedEach``'s one size counts its rows as this much narrower, the size the default was set at
const ROW_LEAST = 0.8;
const ownRow = (b: Box, r: Placed) => !r.end && degOf(r.t, b.deg) !== undefined;

/** ``rows``: the grahas' rows count as ``ROW_LEAST`` of their width (``fittedEach``'s reference box only). */
function fits(b: Box, z: BodySizes, rows = false) {
  const strips = b.stripAlong ? b.labels.filter((t) => bodyKind(t) === "strip").length : 0;
  const room = b.h - (strips ? 6 + Math.ceil(strips / stripColumns(z, b.w)) * stripRowHeight(z) : 0);
  const placed = flow(b.stripAlong ? b.labels.filter((t) => bodyKind(t) !== "strip") : b.labels, b.w, z, b.deg, b.beside, b.low ? b.h : undefined, false, b.name);
  const size = (r: Placed) => z[bodyKind(r.t)];
  return placed.every((r) => r.y + size(r) * 0.25 <= room && (r.end ? !b.low || r.y - size(r) * 0.8 >= z.sign + 5
    : r.x + labelWidth(r.t, z, b.plain ? undefined : b.deg, b.moved) * (rows && ownRow(b, r) ? ROW_LEAST : 1) <= roomRight(b, z, placed, r)));
}

const scaled = (z: BodySizes, s: number): BodySizes => ({ ...z, major: z.major * s, minor: z.minor * s, strip: z.strip * s, sign: z.sign * s });
// a chart with degrees has two columns a box, so it may run smaller
const leastOf = (z: BodySizes, boxes: Box[], factor: number) => Math.min(1, (MIXED.major * factor) / z.major) * (boxes.some((b) => b.deg) ? 0.55 : 1);
function largest(z: BodySizes, boxes: Box[], least: number, most = 1, rows = false) {
  for (let s = most; s > least; s -= 0.04) if (boxes.every((b) => fits(b, scaled(z, s), rows))) return scaled(z, s);
  return scaled(z, least);
}

/** ``z``, shrunk only as far as this chart's boxes need, so a crowded chart reads smaller instead of overflowing; never under the size its layout was first drawn at. */
export const fitted = (z: BodySizes, boxes: Box[], factor = 1) => largest(z, boxes, leastOf(z, boxes, factor));

/** Each box's own sizes: a box shrinks only for its own bodies, so a crowded one leaves the rest large; within a box every graha is one size. */
export const fittedEach = (z: BodySizes, boxes: Box[], factor = 1, most = 1) => {
  const least = leastOf(z, boxes, factor);
  // one size for every box with degrees: a step under what three wide grahas and a row of points fit at, so a box of one or two isn't larger; a busier box still shrinks
  const deg = { Ma: 28.99, Me: 28.99, Ju: 28.99 }, b0 = boxes.find((b) => b.deg);
  const cap = b0 ? largest(z, [{ ...b0, labels: ["Ma", "Me", "Ju", "HL"], deg, moved: undefined }], least, most, true).major / z.major * 0.9 : most;
  return boxes.map((b) => largest(z, [b], least, b.deg ? Math.min(most, cap) : most));
};

/** A bhava chart's box (its sign, 0-11) as the bhava it holds (1-12): counted on from the box of the 1st bhava (the reference's), back
 *  from it when the bhavas run backward (counted from Rahu or Ketu with "bhavas of the nodes reversed"). */
export const bhavaOfBox = (box: number, first: number, backward = false) => ((((backward ? first - box : box - first) % 12) + 12) % 12) + 1;
