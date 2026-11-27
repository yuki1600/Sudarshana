import type { Chakras, WheelSlot } from "./api";
import { GHATAKA, type GhatakaDay, ghatakaHits, MONTHS, SHALAKA, SYLLABLES, TARA_KIND, TARA_NAMES, TITHI_GROUPS, WEEKDAY_NAMES } from "./chakraTables";
import { SIGN_NAMES } from "./format";
import { supOrd } from "./ui";
import { CHANDRA, KALA, KOTA_X, KOTA_Y, pack, type Row, rowsOf, SBC, SHOOLA, SURYA, type Wheel } from "./wheelGeometry";

/** A slot's natal bodies, and (Starlight) the transit bodies on it: `over`, undefined when transits are not shown. */
export type Slot = WheelSlot & { over?: string[] };
/** What Starlight lights on a drawing, by slot key (a star, a sign's sector, a box "r-c" or a Kurma direction): the picked one, the lit ones, the native's own, and the wheel's danger points. */
export interface Picks { sel?: string | null; lit?: ReadonlySet<string>; here?: ReadonlySet<string>; tips?: ReadonlySet<string>; onPick?: (key: string) => void }

const cls = (key: string, p?: Picks) => "slot" + (p?.sel === key ? " selected" : p?.here?.has(key) ? " here" : "") + (p?.lit?.has(key) ? " lit" : "") + (p?.tips?.has(key) ? " tip" : "");

/** `y` is the first row's baseline. */
function Rows({ x, y, rows, size }: { x: number; y: number; rows: Row[]; size: number }) {
  return <>{rows.map(([text, transit], i) => <text key={i} x={x} y={y + i * size} textAnchor="middle" className={transit ? "wheel-body transit" : "wheel-body"} style={{ fontSize: size }}>{text}</text>)}</>;
}
const Bodies = ({ x, y, names, over, size = 28 }: { x: number; y: number; names: string[]; over?: string[]; size?: number }) => <Rows x={x} y={y} rows={rowsOf(names, over, Infinity)} size={size} />;

/** A wheel drawn from its geometry: each slot's star, with the bodies on it underneath. */
export function StarWheel({ wheel, slots, title, picks }: { wheel: Wheel; slots: Slot[]; title: string; picks?: Picks }) {
  return (
    <svg viewBox={wheel.box} className="wheel" role="img" aria-label={title}>
      {wheel.circle && <circle cx={wheel.circle[0]} cy={wheel.circle[1]} r={wheel.circle[2]} className="wheel-line" />}
      {wheel.lines.map(([a, b, c, d], i) => <line key={i} x1={a} y1={b} x2={c} y2={d} className="wheel-line" />)}
      {wheel.labels?.map(([t, x, y]) => <text key={t} x={x} y={y} textAnchor="middle" className="wheel-note">{t}</text>)}
      {slots.map((s, i) => {
        const [x, y] = wheel.slots[i], fit = wheel.fit, w = (fit ?? 94) + 16;
        // a packed wheel's grahas fill the room under the star, down to the next star below them
        const room = () => Math.min(60, ...wheel.slots.filter(([sx, sy]) => sy > y && Math.abs(sx - x - 16) < fit! / 2 + 28).map(([, sy]) => sy - y - 24));
        const p = fit ? pack(s.bodies, s.over, (a, b) => Math.min(fit / a, room() / b), wheel.body ?? 28) : null;
        const bottom = p ? y + 6 + p.rows.length * p.size : y + 36 + (s.over?.length && s.bodies.length ? 28 : 0);
        return <g key={s.star} onClick={picks?.onPick && (() => picks.onPick!(s.star))}>
          {picks && <rect x={x + 9 - w / 2} y={y - 26} width={w} height={bottom - y + 34} rx={10} className={cls(s.star, picks)} />}
          <text x={x} y={y} textAnchor="middle" className="wheel-star">{s.star}</text>
          {p ? <Rows x={x + 16} y={y + 6 + 0.8 * p.size} rows={p.rows} size={p.size} /> : <Bodies x={x + 16} y={y + 36} names={s.bodies} over={s.over} />}
        </g>;
      })}
    </svg>
  );
}

