"""
matchmaking.py — Complete Marriage Compatibility Analysis

Implements:
1. Ashtakoota Guna Milan (36-point system)
2. Kuja Dosha (Manglik) — precise detection with all classical cancellations
3. Papa Samya (Malefic Balance) — neutralization check between two charts

Sources: BPHS, Muhurta Chintamani, Phaladeepika
"""

from .shadbala import ShadbalaCalculator
from .constants import SIGN_OWNERS

# ─────────────────────────────────────────────────────────────────────────────
# ASHTAKOOTA DATA TABLES
# ─────────────────────────────────────────────────────────────────────────────

VARNA_MAP = {
    1: 2, 2: 3, 3: 4, 4: 1,   # Ar=Kshatriya, Ta=Vaishya, Ge=Shudra, Cn=Brahmin
    5: 2, 6: 3, 7: 4, 8: 1,   # Le=Kshatriya, Vi=Vaishya, Li=Shudra, Sc=Brahmin
    9: 2, 10: 3, 11: 4, 12: 1 # Sg=Kshatriya, Cp=Vaishya, Aq=Shudra, Pi=Brahmin
}
# Varna rank: 1=Brahmin (highest), 2=Kshatriya, 3=Vaishya, 4=Shudra (lowest)

VASHYA_GROUPS = {
    1: "Chatushpada", 2: "Manava", 3: "Manava", 4: "Jalchar",
    5: "Chatushpada", 6: "Manava", 7: "Manava", 8: "Keeta",
    9: "Chatushpada", 10: "Chatushpada", 11: "Manava", 12: "Jalchar"
}
# Vashya compatibility table: who has "vashya" over whom
VASHYA_SCORES = {
    ("Manava",    "Jalchar"):    2,   # Man rules water
    ("Jalchar",   "Manava"):     1,   # Water partial to man
    ("Manava",    "Chatushpada"):2,
    ("Chatushpada","Manava"):    1,
    ("Manava",    "Keeta"):      2,
    ("Chatushpada","Keeta"):     1,
}

# Nakshatra Nadi (0=Aadi, 1=Madhya, 2=Antya)
NADI_MAP = [0,1,2,2,1,0,0,1,2,2,1,0,0,1,2,2,1,0,0,1,2,2,1,0,0,1,2]

# Nakshatra Gana (0=Deva, 1=Manushya, 2=Rakshasa)
GANA_MAP = {
    1:0,2:1,3:2,4:1,5:0,6:1,7:0,8:0,9:2,10:2,
    11:1,12:1,13:0,14:2,15:0,16:2,17:0,18:2,
    19:2,20:1,21:1,22:0,23:2,24:2,25:1,26:1,27:0
}

# Nakshatra Yoni (animal symbol) — pairs determine compatibility
YONI_MAP = {
    1:"Ashwa", 2:"Gaja", 3:"Mesha", 4:"Sarpa", 5:"Swa",
    6:"Marjara", 7:"Mahisha", 8:"Vyaghra", 9:"Marjara", 10:"Swa",
    11:"Sarpa", 12:"Ashwa", 13:"Mahisha", 14:"Vyaghra", 15:"Mesha",
    16:"Gaja", 17:"Vanara", 18:"Nakula", 19:"Swa", 20:"Ashwa",
    21:"Nakula", 22:"Gau", 23:"Vanara", 24:"Simha", 25:"Gau",
    26:"Simha", 27:"Gaja"
}
# Yoni enemy pairs (sworn enemies = 0 pts)
YONI_ENEMIES = {
    ("Ashwa",  "Mahisha"), ("Gaja",   "Simha"),  ("Mesha",  "Vanara"),
    ("Sarpa",  "Nakula"),  ("Swa",    "Marjara"), ("Vyaghra","Gau"),
}

SIGN_NAMES_12 = [
    "Aries","Taurus","Gemini","Cancer","Leo","Virgo",
    "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"
]

