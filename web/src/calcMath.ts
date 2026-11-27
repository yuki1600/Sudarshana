/** The arithmetic the Calculations tab works through on the open chart, step by step. The engine's own values are the check. */

export const PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"] as const;
export const SEVEN = PLANETS.slice(0, 7);
export const NAKSHATRAS = ["Aśvinī", "Bharaṇī", "Kṛttikā", "Rohiṇī", "Mṛgaśiras", "Ārdrā", "Punarvasu", "Puṣya", "Āśleṣā", "Maghā",
  "Pūrva Phalgunī", "Uttara Phalgunī", "Hasta", "Citrā", "Svātī", "Viśākhā", "Anurādhā", "Jyeṣṭhā", "Mūla", "Pūrvāṣāḍhā",
  "Uttarāṣāḍhā", "Śravaṇa", "Dhaniṣṭhā", "Śatabhiṣā", "Pūrva Bhādrapadā", "Uttara Bhādrapadā", "Revatī"];
export const SIGN_LORD = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"];
/** A sign's lords wherever the app names a house's lord (as the server's owns_sign): its natural lord, and Rahu for Aquarius, Ketu for Scorpio. */
export const lordsOf = (sign: number) => [SIGN_LORD[sign], ...(sign === 10 ? ["Rahu"] : sign === 7 ? ["Ketu"] : [])];
export const EXALT: Record<string, number> = { Sun: 0, Moon: 1, Mars: 9, Mercury: 5, Jupiter: 3, Venus: 11, Saturn: 6 };
export const OWN: Record<string, number[]> = { Sun: [4], Moon: [3], Mars: [0, 7], Mercury: [2, 5], Jupiter: [8, 11], Venus: [1, 6], Saturn: [9, 10] };
/** core_logic/ayurdaya.py DEEP_EXALTATION and the years of BPHS 43. */
export const DEEP_EXALT: Record<string, number> = { Sun: 10, Moon: 33, Mars: 298, Mercury: 165, Jupiter: 95, Venus: 357, Saturn: 200 };
export const PINDA_YEARS: Record<string, number> = { Sun: 19, Moon: 25, Mars: 15, Mercury: 12, Jupiter: 15, Venus: 21, Saturn: 20 };
export const VIMS: [string, number][] = [["Ketu", 7], ["Venus", 20], ["Sun", 6], ["Moon", 10], ["Mars", 7], ["Rahu", 18], ["Jupiter", 16], ["Saturn", 19], ["Mercury", 17]];
export const WEEKDAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
export const MODALITY = ["movable", "fixed", "dual"] as const;
const TITHIS = ["Pratipad", "Dvitīyā", "Tṛtīyā", "Caturthī", "Pañcamī", "Ṣaṣṭhī", "Saptamī", "Aṣṭamī", "Navamī", "Daśamī", "Ekādaśī", "Dvādaśī", "Trayodaśī", "Caturdaśī"];
const YOGAS = ["Viṣkambha", "Prīti", "Āyuṣmān", "Saubhāgya", "Śobhana", "Atigaṇḍa", "Sukarmā", "Dhṛti", "Śūla", "Gaṇḍa", "Vṛddhi", "Dhruva", "Vyāghāta",
  "Harṣaṇa", "Vajra", "Siddhi", "Vyatīpāta", "Varīyān", "Parigha", "Śiva", "Siddha", "Sādhya", "Śubha", "Śukla", "Brahma", "Indra", "Vaidhṛti"];
const KARANAS = ["Bava", "Bālava", "Kaulava", "Taitila", "Gara", "Vaṇija", "Viṣṭi"];
/** core_logic/aspects_friendships.py NAISARGIKA_MATRIX, Sun..Saturn: +1 friend, 0 neutral, −1 enemy. */
const NATURAL = [[0, 1, 1, 0, 1, -1, -1], [1, 0, 0, 1, 0, 0, 0], [1, 1, 0, -1, 1, 0, 0], [1, -1, 0, 0, 0, 1, 0],
  [1, 1, 1, -1, 0, -1, 0], [-1, -1, 0, 1, 0, 0, 1], [-1, -1, -1, 1, 0, 1, 0]];
