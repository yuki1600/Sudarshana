import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api, chartName, type Birth, type MatchPart, type Meta } from "./api";
import { BirthDialog, nowChart } from "./BirthDialog";
import { Modal } from "./ChartDialogs";
import { useKept, useSaved } from "./hooks";
import { OpenChart } from "./OpenChart";
import { useChart } from "./store";
import { Loaded, SubTabs } from "./ui";
import { AREAS, DETAILS, type EditWho, type Focus, type Kind, OLD_VIEW, type RankFocus, type Side, type Tab, type View, loadSides, nakShort, partOf, saveSides, tone } from "./matchingShared";
import { GrahaGrid, HouseGrid, MatchChart, Shortlist, sameSide } from "./MatchingCompare";
import { FactorTable } from "./MatchingFactors";
import { MatchDasaLists } from "./MatchingDasas";
import { PartnerActions, PartnerBrief } from "./MatchingPartners";
import { Breakdown, KutaTables } from "./MatchingKutas";
import { RankList } from "./MatchingRank";

/** Marriage matching: 36×36 zodiac-split nakshatra matrix, Ashta Kuta, dual-chart compare. */
export function Matching() {
  const { natal, name: natalName, meta: natalMeta, addChart, activeChartId } = useChart();
  const [tab, setTab] = useSaved<Tab>("matchTab", "matrix");
  const [boyPart, setBoyPart] = useState(0);
  const [girlPart, setGirlPart] = useState(0);
  const [hover, setHover] = useState<{ r: number; c: number } | null>(null);
  const [popup, setPopup] = useState(false);
  const [rank, setRank] = useState<RankFocus | null>(null);
  const openSide = natal ? { name: natalName || "Natal", birth: natal, meta: natalMeta } : undefined;
  const [boy, setBoy] = useState<Side | null>(() => loadSides(openSide).boy);
  const [girl, setGirl] = useState<Side | null>(() => loadSides(openSide).girl);
  const [edit, setEdit] = useState<EditWho>(null);
  const [fresh, setFresh] = useState(false);   // New chart: the birth dialog starts blank, not from the side's chart
  const editSide = (who: "boy" | "girl", blank: boolean) => { setFresh(blank); setEdit(who); };
  const [opening, setOpening] = useKept<"boy" | "girl" | null>("match.opening", null);
  const [loadError, setLoadError] = useState("");
  const [kindD1, setKindD1] = useSaved<Kind>("matchKind1", "bhava");     // new keys: Bhava is the default, over a saved Rasi of the old ones
  const [kindD9, setKindD9] = useSaved<Kind>("matchKind9", "bhava");
  const [focus, setFocus] = useState<Focus>(null);
  const [view, setView] = useSaved<View>("matchView", "overview");
  const [listGirl, setListGirl] = useKept<Side[]>("match.listGirl", []);
  const [listBoy, setListBoy] = useKept<Side[]>("match.listBoy", []);
  const listed = (l: Side[], s: Side | null) => !!s && l.some((x) => sameSide(x, s));
  const toggle = (l: Side[], set: (l: Side[]) => void, s: Side | null) => { if (s) set(listed(l, s) ? l.filter((x) => !sameSide(x, s)) : [...l, s]); };

  useEffect(() => { saveSides(boy, girl); }, [boy, girl]);

  // the chart open up top takes its gender's side; one of no gender leaves both as they were
  useEffect(() => {
    if (!openSide) return;
    if (openSide.meta?.gender === 1) setBoy(openSide); else if (openSide.meta?.gender === 2) setGirl(openSide);
  }, [activeChartId, natal, natalName]); // eslint-disable-line react-hooks/exhaustive-deps

  // no chart open at all: an empty side starts as a chart of this moment
  useEffect(() => {
    if (natal || (boy && girl)) return;
    const c = nowChart();
    const now = (gender: number): Side => ({ name: "Now", birth: c.birth, meta: { ...c.meta, gender } as Meta });
    setBoy((b) => b ?? now(1)); setGirl((g) => g ?? now(2));
  }, [natal]); // eslint-disable-line react-hooks/exhaustive-deps

  const matrix = useQuery({ queryKey: ["matchMatrix"], queryFn: api.matchingMatrix, staleTime: Infinity });
  const parts = matrix.data?.parts;
  const girlSel = parts?.[girlPart];
  const boySel = parts?.[boyPart];
  const detail = useQuery({
    queryKey: ["matchDetail", girlSel?.nakshatra, girlSel?.pada, boySel?.nakshatra, boySel?.pada],
    queryFn: () => api.matchingDetail(girlSel!.nakshatra, girlSel!.pada, boySel!.nakshatra, boySel!.pada),
    enabled: popup && !!girlSel && !!boySel,
  });
  const compare = useQuery({
    queryKey: ["matchCompare", boy?.birth, girl?.birth, boy?.name, girl?.name],
    queryFn: () => api.matchingCompare(girl!.birth, boy!.birth, girl!.name, boy!.name),
    enabled: !!boy && !!girl,
  });

  useEffect(() => {
    if (!compare.data || !parts) return;
    setGirlPart(partOf(parts, compare.data.bride_moon.nakshatra, compare.data.bride_moon.pada - 1));
    setBoyPart(partOf(parts, compare.data.groom_moon.nakshatra, compare.data.groom_moon.pada - 1));
  }, [compare.data, parts]);

  // Saved matchTab may still be the old "compare" id
  useEffect(() => {
    if (tab !== "matrix" && tab !== "charts") setTab("charts");
  }, [tab, setTab]);
  // ... and matchView a sub tab of an older build (Comparison, Rasi, Navamsa, Bhavas, Bala)
  useEffect(() => {
    const now = OLD_VIEW[view as string];
    if (now) setView(now);
  }, [view, setView]);

  /** A partner in from anywhere (entered, a file, the cloud, a recent chart) also joins the open charts, so the pick list has it. */
  const putSide = (who: "boy" | "girl", side: Side) => {
    if (who === "boy") setBoy(side); else setGirl(side);
    addChart(side.name, side.birth, side.meta);
  };
  const pickSide = (who: "boy" | "girl", side: Side) => { if (who === "boy") setBoy(side); else setGirl(side); };
  const loadJhd = async (who: "boy" | "girl", title: string, content: string) => {
    setOpening(null); setLoadError("");
    try {
      const { birth, parsed } = await api.parseJhd(content);
      putSide(who, { name: title, birth,
        meta: { city: parsed.city ?? "", country: parsed.country ?? "", dst: !!parsed.dst, tz_standard_east: parsed.tz_standard_east, tz_dst_east: parsed.tz_dst_east, gender: parsed.gender, ...(parsed.state ? { state: parsed.state } : {}) } as Meta });
    } catch (e) { setLoadError((e as Error).message); }
  };
  const saveSide = (who: "boy" | "girl", n: string, b: Birth, m: Meta) => {
    putSide(who, { name: n, birth: b, meta: { ...m, gender: m.gender ?? (who === "boy" ? 1 : 2) } });
    setEdit(null);
  };

  const pick = (g: number, b: number) => { setRank(null); setGirlPart(g); setBoyPart(b); setPopup(true); };
  const openRank = (who: "girl" | "boy", index: number) => { setPopup(false); setRank({ who, index }); };
  const rasiEdge = (list: MatchPart[], i: number) => i > 0 && list[i].rasi !== list[i - 1].rasi;
  const hr = hover?.r ?? -1;
  const hc = hover?.c ?? -1;
  const editing = fresh ? null : edit === "boy" ? boy : edit === "girl" ? girl : null;

  const chartsTab = tab !== "matrix";
  const c = compare.data;
  const title = chartsTab && !(boy && girl) ? (
    <div className="row wrap match-title match-total">
      <span className="muted">Enter both charts</span>
      <button type="button" title="The matrix of every pair of Moon stars" onClick={() => setTab("matrix")}>Matrix</button>
    </div>
  ) : chartsTab ? (
    <div className="row wrap match-title match-total">
      {!c && <span className="muted">{compare.isError ? "Could not match" : "Matching…"}</span>}
      <button type="button" title="The matrix of every pair of Moon stars" onClick={() => setTab("matrix")}>Matrix</button>
    </div>
  ) : null;

  return (
    <div className={`pane match-pane${chartsTab ? " charts-mode" : ""}`}>
      {tab === "matrix" && (
        <div className="match-body matrix-fill">
          <Loaded q={matrix}>{(m) => (
            <div className="match-matrix-wrap" onMouseLeave={() => setHover(null)}>
              <table className="match-matrix" aria-label="Matching score matrix by nakshatra and rasi">
                <thead>
                  <tr>
                    <th scope="col" className="corner">
                      Girl ↓ · Boy →
                      <button type="button" className="corner-charts" title="The partners' charts and their matching" onClick={() => setTab("charts")}>Charts</button>
                    </th>
                    {m.parts.map((p, i) => (
                      <th key={p.index} className={`${(popup && i === boyPart) || (rank?.who === "boy" && rank.index === i) ? "picked" : ""}${i === hc ? " hover-col" : ""}${rasiEdge(m.parts, i) ? " rasi-start" : ""}`} title={`${p.label} — click for ranked girl matches`}>
                        <button type="button" className="match-axis" onClick={() => openRank("boy", i)}>
                          <span className="col-nak">{nakShort(p.nakshatra_name)}</span>
                          <span className="col-rasi">{p.rasi_abbr}</span>
                          <span className="col-pada">p{p.padas.length === 1 ? p.padas[0] : `${p.padas[0]}–${p.padas[p.padas.length - 1]}`}</span>
                        </button>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {m.parts.map((gp, ri) => (
                    <tr key={gp.index} className={`${ri === hr ? "hover-row" : ""}${rasiEdge(m.parts, ri) ? " rasi-row-start" : ""}`.trim() || undefined}>
                      <th scope="row" className={`${(popup && gp.index === girlPart) || (rank?.who === "girl" && rank.index === gp.index) ? "picked" : ""}${ri === hr ? " hover-label" : ""}`} title={`${gp.label} — click for ranked boy matches`}>
                        <button type="button" className="match-axis row-label" onClick={() => openRank("girl", gp.index)}>
                          <span className="row-nak">{gp.nakshatra_name}</span>
                          <span className="row-rasi">{gp.rasi_abbr}</span>
                          <span className="row-pada">p{gp.padas.length === 1 ? gp.padas[0] : `${gp.padas[0]}–${gp.padas[gp.padas.length - 1]}`}</span>
                        </button>
                      </th>
                      {m.scores[gp.index].map((score, bi) => (
                        <td key={bi} className={`${rasiEdge(m.parts, bi) ? "rasi-start" : ""}${bi === hc ? " hover-col" : ""}`}>
                          <button type="button" className={`match-cell ${tone(score)}`}
                            title={`${gp.label} × ${m.parts[bi].label}: ${score}/36`}
                            onMouseEnter={() => setHover({ r: ri, c: bi })}
                            onClick={() => pick(gp.index, bi)}>{score}</button>
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}</Loaded>
        </div>
      )}

      {chartsTab && (
        <div className="match-body charts-fit match-split">
          <div className="match-left">
            <div className="match-charts" aria-label="Girl and boy, D-1 and D-9">
              <MatchChart label="Girl" side={girl} d={1} kind={kindD1} onKind={setKindD1} onPick={(s) => pickSide("girl", s)} picked={focus?.girl} actions={
                <PartnerActions side={girl} onNew={() => editSide("girl", true)} onEdit={() => editSide("girl", false)} onOpen={() => setOpening("girl")} listed={listed(listGirl, girl)} onList={() => toggle(listGirl, setListGirl, girl)} />} />
              <MatchChart label="Boy" side={boy} d={1} kind={kindD1} onKind={setKindD1} onPick={(s) => pickSide("boy", s)} second picked={focus?.boy} actions={
                <PartnerActions side={boy} onNew={() => editSide("boy", true)} onEdit={() => editSide("boy", false)} onOpen={() => setOpening("boy")} listed={listed(listBoy, boy)} onList={() => toggle(listBoy, setListBoy, boy)} />} />
              <MatchChart label="Girl" side={girl} d={9} kind={kindD9} onKind={setKindD9} onPick={(s) => pickSide("girl", s)} picked={focus?.girl} />
              <MatchChart label="Boy" side={boy} d={9} kind={kindD9} onKind={setKindD9} onPick={(s) => pickSide("boy", s)} second picked={focus?.boy} />
            </div>
          </div>

          <aside className="match-right">
            <div className="match-top tab-head">
              <SubTabs label="Matching" value={view} onChange={setView} tabs={[{ id: "overview", name: "Overview" }, ...AREAS, ...DETAILS, { id: "shortlist", name: listGirl.length + listBoy.length ? `★ Starred ${listGirl.length + listBoy.length}` : "★ Starred" }]} />
              {title}
            </div>
            <div className="match-scroll">
            {view === "overview" && (
              <div className="match-briefs">
                <PartnerBrief label="Girl" side={girl} />
                <PartnerBrief label="Boy" side={boy} />
              </div>
            )}
            {view === "shortlist" ? (
              <div className="match-compare-block ms-block">
                {girl && listBoy.length > 0 && <Shortlist who="girl" fixed={girl} list={listBoy} shown={boy} onShow={(s) => pickSide("boy", s)} onDrop={(s) => toggle(listBoy, setListBoy, s)} />}
                {boy && listGirl.length > 0 && <Shortlist who="boy" fixed={boy} list={listGirl} shown={girl} onShow={(s) => pickSide("girl", s)} onDrop={(s) => toggle(listGirl, setListGirl, s)} />}
                {!(girl && listBoy.length) && !(boy && listGirl.length) && <p className="muted">Press ★ on a boy's chart to star him against the girl shown (or on a girl's, against the boy). Star two or more to rank them here.</p>}
              </div>
            ) : boy && girl ? (
              <Loaded q={compare}>{(c) => {
                const area = (...ids: string[]) => c.factors.filter((a) => ids.includes(a.id));
                return (
                  <div className="match-compare-block">
                    {view === "overview" ? (
                      <div className="mf-kutas"><KutaTables d={c.match} /></div>
                    ) : view === "mind" ? <FactorTable births={{ girl: girl.birth, boy: boy.birth }} areas={area("doshas", "mind", "health")} heads="quiet" /> : view === "timing" ? <MatchDasaLists girl={girl} boy={boy} />
                    : view === "grahas" ? <GrahaGrid c={c} births={{ girl: girl.birth, boy: boy.birth }} onFocus={setFocus} />
                      : view === "bhavas" ? <HouseGrid c={c} births={{ girl: girl.birth, boy: boy.birth }} onFocus={setFocus} />
                      : view === "marriage" ? <FactorTable births={{ girl: girl.birth, boy: boy.birth }} areas={area("marriage", "family")} heads="quiet" />
                      : area(view).length ? <FactorTable births={{ girl: girl.birth, boy: boy.birth }} areas={area(view)} heads={false} />
                      : <p className="muted">Nothing to compare.</p>}
                  </div>
                );
              }}</Loaded>
            ) : <p className="muted">Enter both charts for matching and similarities.</p>}
            </div>
          </aside>
        </div>
      )}

      {edit && (
        <BirthDialog
          open
          blank={!editing}
          seed={editing}
          defaultGender={edit === "boy" ? 1 : 2}
          title={edit === "boy" ? "Boy (groom) birth data" : "Girl (bride) birth data"}
          onClose={() => setEdit(null)}
          onSave={(n, b, m) => saveSide(edit, n, b, m)}
        />
      )}

      {opening && (
        <OpenChart single onClose={() => setOpening(null)}
          onFiles={async (fs) => loadJhd(opening, chartName(fs[0].name), await fs[0].text())}
          onCloud={(n, content) => loadJhd(opening, n, content)}
          onRecent={(n, b, m) => { setOpening(null); putSide(opening, { name: n, birth: b, meta: m }); }} />
      )}
      {loadError && <p role="alert" className="error banner">{loadError}</p>}

      {rank && matrix.data && (
        <RankList m={matrix.data} focus={rank} onClose={() => setRank(null)}
          onOpen={(g, b) => pick(g, b)} />
      )}

      {popup && (
        <Modal title="Kuta details" onClose={() => setPopup(false)} wide>
          <Loaded q={detail}>{(d) => <Breakdown d={d} />}</Loaded>
        </Modal>
      )}
    </div>
  );
}
