# Respuesta de la atmósfera solar a pulsos sucesivos de electrones: objetivos, hipótesis y diseño metodológico

**Proyecto:** STIX → transporte de electrones → hidrodinámica radiativa (RHD) → diagnósticos sintéticos
**Estado del documento:** propuesta de diseño, sujeta a la revisión de la profesora. Los umbrales marcados como *propuesta* deben fijarse antes de ejecutar la campaña (sección 6.8).

---

## 1. Planteamiento del problema

Durante una llamarada, la emisión de rayos X duros (HXR) suele llegar en **pulsos sucesivos**. Cada pulso corresponde a una inyección de electrones no térmicos que se frena en la atmósfera, la calienta y la pone en movimiento. El primer pulso actúa sobre una atmósfera relajada; el **segundo y el tercero actúan sobre una atmósfera ya modificada**: más caliente, más densa en la corona, parcialmente ionizada y con flujos residuales.

La mayoría de los modelos de referencia simulan un solo pulso sobre una atmósfera inicial. Lo que no está cuantificado de forma sistemática y anclada a observaciones es **cómo cambia la respuesta cuando el pulso llega sobre una atmósfera que aún conserva la historia del anterior**.

### 1.1 Pregunta de investigación

> **¿Cómo responde la atmósfera solar (cromosfera, región de transición y corona) a un segundo o tercer pulso de electrones no térmicos, cuando el espectro de esos pulsos está fijado por observaciones reales de STIX, y en qué se diferencia esa respuesta de la de un primer pulso sobre una atmósfera relajada?**

### 1.2 Subpreguntas

| ID | Subpregunta | Observable principal |
|---|---|---|
| SP1 | ¿Cambia la **profundidad y el perfil de deposición** de energía Q(s,t) entre pulsos? | Q(s,t), columna de masa de máxima deposición |
| SP2 | ¿Cómo cambian **T, n, v, ionización y poblaciones atómicas** respecto de la respuesta a un pulso aislado? | T(s,t), n(s,t), v(s,t), x_H(s,t) |
| SP3 | ¿Cómo se **reparte la energía** (radiación, conducción, entalpía, cinética) en cada pulso? | Balance energético por pulso |
| SP4 | ¿De qué dependen esos cambios: **tiempo de espera, energía previa o parámetros del haz**? | Barridos factoriales (sección 6.5) |
| SP5 | ¿Qué parte de la diferencia **sobrevive** a las incertidumbres de STIX, al ruido y a la resolución instrumental? | Diagnósticos sintéticos con errores propagados |
| SP6 (secundaria) | ¿Se distingue el **recalentamiento del mismo tubo** de la activación de **filamentos independientes** con la misma señal HXR? | Comparación E2 frente a E3 |

SP6 es una comparación derivada y no el objetivo central; solo se aborda si SP1–SP5 ofrecen señales medibles.

### 1.3 Hipótesis de trabajo sobre la geometría

Se asume provisionalmente que los pulsos inciden sobre **el mismo tubo de flujo**. Es una hipótesis operativa que la profesora debe confirmar (sección 12); no se trata como evidencia observacional.

---

## 2. Hipótesis falsables

Cada hipótesis tiene una predicción cuantificable y una condición que la refutaría. Se formulan **antes** de ver resultados.

