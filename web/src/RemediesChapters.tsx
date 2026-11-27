import { useState, type CSSProperties, type ReactNode } from "react";
import { useChart } from "./store";
import { CONDITION_META, type Item, PLANET_DATA, VASARA, WEEKDAY_GRAHA, plural, press, short, words } from "./remediesData";
import { Sloka, Split, Verses } from "./RemediesVerses";
import { useKept } from "./hooks";

/* -------------------------------------------------------------------------- */
/*                         1. KARMA: THE ARCHER'S QUIVER                       */
/* -------------------------------------------------------------------------- */

const KARMAS: { name: string; gloss: string; image: string; what: string; change: string; icon: ReactNode }[] = [
  {
    name: "Sañcita", gloss: "stored", image: "The arrows still in the quiver",
    what: "All the karma gathered over countless births that has not yet begun to bear fruit.",
    change: "It can be burnt before it ever ripens. The fire of knowledge turns karma to ashes (Gītā 4.37), and in the Śrī Vaiṣṇava teaching śaraṇāgati destroys it entirely.",
    icon: <><path d="M15 18 19 44h10l4-26z" /><path d="M19 18 16 4M24 18V3M29 18l3-14M13 7l3-3 3 3M21 6l3-3 3 3M29 7l3-3 3 3" /></>,
  },
  {
    name: "Prārabdha", gloss: "begun", image: "The arrow already loosed",
    what: "The portion of sañcita that has started to ripen. It made this body and shapes this life, and it is what the birth chart shows.",
    change: "A loosed arrow flies on: prārabdha is lived out. Remedies soften how it lands, and the Lord's grace can lift it.",
    icon: <><g transform="rotate(-18 24 24)"><path d="M6 24h36M42 24l-7-5M42 24l-7 5M6 24l-3-4M6 24l-3 4M10 24l-3-4M10 24l-3 4" /></g></>,
  },
  {
    name: "Āgāmi", gloss: "coming", image: "The arrow being fitted to the string",
    what: "The new karma made by what we choose to do now. Unless it is offered to the Lord, it joins the quiver and must ripen later.",
    change: "Wholly in our hands. Act without craving the fruit (Gītā 2.47) and offer the act to the Lord, and it binds no further.",
    icon: <><path d="M16 4c14 6 14 34 0 40" /><path d="M16 4 9 24l7 20" /><path d="M9 24h34M43 24l-6-4M43 24l-6 4" /></>,
  },
];

export function Karma({ verses }: { verses: Item[] }) {
  const [pick, setPick] = useKept("remedies.karma", 1);
  const k = KARMAS[pick];
  return (
    <Split aside={<Verses items={verses} />}>
      <div className="rm-quiver" role="group" aria-label="The three kinds of karma">
        {KARMAS.map((x, i) => (
          <button key={x.name} type="button" aria-pressed={i === pick} onClick={() => setPick(i)}>
            <svg viewBox="0 0 48 48" aria-hidden>{x.icon}</svg>
            <b>{x.name}</b>
            <small>{x.gloss}</small>
          </button>
        ))}
      </div>
      <div className="rm-detail" aria-live="polite">
        <h3>{k.image}</h3>
        <dl className="rm-cause">
          <dt>What it is</dt><dd>{k.what}</dd>
          <dt>Can it change?</dt><dd>{k.change}</dd>
        </dl>
      </div>
      <p className="rm-prose">
        Jyotiṣa reads mainly the middle arrow. A chart cannot show the whole quiver, and it does not decide what you do
        next. It shows what has already been loosed in this life, and when each part of it will land.
      </p>
    </Split>
  );
}

/* -------------------------------------------------------------------------- */
/*                      2. JYOTIṢA: WHERE THE CHART SHOWS KARMA                */
/* -------------------------------------------------------------------------- */

