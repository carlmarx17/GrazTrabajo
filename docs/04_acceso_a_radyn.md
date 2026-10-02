# Acceso a RADYN: qué está verificado y qué no

**Fecha:** 2026-10-02. Fuentes: páginas oficiales consultadas hoy; el A&A del artículo de F-CHROMA dio error 403 y no se leyó.

## Verificado

| Hecho | Fuente |
|---|---|
| La **versión F-CHROMA de RADYN** se ofrece como descarga: distribución completa (88 MB) y, aparte, solo las herramientas de análisis en IDL (317 kB). Código en FORTRAN (mayormente F77, algo de F90). Contacto: Mats Carlsson. | [Universidad de Oslo](https://folk.universitetetioslo.no/matsc/radyn/) |
| La página **no indica licencia, condiciones de uso ni forma de citar**. | Misma página |
| Hay una base pública de **96 modelos** RADYN de F-CHROMA: atmósfera VAL-C, δ = 3–8, energía total 3×10¹⁰–10¹² erg, Ec = 10–25 keV, **pulso triangular de 20 s**, haz Fokker–Planck, en archivos CDF. Se pide agradecer la financiación (F-CHROMA, FP7, nº 606862) y notificar las publicaciones a L. Fletcher. | [QUB](https://star.pst.qub.ac.uk/wiki/public/solarmodels/start.html) |
| Existe **RadynPy**, herramienta de análisis en Python para los CDF. | [PyPI](https://pypi.org/project/radynpy/) |

## No verificado (hay que comprobarlo antes de migrar)

1. **Licencia:** que sea descargable no la convierte en código abierto. Mientras no se confirme, no se incorpora su código al repositorio (ya lo dice `THIRD_PARTY_NOTICES.md`).
2. **Fokker–Planck en la distribución descargable:** la base de modelos usa haz FP, pero la página de descarga no lo menciona. Falta saber si incluye colisiones con blanco cálido, corriente de retorno y espejo magnético, y cómo difiere del RADYN+FP de Allred et al. (2020).
3. **Entrada del haz dependiente del tiempo:** formato exacto de la tabla de parámetros (flujo, Ec, δ frente a t) y si admite varios pulsos con huecos.
4. **Reinicio desde un estado guardado:** necesario para bifurcar corridas con historia común (ahorra coste).
5. **Tiempo de pared y memoria** de una corrida con 2–3 pulsos.
6. **Compilación** en este Mac y en el clúster (gfortran; el análisis en IDL no está disponible aquí, por lo que se usaría RadynPy).

## Prueba de verificación disponible

La base pública de F-CHROMA permite una prueba de reproducción: correr la distribución con los parámetros de un modelo de la base y comparar con su CDF publicado. Es la comprobación de la fase F1 (OE3). Esos modelos son de **un solo pulso**; los casos de 2 y 3 pulsos serían nuevos.

## Qué significaría migrar

- **Se conserva:** el generador de tablas (con un adaptador al formato de RADYN), la matriz de experimentos, la definición de memoria y las pruebas.
- **Cambia:** el solver principal. HYDRAD pasa a ser comparación coronal.
- **No se pierde nada:** las métricas de memoria deben escribirse para ambos solvers.
