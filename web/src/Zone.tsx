import { useEffect, useMemo, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { HALF_HOURS, ZONES, type ZoneAt, parse, round, signed, countryOf, zoneLabel, zoneOffset } from "./zones";

/** Under the input, or over it when the window has more room above. */
const place = (r: DOMRect): React.CSSProperties => {
  const below = innerHeight - r.bottom - 8, up = below < 200 && r.top > below;
  const width = Math.max(r.width, 300);
  return { left: Math.min(r.left, innerWidth - width - 8), width, maxHeight: Math.min(300, (up ? r.top - 8 : below) - 2),
    ...(up ? { bottom: innerHeight - r.top + 2 } : { top: r.bottom + 2 }) };
};

/** The time zone, everywhere one is set: hours east of GMT, signed and bold; a click lists the world's zones, and a zone picked from it
 *  follows ``at`` (so DST comes and goes with the date). Typing a number sets the hours by hand; typing letters searches the list. */
export function ZoneInput({ value, onChange, at, disabled, required, placeholder, note, named, zone: heldZone, onZone }: {
  zone?: string | null; onZone?: (z: string | null) => void;   // the picked zone, held by the form (so it can keep it over a refresh)
  named?: string;   // the zone the value came from outside with (a picked place's), shown till one is picked here
  value: string; onChange: (hours: string) => void; at: ZoneAt | null; disabled?: boolean; required?: boolean; placeholder?: string; note?: React.ReactNode;
}) {
  const [ownZone, setOwnZone] = useState<string | null>(null);
  const [zone, setZone] = onZone ? [heldZone ?? null, onZone] : [ownZone, setOwnZone];
  const [text, setText] = useState<string | null>(null);     // null: not typing, so the value shows
  const [box, setBox] = useState<DOMRect | null>(null);   // the input, where the list opens; null: closed
  const open = box !== null;
  const inputRef = useRef<HTMLInputElement>(null);
  const show = () => { if (!open) setBox(inputRef.current!.getBoundingClientRect()); };
  const [active, setActive] = useState(-1);
  const sent = useRef(value);
  const listRef = useRef<HTMLUListElement>(null);
  const emit = (v: string) => { sent.current = v; onChange(v); };

  const ok = at && [at.y, at.mo, at.d, at.hour].every(Number.isFinite);
  // set from outside (a place picked, Now, a found chart): no longer the named zone, unless the zone keeps those hours then
  useEffect(() => {
    if (value === sent.current) return;
    sent.current = value;
    if (zone && !(ok && String(round(zoneOffset(zone, at!))) === value)) setZone(null);
  }, [value]); // eslint-disable-line react-hooks/exhaustive-deps
  // a named zone follows the date and time
  useEffect(() => { if (zone && ok) { const v = String(round(zoneOffset(zone, at!))); if (v !== sent.current) emit(v); } },
    [zone, at?.y, at?.mo, at?.d, at?.hour]); // eslint-disable-line react-hooks/exhaustive-deps

  const rows = useMemo(() => {
    if (!open) return [];
    const when = ok ? at! : (() => { const n = new Date(); return { y: n.getFullYear(), mo: n.getMonth() + 1, d: n.getDate(), hour: n.getHours() }; })();
    const zones: { z: string | null; h: number }[] = ZONES.map((z) => ({ z, h: round(zoneOffset(z, when)) }));
    const have = new Set(zones.map((r) => r.h));
    // the half hours no zone keeps on that date, as bare hours, so every half hour is there
    return [...zones, ...HALF_HOURS.filter((h) => !have.has(h)).map((h) => ({ z: null, h }))].sort((a, b) => a.h - b.h || (a.z ?? "").localeCompare(b.z ?? ""));
  }, [open, at?.y, at?.mo, at?.d, at?.hour]); // eslint-disable-line react-hooks/exhaustive-deps
  const typed = text === null ? null : parse(text);
  const q = text !== null && typed === null ? text.trim().toLowerCase().replace(/\s+/g, " ") : "";
  // search the shown name and the full one at word starts, so "usa", "america" and "new york" find New York (and "usa" not Lusaka)
  // typed hours: the zones at those hours
  // and zones of a country named so first, so "india" puts India before Indiana and the Indian Ocean
  const shown = q ? rows.filter((r) => r.z && ` ${zoneLabel(r.z)} ${r.z.replace(/_/g, " ")}`.toLowerCase().replace(/[/·]/g, " ").includes(` ${q}`))
      .sort((a, b) => Number(!countryOf(a.z!).toLowerCase().startsWith(q)) - Number(!countryOf(b.z!).toLowerCase().startsWith(q)))
    : typed !== null ? rows.filter((r) => r.h === round(typed)) : rows;

  useEffect(() => { setActive(-1); }, [q, typed]);
  useEffect(() => {   // opened: the zone in use, or the first at this offset, in view
    if (!open || active >= 0 || q) return;
    const i = shown.findIndex((r) => (zone ? r.z === zone : String(r.h) === value));
    if (i >= 0) listRef.current?.children[i]?.scrollIntoView({ block: "center" });
  }, [open]); // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => { if (active >= 0) listRef.current?.children[active]?.scrollIntoView({ block: "nearest" }); }, [active]);

  const pick = ({ z, h }: { z: string | null; h: number }) => {
    setZone(z); setText(null); setBox(null);
    if (!z) emit(String(h)); else if (ok) emit(String(round(zoneOffset(z, at!))));
  };
  const close = () => { setBox(null); setText(null); };
  // the list floats over the page (so no dialog cuts it off), so it closes when anything else scrolls
  useEffect(() => {
    if (!open) return;
    const away = (e: Event) => { if (!listRef.current?.contains(e.target as Node)) close(); };
    addEventListener("scroll", away, true); addEventListener("resize", away);
    return () => { removeEventListener("scroll", away, true); removeEventListener("resize", away); };
  }, [open]); // eslint-disable-line react-hooks/exhaustive-deps
  const onKey = (e: React.KeyboardEvent) => {
    if (e.key === "Escape" && open) { e.preventDefault(); close(); }
    else if (e.key === "ArrowDown") { e.preventDefault(); show(); setActive((i) => Math.min(shown.length - 1, i + 1)); }
    else if (e.key === "ArrowUp") { e.preventDefault(); setActive((i) => Math.max(0, i - 1)); }
    else if (e.key === "Enter" && open) {   // the highlighted zone, else the top match of a search; typed hours stand as typed
      e.preventDefault();
      const r = shown[active >= 0 ? active : q ? 0 : -1];
      if (r) pick(r); else close();
    }
  };
  return (
    <label className="zone-field">
      <span>Time zone (GMT ±){note}</span>
      <input className="zone-input" value={text ?? (value === "" ? "" : `${signed(value)} hrs${zone || named ? `  ·  ${zoneLabel(zone ?? named!)}` : ""}`)} disabled={disabled} required={required} placeholder={placeholder} autoComplete="off" spellCheck={false}
        role="combobox" aria-expanded={open} aria-controls="zone-list" aria-autocomplete="list" aria-activedescendant={active >= 0 ? `zone-${active}` : undefined}
        ref={inputRef} onFocus={(e) => e.target.select()} onClick={(e) => { if (text === null) e.currentTarget.select(); show(); }} onBlur={close} onKeyDown={onKey}
        onChange={(e) => {
          const s = e.target.value;
          setText(s); show();
          const h = parse(s);
          if (h !== null) { setZone(null); emit(String(h)); }
        }} />
      {box && createPortal(
        <ul className="hits zone-list" id="zone-list" role="listbox" ref={listRef} style={place(box)}>
          {shown.length ? shown.map((r, i) => (
            <li key={r.z ?? `h${r.h}`} id={`zone-${i}`} role="option" aria-selected={r.z !== null && r.z === zone}>
              {/* mousedown, not click: the input's blur would close the list first */}
              <button type="button" tabIndex={-1} className={i === active ? "active" : undefined} onMouseEnter={() => setActive(i)}
                onMouseDown={(e) => { e.preventDefault(); pick(r); }}>
                <b>{signed(r.h)} hrs</b> {r.z && zoneLabel(r.z)}
              </button>
            </li>
          )) : <li className="muted hits-note">No matching time zone</li>}
        </ul>, inputRef.current?.closest("dialog") ?? document.body)}   {/* a modal dialog sits over the body, so the list goes inside it */}
    </label>
  );
}
