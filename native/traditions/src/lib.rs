//! The Traditions tab's calculations (server/traditions.py, docs/SOURCES.md section 19), from the XALEN Ephemeris
//! crates: Western techniques on the app's own positions, the Chinese and world traditions on the birth's moment and
//! date, I Ching, numerology and Lal Kitab. Every function takes plain numbers and names and returns JSON, the crates'
//! own result types as they serialise.

use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use serde_json::{json, Value};

use xalen_chinese::{self as cn, fengshui, qimen, ziwei, EarthlyBranch, HeavenlyStem};
use xalen_ephem::{mean_lilith, true_lilith, Almanac, Body};
use xalen_houses::{compute_houses, GeoLocation, HouseSystem};
use xalen_iching as ic;
use xalen_lalkitab::{self as lk, LalKitabChart};
use xalen_numerology::{self as nu, System};
use xalen_time::JdTT;
use xalen_western::{
    antiscia, aspects, cosmobiology, declination, dignity, harmonics, hellenistic, lots, lunar, midpoints, patterns,
    progressions, sabian, stars, uranian,
};
use xalen_world::{aztec, celtic, egyptian, mahabote, mayan, nine_star_ki, persian, saju, tibetan};

fn out(v: Value) -> PyResult<String> {
    serde_json::to_string(&v).map_err(|e| PyValueError::new_err(e.to_string()))
}

fn input(s: &str) -> PyResult<Value> {
    serde_json::from_str(s).map_err(|e| PyValueError::new_err(e.to_string()))
}

fn num(v: &Value, k: &str) -> PyResult<f64> {
    v[k].as_f64().ok_or_else(|| PyValueError::new_err(format!("{k}: a number")))
}

fn norm(d: f64) -> f64 {
    d.rem_euclid(360.0)
}

// ---------------------------------------------------------------------------------------------------------------------
// Western
// ---------------------------------------------------------------------------------------------------------------------

const HOUSES: [(&str, HouseSystem); 15] = [
    ("placidus", HouseSystem::Placidus), ("koch", HouseSystem::Koch), ("whole_sign", HouseSystem::WholeSign),
    ("equal", HouseSystem::Equal), ("porphyry", HouseSystem::Porphyry), ("regiomontanus", HouseSystem::Regiomontanus),
    ("campanus", HouseSystem::Campanus), ("morinus", HouseSystem::Morinus), ("alcabitius", HouseSystem::Alcabitius),
    ("topocentric", HouseSystem::Topocentric), ("meridian", HouseSystem::Meridian), ("vehlow", HouseSystem::Vehlow),
    ("sripati", HouseSystem::Sripati), ("krusinski", HouseSystem::KrusinskiPisa),
    ("sunshine", HouseSystem::SunshineMakransky),
];

/// The house cusps, ascendant, MC and vertex (tropical degrees) of a system named as in HOUSES, at UT ``jd_ut`` with the
/// true obliquity ``obliquity`` (degrees).
#[pyfunction]
fn houses(jd_ut: f64, lat: f64, lon: f64, obliquity: f64, system: &str) -> PyResult<String> {
    let sys = HOUSES.iter().find(|(n, _)| *n == system).map(|(_, s)| *s)
        .ok_or_else(|| PyValueError::new_err(format!("unknown house system {system}")))?;
    let h = compute_houses(jd_ut, &GeoLocation::new(lat, lon), obliquity.to_radians(), sys);
    let d = |r: f64| norm(r.to_degrees());
    out(json!({"system": system, "cusps": h.cusps.iter().map(|c| d(*c)).collect::<Vec<_>>(), "ascendant": d(h.ascendant),
               "mc": d(h.mc), "vertex": d(h.vertex)}))
}

/// Chiron (XALEN's apparent place, null where its orbit does not hold) and the mean and true Black Moon Lilith at TT
/// ``jd_tt``: tropical degrees of date.
#[pyfunction]
fn extra_bodies(jd_tt: f64) -> PyResult<String> {
    let t = JdTT(jd_tt);
    let chiron = Almanac::default_vedic().geocentric_ecliptic_tt(Body::Chiron, t).ok().map(|p| norm(p.longitude.to_degrees()));
    out(json!({"Chiron": chiron, "Lilith": norm(mean_lilith(t).to_degrees()),
               "True Lilith": true_lilith(t).ok().map(|r| norm(r.to_degrees()))}))
}

