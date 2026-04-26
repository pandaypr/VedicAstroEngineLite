"""
Vedic Astro Engine - Core Calculations
Author: Prabhakar Panday (prabhakarpanday4@gmail.com)
License: AGPL-3.0
"""
import math
import numpy as np
from skyfield.api import load, wgs84
from skyfield import framelib, almanac
from .utils import load_ephemeris, _sign, _house_of

from .vargas import get_all_vargas
from .panchanga import get_panchanga
from .dashas import get_vimshottari_dasha, get_yogini_dasha, get_chara_dasha
from .ashtakavarga import calculate_ashtakavarga
from .shadbala import ShadbalaCalculator
from .kaals import calculate_kaals
from .kp import get_kp_lords, get_placidus_cusps
from .ayanamsha import get_ayanamsha
from .special_points import calculate_special_lagnas, calculate_upagrahas, calculate_sphutas, calculate_time_upagrahas
from .aspects import calculate_aspects
from .avasthas import calculate_all_avasthas
from .yogas import (
    detect_nabhasa_yogas, detect_raja_yogas, detect_daridra_yogas,
    detect_marakas, calculate_ishta_kashta,
    detect_surya_yogas, detect_chandra_yogas, detect_combination_yogas,
    detect_parivartana_yogas, calculate_jaimini_karakas, detect_raja_sambandha
)
from .balarishta import detect_balarishta, detect_arishta_bhanga, detect_purva_janma_shapa
from .varshaphala import find_solar_return, calculate_muntha, get_all_sahams, detect_tajik_yogas
from .transit import calculate_moorthy_nirnaya, check_vedha
from .sarvatobhadra import calculate_sbc_vedha
from .sudarshan import calculate_sudarshan_chakra
from .longevity import calculate_pinda_ayu, get_health_vulnerabilities, calculate_indu_lagna

from .astronomy import find_next_eclipse
from datetime import datetime

J2000_JD = 2451545.0
J2000_TT = 2451545.0
PLANETS_7 = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

PLANETS_MAP = {
    "Sun": "sun",
    "Moon": "moon",
    "Mercury": "mercury",
    "Venus": "venus",
    "Mars": "mars barycenter",
    "Jupiter": "jupiter barycenter",
    "Saturn": "saturn barycenter",
    "Uranus": "uranus barycenter",
    "Neptune": "neptune barycenter",
    "Pluto": "pluto barycenter"
}


def _get_delta_psi(t) -> float:
    T = (t.tt - J2000_TT) / 36525.0
    omega = 125.04452 - 1934.136261 * T
    l_moon = 134.96298 + 477198.867398 * T
    l_sun = 357.52772 + 35999.050340 * T
    l_prime_moon = 93.27191 + 483202.017538 * T
    d_moon = 297.85036 + 445267.111480 * T
    
    dp = -17.1996 * math.sin(math.radians(omega)) \
         - 1.3187 * math.sin(math.radians(-2*d_moon + 2*l_prime_moon + 2*omega)) \
         - 0.2274 * math.sin(math.radians(2*l_prime_moon + 2*omega)) \
         + 0.2062 * math.sin(math.radians(2*omega)) \
         + 0.1426 * math.sin(math.radians(l_sun))
    return dp / 3600.0

