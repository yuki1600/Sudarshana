import { useEffect, useMemo, useRef, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api, currentSettings, saveSettings, type Choice, type SettingOption, type Settings } from "./api";
import { useChart, type ChartStyle } from "./store";
import { recastMode } from "./Modes";
import { useAdmin, useKept } from "./hooks";
import { backdropClose, Modal } from "./ChartDialogs";
import type { Theme } from "./TopBar";
import { AccountPanel, themeNow } from "./Account";
import { LANGUAGES, languageOf } from "./translate";
import { SIGNS } from "./format";

const STYLES: [ChartStyle, string][] = [["south", "South Indian"], ["north", "North Indian"], ["east", "East Indian"]];
const CHANGED = "Changed";
const TOOLS = "Tools";
const ACCOUNT = "Account";
const LANGUAGE = "Language";

/** Settings > Language: the app's language, chosen at once (no Apply). Each is named in its own script and in English, and
 *  the list itself is never translated (translate="no"), so a language one cannot read still leads back to English. */
function LanguagePick() {
  const language = useChart((s) => languageOf(s.display.language));
  const setDisplay = useChart((s) => s.setDisplay);
  return (
    <>
      <div className="language-pick" role="radiogroup" aria-label="Language" translate="no">
        {LANGUAGES.map((l) => (
          <button key={l.id} type="button" role="radio" aria-checked={language === l.id} onClick={() => setDisplay({ language: l.id })}>
            <span className="language-native" lang={l.code}>{l.native}</span>
            {l.native !== l.id && <span className="language-english">{l.id}</span>}
          </button>
        ))}
      </div>
      <p className="muted hint">Changes at once, without Apply. Names, charts, tabs and tables change; long explanations stay in English.</p>
    </>
  );
}

/** A command that used to live in a menu: shown as a button on the Tools page. */
export interface Tool { group: string; label: string; onClick: () => void; disabled?: boolean }

/** A choice's value can be a number, a bool or a string; a select only holds strings. */
const key = (v: Choice["value"]) => String(v);

export function Control({ o, value, set }: { o: SettingOption; value: Choice["value"]; set: (v: Choice["value"]) => void }) {
  if (o.kind === "choice") {
    return (
      <select id={o.key} value={key(value)} onChange={(e) => set(o.choices!.find((c) => key(c.value) === e.target.value)!.value)}>
        {o.choices!.map((c) => <option key={key(c.value)} value={key(c.value)}>{c.label}</option>)}
      </select>
    );
  }
  if (o.kind === "bool") return <input id={o.key} type="checkbox" checked={value as boolean} onChange={(e) => set(e.target.checked)} />;
  if (o.kind === "number") {
    return <input id={o.key} type="number" step="any" min={o.ge ?? o.gt} max={o.le ?? o.lt} value={value as number}
      onChange={(e) => e.target.value !== "" && set(Number(e.target.value))} />;
  }
  return <input id={o.key} type="text" value={value as string} maxLength={o.max_length} onChange={(e) => set(e.target.value)} />;
}

/** The table of degrees the chosen choice follows (Mrityu and Pushkara bhaga), under the option; a row that another choice has otherwise is marked. */
function ChoiceTable({ o, value }: { o: SettingOption; value: Choice["value"] }) {
  const table = o.choices?.find((c) => c.value === value)?.table;
  if (!table) return null;
  const others = o.choices!.filter((c) => c.value !== value && c.table);
  const differs = (r: { name: string; degrees: number[] }) => others.some((c) => String(c.table!.find((x) => x.name === r.name)?.degrees) !== String(r.degrees));
  return (
    <table className="points degree-table" aria-label="The degrees followed">
      <thead><tr><th />{SIGNS.map((s) => <th key={s}>{s}</th>)}</tr></thead>
      <tbody>{table.map((r) => (
        <tr key={r.name} className={differs(r) ? "differs" : undefined} data-tip={differs(r) ? "Differs in the other table" : undefined}>
          <th scope="row">{r.name}</th>{r.degrees.map((d, i) => <td key={i}>{d}</td>)}
        </tr>
      ))}</tbody>
    </table>
  );
}

/** Every calculation option, by group. Only what differs from the defaults is kept and sent. */
/** the default place for new charts: its name, and choosing another (a dialog), this chart's place, or back to Mysuru */
export interface DefaultPlace { city: string; isDefault: boolean; choose: () => void; fromChart?: () => void; reset: () => void }

