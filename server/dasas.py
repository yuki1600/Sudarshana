"""The Dasas screen: the 49 dasas, their levels and their dates.

One entry per dasa view, with its builder and its labels. Years become dates through the default
definition (true sidereal solar years, ephemeris.dasa_year_mapper).
"""
import functools
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

from core_logic import dasa_systems as J

from . import basics as B

LEVELS = ["Maha Dasas", "Antardasas", "Pratyantardasas", "Sookshma-antardasas", "Praana-antardasas", "Deha-antardasas"]
PLANET_2 = ["", "Su", "Mo", "Ma", "Me", "Ju", "Ve", "Sa", "Ra", "Ke"]


@dataclass(frozen=True)
class Dasa:
    key: str                  # the dasa's key
    title: str
    group: str                # the tab: nakshatra, rasi or other
    build: Callable           # (jc, to_date) -> mahadasas
    label: Callable           # period -> text
    rule: Optional[Callable] = None   # (jc, options) -> the sub-period rule of dasas that divide by their own table
    varga_title: Optional[str] = None # the dasa's chart is an option: the title's start


def _planet(m):
    return J.PLANET_ABBR[m["lord"]] if m["lord"] else "Asc"


def _sign(m):
    return J.SIGN_ABBR[m["lord"]]


def _kalachakra(m):
    p = J.kalachakra_pada(m["lord"])
    return "%s (%s%d)" % (J.SIGN_ABBR[m["sign"]], B._tables()[0]["nakshatra_abbr"][p // 4].strip(), p % 4 + 1)


_sudarsana = lambda m: ":".join(J.SIGN_ABBR[m[k]] for k in ("lord", "moon", "sun"))  # noqa: E731
_nak = lambda name: functools.partial(J.nakshatra_dasa, name)  # noqa: E731
_grp = lambda name: functools.partial(J.group_dasa, name)  # noqa: E731
N, R, O = "nakshatra", "rasi", "other"

CATALOGUE: List[Dasa] = [
    Dasa("vimsottari_dasa", "Vimsottari", N, J.vimsottari_dasa, _planet),
    Dasa("ashtottari_dasa", "Ashtottari", N, _grp("ashtottari"), _planet),
    Dasa("kalachakra_dasa", "Kalachakra", N, J.kalachakra_dasa, _kalachakra, lambda jc, kw: lambda p: J.kalachakra_rule(p, kw["method"], kw["rohini_4_leo"])),
    Dasa("yogini_dasa", "Yogini", N, _nak("yogini"), _planet),
    Dasa("dwi_saptati_sama_dasa", "Dwisaptati sama", N, _nak("dwisaptati"), _planet),
    Dasa("shat_trimsa_sama_dasa", "Shattrimsa sama", N, _nak("shattrimsa"), _planet),
    Dasa("dwadasottari_dasa", "Dwadasottari", N, _nak("dwadasottari"), _planet),
    Dasa("chaturaseeti_sama_dasa", "Chaturaseeti sama", N, _nak("chaturaseeti"), _planet),
    Dasa("sataabdika_dasa", "Sataabdika", N, _nak("sataabdika"), _planet),
    Dasa("shodasottari_dasa", "Shodasottari", N, _nak("shodasottari"), _planet),
    Dasa("panchottari_dasa", "Panchottari", N, _nak("panchottari"), _planet),
    Dasa("shashti_hayani_dasa", "Shashtihayani", N, _grp("shashtihayani"), _planet),
    Dasa("saptarshi_nakshatra_dasa", "Saptarshi nakshatra", N, J.saptarshi_dasa, lambda m: B._tables()[0]["nakshatra_abbr"][m["lord"]].strip()),

    Dasa("narayana_dasa_of_d_1_chart", "Narayana", R, J.narayana_dasa, _sign, varga_title="Narayana of"),
    Dasa("lagnamsaka_dasa_from_d_9_chart", "Lagnamsaka", R, J.lagnamsaka_dasa, _sign, varga_title="Lagnamsaka from"),
    Dasa("padanaathaamsa_dasa_of_d_9_chart", "Padanaathaamsa", R, J.padanaathaamsa_dasa, _sign, varga_title="Padanaathaamsa of"),
    Dasa("sudasa", "Sudasa", R, J.sudasa, _sign),
    Dasa("drigdasa_of_d_1", "Drigdasa of D-1", R, J.drig_dasa, _sign),
    Dasa("lagna_kendradi_rasi_dasa_of_d_1", "Lagna Kendradi rasi of D-1", R, J.lagna_kendradi_rasi_dasa, _sign),
    Dasa("atma_karaka_kendradi_rasi_dasa_of_d_1", "AK Kendradi rasi of D-1", R, J.ak_kendradi_rasi_dasa, _sign),
    Dasa("trikona_dasa_of_d_1", "Trikona of D-1", R, J.trikona_dasa, _sign),
    Dasa("chara_dasa_of_d_1", "Chara (Parasara) of D-1", R, J.chara_parasara_dasa, _sign),
    Dasa("chara_dasa_of_k_n_rao", "Chara (K.N. Rao)", R, J.chara_knrao_dasa, _sign),
    Dasa("iranganti_rangacharya_chara_dasa", "Chara (Rangacharya)", R, J.chara_rangacharya_dasa, _sign),
    Dasa("yogardha_dasa_of_d_1", "Yogardha of D-1", R, J.yogardha_dasa, _sign),
    Dasa("ubhaya_paryaya_dasa_of_d_6_chart", "Paryaaya", R, J.paryaya_dasa, _sign, varga_title="Paryaaya of"),
    Dasa("shoola_dasa", "Shoola", R, J.shoola_dasa, _sign),
    Dasa("niryana_shoola_dasa", "Niryaana shoola", R, J.niryaana_shoola_dasa, _sign),
    Dasa("brahma_dasa", "Brahma", R, J.brahma_dasa, _sign),
    Dasa("sthira_dasa", "Sthira", R, J.sthira_dasa, _sign),
    Dasa("mandooka_dasa_of_d_11", "Mandooka of D-11", R, J.mandooka_d11_dasa, _sign),
    Dasa("mandooka_dasa_of_k_n_rao", "Mandooka (K.N. Rao)", R, J.mandooka_knrao_dasa, _sign),
    Dasa("navamsa_dasa", "Navamsa", R, J.navamsa_dasa, _sign),
    Dasa("varnada_dasa", "Varnada", R, J.varnada_dasa, _sign),

    Dasa("moola_dasa", "Moola", O, J.moola_dasa, _planet),
    Dasa("naisargika_dasa", "Naisargika", O, J.naisargika_dasa, _planet),
    Dasa("tara_dasa", "Tara", O, J.tara_dasa, _planet),
    Dasa("kaala_dasa", "Kaala", O, J.kaala_dasa, _planet),
    Dasa("chakra_dasa", "Chakra", O, J.chakra_dasa, _sign),
    Dasa("ak_kendradi_graha_dasa_of_d_1", "AK Kendradi graha of D-1", O, J.ak_kendradi_graha_dasa, _planet),
    Dasa("patyayini_dasa", "Patyayini", O, J.patyayini_dasa, _planet),
    Dasa("sudarsana_chakra_dasa_of_d_1", "Sudarsana Chakra", O, J.sudarsana_chakra_dasa, _sudarsana,
         lambda jc, kw: J.sudarsana_rule(jc, kw["varga"], kw["ad_from_lord"]), varga_title="Sudarsana Chakra of"),
    Dasa("buddhi_gati_dasa_of_d_1", "Buddhi gati", O, J.buddhi_gati_dasa, _planet, varga_title="Buddhi gati of"),
    Dasa("rasi_bhukta_vimsottari_dasa", "Rasi bhukta Vimsottari", O, J.rasi_bhukta_vimsottari_dasa, _planet),
    Dasa("karaka_dasa", "Karaka", O, J.karaka_dasa, lambda m: J.KARAKA_ABBR[m["karaka"]] + " " + PLANET_2[m["lord"]]),
    Dasa("tithi_ashtottari_dasa_of_janma_tithi_in_d_1", "Tithi Ashtottari", O, J.tithi_ashtottari_dasa, _planet),
    Dasa("yoga_vimsottari_dasa", "Yoga Vimsottari", O, J.yoga_vimsottari_dasa, _planet),
    Dasa("karana_chaturaseeti_sama_dasa", "Karana Chaturaseeti sama", O, J.karana_chaturaseeti_dasa, _planet),
    Dasa("tithi_yogini_dasa_of_janma_tithi", "Tithi Yogini", O, J.tithi_yogini_dasa, _planet),
]
BY_KEY: Dict[str, Dasa] = {d.key: d for d in CATALOGUE}


NAK_FAMILY = {"vimsottari_dasa", "ashtottari_dasa", "yogini_dasa", "dwi_saptati_sama_dasa", "shat_trimsa_sama_dasa", "dwadasottari_dasa", "chaturaseeti_sama_dasa",
              "sataabdika_dasa", "shodasottari_dasa", "panchottari_dasa", "shashti_hayani_dasa"}


def options(key: str, s) -> Dict[str, Any]:
    """One dasa's options as its builder's arguments: the Settings screen's, then what its own Options dialog changed (``per_dasa``, the per-dasa values of NakshatraDasaStartPoint and the like)."""
    kw = {**(base := _options(key, s)), **{k: v for k, v in s.per_dasa.get(key, {}).items() if k in base}}
    if kw.get("option") == 3:       # Ayur Narayana is the normal dasa with other nodal signs: service._typed
        kw["option"] = 0
    return kw


def _options(key: str, s) -> Dict[str, Any]:
    if key in NAK_FAMILY:
        kw = {"seed": s.dasa_seed, "shift": s.dasa_shift, "ad_method": s.dasa_ad_method, "tribhagi": s.dasa_tribhagi}
        return {**kw, "reverse": s.dasa_reverse} if key == "vimsottari_dasa" else kw
    return {
        "kalachakra_dasa": lambda: {"method": s.kalachakra_method, "rohini_4_leo": s.kalachakra_rohini_leo},
        "narayana_dasa_of_d_1_chart": lambda: {"varga": s.narayana_varga, "option": 0},
        "lagnamsaka_dasa_from_d_9_chart": lambda: {"varga": s.lagnamsaka_varga},
        "padanaathaamsa_dasa_of_d_9_chart": lambda: {"varga": s.padanathamsa_varga},
        "ubhaya_paryaya_dasa_of_d_6_chart": lambda: {"varga": s.paryaya_varga},
        "sudasa": lambda: {"ad_option": s.sudasa_ad},
        "shoola_dasa": lambda: {"ad_start": s.shoola_ad},
        "drigdasa_of_d_1": lambda: {"parasara": s.drig_parasara},
        "chara_dasa_of_d_1": lambda: {"exaltation_exception": s.chara_exaltation},
        "moola_dasa": lambda: {"use_lagna": s.moola_lagna, "use_moon": s.moola_moon, "use_sun": s.moola_sun, "no_correction": s.moola_no_correction},
        "naisargika_dasa": lambda: {"no_ad_for_md_lord": s.naisargika_no_lord, "third_tenth_no_ad": s.naisargika_3_10, "others_no_ad": s.naisargika_others},
        "tara_dasa": lambda: {"parasara": s.tara_parasara, "direction_from_star": s.tara_direction_from_star, "use_sesham": s.tara_sesham > 0, "sesham_rev_apasavya": s.tara_sesham == 2},
        "sudarsana_chakra_dasa_of_d_1": lambda: {"varga": s.sudarsana_varga, "ad_from_lord": s.sudarsana_ad_lord},
        "buddhi_gati_dasa_of_d_1": lambda: {"varga": s.buddhi_varga},
    }.get(key, dict)()


RASI_OPTIONS = {d.key for d in CATALOGUE if d.group == R}    # the dasas whose Options have a Strengths box


def listing() -> List[Dict[str, Any]]:
    return [{"key": d.key, "title": d.title, "group": d.group, "strengths": d.key in RASI_OPTIONS} for d in CATALOGUE]


def level(d: Dasa, jc, to_date, mds: List[Dict[str, Any]], path: List[int], tajaka: bool = False, kw: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """The periods at ``path`` (indices from the mahadasa down), the way a click on a period divides it."""
    if len(path) >= len(LEVELS):
        raise ValueError("no level below the deha-antardasas")
    if path:
        try:
            periods = J.sub_periods(mds, to_date, path, d.rule(jc, kw) if d.rule else None)
        except (IndexError, KeyError) as e:
            raise ValueError("no such period: %s" % e)
    else:
        periods = mds
    # the periods below the sign-bhukta mahadasas are labelled as signs, not planets; in a Tajaka chart the
    # mahadasas too: the sign whose index is the lord's point number
    label = _sign if d.key == "rasi_bhukta_vimsottari_dasa" and (path or tajaka) else d.label
    if d.key == "vimsottari_dasa" and kw and kw.get("tribhagi"):    # each mahadasa is a third of a cycle: "Sa (Push)", and below it "Sa"
        label = lambda m: PLANET_2[m["lord"]] + (" (%s)" % B._tables()[0]["nakshatra_abbr"][m["nak"]].strip() if "nak" in m else "")  # noqa: E731
    title = d.title if not d.varga_title else "%s D-%d" % (d.varga_title, J.VARGA_NUMBER[kw["varga"]])
    return {
        "title": title + " Dasa", "key": d.key, "path": path, "level": LEVELS[len(path)],
        "periods": [{"label": label(p), "start": p["start"], "end": p["end"], "years": p["years"]} for p in periods],
        "can_split": len(path) < len(LEVELS) - 1,
    }
