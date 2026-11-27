import { useMemo, useState, type CSSProperties } from "react";
import { useQuery, type UseQueryResult } from "@tanstack/react-query";
import { api, type RemedyBphsEntry, type RemedyVaishnavaTopic, type RemediesChartFlags } from "./api";
import { useKept, useSaved } from "./hooks";
import { useChart } from "./store";
import { CopyButton, Loaded, SubTabs } from "./ui";
import { SCRIPTS, type Script } from "./script";
import { CONDITION_META, FAMILY, type GrahaDetail, MANDALA, PLANET_DATA, SEVERITY, WEEKDAY_GRAHA, fromBphs, plural } from "./remediesData";
import { ScriptCtx, SideCtx, Sloka, Split, Verses } from "./RemediesVerses";
import { Jyotisha, Kala, Karma, Samsara } from "./RemediesChapters";

/* -------------------------------------------------------------------------- */
/*                     5. UPĀYA: FRUIT, FIELD AND ROOT                         */
/* -------------------------------------------------------------------------- */

type Level = "fruit" | "field" | "root";
const LEVELS: { id: Level; name: string; sa: string; text: string }[] = [
  { id: "fruit", name: "Ease the fruit", sa: "Phala", text: "Parāśara's śānti softens prārabdha as it lands." },
  { id: "field", name: "Purify the field", sa: "Kṣetra", text: "Dharma, worship and service stop new binding karma." },
  { id: "root", name: "Cut the root", sa: "Mūla", text: "Śaraṇāgati burns the seed itself and ends the wheel." },
];

const Plant = ({ part }: { part: Level }) => (
  <svg viewBox="0 0 40 56" className={`rm-plant ${part}`} aria-hidden>
    <path className="field" d="M4 34h32M20 34V14M20 25c-6-1-8-5-8-9 5 1 8 4 8 9M20 20c6-2 8-6 8-10-5 1-8 5-8 10" />
    <circle className="fruit" cx="20" cy="9" r="4.5" />
    <path className="root" d="M20 34v10M20 38l-6 9M20 38l6 9M20 43l-3 9M20 43l3 9" />
  </svg>
);

const FACTS: [string, keyof GrahaDetail][] = [
  ["Day", "day"], ["Direction", "direction"], ["Deity", "deity"], ["Gemstone", "gem"],
  ["Substitute", "uparatna"], ["Metal", "metal"], ["Homa wood", "samidh"],
];

function Graha({ general, planet, setPlanet }: { general: RemedyBphsEntry[]; planet: string; setPlanet: (p: string) => void }) {
  const g = PLANET_DATA[planet];
  const today = WEEKDAY_GRAHA[new Date().getDay()];
  const items = useMemo(() => general.filter((e) => (g ? e.planet === planet : !e.planet)).map(fromBphs), [general, planet, g]);
  return (
    <Split id={planet} aside={<Verses items={items} title={g ? `Parāśara on ${g.sanskrit}` : "Parāśara, chapter 84"} />}>
      <div className="rm-mandala-box">
        <div className="rm-mandala" role="group" aria-label="Navagraha">
          {MANDALA.map((k) => {
            const x = PLANET_DATA[k];
            return (
              <button key={k} type="button" aria-pressed={planet === k} onClick={() => setPlanet(k)} style={{ "--c": x.color } as CSSProperties} aria-label={`${x.sanskrit}, ${k}${k === today ? ", today's graha" : ""}`}>
                <b>{x.sanskrit}</b>
                <small>{k}</small>
                {k === today && <i className="today" />}
              </button>
            );
          })}
        </div>
        <div className="rm-mandala-notes">
          <p>Laid out as in a Navagraha shrine, Sūrya at the centre and east at the top.</p>
          <p><i className="today" /> Today belongs to {PLANET_DATA[today].sanskrit}.</p>
          <button type="button" className="rm-link" aria-pressed={planet === "all"} onClick={() => setPlanet("all")}>Why worship the grahas (BPHS 84)</button>
        </div>
      </div>
      {g ? (
        <section className="rm-graha" style={{ "--c": g.color } as CSSProperties}>
          <h3 className="rm-title">{g.sanskrit}<span>{g.name}</span></h3>
          <dl className="rm-facts">
            {FACTS.map(([label, key]) => <div key={key}><dt>{label}</dt><dd>{g[key]}</dd></div>)}
          </dl>
          {([["Bīja mantra", g.mantra, `Recite ${g.japaCount} times`], ["Gāyatrī", g.gayatri, ""]] as const).map(([label, text, count]) => (
            <div key={label} className="rm-mantra">
              <header><h4>{label}</h4><span className="rm-cite">{count}</span><CopyButton text={text} /></header>
              <Sloka text={text.replace(/ \| /g, " |\n")} />
            </div>
          ))}
          <div className="rm-practice">
            <div><h4>Fasting</h4><p>{g.fasting}</p></div>
            <div><h4>Dāna</h4><p>{g.charity}</p></div>
          </div>
        </section>
      ) : (
        <h3 className="rm-title">Why worship the grahas</h3>
      )}
    </Split>
  );
}