const ALL_ASPECTS: [aspects::AspectType; 11] = [
    aspects::AspectType::Conjunction, aspects::AspectType::Opposition, aspects::AspectType::Trine, aspects::AspectType::Square,
    aspects::AspectType::Sextile, aspects::AspectType::SemiSextile, aspects::AspectType::Quincunx, aspects::AspectType::SemiSquare,
    aspects::AspectType::Sesquiquadrate, aspects::AspectType::Quintile, aspects::AspectType::BiQuintile,
];
const CLASSICAL: [&str; 7] = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"];

/// Everything the Western sub tab shows from the natal positions. Input: {bodies: [{name, lon, lat, speed}], asc, mc,
/// obliquity, birth_jd, now_jd, age}; the bodies tropical, the Sun first.
#[pyfunction]
fn western(data: &str) -> PyResult<String> {
    let v = input(data)?;
    let bodies = v["bodies"].as_array().ok_or_else(|| PyValueError::new_err("bodies"))?;
    let (asc, mc, obl) = (num(&v, "asc")?, num(&v, "mc")?, num(&v, "obliquity")?);
    let (birth_jd, now_jd) = (num(&v, "birth_jd")?, num(&v, "now_jd")?);
    let age = v["age"].as_u64().unwrap_or(0) as u32;
    let mut named: Vec<(String, f64, f64, f64)> = Vec::new();
    for b in bodies {
        named.push((b["name"].as_str().unwrap_or("").to_string(), num(b, "lon")?, num(b, "lat")?, num(b, "speed")?));
    }
    let lon = |n: &str| named.iter().find(|b| b.0 == n).map(|b| b.1).unwrap_or(0.0);
    let sun = lon("Sun");
    let is_day = lots::is_day_chart(sun, asc);
    let with_angles: Vec<(&str, f64)> = named.iter().map(|b| (b.0.as_str(), b.1)).chain([("Asc", asc), ("MC", mc)]).collect();

    let dignities: Vec<Value> = named.iter().filter(|b| CLASSICAL.contains(&b.0.as_str())).map(|b| {
        let (p, s, d) = (b.0.as_str(), (b.1 / 30.0) as usize % 12, b.1 % 30.0);
        json!({"body": p, "score": dignity::essential_dignity_score(p, s, d), "domicile": dignity::is_domicile(p, s),
               "exaltation": dignity::is_exaltation(p, s), "detriment": dignity::is_detriment(p, s), "fall": dignity::is_fall(p, s),
               "triplicity": dignity::is_triplicity_ruler(p, s), "term": dignity::is_term_ruler(p, s, d), "face": dignity::is_face_ruler(p, s, d),
               "combustion": if p == "Sun" { "" } else { lunar::combustion_status(p, b.1, sun) }})
    }).collect();
    let aspect_input: Vec<(String, f64, f64)> = named.iter().map(|b| (b.0.clone(), b.1, b.3))
        .chain([("Asc".to_string(), asc, 0.0), ("MC".to_string(), mc, 0.0)]).collect();
    let found = aspects::find_all_aspects(&aspect_input, &ALL_ASPECTS);
    let shapes: Vec<Value> = patterns::detect_patterns(&with_angles.iter().map(|p| p.1).collect::<Vec<_>>(), 8.0).into_iter()
        .map(|(kind, idx)| json!({"pattern": kind, "bodies": idx.iter().map(|i| with_angles[*i].0).collect::<Vec<_>>()})).collect();
    let pp = lots::PlanetPositions { sun, moon: lon("Moon"), mercury: lon("Mercury"), venus: lon("Venus"), mars: lon("Mars"),
                                     jupiter: lon("Jupiter"), saturn: lon("Saturn"), asc, mc };
    let all_lots: Vec<Value> = lots::compute_all_lots(&pp, is_day).into_iter().map(|(n, l)| json!({"name": n, "lon": l})).collect();
    let sabians: Vec<Value> = with_angles.iter().map(|(n, l)| {
        let s = sabian::sabian_for_degree(*l);
        json!({"body": n, "symbol": s, "decanate": sabian::decanate(*l).1, "degree_type": sabian::degree_type(*l)})
    }).collect();
    let decl_input: Vec<(&str, f64, f64)> = named.iter().map(|b| (b.0.as_str(), b.1, b.2)).collect();
    let fortune = lots::part_of_fortune(asc, sun, lon("Moon"), is_day);
    let spirit = lots::part_of_spirit(asc, sun, lon("Moon"), is_day);
    let zr = |l: f64| -> Vec<Value> {
        hellenistic::zodiacal_releasing((l / 30.0) as usize % 12, birth_jd, 2).into_iter()
            .filter(|p| p.end_jd >= birth_jd && p.start_jd <= now_jd + 36525.0).take(120).map(|p| json!(p)).collect()
    };
    let star_hits: Vec<Value> = stars::brighter_than(2.5).into_iter().flat_map(|s| {
        let (slon, _) = stars::precessed_ecliptic(s, birth_jd);
        with_angles.iter().filter(move |(_, l)| aspects::angular_distance(*l, slon) <= 1.0)
            .map(move |(n, l)| json!({"body": n, "star": s.name, "magnitude": s.magnitude, "star_lon": slon, "orb": aspects::angular_distance(*l, slon)}))
    }).collect();
    let tnps: Vec<Value> = uranian::all_tnp_longitudes(birth_jd).iter().map(|(t, l)| json!({"name": t, "lon": l})).collect();
    let harm: Vec<Value> = [5u32, 7, 9].iter().map(|h| json!(harmonics::compute_harmonic_chart(&with_angles, *h))).collect();
    let elong = lunar::moon_elongation(sun, lon("Moon"));
    out(json!({
        "is_day": is_day, "sect": hellenistic::planetary_sect(is_day),
        "dignities": dignities, "aspects": found, "patterns": shapes, "lots": all_lots, "sabian": sabians,
        "midpoints": midpoints::find_activations(&with_angles, 1.5),
        "cosmobiology": cosmobiology::cosmobiology_chart(&with_angles, 1.5),
        "declinations": declination::detect_declination_aspects_from_ecliptic(&decl_input, obl, 1.0),
        "antiscia": antiscia::detect_antiscia(&with_angles, 1.0),
        "harmonics": harm, "fixed_stars": star_hits, "uranian": tnps,
        "moon_phase": {"elongation": elong, "illumination": lunar::lunar_illumination(elong)},
        "hellenistic": {
            "fortune": fortune, "spirit": spirit,
            "profection": hellenistic::annual_profection((asc / 30.0) as usize % 12, age),
            "zr_spirit": zr(spirit), "zr_fortune": zr(fortune),
            "firdaria": hellenistic::compute_firdaria(birth_jd, is_day),
            "decennials": hellenistic::compute_decennials(birth_jd, is_day, 4),
        },
    }))
}

