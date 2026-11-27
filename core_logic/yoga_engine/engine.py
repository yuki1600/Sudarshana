"""engine: part of yoga_engine (split from one module; see __init__.py)."""
from typing import Any, Dict, List, Optional, Sequence, Tuple
from .. import house_systems as H
from .. import dasa_systems as JD
from .. import natal_chart as N
from .. import sign_strength as SS
from ..shadbala import NATURAL_RELATIONS_9, compound_relationships
from .catalogue import ASCETIC, BASIS, BASIS_NAMES, BENEFICS, CATALOGUE, CO_LORDS, DEBIL, DHANA_5_11, DHANA_LAGNA, EXALT, GIVER_CODES, GROUPS, LORDS, MALEFICS, MAX_YOGAS, MOOLA, NAABHASA_GIVERS, OCCUPANCY

def rasi_drishti(a: int, b: int) -> bool:
    """Rasi drishti (BPHS 8.1-5): sign a aspects sign b, or is b (movable <-> fixed except adjacent, dual <-> dual)."""
    if a == b:
        return True
    if a % 3 == 2:
        return b % 3 == 2
    return b % 3 == (1 if a % 3 == 0 else 0) and (a + 1) % 12 != b and (b + 1) % 12 != a


def graha_drishti(p: int, a: int, b: int) -> bool:
    """Graha drishti by sign (BPHS 26.2-5): planet p in sign a aspects sign b (7th; Mars 4/8, Jupiter 5/9, Saturn
    3/10; Rahu 5/9/2 and Ketu none are a convention of the reference catalogue)."""
    if p == 9:
        return False
    d = (b - a) % 12
    return d == 6 or d in {3: (3, 7), 5: (4, 8), 7: (2, 9), 8: (4, 8, 1)}.get(p, ())


def owns(p: int, sign: int) -> bool:
    """Sign lordship, Rahu co-owning Aquarius and Ketu Scorpio (BPHS 47.34-39)."""
    return LORDS[sign] == p or (sign == 10 and p == 8) or (sign == 7 and p == 9)


