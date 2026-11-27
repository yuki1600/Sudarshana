import { Fragment, useState, type ReactNode } from "react";
import { useQuery } from "@tanstack/react-query";
import { api, type Basics, type Birth, type CalcTopic, nowMoment } from "./api";
import { useBasics, useSaved, useView } from "./hooks";
import { useChart } from "./store";
import { CopyButton, Loaded, supOrd } from "./ui";
import { SIGNS, SIGN_NAMES } from "./format";
import * as M from "./calcMath";

/* -------------------------------------------------------------------------- */
/*                                 SMALL TEXT                                 */
/* -------------------------------------------------------------------------- */

/** 133.3333 -> "133°20′". */
const dm = (x: number) => { const t = Math.round(x * 60); return `${Math.floor(t / 60)}°${String(t % 60).padStart(2, "0")}′`; };
/** A longitude as degrees in its sign: "18°02′ Virgo". */
const at = (lon: number) => `${dm(M.mod(lon) % 30)} ${SIGN_NAMES[M.signOf(lon)]}`;
const pct = (x: number) => `${(x * 100).toFixed(2)}%`;
const hm = (h: number) => { const t = Math.round(M.mod(h, 24) * 60); return `${Math.floor(t / 60)}:${String(t % 60).padStart(2, "0")}`; };
export const ord = (n: number) => `${n}${n % 100 >= 11 && n % 100 <= 13 ? "th" : ["th", "st", "nd", "rd"][n % 10] ?? "th"}`;
const ym = (years: number) => { const m = Math.round(years * 12 * 10) / 10; return `${Math.floor(m / 12)} y ${(m % 12).toFixed(1).replace(/\.0$/, "")} m`; };
const arcGap = (a: number, b: number) => Math.abs(M.mod(a - b + 180) - 180);
const ABBR: Record<string, string> = { Sun: "Su", Moon: "Mo", Mars: "Ma", Mercury: "Me", Jupiter: "Ju", Venus: "Ve", Saturn: "Sa", Rahu: "Ra", Ketu: "Ke", Lagna: "As" };
const BODIES = ["Lagna", ...M.PLANETS];

const point = (b: Basics, name: string) => b.points.find((p) => p.name === name)!;
const lon = (b: Basics, name: string) => point(b, name).lon;
const core = (b: Basics, key: string) => b.core.find(([k]) => k === key)?.[1] ?? "";
const weekday = (b: Basics) => M.WEEKDAYS.indexOf(core(b, "Vedic Weekday").split(" ")[0]);
/** Who sits in a sign, of the Lagna and the nine planets. */
const occupants = (b: Basics, sign: number, skip?: string) => BODIES.filter((n) => n !== skip && point(b, n).rasi === sign);
const list = (xs: string[], none = "none") => (xs.length ? xs.join(", ") : none);
function dayTimes(b: Basics, birth: Birth) {
  const sunrise = M.clockHours(core(b, "Sunrise")) ?? 6, sunset = M.clockHours(core(b, "Sunset")) ?? 18;
  const t = birth.hour_local;
  return { sunrise, sunset, t, day: t >= sunrise && t < sunset, since: M.mod(t - sunrise, 24) };
}
/** Midnight UTC of a date as ms, for years before 100 too. */
const utc = (y: number, m: number, d: number) => { const x = new Date(0); x.setUTCFullYear(y, m - 1, d); return x.getTime(); };

/* -------------------------------------------------------------------------- */
/*                              THE WORKED BOX                                */
/* -------------------------------------------------------------------------- */

type Step = [ReactNode, ReactNode];
interface Check { engine: ReactNode; ok: boolean; why?: string }

/** The steps of a rule on this chart, ending with what the engine got. */
function Work({ steps, check, note, pick }: { steps: Step[]; check?: Check; note?: ReactNode; pick?: ReactNode }) {
  return (
    <div className="rm-detail cx-work">
      <p className="rm-cite">Worked on this chart</p>
      {pick}
      <dl className="rm-cause">
        {steps.map(([k, v], i) => <Fragment key={i}><dt>{supOrd(k)}</dt><dd>{supOrd(v)}</dd></Fragment>)}
      </dl>
      {check && (
        <p className={`cx-check${check.ok ? " ok" : ""}`}>
          <b>Engine</b> {check.engine} <span>{check.ok ? "agrees" : check.why ?? "differs: a setting changes how the engine counts this"}</span>
        </p>
      )}
      {note && <p className="rm-note">{note}</p>}
    </div>
  );
}

function Pick({ items, value, onChange, label, names }: { items: readonly string[]; value: string; onChange: (v: string) => void; label: string; names?: Record<string, string> }) {
  return (
    <div className="rm-chips" role="group" aria-label={label}>
      {items.map((i) => <button key={i} type="button" aria-pressed={i === value} onClick={() => onChange(i)}>{names?.[i] ?? i}</button>)}
    </div>
  );
}

type W = (p: { b: Basics; birth: Birth }) => ReactNode;

/* -------------------------------------------------------------------------- */
/*                         1. THE MOMENT                                      */
/* -------------------------------------------------------------------------- */

const Ayanamsa: W = ({ b }) => {
  const [p, setP] = useState("Sun");
  const ay = M.dmsDegrees(core(b, "Ayanamsa"));
  if (ay === null) return null;
  const x = lon(b, p);
  return (
    <Work pick={<Pick items={BODIES} value={p} onChange={setP} label="Body" />} steps={[
      ["Ayanāṃśa", `${core(b, "Ayanamsa")} = ${ay.toFixed(4)}°`],
      [`${p}, sidereal`, `${at(x)} (${M.mod(x).toFixed(4)}°)`],
      [`${p}, tropical`, `${M.mod(x).toFixed(4)}° + ${ay.toFixed(4)}° = ${at(x + ay)}`],
    ]} note="The engine works the other way round, from the tropical position to the sidereal one." />
  );
};

const Lagna: W = ({ b, birth }) => {
  const lst = M.clockHours(core(b, "Sidereal Time"));
  const ay = M.dmsDegrees(core(b, "Ayanamsa"));
  if (lst === null || ay === null) return null;
  const eps = M.obliquity(birth.year + (birth.month - 0.5) / 12);
  const a = M.ascendant(lst, birth.latitude, eps);
  const mine = M.mod(a.lon - ay), engine = lon(b, "Lagna");
  return (
    <Work steps={[
      ["Local sidereal time", `${core(b, "Sidereal Time")} × 15° = ${a.ramc.toFixed(3)}° (RAMC)`],
      ["Latitude φ", `${Math.abs(birth.latitude).toFixed(3)}° ${birth.latitude >= 0 ? "N" : "S"}`],
      ["Obliquity ε", `${eps.toFixed(4)}° (mean, for ${birth.year})`],
      ["Tropical Lagna", `atan2(…) = ${a.lon.toFixed(3)}°`],
      ["− ayanāṃśa", `${a.lon.toFixed(3)}° − ${ay.toFixed(3)}° = ${at(mine)}`],
    ]} check={{ engine: at(engine), ok: arcGap(mine, engine) < 0.05, why: "differs: the chart's Lagna has been moved, or the time is not the birth moment" }}
    note="The engine uses the true obliquity and nutation, so the last minute of arc can differ." />
  );
};

