import { useQuery } from "@tanstack/react-query";
import { api, type Birth } from "./api";
import { MixedGrid } from "./SouthGrid";
import { Loaded } from "./ui";

/** One division of two charts, nested (the mixed charts of Progressions and Transits; Mixed 2-Vargas takes two divisions of one chart). */
export function MixedChart({ outerBirth, outerName, innerBirth, innerName, outerDiv = 1, innerDiv = 1 }: {
  outerBirth: Birth; outerName: string; innerBirth: Birth; innerName: string; outerDiv?: number; innerDiv?: number;
}) {
  const q = useQuery({
    queryKey: ["mixed", outerBirth, innerBirth, outerDiv, innerDiv],
    queryFn: async () => {
      const [[o], [i]] = await Promise.all([api.vargas(outerBirth, [outerDiv]), api.vargas(innerBirth, [innerDiv])]);
      return { outer: { ...o, title: `${outerName} ${o.title}`.trim() }, inner: { ...i, title: `${innerName} ${i.title}`.trim() } };
    },
  });
  return <Loaded q={q}>{({ inner, outer }) => <MixedGrid inner={inner} outer={outer} />}</Loaded>;
}