| ID | Hipótesis (mecanismo físico) | Predicción | Se refuta si |
|---|---|---|---|
| **H0** | *Nula.* La respuesta al pulso k no depende de la historia: es la de un pulso sobre atmósfera relajada. | M̂ ≈ 0 en todas las variables dentro de la incertidumbre | — (es la referencia) |
| **H1** | *Desplazamiento de la deposición.* Dos efectos compiten tras el pulso 1: la compresión de la cromosfera y la ionización llevan la altura de frenado hacia abajo, y el aumento de la densidad coronal por evaporación la lleva hacia arriba. Kennedy et al. (2015) encuentra ambos sentidos en una misma simulación continua. El **signo y la magnitud** del desplazamiento dependen de τ_w/τ_rel y de Ec. | La altura (o columna) del máximo de Q(s,t) del pulso 2 difiere de la del pulso 1 por encima de la incertidumbre numérica y la de STIX, con un signo predicho por el régimen | Δz entre pulsos compatible con cero, o de signo inconsistente con el régimen predicho |
| **H2** | *Memoria hidrodinámica.* Flujos y densidades residuales persisten durante un tiempo de relajación τ_rel; si el tiempo de espera τ_w ≲ τ_rel, la respuesta al pulso 2 queda modificada; si τ_w ≫ τ_rel, tiende a la de un pulso aislado. | M̂(τ_w) decrece monótonamente con τ_w/τ_rel | M̂ no depende de τ_w |
| **H3** | *Blanco cálido.* Con plasma más caliente, los electrones de baja energía se frenan y termalizan de forma distinta, y el calentamiento por debajo de unas pocas veces kT cambia respecto del blanco frío. | La diferencia entre transporte con blanco frío y cálido crece con la temperatura previa y con la cercanía de Ec a la energía térmica | Diferencia inferior a la incertidumbre numérica |
| **H4** | *Observabilidad.* La diferencia M en al menos un diagnóstico (SXR, Fe XVIII, Hα o líneas de IRIS) supera la incertidumbre total tras incluir STIX, ruido, cadencia y resolución. | d/σ_tot por encima del umbral preregistrado en algún diagnóstico y régimen | Ningún diagnóstico lo supera: la memoria es **no detectable** con el instrumento |

Un resultado negativo de H4, con el régimen bien acotado, **también es un resultado** (límite de detectabilidad).

---

## 3. Objetivo general

Cuantificar, mediante simulación radiativa-hidrodinámica anclada a espectros reales de electrones inferidos de STIX, **cómo responde la atmósfera solar al segundo y tercer pulso de electrones y en qué medida esa respuesta conserva la memoria de los pulsos previos**, y entregar un pipeline reproducible que conecte un espectro STIX con la respuesta atmosférica sintética.

---

## 4. Objetivos específicos

Cada objetivo tiene método, entradas, salidas, criterio de éxito y dependencias. Los criterios de éxito son comprobables.

### OE1 — Seleccionar y caracterizar el evento

- **Método:** aplicar los criterios de inclusión de la sección 6.1 a la lista de llamaradas de STIX; verificar visibilidad, saturación, cadencia y correcciones de tiempo Solar Orbiter–Tierra.
- **Entradas:** catálogo de STIX; datos de GOES, AIA/HMI y, si existen, IRIS y Hα.
- **Salidas:** expediente del evento (D1) con intervalos, pulsos identificados, cobertura y calibraciones.
- **Criterio de éxito:** al menos dos pulsos HXR resolubles, cobertura GOES/AIA y una evaluación documentada de la posición de la fuente (mismo sitio o no).
- **Depende de:** acceso a datos.

### OE2 — Inferir el haz de electrones de cada pulso

- **Método:** ajuste espectral con respuesta instrumental (térmico + no térmico de blanco grueso o cálido) por pulso, con incertidumbres y covarianzas conjuntas; conversión a (Ṅ, Ec, δ, P, F).
- **Entradas:** espectrogramas STIX; matriz de respuesta; fondo; área A de la fuente (imagen STIX, AIA o IRIS).
- **Salidas:** tabla de parámetros por pulso con covarianzas (D2).
- **Criterio de éxito:** parámetros con incertidumbre cuantificada; degeneración térmica/no térmica y cota inferior de Ec **declaradas**; área A con incertidumbre propagada.
- **Depende de:** OE1.

### OE3 — Establecer y verificar la cadena de transporte y RHD

- **Método:** reproducir un caso publicado (Allred et al. 2020; Carlsson et al. 2023); verificar acoplamiento autoconsistente del haz con la atmósfera **que evoluciona**; convergencia espacial y temporal; balance de energía.
- **Entradas:** RADYN con Fokker–Planck (versión F-CHROMA, ver `docs/04_acceso_a_radyn.md`); versiones y configuraciones.
- **Salidas:** informe de verificación (D4) y configuraciones reproducibles.
- **Criterio de éxito:** reproducción del caso de referencia dentro de una tolerancia fijada de antemano (*propuesta:* diferencias de T y n máximas por debajo del 10 % frente a la publicación); balance de energía cerrado (*propuesta:* error < 1 % de la energía inyectada).
- **Depende de:** acceso al solver y al clúster (sección 12).

