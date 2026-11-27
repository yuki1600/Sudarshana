import { useEffect, useRef, useState, type MouseEvent, type ReactNode } from "react";
import { currentSettings, type ChartSpec } from "./api";

const DIVISIONS = [1, 9, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 16, 20, 24, 27, 30, 40, 45, 60, 81, 108, 144];
const REFS = ["Lagna", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"];
const STARTS = ["The base", "The 1st/7th from base (if sign is odd/even)", "The 1st/9th from base (if sign is odd/even)", "The 1st/5th from base (if sign is odd/even)", "The 1st/11th from base (if sign is odd/even)", "The 1st/3rd from base (if sign is odd/even)",
  "The 1st/5th/9th from base (if sign is movable/fixed/dual)", "The 1st/9th/5th from base (if sign is movable/fixed/dual)", "The 1st/4th/7th/10th from base (by element)", "The 1st/10th/7th/4th from base (by element)"];

/** Close a modal dialog on a click outside its box (the backdrop). Its own padding counts as inside. */
export const backdropClose = (e: MouseEvent<HTMLDialogElement>) => {
  const r = e.currentTarget.getBoundingClientRect();
  if (e.target === e.currentTarget && (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom)) e.currentTarget.close();
};

/** A small modal form opened from a menu; it closes itself when its window does. */
export function Modal({ title, onClose, children, wide }: { title: string; onClose: () => void; children: ReactNode; wide?: boolean }) {
  const ref = useRef<HTMLDialogElement>(null);
  useEffect(() => { if (!ref.current?.open) ref.current?.showModal(); }, []);
  return (
    <dialog ref={ref} className={wide ? "dialog wide" : "dialog"} onClose={onClose} onClick={backdropClose} aria-labelledby="modal-title">
      <h2 id="modal-title">{title}</h2>
      {children}
    </dialog>
  );
}

export function FormButtons({ ok = "OK" }: { ok?: string }) {
  return <menu><button type="submit" className="primary">{ok}</button></menu>;
}

const division = (v: number, set: (n: number) => void) => (
  <select value={v} onChange={(e) => set(Number(e.target.value))}>{DIVISIONS.map((d) => <option key={d} value={d}>{d === 1 ? "Rasi (D-1)" : `D-${d}`}</option>)}</select>
);

/** The custom division dialog. */
export function CustomDialog({ spec, onOk, onClose }: { spec: ChartSpec; onOk: (s: ChartSpec) => void; onClose: () => void }) {
  const [f, setF] = useState({ d: spec.kind === "custom" ? spec.d ?? 7 : 7, cyclic: !!spec.cyclic, from_sign: !!spec.from_sign, reverse_even: !!spec.reverse_even, start: spec.start ?? 0 });
  return (
    <Modal title="Custom Divisional Chart for Research" onClose={onClose}>
      <form method="dialog" onSubmit={(e) => { e.preventDefault(); onOk({ kind: "custom", ...f }); }}>
        <label>Divide each sign into this number of equal parts<input type="number" min={1} max={3600} value={f.d} onChange={(e) => setF({ ...f, d: Number(e.target.value) })} required /></label>
        <label className="check"><input type="checkbox" checked={f.cyclic} onChange={(e) => setF({ ...f, cyclic: e.target.checked })} /> This is a cyclical (parivritti) chart: keep going around the zodiac</label>
        <label>The base for the mapping of N divisions in a sign (non-cyclical charts)
          <select value={String(f.from_sign)} disabled={f.cyclic} onChange={(e) => setF({ ...f, from_sign: e.target.value === "true" })}><option value="false">Aries always</option><option value="true">The sign in question</option></select>
        </label>
        <label>Mapping of divisions starts from
          <select value={f.start} disabled={f.cyclic} onChange={(e) => setF({ ...f, start: Number(e.target.value) })}>{STARTS.map((n, i) => <option key={n} value={i}>{n}</option>)}</select>
        </label>
        <label className="check"><input type="checkbox" checked={f.reverse_even} disabled={f.cyclic} onChange={(e) => setF({ ...f, reverse_even: e.target.checked })} /> Count N divisions from the end of the sign if the sign is even</label>
        <FormButtons />
      </form>
    </Modal>
  );
}

/** The sub-division (D-m of D-n) dialog. */
export function SubDialog({ spec, onOk, onClose }: { spec: ChartSpec; onOk: (s: ChartSpec) => void; onClose: () => void }) {
  const [m, setM] = useState(spec.m ?? 9);
  const [n, setN] = useState(spec.n ?? 1);
  return (
    <Modal title="Choose sub-divisional chart D-mxn (i.e. D-n of D-m)" onClose={onClose}>
      <form method="dialog" onSubmit={(e) => { e.preventDefault(); onOk({ kind: "sub", m, n }); }}>
        <label>Take this D-m as the base divisional chart{division(m, setM)}</label>
        <label>Take the above as rasi chart and find D-n in it{division(n, setN)}</label>
        <FormButtons />
      </form>
    </Modal>
  );
}

/** The division and house reference dialog. */
export function DivisionDialog({ spec, onOk, onClose }: { spec: ChartSpec; onOk: (s: ChartSpec, ref: number, reversed: boolean, middle: boolean) => void; onClose: () => void }) {
  const s = currentSettings();
  const [ref, setRef] = useState(Number(s.bhava_ref ?? 2));
  const [middle, setMiddle] = useState(s.house_cusp_in_middle !== false);
  const [rev, setRev] = useState(s.bhava_nodes_reversed === true);
  const [d, setD] = useState(spec.kind === "bhava" ? spec.d ?? 1 : 1);
  return (
    <Modal title="Choose the Reference for Bhava/Chalit Chakra" onClose={onClose}>
      <form method="dialog" onSubmit={(e) => { e.preventDefault(); onOk({ kind: "bhava", d }, ref, rev, middle); }}>
        <p className="muted">Bhava systems such as Sripathi are used only if the lagna is the reference in D-1. Otherwise the bhavas are equal from the reference.</p>
        <label>The reference<select value={ref} onChange={(e) => setRef(Number(e.target.value))}>{REFS.map((n, i) => <option key={n} value={i}>{n}</option>)}</select></label>
        <label className="check"><input type="checkbox" checked={middle} onChange={(e) => setMiddle(e.target.checked)} /> Lagna is in the middle of the first bhava (unchecked: at its beginning)</label>
        <label className="check"><input type="checkbox" checked={rev} onChange={(e) => setRev(e.target.checked)} /> Bhavas from Rahu and Ketu are reckoned anti-zodiacally</label>
        <label>The divisional chart it is based on{division(d, setD)}</label>
        <FormButtons />
      </form>
    </Modal>
  );
}
