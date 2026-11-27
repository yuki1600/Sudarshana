// Where each slot of a wheel goes, (px of a 1938-wide drawing); slot 0 is the wheel's base star.
export type Point = [number, number];
export type Segment = [number, number, number, number];

/** body: the grahas' font size (28 when unset), or with `fit` their largest; fit: the widest a row of them may run, the grahas then stacked in rows to fill the room under the star. */
export interface Wheel { box: string; slots: Point[]; lines: Segment[]; circle?: [number, number, number]; labels?: [string, number, number][]; body?: number; fit?: number }

const seg = (...xs: number[]): Segment[] => { const out: Segment[] = []; for (let i = 0; i + 3 < xs.length; i += 2) out.push([xs[i], xs[i + 1], xs[i + 2], xs[i + 3]]); return out; };

export const SURYA: Wheel = {
  box: "30 205 960 780",
  slots: [[500, 930], [306, 930], [189, 930], [73, 847], [73, 706], [73, 612], [73, 518], [73, 367], [73, 231], [176, 231], [241, 231], [306, 231], [371, 231], [435, 231],
    [500, 231], [565, 231], [630, 231], [695, 231], [759, 231], [824, 231], [929, 231], [929, 367], [929, 518], [929, 612], [929, 706], [929, 847], [811, 930], [695, 930]],
  lines: [[307, 268, 307, 895], [501, 268, 501, 895], [695, 268, 695, 895], [113, 519, 890, 519], [113, 613, 890, 613], [113, 707, 890, 707],
    [116, 278, 307, 519], [178, 268, 307, 435], [242, 268, 307, 352], [372, 268, 307, 352], [436, 268, 501, 352], [566, 268, 501, 352], [631, 268, 695, 352], [760, 268, 695, 352],
    [825, 268, 695, 435], [890, 268, 695, 519], [113, 352, 242, 519], [890, 352, 761, 519], [113, 832, 230, 707], [190, 895, 307, 771], [695, 771, 812, 895], [773, 707, 890, 832]],
};

export const CHANDRA: Wheel = {
  box: "30 205 830 750",
  slots: [[435, 231], [350, 231], [350, 362], [394, 461], [301, 513], [218, 503], [68, 503], [68, 581], [68, 659], [218, 659], [301, 607], [395, 670], [322, 800], [350, 910],
    [434, 910], [517, 910], [544, 800], [473, 670], [568, 607], [655, 659], [801, 659], [801, 581], [801, 503], [655, 503], [567, 513], [473, 461], [517, 362], [518, 231]],
  circle: [435, 582, 194],
  lines: [[435, 268, 435, 895], [101, 582, 769, 582], [298, 453, 572, 710], [572, 453, 298, 710],
    ...seg(351, 268, 351, 347, 518, 347, 518, 268), ...seg(351, 895, 351, 817, 518, 817, 518, 895), ...seg(101, 503, 185, 503, 185, 660, 101, 660), ...seg(769, 503, 685, 503, 685, 660, 769, 660)],
};

export const KALA: Wheel = {
  box: "15 180 840 810",
  slots: [[434, 231], [434, 315], [434, 398], [467, 492], [556, 450], [622, 388], [689, 325], [789, 597], [701, 597], [612, 597], [512, 597], [556, 680], [622, 743], [689, 805],
    [434, 899], [434, 816], [434, 732], [401, 659], [312, 680], [245, 743], [179, 805], [79, 597], [168, 597], [256, 597], [355, 534], [312, 450], [245, 388], [179, 325]],
  circle: [435, 582, 133],
  lines: [[435, 205, 435, 449], [435, 715, 435, 958], [35, 582, 301, 582], [568, 582, 835, 582], [146, 310, 340, 492], [724, 310, 530, 492], [146, 853, 340, 671], [723, 853, 530, 671]],
  labels: [["EAST: Indra (power)", 434, 198], ["SE: Agni (prosperity)", 723, 281], ["S: Yama (death)", 764, 573], ["SW: Nirriti (curses of gods)", 723, 890],
    ["W: Varuna (suffering/foreign things)", 434, 974], ["NW: Vayu (wandering)", 145, 890], ["N: Kubera (money)", 116, 573], ["NE: Isana (blessings of gods)", 145, 281]],
};

export const SHOOLA: Wheel = {
  box: "150 205 590 780",
  slots: [[433, 910], [367, 837], [368, 774], [367, 711], [401, 638], [401, 576], [400, 513], [278, 283], [234, 231], [201, 283], [201, 377], [201, 440], [233, 503], [401, 283],
    [434, 231], [478, 283], [478, 356], [401, 388], [479, 419], [600, 283], [634, 231], [680, 283], [679, 377], [679, 440], [633, 503], [478, 711], [478, 774], [479, 837]],
  lines: [[435, 268, 435, 895], ...seg(235, 268, 235, 477, 635, 477, 635, 268)],
  body: 24, fit: 66,   // the stars are 63 apart down a prong and 77 across
};

