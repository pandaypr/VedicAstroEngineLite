"""
festivals.py — Festival Calendar, Lunar Months, and Choghadiya

Implements:
1. Lunar Month Calendar (Amanta & Purnimanta)
2. Tithi-based Festival Detection (20+ festivals)
3. Choghadiya (8 daily time slots for auspiciousness)

Mathematical Basis:
- Tithi  = (Moon_lon - Sun_lon) / 12, gives 1-30
- Lunar Month = determined by the Sun's sidereal sign at New Moon
- Choghadiya = day divided into 8 equal parts from sunrise to sunset

Sources: BPHS, Muhurta Chintamani, Panchangam traditions
"""

import math
from datetime import datetime, timedelta, timezone
from .core import load_ephemeris
from .ayanamsha import get_ayanamsha

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

SIGN_NAMES = [
    "Aries","Taurus","Gemini","Cancer","Leo","Virgo",
    "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"
]

# Lunar month names (Amanta system — month ends on New Moon)
# The month is named after the Nakshatra of the Full Moon in that month
AMANTA_MONTHS = [
    "Chaitra",     # Sun in Pisces → Full Moon near Chitra nakshatra
    "Vaishakha",   # Sun in Aries
    "Jyeshtha",    # Sun in Taurus
    "Ashadha",     # Sun in Gemini
    "Shravana",    # Sun in Cancer
    "Bhadrapada",  # Sun in Leo
    "Ashwin",      # Sun in Virgo
    "Kartika",     # Sun in Libra
    "Margashirsha",# Sun in Scorpio
    "Pausha",      # Sun in Sagittarius
    "Magha",       # Sun in Capricorn
    "Phalguna",    # Sun in Aquarius
]

TITHI_NAMES = [
    "Pratipada","Dwitiya","Tritiya","Chaturthi","Panchami","Shashti","Saptami",
    "Ashtami","Navami","Dashami","Ekadashi","Dwadashi","Trayodashi","Chaturdashi",
    "Purnima",
    "Pratipada","Dwitiya","Tritiya","Chaturthi","Panchami","Shashti","Saptami",
    "Ashtami","Navami","Dashami","Ekadashi","Dwadashi","Trayodashi","Chaturdashi",
    "Amavasya"
]

# Choghadiya names, nature, and suitability
# Day sequence starting from Sunday: Udvega, Chara, Labha, Amrit, Kaal, Shubh, Rog, Udvega
# Each weekday shifts the starting slot
CHOGHADIYA_NAMES = ["Udvega","Chara","Labha","Amrit","Kaal","Shubh","Rog","Udvega"]
CHOGHADIYA_NATURE = {
    "Udvega": "Malefic",
    "Chara":  "Benefic",
    "Labha":  "Benefic",
    "Amrit":  "Benefic",
    "Kaal":   "Malefic",
    "Shubh":  "Benefic",
    "Rog":    "Malefic",
}
CHOGHADIYA_SUITABILITY = {
    "Udvega": "Avoid — causes anxiety and obstacles",
    "Chara":  "Good for travel and movement",
    "Labha":  "Excellent for business and gains",
    "Amrit":  "Best — auspicious for all activities",
    "Kaal":   "Avoid — inauspicious, causes delays",
    "Shubh":  "Good for marriages and auspicious events",
    "Rog":    "Avoid — causes disease and conflict",
}
# Weekday index: 0=Sun, 1=Mon, 2=Tue, 3=Wed, 4=Thu, 5=Fri, 6=Sat
# Day Choghadiya start offset (which slot index is first for each weekday)
# For day: Sun=0(Udvega),Mon=2(Labha),Tue=6(Rog),Wed=5(Shubh),Thu=4(Kaal),Fri=3(Amrit),Sat=1(Chara)
DAY_CHOGHADIYA_START = {0: 0, 1: 2, 2: 6, 3: 5, 4: 4, 5: 3, 6: 1}
# Night Choghadiya start offset
# Sun=5(Shubh),Mon=4(Kaal),Tue=3(Amrit),Wed=2(Chara),Thu=1(Rog),Fri=0(Udvega),Sat=6(Labha) — not exact but classical
NIGHT_CHOGHADIYA_START = {0: 5, 1: 4, 2: 3, 3: 2, 4: 1, 5: 0, 6: 6}


