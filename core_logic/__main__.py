"""
python -m core_logic path/to/chart.jhd [--ayanamsa KEY] [--house SYSTEM]

Runs the full pipeline on a .jhd file: parse -> Swiss Ephemeris positions/houses ->
Vimshottari, Ashtakavarga and KP lords.  Demonstrates the ephemeris -> engines wiring.
"""
import argparse
from datetime import datetime

from . import ashtakavarga, dashas, ephemeris as E, jhd_io, kp_astrology
from .natal_chart import RASI_NAMES_EN


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m core_logic")
    ap.add_argument("jhd")
    ap.add_argument("--ayanamsa", default="TRUE_LAHIRI", choices=[a["key"] for a in E.AYANAMSAS])
    ap.add_argument("--house", default="PORPHYRY", choices=list(E.HOUSE_SYSTEM_CODES))
    a = ap.parse_args(argv)

    c = jhd_io.parse_jhd_file(a.jhd)
    cfg = E.EphemerisConfig(ayanamsa=a.ayanamsa)
    chart = E.build_chart(jhd_io.to_birth_data(c), cfg, a.house)

    print(f"{c['name']}  {c['year']}-{c['month']:02d}-{c['day']:02d}  {c['hour_local']:.4f}h  "
          f"lat {c['latitude']:.4f} lon {c['longitude_east']:.4f}  tz +{c['tz_east_hours']:.4f}")
    print(f"ayanamsa {a.ayanamsa} = {chart['ayanamsa']:.4f}   sunrise {chart['sunrise_hours']:.3f}h  sunset {chart['sunset_hours']:.3f}h")
    print(f"Lagna  {chart['lagna_lon']:8.4f}  {RASI_NAMES_EN[chart['lagna_sign']]}")
    for n, p in chart["positions"].items():
        kp = kp_astrology.get_kp_sub_levels(p["lon"], 2)
        print(f"{n:8} {p['lon']:8.4f}  {RASI_NAMES_EN[p['sign_index']]:12} {'R' if p['retrograde'] else ' '}  "
              f"KP {kp['star_lord']}/{kp['sub_lord']}/{kp['prati_sub_lord']}")
    tree = dashas.compute_vimshottari_tree(chart["planet_longitudes"]["Moon"], datetime(c["year"], c["month"], c["day"]))
    print("Vimshottari:", ", ".join(f"{d['lord']} {d.get('balance_years', d['duration_years']):.2f}y" for d in tree[:3]), "...")
    av = ashtakavarga.run_full_ashtakavarga_pipeline(
        {k: v for k, v in chart["planet_signs"].items() if k in E.CLASSICAL_PLANETS}, chart["lagna_sign"])
    print("Sarvashtakavarga:", av["sav"], "=", sum(av["sav"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
