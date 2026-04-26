"""
yogas.py - Comprehensive Yoga Detection

Implements:
  1. Nabhasa Yogas (Planetary pattern yogas)
  2. Raja Yogas (Power/authority combinations)
  3. Daridra Yogas (Poverty combinations)
  4. Dhana Yogas (Wealth combinations)
  5. Parivartana Yogas (Mutual exchange)
  6. Chandra Yogas (Moon-based)

Source: Brihat Parasara Hora Shastra, Phala Deepika, Saravali
"""

SIGN_NAMES = [
    "Aries","Taurus","Gemini","Cancer","Leo","Virgo",
    "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"
]

# Sign lords (1-indexed)
SIGN_LORDS = {
    1:"Mars",2:"Venus",3:"Mercury",4:"Moon",5:"Sun",6:"Mercury",
    7:"Venus",8:"Mars",9:"Jupiter",10:"Saturn",11:"Saturn",12:"Jupiter"
}

# Kendra houses
KENDRA = {1, 4, 7, 10}
# Trikona houses
TRIKONA = {1, 5, 9}
# Trik / Dusthana houses
DUSTHANA = {6, 8, 12}

NATURAL_BENEFICS = {"Jupiter", "Venus", "Moon", "Mercury"}
NATURAL_MALEFICS = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}


def _house_of(lon: float, asc_lon: float) -> int:
    """Return house number (1-12) for a longitude given ascendant longitude."""
    diff = (lon - asc_lon) % 360.0
    return int(diff / 30.0) + 1


def _sign(lon: float) -> int:
    """Return 1-indexed sign number."""
    return int(lon / 30.0) % 12 + 1


def _sign0(lon: float) -> int:
    """Return 0-indexed sign number."""
    return int(lon / 30.0) % 12


# ─────────────────────────────────────────────────────────────────────────────
# NABHASA YOGAS
# ─────────────────────────────────────────────────────────────────────────────

def detect_nabhasa_yogas(planet_longitudes: dict) -> list:
    """
    Detect Nabhasa (Celestial Pattern) Yogas.
    These are based on the distribution of planets across signs/houses.
    """
    yogas = []
    # Use 7 classical planets only
    SEVEN = ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]
    lons = {p: planet_longitudes[p] for p in SEVEN if p in planet_longitudes}
    signs = sorted(set(_sign0(l) for l in lons.values()))
    n_signs = len(signs)

    # Sankhya (count-based) yogas — n_signs = number of OCCUPIED signs (1-7)
    # BPHS: Gola = all 7 planets in 1 sign (n_signs=1)
    #        Yuga = 7 planets in 2 signs (n_signs=2) ... Veena = all in 7 signs (n_signs=7)
    if n_signs == 1:
        yogas.append({"yoga": "Gola",    "type": "Nabhasa", "description": "All 7 planets in 1 sign — extraordinary, extreme life"})
    elif n_signs == 2:
        yogas.append({"yoga": "Yuga",    "type": "Nabhasa", "description": "Planets in 2 signs — polarized, intense duality"})
    elif n_signs == 3:
        yogas.append({"yoga": "Shoola",  "type": "Nabhasa", "description": "Planets in 3 signs — dynamic, focused force"})
    elif n_signs == 4:
        yogas.append({"yoga": "Kedara",  "type": "Nabhasa", "description": "Planets in 4 signs — agricultural, steady growth"})
    elif n_signs == 5:
        yogas.append({"yoga": "Pasha",   "type": "Nabhasa", "description": "Planets in 5 signs — bound/constrained; many entanglements"})
    elif n_signs == 6:
        yogas.append({"yoga": "Dama",    "type": "Nabhasa", "description": "Planets in 6 signs — generous but scattered energy"})
    elif n_signs == 7:
        yogas.append({"yoga": "Veena",   "type": "Nabhasa", "description": "Planets in 7 different signs — musical, artistic, balanced life"})

    # Aakruti (shape) yogas — check sign groupings
    sign_list = [_sign0(l) for l in lons.values()]

    # Rajju: all in movable signs (0,3,6,9)
    movable = {0, 3, 6, 9}
    fixed   = {1, 4, 7, 10}
    dual    = {2, 5, 8, 11}

    all_movable = all(s in movable for s in sign_list)
    all_fixed   = all(s in fixed   for s in sign_list)
    all_dual    = all(s in dual    for s in sign_list)

    if all_movable:
        yogas.append({"yoga": "Rajju",  "type": "Nabhasa-Aakruti", "description": "All in movable signs — frequent travel, no fixed abode"})
    elif all_fixed:
        yogas.append({"yoga": "Musala", "type": "Nabhasa-Aakruti", "description": "All in fixed signs — firm, stubborn, dignified nature"})
    elif all_dual:
        yogas.append({"yoga": "Nala",   "type": "Nabhasa-Aakruti", "description": "All in dual signs — clever, skilled, versatile"})

    # Mala: all in trines (signs 1,5,9 = 0,4,8)
    trine_signs = {0, 4, 8}
    if all(s in trine_signs for s in sign_list):
        yogas.append({"yoga": "Mala",  "type": "Nabhasa-Aakruti", "description": "All in trine signs — fortunate, prosperous, Lakshmipati"})

    # Sarpa: all in even (water/earth) signs
    if all(s % 2 == 1 for s in sign_list):
        yogas.append({"yoga": "Sarpa", "type": "Nabhasa-Aakruti", "description": "All in even signs — serpentine nature, cunning but troubled"})

    return yogas


