/** The Starlight bar's icons in their two halves, as the ids TopBar gives them. */
export interface BarOrder { left: string[]; right: string[] }

/** The saved order kept to the ids the bar has now; one it lacks (a page Settings brings back) goes in after its neighbour in the default. */
export function reconcile(saved: BarOrder | null | undefined, def: BarOrder): BarOrder {
  if (!saved) return def;
  const all = [...def.left, ...def.right];
  const out = { left: saved.left.filter((id) => all.includes(id)), right: saved.right.filter((id) => all.includes(id) && !saved.left.includes(id)) };
  for (const side of ["left", "right"] as const) def[side].forEach((id, i) => {
    if (out.left.includes(id) || out.right.includes(id)) return;
    const prev = def[side].slice(0, i).reverse().find((p) => out[side].includes(p));
    out[side].splice(prev ? out[side].indexOf(prev) + 1 : 0, 0, id);
  });
  return out;
}

/** id taken out of wherever it is and put on side, before the id `before` (null: at the side's end). */
export function moveTo(o: BarOrder, id: string, side: keyof BarOrder, before: string | null): BarOrder {
  const out = { left: o.left.filter((x) => x !== id), right: o.right.filter((x) => x !== id) };
  const i = before ? out[side].indexOf(before) : -1;
  out[side].splice(i < 0 ? out[side].length : i, 0, id);
  return out;
}