const CELL = 88;
/** Kota's four walls, from the cell's distance to the edge of the 9 x 9 square. */
export const KOTA_ZONES = ["Bahya", "Praakaara", "Durgantara", "Stambha"];
export const kotaZone = (i: number) => Math.min(3, KOTA_X[i], KOTA_Y[i], 8 - KOTA_X[i], 8 - KOTA_Y[i]);

export function Kota({ k, slots = k.slots, picks }: { k: Chakras["kota"]; slots?: Slot[]; picks?: Picks }) {
  const ring = (n: number, cls: string) => <rect x={n * CELL} y={n * CELL} width={(9 - 2 * n) * CELL} height={(9 - 2 * n) * CELL} className={cls} />;
  return (
    <>
      {!picks && <p className="wheel-caption">Kota Swami (fort lord): <strong>{k.swami}</strong> · Kota Pala (fort guard): <strong>{k.pala}</strong></p>}
      <svg viewBox={`0 0 ${9 * CELL} ${9 * CELL}`} className="wheel square" role="img" aria-label="Kota Chakra">
        {ring(0, "kota bahya")}{ring(1, "kota prakaara")}{ring(2, "kota durga")}{ring(3, "kota stambha")}
        {slots.map((s, i) => {
          const x = (KOTA_X[i] + 0.5) * CELL, y = KOTA_Y[i] * CELL + 24;
          return <g key={s.star} onClick={picks?.onPick && (() => picks.onPick!(s.star))}>
            {picks && <rect x={KOTA_X[i] * CELL + 3} y={KOTA_Y[i] * CELL + 3} width={CELL - 6} height={CELL - 6} rx={8} className={cls(s.star, picks)} />}
            <text x={x} y={y} textAnchor="middle" className="wheel-star small">{s.star}</text><Bodies x={x} y={y + 30} names={s.bodies} over={s.over} size={picks ? 22 : 28} />
          </g>;
        })}
        <text x={5.5 * CELL} y={5.65 * CELL} textAnchor="middle" className="wheel-note">Stambha</text>
        <text x={5.5 * CELL} y={6.5 * CELL} textAnchor="middle" className="wheel-note">Durgantara</text>
        <text x={6.3 * CELL} y={7.5 * CELL} textAnchor="middle" className="wheel-note">Praakaara</text>
        <text x={6.9 * CELL} y={8.55 * CELL} textAnchor="middle" className="wheel-note">Bahya</text>
      </svg>
    </>
  );
}

/** The boxes a box aspects: its row and column unless it is on the edge of them, both diagonals, and the corners' two neighbours. */
export function vedhas(r: number, c: number): Set<string> {
  const out = new Set<string>();
  for (let i = 0; i < 9; i++) for (let j = 0; j < 9; j++) {
    let hit = (r === i && r !== 0 && r !== 8) || (c === j && c !== 0 && c !== 8) || r - i === c - j || r - i === j - c;
    if (r === 0 && c === 0 && i + j === 1) hit = true;
    if (r === 8 && c === 0 && i - j === 7) hit = true;
    if (r === 8 && c === 8 && i + j === 15) hit = true;
    if (r === 0 && c === 8 && i - j === -7) hit = true;
    if (hit && !(i === r && j === c)) out.add(`${i}-${j}`);
  }
  return out;
}

/** A graha in a Sarvatobhadra box: its box, its name and whether it is the transit's (else the natal chart's). */
export interface SbcGraha { key: string; g: string; transit: boolean }
const SBC_GRAHAS = new Set(["Su", "Mo", "Ma", "Me", "Ju", "Ve", "Sa", "Ra", "Ke"]);

/** A box's bodies a row each, natal then transit, each name drawn on its own so a graha can be clicked (``onGraha``) and the picked one
 *  shown, purple behind it; the row shrinks to fit the box's width ``w``. */
