// The textbook chakras' tables (Tara, Sapta Shalaka, Avakahada, Ghataka): what Wheels.tsx draws and Chakras.tsx reads.

/** The nine taras counted from the natal Moon's star, with what each does. */
export const TARA_NAMES = ["Janma", "Sampat", "Vipat", "Kshema", "Pratyak", "Sadhana", "Naidhana", "Mitra", "Parama Mitra"];
export const TARA_KIND = ["Mixed", "Good", "Bad", "Good", "Bad", "Good", "Bad", "Good", "Good"];

/** Sapta Shalaka: seven lines down and seven across; the 28 stars (Abhijit too) round their ends clockwise from Krittika at the top of the first. */
export const SHALAKA = ["Krit", "Rohi", "Mrig", "Ardr", "Puna", "Push", "Asre", "Magh", "PPha", "UPha", "Hast", "Chit", "Swat", "Visa",
  "Anu", "Jye", "Mool", "PSha", "USha", "Abhi", "Srav", "Dhan", "Sata", "PBha", "UBha", "Reva", "Aswi", "Bhar"];
/** The star at the other end of a star's line, which it pierces (Krittika and Shravana, Magha and Bharani ...). */
export const shalakaPartner = (star: string) => { const k = SHALAKA.indexOf(star); return SHALAKA[k < 7 || (k >= 14 && k < 21) ? 20 - k : 34 - k]; };
/** The first syllable of a name, by the Moon's pada at birth: Ashwini's four, Bharani's four ... (the common North Indian list). */
export const SYLLABLES = ["Chu", "Che", "Cho", "La", "Li", "Lu", "Le", "Lo", "A", "I", "U", "E", "O", "Va", "Vi", "Vu", "Ve", "Vo", "Ka", "Ki",
  "Ku", "Gha", "Ng", "Chha", "Ke", "Ko", "Ha", "Hi", "Hu", "He", "Ho", "Da", "Di", "Du", "De", "Do", "Ma", "Mi", "Mu", "Me",
  "Mo", "Ta", "Ti", "Tu", "Te", "To", "Pa", "Pi", "Pu", "Sha", "Na", "Tha", "Pe", "Po", "Ra", "Ri", "Ru", "Re", "Ro", "Ta",
  "Ti", "Tu", "Te", "To", "Na", "Ni", "Nu", "Ne", "No", "Ya", "Yi", "Yu", "Ye", "Yo", "Bha", "Bhi", "Bhu", "Dha", "Pha", "Dha",
  "Bhe", "Bho", "Ja", "Ji", "Khi", "Khu", "Khe", "Kho", "Ga", "Gi", "Gu", "Ge", "Go", "Sa", "Si", "Su", "Se", "So", "Da", "Di",
  "Du", "Tha", "Jha", "Na", "De", "Do", "Cha", "Chi"];

/** Ghataka Chakra, by the natal Moon's sign (Aries .. Pisces): the lunar month (0 Chaitra), tithi group (0 Nanda .. 4 Poorna), weekday (0 Sunday), the Moon's star (0 Ashwini) and the Moon's sign that are bad for the native. */
export const GHATAKA = {
  month: [7, 8, 3, 9, 2, 5, 10, 6, 4, 1, 0, 11],
  tithi: [0, 4, 1, 1, 2, 4, 3, 0, 2, 3, 2, 4],
  weekday: [0, 6, 1, 3, 6, 6, 4, 5, 5, 2, 4, 5],
  star: [9, 12, 14, 16, 18, 21, 23, 26, 1, 3, 5, 8],
  sign: [0, 5, 10, 4, 9, 2, 8, 1, 11, 4, 8, 10],
};
export const MONTHS = ["Chaitra", "Vaishakha", "Jyeshtha", "Ashadha", "Shravana", "Bhadrapada", "Ashwina", "Kartika", "Margashirsha", "Pausha", "Magha", "Phalguna"];
export const TITHI_GROUPS = ["Nanda (1 6 11)", "Bhadra (2 7 12)", "Jaya (3 8 13)", "Rikta (4 9 14)", "Poorna (5 10 15)"];
export const WEEKDAY_NAMES = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
/** What the Ghataka checks of a moment (the server's chakras.ghataka.day). */
export type GhatakaDay = { month: number; tithi: number; weekday: number; nakshatra: number; moon_sign: number };
/** Which of a moment's five are ghataka for a Moon sign, in GHATAKA's order. */
export const ghatakaHits = (sign: number, d: GhatakaDay) => [GHATAKA.month[sign] === d.month, GHATAKA.tithi[sign] === d.tithi % 15 % 5,
  GHATAKA.weekday[sign] === d.weekday, GHATAKA.star[sign] === d.nakshatra, GHATAKA.sign[sign] === d.moon_sign];
