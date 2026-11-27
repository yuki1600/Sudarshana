import { useEffect, useRef } from "react";
import { design, R, TAU, TIP, type Pt, type Shape } from "./chakra";

/** First-run intro, about 4s, drawn with the plain Canvas 2D API (no library, no WebGL). The Sudarshana Chakra
 *  blooms out from its hub, its lines brightening as it opens, and stops at the chakra's edge; the wheel turns at one steady
 *  speed throughout, its glow growing with it and flaring as it completes. The name opens out from the hub the same way, each letter lit gold as
 *  it is uncovered before it settles to black with a pale-gold glow round it. Then a second ring runs out past the
 *  corners of the page, and the overlay is cut away behind it so the home page shows through as it passes.
 *
 *  The chakra is crisp line art (curved flame-blades round a rim of 108 navamsa padas, a twisted cord, a hexagram, 12 rasi spokes, a lotus, the
 *  hub) with a soft glow and a dusting of fine glints along its lines. It is drawn once into an offscreen picture;
 *  each frame shows it through a soft-edged disc widening from the hub. The name is drawn on the canvas too, so its
 *  letters (not its line boxes) are centred on the hub. */

const LEAD = 0.2;                     // seconds of dark, from the first frame, before the bloom begins
const REVEAL = [0.12, 3.3];           // seconds: the reveal travels slowly from the hub out to the edge of the chakra and stops there
const FLASH = 3.2;                    // the glow flares about when the wave reaches the blade tips and the wheel is whole
const NAME_IN = [3.2, 3.85];           // seconds: the name opens out from the hub as the wheel comes whole
const PULSE = [4.45, 5.0];             // seconds, brisk: a second ring of light runs out past the page corners, opening the overlay to the home page behind it
const TURN = 0.15;                    // radians a second the wheel turns, uniformly, the whole time
const SPEED = 1.2;                    // the timings below are in intro seconds; this many pass each real second
const GLINTS = 20000;                 // fine glints along the lines
/** The name, drawn on the canvas at the hub: its text and its font for a given number of device px per world unit. */
const NAME: [string, (u: number) => string][] = [
  ["Sudarshana", (u) => `600 ${0.3 * u}px Georgia, "Times New Roman", serif`],   // a title over the wheel, about half the rim's width
  ["सुदर्शन", (u) => `${0.17 * u}px system-ui, -apple-system, "Segoe UI", sans-serif`],
];
const VIEW = 6.63;                    // glint sizes were tuned for this many world units top to bottom
const SHADES = 8, CELL = 32;          // the glint atlas: gold from deep to pale

/** Points along the lines, picked by vertex so dense outlines get more of them; seeded, so the picture is the same every time. */
function glintsAlong(shapes: Shape[]) {
  let seed = 7;
  const rand = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
  const verts = shapes.flatMap((sh) => sh.pts.map((p, i) => [p, sh.pts[(i + 1) % sh.pts.length]] as [Pt, Pt]));
  return Array.from({ length: GLINTS }, () => {
    const [a, b] = verts[Math.floor(rand() * verts.length)], t = rand();
    return { x: a[0] + (b[0] - a[0]) * t, y: a[1] + (b[1] - a[1]) * t, size: 7 + rand() * 7, shade: rand() };
  });
}

/** A soft glow per shade of gold on one sheet, for the glints. */
function atlas() {
  const c = document.createElement("canvas");
  c.width = SHADES * CELL; c.height = CELL;
  const ctx = c.getContext("2d")!, h = CELL / 2;
  for (let i = 0; i < SHADES; i++) {
    const f = i / (SHADES - 1), rgb = `255,${Math.round(159 + 81 * f)},${Math.round(46 + 146 * f)}`;   // #ff9f2e to #fff0c0
    const g = ctx.createRadialGradient(i * CELL + h, h, 0, i * CELL + h, h, h);
    g.addColorStop(0, `rgba(${rgb},.7)`); g.addColorStop(0.5, `rgba(${rgb},.3)`); g.addColorStop(1, `rgba(${rgb},0)`);
    ctx.fillStyle = g; ctx.fillRect(i * CELL, 0, CELL, CELL);
  }
  return c;
}