const Ghati: W = ({ b, birth }) => {
  const { sunrise, t, since } = dayTimes(b, birth);
  const g = M.ghatis(t, sunrise), engine = Number(core(b, "Janma Ghatis"));
  return (
    <Work steps={[
      ["Birth", hm(t)],
      ["Sunrise", core(b, "Sunrise")],
      ["Since sunrise", `${hm(since)} = ${since.toFixed(4)} h`],
      ["× 2.5", `${g.toFixed(4)} ghaṭīs (${Math.floor(g)} ghaṭīs ${Math.round((g % 1) * 60)} vighaṭīs)`],
    ]} check={{ engine: `${engine.toFixed(4)} ghaṭīs`, ok: Math.abs(g - engine) < 0.002 }} />
  );
};

const Limbs: W = ({ b }) => {
  const sun = lon(b, "Sun"), moon = lon(b, "Moon");
  const p = M.panchanga(sun, moon), n = M.nakshatraOf(moon);
  const engine = [core(b, "Tithi"), core(b, "Yoga"), core(b, "Karana")];
  const ok = [p.tithiLeft, p.yogaLeft, p.karanaLeft].every((x, i) => { const e = M.leftOf(engine[i]); return e !== null && Math.abs(x - e) < 1e-4; });
  return (
    <Work steps={[
      ["Moon − Sun", `${M.mod(moon).toFixed(3)}° − ${M.mod(sun).toFixed(3)}° = ${p.elong.toFixed(3)}°`],
      ["÷ 12°", `${(p.elong / 12).toFixed(4)}: tithi ${p.tithi}, ${p.tithiName}, ${pct(p.tithiLeft)} left`],
      ["Moon ÷ 13°20′", `${(M.mod(moon) / (40 / 3)).toFixed(4)}: ${n.name}, pada ${n.pada}, ${pct(1 - n.done)} left`],
      ["(Moon + Sun) ÷ 13°20′", `${p.sum.toFixed(3)}° → ${(p.sum / (40 / 3)).toFixed(4)}: yoga ${p.yoga}, ${p.yogaName}, ${pct(p.yogaLeft)} left`],
      ["(Moon − Sun) ÷ 6°", `${(p.elong / 6).toFixed(4)}: karaṇa ${p.karana}, ${p.karanaName}, ${pct(p.karanaLeft)} left`],
    ]} check={{ engine: engine.join(" · "), ok }} />
  );
};

const RahuKala: W = ({ b, birth }) => {
  const { sunrise, sunset } = dayTimes(b, birth);
  const w = weekday(b);
  if (w < 0) return null;
  const r = M.rahuKala(sunrise, sunset, w);
  return (
    <Work steps={[
      ["Daylight", `${hm(sunrise)} to ${hm(sunset)} = ${(sunset - sunrise).toFixed(3)} h`],
      ["÷ 8", `${hm(r.part)} a part`],
      ["Weekday", `${M.WEEKDAYS[w]}: Rāhu has the ${ord(r.k)} part`],
      ["Rāhu kāla", `${hm(r.start)} to ${hm(r.end)}`],
    ]} />
  );
};

/* -------------------------------------------------------------------------- */
/*                               2. THE MAP                                   */
/* -------------------------------------------------------------------------- */

const D12: W = ({ b, birth }) => {
  const [p, setP] = useState("Lagna");
  const q = useQuery({ queryKey: ["calcD12", birth], queryFn: () => api.vargas(birth, [12]) });
  const x = lon(b, p), s = M.signOf(x), part = M.segment(x, 12), mine = M.d12Sign(x);
  const box = q.data?.[0] && Object.entries(q.data[0].boxes).find(([, xs]) => xs.includes(ABBR[p]));
  return (
    <Work pick={<Pick items={BODIES} value={p} onChange={setP} label="Body" />} steps={[
      [p, at(x)],
      ["÷ 2°30′", `${dm(M.mod(x) % 30)} → part ${part + 1} of 12`],
      ["Count on from the sign", `${SIGN_NAMES[s]} + ${part} = ${SIGN_NAMES[mine]}`],
    ]} check={box ? { engine: `D12 in ${SIGN_NAMES[Number(box[0])]}`, ok: Number(box[0]) === mine, why: "differs: the D12 scheme in the settings is not Parāśara's" } : undefined} />
  );
};

const Navamsa: W = ({ b }) => {
  const [p, setP] = useState("Lagna");
  const x = lon(b, p), s = M.signOf(x), part = M.segment(x, 9), mine = M.navamsaSign(x);
  const vargottama = BODIES.filter((n) => point(b, n).rasi === point(b, n).navamsa);
  return (
    <Work pick={<Pick items={BODIES} value={p} onChange={setP} label="Body" />} steps={[
      [p, at(x)],
      ["Sign number", `${SIGN_NAMES[s]} = ${s}`],
      ["÷ 3°20′", `${dm(M.mod(x) % 30)} → part ${part}`],
      ["× 9, + part, mod 12", `${s} × 9 + ${part} = ${s * 9 + part} → ${SIGN_NAMES[mine]}`],
      ["Vargottama here", list(vargottama)],
    ]} check={{ engine: `D9 in ${SIGN_NAMES[point(b, p).navamsa]}`, ok: point(b, p).navamsa === mine, why: "differs: the navāṃśa scheme in the settings is not Parāśara's" }} />
  );
};

const Drishti: W = ({ b }) => {
  const [p, setP] = useState("Saturn");
  const s = point(b, p).rasi;
  return (
    <Work pick={<Pick items={M.SEVEN} value={p} onChange={setP} label="Graha" />} steps={[
      [p, `in ${SIGN_NAMES[s]}`],
      ...M.grahaDrishti(p, s).map(({ house: h, sign }): Step => [`${ord(h)} from it`, `${SIGN_NAMES[sign]}: ${list(occupants(b, sign), "empty")}`]),
    ]} />
  );
};

