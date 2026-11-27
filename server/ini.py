"""Preferences .ini files: read and write the options the Settings screen has, by the ini's key names. What this app has no use for is kept as it came."""
import os
import re

from core_logic import ephemeris as E

from . import settings as S

DEFAULT_INI = os.path.join(os.path.dirname(__file__), "..", "data", "default_settings.ini")
# ini key -> (option key, how the ini's value maps to the option's, and back); a plain int, float or 0/1 unless noted
_BOOL = (lambda v: v not in ("0", "0.000000"), lambda x: str(int(bool(x))))
_NOT = (lambda v: v in ("0", "0.000000"), lambda x: str(int(not x)))
_INT = (int, str)
_FLOAT = (float, lambda x: "%f" % x)
# UserSelectedAyanamsa, the ini's code, by the order of ephemeris.AYANAMSAS (the Settings list's order)
AYANAMSA_CODES = [17, 0, 21, 2, 4, 19, 1, 20, 18, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
KEYS = {
    "HoraPreference": ("d2", _INT), "D3Preference": ("d3", _INT), "D4Preference": ("d4", _INT), "D5Preference": ("d5", _INT), "D7Preference": ("d7", _INT), "D8Preference": ("d8", _INT), "D9Preference": ("d9", _INT),
    "D10Preference": ("d10", _INT), "D11Preference": ("d11", _INT), "D12Preference": ("d12", _INT), "D16Preference": ("d16", _INT), "D20Preference": ("d20", _INT), "D24Preference": ("d24", _INT), "D27Preference": ("d27", _INT),
    "D30Preference": ("d30", _INT), "D60Preference": ("d60", _INT), "D108Preference": ("d108", _INT), "D150Preference": ("d150", _INT), "D150NamePreference": ("d150_names", _INT), "VyatipataMethod": ("vyatipata_method", _INT),
    "MandiInSaturnPortion": ("mandi_in_saturn_portion", _BOOL), "GulikaInSaturnPortion": ("gulika_in_saturn_portion", _BOOL), "TopocentricPositions": ("topocentric", _BOOL), "TruePositions": ("true_positions", _BOOL),
    "NoNutation": ("no_nutation", _BOOL), "NoAberration": ("no_aberration", _BOOL), "NoGravDeflection": ("no_gravitational_deflection", _BOOL), "ApparentRefraction": ("apparent_refraction", _BOOL),
    "TrueNodes": ("nodes", (lambda v: "true" if v != "0" else "mean", lambda x: str(int(x == "true")))), "LagnaUsedInMoolaDasa": ("moola_lagna", _BOOL), "MoonUsedInMoolaDasa": ("moola_moon", _BOOL), "SunUsedInMoolaDasa": ("moola_sun", _BOOL),
    "MoolaDasaNoCorrectionInMoolaTrikona": ("moola_no_correction", _BOOL), "DeltaFromUserSelectedAyanamsa": ("ayanamsa_offset_deg", _FLOAT), "HouseTypeWanted": ("house_type", _INT), "HouseCuspsInMiddle": ("house_cusp_in_middle", _BOOL),
    "BhavaChartRef": ("bhava_ref", _INT), "HousesFromNodesReversed": ("bhava_nodes_reversed", _BOOL), "SpecialYearForTajaka": ("special_year_tajaka", _BOOL), "SpecialYearForTP": ("special_year_tp", _BOOL),
    "DasaSeshamInMundaneCharts": ("dasa_sesham_mundane", _BOOL), "UseCompundRelationshipInAvasthas": ("avastha_compound", _BOOL), "CompoundRelationshipsFromRasi": ("vimsopaka_from_rasi", _BOOL),
    "LifeCycleYears": ("lifecycle_years", _FLOAT), "SunriseDefinition": ("sunrise_definition", _INT), "WeekdayDefinition": ("weekday_definition", _INT), "WeekdayDefinitionKaala": ("mahakala_definition", _INT), "MBTablePreference": ("mrityu_second_table", _BOOL),
    "MBLocationPreference": ("mrityu_location", _INT), "UpagrahaDayDefinition": ("upagraha_day_definition", _INT), "TrueTajaka": ("tajaka_true_year", _BOOL), "TropicalTajaka": ("tajaka_tropical", _BOOL), "MunthaPreference": ("muntha_method", _INT),
    "ShoolaDasaAntardasaStart": ("shoola_ad", _INT), "CharaKarakaDefinition": ("chara_karakas", _INT), "NaisargikaDasaNoADForMDLord": ("naisargika_no_lord", _BOOL), "NaisargikaDasa3rd10thNoAD": ("naisargika_3_10", _BOOL), "NaisargikaDasaOthersNoAD": ("naisargika_others", _BOOL),
    "SwarudhaInAmsaBala": ("swarudha", _INT), "CombustionBadInAmsaBala": ("amsa_combustion", _BOOL), "DispositorCombustionBadInAmsaBala": ("amsa_dispositor_combustion", _BOOL), "DefeatBadInAmsaBala": ("amsa_defeat", _BOOL), "DispositorDefeatBadInAmsaBala": ("amsa_dispositor_defeat", _BOOL),
    "NeechaBadInAmsaBala": ("amsa_neecha", _BOOL), "DispositorNeechaBadInAmsaBala": ("amsa_dispositor_neecha", _BOOL), "DispositorNeechaRasiBadInAmsaBala": ("amsa_dispositor_neecha_rasi", _BOOL), "PoorVimsopakaBadInAmsaBala": ("amsa_poor_vimsopaka", _BOOL),
    "DispositorPoorVimsopakaBadInAmsaBala": ("amsa_dispositor_poor_vimsopaka", _BOOL), "SayanadiBadInAmsaBala": ("amsa_sayanadi", _BOOL), "DispositorSayanadiBadInAmsaBala": ("amsa_dispositor_sayanadi", _BOOL), "CombustionSpecialRuleVenusMercury": ("combustion_by_motion", _BOOL),
    "SudasaADOption": ("sudasa_ad", _INT), "AshtakaVargaDefinition": ("av_definition", _INT), "BhavaDrivenSarvaAshtakaVarga": ("av_bhava_driven_sav", _BOOL), "SudarsanaChakraDasaAD": ("sudarsana_ad_lord", _BOOL), "KalachakraDasaCalculation": ("kalachakra_method", _INT),
    "KCDRohini4NavamsaInLeo": ("kalachakra_rohini_leo", _BOOL), "NodesInArudhas": ("arudha_nodes", _BOOL), "ExceptionsInBhavaArudhas": ("arudha_exceptions_bhava", _BOOL), "ExceptionsInGrahaArudhas": ("arudha_exceptions_graha", _BOOL), "ArudhaBasePlanet": ("arudha_base", _INT),
    "LongitudeBasedBhavaArudhas": ("arudha_longitude", _BOOL), "DivLongsInBhavaArudhas": ("arudha_div_longs", _BOOL), "DrigdasaOfParasara": ("drig_parasara", _BOOL), "SolarMonthUsedInTP": ("tp_solar_month", _BOOL), "LunarYrSign": ("lunar_year_sign", _INT), "SolarYrSign": ("solar_year_sign", _INT),
    "SolarYrTrop": ("solar_tropical", _BOOL), "SiderealNaksharasInTropical": ("sidereal_nakshatras_in_tropical", _BOOL), "Siddhanta": ("siddhanta", _INT), "Use1DegInD30ForDivLong": ("equal_d30_longitudes", _BOOL),
    "AspectValueMax": ("aspect_full", (lambda v: int(float(v)), lambda x: "%f" % x)), "AspectEvalAsPerParasara": ("aspect_parasara", _BOOL), "FixedPlaneInCustomStarAyanamsa": ("custom_star_fixed_plane", _BOOL), "CustomStarLongitude": ("custom_star_longitude", _FLOAT), "CustomStarCode": ("custom_star", (str, str)),
    "TaraDasaParasara": ("tara_parasara", _BOOL), "TaraDasaDirectionFromStar": ("tara_direction_from_star", _BOOL), "NodalExaltationParasara": ("nodal_parasara", _BOOL), "PushkaraBhagaJP": ("pushkara_patel", _NOT), "KaalaInDayNightSeparate": ("kaala_day_night_separate", _BOOL),
    "DivLongFromEndToo": ("mirror_reversed_longitudes", _BOOL), "ContinuousSpecialLagnas": ("continuous_special_lagnas", _BOOL), "CharaDasaExaltationException": ("chara_exaltation", _BOOL),
    "NarayanaDasaChart": ("narayana_varga", _INT), "LagnamsakaDasaChart": ("lagnamsaka_varga", _INT), "PadanathamsaDasaChart": ("padanathamsa_varga", _INT), "ParyaayaDasaChart": ("paryaya_varga", _INT), "SCDasaVarga": ("sudarsana_varga", _INT), "BuddhiGatiDasaVarga": ("buddhi_varga", _INT),
    "SpecialLagnaOn": ("special_lagna_on", _BOOL), "SpecialLagnaPlanet": ("special_lagna_planet", _INT), "SpecialLagnaSpeedFactor": ("special_lagna_speed", _INT), "SpecialLagnaNodesReverse": ("special_lagna_nodes_reverse", _BOOL), "SpecialPointOn": ("special_point_on", _BOOL),
    "SpecialPointBehindAfter": ("special_point_after", _BOOL), "SpecialPointPlanetIndex": ("special_point_planet", _INT), "SpecialPointSahamIndex": ("special_point_saham", _INT), "SpecialPointSignIndex": ("special_point_sign", _INT), "SpecialPointPlanetIndex1": ("special_point_planet", _INT),
    "SpecialPointPlanetIndex2": ("special_point_planet2", _INT), "SpecialPointName": ("special_point_name", (str, str)), "SpecialPointSymbol": ("special_point_symbol", (str, str)),
}
# Keys with one value per dasa ("YearDefinition=<dasa> <value>"): the screen has one value for the family (the dasa's own Options keep the others), so the first dasa's is read and every line written
PER_DASA = {"YearDefinition": ("year_definition", _INT), "YearLength": ("year_length", _FLOAT), "NakshatraDasaStartPoint": ("dasa_seed", _INT), "NaksDasaADMethodPreference": ("dasa_ad_method", _INT),
            "NakshatraDasaShift": ("dasa_shift", _INT), "AntiZodiacalDasa": ("dasa_reverse", _BOOL), "UseDasaSeedFromNatalInTajaka": None, "ProgressDasaSeedInTajaka": None}
PER_DASA = {k: v for k, v in PER_DASA.items() if v}
LINE = re.compile(r"^([A-Za-z_.0-9]+)=(.*)$")
_OPTION = {o["key"]: o for o in S.OPTIONS}


def parse(text):
    """The options an ini sets, by the Settings screen's keys, with only the values that differ from the defaults and that the option allows. Unknown keys and values are left out."""
    out = {}
    for ln in text.splitlines():
        m = LINE.match(ln.strip())
        if not m:
            continue
        k, v = m.group(1), m.group(2).strip()
        if k == "UserSelectedAyanamsa":
            if v.isdigit() and int(v) in AYANAMSA_CODES and E.AYANAMSAS[AYANAMSA_CODES.index(int(v))]["key"] != _OPTION["ayanamsa"]["default"]:
                out["ayanamsa"] = E.AYANAMSAS[AYANAMSA_CODES.index(int(v))]["key"]
            continue
        if k in PER_DASA:
            if not v.startswith("0 "):
                continue
            opt, (read, _) = PER_DASA[k]
            v = v.split()[1]
        elif k in KEYS:
            opt, (read, _) = KEYS[k]
        else:
            continue
        try:
            value = read(v)
        except (ValueError, IndexError):
            continue
        o = _OPTION[opt]
        if o["choices"] and value not in [c["value"] for c in o["choices"]]:
            continue
        if value != o["default"]:
            out[opt] = value
    return out


def write(settings):
    """The default ini (data/default_settings.ini) with the current options written over it, in its own layout. ``settings``: the validated options."""
    with open(DEFAULT_INI, encoding="latin-1") as f:
        lines = f.read().splitlines()
    out = []
    for ln in lines:
        m = LINE.match(ln)
        if m and m.group(1) in KEYS:
            opt, (_, show) = KEYS[m.group(1)]
            ln = "%s=%s" % (m.group(1), show(getattr(settings, opt)))
        elif m and m.group(1) in PER_DASA:
            opt, (_, show) = PER_DASA[m.group(1)]
            ln = "%s=%s %s" % (m.group(1), m.group(2).split()[0], show(getattr(settings, opt)))
        elif m and m.group(1) == "UserSelectedAyanamsa":
            ln = "UserSelectedAyanamsa=%d" % AYANAMSA_CODES[[a["key"] for a in E.AYANAMSAS].index(settings.ayanamsa)]
        out.append(ln)
    return "\n".join(out) + "\n"
