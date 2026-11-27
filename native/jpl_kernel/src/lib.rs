//! Graha positions from a NASA JPL planetary ephemeris kernel for Settings > Ephemeris "XALEN"
//! (core_logic/ephemeris/jpl.py, docs/SOURCES.md section 1).
//!
//! The kernel (DE442, an SPK of Chebyshev segments) is read by the XALEN Ephemeris SPK reader (xalen-ephem's
//! `De440Reader`, which takes any type 2 SPK), and the place of date comes from its IAU 2006 precession with frame
//! bias and IAU 2000B nutation (xalen-coords). Light-time, light deflection by the Sun and annual aberration are the
//! IAU SOFA routines iauLd and iauAb (Explanatory Supplement to the Astronomical Almanac, 3rd ed., ch. 7), seen from
//! the Earth's centre or from the place. `calc` answers the shape of Swiss Ephemeris' `swe_calc_ut` for the bodies
//! and position flags core_logic asks for.

use std::path::Path;
use std::sync::OnceLock;

use pyo3::create_exception;
use pyo3::exceptions::{PyRuntimeError, PyValueError};
use pyo3::prelude::*;
use xalen_coords::{gast_deg, mean_obliquity, nutation_2000b, precession_bias_matrix_iau2006, rotate3, transpose3};
use xalen_ephem::{mean_lunar_node, De440Reader, EphemerisError};
use xalen_time::JdTT;

type V3 = [f64; 3];
type M3 = [[f64; 3]; 3];

const J2000: f64 = 2_451_545.0;
const AU_KM: f64 = 149_597_870.7;
/// Speed of light, AU per day.
const C: f64 = 299_792.458 * 86_400.0 / AU_KM;
/// Schwarzschild radius of the Sun (2GM/c^2), AU: SOFA's SRS.
const SRS: f64 = 1.974_125_743_36e-8;
/// G (M_Earth + M_Moon), AU^3/day^2: GMB of DE440 and DE442.
const GMB: f64 = 8.997_011_393_442_166e-10;
/// The distance Swiss Ephemeris gives the mean node (the Moon's mean distance), AU.
const MEAN_NODE_DIST: f64 = 0.002_569_555_289_8;
/// Step of the numerical speeds, days.
const SPEED_STEP: f64 = 1e-4;
/// Step of the Moon's velocity for the osculating (true) node, days.
const NODE_STEP: f64 = 0.01;

create_exception!(jpl_kernel, OutOfRange, PyValueError, "The moment is outside the kernel's span.");

static KERNEL: OnceLock<De440Reader> = OnceLock::new();

fn kernel() -> PyResult<&'static De440Reader> {
    KERNEL.get().ok_or_else(|| PyRuntimeError::new_err("no kernel loaded: call jpl_kernel.load(path) first"))
}

fn py_err(e: EphemerisError) -> PyErr {
    match e {
        EphemerisError::EpochOutOfRange(jd) => OutOfRange::new_err(format!("JD {jd} is outside the kernel")),
        e => PyRuntimeError::new_err(e.to_string()),
    }
}

// ---------------------------------------------------------------------------------------------------------------------
// Vectors and rotations
// ---------------------------------------------------------------------------------------------------------------------

fn add(a: V3, b: V3) -> V3 {
    [a[0] + b[0], a[1] + b[1], a[2] + b[2]]
}

fn sub(a: V3, b: V3) -> V3 {
    [a[0] - b[0], a[1] - b[1], a[2] - b[2]]
}

fn scale(a: V3, k: f64) -> V3 {
    [a[0] * k, a[1] * k, a[2] * k]
}

fn dot(a: V3, b: V3) -> f64 {
    a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
}

