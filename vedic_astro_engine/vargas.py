"""
vargas.py — Divisional Chart (Varga) Calculations

Implements all 16 major Shodasha Vargas (D-1 to D-60) using 
classical Parasari rules.

Accuracy verified against BPHS (Brihat Parasara Hora Shastra).
"""

def get_all_vargas(longitude: float) -> dict:
    """
    Calculate all 16 major divisional charts for a given sidereal longitude.
    Returns 0-indexed signs (0=Aries, 11=Pisces).
    """
    v = {}
    sign_idx = int(longitude / 30) % 12
    rem = longitude % 30
    is_odd = (sign_idx % 2 == 0) # 0=Ar(Odd), 1=Ta(Even), 2=Ge(Odd)...
    
    # D1: Rashi (1 part of 30°)
    v['D1'] = sign_idx
    
    # D2: Hora (2 parts of 15°)
    # Odd: 0-15 Sun(Leo=4), 15-30 Moon(Cn=3)
    # Even: 0-15 Moon(Cn=3), 15-30 Sun(Leo=4)
    if is_odd:
        v['D2'] = 4 if rem < 15 else 3
    else:
        v['D2'] = 3 if rem < 15 else 4
        
    # D3: Drekkana (3 parts of 10°)
    # 1st: Self, 2nd: 5th from self, 3rd: 9th from self
    part3 = int(rem / 10.0)
    v['D3'] = (sign_idx + part3 * 4) % 12
    
    # D4: Chaturthamsa (4 parts of 7.5°)
    # 1st: Self, 2nd: 4th, 3rd: 7th, 4th: 10th
    part4 = int(rem / 7.5)
    v['D4'] = (sign_idx + part4 * 3) % 12
    
    # D7: Saptamsa (7 parts of 4.2857°)
    # Odd: Start from self. Even: Start from 7th from self.
    part7 = int(rem / (30.0 / 7.0))
    base7 = sign_idx if is_odd else (sign_idx + 6)
    v['D7'] = (base7 + part7) % 12
    
    # D9: Navamsha (9 parts of 3.3333°)
    # Ar/Le/Sg: Start Ar(0). Ta/Vi/Cp: Start Cp(9). Ge/Li/Aq: Start Li(6). Cn/Sc/Pi: Start Cn(3).
    total_nav = int(longitude / (30.0 / 9.0))
    v['D9'] = total_nav % 12
    
    # D10: Dashamsha (10 parts of 3°)
    # Odd: Start self. Even: Start 9th from self.
    part10 = int(rem / 3.0)
    base10 = sign_idx if is_odd else (sign_idx + 8)
    v['D10'] = (base10 + part10) % 12
    
    # D12: Dwadashamsha (12 parts of 2.5°)
    # Starts from self
    part12 = int(rem / 2.5)
    v['D12'] = (sign_idx + part12) % 12
    
    # D16: Shodashamsha (16 parts of 1.875°)
    # Movable: Ar(0). Fixed: Le(4). Dual: Sg(8).
    part16 = int(rem / 1.875)
    base16 = (sign_idx % 3) * 4 # 0->0, 1->4, 2->8
    v['D16'] = (base16 + part16) % 12
    
    # D20: Vimsamsa (20 parts of 1.5°)
    # Movable: Ar(0). Fixed: Sg(8). Dual: Le(4).
    part20 = int(rem / 1.5)
    base_map20 = {0: 0, 1: 8, 2: 4}
    v['D20'] = (base_map20[sign_idx % 3] + part20) % 12
    
    # D24: Chaturvimsamsa (24 parts of 1.25°)
    # Odd: Le(4). Even: Cn(3).
    part24 = int(rem / 1.25)
    base24 = 4 if is_odd else 3
    v['D24'] = (base24 + part24) % 12
    
    # D27: Sapta-Vimsamsa (27 parts of 1.111°)
    # Fire: Ar(0). Earth: Cn(3). Air: Li(6). Water: Cp(9).
    part27 = int(rem / (30.0 / 27.0))
    base27 = (sign_idx % 4) * 3 # 0->0, 1->3, 2->6, 3->9
    v['D27'] = (base27 + part27) % 12
    
    # D30: Trimsamsa (Non-equal)
    # Odd: 5°Ma(Ar), 5°Sa(Aq), 8°Ju(Sg), 7°Me(Ge), 5°Ve(Li)
    # Even: 5°Ve(Ta), 7°Me(Vi), 8°Ju(Pi), 5°Sa(Cp), 5°Ma(Sc)
    if is_odd:
        if rem < 5: v['D30'] = 0
        elif rem < 10: v['D30'] = 10
        elif rem < 18: v['D30'] = 8
        elif rem < 25: v['D30'] = 2
        else: v['D30'] = 6
    else:
        if rem < 5: v['D30'] = 1
        elif rem < 12: v['D30'] = 5
        elif rem < 20: v['D30'] = 11
        elif rem < 25: v['D30'] = 8 # Should be Sa(Capricorn=9)
        else: v['D30'] = 7
    # Fix D30 Sa even
    if not is_odd and 20 <= rem < 25: v['D30'] = 9

    # D40: Khavedamsa (40 parts of 0.75°)
    # Odd: Ar(0). Even: Li(6).
    part40 = int(rem / 0.75)
    base40 = 0 if is_odd else 6
    v['D40'] = (base40 + part40) % 12
    
    # D45: Akshavedamsa (45 parts of 0.666°)
    # Movable: Ar(0). Fixed: Le(4). Dual: Sg(8).
    part45 = int(rem / (30.0 / 45.0))
    base45 = (sign_idx % 3) * 4
    v['D45'] = (base45 + part45) % 12
    
    # D60: Shashtiamsha (60 parts of 0.5°)
    # Starts from sign itself
    part60 = int(rem / 0.5)
    v['D60'] = (sign_idx + part60) % 12
    
    return v