const WORD: Record<number, string> = { 1: "friend", 0: "neutral", [-1]: "enemy" };
const Maitri: W = ({ b }) => {
  const [p, setP] = useState("Sun");
  const s = point(b, p).rasi;
  return (
    <Work pick={<Pick items={M.SEVEN} value={p} onChange={setP} label="Graha" />} steps={M.SEVEN.filter((q) => q !== p).map((q): Step => {
      const qs = point(b, q).rasi, n = M.natural(p, q), t = M.temporary(s, qs);
      return [q, `natural ${WORD[n]} + temporary ${WORD[t]} (${ord(M.house(s, qs))}) = ${M.PANCHADHA[n + t]}`];
    })} note={`How ${p} regards each graha; the relationship need not be returned.`} />
  );
};

const Sambandha: W = ({ b }) => {
  const sign = (p: string) => point(b, p).rasi;
  const swaps = M.SEVEN.flatMap((a, i) => M.SEVEN.slice(i + 1).filter((c) => M.SIGN_LORD[sign(a)] === c && M.SIGN_LORD[sign(c)] === a).map((c) => `${a} ⇄ ${c}`));
  const together = [...new Set(M.SEVEN.map(sign))].map((s) => M.SEVEN.filter((p) => sign(p) === s)).filter((g) => g.length > 1);
  return (
    <Work steps={[
      ["Exchanges", list(swaps)],
      ["Together in a sign", list(together.map((g) => `${g.join(" and ")} in ${SIGN_NAMES[sign(g[0])]}`))],
    ]} />
  );
};

const SUN_DAILY = 0.9856;   // mean motion, degrees a day
const Special: W = ({ b, birth }) => {
  const { since } = dayTimes(b, birth);
  const s0 = M.mod(lon(b, "Sun") - (SUN_DAILY * since) / 24);
  const rows: [string, string, number][] = [["Bhava Lagna", "BL", 15], ["Hora Lagna", "HL", 30], ["Ghati Lagna", "GL", 75]];
  const mine = rows.map(([, , r]) => M.mod(s0 + since * r));
  const ok = rows.every(([n], i) => arcGap(mine[i], lon(b, n)) < 0.1);
  return (
    <Work steps={[
      ["Since sunrise", `${since.toFixed(4)} h`],
      ["Sun at sunrise", `≈ ${at(s0)}`],
      ...rows.map(([, k, r], i): Step => [k, `+ ${since.toFixed(4)} × ${r}° = ${dm(since * r)} → ${at(mine[i])}`]),
    ]} check={{ engine: rows.map(([n, k]) => `${k} ${at(lon(b, n))}`).join(" · "), ok }}
    note="The Sun's place at sunrise is taken back from its place at birth at its mean daily motion, so it is good to a few seconds of arc." />
  );
};

const Aprakasha: W = ({ b }) => {
  const sun = lon(b, "Sun"), a = M.aprakasha(sun);
  const how: Record<string, string> = { Dhooma: "Sun + 133°20′", Vyatipata: "360° − Dhūma", Parivesha: "Vyatīpāta + 180°", "Indra Chapa": "360° − Pariveśa", Upaketu: "Indracāpa + 16°40′" };
  const ok = Object.entries(a).every(([k, v]) => arcGap(v, lon(b, k)) < 0.001);
  return (
    <Work steps={[["Sun", `${M.mod(sun).toFixed(4)}°`], ...Object.entries(a).map(([k, v]): Step => [k, `${how[k]} = ${v.toFixed(4)}° (${at(v)})`])]}
      check={{ engine: Object.keys(a).map((k) => lon(b, k).toFixed(4) + "°").join(" · "), ok }} />
  );
};

const Gulika: W = ({ b, birth }) => {
  const { sunrise, sunset, t, day } = dayTimes(b, birth);
  const w = weekday(b);
  const lst = M.clockHours(core(b, "Sidereal Time")), ay = M.dmsDegrees(core(b, "Ayanamsa"));
  if (w < 0 || lst === null || ay === null) return null;
  const length = day ? sunset - sunrise : 24 - (sunset - sunrise);
  const k = M.gulikaPart(w, !day), part = length / 8;
  const start = (day ? sunrise : sunset) + (k - 1) * part;
  const back = (M.mod(start - t + 12, 24) - 12);   // hours from birth to the part's start, either way
  const asc = M.mod(M.ascendant(lst + back * 1.00273791, birth.latitude, M.obliquity(birth.year)).lon - ay);
  const engine = lon(b, "Gulika");
  return (
    <Work steps={[
      ["Born", day ? "by day" : "by night"],
      [day ? "Day" : "Night", `${length.toFixed(3)} h ÷ 8 = ${hm(part)} a part`],
      ["Saturn's part", `the ${ord(k)}, from ${M.WEEKDAYS[w]}'s ${day ? "lord" : "fifth lord"}`],
      ["It begins", hm(start)],
      ["Lagna rising then", `≈ ${at(asc)}`],
    ]} check={{ engine: `Gulika ${at(engine)} · Māndi ${at(lon(b, "Maandi"))}`, ok: arcGap(asc, engine) < 0.15, why: "differs: the Gulika setting takes another point of the part" }} />
  );
};

/* -------------------------------------------------------------------------- */
/*                               3. STRENGTH                                  */
/* -------------------------------------------------------------------------- */

const Six: W = () => {
  const [p, setP] = useState("Sun");
  return (
    <Loaded q={useView("strengths")}>{(s) => {
      const r = s.shadbala.planets.find((x) => x.name === p)!;
      // the luminaries' ceṣṭā is their ayana and pakṣa bala, already inside kāla bala (BPHS 27)
      const inKala = p === "Sun" || p === "Moon";
      const parts: [string, number][] = [["Sthāna", r.sthana], ["Dig", r.dig], ["Kāla", r.kala], ["Ceṣṭā", inKala ? 0 : r.cheshta], ["Naisargika", r.naisargika], ["Dṛk", r.drig]];
      const sum = parts.reduce((a, [, v]) => a + v, 0);
      return (
        <Work pick={<Pick items={M.SEVEN} value={p} onChange={setP} label="Graha" />} steps={[
          ...parts.map(([k, v]): Step => [k, k === "Ceṣṭā" && inKala ? `${r.cheshta.toFixed(2)}, not added: it is the ${p === "Sun" ? "ayana" : "pakṣa"} bala, already in kāla` : v.toFixed(2)]),
          ["Sum", `${sum.toFixed(2)} virūpas`],
          ["÷ 60", `${(sum / 60).toFixed(3)} rūpas`],
        ]} check={{ engine: `${r.total.toFixed(2)} virūpas, ${r.rupas.toFixed(3)} rūpas`, ok: Math.abs(sum - r.total) < 0.01 }} />
      );
    }}</Loaded>
  );
};

