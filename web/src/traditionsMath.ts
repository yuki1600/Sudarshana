/** The Traditions tab's geometry and tables (Traditions.tsx), kept pure so they can be tested. */

/** A Western wheel's angle (degrees, counter-clockwise from the right) of an ecliptic longitude: the ascendant on the left. */
export const wheelAngle = (lon: number, asc: number) => (((180 + lon - asc) % 360) + 360) % 360;

/** A point on a circle of radius ``r`` round (cx, cy) at ``angle`` degrees counter-clockwise from the right (SVG's y runs down). */
export function polar(cx: number, cy: number, r: number, angle: number): [number, number] {
  const a = (angle * Math.PI) / 180;
  return [cx + r * Math.cos(a), cy - r * Math.sin(a)];
}

/** Labels at these angles (degrees) moved apart to at least ``gap`` degrees, in their own order round the circle, each as
 *  near its own angle as it can be: the bodies of a wheel that would print over each other. */
export function spread(angles: number[], gap: number): number[] {
  const order = angles.map((a, i) => [((a % 360) + 360) % 360, i] as const).sort((x, y) => x[0] - y[0]);
  const out = order.map(([a]) => a);
  for (let pass = 0; pass < 12; pass++) {
    let moved = false;
    for (let k = 0; k < out.length; k++) {
      const j = (k + 1) % out.length;
      if (out.length < 2) break;
      const d = (((out[j] - out[k]) % 360) + 360) % 360;
      if (d < gap) {
        const push = (gap - d) / 2;
        out[k] -= push;
        out[j] += push;
        moved = true;
      }
    }
    if (!moved) break;
  }
  const back = new Array<number>(angles.length);
  order.forEach(([, i], k) => { back[i] = ((out[k] % 360) + 360) % 360; });
  return back;
}

/** The Lo Shu square's cells, South at the top as Chinese charts draw it: [row][column] -> its palace number. */
export const LO_SHU = [[4, 9, 2], [3, 5, 7], [8, 1, 6]];
/** Each cell's direction, as LO_SHU. */
export const LO_SHU_DIRECTIONS = [["SE", "S", "SW"], ["E", "", "W"], ["NE", "N", "NW"]];
/** The order the stars fly through the palaces from the centre: centre, NW, W, NE, S, N, SW, E, SE. */
const FLIGHT = [5, 6, 7, 8, 9, 1, 2, 3, 4];

/** The magic square with ``centre`` in the middle, flown forward (the year's or month's stars of Nine Star Ki and Flying
 *  Stars): [row][column], South at the top. */
export function flyStars(centre: number): number[][] {
  const star: Record<number, number> = {};
  FLIGHT.forEach((palace, k) => { star[palace] = ((centre - 1 + k) % 9) + 1; });
  return LO_SHU.map((row) => row.map((palace) => star[palace]));
}

/** The twelve branches round a Zi Wei Dou Shu chart's 4 x 4 square: branch index (Zi 0 .. Hai 11) -> [row, column]. */
export const ZIWEI_RING: Record<number, [number, number]> = {
  5: [0, 0], 6: [0, 1], 7: [0, 2], 8: [0, 3], 9: [1, 3], 10: [2, 3], 11: [3, 3], 0: [3, 2], 1: [3, 1], 2: [3, 0], 3: [2, 0], 4: [1, 0]
};

export const STEMS = ["Jia", "Yi", "Bing", "Ding", "Wu", "Ji", "Geng", "Xin", "Ren", "Gui"];
export const STEM_HANZI = "甲乙丙丁戊己庚辛壬癸";
export const BRANCHES = ["Zi", "Chou", "Yin", "Mao", "Chen", "Si", "Wu", "Wei", "Shen", "You", "Xu", "Hai"];
export const BRANCH_HANZI = "子丑寅卯辰巳午未申酉戌亥";
export const BRANCH_ANIMALS = ["Rat", "Ox", "Tiger", "Rabbit", "Dragon", "Snake", "Horse", "Goat", "Monkey", "Rooster", "Dog", "Pig"];
/** Korean (Saju) readings of the stems and branches, as XALEN names them, to their Hanja and Hangul. */
export const SAJU_STEMS = ["Gap", "Eul", "Byeong", "Jeong", "Mu", "Gi", "Gyeong", "Sin", "Im", "Gye"];
export const SAJU_STEM_HANGUL = ["갑", "을", "병", "정", "무", "기", "경", "신", "임", "계"];
export const SAJU_BRANCHES = ["Ja", "Chuk", "In", "Myo", "Jin", "Sa", "O", "Mi", "Sin", "Yu", "Sul", "Hae"];
export const SAJU_BRANCH_HANGUL = ["자", "축", "인", "묘", "진", "사", "오", "미", "신", "유", "술", "해"];

/** A stem or branch by its name (Chinese pinyin, or the Korean reading with ``korean``): its index, or -1. XALEN writes the
 *  Korean branch Sin "Sin_" to tell it from the stem. */
export function stemIndex(name: string, korean = false): number {
  return (korean ? SAJU_STEMS : STEMS).indexOf(name.replace(/_$/, ""));
}
export function branchIndex(name: string, korean = false): number {
  return (korean ? SAJU_BRANCHES : BRANCHES).indexOf(name.replace(/_$/, ""));
}

/** "TianLiang" -> "Tian Liang", "WuXing" -> "Wu Xing": XALEN's pinyin names, spaced. */
export const spaced = (s: string) => s.replace(/_$/, "").replace(/([a-z])([A-Z])/g, "$1 $2").replace(/(\D)(\d)/g, "$1 $2");

/** The 20 day signs of the 260-day count, Aztec (Nahuatl) and Maya (Yucatec) names in the same order. */
export const AZTEC_SIGNS = ["Cipactli", "Ehecatl", "Calli", "Cuetzpalin", "Coatl", "Miquiztli", "Mazatl", "Tochtli", "Atl", "Itzcuintli",
  "Ozomatli", "Malinalli", "Acatl", "Ocelotl", "Cuauhtli", "Cozcacuauhtli", "Ollin", "Tecpatl", "Quiahuitl", "Xochitl"];
export const MAYA_SIGNS = ["Imix", "Ik", "Akbal", "Kan", "Chikchan", "Kimi", "Manik", "Lamat", "Muluk", "Ok", "Chuwen", "Eb", "Ben", "Ix",
  "Men", "Kib", "Kaban", "Etznab", "Kawak", "Ajaw"];
/** A Maya day sign's index whatever its spelling (Ik', Chicchan, Ahau ..): -1 if none. */
export function mayaIndex(name: string): number {
  // a skeleton both spellings share: ch kept apart, c as k, j and h dropped, w as u, letters not doubled
  const plain = (s: string) => s.toLowerCase().replace(/['’]/g, "").replace(/ch/g, "#").replace(/c/g, "k").replace(/[jh]/g, "")
    .replace(/w/g, "u").replace(/(.)\1+/g, "$1");
  const n = plain(name);
  return MAYA_SIGNS.findIndex((s) => plain(s) === n);
}
