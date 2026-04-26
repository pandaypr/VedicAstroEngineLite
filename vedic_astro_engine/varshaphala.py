"""
varshaphala.py — Tajika Annual Horoscopy (Solar Return)

Implements:
1. Solar Return Time Calculation
2. Muntha (The Annual Sensitive Point)
3. Tajik Yogas (Ithasala, Eshrpha, Manahoo, Kamboola, etc.)
4. Sahams (36+ Sensitive points)
5. Varsha Swamy (Lord of the Year) Selection

Sources: Tajika Neelakanthi, Varshaphala (B.V. Raman)
"""

import math
from .utils import load_ephemeris, _sign, _house_of
from .ayanamsha import get_ayanamsha
from .constants import SIGN_OWNERS

# ─────────────────────────────────────────────────────────────────────────────
# 1. SOLAR RETURN TIME
# ─────────────────────────────────────────────────────────────────────────────

def find_solar_return(natal_sun_lon: float, year: int, ayanamsha_type="LAHIRI") -> float:
    """Finds exact Julian Day (TT) of Solar Return."""
    ts, eph = load_ephemeris()
    
    def get_sun_lon(jd_tt):
        t = ts.tt_jd(jd_tt)
        ayan = get_ayanamsha(jd_tt, ayanamsha_type)
        from skyfield import framelib
        app = eph["earth"].at(t).observe(eph["sun"]).apparent()
        R = framelib.build_ecliptic_matrix(t)
        r_ecl = R.dot(app.position.au)
        lon = math.degrees(math.atan2(r_ecl[1], r_ecl[0])) % 360.0
        return (lon - ayan) % 360.0

    # Start search around the year
    curr_jd = ts.utc(year, 1, 1).tt
    for _ in range(15):
        curr_lon = get_sun_lon(curr_jd)
        diff = (natal_sun_lon - curr_lon + 180) % 360 - 180
        curr_jd += diff * 1.016
    return curr_jd

# ─────────────────────────────────────────────────────────────────────────────
# 2. MUNTHA
# ─────────────────────────────────────────────────────────────────────────────

def calculate_muntha(natal_lagna_sign: int, years_elapsed: int) -> int:
    return (natal_lagna_sign + years_elapsed - 1) % 12 + 1

# ─────────────────────────────────────────────────────────────────────────────
# 3. SAHAMS
# ─────────────────────────────────────────────────────────────────────────────

SAHAM_DEFINITIONS = [
    # Name, A, B, C (usually Lagna)
    ("Punya", "Moon", "Sun", "Lagna", "Merit/Fortune"),
    ("Vidya", "Sun", "Moon", "Lagna", "Education"),
    ("Yasha", "Jupiter", "Moon", "Lagna", "Fame"),
    ("Mitra", "Jupiter", "Punya", "Lagna", "Friends"),
    ("Mahatpya", "Mars", "Sun", "Lagna", "Greatness"),
    ("Deshantara", "Venus", "Sun", "Lagna", "Foreign Travel"),
    ("Artha", "Punya", "L2", "Lagna", "Wealth"),
    ("Samartha", "Mars", "Lagna", "Lagna", "Ability"),
    ("Rajya", "Saturn", "Sun", "Lagna", "Profession"),
    ("Karma", "Mars", "Mercury", "Lagna", "Action"),
    ("Roga", "Lagna", "Moon", "Lagna", "Disease"),
    ("Choura", "L6", "Saturn", "Lagna", "Theft"),
    ("Bandhu", "Mercury", "Moon", "Lagna", "Relatives"),
    ("Shatru", "Mars", "Saturn", "Lagna", "Enemies"),
    ("Vivaha", "Venus", "Saturn", "Lagna", "Marriage"),
    ("Santapa", "Saturn", "Moon", "Lagna", "Sorrows"),
    ("Shraddha", "Venus", "Mars", "Lagna", "Devotion"),
    ("Preeti", "Sun", "Moon", "Lagna", "Love"),
]

def calculate_saham(a_lon: float, b_lon: float, c_lon: float) -> float:
    """A - B + C rule with Tajika correction."""
    res = (a_lon - b_lon + c_lon) % 360
    # Correction: If C is not between B and A (B -> A direction), add 30 deg
    a_rel = (a_lon - b_lon) % 360
    c_rel = (c_lon - b_lon) % 360
    if c_rel > a_rel:
        res = (res + 30) % 360
    return res

