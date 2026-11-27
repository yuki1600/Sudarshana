import { useEffect, useLayoutEffect, useRef, useState, type ReactNode } from "react";
import { useMenu } from "./Menu";
import { tr, useLanguage } from "./language";

const NONE: ReadonlySet<string> = new Set();

/** Text with its ordinals' endings raised: "12th house" → 12<sup>th</sup> house. Anything not a string passes through as it is.
 *  Each ordinal is one untranslated unit, so a page translator can't move the raised ending onto a neighbouring word
 *  ("9th, 12th" came out as 9th, <sup>12th</sup>; "placed in the 4th" as placed in <sup>the</sup> 4th). */
export function supOrd(v: ReactNode): ReactNode {
  if (typeof v !== "string" || !/\d(st|nd|rd|th)\b/.test(v)) return v;
  const p = v.split(/(\d+)(st|nd|rd|th)\b/), out: ReactNode[] = [];   // text, number, ending, text, number, ending, ..., text
  for (let i = 0; i < p.length; i += 3) {
    if (p[i]) out.push(p[i]);
    if (i + 1 < p.length) out.push(<span key={i} className="ord" translate="no">{p[i + 1]}<sup>{p[i + 2]}</sup></span>);
  }
  return out;
}

/** Retrograde, as the charts mark it: an R straight after the graha (SaR), in red. */
/** The retrograde mark, "(R)" everywhere (charts: names.ts retroMark). */
export const Retro = () => <span className="retro-r" data-tip="Retrograde">(R)</span>;

/** A dignity as the Grahas tab marks it, the same everywhere: ↑ exalted, ↓ debilitated, "Moola" outlined, "Own" on --here
 *  (purple in Starlight). Vargottama, where it is shown, a plain tag beside them. */
export const Dignity = ({ d, vg }: { d?: string | null; vg?: boolean }) => (
  <>
    {d === "Exalted" && <span className="kp-dig up" title="Exalted">↑</span>}
    {d === "Debilitated" && <span className="kp-dig down" title="Debilitated">↓</span>}
    {d === "Moolatrikona" && <span className="kp-tag moola dig-tag" title="Moolatrikona">Moola</span>}
    {(d === "Own Sign" || d === "Own") && <span className="kp-tag own dig-tag" title="Own sign">Own</span>}
    {vg && <span className="kp-tag dig-tag" title="Vargottama: the same sign in the D-9">Vg</span>}
  </>
);

/** A partner's age in whole years today (``b`` their birth). setUTCFullYear, not Date.UTC, so a year below 100 is not read as 19xx. */
export function ageNow(b: { year: number; month: number; day: number; hour_local: number; tz_east_hours: number }): number {
  const born = new Date(0);
  born.setUTCFullYear(b.year, b.month - 1, b.day);
  return Math.floor((Date.now() - born.getTime() - (b.hour_local - b.tz_east_hours) * 3.6e6) / (365.2425 * 864e5));
}

/** "Girl  Age 27": a partner's heading with their current age beside it. */
export const WhoAge = ({ who, birth }: { who: string; birth?: Parameters<typeof ageNow>[0] | null }) => (
  <>{who}{birth && <small className="who-age">Age {ageNow(birth)}</small>}</>
);

/** The tabs of a screen, shown at the top of the page content. */
export function SubTabs<T extends string>({ tabs, value, onChange, label }: {
  tabs: { id: T; name: string }[]; value: T; onChange: (id: T) => void; label: string;
}) {
  return (
    <div className="seg" role="tablist" aria-label={label}>
      {tabs.map((t) => (
        <button key={t.id} role="tab" aria-selected={value === t.id} aria-label={t.name} title={t.name} onClick={() => onChange(t.id)}>
          {t.name}
        </button>
      ))}
    </div>
  );
}

/** The tabs on one row: as many as fit, then the pinned ones, the rest under "More", which takes the open tab's name when that tab is one of them.
 *  ``more``: views that are always under "More", after the tabs that did not fit. Which tabs fit depends on the row's width alone, never on
 *  the tab open: "More" keeps room as wide as the row's widest tab, so picking a tab never moves another on or off the row. The name it
 *  takes (a ``more`` view's may be longer) runs on to the row's end, "…" only where the row ends. */
