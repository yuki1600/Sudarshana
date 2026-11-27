import { type KeyboardEvent } from "react";
import { type RemedyBphsEntry } from "./api";

/** One verse as the reader shows it, whatever file it came from. */
export interface Item {
  id: string; title: string; source: string; citation: string;
  sanskrit?: string; translation: string; note?: string;
}

/* -------------------------------------------------------------------------- */
/*                            PLANETARY METADATA                              */
/* -------------------------------------------------------------------------- */

export interface GrahaDetail {
  name: string;
  sanskrit: string;
  code: string;
  color: string;
  deity: string;
  day: string;
  direction: string;
  gem: string;
  uparatna: string;
  metal: string;
  samidh: string;
  japaCount: string;
  mantra: string;
  gayatri: string;
  charity: string;
  fasting: string;
}

export const PLANET_DATA: Record<string, GrahaDetail> = {
  Sun: {
    name: "Sun",
    sanskrit: "Sūrya",
    code: "SY",
    color: "var(--g-Su)",
    deity: "Agni / Śiva / Śrīman Nārāyaṇa",
    day: "Sunday",
    direction: "East (Pūrva)",
    gem: "Ruby (Māṇikya)",
    uparatna: "Garnet / Red Spinel",
    metal: "Copper / Gold",
    samidh: "Arka (Calotropis gigantea)",
    japaCount: "7,000",
    mantra: "oṃ hrāṃ hrīṃ hrauṃ saḥ sūryāya namaḥ",
    gayatri: "oṃ ādityāya vidmahe mārtaṇḍāya dhīmahi | tanno sūryaḥ pracodayāt ||",
    charity: "Wheat, copper vessels, ruby, jaggery, red sandalwood, red flowers, milch cow with calf.",
    fasting: "Sunday fasting with one meal without salt after sunset, worship of Sūrya at dawn.",
  },
  Moon: {
    name: "Moon",
    sanskrit: "Candra",
    code: "CH",
    color: "var(--g-Mo)",
    deity: "Varuṇa / Pārvatī",
    day: "Monday",
    direction: "North-West (Vāyavya)",
    gem: "Natural Pearl (Muktā)",
    uparatna: "Moonstone (Candra-kānta)",
    metal: "Pure Silver",
    samidh: "Palāśa (Butea monosperma)",
    japaCount: "11,000",
    mantra: "oṃ śrāṃ śrīṃ śrauṃ saḥ candrāya namaḥ",
    gayatri: "oṃ kṣīraputrāya vidmahe amṛtatattvāya dhīmahi | tanno candraḥ pracodayāt ||",
    charity: "Rice, pure cow's milk, silver, white garments, pearl, conch, sugar, white flowers.",
    fasting: "Monday fasting, drinking milk or fruit juice; evening worship of Candradeva / Somavāra vrata.",
  },
  Mars: {
    name: "Mars",
    sanskrit: "Maṅgala",
    code: "MA",
    color: "var(--g-Ma)",
    deity: "Skanda (Subrahmaṇya) / Kṣetrapāla",
    day: "Tuesday",
    direction: "South (Dakṣiṇa)",
    gem: "Red Coral (Vidruma / Pravāla)",
    uparatna: "Carnelian",
    metal: "Copper",
    samidh: "Khadira (Acacia catechu)",
    japaCount: "10,000",
    mantra: "oṃ krāṃ krīṃ krauṃ saḥ bhaumāya namaḥ",
    gayatri: "oṃ aṅgārakāya vidmahe śaktihastāya dhīmahi | tanno bhaumaḥ pracodayāt ||",
    charity: "Red lentils (masoor dal), red coral, copper utensils, red cloth, jaggery, bullock.",
    fasting: "Tuesday fasting (Maṅgalavāra vrata), consuming meal with jaggery and wheat once.",
  },
  Mercury: {
    name: "Mercury",
    sanskrit: "Budha",
    code: "BU",
    color: "var(--g-Me)",
    deity: "Śrī Viṣṇu Bhagavān",
    day: "Wednesday",
    direction: "North (Uttara)",
    gem: "Emerald (Marakata / Pannā)",
    uparatna: "Peridot / Green Tourmaline",
    metal: "Bronze (Kāṃsya)",
    samidh: "Apāmārga (Achyranthes aspera)",
    japaCount: "9,000",
    mantra: "oṃ brāṃ brīṃ brauṃ saḥ budhāya namaḥ",
    gayatri: "oṃ saumyarūpāya vidmahe vāṇeśāya dhīmahi | tanno budhaḥ pracodayāt ||",
    charity: "Green gram (moong dal), emerald, green apparel, bronze plates, sacred books, ivory.",
    fasting: "Wednesday fasting, worship of Lord Viṣṇu, reciting Viṣṇu Sahasranāma.",
  },
  Jupiter: {
    name: "Jupiter",
    sanskrit: "Guru",
    code: "GU",
    color: "var(--g-Ju)",
    deity: "Brahmā / Bṛhaspati / Indra",
    day: "Thursday",
    direction: "North-East (Īśāna)",
    gem: "Yellow Sapphire (Puṣparāga)",
    uparatna: "Yellow Topaz / Heliodor",
    metal: "Gold",
    samidh: "Aśvattha / Pīpal (Ficus religiosa)",
    japaCount: "19,000",
    mantra: "oṃ grāṃ grīṃ grauṃ saḥ gurave namaḥ",
    gayatri: "oṃ devācāryāya vidmahe devapūjyāya dhīmahi | tanno guruḥ pracodayāt ||",
    charity: "Bengal gram (chana dal), turmeric, yellow sapphire, gold, books of scripture, yellow silk, salt.",
    fasting: "Thursday fasting (Bṛhaspativāra vrata), worship of Guru and Lord Nārāyaṇa, honoring preceptors.",
  },
  Venus: {
    name: "Venus",
    sanskrit: "Śukra",
    code: "SK",
    color: "var(--g-Ve)",
    deity: "Śrī Mahālakṣmī / Indrāṇī",
    day: "Friday",
    direction: "South-East (Āgneya)",
    gem: "Diamond (Vajra / Hīrā)",
    uparatna: "White Zircon / White Sapphire",
    metal: "Silver / Platinum",
    samidh: "Audumbara / Gūlar (Ficus glomerata)",
    japaCount: "16,000",
    mantra: "oṃ drāṃ drīṃ drauṃ saḥ śukrāya namaḥ",
    gayatri: "oṃ bhārgavāya vidmahe daityācāryāya dhīmahi | tanno śukraḥ pracodayāt ||",
    charity: "Pure desi cow ghee, curd, rice cooked in milk, white silk, diamond, silver, white camphor.",
    fasting: "Friday fasting (Śukravāra vrata), worship of Mahālakṣmī with Śrī Sūkta recitation.",
  },
  Saturn: {
    name: "Saturn",
    sanskrit: "Śani",
    code: "SA",
    color: "var(--g-Sa)",
    deity: "Yama / Prajāpati / Śiva",
    day: "Saturday",
    direction: "West (Paścima)",
    gem: "Blue Sapphire (Nīlama)",
    uparatna: "Amethyst / Iolite / Blue Topaz",
    metal: "Iron (Loha)",
    samidh: "Śamī (Prosopis cineraria)",
    japaCount: "23,000",
    mantra: "oṃ prāṃ prīṃ prauṃ saḥ śanaiścarāya namaḥ",
    gayatri: "oṃ śanaiścarāya vidmahe sūryaputrāya dhīmahi | tanno mandaḥ pracodayāt ||",
    charity: "Black sesame (til), mustard oil in iron pot (chāya dāna), black blanket, iron tools, black cow.",
    fasting: "Saturday fasting (Śanivāra vrata), lighting mustard oil lamp under Pīpal tree at dusk, Hanumān Cālīsā.",
  },
  Rahu: {
    name: "Rahu",
    sanskrit: "Rāhu",
    code: "RA",
    color: "var(--g-Ra)",
    deity: "Sarpa Devatā / Durgā",
    day: "Saturday evening / Wednesday night",
    direction: "South-West (Nairṛti)",
    gem: "Hessonite Garnet (Gomeda)",
    uparatna: "Orange Zircon",
    metal: "Mixed alloy / Lead",
    samidh: "Dūrvā grass (Cynodon dactylon)",
    japaCount: "18,000",
    mantra: "oṃ bhrāṃ bhrīṃ bhrauṃ saḥ rāhave namaḥ",
    gayatri: "oṃ nīlavarṇāya vidmahe siṃhikāsutāya dhīmahi | tanno rāhuḥ pracodayāt ||",
    charity: "Black gram (urad dal), dark-blue blanket, hessonite, mustard, iron, feeding stray dogs.",
    fasting: "Fasting on Saturdays or during Rahu Kāla on Saturdays; worship of Goddess Durgā or Lord Narasiṃha.",
  },
  Ketu: {
    name: "Ketu",
    sanskrit: "Ketu",
    code: "KE",
    color: "var(--g-Ke)",
    deity: "Lord Gaṇeśa / Citragupta",
    day: "Tuesday night",
    direction: "North-West (Adhaḥ)",
    gem: "Cat's Eye (Vaidūrya / Lahsuniyā)",
    uparatna: "Chrysoberyl / Hawk's Eye",
    metal: "Bell metal / Lead",
    samidh: "Kuśa / Darbha grass (Desmostachya bipinnata)",
    japaCount: "17,000",
    mantra: "oṃ strāṃ strīṃ strauṃ saḥ ketave namaḥ",
    gayatri: "oṃ padmaputrāya vidmahe amṛteśāya dhīmahi | tanno ketuḥ pracodayāt ||",
    charity: "Seven grains (sapta-dhānya), multi-colored blanket, cat's eye, iron weapons, feeding street dogs.",
    fasting: "Fasting on Tuesdays; worship of Lord Gaṇeśa with Gaṇapati Atharvaśīrṣa recitation.",
  },
};

