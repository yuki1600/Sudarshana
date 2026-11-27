/** Settings > Language on the page: the text the app draws, and its labels and hover texts, put into the chosen language as
 *  they land (a translator of the app's own over the DOM; translate.ts and languageWords.ts have the words). React keeps
 *  writing English and the data stays English: this only changes a text's value or an attribute, never the page's
 *  structure, so every node stays React's own. Left as they are: anything inside translate="no" (a chart's or a person's
 *  name, the list of languages itself), what is typed, code, and sentences the tables don't have. The charts' labels are
 *  names.ts's own, so their boxes are laid out on what they show. Started by main.tsx before the app's first render. */
import { useSyncExternalStore } from "react";
import { useChart } from "./store";
import { codeOf, languageOf, translate, type Code, type LanguageId, type Words } from "./translate";

let shown: LanguageId = "English";      // the language on the page, its words loaded
let words: Words | null = null;
const listeners = new Set<() => void>();
const listen = (f: () => void) => { listeners.add(f); return () => { listeners.delete(f); }; };
/** The language on the page: a component that translates its own text (one that measures it) renders again when it changes. */
export const useLanguage = () => useSyncExternalStore(listen, () => shown);

const cache = new Map<string, string>();
const back = new Map<string, string>();     // a translation to its English: a value copied from one attribute to another (ui.tsx IconTips: title to data-tip)
/** ``s`` in the language on the page: itself in English, or where the tables don't have it. */
export function tr(s: string): string {
  if (!words || !/[A-Za-z]/.test(s)) return s;
  let out = cache.get(s);
  if (out === undefined) {
    out = translate(words, s);
    if (cache.size > 30000) { cache.clear(); back.clear(); }
    cache.set(s, out);
    if (out !== s) back.set(out, s);
  }
  return out;
}

const ATTRS = ["title", "aria-label", "data-tip", "placeholder", "alt"];
// the page's own <html translate="no"> aside: that one tells the browser's translator the page translates itself
const KEEP = "script, style, textarea, pre, code, [contenteditable]:not([contenteditable='false']), :not(html)[translate='no']";
const texts = new WeakMap<Text, [string, string]>();     // a text's English, and what was written into it
const attrs = new WeakMap<Element, Map<string, [string, string]>>();
const pinned = new WeakSet<Element>();                    // an <option> given its English as its value

function text(n: Text, checked = false) {
  const p = n.parentElement;
  if (!p) return;
  const now = n.data, had = texts.get(n);
  const en = had && had[1] === now ? had[0] : now;
  let out = en;
  if (p.tagName === "SUP" && p.parentElement?.classList.contains("ord")) out = words ? "" : en;     // 12<sup>th</sup> (ui.tsx supOrd): the number alone
  else if (words && (checked || !p.closest(KEEP))) out = tr(en);
  // an option with no value has its text for one: the English stays there, or its select stops matching it
  if (p.tagName === "OPTION" && out !== en && p.childNodes.length === 1 && (pinned.has(p) || !p.hasAttribute("value"))) { pinned.add(p); p.setAttribute("value", en); }
  if (out !== now) n.data = out;
  texts.set(n, [en, out]);
}

function attr(el: Element, a: string, checked = false) {
  const now = el.getAttribute(a);
  if (now === null) return;
  let kept = attrs.get(el);
  const had = kept?.get(a);
  const en = had && had[1] === now ? had[0] : back.get(now) ?? now;
  const out = words && (checked || !el.closest(KEEP)) ? tr(en) : en;
  if (out !== now) el.setAttribute(a, out);
  if (!kept) attrs.set(el, (kept = new Map()));
  kept.set(a, [en, out]);
}

/** The raised endings of supOrd's ordinals, inside its translate="no" span. */
const ordinals = (el: Element) => {
  for (const o of el.classList.contains("ord") ? [el] : el.querySelectorAll(".ord"))
    for (const sup of o.querySelectorAll("sup")) for (const c of sup.childNodes) if (c.nodeType === Node.TEXT_NODE) text(c as Text);
};

/** Every text and label under ``root``, as it is now. */
function walk(root: Node) {
  if (root.nodeType === Node.TEXT_NODE) return text(root as Text);
  if (root.nodeType !== Node.ELEMENT_NODE) return;
  const top = root as Element;
  if (top.closest(KEEP)) { ordinals(top); return; }
  for (const a of ATTRS) if (top.hasAttribute(a)) attr(top, a, true);
  const walker = document.createTreeWalker(top, NodeFilter.SHOW_ELEMENT | NodeFilter.SHOW_TEXT, {
    acceptNode: (n) => {
      if (n.nodeType === Node.TEXT_NODE || !(n as Element).matches(KEEP)) return NodeFilter.FILTER_ACCEPT;
      ordinals(n as Element);
      return NodeFilter.FILTER_REJECT;     // and all inside it
    },
  });
  for (let n = walker.nextNode(); n; n = walker.nextNode()) {
    if (n.nodeType === Node.TEXT_NODE) text(n as Text, true);
    else for (const a of ATTRS) if ((n as Element).hasAttribute(a)) attr(n as Element, a, true);
  }
}

const observer = new MutationObserver((records) => {
  for (const r of records) {
    if (r.type === "childList") r.addedNodes.forEach((n) => { if (n.isConnected) walk(n); });
    else if (r.type === "characterData") { if (r.target.isConnected) text(r.target as Text); }
    else if (r.attributeName) attr(r.target as Element, r.attributeName);
  }
  observer.takeRecords();     // the writes just made
});

let asked: LanguageId = "English";
async function show(id: LanguageId) {
  asked = id;
  const next = id === "English" ? null : (await import("./languageWords")).wordsFor(codeOf(id) as Code);
  if (asked !== id) return;     // another was picked while these loaded
  words = next;
  shown = id;
  cache.clear();
  const html = document.documentElement;
  html.lang = codeOf(id);
  if (id === "English") html.removeAttribute("translate"); else html.setAttribute("translate", "no");
  walk(document.body);
  observer.takeRecords();
  listeners.forEach((f) => f());
}

/** Puts the page into the kept language and follows Settings' changes of it; main.tsx waits for it, so the first render is in the language. */
export async function startLanguage() {
  observer.observe(document.body, { subtree: true, childList: true, characterData: true, attributes: true, attributeFilter: ATTRS });
  useChart.subscribe((s, p) => { if (s.display.language !== p.display.language) void show(languageOf(s.display.language)); });
  await show(languageOf(useChart.getState().display.language));
}