# ─────────────────────────────────────────────────────────────────────────────
# RAJA & DARIDRA YOGAS
# ─────────────────────────────────────────────────────────────────────────────

def detect_raja_yogas(planet_longitudes: dict, asc_lon: float) -> list:
    """
    Detect Raja Yogas — combinations of Kendra and Trikona lords.
    Classic rule: A Kendra lord + Trikona lord in conjunction/mutual aspect = Raja Yoga.
    """
    yogas = []
    asc_sign = _sign(asc_lon)  # 1-indexed

    def house_lord(house_num):
        sign_num = (asc_sign + house_num - 2) % 12 + 1
        return SIGN_LORDS[sign_num]

    kendra_lords  = {house_lord(h) for h in KENDRA}
    trikona_lords = {house_lord(h) for h in TRIKONA}

    # Yoga 1: Kendra lord + Trikona lord conjunct
    planets_by_sign = {}
    for p, lon in planet_longitudes.items():
        s = _sign0(lon)
        planets_by_sign.setdefault(s, []).append(p)

    for sign_planets in planets_by_sign.values():
        set_p = set(sign_planets)
        for kl in kendra_lords:
            for tl in trikona_lords:
                if kl != tl and kl in set_p and tl in set_p:
                    yogas.append({
                        "yoga": "Raja Yoga",
                        "type": "Raja",
                        "planets": [kl, tl],
                        "description": f"{kl} (Kendra lord) conjunct {tl} (Trikona lord) — power, authority, recognition"
                    })

    # Yoga 2: Lagna lord in Kendra or Trikona
    lagna_lord = house_lord(1)
    if lagna_lord in planet_longitudes:
        ll_house = _house_of(planet_longitudes[lagna_lord], asc_lon)
        if ll_house in KENDRA | TRIKONA:
            yogas.append({
                "yoga": "Lagna Lord in Kendra/Trikona",
                "type": "Raja",
                "planets": [lagna_lord],
                "description": f"Lagna lord {lagna_lord} in house {ll_house} — strong self, leadership ability"
            })

    # Yoga 3: 5th and 9th lord conjunct
    lord5 = house_lord(5)
    lord9 = house_lord(9)
    if lord5 in planet_longitudes and lord9 in planet_longitudes:
        if _sign0(planet_longitudes[lord5]) == _sign0(planet_longitudes[lord9]):
            yogas.append({
                "yoga": "Dharma-Karma Adhipati Raja Yoga",
                "type": "Raja",
                "planets": [lord5, lord9],
                "description": f"5th lord {lord5} conjunct 9th lord {lord9} — highest Raja Yoga, fortune + intellect"
            })

    return yogas


def detect_daridra_yogas(planet_longitudes: dict, asc_lon: float) -> list:
    """
    Detect Daridra (Poverty) Yogas.
    """
    yogas = []
    asc_sign = _sign(asc_lon)

    def house_lord(house_num):
        sign_num = (asc_sign + house_num - 2) % 12 + 1
        return SIGN_LORDS[sign_num]

    def planet_house(p):
        if p not in planet_longitudes:
            return None
        return _house_of(planet_longitudes[p], asc_lon)

    # Lagna lord in Dusthana
    ll = house_lord(1)
    if ll in planet_longitudes:
        h = planet_house(ll)
        if h in DUSTHANA:
            yogas.append({
                "yoga": "Lagna Lord in Dusthana",
                "type": "Daridra",
                "planets": [ll],
                "description": f"Lagna lord {ll} in house {h} — health challenges, self-undoing tendencies"
            })

    # 2nd lord in 12th or 8th
    lord2 = house_lord(2)
    if lord2 in planet_longitudes:
        h = planet_house(lord2)
        if h in {8, 12}:
            yogas.append({
                "yoga": "2nd Lord in 8th/12th",
                "type": "Daridra",
                "planets": [lord2],
                "description": f"2nd lord {lord2} in house {h} — financial losses, wealth dissipation"
            })

    # Saturn in 1st aspecting Moon
    if "Saturn" in planet_longitudes and "Moon" in planet_longitudes:
        sat_h = planet_house("Saturn")
        moon_h = planet_house("Moon")
        if sat_h == 1 and moon_h == 7:
            yogas.append({
                "yoga": "Daridra Yoga (Sat-Moon)",
                "type": "Daridra",
                "planets": ["Saturn", "Moon"],
                "description": "Saturn in 1st aspecting Moon in 7th — emotional and financial hardship"
            })

    return yogas