export const CONDITION_META: Record<
  string,
  {
    title: string;
    chapter: string;
    severity: "critical" | "warning" | "info";
    cause: string;
    deity: string;
    summary: string;
  }
> = {
  amavasya: {
    title: "Amāvāsyā Janana",
    chapter: "BPHS Ch. 85",
    severity: "warning",
    cause: "Moon-Sun conjunction (30th Tithi) with zero lunar illumination.",
    deity: "Rudra & Sūrya-Candra",
    summary: "Rudra pūjā, silver cow donation, water sanctification rites and brāhmaṇa feast.",
  },
  krishna_chaturdashi: {
    title: "Kṛṣṇa Caturdaśī Janana",
    chapter: "BPHS Ch. 86",
    severity: "warning",
    cause: "Birth on the 14th day of waning moon, divided into six sensitive time segments.",
    deity: "Lord Śiva (Mahāmṛtyuñjaya)",
    summary: "Worship of Lord Śiva with bilva leaves, black sesame seeds dāna, Mṛtyuñjaya homa.",
  },
  bhadra_yoga: {
    title: "Bhadra (Viṣṭi) / Vyātīpāta Yoga",
    chapter: "BPHS Ch. 88",
    severity: "critical",
    cause: "Birth occurring during the inauspicious Viṣṭi karaṇa or the malefic Vyātīpāta yoga.",
    deity: "Yama & Rudra",
    summary: "Mṛtyu devatā pūjā, ghee filled bronze pot dāna, and Mahāmṛtyuñjaya japa.",
  },
  sankranti: {
    title: "Saṅkrānti Janana",
    chapter: "BPHS Ch. 89",
    severity: "warning",
    cause: "Birth at the exact celestial moment when the Sun transitions into a new rāśi.",
    deity: "Sūrya Bhagavān",
    summary: "Red sandalwood & lotus pūjā, copper vessel donation with gold and red apparel.",
  },
  eclipse: {
    title: "Grahaṇa Janana (Eclipse Birth)",
    chapter: "BPHS Ch. 90",
    severity: "critical",
    cause: "Birth occurring during or closely flanking a Solar or Lunar Eclipse.",
    deity: "Three-Metal Deities",
    summary: "Worship of gold, silver and copper images, eclipse snāna, garments and food charity.",
  },
  gandanta: {
    title: "Nakṣatra / Tithi / Lagna Gandānta",
    chapter: "BPHS Ch. 91",
    severity: "critical",
    cause: "Water-fire transitional junctions (Revatī-Aśvinī, Āśleṣā-Maghā, Jyeṣṭhā-Mūla).",
    deity: "Presiding Star Deities & Varuṇa",
    summary: "Kalaśa snāna with herbal extracts, father viewing newborn only after sanctification.",
  },
  abhukta_mula: {
    title: "Abhukta Mūla Janana",
    chapter: "BPHS Ch. 92",
    severity: "critical",
    cause: "Birth in terminal 6 ghaṭīs of Jyeṣṭhā or initial 8 ghaṭīs of Mūla star.",
    deity: "Nirṛti & Bṛhaspati",
    summary: "Comprehensive Mūla Śānti, land/cow charity, pacification homa with Darbha grass.",
  },
  jyeshtha_gandanta: {
    title: "Jyeṣṭhā Nakṣatra Gandānta",
    chapter: "BPHS Ch. 93",
    severity: "warning",
    cause: "Birth in the delicate concluding portion of Jyeṣṭhā nakṣatra.",
    deity: "Indra & Varuṇa",
    summary: "Gold idol propitiation, specific nakṣatra mantra japa, and brāhmaṇa dakṣiṇā.",
  },
  daughter_after_three_sons: {
    title: "Trik-Prasava Janana",
    chapter: "BPHS Ch. 94",
    severity: "info",
    cause: "Birth of a child of differing gender immediately succeeding three of the opposite.",
    deity: "Brahma-Viṣṇu-Śiva",
    summary: "Trideva pūjā, gifts of grain mounds and ornaments to prevent familial discord.",
  },
  unusual_delivery: {
    title: "Unusual Presentation / Omens",
    chapter: "BPHS Ch. 95",
    severity: "warning",
    cause: "Irregular birth presentation, multiple births, or unusual natural portents.",
    deity: "Vedic Gāyatrī",
    summary: "Gāyatrī japa, 108 oblations of clarified butter into the sacred fire.",
  },
  family_nakshatra: {
    title: "Sajāti Janma (Shared Family Star)",
    chapter: "BPHS Ch. 96",
    severity: "info",
    cause: "Child born in the same birth nakṣatra as father, mother or an elder sibling.",
    deity: "Nakṣatra Devatā",
    summary: "Star deity worship, silver gifts and food distribution to brāhmaṇas.",
  },
  inauspicious_list: {
    title: "BPHS Inauspicious Birth Catalog",
    chapter: "BPHS Ch. 85–96",
    severity: "info",
    cause: "Comprehensive reference of Parāśara's remedial śānti chapters for birth moments.",
    deity: "Parāśara Ṛṣi Tradition",
    summary: "Systematic remedial measures addressing afflicted birth moments through Vedic rites.",
  },
};