const Required: W = () => (
  <Loaded q={useView("strengths")}>{(s) => (
    <Work steps={s.shadbala.planets.map((r): Step => {
      const ratio = r.rupas / r.required;
      return [r.name, `${r.rupas.toFixed(2)} ÷ ${r.required} = ${(ratio * 100).toFixed(0)}%: ${ratio >= 1 ? "enough" : "short of its minimum"}`];
    })} check={{ engine: s.shadbala.planets.map((r) => `${ABBR[r.name]} ${r.percent.toFixed(0)}%`).join(" · "), ok: s.shadbala.planets.every((r) => Math.abs((r.rupas / r.required) * 100 - r.percent) < 0.05) }} />
  )}</Loaded>
);

const Ishta: W = ({ b }) => {
  const [p, setP] = useState("Sun");
  return (
    <Loaded q={useView("strengths")}>{(s) => {
      const r = s.shadbala.planets.find((x) => x.name === p)!;
      const fromDebility = arcGap(lon(b, p), M.DEEP_EXALT[p] + 180);
      const uccha = fromDebility / 3, ishta = Math.sqrt(uccha * r.cheshta), kashta = Math.sqrt((60 - uccha) * (60 - r.cheshta));
      return (
        <Work pick={<Pick items={M.SEVEN} value={p} onChange={setP} label="Graha" />} steps={[
          ["From deep debility", `${dm(fromDebility)} (debility at ${at(M.DEEP_EXALT[p] + 180)})`],
          ["Uccha bala", `${dm(fromDebility)} ÷ 3 = ${uccha.toFixed(2)}`],
          ["Ceṣṭā bala", r.cheshta.toFixed(2)],
          ["Iṣṭa", `√(${uccha.toFixed(2)} × ${r.cheshta.toFixed(2)}) = ${ishta.toFixed(2)}`],
          ["Kaṣṭa", `√(${(60 - uccha).toFixed(2)} × ${(60 - r.cheshta).toFixed(2)}) = ${kashta.toFixed(2)}`],
        ]} check={{ engine: `iṣṭa ${r.ishta.toFixed(2)}, kaṣṭa ${r.kashta.toFixed(2)}`, ok: Math.abs(ishta - r.ishta) < 0.02 && Math.abs(kashta - r.kashta) < 0.02 }} />
      );
    }}</Loaded>
  );
};

const Sav: W = ({ b }) => {
  const sums = Array.from({ length: 12 }, (_, s) => b.av.bav.slice(1, 8).reduce((a, row) => a + row[s], 0));
  const total = sums.reduce((a, x) => a + x, 0);
  const best = sums.indexOf(Math.max(...sums)), worst = sums.indexOf(Math.min(...sums));
  return (
    <Work steps={[
      ["Sun … Saturn, sign by sign", <span className="cx-row">{sums.map((n, s) => <span key={s} className={n > 28 ? "hi" : n < 28 ? "lo" : undefined}>{SIGNS[s]} {n}</span>)}</span>],
      ["Total", `${total} (always 337)`],
      ["Strongest, weakest", `${SIGN_NAMES[best]} ${sums[best]}, ${SIGN_NAMES[worst]} ${sums[worst]}`],
    ]} check={{ engine: `SAV ${b.av.sav.join(" ")}`, ok: sums.every((n, s) => n === b.av.sav[s]) && total === 337 }} />
  );
};

const Trikona: W = () => {
  const [p, setP] = useState("Sun");
  return (
    <Loaded q={useView("strengths")}>{(s) => {
      const i = M.SEVEN.indexOf(p as never) + 1;
      const bav = s.av.bav[i], mine = M.trikonaReduce(bav), engine = s.av.reduced[i];
      return (
        <Work pick={<Pick items={M.SEVEN} value={p} onChange={setP} label="Graha" />} steps={[
          [`${p}'s points`, <span className="cx-row">{bav.map((n, k) => <span key={k}>{SIGNS[k]} {n}</span>)}</span>],
          ...[0, 1, 2, 3].map((g): Step => {
            const trine = [g, g + 4, g + 8], least = Math.min(...trine.map((k) => bav[k]));
            return [trine.map((k) => SIGNS[k]).join(" "), `${trine.map((k) => bav[k]).join(" ")} − ${least} → ${trine.map((k) => mine[k]).join(" ")}`];
          }),
          ["After both reductions", <span className="cx-row">{engine.map((n, k) => <span key={k}>{SIGNS[k]} {n}</span>)}</span>],
        ]} check={{ engine: `Cancer ${engine[3]}, Leo ${engine[4]}`, ok: engine[3] === mine[3] && engine[4] === mine[4] }}
        note="Cancer and Leo have one lord each, so the second reduction never touches them: they are the check." />
      );
    }}</Loaded>
  );
};

const Pinda: W = () => (
  <Loaded q={useView("strengths")}>{(s) => (
    <Work steps={M.SEVEN.map((p, i): Step => {
      const [sodhya, rasi, graha] = s.av.pindas[i + 1];
      return [p, `${rasi} + ${graha} = ${rasi + graha}${rasi + graha === sodhya ? "" : ` (engine ${sodhya})`}`];
    })} check={{ engine: "śodhya piṇḍas " + M.SEVEN.map((_, i) => s.av.pindas[i + 1][0]).join(" "), ok: M.SEVEN.every((_, i) => s.av.pindas[i + 1][1] + s.av.pindas[i + 1][2] === s.av.pindas[i + 1][0]) }} />
  )}</Loaded>
);

const Mahapurusha: W = ({ b }) => {
  const lagna = point(b, "Lagna").rasi;
  const rows = Object.entries(M.MAHAPURUSHA).map(([p, name]) => {
    const s = point(b, p).rasi, h = M.house(lagna, s), dignified = M.isOwnOrExalted(p, s), kendra = [1, 4, 7, 10].includes(h);
    return { p, name, s, h, dignified, kendra, formed: dignified && kendra };
  });
  const formed = rows.filter((r) => r.formed).map((r) => r.name);
  return (
    <Loaded q={useView("strengths")}>{(st) => {
      const engine = st.yogas.filter((y) => y.type === "Mahapurusha").map((y) => y.name);
      return (
        <Work steps={rows.map((r): Step => [r.p, `${SIGN_NAMES[r.s]} (${r.dignified ? M.EXALT[r.p] === r.s ? "exalted" : "own sign" : "neither own nor exalted"}), ${ord(r.h)} house${r.kendra ? ", a kendra" : ""}${r.formed ? ` → ${r.name}` : ""}`])}
          check={{ engine: `formed: ${list(engine)}`, ok: engine.length === formed.length && formed.every((n) => engine.includes(n)), why: "differs: the engine also counts these from the Moon" }} />
      );
    }}</Loaded>
  );
};

