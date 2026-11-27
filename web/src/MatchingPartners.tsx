import { Fragment } from "react";
import { createPortal } from "react-dom";
import { useQuery } from "@tanstack/react-query";
import { api } from "./api";
import { formatDateOrdinal, formatTime12, formatTz } from "./format";
import { useMenu } from "./Menu";
import { useChart } from "./store";
import { Icon } from "./Icons";
import { supOrd, WhoAge } from "./ui";
import { useShownRows } from "./Starlight";
import { type Side } from "./matchingShared";

/** The chart's name as a drop-down of the open charts; a starred one (in ``starred``, this side's list) has a ★ after its name. */
export function PartnerName({ label, side, onPick, starred = [] }: { label: string; side: Side | null; onPick: (s: Side) => void; starred?: Side[] }) {
  const { openCharts, activeChartId, name, natal, meta } = useChart();
  const { open: showMenu, node: menu } = useMenu();
  // the shown chart's own fields are current; its openCharts entry is only refreshed on a switch
  const charts = openCharts.map((c) => c.id === activeChartId && natal ? { ...c, name, natal, meta } : c);
  const pickOpen = (e: React.MouseEvent<HTMLElement>) => {
    const r = e.currentTarget.getBoundingClientRect();
    showMenu({ clientX: r.left, clientY: r.bottom + 4 }, charts.map((c) => {
      const star = starred.some((x) => x.name === (c.name || "Natal") && JSON.stringify(x.birth) === JSON.stringify(c.natal));
      return {
      label: c.name || "(untitled)", show: star ? <>{c.name || "(untitled)"} <span className="menu-star" aria-label="starred">★</span></> : undefined, checked: !!side && side.name === c.name && JSON.stringify(side.birth) === JSON.stringify(c.natal),
      onClick: () => onPick({ name: c.name || "Natal", birth: c.natal, meta: c.meta }),
    }; }), "Open charts");
  };
  return (
    <>
      <button type="button" className="match-name" disabled={!charts.length} onClick={pickOpen} aria-haspopup="menu" title="Pick one of the open charts">
        {side ? side.name || label : "Pick a chart"} <span aria-hidden="true">▾</span>
      </button>
      {menu && createPortal(menu, document.body)}{/* .match-centre's transform would pin the fixed menu to the chart, not the window */}
    </>
  );
}

/** New chart, edit, Open chart (the same dialog as the top bar's), starred or not (the shortlist, the Starred sub tab).
 *  One chart against many, never many against many: while the other side has starred charts, this side's star is off
 *  (``otherStarred``), except to take this chart off if it was starred before. */
export function PartnerActions({ side, onNew, onEdit, onOpen, listed, onList, otherStarred = false }: {
  side: Side | null; onNew: () => void; onEdit: () => void; onOpen: () => void; listed: boolean; onList: () => void; otherStarred?: boolean;
}) {
  const locked = otherStarred && !listed;
  return (
    <span className="row match-actions">
      <button type="button" className="icon-btn" onClick={onNew} aria-label="New chart" title="New chart"><Icon name="new" /></button>
      <button type="button" className="icon-btn" onClick={onEdit} aria-label={side ? "Edit birth data" : "Enter birth data"} title={side ? "Edit birth data" : "Enter birth data"}><Icon name="edit" /></button>
      <button type="button" className="icon-btn" onClick={onOpen} aria-label="Open chart" title="Open chart"><Icon name="open" /></button>
      <button type="button" className="icon-btn match-star" disabled={!side || locked} onClick={onList} aria-pressed={listed} aria-label="Star"
        title={listed ? "Starred: click to take it off" : locked ? "The other side has starred charts: one chart is matched against many, so unstar those to star here" : "Star it, to rank against the other side's chart under Starred"}><Icon name="star" /></button>
    </span>
  );
}

/** "Jyeshtha (Me) (95.12% left)" → "Jyeshtha pada 1 (Me) (95.12% left)": pada from the share of the star left */
const withPada = (nak: string) => {
  const left = Number(/\(([\d.]+)% left\)/.exec(nak)?.[1]);
  if (!Number.isFinite(left)) return nak;
  const pada = Math.min(4, Math.floor((100 - left) / 25) + 1);
  return nak.replace(/^([^(]+?)\s*\(/, `$1 pada ${pada} (`);
};

/** The birth details the Overview shows of each partner at first; a right-click picks others from the Home overview's list (one choice for both). */
const BRIEF_HIDDEN = ["Time Zone", "Altitude", "Hora Lord", "Mahakala Hora", "Kaala Lord", "Sunrise", "Sunset", "Janma Ghatis", "Ayanamsa", "Sidereal Time"];
const BRIEF_NAMES = ["Date", "Time", "Time Zone", "Place", "Altitude", "Lunar Yr-Mo", "Tithi", "Vedic Weekday", "Nakshatra", "Yoga", "Karana", ...BRIEF_HIDDEN.slice(2)];

/** A partner's birth details, as the Home overview lists them: a right-click picks which show (several at once, the menu stays open). */
export function PartnerBrief({ label, side }: { label: string; side: Side | null }) {
  const basics = useQuery({
    queryKey: ["basics", side?.birth, side?.name],
    queryFn: () => api.basics(side!.birth, side!.name),
    enabled: !!side,
  });
  const names = basics.data?.core.map(([k]) => k) ?? BRIEF_NAMES;
  const { hidden, onContextMenu, node } = useShownRows("matchBriefHidden", BRIEF_HIDDEN, names);
  if (!side) return (
    <section className="match-brief">
      <h4>{label}</h4>
      <p className="muted">No chart yet</p>
    </section>
  );
  const pob = [side.meta.city, side.meta.state, side.meta.country].filter(Boolean).join(", ") || "—";
  // the place by its name (its coordinates on hover), the time with its zone, the nakshatra with its pada; the rest as Home writes them
  const shown = (k: string, v: string) => (k === "Place" ? pob : k === "Time" ? `${formatTime12(side.birth.hour_local)} (${formatTz(side.birth.tz_east_hours)})`
    : k === "Date" ? formatDateOrdinal(side.birth.year, side.birth.month, side.birth.day) : k === "Nakshatra" ? withPada(v) : v);
  const rows = (basics.data?.core ?? []).filter(([k, v]) => v && !hidden.includes(k));
  return (
    <section className="match-brief" onContextMenu={onContextMenu}>
      <h4><WhoAge who={label} birth={side.birth} /> · <span translate="no">{side.name}</span></h4>
      <dl className="match-brief-grid">
        {rows.map(([k, v]) => (
          <Fragment key={k}>
            <dt className={k === "Nakshatra" ? "hl" : undefined}>{k}</dt>
            <dd className={k === "Nakshatra" ? "hl" : undefined} data-tip={k === "Place" ? v : undefined} translate={k === "Place" ? "no" : undefined}>{supOrd(shown(k, v))}</dd>
          </Fragment>
        ))}
      </dl>
      {node}
    </section>
  );
}