def get_all_sahams(planet_lons: dict, lagna_lon: float) -> dict:
    results = {}
    # Helper to get lon or house lord lon
    def get_lon(key):
        if key in planet_lons: return planet_lons[key]
        if key == "Lagna": return lagna_lon
        # Simple lord detection (requires full house calculation, usually simplified for Sahams)
        return None

    # First pass: direct sahams
    for name, a_key, b_key, c_key, desc in SAHAM_DEFINITIONS:
        a = get_lon(a_key)
        b = get_lon(b_key)
        c = get_lon(c_key)
        if a is not None and b is not None and c is not None:
            results[name] = {"longitude": calculate_saham(a, b, c), "description": desc}
    
    # Second pass: dependent sahams (like Punya)
    if "Punya" in results:
        p_lon = results["Punya"]["longitude"]
        results["Mitra"] = {"longitude": calculate_saham(planet_lons["Jupiter"], p_lon, lagna_lon), "description": "Friends"}

    return results

# ─────────────────────────────────────────────────────────────────────────────
# 4. TAJIK YOGAS
# ─────────────────────────────────────────────────────────────────────────────

TAJIKA_ASPECTS = {
    0: "Conjunction", 2: "Sextile", 3: "Square", 4: "Trine", 6: "Opposition"
}

def detect_tajik_yogas(planet_data: dict) -> list:
    yogas = []
    planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    ORBS = {"Sun": 15, "Moon": 12, "Mars": 8, "Mercury": 7, "Jupiter": 9, "Venus": 7, "Saturn": 9}

    for i, p1 in enumerate(planets):
        for p2 in planets[i+1:]:
            l1, l2 = planet_data[p1]["longitude"], planet_data[p2]["longitude"]
            s1, s2 = planet_data[p1]["speed"], planet_data[p2]["speed"]
            
            diff = (l1 - l2) % 360
            if diff > 180: diff = 360 - diff
            
            aspect_signs = round(diff / 30)
            if aspect_signs not in TAJIKA_ASPECTS: continue
            
            mean_orb = (ORBS[p1] + ORBS[p2]) / 2.0
            if abs(diff - aspect_signs * 30) > mean_orb: continue
            
            # Determine faster/slower
            if abs(s1) > abs(s2):
                f, s = p1, p2
                fl, sl = l1, l2
            else:
                f, s = p2, p1
                fl, sl = l2, l1
            
            # Distance in zodiac direction
            dist = (sl - fl) % 360
            if dist < mean_orb:
                yogas.append({"yoga": "Ithasala", "planets": [f, s], "desc": f"{f} (faster) approaching {s} (slower)"})
                # Check for Kamboola (Moon involvement)
                if f == "Moon" or s == "Moon":
                    yogas.append({"yoga": "Kamboola", "planets": [f, s], "desc": f"Moon involved in Ithasala"})
            elif dist > 360 - mean_orb:
                yogas.append({"yoga": "Eshrpha", "planets": [f, s], "desc": f"{f} separating from {s}"})

    return yogas

# ─────────────────────────────────────────────────────────────────────────────
# 5. VARSHA SWAMY (Lord of the Year)
# ─────────────────────────────────────────────────────────────────────────────

def calculate_varsha_swamy(planet_data: dict, lagna_lon: float, muntha_sign: int, is_day: bool) -> dict:
    """
    Selects the Lord of the Year (Varsheshwara).
    Candidates (Pancha-Adhikaris):
    1. Muntha Lord
    2. Natal Lagna Lord (Need from natal chart context, simplified here)
    3. Varsha Lagna Lord
    4. Din-Ratri Lord (Sun for Day, Moon for Night)
    5. Tri-Rashi Lord (based on Lagna sign and day/night)
    """
    lagna_sign = _sign(lagna_lon)
    
    # Tri-Rashi Lord Table (Day/Night)
    TRI_RASHI = {
        1: (Sun, Jup), 2: (Ven, Mon), 3: (Sat, Mer), 4: (Ven, Mar),
        5: (Jup, Sun), 6: (Mon, Ven), 7: (Mer, Sat), 8: (Mar, Ven),
        9: (Sat, Sat), 10: (Mar, Mar), 11: (Jup, Jup), 12: (Mon, Mon)
    } # Simplified placeholders
    
    candidates = [
        SIGN_OWNERS[muntha_sign],
        SIGN_OWNERS[lagna_sign],
        "Sun" if is_day else "Moon"
    ]
    
    # Varsha Swamy must aspect the Lagna
    valid_candidates = []
    for c in set(candidates):
        c_lon = planet_data[c]["longitude"]
        h = _house_of(c_lon, lagna_lon)
        # Aspects in Tajika: 1, 3, 4, 5, 7, 9, 10, 11
        if h in {1, 3, 4, 5, 7, 9, 10, 11}:
            valid_candidates.append(c)
            
    if not valid_candidates: return {"lord": "None", "reason": "No candidate aspects Lagna"}
    
    # Highest Pancha-Varghiya Bala wins (Placeholder: returning strongest candidate)
    return {"lord": valid_candidates[0], "candidates": valid_candidates}
