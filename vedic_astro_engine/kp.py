import math
from .constants import VIM_LORDS, VIM_YEARS, SIGN_OWNERS

def get_kp_lords(longitude):
    """
    Calculates the Sign Lord, Nakshatra Lord, and KP Sub-Lord for an exact sidereal longitude.
    """
    sign_idx = int(longitude / 30.0) + 1
    sign_lord = SIGN_OWNERS[sign_idx]
    
    nak_len = 360.0 / 27.0
    nak_idx = int(longitude / nak_len)
    rem_lon = longitude % nak_len
    
    nak_lord_idx = nak_idx % 9
    nak_lord = VIM_LORDS[nak_lord_idx]
    
    current_lon = 0.0
    sub_lord = None
    sub_lord_idx = 0
    
    for i in range(9):
        idx = (nak_lord_idx + i) % 9
        sub_len = (VIM_YEARS[idx] / 120.0) * nak_len
        
        # Avoid floating point precision issues at the exact boundary
        if current_lon <= rem_lon < current_lon + sub_len + 1e-9:
            sub_lord = VIM_LORDS[idx]
            sub_lord_idx = idx
            break
        current_lon += sub_len
        
    # Optional: Sub-Sub Lord (for extremely fine precision)
    current_sub_lon = 0.0
    rem_sub_lon = rem_lon - current_lon
    sub_sub_lord = None
    for i in range(9):
        idx = (sub_lord_idx + i) % 9
        sub_sub_len = (VIM_YEARS[idx] / 120.0) * sub_len
        if current_sub_lon <= rem_sub_lon < current_sub_lon + sub_sub_len + 1e-9:
            sub_sub_lord = VIM_LORDS[idx]
            break
        current_sub_lon += sub_sub_len
        
    return {
        "sign_lord": sign_lord,
        "nakshatra_lord": nak_lord,
        "sub_lord": sub_lord,
        "sub_sub_lord": sub_sub_lord
    }

def get_placidus_cusps(ramc_deg, eps_rad, lat_rad, asc_deg, mc_deg):
    """
    Iterative calculation of Placidus houses.
    Since Placidus divides the semi-arc (time), not space, it requires iteration.
    """
    ramc_rad = math.radians(ramc_deg)
    
    def calculate_cusp(ramc_offset, fraction):
        # Initial guess is the RAMC offset on the equator
        ra = ramc_rad + math.radians(ramc_offset)
        
        for _ in range(15): # 15 iterations is usually enough for convergence
            # Declination of the point on the ecliptic at this RA
            sin_d = math.sin(eps_rad) * math.sin(ra)
            d = math.asin(sin_d)
            
            # Ascensional difference
            val = math.tan(lat_rad) * math.tan(d)
            val = max(-1.0, min(1.0, val)) # Clamp to valid range
            asc_diff = math.asin(val)
            
            # Update RA
            new_ra = ramc_rad + math.radians(ramc_offset) + fraction * asc_diff
            
            if abs(new_ra - ra) < 1e-6:
                break
            ra = new_ra
            
        # Convert RA to Ecliptic Longitude
        y = math.sin(ra) * math.cos(eps_rad) + math.tan(d) * math.sin(eps_rad)
        x = math.cos(ra)
        lon = math.degrees(math.atan2(y, x)) % 360.0
        return lon

    # Cusp 11 and 12
    c11 = calculate_cusp(30.0, 1.0/3.0)
    c12 = calculate_cusp(60.0, 2.0/3.0)
    
    # Cusp 2 and 3
    c2 = calculate_cusp(120.0, 2.0/3.0)
    c3 = calculate_cusp(150.0, 1.0/3.0)
    
    cusps = [0] * 12
    cusps[0] = asc_deg
    cusps[1] = c2
    cusps[2] = c3
    cusps[3] = (mc_deg + 180.0) % 360.0 # IC
    cusps[4] = (c11 + 180.0) % 360.0
    cusps[5] = (c12 + 180.0) % 360.0
    cusps[6] = (asc_deg + 180.0) % 360.0 # DC
    cusps[7] = (c2 + 180.0) % 360.0
    cusps[8] = (c3 + 180.0) % 360.0
    cusps[9] = mc_deg # MC
    cusps[10] = c11
    cusps[11] = c12
    
    return cusps
