from .constants import SIGN_OWNERS
from .shadbala import ShadbalaCalculator

# Shodashavarga Weights (Standard BPHS)
VIM_WEIGHTS = {
    "D1": 3.5, "D2": 1.0, "D3": 1.0, "D4": 0.5, "D7": 0.5, "D9": 3.0,
    "D10": 0.5, "D12": 0.5, "D16": 2.0, "D20": 0.5, "D24": 0.5, "D27": 0.5,
    "D30": 1.0, "D40": 0.5, "D45": 0.5, "D60": 4.0
}

# Vimsopaka status scores (out of 20)
# Swakshetra (Own) = 15, Mitra (Friend) = 10... 
# Actually BPHS: Swavarga=20, Adhimitra=18, Mitra=15, Sama=10, Shatru=7, Adhishatru=5
STATUS_SCORES = {
    "exalt": 20,
    "mool": 18,
    "own": 15,
    "adhimitra": 13,
    "mitra": 10,
    "sama": 7,
    "shatru": 4,
    "adhishatru": 2,
    "debil": 0
}

def get_vimsopaka_bala(planet, planets_data):
    """
    Calculates Vimsopaka Bala (strength in 16 divisional charts).
    """
    p_info = planets_data.get(planet, {})
    vargas = p_info.get("vargas", {})
    if not vargas:
        return 0.0

    # 1. Determine Temporal Relationships (Tatkalika Maitri)
    # Based on D1 positions
    p_house = p_info.get("house", 1)
    tatkalika = {}
    for other_p, other_info in planets_data.items():
        if other_p == planet or other_p in ["Rahu", "Ketu", "Uranus", "Neptune", "Pluto"]:
            continue
        oh = other_info.get("house", 1)
        diff = (oh - p_house) % 12
        if diff in [1, 2, 3, 9, 10, 11]: # 2,3,4,10,11,12 from self
            tatkalika[other_p] = 1 # Friend
        else:
            tatkalika[other_p] = -1 # Enemy

    total_score = 0.0
    for v_key, weight in VIM_WEIGHTS.items():
        sign_idx = vargas.get(v_key)
        if sign_idx is None: continue
        
        owner = SIGN_OWNERS[sign_idx + 1]
        
        # Determine relationship
        if owner == planet:
            status = "own"
        else:
            perm = ShadbalaCalculator.PERMANENT_MAITRI.get(planet, {}).get(owner, 0)
            temp = tatkalika.get(owner, 0)
            combined = perm + temp
            if combined == 2: status = "adhimitra"
            elif combined == 1: status = "mitra"
            elif combined == 0: status = "sama"
            elif combined == -1: status = "shatru"
            else: status = "adhishatru"
            
        # Check Exaltation/Debilitation (Simplified for Vimsopaka)
        # Usually Vimsopaka is just based on Varga status, 
        # but some include Exaltation as a boost.
        
        score = STATUS_SCORES.get(status, 7)
        total_score += (score / 20.0) * weight
        
    return round(total_score, 2)