/// The secondary-progressed moment for ``target_jd`` (a day after birth for each year of life).
#[pyfunction]
fn progressed_jd(birth_jd: f64, target_jd: f64) -> f64 {
    progressions::progressed_jd(birth_jd, target_jd, progressions::ProgressionType::Secondary)
}

/// Solar-arc directions: every natal point moved by the progressed Sun's arc. ``natal``: [[name, lon], ...].
#[pyfunction]
fn solar_arc(natal_sun: f64, progressed_sun: f64, natal: &str) -> PyResult<String> {
    let v: Vec<(String, f64)> = serde_json::from_str(natal).map_err(|e| PyValueError::new_err(e.to_string()))?;
    let pairs: Vec<(&str, f64)> = v.iter().map(|(n, l)| (n.as_str(), *l)).collect();
    out(json!(progressions::solar_arc_directions(natal_sun, progressed_sun, &pairs)))
}

// ---------------------------------------------------------------------------------------------------------------------
// Chinese
// ---------------------------------------------------------------------------------------------------------------------

/// The month stem by the Five Tigers rule (五虎遁): the Yin month's stem from the year stem, then on by the month.
fn month_stem(year_stem: HeavenlyStem, month: usize) -> HeavenlyStem {
    let first = [2usize, 4, 6, 8, 0][(year_stem as usize) % 5];
    HeavenlyStem::from_index((first + month - 1) % 10)
}

