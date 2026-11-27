import { api, type Birth } from "./api";
import type { PanelState } from "./store";

export type Bitmap = "screen" | "south-north" | "rasi-navamsa";

const CSS_VARS = ["--panel", "--ink", "--line", "--muted", "--shade", "--lagna", "--accent"];

/** A drawn chart as a stand-alone SVG string, its colours and fonts inlined so it renders outside the page. */
function inline(svg: SVGSVGElement, size: number, x = 0, y = 0): string {
  const clone = svg.cloneNode(true) as SVGSVGElement;
  const live = Array.from(svg.querySelectorAll<SVGElement>("*")), copies = Array.from(clone.querySelectorAll<SVGElement>("*"));
  copies.forEach((c, i) => {
    const s = getComputedStyle(live[i]);
    for (const p of ["fill", "stroke", "stroke-width", "font-size", "font-weight", "font-family", "paint-order"]) c.style.setProperty(p, s.getPropertyValue(p));
  });
  clone.setAttribute("x", String(x));
  clone.setAttribute("y", String(y));
  clone.setAttribute("width", String(size));
  clone.setAttribute("height", String(size));
  return new XMLSerializer().serializeToString(clone);
}

function downloadBlob(blob: Blob, name: string) {
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = name;
  a.click();
  URL.revokeObjectURL(a.href);
}

/** Put a PNG on the clipboard, or save it when the browser blocks image clipboard. */
export async function writePng(blob: Blob, downloadName = "image.png"): Promise<"copied" | "downloaded"> {
  if (navigator.clipboard?.write && typeof ClipboardItem !== "undefined") {
    try {
      await navigator.clipboard.write([new ClipboardItem({ "image/png": blob })]);
      return "copied";
    } catch { /* fall through to download */ }
  }
  downloadBlob(blob, downloadName);
  return "downloaded";
}

/** Share a PNG via the system sheet when available; otherwise save the file. */
export async function sharePng(blob: Blob, title: string, filename: string): Promise<"shared" | "downloaded"> {
  const file = new File([blob], filename, { type: "image/png" });
  if (typeof navigator.canShare === "function" && navigator.canShare({ files: [file] })) {
    await navigator.share({ files: [file], title, text: title });
    return "shared";
  }
  downloadBlob(blob, filename);
  return "downloaded";
}

async function toClipboard(markup: string, w: number, h: number, background: string) {
  const img = new Image();
  img.src = "data:image/svg+xml;charset=utf-8," + encodeURIComponent(markup);
  await img.decode();
  const canvas = document.createElement("canvas");
  canvas.width = w;
  canvas.height = h;
  const g = canvas.getContext("2d")!;
  g.fillStyle = background;
  g.fillRect(0, 0, w, h);
  g.drawImage(img, 0, 0);
  const blob = await new Promise<Blob>((ok, no) => canvas.toBlob((b) => (b ? ok(b) : no(new Error("Could not make the bitmap"))), "image/png"));
  await writePng(blob, "chart.png");
}

/** Copy a chart as a bitmap: 360 px a chart for the screen, 720 for books. */
export async function copyBitmap(which: Bitmap, chart: Birth, state: PanelState, optional: Record<string, boolean>, dpi: 1 | 2) {
  const root = document.createElement("div");
  root.style.cssText = "position:fixed;left:-9999px;top:0;width:800px";
  document.body.append(root);
  try {
    const { renderChart } = await import("./renderChart");
    const specs = which === "rasi-navamsa" ? [{ kind: "varga", d: 1 }, { kind: "varga", d: 9 }] as const : [state.spec, state.spec];
    const styles: ("south" | "north" | null)[] = which === "south-north" ? ["south", "north"] : [null, null];
    const count = which === "screen" ? 1 : 2;
    const size = 360 * dpi, pad = 6 * dpi;
    const svgs: string[] = [];
    for (let i = 0; i < count; i++) {
      const panel = await api.panel(chart, specs[i], state.view, optional);
      const svg = await renderChart(root, panel, styles[i]);
      svgs.push(inline(svg, size, pad + i * (size + pad), pad));
    }
    const w = count * (size + pad) + pad, h = size + 2 * pad;
    const bg = getComputedStyle(document.documentElement);
    const vars = CSS_VARS.map((v) => `${v}:${bg.getPropertyValue(v)}`).join(";");
    await toClipboard(`<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" style="${vars}">${svgs.join("")}</svg>`, w, h, bg.getPropertyValue("--panel").trim() || "#fff");
  } finally { root.remove(); }
}
