/** What each slot, span and limb of the Muhurta tab means, for the dial's popups. Common usage, kept short. */

export const CHOGHADIYA: Record<string, [string, string]> = {
  Amrita: ["Moon", "Nectar. The best of the eight; good for any work."],
  Shubha: ["Jupiter", "Auspicious. Good for ceremonies, marriage and study."],
  Labha: ["Mercury", "Gain. Good for business, trade and learning."],
  Chara: ["Venus", "Moving. Good for travel and for work that keeps changing."],
  Udvega: ["Sun", "Anxiety. Avoid new starts; fair for government work."],
  Roga: ["Mars", "Disease. Avoid; only for disputes and competition."],
  Kala: ["Saturn", "Loss. Avoid new starts; work that is begun drags on."],
};

export const GOWRI: Record<string, string> = {
  Uthama: "Best. Good for every kind of work.",
  Amrutha: "Nectar. Highly auspicious.",
  Labha: "Gain. Good for money matters and trade.",
  Shubha: "Good. Suits auspicious beginnings.",
  Roga: "Disease. Avoid.",
  Bhaya: "Fear. Avoid.",
  Visha: "Poison. Avoid.",
  Chora: "Theft. Avoid; things go missing.",
};

export const HORA: Record<string, string> = {
  Sun: "Authority, government and dealings with seniors.",
  Moon: "Travel, the public, and anything to do with water and food.",
  Mars: "Disputes, sport, surgery and machinery. Avoid auspicious starts.",
  Mercury: "Study, writing, trade and agreements.",
  Jupiter: "Ceremonies, teaching, finance and worship.",
  Venus: "Marriage, the arts, buying clothes, jewellery and vehicles.",
  Saturn: "Labour, repairs and property work. Avoid new starts.",
};

export const SIGN_TYPE: Record<string, [string, string]> = Object.fromEntries(
  ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"].map((s, i) => [s, [
    ["Movable", "Fixed", "Dual"][i % 3],
    ["Movable signs suit travel and things meant to change.", "Fixed signs suit what should last: a home, a marriage, a foundation.", "Dual signs suit learning, the arts and most ceremonies."][i % 3],
  ]]),
) as Record<string, [string, string]>;

export const SPANS: Record<string, string> = {
  "Rahu Kalam": "Ruled by Rahu, an eighth of the daytime. Do not begin anything new.",
  "Yamaganda": "Ruled by Yama, an eighth of the daytime. Avoid new starts and travel.",
  "Gulika Kalam": "Ruled by Saturn's son Gulika: what is begun repeats. Avoid good starts.",
  "Dur Muhurta": "An inauspicious muhurta of this weekday, 1/15 of the daytime.",
  "Varjyam": "The poisonous part of the nakshatra, 4 of its 60 ghatis. Avoid.",
  "Bhadra (Vishti)": "The Vishti karana. Avoid auspicious work while it runs.",
  "Ganda Moola": "The Moon at a junction of water and fire signs. Take care with ceremonies for children.",
  "Panchak": "The Moon in Aquarius or Pisces. Avoid travel south, building roofs and gathering wood.",
  "Abhijit Muhurta": "The 8th muhurta of the day, around local noon. Good for all work (not on Wednesdays).",
  "Brahma Muhurta": "Two muhurtas before sunrise. Best for prayer, study and meditation.",
  "Sarvartha Siddhi": "The weekday and the nakshatra together bring success to all work.",
  "Amrit Siddhi": "A weekday and nakshatra pair that brings lasting results.",
  "Guru Pushya": "Pushya on a Thursday. Very good for buying gold, starting study and new ventures.",
  "Ravi Pushya": "Pushya on a Sunday. Good for buying, medicine and new ventures.",
  "Ravi Yoga": "The Moon's nakshatra well placed from the Sun's. Clears faults of the day.",
};

export const LIMBS: Record<string, string> = {
  Tithi: "The lunar day: each 12 degrees the Moon gains on the Sun.",
  Nakshatra: "The lunar mansion the Moon is passing through.",
  Yoga: "The sum of the Sun's and Moon's longitudes, in 27 parts.",
  Karana: "Half a tithi.",
  "Moon sign": "The sign the Moon is in.",
};

const TITHI_GROUP = ["Nanda (joy)", "Bhadra (well-being)", "Jaya (victory)", "Rikta (empty, avoided for good work)", "Purna (fullness)"];
const TITHIS = ["Pratipada", "Dvitiya", "Tritiya", "Chaturthi", "Panchami", "Shasthi", "Saptami", "Ashtami", "Navami", "Dashami", "Ekadashi", "Dvadashi", "Trayodashi", "Chaturdashi"];

/** "Nanda (joy)" .. for a tithi name as the server writes it ("Krishna Ekadashi", "Shukla Purnima"). */
export function tithiGroup(name: string): string {
  const t = name.split(" ").slice(1).join(" ");
  const n = t === "Purnima" || t === "Amavasya" ? 15 : TITHIS.indexOf(t) + 1;
  return n > 0 ? TITHI_GROUP[(n - 1) % 5] : "";
}

export const NAK_LORDS: Record<string, string> = Object.fromEntries(
  ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Moola", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta",
    "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"].map((n, i) => [n, ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"][i % 9]]),
);

export const WEEKDAY_LORD: Record<string, string> = { Sunday: "Sun", Monday: "Moon", Tuesday: "Mars", Wednesday: "Mercury", Thursday: "Jupiter", Friday: "Venus", Saturday: "Saturn" };
