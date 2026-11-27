import { bodySizes, fitted, fittedEach, flow, type BodySizes, type Box } from "./chartGeometry";
import { SIGNS } from "./format";
import { useShape } from "./hooks";
import { BigTitle, BodyText, sizeVars, SouthGrid, titleLines, titleShift, type Decoration } from "./SouthGrid";
import { FONT_FACTORS, useChart } from "./store";
import { signName } from "./names";

interface Props extends Decoration { title: string; cell: (sign: number) => string[]; lagnaSign?: number; shaded?: ReadonlySet<number> }
const W = 400;

// North Indian boxes: the bounding rectangle's cell of each house, in quarters of the square, and its shape
const N_COL = [1, 0, 0, 0, 0, 0, 1, 2, 2, 2, 2, 2], N_ROW = [0, 0, 0, 1, 2, 2, 2, 2, 2, 1, 0, 0], N_TYPE = [0, 1, 2, 0, 2, 3, 0, 3, 4, 0, 4, 1];

function northBox(b: number, k: number) {
  const l = N_COL[b] * 100, t = N_ROW[b] * 100 * k, r = l + 200, bo = t + 200 * k, mx = l + 100, my = t + 100 * k;
  switch (N_TYPE[b]) {
    case 0: return { poly: `${mx},${t} ${r},${my} ${mx},${bo} ${l},${my}`, x: mx - 40, y: my - 20, w: 86, bottom: bo };
    case 1: return { poly: `${l},${t} ${r},${t} ${mx},${my}`, x: mx - 40, y: t + 24, w: 86, bottom: my };
    case 2: return { poly: `${l},${t} ${l},${bo} ${mx},${my}`, x: l + 8, y: my - 20, w: 60, bottom: bo };
    case 3: return { poly: `${l},${bo} ${r},${bo} ${mx},${my}`, x: mx - 40, y: my + 48 * k, w: 86, bottom: bo };
    default: return { poly: `${r},${t} ${r},${bo} ${mx},${my}`, x: r - 64, y: my - 20, w: 60, bottom: bo };
  }
}

function Centre({ title, d, k, z }: { title: string; d: Decoration; k: number; z: BodySizes }) {
  const [big, small] = titleLines(title);
  const mid = W * k / 2, shift = titleShift(big, 20);
  return (
    <>
      {d.chartName && <text x={W / 2} y={mid - z.sub - 13} textAnchor="middle" className="grid-sub corner">{d.chartName}</text>}
      <BigTitle big={big} x={W / 2} y={mid} line={20} className="grid-title corner" />
      {small && <text x={W / 2} y={mid + z.sub + 7 + shift} textAnchor="middle" className="grid-sub corner">{small}</text>}
      {d.note && <text x={W / 2} y={mid + 2 * z.sub + 12 + shift} textAnchor="middle" className="grid-sub note corner">{d.note}</text>}
    </>
  );
}

export function NorthGrid({ title, cell, lagnaSign = 0, shaded, ...d }: Props) {
  const display = useChart((s) => s.display);
  const [ref, k, px] = useShape();
  const factor = FONT_FACTORS[display.chartFont];
  const boxes: Box[] = Array.from({ length: 12 }, (_, b) => {
    const box = northBox(b, k);
    return { labels: cell((b + lagnaSign) % 12), w: box.w, h: box.bottom - (box.y - 12) - 4, deg: d.degrees, moved: d.moved, plain: d.plain };     // 4: clear of the box's bottom edge
  });
  const base = d.bare || (d.each && !display.signLabels) ? { ...bodySizes(px, factor), sign: 0 } : bodySizes(px, factor);
  const z = fitted(base, boxes, factor);
  const each = d.each ? fittedEach(base, boxes, factor, d.bare ? 1.5 : 1) : null;
  return (
    <svg ref={ref} viewBox={`0 0 ${W} ${W * k}`} className="grid" style={sizeVars(z)} role="img" aria-label={title}>
      {Array.from({ length: 12 }, (_, b) => {
        const sign = (b + lagnaSign) % 12, box = northBox(b, k);
        const flowed = flow(cell(sign), box.w, each?.[b] ?? z, d.degrees);
        return (
          <g key={b} data-sign={d.interactive ? sign : undefined} style={each ? sizeVars(each[b]) : undefined}>
            <polygon points={box.poly} className={(shaded?.has(sign) ? "box shaded" : "box") + (d.muntha === sign ? " muntha" : "") + (d.focus === sign ? " focus" : "")} />
            {!d.bare && <text x={box.x} y={box.y - 6} className="sign-name">{b + 1} {signName(sign, SIGNS[sign], display)}</text>}
            {flowed.map((l, i) => <BodyText key={i} t={l.t} x={box.x + l.x - 8} y={box.y + l.y - 12} d={d} end={l.end} />)}
          </g>
        );
      })}
      <Centre title={title} d={d} k={k} z={z} />
    </svg>
  );
}

