from datetime import datetime, timedelta

def calculate_kaals(sunrise_iso, sunset_iso, weekday_index):
    """
    Calculates Rahu Kaal and Gulika Kaal for a given day.
    sunrise_iso: str, ISO format string of sunrise time.
    sunset_iso: str, ISO format string of sunset time.
    weekday_index: int, 0=Monday, 6=Sunday (Python datetime.weekday() standard).
    """
    if not sunrise_iso or not sunset_iso:
        return {}
        
    try:
        sr = datetime.fromisoformat(sunrise_iso.replace('Z', '+00:00'))
        ss = datetime.fromisoformat(sunset_iso.replace('Z', '+00:00'))
    except Exception:
        return {}
        
    daytime_duration = ss - sr
    if daytime_duration.total_seconds() < 0:
        # UTC crossover: sr is the next day's sunrise
        sr = sr - timedelta(days=1)
        daytime_duration = ss - sr
        
    muhurta_len = daytime_duration / 8.0
    
    # Rahu Kaal 1-indexed parts (out of 8)
    # Mon: 2, Tue: 7, Wed: 5, Thu: 6, Fri: 4, Sat: 3, Sun: 8
    rahu_parts = {0: 2, 1: 7, 2: 5, 3: 6, 4: 4, 5: 3, 6: 8}
    
    # Gulika Kaal 1-indexed parts (out of 8)
    # Mon: 6, Tue: 5, Wed: 4, Thu: 3, Fri: 2, Sat: 1, Sun: 7
    gulika_parts = {0: 6, 1: 5, 2: 4, 3: 3, 4: 2, 5: 1, 6: 7}
    
    # Yamaganda Kaal 1-indexed parts (out of 8)
    # Mon: 5, Tue: 4, Wed: 3, Thu: 2, Fri: 1, Sat: 7, Sun: 6
    yamaganda_parts = {0: 5, 1: 4, 2: 3, 3: 2, 4: 1, 5: 7, 6: 6}
    
    r_part = rahu_parts.get(weekday_index, 8)
    g_part = gulika_parts.get(weekday_index, 7)
    y_part = yamaganda_parts.get(weekday_index, 6)
    
    rahu_start = sr + muhurta_len * (r_part - 1)
    rahu_end = rahu_start + muhurta_len
    
    gulika_start = sr + muhurta_len * (g_part - 1)
    gulika_end = gulika_start + muhurta_len

    yamaganda_start = sr + muhurta_len * (y_part - 1)
    yamaganda_end = yamaganda_start + muhurta_len
    
    return {
        "Rahu_Kaal": {
            "start": rahu_start.isoformat(),
            "end": rahu_end.isoformat()
        },
        "Gulika_Kaal": {
            "start": gulika_start.isoformat(),
            "end": gulika_end.isoformat()
        },
        "Yamaganda_Kaal": {
            "start": yamaganda_start.isoformat(),
            "end": yamaganda_end.isoformat()
        }
    }

