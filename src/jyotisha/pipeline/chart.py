# src/jyotisha/pipeline/chart.py
#
# Chart orchestrator — composes category components into one birth chart.
# Extraction roadmap (see docs/ARCHITECTURE.md):
#   [identity]  positions, lagnas, panchanga, vargas
#   [strength]  shadbala, bhava bala, ishta/kashta
#   [timing]    vimshottari/yogini + dasa_systems builders
#   [relational] aspect grid, arudha, pushkara
from datetime import datetime, timedelta, date, timezone
import colorsys
from dateutil import tz
import pandas as pd
import swisseph as swe

# Import Dasa Systems (assuming src.dasa_systems is available in path)
from src.jyotisha.timing.dasha.systems import (
    build_ashtottari, build_shodshottari, build_dwadashottari,
    build_panchottari, build_shatabdik, build_chaturashiti_sama,
    build_dwisaptati_sama, build_shastihayani, build_shattrimshat_sama,
    build_chakra,
    build_sthir_dasa, build_yogardha_dasa, build_kendradi_dasa,
    build_karak_dasa, build_manduk_dasa, build_shula_dasa,
    build_trikon_dasa, build_dirga_dasa, build_panch_swar_dasa,
    build_kalachakra_dasa
)

from src.jyotisha.base.constants import (
    AYANAMSA_OPTIONS, RASHI_SA, RASHI_EN, RASHI_ABR, PLANETS, GRAHAS_FOR_HOUSE,
    SIGN_INDEX, SIGN_LORD, PERM_FRIENDS, PERM_ENEMIES, BENEFICS, MALEFICS,
    EXALT, DEBIL, MOOLATR, NAISARGIKA,
    MIN_SHADBALA_RUPA, MAX_SHADBALA_RUPA,
    YOGA_NAMES, KARANA_FIXED, KARANA_MOV, TITHI_NAMES_FULL, VARA_SA_MON_FIRST, CHALDEAN,
    PUSHKARA_AMSA_RANGES, PUSHKARA_BHAGA_DEG, MRITYU_BHAGA_DEG,
    MAASA_MAP, SUNRISE_DEFINITION, SITE_ELEVATION_M, PRESSURE_MBAR, TEMP_C, HINDU_BIT,
    get_ayanamsa_code
)
from src.jyotisha.base.dates import HistoricalDate, local_and_utc, fmt_dt
from src.jyotisha.base.utils import norm360, lon_to_sign_idx, sign_dms_str, dms_str, rashi_name, aspect_strength_pct, sign_distance
from src.jyotisha.identity.vargas import (
    navamsa_for, get_all_vargas, get_varga_names, get_nakshatra_details,
)
from src.jyotisha.strength import compute_shadbala, compute_bhava_bala, compute_ishta_kashta
from src.jyotisha.relational import compute_aspect_grid, compute_arudha_padas
from src.jyotisha.relational.arudha import compute_argala
from src.jyotisha.relational.yogas import detect_yogas
from src.jyotisha.state import compute_avastha
from src.jyotisha.identity.karakas import compute_chara_karakas, compute_karakamsha
from src.jyotisha.identity.marak import compute_marak_grahas
from src.jyotisha.identity.upagrahas import compute_upagrahas
from src.jyotisha.identity.elements import compute_elements_gunas

# ---------------------------------
# Core
# ---------------------------------
from src.jyotisha.base.ephemeris import init_ephe