const AIMS = {
  dharma: { name: "Dharma", gloss: "right living", color: "var(--lv-2)" },
  artha: { name: "Artha", gloss: "means and wealth", color: "var(--lv-1)" },
  kama: { name: "Kāma", gloss: "desire fulfilled", color: "var(--lv-4)" },
  moksa: { name: "Mokṣa", gloss: "release", color: "var(--lv-3)" },
};
type Aim = keyof typeof AIMS;
const HOUSES: { name: string; fields: string; aim: Aim; karma?: string }[] = [
  { name: "Tanu", fields: "The body and the self", aim: "dharma", karma: "The vessel prārabdha has built for this life." },
  { name: "Dhana", fields: "Wealth, speech, family, food", aim: "artha" },
  { name: "Sahaja", fields: "Courage, effort, younger siblings", aim: "kama" },
  { name: "Sukha", fields: "Home, mother, inner contentment", aim: "moksa" },
  { name: "Putra", fields: "Children, intelligence, mantra", aim: "dharma", karma: "Pūrva-puṇya: the merit carried in from past lives." },
  { name: "Ari", fields: "Debts, disease, rivals, service", aim: "artha", karma: "Old debts that come due and must be repaid." },
  { name: "Kalatra", fields: "Spouse and partnership", aim: "kama" },
  { name: "Āyus", fields: "Span of life, the hidden, sudden change", aim: "moksa", karma: "How long this ripening of prārabdha runs." },
  { name: "Bhāgya", fields: "Fortune, dharma, the guru", aim: "dharma", karma: "Fortune earned by dharma in earlier lives, and the guru who shows the way out." },
  { name: "Karma", fields: "Action in the world, profession", aim: "artha", karma: "Karma-sthāna: where āgāmi, the new karma, is made." },
  { name: "Lābha", fields: "Gains and fulfilled desires", aim: "kama" },
  { name: "Vyaya", fields: "Loss, letting go, final release", aim: "moksa", karma: "Where the account is spent: the bhava of mokṣa." },
];

/** House h (1–12) as a ring sector: the 1st on the eastern horizon at the left, the rest counter-clockwise. */
function sector(h: number, r0: number, r1: number) {
  const at = (deg: number, r: number) => {
    const a = (deg * Math.PI) / 180;
    return `${(150 + r * Math.cos(a)).toFixed(2)} ${(150 - r * Math.sin(a)).toFixed(2)}`;
  };
  const mid = 180 + 30 * (h - 1);
  return `M${at(mid - 15, r1)} A${r1} ${r1} 0 0 0 ${at(mid + 15, r1)} L${at(mid + 15, r0)} A${r0} ${r0} 0 0 1 ${at(mid - 15, r0)}Z`;
}
const polar = (deg: number, r: number) => ({ x: 150 + r * Math.cos((deg * Math.PI) / 180), y: 150 - r * Math.sin((deg * Math.PI) / 180) });

function HouseWheel() {
  const [house, setHouse] = useState(5);
  const [aim, setAim] = useState<Aim | null>(null);
  const h = HOUSES[house - 1];
  return (
    <div className="rm-wheelbox">
      <div>
        <svg viewBox="0 0 300 300" className="rm-houses" role="group" aria-label="The twelve bhavas">
          {HOUSES.map((x, i) => {
            const n = i + 1;
            const p = polar(180 + 30 * i, 104);
            const dot = polar(180 + 30 * i, 132);
            return (
              <g key={x.name} {...press(`Bhava ${n}, ${x.name}`, () => setHouse(n))} aria-pressed={house === n}
                className={aim && x.aim !== aim ? "dim" : undefined} style={{ "--c": AIMS[x.aim].color } as CSSProperties}>
                <path d={sector(n, 72, 142)} />
                <text x={p.x} y={p.y} dy=".35em">{n}</text>
                {x.karma && <circle cx={dot.x} cy={dot.y} r="3" className="mark" />}
              </g>
            );
          })}
          <text x="150" y="142" className="hub-n">{house}</text>
          <text x="150" y="166" className="hub">{h.name}</text>
        </svg>
        <div className="rm-aims" role="group" aria-label="Aims of life">
          {(Object.keys(AIMS) as Aim[]).map((a) => (
            <button key={a} type="button" aria-pressed={aim === a} onClick={() => setAim(aim === a ? null : a)} style={{ "--c": AIMS[a].color } as CSSProperties}>
              <i />{AIMS[a].name}
            </button>
          ))}
        </div>
      </div>
      <div className="rm-detail" aria-live="polite">
        <p className="rm-cite">Bhava {house}, {AIMS[h.aim].name.toLowerCase()} ({AIMS[h.aim].gloss})</p>
        <h3>{h.name}</h3>
        <p>{h.fields}.</p>
        {h.karma && <p className="rm-key"><b>What it says of karma</b> {h.karma}</p>}
        <p className="rm-note">
          {aim
            ? `${AIMS[aim].name} bhavas form a triangle: ${HOUSES.map((x, i) => (x.aim === aim ? i + 1 : 0)).filter(Boolean).join(", ")}.`
            : "Dots mark the bhavas that speak most directly of karma. Pick an aim to see its three bhavas."}
        </p>
      </div>
    </div>
  );
}

