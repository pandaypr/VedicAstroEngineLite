"""
avasthas.py - Planetary States (Avasthas)

Two classical systems:

TYPE 1 — Shayana-Adi Avasthas (12 states)
  Based on degree within the sign (odd/even sign matters) and planet nature.
  Each planet is in exactly one of the 12 states at birth.
  Source: Prasna Marga / Jataka Parijata

TYPE 2 — Baala-Adi Avasthas (5 age states)
  Based on degree within the sign (each 6-degree span = one state).
  Different for odd and even signs.
  Source: BPHS Chapter 45
"""

SIGN_ODD = {1, 3, 5, 7, 9, 11}  # Aries=1, Gemini=3... (1-indexed)

# TYPE 1 — 12 Shayana-Adi Avasthas
# The state is determined by (degree_in_sign / 2.5) → integer → one of 12 states
# Each 2.5 degrees of a 30-degree sign = one state (30/12 = 2.5 deg each)
SHAYANA_ADI = [
    "Shayana",       # Sleeping (0-2.5°)   — weak, lazy results
    "Upaveshana",    # Sitting  (2.5-5°)   — moderate
    "Netrapani",     # Hand-on-eye (5-7.5°) — troubled, secretive
    "Prakashana",    # Shining  (7.5-10°)  — good, visible
    "Gamanechcha",   # Desire to move (10-12.5°) — restless
    "Gamana",        # Moving (12.5-15°)   — active, traveling
    "Sabhavasa",     # Assembly (15-17.5°) — social, prosperous
    "Agama",         # Arriving (17.5-20°) — improvement
    "Bhojana",       # Eating (20-22.5°)   — enjoying life
    "Nrityalipsa",   # Desire to dance (22.5-25°) — artistic
    "Kautuka",       # Curious (25-27.5°)  — enthusiastic
    "Nidra",         # Sleeping deeply (27.5-30°) — dormant
]

# TYPE 2 — 5 Baala-Adi Avasthas (6 degrees each = 5 states per sign)
# For ODD signs: Baala→Kumara→Yuva→Vriddha→Mrita (0→6→12→18→24→30)
# For EVEN signs: Mrita→Vriddha→Yuva→Kumara→Baala (reversed)
BAALA_ADI_ODD  = ["Baala", "Kumara", "Yuva", "Vriddha", "Mrita"]
BAALA_ADI_EVEN = ["Mrita", "Vriddha", "Yuva", "Kumara", "Baala"]

# Interpretation lookup
BAALA_EFFECTS = {
    "Baala":   {"strength": 25,  "description": "Infant — 25% strength, weak, inexperienced"},
    "Kumara":  {"strength": 50,  "description": "Youth — 50% strength, growing power"},
    "Yuva":    {"strength": 100, "description": "Adult — Full strength, gives full results"},
    "Vriddha": {"strength": 25,  "description": "Old — declining, gives past-tense results"},
    "Mrita":   {"strength": 0,   "description": "Dead — negligible results, dormant"},
}

SHAYANA_EFFECTS = {
    "Shayana":      "Sleeping — weak, dormant results; person sleeps or rests excessively",
    "Upaveshana":   "Sitting — moderate ease; sedentary lifestyle",
    "Netrapani":    "Hand on eye — anxious, troubled; eye-related issues",
    "Prakashana":   "Shining — prominent, visible, good results",
    "Gamanechcha":  "Desire to move — restless, wants travel or change",
    "Gamana":       "Moving — active, traveling; results come through movement",
    "Sabhavasa":    "In assembly — social, honorable, group leadership",
    "Agama":        "Arriving — improving fortunes, prosperity ahead",
    "Bhojana":      "Eating/Enjoying — material comforts, sensual pleasures",
    "Nrityalipsa":  "Desire to dance — artistic, creative, performative",
    "Kautuka":      "Curious/Eager — enthusiastic, inventive, exploratory",
    "Nidra":        "Deep sleep — very dormant; results severely delayed or absent",
}


def get_avasthas(planet_name: str, longitude: float) -> dict:
    """
    Calculates both Avastha systems for a planet.

    Parameters
    ----------
    planet_name : str  (not used currently but kept for future odd/even planet rules)
    longitude : float  Sidereal longitude 0-360

    Returns
    -------
    dict with 'shayana_adi' and 'baala_adi' entries
    """
    sign_idx  = int(longitude / 30.0) % 12   # 0-indexed
    sign_num  = sign_idx + 1                  # 1-indexed
    deg_in    = longitude % 30.0

    # --- TYPE 1: Shayana-Adi ---
    state_idx  = int(deg_in / 2.5)
    state_idx  = min(state_idx, 11)           # clamp for exactly 30.0°
    shayana    = SHAYANA_ADI[state_idx]

    # --- TYPE 2: Baala-Adi ---
    segment    = int(deg_in / 6.0)
    segment    = min(segment, 4)
    if sign_num in SIGN_ODD:
        baala  = BAALA_ADI_ODD[segment]
    else:
        baala  = BAALA_ADI_EVEN[segment]

    return {
        "shayana_adi": {
            "state": shayana,
            "degree_range": f"{round(state_idx * 2.5, 1)}-{round((state_idx + 1) * 2.5, 1)}",
            "effect": SHAYANA_EFFECTS.get(shayana, ""),
        },
        "baala_adi": {
            "state": baala,
            "strength_percent": BAALA_EFFECTS[baala]["strength"],
            "description": BAALA_EFFECTS[baala]["description"],
        },
    }


def calculate_all_avasthas(planet_longitudes: dict) -> dict:
    """Returns Avastha data for all planets."""
    return {p: get_avasthas(p, lon) for p, lon in planet_longitudes.items()}