# ─────────────────────────────────────────────────────────────────────────────
# MARAKA GRAHAS
# ─────────────────────────────────────────────────────────────────────────────

def detect_marakas(planet_longitudes: dict, asc_lon: float) -> dict:
    """
    Determine Maraka (Death-inflicting) planets.
    Primary Marakas: Lords of 2nd and 7th houses.
    Secondary Marakas: Planets in 2nd or 7th, or associated with their lords.
    """
    asc_sign = _sign(asc_lon)

    def house_lord(h):
        return SIGN_LORDS[(asc_sign + h - 2) % 12 + 1]

    lord2 = house_lord(2)
    lord7 = house_lord(7)

    # Planets in 2nd and 7th houses
    in_2nd = [p for p, lon in planet_longitudes.items()
               if _house_of(lon, asc_lon) == 2]
    in_7th = [p for p, lon in planet_longitudes.items()
               if _house_of(lon, asc_lon) == 7]

    primary   = list({lord2, lord7})
    secondary = list(set(in_2nd + in_7th) - set(primary))

    # Saturn as universal maraka (if not already primary)
    # Per BPHS, Saturn is always a potential maraka
    additional = []
    if "Saturn" not in primary and "Saturn" not in secondary:
        additional.append("Saturn")

    return {
        "primary_marakas":   primary,
        "secondary_marakas": secondary,
        "additional":        additional,
        "explanation": (
            f"2nd lord ({lord2}) and 7th lord ({lord7}) are primary Marakas. "
            f"Their Dashas, especially Antardasha of Saturn, can trigger health crises."
        )
    }


# ─────────────────────────────────────────────────────────────────────────────
# ISHTA & KASHTA PHALA
# ─────────────────────────────────────────────────────────────────────────────

# BPHS formula for Cheshta Bala (speed-based)
# Uccha Bala = how close to exaltation
# Ishta Phala = sqrt(Uccha_Bala × Cheshta_Bala)
# Kashta Phala = sqrt((60-Uccha_Bala) × (60-Cheshta_Bala))

UCCHA_LONG = {
    "Sun":60.0,"Moon":33.0,"Mars":298.0,"Mercury":165.0,
    "Jupiter":95.0,"Venus":357.0,"Saturn":200.0
}

def calculate_ishta_kashta(planet_name: str, longitude: float,
                            speed_deg_day: float) -> dict:
    """
    Ishta Phala = √(Uchcha_Bala × Cheshta_Bala)
    Kashta Phala = √((60−Uchcha_Bala) × (60−Cheshta_Bala))

    speed_deg_day: daily motion of the planet (negative = retrograde)
    """
    import math
    uccha_long = UCCHA_LONG.get(planet_name)
    if uccha_long is None:
        return {}

    # Uchcha Bala (0-60 virupas)
    dist = abs(longitude - uccha_long) % 360
    if dist > 180:
        dist = 360 - dist
    uccha_bala = 60.0 * (1.0 - dist / 180.0)

    # Cheshta Bala (0-60 virupas) — based on speed relative to mean
    # Mean speeds (deg/day)
    MEAN_SPEED = {
        "Sun":0.9856,"Moon":13.176,"Mars":0.5240,
        "Mercury":1.383,"Jupiter":0.0830,"Venus":1.200,"Saturn":0.0330
    }
    mean = MEAN_SPEED.get(planet_name, 1.0)
    is_retro = speed_deg_day < 0
    if is_retro:
        cheshta_bala = 60.0
    else:
        ratio = abs(speed_deg_day) / mean if mean != 0 else 1.0
        cheshta_bala = min(60.0, 60.0 * ratio)

    ishta  = round(math.sqrt(uccha_bala * cheshta_bala), 3)
    kashta = round(math.sqrt((60 - uccha_bala) * (60 - cheshta_bala)), 3)

    return {
        "uccha_bala":   round(uccha_bala, 3),
        "cheshta_bala": round(cheshta_bala, 3),
        "ishta_phala":  ishta,
        "kashta_phala": kashta,
        "net_balance":  round(ishta - kashta, 3),
        "dominant":     "Benefic" if ishta > kashta else "Malefic"
    }


