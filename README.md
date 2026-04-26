# VedicAstroEngine Lite

**VedicAstroEngine Lite** is a high-precision, open-source Python library for Vedic (Hindu) Astrology. Built on top of the robust **Skyfield** astronomical library and the **Swiss Ephemeris** (via de421/de440), it provides core calculations for astronomical points, panchanga, and divisional charts.

## Key Features (Lite Version)

- **Shodashavarga**: High-resolution calculation of all 16 divisional charts (D-1 to D-60).
- **Panchanga**: Tithi, Vara, Nakshatra, Yoga, and Karana.
- **Ashtakavarga**: Core points for the 7 classical planets.
- **Vimshottari Dasha**: Full recursive calculation of Mahadasha, Antardasha, and deeper levels.
- **Special Points**: Special Lagnas, Upagrahas, and Sphutas.
- **Accuracy**: Verified against standard reference software like Jagannatha Hora.

## Installation

```bash
pip install vedic_astro_engine_lite
```

## Quick Start

```python
from vedic_astro_engine import build_charts

# Build data for a specific moment (Lat/Lon for Bangalore)
data = build_charts(1996, 5, 27, 14, 18, lat=12.98, lon_deg=77.58)

# Access Vimshottari Dashas
print(data['dashas']['vimshottari'][0]['lord'])
```

## Licensing

### Open Source (AGPL-3.0)
This library is licensed under the **GNU Affero General Public License v3.0**. If you use this library in a public project, you must open-source your derivative work under the same license.

### Commercial / Pro Version
For features like **Shadbala**, **Yogas**, **Medical Astrology**, and **Professional PDF Reporting**, please contact the author for the Pro/Commercial version.

**For inquiries:**
📧 **prabhakarpanday4@gmail.com**

---
© 2026 Prabhakar Panday. All rights reserved.