export function OneRowTabs<T extends string>({ tabs: TABS, value, onChange, label, pinned: PINNED = NONE, more: MORE = [] }: {
  tabs: readonly { id: T; name: string }[]; value: T; onChange: (id: T) => void; label: string; pinned?: ReadonlySet<string>; more?: readonly { id: T; name: string }[];
}) {
  const row = useRef<HTMLDivElement>(null), ghost = useRef<HTMLDivElement>(null);
  const [fit, setFit] = useState<number | null>(null);     // how many of the unpinned tabs show; null: every tab, in order
  const { open, node } = useMenu();
  // the names in Settings > Language's language here, not by the page's translator: they are measured as soon as they are drawn
  const language = useLanguage();
  const ALL = [...TABS, ...MORE].map((t) => ({ ...t, name: tr(t.name) }));
  const names = language + "\n" + ALL.map((t) => t.name).join("\n");     // measure again when the tabs or their language change, not on every new array of the same tabs
  const named = ALL.slice(0, TABS.length), others = named.filter((t) => !PINNED.has(t.id)), pins = named.filter((t) => PINNED.has(t.id));
  useLayoutEffect(() => {
    const measure = () => {
      const room = row.current!.clientWidth - 8;     // 8: the open tab's bold is a little wider than the ghost's
      const width: Record<string, number> = {};
      [...ghost.current!.children].forEach((c, i) => { width[ALL[i].id] = (c as HTMLElement).offsetWidth + 2; });     // 2: the row's gap
      if (!MORE.length && named.reduce((a, t) => a + width[t.id], 0) <= room) return setFit(null);
      const keepW = Math.max(64, ...others.map((t) => width[t.id])) + 18;     // "More ▾", or the open tab's name and ▾: the widest tab that could go under it
      let left = room - pins.reduce((a, t) => a + width[t.id], 0) - keepW;
      let n = 0;
      while (n < others.length && width[others[n].id] <= left) left -= width[others[n++].id];
      setFit(n);
    };
    const ro = new ResizeObserver(measure);
    ro.observe(row.current!);
    measure();
    return () => ro.disconnect();
  }, [names]); // eslint-disable-line react-hooks/exhaustive-deps
  const shown = fit === null ? named : named.filter((t) => PINNED.has(t.id) || others.slice(0, fit).includes(t));     // in their own order: pinned ones keep their place
  const over = fit === null ? [] : others.slice(fit), rest = [...over, ...ALL.slice(TABS.length)];
  const hidden = rest.find((t) => t.id === value);
  const item = (t: { id: T; name: string }) => ({ label: t.name, checked: t.id === value, onClick: () => onChange(t.id) });
  return (
    <div ref={row} className="seg one-row-tabs" role="tablist" aria-label={label}>
      {shown.map((t) => <button key={t.id} role="tab" aria-selected={value === t.id} onClick={() => onChange(t.id)}>{t.name}</button>)}
      {rest.length > 0 && (
        <button role="tab" className="one-row-more" aria-selected={!!hidden} aria-haspopup="menu"
          title={hidden?.name ?? (over.map((t) => t.name).join(", ") || undefined)}
          onClick={(e) => { const r = e.currentTarget.getBoundingClientRect(); open({ clientX: r.left, clientY: r.bottom }, [...over.map(item), "-", ...ALL.slice(TABS.length).map(item)], "More tabs"); }}>
          <span className="one-row-name">{hidden ? hidden.name : tr("More")}</span> ▾
        </button>
      )}
      <div ref={ghost} className="seg one-row-ghost" aria-hidden>{ALL.map((t) => <button key={t.id} tabIndex={-1}>{t.name}</button>)}</div>
      {node}
    </div>
  );
}

/** Copy to clipboard, as every list had: hidden across the app for now (the right-click menus still copy). Bring it back by restoring the button. */
export function CopyButton(_: { text: string }) {
  return null;
}