# ─────────────────────────────────────────────────────────────────────────────
# JAIMINI KARAKAS
# ─────────────────────────────────────────────────────────────────────────────

# Exaltation signs (1-indexed) for each planet
EXALTATION_SIGN = {
    "Sun": 1, "Moon": 2, "Mars": 10, "Mercury": 6,
    "Jupiter": 4, "Venus": 12, "Saturn": 7
}

# Own signs (1-indexed) for each planet
OWN_SIGNS = {
    "Sun":     [5],
    "Moon":    [4],
    "Mars":    [1, 8],
    "Mercury": [3, 6],
    "Jupiter": [9, 12],
    "Venus":   [2, 7],
    "Saturn":  [10, 11],
}


def calculate_jaimini_karakas(planet_longitudes: dict) -> dict:
    """
    Jaimini Chara Karakas — planets ranked by their degree within the sign
    (highest degree = Atma Karaka, 2nd highest = Amatya Karaka, etc.)

    Rahu and Ketu are excluded. Rahu uses reverse count in some traditions,
    but here we follow the simpler 7-karaka system (excluding Rahu).

    Returns dict with AK, AmK, BK, MK, PuK, GK, DK planet names.
    """
    KARAKA_NAMES = ["AK", "AmK", "BK", "MK", "PuK", "GK", "DK"]
    KARAKA_FULL  = [
        "Atma Karaka",     "Amatya Karaka", "Bhratru Karaka",
        "Matru Karaka",    "Putra Karaka",  "Gnati Karaka",
        "Dara Karaka"
    ]
    SEVEN = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    candidates = {p: planet_longitudes[p] for p in SEVEN if p in planet_longitudes}

    # Degree within sign (0-30) — higher = stronger karaka
    def deg_in_sign(lon):
        return lon % 30.0

    sorted_planets = sorted(candidates.items(), key=lambda x: deg_in_sign(x[1]), reverse=True)

    karakas = {}
    for i, (planet, lon) in enumerate(sorted_planets):
        if i < len(KARAKA_NAMES):
            karakas[KARAKA_NAMES[i]] = {
                "planet":      planet,
                "full_name":   KARAKA_FULL[i],
                "longitude":   round(lon, 4),
                "deg_in_sign": round(deg_in_sign(lon), 4),
            }
    return karakas


# ─────────────────────────────────────────────────────────────────────────────
# RAJA SAMBANDHA (Jaimini-based)
# ─────────────────────────────────────────────────────────────────────────────

def detect_raja_sambandha(planet_longitudes: dict, asc_lon: float,
                           karakas: dict) -> list:
    """
    Raja Sambandha Yogas — Jaimini-based combinations of Atma Karaka (AK)
    and Amatya Karaka (AmK).

    Rules:
    1. AmK in own sign or exaltation sign → strong minister/advisor
    2. AmK in kendra or trikona from AK → intelligence + authority
    3. Sun + AK in kendra/trikona → royal connection
    """
    yogas = []
    if "AK" not in karakas or "AmK" not in karakas:
        return yogas

    ak_planet  = karakas["AK"]["planet"]
    amk_planet = karakas["AmK"]["planet"]

    if ak_planet not in planet_longitudes or amk_planet not in planet_longitudes:
        return yogas

    ak_lon  = planet_longitudes[ak_planet]
    amk_lon = planet_longitudes[amk_planet]
    amk_sign = _sign(amk_lon)  # 1-indexed

    # Rule 1: AmK in own sign
    if amk_sign in OWN_SIGNS.get(amk_planet, []):
        yogas.append({
            "yoga": "Raja Sambandha",
            "type": "Jaimini-Raja",
            "planets": [amk_planet],
            "description": (
                f"Amatya Karaka ({amk_planet}) in own sign {SIGN_NAMES[amk_sign-1]} "
                f"— an intelligent minister or advisor of high caliber"
            )
        })

    # Rule 2: AmK in exaltation sign
    if amk_sign == EXALTATION_SIGN.get(amk_planet):
        yogas.append({
            "yoga": "Raja Sambandha",
            "type": "Jaimini-Raja",
            "planets": [amk_planet],
            "description": (
                f"Amatya Karaka ({amk_planet}) exalted in {SIGN_NAMES[amk_sign-1]} "
                f"— top-level career excellence, trusted by authority"
            )
        })

    # Rule 3: AmK in kendra or trikona from AK
    ak_sign   = _sign(ak_lon)
    diff_signs = (amk_sign - ak_sign) % 12 + 1  # 1-indexed house from AK
    if diff_signs in KENDRA | TRIKONA:
        yogas.append({
            "yoga": "Raja Sambandha",
            "type": "Jaimini-Raja",
            "planets": [ak_planet, amk_planet],
            "description": (
                f"Amatya Karaka ({amk_planet}) in house {diff_signs} "
                f"from Atma Karaka ({ak_planet}) — associate liked by powerful people, "
                f"achieves high office through ability"
            )
        })

    # Rule 4: Atma Karaka + Sun in kendra/trikona from Lagna
    if "Sun" in planet_longitudes:
        sun_sign  = _sign(planet_longitudes["Sun"])
        ak_h_from_lagna = _house_of(ak_lon, asc_lon)
        sun_h_from_lagna = _house_of(planet_longitudes["Sun"], asc_lon)
        if ak_h_from_lagna in KENDRA | TRIKONA and sun_h_from_lagna in KENDRA | TRIKONA:
            yogas.append({
                "yoga": "Raja Sambandha",
                "type": "Jaimini-Raja",
                "planets": [ak_planet, "Sun"],
                "description": (
                    f"Atma Karaka ({ak_planet}) and Sun both in kendra/trikona "
                    f"— royal association, recognition from government/authority figures"
                )
            })

    return yogas