function SbcBodies({ x, y, w, rows, size, at, picked, onGraha }: { x: number; y: number; w: number; rows: [string[], boolean][]; size: number; at: string;
  picked?: SbcGraha | null; onGraha: (p: SbcGraha) => void }) {
  return <>{rows.map(([names, transit], i) => {
    const ems = names.map((n) => 0.6 * n.length + 0.35), z = Math.min(size, (w - 8) / ems.reduce((a, b) => a + b, 0));
    let left = x - (ems.reduce((a, b) => a + b, 0) * z) / 2;
    const yy = y + i * size;
    return names.map((n, k) => {
      const cx = left + (ems[k] * z) / 2, on = picked?.key === at && picked.g === n && picked.transit === transit, can = SBC_GRAHAS.has(n);
      left += ems[k] * z;
      return <g key={`${i}${k}`} className={can ? "sbc-graha" : undefined} onClick={can ? (e) => { e.stopPropagation(); onGraha({ key: at, g: n, transit }); } : undefined}>
        {can && <rect x={cx - (ems[k] * z) / 2} y={yy - 0.85 * z} width={ems[k] * z} height={1.1 * z} rx={4} className={on ? "sbc-graha-box on" : "sbc-graha-box"} />}
        <text x={cx} y={yy} textAnchor="middle" className={(transit ? "wheel-body transit" : "wheel-body") + (on ? " on" : "")} style={{ fontSize: z }}>{n}</text>
      </g>;
    });
  })}</>;
}

/** ``main``: the boxes of the main vedha of the grahas in the picked box (or of the graha picked in it), light purple over the grey of
 *  ``shaded``. ``onGraha`` (Starlight): each graha in a box can be clicked, ``graha`` the one picked. */
export function Sarvatobhadra({ s, over, marked, shaded, main, onBox, picks, table = true, graha, onGraha }: {
  s: Chakras["sarvatobhadra"]; over?: Record<string, string[]>; marked?: ReadonlySet<string>; shaded?: ReadonlySet<string>; main?: ReadonlySet<string>;
  onBox?: (e: React.MouseEvent, r: number, c: number, star: string | null) => void; picks?: Picks; table?: boolean;
  graha?: SbcGraha | null; onGraha?: (p: SbcGraha) => void;
}) {
  const C = 88;
  const svg = (
    <svg viewBox={`0 0 ${9 * C} ${9 * C}`} className="wheel square" role="img" aria-label="Sarvatobhadra Chakra">
      {SBC.flatMap((row, r) => row.map((cell, c) => {
        const x = c * C, y = r * C, key = `${r}-${c}`;
        const star = typeof cell === "string" && cell.startsWith("*") ? cell.slice(1) : null;
        const [top, under] = typeof cell === "string" ? [cell, ""] : cell;
        return (
          <g key={key} onClick={picks?.onPick && (() => picks.onPick!(key))} onContextMenu={onBox && ((e) => { e.preventDefault(); e.stopPropagation(); onBox(e, r, c, star); })}>
            <rect x={x} y={y} width={C} height={C} className={`sbc-cell${marked?.has(key) ? " special" : main?.has(key) ? " vedha-main" : shaded?.has(key) ? " vedha" : ""}`} />
            {picks && <rect x={x + 3} y={y + 3} width={C - 6} height={C - 6} className={cls(key, picks)} />}
            {star ? (
              <>
                <text x={x + C / 2} y={y + 24} textAnchor="middle" className="wheel-star small">{star}</text>
                {onGraha
                  ? <SbcBodies x={x + C / 2} y={y + (over ? 50 : 62)} w={C} size={over ? 22 : 26} at={key} picked={graha} onGraha={onGraha}
                    rows={[[s.stars[star] ?? [], false] as [string[], boolean], ...(over ? [[over[star] ?? [], true] as [string[], boolean]] : [])].filter(([n]) => n.length)} />
                  : <Bodies x={x + C / 2} y={y + (over ? 50 : 62)} names={s.stars[star] ?? []} over={over && (over[star] ?? [])} size={over ? 22 : 26} />}
              </>
            ) : (
              <>
                <text x={x + C / 2} y={y + (under ? 40 : 52)} textAnchor="middle" className="sbc-text">{top}</text>
                {under && <text x={x + C / 2} y={y + 66} textAnchor="middle" className="wheel-note small">{under}</text>}
              </>
            )}
          </g>
        );
      }))}
    </svg>
  );
  if (!table) return svg;
  return (
    <div className="sbc">
      {svg}
      <table className="points">
        <thead><tr><th>Nakshatra</th><th>From Moon</th><th>From Lagna</th></tr></thead>
        <tbody>{s.special.map((r) => <tr key={r[0]}>{r.map((c, i) => <td key={i}>{supOrd(c)}</td>)}</tr>)}</tbody>
      </table>
    </div>
  );
}

