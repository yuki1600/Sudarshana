/** BPHS 45.30-37: the anka (1 to 5) of the first syllable of a name, counting the letters a, i, u, e, o and then
 *  ka, kha, ga, gha, nga, cha, ja, jha, ta, tha, da .. ha round 1 to 5 (BPHS's own list skips chha, nya and nna). */
// shortcut: reads an English spelling, where t/d/th/dh are taken as dental (ta 3, da 5, tha 4, dha 1), not retroflex (ta 4, da 1, tha 5, dha 2); the tab lets the reader pick the number instead
const SYLLABLES: [string, number][] = [
  ["chh", 1], ["ch", 1], ["kh", 2], ["gh", 4], ["jh", 3], ["th", 4], ["dh", 1], ["ph", 4], ["bh", 1], ["sh", 2],
  ["aa", 1], ["ai", 4], ["au", 5], ["ee", 2], ["oo", 3],
  ["a", 1], ["i", 2], ["u", 3], ["e", 4], ["o", 5],
  ["k", 1], ["c", 1], ["q", 1], ["x", 1], ["g", 3], ["j", 2], ["z", 2], ["t", 3], ["d", 5], ["n", 2], ["p", 3], ["f", 4], ["b", 5],
  ["m", 2], ["y", 3], ["r", 4], ["l", 5], ["v", 1], ["w", 1], ["s", 4], ["h", 5],
];

/** The first syllable of a name and its anka, or null when the name has no Latin letter to read. */
export function nameAnka(name: string): { syllable: string; n: number } | null {
  const word = name.toLowerCase().replace(/^[^a-z]+/, "");
  const hit = SYLLABLES.find(([s]) => word.startsWith(s));
  if (!hit) return null;
  const vowel = /^[aeiou]+/.exec(word.slice(hit[0].length))?.[0] ?? "";
  return { syllable: /^[aeiou]/.test(hit[0]) ? hit[0] : hit[0] + vowel.slice(0, 2), n: hit[1] };
}
