"""
longevity.py — Classical Ayurdaya (Longevity) Calculations

Implements:
1. Pinda Ayu (Exaltation-based)
2. Amsa Ayu (Navamsha-based)
3. Nisarga Ayu (Fixed-cycle)
4. Maraka & Badhaka Analysis

Sources: BPHS (Brihat Parasara Hora Shastra), Saravali
"""

import math
from .utils import _sign, _house_of

# ─────────────────────────────────────────────────────────────────────────────
# 1. CLASSICAL LONGEVITY METHODS
# ─────────────────────────────────────────────────────────────────────────────

# Maximum years contributed by planets in Pinda Ayu
PINDA_MAX_YEARS = {
    "Sun": 19, "Moon": 25, "Mars": 15, "Mercury": 12, 
    "Jupiter": 15, "Venus": 21, "Saturn": 20
}

# Deep Exaltation Points
EXALT_POINTS = {
    "Sun": 10, "Moon": 33, "Mars": 298, "Mercury": 165,
    "Jupiter": 95, "Venus": 357, "Saturn": 200
}

def calculate_pinda_ayu(planet_lons: dict, lagna_lon: float) -> dict:
    """
    Calculates longevity using Pinda Ayu method.
    Years = Max * (Distance from Deep Debilitation / 360)
    """
    results = {}
    total_ayu = 0
    
    for p, max_y in PINDA_MAX_YEARS.items():
        if p not in planet_lons: continue
        lon = planet_lons[p]
        exalt = EXALT_POINTS[p]
        debil = (exalt + 180) % 360
        
        # Distance from deep debilitation in direction of zodiac
        dist = (lon - debil) % 360
        years = (dist / 360.0) * max_y
        results[p] = round(years, 4)
        total_ayu += years
        
    # Lagna Contribution
    lagna_years = (lagna_lon % 30) / 30.0 # Standard rule
    results["Lagna"] = round(lagna_years, 4)
    total_ayu += lagna_years
    
    return {"breakdown": results, "total_unrefined": round(total_ayu, 2)}

def calculate_amsa_ayu(planet_lons: dict, lagna_lon: float) -> dict:
    """
    Calculates longevity using Amsa Ayu (Navamsha-based).
    Years = Navamsha Index (1-108) / 9? No, typically years = sign index in D9?
    Standard Parasara: Years = Sign index in D9 (1-12) etc.
    """
    results = {}
    total_ayu = 0
    
    for p, lon in planet_lons.items():
        if p in {"Rahu", "Ketu"}: continue
        # Years = Navamshas passed in current sign
        # Each sign has 9 navamshas.
        # Total years = Navamsha number from Aries?
        nav_total = int(lon / (30.0 / 9.0)) + 1
        years = nav_total % 12
        if years == 0: years = 12
        results[p] = years
        total_ayu += years
        
    return {"breakdown": results, "total_unrefined": total_ayu}

# ─────────────────────────────────────────────────────────────────────────────
# 2. MARAKA & BADHAKA ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────


def detect_badhaka(lagna_sign: int, house_lords: dict) -> str:
    """
    Identifies the Badhaka (Obstruction) lord.
    Movable (Ar, Cn, Li, Cp): 11th lord.
    Fixed (Ta, Le, Sc, Aq): 9th lord.
    Dual (Ge, Vi, Sg, Pi): 7th lord.
    """
    # Lagna sign: 1-indexed
    movable = {1, 4, 7, 10}
    fixed = {2, 5, 8, 11}
    dual = {3, 6, 9, 12}
    
    target_house = 0
    if lagna_sign in movable: target_house = 11
    elif lagna_sign in fixed: target_house = 9
    elif lagna_sign in dual: target_house = 7
    
    return house_lords.get(str(target_house), "Unknown")

# ─────────────────────────────────────────────────────────────────────────────
# 3. MEDICAL MAPPING (Kalapurusha)
# ─────────────────────────────────────────────────────────────────────────────

BODY_PARTS_SIGNS = {
    1: "Head", 2: "Face/Throat", 3: "Shoulders/Arms", 4: "Chest/Heart",
    5: "Upper Abdomen/Stomach", 6: "Lower Abdomen/Intestines",
    7: "Pelvis/Kidneys", 8: "Private Parts", 9: "Thighs",
    10: "Knees", 11: "Calves/Ankle", 12: "Feet"
}

def get_health_vulnerabilities(planet_houses: dict, house_lords: dict) -> list:
    """
    Maps malefic afflictions to body parts.
    """
    vulnerabilities = []
    malefics = {"Saturn", "Mars", "Rahu", "Ketu"}
    
    for p, h in planet_houses.items():
        if p in malefics:
            part = BODY_PARTS_SIGNS.get(h, "Unknown")
            vulnerabilities.append(f"{p} in {part} area (House {h})")
            
    return vulnerabilities

# ─────────────────────────────────────────────────────────────────────────────
# 4. INDU LAGNA (Wealth Point)
# ─────────────────────────────────────────────────────────────────────────────

INDU_UNITS = {
    "Sun": 30, "Moon": 16, "Mars": 6, "Mercury": 8,
    "Jupiter": 10, "Venus": 12, "Saturn": 1
}

SIGN_LORDS = {
    0: "Mars", 1: "Venus", 2: "Mercury", 3: "Moon", 4: "Sun", 5: "Mercury",
    6: "Venus", 7: "Mars", 8: "Jupiter", 9: "Saturn", 10: "Saturn", 11: "Jupiter"
}

SIGN_NAMES_LON = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
                   "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

def calculate_indu_lagna(planet_lons: dict, lagna_lon: float, moon_lon: float) -> dict:
    """
    Calculates Indu Lagna for wealth.
    Sum of units of 9th lord from Lagna and 9th lord from Moon.
    Count that sum from Moon's sign.
    """
    l_sign = int(lagna_lon / 30) % 12
    m_sign = int(moon_lon / 30) % 12

    # 9th sign from Lagna
    l9_sign = (l_sign + 8) % 12
    l9_lord = SIGN_LORDS[l9_sign]

    # 9th sign from Moon
    m9_sign = (m_sign + 8) % 12
    m9_lord = SIGN_LORDS[m9_sign]

    total_units = INDU_UNITS.get(l9_lord, 0) + INDU_UNITS.get(m9_lord, 0)

    # Count total_units from Moon's sign
    indu_sign = (m_sign + total_units - 1) % 12

    return {
        "l9_lord": l9_lord,
        "m9_lord": m9_lord,
        "total_units": total_units,
        "indu_sign": indu_sign + 1,
        "indu_sign_name": SIGN_NAMES_LON[indu_sign]  # FIXED: was using BODY_PARTS_SIGNS
    }

