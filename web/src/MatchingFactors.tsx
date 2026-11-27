import { type Birth, type MatchArea, type MatchCell, type MatchTone } from "./api";
import { ord } from "./Calculations";
import { SIGN_NAMES } from "./format";
import { Icon } from "./Icons";
import { signName } from "./names";
import { ABBR_NAME } from "./Panels";
import { useChart } from "./store";
import { Dignity, supOrd, WhoAge } from "./ui";

/** An area's verdict in a word; a dosha area's bad is a dosha. */
export const toneWord = (t: MatchTone, doshas = false) => (t === "good" ? "Good" : t === "mid" ? "Mixed" : t === "bad" ? (doshas ? "Dosha" : "Weak") : "");

export const pctTone = (p: number): "good" | "mid" | "bad" => (p >= 100 ? "good" : p >= 85 ? "mid" : "bad");

/** A graha's strength (Shadbala) as a ring round, closing at its minimum (100%), anything past it a second, darker lap. */
const RingShape = ({ pct }: { pct: number }) => {
  const lap = (f: number) => `${Math.max(0, Math.min(f, 1)) * 100} 100`;
  return (
    <span className="mc-ring">
      <svg viewBox="0 0 36 36" aria-hidden="true">
        <circle className="mc-ring-track" cx="18" cy="18" r="15" pathLength={100} />
        <circle className="mc-ring-fill" cx="18" cy="18" r="15" pathLength={100} strokeDasharray={lap(pct / 100)} />
        {pct > 100 && <circle className="mc-ring-over" cx="18" cy="18" r="15" pathLength={100} strokeDasharray={lap(pct / 100 - 1)} />}
      </svg>
    </span>
  );
};

/** A bhava's strength (Bhava Bala) as a house filling up: the walls hold its minimum (100%, the 7 rupas), the eaves line marks it,
 *  and anything past it rises into the roof, darker, full at twice the minimum. */
const HouseShape = ({ pct }: { pct: number }) => {
  const p = Math.max(0, pct) / 100;
  const wall = 33 - 18 * Math.min(p, 1);
  const top = 15 - 12 * Math.min(Math.max(p - 1, 0), 1);
  const half = (y: number) => (15 * (y - 3)) / 12;      // the roof's half width at height y
  return (
    <span className="mc-house">
      <svg viewBox="0 0 36 36" aria-hidden="true">
        <path className="mc-house-track" d="M18 3 33 15V33H3V15Z" />
        <g className="mc-house-fill">
          <rect x="3" y={wall} width="30" height={33 - wall} />
          {p > 1 && <polygon className="mc-house-over" points={`3,15 33,15 ${18 + half(top)},${top} ${18 - half(top)},${top}`} />}
        </g>
        <line className="mc-house-need" x1="3" x2="33" y1="15" y2="15" />
      </svg>
    </span>
  );
};

/** A strength as a share of its minimum, the % beside its shape: a graha's a ring, a bhava's a house, so the two never read alike. */
export const Strength = ({ pct, kind, tone = pctTone(pct), tip }: { pct: number; kind: "graha" | "bhava"; tone?: "good" | "mid" | "bad"; tip?: string }) => (
  <span className={`mc-strength ${kind} ${tone}`} data-tip={tip}>
    {kind === "graha" ? <RingShape pct={pct} /> : <HouseShape pct={pct} />}
    <b>{pct}%</b>
  </span>
);

/** A cell's sign in full as the charts name it (Taurus; with Sanskrit names Vrish, in a language its own name) */
const useSign = () => {
  const { display } = useChart();
  return (s?: string) => {
    const i = s ? SIGN_NAMES.indexOf(s) : -1;
    return i >= 0 ? signName(i, SIGN_NAMES[i], display) : s ?? "";
  };
};

/** A value: a graha's or a bhava's from its parts. On the left its strength, named under its % (Shadbala, Bhava Bala), one width
 *  so the strengths read down a column; then in words which graha and sign it is about and where it sits ("Venus in Taurus" over
 *  "2nd bhava"; a bhava's "Taurus · holds Ma Ve" over "lord Ju in 9th"). Anything else as text. The whole reading on hover. */
