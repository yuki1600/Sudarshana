import { Fragment, useCallback, useEffect, useState } from "react";
import { useMutation, useQueries, useQuery, useQueryClient } from "@tanstack/react-query";
import { api, currentSettings, perDasa, saveSettings, savePerDasa, type BestDasa, type DasaItem, type DasaLevel, type PerDasa, type SettingOption } from "./api";
import { FormButtons, Modal } from "./ChartDialogs";
import { formatDuration, formatMoment } from "./format";
import { useDeath, useKept, useSaved } from "./hooks";
import { modeOf, useMoment } from "./Modes";
import { useChart } from "./store";
import { supOrd } from "./ui";

const GROUPS = [
  { id: "nakshatra", name: "Nakshatra dasas", first: "vimsottari_dasa" },
  { id: "rasi", name: "Rasi dasas", first: "narayana_dasa_of_d_1_chart" },
  { id: "other", name: "Other dasas", first: "moola_dasa" },
] as const;
const LEVEL_NAMES = ["Mahadasa (MD)", "Antardasa (AD)", "Pratyantardasa (PD)", "Sookshma-antardasa (SD)", "Prana-antardasa (PAD)", "Deha-antardasa (DAD)"];
const LEVEL_TAGS = LEVEL_NAMES.map((n) => n.slice(n.indexOf("(") + 1, -1));
const RUNNING_DEPTH = 3;   // the view opens on the period running now, down to its pratyantardasa
const SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"];
const PAIRS: [string, string][] = [["Aries", "Libra"], ["Taurus", "Scorpio"], ["Gemini", "Sagittarius"], ["Cancer", "Capricorn"], ["Leo", "Aquarius"], ["Virgo", "Pisces"]];
const EXCEPTIONS = ["No exception", "Saturn exception", "Ketu exception"];

type Shown = (DasaLevel | undefined)[];

type Tool = { label: string; disabled?: boolean; onClick: () => void };

/** One dasa's Options, with the nakshatra dasas' seed settings: stored for this dasa alone,
 *  but for the year and dasa sesham, which all dasas share. Above them, the dasa's tools. */