const polar = (r: number, deg: number): [number, number] => [400 + r * Math.cos((deg - 90) * Math.PI / 180), 400 + r * Math.sin((deg - 90) * Math.PI / 180)];
const wedge = (k: number, r: number) => { const [ax, ay] = polar(r, k * 30), [bx, by] = polar(r, (k + 1) * 30); return `M400 400 L${ax} ${ay} A${r} ${r} 0 0 1 ${bx} ${by} Z`; };
/** Sector `k` of the band between radii `r0` and `r1`. */
const band = (k: number, r0: number, r1: number) => {
  const [ax, ay] = polar(r1, k * 30), [bx, by] = polar(r1, (k + 1) * 30), [cx, cy] = polar(r0, (k + 1) * 30), [dx, dy] = polar(r0, k * 30);
  return `M${dx} ${dy} L${ax} ${ay} A${r1} ${r1} 0 0 1 ${bx} ${by} L${cx} ${cy} A${r0} ${r0} 0 0 0 ${dx} ${dy} Z`;
};

/** Each ring's middle radius, then 0.9 of its room across the ring and along it (the chord there). */
const RING = [[150, 99, 70], [259, 77, 121], [353, 77, 164]];
/** Sector `k` of every ring holds the same house: (2 - k) mod 12 + 1 from the lagna, Moon and Sun. Picks are keyed by the sector. */
export function Sudarsana({ rings, picks }: { rings: { from: string; sectors: { sign: string; bodies: string[]; over?: string[] }[] }[]; picks?: Picks }) {
  const R = [213, 306, 400];
  return (
    <svg viewBox="-5 -5 810 810" className="wheel square" role="img" aria-label="Sudarsana Chakra: rings from the lagna, Moon and Sun">
      <circle cx={400} cy={400} r={R[2]} className="ring outer" /><circle cx={400} cy={400} r={R[1]} className="ring middle" /><circle cx={400} cy={400} r={R[0]} className="ring inner" />
      {picks && Array.from({ length: 12 }, (_, k) => <path key={k} d={wedge(k, R[2] - 3)} className={cls(String(k), picks)} onClick={picks.onPick && (() => picks.onPick!(String(k)))} />)}
      {/* each ring's own sign (sector 2): the Lagna's in the inner ring, the Moon's in the middle, the Sun's outside */}
      {picks && R.map((r, i) => <path key={`own${i}`} d={band(2, i ? R[i - 1] : 0.01, r)} className="sc-own" />)}
      {Array.from({ length: 12 }, (_, k) => { const [x, y] = polar(R[2], k * 30); return <line key={k} x1={400} y1={400} x2={x} y2={y} className="wheel-line" />; })}
      {rings.map((ring, i) => ring.sectors.map((s, k) => {
        // the sector's sign, then its grahas, stacked about the ring's middle: the block's reach across the ring and along it each stays inside the sector
        const deg = (k + 0.5) * 30, [r, across, along] = RING[i], [x, y] = polar(r, deg), head = 19;
        const sin = Math.abs(Math.sin(deg * Math.PI / 180)), cos = Math.abs(Math.cos(deg * Math.PI / 180));
        const { rows, size } = pack(s.bodies, s.over, (a, b) => Math.min((across - head * cos) / (a * sin + b * cos), (along - head * sin) / (a * cos + b * sin)), 26);
        const top = y - (head + rows.length * size) / 2;
        return <g key={`${i}-${k}`} pointerEvents="none"><text x={x} y={top + 15} textAnchor="middle" className="wheel-star small">{s.sign}</text><Rows x={x} y={top + head + 0.8 * size} rows={rows} size={size} /></g>;
      }))}
    </svg>
  );
}

