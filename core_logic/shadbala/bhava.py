"""bhava: part of shadbala (split from one module; see __init__.py)."""
from __future__ import annotations
from typing import Dict, Optional, Any
from ..utils import norm360
from .components import NATURAL_BENEFICS, compute_full_shadbala
from .common import PLANETS, SIGN_RULERS

# ===========================================================================
# 8. Bhava Bala (Twelve House Strengths) Engine
# Source: BPHS 27.26-31 (Bhava Bala)
# ===========================================================================

# Optimal house for sign categories to receive Digbala (60 virupas)
# Nara (Human: Gem, Vir, Lib, Aqu, 1st half Sgr) -> 1st house
# Jala (Water: Can, Psc, 2nd half Cap) -> 4th house
# Keeta (Insect: Sco) -> 7th house
# Chatushpada (Quadruped: Ari, Tau, Leo, 2nd half Sgr, 1st half Cap) -> 10th house
SIGN_OPTIMAL_BHAVA = {
    0: 10,  # Aries: Chatushpada (10th)
    1: 10,  # Taurus: Chatushpada (10th)
    2: 1,   # Gemini: Nara (1st)
    3: 4,   # Cancer: Jala (4th)
    4: 10,  # Leo: Chatushpada (10th)
    5: 1,   # Virgo: Nara (1st)
    6: 1,   # Libra: Nara (1st)
    7: 7,   # Scorpio: Keeta (7th)
    8: 1,   # Sagittarius: Nara (1st)
    9: 10,  # Capricorn: Chatushpada (10th)
    10: 1,  # Aquarius: Nara (1st)
    11: 4   # Pisces: Jala (4th)
}

