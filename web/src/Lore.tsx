import { createContext, useContext, useEffect, useLayoutEffect, useRef, useState, type CSSProperties, type ReactNode } from "react";
import { useQuery } from "@tanstack/react-query";
import { api, type BhavaLore, type BhavaReading, type GrahaLore, type JivaAjiva, type LoreFacts, type LoreLink, type LoreQuote, type LoreSide, type NakshatraLore, type RashiLore } from "./api";
import { backdropClose } from "./ChartDialogs";
import { SYLLABLES } from "./chakraTables";
import { keep, useKept } from "./hooks";
import { brief, nameAndGloss, SIGN_NAMES } from "./format";
import { useChart } from "./store";
import { Loaded, OneRowTabs, supOrd } from "./ui";
import { Icon } from "./Icons";
import { GrahaStrengths } from "./Panels";

/** A pop-up for reading: a fixed head (title, a line under it, then its tab row) over a body that scrolls, Close at the head's top right.
 *  ``aside``: what sits at the head's top right, before Close (the picker; in the panel, the kind's drop-down before it). ``back``: a way back to the reading this one was opened from.
 *  ``side``: Starlight's panel over the right half, where it stays open beside the charts (not modal) at that box; else a centred modal. */
export function LoreDialog({ title, sub, tabs, aside, back, side, onClose, children }: {
  title: ReactNode; sub?: ReactNode; tabs?: ReactNode; aside?: ReactNode; back?: () => void; side?: CSSProperties; onClose: () => void; children: ReactNode }) {
  const ref = useRef<HTMLDialogElement>(null);
  const kinds = useContext(LoreKinds);
  useEffect(() => { if (!side && !ref.current?.open) ref.current?.showModal(); }, [side]);
  return (
    <dialog ref={ref} open={side ? true : undefined} className={side ? "dialog lore side" : "dialog lore"} style={side} aria-labelledby="lore-title"
      onClose={side ? undefined : onClose} onClick={side ? undefined : backdropClose}>
      <header className="lore-head">
        <div className="lore-top">
          {back && <button type="button" className="icon-btn lore-back" aria-label="Back" data-tip="Back to the last reading" onClick={back}>‹</button>}
          <div className="lore-title"><h2 id="lore-title">{title}</h2>{sub && <p className="muted">{sub}</p>}</div>
          <div className="lore-aside">
            {side && kinds && <LorePicker plain items={KIND_NAMES} n={KINDS.indexOf(kinds.now) + 1} onPick={(k) => kinds.to(KINDS[k - 1])} label="Read a" rows={4} />}
            {aside}
          </div>
          <button type="button" className="icon-btn lore-close" aria-label="Close" data-tip="Close (Esc)" onClick={() => (side ? onClose() : ref.current?.close())}><Icon name="close" /></button>
        </div>
        {tabs}
      </header>
      <div className="lore-body">{children}</div>
    </dialog>
  );
}

// --- what is open, kept over a refresh: one reading at a time in the panel, with the readings it was reached from behind it

/** A reading to open: ``from`` marks a nakshatra's reading for the graha that opened it ("La": the Lagna); ``ref`` counts a bhava from
 *  a graha (the bhava chart's reference); ``d`` reads a rashi in that varga of the chart (0: in no chart). */
export type LoreAt = LoreLink & { from?: string; ref?: number; d?: number };
type LoreKept = { at: LoreAt; back: LoreAt[] } | null;
const LORE = "lore.open";

/** Opens a reading in the panel from anywhere outside it (a chart, a table): a fresh start, with nothing to go back to. A second click on
 *  the one the panel shows now closes it. */
export function openLore(at: LoreAt) {
  const same = (a: LoreAt) => [a.kind, String(a.n), a.d ?? "", a.ref ?? "", a.from ?? ""].join("|");
  let now: LoreKept = null;
  try { now = JSON.parse(localStorage.getItem("view." + LORE) ?? "null") as LoreKept; } catch { /* nothing kept */ }
  const shown = !!document.querySelector("dialog.lore.side[open]");
  keep(LORE, shown && now && same(now.at) === same(at) ? null : { at, back: [] });
}

/** Where a link in a reading goes: inside the panel it opens there (and Back returns); elsewhere it opens the panel. */
const LoreNav = createContext<(to: LoreAt) => void>(openLore);
/** The panel's kind drop-down: the kind open now, and a way to read another kind (the one this reading is tied to in the chart). */
type LoreKind = LoreAt["kind"];
const KINDS: LoreKind[] = ["graha", "rashi", "bhava", "nakshatra"];
const KIND_NAMES = ["Graha", "Rashi", "Bhava", "Nakshatra"];
const LoreKinds = createContext<{ now: LoreKind; to: (k: LoreKind) => void } | null>(null);
function Go({ to, children, tip }: { to: LoreAt; children: ReactNode; tip?: string }) {
  const go = useContext(LoreNav);
  return <button type="button" className="nak-link" data-tip={tip} onClick={() => go(to)}>{children}</button>;
}

// the screens without the charts on the left: the panel waits there, hidden, until one comes back
const NO_CHARTS = new Set(["Remedies", "Muhurta", "Calculations", "Research", "Timeline", "Chakras", "Astrocartography", "Finance", "Matching"]);

/** The panel's box: over the right half, from the charts' right edge (past their gap) to the page's right margin, as tall as the
 *  charts; the whole window less a margin where Starlight stacks its halves. */
function useSideBox(active: boolean, tab: string) {
  const [box, setBox] = useState<CSSProperties | null>(null);
  useLayoutEffect(() => {
    if (!active) return;
    let charts: Element | null = null;
    const ro = new ResizeObserver(() => fit());
    const fit = () => {
      const now = document.querySelector(".star-charts, .star-chart.transit-square, .star-chart.transit-chakra");
      if (now !== charts) { if (charts) ro.unobserve(charts); charts = now; if (charts) ro.observe(charts); }
      const r = charts?.getBoundingClientRect(), W = window.innerWidth, H = window.innerHeight;
      setBox(r && r.width > 0 && W - r.right > 320 ? { left: r.right + 8, top: r.top, width: W - r.right - 8 - Math.max(8, r.left), height: r.height }
        : { left: 8, top: 8, width: W - 16, height: H - 16 });
    };
    fit();
    const raf = requestAnimationFrame(fit);     // the charts may be laid out a frame after the panel opens
    addEventListener("resize", fit);
    return () => { cancelAnimationFrame(raf); ro.disconnect(); removeEventListener("resize", fit); };
  }, [active, tab]);
  return active ? box : null;
}

/** Starlight's lore panel, mounted once (App): the graha, rashi, bhava or nakshatra open, over the right half beside the charts. A link
 *  inside opens there and can be gone back from; the picker swaps within a kind; Escape or Close closes it. Kept over a refresh. */
export function LoreHost() {
  const [st, setSt] = useKept<LoreKept>(LORE, null);
  const tab = useChart((s) => s.tab);
  const starlight = useChart((s) => s.display.layout) === "starlight";
  const birth = useChart((s) => s.birth);
  const active = !!st && starlight && !!birth && !NO_CHARTS.has(tab);
  const box = useSideBox(active, tab);
  const facts = useChartFacts(active ? 1 : 0);
  useEffect(() => {
    if (!active) return;
    const key = (e: KeyboardEvent) => { if (e.key === "Escape" && !document.querySelector("dialog:modal")) setSt(null); };
    addEventListener("keydown", key);
    return () => removeEventListener("keydown", key);
  }, [active]); // eslint-disable-line react-hooks/exhaustive-deps
  if (!active || !box || !st) return null;
  const go = (to: LoreAt) => setSt({ at: to, back: [...st.back.slice(-19), st.at] });
  const swap = (to: LoreAt) => setSt({ at: to, back: st.back });
  const back = st.back.length ? () => setSt({ at: st.back[st.back.length - 1], back: st.back.slice(0, -1) }) : undefined;
  const p = { side: box, back, swap, onClose: () => setSt(null) };
  const at = st.at;
  const kinds = { now: at.kind, to: (k: LoreKind) => k !== at.kind && go(tied(at, k, facts)) };
  return (
    <LoreNav.Provider value={go}><LoreKinds.Provider value={kinds}>
      {at.kind === "graha" ? <GrahaPop key={`g${at.n}`} ab={String(at.n)} {...p} />
        : at.kind === "rashi" ? <RashiPop key={`r${at.n}.${at.d ?? 1}`} n={Number(at.n)} d={at.d ?? 1} {...p} />
          : at.kind === "bhava" ? <BhavaPop key={`b${at.n}.${at.ref ?? 0}`} n={Number(at.n)} base={at.ref ?? 0} {...p} />
            : <NakshatraPop key={`n${at.n}`} n={Number(at.n)} graha={at.from} {...p} />}
    </LoreKinds.Provider></LoreNav.Provider>
  );
}
/** The ``kind`` reading tied to the one open, in this chart where it can be: a graha's rashi, nakshatra and bhava; a rashi's lord, its first
 *  nakshatra and the bhava whose cusp it holds (else its count from the Lagna); a bhava's cusp's rashi and nakshatra and its lord; a
 *  nakshatra's lord, its rashi and the bhava whose cusp is in it (else its rashi's). Without the chart: the first of the kind. */
