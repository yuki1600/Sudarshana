import { lazy, Suspense, useEffect, useRef, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api, auth, chartName, saveSettings, type Account, type Birth, type ChartFormat, type Meta, type Settings } from "./api";
import { Login } from "./Login";
import Intro from "./Intro";   // bundled, not lazy: a lazy one suspends for a tick and the home page flashes before it
import { About } from "./About";
import { BirthDialog, keepHome, keptHome, MYSURU, nowChart, saveHome } from "./BirthDialog";
import { Chakras } from "./Chakras";
import { Dasas } from "./Dasas";
import { Longevity } from "./Longevity";
import { Predictions } from "./Predictions";
import { modeOf, MundaneCharts, recastMode, TithiPravesha } from "./Modes";
import { PrintView } from "./Print";
import { SettingsScreen, type Tool } from "./Settings";
import { Tajaka } from "./Tajaka";
import { Traditions, TraditionsLeft } from "./Traditions";
import { openTransitChakras, Transits, TransitsLeft } from "./Transits";
import { Timeline } from "./Timeline";
import { download, useDisplayStyles, Windows } from "./Windows";
import { OpenChart } from "./OpenChart";
import { useBasics, useKept } from "./hooks";
import { ChartPane } from "./ChartPane";
import { Strengths } from "./Strengths";
import { BasicsPane } from "./Views";
import { LeftCharts, Starlight } from "./Starlight";
import { LoreHost } from "./Lore";
import { Muhurta } from "./Muhurta";
import { Remedies } from "./Remedies";
import { Calculations } from "./Calculations";
import { useChart } from "./store";
import { leave, pull } from "./kept";
import { pageTabs, TopBar, type Theme } from "./TopBar";
import { IconTips } from "./ui";

const Astrocartography = lazy(() => import("./Astrocartography").then((m) => ({ default: m.Astrocartography })));   // its map data is big, and most sessions never open it
const Finance = lazy(() => import("./Finance").then((m) => ({ default: m.Finance })));
const Matching = lazy(() => import("./Matching").then((m) => ({ default: m.Matching })));
const Research = lazy(() => import("./Mundane").then((m) => ({ default: m.Research })));   // the four event databases: loaded on first visit

const SCREENS: Record<string, React.ReactNode> = {
  Strengths: <Strengths />, Dasas: <Dasas />, Transits: <Transits />, Longevity: <Longevity />, Predictions: <Predictions />, Tajaka: <Tajaka />,
  "Tithi Pravesha": <TithiPravesha />, Mundane: <MundaneCharts />, Traditions: <Traditions />
};

const readTheme = (): Theme => { try { return (localStorage.getItem("theme") as Theme) || "auto"; } catch { return "auto"; } };