### OE4 — Cuantificar la respuesta a pulsos sucesivos

- **Método:** matriz de experimentos E1–E5 (sección 6.4) con 2 y 3 pulsos, con parámetros inferidos en OE2; las métricas de memoria de la sección 6.6.
- **Entradas:** D2 y D4.
- **Salidas:** base de simulaciones con esquema documentado (D5) y métricas M_X(τ) con incertidumbres (D6).
- **Criterio de éxito:** M_X(τ) calculado para T, n, v, ionización, Q y profundidad de deposición, con incertidumbres numéricas y observacionales.
- **Depende de:** OE2, OE3.

### OE5 — Identificar qué controla la memoria

- **Método:** barridos factoriales (tiempo de espera, energía previa, cociente de flujos, Ec y δ del pulso nuevo) y análisis de sensibilidad (sección 6.5).
- **Salidas:** mapa de régimen M̂(τ_w/τ_rel, E_prev/E_new, …) y estimación de τ_rel (D6).
- **Criterio de éxito:** separar de forma cuantitativa el efecto de cada factor; documentar los regímenes donde la memoria es despreciable.
- **Depende de:** OE4.

### OE6 — Sintetizar diagnósticos y compararlos con las observaciones

- **Método:** curvas SXR/GOES y AIA, Fe XVIII, Hα y líneas de IRIS según cobertura; respuestas instrumentales; test de Neupert por pulso; propagación de incertidumbres.
- **Salidas:** observables sintéticos y comparación con datos (D7).
- **Criterio de éxito:** comparación cuantitativa con estadístico definido de antemano; discrepancias que los parámetros permitidos por STIX no resuelvan, **documentadas y no ocultas**.
- **Depende de:** OE4; datos de OE1.

### OE7 — Evaluar la detectabilidad (y, si procede, SP6)

- **Método:** aplicar la regla de decisión de la sección 6.8 a cada diagnóstico; comparar E2 con E3a/E3b.
- **Salidas:** tabla de detectabilidad por diagnóstico y régimen (D8).
- **Criterio de éxito:** conclusión explícita: detectable, no detectable o degenerado, con el régimen que lo sostiene.
- **Depende de:** OE4–OE6.

### OE8 — Empaquetar el pipeline y redactar el manuscrito

- **Método:** pipeline reproducible “espectro STIX → respuesta atmosférica sintética”; manuscrito de prueba de concepto de un evento.
- **Salidas:** repositorio con pruebas, documentación y manifiestos (D9); manuscrito (D10).
- **Criterio de éxito:** un tercero reproduce las figuras principales a partir de los datos y las configuraciones archivadas.
- **Depende de:** todos los anteriores.

---

## 5. Resultados esperados

Los resultados se formulan como posibilidades abiertas, no como promesas.

| Escenario | Qué se observaría | Aporte |
|---|---|---|
| **A. Memoria medible** | M̂ significativo en la profundidad de deposición, T, v o ionización para τ_w ≲ τ_rel | Mecanismo físico identificado y régimen en que domina |
| **B. Memoria real pero no detectable** | M̂ ≠ 0 en la simulación, pero por debajo de σ_tot en todos los diagnósticos | **Límite de detectabilidad** acotado (resultado válido) |
| **C. Memoria despreciable** | M̂ ≈ 0 para los parámetros de STIX | Justifica modelar cada pulso como aislado en ese régimen |
| **D. Degeneración** | E2 y E3 indistinguibles con la señal disponible | Condiciones en que la geometría no se puede inferir |

Resultados cuantitativos que se persiguen en cualquier escenario:

