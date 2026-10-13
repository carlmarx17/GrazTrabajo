// Fig 1 — El escenario: qué pasa cuando una fulguración golpea un bucle.
// Banco de demostración: un tubo de flujo semicircular entre dos pies anclados en
// la cromosfera, con el cabezal inyector del haz en el ápice y un manómetro que lee
// la densidad coronal. Todo número viene de ./model.mjs.
//
//   node build.mjs            → fig1_escenario.html (tema oscuro)
//   node build.mjs --light    → fig1_escenario-light.html

import { writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import * as k from "../kit/iso-kit.mjs";
import { tubePieces, tubeSvg } from "../kit/tube.mjs";
import { kitScript } from "../scripts/inline-kit.mjs";
import * as m from "./model.mjs";

const HERE = dirname(fileURLToPath(import.meta.url));
const theme = process.argv.includes("--light") ? "light" : "dark";

const WIDTH = 660;
const HEIGHT = 430;

// --- Mundo ---------------------------------------------------------------
const PLATE = { x: -162, y: -54, w: 324, d: 108, r: 8 };
const PLATE_H = 12;
const FOOT_H = 5;

const R = 104; // radio del bucle en unidades de mundo
const Z0 = 11; // altura de los pies sobre la placa
const TUBE_R = 5.6;
const PLASMA_R = 3.1;

const apex = [0, 0, Z0 + R];
const pointAt = (th) => [Math.cos(th) * R, 0, Z0 + Math.sin(th) * R];
// Longitud de arco (unidades de mundo) ↔ posición física (Mm) desde el pie derecho.
const TOTAL = Math.PI * R;
const mmToArc = (s) => (s / m.LOOP_MM) * TOTAL;
const thetaAtMm = (s) => (Math.PI * s) / m.LOOP_MM;

const CHROM_ARC = mmToArc(m.S_TR); // los 2 Mm de cromosfera en cada pata

const MOUNT = (sign) => ({ x: sign * R - 26, y: -26, w: 52, d: 52, r: 4 });
const MOUNT_H = Z0;

const INJ = { x: -19, y: -15, w: 38, d: 30, r: 3 };
const INJ_Z = apex[2] + TUBE_R - 2;
const INJ_H = 15;

const POST = [0, 42];
const POST_Z = 196;
const GAUGE = [0, 4];
const GAUGE_R = 19;
const GAUGE_Z = 176;
const GAUGE_H = 9;
const GAUGE_TOP = GAUGE_Z + GAUGE_H;

// El haz: los tres números de beam_heating_model.cfg.
const F = 1e10; // erg cm⁻² s⁻¹
const EC = 20; // keV
const DELTA = 5;

const S_STOP = m.stopHeight(EC); // Mm sobre el pie
const N_STOP = m.columnFrom(S_STOP); // cm⁻² recorridas hasta frenar

const P = k.fitProjection(
  [
    ...k.boxCorners(PLATE, -PLATE_H - FOOT_H, 0),
    [POST[0], POST[1], POST_Z],
    [GAUGE[0] + GAUGE_R, GAUGE[1], GAUGE_TOP],
    [GAUGE[0] - GAUGE_R, GAUGE[1], GAUGE_TOP],
    [R + 10, 0, Z0],
    [-R - 10, 0, Z0],
  ],
  WIDTH,
  HEIGHT,
  { pad: 26, azimuth: 44 },
);

const at = (point) => k.iso(point, P);
const S = (paths, style) => k.solidSvg(paths, style);
const L = (d, style) => k.lineSvg(d, style);
const D = (points, style) => k.dotsSvg(points, style);
const byDepth = (points) => [...points].sort((a, b) => k.depthOf([a[0], a[1], 0], P) - k.depthOf([b[0], b[1], 0], P));

// --- La placa base: la fotosfera sobre la que se monta todo ---------------
function plate() {
  const out = [`<path class="iso-halo" d="${k.haloOf(PLATE, -PLATE_H - FOOT_H, PLATE_H, P)}"/>`];
  for (const [x, y] of byDepth(k.corners(PLATE, 24))) {
    out.push(S(k.cylinder(x, y, 7, -PLATE_H - FOOT_H, 1.6, P, 28), { tone: "lo" }));
    out.push(S(k.cylinder(x, y, 5.4, -PLATE_H - FOOT_H + 1.6, FOOT_H - 1.6, P, 28), { tone: "mid" }));
  }
  out.push(S(k.slabOf(PLATE, -PLATE_H, PLATE_H, P, 8, 1.6), { tone: "mid" }));
  out.push(L(k.planOutline(k.insetPlan(PLATE, 5), 0, P), { tone: "lo" }));
  const screws = k.corners(PLATE, 11);
  out.push(L(screws.map(([x, y]) => k.ring(x, y, 2.2, 0, P, 16)).join(""), { tone: "lo" }));
  out.push(D(screws.map(([x, y]) => at([x, y, 0])), { size: 0.5 }));

  // Regla: separación de los pies en Mm (2R de mundo ↔ el diámetro físico del bucle).
  const sepMm = (2 * m.LOOP_MM) / Math.PI;
  const strip = { x: -R, y: PLATE.y + PLATE.d - 16, w: 2 * R, d: 7, r: 1 };
  out.push(S(k.slabOf(strip, 0, 0.6, P, 3), { tone: "lo", crease: "none" }));
  const perMm = (2 * R) / sepMm;
  const ticks = k.topTicks(strip.x, strip.x + strip.w, perMm, 5, strip.y + 0.8, 0.6, [2, 3.6], P);
  out.push(L(ticks.minor, { tone: "lo" }), L(ticks.major, { tone: "mid" }));
  out.push(D([at([strip.x, strip.y + 3.5, 0.6]), at([strip.x + strip.w, strip.y + 3.5, 0.6])], { size: 0.45 }));

  // Placa de datos, con sus tres rayas grabadas.
  const label = { x: PLATE.x + 16, y: PLATE.y + 10, w: 46, d: 20, r: 2 };
  out.push(S(k.slabOf(label, 0, 1.1, P, 3, 0.3), { tone: "lo" }));
  for (const f of [0.3, 0.52, 0.74]) {
    out.push(L(k.lineOnTop([label.x + 5, label.y + label.d * f], [label.x + label.w - 5 - (f === 0.74 ? 12 : 0), label.y + label.d * f], 1.1, P), { tone: "faint" }));
  }
  out.push(D(k.corners(label, 3).map(([x, y]) => at([x, y, 1.1])), { size: 0.4, tone: "lo" }));
  return out.join("");
}

// --- Los dos pies: el anclaje en la cromosfera ---------------------------
function mounts() {
  const out = [];
  for (const sign of [-1, 1]) {
    const plan = MOUNT(sign);
    out.push(S(k.slabOf(plan, 0, MOUNT_H, P, 5, 0.8), { tone: "lo" }));
    out.push(L(k.planOutline(k.insetPlan(plan, 4), MOUNT_H, P), { tone: "faint" }));
    out.push(D(k.corners(plan, 7).map(([x, y]) => at([x, y, MOUNT_H])), { size: 0.45, tone: "lo" }));
    // Collar por donde el tubo entra en el pie.
    out.push(S(k.cylinder(sign * R, 0, TUBE_R + 3.4, MOUNT_H, 7, P, 32, 0.6), { tone: "mid" }));
    out.push(L(k.ring(sign * R, 0, TUBE_R + 1.2, MOUNT_H + 7, P, 32), { tone: "faint" }));
    out.push(D([0, 1, 2, 3].map((i) => {
      const a = (i * Math.PI) / 2 + Math.PI / 4;
      return at([sign * R + Math.cos(a) * (TUBE_R + 2.3), Math.sin(a) * (TUBE_R + 2.3), MOUNT_H + 7]);
    }), { size: 0.45, tone: "lo" }));
  }
  return out.join("");
}

// --- El tubo de flujo ----------------------------------------------------
const STEPS = 180;
const route = Array.from({ length: STEPS + 1 }, (_, i) => pointAt((Math.PI * i) / STEPS));
const COLLAR = 8; // arco tapado por el collar en cada extremo

const tube = tubePieces(route, TUBE_R, P, {
  maxLength: 13,
  gaps: [
    [0, COLLAR],
    [TOTAL - COLLAR, TOTAL],
  ],
});

// El plasma dentro del tubo, en celdas de 1 Mm: la malla del modelo 1D.
const plasma = tubePieces(route, PLASMA_R, P, {
  maxLength: mmToArc(1),
  gaps: [
    [0, COLLAR],
    [TOTAL - COLLAR, TOTAL],
  ],
});

// Arco medido desde el pie derecho (θ = 0) → Mm sobre ese pie.
const arcToMm = (arc) => (arc / TOTAL) * m.LOOP_MM;

function loop() {
  const items = [];
  for (const piece of tube) items.push({ mid: piece.mid, svg: tubeSvg(piece, { tone: "hi" }) });
  for (const [i, piece] of plasma.entries()) {
    const sMm = arcToMm((piece.from + piece.to) / 2);
    items.push({
      mid: piece.mid,
      svg: `<g data-cell="${i}" data-mm="${sMm.toFixed(2)}" style="opacity:0">${tubeSvg(piece, { tone: "lit" })}</g>`,
    });
  }
  return items
    .sort((a, b) => k.depthOf(a.mid, P) - k.depthOf(b.mid, P))
    .map((item) => item.svg)
    .join("");
}

// --- La cromosfera: manguito graduado sobre los 2 Mm bajos de cada pata ---
function chromosphere() {
  const out = [];
  for (const sign of [1, -1]) {
    const inner = sign > 0 ? 0 : Math.PI;
    for (let j = 0; j <= 4; j++) {
      const sMm = (j * m.S_TR) / 4;
      const th = sign > 0 ? thetaAtMm(sMm) : Math.PI - thetaAtMm(sMm);
      const p = pointAt(th);
      const long = j % 2 === 0;
      const r0 = TUBE_R + 0.6;
      const r1 = TUBE_R + (long ? 5.2 : 3.4);
      const nx = Math.cos(th);
      const nz = Math.sin(th);
      out.push(
        L(
          `M ${at([p[0] + nx * r0, 0, p[2] + nz * r0]).join(" ")} L ${at([p[0] + nx * r1, 0, p[2] + nz * r1]).join(" ")}`,
          { tone: long ? "mid" : "lo" },
        ),
      );
      void inner;
    }
  }
  return out.join("");
}

// --- El cabezal inyector: el haz entra como tres números ------------------
function injector() {
  const out = [];
  out.push(S(k.slabOf(INJ, INJ_Z, INJ_H, P, 5, 0.8), { tone: "mid" }));
  out.push(L(k.planOutline(k.insetPlan(INJ, 4), INJ_Z + INJ_H, P), { tone: "faint" }));
  out.push(D(k.corners(INJ, 5).map(([x, y]) => at([x, y, INJ_Z + INJ_H])), { size: 0.45, tone: "lo" }));
  // Tres perillas moleteadas: F, Ec y δ.
  const knobs = [
    [INJ.x + 9, INJ.y + 9, "F"],
    [INJ.x + 19, INJ.y + 21, "Ec"],
    [INJ.x + 29, INJ.y + 9, "d"],
  ];
  for (const [x, y, name] of byDepth(knobs)) {
    out.push(S(k.cylinder(x, y, 3.6, INJ_Z + INJ_H, 3.4, P, 24), { tone: "mid" }));
    out.push(L(k.knurl(x, y, 3.6, INJ_Z + INJ_H, INJ_Z + INJ_H + 3.4, 22, P), { tone: "lo" }));
    out.push(L(k.lineOnTop([x, y], [x + 3.6, y], INJ_Z + INJ_H + 3.4, P), { tone: "hi" }));
    out.push(D([at([x, y, INJ_Z + INJ_H + 3.4])], { size: 0.45, tone: "hi" }));
    void name;
  }
  // Boquilla: por donde el haz entra en el tubo.
  out.push(S(k.cylinder(0, 0, 4.2, INJ_Z - 5, 5.4, P, 24), { tone: "mid" }));
  out.push(L(k.ring(0, 0, 3, INJ_Z - 5, P, 24), { tone: "faint" }));
  return out.join("");
}

// --- El poste, el brazo y el manómetro de densidad coronal ---------------
function stand() {
  const out = [];
  const base = { x: POST[0] - 17, y: POST[1] - 15, w: 34, d: 30, r: 3 };
  out.push(S(k.slabOf(base, 0, 13, P, 5, 0.8), { tone: "lo" }));
  out.push(D(k.corners(base, 6).map(([x, y]) => at([x, y, 13])), { size: 0.45, tone: "lo" }));
  out.push(S(k.cylinder(POST[0], POST[1], 5.4, 13, 7, P, 28), { tone: "mid" }));
  out.push(S(k.cylinder(POST[0], POST[1], 3.4, 20, POST_Z - 20, P, 28), { tone: "mid", crease: "none" }));
  for (const z of [70, 120, 168]) out.push(L(k.sideArc(POST[0], POST[1], 3.4, z, P, 16), { tone: "faint" }));
  out.push(S(k.cylinder(POST[0], POST[1], 4.2, POST_Z, 2.4, P, 28), { tone: "mid" }));
  // Abrazadera y brazo hacia el ápice.
  const clamp = { x: POST[0] - 7.5, y: POST[1] - 7.5, w: 15, d: 15, r: 2.5 };
  out.push(S(k.slabOf(clamp, GAUGE_Z - 6, 12, P, 4, 0.6), { tone: "mid" }));
  const arm = { x: -3, y: GAUGE[1], w: 6, d: POST[1] - GAUGE[1], r: 2 };
  out.push(S(k.slabOf(arm, GAUGE_Z - 2, 4.4, P, 4, 0.5), { tone: "mid" }));
  out.push(D([at([0, POST[1] - 11, GAUGE_Z + 2.4]), at([0, GAUGE[1] + 7, GAUGE_Z + 2.4])], { size: 0.45, tone: "lo" }));
  // Tornillo de apriete.
  const thumb = [clamp.x + 7.5, clamp.y + clamp.d + 3.2];
  out.push(S(k.cylinder(thumb[0], thumb[1], 2.8, GAUGE_Z - 4, 6, P, 20), { tone: "mid" }));
  out.push(L(k.knurl(thumb[0], thumb[1], 2.8, GAUGE_Z - 4, GAUGE_Z + 2, 18, P), { tone: "lo" }));
  return out.join("");
}

function gauge() {
  const out = [];
  const [x, y] = GAUGE;
  out.push(S(k.cylinder(x, y, 3, GAUGE_Z - 10, 10, P, 20), { tone: "mid" }));
  out.push(S(k.cylinder(x, y, GAUGE_R, GAUGE_Z, GAUGE_H, P, 64, 0.8), { tone: "hi", crease: "lo" }));
  out.push(L(k.knurl(x, y, GAUGE_R, GAUGE_TOP - 3.2, GAUGE_TOP, 80, P, 0.3), { tone: "lo" }));
  out.push(L(k.sideArc(x, y, GAUGE_R, GAUGE_TOP - 3.2, P, 40), { tone: "faint" }));
  out.push(L(k.ring(x, y, GAUGE_R - 2.2, GAUGE_TOP, P, 64), { tone: "lo" }));
  const ticks = k.radialTicks(x, y, GAUGE_R - 3, 40, 5, GAUGE_TOP, [1.3, 2.8], P);
  out.push(L(ticks.minor, { tone: "lo" }), L(ticks.major, { tone: "mid" }));
  out.push(L(k.ring(x, y, 1.6, GAUGE_TOP, P, 16), { tone: "mid" }));
  out.push(k.faceTextSvg(k.topMatrix([x, y + 9.5], GAUGE_TOP, P, "x"), "log n", { size: 2.4, tone: "lo", anchor: "middle" }));
  return out.join("");
}

// El haz: una cuenta que baja por la pata derecha, y la marca de frenado.
function beam() {
  return [
    S(k.cylinder(0, 0, 2.4, Z0 + R - 2.4, 4.8, P, 20), { tone: "hi", lit: true }),
  ].join("");
}

// --- La figura -----------------------------------------------------------
const needleAt = (turn) => {
  const angle = turn * Math.PI * 2;
  const [x, y] = GAUGE;
  return k.lineOnTop(
    [x - Math.sin(angle) * 3.2, y + Math.cos(angle) * 3.2],
    [x + Math.sin(angle) * (GAUGE_R - 4), y - Math.cos(angle) * (GAUGE_R - 4)],
    GAUGE_TOP + 0.2,
    P,
  );
};

const stopPoint = pointAt(thetaAtMm(S_STOP));

const svg = k.figureSvg({
  width: WIDTH,
  height: HEIGHT,
  label:
    "Un banco con un tubo de flujo semicircular de 26 Mm montado entre dos pies anclados en la cromosfera. Un cabezal en el ápice inyecta un haz de electrones descrito por tres números; la cuenta iluminada baja por la pata derecha y se detiene a 0.3 Mm sobre el pie, donde la columna atravesada iguala la columna de frenado. Después el tubo se llena de plasma evaporado desde los dos pies y el manómetro sube.",
  body: [
    plate(),
    stand(),
    mounts(),
    loop(),
    chromosphere(),
    `<g data-part="beam" transform="${k.translateAlong(P, [0, 0, 0])}">${beam()}</g>`,
    injector(),
    gauge(),
    `<path data-part="needle" class="iso-line" data-tone="lit" data-free="start" d="${needleAt(0)}" style="stroke-width:1.1"/>`,
  ],
});

const live = `
const P = ${JSON.stringify(P)};
const R = ${R}, Z0 = ${Z0}, TOTAL = ${TOTAL}, LOOP_MM = ${m.LOOP_MM};
const GAUGE = ${JSON.stringify(GAUGE)}, GAUGE_R = ${GAUGE_R}, GAUGE_TOP = ${GAUGE_TOP};
const S_STOP = ${S_STOP}, N_STOP = ${N_STOP}, EC = ${EC};
const N_CORONA = ${m.N_CORONA}, N_FULL = 8.3e10;
const apex = ${JSON.stringify(apex)};
const stage = document.querySelector(".iso-stage");
const svg = stage.querySelector("svg");
const beam = svg.querySelector('[data-part="beam"]');
const needle = svg.querySelector('[data-part="needle"]');
const cells = [...svg.querySelectorAll('[data-cell]')].map((node) => ({ node, mm: Number(node.dataset.mm) }));
const readout = document.querySelector("[data-readout]");
const still = matchMedia("(prefers-reduced-motion: reduce)");
const clamp = (value, low, high) => Math.min(high, Math.max(low, value));
const pointAt = (th) => [Math.cos(th) * R, 0, Z0 + Math.sin(th) * R];
const thetaAtMm = (s) => (Math.PI * s) / LOOP_MM;
const needleAt = ${needleAt.toString().replaceAll("k.lineOnTop", "lineOnTop")};
const fmt = (N) => {
  const e = Math.floor(Math.log10(N));
  const sup = String(e).split("").map((c) => "⁰¹²³⁴⁵⁶⁷⁸⁹"[Number(c)] ?? c).join("");
  return (N / 10 ** e).toFixed(1) + "×10" + sup;
};
let t = 0, target = 0, touring = true, visible = false, frame = 0, last = 0, idle = 0;
function draw() {
  // Fase 1 (0→0.30): el haz baja del ápice al punto de frenado.
  // Fase 2 (0.30→0.46): frena. Fase 3 (0.46→1): evaporación.
  const fall = clamp(t / 0.30, 0, 1);
  const mm = (LOOP_MM / 2) * (1 - fall) + S_STOP * fall;
  const here = pointAt(thetaAtMm(mm));
  beam.setAttribute("transform", translateAlong(P, [here[0] - apex[0], 0, here[2] - apex[2]]));
  const fill = clamp((t - 0.46) / 0.54, 0, 1);
  const front = fill * (LOOP_MM / 2);
  for (const cell of cells) {
    const from = Math.min(cell.mm, LOOP_MM - cell.mm); // Mm sobre el pie más cercano
    const on = clamp((front - from) / 1.2, 0, 1);
    cell.node.style.opacity = String(on * 0.85);
  }
  const n = N_CORONA * (N_FULL / N_CORONA) ** fill;
  const turn = (Math.log10(n) - 9) / 2;
  needle.setAttribute("d", needleAt(turn));
  let text;
  if (t < 0.30) text = "el haz baja · N recorrida " + fmt(colAt(mm)) + " cm⁻²";
  else if (t < 0.46) text = "frena a " + S_STOP.toFixed(2) + " Mm sobre el pie · N = " + fmt(N_STOP) + " cm⁻²";
  else text = "evaporación · n corona " + fmt(n) + " cm⁻³";
  if (readout.textContent !== text) readout.textContent = text;
  stage.setAttribute("aria-valuenow", String(Math.round(t * 100)));
  stage.setAttribute("aria-valuetext", text);
}
// Columna recorrida desde el ápice hasta mm, con el mismo perfil que model.mjs.
const N_BASE = ${m.N_BASE}, H_CHROM = ${m.H_CHROM}, S_TR = ${m.S_TR}, MM = ${m.MM};
const density = (s) => (s >= S_TR ? N_CORONA : Math.max(N_CORONA, N_BASE * Math.exp(-s / H_CHROM)));
function colAt(s) {
  const from = clamp(s, 0, LOOP_MM / 2);
  const steps = 400, h = (LOOP_MM / 2 - from) / steps;
  let sum = 0;
  for (let i = 0; i < steps; i++) sum += 0.5 * (density(from + h * i) + density(from + h * (i + 1))) * h * MM;
  return Math.max(sum, 1);
}
function tick(now) {
  const dt = last ? Math.min((now - last) / 1000, 1 / 30) : 1 / 60;
  last = now;
  if (touring) target = (target + dt / 7) % 1;
  t = still.matches ? target : t + (target - t) * (1 - Math.exp(-dt / 0.2));
  if (Math.abs(target - t) < 0.0005) t = target;
  draw();
  frame = visible ? requestAnimationFrame(tick) : 0;
}
const run = () => { if (!frame && visible) { last = 0; frame = requestAnimationFrame(tick); } };
const steer = (next) => { touring = false; target = clamp(next, 0, 1); clearTimeout(idle); idle = setTimeout(() => { touring = !still.matches; run(); }, 3600); run(); };
new IntersectionObserver((entries) => { visible = entries[entries.length - 1].isIntersecting; if (visible) run(); }, { rootMargin: "120px 0px" }).observe(stage);
if (still.matches) touring = false;
stage.addEventListener("pointermove", (event) => {
  const box = svg.getBoundingClientRect();
  steer(clamp(((event.clientX - box.left) / box.width - 0.12) / 0.76, 0, 1));
});
stage.addEventListener("keydown", (event) => {
  let to = null;
  if (event.key === "ArrowRight" || event.key === "ArrowUp") to = target + 0.08;
  if (event.key === "ArrowLeft" || event.key === "ArrowDown") to = target - 0.08;
  if (event.key === "Home") to = 0;
  if (event.key === "End") to = 1;
  if (to === null) return;
  event.preventDefault();
  steer(to);
});
draw();
`;

const body = k.plateHtml({
  fig: "Fig 1",
  title: "El escenario",
  hint: "Recorre la secuencia con el puntero",
  readout: "el haz baja · N recorrida 1.0×10⁰ cm⁻²",
  keys: [
    { mark: "lit", label: "El haz y el plasma evaporado: lo que se mueve" },
    { mark: "raised", label: `Bucle de ${m.LOOP_MM} Mm; cromosfera, los ${m.S_TR} Mm graduados de cada pata` },
  ],
  caption:
    `Esquema conceptual, no una salida de HYDRAD. El haz entra en el ápice como tres números (F = 1e10 erg cm⁻² s⁻¹, Ec = ${EC} keV, δ = ${DELTA}) y baja perdiendo energía por colisiones de Coulomb: dE/dN = −K/E. La corona relajada (n = 1.6×10⁹ cm⁻³) solo aporta 1.8×10¹⁸ cm⁻², así que no lo frena; el haz se detiene a ${S_STOP.toFixed(2)} Mm sobre el pie, ya en la cromosfera, tras atravesar ${m.fmtColumn(N_STOP)} cm⁻². El plasma calentado se evapora y llena el tubo desde los dos pies.`,
  body: `<div class="iso-stage" tabindex="0" role="slider" aria-label="Secuencia de la fulguración: las flechas recorren el tiempo" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0">${svg}</div>`,
});

const file = theme === "light" ? "fig1_escenario-light.html" : "fig1_escenario.html";
writeFileSync(join(HERE, file), k.pageHtml({ title: "Fig 1 — El escenario", theme, body, script: kitScript() + live }));
console.log("wrote", file);
