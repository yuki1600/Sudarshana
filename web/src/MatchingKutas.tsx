import { type MatchDetail } from "./api";
import { useKept } from "./hooks";
import { CopyButton, supOrd, tableText } from "./ui";
import { KUTA_LABEL, KUTA_ORDER } from "./matchingShared";

export const toneA = (s: number) => (s >= 31 ? "ex" : s >= 21 ? "gd" : s >= 17 ? "av" : "lo");     // the Ashtakuta bands
export const toneD = (s: number) => (s >= 6.5 ? "ex" : s >= 4.5 ? "gd" : s >= 3 ? "av" : "lo");      // the Dashakuta (porutham) bands
export const num = (x: number) => (Number.isInteger(x) ? String(x) : x.toFixed(1));


const GRADE_TONE = { Uttama: "same", Madhyama: "sign", Adhama: "diff" } as const;

/** What each kuta reads, for its row's open text. */
const ASHTA_ABOUT: Record<string, string> = {
  varna: "Temperament and ego: the varna of each Moon sign; the boy's should be equal to or above the girl's.",
  vashya: "Mutual attraction and give-and-take: the class of each Moon sign (human, quadruped, water, wild, insect); Sagittarius and Capricorn change class at 15°.",
  tara: "Luck and health: each one's birth star counted from the other's, in nines; the 3rd, 5th and 7th of a nine are unlucky.",
  yoni: "Physical and intimate harmony: the animal of each birth star, from the same animal (4) to sworn enemies (0).",
  graha_maitri: "Mental bond: how the lords of the two Moon signs regard each other.",
  gana: "Nature: Deva, Manushya or Rakshasa by birth star; a Rakshasa with either of the others loses the points.",
  bhakoota: "Family welfare and prosperity: Moon signs 2/12, 6/8 or 5/9 from each other lose all 7 (a friendly pair of lords softens it but restores no points).",
  nadi: "Health and children: the same nadi (Adi, Madhya, Antya) loses all 8, the gravest fault of the eight.",
};
const DASHA_ABOUT: Record<string, string> = {
  Dina: "Health and everyday well-being: the boy's star counted from the girl's, in nines (2nd, 4th, 6th, 8th, 9th good).",
  Gana: "Nature: Deva, Manushya or Rakshasa; the same gana is best, a Rakshasa with another is a fault.",
  Mahendra: "Prosperity and children: the boy's star the 4th, 7th, 10th, 13th, 16th, 19th, 22nd or 25th from the girl's.",
  "Stree Deergha": "The wife's welfare: the boy's star well beyond the girl's, past the 13th best.",
  Yoni: "Physical harmony: the animals of the two stars.",
  Rasi: "The Moon signs from each other: 2/12, 6/8 and 5/9 are faults, softened when their lords are friends.",
  Rasyadhipati: "Friendship of the two Moon signs' lords.",
  Vasya: "Attraction: Moon signs that are vasya to (drawn to) each other.",
  Rajju: "The marriage's life: both stars on one rajju (cord: feet, waist, navel, neck, head) is held the gravest fault.",
  Vedha: "Obstruction: stars that pierce each other (Ashwini–Jyeshtha and so on) block the match.",
};

const TARA = ["Janma", "Sampat", "Vipat", "Kshema", "Pratyak", "Sadhana", "Naidhana", "Mitra", "Parama Mitra"];
const taraName = (n: unknown) => { const i = Number(n); return i ? `${TARA[i - 1]} (${i}${i === 1 ? "st" : i === 2 ? "nd" : i === 3 ? "rd" : "th"})` : ""; };
const taraGood = (n: unknown) => ([3, 5, 7].includes(Number(n)) ? "unlucky" : "lucky");

/** Each kuta's girl and boy value (the girl first, as her charts are on the left), full names; Tara is the tara each one's star falls in, counted from the other's. */
function kutaPair(d: MatchDetail, x: string): [string, string] {
  const f = d.ashta_kuta_breakdown[x] ?? {};
  const get = (k: string) => String(f[k] ?? "");
  switch (x) {
    case "tara": return [taraName(f.groom_to_bride_tara), taraName(f.bride_to_groom_tara)];
    case "graha_maitri": return [get("bride_lord"), get("groom_lord")];
    case "bhakoota": return [d.bride.moon_rasi, d.groom.moon_rasi];
    default: return [get(`bride_${x}`), get(`groom_${x}`)];
  }
}
const bare = (s: string) => s.replace(/ \(.*\)$/, "");
/** A porutham's reason in two: what the row shows ("7th star from the girl's") and the rest for when it opens ("beyond 13th good, …").
 *  One that compares the two's own values (gana, yoni …) has them in the Girl and Boy columns; what its reason adds ("friend / neutral") opens. */
function split(x: MatchDetail["dashakoota"]["kutas"][number]): [string, string] {
  if (x.girl || x.boy) return ["", x.status.replace(`Girl ${x.girl}, boy ${x.boy}`, "").replace(`${x.girl} / ${x.boy}`, "").replace(/^[:,\s]+/, "")];
  const m = / \((.*)\)$/.exec(x.status);
  return m ? [x.status.slice(0, m.index), m[1]] : [x.status, ""];
}

/** What the pair line under a kuta's text adds for Tara and Bhakoota. */
function kutaHow(d: MatchDetail, x: string): string | null {
  const f = d.ashta_kuta_breakdown[x] ?? {};
  if (x === "tara") return `The girl's star from the boy's is ${taraName(f.groom_to_bride_tara)}, ${taraGood(f.groom_to_bride_tara)}; the boy's from the girl's is ${taraName(f.bride_to_groom_tara)}, ${taraGood(f.bride_to_groom_tara)}. Each lucky way gives 1.5.`;
  if (x === "bhakoota" && f.placement) return `The Moon signs are ${String(f.placement)} from each other.`;
  return null;
}

