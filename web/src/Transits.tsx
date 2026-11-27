import { Fragment, useEffect, useRef, useState } from "react";
import { useInfiniteQuery, useMutation, useQuery } from "@tanstack/react-query";
import { api, type AheadEvent, type Birth, type CalendarRow, type CorrelationRow, type DomainAhead, type LoreNote } from "./api";
import { formatLon, timeLeft } from "./format";
import { keep, useBasics, useKept, useSaved } from "./hooks";
import { MixedChart } from "./Mixed";
import { Jamakkol, JamakkolLeft, useJamakkolCast } from "./Jamakkol";
import { AngularReturn, CastButton, ChartPanes, ModeCard, ModeLinks, Prasna, Progressions, TithiPravesha, useFind, useMoment } from "./Modes";
import { Tajaka } from "./Tajaka";
import { useChart, type Display } from "./store";
import { CopyButton, Loaded, OneRowTabs, Retro, SubTabs, supOrd, tableText } from "./ui";
import { DIVISIONS, DivisionSelect, STARS } from "./Windows";
import { LoreDialog, openLore } from "./Lore";
import { useMenu, type MenuEntry } from "./Menu";
import { Meter } from "./Lab";
import { verdict } from "./tone";
import { Icon } from "./Icons";
import { Inspector, LeftCharts } from "./Starlight";
import { Stepper } from "./TopBar";
import { TRANSIT_CHAKRAS, TransitChakra } from "./Chakras";

