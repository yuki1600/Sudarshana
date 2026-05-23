"""
Avastha (planetary state / readiness).
Implements five classical avastha systems:
1. Baladi Avasthas (Age-based)
2. Jagratadi Avasthas (Alertness-based)
3. Deeptaadi Avasthas (Dignity-based)
4. Lajjitadi Avasthas (Psychological states)
5. Shayanadi Avasthas (Activity/Posture states)
"""

from __future__ import annotations

import pandas as pd
from typing import Any

from src.jyotisha.base.constants import (
    DEBIL, EXALT, MOOLATR, SIGN_INDEX, SIGN_LORD, RASHI_SA,
    PERM_FRIENDS, PERM_ENEMIES
)


def relation_to_lord(graha: str, lord: str) -> str:
    # Safe checks for Rahu/Ketu or others not in PERM_* constants
    if graha not in PERM_FRIENDS:
        return "neutral"
    if lord in PERM_FRIENDS[graha] and graha in PERM_FRIENDS.get(lord, set()):
        return "great_friend"
    if lord in PERM_ENEMIES[graha] and graha in PERM_ENEMIES.get(lord, set()):
        return "great_enemy"
    if lord in PERM_FRIENDS[graha] or graha in PERM_FRIENDS.get(lord, set()):
        return "friend"
    if lord in PERM_ENEMIES[graha] or graha in PERM_ENEMIES.get(lord, set()):
        return "enemy"
    return "neutral"


def in_moolatrikona(graha: str, lon_: float) -> bool:
    if graha not in MOOLATR:
        return False
    s, a, b = MOOLATR[graha]
    si = SIGN_INDEX[s]
    deg = (lon_ - si * 30.0) % 360.0
    if deg < 0:
        deg += 360.0
    return 0.0 <= deg < 30.0 and (a <= deg <= b)