export function SettingsScreen({ open, group: first, tools = [], onClose, theme, setTheme, onSignOut, place }: { open: boolean; group: string; tools?: Tool[]; onClose: () => void; theme?: Theme; setTheme?: (t: Theme) => void; onSignOut?: () => void; place?: DefaultPlace }) {
  const ref = useRef<HTMLDialogElement>(null);
  const client = useQueryClient();
  const { chartStyle, setChartStyle, mode, display, setDisplay } = useChart();
  const english = languageOf(display.language) === "English";
  const schema = useQuery({ queryKey: ["settingsSchema"], queryFn: api.settingsSchema, enabled: open, staleTime: Infinity });
  const [draft, setDraft] = useState<Settings>({});
  const [style, setStyle] = useState<ChartStyle>(chartStyle);
  const admin = useAdmin();   // only the owner picks the layout and the colours, for now
  const [layout, setLayout] = useState(display.layout);
  const [brand, setBrand] = useState(display.brand);
  const [together, setTogether] = useState(display.transitsTogether);
  const [group, setGroup] = useKept("settings.group", "");
  const [find, setFind] = useState("");
  const [asking, setAsking] = useKept("settings.asking", false);
  const [naming, setNaming] = useKept("settings.naming", false);
  const [themeName, setThemeName] = useKept("settings.themeName", "");
  const [nameError, setNameError] = useState("");
  const account = useQuery({ queryKey: ["me"], queryFn: api.me, enabled: open && !!onSignOut }).data;
  /** the draft as applied now: on opening, and after the Account page switches theme */
  const reload = () => { const s = useChart.getState(); setDraft(currentSettings()); setStyle(s.chartStyle); setLayout(s.display.layout); setBrand(s.display.brand); setTogether(s.display.transitsTogether); };

  useEffect(() => {
    const d = ref.current;
    if (!d) return;
    if (open && !d.open) { reload(); setFind(""); if (first) setGroup(first); d.showModal(); } else if (!open && d.open) d.close();
  }, [open]); // eslint-disable-line react-hooks/exhaustive-deps

  const groups = schema.data ?? [];
  const options = useMemo(() => groups.flatMap((g) => g.options.map((o) => ({ ...o, group: g.name }))), [groups]);
  const changed = options.filter((o) => o.key in draft && draft[o.key] !== o.default);
  const needle = find.trim().toLowerCase();
  // a page kept from before its group was renamed or merged opens the first group
  const current = group && ([CHANGED, TOOLS, ACCOUNT, LANGUAGE, "Display"].includes(group) || !groups.length || groups.some((g) => g.name === group)) ? group : groups[0]?.name;
  const shown = needle
    ? options.filter((o) => (o.label + " " + o.group + " " + (o.choices ?? []).map((c) => c.label).join(" ")).toLowerCase().includes(needle))
    : current === CHANGED ? changed : options.filter((o) => o.group === current);

  const set = (o: SettingOption, v: Choice["value"]) => {
    const { [o.key]: _, ...rest } = draft;
    setDraft(v === o.default ? rest : { ...rest, [o.key]: v });
  };
  const resetGroup = () => {
    const names = new Set(shown.map((o) => o.key));
    setDraft(Object.fromEntries(Object.entries(draft).filter(([k]) => !names.has(k))));
  };
  const clean = () => Object.fromEntries(changed.map((o) => [o.key, draft[o.key]]));
  const commit = () => {
    setChartStyle(style);
    setDisplay({ layout, brand, transitsTogether: together });
    const kept = (currentSettings() as unknown as { per_dasa?: unknown }).per_dasa;     // what the dasas' own Options keep
    const next = (kept ? { ...clean(), per_dasa: kept } : clean()) as Settings;
    if (JSON.stringify(next) !== JSON.stringify(currentSettings())) {
      saveSettings(next);
      client.clear();
      recastMode();      // the chart in use (a Tajaka year ...) stays on screen, cast again with the new options
    }
  };
  const apply = () => { commit(); onClose(); };
  /** apply the draft, then keep it with the account under a name; a theme of the same name is replaced */
  const createTheme = async (e: React.FormEvent) => {
    e.preventDefault();
    const name = themeName.trim();
    if (!account || !name) return;
    commit();
    try {
      client.setQueryData(["me"], await api.saveThemes([...account.themes.filter((t) => t.name !== name), themeNow(name)]));
      setNaming(false); setThemeName(""); setNameError("");
    } catch (err) { setNameError((err as Error).message); }
  };

  return (
    <dialog ref={ref} className="dialog settings" onClose={onClose} onClick={backdropClose} aria-labelledby="settings-title">
      <header className="settings-head">
        <h2 id="settings-title">Settings</h2>
        <input type="search" aria-label="Find a setting" placeholder="Find a setting" value={find} onChange={(e) => setFind(e.target.value)} />
      </header>
      <div className="settings-body">
        <nav aria-label="Setting groups" className="settings-nav">
          {onSignOut && <button aria-current={!needle && current === ACCOUNT} onClick={() => { setGroup(ACCOUNT); setFind(""); }}>{ACCOUNT}</button>}
          {/* near the top, and named in English too while the app is in another language */}
          <button aria-current={!needle && current === LANGUAGE} onClick={() => { setGroup(LANGUAGE); setFind(""); }}>{LANGUAGE}{!english && <span className="muted" translate="no">Language</span>}</button>
          {groups.map((g) => {
            const edited = g.options.some((o) => o.key in draft && draft[o.key] !== o.default);
            return <button key={g.name} className={edited ? "edited" : undefined} title={edited ? "Changed from the defaults" : undefined} aria-current={!needle && current === g.name} onClick={() => { setGroup(g.name); setFind(""); }}>{g.name}</button>;
          })}
          <button aria-current={!needle && current === CHANGED} onClick={() => { setGroup(CHANGED); setFind(""); }} disabled={!changed.length}>{CHANGED}</button>
          <button aria-current={!needle && current === "Display"} onClick={() => { setGroup("Display"); setFind(""); }}>Display</button>
          <button aria-current={!needle && current === TOOLS} onClick={() => { setGroup(TOOLS); setFind(""); }}>{TOOLS}</button>
        </nav>
        <section className="settings-options" aria-live="polite">
          {schema.isError ? <p role="alert" className="error">{schema.error.message}</p> : schema.isPending ? <p className="muted">Loading…</p> : (
            <>
              <div className="settings-title-row">
                <h3>{needle ? `Settings matching "${find}"` : current}</h3>
                {shown.some((o) => o.key in draft) && <button onClick={resetGroup}>Back to defaults here</button>}
              </div>
              {!needle && current === "Display" && (
                <div className="setting">
                  <label htmlFor="chart-style">Chart style</label>
                  <select id="chart-style" value={style} onChange={(e) => setStyle(e.target.value as ChartStyle)}>
                    {STYLES.map(([v, t]) => <option key={v} value={v}>{t}</option>)}
                  </select>
                </div>
              )}
              {!needle && current === "Display" && admin && (
                <div className="setting">
                  <label htmlFor="layout-theme">Layout theme</label>
                  <select id="layout-theme" value={layout} onChange={(e) => setLayout(e.target.value as typeof layout)}>
                    <option value="windows">Windows: four charts and the Key Info windows</option>
                    <option value="starlight">Starlight: four charts, an inspector and tabs</option>
                  </select>
                </div>
              )}
              {!needle && current === "Display" && admin && layout === "starlight" && (
                <div className="setting">
                  <label htmlFor="brand-colours">Brand colours</label>
                  <select id="brand-colours" value={brand} onChange={(e) => setBrand(e.target.value as typeof brand)}>
                    <option value="sudarshana">Sudarshana: black, white, purple and gold</option>
                    <option value="praajna">Praajna Jyotisha: saffron, gold and maroon</option>
                  </select>
                </div>
              )}
              {!needle && current === "Display" && (
                <div className="setting">
                  <label htmlFor="transits-together">Transits, Tajaka and Tithi Pravesha</label>
                  <select id="transits-together" value={String(together)} onChange={(e) => setTogether(e.target.value === "true")}>
                    <option value="true">Together: Tajaka and Tithi Pravesha as sub tabs of Transits</option>
                    <option value="false">Separate: each a page of its own on the top bar</option>
                  </select>
                </div>
              )}
              {!needle && current === "Display" && theme && setTheme && (
                <div className="setting">
                  <label htmlFor="colour-theme">Colour theme</label>
                  <select id="colour-theme" value={theme} onChange={(e) => setTheme(e.target.value as Theme)}>
                    <option value="auto">System</option>
                    <option value="light">Light</option>
                    <option value="dark">Dark</option>
                  </select>
                </div>
              )}
              {!needle && current === "Display" && place && (
                <div className="setting">
                  <label htmlFor="default-place">Default place for new charts</label>
                  <span className="row">
                    <strong>{place.city}</strong>
                    <button id="default-place" type="button" onClick={place.choose}>Choose a place…</button>
                    <button type="button" disabled={!place.fromChart} onClick={place.fromChart}>Use this chart's place</button>
                    {!place.isDefault && <button type="button" onClick={place.reset}>Back to Mysuru</button>}
                  </span>
                  <p className="muted hint">The app opens on a chart of this moment here, and every new chart starts here. Kept with your account; it changes at once, without Apply.</p>
                </div>
              )}
              {!needle && current === ACCOUNT && onSignOut && <AccountPanel onSignOut={() => { onClose(); onSignOut(); }} onTheme={reload} />}
              {!needle && current === LANGUAGE && <LanguagePick />}
              {!needle && current === TOOLS && Array.from(new Set(tools.map((t) => t.group))).map((g) => (
                <fieldset key={g} className="tools">
                  <legend>{g}</legend>
                  {tools.filter((t) => t.group === g).map((t) => <button key={t.label} type="button" disabled={t.disabled} onClick={() => { onClose(); t.onClick(); }}>{t.label}</button>)}
                </fieldset>
              ))}
              {needle && !shown.length && <p className="muted">Nothing matches.</p>}
              {shown.map((o) => {
                const edited = o.key in draft && draft[o.key] !== o.default;
                return (
                  <div key={o.key} className={`setting ${o.kind}${edited ? " edited" : ""}`}>
                    <label htmlFor={o.key}>{needle && <span className="muted">{o.group}: </span>}{o.label}</label>
                    <Control o={o} value={o.key in draft ? draft[o.key] : o.default} set={(v) => set(o, v)} />
                    {o.help && <p className="muted hint">{o.help}</p>}
                    <ChoiceTable o={o} value={o.key in draft ? draft[o.key] : o.default} />
                  </div>
                );
              })}
            </>
          )}
        </section>
      </div>
      <footer className="settings-foot">
        <span className="muted">{changed.length ? `${changed.length} changed from the defaults. ` : "All at the defaults. "}{mode && `Applying a change recalculates ${mode.title} in place.`}</span>
        <menu>
          <button type="button" onClick={() => setAsking(true)} disabled={!changed.length}>All back to defaults</button>
          {account && <button type="button" onClick={() => setNaming(true)}>Create theme</button>}
          <button type="button" className="primary" onClick={apply}>Apply</button>
        </menu>
      </footer>
      {naming && account && (
        <Modal title="Create theme" onClose={() => setNaming(false)}>
          <form onSubmit={createTheme}>
            <p className="muted">Applies these settings and saves them with your account, to pick later under Account, Themes.</p>
            <div className="setting"><label htmlFor="theme-name">Name</label>
              <input id="theme-name" value={themeName} onChange={(e) => setThemeName(e.target.value)} required maxLength={60} autoFocus /></div>
            {account.themes.some((t) => t.name === themeName.trim()) && <p className="muted hint">Replaces the theme of this name.</p>}
            {nameError && <p role="alert" className="error">{nameError}</p>}
            <menu>
              <button type="button" onClick={() => setNaming(false)}>Cancel</button>
              <button type="submit" className="primary">Save theme</button>
            </menu>
          </form>
        </Modal>
      )}
      {asking && (
        <Modal title="Back to defaults" onClose={() => setAsking(false)}>
          <form method="dialog" onSubmit={(e) => { e.preventDefault(); setDraft({}); setAsking(false); }}>
            <p>Are you sure you want to revert back to defaults?</p>
            <menu>
              <button type="button" onClick={() => setAsking(false)}>Cancel</button>
              <button type="submit" className="primary">Revert</button>
            </menu>
          </form>
        </Modal>
      )}
    </dialog>
  );
}
