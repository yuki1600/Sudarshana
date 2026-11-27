import { bodyKind, bodySizes, degOf, degText, fitted, fittedEach, flow, stripColumns, stripPitch, stripRowHeight, type BodySizes } from "./chartGeometry";
import { SIGNS } from "./format";
import { useShape } from "./hooks";
import { retroMark, shown, signName } from "./names";
import { FONT_FACTORS, useChart } from "./store";
import { toneStyle } from "./tone";

// Box (row, column) of each sign in the South Indian square; Aries is fixed at the top, second from the left.
export const CELL: [number, number][] = [[0, 1], [0, 2], [0, 3], [1, 3], [2, 3], [3, 3], [3, 2], [3, 1], [3, 0], [2, 0], [1, 0], [0, 0]];

export interface Panel { title: string; lagna: number; boxes: Record<string, string[]> }

export interface Decoration {
  chartName?: string;                       // "Natal Chart", or the mode's chart
  note?: string;                            // a third line in the centre: "Arudhas of Planets", "Bhava from Moon"
  classes?: Record<string, number> | null;  // relationship class of each planet, 0 self .. 5 great enemy
  selected?: string | null;                 // the body a highlight or relationship is about
  interactive?: boolean;                    // right-clicks say which rasi and which body
  degrees?: Record<string, number>;         // each graha's degrees in its sign, drawn beside it
  moved?: Record<string, string>;           // a bhava chart's grahas whose box is not their sign: that sign, after the degrees
  retro?: string[];                         // the retrograde grahas, drawn in red (Starlight)
  each?: boolean;                           // each box sized to its own bodies, the other points at its bottom right (Starlight)
  muntha?: number;                          // a Tajaka chart's Muntha box, tinted
  focus?: number;                           // the box of the graha open on the Grahas tab, tinted purple (Starlight)
  plain?: boolean;                          // ``degrees`` order and place the grahas, but aren't drawn (longitudes turned off in Starlight)
  bare?: boolean;                           // no sign names, and with ``each`` a box's bodies grow up to half again to fill it (Matching)
  top?: React.ReactNode;                    // controls atop the centre (the Divisional charts' Rasi / Bhava): under them the name, title and note, the lot centred together
}

interface Props extends Decoration {
  title: string;
  /** Text lines of a sign's box: bodies for a chart, a bindu count for an ashtakavarga. */
  cell: (sign: number) => string[];
  lagnaSign?: number;
  shaded?: ReadonlySet<number>;
  compact?: boolean;
  /** How strong each sign's number is, 0 weak to 1 strong: the box is filled red to green. */
  tone?: (sign: number) => number;
}

/** A chart's text sizes as the CSS variables its labels read. */
export const sizeVars = (z: BodySizes) => ({ "--major": `${z.major}px`, "--minor": `${z.minor}px`, "--strip": `${z.strip}px`, "--sign": `${z.sign}px`, "--sub": `${z.sub}px` }) as React.CSSProperties;

/** One body's text: its size by kind, its relationship colour, and what a right-click needs. */
export function BodyText({ t, x, y, d, small, end }: { t: string; x: number; y: number; d: Decoration; small?: boolean; end?: boolean }) {
  const cls = d.classes?.[t.replace(/R$/, "")];
  const display = useChart((s) => s.display);
  return (
    <text x={x} y={y} textAnchor={end ? "end" : undefined} data-body={d.interactive ? t : undefined} className={`body-label ${small ? "small" : bodyKind(t)}${t === "As" ? " lagna" : ""}${cls !== undefined ? ` rel${cls}` : ""}${d.selected === t || d.selected === t.replace(/R$/, "") ? " selected" : ""}${degOf(t, d.degrees) !== undefined && !d.plain ? " graha-deg" : ""}${d.retro?.includes(t.replace(/R$/, "")) ? " retro" : ""}`}>{shown(t, display)}{degOf(t, d.degrees) !== undefined && !d.plain && <tspan className="deg">{` ${degText(degOf(t, d.degrees)!)}${d.moved?.[t.replace(/R$/, "")] ? ` ${d.moved[t.replace(/R$/, "")]}` : ""}`}</tspan>}</text>
  );
}

