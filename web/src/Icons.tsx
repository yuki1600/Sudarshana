import { Fragment } from "react";
/** Stroke icons on a 24x24 grid: the path data of each, drawn in currentColor.
 *  Remedies / Calculations / Home from Tabler Icons (MIT): om + tool/spanner + home. */
const PATHS = {
  Chakras: "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18zM12 3v18M3 12h18M5.6 5.6l12.8 12.8M18.4 5.6L5.6 18.4",
  Home: "M5 12H3l9-9 9 9h-2M5 12v7a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-7M9 21v-6a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v6",
  // Tabler Icons outline/barbell.svg (a dumbbell) — MIT https://tabler.io/icons/icon/barbell
  Strengths: "M2 12h1M6 8H4a1 1 0 0 0-1 1v6a1 1 0 0 0 1 1h2M6 7v10a1 1 0 0 0 1 1h1a1 1 0 0 0 1-1V7a1 1 0 0 0-1-1H7a1 1 0 0 0-1 1zM9 12h6M15 7v10a1 1 0 0 0 1 1h1a1 1 0 0 0 1-1V7a1 1 0 0 0-1-1h-1a1 1 0 0 0-1 1zM18 8h2a1 1 0 0 1 1 1v6a1 1 0 0 1-1 1h-2M22 12h-1",
  Dasas: "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18zM12 7v5l3.5 2",
  Transits: "M19.66 8.69A9 9 0 1 1 15.3 4.35M17.86 3.54a2.6 2.6 0 1 0 0 5.2 2.6 2.6 0 0 0 0-5.2zM11.5 9.7a2.8 2.8 0 1 0 0 5.6 2.8 2.8 0 0 0 0-5.6z",
  Predictions: "M8 19V5h5a4 4 0 0 1 0 8H8",   // a P
  Timeline: "M4 7a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2zM16 3v4M8 3v4M4 11h16M8 14.5h.01M12 14.5h.01M16 14.5h.01M8 17.5h.01M12 17.5h.01",   // a calendar: the tab is a year of the sky
  Longevity: "M6 3h12M6 21h12M7 3v4l5 5 5-5V3M7 21v-4l5-5 5 5v4",
  Tajaka: "M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8zM12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M4.9 19.1L7 17M17 7l2.1-2.1",
  "Tithi Pravesha": "M20 14.5A8.5 8.5 0 0 1 9.5 4 8.5 8.5 0 1 0 20 14.5z",
  Astrocartography: "M13.2 5.5L9 4 3 6.5v13L9 17l6 2.5 6-2.5v-4.2M9 4v13M15 12.6v6.9M17.5 2.5a3.7 3.7 0 0 0-3.7 3.7c0 2.6 3.7 6.1 3.7 6.1s3.7-3.5 3.7-6.1a3.7 3.7 0 0 0-3.7-3.7zM17.5 5.2a1 1 0 1 0 0 2 1 1 0 0 0 0-2z",
  // Tabler Icons outline/yin-yang.svg — MIT https://tabler.io/icons/icon/yin-yang
  Traditions: "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18zM12 3a4.5 4.5 0 0 0 0 9 4.5 4.5 0 0 1 0 9M12 7a.5.5 0 1 0 0 1 .5.5 0 0 0 0-1zM12 16a.5.5 0 1 0 0 1 .5.5 0 0 0 0-1z",
  Finance: "M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6",
  Matching: "M12 21s-7.5-4.6-9.5-9A5.2 5.2 0 0 1 12 6.2 5.2 5.2 0 0 1 21.5 12c-2 4.4-9.5 9-9.5 9z",
  Muhurta: "M2 16h20M6 16a6 6 0 0 1 12 0M12 4.5V7.5M4.6 8.6l1.8 1.8M19.4 8.6l-1.8 1.8M7 20h10",   // the sun on the horizon: the day runs sunrise to sunrise
  // Tabler Icons outline/om.svg — MIT https://tabler.io/icons/icon/om
  Remedies: "M7 12c2.21 0 4-1.567 4-3.5S9.21 5 7 5c-1.594 0-2.97.816-3.613 2M3.423 14.483A4.944 4.944 0 0 0 3 16.5C3 18.985 4.79 21 7 21s4-2.015 4-4.5-1.79-4.5-4-4.5M14.071 17.01c.327 2.277 1.739 3.99 3.429 3.99 1.933 0 3.5-2.239 3.5-5s-1.567-5-3.5-5c-.96 0-1.868.606-2.5 1.5-.717 1.049-1.76 1.7-2.936 1.7-.92 0-1.766-.406-2.434-1.087M17 3l2 2M12 3c1.667 3.667 4.667 5.333 9 5",
  // Tabler Icons outline/tool.svg (spanner) — MIT https://tabler.io/icons/icon/tool
  Calculations: "M7 10h3v-3l-3.5-3.5a6 6 0 0 1 8 8l6 6a2 2 0 0 1-3 3l-6-6a6 6 0 0 1-8-8l3.5 3.5",
  Research: "M10.5 3a7.5 7.5 0 1 0 0 15 7.5 7.5 0 0 0 0-15zM21 21l-5.2-5.2M7.5 13.5v-2.5M10.5 13.5V7.5M13.5 13.5v-4",   // a magnifier over bars: searching the records for patterns
  Mundane: "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18zM3 12h18M4.2 7.5h15.6M4.2 16.5h15.6M12 3c2.6 2.7 3.9 5.7 3.9 9s-1.3 6.3-3.9 9c-2.6-2.7-3.9-5.7-3.9-9s1.3-6.3 3.9-9z",
  new: "M12 5v14M5 12h14",
  open: "M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z",
  save: "M12 4v11M7.5 10.5L12 15l4.5-4.5M5 19h14",
  edit: "M4 20h4L19 9l-4-4L4 16zM13.5 6.5l4 4",
  insights: "M12 2.5Q13 11 21.5 12Q13 13 12 21.5Q11 13 2.5 12Q11 11 12 2.5z",   // a four-point sparkle
  prev: "M15 5l-7 7 7 7",
  next: "M9 5l7 7-7 7",
  undo: "M9 14L4 9l5-5M4 9h10.5a5.5 5.5 0 0 1 0 11H11",
  down: "M5 9l7 7 7-7",
  natal: "M7 19V5l10 14V5",
  ayanamsa: "M6 20l6-16 6 16M8.4 14h7.2",
  plus: "M12 5v14M5 12h14",
  minus: "M5 12h14",
  pin: "M12 2.5a7 7 0 0 0-7 7c0 5 7 12 7 12s7-7 7-12a7 7 0 0 0-7-7zM12 7a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5z",
  matching: "M8.5 11a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7zM2 20c0-3.3 2.7-6 6.5-6S15 16.7 15 20M16 4.3a3.5 3.5 0 0 1 0 6.4M18 14.4c2 .8 3.5 2.7 3.5 5.6",
  print: "M7 9V3h10v6M7 17H5a2 2 0 0 1-2-2v-4a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v4a2 2 0 0 1-2 2h-2M7 14h10v7H7z",
  light: "M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8zM12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4",
  dark: "M20 14.5A8.5 8.5 0 0 1 9.5 4 8.5 8.5 0 1 0 20 14.5z",
  settings: "M12 9a3 3 0 1 0 0 6 3 3 0 0 0 0-6zM19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z",
  fontUp: "M2 19L8 5l6 14M4.5 14h7M19 5v6M16 8h6",
  fontDown: "M2 19L8 5l6 14M4.5 14h7M16 8h6",
  list: "M4 6h16M4 12h16M4 18h16",
  spanner: "M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.8-3.8a6 6 0 0 1-7.9 7.9l-6.9 6.9a2.1 2.1 0 0 1-3-3l6.9-6.9a6 6 0 0 1 7.9-7.9z",
  house: "M3 11l9-8 9 8M5 10v10h14V10M10 20v-6h4v6",
  layers: "M12 3l9 5-9 5-9-5zM3 13l9 5 9-5",
  star: "M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z",
  info: "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18zM12 11v6M12 7.5v.01",
  chartsMany: "M4 4h7v5H4zM13 4h7v5h-7zM4 10h7v5H4zM13 10h7v5h-7zM4 16h7v4H4zM13 16h7v4h-7z",
  charts4: "M4 4h7v7H4zM13 4h7v7h-7zM4 13h7v7H4zM13 13h7v7h-7z",
  chartsFew: "M5 3h14v8H5zM5 13h14v8H5z",
  close: "M6 6l12 12M18 6L6 18",
  search: "M11 4a7 7 0 1 0 0 14 7 7 0 0 0 0-14zM20 20l-4-4",
  share: "M18 2.5a3 3 0 1 0 0 6 3 3 0 0 0 0-6zM6 9a3 3 0 1 0 0 6 3 3 0 0 0 0-6zM18 15.5a3 3 0 1 0 0 6 3 3 0 0 0 0-6zM8.6 13.5l6.8 4M15.4 6.5l-6.8 4",
  trash: "M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13M10 11v6M14 11v6",
  signOut: "M14 8V6a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h7a2 2 0 0 0 2-2v-2M9 12h12M18 9l3 3-3 3",
  lightning: "M13 2L4.5 13.5h6.2L9.2 22 19.5 10.5h-6.5L13 2z",
  hand: "M8 13V7.5a1.5 1.5 0 0 1 3 0V12M11 11.5V6a1.5 1.5 0 0 1 3 0v6M14 11V8a1.5 1.5 0 0 1 3 0v8.2a4.8 4.8 0 0 1-4.8 4.8h-1a6 6 0 0 1-5.3-3.2L5.2 14a1.6 1.6 0 0 1 2.3-2.2L8 13",
  percent: "M19 5L5 19M8 8.5a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5zM16 20.5a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5z",
  now: "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18zM12 7v5l3.2 2",   // a clock: back to the present moment
  fast: "M6 12l6-6 6 6M6 18l6-6 6 6",   // two arrow tips up
  slow: "M6 6l6 6 6-6M6 12l6 6 6-6",    // two arrow tips down
} as const;

