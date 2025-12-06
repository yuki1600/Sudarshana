# src/ci_core.py
from datetime import datetime, timedelta, date, timezone
import colorsys
from dateutil import tz
from timezonefinder import TimezoneFinder
import pandas as pd
import swisseph as swe
from src.dasa_systems import (
    build_ashtottari, build_shodshottari, build_dwadashottari,
    build_panchottari, build_shatabdik, build_chaturashiti_sama,
    build_dwisaptati_sama, build_shastihayani, build_shattrimshat_sama,
    build_chakra,
    # New Dasa Systems
    build_sthir_dasa, build_yogardha_dasa, build_kendradi_dasa,
    build_karak_dasa, build_manduk_dasa, build_shula_dasa,
    build_trikon_dasa, build_dirga_dasa, build_panch_swar_dasa,
    build_kalachakra_dasa
)

# Vedic Lunar Month Map (Sun Sign Index 0=Aries -> Vaisakha)
# Key: Sun Sign Index at New Moon (Sidereal)
# Value: (Sanskrit, Tamil)
MAASA_MAP = {
    11: ("Chaitra", "Chithirai"),
    0: ("Vaisakha", "Vaikasi"),
    1: ("Jyeshtha", "Aani"),
    2: ("Ashadha", "Aadi"),
    3: ("Shravana", "Avani"),
    4: ("Bhadrapada", "Purattasi"),
    5: ("Ashvina", "Aippasi"),
    6: ("Kartika", "Karthigai"),
    7: ("Margashirsha", "Margazhi"),
    8: ("Pausha", "Thai"),
    9: ("Magha", "Maasi"),
    10: ("Phalguna", "Panguni")
}

