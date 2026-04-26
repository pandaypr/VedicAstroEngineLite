"""
aspects.py - Graha Drishti (Planetary Aspects)

All 7 planets have 7th house full aspect.
Special additional aspects (full strength):
  Mars:    4th and 8th house
  Jupiter: 5th and 9th house
  Saturn:  3rd and 10th house
  Rahu/Ketu: 5th and 9th (same as Jupiter, per standard Parasara rules)

Aspect strength (Drishti Bala):
  Full  = 1.0  (7th for all; special aspects)
  3/4   = 0.75 (not used in classical — but included for Tajika if needed)
  We use only full/none per BPHS.
"""

FULL_ASPECT_HOUSES = {
    "Sun":     [7],
    "Moon":    [7],
    "Mars":    [4, 7, 8],
    "Mercury": [7],
    "Jupiter": [5, 7, 9],
    "Venus":   [7],
    "Saturn":  [3, 7, 10],
    "Rahu":    [5, 7, 9],
    "Ketu":    [5, 7, 9],
}

SIGN_NAMES = [
    "Aries","Taurus","Gemini","Cancer","Leo","Virgo",
    "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"
]


def calculate_aspects(planet_longitudes: dict) -> dict:
    """
    Calculate all Graha Drishti (aspects) for the chart.

    Returns
    -------
    dict
        "aspected_by": { sign_name: [list of aspecting planets] }
        "planet_aspects": { planet: { "aspecting_signs": [...], "aspecting_planets": [...] } }
        "mutual_aspects": [ {planet_a, planet_b, house_diff} ]
    """
    # Map each planet to its 0-indexed sign
    planet_sign = {}
    for name, lon in planet_longitudes.items():
        planet_sign[name] = int(lon / 30.0) % 12

    # Build aspected_by: which planets aspect each sign
    aspected_by = {s: [] for s in SIGN_NAMES}

    planet_aspects = {}
    for planet, p_sign in planet_sign.items():
        houses = FULL_ASPECT_HOUSES.get(planet, [7])
        aspected_signs = []
        for h in houses:
            target = (p_sign + h - 1) % 12
            aspected_by[SIGN_NAMES[target]].append(planet)
            aspected_signs.append(SIGN_NAMES[target])

        # What planets are in those aspected signs?
        aspecting_planets = []
        for a_sign in aspected_signs:
            for other, o_sign_idx in planet_sign.items():
                if other != planet and SIGN_NAMES[o_sign_idx] == a_sign:
                    aspecting_planets.append(other)

        planet_aspects[planet] = {
            "aspecting_signs": aspected_signs,
            "aspecting_planets": aspecting_planets,
        }

    # Mutual aspects: A aspects B AND B aspects A
    mutual = []
    planets = list(planet_sign.keys())
    for i in range(len(planets)):
        for j in range(i + 1, len(planets)):
            a, b = planets[i], planets[j]
            a_asp = planet_aspects[a]["aspecting_planets"]
            b_asp = planet_aspects[b]["aspecting_planets"]
            if b in a_asp and a in b_asp:
                diff = abs(planet_sign[a] - planet_sign[b])
                if diff > 6:
                    diff = 12 - diff
                mutual.append({"planet_a": a, "planet_b": b, "sign_diff": diff})

    return {
        "aspected_by": aspected_by,
        "planet_aspects": planet_aspects,
        "mutual_aspects": mutual,
    }
