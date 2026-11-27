import { createContext, useContext, useEffect, type ReactNode } from "react";
import { createPortal } from "react-dom";
import { CopyButton } from "./ui";
import { SCRIPTS, transliterate, type Script } from "./script";
import { type Item } from "./remediesData";

/* -------------------------------------------------------------------------- */
/*                                   VERSES                                   */
/* -------------------------------------------------------------------------- */

/** A śloka centred on a shaded leaf, the way printed editions set verses. */
export const ScriptCtx = createContext<{ script: Script; setScript: (s: Script) => void }>({ script: "deva", setScript: () => {} });

/** A śloka centred on a shaded leaf, the way printed editions set verses: in the chosen script, with the Roman reading under it. */
export function Sloka({ text }: { text: string }) {
  const { script } = useContext(ScriptCtx);
  const shown = transliterate(text, script);
  return (
    <div className="rm-sloka">
      <p lang={shown === text ? "sa-Latn" : "sa"}>{shown}</p>
      {shown !== text && <p className="rm-iast" lang="sa-Latn">{text}</p>}
    </div>
  );
}

/** Which script the ślokas are shown in; the translations stay in English. */
function ScriptPicker() {
  const { script, setScript } = useContext(ScriptCtx);
  return (
    <select className="rm-script" aria-label="Script for the ślokas" value={script} onChange={(e) => setScript(e.target.value as Script)}>
      {SCRIPTS.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
    </select>
  );
}

function Verse({ item }: { item: Item }) {
  return (
    <article className="rm-verse">
      <header>
        <div>
          <p className="rm-cite">{item.source} {item.citation}</p>
          <h4>{item.title}</h4>
        </div>
        <CopyButton text={[item.title, `${item.source} ${item.citation}`, item.sanskrit, item.translation, item.note].filter(Boolean).join("\n\n")} />
      </header>
      {item.sanskrit && <Sloka text={item.sanskrit} />}
      <p className="rm-translation">{item.translation}</p>
      {item.note && <p className="rm-note"><b>Purport</b> {item.note}</p>}
    </article>
  );
}

/** The śāstra column on the right; a chapter's verses render there from wherever the chapter decides them. */
export const SideCtx = createContext<HTMLElement | null>(null);

/** The story renders in place; `aside` goes to the śāstra column, which starts at its top whenever `id` changes. */
export function Split({ aside, children, id }: { aside: ReactNode; children: ReactNode; id?: string }) {
  const side = useContext(SideCtx);
  useEffect(() => { side?.scrollTo(0, 0); }, [side, id]);
  return <>{children}{side && createPortal(aside, side)}</>;
}

export function Verses({ items, title = "From the śāstra", picker = true }: { items: Item[]; title?: string; picker?: boolean }) {
  if (!items.length) return null;
  return (
    <section className="rm-verses">
      <div className="rm-verses-head">
        <h3 className="rm-title minor">{title}</h3>
        {picker && items.some((i) => i.sanskrit) && <ScriptPicker />}
      </div>
      {items.map((i) => <Verse key={i.id} item={i} />)}
    </section>
  );
}