# ─────────────────────────────────────────────────────────────────────────────
# SURYA YOGAS (Sun-based Yogas)
# ─────────────────────────────────────────────────────────────────────────────

def detect_surya_yogas(planet_longitudes: dict) -> list:
    """
    Detects Vesi, Vasi, and Ubhayachara yogas — based on planets relative to Sun.

    Vesi   — planet(s) other than Moon in the 2nd from Sun
    Vasi   — planet(s) other than Moon in the 12th from Sun
    Ubhayachara — planets on BOTH sides of Sun (2nd AND 12th)

    Source: BPHS Chapter 35, Phala Deepika
    """
    yogas = []
    if "Sun" not in planet_longitudes:
        return yogas

    sun_sign = _sign0(planet_longitudes["Sun"])  # 0-indexed
    sign_2nd_from_sun  = (sun_sign + 1) % 12
    sign_12th_from_sun = (sun_sign - 1) % 12

    EXCLUDE = {"Sun", "Moon", "Rahu", "Ketu"}

    in_2nd  = [p for p, lon in planet_longitudes.items()
               if p not in EXCLUDE and _sign0(lon) == sign_2nd_from_sun]
    in_12th = [p for p, lon in planet_longitudes.items()
               if p not in EXCLUDE and _sign0(lon) == sign_12th_from_sun]

    if in_2nd and in_12th:
        yogas.append({
            "yoga": "Ubhayachara",
            "type": "Surya",
            "planets": in_2nd + in_12th,
            "description": (
                f"Planets in 2nd ({', '.join(in_2nd)}) AND 12th ({', '.join(in_12th)}) from Sun "
                f"— enjoys comforts, equal to a king, well-rounded personality"
            )
        })
    elif in_2nd:
        yogas.append({
            "yoga": "Vesi",
            "type": "Surya",
            "planets": in_2nd,
            "description": (
                f"{', '.join(in_2nd)} in 2nd from Sun — eloquent, prosperous, "
                f"industrious; benefits from career and worldly matters"
            )
        })
    elif in_12th:
        yogas.append({
            "yoga": "Vasi",
            "type": "Surya",
            "planets": in_12th,
            "description": (
                f"{', '.join(in_12th)} in 12th from Sun — comfort-loving, "
                f"virtuous, renowned for learning; spends on good causes"
            )
        })

    return yogas


# ─────────────────────────────────────────────────────────────────────────────
# CHANDRA YOGAS (Moon-based Yogas)
# ─────────────────────────────────────────────────────────────────────────────

