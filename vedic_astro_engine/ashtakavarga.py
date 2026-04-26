"""
ashtakavarga.py - Complete Ashtakavarga System

Implements Bhinnashtakavarga (BAV), Sarvashtakavarga (SAV), and provides
analysis tools - all based on Brihat Parasara Hora Shastra (BPHS) tables.

BPHS Bindu Tables:
Each table row = which houses (1-indexed from the contributor's sign) give bindus.
All 8 contributors: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Ascendant.
"""

# -----------------------------------------------------------------------------
# BPHS Bindu Tables (Parasara's standard rules, 1-indexed house offsets)
# Each set is the list of house-offsets (from 1) where 1 = bindu granted
# The table is indexed as: BPHS_TABLES[planet_receiving][contributor]
# Each contributor grants a bindu if the target sign is [offset] houses away
# from the contributor's own sign.
# -----------------------------------------------------------------------------

# Houses counted from contributor's natal sign position (1-based)
BPHS_OFFSETS = {
    "Sun": {
        "Sun":      [1, 2, 4, 7, 8, 9, 10, 11],
        "Moon":     [3, 6, 10, 11],
        "Mars":     [1, 2, 4, 7, 8, 9, 10, 11],
        "Mercury":  [3, 5, 6, 9, 10, 11, 12],
        "Jupiter":  [5, 6, 9, 11],
        "Venus":    [6, 7, 12],
        "Saturn":   [1, 2, 4, 7, 8, 9, 10, 11],
        "Asc":      [3, 4, 6, 10, 11, 12],
    },
    "Moon": {
        "Sun":      [3, 6, 7, 8, 10, 11],
        "Moon":     [1, 3, 6, 7, 10, 11],
        "Mars":     [2, 3, 5, 6, 9, 10, 11],
        "Mercury":  [1, 3, 4, 5, 7, 8, 10, 11],
        "Jupiter":  [1, 4, 7, 8, 10, 11, 12],
        "Venus":    [3, 4, 5, 7, 9, 10, 11],
        "Saturn":   [3, 5, 6, 11],
        "Asc":      [3, 6, 10, 11],
    },
    "Mars": {
        "Sun":      [3, 5, 6, 10, 11],
        "Moon":     [3, 6, 11],
        "Mars":     [1, 2, 4, 7, 8, 10, 11],
        "Mercury":  [3, 5, 6, 11],
        "Jupiter":  [6, 10, 11, 12],
        "Venus":    [6, 8, 11, 12],
        "Saturn":   [1, 4, 7, 8, 9, 10, 11],
        "Asc":      [1, 3, 6, 10, 11],
    },
    "Mercury": {
        "Sun":      [5, 6, 9, 11, 12],
        "Moon":     [2, 4, 6, 8, 10, 11],
        "Mars":     [1, 2, 4, 7, 8, 9, 10, 11],
        "Mercury":  [1, 3, 5, 6, 9, 10, 11, 12],
        "Jupiter":  [6, 8, 11, 12],
        "Venus":    [1, 2, 3, 4, 5, 8, 9, 11],
        "Saturn":   [1, 2, 4, 7, 8, 9, 10, 11],
        "Asc":      [1, 2, 4, 6, 8, 10, 11],
    },
    "Jupiter": {
        "Sun":      [1, 2, 3, 4, 7, 8, 9, 10, 11],
        "Moon":     [2, 5, 7, 9, 11],
        "Mars":     [1, 2, 4, 7, 8, 10, 11],
        "Mercury":  [1, 2, 4, 5, 6, 9, 10, 11],
        "Jupiter":  [1, 2, 3, 4, 7, 8, 10, 11],
        "Venus":    [2, 5, 6, 9, 10, 11],
        "Saturn":   [3, 5, 6, 12],
        "Asc":      [1, 2, 4, 5, 6, 9, 10, 11],
    },
    "Venus": {
        "Sun":      [8, 11, 12],
        "Moon":     [1, 2, 3, 4, 5, 8, 9, 11, 12],
        "Mars":     [3, 4, 6, 9, 11, 12],
        "Mercury":  [3, 5, 6, 9, 11],
        "Jupiter":  [5, 8, 9, 10, 11],
        "Venus":    [1, 2, 3, 4, 5, 8, 9, 10, 11],
        "Saturn":   [3, 4, 5, 8, 9, 10, 11],
        "Asc":      [1, 2, 3, 4, 5, 8, 9, 11],
    },
    "Saturn": {
        "Sun":      [1, 2, 4, 7, 8, 10, 11],
        "Moon":     [3, 6, 11],
        "Mars":     [3, 5, 6, 10, 11, 12],
        "Mercury":  [6, 8, 9, 10, 11, 12],
        "Jupiter":  [5, 6, 11, 12],
        "Venus":    [6, 11, 12],
        "Saturn":   [3, 5, 6, 11],
        "Asc":      [1, 3, 4, 6, 10, 11],
    },
}