class _Yogas:
    """The yoga search over one chart: ``s[p]`` signs of the points in the varga, ``occ[m][sign]`` the five
    occupancy counts (``OCCUPANCY``), ``out`` the result records (group, index, givers)."""

    def __init__(self, s: Dict[int, int], vargas: Dict[int, Sequence[int]], karakas: Sequence[int],
                 lagna_degree: int, compound: Sequence[Sequence[int]],
                 houses: Optional[Sequence[int]] = None, cusps: Optional[Sequence[int]] = None):
        """``vargas``: signs of points 0 .. 9 in the vargas some checks read whatever varga is chosen
        (index 0 D-1, 1 D-9, 2 D-2, 3 D-3, 11 D-12, 16 D-30).  ``houses`` (0-based bhava of points 0 .. 9) and
        ``cusps`` (sign of each bhava's cusp) switch the house reads to bhavas; left out, a house is a sign."""
        self.s, self.k, self.lagna_degree, self.comp = s, karakas, lagna_degree, compound
        self.d1, self.d9, self.moon_d3 = vargas[0], vargas[1], vargas[3][2]
        self.aspect_vargas = [vargas[i] for i in (0, 1, 2, 3, 11, 16)]
        self.occ = [[sum(1 for p in m if s[p] == x) for x in range(12)] for m in OCCUPANCY]
        self.h = list(houses) if houses is not None else [(s[p] - s[0]) % 12 for p in range(10)]
        self.cusp = list(cusps) if cusps is not None else [(s[0] + i) % 12 for i in range(12)]
        self.hocc = [[sum(1 for p in m if self.h[p] == d) for d in range(12)] for m in OCCUPANCY]   # occ by house
        self.out: List[Dict[str, Any]] = []

    # --- helpers
    def lord(self, house: int) -> int:              # lord of the sign on the house's cusp
        return LORDS[self.cusp[house - 1]]

    def d0(self, p: int) -> int:                    # 0-based house of p from lagna
        return self.h[p]

    def kk(self, p: int) -> bool:                   # p in a kendra or kona from lagna
        return self.d0(p) % 3 == 0 or self.d0(p) % 4 == 0

    def strong(self, p: int) -> bool:               # own or exaltation sign
        return owns(p, self.s[p]) or EXALT[p] == self.s[p]

    def friendly(self, p: int) -> bool:             # own / exalted / natural friend / compound (great) friend
        lord = LORDS[self.s[p]]
        return self.strong(p) or NATURAL_RELATIONS_9[p - 1][lord - 1] == 2 or self.comp[p - 1][lord - 1] in (1, 2)

    def well(self, p: int) -> bool:                 # kendra / kona or friendly
        return self.kk(p) or self.friendly(p)

    def ra(self, p: int, q: int) -> bool:           # rasi aspect (or conjunction) of two points
        return rasi_drishti(self.s[p], self.s[q])

    def maraka_on(self, sign: int) -> bool:         # a maraka on the sign
        m2, m7 = self.cusp[1], self.cusp[6]
        return any((self.h[p] in (1, 6) or owns(p, m2) or owns(p, m7)) and rasi_drishti(self.s[p], sign)
                   for p in range(1, 10))

    def add(self, group: int, index: int, givers: Sequence[int] = (), extra: str = "") -> None:
        if len(self.out) < MAX_YOGAS:
            self.out.append({"group": group, "index": index, "givers": list(givers), "extra": extra})

    def in_signs(self, planets: Sequence[int], signs: Sequence[int]) -> List[int]:
        return [p for p in planets if self.s[p] in signs]

    def from_sign(self, sign: int, *houses: int) -> List[int]:
        return [(sign + h - 1) % 12 for h in houses]

    # --- group 1, Pancha Mahapurusha (BPHS 75.1-2; PD 6.1-4)
    def mahapurusha(self):
        for idx, (p, signs) in enumerate(((5, (8, 11, 3)), (6, (1, 6, 11)), (4, (2, 5)), (3, (0, 7, 9)),
                                          (7, (9, 10, 6)))):
            if self.d0(p) % 3 == 0 and self.s[p] in signs:
                self.add(1, idx, [p])

    # --- group 2, solar (BPHS 38.1-3): Mars .. Saturn from the Sun
    def solar(self):
        vesi = [p for p in range(3, 8) if (self.s[p] - self.s[1]) % 12 == 1]
        vosi = [p for p in range(3, 8) if (self.s[p] - self.s[1]) % 12 == 11]
        if vosi and vesi:
            self.add(2, 0, vesi + vosi)
        elif vesi:
            self.add(2, 1, vesi)
        elif vosi:
            self.add(2, 2, vosi)
        if (self.s[4] - self.s[1]) % 12 in (0, 6):
            self.add(2, 3, [1, 4])

    # --- group 3, lunar (BPHS 37; Gaja-Kesari 36.3-4)
    def lunar(self):
        suna = [p for p in range(3, 8) if (self.s[p] - self.s[2]) % 12 == 1]
        ana = [p for p in range(3, 8) if (self.s[p] - self.s[2]) % 12 == 11]
        if ana and suna:
            self.add(3, 0, suna + ana)
        elif suna:
            self.add(3, 1, suna)
        elif ana:
            self.add(3, 2, ana)
        elif all(self.d0(p) % 3 != 0 or p == 2 for p in range(1, 8)):   # Kemadruma: kendras from lagna
            self.add(3, 3, [2])
        if (self.s[3] - self.s[2]) % 12 in (0, 6):
            self.add(3, 4, [2, 3])
        if (self.s[5] - self.s[2]) % 3 == 0:
            self.add(3, 5, [2, 5])
        near = [p for p in range(1, 8) if (self.s[p] - self.s[2]) % 12 in (5, 6, 7)]
        good = [p for p in near if p in BENEFICS]                         # Adhi: Mercury, Jupiter, Venus
        if len(good) > 1 and len(near) - len(good) <= len(good):
            self.add(3, 6, good)

    # --- group 4, nabhasa (BPHS 35; Sankhya 35.16-17)
    def nabhasa(self):
        o = self.occ[0]                                                   # by sign
        ho, b, m = self.hocc[0], self.hocc[1], self.hocc[4]               # by house
        for idx in range(3):                                              # Rajju, Musala, Nala
            if all(o[x] == 0 or x % 3 == idx for x in range(12)):
                self.add(4, idx)
        if sum(1 for d in (0, 3, 6, 9) if 0 < b[d] and m[d] <= b[d]) > 2:   # Maalaa
            self.add(4, 3)
        if sum(1 for d in (0, 3, 6, 9) if 0 < m[d] and b[d] <= m[d]) > 2:   # Sarpa
            self.add(4, 4)
        only = lambda test: all(ho[d] == 0 or test(d) for d in range(12))
        exactly = lambda test: all((ho[d] != 0) == test(d) for d in range(12))
        # Sankhya (Gola .. Veena) runs last in the display order; listed here in its place
        if any(only(lambda d, a=a, c=c: d in (a, c)) for a, c in ((0, 3), (3, 6), (6, 9), (9, 0))):
            self.add(4, 12)                                               # Gadaa
        if only(lambda d: d in (0, 6)):                                   # Sakata
            self.add(4, 13)
        if only(lambda d: d in (3, 9)):                                   # Vihanga
            self.add(4, 14)
        if only(lambda d: d % 4 == 0):                                    # Sringaataka
            self.add(4, 15)
        if any(only(lambda d, r=r: d % 4 == r) for r in (1, 2, 3)):       # Hala
            self.add(4, 16)
        if m[0] < b[0] and m[6] < b[6] and b[3] < m[3] and b[9] < m[9]:
            self.add(4, 17)                                               # Vajra
        if m[3] < b[3] and m[9] < b[9] and b[0] < m[0] and b[6] < m[6]:
            self.add(4, 18)                                               # Yava
        if exactly(lambda d: d % 3 == 0):                                 # Kamala
            self.add(4, 19)
        if exactly(lambda d: d % 3 == 1) or exactly(lambda d: d % 3 == 2):
            self.add(4, 20)                                               # Vaapi
        for idx, first in ((21, 0), (22, 3), (23, 6), (24, 9)):           # Yoopa, Sara, Sakti, Danda
            if exactly(lambda d, f=first: (d - f) % 12 < 4):
                self.add(4, idx)
        run, start = 0, 0                                                 # Naukaa .. Ardha-Chandra (BPHS 35.14)
        for x in range(24):                                               # houses; the run of 7 is unique
            if ho[x % 12] == 0:
                run = 0
                continue
            if run == 0:
                start = x % 12
            run += 1
            if run == 7:
                self.add(4, {0: 25, 3: 26, 6: 27, 9: 28}.get(start, 29))
                break
        if exactly(lambda d: d % 2 == 0):                                 # Chakra
            self.add(4, 30)
        if exactly(lambda d: d % 2 == 1):                                 # Samudra
            self.add(4, 31)
        self.add(4, sum(1 for x in range(12) if o[x] > 0) + 4)            # Sankhya: 1 sign Gola (5) .. 7 Veena

    # --- group 5, other popular yogas (BPHS 36, PD 6; YOGA_SOURCES)
    def other(self):
        s, b, m, L = self.s, self.occ[1], self.occ[4], self.s[0]
        hb, hm = self.hocc[1], self.hocc[4]                               # benefics / malefics by house
        LL = self.lord(1)
        ben_in = lambda *houses: [p for p in BENEFICS if self.d0(p) + 1 in houses]
        # Subha / Asubha (BPHS 36.1-2)
        if hb[1] > 0 and hb[11] > 0:
            self.add(5, 0, ben_in(2, 12))
        if hm[1] > 0 and hm[11] > 0:
            self.add(5, 1, [p for p in MALEFICS if self.d0(p) + 1 in (2, 12)])
        if s[5] == s[3] or (s[5] + 6) % 12 == s[3]:                      # Guru-Mangala
            self.add(5, 2, [5, 3])
        t2 = (s[2] + 9) % 12                                              # Amala (10th house / 10th sign from Moon)
        if hm[9] == 0 and m[t2] == 0 and (hb[9] > 0 or b[t2] > 0):
            self.add(5, 3, [p for p in BENEFICS if self.d0(p) == 9 or s[p] == t2])
        if (sum(1 for d in (0, 3, 6, 9) if hb[d] > 0) > 1 and hm[6] == 0
                and hm[7] == 0):                                         # Parvata
            self.add(5, 4, [p for p in BENEFICS if self.d0(p) % 3 == 0])
        L4, L10 = self.lord(4), self.lord(10)                            # Kaahala
        if L4 != 5 and (s[5] - s[L4]) % 12 % 3 == 0 and self.well(LL):
            self.add(5, 5, [L4, 5])
        elif s[L4] == s[L10] and (owns(L4, s[L4]) or EXALT[L4] == s[L4]):
            self.add(5, 6, [L4, L10])
        if EXALT[LL] == s[LL] and self.d0(LL) % 3 == 0 and self.ra(LL, 5):   # Chaamara
            self.add(5, 7, [LL, 5])
        elif hb[9] + hb[8] + hb[6] > 1:
            self.add(5, 8, [p for p in BENEFICS if self.d0(p) in (6, 8, 9)])
        L5, L6, L9 = self.lord(5), self.lord(6), self.lord(9)            # Sankha
        if L5 != L6 and (s[L5] - s[L6]) % 3 == 0 and self.well(LL):
            self.add(5, 9, [L5, L6])
        elif s[LL] == s[L10] and s[LL] % 3 == 0 and LL != L10 and self.well(L9):
            self.add(5, 10, [LL, L10, L9])
        a = self.hocc[3]                                                  # Bheri
        if all(a[d] >= 1 for d in (0, 1, 6, 11)) and self.well(L9):
            self.add(5, 11, [p for p in range(1, 10) if self.d0(p) + 1 in (1, 2, 7, 12)])
        elif (s[LL] - s[5]) % 3 == 0 and (s[6] - s[5]) % 3 == 0 and self.well(L9):
            self.add(5, 12, [LL, 5, 6, L9])
        strong = [p for p in range(1, 10) if self.kk(p) and (owns(p, s[p]) or EXALT[p] == s[p])]
        if len(strong) > 1 and self.well(LL):                            # Mridanga
            self.add(5, 13, strong)
        L7, L11, L2 = self.lord(7), self.lord(11), self.lord(2)          # Sreenatha
        if self.d0(L7) == 9 and EXALT[L7] == s[L7] and s[L9] == s[L10]:
            self.add(5, 14, [L7, L9, L10])
        if (hb[0] > 0 and hb[8] > 0 and self.hocc[3][4] > 0 and hm[3] > 0
                and hm[7] > 0):                                          # Matsya
            self.add(5, 15)
        good = [p for p in BENEFICS if self.friendly(p) and self.d0(p) in (4, 5, 6)]   # Koorma
        bad = [p for p in MALEFICS if self.friendly(p) and self.d0(p) in (0, 2, 10)]
        if len(good) > 1 and len(bad) > 1:
            self.add(5, 16, good + bad)
        if self.d0(L2) == 8 and self.d0(L9) == 1 and self.kk(LL):         # Khadga
            self.add(5, 17, [L2, L9, LL])
        if (self.d0(7) == 9 and self.d0(2) % 4 == 0 and L % 3 == 1 and self.d0(6) % 3 == 0
                and b[s[2]] > 1):                                         # Kusuma
            self.add(5, 18, [2, 6, 7] + [p for p in BENEFICS if s[p] == s[2] and p != 2])
        if self.d0(5) == 1 and (s[5] == s[4] or self.ra(5, 4)) and (s[5] == s[6] or self.ra(5, 6)):
            self.add(5, 19, [5, 4, 6])                                    # Kalanidhi
        disp = LORDS[s[LL]]                                               # Kalpadruma / Parijata
        rasi_disp, amsa_disp = LORDS[self.d1[disp]], LORDS[self.d9[disp]]
        if all(self.strong(p) or self.kk(p) for p in (LL, disp, rasi_disp, amsa_disp)):
            self.add(5, 20, [LL, disp, rasi_disp, amsa_disp])
        if hb[6] > 0 and hb[7] > 0 and hm[6] == 0 and hm[7] == 0:
            self.add(5, 21, ben_in(7, 8))                                 # Lagnaadhi

    def other_2(self):
        s, b, m, L = self.s, self.occ[1], self.occ[4], self.s[0]
        LL = self.lord(1)
        L2, L4, L5, L6, L7 = self.lord(2), self.lord(4), self.lord(5), self.lord(6), self.lord(7)
        L9, L10, L11, L12 = self.lord(9), self.lord(10), self.lord(11), self.lord(12)
        if s[5] == 8 and s[L2] == 8 and EXALT[LL] == s[LL]:              # Go
            self.add(5, 23, [5, L2, LL])
        if EXALT[L11] == s[L11] and s[L11] == s[6] and (s[L11] - s[LL]) % 3 == 0:   # Vidyut
            self.add(5, 24, [L11] if L11 == 6 else [L11, 6])
        if self.d0(L4) == 9 and self.d0(L10) == 3 and EXALT[LL] == s[LL]:   # Chaapa
            self.add(5, 25, [L4, L10, LL])
        disp = LORDS[s[LL]]                                               # Pushkala
        if (s[LL] == s[2] and (self.d0(disp) % 3 == 0 or self.comp[disp - 1][LORDS[s[disp]] - 1] in (0, 1))
                and self.ra(0, disp) and self.hocc[3][0] > 0):
            self.add(5, 26, [LL, disp, 2])
        if s[5] == (s[L9] + 8) % 12 and b[(s[5] + 8) % 12] > 0 and self.d0(7) == 9:   # Makuta
            self.add(5, 27, [5, 7])
        if EXALT[L10] == s[L10] and DEBIL[L6] == s[L6]:                  # Jaya
            self.add(5, 28, [L10, L6])
        for idx, house in ((29, 6), (30, 8), (31, 12)):                   # Harsha, Sarala, Vimala
            lord = self.lord(house)
            if self.d0(lord) == house - 1:
                self.add(5, idx, [lord])
        if self.ra(6, 7) and self.ra(7, 9) and self.ra(9, 6):             # Tapaswi
            self.add(5, 32, [6, 7, 9])
        elif (s[7] - s[6]) % 4 == 0 and (s[9] - s[6]) % 4 == 0:
            self.add(5, 33, [6, 7, 9])
        al = self.s[59]                                                   # Sadhu: 3rd / 6th from AL
        x3, x6 = (al + 2) % 12, (al + 5) % 12
        if b[x3] + b[x6] > 0 and m[x3] + m[x6] == 0:
            self.add(5, 34, self.in_signs(BENEFICS, (x3, x6)))
        for idx, lord, houses in ((35, L2, (2, 12, 8)), (36, L7, (4, 9, 8)), (37, LL, (4, 10, 11))):
            signs = self.from_sign(s[lord], *houses)                       # Hari, Hara, Brahma
            nb, nm = sum(b[x] for x in signs), sum(m[x] for x in signs)
            if nb == len(BENEFICS) or (nb > 2 and nm < nb):
                self.add(5, idx, self.in_signs(BENEFICS, signs))
        if ((s[5] - s[L9]) % 3 == 0 and (s[6] - s[L11]) % 3 == 0
                and ((s[4] - s[LL]) % 3 == 0 or (s[4] - s[L10]) % 3 == 0)):   # Brahma (2)
            self.add(5, 38, [5, 6, 4])
        amsa9 = LORDS[self.d9[L9]]                                         # Vishnu: conjoined (sign) in the 2nd
        if all(self.d0(p) == 1 for p in (L9, L10, amsa9)) and s[L9] == s[L10] == s[amsa9]:
            self.add(5, 39, [L9, L10, amsa9])
        if self.d0(L5) == 8 and self.d0(L9) == 9 and self.d0(L10) == 4:   # Siva
            self.add(5, 40, [L5, L9, L10])
        if (s[1] - s[2]) % 4 == 0 and (s[3] - s[2]) % 4 == 0:             # Trilochana
            self.add(5, 41, [1, 2, 3])
        amsa10 = LORDS[self.d9[L10]]                                       # Gouri
        if EXALT[amsa10] == s[amsa10] and self.d0(amsa10) == 9 and s[LL] == s[amsa10]:
            self.add(5, 42, [amsa10, LL])
        a6, a9 = LORDS[self.d9[L6]], LORDS[self.d9[L9]]                    # Chandika
        if L % 3 == 1 and self.ra(0, L6) and s[a6] == s[1] and s[a9] == s[1]:
            self.add(5, 43, [L6, a6, a9, 1])
        if self.d0(L9) % 3 == 0 and self.strong(L9) and self.well(LL):   # Lakshmi
            self.add(5, 44, [L9])
        if (self.d0(L10) == 4 and self.d0(4) % 3 == 0 and s[1] == 4
                and ((s[4] - s[2]) % 4 == 0 or (s[5] - s[2]) % 4 == 0) and self.d0(3) == 10):
            self.add(5, 45, [L10, 5, 4, 1])                               # Saarada
        for idx, house in ((46, 2), (47, 5), (48, 11)):                   # Bhaarathi
            amsa = LORDS[self.d9[self.lord(house)]]
            if s[amsa] == s[L9] and EXALT[amsa] == s[amsa]:
                # (5, 46) leaves the record's giver count as it was (a quirk kept for its results); two givers here
                self.add(5, idx, [amsa, L9])
                break
        if (all(d == 1 or d % 3 == 0 or d % 4 == 0 for d in (self.d0(4), self.d0(5), self.d0(6)))
                and (self.strong(5) or NATURAL_RELATIONS_9[4][LORDS[s[5]] - 1] == 2
                     or self.comp[4][LORDS[s[5]] - 1] in (1, 2))):        # Saraswati
            self.add(5, 49, [4, 5, 6])
        if s[7] == EXALT[7] and self.d0(7) % 3 == 0 and self.d0(5) % 3 == 0 and self.d0(6) % 3 == 0:
            self.add(5, 50, [5, 6, 7])                                    # Amsavatara
        if (self.d0(L2) == 9 and self.d0(L10) == 1 and self.d0(LL) == 10
                and self.d0(L11) == 0 and L % 3 == 1):                    # Devendra
            self.add(5, 51, [L2, L10, LL, L11])
        if self.d0(L5) == 10 and self.d0(L11) == 4 and s[2] == s[L11]:    # Indra: Moon with the 11th lord
            self.add(5, 52, [L5, L11, 2])
        if self.d0(1) == 9 and self.d0(L10) == 2 and s[L10] == s[7]:      # Ravi
            self.add(5, 53, [1, L10, 7])
        if ((s[1] - s[2]) % 12 == 1 and (s[4] - s[2]) % 12 == 2
                and (s[5] - s[2]) % 12 in (4, 8)):                       # Bhaaskara
            self.add(5, 54, [2, 1, 4, 5])

    def other_3(self):
        s, L = self.s, self.s[0]
        upa = lambda p: self.d0(p) in (2, 5, 9, 10)                       # Vasumati: upachayas from lagna
        nb, nm = sum(1 for p in BENEFICS if upa(p)), sum(1 for p in MALEFICS if upa(p))
        if nb == len(BENEFICS) or (nb > 2 and nm < nb):
            self.add(5, 55, [p for p in BENEFICS if upa(p)])
        LL, L10 = self.lord(1), self.lord(10)                              # Gandharva
        if ((self.d0(L10) - 6) % 4 == 0 and s[1] == EXALT[1] and self.d0(2) == 8
                and self.ra(LL, 5)):
            self.add(5, 56, [L10, 1, 2, LL])

    # --- group 6, raja yogas (BPHS 34.11-14, 39)
    def raja(self):
        s, L = self.s, self.s[0]
        pairs = []
        for kona in (8, 4, 0):                                            # the trikonas
            kl = self.lord(kona + 1)
            for kendra in (9, 0, 3, 6):
                dl = self.lord(kendra + 1)
                if dl == kl:
                    if kendra != 0 and kona != 0:
                        self.add(6, 0, [dl])
                    continue
                if not (s[dl] == s[kl] or (graha_drishti(dl, s[dl], s[kl]) and graha_drishti(kl, s[kl], s[dl]))
                        or (LORDS[s[dl]] == kl and LORDS[s[kl]] == dl)):
                    continue
                if kendra == 0 and kona == 8:
                    idx = 1
                elif kendra == 9 and kona == 8:
                    idx = 2
                else:
                    idx = 3
                    if any({a, c} == {dl, kl} for a, c in pairs):
                        continue
                if len(self.out) < MAX_YOGAS:
                    pairs.append((dl, kl))
                self.add(6, idx, [dl, kl])
        ak, pik, pk = self.k[0], self.k[4], self.k[5]                       # BPHS 39.3-5
        h_ak, h_pk, h_pik = self.d0(ak), self.d0(pk), self.d0(pik)
        if (h_ak in (0, 4) and h_pk in (0, 4)) or s[ak] == s[pk]:        # together = same sign
            self.add(6, 4, [ak, pk])
        if (h_ak in (0, 4) and h_pik in (0, 4)) or s[ak] == s[pik]:
            self.add(6, 5, [ak, pik])
        hl, gl = s[14], s[15]                                               # hora and ghati lagnas
        assoc = lambda p, x: s[p] == x or LORDS[x] == p or CO_LORDS[x] == p or rasi_drishti(s[p], x)
        for p in range(1, 10):
            a_l, a_h, a_g = assoc(p, L), assoc(p, hl), assoc(p, gl)
            if a_l and a_h and a_g:
                self.add(6, 6, [p])
            elif a_l and a_g:
                self.add(6, 7, [p])
            elif a_l and a_h:
                self.add(6, 8, [p])
        self.raja_2(ak)

    def raja_2(self, ak: int):
        s, b, m, L = self.s, self.occ[1], self.occ[4], self.s[0]
        L9 = self.lord(9)
        if self.d0(L9) in (0, 4, 6) and self.d0(ak) in (0, 4, 6):
            self.add(6, 9, [ak, L9])
        LL = self.lord(1)
        two_five = lambda x: b[(x + 4) % 12] + 2 * b[(x + 1) % 12] > 2
        if two_five(s[ak]) and two_five(s[LL]):
            self.add(6, 10)
        hb, hm = self.hocc[1], self.hocc[4]
        if (sum(hb[d] for d in (0, 3, 6, 9)) == len(BENEFICS)
                and sum(hm[d] for d in (2, 5, 10)) == len(MALEFICS)):
            self.add(6, 11)
        L6, L8, L12 = self.lord(6), self.lord(8), self.lord(12)
        debil = [p for p in (L6, L8, L12) if DEBIL[p] == s[p]]
        if self.strong(LL) and self.ra(0, LL) and debil:
            self.add(6, 12, [LL] + debil)
        L5 = self.lord(5)
        if (s[L5] == s[L9] or s[L5] == s[LL]) and self.d0(L5) in (0, 3, 9):
            self.add(6, 13)
        if s[L5] == s[L9] or s[L5] == (s[L9] + 6) % 12:
            self.add(6, 14 if self.ra(0, LL) else 15, [L5, L9])
        high = [p for p in range(1, 10) if s[p] in (MOOLA[p], EXALT[p])]
        if len(high) > 3:
            self.add(6, 16, high)
        if self.d0(L6) in (7, 11):
            self.add(6, 17, [L6])
        if self.d0(L8) in (5, 11):
            self.add(6, 18, [L8])
        if self.d0(L12) in (5, 7):
            self.add(6, 19, [L12])
        tie = lambda p, q: s[p] == s[q] or s[p] == (s[q] + 6) % 12
        if tie(L6, L8) and tie(L6, L12):
            self.add(6, 20, [L6, L8, L12])
        elif tie(L6, L8):
            self.add(6, 21, [L6, L8])
        elif tie(L6, L12):
            self.add(6, 22, [L6, L12])
        elif tie(L8, L12):
            self.add(6, 23, [L8, L12])
        # same planet aspecting lagna in D-1, D-9, D-2, D-3, D-12, D-30 (varga indices 0 1 2 3 11 16)
        same = [p for p in range(1, 10) if all(rasi_drishti(v[0], v[p]) for v in self.aspect_vargas)]
        if same:
            self.add(6, 24, same)

    # --- group 7, raja sambandha (BPHS 40)
    def sambandha(self):
        s, L = self.s, self.s[0]
        amk, ak = self.k[1], self.k[0]
        L10, LL = self.lord(10), self.lord(1)
        if s[amk] == s[L10] or rasi_drishti(s[amk], s[L10]):
            self.add(7, 0, [amk, L10])
        elif s[LL] == s[L10] or rasi_drishti(s[LL], s[L10]):            # text: AmK's dispositor; code: lagna lord
            self.add(7, 1, [LL, L10])
        h_ak = self.d0(ak)
        if s[amk] == s[ak]:
            self.add(7, 2, [ak, amk])
        if s[amk] == EXALT[amk] or owns(amk, s[amk]):
            self.add(7, 3, [amk])
        if self.d0(amk) % 4 == 0:
            self.add(7, 4, [amk])
        if (s[amk] - s[ak]) % 12 % 4 == 0 or (s[amk] - s[ak]) % 3 == 0:
            self.add(7, 5, [ak, amk])
        al = s[59]
        if (self.hocc[4][2] > 0 and self.hocc[4][5] > 0                  # 3rd / 6th house, then signs from AL, AK
                and all(self.occ[4][(x + d) % 12] > 0 for x in (al, s[ak]) for d in (2, 5))):
            self.add(7, 6)
        L9 = self.lord(9)
        if ((s[ak] == EXALT[ak] or owns(ak, s[ak])) and (h_ak % 4 == 0 or h_ak % 3 == 0)
                and rasi_drishti(s[L9], s[ak])):
            self.add(7, 7, [ak, L9])
        n = self.occ[1][s[ak]]
        with_benefic = (n > 1 and ak in BENEFICS) or (n > 0 and ak in MALEFICS)
        if owns(ak, s[2]) and h_ak == 0:
            if with_benefic:
                self.add(7, 8, [ak])
        else:
            if h_ak in (4, 6, 8, 9) and with_benefic:
                self.add(7, 9, [ak])
            if h_ak == 8 and s[67] == L:
                self.add(7, 10, [ak])
        if self.d0(LL) == 9 and self.d0(L10) == 0:
            self.add(7, 11, [LL, L10])
        x5 = (s[ak] + 4) % 12
        if s[2] == x5 and s[6] == x5:
            self.add(7, 12, [2, 6])
        L5 = self.lord(5)
        if s[ak] == s[L5] and (h_ak % 4 == 0 or h_ak % 3 == 0):
            self.add(7, 13, [ak, L5])
        h_ll = self.d0(LL)
        if s[LL] == s[L5] and (h_ll % 4 == 0 or h_ll % 3 == 0):
            self.add(7, 14, [LL, L5])

    # --- group 8, dhana (BPHS 41)
    def dhana(self):
        L = self.s[0]
        a, *rest = DHANA_5_11[L]
        if self.d0(a) + 1 == 5 and all(p == 0 or self.d0(p) + 1 == 11 for p in rest):
            self.add(8, L, [a] + [p for p in rest if p])
        a, *rest = DHANA_LAGNA[L]
        if self.d0(a) == 0 and all(p == 0 or self.ra(a, p) for p in rest):
            self.add(8, L + 12, [a] + [p for p in rest if p])

    # --- group 9, daridra (BPHS 42)
    def daridra(self):
        s, L = self.s, self.s[0]
        LL, L2, L5, L6, L9, L10, L12 = (self.lord(h) for h in (1, 2, 5, 6, 9, 10, 12))
        hit = lambda *ps: any(self.maraka_on(s[p]) for p in ps)
        d = self.d0
        if d(LL) == 11 and d(L12) == 0 and hit(LL, L12):
            self.add(9, 0, [LL, L12])
        if d(LL) == 5 and d(L6) == 0 and hit(LL, L6):
            self.add(9, 1, [LL, L6])
        if d(LL) == 7 and hit(LL) and (d(9) == 0 or s[2] == s[9]):
            self.add(9, 2, [LL, 9])
        n = self.occ[4][s[LL]]                                            # malefics with the lagna lord (sign)
        if (d(LL) in (5, 7, 11)
                and ((n > 0 and LL in BENEFICS) or (n > 1 and LL in MALEFICS))
                and (s[L2] == DEBIL[L2] or NATURAL_RELATIONS_9[L2 - 1][LORDS[s[L2]] - 1] == 4)):
            self.add(9, 3, [LL, L2])
        if d(L5) == 5 and d(L9) == 11 and hit(L5, L9):
            self.add(9, 4, [L5, L9])
        if self.hocc[4][0] > 1 and d(L9) != 0 and d(L10) != 0 and self.maraka_on(L):
            self.add(9, 5, [p for p in MALEFICS if d(p) == 0])

    # --- group 10, parivraja / pravrajya (BPHS 79.2-3)
    def parivraja(self):
        s, L = self.s, self.s[0]
        al, moon = s[59], s[2]
        if moon == s[7]:
            if moon == al:
                self.add(10, 0, [7, 2])
            elif rasi_drishti(moon, al):
                self.add(10, 1, [7, 2])
        L10 = self.lord(10)
        if self.occ[3][s[L10]] > 4 and self.kk(L10):
            self.add(10, 2, [L10])
        if self.lagna_degree > 27 and self.occ[1][L] > 0 and self.kk(5):
            self.add(10, 3, [5] + [p for p in BENEFICS if s[p] == L])
        if self.moon_d3 in (9, 10) and self.ra(2, 3) and self.ra(2, 7):
            self.add(10, 4, [2, 7, 3])
        if self.d9[2] in (0, 7) and self.ra(2, 7):
            self.add(10, 5, [2, 7])
        disp = LORDS[moon]
        if all(p == disp or not self.ra(disp, p) for p in range(1, 7)) and (disp == 7 or self.ra(disp, 7)):
            self.add(10, 6, [disp], ASCETIC[disp])

    def find_all(self, group: int = 0) -> List[Dict[str, Any]]:
        """All yogas of the chart: ``group`` 0 = all, else 1 .. 10 (GROUPS)."""
        if not 0 <= group <= 10:
            group = 0
        runs = ((1, (self.mahapurusha,)), (2, (self.solar,)), (3, (self.lunar,)), (4, (self.nabhasa,)),
                (5, (self.other, self.other_2, self.kulavardhana, self.other_3)), (6, (self.raja,)),
                (7, (self.sambandha,)), (8, (self.dhana,)), (9, (self.daridra,)), (10, (self.parivraja,)))
        for g, checks in runs:
            if group in (0, g):
                for check in checks:
                    check()
        return self.out

    def kulavardhana(self):                                               # run after Bhaaskara
        s = self.s
        if all(self.d0(p) == 4 or (s[p] + 8) % 12 in (s[2], s[1]) for p in range(1, 8)):
            self.add(5, 22)


