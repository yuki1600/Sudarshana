import { useEffect, useMemo, useRef, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api, CHART_FILES, type Birth, type ChartFormat, type CloudChart, type Meta, type RoddenChart, type SharedChart } from "./api";
import { Modal } from "./ChartDialogs";
import { formatDateOrdinal, formatTime12 } from "./format";
import { useKept } from "./hooks";
import { Icon } from "./Icons";
import { supOrd } from "./ui";
import { useChart } from "./store";
import { download } from "./Windows";

/** One row of the list: a chart saved in the cloud, shared, opened lately on this device, or from the Rodden library. */
interface Item {
  key: string;
  name: string;          // as saved: "Tajaka-2026-Rahul Sudish"
  person: string;        // "Rahul Sudish"
  type: string;          // "Natal", "Tajaka", "Transit", "Tithi Pravesha" ...
  year?: string;         // a cast chart's year
  date?: string;
  time?: string;
  place: string;
  notes?: boolean;
  updated?: number;      // seconds; cloud only
  born?: number;         // sortable birth moment
  recent?: { birth: Birth; meta: Meta };
  shared?: { id: number; from: string };   // another account sent it
  rodden?: number;       // a Rodden library chart's id; its type is its rating, AA or A
  category?: string;     // a cloud chart's category ("Sample charts"), kept in its .vs file
}

// a cast chart's name: "Tajaka-2026-Name", or the older "2026-Tajaka-Name"
const CAST = /^(\D[^-]*?)-(\d{3,4})-(.+)$/;
const CAST_OLD = /^(\d{3,4})-(\D[^-]*?)-(.+)$/;
function classify(name: string) {
  const m = CAST.exec(name), o = CAST_OLD.exec(name);
  return m ? { type: m[1], year: m[2], person: m[3] } : o ? { type: o[2], year: o[1], person: o[3] } : { type: "Natal", person: name };
}

const when = (y?: number, m?: number, d?: number, h?: number | null) =>
  y && m && d ? { date: formatDateOrdinal(y, m, d), time: h == null ? undefined : formatTime12(h), born: Date.UTC(y, m - 1, d) / 1000 + (h ?? 0) * 3600 } : {};

function ago(t: number) {
  const s = Date.now() / 1000 - t, rtf = new Intl.RelativeTimeFormat(undefined, { numeric: "auto" });
  const [n, unit]: [number, Intl.RelativeTimeFormatUnit] = s < 60 ? [0, "second"] : s < 3600 ? [s / 60, "minute"] : s < 86400 ? [s / 3600, "hour"]
    : s < 30 * 86400 ? [s / 86400, "day"] : s < 365 * 86400 ? [s / (30 * 86400), "month"] : [s / (365 * 86400), "year"];
  return rtf.format(-Math.floor(n), unit);
}

const fromCloud = (c: CloudChart): Item => ({ key: "c:" + c.name, name: c.name, ...classify(c.name), ...when(c.year, c.month, c.day, c.hour),
  place: [c.place, c.state, c.country].filter(Boolean).join(", "), notes: c.notes, updated: c.updated, category: c.category || undefined });

const fromShared = (c: SharedChart): Item => ({ ...fromCloud(c), key: "s:" + c.id, shared: { id: c.id, from: c.from } });

const fromRodden = ([id, name, rating, y, m, d, h, place]: RoddenChart): Item => ({ key: "l:" + id, name, person: name, type: rating, ...when(y, m, d, h), place, rodden: id });

const SAMPLES = "Sample charts";   // the cloud category the sample charts are saved under: a button after All
const SHOWN = 200;   // rows drawn at once: the Rodden library has some 54 000

const initials = (s: string) => s.split(/\s+/).filter(Boolean).slice(0, 2).map((w) => w[0]).join("").toUpperCase() || "?";

const SORTS: [string, string][] = [["saved", "Recently saved"], ["name", "Name A–Z"], ["person", "Grouped by person"], ["born-new", "Birth date, newest"], ["born-old", "Birth date, oldest"]];

/** Open chart: drop or pick files from this device, or open a chart saved in the cloud, shared with this account or opened lately;
 *  search, filter by kind, sort, and rename, share, download or delete a saved chart. A click outside or Esc closes it. */