def detect_chandra_yogas(planet_longitudes: dict, asc_lon: float) -> list:
    """
    Detects yogas based on planets relative to Moon:

    Sunaphaa  — planet(s) other than Sun in 2nd from Moon → intelligent, wealthy
    Anapha    — planet(s) other than Sun in 12th from Moon → virtuous, famous
    Durudhara — planets on BOTH sides of Moon → wealthy, generous
    Kemadruma — NO planets in 2nd/12th from Moon AND Moon not in kendra → poverty
    Adhi Yoga — benefics in 6th, 7th, AND 8th from Moon → king, minister, army chief
    Chandra-Adhi Yoga — benefics in 6th and 7th only (partial Adhi)

    Source: BPHS Chapter 36, Phala Deepika
    """
    yogas = []
    if "Moon" not in planet_longitudes:
        return yogas

    moon_sign = _sign0(planet_longitudes["Moon"])
    sign_2nd  = (moon_sign + 1) % 12
    sign_12th = (moon_sign - 1) % 12

    EXCL_SUN  = {"Sun", "Rahu", "Ketu"}

    in_2nd  = [p for p, lon in planet_longitudes.items()
               if p not in EXCL_SUN and p != "Moon" and _sign0(lon) == sign_2nd]
    in_12th = [p for p, lon in planet_longitudes.items()
               if p not in EXCL_SUN and p != "Moon" and _sign0(lon) == sign_12th]

    # Sunaphaa
    if in_2nd:
        yogas.append({
            "yoga": "Sunaphaa",
            "type": "Chandra",
            "planets": in_2nd,
            "description": (
                f"{', '.join(in_2nd)} in 2nd from Moon — intelligent, wealthy, "
                f"self-made, famous by own merit"
            )
        })

    # Anapha
    if in_12th:
        yogas.append({
            "yoga": "Anapha",
            "type": "Chandra",
            "planets": in_12th,
            "description": (
                f"{', '.join(in_12th)} in 12th from Moon — virtuous, healthy, "
                f"free from worries; renowned for spiritual qualities"
            )
        })

    # Durudhara
    if in_2nd and in_12th:
        yogas.append({
            "yoga": "Durudhara",
            "type": "Chandra",
            "planets": in_2nd + in_12th,
            "description": (
                f"Planets on both sides of Moon ({', '.join(in_2nd + in_12th)}) "
                f"— wealthy, generous, commands vehicles and armies"
            )
        })

    # Kemadruma — no planets in 2nd or 12th from Moon, AND Moon not in kendra
    moon_house = _house_of(planet_longitudes["Moon"], asc_lon)
    if not in_2nd and not in_12th and moon_house not in KENDRA:
        yogas.append({
            "yoga": "Kemadruma",
            "type": "Chandra-Dosha",
            "planets": ["Moon"],
            "description": (
                "Moon has no flanking planets and is not in kendra — "
                "poverty, solitude, mental instability; results reduced if cancelled by benefics"
            )
        })

    # Adhi Yoga — natural benefics (Ju, Ve, Me) in 6th, 7th, 8th from Moon
    sign_6  = (moon_sign + 5) % 12
    sign_7  = (moon_sign + 6) % 12
    sign_8  = (moon_sign + 7) % 12

    BENEFICS = {"Jupiter", "Venus", "Mercury"}
    in_6 = [p for p in BENEFICS if p in planet_longitudes and _sign0(planet_longitudes[p]) == sign_6]
    in_7 = [p for p in BENEFICS if p in planet_longitudes and _sign0(planet_longitudes[p]) == sign_7]
    in_8 = [p for p in BENEFICS if p in planet_longitudes and _sign0(planet_longitudes[p]) == sign_8]

    if in_6 and in_7 and in_8:
        all_benefics = in_6 + in_7 + in_8
        yogas.append({
            "yoga": "Adhi Yoga",
            "type": "Chandra",
            "planets": list(set(all_benefics)),
            "description": (
                f"Benefics in 6th ({', '.join(in_6)}), 7th ({', '.join(in_7)}), "
                f"8th ({', '.join(in_8)}) from Moon — becomes a king, minister, or army chief"
            )
        })
    elif (in_6 or in_7 or in_8) and (len([x for x in [in_6, in_7, in_8] if x]) >= 2):
        filled = [h for h, lst in [(6, in_6), (7, in_7), (8, in_8)] if lst]
        all_b = in_6 + in_7 + in_8
        yogas.append({
            "yoga": "Partial Adhi Yoga",
            "type": "Chandra",
            "planets": list(set(all_b)),
            "description": (
                f"Benefics in houses {filled} from Moon — minister or army chief qualities; "
                f"partial Adhi yoga (full requires all 3 houses occupied)"
            )
        })

    return yogas


# ─────────────────────────────────────────────────────────────────────────────
# COMBINATION YOGAS (Gaja-Kesari, Bheri, Parvata, Saraswati, etc.)
# ─────────────────────────────────────────────────────────────────────────────