function tied(at: LoreAt, kind: LoreKind, { rows, insights, houses }: ReturnType<typeof useChartFacts>): LoreAt {
  const cusps = (houses ?? []).map((h) => h.cusp), lagna = rows?.find((r) => r.name === "Lagna");
  const bhavaOf = (sign: number, nak?: number) => {     // sign 0..11; the first bhava whose cusp is in that nakshatra or that sign
    const h = (nak ? cusps.findIndex((c) => nakOf(c) === nak) : -1) + 1 || cusps.findIndex((c) => signOf(c) === sign) + 1;
    return h || (lagna ? ((sign - signOf(lagna.lon) + 12) % 12) + 1 : 1);
  };
  let sign = 0, nak = 1, ab = "Su", bhava = 1;
  if (at.kind === "graha") {
    const row = rows?.find((r) => r.name === GRAHA_NAMES[String(at.n)]), ins = insights?.find((g) => g.name === GRAHA_NAMES[String(at.n)]);
    if (row) { sign = signOf(row.lon); nak = nakOf(row.lon); }
    ab = String(at.n); bhava = ins?.bhava ?? bhavaOf(sign);
  } else if (at.kind === "rashi") {
    sign = Number(at.n) - 1; nak = nakOf(sign * 30 + 1e-6); ab = SIGN_LORDS[sign]; bhava = bhavaOf(sign);
  } else if (at.kind === "bhava") {
    bhava = Number(at.n);
    const c = cusps[bhava - 1];
    if (c != null) { sign = signOf(c); nak = nakOf(c); } else if (lagna) { sign = (signOf(lagna.lon) + bhava - 1) % 12; nak = nakOf(sign * 30 + 1e-6); }
    ab = SIGN_LORDS[sign];
  } else {
    nak = Number(at.n); sign = signOf((nak - 1) * (360 / 27) + 1e-6); ab = NAK_LORDS[(nak - 1) % 9]; bhava = bhavaOf(sign, nak);
  }
  return kind === "graha" ? { kind, n: ab } : kind === "rashi" ? { kind, n: sign + 1, d: 1 } : kind === "bhava" ? { kind, n: bhava } : { kind, n: nak };
}
type PopProps = { side?: CSSProperties; back?: () => void; swap: (to: LoreAt) => void; onClose: () => void };

// --- the pieces every reading is made of

/** Words as chips: "Youthful", "Ageless"…; ``more`` ends the row (its "+n more"). */
export const Chips = ({ items, tone, more }: { items: string[]; tone?: "good" | "bad"; more?: ReactNode }) =>
  items.length ? <ul className={`lore-chips${tone ? ` ${tone}` : ""}`}>{items.map((x) => <li key={x}>{x}</li>)}{more && <li className="lore-chip-more">{more}</li>}</ul> : null;

/** The pop-ups' passages and chip rows opened past their first part: kept over a refresh, the last 60. */
function useOpened(id: string) {
  const [open, setOpen] = useKept<string[]>("lore.opened", []);
  const on = open.includes(id);
  return [on, () => setOpen(on ? open.filter((x) => x !== id) : [...open.slice(-59), id])] as const;
}

/** A passage cut to its first ``n`` sentences (format.ts brief), the rest behind "more". */
function Brief({ text, id, n = 1 }: { text: string; id: string; n?: number }) {
  const [on, flip] = useOpened(id);
  const cut = brief(text, n);
  if (cut === text) return <>{text}</>;
  return <>{on ? text : cut} <button type="button" className="lore-more" onClick={flip}>{on ? "less" : "more"}</button></>;
}

/** The first ``n`` chips, the rest behind "+k more". */
function SomeChips({ items, tone, n, id }: { items: string[]; tone?: "good" | "bad"; n: number; id: string }) {
  const [on, flip] = useOpened(id);
  const more = items.length > n && <button type="button" className="lore-more" onClick={flip}>{on ? "fewer" : `+${items.length - n} more`}</button>;
  return <Chips items={on ? items : items.slice(0, n)} tone={tone} more={more} />;
}

const Section = ({ title, tone, children }: { title: ReactNode; tone?: "good" | "bad"; children: ReactNode }) =>
  <section className="lore-sec"><h3>{tone && <i className={`lore-dot ${tone}`} aria-hidden />}{title}</h3>{children}</section>;
/** A list of the book's passages, each cut to its first sentence. */
const Points = ({ items, id }: { items: string[]; id: string }) =>
  items.length ? <ul className="lore-points">{items.map((x, i) => <li key={i}><Brief text={x} id={`${id}.${i}`} /></li>)}</ul> : null;

/** A fact's value: its name, then its gloss under it, smaller ("Moksha", "Spiritual Liberation / Emancipation"). */
const Value = ({ v }: { v: string }) => { const [name, gloss] = nameAndGloss(v); return <><b>{name}</b>{gloss && <small>{gloss}</small>}</>; };

/** The facts marked for a glance, as tiles. */
const Tiles = ({ facts, more = [] }: { facts: LoreFacts; more?: [string, ReactNode][] }) => (
  <div className="lore-tiles">
    {facts.flatMap((g) => g.rows).filter((r) => r.tile).map((r) => <div key={r.k}><span>{r.k}</span><Value v={r.v} /></div>)}
    {more.map(([k, v]) => <div key={k}><span>{k}</span>{v}</div>)}
  </div>
);

/** The facts in their groups, key and value, each with the classic it comes from. */
const Facts = ({ facts }: { facts: LoreFacts }) => (
  <div className="lore-pair">
    {facts.map((g) => (
      <Section key={g.name} title={g.name}>
        <dl className="lore-kv">{g.rows.map((r) => <div key={r.k}><dt>{r.k}</dt><dd><Value v={r.v} />{r.src && <small className="lore-cite">{r.src}</small>}</dd></div>)}</dl>
      </Section>
    ))}
  </div>
);

/** What it signifies, Jiva (the living) beside Ajiva (the non-living), each part's chips; ``n``: chips shown before "+k more". */
function Significations({ sides, id, n = 24, extra }: { sides: LoreSide[]; id: string; n?: number; extra?: Record<string, ReactNode> }) {
  return (
    <div className="lore-jiva">
      {sides.map((side) => (
        <section key={side.id} className={`lore-side ${side.id}`}>
          <h3>{side.name} <small>{side.gloss}</small></h3>
          {side.parts.map((p) => <div key={p.id} className="lore-part"><span className="g-kicker">{p.name}</span><SomeChips items={p.items} n={n} id={`${id}.${side.id}.${p.id}`} /></div>)}
          {!side.parts.length && <p className="muted">Nothing the classics name here.</p>}
          {extra?.[side.id]}
        </section>
      ))}
    </div>
  );
}