def _get_sun_moon_lons(ts, eph, t, ayanamsha_type="LAHIRI"):
    """Returns (sun_sidereal_lon, moon_sidereal_lon) at time t."""
    from skyfield import framelib
    ayan = get_ayanamsha(t.tt, ayanamsha_type)

    def sid_lon(body_name):
        import math as _math
        app = eph["earth"].at(t).observe(eph[body_name]).apparent()
        R = framelib.build_ecliptic_matrix(t)
        r_ecl = R.dot(app.position.au)
        lon = _math.degrees(_math.atan2(r_ecl[1], r_ecl[0])) % 360.0
        return (lon - ayan) % 360.0

    return sid_lon("sun"), sid_lon("moon")


def _get_tithi(sun_lon, moon_lon):
    """Returns 1-indexed Tithi (1=Shukla Pratipada ... 30=Amavasya)."""
    diff = (moon_lon - sun_lon) % 360.0
    return int(diff / 12.0) + 1


def _get_sun_sign(sun_lon):
    """Returns 0-indexed sign of Sun."""
    return int(sun_lon / 30.0) % 12


# ─────────────────────────────────────────────────────────────────────────────
# LUNAR MONTH CALENDAR
# ─────────────────────────────────────────────────────────────────────────────

def get_lunar_months(year: int, ayanamsha_type: str = "LAHIRI") -> list:
    """
    Returns all lunar months (New Moon to New Moon) for a given year.

    Each entry contains:
    - amanta_month: Chaitra, Vaishakha, etc.
    - purnimanta_month: same name but New Moon ends PREVIOUS month in this system
    - new_moon_date: date of the Amavasya (New Moon)
    - full_moon_date: date of the Purnima (Full Moon) within this month
    - sun_sign_at_new_moon: Aries, Taurus, etc.
    - is_adhika: True if this is a leap (intercalary) month
    """
    ts, eph = load_ephemeris()
    from skyfield import almanac

    t0 = ts.utc(year - 1, 12, 1)
    t1 = ts.utc(year + 1,  1, 1)

    # Find all New Moons and Full Moons
    f_phases = almanac.moon_phases(eph)
    t_phases, v_phases = almanac.find_discrete(t0, t1, f_phases)

    new_moons  = [t for t, v in zip(t_phases, v_phases) if v == 0]
    full_moons = [t for t, v in zip(t_phases, v_phases) if v == 2]

    months = []
    prev_sun_sign = None

    for i, nm in enumerate(new_moons):
        utc = nm.utc_datetime()
        if utc.year < year: continue
        if utc.year > year: break

        sun_lon, _ = _get_sun_moon_lons(ts, eph, nm, ayanamsha_type)
        sun_sign = _get_sun_sign(sun_lon)

        # Amanta month: named by Sun's sign at or just before New Moon
        amanta_name = AMANTA_MONTHS[sun_sign]

        # Adhika (leap) month: if Sun stays in same sign at two consecutive New Moons
        is_adhika = (prev_sun_sign == sun_sign)

        # Find Full Moon in this window (between this and next New Moon)
        if i + 1 < len(new_moons):
            next_nm = new_moons[i + 1]
            fm_in_window = [f for f in full_moons if nm.tt < f.tt < next_nm.tt]
        else:
            fm_in_window = []

        entry = {
            "amanta_month": amanta_name,
            "purnimanta_month": AMANTA_MONTHS[(sun_sign - 1) % 12],
            "new_moon_date": utc.strftime("%Y-%m-%d"),
            "full_moon_date": fm_in_window[0].utc_datetime().strftime("%Y-%m-%d") if fm_in_window else "N/A",
            "sun_sign_at_new_moon": SIGN_NAMES[sun_sign],
            "is_adhika_masa": is_adhika,
            "sun_longitude": round(sun_lon, 4),
        }
        months.append(entry)
        prev_sun_sign = sun_sign

    return months


