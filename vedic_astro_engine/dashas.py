from datetime import timedelta, datetime
from .constants import VIM_LORDS, VIM_YEARS

# Vimshottari
VIM_TOTAL = 120.0

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
