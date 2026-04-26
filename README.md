# VedicAstroEngine

**VedicAstroEngine** is a high-precision, professional-grade Python library for Vedic (Hindu) Astrology. Built on top of the robust **Skyfield** astronomical library and NASA's JPL ephemerides, it provides a complete suite of calculations for predictive, electional, and medical astrology.

## 🚀 Key Advantages

### 🛡️ Completely Free of Swiss Ephemeris (`pyswisseph`)
VedicAstroEngine is **completely independent of the Swiss Ephemeris library**.
- **No Licensing Headaches**: Free from the restrictive dual-licensing (GPL/Commercial) of Swiss Ephemeris.
- **Pure Python & NASA JPL Power**: Uses NASA's DE421/DE440 ephemerides via Skyfield for state-of-the-art precision.
- **Lightweight**: No complex C-extensions to compile; works seamlessly across all platforms.

### ✅ Validated & Professional Grade
This engine has been rigorously **validated and tested against professional astrological software** (such as Jagannatha Hora) to ensure identical results for core and advanced calculations.

## 🌟 Features (Full Version)

- **Shodashavarga**: High-resolution calculation of all 16 divisional charts (D-1 to D-60).
- **Planetary Strength**: Full implementation of **Shadbala** (six-fold strength), **Vimsopaka Bala**, and Ishta/Kashta Phala.
- **Professional PDF Engine**: Generate stunning multi-page Kundali reports with traditional diamond charts, Sudarshan Chakra, and SBC grids.
- **Predictive Modules**: Vimshottari, Yogini, Chara, and Kaal Chakra Dashas.
- **Comprehensive Yoga System**: Detection of thousands of Nabhasa, Raja, and Dhana Yogas.
- **Matchmaking & Kuja Dosha**: Full Ashtakoota Guna Milan and Manglik analysis.
- **Medical Astrology**: Longevity (Pinda/Amsa Ayu), health vulnerabilities, and Balarishta.
- **Muhurta & Transit**: Real-time detection of auspicious times and SBC Vedha.

## Installation

```bash
pip install vedic_astro_engine_lite
```

## Quick Start

```python
from vedic_astro_engine import build_charts, generate_pdf_report

# Build data for a specific moment (Lat/Lon for Bangalore)
data = build_charts(1996, 5, 27, 14, 18, lat=12.98, lon_deg=77.58)

# Generate a professional PDF report
generate_pdf_report(data, "My_Kundali_Report.pdf")
```

## 📜 Licensing (AGPL-3.0)

This project is licensed under the **GNU Affero General Public License v3.0**. 

- **Open Source**: The full professional engine is free for everyone to use, modify, and distribute for open-source projects.
- **Copyleft**: If you use this library in a public project or a web service, you must release your derivative work under the same AGPL license.
- **Commercial Use**: Commercial use is permitted, provided you adhere to the AGPL terms (releasing your source code). For closed-source commercial needs, please contact the author.

**For inquiries:**
📧 **prabhakarpanday4@gmail.com**

---
© 2026 Prabhakar Panday. All rights reserved.
