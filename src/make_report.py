"""Builds docs/02_informe_experimentos_pulsos.html (single file, figures embedded).

Every number in the tables is read from the experiment objects, never typed.
"""
from __future__ import annotations

import base64
import math
import os

from beam_tables import KEV_TO_ERG, build_table, naive_table
from experiments import BaseCase, build_experiments

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "..", "docs", "figures")
OUT = os.path.join(HERE, "..", "docs", "02_informe_experimentos_pulsos.html")


def img(name: str, alt: str) -> str:
    with open(os.path.join(FIG, name), "rb") as fh:
        b64 = base64.b64encode(fh.read()).decode()
    return '<figure><img src="data:image/png;base64,%s" alt="%s"></figure>' % (b64, alt)


def sci(x: float, d: int = 3) -> str:
    m, e = ("%.*e" % (d - 1, x)).split("e")
    return "%s×10<sup>%d</sup>" % (m, int(e))


def main() -> None:
    base = BaseCase()
    exps = build_experiments(base)
    ps = base.pulses()
    p = ps[0]
    good, bad = build_table(ps, base.ramp), naive_table(ps)
    n_arcsec2 = base.area_cm2 / (7.25e7) ** 2
    avg_e = p.ec_kev * (p.delta - 1) / (p.delta - 2)

    rows = ""
    descr = {
        "E1_single_relaxed": ("1 tubo, 1 pulso", "Respuesta de referencia a un pulso sobre una atmósfera sin historia."),
        "E2_same_strand": ("1 tubo, %d pulsos" % base.n_pulses, "Recalentamiento: estado del solver conservado entre pulsos."),
        "E3a_independent_same_flux": ("%d tubos, 1 pulso c/u" % base.n_pulses, "Filamentos independientes con el mismo F por pulso (área emisora total mayor)."),
        "E3b_independent_equal_area": ("%d tubos, 1 pulso c/u" % base.n_pulses, "Filamentos independientes con el área repartida: F×%d por pulso, área total igual a E2." % base.n_pulses),
        "E4_continuous": ("1 tubo, 1 pulso largo", "Misma energía repartida uniformemente: control de la distribución temporal."),
        "E5_relaxation": ("1 tubo, 1 pulso", "Primer pulso y enfriamiento: separa el residuo de la respuesta al pulso nuevo."),
    }
    for e in exps:
        m = e.manifest()
        pk = max(c["peak_flux_erg_cm2_s"] for c in m["components"])
        rows += ("<tr><td><b>%s</b><br><span class='sm'>%s</span></td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
                 % (e.name, e.title, descr[e.name][0], sci(m["total_energy_erg"]), sci(m["total_emitting_area_cm2"]),
                    sci(pk), descr[e.name][1]))

    # neutral / ionized stopping-column ratio at the reference Ec (same expression as heat.cpp)
    e_avg = p.ec_kev * KEV_TO_ERG * (p.delta - 1) / (p.delta - 2)
    lam1 = 66.0 + 1.5 * math.log(e_avg) - 0.5 * math.log(1e11)
    lam2 = 25.1 + math.log(e_avg)
    nc = lambda g: (p.ec_kev * KEV_TO_ERG) ** 2 / (g * 1.0006128424679109e-36)
    nc_n, nc_i = nc(lam2), nc(lam1)

    html = """<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Informe: pulsos sucesivos y memoria cromosférica</title>
<style>
:root{--bg:#fff;--fg:#1d2430;--mut:#5b6575;--ln:#d9dee6;--acc:#1f4e79;--warn:#fff4e0;--wb:#e0a030;--ok:#e8f5ec;--okb:#1b7a3d;--tb:#f4f6f9}
@media (prefers-color-scheme:dark){:root{--bg:#14171c;--fg:#e4e8ee;--mut:#9aa5b5;--ln:#2e3540;--acc:#7fb2e5;--warn:#2d2616;--wb:#b88a2a;--ok:#16281d;--okb:#4cae6e;--tb:#1c2027}
figure img{background:#fff;border-radius:6px}}
body{background:var(--bg);color:var(--fg);font:16px/1.55 -apple-system,Segoe UI,Helvetica,Arial,sans-serif;margin:0}
main{max-width:920px;margin:0 auto;padding:28px 18px 60px}
h1{font-size:1.65rem;margin:.2em 0 .1em}h2{font-size:1.25rem;margin:2em 0 .5em;border-bottom:1px solid var(--ln);padding-bottom:.25em;color:var(--acc)}
h3{font-size:1.02rem;margin:1.4em 0 .3em}
p,li{max-width:75ch}.sub{color:var(--mut);margin:0 0 1.2em}
table{border-collapse:collapse;width:100%%;font-size:.9rem;margin:.8em 0}
th,td{border:1px solid var(--ln);padding:6px 8px;text-align:left;vertical-align:top}th{background:var(--tb)}
.sm{color:var(--mut);font-size:.82rem}
code,.mono{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:.88em}
.eq{background:var(--tb);border-left:3px solid var(--acc);padding:.5em .9em;margin:.8em 0;overflow-x:auto}
.box{padding:.7em 1em;border-radius:6px;margin:1em 0;border-left:4px solid}
.warn{background:var(--warn);border-color:var(--wb)}.ok{background:var(--ok);border-color:var(--okb)}
figure{margin:1em 0}figure img{max-width:100%%;height:auto}
figcaption{color:var(--mut);font-size:.86rem}
.tablewrap{overflow-x:auto}
</style></head><body><main>

<h1>Pulsos sucesivos de electrones y memoria cromosférica</h1>
<p class="sub">Informe de la infraestructura de experimentos (puntos 1 y 2 del plan) · generado el 2026-10-01 · todos los parámetros son <b>sintéticos</b></p>

<div class="box warn"><b>Alcance.</b> Este informe describe qué se quiere simular y deja listas las entradas de los cinco experimentos
con energía comparable. <b>No contiene resultados observacionales ni conclusiones físicas.</b> Los parámetros del haz son valores
ilustrativos, no ajustes de STIX; ningún evento ha sido seleccionado.</div>

<h2>1. Qué se quiere responder</h2>
<p><b>¿Cómo responde la atmósfera al segundo o tercer pulso de electrones</b>, cuando los pulsos están fijados por espectros reales de STIX, y en qué se diferencia esa respuesta de la de un primer pulso sobre una atmósfera relajada?
Interesan la profundidad de deposición, la temperatura, la densidad, la velocidad, la ionización y el reparto energético. Como comparación secundaria: distinguir el recalentamiento del mismo tubo de la activación de <b>filamentos independientes</b> compatibles con la misma señal de rayos X duros.
El diseño completo (hipótesis, objetivos, métodos y entregables) está en <code>docs/00_objetivos_y_metodologia.md</code>.</p>
%(fig0)s
<p>Hipótesis de trabajo (aún por confirmar con la profesora): los «impactos» son pulsos de electrones sobre el mismo tubo de flujo. Es una hipótesis, no una evidencia.
Un límite de detectabilidad bien establecido —casos en que los escenarios no se pueden distinguir— también sería un resultado.</p>

<h2>2. Física del forzamiento</h2>
<p>Cada pulso se describe como un haz de electrones con ley de potencias en número, por encima de una energía de corte Ec, que se frena colisionalmente
(blanco grueso). Para un índice δ &gt; 2 y sin corte superior:</p>
<div class="eq mono">P = Ṅ · Ec · (δ − 1)/(δ − 2)  [erg s⁻¹] &nbsp;&nbsp;&nbsp; F = P / A  [erg cm⁻² s⁻¹]</div>
<table><tr><th>Magnitud</th><th>Símbolo y unidad</th><th>Nota</th></tr>
<tr><td>Tasa de electrones sobre Ec</td><td>Ṅ [s⁻¹]</td><td>Lo que ajusta el espectro de fotones, junto con Ec y δ</td></tr>
<tr><td>Potencia del haz</td><td>P [erg s⁻¹]</td><td>Es lo que se conserva al comparar escenarios</td></tr>
<tr><td>Flujo de energía</td><td>F [erg cm⁻² s⁻¹]</td><td>Entrada de HYDRAD; depende del área A del tubo, que STIX no fija</td></tr>
<tr><td>Deposición volumétrica</td><td>Q(s,t) [erg cm⁻³ s⁻¹]</td><td>Salida que calcula el solver; es lo que calienta</td></tr></table>
<p>Condiciones respetadas: Ec se convierte de keV a erg (1 keV = 1.602×10⁻⁹ erg); δ ≤ 2 se rechaza porque la energía media diverge; Ec y δ del
fotón no se intercambian con los del electrón. Con los valores base, la energía media por electrón es %(avg_e).1f keV.</p>

<h3>Dónde se frena el haz</h3>
<p>La columna de frenado N<sub>c</sub> crece como Ec² y depende del estado del gas. Con la expresión de <code>Heating_Model/source/heat.cpp</code>, para
Ec = %(ec).0f keV y δ = %(delta).0f, N<sub>c</sub> ≈ %(ncn)s cm⁻² en gas neutro y ≈ %(nci)s cm⁻² en gas ionizado (×%(ratio).1f). Un pulso que ioniza o comprime
el plasma cambia por tanto <i>dónde</i> deposita energía el siguiente: este es uno de los canales físicos de la «memoria» que se quiere medir.</p>
%(fig1)s

<div class="box warn"><b>Límites del modelo de haz de HYDRAD.</b> Es el calentamiento colisional analítico de Hawley &amp; Fisher con incidencia normal fija (μ₀ = 1):
sin dispersión de ángulo de paso, sin corriente de retorno y sin transporte Fokker–Planck. Además la radiación de la configuración enviada es ópticamente delgada, sin NLTE ni Hα.
Sirve para probar la mecánica de pulsos y la evaporación hacia la corona; no para decidir la memoria cromosférica, para lo que se prefiere RADYN+FP.</div>

<h2>3. Cómo se codifican los pulsos para HYDRAD</h2>
<p>HYDRAD lee filas (t, F, Ec, δ), <b>interpola las tres magnitudes linealmente</b> entre filas y apaga el haz antes de la primera y después de la última.
Una codificación de dos filas por pulso parece natural, pero rellena el hueco entre pulsos. Con los parámetros base inyectaría
%(ebad)s erg cm⁻² frente a los %(egood)s correctos (×%(rat).1f).</p>
%(fig2)s
<p>El generador (<code>src/beam_tables.py</code>) usa filas con F = 0 y una rampa de %(ramp).1f s <b>centrada</b> en cada frontera, de modo que ∫F dt = F·duración exactamente.
Exige además: pulsos más largos que la rampa, huecos mayores que la rampa, inicio ≥ rampa/2 (el tiempo de HYDRAD empieza en 0), una única área por tabla
(F solo tiene sentido para un tubo) y δ &gt; 2 en toda fila, incluidas las de F = 0, para que la interpolación nunca cruce δ = 2.</p>

<h2>4. La matriz de experimentos</h2>
<p>Los cinco experimentos del plan, con la fragmentación en filamentos generada con <b>dos asignaciones de área</b> porque los rayos X duros fijan P(t) pero no A.
Parámetros base (sintéticos): Ṅ = %(ndot)s s⁻¹, Ec = %(ec).0f keV, δ = %(delta).0f, %(npul)d pulsos de %(dur).0f s separados %(gap).0f s, A<sub>ref</sub> = %(area)s cm²
(≈ %(arc).0f arcsec² a 1 UA), lo que da P = %(pw)s erg s⁻¹ y F = %(fl)s erg cm⁻² s⁻¹ por pulso.</p>
<div class="tablewrap"><table>
<tr><th>Experimento</th><th>Montaje</th><th>Energía total [erg]</th><th>Área emisora total [cm²]</th><th>F pico [erg cm⁻² s⁻¹]</th><th>Función</th></tr>
%(rows)s</table></div>
%(fig3)s
%(fig4)s
<p><b>Lo que se conserva y lo que no.</b> E2, E3a, E3b y E4 inyectan la misma energía total y E2, E3a y E3b la misma P<sub>total</sub>(t) = Σ A<sub>i</sub>F<sub>i</sub>(t) (verificado
numéricamente). No coinciden el área emisora ni el flujo por pulso; informarlo es obligatorio, porque comparar casos con distinta energía o área sin declararlo invalida la comparación.</p>
%(fig5)s

<h3>Cómo se leerá la memoria cuando haya salidas</h3>
<ul>
<li><b>Respuesta con historia (contrafactual pareado):</b> R<sub>hist</sub>(τ) = X<sub>con pulso 2</sub>(t₂ + τ) − X<sub>sin pulso 2</sub>(t₂ + τ), con la misma historia hasta t₂. Para el pulso 2 es E2 − E5, que descuenta el residuo del pulso 1.</li>
<li><b>Respuesta en atmósfera relajada:</b> R<sub>rel</sub>(τ) = X<sub>E1</sub>(t₀ + τ) − X₀. La <b>memoria</b> es M(τ) = R<sub>hist</sub>(τ) − R<sub>rel</sub>(τ), con X = T, n, v, ionización, Q(s,t) y profundidad de deposición, alineando los inicios de pulso.</li>
<li><b>Pulso 3:</b> exige el contrafactual «pulsos 1 y 2 sin pulso 3», aún no generado.</li>
<li><b>Filamentos independientes (secundario):</b> la emisión es la suma ponderada por área, I(t) = Σ A<sub>i</sub> I<sub>i</sub>(t − desfase<sub>i</sub>), válida solo bajo las hipótesis geométricas y radiativas que se documenten.</li>
<li><b>Control continuo (E4):</b> aísla el efecto de la distribución temporal de la energía; su Ec y δ son medias ponderadas por energía, una elección y no una medida.</li>
</ul>
<p>No se suman respuestas de pulsos aislados para representar recalentamiento: la física es no lineal y esa suma solo describe filamentos independientes.</p>

<h2>5. Verificaciones realizadas</h2>
<div class="box ok"><b>30 pruebas automáticas pasan</b> (<code>pytest</code>): fórmula de potencia contra cálculo manual; ida y vuelta Ṅ↔F; rechazo de δ ≤ 2;
energía exacta de cada tabla e integración numérica independiente; valores en meseta, hueco y fuera de tabla; ida y vuelta del formato <code>.cfg</code> y los 7 tokens de cabecera que salta HYDRAD;
equivalencia con una réplica línea a línea de <code>CalculateBeamParameters</code>; rechazo de tablas inválidas; energía total igual en E2/E3a/E3b/E4; conservación de P<sub>total</sub>(t) en la fragmentación (2 y 3 pulsos).</div>
<p><b>Prueba con HYDRAD real</b> (copia compilada en macOS, 6 s de tiempo físico con la tabla de E2): el ejecutable lee la tabla sin errores y el calentamiento empieza en t ≈ 1 s. Después se corrieron E2 y E5 completos (101 s). La temperatura máxima pasa de
1.6 a 3.4 MK y los flujos ascendentes llegan a ≈ 73 km/s, sin NaN. Es una comprobación de formato y de arranque, <b>no una validación de la física</b>.</p>
<div class="box warn"><b>Problema abierto en HYDRAD, y su alcance.</b> En pruebas iniciales, un haz constante de 5×10¹⁰ erg cm⁻² s⁻¹ (Ec = 15 keV, δ = 5) dejó todas las celdas en NaN antes de t = 2 s (dt ≈ 10⁻²⁰ s), y un haz de 10¹⁰ apagado bruscamente a los 10 s falló después. Se reproduce sin optimización (-O0). En cambio, las tablas de este informe (cajas con rampas, F = 1.3×10¹⁰) corrieron completas: E2 (101 s, con el segundo pulso) en ≈41 s de pared y E5 en ≈19 s, sin NaN. La causa sigue sin diagnosticarse (alto flujo o apagado brusco son los sospechosos); debe aclararse antes de ampliar el barrido a flujos mayores.</div>

<h2>6. Qué no es todavía este trabajo</h2>
<ul>
<li>No hay evento, ajuste espectral ni incertidumbres de STIX; Ṅ, Ec, δ y A son ilustrativos.</li>
<li>La energía del caso base (%(etot)s erg) es solo un orden de magnitud plausible para una llamarada pequeña, no una estimación.</li>
<li>Los pulsos son cajas idénticas. Los datos reales tendrán Ec(t) y δ(t) variables y covarianzas; el generador admite pulsos distintos, pero el ajuste por intervalos queda por hacer.</li>
<li>El área del filamento no está acotada; E3a y E3b son dos puntos de una familia, no un barrido.</li>
</ul>

<h2>7. Siguientes pasos y preguntas para la profesora</h2>
<ol>
<li>Diagnosticar el NaN de HYDRAD (primera celda y primer instante, balance de energía ∫Q<sub>beam</sub>dV frente a F·A·t) o descartar HYDRAD como banco de pruebas.</li>
<li>Escribir el código de diagnósticos de memoria (columna de masa, profundidad de frenado, ΔX(τ)) y probarlo con las salidas de HYDRAD que sean estables.</li>
<li>Elegir evento y ajustar espectros STIX; alimentar este generador con Ec(t), δ(t), Ṅ(t) y sus incertidumbres.</li>
<li><b>Preguntas:</b> ¿qué significa exactamente «impacto»? ¿Qué RADYN+FP o FLARIX, y qué cuota de clúster, están disponibles? ¿Son Hα o IRIS diagnósticos centrales? ¿Hay un evento preferido?</li>
</ol>

<h2>Reproducir</h2>
<div class="eq mono">.venv/bin/python -m pytest -q<br>.venv/bin/python src/experiments.py &nbsp;&nbsp;# escribe results/experiments/*/beam_heating_model.cfg y manifest.json<br>.venv/bin/python src/make_figures.py<br>.venv/bin/python src/make_report.py</div>
<p class="sub">Código: <code>src/beam_tables.py</code>, <code>src/experiments.py</code>, <code>tests/</code>. Basado en HYDRAD (Bradshaw &amp; Mason 2003; Reep et al. 2019; MIT).
La interpretación es del proyecto, no de los autores de HYDRAD.</p>
</main></body></html>
""" % dict(
        fig0=img("fig0_scenarios.png", "Esquema de los dos escenarios") + "<figcaption>Figura 0. Los dos escenarios que se quieren distinguir.</figcaption>",
        fig1=img("fig1_stopping_column.png", "Columna de frenado frente a Ec") + "<figcaption>Figura 1. Columna de frenado en función de Ec; expresión de heat.cpp, incidencia normal.</figcaption>",
        fig2=img("fig2_table_encoding.png", "Codificación de la tabla de haz") + "<figcaption>Figura 2. Codificación correcta frente a la ingenua; abajo, la energía acumulada por unidad de área.</figcaption>",
        fig3=img("fig3_experiments_flux.png", "Flujo de energía por experimento") + "<figcaption>Figura 3. Flujo de energía de cada tubo en cada experimento. Los filamentos se muestran en tiempo global.</figcaption>",
        fig4=img("fig4_energy_ledger.png", "Balance de energía") + "<figcaption>Figura 4. Izquierda: energía acumulada. Derecha: área emisora y flujo pico, que no se conservan.</figcaption>",
        fig5=img("fig5_degeneracy.png", "Degeneración de la potencia total") + "<figcaption>Figura 5. P<sub>total</sub>(t) es idéntica para E2, E3a y E3b; el flujo por pulso depende del área asumida.</figcaption>",
        avg_e=avg_e, ec=p.ec_kev, delta=p.delta, ncn=sci(nc_n, 2), nci=sci(nc_i, 2), ratio=nc_n / nc_i,
        ebad=sci(bad.energy_per_area(), 3), egood=sci(good.energy_per_area(), 3),
        rat=bad.energy_per_area() / good.energy_per_area(), ramp=base.ramp,
        ndot=sci(base.ndot, 2), npul=base.n_pulses, dur=base.duration, gap=base.gap, area=sci(base.area_cm2, 2),
        arc=n_arcsec2, pw=sci(p.power_erg_s, 3), fl=sci(p.flux, 3), rows=rows,
        etot=sci(sum(q.energy_erg for q in ps), 2))
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(html)
    print("report written to", os.path.normpath(OUT), "(%d kB)" % (len(html) // 1024))


if __name__ == "__main__":
    main()