/** core_logic/transits.py GOCHARA_AND_VEDHA: good house from the Moon -> its vedha house. */
const SLOW = { 3: 12, 6: 9, 11: 5 };
export const GOCARA: Record<string, Record<number, number>> = {
  Sun: { 3: 9, 6: 12, 10: 4, 11: 5 }, Moon: { 1: 5, 3: 9, 6: 12, 7: 2, 10: 4, 11: 8 }, Mars: SLOW,
  Mercury: { 2: 5, 4: 3, 6: 9, 8: 1, 10: 8, 11: 12 }, Jupiter: { 2: 12, 5: 4, 7: 3, 9: 10, 11: 8 },
  Venus: { 1: 8, 2: 7, 3: 1, 4: 10, 5: 9, 8: 5, 9: 11, 11: 6, 12: 3 }, Saturn: SLOW, Rahu: SLOW, Ketu: SLOW,
};
const NO_VEDHA = new Set(["Sun|Saturn", "Saturn|Sun", "Moon|Mercury", "Mercury|Moon"]);

const STAR = 40 / 3;
export const mod = (x: number, m = 360) => ((x % m) + m) % m;
/** Sign `to` counted from sign `from`, 1 to 12. */
export const house = (from: number, to: number) => mod(to - from, 12) + 1;
export const signOf = (lon: number) => Math.floor(mod(lon) / 30);
export const modality = (sign: number) => MODALITY[sign % 3];

export function nakshatraOf(lon: number) {
  const x = mod(lon) / STAR;
  const index = Math.floor(x);
  const done = x - index;
  return { index, name: NAKSHATRAS[index], pada: Math.floor(done * 4) + 1, done, start: index * STAR, end: (index + 1) * STAR, lord: VIMS[index % 9][0], years: VIMS[index % 9][1] };
}

export const segment = (lon: number, n: number) => Math.floor((mod(lon) % 30) / (30 / n));
export const navamsaSign = (lon: number) => mod(signOf(lon) * 9 + segment(lon, 9), 12);
export const d12Sign = (lon: number) => mod(signOf(lon) + segment(lon, 12), 12);

export function vimsottariBalance(moon: number) {
  const n = nakshatraOf(moon);
  return { ...n, left: 1 - n.done, balance: (1 - n.done) * n.years };
}

/** The sub-periods of a main period, in months: main years × sub years ÷ 10. */
export function antardasas(lord: string) {
  const k = VIMS.findIndex(([p]) => p === lord);
  const main = VIMS[k][1];
  return Array.from({ length: 9 }, (_, j) => { const [p, y] = VIMS[(k + j) % 9]; return { lord: p, months: (main * y) / 10 }; });
}

export function panchanga(sun: number, moon: number) {
  const elong = mod(moon - sun);
  const t = elong / 12, y = mod(sun + moon) / STAR, k = elong / 6;
  const tithi = Math.floor(t) + 1, yoga = Math.floor(y) + 1, karana = Math.floor(k) + 1;
  const tithiName = tithi === 15 ? "Śukla Pūrṇimā" : tithi === 30 ? "Kṛṣṇa Amāvāsyā" : `${tithi <= 15 ? "Śukla" : "Kṛṣṇa"} ${TITHIS[(tithi - 1) % 15]}`;
  const karanaName = karana === 1 ? "Kiṃstughna" : karana >= 58 ? ["Śakuni", "Catuṣpada", "Nāga"][karana - 58] : KARANAS[(karana - 2) % 7];
  return {
    elong, tithi, tithiName, tithiLeft: 1 - (t % 1),
    sum: mod(sun + moon), yoga, yogaName: YOGAS[yoga - 1], yogaLeft: 1 - (y % 1),
    karana, karanaName, karanaLeft: 1 - (k % 1),
  };
}