NAK_NAMES_27 = [
    "Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra","Punarvasu","Pushya","Ashlesha",
    "Magha","Purva Phalguni","Uttara Phalguni","Hasta","Chitra","Swati","Vishakha","Anuradha","Jyeshtha",
    "Mula","Purva Ashadha","Uttara Ashadha","Shravana","Dhanishta","Shatabhisha",
    "Purva Bhadrapada","Uttara Bhadrapada","Revati"
]


def _nak(moon_lon):
    """1-indexed Nakshatra from Moon longitude."""
    return int(moon_lon / (360 / 27)) + 1

def _sign(lon):
    """1-indexed sign from longitude."""
    return int(lon / 30) % 12 + 1


def _yoni_score(nak_b, nak_g):
    y_b = YONI_MAP.get(nak_b, "Ashwa")
    y_g = YONI_MAP.get(nak_g, "Ashwa")
    if y_b == y_g:
        return 4
    pair = (y_b, y_g)
    pair_rev = (y_g, y_b)
    if pair in YONI_ENEMIES or pair_rev in YONI_ENEMIES:
        return 0
    # Friendly animals
    FRIENDLY = {
        ("Ashwa","Ashwa"),("Gau","Vanara"),("Mesha","Mesha"),
        ("Gaja","Gaja"),("Sarpa","Sarpa"),("Swa","Swa"),
    }
    if pair in FRIENDLY or pair_rev in FRIENDLY:
        return 3
    return 2  # Neutral


def get_maitri_score(b_sign, g_sign):
    if b_sign == g_sign:
        return 5.0
    lord_b = SIGN_OWNERS[b_sign]
    lord_g = SIGN_OWNERS[g_sign]
    if lord_b == lord_g:
        return 5.0
    rel_b = ShadbalaCalculator.get_relationship(lord_b, lord_g)
    rel_g = ShadbalaCalculator.get_relationship(lord_g, lord_b)
    score_map = {
        ("friend", "friend"): 5.0,
        ("friend", "neutral"): 4.0, ("neutral", "friend"): 4.0,
        ("neutral", "neutral"): 3.0,
        ("friend", "enemy"): 1.0, ("enemy", "friend"): 1.0,
        ("neutral", "enemy"): 0.5, ("enemy", "neutral"): 0.5,
        ("enemy", "enemy"): 0.0
    }
    return score_map.get((rel_b, rel_g), 0.0)


