"""
Catalog of Jyotisha calculation components by functional category.

Categories map to the computational model:
  identity   → what a graha/sign represents
  strength   → how strongly it delivers (amplitude)
  state      → how effectively it delivers (modulation)
  timing     → when effects manifest (temporal gate)
  relational → how grahas modulate each other (edges)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Literal


class Category(str, Enum):
    IDENTITY = "identity"
    STRENGTH = "strength"
    STATE = "state"
    TIMING = "timing"
    RELATIONAL = "relational"


Status = Literal["implemented", "partial", "planned"]


@dataclass(frozen=True, slots=True)
class Component:
    """One modular Jyotisha calculation unit."""

    id: str
    category: Category
    name: str
    module: str
    encodes: str
    model_role: str
    status: Status = "implemented"
    entrypoint: str | None = None


# Hierarchical registry: category → components
COMPONENTS: tuple[Component, ...] = (
    # --- Identity / Nature ---
    Component(
        "identity.positions",
        Category.IDENTITY,
        "Graha & lagna positions",
        "src.jyotisha.pipeline.chart",
        "Sidereal longitudes, houses, special lagnas",
        "Semantic embedding (chart state)",
        entrypoint="compute_chart",
    ),
    Component(
        "identity.vargas",
        Category.IDENTITY,
        "Divisional charts (D1–D60)",
        "src.jyotisha.identity.vargas",
        "Varga positions per classical rules",
        "Semantic embedding",
        entrypoint="get_all_vargas",
    ),
    Component(
        "identity.panchanga",
        Category.IDENTITY,
        "Panchanga (tithi, nakshatra, yoga, karana)",
        "src.jyotisha.pipeline.chart",
        "Calendar elements at birth",
        "Semantic embedding",
        status="partial",
    ),
    Component(
        "identity.astrocartography",
        Category.IDENTITY,
        "Astrocartography / world lagna",
        "src.jyotisha.identity.astrocartography",
        "Location-dependent lagna lines",
        "Semantic embedding",
        entrypoint="compute_lagna_grid",
    ),
    # --- Strength / Intensity ---
    Component(
        "strength.shadbala",
        Category.STRENGTH,
        "Shadbala (six-fold strength)",
        "src.jyotisha.strength.shadbala",
        "Total and component bala in rupas",
        "Amplitude scalar on node",
        status="implemented",
    ),
    Component(
        "strength.bhava_bala",
        Category.STRENGTH,
        "Bhava bala",
        "src.jyotisha.strength.shadbala",
        "House strength",
        "Amplitude scalar on node",
        status="implemented",
    ),
    Component(
        "strength.dignity",
        Category.STRENGTH,
        "Uccha / neecha / moolatrikona",
        "src.jyotisha.base.constants",
        "Dignity lookup tables",
        "Amplitude scalar on node",
        status="partial",
    ),
    Component(
        "strength.panchbala",
        Category.STRENGTH,
        "Panchbala",
        "src.jyotisha.strength.panchbala",
        "Five-fold strength",
        "Amplitude scalar on node",
        status="planned",
    ),
    # --- State / Readiness ---
    Component(
        "state.avastha",
        Category.STATE,
        "Avastha (jagrat/swapna/sushupti; bala/yuva/vriddha/mrita)",
        "src.jyotisha.state.avastha",
        "Planetary readiness to deliver",
        "Modulation multiplier on strength",
        status="implemented",
    ),
    # --- Timing / Activation ---
    Component(
        "timing.vimshottari",
        Category.TIMING,
        "Vimshottari mahadasha",
        "src.jyotisha.pipeline.chart",
        "Nakshatra-based MD sequence",
        "Temporal gate scalar",
        status="partial",
    ),
    Component(
        "timing.dasha_systems",
        Category.TIMING,
        "Extended dasha systems (BPHS / Jaimini)",
        "src.jyotisha.timing.dasha.systems",
        "Rashi & nakshatra dasha builders",
        "Temporal gate scalar",
    ),
    Component(
        "timing.antardasha",
        Category.TIMING,
        "Antardasha / pratyantardasha",
        "src.jyotisha.timing.dasha.vimshottari",
        "Sub-period lists",
        "Temporal gate scalar",
        entrypoint="get_vimshottari_antardasha",
    ),
    Component(
        "timing.ashtakavarga",
        Category.TIMING,
        "Ashtakavarga (BAV / SAV)",
        "src.jyotisha.timing.ashtakavarga",
        "Benefic points per sign",
        "Temporal gate scalar",
        entrypoint="compute_ashtakavarga",
    ),
    Component(
        "timing.transits",
        Category.TIMING,
        "Transits & ingress finders",
        "src.jyotisha.timing.transits",
        "Moving graha positions & events",
        "Temporal gate scalar",
        entrypoint="compute_transit_positions",
    ),
    Component(
        "timing.mundane",
        Category.TIMING,
        "Mundane event timing",
        "src.jyotisha.timing.mundane",
        "Ingress, new moon, solar return, etc.",
        "Temporal gate scalar",
    ),
    # --- Relational / Effect ---
    Component(
        "relational.aspects",
        Category.RELATIONAL,
        "Graha & house aspects",
        "src.jyotisha.relational.aspects",
        "Aspect grid with strengths",
        "Edge weight in attention matrix",
        status="implemented",
    ),
    Component(
        "relational.arudha",
        Category.RELATIONAL,
        "Arudha padas & Upapada",
        "src.jyotisha.relational.arudha",
        "Perception / relationship significators",
        "Edge weight in attention matrix",
        status="implemented",
    ),
    Component(
        "relational.match",
        Category.RELATIONAL,
        "Das Kuta (marriage compatibility)",
        "src.jyotisha.relational.match.core",
        "Synastry scores from Moon nakshatra",
        "Edge weight in attention matrix",
        entrypoint="calculate_match",
    ),
    Component(
        "relational.yogas",
        Category.RELATIONAL,
        "Classical yogas (Raja, Dhana, …)",
        "src.jyotisha.relational.yogas",
        "Combination rules",
        "Edge weight in attention matrix",
        status="planned",
    ),
)


def by_category(category: Category) -> list[Component]:
    return [c for c in COMPONENTS if c.category == category]


def get_component(component_id: str) -> Component | None:
    for c in COMPONENTS:
        if c.id == component_id:
            return c
    return None
