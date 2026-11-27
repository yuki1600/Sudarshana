/** The Predictions tab's questions and the plain helpers over its answers, so the tests can run them. */
import type { Birth } from "./api";

export type Answer = string | number | boolean;
export type Answers = Record<string, Answer>;
export interface LifeEvent { id: string; year: number; approx: boolean; kind: string; note: string }
/** What the account keeps for one chart: the answers by question id (a year's "≈" under `<id>.approx`), other dated events,
 *  and notes, free text (a Rodden library chart's biography and the rest of its file). */
export interface Facts { answers: Answers; events: LifeEvent[]; notes: string }
export const EMPTY: Facts = { answers: {}, events: [], notes: "" };

/** pick: one of the options, as its label; count: 0-3 or "Other"; year: a year, with "≈" for a rough one.
 *  Choosing "Other" in a pick or a count asks for text, kept under `<id>.other`. */
export interface Question { id: string; label: string; kind: "pick" | "count" | "year"; options?: string[]; show?: (a: Answers) => boolean }
export interface Section { title: string; questions: Question[] }

export const OTHER = "Other";
export const COUNTS = ["0", "1", "2", "3", OTHER];
const FIELDS = ["Engineering", "Medicine", "Science", "Commerce", "Arts", "Law", "Other"];
const is = (id: string, ...values: string[]) => (a: Answers) => values.includes(a[id] as string);

export const SECTIONS: Section[] = [
  { title: "Person", questions: [{ id: "gender", label: "Gender", kind: "pick", options: ["Male", "Female", "Other"] }] },
  { title: "Parents", questions: [
    { id: "father", label: "Father", kind: "pick", options: ["Alive", "Passed"] },
    { id: "father.year", label: "Father passed in", kind: "year", show: is("father", "Passed") },
    { id: "mother", label: "Mother", kind: "pick", options: ["Alive", "Passed"] },
    { id: "mother.year", label: "Mother passed in", kind: "year", show: is("mother", "Passed") }] },
  // elder ones are read from the 11th house, younger ones from the 3rd, so they are asked apart
  { title: "Siblings", questions: [
    { id: "elderBrothers", label: "Elder brothers", kind: "count" },
    { id: "elderSisters", label: "Elder sisters", kind: "count" },
    { id: "youngerBrothers", label: "Younger brothers", kind: "count" },
    { id: "youngerSisters", label: "Younger sisters", kind: "count" }] },
  { title: "Marriage", questions: [
    { id: "marriage", label: "Status", kind: "pick", options: ["Single", "Married", "Divorced", "Widowed", "Remarried"] },
    { id: "marriage.year", label: "Married in", kind: "year", show: is("marriage", "Married", "Divorced", "Widowed", "Remarried") },
    { id: "marriage.kind", label: "Kind", kind: "pick", options: ["Love", "Arranged"], show: is("marriage", "Married", "Divorced", "Widowed", "Remarried") }] },
  { title: "Children", questions: [
    { id: "sons", label: "Sons", kind: "count" },
    { id: "daughters", label: "Daughters", kind: "count" },
    { id: "children.year", label: "First child born", kind: "year", show: (a) => Number(a.sons ?? 0) + Number(a.daughters ?? 0) > 0 }] },
  { title: "Education", questions: [
    { id: "education", label: "Highest", kind: "pick", options: ["School", "Diploma", "Bachelor's", "Master's", "Doctorate"] },
    { id: "education.field", label: "Field", kind: "pick", options: FIELDS }] },
  { title: "Career", questions: [
    { id: "career", label: "Kind", kind: "pick", options: ["Job", "Government", "Business", "Profession", "Homemaker", "Student", "Retired"] },
    { id: "career.field", label: "Field", kind: "pick", options: [...FIELDS.slice(0, -1), "IT", "Finance", "Teaching", "Media", "Other"], show: (a) => !["Homemaker", "Student"].includes(a.career as string) },
    { id: "career.year", label: "Started in", kind: "year", show: is("career", "Job", "Government", "Business", "Profession", "Retired") }] },
  { title: "Abroad", questions: [
    { id: "abroad", label: "Abroad", kind: "pick", options: ["Never", "Travelled", "Settled"] },
    { id: "abroad.year", label: "First went in", kind: "year", show: is("abroad", "Travelled", "Settled") }] },
  { title: "Property and health", questions: [
    { id: "home", label: "Own home", kind: "pick", options: ["No", "Yes"] },
    { id: "home.year", label: "Bought in", kind: "year", show: is("home", "Yes") },
    { id: "illness", label: "Major illness or surgery", kind: "pick", options: ["None", "Yes"] },
    { id: "illness.year", label: "In", kind: "year", show: is("illness", "Yes") }] },
];

export const EVENT_KINDS = ["Accident", "Job change", "Move", "Loss", "Gain", "Spiritual", "Other"];

/** The chart the facts belong to: its name and birth date, not the time, so stepping the birth time keeps them. */
export const chartKey = (name: string, natal: Pick<Birth, "year" | "month" | "day">) =>
  `${name || "(untitled)"}|${natal.year}-${String(natal.month).padStart(2, "0")}-${String(natal.day).padStart(2, "0")}`;

/** The questions to ask now: those whose condition the answers so far meet. */
export const visible = (sections: Section[], a: Answers) => sections.flatMap((s) => s.questions).filter((q) => !q.show || q.show(a));

/** An answer as words: "Engineering", the text typed for "Other", "≈ 1884". */
export function answerText(q: Question, a: Answers): string | undefined {
  const v = a[q.id];
  if (v === undefined) return undefined;
  if (q.kind === "year") return `${a[`${q.id}.approx`] ? "≈ " : ""}${v}`;
  return v === OTHER ? String(a[`${q.id}.other`] ?? "") || OTHER : String(v);
}
