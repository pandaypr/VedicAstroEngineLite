"""
balarishta.py — Balarishta, Arishta Bhanga, and Purva Janma Shapa

BALARISHTA — Combinations indicating early childhood death/suffering.
  Source: BPHS Chapter 7, Phala Deepika Chapter 5

ARISHTA BHANGA — Cancellation of evil (protective combinations).
  If a Balarishta is cancelled by Arishta Bhanga, the evil is greatly reduced.

PURVA JANMA SHAPA — Past-life curses.
  8 types based on planetary afflictions in specific houses/signs.
  Source: BPHS Chapter 84, various Jyotisha classical texts.
"""

SIGN_NAMES = [
    "Aries","Taurus","Gemini","Cancer","Leo","Virgo",
    "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"
]

SIGN_LORDS = {
    1:"Mars",2:"Venus",3:"Mercury",4:"Moon",5:"Sun",6:"Mercury",
    7:"Venus",8:"Mars",9:"Jupiter",10:"Saturn",11:"Saturn",12:"Jupiter"
}

NATURAL_MALEFICS = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}
NATURAL_BENEFICS = {"Jupiter", "Venus", "Moon", "Mercury"}


def _sign(lon):
    return int(lon / 30.0) % 12 + 1  # 1-indexed

def _sign0(lon):
    return int(lon / 30.0) % 12

def _house_of(lon, asc_lon):
    return int((lon - asc_lon) % 360 / 30.0) + 1

def _planets_in_sign(sign_num, planet_lons):
    return [p for p, l in planet_lons.items() if _sign(l) == sign_num]

def _planets_in_house(house, asc_lon, planet_lons):
    return [p for p, l in planet_lons.items() if _house_of(l, asc_lon) == house]

def _aspects_planet(aspector_lon, target_lon, aspector_name):
    """Returns True if aspector aspects target using Graha Drishti."""
    from .aspects import FULL_ASPECT_HOUSES
    aspector_sign = _sign0(aspector_lon)
    target_sign   = _sign0(target_lon)
    houses = FULL_ASPECT_HOUSES.get(aspector_name, [7])
    for h in houses:
        if (aspector_sign + h - 1) % 12 == target_sign:
            return True
    return False


# ─────────────────────────────────────────────────────────────────────────────
# BALARISHTA
# ─────────────────────────────────────────────────────────────────────────────

