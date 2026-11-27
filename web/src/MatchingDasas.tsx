import { useQuery } from "@tanstack/react-query";
import { api, type Birth } from "./api";
import { formatDuration } from "./format";
import { useKept } from "./hooks";
import { type Side } from "./matchingShared";
import { WhoAge } from "./ui";

const MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const day = (iso: string) => `${Number(iso.slice(8, 10))} ${MON[Number(iso.slice(5, 7)) - 1]} ${iso.slice(0, 4)}`;
const GRAHAS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"];
/** A period's lord: a graha's full name for a mahadasa, Su Mo … below it; a sign as the dasa gives it. */
const graha = (label: string) => (label.length >= 3 ? GRAHAS.find((g) => g.startsWith(label.slice(0, 3))) : undefined);
const short = (label: string) => (graha(label) ? graha(label)!.slice(0, 2) : label);
const DEPTH = 3;    // mahadasa, antardasa, pratyantardasa

/** One level of a partner's dasa: each period with its dates and length, opening to the level below; the running one shaded,
 *  darker the higher its level. */
function Level({ birth, dkey, path, chain, run, open, onToggle }: {
  birth: Birth; dkey: string; path: number[]; chain: string[]; run: number[]; open: Set<string>; onToggle: (k: string) => void;
}) {
  const q = useQuery({ queryKey: ["dasa", birth, dkey, path, undefined, 0], queryFn: () => api.dasa(birth, dkey, path) });
  const depth = path.length;
  if (!q.data) return <p className="md-wait muted">{q.isError ? "Could not work these out" : "…"}</p>;
  return (
    <ol className={`md-level md-d${depth}`}>
      {q.data.periods.map((p, i) => {
        const at = [...path, i], k = at.join("."), names = [...chain, p.label];
        const running = at.every((x, n) => run[n] === x);
        const can = q.data!.can_split && depth < DEPTH - 1, shown = can && open.has(k);
        return (
          <li key={k} className={`md-p${running ? " now" : ""}`}>
            <button type="button" className="md-row" disabled={!can} aria-expanded={can ? shown : undefined} onClick={() => onToggle(k)}>
              <b>{depth ? names.map(short).join("–") : graha(p.label) ?? p.label}</b>
              <span className="md-when">{day(p.start)} – {day(p.end)}</span>
              <small className="md-len">{formatDuration(p)}</small>
              {can && <i aria-hidden="true">▾</i>}
            </button>
            {shown && <Level birth={birth} dkey={dkey} path={at} chain={names} run={run} open={open} onToggle={onToggle} />}
          </li>
        );
      })}
    </ol>
  );
}

/** One partner's dasas: the dasa picked beside the name, Vimsottari to start with (the one that suits the chart starred); the running mahadasa and
 *  antardasa open to start with, so the running pratyantardasa shows. */
function DasaList({ label, side }: { label: string; side: Side }) {
  const who = label.toLowerCase(), birth = side.birth, chart = JSON.stringify(birth);
  const list = useQuery({ queryKey: ["dasaList"], queryFn: api.dasaList, staleTime: Infinity });
  const best = useQuery({ queryKey: ["bestDasa", birth], queryFn: () => api.bestDasa(birth) });
  const [picked, setPicked] = useKept<{ of: string; key: string } | null>(`match.dasaKey.${who}`, null);
  const dkey = picked?.of === chart ? picked.key : "vimsottari_dasa";
  const of = JSON.stringify([birth, dkey]);
  const running = useQuery({
    queryKey: ["dasaRunning", birth, dkey, "match"],
    queryFn: () => {
      const t = new Date();
      return api.locate(birth, dkey, { year: t.getUTCFullYear(), month: t.getUTCMonth() + 1, day: t.getUTCDate(), hour_local: t.getUTCHours() + t.getUTCMinutes() / 60, tz_east_hours: 0 }, DEPTH);
    },
    staleTime: 0,
  });
  const run = running.data?.path ?? [];
  const [kept, setKept] = useKept<{ of: string; open: string[] } | null>(`match.dasaOpen.${who}`, null);
  const open = new Set(kept?.of === of ? kept.open : run.slice(0, DEPTH - 1).map((_, n) => run.slice(0, n + 1).join(".")));
  const toggle = (k: string) => { const next = new Set(open); if (next.has(k)) next.delete(k); else next.add(k); setKept({ of, open: [...next] }); };
  const isBest = (k: string) => !!best.data?.best.includes(k);
  return (
    <section className="md-side">
      <header className="md-head">
        <h4><WhoAge who={label} birth={side.birth} /></h4>
        <select aria-label={`${label}'s dasa`} value={dkey ?? ""} onChange={(e) => setPicked({ of: chart, key: e.target.value })}>
          {(["nakshatra", "rasi", "other"] as const).map((g) => (
            <optgroup key={g} label={{ nakshatra: "Nakshatra dasas", rasi: "Rasi dasas", other: "Other dasas" }[g]}>
              {list.data?.filter((d) => d.group === g).map((d) => <option key={d.key} value={d.key}>{isBest(d.key) ? "★ " : ""}{d.title}</option>)}
            </optgroup>
          ))}
        </select>
      </header>
      <Level birth={birth} dkey={dkey} path={[]} chain={[]} run={run} open={open} onToggle={toggle} />
    </section>
  );
}

/** The girl's and the boy's dasas side by side. */
export function MatchDasaLists({ girl, boy }: { girl: Side; boy: Side }) {
  return (
    <div className="md-sides">
      <DasaList label="Girl" side={girl} />
      <DasaList label="Boy" side={boy} />
    </div>
  );
}
