import math
from datetime import datetime

def calculate_special_lagnas(sun_lon_sunrise, lagna_lon, sunrise_dt, current_dt):
    """
    Calculates Bhava, Hora, Ghati, and Vighati Lagnas.
    Time difference is calculated in minutes from Sunrise.
    """
    diff_minutes = (current_dt - sunrise_dt).total_seconds() / 60.0
    
    # Bhava Lagna: Advances 30 degrees every 120 minutes (0.25 deg/min)
    bhava = (sun_lon_sunrise + diff_minutes * 0.25) % 360.0
    
    # Hora Lagna: Advances 30 degrees every 60 minutes (0.5 deg/min)
    hora = (sun_lon_sunrise + diff_minutes * 0.5) % 360.0
    
    # Ghati Lagna: Advances 30 degrees every 24 minutes (1.25 deg/min)
    ghati = (sun_lon_sunrise + diff_minutes * 1.25) % 360.0
    
    # Vighati Lagna: Advances 30 degrees every 0.4 minutes (24 seconds) (75 deg/min)
    vighati = (sun_lon_sunrise + diff_minutes * 75.0) % 360.0
    
    # Pranapada Lagna: 
    # Advances 1 Rashi per 15 Vighatis (6 mins). Velocity = 5 deg/min
    # Starts from Sun if Movable, 9th from Sun if Fixed, 5th from Sun if Dual
    sun_sign_idx = int(sun_lon_sunrise / 30)
    if sun_sign_idx % 3 == 0: # Movable
        pranapada_start = sun_lon_sunrise
    elif sun_sign_idx % 3 == 1: # Fixed
        pranapada_start = (sun_lon_sunrise + 240.0) % 360.0
    else: # Dual
        pranapada_start = (sun_lon_sunrise + 120.0) % 360.0
    pranapada = (pranapada_start + diff_minutes * 5.0) % 360.0

    return {
        "Bhava Lagna": bhava,
        "Hora Lagna": hora,
        "Ghati Lagna": ghati,
        "Vighati Lagna": vighati,
        "Pranapada Lagna": pranapada
    }

def calculate_upagrahas(sun_lon):
    """
    Calculates non-luminous mathematical points (Upagrahas).
    """
    dhooma = (sun_lon + 133.333333) % 360.0 # 133 deg 20 min
    vyatipata = (360.0 - dhooma) % 360.0
    parivesha = (vyatipata + 180.0) % 360.0
    indrachapa = (360.0 - parivesha) % 360.0
    upaketu = (indrachapa + 16.666667) % 360.0 # 16 deg 40 min
    
    return {
        "Dhooma": dhooma,
        "Vyatipata": vyatipata,
        "Parivesha": parivesha,
        "Indra Chapa": indrachapa,
        "Upaketu": upaketu
    }

def calculate_sphutas(planets, lagna, mandi_lon):
    """
    Calculates various mathematical Sphutas (points).
    """
    sun = planets.get("Sun", 0)
    moon = planets.get("Moon", 0)
    mars = planets.get("Mars", 0)
    jup = planets.get("Jupiter", 0)
    ven = planets.get("Venus", 0)
    rahu = planets.get("Rahu", 0)
    gulika = planets.get("Gulika", mandi_lon) # Fallback to Mandi if Gulika not provided

    bhrigu_bindu = (moon + rahu) / 2.0
    
    beeja = (sun + ven + jup) % 360.0
    kshetra = (moon + mars + jup) % 360.0
    
    tithi_sphuta = (moon - sun) % 360.0
    if tithi_sphuta < 0: tithi_sphuta += 360.0
    
    yoga_sphuta = (moon + sun) % 360.0
    rahu_tithi_sphuta = (moon - sun + rahu) % 360.0
    
    prana_sphuta = (lagna * 5 + mandi_lon) % 360.0
    deha_sphuta = (moon * 8 + mandi_lon) % 360.0
    mrityu_sphuta = (mandi_lon * 7 + sun) % 360.0
    sookshma_trisphuta = (prana_sphuta + deha_sphuta + mrityu_sphuta) % 360.0
    
    trisphuta = (lagna + moon + gulika) % 360.0
    chatussphuta = (trisphuta + sun) % 360.0
    panchasphuta = (chatussphuta + rahu) % 360.0
    
    return {
        "Bhrigu Bindu": bhrigu_bindu,
        "Beeja Sphuta": beeja,
        "Kshetra Sphuta": kshetra,
        "Tithi Sphuta": tithi_sphuta,
        "Yoga Sphuta": yoga_sphuta,
        "Rahu Tithi Sphuta": rahu_tithi_sphuta,
        "Prana Sphuta": prana_sphuta,
        "Deha Sphuta": deha_sphuta,
        "Mrityu Sphuta": mrityu_sphuta,
        "Sookshma TriSphuta": sookshma_trisphuta,
        "TriSphuta": trisphuta,
        "ChatusSphuta": chatussphuta,
        "PanchaSphuta": panchasphuta
    }