def calculate_guna_milan(boy_moon_lon: float, girl_moon_lon: float) -> dict:
    """
    Full 36-point Ashtakoota Guna Milan.
    Returns detailed breakdown of all 8 Kootas with scores, max, and interpretation.
    """
    b_nak = _nak(boy_moon_lon)
    g_nak = _nak(girl_moon_lon)
    b_sign = _sign(boy_moon_lon)
    g_sign = _sign(girl_moon_lon)

    score = {}
    total = 0.0

    # 1. Varna (1 pt) — spiritual/social hierarchy
    v_b = VARNA_MAP[b_sign]
    v_g = VARNA_MAP[g_sign]
    # Boy's varna must be >= girl's varna (lower number = higher)
    pt_varna = 1.0 if v_b <= v_g else 0.0
    score["Varna"] = {
        "score": pt_varna, "max": 1,
        "boy": ["Brahmin","Kshatriya","Vaishya","Shudra"][v_b-1],
        "girl": ["Brahmin","Kshatriya","Vaishya","Shudra"][v_g-1],
        "note": "Boy's spiritual class should be >= girl's"
    }
    total += pt_varna

    # 2. Vashya (2 pts) — power/dominance
    vb_grp = VASHYA_GROUPS[b_sign]
    vg_grp = VASHYA_GROUPS[g_sign]
    if vb_grp == vg_grp:
        pt_vashya = 2.0
    else:
        pt_vashya = float(VASHYA_SCORES.get((vb_grp, vg_grp),
                          VASHYA_SCORES.get((vg_grp, vb_grp), 0)))
    score["Vashya"] = {
        "score": pt_vashya, "max": 2,
        "boy_group": vb_grp, "girl_group": vg_grp
    }
    total += pt_vashya

    # 3. Tara (3 pts) — destiny/longevity
    t1 = ((b_nak - g_nak) % 9) + 1
    t2 = ((g_nak - b_nak) % 9) + 1
    BAD_TARAS = {3, 5, 7}  # Vipat, Pratyari, Naidhana
    pt_tara = 0.0
    if t1 not in BAD_TARAS: pt_tara += 1.5
    if t2 not in BAD_TARAS: pt_tara += 1.5
    score["Tara"] = {
        "score": pt_tara, "max": 3,
        "boy_tara": t1, "girl_tara": t2,
        "note": "Taras 3,5,7 (Vipat/Pratyari/Naidhana) are inauspicious"
    }
    total += pt_tara

    # 4. Yoni (4 pts) — physical/sexual compatibility
    pt_yoni = _yoni_score(b_nak, g_nak)
    score["Yoni"] = {
        "score": float(pt_yoni), "max": 4,
        "boy_animal": YONI_MAP.get(b_nak, "?"),
        "girl_animal": YONI_MAP.get(g_nak, "?")
    }
    total += pt_yoni

    # 5. Graha Maitri (5 pts) — mental/intellectual compatibility
    pt_maitri = get_maitri_score(b_sign, g_sign)
    score["GrahaMaitri"] = {
        "score": pt_maitri, "max": 5,
        "boy_lord": SIGN_OWNERS[b_sign],
        "girl_lord": SIGN_OWNERS[g_sign]
    }
    total += pt_maitri

    # 6. Gana (6 pts) — temperament
    g1 = GANA_MAP[b_nak]
    g2 = GANA_MAP[g_nak]
    gana_names = ["Deva", "Manushya", "Rakshasa"]
    if g1 == g2:
        pt_gana = 6.0
    elif (g1 == 0 and g2 == 1) or (g1 == 1 and g2 == 0):
        pt_gana = 5.0
    elif (g1 == 0 and g2 == 2) or (g1 == 2 and g2 == 0):
        pt_gana = 1.0
    else:
        pt_gana = 0.0
    score["Gana"] = {
        "score": pt_gana, "max": 6,
        "boy_gana": gana_names[g1],
        "girl_gana": gana_names[g2]
    }
    total += pt_gana

    # 7. Bhakoot (7 pts) — emotional/family compatibility
    diff_bg = (b_sign - g_sign) % 12
    diff_gb = (g_sign - b_sign) % 12
    # Inauspicious: 2/12, 5/9, 6/8
    INAUSPICIOUS_BHAKOOT = {(2,10),(10,2),(5,7),(7,5),(6,6)}
    pair = (diff_bg, diff_gb) if diff_bg > 0 else (12, 12)
    inauspicious = (diff_bg in {1,11} or diff_bg in {4,8} or diff_bg in {5,7})
    pt_bhakoot = 0.0 if inauspicious else 7.0
    score["Bhakoot"] = {
        "score": pt_bhakoot, "max": 7,
        "boy_sign": SIGN_NAMES_12[b_sign-1],
        "girl_sign": SIGN_NAMES_12[g_sign-1],
        "relationship": f"{diff_bg+1}/{diff_gb+1}",
        "note": "2/12, 5/9, 6/8 relationships are Bhakoot dosha"
    }
    total += pt_bhakoot

    # 8. Nadi (8 pts) — health/genetics
    n1 = NADI_MAP[b_nak - 1]
    n2 = NADI_MAP[g_nak - 1]
    pt_nadi = 8.0 if n1 != n2 else 0.0
    score["Nadi"] = {
        "score": pt_nadi, "max": 8,
        "boy_nadi": ["Aadi","Madhya","Antya"][n1],
        "girl_nadi": ["Aadi","Madhya","Antya"][n2],
        "note": "Same Nadi = Nadi Dosha (genetic incompatibility)"
    }
    total += pt_nadi

    # Summary
    score["Total"] = {"score": round(total, 1), "max": 36}
    if total >= 28:
        status = "Excellent Match (Uttam)"
    elif total >= 21:
        status = "Good Match (Madhyam)"
    elif total >= 18:
        status = "Acceptable Match"
    else:
        status = "Unfavorable Match — Doshas need remediation"
    score["Status"] = status
    score["Boy_Nakshatra"] = NAK_NAMES_27[b_nak - 1]
    score["Girl_Nakshatra"] = NAK_NAMES_27[g_nak - 1]

    return score


