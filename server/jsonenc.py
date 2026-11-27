"""Make engine results JSON-safe: dataclasses, datetimes, NamedTuples, non-string dict keys."""
import dataclasses
import datetime as dt
import math


def to_jsonable(o):
    if dataclasses.is_dataclass(o) and not isinstance(o, type):
        return {f.name: to_jsonable(getattr(o, f.name)) for f in dataclasses.fields(o)}
    if isinstance(o, dict):
        return {str(k): to_jsonable(v) for k, v in o.items()}
    if hasattr(o, "_asdict"):  # NamedTuple
        return to_jsonable(o._asdict())
    if isinstance(o, (list, tuple, set)):
        return [to_jsonable(v) for v in o]
    if isinstance(o, (dt.datetime, dt.date)):
        return o.isoformat()
    if isinstance(o, float) and not math.isfinite(o):
        return None
    return o
