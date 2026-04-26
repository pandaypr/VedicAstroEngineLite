"""
reports.py — Comprehensive PDF Report Engine (Modular)
Each chapter is a separate method for maintainability.
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
                                 Paragraph, Spacer, PageBreak, Flowable)

from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
import math

SIGN_NAMES = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]

NAK_NAMES  = ["Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra",
              "Punarvasu","Pushya","Ashlesha","Magha","Purva Phalguni",
              "Uttara Phalguni","Hasta","Chitra","Swati","Vishakha","Anuradha",
              "Jyeshtha","Mula","Purva Ashadha","Uttara Ashadha","Shravana",
              "Dhanishta","Shatabhisha","Purva Bhadrapada","Uttara Bhadrapada","Revati"]
PLANETS_7  = ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]
YOG_LORDS  = {"Mangala":"Moon","Pingala":"Sun","Dhanya":"Jupiter",
               "Bhramari":"Mars","Bhadrika":"Mercury","Ulka":"Saturn",
               "Siddha":"Venus","Sankata":"Rahu"}

# ── Colour palette ─────────────────────────────────────────────────────────────
C_HEAD  = colors.HexColor("#1a237e")   # dark indigo header
C_SUB   = colors.HexColor("#283593")   # subheader
C_ALT   = colors.HexColor("#e8eaf6")   # alternating row tint
C_WHITE = colors.whitesmoke
C_GRID  = colors.HexColor("#9fa8da")


def _fmt_lon(lon):
    """Convert decimal longitude → Deg°Min'Sec\" Sign"""
    sign_idx = int(lon / 30) % 12
    deg_in   = lon % 30
    d = int(deg_in)
    m = int((deg_in - d) * 60)
    s = int(((deg_in - d) * 60 - m) * 60)
    return f"{d:02d}°{m:02d}'{s:02d}\" {SIGN_NAMES[sign_idx]}"



def _nakshatra(lon):
    idx = int(lon / (360/27)) % 27
    pada = int((lon % (360/27)) / (360/27/4)) + 1
    return NAK_NAMES[idx], pada


def _parse_date(s):
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).strftime("%Y-%m-%d")
    except Exception:
        return str(s)[:10]