export function aprakasha(sun: number) {
  const dhuma = mod(sun + 400 / 3), vyatipata = mod(360 - dhuma), parivesha = mod(vyatipata + 180), indra = mod(360 - parivesha);
  return { Dhooma: dhuma, Vyatipata: vyatipata, Parivesha: parivesha, "Indra Chapa": indra, Upaketu: mod(indra + 50 / 3) };
}

export const KARAKA_SLOTS = ["AK", "AmK", "BK", "MK", "PiK", "PK", "GK", "DK"];
/** The eight-kāraka scheme (the engine's default): Rāhu counted from the end of its sign; ties keep the order given. */
export function charaKarakas(lons: Record<string, number>) {
  const deg = (p: string) => (p === "Rahu" ? 30 - (mod(lons[p]) % 30) : mod(lons[p]) % 30);
  return [...SEVEN, "Rahu"].map((p) => ({ planet: p, deg: deg(p) })).sort((a, b) => b.deg - a.deg)
    .map((x, i) => ({ ...x, slot: KARAKA_SLOTS[i] }));
}

export function arudha(houseSign: number, lordSign: number) {
  const count = house(houseSign, lordSign);
  const raw = mod(lordSign + count - 1, 12);
  const at = house(houseSign, raw);
  const pada = at === 1 ? mod(houseSign + 9, 12) : at === 7 ? mod(houseSign + 3, 12) : raw;
  return { count, raw, pada, exception: at === 1 ? "10th" : at === 7 ? "4th" : null };
}

/** The nine subs of `lon`'s star, and the star, sub and sub-sub lords. */
export function kpLords(lon: number) {
  const x = mod(lon);
  const walk = (start: number, span: number, first: number) =>
    Array.from({ length: 9 }, (_, j) => VIMS[(first + j) % 9]).reduce<{ lord: string; k: number; from: number; to: number }[]>((out, [lord, y]) => {
      const from = out.length ? out[out.length - 1].to : start;
      return [...out, { lord, k: VIMS.findIndex(([p]) => p === lord), from, to: from + (span * y) / 120 }];
    }, []);
  const star = nakshatraOf(x);
  const subs = walk(star.start, STAR, star.index % 9);
  const sub = subs.find((s) => x < s.to) ?? subs[8];
  const subsubs = walk(sub.from, sub.to - sub.from, sub.k);
  const subsub = subsubs.find((s) => x < s.to) ?? subsubs[8];
  return { star, subs, sub, subsub, lords: [star.lord, sub.lord, subsub.lord] };
}

export function trikonaReduce(bav: number[]) {
  const out = [...bav];
  for (let g = 0; g < 4; g++) {
    const trine = [g, g + 4, g + 8];
    const least = Math.min(...trine.map((s) => bav[s]));
    trine.forEach((s) => { out[s] = bav[s] - least; });
  }
  return out;
}

const SPECIAL: Record<string, number[]> = { Mars: [4, 8], Jupiter: [5, 9], Saturn: [3, 10] };
/** Houses (from the planet) and signs that a planet aspects fully. */
export const grahaDrishti = (planet: string, sign: number) =>
  [...(SPECIAL[planet] ?? []), 7].sort((a, b) => a - b).map((h) => ({ house: h, sign: mod(sign + h - 1, 12) }));

export const natural = (a: string, b: string) => NATURAL[SEVEN.indexOf(a as never)][SEVEN.indexOf(b as never)];
export const temporary = (fromSign: number, toSign: number) => ([2, 3, 4, 10, 11, 12].includes(house(fromSign, toSign)) ? 1 : -1);
export const PANCHADHA: Record<number, string> = { 2: "great friend", 1: "friend", 0: "neutral", [-1]: "enemy", [-2]: "great enemy" };

export const isOwnOrExalted = (planet: string, sign: number) => EXALT[planet] === sign || (OWN[planet] ?? []).includes(sign);
export const isDebilitated = (planet: string, sign: number) => EXALT[planet] !== undefined && mod(EXALT[planet] + 6, 12) === sign;
export const MAHAPURUSHA: Record<string, string> = { Mars: "Ruchaka", Mercury: "Bhadra", Jupiter: "Hamsa", Venus: "Malavya", Saturn: "Sasa" };