def detect_combination_yogas(planet_longitudes: dict, asc_lon: float) -> list:
    """
    Detects multi-planet combination yogas:

    Gaja-Kesari — Jupiter in kendra from Moon → famous, virtuous, eloquent
    Bheri       — Venus, Mercury, Jupiter in 1st/2nd/12th + strong 9th lord
    Parvata     — Benefics in kendras, dusthanas empty (or with benefics only)
    Saraswati   — Venus, Mercury, Jupiter in own/exaltation/kendra → brilliance
    Hamsa       — Jupiter in own/exaltation sign in kendra
    Malavya     — Venus in own/exaltation sign in kendra
    Ruchaka     — Mars in own/exaltation sign in kendra
    Sasha       — Saturn in own/exaltation sign in kendra
    Bhadra      — Mercury in own/exaltation sign in kendra

    Source: BPHS (Pancha Mahapurusha Yogas), Phala Deepika
    """
    yogas = []

    def house_lord(house_num, asc_sign):
        sign_num = (asc_sign + house_num - 2) % 12 + 1
        return SIGN_LORDS[sign_num]

    asc_sign = _sign(asc_lon)

    # Gaja-Kesari Yoga
    if "Jupiter" in planet_longitudes and "Moon" in planet_longitudes:
        moon_sign = _sign0(planet_longitudes["Moon"])
        jup_sign  = _sign0(planet_longitudes["Jupiter"])
        diff = (jup_sign - moon_sign) % 12  # 0-indexed house offset
        # Kendra from Moon = 0,3,6,9 (i.e., houses 1,4,7,10)
        if diff in {0, 3, 6, 9}:
            yogas.append({
                "yoga": "Gaja-Kesari",
                "type": "Combination",
                "planets": ["Moon", "Jupiter"],
                "description": (
                    f"Jupiter in house {diff+1} from Moon (mutual kendra) — "
                    f"famous, virtuous, long-lived, overcomes enemies"
                )
            })

    # Pancha Mahapurusha Yogas
    # Planet must be in OWN sign or EXALTATION sign, AND in a kendra house from Lagna
    PANCHA = {
        "Mars":    ("Ruchaka",  [1, 8], 10),      # own: Ar/Sc, exalt: Cp
        "Mercury": ("Bhadra",   [3, 6], 6),        # own: Ge/Vi, exalt: Vi
        "Jupiter": ("Hamsa",    [9, 12], 4),        # own: Sg/Pi, exalt: Cn
        "Venus":   ("Malavya",  [2, 7], 12),        # own: Ta/Li, exalt: Pi
        "Saturn":  ("Sasha",    [10, 11], 7),       # own: Cp/Aq, exalt: Li
    }
    for planet, (yoga_name, own_list, exalt_sign) in PANCHA.items():
        if planet not in planet_longitudes:
            continue
        p_sign    = _sign(planet_longitudes[planet])   # 1-indexed
        p_house   = _house_of(planet_longitudes[planet], asc_lon)
        in_own    = p_sign in own_list
        in_exalt  = p_sign == exalt_sign
        in_kendra = p_house in KENDRA
        if (in_own or in_exalt) and in_kendra:
            status = "own sign" if in_own else "exaltation"
            yogas.append({
                "yoga": yoga_name,
                "type": "Pancha-Mahapurusha",
                "planets": [planet],
                "description": (
                    f"{planet} in {status} ({SIGN_NAMES[p_sign-1]}) in kendra (house {p_house}) "
                    f"— {yoga_name} Yoga: strong, distinguished, leader in its domain"
                )
            })

    # Saraswati Yoga — Jupiter, Venus, Mercury all in own/exalt/kendra/trikona
    jup_ok = mer_ok = ven_ok = False
    for planet in ["Jupiter", "Mercury", "Venus"]:
        if planet not in planet_longitudes:
            break
        p_sign  = _sign(planet_longitudes[planet])
        p_house = _house_of(planet_longitudes[planet], asc_lon)
        own_or_exalt = p_sign in OWN_SIGNS.get(planet, []) or p_sign == EXALTATION_SIGN.get(planet)
        strong = own_or_exalt or p_house in KENDRA | TRIKONA
        if planet == "Jupiter":   jup_ok = strong
        elif planet == "Mercury": mer_ok = strong
        elif planet == "Venus":   ven_ok = strong
    if jup_ok and mer_ok and ven_ok:
        yogas.append({
            "yoga": "Saraswati",
            "type": "Combination",
            "planets": ["Jupiter", "Mercury", "Venus"],
            "description": (
                "Jupiter, Mercury, and Venus all strong (own/exaltation or kendra/trikona) "
                "— blessed with brilliance, learning, arts, and eloquence"
            )
        })

    # Bheri Yoga — Venus, Mercury, Jupiter in 1st, 2nd, 12th houses + strong 9th lord
    houses_123 = {1, 2, 12}
    bj = [p for p in ["Jupiter", "Mercury", "Venus", "Saturn", "Mars"]
          if p in planet_longitudes
          and _house_of(planet_longitudes[p], asc_lon) in houses_123]
    lord9 = house_lord(9, asc_sign)
    lord9_strong = False
    if lord9 in planet_longitudes:
        l9_h = _house_of(planet_longitudes[lord9], asc_lon)
        l9_sign = _sign(planet_longitudes[lord9])
        lord9_strong = (l9_h in KENDRA | TRIKONA or
                        l9_sign in OWN_SIGNS.get(lord9, []) or
                        l9_sign == EXALTATION_SIGN.get(lord9))
    if len(bj) >= 3 and lord9_strong:
        yogas.append({
            "yoga": "Bheri",
            "type": "Combination",
            "planets": bj,
            "description": (
                f"Planets ({', '.join(bj)}) in 1st/2nd/12th with strong 9th lord ({lord9}) "
                f"— wealth, good spouse and children, fame, virtuous, religious"
            )
        })

    # Parvata Yoga — benefics in all kendras, dusthanas empty or with benefics only
    kendra_planets = [p for p, lon in planet_longitudes.items()
                      if _house_of(lon, asc_lon) in KENDRA and p not in {"Rahu", "Ketu"}]
    dusthana_planets = [p for p, lon in planet_longitudes.items()
                        if _house_of(lon, asc_lon) in DUSTHANA and p not in {"Rahu", "Ketu"}]
    all_kendra_benefic = all(p in NATURAL_BENEFICS for p in kendra_planets) and len(kendra_planets) > 0
    all_dust_benefic   = all(p in NATURAL_BENEFICS for p in dusthana_planets)
    if all_kendra_benefic and all_dust_benefic:
        yogas.append({
            "yoga": "Parvata",
            "type": "Combination",
            "planets": kendra_planets,
            "description": (
                "Benefics occupy all kendras and no malefics in dusthanas "
                "— highly fortunate, prosperous, respected like a mountain king"
            )
        })

    return yogas