class PDFReportEngine:
    def __init__(self, filename, data):
        self.filename = filename
        self.data     = data
        self.styles   = getSampleStyleSheet()
        self.h1 = ParagraphStyle("h1", parent=self.styles["Heading1"],
                                  textColor=C_HEAD, spaceAfter=4)
        self.h2 = ParagraphStyle("h2", parent=self.styles["Heading2"],
                                  textColor=C_SUB, spaceAfter=3)
        self.h3 = ParagraphStyle("h3", parent=self.styles["Heading3"],
                                  textColor=colors.HexColor("#37474f"), spaceAfter=2)
        self.normal = self.styles["Normal"]
        self.small  = ParagraphStyle("small", parent=self.styles["Normal"], fontSize=7, leading=9)

    # ── helpers ──────────────────────────────────────────────────────────────
    def _h(self, text, level=2):
        s = {1: self.h1, 2: self.h2, 3: self.h3}.get(level, self.h2)
        return Paragraph(f"<b>{text}</b>", s)

    def _tbl(self, data, col_widths, header_row=True):
        # Format every cell as a Paragraph to support wrapping
        clean_data = []
        for r_idx, row in enumerate(data):
            clean_row = []
            for cell in row:
                if isinstance(cell, Paragraph):
                    clean_row.append(cell)
                    continue
                
                c_str = str(cell)
                # If header, make bold and white
                if r_idx == 0 and header_row:
                    p = Paragraph(f"<b>{c_str}</b>", 
                                  ParagraphStyle("h_cell", parent=self.small, 
                                                 textColor=colors.white, alignment=TA_CENTER))
                else:
                    p = Paragraph(c_str, self.small)
                clean_row.append(p)
            clean_data.append(clean_row)

        t = Table(clean_data, colWidths=col_widths, repeatRows=1 if header_row else 0)
        cmds = [
            ("GRID",    (0,0), (-1,-1), 0.4, C_GRID),
            ("VALIGN",  (0,0), (-1,-1), "TOP"),
            ("TOPPADDING", (0,0), (-1,-1), 4),
            ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ]
        if header_row:
            cmds += [
                ("BACKGROUND",(0,0),(-1,0), C_HEAD),
                ("ALIGN", (0,0), (-1,0), "CENTER"),
                ("VALIGN", (0,0), (-1,0), "MIDDLE"),
            ]
        # Alternating rows
        for i in range(1, len(data)):
            if i % 2 == 0:
                cmds.append(("BACKGROUND",(0,i),(-1,i), C_ALT))
        t.setStyle(TableStyle(cmds))
        return t



    def _sp(self, h=10):
        return Spacer(1, h)

    # ── generate ─────────────────────────────────────────────────────────────
    def generate(self):
        doc = SimpleDocTemplate(
            self.filename, pagesize=A4,
            rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30
        )
        el = []
        el.append(Paragraph("<b>KUDALI REPORT, BPHS BASED</b>",
                             ParagraphStyle("title", parent=self.styles["Title"],
                                            textColor=C_HEAD, spaceAfter=10)))
        el.append(self._sp(280))  # HUGE spacer to avoid overlapping with Kundali charts at the top
        self._page_basic_panchanga(el)
        el.append(PageBreak())

        # Shodashavarga (16 Charts) - Pages 2-5
        self._page_varga_group(el, "Divisional Charts (Shodashavarga) - I", ["D2", "D3", "D4", "D7"])
        el.append(PageBreak())
        self._page_varga_group(el, "Divisional Charts (Shodashavarga) - II", ["D10", "D12", "D16", "D20"])
        el.append(PageBreak())
        self._page_varga_group(el, "Divisional Charts (Shodashavarga) - III", ["D24", "D27", "D30", "D40"])
        el.append(PageBreak())
        self._page_varga_group(el, "Divisional Charts (Shodashavarga) - IV", ["D45", "D60"])
        el.append(PageBreak())


        self._page_planets(el)
        el.append(PageBreak())

        self._page_dashas(el)
        el.append(PageBreak())

        self._page_ashtakavarga(el)
        el.append(PageBreak())

        self._page_aspects(el)
        el.append(PageBreak())

        self._page_yogas(el)
        el.append(PageBreak())



        self._page_varshaphala(el)
        el.append(PageBreak())

        self._page_longevity(el)
        el.append(PageBreak())

        self._page_chakras_transits(el)
        el.append(PageBreak())

        self._page_shadbala(el)
        el.append(PageBreak())

        self._page_special_points(el)

        el.append(PageBreak())

        self._page_balarishta(el)

        doc.build(el, onFirstPage=self._draw_charts, onLaterPages=self._draw_charts)

    # ── placeholder page methods (filled in subsequent phases) ───────────────
    def _page_basic_panchanga(self, el):
        el.append(self._h("Basic Details & Panchanga", 2))
        p = self.data.get("panchanga", {})
        lagna = self.data.get("lagna", 0)
        rows = [
            ["Attribute", "Value"],
            ["Birth Date (UTC)", _parse_date(self.data.get("date_utc", ""))],
            ["Ayanamsha", f"{self.data.get('ayanamsha', 0):.4f}° (Lahiri)"],
            ["Lagna", _fmt_lon(lagna)],
            ["Sunrise", self.data.get("sunrise", "N/A")],
            ["Sunset",  self.data.get("sunset",  "N/A")],
            ["Tithi",    p.get("tithi", "N/A")],
            ["Nakshatra", p.get("nakshatra", "N/A")],
            ["Yoga",     p.get("yoga", "N/A")],
            ["Karana",   p.get("karana", "N/A")],
            ["Vara (Weekday)", p.get("vara", "N/A")],
        ]
        el.append(self._tbl(rows, [180, 300]))

    def _page_planets(self, el):
        el.append(self._h("Planetary Positions, Avasthas & KP Lords", 2))
        header = ["Planet", "Longitude", "Nakshatra/Pada", "House", "Shayana-Adi", "Baala-Adi", "Status"]
        rows = [header]
        skip = {"Uranus", "Neptune", "Pluto"}
        av_all = self.data.get("avasthas", {})
        for p, d in self.data.get("planets", {}).items():
            if p in skip: continue
            lon  = d.get("longitude", 0)
            nak, pada = _nakshatra(lon)
            house = d.get("house", "?")
            av = av_all.get(p, {})
            sh = av.get("shayana_adi", {})
            ba = av.get("baala_adi", {})
            sh_state = sh.get("state", "N/A") if isinstance(sh, dict) else "N/A"
            ba_state = ba.get("state", "N/A") if isinstance(ba, dict) else "N/A"
            status = d.get("status", "Direct")
            rows.append([p, _fmt_lon(lon), f"{nak} {pada}", house, sh_state, ba_state, status])
        el.append(self._tbl(rows, [55, 90, 100, 30, 80, 80, 65]))
        el.append(self._sp(12))
        # KP sublords
        el.append(self._h("KP Sublords (Sign / Nakshatra / Sub)", 3))
        kp_planets = self.data.get("kp", {}).get("planets", {})
        kp_rows = [["Planet", "Sign Lord", "Nak Lord", "Sub Lord", "Sub-Sub"]]
        for p in list(self.data.get("planets", {}).keys()) + ["Ascendant"]:
            if p in skip: continue
            kp = kp_planets.get(p, {})
            kp_rows.append([p, kp.get("sign_lord",""), kp.get("nakshatra_lord",""),
                            kp.get("sub_lord",""), kp.get("sub_sub_lord","")])
        el.append(self._tbl(kp_rows, [70, 70, 70, 70, 70]))
        el.append(self._sp(12))
        # Removed Kaals table as requested

    def _page_dashas(self, el):
        dashas = self.data.get("dashas", {})
        # ── 1. Vimshottari ───────────────────────────────────────────────────
        el.append(self._h("Vimshottari Dasha (Mahadasha & Antardasha)", 2))
        vim_rows = [["Level", "Lord", "Start", "End"]]
        for md in dashas.get("vimshottari", []):
            vim_rows.append(["MD", f"★ {md['lord']}", _parse_date(md["start"]), _parse_date(md["end"])])
            for ad in md.get("antardashas", []):
                vim_rows.append(["  AD", ad["lord"], _parse_date(ad["start"]), _parse_date(ad["end"])])
        t = Table(vim_rows, colWidths=[40, 90, 105, 105], repeatRows=1)
        cmds = [("GRID",(0,0),(-1,-1),0.4,C_GRID),("FONTSIZE",(0,0),(-1,-1),8),
                ("PADDING",(0,0),(-1,-1),3),
                ("BACKGROUND",(0,0),(-1,0),C_HEAD),("TEXTCOLOR",(0,0),(-1,0),C_WHITE),
                ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold")]
        # Highlight MD rows
        for i, row in enumerate(vim_rows):
            if i > 0 and row[0] == "MD":
                cmds.append(("BACKGROUND",(0,i),(-1,i),colors.HexColor("#c5cae9")))
                cmds.append(("FONTNAME",(0,i),(-1,i),"Helvetica-Bold"))
        t.setStyle(TableStyle(cmds))
        el.append(t); el.append(self._sp(14))

        # ── 2. Yogini ────────────────────────────────────────────────────────
        el.append(self._h("Yogini Dasha (36-Year Cycle)", 3))
        yog_rows = [["Yogini", "Lord", "Start", "End"]]
        for y in dashas.get("yogini", []):
            yog_rows.append([y.get("yogini",""), YOG_LORDS.get(y.get("yogini",""),""),
                             _parse_date(y["start"]), _parse_date(y["end"])])
        el.append(self._tbl(yog_rows, [90, 80, 105, 105]))
        el.append(self._sp(14))

        # ── 3. Chara ─────────────────────────────────────────────────────────
        el.append(self._h("Jaimini Chara Dasha (K.N. Rao)", 3))
        ch_rows = [["Sign", "Duration (yrs)", "Start", "End"]]
        for c in dashas.get("chara", []):
            ch_rows.append([c.get("sign",""), c.get("duration_years",""),
                            _parse_date(c["start"]), _parse_date(c["end"])])
        el.append(self._tbl(ch_rows, [90, 80, 105, 105]))
        el.append(self._sp(14))

        # ── 4. Kaal Chakra ───────────────────────────────────────────────────
        el.append(self._h("Kaal Chakra Dasha", 3))
        kcd_rows = [["Sign", "Duration (yrs)", "Start", "End"]]
        for c in dashas.get("kaal_chakra", []):
            kcd_rows.append([c.get("sign",""), c.get("duration_years",""),
                             _parse_date(c["start"]), _parse_date(c["end"])])
        el.append(self._tbl(kcd_rows, [90, 80, 105, 105]))

    def _page_ashtakavarga(self, el):
        el.append(self._h("Ashtakavarga System", 2))
        av = self.data.get("ashtakavarga", {})
        bav = av.get("bhinnashtakavarga", {})
        sav = av.get("sarvashtakavarga", [0]*12)
        analysis = av.get("analysis", {})

        # ── BAV table (7 planets × 12 signs) ─────────────────────────────────
        el.append(self._h("Bhinnashtakavarga (BAV) — Bindus per Planet per Sign", 3))
        sign_abbr = [s[:3] for s in SIGN_NAMES]
        bav_header = ["Planet"] + sign_abbr + ["Total"]
        bav_rows = [bav_header]
        for planet in PLANETS_7:
            row = bav.get(planet, [0]*12)
            bav_rows.append([planet] + row + [sum(row)])
        # SAV totals row
        bav_rows.append(["SAV"] + sav + [sum(sav)])
        t = Table(bav_rows, colWidths=[52]+[28]*12+[34], repeatRows=1)
        cmds = [("GRID",(0,0),(-1,-1),0.4,C_GRID),("FONTSIZE",(0,0),(-1,-1),7),
                ("PADDING",(0,0),(-1,-1),2),("ALIGN",(1,0),(-1,-1),"CENTER"),
                ("BACKGROUND",(0,0),(-1,0),C_HEAD),("TEXTCOLOR",(0,0),(-1,0),C_WHITE),
                ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
                # SAV row (last)
                ("BACKGROUND",(0,-1),(-1,-1),colors.HexColor("#c5cae9")),
                ("FONTNAME",(0,-1),(-1,-1),"Helvetica-Bold")]
        # Colour cells: >=5 green, <=2 red
        for r, planet in enumerate(PLANETS_7, start=1):
            row = bav.get(planet, [0]*12)
            for c, val in enumerate(row):
                if val >= 5:
                    cmds.append(("BACKGROUND",(c+1,r),(c+1,r),colors.HexColor("#a5d6a7")))
                elif val <= 2:
                    cmds.append(("BACKGROUND",(c+1,r),(c+1,r),colors.HexColor("#ef9a9a")))
        t.setStyle(TableStyle(cmds))
        el.append(t); el.append(self._sp(12))

        # ── SAV analysis ──────────────────────────────────────────────────────
        el.append(self._h("Sarvashtakavarga (SAV) Analysis", 3))
        sav_an = analysis.get("Sarvashtakavarga", {})
        info_rows = [["Metric", "Value"],
                     ["Total Bindus",        str(sav_an.get("total_bindus",""))],
                     ["Strongest Sign",      sav_an.get("strongest_sign","")],
                     ["Weakest Sign",        sav_an.get("weakest_sign","")],
                     ["Auspicious Zones",    ", ".join(sav_an.get("auspicious_zones",[]))],
                     ["Inauspicious Zones",  ", ".join(sav_an.get("inauspicious_zones",[]))]]
        el.append(self._tbl(info_rows, [160, 300]))
        el.append(self._sp(12))

        # ── Per-planet BAV analysis ───────────────────────────────────────────
        el.append(self._h("Per-Planet BAV Analysis", 3))
        pan_rows = [["Planet","Total Bindus","Natural Max","Natal Sign Bindus","Strength","Transit Benefic Signs"]]
        for planet in PLANETS_7:
            a = analysis.get(planet, {})
            pan_rows.append([planet, a.get("total_bindus",""), a.get("natural_max",""),
                             a.get("bindus_in_natal_sign",""), a.get("strength",""),
                             ", ".join(a.get("transit_benefic_signs",[])[:4])])
        el.append(self._tbl(pan_rows, [52, 55, 55, 60, 50, 178]))

    def _page_aspects(self, el):
        el.append(self._h("Graha Drishti (Planetary Aspects)", 2))
        
        # Add D1 chart with Drishti arrows here as a visual reference
        # We wrap it in a Table to center it
        chart = DiamondChart(self, 250, "D-1: Rashi (Aspect Visualization)", "D1", draw_drishti=True)
        el.append(Table([[chart]], colWidths=[500], style=[('ALIGN',(0,0),(-1,-1),'CENTER')]))
        el.append(self._sp(20))

        aspects_data = self.data.get("aspects", {})
        planet_aspects = aspects_data.get("planet_aspects", {})

        rows = [["Planet", "Aspects Received From"]]
        received = {p: [] for p in planet_aspects}
        for aspector, info in planet_aspects.items():
            for target in info.get("aspecting_planets", []):
                if target in received:
                    received[target].append(aspector)
                    
        for planet in PLANETS_7 + ["Rahu", "Ketu"]:
            if planet in received:
                aspectors = received[planet]
                rows.append([planet, ", ".join(aspectors) if aspectors else "None"])
        el.append(self._tbl(rows, [100, 370]))

        el.append(self._sp(12))

        # Ishta / Kashta Phala
        el.append(self._h("Ishta & Kashta Phala (Planetary Beneficence)", 3))
        ik = self.data.get("ishta_kashta", {})
        ik_rows = [["Planet", "Ishta (Good)", "Kashta (Bad)", "Result"]]
        for p in PLANETS_7:
            v = ik.get(p, {})
            ik_rows.append([p, str(v.get("ishta_phala","")), str(v.get("kashta_phala","")), v.get("dominant","")])
        el.append(self._tbl(ik_rows, [80, 120, 120, 80]))

    def _page_yogas(self, el):
        el.append(self._h("Yoga Identifications (All Categories)", 2))
        yogas = self.data.get("yogas", {})
        YOGA_LABELS = {
            "nabhasa": "Nabhasa (Celestial Pattern) Yogas",
            "raja":    "Raja Yogas (Power & Success)",
            "daridra": "Daridra Yogas (Poverty Indicators)",
            "surya":   "Surya (Solar) Yogas",
            "chandra": "Chandra (Lunar) Yogas",
            "combination": "Combination Yogas",
            "parivartana": "Parivartana (Exchange) Yogas",
            "raja_sambandha": "Raja Sambandha (Royal Connection) Yogas",
        }
        for key, label in YOGA_LABELS.items():
            entries = yogas.get(key, [])
            if not isinstance(entries, list) or not entries: continue
            el.append(self._h(label, 3))
            y_rows = [["Yoga Name", "Planets", "Description"]]
            for y in entries:
                name = y.get("yoga") or y.get("name") or "Yoga"
                planets = y.get("planets", [])
                if isinstance(planets, list): planets = ", ".join(planets)
                desc = Paragraph(y.get("description", y.get("desc", "")), self.normal)
                y_rows.append([name, str(planets), desc])
            el.append(self._tbl(y_rows, [110, 80, 280]))

            el.append(self._sp(8))
        # Tajik Yogas
        tajik = self.data.get("tajik_yogas", [])
        if tajik:
            el.append(self._h("Tajik Yogas (Annual Chart)", 3))
            t_rows = [["Yoga", "Planets", "Description"]]
            for y in tajik:
                desc = Paragraph(y.get("desc",""), self.normal)
                t_rows.append([y.get("yoga",""), ", ".join(y.get("planets",[])), desc])
            el.append(self._tbl(t_rows, [80, 100, 290]))

        # Jaimini Karakas are now displayed on the D1 chart directly

    def _page_varshaphala(self, el):
        el.append(self._h("Varshaphala — Tajika Annual Horoscopy", 2))
        muntha = self.data.get("muntha", 0)
        muntha_name = SIGN_NAMES[muntha-1] if isinstance(muntha, int) and 1<=muntha<=12 else str(muntha)
        
        # Date range for Varshaphala
        birth_date_str = self.data.get("date_utc", "")
        try:
            # Extract month and day from ISO string (e.g., "1992-11-14T...")
            b_dt = datetime.fromisoformat(birth_date_str.replace("Z", "+00:00"))
            b_month_day = b_dt.strftime("%b %d")
        except Exception:
            b_month_day = "Nov 14" # Fallback
            
        curr_year = datetime.now().year
        el.append(Paragraph(f"<b>Annual Prediction Year:</b> {curr_year}", self.normal))
        el.append(Paragraph(f"<b>Period:</b> {curr_year} {b_month_day} — {curr_year+1} {b_month_day}", self.normal))
        el.append(Paragraph(f"<b>Muntha Sign:</b> {muntha_name} (Focus of the Year)", self.normal))

        el.append(self._sp(8))
        # Sahams
        sahams = self.data.get("sphutas", {})
        if not sahams:
            sahams = {}
        sl = self.data.get("special_lagnas", {})
        if sl:
            el.append(self._h("Special Lagnas", 3))
            sl_rows = [["Lagna", "Longitude", "Sign"]]
            for name, lon in sl.items():
                sign = SIGN_NAMES[int(lon/30)%12]
                sl_rows.append([name, f"{lon:.2f}°", sign])
            el.append(self._tbl(sl_rows, [130, 100, 100]))
            el.append(self._sp(8))
    def _page_longevity(self, el):
        el.append(self._h("Longevity & Health (Ayurdaya)", 2))
        # Pinda Ayu
        lon_data = self.data.get("longevity", {})
        el.append(self._h("Pinda Ayu (Longevity Estimate)", 3))
        bkdn = lon_data.get("breakdown", {})
        la_rows = [["Planet/Point", "Years Contributed"]]
        for p, y in bkdn.items():
            la_rows.append([p, f"{y:.2f}"])
        la_rows.append(["Total (Unrefined)", f"{lon_data.get('total_unrefined',0):.2f} yrs"])
        el.append(self._tbl(la_rows, [150, 150]))
        el.append(self._sp(10))
        # Indu Lagna
        indu = self.data.get("indu_lagna", {})
        el.append(self._h("Indu Lagna (Wealth Point)", 3))
        indu_sign_idx = (indu.get("indu_sign", 1) - 1) % 12
        indu_sign_name = SIGN_NAMES[indu_sign_idx]
        el.append(Paragraph(f"<b>Indu Lagna:</b> {indu_sign_name}  |  "
                            f"9th lord from Lagna: {indu.get('l9_lord','')}  |  "
                            f"9th lord from Moon: {indu.get('m9_lord','')}  |  "
                            f"Total Units: {indu.get('total_units','')}", self.normal))
        el.append(self._sp(10))
        # Marakas
        marakas = self.data.get("marakas", {})
        pm = marakas.get("primary_marakas", [])
        if pm:
            el.append(self._h("Marakas (Death Inflictors)", 3))
            el.append(Paragraph(f"Primary Marakas: <b>{', '.join(pm)}</b>", self.normal))
            el.append(self._sp(8))
        # Health Vulnerabilities
        hv = self.data.get("health_vulnerabilities", [])
        if hv:
            el.append(self._h("Health Vulnerabilities (Based on D1 Chart)", 3))
            el.append(Paragraph("<i>Analysis of Kalapurusha based on planetary placements in the Natal Rashi (D1) chart houses.</i>", self.small))
            for v in hv:
                el.append(Paragraph(f"■ {v}", self.normal))

    def _page_chakras_transits(self, el):
        el.append(self._h("Chakras — Sudarshan & Sarvatobhadra", 2))
        # Sudarshan Chakra
        el.append(self._h("Sudarshan Chakra (Triple Ring View)", 3))
        el.append(Paragraph("<i>Inner: Sun, Middle: Moon, Outer: Lagna. Houses align based on sign number.</i>", self.small))
        el.append(self._sp(10))
        
        sc_chart = SudarshanChakra(self.data.get("sudarshan_chakra", {}))
        el.append(Table([[sc_chart]], colWidths=[500], style=[('ALIGN',(0,0),(-1,-1),'CENTER')]))
        el.append(self._sp(20))

        # SBC
        el.append(PageBreak())
        el.append(self._h("Sarvatobhadra Chakra — Vedha Analysis", 2))
        sbc_data = self.data.get("sarvatobhadra", {})
        sbc_chart = SBCGrid(sbc_data)
        el.append(Table([[sbc_chart]], colWidths=[500], style=[('ALIGN',(0,0),(-1,-1),'CENTER')]))
        el.append(self._sp(15))

        vedha = sbc_data.get("vedha_hits", [])
        if vedha:
            el.append(self._h("Vedha Hits (Transit -> Natal)", 3))
            v_rows = [["Transit Planet","Target Planet","Nakshatra","Type"]]
            for v in vedha:
                v_rows.append([v.get("transit_planet",""), v.get("target_planet",""),
                               v.get("nakshatra",""), v.get("type","")])
            el.append(self._tbl(v_rows, [110, 110, 130, 110]))
        else:
            el.append(Paragraph("No active Vedha hits found.", self.normal))

    def _page_shadbala(self, el):
        el.append(self._h("Shadbala — Six-fold Planetary Strength", 2))
        shadbala = self.data.get("shadbala", {})
        vimsopaka = self.data.get("vimsopaka", {})
        if not shadbala:
            el.append(Paragraph("Shadbala data not available.", self.normal))
            return

        # Visual Strength Bars
        el.append(self._h("Planetary Strength Visual Analysis", 3))
        sb_data = []
        for p in PLANETS_7:
            sb_data.append({
                "planet": p,
                "shadbala_rupas": shadbala.get(p, {}).get("rupas", 0),
                "vimsopaka": vimsopaka.get(p, 0)
            })
        el.append(StrengthBars(sb_data))
        el.append(self._sp(20))

        # Total table
        el.append(self._h("Total Strength Details", 3))
        rows = [["Planet", "Virupas", "Rupas", "Vimsopaka (Out of 20)"]]
        for p in PLANETS_7:
            d = shadbala.get(p, {})
            rows.append([p, str(d.get("virupas", 0)), str(d.get("rupas", 0)), str(vimsopaka.get(p, 0))])
        el.append(self._tbl(rows, [100, 100, 100, 100]))


        # Component breakdown
        el.append(self._h("Shadbala Component Breakdown (Virupas)", 3))
        comp_rows = [["Planet", "Sthana", "Dig", "Kala", "Cheshta", "Drig", "Naisargika"]]
        for p in PLANETS_7:
            c = shadbala.get(p, {}).get("components", {})
            comp_rows.append([p, str(c.get("sthana_bala",0)), str(c.get("dig_bala",0)),
                              str(c.get("kala_bala",0)), str(c.get("cheshta_bala",0)),
                              str(c.get("drig_bala",0)), str(c.get("naisargika_bala",0))])
        el.append(self._tbl(comp_rows, [70, 60, 60, 60, 60, 60, 70]))

    def _page_special_points(self, el):

        el.append(self._h("Special Points, Sphutas & Upagrahas", 2))
        # Sphutas
        sphutas = self.data.get("sphutas", {})
        if sphutas:
            el.append(self._h("Mathematical Sphutas", 3))
            sp_rows = [["Sphuta", "Longitude", "Sign"]]
            for name, lon in sphutas.items():
                sign = SIGN_NAMES[int(lon/30)%12]
                sp_rows.append([name, f"{lon:.4f}°", sign])
            el.append(self._tbl(sp_rows, [140, 100, 100]))
            el.append(self._sp(10))
        # Upagrahas
        ug = self.data.get("upagrahas", {})
        if ug:
            el.append(self._h("Upagrahas (Shadow Points)", 3))
            ug_rows = [["Upagraha", "Longitude", "Sign"]]
            for name, lon in ug.items():
                sign = SIGN_NAMES[int(lon/30)%12]
                ug_rows.append([name, _fmt_lon(lon), sign])
            el.append(self._tbl(ug_rows, [130, 130, 100]))
    def _page_balarishta(self, el):
        el.append(self._h("Balarishta & Arishta Bhanga", 2))
        # Balarishta
        bal = self.data.get("balarishta", [])
        el.append(self._h("Balarishta (Early-Life Adversities)", 3))
        if bal:
            b_rows = [["Name", "Severity", "Description"]]
            for b in bal:
                desc = Paragraph(b.get("description",""), self.normal)
                b_rows.append([b.get("name",""), b.get("severity",""), desc])
            el.append(self._tbl(b_rows, [110, 60, 300]))
        else:
            el.append(Paragraph("No Balarishta combinations found.", self.normal))
        el.append(self._sp(10))
        # Arishta Bhanga
        ab = self.data.get("arishta_bhanga", [])
        el.append(self._h("Arishta Bhanga (Cancellations of Evil)", 3))
        if ab:
            ab_rows = [["Cancellation", "Effect"]]
            for b in ab:
                eff = Paragraph(b.get("effect",""), self.normal)
                ab_rows.append([b.get("cancellation",""), eff])
            el.append(self._tbl(ab_rows, [150, 320]))
        else:
            el.append(Paragraph("No Arishta Bhanga applicable.", self.normal))
        el.append(self._sp(10))
        # Purva Janma Shapa
        pjs = self.data.get("purva_janma_shapa", [])
        el.append(self._h("Purva Janma Shapa (Past-Life Curses)", 3))
        if pjs:
            pjs_rows = [["Shapa", "Severity", "Description"]]
            for s in pjs:
                desc = Paragraph(s.get("description",""), self.normal)
                pjs_rows.append([s.get("shapa",""), s.get("severity",""), desc])
            el.append(self._tbl(pjs_rows, [110, 60, 300]))
        else:
            el.append(Paragraph("No Purva Janma Shapa detected.", self.normal))


    def _page_varga_group(self, el, title, vargas):
        el.append(self._h(title, 2))
        # Spacer for 2x2 grid (approx 450 points)
        el.append(self._sp(480))

    # ── canvas chart drawing ──────────────────────────────────────────────────
    def _draw_charts(self, canv, doc):
        # Full Varga names for titles
        V_NAMES = {
            "D1": "D-1: Rashi", "D2": "D-2: Hora", "D3": "D-3: Drekkana",
            "D4": "D-4: Chaturthamsa", "D7": "D-7: Saptamsa", "D9": "D-9: Navamsha",
            "D10": "D-10: Dashamsha", "D12": "D-12: Dwadashamsha", "D16": "D-16: Shodashamsha",
            "D20": "D-20: Vimsamsha", "D24": "D-24: Chaturvimsamsha", "D27": "D-27: Saptavimsamsha",
            "D30": "D-30: Trimsamsha", "D40": "D-40: Khavedamsha", "D45": "D-45: Akshavedamsha",
            "D60": "D-60: Shastiamsha"
        }
        
        page_map = {
            1: [("D1", 50, 550), ("D9", 310, 550)],
            2: [("D2", 50, 550), ("D3", 310, 550), ("D4", 50, 300), ("D7", 310, 300)],
            3: [("D10", 50, 550), ("D12", 310, 550), ("D16", 50, 300), ("D20", 310, 300)],
            4: [("D24", 50, 550), ("D27", 310, 550), ("D30", 50, 300), ("D40", 310, 300)],
            5: [("D45", 50, 550), ("D60", 310, 550)],
        }

        page_map = {
            1: [("D1", 50, 550, False), ("D9", 310, 550, False)],
            2: [("D2", 50, 550, False), ("D3", 310, 550, False), ("D4", 50, 300, False), ("D7", 310, 300, False)],
            3: [("D10", 50, 550, False), ("D12", 310, 550, False), ("D16", 50, 300, False), ("D20", 310, 300, False)],
            4: [("D24", 50, 550, False), ("D27", 310, 550, False), ("D30", 50, 300, False), ("D40", 310, 300, False)],
            5: [("D45", 50, 550, False), ("D60", 310, 550, False)],
        }

        if doc.page in page_map:
            for v_key, x, y, drishti in page_map[doc.page]:
                self._diamond(canv, x, y, 210, V_NAMES.get(v_key, v_key), v_key, draw_drishti=drishti)

    def _diamond(self, canv, x, y, size, title, varga_key, draw_drishti=False):


        canv.setStrokeColor(colors.black); canv.setLineWidth(0.8)
        canv.rect(x, y, size, size)
        canv.line(x, y, x+size, y+size); canv.line(x+size, y, x, y+size)
        canv.line(x+size/2, y, x, y+size/2); canv.line(x, y+size/2, x+size/2, y+size)
        canv.line(x+size/2, y+size, x+size, y+size/2); canv.line(x+size, y+size/2, x+size/2, y)
        canv.setFont("Helvetica-Bold", 8)
        canv.drawCentredString(x+size/2, y+size+6, title)
        # Planet text coordinates (centers of houses)
        coords = {
            1:(x+size/2,y+size*0.75), 2:(x+size*0.25,y+size*0.875),
            3:(x+size*0.125,y+size*0.75), 4:(x+size*0.25,y+size/2),
            5:(x+size*0.125,y+size*0.25), 6:(x+size*0.25,y+size*0.125),
            7:(x+size/2,y+size*0.25), 8:(x+size*0.75,y+size*0.125),
            9:(x+size*0.875,y+size*0.25),10:(x+size*0.75,y+size/2),
            11:(x+size*0.875,y+size*0.75),12:(x+size*0.75,y+size*0.875)
        }
        # Sign number coordinates (refined based on red-arrow feedback)
        sn_coords = {
            1:  (x+size*0.5,     y+size*0.5 + 8),
            2:  (x+size*0.25 + 14, y+size*0.75 + 4), 
            3:  (x+size*0.25 - 4,  y+size*0.75 + 14), 
            4:  (x+size*0.5 - 14,  y+size*0.5),
            5:  (x+size*0.25 - 4,  y+size*0.25 - 14),
            6:  (x+size*0.25 + 14, y+size*0.25 - 4),
            7:  (x+size*0.5,     y+size*0.5 - 18),
            8:  (x+size*0.75 - 14, y+size*0.25 - 4),
            9:  (x+size*0.75 + 4,  y+size*0.25 - 14),
            10: (x+size*0.5 + 12,  y+size*0.5),
            11: (x+size*0.75 + 4,  y+size*0.75 + 14),
            12: (x+size*0.75 - 14, y+size*0.75 + 4)
        }
        vargas_all = self.data.get("vargas", {})
        jk = self.data.get("jaimini_karakas", {})
        lagna_v = int(vargas_all.get("Ascendant", {}).get(varga_key, 0))
        
        # Draw Rashi numbers near edges
        canv.setFont("Helvetica-Oblique", 6)
        for h in range(1, 13):
            sx, sy = sn_coords[h]
            sn = (lagna_v + h - 1) % 12
            canv.drawCentredString(sx, sy, f"{sn+1}")
        
        pih = {}
        # Invert JK to get planet -> karaka
        planet_to_jk = {}
        for k, info in jk.items():
            p = info.get("planet")
            if p: planet_to_jk[p] = k

        for p, vd in vargas_all.items():
            if p in ["Ascendant","Uranus","Neptune","Pluto"]: continue
            ps = vd.get(varga_key, 0)
            h_num = (ps - lagna_v) % 12 + 1
            pih.setdefault(h_num, []).append(p)
        
        # Draw Planets
        canv.setFont("Helvetica", 7)
        for h, pts in pih.items():
            cx, cy = coords[h]
            # Planet string: Su Mo...
            p_str = " ".join([pt[:2] for pt in pts])
            canv.drawCentredString(cx, cy, p_str)
            
            # If D1, draw Karakas underneath in light grey
            if varga_key == "D1":
                canv.saveState()
                canv.setFillColor(colors.grey)
                canv.setFont("Helvetica", 5)
                k_list = [planet_to_jk.get(pt, "") for pt in pts if planet_to_jk.get(pt)]
                if k_list:
                    canv.drawCentredString(cx, cy-7, " ".join(k_list))
                canv.restoreState()

        # Graha Drishti Arrows (only for D1)
        if varga_key == "D1" and draw_drishti:
            canv.setLineWidth(0.3)

            p_colors = {
                "Sun": colors.HexColor("#FFB300"), "Moon": colors.HexColor("#78909C"),
                "Mars": colors.HexColor("#D32F2F"), "Mercury": colors.HexColor("#2E7D32"),
                "Jupiter": colors.HexColor("#F9A825"), "Venus": colors.HexColor("#EC407A"),
                "Saturn": colors.HexColor("#37474F")
            }
            # Define Aspects
            aspects_map = {
                "Sun": [7], "Moon": [7], "Mercury": [7], "Venus": [7],
                "Mars": [4, 7, 8], "Jupiter": [5, 7, 9], "Saturn": [3, 7, 10]
            }
            for h_start, pts in pih.items():
                for p in pts:
                    if p in aspects_map:
                        canv.setStrokeColor(p_colors.get(p, colors.grey))
                        for asp in aspects_map[p]:
                            h_end = (h_start + asp - 2) % 12 + 1
                            x1, y1 = coords[h_start]
                            x2, y2 = coords[h_end]
                            # Draw thin arrow
                            self._draw_arrow(canv, x1, y1, x2, y2)

    def _draw_arrow(self, canv, x1, y1, x2, y2):
        # Draw line from center to center but slightly offset or shortened
        dx, dy = x2-x1, y2-y1
        dist = math.sqrt(dx**2 + dy**2)
        if dist == 0: return
        # Shorten line slightly to not touch the labels
        margin = 12
        x_s, y_s = x1 + (dx/dist)*margin, y1 + (dy/dist)*margin
        x_e, y_e = x2 - (dx/dist)*margin, y2 - (dy/dist)*margin
        canv.line(x_s, y_s, x_e, y_e)
        
        # Draw tiny arrow head
        angle = math.atan2(dy, dx)
        a_size = 3
        canv.line(x_e, y_e, x_e - a_size*math.cos(angle - 0.5), y_e - a_size*math.sin(angle - 0.5))
        canv.line(x_e, y_e, x_e - a_size*math.cos(angle + 0.5), y_e - a_size*math.sin(angle + 0.5))



class DiamondChart(Flowable):
    """Flowable wrapper for the diamond chart to place it anywhere in the report."""
    def __init__(self, engine, size, title, varga_key, draw_drishti=False):
        Flowable.__init__(self)
        self.engine = engine
        self.size = size
        self.title = title
        self.varga_key = varga_key
        self.draw_drishti = draw_drishti
        self.width = size
        self.height = size + 20

    def draw(self):
        # Translate to 0,0 for the diamond drawer
        self.engine._diamond(self.canv, 0, 0, self.size, self.title, self.varga_key, self.draw_drishti)


class SudarshanChakra(Flowable):

    def __init__(self, sc_data):
        Flowable.__init__(self)
        self.sc_data = sc_data
        self.width = 300
        self.height = 300

    def draw(self):
        canv = self.canv
        size = 300
        cx, cy = size/2, size/2
        canv.setLineWidth(0.5)
        canv.setStrokeColor(C_GRID)
        
        # Draw 3 Rings
        radii = [40, 75, 110]
        for r in radii:
            canv.circle(cx, cy, r)
            
        # Draw 12 radial lines
        for i in range(12):
            angle = math.radians(i * 30 - 90)
            canv.line(cx + 15*math.cos(angle), cy + 15*math.sin(angle), 
                      cx + 130*math.cos(angle), cy + 130*math.sin(angle))
            # Sign numbers on outer edge
            canv.setFont("Helvetica-Bold", 7)
            canv.drawCentredString(cx + 120*math.cos(angle + math.radians(15)), 
                                   cy + 120*math.sin(angle + math.radians(15)), str(i+1))

        # Place Planets
        canv.setFont("Helvetica", 6)
        perspectives = ["from_sun", "from_moon", "from_lagna"]
        for p_idx, p_key in enumerate(perspectives):
            r = radii[p_idx] + 15
            for h in range(1, 13):
                # We need to map house index to sign number if needed, 
                # but sc_data uses house keys 1..12 where 1 is Aries for alignment
                pts = self.sc_data.get(h, {}).get(p_key, [])
                if pts:
                    angle = math.radians((h-1)*30 - 75)
                    p_str = "".join([pt[:2] for pt in pts])
                    canv.drawCentredString(cx + r*math.cos(angle), cy + r*math.sin(angle), p_str)

class SBCGrid(Flowable):
    def __init__(self, sbc_data):
        Flowable.__init__(self)
        self.sbc_data = sbc_data
        self.width = 350
        self.height = 350
        # 28 Nakshatras including Abhijit
        self.nak_28 = [
            "Ashwi", "Bhara", "Kritt", "Rohin", "Mriga", "Ardra", "Punar",
            "Pushy", "Ashle", "Magha", "P.Pha", "U.Pha", "Hasta",
            "Chitr", "Swati", "Visha", "Anura", "Jyesh", "Mula", "P.Ash",
            "U.Ash", "Abhij", "Shrav", "Dhani", "Shatab", "P.Bha", "U.Bha", "Revat"
        ]

    def draw(self):
        canv = self.canv
        size = 350
        sq = size / 9
        canv.setLineWidth(0.4)
        canv.setStrokeColor(colors.grey)
        
        # Draw 9x9 Grid
        for i in range(10):
            canv.line(0, i*sq, size, i*sq)
            canv.line(i*sq, 0, i*sq, size)
        
        # Populate outer boundary (Nakshatras)
        canv.setFont("Helvetica", 5)
        canv.setFillColor(colors.black)
        
        # Mapping Nakshatras to grid cells
        # Top (2-8)
        for i in range(7):
            canv.drawCentredString((i+1)*sq + sq/2, 8*sq + sq/2, self.nak_28[i+2])
        # Right (9-15)
        for i in range(7):
            canv.drawCentredString(8*sq + sq/2, (7-i)*sq + sq/2, self.nak_28[i+9])
        # Bottom (16-22)
        for i in range(7):
            canv.drawCentredString((7-i)*sq + sq/2, 0*sq + sq/2, self.nak_28[i+16])
        # Left (23,24,25,26,27,0,1)
        left_naks = [23, 24, 25, 26, 27, 0, 1]
        for i in range(7):
            canv.drawCentredString(0*sq + sq/2, (i+1)*sq + sq/2, self.nak_28[left_naks[i]])

        # Corners
        canv.setFont("Helvetica-Bold", 8)
        canv.drawCentredString(sq/2, 8*sq + sq/2, "A")
        canv.drawCentredString(8*sq + sq/2, 8*sq + sq/2, "I")
        canv.drawCentredString(8*sq + sq/2, sq/2, "U")
        canv.drawCentredString(sq/2, sq/2, "E")

        # Center Title
        canv.setFont("Helvetica-Bold", 10)
        canv.setFillColor(colors.HexColor("#1a237e"))
        canv.drawCentredString(size/2, size/2, "SBC")
        canv.setFont("Helvetica", 6)
        canv.drawCentredString(size/2, size/2 - 12, "Transit Analysis")


class StrengthBars(Flowable):
    def __init__(self, sb_data):
        Flowable.__init__(self)
        self.sb_data = sb_data
        self.width = 400
        self.height = len(sb_data) * 20 + 20

    def draw(self):
        canv = self.canv
        canv.setFont("Helvetica-Bold", 8)
        canv.drawString(50, self.height - 10, "Planet")
        canv.drawString(100, self.height - 10, "Shadbala (Rupas)")
        canv.drawString(250, self.height - 10, "Vimsopaka (0-20)")
        
        y = self.height - 30
        for d in self.sb_data:
            canv.setFont("Helvetica", 7)
            canv.drawString(50, y, d["planet"])
            
            # Shadbala Bar
            shad = d["shadbala_rupas"]
            # Max expected ~10 rupas
            bw = min(120, shad * 12)
            canv.setFillColor(C_HEAD)
            canv.rect(100, y-2, bw, 8, fill=1)
            canv.setFillColor(colors.black)
            canv.drawString(100 + bw + 5, y, f"{shad:.2f}")
            
            # Vimsopaka Bar
            vim = d["vimsopaka"]
            vw = min(100, vim * 5)
            canv.setFillColor(colors.HexColor("#388E3C"))
            canv.rect(250, y-2, vw, 8, fill=1)
            canv.setFillColor(colors.black)
            canv.drawString(250 + vw + 5, y, f"{vim:.1f}")
            
            y -= 20


def generate_pdf_report(data, filename="comprehensive_report.pdf"):

    PDFReportEngine(filename, data).generate()
    return filename
