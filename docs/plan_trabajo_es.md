# Plan de trabajo: objetivos finales, resultados esperados y tiempos

**Autor:** Carlos Alberto Martínez Sibaja · **Plan que describe:** v5.1 (2026-10-05) · **Fecha:** 2026-10-13

Documento **de apoyo en español**, para estudiar y para planear. No es autoritativo: manda
[00_objectives_and_methodology.md](00_objectives_and_methodology.md) para el diseño y
[07_core_pilot_hydrad.md](07_core_pilot_hydrad.md) para los resultados. Si algo aquí los contradice, ellos ganan.

Complementa a [guia_conceptos_es.md](guia_conceptos_es.md), que explica la **física desde cero**.
Este documento no repite esa física: responde otras tres preguntas.

1. ¿Cuáles son los **objetivos finales** y en qué se diferencian de los originales?
2. ¿Qué se va a **hacer**, paso a paso, con qué comandos y con qué criterio de cierre?
3. ¿**Cuánto tiempo** toma cada cosa y qué resultados se esperan al final?

**Índice**

1. [Los objetivos finales](#1-los-objetivos-finales)
2. [Por qué cambiaron los objetivos](#2-por-qué-cambiaron-los-objetivos)
3. [El punto de partida real, hoy](#3-el-punto-de-partida-real-hoy)
4. [Qué se va a hacer, paso a paso](#4-qué-se-va-a-hacer-paso-a-paso)
5. [Resultados esperados](#5-resultados-esperados)
6. [Cronograma y presupuesto de cómputo](#6-cronograma-y-presupuesto-de-cómputo)
7. [Riesgos y plan B](#7-riesgos-y-plan-b)
8. [Lo que esta ruta no podrá afirmar](#8-lo-que-esta-ruta-no-podrá-afirmar)
9. [Checklist por corrida](#9-checklist-por-corrida)
10. [Decisiones pendientes con la supervisora](#10-decisiones-pendientes-con-la-supervisora)

---

## 1. Los objetivos finales

### 1.1 La pregunta

> **¿Cuándo tratar cada pulso de electrones como si hubiera golpeado la atmósfera inicial relajada tergiversa la
> respuesta a un pulso posterior más allá de las incertidumbres de haz, numéricas y observacionales de un
> diagnóstico elegido?**

A ese tratamiento se le llama aquí **aproximación de pulsos independientes**: la respuesta a un pulso se calcula
sobre la atmósfera inicial y se suma a lo que dejaron los pulsos anteriores. Un modelo *multithread* que pone cada
pulso en una hebra nueva hace la misma suposición cada vez que, en realidad, la hebra vuelve a ser golpeada.

### 1.2 Los tres objetivos comprometidos

Para **dos pulsos idénticos en un bucle y un diagnóstico primario**:

**Reordenados el 2026-10-13.** El efecto, su mecanismo y la dependencia del tiempo de espera están publicados
(§4.1, cuarta pasada), así que **la frontera es el aporte** y pasa a ser el objetivo principal.

| # | Objetivo | Prioridad | Producto concreto |
|---|---|---|---|
| **O3** | Decir en qué rango de `τ` la aproximación es **adecuada** y en cuál falla | **Principal** | `τ*(F)`: el `τ` más corto desde el cual `\|M_D\| ≤ k σ_tot` para todo `τ` mayor muestreado. Reportarlo **también en unidades de `τ_enfriamiento`** |
| **O1** | Medir el contraste `M_D` con cuatro ramas pareadas, en función de `τ` y de `F` | El medio | El mapa `τ × F` de `M_D(τ, t′)`, en unidades físicas, con su presupuesto de error |
| **O2** | **Explicarlo** con el estado que dejó el primer pulso | Evidencia | El mecanismo: columna coronal en `t_k`, perfil de depósito, energía que llega a la cromosfera, flujos. **El mecanismo en sí es trabajo previo** |

**Lo que define "falla"** (fijado *antes* de calcular cualquier contraste):

```text
falla para D donde   |M_D| > k · σ_tot
σ_tot² = σ_num² + σ_beam² + σ_obs²        (en las unidades de D)
k = 3 por defecto; cambiarlo exige razón escrita
```

Dos salvaguardas que no se negocian:

- la **relajación** del pulso 1 se juzga comparando el estado de `A1` con `A0` en `t_k`, nunca por `M_D → 0`
  (eso es justo lo que se está midiendo);
- una corrida que revienta o no converge es un **fallo en el registro**, no un efecto pequeño.

### 1.3 Por qué importa

Los modelos *multithread* y los guiados por observaciones calientan cada hebra **una sola vez** desde un estado
relajado. Si una hebra vuelve a ser golpeada dentro del rango donde la aproximación falla, esos modelos
**tergiversan** su respuesta. Si no, la aproximación queda **justificada en el dominio explorado**.
Las dos respuestas se pueden publicar, y eso es lo que hace seguro comprometerse con este objetivo.

---

## 2. Por qué cambiaron los objetivos

Cada versión anterior murió por una razón concreta. Conviene saber decirlas en una frase cada una.

| Versión | Qué preguntaba | Por qué se abandonó |
|---|---|---|
| **v2** · sesgo de inferencia | ¿cuánto sesga la memoria los parámetros (`Ṅ`, `Ec`, `δ`) ajustados a STIX? | el mecanismo es real pero **ya conocido** (ionización no uniforme, Kontar, Brown & McArthur 2002) y el resultado es modesto: daría una nota de métodos |
| **v3** · memoria vs. corriente de retorno vs. aceleración | ¿qué proceso moldea la evolución espectral pulso a pulso? | exige **síntesis de fotones** desde el transporte y datos reales: demasiado grande para el tiempo disponible |
| **v4** · reúso de bucles | ¿los pulsos posteriores reutilizan bucles ya llenos? | **la premisa falla**: la medida de emisión no acota la columna *a lo largo del camino de los electrones* en una fuente no resuelta y no uniforme |
| **v5.1** · actual | ¿cuándo falla la aproximación de pulsos independientes? | se conserva: pregunta cerrada, medible con herramientas que ya corren, y con **tres desenlaces publicables** |

**El cambio no es una ambición menor, es una ambición defendible.** v4 no cayó por falta de trabajo: cayó porque la
cantidad observable (EM) integra a lo largo de la línea de visión y no a lo largo del camino del haz. v5.1 mueve la
pregunta a donde sí hay control total: **dentro del modelo**, con un contrafactual explícito.

Lo que sobrevive de las versiones viejas es **infraestructura opcional**, no compromiso: `src/toy_bias.py` (sesgo
espectral de juguete), `src/tracer.py` (trazador v4), la búsqueda de eventos STIX y la primera mirada al X5.0.

---

## 3. El punto de partida real, hoy

### 3.1 Lo que ya está hecho y cerrado

- **Fase 0 completa** y **revisión R1 decidida** (2026-10-05): opción (a), seguir el mapa del núcleo con **HYDRAD** y
  *proxies* coronales, con la puerta RADYN **en paralelo**, no como prerrequisito.
- **Las cuatro ramas corren limpias** para `τ` = 10, 30 y 60 s sobre la ventana completa de 89 s, en el bucle de
  60 Mm con cromosfera de 8 Mm por pie, en ~2 h de reloj sobre 6 núcleos.
- **La inestabilidad del segundo pulso está diagnosticada y curada**: era el paso explícito de conducción térmica,
  no la interpolación ni la falta de viscosidad. `SAFETY_CONDUCTION = 0.2`.
- **La masa del bucle se conserva** al profundizar la cromosfera de 5 a 8 Mm por pie (la de serie es un depósito
  demasiado fino para flujos de fulguración; la malla adaptativa llegaba a las celdas de frontera).
- **El contraste no es residuo numérico.** Pico de `|M|` frente a `σ_num` del paso de conducción:

  | Diagnóstico | `σ_num` (pico) | `σ_beam` (pico) | máx `\|M\|` | margen |
  |---|---|---|---|---|
  | EM de plasma con T > 1 MK | 2.8×10⁴⁶ cm⁻³ | 1.5×10⁴⁷ | 2.5×10⁴⁷ | 9 σ_num |
  | T ponderada por EM | 0.25 MK | 1.6 MK | 5.2 MK | 21 σ_num |
  | Temperatura del ápice | 0.32 MK | 1.1 MK | 3.0 MK | 9 σ_num |
  | Densidad del ápice | 2.9×10⁹ cm⁻³ | 9.4×10⁹ | 2.7×10¹⁰ | 9 σ_num |

- **Hay mecanismo**, no solo correlación: en `t_k` la columna coronal es ~4×10¹⁹ cm⁻² (≈56 % de la columna de
  frenado a 20 keV), así que parte del haz frena arriba, el ápice se calienta menos y la emisión caliente no
  necesita esperar la evaporación.

### 3.2 Lo que está abierto, y por eso define la Fase 1

| Pendiente | Por qué bloquea |
|---|---|
| **σ_num espacial** sin medir (solo se varió el paso de conducción) | todos los márgenes de arriba son **cotas superiores**; además decide si el segundo episodio de `A1` (t ≈ 85–130 s, subida de EM y T **sin haz** y con masa conservada) es dinámica del bucle o artefacto de resolución |
| **σ_obs** sin fijar y σ medidas **después** de los contrastes | invierte el orden que exige el plan: hoy el análisis de incertidumbre es **exploratorio**, no una decisión |
| **El bucle no se relaja en 120 s** (el criterio del 5 % falla en todo `τ` muestreado) | `τ*` > 120 s: el piloto no lo acota por arriba, así que O3 todavía no tiene respuesta |
| **Diagnóstico primario sin elegir** | la columna coronal falla `σ_num` (su umbral de 3×10⁴ K cae sobre las condensaciones y el piso radiativo) y los diagnósticos puntuales del ápice cambian de signo con `t′` y con `τ` |
| **Flujos ≥ 2.5–5×10¹⁰ siguen dando NaN** | el eje de flujo del mapa queda acotado muy por debajo de la rejilla F-CHROMA |

---

## 4. Qué se va a hacer, paso a paso

### 4.1 Fase 1a — las cinco compuertas, más un pendiente de Fase 0

Van **antes** porque cualquiera de ellas puede invalidar un mapa ya calculado.

#### Compuerta 0 · búsqueda dirigida — **CERRADA el 2026-10-13**

**Qué:** completar la búsqueda que la Fase 0 exigía y que R1 se decidió sin cerrar. Hoy la última búsqueda es del
**2026-10-02** y de los papers más cercanos **solo se leyeron resúmenes**; el propio documento de novedad dice que no
se completó ninguna búsqueda ADS exhaustiva ([03, §6 y §11.4](03_novelty_and_prior_work.md)).

**Por qué primero:** decide **cómo se escribe la introducción**, no si el experimento sirve. Mientras no esté cerrada,
la regla del proyecto prohíbe describir el trabajo como "el primero" de su tipo.

**Cómo:**

1. **Tres textos completos, en este orden:** Cho et al. 2023 (el más amenazante: su Tabla 2 ya tiene 20 s + 60 s de
   pausa + 20 s; hay que confirmar si comparan esa segunda respuesta contra una atmósfera fresca),
   Kerr et al. 2024 y Litwicka et al. 2025 (bloqueado por un 403: leer a mano).
2. **Las consultas ADS** de [03, §11.4](03_novelty_and_prior_work.md): calentamiento repetido / sucesivo /
   intermitente, regolpe de la misma hebra, precondicionamiento atmosférico, ionización dependiente del tiempo,
   experimentos de *restart* o contrafactuales; en RADYN, HYDRAD, FLARIX y FP, solar y estelar.
3. **Seguir citas** de los estudios más cercanos, leer métodos y no solo resúmenes, y **registrar fechas de
   búsqueda y accesos denegados**.

**Criterio de cierre:** §11 de [03](03_novelty_and_prior_work.md) actualizado con fecha, y una frase escrita de
posicionamiento que sobreviva a un informe de árbitro.

**Resultado (2026-10-13).** Registro completo en [03, §11.6 y §11.7](03_novelty_and_prior_work.md).

| Paper | Veredicto |
|---|---|
| **Cho et al. 2023** | Su modelo E6 (20 s + 60 s + 20 s, F = 6×10⁸, Ec = 10 keV, δ = 7, bucle de 15 Mm) es **una entrada de una rejilla de 13 modelos**. No hay control con solo el segundo pulso, no se analiza qué dejó el primero, y **el paper no menciona precalentamiento, memoria ni tiempos de espera en ninguna parte**. La distinción queda **confirmada**, ya no supuesta |
| **Kerr et al. 2024** | 100 s débiles a 5×10⁸ y después una rampa *ad hoc* a 1×10¹¹; **sin pausa entre fases**, sin control de pulso fuerte solo, sin barrido de espera y **sin estimar cuánto cambia la respuesta por estar precalentada**. Su barrido es de la *duración* del calentamiento débil a energía total igual. Ellos mismos llaman sus experimentos "overly simplified" |
| **Litwicka et al. 2025** | **Sigue inaccesible**: 403 en IOP el 2026-10-02 y otra vez el 2026-10-13, y no hay preprint en arXiv por título, autor ni DOI. Hay que conseguirlo por acceso institucional, por la supervisora o pidiéndolo a los autores |

**Precedente nuevo, que no estaba en la tabla: [Bakke et al. 2022](https://arxiv.org/abs/2201.11961)** (A&A 659, A186).
Seis corridas RADYN de nanofulguración con ápices a 1 y 3 MK; al bucle de 3 MK lo llaman **"pre-heated"** y dicen que
**"representa una hebra previamente calentada"**, y reportan que *"por la mayor densidad inicial, los electrones
inyectados depositan más de su energía en la corona"*, con respuesta más lenta.

**Esto obliga a un ajuste honesto del encuadre.** El **mecanismo** del núcleo — corona más densa, el haz frena
arriba, el ápice se calienta menos — **ya está publicado como efecto de condición inicial** (Polito et al. 2018;
Bakke et al. 2022). Hay que dejar de presentarlo como hallazgo propio. El objetivo **O2 sigue siendo necesario**
como evidencia de que `M` es causal y no numérico, pero **no es el elemento novedoso**.

**Lo que sí queda como aporte** (frase de posicionamiento de [03, §11.7](03_novelty_and_prior_work.md)): la
**medición del error mismo** — el contraste de ramas emparejadas, a flujos de fulguración, entre la respuesta de un
bucle regolpeado y la de uno relajado, en función de la espera y del flujo, juzgada contra incertidumbres fijadas
antes de calcular el contraste.

**Tercera pasada, verificada (mismo día).** Registro en [03, §11.8](03_novelty_and_prior_work.md). Dos precedentes
más, los dos comprobados contra el texto primario:

- **[Reep et al. 2016](https://arxiv.org/abs/1607.06684)** — **siete ráfagas de haz de electrones en un solo bucle de
  HYDRAD** (Ec ≈ 11 keV, δ ≈ 6, pico 5×10⁹), descartadas contra corrimientos al rojo observados de Si IV y C II:
  *"woefully inadequate"*. El encuadre "nadie ha disparado pulsos repetidos en el mismo bucle" **está muerto**.
  Sobrevive: no hay control relajado (comparan contra observaciones), los intervalos no se declaran ni se barren,
  el flujo es sub-fulguración, y el objetivo es rechazar un modelo, no medir el error de una aproximación.
- **[Barnes, Bradshaw & Viall 2019](https://arxiv.org/abs/1906.03350)** — la literatura de **frecuencia de
  nanofulguraciones** define la frecuencia como ε = ⟨t_espera⟩/τ_enfriamiento y dice que una hebra de alta
  frecuencia *"no alcanza a enfriarse antes de ser calentada otra vez"*. **La dependencia del tiempo de espera ya
  es suya; no se puede reclamar.** Pero es calentamiento volumétrico *ad hoc* sin haz, en EBTEL de dos fluidos
  integrado sobre la corona, sin evaporación modelada, y con el tiempo de espera **acoplado a la energía** del
  evento: no puede hablar de dónde frena un haz. **Mejora concreta: reportar `τ*` también en unidades de
  `τ_enfriamiento`**, para que el resultado sea legible por esa comunidad.

**Litwicka 2025, parcialmente conseguido** vía texto indexado en ResearchGate, y ayuda: sus cuatro pulsos calientan
**cuatro subáreas distintas**, una cada uno, promediando la emisión entre ellas. **No son cuatro recalentamientos de
una hebra**: es un experimento espacial, no temporal. Falta leer el PDF completo.

**El reclamo ahora es puramente metodológico**, y eso es todo el aporte: el contrafactual emparejado, la regla de
incertidumbre pre-registrada, y el mapa `τ × F` a flujos de fulguración para un diagnóstico nombrado.

**Cuarta pasada, verificada (mismo día) — y corrige un error de la tercera.** Registro en
[03, §11.11](03_novelty_and_prior_work.md). La tercera pasada (y mi lectura de ella) decía que Reep et al. 2016
comparaba contra observaciones y no contra un bucle relajado. **Era falso.** El texto primario, §3.1 y Figura 2:

> *"We first attempted to model this event with a single loop, on which seven heating bursts occurred."*
> *"We also attempted to model this event using a multi-threaded loop composed of seven strands, on each of which
> one heating burst occurred."*

Y el mecanismo, textual: *"once evaporation brings material into the corona, later heating bursts cannot cause a
strong velocity flow … due to the increased inertia."*

**En 2016, en HYDRAD, con haz de electrones, ya pusieron lado a lado el bucle regolpeado y las hebras frescas, el
diagnóstico sintético difiere, y lo explicaron por la corona ya llena.** El contraste cualitativo del proyecto
**está publicado** desde hace diez años. No se puede reclamar.

**Lo que su experimento NO hace, y ahora es toda la distinción:**

1. **No es un contraste pareado.** Un bucle con siete ráfagas contra **siete** hebras con una cada una difieren en
   número de hebras, área y masa total, no solo en historia. Que siete hebras frescas den siete corrimientos al
   rojo es en parte consecuencia de que son siete. Su diseño **no puede separar historia de área y multiplicidad**;
   `M_D` está definido por unidad de área de **un** bucle, con las cuatro ramas compartiendo geometría y pulso de
   prueba idénticos.
2. **No hay diferencia de diferencias**: sin rama sin haz y sin rama de "pulso de prueba solo sobre la atmósfera
   relajada", la respuesta *incremental* a un pulso posterior nunca se aísla.
3. **No hay barrido**: los tiempos de las ráfagas vienen de la curva de rayos X observada; ni la espera ni el flujo
   se varían. Y el flujo (5×10⁹) es sub-fulguración.
4. **No hay presupuesto de error ni umbral** fijado de antemano.
5. **Su objetivo es el opuesto**: rechazan los dos modelos de juguete a favor de uno de más de 60 hebras. La
   pregunta "¿cuándo es adecuada la independencia?" no se hace nunca.

**Una oportunidad en el mismo paper.** Reep 2016 es HYDRAD con haz y Si IV sintético — **tu mismo solver**. Es el
**benchmark más barato disponible**: reproducir su Figura 2 cualitativamente respondería la crítica de que nada
aquí se ha validado contra un resultado publicado (extensión E3), en el código que ya tienes compilado. La mayor
amenaza a la novedad es también el mejor blanco de validación.

**Más atrás todavía: Emslie, Li & Mariska 1992** (ApJ 399, 714). Hidrodinámica con haz de electrones comparando
atmósferas precalentadas y no precalentadas, con Ca XIX: la precalentada *"responde lentamente"*. Solo resumen, no
el texto completo. **La comparación precalentado-contra-relajado es de 1992.** Cualquier encuadre que la presente
como nueva está muerto.

**La mejor carta del expediente: [Lörinčík, Polito, Kerr, Hayes & Russell 2025](https://arxiv.org/abs/2504.10619)**
(ApJ 986, 73), §6.3, textual: *"all models considered in our study for simplicity assume a single instance of
constant heating"* y que si *"repeated heating of a single loop"* reproduce los picos cuasi-periódicos
*"remains to be simulated in the future"*. **Polito y Kerr son autores de Cho 2023 y Kerr 2024**, los precedentes
más cercanos: en 2025 dicen por escrito que falta simular el recalentamiento de un bucle. **Esa es la frase con la
que abre tu introducción.** Con un reparo que no se puede omitir: su pregunta es de **tiempos entre líneas
cromosféricas** (Si IV antes que Mg II por 1–6 s), que **HYDRAD no puede responder**. Es un argumento para la ruta
RADYN en R2, no una afirmación de que la ruta actual la cumple.

**Lo que queda del proyecto, dicho sin adornos.** Cuatro pasadas, cuatro estrechamientos; esta le quitó el núcleo
cualitativo. Lo que sobrevive es un **estudio de límites de validez**: no que la memoria exista, no que cambie un
diagnóstico, sino **dónde la suposición de independencia es y no es suficientemente buena**, en condiciones
pareadas y con regla pre-declarada. Es una contribución legítima y modesta. Y convierte a **O3 — el rango donde la
aproximación SÍ es adecuada — en la parte más valiosa del proyecto**, no en un plan B: es la única que ningún
estudio previo entrega.

**Lo que falta para poder decir "el primero":** el barrido de ADS **nunca se ha corrido** — cuatro pasadas, cuatro
fracasos para alcanzarlo. Necesita a una persona con acceso a ADS, o el [prompt](novelty_search_prompt.md) dado a un
agente que sí pueda consultarlo. Más el texto completo de Emslie 1992, la Figura 2 de Reep 2016 en detalle, el PDF
de Litwicka, y el cribado de citas hacia adelante hasta la fecha de envío.

#### Compuerta 1 · σ_num espacial

**Qué:** variar los **umbrales de refinamiento** y el **nivel máximo de refinamiento** de HYDRAD, no solo el paso de
conducción, y volver a medir `M_D` en la configuración adoptada (60 Mm, cromosfera 8 Mm, `SAFETY_CONDUCTION = 0.2`).

**Cómo:** reconstruir con `scripts/build_hydrad_scratch.sh <dir> --set <parámetro>=<valor>` para cada variante y
correr las cuatro ramas de un `τ` de referencia (10 s) con `scripts/hydrad_numerical_error.py`, que ya hace esto
para el paso temporal. `σ_num` final = combinación de la variante temporal y la espacial.

**Criterio de cierre:** `σ_num(t′)` escrito por diagnóstico, y una respuesta a si el segundo episodio de `A1`
sobrevive al cambio de resolución. Si **no** sobrevive, las ventanas de `τ` = 30 y 60 s se reinterpretan.

**Tiempo:** 2 semanas (incluye reconstrucciones y ~4–6 corridas de cuatro ramas).

#### Compuerta 2 · σ_obs y decisión pre-registrada

**Qué:** nombrar el **instrumento** que mediría el *proxy* elegido, con su ruido y su calibración, y escribir
`sigma.json` **antes** de correr.

**Cómo:** con Si IV como diagnóstico primario (compuerta 4), el instrumento es **IRIS**, cuyo ruido y calibración
están publicados. De ahí sale `σ_obs(t′)` en las unidades del diagnóstico. Luego
`scripts/hydrad_paired_branches.py ... --sigma sigma.json`, que aplica la regla `k σ_tot`.
**Esta compuerta subió de importancia con el reordenamiento:** si la frontera es el producto, `σ_obs` ya no es un
término del presupuesto, es *lo que define dónde está la frontera*.

**Criterio de cierre:** `sigma.json` versionado y con fecha anterior a la primera corrida del mapa, y `k` declarado.

**Tiempo:** 1 semana. **Es la compuerta bloqueante**: sin ella no hay decisión, solo exploración.

#### Compuerta 3 · una rejilla de τ que alcance la relajación

**Qué:** poder acotar `τ*` por arriba. Hoy no se puede.

**Dos caminos, hay que elegir uno:**

- **(i) extender la rejilla más allá de 120 s**, lo que exige `SAFETY_CONDUCTION = 0.1` para la oscilación de
  escala de malla que mató a `B1` en `τ` = 120 s — más caro, probablemente ×2–4 en reloj;
- **(ii) mover el dominio a un pulso 1 más débil**, donde el bucle sí se relaje dentro de la ventana. Cambia el
  dominio físico, pero hace la pregunta contestable.

**Criterio de cierre:** una rejilla de `τ` donde el criterio de relajación del 5 % (columna coronal, densidad y
temperatura del ápice, masa de columna sobre la TR) **se cumpla** en el `τ` más largo.

**Tiempo:** 2 semanas de pruebas, incluida la estimación de costo del camino (i).

#### Compuerta 4 · un diagnóstico primario elegido por robustez

**Qué:** fijar **uno** antes del mapa. **Candidato primario desde el 2026-10-13: Si IV 1402.77 Å**, intensidad y
corrimiento Doppler.

**Por qué Si IV y no los *proxies* coronales:**

- **Reep et al. 2016 ya lo sintetizó desde HYDRAD** con calentamiento por haz. Prueba que se puede calcular con tu
  solver, y vuelve su Figura 2 un **benchmark reproducible**. No necesita RADYN ni colaborador.
- Es línea de **zona de transición**, dentro de lo que el solver tal como viene soporta; no es una afirmación cromosférica.
- **Es la moneda que la audiencia ajusta**: toda la cadena *multithread* (Rubio da Costa 2016; Reep 2018, 2020)
  mide Si IV y Fe XXI. La EM caliente y la T ponderada por EM no las ajusta ningún grupo objetivo.
- Es la línea cuyos tiempos bajo calentamiento repetido **Lörinčík et al. 2025 dejan explícitamente abiertos**.
- Hace `σ_obs` nombrable: **IRIS**.

**El reparo, que se declara y se acota:** la formación de Si IV es sensible a la ionización fuera de equilibrio
(Nóbrega-Siverio et al. 2018) y HYDRAD supone equilibrio con nₑ = n_H. Reep et al. 2016 cargaba la misma
limitación y publicó.

**Respaldo:** EM caliente y T ponderada por EM quedan como par de verificación cruzada (son el par estable del
piloto). Descartados: la columna coronal (falla `σ_num`) y los diagnósticos puntuales del ápice (cambian de signo).

**Criterio de cierre:** la síntesis de Si IV funcionando sobre las cuatro ramas, el diagnóstico escrito en el plan
con su razón, y el reparo de ionización declarado.

**Tiempo:** 1–2 semanas (la síntesis es nueva; el resto cae de las compuertas 1 y 2).

#### Compuerta 5 · el límite de degeneración, como resultado

**Qué:** cuantificar y **reportar** que, alrededor del final del pulso (`t′` ≈ 15–45 s), un haz variado dentro de
sus errores típicos de ajuste STIX mueve la medida de emisión **tanto como la historia**.

**Cómo:** `scripts/hydrad_beam_error.py` ya repite `B0` variando un parámetro a la vez con las incertidumbres
relativas del primer estallido de Collier et al. (2024): tasa de electrones ±12 %, corte ±4 %, índice espectral
±0.1. `scripts/pilot_uncertainty.py` compara `|M_D(t′)|` con `3(σ_num ⊕ σ_beam)` en cada `t′`.

**Criterio de cierre:** una figura y un párrafo que digan **en qué ventanas de `t′`** el diagnóstico separa historia
de haz y en cuáles no. Esto es un hallazgo sobre el diagnóstico, no un defecto de la corrida.

**Tiempo:** 1 semana (el código ya existe; falta correrlo en la configuración final y escribirlo).

#### Compuerta 6 · el benchmark de Reep 2016 (nueva, 2026-10-13)

**Qué:** reproducir cualitativamente la Figura 2 de [Reep et al. 2016](https://arxiv.org/abs/1607.06684): siete
ráfagas de haz en un bucle contra siete hebras calentadas una vez cada una, con Si IV sintético, en tu HYDRAD.

**Por qué vale dos semanas:** responde de un golpe tres debilidades distintas. **(1) Validación** — hoy nada de
este proyecto se ha comparado contra un resultado publicado (era la extensión E3, y sale gratis porque es el mismo
código). **(2) Posicionamiento** — demuestra ante un árbitro que sabes exactamente dónde termina su aporte y
empieza el tuyo. **(3) Diagnóstico** — es el camino más corto para tener la síntesis de Si IV funcionando y
verificada.

**Criterio de cierre:** los signos y el orden de magnitud de su Figura 2 reproducidos, con las diferencias
explicadas (sus intervalos vienen de la curva de rayos X observada y no están declarados, así que la reproducción
es cualitativa por construcción).

**Tiempo:** 2 semanas, después de la compuerta 4.

### 4.2 Fase 1b — el mapa del núcleo `τ × F`

**El barrido:** la rejilla de `τ` que salga de la compuerta 3, cruzada con **2–3 niveles de flujo**, añadidos solo
donde las cuatro ramas corran limpias y converjan. El techo del eje de flujo está acotado: `F ≥ 2.5–5×10¹⁰`
sigue dando NaN y esa falla **no** está diagnosticada.

**Por celda del mapa** (un `τ`, un `F`): cuatro ramas, pero `A0` se comparte y `A1` se corre una sola vez hasta la
ventana más larga; `B1` se **reinicia** desde el perfil de `A1` justo antes de cada `t_k`, en paralelo.

**Comandos:**

```bash
.venv/bin/python -m pytest -q
```

```bash
.venv/bin/python src/experiments.py
```

```bash
scripts/build_hydrad_scratch.sh ../hydrad-scratch --set SAFETY_CONDUCTION=0.2
```

```bash
.venv/bin/python scripts/hydrad_paired_branches.py ../hydrad-scratch --length-cm 6.0e9 --chromosphere-cm 8e8 --taus 10 30 60 --label L60_chr8 --sigma sigma.json
```

Con `--analyze-only` se recalcula el análisis sin volver a simular. El resumen trae la relajación en `t_k`, el error
de *restart*, la ventana de conservación de masa y `M_D`. Dos máscaras automáticas protegen el análisis:
`MASS_TOL` (1 % de la masa del bucle) y `OSC_MAX` (60 % de celdas oscilando) — ambas fijadas antes de mirar
contrastes.

**El mecanismo (O2), en cada celda:** registrar en `t_k` la columna coronal, la posición y la masa de columna de la
zona de transición, los perfiles de temperatura e ionización y los flujos; después comparar `B1` con `B0` en el
perfil de depósito de `b` sobre coordenada de columna, la energía que llega a la cromosfera, y los flujos de
evaporación y condensación. **Un pico desplazado en el tiempo no es una diferencia simultánea.**

**Tiempo:** 4 semanas.

### 4.3 Revisión R2

Dos preguntas: ¿está `M` **entendido** y es **robusto a la resolución**? ¿se añade un diagnóstico cromosférico o
alguna extensión? Como en R1, se elige entre opciones y **se registra la decisión** en el plan.

**Tiempo:** 1 semana.

### 4.4 Fase 2 — la escritura

Un artículo enfocado sobre **cuándo falla la aproximación de pulsos independientes**, con configuración
reproducible. Esqueleto que ya está implícito en los tres objetivos:

1. el problema (quién usa la aproximación y dónde);
2. el método (cuatro ramas, `M_D`, la regla de decisión pre-registrada);
3. el mapa `τ × F` y `τ*(F)`  → **O1 y O3**;
4. el mecanismo → **O2**;
5. los límites: degeneración con el haz, condensaciones como propiedad del modelo, techo de flujo;
6. qué implica para los modelos *multithread*.

**Tiempo:** ~4 semanas.

### 4.5 En paralelo todo el tiempo: la puerta RADYN

Seis requisitos, **ninguno** hecho: compilador Fortran, librería NASA CDF, reproducir un modelo F-CHROMA,
demostrar que el *restart* preserva las poblaciones atómicas, medir el tiempo de reloj, confirmar la licencia.
Es un problema de **cadena de compilación y licencia, no de física**, y su costo es desconocido hasta que exista el
compilador. Por eso **no bloquea** el núcleo. Es la única ruta a líneas cromosféricas (Mg II, Si IV, Hα).

---

## 5. Resultados esperados

### 5.1 Los tres desenlaces, todos reportables

| # | Desenlace | Qué se publica |
|---|---|---|
| **R-A** | La aproximación **falla** para `τ < τ*(F)` | `τ*(F)` como número de cabecera, más el mecanismo |
| **R-B** | `M` es apreciable en las **variables de estado** pero queda bajo `σ_tot` en el diagnóstico | "este diagnóstico no puede verlo": una afirmación útil sobre el observable |
| **R-C** | `M` queda bajo `σ_tot` en **todo** el dominio explorado | la aproximación es **adecuada ahí**, con el dominio explícito |

### 5.2 Las predicciones concretas (ya visibles en el piloto)

Lo que el mapa debe confirmar o refutar, con su dependencia de `τ` y `F`:

1. **La emisión caliente aparece de inmediato.** En un bucle fresco la corona debe llenarse primero por
   evaporación; en uno regolpeado la señal está en segundos. En el piloto esto **sobrevive** a `3(σ_num ⊕ σ_beam)`
   en los primeros ~14 s.
2. **El ápice se calienta menos, ~1.5–2.4 MK.** La misma energía se reparte entre muchas más partículas y parte
   del haz nunca llega a la cromosfera. Sobrevive de `t′` ≈ 14 s en adelante.
3. **El bucle regolpeado se queda más caliente después del pulso**: T ponderada por EM 2–5 MK más alta y entre 2 y
   17 veces la EM caliente de la respuesta fresca.
4. **Ningún contraste decrece** de `τ` = 10 s a 60 s: coherente con un `τ*` > 120 s para pulsos fuertes.
5. **Hay un límite de degeneración**, y es un resultado: cerca del final del pulso, un haz dentro de sus errores de
   ajuste mueve la EM tanto como la historia.

### 5.3 Qué número es "la cabecera"

`τ*(F)`. Es lo que un modelador *multithread* puede usar directamente: **si vuelves a golpear una hebra antes de
`τ*`, tu modelo se equivoca en más de lo que mides**. Todo lo demás lo sostiene.

### 5.4 ¿Y lo de STIX? Sí, como agregado posterior — pero con una distinción

**STIX ya está dentro del núcleo**, como fuente de `σ_beam`: las variantes del haz siguen un ajuste STIX
(tasa de electrones ±12 %, corte ±4 %, `δ` ±0.1, según Collier et al. 2024) y corren en
`scripts/hydrad_beam_error.py`. Eso no es extensión, es compuerta 5.

**E1 sí es modular y va después.** Los parámetros de haz resueltos por pulso y los tiempos de espera observados
fijan **qué parte del mapa `τ × F` importa**. Acota el dominio; no toca el diseño del experimento, ni las ramas,
ni la regla de decisión. Nada del núcleo lo espera, y nada de E1 se rehace si el núcleo se mueve. **Es el orden
correcto**, no una postergación.

**E2 no es un agregado.** "Mismos datos STIX, distintas historias" exige síntesis de fotones desde el transporte,
es decir RADYN+FP o el solver FP suelto. Es otra máquina, no una suma.

**Con Si IV como primario, la división se vuelve limpia:** **IRIS** es el socio observacional (fija `σ_obs` y por
tanto la frontera) y **STIX** es la restricción del lado del haz (fija la entrada y su incertidumbre).

**Advertencia de colisión.** STIX + IRIS sobre una fulguración multipulso es justo el enfoque del grupo de
Litwicka (su resumen de 2026: FLARIX, el X9 del 3 de octubre de 2024, STIX + IRIS + CHASE). Si se toma E1, hay que
elegir otro evento y otra pregunta.

**Lo que STIX nunca podrá dar:** que dos pulsos iluminen el mismo pie no prueba que sea la misma hebra. STIX puede
acotar el dominio; no puede validar el escenario.

---

## 6. Cronograma y presupuesto de cómputo

**Horizonte: 3–6 meses, sin fecha fija** (Fase 1 de 1–2 meses, Fase 2 de ~1 mes, según el plan v5.1).
Fechas contadas desde el 13 de octubre de 2026.

| Bloque | Fechas | Contenido | Cierre |
|---|---|---|---|
| ~~Compuerta 0~~ | **cerrada 13 oct 2026** | búsqueda dirigida: Cho y Kerr leídos completos, Litwicka inaccesible, precedente nuevo (Bakke 2022) | §11.6–11.7 de [03](03_novelty_and_prior_work.md) escritas |
| Compuerta 1 | 13–26 oct 2026 | σ_num espacial; veredicto sobre el segundo episodio de `A1` | `σ_num(t′)` por diagnóstico |
| Compuerta 2 | 27 oct – 2 nov | instrumento, `σ_obs`, `sigma.json` pre-registrado | manifiesto con fecha anterior al mapa |
| Compuerta 3 | 3–16 nov | rejilla de `τ` que alcance relajación: camino (i) o (ii) | relajación cumplida en el `τ` más largo |
| Compuerta 4 | 17–30 nov | síntesis de Si IV sobre las cuatro ramas; diagnóstico fijado con su reparo | Si IV corriendo y escrito |
| Compuerta 6 | 1–14 dic | benchmark: Figura 2 de Reep 2016 reproducida cualitativamente | signos y órdenes de magnitud |
| Compuerta 5 | 15–21 dic | degeneración con el haz cuantificada y escrita | párrafo y figura listos |
| **Fase 1b · mapa** | 22 dic – 25 ene 2027 | `τ × F` (2–3 flujos) + mecanismo en cada celda | mapa con decisión aplicada |
| Revisión R2 | 26 ene – 1 feb 2027 | ¿`M` entendido y robusto? ¿extensión? | decisión registrada |
| **Fase 2 · escritura** | 2 feb – 6 mar 2027 | artículo + configuración reproducible | borrador completo |

**Si en R2 se añade un diagnóstico cromosférico** (ruta RADYN o colaboración), el cierre se corre hacia **abril de
2027**: ese es el extremo de los 6 meses.

**Presupuesto de cómputo**, extrapolado del piloto (~2 h de reloj en 6 núcleos para 4 ramas × 3 `τ`):

| Partida | Estimación |
|---|---|
| Una celda del mapa (un `τ`, un `F`) | ~40 min de reloj en 6 núcleos |
| Mapa completo, 3–4 `τ` × 3 `F` | ~8–10 h |
| Duplicados para `σ_num` (temporal + espacial) | ×2–3 sobre lo anterior |
| Variantes de haz para `σ_beam` (6 por flujo) | modesto, solo rama `B0` |
| `τ` > 120 s con `SAFETY_CONDUCTION = 0.1` | ×2–4 por celda afectada |
| **Total realista** | **2–4 días de reloj repartidos en semanas**, no un *cluster* |

El cómputo **no es el cuello de botella**. Lo son las compuertas 2 y 3.

---

## 7. Riesgos y plan B

| Riesgo | Señal temprana | Qué se hace |
|---|---|---|
| El segundo episodio de `A1` resulta ser **artefacto de resolución** | cambia al variar umbrales de refinamiento (compuerta 1) | se reinterpretan las ventanas de `τ` = 30 y 60 s y se acorta la ventana de análisis; el resultado impulsivo no se toca |
| **`τ*` no se puede acotar** ni extendiendo la rejilla ni con pulso débil | el criterio del 5 % sigue fallando en el `τ` más largo | se reporta una **cota inferior** de `τ*` y el dominio explorado (desenlace R-C parcial), en una nota corta |
| `M` queda **bajo `σ_tot`** al incluir `σ_obs` | `σ_obs` del instrumento elegido domina el presupuesto | desenlace **R-B**: se publica "este diagnóstico no puede verlo" y se motiva la ruta cromosférica |
| El eje de flujo **no se puede ampliar** (NaN sin diagnosticar en ≥2.5×10¹⁰) | las ramas revientan al subir `F` | el mapa se reporta con 2 flujos y el techo declarado explícitamente |
| La **puerta RADYN** no abre en el horizonte | sin compilador o sin licencia en enero | se cierra el artículo con *proxies* coronales; la línea cromosférica pasa a extensión E9 (colaboración) |
| Las **condensaciones** dominan la interpretación | el diagnóstico elegido depende del umbral que cae sobre ellas | se elige un diagnóstico integrado (EM, T ponderada) y se declara la condicionalidad |

---

## 8. Lo que esta ruta no podrá afirmar

Decirlo antes, no después:

- **Nada sobre líneas cromosféricas.** HYDRAD calienta analíticamente y radía ópticamente fino, sin transferencia
  NLTE. Mg II, Si IV y Hα exigen RADYN o un colaborador.
- **Nada por encima de `F` ≈ 5×10¹⁰ erg cm⁻² s⁻¹**, donde el solver sigue fallando por una causa no diagnosticada.
- **Las condensaciones y el vaivén son propiedades del modelo**: en un bucle 1D simétrico los dos flujos de
  evaporación chocan y el plasma comprimido se enfría catastróficamente. Todo resultado de memoria aquí es
  condicional a ese tratamiento.
- **Nada sobre si las fulguraciones reales regolpean la misma hebra.** El regolpe en el mismo bucle es el
  **escenario de modelado** del núcleo; que dos pulsos coincidan en el mismo pie no prueba la misma hebra. Eso es
  la extensión E1, con STIX.
- **Un solo bucle y una sola forma de pulso**: nada separa historia de longitud del bucle, de forma de pulso ni de
  asimetría.
- **La novedad es incremental, y se describe así.** Dos episodios separados ya se simularon (Cho et al. 2023, a
  flujos de nanofulguración); que un precalentamiento débil cambie una respuesta fuerte posterior ya se mostró
  (Kerr et al. 2024, con observable). Lo que queda: **pulsos fuertes → fuertes a flujos de fulguración, barrido en
  `τ`, controles emparejados y una regla de decisión.** Hasta cerrar la búsqueda bibliográfica dirigida, no se dice
  "el primero".

---

## 9. Checklist por corrida

Para **cada** corrida de producción, al registro:

- [ ] configuración y revisión del código (`git rev-parse HEAD`);
- [ ] estado inicial y tablas de haz;
- [ ] cadencia de salida;
- [ ] valores de `σ` y tolerancias, **escritos antes** de los contrastes;
- [ ] tiempo de reloj y almacenamiento;
- [ ] **las corridas fallidas** — se quedan en el registro.

Los datos y resultados generados están fuera de git. Citar los solvers, datos atómicos y herramientas
observacionales realmente usados, dentro de sus licencias.

---

## 10. Decisiones pendientes con la supervisora

Cada una tiene un valor por defecto que puedo tomar si no hay preferencia, pero cada una cambia lo que el artículo
puede decir.

| # | Decisión | Mi recomendación por defecto |
|---|---|---|
| **D1** | ¿Diagnóstico primario: **Si IV**, EM caliente, o T ponderada por EM? | **Si IV**: es la moneda de la audiencia, tiene benchmark publicado en HYDRAD y hace `σ_obs` nombrable. Los *proxies* coronales quedan de verificación cruzada |
| **D2** | ¿Qué instrumento fija `σ_obs`? | **IRIS**, si D1 es Si IV. Sigue siendo **bloqueante**: sin instrumento no hay frontera, y la frontera es ahora el producto |
| **D3** | ¿Alcanzar la relajación extendiendo `τ` > 120 s (más caro) o con un pulso 1 más débil? | **pulso 1 más débil**: hace la pregunta contestable sin multiplicar el cómputo |
| **D4** | ¿Vale dos semanas el benchmark de Reep 2016 (compuerta 6)? | **Sí**: valida el *pipeline*, fija el posicionamiento y deja la síntesis de Si IV lista. Es el mejor uso de dos semanas que tiene el proyecto |
| **D5** | ¿Se compromete alguna extensión ahora (STIX / colaboración RADYN)? | **ninguna todavía**: E1 es modular y va después del núcleo (§5.4); decidir en R2 |

---

**Qué leer después:** [00_objectives_and_methodology.md](00_objectives_and_methodology.md) (plan autoritativo),
[07_core_pilot_hydrad.md](07_core_pilot_hydrad.md) (el piloto completo y la decisión R1),
[guia_conceptos_es.md](guia_conceptos_es.md) (la física desde cero),
[03_novelty_and_prior_work.md](03_novelty_and_prior_work.md) §11 (posicionamiento).