def detect_balarishta(planet_lons: dict, asc_lon: float) -> list:
    """
    Detect Balarishta (early-life adversity/death) combinations.
    Returns list of triggered combinations with descriptions.
    """
    results = []
    moon_lon = planet_lons.get("Moon")
    sun_lon  = planet_lons.get("Sun")
    lagna_sign = _sign(asc_lon)

    def h(p):
        return _house_of(planet_lons[p], asc_lon) if p in planet_lons else None

    def mal_aspect_moon():
        """True if Moon is aspected by a malefic."""
        if moon_lon is None: return False
        for mal in NATURAL_MALEFICS:
            if mal in planet_lons:
                if _aspects_planet(planet_lons[mal], moon_lon, mal):
                    return True
        return False

    def ben_conjunct_moon():
        """True if a natural benefic is conjunct Moon."""
        if moon_lon is None: return False
        for ben in NATURAL_BENEFICS:
            if ben in planet_lons and ben != "Moon":
                if _sign0(planet_lons[ben]) == _sign0(moon_lon):
                    return True
        return False

    # Rule 1: Moon in 6th/8th/12th without benefic association
    if moon_lon:
        moon_h = h("Moon")
        if moon_h in {6, 8, 12} and not ben_conjunct_moon():
            results.append({
                "name": "Moon in Dusthana",
                "severity": "Moderate",
                "description": f"Moon in house {moon_h} without benefic — mental/physical adversity in early childhood"
            })

    # Rule 2: Moon aspected by malefic and lagna aspected by malefic (no benefic)
    if mal_aspect_moon():
        mal_asp_lagna = False
        for mal in NATURAL_MALEFICS:
            if mal in planet_lons and _aspects_planet(planet_lons[mal], asc_lon, mal):
                mal_asp_lagna = True
                break
        ben_asp_lagna = False
        for ben in NATURAL_BENEFICS:
            if ben in planet_lons and _aspects_planet(planet_lons[ben], asc_lon, ben):
                ben_asp_lagna = True
                break
        if mal_asp_lagna and not ben_asp_lagna:
            results.append({
                "name": "Malefic aspects Moon & Lagna",
                "severity": "Severe",
                "description": "Malefic aspects both Moon and Lagna without benefic protection — significant early hardship"
            })

    # Rule 3: Lagna and Moon both in malefic signs + malefic aspects
    malefic_signs = {1,2,3,6,8,10,11}  # Aries, Tau, Gem, Vir, Sco, Cap, Aqu (approximate)
    if moon_lon and lagna_sign in malefic_signs and _sign(moon_lon) in malefic_signs:
        if mal_aspect_moon():
            results.append({
                "name": "Lagna & Moon in malefic signs",
                "severity": "Severe",
                "description": "Both Lagna and Moon in harsh signs under malefic aspect — Balarishta present"
            })

    # Rule 4: Saturn in Lagna, Moon not aspected by Jupiter
    if "Saturn" in planet_lons and h("Saturn") == 1:
        jup_aspects_moon = False
        if "Jupiter" in planet_lons and moon_lon:
            jup_aspects_moon = _aspects_planet(planet_lons["Jupiter"], moon_lon, "Jupiter")
        if not jup_aspects_moon:
            results.append({
                "name": "Saturn in Lagna, Moon unprotected",
                "severity": "Moderate",
                "description": "Saturn occupies Lagna without Jupiter aspecting Moon — early life burdens"
            })

    return results


# ─────────────────────────────────────────────────────────────────────────────
# ARISHTA BHANGA
# ─────────────────────────────────────────────────────────────────────────────

def detect_arishta_bhanga(planet_lons: dict, asc_lon: float,
                           balarishtas: list) -> list:
    """
    Detect Arishta Bhanga (cancellations of evil).
    Only meaningful if Balarishtas are present.
    Returns list of active cancellations.
    """
    results = []
    moon_lon = planet_lons.get("Moon")
    if not balarishtas:
        return results  # Nothing to cancel

    def h(p):
        return _house_of(planet_lons[p], asc_lon) if p in planet_lons else None

    # Cancellation 1: Jupiter aspects Moon or Lagna
    if "Jupiter" in planet_lons:
        if moon_lon and _aspects_planet(planet_lons["Jupiter"], moon_lon, "Jupiter"):
            results.append({
                "cancellation": "Jupiter aspects Moon",
                "effect": "Balarishta greatly reduced — Jupiter's protection preserves life and health"
            })
        if _aspects_planet(planet_lons["Jupiter"], asc_lon, "Jupiter"):
            results.append({
                "cancellation": "Jupiter aspects Lagna",
                "effect": "Lagna protected by Jupiter — strength to overcome adversity"
            })

    # Cancellation 2: Lagna lord in Kendra or Trikona
    lagna_sign = _sign(asc_lon)
    ll = SIGN_LORDS[lagna_sign]
    if ll in planet_lons:
        ll_h = h(ll)
        if ll_h in {1,4,5,7,9,10}:
            results.append({
                "cancellation": f"Lagna lord {ll} in house {ll_h}",
                "effect": "Strong Lagna lord cancels Balarishta — native survives and grows strong"
            })

    # Cancellation 3: Full Moon (Poornima birth) — bright Moon in angles
    if moon_lon:
        sun_lon = planet_lons.get("Sun")
        if sun_lon:
            moon_phase = (moon_lon - sun_lon) % 360
            if 150 <= moon_phase <= 210:  # Near full moon
                results.append({
                    "cancellation": "Full Moon birth",
                    "effect": "Waxing/Full Moon greatly cancels Balarishta — lunar vitality"
                })

    # Cancellation 4: Benefic in Lagna
    for ben in NATURAL_BENEFICS:
        if ben in planet_lons and h(ben) == 1:
            results.append({
                "cancellation": f"{ben} in Lagna",
                "effect": f"{ben} in Lagna acts as shield — native protected from early adversity"
            })
            break

    return results


