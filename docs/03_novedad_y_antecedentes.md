# Antecedentes y evaluación de novedad

**Fecha de la búsqueda:** 2026-10-02 (segunda pasada, más profunda que la del mismo día).
**Veredicto resumido:** existe un hueco real pero **estrecho**. El pipeline STIX → RHD, el efecto cualitativo de que la profundidad de frenado cambia con la atmósfera y la comparación «filamentos frente a continuo» **ya están hechos**. No se encontró un estudio que cuantifique la **memoria pulso a pulso del mismo tubo** con un contrafactual controlado, ni su **detectabilidad** con incertidumbres de STIX.

## 1. Método de búsqueda y sus límites

| Herramienta | Uso | Límite observado |
|---|---|---|
| Búsqueda web general | Localizar trabajos | Sus resúmenes automáticos **se equivocan** (atribuyó RADYN+FP a Litwicka 2025; es FLARIX). Cada dato se verificó en la fuente. |
| API de arXiv | Consultas dirigidas por fecha | **Índice incompleto:** `all:RADYN` da solo 53 resultados, `all:FLARIX` da 3 y Litwicka 2025 no aparece. Un resultado de 0 **no** prueba ausencia. |
| Semantic Scholar | Citas hacia adelante de Litwicka 2025, Kennedy 2015 y Collier 2024 | Consultas posteriores devolvieron HTTP 429 (límite de uso); cobertura parcial. |
| **Texto completo** | Kennedy 2015, Rubio da Costa 2016, Collier 2024 (extraído y buscado por palabras clave) | Es la única lectura completa; el resto, resúmenes. |

**No leídos** (acceso denegado o no disponible): texto completo de Litwicka et al. 2025; Polito et al. 2022 y A&A 710, A105 (2026), ambos con error 403; «STIX observation of chromospheric evaporation» (A&A, 2026), 403. Hay que leerlos a mano.

## 2. Qué ya existe

### 2.1 Lo más cercano a la «memoria» (leído en texto completo)

