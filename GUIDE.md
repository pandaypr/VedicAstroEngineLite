# Vedic Astro Engine Lite: Developer's Guide

Welcome to the **Vedic Astro Engine Lite**, a high-precision, open-source Python library for Vedic (Hindu) Astrology. This version is designed for developers who need core astronomical and astrological calculations without the complexity and licensing restrictions of the Swiss Ephemeris.

---

## Table of Contents
1. [Core Engine (`build_charts`)](#1-core-engine-build_charts)
2. [Mathematics & Precision (NASA JPL)](#2-mathematics--precision-nasa-jpl)
3. [Panchanga (Daily Elements)](#3-panchanga-daily-elements)
4. [Shodashavarga (Divisional Charts)](#4-shodashavarga-divisional-charts)
5. [Vimshottari Dasha](#5-vimshottari-dasha)
6. [Ashtakavarga](#6-ashtakavarga)
7. [Special Points (Lagnas & Upagrahas)](#7-special-points-lagnas--upagrahas)
8. [Ayanamsha Support](#8-ayanamsha-support)
9. [Pro Version Comparison](#9-pro-version-comparison)

---

## 1. Core Engine (`build_charts`)

The `build_charts` function is the main entry point. It calculates the entire astrological profile in one pass.

### Usage
```python
from vedic_astro_engine import build_charts

# Generate full chart data for a specific moment
data = build_charts(
    year=1992, month=11, day=14, 
    hour=8, minute=10, 
    lat=26.0411, lon_deg=84.6514, 
    ayanamsha_type="LAHIRI", 
    node_type="TRUE"
)
```

### Coordinate Entry (N/E/S/W)
The engine uses decimal degrees:
*   **Latitude**: Positive for **North** (+), Negative for **South** (-).
*   **Longitude**: Positive for **East** (+), Negative for **West** (-).

### Main Output Object
- `data["planets"]`: Dictionary of planet objects (Longitudes, signs, houses, etc.).
- `data["lagna"]`: Ascendant longitude (float).
- `data["vargas"]`: Nested dictionary with longitudes for all 16 divisional charts.
- `data["dashas"]`: Hierarchical Vimshottari dasha tree.

---

## 2. Mathematics & Precision (NASA JPL)

### Swiss Ephemeris Independence
VedicAstroEngine Lite is **completely free of the Swiss Ephemeris (`pyswisseph`)**. It uses NASA's DE421/DE440 ephemerides via the `Skyfield` library.

### Nutation Correction
We apply `delta_psi` nutation adjustment to ensure sub-arcsecond accuracy:
$$ \lambda_{sidereal} = \lambda_{geo} - \Delta\psi - \text{Ayanamsha} $$

---

## 3. Panchanga (Daily Elements)

The engine calculates the five elements (Panchanga) with high precision:

```python
panchanga = data["panchanga"]
print(f"Tithi: {panchanga['tithi_name']}")
print(f"Nakshatra: {panchanga['nakshatra_name']}")
print(f"Yoga: {panchanga['yoga_name']}")
print(f"Karana: {panchanga['karana_name']}")
```

---

## 4. Shodashavarga (Divisional Charts)

Lite version includes full support for all 16 traditional divisional charts (D-1 to D-60):

```python
# Access Navamsha (D-9) for the Sun
sun_d9 = data["vargas"]["Sun"]["D9"]
print(f"Sun's Navamsha Longitude: {sun_d9}")
```

---

## 5. Vimshottari Dasha

The engine provides a recursive dasha tree (up to 4+ levels deep):

```python
# Accessing Mahadasha (MD)
md_list = data["dashas"]["vimshottari"]
first_md = md_list[0] 
print(f"Current MD Lord: {first_md['lord']}")

# Accessing Antardasha (AD) within the MD
for ad in first_md['antardashas']:
    print(f"  AD Lord: {ad['lord']} (Starts: {ad['start']})")
```

---

## 6. Ashtakavarga

Calculates Bindus (points) for the 7 classical planets and the Sarvashtakavarga (SAV).

```python
# Sarvashtakavarga (SAV) points for Aries (Sign 1)
sav_score = data["ashtakavarga"]["SAV"][1] 
print(f"Points in Aries: {sav_score}")
```

---

## 7. Special Points (Lagnas & Upagrahas)

Calculates sensitive points like **Hora Lagna**, **Ghati Lagna**, and the **Upagrahas** (Gulika, Mandi, etc.).

```python
# Access Special Lagnas
print(f"Hora Lagna: {data['special_lagnas']['Hora_Lagna']}")

# Access Upagrahas
print(f"Gulika: {data['planets']['Gulika']['longitude']}")
```

---

## 8. Ayanamsha Support

The engine supports various Ayanamsha types:
- `LAHIRI` (Default)
- `RAMAN`
- `KP`
- `FAGAN_BRADLEY`
- `SAYANA` (Tropical)

---

## 9. Pro Version Comparison

VedicAstroEngine Lite is designed for core functionality. For professional or commercial applications, the **Pro Version** provides:

| Feature | Lite | Pro |
| :--- | :---: | :---: |
| **Panchanga & Vargas** | ✅ | ✅ |
| **Vimshottari Dasha** | ✅ | ✅ |
| **Shadbala (Strengths)** | ❌ | ✅ |
| **Yogas (1000+ Combinations)** | ❌ | ✅ |
| **PDF Report Engine** | ❌ | ✅ |
| **Medical Astrology** | ❌ | ✅ |
| **Chara & Yogini Dashas** | ❌ | ✅ |
| **Ashtakoota Matchmaking** | ❌ | ✅ |

For Pro Version inquiries, contact: **prabhakarpanday4@gmail.com**

---

## Licensing & Usage
This library is licensed under the **AGPL-3.0**. 
- **Open Source**: Free to use for open-source projects.
- **Commercial**: For-profit use requires a separate **Commercial License**.

**Developed by Prabhakar Panday.**
