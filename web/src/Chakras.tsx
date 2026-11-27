import { Fragment, useEffect, useMemo, useState, type ReactNode } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { api, nowMoment, type Birth, type ChakraOptions, type Chakras, type SpecialPoint } from "./api";
import { FormButtons, Modal } from "./ChartDialogs";
import { GHATAKA, ghatakaHits, MONTHS, SHALAKA, shalakaPartner, SYLLABLES, TARA_KIND, TARA_NAMES, TITHI_GROUPS, WEEKDAY_NAMES } from "./chakraTables";
import { ManyVargas } from "./ChartPane";
import { SIGN_NAMES, SIGNS } from "./format";
import { useBasics, useKept, useSaved } from "./hooks";
import { Icon } from "./Icons";
import { useMenu, type MenuEntry } from "./Menu";
import { MixedChart } from "./Mixed";
import { useMoment } from "./Modes";
import { KeyInfo, SmallAv } from "./Panels";
import { transitBase, useChart } from "./store";
import { Loaded, SubTabs, supOrd } from "./ui";
import { Avakahada, CHANDRA, Ghataka, KALA, Kota, KOTA_ZONES, kotaZone, Kurma, type Picks, SaptaShalaka, Sarvatobhadra, type SbcGraha, SHOOLA, StarWheel, Sudarsana, SURYA, TaraChakra, Tripataki, triVedhas, vedhas } from "./Wheels";
import { SBC, vedhaLines } from "./wheelGeometry";
import { DIVISIONS, DivisionSelect } from "./Windows";

const TABS = [{ id: "many", name: "Divisional charts" }, { id: "mixed", name: "Mixed 2-Vargas" }, { id: "kala", name: "Kalachakra" }, { id: "sbc", name: "Sarvatobhadra" },
  { id: "tara", name: "Tara Chakra" }, { id: "shalaka", name: "Sapta Shalaka" }, { id: "avakahada", name: "Avakahada" }, { id: "ghataka", name: "Ghataka" },
  { id: "kota", name: "Kota Chakra" }, { id: "kurma", name: "Kurma Chakra" }, { id: "surya", name: "Surya Kalanala" }, { id: "chandra", name: "Chandra Kalanala" }, { id: "sudarsana", name: "Sudarsana" },
  { id: "shoola", name: "Shoola" }, { id: "tripataki", name: "Tripataki" }] as const;