def compute_bhava_bala(
    lagna_lon: float,
    planet_longitudes: Dict[str, float],
    planet_shadbala_virupas: Optional[Dict[str, float]] = None
) -> Dict[int, Dict[str, Any]]:
    """
    Computes Bhava Bala for all 12 houses according to Parasara:
    1. Bhava Adhipati Bala: Lord's Shadbala
    2. Bhava Digbala: House directional strength (based on sign nature)
    3. Bhava Drishti Bala: Aspectual strength cast upon the cusp
    Returns comprehensive breakdown for houses 1 through 12.
    """
    if planet_shadbala_virupas is None:
        # Compute baseline shadbala if not provided
        sb = compute_full_shadbala(planet_longitudes, lagna_lon, 12.0, 6.0, 18.0)
        planet_shadbala_virupas = {p: sb[p]["total_virupas"] for p in sb}

    bhava_results = {}
    
    for h in range(1, 13):
        # House cusp longitude (equal house system from Lagna)
        cusp_lon = norm360(lagna_lon + (h - 1) * 30.0)
        sign_idx = int(cusp_lon // 30.0)
        lord = SIGN_RULERS[sign_idx]
        
        # 1. Adhipati Bala (Lord's Shadbala in Virupas)
        adhipati_virupas = planet_shadbala_virupas.get(lord, 300.0)
        
        # 2. Digbala (Directional Strength of House)
        opt_h = SIGN_OPTIMAL_BHAVA.get(sign_idx, 1)
        # Distance between current house and optimal house (in houses 0..6)
        h_diff = abs(h - opt_h)
        if h_diff > 6:
            h_diff = 12 - h_diff
        digbala_virupas = round(60.0 * (1.0 - (h_diff / 6.0)), 2)
        
        # 3. Drishti Bala (Aspects on Bhava Cusp)
        drishti_virupas = 0.0
        for p, p_lon in planet_longitudes.items():
            if p not in PLANETS:
                continue
            arc = norm360(cusp_lon - p_lon)
            # Standard Parasari aspect percentage on house cusp
            # 7th aspect = 100% (60 virupas)
            # Special aspects for Mars (4th/8th), Jupiter (5th/9th), Saturn (3rd/10th)
            asp = 0.0
            if 150.0 <= arc <= 210.0:
                asp = 60.0 * (1.0 - abs(arc - 180.0) / 30.0)
            elif p == "Mars" and (90.0 <= arc <= 150.0 or 210.0 <= arc <= 270.0):
                target = 120.0 if arc <= 180.0 else 240.0
                asp = 45.0 * max(0.0, 1.0 - abs(arc - target) / 30.0)
            elif p == "Jupiter" and (100.0 <= arc <= 160.0 or 220.0 <= arc <= 280.0):
                target = 120.0 if arc <= 180.0 else 240.0
                asp = 30.0 * max(0.0, 1.0 - abs(arc - target) / 30.0)
            elif p == "Saturn" and (40.0 <= arc <= 100.0 or 250.0 <= arc <= 310.0):
                target = 60.0 if arc <= 180.0 else 270.0
                asp = 30.0 * max(0.0, 1.0 - abs(arc - target) / 30.0)
                
            # Benefics add strength, Malefics reduce strength
            if p in NATURAL_BENEFICS:
                drishti_virupas += asp * 0.25
            else:
                drishti_virupas -= asp * 0.25
                
        drishti_virupas = round(drishti_virupas, 2)
        total_virupas = round(adhipati_virupas + digbala_virupas + drishti_virupas, 2)
        total_rupas = round(total_virupas / 60.0, 2)
        
        bhava_results[h] = {
            "house": h,
            "cusp_longitude": round(cusp_lon, 2),
            "sign_index": sign_idx,
            "lord": lord,
            "adhipati_bala": adhipati_virupas,
            "dig_bala": digbala_virupas,
            "drishti_bala": drishti_virupas,
            "total_virupas": total_virupas,
            "total_rupas": total_rupas,
            "strength_rank": 0  # Populated after ranking
        }
        
    # Rank houses by total virupas
    sorted_houses = sorted(bhava_results.values(), key=lambda x: x["total_virupas"], reverse=True)
    for rank, item in enumerate(sorted_houses, 1):
        bhava_results[item["house"]]["strength_rank"] = rank
        
    return bhava_results


def generate_bhava_bala_ascii_graph(bhava_bala: Dict[int, Dict[str, Any]]) -> str:
    """
    Renders an ASCII horizontal bar chart ranking all 12 houses by Bhava Bala Virupas.
    Benchmark: 350 Virupas (~5.83 Rupas).
    """
    lines = [
        "=========================================================================",
        "                     BHAVA BALA PROFILE GRAPH (12 HOUSES)                ",
        "=========================================================================",
        "Bhava | Lord     | Virupas | Rupas | Rank | Visual Bar (Scale: 1 block = 15 virupas)",
        "------+----------+---------+-------+------+----------------------------------"
    ]
    
    # Sort in canonical house order 1 to 12
    for h in range(1, 13):
        data = bhava_bala.get(h, {})
        virupas = data.get("total_virupas", 0.0)
        rupas = data.get("total_rupas", 0.0)
        lord = data.get("lord", "N/A")
        rank = data.get("strength_rank", 0)
        
        bar_len = int(max(0, virupas) // 15)
        # Highlight benchmark at 350 virupas (approx block 23)
        bar = "█" * min(bar_len, 40)
        
        tag = "(Strong)" if virupas >= 400 else ("(Moderate)" if virupas >= 320 else "(Weak)")
        lines.append(f"H{h:<4} | {lord:<8} | {virupas:>7.1f} | {rupas:>5.2f} | #{rank:<3} | {bar} {tag}")
        
    lines.append("-------------------------------------------------------------------------")
    lines.append("Benchmark: 350 Virupas (approx 23 blocks) represents standard bhava vitality.")
    lines.append("=========================================================================")
    return "\n".join(lines)


def generate_bhava_bala_graph_svg(
    bhava_bala: Dict[int, Dict[str, Any]],
    width: int = 760,
    height: int = 380
) -> str:
    """
    Generates a responsive, modern dark-mode SVG vector bar chart of Bhava Bala
    featuring gradient fills, benchmark threshold line, rank badges, and crisp typography.
    """
    max_virupas = max((d.get("total_virupas", 400.0) for d in bhava_bala.values()), default=500.0)
    y_scale = max(600.0, max_virupas * 1.15)
    
    margin_left = 60
    margin_bottom = 50
    margin_top = 40
    margin_right = 30
    
    chart_w = width - margin_left - margin_right
    chart_h = height - margin_top - margin_bottom
    
    bar_width = chart_w / 12.0
    bar_gap = 10.0
    
    # Benchmark 350 virupas y-coord
    bench_y = margin_top + chart_h * (1.0 - (350.0 / y_scale))
    
    svg_elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%" style="background:#0f172a; border-radius:12px; font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif;">',
        '  <defs>',
        '    <linearGradient id="strongBar" x1="0" y1="0" x2="0" y2="1">',
        '      <stop offset="0%" stop-color="#10b981" />',
        '      <stop offset="100%" stop-color="#047857" />',
        '    </linearGradient>',
        '    <linearGradient id="modBar" x1="0" y1="0" x2="0" y2="1">',
        '      <stop offset="0%" stop-color="#06b6d4" />',
        '      <stop offset="100%" stop-color="#0e7490" />',
        '    </linearGradient>',
        '    <linearGradient id="weakBar" x1="0" y1="0" x2="0" y2="1">',
        '      <stop offset="0%" stop-color="#f59e0b" />',
        '      <stop offset="100%" stop-color="#b45309" />',
        '    </linearGradient>',
        '  </defs>',
        f'  <text x="{width/2}" y="24" fill="#f8fafc" font-size="16" font-weight="bold" text-anchor="middle">Bhava Bala (12 Bhava Balas) Profile</text>',
        f'  <!-- Benchmark threshold line at 350 Virupas -->',
        f'  <line x1="{margin_left}" y1="{bench_y}" x2="{width - margin_right}" y2="{bench_y}" stroke="#94a3b8" stroke-dasharray="4,4" stroke-width="1.5" />',
        f'  <text x="{width - margin_right}" y="{bench_y - 6}" fill="#94a3b8" font-size="11" text-anchor="end">Par Benchmark (350 Virupas)</text>'
    ]
    
    for h in range(1, 13):
        data = bhava_bala.get(h, {})
        virupas = data.get("total_virupas", 0.0)
        rupas = data.get("total_rupas", 0.0)
        lord = data.get("lord", "")
        
        # Color gradient based on strength
        if virupas >= 400.0:
            fill_grad = "url(#strongBar)"
        elif virupas >= 320.0:
            fill_grad = "url(#modBar)"
        else:
            fill_grad = "url(#weakBar)"
            
        b_height = chart_h * (virupas / y_scale)
        bx = margin_left + (h - 1) * bar_width + (bar_gap / 2.0)
        by = margin_top + chart_h - b_height
        bw = bar_width - bar_gap
        
        # Bar rect
        svg_elements.append(f'  <rect x="{bx:.1f}" y="{by:.1f}" width="{bw:.1f}" height="{b_height:.1f}" rx="4" fill="{fill_grad}"><title>H{h} ({lord}): {virupas} Virupas ({rupas} Rupas)</title></rect>')
        
        # Value label on top of bar
        svg_elements.append(f'  <text x="{bx + bw/2.0:.1f}" y="{by - 6:.1f}" fill="#e2e8f0" font-size="10" font-weight="600" text-anchor="middle">{int(virupas)}</text>')
        
        # House label below bar
        svg_elements.append(f'  <text x="{bx + bw/2.0:.1f}" y="{margin_top + chart_h + 16:.1f}" fill="#cbd5e1" font-size="11" font-weight="bold" text-anchor="middle">H{h}</text>')
        
        # Lord label below house
        svg_elements.append(f'  <text x="{bx + bw/2.0:.1f}" y="{margin_top + chart_h + 30:.1f}" fill="#64748b" font-size="9" text-anchor="middle">{lord[:3]}</text>')
        
    svg_elements.append('</svg>')
    return "\n".join(svg_elements)