/** The centre of a chart: which chart, the varga's name, its number and scheme, and the note. */
export function titleLines(title: string): [string, string] {
  const m = title.match(/^(.*?) ?(D-\d.*)$/);
  return m ? [m[1], m[2]] : [title, ""];
}

/** The varga's name in the centre; a long hyphenated one goes on two lines without its hyphen ("Dwadasa" over "Dwadasamsa"). */
const titleRows = (big: string) => (big.length > 14 ? big.split("-") : [big]);
/** The first row sits where a one-line name does (the same gap to what is above); the rest go below. */
export function BigTitle({ big, x, y, line, className }: { big: string; x: number; y: number; line: number; className: string }) {
  return (
    <text x={x} y={y} textAnchor="middle" dominantBaseline="middle" className={className}>
      {titleRows(big).map((r, i) => <tspan key={i} x={x} dy={i ? line : 0}>{r}</tspan>)}
    </text>
  );
}
/** How far the lines below the name move for its extra rows. */
export const titleShift = (big: string, line: number) => (titleRows(big).length - 1) * line;

export function SouthGrid({ title, cell, lagnaSign, shaded, compact, tone, ...d }: Props) {
  const W = 100;
  const [ref, k, px] = useShape();
  const H = W * k;
  const display = useChart((s) => s.display);
  const factor = FONT_FACTORS[display.chartFont];
  const low = !!(d.each && d.degrees);
  const name = (sign: number) => (display.layout === "starlight" && !d.bare ? signName(sign, SIGNS[sign], display) : undefined);     // Starlight: the first row beside the sign's name
  const boxes = CELL.map((_, sign) => ({ labels: cell(sign), w: W, h: H, stripAlong: !d.degrees, deg: d.degrees, beside: true, low, moved: d.moved, plain: d.plain, name: name(sign) }));
  const base = d.bare || (d.each && !display.signLabels) ? { ...bodySizes(px, factor), sign: 0 } : bodySizes(px, factor);
  const z = compact ? base : fitted(base, boxes, factor);
  const each = d.each && !compact ? fittedEach(base, boxes, factor, d.bare ? 1.5 : 1) : null;
  const [big, small] = titleLines(title);
  const shift = titleShift(big, 26);
  // with controls atop the centre: they, the chart's name, the title, its scheme and the note stacked as one block, centred in the centre
  // square; the lines' offsets from the middle as without them, all moved by ``dy``
  const top = d.top && !compact ? d.top : null;
  const B = 30, GAP = 12;     // the controls' height, and their gap to the first line
  const above = d.chartName ? -34 - 0.72 * z.sub : -14;     // the first line's top: the name's cap height, or the title's half height
  const below = (d.note ? 50 : small ? 30 : 12) + shift;     // the last line's foot
  const dy = top ? -(above - GAP - B + below) / 2 : 0;
  const mid = 2 * H + dy;
  return (
    <svg ref={ref} viewBox={`0 0 ${4 * W} ${4 * H}`} className={compact ? "grid compact" : "grid"} style={sizeVars(z)} role="img" aria-label={title}>
      <rect x={W} y={H} width={2 * W} height={2 * H} fill="none" className="centre" />{/* tinted by CSS where wanted (Matching) */}
      {CELL.map(([r, c], sign) => {
        const labels = cell(sign);
        const x = c * W, y = r * H, zb = each?.[sign] ?? z;
        const flowed = compact ? [] : flow(d.degrees ? labels : labels.filter((t) => bodyKind(t) !== "strip"), W, zb, d.degrees, true, low ? H : undefined, sign >= 8, name(sign));     // Sagittarius .. Pisces run upward
        return (
          <g key={sign} data-sign={d.interactive ? sign : undefined} style={each ? sizeVars(zb) : undefined}>
            <rect x={x} y={y} width={W} height={H} className={`box${shaded?.has(sign) ? " shaded" : ""}${d.muntha === sign ? " muntha" : ""}${d.focus === sign ? " focus" : ""}${tone ? " toned tone" : ""}`} style={tone ? toneStyle(tone(sign)) : undefined} />
            {lagnaSign === sign && <path d={`M${x} ${y} l${W * 0.28} 0 l${-W * 0.28} ${W * 0.28} z`} className="lagna-mark" />}
            {!compact && !d.bare && <text x={x + W - 4} y={y + zb.sign + 3} textAnchor="end" className="sign-name">{signName(sign, SIGNS[sign], display)}</text>}
            {compact ? labels.map((t, i) => <text key={i} x={x + W / 2} y={y + H / 2 + W * 0.12} textAnchor="middle" className="body-label">{t}</text>)
              : flowed.map((l, i) => <BodyText key={i} t={l.t} x={x + l.x} y={y + l.y} d={d} end={l.end} />)}
            {!compact && !d.degrees && labels.filter((t) => bodyKind(t) === "strip").map((t, i) => <BodyText key={t} t={t} x={x + 6 + (i % stripColumns(zb, W)) * stripPitch(zb)} y={y + H - 6 - Math.floor(i / stripColumns(zb, W)) * stripRowHeight(zb)} d={d} />)}
          </g>
        );
      })}
      {/* the lagna's box outlined over its neighbours' edges; only the Starlight theme shows it (in place of the corner mark) */}
      {lagnaSign != null && <rect x={CELL[lagnaSign][1] * W + 1} y={CELL[lagnaSign][0] * H + 1} width={W - 2} height={H - 2} className="lagna-box" />}
      {top && <foreignObject x={W} y={mid + above - GAP - B} width={2 * W} height={B}>{top}</foreignObject>}
      {d.chartName && !compact && <text x={2 * W} y={mid - 34} textAnchor="middle" className="grid-sub">{d.chartName}</text>}
      <BigTitle big={big} x={2 * W} y={mid} line={26} className="grid-title" />
      {small && <text x={2 * W} y={mid + 26 + shift} textAnchor="middle" className="grid-sub">{small}</text>}
      {d.note && <text x={2 * W} y={mid + 46 + shift} textAnchor="middle" className="grid-sub note">{d.note}</text>}
    </svg>
  );
}