export const muntha = (lagnaSign: number, years: number) => mod(lagnaSign + years, 12);
export const punyaSaham = (lagna: number, sun: number, moon: number, day: boolean) => mod(day ? lagna + moon - sun : lagna + sun - moon);
export const KUJA_HOUSES = [1, 2, 4, 7, 8, 12];

/** core_logic/ayurdaya.py arc_years: full years at deep exaltation, half at deep debility. */
export function arcYears(planet: string, lon: number, full = PINDA_YEARS[planet]) {
  const arc = mod(DEEP_EXALT[planet] - lon);
  return { arc, years: (full * (arc < 180 ? 360 - arc : arc)) / 360 };
}

/** Jaimini's rule for one pair of signs. */
export function jaiminiClass(a: number, b: number): "long" | "medium" | "short" {
  const m = [a % 3, b % 3].sort().join("");
  return m === "00" || m === "12" ? "long" : m === "01" || m === "22" ? "medium" : "short";
}

const RAHU_PART = [8, 2, 7, 5, 6, 4, 3];
/** Rāhu kāla of a day, in clock hours. */
export function rahuKala(sunrise: number, sunset: number, weekday: number) {
  const part = (sunset - sunrise) / 8;
  const k = RAHU_PART[weekday];
  return { k, part, start: sunrise + (k - 1) * part, end: sunrise + k * part };
}

/** Saturn's part (1–7) of the day or the night: by day the parts run from the weekday's lord, by night from the fifth lord on. */
export const gulikaPart = (weekday: number, night: boolean) => mod(6 - (night ? weekday + 4 : weekday), 7) + 1;

/** Ghaṭīs since sunrise; a birth before sunrise counts from the sunrise before. */
export const ghatis = (birth: number, sunrise: number) => mod(birth - sunrise, 24) * 2.5;

/** A planet's transit from the natal Moon's sign: good or not, and who blocks it. */
export function gocara(planet: string, moonSign: number, signs: Record<string, number>) {
  const h = house(moonSign, signs[planet]);
  const vedha = GOCARA[planet]?.[h];
  const blockers = vedha === undefined ? [] : Object.keys(signs).filter((q) => q !== planet && !NO_VEDHA.has(`${planet}|${q}`) && signs[q] === mod(moonSign + vedha - 1, 12));
  return { house: h, good: vedha !== undefined, vedha, blockers };
}

/** "5:55:02 AM" (maybe with a trailing date) -> clock hours. */
export function clockHours(text: string): number | null {
  const m = /(\d+):(\d+):(\d+)\s*(AM|PM)?/.exec(text);
  if (!m) return null;
  const h = Number(m[1]) % (m[4] ? 12 : 24) + (m[4] === "PM" ? 12 : 0);
  return h + Number(m[2]) / 60 + Number(m[3]) / 3600;
}

/** "20-54-05.56" -> degrees. */
export function dmsDegrees(text: string): number | null {
  const m = /(-?\d+)-(\d+)-([\d.]+)/.exec(text);
  return m ? Number(m[1]) + Number(m[2]) / 60 + Number(m[3]) / 3600 : null;
}

/** The "(7.44% left)" of a core line, as a share. */
export function leftOf(text: string | undefined): number | null {
  const m = text && /([\d.]+)% left/.exec(text);
  return m ? Number(m[1]) / 100 : null;
}

/** Tropical ascendant from the local sidereal time (hours), latitude and obliquity (degrees). */
export function ascendant(lstHours: number, lat: number, eps: number) {
  const r = Math.PI / 180;
  const ramc = mod(lstHours * 15);
  return { ramc, lon: mod(Math.atan2(Math.cos(ramc * r), -(Math.sin(ramc * r) * Math.cos(eps * r) + Math.tan(lat * r) * Math.sin(eps * r))) / r) };
}

/** Mean obliquity of the ecliptic (IAU 1980, first terms), degrees, for a Julian year. */
export const obliquity = (year: number) => 23.439291 - 0.0130042 * ((year - 2000) / 100);