function Natal({ conditional, flagsQ, present }: {
  conditional: RemedyBphsEntry[]; flagsQ: UseQueryResult<RemediesChartFlags>; present: string[];
}) {
  const { birth, name } = useChart();
  const [selected, setSelected] = useKept<string | null>("remedies.condition", null);
  const flags = birth ? flagsQ.data : undefined;
  const who = name || "This chart";
  const items = useMemo(() => {
    if (selected) return conditional.filter((e) => e.condition === selected).map(fromBphs);
    if (!flags) return conditional.map(fromBphs);
    const ids = new Set(flags.applicable);
    return conditional.filter((e) => e.condition === "inauspicious_list" || ids.has(e.id) || (e.condition && flags.flags[e.condition])).map(fromBphs);
  }, [conditional, selected, flags]);
  const conditions = Object.keys(CONDITION_META)
    .filter((k) => k !== "inauspicious_list")
    .sort((a, b) => Number(present.includes(b)) - Number(present.includes(a)));
  const meta = selected ? CONDITION_META[selected] : null;

  return (
    <Split id={selected ?? ""} aside={<Verses items={items} title={selected ? "From the śāstra" : flags ? "Verses that apply" : "All verses"} />}>
      {selected && meta ? (
        <section className="rm-condition">
          <p className="rm-cite">
            <span><i className={`rm-dot ${meta.severity}`} />{SEVERITY[meta.severity]}</span>
            <span>{meta.chapter}</span>
            {present.includes(selected) && <b>Present in {name || "this chart"}</b>}
          </p>
          <h3 className="rm-title">{meta.title}</h3>
          <dl className="rm-cause">
            <dt>Cause</dt><dd>{meta.cause}</dd>
            <dt>Deity</dt><dd>{meta.deity}</dd>
            <dt>Rite</dt><dd>{meta.summary}</dd>
          </dl>
          {FAMILY.has(selected) && <p className="rm-note">The chart alone cannot show this condition; it depends on details of the family.</p>}
        </section>
      ) : birth ? (
        <Loaded q={flagsQ}>
          {() => (
            <div className="rm-diagnosis">
              <h3 className="rm-title">
                {present.length ? `${who} has ${plural(present.length, "birth condition")} with a prescribed remedy` : `${who} has no inauspicious birth conditions`}
              </h3>
              {present.length > 0 && (
                <div className="rm-cards">
                  {present.map((k) => {
                    const m = CONDITION_META[k];
                    return (
                      <button key={k} type="button" className="rm-card" onClick={() => setSelected(k)}>
                        <span className="rm-cite"><i className={`rm-dot ${m.severity}`} />{SEVERITY[m.severity]}, {m.chapter}</span>
                        <strong>{m.title}</strong>
                        <span>{m.summary}</span>
                      </button>
                    );
                  })}
                </div>
              )}
              <p className="rm-note">Three conditions depend on the family and are not checked: a star shared with a parent or sibling, a child after three of the other sex, and an unusual delivery.</p>
            </div>
          )}
        </Loaded>
      ) : (
        <p className="rm-prose">Open a chart to see which of these conditions apply to it. Until then this is Parāśara's full catalogue, BPHS chapters 85 to 96.</p>
      )}
      <h3 className="rm-title minor">Every birth condition in BPHS 85 to 96</h3>
      <div className="rm-chips" role="group" aria-label="Birth conditions">
        <button type="button" aria-pressed={selected === null} onClick={() => setSelected(null)}>{birth ? "This chart" : "Overview"}</button>
        {conditions.map((k) => (
          <button key={k} type="button" aria-pressed={selected === k} onClick={() => setSelected(k)} className={present.includes(k) ? "in" : undefined}>
            <i className={`rm-dot ${CONDITION_META[k].severity}`} />{CONDITION_META[k].title}
          </button>
        ))}
      </div>
    </Split>
  );
}