# ─────────────────────────────────────────────────────────────────────────────
# KUJA DOSHA (MANGLIK DOSHA)
# ─────────────────────────────────────────────────────────────────────────────

def detect_kuja_dosha(planet_longitudes: dict, asc_lon: float) -> dict:
    """
    Kuja (Mars) Dosha — Manglik detection.

    Classical Rule: Mars in houses 1, 2, 4, 7, 8, or 12 from
    - Ascendant
    - Moon
    - Venus (as per South Indian tradition)

    Severity:
    - Mars in 7th or 8th = HIGH (directly damages marriage house)
    - Mars in 1st, 4th   = MODERATE (indirect impact on relationship)
    - Mars in 2nd, 12th  = MILD (loss of wealth/happiness in marriage)

    Returns:
    - is_manglik: True/False
    - severity: "High" / "Moderate" / "Mild" / "None"
    - positions: list of Mars house placements causing the dosha
    - cancellations: list of classical cancellations active in this chart
    - net_dosha: "Active" / "Cancelled" / "Reduced"
    """
    if "Mars" not in planet_longitudes:
        return {"is_manglik": False, "severity": "None", "positions": [],
                "cancellations": [], "net_dosha": "None"}

    mars_lon = planet_longitudes["Mars"]
    mars_sign = int(mars_lon / 30) % 12  # 0-indexed

    DOSHA_HOUSES = {1, 2, 4, 7, 8, 12}
    HIGH_SEVERITY = {7, 8}
    MOD_SEVERITY  = {1, 4}

    def house_from(ref_lon):
        """1-indexed house of Mars from a reference longitude."""
        return int((mars_lon - ref_lon) % 360 / 30) + 1

    positions = []

    # Check from Lagna
    h_lagna = house_from(asc_lon)
    if h_lagna in DOSHA_HOUSES:
        positions.append({"reference": "Lagna", "house": h_lagna})

    # Check from Moon
    if "Moon" in planet_longitudes:
        h_moon = house_from(planet_longitudes["Moon"])
        if h_moon in DOSHA_HOUSES:
            positions.append({"reference": "Moon", "house": h_moon})

    # Check from Venus
    if "Venus" in planet_longitudes:
        h_venus = house_from(planet_longitudes["Venus"])
        if h_venus in DOSHA_HOUSES:
            positions.append({"reference": "Venus", "house": h_venus})

    is_manglik = len(positions) > 0

    # Determine severity
    houses_hit = {p["house"] for p in positions}
    if houses_hit & HIGH_SEVERITY:
        severity = "High"
    elif houses_hit & MOD_SEVERITY:
        severity = "Moderate"
    elif is_manglik:
        severity = "Mild"
    else:
        severity = "None"

    # ─── CLASSICAL CANCELLATIONS ───────────────────────────────────────────
    # Source: Brihat Parasara Hora Shastra, Muhurta Chintamani
    cancellations = []
    mars_sign_1indexed = mars_sign + 1  # 1-indexed
    asc_sign = int(asc_lon / 30) % 12 + 1  # 1-indexed

    def house_of(planet):
        if planet not in planet_longitudes: return None
        return int((planet_longitudes[planet] - asc_lon) % 360 / 30) + 1

    def sign_of(planet):
        if planet not in planet_longitudes: return None
        return int(planet_longitudes[planet] / 30) % 12 + 1

    # 1. Mars in its own sign (Aries=1 or Scorpio=8) — own strength cancels dosha
    if mars_sign_1indexed in {1, 8}:
        cancellations.append({
            "rule": "Mars in own sign (Aries/Scorpio)",
            "effect": "Full cancellation — Mars is strong and dignified"
        })

    # 2. Mars in exaltation (Capricorn = sign 10)
    if mars_sign_1indexed == 10:
        cancellations.append({
            "rule": "Mars exalted in Capricorn",
            "effect": "Full cancellation — exalted Mars acts beneficially"
        })

    # 3. Mars in 2nd house but Lagna is Gemini or Virgo
    if h_lagna == 2 and asc_sign in {3, 6}:
        cancellations.append({
            "rule": "Mars in 2nd from Gemini/Virgo Lagna",
            "effect": "Cancellation — Mercury-ruled Lagna neutralizes Mars in 2nd"
        })

    # 4. Jupiter or Venus aspects Mars
    from .aspects import FULL_ASPECT_HOUSES
    def aspects_mars(planet_name):
        if planet_name not in planet_longitudes: return False
        p_sign0 = int(planet_longitudes[planet_name] / 30) % 12
        houses = FULL_ASPECT_HOUSES.get(planet_name, [7])
        for h in houses:
            if (p_sign0 + h - 1) % 12 == mars_sign:
                return True
        return False

    if aspects_mars("Jupiter"):
        cancellations.append({
            "rule": "Jupiter aspects Mars",
            "effect": "Strong reduction — Jupiter neutralizes Manglik energy"
        })

    if aspects_mars("Venus"):
        cancellations.append({
            "rule": "Venus aspects Mars",
            "effect": "Reduction — Venus softens Mars' harsh marital influence"
        })

    # 5. Mars in 1st house with Aries/Scorpio Lagna
    if h_lagna == 1 and asc_sign in {1, 8}:
        cancellations.append({
            "rule": "Mars in 1st house, Lagna is Aries/Scorpio",
            "effect": "Cancellation — Mars rules the Lagna, no dosha"
        })

    # 6. Mars in 4th house with Aries Lagna (Mars rules 4th from Aries = Kendra lord)
    if h_lagna == 4 and asc_sign == 1:
        cancellations.append({
            "rule": "Mars in 4th with Aries Lagna (owns 4th's Scorpio)",
            "effect": "Partial cancellation"
        })

    # 7. Mars in 8th but Aquarius or Cancer Lagna
    if h_lagna == 8 and asc_sign in {4, 11}:
        cancellations.append({
            "rule": "Mars in 8th from Cancer/Aquarius Lagna",
            "effect": "Cancellation per Parasara — specific Lagna exception"
        })

    # 8. If both partners have Kuja Dosha — mutual dosha cancels
    # (This is applied in calculate_papa_samya)

    # Net result
    if len(cancellations) >= 2:
        net_dosha = "Cancelled"
    elif len(cancellations) == 1:
        net_dosha = "Reduced"
    elif is_manglik:
        net_dosha = "Active"
    else:
        net_dosha = "None"

    return {
        "is_manglik": is_manglik,
        "severity": severity,
        "positions": positions,
        "cancellations": cancellations,
        "net_dosha": net_dosha,
        "mars_sign": SIGN_NAMES_12[mars_sign],
        "explanation": (
            f"Mars occupies house(s) {[p['house'] for p in positions]} from "
            f"{'Lagna, Moon, Venus'} — {severity} Kuja Dosha. "
            f"Status: {net_dosha}"
        )
    }