/// The Chinese sub tab. ``solar_year`` and ``solar_month`` (1 = the Yin month from Li Chun) come from the app's own Sun;
/// ``jd_local``: the birth's local civil Julian day (the day pillar turns at local midnight); ``hour``: local hours;
/// ``lunar_year`` / ``lunar_month`` / ``lunar_day``: the Chinese lunar date (core_logic/chinese_calendar.py), whose year's
/// stem and branch Zi Wei takes; ``year``/``month``/``day``: the
/// local civil date, for Flying Stars, Ba Zhai and Qi Men.
#[pyfunction]
#[allow(clippy::too_many_arguments)]
fn chinese(solar_year: i32, solar_month: usize, jd_local: f64, hour: f64, lunar_year: i32, lunar_month: u32, lunar_day: u32, male: bool,
           year: i32, month: u32, day: u32) -> PyResult<String> {
    let y = cn::sexagenary_year(solar_year);
    let m = cn::Pillar { stem: month_stem(y.stem, solar_month), branch: EarthlyBranch::from_index((solar_month + 1) % 12) };
    let d = cn::sexagenary_day(jd_local);
    let hb = cn::hour_branch(hour);
    let h = cn::Pillar { stem: cn::hour_stem(d.stem, hb), branch: hb };
    let bazi = cn::BaZiChart { year: y.clone(), month: m.clone(), day: d.clone(), hour: h.clone(), day_master: d.stem };
    let elements: Vec<Value> = [&y, &m, &d, &h].iter().map(|p| json!({"stem": p.stem.element(), "branch": p.branch.element(),
                                                                       "stem_yang": p.stem.is_yang()})).collect();
    let ly = cn::sexagenary_year(lunar_year);
    let zw = ziwei::compute_chart(ly.stem, lunar_month, lunar_day, hb);
    let ming = zw.palaces.iter().position(|p| p.branch == zw.ming_gong_branch).unwrap_or(0);
    let yang = ly.stem.is_yang() == male;
    out(json!({
        "bazi": bazi, "elements": elements,
        "ziwei": {"chart": zw, "minor": ziwei::place_minor_stars(ly.stem, ly.branch, lunar_month, hb), "lunar_year": ly,
                  "da_xian": ziwei::compute_da_xian(zw.wu_xing_ju, ming, yang, 12),
                  "lunar_month": lunar_month, "lunar_day": lunar_day},
        "flying_stars": fengshui::flying_star_chart(year), "annual_center": fengshui::annual_center_star(year),
        "monthly_center": fengshui::monthly_center_star(year, month),
        "star_meanings": (1..=9u8).map(|s| json!({"star": s, "meaning": fengshui::star_meaning(s), "element": fengshui::star_element(s)})).collect::<Vec<_>>(),
        "ba_zhai": fengshui::ba_zhai(solar_year, male),
        "qimen": qimen::compute_qimen(year, month, day, hour as u32),
    }))
}

// ---------------------------------------------------------------------------------------------------------------------
// World traditions
// ---------------------------------------------------------------------------------------------------------------------

/// The World sub tab: Korean Saju and its Daeun, Nine Star Ki, Burmese Mahabote, the Tibetan year, the Mayan and Aztec
/// calendars, the Egyptian decans of the Sun and the ascendant, the Celtic tree and the Persian Jarbakhtar.
/// ``jd_local``: the local civil Julian day; ``sun`` and ``asc``: tropical degrees; ``almuten``: the strongest of the seven
/// grahas by essential dignity, where the Jarbakhtar begins.
#[pyfunction]
#[allow(clippy::too_many_arguments)]
fn world(year: i32, month: u32, day: u32, hour: u32, jd_local: f64, male: bool, sun: f64, asc: f64, birth_year: f64, almuten: &str) -> PyResult<String> {
    let s = saju::compute_saju(year, month, day, hour);
    let gender = if male { saju::Gender::Male } else { saju::Gender::Female };
    let decan = |l: f64| { let d = egyptian::decan_for_degree(l); json!(d) };
    out(json!({
        "saju": s, "daeun": saju::daeun(&s, gender, year),
        "nine_star_ki": nine_star_ki::nine_star_ki(year, month), "nine_star_compatible": nine_star_ki::compatible_stars(nine_star_ki::year_star(year)),
        "mahabote": mahabote::mahabote_from_jd(jd_local), "mahabote_square": mahabote::mahabote_house_square_from_jd(jd_local),
        "tibetan": tibetan::tibetan_year(year),
        "mayan": {"long_count": mayan::long_count_from_jd(jd_local), "round": mayan::calendar_round(jd_local)},
        "aztec": aztec::tonalpohualli_from_jd(jd_local),
        "egyptian": {"sun": decan(sun), "asc": decan(asc), "all": egyptian::all_decans().to_vec()},
        "celtic": {"month": celtic::celtic_tree(month, day), "year": celtic::celtic_year_tree(year)},
        "persian": persian::compute_jarbakhtar(birth_year, almuten), "almuten": almuten,
    }))
}

