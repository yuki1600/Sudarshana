import type { Display } from "./store";
import { languageOf, type LanguageId } from "./translate.ts";

// the Sanskrit short names (point_names.csv) and sign abbreviations
const SANSKRIT: Record<string, string> = { As: "Lg", Su: "Sy", Mo: "Ch", Ma: "Ma", Me: "Bu", Ju: "Gu", Ve: "Sk", Sa: "Sa", Ra: "Ra", Ke: "Ke" };
export const SANSKRIT_SIGNS = ["Mesh", "Vrish", "Mith", "Kark", "Simh", "Kany", "Tula", "Vris", "Dhan", "Maka", "Kumb", "Meen"];

// The charts in the language of Settings > Language. the names come from languageWords.ts
// (ui-languages-colours.md §5), so these are written by hand in Unicode: the lagna and grahas by their first letters, as Indian
// charts write them, Uranus to Pluto, Maandi and Gulika; the signs by name; a retrograde graha's (R) as (व), vakri. The other
// points (HL, GL, AL, A2 ...) stay Latin. languageWords.ts reads these too, so a table and a chart name a graha alike.
export const KEYS = ["As", "Su", "Mo", "Ma", "Me", "Ju", "Ve", "Sa", "Ra", "Ke", "Ur", "Ne", "Pl", "Md", "Gk"];
export const CHART_LABELS: Partial<Record<LanguageId, { bodies: string[]; signs: string[]; retro: string }>> = {
  Hindi: { bodies: ["ल", "सू", "चं", "मं", "बु", "गु", "शु", "श", "रा", "के", "यू", "ने", "प्लू", "मा", "गुलि"],
    signs: ["मेष", "वृषभ", "मिथुन", "कर्क", "सिंह", "कन्या", "तुला", "वृश्चिक", "धनु", "मकर", "कुम्भ", "मीन"], retro: "(व)" },
  Gujarati: { bodies: ["લ", "સૂ", "ચં", "મં", "બુ", "ગુ", "શુ", "શ", "રા", "કે", "યુ", "ને", "પ્લૂ", "મા", "ગુલિ"],
    signs: ["મેષ", "વૃષભ", "મિથુન", "કર્ક", "સિંહ", "કન્યા", "તુલા", "વૃશ્ચિક", "ધન", "મકર", "કુંભ", "મીન"], retro: "(વ)" },
  Marathi: { bodies: ["ल", "र", "चं", "मं", "बु", "गु", "शु", "श", "रा", "के", "यु", "ने", "प्लू", "मां", "गुलि"],
    signs: ["मेष", "वृषभ", "मिथुन", "कर्क", "सिंह", "कन्या", "तूळ", "वृश्चिक", "धनु", "मकर", "कुंभ", "मीन"], retro: "(व)" },
  Odia: { bodies: ["ଲ", "ର", "ଚ", "ମ", "ବୁ", "ଗୁ", "ଶୁ", "ଶ", "ରା", "କେ", "ୟୁ", "ନେ", "ପ୍ଲୁ", "ମା", "ଗୁଳି"],
    signs: ["ମେଷ", "ବୃଷ", "ମିଥୁନ", "କର୍କଟ", "ସିଂହ", "କନ୍ୟା", "ତୁଳା", "ବୃଶ୍ଚିକ", "ଧନୁ", "ମକର", "କୁମ୍ଭ", "ମୀନ"], retro: "(ବ)" },
  Bengali: { bodies: ["ল", "র", "চ", "ম", "বু", "বৃ", "শু", "শ", "রা", "কে", "ইউ", "নে", "প্লু", "মা", "গুলি"],
    signs: ["মেষ", "বৃষ", "মিথুন", "কর্কট", "সিংহ", "কন্যা", "তুলা", "বৃশ্চিক", "ধনু", "মকর", "কুম্ভ", "মীন"], retro: "(ব)" },
  Assamese: { bodies: ["ল", "ৰ", "চ", "ম", "বু", "বৃ", "শু", "শ", "ৰা", "কে", "ইউ", "নে", "প্লু", "মা", "গুলি"],
    signs: ["মেষ", "বৃষ", "মিথুন", "কৰ্কট", "সিংহ", "কন্যা", "তুলা", "বৃশ্চিক", "ধনু", "মকৰ", "কুম্ভ", "মীন"], retro: "(ব)" },
  Kannada: { bodies: ["ಲ", "ರ", "ಚಂ", "ಕು", "ಬು", "ಗು", "ಶು", "ಶ", "ರಾ", "ಕೇ", "ಯು", "ನೆ", "ಪ್ಲೂ", "ಮಾಂ", "ಗುಳಿ"],
    signs: ["ಮೇಷ", "ವೃಷಭ", "ಮಿಥುನ", "ಕರ್ಕಾಟಕ", "ಸಿಂಹ", "ಕನ್ಯಾ", "ತುಲಾ", "ವೃಶ್ಚಿಕ", "ಧನು", "ಮಕರ", "ಕುಂಭ", "ಮೀನ"], retro: "(ವ)" },
  Tamil: { bodies: ["ல", "சூ", "சந்", "செ", "பு", "கு", "சு", "சனி", "ரா", "கே", "யு", "நெ", "புளூ", "மா", "குளி"],
    signs: ["மேஷம்", "ரிஷபம்", "மிதுனம்", "கடகம்", "சிம்மம்", "கன்னி", "துலாம்", "விருச்சிகம்", "தனுசு", "மகரம்", "கும்பம்", "மீனம்"], retro: "(வ)" },
  Telugu: { bodies: ["ల", "ర", "చం", "కు", "బు", "గు", "శు", "శ", "రా", "కే", "యు", "నె", "ప్లూ", "మాం", "గుళి"],
    signs: ["మేషం", "వృషభం", "మిథునం", "కర్కాటకం", "సింహం", "కన్య", "తుల", "వృశ్చికం", "ధనుస్సు", "మకరం", "కుంభం", "మీనం"], retro: "(వ)" },
  Punjabi: { bodies: ["ਲ", "ਸੂ", "ਚੰ", "ਮੰ", "ਬੁ", "ਗੁ", "ਸ਼ੁ", "ਸ਼", "ਰਾ", "ਕੇ", "ਯੂ", "ਨੈ", "ਪਲੂ", "ਮਾ", "ਗੁਲਿ"],
    signs: ["ਮੇਖ", "ਬ੍ਰਿਖ", "ਮਿਥੁਨ", "ਕਰਕ", "ਸਿੰਘ", "ਕੰਨਿਆ", "ਤੁਲਾ", "ਬ੍ਰਿਸ਼ਚਕ", "ਧਨ", "ਮਕਰ", "ਕੁੰਭ", "ਮੀਨ"], retro: "(ਵ)" },
};
const labels = (d: Display) => CHART_LABELS[languageOf(d.language)];

/** A body's label as the chart shows it. The label stays the key of everything else (highlights, menus). */
/** A chart label's retrograde mark as the app writes it everywhere: the server's "SaR" shown as "Sa(R)". */
export const retroMark = (t: string) => t.replace(/^(Su|Mo|Ma|Me|Ju|Ve|Sa|Ra|Ke|Ur|Ne|Pl)R$/, "$1(R)");

export function shown(t: string, d: Display): string {
  const m = t.match(/^(As|Su|Mo|Ma|Me|Ju|Ve|Sa|Ra|Ke|Ur|Ne|Pl|Md|Gk)(R?)$/);
  if (!m) return retroMark(t);
  const l = labels(d);
  if (l) return l.bodies[KEYS.indexOf(m[1])] + (m[2] ? l.retro : "");
  const r = m[2] ? "(R)" : "";
  return (d.planets === "sanskrit" ? SANSKRIT[m[1]] ?? m[1] : m[1]) + r;
}

/** A sign's name as the charts write it: in the language, else its English abbreviation or its Sanskrit one. */
export const signName = (s: number, abbr: string, d: Display) => labels(d)?.signs[s] ?? (d.signs === "sanskrit" ? SANSKRIT_SIGNS[s] : abbr);
