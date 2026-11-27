import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api, currentSettings, saveSettings, type Choice, type SettingOption, type Settings } from "./api";
import { OPTIONAL, starOptional } from "./ChartPane";
import { LANGUAGES, languageOf } from "./translate";
import { Control } from "./Settings";
import { useChart, type ChartStyle, type Display } from "./store";
import { useAdmin } from "./hooks";
import { recastMode } from "./Modes";
import { SIZES } from "./Windows";
import { reconcile } from "./barOrder";
import { barDefault, barLabel, canHide } from "./TopBar";

const STYLES: [ChartStyle, string][] = [["north", "North"], ["south", "South"], ["east", "East"]];
// the calculation groups that change what the charts and the Grahas tab show; the bhava chart's reference is already on its own buttons
const GROUPS = ["Arudha padas", "Bhava chart and aspect table", "Outer grahas"];
const SKIP = new Set(["bhava_ref"]);

/** Starlight's Settings tab: how the charts look and which bodies they show, each change applied at once. The full Settings dialog still has everything. */
export function StarSettings() {
  const { chartStyle, setChartStyle, display, setDisplay, optional, setOptional, openWindow } = useChart();
  const client = useQueryClient();
  const admin = useAdmin();   // only the owner picks the colours, for now
  const schema = useQuery({ queryKey: ["settingsSchema"], queryFn: api.settingsSchema, staleTime: Infinity });
  const [, redraw] = useState(0);
  const saved = currentSettings() as unknown as Record<string, Choice["value"]>;
  const set = (o: SettingOption, v: Choice["value"]) => {     // only what differs from the default is kept, as in the dialog
    const { [o.key]: _, ...rest } = saved;
    saveSettings((v === o.default ? rest : { ...rest, [o.key]: v }) as unknown as Settings);
    client.invalidateQueries();
    recastMode();
    redraw((n) => n + 1);
  };
  const flag = (k: "degrees" | "retroRed" | "signLabels" | "linkCharts", label: string) => (
    <label className="check"><input type="checkbox" checked={display[k]} onChange={(e) => setDisplay({ [k]: e.target.checked } as Partial<Display>)} />{label}</label>
  );
  const pick = <K extends keyof Display>(k: K, label: string, options: [Display[K], string][]) => (
    <label className="set-row">{label}
      <select value={String(display[k])} onChange={(e) => setDisplay({ [k]: options.find(([v]) => String(v) === e.target.value)![0] } as Partial<Display>)}>
        {options.map(([v, t]) => <option key={String(v)} value={String(v)}>{t}</option>)}
      </select>
    </label>
  );
  // a few choices as one row of buttons, the chosen one lit
  const buttons = <T,>(label: string, value: T, options: [T, string][], choose: (v: T) => void) => (
    <div className="set-row">{label}
      <div className="seg" role="radiogroup" aria-label={label}>
        {options.map(([v, t]) => <button key={String(v)} type="button" role="radio" aria-checked={value === v} aria-selected={value === v} onClick={() => choose(v)}>{t}</button>)}
      </div>
    </div>
  );
  // the top bar's pieces in their halves, as the user arranged them: ticked ones show (right-clicking the bar does the same)
  const bar = reconcile(display.bar, barDefault(display.transitsTogether));
  const showOnBar = (id: string, on: boolean) => setDisplay({ barHidden: on ? display.barHidden.filter((x) => x !== id) : [...display.barHidden, id] });
  const names: ["english" | "sanskrit", string][] = [["english", "English"], ["sanskrit", "Sanskrit"]];
  const sizes = SIZES.map((t, i): [number, string] => [i, t]);
  const reset = (options: SettingOption[]) => {     // the group's options back at their defaults: none of them kept
    const rest = { ...saved };
    for (const o of options) delete rest[o.key];
    saveSettings(rest as unknown as Settings);
    client.invalidateQueries();
    recastMode();
    redraw((n) => n + 1);
  };
  const value = (o: SettingOption) => (o.key in saved ? saved[o.key] : o.default);
  const group = (g: { name: string; options: SettingOption[] }) => g.name === "Outer grahas" ? (
    // one row per graha: its own sign, then where it is exalted (debilitated opposite)
    <section key={g.name} className="pane star-outer">
      <header className="pane-head"><h2>{g.name}</h2><button type="button" onClick={() => reset(g.options)}>Restore defaults</button></header>
      <div className="outer-grid">
        <span /><span className="muted">Own sign</span><span className="muted">Exalted / debilitated</span>
        {["uranus", "neptune", "pluto"].map((p) => [g.options.find((o) => o.key === p + "_own"), g.options.find((o) => o.key === p + "_exalted")]).map(([own, ex]) => own && ex && (
          <div key={own.key} className="outer-row">
            <span>{own.label.split("'")[0]}</span>
            <Control o={own} value={value(own)} set={(v) => set(own, v)} />
            <Control o={{ ...ex, choices: ex.choices!.map((c) => ({ ...c, label: c.label.replace(/ \(debilitated in (\w+)\)/, " / $1") })) }} value={value(ex)} set={(v) => set(ex, v)} />
          </div>
        ))}
      </div>
    </section>
  ) : (
    <section key={g.name} className="pane">
      <header className="pane-head"><h2>{g.name}</h2></header>
      {g.options.filter((o) => !SKIP.has(o.key)).map((o) => (
        <div key={o.key} className={`set-row ${o.kind}`}>
          <label htmlFor={o.key}>{o.label}</label>
          <Control o={o} value={value(o)} set={(v) => set(o, v)} />
        </div>
      ))}
    </section>
  );
  return (
    <div className="star-settings">
      <div className="star-settings-col">
        <section className="pane">
          <header className="pane-head"><h2>Charts</h2></header>
          {admin && buttons<Display["brand"]>("Colours", display.brand, [["sudarshana", "Sudarshana"], ["praajna", "Praajna Jyotisha"]], (v) => setDisplay({ brand: v }))}
          {buttons("Chart style", chartStyle, STYLES, setChartStyle)}
          {buttons("Graha names", display.planets, names, (v) => setDisplay({ planets: v }))}
          {buttons("Sign names", display.signs, names, (v) => setDisplay({ signs: v }))}
          {/* the whole app's, as Settings > Language: each named in its own script, never translated */}
          <label className="set-row">Language
            <select translate="no" value={languageOf(display.language)} onChange={(e) => setDisplay({ language: e.target.value })}>
              {LANGUAGES.map((l) => <option key={l.id} value={l.id}>{l.native === l.id ? l.id : `${l.native} (${l.id})`}</option>)}
            </select>
          </label>
          {pick("chartFont", "Text in the charts", sizes)}
          {pick("listFont", "Text in lists and tables", sizes)}
          {flag("degrees", "Degrees beside each graha")}
          {flag("retroRed", "Retrograde grahas in red")}
          {flag("signLabels", "Sign names in each box")}
          {flag("linkCharts", "Lower charts follow the top chart: their varga of its varga (D-9 of D-24)")}
        </section>
        <section className="pane">
          <header className="pane-head"><h2>Bodies in the chart</h2></header>
          {OPTIONAL.map(([k, n, on]) => { const o = starOptional(optional); return (
            <label key={k} className="check"><input type="checkbox" checked={o[k] ?? on} onChange={() => setOptional(k, !(o[k] ?? on))} />{n}</label>
          ); })}
        </section>
        <section className="pane">
          <header className="pane-head"><h2>Top bar</h2>
            {display.barHidden.length > 0 && <button type="button" onClick={() => setDisplay({ barHidden: [] })}>Show all</button>}</header>
          <p className="muted hint">Right-click an icon on the bar to hide it; right-click the bar anywhere to bring one back.</p>
          <div className="bar-pick">
            {(["left", "right"] as const).map((side) => (
              <div key={side}><span className="muted">{side === "left" ? "Left half" : "Right half"}</span>
                {bar[side].filter(canHide).map((id) => (
                  <label key={id} className="check"><input type="checkbox" checked={!display.barHidden.includes(id)} onChange={(e) => showOnBar(id, e.target.checked)} />{barLabel(id)}</label>
                ))}
              </div>
            ))}
          </div>
        </section>
      </div>
      <div className="star-settings-col">
        {schema.data?.filter((g) => GROUPS.includes(g.name)).map(group)}
        <section className="pane">
          <header className="pane-head"><h2>More</h2></header>
          <div className="row wrap">
            <button type="button" onClick={() => openWindow({ kind: "settings" })}>All settings…</button>
          </div>
        </section>
      </div>
    </div>
  );
}
