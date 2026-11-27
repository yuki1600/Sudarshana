/** The shared parts of the analysis tabs (Strengths, Dasas, Tajaka, Tithi Pravesha, Transits): meters, the tone key, stats. */
import { clamp01, toneStyle } from "./tone";
import { supOrd } from "./ui";

/** A bar for a number shown beside it: ``fill`` is how full, ``t`` how strong, ``mark`` an optional threshold tick. */
export function Meter({ t, fill, mark }: { t: number; fill: number; mark?: number }) {
  return (
    <span className="meter tone" style={toneStyle(t)} aria-hidden="true">
      <i style={{ width: `${clamp01(fill) * 100}%` }} />
      {mark !== undefined && <b style={{ left: `${clamp01(mark) * 100}%` }} />}
    </span>
  );
}

/** The key to the tones: five steps from weak to strong. */
export function ToneLegend({ weak = "Weak", strong = "Strong" }: { weak?: string; strong?: string }) {
  return (
    <span className="tone-legend">
      {weak}{[0, 0.25, 0.5, 0.75, 1].map((t) => <i key={t} className="tone" style={toneStyle(t)} />)}{strong}
    </span>
  );
}

/** One fact in a stat strip: a label over a value, toned when it says how strong something is. */
export function Stat({ label, value, sub, t, onClick }: { label: string; value: React.ReactNode; sub?: React.ReactNode; t?: number; onClick?: () => void }) {
  const Box = onClick ? "button" : "div";
  return (
    <Box type={onClick ? "button" : undefined} onClick={onClick} className={t === undefined ? "stat" : "stat tone"} style={t === undefined ? undefined : toneStyle(t)}>
      <span className="stat-label">{label}</span>
      <span className="stat-value">{supOrd(value)}</span>
      {sub && <span className="stat-sub">{supOrd(sub)}</span>}
    </Box>
  );
}

