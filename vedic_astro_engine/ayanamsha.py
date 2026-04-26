# ayanamsha.py - Precise Ayanamsha Calculations

# Constants for Lahiri (Chitra Paksha)
J2000_JD = 2451545.0
_AYAN_A0 = 23.857092352
_AYAN_A1 = 5028.796648
_AYAN_A2 = 1.105516

# Offsets from Lahiri at J2000
AYANAMSHA_OFFSETS = {
    "LAHIRI": 0.0,
    "RAMAN": -1.39661,         # B.V. Raman
    "KP": -0.08182,            # Krishnamurti Padhathi
    "FAGAN_BRADLEY": 0.87957,  # Fagan-Bradley
    "TROPICAL": None           # Special case, Ayanamsha = 0
}

def get_ayanamsha(jd: float, ayanamsha_type: str = "LAHIRI") -> float:
    """
    Calculates the Ayanamsha for a given Julian Date.
    Supported types: LAHIRI, RAMAN, KP, FAGAN_BRADLEY, TROPICAL.
    """
    ayan_type_upper = ayanamsha_type.upper()
    if ayan_type_upper == "TROPICAL":
        return 0.0
        
    # Calculate base Lahiri
    T = (jd - J2000_JD) / 36525.0
    lahiri = _AYAN_A0 + (_AYAN_A1 * T + _AYAN_A2 * T**2) / 3600.0
    
    # Apply offset
    offset = AYANAMSHA_OFFSETS.get(ayan_type_upper, 0.0)
    return lahiri + offset