# ─────────────────────────────────────────────────────────────────────────────
# PAPA SAMYA (Malefic Balance Between Two Charts)
# ─────────────────────────────────────────────────────────────────────────────

# Natural malefics: Sun, Mars, Saturn, Rahu, Ketu
# Functional malefics depend on the Lagna, but for Papa Samya we use natural ones.

MALEFIC_PLANETS = ["Sun", "Mars", "Saturn", "Rahu", "Ketu"]

# Papa (malefic) strength by house placement
# Based on classical Papa Samya rules from Muhurta Chintamani
PAPA_HOUSE_WEIGHTS = {
    1: 0.5,   # 1st — mars, rahu, ketu strong here
    2: 2.0,   # 2nd — family/speech
    4: 2.0,   # 4th — home/happiness
    7: 4.0,   # 7th — marriage (highest impact)
    8: 4.0,   # 8th — longevity (highest impact)
    12: 2.0,  # 12th — expenses/bed pleasures
    # Other houses get 0 weight for Papa Samya purposes
}

# Modified weights for specific planets in specific houses
PLANET_HOUSE_MODIFIERS = {
    ("Saturn", 8): 1.5,  # Saturn in 8th is extremely negative
    ("Mars",   7): 1.5,  # Mars in 7th is Kuja Dosha center
    ("Rahu",   7): 1.5,
    ("Ketu",   7): 1.5,
}