PLANETS_7 = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
SIGN_NAMES = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
              "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

# Natural (maximum possible) bindus per planet - from BPHS
# Verified: Sun=48, Moon=49, Mars=39, Mercury=54, Jupiter=55, Venus=52, Saturn=39
BPHS_NATURAL_TOTALS = {
    "Sun": 48, "Moon": 49, "Mars": 39,
    "Mercury": 54, "Jupiter": 55, "Venus": 52, "Saturn": 39
}


def _build_bindu_row(planet_name, contributor_signs):
    """
    Compute a planet's BAV row (12 bindus, one per sign 0-11)
    by applying BPHS offset rules for all contributors.
    """
    row = [0] * 12
    table = BPHS_OFFSETS.get(planet_name, {})
    for contributor, offsets in table.items():
        base = contributor_signs.get(contributor)
        if base is None:
            continue
        for h in offsets:                        # h is 1-indexed
            target = (base + h - 1) % 12        # convert to 0-indexed sign
            row[target] += 1
    return row


def calculate_ashtakavarga(planet_longitudes: dict, asc_longitude: float) -> dict:
    """
    Full Ashtakavarga calculation.

    Parameters
    ----------
    planet_longitudes : dict
        Keys: 'Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn'
        Values: sidereal longitude in degrees (0-360)
    asc_longitude : float
        Sidereal Ascendant longitude in degrees (0-360)

    Returns
    -------
    dict with keys:
        bhinnashtakavarga  : { planet: [12 bindus per sign] }
        sarvashtakavarga   : [12 totals, one per sign]
        analysis           : per-planet + total analysis with named-sign breakdown
    """
    # Build contributor sign index (0-11)
    contrib_signs = {}
    for p in PLANETS_7:
        if p in planet_longitudes:
            contrib_signs[p] = int(planet_longitudes[p] / 30.0) % 12
    contrib_signs["Asc"] = int(asc_longitude / 30.0) % 12

    # --- Bhinnashtakavarga (BAV) ---
    bav = {}
    for planet in PLANETS_7:
        bav[planet] = _build_bindu_row(planet, contrib_signs)

    # --- Sarvashtakavarga (SAV) = column-wise sum of all 7 BAVs ---
    sav = [sum(bav[p][s] for p in PLANETS_7) for s in range(12)]

    # --- Analysis helpers ---
    def _sign_breakdown(row):
        return {SIGN_NAMES[i]: row[i] for i in range(12)}

    def _planet_sign(p):
        """Return the sign (0-11) the planet occupies."""
        return contrib_signs.get(p, 0)

    def _natal_house_score(row, planet):
        """Bindus in the sign where the planet is placed."""
        return row[_planet_sign(planet)]

    def _strength_label(score, planet):
        # Use correct BPHS natural totals (not 8)
        max_score = BPHS_NATURAL_TOTALS.get(planet, 48)
        # Average per sign
        avg = max_score / 12.0
        if score > avg * 1.25:   return "Strong"
        if score >= avg * 0.75:  return "Moderate"
        return "Weak"

    # BAV max per planet = number of contributors (8) → but actual max varies
    # SAV max per sign = sum of individual maxes (varies); use 48 as reference
    analysis = {}
    for planet in PLANETS_7:
        row = bav[planet]
        total_bindus = sum(row)
        natal_bindus = _natal_house_score(row, planet)
        analysis[planet] = {
            "total_bindus": total_bindus,
            "natural_max": BPHS_NATURAL_TOTALS.get(planet, 48),
            "bindus_in_natal_sign": natal_bindus,
            "strength": _strength_label(natal_bindus, planet),
            "signs": _sign_breakdown(row),
            # Signs with >=4 bindus are "benefic" for transits
            "transit_benefic_signs": [SIGN_NAMES[i] for i in range(12) if row[i] >= 4],
            "transit_malefic_signs": [SIGN_NAMES[i] for i in range(12) if row[i] <= 2],
        }

    sav_total = sum(sav)
    analysis["Sarvashtakavarga"] = {
        "total_bindus": sav_total,
        "signs": _sign_breakdown(sav),
        "strongest_sign": SIGN_NAMES[sav.index(max(sav))],
        "weakest_sign": SIGN_NAMES[sav.index(min(sav))],
        # Kaksha reduction: signs with < 25 SAV bindus are "inauspicious zones"
        "inauspicious_zones": [SIGN_NAMES[i] for i in range(12) if sav[i] < 25],
        "auspicious_zones": [SIGN_NAMES[i] for i in range(12) if sav[i] >= 30],
    }

    return {
        "bhinnashtakavarga": bav,
        "sarvashtakavarga": sav,
        "analysis": analysis,
    }