# ─────────────────────────────────────────────────────────────────────────────
# PARIVARTANA YOGA (Mutual Sign Exchange)
# ─────────────────────────────────────────────────────────────────────────────

def detect_parivartana_yogas(planet_longitudes: dict, asc_lon: float) -> list:
    """
    Parivartana (Mutual Exchange) — when planet A is in the sign of planet B
    AND planet B is in the sign of planet A.

    Three types:
    - Maha Parivartana: both planets in kendra/trikona
    - Dainya Parivartana: one or both in dusthana (6/8/12)
    - Kahala Parivartana: one in kendra and one in upachaya (3/6/10/11)
    """
    yogas = []
    asc_sign = _sign(asc_lon)

    def get_lord(sign_1indexed):
        return SIGN_LORDS[sign_1indexed]

    planets_7 = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    checked = set()

    for p1 in planets_7:
        if p1 not in planet_longitudes:
            continue
        p1_sign = _sign(planet_longitudes[p1])  # sign p1 is IN
        lord_of_p1_sign = get_lord(p1_sign)     # who owns that sign

        for p2 in planets_7:
            if p2 == p1 or (p1, p2) in checked or (p2, p1) in checked:
                continue
            if p2 not in planet_longitudes:
                continue
            p2_sign = _sign(planet_longitudes[p2])
            lord_of_p2_sign = get_lord(p2_sign)

            # Mutual exchange: p1 is in p2's sign AND p2 is in p1's sign
            if lord_of_p1_sign == p2 and lord_of_p2_sign == p1:
                checked.add((p1, p2))
                h1 = _house_of(planet_longitudes[p1], asc_lon)
                h2 = _house_of(planet_longitudes[p2], asc_lon)
                both_kendra_trikona = h1 in KENDRA | TRIKONA and h2 in KENDRA | TRIKONA
                either_dusthana     = h1 in DUSTHANA or h2 in DUSTHANA
                upachaya = {3, 6, 10, 11}

                if both_kendra_trikona:
                    yoga_type = "Maha Parivartana"
                    desc_extra = "— very auspicious; strong, mutual support between houses"
                elif either_dusthana:
                    yoga_type = "Dainya Parivartana"
                    desc_extra = "— challenging exchange; can cause setbacks and humiliation"
                else:
                    yoga_type = "Kahala Parivartana"
                    desc_extra = "— mixed results; energetic but stubborn nature"

                yogas.append({
                    "yoga": yoga_type,
                    "type": "Parivartana",
                    "planets": [p1, p2],
                    "description": (
                        f"{p1} (house {h1}) and {p2} (house {h2}) exchange signs "
                        f"{SIGN_NAMES[p1_sign-1]}/{SIGN_NAMES[p2_sign-1]} {desc_extra}"
                    )
                })

    return yogas

