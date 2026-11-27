import { useEffect, useRef } from "react";
import { backdropClose } from "./ChartDialogs";

const CREDITS: [string, string, string][] = [
  ["Swiss Ephemeris", "https://www.astro.com/swisseph/", "Graha positions, by Astrodienst AG (Dieter Koch and Alois Treindl), through pyswisseph."],
  ["GeoNames", "https://www.geonames.org/", "The places atlas: names, coordinates and time zones (CC BY 4.0)."],
  ["IANA Time Zones", "https://www.iana.org/time-zones", "Historical time-zone and daylight-saving rules."],
  ["Natural Earth", "https://www.naturalearthdata.com/", "The world map in Astrocartography and Mundane (public domain)."],
  ["NOAA NCEI", "https://www.ncei.noaa.gov/", "Earthquake, tsunami and volcano records in Mundane."],
  ["Tabler Icons", "https://tabler.io/icons", "Some of the icons (MIT)."],
  ["three.js", "https://threejs.org/", "The opening animation (MIT)."],
  ["React, TanStack, Zustand, Vite", "https://react.dev/", "The open-source tools the app is built with."],
];

/** The chakra emblem: serrated rim, spokes, hub. */
export function Emblem() {
  const teeth = Array.from({ length: 24 }, (_, i) => {
    const a = (i / 24) * Math.PI * 2, b = a + Math.PI / 24, c = a + Math.PI / 12;
    const p = (r: number, t: number) => `${(32 + r * Math.cos(t)).toFixed(2)} ${(32 + r * Math.sin(t)).toFixed(2)}`;
    return `${i ? "L" : "M"}${p(26, a)} L${p(30, b)} L${p(26, c)}`;
  }).join(" ") + "Z";
  return (
    <svg className="about-emblem" viewBox="0 0 64 64" aria-hidden="true">
      <path d={teeth} />
      <circle cx="32" cy="32" r="21" />
      {Array.from({ length: 16 }, (_, i) => {
        const a = (i / 16) * Math.PI * 2;
        return <line key={i} x1={32 + 6 * Math.cos(a)} y1={32 + 6 * Math.sin(a)} x2={32 + 21 * Math.cos(a)} y2={32 + 21 * Math.sin(a)} />;
      })}
      <circle cx="32" cy="32" r="5" />
    </svg>
  );
}

/** The credits: the vision and creator, the inspiration, and the data and software it stands on. */
export function About({ open, onClose }: { open: boolean; onClose: () => void }) {
  const ref = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    const d = ref.current;
    if (open && d && !d.open) d.showModal(); else if (!open && d?.open) d.close();
  }, [open]);

  return (
    <dialog ref={ref} className="dialog about" onClose={onClose} onClick={backdropClose} aria-labelledby="about-title">
      <header className="about-hero">
        <Emblem />
        <h2 id="about-title">Sudarshana</h2>
        <p lang="sa">सुदर्शन</p>
      </header>

      <section className="about-vision">
        <p>Sudarshana brings the full depth of classical Jyotisha to a modern app that is fast and clear.
          Every calculation follows the classical texts, so a student or a practitioner can see the whole chart, and the reasoning behind it, at a glance.</p>
        <a className="about-creator" href="https://www.linkedin.com/in/yuktesh-b-aa4a801a5/" target="_blank" rel="noreferrer">
          <span className="about-avatar" aria-hidden="true">YB</span>
          <span><small>Vision and creation</small><strong>Yuktesh B</strong></span>
          <span className="about-link">LinkedIn ↗</span>
        </a>
      </section>

      <section className="about-tribute">
        <small>Honourable mention</small>
        <p><strong>P.V.R. Narasimha Rao</strong>, creator of <a href="https://www.vedicastrologer.org/jh/" target="_blank" rel="noreferrer">Jagannatha Hora</a>.
          His software and teaching have been the inspiration for this one.</p>
      </section>

      <section>
        <h3>Built on</h3>
        <ul className="credits">
          {CREDITS.map(([name, url, what]) => (
            <li key={name}><a href={url} target="_blank" rel="noreferrer">{name}</a><span>{what}</span></li>
          ))}
        </ul>
      </section>
    </dialog>
  );
}