/** A table as aligned plain text. */
export function tableText(columns: string[], rows: string[][]): string {
  const width = columns.map((c, i) => Math.max(c.length, ...rows.map((r) => (r[i] ?? "").length)));
  const line = (cells: string[]) => cells.map((c, i) => c.padEnd(width[i])).join(" ").trimEnd();
  return [line(columns), "", ...rows.map(line)].join("\n");
}

/** Shows what a query is doing until its data is there. */
export function Loaded<T>({ q, children }: { q: { data?: T; isError: boolean; error: Error | null }; children: (d: T) => ReactNode }) {
  if (q.isError) return <p role="alert" className="error banner">{q.error?.message}</p>;
  if (q.data === undefined) return <p className="empty small">Calculating…</p>;
  return <>{children(q.data)}</>;
}

const CONTROL = "button, a, [role=button], [role=tab], label, summary";

/** The element whose hover label shows and its text: a data-tip, or an icon-only control's aria-label. */
export function tipOf(target: Element): { el: HTMLElement; text: string } | null {
  const own = target.closest<HTMLElement>("[data-tip]");
  if (own) return own.dataset.tip ? { el: own, text: own.dataset.tip } : null;
  const c = target.closest<HTMLElement>(CONTROL);
  if (!c || !c.querySelector("svg") || c.textContent?.trim()) return null;   // only icons: worded controls say what they are
  const text = c.getAttribute("aria-label");
  return text ? { el: c, text } : null;
}

/** An instant hover label on every icon (the browser's own title tooltip waits about a second), as the top bar's. */
export function IconTips() {
  const [tip, setTip] = useState<{ text: string; x: number; y: number; above: boolean; side?: boolean } | null>(null);
  useEffect(() => {
    const over = (e: PointerEvent) => {
      if (!(e.target instanceof Element)) return setTip(null);
      // a control's title (often fuller than its aria-label) becomes its data-tip, so the native tooltip doesn't come up a second later too
      const ctl = e.target.closest<HTMLElement>(CONTROL);
      if (ctl?.title) { ctl.dataset.tip = ctl.title; if (!ctl.getAttribute("aria-label")) ctl.setAttribute("aria-label", ctl.title); ctl.removeAttribute("title"); }
      const t = tipOf(e.target);
      if (!t) return setTip(null);
      const { el: c, text } = t;
      const r = c.getBoundingClientRect(), above = r.bottom + 32 > innerHeight;
      // in a menu: beside the whole menu, on its left, so it covers neither the menu nor a sub-menu open on its right
      const menu = c.closest(".floating-menu")?.getBoundingClientRect();
      if (menu && menu.left > 120) return setTip({ text, x: menu.left - 6, y: r.top + r.height / 2, above: false, side: true });
      setTip({ text, x: r.left + r.width / 2, y: above ? r.top - 6 : r.bottom + 6, above });
    };
    const hide = () => setTip(null);
    document.addEventListener("pointerover", over);
    document.addEventListener("scroll", hide, true);
    document.addEventListener("pointerdown", hide);
    document.documentElement.addEventListener("pointerleave", hide);
    return () => { document.removeEventListener("pointerover", over); document.removeEventListener("scroll", hide, true); document.removeEventListener("pointerdown", hide); document.documentElement.removeEventListener("pointerleave", hide); };
  }, []);
  const ref = useRef<HTMLSpanElement>(null);
  useLayoutEffect(() => {     // centred under its control, but moved in to stay whole inside the window
    const el = ref.current;
    if (!el || !tip || tip.side) return;
    const half = el.offsetWidth / 2;
    el.style.left = `${Math.min(Math.max(tip.x, half + 4), innerWidth - half - 4)}px`;
  }, [tip]);
  return tip && <span ref={ref} className={`bar-tip${tip.above ? " above" : ""}${tip.side ? " side" : ""}`} role="tooltip" style={{ left: tip.x, top: tip.y }}>{tip.text}</span>;
}
