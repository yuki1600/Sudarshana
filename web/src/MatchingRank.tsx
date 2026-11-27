import { useState } from "react";
import { type MatchMatrix } from "./api";
import { sharePng, writePng } from "./bitmap";
import { Modal } from "./ChartDialogs";
import { useChart } from "./store";
import { RANK_BANDS, type RankFocus, partFull, partPada, tone } from "./matchingShared";

async function rankTablePng(title: string, bands: { name: string; range: string; fill: string; items: { score: number; nak: string; meta: string }[] }[]) {
  const scale = 2;
  const colW = 268;
  const gap = 10;
  const pad = 22;
  const titleH = 44;
  const headH = 36;
  const rowH = 42;
  const maxRows = Math.max(1, ...bands.map((b) => b.items.length));
  const w = pad * 2 + bands.length * colW + (bands.length - 1) * gap;
  const h = pad * 2 + titleH + headH + maxRows * rowH + 10;
  const canvas = document.createElement("canvas");
  canvas.width = w * scale;
  canvas.height = h * scale;
  const g = canvas.getContext("2d")!;
  g.scale(scale, scale);
  g.fillStyle = "#ffffff";
  g.fillRect(0, 0, w, h);
  g.fillStyle = "#1a1a1a";
  g.font = "700 18px Georgia, 'Times New Roman', serif";
  g.fillText(title, pad, pad + 22);
  g.font = "400 12px system-ui, sans-serif";
  g.fillStyle = "#666";
  g.fillText("Ashta Kuta · best to worst", pad, pad + 38);

  bands.forEach((band, bi) => {
    const x = pad + bi * (colW + gap);
    const y0 = pad + titleH;
    g.fillStyle = band.fill;
    g.fillRect(x, y0, colW, headH);
    g.fillStyle = "#1a1a1a";
    g.font = "700 13px system-ui, sans-serif";
    g.fillText(`${band.name}  ${band.range}  (${band.items.length})`, x + 10, y0 + 22);

    band.items.forEach((item, ri) => {
      const y = y0 + headH + ri * rowH;
      g.fillStyle = ri % 2 ? "#f4f4f5" : "#ffffff";
      g.fillRect(x, y, colW, rowH);
      g.fillStyle = band.fill;
      g.globalAlpha = 0.28;
      g.fillRect(x, y, 4, rowH);
      g.globalAlpha = 1;
      g.fillStyle = "#1a1a1a";
      g.font = "800 14px system-ui, sans-serif";
      g.fillText(String(item.score), x + 12, y + 25);
      g.font = "600 12px system-ui, sans-serif";
      g.fillText(item.nak, x + 42, y + 17);
      g.font = "400 11px system-ui, sans-serif";
      g.fillStyle = "#555";
      g.fillText(item.meta, x + 42, y + 33);
    });

    if (!band.items.length) {
      g.fillStyle = "#ffffff";
      g.fillRect(x, y0 + headH, colW, rowH);
      g.fillStyle = "#888";
      g.font = "400 12px system-ui, sans-serif";
      g.fillText("None", x + 12, y0 + headH + 25);
    }
  });

  return new Promise<Blob>((ok, no) => canvas.toBlob((b) => (b ? ok(b) : no(new Error("Could not make the image"))), "image/png"));
}

export function RankList({ m, focus, onClose, onOpen }: {
  m: MatchMatrix; focus: RankFocus; onClose: () => void;
  onOpen: (girl: number, boy: number) => void;
}) {
  const { say } = useChart();
  const [busy, setBusy] = useState(false);
  const self = m.parts[focus.index];
  const other = focus.who === "girl" ? "Boy" : "Girl";
  const title = `${other} matches for ${partFull(self)}`;
  const ranked = m.parts
    .map((part, i) => ({
      part,
      score: focus.who === "girl" ? m.scores[focus.index][i] : m.scores[i][focus.index],
      girl: focus.who === "girl" ? focus.index : i,
      boy: focus.who === "boy" ? focus.index : i,
    }))
    .sort((a, b) => b.score - a.score || a.part.index - b.part.index);
  const bands = RANK_BANDS.map((band) => ({
    ...band,
    items: ranked.filter((r) => band.test(r.score)).map((r) => ({
      score: r.score,
      nak: r.part.nakshatra_name,
      meta: `${r.part.rasi_name} · pada ${partPada(r.part)}`,
      girl: r.girl,
      boy: r.boy,
      part: r.part,
    })),
  }));
  const fileStem = `${other.toLowerCase()}-matches-${self.nakshatra_name.replace(/\s+/g, "-").toLowerCase()}`;

  const makePng = () => rankTablePng(title, bands.map(({ name, range, fill, items }) => ({
    name, range, fill, items: items.map(({ score, nak, meta }) => ({ score, nak, meta })),
  })));

  const copyImage = async () => {
    setBusy(true);
    try { await writePng(await makePng(), `${fileStem}.png`); }
    catch (e) { say("Matching", (e as Error).message); }
    finally { setBusy(false); }
  };
  const shareImage = async () => {
    setBusy(true);
    try { await sharePng(await makePng(), title, `${fileStem}.png`); }
    catch (e) {
      if ((e as Error).name !== "AbortError") say("Matching", (e as Error).message);
    } finally { setBusy(false); }
  };

  return (
    <Modal title={title} onClose={onClose} wide>
      <p className="muted" style={{ marginTop: 0 }}>Best to worst · click for Ashta Kuta</p>
      <div className="match-rank">
        {bands.map((band) => (
          <section key={band.id} className="match-rank-band">
            <h3><i className={band.id} aria-hidden /> {band.name} <span className="muted">({band.items.length})</span></h3>
            {!band.items.length && <p className="muted" style={{ margin: 0, fontSize: "0.9em" }}>None</p>}
            <ol>
              {band.items.map((r) => (
                <li key={r.part.index}>
                  <button type="button" className={`match-rank-row ${tone(r.score)}`} onClick={() => onOpen(r.girl, r.boy)}
                    title={`${partFull(r.part)} · ${r.score}/36`}>
                    <span className="match-rank-score">{r.score}</span>
                    <span className="match-rank-label">{r.nak}</span>
                    <span className="match-rank-meta">{r.meta}</span>
                  </button>
                </li>
              ))}
            </ol>
          </section>
        ))}
      </div>
      <menu>
        <button type="button" disabled={busy} onClick={copyImage}>Copy as image</button>
        <button type="button" disabled={busy} onClick={shareImage}>Share</button>
      </menu>
    </Modal>
  );
}