def compute_avastha(chart: dict[str, Any]) -> pd.DataFrame:
    """
    Computes Baladi, Jagratadi, Deeptaadi, Lajjitadi, and Shayanadi Avasthas
    for the planets in the chart.
    """
    points = chart.get("points")
    if points is None:
        return pd.DataFrame()

    if hasattr(points, "to_dict"):
        points_list = points.to_dict(orient="records")
    else:
        points_list = points

    janma_ghatis = chart.get("janma_ghatis", 15.0)

    # Find Moon longitude and Ascendant Sign Index for Shayanadi calculations
    moon_point = next((p for p in points_list if p["Point"] == "Moon"), None)
    moon_lon = moon_point["Longitude (Dec)"] if moon_point else 0.0

    asc_point = next((p for p in points_list if p["Point"] == "Ascendant (1st House Cusp)"), None)
    asc_sign_idx = asc_point["Rashi_Idx"] if asc_point else 0

    # Planet indexes for Shayanadi (Sun=1 ... Ketu=9)
    planet_idxs = {
        "Sun": 1, "Moon": 2, "Mars": 3, "Mercury": 4,
        "Jupiter": 5, "Venus": 6, "Saturn": 7,
        "Rahu (true)": 8, "Ketu (true)": 9
    }

    # Identify houses of all planets for Lajjitadi calculations
    planet_positions = {}
    for pt in points_list:
        p_name = pt.get("Point")
        p_lon = pt.get("Longitude (Dec)")
        if p_name and p_lon is not None:
            r_idx = pt.get("Rashi_Idx")
            if r_idx is None:
                r_idx = int(p_lon // 30.0) % 12
            house_num = (r_idx - asc_sign_idx + 12) % 12 + 1
            planet_positions[p_name] = {
                "lon": p_lon,
                "rashi": r_idx,
                "house": house_num
            }

    target_grahas = {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu (true)", "Ketu (true)"}
    rows = []

    # Get Sun position for combustion calculations
    sun_pos = planet_positions.get("Sun")
    sun_lon = sun_pos["lon"] if sun_pos else 0.0

    for pt in points_list:
        planet = pt.get("Point")
        if planet not in target_grahas:
            continue

        lon = pt.get("Longitude (Dec)", 0.0)
        rashi_idx = pt.get("Rashi_Idx")
        if rashi_idx is None:
            rashi_idx = int(lon // 30.0) % 12

        # ----------------------------------------------------
        # 1. Baladi Avastha
        # ----------------------------------------------------
        deg_in_sign = lon % 30.0
        is_odd = (rashi_idx % 2 == 0)

        if is_odd:
            if 0.0 <= deg_in_sign < 6.0:
                baladi_name = "Bala"
            elif 6.0 <= deg_in_sign < 12.0:
                baladi_name = "Kumara"
            elif 12.0 <= deg_in_sign < 18.0:
                baladi_name = "Yuva"
            elif 18.0 <= deg_in_sign < 24.0:
                baladi_name = "Vriddha"
            else:
                baladi_name = "Mrita"
        else:
            if 0.0 <= deg_in_sign < 6.0:
                baladi_name = "Mrita"
            elif 6.0 <= deg_in_sign < 12.0:
                baladi_name = "Vriddha"
            elif 12.0 <= deg_in_sign < 18.0:
                baladi_name = "Yuva"
            elif 18.0 <= deg_in_sign < 24.0:
                baladi_name = "Kumara"
            else:
                baladi_name = "Bala"

        # ----------------------------------------------------
        # 2. Jagratadi Avastha
        # ----------------------------------------------------
        lord = SIGN_LORD.get(rashi_idx)
        if lord == planet:
            dignity = "own"
        elif planet in EXALT and SIGN_INDEX.get(EXALT[planet][0]) == rashi_idx:
            dignity = "exaltation"
        elif planet in DEBIL and SIGN_INDEX.get(DEBIL[planet][0]) == rashi_idx:
            dignity = "debilitation"
        elif planet == "Rahu (true)" and rashi_idx == 1:
            dignity = "exaltation"
        elif planet == "Rahu (true)" and rashi_idx == 7:
            dignity = "debilitation"
        elif planet == "Ketu (true)" and rashi_idx == 7:
            dignity = "exaltation"
        elif planet == "Ketu (true)" and rashi_idx == 1:
            dignity = "debilitation"
        else:
            dignity = "other"

        if dignity in {"own", "exaltation"}:
            jagratadi_name = "Jagrat (Awake)"
        elif dignity == "debilitation":
            jagratadi_name = "Sushupti (Deep Sleep)"
        else:
            if lord:
                rel = relation_to_lord(planet, lord)
                if rel in {"great_friend", "friend", "neutral"}:
                    jagratadi_name = "Swapna (Dreaming)"
                else:
                    jagratadi_name = "Sushupti (Deep Sleep)"
            else:
                jagratadi_name = "Swapna (Dreaming)"

        # ----------------------------------------------------
        # 3. Deeptaadi Avastha (Dignity-based)
        # ----------------------------------------------------
        # Combustion check
        combust_orbs = {
            "Moon": 12.0, "Mars": 17.0, "Mercury": 14.0,
            "Jupiter": 11.0, "Venus": 10.0, "Saturn": 15.0
        }
        is_combust = False
        if planet != "Sun" and planet in combust_orbs:
            orb = combust_orbs[planet]
            diff = abs(lon - sun_lon) % 360
            if diff > 180:
                diff = 360 - diff
            if diff < orb:
                is_combust = True

        if dignity == "exaltation":
            deeptaadi_name = "Dīpta (Exalted)"
        elif dignity == "own":
            deeptaadi_name = "Svastha (Own Sign)"
        elif is_combust:
            deeptaadi_name = "Vikala (Combust)"
        elif dignity == "debilitation":
            deeptaadi_name = "Khala (Debilitated)"
        else:
            if lord:
                rel = relation_to_lord(planet, lord)
                if rel in {"great_friend", "friend"}:
                    deeptaadi_name = "Mudita (Friendly Sign)"
                elif lord in {"Jupiter", "Venus", "Mercury", "Moon"}:
                    deeptaadi_name = "Śānta (Benefic Sign)"
                elif rel == "neutral":
                    deeptaadi_name = "Dīna (Neutral Sign)"
                else:
                    deeptaadi_name = "Duḥkhita (Enemy Sign)"
            else:
                deeptaadi_name = "Dīna (Neutral Sign)"

        # ----------------------------------------------------
        # 4. Lajjitadi Avastha (Psychological States)
        # ----------------------------------------------------
        # Helper to check aspect: target house receives aspect from source planet
        # target_house (1-12), source_planet
        def aspects_house(src_pl: str, tgt_hs: int) -> bool:
            pos = planet_positions.get(src_pl)
            if not pos:
                return False
            src_hs = pos["house"]
            diff = (tgt_hs - src_hs + 12) % 12
            # All planets aspect 7th house (diff == 6)
            if diff == 6:
                return True
            if src_pl == "Mars" and diff in {3, 7}:  # 4th and 8th
                return True
            if src_pl == "Jupiter" and diff in {4, 8}:  # 5th and 9th
                return True
            if src_pl == "Saturn" and diff in {2, 9}:  # 3rd and 10th
                return True
            if src_pl in {"Rahu (true)", "Ketu (true)"} and diff in {4, 8}:  # 5th and 9th
                return True
            return False

        # Gather conjunct and aspecting planets
        my_pos = planet_positions[planet]
        my_house = my_pos["house"]
        my_rashi = my_pos["rashi"]

        conjunct_planets = [p for p, info in planet_positions.items() if p != planet and info["rashi"] == my_rashi]
        aspecting_planets = [p for p in planet_positions if p != planet and aspects_house(p, my_house)]

        is_lajjita = False
        is_garvita = False
        is_kshudhita = False
        is_trishita = False
        is_mudita_laj = False
        is_kshobhita = False

        # Garvita
        if dignity == "exaltation" or in_moolatrikona(planet, lon):
            is_garvita = True

        # Lajjita
        # Placed in 5th house and conjunct Sun, Mars, Saturn, Rahu, Ketu
        malefics = {"Sun", "Mars", "Saturn", "Rahu (true)", "Ketu (true)"}
        if my_house == 5 and any(p in malefics for p in conjunct_planets):
            is_lajjita = True
        # Or conjunct its enemy
        if lord and relation_to_lord(planet, lord) in {"enemy", "great_enemy"}:
            is_lajjita = True
        if any(relation_to_lord(planet, cp) in {"enemy", "great_enemy"} for cp in conjunct_planets):
            is_lajjita = True

        # Kshudhita
        # Placed in enemy sign or conjunct/aspected by enemy, or aspected by malefic
        if lord and relation_to_lord(planet, lord) in {"enemy", "great_enemy"}:
            is_kshudhita = True
        if any(relation_to_lord(planet, cp) in {"enemy", "great_enemy"} for cp in conjunct_planets):
            is_kshudhita = True
        if any(relation_to_lord(planet, ap) in {"enemy", "great_enemy"} for ap in aspecting_planets):
            is_kshudhita = True
        if any(ap in malefics for ap in aspecting_planets):
            is_kshudhita = True

        # Trishita
        # Placed in water sign (Cancer, Scorpio, Pisces) and aspected by malefic, no benefic aspect
        is_water = my_rashi in {3, 7, 11}  # Karka, Vrischika, Meena
        aspected_by_mal = any(ap in malefics for ap in aspecting_planets)
        aspected_by_ben = any(ap in {"Jupiter", "Venus", "Mercury", "Moon"} for ap in aspecting_planets)
        if is_water and aspected_by_mal and not aspected_by_ben:
            is_trishita = True

        # Mudita
        # Placed in friend sign, conjunct/aspected by friend, conjunct Jupiter
        if lord and relation_to_lord(planet, lord) in {"great_friend", "friend"}:
            is_mudita_laj = True
        if any(relation_to_lord(planet, cp) in {"great_friend", "friend"} for cp in conjunct_planets):
            is_mudita_laj = True
        if any(relation_to_lord(planet, ap) in {"great_friend", "friend"} for ap in aspecting_planets):
            is_mudita_laj = True
        if "Jupiter" in conjunct_planets:
            is_mudita_laj = True

        # Kshobhita
        # Conjunct Sun (combust), or aspected by/conjunct malefic/enemy
        if is_combust:
            is_kshobhita = True
        if any(ap in malefics or relation_to_lord(planet, ap) in {"enemy", "great_enemy"} for ap in aspecting_planets):
            is_kshobhita = True
        if any(cp in malefics or relation_to_lord(planet, cp) in {"enemy", "great_enemy"} for cp in conjunct_planets):
            is_kshobhita = True

        lajjitadi_states = []
        if is_lajjita:
            lajjitadi_states.append("Lajjita (Ashamed)")
        if is_garvita:
            lajjitadi_states.append("Garvita (Proud)")
        if is_kshudhita:
            lajjitadi_states.append("Kṣudhita (Hungry)")
        if is_trishita:
            lajjitadi_states.append("Tṛṣita (Thirsty)")
        if is_mudita_laj:
            lajjitadi_states.append("Mudita (Delighted)")
        if is_kshobhita:
            lajjitadi_states.append("Kṣobhita (Agitated)")

        lajjitadi_name = ", ".join(lajjitadi_states) if lajjitadi_states else "Sama (Neutral)"

        # ----------------------------------------------------
        # 5. Shayanadi Avastha (Activity/Posture States)
        # ----------------------------------------------------
        # Nakshatra of planet
        nak_p = int(lon // (360.0 / 27.0)) + 1
        # Planet index (Sun=1...Ketu=9)
        idx_p = planet_idxs.get(planet, 1)
        # Navamsha of planet (1-9)
        nav_p = int((lon % 30.0) / (30.0 / 9.0)) + 1
        # Nakshatra of birth (Moon nakshatra)
        nak_birth = int(moon_lon // (360.0 / 27.0)) + 1

        sum_val = (nak_p * idx_p * nav_p) + nak_birth + int(janma_ghatis) + (asc_sign_idx + 1)
        rem = sum_val % 12

        shayanadi_map = {
            1: "Śayana (Lying down)",
            2: "Upaveśana (Sitting)",
            3: "Netrapāṇi (Observing)",
            4: "Prakāśa (Shining)",
            5: "Gamana (Moving)",
            6: "Āgamana (Arriving)",
            7: "Sabhā (In Assembly)",
            8: "Āgama (Approaching)",
            9: "Bhojana (Eating)",
            10: "Nṛtya-lipsā (Desiring Dance)",
            11: "Kautuka (Excited)",
            0: "Nidrā (Sleeping)"
        }
        shayanadi_name = shayanadi_map.get(rem, "Nidrā (Sleeping)")

        rows.append({
            "Planet": planet,
            "Baladi": baladi_name,
            "Jagratadi": jagratadi_name,
            "Deeptaadi": deeptaadi_name,
            "Lajjitadi": lajjitadi_name,
            "Shayanadi": shayanadi_name
        })

    return pd.DataFrame(rows)
