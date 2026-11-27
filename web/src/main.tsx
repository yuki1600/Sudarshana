import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { pull } from "./kept";
import { startSelectKeys } from "./selectKeys";
import "./styles.css";

startSelectKeys();

// A chart's numbers never change for the same input, so keep them
const client = new QueryClient({ defaultOptions: { queries: { staleTime: Infinity, refetchOnWindowFocus: false, retry: false } } });

// Reload when a new web/dist lands (every build changes index.html); the store reopens what was on screen
if (import.meta.env.PROD) {
  let seen: string | null = null;
  setInterval(async () => {
    if (document.visibilityState !== "visible") return;
    try {
      const r = await fetch("/index.html", { method: "HEAD", cache: "no-store" });
      const tag = r.headers.get("etag") ?? r.headers.get("last-modified");
      if (r.ok && tag) { if (seen && tag !== seen) location.reload(); seen = tag; }
    } catch { /* server restarting: try again next tick */ }
  }, 2000);
}

// The account's kept localStorage first: the app's modules read it as they load (settings, the chart store); then the page
// in the language of Settings > Language, so the first render is in it (should its words fail to load, the app opens in English)
pull().then(() => import("./language")).then((l) => l.startLanguage()).catch(() => {}).then(() => import("./App")).then(({ default: App }) => createRoot(document.getElementById("root")!).render(
  <StrictMode><QueryClientProvider client={client}><App /></QueryClientProvider></StrictMode>,
));