| Trabajo | Qué hace realmente | Implicación |
|---|---|---|
| **Kennedy et al. (2015)**, [arXiv](https://arxiv.org/abs/1504.07541) | RADYN conducido por ajustes RHESSI cada 12 s a lo largo de toda la fase impulsiva de una X1.5 (110 s de calentamiento, 300 s de relajación). Los parámetros se endurecen en dos picos de HXR. Calculan con la expresión de Emslie (1978) **la altura de frenado de electrones de 5–200 keV durante la simulación**: para 50 keV pasa de ≈1.1 Mm (t = 0) a ≈0.75 Mm (t = 70 s) y a ≈5 Mm al final del calentamiento. | **Ya demuestra que la profundidad de frenado cambia en ambos sentidos con la historia.** No separan pulsos ni definen una métrica de memoria; el calentamiento es continuo durante ≈100 s. |
| **Rubio da Costa et al. (2016)**, [arXiv](https://arxiv.org/abs/1603.04951) | Modelo de 16 hilos (RADYN, RHESSI). **Cada ráfaga es un hilo nuevo y «cada nueva simulación parte de la atmósfera inicial».** Los hilos se definen con los picos de la derivada de GOES (efecto Neupert) y se asume tres veces la duración como fase de relajación. | La independencia entre ráfagas es una **hipótesis de partida, no un resultado contrastado**. Es el hueco que abordaría un contraste mismo tubo/independiente. |
| **Collier et al. (2024)**, A&A, [arXiv](https://arxiv.org/abs/2411.09319) | Ajuste OSPEX (4–36 keV) de **la primera ráfaga** de STIX: Ṅ = (0.34 ± 0.04)×10³⁵ s⁻¹, δ = 4.97 ± 0.09, Ec = 13.37 ± 0.57 keV; área A ≈ 10¹⁷ cm² (contorno del 30 % de AIA); haz **triangular de 45 s** en RADYN sobre VAL3C con ápice a 3 MK; compara con EUI/FSI 174 Å. Observacionalmente notan un bucle «previamente calentado» en los marcos posteriores. | **STIX → RADYN ya existe, pero solo para el primer pulso.** La segunda ráfaga no se simula. (Su área y su Ṅ coinciden en orden de magnitud con el caso sintético de este proyecto.) |

### 2.2 Filamentos y calentamiento sucesivo

| Trabajo | Qué hace | Fuente |
|---|---|---|
| **Litwicka, Heinzel & Kašparová (2025)**, ApJ 983, 155 | FLARIX. Continuo (10¹⁰, 6.5 s) frente a 4 pulsos consecutivos en filamentos (25 % del área cada uno, 4×10¹⁰, 2 s, solape 0.5 s). Condición inicial VAL-C y VAL-C precalentada. **Sin datos analizados.** Hα −36–46 %, Mg II k −51–53 %. | [IOP](https://iopscience.iop.org/article/10.3847/1538-4357/adc393) |
| **Litwicka et al. (resumen, marzo de 2026)** | FLARIX, X9 del 3 de octubre de 2024, STIX + IRIS + CHASE; el filamentario se acerca más a Hα y Mg II k. **Resumen de congreso**; no se encontró artículo. | [Resumen](https://plan.events.mpg.de/event/453/contributions/3104/) |
| **Reep et al. (2016)** | RHD multihilo: la sucesión de hebras independientes (intervalos < 10 s) reproduce corrimientos al rojo largos; un bucle único no. | [arXiv](https://arxiv.org/abs/1607.06684) |
| **Radziszewski et al. (2024)**, ApJ | FLARIX con parámetros de **RHESSI** cada 4 s (OSPEX, 6–70 keV) modulados a 0.25 s, para una C1.6 con cuatro pulsos HXR (H1–H4); **modelan solo el pulso H3**; no tratan la historia entre pulsos. | [IOP](https://iopscience.iop.org/article/10.3847/1538-4357/ad8ba9) |

### 2.3 Otros antecedentes relevantes

- **Mrozek, Falewicz, Kołomański & Litwicka (2021)**: 1D hidrodinámico + Fokker–Planck con RHESSI; se centra en una ráfaga no térmica y en la altitud de las fuentes HXR frente a la energía ([arXiv](https://arxiv.org/abs/2112.11392)).
- **Awasthi et al. (2024)**: STIX, ≈200 llamaradas débiles, código PH 1D; partición térmico/no térmico, sin memoria entre pulsos ([arXiv](https://arxiv.org/abs/2402.01936)).
- **Polito et al. (2018)**: RADYN con nanocalentamientos; **la temperatura inicial del ápice (1 o 3 MK) y Ec cambian dónde se frena el haz**, por lo que la densidad previa del bucle ya se sabe que importa ([arXiv](https://arxiv.org/abs/1804.05970)). Es el precalentamiento como condición inicial, no como historia de un pulso.
- **Dennis & Zarro (1993)**: en 20 de 66 eventos la derivada de SXR sigue alta cuando el HXR cae; se interpreta como energía liberada en un bucle ya afectado (cifras vistas en un resumen de búsqueda, verificar) ([Springer](https://link.springer.com/doi/10.1007/BF00662178)).
- **Qiu (2021)**: muchos eventos impulsivos reproducen mal SXR; un modelo de dos fases lo hace mejor ([arXiv](https://arxiv.org/abs/2101.11069)).
- **Reep & Airapetian (2023)**: duración de llamaradas por longitud de onda y evaporación vía RHD ([arXiv](https://arxiv.org/abs/2306.03765)).
- **Allred et al. (2026-10-01)**: marco ARMS + kglobal + RADYN+FP para una llamarada; no trata pulsos sucesivos ni STIX ([arXiv](https://arxiv.org/abs/2610.02149)). **Granovsky et al. (2025)**: RMHD 3D con haces frente a RADYN 1D ([arXiv](https://arxiv.org/abs/2512.24507)).

### 2.4 Citas hacia adelante (Semantic Scholar)

- **Litwicka 2025:** dos citantes, Kowalski 2025 (RHD de condensaciones en la X9) y un trabajo de DKIST sobre estructura fina. Ninguno trata memoria entre pulsos.
- **Kennedy 2015:** 36 citantes (2013–2025); marcados por posible relación: Singh 2025 (inyección episódica), Lörinčík 2022 (pulsaciones en Si IV), Sellers 2022, Rubio da Costa 2016. **Ninguno** presenta un estudio de memoria pulso a pulso en las descripciones vistas.
- **Collier 2024:** cinco citantes (2025–2026); ninguno combina parámetros de STIX con RHD de pulsos múltiples.

## 3. Qué no se encontró

Con las limitaciones de la sección 1, **no se encontró** un estudio con:

1. Una **métrica de memoria** definida como contrafactual pareado (misma historia hasta t_k, con y sin el pulso k).
2. Un **mapa de régimen** en función del tiempo de espera/τ_rel y del cociente de energías.
3. Una prueba de **mismo tubo frente a hilos independientes** por pulso en lugar de asumir la independencia.
4. Un **límite de detectabilidad** con la incertidumbre de STIX propagada.
5. Un **RHD guiado por STIX** que simule más de una ráfaga.

## 4. Evaluación de novedad

| Enfoque | Novedad | Motivo |
|---|---|---|
| Pipeline «espectro STIX → respuesta atmosférica» | **Baja** | Collier 2024; Kennedy 2015 y Rubio da Costa 2016 con RHESSI |
| «La profundidad de frenado cambia con la historia» | **Baja** | Kennedy 2015, con cifras (1.1 → 0.75 → 5 Mm) |
| «Filamentos frente a continuo» | **Baja y arriesgada** | Litwicka 2025 y el resumen de 2026 |
| «Precalentamiento cambia la deposición» | **Baja** | Polito 2018; Litwicka 2025 |
| **Cuantificar la memoria del mismo tubo (contrafactual) + mapa de régimen + prueba frente a hilos independientes + detectabilidad con STIX** | **Moderada** | Es el hueco que dejan Kennedy (continuo, sin separar pulsos) y Rubio da Costa (independencia asumida) |

**Lectura honesta:** la novedad es defendible **solo si el artículo se define por la cuantificación y la prueba de hipótesis**, no por el qué ocurre. Un revisor que conozca Kennedy 2015 considerará trivial que la profundidad cambie. Hay que mostrar *cuánto*, *cuándo* (régimen), *con qué incertidumbre* y *si se puede observar*.

## 5. Consecuencias para el diseño

1. **Corrección de H1.** La hipótesis «el pulso 2 deposita a mayor altura» estaba formulada con un solo sentido. Kennedy 2015 muestra que la altura de frenado de una energía dada **baja** con la compresión de la cromosfera (1.1 → 0.75 Mm) y luego **sube** con la densidad coronal (≈5 Mm). Hay dos efectos en competencia y el signo depende del tiempo y de los parámetros. H1 se reformula sin signo (`docs/00_objetivos_y_metodologia.md`).
2. **El caso nulo ya está parcialmente refutado.** Con calentamiento continuo de ≈100 s hay cambios grandes; el régimen interesante es el de **pulsos cortos con huecos**, donde la memoria depende de τ_w/τ_rel.
3. **Contrastar la hipótesis de Rubio da Costa** (cada ráfaga = hilo nuevo) con el contrafactual es un objetivo concreto y diferenciador.
4. **Evitar la X9 del 3 de octubre de 2024** y el enfoque «filamentos frente a continuo con STIX/IRIS», que el grupo de Litwicka presenta.

## 6. Riesgos para la publicación

- **Competencia activa** del grupo de Wrocław/Ondřejov (Litwicka, Mrozek, Falewicz, Berlicki, Heinzel), que usa FLARIX con STIX y RHESSI. Su resumen de 2026 puede convertirse en artículo.
- **Cobertura de la búsqueda incompleta:** ADS no se consultó y varios textos no se leyeron.
- **Solver:** usar RADYN+FP (en lugar de FLARIX) aporta independencia, pero requiere acceso.
- **Un solo evento** limita la generalización.

## 7. Qué falta antes de comprometer meses de trabajo

1. **Buscar en ADS** (no accesible desde aquí): `abs:("RADYN" OR "FLARIX" OR "Fokker-Planck") AND abs:("successive" OR "consecutive" OR "multiple" OR "repeated" OR "preheat*" OR "memory") AND abs:"flare"`, y `abs:"STIX" AND abs:("radiative hydrodynamic" OR "RADYN" OR "FLARIX")`; después, las citas de Kennedy 2015, Rubio da Costa 2016, Collier 2024, Radziszewski 2024 y Litwicka 2025.
2. **Leer a mano** lo que quedó bloqueado: Litwicka 2025 (texto completo), Polito 2022, A&A 710, A105 y «STIX observation of chromospheric evaporation».
3. **Preguntar a la profesora** por preprints o planes del grupo de Litwicka y por trabajos que ella conozca sobre ráfagas sucesivas en un mismo bucle.
4. Repetir la búsqueda justo antes de enviar el manuscrito.
