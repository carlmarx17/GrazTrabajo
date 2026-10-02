# Antecedentes y evaluación de novedad

**Fecha de la búsqueda:** 2026-10-02. **Alcance:** exploración preliminar con búsqueda web general y lectura de resúmenes en las páginas de los editores y arXiv. **No es una revisión exhaustiva**: no se consultó ADS, no se leyeron los textos completos salvo donde se indica, y varios sitios (A&A) bloquearon la descarga. Cualquier afirmación de «no encontrado» significa *no encontrado en esta búsqueda*, no *no existe*.

## 1. Qué ya existe

| Trabajo | Qué hace | Relación con este proyecto | Fuente |
|---|---|---|---|
| **Litwicka, Heinzel & Kašparová (2025)**, ApJ | FLARIX NLTE. Compara calentamiento continuo (F = 10¹⁰ erg cm⁻² s⁻¹, 6.5 s) con 4 pulsos consecutivos en filamentos (cada uno 25 % del área, F = 4×10¹⁰, 2 s, solapados 0.5 s). Usa VAL-C y una VAL-C precalentada como condiciones iniciales. **Sin datos observacionales analizados.** El filamentario reduce Hα un 36–46 % y Mg II k un 51–53 %. | Ocupa el planteamiento «continuo frente a pulsos en filamentos». El precalentamiento es una condición inicial, no la historia de un pulso previo. | [IOP](https://iopscience.iop.org/article/10.3847/1538-4357/adc393) |
| **Litwicka et al. (resumen, congreso de marzo de 2026)** | FLARIX, llamarada X9 del 3 de octubre de 2024, con **STIX, IRIS y CHASE**. Compara calentamiento continuo y filamentario; el filamentario se acerca más a Hα y Mg II k. Es un **resumen**, no un artículo. | **Competencia directa** en la línea «STIX + filamentos»; un artículo puede estar en preparación. | [Resumen](https://plan.events.mpg.de/event/453/contributions/3104/) |
| **Kennedy et al. (2015)** | RADYN guiado por parámetros del haz que evolucionan, obtenidos de espectros RHESSI de la X1.5 del 9 de marzo de 2011 (110 s de calentamiento + 300 s). Calculan la profundidad de frenado durante la evolución. | RHD guiado por HXR observados a lo largo de toda la fase impulsiva ya existe. No se vio (solo resumen) un análisis de memoria pulso a pulso. | [arXiv](https://arxiv.org/abs/1504.07541) |
| **Rubio da Costa et al. (2016)** | Modelo multihilo con RADYN y flujo de electrones inferido de RHESSI, para la X1.0 del 29 de marzo de 2014; compara con IRIS e IBIS. | Idem: modelado guiado por datos con múltiples hilos. | [arXiv](https://arxiv.org/abs/1603.04951) |
| **Collier et al. (2024)**, A&A | Observaciones EUI/FSI de llamaradas de STIX; incluye RADYN con un haz triangular de 45 s, Ec ≈ 13 keV y δ = 5, a partir del ajuste OSPEX de **la primera ráfaga** no térmica. | **STIX → RADYN ya existe** para un solo pulso. El pipeline en sí no es novedoso. | [arXiv](https://arxiv.org/abs/2411.09319) |
| **Reep et al. (2016)** | Modelo RHD multihilo: calentamiento sucesivo de hebras **independientes** reproduce corrimientos al rojo largos de la región de transición; un modelo de bucle único no. | Evidencia a favor de hilos independientes en un evento; ataca el supuesto de «mismo tubo». | [arXiv](https://arxiv.org/abs/1607.06684) |
| **Dennis & Zarro (1993)** | En 66 eventos de HXRBS, en 20 la derivada de SXR sigue alta cuando el HXR ya cayó, lo que se interpreta como energía liberada en un bucle ya afectado. (Cifras tomadas de un resumen de búsqueda; verificar en el original.) | Antecedente observacional de la idea de «bucle ya afectado», sin simulación del haz. | [Springer](https://link.springer.com/doi/10.1007/BF00662178) |
| **Qiu (2021)** | Efecto Neupert con UV de pies; muchos eventos impulsivos no reproducen bien SXR y un modelo de dos fases lo hace mejor. | Relevante para el test de Neupert pulso a pulso. | [arXiv](https://arxiv.org/abs/2101.11069) |

No leídos por falta de acceso: Polito et al. 2022 (nanocalentamientos con RADYN; [A&A](https://www.aanda.org/articles/aa/full_html/2022/03/aa42842-21/aa42842-21.html)) y A&A 710, A105 (2026). Pueden tocar calentamientos repetidos; hay que mirarlos.

**Nota de fiabilidad:** el resumen automático de una búsqueda atribuyó a Litwicka (2025) el uso de RADYN+FP; la página del editor dice FLARIX. Se toma la página del editor. Conviene desconfiar de los resúmenes de búsqueda y comprobar cada dato en la fuente.

## 2. Qué no se encontró (con las limitaciones anteriores)

1. Un estudio que **cuantifique la «memoria»** de una atmósfera, es decir, la respuesta al pulso k con la misma historia, con y sin ese pulso (contrafactual pareado, `docs/00_objetivos_y_metodologia.md`, sección 6.6).
2. Un **mapa de régimen** de esa memoria frente a tiempo de espera/τ_rel y cociente de energías, con parámetros fijados por STIX y su incertidumbre propagada.
3. Un **límite de detectabilidad** de esa memoria en diagnósticos sintéticos (SXR, Fe XVIII, Hα, IRIS), con incertidumbre de STIX, cadencia y resolución incluidas.
4. Un **test de Neupert pulso a pulso** acoplado a un modelo RHD que conserva el estado entre pulsos.

## 3. Evaluación de novedad

| Enfoque posible | Novedad estimada | Motivo |
|---|---|---|
| Pipeline «espectro STIX → respuesta cromosférica» | **Baja** | Collier et al. (2024) ya hace STIX → RADYN para un pulso; Kennedy (2015) y Rubio da Costa (2016) lo hicieron con RHESSI. Útil como infraestructura, no como aportación. |
| «STIX + filamentos independientes frente a continuo» | **Baja y arriesgada** | Litwicka et al. (2025, 2026) ocupan esta línea con FLARIX y STIX/IRIS. |
| «Efecto cualitativo: un haz sobre un bucle ya modificado deposita distinto» | **Baja** | Es esperable y está sugerido en la literatura (evolución de la profundidad de frenado en Kennedy 2015). |
| **Cuantificar la memoria del mismo tubo (contrafactual pareado) + mapa de régimen + detectabilidad con STIX** | **Moderada, aún por confirmar** | No se encontró en esta búsqueda. Es la formulación más defendible, pero depende de una búsqueda más exhaustiva. |

**Lectura honesta:** hay novedad plausible **solo en el planteamiento cuantitativo y de detectabilidad**, no en el uso de STIX, de varios pulsos ni de atmósferas precalentadas. La estrategia sugerida es que el artículo se defina por la métrica de memoria y el límite de detectabilidad, y que la comparación con filamentos independientes sea un control, no el eje.

## 4. Riesgos para la publicación

- **Competencia activa.** El grupo de Litwicka trabaja con STIX, IRIS y CHASE en una llamarada concreta (X9, 3 de octubre de 2024). Evitar ese evento o coordinar; revisar si ya hay preprint.
- **Objeción previsible.** Un revisor puede objetar que «el efecto es conocido»; hay que mostrar la cuantificación y los regímenes, no el efecto cualitativo.
- **Dependencia del solver.** Litwicka usa FLARIX; usar RADYN+FP aporta una verificación independiente, pero exige acceso (pregunta abierta con la profesora).
- **Un solo evento** limita la generalización; el diseño es de prueba de concepto.

## 5. Búsqueda que falta (antes de comprometer meses de trabajo)

1. **ADS y arXiv**, con combinaciones de: *RADYN* / *FLARIX* / *Fokker-Planck* × *multiple heating episodes* / *successive* / *repeated* / *pre-heated* / *memory* / *history*; *STIX* × *radiative hydrodynamic*; *Neupert* × *individual pulses*.
2. **Citas hacia adelante** de Litwicka (2025), Kennedy (2015), Collier (2024) y Rubio da Costa (2016), para ver quién los continuó.
3. **Texto completo** de Kennedy (2015), Rubio da Costa (2016), Collier (2024) y Litwicka (2025): comprobar si analizan la respuesta a ráfagas sucesivas.
4. Los dos trabajos no leídos (Polito 2022 y A&A 710, A105).
5. **Consultar a la profesora** y a su red: si conoce preprints del grupo de Litwicka o planes en curso.
6. Repetir la búsqueda justo antes de enviar el manuscrito.