/** Kota Chakra, in cells of a 9 x 9 square. */
export const KOTA_X = [0, 1, 2, 4, 4, 4, 4, 8, 7, 6, 5, 6, 7, 8, 8, 7, 6, 4, 4, 4, 4, 0, 1, 2, 3, 2, 1, 0];
export const KOTA_Y = [0, 1, 2, 3, 2, 1, 0, 0, 1, 2, 4, 4, 4, 4, 8, 7, 6, 5, 6, 7, 8, 8, 7, 6, 4, 4, 4, 4];

/** Sarvatobhadra's 9 x 9 cells; the border stars carry the bodies. */
export const SBC: (string | [string, string])[][] = [
  ["ii", "*Dhan", "*Sata", "*PBha", "*UBha", "*Reva", "*Aswi", "*Bhar", "a"],
  ["*Srav", "rii", "g", "s", "d", "ch", "l", "u", "*Krit"],
  ["*Abhi", "kh", "ai", "Aq", "Pi", "Ar", "lu", "a", "*Rohi"],
  ["*USha", "j", "Cp", "ah", ["Rikta", "Fri"], "o", "Ta", "v", "*Mrig"],
  ["*PSha", "bh", "Sg", ["Jaya", "Thu"], ["Poorna", "Sat"], ["Nanda", "Sun Tue"], "Ge", "k", "*Ardr"],
  ["*Mool", "y", "Sc", "am", ["Bhadra", "Mon Wed"], "au", "Cn", "h", "*Puna"],
  ["*Jye", "n", "e", "Li", "Vi", "Le", "luu", "d", "*Push"],
  ["*Anu", "ri", "t", "r", "p", "t~", "m", "uu", "*Asre"],
  ["i", "*Visa", "*Swat", "*Chit", "*Hast", "*UPha", "*PPha", "*Magh", "aa"],
];

export type Row = [text: string, transit: boolean];
/** Natal names then transit ones, `per` to a row. */
export function rowsOf(names: string[], over: string[] | undefined, per: number): Row[] {
  const out: Row[] = [];
  [names, over ?? []].forEach((list, t) => { for (let i = 0; i < list.length; i += per) out.push([list.slice(i, i + per).join(" "), t === 1]); });
  return out;
}
/** Graha names stacked one or more to a row, whichever lets them run largest (up to `max`): `limit(a, b)` is the biggest size a block a·size wide and b·size tall may take. */
export function pack(names: string[], over: string[] | undefined, limit: (a: number, b: number) => number, max: number) {
  let best = { rows: [] as Row[], size: 0 };
  for (let per = Math.max(names.length, over?.length ?? 0); per >= 1; per--) {
    const rows = rowsOf(names, over, per);
    const size = Math.min(max, limit(Math.max(...rows.map(([t]) => t.length)) * 0.55, rows.length));   // a character is about 0.55em
    if (size > best.size) best = { rows, size };
  }
  return best;
}

/** A star's three vedha lines, front, left and right, each the boxes it runs through. A graha looks into the chakra: on the top (East) row
 *  it faces down, the front its column, its right hand the diagonal back towards the stars behind it (Krittika's: Bharani), its left the one
 *  on towards those ahead (Krittika's: Vishakha); the other sides as turned. So a retrograde graha's main vedha (the right) falls the way it
 *  moves, as Ketu's from Magha onto Ashlesha. null for a box that is not a star (the corners and the inner boxes). */
export function vedhaLines(r: number, c: number): Record<"front" | "left" | "right", Set<string>> | null {
  const side = c > 0 && c < 8 ? (r === 0 ? 0 : r === 8 ? 2 : -1) : r > 0 && r < 8 ? (c === 8 ? 1 : c === 0 ? 3 : -1) : -1;
  if (side < 0) return null;
  let dirs: [number, number][] = [[1, 0], [1, 1], [1, -1]];     // front, left, right, from the top row
  for (let k = 0; k < side; k++) dirs = dirs.map(([dr, dc]) => [dc, -dr]);     // a quarter turn clockwise per side
  const walk = ([dr, dc]: [number, number]) => { const out = new Set<string>(); for (let i = r + dr, j = c + dc; i >= 0 && i < 9 && j >= 0 && j < 9; i += dr, j += dc) out.add(`${i}-${j}`); return out; };
  return { front: walk(dirs[0]), left: walk(dirs[1]), right: walk(dirs[2]) };
}
