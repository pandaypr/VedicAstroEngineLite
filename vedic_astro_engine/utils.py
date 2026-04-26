"""
utils.py — Shared utilities to break circular imports.
"""

from skyfield.api import load

_eph = None
_ts = None

def load_ephemeris():
    """Loads NASA DE421 ephemeris and Skyfield timescale once."""
    global _eph, _ts
    if _eph is None:
        _ts = load.timescale()
        # Look for local bsp first, then download
        import os
        bsp_path = "de421.bsp"
        if os.path.exists(bsp_path):
            _eph = load(bsp_path)
        else:
            _eph = load("de421.bsp")
    return _ts, _eph

def _sign(lon):
    """1-indexed sign (1-12)."""
    return int(lon / 30.0) % 12 + 1

def _house_of(lon, asc_lon):
    """1-indexed house of a longitude relative to an ascendant."""
    return int((lon - asc_lon) % 360 / 30) + 1