def get_lagna_and_cusps(t, lat, lon_deg, ayanamsha):
    gast = t.gast
    last_hours = (gast + lon_deg / 15.0) % 24.0
    ramc = last_hours * 15.0
    
    T = (t.tt - J2000_TT) / 36525.0
    eps0 = 23.439291 - 0.0130042 * T
    deps = 0.00256 * math.cos(math.radians(125.04452 - 1934.136261 * T))
    eps = math.radians(eps0 + deps)
    
    L = math.radians(lat)
    ramc_rad = math.radians(ramc)
    
    num = math.cos(ramc_rad)
    den = -math.sin(ramc_rad) * math.cos(eps) - math.tan(L) * math.sin(eps)
    asc_deg = math.degrees(math.atan2(num, den)) % 360.0
    
    y = math.sin(ramc_rad)
    x = math.cos(ramc_rad) * math.cos(eps)
    mc_deg = math.degrees(math.atan2(y, x)) % 360.0
    
    asc_sidereal = (asc_deg - ayanamsha) % 360.0
    mc_sidereal = (mc_deg - ayanamsha) % 360.0
    dc_sidereal = (asc_sidereal + 180.0) % 360.0
    ic_sidereal = (mc_sidereal + 180.0) % 360.0
    
    cusps = [0] * 12
    cusps[0] = asc_sidereal
    cusps[3] = ic_sidereal
    cusps[6] = dc_sidereal
    cusps[9] = mc_sidereal
    
    q1_size = (ic_sidereal - asc_sidereal) % 360.0
    cusps[1] = (asc_sidereal + q1_size / 3.0) % 360.0
    cusps[2] = (asc_sidereal + 2 * q1_size / 3.0) % 360.0
    
    q2_size = (dc_sidereal - ic_sidereal) % 360.0
    cusps[4] = (ic_sidereal + q2_size / 3.0) % 360.0
    cusps[5] = (ic_sidereal + 2 * q2_size / 3.0) % 360.0
    
    q3_size = (mc_sidereal - dc_sidereal) % 360.0
    cusps[7] = (dc_sidereal + q3_size / 3.0) % 360.0
    cusps[8] = (dc_sidereal + 2 * q3_size / 3.0) % 360.0
    
    q4_size = (asc_sidereal - mc_sidereal) % 360.0
    cusps[10] = (mc_sidereal + q4_size / 3.0) % 360.0
    cusps[11] = (mc_sidereal + 2 * q4_size / 3.0) % 360.0
    
    return {"lagna": asc_sidereal, "cusps": cusps}

def get_sunrise_sunset(lat, lon_deg, date_utc):
    ts, eph = load_ephemeris()
    observer = wgs84.latlon(lat, lon_deg)
    t0 = ts.utc(date_utc.year, date_utc.month, date_utc.day, 0, 0, 0)
    t1 = ts.utc(date_utc.year, date_utc.month, date_utc.day + 1, 0, 0, 0)
    
    f = almanac.sunrise_sunset(eph, observer)
    times, events = almanac.find_discrete(t0, t1, f)
    
    sunrise = None
    sunset = None
    for t_event, is_sunrise in zip(times, events):
        if is_sunrise:
            sunrise = t_event.utc_iso()
        else:
            sunset = t_event.utc_iso()
            
    return {"sunrise": sunrise, "sunset": sunset}

def is_retrograde(t, sky_name):
    ts, eph = load_ephemeris()
    dt = 1.0 / 86400.0
    t_minus = ts.tt_jd(t.tt - dt)
    t_plus  = ts.tt_jd(t.tt + dt)
    
    earth = eph["earth"]
    body = eph[sky_name]
    
    app_m = earth.at(t_minus).observe(body).apparent()
    app_p = earth.at(t_plus).observe(body).apparent()
    
    Rm = framelib.build_ecliptic_matrix(t_minus)
    Rp = framelib.build_ecliptic_matrix(t_plus)
    
    r_m = Rm.dot(app_m.position.au)
    r_p = Rp.dot(app_p.position.au)
    
    lon_m = math.degrees(math.atan2(r_m[1], r_m[0]))
    lon_p = math.degrees(math.atan2(r_p[1], r_p[0]))
    
    diff = (lon_p - lon_m + 180.0) % 360.0 - 180.0
    return diff < 0