/** A reading split in two: what it says of the living (jiva) and of the non-living (ajiva). */
const JA = ({ r }: { r: JivaAjiva }) => (
  <div className="lore-ja"><p><span className="g-kicker">Jiva</span>{r.jiva}</p><p><span className="g-kicker">Ajiva</span>{r.ajiva}</p></div>
);

/** The classics' own words: each sloka's heading, its first two sentences (the rest behind "more") and where it is. */
const Quotes = ({ items, id }: { items: LoreQuote[]; id: string }) => (
  <>{items.map((q, i) => (
    <blockquote key={i} className="lore-quote"><p>{q.head && <b>{q.head}. </b>}<Brief text={q.text} id={`${id}.${i}`} n={2} /></p><cite>{q.source}</cite></blockquote>
  ))}</>
);

/** Rows, one per item (a bhava, a rashi, a nakshatra, a graha): its name (a link), its reading; the chart's own marked. */
const Rows = ({ rows }: { rows: { key: string; head: ReactNode; body: ReactNode; here?: boolean; cite?: string }[] }) => (
  <ol className="lore-rows">{rows.map((r) => (
    <li key={r.key} className={r.here ? "here" : undefined}>
      <div className="lore-row-head">{r.head}{r.here && <small className="lore-here">in this chart</small>}</div>
      <div>{r.body}{r.cite && <small className="lore-cite">{r.cite}</small>}</div>
    </li>
  ))}</ol>
);

/** Back, the list in a drop-down, forward: which one of its kind the pop-up shows. The drop-down is the app's own, opening inside the pop-up
 *  under its button in columns of ``rows``: Escape or a click outside closes it, the arrows step through it. ``n`` counts from 1. */