# ─────────────────────────────────────────────────────────────────────────────
# FESTIVAL CALENDAR
# ─────────────────────────────────────────────────────────────────────────────

# Festival definitions: (tithi_number, sun_sign_of_month, name, description)
# tithi_number: 1-30 (Shukla 1-15 / Krishna 1-14 + 30=Amavasya)
# sun_sign: 0-indexed sign of Sun at that time (determines the lunar month)
FESTIVAL_RULES = [
    # Tithi, Sun_sign_0indexed, Name, Type, Notes
    (3,  11, "Akshaya Tritiya",        "Auspicious", "Vaishakha Shukla Tritiya — permanent auspicious day"),
    (4,  7,  "Sankashti Chaturthi",    "Vrat",       "Monthly — most important in Bhadrapada (Ganesh Chaturthi)"),
    (4,  5,  "Ganesh Chaturthi",       "Festival",   "Bhadrapada Shukla Chaturthi — birth of Lord Ganesha"),
    (8,  3,  "Kamada Ekadashi",        "Ekadashi",   "Chaitra Shukla Ekadashi — frees from sins"),
    (8,  3,  "Janmashtami",            "Festival",   "Shravana Krishna Ashtami — Krishna's birthday"),
    (11, 3,  "Ekadashi",               "Vrat",       "Shukla Ekadashi — fasting for Vishnu"),
    (11, 11, "Dev Uthani Ekadashi",    "Festival",   "Kartika Shukla Ekadashi — Vishnu wakes from rest"),
    (13, 7,  "Pradosh Vrat",           "Vrat",       "Bhadrapada Trayodashi — Shiva worship"),
    (15, 3,  "Chaitra Purnima",        "Festival",   "Hanuman Jayanti in some regions"),
    (15, 4,  "Vaishakha Purnima",      "Festival",   "Buddha Purnima / Vesak"),
    (15, 6,  "Ashadha Purnima",        "Festival",   "Guru Purnima — honoring teachers"),
    (15, 7,  "Raksha Bandhan",         "Festival",   "Shravana Purnima — brother-sister bond"),
    (15, 9,  "Sharad Purnima",         "Festival",   "Ashwin Purnima — full moon of autumn, Kojagiri"),
    (15, 10, "Kartika Purnima",        "Festival",   "Deva Diwali / Guru Nanak Jayanti"),
    (15, 11, "Phalguna Purnima",       "Festival",   "Holi (eve)"),
    (16, 7,  "Hartalika Teej",         "Festival",   "Bhadrapada Krishna Pratipada — Shiva-Parvati worship"),
    (19, 6,  "Ashadha Krishna Navami", "Vrat",       "Navami of Ashadha Krishna"),
    (19, 7,  "Mahalaya",               "Festival",   "Ashwin Krishna Navami — Pitru Paksha begins"),
    (22, 7,  "Navratri",               "Festival",   "Ashwin Shukla Pratipada — 9 nights of Devi (from Pratipada to Navami)"),
    (24, 7,  "Maha Navami",            "Festival",   "Ashwin Shukla Navami — last day of Navratri"),
    (25, 7,  "Dussehra / Vijaya Dashami","Festival", "Ashwin Shukla Dashami — victory of good over evil"),
    (30, 7,  "Diwali (Deepavali)",     "Festival",   "Kartika Amavasya — festival of lights"),
    (30, 8,  "Diwali (Kartika Amavasya)","Festival", "Main Diwali night — Lakshmi Puja"),
    (30, 11, "Makar Sankranti",        "Festival",   "Solar festival — Sun enters Capricorn"),
]