export function OpenChart({ onFiles, onCloud, onRecent, onClose, single }: {
  onFiles: (f: File[]) => void; onCloud: (name: string, content: string) => void; onClose: () => void;   // onCloud: a cloud or shared chart's file
  onRecent?: (name: string, birth: Birth, meta: Meta) => void;   // a recent chart picked; opens it as the shown chart when not given
  single?: boolean;   // a click opens the chart (Matching's one side); otherwise clicks select charts and Open / Open all opens them
}) {
  const client = useQueryClient();
  const { recent, openChart } = useChart();
  const cloud = useQuery({ queryKey: ["cloudCharts"], queryFn: api.cloudCharts });
  const shared = useQuery({ queryKey: ["sharedCharts"], queryFn: api.sharedCharts });
  const [source, setSource] = useKept<"cloud" | "shared" | "recent" | "rodden">("open.source", "cloud");
  const library = useQuery({ queryKey: ["rodden"], queryFn: api.rodden, staleTime: Infinity, enabled: source === "rodden" });   // megabytes: only once asked for
  const remote = source === "cloud" ? cloud : source === "shared" ? shared : source === "rodden" ? library : null;
  const [sort, setSort] = useKept("open.sort", "saved");
  const [type, setType] = useKept("open.type", "All");
  const [query, setQuery] = useState("");
  const [cursor, setCursor] = useState(0);
  const [over, setOver] = useState(false);
  const [renaming, setRenaming] = useKept<{ from: string; to: string } | null>("open.renaming", null);
  const [deleting, setDeleting] = useKept<string | null>("open.deleting", null);
  const [sharing, setSharing] = useKept<{ name: string; to: string } | null>("open.sharing", null);
  const [sent, setSent] = useState("");
  const matches = useQuery({ queryKey: ["findUsers", sharing?.to.trim()], queryFn: () => api.findUsers(sharing!.to.trim()),
    enabled: (sharing?.to.trim().replace(/^@/, "").length ?? 0) >= 2 });
  const [picked, setPicked] = useKept<Item[]>("open.picked", []);
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState("");
  const search = useRef<HTMLInputElement>(null);
  const list = useRef<HTMLUListElement>(null);

  const all: Item[] = useMemo(() => source === "cloud" ? (cloud.data ?? []).map(fromCloud)
    : source === "shared" ? (shared.data ?? []).map(fromShared)
    : source === "rodden" ? (library.data ?? []).map(fromRodden)
    : recent.map((r) => ({ key: "r:" + r.name, name: r.name || "(no name)", ...classify(r.name), ...when(r.birth.year, r.birth.month, r.birth.day, r.birth.hour_local),
      place: [r.meta.city, r.meta.state, r.meta.country].filter(Boolean).join(", "), recent: { birth: r.birth, meta: r.meta } })), [source, cloud.data, shared.data, library.data, recent]);
  const types = useMemo(() => {
    const n = new Map<string, number>();
    for (const i of all) n.set(i.type, (n.get(i.type) ?? 0) + 1);
    return [...n].sort(([a], [b]) => (a === "Natal" ? -1 : b === "Natal" ? 1 : a.localeCompare(b)));
  }, [all]);
  const samples = useMemo(() => all.filter((i) => i.category === SAMPLES).length, [all]);
  // a kind (or Sample charts) with no charts left falls back to All
  const kind = type === "All" || types.some(([t]) => t === type) || (type === SAMPLES && samples) ? type : "All";
  const matched = useMemo(() => {
    const words = query.toLowerCase().split(/\s+/).filter(Boolean);
    const hit = (i: Item) => words.every((w) => [i.name, i.type, i.place, i.date, i.time, i.shared?.from, i.category].join(" ").toLowerCase().includes(w));
    const by: Record<string, (a: Item, b: Item) => number> = {
      saved: (a, b) => (b.updated ?? 0) - (a.updated ?? 0),
      name: (a, b) => a.name.localeCompare(b.name),
      person: (a, b) => a.person.localeCompare(b.person) || (a.type === "Natal" ? -1 : b.type === "Natal" ? 1 : a.name.localeCompare(b.name)),
      "born-new": (a, b) => (b.born ?? 0) - (a.born ?? 0),
      "born-old": (a, b) => (a.born ?? 0) - (b.born ?? 0),
    };
    const shown = all.filter((i) => (kind === "All" || (kind === SAMPLES ? i.category === SAMPLES : i.type === kind)) && hit(i));
    // recent keeps its own order, last opened first; the Rodden library comes in name order
    return (source === "recent" && sort === "saved") || (source === "rodden" && (sort === "saved" || sort === "name")) ? shown : shown.sort(by[sort] ?? by.saved);
  }, [all, kind, query, sort, source]);
  const items = matched.length > SHOWN ? matched.slice(0, SHOWN) : matched;

  useEffect(() => { requestAnimationFrame(() => search.current?.focus()); }, []);   // after showModal, which focuses the first button
  useEffect(() => setCursor(0), [query, kind, sort, source]);
  useEffect(() => { list.current?.querySelector('[aria-selected="true"]')?.scrollIntoView({ block: "nearest" }); }, [cursor]);

  const refresh = () => client.invalidateQueries({ queryKey: [source === "shared" ? "sharedCharts" : "cloudCharts"] });
  const content = async (i: Item) => (await (i.rodden ? api.roddenChart(i.rodden) : i.shared ? api.sharedChart(i.shared.id) : api.cloudChart(i.name))).content;
  const act = async (key: string, run: () => Promise<unknown>) => {
    setBusy(key); setError("");
    try { await run(); } catch (e) { setError((e as Error).message); } finally { setBusy(null); }
  };
  const open = (i: Item) => {
    if (i.recent) { (onRecent ?? openChart)(i.name, i.recent.birth, i.recent.meta); onClose(); }
    else act(i.key, async () => onCloud(i.name, await content(i)));
  };
  const isPicked = (i: Item) => picked.some((x) => x.key === i.key);
  const pick = (i: Item) => setPicked(isPicked(i) ? picked.filter((x) => x.key !== i.key) : [...picked, i]);
  const openPicked = () => act("open", async () => {
    const texts = await Promise.all(picked.map((i) => (i.recent ? null : content(i))));   // all fetched first: opening one closes this dialog
    setPicked([]);
    picked.forEach((i, n) => (i.recent ? (onRecent ?? openChart)(i.name, i.recent.birth, i.recent.meta) : onCloud(i.name, texts[n]!)));
    onClose();
  });
  const save = (i: Item, format: ChartFormat) => act(i.key + format, async () => {
    if (i.recent) return download(`${i.name}.${format}`, (await api.exportChart(i.recent.birth, i.recent.meta, format, i.name)).content);
    const text = await content(i);
    if (format === "vs") return download(`${i.name}.vs`, text);
    const { birth, parsed: p } = await api.parseJhd(text);
    const meta = { city: p.city ?? "", country: p.country ?? "", dst: !!p.dst, tz_standard_east: p.tz_standard_east, tz_dst_east: p.tz_dst_east, gender: p.gender, state: p.state ?? "" } as Meta;
    download(`${i.name}.jhd`, (await api.exportChart(birth, meta, "jhd", i.name)).content);
  });
  const rename = () => {
    const r = renaming!;
    const to = r.to.trim();
    if (!to || to === r.from) return setRenaming(null);
    act("c:" + r.from, async () => { await api.renameCloudChart(r.from, to); setRenaming(null); await refresh(); });
  };
  const remove = (i: Item) => act(i.key, async () => { await (i.shared ? api.deleteShared(i.shared.id) : api.deleteCloudChart(i.name)); setDeleting(null); await refresh(); });
  const share = (name: string, to: string) => act("c:" + name, async () => {
    if (!to.trim()) return;
    const r = await api.shareChart(name, to);
    setSharing(null); setSent(`Sent ${r.name} to @${r.to}`);
  });

  const keys = (e: React.KeyboardEvent) => {
    if (renaming || deleting || sharing) return;
    if (e.key === "ArrowDown" || e.key === "ArrowUp") {
      e.preventDefault();
      setCursor((c) => Math.max(0, Math.min(items.length - 1, c + (e.key === "ArrowDown" ? 1 : -1))));
    } else if (e.key === "Enter" && items[cursor] && !(e.target as Element).closest("button, select")) { e.preventDefault(); open(items[cursor]); }
    else if (e.key === "/" && document.activeElement !== search.current) { e.preventDefault(); search.current?.focus(); }
  };
  const drop = (e: React.DragEvent) => { e.preventDefault(); setOver(false); const fs = [...e.dataTransfer.files]; if (fs.length) onFiles(fs); };

  const row = (i: Item, n: number) => {
    const cast = i.type !== "Natal" && !i.rodden;
    const sub = [i.shared && `from @${i.shared.from}`, i.date, i.time, i.place].filter(Boolean).join(" · ");
    const mine = !i.recent && !i.shared && !i.rodden;   // a chart saved in this account's cloud
    const confirming = deleting === i.name && mine;
    return (
      <li key={i.key} className={!single && isPicked(i) ? "oc-row picked" : "oc-row"} role="option" aria-selected={n === cursor} onMouseEnter={() => setCursor(n)}>
        {sharing?.name === i.name && mine ? (
          <form className="oc-rename oc-share" onSubmit={(e) => { e.preventDefault(); share(i.name, sharing.to); }}>
            <input autoFocus aria-label={`Share ${i.name} with the user ID`} placeholder="User ID" value={sharing.to} onChange={(e) => setSharing({ ...sharing, to: e.target.value })}
              onKeyDown={(e) => { if (e.key === "Escape") { e.preventDefault(); e.stopPropagation(); setSharing(null); } }} />
            <button type="submit" className="primary" disabled={busy === i.key || !sharing.to.trim()}>Share</button>
            <button type="button" onClick={() => setSharing(null)}>Cancel</button>
            {!!matches.data?.length && (
              <ul className="oc-users" role="listbox" aria-label="Users">
                {matches.data.map((u) => (
                  <li key={u.username}><button type="button" onClick={() => share(i.name, u.username)}>@{u.username}<span className="muted">{u.name}</span></button></li>
                ))}
              </ul>
            )}
          </form>
        ) : renaming?.from === i.name && mine ? (
          <form className="oc-rename" onSubmit={(e) => { e.preventDefault(); rename(); }}>
            <input autoFocus aria-label={`New name for ${i.name}`} value={renaming.to} onChange={(e) => setRenaming({ ...renaming, to: e.target.value })}
              onKeyDown={(e) => { if (e.key === "Escape") { e.preventDefault(); e.stopPropagation(); setRenaming(null); } }} />
            <button type="submit" className="primary" disabled={busy === i.key}>Rename</button>
            <button type="button" onClick={() => setRenaming(null)}>Keep</button>
          </form>
        ) : (
          <>
            <button type="button" className="oc-main" onClick={() => (single ? open(i) : pick(i))} aria-pressed={single ? undefined : isPicked(i)}>
              <span className={cast ? "oc-avatar cast" : "oc-avatar"} aria-hidden="true" translate="no">{initials(i.person)}</span>
              <span className="oc-text">
                <span className="oc-name"><span translate="no">{i.person}</span><span className={cast ? `oc-kind cast${i.type === "Transit" ? " transit" : ""}` : "oc-kind"}>{i.type}{i.year ? ` ${i.year}` : ""}</span>{i.notes && <span className="oc-kind notes">Notes</span>}</span>
                <span className="oc-sub">{supOrd(sub || "No birth details")}</span>
              </span>
              {i.updated !== undefined && <span className="oc-when" title={new Date(i.updated * 1000).toLocaleString()}>{ago(i.updated)}</span>}
            </button>
            {confirming ? (
              <span className="oc-actions confirm">
                <span>{i.shared ? "Remove from shared?" : "Delete from the cloud?"}</span>
                <button type="button" className="danger" disabled={busy === i.key} onClick={() => remove(i)}>Delete</button>
                <button type="button" onClick={() => setDeleting(null)}>Keep</button>
              </span>
            ) : (
              <span className="oc-actions">
                <button type="button" className="oc-dl" disabled={busy === i.key + "vs"} onClick={() => save(i, "vs")} data-tip="Download as .vs (keeps the name, state and notes)"><Icon name="save" />.vs</button>
                <button type="button" className="oc-dl" disabled={busy === i.key + "jhd"} onClick={() => save(i, "jhd")} data-tip="Download as .jhd"><Icon name="save" />.jhd</button>
                {mine && <>
                  <button type="button" className="icon-btn" aria-label={`Rename ${i.name}`} data-tip="Rename" onClick={() => setRenaming({ from: i.name, to: i.name })}><Icon name="edit" /></button>
                  <button type="button" className="icon-btn" aria-label={`Share ${i.name}`} data-tip="Share with another user" onClick={() => { setSent(""); setSharing({ name: i.name, to: "" }); }}><Icon name="share" /></button>
                </>}
                {!i.recent && !i.rodden && <button type="button" className="icon-btn oc-del" aria-label={`${i.shared ? "Remove" : "Delete"} ${i.name}`} data-tip={i.shared ? "Remove from shared" : "Delete"} onClick={() => setDeleting(i.name)}><Icon name="trash" /></button>}
              </span>
            )}
          </>
        )}
      </li>
    );
  };

  const cloudCount = cloud.data?.length;
  return (
    <Modal title="Open chart" onClose={onClose}>
      <div className={over ? "oc dragging" : "oc"} onKeyDown={keys} onDragOver={(e) => { e.preventDefault(); setOver(true); }}
        onDragLeave={(e) => { if (!e.currentTarget.contains(e.relatedTarget as Node)) setOver(false); }} onDrop={drop}>
        <label className="oc-drop">
          <span className="oc-drop-icon" aria-hidden="true"><Icon name="open" /></span>
          <span><strong>{over ? "Let go to open" : "Drop .jhd or .vs files here"}</strong><span className="muted">or click to choose from this device; several at once open side by side</span></span>
          <input type="file" accept={CHART_FILES} multiple hidden onChange={(e) => { const fs = [...(e.target.files ?? [])]; if (fs.length) onFiles(fs); e.target.value = ""; }} />
        </label>

        <div className="oc-bar">
          <div className="seg" role="tablist" aria-label="Where from">
            <button type="button" role="tab" aria-selected={source === "cloud"} onClick={() => setSource("cloud")}>Cloud{cloudCount !== undefined && <span className="oc-count">{cloudCount}</span>}</button>
            <button type="button" role="tab" aria-selected={source === "shared"} onClick={() => setSource("shared")}>Shared{shared.data !== undefined && <span className="oc-count">{shared.data.length}</span>}</button>
            <button type="button" role="tab" aria-selected={source === "recent"} onClick={() => setSource("recent")}>Recent<span className="oc-count">{recent.length}</span></button>
            <button type="button" role="tab" aria-selected={source === "rodden"} onClick={() => setSource("rodden")}>Rodden{library.data !== undefined && <span className="oc-count">{library.data.length}</span>}</button>
          </div>
          <label className="oc-search">
            <Icon name="search" />
            <input ref={search} type="search" placeholder="Search name, place, date, kind…" aria-label="Search charts" value={query} onChange={(e) => setQuery(e.target.value)} />
            <kbd aria-hidden="true">/</kbd>
          </label>
          <select aria-label="Sort" value={source === "rodden" && sort === "saved" ? "name" : sort} onChange={(e) => setSort(e.target.value)}>
            {SORTS.filter(([k]) => (source !== "recent" && source !== "rodden") || k !== "saved").map(([k, n]) => <option key={k} value={k}>{n}</option>)}
            {source === "recent" && <option value="saved">Last opened</option>}
          </select>
        </div>

        {(types.length > 1 || samples > 0 || !single) && (
          <div className="oc-pickrow">
            {(types.length > 1 || samples > 0) && (
              <div className="oc-chips" role="group" aria-label="Kind of chart">
                {[["All", all.length] as [string, number], ...(samples ? [[SAMPLES, samples] as [string, number]] : []), ...types].map(([t, n]) => (
                  <button key={t} type="button" className="oc-chip" aria-pressed={kind === t} onClick={() => setType(t)}>{t}<span className="oc-count">{n}</span></button>
                ))}
              </div>
            )}
            {!single && (
              <span className="oc-open">
                {picked.length > 1 && <span className="muted">{picked.length} selected</span>}
                {!!picked.length && <button type="button" onClick={() => setPicked([])}>Unselect all</button>}
                <button type="button" className="primary" disabled={!picked.length || busy === "open"} onClick={openPicked}>{picked.length > 1 ? "Open all" : "Open"}</button>
              </span>
            )}
          </div>
        )}

        {error && <p role="alert" className="error banner">{error}</p>}
        {sent && <p role="status" className="oc-sent">{sent}</p>}
        {remote?.isPending ? <p className="oc-empty muted">Loading {source === "cloud" ? "your saved charts" : source === "shared" ? "shared charts" : "the Rodden library"}…</p>
          : remote?.isError ? <p role="alert" className="oc-empty error">{remote.error?.message}</p>
            : !all.length ? (
              <div className="oc-empty">
                <strong>{source === "cloud" ? "Nothing saved in the cloud yet" : source === "shared" ? "No charts shared with you yet" : source === "rodden" ? "The Rodden library isn't built yet" : "No charts opened lately"}</strong>
                <span className="muted">{source === "cloud" ? "Use Save > Save current chart in Cloud, or Save all open charts in Cloud."
                  : source === "shared" ? "When another user shares a chart with your user ID, it shows up here."
                    : source === "rodden" ? "Run databases/build_rodden_db.py on the server, then restart it." : "Charts you open show up here."}</span>
              </div>
            ) : !items.length ? (
              <div className="oc-empty">
                <strong>No chart matches{query ? ` “${query}”` : ""}</strong>
                <button type="button" onClick={() => { setQuery(""); setType("All"); }}>Show all charts</button>
              </div>
            ) : (
              <ul ref={list} className="oc-list" role="listbox" aria-label="Charts">
                {items.flatMap((i, n) => sort === "person" && (n === 0 || items[n - 1].person !== i.person)
                  ? [<li key={"h:" + i.person} className="oc-group" role="presentation">{i.person}</li>, row(i, n)] : [row(i, n)])}
                {matched.length > items.length && <li className="oc-group" role="presentation">First {items.length} of {matched.length.toLocaleString()}: search to find the rest</li>}
              </ul>
            )}
      </div>
    </Modal>
  );
}
