import { Fragment, useEffect, useLayoutEffect, useRef, useState } from "react";
import { flushSync } from "react-dom";
import { moveTo, reconcile, type BarOrder } from "./barOrder";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api, saveSettings, type Birth, type ChartFormat, type Settings } from "./api";
import { formatMoment } from "./format";
import { castKind, ChartName, Icon, type IconName } from "./Icons";
import { useKept, useSettings } from "./hooks";
import { useMenu } from "./Menu";
import { FormButtons, Modal } from "./ChartDialogs";
import { Control } from "./Settings";
import { inCloud, useChart } from "./store";

export const TABS = ["Home", "Dasas", "Strengths", "Transits", "Timeline", "Predictions", "Tajaka", "Tithi Pravesha", "Muhurta", "Longevity", "Chakras", "Matching", "Mundane", "Astrocartography", "Traditions", "Research", "Finance", "Remedies"] as const;   // Calculations hidden for now: add it back here to show its icon
/** The pages on the bar: Tajaka and Tithi Pravesha drop out when Settings keeps them inside Transits. */
const NAME: Partial<Record<string, string>> = { Timeline: "Calendar", Strengths: "Balas" };   // shown names that differ from the tab's stored id
/** The pages: Tajaka and Tithi Pravesha not when Settings keeps them as Transits' sub tabs; in Starlight (``star``) no Chakras, whose
 *  chakras are Transits' Chakras view and Avakahada a Home view. */
export const pageTabs = (together: boolean, star = false) =>
  TABS.filter((t) => !(together && (t === "Tajaka" || t === "Tithi Pravesha")) && !(star && t === "Chakras") && !(!star && t === "Traditions"));   // Traditions: Starlight's own
export type Theme = "auto" | "light" | "dark";

// The seven units of the step combos: seconds, or calendar months
const STEPS: [string, number, number][] = [["Sec", 1, 0], ["15Sec", 15, 0], ["Min", 60, 0], ["Hour", 3600, 0], ["Day", 86400, 0], ["Month", 0, 1], ["Year", 0, 12]];

/** Scrub the time: every view recalculates. The birth-time group moves the natal chart, the transit-time group a transit chart
 *  (``onStep`` then hears the transit's new moment, so a form showing it follows), a ``cast`` one that chart (Jamakkol's), handing it the new moment. */
export function Stepper({ transit, onStep, cast }: { transit?: boolean; onStep?: (b: Birth) => void; cast?: { name: string; birth: Birth; move: (b: Birth) => void } }) {
  const { natal, birth, mode, changeBirth, enterMode } = useChart();
  const [unit, setUnit] = useState(transit || cast ? 4 : 2);  // TimeAdjBase, TranTimeAdjBase
  const go = async (dir: number) => {
    const [, seconds, months] = STEPS[unit];
    if (cast) {
      cast.move((await api.step(cast.birth, dir * seconds, dir * months)).birth);
    } else if (transit) {
      const r = await api.step(birth!, dir * seconds, dir * months);
      enterMode(r.birth, { ...mode!, recast: undefined, lines: [["At", formatMoment(r.start)]] });     // a moment of its own now: not cast again
      onStep?.(r.birth);
    } else {
      const { birth: b } = await api.step(natal!, dir * seconds, dir * months);
      changeBirth(b);
    }
  };
  // the natal chart's plain; a transit's or a cast chart's each step its name: "Transit-Day", "Jamakkol-Day"
  const kind = cast?.name ?? (transit ? "Transit" : undefined);
  const label = kind ? `${kind.toLowerCase()} ` : "birth ";
  return (
    <span className="stepper" data-bar-id="stepper" role="group" aria-label={`${kind ?? "Birth"} time`}>
      <button className="icon-btn" onClick={() => go(-1)} disabled={!natal} aria-label={`Move ${label}time backward`} data-tip={`Move ${label}time back`}><Icon name="prev" /></button>
      <select aria-label={`${kind ?? "Birth"} time step`} data-tip="Step size" value={unit} onChange={(e) => setUnit(Number(e.target.value))}>{STEPS.map(([n], i) => <option key={n} value={i}>{kind ? `${kind}-${n}` : n}</option>)}</select>
      <button className="icon-btn" onClick={() => go(1)} disabled={!natal} aria-label={`Move ${label}time forward`} data-tip={`Move ${label}time forward`}><Icon name="next" /></button>
    </span>
  );
}

