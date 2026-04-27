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
    
    EXALTED_SIGNS = {
        "Sun": 0, "Moon": 1, "Mars": 9, "Mercury": 5,
        "Jupiter": 3, "Venus": 11, "Saturn": 6
    }
    
    DEBILITATED_SIGNS = {
        "Sun": 6, "Moon": 7, "Mars": 3, "Mercury": 11,
        "Jupiter": 9, "Venus": 5, "Saturn": 0
    }
    
    MOOLATRIKONA_SIGNS = {
        "Sun": 4, "Moon": 1, "Mars": 0, "Mercury": 5,
        "Jupiter": 8, "Venus": 6, "Saturn": 10
    }
    
    HORA_ORDER = ["Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars"]

    @classmethod
    def get_sign_relationship(cls, planet, sign_idx, temporal_friends, temporal_enemies):
        if cls.EXALTED_SIGNS.get(planet) == sign_idx:
            return "exalted"
        if cls.DEBILITATED_SIGNS.get(planet) == sign_idx:
            return "debilitated"
        if cls.MOOLATRIKONA_SIGNS.get(planet) == sign_idx:
            return "moolatrikona"
            
        from .constants import SIGN_OWNERS
        owner = SIGN_OWNERS[sign_idx + 1]
        if planet == owner:
            return "own"
            
        # Natural relationship
        nat_rel = cls.PERMANENT_MAITRI.get(planet, {}).get(owner, 0)
        
        # Temporal relationship
        temp_rel = 1 if owner in temporal_friends else (-1 if owner in temporal_enemies else 0)
        
        combined = nat_rel + temp_rel
        if combined >= 2: return "great_friend"
        if combined == 1: return "friend"
        if combined == 0: return "neutral"
        if combined == -1: return "enemy"
        if combined <= -2: return "great_enemy"
        return "neutral"

    @classmethod
    def _saptavarga_bala(cls, planet: str, varga_signs: dict, temporal_friends: set, temporal_enemies: set) -> float:
        scores = {
            "exalted": 30.0, "moolatrikona": 22.5, "own": 15.0,
            "great_friend": 11.25, "friend": 7.5, "neutral": 3.75,
            "enemy": 1.875, "great_enemy": 0.9375, "debilitated": 0.0
        }
        total = 0.0
        for v in ["D1", "D2", "D3", "D7", "D9", "D12", "D30"]:
            s_idx = varga_signs.get(v)
            if s_idx is not None:
                r = cls.get_sign_relationship(planet, s_idx, temporal_friends, temporal_enemies)
                total += scores.get(r, 3.75)
        return round(total, 4)

    @classmethod
    def calculate_sthana_bala(cls, planet, abs_long, house_num, vargas, temporal_friends, temporal_enemies):
        dist = abs(abs_long - cls.UCCHA_LONG[planet]) % 360
        if dist > 180: dist = 360 - dist
        uccha = 60.0 * (1.0 - dist / 180.0)
        
        varga_score = cls._saptavarga_bala(planet, vargas, temporal_friends, temporal_enemies)
        
        k_scores = {1:60, 4:60, 7:60, 10:60, 2:30, 5:30, 8:30, 11:30}
        kendradi = k_scores.get(house_num, 15)
        
        return round(uccha + varga_score + kendradi, 2)

    @staticmethod
    def calculate_dig_bala(planet: str, abs_long: float, cusps: list) -> float:
        # 0 = 1st cusp (Asc), 3 = 4th cusp (IC), 6 = 7th cusp (Dsc), 9 = 10th cusp (MC)
        strong_idx = {
            "Sun": 9, "Mars": 9, "Moon": 3, "Venus": 3,
            "Mercury": 0, "Jupiter": 0, "Saturn": 6
        }
        strong_point = cusps[strong_idx[planet]]
        d = min(abs(abs_long - strong_point) % 360, 360 - (abs(abs_long - strong_point) % 360))
        return round(60.0 * (1.0 - d / 180.0), 4)

    @classmethod
    def _hora_bala(cls, planet: str, hora_weekday: int, hours_since_sunrise: float) -> float:
        # hora_weekday is the weekday of the sunrise that started the current day
        start_hora_idx = (hora_weekday * 3) % 7 
        hora_offset = int(hours_since_sunrise) % 24
        hora_lord = cls.HORA_ORDER[(start_hora_idx + hora_offset) % 7]
        return 60.0 if hora_lord == planet else 0.0

    @classmethod
    def calculate_kala_bala(cls, planet, is_day, moon_diff_deg, weekday_lord, hora_weekday, hours_since_sunrise):
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
        hora = cls._hora_bala(planet, hora_weekday, hours_since_sunrise)
        
        return round(nat + paksha + vara + hora, 2)

    @classmethod
    def calculate_cheshta_bala(cls, planet, speed, is_retro, moon_diff_deg):
        if planet == "Moon":
            # Direct BPHS override: Moon's Motional Strength (Cheshta) is equal to its Paksha Bala
            p_val = moon_diff_deg / 3.0 if moon_diff_deg <= 180 else (360 - moon_diff_deg) / 3.0
            return round(p_val, 4)
        if planet == "Sun": return 30.0
        if is_retro: return 60.0
        avg = cls.AVG_SPEED.get(planet, 1.0)
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