// East Indian cells: Aries top centre, counter-clockwise; the corners hold two rasis split by a diagonal
const E_COL = [1, 0, 0, 0, 0, 0, 1, 2, 2, 2, 2, 2], E_ROW = [0, 0, 0, 1, 2, 2, 2, 2, 2, 1, 0, 0], E_TYPE = [0, 1, 2, 0, 3, 4, 0, 2, 1, 0, 4, 3];
const C = W / 3;

function eastBox(s: number, k: number) {
  const l = E_COL[s] * C, t = E_ROW[s] * C * k, r = l + C, b = t + C * k;
  switch (E_TYPE[s]) {
    case 0: return { poly: `${l},${t} ${r},${t} ${r},${b} ${l},${b}`, x: l + 10, y: t + 8, w: 110, bottom: b };
    case 1: return { poly: `${l},${t} ${r},${t} ${r},${b}`, x: l + 52, y: t, w: 76, bottom: b };
    case 2: return { poly: `${l},${t} ${r},${b} ${l},${b}`, x: l + 2, y: t + 62 * k, w: 76, bottom: b };
    case 3: return { poly: `${l},${t} ${r},${t} ${l},${b}`, x: l + 2, y: t, w: 76, bottom: b };
    default: return { poly: `${r},${t} ${r},${b} ${l},${b}`, x: l + 72, y: t + 62 * k, w: 56, bottom: b };
  }
}

export function EastGrid({ title, cell, lagnaSign, shaded, ...d }: Props) {
  const display = useChart((s) => s.display);
  const [ref, k, px] = useShape();
  const factor = FONT_FACTORS[display.chartFont];
  const boxes: Box[] = SIGNS.map((_, s) => {
    const box = eastBox(s, k);
    return { labels: cell(s), w: box.w, h: box.bottom - (box.y + 8), deg: d.degrees, moved: d.moved, plain: d.plain };
  });
  const base = d.bare || (d.each && !display.signLabels) ? { ...bodySizes(px, factor), sign: 0 } : bodySizes(px, factor);
  const z = fitted(base, boxes, factor);
  const each = d.each ? fittedEach(base, boxes, factor, d.bare ? 1.5 : 1) : null;
  return (
    <svg ref={ref} viewBox={`0 0 ${W} ${W * k}`} className="grid" style={sizeVars(z)} role="img" aria-label={title}>
      {SIGNS.map((name, s) => {
        const box = eastBox(s, k);
        const flowed = flow(cell(s), box.w, each?.[s] ?? z, d.degrees);
        return (
          <g key={s} data-sign={d.interactive ? s : undefined} style={each ? sizeVars(each[s]) : undefined}>
            <polygon points={box.poly} className={(s === lagnaSign || shaded?.has(s) ? "box shaded" : "box") + (d.muntha === s ? " muntha" : "") + (d.focus === s ? " focus" : "")} />
            {!d.bare && <text x={box.x + 6} y={box.y + 8 + (each?.[s] ?? z).sign} className="sign-name">{signName(s, name, display)}{s === lagnaSign ? " (Lagna)" : ""}</text>}
            {flowed.map((l, i) => <BodyText key={i} t={l.t} x={box.x + l.x - 2} y={box.y + l.y + 8} d={d} end={l.end} />)}
          </g>
        );
      })}
      <Centre title={title} d={d} k={k} z={z} />
    </svg>
  );
}

/** A chart in the style chosen in Preferences; ``second`` panels take the second style when two are in use. */
export function ChartGrid({ second, ...p }: Props & { second?: boolean }) {
  const main = useChart((s) => s.chartStyle);
  const display = useChart((s) => s.display);
  const style = second && display.twoStyles ? display.style2 : main;
  return style === "north" ? <NorthGrid {...p} /> : style === "east" ? <EastGrid {...p} /> : <SouthGrid {...p} />;
}