1. Tiempo de relajación τ_rel y su dependencia con los parámetros del haz.
2. Desplazamiento de la profundidad de deposición entre pulsos, con su incertidumbre.
3. Reparto energético por pulso y su cambio con la historia.
4. Sensibilidad de los diagnósticos a la incertidumbre de STIX.
5. Concordancia (o no) del test de Neupert pulso a pulso.

No se promete detección, novedad ni una revista determinada.

---

## 6. Diseño metodológico

### 6.1 Criterios de selección del evento

| Criterio | Requisito | Tipo |
|---|---|---|
| Pulsos HXR | ≥ 2 pulsos resolubles; contraste y estadística suficientes para un ajuste por pulso | Obligatorio |
| Espectros STIX | Ciencia, sin saturación; atenuador identificado | Obligatorio |
| Contexto | GOES y AIA | Obligatorio |
| Diagnósticos cromosféricos | IRIS y/o Hα si son centrales; AIA/HMI no sustituyen a Hα | Deseable |
| Geometría | Visibilidad desde Tierra y Solar Orbiter; evolución espacial; **corrección del tiempo de viaje de la luz** antes de atribuir pulsos al mismo sitio | Obligatorio |

La decisión se registra en una tabla de candidatos con los criterios satisfechos y descartados.

### 6.2 Análisis de los datos de STIX

1. **Reducción:** fondo, correcciones de atenuador, apilamiento, tiempo de integración por pulso.
2. **Modelo:** componente térmica (isoterma) más no térmica de blanco grueso; contraste con blanco cálido.
3. **Ajuste:** con la respuesta instrumental completa; estimar la distribución a posteriori de θ = (Ṅ, Ec, δ, T, EM) por pulso, y sus covarianzas.
4. **Cautelas físicas:** STIX observa **fotones**, no electrones; el índice fotónico no es el del electrón; Ec puede estar débilmente acotado (cota superior o inferior); degeneración térmico/no térmico a baja energía.
5. **Conversión:** P = Ṅ·Ec·(δ−1)/(δ−2); F = P/A. Cada magnitud conserva sus unidades y se propaga A con su incertidumbre.

### 6.3 Cadena de transporte y RHD

| Etapa | Requisito físico | Consecuencia metodológica |
|---|---|---|
| Transporte | Fokker–Planck con colisiones; corriente de retorno y blanco cálido cuando corresponda | Verificar qué física incluye la versión concreta |
| Acoplamiento | Q(s,t) debe **recalcularse con la atmósfera que evoluciona** | Un perfil Q precalculado sobre una atmósfera estática **no es válido** para estudiar memoria |
| RHD | Transferencia radiativa fuera del equilibrio local para la cromosfera | RADYN+FP (preferido) o FLARIX |
| HYDRAD | Calentamiento analítico, radiación ópticamente delgada | Se retira del proyecto tras verificar RADYN; no se usan dos códigos |

Regla de no doble conteo: el calentamiento del haz entra en la ecuación de energía **una sola vez**.

### 6.4 Matriz de experimentos

Núcleo (preguntas SP1–SP5) y comparación (SP6):

| ID | Montaje | Papel |
|---|---|---|
| E1 | Pulso en atmósfera relajada | Respuesta de referencia R_rel |
| E2 | 2 o 3 pulsos en el mismo tubo, sin reinicio | Objeto de estudio: respuesta con historia |
| E5 | Pulso 1 y relajación, sin pulso 2 | Contrafactual para aislar la respuesta al pulso nuevo |
| E4 | Calentamiento continuo, igual energía | Control de la distribución temporal |
| E3a/E3b | Filamentos independientes, dos asignaciones de área | Comparación SP6 |

Para el pulso 3 se necesita además el contrafactual «pulsos 1 y 2 sin pulso 3» (E5′). Las tablas de entrada de E1–E5 ya se generan con `src/experiments.py` (caso sintético).

### 6.5 Diseño factorial y propagación de incertidumbre

| Factor | Niveles propuestos (a fijar con pilotos) |
|---|---|
| Número de pulsos | 1, 2, 3 |
| Tiempo de espera τ_w | Múltiplos de τ_rel estimado (< 1, ≈ 1, > 1) |
| Cociente de energía pulso previo / nuevo | < 1, 1, > 1 |
| Ec y δ del pulso nuevo | Dentro del intervalo permitido por STIX |
| Área A / flujo F | Dentro de la incertidumbre de A |