function BirthMoment({ present, onOpen }: { present: string[] | null; onOpen: () => void }) {
  const { birth, name } = useChart();
  const who = name || "This chart";
  return (
    <div className="rm-callout">
      <h3>The birth moment</h3>
      {!birth ? <p>Open a chart and this reads its birth moment against the conditions Parāśara singles out for a śānti.</p>
        : present === null ? <p>Reading the birth moment…</p>
          : present.length === 0 ? <p>{who} was born at a moment that carries none of the conditions Parāśara singles out for a śānti.</p>
            : (
              <>
                <p>{who} was born under {plural(present.length, "condition")} for which Parāśara prescribes a śānti: {present.map((k) => CONDITION_META[k].title).join(", ")}.</p>
                <button type="button" className="rm-go" onClick={onOpen}>See the śānti</button>
              </>
            )}
    </div>
  );
}

export function Jyotisha({ verses, present, onOpenBirth }: { verses: Item[]; present: string[] | null; onOpenBirth: () => void }) {
  return (
    <Split aside={<Verses items={verses} />}>
      <HouseWheel />
      <p className="rm-prose">
        The nine grahas are not the cause of karma; they are its messengers. Each delivers results already earned, in its
        own daśā and through its transits, under the oversight of Śrīman Nārāyaṇa, the <em>adhyakṣa</em> (Gītā 9.10).
        Reading a chart is reading what has ripened, not a sentence passed by the grahas.
      </p>
      <BirthMoment present={present} onOpen={onOpenBirth} />
    </Split>
  );
}

/* -------------------------------------------------------------------------- */
/*                         3. KĀLA: WHERE WE STAND                             */
/* -------------------------------------------------------------------------- */

const MAHAYUGA = 4_320_000;
const SANDHI = 1_728_000;
// shortcut: Kali began 18 Feb 3102 BCE; the count is a year high before mid-February
const KALI = new Date().getFullYear() + 3101;
const YUGAS: [string, number, number][] = [["Kṛta", 1_728_000, 4], ["Tretā", 1_296_000, 3], ["Dvāpara", 864_000, 2], ["Kali", 432_000, 1]];

const KALA: { name: string; place: string; span: string; years?: number; elapsed?: number; now: string }[] = [
  { name: "Para", place: "Dvitīya parārdha", years: 100 * 360 * 2 * 1000 * MAHAYUGA, elapsed: 50 * 360 * 2 * 1000 * MAHAYUGA,
    span: "The life of Brahmā: a hundred of his years, each of 360 days and nights.",
    now: "Fifty of Brahmā's years have passed; the second half, the dvitīya parārdha, has begun." },
  { name: "Kalpa", place: "Śveta-varāha kalpa", years: 1000 * MAHAYUGA, elapsed: 6 * 71 * MAHAYUGA + 7 * SANDHI + 27 * MAHAYUGA + 3_888_000 + KALI,
    span: "A day of Brahmā: a thousand mahāyugas (Gītā 8.17). His night is as long.",
    now: "Six Manus have reigned; this day of Brahmā is a little under half spent." },
  { name: "Manvantara", place: "Vaivasvata manvantara", years: 71 * MAHAYUGA, elapsed: 27 * MAHAYUGA + 3_888_000 + KALI,
    span: "The reign of one Manu: 71 mahāyugas. Fourteen Manus reign in each day of Brahmā; this is the seventh.",
    now: "Twenty-seven mahāyugas of it have passed; we are in the twenty-eighth." },
  { name: "Mahāyuga", place: "28th mahāyuga", years: MAHAYUGA, elapsed: 3_888_000 + KALI,
    span: "Four yugas: Kṛta of 17,28,000 years, Tretā of 12,96,000, Dvāpara of 8,64,000 and Kali of 4,32,000. Dharma stands on four legs in Kṛta and loses one in each age after.",
    now: "Kṛta, Tretā and Dvāpara have passed; this is Kali." },
  { name: "Yuga", place: "Kali yuga, first quarter", years: 432_000, elapsed: KALI,
    span: "The shortest age, when dharma stands on one leg.",
    now: `${KALI.toLocaleString("en-IN")} years have passed since it began in 3102 BCE, when Śrī Kṛṣṇa left the world.` },
  { name: "Vāra", place: `${VASARA[new Date().getDay()]}-vāsara`, span: "",
    now: "Jyotiṣa reads the moment itself: the tithi, nakṣatra, yoga and karaṇa of this day." },
];