def _lagna_degree(lon: float) -> int:
    """Whole degrees of the lagna in its sign as ``utils.split_sign_dms`` gives them:
    seconds within 1e-4 of 60 carry into the minutes, 60 minutes into the degrees."""
    d = lon % 30.0
    deg, mins = int(d), int((d - int(d)) * 60.0)
    sec = (d - deg - mins / 60.0) * 3600.0
    if 60.0 - sec < 1e-4 and mins + 1 == 60:
        deg += 1
    return deg


def chart_yogas(chart: Dict[str, Any], group: int = 0, varga: int = 0,
                bhavas: Optional[Sequence[Tuple[float, float, float]]] = None,
                cusp_in_middle: bool = True) -> List[Dict[str, Any]]:
    """Yogas of an ``ephemeris.build_chart`` result as the yogas view lists them: ``group`` 0 = all or
    1 .. 10 (GROUPS), ``varga`` the varga index (dasa_systems.VARGAS; 0 = D-1, the default).
    ``bhavas`` ((start, middle, end) of the 12 houses, D-1 only): house placements by longitude and house lords
    from the sign of each cusp (its middle, or its start when the ascendant starts the 1st house); without them a
    house is a sign.
    Each yoga: group, index, type, name, varga, givers (point indices), givers_text, result, definition, basis."""
    jc = JD.JChart(chart)
    bhava = bool(bhavas) and varga == 0
    sg = jc.signs[varga]
    rasi = jc.lons
    fn = JD.VARGAS[varga][1]
    sl = chart["special_lagnas"]
    arudhas = SS.bhava_arudhas(sg, rasi)
    s = dict(enumerate(sg))
    s.update({14: fn(sl["Hora_Lagna"]), 15: fn(sl["Ghati_Lagna"]), 59: arudhas[0], 67: arudhas[8]})
    deg = [x % 30.0 for x in rasi[:9]]
    deg[8] = 30.0 - deg[8]                                                # Rahu counted from the end of its sign
    names = JD.JChart.POINTS
    kar = N.compute_chara_karakas(dict(zip(names[1:9], deg[1:9])), use_8_karakas=True)
    karakas = [names.index(kar[k]) for k in ("AK", "AmK", "BK", "MK", "PiK", "PK", "GK", "DK")]
    houses = cusps = None
    if bhava:
        houses = [H.house_of(lon, bhavas) for lon in rasi[:10]]
        cusps = [int((b[1] if cusp_in_middle else b[0]) % 360.0 // 30) for b in bhavas]
    y = _Yogas(s, {i: jc.signs[i] for i in (0, 1, 2, 3, 11, 16)}, karakas, _lagna_degree(chart["lagna_lon"]),
               compound_relationships(sg[1:10]), houses, cusps)
    out = []
    for r in y.find_all(group):
        name, definition, result = CATALOGUE[r["group"] - 1][r["index"]]
        g = r["givers"]
        out.append({"group": r["group"], "index": r["index"], "type": GROUPS[r["group"]], "name": name,
                    "varga": "D-%d" % JD.VARGA_NUMBER[varga], "givers": g,
                    "givers_text": NAABHASA_GIVERS if r["group"] == 4 else ", ".join(GIVER_CODES[p] for p in g),
                    "result": result + r["extra"], "definition": definition,
                    "basis": BASIS_NAMES[BASIS[r["group"] - 1][r["index"]] if bhava else "r"],
                    "places": [[GIVER_CODES[p], y.h[p] + 1, s[p]] for p in g if p < 10]})   # giver, house, sign
    return out
