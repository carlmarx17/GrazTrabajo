// Modelo mínimo del frenado colisional de un haz de electrones en un bucle coronal.
// Relaciones de libro (Emslie 1978; Brown 1971). Es un esquema conceptual, no una
// salida de HYDRAD: sirve para que cada número que muestra la figura sea cierto en
// magnitud y para que el movimiento y la lectura vengan del mismo sitio.

// K = 2π e⁴ Λ con Λ ≈ 20, en unidades de keV² cm².
export const K = 2.6e-18;

export const MM = 1e8; // cm por Mm

// --- El bucle ------------------------------------------------------------
// Longitud total del bucle, de pie a pie por la corona. La guía usa 26 y 60 Mm.
export const LOOP_MM = 26;
export const HALF_MM = LOOP_MM / 2;

// Densidades. La atmósfera inicial de la guía: ápice ≈1.1 MK, n ≈1.6e9 cm⁻³.
export const N_CORONA = 1.6e9; // cm⁻³, corona relajada
export const N_BASE = 1e13; // cm⁻³, fondo de la cromosfera
export const H_CHROM = 0.25; // Mm, altura de escala cromosférica
export const S_TR = 2.0; // Mm, altura de la región de transición sobre el pie

export const T_CORONA = 1.1; // MK, ápice relajado

// Densidad a lo largo de la pata, s medido desde el pie (Mm).
export function density(s) {
  if (s >= S_TR) return N_CORONA;
  return Math.max(N_CORONA, N_BASE * Math.exp(-s / H_CHROM));
}

// Columna recorrida por el haz desde el ápice hasta la posición s (cm⁻²).
// El haz entra arriba y baja, así que se integra desde HALF_MM hacia s.
export function columnFrom(s, steps = 2000) {
  const from = Math.min(HALF_MM, Math.max(0, s));
  const h = (HALF_MM - from) / steps;
  let sum = 0;
  for (let i = 0; i < steps; i++) {
    const a = from + h * i;
    const b = a + h;
    sum += 0.5 * (density(a) + density(b)) * h * MM; // regla del trapecio
  }
  return sum;
}

// dE/dN = −K/E  ⇒  tras atravesar la columna N, un electrón de E keV conserva:
export const energyAfter = (E, N) => Math.sqrt(Math.max(0, E * E - 2 * K * N));

// ...y se detiene por completo tras la columna:
export const stoppingColumn = (E) => (E * E) / (2 * K);

// Posición de frenado (Mm sobre el pie) de un electrón de energía E keV.
// Busca por bisección la s donde la columna acumulada iguala la de frenado.
export function stopHeight(E) {
  const target = stoppingColumn(E);
  if (columnFrom(0) < target) return 0; // llega al fondo: blanco grueso cromosférico
  let lo = 0;
  let hi = HALF_MM;
  for (let i = 0; i < 60; i++) {
    const mid = (lo + hi) / 2;
    if (columnFrom(mid) > target) lo = mid;
    else hi = mid;
  }
  return (lo + hi) / 2;
}

// Formato compacto de una densidad de columna, para la lectura en vivo.
export function fmtColumn(N) {
  if (N <= 0) return "0";
  const e = Math.floor(Math.log10(N));
  const m = N / 10 ** e;
  const sup = String(e)
    .split("")
    .map((c) => "⁰¹²³⁴⁵⁶⁷⁸⁹"[Number(c)] ?? c)
    .join("");
  return `${m.toFixed(1)}×10${sup}`;
}
