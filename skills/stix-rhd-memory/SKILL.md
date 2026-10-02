---
name: stix-rhd-memory
description: Orientar el diseño, las simulaciones y la escritura del paper STIX/RHD sobre la respuesta cromosférica al segundo o tercer pulso de electrones. Usar al trabajar en este proyecto, sus experimentos con RADYN/FP, sus diagnósticos o su pipeline reproducible.
---

# STIX/RHD: memoria atmosférica ante pulsos sucesivos

## Propósito y decisiones del proyecto

El producto final es un paper científico y un pipeline reproducible que conecten
espectros STIX con la respuesta atmosférica a inyecciones sucesivas de electrones.
El interés central es el segundo o tercer pulso sobre una atmósfera modificada por
los anteriores. El usuario prevé acceso a un clúster; sus recursos y cuota aún no
se han especificado. Es simulación física, no entrenamiento de una red neuronal.

Hipótesis de trabajo: los «impactos» son pulsos de electrones sobre el mismo tubo
de flujo. El usuario lo considera probable; falta confirmar el significado exacto
con su profesora. No tratar esa interpretación como evidencia observacional.

Decisión (2026-10-02): **un solo solver, RADYN con Fokker–Planck**, no dos códigos.
La distribución F-CHROMA de RADYN (descargada de la Universidad de Oslo) incluye FP
(`ibeam=8`, versión de 2015, con corriente de retorno opcional), haz dependiente del
tiempo (`ftab.dat`) y reinicio; la licencia está sin confirmar y no se redistribuye.
Detalles, formato del haz y puerta de verificación: docs/04_acceso_a_radyn.md.
HYDRAD (solo calentamiento analítico, radiación ópticamente delgada) se retira del
proyecto cuando RADYN reproduzca un modelo publicado de F-CHROMA. No equiparar nunca
el calentamiento analítico de HYDRAD con Fokker–Planck. FLARIX queda como alternativa
si no se confirma la licencia de RADYN.

## Pregunta y resultado al que se quiere llegar

Determinar cómo responde la atmósfera (cromosfera, región de transición y corona) a
un segundo o tercer pulso de electrones, con los pulsos fijados por espectros reales
de STIX, y en qué se diferencia de la respuesta a un primer pulso sobre una atmósfera
relajada. La memoria se mide con un contrafactual pareado: la respuesta al pulso k es
la diferencia entre dos corridas con la misma historia hasta t_k, con y sin ese pulso
(definición en docs/00_objetivos_y_metodologia.md, sección 6.6).

Comparación secundaria: distinguir el recalentamiento del mismo tubo de la activación
sucesiva de filamentos independientes bajo restricciones compatibles con STIX.

Se busca identificar el mecanismo físico, el régimen donde importa, los
observables que lo revelan y las condiciones donde la memoria no es detectable.
Un límite de detectabilidad bien establecido también es un resultado.
No prometer detección, novedad, aceptación editorial ni una revista determinada.
Objetivos específicos, hipótesis falsables, entregables y reglas de decisión están en
docs/00_objetivos_y_metodologia.md.

## Objetivos científicos

1. Seleccionar un evento con espectros STIX de ciencia y varios pulsos resolubles,
   con GOES y AIA; priorizar espectroscopia IRIS y datos Hα si son diagnósticos
   centrales. AIA/HMI e IRIS no sustituyen una observación de Hα. Comprobar
   visibilidad, saturación, cadencia, evolución espacial y correcciones temporales
   entre Solar Orbiter y la Tierra antes de atribuir los pulsos al mismo lugar.
2. Inferir del ajuste de cuentas y respuesta instrumental los parámetros del haz
   y su evolución: Ec, índice electrónico δ y tasa de inyección. Conservar sus
   incertidumbres conjuntas y degeneraciones térmico/no térmico; Ec puede estar
   débilmente acotado. STIX observa fotones, no electrones directamente, y el índice
   fotónico no es intercambiable con δ.
3. Transportar el haz en una atmósfera que evoluciona y calcular la deposición
   Q(s,t). Acoplarla de forma coherente a la RHD; verificar qué física incluye la
   versión concreta de FP, incluidas colisiones y, cuando corresponda, corriente
   de retorno. Evitar contar dos veces el calentamiento del haz.
4. Cuantificar el cambio entre pulsos en temperatura, densidad, velocidad,
   ionización, profundidad de deposición y reparto energético. Separar los efectos
   del tiempo de espera, la energía previa y las condiciones iniciales.
5. Sintetizar un conjunto viable de diagnósticos según la cobertura real:
   Hα, líneas de IRIS, emisión coronal/Fe XVIII y curvas GOES/AIA/STIX. Usar el
   tratamiento de transferencia y respuesta instrumental apropiado para cada uno;
   no identificar sin más AIA 94 Å con Fe XVIII. No exigir todos para el primer paper.
6. Evaluar si las diferencias entre escenarios sobreviven al ruido, exposición,
   resolución espacial y temporal, mezcla de estructuras e incertidumbres del haz.
   La comparación Neupert es complementaria, no prueba única de la geometría
   de calentamiento ni causa suficiente para reajustar el haz hasta forzar acuerdo.

## Experimentos que deben sostener la comparación

