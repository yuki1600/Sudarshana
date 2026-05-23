"""
Sudarshana Jyotisha engine — modular calculations by functional category.

Categories (see registry.py):
  identity   — rashi, nakshatra, positions, vargas
  strength   — shadbala, dignity, bhava bala
  state      — avastha (planned)
  timing     — dasha, transits, ashtakavarga, mundane
  relational — aspects, arudha, match, yogas (planned)
"""

from . import base, identity, strength, state, timing, relational, pipeline
from .registry import Category, Component, COMPONENTS, by_category, get_component
from .pipeline import compute_chart, compute_chart_with_tzname, init_ephe

__all__ = [
    "base",
    "identity",
    "strength",
    "state",
    "timing",
    "relational",
    "pipeline",
    "Category",
    "Component",
    "COMPONENTS",
    "by_category",
    "get_component",
    "compute_chart",
    "compute_chart_with_tzname",
    "init_ephe",
]