/** The charts, tools and dialogs: everything behind sign-in. */
function Workspace({ theme, setTheme, onSignOut }: { theme: Theme; setTheme: (t: Theme) => void; onSignOut: () => void }) {
  const store = useChart();
  const { name, natal, birth, meta, tab, setTab, openChart, notes, setNotes, openWindow, display, setDisplay, navigate, undo, undoAll, recent, birthZone, enterMode } = store;
  const [dialog, setDialog] = useKept<"edit" | "new" | "home" | null>("app.dialog", null);
  const [prefs, setPrefs] = useKept<string | null>("app.prefs", null);
  const [printing, setPrinting] = useKept("app.printing", false);
  const [about, setAbout] = useKept("app.about", false);
  const [error, setError] = useState("");
  const [opening, setOpening] = useKept("app.opening", false);
  const [saved, setSaved] = useState(0);   // bumped on each cloud save: remounts the "Saved" flash so it plays again
  const iniFile = useRef<HTMLInputElement>(null);
  const client = useQueryClient();
  const basics = useBasics();
  useDisplayStyles();

  const load = async (title: string, content: string) => {
    setError("");
    try {
      const { birth, parsed } = await api.parseJhd(content);
      if (parsed.notes) setNotes(title, parsed.notes);   // only a .vs file carries notes
      openChart(title, birth, {
        city: parsed.city ?? "", country: parsed.country ?? "", dst: !!parsed.dst,
        tz_standard_east: parsed.tz_standard_east, tz_dst_east: parsed.tz_dst_east, gender: parsed.gender,
        ...(parsed.state ? { state: parsed.state } : {})
      });
    } catch (e) { setError((e as Error).message); }
  };
  // the account's default place into this browser before the first chart of the moment (App's own copy runs after this)
  const sampling = useRef(new URLSearchParams(location.search).get("sample"));
  useEffect(() => {  // /?sample=Mahatma%20Gandhi opens that sample chart
    const home = client.getQueryData<Account | null>(["me"])?.home;
    if (home) keepHome(home);
    const s = sampling.current;
    if (!s) return;
    history.replaceState(null, "", location.pathname);   // a refresh must keep the chart's mode, not reopen the sample
    api.sample(s).then((r) => load(s, r.content)).catch((e) => setError(e.message))
      .finally(() => { sampling.current = null; if (!useChart.getState().natal) newChart(); });
  }, []); // eslint-disable-line react-hooks/exhaustive-deps
  // never an empty page: no chart open (signed in, or the last one closed) → a chart of this moment at the default place
  useEffect(() => { if (!natal && !sampling.current) newChart(); }, [natal]); // eslint-disable-line react-hooks/exhaustive-deps

  // a new chart is this moment at the default place (Mysuru until one is chosen in Settings > Display); Edit (Ctrl+D) changes it
  const newChart = () => { const c = nowChart(); openChart("Prashna (Now)", c.birth, c.meta); };
  // the default place, shown and changed in Settings > Display; homes bumps so that row shows the new one
  const [, setHomes] = useState(0);
  const setHome = (b: Birth | null, m?: Meta) => { saveHome(b, m); setHomes((n) => n + 1); };
  const place = { city: (keptHome() ?? MYSURU).meta?.city || "the chosen place", isDefault: !keptHome(), choose: () => setDialog("home"),
    fromChart: natal ? () => setHome(natal, meta as Meta) : undefined, reset: () => setHome(null) };
  const open = async (files: File[]) => { setOpening(false); for (const f of files) await load(chartName(f.name), await f.text()); };   // each opens as its own chart
  const openCloud = (n: string, content: string) => { setOpening(false); load(n, content); };
  type Doc = { name: string; natal: Birth | null; meta: Partial<Meta>; birthZone: number | null };
  const chartFile = async (format: ChartFormat = "jhd", c: Doc = { name, natal, meta, birthZone }) => {
    // always the natal chart, even inside a mode; and at its own zone (Change timezone only changes the clock shown)
    const b = c.birthZone === null ? c.natal! : (await api.timezone(c.natal!, c.birthZone)).birth;
    return (await api.exportChart(b, c.meta as Meta, format, c.name, notes[c.name] ?? "")).content;
  };
  /** Every open chart's natal chart into the cloud, under its name. A cast chart (Transit, Tajaka...) only being viewed stays
   *  unsaved; one cast with + is an open chart of its own, already named like "Tajaka-2026-Name". */
  const saveAll = async (pick?: (id: string) => boolean) => {   // pick: only those open charts (by id)
    try {
      const docs = store.openCharts.map((c) => c.id === store.activeChartId ? { ...c, name, natal: natal!, meta: meta as Meta, birthZone } : c)
        .filter((c) => !pick || pick(c.id));
      await Promise.all(docs.map(async (c) => api.saveCloudChart(c.name || "chart", await chartFile("vs", { ...c, name: c.name || "chart" }))));
      client.invalidateQueries({ queryKey: ["cloudCharts"] });
      setSaved((n) => n + 1);
    } catch (e) { setError((e as Error).message); }
  };
  // the current chart into the cloud (Save icon, Ctrl+S); Save chart as... asks for the name first
  const save = async (asNew = false) => {
    if (!natal) return;
    const chosen = asNew ? prompt("Save as", name || "chart") : name || "chart";
    if (!chosen) return;
    try {
      await api.saveCloudChart(chosen, await chartFile("vs"));   // a .vs file: it keeps the name, state and notes
      client.invalidateQueries({ queryKey: ["cloudCharts"] });
      setSaved((n) => n + 1);
    } catch (e) { setError((e as Error).message); }
  };
  // Edit birth data's Save is a real save: into the cloud too, so the chart isn't marked unsaved (only stepping the time is)
  const editSaved = async (n: string, b: Birth, m: Meta) => {
    store.setChart(n, b, m);
    const s = useChart.getState();
    try {
      await api.saveCloudChart(s.name || "chart", await chartFile("vs", { ...s, name: s.name || "chart" }));
      client.invalidateQueries({ queryKey: ["cloudCharts"] });
      setSaved((k) => k + 1);
    } catch (e) { setError((e as Error).message); }
  };
  const downloadFile = async (format: ChartFormat) => {
    if (!natal) return;
    try { download(`${name || "chart"}.${format}`, await chartFile(format)); } catch (e) { setError((e as Error).message); }
  };
  const email = async () => { location.href = `mailto:?subject=${encodeURIComponent(`Chart: ${name}`)}&body=${encodeURIComponent(await chartFile())}`; };
  const copyReport = (complete: boolean) => openWindow({ kind: "copy_all", complete });
  const exportIni = async () => download("preferences.ini", (await api.iniExport()).content);
  const importIni = async (f?: File) => {
    if (!f) return;
    try {
      const s: Settings = await api.iniParse(await f.text());
      saveSettings(s);
      client.clear();
      recastMode();      // the chart in use stays, cast again with the new options
      openWindow({ kind: "message", title: "Import preferences", text: `Read ${Object.keys(s).length} option(s) that differ from the defaults.` });
    } catch (e) { setError((e as Error).message); }
  };
  const restore = () => { saveSettings({}); client.clear(); recastMode(); openWindow({ kind: "message", title: "Calculation options", text: "All calculation options are back at the defaults." }); };
  const lifecycle = async (n: number) => {
    if (!natal) return;
    try {
      const r = await api.lifecycle(natal, n);
      enterMode(r.birth, modeOf(r));
    } catch (e) { setError((e as Error).message); }
  };
  const nisheka = async () => {
    if (!natal) return;
    try {
      const r = await api.nisheka(natal);
      enterMode(r.birth, modeOf(r));
    } catch (e) { setError((e as Error).message); }
  };
  const noChart = !natal;
  const win = (label: string, w: Parameters<typeof openWindow>[0], disabled = false, group = "Display"): Tool => ({ group, label, disabled, onClick: () => openWindow(w) });
  const bigger = (d: number) => setDisplay({ listFont: Math.min(7, Math.max(0, display.listFont + d)), chartFont: Math.min(7, Math.max(0, display.chartFont + d)) });
  const tools: Tool[] = [
    { group: "Chart", label: "Save chart as...", disabled: noChart, onClick: () => save(true) },
    { group: "Chart", label: "Email chart", disabled: noChart, onClick: email },
    win("Change time zone", { kind: "timezone" }, noChart, "Chart"),
    win("Chart notes", { kind: "notes" }, noChart, "Chart"),
    win("Aspect table with relationships", { kind: "aspects" }, noChart, "Chart"),
    { group: "Chart", label: "Undo all birth time changes", disabled: !undo.length, onClick: undoAll },
    { group: "Chart", label: "Copy basic calculations", disabled: noChart, onClick: () => copyReport(false) },
    { group: "Chart", label: "Copy complete calculations", disabled: noChart, onClick: () => copyReport(true) },
    { group: "Chart", label: "Nisheka / Aadhana chart", disabled: noChart, onClick: nisheka },
    { group: "Chart", label: "Next lifecycle", disabled: noChart, onClick: () => lifecycle(1) },
    { group: "Chart", label: "Previous lifecycle", disabled: noChart, onClick: () => lifecycle(-1) },
    win("Chart style and language", { kind: "style" }),
    { group: "Display", label: "Bigger fonts", disabled: display.listFont >= 7, onClick: () => bigger(1) },
    { group: "Display", label: "Smaller fonts", disabled: display.listFont <= 0, onClick: () => bigger(-1) },
    win("Adjust font size", { kind: "fonts" }),
    win("Colors", { kind: "colors" }),
    win("Pages to include in printouts", { kind: "pages" }),
    win("Name and address for printouts", { kind: "address" }),
    { group: "Display", label: "Save current window sizes", onClick: () => { const w = document.querySelector<HTMLElement>(".charts")?.getBoundingClientRect().width; setDisplay({ split: w ? Math.round(w) : null }); } },
    { group: "Display", label: "Back to default window sizes", disabled: !display.split, onClick: () => setDisplay({ split: null }) },
    { group: "Preferences", label: "Import preferences", onClick: () => iniFile.current?.click() },
    { group: "Preferences", label: "Export preferences", onClick: exportIni },
    win("View preferences file", { kind: "ini" }, false, "Preferences"),
    { group: "Preferences", label: "Restore default calculation options", onClick: restore },
    ...recent.map((r): Tool => ({ group: "Recent charts", label: r.name || "(no name)", onClick: () => openChart(r.name, r.birth, r.meta) })),
  ];

  // Keyboard shortcuts; not while typing in a field
  useEffect(() => {
    const key = (e: KeyboardEvent) => {
      const typing = (e.target as Element)?.matches?.("input,textarea,select");
      if (e.altKey && e.key === "ArrowLeft") { navigate(-1); e.preventDefault(); }
      if (e.altKey && e.key === "ArrowRight") { navigate(1); e.preventDefault(); }
      if (e.key === "F6") {   // Next and previous pane
        const panes = Array.from(document.querySelectorAll<HTMLElement>(".pane, .chart-panel"));
        const i = panes.findIndex((p) => p.contains(document.activeElement));
        const next = panes[(i + (e.shiftKey ? panes.length - 1 : 1)) % panes.length];
        next?.setAttribute("tabindex", "-1");
        next?.focus();
        e.preventDefault();
      }
      if (e.ctrlKey && e.key === "Tab") { const TABS: readonly string[] = pageTabs(display.transitsTogether, display.layout === "starlight"); setTab(TABS[(TABS.indexOf(tab) + (e.shiftKey ? TABS.length - 1 : 1)) % TABS.length]); e.preventDefault(); }
      if (!(e.ctrlKey || e.metaKey) || typing) return;
      const k = e.key.toLowerCase();
      if (k === "o") { setOpening(true); e.preventDefault(); }
      if (k === "s" && natal) { save(); e.preventDefault(); }
      if (k === "d") { setDialog("edit"); e.preventDefault(); }
      if (k === "n") { newChart(); e.preventDefault(); }
      if (k === "p" && natal) { setPrinting(true); e.preventDefault(); }
      if (k === "c" && natal && !getSelection()?.toString()) { copyReport(true); e.preventDefault(); }
    };
    document.addEventListener("keydown", key);
    return () => document.removeEventListener("keydown", key);
  });

  // Tajaka or Tithi Pravesha kept as a page (an old session, or Settings just joined them): open it as Transits' sub tab
  const joined = display.transitsTogether && (tab === "Tajaka" || tab === "Tithi Pravesha");
  useEffect(() => { if (joined) store.go("Transits", ["transits", tab === "Tajaka" ? "tajaka" : "tithi"]); }, [joined]); // eslint-disable-line react-hooks/exhaustive-deps

  // Starlight has no Chakras page: one kept from before opens where its views went (Avakahada on Home, the rest in Transits' Chakras view)
  const oldChakras = display.layout === "starlight" && tab === "Chakras";
  useEffect(() => {
    if (!oldChakras) return;
    let sub = "";
    try { sub = localStorage.getItem("view.chakras") ?? ""; } catch { /* private window */ }
    if (sub === "avakahada") store.go("Home", ["starTab", "avakahada"]); else openTransitChakras(sub);
  }, [oldChakras]); // eslint-disable-line react-hooks/exhaustive-deps

  if (printing && natal) return <PrintView onClose={() => setPrinting(false)} />;
  return (
    <div className="app">
      <IconTips />
      <TopBar onNew={newChart} onOpen={() => setOpening(true)} onSave={() => save()} onSaveAll={saveAll} onDownload={downloadFile} onEdit={() => setDialog("edit")} onSettings={() => setPrefs("")} onAbout={() => setAbout(true)}
        onPrint={() => setPrinting(true)} onSignOut={onSignOut} theme={theme} setTheme={setTheme} />
      <input ref={iniFile} type="file" accept=".ini,text/plain" hidden onChange={(e) => { importIni(e.target.files?.[0]); e.target.value = ""; }} />
      {error && <p role="alert" className="error banner">{error}</p>}
      <main>
        {tab === "Remedies" ? <Remedies />
          : tab === "Muhurta" ? <Muhurta />
          : tab === "Calculations" ? <Calculations />
          : tab === "Research" ? <Suspense fallback={<p className="empty">Loading…</p>}><Research /></Suspense>
            : !birth ? <p className="empty">Loading…</p>
              : basics.isPending ? <p className="empty">Calculating…</p>
                : basics.isError ? <p role="alert" className="error banner">{basics.error.message}</p>
                  : tab === "Timeline" ? <Timeline />
                  : tab === "Chakras" ? <Chakras />
                    : tab === "Astrocartography" ? <Suspense fallback={<p className="empty">Calculating…</p>}><Astrocartography /></Suspense>
                      : tab === "Finance" ? <Suspense fallback={<p className="empty">Loading…</p>}><Finance /></Suspense>
                        : tab === "Matching" ? <Suspense fallback={<p className="empty">Calculating…</p>}><Matching /></Suspense>
                          : tab === "Home" && display.layout === "starlight" ? <Starlight b={basics.data} />
                          : (
                            <div className={display.layout === "starlight" ? "basics star-basics" : "basics"}>
                              {display.layout === "starlight" ? (tab === "Transits" ? <TransitsLeft /> : tab === "Traditions" ? <TraditionsLeft /> : <LeftCharts />) : <ChartPane />}
                              {SCREENS[tab] ?? <BasicsPane />}
                            </div>
                          )}
      </main>
      <SettingsScreen open={prefs !== null} group={prefs ?? ""} tools={tools} onClose={() => setPrefs(null)} theme={theme} setTheme={setTheme} onSignOut={onSignOut} place={place} />
      <BirthDialog open={dialog !== null} blank={dialog !== "edit"} onClose={() => setDialog(null)} placeOnly={dialog === "home"}
        title={dialog === "home" ? "Default place for new charts" : undefined}
        onSave={dialog === "home" ? (_n, b, m) => setHome(b, m) : dialog === "edit" ? editSaved : undefined} />
      <About open={about} onClose={() => setAbout(false)} />
      {store.notice && <div key={store.notice.at} className="notice-flash" role="status" onAnimationEnd={store.clearNotice}>{store.notice.text}</div>}
      {saved > 0 && <div key={saved} className="saved-flash" role="status" onAnimationEnd={() => setSaved(0)}><span className="saved-tick" aria-hidden="true">✓</span>Saved successfully</div>}
      {opening && <OpenChart onFiles={open} onCloud={openCloud} onClose={() => setOpening(false)} />}
      <Windows />
      <LoreHost />
    </div>
  );
}