| Experimento | Función |
| --- | --- |
| Pulso aislado en atmósfera relajada | Respuesta de referencia |
| Dos o tres pulsos en la misma atmósfera | Medir efectos de la historia térmica y dinámica |
| Pulsos en filamentos independientes | Alternativa espacialmente no resuelta |
| Calentamiento continuo con energía total comparable | Control de duración y distribución temporal de energía |
| Primer pulso seguido de enfriamiento, sin segundo pulso | Distinguir emisión residual de la respuesta al nuevo haz |

Evolucionar continuamente entre pulsos: no restablecer temperatura, velocidades
ni poblaciones atómicas. Una reanudación debe conservar el estado necesario del
solver. No sumar respuestas de pulsos aislados para representar recalentamiento
no lineal; la suma de emisiones solo representa estructuras independientes bajo
las hipótesis geométricas y radiativas que se documenten.

Comparar potencia total y áreas de forma explícita. La tasa de electrones [s⁻¹],
la potencia [erg s⁻¹], el flujo energético [erg cm⁻² s⁻¹] y Q [erg cm⁻³ s⁻¹]
son magnitudes diferentes. Para una ley simple sin corte superior, δ > 2:
P = Ndot × Ec × (δ−1)/(δ−2), con Ec convertido a erg; F = P/A.
Adaptar esa conversión a cortes finitos u otras distribuciones. Propagar la
incertidumbre en A y la asignación a cada pie/filamento; conservar
P_total(t) = Σ A_i F_i(t) en comparaciones de fragmentación equivalentes.

## Uso del clúster y validación

Empezar reproduciendo un caso publicado con versión y configuración documentadas.
Medir tiempo de pared, CPU, memoria, almacenamiento y estabilidad en pilotos
representativos antes de presupuestar la campaña. Decenas de pilotos y cientos
de casos son una posibilidad de planificación, no un requisito ni una estimación
de rendimiento. Favorecer trabajos independientes en paralelo; no asumir escalado
MPI/GPU de una corrida por disponer de muchos núcleos.

Elegir un muestreo de parámetros informado por los pilotos y por las incertidumbres
observadas. Comprobar convergencia espacial/temporal y balance energético en casos
decisivos, además de persistencia de los diagnósticos frente a condiciones iniciales.
Registrar fallos de convergencia y no excluirlos silenciosamente del análisis.
Una comparación con otro solver es una ampliación útil si responde a una duda
concreta. La MHD 3D requiere una motivación física y un alcance propio; disponer
de clúster no la convierte automáticamente en el siguiente paso.

## Entregables y criterios de finalización

- Evento, datos, intervalos, calibraciones y ajustes trazables, con incertidumbres.
- Matriz de experimentos y justificación de los controles y parámetros explorados.
- Corridas reproducibles: versiones del solver, entradas, estado inicial, scripts
  del clúster, registros de ejecución y salidas con unidades y coordenadas claras.
- Evidencia cuantitativa del mecanismo, robustez numérica y detectabilidad o
  degeneración entre escenarios; incluir discrepancias que los parámetros
  permitidos por STIX no resuelvan.
- Pipeline reutilizable desde datos/ajustes STIX hasta resultados y figuras,
  documentando cualquier paso manual, licencia o dependencia externa.
- Manuscrito de prueba de concepto con antecedentes, métodos, incertidumbres,
  resultados, límites y materiales suficientes para reproducir las conclusiones.

Instalar, compilar o generar figuras de demostración no equivale a completar el
objetivo. Distinguir siempre resultados de prueba, resultados observacionales y
predicciones por verificar. Una skill con este alcance no autoriza por sí sola
a enviar correos, publicar resultados ni consumir una cuota de clúster no acordada.

## Antecedentes para delimitar la aportación

Al preparar novedad o manuscrito, revisar estos trabajos y actualizar la búsqueda;
esta lista procede de una exploración preliminar, no de una revisión exhaustiva:

- [Kennedy et al. (2015)](https://arxiv.org/abs/1504.07541): RADYN impulsado por
  espectros HXR y evolución de la profundidad de frenado.
- [Allred et al. (2020)](https://arxiv.org/abs/2008.10671): transporte FP.
- [Carlsson et al. (2023)](https://arxiv.org/abs/2304.02618): F-CHROMA y su versión
  pública de RADYN; verificar diferencias respecto al RADYN+FP más reciente.
- [Litwicka et al. (2025)](https://doi.org/10.3847/1538-4357/adc393): FLARIX;
  calentamiento continuo frente a pulsos en filamentos distintos, con VAL-C precalentada
  como condición inicial; sin datos observacionales.
- [Litwicka et al., congreso de marzo de 2026](https://plan.events.mpg.de/event/453/contributions/3104/):
  aplicación con STIX, IRIS y CHASE; distinguir resumen de congreso de artículo.

Evaluación de novedad y antecedentes adicionales: docs/03_novedad_y_antecedentes.md.

La posible contribución es cuantificar y contrastar la memoria de una atmósfera
recalentada frente a esas alternativas, no atribuir novedad al mero uso de STIX,
varios pulsos o condiciones precalentadas.

## Contexto operativo al retomar

Leer primero los archivos actuales y verificar las capacidades instaladas.
En la creación de esta skill se había reportado HYDRAD compilado y un entorno
Python STIXpy/SunPy/AIApy, pero ninguna corrida física validada, evento definitivo
ni instalación de RADYN. No tratar ese inventario histórico como estado perpetuo.
Mantener los objetivos al resolver cada tarea concreta; no lanzar toda la campaña
cuando el usuario pida únicamente una explicación, revisión o edición.