const TX = [102, 268, 435, 601, 768], TY = [288, 439, 592, 744, 897];
export const TRI_SLOTS: [number, number][] = [[2, 0], [3, 0], [4, 1], [4, 2], [4, 3], [3, 4], [2, 4], [1, 4], [0, 3], [0, 2], [0, 1], [1, 0]];
export const TRI_EDGES: [number, number, number, number][] = [[1, 0, 0, 1], [2, 0, 0, 2], [3, 0, 0, 3], [4, 1, 1, 4], [4, 2, 2, 4], [4, 3, 3, 4],
  [3, 0, 4, 1], [2, 0, 4, 2], [1, 0, 4, 3], [0, 1, 3, 4], [0, 2, 2, 4], [0, 3, 1, 4],
  [1, 0, 1, 4], [2, 0, 2, 4], [3, 0, 3, 4], [0, 1, 4, 1], [0, 2, 4, 2], [0, 3, 4, 3]];
/** The slots a Tripataki slot has vedha with: the other end of each line through it. */
export function triVedhas(k: number): Set<number> {
  const [c, r] = TRI_SLOTS[k], out = new Set<number>();
  for (const [a, b, x, y] of TRI_EDGES) {
    const other = a === c && b === r ? [x, y] : x === c && y === r ? [a, b] : null;
    if (other) out.add(TRI_SLOTS.findIndex(([p, q]) => p === other[0] && q === other[1]));
  }
  out.delete(-1);
  return out;
}

export function Tripataki({ slots, picks }: { slots: { sign: string; bodies: string[]; over?: string[] }[]; picks?: Picks }) {
  const p = (c: number, r: number) => [TX[c], TY[r]];
  const at = picks?.sel ? slots.findIndex((s) => s.sign === picks.sel) : -1;
  const [sc, sr] = at >= 0 ? TRI_SLOTS[at] : [-1, -1];
  return (
    <svg viewBox="20 190 860 800" className="wheel" role="img" aria-label="Tripataki Chakra">
      {TRI_EDGES.map(([a, b, c, d], i) => { const [x1, y1] = p(a, b), [x2, y2] = p(c, d); return <line key={i} x1={x1} y1={y1} x2={x2} y2={y2} className={(a === sc && b === sr) || (c === sc && d === sr) ? "wheel-line lit" : "wheel-line"} />; })}
      {[1, 2, 3].map((c) => <path key={c} d={`M${TX[c]} ${TY[0]} L${TX[c]} ${TY[0] - 32} L${TX[c] - 34} ${TY[0] - 16} Z`} className="wheel-line" />)}
      {slots.map((s, k) => {
        const [c, r] = TRI_SLOTS[k];
        const x = TX[c] + (c === 0 ? -34 : c === 4 ? 34 : 0), y = TY[r] + (r === 0 ? -86 : r === 4 ? 24 : 6);
        return <g key={s.sign} onClick={picks?.onPick && (() => picks.onPick!(s.sign))}>
          {picks && <rect x={x - 48} y={y - 28} width={112} height={s.over?.length && s.bodies.length ? 96 : 72} rx={10} className={cls(s.sign, picks)} />}
          <text x={x} y={y} textAnchor="middle" className="wheel-star">{s.sign}</text><Bodies x={x + 16} y={y + 34} names={s.bodies} over={s.over} />
        </g>;
      })}
    </svg>
  );
}

/** Kurma Chakra (Brihat Samhita 14): the tortoise's nine parts as on a map, North up and East to the right. */
const KURMA_AT: Record<string, [number, number]> = { NW: [0, 0], North: [1, 0], NE: [2, 0], West: [0, 1], Madhya: [1, 1], East: [2, 1], SW: [0, 2], South: [1, 2], SE: [2, 2] };
export function Kurma({ regions, picks }: { regions: { dir: string; stars: string[]; bodies: string[]; over?: string[] }[]; picks?: Picks }) {
  const K = 260;
  return (
    <svg viewBox={`-4 -4 ${3 * K + 8} ${3 * K + 8}`} className="wheel square" role="img" aria-label="Kurma Chakra">
      {regions.map((g) => {
        const [c, r] = KURMA_AT[g.dir], x = c * K, y = r * K;
        return <g key={g.dir} onClick={picks?.onPick && (() => picks.onPick!(g.dir))}>
          <rect x={x + 4} y={y + 4} width={K - 8} height={K - 8} rx={14} className={`kurma-cell${g.dir === "Madhya" ? " middle" : ""} ${cls(g.dir, picks)}`} />
          <text x={x + K / 2} y={y + 44} textAnchor="middle" className="wheel-note kurma-dir">{g.dir}</text>
          <text x={x + K / 2} y={y + 86} textAnchor="middle" className="wheel-star small">{g.stars.join(" · ")}</text>
          <Bodies x={x + K / 2} y={y + 150} names={g.bodies} over={g.over} size={30} />
        </g>;
      })}
    </svg>
  );
}