/** Navagraha shrine order, east at top: Budha Śukra Candra / Guru Sūrya Maṅgala / Ketu Śani Rāhu. */
export const MANDALA = ["Mercury", "Venus", "Moon", "Jupiter", "Sun", "Mars", "Ketu", "Saturn", "Rahu"];
export const WEEKDAY_GRAHA = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"];
export const VASARA = ["Bhānu", "Soma", "Maṅgala", "Budha", "Guru", "Śukra", "Śani"];
export const SEVERITY = { critical: "Critical", warning: "Warning", info: "Advisory" } as const;
/** Conditions that depend on the family, which the chart alone cannot show. */
export const FAMILY = new Set(["family_nakshatra", "daughter_after_three_sons", "unusual_delivery"]);

export const fromBphs = (e: RemedyBphsEntry): Item => ({
  id: e.id, title: e.title, source: "BPHS", citation: `Ch. ${e.chapter}, vv. ${e.verses}`, translation: e.translation,
});
export const plural = (n: number, word: string) => `${n} ${word}${n === 1 ? "" : "s"}`;
export const words = new Intl.NumberFormat("en", { notation: "compact", compactDisplay: "long", maximumFractionDigits: 2 });
export const short = new Intl.NumberFormat("en", { notation: "compact", maximumFractionDigits: 2 });

/** Click and Enter/Space for SVG shapes that act as buttons. */
export const press = (label: string, f: () => void) => ({
  role: "button", tabIndex: 0, "aria-label": label, onClick: f,
  onKeyDown: (e: KeyboardEvent) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); f(); } },
});