function DasaOptions({ item, tools, onClose }: { item: DasaItem; tools: Tool[]; onClose: () => void }) {
  const client = useQueryClient();
  const schema = useQuery({ queryKey: ["settingsSchema"], queryFn: api.settingsSchema, staleTime: Infinity });
  const [p, setP] = useState<PerDasa>(perDasa(item.key));
  const [typed, setTyped] = useState(p.typed ?? {});
  const options = schema.data?.flatMap((g) => g.options) ?? [];
  const opt = (k: string) => options.find((o) => o.key === k);
  const cur = currentSettings();
  const [shared, setShared] = useState({ year_definition: Number(cur.year_definition ?? 3), year_length: Number(cur.year_length ?? 365.24219), dasa_sesham_mundane: cur.dasa_sesham_mundane !== false });
  const value = (k: string, s: string) => (p[k] as number | boolean | string | undefined) ?? (cur[s] as number | boolean | string | undefined) ?? opt(s)?.default;
  const family = ["vimsottari_dasa", "ashtottari_dasa", "yogini_dasa", "dwi_saptati_sama_dasa", "shat_trimsa_sama_dasa", "dwadasottari_dasa", "chaturaseeti_sama_dasa", "sataabdika_dasa", "shodasottari_dasa", "panchottari_dasa", "shashti_hayani_dasa"].includes(item.key);
  const select = (k: string, s: string, o?: SettingOption) => o && (
    <label key={k}>{o.label}
      <select value={String(value(k, s))} onChange={(e) => setP({ ...p, [k]: o.choices!.find((c) => String(c.value) === e.target.value)!.value })}>
        {o.choices!.map((c) => <option key={String(c.value)} value={String(c.value)}>{c.label}</option>)}
      </select>
    </label>
  );
  const save = (e: React.FormEvent) => {
    e.preventDefault();
    const clean = Object.fromEntries(Object.entries(typed).filter(([, v]) => v !== null && v !== undefined && !(Array.isArray(v) && v.every((x) => x === null))));
    savePerDasa(item.key, { ...p, typed: Object.keys(clean).length ? clean : undefined });
    saveSettings({ ...currentSettings(), ...shared });
    client.invalidateQueries();
    onClose();
  };
  const pair = (k: "stronger" | "exception", i: number, v: number | null) => {
    const list = [...(typed[k] ?? Array(6).fill(null))] as (number | null)[];
    list[i] = v;
    setTyped({ ...typed, [k]: list });
  };
  return (
    <Modal title={`${item.title} dasa options`} onClose={onClose} wide>
      <div className="row dasa-tools">
        {tools.map((t) => <button key={t.label} type="button" disabled={t.disabled} onClick={t.onClick}>{t.label}</button>)}
      </div>
      <form method="dialog" onSubmit={save}>
        {opt("year_definition") && <label>{opt("year_definition")!.label}
          <select value={shared.year_definition} onChange={(e) => setShared({ ...shared, year_definition: Number(e.target.value) })}>
            {opt("year_definition")!.choices!.map((c) => <option key={String(c.value)} value={String(c.value)}>{c.label}</option>)}
          </select>
        </label>}
        {shared.year_definition === 2 && <label>User defined year (days)<input type="number" min={1} max={1000} step="any" value={shared.year_length} onChange={(e) => setShared({ ...shared, year_length: Number(e.target.value) })} /></label>}
        <label className="check"><input type="checkbox" checked={shared.dasa_sesham_mundane} onChange={(e) => setShared({ ...shared, dasa_sesham_mundane: e.target.checked })} /> Use dasa sesham in compressed mundane dasas</label>
        {family && <>
          {select("seed", "dasa_seed", opt("dasa_seed"))}{select("shift", "dasa_shift", opt("dasa_shift"))}{select("ad_method", "dasa_ad_method", opt("dasa_ad_method"))}
          <label className="check"><input type="checkbox" checked={!!value("tribhagi", "dasa_tribhagi")} onChange={(e) => setP({ ...p, tribhagi: e.target.checked })} /> Use Tribhagi variation</label>
          {item.key === "vimsottari_dasa" && <label className="check"><input type="checkbox" checked={!!value("reverse", "dasa_reverse")} onChange={(e) => setP({ ...p, reverse: e.target.checked })} /> Reckon everything antizodiacally</label>}
        </>}
        {item.key === "narayana_dasa_of_d_1_chart" && <label>Kind of Narayana dasa
          <select value={p.option ?? 0} onChange={(e) => setP({ ...p, option: Number(e.target.value) })}>{["Normal Narayana Dasa", "Paka Narayana Dasa", "Sama Narayana Dasa", "Ayur Narayana Dasa"].map((n, i) => <option key={n} value={i}>{n}</option>)}</select>
        </label>}
        <label>In Tajaka charts, the dasa seed
          <select value={p.tajaka_seed ?? "default"} onChange={(e) => setP({ ...p, tajaka_seed: e.target.value })}>
            <option value="default">From the natal chart, moved on one nakshatra/rasi a year (the default)</option>
            <option value="natal">From the natal chart, not moved on</option>
            <option value="event">From the Tajaka chart itself</option>
          </select>
        </label>
        {item.strengths && (
          <fieldset className="mode-group wide"><legend>Balas</legend>
            <p className="muted hint full">These override what the chart computes, for this dasa, until you change them back.</p>
            <label>Lord of Aquarius<select value={typed.aq ?? ""} onChange={(e) => setTyped({ ...typed, aq: e.target.value === "" ? null : Number(e.target.value) })}><option value="">As computed</option><option value={7}>Saturn</option><option value={8}>Rahu</option></select></label>
            <label>Lord of Scorpio<select value={typed.sc ?? ""} onChange={(e) => setTyped({ ...typed, sc: e.target.value === "" ? null : Number(e.target.value) })}><option value="">As computed</option><option value={3}>Mars</option><option value={9}>Ketu</option></select></label>
            <label>Start dasas from<select value={typed.start ?? ""} onChange={(e) => setTyped({ ...typed, start: e.target.value === "" ? null : Number(e.target.value) })}><option value="">Use the default</option>{SIGNS.map((n, i) => <option key={n} value={i}>{n}</option>)}</select></label>
            <label>Does Saturn or Ketu exception apply?<select value={typed.start_exception ?? ""} onChange={(e) => setTyped({ ...typed, start_exception: e.target.value === "" ? null : Number(e.target.value) })}><option value="">Last setting</option>{EXCEPTIONS.map((n, i) => <option key={n} value={i}>{n}</option>)}</select></label>
            <div className="strength-pairs">
              {PAIRS.map(([a, b], i) => (
                <div key={a} className="strength-pair">
                  <label>Stronger of {a} &amp; {b}<select value={typed.stronger?.[i] ?? ""} onChange={(e) => pair("stronger", i, e.target.value === "" ? null : Number(e.target.value))}><option value="">As computed</option><option value={0}>{a}</option><option value={1}>{b}</option></select></label>
                  <label>Exception<select value={typed.exception?.[i] ?? ""} onChange={(e) => pair("exception", i, e.target.value === "" ? null : Number(e.target.value))}><option value="">As computed</option>{EXCEPTIONS.map((n, k) => <option key={n} value={k}>{n}</option>)}</select></label>
                </div>
              ))}
            </div>
          </fieldset>
        )}
        <FormButtons />
      </form>
    </Modal>
  );
}