const Raja: W = ({ b }) => {
  const lagna = point(b, "Lagna").rasi;
  const lord = (h: number) => M.SIGN_LORD[M.mod(lagna + h - 1, 12)];
  const where = (h: number) => `${lord(h)}, in the ${ord(M.house(lagna, point(b, lord(h)).rasi))}`;
  return (
    <Loaded q={useView("strengths")}>{(st) => (
      <Work steps={[
        ...[1, 4, 7, 10].map((h): Step => [`Kendra ${h}`, where(h)]),
        ...[5, 9].map((h): Step => [`Trikoṇa ${h}`, where(h)]),
        ["Formed here", list(st.yogas.filter((y) => y.type === "Raja").map((y) => y.name))],
      ]} note="The 1st is both a kendra and a trikoṇa, so its lord alone joins both sides." />
    )}</Loaded>
  );
};

const Neecha: W = ({ b }) => {
  const lagna = point(b, "Lagna").rasi, moon = point(b, "Moon").rasi;
  const low = M.SEVEN.filter((p) => M.isDebilitated(p, point(b, p).rasi));
  if (!low.length) return <Work steps={[["Debilitated", "none in this chart"]]} />;
  return (
    <Work steps={low.map((p): Step => {
      const s = point(b, p).rasi, d = M.SIGN_LORD[s], ds = point(b, d).rasi;
      const fromL = M.house(lagna, ds), fromM = M.house(moon, ds), k = (h: number) => [1, 4, 7, 10].includes(h);
      return [p, `debilitated in ${SIGN_NAMES[s]}; its lord ${d} is ${ord(fromL)} from the Lagna and ${ord(fromM)} from the Moon: ${k(fromL) || k(fromM) ? "cancelled by this rule" : "not cancelled by this rule"}`];
    })} />
  );
};

/* -------------------------------------------------------------------------- */
/*                                4. TIMING                                   */
/* -------------------------------------------------------------------------- */

const YEARS: [string, number][] = [["sāvana", 360], ["tropical", 365.2422], ["sidereal", 365.25636]];
function useVimsottari(birth: Birth, path: number[] = []) {
  return useQuery({ queryKey: ["calcVims", birth, path], queryFn: () => api.dasa(birth, "vimsottari_dasa", path) });
}
const daysFromBirth = (birth: Birth, iso: string) => (Date.parse(iso.slice(0, 23) + "Z") - (utc(birth.year, birth.month, birth.day) + birth.hour_local * 3.6e6)) / 864e5;

const Balance: W = ({ b, birth }) => {
  const moon = lon(b, "Moon"), v = M.vimsottariBalance(moon);
  const d = useVimsottari(birth).data;
  const days = d?.periods[0] ? daysFromBirth(birth, d.periods[0].end) : NaN;
  return (
    <Work steps={[
      ["Moon", `${at(moon)} (${M.mod(moon).toFixed(4)}°)`],
      ["Its star", `${v.name}, ${v.start.toFixed(3)}° to ${v.end.toFixed(3)}°, ruled by ${v.lord} (${v.years} years)`],
      ["Share left", `(${v.end.toFixed(3)}° − ${M.mod(moon).toFixed(3)}°) ÷ 13°20′ = ${pct(v.left)}`],
      ["Balance", `${pct(v.left)} × ${v.years} = ${v.balance.toFixed(4)} years, ${ym(v.balance)} of ${v.lord}`],
    ]} check={Number.isFinite(days) ? { engine: `${v.lord} daśā runs ${days.toFixed(1)} days from birth (${d!.years})`, ok: YEARS.some(([, y]) => Math.abs(days - v.balance * y) < 4) } : undefined}
    note="A true solar year follows the Sun's uneven speed, so its dates can sit a few days from a mean year's." />
  );
};

const Antardasa: W = ({ b, birth }) => {
  const lord = M.vimsottariBalance(lon(b, "Moon")).lord;
  const subs = M.antardasas(lord);
  const d = useVimsottari(birth, [0]).data;
  const ok = !!d && d.periods.length === 9 && subs.every((s, i) => Math.abs(d.periods[i].years - s.months / 12) < 0.001);
  return (
    <Work steps={subs.map((s): Step => [`${lord}–${s.lord}`, `${M.VIMS.find(([p]) => p === lord)![1]} × ${M.VIMS.find(([p]) => p === s.lord)![1]} ÷ 10 = ${s.months.toFixed(1)} months (${ym(s.months / 12)})`])}
      check={d ? { engine: d.periods.map((x) => x.years.toFixed(3)).join(" · ") + " years", ok } : undefined}
      note={`The first daśā of this chart is ${lord}'s; its opening sub-periods were already over at birth.`} />
  );
};

const YearLength: W = ({ b, birth }) => {
  const v = M.vimsottariBalance(lon(b, "Moon"));
  const d = useVimsottari(birth).data;
  return (
    <Work steps={YEARS.map(([n, y]): Step => [`${n} year, ${y} days`, `${v.balance.toFixed(4)} × ${y} = ${(v.balance * y).toFixed(1)} days`])}
      note={d && `The engine counts in: ${d.years}.`} />
  );
};

const title = (key: string) => key.replace(/_dasa$/, "").split("_").map((w) => w[0].toUpperCase() + w.slice(1)).join(" ");
const Conditional: W = ({ birth }) => {
  const q = useQuery({ queryKey: ["calcBestDasa", birth], queryFn: () => api.bestDasa(birth) });
  return (
    <Loaded q={q}>{(d) => (
      <Work steps={[
        ...d.rows.map((r): Step => [title(r.key), `${r.condition}: ${r.met ? "holds" : "does not hold"}`]),
        ["Use", list(d.best.map(title))],
      ]} />
    )}</Loaded>
  );
};

function useNow(birth: Birth) {
  return useQuery({
    queryKey: ["calcNow", birth], staleTime: 10 * 60_000,
    queryFn: async () => { const r = await api.transitMode(birth, nowMoment()); return api.basics(r.birth, ""); },
  });
}
const nowSigns = (n: Basics) => Object.fromEntries(M.PLANETS.map((p) => [p, point(n, p).rasi]));

const Gocara: W = ({ b, birth }) => {
  const moon = point(b, "Moon").rasi;
  return (
    <Loaded q={useNow(birth)}>{(n) => {
      const signs = nowSigns(n);
      return (
        <Work steps={[
          ["Natal Moon", SIGN_NAMES[moon]],
          ...M.PLANETS.map((p): Step => { const g = M.gocara(p, moon, signs); return [p, `today in ${SIGN_NAMES[signs[p]]}, ${ord(g.house)} from the Moon: ${g.good ? "good" : "not good"}`]; }),
        ]} note={`Today's sky, ${new Date().toLocaleDateString()}, at the birthplace.`} />
      );
    }}</Loaded>
  );
};

