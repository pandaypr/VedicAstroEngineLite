TITHI_NAMES = ["Pratipada", "Dvitiya", "Tritiya", "Chaturthi", "Panchami", "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami", "Ekadashi", "Dvadashi", "Trayodashi", "Chaturdashi", "Purnima/Amavasya"]
PAKSHA_NAMES = ["Shukla", "Krishna"]
VARA_NAMES = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
YOGA_NAMES = ["Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda", "Sukarma", "Dhriti", "Shula", "Ganda", "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra", "Siddhi", "Vyatipata", "Variyana", "Parigha", "Shiva", "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma", "Indra", "Vaidhriti"]
KARANA_NAMES = ["Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti", "Shakuni", "Chatushpada", "Naga", "Kinstughna"]
MASA_NAMES = ["Chaitra", "Vaishakha", "Jyeshtha", "Ashadha", "Shravana", "Bhadrapada", "Ashvina", "Kartika", "Margashirsha", "Pausha", "Magha", "Phalguna"]
NAKSHATRA_NAMES = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

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
    paksha = PAKSHA_NAMES[0] if tithi <= 15 else PAKSHA_NAMES[1]
    tithi_name = TITHI_NAMES[(tithi - 1) % 15]
    
    # 3. Karana (1-60)
    karana = int(diff / 6.0) + 1
    if karana == 1:
        karana_name = KARANA_NAMES[10] # Kinstughna
    elif karana == 58:
        karana_name = KARANA_NAMES[7] # Shakuni
    elif karana == 59:
        karana_name = KARANA_NAMES[8] # Chatushpada
    elif karana == 60:
        karana_name = KARANA_NAMES[9] # Naga
    else:
        karana_name = KARANA_NAMES[(karana - 2) % 7]
    
    # 4. Yoga (1-27)
    sum_lon = (moon_lon + sun_lon) % 360.0
    yoga = int(sum_lon / nak_len) + 1
    yoga_name = YOGA_NAMES[yoga - 1]
    
    return {
        "nakshatra": NAKSHATRA_NAMES[nak_index],
        "pada": pada,
        "tithi": f"{paksha} {tithi_name}",
        "karana": karana_name,
        "yoga": yoga_name
    }