/** Grahas packed into a w by h block whose top is `y`, centred on `x`. */
function Packed({ x, y, w, h, names, over, max }: { x: number; y: number; w: number; h: number; names: string[]; over?: string[]; max: number }) {
  const p = pack(names, over, (a, b) => Math.min(w / a, h / b), max);
  return <Rows x={x} y={y + 0.8 * p.size} rows={p.rows} size={p.size} />;
}

/** Tara (Navatara) Chakra: the 27 stars from the natal Moon's, nine taras across and three rounds down. */
export function TaraChakra({ slots, picks }: { slots: Slot[]; picks?: Picks }) {
  const C = 110, H = 116, top = 76;
  return (
    <svg viewBox={`0 0 ${9 * C} ${top + 3 * H}`} className="wheel square" role="img" aria-label="Tara Chakra">
      {TARA_NAMES.map((n, c) => <g key={n}>
        <text x={c * C + C / 2} y={30} textAnchor="middle" className="wheel-note small">{n}</text>
        <text x={c * C + C / 2} y={58} textAnchor="middle" className="wheel-note small">{TARA_KIND[c]}</text>
      </g>)}
      {slots.map((s, i) => {
        const x = (i % 9) * C, y = top + Math.floor(i / 9) * H;
        return <g key={s.star} onClick={picks?.onPick && (() => picks.onPick!(s.star))}>
          <rect x={x} y={y} width={C} height={H} className="sbc-cell" />
          {picks && <rect x={x + 3} y={y + 3} width={C - 6} height={H - 6} className={cls(s.star, picks)} />}
          <text x={x + C / 2} y={y + 28} textAnchor="middle" className="wheel-star small">{s.star}</text>
          <Packed x={x + C / 2} y={y + 38} w={C - 12} h={H - 44} names={s.bodies} over={s.over} max={24} />
        </g>;
      })}
    </svg>
  );
}

const SH0 = 230, SH = 90;     // the first line, and the lines' spacing
/** Where a star's end of its line is: the line ("v" down, "h" across, by number) and the box its label goes in. */
function shalakaEnd(k: number): { line: [string, number]; x: number; y: number; w: number; h: number } {
  const at = (n: number) => SH0 + SH * n;
  if (k < 7) return { line: ["v", k], x: at(k) - 44, y: 20, w: 88, h: 196 };
  if (k < 14) return { line: ["h", k - 7], x: 784, y: at(k - 7) - 44, w: 196, h: 88 };
  if (k < 21) return { line: ["v", 20 - k], x: at(20 - k) - 44, y: 784, w: 88, h: 196 };
  return { line: ["h", 27 - k], x: 20, y: at(27 - k) - 44, w: 196, h: 88 };
}

export function SaptaShalaka({ slots, focus, picks }: { slots: Slot[]; focus?: string; picks?: Picks }) {
  const f = focus ? shalakaEnd(SHALAKA.indexOf(focus)).line : null;
  const end = SH0 + 6 * SH;
  return (
    <svg viewBox="0 0 1000 1000" className="wheel square" role="img" aria-label="Sapta Shalaka Chakra">
      {Array.from({ length: 7 }, (_, n) => <g key={n}>
        <line x1={SH0 + SH * n} y1={SH0} x2={SH0 + SH * n} y2={end} className={`wheel-line${f?.[0] === "v" && f[1] === n ? " lit" : ""}`} />
        <line x1={SH0} y1={SH0 + SH * n} x2={end} y2={SH0 + SH * n} className={`wheel-line${f?.[0] === "h" && f[1] === n ? " lit" : ""}`} />
      </g>)}
      {slots.map((s) => {
        const b = shalakaEnd(SHALAKA.indexOf(s.star)), side = b.w > b.h;
        return <g key={s.star} onClick={picks?.onPick && (() => picks.onPick!(s.star))}>
          {picks && <rect x={b.x} y={b.y} width={b.w} height={b.h} rx={10} className={cls(s.star, picks)} />}
          <text x={b.x + b.w / 2} y={b.y + 30} textAnchor="middle" className="wheel-star small">{s.star}</text>
          <Packed x={b.x + b.w / 2} y={b.y + 40} w={b.w - 12} h={b.h - (side ? 44 : 48)} names={s.bodies} over={s.over} max={24} />
        </g>;
      })}
    </svg>
  );
}