fn cross(a: V3, b: V3) -> V3 {
    [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
}

fn norm(a: V3) -> f64 {
    dot(a, a).sqrt()
}

fn unit(a: V3) -> V3 {
    scale(a, 1.0 / norm(a))
}

fn mul(a: M3, b: M3) -> M3 {
    let mut m = [[0.0; 3]; 3];
    for (i, row) in m.iter_mut().enumerate() {
        for (j, x) in row.iter_mut().enumerate() {
            *x = (0..3).map(|k| a[i][k] * b[k][j]).sum();
        }
    }
    m
}

/// Rotation of the axes about x by `a` (SOFA iauRx).
fn rx(a: f64) -> M3 {
    let (s, c) = a.sin_cos();
    [[1.0, 0.0, 0.0], [0.0, c, s], [0.0, -s, c]]
}

/// Rotation of the axes about z by `a` (SOFA iauRz).
fn rz(a: f64) -> M3 {
    let (s, c) = a.sin_cos();
    [[c, s, 0.0], [-s, c, 0.0], [0.0, 0.0, 1.0]]
}

// ---------------------------------------------------------------------------------------------------------------------
// The kernel
// ---------------------------------------------------------------------------------------------------------------------

/// TDB from TT: the periodic terms of the Explanatory Supplement (3rd ed., 3.5), under 2 ms.
fn tdb(tt: f64) -> f64 {
    let g = (357.53 + 0.985_600_28 * (tt - J2000)).to_radians();
    tt + (0.001_657 * g.sin() + 0.000_014 * (2.0 * g).sin()) / 86_400.0
}

fn at(k: &De440Reader, target: i32, center: i32, tdb: f64) -> Result<V3, EphemerisError> {
    let (x, y, z) = k.position_at(target, center, tdb)?;
    Ok([x / AU_KM, y / AU_KM, z / AU_KM])
}

/// Barycentric ICRS position of a NAIF body (10 Sun, 1-9 planet barycentres, 301 Moon, 399 Earth), AU.
fn ssb(k: &De440Reader, naif: i32, tdb: f64) -> Result<V3, EphemerisError> {
    match naif {
        301 | 399 => Ok(add(at(k, 3, 0, tdb)?, at(k, naif, 3, tdb)?)),
        n => at(k, n, 0, tdb),
    }
}

fn ssb_velocity(k: &De440Reader, naif: i32, tdb: f64) -> Result<V3, EphemerisError> {
    const H: f64 = 1e-3;
    Ok(scale(sub(ssb(k, naif, tdb + H)?, ssb(k, naif, tdb - H)?), 0.5 / H))
}

/// The geometric geocentric Moon, ICRS, AU.
fn moon(k: &De440Reader, tdb: f64) -> Result<V3, EphemerisError> {
    Ok(sub(at(k, 301, 3, tdb)?, at(k, 399, 3, tdb)?))
}

/// Swiss Ephemeris body number -> NAIF id: the Sun, the Moon, and the planets' barycentres (as Swiss Ephemeris
/// gives them by default).
fn naif(body: i32) -> Option<i32> {
    match body {
        0 => Some(10),
        1 => Some(301),
        2 => Some(1),
        3 => Some(2),
        4..=9 => Some(body),
        _ => None,
    }
}

// ---------------------------------------------------------------------------------------------------------------------
// The place of date
// ---------------------------------------------------------------------------------------------------------------------

#[derive(Clone, Copy)]
struct Opts {
    light: bool,
    deflect: bool,
    aberrate: bool,
    nutate: bool,
    equatorial: bool,
}

/// The frames at TT Julian centuries `t`: ICRS -> the output equator of date (true, or mean without nutation),
/// ICRS -> the true equator (the Earth turns about it), the obliquity to the output ecliptic, and the nutation in
/// longitude when nutation is on.
fn frames(t: f64, nutate: bool) -> (M3, M3, f64, f64) {
    let pb = precession_bias_matrix_iau2006(t);
    let nut = nutation_2000b(t);
    let eps = mean_obliquity(t);
    // SOFA iauNumat: Rx(-(eps + deps)) Rz(-dpsi) Rx(eps)
    let true_eq = mul(mul(mul(rx(-(eps + nut.delta_epsilon)), rz(-nut.delta_psi)), rx(eps)), pb);
    if nutate {
        (true_eq, true_eq, eps + nut.delta_epsilon, nut.delta_psi)
    } else {
        (pb, true_eq, eps, 0.0)
    }
}

/// The place's geocentric position and velocity, ICRS (AU, AU/day): the IERS ellipsoid Swiss Ephemeris uses
/// (a = 6378136.6 m, f = 1/298.25642) turned by Greenwich apparent sidereal time; polar motion ignored.
fn observer(ut: f64, t: f64, true_eq: M3, (lon, lat, alt): (f64, f64, f64)) -> (V3, V3) {
    const A: f64 = 6_378_136.6;
    const F: f64 = 1.0 / 298.256_42;
    const OMEGA: f64 = 7.292_115e-5 * 86_400.0; // the Earth's rotation, rad/day
    let au_m = AU_KM * 1000.0;
    let (sp, cp) = lat.to_radians().sin_cos();
    let c = 1.0 / (cp * cp + (1.0 - F) * (1.0 - F) * sp * sp).sqrt();
    let s = (1.0 - F) * (1.0 - F) * c;
    let theta = (gast_deg(ut, t) + lon).to_radians();
    let rxy = (A * c + alt) * cp / au_m;
    let p = [rxy * theta.cos(), rxy * theta.sin(), (A * s + alt) * sp / au_m];
    let v = [-OMEGA * p[1], OMEGA * p[0], 0.0];
    let back = transpose3(true_eq);
    (rotate3(back, p), rotate3(back, v))
}

/// SOFA iauLd: light from a body (direction `p` from the observer, `q` from the Sun) bent by the Sun; `e` the
/// direction Sun -> observer, `em` that distance (AU).
fn deflect(p: V3, q: V3, e: V3, em: f64) -> V3 {
    let qdqpe = dot(q, add(q, e));
    let dlim = 1e-6 / (em * em).max(1.0); // SOFA iauLdsun's limiter
    let w = SRS / em / qdqpe.max(dlim);
    add(p, scale(cross(p, cross(e, q)), w))
}

/// SOFA iauAb: aberration for an observer moving at `v` (units of c), `s` AU from the Sun.
fn aberrate(p: V3, v: V3, s: f64) -> V3 {
    let pdv = dot(p, v);
    let bm1 = (1.0 - dot(v, v)).sqrt();
    let w1 = 1.0 + pdv / (1.0 + bm1);
    let w2 = SRS / s;
    unit([0, 1, 2].map(|i| p[i] * bm1 + w1 * v[i] + w2 * (v[i] - pdv * p[i])))
}

/// (longitude or right ascension, latitude or declination, degrees) of a direction in the equator of date.
fn spherical(eq: V3, eps: f64, equatorial: bool) -> (f64, f64) {
    let v = if equatorial { eq } else { rotate3(rx(eps), eq) };
    (v[1].atan2(v[0]).to_degrees().rem_euclid(360.0), (v[2] / norm(v)).clamp(-1.0, 1.0).asin().to_degrees())
}

/// A point of the ecliptic of date (the nodes) in the output frame.
fn from_ecliptic(lon: f64, eps: f64, equatorial: bool) -> (f64, f64) {
    if !equatorial {
        return (lon.to_degrees().rem_euclid(360.0), 0.0);
    }
    let (s, c) = lon.sin_cos();
    spherical(rotate3(rx(-eps), [c, s, 0.0]), eps, true)
}

/// (lon, lat, distance) of Swiss Ephemeris body `body` at TT `tt`, UT `ut`.
fn place(k: &De440Reader, body: i32, tt: f64, ut: f64, o: Opts, topo: Option<(f64, f64, f64)>) -> Result<V3, EphemerisError> {
    let t = (tt - J2000) / 36_525.0;
    let tb = tdb(tt);
    let (out_eq, true_eq, eps, dpsi) = frames(t, o.nutate);
    if body == 10 {
        // the mean node: the IAU polynomial (Meeus ch. 47) on the mean equinox, nutated with the rest
        let (lon, lat) = from_ecliptic(mean_lunar_node(JdTT(tt)) + dpsi, eps, o.equatorial);
        return Ok([lon, lat, MEAN_NODE_DIST]);
    }
    if body == 11 {
        // the true (osculating) node: where the plane of the Moon's geocentric orbit at this moment, r x v of the
        // geometric Moon, meets the ecliptic of date; its distance is the osculating ellipse's at the node. The
        // ecliptic is one plane on either equinox: the mean ecliptic of date here, the nutation in longitude after
        let m = mul(rx(mean_obliquity(t)), precession_bias_matrix_iau2006(t));
        let r = rotate3(m, moon(k, tb)?);
        let v = rotate3(m, scale(sub(moon(k, tb + NODE_STEP)?, moon(k, tb - NODE_STEP)?), 0.5 / NODE_STEP));
        let h = cross(r, v);
        let node = h[0].atan2(-h[1]);
        let e = sub(scale(cross(v, h), 1.0 / GMB), scale(r, 1.0 / norm(r)));
        let dist = dot(h, h) / GMB / (1.0 + dot(e, [node.cos(), node.sin(), 0.0]));
        let (lon, lat) = from_ecliptic(node + dpsi, eps, o.equatorial);
        return Ok([lon, lat, dist]);
    }
    let target = naif(body).ok_or_else(|| EphemerisError::ComputationFailed(format!("no body {body} in the kernel")))?;
    let mut obs = ssb(k, 399, tb)?;
    let mut obs_v = ssb_velocity(k, 399, tb)?;
    if let Some(place) = topo {
        let (p, v) = observer(ut, t, true_eq, place);
        obs = add(obs, p);
        obs_v = add(obs_v, v);
    }
    let mut emitted = tb;
    let mut p = sub(ssb(k, target, tb)?, obs);
    if o.light {
        for _ in 0..3 {
            emitted = tb - norm(p) / C;
            p = sub(ssb(k, target, emitted)?, obs);
        }
    }
    let dist = norm(p);
    let mut u = unit(p);
    if o.deflect || o.aberrate {
        let sun = ssb(k, 10, tb)?;
        let e = sub(obs, sun);
        let em = norm(e);
        if o.deflect && target != 10 && target != 301 {
            // as Swiss Ephemeris: not for the Sun's own light, nor the Moon's (under a milliarc second)
            u = deflect(u, unit(sub(ssb(k, target, emitted)?, sun)), unit(e), em);
        }
        if o.aberrate {
            u = aberrate(unit(u), scale(obs_v, 1.0 / C), em);
        }
    }
    let (lon, lat) = spherical(rotate3(out_eq, u), eps, o.equatorial);
    Ok([lon, lat, dist])
}

// ---------------------------------------------------------------------------------------------------------------------
// Python
// ---------------------------------------------------------------------------------------------------------------------

/// Load the kernel at `path` (once a process) and return its span (first and last Julian day, TDB) and its label.
#[pyfunction]
fn load(path: &str) -> PyResult<(f64, f64, String)> {
    if KERNEL.get().is_none() {
        let reader = De440Reader::from_file(Path::new(path)).map_err(|e| PyRuntimeError::new_err(format!("{path}: {e}")))?;
        let _ = KERNEL.set(reader); // another thread's copy of the same file may have won
    }
    let k = kernel()?;
    Ok((k.header().jd_start, k.header().jd_end, k.kernel_id().unwrap_or("SPK").to_string()))
}

/// swe_calc_ut's (lon, lat, distance, and their speeds a day) for Swiss Ephemeris body `body` (0 Sun, 1 Moon,
/// 2-9 Mercury..Pluto, 10 mean node, 11 true node) at TT `tt` (UT `ut`, for the sidereal time). `light`: light-time
/// (off = the geometric, "true" position); `deflect`, `aberrate`: the Sun's light deflection, annual aberration;
/// `nutate`: the true equinox (off = mean); `equatorial`: right ascension and declination; `topo`: the observer at
/// (east longitude, latitude, metres) instead of the Earth's centre (not for the nodes, as Swiss Ephemeris).
#[pyfunction]
#[pyo3(signature = (tt, ut, body, light, deflect, aberrate, nutate, equatorial, speed, topo=None))]
#[allow(clippy::too_many_arguments)]
fn calc(
    tt: f64,
    ut: f64,
    body: i32,
    light: bool,
    deflect: bool,
    aberrate: bool,
    nutate: bool,
    equatorial: bool,
    speed: bool,
    topo: Option<(f64, f64, f64)>,
) -> PyResult<(f64, f64, f64, f64, f64, f64)> {
    if naif(body).is_none() && body != 10 && body != 11 {
        return Err(PyValueError::new_err(format!("body {body} is not in the kernel")));
    }
    let k = kernel()?;
    let o = Opts { light, deflect, aberrate, nutate, equatorial };
    let topo = if body >= 10 { None } else { topo };
    let x = place(k, body, tt, ut, o, topo).map_err(py_err)?;
    if !speed {
        return Ok((x[0], x[1], x[2], 0.0, 0.0, 0.0));
    }
    let a = place(k, body, tt - SPEED_STEP, ut - SPEED_STEP, o, topo).map_err(py_err)?;
    let b = place(k, body, tt + SPEED_STEP, ut + SPEED_STEP, o, topo).map_err(py_err)?;
    let per_day = 0.5 / SPEED_STEP;
    let dlon = (b[0] - a[0] + 540.0).rem_euclid(360.0) - 180.0;
    Ok((x[0], x[1], x[2], dlon * per_day, (b[1] - a[1]) * per_day, (b[2] - a[2]) * per_day))
}

#[pymodule]
fn jpl_kernel(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(load, m)?)?;
    m.add_function(wrap_pyfunction!(calc, m)?)?;
    m.add("OutOfRange", m.py().get_type::<OutOfRange>())?;
    Ok(())
}