class HistoricalDate:
    """
    Represents a date that might be outside Python's datetime range (1-9999).
    Mimics datetime interface for basic attributes and isoformat.
    """
    def __init__(self, year, month, day, hour=0, minute=0, second=0, microsecond=0, tzinfo=None):
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second
        self.microsecond = microsecond
        self.tzinfo = tzinfo
        
    def isoformat(self):
        # ISO 8601 expanded format: ±YYYYY-MM-DDTHH:MM:SS...
        if self.year < 0:
            y_str = f"{self.year:+07d}" # e.g. -000500
        elif self.year > 9999:
            y_str = f"+{self.year:06d}"
        else:
            y_str = f"{self.year:04d}"
            
        t_str = f"{self.hour:02d}:{self.minute:02d}:{self.second:02d}"
        if self.microsecond:
            t_str += f".{self.microsecond:06d}"
            
        tz_str = ""
        if self.tzinfo == timezone.utc:
            tz_str = "+00:00"
        # Note: Complex timezone offsets for historical dates are not fully supported here
        # without a reference datetime, so we default to UTC or empty if unknown.
        
        return f"{y_str}-{self.month:02d}-{self.day:02d}T{t_str}{tz_str}"
    
    def strftime(self, fmt):
        """
        Basic strftime implementation for HistoricalDate.
        Only supports common format codes. For full formatting, use isoformat().
        """
        # For simplicity, we'll construct the time string manually
        # This is a minimal implementation - extend as needed
        if fmt == '%Y-%m-%dT%H:%M:%S':
            y_str = f"{self.year:04d}" if 0 <= self.year <= 9999 else f"{self.year:+07d}"
            return f"{y_str}-{self.month:02d}-{self.day:02d}T{self.hour:02d}:{self.minute:02d}:{self.second:02d}"
        else:
            # Fallback: just return isoformat for unsupported formats
            return self.isoformat()
        
    def __str__(self):
        return self.isoformat()
        
    def utcoffset(self):
        # Return None for HistoricalDate - offsets are unreliable for ancient dates
        return None
    
    def date(self):
        """Return a date-like object (self) for compatibility"""
        return self
    
    def weekday(self):
        """Calculate day of week (0=Monday, 6=Sunday) using Zeller's congruence"""
        # Zeller's congruence works for Gregorian calendar
        y, m, d = self.year, self.month, self.day
        if m < 3:
            m += 12
            y -= 1
        q = d
        m_adjusted = m
        K = y % 100
        J = y // 100
        h = (q + ((13 * (m_adjusted + 1)) // 5) + K + (K // 4) + (J // 4) - (2 * J)) % 7
        # Convert Zeller (0=Saturday) to ISO (0=Monday)
        return (h + 5) % 7
    
    def __sub__(self, other):
        """Subtract timedelta from HistoricalDate or calculate difference between dates"""
        from datetime import timedelta
        if isinstance(other, timedelta):
            # Approximate: convert to JD, subtract days, convert back
            # This is a simplification but works for basic date arithmetic
            total_days = other.total_seconds() / 86400
            new_day = self.day - int(total_days)
            new_month = self.month
            new_year = self.year
            
            # Handle negative days (simple implementation)
            while new_day < 1:
                new_month -= 1
                if new_month < 1:
                    new_month = 12
                    new_year -= 1
                # Approximate days in month
                new_day += 30  # Simplified
            
            return HistoricalDate(new_year, new_month, new_day, self.hour, self.minute, self.second, self.microsecond, self.tzinfo)
        elif isinstance(other, (HistoricalDate, datetime, date)):
            # Calculate difference between two dates - return timedelta
            # Approximate calculation based on year/month/day/time differences
            days_diff = (self.year - other.year) * 365 + (self.month - other.month) * 30 + (self.day - other.day)
            seconds_diff = days_diff * 86400 + \
                          (self.hour - getattr(other, 'hour', 0)) * 3600 + \
                          (self.minute - getattr(other, 'minute', 0)) * 60 + \
                          (self.second - getattr(other, 'second', 0))
            return timedelta(seconds=seconds_diff)
        else:
            raise TypeError(f"unsupported operand type(s) for -: 'HistoricalDate' and '{type(other).__name__}'")
    
    def __add__(self, other):
        """Add timedelta to HistoricalDate"""
        from datetime import timedelta
        if isinstance(other, timedelta):
            total_days = other.total_seconds() / 86400
            new_day = self.day + int(total_days)
            new_month = self.month
            new_year = self.year
            
            # Handle days overflow (simple implementation)
            while new_day > 30:  # Simplified
                new_day -= 30
                new_month += 1
                if new_month > 12:
                    new_month = 1
                    new_year += 1
            
            return HistoricalDate(new_year, new_month, new_day, self.hour, self.minute, self.second, self.microsecond, self.tzinfo)
        else:
            raise TypeError(f"unsupported operand type(s) for +: 'HistoricalDate' and '{type(other).__name__}'")
    
    def __lt__(self, other):
        """Less than comparison"""
        if isinstance(other, (HistoricalDate, datetime, date)):
            return (self.year, self.month, self.day, self.hour, self.minute, self.second) < \
                   (other.year, other.month, other.day, getattr(other, 'hour', 0), getattr(other, 'minute', 0), getattr(other, 'second', 0))
        return NotImplemented
    
    def __le__(self, other):
        """Less than or equal comparison"""
        return self < other or self == other
    
    def __eq__(self, other):
        """Equality comparison"""
        if isinstance(other, (HistoricalDate, datetime, date)):
            return (self.year, self.month, self.day, self.hour, self.minute, self.second) == \
                   (other.year, other.month, other.day, getattr(other, 'hour', 0), getattr(other, 'minute', 0), getattr(other, 'second', 0))
        return False

# ---------------------------------
# Sunrise/Sunset configuration
# ---------------------------------
# "vedic"        -> Sun's CENTER on the horizon, no refraction (Hindu/Vedic method)
# "astronomical" -> Apparent (upper limb) with standard refraction (almanac style)
# "geometric"    -> Center, no refraction (topocentric), non-Hindu
SUNRISE_DEFINITION = "vedic"   # default per your earlier preference
SITE_ELEVATION_M   = 0.0       # meters above sea level (set if you know site altitude)
PRESSURE_MBAR      = 1013.25   # used for "astronomical"
TEMP_C             = 15.0      # used for "astronomical"

# If your pyswisseph build exposes BIT_HINDU_RISING, use it; otherwise fall back.
HINDU_BIT = getattr(swe, "BIT_HINDU_RISING", None)

# ---------------------------------
# Constants / lookups
# ---------------------------------
RASHI_EN  = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
RASHI_SA  = ["Mesha","Vrishabha","Mithuna","Karka","Simha","Kanya","Tula","Vrischika","Dhanu","Makara","Kumbha","Meena"]
RASHI_ABR = ["Ar","Ta","Ge","Cn","Le","Vi","Li","Sc","Sg","Cp","Aq","Pi"]
NAK_NAMES = ["Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra","Punarvasu","Pushya","Ashlesha","Magha","Purva Phalguni","Uttara Phalguni","Hasta","Chitra","Swati","Vishakha","Anuradha","Jyeshtha","Mula","Purva Ashadha","Uttara Ashadha","Shravana","Dhanishtha","Shatabhisha","Purva Bhadrapada","Uttara Bhadrapada","Revati"]
YOGA_NAMES = ["Vishkambha","Priti","Ayushman","Saubhagya","Shobhana","Atiganda","Sukarma","Dhriti","Shoola","Ganda","Vriddhi","Dhruva","Vyaghata","Harshana","Vajra","Siddhi","Vyatipat","Variyan","Parigha","Shiva","Siddha","Sadhya","Shubha","Shukla","Brahma","Indra","Vaidhriti"]
KARANA_MOV = ["Bava","Balava","Kaulava","Taitila","Gara","Vanija","Vishti"]
KARANA_FIXED = ["Kinstughna","Shakuni","Chatushpada","Naga"]
VARA_SA_MON_FIRST = ["Somavara","Mangalavara","Budhavara","Guruvara","Shukravara","Shanivara","Ravivara"]  # Mon..Sun
CHALDEAN = ["Saturn","Jupiter","Mars","Sun","Venus","Mercury","Moon"]  # planetary hour cycle

NAISARGIKA = {"Sun":60.0, "Moon":51.4, "Venus":42.9, "Jupiter":34.3, "Mercury":25.7, "Mars":17.1, "Saturn":8.6}
EXALT = {"Sun":("Aries",10.0),"Moon":("Taurus",3.0),"Mars":("Capricorn",28.0),"Mercury":("Virgo",15.0),"Jupiter":("Cancer",5.0),"Venus":("Pisces",27.0),"Saturn":("Libra",20.0)}
DEBIL={"Sun":("Libra",10.0),"Moon":("Scorpio",3.0),"Mars":("Cancer",28.0),"Mercury":("Pisces",15.0),"Jupiter":("Capricorn",5.0),"Venus":("Virgo",27.0),"Saturn":("Aries",20.0)}
MOOLATR={"Sun":("Leo",0.0,20.0),"Moon":("Taurus",0.0,3.0),"Mars":("Aries",0.0,12.0),"Mercury":("Virgo",15.0,20.0),"Jupiter":("Sagittarius",0.0,10.0),"Venus":"Libra 0-15","Saturn":("Aquarius",0.0,20.0)}
if isinstance(MOOLATR["Venus"], str):
    MOOLATR["Venus"] = ("Libra",0.0,15.0)

SIGN_INDEX = {name:i for i,name in enumerate(RASHI_EN)}
SIGN_LORD = {0:"Mars",1:"Venus",2:"Mercury",3:"Moon",4:"Sun",5:"Mercury",6:"Venus",7:"Mars",8:"Jupiter",9:"Saturn",10:"Saturn",11:"Jupiter"}
PERM_FRIENDS={"Sun":{"Moon","Mars","Jupiter"},"Moon":{"Sun","Mercury"},"Mars":{"Sun","Moon","Jupiter"},"Mercury":{"Sun","Venus"},"Jupiter":{"Sun","Moon","Mars"},"Venus":{"Mercury","Saturn"},"Saturn":{"Mercury","Venus"}}
PERM_ENEMIES={"Sun":{"Venus","Saturn"},"Moon":set(),"Mars":{"Mercury"},"Mercury":{"Moon"},"Jupiter":{"Venus","Mercury"},"Venus":{"Sun","Moon"},"Saturn":{"Sun","Moon","Mars"}}
BENEFICS={"Jupiter","Venus","Mercury"}; MALEFICS={"Saturn","Mars","Sun"}
MIN_SHADBALA_RUPA={"Sun":6.5,"Moon":6.0,"Mars":5.0,"Mercury":7.0,"Jupiter":6.5,"Venus":5.5,"Saturn":5.0}
# Practical upper ceiling for normalizing Śaḍbala into a percentage
# Classical texts allow very high theoretical maxima; 20 Rupas keeps the scale readable in UI.
MAX_SHADBALA_RUPA={"Sun":20.0,"Moon":20.0,"Mars":20.0,"Mercury":20.0,"Jupiter":20.0,"Venus":20.0,"Saturn":20.0}
DIG_MAX_ANGLE={"Sun":90.0,"Mars":90.0,"Jupiter":0.0,"Mercury":0.0,"Moon":180.0,"Venus":180.0,"Saturn":270.0}

PLANETS = {"Sun":swe.SUN,"Moon":swe.MOON,"Mars":swe.MARS,"Mercury":swe.MERCURY,"Jupiter":swe.JUPITER,"Venus":swe.VENUS,"Saturn":swe.SATURN,"Uranus":swe.URANUS,"Neptune":swe.NEPTUNE,"Pluto":swe.PLUTO}
GRAHAS_FOR_HOUSE = ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu (true)","Ketu (true)"]

# ---------------------------------
# Varga Names (Classical Divisional Chart Names)
# ---------------------------------
# D-2 Hora: Sun's hora (Solar) or Moon's hora (Lunar)
HORA_NAMES = ["Solar", "Lunar"]  # Sun=0 (Leo), Moon=1 (Cancer)

# D-3 Drekkana: Named after sages - one for each decanate
DREKKANA_NAMES = ["Nārada", "Agastya", "Durvāsa"]  # 1st, 2nd, 3rd decanate

# D-4 Chaturthamsa: Four Kumaras
CHATURTHAMSA_NAMES = ["Sanaka", "Sananda", "Kumara", "Sanatana"]

# D-9 Navamsa: Deva (divine), Manushya (human), Rakshasa (demonic)
# Pattern repeats: Deva for movable signs, Manushya for fixed, Rakshasa for dual
NAVAMSA_NAMES = ["Deva", "Manushya", "Rākṣasa"]

# D-7 Saptamsa: Named after the 7 aspects of children/progeny
SAPTAMSA_NAMES = ["Kṣāra", "Kṣīra", "Dadhi", "Ājya", "Ikṣurasa", "Madya", "Śuddha-Jala"]

# D-10 Dasamsa: Named for career/profession aspects
DASAMSA_NAMES = ["Indra", "Agni", "Yama", "Nirṛti", "Varuṇa", "Vāyu", "Kubera", "Īśāna", "Brahmā", "Ananta"]

# D-12 Dvadasamsa: Named after the 12 Adityas (solar deities)
DVADASAMSA_NAMES = ["Dhātā", "Aryamā", "Mitra", "Varuṇa", "Indra", "Vivasvān", "Pūṣā", "Parjanya", "Aṁśu", "Bhaga", "Tvaṣṭā", "Viṣṇu"]

# D-16 Shodasamsa: Named for vehicles/conveyances (Kala)
SHODASAMSA_NAMES = ["Brahmā", "Viṣṇu", "Rudra", "Śiva", "Parameṣṭhī", "Maheśvara", "Deveśa", "Ardhanārīśa",
                    "Lakṣmī", "Vijayā", "Bhadrā", "Śubhā", "Rambhā", "Urvaśī", "Menakā", "Tilottamā"]

# D-20 Vimsamsa: Named for spiritual/religious aspects
VIMSAMSA_NAMES = ["Kālī", "Gaurī", "Jyeṣṭhā", "Lakṣmī", "Vijayā", "Vimalā", "Saṃkarī", "Balā", "Dhanyā", "Aṅkuśā",
                  "Piṅgalā", "Chūḍāmaṇi", "Māṁsī", "Sarvakāmī", "Vāruṇī", "Padmā", "Bhuvaneśī", "Kṣobhiṇī", "Mahāmāyā", "Ratī"]

# D-24 Siddhamsa/Chaturvimsamsa: Named for learning/education
SIDDHAMSA_NAMES = ["Skanda", "Parśudhara", "Anala", "Viśvakarmā", "Bhaga", "Mitra", "Maya", "Antaka",
                   "Vṛṣadhvaja", "Govinda", "Madana", "Bhīma", "Varuṇa", "Gāyatrī", "Mṛgāṅka", "Pitrī",
                   "Durgā", "Gaṇeśa", "Mukuṭeśvarī", "Prabhākara", "Dikpālaka", "Soumya", "Śānti", "Amṛta"]

# D-27 Saptavimsamsa/Bhamsa: Named after 27 Nakshatras (lunar mansions)
SAPTAVIMSAMSA_NAMES = NAK_NAMES  # Uses the 27 Nakshatra names

# D-30 Trimsamsa: Named after the 5 ruling planets of the degrees
TRIMSAMSA_NAMES_ODD = ["Agni (Mars)", "Vāyu (Saturn)", "Indra (Jupiter)", "Kubera (Mercury)", "Varuṇa (Venus)"]
TRIMSAMSA_NAMES_EVEN = ["Varuṇa (Venus)", "Kubera (Mercury)", "Indra (Jupiter)", "Vāyu (Saturn)", "Agni (Mars)"]

# D-40 Khavedamsa: 40 divisions for maternal lineage
KHAVEDAMSA_NAMES = [f"Kha-{i+1}" for i in range(40)]  # Numbered 1-40

# D-45 Akshavedamsa: 45 divisions for paternal lineage
AKSHAVEDAMSA_NAMES = [f"Akṣa-{i+1}" for i in range(45)]  # Numbered 1-45

# D-60 Shashtiamsa: 60 named divisions - very important for fine predictions
SHASHTIAMSA_NAMES = [
    "Ghora", "Rākṣasa", "Deva", "Kubera", "Yakṣa", "Kiṁnara", "Bhrashṭa", "Kulāghna", "Garala", "Agni",
    "Maya", "Puriṣaka", "Apāṁpati", "Marut", "Kāla", "Sarpa", "Amṛta", "Indu", "Mṛdu", "Komala",
    "Padma", "Viṣa-Dagdha", "Kṣitīśa", "Kamalākara", "Gulika", "Mṛtyu", "Kāla", "Davāgni", "Ghora", "Yama",
    "Kaṇṭaka", "Sudhā", "Amṛta", "Pūrṇa-Candra", "Viṣa-Dagdha", "Kulāghna", "Vāṁśakṣaya", "Utpāta", "Kāla", "Saumya",
    "Komala", "Śītala", "Karāla-Daṁṣṭra", "Caṇḍāla", "Pravīṇa", "Kalyāṇī", "Kṣiteśa", "Kamalākara", "Gulika", "Mṛtyu",
    "Kāla", "Davāgni", "Ghora", "Nirmala", "Saumya", "Kroora", "Atīśītala", "Amṛta", "Payodhī", "Brahma"
]
# Classification of Shashtiamsa as benefic or malefic
SHASHTIAMSA_BENEFIC = {2, 3, 4, 5, 16, 17, 18, 19, 20, 23, 24, 31, 32, 33, 39, 40, 41, 45, 46, 47, 48, 53, 54, 57, 58, 59, 60}  # 1-based indices

# ---------------------------------
# Tiny helpers
# ---------------------------------
_tf = TimezoneFinder()

# Pushkara / Mrityu Bhaga reference data (sign order 0=Aries..11=Pisces)
PUSHKARA_BHAGA_DEG = [21.0, 14.0, 24.0, 14.0, 21.0, 24.0, 24.0, 14.0, 21.0, 14.0, 21.0, 24.0]
MRITYU_BHAGA_DEG = [1.0, 9.0, 21.0, 22.0, 25.0, 2.0, 4.0, 23.0, 18.0, 20.0, 24.0, 10.0]
# Each sign has two Pushkara aṁśa ranges (degrees within the sign)
PUSHKARA_AMSA_RANGES = [
    [(21.0, 24.0), (3.3333, 6.6667)],   # Aries
    [(5.0, 8.0), (15.0, 18.0)],         # Taurus
    [(0.0, 3.3333), (13.3333, 16.6667)],# Gemini
    [(26.6667, 30.0), (16.6667, 20.0)], # Cancer
    [(0.0, 3.3333), (13.3333, 16.6667)],# Leo
    [(13.3333, 16.6667), (23.3333, 26.6667)], # Virgo
    [(16.6667, 20.0), (26.6667, 30.0)], # Libra
    [(6.6667, 10.0), (26.6667, 30.0)],  # Scorpio
    [(0.0, 3.3333), (10.0, 13.3333)],   # Sagittarius
    [(13.3333, 16.6667), (23.3333, 26.6667)], # Capricorn
    [(0.0, 3.3333), (10.0, 13.3333)],   # Aquarius
    [(6.6667, 10.0), (16.6667, 20.0)],  # Pisces
]

def norm360(x): return x % 360.0
def aspect_strength_pct(angle_deg: float, planet: str | None = None) -> float:
    """
    Piecewise-linear aspect strength in percentage based on anchor angles.
    Base anchors (deg→pct): 0/30/150/300/330 → 0%; 60/270 → 25%;
    90/210 → 75%; 120/240 → 50%; 180 → 100%.
    Planet-specific full aspects: Mars (4th/8th), Jupiter (5th/9th), Saturn (3rd/10th).
    """
    ang = norm360(angle_deg)
    base = {
        0.0: 0.0,
        30.0: 0.0,
        60.0: 25.0,
        90.0: 75.0,
        120.0: 50.0,
        150.0: 0.0,
        180.0: 100.0,
        210.0: 75.0,
        240.0: 50.0,
        270.0: 25.0,
        300.0: 0.0,
        330.0: 0.0,
        360.0: 0.0,
    }
    planet_full = {
        "Mars": [90.0, 270.0],
        "Jupiter": [120.0, 240.0],
        "Saturn": [60.0, 300.0],
    }
    anchors = base.copy()
    for p, angles in planet_full.items():
        if planet == p:
            for a in angles:
                anchors[a] = 100.0
    # sort anchors and interpolate linearly between successive knots
    pts = sorted(anchors.items())
    for (a1, v1), (a2, v2) in zip(pts, pts[1:]):
        if a1 <= ang <= a2:
            if a2 == a1:
                return v1
            t = (ang - a1) / (a2 - a1)
            return v1 + t * (v2 - v1)
    return 0.0
def lon_to_sign_idx(lon): return int(norm360(lon) // 30)

def dms_tuple(x):
    x = float(abs(x)); d = int(x); m_float = (x - d) * 60.0
    m = int(m_float); s = round((m_float - m) * 60.0)
    if s == 60: s = 0; m += 1
    if m == 60: m = 0; d += 1
    return d, m, s

def dms_str(x):
    d, m, s = dms_tuple(x); return f"{d:02d}°{m:02d}′{s:02d}″"

def sign_dms_str(lon):
    lon = norm360(lon); si = lon_to_sign_idx(lon); within = lon - 30*si
    return f"{RASHI_ABR[si]} {dms_str(within)}"

def rashi_name(lon): return RASHI_SA[lon_to_sign_idx(lon)]
def ordinal(n): return f"{n}{'th' if 11<=n%100<=13 else {1:'st',2:'nd',3:'rd'}.get(n%10,'th')}"
def fmt_dt(dt): return dt.strftime("%Y-%m-%d %H:%M:%S %Z")

def navamsa_for(lon):
    lon = norm360(lon); si = lon_to_sign_idx(lon); intra = lon - 30*si
    pada = int(intra // (30/9)) + 1
    movable = {0,3,6,9}; fixed = {1,4,7,10}; dual = {2,5,8,11}
    if si in movable: start = si
    elif si in fixed: start = (si + 8) % 12
    else:             start = (si + 4) % 12
    nsign = (start + (pada - 1)) % 12
    return nsign, pada

# ---------------------------------
# Divisional Chart (Varga) Calculations
# ---------------------------------
def drekkana_for(lon):
    """D-3: Drekkana - each sign divided into 3 parts of 10°"""
    lon = norm360(lon)
    si = lon_to_sign_idx(lon)
    intra = lon - 30*si
    drek = int(intra // 10)  # 0, 1, or 2
    if drek == 0:
        return si
    elif drek == 1:
        return (si + 4) % 12
    else:
        return (si + 8) % 12

def chaturthamsa_for(lon):
    """D-4: Chaturthamsa - each sign divided into 4 parts of 7.5°"""
    lon = norm360(lon)
    si = lon_to_sign_idx(lon)
    intra = lon - 30*si
    part = int(intra // 7.5)  # 0-3
    return (si + part * 3) % 12

def saptamsa_for(lon):
    """D-7: Saptamsa - each sign divided into 7 parts"""
    lon = norm360(lon)
    si = lon_to_sign_idx(lon)
    intra = lon - 30*si
    part = int(intra // (30/7))
    odd = (si % 2 == 0)
    if odd:
        return (si + part) % 12
    else:
        return (si + 6 + part) % 12

def dasamsa_for(lon):
    """D-10: Dasamsa - each sign divided into 10 parts of 3°
    Starts from the same sign for odd signs, from the 9th for even signs."""
    lon = norm360(lon)
    si = lon_to_sign_idx(lon)
    intra = lon - 30*si
    part = int(intra // 3)  # 0-9
    odd = (si % 2 == 0)  # Aries(0)=odd, Taurus(1)=even, etc.
    if odd:
        return (si + part) % 12
    else:
        return (si + 8 + part) % 12  # 9th sign = si + 8 (0-indexed)

def dwadasamsa_for(lon):
    """D-12: Dwadasamsa - each sign divided into 12 parts of 2.5°"""
    lon = norm360(lon)
    si = lon_to_sign_idx(lon)
    intra = lon - 30*si
    part = int(intra // 2.5)  # 0-11
    return (si + part) % 12

def shodasamsa_for(lon):
    """D-16: Shodasamsa - each sign divided into 16 parts"""
    lon = norm360(lon)
    si = lon_to_sign_idx(lon)
    intra = lon - 30*si
    part = int(intra // (30/16))
    # Movable signs start from Aries, Fixed from Leo, Dual from Sagittarius
    movable = {0, 3, 6, 9}
    fixed = {1, 4, 7, 10}
    if si in movable:
        return (0 + part) % 12  # Aries
    elif si in fixed:
        return (4 + part) % 12  # Leo
    else:
        return (8 + part) % 12  # Sagittarius

def vimsamsa_for(lon):
    """D-20: Vimsamsa - each sign divided into 20 parts"""
    lon = norm360(lon)
    si = lon_to_sign_idx(lon)
    intra = lon - 30*si
    part = int(intra // 1.5)  # Each part = 1.5°
    # Movable from Aries, Fixed from Sagittarius, Dual from Leo
    movable = {0, 3, 6, 9}
    fixed = {1, 4, 7, 10}
    if si in movable:
        return (0 + part) % 12
    elif si in fixed:
        return (8 + part) % 12
    else:
        return (4 + part) % 12

def chaturvimsamsa_for(lon):
    """D-24: Chaturvimsamsa/Siddhamsa - each sign divided into 24 parts"""
    lon = norm360(lon)
    si = lon_to_sign_idx(lon)
    intra = lon - 30*si
    part = int(intra // 1.25)  # Each part = 1.25°
    odd = (si % 2 == 0)
    if odd:
        return (4 + part) % 12  # Starts from Leo
    else:
        return (3 + part) % 12  # Starts from Cancer

def trimsamsa_for(lon):
    """D-30: Trimsamsa - unequal division based on sign"""
    lon = norm360(lon)
    si = lon_to_sign_idx(lon)
    intra = lon - 30*si
    odd = (si % 2 == 0)
    
    if odd:  # Odd signs (Aries, Gemini, Leo, etc.)
        if intra < 5: return 0      # Aries (Mars)
        elif intra < 10: return 10  # Aquarius (Saturn)
        elif intra < 18: return 8   # Sagittarius (Jupiter)
        elif intra < 25: return 2   # Gemini (Mercury)
        else: return 1              # Taurus (Venus)
    else:  # Even signs
        if intra < 5: return 1      # Taurus (Venus)
        elif intra < 12: return 5   # Virgo (Mercury)
        elif intra < 20: return 11  # Pisces (Jupiter)
        elif intra < 25: return 9   # Capricorn (Saturn)
        else: return 7              # Scorpio (Mars)

def khavedamsa_for(lon):
    """D-40: Khavedamsa - each sign divided into 40 parts"""
    lon = norm360(lon)
    si = lon_to_sign_idx(lon)
    intra = lon - 30*si
    part = int(intra // 0.75)  # Each part = 0.75°
    odd = (si % 2 == 0)
    if odd:
        return (0 + part) % 12  # Starts from Aries
    else:
        return (6 + part) % 12  # Starts from Libra

def akshavedamsa_for(lon):
    """D-45: Akshavedamsa - each sign divided into 45 parts"""
    lon = norm360(lon)
    si = lon_to_sign_idx(lon)
    intra = lon - 30*si
    part = int(intra // (30/45))
    # Movable from Aries, Fixed from Leo, Dual from Sagittarius
    movable = {0, 3, 6, 9}
    fixed = {1, 4, 7, 10}
    if si in movable:
        return (0 + part) % 12
    elif si in fixed:
        return (4 + part) % 12
    else:
        return (8 + part) % 12

def shashtiamsa_for(lon):
    """D-60: Shashtiamsa - each sign divided into 60 parts of 0.5°

    Formula: Multiply degrees in sign by 2, divide by 12.
    The remainder (plus 1 for 1-based) indicates the sign.
    Note: Sign index is ignored - only degrees within sign matter.
    """
    lon = norm360(lon)
    si = lon_to_sign_idx(lon)
    intra = lon - 30*si
    # Multiply degrees by 2 and take modulo 12 to get sign index
    # Each 0.5° advances by 1 shashtiamsa, every 6° (12 shashtiamsas) cycles through all 12 signs
    result = int((intra * 2) % 12)
    return result

def saptavimsamsa_for(lon):
    """D-27: Saptavimsamsa (Bhamsa/Nakshatramsa) - each sign divided into 27 parts

    Each part = 30/27 = 1°6'40" = 1.1111...°
    Distribution starts from movable signs:
    - Fire signs (Ar, Le, Sg): start from Aries
    - Earth signs (Ta, Vi, Cp): start from Cancer
    - Air signs (Ge, Li, Aq): start from Libra
    - Water signs (Cn, Sc, Pi): start from Capricorn
    """
    lon = norm360(lon)
    si = lon_to_sign_idx(lon)
    intra = lon - 30*si
    part = int(intra // (30/27))  # 0-26

    # Determine starting sign based on element
    fire = {0, 4, 8}      # Aries, Leo, Sagittarius
    earth = {1, 5, 9}     # Taurus, Virgo, Capricorn
    air = {2, 6, 10}      # Gemini, Libra, Aquarius
    # water = {3, 7, 11}  # Cancer, Scorpio, Pisces

    if si in fire:
        start = 0   # Aries
    elif si in earth:
        start = 3   # Cancer
    elif si in air:
        start = 6   # Libra
    else:  # water
        start = 9   # Capricorn

    return (start + part) % 12

def get_all_vargas(lon):
    """Return all divisional chart sign indices for a given longitude

    Returns indices for all 16 divisional charts (Shodashvarga):
    D1 (Rasi), D2 (Hora), D3 (Drekkana), D4 (Chaturthamsa), D7 (Saptamsa),
    D9 (Navamsa), D10 (Dasamsa), D12 (Dvadasamsa), D16 (Shodasamsa),
    D20 (Vimsamsa), D24 (Siddhamsa), D27 (Bhamsa), D30 (Trimsamsa),
    D40 (Khavedamsa), D45 (Akshavedamsa), D60 (Shashtiamsa)
    """
    return {
        'D1': lon_to_sign_idx(lon),
        'D2': 4 if (lon_to_sign_idx(lon) % 2 == 0 and (lon % 30) < 15) or (lon_to_sign_idx(lon) % 2 == 1 and (lon % 30) >= 15) else 3,  # Hora
        'D3': drekkana_for(lon),
        'D4': chaturthamsa_for(lon),
        'D7': saptamsa_for(lon),
        'D9': navamsa_for(lon)[0],
        'D10': dasamsa_for(lon),
        'D12': dwadasamsa_for(lon),
        'D16': shodasamsa_for(lon),
        'D20': vimsamsa_for(lon),
        'D24': chaturvimsamsa_for(lon),
        'D27': saptavimsamsa_for(lon),
        'D30': trimsamsa_for(lon),
        'D40': khavedamsa_for(lon),
        'D45': akshavedamsa_for(lon),
        'D60': shashtiamsa_for(lon),
    }

def get_varga_names(lon):
    """Get the classical names for each Varga (divisional chart) position."""
    lon = norm360(lon)
    si = lon_to_sign_idx(lon)
    intra = lon - 30 * si
    odd = (si % 2 == 0)  # Aries(0) is odd in Jyotish

    # D-1 Rasi (sign)
    d1_name = RASHI_SA[si]

    # D-2 Hora
    if odd:
        hora_idx = 0 if intra < 15 else 1  # Sun then Moon for odd
    else:
        hora_idx = 1 if intra < 15 else 0  # Moon then Sun for even
    d2_name = HORA_NAMES[hora_idx]

    # D-3 Drekkana (0-9°=1st, 10-19°=2nd, 20-29°=3rd)
    drek = int(intra // 10)
    d3_name = DREKKANA_NAMES[drek]

    # D-4 Chaturthamsa (each 7.5°)
    part = int(intra // 7.5)
    d4_name = CHATURTHAMSA_NAMES[part] if part < 4 else CHATURTHAMSA_NAMES[3]

    # D-7 Saptamsa
    part = int(intra // (30/7))
    d7_name = SAPTAMSA_NAMES[part] if part < 7 else SAPTAMSA_NAMES[6]

    # D-9 Navamsa: Deva/Manushya/Rakshasa based on sign type
    movable = {0, 3, 6, 9}
    fixed = {1, 4, 7, 10}
    if si in movable:
        d9_name = NAVAMSA_NAMES[0]  # Deva
    elif si in fixed:
        d9_name = NAVAMSA_NAMES[1]  # Manushya
    else:
        d9_name = NAVAMSA_NAMES[2]  # Rakshasa

    # D-10 Dasamsa
    part = int(intra // 3)
    d10_name = DASAMSA_NAMES[part] if part < 10 else DASAMSA_NAMES[9]

    # D-12 Dvadasamsa
    part = int(intra // 2.5)
    d12_name = DVADASAMSA_NAMES[part] if part < 12 else DVADASAMSA_NAMES[11]

    # D-16 Shodasamsa
    part = int(intra // (30/16))
    d16_name = SHODASAMSA_NAMES[part] if part < 16 else SHODASAMSA_NAMES[15]

    # D-20 Vimsamsa
    part = int(intra // 1.5)
    d20_name = VIMSAMSA_NAMES[part] if part < 20 else VIMSAMSA_NAMES[19]

    # D-24 Siddhamsa
    part = int(intra // 1.25)
    d24_name = SIDDHAMSA_NAMES[part] if part < 24 else SIDDHAMSA_NAMES[23]

    # D-27 Saptavimsamsa (Bhamsa) - uses Nakshatra names
    # Calculate which of 27 parts the degree falls into across the zodiac
    nak_span = 360.0 / 27.0
    nak_idx = int(lon // nak_span)
    d27_name = SAPTAVIMSAMSA_NAMES[nak_idx]

    # D-30 Trimsamsa - unequal divisions, different for odd/even
    if odd:
        if intra < 5: d30_name = TRIMSAMSA_NAMES_ODD[0]
        elif intra < 10: d30_name = TRIMSAMSA_NAMES_ODD[1]
        elif intra < 18: d30_name = TRIMSAMSA_NAMES_ODD[2]
        elif intra < 25: d30_name = TRIMSAMSA_NAMES_ODD[3]
        else: d30_name = TRIMSAMSA_NAMES_ODD[4]
    else:
        if intra < 5: d30_name = TRIMSAMSA_NAMES_EVEN[0]
        elif intra < 12: d30_name = TRIMSAMSA_NAMES_EVEN[1]
        elif intra < 20: d30_name = TRIMSAMSA_NAMES_EVEN[2]
        elif intra < 25: d30_name = TRIMSAMSA_NAMES_EVEN[3]
        else: d30_name = TRIMSAMSA_NAMES_EVEN[4]

    # D-40 Khavedamsa
    part = int(intra // 0.75)
    d40_name = KHAVEDAMSA_NAMES[part] if part < 40 else KHAVEDAMSA_NAMES[39]

    # D-45 Akshavedamsa
    part = int(intra // (30/45))
    d45_name = AKSHAVEDAMSA_NAMES[part] if part < 45 else AKSHAVEDAMSA_NAMES[44]

    # D-60 Shashtiamsa
    part = int(intra * 2)  # Each 0.5° is one shashtiamsa
    d60_name = SHASHTIAMSA_NAMES[part] if part < 60 else SHASHTIAMSA_NAMES[59]
    d60_benefic = (part + 1) in SHASHTIAMSA_BENEFIC

    return {
        'D1': d1_name,
        'D2': d2_name,
        'D3': d3_name,
        'D4': d4_name,
        'D7': d7_name,
        'D9': d9_name,
        'D10': d10_name,
        'D12': d12_name,
        'D16': d16_name,
        'D20': d20_name,
        'D24': d24_name,
        'D27': d27_name,
        'D30': d30_name,
        'D40': d40_name,
        'D45': d45_name,
        'D60': d60_name,
        'D60_benefic': d60_benefic
    }

def get_nakshatra_details(lon):
    """Get nakshatra name, pada (1-4), and percentage left in nakshatra"""
    lon = norm360(lon)
    nak_span = 360.0 / 27.0  # 13.333...
    pada_span = nak_span / 4.0  # 3.333...

    nak_idx = int(lon // nak_span)
    intra_nak = lon - nak_idx * nak_span
    pada = int(intra_nak // pada_span) + 1

    # Percentage left in nakshatra
    pct_left = ((nak_span - intra_nak) / nak_span) * 100

    return {
        'nakshatra': NAK_NAMES[nak_idx],
        'pada': pada,
        'pct_left': round(pct_left, 2)
    }

def tz_from_latlon(lat: float, lon: float) -> str:
    name = _tf.timezone_at(lat=lat, lng=lon) or _tf.certain_timezone_at(lat=lat, lng=lon)
    if not name:
        raise ValueError("Could not determine timezone for the given coordinates.")
    return name

# Updated to allow explicit tzname from the Places DB:
def local_and_utc(y, m, d, hh, mm, ss, lat, lon, tzname_override: str | None = None):
    """
    Build timezone-aware local and UTC datetimes.
    If tzname_override is provided, use that tz (e.g., 'Asia/Kolkata') instead of inferring from lat/lon.
    """
    if tzname_override:
        tzname = tzname_override
    else:
        tzname = tz_from_latlon(lat, lon)

    local_zone = tz.gettz(tzname)
    if local_zone is None:
        raise ValueError(f"Could not resolve timezone '{tzname}'")

    try:
        dt_local = datetime(y, m, d, hh, mm, ss, tzinfo=local_zone)
        dt_utc   = dt_local.astimezone(timezone.utc)
        tz_offset_hours = dt_local.utcoffset().total_seconds() / 3600.0
    except (ValueError, OverflowError):
        # Fallback for historical dates
        # Estimate offset using current standard offset for the zone
        offset_td = local_zone.utcoffset(datetime.now(timezone.utc)) or timedelta(0)
        tz_offset_hours = offset_td.total_seconds() / 3600.0
        dt_local = HistoricalDate(y, m, d, hh, mm, ss, tzinfo=local_zone)
        dt_utc = HistoricalDate(y, m, d, hh, mm, ss, tzinfo=timezone.utc)
        
    return dt_local, dt_utc, tz_offset_hours, tzname, local_zone

# ---------------------------------
# Ayanamsa Options (from Swiss Ephemeris)
# ---------------------------------
AYANAMSA_OPTIONS = {
    "Lahiri": swe.SIDM_LAHIRI,
    "Lahiri (1940)": swe.SIDM_LAHIRI_1940,
    "Lahiri ICRC": swe.SIDM_LAHIRI_ICRC,
    "Lahiri VP285": swe.SIDM_LAHIRI_VP285,
    "Raman": swe.SIDM_RAMAN,
    "Krishnamurti": swe.SIDM_KRISHNAMURTI,
    "Krishnamurti VP291": swe.SIDM_KRISHNAMURTI_VP291,
    "Fagan-Bradley": swe.SIDM_FAGAN_BRADLEY,
    "DeLuce": swe.SIDM_DELUCE,
    "Djwhal Khul": swe.SIDM_DJWHAL_KHUL,
    "Yukteshwar": swe.SIDM_YUKTESHWAR,
    "JN Bhasin": swe.SIDM_JN_BHASIN,
    "Ushashashi": swe.SIDM_USHASHASHI,
    "Pushya Paksha": swe.SIDM_TRUE_PUSHYA,
    "True Chitra": swe.SIDM_TRUE_CITRA,
    "True Revati": swe.SIDM_TRUE_REVATI,
    "True Mula": swe.SIDM_TRUE_MULA,
    "True Sheoran": swe.SIDM_TRUE_SHEORAN,
    "Suryasiddhanta": swe.SIDM_SURYASIDDHANTA,
    "Suryasiddhanta (mean Sun)": swe.SIDM_SURYASIDDHANTA_MSUN,
    "SS Chitra": swe.SIDM_SS_CITRA,
    "SS Revati": swe.SIDM_SS_REVATI,
    "Aryabhata": swe.SIDM_ARYABHATA,
    "Aryabhata (mean Sun)": swe.SIDM_ARYABHATA_MSUN,
    "Aryabhata 522": swe.SIDM_ARYABHATA_522,
    "Hipparchos": swe.SIDM_HIPPARCHOS,
    "Sassanian": swe.SIDM_SASSANIAN,
    "Aldebaran 15 Tau": swe.SIDM_ALDEBARAN_15TAU,
    "Galactic Center 0 Sag": swe.SIDM_GALCENT_0SAG,
    "Galactic Center Cochrane": swe.SIDM_GALCENT_COCHRANE,
    "Galactic Center Mula Wilhelm": swe.SIDM_GALCENT_MULA_WILHELM,
    "Galactic Center R Gilbrand": swe.SIDM_GALCENT_RGILBRAND,
    "Galactic Equator IAU 1958": swe.SIDM_GALEQU_IAU1958,
    "Galactic Equator True": swe.SIDM_GALEQU_TRUE,
    "Galactic Equator Mula": swe.SIDM_GALEQU_MULA,
    "Galactic Equator Fiorenza": swe.SIDM_GALEQU_FIORENZA,
    "Galactic Align Mardyks": swe.SIDM_GALALIGN_MARDYKS,
    "Babylonian Kugler 1": swe.SIDM_BABYL_KUGLER1,
    "Babylonian Kugler 2": swe.SIDM_BABYL_KUGLER2,
    "Babylonian Kugler 3": swe.SIDM_BABYL_KUGLER3,
    "Babylonian Huber": swe.SIDM_BABYL_HUBER,
    "Babylonian Eta Piscium": swe.SIDM_BABYL_ETPSC,
    "Babylonian Britton": swe.SIDM_BABYL_BRITTON,
    "J2000": swe.SIDM_J2000,
    "J1900": swe.SIDM_J1900,
    "B1950": swe.SIDM_B1950,
    "Valens Moon": swe.SIDM_VALENS_MOON,
}

def get_ayanamsa_list():
    """Return list of available ayanamsa names"""
    return list(AYANAMSA_OPTIONS.keys())

def get_ayanamsa_code(name: str) -> int:
    """Get Swiss Ephemeris code for ayanamsa name"""
    return AYANAMSA_OPTIONS.get(name, swe.SIDM_LAHIRI)

# ---------------------------------
# Core
# ---------------------------------
def init_ephe(ephe_path="ephe", use_moseph=False, sidereal_mode=swe.SIDM_LAHIRI):
    if not use_moseph:
        swe.set_ephe_path(ephe_path)
    if sidereal_mode is not None:
        swe.set_sid_mode(sidereal_mode)
    ephflag = swe.FLG_MOSEPH if use_moseph else swe.FLG_SWIEPH
    # Only set FLG_SIDEREAL if using sidereal mode (tropical mode when sidereal_mode is None)
    flags = ephflag | swe.FLG_SPEED
    if sidereal_mode is not None:
        flags |= swe.FLG_SIDEREAL
    return flags

def compute_chart(y, m, d, hh, mm, ss, lat, lon,
                  ephe_path="ephe", use_moseph=False, house_sys=b'O',
                  tzname_override: str | None = None,
                  ayanamsa: str | None = "Lahiri", name: str | None = None):
    # Get ayanamsa code from name (None means tropical mode)
    ayanamsa_code = get_ayanamsa_code(ayanamsa) if ayanamsa is not None else None
    FLAGS = init_ephe(ephe_path, use_moseph, sidereal_mode=ayanamsa_code)

    # time setup (with optional timezone override)
    local_dt, utc_dt, tz_offset_hours, tzname, LOCAL_ZONE = local_and_utc(
        y, m, d, hh, mm, ss, lat, lon, tzname_override=tzname_override
    )
    ut_hour  = utc_dt.hour + utc_dt.minute/60 + utc_dt.second/3600
    jd_ut    = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, ut_hour, swe.GREG_CAL)
    # For historical dates, use HistoricalDate; otherwise use standard date
    try:
        birth_date_local = date(y, m, d)
    except (ValueError, OverflowError):
        # Use HistoricalDate for dates outside Python's date range
        birth_date_local = HistoricalDate(y, m, d, 0, 0, 0, tzinfo=LOCAL_ZONE)

    # ---------------------------------
    # SUNRISE / SUNSET (Swiss Ephemeris) — robust across pyswisseph versions
    # ---------------------------------
    def _jd_to_local_dt(jd):
        # IMPORTANT: swe.revjul returns UT in HOURS, not fraction of a day.
        y_, m_, d_, ut_hours = swe.revjul(jd, swe.GREG_CAL)
        
        # Handle time components
        h_ = int(ut_hours)
        rem = (ut_hours - h_) * 60
        min_ = int(rem)
        sec_ = int((rem - min_) * 60)
        
        # Check year range for Python datetime
        if 1 <= y_ <= 9999:
            dt_utc = datetime(y_, m_, d_, h_, min_, sec_, tzinfo=timezone.utc)
            return dt_utc.astimezone(LOCAL_ZONE)
        else:
            # Return HistoricalDate for out-of-range years
            # Note: We are returning it as if it's in LOCAL_ZONE, but without proper DST adjustment
            # because dateutil/zoneinfo doesn't support ancient dates.
            # We'll just return it with the timezone info attached.
            return HistoricalDate(y_, m_, d_, h_, min_, sec_, tzinfo=LOCAL_ZONE)

    def _call_rise_trans(tjd, epheflag_for_rise, rsmi, geopos, atpress, attemp):
        """
        Try multiple pyswisseph signatures for rise_trans, from newest to oldest.
        Returns (retflag, values). Raises TypeError only if all signatures fail.
        """
        try:
            return swe.rise_trans(tjd, swe.SUN, "", epheflag_for_rise, rsmi, geopos, atpress, attemp)
        except TypeError:
            pass
        try:
            return swe.rise_trans(tjd, swe.SUN, "", epheflag_for_rise, rsmi, geopos, atpress)
        except TypeError:
            pass
        try:
            return swe.rise_trans(tjd, swe.SUN, "", epheflag_for_rise, rsmi, geopos)
        except TypeError:
            pass
        try:
            return swe.rise_trans(tjd, swe.SUN, rsmi, geopos, atpress, attemp)
        except TypeError:
            pass
        return swe.rise_trans(tjd, swe.SUN, rsmi, geopos)

    def _rsmi_for(mode):
        rsmi_rise = swe.CALC_RISE
        rsmi_set  = swe.CALC_SET
        atpress = PRESSURE_MBAR
        attemp  = TEMP_C
        if mode == "vedic":
            # center on horizon, no refraction (Hindu)
            if HINDU_BIT is not None:
                rsmi_rise |= HINDU_BIT
                rsmi_set  |= HINDU_BIT
                atpress, attemp = 0.0, 0.0
            else:
                rsmi_rise |= swe.BIT_DISC_CENTER | swe.BIT_NO_REFRACTION
                rsmi_set  |= swe.BIT_DISC_CENTER | swe.BIT_NO_REFRACTION
                atpress, attemp = 0.0, 0.0
        elif mode == "geometric":
            rsmi_rise |= swe.BIT_DISC_CENTER | swe.BIT_NO_REFRACTION
            rsmi_set  |= swe.BIT_DISC_CENTER | swe.BIT_NO_REFRACTION
            atpress, attemp = 0.0, 0.0
        # else: "astronomical" (default in this branch): upper limb + refraction
        return rsmi_rise, rsmi_set, atpress, attemp

    def _sunrise_sunset_for_anchor(anchor_jd_ut, lat_, lon_, elev_m, mode):
        """Compute next sunrise and next sunset AFTER the given UT JD anchor."""
        rsmi_rise, rsmi_set, atpress, attemp = _rsmi_for(mode)
        epheflag_for_rise = swe.FLG_MOSEPH if use_moseph else swe.FLG_SWIEPH
        geopos = (lon_, lat_, float(elev_m))
        ret_rise, val_rise = _call_rise_trans(anchor_jd_ut, epheflag_for_rise, rsmi_rise, geopos, atpress, attemp)
        if ret_rise < 0: raise RuntimeError("Sunrise computation failed.")
        ret_set,  val_set  = _call_rise_trans(anchor_jd_ut, epheflag_for_rise, rsmi_set,  geopos, atpress, attemp)
        if ret_set < 0: raise RuntimeError("Sunset computation failed.")
        return _jd_to_local_dt(val_rise[0]), _jd_to_local_dt(val_set[0])

    def _jd_ut_at_local_midnight(d_):
        """UT JD corresponding to local midnight at start of local date d_."""
        dt_local_mid = datetime(d_.year, d_.month, d_.day, 0, 0, 0, tzinfo=LOCAL_ZONE)
        dt_utc_mid = dt_local_mid.astimezone(timezone.utc)
        ut = dt_utc_mid.hour + dt_utc_mid.minute/60 + dt_utc_mid.second/3600
        return swe.julday(dt_utc_mid.year, dt_utc_mid.month, dt_utc_mid.day, ut, swe.GREG_CAL)

    def _sunrise_for_local_date(d_, lat_, lon_, elev_m, mode):
        """
        Return the sunrise whose LOCAL calendar date equals d_.
        Anchor at local midnight (converted to UT). If that still lands on the wrong
        calendar day due to edge cases, try anchors at +/-1 day and choose the one
        whose LOCAL date equals d_.
        """
        anchors = []
        try:
            anchors.append(_jd_ut_at_local_midnight(d_ - timedelta(days=1)))
        except (ValueError, OverflowError):
            pass
            
        try:
            anchors.append(_jd_ut_at_local_midnight(d_))
        except (ValueError, OverflowError):
            pass
            
        try:
            anchors.append(_jd_ut_at_local_midnight(d_ + timedelta(days=1)))
        except (ValueError, OverflowError):
            pass
        candidates = []
        for a in anchors:
            try:
                sr, _ = _sunrise_sunset_for_anchor(a, lat_, lon_, elev_m, mode)
                candidates.append(sr)
            except (ValueError, OverflowError, RuntimeError):
                pass
        for sr in candidates:
            if sr.date() == d_:
                return sr
        # fallback: choose the closest by local-date difference + time-of-day proximity
        return min(candidates, key=lambda t: abs((t.date() - d_).days) + abs((t - datetime(t.year, t.month, t.day, tzinfo=t.tzinfo)).total_seconds())/86400.0)

    def _sunset_for_local_date(d_, lat_, lon_, elev_m, mode):
        anchors = []
        try:
            anchors.append(_jd_ut_at_local_midnight(d_ - timedelta(days=1)))
        except (ValueError, OverflowError):
            pass
            
        try:
            anchors.append(_jd_ut_at_local_midnight(d_))
        except (ValueError, OverflowError):
            pass
            
        try:
            anchors.append(_jd_ut_at_local_midnight(d_ + timedelta(days=1)))
        except (ValueError, OverflowError):
            pass
        candidates = []
        for a in anchors:
            try:
                _, ss = _sunrise_sunset_for_anchor(a, lat_, lon_, elev_m, mode)
                candidates.append(ss)
            except (ValueError, OverflowError, RuntimeError):
                pass
        for ss in candidates:
            if ss.date() == d_:
                return ss
        return min(candidates, key=lambda t: abs((t.date() - d_).days) + abs((t - datetime(t.year, t.month, t.day, tzinfo=t.tzinfo)).total_seconds())/86400.0)

    # Get sunrise/sunset for the requested local date (using requested definition)
    # For accuracy, do not substitute arbitrary times; fail if Swiss Ephemeris cannot compute.
    if isinstance(birth_date_local, HistoricalDate):
        # Use Swiss Ephemeris directly with astronomical year numbering
        rsmi_rise, rsmi_set, atpress, attemp = _rsmi_for(SUNRISE_DEFINITION)
        epheflag_for_rise = swe.FLG_MOSEPH if use_moseph else swe.FLG_SWIEPH
        geopos = (lon, lat, float(SITE_ELEVATION_M))

        def jd_to_hist_local(jd_ut):
            jd_local = jd_ut + (tz_offset_hours / 24.0)
            y_, m_, d_, local_hours = swe.revjul(jd_local, swe.GREG_CAL)
            h_ = int(local_hours)
            rem = (local_hours - h_) * 60
            min_ = int(rem)
            sec_ = int((rem - min_) * 60)
            return HistoricalDate(y_, m_, d_, h_, min_, sec_, tzinfo=LOCAL_ZONE)

        def rise_set_for_day(day_offset):
            # Anchor at 0h UT on the target day; convert to local after rise/set
            jd_anchor_ut = swe.julday(y, m, d + day_offset, 0.0, swe.GREG_CAL)
            ret_rise, val_rise = _call_rise_trans(jd_anchor_ut, epheflag_for_rise, rsmi_rise, geopos, atpress, attemp)
            ret_set, val_set = _call_rise_trans(jd_anchor_ut, epheflag_for_rise, rsmi_set, geopos, atpress, attemp)
            if ret_rise < 0 or ret_set < 0:
                raise RuntimeError("Rise/set computation failed for historical date")
            return jd_to_hist_local(val_rise[0]), jd_to_hist_local(val_set[0])

        sunrise_prev_local, _ = rise_set_for_day(-1)
        sunrise_local, sunset_local = rise_set_for_day(0)
        sunrise_next_local, _ = rise_set_for_day(1)
    else:
        try:
            sunrise_local = _sunrise_for_local_date(birth_date_local, lat, lon, SITE_ELEVATION_M, SUNRISE_DEFINITION)
            sunset_local  = _sunset_for_local_date (birth_date_local, lat, lon, SITE_ELEVATION_M, SUNRISE_DEFINITION)
        except Exception as e:
            raise RuntimeError(f"Sunrise/sunset calculation failed: {e}")
                
        # And bracketing sunrises for Hora partitioning
        try:
            sunrise_prev_local = _sunrise_for_local_date(birth_date_local - timedelta(days=1), lat, lon, SITE_ELEVATION_M, SUNRISE_DEFINITION)
        except Exception as e:
            raise RuntimeError(f"Previous sunrise calculation failed: {e}")

        try:
            sunrise_next_local = _sunrise_for_local_date(birth_date_local + timedelta(days=1), lat, lon, SITE_ELEVATION_M, SUNRISE_DEFINITION)
        except Exception as e:
            raise RuntimeError(f"Next sunrise calculation failed: {e}")
    
    # Calculate Janma Ghatis early (needed for special Lagnas)
    if isinstance(local_dt, HistoricalDate) or isinstance(sunrise_local, HistoricalDate):
        # For historical dates, approximate Janma Ghatis based on simple time difference
        # Compare using timestamps if possible, otherwise estimate based on hours
        since_sunrise_hours = (local_dt.hour - sunrise_local.hour) + (local_dt.minute - sunrise_local.minute)/60.0
        if since_sunrise_hours < 0:
            since_sunrise_hours += 24  # Handle day wraparound
        since_sunrise = since_sunrise_hours * 3600.0  # Convert to seconds
    elif sunrise_local <= local_dt < sunrise_next_local:
        since_sunrise = (local_dt - sunrise_local).total_seconds()
    elif local_dt < sunrise_local:
        since_sunrise = (local_dt - sunrise_prev_local).total_seconds()
    else:
        since_sunrise = (local_dt - sunrise_next_local).total_seconds()
    janma_ghatis = round(since_sunrise / (24 * 60), 4)  # 1 ghati = 24 minutes = 1440 seconds

    def local_dt_to_jd_ut(dt_local):
        """
        Convert a timezone-aware datetime (or HistoricalDate with tzinfo) to UT Julian day.
        Falls back to birth jd if conversion fails.
        """
        try:
            if isinstance(dt_local, datetime):
                dt_utc = dt_local.astimezone(timezone.utc)
                ut_hours = dt_utc.hour + dt_utc.minute/60 + dt_utc.second/3600
                return swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, ut_hours, swe.GREG_CAL)
            # HistoricalDate: assume stored in local time with tzinfo carrying offset hours
            ut_hours = dt_local.hour - tz_offset_hours + dt_local.minute/60 + dt_local.second/3600
            return swe.julday(dt_local.year, dt_local.month, dt_local.day, ut_hours, swe.GREG_CAL)
        except Exception:
            return jd_ut

    # Sun longitude at local sunrise (sidereal)
    sunrise_jd_ut = local_dt_to_jd_ut(sunrise_local)
    sunrise_sun_lon_sid = norm360(swe.calc_ut(sunrise_jd_ut, swe.SUN, FLAGS)[0][0])

    # ---------------------------------
    # Houses, ayanāṁśa
    # ---------------------------------
    cusps_trop, ascmc_trop = swe.houses(jd_ut, lat, lon, house_sys)
    # For tropical mode (ayanamsa is None), ayanamsa value is 0
    if ayanamsa is None:
        ayan = 0.0
        ayanamsa_name = "Tropical"
    else:
        ayan = swe.get_ayanamsa_ut(jd_ut)
        ayanamsa_name = ayanamsa
    asc_sid = norm360(ascmc_trop[0] - ayan)
    mc_sid  = norm360(ascmc_trop[1] - ayan)
    asc_sign_idx = lon_to_sign_idx(asc_sid)

    # ---------------------------------
    # Planets / points
    # ---------------------------------
    def calc_vals(code): return swe.calc_ut(jd_ut, code, FLAGS)[0]

    rows=[]; numeric_lons={}; vargas_data = {}
    
    for nm, lonv, label in [("Ascendant (1st House Cusp)", asc_sid, "Ascendant (1st House Cusp)"),
                            ("10th House Cusp", mc_sid, "10th House Cusp")]:
        nsi, _ = navamsa_for(lonv)
        nak_det = get_nakshatra_details(lonv)
        all_vargas = get_all_vargas(lonv)
        varga_names = get_varga_names(lonv)
        vargas_data[nm] = all_vargas
        rows.append({
            "Point": label,
            "Longitude (Sign DMS)": sign_dms_str(lonv),
            "Longitude (Dec)": round(lonv, 4),
            "Rashi": rashi_name(lonv),
            "Rashi_Idx": lon_to_sign_idx(lonv),
            "Nakshatra": nak_det['nakshatra'],
            "Pada": nak_det['pada'],
            "Nak_Pct_Left": nak_det['pct_left'],
            "Navamsha": RASHI_SA[nsi],
            "Navamsha_Idx": nsi,
            # All divisional chart indices for UI rendering
            "D2": all_vargas['D2'],
            "D3": all_vargas['D3'],
            "D4": all_vargas['D4'],
            "D7": all_vargas['D7'],
            "D10": all_vargas['D10'],
            "D12": all_vargas['D12'],
            "D16": all_vargas['D16'],
            "D20": all_vargas['D20'],
            "D24": all_vargas['D24'],
            "D27": all_vargas['D27'],
            "D30": all_vargas['D30'],
            "D40": all_vargas['D40'],
            "D45": all_vargas['D45'],
            "D60": all_vargas['D60'],
            # Varga names for display
            "Varga_Names": varga_names,
            "Latitude (DMS)": "—",
            "Speed (DMS/day)": "—",
            "Retro": False
        })
        numeric_lons[nm] = lonv

    for nm, code in PLANETS.items():
        vals = calc_vals(code); lonv, latv, spd = norm360(vals[0]), vals[1], vals[3]
        numeric_lons[nm] = lonv
        nsi, _ = navamsa_for(lonv)
        nak_det = get_nakshatra_details(lonv)
        all_vargas = get_all_vargas(lonv)
        varga_names = get_varga_names(lonv)
        vargas_data[nm] = all_vargas
        is_retro = spd < 0
        rows.append({
            "Point": nm,
            "Longitude (Sign DMS)": sign_dms_str(lonv),
            "Longitude (Dec)": round(lonv, 4),
            "Rashi": rashi_name(lonv),
            "Rashi_Idx": lon_to_sign_idx(lonv),
            "Nakshatra": nak_det['nakshatra'],
            "Pada": nak_det['pada'],
            "Nak_Pct_Left": nak_det['pct_left'],
            "Navamsha": RASHI_SA[nsi],
            "Navamsha_Idx": nsi,
            # All divisional chart indices for UI rendering
            "D2": all_vargas['D2'],
            "D3": all_vargas['D3'],
            "D4": all_vargas['D4'],
            "D7": all_vargas['D7'],
            "D10": all_vargas['D10'],
            "D12": all_vargas['D12'],
            "D16": all_vargas['D16'],
            "D20": all_vargas['D20'],
            "D24": all_vargas['D24'],
            "D27": all_vargas['D27'],
            "D30": all_vargas['D30'],
            "D40": all_vargas['D40'],
            "D45": all_vargas['D45'],
            "D60": all_vargas['D60'],
            # Varga names for display
            "Varga_Names": varga_names,
            "Latitude (DMS)": f"{'N' if latv>=0 else 'S'} {dms_str(latv)}",
            "Speed (DMS/day)": ("-" if spd<0 else "+")+dms_str(abs(spd))+"/day",
            "Retro": is_retro
        })

    # true node
    try: vals_true = swe.calc_ut(jd_ut, swe.TRUE_NODE, FLAGS)[0]
    except Exception:
        vals_true = swe.nod_aps_ut(jd_ut, swe.MOON, FLAGS, swe.NODBIT_OSCU)[0]
    rahu = norm360(vals_true[0]); ketu = norm360(rahu+180)
    numeric_lons["Rahu (true)"] = rahu; numeric_lons["Ketu (true)"] = ketu
    for nm, lonv in [("Rahu (true)", rahu), ("Ketu (true)", ketu)]:
        nsi, _ = navamsa_for(lonv)
        nak_det = get_nakshatra_details(lonv)
        all_vargas = get_all_vargas(lonv)
        varga_names = get_varga_names(lonv)
        vargas_data[nm] = all_vargas
        rows.append({
            "Point": nm,
            "Longitude (Sign DMS)": sign_dms_str(lonv),
            "Longitude (Dec)": round(lonv, 4),
            "Rashi": rashi_name(lonv),
            "Rashi_Idx": lon_to_sign_idx(lonv),
            "Nakshatra": nak_det['nakshatra'],
            "Pada": nak_det['pada'],
            "Nak_Pct_Left": nak_det['pct_left'],
            "Navamsha": RASHI_SA[nsi],
            "Navamsha_Idx": nsi,
            # All divisional chart indices for UI rendering
            "D2": all_vargas['D2'],
            "D3": all_vargas['D3'],
            "D4": all_vargas['D4'],
            "D7": all_vargas['D7'],
            "D10": all_vargas['D10'],
            "D12": all_vargas['D12'],
            "D16": all_vargas['D16'],
            "D20": all_vargas['D20'],
            "D24": all_vargas['D24'],
            "D27": all_vargas['D27'],
            "D30": all_vargas['D30'],
            "D40": all_vargas['D40'],
            "D45": all_vargas['D45'],
            "D60": all_vargas['D60'],
            # Varga names for display
            "Varga_Names": varga_names,
            "Latitude (DMS)": "—",
            "Speed (DMS/day)": "—",
            "Retro": True  # Rahu/Ketu always retrograde
        })
    
    # Calculate special Lagnas (need janma_ghatis and Sun/Moon positions)
    # Get Sun and Moon sidereal longitudes from numeric_lons (already calculated in planets loop)
    sun_lon_sid = numeric_lons.get("Sun", 0)
    moon_lon_sid = numeric_lons.get("Moon", 0)
    
    # Calculate special Lagnas
    def calculate_hora_lagna(sunrise_sun_lon, janma_ghatis):
        """
        Hora Lagna: 1 sign every 2.5 ghatis (60 minutes) from sunrise.
        Advance = janma_ghatis * 12 degrees from sunrise Sun.
        """
        advance_deg = janma_ghatis * 12.0
        return norm360(sunrise_sun_lon + advance_deg)
    
    def calculate_bhava_lagna(sunrise_sun_lon, janma_ghatis):
        """
        Bhava Lagna: every 5 ghatis = 1 sign. Advance = (janma_ghatis / 5) signs from sunrise Sun.
        Degrees = janma_ghatis * 6.
        """
        advance_deg = janma_ghatis * 6.0
        return norm360(sunrise_sun_lon + advance_deg)
    
    def calculate_ghati_lagna(sunrise_sun_lon, janma_ghatis):
        """
        Ghati Lagna per classics:
          - Ghatis past sunrise = whole signs
          - Vighatis (1/60 ghati) converted to degrees: vighati/2 degrees (30 arcmin each)
        """
        ghatis_whole = int(janma_ghatis)
        vighatis = (janma_ghatis - ghatis_whole) * 60.0
        advance_deg = ghatis_whole * 30.0 + vighatis * 0.5
        return norm360(sunrise_sun_lon + advance_deg)
    
    def calculate_pranapada_lagna(sun_lon, janma_ghatis):
        """Pranapada Lagna = Sun + (Janma Ghatis * 30)"""
        return norm360(sun_lon + (janma_ghatis * 30))
    
    def calculate_sree_lagna(asc_lon, sun_lon, moon_lon):
        """Sree Lagna = Ascendant + (Moon - Sun)"""
        return norm360(asc_lon + (moon_lon - sun_lon))
    
    def calculate_indu_lagna(sun_lon):
        """Indu Lagna = Sun position"""
        return norm360(sun_lon)
    
    hora_lagna_lon = calculate_hora_lagna(sunrise_sun_lon_sid, janma_ghatis)
    bhava_lagna_lon = calculate_bhava_lagna(sunrise_sun_lon_sid, janma_ghatis)
    ghati_lagna_lon = calculate_ghati_lagna(sunrise_sun_lon_sid, janma_ghatis)
    pranapada_lagna_lon = calculate_pranapada_lagna(sun_lon_sid, janma_ghatis)
    sree_lagna_lon = calculate_sree_lagna(asc_sid, sun_lon_sid, moon_lon_sid)
    indu_lagna_lon = calculate_indu_lagna(sun_lon_sid)
    
    # Add special Lagnas to rows
    special_lagnas = [
        ("Hora Lagna", hora_lagna_lon),
        ("Bhava Lagna", bhava_lagna_lon),
        ("Ghati Lagna", ghati_lagna_lon),
        ("Pranapada Lagna", pranapada_lagna_lon),
        ("Sree Lagna", sree_lagna_lon),
        ("Indu Lagna", indu_lagna_lon)
    ]

    for nm, lonv in special_lagnas:
        nsi, _ = navamsa_for(lonv)
        nak_det = get_nakshatra_details(lonv)
        all_vargas = get_all_vargas(lonv)
        varga_names = get_varga_names(lonv)
        vargas_data[nm] = all_vargas
        rows.append({
            "Point": nm,
            "Longitude (Sign DMS)": sign_dms_str(lonv),
            "Longitude (Dec)": round(lonv, 4),
            "Rashi": rashi_name(lonv),
            "Rashi_Idx": lon_to_sign_idx(lonv),
            "Nakshatra": nak_det['nakshatra'],
            "Pada": nak_det['pada'],
            "Nak_Pct_Left": nak_det['pct_left'],
            "Navamsha": RASHI_SA[nsi],
            "Navamsha_Idx": nsi,
            # All divisional chart indices for UI rendering
            "D2": all_vargas['D2'],
            "D3": all_vargas['D3'],
            "D4": all_vargas['D4'],
            "D7": all_vargas['D7'],
            "D10": all_vargas['D10'],
            "D12": all_vargas['D12'],
            "D16": all_vargas['D16'],
            "D20": all_vargas['D20'],
            "D24": all_vargas['D24'],
            "D27": all_vargas['D27'],
            "D30": all_vargas['D30'],
            "D40": all_vargas['D40'],
            "D45": all_vargas['D45'],
            "D60": all_vargas['D60'],
            # Varga names for display
            "Varga_Names": varga_names,
            "Latitude (DMS)": "—",
            "Speed (DMS/day)": "—",
            "Retro": False
        })
        numeric_lons[nm] = lonv

    # Varnada for Lagna and each house (Rasi-based houses from Ascendant sign)
    hora_sign_idx = lon_to_sign_idx(hora_lagna_lon)

    def varnada_for_sign(base_sign_idx):
        """
        Compute Varnada sign index for a given base sign (0-11) using Hora Lagna sign.
        Follows BPHS rule: odd signs count from Aries forward, even signs from Pisces backward.
        """
        base_num = base_sign_idx + 1
        hora_num = hora_sign_idx + 1
        base_count = base_num if base_num % 2 == 1 else 13 - base_num
        hora_count = hora_num if hora_num % 2 == 1 else 13 - hora_num
        total = base_count + hora_count if (base_count % 2) == (hora_count % 2) else abs(base_count - hora_count)
        if total == 0:
            return base_sign_idx
        if total % 2 == 1:
            sign_num = ((total - 1) % 12) + 1  # direct from Aries
        else:
            sign_num = 12 - ((total - 1) % 12)  # reverse from Pisces
        return (sign_num - 1) % 12

    varnada_by_house = {}
    for offset in range(12):
        house_num = offset + 1
        house_sign_idx = (asc_sign_idx + offset) % 12
        varnada_idx = varnada_for_sign(house_sign_idx)
        varnada_by_house[house_num] = varnada_idx
        varnada_lon = varnada_idx * 30.0
        nsi, _ = navamsa_for(varnada_lon)
        nak_det = get_nakshatra_details(varnada_lon)
        all_vargas = get_all_vargas(varnada_lon)
        varga_names = get_varga_names(varnada_lon)
        vargas_data_name = "Varnada Lagna" if house_num == 1 else f"Varnada H{house_num}"
        vargas_data[vargas_data_name] = all_vargas
        rows.append({
            "Point": vargas_data_name,
            "Longitude (Sign DMS)": sign_dms_str(varnada_lon),
            "Longitude (Dec)": round(varnada_lon, 4),
            "Rashi": rashi_name(varnada_lon),
            "Rashi_Idx": varnada_idx,
            "Nakshatra": nak_det['nakshatra'],
            "Pada": nak_det['pada'],
            "Nak_Pct_Left": nak_det['pct_left'],
            "Navamsha": RASHI_SA[nsi],
            "Navamsha_Idx": nsi,
            "D2": all_vargas['D2'],
            "D3": all_vargas['D3'],
            "D4": all_vargas['D4'],
            "D7": all_vargas['D7'],
            "D10": all_vargas['D10'],
            "D12": all_vargas['D12'],
            "D16": all_vargas['D16'],
            "D20": all_vargas['D20'],
            "D24": all_vargas['D24'],
            "D27": all_vargas['D27'],
            "D30": all_vargas['D30'],
            "D40": all_vargas['D40'],
            "D45": all_vargas['D45'],
            "D60": all_vargas['D60'],
            "Varga_Names": varga_names,
            "Latitude (DMS)": "—",
            "Speed (DMS/day)": "—",
            "Retro": False,
            "IsVarnada": True,
            "House": house_num,
        })
        numeric_lons[vargas_data_name] = varnada_lon

    # Arudha Padas for houses 1..12 (Upapada for 12th)
    def arudha_sign_for_house(house_sign_idx: int, lord_sign_idx: int | None) -> int | None:
        if lord_sign_idx is None:
            return None
        offset = (lord_sign_idx - house_sign_idx + 12) % 12  # distance in signs from house to lord
        # If lord in 4th, pada is where the lord sits
        if offset == 3:
            return lord_sign_idx
        # Base pada: count the same offset from the lord
        pada_idx = (lord_sign_idx + offset) % 12
        # Same-house -> shift to 10th from the house
        if offset == 0:
            return (house_sign_idx + 9) % 12
        # 7th-house -> shift to 4th from the house
        if offset == 6:
            return (house_sign_idx + 3) % 12
        # If computed pada lands on same or 7th, adjust per rule
        if pada_idx == house_sign_idx:
            return (house_sign_idx + 9) % 12
        if pada_idx == (house_sign_idx + 6) % 12:
            return (house_sign_idx + 3) % 12
        return pada_idx

    for offset in range(12):
        house_num = offset + 1
        house_sign_idx = (asc_sign_idx + offset) % 12
        lord = SIGN_LORD.get(house_sign_idx)
        lord_lon = numeric_lons.get(lord, None)
        lord_sign_idx = lon_to_sign_idx(lord_lon) if lord_lon is not None else None
        pada_sign_idx = arudha_sign_for_house(house_sign_idx, lord_sign_idx)
        if pada_sign_idx is None:
            continue
        pada_lon = pada_sign_idx * 30.0
        nsi, _ = navamsa_for(pada_lon)
        nak_det = get_nakshatra_details(pada_lon)
        all_vargas = get_all_vargas(pada_lon)
        varga_names = get_varga_names(pada_lon)
        is_ul = house_num == 12
        point_name = "Arudha Lagna" if house_num == 1 else ("Upapada Lagna" if is_ul else f"Arudha H{house_num}")
        vargas_data[point_name] = all_vargas
        rows.append({
            "Point": point_name,
            "Longitude (Sign DMS)": sign_dms_str(pada_lon),
            "Longitude (Dec)": round(pada_lon, 4),
            "Rashi": rashi_name(pada_lon),
            "Rashi_Idx": pada_sign_idx,
            "Nakshatra": nak_det['nakshatra'],
            "Pada": nak_det['pada'],
            "Nak_Pct_Left": nak_det['pct_left'],
            "Navamsha": RASHI_SA[nsi],
            "Navamsha_Idx": nsi,
            "D2": all_vargas['D2'],
            "D3": all_vargas['D3'],
            "D4": all_vargas['D4'],
            "D7": all_vargas['D7'],
            "D10": all_vargas['D10'],
            "D12": all_vargas['D12'],
            "D16": all_vargas['D16'],
            "D20": all_vargas['D20'],
            "D24": all_vargas['D24'],
            "D27": all_vargas['D27'],
            "D30": all_vargas['D30'],
            "D40": all_vargas['D40'],
            "D45": all_vargas['D45'],
            "D60": all_vargas['D60'],
            "Varga_Names": varga_names,
            "Latitude (DMS)": "—",
            "Speed (DMS/day)": "—",
            "Retro": False,
            "IsArudha": True,
            "House": house_num,
        })
        numeric_lons[point_name] = pada_lon

    points_df = pd.DataFrame(rows)
    order_points = ["Ascendant (1st House Cusp)","10th House Cusp","Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Uranus","Neptune","Pluto","Rahu (true)","Ketu (true)","Hora Lagna","Ghati Lagna","Pranapada Lagna","Sree Lagna","Indu Lagna"]
    varnada_order = ["Varnada Lagna"] + [f"Varnada H{i}" for i in range(2, 13)]
    arudha_order = ["Arudha Lagna"] + [f"Arudha H{i}" for i in range(2, 12)] + ["Upapada Lagna"]
    order_points = order_points + varnada_order + arudha_order
    points_df["__o__"] = points_df["Point"].apply(lambda x: order_points.index(x) if x in order_points else 999)
    points_df = points_df.sort_values("__o__").drop(columns="__o__").reset_index(drop=True)

    # ---------------------------------
    # Śrīpati (Porphyry) houses — spans between cusps
    # ---------------------------------
    def unwrap(seq):
        out=[seq[0]]
        for v in seq[1:]:
            pv=out[-1]
            if v<pv: v+=360.0
            out.append(v)
        return out

    def mid(a,b):
        if b<a: b+=360.0
        return (a+b)/2.0

    cusps_sid = [norm360(c - ayan) for c in cusps_trop]
    cusps_unw = unwrap(cusps_sid)
    starts, ends = [], []
    for i in range(12):
        cprev = cusps_unw[i-1] if i>0 else cusps_unw[-1]-360.0
        ci    = cusps_unw[i]
        cnext = cusps_unw[i+1] if i<11 else cusps_unw[0]+360.0
        s = mid(cprev, ci); e = mid(ci, cnext)
        starts.append(norm360(s)); ends.append(norm360(e))

    def arc_contains(start, end, x):
        start = norm360(start); end = norm360(end); x = norm360(x)
        return (start <= end and start <= x < end) or (start > end and (x >= start or x < end))

    house_occ = {i+1: [] for i in range(12)}
    for g in GRAHAS_FOR_HOUSE:
        glon = numeric_lons[g]
        found = 12
        for i in range(12):
            if arc_contains(starts[i], ends[i], glon): found = i+1; break
        house_occ[found].append(g.replace(" (true)",""))

    house_rows = [{"House": i+1,
                   "Start (Sign DMS)": sign_dms_str(starts[i]),
                   "Cusp (Sign DMS)":  sign_dms_str(cusps_sid[i]),
                   "End (Sign DMS)":   sign_dms_str(ends[i]),
                   "Occupants": ", ".join(house_occ[i+1]) if house_occ[i+1] else ""} for i in range(12)]
    houses_df = pd.DataFrame(house_rows).sort_values("House").reset_index(drop=True)

    # ---------------------------------
    # Aspect grid (planets aspecting planets + equal-house cusps)
    # ---------------------------------
    def pct_to_color(pct: float) -> str:
        """
        Map 0-100% to a red->green gradient (HSL hue 0->120) for UI heatmap.
        """
        pct_clamped = max(0.0, min(100.0, pct))
        hue = (pct_clamped / 100.0) * 120.0
        r, g, b = colorsys.hls_to_rgb(hue / 360.0, 0.5, 0.7)
        return "#{:02x}{:02x}{:02x}".format(int(round(r * 255)), int(round(g * 255)), int(round(b * 255)))

    aspect_planets = [p for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu (true)", "Ketu (true)", "Uranus", "Neptune", "Pluto"] if p in numeric_lons]
    # Bhava Chalit cusps (sidereal, from computed houses)
    aspect_targets = []
    for p in aspect_planets:
        aspect_targets.append({"Name": p, "Longitude": numeric_lons[p], "Type": "Planet"})
    for idx, lonv in enumerate(cusps_sid):
        aspect_targets.append({"Name": f"House {idx+1}", "Longitude": lonv, "Type": "House Cusp"})

    aspect_rows = []
    for tgt in aspect_targets:
        tgt_lon = tgt["Longitude"]
        row = {
            "Target": tgt["Name"],
            "Longitude": sign_dms_str(tgt_lon),
        }
        for src in aspect_planets:
            src_lon = numeric_lons.get(src)
            if src_lon is None:
                row[src] = None
                row[f"{src}_color"] = None
                continue
            if tgt["Name"] == src:
                row[src] = None  # self aspect not meaningful
                row[f"{src}_color"] = "#9aa3ad"
                continue
            angle = norm360(tgt_lon - src_lon)
            pct = round(aspect_strength_pct(angle, src), 1)
            row[src] = pct
            row[f"{src}_color"] = pct_to_color(pct)
        aspect_rows.append(row)

    aspect_grid_df = pd.DataFrame(aspect_rows)

    # ---------------------------------
    # Pushkara Amsa / Pushkara Bhaga / Mrityu Bhaga table
    # ---------------------------------
    def format_deg_range(start_deg, end_deg):
        return f"{dms_str(start_deg)}–{dms_str(end_deg)}"

    def label_with_color(text, color_hex):
        fg = "#0f1a1c" if color_hex else ""
        return f'<span style="display:inline-block;padding:2px 6px;border-radius:4px;background:{color_hex};color:{fg};">{text}</span>' if color_hex else text

    def tol_for(name):
        slow = {"Jupiter", "Saturn", "Rahu (true)", "Ketu (true)", "Uranus", "Neptune", "Pluto"}
        return 0.5 if name in slow else 1.0

    def pushkara_flags(name, lon):
        si = lon_to_sign_idx(lon)
        intra = norm360(lon) - si * 30.0
        # Pushkara aṁśa
        ranges = PUSHKARA_AMSA_RANGES[si]
        in_amsa = None
        for s, e in ranges:
            if s <= intra <= e:
                in_amsa = (s, e)
                break
        amsa_text = "Yes" + (f" ({format_deg_range(*in_amsa)})" if in_amsa else "")
        if in_amsa is None:
            amsa_text = "No"
        # Pushkara bhaga (use 1 arcmin tolerance)
        pb_deg = PUSHKARA_BHAGA_DEG[si]
        tol = tol_for(name)
        in_pb = abs(intra - pb_deg) <= tol
        pb_offset = abs(intra - pb_deg)
        pb_label = f"Yes (Δ {pb_offset:.2f}° from {dms_str(pb_deg)})" if in_pb else f"No (Δ {pb_offset:.2f}° to {dms_str(pb_deg)})"
        pb_color = "#b7e3b5" if in_pb else ""
        # Mrityu bhaga
        mb_deg = MRITYU_BHAGA_DEG[si]
        in_mb = abs(intra - mb_deg) <= tol
        mb_offset = abs(intra - mb_deg)
        mb_label = f"Yes (Δ {mb_offset:.2f}° from {dms_str(mb_deg)})" if in_mb else f"No (Δ {mb_offset:.2f}° to {dms_str(mb_deg)})"
        mb_color = "#f5b7b1" if in_mb else ""
        return amsa_text, pb_label, pb_color, mb_label, mb_color, si

    push_targets = []
    planet_list_for_push = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu (true)", "Ketu (true)", "Uranus", "Neptune", "Pluto"]
    for p in planet_list_for_push:
        if p in numeric_lons:
            push_targets.append((p, numeric_lons[p]))
    for idx, lonv in enumerate(cusps_sid):
        push_targets.append((f"House {idx+1}", lonv))

    push_rows = []
    for name, lonv in push_targets:
        amsa_text, pb_text, pb_color, mb_text, mb_color, si = pushkara_flags(name, lonv)
        push_rows.append({
            "Target": name,
            "Sign": RASHI_ABR[si],
            "Longitude": sign_dms_str(lonv),
            "Pushkara Amsa": label_with_color(amsa_text, "#b7e3b5" if "Yes" in amsa_text else ""),
            "Pushkara Bhaga": label_with_color(pb_text, pb_color),
            "Mrityu Bhaga": label_with_color(mb_text, mb_color)
        })
    pushkara_df = pd.DataFrame(push_rows)

    # ---------------------------------
    # Vimśottarī (Mahādaśā only)
    # ---------------------------------
    NAK_STEP = 360.0/27.0
    MD_ORDER = ["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"]
    MD_YEARS = {"Ketu":7, "Venus":20, "Sun":6, "Moon":10, "Mars":7, "Rahu":18, "Jupiter":16, "Saturn":19, "Mercury":17}

    moon_lon = numeric_lons["Moon"]
    nak_index = int(moon_lon // NAK_STEP)
    frac_in   = (moon_lon - nak_index*NAK_STEP) / NAK_STEP
    frac_left = 1.0 - frac_in

    start_md_i = nak_index % 9
    start_md   = MD_ORDER[start_md_i]
    start_md_left_years = MD_YEARS[start_md] * frac_left

    def years_to_days(yf): return yf*365.25

    def build_vim_md(local_start):
        rows=[]; cur=local_start
        seq=[(start_md, start_md_left_years)]
        j=(start_md_i+1)%9; spent=start_md_left_years
        while spent < 120 - 1e-9:
            lord=MD_ORDER[j]; y2=MD_YEARS[lord]
            seq.append((lord,y2)); spent += y2; j=(j+1)%9
        for lord,yrs in seq:
            st=cur; en=st+timedelta(days=years_to_days(yrs))
            rows.append({"Mahadasa": lord,"Start (local)": st.strftime("%Y-%m-%d %H:%M:%S"),
                         "End (local)": en.strftime("%Y-%m-%d %H:%M:%S"),"Duration (years)": round(yrs,6)})
            cur=en
        return pd.DataFrame(rows)

    vim_md_df = build_vim_md(local_dt)

    # ---------------------------------
    # Vimśottarī Antardaśā & Pratyantardaśā functions
    # ---------------------------------
    def build_antardasha(md_lord, md_start, md_duration_years):
        """Build Antardasha periods within a Mahadasha."""
        rows = []
        cur = md_start if isinstance(md_start, datetime) else datetime.strptime(md_start, "%Y-%m-%d %H:%M:%S")
        
        # Antardasha sequence starts with Mahadasha lord
        md_idx = MD_ORDER.index(md_lord)
        total_md_days = md_duration_years * 365.25
        
        for i in range(9):
            ad_lord = MD_ORDER[(md_idx + i) % 9]
            # Antardasha duration = (MD years * AD years) / 120 years
            ad_years = (md_duration_years * MD_YEARS[ad_lord]) / 120.0
            ad_days = ad_years * 365.25
            end = cur + timedelta(days=ad_days)
            
            rows.append({
                "Mahadasa": md_lord,
                "Antardasa": ad_lord,
                "Start": cur.strftime("%Y-%m-%d %H:%M:%S"),
                "End": end.strftime("%Y-%m-%d %H:%M:%S"),
                "Duration (days)": round(ad_days, 2)
            })
            cur = end
        
        return rows
    
    def build_pratyantardasha(md_lord, ad_lord, ad_start, ad_duration_days):
        """Build Pratyantardasha periods within an Antardasha."""
        rows = []
        cur = ad_start if isinstance(ad_start, datetime) else datetime.strptime(ad_start, "%Y-%m-%d %H:%M:%S")
        
        # Pratyantardasha sequence starts with Antardasha lord
        ad_idx = MD_ORDER.index(ad_lord)
        
        for i in range(9):
            pd_lord = MD_ORDER[(ad_idx + i) % 9]
            # Pratyantardasha duration = (AD days * PD years) / 120 years
            pd_days = (ad_duration_days * MD_YEARS[pd_lord]) / 120.0
            end = cur + timedelta(days=pd_days)
            
            rows.append({
                "Mahadasa": md_lord,
                "Antardasa": ad_lord,
                "Pratyantardasa": pd_lord,
                "Start": cur.strftime("%Y-%m-%d %H:%M:%S"),
                "End": end.strftime("%Y-%m-%d %H:%M:%S"),
                "Duration (days)": round(pd_days, 2)
            })
            cur = end
        
        return rows

    # ---------------------------------
    # Yoginī (major)
    # ---------------------------------
    YOG_ORDER = ["Mangala","Pingala","Dhanya","Bhramari","Bhadrika","Ulka","Siddha","Sankata"]
    YOG_YEARS = {"Mangala":1,"Pingala":2,"Dhanya":3,"Bhramari":4,"Bhadrika":5,"Ulka":6,"Siddha":7,"Sankata":8}
    N2Y = {0:"Bhramari",1:"Bhadrika",2:"Ulka",3:"Siddha",4:"Sankata",5:"Mangala",6:"Pingala",7:"Dhanya",
           8:"Bhramari",9:"Bhadrika",10:"Ulka",11:"Siddha",12:"Sankata",13:"Mangala",14:"Pingala",15:"Dhanya",
           16:"Bhramari",17:"Bhadrika",18:"Ulka",19:"Siddha",20:"Sankata",21:"Mangala",22:"Pingala",23:"Dhanya",
           24:"Bhramari",25:"Bhadrika",26:"Ulka"}
    start_yog = N2Y[nak_index]

    def build_yogini(local_start, cycles=3):
        rows=[]; cur=local_start; yog_i=YOG_ORDER.index(start_yog)
        y1=YOG_YEARS[start_yog]*frac_left
        rows.append({"Yogini":YOG_ORDER[yog_i],
                     "Start (local)":cur.strftime("%Y-%m-%d %H:%M:%S"),
                     "End (local)":(cur+timedelta(days=years_to_days(y1))).strftime("%Y-%m-%d %H:%M:%S"),
                     "Duration (years)":round(y1,6)})
        cur+=timedelta(days=years_to_days(y1)); yog_i=(yog_i+1)%8
        for _ in range(cycles*8 - 1):
            lord=YOG_ORDER[yog_i]; y2=YOG_YEARS[lord]; end=cur+timedelta(days=years_to_days(y2))
            rows.append({"Yogini":lord,"Start (local)":cur.strftime("%Y-%m-%d %H:%M:%S"),
                         "End (local)":end.strftime("%Y-%m-%d %H:%M:%S"),"Duration (years)":round(y2,6)})
            cur=end; yog_i=(yog_i+1)%8
        return pd.DataFrame(rows)

    yogini_df = build_yogini(local_dt, cycles=3)

    # ---------------------------------
    # Pañcāṅga bits: Tithi/Nakṣatra/Yoga/Karaṇa + Hora
    # ---------------------------------
    TITHI_NAMES = ["Pratipada","Dvitiya","Tritiya","Chaturthi","Panchami","Shashthi","Saptami","Ashtami","Navami","Dashami","Ekadashi","Dvadashi","Trayodashi","Chaturdashi","Purnima",
                   "Pratipada","Dvitiya","Tritiya","Chaturthi","Panchami","Shashthi","Saptami","Ashtami","Navami","Dashami","Ekadashi","Dvadashi","Trayodashi","Chaturdashi","Amavasya"]
    
    def tithi_yoga_karana(jd_ut_):
        sun = norm360(swe.calc_ut(jd_ut_, swe.SUN, FLAGS)[0][0])
        moon = norm360(swe.calc_ut(jd_ut_, swe.MOON, FLAGS)[0][0])
        diff = norm360(moon - sun)
        
        # Tithi with percentage left
        tithi_num = int(diff // 12) + 1  # 1..30
        tithi_progress = (diff % 12) / 12.0
        tithi_pct_left = round((1.0 - tithi_progress) * 100, 2)
        
        tname = TITHI_NAMES[tithi_num-1]
        paksha = "Shukla" if tithi_num <= 15 else "Krishna"
        if tithi_num == 15: tithi_disp = "Purnima"
        elif tithi_num == 30: tithi_disp = "Amavasya"
        else: tithi_disp = tname
        
        # Nakshatra with percentage left
        nak_span = 360.0 / 27.0
        nak_idx = int(moon // nak_span)
        nak_progress = (moon % nak_span) / nak_span
        nak_pct_left = round((1.0 - nak_progress) * 100, 2)
        nak = NAK_NAMES[nak_idx]
        
        # Yoga with percentage left
        yoga_sum = norm360(moon + sun)
        yoga_span = 360.0 / 27.0
        yoga_idx = int(yoga_sum // yoga_span)
        yoga_progress = (yoga_sum % yoga_span) / yoga_span
        yoga_pct_left = round((1.0 - yoga_progress) * 100, 2)
        yoga = YOGA_NAMES[yoga_idx]
        
        # Karana with percentage left
        half_idx = int(diff // 6)  # 60 half-tithis
        karana_progress = (diff % 6) / 6.0
        karana_pct_left = round((1.0 - karana_progress) * 100, 2)
        if half_idx == 0: kar = KARANA_FIXED[0]
        elif half_idx >= 57: kar = KARANA_FIXED[half_idx-56]
        else: kar = KARANA_MOV[(half_idx-1) % 7]
        
        return dict(
            tithi=tithi_disp,
            tithi_num=tithi_num,
            tithi_pct_left=tithi_pct_left,
            paksha=paksha,
            nakshatra=nak,
            nak_pct_left=nak_pct_left,
            yoga=yoga,
            yoga_pct_left=yoga_pct_left,
            karana=kar,
            karana_pct_left=karana_pct_left
        )

    p = tithi_yoga_karana(jd_ut)



    # ---------------------------------
    # Lunar Month (Maasa) Calculation
    # ---------------------------------
    def calculate_maasa(jd_curr):
        # Use Sidereal Lahiri for Maasa
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        FlagsSid = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
        
        # 1. Find Prev New Moon
        sun = swe.calc_ut(jd_curr, swe.SUN, FlagsSid)[0][0]
        moon = swe.calc_ut(jd_curr, swe.MOON, FlagsSid)[0][0]
        phase = (moon - sun) % 360
        
        # Binary search for phase=0 (New Moon)
        t = jd_curr - (phase / 12.19) - 0.5 # start slightly before
        for _ in range(6):
            s = swe.calc_ut(t, swe.SUN, FlagsSid)[0][0]
            m = swe.calc_ut(t, swe.MOON, FlagsSid)[0][0]
            ph = (m - s) % 360
            if ph > 180: ph -= 360
            t -= ph / 12.19
        prev_nm = t
        
        # 2. Find Next New Moon
        t = jd_curr + (29.5 - (phase / 12.19))
        for _ in range(6):
            s = swe.calc_ut(t, swe.SUN, FlagsSid)[0][0]
            m = swe.calc_ut(t, swe.MOON, FlagsSid)[0][0]
            ph = (m - s) % 360
            if ph > 180: ph -= 360
            t -= ph / 12.19
        next_nm = t
        
        # 3. Check Solar Ingresses (Sidereal)
        s1 = swe.calc_ut(prev_nm, swe.SUN, FlagsSid)[0][0]
        s2 = swe.calc_ut(next_nm, swe.SUN, FlagsSid)[0][0]
        
        # Count boundaries crossed (30 deg)
        # Handle wrap around 360
        if s2 < s1: s2_adj = s2 + 360
        else: s2_adj = s2
        
        c1 = int(s1 // 30)
        c2 = int(s2_adj // 30)
        ingresses = c2 - c1
        
        s1_sign = int(s1 // 30) % 12
        
        status = "Nija"
        maasa_key = s1_sign
        
        if ingresses == 0:
            status = "Adhika"
            # Named after current sign (which is same as next ingress generally)
            # Standard rule: Adhika SunSign -> Adhika Maasa of that sign
            maasa_key = s1_sign
        elif ingresses == 1:
            status = "Nija"
            maasa_key = s1_sign
        elif ingresses >= 2:
            status = "Kshaya"
            maasa_key = s1_sign
            
        name_sans, name_tam = MAASA_MAP.get(maasa_key, ("Unknown", "Unknown"))
        
        if status == "Adhika":
            name_sans = f"Adhika {name_sans}"
            name_tam = f"Adhika {name_tam}"
        elif status == "Kshaya":
            name_sans = f"Kshaya {name_sans}"
            name_tam = f"Kshaya {name_tam}"
            
        return {
            "maasa_sanskrit": name_sans,
            "maasa_tamil": name_tam,
            "maasa_status": status,
            "maasa_ingresses": ingresses
        }
        
    maasa_info = calculate_maasa(jd_ut)
    p.update(maasa_info)

    
    # Janma Ghatis (time from sunrise in ghatis, 1 ghati = 24 minutes)
    if sunrise_local <= local_dt < sunrise_next_local:
        since_sunrise = (local_dt - sunrise_local).total_seconds()
    elif local_dt < sunrise_local:
        since_sunrise = (local_dt - sunrise_prev_local).total_seconds()
    else:
        since_sunrise = (local_dt - sunrise_next_local).total_seconds()
    janma_ghatis = round(since_sunrise / (24 * 60), 4)  # 1 ghati = 24 minutes = 1440 seconds

    # Hora — 24 seasonal horas between [sunrise → next sunrise); Hora0 = weekday lord
    def weekday_lord_from_pyweekday(py_weekday: int) -> str:
        # Python weekday: Mon=0..Sun=6
        return ["Moon","Mars","Mercury","Jupiter","Venus","Saturn","Sun"][py_weekday]

    def hora_lord_at_birth_seasonal_24(dt_local) -> str:
        if sunrise_local <= dt_local < sunrise_next_local:
            last_sr, next_sr = sunrise_local, sunrise_next_local
        elif dt_local < sunrise_local:
            last_sr, next_sr = sunrise_prev_local, sunrise_local
        else:
            last_sr = sunrise_next_local
            # compute the sunrise 2 days ahead (rare path when after next sunrise)
            next_sr = _sunrise_for_local_date(birth_date_local + timedelta(days=2), lat, lon, SITE_ELEVATION_M, SUNRISE_DEFINITION)

        span_sec = (next_sr - last_sr).total_seconds()
        hora_len = span_sec / 24.0
        idx = int(min(23, max(0, (dt_local - last_sr).total_seconds() // hora_len)))

        start_planet = weekday_lord_from_pyweekday(last_sr.weekday())
        start_idx = CHALDEAN.index(start_planet)
        return CHALDEAN[(start_idx + idx) % 7]

    hora_lord = hora_lord_at_birth_seasonal_24(local_dt)
    vara_name = VARA_SA_MON_FIRST[sunrise_local.weekday()]

    # Vedic weekday name (Sanskrit)
    VEDIC_WEEKDAYS = ["Somavara (Monday)", "Mangalavara (Tuesday)", "Budhavara (Wednesday)", 
                      "Guruvara (Thursday)", "Shukravara (Friday)", "Shanivara (Saturday)", "Ravivara (Sunday)"]
    
    panchanga_df = pd.DataFrame([{
        "Sunrise (local)": fmt_dt(sunrise_local),
        "Sunset (local)": fmt_dt(sunset_local),
        "Next Sunrise":    fmt_dt(sunrise_next_local),
        "Vara (weekday)":  vara_name,
        "Vedic Weekday": VEDIC_WEEKDAYS[sunrise_local.weekday()],
        "Maasa": p.get('maasa_sanskrit', '—'),
        "Maasa_Tamil": p.get('maasa_tamil', '—'),
        "Maasa_Status": p.get('maasa_status', 'Nija'),
        "Tithi":           p['tithi'],
        "Tithi_Num":       p['tithi_num'],
        "Tithi_Pct_Left":  p['tithi_pct_left'],
        "Paksha":          p['paksha'],
        "Nakshatra":       p['nakshatra'],
        "Nak_Pct_Left":    p['nak_pct_left'],
        "Yoga":            p['yoga'],
        "Yoga_Pct_Left":   p['yoga_pct_left'],
        "Karana":          p['karana'],
        "Karana_Pct_Left": p['karana_pct_left'],
        "Hora":            hora_lord,
        "Janma_Ghatis":    janma_ghatis,
        "Ayanamsa":        round(ayan, 6),
        "Sidereal_Time":   round(jd_ut % 1 * 24, 4)  # Approximate sidereal time hours
    }])

    # ---------------------------------
    # Śaḍbala (compact implementation)
    # ---------------------------------
    def lon_deg(sign_name, deg): return SIGN_INDEX[sign_name]*30.0 + deg

    def uccha_bala(lon_, graha):
        # Classical: distance from deep debility; if > 180, use 360 - dist; divide by 3 = Virupas
        if graha not in DEBIL: return 0.0
        deb_sign, deb_deg = DEBIL[graha]; deb = lon_deg(deb_sign, deb_deg)
        dist = min(abs(norm360(lon_-deb)), 360-abs(norm360(lon_-deb)))
        dist = dist if dist <= 180.0 else 360.0 - dist
        return max(0.0, dist / 3.0)

    MALE={"Sun","Mars","Jupiter","Saturn"}; FEMALE={"Moon","Venus"}

    def oja_yugma_bala(lon_, graha):
        # Even/odd sign and Navamsa: Venus/Moon gain in even, others in odd, 15 virupas each
        sidx = lon_to_sign_idx(lon_)
        even = (sidx % 2 == 1)  # sign 1-based even -> index odd
        sig_gain = 15.0 if ((graha in FEMALE and even) or (graha not in FEMALE and not even)) else 0.0
        nsign,_ = navamsa_for(lon_); neven = (nsign % 2 == 1)
        nav_gain = 15.0 if ((graha in FEMALE and neven) or (graha not in FEMALE and not neven)) else 0.0
        if graha == "Mercury":
            return 15.0  # hermaphrodite fixed per text
        return sig_gain + nav_gain

    def kendradi_bala(lon_):
        def _contains(start, end, x):
            start = norm360(start); end = norm360(end); x = norm360(x)
            return (start <= end and start <= x < end) or (start > end and (x >= start or x < end))
        h=12
        for i in range(12):
            if _contains(starts[i], ends[i], lon_): h=i+1; break
        return 60.0 if h in (1,4,7,10) else (30.0 if h in (2,5,8,11) else 15.0)

    def drekkana_bala(lon_, graha):
        # Male gets 15 in 1st drekkana, female in 2nd, Mercury in 3rd
        intra = lon_ - 30*lon_to_sign_idx(lon_)
        drek = int(intra//10) + 1
        if graha in MALE:
            return 15.0 if drek == 1 else 0.0
        if graha in FEMALE:
            return 15.0 if drek == 2 else 0.0
        return 15.0 if drek == 3 else 0.0

    def in_moolatrikona(graha, lon_):
        if graha not in MOOLATR: return False
        s,a,b=MOOLATR[graha]; si=SIGN_INDEX[s]; deg=norm360(lon_)-si*30.0
        if deg<0: deg+=360
        return 0<=deg<30 and (a<=deg<=b)

    SV_WEIGHTS = {"moolatrikona":45.0,"own":30.0,"great_friend":20.0,"friend":15.0,"neutral":10.0,"enemy":4.0,"great_enemy":2.0}

    def relation_to_lord(graha, lord):
        if lord in PERM_FRIENDS[graha] and graha in PERM_FRIENDS.get(lord,set()): return "great_friend"
        if lord in PERM_ENEMIES[graha] and graha in PERM_ENEMIES.get(lord,set()): return "great_enemy"
        if lord in PERM_FRIENDS[graha] or graha in PERM_FRIENDS.get(lord,set()): return "friend"
        if lord in PERM_ENEMIES[graha] or graha in PERM_ENEMIES.get(lord,set()): return "enemy"
        return "neutral"

    def varga_sign_D1(lon_): return lon_to_sign_idx(lon_)
    def varga_sign_D2(lon_):
        si=lon_to_sign_idx(lon_); intra=lon_-30*si; odd=(si%2==0)
        return 4 if (odd and intra<15) or ((not odd) and intra>=15) else 3
    def varga_sign_D3(lon_):
        si=lon_to_sign_idx(lon_); intra=lon_-30*si; return (si + int(intra//10))%12
    def varga_sign_D7(lon_):
        si=lon_to_sign_idx(lon_); intra=lon_-30*si; start=si if (si%2==0) else (si+6)%12
        return (start + int(intra//(30/7)))%12
    def varga_sign_D9(lon_): return navamsa_for(lon_)[0]
    def varga_sign_D12(lon_):
        si=lon_to_sign_idx(lon_); intra=lon_-30*si; return (si + int(intra//(30/12)))%12
    def varga_sign_D30(lon_):
        si=lon_to_sign_idx(lon_); intra=lon_-30*si; odd=(si%2==0)
        if odd:
            lord="Mars" if intra<5 else ("Saturn" if intra<10 else ("Jupiter" if intra<18 else ("Mercury" if intra<25 else "Venus")))
        else:
            lord="Venus" if intra<5 else ("Mercury" if intra<12 else ("Jupiter" if intra<20 else ("Saturn" if intra<25 else "Mars")))
        lord_to_sign={"Sun":4,"Moon":3,"Mars":0,"Mercury":2,"Jupiter":8,"Venus":1,"Saturn":10}
        return lord_to_sign[lord]

    def saptavargaja_bala(lon_, graha):
        v_funcs=[varga_sign_D1,varga_sign_D2,varga_sign_D3,varga_sign_D7,varga_sign_D9,varga_sign_D12,varga_sign_D30]
        total=0.0
        for vf in v_funcs:
            vs=vf(lon_); lord=SIGN_LORD[vs]
            if graha in EXALT and SIGN_INDEX[EXALT[graha][0]]==vs: total+=SV_WEIGHTS["own"]+15.0; continue
            if graha in DEBIL and SIGN_INDEX[DEBIL[graha][0]]==vs: total+=SV_WEIGHTS["enemy"]/2; continue
            if in_moolatrikona(graha, vs*30.0+1e-6): total+=SV_WEIGHTS["moolatrikona"]; continue
            total+= SV_WEIGHTS["own"] if lord==graha else SV_WEIGHTS[relation_to_lord(graha,lord)]
        return min(total,225.0)

    def angle_from_asc(lon_): return norm360(lon_ - asc_sid)
    def dig_bala(lon_, graha):
        # Classical: compute distance from reference house; divide by 3
        if graha in {"Sun","Mars"}:
            ref = norm360(asc_sid - 90.0)  # 4th house
        elif graha in {"Jupiter","Mercury"}:
            ref = norm360(asc_sid + 180.0)  # 7th
        elif graha in {"Venus","Moon"}:
            ref = norm360(asc_sid + 90.0)   # 10th
        else:  # Saturn
            ref = asc_sid                  # 1st
        delta = min(abs(norm360(lon_-ref)), 360-abs(norm360(lon_-ref)))
        return max(0.0, delta/3.0 if delta<=180 else (360-delta)/3.0)

    def nathonnatha_bala(graha, speed):
        """
        Ghati-based Natha/Unnatha:
        Unnata = ghatis from midnight to birth; Nata = 30 - Unnata.
        Moon/Mars/Saturn: Natha bala = 2 * Nata (in ghatis) => virupas.
        Sun/Jupiter/Venus: Unnatha bala = 60 - Natha bala.
        Mercury: full 60.
        Retro still capped to 60 as classical max.
        """
        try:
            # ghatis from local midnight
            ghatis = ((local_dt.hour * 60 + local_dt.minute + local_dt.second / 60.0) / 60.0) * 2.5
            ghatis = max(0.0, min(30.0, ghatis))
            nata = 30.0 - ghatis
        except Exception:
            ghatis = 15.0
            nata = 15.0
        if graha == "Mercury":
            return 60.0
        if speed < 0:
            return 60.0  # retrograde max
        natha_bala = max(0.0, min(60.0, 2.0 * nata))
        if graha in {"Moon", "Mars", "Saturn"}:
            return natha_bala
        if graha in {"Sun", "Jupiter", "Venus"}:
            return max(0.0, 60.0 - natha_bala)
        return natha_bala

    def paksha_bala(graha, moon_lon):
        sun_lon=numeric_lons["Sun"]; elong=norm360(moon_lon - sun_lon)
        diff = elong if elong<=180 else 360-elong
        virupa = diff/3.0
        if graha in {"Jupiter","Venus","Mercury","Moon"}:
            return virupa
        elif graha in {"Sun","Mars","Saturn"}:
            return max(0.0, 60.0 - virupa)
        else:
            return 30.0

    def tribhaga_bala(graha):
        try:
            if sunrise_local <= local_dt < sunrise_next_local:
                seg=(local_dt - sunrise_local).total_seconds()/(sunrise_next_local - sunrise_local).total_seconds()
                day=True
            else:
                seg=(local_dt - sunrise_prev_local).total_seconds()/(sunrise_local - sunrise_prev_local).total_seconds()
                day=False
        except Exception:
            return 0.0
        if graha=="Jupiter":
            return 60.0
        if day:
            if seg < 1/3:   return 60.0 if graha=="Mercury" else 0.0
            if seg < 2/3:   return 60.0 if graha=="Sun" else 0.0
            return 60.0 if graha=="Saturn" else 0.0
        else:
            if seg < 1/3:   return 60.0 if graha=="Moon" else 0.0
            if seg < 2/3:   return 60.0 if graha=="Venus" else 0.0
            return 60.0 if graha=="Mars" else 0.0

    def abda_bala(graha):
        """
        Varsha lord: take weekday lord of birth sunrise.
        Classical assigns 15 Virupa to the Varsha lord.
        """
        varsha_lord = ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"][sunrise_local.weekday()]
        return 15.0 if graha==varsha_lord else 0.0

    def maasa_bala(graha):
        """
        Maasa lord: lord of the Sun sign.
        Classical assigns 30 Virupa to that lord.
        """
        sun_sign=lon_to_sign_idx(numeric_lons["Sun"]); lord=SIGN_LORD[sun_sign]
        return 30.0 if graha==lord else 0.0

    def vara_bala(graha):
        """
        Dina/vara lord: weekday lord at birth.
        45 Virupa to day lord.
        """
        day_lord = ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"][sunrise_local.weekday()]
        return 45.0 if graha==day_lord else 0.0

    def hora_bala(graha):
        """
        Hora lord at birth: full 60 Virupa to hora lord.
        """
        return 60.0 if graha==hora_lord else 0.0

    KHANDA_RASI = {
        "movable":45.0, "fixed":33.0, "dual":12.0
    }
    def ayana_bala(graha):
        """Ayana Bala using khanda method (approximate)."""
        if graha == "Mercury":
            return 60.0
        try:
            lon_sid = numeric_lons[graha]
            lon_trop = norm360(lon_sid + ayan)  # tropical position
            lon_mod = lon_trop % 180.0
            bhuja = lon_mod if lon_mod <= 90.0 else 180.0 - lon_mod
            bhuja_rasi_idx = int(lon_trop // 30) % 12
            # khanda for bhuja rasi
            if bhuja_rasi_idx in {0,3,6,9}:  # movable
                base = KHANDA_RASI["movable"]; other=[KHANDA_RASI["fixed"], KHANDA_RASI["dual"]]
            elif bhuja_rasi_idx in {1,4,7,10}:  # fixed
                base = KHANDA_RASI["fixed"]; other=[KHANDA_RASI["movable"], KHANDA_RASI["dual"]]
            else:  # dual
                base = KHANDA_RASI["dual"]; other=[KHANDA_RASI["movable"], KHANDA_RASI["fixed"]]
            add_deg = (bhuja % 30.0) * max(other) / 30.0
            total = base + add_deg
            # Hemisphere adjustment
            if graha in {"Moon","Saturn"} and bhuja_rasi_idx in {6,7,8,9,10,11}:  # Libra to Pisces
                total += 90.0
            if graha in {"Sun","Mars","Venus","Jupiter"} and bhuja_rasi_idx in {0,1,2,3,4,5}:  # Aries to Virgo
                total += 90.0
            return max(0.0, total/3.0)
        except Exception:
            return 0.0

    def yuddha_bala(graha):
        contenders=["Mars","Mercury","Jupiter","Venus","Saturn"]; my=numeric_lons[graha]; sc=0.0
        if graha in contenders:
            for o in contenders:
                if o==graha: continue
                if min(abs(my-numeric_lons[o]), 360-abs(my-numeric_lons[o])) < 1.0: sc+=15.0
        return sc

    def cheshta_bala(graha):
        """
        Cheshta Bala using seeghra/manda kendra + speed:
        - Retrograde => Vakra (60); forward-after-retro => Anuvakra (30).
        - Stationary slow => Vikala (15).
        - Uses elongation from Sun (seeghra kendra) to refine inner vs outer behavior.
        - Manda kendra proxy: deviation of true vs mean longitude (via speed ratio) modulates states.
        """
        spd = swe.calc_ut(jd_ut, getattr(swe, graha.upper()), FLAGS)[0][3]
        try:
            spd_prev = swe.calc_ut(jd_ut-1, getattr(swe, graha.upper()), FLAGS)[0][3]
        except Exception:
            spd_prev = spd
        if graha in {"Sun","Moon"}:
            return paksha_bala(graha, numeric_lons["Moon"])
        if graha not in {"Mars","Mercury","Jupiter","Venus","Saturn"}:
            return 0.0
        mean_speeds={"Mars":0.524,"Mercury":1.2,"Jupiter":0.0831,"Venus":1.2,"Saturn":0.0335}
        mean = mean_speeds.get(graha, abs(spd) if abs(spd)>0 else 1.0)
        ratio = abs(spd) / mean if mean else 0.0
        sun_lon = numeric_lons["Sun"]
        glon = numeric_lons[graha]
        seeghra = min(abs(norm360(glon - sun_lon)), 360-abs(norm360(glon - sun_lon)))
        manda_kendra = abs(ratio-1.0)  # proxy: deviation from mean speed
        if spd < 0:
            return 60.0  # Vakra
        if spd >= 0 and spd_prev < 0:
            return 30.0  # Anuvakra (entering forward from retro)
        if ratio < 0.05:
            return 15.0  # Vikala
        # Outer planets are fastest near opposition; inner are fastest near conjunction elongations
        is_inner = graha in {"Mercury","Venus"}
        if not is_inner and 150 <= seeghra <= 210 and ratio >= 1.0:
            return 45.0  # Chara near opposition
        if is_inner and seeghra <= 30 and ratio >= 1.0:
            return 45.0  # Chara near conjunction elongation
        if ratio < 0.6 or manda_kendra > 0.5:
            return 30.0  # Manda
        if ratio < 0.9:
            return 15.0  # Mandatara
        if ratio < 1.1:
            return 7.5   # Sama
        if ratio < 1.4:
            return 45.0  # Chara (default fast)
        return 30.0      # Atichara default

    def aspect_score(src_lon, tgt_lon, src_graha, orb=12.0):
        ang=norm360(tgt_lon - src_lon)
        def near(a):
            d=min(abs(norm360(ang-a)), 360-abs(norm360(ang-a)))
            return max(0.0, 1.0 - d/orb)
        allowed={0,180}
        if src_graha=="Jupiter": allowed|={120,240}
        if src_graha=="Mars":    allowed|={90,270}
        if src_graha=="Saturn":  allowed|={60,300}
        return max(near(a) for a in allowed)

    def drig_bala(graha, lon_, all_lons):
        """
        Drig Bala with explicit drishti pindas and planet strength + dignity mod:
        - Aspect sets per classical: Jupiter (5/7/9), Mars (4/7/8), Saturn (3/7/10), others (7).
        - Base pinda per graha for full aspect (classical: benefics stronger, Saturn/Mars lower, Sun weakest).
        - Benefic add 1/4 pinda, malefic subtract 1/4; Jupiter/Mercury superadd full pinda.
        - Modulate aspect pinda by aspecting planet dignity (exalt/own/friend/enemy/debil).
        """
        aspect_map = {
            "Jupiter":[120,180,240],
            "Mars":[90,180,270],
            "Saturn":[60,180,300],
        }
        pinda_base = {"Sun":30.0,"Moon":60.0,"Mars":45.0,"Mercury":60.0,"Jupiter":60.0,"Venus":60.0,"Saturn":45.0}
        def dignity_factor(planet, lon_planet):
            # Exalt > own > friend > neutral > enemy > debil
            if planet in EXALT and lon_to_sign_idx(lon_planet) == SIGN_INDEX[EXALT[planet][0]]:
                return 1.15
            if planet in DEBIL and lon_to_sign_idx(lon_planet) == SIGN_INDEX[DEBIL[planet][0]]:
                return 0.85
            lord = SIGN_LORD[lon_to_sign_idx(lon_planet)]
            rel = relation_to_lord(planet, lord)
            if rel == "moolatrikona" or in_moolatrikona(planet, lon_planet):
                return 1.1
            if rel == "great_friend":
                return 1.08
            if rel == "friend":
                return 1.05
            if rel == "neutral":
                return 1.0
            if rel == "enemy":
                return 0.95
            if rel == "great_enemy":
                return 0.90
            return 1.0
        total=0.0
        for other,olon in all_lons.items():
            if other not in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"] or other==graha:
                continue
            angles = aspect_map.get(other, [180])
            s = max(0.0, max(1.0 - min(abs(norm360(lon_-olon - a)), 360-abs(norm360(lon_-olon - a)))/12.0 for a in angles))
            if s<=0:
                continue
            pinda = pinda_base.get(other,60.0) * s * dignity_factor(other, olon)
            if other in BENEFICS:
                total += pinda/4.0
            if other in MALEFICS:
                total -= pinda/4.0
            if other in {"Jupiter","Mercury"}:
                total += pinda
        return max(-240.0, min(240.0, total))

    sb_rows=[]
    sb_sthana=[]
    sb_kala=[]
    sb_bhava=[]
    base_totals={}
    for g in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]:
        glon=numeric_lons[g]
        # Sthana components
        uc = float(uccha_bala(glon,g))
        sv = float(saptavargaja_bala(glon,g))
        oy = float(oja_yugma_bala(glon,g))
        ken = float(kendradi_bala(glon))
        dre = float(drekkana_bala(glon,g))
        sth = uc + sv + oy + ken + dre

        sb_sthana.append({
            "Planet": g,
            "Uccha": round(uc,2),
            "Saptavargaja": round(sv,2),
            "Oja/Yugma": round(oy,2),
            "Kendradi": round(ken,2),
            "Drekkana": round(dre,2),
            "Total (Virupa)": round(sth,2),
            "Total (Rupa)": round(sth/60.0,3)
        })

        nai=float(NAISARGIKA[g])
        dig=float(dig_bala(glon,g))
        # Kala components
        natha = float(nathonnatha_bala(g, swe.calc_ut(jd_ut, getattr(swe, g.upper()), FLAGS)[0][3]))
        pak   = float(paksha_bala(g, numeric_lons["Moon"]))
        tri   = float(tribhaga_bala(g))
        abd   = float(abda_bala(g))
        maa   = float(maasa_bala(g))
        var   = float(vara_bala(g))
        hor   = float(hora_bala(g))
        aya   = float(ayana_bala(g))
        yud   = float(yuddha_bala(g))
        kal = natha + pak + tri + abd + maa + var + hor + aya + yud

        sb_kala.append({
            "Planet": g,
            "Nathonnatha/Cheshta": round(natha,2),
            "Paksha": round(pak,2),
            "Tribhaga": round(tri,2),
            "Abda": round(abd,2),
            "Maasa": round(maa,2),
            "Vara": round(var,2),
            "Hora": round(hor,2),
            "Ayana": round(aya,2),
            "Yuddha": round(yud,2),
            "Total (Virupa)": round(kal,2),
            "Total (Rupa)": round(kal/60.0,3)
        })

        che=float(cheshta_bala(g))
        dri=float(drig_bala(g, glon, numeric_lons))
        total_v=sth+dig+kal+che+nai+dri
        base_totals[g]=total_v
        total_r=total_v/60.0
        total_pct = max(0.0, min(100.0, (total_r / MAX_SHADBALA_RUPA.get(g, total_r)) * 100.0 if g in MAX_SHADBALA_RUPA else (total_r/6.0)*100.0))
        sb_rows.append({"Planet":g,"Sthana":round(sth,2),"Dig":round(dig,2),"Kala":round(kal,2),
                        "Cheshta":round(che,2),"Naisargika":round(nai,2),"Drig":round(dri,2),
                        "Total (Virupa)":round(total_v,2),"Total (Rupa)":round(total_r,3),
                        "Total (%)":round(total_pct,1),
                        "Min Req (Rupa)":MIN_SHADBALA_RUPA[g],"Meets Min?":"Yes" if total_r>=MIN_SHADBALA_RUPA[g] else "No"})

    def war_victor(p1, p2):
        """Pick victor by brightness (magnitude); fallback to higher base total."""
        try:
            mag1 = swe.pheno_ut(jd_ut, getattr(swe, p1.upper()))[3]
            mag2 = swe.pheno_ut(jd_ut, getattr(swe, p2.upper()))[3]
            if mag1 < mag2:
                return p1
            if mag2 < mag1:
                return p2
        except Exception:
            pass
        return p1 if base_totals.get(p1,0) >= base_totals.get(p2,0) else p2

    # Apply war adjustment: pairs among Mars, Mercury, Jupiter, Venus, Saturn within 1°
    contenders=["Mars","Mercury","Jupiter","Venus","Saturn"]
    war_adjust={g:0.0 for g in contenders}
    for i,p1 in enumerate(contenders):
        for p2 in contenders[i+1:]:
            dist=min(abs(numeric_lons[p1]-numeric_lons[p2]), 360-abs(numeric_lons[p1]-numeric_lons[p2]))
            if dist < 1.0:
                victor = war_victor(p1,p2)
                loser = p2 if victor==p1 else p1
                diff=abs(base_totals.get(p1,0)-base_totals.get(p2,0))
                war_adjust[victor]+=diff
                war_adjust[loser]-=diff

    if any(abs(v)>0 for v in war_adjust.values()):
        for row in sb_rows:
            p=row["Planet"]
            if p in war_adjust:
                row["Total (Virupa)"]=round(row["Total (Virupa)"]+war_adjust[p],2)
                row["Total (Rupa)"]=round(row["Total (Virupa)"]/60.0,3)
                row["Meets Min?"]="Yes" if row["Total (Rupa)"]>=MIN_SHADBALA_RUPA[p] else "No"

    # Map planet total Rupa for Bhava lord contribution
    planet_total_rupa = {r["Planet"]: r["Total (Rupa)"] for r in sb_rows}

    # Bhava Bala (simplified per classical cues)
    desc = norm360(asc_sid + 180.0)
    nadir = norm360(asc_sid - 90.0)
    midh = norm360(asc_sid + 90.0)

    def bhava_ref(cusp_lon):
        si = lon_to_sign_idx(cusp_lon)
        intra = cusp_lon - si*30.0
        # Gemini, Virgo, Libra, Aquarius, first half Sagittarius -> subtract 7th
        if si in {2,5,6,10} or (si==8 and intra<15.0):
            return desc
        # Aries, Taurus, Leo, first half Capricorn, second half Sagittarius -> subtract 4th
        if si in {0,1,4} or (si==9 and intra<15.0) or (si==8 and intra>=15.0):
            return nadir
        # Cancer or Scorpio -> subtract Asc
        if si in {3,7}:
            return asc_sid
        # Capricorn second half or Pisces -> subtract 10th
        if (si==9 and intra>=15.0) or si==11:
            return midh
        return asc_sid

    BENEFICS_SET={"Jupiter","Venus","Mercury","Moon"}
    MALEFICS_SET={"Saturn","Mars","Sun"}

    for i in range(12):
        cusp_sign_idx = lon_to_sign_idx(cusps_sid[i])
        ref = bhava_ref(cusps_sid[i])
        diff = abs(norm360(cusps_sid[i]-ref))
        if diff>180: diff = 360 - diff
        virupa = diff/3.0
        # Aspect adjustments
        for p, lonp in numeric_lons.items():
            if p not in {"Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"}:
                continue
            s=aspect_score(lonp, cusps_sid[i], p, orb=12.0)
            if s<=0:
                continue
            pinda = 60.0 * s
            if p in BENEFICS_SET:
                virupa += pinda/4.0
            if p in MALEFICS_SET:
                virupa -= pinda/4.0
            if p in {"Jupiter","Mercury"}:
                virupa += pinda
        # Lord contribution (Rupa -> Virupa)
        lord = SIGN_LORD[cusp_sign_idx]
        # Lord strength contribution (scaled to keep Bhava Bala in a readable range)
        virupa += planet_total_rupa.get(lord,0.0) * 60.0 * 0.25
        # Occupant adjustments
        occs = house_occ[i+1]
        if any(o in occs for o in ["Jupiter","Mercury"]):
            virupa += 60.0
        if any(o in occs for o in ["Saturn","Mars","Sun"]):
            virupa -= 60.0
        # Day/night bonus
        is_day = False
        try:
            is_day = sunrise_local <= local_dt < sunset_local
        except Exception:
            pass
        seershodaya = cusp_sign_idx in {2,4,5,6,10}  # Ge, Le, Vi, Li, Aq
        prishtodaya = cusp_sign_idx in {0,1,3,7,9}  # Ar, Ta, Cn, Sc, Cp
        dual = cusp_sign_idx in {2,5,8,11}  # Ge, Vi, Sg, Pi
        if is_day and seershodaya:
            virupa += 15.0
        elif (not is_day) and prishtodaya:
            virupa += 15.0
        # clamp
        virupa = max(0.0, virupa)
        bhava_rupa = virupa / 60.0
        sb_bhava.append({
            "Bhava": i+1,
            "Cusp": sign_dms_str(cusps_sid[i]),
            "Bhava Bala (Rupa)": round(bhava_rupa,3),
            "Strength (%)": round(bhava_rupa*100.0,1),
            "Lord": lord,
            "Lord Shadbala (Rupa)": round(planet_total_rupa.get(lord, 0.0),3),
            "Occupants": ", ".join(occs)
        })

    # Normalize bhava strengths to percent and add rank
    if sb_bhava:
        ranks_bh = {row["Bhava"]: rank for rank, row in enumerate(sorted(sb_bhava, key=lambda r: r["Bhava Bala (Rupa)"], reverse=True), start=1)}
        for row in sb_bhava:
            row["Rank"] = ranks_bh[row["Bhava"]]

    shadbala_df = pd.DataFrame(sb_rows)
    ranks = shadbala_df.set_index("Planet")["Total (Rupa)"].rank(method="dense", ascending=False).astype(int).to_dict()
    NATURAL_ORDER = ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]
    shadbala_df = shadbala_df.set_index("Planet").loc[NATURAL_ORDER].reset_index()
    shadbala_df["Rank"] = shadbala_df["Planet"].map(ranks)

    # ---------------------------------
    # Ishta / Kashta Phala (Rasmis-based)
    # ---------------------------------
    def rasmi_from_kendra(angle_deg: float) -> float:
        ang = norm360(angle_deg)
        if ang > 180.0:
            ang = 360.0 - ang
        signs = int(ang // 30.0)
        deg = ang - signs * 30.0
        signs += 1  # add 1 Rasi
        deg *= 2.0  # double degrees per classical rule
        signs += int(deg // 30.0)
        deg = deg % 30.0
        return signs + deg / 30.0

    def uchcha_rasmi_val(planet: str) -> float:
        if planet not in DEBIL or planet not in numeric_lons:
            return 0.0
        deb_sign, deb_deg = DEBIL[planet]
        deb_lon = lon_deg(deb_sign, deb_deg)
        return rasmi_from_kendra(numeric_lons[planet] - deb_lon)

    def chesta_kendra_angle(planet: str) -> float:
        if planet == "Sun":
            return 90.0  # 3 rasis from sayana Sun → 90°
        if planet not in numeric_lons or "Sun" not in numeric_lons:
            return 0.0
        return numeric_lons[planet] - numeric_lons["Sun"]

    def chesta_rasmi_val(planet: str) -> float:
        return rasmi_from_kendra(chesta_kendra_angle(planet))

    ishta_rows = []
    for g in NATURAL_ORDER:
        u_rasmi = uchcha_rasmi_val(g)
        c_rasmi = chesta_rasmi_val(g)
        subha = max(0.0, min(8.0, (u_rasmi + c_rasmi) / 2.0))
        asubha = max(0.0, 8.0 - subha)
        ishta = max(0.0, min(60.0, ((u_rasmi - 1.0) * 10.0 + (c_rasmi - 1.0) * 10.0) / 2.0))
        kashta = max(0.0, 60.0 - ishta)
        ishta_rows.append({
            "Planet": g,
            "Uchcha Rasmi": round(u_rasmi, 3),
            "Cheshta Rasmi": round(c_rasmi, 3),
            "Subha Rasmi": round(subha, 3),
            "Asubha Rasmi": round(asubha, 3),
            "Ishta Phala": round(ishta, 2),
            "Kashta Phala": round(kashta, 2)
        })

    # ---------------------------------
    # Varnada Daśā (Rāśi-based)
    # ---------------------------------
    def format_varnada_dt(dt_obj):
        try:
            return dt_obj.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return str(dt_obj)

    def sign_distance(start_idx, end_idx, direction_step):
        if direction_step == 1:
            return ((end_idx - start_idx + 12) % 12) + 1
        return ((start_idx - end_idx + 12) % 12) + 1

    direction_step = 1 if asc_sign_idx % 2 == 0 else -1  # odd sign -> clockwise (forward)
    direction_label = "Clockwise" if direction_step == 1 else "Anti-clockwise"

    asc_lord = SIGN_LORD.get(asc_sign_idx)
    hora_lord = SIGN_LORD.get(hora_sign_idx)
    asc_strength = planet_total_rupa.get(asc_lord, 0.0)
    hora_strength = planet_total_rupa.get(hora_lord, 0.0)
    start_sign_idx = asc_sign_idx if asc_strength >= hora_strength else hora_sign_idx

    if direction_step == 1:
        sign_sequence = [(start_sign_idx + i) % 12 for i in range(12)]
    else:
        sign_sequence = [(start_sign_idx - i) % 12 for i in range(12)]

    varnada_dasa_rows = []
    current_start = local_dt
    for sign_idx in sign_sequence:
        house_num = ((sign_idx - asc_sign_idx + 12) % 12) + 1
        varnada_idx = varnada_by_house.get(house_num, sign_idx)
        duration_years = sign_distance(sign_idx, varnada_idx, direction_step)
        end_time = current_start + timedelta(days=years_to_days(duration_years))
        varnada_dasa_rows.append({
            "House": house_num,
            "Dasha Rashi": RASHI_SA[sign_idx],
            "Varnada": RASHI_SA[varnada_idx],
            "Direction": direction_label,
            "Start (local)": format_varnada_dt(current_start),
            "End (local)": format_varnada_dt(end_time),
            "Duration (years)": round(duration_years, 6)
        })
        current_start = end_time

    varnada_dasa_df = pd.DataFrame(varnada_dasa_rows)

    # ---------------------------------
    # Additional Dasa Systems
    # ---------------------------------
    # Determine day/night/sandhya for Chakra dasa
    is_night = local_dt < sunrise_local or local_dt >= sunset_local
    is_sandhya = False  # Could be refined with Ghati calculations
    
    # Get lagna lord's rashi for Chakra dasa
    lagna_lord = SIGN_LORD.get(asc_sign_idx, "Sun")
    lagna_lord_lon = numeric_lons.get(lagna_lord, 0)
    lagna_lord_rashi_idx = lon_to_sign_idx(lagna_lord_lon)
    
    # Compute all dasa systems
    ashtottari_df = build_ashtottari(moon_lon, local_dt)
    shodshottari_df = build_shodshottari(moon_lon, local_dt)
    dwadashottari_df = build_dwadashottari(moon_lon, local_dt)
    panchottari_df = build_panchottari(moon_lon, local_dt)
    shatabdik_df = build_shatabdik(moon_lon, local_dt)
    chaturashiti_df = build_chaturashiti_sama(moon_lon, local_dt)
    dwisaptati_df = build_dwisaptati_sama(moon_lon, local_dt)
    shastihayani_df = build_shastihayani(moon_lon, local_dt)
    shattrimshat_df = build_shattrimshat_sama(moon_lon, local_dt)
    chakra_df = build_chakra(asc_sign_idx, lagna_lord_rashi_idx, local_dt, is_night, is_sandhya)
    
    # New Dasa Systems
    # We pass points now as they need full chart context
    points_list = points_df.to_dict('records') # Convert to list of dicts
    
    sthir_df = build_sthir_dasa(points_list, local_dt)
    yogardha_df = build_yogardha_dasa(points_list, local_dt)
    kendradi_lagn_df = build_kendradi_dasa(points_list, local_dt, variant="lagn")
    kendradi_ak_df = build_kendradi_dasa(points_list, local_dt, variant="ak")
    karak_df = build_karak_dasa(points_list, local_dt)
    manduk_df = build_manduk_dasa(points_list, local_dt)
    shula_df = build_shula_dasa(points_list, local_dt)
    trikon_df = build_trikon_dasa(points_list, local_dt)
    dirga_df = build_dirga_dasa(points_list, local_dt)
    panch_swar_df = build_panch_swar_dasa(points_list, local_dt, name_str=name)
    panch_swar_df = build_panch_swar_dasa(points_list, local_dt, name_str=name)
    kalachakra_df, kalachakra_total_years, kalachakra_remaining = build_kalachakra_dasa(points_list, local_dt)

    # ---------------------------------
    # Return everything
    # ---------------------------------
    return {
        "tzname": tzname,
        "local_dt": local_dt,
        "utc_dt": utc_dt,
        "jd_ut": jd_ut,
        "ayanamsa_name": ayanamsa_name,
        "ayanamsa_value": round(ayan, 6),
        "points": points_df,
        "houses": houses_df,
        "vimshottari_md": vim_md_df,
        "yogini": yogini_df,
        "varnada_dasa": varnada_dasa_df,
        "ashtottari": ashtottari_df,
        "shodshottari": shodshottari_df,
        "dwadashottari": dwadashottari_df,
        "panchottari": panchottari_df,
        "shatabdik": shatabdik_df,
        "chaturashiti_sama": chaturashiti_df,
        "dwisaptati_sama": dwisaptati_df,
        "shastihayani": shastihayani_df,
        "shattrimshat_sama": shattrimshat_df,
        "chakra": chakra_df,
        "shadbala": shadbala_df,
        "shadbala_sthana": pd.DataFrame(sb_sthana),
        "shadbala_kala": pd.DataFrame(sb_kala),
        "ishta_kashta": pd.DataFrame(ishta_rows),
        "bhava_bala": pd.DataFrame(sb_bhava),
        "aspect_grid": aspect_grid_df,
        "pushkara_table": pushkara_df,
        "panchanga": panchanga_df,
        "vargas": vargas_data,
        "sthir": sthir_df,
        "yogardha": yogardha_df,
        "kendradi_lagn": kendradi_lagn_df,
        "kendradi_ak": kendradi_ak_df,
        "karak": karak_df,
        "manduk": manduk_df,
        "shula": shula_df,
        "trikon": trikon_df,
        "dirga": dirga_df,
        "panch_swar": panch_swar_df,
        "kalachakra": kalachakra_df,
        "kalachakra_ayurdaya": kalachakra_total_years,
        "kalachakra_remaining": kalachakra_remaining,
    }

# Convenience wrapper when you already know the tz database name (e.g., from your places DB).
def compute_chart_with_tzname(y, m, d, hh, mm, ss, lat, lon, tzname,
                              ephe_path="ephe", use_moseph=False, house_sys=b'O',
                              ayanamsa: str = "Lahiri", name: str = None):
    return compute_chart(y, m, d, hh, mm, ss, lat, lon,
                         ephe_path=ephe_path, use_moseph=use_moseph, house_sys=house_sys,
                         tzname_override=tzname, ayanamsa=ayanamsa, name=name)


# ---------------------------------
# Ashtakavarga Calculation
# ---------------------------------
# Benefic points (bindus) contributed by each planet from various positions
# Format: {contributing_planet: {reference_body: [houses_from_reference_that_get_bindu]}}
# Houses are 1-based, so house 1 means same sign as reference

ASHTAKAVARGA_RULES = {
    "Sun": {
        "Sun": [1, 2, 4, 7, 8, 9, 10, 11],
        "Moon": [3, 6, 10, 11],
        "Mars": [1, 2, 4, 7, 8, 9, 10, 11],
        "Mercury": [3, 5, 6, 9, 10, 11, 12],
        "Jupiter": [5, 6, 9, 11],
        "Venus": [6, 7, 12],
        "Saturn": [1, 2, 4, 7, 8, 9, 10, 11],
        "Ascendant": [3, 4, 6, 10, 11, 12],
    },
    "Moon": {
        "Sun": [3, 6, 7, 8, 10, 11],
        "Moon": [1, 3, 6, 7, 10, 11],
        "Mars": [2, 3, 5, 6, 9, 10, 11],
        "Mercury": [1, 3, 4, 5, 7, 8, 10, 11],
        "Jupiter": [1, 4, 7, 8, 10, 11, 12],
        "Venus": [3, 4, 5, 7, 9, 10, 11],
        "Saturn": [3, 5, 6, 11],
        "Ascendant": [3, 6, 10, 11],
    },
    "Mars": {
        "Sun": [3, 5, 6, 10, 11],
        "Moon": [3, 6, 11],
        "Mars": [1, 2, 4, 7, 8, 10, 11],
        "Mercury": [3, 5, 6, 11],
        "Jupiter": [6, 10, 11, 12],
        "Venus": [6, 8, 11, 12],
        "Saturn": [1, 4, 7, 8, 9, 10, 11],
        "Ascendant": [1, 3, 6, 10, 11],
    },
    "Mercury": {
        "Sun": [5, 6, 9, 11, 12],
        "Moon": [2, 4, 6, 8, 10, 11],
        "Mars": [1, 2, 4, 7, 8, 9, 10, 11],
        "Mercury": [1, 3, 5, 6, 9, 10, 11, 12],
        "Jupiter": [6, 8, 11, 12],
        "Venus": [1, 2, 3, 4, 5, 8, 9, 11],
        "Saturn": [1, 2, 4, 7, 8, 9, 10, 11],
        "Ascendant": [1, 2, 4, 6, 8, 10, 11],
    },
    "Jupiter": {
        "Sun": [1, 2, 3, 4, 7, 8, 9, 10, 11],
        "Moon": [2, 5, 7, 9, 11],
        "Mars": [1, 2, 4, 7, 8, 10, 11],
        "Mercury": [1, 2, 4, 5, 6, 9, 10, 11],
        "Jupiter": [1, 2, 3, 4, 7, 8, 10, 11],
        "Venus": [2, 5, 6, 9, 10, 11],
        "Saturn": [3, 5, 6, 12],
        "Ascendant": [1, 2, 4, 5, 6, 7, 9, 10, 11],
    },
    "Venus": {
        "Sun": [8, 11, 12],
        "Moon": [1, 2, 3, 4, 5, 8, 9, 11, 12],
        "Mars": [3, 5, 6, 9, 11, 12],
        "Mercury": [3, 5, 6, 9, 11],
        "Jupiter": [5, 8, 9, 10, 11],
        "Venus": [1, 2, 3, 4, 5, 8, 9, 10, 11],
        "Saturn": [3, 4, 5, 8, 9, 10, 11],
        "Ascendant": [1, 2, 3, 4, 5, 8, 9, 11],
    },
    "Saturn": {
        "Sun": [1, 2, 4, 7, 8, 10, 11],
        "Moon": [3, 6, 11],
        "Mars": [3, 5, 6, 10, 11, 12],
        "Mercury": [6, 8, 9, 10, 11, 12],
        "Jupiter": [5, 6, 11, 12],
        "Venus": [6, 11, 12],
        "Saturn": [3, 5, 6, 11],
        "Ascendant": [1, 3, 4, 6, 10, 11],
    },
    "Ascendant": {
        "Sun": [3, 4, 6, 10, 11, 12],
        "Moon": [3, 6, 10, 11, 12],
        "Mars": [1, 3, 6, 10, 11],
        "Mercury": [1, 2, 4, 6, 8, 10, 11],
        "Jupiter": [1, 2, 4, 5, 6, 7, 9, 10, 11],
        "Venus": [1, 2, 3, 4, 5, 8, 9],
        "Saturn": [1, 3, 4, 6, 10, 11],
        "Ascendant": [3, 6, 10, 11],
    },
}


def compute_ashtakavarga(points_df):
    """
    Compute Bhinnashtakavarga (individual planet contributions) and Sarvashtakavarga (totals).
    
    Returns dict with:
    - bav: {planet: [12 bindu values for each sign 0-11]}
    - sav: [12 total bindu values for each sign 0-11]
    """
    # Get sign indices for all relevant bodies
    sign_positions = {}
    
    for _, row in points_df.iterrows():
        point = row['Point']
        sign_idx = row['Rashi_Idx']
        
        # Map point names to our standard names
        if point == "Ascendant (1st House Cusp)":
            sign_positions["Ascendant"] = sign_idx
        elif point in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
            sign_positions[point] = sign_idx
    
    # Initialize Bhinnashtakavarga for each planet
    bav = {planet: [0] * 12 for planet in ASHTAKAVARGA_RULES.keys()}
    
    # Calculate bindus for each planet
    for planet, rules in ASHTAKAVARGA_RULES.items():
        for ref_body, houses in rules.items():
            if ref_body not in sign_positions:
                continue
            ref_sign = sign_positions[ref_body]
            
            for house in houses:
                # House 1 = same sign as reference, house 2 = next sign, etc.
                target_sign = (ref_sign + house - 1) % 12
                bav[planet][target_sign] += 1
    
    # Calculate Sarvashtakavarga (sum of all BAVs)
    sav = [0] * 12
    for sign_idx in range(12):
        for planet in bav:
            sav[sign_idx] += bav[planet][sign_idx]
    
    return {
        "bav": bav,
        "sav": sav,
        "sign_positions": sign_positions
    }


def calculate_ashtakavarga_longevity(bav):
    """
    Calculate longevity based on Ashtakavarga rekhas.
    Mapping:
    0 rekhas = 2 days
    1 rekha  = 1.5 days
    2 rekhas = 1 day
    3 rekhas = 0.5 days
    4 rekhas = 7.5 days
    5 rekhas = 2 years
    6 rekhas = 4 years
    7 rekhas = 6 years
    8 rekhas = 8 years
    
    Longevity = (Sum of all spans) / 2
    """
    # Duration in days (using 365.25 for years)
    mapping = {
        0: 2.0,
        1: 1.5,
        2: 1.0,
        3: 0.5,
        4: 7.5,
        5: 2.0 * 365.25,
        6: 4.0 * 365.25,
        7: 6.0 * 365.25,
        8: 8.0 * 365.25
    }
    
    total_days = 0.0
    
    # Iterate through all Ashtakavargas (Lagna + 7 Grahas)
    # The bav dict contains keys for all planets in ASHTAKAVARGA_RULES
    for planet, rekhas in bav.items():
        for r_points in rekhas:
            # Ensure points are within 0-8 just in case, though they should be
            points = max(0, min(8, int(r_points)))
            if points in mapping:
                total_days += mapping[points]
            
    # "Half of the sum total of all will be the longevity"
    final_years = (total_days / 365.25) / 2.0
    
    return round(final_years, 2)


# ---------------------------------
# Transit Calculations
# ---------------------------------
def compute_transit_positions(transit_dt, lat, lon, tzname, ephe_path="ephe", use_moseph=False, ayanamsa="Lahiri"):
    """
    Compute current planetary positions for a given datetime (transit).
    Returns similar structure to natal chart points for overlay.
    """
    ayanamsa_code = get_ayanamsa_code(ayanamsa)
    FLAGS = init_ephe(ephe_path, use_moseph, sidereal_mode=ayanamsa_code)
    
    # Convert transit datetime to JD
    local_zone = tz.gettz(tzname)
    if isinstance(transit_dt, str):
        transit_dt = datetime.fromisoformat(transit_dt.replace('Z', '+00:00'))
    
    if transit_dt.tzinfo is None:
        transit_dt = transit_dt.replace(tzinfo=local_zone)
    
    dt_utc = transit_dt.astimezone(timezone.utc)
    ut_hour = dt_utc.hour + dt_utc.minute/60 + dt_utc.second/3600
    jd_ut = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, ut_hour, swe.GREG_CAL)
    
    # Get houses for transit ascendant
    cusps_trop, ascmc_trop = swe.houses(jd_ut, lat, lon, b'O')
    ayan = swe.get_ayanamsa_ut(jd_ut)
    asc_sid = norm360(ascmc_trop[0] - ayan)
    
    rows = []
    
    # Add transit Ascendant
    all_vargas = get_all_vargas(asc_sid)
    nak_det = get_nakshatra_details(asc_sid)
    nsi, pada = navamsa_for(asc_sid)
    rows.append({
        "Point": "Ascendant (Transit)",
        "Longitude (Sign DMS)": sign_dms_str(asc_sid),
        "Longitude (Dec)": round(asc_sid, 4),
        "Rashi": rashi_name(asc_sid),
        "Rashi_Idx": lon_to_sign_idx(asc_sid),
        "Nakshatra": nak_det['nakshatra'],
        "Pada": nak_det['pada'],
        "Navamsha_Idx": nsi,
        "D3_Idx": all_vargas['D3'],
        "D10_Idx": all_vargas['D10'],
        "Retro": False
    })
    
    # Calculate transit positions for all planets
    for nm, code in PLANETS.items():
        vals = swe.calc_ut(jd_ut, code, FLAGS)[0]
        lonv, spd = norm360(vals[0]), vals[3]
        nak_det = get_nakshatra_details(lonv)
        all_vargas = get_all_vargas(lonv)
        nsi, pada = navamsa_for(lonv)
        is_retro = spd < 0
        
        rows.append({
            "Point": nm,
            "Longitude (Sign DMS)": sign_dms_str(lonv),
            "Longitude (Dec)": round(lonv, 4),
            "Rashi": rashi_name(lonv),
            "Rashi_Idx": lon_to_sign_idx(lonv),
            "Nakshatra": nak_det['nakshatra'],
            "Pada": nak_det['pada'],
            "Navamsha_Idx": nsi,
            "D3_Idx": all_vargas['D3'],
            "D10_Idx": all_vargas['D10'],
            "Retro": is_retro
        })
    
    # Add Rahu/Ketu
    try:
        vals_true = swe.calc_ut(jd_ut, swe.TRUE_NODE, FLAGS)[0]
    except Exception:
        vals_true = swe.nod_aps_ut(jd_ut, swe.MOON, FLAGS, swe.NODBIT_OSCU)[0]
    
    rahu = norm360(vals_true[0])
    ketu = norm360(rahu + 180)
    
    for nm, lonv in [("Rahu (true)", rahu), ("Ketu (true)", ketu)]:
        nak_det = get_nakshatra_details(lonv)
        all_vargas = get_all_vargas(lonv)
        nsi, pada = navamsa_for(lonv)
        rows.append({
            "Point": nm,
            "Longitude (Sign DMS)": sign_dms_str(lonv),
            "Longitude (Dec)": round(lonv, 4),
            "Rashi": rashi_name(lonv),
            "Rashi_Idx": lon_to_sign_idx(lonv),
            "Nakshatra": nak_det['nakshatra'],
            "Pada": nak_det['pada'],
            "Navamsha_Idx": nsi,
            "D3_Idx": all_vargas['D3'],
            "D10_Idx": all_vargas['D10'],
            "Retro": True
        })
    
    return {
        "transit_dt": transit_dt.isoformat(),
        "ayanamsa_value": round(ayan, 6),
        "points": pd.DataFrame(rows)
    }


# ---------------------------------
# Mundane Astrology Calculations
# ---------------------------------

TITHI_NAMES_FULL = [
    "Shukla Pratipada", "Shukla Dvitiya", "Shukla Tritiya", "Shukla Chaturthi", 
    "Shukla Panchami", "Shukla Shashthi", "Shukla Saptami", "Shukla Ashtami",
    "Shukla Navami", "Shukla Dashami", "Shukla Ekadashi", "Shukla Dvadashi",
    "Shukla Trayodashi", "Shukla Chaturdashi", "Purnima",
    "Krishna Pratipada", "Krishna Dvitiya", "Krishna Tritiya", "Krishna Chaturthi",
    "Krishna Panchami", "Krishna Shashthi", "Krishna Saptami", "Krishna Ashtami",
    "Krishna Navami", "Krishna Dashami", "Krishna Ekadashi", "Krishna Dvadashi",
    "Krishna Trayodashi", "Krishna Chaturdashi", "Amavasya"
]


def jd_to_datetime(jd, tzname="UTC"):
    """
    Convert Julian Day to datetime with timezone.
    Returns a datetime object that will serialize to ISO 8601 format compatible with JavaScript.
    
    Note: For historical dates, timezone offsets may include seconds (e.g., +5:53:28 for Asia/Kolkata in 1800).
    This is handled correctly by Python but may cause issues with JavaScript Date parsing.
    """
    try:
        y, m, d, ut_hours = swe.revjul(jd, swe.GREG_CAL)
        
        # Check if year is within Python datetime range (1-9999)
        if not (1 <= y <= 9999):
            # Return HistoricalDate for out-of-range years
            # Calculate time components from ut_hours
            total_seconds = int(ut_hours * 3600)
            hour = total_seconds // 3600
            minute = (total_seconds % 3600) // 60
            second = total_seconds % 60
            microsecond = int((ut_hours * 3600 - total_seconds) * 1e6)
            
            # For out-of-range dates, we return UTC time as we can't easily convert 
            # to local timezone without a valid datetime object for dateutil/zoneinfo
            return HistoricalDate(y, m, d, hour, minute, second, microsecond, tzinfo=timezone.utc)
        
        dt_utc = datetime(y, m, d, tzinfo=timezone.utc) + timedelta(hours=ut_hours)
        local_zone = tz.gettz(tzname)
        result = dt_utc.astimezone(local_zone) if local_zone else dt_utc
        
        return result
    except (ValueError, OverflowError) as e:
        raise ValueError(f"Cannot convert JD {jd} to datetime: {e}")


def datetime_to_jd(dt):
    """Convert datetime to Julian Day"""
    if dt.tzinfo:
        dt_utc = dt.astimezone(timezone.utc)
    else:
        dt_utc = dt
    ut_hour = dt_utc.hour + dt_utc.minute/60 + dt_utc.second/3600
    return swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, ut_hour, swe.GREG_CAL)


def get_sun_moon_positions(jd, ayanamsa_code=swe.SIDM_LAHIRI):
    """Get sidereal Sun and Moon positions at given JD"""
    swe.set_sid_mode(ayanamsa_code)
    FLAGS = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    
    sun_data = swe.calc_ut(jd, swe.SUN, FLAGS)[0]
    moon_data = swe.calc_ut(jd, swe.MOON, FLAGS)[0]
    
    return {
        "sun_lon": norm360(sun_data[0]),
        "moon_lon": norm360(moon_data[0]),
        "sun_speed": sun_data[3],
        "moon_speed": moon_data[3]
    }


def get_tithi_at_jd(jd, ayanamsa_code=swe.SIDM_LAHIRI):
    """Get tithi number (1-30) at given JD"""
    pos = get_sun_moon_positions(jd, ayanamsa_code)
    diff = norm360(pos["moon_lon"] - pos["sun_lon"])
    tithi_num = int(diff // 12) + 1  # 1 to 30
    tithi_progress = (diff % 12) / 12.0
    return tithi_num, tithi_progress


def find_new_moon(start_jd, direction="next", ayanamsa_code=swe.SIDM_LAHIRI):
    """
    Find the New Moon (Amavasya) before or after start_jd.
    New Moon = Sun-Moon conjunction (tithi 30)
    """
    jd = start_jd
    step = 1.0 if direction == "next" else -1.0
    
    # Initial search with larger steps
    for _ in range(60):
        tithi, _ = get_tithi_at_jd(jd, ayanamsa_code)
        if tithi == 30:
            break
        jd += step
    
    # Binary search refinement
    for _ in range(20):
        pos = get_sun_moon_positions(jd, ayanamsa_code)
        diff = norm360(pos["moon_lon"] - pos["sun_lon"])
        
        # For new moon, diff should be near 0 (or 360)
        if diff > 180:
            diff = diff - 360
        
        if abs(diff) < 0.0001:
            break
        
        # Moon is faster, so adjust based on difference
        relative_speed = pos["moon_speed"] - pos["sun_speed"]
        adjustment = -diff / relative_speed if relative_speed != 0 else step * 0.1
        jd += adjustment
    
    return jd


def find_full_moon(start_jd, direction="next", ayanamsa_code=swe.SIDM_LAHIRI):
    """
    Find the Full Moon (Purnima) before or after start_jd.
    Full Moon = Sun-Moon opposition (tithi 15)
    """
    jd = start_jd
    step = 1.0 if direction == "next" else -1.0
    
    # Initial search
    for _ in range(60):
        tithi, _ = get_tithi_at_jd(jd, ayanamsa_code)
        if tithi == 15:
            break
        jd += step
    
    # Binary search refinement
    for _ in range(20):
        pos = get_sun_moon_positions(jd, ayanamsa_code)
        diff = norm360(pos["moon_lon"] - pos["sun_lon"])
        
        # For full moon, diff should be near 180
        target_diff = diff - 180
        
        if abs(target_diff) < 0.0001:
            break
        
        relative_speed = pos["moon_speed"] - pos["sun_speed"]
        adjustment = -target_diff / relative_speed if relative_speed != 0 else step * 0.1
        jd += adjustment
    
    return jd


def find_tithi_start(start_jd, target_tithi, direction="next", ayanamsa_code=swe.SIDM_LAHIRI):
    """
    Find when a specific tithi (1-30) begins.
    """
    jd = start_jd
    step = 1.0 if direction == "next" else -1.0
    
    # Each tithi spans 12 degrees of Moon-Sun difference
    target_diff = (target_tithi - 1) * 12
    
    # Initial search
    for _ in range(60):
        tithi, progress = get_tithi_at_jd(jd, ayanamsa_code)
        if tithi == target_tithi:
            # Go back to start of this tithi
            pos = get_sun_moon_positions(jd, ayanamsa_code)
            relative_speed = pos["moon_speed"] - pos["sun_speed"]
            jd -= (progress * 12) / relative_speed
            break
        jd += step
    
    # Refinement
    for _ in range(20):
        pos = get_sun_moon_positions(jd, ayanamsa_code)
        diff = norm360(pos["moon_lon"] - pos["sun_lon"])
        
        error = diff - target_diff
        if error > 180:
            error -= 360
        elif error < -180:
            error += 360
        
        if abs(error) < 0.0001:
            break
        
        relative_speed = pos["moon_speed"] - pos["sun_speed"]
        adjustment = -error / relative_speed if relative_speed != 0 else step * 0.1
        jd += adjustment
    
    return jd


def find_lunar_new_year(year, system="amanta", ayanamsa_code=swe.SIDM_LAHIRI):
    """
    Find Lunar New Year (Chaitra Shukla Pratipada).
    Amanta system: New Moon in Pisces or just after Sun enters Aries
    
    The lunar year begins with Chaitra masa, which starts with the new moon 
    when Sun is in Pisces (or has just entered Aries).
    """
    # Start search from around Feb-March of the given year
    start_jd = swe.julday(year, 2, 15, 12.0, swe.GREG_CAL)
    
    # Find new moons from Feb to May and check Sun's position
    for _ in range(5):
        nm_jd = find_new_moon(start_jd, "next", ayanamsa_code)
        pos = get_sun_moon_positions(nm_jd, ayanamsa_code)
        sun_sign = lon_to_sign_idx(pos["sun_lon"])
        
        # Chaitra begins with new moon when Sun is in Pisces (11) or Aries (0)
        # The new moon should be in Pisces/early Aries
        if sun_sign == 11 or sun_sign == 0:
            # This is Chaitra Amavasya, next day is Shukla Pratipada
            return nm_jd
        
        start_jd = nm_jd + 1
    
    return start_jd


def find_lunar_month_start(start_jd, direction="next", system="amanta", ayanamsa_code=swe.SIDM_LAHIRI):
    """
    Find the start of a lunar month.
    Amanta system: Month starts from new moon (Amavasya)
    Purnimant system: Month starts from full moon (Purnima)
    """
    if system == "amanta":
        return find_new_moon(start_jd, direction, ayanamsa_code)
    else:  # purnimant
        return find_full_moon(start_jd, direction, ayanamsa_code)


def find_solar_return(natal_sun_lon, year, lat, lon, tzname, ayanamsa_code=swe.SIDM_LAHIRI):
    """
    Find Tajika/Solar Return - when Sun returns to its natal position.
    Returns the exact JD when Sun reaches natal longitude.
    """
    # Start search around the birthday time
    start_jd = swe.julday(year, 1, 1, 12.0, swe.GREG_CAL)
    
    swe.set_sid_mode(ayanamsa_code)
    FLAGS = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    
    # Initial coarse search - Sun takes ~365 days to complete a cycle
    jd = start_jd
    for _ in range(400):
        sun_lon = norm360(swe.calc_ut(jd, swe.SUN, FLAGS)[0][0])
        diff = norm360(sun_lon - natal_sun_lon)
        if diff < 1 or diff > 359:
            break
        jd += 1
    
    # Fine refinement using Newton-Raphson
    for _ in range(20):
        sun_data = swe.calc_ut(jd, swe.SUN, FLAGS)[0]
        sun_lon = norm360(sun_data[0])
        sun_speed = sun_data[3]
        
        diff = sun_lon - natal_sun_lon
        if diff > 180:
            diff -= 360
        elif diff < -180:
            diff += 360
        
        if abs(diff) < 0.00001:
            break
        
        adjustment = -diff / sun_speed if sun_speed != 0 else 0.1
        jd += adjustment
    
    return jd


def find_tithi_pravesha(natal_sun_lon, natal_tithi, year, lat, lon, tzname, ayanamsa_code=swe.SIDM_LAHIRI):
    """
    Find Tithi Pravesha - when Sun returns to natal position AND 
    the tithi matches the birth tithi.
    
    This is more complex as we need to find when both conditions are satisfied.
    """
    # First find the solar return
    solar_return_jd = find_solar_return(natal_sun_lon, year, lat, lon, tzname, ayanamsa_code)
    
    # Now search nearby for when the tithi matches
    # The tithi cycle is ~29.5 days, so check within a lunar month
    best_jd = solar_return_jd
    best_diff = float('inf')
    
    # Check dates around solar return
    for day_offset in range(-15, 16):
        test_jd = solar_return_jd + day_offset
        tithi, progress = get_tithi_at_jd(test_jd, ayanamsa_code)
        
        if tithi == natal_tithi:
            # Check how close sun is to natal position
            swe.set_sid_mode(ayanamsa_code)
            FLAGS = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
            sun_lon = norm360(swe.calc_ut(test_jd, swe.SUN, FLAGS)[0][0])
            sun_diff = abs(norm360(sun_lon - natal_sun_lon))
            if sun_diff > 180:
                sun_diff = 360 - sun_diff
            
            if sun_diff < best_diff:
                best_diff = sun_diff
                best_jd = test_jd
    
    return best_jd, best_diff


def moon_nakshatra_idx(jd, ayanamsa_code=swe.SIDM_LAHIRI):
    swe.set_sid_mode(ayanamsa_code)
    FLAGS = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    lon = norm360(swe.calc_ut(jd, swe.MOON, FLAGS)[0][0])
    return int(lon // (360.0 / 27.0))


def yoga_idx_at(jd, ayanamsa_code=swe.SIDM_LAHIRI):
    swe.set_sid_mode(ayanamsa_code)
    FLAGS = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    sun_lon = norm360(swe.calc_ut(jd, swe.SUN, FLAGS)[0][0])
    moon_lon = norm360(swe.calc_ut(jd, swe.MOON, FLAGS)[0][0])
    yoga_lon = norm360(sun_lon + moon_lon)
    return int(yoga_lon // (360.0 / 27.0))


def find_nakshatra_pravesha(natal_sun_lon, natal_nak_idx, year, lat, lon, tzname, ayanamsa_code=swe.SIDM_LAHIRI):
    """
    Find Nakshatra Pravesha: nearest Moon return to natal Nakshatra around the solar return of the target year.
    """
    anchor_jd = find_solar_return(natal_sun_lon, year, lat, lon, tzname, ayanamsa_code)
    best_jd = None
    window_days = 30
    step = 0.25  # 6 hours
    prev_idx = None
    jd = anchor_jd - window_days
    while jd <= anchor_jd + window_days:
        idx = moon_nakshatra_idx(jd, ayanamsa_code)
        if idx == natal_nak_idx and prev_idx is not None and prev_idx != idx:
            # refine boundary between jd-step and jd
            low, high = jd - step, jd
            for _ in range(25):
                mid = (low + high) / 2.0
                mid_idx = moon_nakshatra_idx(mid, ayanamsa_code)
                if mid_idx == natal_nak_idx:
                    high = mid
                else:
                    low = mid
            best_jd = high
            break
        prev_idx = idx
        jd += step
    if best_jd is None:
        best_jd = anchor_jd
    return best_jd


def find_yoga_pravesha(natal_sun_lon, natal_yoga_idx, year, lat, lon, tzname, ayanamsa_code=swe.SIDM_LAHIRI):
    """
    Find Yoga Pravesha: nearest Sun+Moon yoga return to natal yoga around the solar return of the target year.
    """
    anchor_jd = find_solar_return(natal_sun_lon, year, lat, lon, tzname, ayanamsa_code)
    best_jd = None
    window_days = 30
    step = 0.25  # 6 hours
    prev_idx = None
    jd = anchor_jd - window_days
    while jd <= anchor_jd + window_days:
        idx = yoga_idx_at(jd, ayanamsa_code)
        if idx == natal_yoga_idx and prev_idx is not None and prev_idx != idx:
            low, high = jd - step, jd
            for _ in range(25):
                mid = (low + high) / 2.0
                mid_idx = yoga_idx_at(mid, ayanamsa_code)
                if mid_idx == natal_yoga_idx:
                    high = mid
                else:
                    low = mid
            best_jd = high
            break
        prev_idx = idx
        jd += step
    if best_jd is None:
        best_jd = anchor_jd
    return best_jd


def find_planet_sign_change(planet_code, start_jd, target_sign=None, direction="next", ayanamsa_code=swe.SIDM_LAHIRI):
    """
    Find when a planet enters a new sign (or a specific sign).
    """
    swe.set_sid_mode(ayanamsa_code)
    FLAGS = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    
    jd = start_jd
    step = 1.0 if direction == "next" else -1.0
    
    # Get starting sign
    start_lon = norm360(swe.calc_ut(jd, planet_code, FLAGS)[0][0])
    start_sign = lon_to_sign_idx(start_lon)
    
    # For "next" direction, ensure we start searching from slightly after start_jd
    # to avoid finding the same event if start_jd is very close to a previous result
    if direction == "next":
        jd = start_jd + 0.01  # Add ~14 minutes to ensure we're past any recent event
        start_lon = norm360(swe.calc_ut(jd, planet_code, FLAGS)[0][0])
        start_sign = lon_to_sign_idx(start_lon)
    
    # Search for sign change
    for _ in range(1000):  # Max ~3 years search
        jd += step
        lon = norm360(swe.calc_ut(jd, planet_code, FLAGS)[0][0])
        current_sign = lon_to_sign_idx(lon)
        
        if target_sign is not None:
            if current_sign == target_sign:
                break
        else:
            if current_sign != start_sign:
                break
        
        start_sign = current_sign
    
    # Refine to exact moment of sign entry
    target_entry = (current_sign * 30) if direction == "next" else ((current_sign + 1) * 30) % 360
    
    for _ in range(20):
        data = swe.calc_ut(jd, planet_code, FLAGS)[0]
        lon = norm360(data[0])
        speed = data[3]
        
        diff = lon - target_entry
        if diff > 180:
            diff -= 360
        elif diff < -180:
            diff += 360
        
        if abs(diff) < 0.00001:
            break
        
        adjustment = -diff / speed if speed != 0 else step * 0.1
        jd += adjustment
    
    return jd, current_sign


def find_planet_stationary(planet_code, start_jd, direction="next", station_type="retrograde"):
    """
    Find when a planet becomes stationary (speed = 0).
    station_type: "retrograde" (before retrograde) or "direct" (before direct)
    """
    FLAGS = swe.FLG_SWIEPH | swe.FLG_SPEED
    
    jd = start_jd
    step = 1.0 if direction == "next" else -1.0
    
    # Get starting speed
    start_speed = swe.calc_ut(jd, planet_code, FLAGS)[0][3]
    
    # Search for speed sign change
    for _ in range(1000):
        jd += step
        speed = swe.calc_ut(jd, planet_code, FLAGS)[0][3]
        
        if station_type == "retrograde":
            # Looking for speed going from positive to negative
            if start_speed > 0 and speed < 0:
                break
        else:  # direct
            # Looking for speed going from negative to positive
            if start_speed < 0 and speed > 0:
                break
        
        start_speed = speed
    
    # Go back and refine to when speed = 0
    jd -= step
    for _ in range(20):
        data = swe.calc_ut(jd, planet_code, FLAGS)[0]
        speed = data[3]
        
        if abs(speed) < 0.00001:
            break
        
        # Use acceleration to estimate when speed = 0
        jd2 = jd + 0.01
        speed2 = swe.calc_ut(jd2, planet_code, FLAGS)[0][3]
        accel = (speed2 - speed) / 0.01
        
        if abs(accel) > 0.00001:
            adjustment = -speed / accel
            jd += adjustment
        else:
            jd += step * 0.1
    
    return jd


def find_conjunction(planet1_code, planet2_code, start_jd, direction="next", ayanamsa_code=swe.SIDM_LAHIRI):
    """
    Find when two planets conjoin (same longitude).
    """
    swe.set_sid_mode(ayanamsa_code)
    FLAGS = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    
    jd = start_jd
    step = 1.0 if direction == "next" else -1.0
    
    # Initial search
    prev_diff = None
    for _ in range(1000):
        lon1 = norm360(swe.calc_ut(jd, planet1_code, FLAGS)[0][0])
        lon2 = norm360(swe.calc_ut(jd, planet2_code, FLAGS)[0][0])
        diff = norm360(lon1 - lon2)
        if diff > 180:
            diff -= 360
        
        if prev_diff is not None:
            # Check for zero crossing
            if (prev_diff > 0 and diff <= 0) or (prev_diff < 0 and diff >= 0):
                break
        
        prev_diff = diff
        jd += step
    
    # Refine
    for _ in range(20):
        data1 = swe.calc_ut(jd, planet1_code, FLAGS)[0]
        data2 = swe.calc_ut(jd, planet2_code, FLAGS)[0]
        
        lon1, speed1 = norm360(data1[0]), data1[3]
        lon2, speed2 = norm360(data2[0]), data2[3]
        
        diff = lon1 - lon2
        if diff > 180:
            diff -= 360
        elif diff < -180:
            diff += 360
        
        if abs(diff) < 0.00001:
            break
        
        relative_speed = speed1 - speed2
        adjustment = -diff / relative_speed if abs(relative_speed) > 0.00001 else step * 0.1
        jd += adjustment
    
    return jd


def find_opposition(planet1_code, planet2_code, start_jd, direction="next", ayanamsa_code=swe.SIDM_LAHIRI):
    """
    Find when two planets are in opposition (180 degrees apart).
    """
    swe.set_sid_mode(ayanamsa_code)
    FLAGS = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    
    jd = start_jd
    step = 1.0 if direction == "next" else -1.0
    
    # Initial search
    prev_diff = None
    for _ in range(1000):
        lon1 = norm360(swe.calc_ut(jd, planet1_code, FLAGS)[0][0])
        lon2 = norm360(swe.calc_ut(jd, planet2_code, FLAGS)[0][0])
        diff = norm360(lon1 - lon2) - 180
        if diff > 180:
            diff -= 360
        elif diff < -180:
            diff += 360
        
        if prev_diff is not None:
            if (prev_diff > 0 and diff <= 0) or (prev_diff < 0 and diff >= 0):
                break
        
        prev_diff = diff
        jd += step
    
    # Refine
    for _ in range(20):
        data1 = swe.calc_ut(jd, planet1_code, FLAGS)[0]
        data2 = swe.calc_ut(jd, planet2_code, FLAGS)[0]
        
        lon1, speed1 = norm360(data1[0]), data1[3]
        lon2, speed2 = norm360(data2[0]), data2[3]
        
        diff = norm360(lon1 - lon2) - 180
        if diff > 180:
            diff -= 360
        elif diff < -180:
            diff += 360
        
        if abs(diff) < 0.00001:
            break
        
        relative_speed = speed1 - speed2
        adjustment = -diff / relative_speed if abs(relative_speed) > 0.00001 else step * 0.1
        jd += adjustment
    
    return jd


def get_mundane_chart(event_jd, lat, lon, tzname, ayanamsa="Lahiri", ephe_path="ephe"):
    """
    Generate a full chart for a mundane event (lunar new year, solar return, etc.)
    """
    dt = jd_to_datetime(event_jd, tzname)
    return compute_chart_with_tzname(
        dt.year, dt.month, dt.day,
        dt.hour, dt.minute, dt.second,
        lat, lon, tzname,
        ephe_path=ephe_path,
        ayanamsa=ayanamsa
    )


# ---------------------------------
# Muntha Calculation (Tajika/Varshaphal)
# ---------------------------------
def calculate_muntha(natal_asc_lon, birth_year, varsha_year):
    """
    Calculate Muntha for a Tajika/Varshaphal chart.
    
    Muntha progresses one rashi (30 deg) for each year of life.
    See Dr. B.V. Raman "Varshaphal", chap 5.
    
    Muntha = Natal Ascendant + ((N - 1) * 30 deg)
    
    In the first year of life, Muntha is in the same rashi as natal lagna.
    In the second year, it moves to the second rashi, and so on.
    
    Args:
        natal_asc_lon: Natal Ascendant longitude in degrees
        birth_year: Year of birth
        varsha_year: Year for which Varshaphal is being calculated
    
    Returns:
        dict with Muntha longitude, sign index, and sign name
    """
    # Years elapsed (0 for birth year, 1 for first varshaphal, etc.)
    years_elapsed = varsha_year - birth_year
    
    # Muntha longitude = Natal Asc + (years * 30 degrees)
    muntha_lon = norm360(natal_asc_lon + (years_elapsed * 30.0))
    
    sign_idx = lon_to_sign_idx(muntha_lon)
    
    # Get nakshatra details for Muntha
    nak_det = get_nakshatra_details(muntha_lon)
    nsi, pada = navamsa_for(muntha_lon)
    all_vargas = get_all_vargas(muntha_lon)
    
    return {
        'longitude': muntha_lon,
        'longitude_dms': sign_dms_str(muntha_lon),
        'sign_idx': sign_idx,
        'sign_name': RASHI_SA[sign_idx],
        'sign_en': RASHI_EN[sign_idx],
        'nakshatra': nak_det['nakshatra'],
        'pada': nak_det['pada'],
        'navamsha_idx': nsi,
        'navamsha': RASHI_SA[nsi],
        'vargas': all_vargas
    }


# ---------------------------------
# Compressed Dasha for Varshaphal (1 year duration)
# ---------------------------------
def build_varsha_vimshottari(moon_lon, varsha_start_dt, duration_days=365.25):
    """
    Build Vimshottari Mahadasha compressed to fit within one year.
    
    Standard Vimshottari spans 120 years. For Varshaphal, we compress
    this to 1 year (or specified duration).
    
    Args:
        moon_lon: Moon longitude at the Varshaphal moment
        varsha_start_dt: datetime of the Varshaphal (solar return)
        duration_days: Total duration to compress into (default 365.25 = 1 year)
    
    Returns:
        DataFrame with compressed Mahadasha periods
    """
    NAK_STEP = 360.0 / 27.0
    MD_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
    MD_YEARS = {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7, "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17}
    TOTAL_YEARS = 120.0
    
    # Compression factor: 1 year's worth of days / 120 years
    compression_ratio = duration_days / (TOTAL_YEARS * 365.25)
    
    # Calculate starting nakshatra and dasha
    nak_index = int(moon_lon // NAK_STEP)
    frac_in = (moon_lon - nak_index * NAK_STEP) / NAK_STEP
    frac_left = 1.0 - frac_in
    
    start_md_i = nak_index % 9
    start_md = MD_ORDER[start_md_i]
    start_md_left_years = MD_YEARS[start_md] * frac_left
    
    # Build the sequence
    rows = []
    cur = varsha_start_dt
    seq = [(start_md, start_md_left_years)]
    j = (start_md_i + 1) % 9
    spent = start_md_left_years
    
    # Build full 120-year sequence
    while spent < TOTAL_YEARS - 1e-9:
        lord = MD_ORDER[j]
        y2 = MD_YEARS[lord]
        seq.append((lord, y2))
        spent += y2
        j = (j + 1) % 9
    
    # Now compress each period
    for lord, years in seq:
        compressed_days = years * 365.25 * compression_ratio
        st = cur
        en = st + timedelta(days=compressed_days)
        rows.append({
            "Mahadasa": lord,
            "Start": st.strftime("%Y-%m-%d %H:%M"),
            "End": en.strftime("%Y-%m-%d %H:%M"),
            "Duration (days)": round(compressed_days, 2),
            "Duration (original years)": round(years, 2)
        })
        cur = en
    
    return pd.DataFrame(rows)


def build_varsha_yogini(moon_lon, varsha_start_dt, duration_days=365.25):
    """
    Build Yogini Dasha compressed to fit within one year.
    
    Standard Yogini spans 36 years. For Varshaphal, we compress
    this to 1 year (or specified duration).
    
    Args:
        moon_lon: Moon longitude at the Varshaphal moment
        varsha_start_dt: datetime of the Varshaphal (solar return)
        duration_days: Total duration to compress into (default 365.25 = 1 year)
    
    Returns:
        DataFrame with compressed Yogini periods
    """
    NAK_STEP = 360.0 / 27.0
    YOG_ORDER = ["Mangala", "Pingala", "Dhanya", "Bhramari", "Bhadrika", "Ulka", "Siddha", "Sankata"]
    YOG_YEARS = {"Mangala": 1, "Pingala": 2, "Dhanya": 3, "Bhramari": 4, "Bhadrika": 5, "Ulka": 6, "Siddha": 7, "Sankata": 8}
    TOTAL_YEARS = 36.0  # 1+2+3+4+5+6+7+8 = 36
    
    # Nakshatra to Yogini mapping
    N2Y = {
        0: "Bhramari", 1: "Bhadrika", 2: "Ulka", 3: "Siddha", 4: "Sankata",
        5: "Mangala", 6: "Pingala", 7: "Dhanya", 8: "Bhramari", 9: "Bhadrika",
        10: "Ulka", 11: "Siddha", 12: "Sankata", 13: "Mangala", 14: "Pingala",
        15: "Dhanya", 16: "Bhramari", 17: "Bhadrika", 18: "Ulka", 19: "Siddha",
        20: "Sankata", 21: "Mangala", 22: "Pingala", 23: "Dhanya", 24: "Bhramari",
        25: "Bhadrika", 26: "Ulka"
    }
    
    # Compression factor
    compression_ratio = duration_days / (TOTAL_YEARS * 365.25)
    
    # Calculate starting nakshatra
    nak_index = int(moon_lon // NAK_STEP)
    frac_in = (moon_lon - nak_index * NAK_STEP) / NAK_STEP
    frac_left = 1.0 - frac_in
    
    start_yog = N2Y[nak_index]
    yog_i = YOG_ORDER.index(start_yog)
    
    rows = []
    cur = varsha_start_dt
    
    # First (partial) period
    y1 = YOG_YEARS[start_yog] * frac_left
    compressed_days = y1 * 365.25 * compression_ratio
    rows.append({
        "Yogini": YOG_ORDER[yog_i],
        "Start": cur.strftime("%Y-%m-%d %H:%M"),
        "End": (cur + timedelta(days=compressed_days)).strftime("%Y-%m-%d %H:%M"),
        "Duration (days)": round(compressed_days, 2),
        "Duration (original years)": round(y1, 2)
    })
    cur += timedelta(days=compressed_days)
    yog_i = (yog_i + 1) % 8
    
    # Complete 3 full cycles (to cover enough time)
    for _ in range(24):  # 3 cycles × 8 yoginis
        lord = YOG_ORDER[yog_i]
        y2 = YOG_YEARS[lord]
        compressed_days = y2 * 365.25 * compression_ratio
        end = cur + timedelta(days=compressed_days)
        rows.append({
            "Yogini": lord,
            "Start": cur.strftime("%Y-%m-%d %H:%M"),
            "End": end.strftime("%Y-%m-%d %H:%M"),
            "Duration (days)": round(compressed_days, 2),
            "Duration (original years)": round(y2, 2)
        })
        cur = end
        yog_i = (yog_i + 1) % 8
    
    return pd.DataFrame(rows)


# ==============================================================
# Vimshottari Antardasha & Pratyantardasha (standalone functions)
# ==============================================================

# Vimshottari constants (module-level for reuse)
VIM_MD_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
VIM_MD_YEARS = {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7, "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17}

def get_vimshottari_antardasha(md_lord: str, md_start: str, md_duration_years: float) -> list:
    """
    Calculate all Antardasha periods within a Mahadasha.
    
    Args:
        md_lord: Mahadasha lord (e.g., "Saturn")
        md_start: Start datetime string (YYYY-MM-DD HH:MM:SS)
        md_duration_years: Duration of Mahadasha in years
    
    Returns:
        List of Antardasha periods with Start, End, Duration
    """
    rows = []
    cur = datetime.strptime(md_start, "%Y-%m-%d %H:%M:%S")
    
    # Antardasha sequence starts with Mahadasha lord
    md_idx = VIM_MD_ORDER.index(md_lord)
    
    for i in range(9):
        ad_lord = VIM_MD_ORDER[(md_idx + i) % 9]
        # Antardasha duration = (MD years * AD years) / 120 years
        ad_years = (md_duration_years * VIM_MD_YEARS[ad_lord]) / 120.0
        ad_days = ad_years * 365.25
        end = cur + timedelta(days=ad_days)
        
        rows.append({
            "Mahadasa": md_lord,
            "Antardasa": ad_lord,
            "Start": cur.strftime("%Y-%m-%d %H:%M:%S"),
            "End": end.strftime("%Y-%m-%d %H:%M:%S"),
            "Duration (days)": round(ad_days, 2),
            "Duration (years)": round(ad_years, 4)
        })
        cur = end
    
    return rows


def get_vimshottari_pratyantardasha(md_lord: str, ad_lord: str, ad_start: str, ad_duration_days: float) -> list:
    """
    Calculate all Pratyantardasha periods within an Antardasha.
    
    Args:
        md_lord: Mahadasha lord
        ad_lord: Antardasha lord
        ad_start: Start datetime string (YYYY-MM-DD HH:MM:SS)
        ad_duration_days: Duration of Antardasha in days
    
    Returns:
        List of Pratyantardasha periods with Start, End, Duration
    """
    rows = []
    cur = datetime.strptime(ad_start, "%Y-%m-%d %H:%M:%S")
    
    # Pratyantardasha sequence starts with Antardasha lord
    ad_idx = VIM_MD_ORDER.index(ad_lord)
    
    for i in range(9):
        pd_lord = VIM_MD_ORDER[(ad_idx + i) % 9]
        # Pratyantardasha duration = (AD days * PD years) / 120 years
        pd_days = (ad_duration_days * VIM_MD_YEARS[pd_lord]) / 120.0
        end = cur + timedelta(days=pd_days)
        
        rows.append({
            "Mahadasa": md_lord,
            "Antardasa": ad_lord,
            "Pratyantardasa": pd_lord,
            "Start": cur.strftime("%Y-%m-%d %H:%M:%S"),
            "End": end.strftime("%Y-%m-%d %H:%M:%S"),
            "Duration (days)": round(pd_days, 2)
        })
        cur = end
    
    return rows


# ==============================================================
# YOGINI DASHA SUB-PERIODS
# ==============================================================

# Yogini constants (module-level for reuse)
YOG_ORDER = ["Mangala", "Pingala", "Dhanya", "Bhramari", "Bhadrika", "Ulka", "Siddha", "Sankata"]
YOG_YEARS = {"Mangala": 1, "Pingala": 2, "Dhanya": 3, "Bhramari": 4, "Bhadrika": 5, "Ulka": 6, "Siddha": 7, "Sankata": 8}
YOG_TOTAL_YEARS = 36.0  # 1+2+3+4+5+6+7+8 = 36

def get_yogini_antardasha(md_lord: str, md_start: str, md_duration_years: float) -> list:
    """Calculate all Antardasha periods within a Yogini Mahadasha."""
    rows = []
    cur = datetime.strptime(md_start, "%Y-%m-%d %H:%M:%S")
    
    # Antardasha sequence starts with Mahadasha lord
    md_idx = YOG_ORDER.index(md_lord)
    
    for i in range(8):
        ad_lord = YOG_ORDER[(md_idx + i) % 8]
        # Antardasha duration = (MD years * AD years) / 36 years
        ad_years = (md_duration_years * YOG_YEARS[ad_lord]) / YOG_TOTAL_YEARS
        ad_days = ad_years * 365.25
        end = cur + timedelta(days=ad_days)
        
        rows.append({
            "Mahadasa": md_lord,
            "Antardasa": ad_lord,
            "Start": cur.strftime("%Y-%m-%d %H:%M:%S"),
            "End": end.strftime("%Y-%m-%d %H:%M:%S"),
            "Duration (days)": round(ad_days, 2),
            "Duration (years)": round(ad_years, 4)
        })
        cur = end
    
    return rows


def get_yogini_pratyantardasha(md_lord: str, ad_lord: str, ad_start: str, ad_duration_days: float) -> list:

    rows = []
    cur = datetime.strptime(ad_start, "%Y-%m-%d %H:%M:%S")
    
    # Pratyantardasha sequence starts with Antardasha lord
    ad_idx = YOG_ORDER.index(ad_lord)
    
    for i in range(8):
        pd_lord = YOG_ORDER[(ad_idx + i) % 8]
        # Pratyantardasha duration = (AD days * PD years) / 36 years
        pd_days = (ad_duration_days * YOG_YEARS[pd_lord]) / YOG_TOTAL_YEARS
        end = cur + timedelta(days=pd_days)
        
        rows.append({
            "Mahadasa": md_lord,
            "Antardasa": ad_lord,
            "Pratyantardasa": pd_lord,
            "Start": cur.strftime("%Y-%m-%d %H:%M:%S"),
            "End": end.strftime("%Y-%m-%d %H:%M:%S"),
            "Duration (days)": round(pd_days, 2)
        })
        cur = end
    
    return rows