const BODY_SETS: [string, string][] = [["planets", "Show Grahas"], ["yogini", "Show Yogini and Mrityu"], ["trisphuta", "Show Trisphuta etc"], ["upagrahas", "Show Upagrahas"], ["lagnas", "Show Special Lagnas"], ["sahams", "Show Sahamas"]];
const BASE_POINTS = ["Lagna", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu", "Uranus", "Neptune", "Pluto"];
const STARS_28 = ["Aswini", "Bharani", "Krittika", "Rohini", "Mrigasira", "Ardra", "Punarvasu", "Pushyami", "Asresha", "Magha", "Poorva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swaati", "Visaakha", "Anooradha", "Jyeshtha", "Moola", "Poorvashadha", "Uttarashadha", "Abhijit", "Sravanam", "Dhanishtha", "Satabhisham", "Poorvabhadra", "Uttarabhadra", "Revati"];
const TARAS = ["Janma tara (birth)", "Sampat tara (wealth)", "Vipat tara (danger)", "Kshema tara (well-being)", "Pratyak tara (obstacles)", "Sadhana tara (achievement)", "Naidhana tara (death)", "Mitra tara (friend)", "Parama mitra tara (good friend)"];
const SPECIAL_NAKS = ["Janma (birth)", "Karma (profession)", "Samudayika (crowd)", "Sanghatika (group)", "Jaati (community)", "Naidhana (death)", "Desa (country)", "Abhisheka (coronation)", "Aadhaana (epoch/conception)", "Vainasika (destruction)", "Maanasa (mind)"];
const SPECIAL_TITHIS = ["Janma tithi (1st)", "Dhana tithi (2nd)", "Bhratri tithi (3rd)", "Matri tithi (4th)", "Putra tithi (5th)", "Satru tithi (6th)", "Dara tithi (7th)", "Mrityu tithi (8th)", "Pitri tithi (9th)", "Karma tithi (10th)", "Laabha tithi (11th)", "Vyaya tithi (12th)"];
const HOUSE_POINTS = ["Lagna", "Arudha lagna", "Upapada lagna", "Hora lagna", "Ghati lagna", "Bhava lagna", "Varnada lagna", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"];
const ORDINALS = ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th", "10th", "11th", "12th"];

function Mixed2() {
  const birth = useChart((s) => s.birth)!;
  const b = useBasics();
  const [outer, setOuter] = useState(9);
  const [inner, setInner] = useState(1);
  const pick = (label: string, v: number, set: (n: number) => void) => (
    <label className="row">{label}
      <select value={v} onChange={(e) => set(Number(e.target.value))}>{DIVISIONS.map((d) => <option key={d} value={d}>D-{d}</option>)}</select>
    </label>
  );
  return (
    <div className="pad mixed-screen">
      <div>
        <div className="row bottom-gap">{pick("Outer", outer, setOuter)}{pick("Inner", inner, setInner)}</div>
        <MixedChart outerBirth={birth} outerName="" innerBirth={birth} innerName="" outerDiv={outer} innerDiv={inner} />
      </div>
      {b.data && <div className="side"><SmallAv b={b.data} /></div>}
    </div>
  );
}

function BaseDialog({ options, onOk, onClose }: { options: ChakraOptions; onOk: (o: ChakraOptions) => void; onClose: () => void }) {
  const [point, setPoint] = useState(options.base_point ?? 1);
  const [division, setDivision] = useState(options.base_division ?? 1);
  return (
    <Modal title="Select a graha as base" onClose={onClose}>
      <form method="dialog" onSubmit={(e) => { e.preventDefault(); onOk({ ...options, base_point: point, base_division: division, base_star: null }); onClose(); }}>
        <label>Graha whose nakshatra is to be used as the base (seed)<select value={point} onChange={(e) => setPoint(Number(e.target.value))}>{BASE_POINTS.map((n, i) => <option key={n} value={i}>{n}</option>)}</select></label>
        <label>in the divisional chart<DivisionSelect value={division} onChange={setDivision} /></label>
        <FormButtons />
      </form>
    </Modal>
  );
}

function StarDialog({ options, note, onOk, onClose }: { options: ChakraOptions; note: string; onOk: (o: ChakraOptions) => void; onClose: () => void }) {
  const [custom, setCustom] = useState(options.base_star !== null && options.base_star !== undefined);
  const [star, setStar] = useState(options.base_star ?? 0);
  return (
    <Modal title="Choose the base nakshatra" onClose={onClose}>
      <p className="muted">{note}</p>
      <form method="dialog" onSubmit={(e) => { e.preventDefault(); onOk({ ...options, base_star: custom ? star : null, base_point: null }); onClose(); }}>
        <label><select value={String(custom)} onChange={(e) => setCustom(e.target.value === "true")}><option value="false">Stick to the default base star mentioned above</option><option value="true">No, use the following star as the base instead</option></select></label>
        <label>Base star<select value={star} disabled={!custom} onChange={(e) => setStar(Number(e.target.value))}>{STARS_28.map((n, i) => <option key={n} value={i}>{n}</option>)}</select></label>
        <FormButtons />
      </form>
    </Modal>
  );
}

/** The date dialog, for wheels that show a transit date of their own. */
function DateDialog({ onOk, onClose }: { onOk: (b: Birth) => void; onClose: () => void }) {
  const natal = useChart(transitBase)!;
  const { fields, moment } = useMoment();
  const find = useMutation({ mutationFn: () => api.transitMode(natal, moment()), onSuccess: (r) => { onOk(r.birth); onClose(); } });
  return (
    <Modal title="Change Date and Time" onClose={onClose}>
      <form method="dialog" onSubmit={(e) => { e.preventDefault(); find.mutate(); }}>
        {fields}
        {find.error && <p role="alert" className="error">{find.error.message}</p>}
        <FormButtons />
      </form>
    </Modal>
  );
}

function pickList(title: string, list: string[], withDivision: boolean, onOk: (i: number, d: number) => void, onClose: () => void) {
  return <PickDialog title={title} list={list} withDivision={withDivision} onOk={onOk} onClose={onClose} />;
}

function PickDialog({ title, list, withDivision, onOk, onClose }: { title: string; list: string[]; withDivision: boolean; onOk: (i: number, d: number) => void; onClose: () => void }) {
  const [i, setI] = useState(0);
  const [d, setD] = useState(1);
  return (
    <Modal title={title} onClose={onClose}>
      <form method="dialog" onSubmit={(e) => { e.preventDefault(); onOk(i, d); onClose(); }}>
        <label><select value={i} onChange={(e) => setI(Number(e.target.value))}>{list.map((n, k) => <option key={n} value={k}>{n}</option>)}</select></label>
        {withDivision && <label>in the divisional chart<DivisionSelect value={d} onChange={setD} /></label>}
        <FormButtons />
      </form>
    </Modal>
  );
}

function boxesOf(p: SpecialPoint) {
  const out = new Set<string>();
  SBC.forEach((row, r) => row.forEach((cell, c) => {
    const key = `${r}-${c}`;
    if (typeof cell === "string") {
      if (cell.startsWith("*") && p.stars?.includes(cell.slice(1))) out.add(key);
      if (p.signs?.includes(cell)) out.add(key);
    } else if (cell[0] === p.tithi) out.add(key);
  }));
  return out;
}

type Form = { kind: "tara" | "special_nakshatra" | "tithi" | "planet" | "house" | "from_tara" | "from_special" | "base" | "star" | "date" | "varga"; star?: string } | null;
type View = "both" | "natal" | "transit";
type Row = { key: string; cells: ReactNode[] };

const ABBR28 = ["Aswi", "Bhar", "Krit", "Rohi", "Mrig", "Ardr", "Puna", "Push", "Asre", "Magh", "PPha", "UPha", "Hast", "Chit", "Swat", "Visa", "Anu", "Jye", "Mool", "PSha", "USha", "Abhi", "Srav", "Dhan", "Sata", "PBha", "UBha", "Reva"];
const GRAHAS = ["Su", "Mo", "Ma", "Me", "Ju", "Ve", "Sa", "Ra", "Ke"];
const BENEFICS = new Set(["Mo", "Me", "Ju", "Ve"]);
const VIEWS: { id: View; name: string }[] = [{ id: "both", name: "Natal + Transit" }, { id: "natal", name: "Natal" }, { id: "transit", name: "Transit" }];
const STEPS: [string, number, number][] = [["Hour", 3600, 0], ["Day", 86400, 0], ["Week", 604800, 0], ["Month", 0, 1], ["Year", 0, 12]];
const ROTATING = new Set(["kala", "kota", "surya", "chandra", "shoola"]);
// the trident points, by slot: Surya's three tridents, Chandra's four, Shoola's three prongs
const TIPS: Record<string, number[]> = { surya: [10, 11, 12, 13, 14, 15, 16, 17, 18], chandra: [27, 0, 1, 6, 7, 8, 13, 14, 15, 20, 21, 22], shoola: [7, 8, 9, 13, 14, 15, 19, 20, 21] };
// each drawing's width over its height (its viewBox), so the wheel's column is exactly as wide as the wheel
const ASPECT: Record<string, number> = { tara: 990 / 424, shalaka: 1, avakahada: 990 / 900, ghataka: 990 / 722, kala: 840 / 810, surya: 960 / 780, chandra: 830 / 750, shoola: 590 / 780, tripataki: 860 / 800 };
const DIRECTIONS = KALA.labels!.map(([t]) => t);
const KURMA_NAMES: Record<string, string> = { Madhya: "Centre (Madhya desa)", East: "East (Prachya)", SE: "South-east (Agneya)", South: "South (Dakshina)", SW: "South-west (Nairritya)", West: "West (Paschima)", NW: "North-west (Vayavya)", North: "North (Uttara)", NE: "North-east (Aisanya)" };
const SBC_SOUNDS = SBC.flat().filter((c): c is string => typeof c === "string" && !c.startsWith("*") && !SIGNS.includes(c));

const star27 = (s: string) => { const i = ABBR28.indexOf(s); return i > 21 ? i - 1 : Math.min(i, 20); };   // Abhijit counts as Uttarashadha
const taraOf = (s: string, moon: string) => TARAS[(star27(s) - star27(moon) + 27) % 27 % 9];
const starName = (s: string) => STARS_28[ABBR28.indexOf(s)] ?? s;
const STARS_27 = STARS_28.filter((x) => x !== "Abhijit"), ABBR27 = ABBR28.filter((x) => x !== "Abhi");
// the tabs Starlight adds to the Windows layout's
const STARLIGHT_ONLY = new Set(["tara", "shalaka", "avakahada", "ghataka"]);
const DATED = new Set(["View transits on this date", "Back to the current chart"]);
// the Sarvatobhadra's main vedha by a graha's motion, and the motion's name
const SIDE = { retro: "right", fast: "left", normal: "front" } as const;
const MOTION = { retro: "retrograde", fast: "fast", normal: "usual pace" } as const;
/** Kalachakra: the direction of a slot, by its angle round the wheel's hub, East at the top. */
const kalaDir = (i: number) => { const [x, y] = KALA.slots[i]; return Math.round(((Math.atan2(x - 435, 582 - y) * 180 / Math.PI + 360) % 360) / 45) % 8; };
const pad2 = (n: number) => String(n).padStart(2, "0");
const whenOf = (b: Birth) => { const m = Math.round(b.hour_local * 60); return `${b.year}-${pad2(b.month)}-${pad2(b.day)} ${pad2(Math.floor(m / 60) % 24)}:${pad2(m % 60)}`; };
const grahas = (names: string[]) => names.filter((n) => GRAHAS.includes(n));
const tone = (g: string) => <span key={g} className={BENEFICS.has(g) ? "benefic" : "malefic"}>{g}</span>;
const list = (gs: string[]) => gs.length ? gs.map((g, i) => <Fragment key={g}>{i > 0 && " "}{tone(g)}</Fragment>) : <span className="muted">–</span>;

/** The natal wheel's slots with the transit bodies of the same star or sign added as `over`. */
function mix<S extends { bodies: string[] }>(ns: S[], ts: S[] | undefined, key: (s: S) => string, view: View): (S & { over?: string[] })[] {
  const m = new Map((ts ?? []).map((s) => [key(s), s.bodies]));
  return ns.map((s) => ({ ...s, bodies: view === "transit" ? [] : s.bodies, over: view === "natal" ? undefined : m.get(key(s)) ?? [] }));
}

/** A chakra wheel and, in Starlight, its controls, the picked slot's card and its reading beside it. ``part`` (Starlight's Transits): just
 *  the drawing (the left half) or just what goes beside it (the box under the cast form), the natal chart against the transit cast there,
 *  its moment the cast form's; the two parts share their picks through the kept keys. */
function Wheels({ tab, part }: { tab: string; part?: "draw" | "side" }) {
  const { birth, mode, say } = useChart();
  const natal = useChart(transitBase);     // the chart in use as the natal one; a transit's, the chart it is read against
  const embed = !!part;
  const star = useChart((s) => s.display.layout === "starlight");
  const [options, setOptions] = useKept<ChakraOptions>("chakras.options", { show: ["planets"], planet_varga: 1 });
  const natalKey = JSON.stringify(natal);
  const [keptAt, setKeptAt] = useKept<{ of: string; at: Birth } | null>("chakras.at", null);   // "View transits on this date", for this natal chart only
  const at = keptAt?.of === natalKey ? keptAt.at : null;
  const setAt = (b: Birth | null) => setKeptAt(b && { of: natalKey, at: b });
  const [view, setView] = useKept<View>("chakras.view", "both");
  const [unit, setUnit] = useKept("chakras.step", 1);
  const [sel, setSel] = useKept<string | null>(`chakras.sel.${tab}`, null);
  const [form, setForm] = useKept<Form>(`chakras.form.${tab}`, null);
  const [markedList, setMarkedList] = useKept<string[]>("chakras.sbc.marked", []);
  const [shadedList, setShadedList] = useKept<string[]>("chakras.sbc.shaded", []);
  const [graha, setGraha] = useKept<SbcGraha | null>("chakras.sbc.graha", null);     // Starlight: the graha clicked in the picked box
  const [sound, setSound] = useKept("chakras.sbc.sound", "");
  const marked = new Set(markedList), shaded = new Set(shadedList);
  const setMarked = (s: Set<string>) => setMarkedList([...s]);
  const setShaded = (s: Set<string>) => setShadedList([...s]);
  const { open, node } = useMenu();
  const chart = embed ? natal! : star ? birth! : at ?? birth!;     // Starlight keeps the chart and lays the transits over it
  const asked: ChakraOptions = { ...options, chart_kind: embed ? null : mode?.event?.kind ?? null };
  const q = useQuery({ queryKey: ["chakras", natal, chart, asked], queryFn: () => api.chakras(natal!, chart, asked), placeholderData: (p) => p });
  const now = useQuery({ queryKey: ["chakras-now", natal], queryFn: async () => (await api.transitMode(natal!, nowMoment())).birth, enabled: star && !at && !embed, staleTime: Infinity });
  const tb = embed ? birth! : at ?? now.data;
  const v: View = star ? view : "natal";
  const tq = useQuery({ queryKey: ["chakras", natal, tb, asked], queryFn: () => api.chakras(natal!, tb!, asked), enabled: star && !!tb && v !== "natal", placeholderData: (p) => p });
  const stepper = useMutation({ mutationFn: (dir: number) => api.step(tb!, dir * STEPS[unit][1], dir * STEPS[unit][2]), onSuccess: (r) => setAt(r.birth) });
  const show = options.show ?? ["planets"];
  const toggle = (k: string) => setOptions({ ...options, show: show.includes(k) ? show.filter((x) => x !== k) : [...show, k] });
  const special = async (o: Parameters<typeof api.specialPoint>[1], add = true) => {
    try {
      const r = await api.specialPoint(natal!, o);
      const boxes = boxesOf(r);
      setMarked(new Set([...(add ? marked : []), ...boxes]));
      if (r.text) say("Special tithi", r.text);
    } catch (e) { say("Special point", (e as Error).message); }
  };
  const starBoxes = useMemo(() => {
    const out = new Map<string, string>();
    SBC.forEach((row, r) => row.forEach((cell, c) => { if (typeof cell === "string" && cell.startsWith("*")) out.set(cell.slice(1), `${r}-${c}`); }));
    return out;
  }, []);
  const wheelMenu: MenuEntry[] = [
    ...BODY_SETS.map(([k, n]) => ({ label: n, checked: show.includes(k), onClick: () => toggle(k) })),
    "-",
    { label: "Base graha and division", onClick: () => setForm({ kind: "base" }) },
    { label: "Divisional chart to be used for grahas", onClick: () => setForm({ kind: "varga" }) },
    { label: "Fully customize base nakshatra", onClick: () => setForm({ kind: "star" }) },
  ];
  const kotaMenu: MenuEntry[] = [
    { label: "View transits on this date", onClick: () => setForm({ kind: "date" }) },
    { label: "Back to the current chart", disabled: !at, onClick: () => setAt(null) },
    { label: "Change the base nakshatra", onClick: () => setForm({ kind: "star" }) },
  ];
  const sbcMenu = (r: number, c: number, star: string | null): MenuEntry[] => {
    const sb = q.data?.sarvatobhadra;
    const key = `${r}-${c}`;
    const fromPlanets = (list: Record<string, string[]> | undefined) => {   // the boxes of the planets that kick or aspect this star
      if (!star || !list || !sb) return new Set<string>();
      const who = list[star] ?? [];
      return new Set(Object.entries(sb.stars).filter(([, bodies]) => bodies.some((b) => who.includes(b))).map(([s]) => starBoxes.get(s)!).filter(Boolean));
    };
    return [
      { label: "Highlight vedhas, aspects and lattas on this star (if any)", disabled: !star, onClick: () => setShaded(new Set([...vedhas(r, c), ...fromPlanets(sb?.latta), ...fromPlanets(sb?.aspect)])) },
      { label: "Highlight aspects (vedhas) FROM this star", onClick: () => setShaded(vedhas(r, c)) },
      { label: "Highlight aspects (vedhas) ON this box", onClick: () => setShaded(vedhas(r, c)) },
      { label: "Highlight fixed graha drishti on this star (if any)", disabled: !star, onClick: () => setShaded(fromPlanets(sb?.aspect)) },
      { label: "Highlight lattas on this star (if any)", disabled: !star, onClick: () => setShaded(fromPlanets(sb?.latta)) },
      { label: "Clear the highlights", disabled: !shaded.size, onClick: () => setShaded(new Set()) },
      "-",
      { label: "Set a special nakshatra (natal) as a special point", onClick: () => setForm({ kind: "special_nakshatra" }) },
      { label: "Set a natal tara as a special point (nava-tara scheme)", onClick: () => setForm({ kind: "tara" }) },
      { label: "Set a special tithi (natal) as a special point", onClick: () => setForm({ kind: "tithi" }) },
      { label: "Set a bhava in natal chart as a special point", onClick: () => setForm({ kind: "house" }) },
      { label: "Set the natal nakshatra of a graha as a special point", onClick: () => setForm({ kind: "planet" }) },
      { label: "Set this box as a special point", onClick: () => setMarked(new Set([...marked, key])) },
      { label: "Set a special nakshatra from here as a special point", disabled: !star, onClick: () => setForm({ kind: "from_special", star: star ?? undefined }) },
      { label: "Set a tara from here as a special point", disabled: !star, onClick: () => setForm({ kind: "from_tara", star: star ?? undefined }) },
      { label: "Reset this special point box", disabled: !marked.has(key), onClick: () => { const m = new Set(marked); m.delete(key); setMarked(m); } },
      { label: "Reset all special points", disabled: !marked.size, onClick: () => setMarked(new Set()) },
      "-",
      { label: "Divisional chart used for transit positions", onClick: () => setForm({ kind: "varga" }) },
      { label: "View transits on this date", onClick: () => setForm({ kind: "date" }) },
      { label: "Back to the current chart", disabled: !at, onClick: () => setAt(null) },
    ];
  };
  const close = () => setForm(null);
  // in Transits the cast form sets the moment: no date of the wheel's own
  const undated = (m: MenuEntry[]) => (embed ? m.filter((x) => typeof x === "string" || !DATED.has(x.label)) : m);
  const note = tab === "kota" ? "Natal Moonstar is taken as the base." : "Star of Sun is taken as the base in natal charts and the star of lagna in Tajaka/TP charts. It is placed in the eastern corner.";
  const pick = (k: string) => setSel(sel === k ? null : k);
  // a box picked shows its own lines (the Sarvatobhadra below works them out); picked again, nothing. A graha clicked in a box picks the box
  // and lights that graha's main line alone; clicked again, the box's every graha
  const sbcBox = (key: string) => { pick(key); setShaded(new Set()); setGraha(null); };
  const sbcGraha = (p: SbcGraha) => { const same = graha?.key === p.key && graha.g === p.g && graha.transit === p.transit; setSel(p.key); setShaded(new Set()); setGraha(same ? null : p); };

  /** The drawing, and in Starlight what goes beside it: the picked slot's card and the chakra's reading. */
  const build = (w: Chakras, t: Chakras | undefined): { draw: ReactNode; card?: { title: string; lines: [string, ReactNode][]; tools?: ReactNode }; reading?: { title: string; head?: ReactNode; cols: string[]; rows: Row[]; foot?: ReactNode; onRow?: (k: string) => void; picked?: string } } => {
    const layer = (s: { bodies: string[]; over?: string[] }) => grahas(v === "natal" ? s.bodies : s.over ?? []);
    const whose = v === "natal" ? "Natal" : "Transit";
    const moon = w.sarvatobhadra.refs.moon_star;
    const starCard = (s: string, bodies: string[], over: string[] | undefined, extra: [string, ReactNode][] = []) =>
      ({ title: starName(s), lines: [...(v !== "transit" ? [["Natal", list(bodies)] as [string, ReactNode]] : []), ...(over ? [["Transit", list(over)] as [string, ReactNode]] : []),
        ["Tara from natal Moon", ABBR28.includes(s) ? taraOf(s, moon) : "–"] as [string, ReactNode], ...extra] });
    const picks = (extra: Partial<Picks> = {}): Picks | undefined => star ? { sel, onPick: pick, ...extra } : undefined;
    const rowOn = (key: string, cells: ReactNode[]): Row => ({ key, cells });

    const starSlots = (order: string[], merged = false) => {      // a star's bodies by name (Abhijit's in Uttarashadha on the 27-star rounds)
      const of = (c: Chakras | undefined) => order.map((x) => ({ star: x, bodies: [...(c?.sarvatobhadra.stars[x] ?? []), ...(merged && x === "USha" ? c?.sarvatobhadra.stars.Abhi ?? [] : [])] }));
      return mix(of(w), t && of(t), (x) => x.star, v);
    };
    if (tab === "tara") {
      const from = star27(moon), slots = starSlots(ABBR27.map((_, i) => ABBR27[(from + i) % 27]), true);
      const s = slots.find((x) => x.star === sel);
      return {
        draw: <TaraChakra slots={slots} picks={picks({ here: new Set([slots[0].star]) })} />,
        card: s && starCard(s.star, s.bodies, s.over, [["Round", String(Math.floor(slots.indexOf(s) / 9) + 1)]]),
        reading: { title: `${whose} grahas by tara`, head: <p className="chakra-lead">Counted from your Moon's star, <strong>{starName(ABBR27[from])}</strong>.</p>,
          cols: ["", "Star", "Tara", ""],
          rows: GRAHAS.flatMap((g) => { const i = slots.findIndex((x) => layer(x).includes(g)); return i < 0 ? [] : [rowOn(slots[i].star, [tone(g), starName(slots[i].star), TARA_NAMES[i % 9], TARA_KIND[i % 9]])]; }),
          foot: <p className="muted hint">Grahas, the Moon most of all, in Vipat, Pratyak and Naidhana hurt; in Sampat, Kshema, Sadhana, Mitra and Parama Mitra they help.</p> },
      };
    }
    if (tab === "shalaka") {
      const slots = starSlots(SHALAKA), s = slots.find((x) => x.star === sel);
      const focus = s?.star ?? moon;
      const rows = GRAHAS.flatMap((g) => {
        const x = slots.find((y) => layer(y).includes(g));
        if (!x) return [];
        const hit = shalakaPartner(x.star);
        return [rowOn(x.star, [tone(g), starName(x.star), starName(hit), hit === moon ? "Your Moon's star" : x.star === moon ? "On your Moon's star" : ""])];
      });
      return {
        draw: <SaptaShalaka slots={slots} focus={focus} picks={picks({ here: new Set([moon]), lit: new Set([shalakaPartner(focus)]) })} />,
        card: s && starCard(s.star, s.bodies, s.over, [["Pierces", starName(shalakaPartner(s.star))]]),
        reading: { title: `${whose} vedhas on the lines`, head: <p className="chakra-lead">Your Moon's star: <strong>{starName(moon)}</strong></p>,
          cols: ["", "Star", "Pierces", ""], rows,
          foot: <p className="muted hint">Each star pierces the one at the other end of its line. Malefics piercing your Moon's star hurt; benefics help.</p> },
      };
    }
    if (tab === "avakahada") {
      const n = w.avakahada.native, padas = mix(w.avakahada.padas.map((b, i) => ({ star: String(i), bodies: b })), t?.avakahada.padas.map((b, i) => ({ star: String(i), bodies: b })), (x) => x.star, v);
      const k = sel !== null && /^\d+$/.test(sel) ? Number(sel) : null, s = k !== null ? padas[k] : undefined;
      const padaName = (i: number) => `${STARS_27[Math.floor(i / 4)]} pada ${i % 4 + 1}`;
      const rasi = (i: number) => SIGN_NAMES[Math.floor(i / 9)];
      const facts: [string, string][] = [["Nakshatra", padaName(n.pada)], ["Name syllable", SYLLABLES[n.pada]], ["Rasi", rasi(n.pada)], ["Rasi lord", n.rasi_lord], ["Nakshatra lord", n.nak_lord],
        ["Varna", n.varna], ["Vashya", n.vashya], ["Yoni", n.yoni], ["Gana", n.gana], ["Nadi", n.nadi], ["Tatva", n.tatva]];
      return {
        draw: <Avakahada padas={padas} names={STARS_27} picks={picks({ here: new Set([String(n.pada)]) })} />,
        card: s && k !== null ? { title: padaName(k), lines: [["Syllable", SYLLABLES[k]], ["Rasi", rasi(k)], ...(v !== "transit" ? [["Natal", list(s.bodies)] as [string, ReactNode]] : []),
          ...(s.over ? [["Transit", list(s.over)] as [string, ReactNode]] : []), ["Tara from natal Moon", taraOf(ABBR27[Math.floor(k / 4)], moon)]] } : undefined,
        reading: { title: "Your Moon's avakahada", cols: ["", "Natal"], picked: "",
          rows: facts.map(([a, b], i) => rowOn(`a${i}`, [a, b])), onRow: () => setSel(String(n.pada)),
          foot: <p className="muted hint">A name for the native starts with the syllable of the Moon's pada. Click a pada to see it.</p> },
      };
    }
    if (tab === "ghataka") {
      const own = w.ghataka.moon_sign, d = (v === "natal" ? w : t ?? w).ghataka.day, hits = ghatakaHits(own, d);
      const have = [MONTHS[GHATAKA.month[own]], TITHI_GROUPS[GHATAKA.tithi[own]], WEEKDAY_NAMES[GHATAKA.weekday[own]], STARS_27[GHATAKA.star[own]], SIGN_NAMES[GHATAKA.sign[own]]];
      const now = [d.month_name, d.tithi_name, WEEKDAY_NAMES[d.weekday], STARS_27[d.nakshatra], SIGN_NAMES[d.moon_sign]];
      const count = hits.filter(Boolean).length;
      return {
        draw: <Ghataka stars={STARS_27} day={d} moonSign={own} picks={picks({ here: new Set([String(own)]) })} />,
        reading: { title: `Ghataka for your Moon in ${SIGN_NAMES[own]}`, picked: "", head: <p className="chakra-lead">{v === "natal" ? "The birth" : "The transit"} day against your ghatakas.</p>,
          cols: ["", "Ghataka", v === "natal" ? "Birth" : "Transit", ""],
          rows: ["Month", "Tithi", "Weekday", "Moon's star", "Moon in"].map((f, i) => rowOn(`g${i}`, [f, have[i], now[i], hits[i] ? <span className="malefic">Ghataka</span> : ""])),
          onRow: () => setSel(String(own)),
          foot: <p className="muted hint">{count ? `${count} of 5 meet. ` : "None meet. "}A ghataka day, star or Moon sign is avoided for new work, travel, lawsuits and surgery; the more meet, the worse.</p> },
      };
    }
    if (tab === "sbc") {
      const s = w.sarvatobhadra, over = v === "natal" ? undefined : t?.sarvatobhadra.stars;
      const bodies = v === "transit" ? { ...s, stars: {} } : s;
      const refs = s.refs;
      const boxOf = (test: (cell: string | [string, string]) => boolean) => { for (let r = 0; r < 9; r++) for (let c = 0; c < 9; c++) if (test(SBC[r][c])) return `${r}-${c}`; return ""; };
      const textOf = (key: string) => { const [r, c] = key.split("-").map(Number); const cell = SBC[r][c]; return typeof cell === "string" ? (cell.startsWith("*") ? starName(cell.slice(1)) : cell) : cell.join(" · "); };
      const refRows: [string, string][] = [["Janma nakshatra", starBoxes.get(refs.moon_star)!], ["Lagna rasi", boxOf((c) => c === refs.lagna_sign)],
        ["Janma tithi", boxOf((c) => typeof c !== "string" && c[0] === refs.tithi_group)], ["Janma vaara", boxOf((c) => typeof c !== "string" && c[1].split(" ").includes(refs.weekday))],
        ...(sound ? [["Name sound", boxOf((c) => c === sound)] as [string, string]] : []), ...markedList.map((k) => ["Special point", k] as [string, string])];
      const src = v === "natal" ? s.stars : t?.sarvatobhadra.stars ?? {};
      const at: [string, string][] = Object.entries(src).flatMap(([st, bs]) => grahas(bs).map((g) => [g, starBoxes.get(st)!] as [string, string]));
      const hits = (key: string) => at.filter(([, b]) => b === key || vedhas(...(b.split("-").map(Number) as [number, number])).has(key)).map(([g]) => g);
      const shadeOf = (key: string) => new Set([key, ...at.filter(([g]) => hits(key).includes(g)).flatMap(([, b]) => [b, ...vedhas(...(b.split("-").map(Number) as [number, number]))])]);
      const key = sel && /^\d-\d$/.test(sel) ? sel : null;     // nothing lit until a box is picked
      const [kr, kc] = key ? key.split("-").map(Number) : [-1, -1];
      const cellStar = (() => { const x = key ? SBC[kr][kc] : null; return typeof x === "string" && x.startsWith("*") ? x.slice(1) : null; })();
      // no highlight asked for: the picked box's vedha lines grey, and of each graha shown in it (natal and transit) the one its motion makes
      // its main vedha light purple (retrograde the right, fast the left, at its usual pace the front); a graha clicked in the box, its alone
      const lines = key ? vedhaLines(kr, kc) : null;
      const inBox = cellStar ? [...(v !== "transit" ? grahas(s.stars[cellStar] ?? []).map((g) => ({ g, transit: false, m: w.motion?.[g] })) : []),
        ...(v !== "natal" && t ? grahas(t.sarvatobhadra.stars[cellStar] ?? []).map((g) => ({ g, transit: true, m: t.motion?.[g] })) : [])] : [];
      const chosen = graha?.key === key ? inBox.filter((x) => x.g === graha.g && x.transit === graha.transit) : [];
      const lit = chosen.length ? chosen : inBox;
      const main = !shaded.size && lines ? new Set(lit.flatMap((x) => (x.m ? [...lines[SIDE[x.m]]] : []))) : new Set<string>();
      const shade = shaded.size ? shaded : key ? new Set([...vedhas(kr, kc)].filter((x) => !main.has(x))) : new Set<string>();
      const mainLine: [string, ReactNode][] = inBox.length ? [["Main vedha", <span className="sbc-main">{inBox.map((x) => (
        <span key={`${x.transit}${x.g}`} className={chosen.includes(x) || !chosen.length ? "on" : undefined}>{tone(x.g)}{v === "both" && <small>{x.transit ? " transit" : " natal"}</small>} {x.m ? `${MOTION[x.m]}: ${SIDE[x.m]}` : "–"}</span>))}
        <small className="muted">{inBox.length > 1 ? "Click a graha in the box to light its line alone." : "Its line is light purple, the other two grey."}</small></span>]] : [];
      const tools = ([[0, "Vedhas, drishti and lattas"], [1, "Vedhas"], [3, "Graha drishti"], [4, "Lattas"], [5, "Clear"], [12, "Make it a special point"]] as const);
      const menuOf = sbcMenu(kr, kc, cellStar);
      const buttons = <div className="chakra-tools">{tools.map(([i, label]) => { const m = menuOf[i] as Exclude<MenuEntry, string>; return <button key={i} disabled={m.disabled} onClick={m.onClick}>{label}</button>; })}</div>;
      return {
        draw: <Sarvatobhadra s={bodies} over={over} marked={marked} shaded={star ? shade : shaded} main={star ? main : undefined} table={!star} picks={picks({ sel: key, onPick: sbcBox })}
          graha={graha} onGraha={star ? sbcGraha : undefined} onBox={(e, r, c, st) => open(e, undated(sbcMenu(r, c, st)), "Sarvatobhadra menu")} />,
        card: key ? { ...(cellStar ? starCard(cellStar, s.stars[cellStar] ?? [], over?.[cellStar], [["Vedha from", list(hits(key))], ...mainLine]) : { title: textOf(key), lines: [["Vedha from", list(hits(key))] as [string, ReactNode]] }), tools: buttons } : undefined,
        reading: {
          picked: key ?? "",
          title: `${whose} vedhas on your natal points`,
          head: <div className="chakra-tools">
            <label className="row">Name sound<select value={sound} onChange={(e) => setSound(e.target.value)}><option value="">–</option>{SBC_SOUNDS.map((x) => <option key={x}>{x}</option>)}</select></label>
            <button onClick={() => setForm({ kind: "special_nakshatra" })}>+ Special nakshatra</button>
            <button onClick={() => setForm({ kind: "tara" })}>+ Tara</button>
            <button onClick={() => setForm({ kind: "tithi" })}>+ Special tithi</button>
            <button onClick={() => setForm({ kind: "house" })}>+ Bhava</button>
            <button onClick={() => setForm({ kind: "planet" })}>+ Graha's star</button>
            <button onClick={() => { setMarked(new Set()); setShaded(new Set()); setSel(null); setGraha(null); }} disabled={!marked.size && !shaded.size && !key}>Reset</button>
          </div>,
          cols: ["Natal point", "Box", "Benefics", "Malefics"],
          rows: refRows.filter(([, k]) => k).map(([label, k], i) => { const h = hits(k); return rowOn(`${i}-${k}`, [label, textOf(k), list(h.filter((g) => BENEFICS.has(g))), list(h.filter((g) => !BENEFICS.has(g)))]); }),
          foot: <p className="muted hint">Click a row to light the lines that reach it. Vedhas by benefics help, by malefics hurt; two or three points hit together is what counts.</p>,
          // shortcut: the help's extra vowel and consonant pairings (a/aa, b/v ...) are not counted; add them to hits() if wanted
          onRow: (k: string) => { const box = k.split("-").slice(1).join("-"); setSel(box); setShaded(shadeOf(box)); },
        },
      };
    }
    if (tab === "kota") {
      const slots = mix(w.kota.slots, t?.kota.slots, (s) => s.star, v);
      const retro = new Set((v === "natal" ? w : t ?? w).retro);
      const rows = GRAHAS.flatMap((g) => {
        const i = slots.findIndex((s) => layer(s).includes(g));
        if (i < 0) return [];
        const inward = (i % 7 < 4) !== retro.has(g);
        return [rowOn(slots[i].star, [tone(g), starName(slots[i].star), KOTA_ZONES[kotaZone(i)], inward ? "Entering" : "Leaving"])];
      });
      const attack = GRAHAS.filter((g) => !BENEFICS.has(g)).filter((g) => { const i = slots.findIndex((s) => layer(s).includes(g)); return i >= 0 && (kotaZone(i) === 3 || (kotaZone(i) >= 1 && (i % 7 < 4) !== retro.has(g))); });
      const s = slots.find((x) => x.star === sel);
      return {
        draw: <Kota k={w.kota} slots={slots} picks={picks({ here: new Set([slots[0].star]) })} />,
        card: s && starCard(s.star, s.bodies, s.over, [["Wall", KOTA_ZONES[kotaZone(slots.indexOf(s))]]]),
        reading: { title: `${whose} grahas in the fort`, head: <p className="chakra-lead">Kota Swami <strong>{w.kota.swami}</strong> · Kota Pala <strong>{w.kota.pala}</strong></p>,
          cols: ["", "Star", "Wall", "Moving"], rows,
          foot: <p className="chakra-lead">{attack.length ? <>Malefics pressing on the fort: {list(attack)}</> : "No malefic is inside or entering the fort."}</p> },
      };
    }
    if (tab === "sudarsana") {
      const rings = w.sudarsana.map((r, i) => ({ ...r, sectors: mix(r.sectors, t?.sudarsana[i].sectors, (s) => s.sign, v) }));
      const tb2 = tb ?? birth!;
      const age = tb2.year - natal!.year - (tb2.month * 100 + tb2.day < natal!.month * 100 + natal!.day ? 1 : 0);   // shortcut: by the calendar birthday, not the solar return
      const yearSector = String((3 - (age % 12 + 1) + 12) % 12);
      const k = sel !== null && /^\d+$/.test(sel) ? Number(sel) : null;
      const houseOf = (k: number) => (14 - k) % 12 + 1;
      return {
        draw: <Sudarsana rings={rings} picks={picks({ here: new Set([yearSector]) })} />,
        card: k !== null ? { title: `Bhava ${houseOf(k)}`, lines: rings.map((r) => [`From ${r.from}`, <>{SIGN_NAMES[SIGNS.indexOf(r.sectors[k].sign)]} {list(layer(r.sectors[k]))}</>] as [string, ReactNode]) } : undefined,
        reading: { title: `${whose} bhavas from Lagna, Moon and Sun`, head: <p className="chakra-lead">Sudarsana year {age + 1}: bhava <strong>{age % 12 + 1}</strong> from each, highlighted.</p>,
          cols: ["Bhava", "Lagna", "Moon", "Sun"],
          rows: Array.from({ length: 12 }, (_, h) => { const kk = (3 - (h + 1) + 12) % 12; return rowOn(String(kk), [String(h + 1), ...rings.map((r) => <>{r.sectors[kk].sign} {list(layer(r.sectors[kk]))}</>)]); }) },
      };
    }
    if (tab === "tripataki") {
      const slots = mix(w.tripataki, t?.tripataki, (s) => s.sign, v);
      const moonSign = w.sudarsana[1].sectors[2].sign, mk = slots.findIndex((s) => s.sign === moonSign);
      const reach = [mk, ...triVedhas(mk)];
      const on = reach.flatMap((i) => layer(slots[i]).map((g) => [g, slots[i].sign] as [string, string]));
      const si = slots.findIndex((s) => s.sign === sel);
      const s = slots[si];
      return {
        draw: <Tripataki slots={slots} picks={picks({ here: new Set([moonSign]), lit: si >= 0 ? new Set([...triVedhas(si)].map((i) => slots[i].sign)) : undefined })} />,
        card: s && { title: SIGN_NAMES[SIGNS.indexOf(s.sign)], lines: [...(v !== "transit" ? [["Natal", list(s.bodies)] as [string, ReactNode]] : []), ...(s.over ? [["Transit", list(s.over)] as [string, ReactNode]] : []),
          ["Vedha with", [...triVedhas(si)].map((i) => slots[i].sign).join(" ")]] },
        reading: { title: `${whose} vedhas on the natal Moon (${moonSign})`, cols: ["", "From", "Effect"],
          rows: on.map(([g, sign]) => rowOn(sign, [tone(g), sign === moonSign ? "On the Moon" : sign, BENEFICS.has(g) ? "Helps" : "Hurts"])),
          foot: <p className="muted hint">Click a sign to light the lines from it. The Moon's sign is highlighted.</p> },
      };
    }
    if (tab === "kurma") {
      const regions = mix(w.kurma.regions, t?.kurma.regions, (g) => g.dir, v);
      const own = w.kurma.regions[w.kurma.janma].dir;
      const g = regions.find((x) => x.dir === sel);
      return {
        draw: <Kurma regions={regions} picks={picks({ here: new Set([own]) })} />,
        card: g && { title: KURMA_NAMES[g.dir], lines: [["Stars", g.stars.map(starName).join(", ")], ...(v !== "transit" ? [["Natal", list(g.bodies)] as [string, ReactNode]] : []), ...(g.over ? [["Transit", list(g.over)] as [string, ReactNode]] : [])] },
        reading: { title: `${whose} grahas over the nine regions`, head: <p className="chakra-lead">Your region (janma nakshatra): <strong>{KURMA_NAMES[own]}</strong></p>,
          cols: ["Region", "Benefics", "Malefics"],
          rows: regions.map((x) => rowOn(x.dir, [x.dir === own ? <strong>{KURMA_NAMES[x.dir]}</strong> : KURMA_NAMES[x.dir], list(layer(x).filter((y) => BENEFICS.has(y))), list(layer(x).filter((y) => !BENEFICS.has(y)))])),
          foot: <p className="muted hint">Malefics over a region trouble the land and people there; over your own region, you.</p> },
      };
    }
    // the star wheels: Kalachakra, the Kalanalas and Shoola
    const [wheel, raw, rawT, title] = tab === "kala" ? [KALA, w.kalachakra, t?.kalachakra, "Kalachakra"] as const : tab === "surya" ? [SURYA, w.surya_kalanala, t?.surya_kalanala, "Surya Kalanala"] as const
      : tab === "chandra" ? [CHANDRA, w.chandra_kalanala, t?.chandra_kalanala, "Chandra Kalanala"] as const : [SHOOLA, w.shoola, t?.shoola, "Shoola"] as const;
    const slots = mix(raw, rawT, (s) => s.star, v);
    const si = slots.findIndex((s) => s.star === sel), s = slots[si];
    if (tab === "kala") {
      const dir = si >= 0 ? kalaDir(si) : -1;
      return {
        draw: <StarWheel title={title} wheel={wheel} slots={slots} picks={picks({ lit: new Set(slots.filter((_, i) => kalaDir(i) === dir).map((x) => x.star)) })} />,
        card: s && starCard(s.star, s.bodies, s.over, [["Direction", DIRECTIONS[dir]]]),
        reading: { title: `${whose} grahas by direction`, cols: ["", "Star", "Direction"],
          rows: GRAHAS.flatMap((g) => { const i = slots.findIndex((x) => layer(x).includes(g)); return i < 0 ? [] : [rowOn(slots[i].star, [tone(g), starName(slots[i].star), DIRECTIONS[kalaDir(i)]])]; }),
          foot: <p className="muted hint">Click a star to light its whole direction.</p> },
      };
    }
    const tips = new Set(TIPS[tab].map((i) => slots[i].star));
    const onTips = slots.filter((x) => tips.has(x.star)).flatMap((x) => layer(x).map((g) => [g, x.star] as [string, string]));
    return {
      draw: <StarWheel title={title} wheel={wheel} slots={slots} picks={picks({ tips })} />,
      card: s && starCard(s.star, s.bodies, s.over, [["On a trident point", tips.has(s.star) ? "Yes" : "No"]]),
      reading: { title: `${whose} grahas on the trident points`, cols: ["", "Star", "Effect"],
        rows: onTips.map(([g, st]) => rowOn(st, [tone(g), starName(st), BENEFICS.has(g) ? "Softens" : "Danger"])),
        foot: <p className="muted hint">{onTips.length ? "Malefics on the trident's points bring danger in the matters of this wheel; benefics soften it." : "No graha sits on a trident point."} Click a row to find its star.</p> },
    };
  };

  // the textbook chakras turn from the natal Moon alone: their menu has no base to change
  const menu = (e: React.MouseEvent) => { e.preventDefault(); open(e, undated(tab === "kota" ? kotaMenu : tab === "sbc" ? sbcMenu(-1, -1, null).slice(7) : STARLIGHT_ONLY.has(tab) ? [...wheelMenu.slice(0, BODY_SETS.length + 1), wheelMenu[BODY_SETS.length + 2]] : wheelMenu), "Chakra menu"); };
  const dialogs = <>
    {node}
    {form?.kind === "base" && <BaseDialog options={options} onOk={setOptions} onClose={close} />}
    {form?.kind === "star" && <StarDialog options={options} note={note} onOk={setOptions} onClose={close} />}
    {form?.kind === "date" && !embed && <DateDialog onOk={setAt} onClose={close} />}
    {form?.kind === "varga" && pickList("Select a divisional chart", DIVISIONS.map((d) => (d === 1 ? "Rasi" : `D-${d}`)), false, (i) => setOptions({ ...options, planet_varga: DIVISIONS[i] }), close)}
    {form?.kind === "tara" && pickList("Select a tara under nava-tara scheme", TARAS, true, (i, d) => special({ kind: "tara", value: i, division: d }), close)}
    {form?.kind === "special_nakshatra" && pickList("Select a special nakshatra", SPECIAL_NAKS, true, (i, d) => special({ kind: "special_nakshatra", value: i, division: d }), close)}
    {form?.kind === "tithi" && pickList("Select a special tithi", SPECIAL_TITHIS, true, (i, d) => special({ kind: "tithi", value: i, division: d }), close)}
    {form?.kind === "planet" && pickList("Select a graha", HOUSE_POINTS, true, (i, d) => special({ kind: "planet", point: HOUSE_POINTS[i], division: d }), close)}
    {form?.kind === "from_tara" && pickList("Select a tara under nava-tara scheme", TARAS, false, (i) => special({ kind: "tara", value: i, star: form.star }), close)}
    {form?.kind === "from_special" && pickList("Select a special nakshatra", SPECIAL_NAKS, false, (i) => special({ kind: "special_nakshatra", value: i, star: form.star }), close)}
    {form?.kind === "house" && <HouseDialog onOk={(v, p, d) => special({ kind: "house", value: v, point: p, division: d })} onClose={close} />}
  </>;

  if (star) {
    const based = options.base_point !== null && options.base_point !== undefined || options.base_star !== null && options.base_star !== undefined;
    return (
      <div className={part ? `chakra-screen chakra-only-${part}` : "chakra-screen"} style={{ "--ar": ASPECT[tab] ?? 1 } as React.CSSProperties} onContextMenu={menu}>
        <Loaded q={q}>{(w) => {
          const b = build(w, v === "natal" ? undefined : tq.data);
          const r = b.reading;
          return <>
            {part !== "side" && <div className="chakra-draw">{b.draw}</div>}
            {part !== "draw" && <aside className="chakra-side">
              <div className="chakra-col">
              <section className="pane chakra-box">
                <div className="seg chakra-views" role="tablist" aria-label="Positions shown">
                  {VIEWS.map((x) => <button key={x.id} role="tab" aria-selected={view === x.id} onClick={() => setView(x.id)}>{x.name}</button>)}
                </div>
                {!embed && <><div className="chakra-when">
                  <button aria-label="Back" onClick={() => stepper.mutate(-1)} disabled={!tb || stepper.isPending}><Icon name="prev" /></button>
                  <select value={unit} onChange={(e) => setUnit(Number(e.target.value))} aria-label="Step by">{STEPS.map(([n], i) => <option key={n} value={i}>{n}</option>)}</select>
                  <button aria-label="On" onClick={() => stepper.mutate(1)} disabled={!tb || stepper.isPending}><Icon name="next" /></button>
                  <button className="now-btn" onClick={() => { setAt(null); now.refetch(); }} disabled={!at} aria-label="Now" data-tip="Back to now"><Icon name="now" /></button>
                  <button onClick={() => setForm({ kind: "date" })}>Date…</button>
                </div>
                <p className="chakra-lead">Transits {tb ? whenOf(tb) : "…"}{at ? "" : " (now)"}</p></>}
                <div className="chakra-sets">{BODY_SETS.map(([k, n]) => <label key={k} className="check"><input type="checkbox" checked={show.includes(k)} onChange={() => toggle(k)} /> {n.replace("Show ", "")}</label>)}</div>
                <div className="chakra-tools">
                  <label className="row">Grahas in<DivisionSelect value={options.planet_varga ?? 1} onChange={(d) => setOptions({ ...options, planet_varga: d })} /></label>
                  {ROTATING.has(tab) && <>
                    {tab !== "kota" && <button onClick={() => setForm({ kind: "base" })}>Base graha</button>}
                    <button onClick={() => setForm({ kind: "star" })}>Base star</button>
                    {based && <button onClick={() => setOptions({ ...options, base_point: null, base_star: null })}>Default base</button>}
                  </>}
                </div>
              </section>
              {b.card && <section className="pane chakra-box chakra-card">
                <h3>{b.card.title}</h3>
                <dl>{b.card.lines.map(([k, x]) => <Fragment key={k}><dt>{k}</dt><dd>{x}</dd></Fragment>)}</dl>
                {b.card.tools}
              </section>}
              </div>
              {r && <section className="pane chakra-box chakra-reading">
                <h3>{r.title}</h3>
                {r.head}
                <table className="points"><thead><tr>{r.cols.map((c, i) => <th key={i}>{c}</th>)}</tr></thead>
                  <tbody>{r.rows.length ? r.rows.map((row, i) => <tr key={i} className={row.key === (r.picked ?? sel) || r.onRow && row.key.endsWith(`-${r.picked ?? sel}`) ? "picked" : ""} onClick={() => (r.onRow ? r.onRow(row.key) : setSel(row.key))}>{row.cells.map((c, j) => <td key={j}>{supOrd(c)}</td>)}</tr>)
                    : <tr><td colSpan={r.cols.length} className="muted">None</td></tr>}</tbody>
                </table>
                {r.foot}
              </section>}
            </aside>}
          </>;
        }}</Loaded>
        {part === "draw" ? node : dialogs}
      </div>
    );
  }
  return (
    <div className="wheels" onContextMenu={menu}>
      {tab === "kota" ? (
        <div className="chakra-tools pad">
          <button onClick={() => setForm({ kind: "date" })}>View transits on a date</button>
          {at && <button onClick={() => setAt(null)}>Back to the current chart</button>}
          <button onClick={() => setForm({ kind: "star" })}>Change the base nakshatra</button>
        </div>
      ) : tab === "sbc" ? (
        <div className="chakra-tools pad">
          <span className="muted">Right-click a box for vedhas and special points.</span>
          <label className="row">Divisional chart for positions<DivisionSelect value={options.planet_varga ?? 1} onChange={(d) => setOptions({ ...options, planet_varga: d })} /></label>
          <button onClick={() => setForm({ kind: "date" })}>View transits on a date</button>
          {at && <button onClick={() => setAt(null)}>Back to the current chart</button>}
          <button onClick={() => { setMarked(new Set()); setShaded(new Set()); }} disabled={!marked.size && !shaded.size}>Reset all</button>
        </div>
      ) : (
        <div className="chakra-tools pad">
          {BODY_SETS.map(([k, n]) => <label key={k} className="check"><input type="checkbox" checked={show.includes(k)} onChange={() => toggle(k)} /> {n.replace("Show ", "")}</label>)}
          <label className="row">Grahas in<DivisionSelect value={options.planet_varga ?? 1} onChange={(d) => setOptions({ ...options, planet_varga: d })} /></label>
          {tab !== "kurma" && <>
            <button onClick={() => setForm({ kind: "base" })}>Base graha and division</button>
            <button onClick={() => setForm({ kind: "star" })}>Base nakshatra</button>
            {(options.base_point !== null && options.base_point !== undefined || options.base_star !== null && options.base_star !== undefined) && <button onClick={() => setOptions({ ...options, base_point: null, base_star: null })}>Default base</button>}
          </>}
        </div>
      )}
      <Loaded q={q}>{(w) => <div className="pad">{build(w, undefined).draw}</div>}</Loaded>
      {dialogs}
    </div>
  );
}

function HouseDialog({ onOk, onClose }: { onOk: (house: number, point: string, d: number) => void; onClose: () => void }) {
  const [h, setH] = useState(0);
  const [p, setP] = useState(0);
  const [d, setD] = useState(1);
  return (
    <Modal title="Select a bhava" onClose={onClose}>
      <form method="dialog" onSubmit={(e) => { e.preventDefault(); onOk(h, HOUSE_POINTS[p], d); onClose(); }}>
        <label>Bhava to be highlighted as a special point<select value={h} onChange={(e) => setH(Number(e.target.value))}>{ORDINALS.map((n, i) => <option key={n} value={i}>{n}</option>)}</select></label>
        <label>from<select value={p} onChange={(e) => setP(Number(e.target.value))}>{HOUSE_POINTS.map((n, i) => <option key={n} value={i}>{n}</option>)}</select></label>
        <label>in the divisional chart<DivisionSelect value={d} onChange={setD} /></label>
        <FormButtons />
      </form>
    </Modal>
  );
}

export function Chakras() {
  const star = useChart((s) => s.display.layout === "starlight");
  const tabs = TABS.filter((t) => (star ? t.id !== "mixed" : !STARLIGHT_ONLY.has(t.id)));     // Mixed 2-Vargas in the Windows layout only, the textbook chakras in Starlight only
  const [kept, setTab] = useSaved<(typeof TABS)[number]["id"]>("chakras", "many");
  const tab = tabs.some((t) => t.id === kept) ? kept : "many";
  return (
    <section className="pane">
      <header className="pane-head tab-head"><SubTabs tabs={[...tabs]} value={tab} onChange={setTab} label="Chakras views" /></header>
      {tab === "many" ? <ManyVargas /> : tab === "mixed" ? <Mixed2 /> : <Wheels tab={tab} />}
    </section>
  );
}

/** The chakras read for transits, Starlight's Transits view Chakras: the Sarvatobhadra first, then the Kota, Kalachakra, Tripataki and
 *  Kurma, then the wheels whose vedhas, taras or trident points a transiting graha strikes, the Sudarsana with the transit over its rings,
 *  and the divisional charts. Not Avakahada (the name's syllable). */
export const TRANSIT_CHAKRAS = [{ id: "sbc", name: "Sarvatobhadra" }, { id: "kota", name: "Kota" }, { id: "kala", name: "Kalachakra" }, { id: "tripataki", name: "Tripataki" },
  { id: "kurma", name: "Kurma" }, { id: "shalaka", name: "Sapta Shalaka" }, { id: "tara", name: "Tara" }, { id: "ghataka", name: "Ghataka" },
  { id: "surya", name: "Surya Kalanala" }, { id: "chandra", name: "Chandra Kalanala" }, { id: "shoola", name: "Shoola" }, { id: "sudarsana", name: "Sudarsana" },
  { id: "many", name: "Divisional charts" }] as const;
/** Starlight Home's Avakahada (under More): over the box, the native's name sound (the syllable of the Moon's pada) with its pada and rasi,
 *  beside the Moon's avakahada; under it every nakshatra's four padas and their sounds, the natal grahas in theirs, the native's outlined.
 *  A pada clicked shows its own sound and reading over the box (kept over a refresh); a click anywhere else goes back to the Moon's. */
export function AvakahadaView() {
  const natal = useChart((s) => s.birth), birth = natal;     // the chart in use (a cast one too) as the native's
  const [picked, setPicked] = useKept<number | null>("avakahada.pada", null);
  useEffect(() => {
    if (picked === null) return;
    const off = (e: PointerEvent) => { if (!(e.target as Element).closest?.(".ava-pada")) setPicked(null); };
    addEventListener("pointerdown", off);
    return () => removeEventListener("pointerdown", off);
  }, [picked]); // eslint-disable-line react-hooks/exhaustive-deps
  const asked: ChakraOptions = { show: ["planets"], planet_varga: 1, chart_kind: null };
  const q = useQuery({ queryKey: ["chakras", natal, birth, asked], queryFn: () => api.chakras(natal!, birth!, asked), placeholderData: (p) => p });
  const padaName = (i: number) => `${STARS_27[Math.floor(i / 4)]} pada ${i % 4 + 1}`;
  const rasi = (i: number) => SIGN_NAMES[Math.floor(i / 9)];
  return (
    <Loaded q={q}>{(w) => {
      const { native: n, padas, every } = w.avakahada;
      const r = picked !== null && every?.[picked] ? every[picked] : n, mine = r.pada === n.pada;
      const facts: [string, string][] = [["Rasi lord", r.rasi_lord], ["Nakshatra lord", r.nak_lord], ["Varna", r.varna], ["Vashya", r.vashya],
        ["Yoni", r.yoni], ["Gana", r.gana], ["Nadi", r.nadi], ["Tatva", r.tatva]];
      const own = Math.floor(n.pada / 4);
      return <>
        <section className={mine ? "pane ava-native" : "pane ava-native other"}>
          <div className="ava-sound">
            <span className="ava-caption">{mine ? "Name sound" : "Sound of this pada"}</span>
            <span className="ava-syllable">{SYLLABLES[r.pada]}</span>
            <span className="ava-where">{padaName(r.pada)}<br />{rasi(r.pada)}</span>
          </div>
          <dl className="ava-facts">{facts.map(([k, v]) => <div key={k}><dt>{k}</dt><dd>{v}</dd></div>)}</dl>
        </section>
        <section className="pane ava-table">
          <table className="points">
            <thead><tr><th>Nakshatra</th><th>Rasi</th>{[1, 2, 3, 4].map((p) => <th key={p}>Pada {p}</th>)}</tr></thead>
            <tbody>{STARS_27.map((s, k) => (
              <tr key={s} className={k === own ? "here" : undefined}>
                <td>{s}</td>
                <td>{[...new Set([0, 1, 2, 3].map((j) => rasi(4 * k + j)))].join(" · ")}</td>
                {[0, 1, 2, 3].map((j) => {
                  const i = 4 * k + j, bodies = padas[i] ?? [];
                  return <td key={j} className={["ava-pada", i === n.pada && "ava-own", i === picked && i !== n.pada && "ava-picked"].filter(Boolean).join(" ")}
                    onClick={() => setPicked(i === n.pada ? null : i)} data-tip={`${padaName(i)} · ${rasi(i)}${bodies.length ? ` · ${bodies.join(" ")}` : ""}`}>
                    <strong>{SYLLABLES[i]}</strong>{bodies.length > 0 && <small>{bodies.join(" ")}</small>}
                  </td>;
                })}
              </tr>
            ))}</tbody>
          </table>
        </section>
      </>;
    }}</Loaded>
  );
}

/** One of TRANSIT_CHAKRAS for the cast transit: ``part`` "draw" the wheel alone (the left half), "side" its controls and reading. The
 *  divisional charts: the Chakras tab's nineteen, scrolling, in the left half; beside them Home's All Divisional Longitudes table. */
export function TransitChakra({ tab, part }: { tab: string; part: "draw" | "side" }) {
  if (tab === "many") return part === "draw" ? <div className="chakra-only-vargas"><ManyVargas /></div> : <Longitudes />;
  return <Wheels tab={tab} part={part} />;
}

function Longitudes() {
  const b = useBasics();
  return <Loaded q={b}>{(d) => <KeyInfo b={d} bare show="varga_longitudes" />}</Loaded>;
}