function LocateDialog({ onLocate, onClose }: { onLocate: (m: ReturnType<ReturnType<typeof useMoment>["moment"]>, depth: number) => void; onClose: () => void }) {
  const natal = useChart((s) => s.natal)!;
  const { fields, moment } = useMoment(natal.tz_east_hours);
  const [depth, setDepth] = useState(2);
  return (
    <Modal title="Locate an event" onClose={onClose}>
      <form method="dialog" onSubmit={(e) => { e.preventDefault(); onLocate(moment(), depth); }}>
        <p className="muted">Give the date and time of the event:</p>
        {fields}
        <label>Identify the periods and sub-periods running at the above time, up to
          <select value={depth} onChange={(e) => setDepth(Number(e.target.value))}>{LEVEL_NAMES.map((n, i) => <option key={n} value={i + 1}>{n}</option>)}</select>
        </label>
        <FormButtons />
      </form>
    </Modal>
  );
}

function ShiftDialog({ dasa, title, onClose }: { dasa: string; title: string; onClose: () => void }) {
  const { shifts, setShift } = useChart();
  const now = shifts[dasa] ?? 0;
  const [sign, setSign] = useState(now < 0 ? -1 : 1);
  const a = Math.abs(now);
  const [f, setF] = useState({ d: Math.floor(a / 1440), h: Math.floor((a % 1440) / 60), m: a % 60 });
  const num = (k: "d" | "h" | "m", label: string) => <label>{label}<input type="number" min={0} value={f[k]} onChange={(e) => setF({ ...f, [k]: Number(e.target.value) })} /></label>;
  return (
    <Modal title="Enter the dasa shift amount" onClose={onClose}>
      <p className="muted">Errors in birthdata, ayanamsa and other uncertainties can cause errors in the dasa dates. You can shift the dates of {title} by a set amount, which is a lot easier than rectifying all of those.</p>
      <form method="dialog" onSubmit={(e) => { e.preventDefault(); setShift(dasa, sign * (f.d * 1440 + f.h * 60 + f.m)); onClose(); }}>
        <label>Shift<select value={sign} onChange={(e) => setSign(Number(e.target.value))}><option value={1}>Later</option><option value={-1}>Earlier</option></select></label>
        {num("d", "Days")}{num("h", "Hours")}{num("m", "Minutes")}
        <FormButtons />
      </form>
    </Modal>
  );
}