# ─────────────────────────────────────────────────────────────────────────────
# PURVA JANMA SHAPA (Past-life Curses)
# ─────────────────────────────────────────────────────────────────────────────

def detect_purva_janma_shapa(planet_lons: dict, asc_lon: float) -> list:
    """
    Detect Purva Janma Shapa — past-life curses indicated in the natal chart.

    The 8 Shapas:
    1. Sarpa Shapa  — Curse of serpents (Rahu/Ketu + 5th house affliction)
    2. Pitra Shapa  — Curse of ancestors/father (Sun + 9th house affliction)
    3. Matra Shapa  — Curse of mother (Moon + 4th house affliction)
    4. Bhratra Shapa— Curse of siblings (Mars + 3rd house affliction)
    5. Matula Shapa — Curse of maternal uncle (Mercury affliction in 3rd/6th)
    6. Brahmana Shapa— Curse of Brahmins/teachers (Jupiter + 9th affliction)
    7. Patni Shapa  — Curse of wife/partner (Venus + 7th house affliction)
    8. Preta Shapa  — Curse of departed spirits (Saturn + 12th affliction)
    """
    results = []

    def h(p):
        return _house_of(planet_lons[p], asc_lon) if p in planet_lons else None

    def malefic_in_house(house_num):
        return [p for p in NATURAL_MALEFICS if p in planet_lons and h(p) == house_num]

    def lord_afflicted(house_num):
        """True if the lord of house_num is in a dusthana or conjunct malefic."""
        lagna_sign = _sign(asc_lon)
        sign = (lagna_sign + house_num - 2) % 12 + 1
        lord = SIGN_LORDS[sign]
        if lord not in planet_lons: return False
        lord_h = h(lord)
        if lord_h in {6, 8, 12}: return True
        # Conjunct with malefic
        lord_sign0 = _sign0(planet_lons[lord])
        for mal in NATURAL_MALEFICS:
            if mal in planet_lons and mal != lord:
                if _sign0(planet_lons[mal]) == lord_sign0:
                    return True
        return False

    # 1. SARPA SHAPA — Rahu or Ketu in 5th house, 5th lord afflicted
    rahu_h = h("Rahu") if "Rahu" in planet_lons else None
    ketu_h = h("Ketu") if "Ketu" in planet_lons else None
    mal_in_5 = malefic_in_house(5)
    if (rahu_h == 5 or ketu_h == 5) or (len(mal_in_5) >= 2):
        if lord_afflicted(5):
            results.append({
                "shapa": "Sarpa Shapa",
                "description": "Curse of Serpents — Rahu/Ketu afflicting 5th house and its lord. "
                               "Causes childlessness, snake-related fears, hidden enemies. "
                               "Remedy: Nag Panchami puja, feed serpents milk, Rahu-Ketu Shanti.",
                "severity": "High"
            })

    # 2. PITRA SHAPA — Sun + Rahu in 9th, or 9th lord weak/afflicted
    sun_h = h("Sun")
    if sun_h == 9 and rahu_h == 9:
        results.append({
            "shapa": "Pitra Shapa",
            "description": "Curse of Ancestors (Father) — Sun with Rahu in 9th. "
                           "Causes lack of paternal blessings, career obstacles, disrespect. "
                           "Remedy: Pitru Tarpan, Gaya Shraddha, feed crows on Amavasya.",
            "severity": "High"
        })
    elif lord_afflicted(9) and (sun_h in {6, 8, 12} or (sun_h and rahu_h == sun_h)):
        results.append({
            "shapa": "Pitra Shapa (Mild)",
            "description": "Mild Pitra Dosha — 9th lord afflicted with Sun's association.",
            "severity": "Moderate"
        })

    # 3. MATRA SHAPA — Moon + Saturn/Rahu in 4th, or 4th lord afflicted
    moon_h = h("Moon")
    sat_h  = h("Saturn")
    if moon_h == 4 and (sat_h == 4 or rahu_h == 4):
        results.append({
            "shapa": "Matra Shapa",
            "description": "Curse of Mother — Moon afflicted in 4th by Saturn/Rahu. "
                           "Causes maternal deprivation, home instability, lack of nurturing. "
                           "Remedy: Chandra Shanti, Devi puja, care for mother figure.",
            "severity": "High"
        })
    elif lord_afflicted(4) and moon_h in {6, 8, 12}:
        results.append({
            "shapa": "Matra Shapa (Mild)",
            "description": "Moon in dusthana with afflicted 4th lord — mild maternal curse.",
            "severity": "Moderate"
        })

    # 4. BHRATRA SHAPA — Mars + Saturn/Rahu in 3rd, or 3rd lord afflicted
    mars_h = h("Mars")
    if mars_h == 3 and (sat_h == 3 or rahu_h == 3):
        results.append({
            "shapa": "Bhratra Shapa",
            "description": "Curse of Siblings — Mars afflicted in 3rd house. "
                           "Causes sibling disputes, lack of brotherly support, accidents. "
                           "Remedy: Hanuman puja, fast on Tuesdays, donate red items.",
            "severity": "High"
        })

    # 5. MATULA SHAPA — Mercury afflicted in 3rd or 6th (maternal uncle = 6th)
    mer_h = h("Mercury")
    if mer_h in {3, 6} and (sat_h == mer_h or rahu_h == mer_h):
        results.append({
            "shapa": "Matula Shapa",
            "description": "Curse of Maternal Uncle — Mercury afflicted in 3rd/6th. "
                           "Causes disputes with maternal relatives, communication problems. "
                           "Remedy: Vishnu Sahasranama, green offering on Wednesdays.",
            "severity": "Moderate"
        })

    # 6. BRAHMANA SHAPA — Jupiter + Rahu in 9th, or Jupiter in 8th/12th
    jup_h = h("Jupiter")
    if jup_h == 9 and rahu_h == 9:
        results.append({
            "shapa": "Brahmana Shapa",
            "description": "Curse of Teachers/Brahmins — Jupiter with Rahu in 9th. "
                           "Causes lack of wisdom, blocked spiritual growth, guru problems. "
                           "Remedy: Guru Puja, respect teachers, donate yellow items on Thursdays.",
            "severity": "High"
        })
    elif jup_h in {6, 8, 12} and lord_afflicted(9):
        results.append({
            "shapa": "Brahmana Shapa (Mild)",
            "description": "Jupiter in dusthana with afflicted 9th lord — mild teacher's curse.",
            "severity": "Moderate"
        })

    # 7. PATNI SHAPA — Venus + Saturn/Rahu in 7th, or 7th lord afflicted
    ven_h = h("Venus")
    if ven_h == 7 and (sat_h == 7 or rahu_h == 7):
        results.append({
            "shapa": "Patni Shapa",
            "description": "Curse of Spouse/Partner — Venus afflicted in 7th. "
                           "Causes marital discord, delayed marriage, partner's suffering. "
                           "Remedy: Shukra Shanti, Uma-Maheshwar puja, donate white on Fridays.",
            "severity": "High"
        })

    # 8. PRETA SHAPA — Saturn + Rahu in 12th, or 12th lord severely afflicted
    if sat_h == 12 and rahu_h == 12:
        results.append({
            "shapa": "Preta Shapa",
            "description": "Curse of Departed Spirits — Saturn with Rahu in 12th. "
                           "Causes nightmares, spirit disturbances, losses, isolation. "
                           "Remedy: Tripindi Shraddha, Narayan Nagbali, Pitru puja.",
            "severity": "High"
        })

    return results
