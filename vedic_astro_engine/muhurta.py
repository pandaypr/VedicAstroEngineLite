"""
muhurta.py — The Vedic Electional Astrology Engine
Includes: Panchak, Bhadra, Sarvartha Siddhi, Amrit Siddhi, and more.
"""

def check_panchak(moon_lon: float) -> bool:
    """
    Panchak occurs when the Moon is in Aquarius or Pisces, 
    specifically from the 3rd quarter of Dhanishta to Revati.
    Longitude Range: 296° 40' to 360°
    """
    return 296.6667 <= moon_lon <= 360.0

NAKS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu",
    "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta",
    "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",
    "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", 
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

def check_bhadra(karana_num: int) -> bool:
    """
    Bhadra is another name for Vishti Karana.
    Vishti is every 7th karana in the moving sequence.
    Indices: 7, 14, 21, 28, 35, 42, 49, 56
    """
    return karana_num in [7, 14, 21, 28, 35, 42, 49, 56]

def get_muhurta_yogas(weekday: int, nak_idx: int) -> list:
    """
    Finds special auspicious yogas based on Weekday + Nakshatra.
    nak_idx: 1-27
    """
    if not (1 <= nak_idx <= 27): return []
    nak_name = NAKS[nak_idx - 1]
    yogas = []
    
    # Sarvartha Siddhi Yoga (SSY)
    ssy_map = {
        6: ["Ashwini", "Pushya", "Uttara Phalguni", "Uttara Ashadha", "Uttara Bhadrapada", "Mula", "Hasta"], # Sun
        0: ["Rohini", "Mrigashira", "Pushya", "Anuradha", "Shravana"], # Mon
        1: ["Ashwini", "Mrigashira", "Jyeshtha", "Mula"], # Tue
        2: ["Krittika", "Rohini", "Mrigashira", "Hasta", "Anuradha"], # Wed
        3: ["Ashwini", "Rohini", "Punarvasu", "Pushya", "Anuradha"], # Thu
        4: ["Ashwini", "Bharani", "Rohini", "Punarvasu", "Shravana"], # Fri
        5: ["Rohini", "Shravana", "Swati"] # Sat
    }
    
    if nak_name in ssy_map.get(weekday, []):
        yogas.append("Sarvartha Siddhi Yoga")
        
    # Amrit Siddhi Yoga (ASY)
    asy_map = {
        6: ["Hasta"], # Sun
        0: ["Mrigashira"], # Mon
        1: ["Ashwini"], # Tue
        2: ["Anuradha"], # Wed
        3: ["Pushya"], # Thu
        4: ["Revati"], # Fri
        5: ["Rohini"] # Sat
    }
    
    if nak_name in asy_map.get(weekday, []):
        yogas.append("Amrit Siddhi Yoga")
        
    return yogas

def get_muhurta_summary(panchanga: dict, planets: dict, weekday: int) -> dict:
    """
    Consolidates all Muhurta factors.
    """
    moon_lon = planets.get("Moon", {}).get("longitude", 0)
    nak_idx = panchanga.get("nakshatra", 1)
    karana_num = panchanga.get("karana", 1)
    
    return {
        "is_panchak": check_panchak(moon_lon),
        "is_bhadra": check_bhadra(karana_num),
        "yogas": get_muhurta_yogas(weekday, nak_idx)
    }