- **Barrido de un factor a la vez** desde el caso central, y luego un diseño espacialmente uniforme (p. ej. hipercubo latino) sobre el posterior de STIX.
- **Propagación:** muestras del posterior → simulaciones → distribución de las métricas. El número de muestras se decide tras los pilotos (coste medido, no supuesto).
- **Sensibilidad:** correlación de rangos o índices de Sobol sobre M̂.
- Todos los casos comparados tienen **la misma energía total y la misma área** salvo que la diferencia sea el factor estudiado y se declare.

### 6.6 Definición operativa de memoria

Sean X(s,t) una variable de estado (T, n, v, x_H, Q, columna de deposición), X₀ su valor inicial, t_k el inicio del pulso k y τ = t − t_k.

- **Respuesta con historia (contrafactual pareado):** R_hist(τ) = X_con k(t_k+τ) − X_sin k(t_k+τ), donde ambas simulaciones comparten la misma historia hasta t_k. Para k = 2 es E2 − E5.
- **Respuesta en atmósfera relajada:** R_rel(τ) = X_E1(t₀+τ) − X₀.
- **Memoria:** M_X(τ) = R_hist(τ) − R_rel(τ); normalizada M̂_X = ‖M_X‖ / ‖R_rel‖ con una norma definida de antemano (L2 en s y τ, o el valor en el pico).
- **Tiempo de relajación:** τ_rel, el tiempo en que una variable de referencia de E5 cae a una fracción fijada de su pico (*propuesta:* 1/e). En RADYN, un término de calentamiento de fondo mantiene el equilibrio inicial, de modo que la relajación es hacia ese estado; τ_rel se mide con ese término y se declara.
- **Deposición:** columna de masa y altura del máximo de Q y del centroide de Q; desplazamiento entre pulsos.
- **Reparto energético:** fracciones radiada, conducida, advectada (entalpía) y cinética por pulso.

Esta definición evita confundir el residuo del pulso anterior con la respuesta al pulso nuevo.

### 6.7 Diagnósticos sintéticos y comparación con los datos

| Diagnóstico | Tratamiento | Cautela |
|---|---|---|
| SXR / GOES | Integral con respuesta del instrumento | Dependiente de la medida de emisión |
| AIA | Respuesta por canal | No identificar AIA 94 Å con Fe XVIII sin más |
| Fe XVIII | Líneas ópticamente delgadas, equilibrio o no equilibrio de ionización | Requiere temperatura >~6 MK |
| Hα, IRIS | Transferencia radiativa adecuada (RADYN o postproceso) | No equiparar con la emisión delgada de HYDRAD |

**Efectos instrumentales:** cadencia, exposición, función de respuesta espacial, mezcla de estructuras y ruido, incluidos en el modelo directo.

**Test de Neupert** (dF_SXR/dt ∝ F_HXR): aplicado **pulso a pulso**. Es una comprobación **complementaria**, no una prueba única de la geometría; el desacuerdo se estudia dentro de la incertidumbre de STIX y **no se corrige reajustando el haz hasta forzar el acuerdo**.

### 6.8 Reglas de decisión (a fijar antes de simular)

- **Detectabilidad:** para cada diagnóstico D, d = |D_A − D_B| frente a σ_tot² = σ_STIX² + σ_instr² + σ_num². Se declara diferencia detectable si d/σ_tot > k (*propuesta:* k = 3).
- **Tolerancias numéricas:** convergencia espacial/temporal, conservación de energía y reproducción del caso publicado (OE3).
- **Casos fallidos:** los no convergentes **se registran y se reportan**; no se excluyen en silencio.
- **Preregistro:** umbrales, normas y estadísticos se escriben en el repositorio antes de ejecutar la campaña de producción.

### 6.9 Verificación, validación y cuantificación de incertidumbre