def get_festivals_for_year(year: int, ayanamsha_type: str = "LAHIRI") -> dict:
    """
    Returns a comprehensive dictionary of festivals for the given year.
    Includes: astronomical date, tithi, lunar month, and description.

    Algorithm:
    1. Scan every day of the year
    2. Calculate Tithi at sunrise (most traditional method)
    3. Match against FESTIVAL_RULES by Tithi + Sun sign
    4. Special cases: Sankranti (solar), Ekadashis (every month)
    """
    ts, eph = load_ephemeris()
    festivals = {}

    # Scan every day of the year
    for month in range(1, 13):
        days_in_month = 31
        for day in range(1, days_in_month + 1):
            try:
                t = ts.utc(year, month, day, 6, 0, 0)  # 6:00 UTC approx sunrise
            except Exception:
                continue

            try:
                sun_lon, moon_lon = _get_sun_moon_lons(ts, eph, t, ayanamsha_type)
            except Exception:
                continue

            tithi = _get_tithi(sun_lon, moon_lon)
            sun_sign = _get_sun_sign(sun_lon)
            date_str = f"{year}-{month:02d}-{day:02d}"

            for (rule_tithi, rule_sun_sign, festival_name, festival_type, description) in FESTIVAL_RULES:
                if tithi == rule_tithi and sun_sign == rule_sun_sign:
                    if festival_name not in festivals:
                        festivals[festival_name] = {
                            "date": date_str,
                            "tithi": TITHI_NAMES[tithi - 1],
                            "type": festival_type,
                            "sun_sign": SIGN_NAMES[sun_sign],
                            "description": description,
                        }

    # Special: All Ekadashis (Tithi 11 = Shukla, Tithi 26 = Krishna)
    ekadashis = []
    for month in range(1, 13):
        for day in range(1, 32):
            try:
                t = ts.utc(year, month, day, 6, 0, 0)
                sun_lon, moon_lon = _get_sun_moon_lons(ts, eph, t, ayanamsha_type)
                tithi = _get_tithi(sun_lon, moon_lon)
                sun_sign = _get_sun_sign(sun_lon)
                if tithi in {11, 26}:
                    phase = "Shukla" if tithi == 11 else "Krishna"
                    ekadashis.append({
                        "date": f"{year}-{month:02d}-{day:02d}",
                        "phase": phase,
                        "lunar_month": AMANTA_MONTHS[sun_sign],
                        "tithi": TITHI_NAMES[tithi - 1],
                        "description": "Fast of Lord Vishnu — most auspicious for spiritual practice",
                    })
            except Exception:
                continue

    # Deduplicate ekadashis by date
    seen_dates = set()
    unique_ekadashis = []
    for e in ekadashis:
        if e["date"] not in seen_dates:
            seen_dates.add(e["date"])
            unique_ekadashis.append(e)

    festivals["All_Ekadashis"] = unique_ekadashis

    # Special: Makar Sankranti (Sun enters Capricorn = sidereal sign 9, lon 270°)
    for month in range(1, 13):
        for day in range(1, 32):
            try:
                t      = ts.utc(year, month, day, 0, 0, 0)
                t_next = ts.utc(year, month, day, 23, 59, 0)
                s0, _  = _get_sun_moon_lons(ts, eph, t, ayanamsha_type)
                s1, _  = _get_sun_moon_lons(ts, eph, t_next, ayanamsha_type)
                if int(s0 / 30) == 8 and int(s1 / 30) == 9:
                    festivals["Makar Sankranti"] = {
                        "date": f"{year}-{month:02d}-{day:02d}",
                        "tithi": "Solar Transit",
                        "type": "Festival",
                        "sun_sign": "Capricorn",
                        "description": "Sun enters sidereal Capricorn — harvest festival, Uttarayan begins",
                    }
                    break
            except Exception:
                continue

    return festivals


# ─────────────────────────────────────────────────────────────────────────────
# CHOGHADIYA
# ─────────────────────────────────────────────────────────────────────────────

