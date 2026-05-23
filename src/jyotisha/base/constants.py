# src/ci_core/constants.py
import swisseph as swe

# ---------------------------------
# Sunrise/Sunset configuration
# ---------------------------------
SUNRISE_DEFINITION = "vedic"   # default
SITE_ELEVATION_M   = 0.0       # meters above sea level
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
MOOLATR={"Sun":("Leo",0.0,20.0),"Moon":("Taurus",0.0,3.0),"Mars":("Aries",0.0,12.0),"Mercury":("Virgo",15.0,20.0),"Jupiter":("Sagittarius",0.0,10.0),"Venus":("Libra",0.0,15.0),"Saturn":("Aquarius",0.0,20.0)}

SIGN_INDEX = {name:i for i,name in enumerate(RASHI_EN)}
SIGN_LORD = {0:"Mars",1:"Venus",2:"Mercury",3:"Moon",4:"Sun",5:"Mercury",6:"Venus",7:"Mars",8:"Jupiter",9:"Saturn",10:"Saturn",11:"Jupiter"}
PERM_FRIENDS={"Sun":{"Moon","Mars","Jupiter"},"Moon":{"Sun","Mercury"},"Mars":{"Sun","Moon","Jupiter"},"Mercury":{"Sun","Venus"},"Jupiter":{"Sun","Moon","Mars"},"Venus":{"Mercury","Saturn"},"Saturn":{"Mercury","Venus"}}
PERM_ENEMIES={"Sun":{"Venus","Saturn"},"Moon":set(),"Mars":{"Mercury"},"Mercury":{"Moon"},"Jupiter":{"Venus","Mercury"},"Venus":{"Sun","Moon"},"Saturn":{"Sun","Moon","Mars"}}
BENEFICS={"Jupiter","Venus","Mercury"}; MALEFICS={"Saturn","Mars","Sun"}
MIN_SHADBALA_RUPA={"Sun":6.5,"Moon":6.0,"Mars":5.0,"Mercury":7.0,"Jupiter":6.5,"Venus":5.5,"Saturn":5.0}
MAX_SHADBALA_RUPA={"Sun":20.0,"Moon":20.0,"Mars":20.0,"Mercury":20.0,"Jupiter":20.0,"Venus":20.0,"Saturn":20.0}
DIG_MAX_ANGLE={"Sun":90.0,"Mars":90.0,"Jupiter":0.0,"Mercury":0.0,"Moon":180.0,"Venus":180.0,"Saturn":270.0}

PLANETS = {"Sun":swe.SUN,"Moon":swe.MOON,"Mars":swe.MARS,"Mercury":swe.MERCURY,"Jupiter":swe.JUPITER,"Venus":swe.VENUS,"Saturn":swe.SATURN,"Uranus":swe.URANUS,"Neptune":swe.NEPTUNE,"Pluto":swe.PLUTO}
GRAHAS_FOR_HOUSE = ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu (true)","Ketu (true)","Uranus","Neptune","Pluto"]

# Varga Names
HORA_NAMES = ["Solar", "Lunar"]
DREKKANA_NAMES = ["Nārada", "Agastya", "Durvāsa"]
CHATURTHAMSA_NAMES = ["Sanaka", "Sananda", "Kumara", "Sanatana"]
NAVAMSA_NAMES = ["Deva", "Manushya", "Rākṣasa"]
SAPTAMSA_NAMES = ["Kṣāra", "Kṣīra", "Dadhi", "Ājya", "Ikṣurasa", "Madya", "Śuddha-Jala"]
DASAMSA_NAMES = ["Indra", "Agni", "Yama", "Nirṛti", "Varuṇa", "Vāyu", "Kubera", "Īśāna", "Brahmā", "Ananta"]
DVADASAMSA_NAMES = ["Dhātā", "Aryamā", "Mitra", "Varuṇa", "Indra", "Vivasvān", "Pūṣā", "Parjanya", "Aṁśu", "Bhaga", "Tvaṣṭā", "Viṣṇu"]
SHODASAMSA_NAMES = ["Brahmā", "Viṣṇu", "Rudra", "Śiva", "Parameṣṭhī", "Maheśvara", "Deveśa", "Ardhanārīśa",
                    "Lakṣmī", "Vijayā", "Bhadrā", "Śubhā", "Rambhā", "Urvaśī", "Menakā", "Tilottamā"]
