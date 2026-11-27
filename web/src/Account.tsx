import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api, currentSettings, saveSettings, type Account, type SavedTheme } from "./api";
import { useKept, useSettings } from "./hooks";
import { useChart, type ChartStyle, type Display } from "./store";
import { recastMode } from "./Modes";
import { Forgot, TermsDialog } from "./Terms";

const BUILT_IN: [Display["layout"], string][] = [["windows", "Windows"], ["starlight", "Starlight"]];
const sorted = (o: object) => JSON.stringify(Object.entries(o).sort(([x], [y]) => (x < y ? -1 : 1)));

/** The theme of what is applied now: the settings, chart style and the look, not this browser's pane split, print choices, address or language. */
export function themeNow(name: string): SavedTheme {
  const { chartStyle, display } = useChart.getState();
  const { split: _s, address: _a, printSections: _p, language: _l, ...look } = display;
  return { name, settings: currentSettings(), chartStyle, display: look };
}

/** A square picture, shrunk to 128 px so it keeps small with the account. */
function shrink(file: File): Promise<string> {
  return new Promise((done, fail) => {
    const img = new Image();
    img.onload = () => {
      const c = document.createElement("canvas"), n = 128, side = Math.min(img.width, img.height);
      c.width = c.height = n;
      c.getContext("2d")!.drawImage(img, (img.width - side) / 2, (img.height - side) / 2, side, side, 0, 0, n, n);
      URL.revokeObjectURL(img.src);
      done(c.toDataURL("image/jpeg", 0.85));
    };
    img.onerror = () => fail(new Error("That file isn't a picture this browser can read."));
    img.src = URL.createObjectURL(file);
  });
}

/** Settings, Account: name and username, password, signing out everywhere, the Terms, deleting the account.
 *  Each part saves on its own button, apart from the Settings screen's Apply. */
