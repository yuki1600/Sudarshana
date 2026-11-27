import { Icon } from "./Icons";
import { useEffect, useLayoutEffect, useRef, useState, type ReactNode } from "react";

export interface MenuItem {
  label: string;
  show?: ReactNode;       // drawn in place of the label's text (which stays its name for screen readers and its buttons)
  onClick?: () => void;
  checked?: boolean;
  disabled?: boolean;
  items?: MenuEntry[];    // a sub-menu
  hint?: string;          // the shortcut, on the right
  onSave?: () => void;    // a save icon beside the ×: that chart isn't saved in the Cloud, and a click saves it
  onRemove?: () => void;  // a × beside the item, e.g. to close that chart
  keep?: boolean;         // the menu stays open after a click: one of a multi-select list
  title?: string;         // the tip on hover
}
export type MenuEntry = MenuItem | "-";

/** A sub-menu beside its item, in window coordinates: the parent list scrolls, which would clip it otherwise. */
function Sub({ children }: { children: ReactNode }) {
  const ref = useRef<HTMLDivElement>(null);
  const [at, setAt] = useState({ left: -9999, top: 0 });
  useLayoutEffect(() => {
    // against the parent menu's edge (borders overlapping), its first item level with the one that opened it, so the two read as one
    const item = ref.current!.parentElement!.getBoundingClientRect(), menu = ref.current!.parentElement!.closest(".menu")!.getBoundingClientRect(), me = ref.current!.getBoundingClientRect();
    setAt({ left: menu.right + me.width > innerWidth - 4 ? Math.max(4, menu.left - me.width + 1) : menu.right - 1, top: Math.max(4, Math.min(item.top - 5, innerHeight - me.height - 4)) });
  }, []);
  return <div ref={ref} className="submenu" style={at}>{children}</div>;
}

function Entries({ items, close, focus = true }: { items: MenuEntry[]; close: () => void; focus?: boolean }) {
  const [open, setOpen] = useState(-1);
  const ref = useRef<HTMLUListElement>(null);
  const move = (e: React.KeyboardEvent) => {
    const all = Array.from(ref.current!.querySelectorAll<HTMLElement>(":scope > li > button:not(:disabled)"));
    const i = all.indexOf(document.activeElement as HTMLElement);
    if (e.key === "ArrowDown") { all[(i + 1) % all.length]?.focus(); e.preventDefault(); e.stopPropagation(); }
    if (e.key === "ArrowUp") { all[(i - 1 + all.length) % all.length]?.focus(); e.preventDefault(); e.stopPropagation(); }
  };
  useEffect(() => { if (focus) ref.current?.querySelector<HTMLElement>(":scope > li > button:not(:disabled)")?.focus(); }, []);
  return (
    <ul className="menu" role="menu" ref={ref} onKeyDown={move}>
      {items.map((m, i) => m === "-" ? (i > 0 && i < items.length - 1 && items[i - 1] !== "-" && <li key={i} role="separator" />) : (
        <li key={i} role="none" className={m.onRemove || m.onSave ? "removable" : undefined} onMouseEnter={() => setOpen(m.items ? i : -1)}>
          <button role={m.checked === undefined ? "menuitem" : "menuitemcheckbox"} aria-checked={m.checked} aria-haspopup={m.items ? "menu" : undefined} aria-expanded={m.items ? open === i : undefined} disabled={m.disabled} title={m.title}
            onClick={() => { if (m.items) setOpen(open === i ? -1 : i); else { m.onClick?.(); if (!m.keep) close(); } }}
            onKeyDown={(e) => {
              if (e.key === "ArrowRight" && m.items) { setOpen(i); e.preventDefault(); e.stopPropagation(); }
              if (e.key === "ArrowLeft" && open === i) { setOpen(-1); e.preventDefault(); e.stopPropagation(); }
            }}>
            <span className="tick" aria-hidden>{m.checked ? "✓" : ""}</span>
            <span className="label">{m.show ?? m.label}</span>
            {m.hint && <span className="muted">{m.hint}</span>}
            {m.items && <span aria-hidden>›</span>}
          </button>
          {m.onSave && <button type="button" className="menu-remove unsaved-mark" aria-label={`Save ${m.label} in Cloud`} onClick={m.onSave}><Icon name="save" /></button>}
          {m.onRemove && <button type="button" className="menu-remove" aria-label={`Close ${m.label}`} title="Close" onClick={m.onRemove}><Icon name="close" /></button>}
          {m.items && open === i && (
            <Sub><Entries items={m.items} close={close} /></Sub>
          )}
        </li>
      ))}
    </ul>
  );
}

/** A floating menu: closes on Escape and on a click outside it. Keeps inside the window. */
export function FloatingMenu({ x, y, width, items, close, label, focus }: { x: number; y: number; width?: number; items: MenuEntry[]; close: () => void; label: string; focus?: boolean }) {
  const ref = useRef<HTMLDivElement>(null);
  const [at, setAt] = useState({ x, y });
  useEffect(() => {
    const away = (e: MouseEvent) => { if (!ref.current?.contains(e.target as Node)) close(); };
    const key = (e: KeyboardEvent) => {
      if (e.key === "Escape") close();
      // opened by a hover, so no item has the focus yet: the arrows step into it (Enter then picks)
      else if ((e.key === "ArrowDown" || e.key === "ArrowUp") && !ref.current?.contains(document.activeElement)) {
        const all = ref.current?.querySelectorAll<HTMLElement>(":scope > .menu > li > button:not(:disabled)");
        if (all?.length) { e.preventDefault(); all[e.key === "ArrowDown" ? 0 : all.length - 1].focus(); }
      }
    };
    document.addEventListener("mousedown", away);
    document.addEventListener("keydown", key);
    const r = ref.current!.getBoundingClientRect();
    setAt({ x: Math.max(4, Math.min(x, innerWidth - r.width - 4)), y: Math.max(4, Math.min(y, innerHeight - r.height - 4)) });
    return () => { document.removeEventListener("mousedown", away); document.removeEventListener("keydown", key); };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps
  // width: as wide as the button it drops from
  return <div ref={ref} className={width ? "floating-menu sized" : "floating-menu"} style={{ left: at.x, top: at.y, width }} aria-label={label}><Entries items={items} close={close} focus={focus} /></div>;
}

/** The right-click menu of a pane. ``open`` also takes a button's click, so the same menu is there without a right mouse button. */
export function useMenu() {
  const [menu, setMenu] = useState<{ x: number; y: number; width?: number; items: MenuEntry[]; label: string; focus?: boolean } | null>(null);
  // focus: false when a hover opens it, so no item gets the focus ring
  const open = (e: { clientX: number; clientY: number; width?: number }, items: MenuEntry[], label = "Menu", focus = true) => setMenu({ x: e.clientX, y: e.clientY, width: e.width, items, label, focus });
  const node: ReactNode = menu && <FloatingMenu {...menu} close={() => setMenu(null)} />;
  // update: new items in the open menu, where it stands (e.g. after one of them is removed)
  return { open, node, close: () => setMenu(null), update: (items: MenuEntry[]) => setMenu((m) => m && { ...m, items }) };
}