const STAR_KEYS = ["custom_star", "custom_star_longitude", "custom_star_fixed_plane"];
const name = (label: string) => label.replace(/^Custom ayanamsa: /, "").replace(/^./, (c) => c.toUpperCase());
// well-known reference stars (Swiss Ephemeris codes) with the sidereal longitude each is usually given: its nakshatra's middle, or the paksha's convention
const STARS: [string, string, number][] = [
  [",alVir", "Spica (Chitra)", 180], [",deCnc", "Asellus Australis, δ Cancri (Pushya)", 106], [",alTau", "Aldebaran (Rohini)", 46.6667],
  [",zePsc", "ζ Piscium (Revati)", 359.8333], [",alLeo", "Regulus (Magha)", 126.6667], [",alSco", "Antares (Jyeshtha)", 233.3333],
  [",beGem", "Pollux (Punarvasu)", 86.6667], [",alBoo", "Arcturus (Swati)", 193.3333]];

/** A: pick the ayanamsa. It is the same saved option as Settings > Model and ayanamsa, so each shows the other's change. */
function AyanamsaButton() {
  const settings = useSettings();
  const client = useQueryClient();
  const { open, node } = useMenu();
  const [star, setStar] = useKept<Settings | null>("ayanamsa.star", null);     // the fixed-star form's values while it is open
  const schema = useQuery({ queryKey: ["settingsSchema"], queryFn: api.settingsSchema, staleTime: Infinity });
  const options = schema.data?.flatMap((g) => g.options) ?? [];
  const choices = options.find((o) => o.key === "ayanamsa")?.choices ?? [];
  const starOptions = options.filter((o) => STAR_KEYS.includes(o.key));
  const current = choices.find((c) => c.value === settings.ayanamsa)?.label ?? String(settings.ayanamsa);
  const apply = (s: Settings) => { saveSettings({ ...settings, ...s }); client.invalidateQueries(); };
  // the fixed-star ayanamsa needs its star first: a form, filled with what Settings has
  const item = (c: (typeof choices)[number]) => ({ label: c.label + (c.value === "CUSTOM_STAR" ? "..." : ""), checked: c.value === settings.ayanamsa,
    onClick: () => c.value === "CUSTOM_STAR" ? setStar(Object.fromEntries(starOptions.map((o) => [o.key, settings[o.key] ?? o.default]))) : apply({ ayanamsa: c.value }) });
  const show = (e: React.MouseEvent<HTMLElement>) => {
    const r = e.currentTarget.getBoundingClientRect();
    // one list in the settings' order, the fixed-star one (it asks for its star) last
    open({ clientX: r.left, clientY: r.bottom }, [...choices.filter((c) => c.value !== "CUSTOM_STAR"), ...choices.filter((c) => c.value === "CUSTOM_STAR")].map(item), "Ayanamsa");
  };
  return (
    <>
      <button className="icon-btn" data-bar-id="ayanamsa" aria-haspopup="menu" aria-label={`Ayanamsa: ${current}`} data-tip={`Ayanamsa: ${current}`} disabled={!choices.length} onClick={show}><Icon name="ayanamsa" /></button>
      {node}
      {star && (
        <Modal title="Fixed star based ayanamsa" onClose={() => setStar(null)}>
          <form method="dialog" onSubmit={(e) => { e.preventDefault(); if (!String(star.custom_star).trim()) return;     /* "Another star" with no code typed yet */
            apply({ ayanamsa: "CUSTOM_STAR", ...star }); setStar(null); }}>
            {starOptions.map((o) => (
              <label key={o.key} className={o.kind === "bool" ? "check" : undefined}>{o.kind !== "bool" && name(o.label)}
                {o.key === "custom_star" ? (
                  <select value={STARS.some(([c]) => c === star.custom_star) ? String(star.custom_star) : ""}
                    onChange={(e) => { const hit = STARS.find(([c]) => c === e.target.value); setStar(hit ? { ...star, custom_star: hit[0], custom_star_longitude: hit[2] } : { ...star, custom_star: "" }); }}>
                    {STARS.map(([c, n]) => <option key={c} value={c}>{n}</option>)}
                    <option value="">Another star (type its code)</option>
                  </select>
                ) : <Control o={o} value={star[o.key]} set={(v) => setStar({ ...star, [o.key]: v })} />}{o.kind === "bool" && ` ${name(o.label)}`}
                {o.key === "custom_star" && !STARS.some(([c]) => c === star.custom_star) && (
                  <><Control o={o} value={star[o.key]} set={(v) => setStar({ ...star, [o.key]: v })} />{o.help && <small className="muted">{o.help}</small>}</>
                )}
              </label>
            ))}
            <FormButtons />
          </form>
        </Modal>
      )}
    </>
  );
}

