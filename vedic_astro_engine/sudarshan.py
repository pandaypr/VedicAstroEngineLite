"""
sudarshan.py — The Triple-Perspective Wheel

Implements:
1. Lagna-based house analysis
2. Chandra (Moon)-based house analysis
3. Surya (Sun)-based house analysis
4. Aggregated house strength calculation

Sources: Brihat Parasara Hora Shastra
"""

from .utils import _house_of

def calculate_sudarshan_chakra(planet_lons: dict, lagna_lon: float) -> dict:
    """
    Analyzes houses 1-12 from Lagna, Moon, and Sun.
    Returns a unified view and house strength scores.
    """
    moon_lon = planet_lons.get("Moon")
    sun_lon = planet_lons.get("Sun")
    
    if moon_lon is None or sun_lon is None:
        return {}
    
    results = {}
    MALEFICS = {"Mars", "Saturn", "Sun", "Rahu", "Ketu"}
    BENEFICS = {"Jupiter", "Venus", "Mercury", "Moon"}

    for h_num in range(1, 13):
        # Planets in house 'h_num' from Lagna
        in_lagna = [p for p, lon in planet_lons.items() if _house_of(lon, lagna_lon) == h_num]
        in_moon  = [p for p, lon in planet_lons.items() if _house_of(lon, moon_lon) == h_num]
        in_sun   = [p for p, lon in planet_lons.items() if _house_of(lon, sun_lon) == h_num]
        
        # Combined Strength Score
        # Rule: Benefics in house add strength, malefics reduce it.
        # If a house is occupied from multiple perspectives, its influence is tripled.
        score = 0
        all_planets = set(in_lagna) | set(in_moon) | set(in_sun)
        for p in all_planets:
            weight = 1
            if p in BENEFICS: score += weight
            if p in MALEFICS: score -= weight
            
        results[h_num] = {
            "from_lagna": in_lagna,
            "from_moon": in_moon,
            "from_sun": in_sun,
            "strength_score": score,
            "status": "Strong" if score > 1 else "Weak" if score < -1 else "Neutral"
        }
        
    return results