const Vedha: W = ({ b, birth }) => {
  const moon = point(b, "Moon").rasi;
  return (
    <Loaded q={useNow(birth)}>{(n) => {
      const signs = nowSigns(n);
      const good = M.PLANETS.map((p) => ({ p, ...M.gocara(p, moon, signs) })).filter((g) => g.good);
      return (
        <Work steps={good.length ? good.map((g): Step => [g.p, `good in the ${ord(g.house)}; blocked from the ${ord(g.vedha!)}: ${g.blockers.length ? `yes, by ${g.blockers.join(", ")}` : "no one there, so it stands"}`]) : [["Good transits", "none today"]]} />
      );
    }}</Loaded>
  );
};

function completedYears(birth: Birth) {
  const n = new Date();
  return n.getFullYear() - birth.year - (n.getMonth() + 1 < birth.month || (n.getMonth() + 1 === birth.month && n.getDate() < birth.day) ? 1 : 0);
}

const Muntha: W = ({ b, birth }) => {
  const lagna = point(b, "Lagna").rasi, years = completedYears(birth), m = M.muntha(lagna, years);
  return (
    <Work steps={[
      ["Lagna", SIGN_NAMES[lagna]],
      ["Completed years", `${years} (to today)`],
      ["Munthā", `${lagna} + ${years} = ${lagna + years}, mod 12 → ${SIGN_NAMES[m]}`],
    ]} note="Near the birthday the exact solar return decides which year has begun." />
  );
};

const Saham: W = ({ b, birth }) => {
  const { day } = dayTimes(b, birth);
  const L = lon(b, "Lagna"), sun = lon(b, "Sun"), moon = lon(b, "Moon");
  const s = M.punyaSaham(L, sun, moon, day);
  const f = (x: number) => `${M.mod(x).toFixed(2)}°`;
  return (
    <Work steps={[
      ["Born", day ? "by day" : "by night"],
      ["Puṇya Saham", day ? `${f(L)} + ${f(moon)} − ${f(sun)}` : `${f(L)} + ${f(sun)} − ${f(moon)}`],
      ["", `= ${f(s)}, ${at(s)}`],
    ]} />
  );
};

const Angle: W = ({ b }) => {
  const sun = lon(b, "Sun"), moon = lon(b, "Moon"), p = M.panchanga(sun, moon), engine = lon(b, "Tithi Sphuta");
  return (
    <Work steps={[
      ["Moon − Sun", `${M.mod(moon).toFixed(4)}° − ${M.mod(sun).toFixed(4)}° = ${p.elong.toFixed(4)}°`],
      ["As a tithi", `${p.tithiName}, ${pct(1 - p.tithiLeft)} gone`],
    ]} check={{ engine: `Tithi Sphuta ${engine.toFixed(4)}°`, ok: arcGap(p.elong, engine) < 0.001 }} />
  );
};

/* -------------------------------------------------------------------------- */
/*                             5. OTHER SCHOOLS                               */
/* -------------------------------------------------------------------------- */

const Karakas: W = ({ b }) => {
  const k = M.charaKarakas(Object.fromEntries([...M.SEVEN, "Rahu"].map((p) => [p, lon(b, p)])));
  const ok = k.every((x) => (point(b, x.planet).karaka ?? "").split("/").includes(x.slot));
  return (
    <Work steps={k.map((x): Step => [x.slot, `${x.planet}, ${dm(x.deg)}${x.planet === "Rahu" ? " (30° less its degrees)" : ""}`])}
      check={{ engine: [...M.SEVEN, "Rahu"].map((p) => `${ABBR[p]} ${point(b, p).karaka ?? "–"}`).join(" · "), ok, why: "differs: the Chara kāraka setting uses a seven-kāraka scheme" }} />
  );
};

const Arudha: W = ({ b, birth }) => {
  const L = point(b, "Lagna").rasi, lord = M.SIGN_LORD[L], ls = point(b, lord).rasi, a = M.arudha(L, ls);
  const q = useQuery({ queryKey: ["calcKeyInfo", birth], queryFn: () => api.keyInfo(birth, 1) });
  const al = q.data?.find((r) => r.name === "AL");
  return (
    <Work steps={[
      ["Lagna", SIGN_NAMES[L]],
      ["Its lord", `${lord}, in ${SIGN_NAMES[ls]}: the ${ord(a.count)} from the Lagna`],
      [`${ord(a.count)} again from ${lord}`, SIGN_NAMES[a.raw]],
      ["Exception", a.exception ? `that is the ${a.exception === "10th" ? "Lagna itself" : "7th"}, so take the ${a.exception} from the Lagna` : "none"],
      ["Ārūḍha Lagna", SIGN_NAMES[a.pada]],
    ]} check={al ? { engine: `AL in ${SIGN_NAMES[al.rasi]}`, ok: al.rasi === a.pada, why: L === 7 || L === 10 ? "differs: this sign has two lords and the engine takes the stronger" : "differs: the Ārūḍha exceptions are set differently" } : undefined} />
  );
};

const Argala: W = ({ b }) => {
  const L = point(b, "Lagna").rasi;
  const at_ = (h: number) => occupants(b, M.mod(L + h - 1, 12), "Lagna");
  return (
    <Work steps={[[2, 12], [4, 10], [11, 3], [5, 9]].map(([a, o]): Step => [`${ord(a)} against ${ord(o)}`, `${list(at_(a), "empty")} against ${list(at_(o), "empty")}`])}
      note="Counted from the Lagna. Whichever side holds more grahas prevails." />
  );
};

const KP_PLANETS = ["As", "Su", "Mo", "Ma", "Me", "Ju", "Ve", "Sa", "Ra", "Ke"];
const FULL = Object.fromEntries(Object.entries(ABBR).map(([k, v]) => [v, k]));
const Sub: W = () => {
  const [p, setP] = useState("Mo");
  return (
    <Loaded q={useView("kp")}>{(rows) => {
      const r = rows.find((x) => x.label === p)!;
      const k = M.kpLords(r.lon);
      const engine = r.lords.slice(0, 3).map((x) => FULL[x] ?? x);
      return (
        <Work pick={<Pick items={KP_PLANETS} value={p} onChange={setP} label="Point" names={FULL} />} steps={[
          [FULL[p], `${M.mod(r.lon).toFixed(4)}°, in ${k.star.name} (${k.star.start.toFixed(3)}° to ${k.star.end.toFixed(3)}°)`],
          ["Star lord", k.star.lord],
          ["Its subs", <span className="cx-row">{k.subs.map((s) => <span key={s.lord} className={s === k.sub ? "hi" : undefined}>{ABBR[s.lord]} {s.to.toFixed(3)}°</span>)}</span>],
          ["Sub lord", `${k.sub.lord}, ${k.sub.from.toFixed(3)}° to ${k.sub.to.toFixed(3)}°`],
          ["Sub-sub lord", k.subsub.lord],
        ]} check={{ engine: engine.join(" · "), ok: engine.join() === k.lords.join() }} note="Each sub is shown by where it ends; the marked one holds the point." />
      );
    }}</Loaded>
  );
};

