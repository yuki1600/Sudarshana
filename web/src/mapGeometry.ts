// The world map's geometry: pure numbers, degrees in and out.
const RAD = Math.PI / 180;

/** The height of a parallel on a map whose meridians are straight: Natural Earth I's spacing, which draws the polar regions in, on the unit sphere. */
export function mapY(lat: number) {
  const p = lat * RAD, p2 = p * p, p4 = p2 * p2;
  return p * (1.007226 + p2 * (0.015085 + p4 * (-0.044475 + 0.028874 * p2 - 0.005916 * p4)));
}

export const HALF_HEIGHT = mapY(90);

/** An SVG path in degrees on the map's parallels: longitudes stay degrees, latitudes become mapY, downwards. */
export const drawn = (degrees: string) => degrees.replace(/(-?[\d.]+) (-?[\d.]+)/g, (_, lon, lat) => `${lon} ${(-mapY(+lat)).toFixed(4)}`);

/** The latitude at a height of ``mapY``; null off the map. */
export function latAt(y: number) {
  if (Math.abs(y) > HALF_HEIGHT) return null;
  let [lo, hi] = [-90, 90];
  for (let i = 0; i < 40; i++) { const mid = (lo + hi) / 2; if (mapY(mid) < y) lo = mid; else hi = mid; }
  return lo;
}

export const wrap = (lon: number) => ((lon + 180) % 360 + 360) % 360 - 180;

/** Where a curve running south to north crosses a latitude. */
export function lonAt(curve: number[][], lat: number) {
  const i = Math.max(1, curve.findIndex((p) => p[1] >= lat));
  const [[x0, y0], [x1, y1]] = [curve[i - 1], curve[i]];
  return x0 + (x1 - x0) * (lat - y0) / (y1 - y0);
}

const turn = (x: number) => ((x % 360) + 360) % 360;

/** The bhava a place falls in: the band (between curves i and i + 1) its longitude lies in at its latitude. 0 past the polar circles, where the curves end and the bands turn over. */
export function bhavaOf(bands: { house?: number; curve: number[][] }[], lon: number, lat: number) {
  if (Math.abs(lat) > 66) return 0;
  const i = bands.slice(0, -1).findIndex((b, j) => { const west = lonAt(b.curve, lat); return turn(lon - west) < turn(lonAt(bands[j + 1].curve, lat) - west); });
  return bands[i]?.house ?? 0;
}

/** Ascending positions moved as little as it takes to stand a width apart and within a limit: the mean of pushing them all right and all left keeps that distance. */
export function spread(xs: number[], width: number, limit: number) {
  const right = [...xs], left = [...xs], last = xs.length - 1;
  for (let i = 1; i <= last; i++) right[i] = Math.max(xs[i], right[i - 1] + width);
  for (let i = last - 1; i >= 0; i--) left[i] = Math.min(xs[i], left[i + 1] - width);
  return xs.map((_, i) => Math.max(-limit + i * width, Math.min(limit - (last - i) * width, (right[i] + left[i]) / 2)));
}
