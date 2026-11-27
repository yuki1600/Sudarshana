/** The Sudarshana Chakra's geometry, in world units round the hub (y up): drawn by the intro and the sign-in page. */

export const R = 1.6;                        // the chakra's rim radius
export const TIP = R + 0.36;                 // the blades' tips
export const TAU = Math.PI * 2;

export type Pt = [number, number];
/** One stroke of the design, in world units round the hub: its outline, whether it closes, how strongly it is
 *  filled (0 for none), its line width, and how bright its line is. */
export type Shape = { pts: Pt[]; closed: boolean; fill: number; line: number; ink: number };

const polar = (r: number, a: number): Pt => [Math.cos(a) * r, Math.sin(a) * r];
const quad = (p0: Pt, c: Pt, p1: Pt, n = 16): Pt[] =>
  Array.from({ length: n + 1 }, (_, i) => { const t = i / n, u = 1 - t; return [u * u * p0[0] + 2 * u * t * c[0] + t * t * p1[0], u * u * p0[1] + 2 * u * t * c[1] + t * t * p1[1]] as Pt; });
const circle = (r: number, n = Math.max(48, Math.round(r * 260))): Pt[] => Array.from({ length: n }, (_, i) => polar(r, (i / n) * TAU));
const around = (pts: Pt[], c: Pt): Pt[] => pts.map(([x, y]) => [x + c[0], y + c[1]]);
const petal = (c: number, ri: number, ro: number, half: number, bow: number): Pt[] =>
  [...quad(polar(ri, c - half), polar(ri + (ro - ri) * bow, c - half * 1.25), polar(ro, c)), ...quad(polar(ro, c), polar(ri + (ro - ri) * bow, c + half * 1.25), polar(ri, c + half)).slice(1)];

/** The Sudarshana Chakra as line art, from the rim inward: the swept blades round a Navamsa yantra. */
export function design(): Shape[] {
  const s: Shape[] = [];
  const add = (pts: Pt[], o: Partial<Shape> = {}) => s.push({ pts, closed: true, fill: 0, line: 0.006, ink: 1, ...o });

  // 36 flame-blades swept forward round the rim: a convex leading edge, a hollowed trailing edge, a vein down each
  const blades = 36, w = TAU / blades;
  for (let i = 0; i < blades; i++) {
    const a = i * w, tip = polar(TIP, a + w * 1.55);
    add([...quad(polar(R, a + w), polar(R + 0.2, a + w * 1.5), tip), ...quad(tip, polar(R + 0.12, a + w * 0.95), polar(R, a)).slice(1)], { fill: 0.2, line: 0.007 });
    add(quad(polar(R + 0.02, a + w * 0.55), polar(R + 0.16, a + w * 1.05), polar(TIP - 0.07, a + w * 1.45), 10), { closed: false, line: 0.0035, ink: 0.7 });
  }
  // the rim, a hairline, and 108 navamsa padas: a longer tick at each rasi, a bead at each nakshatra
  add(circle(R), { line: 0.016 });
  add(circle(R - 0.03), { line: 0.004, ink: 0.7 });
  for (let i = 0; i < 108; i++) {
    const a = (i / 108) * TAU, rasi = i % 9 === 0;
    add([polar(R - 0.04, a), polar(rasi ? R - 0.125 : R - 0.085, a)], { closed: false, line: rasi ? 0.006 : 0.0025, ink: rasi ? 1 : 0.7 });
    if (i % 4 === 0 && !rasi) add(around(circle(0.011, 10), polar(R - 0.105, a)), { fill: 0.9, line: 0.002 });
  }
  add(circle(R - 0.13), { line: 0.008 });
  // a twisted cord: two waves crossing, a bead in each eye
  for (const sgn of [1, -1]) add(Array.from({ length: 576 }, (_, i) => polar(R - 0.172 + sgn * 0.026 * Math.sin(36 * (i / 576) * TAU), (i / 576) * TAU)), { line: 0.004, ink: 0.85 });
  for (let i = 0; i < 72; i++) add(around(circle(0.008, 8), polar(R - 0.172, ((i + 0.5) / 72) * TAU)), { fill: 1, line: 0.002 });
  add(circle(R - 0.215), { line: 0.009 });
  add(circle(R - 0.24), { line: 0.004, ink: 0.7 });

  // a hexagram, its lines doubled, with a small lotus wheel in each of its six pockets
  const Rh = R - 0.25;
  for (const k of [0, 1]) for (const sc of [1, 0.95]) add([0, 1, 2].map((j) => polar(Rh * sc, TAU / 4 + k * TAU / 6 + j * TAU / 3)), sc === 1 ? { fill: 0.07, line: 0.01 } : { line: 0.0035, ink: 0.7 });
  for (let k = 0; k < 6; k++) {
    const c = polar(1.12, TAU / 4 + TAU / 12 + k * TAU / 6);
    add(around(circle(0.15), c), { line: 0.006 });
    add(around(circle(0.13), c), { line: 0.0025, ink: 0.6 });
    for (let j = 0; j < 8; j++) add(around(petal((j / 8) * TAU, 0.035, 0.12, 0.17, 0.7), c), { fill: 0.25, line: 0.004 });
    add(around(circle(0.03), c), { fill: 0.8, line: 0.003 });
  }

  // 12 rasi spokes with an arch and a bead between each pair
  add(circle(0.65), { line: 0.012 });
  add(circle(0.615), { line: 0.004, ink: 0.7 });
  const prof: [number, number][] = [[0, 0.012], [0.3, 0.032], [0.5, 0.012], [0.75, 0.028], [1, 0.004]];
  for (let i = 0; i < 12; i++) {
    const a = (i / 12) * TAU, at = (t: number, off: number): Pt => { const r = 0.34 + t * 0.26; return [Math.cos(a) * r - Math.sin(a) * off, Math.sin(a) * r + Math.cos(a) * off]; };
    add([...prof.map(([t, h]) => at(t, h)), ...[...prof].reverse().map(([t, h]) => at(t, -h))], { fill: 0.3, line: 0.005 });
    add(quad(polar(0.6, a), polar(0.5, a + TAU / 24), polar(0.6, a + TAU / 12), 12), { closed: false, line: 0.004, ink: 0.8 });
    add(around(circle(0.013, 10), polar(0.44, a + TAU / 24)), { fill: 0.9, line: 0.002 });
  }
  add(circle(0.34), { line: 0.01 });
  add(circle(0.31), { line: 0.0035, ink: 0.7 });

  // an eight-petal lotus, eight behind and eight in front, round nine seeds for the grahas
  for (let i = 0; i < 8; i++) add(petal((i / 8) * TAU + TAU / 16, 0.1, 0.3, 0.3, 0.75), { fill: 0.14, line: 0.004, ink: 0.7 });
  for (let i = 0; i < 8; i++) add(petal((i / 8) * TAU, 0.1, 0.27, 0.27, 0.7), { fill: 0.26, line: 0.006 });
  add(circle(0.1), { line: 0.01 });
  add(around(circle(0.022, 12), [0, 0]), { fill: 1, line: 0.002 });
  for (let i = 0; i < 8; i++) add(around(circle(0.014, 10), polar(0.062, (i / 8) * TAU)), { fill: 0.9, line: 0.002 });
  return s;
}