export type IconName = keyof typeof PATHS;

export function Icon({ name }: { name: IconName }) {
  return (
    <svg className="icon" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
      <path d={PATHS[name]} />
    </svg>
  );
}

/** A chart Cast + opened on its own is named "Tajaka-2026-Name" (so its saves and files still say what it is) and drawn with
 *  its page's icon for the word: the Sun for Tajaka, the Moon for Tithi Pravesha, the Transits logo. Cast from a cast chart,
 *  the layers stack, the newest first: the Tajaka of the 2026 transit chart is "Tajaka-2027-Transit-2026-Name". */
const CAST_LAYER = /^(Tajaka|Tithi Pravesha|Transit|Jamakkol)-(\d+)-(.+)$/s;

/** The name for a chart cast from the chart named ``name``. */
export const castName = (kind: string, year: number, name: string) => `${kind}-${year}-${name}`;

/** A chart's name as shown: each cast layer its kind and year, one "of" the next, then the name: "Tajaka - 2027 of Transit - 2026 - Name". */
export function ChartName({ name }: { name: string }) {
  const layers: [string, string][] = [];
  let rest = name, m: RegExpMatchArray | null;
  while ((m = rest.match(CAST_LAYER))) { layers.push([m[1], m[2]]); rest = m[3]; }
  // the person's name as written, never put into Settings > Language's language (a "Rohini" is a name, not the nakshatra)
  if (!layers.length) return <span translate="no">{name}</span>;
  return <>{layers.map(([kind, year], i) => (
    <Fragment key={i}>{i > 0 && " of "}{kind} - {year}</Fragment>
  ))} - <span translate="no">{rest}</span></>;
}

/** The kind of a cast chart shown over a chart (its pill): Tajaka and Tithi Pravesha by their event kind, a transit by its title. */
export function castKind(mode: { title: string; event?: { kind: number } }): string | undefined {
  return mode.title === "Transit" ? "Transit" : mode.event?.kind === 1 ? "Tajaka" : mode.event?.kind === 2 ? "Tithi Pravesha" : undefined;
}
