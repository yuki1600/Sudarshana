import { useEffect, useLayoutEffect, useRef, useState, useSyncExternalStore } from "react";
import { useQuery } from "@tanstack/react-query";
import { api, currentSettings, onSettings, type Birth } from "./api";
import { chartKey, EMPTY } from "./lifeFacts";
import { useChart, type PanelState } from "./store";

/** The settings, re-rendering when any screen saves them. */
export const useSettings = () => useSyncExternalStore(onSettings, currentSettings);

/** Whether the signed-in account is the owner's: for now only it may pick the Windows layout or the Praajna colours. */
export const useAdmin = () => !!useQuery({ queryKey: ["me"], queryFn: api.me }).data?.admin;

/** useState that survives a refresh: which sub-tab or dasa was open. */
export function useSaved<T extends string>(name: string, first: T) {
  const key = "view." + name;
  const [value, setValue] = useState<T>(() => { try { return (localStorage.getItem(key) as T) || first; } catch { return first; } });
  const jump = useChart((s) => s.jump);
  // used once: a jump left in the store would reopen this sub-tab every time its screen remounts
  useEffect(() => { if (jump?.name === name) { set(jump.value as T); useChart.setState({ jump: null }); } }, [jump?.n]); // eslint-disable-line react-hooks/exhaustive-deps
  // live, as useKept: another screen open now on the same name follows (Starlight's left half follows the Transits sub tab)
  useEffect(() => {
    const on = (e: Event) => { const [n, v] = (e as CustomEvent<[string, T]>).detail; if (n === name) setValue(v); };
    addEventListener("view-saved", on);
    return () => removeEventListener("view-saved", on);
  }, [name]);
  const set = (v: T) => {
    setValue(v);
    try { localStorage.setItem(key, v); } catch { /* private window: this page only */ }
    dispatchEvent(new CustomEvent("view-saved", { detail: [name, v] }));
  };
  return [value, set] as const;
}

/** Sets a useKept value from another screen: a screen open now shows it at once, one opened later reads it. */
export const keep = (name: string, v: unknown) => {
  try { localStorage.setItem("view." + name, JSON.stringify(v)); } catch { /* private window: this page only */ }
  dispatchEvent(new CustomEvent("view-kept", { detail: [name, v] }));
};

/** useSaved for any JSON value (numbers, null, booleans): a pick that a refresh keeps. */
export function useKept<T>(name: string, first: T) {
  const key = "view." + name;
  const [value, setValue] = useState<T>(() => { try { const v = localStorage.getItem(key); return v === null ? first : (JSON.parse(v) as T); } catch { return first; } });
  useEffect(() => {
    const on = (e: Event) => { const [n, v] = (e as CustomEvent<[string, T]>).detail; if (n === name) setValue(v); };
    addEventListener("view-kept", on);
    return () => removeEventListener("view-kept", on);
  }, [name]);
  const set = (v: T) => {
    setValue(v);
    keep(name, v);
  };
  return [value, set] as const;
}

/** How far the page is scaled: the root font-size, which follows the window (styles/base.css), over the 16px the sizes were drawn at. */
export const pageScale = () => parseFloat(getComputedStyle(document.documentElement).fontSize) / 16 || 1;

/** Starlight: the varga of the top left chart (and of the bhava chart beside it), which the chart's tabs on the right follow; a custom research chart, the rasi. */
export function useTopVarga(): number {
  const [charts] = useKept<PanelState[]>("starCharts3", []);
  const spec = Array.isArray(charts) ? charts[0]?.spec : undefined;
  return spec && (spec.kind === "varga" || spec.kind === "bhava") && spec.d ? spec.d : 1;
}

/** Height over width of the box a chart is drawn in: a stretched chart is redrawn to that shape, not squashed. */
export function useShape() {
  const ref = useRef<SVGSVGElement>(null);
  const [k, setK] = useState(1);
  const [px, setPx] = useState(400);    // its width on screen
  // a layout effect, so a chart is measured before its first paint: measured after it, a remounted chart showed one frame drawn square at 400 px
  useLayoutEffect(() => {
    const fit = (width: number, height: number) => { if (width && height) { setK(Math.round(height / width * 1000) / 1000); setPx(Math.round(width)); } };
    const r = ref.current!.getBoundingClientRect();
    fit(r.width, r.height);
    const ro = new ResizeObserver(([e]) => fit(e.contentRect.width, e.contentRect.height));
    ro.observe(ref.current!);
    return () => ro.disconnect();
  }, []);
  return [ref, k, px] as const;
}

/** The Basics data of the current chart; every screen that draws the charts shares it. */
export function useBasics() {
  const { name, birth } = useChart();
  // the last chart stays up until the next one is ready, so a new chart (a mode, a time step) keeps the screen and its forms
  return useQuery({ queryKey: ["basics", birth, name], queryFn: () => api.basics(birth!, name), enabled: !!birth, placeholderData: (p) => p });
}

/** Strengths, houses or KP of the current chart, fetched when the tab that shows them opens. */
export function useView<K extends "strengths" | "houses" | "kp">(kind: K) {
  const birth = useChart((s) => s.birth)!;
  return useQuery({ queryKey: [kind, birth], queryFn: () => api[kind](birth) as Promise<Awaited<ReturnType<(typeof api)[K]>>> });
}

/** The death the Predictions tab keeps ("1950-04-14", "20:47"), as ms, in the birth's zone; noon when no time is given. */
export function deathAt(b: Birth, date: string, time?: string): number {
  const [y, m, d] = date.split("-").map(Number), [hh, mm] = (time || "12:00").split(":").map(Number);
  const t = new Date(0);
  t.setUTCFullYear(y, m - 1, d);
  return t.getTime() + (hh + mm / 60 - b.tz_east_hours) * 3.6e6;
}

/** The Predictions tab's death for this natal chart, from the same cache: its date and its moment (deathAt); null while the person lives. */
export function useDeath(natal: Birth) {
  const chart = chartKey(useChart((s) => s.name), natal);
  const facts = useQuery({ queryKey: ["facts", chart], queryFn: async () => ({ ...EMPTY, ...(await api.facts(chart)).data }) });
  const a = facts.data?.answers ?? {}, date = a["death.date"];
  return a.status === "Dead" && typeof date === "string" ? { date, at: deathAt(natal, date, a["death.time"] as string | undefined) } : null;
}