const BODIES = ["Lagna", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"];
const SIGN_NAMES = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"];

/** A search whose result a refresh keeps, for the natal chart it was worked out for (another chart shows nothing). */
function useKeptRun<T>(name: string, run: () => Promise<T>) {
  const natal = useChart((s) => s.natal);
  const [kept, setKept] = useKept<{ natal: unknown; data: T } | null>(name, null);
  const m = useMutation({ mutationFn: run, onSuccess: (data) => setKept({ natal, data }) });
  const same = kept !== null && JSON.stringify(kept.natal) === JSON.stringify(natal);
  return { ...m, data: m.data ?? (same ? kept.data : undefined) };
}

const day = (iso: string) => new Date(iso).toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" });
const at = (iso: string) => iso.replace("T", " ");      // the exact moment, for a hover label
const ms = (iso: string) => Date.parse(`${iso}:00Z`);
const fromNow = (iso: string, now: string) => { const d = ms(iso) - ms(now); return d >= 0 ? `in ${timeLeft(d)}` : `${timeLeft(-d)} ago`; };
/** Of a run of moments, the one to show: the next to come, else the last gone. */
const pickMoment = (m: { when: string; past: boolean }[]) => m.find((x) => !x.past) ?? m[m.length - 1];
const CONTACT = { on: "on", opposite: "opposite", aspect: "aspects" } as const;

const NOT_CAST = "— Not yet cast";

/** The Transit Calendar's items and their short names in its cells. */
const ITEMS: [string, string][] = [["moon", "Bhavas from natal Moon and vedhas"], ["lagna", "Bhavas from natal lagna and vedhas"], ["tara", "Transit taras (stars)"],
  ["murthi", "Murthis (idol/form)"], ["av", "Ashtakavarga scores"], ["kakshya", "Kakshya details"]];
const SHORT: Record<string, string> = { moon: "Mo", lagna: "Lg", tara: "Tara", murthi: "Murthi", av: "AV/SAV", kakshya: "Kak" };

/** Starlight's Home: the natal and transit charts' birth details as Overview shows them, in one full-width box with a column each.
 *  ``menu`` heads its right-click menu, over the birth details' own; ``cast`` false: the transit column says it is not cast yet. */
function TransitInfo({ menu, cast }: { menu: MenuEntry[]; cast: boolean }) {
  const { natal, name } = useChart();
  const transit = useBasics();
  const natalB = useQuery({ queryKey: ["basics", natal, name], queryFn: () => api.basics(natal!, name), enabled: !!natal, placeholderData: (p) => p });
  const { open, node } = useMenu();
  const column = (title: string, b: typeof transit | null) => (
    <div>
      <header className="pane-head"><h2>{title}</h2></header>
      {!b ? <p className="muted pad">{NOT_CAST}</p> : b.data ? <Inspector b={b.data} menu={menu} /> : <p className="muted pad">Calculating…</p>}
    </div>
  );
  return (
    <div className="finder"><section className="pane star-inspector transit-info" onContextMenu={(e) => { if (e.defaultPrevented) return; e.preventDefault(); open(e, menu, "Home"); }}>
      {column("Natal Chart", natalB)}{column("Transit Chart", cast ? transit : null)}{node}
    </section></div>
  );
}

/** Starlight, beside the cast form: what the box under it shows, a button each, two across in four rows; the full name on hover. Home, then
 *  the transit lists by their keys in server/transits.py, Ashtakavarga with the Kakshyas list under it in the same box (ALSO),
 *  then the Transit Calendar (Outlook), which in Starlight is this view, not a sub tab, and the Chakras (ChakrasView), whose wheel takes the
 *  left half. The special nakshatra lists, whose counts are modern teaching (their notes say whose), are the Windows layout's only. */
const VIEWS: [string, string, string][] = [
  ["home", "Home", "The natal and transit charts' birth details"],
  ["standard", "Murthi", "Standard: tara, murthi and vedha"],
  ["houses", "Bhavas", "Bhavas from the natal lagna and Moon"],
  ["ashtakavarga", "Ashtakavarga", "Ashtakavarga scores and the kakshya lord's bindu, then the kakshya each graha is in"],
  ["latta", "Latta", "Latta: the nakshatra each graha kicks"],
  ["anga_graha", "Anga graha", "Anga graha: the limb each graha transits, from the natal Moon, lagna and Sun"],
  ["calendar", "Transit Calendar", "Each graha's transit in a domain's chart (D1 Self, D10 Career…), now and coming up; or day by day"],
  ["chakras", "Chakras", "The transit in a chakra (Sarvatobhadra, Kota, Kalachakra, Tripataki, Kurma…), drawn in the left half"],
];
const VIEW_KEYS = new Set(VIEWS.map(([k]) => k));
const ALSO: Record<string, string[]> = { ashtakavarga: ["kakshya"] };
/** A kept view since folded into another (Kakshya into Ashtakavarga, Domain into the Transit Calendar), or not in Starlight (the special
 *  nakshatra lists): Home. */
const viewOf = (k: string) => (VIEW_KEYS.has(k) ? k : k === "kakshya" ? "ashtakavarga" : k === "domain" ? "calendar" : "home");

/** A date cell: the date, how far from now under it (and ``to``, the house it moves into then); past ones muted, the row's next to come bold, the exact time on hover. */
function When({ m, now, next, to }: { m?: { when: string; past: boolean }; now: string; next?: string; to?: string }) {
  if (!m) return <td className="muted">—</td>;
  return <td className={m.past ? "past" : m.when === next ? "next" : undefined} data-tip={at(m.when)}>{day(m.when)}<small>{fromNow(m.when, now)}{to && <> → {supOrd(to)}</>}</small></td>;
}

const ORD = ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th", "10th", "11th", "12th"];
const KIND: Record<LoreNote["kind"], string> = { house: "The house", moon: "From the Moon · classical", lord: "Lordship · BPHS", karaka: "Karaka", nakshatra: "Nakshatra" };

const MODES = [{ id: "outlook", name: "Outlook" }, { id: "days", name: "Day by day" }] as const;
const YEARS = [{ id: "1", name: "1 year" }, { id: "2", name: "2 years" }, { id: "5", name: "5 years" }, { id: "10", name: "10 years" }] as const;

/** Starlight's Transit Calendar, the Transits view under the cast form once a transit is cast: the transit read in a domain's chart (D1 Self,
 *  D10 Career…), graha by graha now (DomainBody) and what is coming (Ahead); or, by its toggle, the same chart and span day by day (DayByDay).
 *  The bar over them stays put while they scroll: the toggle, the domain (the box's right-click menu has it too; its hover label says what
 *  the houses are counted from) and how far ahead to look, each kept over a refresh and the same in both. */
function Outlook() {
  const { natal, birth } = useChart();
  const [view, setView] = useKept<"outlook" | "days">("transit.calendar.view", "outlook");
  const [kept, setDomain] = useKept("transit.domain", 1);
  const [years, setYears] = useKept("transit.ahead.years", 2);
  const tiles = useQuery({ queryKey: ["transitDomains", natal, birth], queryFn: () => api.transitDomains(natal!, birth!), placeholderData: (p) => p });
  // a kept domain since dropped (D60), or the 0 that once meant Home, opens the first
  const d = tiles.data && !tiles.data.some((x) => x.d === kept) ? tiles.data[0]?.d ?? 1 : kept || 1;
  const tile = tiles.data?.find((x) => x.d === d);
  const head = useQuery(domainQuery(natal, birth, d)).data;      // what the houses are counted from, for the domain's hover label
  const tip = [tile?.meaning, head && `Houses from the D${head.d} lagna (${head.lagna}); key ${head.houses.join(", ")}${tile?.karakas.length ? `; karaka ${tile.karakas.join(" ")}` : ""}.`]
    .filter(Boolean).join(" ");
  const { open, node } = useMenu();
  const menu = (e: React.MouseEvent) => {
    if (!tiles.data) return;
    e.preventDefault();
    open(e, tiles.data.map((t) => ({ label: `D${t.d} · ${t.name}`, checked: t.d === d, title: t.meaning, onClick: () => setDomain(t.d) })), "Domain");
  };
  return (
    <div className="finder"><section className="pane domain-timeline" onContextMenu={menu}>
      {node}
      <div className="outlook-bar">
        <SubTabs tabs={[...MODES]} value={view} onChange={setView} label="Transit Calendar view" />
        <select aria-label="Domain" value={d} data-tip={tip || undefined} onChange={(e) => setDomain(Number(e.target.value))}>
          {(tiles.data ?? [{ d, name: tile?.name ?? "" }]).map((t) => <option key={t.d} value={t.d}>D{t.d} · {t.name}</option>)}
        </select>
        <SubTabs tabs={[...YEARS]} value={String(years) as (typeof YEARS)[number]["id"]} onChange={(y) => setYears(Number(y))} label="How far ahead" />
      </div>
      {view === "days" ? <DayByDay d={d} years={years} /> : <DomainBody d={d} years={years} toDays={() => setView("days")} />}
    </section></div>
  );
}

const domainQuery = (natal: Birth | null, birth: Birth | null, d: number) =>
  ({ queryKey: ["transitDomain", natal, birth, d], queryFn: () => api.transitDomain(natal!, birth!, d), placeholderData: <T,>(p: T) => p });

const DAYS = 92;     // a page of Day by day: three months, ~0.1 s on the server
const ITEMS_ALL = ITEMS.map(([k]) => k);
const SHORT_TIP: Record<string, string> = { moon: "The house from the natal Moon; good, or obstructed (vedha), by the classical count", lagna: "The house from the natal lagna",
  tara: "The tara: its star counted from the natal Moon's", murthi: "Its murthi (form) from the natal Moon when it entered the sign: Swarna, Rajata, Taamra, Loha",
  av: "Its own ashtakavarga bindus in the sign / the sign's total", kakshya: "The lord of the kakshya (eighth of the sign) it is in" };

/** The Outlook's Day by day: the Transit Calendar (every item of it) in the domain's chart, a row a day from the transit moment over
 *  the chosen years; it loads three months at a time as it scrolls. A graha's sign on the day it changes is marked. */
function DayByDay({ d, years }: { d: number; years: number }) {
  const { natal, birth } = useChart();
  const total = Math.round(years * 365.25);
  const q = useInfiniteQuery({
    queryKey: ["transitDays", natal, birth, d, total],
    queryFn: ({ pageParam }) => api.calendar(natal!, birth!, 1, Math.min(DAYS, total - pageParam), ITEMS_ALL, d, d, pageParam),
    initialPageParam: 0,
    getNextPageParam: (_last, pages) => (pages.length * DAYS < total ? pages.length * DAYS : undefined),
  });
  const end = useRef<HTMLParagraphElement>(null);
  const { hasNextPage, isFetchingNextPage, fetchNextPage } = q;
  useEffect(() => {
    if (!end.current || !hasNextPage) return;
    const io = new IntersectionObserver(([e]) => { if (e.isIntersecting && !isFetchingNextPage) fetchNextPage(); }, { rootMargin: "400px" });
    io.observe(end.current);
    return () => io.disconnect();
  }, [hasNextPage, isFetchingNextPage, fetchNextPage, q.data?.pages.length]);
  if (q.isError) return <p role="alert" className="error banner">{q.error.message}</p>;
  if (!q.data) return <p className="muted pad">Calculating…</p>;
  const rows = q.data.pages.flat();
  const grahas = BODIES.slice(1);
  return (
    <div className="scroll">
      <table className="points wrap calendar days">
        <thead><tr><th>Date</th>{grahas.map((p) => <th key={p}>{p.slice(0, 2)}</th>)}</tr></thead>
        <tbody>{rows.map((r, i) => {
          const date = new Date(r.when);
          return (
            <tr key={r.when}>
              <td className="num" data-tip={r.when.slice(0, 16).replace("T", " ")}>{date.toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" })}
                <small>{date.toLocaleDateString("en-GB", { weekday: "short" })}</small></td>
              {grahas.map((p) => {
                const c = r.cells[p], moved = i > 0 && rows[i - 1].cells[p].sign !== c.sign;
                return (
                  <td key={p}>
                    <strong className={moved ? "moved" : undefined} data-tip={moved ? `Enters ${c.sign} today` : undefined}>{moved && "→ "}{c.sign}</strong>
                    {ITEMS_ALL.filter((k) => c[k] !== undefined).map((k) => <div key={k} className={verdict(c[k]) ? `v-${verdict(c[k])}` : undefined}><span className="muted" data-tip={SHORT_TIP[k]}>{SHORT[k]}:</span> {c[k]}</div>)}
                  </td>
                );
              })}
            </tr>
          );
        })}</tbody>
      </table>
      <p ref={end} className="muted pad">{hasNextPage ? "Loading the next three months…" : rows.length > 0 && `${rows.length} days, to ${day(rows[rows.length - 1].when)}`}</p>
    </div>
  );
}

/** The Outlook: domain ``d``'s chart read graha by graha, a fixed row each, Sun to Ketu: the houses it rules there, the house it transits
 *  from that chart's lagna (From Asc) and from the natal Moon (From Moon: the classical count, good or bad, with vedha), in D-1 by the natal
 *  bhavas (the lagna's Bhava system, the one for a graha from the Moon: Settings, or the Houses tab), in a varga by its signs, the nakshatra it is in, its contacts with
 *  the natal grahas and when each is exact, and when it entered, is on the cusp and leaves (and for which house); under it what the next
 *  ``years`` bring (Ahead). The tables scroll together; a graha's name opens what the books say of its transit, its nakshatra the
 *  nakshatra's own pop-up. */
function DomainBody({ d, years, toDays }: { d: number; years: number; toDays: () => void }) {
  const { natal, birth } = useChart();
  const [info, setInfo] = useKept("transit.domain.info", "");      // the graha whose info pop-up is open
  const q = useQuery(domainQuery(natal, birth, d));
  const ahead = useQuery({ queryKey: ["transitAhead", natal, birth, d, years], queryFn: () => api.transitAhead(natal!, birth!, d, years), placeholderData: (p) => p });
  return (
    <Loaded q={q}>{(t) => {
        const row = t.rows.find((r) => r.graha === info);
        return (
          <>
            <div className="scroll">
              <table className="points domain-table">
                <thead><tr><th>Graha</th><th>Rules</th><th data-tip={`The bhava from the natal lagna: ${t.systems[0]}`}>From Asc</th>
                  <th data-tip={`The bhava from the natal Moon: ${t.systems[1]}; good, or obstructed (vedha), by the classical count`}>From Moon</th><th>Nakshatra</th><th>Contacts</th><th>Entered</th><th>Cusp</th><th>Leaves</th></tr></thead>
                <tbody>
                  {t.rows.map((r) => {
                    const cusp = pickMoment(r.cusps);
                    const next = [r.entry, ...r.cusps.map((c) => c.when), r.exit].filter((w) => w >= t.now).sort()[0];
                    const mo = r.moon.good > 0 && !r.moon.vedha.length ? "good" : r.moon.good < 0 ? "bad" : undefined;
                    return (
                      <tr key={r.graha} className={r.tone ? `tone-${r.tone}` : undefined}>
                        <td><button type="button" className="dt-graha" data-tip="What this transit means" onClick={() => setInfo(r.graha)}>{r.graha}</button>{r.retro && <> <Retro /></>}</td>
                        <td>{r.rules.length ? supOrd(r.rules.map((k) => ORD[k - 1]).join(", ")) : <span className="muted">—</span>}
                          {(r.karaka || r.flags.length > 0) && <small>{[r.karaka && "karaka", ...r.flags].filter(Boolean).join(" · ")}</small>}</td>
                        <td className={r.key ? "key" : undefined}>{supOrd(r.house)}</td>
                        <td className={mo}>{supOrd(r.moon.house)}<small>{r.moon.vedha.length ? `vedha ${r.moon.vedha.join(" ")}` : mo === "good" ? "good" : mo === "bad" ? "bad" : "neutral"}</small></td>
                        <td><button type="button" className="nak-link" data-tip="What this nakshatra signifies" onClick={() => openLore({ kind: "nakshatra", n: r.nakshatra.n, from: r.graha })}>{STARS[r.nakshatra.n - 1]}</button>
                          <small>pada {r.nakshatra.pada}</small></td>
                        <td className="dt-contacts">{r.contacts.length ? r.contacts.map((c) => {
                          const e = pickMoment(c.exact);
                          return (
                            <span key={c.kind + c.what} className={`contact tone-${c.tone}${c.domain ? "" : " other"}`} data-tip={c.exact.length ? `Exact ${c.exact.map((x) => at(x.when)).join(", ")}` : "Not exact in this stay"}>
                              {CONTACT[c.kind]} {c.what}<small className={e?.past ? "past" : undefined}>{c.exact.length > 1 ? c.exact.map((x) => day(x.when)).join(" · ") : e ? `exact ${day(e.when)}` : "not exact"}</small>
                            </span>
                          );
                        }) : <span className="muted">—</span>}</td>
                        <When m={{ when: r.entry, past: true }} now={t.now} />
                        <When m={cusp} now={t.now} next={next} />
                        <When m={{ when: r.exit, past: false }} now={t.now} next={next} to={r.next} />
                      </tr>
                    );
                  })}
                </tbody>
              </table>
              {ahead.isError ? <p role="alert" className="error banner">{ahead.error?.message}</p>
                : ahead.data ? <Ahead a={ahead.data} toDays={toDays} /> : <p className="muted pad">Looking ahead…</p>}
            </div>
            {row && <LoreDialog title={`${row.graha} in D${t.d} · ${t.name}`} onClose={() => setInfo("")}
              sub={<>{supOrd(row.house)} from the D{t.d} lagna · {supOrd(row.moon.house)} from the natal Moon{row.rules.length > 0 && <> · rules the {supOrd(row.rules.map((k) => ORD[k - 1]).join(", "))}</>}</>}>
              {row.info.map((n, i) => (
                <section key={i} className={`lore-sec lore-note${n.tone ? ` tone-${n.tone}` : ""}`}>
                  <span className="g-kicker">{KIND[n.kind]}</span>
                  <h3>{supOrd(n.head)}{n.verdict && <small> · {n.verdict}</small>}</h3>
                  <p>{supOrd(n.text)}</p>
                  {n.notes.length > 0 && <ul className="lore-points">{n.notes.map((x, j) => <li key={j}>{supOrd(x)}</li>)}</ul>}
                  {(n.source || n.n) && <p className="muted lore-src">{n.source}{n.source && n.n ? " · " : ""}{n.n && <button type="button" className="nak-link" onClick={() => { setInfo(""); openLore({ kind: "nakshatra", n: n.n!, from: row.graha }); }}>All about {STARS[n.n - 1]}</button>}</p>}
                </section>
              ))}
            </LoreDialog>}
          </>
        );
      }}</Loaded>
  );
}

const SHOWN = 10;      // events a graha's row shows before "+n more"
const dm = (iso: string) => new Date(iso).toLocaleDateString("en-GB", { day: "numeric", month: "short" });
/** "14 Apr → 15 May", the end's year named when it is another year than the start's (the row's year marks name the start's). */
const span = (from: string | null, to: string | null) =>
  `${from ? dm(from) : "now"} → ${!to ? "…" : from && to.slice(0, 4) !== from.slice(0, 4) ? day(to) : dm(to)}`;
const startOf = (e: AheadEvent, now: string) => (e.kind === "stay" ? e.from : e.kind === "retro" ? e.from ?? now : e.when);

/** One coming event as a chip, its tone (a key house, the classical count from the Moon, a contact's graha) as its bar: a stay in a sign
 *  (its house, the house from the natal Moon, Sade Sati and the like, its dates), a retrograde spell, or a contact's exact day. */
function AheadChip({ e, d, now }: { e: AheadEvent; d: number; now: string }) {
  if (e.kind === "stay") {
    const verdict = e.good > 0 ? "good" : e.good < 0 ? "bad" : "";
    const tip = `The ${e.house} from the D${d} lagna${e.key ? " (a key house)" : ""}${e.aspects.length ? `, aspecting the ${e.aspects.join(", ")}` : ""}; the ${e.moon} from the natal Moon${verdict && `, ${verdict} by the classical count`}. ${at(e.from)} to ${e.to ? at(e.to) : "past the search's reach"} · ${fromNow(e.from, now)}`;
    return (
      <span className={`ahead-ev${e.tone ? ` tone-${e.tone}` : ""}`} data-tip={tip}>
        <span>{e.key ? <b>{supOrd(e.house)} house</b> : <>{supOrd(e.house)} house</>}{e.aspects.length > 0 && <small className="inline"> · aspects {supOrd(e.aspects.join(", "))}</small>}</span>
        <small>{supOrd(e.moon)} from Mo{verdict && ` · ${verdict}`}{e.note && <b> · {e.note}</b>}</small>
        <small>{span(e.from, e.to)}</small>
      </span>
    );
  }
  if (e.kind === "retro") return (
    <span className="ahead-ev" data-tip={`Retrograde ${e.from ? `from ${at(e.from)}` : "now"} ${e.to ? `to ${at(e.to)}` : "past the search's reach"}`}>
      <span>Retrograde</span><small>{span(e.from, e.to)}</small>
    </span>
  );
  return (
    <span className={`ahead-ev tone-${e.tone}${e.domain ? "" : " other"}`} data-tip={`Exact ${at(e.when)} · ${fromNow(e.when, now)}`}>
      <span>{CONTACT[e.kind]} {e.what}</span><small>exact {dm(e.when)}</small>
    </span>
  );
}

/** Under the Outlook's table, graha by graha (the Moon's weeks are the day-by-day view's): what the next years bring in the domain's
 *  chart, in time order, each year's first under its year; the first SHOWN, then "+n more" (kept open over a refresh); and how far the list reaches. */
function Ahead({ a, toDays }: { a: DomainAhead; toDays: () => void }) {
  const [open, setOpen] = useKept<string[]>("transit.ahead.open", []);
  const rows = [a.grahas[0], null, ...a.grahas.slice(1)];      // the Moon's row, second as everywhere
  return (
    <table className="points ahead-table">
      <thead><tr><th>Graha</th><th>Coming up in D{a.d} · the next {a.years === 1 ? "year" : `${a.years} years`}</th></tr></thead>
      <tbody>{rows.map((g) => {
        if (!g) return <tr key="Mo"><td><strong>Mo</strong></td><td className="muted">A sign every 2¼ days: <button type="button" className="nak-link" onClick={toDays}>Day by day</button> shows its weeks.</td></tr>;
        const all = open.includes(g.graha);
        const shown = all ? g.events : g.events.slice(0, SHOWN);
        let year = "";
        return (
          <tr key={g.graha}>
            <td><strong>{g.graha}</strong></td>
            <td><div className="ahead-flow">
              {shown.map((e, i) => {
                const y = startOf(e, a.now).slice(0, 4);
                const mark = y !== year;
                year = y;
                return <Fragment key={i}>{mark && <span className="ahead-year">{y}</span>}<AheadChip e={e} d={a.d} now={a.now} /></Fragment>;
              })}
              {g.events.length > SHOWN && <button type="button" className="nak-link ahead-more" onClick={() => setOpen(all ? open.filter((x) => x !== g.graha) : [...open, g.graha])}>
                {all ? "Fewer" : `+${g.events.length - SHOWN} more`}</button>}
              <small className="muted ahead-reach">{g.events.length ? "Listed up to" : "Nothing new up to"} {day(g.reach)}</small>
            </div></td>
          </tr>
        );
      })}</tbody>
    </table>
  );
}

/** A result's cell, marked good or bad when its words say so. */
const Verdict = ({ text }: { text: string }) => { const v = verdict(text); return <td className={v ? `v-${v}` : undefined}>{supOrd(text)}</td>; };

const REFERENCES = ["Moon", "Lagna", "Arudha lagna"];

/** The Basic Transit Results lists: which one is open, the natal reference and the ashtakavarga vargas, kept over a
 *  refresh. ``menu`` is the transit lists' menu, as a list's right-click menu. Starlight's ``view`` can also be its Home or Domain (VIEWS); the Windows layout then shows the first list. */
const LISTS = { view: "home", reference: 0, natalVarga: 1, transitVarga: 1 };

/** Opens Starlight's Transits on its Chakras view, at chakra ``id`` if it is one of them: where the Chakras page, which Starlight no longer
 *  has, now is. */
export function openTransitChakras(id?: string) {
  let o = {};
  try { o = JSON.parse(localStorage.getItem("view.transit.lists") ?? "{}") ?? {}; } catch { /* none kept */ }
  keep("transit.lists", { ...LISTS, ...o, view: "chakras" });
  if (TRANSIT_CHAKRAS.some((c) => c.id === id)) keep("transit.chakra", id);
  useChart.getState().go("Transits", ["transits", "basic"]);
}

function useTransitLists(enabled: boolean) {
  const { natal, birth } = useChart();
  const [o, save] = useKept("transit.lists", LISTS);
  const set = (patch: Partial<typeof o>) => save({ ...o, ...patch });
  const q = useQuery({ queryKey: ["transit", natal, birth, o.reference, o.natalVarga, o.transitVarga], queryFn: () => api.transit(natal!, birth!, o.reference, o.natalVarga, o.transitVarga), enabled, placeholderData: (p) => p });
  // a reference or varga picked opens the one list it changes
  const vargas = (k: "natalVarga" | "transitVarga") => DIVISIONS.map((d) => ({ label: d === 1 ? "Rasi (D-1)" : `D-${d}`, checked: o[k] === d, onClick: () => set({ [k]: d, view: "ashtakavarga" }) }));
  const options: MenuEntry[] = [
    { label: "Natal reference to use", items: REFERENCES.map((n, i) => ({ label: n, checked: o.reference === i, onClick: () => set({ reference: i, view: "standard" }) })) },
    { label: "Natal varga for ashtakavarga", items: vargas("natalVarga") },
    { label: "Transit varga for ashtakavarga", items: vargas("transitVarga") },
  ];
  const menu: MenuEntry[] = [
    ...(q.data ?? []).map((v) => ({ label: v.name, checked: v.key === o.view, onClick: () => set({ view: v.key }) })),
    ...(q.data ? [] : [{ label: "Calculating…", disabled: true }]),
    "-", ...options,
  ];
  return { o, set, q, menu, options };
}

/** The open transit list: its dropdown, the natal reference and (for the ashtakavarga list) the vargas in its head, then the table and its note.
 *  ``bare`` (Starlight) drops the head: the tiles pick the list and its right-click menu has the rest. ``also``: lists shown under it in the
 *  same box, each table with its note under it. */
function TransitList({ lists: { o, set, q }, bare, also = [] }: { lists: ReturnType<typeof useTransitLists>; bare?: boolean; also?: string[] }) {
  return (
    <Loaded q={q}>{(all) => {
      const v = all.find((x) => x.key === o.view) ?? all[0];
      const tables = [v, ...also.flatMap((k) => all.filter((x) => x.key === k))];
      const last = tables[tables.length - 1];
      return (
        <>
          {!bare && <header className="pane-head">
            <span className="row wrap">
              <select aria-label="Transit list" value={v.key} onChange={(e) => set({ view: e.target.value })}>
                {all.map((x) => <option key={x.key} value={x.key}>{x.name}</option>)}
              </select>
              <label className="row">Natal reference<select value={o.reference} onChange={(e) => set({ reference: Number(e.target.value) })}>{REFERENCES.map((n, i) => <option key={n} value={i}>{n}</option>)}</select></label>
              {v.key === "ashtakavarga" && <>
                <label className="row">Natal varga<DivisionSelect value={o.natalVarga} onChange={(d) => set({ natalVarga: d })} /></label>
                <label className="row">Transit varga<DivisionSelect value={o.transitVarga} onChange={(d) => set({ transitVarga: d })} /></label>
              </>}
            </span>
            <CopyButton text={tableText(v.columns, v.rows)} />
          </header>}
          <div className="scroll">
            {tables.map((t, k) => (
              <Fragment key={t.key}>
                <table className={k ? "points wrap verdicts aspect-next" : "points wrap verdicts"}>
                  <thead><tr>{t.columns.map((c) => <th key={c}>{c}</th>)}</tr></thead>
                  <tbody>{t.rows.map((r) => <tr key={r[0]}><td><strong>{r[0]}</strong></td>{r.slice(1).map((c, i) => <Verdict key={i} text={c} />)}</tr>)}</tbody>
                </table>
                {t !== last && t.note && <p className="muted hint pad">{t.note}</p>}
              </Fragment>
            ))}
          </div>
          {last.note && <p className="muted hint pad">{last.note}</p>}
        </>
      );
    }}</Loaded>
  );
}

type ChakraId = (typeof TRANSIT_CHAKRAS)[number]["id"];
const PINNED_CHAKRAS = new Set<string>(["sbc", "kota", "kala", "tripataki", "kurma"]);     // always on the row; the rest as there is room, else under "More"
/** The chakra Starlight's Chakras view shows, kept over a refresh: the Sarvatobhadra until another is picked. */
function useTransitChakra() {
  const [kept, set] = useKept<string>("transit.chakra", "sbc");
  return [(TRANSIT_CHAKRAS.some((c) => c.id === kept) ? kept : "sbc") as ChakraId, set] as const;
}

/** Starlight's Chakras view, under the cast form: the chakras' row, which stays put, over the picked one's controls, the picked slot's card
 *  and its reading, which scroll; its wheel is in the left half (TransitsLeft), the two in step. */
function ChakrasView() {
  const [chakra, setChakra] = useTransitChakra();
  return (
    <div className="finder"><section className="pane domain-timeline chakra-view">
      <div className="outlook-bar"><OneRowTabs tabs={TRANSIT_CHAKRAS} pinned={PINNED_CHAKRAS} value={chakra} onChange={setChakra} label="Chakras" /></div>
      <TransitChakra key={chakra} tab={chakra} part="side" />
    </section></div>
  );
}

/** Starlight's left half on the Transits tab: the chakra picked in the Chakras view of the Transits sub tab once a transit is cast, else the
 *  Jamakkol chart on its sub tab once cast; else the charts as on the other tabs (the transit square while cast). */
export function TransitsLeft() {
  const { mode, display } = useChart();
  const [kept] = useSaved<string>("transits", "basic");
  const [lists] = useKept<{ view: string }>("transit.lists", { view: "home" });
  const [chakra] = useTransitChakra();
  const on = subTab(kept, display) === "basic" && viewOf(lists.view) === "chakras" && mode?.title === "Transit";
  const jamakkol = useJamakkolCast() && subTab(kept, display) === "jamakkol";     // the Jamakkol chart cast on its sub tab
  if (jamakkol) return <JamakkolLeft />;
  return on ? <div className="star-chart transit-chakra"><TransitChakra key={chakra} tab={chakra} part="draw" /></div> : <LeftCharts />;
}

const EMPTY = "No transit chart yet. Pick a moment, then show its transit calculations.";
const links = <ModeLinks links={[["Sarvatobhadra Chakra", "Chakras", "chakras:sbc"], ["Kota Chakra (Durga Chakra)", "Chakras", "chakras:kota"], ["Kalachakra", "Chakras", "chakras:kala"]]} />;

function Basic() {
  const { natal, birth, mode, display } = useChart();
  const { fields, moment, now, put } = useMoment(undefined, true, "transit.basic");
  const star = display.layout === "starlight";   // Starlight shows only the two panes: its transit chart on the left has the rest
  const show = useFind(() => api.transitMode(natal!, moment()));
  const cast = mode?.title === "Transit";
  const inTransit = cast && !star;
  const lists = useTransitLists(cast);
  const view = viewOf(lists.o.view);
  const { open, node } = useMenu();
  const home: MenuEntry[] = [{ label: "Transit Calendar", title: "Important graha transits by domain of life, now and coming up", onClick: () => lists.set({ view: "calendar" }) }];
  const listMenu = (e: React.MouseEvent) => { e.preventDefault(); open(e, lists.options, "Transit lists"); };
  return (
    <>
      <div className="finder">
        <section className="pane finder-form">
          {!star && <header className="pane-head"><h2>Transit moment</h2><span className="muted">The sky at this time, read against the natal chart</span></header>}
          <form className="mode-form" onSubmit={(e) => { e.preventDefault(); show.mutate(undefined); }}>
            {fields}
            <div className="mode-buttons">
              {star ? <CastButton busy={show.isPending} kind="Transit" cast={(keep) => show.mutate(undefined, { onSuccess: keep })} />
                : <button type="submit" className="primary" disabled={show.isPending}>Show Transit Calculations</button>}
              <button type="button" className="now-btn" onClick={now} aria-label="Now" data-tip="Set the date and time to now"><Icon name="now" /></button>
              {/* cast: step the transit's time (the natal chart stays), the fields following it */}
              {cast && <Stepper transit onStep={put} />}
            </div>
          </form>
        </section>
        {star   // the flags alone: the transit chart beside it already names the moment
          ? <section className="pane finder-result">{show.error && <p role="alert" className="error banner">{show.error.message}</p>}
            <div className="view-tiles" role="group" aria-label="Transit views">
              {VIEWS.map(([k, label, tip]) => <button key={k} type="button" aria-pressed={view === k} onClick={() => lists.set({ view: k })} data-tip={tip}>{label}</button>)}
            </div></section>
          : <ModeCard error={show.error} empty={EMPTY}>{links}</ModeCard>}
      </div>
      {/* Starlight before a transit is cast (none, or a Tajaka year in use): the natal chart's details, every transit view empty */}
      {star && (view === "home" ? <TransitInfo menu={home} cast={cast} /> : !cast ? <div className="finder"><section className="pane domain-timeline"><p className="muted pad">{NOT_CAST}</p></section></div>
        : view === "calendar" ? <Outlook /> : view === "chakras" ? <ChakrasView />
        : <div className="finder"><section className="pane domain-timeline" onContextMenu={listMenu}>
          <TransitList lists={lists} bare also={ALSO[view]} />{node}</section></div>)}
      {inTransit && <section className="pane transit-results"><TransitList lists={lists} /></section>}
      {inTransit && <section className="pane"><header className="pane-head"><h2>Mixed Transit-Natal Chart</h2></header>
        <div className="pad mixed"><MixedChart outerBirth={birth!} outerName="Transit" innerBirth={natal!} innerName="Natal Chart" /></div></section>}
      <ChartPanes />
    </>
  );
}


/** The Transit Calendar, the Windows layout's sub tab; Starlight's is the Transits view Outlook, its Day by day. */
function Calendar() {
  const natal = useChart((s) => s.natal)!;
  const { fields, moment } = useMoment(undefined, true, "transit.calendar");
  const [step, setStep] = useKept("transit.calendar.step", 1);
  const [count, setCount] = useKept("transit.calendar.count", 15);
  const [items, setItems] = useKept<string[]>("transit.calendar.items", ITEMS.map(([k]) => k));
  const [natalVarga, setNatalVarga] = useKept("transit.calendar.natalVarga", 1);
  const [transitVarga, setTransitVarga] = useKept("transit.calendar.transitVarga", 1);
  const [legend, setLegend] = useKept("transit.calendar.legend", false);
  const find = useKeptRun("transit.calendar.rows", async () => {
    const { birth } = await api.transitMode(natal, moment());
    return api.calendar(natal, birth, step, count, items, natalVarga, transitVarga);
  });
  const planets = BODIES.slice(1);
  const star = useChart((s) => s.display.layout === "starlight");     // Starlight: the sub tab already names the view
  const when = (r: CalendarRow) => r.when.slice(0, 16).replace("T", " ");
  return (
    <section className="pane">
      {!star && <header className="pane-head"><h2>Transit Calendar</h2>{find.data && <CopyButton text={tableText(["Date", ...planets],
        find.data.map((r) => [when(r), ...planets.map((p) => Object.values(r.cells[p]).join(" "))]))} />}</header>}
      <form className="mode-form" onSubmit={(e) => { e.preventDefault(); find.mutate(); }}>
        {fields}
        <label>Natal varga<DivisionSelect value={natalVarga} onChange={setNatalVarga} /></label>
        <label>Transit varga<DivisionSelect value={transitVarga} onChange={setTransitVarga} /></label>
        <label>Every (days)<input type="number" step="any" min={0.01} max={366} value={step} onChange={(e) => setStep(Number(e.target.value))} required /></label>
        <label>Number of rows (at most 100)<input type="number" min={1} max={100} value={count} onChange={(e) => setCount(Number(e.target.value))} required /></label>
        <fieldset className="mode-group"><legend>Items in the calendar</legend>
          {ITEMS.map(([k, name]) => (
            <label key={k} className="check"><input type="checkbox" checked={items.includes(k)}
              onChange={(e) => setItems(e.target.checked ? [...items, k] : items.filter((x) => x !== k))} /> {name}</label>
          ))}
        </fieldset>
        <div className="mode-buttons"><button type="submit" className="primary" disabled={find.isPending}>{find.isPending ? "Calculating…" : "Show Transit Calendar"}</button>
          <button type="button" onClick={() => setLegend(!legend)}>Show Legend (explanation of symbols)</button></div>
      </form>
      {legend && <p className="muted pad">Mo, Lg: the bhava from the natal Moon or lagna, "(good)" for a good bhava, "(vedha)" when another graha obstructs it. Tara: the transit star from the natal Moon's. Murthi: the form (Swarna, Rajata, Taamra, Loha). AV/SAV: the graha's own score and the total in its sign. Kak: the lord of its kakshya.</p>}
      {find.error && <p role="alert" className="error banner">{find.error.message}</p>}
      {find.data && (
        <div className="scroll tall">
          <table className="points wrap calendar">
            <thead><tr><th>Date</th>{planets.map((p) => <th key={p}>{p}</th>)}</tr></thead>
            <tbody>{find.data.map((r) => (
              <tr key={r.when}><td className="num">{when(r)}</td>{planets.map((p) => (
                <td key={p}>
                  <strong>{r.cells[p].sign}</strong>
                  {Object.entries(r.cells[p]).filter(([k]) => k !== "sign").map(([k, v]) => <div key={k} className={verdict(v) ? `v-${verdict(v)}` : undefined}><span className="muted">{SHORT[k]}:</span> {v}</div>)}
                </td>
              ))}</tr>
            ))}</tbody>
          </table>
        </div>
      )}
    </section>
  );
}

function Search() {
  const natal = useChart((s) => s.natal)!;
  const sahams = useQuery({ queryKey: ["sahams"], queryFn: api.sahams });
  const { fields, moment } = useMoment(undefined, true, "transit.search");
  const [f, setF] = useState({ body: 5, deg: 0, min: 0, sec: 0, ahead: false, target: "saham", value: 0, backward: true, division: 1 });
  const set = <K extends keyof typeof f>(k: K, v: (typeof f)[K]) => setF({ ...f, [k]: v });
  const find = useFind(() => api.specialSearch(natal, { when: moment(), body: f.body, offset: f.deg + f.min / 60 + f.sec / 3600, ahead: f.ahead,
    target: f.target, value: f.value, backward: f.backward, division: f.division }));
  const num = (k: "deg" | "min" | "sec", label: string, max: number) => (
    <label>{label}<input type="number" step="any" min={0} max={max} value={f[k]} onChange={(e) => set(k, Number(e.target.value))} /></label>
  );
  const star = useChart((s) => s.display.layout === "starlight");
  const choices = f.target === "planet" ? BODIES : f.target === "saham" ? (sahams.data ?? []) : SIGN_NAMES;
  return (
    <>
      <div className="finder">
      <section className="pane finder-form">
        {!star && <header className="pane-head"><h2>Special Search</h2><span className="muted">When a transit reaches an exact point</span></header>}
        <form className="mode-form" onSubmit={(e) => { e.preventDefault(); find.mutate(undefined); }}>
          <label>Find when<select value={f.body} onChange={(e) => set("body", Number(e.target.value))}>{BODIES.map((n, i) => <option key={n} value={i}>{n}</option>)}</select></label>
          {num("deg", "Transited exactly (deg)", 359)}{num("min", "Min", 59)}{num("sec", "Sec", 59.99)}
          <label>Relative to<select value={String(f.ahead)} onChange={(e) => set("ahead", e.target.value === "true")}><option value="false">Behind</option><option value="true">Ahead of</option></select></label>
          <label>Target
            <select value={f.target} onChange={(e) => setF({ ...f, target: e.target.value, value: 0 })}>
              <option value="saham">Natal saham</option><option value="planet">Natal graha</option><option value="sign">The beginning of a sign</option>
            </select>
          </label>
          <label>Which<select value={f.value} onChange={(e) => set("value", Number(e.target.value))}>{choices.map((n, i) => <option key={n} value={i}>{n}</option>)}</select></label>
          <label>In<DivisionSelect value={f.division} onChange={(d) => set("division", d)} /></label>
          <label>The date below<select value={String(f.backward)} onChange={(e) => set("backward", e.target.value === "true")}><option value="true">Before</option><option value="false">After</option></select></label>
          {fields}
          <div className="mode-buttons">
            <button type="submit" className="primary" disabled={find.isPending}>Search for Transit</button>
          </div>
        </form>
      </section>
      <ModeCard error={find.error} empty="Nothing found yet. Describe the point and search from a date." />
      </div>
      <ChartPanes />
    </>
  );
}

const CORRELATION_RULES = ["Quantify aspects based on Parasara's teachings and show aspects greater than this percentage", "Consider conjunction, full, three-quarter and half aspects and take an orb of these many degrees", "Consider perfect quadrants from natal points, within an orb of these many degrees", "Consider perfect trines and 7th from natal points, within an orb of these many degrees"];
const STEP_UNITS: [string, number, number][] = [["Year", 0, 12], ["3 Months", 0, 3], ["Month", 0, 1], ["10 Days", 864000, 0], ["5 Days", 432000, 0], ["Day", 86400, 0], ["Hour", 3600, 0]];

function Correlation() {
  const natal = useChart((s) => s.natal)!;
  const { fields, moment, shift } = useMoment(undefined, true, "transit.correlation");
  const [threshold, setThreshold] = useKept("transit.correlation.threshold", 80);
  const [rule, setRule] = useKept("transit.correlation.rule", 0);
  const [orb, setOrb] = useKept("transit.correlation.orb", 1);
  const [division, setDivision] = useKept("transit.correlation.division", 1);
  const [unit, setUnit] = useKept("transit.correlation.unit", 0);
  const find = useKeptRun("transit.correlation.rows", async () => {
    const { birth } = await api.transitMode(natal, moment());
    return api.correlation(natal, birth, threshold, rule, orb, division);
  });
  const move = async (dir: number) => {
    const [, seconds, months] = STEP_UNITS[unit];
    await shift(natal, dir * seconds, dir * months);
    find.mutate();
  };
  const rows = (r: CorrelationRow[]) => r.map((x) => [x.planet, formatLon(x.lon), x.speed.toFixed(4), x.point, x.percent.toFixed(2), formatLon(x.natal_lon)]);
  const star = useChart((s) => s.display.layout === "starlight");
  const cols = ["Transit Graha", "Transit Longitude", "Speed", "Natal Point", rule ? "Orb (deg)" : "Aspect %", "Natal Longitude"];
  return (
    <section className="pane">
      {!star && <header className="pane-head"><h2>Longitude Correlation</h2>{find.data && <CopyButton text={tableText(cols, rows(find.data))} />}</header>}
      <form className="mode-form" onSubmit={(e) => { e.preventDefault(); find.mutate(); }}>
        {fields}
        <label>Divisional chart to be used in transit<DivisionSelect value={division} onChange={setDivision} /></label>
        <label>Rule<select value={rule} onChange={(e) => setRule(Number(e.target.value))}>{CORRELATION_RULES.map((n, i) => <option key={n} value={i}>{n}</option>)}</select></label>
        {rule === 0 ? <label>Percentage<input type="number" step="any" min={0} max={100} value={threshold} onChange={(e) => setThreshold(Number(e.target.value))} required /></label>
          : <label>Orb (degrees)<input type="number" step="any" min={0.01} max={30} value={orb} onChange={(e) => setOrb(Number(e.target.value))} required /></label>}
        <div className="mode-buttons"><button type="submit" className="primary" disabled={find.isPending}>Show Natal Points Aspected in Transit</button>
          <button type="button" aria-label="Earlier" onClick={() => move(-1)} disabled={find.isPending}>&lt;&lt;</button>
          <select aria-label="Step" value={unit} onChange={(e) => setUnit(Number(e.target.value))}>{STEP_UNITS.map(([n], i) => <option key={n} value={i}>{n}</option>)}</select>
          <button type="button" aria-label="Later" onClick={() => move(1)} disabled={find.isPending}>&gt;&gt;</button>
        </div>
      </form>
      {find.error && <p role="alert" className="error banner">{find.error.message}</p>}
      {find.data && (
        <div className="scroll tall">
          <table className="points">
            <thead><tr>{cols.map((c) => <th key={c}>{c}</th>)}</tr></thead>
            <tbody>{rows(find.data).map((r, i) => <tr key={i}>{r.map((c, k) => k === 4 ? (
              <td key={k} className="num"><span className="cell-meter">{c}<Meter t={rule ? 1 - find.data![i].percent / orb : find.data![i].percent / 100} fill={rule ? 1 - find.data![i].percent / orb : find.data![i].percent / 100} /></span></td>
            ) : <td key={k} className={k === 1 || k === 5 ? "num" : k === 0 ? "strong" : ""}>{supOrd(c)}</td>)}</tr>)}</tbody>
          </table>
          {find.data.length === 0 && <p className="muted pad">No natal point is aspected above this percentage.</p>}
        </div>
      )}
    </section>
  );
}

const WHAT_IS_THIS = "By adding the longitudes of various bodies and lagnas, years of some important events can be obtained.\nCounting of various amsas is also possible. These methods are basically like simple progression techniques.\nThese calculations are given to facilitate research.";
const COUNTS: [number, string][] = [[0, "1 body, with upagrahas"], [1, "2 grahas"], [2, "2 bodies, with upagrahas"], [3, "3 grahas"], [4, "4 grahas"], [5, "5 grahas"]];
const LAGNAS = ["Lagna", "Bhava Lagna", "Hora Lagna", "Ghati Lagna", "Vighati Lagna", "Sree Lagna", "Indu Lagna", "Pranapada Lagna"];

function LaghuParasari() {
  const { birth, natal, mode } = useChart();
  const [count, setCount] = useState(1);
  const [added, setAdded] = useState("Lagna");
  const [division, setDivision] = useState(1);
  const [countSigns, setCountSigns] = useState(true);
  const [oneCycle, setOneCycle] = useState(false);
  const { say } = useChart();
  const star = useChart((s) => s.display.layout === "starlight");
  // an event chart's ages fit into its span; transit, progressed and Prasna charts keep the natal ages
  const chart = mode?.natalDasas ? natal! : birth!;
  const span = mode?.event?.span_days;
  const q = useQuery({ queryKey: ["laghu", chart, count, added, span, division, countSigns, oneCycle], queryFn: () => api.laghuParasari(chart, count, added || null, span, division, countSigns, oneCycle) });
  const text = (q.data ?? []).map((r) => [r.label.padEnd(30), ...r.cells.map(([d, a]) => `${d} (${a.toFixed(2)})`)].join(" ")).join("\n");
  return (
    <section className="pane">
      <header className="pane-head">
        {!star && <h2>Laghu Parasari</h2>}
        <span className="row">
          <select aria-label="Bodies to add" value={count} onChange={(e) => setCount(Number(e.target.value))}>
            {COUNTS.map(([v, n]) => <option key={v} value={v}>{n}</option>)}
          </select>
          <select aria-label="Lagna to add" value={added} onChange={(e) => setAdded(e.target.value)}>
            <option value="">No lagna</option>
            {LAGNAS.map((l) => <option key={l}>{l}</option>)}
          </select>
          <DivisionSelect value={division} onChange={setDivision} label="Varga to be used" />
          <select aria-label="Method used in vargas" value={String(countSigns)} onChange={(e) => setCountSigns(e.target.value === "true")}><option value="true">Count signs in divisions</option><option value="false">Find longitudes in divisions</option></select>
          <label className="check"><input type="checkbox" checked={oneCycle} onChange={(e) => setOneCycle(e.target.checked)} /> Use only one cycle in compressed/annual charts</label>
          <button onClick={() => say("What's all this?", WHAT_IS_THIS)}>What is all this?</button>
          <CopyButton text={text} />
        </span>
      </header>
      <p className="muted pad">Adds the longitudes of the chosen bodies and lists the dates and ages (in brackets) the sum stands for.</p>
      <Loaded q={q}>{(rows) => (
        <div className="scroll tall">
          <table className="points">
            <thead><tr><th>Sum of</th>{rows[0]?.cells.map((_, i) => <th key={i}>Date {i + 1} (age)</th>)}</tr></thead>
            <tbody>{rows.map((r) => (
              <tr key={r.label}><td>{r.label}</td>{r.cells.map(([d, a], i) => <td key={i} className="num">{d} ({a.toFixed(2)})</td>)}</tr>
            ))}</tbody>
          </table>
        </div>
      )}</Loaded>
    </section>
  );
}

const TABS = [{ id: "basic", name: "Transits" }, { id: "tajaka", name: "Tajaka" }, { id: "tithi", name: "Tithi Pravesha" }, { id: "jamakkol", name: "Jamakkol" }, { id: "calendar", name: "Transit Calendar" }, { id: "search", name: "Special Search" }, { id: "correlation", name: "Longitude Correlation" },
  { id: "angular", name: "Angular Return" }, { id: "progressions", name: "Progressions" }, { id: "prasna", name: "Prasna (Horary)" }, { id: "laghu", name: "Laghu Parasari" }] as const;

const PINNED = new Set(["basic", "tajaka", "tithi", "jamakkol", "calendar", "search", "correlation"]);     // always on the row; the rest under "More", which takes the open one's name

/** The Transits sub tabs. Settings > Display can keep Tajaka and Tithi Pravesha as pages of their own; then they are not sub tabs here.
 *  Starlight: the Transit Calendar is a view of Transits (Outlook), not a sub tab. */
function subTabs(display: Display) {
  const some = display.transitsTogether ? TABS : TABS.filter((t) => t.id !== "tajaka" && t.id !== "tithi");
  return display.layout === "starlight" ? some.filter((t) => t.id !== "calendar") : some;
}
/** The sub tab open: the kept one, if it is still a sub tab; else Transits. */
const subTab = (kept: string, display: Display) => (subTabs(display).find((t) => t.id === kept)?.id ?? "basic");

export function Transits() {
  const [kept, setTab] = useSaved<(typeof TABS)[number]["id"]>("transits", "basic");
  const display = useChart((s) => s.display);
  const star = display.layout === "starlight";
  const tabs = subTabs(display);
  const tab = subTab(kept, display);
  const head = <>
    <h1>Transits</h1>
    {/* the transit time steps with the top bar's time buttons */}
    {star ? <OneRowTabs tabs={tabs} pinned={PINNED} value={tab} onChange={setTab} label="Transits views" />
      : <SubTabs tabs={[...tabs]} value={tab} onChange={setTab} label="Transits views" />}
  </>;
  // Tajaka and Tithi Pravesha lay out their own page: they take these sub tabs as its head
  if (tab === "tajaka") return <Tajaka head={head} />;
  if (tab === "tithi") return <TithiPravesha head={head} />;
  return (
    <div className="right lab">
      <header className="lab-head">{head}</header>
      {tab === "basic" ? <Basic /> : tab === "calendar" ? <Calendar /> : tab === "search" ? <Search /> : tab === "correlation" ? <Correlation />
        : tab === "angular" ? <AngularReturn /> : tab === "progressions" ? <Progressions /> : tab === "prasna" ? <Prasna /> : tab === "jamakkol" ? <Jamakkol /> : <LaghuParasari />}
    </div>
  );
}
