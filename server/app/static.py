"""static: part of app (split from one module; see __init__.py)."""
import os
from fastapi.staticfiles import StaticFiles
from .main import app

_dist = os.path.join(os.path.dirname(__file__), "..", "..", "web", "dist")
if os.path.isdir(_dist):  # registered last so it never shadows /api
    app.mount("/", StaticFiles(directory=_dist, html=True), name="web")