function IconButton({ id, icon, label, onClick, disabled, pressed, children }: { id?: string; icon: IconName; label: string; onClick: (e: React.MouseEvent<HTMLButtonElement>) => void; disabled?: boolean; pressed?: boolean; children?: React.ReactNode }) {
  return <button className="icon-btn" data-bar-id={id} onClick={onClick} disabled={disabled} aria-pressed={pressed} aria-label={label} data-tip={label}><Icon name={icon} />{children}</button>;
}

/** A page's button. The Windows layout's sit in one tablist; Starlight's move about the bar among other icons, so each marks its page with aria-current. */
function PageTab({ t, loose }: { t: (typeof TABS)[number]; loose?: boolean }) {
  const { tab, setTab } = useChart();
  return (
    <button role={loose ? undefined : "tab"} className="page-tab" data-bar-id={t} aria-selected={loose ? undefined : tab === t} aria-current={loose && tab === t ? "page" : undefined}
      aria-label={NAME[t] ?? t} data-tip={NAME[t] ?? t} onClick={() => setTab(t)}>
      <Icon name={t} /><span className="tab-label">{NAME[t] ?? t}</span>
    </button>
  );
}

/** The pages, at the left of the Windows layout's top bar. */
function PageTabs() {
  const { display } = useChart();
  return <nav className="page-tabs" role="tablist" aria-label="Pages">{pageTabs(display.transitsTogether).map((t) => <PageTab key={t} t={t} />)}</nav>;
}

const PINNED = ["chart", "stepper"];   // not icons: they keep their places and the icons move round them

/** Starlight's bar as shipped: the actions and the chart's name on the left, the pages and the account's icons on the right. */
export const barDefault = (together: boolean): BarOrder => {
  const pages = pageTabs(together, true).filter((t) => t !== "Predictions");
  return { left: ["new", "open", "save", "edit", "print", "fontDown", "fontUp", "chart", "stepper", "ayanamsa", "natal", "Predictions"], right: [...pages, "settings", "info", "signOut"] };
};
const BAR_NAMES: Record<string, string> = { new: "New chart", open: "Open chart", save: "Save chart", edit: "Edit birth data", print: "Print", fontDown: "Smaller fonts", fontUp: "Bigger fonts",
  chart: "Chart name", stepper: "Time stepper", ayanamsa: "Ayanamsa", natal: "Natal chart", Predictions: "Predictions", settings: "Settings", info: "About and credits", signOut: "Sign out" };
/** A bar piece's name in its menus and in Settings' list. */
export const barLabel = (id: string) => BAR_NAMES[id] ?? NAME[id] ?? id;
/** The pieces that can be hidden: all but the chart's name, which the left half is built round. */
export const canHide = (id: string) => id !== "chart";