/** Two charts in one square (Chakras > Mixed 2-Vargas, the mixed charts of the modes): ``inner`` nested inside ``outer``. */
export function MixedGrid({ inner, outer }: { inner: Panel; outer: Panel }) {
  const X = [50, 100, 200, 300, 350], W = 100;
  return (
    <svg viewBox="0 0 400 400" className="grid" role="img" aria-label={`Outer: ${outer.title}. Inner: ${inner.title}`}>
      {CELL.map(([r, c], sign) => (
        <g key={sign}>
          <rect x={c * W} y={r * W} width={W} height={W} className="box shaded" />
          {flow(outer.boxes[sign] ?? [], c === 1 || c === 2 ? 110 : 52).map((l, i) => (
            <text key={i} x={c * W + (c === 3 ? 44 : -4) + l.x} y={r * W + (r === 3 ? 34 : -8) + l.y} className="body-label small">{retroMark(l.t)}</text>
          ))}
        </g>
      ))}
      {CELL.map(([r, c], sign) => (
        <g key={sign}>
          <rect x={X[c]} y={X[r]} width={X[c + 1] - X[c]} height={X[r + 1] - X[r]} className="box inner" />
          {flow(inner.boxes[sign] ?? [], c === 1 || c === 2 ? 110 : 60).map((l, i) => (
            <text key={i} x={X[c] + l.x - 5} y={X[r] + l.y - 6} className="body-label small">{retroMark(l.t)}</text>
          ))}
        </g>
      ))}
      <text x={200} y={160} textAnchor="middle" className="grid-title small">Outer: {outer.title}</text>
      <text x={200} y={250} textAnchor="middle" className="grid-title small">Inner: {inner.title}</text>
    </svg>
  );
}
