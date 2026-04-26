import math

class ShadbalaCalculator:
    """
    Parashari Shadbala (Six-fold planetary strength) logic.
    """
    
    PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    
    # Permanent Relationships (Friend=1, Neutral=0, Enemy=-1)
    PERMANENT_MAITRI = {
        "Sun": {"Moon": 1, "Mars": 1, "Mercury": 0, "Jupiter": 1, "Venus": -1, "Saturn": -1},
        "Moon": {"Sun": 1, "Mercury": 1, "Mars": 0, "Jupiter": 0, "Venus": 0, "Saturn": 0},
        "Mars": {"Sun": 1, "Moon": 1, "Jupiter": 1, "Mercury": -1, "Venus": 0, "Saturn": 0},
        "Mercury": {"Sun": 1, "Venus": 1, "Moon": -1, "Mars": 0, "Jupiter": 0, "Saturn": 0},
        "Jupiter": {"Sun": 1, "Moon": 1, "Mars": 1, "Mercury": -1, "Venus": -1, "Saturn": 0},
        "Venus": {"Mercury": 1, "Saturn": 1, "Sun": -1, "Moon": -1, "Mars": 0, "Jupiter": 0},
        "Saturn": {"Mercury": 1, "Venus": 1, "Sun": -1, "Moon": -1, "Mars": -1, "Jupiter": 0}
    }

    NAISARGIKA_BALA = {
        "Sun": 60.0, "Moon": 51.43, "Venus": 42.85, "Jupiter": 34.28,
        "Mercury": 25.71, "Mars": 17.14, "Saturn": 8.57
    }
    
    UCCHA_LONG = {
        "Sun": 10.0, "Moon": 33.0, "Mars": 298.0, "Mercury": 165.0,
        "Jupiter": 95.0, "Venus": 357.0, "Saturn": 200.0
    }
    
    AVG_SPEED = {
        "Sun": 0.9856, "Moon": 13.176, "Mars": 0.524,
        "Mercury": 1.383, "Jupiter": 0.083, "Venus": 1.2, "Saturn": 0.033
    }

    @staticmethod
    def get_relationship(planet, owner):
        if planet == owner: return "own"
        rel = ShadbalaCalculator.PERMANENT_MAITRI.get(planet, {}).get(owner, 0)
        if rel == 1: return "friend"
        if rel == -1: return "enemy"
        return "neutral"

    @staticmethod
    def calculate_sthana_bala(planet, abs_long, house_num, vargas):
        dist = abs(abs_long - ShadbalaCalculator.UCCHA_LONG[planet]) % 360
        if dist > 180: dist = 360 - dist
        uccha = 60.0 * (1.0 - dist / 180.0)
        
        varga_score = 0
        from .constants import SIGN_OWNERS
        for varga_name, sign_idx in vargas.items():
            if varga_name not in ['D1', 'D2', 'D3', 'D7', 'D9', 'D12', 'D30']: continue
            owner = SIGN_OWNERS[sign_idx + 1] # sign_idx is 0-indexed in our system, SIGN_OWNERS is 1-indexed
            rel = ShadbalaCalculator.get_relationship(planet, owner)
            scores = {"own": 30, "friend": 20, "neutral": 10, "enemy": 5}
            varga_score += scores.get(rel, 10)
            
        k_scores = {1:60, 4:60, 7:60, 10:60, 2:30, 5:30, 8:30, 11:30}
        kendradi = k_scores.get(house_num, 15)
        
        return round(uccha + varga_score + kendradi, 2)

    @staticmethod
    def calculate_dig_bala(planet, abs_long, asc_long, mc_long):
        targets = {
            "Sun": mc_long, "Mars": mc_long,
            "Moon": (mc_long + 180) % 360, "Venus": (mc_long + 180) % 360,
            "Mercury": asc_long, "Jupiter": asc_long,
            "Saturn": (asc_long + 180) % 360
        }
        target = targets.get(planet, asc_long)
        dist = abs(abs_long - target) % 360
        if dist > 180: dist = 360 - dist
        return round(60.0 * (1.0 - dist / 180.0), 2)

    @staticmethod
    def calculate_kala_bala(planet, is_day, moon_diff_deg, weekday_lord, hora_lord):
        diurnal = {"Sun", "Jupiter", "Venus"}
        nocturnal = {"Moon", "Mars", "Saturn"}
        if (planet in diurnal and is_day) or (planet in nocturnal and not is_day) or (planet == "Mercury"):
            nat = 60
        else:
            nat = 30
        
        is_benefic = planet in ["Jupiter", "Venus", "Mercury", "Moon"]
        p_val = moon_diff_deg / 3.0 if moon_diff_deg <= 180 else (360 - moon_diff_deg) / 3.0
        paksha = p_val if is_benefic else (60 - p_val)
        
        vara = 45 if planet == weekday_lord else 0
        hora = 60 if planet == hora_lord else 0
        
        return round(nat + paksha + vara + hora, 2)

    @staticmethod
    def calculate_cheshta_bala(planet, speed, is_retro):
        if planet in ["Sun", "Moon"]: return 30.0
        if is_retro: return 60.0
        avg = ShadbalaCalculator.AVG_SPEED.get(planet, 1.0)
        cheshta = 60.0 * avg / (avg + abs(speed))
        return round(min(60.0, max(0, cheshta)), 2)

    @staticmethod
    def calculate_drig_bala(planet, planet_positions):
        score = 0
        p_lon = planet_positions[planet]
        for aspector, a_lon in planet_positions.items():
            if aspector == planet: continue
            dist = (p_lon - a_lon) % 360
            if 170 < dist < 190:
                if aspector in ["Jupiter", "Venus"]: score += 15
                if aspector in ["Mars", "Saturn"]: score -= 15
        return score

    @classmethod
    def get_total_shadbala(cls, planet, components):
        total_virupas = sum(components.values()) + cls.NAISARGIKA_BALA.get(planet, 0)
        return {
            "virupas": round(total_virupas, 2),
            "rupas": round(total_virupas / 60.0, 2)
        }
