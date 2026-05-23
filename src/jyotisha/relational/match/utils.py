# src/ci_match/utils.py

def get_nakshatra_idx(deg_longitude):
    """0-based index of Nakshatra (0..26)"""
    # 27 Nakshatras in 360 degrees = 13.3333 deg each
    return int(deg_longitude // (360/27))

def get_pada(deg_longitude):
    """1-based Pada number (1..4)"""
    nak_len = 360/27
    intra_nak = deg_longitude % nak_len
    pada_len = nak_len / 4
    return int(intra_nak // pada_len) + 1

def get_rashi_idx(deg_longitude):
    """1-based Rashi index (1..12)"""
    return int(deg_longitude // 30) + 1