// ---------------------------------------------------------------------------------------------------------------------
// I Ching, numerology, Lal Kitab
// ---------------------------------------------------------------------------------------------------------------------

/// The hexagram of a date and hour (Mei Hua Yi Shu), its changing line's text, and the relating, nuclear and opposite
/// hexagrams with their six line texts.
#[pyfunction]
fn iching(year: i32, month: u32, day: u32, hour: u32) -> PyResult<String> {
    let r = ic::hexagram_from_date(year, month, day, hour);
    let full = |h: &ic::Hexagram| json!({"hexagram": h, "lines": ic::line_texts(h.number)});
    out(json!({"changing_line": r.changing_line, "line_text": r.changing_line_text, "primary": full(r.primary), "relating": full(r.relating),
               "nuclear": full(ic::nuclear_hexagram(r.primary)), "opposite": full(ic::opposite_hexagram(r.primary))}))
}

/// The core numbers of a name and birth date, in the Pythagorean or Chaldean system, with their meanings.
#[pyfunction]
fn numerology(name: &str, year: u32, month: u32, day: u32, chaldean: bool, current_year: u32) -> PyResult<String> {
    let system = if chaldean { System::Chaldean } else { System::Pythagorean };
    let p = nu::full_profile(year, month, day, name, system);
    let py = nu::personal_year(month, day, current_year);
    let numbers = [("Life path", p.life_path), ("Birthday", p.birthday_number), ("Expression", p.expression),
                   ("Soul urge", p.soul_urge), ("Personality", p.personality), ("Maturity", p.maturity), ("Personal year", py)];
    out(json!({"profile": p, "numbers": numbers.iter().map(|(k, n)| json!({"name": k, "number": n, "meaning": nu::number_meaning(*n),
                                                                          "karmic_debt": nu::karmic_debt(*n)})).collect::<Vec<_>>()}))
}

/// Lal Kitab from the houses of the nine grahas (``houses``: {"Sun": 1-12, ...}, counted from the lagna) and the year of
/// life for the Varshphal.
#[pyfunction]
fn lalkitab(houses: &str, year_of_life: u32) -> PyResult<String> {
    let v = input(houses)?;
    let mut chart = LalKitabChart::empty();
    let map = v.as_object().ok_or_else(|| PyValueError::new_err("houses"))?;
    for (name, h) in map {
        let planet: lk::Planet = serde_json::from_value(json!(name)).map_err(|e| PyValueError::new_err(e.to_string()))?;
        chart.place(planet, h.as_u64().unwrap_or(1) as usize);
    }
    let mut rows = Vec::new();
    for (name, h) in map {
        let planet: lk::Planet = serde_json::from_value(json!(name)).map_err(|e| PyValueError::new_err(e.to_string()))?;
        let house = h.as_u64().unwrap_or(1) as usize;
        let others: Vec<lk::Planet> = chart.planets_in(house).iter().copied().filter(|p| *p != planet).collect();
        rows.push(json!({"planet": planet, "house": house, "effect": lk::planet_effect(planet, house),
                         "dormant": lk::is_dormant(planet, house, &others)}));
    }
    out(json!({"chart": chart, "planets": rows, "debts": lk::detect_debts(&chart),
               "annual": lk::build_annual_chart(&chart, year_of_life), "year_of_life": year_of_life,
               "rulers": (1..=12usize).map(|h| json!(lk::houses::natural_rulers(h))).collect::<Vec<_>>()}))
}

#[pymodule]
fn traditions(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(houses, m)?)?;
    m.add_function(wrap_pyfunction!(extra_bodies, m)?)?;
    m.add_function(wrap_pyfunction!(western, m)?)?;
    m.add_function(wrap_pyfunction!(progressed_jd, m)?)?;
    m.add_function(wrap_pyfunction!(solar_arc, m)?)?;
    m.add_function(wrap_pyfunction!(chinese, m)?)?;
    m.add_function(wrap_pyfunction!(world, m)?)?;
    m.add_function(wrap_pyfunction!(iching, m)?)?;
    m.add_function(wrap_pyfunction!(numerology, m)?)?;
    m.add_function(wrap_pyfunction!(lalkitab, m)?)?;
    m.add("HOUSE_SYSTEMS", HOUSES.iter().map(|(n, _)| *n).collect::<Vec<_>>())?;
    Ok(())
}