/** Avakahada Chakra: the 108 padas with their syllables, nine stars to a column (each column four signs), the grahas in their padas. */
export function Avakahada({ padas, names, picks }: { padas: Slot[]; names: string[]; picks?: Picks }) {
  const W = 330, H = 100, P = W / 4;
  return (
    <svg viewBox={`0 0 ${3 * W} ${9 * H}`} className="wheel square" role="img" aria-label="Avakahada Chakra">
      {names.map((n, k) => {
        const x = Math.floor(k / 9) * W, y = (k % 9) * H;
        return <g key={n}>
          <rect x={x} y={y} width={W} height={H} className="sbc-cell" />
          <text x={x + W / 2} y={y + 24} textAnchor="middle" className="wheel-star small">{n}</text>
          {[0, 1, 2, 3].map((j) => {
            const i = 4 * k + j, s = padas[i], px = x + j * P;
            return <g key={j} onClick={picks?.onPick && (() => picks.onPick!(String(i)))}>
              {picks && <rect x={px + 3} y={y + 33} width={P - 6} height={H - 36} rx={6} className={cls(String(i), picks)} />}
              <text x={px + P / 2} y={y + 58} textAnchor="middle" className="sbc-text">{SYLLABLES[i]}</text>
              <Packed x={px + P / 2} y={y + 66} w={P - 10} h={H - 70} names={s.bodies} over={s.over} max={18} />
            </g>;
          })}
        </g>;
      })}
    </svg>
  );
}

export function Ghataka({ stars, day, moonSign, picks }: { stars: string[]; day?: GhatakaDay; moonSign: number; picks?: Picks }) {
  const cols: [string, number, (r: number) => string][] = [["Janma rasi", 170, (r) => SIGN_NAMES[r]], ["Month", 165, (r) => MONTHS[GHATAKA.month[r]]],
    ["Tithi", 190, (r) => TITHI_GROUPS[GHATAKA.tithi[r]]], ["Weekday", 140, (r) => WEEKDAY_NAMES[GHATAKA.weekday[r]]],
    ["Nakshatra", 175, (r) => stars[GHATAKA.star[r]]], ["Moon in", 150, (r) => SIGN_NAMES[GHATAKA.sign[r]]]];
  const W = cols.reduce((a, [, w]) => a + w, 0), top = 50, H = 56;
  const xs = cols.map((_, i) => cols.slice(0, i).reduce((a, [, w]) => a + w, 0));
  const hits = day ? ghatakaHits(moonSign, day) : [];
  return (
    <svg viewBox={`0 0 ${W} ${top + 12 * H}`} className="wheel square" role="img" aria-label="Ghataka Chakra">
      {cols.map(([n, w], c) => <text key={n} x={xs[c] + w / 2} y={32} textAnchor="middle" className="wheel-note small">{n}</text>)}
      {Array.from({ length: 12 }, (_, r) => {
        const y = top + r * H;
        return <g key={r} onClick={picks?.onPick && (() => picks.onPick!(String(r)))}>
          {cols.map(([n, w, text], c) => <g key={n}>
            <rect x={xs[c]} y={y} width={w} height={H} className="sbc-cell" />
            {r === moonSign && c > 0 && hits[c - 1] && <rect x={xs[c] + 3} y={y + 3} width={w - 6} height={H - 6} className="slot lit" />}
            <text x={xs[c] + w / 2} y={y + 36} textAnchor="middle" className="sbc-text">{text(r)}</text>
          </g>)}
          {picks && <rect x={2} y={y + 2} width={W - 4} height={H - 4} rx={6} className={cls(String(r), picks)} />}
        </g>;
      })}
    </svg>
  );
}

export { CHANDRA, KALA, SHOOLA, SURYA };
