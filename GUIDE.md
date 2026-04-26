# Vedic Astro Engine: The Definitive Developer's Guide

Welcome to the **Vedic Astro Engine**, a professional-grade, pure-Python library designed for high-precision astrological research and application development.

---

## Table of Contents
1. [Core Engine (`build_charts`)](#1-core-engine-build_charts)
2. [Mathematics & Precision](#2-mathematics--precision)
3. [Dasha Systems (Timing Analysis)](#3-dasha-systems-timing-analysis)
4. [Ashtakavarga (The Point System)](#4-ashtakavarga-the-point-system)
5. [Graha Drishti (Planetary Aspects)](#5-graha-drishti-planetary-aspects)
6. [Planetary Avasthas (States)](#6-planetary-avasthas-states)
7. [Yogas (Planetary Combinations)](#7-yogas-planetary-combinations)
8. [Jaimini Astrology (Karakas & Yogas)](#8-jaimini-astrology-karakas--yogas)
9. [Matchmaking & Kuja Dosha](#9-matchmaking--kuja-dosha)
10. [Varshaphala (Tajika Annual Chart)](#10-varshaphala-tajika-annual-chart)
11. [Longevity & Health (Ayurdaya)](#11-longevity--health-ayurdaya)
12. [Advanced Transit (Gochar)](#12-advanced-transit-gochar)
13. [Chakras (SBC & Sudarshan)](#13-chakras-sbc--sudarshan)
14. [Panchanga & Astronomy](#14-panchanga--astronomy)
15. [AI Agent Integration (Graphify)](#15-ai-agent-integration-graphify)

---

## 1. Core Engine (`build_charts`)

The `build_charts` function is the main entry point. It calculates the entire astrological profile in one pass.

### Usage
```python
from vedic_astro_engine import build_charts

# Generate full chart data
data = build_charts(
    year=1992, month=11, day=14, 
    hour=8, minute=10, 
    lat=26.0411, lon=84.6514, 
    ayanamsha_type="LAHIRI", 
    node_type="TRUE"
)
```

### Important: Coordinate Entry (N/E/S/W)
To ensure mathematical precision, the engine uses decimal degrees:
*   **Latitude**: Use positive values for **North** (`+`) and negative values for **South** (`-`).
*   **Longitude**: Use positive values for **East** (`+`) and negative values for **West** (`-`).

| Direction | Sign | Example |
| :--- | :--- | :--- |
| North (N) | `+` | Delhi: `28.61` |
| South (S) | `-` | Sydney: `-33.86` |
| East (E) | `+` | Mumbai: `72.87` |
| West (W) | `-` | New York: `-74.00` |

### Main Output Object
- `data["planets"]`: Dictionary of planet objects.
- `data["lagna"]`: Ascendant longitude (float).
- `data["vargas"]`: List of longitudes for all 16+ divisional charts.
- `data["dashas"]`: Complete hierarchical dasha trees.

---

## 2. Mathematics & Precision

### Nutation Correction
We apply the `delta_psi` nutation adjustment to geocentric longitudes to ensure sub-arcsecond accuracy compared to Swiss Ephemeris.
$$ \lambda_{sidereal} = \lambda_{geo} - \Delta\psi - \text{Ayanamsha} $$

### Retrogression logic
Calculated via central-difference velocity checking.
```python
# Check if a planet is retrograde
is_retro = data["planets"]["Saturn"]["is_retrograde"] # Boolean
```

---

## 3. Dasha Systems (Timing Analysis)

### Vimshottari Dasha (6 Levels)
```python
# Accessing Mahadasha (MD) and Antardasha (AD)
md_list = data["dashas"]["vimshottari"]
current_md = md_list[0] # Returns dict with 'lord', 'start', 'end'
```

### Other Systems
- **Chara Dasha**: Jaimini-style sign-based dasha.
- **Yogini Dasha**: 36-year cycle.
- **Kaal Chakra Dasha**: Based on Nakshatra Padas.

---

## 4. Ashtakavarga (The Point System)

### BAV & SAV
Calculates Bindus for 7 planets + Lagna.
```python
# Total Sarvashtakavarga (SAV) for a sign
sav_score = data["ashtakavarga"]["SAV"][1] # Points in Aries
```

---

## 5. Graha Drishti (Planetary Aspects)

Full aspect calculation (100% strength) as per BPHS.
- **Special Aspects**: Mars (4,8), Jupiter (5,9), Saturn (3,10).
```python
# Check aspects on a specific planet
aspects_on_moon = data["aspects"]["Moon"] # List of aspecting planets
```

---

## 6. Planetary Avasthas (States)

### Baala-Adi (Age) & Shayana-Adi (Activity)
```python
# Example: Check Sun's activity state
state = data["avasthas"]["Sun"]["shayana_adi"] # e.g., "Prakashana"
age = data["avasthas"]["Sun"]["baala_adi"]      # e.g., "Yuva"
```

---

## 7. Yogas (Planetary Combinations)

Extensive detection of:
- **Nabhasa Yogas**: Gola, Yuga, Veena, etc.
- **Surya/Chandra Yogas**: Vesi, Vasi, Sunaphaa, Anapha, etc.
- **Raja Yogas**: Kendra-Trikona lord relationships.

```python
# Check detected yogas
for yoga in data["yogas"]["combinations"]:
    print(f"Detected: {yoga['name']} - {yoga['description']}")
```

---

## 8. Jaimini Astrology (Karakas & Yogas)

### Chara Karakas (7-Planetary System)
1. Atma Karaka (AK) to 7. Dara Karaka (DK).
```python
ak = data["jaimini_karakas"]["AK"] # returns 'Sun', 'Mars', etc.
```

### Jaimini Raja Sambandha
Detects high-level career yogas involving AK and AmK.

---

## 9. Matchmaking & Kuja Dosha

### Ashtakoota Guna Milan
```python
from vedic_astro_engine import calculate_guna_milan, detect_kuja_dosha

# Compare two charts
comparison = calculate_guna_milan(boy_data, girl_data)
score = comparison["total_score"] # x/36
```

### Kuja Dosha (Manglik) & Papa Samya
```python
dosha = detect_kuja_dosha(data["planets"], data["lagna"])
malefic_balance = calculate_papa_samya(data["planets"], data["lagna"])
```

---

## 10. Varshaphala (Tajika Annual Chart)

### Solar Return & Muntha
```python
from vedic_astro_engine import find_solar_return

# Find moment when Sun returns to natal longitude
sr_time = find_solar_return(natal_sun_lon=208.22, year=2024)
```

### Tajik Features
- **Sahams**: 36+ sensitive points (`data["sahams"]`).
- **Tajik Yogas**: Ithasala, Eshrpha, Kamboola.
- **Varsha Swamy**: The Lord of the Year.

---

## 11. Longevity & Health (Ayurdaya)

### Pinda & Amsa Ayu
Classical mathematical models for life expectancy.
```python
from vedic_astro_engine import calculate_pinda_ayu

# Calculate longevity years
ayu = calculate_pinda_ayu(planet_lons, lagna_lon)
print(f"Total Ayu: {ayu['total_unrefined']} years")
```

### Medical Mapping (Kalapurusha)
Maps malefic afflictions to specific body areas.
```python
# Accessing health vulnerabilities
for issue in data["health_vulnerabilities"]:
    print(f"Health Alert: {issue}")
```

### Maraka & Badhaka
Detects killer planets and obstructing lords for timing critical life events.

---

## 12. Advanced Transit (Gochar)

### Moorthy Nirnaya & Vedha
- **Moorthy**: Classification (Gold/Silver/Copper/Iron) based on Moon sign at entry.
- **Vedha**: Checks if a transit result is blocked by another planet.

### Transit Scanner (Precise Degree Hits)
```python
from vedic_astro_engine import find_transit_crossing

# Find when Saturn hits exactly 300° (Aquarius)
hits = find_transit_crossing("Saturn", 300.0, start_jd=2460310.5)
```

---

## 12. Chakras (SBC & Sudarshan)

### Sarvatobhadra Chakra (SBC)
Analyzes 28 Nakshatras (including Abhijit) for "piercing" (Vedha) on natal positions.
```python
vedha_hits = data["sarvatobhadra"]["vedha_hits"]
```

### Sudarshan Chakra
Triple-chart overlay (Lagna, Moon, Sun) for combined house strength.
```python
strength = data["sudarshan_chakra"][10]["strength_score"] # Strength of 10th house
```

---

## 14. Panchanga & Astronomy

### Daily Calculations
- **Tithi, Vara, Nakshatra, Yoga, Karana**.
- **Choghadiya**: Auspicious time slots for the day/night.

### Eclipse Scanner
High-precision search for Solar and Lunar eclipses.
```python
from vedic_astro_engine import find_next_eclipse

# Search for eclipses in the next year
events = find_next_eclipse(start_jd=2460310.5, eclipse_type="SOLAR")
```

### Indu Lagna (Wealth)
Calculation of the wealth point and its lord.
```python
indu = data["indu_lagna"]
print(f"Indu Lagna is in {indu['indu_sign_name']}")
```

---

## 15. AI Agent Integration (Graphify)

This repository includes a **Knowledge Graph** to help AI agents navigate the code.
- **`graphify-out/graph.json`**: The full semantic map.
- **`.agents/rules/`**: Instructions for agents to save tokens and avoid redundant research.

---

## Licensing & Usage
This library is licensed under the **MIT License**.

**Developed by the Antigravity Team.**