const strength = (r: BestDasa["rows"][number]) => [r.dignity, ...r.notes].join(", ");
/** Why the banner names the dasa it does: the nine conditions and their controlling planets. */
function BestDasaDialog({ best, title, onClose }: { best: BestDasa; title: (key: string) => string; onClose: () => void }) {
  return (
    <Modal title="Best dasa for this chart" onClose={onClose} wide>
      <p className="muted">A condition only makes a dasa applicable. It works better than Vimsottari when its controlling graha is strong too, and the strongest controlling graha among the applicable dasas wins. With none strong, Vimsottari stands.</p>
      <div className="scroll">
        <table className="periods best-dasa">
          <thead><tr><th>Dasa</th><th>Condition</th><th>Holds</th><th>Controlling graha</th><th>Its bala</th></tr></thead>
          <tbody>
            {best.rows.map((r) => (
              <tr key={r.key} className={best.best.includes(r.key) ? "best" : ""}>
                <td>{best.best.includes(r.key) ? "★ " : ""}{title(r.key)}</td><td>{supOrd(r.condition)}</td><td>{r.met ? "Yes" : "No"}</td><td>{r.planet}</td>
                <td>{strength(r)}{r.score > 0 ? "" : " (weak)"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="muted hint">Strongest first: exalted, moolatrikona, own sign, great friend's sign, friend's sign. Weak: at the first or last degree of a sign, combust, or in the same sign as an enemy or the 6th or 8th lord. A little stronger: in the same sign as the 9th or 10th lord, and Rahu or Ketu with any graha.</p>
    </Modal>
  );
}

export function Dasas() {
  const { birth: current, natal, mode, enterMode, say, openWindow, shifts } = useChart();
  // The dasas of an event chart fill its span (dasa_systems.fitted_to_span); transit, progressed and Prasna charts keep the natal dasas
  const event = mode?.event;
  const birth = mode?.natalDasas ? natal! : current!;
  const list = useQuery({ queryKey: ["dasaList"], queryFn: api.dasaList });
  const [group, setGroup] = useSaved<(typeof GROUPS)[number]["id"]>("dasaGroup", "nakshatra");
  const [chosen, setChosen] = useKept<Record<string, string>>("dasa.chosen", {});
  // the open branch: a period's index at each level, mahadasa first; kept for this chart and dasa, so a refresh keeps it open
  const [branch, setBranch] = useKept<{ of: string; path: number[] } | null>("dasa.path", null);
  const [form, setForm] = useKept<"options" | "locate" | "shift" | "best" | null>("dasa.form", null);
  // the method is about nakshatra dasas of a birth chart, so not the dasas fitted into an event chart's span
  const best = useQuery({ queryKey: ["bestDasa", birth], queryFn: () => api.bestDasa(birth), enabled: !event && group === "nakshatra" });
  const isBest = (k: string) => !event && !!best.data?.best.includes(k);
  const titleOf = (k: string) => list.data?.find((d) => d.key === k)?.title ?? k;

  const g = GROUPS.find((x) => x.id === group)!;
  const key = chosen[group] ?? g.first;
  const of = JSON.stringify([birth, key]);
  const path = branch?.of === of ? branch.path : [];
  const setPath = (p: number[]) => setBranch({ of, path: p });
  const items: DasaItem[] = list.data?.filter((d) => d.group === group) ?? [];
  const item = list.data?.find((d) => d.key === key);
  const shift = shifts[key] ?? 0;
  const levels = useQueries({
    queries: [[], ...path.map((_, n) => path.slice(0, n + 1))].map((p: number[], n) => ({
      queryKey: ["dasa", birth, key, p, event, shift],
      queryFn: () => api.dasa(birth, key, p, event, natal!, shift),
      placeholderData: n ? undefined : (prev?: DasaLevel) => prev,
    })),
  });
  const shown: Shown = levels.map((q) => q.data);
  const failed = levels.find((q) => q.isError);
  const death = useDeath(natal ?? birth);   // with a death, the period it came in instead of today's
  const running = useQuery({
    queryKey: ["dasaRunning", birth, key, event, shift, death?.at],
    queryFn: () => {
      const t = new Date((death?.at ?? Date.now()) - shift * 60000);   // locate reads the dates before their shift
      return api.locate(birth, key, { year: t.getUTCFullYear(), month: t.getUTCMonth() + 1, day: t.getUTCDate(), hour_local: t.getUTCHours() + t.getUTCMinutes() / 60 + t.getUTCSeconds() / 3600, tz_east_hours: 0 }, LEVEL_NAMES.length, event, natal!);
    },
    staleTime: 0,   // today's period each time the view opens
  });
  useEffect(() => { if (!running.data || branch?.of === of) return; const p = running.data.path; setPath(p.slice(0, Math.min(RUNNING_DEPTH, p.length) - 1)); }, [running.data, birth, key]);
  const toNow = useCallback((el: HTMLTableRowElement | null) => el?.scrollIntoView({ block: "nearest" }), []);

  const entry = useMutation({
    mutationFn: (p: number[]) => api.entryChart(birth, key, p, event, natal!),
    onSuccess: (r) => enterMode(r.birth, modeOf(r)),
    onError: (e) => say("Entry chart", (e as Error).message),
  });
  const locate = async (when: Parameters<typeof api.locate>[2], depth: number) => {
    setForm(null);
    try {
      const r = await api.locate(birth, key, when, depth, event, natal!);
      if (r.path.length) setPath(r.path.slice(0, -1));
      say("Locate an event", r.path.length ? `Running at that time: ${r.labels.join(" > ")}` : "That moment is outside this dasa.");
    } catch (e) { say("Locate an event", (e as Error).message); }
  };
  const sum = async (p: number[]) => {
    try { say("Sum of Longitudes", (await api.sumOfLongitudes(birth, key, p, event, natal!)).text); } catch (e) { say("Sum of Longitudes", (e as Error).message); }
  };
  // the open period: the deepest one whose divisions are on show
  const openLabel = path.length ? shown[path.length - 1]?.periods[path[path.length - 1]]?.label : undefined;
  const run = (f: () => void) => () => { setForm(null); f(); };
  const tools: Tool[] = [
    { label: `Entry chart of ${openLabel ?? "the open period"}`, disabled: !path.length, onClick: run(() => entry.mutate(path)) },
    { label: "Dasa-Transit Correlation", disabled: !path.length, onClick: run(() => openWindow({ kind: "transit_correlation", key, path, title: "" })) },
    ...(group === "nakshatra" ? [
      { label: "Sum of longitudes of grahas upto this level", disabled: !path.length, onClick: run(() => sum(path)) },
      { label: "Vimsottari seed bala comparison help", onClick: run(() => openWindow({ kind: "seeds" })) }] : []),
    { label: "Locate an event", onClick: () => setForm("locate") },
    { label: "Shift dasa dates", onClick: () => setForm("shift") },
  ];
  // < and >: the period beside the one being divided, at the same level
  const siblings = shown[shown.length - 2];
  const last = path[path.length - 1];
  const stepTo = (d: number) => {
    if (siblings?.periods[last + d]) setPath([...path.slice(0, -1), last + d]);
  };
  const rows = (depth: number): React.ReactNode => shown[depth]?.periods.map((p, i) => {
    const here = [...path.slice(0, depth), i];
    const opened = path[depth] === i;
    const divides = shown[depth]!.can_split;
    const inBranch = here.every((x, k) => x === running.data?.path[k]);
    const now = inBranch && !(opened && shown[depth + 1]);   // the running period at the deepest level on show
    const toggle = () => { if (divides) setPath(opened ? path.slice(0, depth) : here); };
    return (
      <Fragment key={i}>
        <tr data-path={here.join()} data-label={p.label} data-depth={depth} style={{ "--level": depth, "--lv": `var(--dl-${depth})`, "--band": `var(--b${depth})` } as React.CSSProperties} className={[divides && "split", inBranch && "running", now && "now"].filter(Boolean).join(" ")} aria-current={inBranch || undefined}
            aria-expanded={divides ? opened : undefined} tabIndex={divides ? 0 : undefined} ref={now ? toNow : undefined}
            onClick={toggle} onKeyDown={(e) => { if (e.key === "Enter") toggle(); }}>
          <td><span className="twisty" aria-hidden="true">{divides ? (opened ? "▾" : "▸") : ""}</span>{p.label}</td>
          <td title={LEVEL_NAMES[depth]}><span className="level-tag">{LEVEL_TAGS[depth]}</span></td>
          <td className="num">{formatMoment(p.start)}</td><td className="num">{formatMoment(p.end)}</td>
          <td className="num">{formatDuration(p, !!event)}</td>
        </tr>
        {opened && rows(depth + 1)}
      </Fragment>
    );
  });

  return (
    <div className="right">
      <header className="lab-head">
        <div className="seg" role="tablist" aria-label="Kind of dasa">
          {GROUPS.map((x) => (
            <button key={x.id} role="tab" aria-selected={group === x.id} onClick={() => setGroup(x.id)}>{x.name}</button>
          ))}
        </div>
      </header>
      <section className="pane dasas printable">
        <div className="dasa-bar">
          <select aria-label="Dasa" value={key} onChange={(e) => setChosen({ ...chosen, [group]: e.target.value })}>
            {items.map((d) => <option key={d.key} value={d.key}>{isBest(d.key) ? "★ " : ""}{d.title}</option>)}
          </select>
          <span className="muted">{event && `${mode!.title}, fitted to its span.`}{shift ? `${event ? " " : ""}Shifted by ${shift} minutes.` : ""}</span>
          <span className="row dasa-nav">
            <button onClick={() => stepTo(-1)} disabled={!path.length || last === 0} aria-label="Previous period">‹</button>
            <button onClick={() => setPath(path.slice(0, -1))} disabled={!path.length} aria-label="Up one level">↑ Up</button>
            <button onClick={() => stepTo(1)} disabled={!path.length || !siblings?.periods[last + 1]} aria-label="Next period">›</button>
            <span className="bar-sep" />
            <button onClick={() => setForm("options")}>Options</button>
          </span>
        </div>
        {group === "nakshatra" && !event && best.data && (
          <p className="best-banner">
            <span aria-hidden="true">★</span> Best for this chart:{" "}
            {best.data.best.map((k, i) => (
              <span key={k}>{i > 0 && " or "}<button className="link" aria-current={k === key} onClick={() => setChosen({ ...chosen, [group]: k })}>{titleOf(k)}</button></span>
            ))}
            <span className="muted"> {best.data.best[0] === "vimsottari_dasa"
              ? (best.data.rows.some((r) => r.met) ? "No applicable conditional dasa has a strong controlling graha." : "None of the nine conditions holds.")
              : best.data.rows.filter((r) => isBest(r.key)).map((r) => `${r.planet}: ${strength(r)}`).join("; ") + (best.data.best.length > 1 ? ". Tied." : ".")}</span>
            {" "}<button className="link" onClick={() => setForm("best")}>Why?</button>
          </p>
        )}
        {failed && <p role="alert" className="error banner">{failed.error!.message}</p>}
        {!shown[0] ? !failed && <p className="empty">Calculating…</p> : (
          <div className="scroll tall">
            <table className={death ? "periods dasa-tree died" : "periods dasa-tree"}>
              <thead><tr><th>Period</th><th>Level</th><th>From</th><th>To</th><th title={event ? "From the dates, as this chart's dasa is fitted to its span" : "In this dasa's years: 12 months to a year, 30 days to a month. From and To can differ from it by a few days."}>Duration</th></tr></thead>
              <tbody>{rows(0)}</tbody>
            </table>
            <p className="muted hint">{running.data?.path.length === 0 && (death ? "No period of this dasa was running at the death. " : "No period of this dasa is running now. ")}Click a period to open or close its divisions; Options has its entry chart.</p>
          </div>
        )}
        {form === "options" && item && <DasaOptions item={item} tools={tools} onClose={() => setForm(null)} />}
        {form === "locate" && <LocateDialog onLocate={locate} onClose={() => setForm(null)} />}
        {form === "shift" && <ShiftDialog dasa={key} title={item?.title ?? ""} onClose={() => setForm(null)} />}
        {form === "best" && best.data && <BestDasaDialog best={best.data} title={titleOf} onClose={() => setForm(null)} />}
      </section>
    </div>
  );
}