export function AccountPanel({ onSignOut, onTheme }: { onSignOut: () => void; onTheme?: () => void }) {
  const client = useQueryClient();
  const { chartStyle, display, setChartStyle, setDisplay } = useChart();
  const settings = useSettings();
  const a = useQuery({ queryKey: ["me"], queryFn: api.me }).data;
  const [terms, setTerms] = useKept("account.terms", false);
  const [note, setNote] = useState<{ part: string; text: string; error?: boolean } | null>(null);
  const [busy, setBusy] = useState("");
  if (!a) return null;

  /** run one part's change; a returned account replaces the one on screen */
  const run = (part: string, done: string, fn: (d: FormData) => Promise<Account | object | void>) => async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const form = e.currentTarget, d = new FormData(form);
    setBusy(part); setNote(null);
    try {
      const r = await fn(d);
      if (r && "email" in r) client.setQueryData(["me"], r);
      if (part === "password") form.reset();
      setNote({ part, text: done });
    } catch (err) { setNote({ part, text: (err as Error).message, error: true }); } finally { setBusy(""); }
  };
  const s = (d: FormData, k: string) => String(d.get(k) ?? "");
  /** a change saved straight away, outside a form */
  const now = (part: string, done: string, fn: () => Promise<Account | void>) => async () => {
    setBusy(part); setNote(null);
    try {
      const r = await fn();
      if (r) client.setQueryData(["me"], r);
      setNote({ part, text: done });
    } catch (err) { setNote({ part, text: (err as Error).message, error: true }); } finally { setBusy(""); }
  };
  const isOn = (t: SavedTheme) => sorted(t.settings) === sorted(settings) && t.chartStyle === chartStyle && t.display.layout === display.layout;
  const on = a.themes.find(isOn);
  const use = (t: SavedTheme) => {
    saveSettings(t.settings);
    setChartStyle(t.chartStyle as ChartStyle);
    const { language: _l, ...look } = t.display as Partial<Display>;     // a theme saved before Settings > Language kept the language too: it stays as chosen
    setDisplay(look);
    client.invalidateQueries();
    recastMode();      // the chart in use stays, cast again with the theme's options
    onTheme?.();
  };
  const Note = ({ part }: { part: string }) => note?.part === part
    ? <p role={note.error ? "alert" : "status"} className={note.error ? "error" : "muted"}>{note.text}</p> : null;

  return (
    <div className="account">
      <form onSubmit={run("profile", "Saved.", (d) => api.saveAccount(s(d, "name"), s(d, "username")))}>
        <h4>Profile</h4>
        <div className="setting account-avatar">
          <span className="avatar" aria-hidden="true">{a.avatar ? <img src={a.avatar} alt="" /> : (a.name.trim()[0] ?? "?").toUpperCase()}</span>
          <label className="button">{a.avatar ? "Change picture" : "Add a picture"}
            <input type="file" accept="image/png,image/jpeg,image/webp" hidden onChange={(e) => {
              const f = e.target.files?.[0];
              e.target.value = "";
              if (f) void now("avatar", "Picture saved.", async () => api.saveAvatar(await shrink(f)))();
            }} />
          </label>
          {a.avatar && <button type="button" disabled={busy === "avatar"} onClick={now("avatar", "Picture removed.", () => api.saveAvatar(null))}>Remove</button>}
        </div>
        <Note part="avatar" />
        <div className="setting"><label htmlFor="acct-name">Name</label><input id="acct-name" name="name" defaultValue={a.name} required maxLength={100} autoComplete="name" /></div>
        <div className="setting"><label htmlFor="acct-username">Username <span className="muted">(optional)</span></label><input id="acct-username" name="username" defaultValue={a.username} maxLength={32} autoComplete="username" /></div>
        <div className="setting"><label htmlFor="acct-email">Email</label><input id="acct-email" value={a.email} readOnly aria-describedby="acct-email-hint" /><p id="acct-email-hint" className="muted hint">To change the email on your account, write to the owner.</p></div>
        <Note part="profile" />
        <menu><button className="primary" disabled={busy === "profile"}>{busy === "profile" ? "Saving…" : "Save"}</button></menu>
      </form>

      <section>
        <h4>Themes</h4>
        <p className="muted">Pick a theme. To make your own, change any settings, then Create theme at the foot of Settings.</p>
        <div className="account-themes" role="group" aria-label="Themes">
          {BUILT_IN.filter(([layout]) => a.admin || layout === "starlight").map(([layout, label]) => (
            <button key={layout} type="button" aria-pressed={!on && display.layout === layout} onClick={() => { setDisplay({ layout }); onTheme?.(); }}>{label}</button>
          ))}
          {a.themes.map((t) => (
            <span key={t.name} className="account-theme">
              <button type="button" aria-pressed={t === on} onClick={() => use(t)}>{t.name}</button>
              <button type="button" className="icon-x" aria-label={`Delete the theme ${t.name}`} disabled={busy === "themes"}
                onClick={() => confirm(`Delete the theme “${t.name}”?`) && void now("themes", "Theme deleted.", () => api.saveThemes(a.themes.filter((x) => x !== t)))()}>×</button>
            </span>
          ))}
        </div>
        <Note part="themes" />
      </section>

      <form onSubmit={run("password", "Password changed. Other devices are signed out.", (d) => {
        if (s(d, "new") !== s(d, "confirm")) throw new Error("The new password and its confirmation don't match.");
        return api.changePassword(s(d, "current"), s(d, "new"));
      })}>
        <h4>{a.hasPassword ? "Change password" : "Set a password"}</h4>
        {!a.hasPassword && <p className="muted">You sign in with Google, Facebook, LinkedIn or Microsoft. A password lets you also sign in with your email.</p>}
        {a.hasPassword && <div className="setting"><label htmlFor="acct-current">Current password</label><input id="acct-current" name="current" type="password" required maxLength={256} autoComplete="current-password" /></div>}
        <div className="setting"><label htmlFor="acct-new">New password</label><input id="acct-new" name="new" type="password" required minLength={8} maxLength={256} autoComplete="new-password" aria-describedby="acct-new-hint" /><p id="acct-new-hint" className="muted hint">At least 8 characters.</p></div>
        <div className="setting"><label htmlFor="acct-confirm">Confirm new password</label><input id="acct-confirm" name="confirm" type="password" required minLength={8} maxLength={256} autoComplete="new-password" /></div>
        {a.hasPassword && <p className="muted hint">Forgot your current password? <Forgot /></p>}
        <Note part="password" />
        <menu><button className="primary" disabled={busy === "password"}>{busy === "password" ? "Saving…" : a.hasPassword ? "Change password" : "Set password"}</button></menu>
      </form>

      <section>
        <h4>Signed-in devices</h4>
        <p className="muted">Sign out of Sudarshana on every browser and device, this one included.</p>
        <menu><button type="button" onClick={async () => { await api.signOutEverywhere().catch(() => {}); onSignOut(); }}>Sign out everywhere</button></menu>
      </section>

      <section>
        <h4>Terms of Service</h4>
        <p className="muted">The terms you agreed to, including how your data is kept.</p>
        <menu><button type="button" onClick={() => setTerms(true)}>Read the Terms</button></menu>
        <TermsDialog open={terms} onClose={() => setTerms(false)} />
      </section>

      <form className="account-danger" onSubmit={run("delete", "", async (d) => {
        if (!confirm("Delete your account and every chart saved with it? This can't be undone.")) throw new Error("Nothing was deleted.");
        await api.deleteAccount(s(d, "password"));
        onSignOut();
      })}>
        <h4>Delete account</h4>
        <p className="muted">Deletes your account, your saved charts, life events and sign-ins, at once and for good.</p>
        {a.hasPassword && <div className="setting"><label htmlFor="acct-delete-pw">Password</label><input id="acct-delete-pw" name="password" type="password" required maxLength={256} autoComplete="current-password" /></div>}
        <Note part="delete" />
        <menu><button className="danger" disabled={busy === "delete"}>{busy === "delete" ? "Deleting…" : "Delete account"}</button></menu>
      </form>
    </div>
  );
}