def calculate_time_upagrahas(sunrise_dt, sunset_dt, current_dt, lat, lon_deg):
    """
    Approximates Gulika, Mandi, Kaala, Mrityu, Artha Prahara, Yama Ghantaka 
    longitudes based on proportional time passed in their respective Muhurtas.
    Since we don't have a continuous Ascendant function in this scope, 
    we return the start times of these portions. The main engine will calculate 
    the Lagna at these exact times.
    """
    is_day = sunrise_dt <= current_dt < sunset_dt
    
    if is_day:
        duration = (sunset_dt - sunrise_dt).total_seconds()
        start_time = sunrise_dt
    else:
        # Night calculation requires next sunrise
        duration = 24 * 3600 - (sunset_dt - sunrise_dt).total_seconds() # Approx
        start_time = sunset_dt
        
    muhurta = duration / 8.0
    weekday = start_time.weekday() # 0=Monday, 6=Sunday
    
    # 1-indexed parts for daytime
    # Planets: Sun, Moon, Mars, Mer, Jup, Ven, Sat
    # Order: Sun(Sun), Moon(Mon), Mars(Tue), Mer(Wed), Jup(Thu), Ven(Fri), Sat(Sat)
    # Gulika = Saturn's part
    # Yama Ghantaka = Jupiter's part
    # Artha Prahara = Mercury's part
    # Kaala = Sun's part
    # Mrityu = Mars' part
    # Mandi is slightly before Gulika.
    
    day_parts = {
        "Kaala":      {0: 2, 1: 7, 2: 5, 3: 6, 4: 4, 5: 3, 6: 8}, # Sun
        "Mrityu":     {0: 7, 1: 5, 2: 6, 3: 4, 4: 3, 5: 8, 6: 2}, # Mars
        "Artha":      {0: 5, 1: 6, 2: 4, 3: 3, 4: 8, 5: 2, 6: 7}, # Mercury
        "Yama":       {0: 6, 1: 4, 2: 3, 3: 8, 4: 2, 5: 7, 6: 5}, # Jupiter
        "Gulika":     {0: 6, 1: 5, 2: 4, 3: 3, 4: 2, 5: 1, 6: 7}, # Saturn
        "Mandi":      {0: 5, 1: 4, 2: 3, 3: 2, 4: 1, 5: 7, 6: 6}  # Mandi
    }
    
    # Night parts start from the 5th lord from the day lord
    night_parts = {
        "Kaala":      {0: 4, 1: 3, 2: 8, 3: 2, 4: 7, 5: 5, 6: 6}, 
        "Mrityu":     {0: 3, 1: 8, 2: 2, 3: 7, 4: 5, 5: 6, 6: 4}, 
        "Artha":      {0: 8, 1: 2, 2: 7, 3: 5, 4: 6, 5: 4, 6: 3}, 
        "Yama":       {0: 2, 1: 7, 2: 5, 3: 6, 4: 4, 5: 3, 6: 8}, 
        "Gulika":     {0: 2, 1: 1, 2: 7, 3: 6, 4: 5, 5: 4, 6: 3}, 
        "Mandi":      {0: 1, 1: 7, 2: 6, 3: 5, 4: 4, 5: 3, 6: 2}  
    }
    
    active_parts = day_parts if is_day else night_parts
    
    times = {}
    for name, parts in active_parts.items():
        part_idx = parts.get(weekday, 1) - 1
        # The rising degree (Lagna) at the START of this part is the longitude
        times[name] = start_time.timestamp() + (part_idx * muhurta)
        
    return times
