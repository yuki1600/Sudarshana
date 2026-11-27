/** This browser's localStorage (open charts, recents, settings, what is on screen), kept with the signed-in account on the
 *  server too (/api/auth/state, in accounts.db), so another browser or Mac opens where the last one left off. Every module
 *  still reads and writes localStorage as before: pull() fills it from the account before the app's modules load, and
 *  every write after that is sent on. */

const OWNER = "kept.owner";   // the account this browser's localStorage belongs to; never sent
const BATCH = 2 ** 20;        // characters one request carries at most (the server takes 2 MB)

type Changes = Record<string, string | null>;   // null: removed
export interface Plan { clear: boolean; set: Record<string, string>; upload: Record<string, string> }

/** The account's values win. Keys only this browser has go up when the browser was this account's, or no one's yet
 *  (the first sign-in after this was added); another account's storage is wiped first, so nothing of it carries over. */
export function plan(local: Record<string, string>, server: Record<string, string>, owner: string | null, user: string): Plan {
  const clear = owner !== null && owner !== user;
  const upload: Record<string, string> = {};
  if (!clear) for (const [k, v] of Object.entries(local)) if (k !== OWNER && !(k in server)) upload[k] = v;
  const set = Object.fromEntries(Object.entries(server).filter(([k, v]) => clear || local[k] !== v));
  return { clear, set, upload };
}

let on = false;   // sending, once pull() found a signed-in account
let me = "";      // that account: what this page sends goes to it alone
let pending = new Map<string, string | null>();
let timer: ReturnType<typeof setTimeout> | undefined;
let chain = Promise.resolve();   // one request at a time, so a key's later value never lands before its earlier one
let raw: { set: (k: string, v: string) => void; clear: () => void } | null = null;

function watch() {
  if (raw) return;
  const proto = Storage.prototype, setItem = proto.setItem, removeItem = proto.removeItem, clear = proto.clear;
  raw = { set: (k, v) => setItem.call(localStorage, k, v), clear: () => clear.call(localStorage) };
  const note = (s: Storage, k: string, v: string | null) => {
    if (!on || k === OWNER || s !== localStorage) return;
    pending.set(k, v);
    clearTimeout(timer);
    timer = setTimeout(() => void flush(), 500);
  };
  proto.setItem = function (k: string, v: string) { setItem.call(this, k, v); note(this, k, String(v)); };
  proto.removeItem = function (k: string) { removeItem.call(this, k); note(this, k, null); };
  addEventListener("pagehide", () => void flush(true));
  // another tab signed in as another account (it wiped this storage and took it over): this page's charts are the old one's
  addEventListener("storage", (e) => {
    if (on && (e.key === OWNER || e.key === null) && localStorage.getItem(OWNER) !== me) { on = false; pending = new Map(); location.reload(); }
  });
  document.addEventListener("visibilitychange", () => { if (document.visibilityState === "hidden") void flush(true); });
}

async function send(all: [string, string | null][], keepalive: boolean) {
  for (let i = 0; i < all.length;) {
    const batch: Changes = {};
    for (let n = 0; i < all.length && (n === 0 || n + all[i][0].length + (all[i][1]?.length ?? 0) < BATCH); i++) {
      batch[all[i][0]] = all[i][1];
      n += all[i][0].length + (all[i][1]?.length ?? 0);
    }
    const body = JSON.stringify({ changes: batch, user: Number(me) });
    // keepalive lets a closing page's last changes through, but only for a body under 64 KB
    const r = await fetch("/api/auth/state", { method: "PUT", headers: { "Content-Type": "application/json" }, body,
      keepalive: keepalive && body.length < 60_000 }).catch(() => null);
    if (!r || r.status >= 500)   // offline or the server restarting: they go again with the next change
      for (const [k, v] of Object.entries(batch)) if (!pending.has(k)) pending.set(k, v);
    // a 4xx (signed out, too much) is dropped: this browser still has it
  }
}

/** Send what changed now: closing the page sends at once, otherwise after the requests already on their way. */
export function flush(closing = false): Promise<void> {
  clearTimeout(timer);
  if (!pending.size) return chain;
  const all = [...pending];
  pending = new Map();
  if (closing) return send(all, true);
  return (chain = chain.then(() => send(all, false)));
}

/** Signing out: send what is left, then stop sending until the next pull(). */
export async function leave() {
  await flush();
  on = false;
}

/** Bring this browser's localStorage in line with the signed-in account's; true when it changed what the app would read. */
export async function pull(): Promise<boolean> {
  let got: { user: number; data: Record<string, string> } | null = null;
  try {
    const r = await fetch("/api/auth/state", { cache: "no-store" });
    if (r.ok) got = await r.json();
  } catch { /* server unreachable: this browser's copy */ }
  if (!got) return false;   // signed out
  try {
    watch();
    const p = plan({ ...localStorage }, got.data, localStorage.getItem(OWNER), String(got.user));
    if (p.clear) raw!.clear();
    for (const [k, v] of Object.entries(p.set)) raw!.set(k, v);
    raw!.set(OWNER, String(got.user));
    me = String(got.user);
    on = true;
    for (const [k, v] of Object.entries(p.upload)) pending.set(k, v);
    void flush();
    return p.clear || Object.keys(p.set).length > 0;
  } catch {
    return false;   // storage blocked (a private window): nothing to keep
  }
}
