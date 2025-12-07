# src/ci_core/dasa.py
from datetime import datetime, timedelta

# Vimshottari constants
VIM_MD_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
VIM_MD_YEARS = {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7, "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17}

# Yogini constants
YOG_ORDER = ["Mangala", "Pingala", "Dhanya", "Bhramari", "Bhadrika", "Ulka", "Siddha", "Sankata"]
YOG_YEARS = {"Mangala": 1, "Pingala": 2, "Dhanya": 3, "Bhramari": 4, "Bhadrika": 5, "Ulka": 6, "Siddha": 7, "Sankata": 8}
YOG_TOTAL_YEARS = 36.0

def get_vimshottari_antardasha(md_lord: str, md_start: str, md_duration_years: float) -> list:
    rows = []
    cur = datetime.strptime(md_start, "%Y-%m-%d %H:%M:%S")
    md_idx = VIM_MD_ORDER.index(md_lord)
    for i in range(9):
        ad_lord = VIM_MD_ORDER[(md_idx + i) % 9]
        ad_years = (md_duration_years * VIM_MD_YEARS[ad_lord]) / 120.0
        ad_days = ad_years * 365.25
        end = cur + timedelta(days=ad_days)
        rows.append({
            "Mahadasa": md_lord,
            "Antardasa": ad_lord,
            "Start": cur.strftime("%Y-%m-%d %H:%M:%S"),
            "End": end.strftime("%Y-%m-%d %H:%M:%S"),
            "Duration (days)": round(ad_days, 2),
            "Duration (years)": round(ad_years, 4)
        })
        cur = end
    return rows

def get_vimshottari_pratyantardasha(md_lord: str, ad_lord: str, ad_start: str, ad_duration_days: float) -> list:
    rows = []
    try:
        cur = datetime.strptime(ad_start, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        # Fallback if ad_start is not strictly formatted or already datetime
        if isinstance(ad_start, datetime):
            cur = ad_start
        else:
            raise
    ad_idx = VIM_MD_ORDER.index(ad_lord)
    for i in range(9):
        pd_lord = VIM_MD_ORDER[(ad_idx + i) % 9]
        pd_days = (ad_duration_days * VIM_MD_YEARS[pd_lord]) / 120.0
        end = cur + timedelta(days=pd_days)
        rows.append({
            "Mahadasa": md_lord,
            "Antardasa": ad_lord,
            "Pratyantardasa": pd_lord,
            "Start": cur.strftime("%Y-%m-%d %H:%M:%S"),
            "End": end.strftime("%Y-%m-%d %H:%M:%S"),
            "Duration (days)": round(pd_days, 2)
        })
        cur = end
    return rows

def get_yogini_antardasha(md_lord: str, md_start: str, md_duration_years: float) -> list:
    rows = []
    cur = datetime.strptime(md_start, "%Y-%m-%d %H:%M:%S")
    md_idx = YOG_ORDER.index(md_lord)
    for i in range(8):
        ad_lord = YOG_ORDER[(md_idx + i) % 8]
        ad_years = (md_duration_years * YOG_YEARS[ad_lord]) / YOG_TOTAL_YEARS
        ad_days = ad_years * 365.25
        end = cur + timedelta(days=ad_days)
        rows.append({
            "Mahadasa": md_lord,
            "Antardasa": ad_lord,
            "Start": cur.strftime("%Y-%m-%d %H:%M:%S"),
            "End": end.strftime("%Y-%m-%d %H:%M:%S"),
            "Duration (days)": round(ad_days, 2),
            "Duration (years)": round(ad_years, 4)
        })
        cur = end
    return rows

def get_yogini_pratyantardasha(md_lord: str, ad_lord: str, ad_start: str, ad_duration_days: float) -> list:
    rows = []
    cur = datetime.strptime(ad_start, "%Y-%m-%d %H:%M:%S")
    ad_idx = YOG_ORDER.index(ad_lord)
    for i in range(8):
        pd_lord = YOG_ORDER[(ad_idx + i) % 8]
        pd_days = (ad_duration_days * YOG_YEARS[pd_lord]) / YOG_TOTAL_YEARS
        end = cur + timedelta(days=pd_days)
        rows.append({
            "Mahadasa": md_lord,
            "Antardasa": ad_lord,
            "Pratyantardasa": pd_lord,
            "Start": cur.strftime("%Y-%m-%d %H:%M:%S"),
            "End": end.strftime("%Y-%m-%d %H:%M:%S"),
            "Duration (days)": round(pd_days, 2)
        })
        cur = end
    return rows
