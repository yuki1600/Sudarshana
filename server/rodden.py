"""The Rodden library: AA- and A-rated public charts any account can open from Open chart, each with its Predictions
facts (biography and all) taken from its source file. Built by databases/build_rodden_db.py; empty until it has run."""
import functools
import gzip
import json
import os
import re
import sqlite3

DB = os.path.join(os.path.dirname(__file__), "..", "databases", "rodden.db")


def _query(sql: str, *args) -> list:
    if not os.path.exists(DB):
        return []
    c = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    try:
        return c.execute(sql, args).fetchall()
    finally:
        c.close()


@functools.cache
def listing() -> bytes:
    """Every chart as [id, name, rating, year, month, day, hour, place], by name, gzipped: it runs to megabytes, so it is made the
    first time Open chart asks for it and kept compressed (not compressed again for every request)."""
    rows = _query("SELECT id, name, rating, year, month, day, hour, place FROM charts ORDER BY id")
    return gzip.compress(json.dumps(rows, ensure_ascii=False, separators=(",", ":")).encode(), 6)


def chart(id: int) -> dict | None:
    """One chart as a .vs file's text, under its name."""
    r = _query("SELECT name, content FROM charts WHERE id = ?", id)
    return {"name": r[0][0], "content": r[0][1]} if r else None


MONTHS = {m: i for i, m in enumerate(("january", "february", "march", "april", "may", "june", "july", "august", "september",
                                       "october", "november", "december"), 1)}
# the person's own death among the file's events; "Death of Mother" and the like are someone else's, an attempt or a return is no death
_OWN_DEATH = re.compile(r"^Death(?!: Suicide Attempt| and Came back| of )")
_WHEN = re.compile(r"^(\d{1,2}) ([A-Za-z]+) (\d{1,4})(?:.*?\b(\d{1,2}):(\d{2}))?")


def with_death(f: dict) -> dict:
    """The Predictions tab's Alive / Dead from the person's death event: Dead, with its date ("1962-08-05") and time when the file gives them."""
    death = next((e for e in reversed(f.get("events") or []) if _OWN_DEATH.match(e.get("kind", ""))), None)
    if not death or (f.get("answers") or {}).get("status"):
        return f
    a = {**f.get("answers", {}), "status": "Dead"}
    m = _WHEN.match(death.get("note", "").split(" · ")[0])
    if m and m.group(2).lower() in MONTHS:
        a["death.date"] = "%04d-%02d-%02d" % (int(m.group(3)), MONTHS[m.group(2).lower()], int(m.group(1)))
        if m.group(4):
            a["death.time"] = "%02d:%s" % (int(m.group(4)), m.group(5))
    return {**f, "answers": a}


def facts(key: str) -> dict | None:
    """The Predictions facts of the library chart with this chart key (name and birth date), or None."""
    r = _query("SELECT facts FROM charts WHERE key = ? LIMIT 1", key)
    return with_death(json.loads(r[0][0])) if r else None
