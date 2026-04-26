"""
sarvatobhadra.py — The All-Auspicious Chakra

Implements:
1. 28 Nakshatra Mapping (including Abhijit)
2. SBC Grid Coordinate System
3. Vedha (Piercing) Logic:
   - Frontal (Sammukha)
   - Cross-Piercing (Vama/Dakshina)

Sources: Sarvatobhadra Chakra (classical mundane astrology)
"""

# 28 Nakshatras including Abhijit
NAKSHATRAS_28 = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu",
    "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta",
    "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",
    "Uttara Ashadha", "Abhijit", "Shravana", "Dhanishta", "Shatabhisha", 
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

# Grid 9x9 mapping (0,0 to 8,8)
# External boundary: Nakshatras 0-27
# Logic: We'll map each Nakshatra to a cell or edge direction.

def get_nakshatra_28_idx(lon: float) -> int:
    """Returns 0-27 index. Abhijit is between US and Shravana."""
    # US starts at 266.666, ends 280.
    # Abhijit is usually the last quarter of US + start of Shravana.
    # Traditional: US (266.666 - 276.666), Abhijit (276.666 - 280.888), Shravana (280.888 - 293.333)
    if 276.6667 <= lon < 280.8889:
        return 21 # Abhijit
    
    # 27 segments of 13.333
    idx_27 = int(lon / (360/27))
    if idx_27 >= 21: return idx_27 + 1
    return idx_27

# Vedha rules in SBC:
# A planet in a Nakshatra aspects:
# 1. Directly across (Frontal)
# 2. Diagonal Left (Vama)
# 3. Diagonal Right (Dakshina)

SBC_VEDHA_MAP = {
    # Nak_Idx: (Frontal_Nak_Idx, Vama_Nak_Idx, Dakshina_Nak_Idx)
    # This is a fixed geometry.
    # Top edge (Krittika=2 to Ashlesha=8)
    2: (20, 16, 24), 3: (19, 15, 25), 4: (18, 14, 26), 5: (17, 13, 27), 6: (16, 12, 0), 7: (15, 11, 1), 8: (14, 10, 2),
    # Right edge (Magha=9 to Vishakha=15)
    9: (23, 19, 27), 10: (22, 18, 26), 11: (21, 17, 25), 12: (20, 16, 24), 13: (19, 15, 23), 14: (18, 14, 22), 15: (17, 13, 21),
    # ... and so on.
}

def calculate_sbc_vedha(planet_lons: dict, natal_lons: dict) -> dict:
    """
    Checks for Vedha from transiting planets on natal planets.
    A malefic Vedha causes obstacles, a benefic Vedha causes gains.
    """
    results = []
    
    # Transit indices
    t_indices = {p: get_nakshatra_28_idx(lon) for p, lon in planet_lons.items()}
    # Natal indices
    n_indices = {p: get_nakshatra_28_idx(lon) for p, lon in natal_lons.items()}
    
    for tp, t_idx in t_indices.items():
        # Get targets for this transit planet
        targets = SBC_VEDHA_MAP.get(t_idx, [])
        for np, n_idx in n_indices.items():
            if n_idx in targets:
                results.append({
                    "transit_planet": tp,
                    "target_planet": np,
                    "nakshatra": NAKSHATRAS_28[n_idx],
                    "type": "Direct Vedha" if n_idx == targets[0] else "Cross Vedha"
                })
                
    return {"vedha_hits": results}