/** Press and hold a Starlight bar icon: the icons jiggle, and each can be dragged along its half, or into the other one if that half still has
 * the room; a click anywhere off the bar (or Escape) ends it. */
function useBarDrag(order: BarOrder, save: (o: BarOrder) => void) {
  const header = useRef<HTMLElement>(null);
  const press = useRef<{ timer: number; x: number; y: number } | null>(null);
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState<BarOrder | null>(null);
  const [drag, setDrag] = useState<{ id: string; full: boolean } | null>(null);
  const shown = draft ?? order;
  // how far the halves spill: the left past its 50%, the right past the bar's end
  const spill = () => {
    const h = header.current!, cs = getComputedStyle(h);
    const half = (h.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight)) / 2;
    return Math.max(0, h.querySelector<HTMLElement>(".bar-left")!.getBoundingClientRect().width - half) + Math.max(0, h.scrollWidth - h.clientWidth);
  };
  const cancel = () => { if (press.current) clearTimeout(press.current.timer); press.current = null; };
  const onPointerDown = (e: React.PointerEvent<HTMLElement>) => {
    const id = (e.target as Element).closest<HTMLElement>("[data-bar-id]")?.dataset.barId;
    if (!id || PINNED.includes(id) || e.button !== 0) return;
    const bar = e.currentTarget, pointer = e.pointerId;
    const lift = () => { bar.setPointerCapture(pointer); setEditing(true); setDraft(order); setDrag({ id, full: false }); };
    if (editing) { e.preventDefault(); lift(); return; }      // already jiggling: a press picks the icon straight up
    press.current = { x: e.clientX, y: e.clientY, timer: window.setTimeout(lift, 450) };
  };
  const onPointerMove = (e: React.PointerEvent<HTMLElement>) => {
    if (!drag) { const p = press.current; if (p && Math.hypot(e.clientX - p.x, e.clientY - p.y) > 6) cancel(); return; }
    const h = header.current!;
    const side = e.clientX < h.querySelector(".bar-left")!.getBoundingClientRect().right ? "left" : "right";
    const before = [...h.querySelectorAll<HTMLElement>(`.bar-${side} [data-bar-id]`)].find((el) => {
      const r = el.getBoundingClientRect();
      return el.dataset.barId !== drag.id && e.clientX < r.left + r.width / 2;
    })?.dataset.barId ?? null;
    const next = moveTo(shown, drag.id, side, before);
    if (next[side].join() === shown[side].join()) return;
    if (shown[side].includes(drag.id)) { setDraft(next); setDrag({ ...drag, full: false }); return; }
    // into the other half: try it, and put it back before the paint if either half now runs out of room
    const was = spill();
    flushSync(() => setDraft(next));
    const full = spill() > was + 0.5;
    if (full) flushSync(() => setDraft(shown));
    setDrag({ ...drag, full });
  };
  const onPointerUp = () => {
    cancel();
    if (!drag) return;
    save(shown); setDraft(null); setDrag(null);
  };
  // while jiggling, a click on the bar moves nothing and opens nothing; one anywhere else (or Escape) ends it, and does only that
  useEffect(() => {
    if (!editing) return;
    const done = (e: Event) => {
      if (e instanceof KeyboardEvent ? e.key !== "Escape" : header.current?.contains(e.target as Node)) return;
      setEditing(false);
      if (e.type === "pointerdown") window.addEventListener("click", (c) => { c.stopPropagation(); c.preventDefault(); }, { capture: true, once: true });
    };
    window.addEventListener("pointerdown", done, true);
    window.addEventListener("keydown", done);
    return () => { window.removeEventListener("pointerdown", done, true); window.removeEventListener("keydown", done); };
  }, [editing]);
  // lift the dragged icon; its node changes when it crosses halves, so this runs on every move
  useLayoutEffect(() => {
    const el = drag && header.current?.querySelector(`[data-bar-id="${CSS.escape(drag.id)}"]`);
    el?.classList.add("dragging");
    return () => el?.classList.remove("dragging");
  }, [drag, shown]);
  return { shown, header, mode: [editing && "bar-edit", drag && "bar-drag", drag?.full && "bar-full"].filter(Boolean).join(" "),
    handlers: { onPointerDown, onPointerMove, onPointerUp, onPointerCancel: onPointerUp,
      onClickCapture: (e: React.MouseEvent) => { if (editing) { e.preventDefault(); e.stopPropagation(); } },
      onContextMenu: (e: React.MouseEvent) => { if (press.current || editing) e.preventDefault(); } } };
}