function KalaZoom() {
  const [pick, setPick] = useKept("remedies.kala", 4);
  const k = KALA[pick];
  const today = PLANET_DATA[WEEKDAY_GRAHA[new Date().getDay()]];
  const at = k.years && k.elapsed !== undefined ? k.elapsed / k.years : null;
  return (
    <div className="rm-kala">
      <ol className="rm-address" aria-label="Our address in time">
        {KALA.map((x, i) => (
          <li key={x.name} style={{ "--d": i } as CSSProperties}>
            <button type="button" aria-pressed={i === pick} onClick={() => setPick(i)}>
              <b>{x.place}</b><small>{x.name}</small>
            </button>
          </li>
        ))}
      </ol>
      <div className="rm-detail" aria-live="polite">
        <p className="rm-cite">{k.name}</p>
        <h3>{k.place}</h3>
        {k.years ? (
          <p className="rm-span"><b>{k.years.toLocaleString("en-IN")}</b> years <span>({words.format(k.years)})</span></p>
        ) : (
          <p className="rm-span" style={{ "--c": today.color } as CSSProperties}>Ruled by {today.sanskrit} ({today.name})</p>
        )}
        {k.span && <p>{k.span}</p>}
        {pick === 3 ? (
          <div className="rm-yugas">
            {YUGAS.map(([n, y, legs]) => (
              <div key={n} style={{ flex: legs }} className={n === "Kali" ? "now" : undefined} title={`${n}: ${short.format(y)} years, dharma on ${legs} leg${legs > 1 ? "s" : ""}`}>
                <b>{n}</b>
              </div>
            ))}
            <i className="rm-here" style={{ left: `${(at ?? 0) * 100}%` }} />
          </div>
        ) : at !== null && (
          <div className="rm-bar" aria-hidden><i style={{ width: `${Math.max(at * 100, 0.6)}%` }} /></div>
        )}
        <p className="rm-note">{k.now}</p>
      </div>
    </div>
  );
}

const LOKAS = ["Satya", "Tapas", "Jana", "Mahar", "Svar", "Bhuvar", "Bhū", "Atala", "Vitala", "Sutala", "Talātala", "Mahātala", "Rasātala", "Pātāla"];

export function Kala({ verses }: { verses: Item[] }) {
  return (
    <Split aside={<Verses items={verses} />}>
      <h3 className="rm-title minor first">Where we stand in time</h3>
      <p className="rm-prose">Each span holds the next. Pick one to see how long it is and how much of it has passed.</p>
      <KalaZoom />

      <h3 className="rm-title minor">Where we stand in space</h3>
      <div className="rm-space">
        <ol className="rm-lokas" aria-label="The fourteen worlds">
          {LOKAS.map((l, i) => (
            <li key={l} className={i < 6 ? "up" : i > 6 ? "down" : "here"} style={{ "--w": `${100 - Math.abs(6 - i) * 9}%` } as CSSProperties}>
              {l}{i === 6 && <small>the earth: we are here</small>}
            </li>
          ))}
        </ol>
        <div>
          <p className="rm-prose">
            The universe, the <em>brahmāṇḍa</em>, holds fourteen worlds: seven rising above the earth to Satya-loka, the
            world of Brahmā, and seven below it down to Pātāla. Every one of them lies inside time. Great merit reaches the
            higher worlds, yet when it is spent the soul returns (Gītā 9.21), and even Brahmā's world comes to an end (Gītā 8.16).
          </p>
          <p className="rm-prose">Before every rite, every remedy included, the <em>saṅkalpa</em> states exactly where in this space and time the doer stands:</p>
        </div>
      </div>
      <Sloka text={"dvitīya-parārdhe śveta-varāha-kalpe vaivasvata-manvantare\naṣṭāviṃśati-tame kali-yuge prathame pāde\njambū-dvīpe bhārata-varṣe bharata-khaṇḍe …"} />
      <p className="rm-translation">
        In the second half of Brahmā's life, in the Śveta-varāha kalpa, in the reign of Vaivasvata Manu, in the Kali yuga of
        the twenty-eighth mahāyuga, in its first quarter; in Jambūdvīpa, in Bhārata-varṣa…
      </p>
    </Split>
  );
}

