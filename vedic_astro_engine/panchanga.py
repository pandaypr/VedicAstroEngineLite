def get_panchanga(sun_lon, moon_lon):
    """
    Calculates the 5 limbs of Panchanga based on Sidereal longitudes of Sun and Moon.
    """
    nak_len = 360.0 / 27.0
    
    # 1. Nakshatra (1-27)
    nak_index = int(moon_lon / nak_len)
    nak_rem = moon_lon % nak_len
    pada = int(nak_rem / (nak_len / 4.0)) + 1
    
    # 2. Tithi (1-30)
    diff = (moon_lon - sun_lon) % 360.0
    tithi = int(diff / 12.0) + 1
    
    # 3. Karana (1-60)
    karana = int(diff / 6.0) + 1
    
    # 4. Yoga (1-27)
    sum_lon = (moon_lon + sun_lon) % 360.0
    yoga = int(sum_lon / nak_len) + 1
    
    # 5. Vaara (Weekday) - Usually calculated from the Julian day, 
    # but the API can append it at the end if the date is known.
    
    return {
        "nakshatra": nak_index + 1,
        "pada": pada,
        "tithi": tithi,
        "karana": karana,
        "yoga": yoga
    }