export default function Intro({ onDone }: { onDone: () => void }) {
  const host = useRef<HTMLDivElement>(null);
  const done = useRef(onDone);
  done.current = onDone;

  useEffect(() => {
    const el = host.current!, canvas = document.createElement("canvas"), ctx = canvas.getContext("2d");
    if (!ctx) { done.current(); return; }
    el.appendChild(canvas);

    const shapes = design(), sheet = atlas(), glints = glintsAlong(shapes);
    const art = document.createElement("canvas"), actx = art.getContext("2d")!;
    const shown = document.createElement("canvas"), sctx = shown.getContext("2d")!;   // the art through this frame's mask
    const title = document.createElement("canvas"), tctx = title.getContext("2d")!;   // the name, painted once per size
    const titled = document.createElement("canvas"), dctx = titled.getContext("2d")!;   // the name through this frame's mask

    let scale = 1, cx = 0, cy = 0, half = 0, dpr = 1, sealed = false;   // sealed: the reveal is whole and its mask kept
    /** The whole chakra, once per size: fills, then the lines with a glow, then the lines again crisp, then glints. */
    const paint = () => {
      art.width = art.height = shown.width = shown.height = half * 2;
      sealed = false;
      const P = ([x, y]: Pt): Pt => [half + x * scale, half - y * scale];
      const gold = actx.createRadialGradient(half, half, 0, half, half, TIP * scale);
      gold.addColorStop(0, "#fff2c8"); gold.addColorStop(0.45, "#ffc766"); gold.addColorStop(0.8, "#ffb14a"); gold.addColorStop(1, "#f08c2a");
      const trace = (sh: Shape) => {
        actx.beginPath();
        sh.pts.forEach((p, i) => (i ? actx.lineTo(...P(p)) : actx.moveTo(...P(p))));
        if (sh.closed) actx.closePath();
      };
      actx.lineJoin = actx.lineCap = "round";
      actx.fillStyle = gold;
      for (const sh of shapes) if (sh.fill) { trace(sh); actx.globalAlpha = sh.fill; actx.fill(); }
      actx.strokeStyle = "#ffdc93";
      // the lines four times: a broad amber bloom, a wide amber glow, a tighter bright one, then crisp; the glows scale with the wheel
      const passes: [string, number, number][] = [["rgba(255,150,40,.95)", 0.2, 0.9], ["rgba(255,165,55,1)", 0.1, 1], ["rgba(255,225,150,1)", 0.04, 1], ["transparent", 0, 1]];
      for (const [color, blur, alpha] of passes) {
        actx.shadowColor = color;
        actx.shadowBlur = blur * scale;
        for (const sh of shapes) { trace(sh); actx.globalAlpha = sh.ink * alpha; actx.lineWidth = Math.max(0.6, sh.line * scale); actx.stroke(); }
      }
      actx.shadowBlur = 0;
      actx.globalAlpha = 1;
      actx.globalCompositeOperation = "lighter";
      for (const g of glints) {
        const d = (g.size * scale * VIEW) / 7200, [x, y] = P([g.x, g.y]);
        actx.drawImage(sheet, Math.min(SHADES - 1, Math.floor(g.shade * SHADES)) * CELL, 0, CELL, CELL, x - d / 2, y - d / 2, d, d);
      }
      actx.globalCompositeOperation = "source-over";
    };
    const resize = () => {
      const w = el.clientWidth, h = el.clientHeight;
      dpr = Math.min(devicePixelRatio, 2);
      canvas.width = w * dpr; canvas.height = h * dpr;
      canvas.style.width = `${w}px`; canvas.style.height = `${h}px`;
      // the chakra centred, its blade tips filling most of the shorter side
      scale = ((Math.min(w, h) * 0.86) / (2 * TIP)) * dpr;   // device pixels per world unit
      cx = (w * dpr) / 2; cy = (h * dpr) / 2;
      half = Math.ceil((TIP + 0.4) * scale);   // the blade tips and a margin for the glow, so the broad bloom isn't cut square
      paint();
      // the name's ink (not its line boxes) measured, so the two lines sit exactly centred on the hub
      const lines = NAME.map(([text, font]) => {
        ctx.font = font(scale);
        const m = ctx.measureText(text);
        return { text, font: font(scale), up: m.actualBoundingBoxAscent, down: m.actualBoundingBoxDescent, l: m.actualBoundingBoxLeft, r: m.actualBoundingBoxRight, y: 0 };
      });
      const gap = 0.07 * scale, tall = lines.reduce((s, l) => s + l.up + l.down, 0) + gap * (lines.length - 1), pad = 0.15 * scale;   // pad: room for the glow
      title.width = titled.width = Math.ceil(Math.max(...lines.map((l) => l.l + l.r)) + 2 * pad);
      title.height = titled.height = Math.ceil(tall + 2 * pad);
      let y = (title.height - tall) / 2;
      for (const l of lines) { y += l.up; l.y = y; y += l.down + gap; }
      // black, with two passes of a pale-gold glow so it reads over the dark gaps between the spokes, then one crisp
      tctx.fillStyle = "#000";
      tctx.shadowColor = "rgba(255,236,190,.95)";
      for (const blur of [0.09, 0.05, 0]) {
        tctx.shadowBlur = blur * scale;
        for (const l of lines) { tctx.font = l.font; tctx.fillText(l.text, title.width / 2 + (l.l - l.r) / 2, l.y); }
      }
    };
    resize();
    addEventListener("resize", resize);
    /** A picture through a disc of radius r round its centre, feathered over its outer w px, into o's canvas. With
     *  `lit`, what has just been uncovered (the band inside the edge) shows gold before it settles to its own colour. */
    const masked = (src: HTMLCanvasElement, o: CanvasRenderingContext2D, r: number, w: number, lit = false) => {
      const { width, height } = o.canvas, x = width / 2, y = height / 2;
      o.globalCompositeOperation = "source-over";
      o.clearRect(0, 0, width, height);
      const g = o.createRadialGradient(x, y, 0, x, y, r + w);
      const a0 = `rgba(0,0,0,${Math.min(1, (r + w) / w)})`;   // r may be negative: the soft edge is only part-way out from the centre
      // not max(0, r) / (r + w): on the first frame r + w can round to exactly 0, and 0 / 0 is NaN, which throws and stops the intro
      g.addColorStop(0, a0); g.addColorStop(r > 0 ? r / (r + w) : 0, a0); g.addColorStop(1, "rgba(0,0,0,0)");
      o.fillStyle = g;
      o.fillRect(0, 0, width, height);
      o.globalCompositeOperation = "source-in";   // keep the picture only where the mask is
      o.drawImage(src, 0, 0);
      if (lit) {
        const l = o.createRadialGradient(x, y, Math.max(0, r - 1.5 * w), x, y, r + w);
        l.addColorStop(0, "rgba(255,222,140,0)"); l.addColorStop(0.6, "rgba(255,222,140,1)"); l.addColorStop(1, "rgba(255,222,140,1)");
        o.globalCompositeOperation = "source-atop";
        o.fillStyle = l;
        o.fillRect(0, 0, width, height);
      }
      return o.canvas;
    };

    /** A ring of light of radius rr with a soft tail behind its crest, at strength a. */
    const ring = (rr: number, w: number, a: number) => {
      if (a <= 0 || rr <= 1) return;
      const g = ctx.createRadialGradient(cx, cy, 0, cx, cy, rr + w);
      g.addColorStop(Math.max(0, (rr - w * 2.5) / (rr + w)), "rgba(255,200,110,0)");   // a long soft tail behind the crest
      g.addColorStop(Math.max(0, (rr - w * 0.8) / (rr + w)), "rgba(255,210,130,.18)");
      g.addColorStop(rr / (rr + w), "rgba(255,226,160,.6)");
      g.addColorStop(1, "rgba(255,170,70,0)");
      ctx.globalCompositeOperation = "lighter";
      ctx.globalAlpha = a; ctx.fillStyle = g;
      ctx.beginPath(); ctx.arc(cx, cy, rr + w, 0, TAU); ctx.fill();
    };

    // the clock counts frames, not wall time: each frame adds at most 50ms, so when the page behind is busy (building
    // the art, loading the chart) the bloom waits rather than jumping ahead; LEAD seconds of dark come first, and a
    // stalled frame in the dark restarts them (for up to 3s), so the bloom begins only once frames come smoothly
    let t = -LEAD, last = -1, first = -1, raf = 0;
    const frame = (now: number) => {
      const dt = last < 0 ? 0 : (now - last) / 1000;
      if (first < 0) first = now;
      t = t < 0 && dt > 0.1 && now - first < 3000 ? -LEAD : t + SPEED * Math.min(0.05, dt);
      last = now;
      if (t >= PULSE[1]) { done.current(); return; }
      ctx.globalCompositeOperation = "source-over";
      ctx.globalAlpha = 1;
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // the glow behind the design, growing with it as it is uncovered (not ahead of it), with a flash as the wheel completes
      const f = Math.max(0, Math.min(1, (t - REVEAL[0]) / (REVEAL[1] - REVEAL[0]))), e = (f + f * f * (3 - 2 * f)) / 2;   // between linear and smoothstep: no rush in the middle
      ctx.globalCompositeOperation = "lighter";
      const flash = Math.exp(-(((t - FLASH) / 0.35) ** 2));   // a smooth swell, no corners
      const haloA = Math.min(1, e * 0.45 + flash * 0.25), haloR = (e * R * 1.1 + flash * 0.6) * scale;
      if (haloA > 0) {
        const g = ctx.createRadialGradient(cx, cy, 0, cx, cy, haloR);
        g.addColorStop(0, "rgba(255,220,140,1)"); g.addColorStop(0.35, "rgba(255,160,60,.35)"); g.addColorStop(1, "rgba(255,120,30,0)");
        ctx.globalAlpha = haloA; ctx.fillStyle = g;
        ctx.fillRect(cx - haloR, cy - haloR, haloR * 2, haloR * 2);
      }

      // a soft-edged reveal from the hub out to the chakra's edge, uncovering the turning chakra as it passes
      if (f > 0) {
        // the reveal's edge stops just past the blade tips, its softness narrowing as it nears them
        const wf =(0.9 * (1 - e) + 0.15) * scale, rr = e * (TIP + 0.15) * scale;   // wf: how softly the chakra comes in behind the crest; rr: the crest's radius on screen
        const sc = 0.92 + 0.08 * e, r = rr / sc - wf;   // r: the mask's solid radius in the art's pixels; its leading edge rides the crest
        if (!sealed) { masked(art, sctx, r, wf); sealed = f >= 1; }   // once whole, the last mask is kept
        ctx.save();
        ctx.translate(cx, cy); ctx.rotate(TURN * t); ctx.scale(sc, sc);
        ctx.globalCompositeOperation = "source-over";
        ctx.globalAlpha = 1;
        ctx.drawImage(shown, -half, -half);
        ctx.globalCompositeOperation = "lighter";   // the lines brighten as the wave grows
        ctx.globalAlpha = 0.7 * e;
        ctx.drawImage(shown, -half, -half);
        ctx.restore();
      }
      // the name opens out from the hub as the wheel did, each letter lit gold as it is uncovered, then black
      const n = Math.max(0, Math.min(1, (t - NAME_IN[0]) / (NAME_IN[1] - NAME_IN[0]))), ne = n * n * (3 - 2 * n);
      if (n > 0) {
        const w = 0.3 * scale, r = ne * (Math.hypot(title.width, title.height) / 2 + 2.5 * w);   // ends with the gold band past the letters
        ctx.globalCompositeOperation = "source-over";
        ctx.globalAlpha = 1;
        ctx.drawImage(n >= 1 ? title : masked(title, dctx, r, w, true), cx - title.width / 2, cy - title.height / 2);
      }

      // the second pulse: a ring of light from the hub to past the corners, drawn last so it passes over the letters.
      // The overlay is cut away behind it (a hole in its CSS mask, a little inside the crest), so the home page shows
      // through as the ring passes; the hole is negative until the pulse starts, so nothing shows before then
      const q = Math.max(0, Math.min(1, (t - PULSE[0]) / (PULSE[1] - PULSE[0]))), w = 0.45 * scale;
      const rr = q * q * (3 - 2 * q) * (Math.hypot(cx, cy) + 2.5 * w);
      ring(rr, w, Math.min(1, 4 * (1 - q)));
      el.style.setProperty("--hole", `${(rr - 1.2 * w) / dpr}px`);
      el.style.setProperty("--feather", `${w / dpr}px`);
      raf = requestAnimationFrame(frame);
    };
    raf = requestAnimationFrame(frame);
    const skip = () => done.current();
    addEventListener("keydown", skip);

    return () => {
      cancelAnimationFrame(raf);
      removeEventListener("resize", resize); removeEventListener("keydown", skip);
      canvas.remove();
    };
  }, []);

  return (
    <div className="intro" ref={host} onClick={() => done.current()} role="presentation">
      <div className="sr-only">
        <h1>Sudarshana</h1>
        <p lang="sa">सुदर्शन</p>
      </div>
    </div>
  );
}
