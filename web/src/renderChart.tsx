import { createRoot } from "react-dom/client";
import { flushSync } from "react-dom";
import type { ChartPanel } from "./api";
import { EastGrid, NorthGrid } from "./ChartGrid";
import { SouthGrid } from "./SouthGrid";
import { useChart } from "./store";

/** A panel's chart drawn off-screen, for a bitmap. ``style`` overrides the chosen chart style. */
export async function renderChart(host: HTMLElement, p: ChartPanel, style: "south" | "north" | null): Promise<SVGSVGElement> {
  const div = document.createElement("div");
  host.append(div);
  const st = style ?? useChart.getState().chartStyle;
  const props = { title: p.title, lagnaSign: p.lagna, cell: (s: number) => p.boxes[s] ?? [] };
  const root = createRoot(div);
  flushSync(() => root.render(st === "north" ? <NorthGrid {...props} /> : st === "east" ? <EastGrid {...props} /> : <SouthGrid {...props} />));
  return div.querySelector("svg")!;
}