def build_charts(year, month, day, hour, minute, lat, lon_deg, ayanamsha_type="LAHIRI", node_type="TRUE"):
    ts, eph = load_ephemeris()
    t = ts.utc(year, month, day, hour, minute, 0)
    jd = t.tt
    
    ayan = get_ayanamsha(jd, ayanamsha_type)
    delta_psi = _get_delta_psi(t)
    
    results = {
        "planets": {},
        "ayanamsha": ayan,
        "date_utc": t.utc_iso()
    }
    
    earth = eph["earth"]
    R = framelib.build_ecliptic_matrix(t)
    
    for name, sky_name in PLANETS_MAP.items():
        app = earth.at(t).observe(eph[sky_name]).apparent()
        r_ecl = R.dot(app.position.au)
        
        lon = math.degrees(math.atan2(r_ecl[1], r_ecl[0])) % 360.0
        trop_mean = lon - delta_psi
        sid_lon = (trop_mean - ayan) % 360.0
        
        _, dec, _ = app.radec()
        retro = is_retrograde(t, sky_name)
        
        results["planets"][name] = {
            "longitude": sid_lon,
            "declination": dec.degrees,
            "is_retrograde": retro,
            "speed": 0.0  # filled after node calculation
        }
        
    # True Node or Mean Node calculation
    if node_type.upper() == "TRUE":
        dt_node = 60.0 / 86400.0
        t_plus = ts.tt_jd(t.tt + dt_node)
        t_minus = ts.tt_jd(t.tt - dt_node)
        
        def geo_icrf(t_obs):
            return eph["moon"].at(t_obs).position.km - earth.at(t_obs).position.km

        r_icrf = geo_icrf(t)
        v_icrf = (geo_icrf(t_plus) - geo_icrf(t_minus)) / (2.0 * dt_node)
        
        r = R.dot(r_icrf)
        v = R.dot(v_icrf)
        h = np.cross(r, v)
        
        omega = math.degrees(math.atan2(h[0], -h[1])) % 360.0
        rahu_mean_trop = omega + delta_psi
    else:
        # Mean Node formula (IAU)
        T = (t.tt - J2000_TT) / 36525.0
        omega = 125.04452 - 1934.136261 * T
        rahu_mean_trop = omega % 360.0
        
    rahu_sid = (rahu_mean_trop - ayan) % 360.0
    ketu_sid = (rahu_sid + 180.0) % 360.0
    
    results["planets"]["Rahu"] = {"longitude": rahu_sid, "declination": 0.0, "is_retrograde": True, "speed": -0.053}
    results["planets"]["Ketu"] = {"longitude": ketu_sid, "declination": 0.0, "is_retrograde": True, "speed": -0.053}
    
    # Compute approximate speeds via central difference for classical 7
    # and determine Stambhi (Stationary) status based on user thresholds.
    stambhi_thresholds = {
        "Mercury": 0.100, "Venus": 0.080, "Mars": 0.050, "Jupiter": 0.015, "Saturn": 0.012
    }
    
    dt_speed = 1.0 / 86400.0  # 1 second in days
    for name, sky_name in list(PLANETS_MAP.items())[:7]:  # Sun through Saturn
        if name not in results["planets"]: continue
        try:
            t_p = ts.tt_jd(t.tt + dt_speed)
            t_m = ts.tt_jd(t.tt - dt_speed)
            app_p = earth.at(t_p).observe(eph[sky_name]).apparent()
            app_m = earth.at(t_m).observe(eph[sky_name]).apparent()
            r_p = framelib.build_ecliptic_matrix(t_p).dot(app_p.position.au)
            r_m = framelib.build_ecliptic_matrix(t_m).dot(app_m.position.au)
            lp = math.degrees(math.atan2(r_p[1], r_p[0]))
            lm = math.degrees(math.atan2(r_m[1], r_m[0]))
            diff = (lp - lm + 180.0) % 360.0 - 180.0
            speed = diff * 43200.0
            results["planets"][name]["speed"] = round(speed, 6)
            
            # Retrograde?
            results["planets"][name]["is_retrograde"] = speed < 0
            
            # Stambhi (Stationary)?
            threshold = stambhi_thresholds.get(name)
            if threshold and abs(speed) < threshold:
                results["planets"][name]["status"] = "Stationary (Stambhi)"
            elif speed < 0:
                results["planets"][name]["status"] = "Retrograde"
            else:
                results["planets"][name]["status"] = "Direct"
        except Exception:
            pass

    
    # Sunrise / Sunset
    sun_times = get_sunrise_sunset(lat, lon_deg, t.utc)
    results.update(sun_times)
    
    # Houses / Lagna (Porphyry by default)
    houses = get_lagna_and_cusps(t, lat, lon_deg, ayan)
    results.update(houses)
    
    # Calculate Sign and House for all planets
    for name, p_data in results["planets"].items():
        lon = p_data["longitude"]
        p_data["sign"] = int(lon / 30) + 1
        # Simple house calculation from Lagna (Equal house logic for predictive flags)
        rel_deg = (lon - results["lagna"]) % 360
        p_data["house"] = int(rel_deg / 30) + 1
    
    # KP Astrology (Placidus + Sublords)
    # We calculate the eps_rad (obliquity) and other parameters for Placidus
    T = (t.tt - J2000_TT) / 36525.0
    eps0 = 23.439291 - 0.0130042 * T
    deps = 0.00256 * math.cos(math.radians(125.04452 - 1934.136261 * T))
    eps_rad = math.radians(eps0 + deps)
    
    gast = t.gast
    last_hours = (gast + lon_deg / 15.0) % 24.0
    ramc_deg = last_hours * 15.0
    
    # Compute MC to pass to Placidus
    y = math.sin(math.radians(ramc_deg))
    x = math.cos(math.radians(ramc_deg)) * math.cos(eps_rad)
    mc_deg = math.degrees(math.atan2(y, x)) % 360.0
    mc_sidereal = (mc_deg - ayan) % 360.0
    
    # Placidus calculation
    try:
        placidus_cusps = get_placidus_cusps(ramc_deg, eps_rad, math.radians(lat), results["lagna"], mc_sidereal)
    except Exception:
        placidus_cusps = results["cusps"] # Fallback if iteration fails near poles
        
    results["kp"] = {
        "placidus_cusps": placidus_cusps,
        "planets": {name: get_kp_lords(p["longitude"]) for name, p in results["planets"].items()}
    }
    results["kp"]["planets"]["Ascendant"] = get_kp_lords(results["lagna"])
    
    # Kaals
    dt_utc = t.utc_datetime()
    results["kaals"] = calculate_kaals(results.get("sunrise"), results.get("sunset"), dt_utc.weekday())
    

    # Special Lagnas and Upagrahas

    if results.get("sunrise"):
        sr_dt = datetime.fromisoformat(results["sunrise"].replace('Z', '+00:00'))
        results["special_lagnas"] = calculate_special_lagnas(results["planets"]["Sun"]["longitude"], results["lagna"], sr_dt, dt_utc)
        results["upagrahas"] = calculate_upagrahas(results["planets"]["Sun"]["longitude"])
        
        # Sphutas (Calculate Mandi for sphutas)
        if results.get("sunset"):
            ss_dt = datetime.fromisoformat(results["sunset"].replace('Z', '+00:00'))
            time_up = calculate_time_upagrahas(sr_dt, ss_dt, dt_utc, lat, lon_deg)
            # Find Mandi lagna exactly
            mandi_t = ts.from_datetime(datetime.fromtimestamp(time_up["Mandi"], tz=dt_utc.tzinfo))
            mandi_houses = get_lagna_and_cusps(mandi_t, lat, lon_deg, get_ayanamsha(mandi_t.tt, ayanamsha_type))
            results["sphutas"] = calculate_sphutas(
                {name: p["longitude"] for name, p in results["planets"].items()},
                results["lagna"],
                mandi_houses["lagna"]
            )
            # Add Gulika and Mandi to planets
            gulika_t = ts.from_datetime(datetime.fromtimestamp(time_up["Gulika"], tz=dt_utc.tzinfo))
            gulika_houses = get_lagna_and_cusps(gulika_t, lat, lon_deg, get_ayanamsha(gulika_t.tt, ayanamsha_type))
            results["planets"]["Mandi"] = {"longitude": mandi_houses["lagna"], "declination": 0.0, "is_retrograde": False}
            results["planets"]["Gulika"] = {"longitude": gulika_houses["lagna"], "declination": 0.0, "is_retrograde": False}
    
    # Vargas
    results["vargas"] = {name: get_all_vargas(p["longitude"]) for name, p in results["planets"].items() if name not in ["Mandi", "Gulika"]}
    results["vargas"]["Ascendant"] = get_all_vargas(results["lagna"])
    
    # Panchanga
    results["panchanga"] = get_panchanga(results["planets"]["Sun"]["longitude"], results["planets"]["Moon"]["longitude"])
    
    # Muhurta (Inception) Engine
    from .muhurta import get_muhurta_summary
    results["muhurta"] = get_muhurta_summary(results["panchanga"], results["planets"], dt_utc.weekday())

    # Dashas

    asc_sign_num = int(results["lagna"] / 30) + 1
    planet_signs = {name: int(p["longitude"] / 30) + 1 for name, p in results["planets"].items() if name not in ["Mandi", "Gulika", "Uranus", "Neptune", "Pluto"]}
    
    from .dashas import get_vimshottari_dasha, get_yogini_dasha, get_chara_dasha, get_kaal_chakra_dasha
    results["dashas"] = {
        "vimshottari": get_vimshottari_dasha(results["planets"]["Moon"]["longitude"], t.utc_iso(), max_depth=6),
        "yogini": get_yogini_dasha(results["planets"]["Moon"]["longitude"], t.utc_iso()),
        "chara": get_chara_dasha(asc_sign_num, planet_signs, t.utc_iso()),
        "kaal_chakra": get_kaal_chakra_dasha(results["planets"]["Moon"]["longitude"], t.utc_iso())
    }
    
    # Ashtakavarga (Only core 7 planets)
    planet_lons_7 = {name: p["longitude"] for name, p in results["planets"].items() if name in ShadbalaCalculator.PLANETS}
    results["ashtakavarga"] = calculate_ashtakavarga(planet_lons_7, results["lagna"])
    
    # --- NEW MODULES ---
    # All planet longitudes (excluding math-only points for some)
    all_lons = {name: p["longitude"] for name, p in results["planets"].items()}
    classical_lons = {k: v for k, v in all_lons.items()
                      if k not in ["Mandi", "Gulika", "Uranus", "Neptune", "Pluto"]}
    
    # Aspects (Drishti)
    results["aspects"] = calculate_aspects(classical_lons)
    
    # Avasthas
    results["avasthas"] = calculate_all_avasthas(
        {k: v for k, v in classical_lons.items() if k not in ["Rahu", "Ketu"]}
    )
    
    # Ishta / Kashta Phala (for 7 classical planets with speed data)
    results["ishta_kashta"] = {}
    for p in ShadbalaCalculator.PLANETS:
        if p in results["planets"]:
            spd = results["planets"][p].get("speed", 0.0)
            results["ishta_kashta"][p] = calculate_ishta_kashta(
                p, results["planets"][p]["longitude"], spd
            )
    
    # Jaimini Karakas
    results["jaimini_karakas"] = calculate_jaimini_karakas(classical_lons)

    # Yogas — all categories
    results["yogas"] = {
        "nabhasa":     detect_nabhasa_yogas(classical_lons),
        "raja":        detect_raja_yogas(classical_lons, results["lagna"]),
        "daridra":     detect_daridra_yogas(classical_lons, results["lagna"]),
        "surya":       detect_surya_yogas(classical_lons),
        "chandra":     detect_chandra_yogas(classical_lons, results["lagna"]),
        "combination": detect_combination_yogas(classical_lons, results["lagna"]),
        "parivartana": detect_parivartana_yogas(classical_lons, results["lagna"]),
        "raja_sambandha": detect_raja_sambandha(
            classical_lons, results["lagna"], results["jaimini_karakas"]
        ),
    }
    
    # Marakas
    
    # Balarishta & Arishta Bhanga
    balarishtas = detect_balarishta(classical_lons, results["lagna"])
    results["balarishta"] = balarishtas
    results["arishta_bhanga"] = detect_arishta_bhanga(classical_lons, results["lagna"], balarishtas)
    
    # Purva Janma Shapa
    results["purva_janma_shapa"] = detect_purva_janma_shapa(classical_lons, results["lagna"])
    
    # --- TAJIKA / VARSHAPHALA (Current year) ---
    current_year = datetime.now().year
    # Need natal sun for solar return, but for now we just do muntha
    # Assumes building for current year if not specified
    results["muntha"] = calculate_muntha(int(results["lagna"]/30)+1, current_year - year)
    results["tajik_yogas"] = detect_tajik_yogas(results["planets"])
    
    # --- TRANSIT & CHAKRAS ---
    results["sudarshan_chakra"] = calculate_sudarshan_chakra(classical_lons, results["lagna"])
    results["sarvatobhadra"] = calculate_sbc_vedha(classical_lons, classical_lons)
    
    # --- SHADBALA (Planetary Strengths) ---
    is_day = sr_dt <= dt_utc < ss_dt if sr_dt and ss_dt else True
    moon_diff = (results["planets"]["Moon"]["longitude"] - results["planets"]["Sun"]["longitude"]) % 360
    
    # Simple approximations for lords (can be refined)
    # Weekday lord: 0=Mon, 1=Tue... 6=Sun
    weekday_map = {0: "Moon", 1: "Mars", 2: "Mercury", 3: "Jupiter", 4: "Venus", 5: "Saturn", 6: "Sun"}
    weekday_lord = weekday_map.get(dt_utc.weekday(), "Sun")
    
    results["shadbala"] = {}
    for p in ShadbalaCalculator.PLANETS:
        p_data = results["planets"][p]
        vargas = results["vargas"][p]
        
        sthana = ShadbalaCalculator.calculate_sthana_bala(p, p_data["longitude"], p_data["house"], vargas)
        dig = ShadbalaCalculator.calculate_dig_bala(p, p_data["longitude"], results["lagna"], results["lagna"]) # Placeholder for MC
        # Hora lord placeholder - using Sun for now if day, else Moon
        kala = ShadbalaCalculator.calculate_kala_bala(p, is_day, moon_diff, weekday_lord, "Sun" if is_day else "Moon")
        cheshta = ShadbalaCalculator.calculate_cheshta_bala(p, p_data.get("speed", 0), p_data.get("is_retrograde", False))
        drig = ShadbalaCalculator.calculate_drig_bala(p, {name: pl["longitude"] for name, pl in results["planets"].items() if name in ShadbalaCalculator.PLANETS})
        
        comps = {
            "sthana_bala": sthana,
            "dig_bala": dig,
            "kala_bala": kala,
            "cheshta_bala": cheshta,
            "drig_bala": drig,
            "naisargika_bala": ShadbalaCalculator.NAISARGIKA_BALA.get(p, 0)
        }
        results["shadbala"][p] = ShadbalaCalculator.get_total_shadbala(p, comps)
        results["shadbala"][p]["components"] = comps

    from .vimsopaka import get_vimsopaka_bala
    results["vimsopaka"] = {p: get_vimsopaka_bala(p, results["planets"]) for p in PLANETS_7}

    # --- LONGEVITY & HEALTH ---

    results["longevity"] = calculate_pinda_ayu(classical_lons, results["lagna"])
    results["marakas"] = detect_marakas(classical_lons, results["lagna"])
    results["health_vulnerabilities"] = get_health_vulnerabilities({p: results["planets"][p]["house"] for p in results["planets"] if p in classical_lons or p in ["Rahu", "Ketu"]}, {})
    results["indu_lagna"] = calculate_indu_lagna(classical_lons, results["lagna"], results["planets"]["Moon"]["longitude"])

    return results



