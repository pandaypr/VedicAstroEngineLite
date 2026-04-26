from datetime import timedelta, datetime
from .constants import VIM_LORDS, VIM_YEARS, SIGNS as SIGN_NAMES, SIGN_OWNERS as LORDS

# Vimshottari
VIM_TOTAL = 120.0

# Yogini
YOG_NAMES = ["Mangala", "Pingala", "Dhanya", "Bhramari", "Bhadrika", "Ulka", "Siddha", "Sankata"]
YOG_YEARS = [1, 2, 3, 4, 5, 6, 7, 8]

def _calc_vim_levels(start_date, total_years, lord_idx, current_depth, max_depth, birth_date, now=None):
    """
    Recursively computes Vimshottari sub-periods.
    For depth >= 3 (Sookshma and deeper), only expands the ACTIVE period
    to avoid the 9^N combinatorial explosion.
    """
    if current_depth > max_depth:
        return []
    
    if now is None:
        now = datetime.now(birth_date.tzinfo)
    
    sub_periods = []
    curr_start = start_date
    
    # child_keys maps the CHILD depth to the JSON key name
    child_keys = {
        2: "pratyantardashas",
        3: "sookshmadashas",
        4: "praanadashas",
        5: "dehadashas"
    }
    
    for i in range(9):
        sub_idx = (lord_idx + i) % 9
        sub_years = (total_years * VIM_YEARS[sub_idx]) / VIM_TOTAL
        sub_end = curr_start + timedelta(days=sub_years * 365.2425)
        
        if sub_end > birth_date:
            period = {
                "lord": VIM_LORDS[sub_idx],
                "start": max(curr_start, birth_date).isoformat(),
                "end": sub_end.isoformat()
            }
            # For depth 2 (AD), expand all PDs.
            # For depth 3+ (Sookshma, Praana, Deha), only expand ACTIVE period.
            child_depth = current_depth + 1
            should_expand = False
            if child_depth <= max_depth:
                if current_depth <= 2:  # We're generating PD or deeper from AD/PD level
                    should_expand = True
                else:
                    should_expand = (curr_start <= now <= sub_end)
            
            if should_expand:
                children = _calc_vim_levels(curr_start, sub_years, sub_idx, child_depth, max_depth, birth_date, now)
                if children and child_depth in child_keys:
                    period[child_keys[child_depth]] = children
            sub_periods.append(period)
            
        curr_start = sub_end
        
    return sub_periods

def get_vimshottari_dasha(moon_lon, birth_date_utc_str, max_depth=4):
    """
    Calculates the Vimshottari Dasha periods recursively.
    max_depth controls how deep the tree goes:
    0 = Mahadasha only
    1 = Antardasha (AD)
    2 = Pratyantar Dasha (PD)
    3 = Sookshma Dasha (SD)
    4 = Praanadasha (PrD)
    5 = Dehadasha (DD)
    """
    try:
        birth_date = datetime.fromisoformat(birth_date_utc_str.replace('Z', '+00:00'))
    except Exception:
        birth_date = datetime.now()
        
    nak_len = 360.0 / 27.0
    nak_exact = moon_lon / nak_len
    nak_idx = int(nak_exact)
    fraction_elapsed = nak_exact - nak_idx
    fraction_remaining = 1.0 - fraction_elapsed
    
    start_lord_idx = nak_idx % 9
    
    periods = []
    current_date = birth_date
    
    first_md_total_years = VIM_YEARS[start_lord_idx]
    first_md_remaining_years = first_md_total_years * fraction_remaining
    
    md_start_date = current_date - timedelta(days=(first_md_total_years - first_md_remaining_years) * 365.2425)
    
    # Use a consistent 'now' with timezone awareness matching birth_date
    now = datetime.now(birth_date.tzinfo)
    
    loop_start_date = md_start_date
    for md_count in range(9):
        md_idx = (start_lord_idx + md_count) % 9
        md_years = VIM_YEARS[md_idx]
        md_end_date = loop_start_date + timedelta(days=md_years * 365.2425)
        
        if md_end_date > birth_date:
            md_obj = {
                "lord": VIM_LORDS[md_idx],
                "start": max(loop_start_date, birth_date).isoformat(),
                "end": md_end_date.isoformat()
            }
            if max_depth > 0:
                children = _calc_vim_levels(loop_start_date, md_years, md_idx, 1, max_depth, birth_date, now)
                if children:
                    md_obj["antardashas"] = children
            periods.append(md_obj)
            
        loop_start_date = md_end_date
        
    return periods

