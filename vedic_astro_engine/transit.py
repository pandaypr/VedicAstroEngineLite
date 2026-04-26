"""
transit.py — Advanced Gochar (Transit) Analysis

Implements:
1. Moorthy Nirnaya (Moon's position at transit start)
2. Vedha (Blocking of transit results)
3. Transit Crossing Scanner (Precise degree hits)

Sources: Phala Deepika, Jataka Parijata
"""

import math
from datetime import timedelta
from .utils import load_ephemeris, _sign, _house_of
from .ayanamsha import get_ayanamsha

# ─────────────────────────────────────────────────────────────────────────────
# 1. MOORTHY NIRNAYA
# ─────────────────────────────────────────────────────────────────────────────

def calculate_moorthy_nirnaya(natal_moon_sign: int, transit_moon_sign: int) -> dict:
    """Classifies the transit quality based on Moon's position at sign entry."""
    house = (transit_moon_sign - natal_moon_sign) % 12 + 1
    
    if house in {1, 6, 11}:
        return {"house": house, "type": "Swarna (Gold)", "result": "Very Auspicious"}
    elif house in {2, 5, 9}:
        return {"house": house, "type": "Rajata (Silver)", "result": "Auspicious"}
    elif house in {3, 7, 10}:
        return {"house": house, "type": "Tamra (Copper)", "result": "Average"}
    else:
        return {"house": house, "type": "Loha (Iron)", "result": "Inauspicious"}

# ─────────────────────────────────────────────────────────────────────────────
# 2. VEDHA (The Blocking Rule)
# ─────────────────────────────────────────────────────────────────────────────

VEDHA_MAP = {
    "Sun": {3: 9, 6: 12, 10: 4, 11: 5},
    "Moon": {1: 5, 3: 9, 6: 12, 7: 2, 10: 4, 11: 8},
    "Mars": {3: 12, 6: 9, 11: 5},
    "Mercury": {2: 5, 4: 3, 6: 9, 8: 1, 10: 7, 11: 12},
    "Jupiter": {2: 12, 5: 4, 7: 2, 9: 10, 11: 8},
    "Venus": {1: 8, 2: 7, 3: 1, 4: 10, 5: 9, 8: 5, 9: 11, 11: 3, 12: 6},
    "Saturn": {3: 12, 6: 9, 11: 5}
}

def check_vedha(planet_name: str, transit_house: int, other_planet_houses: list) -> dict:
    rules = VEDHA_MAP.get(planet_name, {})
    blocking_house = rules.get(transit_house)
    
    if blocking_house and blocking_house in other_planet_houses:
        return {"is_blocked": True, "blocking_house": blocking_house}
    return {"is_blocked": False}

# ─────────────────────────────────────────────────────────────────────────────
# 3. TRANSIT SCANNER
# ─────────────────────────────────────────────────────────────────────────────

def find_transit_crossing(planet_name: str, target_lon: float, start_jd: float, days_limit: int = 365, ayanamsha_type="LAHIRI") -> list:
    """
    Scans for exact moments when a planet crosses target_lon.
    Uses binary search for precision.
    """
    ts, eph = load_ephemeris()
    results = []
    
    def get_lon(jd):
        t = ts.tt_jd(jd)
        ayan = get_ayanamsha(jd, ayanamsha_type)
        from skyfield import framelib
        # Map to Skyfield names
        PLANETS_MAP = {
            "Sun": "sun", "Moon": "moon", "Mercury": "mercury", "Venus": "venus", 
            "Mars": "mars barycenter", "Jupiter": "jupiter barycenter", 
            "Saturn": "saturn barycenter", "Uranus": "uranus barycenter", 
            "Neptune": "neptune barycenter", "Pluto": "pluto barycenter"
        }
        sky_name = PLANETS_MAP.get(planet_name, planet_name.lower())
        app = eph["earth"].at(t).observe(eph[sky_name]).apparent()
        R = framelib.build_ecliptic_matrix(t)
        r_ecl = R.dot(app.position.au)
        lon = math.degrees(math.atan2(r_ecl[1], r_ecl[0])) % 360.0
        return (lon - ayan) % 360.0

    step = 1.0 # 1 day
    curr_jd = start_jd
    prev_lon = get_lon(curr_jd)
    
    for _ in range(days_limit):
        curr_jd += step
        curr_lon = get_lon(curr_jd)
        
        # Check if target_lon is crossed
        # Normalize diff to [-180, 180]
        diff_prev = (prev_lon - target_lon + 180) % 360 - 180
        diff_curr = (curr_lon - target_lon + 180) % 360 - 180
        
        if diff_prev * diff_curr < 0: # Crossing detected
            # Binary search for sub-minute precision
            low, high = curr_jd - step, curr_jd
            for _ in range(15):
                mid = (low + high) / 2
                mid_lon = get_lon(mid)
                if ((mid_lon - target_lon + 180) % 360 - 180) * diff_prev > 0:
                    low = mid
                else:
                    high = mid
            results.append(ts.tt_jd(high).utc_iso())
            
        prev_lon = curr_lon
        
    return results