| Nivel | Qué se comprueba | Cómo |
|---|---|---|
| Código | Tablas de entrada, unidades y conservación | Pruebas automáticas (ya existen 30) |
| Numérico | Convergencia en malla y paso; balance de energía | Refinamiento y casos decisivos |
| Físico | Caso publicado reproducido | OE3 |
| Observacional | Curvas sintéticas frente a datos | OE6 |
| Incertidumbre | Posterior de STIX, ruido, numérica | Propagación (6.5) |

### 6.10 Reproducibilidad y uso del clúster

Registrar versiones del solver, banderas del compilador, atmósfera inicial, haz de entrada, cadencia de salida, tiempo de pared, CPU, memoria y almacenamiento. Casos independientes como trabajos separados; no suponer escalado de una corrida con más núcleos. Cada corrida lleva un **manifiesto** (entrada, versión, resultado). El pipeline debe poder ejecutarse de extremo a extremo con una orden documentada.

---

## 7. Productos y salidas esperadas

| ID | Producto | Formato / ubicación | Criterio de aceptación | Estado |
|---|---|---|---|---|
| D1 | Expediente del evento | Markdown + tabla de candidatos | Criterios 6.1 evaluados | Pendiente |
| D2 | Parámetros del haz por pulso con covarianzas | CSV/JSON y figuras | Incertidumbres y degeneraciones declaradas | Pendiente |
| D3 | Generador de tablas de haz y matriz de experimentos | `src/beam_tables.py`, `src/experiments.py` | Energía conservada, 30 pruebas | **Hecho (sintético)** |
| D4 | Informe de verificación del solver | Markdown + figuras | Caso publicado reproducido | Pendiente |
| D5 | Base de simulaciones | HDF5 + manifiestos | Esquema con unidades y coordenadas | Pendiente |
| D6 | Métricas de memoria y mapa de régimen | Código + figuras | Definiciones de 6.6 | Pendiente |
| D7 | Diagnósticos sintéticos y comparación | Código + figuras | Estadístico preregistrado | Pendiente |
| D8 | Tabla de detectabilidad | Markdown + figura | Regla 6.8 aplicada | Pendiente |
| D9 | Pipeline reproducible | Repositorio | Un tercero reproduce las figuras | Parcial |
| D10 | Manuscrito de prueba de concepto | LaTeX/Markdown | Métodos, incertidumbres, límites | Pendiente |
| D11 | Informe de infraestructura de pulsos | `docs/02_informe_experimentos_pulsos.html` | — | **Hecho** |

---

## 8. Fases y puertas de decisión

| Fase | Contenido | Puerta de salida |
|---|---|---|
| F0 | Infraestructura de pulsos sintéticos (hecha) | Pruebas pasan |
| F1 | Elegir solver y acceso; reproducir caso publicado | Verificación aprobada (OE3) |
| F2 | Seleccionar evento y ajustar STIX | D1 y D2 completos |
| F3 | Pilotos de coste y estabilidad en el clúster | Presupuesto de campaña realista |
| F4 | Preregistrar umbrales y diseño factorial | Documento firmado |
| F5 | Campaña de producción E1–E5 y barridos | Casos documentados, incluidos los fallidos |
| F6 | Diagnósticos sintéticos y comparación | D7 completo |
| F7 | Detectabilidad, redacción y empaquetado | D8–D10 |

F1 y F2 pueden avanzar en paralelo; F5 no empieza sin F1, F2 y F4.

---

## 9. Riesgos y mitigaciones

| Riesgo | Efecto | Mitigación |
|---|---|---|
| Sin acceso a RADYN+FP o FLARIX | No hay respuesta cromosférica NLTE | Definir alcance con HYDRAD (corona/evaporación) y declarar la limitación |
| Ec débilmente acotado | Profundidad de deposición incierta | Propagar posterior; análisis de sensibilidad |
| Degeneración térmico/no térmico | Parámetros sesgados | Ajustes alternativos y comparación de modelos |
| Área de la fuente desconocida | F y regímenes cambian | Tratar A como parámetro con incertidumbre |
| Fallo numérico (NaN en HYDRAD con haz) | Casos perdidos | Diagnóstico acotado; registrar los fallos |
| Pocos fotones por pulso | Ajuste ruidoso | Criterios de selección y agregación justificada |
| Coste de cómputo mayor al supuesto | Campaña recortada | Pilotos antes de presupuestar |
| Pulsos en lugares distintos | Hipótesis del mismo tubo falsa | Evaluar posición (OE1) y tratar el caso como SP6 |