def get_chara_dasha(asc_sign_num, planet_signs, birth_date_utc_str):
    """
    Calculates Jaimini Chara Dasha (Basic Parashara/K.N. Rao rules).
    asc_sign_num: 1 to 12 (Aries to Pisces).
    planet_signs: dict mapping planet names to their sign_num (1-12).
    """
    try:
        birth_date = datetime.fromisoformat(birth_date_utc_str.replace('Z', '+00:00'))
    except Exception:
        birth_date = datetime.now()
        
    # Standard K.N. Rao sequences
    # Forward: Ar, Le, Vi, Li, Aq, Pi
    # Reverse: Ta, Ge, Ca, Sc, Sg, Cp
    forward_signs = {1, 5, 6, 7, 11, 12}
    is_forward = asc_sign_num in forward_signs
    
    forward_signs = {1, 5, 6, 7, 11, 12}
    is_forward = asc_sign_num in forward_signs
    
    sequence = []
    if is_forward:
        for i in range(12):
            sequence.append((asc_sign_num - 1 + i) % 12 + 1)
    else:
        for i in range(12):
            sequence.append((asc_sign_num - 1 - i) % 12 + 1)
            if sequence[-1] <= 0: sequence[-1] += 12
            
    periods = []
    current_date = birth_date
    
    for sign in sequence:
        lord = LORDS[sign]
        lord_sign = planet_signs.get(lord, sign)
        
        # Duration: count from sign to lord_sign
        # Forward or Reverse based on the current dasha sign
        dasha_is_forward = sign in forward_signs
        
        if lord_sign == sign:
            duration = 12
        else:
            if dasha_is_forward:
                duration = (lord_sign - sign) % 12
            else:
                duration = (sign - lord_sign) % 12
                
            if duration == 0: duration = 12 # shouldn't happen due to lord_sign == sign check above, but safe
            
        end_date = current_date + timedelta(days=duration * 365.2425)
        periods.append({
            "sign": SIGN_NAMES[sign - 1],
            "duration_years": duration,
            "start": current_date.isoformat(),
            "end": end_date.isoformat()
        })
        current_date = end_date
        
    return periods

def get_yogini_dasha(moon_lon, birth_date_utc_str):
    """
    Calculates the Yogini Dasha 36-year cycle.
    """
    try:
        birth_date = datetime.fromisoformat(birth_date_utc_str.replace('Z', '+00:00'))
    except Exception:
        birth_date = datetime.now()
        
    nak_len = 360.0 / 27.0
    nak_exact = moon_lon / nak_len
    nak_idx = int(nak_exact)
    
    fraction_elapsed = nak_exact - nak_idx
    fraction_remaining = 1.0 - fraction_elapsed
    
    # Formula: (Nakshatra number + 3) / 8
    # Nakshatra number is 1-based.
    nak_num = nak_idx + 1
    start_idx = (nak_num + 3) % 8 - 1
    if start_idx < 0:
        start_idx += 8
        
    start_years = YOG_YEARS[start_idx]
    years_remaining = start_years * fraction_remaining
    
    periods = []
    current_date = birth_date
    end_date = current_date + timedelta(days=years_remaining * 365.2425)
    
    periods.append({
        "yogini": YOG_NAMES[start_idx],
        "start": current_date.isoformat(),
        "end": end_date.isoformat()
    })
    
    current_date = end_date
    curr_idx = (start_idx + 1) % 8
    
    for _ in range(8):
        end_date = current_date + timedelta(days=YOG_YEARS[curr_idx] * 365.2425)
        periods.append({
            "yogini": YOG_NAMES[curr_idx],
            "start": current_date.isoformat(),
            "end": end_date.isoformat()
        })
        current_date = end_date
        curr_idx = (curr_idx + 1) % 8
        
    return periods

# Kaal Chakra Dasha Logic
KCD_YEARS = {1: 7, 2: 16, 3: 9, 4: 21, 5: 5, 6: 9, 7: 16, 8: 7, 9: 10, 10: 4, 11: 4, 12: 10}