/** Back from a social sign-in (Login marks it before leaving): read once per page load, outside React so dev's double render can't lose it. */
const BACK_FROM_SOCIAL = (() => {
  try { const v = sessionStorage.getItem("intro"); sessionStorage.removeItem("intro"); return !!v; } catch { return false; }
})();

/** The sign-in page until there is a session, then the workspace; the intro plays over the sign-in page as it opens, and
 *  signing in fades into the workspace. */
export default function App() {
  const client = useQueryClient();
  const me = useQuery({ queryKey: ["me"], queryFn: api.me });
  // the fade on signing in, by the form or back from a social sign-in (Login marks that), never for a signed-in reload
  const [fade, setFade] = useState(BACK_FROM_SOCIAL);
  const [doorIntro, setDoorIntro] = useState(true);   // only when the page loads on the sign-in page, never after signing out
  const [theme, setTheme] = useState<Theme>(readTheme);
  auth.onUnauthorized = () => client.setQueryData(["me"], null);   // the session ended mid-use: back to sign-in

  // the default place for new charts is the signed-in account's: copy it into this browser on the way in, drop it on the way
  // out so the next login doesn't inherit it. An account with none adopts one this browser chose before places were kept
  // per account.
  const account = me.data;
  useEffect(() => { if (!me.isPending) document.getElementById("boot")?.remove(); }, [me.isPending]);   // the sign-in page or the workspace is up: lift the black cover
  useEffect(() => {
    if (account === undefined) return;   // still asking
    if (account) setDoorIntro(false);   // a signed-in load: signing out later shows the sign-in page without the intro
    if (account === null) return keepHome(null);
    const old = keptHome();
    if (account.home) keepHome(account.home);
    else if (old) api.saveHome(old).catch(() => {});
  }, [account]);

  // for now only the owner may use the Windows layout or the Praajna colours: everyone else is kept on Starlight in
  // Sudarshana's, whatever their browser, a kept screen or a saved theme had
  const layout = useChart((s) => s.display.layout), brand = useChart((s) => s.display.brand);
  useEffect(() => {
    if (account && !account.admin && (layout !== "starlight" || brand !== "sudarshana")) useChart.getState().setDisplay({ layout: "starlight", brand: "sudarshana" });
  }, [account, layout, brand]);

  useEffect(() => {
    const el = document.documentElement;
    if (theme === "auto") el.removeAttribute("data-theme"); else el.setAttribute("data-theme", theme);
    try { localStorage.setItem("theme", theme); } catch { /* private window: theme just isn't remembered */ }
  }, [theme]);

  const signOut = async () => {
    await leave();
    await api.signOut().catch(() => { /* offline: the cookie stays, but this tab still forgets the session */ });
    client.setQueryData(["me"], null);
    client.removeQueries({ predicate: (q) => q.queryKey[0] !== "me" });   // not clear(): App's own "me" observer must keep its query
  };
  return (
    <>
      {me.data ? <Workspace theme={theme} setTheme={setTheme} onSignOut={signOut} />
        : !me.isPending && <Login paused={doorIntro} onDone={async (a) => {
          // the account kept another screen than this browser's: reload so every module reads it, fading in as from a social sign-in
          if (await pull()) { try { sessionStorage.setItem("intro", "1"); } catch { /* no fade */ } location.reload(); return; }
          setFade(true); client.setQueryData(["me"], a);
        }} />}
      {fade && account && <div className="enter-fade" onAnimationEnd={() => setFade(false)} />}
      {doorIntro && account === null && <Intro onDone={() => setDoorIntro(false)} />}
    </>
  );
}

export type { Birth };