/* -------------------------------------------------------------------------- */
/*                          4. SAṂSĀRA: THE WHEEL                              */
/* -------------------------------------------------------------------------- */

const CYCLE: { name: string; gloss: string; text: string; seen?: string }[] = [
  { name: "Avidyā", gloss: "not knowing", text: "The self forgets that it belongs to the Lord and takes the body for itself. Every other link grows from this one." },
  { name: "Kāma", gloss: "desire", text: "Wanting a particular result for oneself: pleasure, gain, or escape from pain." },
  { name: "Karma", gloss: "action", text: "Action driven by that desire. This is āgāmi, the new karma being made.", seen: "The 10th bhava, karma-sthāna" },
  { name: "Saṃskāra", gloss: "impression", text: "The act leaves a mark and a debt. Unspent, it is stored in sañcita, the quiver." },
  { name: "Janma", gloss: "birth", text: "A portion ripens as prārabdha and takes a body, at a moment the birth chart records.", seen: "The birth chart" },
  { name: "Bhoga", gloss: "experience", text: "Pleasure and pain are lived out. Reacting to them, desire rises again, and the wheel turns.", seen: "Daśās and transits" },
];

export function Samsara({ verses, onWayOut }: { verses: Item[]; onWayOut: () => void }) {
  const [turn, setTurn] = useState(0);
  const [broken, setBroken] = useState(false);
  const at = turn % 6;
  const c = CYCLE[at];
  const node = (i: number) => polar(90 - i * 60, 112);
  return (
    <Split aside={<Verses items={verses} />}>
      <div className="rm-wheelbox">
        <div>
          <svg viewBox="0 0 300 300" className={`rm-cycle${broken ? " broken" : ""}`} role="group" aria-label="The wheel of saṃsāra">
            <circle cx="150" cy="150" r="112" className="ring" />
            {CYCLE.map((_, i) => {
              const m = polar(60 - i * 60, 112);
              return <path key={i} d="M-4 -5 4 0-4 5" className="dir" transform={`translate(${m.x} ${m.y}) rotate(${30 + i * 60})`} />;
            })}
            <g className="hand" style={{ transform: `rotate(${turn * 60}deg)` }}><line x1="150" y1="122" x2="150" y2="80" /></g>
            {CYCLE.map((x, i) => {
              const p = node(i);
              return (
                <g key={x.name} {...press(`${x.name}, ${x.gloss}`, () => { setBroken(false); setTurn((t) => t + ((i - (t % 6) + 6) % 6)); })}
                  aria-pressed={i === at} className={`node${i === 0 ? " root" : ""}`}>
                  <circle cx={p.x} cy={p.y} r="34" />
                  <text x={p.x} y={p.y - 2}>{x.name}</text>
                  <text x={p.x} y={p.y + 12} className="gloss">{x.gloss}</text>
                </g>
              );
            })}
            <text x="150" y="150" dy=".35em" className="hub">{broken ? "mokṣa" : `life ${Math.floor(turn / 6) + 1}`}</text>
          </svg>
          <div className="rm-row center">
            <button type="button" onClick={() => setTurn((t) => t + 1)} disabled={broken}>Turn the wheel</button>
            <button type="button" aria-pressed={broken} onClick={() => setBroken((b) => !b)}>{broken ? "Show the wheel again" : "Break the wheel"}</button>
          </div>
        </div>
        {broken ? (
          <div className="rm-detail exit" aria-live="polite">
            <p className="rm-cite">Where the wheel breaks</p>
            <h3>Remove the first link</h3>
            <p>
              The wheel turns on avidyā. Good deeds alone cannot stop it: merit earns a higher world, and when it is spent the
              soul returns (Gītā 9.21). What stops it is the removal of the first link.
            </p>
            <p>
              When the self surrenders to its owner, the Lord burns the stored seed, new action no longer binds, and when this
              life's prārabdha is spent there is no return (Gītā 8.16).
            </p>
            <button type="button" className="rm-go" onClick={onWayOut}>The way out</button>
          </div>
        ) : (
          <div className="rm-detail" aria-live="polite">
            <p className="rm-cite">Link {at + 1} of 6</p>
            <h3>{c.name} <span>{c.gloss}</span></h3>
            <p>{c.text}</p>
            {c.seen && <p className="rm-key"><b>Where Jyotiṣa sees it</b> {c.seen}</p>}
          </div>
        )}
      </div>
    </Split>
  );
}