function Upaya({ topics, data, level, setLevel, fruit, setFruit, planet, setPlanet, flagsQ, present }: {
  topics: (id: string) => RemedyVaishnavaTopic | undefined; data: { general: RemedyBphsEntry[]; conditional: RemedyBphsEntry[] };
  level: Level; setLevel: (l: Level) => void; fruit: "graha" | "birth"; setFruit: (f: "graha" | "birth") => void;
  planet: string; setPlanet: (p: string) => void; flagsQ: UseQueryResult<RemediesChartFlags>; present: string[];
}) {
  const [fieldId, setFieldId] = useState("good-deeds");
  const field = ["good-deeds", "for-all", "worship"].map(topics).filter((t): t is RemedyVaishnavaTopic => !!t);
  const ft = field.find((t) => t.id === fieldId) ?? field[0];
  const nyasa = topics("nyasa-vidya");
  const pointers = topics("scripture-pointers");
  return (
    <>
      <div className="rm-levels" role="group" aria-label="Depth of remedy">
        {LEVELS.map((l) => (
          <button key={l.id} type="button" aria-pressed={level === l.id} onClick={() => setLevel(l.id)}>
            <Plant part={l.id} />
            <span>
              <small>{l.sa}{l.id === "root" && <em>Recommended</em>}</small>
              <b>{l.name}</b>
              <span>{l.text}</span>
            </span>
          </button>
        ))}
      </div>

      {level === "fruit" && (
        <>
          <p className="rm-prose">
            Parāśara's remedies for afflicted grahas and difficult birth moments (BPHS 84 to 96). They ease prārabdha as it
            lands; they are a support along the way, not the way out.
          </p>
          <SubTabs tabs={[{ id: "graha", name: "Navagraha" }, { id: "birth", name: present.length ? `Birth moment (${present.length})` : "Birth moment" }]}
            value={fruit} onChange={setFruit} label="Kind of śānti" />
          <div className="rm-sub">
            {fruit === "graha"
              ? <Graha general={data.general} planet={planet} setPlanet={setPlanet} />
              : <Natal conditional={data.conditional} flagsQ={flagsQ} present={present} />}
          </div>
        </>
      )}

      {level === "field" && ft && (
        <Split id={ft.id} aside={<Verses items={ft.entries} title={ft.title} />}>
          <div className="rm-chips" role="group" aria-label="Practices">
            {field.map((t) => (
              <button key={t.id} type="button" aria-pressed={t.id === ft.id} onClick={() => setFieldId(t.id)}>{t.title}</button>
            ))}
          </div>
          {ft.intro && <p className="rm-prose">{ft.intro}</p>}
        </Split>
      )}

      {level === "root" && (
        <Split aside={<>{nyasa && <Verses items={nyasa.entries} title="Nyāsa Vidyā" />}{pointers && <Verses items={pointers.entries} title="Grace and release across the śāstra" picker={false} />}</>}>
          {nyasa?.intro && <p className="rm-prose">{nyasa.intro}</p>}
          <p className="rm-aside">
            <strong>Nyāsa Vidyā</strong> (Rāmānuja Sampradāya) is held by the Ācāryas to be the complete and immediate
            means to protection and liberation. It asks for no qualification of birth, time, place or purity, only
            sincere surrender to the Lord.
          </p>
        </Split>
      )}
    </>
  );
}

/* -------------------------------------------------------------------------- */
/*                               MAIN COMPONENT                               */
/* -------------------------------------------------------------------------- */

type Step = "karma" | "jyotisha" | "kala" | "samsara" | "upaya";
const CHAPTERS: { id: Step; name: string; title: string; lede: string }[] = [
  { id: "karma", name: "Karma", title: "What is karma",
    lede: "Karma means action, and also what every action leaves behind. Nothing done is lost: each act is a seed that will one day bear fruit for the one who did it. The tradition sorts these seeds by where they stand, using the picture of an archer." },
  { id: "jyotisha", name: "Jyotiṣa", title: "The chart as a map of prārabdha",
    lede: "Prārabdha ripens at a definite moment. The sky at that moment, seen from the place of birth, is the birth chart: twelve bhavas for the fields of life, nine grahas for the powers that deliver the fruit, and the daśās for when each fruit arrives." },
  { id: "kala", name: "Kāla", title: "Space and time",
    lede: "In Sanātana Dharma time is a wheel, the kāla-cakra, turning in cycles within cycles, and space is layered into fourteen worlds. Kāla is also a name of the Lord (Gītā 10.30), and Jyotiṣa, the eye of the Veda, is the science of measuring it." },
  { id: "samsara", name: "Saṃsāra", title: "How the wheel turns",
    lede: "Karma and time together make saṃsāra, the round of birth and death. No one can point to its first turn, and it keeps turning because each link produces the next. Turn it, and watch where Jyotiṣa sees it." },
  { id: "upaya", name: "Upāya", title: "The way out",
    lede: "Every remedy works at one of three depths. Parāśara's śānti eases the fruit as it lands; dharma and worship purify the field so no new seed is sown; śaraṇāgati cuts the root. The first two are worth doing. The third is the one the Ācāryas call complete." },
];