const Cusps: W = () => (
  <Loaded q={useView("kp")}>{(rows) => (
    <Work steps={rows.filter((r) => r.label.endsWith("bhava")).map((r): Step => [r.label, `${at(r.lon)}: star ${FULL[r.lords[0]]}, sub ${FULL[r.lords[1]]}, sub-sub ${FULL[r.lords[2]]}`])} />
  )}</Loaded>
);

/* -------------------------------------------------------------------------- */
/*                                6. APPLIED                                  */
/* -------------------------------------------------------------------------- */

function useLongevity(birth: Birth) {
  return useQuery({ queryKey: ["calcLongevity", birth], queryFn: () => api.longevity(birth) });
}

const Pindayu: W = ({ b, birth }) => {
  const q = useLongevity(birth);
  const t = q.data?.find((s) => s.id === "spans")?.tables.find((x) => x.title.startsWith("Pindayu"));
  const col = t?.columns.indexOf("By arc") ?? -1;
  const mine = M.SEVEN.map((p) => ({ p, ...M.arcYears(p, lon(b, p)) }));
  const ok = !!t && col >= 0 && mine.every((m) => { const row = t.rows.find((r) => r[0] === m.p); return !!row && Math.abs(Number(row[col]) - m.years) < 0.01; });
  return (
    <Work steps={[
      ...mine.map((m): Step => [m.p, `arc ${dm(m.arc)} from ${at(M.DEEP_EXALT[m.p])} → ${M.PINDA_YEARS[m.p]} × ${dm(m.arc < 180 ? 360 - m.arc : m.arc)} ÷ 360° = ${m.years.toFixed(2)}`]),
      ["Sum", `${mine.reduce((a, m) => a + m.years, 0).toFixed(2)} years, before the reductions`],
    ]} check={t ? { engine: "by arc " + M.SEVEN.map((p) => t.rows.find((r) => r[0] === p)?.[col]).join(" · "), ok } : undefined}
    note="The Longevity tab then halves and trims these (BPHS 43.9–11) and adds the Lagna." />
  );
};

const CLASS = { long: "Long", medium: "Medium", short: "Short" };
const Pairs: W = ({ b, birth }) => {
  const q = useLongevity(birth);
  const L = point(b, "Lagna").rasi, lord1 = M.SIGN_LORD[L], lord8 = M.SIGN_LORD[M.mod(L + 7, 12)];
  const pairs: [string, string, number, string, number][] = [
    ["Lagna lord and 8th lord", `${lord1} in`, point(b, lord1).rasi, `${lord8} in`, point(b, lord8).rasi],
    ["Saturn and Moon", "Saturn in", point(b, "Saturn").rasi, "Moon in", point(b, "Moon").rasi],
    ["Lagna and Horā Lagna", "Lagna", L, "HL", point(b, "Hora Lagna").rasi],
  ];
  const classes = pairs.map(([, , a, , c]) => M.jaiminiClass(a, c));
  const engine = q.data?.find((s) => s.id === "pairs")?.tables[0]?.rows.map((r) => r[r.length - 1].split(" ")[0].toLowerCase());
  const s = (n: number) => `${SIGN_NAMES[n]} (${M.modality(n)})`;
  return (
    <Work steps={pairs.map(([name, a, as, c, cs], i): Step => [name, `${a} ${s(as)}, ${c} ${s(cs)} → ${CLASS[classes[i]]}`])}
      check={engine ? { engine: engine.map((c) => c[0].toUpperCase() + c.slice(1)).join(" · "), ok: classes.every((c, i) => c === engine[i]), why: "differs: Scorpio or Aquarius has two lords and the engine takes the stronger" } : undefined} />
  );
};

const Kuja: W = ({ b }) => {
  const mars = point(b, "Mars").rasi;
  const from = (n: string) => M.house(point(b, n).rasi, mars);
  return (
    <Work steps={[
      ...["Lagna", "Moon", "Venus"].map((n): Step => [`From the ${n}`, `Mars ${ord(from(n))}: ${M.KUJA_HOUSES.includes(from(n)) ? "doṣa" : "clear"}`]),
      ["Mars's sign", `${SIGN_NAMES[mars]}${M.isOwnOrExalted("Mars", mars) ? ", own or exalted: the doṣa is softened" : ""}`],
    ]} />
  );
};

const Kutas: W = ({ b }) => {
  const [as, setAs] = useState("bride");
  const q = useQuery({ queryKey: ["calcMatchMatrix"], queryFn: api.matchingMatrix, staleTime: Infinity });
  const n = M.nakshatraOf(lon(b, "Moon"));
  return (
    <Loaded q={q}>{(m) => {
      const me = m.parts.find((x) => x.nakshatra === n.index && x.padas.includes(n.pada));
      if (!me) return null;
      const row = m.parts.map((x) => ({ x, score: as === "bride" ? m.scores[me.index][x.index] : m.scores[x.index][me.index] })).sort((a, c) => c.score - a.score);
      const name = (r: (typeof row)[number]) => `${r.x.label} ${r.score}`;
      return (
        <Work pick={<Pick items={["bride", "groom"]} value={as} onChange={setAs} label="This chart as" names={{ bride: "As the bride", groom: "As the groom" }} />} steps={[
          ["Moon's star", `${n.name}, pada ${n.pada}`],
          ["Best partners", row.slice(0, 3).map(name).join(" · ")],
          ["Weakest", row.slice(-3).map(name).join(" · ")],
          ["18 points or more", `${row.filter((r) => r.score >= 18).length} of ${row.length} star groups`],
        ]} note="Scores out of 36, from the same table as the Matching tab." />
      );
    }}</Loaded>
  );
};

const Eclipse: W = ({ b }) => (
  <Work steps={["Lagna", "Sun", "Moon"].map((n): Step => { const x = lon(b, n); return [n, `${at(x)}: an eclipse from ${at(x - 3.5)} to ${at(x + 3.5)}`]; })} />
);