---

## 10. Límites del alcance

- No es una red neuronal: es simulación física.
- Un solo evento como prueba de concepto; no se generaliza a toda la población de llamaradas.
- 1D a lo largo de un tubo de flujo; no hay MHD 3D, salvo que se justifique con una motivación física propia.
- STIX no determina por sí solo la geometría ni el área.
- No se promete detección, novedad ni una revista.
- No se envían correos, no se publican resultados y no se consume cuota de clúster sin acuerdo previo.

---

## 11. Estado actual frente al plan

| Elemento | Estado |
|---|---|
| Código fuente de HYDRAD | Incluido; compila en macOS con dos `#include` adicionales |
| Generador de tablas y matriz E1–E5 | Hecho, con parámetros **sintéticos** |
| Informe de infraestructura | Hecho |
| Evento, ajuste STIX, datos | **No iniciados** |
| RADYN (versión F-CHROMA) | **Solver único elegido.** Descargado y leído (FP `ibeam=8`, `ftab.dat`, reinicio; ver `docs/04_acceso_a_radyn.md`); **sin compilar** (falta Fortran y la biblioteca CDF); licencia sin confirmar |
| RADYN+FP más reciente / FLARIX | Sin acceso confirmado |
| HYDRAD con haz | **NaN abierto** (flujos de 10¹⁰ a 5×10¹⁰) |
| Diagnósticos de memoria (6.6) | Definidos; sin implementar |

---

## 12. Preguntas abiertas para la profesora

1. ¿Qué significa exactamente «impacto»: pulso de electrones sobre el mismo tubo?
2. ¿Qué solver se usará (RADYN+FP, FLARIX) y qué acceso y cuota de clúster hay? ¿Hay permiso del grupo de Oslo para usar la versión F-CHROMA de RADYN y qué versión de Fokker–Planck incluye?
3. ¿Hα o IRIS son diagnósticos centrales para el artículo?
4. ¿Hay un evento preferido o criterios de selección propios?
5. ¿Se acepta el contrafactual pareado (6.6) como definición de memoria?
6. ¿Qué umbral de detectabilidad y qué tolerancias de verificación se consideran adecuados?
7. ¿La comparación con filamentos independientes (SP6) es parte del artículo o un anexo?

---

## 13. Referencias

Incluidas en el repositorio (README y skill):

- Allred, Kowalski & Carlsson (2015), ApJ 809, 104.
- Allred et al. (2020), ApJ 902, 16.
- Carlsson et al. (2023), A&A 673, A150.
- Kennedy et al. (2015), RADYN impulsado por espectros HXR.
- Krucker et al. (2020), A&A 642, A15 (STIX).
- Bradshaw & Mason (2003); Bradshaw & Cargill (2013); Reep et al. (2019) (HYDRAD).
- Litwicka et al. (2025), ApJ (FLARIX; calentamiento continuo frente a pulsos en filamentos, con VAL-C precalentada); resumen de congreso de marzo de 2026 con STIX/IRIS/CHASE (distinguir resumen de artículo).

La evaluación de novedad y los antecedentes adicionales están en `docs/03_novedad_y_antecedentes.md`.

Conceptos citados por su fuente clásica (consultar la referencia exacta antes de citar): Brown (1971) y Emslie (1978) para el blanco grueso colisional; Hawley & Fisher (1994) para el calentamiento por haz implementado en HYDRAD; Neupert (1968) para la relación entre SXR y HXR. La formulación de blanco cálido debe verificarse en la literatura (p. ej. los trabajos de Kontar y colaboradores) antes de elegirla.

Esta lista procede de una exploración preliminar, no de una revisión exhaustiva; hay que actualizarla al preparar el manuscrito.