export function Remedies() {
  const [saved, setStep] = useSaved<Step>("remediesStep", "karma");
  const [side, setSide] = useState<HTMLElement | null>(null);
  const [savedScript, setScript] = useSaved<Script>("remediesScript", "deva");
  const script: Script = SCRIPTS.some((s) => s.id === savedScript) ? savedScript : "deva";
  const [level, setLevel] = useSaved<Level>("remediesLevel", "root");
  const [fruit, setFruit] = useSaved<"graha" | "birth">("remediesFruit", "graha");
  const [planet, setPlanet] = useSaved<string>("remediesGrahaPick", "Sun");
  const { birth, name } = useChart();

  const q = useQuery({ queryKey: ["remediesTopics"], queryFn: api.remediesTopics, staleTime: Infinity });
  const flagsQ = useQuery({ queryKey: ["remediesChart", birth], queryFn: () => api.remediesChart(birth!), enabled: !!birth });
  const flags = birth ? flagsQ.data?.flags : undefined;
  const present = Object.keys(CONDITION_META).filter((k) => k !== "inauspicious_list" && flags?.[k]);

  const step: Step = CHAPTERS.some((c) => c.id === saved) ? saved : "karma";
  const idx = CHAPTERS.findIndex((c) => c.id === step);
  const chapter = CHAPTERS[idx];
  const openBirth = () => { setLevel("fruit"); setFruit("birth"); setStep("upaya"); };

  return (
    <section className="pane rm">
      <header className="pane-head rm-head">
        <h2>Remedies</h2>
        <nav className="rm-path" aria-label="Chapters">
          {CHAPTERS.map((c, i) => (
            <button key={c.id} type="button" aria-current={c.id === step ? "step" : undefined} className={i < idx ? "done" : undefined} onClick={() => setStep(c.id)} title={c.title}>
              <span>{i + 1}</span><b>{c.name}</b>
            </button>
          ))}
        </nav>
        {flags && (
          <span className="rm-status"><i className={`rm-dot ${present.length ? "warning" : "ok"}`} />{name || "Chart"}: {present.length ? plural(present.length, "birth condition") : "no birth conditions"}</span>
        )}
      </header>

      <ScriptCtx.Provider value={{ script, setScript }}>
      <Loaded q={q}>
        {(data) => {
          const topic = (id: string) => data.vaishnava.topics.find((t) => t.id === id);
          const verses = (id: string) => topic(id)?.entries ?? [];
          const prev = CHAPTERS[idx - 1];
          const next = CHAPTERS[idx + 1];
          return (
            // keyed so a new chapter opens at its top
            <div className="rm-main" key={step}>
              <div className="rm-left">
                <header className="rm-chapter">
                  <h2><span className="rm-num" aria-hidden>{idx + 1}</span>{chapter.title}</h2>
                  <p className="rm-lede">{chapter.lede}</p>
                </header>
                <SideCtx.Provider value={side}>

                {step === "karma" && <Karma verses={verses("karma-types")} />}
                {step === "jyotisha" && <Jyotisha verses={verses("narayana-jyotisha")} present={!birth ? [] : flagsQ.data ? present : null} onOpenBirth={openBirth} />}
                {step === "kala" && <Kala verses={verses("kala")} />}
                {step === "samsara" && <Samsara verses={verses("samsara")} onWayOut={() => { setLevel("root"); setStep("upaya"); }} />}
                {step === "upaya" && (
                  <Upaya topics={topic} data={data.bphs} level={level} setLevel={setLevel} fruit={fruit} setFruit={setFruit}
                    planet={planet} setPlanet={setPlanet} flagsQ={flagsQ} present={present} />
                )}
                </SideCtx.Provider>
                <nav className="rm-pager" aria-label="Previous and next chapter">
                  {prev ? <button type="button" onClick={() => setStep(prev.id)}><small>Previous</small>{prev.title}</button> : <span />}
                  {next && <button type="button" className="next" onClick={() => setStep(next.id)}><small>Next, {idx + 2} of 5</small>{next.title}</button>}
                </nav>
              </div>
              <aside className="rm-side" ref={setSide} aria-label="From the śāstra" />
            </div>
          );
        }}
      </Loaded>
      </ScriptCtx.Provider>
    </section>
  );
}