const WORKED: Record<string, W> = {
  ayanamsa: Ayanamsa, lagna: Lagna, ghati: Ghati, limbs: Limbs, rahukala: RahuKala,
  segment: D12, navamsa: Navamsa, drishti: Drishti, maitri: Maitri, sambandha: Sambandha, special: Special, aprakasha: Aprakasha, gulika: Gulika,
  six: Six, required: Required, ishta: Ishta, sav: Sav, trikona: Trikona, pinda: Pinda, mahapurusha: Mahapurusha, raja: Raja, neecha: Neecha,
  balance: Balance, antardasa: Antardasa, year: YearLength, conditional: Conditional, gocara: Gocara, vedha: Vedha, muntha: Muntha, saham: Saham, angle: Angle,
  karakas: Karakas, arudha: Arudha, argala: Argala, sub: Sub, cusps: Cusps,
  pindayu: Pindayu, pairs: Pairs, kuja: Kuja, kutas: Kutas, eclipse: Eclipse,
};

/* -------------------------------------------------------------------------- */
/*                               MAIN COMPONENT                               */
/* -------------------------------------------------------------------------- */

const CHAPTERS: { id: string; name: string; title: string; lede: string }[] = [
  { id: "moment", name: "Moment", title: "The moment",
    lede: "A chart is a picture of one moment from one place. Before anything is read, three things are measured: where the bodies stand among the stars, which degree is rising, and where the moment falls in the Vedic day." },
  { id: "map", name: "Map", title: "The map",
    lede: "From the longitudes come the signs and bhavas, the divisional charts that look closer at each field of life, the aspects and friendships among the grahas, and the sensitive points that are not bodies at all." },
  { id: "strength", name: "Bala", title: "Bala",
    lede: "A placement promises; bala decides how much of the promise is kept. Parāśara measures bala three ways: in numbers, by points from the other grahas, and by named combinations." },
  { id: "timing", name: "Timing", title: "Timing",
    lede: "The chart says what; timing says when. Daśās hand out the years to the grahas in turn, transits read today's sky against the birth chart, and the annual charts open each new year." },
  { id: "schools", name: "Schools", title: "Other schools",
    lede: "Two later systems read the same sky differently. Jaimini ranks grahas by degree and looks at bhavas through their images. Krishnamurti cuts the stars finer to decide yes or no." },
  { id: "applied", name: "Applied", title: "Applied questions",
    lede: "The same arithmetic answers particular questions: how long a life runs, whether two charts suit each other, and when the wider world touches a single chart." },
];

function Topic({ topic }: { topic: CalcTopic }) {
  const { birth } = useChart();
  const basics = useBasics();
  return (
    <>
      <h3 className="rm-title">{topic.title}</h3>
      <p className="rm-prose">{topic.lede}</p>
      {topic.sections.map((s) => {
        const C = WORKED[s.id];
        return (
          <section key={s.id} className="cx-section">
            <h4 className="rm-title minor">{s.heading}</h4>
            <p className="rm-prose">{s.body}</p>
            {C && (!birth
              ? <p className="rm-note">Open a chart to see this worked on it.</p>
              : <Loaded q={basics}>{(b) => <C b={b} birth={birth} />}</Loaded>)}
          </section>
        );
      })}
    </>
  );
}

function Rules({ topic }: { topic: CalcTopic }) {
  const { go } = useChart();
  const rules = topic.sections.filter((s) => s.formula);
  return (
    <section className="rm-verses">
      <div className="rm-verses-head"><h3 className="rm-title minor">The rule</h3></div>
      <p className="rm-cite">{topic.source}</p>
      {rules.map((s) => (
        <article key={s.id} className="rm-verse">
          <header><div><h4>{s.heading}</h4></div><CopyButton text={s.formula!} /></header>
          <pre className="cx-formula">{s.formula}</pre>
        </article>
      ))}
      {!rules.length && <p className="rm-note">This topic has no formula of its own to set out.</p>}
      <button type="button" className="rm-go" onClick={() => go(topic.tab)}>Open the {topic.tab} tab</button>
    </section>
  );
}

export function Calculations() {
  const q = useQuery({ queryKey: ["calcTopics"], queryFn: api.calculationTopics, staleTime: Infinity });
  const [saved, setId] = useSaved<string>("calcTopic", "chart-core");
  const { name, birth } = useChart();

  return (
    <section className="pane rm cx">
      <Loaded q={q}>
        {({ topics }) => {
          const ix = Math.max(0, topics.findIndex((t) => t.id === saved));
          const topic = topics[ix];
          const ci = CHAPTERS.findIndex((c) => c.id === topic.chapter);
          const chapter = CHAPTERS[ci];
          const inChapter = topics.filter((t) => t.chapter === chapter.id);
          const prev = topics[ix - 1], next = topics[ix + 1];
          return (
            <>
              <header className="pane-head rm-head">
                <h2>Calculations</h2>
                <nav className="rm-path" aria-label="Chapters">
                  {CHAPTERS.map((c, i) => (
                    <button key={c.id} type="button" aria-current={i === ci ? "step" : undefined} className={i < ci ? "done" : undefined}
                      onClick={() => setId(topics.find((t) => t.chapter === c.id)!.id)} title={c.title}>
                      <span>{i + 1}</span><b>{c.name}</b>
                    </button>
                  ))}
                </nav>
                <span className="rm-status">{birth ? `Worked on ${name || "this chart"}` : "No chart open"}</span>
              </header>
              {/* keyed so a new topic opens at its top */}
              <div className="rm-main" key={topic.id}>
                <div className="rm-left">
                  <header className="rm-chapter">
                    <h2><span className="rm-num" aria-hidden>{ci + 1}</span>{chapter.title}</h2>
                    <p className="rm-lede">{chapter.lede}</p>
                  </header>
                  {inChapter.length > 1 && (
                    <div className="rm-chips" role="group" aria-label="Topics">
                      {inChapter.map((t) => <button key={t.id} type="button" aria-pressed={t.id === topic.id} onClick={() => setId(t.id)}>{t.title}</button>)}
                    </div>
                  )}
                  <Topic topic={topic} />
                  <nav className="rm-pager" aria-label="Previous and next topic">
                    {prev ? <button type="button" onClick={() => setId(prev.id)}><small>Previous</small>{prev.title}</button> : <span />}
                    {next && <button type="button" className="next" onClick={() => setId(next.id)}><small>Next, {ix + 2} of {topics.length}</small>{next.title}</button>}
                  </nav>
                </div>
                <aside className="rm-side" aria-label="The rule"><Rules topic={topic} /></aside>
              </div>
            </>
          );
        }}
      </Loaded>
    </section>
  );
}
