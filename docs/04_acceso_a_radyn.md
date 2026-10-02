# RADYN como solver único: qué se verificó y qué falta

**Decisión del proyecto (2026-10-02):** usar **un solo código**, RADYN con Fokker–Planck, y retirar HYDRAD cuando RADYN pase la verificación (sección 5). Esta decisión se apoya en lo que sigue.

**Fuente de lo verificado:** la distribución descargada (`radyn_fchroma.tar`, 87 844 352 bytes, SHA-256 `827948d913cdb33768a6f501cf42a7c8c3d6935fcd264b16a183f070ba70bf14`) desde [folk.universitetetioslo.no/matsc/radyn](https://folk.universitetetioslo.no/matsc/radyn/), con su manual (`doc/radyn_manual.pdf`, fechado en febrero de 2023) y su código fuente. No se incluye en este repositorio (sección 1).

## 1. Licencia: sin resolver

- La distribución **no trae archivo de licencia** y la página de descarga tampoco indica condiciones.
- El manual dice: «We are in the process of getting a permanent home (with proper DOI and license) on Zenodo». No se encontró esa publicación.
- El código incluye `cdf.inc` con la licencia de la NASA para la biblioteca CDF; eso no cubre RADYN.
- **Consecuencia:** RADYN **no se copia ni se redistribuye** en este repositorio. Hay que pedir a Mats Carlsson la confirmación de la licencia y del permiso de uso antes de publicar nada que dependa de ella.
- La base de modelos F-CHROMA sí pide acreditar la financiación (FP7, nº 606862) y notificar publicaciones a L. Fletcher ([QUB](https://star.pst.qub.ac.uk/wiki/public/solarmodels/start.html)).

## 2. Qué incluye la distribución (leído del manual y del código)

| Capacidad | Resultado | Evidencia |
|---|---|---|
| **Fokker–Planck** | **Sí**, `ibeam = 8`. Es la versión de Allred et al. (2015). La versión de Allred et al. (2020) **no** está incluida; el manual dice que se planea publicarla en GitHub. | `doc/radyn_manual.tex`, `prog/fp_solver.f` |
| Física del transporte | Difusión en ángulo de paso por colisiones, espejo magnético y **corriente de retorno** (`irc`), con temperatura del gas y una energía de termalización (`thermE`) | `prog/fp_solver.f`, `prog/beamrat.f` |
| Resolución del FP | **Estacionario en cada paso**, sobre la atmósfera actual; por tanto Q(s,t) se recalcula con la atmósfera que evoluciona | cabecera de `fp_solver.f` |
| Haz dependiente del tiempo | Sí, tabla `ftab.dat` (sección 3) | `prog/rftab.f` |
| **Reinicio** | Sí: `itime0 > 0` reinicia desde ese paso de `radyn_out.cdf`; `itime0 < 0` desde el último. Permite **bifurcar** corridas con historia común | manual, sección 7 |
| Paralelismo | Versión serie y versión MPI (paralela en frecuencia y transiciones) | manual, sección 2 |
| Geometría | 1D, bucle semisimétrico, haz inyectado en el tope; ejemplo con semilongitud de 10 Mm | manual, secciones 4–5 |
| Atmósferas iniciales | VAL3C y bucles de 1 MK ya preparados en `input/` | distribución |
| Salida | Archivos CDF; análisis con IDL (no disponible aquí) o con [RadynPy](https://pypi.org/project/radynpy/) | manual |

**Rejilla adaptativa:** los índices de las variables no corresponden a una altura fija; las rutinas de análisis lo manejan. La conservación de energía está formulada sobre esa rejilla y no es trivial de interpretar (manual, sección 1).

## 3. Formato del haz (`ftab.dat`, FP) y cómo se adapta

```
* comentarios (líneas con '*')
511d3  1.0  2  0.1        masa [eV]  |carga|  tipo de distribución de ángulo de paso  sigma
npts                      como máximo 5000 filas
t [s]   δ   Ec [keV]   F [erg cm⁻² s⁻¹]
```

Particularidades que condicionan el diseño (`prog/rftab.f`, `prog/beam.f`):

1. **Orden de columnas distinto al de HYDRAD:** tiempo, δ, Ec, F.
2. **F no puede ser cero.** Se interpola `log10(F)` y se impone un mínimo de 0.1 erg cm⁻² s⁻¹.
3. **La interpolación es con splines tensados** (tensión 5.5) de δ, Ec y log₁₀F. Una rampa lineal entre el mínimo y 10¹⁰ erg cm⁻² s⁻¹ se comportaría como un escalón tardío.
4. **La tabla debe cubrir toda la corrida:** si el tiempo supera la última fila, RADYN se detiene.
5. El ejemplo de la distribución es un pulso **triangular de 20 s** con fluencia de 10¹¹ erg cm⁻².

**Adaptación implementada:** [`src/radyn_ftab.py`](../src/radyn_ftab.py) subdivide cada rampa en tramos de 0.02 s siguiendo la forma lineal, aplica el mínimo de 0.1, extiende la tabla hasta el final y comprueba la energía suponiendo interpolación log-lineal entre filas. En los seis experimentos la energía codificada coincide con la prevista dentro de **−0.03 %** (38 pruebas pasan). `src/experiments.py` escribe ahora un `ftab.dat` por componente.

**Pendiente:** el spline tensado real de RADYN **no se ha ejecutado** (no hay compilador). La comprobación definitiva es integrar el flujo del haz que RADYN escribe en su propia salida.

## 4. Particularidades físicas que cambian el diseño

- **Calentamiento de fondo permanente.** Para que la atmósfera inicial no se enfríe sin haz, RADYN añade un término no radiativo que equilibra el estado inicial (`xnrh0 = 1e-21` en el ejemplo). La relajación entre pulsos es, por tanto, **hacia el equilibrio inicial** y no un enfriamiento libre. El tiempo de relajación τ_rel del contrafactual E5 debe medirse **con ese mismo término**, y el informe debe declararlo.
- **Frontera superior reflectante** (`ibc0 = 6`, bucle simétrico) y **frontera inferior** reflectante (`ibcx = -1`) o transparente (`ibcx = 4`) según el tiempo estudiado; para tiempos largos hay que usar la transparente.
- **Paso máximo** de 0.1 s recomendado (`dtmax`) y salida frecuente.
- El flujo es un flujo de energía en el tope del bucle; el área A sigue sin estar acotada por STIX y se conserva como parámetro con incertidumbre.

## 5. Puerta de verificación antes de retirar HYDRAD

1. Instalar un compilador Fortran y la biblioteca CDF de la NASA (**ninguno está instalado**; requiere descargas que hay que autorizar).
2. Compilar la versión dinámica (`dyn`) y reproducir un modelo de la base pública F-CHROMA (96 modelos, VAL3C, δ = 3–8, Ec = 10–25 keV, pulso triangular de 20 s) comparando con su CDF publicado.
3. Medir tiempo de pared y memoria de una corrida de 2 pulsos.
4. Probar el **reinicio** para confirmar que restablece el estado completo (incluidas poblaciones atómicas) antes de usarlo para bifurcar.
5. Confirmar la licencia con Mats Carlsson.

Solo después se elimina `vendor/HYDRAD/` del repositorio (queda en el historial de git).

## 6. Riesgos

| Riesgo | Efecto | Mitigación |
|---|---|---|
| Licencia no confirmada | No se puede publicar código derivado | Pedir confirmación; no redistribuir RADYN |
| FP de 2015 sin las mejoras de 2020 | Diferencias en blanco cálido y retorno de corriente | Documentarlo; pedir la versión más reciente |
| Compilación (F77/F90 + CDF) en macOS | Retraso | Probar en el clúster |
| Convergencia difícil de atmósferas nuevas | Casos fallidos | Usar atmósferas ya preparadas; registrar fallos |
| Coste por corrida desconocido | Campaña mal dimensionada | Piloto antes de presupuestar |