KCD_SAVYA_SEQS = [
    [1, 2, 3, 4, 5, 6, 7, 8, 9],       # 1
    [10, 11, 12, 8, 7, 6, 4, 5, 3],    # 2
    [2, 1, 12, 11, 10, 9, 1, 2, 3],    # 3
    [4, 5, 6, 7, 8, 9, 10, 11, 12],    # 4
    [8, 7, 6, 4, 5, 3, 2, 1, 12],      # 5
    [11, 10, 9, 1, 2, 3, 4, 5, 6],     # 6
    [7, 8, 9, 10, 11, 12, 8, 7, 6],    # 7
    [4, 5, 3, 2, 1, 12, 11, 10, 9],    # 8
    [1, 2, 3, 4, 5, 6, 7, 8, 9],       # 9
    [10, 11, 12, 8, 7, 6, 4, 5, 3],    # 10
    [2, 1, 12, 11, 10, 9, 1, 2, 3],    # 11
    [4, 5, 6, 7, 8, 9, 10, 11, 12]     # 12
]

def get_kaal_chakra_dasha(moon_lon, birth_date_utc_str):
    """
    Calculates the Kaal Chakra Dasha.
    """
    try:
        birth_date = datetime.fromisoformat(birth_date_utc_str.replace('Z', '+00:00'))
    except Exception:
        birth_date = datetime.now()
        
    nak_len = 360.0 / 27.0
    nak_exact = moon_lon / nak_len
    nak_idx = int(nak_exact)
    
    fraction_elapsed = nak_exact - nak_idx
    pada_num = int(fraction_elapsed * 4) # 0, 1, 2, 3
    pada_fraction = (fraction_elapsed * 4.0) - pada_num
    pada_fraction_remaining = 1.0 - pada_fraction
    
    # Savya or Apasavya
    group_idx = nak_idx // 3
    is_savya = (group_idx % 2) == 0
    
    seq_idx = (nak_idx % 3) * 4 + pada_num
    
    if is_savya:
        sequence = KCD_SAVYA_SEQS[seq_idx]
    else:
        # Apasavya is exactly the reverse of Savya
        sequence = list(reversed(KCD_SAVYA_SEQS[seq_idx]))
        
    total_cycle_years = sum(KCD_YEARS[s] for s in sequence)
    
    SIGN_NAMES = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    
    # Calculate starting point within the first dasha
    # Standard KCD uses proportional years for the first dasha
    first_sign = sequence[0]
    first_dasha_years = KCD_YEARS[first_sign]
    
    # In KCD, the fraction remaining of the *entire cycle* is sometimes used, 
    # but the exact method uses the fraction of the pada mapped to the sequence.
    # The elapsed time in the pada determines where in the cycle we start.
    elapsed_years_in_cycle = total_cycle_years * pada_fraction
    
    current_years = 0.0
    start_seq_idx = 0
    dasha_years_remaining = 0.0
    
    for i, s in enumerate(sequence):
        s_years = KCD_YEARS[s]
        if current_years + s_years > elapsed_years_in_cycle:
            start_seq_idx = i
            dasha_years_remaining = (current_years + s_years) - elapsed_years_in_cycle
            break
        current_years += s_years
        
    periods = []
    current_date = birth_date
    
    # First partial period
    end_date = current_date + timedelta(days=dasha_years_remaining * 365.2425)
    periods.append({
        "sign": SIGN_NAMES[sequence[start_seq_idx] - 1],
        "duration_years": round(dasha_years_remaining, 2),
        "start": current_date.isoformat(),
        "end": end_date.isoformat()
    })
    current_date = end_date
    
    # Remaining periods (and a second cycle to ensure "full output")
    for _cycle in range(2):
        for i in range(start_seq_idx + 1 if _cycle == 0 else 0, len(sequence)):
            s = sequence[i]
            s_years = KCD_YEARS[s]
            end_date = current_date + timedelta(days=s_years * 365.2425)
            periods.append({
                "sign": SIGN_NAMES[s - 1],
                "duration_years": s_years,
                "start": current_date.isoformat(),
                "end": end_date.isoformat()
            })
            current_date = end_date
            
    return periods