interface Props {
  onNew: () => void; onOpen: () => void; onSave: () => void; onSaveAll: (pick?: (id: string) => boolean) => void; onDownload: (format: ChartFormat) => void; onEdit: () => void; onSettings: () => void; onAbout: () => void; onPrint: () => void; onSignOut: () => void;
  theme: Theme; setTheme: (t: Theme) => void;
}

/** The one bar across the top: the pages, open chart tabs, then the actions. */
export function TopBar({ onNew, onOpen, onSave, onSaveAll, onDownload, onEdit, onSettings, onAbout, onPrint, onSignOut, theme, setTheme }: Props) {
  const { natal, birth, mode, tab, setTab, backToNatal, undo, undoAll, birthZone, display, setDisplay, charts, setCharts,
    openCharts, activeChartId, activateChart, closeChart } = useChart();
  const font = (d: number) => setDisplay({ listFont: Math.min(7, Math.max(0, display.listFont + d)), chartFont: Math.min(7, Math.max(0, display.chartFont + d)) });
  const noChart = !natal;
  const { open: showChartsMenu, node: chartsMenu, close: closeChartsMenu, update: updateChartsMenu } = useMenu();   // its own, so hovering opens and leaving closes it
  const shownChart = openCharts.find((c) => c.id === activeChartId) ?? openCharts[0];
  const many = openCharts.length > 1;
  // read from the store, not this render: a × closes that chart and the list stays open, so several can go in a row
  const chartItems = () => {
    const { openCharts: list, activeChartId: on } = useChart.getState();
    const shown = (list.find((c) => c.id === on) ?? list[0])?.id;
    const dirty = unsaved();
    return list.map((c, i) => ({ label: c.name || "(untitled)", show: c.name ? <ChartName name={c.name} /> : undefined, checked: c.id === shown, onSave: dirty.includes(c.id) ? () => onSaveAll((id) => id === c.id) : undefined, onClick: () => activateChart(c.id), onRemove: () => {
      closeChart(c.id); updateChartsMenu(chartItems());
      stay.current = true;   // the list shrinks under the pointer; it stays open till the pointer is back on it
      // the bottom row went, so the pointer is now below the list: light the new last row instead (a page can't move the pointer)
      if (i === list.length - 1) requestAnimationFrame(() => document.querySelector<HTMLElement>(".chart-tab .menu > li:last-child > button")?.focus());
    } }));
  };
  // the cloud's list, read when a menu opens: an open chart not in it (or saved with another birth time) is unsaved
  const client = useQueryClient();
  // checked again every 20 s and each time the list opens, so a save from elsewhere shows too
  const cloud = useQuery({ queryKey: ["cloudCharts"], queryFn: api.cloudCharts, refetchInterval: 20_000 });
  useEffect(() => { updateChartsMenu(chartItems()); }, [cloud.data]);   // eslint-disable-line react-hooks/exhaustive-deps
  const unsaved = () => { const { openCharts: list, notes } = useChart.getState(); return list.filter((c) => !inCloud(client.getQueryData(["cloudCharts"]), c, notes)).map((c) => c.id); };
  const stay = useRef(false);
  // the × clicked is taken out from under the pointer, which the browser reports as leaving: close only when the pointer really is outside
  const leaveCharts = (e: React.MouseEvent<HTMLElement>) => { if (!stay.current && !e.currentTarget.contains(document.elementFromPoint(e.clientX, e.clientY))) closeChartsMenu(); };
  const pickChart = (e: React.MouseEvent<HTMLElement>) => {
    const r = e.currentTarget.closest(".chart-tab")!.getBoundingClientRect();
    client.invalidateQueries({ queryKey: ["cloudCharts"] });   // fresh from the Cloud; the open list updates when it comes
    showChartsMenu({ clientX: r.left, clientY: r.bottom, width: r.width }, chartItems(), "Open charts", e.type !== "mouseenter");
  };
  const { open: openSaveMenu, node: saveMenuNode, close: closeSaveMenu } = useMenu();   // its own, so hovering opens and leaving closes it
  const saveMenu = (e: React.MouseEvent<HTMLElement>) => {   // below the Save icon: into the cloud (the current chart or all open ones), or the current chart as a file
    const r = e.currentTarget.getBoundingClientRect();
    openSaveMenu({ clientX: r.left, clientY: r.bottom }, [
      { label: "Save current chart in Cloud", onClick: onSave },
      { label: "Save all open charts in Cloud", onClick: () => onSaveAll() },
      { label: "Save all unsaved charts in Cloud", onClick: () => { const dirty = unsaved(); onSaveAll((id) => dirty.includes(id)); }, disabled: !unsaved().length },
      { label: "Download current chart as .vs (keeps the name, state and notes)", onClick: () => onDownload("vs") },
      { label: "Download current chart as .jhd", onClick: () => onDownload("jhd") },
    ], "Save chart", e.type !== "mouseenter");
  };
  const star = display.layout === "starlight";     // Starlight mirrors the bar: actions left, pages right; settings, about and sign out at the right end, till the user moves them
  const btn = {
    new: <IconButton id="new" icon="new" label="New chart" onClick={onNew} />,
    open: <IconButton id="open" icon="open" label="Open chart" onClick={onOpen} />,
    // hover opens the menu (so no tooltip to cover it); it sits inside the span, so moving onto it keeps it open
    save: (
      <span data-bar-id="save" style={{ display: "inline-flex" }} onMouseEnter={noChart ? undefined : saveMenu} onMouseLeave={closeSaveMenu}>
        <button className="icon-btn" aria-label="Save chart" data-tip="" aria-haspopup="menu" onClick={saveMenu} disabled={noChart}><Icon name="save" /></button>
        {saveMenuNode}
      </span>
    ),
    edit: <IconButton id="edit" icon="edit" label="Edit birth data" onClick={onEdit} disabled={noChart} />,
    print: <IconButton id="print" icon="print" label="Print" onClick={onPrint} disabled={noChart} />,
    fontDown: <IconButton id="fontDown" icon="fontDown" label="Smaller fonts" onClick={() => font(-1)} disabled={display.listFont <= 0} />,
    fontUp: <IconButton id="fontUp" icon="fontUp" label="Bigger fonts" onClick={() => font(1)} disabled={display.listFont >= 7} />,
    settings: <IconButton id="settings" icon="settings" label="Settings" onClick={onSettings} />,
    info: <IconButton id="info" icon="info" label="About and credits" onClick={onAbout} />,
    signOut: <IconButton id="signOut" icon="signOut" label="Sign out" onClick={onSignOut} />,
  };
  const chartBlock = (
    <>
      {birthZone !== null && <span className="muted zone-note" data-bar-id="chart" data-tip="The clock shown is not the birth zone">zone {birth?.tz_east_hours} (born in {birthZone})</span>}
      {mode && !star && (
        <span className="mode-badge" data-bar-id="chart">{mode.title}
          <button className="icon-btn" onClick={backToNatal} aria-label="Back to natal" data-tip="Back to natal chart"><Icon name="close" /></button>
        </span>
      )}
      {star && shownChart ? (
        /* Starlight: the open charts in a dropdown, the shown one's name on its button */
        <nav className="chart-tabs" data-bar-id="chart" aria-label="Open charts">
          {/* hover opens the list; the menu sits inside the tab, so moving onto it keeps it open */}
          <span className="chart-tab" aria-selected
            onMouseEnter={many ? pickChart : undefined} onMouseLeave={leaveCharts} onMouseMove={() => { stay.current = false; }}>
            <button type="button" className="chart-tab-main" aria-haspopup={many ? "menu" : undefined} onClick={many ? pickChart : undefined}>
              <span className="chart-tab-label">{shownChart.name ? <ChartName name={shownChart.name} /> : "(untitled)"}</span>
            </button>
            {/* a cast chart shown (Transit, Tajaka...): its pill inside the name's box, so the name keeps its room */}
            {mode && (
              <span className="mode-badge chart-tab-mode" data-tip={mode.title}>
                {/* Transit, Tajaka, Tithi Pravesha: the kind and the year, "Tajaka - 2027"; any other cast chart its title */}
                <span className="chart-tab-label">{castKind(mode) && birth ? `${castKind(mode)} - ${birth.year}` : mode.title}</span>
                <button type="button" className="chart-tab-close" onClick={backToNatal} aria-label="Back to natal" data-tip="Back to natal chart"><Icon name="close" /></button>
              </span>
            )}
            {/* not saved in the Cloud, or edited since: the save icon struck through in red; a click saves it */}
            {unsaved().includes(shownChart.id) && <button type="button" className="chart-tab-close unsaved-mark" aria-label={`Save ${shownChart.name || "chart"} in Cloud`} onClick={() => onSaveAll((id) => id === shownChart.id)}><Icon name="save" /></button>}
            {/* more than one chart: an arrow for the list; just one: the × to close it */}
            {many
              ? <button type="button" className="chart-tab-close" aria-label="Open charts" aria-haspopup="menu" onClick={pickChart}><Icon name="down" /></button>
              : <button type="button" className="chart-tab-close" aria-label={`Close ${shownChart.name || "chart"}`} data-tip="Close chart" onClick={() => closeChart(shownChart.id)}><Icon name="close" /></button>}
            {chartsMenu}
          </span>
        </nav>
      ) : openCharts.length > 0 ? (
        <nav className="chart-tabs" role="tablist" aria-label="Open charts">
          {openCharts.map((c) => {
            const active = c.id === activeChartId;
            return (
              <span key={c.id} role="tab" className="chart-tab" aria-selected={active}
                data-tip={c.name || "(untitled)"}
                onAuxClick={(e) => { if (e.button === 1) { e.preventDefault(); closeChart(c.id); } }}>
                <button type="button" className="chart-tab-main" onClick={() => activateChart(c.id)}>
                  <span className="chart-tab-label">{c.name ? <ChartName name={c.name} /> : "(untitled)"}</span>
                </button>
                {/* Only the active tab shows × — avoids closing while switching in a tight strip */}
                {active && (
                  <button type="button" className="chart-tab-close" aria-label={`Close ${c.name || "chart"}`}
                    data-tip="Close chart" onClick={() => closeChart(c.id)}>
                    <Icon name="close" />
                  </button>
                )}
              </span>
            );
          })}
        </nav>
      ) : <span className="spacer" data-bar-id="chart" />}
    </>
  );
  /* always the birth time, a transit cast staying at its moment (the Transits tab's own stepper moves that) */
  const stepper = !noChart && <Stepper />;
  const pages = pageTabs(display.transitsTogether, true).filter((t) => t !== "Predictions");
  // Starlight's bar, each piece by id (false while no chart is open); the user's arrangement of it, kept to the pieces there are now
  const items: Record<string, React.ReactNode> = {
    ...btn, chart: chartBlock, stepper, ...Object.fromEntries(pages.map((t) => [t, <PageTab t={t} loose />])),
    /* A: the ayanamsa; N: back to the chart as opened, after a time change or a cast chart (transit, Tajaka, Tithi Pravesha...); P: the Predictions page, where the native's life facts are collected */
    ayanamsa: !noChart && <AyanamsaButton />,
    natal: !noChart && <IconButton id="natal" icon="natal" label="Natal chart (back to the saved time)" disabled={!mode && !undo.length} onClick={() => { undoAll(); backToNatal(); }} />,
    Predictions: !noChart && <IconButton id="Predictions" icon="Predictions" label="Predictions: the native's life facts" pressed={tab === "Predictions"} onClick={() => setTab("Predictions")} />,
  };
  const order = reconcile(display.bar, barDefault(display.transitsTogether));
  const { shown, header, mode: barMode, handlers } = useBarDrag(order, (bar) => setDisplay({ bar }));
  // hidden pieces keep their places in the order, so one brought back returns where it was
  const hidden = display.barHidden;
  const half = (ids: string[]) => ids.filter((id) => !hidden.includes(id)).map((id) => <Fragment key={id}>{items[id]}</Fragment>);
  const hide = (id: string, away: boolean) => setDisplay({ barHidden: away ? [...hidden.filter((x) => x !== id), id] : hidden.filter((x) => x !== id) });
  // right-click a piece: hide it; anywhere on the bar: bring back a hidden one
  const { open: openBarMenu, node: barMenu } = useMenu();
  const barMenuAt = (e: React.MouseEvent<HTMLElement>) => {
    handlers.onContextMenu(e);
    if (e.defaultPrevented) return;     // pressed to rearrange, or already jiggling
    e.preventDefault();
    const id = (e.target as Element).closest<HTMLElement>("[data-bar-id]")?.dataset.barId;
    const on = id && canHide(id) ? id : null;
    const back = [...shown.left, ...shown.right].filter((x) => hidden.includes(x));
    openBarMenu(e, [
      ...(on ? [{ label: `Hide ${barLabel(on)}`, onClick: () => hide(on, true) }] : []),
      ...(on && back.length ? ["-" as const] : []),
      ...back.map((x) => ({ label: `Show ${barLabel(x)}`, onClick: () => hide(x, false) })),
      ...(back.length > 1 ? [{ label: "Show all", onClick: () => setDisplay({ barHidden: [] }) }] : []),
      ...(!on && !back.length ? [{ label: "Nothing hidden: right-click an icon to hide it", disabled: true }] : []),
    ], "Top bar");
  };
  if (star) return (
    <header ref={header} className={`topbar star-bar ${barMode}`} {...handlers} onContextMenu={barMenuAt}>
      {/* everything up to the line after the left's last icon takes the left half, so the line sits at the page's centre */}
      <div className="bar-left">{half(shown.left)}<span className="bar-sep" /></div>
      {/* the right half against its end, its icons spread with equal gaps */}
      <div className="bar-right">{half(shown.right)}</div>
      {barMenu}
    </header>
  );
  return (
    <header className="topbar">
      <PageTabs />
      {chartBlock}
      {stepper}
      <span className="bar-sep" />
      {btn.new}{btn.open}{btn.save}{btn.edit}
      <span className="bar-sep" />
      {btn.print}
      <IconButton icon={charts === 2 ? "chartsFew" : charts === 4 ? "charts4" : "chartsMany"} label={`Charts shown: ${charts} (click for ${charts === 6 ? 2 : charts + 2})`} onClick={() => setCharts(charts === 6 ? 2 : charts === 4 ? 6 : 4)} />
      {btn.fontDown}{btn.fontUp}
      <IconButton icon={theme === "dark" ? "light" : "dark"} label="Toggle dark mode" onClick={() => setTheme(theme === "dark" ? "light" : "dark")} />
      {btn.settings}{btn.info}{btn.signOut}
    </header>
  );
}