def get_skyfield_julday(year, month, day, hour=0.0):
    ts, _ = load_ephemeris()
    h_int = int(hour)
    m_int = int((hour - h_int) * 60)
    s_float = ((hour - h_int) * 60 - m_int) * 60
    return ts.utc(year, month, day, h_int, m_int, s_float)

def skyfield_calc_ut(t, body_name, ayanamsha_type="LAHIRI"):
    ts, eph = load_ephemeris()
    jd = t.tt
    ayan = get_ayanamsha(jd, ayanamsha_type)
    delta_psi = _get_delta_psi(t)
    
    sky_name = PLANETS_MAP.get(body_name, body_name)
    app = eph["earth"].at(t).observe(eph[sky_name]).apparent()
    R = framelib.build_ecliptic_matrix(t)
    r_ecl = R.dot(app.position.au)
    
    lon = math.degrees(math.atan2(r_ecl[1], r_ecl[0])) % 360.0
    sid_lon = (lon - delta_psi - ayan) % 360.0
    _, dec, _ = app.radec()
    retro = is_retrograde(t, sky_name)
    
    return [sid_lon, dec.degrees, -1.0 if retro else 1.0]

def skyfield_rise_trans(t, lat, lon_deg):
    return get_sunrise_sunset(lat, lon_deg, t.utc)
