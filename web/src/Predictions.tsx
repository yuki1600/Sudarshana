/** The Predictions tab: what is true of the native, picked from chips, kept with the account under the chart's name and birth date. */
import { useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "./api";
import { Icon } from "./Icons";
import { useChart } from "./store";
import { Loaded, supOrd } from "./ui";
import { answerText, chartKey, COUNTS, EMPTY, EVENT_KINDS, OTHER, SECTIONS, visible, type Answer, type Answers, type Facts, type LifeEvent, type Question } from "./lifeFacts";
import { useKept } from "./hooks";

type Patch = Record<string, Answer | undefined>;
const THIS_YEAR = new Date().getFullYear();
/** A year as typed: a whole number from 1800 to 50 years ahead, else undefined. */
const readYear = (s: string) => { const y = Number(s.trim()); return s.trim() && Number.isInteger(y) && y >= 1800 && y <= THIS_YEAR + 50 ? y : undefined; };

/** One of the options, or none: clicking the chosen one again clears it. */
function Chips({ options, value, onPick, label, round }: { options: string[]; value: number | undefined; onPick: (i: number | undefined) => void; label: string; round?: boolean }) {
  return (
    <div className={round ? "pred-chips round" : "pred-chips"} role="group" aria-label={label}>
      {options.map((o, i) => <button key={o} type="button" className="pred-chip" aria-pressed={value === i} onClick={() => onPick(value === i ? undefined : i)}>{o}</button>)}
    </div>
  );
}

/** Free text, kept on leaving the box or Enter; focused when it opens empty (just after "Other" was picked). */
function TextField({ label, value, placeholder, onCommit }: { label: string; value: string; placeholder: string; onCommit: (v: string) => void }) {
  const [text, setText] = useState(value);
  const commit = () => { if (text.trim() !== value) onCommit(text.trim()); };
  return (
    <input className="pred-text" aria-label={label} placeholder={placeholder} value={text} maxLength={80} autoFocus={!value}
      onChange={(e) => setText(e.target.value)} onBlur={commit} onKeyDown={(e) => { if (e.key === "Enter") commit(); }} />
  );
}

/** A year, kept on leaving the box or Enter; "≈" marks it as rough. */
function YearField({ label, value, approx, onYear, onApprox }: { label: string; value: number | undefined; approx: boolean; onYear: (y: number | undefined) => void; onApprox: (a: boolean) => void }) {
  const [text, setText] = useState(value?.toString() ?? "");
  const bad = text.trim() !== "" && readYear(text) === undefined;
  const commit = () => { const y = readYear(text); if (!bad && y !== value) onYear(y); };
  return (
    <span className="pred-year">
      <input className="pred-text" inputMode="numeric" aria-label={label} placeholder="Year" value={text} aria-invalid={bad} title={bad ? `A year from 1800 to ${THIS_YEAR + 50}` : undefined}
        onChange={(e) => setText(e.target.value)} onBlur={commit} onKeyDown={(e) => { if (e.key === "Enter") commit(); }} />
      <button type="button" className="pred-chip" aria-pressed={approx} title="Roughly this year" onClick={() => onApprox(!approx)}>≈ approx</button>
    </span>
  );
}

/** Alive, the default, or dead: then the date of death, and its time if known (local, as the birth's). */
function LifeStatus({ a, patch }: { a: Answers; patch: (p: Patch) => void }) {
  const dead = a.status === "Dead";
  return (
    <div className={dead ? "pred-life dead" : "pred-life"}>
      <label>Person's status
        <select value={dead ? "Dead" : "Alive"} onChange={(e) => patch(e.target.value === "Dead" ? { status: "Dead" } : { status: undefined, "death.date": undefined, "death.time": undefined })}>
          <option>Alive</option><option>Dead</option>
        </select>
      </label>
      {dead && (<>
        <label>Date of death
          <input type="date" value={(a["death.date"] as string) ?? ""} onChange={(e) => patch({ "death.date": e.target.value || undefined })} />
        </label>
        <label>Time
          <input type="time" value={(a["death.time"] as string) ?? ""} onChange={(e) => patch({ "death.time": e.target.value || undefined })} />
        </label>
      </>)}
    </div>
  );
}

function Row({ q, a, patch }: { q: Question; a: Answers; patch: (p: Patch) => void }) {
  const v = a[q.id];
  if (q.kind === "year") {
    return (
      <div className="pred-q">
        <span className="pred-label">{q.label}</span>
        <YearField label={q.label} value={v as number | undefined} approx={!!a[`${q.id}.approx`]}
          onYear={(y) => patch({ [q.id]: y })} onApprox={(x) => patch({ [`${q.id}.approx`]: x || undefined })} />
      </div>
    );
  }
  const count = q.kind === "count";
  const options = count ? COUNTS : q.options!;
  const at = v === undefined ? undefined : count && v !== OTHER ? (v as number) : options.indexOf(v as string);
  // a pick other than "Other" drops the text typed for it
  const pick = (i: number | undefined) => {
    const value = i === undefined ? undefined : options[i] === OTHER ? OTHER : count ? i : options[i];
    patch({ [q.id]: value, ...(value === OTHER ? {} : { [`${q.id}.other`]: undefined }) });
  };
  return (
    <div className="pred-q">
      <span className="pred-label">{q.label}</span>
      <Chips label={q.label} options={options} value={at} onPick={pick} round={count} />
      {v === OTHER && <TextField label={`${q.label}: other`} value={String(a[`${q.id}.other`] ?? "")} placeholder={count ? "How many?" : "Type it in"}
        onCommit={(t) => patch({ [`${q.id}.other`]: t || undefined })} />}
    </div>
  );
}

/** Free notes, kept a moment after the last key and on leaving the box, so a refresh loses nothing typed. */
function Notes({ value, onCommit }: { value: string; onCommit: (v: string) => void }) {
  const [text, setText] = useState(value);
  const timer = useRef(0);
  const commit = (t: string) => { clearTimeout(timer.current); if (t !== value) onCommit(t); };
  return (
    <textarea className="pred-text pred-notes" aria-label="Notes" placeholder="Anything else about the native: what no question above asks…" value={text}
      onChange={(e) => { const t = e.target.value; setText(t); clearTimeout(timer.current); timer.current = window.setTimeout(() => onCommit(t), 800); }}
      onBlur={() => commit(text)} />
  );
}

/** Other dated events, oldest first: add one with a year, a kind and a note; remove with the cross. */
function Events({ events, onChange }: { events: LifeEvent[]; onChange: (e: LifeEvent[]) => void }) {
  const [year, setYear] = useKept("predictions.event.year", "");
  const [approx, setApprox] = useKept("predictions.event.approx", false);
  const [kind, setKind] = useKept("predictions.event.kind", 0);
  const [otherKind, setOtherKind] = useKept("predictions.event.other", "");
  const [note, setNote] = useKept("predictions.event.note", "");
  const y = readYear(year);
  const isOther = EVENT_KINDS[kind] === OTHER;
  const add = () => {
    if (y === undefined) return;
    const id = crypto.randomUUID?.() ?? `e-${Date.now()}`;
    const k = isOther ? otherKind.trim() || OTHER : EVENT_KINDS[kind];
    onChange([...events, { id, year: y, approx, kind: k, note: note.trim() }].sort((p, q) => p.year - q.year));
    setYear(""); setApprox(false); setNote(""); setOtherKind("");
  };
  return (
    <>
      {events.length > 0 ? (
        <ol className="pred-events">
          {events.map((e) => (
            <li key={e.id}>
              <span className="pred-when">{e.approx ? "≈ " : ""}{e.year}</span>
              <span className="pred-kind">{e.kind}</span>
              <span className="pred-note">{supOrd(e.note)}</span>
              <button type="button" className="icon-btn" aria-label={`Remove ${e.kind}, ${e.year}`} title="Remove" onClick={() => onChange(events.filter((x) => x.id !== e.id))}><Icon name="close" /></button>
            </li>
          ))}
        </ol>
      ) : <p className="pred-empty">No events yet: accidents, moves, losses, turning points…</p>}
      <form className="pred-add" onSubmit={(e) => { e.preventDefault(); add(); }}>
        <Chips label="Kind of event" options={EVENT_KINDS} value={kind} onPick={(i) => setKind(i ?? kind)} />
        <div className="pred-add-row">
          <span className="pred-year">
            <input className="pred-text" inputMode="numeric" aria-label="Event year" placeholder="Year" value={year} aria-invalid={year.trim() !== "" && y === undefined} onChange={(e) => setYear(e.target.value)} />
            <button type="button" className="pred-chip" aria-pressed={approx} title="Roughly this year" onClick={() => setApprox(!approx)}>≈ approx</button>
          </span>
          {isOther && <input className="pred-text" aria-label="What kind of event" placeholder="What kind?" value={otherKind} maxLength={40} autoFocus onChange={(e) => setOtherKind(e.target.value)} />}
          <input className="pred-text grow" aria-label="Note" placeholder="Note (optional)" value={note} maxLength={200} onChange={(e) => setNote(e.target.value)} />
          <button type="submit" className="primary" disabled={y === undefined}><Icon name="plus" /> Add</button>
        </div>
      </form>
    </>
  );
}

function Form({ chart, facts }: { chart: string; facts: Facts }) {
  const client = useQueryClient();
  // one chart's saves run in order, so a slow one never lands after a later one; each sends everything, so a failed one is made good by the next
  const save = useMutation({ mutationFn: (f: Facts) => api.saveFacts(chart, f), scope: { id: `facts:${chart}` } });
  const update = (f: Facts) => { client.setQueryData(["facts", chart], f); save.mutate(f); };
  const patch = (p: Patch) => {
    const answers = { ...facts.answers };
    for (const [id, v] of Object.entries(p)) { if (v === undefined) delete answers[id]; else answers[id] = v; }
    update({ ...facts, answers });
  };
  const a = facts.answers;
  return (
    <section className="pane pred">
      {save.isError && <p role="alert" className="error banner">Couldn't save: {save.error.message}. Your next change will try again.</p>}
      <div className="scroll pred-body"><LifeStatus a={a} patch={patch} /><div className="pred-grid">
        {SECTIONS.map((s) => {
          const asked = visible([s], a);
          const done = asked.filter((q) => answerText(q, a) !== undefined).length;
          return (
            <section key={s.title} className="pred-card" data-done={done === asked.length}>
              <header><h3>{s.title}</h3><span className="pred-count">{done === asked.length ? "Done" : `${done}/${asked.length}`}</span></header>
              {asked.map((q) => <Row key={q.id} q={q} a={a} patch={patch} />)}
            </section>
          );
        })}
        <section className="pred-card wide">
          <header><h3>Other events</h3><span className="pred-count">{facts.events.length || ""}</span></header>
          <Events events={facts.events} onChange={(events) => update({ ...facts, events })} />
        </section>
        <section className="pred-card wide">
          <header><h3>Notes</h3></header>
          {/* the facts as they are when the note is kept: a chip picked while it waited must not be undone */}
          <Notes value={facts.notes} onCommit={(notes) => update({ ...(client.getQueryData<Facts>(["facts", chart]) ?? facts), notes })} />
        </section>
        <p className="muted hint wide">Kept with your account, under this chart's name and birth date: renaming the chart starts a fresh page.</p>
      </div></div>
    </section>
  );
}

export function Predictions() {
  const { name, natal } = useChart();
  const chart = chartKey(name, natal!);
  const q = useQuery({ queryKey: ["facts", chart], queryFn: async () => ({ ...EMPTY, ...(await api.facts(chart)).data }) });
  return <div className="right"><Loaded q={q}>{(facts) => <Form key={chart} chart={chart} facts={facts} />}</Loaded></div>;
}
