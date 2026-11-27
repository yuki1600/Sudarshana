// Every dropdown's letter keys: a letter goes to the next option that starts with it, round and round as the key is
// pressed again (K: Karnataka, Kerala, Karnataka…), never past the letter to the nearest name after it, as macOS's
// own menus do when "kk" matches nothing. Works on a closed dropdown and in an open in-page list (Starlight's).

const starts = (o: HTMLOptionElement, key: string) =>
  !o.disabled && (o.label || o.textContent || "").trim().toLocaleLowerCase().startsWith(key);

function onKey(e: KeyboardEvent) {
  if (e.key.length !== 1 || e.key === " " || e.ctrlKey || e.metaKey || e.altKey) return;
  const t = e.target as HTMLElement | null;
  const option = t instanceof HTMLOptionElement ? t : null;
  const select = option ? option.closest("select") : t instanceof HTMLSelectElement ? t : null;
  if (!select || select.disabled || select.multiple) return;
  const options = Array.from(select.options);
  const key = e.key.toLocaleLowerCase();
  if (!options.some((o) => starts(o, key))) return;
  e.preventDefault();
  e.stopPropagation();
  const from = option ? options.indexOf(option) : select.selectedIndex;
  let next = -1;
  for (let step = 1; step <= options.length; step++) {
    const i = (from + step + options.length) % options.length;
    if (starts(options[i], key)) { next = i; break; }
  }
  if (next < 0) return;
  if (option) { options[next].focus(); return; }   // the list is open: move to it, Enter takes it
  select.selectedIndex = next;
  select.dispatchEvent(new Event("input", { bubbles: true }));
  select.dispatchEvent(new Event("change", { bubbles: true }));
}

export function startSelectKeys() {
  document.addEventListener("keydown", onKey, true);
}