def calculate_papa_samya(
    boy_planet_lons: dict, boy_asc_lon: float,
    girl_planet_lons: dict, girl_asc_lon: float
) -> dict:
    """
    Papa Samya — Malefic Balance Compatibility Analysis.

    This system calculates the "malefic score" of each partner's chart
    and checks whether they are within an acceptable range of each other.

    Classical rule: If the difference between the boy's and girl's malefic
    scores is <= 25%, their charts are considered balanced (Samya).

    Returns:
    - boy_score: total papa score
    - girl_score: total papa score
    - difference_percent: percentage imbalance
    - is_balanced: True if within 25% threshold
    - mutual_kuja_cancellation: True if both are Manglik
    - recommendation: text summary
    """

    def _house_of(lon, asc_lon):
        return int((lon - asc_lon) % 360 / 30) + 1

    def papa_score(planet_lons, asc_lon):
        score = 0.0
        detail = {}
        for planet in MALEFIC_PLANETS:
            if planet not in planet_lons:
                continue
            h = _house_of(planet_lons[planet], asc_lon)
            base_weight = PAPA_HOUSE_WEIGHTS.get(h, 0.0)
            modifier = PLANET_HOUSE_MODIFIERS.get((planet, h), 1.0)
            contribution = base_weight * modifier
            if contribution > 0:
                score += contribution
                detail[planet] = {"house": h, "score": round(contribution, 2)}
        return round(score, 2), detail

    boy_score, boy_detail = papa_score(boy_planet_lons, boy_asc_lon)
    girl_score, girl_detail = papa_score(girl_planet_lons, girl_asc_lon)

    # Check Mutual Kuja Dosha cancellation
    boy_kuja  = detect_kuja_dosha(boy_planet_lons,  boy_asc_lon)
    girl_kuja = detect_kuja_dosha(girl_planet_lons, girl_asc_lon)
    mutual_kuja = boy_kuja["is_manglik"] and girl_kuja["is_manglik"]

    # If both are Manglik, reduce the higher score to match the lower
    if mutual_kuja:
        # Apply a 30% reduction to the higher score to reflect cancellation
        if boy_score > girl_score:
            boy_score_adj  = round(boy_score * 0.70, 2)
            girl_score_adj = girl_score
        else:
            boy_score_adj  = boy_score
            girl_score_adj = round(girl_score * 0.70, 2)
    else:
        boy_score_adj  = boy_score
        girl_score_adj = girl_score

    # Calculate imbalance
    max_score = max(boy_score_adj, girl_score_adj)
    if max_score == 0:
        diff_pct = 0.0
        is_balanced = True
    else:
        diff_pct = round(abs(boy_score_adj - girl_score_adj) / max_score * 100, 1)
        is_balanced = diff_pct <= 25.0

    # Recommendation
    if is_balanced and diff_pct < 10:
        recommendation = "Excellent balance — charts have nearly equal malefic burden. Very compatible."
    elif is_balanced:
        recommendation = f"Acceptable balance ({diff_pct}% difference). Minor imbalance is manageable with remedies."
    else:
        recommendation = (
            f"Significant imbalance ({diff_pct}% difference). "
            f"The partner with lower score ({('Boy' if boy_score_adj < girl_score_adj else 'Girl')}) "
            f"may suffer more in the relationship. Remedies strongly advised."
        )

    return {
        "boy_papa_score":        boy_score,
        "girl_papa_score":       girl_score,
        "boy_adjusted_score":    boy_score_adj,
        "girl_adjusted_score":   girl_score_adj,
        "boy_detail":            boy_detail,
        "girl_detail":           girl_detail,
        "difference_percent":    diff_pct,
        "is_balanced":           is_balanced,
        "mutual_kuja_cancellation": mutual_kuja,
        "boy_kuja_dosha":        boy_kuja,
        "girl_kuja_dosha":       girl_kuja,
        "recommendation":        recommendation,
    }