def get_choghadiya(
    date_str: str,
    sunrise_time_str: str,
    sunset_time_str: str,
    sunrise_next_day_str: str = None
) -> dict:
    """
    Calculates Choghadiya (8 auspicious/inauspicious time slots) for a given date.

    Parameters:
    - date_str: "YYYY-MM-DD"
    - sunrise_time_str: "HH:MM" in local time
    - sunset_time_str:  "HH:MM" in local time
    - sunrise_next_day_str: "HH:MM" next day sunrise for night slots (optional)

    Returns:
    - day_slots: 8 daytime Choghadiya slots
    - night_slots: 8 nighttime Choghadiya slots (if next sunrise given)
    - weekday: Saturday, etc.
    - auspicious_windows: filtered list of Labha/Amrit/Shubh/Chara slots

    Algorithm:
    Daytime = sunrise to sunset, divided into 8 equal slots.
    Night = sunset to next sunrise, divided into 8 equal slots.
    The starting Choghadiya depends on the weekday.
    """
    date = datetime.strptime(date_str, "%Y-%m-%d")
    weekday = date.weekday()  # 0=Mon ... 6=Sun
    # Python weekday: Mon=0, but we need Sun=0 convention
    py_to_vedic = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 0}
    vedic_weekday = py_to_vedic[weekday]  # Sun=0, Mon=1, ..., Sat=6
    weekday_names = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]
    weekday_name = weekday_names[vedic_weekday]

    def parse_time(time_str, date):
        h, m = map(int, time_str.split(":"))
        return date.replace(hour=h, minute=m, second=0, microsecond=0)

    sunrise  = parse_time(sunrise_time_str, date)
    sunset   = parse_time(sunset_time_str,  date)

    # Daytime slots (8 equal parts: sunrise to sunset)
    day_duration = (sunset - sunrise).total_seconds()
    slot_secs_day = day_duration / 8.0

    day_start_idx = DAY_CHOGHADIYA_START[vedic_weekday]
    day_slots = []
    for i in range(8):
        slot_name_idx = (day_start_idx + i) % 8
        chhog_name = CHOGHADIYA_NAMES[slot_name_idx]
        slot_start = sunrise + timedelta(seconds=slot_secs_day * i)
        slot_end   = sunrise + timedelta(seconds=slot_secs_day * (i + 1))
        day_slots.append({
            "slot":       i + 1,
            "name":       chhog_name,
            "nature":     CHOGHADIYA_NATURE[chhog_name],
            "start":      slot_start.strftime("%H:%M"),
            "end":        slot_end.strftime("%H:%M"),
            "suitability": CHOGHADIYA_SUITABILITY[chhog_name],
        })

    # Nighttime slots (8 equal parts: sunset to next sunrise)
    night_slots = []
    if sunrise_next_day_str:
        next_day = date + timedelta(days=1)
        sunrise_next = parse_time(sunrise_next_day_str, next_day)
        night_duration = (sunrise_next - sunset).total_seconds()
        slot_secs_night = night_duration / 8.0
        night_start_idx = NIGHT_CHOGHADIYA_START[vedic_weekday]
        for i in range(8):
            slot_name_idx = (night_start_idx + i) % 8
            chhog_name = CHOGHADIYA_NAMES[slot_name_idx]
            slot_start = sunset  + timedelta(seconds=slot_secs_night * i)
            slot_end   = sunset  + timedelta(seconds=slot_secs_night * (i + 1))
            night_slots.append({
                "slot":       i + 1,
                "name":       chhog_name,
                "nature":     CHOGHADIYA_NATURE[chhog_name],
                "start":      slot_start.strftime("%H:%M"),
                "end":        slot_end.strftime("%H:%M"),
                "suitability": CHOGHADIYA_SUITABILITY[chhog_name],
            })

    # Collect all auspicious windows
    auspicious_names = {"Amrit", "Labha", "Shubh", "Chara"}
    auspicious_windows = [
        {**s, "period": "Day"}   for s in day_slots   if s["name"] in auspicious_names
    ] + [
        {**s, "period": "Night"} for s in night_slots  if s["name"] in auspicious_names
    ]

    return {
        "date":               date_str,
        "weekday":            weekday_name,
        "sunrise":            sunrise_time_str,
        "sunset":             sunset_time_str,
        "day_slots":          day_slots,
        "night_slots":        night_slots,
        "auspicious_windows": auspicious_windows,
    }