VIMSAMSA_NAMES = ["Kālī", "Gaurī", "Jyeṣṭhā", "Lakṣmī", "Vijayā", "Vimalā", "Saṃkarī", "Balā", "Dhanyā", "Aṅkuśā",
                  "Piṅgalā", "Chūḍāmaṇi", "Māṁsī", "Sarvakāmī", "Vāruṇī", "Padmā", "Bhuvaneśī", "Kṣobhiṇī", "Mahāmāyā", "Ratī"]
SIDDHAMSA_NAMES = ["Skanda", "Parśudhara", "Anala", "Viśvakarmā", "Bhaga", "Mitra", "Maya", "Antaka",
                   "Vṛṣadhvaja", "Govinda", "Madana", "Bhīma", "Varuṇa", "Gāyatrī", "Mṛgāṅka", "Pitrī",
                   "Durgā", "Gaṇeśa", "Mukuṭeśvarī", "Prabhākara", "Dikpālaka", "Soumya", "Śānti", "Amṛta"]
SAPTAVIMSAMSA_NAMES = NAK_NAMES
TRIMSAMSA_NAMES_ODD = ["Agni (Mars)", "Vāyu (Saturn)", "Indra (Jupiter)", "Kubera (Mercury)", "Varuṇa (Venus)"]
TRIMSAMSA_NAMES_EVEN = ["Varuṇa (Venus)", "Kubera (Mercury)", "Indra (Jupiter)", "Vāyu (Saturn)", "Agni (Mars)"]
KHAVEDAMSA_NAMES = [f"Kha-{i+1}" for i in range(40)]
AKSHAVEDAMSA_NAMES = [f"Akṣa-{i+1}" for i in range(45)]
SHASHTIAMSA_NAMES = [
    "Ghora", "Rākṣasa", "Deva", "Kubera", "Yakṣa", "Kiṁnara", "Bhrashṭa", "Kulāghna", "Garala", "Agni",
    "Maya", "Puriṣaka", "Apāṁpati", "Marut", "Kāla", "Sarpa", "Amṛta", "Indu", "Mṛdu", "Komala",
    "Padma", "Viṣa-Dagdha", "Kṣitīśa", "Kamalākara", "Gulika", "Mṛtyu", "Kāla", "Davāgni", "Ghora", "Yama",
    "Kaṇṭaka", "Sudhā", "Amṛta", "Pūrṇa-Candra", "Viṣa-Dagdha", "Kulāghna", "Vāṁśakṣaya", "Utpāta", "Kāla", "Saumya",
    "Komala", "Śītala", "Karāla-Daṁṣṭra", "Caṇḍāla", "Pravīṇa", "Kalyāṇī", "Kṣiteśa", "Kamalākara", "Gulika", "Mṛtyu",
    "Kāla", "Davāgni", "Ghora", "Nirmala", "Saumya", "Kroora", "Atīśītala", "Amṛta", "Payodhī", "Brahma"
]
SHASHTIAMSA_BENEFIC = {2, 3, 4, 5, 16, 17, 18, 19, 20, 23, 24, 31, 32, 33, 39, 40, 41, 45, 46, 47, 48, 53, 54, 57, 58, 59, 60}

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

# Tithi Names (Standard List assumed)
TITHI_NAMES_FULL = [
    "Shukla Pratipada", "Shukla Dwitiya", "Shukla Tritiya", "Shukla Chaturthi", "Shukla Panchami",
    "Shukla Shashthi", "Shukla Saptami", "Shukla Ashtami", "Shukla Navami", "Shukla Dashami",
    "Shukla Ekadashi", "Shukla Dwadashi", "Shukla Trayodashi", "Shukla Chaturdashi", "Purnima",
    "Krishna Pratipada", "Krishna Dwitiya", "Krishna Tritiya", "Krishna Chaturthi", "Krishna Panchami",
    "Krishna Shashthi", "Krishna Saptami", "Krishna Ashtami", "Krishna Navami", "Krishna Dashami",
    "Krishna Ekadashi", "Krishna Dwadashi", "Krishna Trayodashi", "Krishna Chaturdashi", "Amavasya"
]

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


# Vedic Lunar Month Map (Sun Sign Index 0=Aries -> Vaisakha)
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

def get_ayanamsa_list():
    """Return list of available ayanamsa names"""
    return list(AYANAMSA_OPTIONS.keys())


def get_ayanamsa_code(name: str) -> int:
    """Get Swiss Ephemeris code for ayanamsa name"""
    return AYANAMSA_OPTIONS.get(name, swe.SIDM_LAHIRI)