function LorePicker({ items, n, onPick, label, rows, plain }: { items: string[]; n: number; onPick: (n: number) => void; label: string; rows: number; plain?: boolean }) {
  const [open, setOpen] = useState(false);
  const box = useRef<HTMLDivElement>(null), list = useRef<HTMLUListElement>(null);
  const [height, setHeight] = useState<number>();
  const count = items.length, cols = Math.ceil(count / rows);
  const step = (by: number) => onPick(((n - 1 + by + count) % count) + 1);
  const pick = (k: number) => { setOpen(false); onPick(k); box.current?.querySelector<HTMLElement>(".lore-pick-btn")?.focus(); };
  useLayoutEffect(() => {
    if (!open) return;
    // no lower than the pop-up's foot, so it never reaches past the pop-up; the open one has the focus
    const end = box.current!.closest("dialog")!.getBoundingClientRect().bottom, top = list.current!.getBoundingClientRect().top;
    setHeight(Math.max(120, end - top - 12));
    list.current!.querySelector<HTMLElement>("[aria-checked=true]")?.focus();
    const away = (e: MouseEvent) => { if (!box.current?.contains(e.target as Node)) setOpen(false); };
    document.addEventListener("mousedown", away);
    return () => document.removeEventListener("mousedown", away);
  }, [open]);
  const keys = (e: React.KeyboardEvent) => {
    const all = Array.from(list.current!.querySelectorAll<HTMLElement>("button")), i = all.indexOf(document.activeElement as HTMLElement);
    const by = { ArrowDown: 1, ArrowUp: -1, ArrowRight: rows, ArrowLeft: -rows }[e.key];
    if (by) { all[(i + by + count) % count]?.focus(); e.preventDefault(); }
    if (e.key === "Escape") { e.preventDefault(); e.stopPropagation(); setOpen(false); box.current?.querySelector<HTMLElement>(".lore-pick-btn")?.focus(); }   // the list, not the pop-up
  };
  return (
    <div className={plain ? "lore-pick plain" : "lore-pick"} ref={box}>
      {!plain && <button type="button" className="icon-btn" aria-label={`Previous: ${items[(n + count - 2) % count]}`} data-tip={items[(n + count - 2) % count]} onClick={() => step(-1)}>‹</button>}
      <button type="button" className="lore-pick-btn" aria-haspopup="menu" aria-expanded={open} aria-label={plain ? `${label}: ${items[n - 1]}` : undefined} onClick={() => setOpen(!open)}>
        {plain ? items[n - 1] : `${n}. ${items[n - 1]}`}<span aria-hidden>▾</span>
      </button>
      {!plain && <button type="button" className="icon-btn" aria-label={`Next: ${items[n % count]}`} data-tip={items[n % count]} onClick={() => step(1)}>›</button>}
      {open && (
        <ul className="menu lore-pick-list" role="menu" aria-label={label} ref={list} onKeyDown={keys}
          style={{ maxHeight: height, gridTemplateRows: `repeat(${rows}, auto)`, gridTemplateColumns: `repeat(${cols}, minmax(${plain ? 7 : 8.5}rem, auto))` }}>
          {items.map((x, i) => (
            <li key={x} role="none">
              <button type="button" role="menuitemradio" aria-checked={i + 1 === n} onClick={() => pick(i + 1)}>
                {!plain && <span className="lore-pick-n">{i + 1}</span>}<span className="label">{x}</span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

// --- names, and the chart a reading is opened in

const GRAHAS = ["Su", "Mo", "Ma", "Me", "Ju", "Ve", "Sa", "Ra", "Ke"];
const GRAHA_NAMES: Record<string, string> = { Su: "Sun", Mo: "Moon", Ma: "Mars", Me: "Mercury", Ju: "Jupiter", Ve: "Venus", Sa: "Saturn", Ra: "Rahu", Ke: "Ketu" };
const GRAHA_LIST = GRAHAS.map((g) => GRAHA_NAMES[g]);
const SIGN_LORDS = ["Ma", "Ve", "Me", "Mo", "Su", "Me", "Ve", "Ma", "Ju", "Sa", "Sa", "Ju"];      // Aries .. Pisces
const NAK_LORDS = ["Ke", "Ve", "Su", "Mo", "Ma", "Ra", "Ju", "Sa", "Me"];                        // Ashwini, Bharani .. and round again
const ORD = ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th", "10th", "11th", "12th"];
const BHAVAS = ["Tanu", "Dhana", "Sahaja", "Bandhu", "Putra", "Ari", "Yuvati", "Randhra", "Dharma", "Karma", "Labha", "Vyaya"];
/** The 27 as the book spells them, for the pop-up's picker. */
const NAKSHATRAS = ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
  "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishtha",
  "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"];
const norm = (lon: number) => ((lon % 360) + 360) % 360;
const signOf = (lon: number) => Math.floor(norm(lon) / 30);                 // 0 Aries .. 11 Pisces
const nakOf = (lon: number) => Math.floor(norm(lon) / (360 / 27)) + 1;      // 1 Ashwini .. 27 Revati
/** 26°04′ Aries */
const degSign = (lon: number) => { const x = norm(lon) % 30, d = Math.floor(x), m = Math.floor((x - d) * 60); return `${d}°${String(m).padStart(2, "0")}′ ${SIGN_NAMES[signOf(lon)]}`; };
const graha = (ab: string) => <Go to={{ kind: "graha", n: ab }}>{GRAHA_NAMES[ab] ?? ab}</Go>;
const list = (xs: ReactNode[]) => xs.flatMap((x, i) => (i ? [i === xs.length - 1 ? " and " : ", ", x] : [x]));

/** The open chart's facts a reading marks: each body's longitude in D-``d``, the grahas' insights (sign, bhava, dignity) and the bhavas
 *  from the Lagna, from the queries the Grahas and Bhavas tabs share. ``d`` 0: no chart. */
function useChartFacts(d = 1) {
  const birth = useChart((s) => s.birth);
  const keyRows = useQuery({ queryKey: ["keyInfo", birth, d || 1], queryFn: () => api.keyInfo(birth!, d || 1), enabled: !!birth && d > 0 });
  const insights = useQuery({ queryKey: ["grahaInsights", birth, 1], queryFn: () => api.grahaInsights(birth!, 1), enabled: !!birth && d > 0 });
  const houses = useQuery({ queryKey: ["houses", birth, 0], queryFn: () => api.houses(birth!, 0), enabled: !!birth && d > 0 });
  return { rows: d > 0 ? keyRows.data : undefined, insights: d > 0 ? insights.data : undefined, houses: d > 0 ? houses.data : undefined };
}

/** A pop-up's tab, kept over a refresh, and a tab saved before the tabs changed taken back to the first. */
function useTab<T extends string>(name: string, tabs: readonly { id: T }[]) {
  const [saved, set] = useKept<string>(name, tabs[0].id);
  return [(tabs.some((t) => t.id === saved) ? saved : tabs[0].id) as T, set] as const;
}

// --- a graha

const GRAHA_TABS = [{ id: "strength", name: "Strengths" }, { id: "glance", name: "At a glance" }, { id: "nature", name: "Nature" }, { id: "signif", name: "Significations" },
  { id: "dignity", name: "Dignity & relations" }, { id: "chart", name: "In a chart" }, { id: "classics", name: "Classics" }] as const;
type GrahaTab = (typeof GRAHA_TABS)[number]["id"];

function GrahaPop({ ab, side, back, swap, onClose }: PopProps & { ab: string }) {
  const q = useQuery({ queryKey: ["grahaLore", ab], queryFn: () => api.grahaLore(ab), staleTime: Infinity });
  const [tab, setTab] = useTab<GrahaTab>("lore.grahaTab", GRAHA_TABS);
  const t = q.data;
  const rows = t?.facts.flatMap((g) => g.rows) ?? [];
  const sub = rows.filter((r) => r.k === "Governs" || r.k === "Cabinet" || r.k === "Nature" && !rows.some((x) => x.k === "Governs")).map((r) => nameAndGloss(r.v)[0]).join(" · ");
  return (
    <LoreDialog side={side} back={back} onClose={onClose} title={t ? (t.sanskrit !== t.name ? `${t.name} · ${t.sanskrit}` : t.name) : "Graha"} sub={sub}
      aside={<LorePicker items={GRAHA_LIST} n={GRAHAS.indexOf(ab) + 1} onPick={(k) => swap({ kind: "graha", n: GRAHAS[k - 1] })} label="Grahas" rows={9} />}
      tabs={<OneRowTabs tabs={GRAHA_TABS} value={tab} onChange={setTab} label="Graha" />}>
      {tab === "strength" ? <GrahaStrengths name={GRAHA_NAMES[ab]} onGo={(name) => swap({ kind: "graha", n: GRAHAS[GRAHA_LIST.indexOf(name)] ?? ab })} />
        : <Loaded q={q}>{(t) => <GrahaBody t={t} tab={tab} />}</Loaded>}
    </LoreDialog>
  );
}

function GrahaBody({ t, tab }: { t: GrahaLore; tab: Exclude<GrahaTab, "strength"> }) {
  const { rows, insights } = useChartFacts(1);
  const me = insights?.find((g) => g.name === t.name), row = rows?.find((r) => r.name === t.name);
  const [part, setPart] = useKept<"bhava" | "aspect" | "rashi" | "nakshatra">("lore.grahaChart", "bhava");
  const id = (x: string) => `g.${t.id}.${x}`;
  const strength = t.facts.filter((g) => g.name === "Strength"), nature = t.facts.filter((g) => g.name !== "Strength");
  const full = me?.aspect_full ?? 60;
  if (tab === "glance") return <>
    <p className="lore-lede">{t.about}</p>
    <Tiles facts={t.facts} />
    {me && row && <Section title="In this chart">
      <p>{t.name} is in <Go to={{ kind: "rashi", n: me.sign_no + 1, d: 1 }}>{me.sign}</Go> ({me.dignity.toLowerCase()}), in the <Go to={{ kind: "bhava", n: me.bhava }}>{supOrd(ORD[me.bhava - 1])} bhava</Go>,
        in <Go to={{ kind: "nakshatra", n: nakOf(row.lon), from: t.id }}>{NAKSHATRAS[nakOf(row.lon) - 1]}</Go> pada {row.pada}{row.retrograde && t.id !== "Ra" && t.id !== "Ke" ? ", retrograde" : ""}{me.combust ? ", combust" : ""}.
        {me.owns.length > 0 && <> It rules the {list(me.owns.map((h) => <Go key={h} to={{ kind: "bhava", n: h }}>{supOrd(ORD[h - 1])}</Go>))}.</>}
        {row.karaka && <> Its chara karaka role is {row.karaka}.</>}</p>
    </Section>}
    <Section title="Strong or afflicted">
      <div className="lore-readings">
        {([["When strong", t.reading.strong, false], ["When weak or afflicted", t.reading.weak, false], ["As the Atmakaraka", t.reading.atmakaraka, row?.karaka === "AK"]] as [string, string, boolean][])
          .map(([k, v, on]) => <div key={k} className={on ? "here" : undefined}><span>{k}</span><p>{v}</p></div>)}
      </div>
    </Section>
    <Section title="What it signifies"><Significations sides={t.significations} id={id("glance")} n={5} /></Section>
  </>;
  if (tab === "nature") return <Facts facts={nature} />;
  if (tab === "signif") return <>
    <Significations sides={t.significations} id={id("signif")} />
    <p className="muted lore-src">{t.source}</p>
  </>;
  if (tab === "dignity") return <>
    <Facts facts={strength} />
    <p className="muted">{t.aspects_note}</p>
    <Section title="Friends, neutrals and enemies">
      <dl className="lore-kv">{([["Friends", t.relations.friends], ["Neutral", t.relations.neutral], ["Enemies", t.relations.enemies]] as [string, string[]][]).map(([k, xs]) => (
        <div key={k}><dt>{k}</dt><dd>{xs.length ? list(xs.map((g) => <span key={g}>{graha(g)}</span>)) : "—"}</dd></div>))}</dl>
    </Section>
    <Section title="It rules">
      <dl className="lore-kv">
        <div><dt>Rashis</dt><dd>{list(t.rules.signs.map((s) => <Go key={s} to={{ kind: "rashi", n: s }}>{SIGN_NAMES[s - 1]}</Go>))}</dd></div>
        <div><dt>Nakshatras</dt><dd>{list(t.rules.nakshatras.map((k) => <Go key={k} to={{ kind: "nakshatra", n: k }}>{NAKSHATRAS[k - 1]}</Go>))}</dd></div>
        <div><dt>Karaka of</dt><dd>{list(t.karaka_of.bphs.map((h) => <Go key={h} to={{ kind: "bhava", n: h }}>{supOrd(`the ${ORD[h - 1]}`)}</Go>))}{t.karaka_of.bphs.length ? " (BPHS)" : "—"}
          {t.karaka_of.phaladeepika.filter((h) => !t.karaka_of.bphs.includes(h)).length > 0 && <>; also {list(t.karaka_of.phaladeepika.filter((h) => !t.karaka_of.bphs.includes(h)).map((h) => <Go key={h} to={{ kind: "bhava", n: h }}>{supOrd(`the ${ORD[h - 1]}`)}</Go>))} (Phaladeepika)</>}</dd></div>
      </dl>
    </Section>
  </>;
  if (tab === "chart") {
    const parts = ([["bhava", "In each bhava"], ["aspect", "Its aspect on each"], ["rashi", "In each rashi"], ["nakshatra", "In each nakshatra"]] as const)
      .filter(([k]) => (k === "rashi" ? t.in_rashi.length : k === "nakshatra" ? t.in_nakshatra.length : true));
    const on = parts.some(([k]) => k === part) ? part : "bhava";
    return <>
      <div className="seg lore-seg" role="tablist" aria-label="Read in">{parts.map(([k, name]) => <button key={k} type="button" role="tab" aria-selected={on === k} onClick={() => setPart(k)}>{name}</button>)}</div>
      {on === "bhava" && <><p className="muted">{t.bhava_note}</p><Rows rows={t.in_bhava.map((x, i) => ({ key: String(i), head: <Go to={{ kind: "bhava", n: i + 1 }}>{supOrd(`In the ${ORD[i]}`)}</Go>, body: x.text, cite: x.source, here: me?.bhava === i + 1 }))} /></>}
      {on === "aspect" && <><p className="muted">{t.aspect_note}</p><Rows rows={t.aspect_on.map((x, i) => ({ key: String(i), head: <Go to={{ kind: "bhava", n: i + 1 }}>{supOrd(`On the ${ORD[i]}`)}</Go>, body: x, here: !!me && me.aspects_houses[i] >= full * 0.75 }))} /></>}
      {on === "rashi" && <Rows rows={t.in_rashi.map((x, i) => ({ key: String(i), head: <Go to={{ kind: "rashi", n: i + 1 }}>{`In ${SIGN_NAMES[i]}`}</Go>, body: x.text, cite: x.source, here: me?.sign_no === i }))} />}
      {on === "nakshatra" && <Rows rows={t.in_nakshatra.map((x, i) => ({ key: String(i), head: <Go to={{ kind: "nakshatra", n: i + 1, from: t.id }}>{`In ${NAKSHATRAS[i]}`}</Go>, body: x, here: !!row && nakOf(row.lon) === i + 1 }))} />}
    </>;
  }
  return <>
    <Section title="BPHS on it"><Quotes items={t.classics} id={id("classics")} /></Section>
    <Section title="BPHS 3 on all the grahas"><Quotes items={t.classics_all} id={id("all")} /></Section>
  </>;
}

// --- a rashi

const RASHI_TABS = [{ id: "glance", name: "At a glance" }, { id: "nature", name: "Nature" }, { id: "signif", name: "Significations" },
  { id: "bhavas", name: "On the bhavas" }, { id: "stars", name: "Nakshatras & grahas" }, { id: "classics", name: "Classics" }] as const;
type RashiTab = (typeof RASHI_TABS)[number]["id"];
const DIGNITY: Record<string, string> = { exalted: "Exalted", debilitated: "Debilitated", moolatrikona: "Moolatrikona", own: "Own sign" };

function RashiPop({ n, d, side, back, swap, onClose }: PopProps & { n: number; d: number }) {
  const q = useQuery({ queryKey: ["rashiLore", n], queryFn: () => api.rashiLore(n), staleTime: Infinity });
  const [tab, setTab] = useTab<RashiTab>("lore.rashiTab", RASHI_TABS);
  const t = q.data;
  const fact = (k: string) => t?.facts.flatMap((g) => g.rows).find((r) => r.k === k)?.v ?? "";
  return (
    <LoreDialog side={side} back={back} onClose={onClose} title={t ? `${t.name} · ${t.sanskrit}` : "Rashi"}
      sub={t && [t.symbol, `ruled by ${nameAndGloss(fact("Lord"))[0]}`, `${nameAndGloss(fact("Modality"))[0].toLowerCase()} ${nameAndGloss(fact("Element"))[0].toLowerCase()}`, `${(n - 1) * 30}°–${n * 30}°`].join(" · ")}
      aside={<LorePicker items={SIGN_NAMES} n={n} onPick={(k) => swap({ kind: "rashi", n: k, d })} label="Rashis" rows={6} />}
      tabs={<OneRowTabs tabs={RASHI_TABS} value={tab} onChange={setTab} label="Rashi" />}>
      <Loaded q={q}>{(t) => <RashiBody t={t} tab={tab} d={d} />}</Loaded>
    </LoreDialog>
  );
}

function RashiBody({ t, tab, d }: { t: RashiLore; tab: RashiTab; d: number }) {
  const { rows, insights, houses } = useChartFacts(d);
  const n = t.n, id = (x: string) => `r.${n}.${x}`;
  // in the chart it was opened from: the bhavas whose cusps it holds (D-1), the grahas in it, its house from the varga's lagna
  const cusps = d === 1 ? (houses ?? []).map((h, i) => [i + 1, h.cusp] as const).filter(([, c]) => signOf(c) === n - 1) : [];
  const here = (rows ?? []).filter((r) => GRAHA_LIST.includes(r.name) && signOf(r.lon) === n - 1);
  const lagna = rows?.find((r) => r.name === "Lagna");
  const fromLagna = lagna ? ((n - 1 - signOf(lagna.lon) + 12) % 12) + 1 : null;
  const lordName = GRAHA_NAMES[t.lord], lordRow = rows?.find((r) => r.name === lordName), lordIns = insights?.find((g) => g.name === lordName);
  const ab = (name: string) => GRAHAS[GRAHA_LIST.indexOf(name)];
  const at1 = (name: string) => d === 1 && rows?.some((r) => r.name === name && signOf(r.lon) === n - 1);
  if (tab === "glance") return <>
    <p className="lore-lede">{t.about}</p>
    <Tiles facts={t.facts} />
    {rows && <Section title={d === 1 ? "In this chart" : `In this chart's D-${d}`}>
      <p>{d === 1 ? (cusps.length ? <>It holds the cusp of the {list(cusps.map(([h, c]) => <span key={h}><Go to={{ kind: "bhava", n: h }}>{supOrd(`${ORD[h - 1]} bhava`)}</Go> ({degSign(c)})</span>))}.</> : <>No bhava's cusp falls in it.</>)
        : fromLagna && <>It is the {supOrd(ORD[fromLagna - 1])} from the D-{d} lagna.</>}
        {" "}{here.length ? <>{list(here.map((r) => <span key={r.name}>{graha(ab(r.name))}</span>))} {here.length > 1 ? "are" : "is"} in it.</> : "No graha is in it."}
        {lordRow && <> Its lord {graha(t.lord)} is in <Go to={{ kind: "rashi", n: signOf(lordRow.lon) + 1, d }}>{SIGN_NAMES[signOf(lordRow.lon)]}</Go>{d === 1 && lordIns ? <>, in the <Go to={{ kind: "bhava", n: lordIns.bhava }}>{supOrd(ORD[lordIns.bhava - 1])} bhava</Go></> : null}.</>}</p>
    </Section>}
    <Section title="In a chart">
      <div className="lore-readings">
        {([["As the Lagna", t.reading.lagna, "Lagna"], ["As the Moon's sign", t.reading.moon, "Moon"], ["As the Sun's sign", t.reading.sun, "Sun"]] as [string, string, string][])
          .map(([k, v, who]) => <div key={k} className={at1(who) ? "here" : undefined}><span>{k}</span><p>{v}</p></div>)}
      </div>
    </Section>
    <div className="lore-pair">
      <Section title="Strengths" tone="good"><Chips items={t.strengths} tone="good" /></Section>
      <Section title="Shadows" tone="bad"><Chips items={t.shadows} tone="bad" /></Section>
    </div>
  </>;
  if (tab === "nature") return <>
    <Facts facts={t.facts} />
    <Section title="Grahas' dignities in it"><Dignities t={t} /></Section>
  </>;
  if (tab === "signif") return <><Significations sides={t.significations} id={id("signif")} /><p className="muted lore-src">{t.source}</p></>;
  if (tab === "bhavas") return <>
    <p className="muted">The rashi on a bhava's cusp colours everything that bhava stands for: its lord rules the bhava, and its nature runs through the bhava's living (jiva) and non-living (ajiva) matters.</p>
    <Rows rows={t.on_bhava.map((r, i) => ({ key: String(i), head: <Go to={{ kind: "bhava", n: i + 1 }}>{supOrd(`On the ${ORD[i]} cusp`)}</Go>, body: <JA r={r} />, here: cusps.some(([h]) => h === i + 1) }))} />
  </>;
  if (tab === "stars") return <>
    <Section title="Its nakshatras">
      <dl className="lore-kv">{t.nakshatras.map((k) => (
        <div key={k.n}><dt><Go to={{ kind: "nakshatra", n: k.n }}>{NAKSHATRAS[k.n - 1]}</Go></dt>
          <dd>{k.padas.length === 4 ? "all four padas" : `pada${k.padas.length > 1 ? "s" : ""} ${k.padas.join(", ")}`} · ruled by {graha(k.lord)}</dd></div>))}</dl>
    </Section>
    <Section title="Grahas' dignities in it"><Dignities t={t} /></Section>
    {t.grahas_in.length > 0 && <Section title="Each graha in it">
      <Rows rows={t.grahas_in.map((x) => ({ key: x.graha, head: graha(x.graha), body: x.text, cite: x.source, here: here.some((r) => ab(r.name) === x.graha) }))} />
    </Section>}
  </>;
  return <>
    <Section title="BPHS on it"><Quotes items={t.classics} id={id("classics")} /></Section>
    <Section title="BPHS 4 on all the rashis"><Quotes items={t.classics_all} id={id("all")} /></Section>
  </>;
}

const Dignities = ({ t }: { t: RashiLore }) => t.dignities.length ? (
  <ul className="lore-points">{t.dignities.map((x, i) => (
    <li key={i}>{graha(x.graha)}: {DIGNITY[x.kind]}{Array.isArray(x.deg) ? ` from ${x.deg[0]}° to ${x.deg[1]}°` : x.deg != null ? `, deepest at ${x.deg}°` : ""}</li>))}</ul>
) : <p className="muted">No graha is exalted, debilitated or at home here.</p>;

// --- a bhava, read for the chart

const BHAVA_TABS = [{ id: "reading", name: "Reading" }, { id: "signif", name: "Significations" }, { id: "about", name: "About" },
  { id: "all", name: "Every sign & star" }, { id: "classics", name: "Classics" }] as const;
type BhavaTab = (typeof BHAVA_TABS)[number]["id"];
const KIND: Record<string, string> = { rashi: "The rashi on its cusp", nakshatra: "Its cusp's nakshatra", lord: "Its lord", occupant: "A graha in it", aspect: "An aspect on it", karaka: "Its karaka" };

function BhavaPop({ n, base, side, back, swap, onClose }: PopProps & { n: number; base: number }) {
  const birth = useChart((s) => s.birth)!;
  const q = useQuery({ queryKey: ["bhavaReading", birth, n, base], queryFn: () => api.bhavaReading(birth, n, base), placeholderData: (p) => p });
  const lore = useQuery({ queryKey: ["bhavaLore", n], queryFn: () => api.bhavaLore(n), staleTime: Infinity });
  const [tab, setTab] = useTab<BhavaTab>("lore.bhavaTab", BHAVA_TABS);
  const r = q.data && q.data.house === n ? q.data : undefined;
  return (
    <LoreDialog side={side} back={back} onClose={onClose} title={supOrd(`${ORD[n - 1]} bhava · ${BHAVAS[n - 1]}`)}
      sub={r && <>Cusp {degSign(r.cusp)} · {r.nakshatra.name} pada {r.nakshatra.pada} · from {r.from}</>}
      aside={<LorePicker items={BHAVAS} n={n} onPick={(k) => swap({ kind: "bhava", n: k, ref: base })} label="Bhavas" rows={6} />}
      tabs={<OneRowTabs tabs={BHAVA_TABS} value={tab} onChange={setTab} label="Bhava" />}>
      <Loaded q={q}>{() => r ? <BhavaBody r={r} lore={lore.data} tab={tab} /> : <p className="muted">Reading…</p>}</Loaded>
    </LoreDialog>
  );
}

function BhavaBody({ r, lore, tab }: { r: BhavaReading; lore?: BhavaLore; tab: BhavaTab }) {
  const n = r.house, id = (x: string) => `b.${n}.${x}`;
  const w = (x: { bhava: number; sign: number; sign_name: string; dignity: string }) =>
    <>in the {supOrd(ORD[x.bhava - 1])}, <Go to={{ kind: "rashi", n: x.sign }}>{x.sign_name}</Go> · {x.dignity.toLowerCase()}</>;
  if (tab === "reading") {
    const tiles: [string, ReactNode][] = [
      ["Rashi", <><b><Go to={{ kind: "rashi", n: r.sign }}>{r.sign_name}</Go></b><small>{r.span.map((p) => `${p.percent}% ${p.name}`).join(" · ")} of the bhava</small></>],
      ["Lord", <><b>{graha(r.lord.graha)}</b><small>{w(r.lord)}{r.lord.retro ? " · retrograde" : ""}{r.lord.combust ? " · combust" : ""}{r.lord.co && <> · {graha(r.lord.co)} co-lord</>}</small></>],
      ["Cusp", <><b>{degSign(r.cusp)}</b><small>{degSign(r.start)} to {degSign(r.end)}</small></>],
      ["Nakshatra", <><b><Go to={{ kind: "nakshatra", n: r.nakshatra.n }}>{r.nakshatra.name}</Go> {r.nakshatra.pada}</b><small>star lord {graha(r.nakshatra.lord)} in the {supOrd(ORD[r.nakshatra.lord_bhava - 1])} · sub lord {graha(r.nakshatra.sub_lord)}</small></>],
      ["Grahas in it", r.occupants.length ? <><b>{list(r.occupants.map((o) => <span key={o.graha}>{graha(o.graha)}</span>))}</b><small>{r.occupants.map((o) => o.dignity.toLowerCase()).join(" · ")}</small></> : <b className="muted">None</b>],
      ["Bhava Bala", r.bala ? <><b>{Math.round(r.bala.percent)}%</b><small>{r.bala.rupas.toFixed(2)} of the 7 rupas a bhava needs</small></> : <><b className="muted">—</b><small>read for the Lagna's bhavas</small></>],
      ["Sarva bindus", <><b>{r.sav}</b><small>in {r.sign_name}; 28 is the average</small></>],
      ["Karaka", <><b>{list(r.karakas.map((k) => <span key={k.graha}>{graha(k.graha)}</span>))}</b><small>{r.karakas.map((k) => (k.in_it ? "in it" : `in the ${ORD[k.bhava - 1]}`)).join(" · ")}</small></>],
    ];
    return <>
      <div className="lore-tiles">{tiles.map(([k, v]) => <div key={k}><span>{k}</span>{v}</div>)}</div>
      <Section title={<>Does it prosper? <small>{r.verdict.word}: {r.verdict.good} for, {r.verdict.bad} against · BPHS 11.14-16</small></>}>
        <ul className="lore-checks">{r.checks.map((c, i) => <li key={i} className={c.good ? "good" : "bad"}>{c.text}{c.source && <small className="lore-cite">{c.source}</small>}</li>)}</ul>
      </Section>
      {r.aspects.length > 0 && <Section title={<>Aspects on its cusp <small>virupas of {r.full}</small></>}>
        <ul className="g-bars lore-bars">{r.aspects.map((a) => (
          <li key={a.graha} className={a.benefic ? "good" : "bad"}><span>{graha(a.graha)}</span><span className="g-bar"><i style={{ width: `${Math.min(100, (a.value / r.full) * 100)}%` }} /></span><b>{a.value}</b></li>))}</ul>
      </Section>}
      <Section title="The reading">
        {r.parts.map((p, i) => (
          <article key={i} className={`lore-sec lore-note${p.tone ? ` tone-${p.tone}` : ""}`}>
            <span className="g-kicker">{KIND[p.kind]}</span>
            <h3>{supOrd(p.head)}</h3>
            {p.jiva !== undefined ? <JA r={{ jiva: p.jiva, ajiva: p.ajiva ?? "" }} /> : p.text && <p>{supOrd(p.text)}</p>}
            {p.notes.length > 0 && <ul className="lore-points">{p.notes.map((x, j) => <li key={j}>{supOrd(x)}</li>)}</ul>}
            <p className="muted lore-src">{p.source}{p.source && " · "}<Go to={p.link}>All about {p.link.kind === "graha" ? GRAHA_NAMES[String(p.link.n)] : p.link.kind === "rashi" ? SIGN_NAMES[Number(p.link.n) - 1] : NAKSHATRAS[Number(p.link.n) - 1]}</Go></p>
          </article>
        ))}
      </Section>
    </>;
  }
  const rashi = r.parts.find((p) => p.kind === "rashi"), star = r.parts.find((p) => p.kind === "nakshatra");
  if (tab === "signif") return <>
    <p className="muted">What the {supOrd(ORD[n - 1])} bhava stands for, living (jiva) and non-living (ajiva), and how this chart's rashi and nakshatra on its cusp colour each side.</p>
    <Significations sides={r.significations} id={id("signif")} extra={Object.fromEntries((["jiva", "ajiva"] as const).map((k) => [k, <div key={k} className="lore-colour">
      {rashi && <p><span className="g-kicker">{r.sign_name} on the cusp</span>{rashi[k]}</p>}
      {star && <p><span className="g-kicker">{r.nakshatra.name} on the cusp</span>{star[k]}</p>}
    </div>]))} />
  </>;
  if (!lore) return <p className="muted">Reading…</p>;
  if (tab === "about") return <>
    <p className="lore-lede">{lore.about}</p>
    <Facts facts={lore.facts} />
    <Section title="Strong or afflicted">
      <div className="lore-readings">{([["When strong", lore.reading.strong], ["When afflicted", lore.reading.weak]] as [string, string][]).map(([k, v]) => <div key={k}><span>{k}</span><p>{v}</p></div>)}</div>
    </Section>
    <Section title={<>Its lord in each bhava <small>BPHS 24</small></>}>
      <Rows rows={lore.lords.from.map((x) => ({ key: String(x.house), head: <Go to={{ kind: "bhava", n: x.house }}>{supOrd(`In the ${ORD[x.house - 1]}`)}</Go>, body: x.text, cite: x.source, here: r.lord.bhava === x.house }))} />
    </Section>
    <Section title={<>Each bhava's lord in it <small>BPHS 24</small></>}>
      <Rows rows={lore.lords.into.map((x) => ({ key: String(x.lord), head: <Go to={{ kind: "bhava", n: x.lord }}>{supOrd(`The ${ORD[x.lord - 1]} lord`)}</Go>, body: x.text, cite: x.source }))} />
    </Section>
  </>;
  if (tab === "all") return <>
    <p className="muted">The template this bhava is read from: every rashi and every nakshatra on its cusp, every graha in it and every graha's aspect on it. This chart's are marked.</p>
    <Section title="Each rashi on its cusp"><Rows rows={lore.on_cusp.rashis.map((x, i) => ({ key: String(i), head: <Go to={{ kind: "rashi", n: i + 1 }}>{SIGN_NAMES[i]}</Go>, body: <JA r={x} />, here: r.sign === i + 1 }))} /></Section>
    <Section title="Each nakshatra on its cusp"><Rows rows={lore.on_cusp.nakshatras.map((x, i) => ({ key: String(i), head: <Go to={{ kind: "nakshatra", n: i + 1 }}>{NAKSHATRAS[i]}</Go>, body: <JA r={x} />, here: r.nakshatra.n === i + 1 }))} /></Section>
    <Section title={<>Each graha in it <small>Phaladeepika 8</small></>}><Rows rows={lore.grahas_in.map((x) => ({ key: x.graha, head: graha(x.graha), body: x.text, cite: x.source, here: r.occupants.some((o) => o.graha === x.graha) }))} /></Section>
    <Section title="Each graha's aspect on it"><Rows rows={lore.aspects_on.map((x) => ({ key: x.graha, head: graha(x.graha), body: x.text, here: r.aspects.some((a) => a.graha === x.graha && a.value >= r.full * 0.75) }))} /></Section>
  </>;
  return <>
    <Section title="BPHS on it"><Quotes items={lore.classics} id={id("classics")} /></Section>
    <Section title="How a bhava prospers or fails"><Quotes items={lore.judge} id={id("judge")} /></Section>
    <Section title="The bhavas' karakas and kinds"><Quotes items={lore.karaka_slokas} id={id("karakas")} /></Section>
  </>;
}

// --- a nakshatra

const NAK_TABS = [{ id: "glance", name: "At a glance" }, { id: "nature", name: "Nature" }, { id: "traits", name: "Traits" }, { id: "padas", name: "Padas & Moon" },
  { id: "signif", name: "Significations" }, { id: "bhavas", name: "On the bhavas" }, { id: "scripture", name: "Scripture & stories" }] as const;
type NakTab = (typeof NAK_TABS)[number]["id"];

/** Nakshatra ``n`` (1 Ashwini .. 27 Revati) (data/lore/nakshatras.json). At a glance: what rules it, its nature in a word each, strengths
 *  beside shadows, what the Moon's transit of it favours beside what to avoid, its work and places; then a tab each for the whole of its
 *  nature, traits, padas, what it signifies (living and non-living), its reading on each bhava's cusp and its scriptures, every long
 *  passage cut to its first sentence. ``graha``: the graha that opened it (its notes from the book come first), "La" for the Lagna; the
 *  Lagna's, the Moon's or the Sun's reading is marked by it. The tab, and what was opened past its first part, are kept over a refresh. */
function NakshatraPop({ n, graha: from, side, back, swap, onClose }: PopProps & { n: number; graha?: string }) {
  const q = useQuery({ queryKey: ["nakshatraLore", n], queryFn: () => api.nakshatraLore(n), staleTime: Infinity });
  const [tab, setTab] = useTab<NakTab>("lore.nakshatraTab2", NAK_TABS);
  const t = q.data;
  return (
    <LoreDialog side={side} back={back} onClose={onClose} title={t ? `${t.name} nakshatra` : "Nakshatra"}
      sub={t && t.range.replace(/\s*\(Sidereal\)/, "")}
      aside={<LorePicker items={NAKSHATRAS} n={n} onPick={(k) => swap({ kind: "nakshatra", n: k })} label="Nakshatras" rows={9} />}
      tabs={<OneRowTabs tabs={NAK_TABS} value={tab} onChange={setTab} label="Nakshatra" />}>
      <Loaded q={q}>{(t) => <NakshatraBody t={t} tab={tab} graha={from} />}</Loaded>
    </LoreDialog>
  );
}

function NakshatraBody({ t, tab, graha: from }: { t: NakshatraLore; tab: NakTab; graha?: string }) {
  const { houses } = useChartFacts(1);
  const id = (part: string) => `${t.n}.${part}`;
  const tree = t.tree.botanical && `${t.tree.names} (${t.tree.botanical})`;
  // the facts in groups, each value a name and its gloss
  const groups: [string, [string, string][]][] = [
    ["What rules it", [["Ruler", t.ruler], ["Deity", t.deity.name], ["Shakti", t.shakti], ["Symbol", t.symbol]]],
    ["Temperament", [["Gana", t.gana], ["Guna", t.guna], ["Dosha", t.dosha], ["Element", t.element], ["Quality", t.quality], ["Activity", t.activity], ["Motivation", t.motivation]]],
    ["Body and bearing", [["Body", t.body], ["Animal (yoni)", t.yoni], ["Caste", t.caste], ["Orientation", t.orientation], ["Direction", t.direction], ["Colour", t.color]]],
    ["In nature", [["Tree", tree && (t.tree.alt ? `${tree}; also ${t.tree.alt}` : tree)], ["Lunar month", t.lunar_month], ["Tithi", t.tithi], ["Sounds", t.sounds]]],
  ];
  const notes = Object.entries(t.grahas).sort(([a], [b]) => (a === from ? -1 : b === from ? 1 : 0));
  const here = from ? t.grahas[from] : undefined;
  // how it reads as the Lagna's, the Moon's and the Sun's nakshatra; the one that opened the pop-up marked
  const readings: [string, string, boolean][] = [["As the Lagna's nakshatra", t.reading.lagna, from === "La"],
    ["As the Moon's (janma) nakshatra", t.reading.moon, from === "Mo"], ["As the Sun's nakshatra", t.reading.sun, from === "Su"]];
  const cusps = (houses ?? []).map((h, i) => [i + 1, h.cusp] as const).filter(([, c]) => nakOf(c) === t.n).map(([h]) => h);     // the chart's bhavas whose cusp is in it
  if (tab === "glance") return <>
    <p className="lore-lede">{t.reading.about}</p>
    {t.meaning && <p className="muted">{t.meaning}</p>}
    <div className="lore-tiles">
      {([["Ruler", t.ruler], ["Deity", t.deity.name], ["Symbol", t.symbol], ["Animal", t.yoni], ["Gana", t.gana], ["Guna", t.guna], ["Element", t.element], ["Shakti", t.shakti]] as [string, string][])
        .filter(([, v]) => v).map(([k, v]) => <div key={k}><span>{k}</span><Value v={v} /></div>)}
    </div>
    {here && here.length > 0 && <Section title={`${GRAHA_NAMES[from!] ?? from} in ${t.name}`}><Points items={here} id={id("here")} /></Section>}
    <Section title="In a chart">
      <div className="lore-readings">
        {readings.map(([k, v, on]) => <div key={k} className={on ? "here" : undefined}><span>{k}</span><p>{v}</p></div>)}
      </div>
      {cusps.length > 0 && <p>In this chart it holds the cusp of the {list(cusps.map((h) => <Go key={h} to={{ kind: "bhava", n: h }}>{supOrd(`${ORD[h - 1]} bhava`)}</Go>))}.</p>}
    </Section>
    <div className="lore-pair">
      <Section title="Strengths" tone="good"><SomeChips items={t.strengths.items} tone="good" n={8} id={id("glance.strengths")} /></Section>
      <Section title="Shadows" tone="bad"><SomeChips items={t.weaknesses.items} tone="bad" n={8} id={id("glance.shadows")} /></Section>
    </div>
    <div className="lore-pair">
      <Section title="Moon here: good for" tone="good"><SomeChips items={t.moon_good.items} tone="good" n={6} id={id("glance.moon_good")} /></Section>
      <Section title="Moon here: avoid" tone="bad"><SomeChips items={t.moon_bad.items} tone="bad" n={6} id={id("glance.moon_bad")} /></Section>
    </div>
    <div className="lore-pair">
      <Section title="Work"><SomeChips items={t.careers.items} n={8} id={id("glance.careers")} /></Section>
      <Section title="Places"><SomeChips items={t.places.items} n={6} id={id("glance.places")} /></Section>
    </div>
  </>;
  if (tab === "nature") return <>
    {t.root && <p className="muted">Root: {t.root}</p>}
    <div className="lore-pair">
      {groups.map(([title, rows]) => (
        <Section key={title} title={title}>
          <dl className="lore-kv">{rows.filter(([, v]) => v).map(([k, v]) => <div key={k}><dt>{k}</dt><dd><Value v={v} /></dd></div>)}</dl>
        </Section>
      ))}
    </div>
    <Section title="Key points"><Points items={t.key_points} id={id("key")} /></Section>
  </>;
  if (tab === "traits") return <>
    <div className="lore-pair">
      <Section title="Strengths" tone="good"><Chips items={t.strengths.items} tone="good" /><Points items={t.strengths.notes} id={id("strengths")} /></Section>
      <Section title="Shadows" tone="bad"><Chips items={t.weaknesses.items} tone="bad" /></Section>
    </div>
    {t.weaknesses.notes.length > 0 && <Section title="The shadow side" tone="bad"><Points items={t.weaknesses.notes} id={id("shadows")} /></Section>}
    <Section title="Important themes"><Points items={t.themes} id={id("themes")} /></Section>
    {notes.length > 0 && <Section title="Grahas in this nakshatra">{notes.map(([g, xs]) => <div key={g} className={g === from ? "lore-graha here" : "lore-graha"}><b>{GRAHA_NAMES[g] ?? g}</b><Points items={xs} id={id(`graha.${g}`)} /></div>)}</Section>}
    {t.grahas_in.length > 0 && <Section title="Each graha in it"><Rows rows={t.grahas_in.map((x) => ({ key: x.graha, head: graha(x.graha), body: x.text, here: x.graha === from }))} /></Section>}
  </>;
  if (tab === "padas") return <>
    <div className="lore-padas">
      {t.pada_facts.map((p) => (
        <div key={p.pada}>
          <span className="g-kicker">Pada {p.pada}</span>
          <b>{p.sign}</b>
          <small>navamsa lord {p.lord} · {p.aim} · sound “{SYLLABLES[(t.n - 1) * 4 + p.pada - 1]}”</small>
          {(p.vargottama || p.pushkara) && <small className="lore-flag">{[p.vargottama && "Vargottama", p.pushkara && "Pushkara navamsa"].filter(Boolean).join(" · ")}</small>}
        </div>
      ))}
    </div>
    {t.dignities.length > 0 && <p>{t.dignities.map((x) => `${GRAHA_NAMES[x.graha]}'s deepest ${x.kind === "exalted" ? "exaltation" : "debilitation"} is here, in pada ${x.pada}`).join("; ")}.</p>}
    {(t.padas.exalted.length > 0 || t.padas.debilitated.length > 0) && <dl className="lore-kv">
      <div><dt>Exalted in its padas’ navamsas</dt><dd className="v-good">{t.padas.exalted.join(" ") || "—"}</dd></div>
      <div><dt>Debilitated there</dt><dd className="v-bad">{t.padas.debilitated.join(" ") || "—"}</dd></div>
    </dl>}
    <div className="lore-pair">
      <Section title="While the Moon transits it: favourable" tone="good"><Chips items={t.moon_good.items} tone="good" /><Points items={t.moon_good.notes} id={id("moon_good")} /></Section>
      <Section title="While the Moon transits it: avoid" tone="bad"><Chips items={t.moon_bad.items} tone="bad" /><Points items={t.moon_bad.notes} id={id("moon_bad")} /></Section>
    </div>
  </>;
  if (tab === "signif") return <>
    <Significations sides={t.significations} id={id("signif")} n={16} />
    {t.famous.length > 0 && <Section title="Famous people"><dl className="lore-kv">{t.famous.map((f) => <div key={f.placement}><dt>{f.placement} here</dt><dd>{f.people.join(", ")}</dd></div>)}</dl></Section>}
  </>;
  if (tab === "bhavas") return <>
    <p className="muted">The nakshatra a bhava's cusp falls in gives the bhava's matters its own colour: its deity's gift, its shakti and its temperament. Its lord, the cusp's star lord, carries the bhava's results to the bhava it sits in.</p>
    <Rows rows={t.on_bhava.map((r, i) => ({ key: String(i), head: <Go to={{ kind: "bhava", n: i + 1 }}>{supOrd(`On the ${ORD[i]} cusp`)}</Go>, body: <JA r={r} />, here: cusps.includes(i + 1) }))} />
  </>;
  return <>
    {t.scriptures.length > 0 && <Section title="From the scriptures">{t.scriptures.map((s, i) => <blockquote key={i}><p>“<Brief text={s.text} id={id(`scripture.${i}`)} n={2} />”</p><cite>{s.source}</cite></blockquote>)}</Section>}
    {t.deity.text && <Section title={`Deity · ${t.deity.name}`}><p><Brief text={t.deity.text} id={id("deity")} n={2} /></p></Section>}
    {t.animal.text && <Section title={`Sacred animal · ${t.animal.name}`}><p><Brief text={t.animal.text} id={id("animal")} n={2} /></p></Section>}
    {t.symbol_text && <Section title={`Symbol · ${t.symbol_text.name}`}><p><Brief text={t.symbol_text.text} id={id("symbol")} n={2} /></p></Section>}
    {t.ganesha.text && <Section title={`Ganesha · ${t.ganesha.form || "his form"}`}><p><Brief text={t.ganesha.text} id={id("ganesha")} n={2} /></p></Section>}
    {t.stars && <Section title="Yoga taras (stars)"><p>{t.stars}</p></Section>}
    {t.other_names.length > 0 && <Section title="Other names"><p className="muted">{t.other_names.join(", ")}</p></Section>}
    {t.myths.map((m, i) => <Section key={i} title={m.title ? `Story · ${m.title}` : "Story"}><p><Brief text={m.text} id={id(`myth.${i}`)} n={2} /></p></Section>)}
    {t.abhijit && <Section title="Abhijit">{t.abhijit.text.map((p, i) => <p key={i}><Brief text={p} id={id(`abhijit.${i}`)} n={2} /></p>)}</Section>}
  </>;
}