export const Value = ({ c }: { c: MatchCell }) => {
  const sign = useSign();
  if (c.parts) return <span className="mc-box mc-parts" title={c.hint || undefined}>{c.parts.map((x, i) => <span key={i} className={`mc-box mc-part${x.tone ? ` ${x.tone}` : ""}`}>{supOrd(x.text)}{x.dig && <Dignity d={x.dig} />}</span>)}</span>;
  if (c.h == null && c.pct === undefined) return <span className={`mc-box${c.tone ? ` ${c.tone}` : ""}`} title={c.hint || undefined}>{c.text ? supOrd(c.text) : <small>–</small>}</span>;
  const bhava = c.g == null && c.h == null;
  return (
    <span className={`mc-box mv${c.tone ? ` ${c.tone}` : ""}`} title={c.hint || undefined}>
      {c.pct != null && <span className="mv-pct">
        <Strength pct={c.pct} kind={bhava ? "bhava" : "graha"} />
        <span className="mv-what">{bhava ? "Bhava Bala" : "Shadbala"}</span>
      </span>}
      <span className="mv-text">
        {bhava ? <>
          <span className="mv-line">{c.s && <b>{sign(c.s)}</b>}{c.holds?.length ? <span>· holds <b className="mv-holds">{c.holds.join(" ")}</b></span> : <span className="mv-empty">· empty</span>}</span>
          {c.lord && <span className="mv-line mv-sub">lord {c.lord.g} in {supOrd(ord(c.lord.h))}</span>}
        </> : <>
          <span className="mv-line"><b>{c.g ? `${ABBR_NAME[c.g] ?? c.g} in ` : ""}{sign(c.s)}</b><Dignity d={c.dig} vg={c.vg} /></span>
          {c.h != null && <span className="mv-line mv-sub">{supOrd(ord(c.h))} bhava</span>}
        </>}
      </span>
    </span>
  );
};

/** What a factor or a category is, on hover (an instant tip, IconTips: a title on a span over an svg never came up). */
export const Info = ({ text }: { text: string }) => (
  <span className="mf-info" data-tip={text} aria-label={text} role="img"><Icon name="info" /></span>
);

/** The factors: a block per area, its name and verdict atop, centred (a button to its sub tab when ``onArea`` is given), then a row per
 *  factor, the girl's value and the boy's (each heading with their age), the factor's rule on its ⓘ. What the two charts give read
 *  together (``r.together``) is left out under the factor for now, at the user's ask (2026-11-27). ``heads`` off: an area's own sub tab,
 *  which names it already; "quiet": a sub tab of two areas, each named small, with room between them. */
export function FactorTable({ areas, births, onArea, heads = true }: { areas: MatchArea[]; births: { girl: Birth; boy: Birth }; onArea?: (id: MatchArea["id"]) => void; heads?: boolean | "quiet" }) {
  return (
    <div className="mc-tablewrap">
      <table className="mf-table" aria-label="Matching factors">
        <colgroup><col className="mf-col-factor" /><col /><col /></colgroup>
        <thead>
          <tr><th scope="col">Factor</th><th scope="col"><WhoAge who="Girl" birth={births.girl} /></th><th scope="col"><WhoAge who="Boy" birth={births.boy} /></th></tr>
        </thead>
        {areas.map((a) => (
          <tbody key={a.id} className={`mf-area ${a.tone ?? ""}`}>
            {heads === "quiet" && <tr className="mf-quiet"><th scope="rowgroup" colSpan={3}>{a.name}</th></tr>}
            {heads === true && <tr className="mf-head">
              <th scope="rowgroup" colSpan={3}>
                {onArea ? <button type="button" onClick={() => onArea(a.id)} title={`Open ${a.name}`}>{a.name}</button> : <span>{a.name}</span>}
                {a.tone && <i className={`mc-box ${a.tone}`}>{toneWord(a.tone, a.id === "doshas")}</i>}
              </th>
            </tr>}
            {a.rows.map((r) => (
              <tr key={r.key}>
                <th scope="row">
                  <span className="mf-factor"><span className="mf-name">{r.factor}{r.about && <small>{r.about}</small>}</span><Info text={r.rule} /></span>
                </th>
                <td><Value c={r.girl} /></td>
                <td><Value c={r.boy} /></td>
              </tr>
            ))}
          </tbody>
        ))}
      </table>
    </div>
  );
}