/** Ashtakuta and Dashakuta side by side: each total, then each kuta a row of its name, the girl's value, the boy's and its score; a kuta opens to what it reads and why this pair got it (all open in the popup).
 *  ``fold`` (the Overview): only the two totals, either of which opens both lists of kutas, and the choice survives a refresh. */
export function KutaTables({ d, open = false, fold = false }: { d: MatchDetail; open?: boolean; fold?: boolean }) {
  const k = d.dashakoota;
  const [unfolded, setUnfolded] = useKept("match.kutasOpen", false);
  const shown = !fold || unfolded;
  const rows = KUTA_ORDER.map((x) => {
    const f = d.ashta_kuta_breakdown[x];
    return [KUTA_LABEL[x], ...kutaPair(d, x), String(f?.obtained_points ?? ""), String(f?.max_points ?? ""), String(f?.status ?? "")];
  });
  const text = tableText(["Kuta", "Girl", "Boy", "Score", "Max", "Status"], rows) + "\n\n" +
    tableText(["Porutham", "Girl", "Boy", "Grade", "Points", "Why"], k.kutas.map((x) => [x.kuta, x.girl, x.boy, x.grade, String(x.points), x.status]));
  const card = (name: string, note: string, score: number, max: number, level: string) => (
    <>
      <span><span className="muted">{name} · {note}</span><strong>{level}</strong></span>
      <b>{num(score)}<small>/{max}</small></b>
    </>
  );
  const head = (name: string, note: string, score: number, max: number, level: string, tone: string) => fold ? (
    <button type="button" className={`mc-scorecard mc-fold ${tone}`} aria-expanded={unfolded} onClick={() => setUnfolded(!unfolded)}
      title={unfolded ? "Hide the kutas" : "Show the kutas one by one"}>{card(name, note, score, max, level)}<i aria-hidden="true">▾</i></button>
  ) : <header className={`mc-scorecard ${tone}`}>{card(name, note, score, max, level)}</header>;
  const cols = shown && <div className="mc-kuta-cols" aria-hidden="true"><span /><span>Girl</span><span>Boy</span><span /></div>;
  return (
    <>
      <div className="mc-kutas">
        <section className="mc-ashta">
          {head("Ashtakuta", "8 kutas", d.gunanka_score, 36, d.match_level, toneA(d.gunanka_score))}
          {cols}
          {shown && KUTA_ORDER.map((x) => {
            const f = d.ashta_kuta_breakdown[x];
            const share = f ? f.obtained_points / f.max_points : 0;
            const [girl, boy] = kutaPair(d, x), how = kutaHow(d, x);
            return (
              <details key={x} open={open} className={`mc-kuta ${share >= 0.75 ? "same" : share > 0 ? "sign" : "diff"}`}>
                <summary title={`Girl ${girl} · Boy ${boy}`}><b>{KUTA_LABEL[x]}</b><i>{supOrd(bare(girl))}</i><i>{supOrd(bare(boy))}</i><span>{num(f?.obtained_points ?? 0)}/{f?.max_points}</span></summary>
                <p>{ASHTA_ABOUT[x]}</p>
                <p>Girl: <b>{supOrd(girl)}</b> · Boy: <b>{supOrd(boy)}</b></p>
                {how && <p>{supOrd(how)}</p>}
                <p className="muted">Here: {String(f?.status ?? "")}</p>
              </details>
            );
          })}
        </section>
        <section className="mc-dasha">
          {head("Dashakuta", "10 poruthams", k.score, 10, k.level, toneD(k.score))}
          {cols}
          {shown && k.kutas.map((x) => {
            const [short, note] = split(x);
            return (
              <details key={x.kuta} open={open} className={`mc-kuta ${GRADE_TONE[x.grade]}`}>
                <summary title={`${x.grade}: ${x.status}`}><b>{x.kuta}</b>
                  {short ? <i className="mc-both">{supOrd(short)}</i> : <><i>{x.girl}</i><i>{x.boy}</i></>}
                  <span>{num(x.points)}</span></summary>
                <p>{DASHA_ABOUT[x.kuta]}</p>
                <p className="mc-note">{x.grade}, {num(x.points)} of 1{note ? `: ${note}` : ""}</p>
              </details>
            );
          })}
        </section>
      </div>
      {shown && <div className="row bottom-gap mc-copy"><CopyButton text={text} /></div>}
    </>
  );
}

export function Breakdown({ d }: { d: MatchDetail }) {
  return (
    <section className="match-break">
      <p className="muted">
        Ashtakuta is the 8 kutas worked out from the Moons with the usual tables (Sagittarius and Capricorn split at 15° for Vashya). The pada table reads the same sum from
        a fixed table and gives <strong>{d.pada_score}</strong> ({d.pada_level}): its table rounds the half points and works by nakshatra, so the two differ by a point or so.
        A Bhakoota or Nadi dosha's cancellation is noted in its row but restores no points. Dashakuta grades each porutham Uttama 1, Madhyama ½, Adhama 0.
      </p>
      <p className="muted">{d.bride.nakshatra} {d.bride.moon_rasi} (girl) × {d.groom.nakshatra} {d.groom.moon_rasi} (boy)</p>
      <KutaTables d={d} open />
    </section>
  );
}