def compute_chart(y, m, d, hh, mm, ss, lat, lon,
                  ephe_path="ephe", use_moseph=False, house_sys=b'O',
                  tzname_override: str | None = None,
                  ayanamsa: str | None = "Lahiri", name: str | None = None):
    # Get ayanamsa code from name (None means tropical mode)
    ayanamsa_code = get_ayanamsa_code(ayanamsa) if ayanamsa is not None else None
    FLAGS = init_ephe(ephe_path, use_moseph, sidereal_mode=ayanamsa_code)

    # time setup (with optional timezone override)
    local_dt, utc_dt, tz_offset_hours, tzname, LOCAL_ZONE = local_and_utc(
        y, m, d, hh, mm, ss, lat, lon, tzname_override=tzname_override
    )
    ut_hour  = utc_dt.hour + utc_dt.minute/60 + utc_dt.second/3600
    jd_ut    = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, ut_hour, swe.GREG_CAL)
    # For historical dates, use HistoricalDate; otherwise use standard date
    try:
        birth_date_local = date(y, m, d)
    except (ValueError, OverflowError):
        # Use HistoricalDate for dates outside Python's date range
        birth_date_local = HistoricalDate(y, m, d, 0, 0, 0, tzinfo=LOCAL_ZONE)

    # ---------------------------------
    # SUNRISE / SUNSET (Swiss Ephemeris) — robust across pyswisseph versions
    # ---------------------------------
    def _jd_to_local_dt(jd):
        # IMPORTANT: swe.revjul returns UT in HOURS, not fraction of a day.
        y_, m_, d_, ut_hours = swe.revjul(jd, swe.GREG_CAL)
        
        # Handle time components
        h_ = int(ut_hours)
        rem = (ut_hours - h_) * 60
        min_ = int(rem)
        sec_ = int((rem - min_) * 60)
        
        # Check year range for Python datetime
        if 1 <= y_ <= 9999:
            dt_utc = datetime(y_, m_, d_, h_, min_, sec_, tzinfo=timezone.utc)
            return dt_utc.astimezone(LOCAL_ZONE)
        else:
            return HistoricalDate(y_, m_, d_, h_, min_, sec_, tzinfo=LOCAL_ZONE)

    def _call_rise_trans(tjd, epheflag_for_rise, rsmi, geopos, atpress, attemp):
        try:
            return swe.rise_trans(tjd, swe.SUN, "", epheflag_for_rise, rsmi, geopos, atpress, attemp)
        except TypeError:
            pass
        try:
            return swe.rise_trans(tjd, swe.SUN, "", epheflag_for_rise, rsmi, geopos, atpress)
        except TypeError:
            pass
        try:
            return swe.rise_trans(tjd, swe.SUN, "", epheflag_for_rise, rsmi, geopos)
        except TypeError:
            pass
        try:
            return swe.rise_trans(tjd, swe.SUN, rsmi, geopos, atpress, attemp)
        except TypeError:
            pass
        return swe.rise_trans(tjd, swe.SUN, rsmi, geopos)

    def _rsmi_for(mode):
        rsmi_rise = swe.CALC_RISE
        rsmi_set  = swe.CALC_SET
        atpress = PRESSURE_MBAR
        attemp  = TEMP_C
        if mode == "vedic":
            # center on horizon, no refraction (Hindu)
            if HINDU_BIT is not None:
                rsmi_rise |= HINDU_BIT
                rsmi_set  |= HINDU_BIT
                atpress, attemp = 0.0, 0.0
            else:
                rsmi_rise |= swe.BIT_DISC_CENTER | swe.BIT_NO_REFRACTION
                rsmi_set  |= swe.BIT_DISC_CENTER | swe.BIT_NO_REFRACTION
                atpress, attemp = 0.0, 0.0
        elif mode == "geometric":
            rsmi_rise |= swe.BIT_DISC_CENTER | swe.BIT_NO_REFRACTION
            rsmi_set  |= swe.BIT_DISC_CENTER | swe.BIT_NO_REFRACTION
            atpress, attemp = 0.0, 0.0
        # else: "astronomical" (default in this branch): upper limb + refraction
        return rsmi_rise, rsmi_set, atpress, attemp

    def _sunrise_sunset_for_anchor(anchor_jd_ut, lat_, lon_, elev_m, mode):
        """Compute next sunrise and next sunset AFTER the given UT JD anchor."""
        rsmi_rise, rsmi_set, atpress, attemp = _rsmi_for(mode)
        epheflag_for_rise = swe.FLG_MOSEPH if use_moseph else swe.FLG_SWIEPH
        geopos = (lon_, lat_, float(elev_m))
        ret_rise, val_rise = _call_rise_trans(anchor_jd_ut, epheflag_for_rise, rsmi_rise, geopos, atpress, attemp)
        if ret_rise < 0: raise RuntimeError("Sunrise computation failed.")
        ret_set,  val_set  = _call_rise_trans(anchor_jd_ut, epheflag_for_rise, rsmi_set,  geopos, atpress, attemp)
        if ret_set < 0: raise RuntimeError("Sunset computation failed.")
        return _jd_to_local_dt(val_rise[0]), _jd_to_local_dt(val_set[0])

    def _jd_ut_at_local_midnight(d_):
        """UT JD corresponding to local midnight at start of local date d_."""
        dt_local_mid = datetime(d_.year, d_.month, d_.day, 0, 0, 0, tzinfo=LOCAL_ZONE)
        dt_utc_mid = dt_local_mid.astimezone(timezone.utc)
        ut = dt_utc_mid.hour + dt_utc_mid.minute/60 + dt_utc_mid.second/3600
        return swe.julday(dt_utc_mid.year, dt_utc_mid.month, dt_utc_mid.day, ut, swe.GREG_CAL)

    def _sunrise_for_local_date(d_, lat_, lon_, elev_m, mode):
        anchors = []
        try: anchors.append(_jd_ut_at_local_midnight(d_ - timedelta(days=1)))
        except (ValueError, OverflowError): pass
        try: anchors.append(_jd_ut_at_local_midnight(d_))
        except (ValueError, OverflowError): pass
        try: anchors.append(_jd_ut_at_local_midnight(d_ + timedelta(days=1)))
        except (ValueError, OverflowError): pass
        candidates = []
        for a in anchors:
            try:
                sr, _ = _sunrise_sunset_for_anchor(a, lat_, lon_, elev_m, mode)
                candidates.append(sr)
            except (ValueError, OverflowError, RuntimeError): pass
        for sr in candidates:
            if sr.date() == d_: return sr
        return min(candidates, key=lambda t: abs((t.date() - d_).days) + abs((t - datetime(t.year, t.month, t.day, tzinfo=t.tzinfo)).total_seconds())/86400.0)

    def _sunset_for_local_date(d_, lat_, lon_, elev_m, mode):
        anchors = []
        try: anchors.append(_jd_ut_at_local_midnight(d_ - timedelta(days=1)))
        except (ValueError, OverflowError): pass
        try: anchors.append(_jd_ut_at_local_midnight(d_))
        except (ValueError, OverflowError): pass
        try: anchors.append(_jd_ut_at_local_midnight(d_ + timedelta(days=1)))
        except (ValueError, OverflowError): pass
        candidates = []
        for a in anchors:
            try:
                _, ss = _sunrise_sunset_for_anchor(a, lat_, lon_, elev_m, mode)
                candidates.append(ss)
            except (ValueError, OverflowError, RuntimeError): pass
        for ss in candidates:
            if ss.date() == d_: return ss
        return min(candidates, key=lambda t: abs((t.date() - d_).days) + abs((t - datetime(t.year, t.month, t.day, tzinfo=t.tzinfo)).total_seconds())/86400.0)

    # Get sunrise/sunset for the requested local date
    if isinstance(birth_date_local, HistoricalDate):
        rsmi_rise, rsmi_set, atpress, attemp = _rsmi_for(SUNRISE_DEFINITION)
        epheflag_for_rise = swe.FLG_MOSEPH if use_moseph else swe.FLG_SWIEPH
        geopos = (lon, lat, float(SITE_ELEVATION_M))

        def jd_to_hist_local(jd_ut):
            jd_local = jd_ut + (tz_offset_hours / 24.0)
            y_, m_, d_, local_hours = swe.revjul(jd_local, swe.GREG_CAL)
            h_ = int(local_hours)
            rem = (local_hours - h_) * 60
            min_ = int(rem)
            sec_ = int((rem - min_) * 60)
            return HistoricalDate(y_, m_, d_, h_, min_, sec_, tzinfo=LOCAL_ZONE)

        def rise_set_for_day(day_offset):
            jd_anchor_ut = swe.julday(y, m, d + day_offset, 0.0, swe.GREG_CAL)
            ret_rise, val_rise = _call_rise_trans(jd_anchor_ut, epheflag_for_rise, rsmi_rise, geopos, atpress, attemp)
            ret_set, val_set = _call_rise_trans(jd_anchor_ut, epheflag_for_rise, rsmi_set, geopos, atpress, attemp)
            if ret_rise < 0 or ret_set < 0:
                raise RuntimeError("Rise/set computation failed for historical date")
            return jd_to_hist_local(val_rise[0]), jd_to_hist_local(val_set[0])

        sunrise_prev_local, _ = rise_set_for_day(-1)
        sunrise_local, sunset_local = rise_set_for_day(0)
        sunrise_next_local, _ = rise_set_for_day(1)
    else:
        try:
            sunrise_local = _sunrise_for_local_date(birth_date_local, lat, lon, SITE_ELEVATION_M, SUNRISE_DEFINITION)
            sunset_local  = _sunset_for_local_date (birth_date_local, lat, lon, SITE_ELEVATION_M, SUNRISE_DEFINITION)
        except Exception as e:
            raise RuntimeError(f"Sunrise/sunset calculation failed: {e}")
                
        try:
            sunrise_prev_local = _sunrise_for_local_date(birth_date_local - timedelta(days=1), lat, lon, SITE_ELEVATION_M, SUNRISE_DEFINITION)
        except Exception as e:
            raise RuntimeError(f"Previous sunrise calculation failed: {e}")

        try:
            sunrise_next_local = _sunrise_for_local_date(birth_date_local + timedelta(days=1), lat, lon, SITE_ELEVATION_M, SUNRISE_DEFINITION)
        except Exception as e:
            raise RuntimeError(f"Next sunrise calculation failed: {e}")
    
    # Calculate Janma Ghatis
    if isinstance(local_dt, HistoricalDate) or isinstance(sunrise_local, HistoricalDate):
        since_sunrise_hours = (local_dt.hour - sunrise_local.hour) + (local_dt.minute - sunrise_local.minute)/60.0
        if since_sunrise_hours < 0:
            since_sunrise_hours += 24
        since_sunrise = since_sunrise_hours * 3600.0
    elif sunrise_local <= local_dt < sunrise_next_local:
        since_sunrise = (local_dt - sunrise_local).total_seconds()
    elif local_dt < sunrise_local:
        since_sunrise = (local_dt - sunrise_prev_local).total_seconds()
    else:
        since_sunrise = (local_dt - sunrise_next_local).total_seconds()
    janma_ghatis = round(since_sunrise / (24 * 60), 4)

    def local_dt_to_jd_ut(dt_local):
        try:
            if isinstance(dt_local, datetime):
                dt_utc = dt_local.astimezone(timezone.utc)
                ut_hours = dt_utc.hour + dt_utc.minute/60 + dt_utc.second/3600
                return swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, ut_hours, swe.GREG_CAL)
            ut_hours = dt_local.hour - tz_offset_hours + dt_local.minute/60 + dt_local.second/3600
            return swe.julday(dt_local.year, dt_local.month, dt_local.day, ut_hours, swe.GREG_CAL)
        except Exception:
            return jd_ut

    sunrise_jd_ut = local_dt_to_jd_ut(sunrise_local)
    sunrise_sun_lon_sid = norm360(swe.calc_ut(sunrise_jd_ut, swe.SUN, FLAGS)[0][0])

    # ---------------------------------
    # Houses, ayanāṁśa
    # ---------------------------------
    cusps_trop, ascmc_trop = swe.houses(jd_ut, lat, lon, house_sys)
    if ayanamsa is None:
        ayan = 0.0
        ayanamsa_name = "Tropical"
    else:
        ayan = swe.get_ayanamsa_ut(jd_ut)
        ayanamsa_name = ayanamsa
    asc_sid = norm360(ascmc_trop[0] - ayan)
    mc_sid  = norm360(ascmc_trop[1] - ayan)
    asc_sign_idx = lon_to_sign_idx(asc_sid)

    # ---------------------------------
    # Planets / points
    # ---------------------------------
    def calc_vals(code): return swe.calc_ut(jd_ut, code, FLAGS)[0]

    rows=[]; numeric_lons={}; vargas_data = {}
    
    for nm, lonv, label in [("Ascendant (1st House Cusp)", asc_sid, "Ascendant (1st House Cusp)"),
                            ("10th House Cusp", mc_sid, "10th House Cusp")]:
        nsi, _ = navamsa_for(lonv)
        nak_det = get_nakshatra_details(lonv)
        all_vargas = get_all_vargas(lonv)
        varga_names = get_varga_names(lonv)
        vargas_data[nm] = all_vargas
        rows.append({
            "Point": label,
            "Longitude (Sign DMS)": sign_dms_str(lonv),
            "Longitude (Dec)": round(lonv, 4),
            "Rashi": rashi_name(lonv),
            "Rashi_Idx": lon_to_sign_idx(lonv),
            "Nakshatra": nak_det['nakshatra'],
            "Pada": nak_det['pada'],
            "Nak_Pct_Left": nak_det['pct_left'],
            "Navamsha": RASHI_SA[nsi],
            "Navamsha_Idx": nsi,
            "D2": all_vargas['D2'], "D3": all_vargas['D3'], "D4": all_vargas['D4'],
            "D7": all_vargas['D7'], "D10": all_vargas['D10'], "D12": all_vargas['D12'],
            "D16": all_vargas['D16'], "D20": all_vargas['D20'], "D24": all_vargas['D24'],
            "D27": all_vargas['D27'], "D30": all_vargas['D30'], "D40": all_vargas['D40'],
            "D45": all_vargas['D45'], "D60": all_vargas['D60'],
            "Varga_Names": varga_names,
            "Latitude (DMS)": "—", "Speed (DMS/day)": "—", "Retro": False
        })
        numeric_lons[nm] = lonv

    for nm, code in PLANETS.items():
        vals = calc_vals(code); lonv, latv, spd = norm360(vals[0]), vals[1], vals[3]
        numeric_lons[nm] = lonv
        nsi, _ = navamsa_for(lonv)
        nak_det = get_nakshatra_details(lonv)
        all_vargas = get_all_vargas(lonv)
        varga_names = get_varga_names(lonv)
        vargas_data[nm] = all_vargas
        is_retro = spd < 0
        rows.append({
            "Point": nm,
            "Longitude (Sign DMS)": sign_dms_str(lonv),
            "Longitude (Dec)": round(lonv, 4),
            "Rashi": rashi_name(lonv),
            "Rashi_Idx": lon_to_sign_idx(lonv),
            "Nakshatra": nak_det['nakshatra'],
            "Pada": nak_det['pada'],
            "Nak_Pct_Left": nak_det['pct_left'],
            "Navamsha": RASHI_SA[nsi],
            "Navamsha_Idx": nsi,
            "D2": all_vargas['D2'], "D3": all_vargas['D3'], "D4": all_vargas['D4'],
            "D7": all_vargas['D7'], "D10": all_vargas['D10'], "D12": all_vargas['D12'],
            "D16": all_vargas['D16'], "D20": all_vargas['D20'], "D24": all_vargas['D24'],
            "D27": all_vargas['D27'], "D30": all_vargas['D30'], "D40": all_vargas['D40'],
            "D45": all_vargas['D45'], "D60": all_vargas['D60'],
            "Varga_Names": varga_names,
            "Latitude (DMS)": f"{'N' if latv>=0 else 'S'} {dms_str(latv)}",
            "Speed (DMS/day)": ("-" if spd<0 else "+")+dms_str(abs(spd))+"/day",
            "Retro": is_retro
        })

    try: vals_true = swe.calc_ut(jd_ut, swe.TRUE_NODE, FLAGS)[0]
    except Exception: vals_true = swe.nod_aps_ut(jd_ut, swe.MOON, FLAGS, swe.NODBIT_OSCU)[0]
    rahu = norm360(vals_true[0]); ketu = norm360(rahu+180)
    numeric_lons["Rahu (true)"] = rahu; numeric_lons["Ketu (true)"] = ketu
    for nm, lonv in [("Rahu (true)", rahu), ("Ketu (true)", ketu)]:
        nsi, _ = navamsa_for(lonv)
        nak_det = get_nakshatra_details(lonv)
        all_vargas = get_all_vargas(lonv)
        varga_names = get_varga_names(lonv)
        vargas_data[nm] = all_vargas
        rows.append({
            "Point": nm,
            "Longitude (Sign DMS)": sign_dms_str(lonv),
            "Longitude (Dec)": round(lonv, 4),
            "Rashi": rashi_name(lonv),
            "Rashi_Idx": lon_to_sign_idx(lonv),
            "Nakshatra": nak_det['nakshatra'],
            "Pada": nak_det['pada'],
            "Nak_Pct_Left": nak_det['pct_left'],
            "Navamsha": RASHI_SA[nsi],
            "Navamsha_Idx": nsi,
            "D2": all_vargas['D2'], "D3": all_vargas['D3'], "D4": all_vargas['D4'],
            "D7": all_vargas['D7'], "D10": all_vargas['D10'], "D12": all_vargas['D12'],
            "D16": all_vargas['D16'], "D20": all_vargas['D20'], "D24": all_vargas['D24'],
            "D27": all_vargas['D27'], "D30": all_vargas['D30'], "D40": all_vargas['D40'],
            "D45": all_vargas['D45'], "D60": all_vargas['D60'],
            "Varga_Names": varga_names,
            "Latitude (DMS)": "—", "Speed (DMS/day)": "—", "Retro": True
        })
    
    # Calculate special Lagnas
    sun_lon_sid = numeric_lons.get("Sun", 0)
    moon_lon_sid = numeric_lons.get("Moon", 0)
    
    def calculate_hora_lagna(sunrise_sun_lon, janma_ghatis): return norm360(sunrise_sun_lon + janma_ghatis * 12.0)
    def calculate_bhava_lagna(sunrise_sun_lon, janma_ghatis): return norm360(sunrise_sun_lon + janma_ghatis * 6.0)
    def calculate_ghati_lagna(sunrise_sun_lon, janma_ghatis):
        ghatis_whole = int(janma_ghatis)
        vighatis = (janma_ghatis - ghatis_whole) * 60.0
        return norm360(sunrise_sun_lon + ghatis_whole * 30.0 + vighatis * 0.5)
    def calculate_pranapada_lagna(sun_lon, janma_ghatis): return norm360(sun_lon + (janma_ghatis * 30))
    def calculate_sree_lagna(asc_lon, sun_lon, moon_lon): return norm360(asc_lon + (moon_lon - sun_lon))
    def calculate_indu_lagna(sun_lon): return norm360(sun_lon)
    
    hora_lagna_lon = calculate_hora_lagna(sunrise_sun_lon_sid, janma_ghatis)
    bhava_lagna_lon = calculate_bhava_lagna(sunrise_sun_lon_sid, janma_ghatis)
    ghati_lagna_lon = calculate_ghati_lagna(sunrise_sun_lon_sid, janma_ghatis)
    pranapada_lagna_lon = calculate_pranapada_lagna(sun_lon_sid, janma_ghatis)
    sree_lagna_lon = calculate_sree_lagna(asc_sid, sun_lon_sid, moon_lon_sid)
    indu_lagna_lon = calculate_indu_lagna(sun_lon_sid)
    
    special_lagnas = [("Hora Lagna", hora_lagna_lon), ("Bhava Lagna", bhava_lagna_lon),
                      ("Ghati Lagna", ghati_lagna_lon), ("Pranapada Lagna", pranapada_lagna_lon),
                      ("Sree Lagna", sree_lagna_lon), ("Indu Lagna", indu_lagna_lon)]

    for nm, lonv in special_lagnas:
        nsi, _ = navamsa_for(lonv)
        nak_det = get_nakshatra_details(lonv)
        all_vargas = get_all_vargas(lonv)
        varga_names = get_varga_names(lonv)
        vargas_data[nm] = all_vargas
        rows.append({
            "Point": nm, "Longitude (Sign DMS)": sign_dms_str(lonv), "Longitude (Dec)": round(lonv, 4),
            "Rashi": rashi_name(lonv), "Rashi_Idx": lon_to_sign_idx(lonv),
            "Nakshatra": nak_det['nakshatra'], "Pada": nak_det['pada'], "Nak_Pct_Left": nak_det['pct_left'],
            "Navamsha": RASHI_SA[nsi], "Navamsha_Idx": nsi,
            "D2": all_vargas['D2'], "D3": all_vargas['D3'], "D4": all_vargas['D4'],
            "D7": all_vargas['D7'], "D10": all_vargas['D10'], "D12": all_vargas['D12'],
            "D16": all_vargas['D16'], "D20": all_vargas['D20'], "D24": all_vargas['D24'],
            "D27": all_vargas['D27'], "D30": all_vargas['D30'], "D40": all_vargas['D40'],
            "D45": all_vargas['D45'], "D60": all_vargas['D60'],
            "Varga_Names": varga_names, "Latitude (DMS)": "—", "Speed (DMS/day)": "—", "Retro": False
        })
        numeric_lons[nm] = lonv

    # Varnada
    hora_sign_idx = lon_to_sign_idx(hora_lagna_lon)
    def varnada_for_sign(base_sign_idx):
        base_num = base_sign_idx + 1
        hora_num = hora_sign_idx + 1
        base_count = base_num if base_num % 2 == 1 else 13 - base_num
        hora_count = hora_num if hora_num % 2 == 1 else 13 - hora_num
        total = base_count + hora_count if (base_count % 2) == (hora_count % 2) else abs(base_count - hora_count)
        if total == 0: return base_sign_idx
        return ((total - 1) % 12) if total % 2 == 1 else 12 - ((total - 1) % 12) - 1

    varnada_by_house = {}
    for offset in range(12):
        house_num = offset + 1
        house_sign_idx = (asc_sign_idx + offset) % 12
        varnada_idx = (varnada_for_sign(house_sign_idx) if varnada_for_sign(house_sign_idx)>=0 else varnada_for_sign(house_sign_idx)+12)%12
        varnada_by_house[house_num] = varnada_idx
        varnada_lon = varnada_idx * 30.0
        nsi, _ = navamsa_for(varnada_lon)
        nak_det = get_nakshatra_details(varnada_lon)
        all_vargas = get_all_vargas(varnada_lon)
        varga_names = get_varga_names(varnada_lon)
        vargas_data_name = "Varnada Lagna" if house_num == 1 else f"Varnada H{house_num}"
        vargas_data[vargas_data_name] = all_vargas
        rows.append({
            "Point": vargas_data_name, "Longitude (Sign DMS)": sign_dms_str(varnada_lon), "Longitude (Dec)": round(varnada_lon, 4),
            "Rashi": rashi_name(varnada_lon), "Rashi_Idx": varnada_idx,
            "Nakshatra": nak_det['nakshatra'], "Pada": nak_det['pada'], "Nak_Pct_Left": nak_det['pct_left'],
            "Navamsha": RASHI_SA[nsi], "Navamsha_Idx": nsi,
            "D2": all_vargas['D2'], "D3": all_vargas['D3'], "D4": all_vargas['D4'],
            "D7": all_vargas['D7'], "D10": all_vargas['D10'], "D12": all_vargas['D12'],
            "D16": all_vargas['D16'], "D20": all_vargas['D20'], "D24": all_vargas['D24'],
            "D27": all_vargas['D27'], "D30": all_vargas['D30'], "D40": all_vargas['D40'],
            "D45": all_vargas['D45'], "D60": all_vargas['D60'],
            "Varga_Names": varga_names, "Latitude (DMS)": "—", "Speed (DMS/day)": "—", "Retro": False,
            "IsVarnada": True, "House": house_num,
        })
        numeric_lons[vargas_data_name] = varnada_lon

    # Arudha Padas
    arudha_results = compute_arudha_padas(asc_sign_idx, numeric_lons)
    for res in arudha_results:
        p_name = res["point_name"]
        vargas_data[p_name] = res["all_vargas"]
        rows.append(res["row_data"])
        numeric_lons[p_name] = res["pada_lon"]

    points_df = pd.DataFrame(rows)
    order_points = ["Ascendant (1st House Cusp)","10th House Cusp","Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Uranus","Neptune","Pluto","Rahu (true)","Ketu (true)","Hora Lagna","Ghati Lagna","Pranapada Lagna","Sree Lagna","Indu Lagna"]
    varnada_order = ["Varnada Lagna"] + [f"Varnada H{i}" for i in range(2, 13)]
    arudha_order = ["Arudha Lagna"] + [f"Arudha H{i}" for i in range(2, 12)] + ["Upapada Lagna"]
    order_points = order_points + varnada_order + arudha_order
    points_df["__o__"] = points_df["Point"].apply(lambda x: order_points.index(x) if x in order_points else 999)
    points_df = points_df.sort_values("__o__").drop(columns="__o__").reset_index(drop=True)

    # Houses (Sripati)
    def unwrap(seq):
        out=[seq[0]]
        for v in seq[1:]:
            pv=out[-1]; v = v+360.0 if v<pv else v
            out.append(v)
        return out
    def mid(a,b): return (a+b)/2.0 if a<=b else (a+b+360.0)/2.0

    cusps_sid = [norm360(c - ayan) for c in cusps_trop]
    cusps_unw = unwrap(cusps_sid)
    starts = []; ends = []
    for i in range(12):
        cprev = cusps_unw[i-1] if i>0 else cusps_unw[-1]-360.0
        ci = cusps_unw[i]
        cnext = cusps_unw[i+1] if i<11 else cusps_unw[0]+360.0
        starts.append(norm360(mid(cprev, ci))); ends.append(norm360(mid(ci, cnext)))

    house_occ = {i+1: [] for i in range(12)}
    for g in GRAHAS_FOR_HOUSE:
        glon = numeric_lons[g]
        for i in range(12):
            s, e = starts[i], ends[i]
            if (s <= e and s <= glon < e) or (s > e and (glon >= s or glon < e)):
                house_occ[i+1].append(g.replace(" (true)","")); break

    house_rows = [{"House": i+1, "Start (Sign DMS)": sign_dms_str(starts[i]),
                   "Cusp (Sign DMS)": sign_dms_str(cusps_sid[i]), "End (Sign DMS)": sign_dms_str(ends[i]),
                   "Occupants": ", ".join(house_occ[i+1])} for i in range(12)]
    houses_df = pd.DataFrame(house_rows)

    # Aspects
    aspect_grid_df = compute_aspect_grid(numeric_lons, cusps_sid)

    # Pushkara
    aspect_planets = [
        p for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu (true)", "Ketu (true)", "Uranus", "Neptune", "Pluto"]
        if p in numeric_lons
    ]
    push_rows = []
    for name in aspect_planets:
        lonv = numeric_lons[name]
        si = lon_to_sign_idx(lonv); intra = norm360(lonv) - si*30.0
        in_amsa = next(((s,e) for s,e in PUSHKARA_AMSA_RANGES[si] if s<=intra<=e), None)
        amsa_text = "Yes" + (f" ({dms_str(in_amsa[0])}–{dms_str(in_amsa[1])})" if in_amsa else "") if in_amsa else "No"
        in_pb = abs(intra - PUSHKARA_BHAGA_DEG[si]) <= (0.5 if name in {"Jupiter","Saturn","Rahu (true)","Ketu (true)"} else 1.0)
        pb_text = f"Yes (Δ {abs(intra-PUSHKARA_BHAGA_DEG[si]):.2f}°)" if in_pb else "No"
        in_mb = abs(intra - MRITYU_BHAGA_DEG[si]) <= (0.5 if name in {"Jupiter","Saturn","Rahu (true)","Ketu (true)"} else 1.0)
        mb_text = f"Yes (Δ {abs(intra-MRITYU_BHAGA_DEG[si]):.2f}°)" if in_mb else "No"
        push_rows.append({"Target": name, "Sign": RASHI_ABR[si], "Longitude": sign_dms_str(lonv),
                          "Pushkara Amsa": amsa_text, "Pushkara Bhaga": pb_text, "Mrityu Bhaga": mb_text})
    pushkara_df = pd.DataFrame(push_rows)

    # Vimshottari
    NAK_STEP = 360.0/27.0
    MD_ORDER = ["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"]
    MD_YEARS = {"Ketu":7, "Venus":20, "Sun":6, "Moon":10, "Mars":7, "Rahu":18, "Jupiter":16, "Saturn":19, "Mercury":17}
    moon_lon = numeric_lons["Moon"]; nak_index = int(moon_lon // NAK_STEP)
    frac_left = 1.0 - (moon_lon % NAK_STEP) / NAK_STEP
    start_md = MD_ORDER[nak_index % 9]; start_years = MD_YEARS[start_md] * frac_left
    
    vim_rows=[]; cur=local_dt; seq=[(start_md, start_years)]
    j=(nak_index%9 + 1)%9; spent=start_years
    while spent < 120:
        lord=MD_ORDER[j]; seq.append((lord, MD_YEARS[lord])); spent+=MD_YEARS[lord]; j=(j+1)%9
    for lord, yrs in seq:
        en = cur + timedelta(days=yrs*365.25)
        vim_rows.append({"Mahadasa": lord, "Start (local)": fmt_dt(cur), "End (local)": fmt_dt(en), "Duration (years)": round(yrs,6)})
        cur=en
    vim_md_df = pd.DataFrame(vim_rows)

    # Yogini
    YOG_ORDER = ["Mangala","Pingala","Dhanya","Bhramari","Bhadrika","Ulka","Siddha","Sankata"]
    YOG_YEARS = {"Mangala":1,"Pingala":2,"Dhanya":3,"Bhramari":4,"Bhadrika":5,"Ulka":6,"Siddha":7,"Sankata":8}
    N2Y = [3,4,5,6,3,4,5,6,3,4,5,6,3,4,5,6,3,4,5,6,3,4,5,6,3,4,5] # Simplified mapping logic (Bhramari=3... actually let's use list)
    # The original map was explicit. Let's reconstruct.
    # 0->Bhramari(3), 1->Bhadrika(4), 2->Ulka(5), 3->Siddha(6), 4->Sankata(7), 5->Mangala(0)... offset=3
    start_yog_idx = (nak_index + 3) % 8
    start_yog = YOG_ORDER[start_yog_idx]
    
    yog_rows=[]; cur=local_dt; y1=YOG_YEARS[start_yog]*frac_left
    yog_rows.append({"Yogini":start_yog, "Start (local)":fmt_dt(cur), "End (local)":fmt_dt(cur+timedelta(days=y1*365.25)), "Duration (years)":round(y1,6)})
    cur+=timedelta(days=y1*365.25); yog_i=(start_yog_idx+1)%8
    for _ in range(23):
        lord=YOG_ORDER[yog_i]; y2=YOG_YEARS[lord]
        en=cur+timedelta(days=y2*365.25)
        yog_rows.append({"Yogini":lord, "Start (local)":fmt_dt(cur), "End (local)":fmt_dt(en), "Duration (years)":round(y2,6)})
        cur=en; yog_i=(yog_i+1)%8
    yogini_df = pd.DataFrame(yog_rows)

    # Panchanga
    def tithi_yoga_karana(jd):
        sun = norm360(swe.calc_ut(jd, swe.SUN, FLAGS)[0][0]); moon = norm360(swe.calc_ut(jd, swe.MOON, FLAGS)[0][0])
        diff = norm360(moon - sun); sum_ = norm360(moon + sun)
        tithi = int(diff//12)+1; tithi_left = (1.0 - (diff%12)/12.0)*100
        nak = int(moon//(360/27)); nak_left = (1.0 - (moon%(360/27))/(360/27))*100
        yoga = int(sum_//(360/27)); yoga_left = (1.0 - (sum_%(360/27))/(360/27))*100
        kar = int(diff//6); kar_left = (1.0 - (diff%6)/6.0)*100
        kar_name = KARANA_FIXED[0] if kar==0 else (KARANA_FIXED[kar-56] if kar>=57 else KARANA_MOV[(kar-1)%7])
        return {"tithi": TITHI_NAMES_FULL[tithi-1] if tithi<=30 else "?", "tithi_num": tithi,
                "tithi_pct_left": round(tithi_left,2), "nakshatra": get_nakshatra_details(moon)['nakshatra'],
                "nak_pct_left": round(nak_left,2), "yoga": YOGA_NAMES[yoga] if yoga<27 else "?",
                "yoga_pct_left": round(yoga_left,2), "karana": kar_name, "karana_pct_left": round(kar_left,2),
                "paksha": "Shukla" if tithi<=15 else "Krishna"}

    p = tithi_yoga_karana(jd_ut)
    # Maasa
    def calculate_maasa(jd_curr):
         swe.set_sid_mode(swe.SIDM_LAHIRI) # Maasa always Lahiri
         FlagsSid = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
         sun = swe.calc_ut(jd_curr, swe.SUN, FlagsSid)[0][0]; moon = swe.calc_ut(jd_curr, swe.MOON, FlagsSid)[0][0]
         phase = (moon - sun) % 360
         t = jd_curr - (phase / 12.19) - 0.5
         for _ in range(6):
             s = swe.calc_ut(t, swe.SUN, FlagsSid)[0][0]; m = swe.calc_ut(t, swe.MOON, FlagsSid)[0][0]
             ph = (m-s)%360; t -= (ph-360 if ph>180 else ph)/12.19
         prev_nm = t
         s1 = swe.calc_ut(prev_nm, swe.SUN, FlagsSid)[0][0]; s1_sign = int(s1//30)%12
         name_sans, name_tam = MAASA_MAP.get(s1_sign, ("Unknown", "Unknown"))
         return {"maasa_sanskrit": name_sans, "maasa_tamil": name_tam, "maasa_status": "Nija"} # Simplified
    
    maasa_info = calculate_maasa(jd_ut)
    p.update(maasa_info)
    
    # Hora
    hora_idx = int(((local_dt - sunrise_local).total_seconds()/3600.0) % 24) # Approximate if not using strict solar hours
    # Use exact seasonal hour logic from original
    next_sr = sunrise_next_local if local_dt >= sunrise_local else sunrise_local
    prev_sr = sunrise_local if local_dt >= sunrise_local else sunrise_prev_local
    span = (next_sr - prev_sr).total_seconds()
    hora_idx = int( min(23, max(0, (local_dt - prev_sr).total_seconds() // (span/24.0))) )
    day_lord_idx = CHALDEAN.index(VARA_SA_MON_FIRST[prev_sr.weekday()].replace("vara","")+"var" if "var" not in VARA_SA_MON_FIRST[0] else ["Moon","Mars","Mercury","Jupiter","Venus","Saturn","Sun"][prev_sr.weekday()])
    # Re-using original lookup
    day_lord_planet = ["Moon","Mars","Mercury","Jupiter","Venus","Saturn","Sun"][prev_sr.weekday()]
    start_idx = CHALDEAN.index(day_lord_planet)
    hora_lord = CHALDEAN[(start_idx + hora_idx) % 7]

    panchanga_df = pd.DataFrame([{
        "Sunrise (local)": fmt_dt(sunrise_local), "Sunset (local)": fmt_dt(sunset_local),
        "Next Sunrise": fmt_dt(sunrise_next_local), "Vara (weekday)": VARA_SA_MON_FIRST[sunrise_local.weekday()],
        "Maasa": p['maasa_sanskrit'], "Maasa_Tamil": p['maasa_tamil'],
        "Tithi": p['tithi'], "Nakshatra": p['nakshatra'], "Yoga": p['yoga'], "Karana": p['karana'],
        "Hora": hora_lord, "Janma_Ghatis": janma_ghatis, "Ayanamsa": round(ayan, 6),
        "Sidereal_Time": round(jd_ut % 1 * 24, 4)
    }])

    # Shadbala
    shadbala_df, sb_sthana_df, sb_kala_df, planet_total_rupa = compute_shadbala(
        local_dt, sunrise_local, sunrise_prev_local, sunrise_next_local,
        jd_ut, FLAGS, numeric_lons, ayan, starts, ends, hora_lord, asc_sid
    )

    # Bhava Bala
    sb_bhava_df = compute_bhava_bala(
        local_dt, sunrise_local, sunset_local, cusps_sid, numeric_lons,
        starts, ends, house_occ, planet_total_rupa, asc_sid
    )

    # Ishta / Kashta
    ishta_df = compute_ishta_kashta(numeric_lons)

    # Dasa Systems
    lagna_lord = SIGN_LORD.get(asc_sign_idx, "Sun")
    lagna_lord_lon = numeric_lons.get(lagna_lord, 0)
    lagna_lord_rashi_idx = lon_to_sign_idx(lagna_lord_lon)
    is_sandhya = False # Simplified logic
    is_night = local_dt < sunrise_local or local_dt >= sunset_local

    ashtottari_df = build_ashtottari(numeric_lons["Moon"], local_dt)
    shodshottari_df = build_shodshottari(numeric_lons["Moon"], local_dt)
    dwadashottari_df = build_dwadashottari(numeric_lons["Moon"], local_dt)
    panchottari_df = build_panchottari(numeric_lons["Moon"], local_dt)
    shatabdik_df = build_shatabdik(numeric_lons["Moon"], local_dt)
    chaturashiti_sama_df = build_chaturashiti_sama(numeric_lons["Moon"], local_dt)
    dwisaptati_sama_df = build_dwisaptati_sama(numeric_lons["Moon"], local_dt)
    shastihayani_df = build_shastihayani(numeric_lons["Moon"], local_dt)
    shattrimshat_sama_df = build_shattrimshat_sama(numeric_lons["Moon"], local_dt)

    chakra_df = build_chakra(asc_sign_idx, lagna_lord_rashi_idx, local_dt, is_night=is_night, is_sandhya=is_sandhya)
    
    sthir_df = build_sthir_dasa(rows, local_dt)
    yogardha_df = build_yogardha_dasa(rows, local_dt)
    kendradi_df = build_kendradi_dasa(rows, local_dt)
    karak_df = build_karak_dasa(rows, local_dt)
    manduk_df = build_manduk_dasa(rows, local_dt)
    shula_df = build_shula_dasa(rows, local_dt)
    trikon_df = build_trikon_dasa(rows, local_dt)
    dirga_df = build_dirga_dasa(rows, local_dt)
    panch_swar_df = build_panch_swar_dasa(rows, local_dt, name_str=name if name else "")
    kalachakra_df = build_kalachakra_dasa(rows, local_dt)

    # Varnada Dasa
    # Start sign: Ascendant. Direction: Forward if Odd (Aries=0, etc.), Backward if Even.
    # Note: 0 (Aries) is Odd in Jyotish logic? 0=odd(1st), 1=even(2nd).
    varnada_dasa_rows = []
    is_odd_asc = (asc_sign_idx % 2 == 0) # 0, 2, 4... are Odd signs (1, 3, 5)
    direction_step = 1 if is_odd_asc else -1
    direction_label = "Direct" if is_odd_asc else "Reverse"
    
    sign_sequence = []
    for i in range(12):
        if is_odd_asc: s_idx = (asc_sign_idx + i) % 12
        else: s_idx = (asc_sign_idx - i + 12) % 12
        sign_sequence.append(s_idx)
        
    current_start = local_dt
    for sign_idx in sign_sequence:
        # House num relative to Asc
        # If Asc=0 (Ar), Sign=0 (Ar) -> House 1
        # If Asc=0, Sign=1 (Ta) -> House 2
        # Need simpler log: House 1 is always First Dasha
        # Wait, Dasha is of Rashis. The "House" column in older code was likely just the count 1..12
        # But old code: house_num = ((sign_idx - asc_sign_idx + 12) % 12) + 1
        
        house_num_calc = ((sign_idx - asc_sign_idx + 12) % 12) + 1
        
        # Varnada Index for this house
        # varnada_by_house is keyed by 1-based house number
        varnada_idx = varnada_by_house.get(house_num_calc, sign_idx)
        
        duration_years = sign_distance(sign_idx, varnada_idx, direction_step)
        days = duration_years * 365.25
        end_time = current_start + timedelta(days=days)
        
        varnada_dasa_rows.append({
            "House": house_num_calc,
            "Dasha Rashi": RASHI_SA[sign_idx],
            "Varnada": RASHI_SA[varnada_idx],
            "Direction": direction_label,
            "Start (local)": fmt_dt(current_start),
            "End (local)": fmt_dt(end_time),
            "Duration (years)": round(duration_years, 6)
        })
        current_start = end_time

    varnada_dasa_df = pd.DataFrame(varnada_dasa_rows)
    
    # Avastha
    avastha_df = compute_avastha({
        "points": points_df,
        "janma_ghatis": janma_ghatis
    })

    # Chara Karakas + Karakamsha
    chara_karakas = compute_chara_karakas(numeric_lons)
    karakamsha = compute_karakamsha(chara_karakas, numeric_lons)

    # Yoga detection
    yogas = detect_yogas({
        "points": points_df,
        "asc_sign_idx": asc_sign_idx,
    })

    # Marak Grahas
    marak_grahas = compute_marak_grahas(numeric_lons, asc_sign_idx)

    # Upagrahas
    upagrahas = compute_upagrahas(
        sun_lon=numeric_lons.get("Sun", 0.0),
        sunrise_local=sunrise_local,
        sunset_local=sunset_local,
        local_dt=local_dt,
    )

    # Argala
    argala = compute_argala(asc_sign_idx, numeric_lons)

    # Elements & Gunas
    elements_gunas = compute_elements_gunas(numeric_lons)

    # Return
    return {
        "tzname": tzname,
        "local_dt": local_dt,
        "utc_dt": utc_dt,
        "jd_ut": jd_ut,
        "ayanamsa_name": ayanamsa_name,
        "ayanamsa_value": round(ayan, 6),
        "points": points_df,
        "houses": houses_df,
        "vimshottari_md": vim_md_df,
        "yogini": yogini_df,
        "ashtottari": ashtottari_df,
        "shodshottari": shodshottari_df,
        "dwadashottari": dwadashottari_df,
        "panchottari": panchottari_df,
        "shatabdik": shatabdik_df,
        "chaturashiti_sama": chaturashiti_sama_df,
        "dwisaptati_sama": dwisaptati_sama_df,
        "shastihayani": shastihayani_df,
        "shattrimshat_sama": shattrimshat_sama_df,
        "chakra_dasa": chakra_df,
        "sthir_dasa": sthir_df,
        "yogardha_dasa": yogardha_df,
        "kendradi_dasa": kendradi_df,
        "karak_dasa": karak_df,
        "manduk_dasa": manduk_df,
        "shula_dasa": shula_df,
        "trikon_dasa": trikon_df,
        "dirga_dasa": dirga_df,
        "panch_swar_dasa": panch_swar_df,
        "kalachakra_dasa": kalachakra_df,
        "varnada_dasa": varnada_dasa_df,
        "panchanga": panchanga_df,
        "vargas": vargas_data,
        "shadbala": shadbala_df,
        "shadbala_sthana": sb_sthana_df,
        "shadbala_kala": sb_kala_df,
        "ishta_kashta": ishta_df,
        "aspect_grid": aspect_grid_df,
        "pushkara_table": pushkara_df,
        "bhava_bala": sb_bhava_df,
        "avastha": avastha_df,
        "chara_karakas": chara_karakas,
        "karakamsha": karakamsha,
        "yogas": yogas,
        "marak_grahas": marak_grahas,
        "upagrahas": upagrahas,
        "argala": argala,
        "elements_gunas": elements_gunas,
    }

def compute_chart_with_tzname(y, m, d, hh, mm, ss, lat, lon, tzname,
                              ephe_path="ephe", use_moseph=False, house_sys=b'O',
                              ayanamsa: str = "Lahiri", name: str = None):
    return compute_chart(y, m, d, hh, mm, ss, lat, lon,
                         ephe_path=ephe_path, use_moseph=use_moseph, house_sys=house_sys,
                         tzname_override=tzname, ayanamsa=ayanamsa, name=name)
