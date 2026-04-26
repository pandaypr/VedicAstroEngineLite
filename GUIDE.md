# Vedic Astro Engine: The Definitive Developer's Guide

Welcome to the **Vedic Astro Engine**, a professional-grade, pure-Python library designed for high-precision astrological research and application development. This engine is completely free of the Swiss Ephemeris dependency and is powered by NASA JPL ephemerides.

---

## 📦 Installation

```bash
pip install vedic_astro_engine_lite
```

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
15. [Professional PDF Reporting](#15-professional-pdf-reporting)

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
    lat=26.0411, lon_deg=84.6514, 
    ayanamsha_type="LAHIRI", 
    node_type="TRUE"
)
```

---

## 2. Mathematics & Precision

### Swiss Ephemeris Independence
VedicAstroEngine is **completely independent of the Swiss Ephemeris library**. It uses NASA's DE421/DE440 ephemerides via the `Skyfield` library.

### Nutation Correction
We apply `delta_psi` nutation adjustment to ensure sub-arcsecond accuracy:
$$ \lambda_{sidereal} = \lambda_{geo} - \Delta\psi - \text{Ayanamsha} $$

---

## 3. Dasha Systems (Timing Analysis)

### Vimshottari Dasha (Up to 6 Levels)
```python
# Accessing Mahadasha (MD)
md_list = data["dashas"]["vimshottari"]
current_md = md_list[0] 
```

### Other Systems
- **Chara Dasha**: Jaimini-style sign-based dasha.
- **Yogini Dasha**: 36-year cycle.
- **Kaal Chakra Dasha**: Based on Nakshatra Padas.

---

## 4. Ashtakavarga (The Point System)

Calculates Bindus for 7 planets + Lagna and the Sarvashtakavarga (SAV).
```python
# Total Sarvashtakavarga (SAV) for Aries (Sign 1)
sav_score = data["ashtakavarga"]["SAV"][1] 
```

---

## 5. Graha Drishti (Planetary Aspects)

Full aspect calculation (100% strength) as per BPHS.
```python
# Check aspects on Moon
aspects_on_moon = data["aspects"]["Moon"] 
```

---

## 6. Planetary Avasthas (States)

### Baala-Adi (Age) & Shayana-Adi (Activity)
```python
age = data["avasthas"]["Sun"]["baala_adi"] # e.g., "Yuva"
```

---

## 7. Yogas (Planetary Combinations)

Extensive detection of:
- **Nabhasa Yogas**: Gola, Yuga, Veena, etc.
- **Raja Yogas**: Kendra-Trikona relationships.
- **Dhana Yogas**: Wealth combinations.

---

## 8. Jaimini Astrology (Karakas & Yogas)

### Chara Karakas (7-Planetary System)
```python
ak = data["jaimini_karakas"]["AK"] # Atma Karaka
```

---

## 9. Matchmaking & Kuja Dosha

### Ashtakoota Guna Milan
```python
from vedic_astro_engine import calculate_guna_milan
comparison = calculate_guna_milan(boy_data, girl_data)
```

---

## 10. Varshaphala (Tajika Annual Chart)

Includes **Muntha**, **Sahams**, and **Tajik Yogas**.

---

## 11. Longevity & Health (Ayurdaya)

### Pinda & Amsa Ayu
Classical mathematical models for life expectancy.

---

## 12. Advanced Transit (Gochar)

### Moorthy Nirnaya & Vedha
Classification of transits and checking for obstacles (Vedha).

---

## 13. Chakras (SBC & Sudarshan)

### Sarvatobhadra Chakra (SBC)
Analyzes 28 Nakshatras (including Abhijit) for "piercing" (Vedha).

---

## 14. Panchanga & Astronomy

- **Tithi, Vara, Nakshatra, Yoga, Karana**.
- **Eclipse Scanner**: High-precision search for Solar and Lunar eclipses.

---

## 15. Professional PDF Reporting

Generate stunning multi-page Kundali reports:
```python
from vedic_astro_engine import generate_pdf_report
generate_pdf_report(data, "My_Report.pdf")
```

---

## Licensing & Usage
This library is licensed under the **AGPL-3.0**. 

**Developed by Prabhakar Panday.**
📧 **prabhakarpanday4@gmail.com**
