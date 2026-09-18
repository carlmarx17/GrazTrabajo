# Primera lectura de HYDRAD

HYDRAD no resuelve las ecuaciones MHD completas. En una línea de campo fija resuelve masa, momento y energía de electrones e iones, con gravedad, conducción térmica, radiación y calentamiento. Para este proyecto el término decisivo es el calentamiento del haz, `Q_beam(s,t)`.

## Recorrido de ejecución

`HYDRAD/source/main.cpp` es deliberadamente corto: crea `CAdaptiveMesh`. El constructor de esa clase, en `HYDRAD/source/mesh.cpp`, lee la configuración, crea la malla adaptativa y ejecuta el avance temporal. La física de cada celda vive en `HYDRAD/source/eqns.cpp`.

La dependencia es:

```text
main.cpp → CAdaptiveMesh (mesh.cpp) → CEquations (eqns.cpp)
                                      ├─ CHeat (Heating_Model/source/heat.cpp)
                                      ├─ CRadiation (Radiation_Model/source/)
                                      └─ CKinetic (Kinetic_Model/source/)
```

`CEquations::Initialise()` abre `HYDRAD/config/hydrad.cfg`, carga el perfil inicial, la gravedad y el tiempo de la corrida. Después crea `CHeat` y los objetos de radiación. La malla decide dónde refinar para resolver la transición cromosfera–corona durante la evaporación.

## Entrada del haz de electrones

La entrada es `Heating_Model/config/beam_heating_model.cfg`. Cada fila tiene:

```text
tiempo [s]    flujo de energía [erg cm^-2 s^-1]    Ec [keV]    δ
```

`CHeat::GetBeamHeatingData()` lee esa tabla. Si tiene una sola fila, aplica un haz constante durante el tiempo indicado; si tiene varias, `CHeat::CalculateBeamParameters()` interpola linealmente entre filas. Esta es exactamente la interfaz que construiremos a partir de los ajustes STIX: cada intervalo espectral produce una fila.

`CHeat::CalculateBeamHeating()` transforma `(F, Ec, δ)` en energía depositada por profundidad de columna. `CEquations` incorpora esa tasa en las ecuaciones de energía. El resultado físico esperado es calentamiento cromosférico, aumento de presión y flujo ascendente: evaporación cromosférica.

## Lo que cambiaremos y lo que no

No modificaremos el solver de HYDRAD. Nuestro código en `src/` hará la traducción reproducible:

```text
ajuste STIX(t) → F(t), Ec(t), δ(t) → beam_heating_model.cfg → perfil Q_beam(s,t)
```

El ejecutable `HYDRAD_beam.exe` ya está compilado con `BEAM_HEATING` activado. El ejecutable genérico `HYDRAD.exe` sirve para comprobar la instalación, pero no incorpora ese término. La siguiente tarea será crear la primera tabla de prueba.

## Límite importante para los diagnósticos

HYDRAD incluye radiación y un modelo directo para líneas ópticamente delgadas, útil para AIA/Fe XVIII. Su tratamiento no sustituye la transferencia radiativa NLTE de RADYN para un perfil de Hα. Para Hα de calidad publicable, usaremos RADYN o postprocesado RH/RH1.5D con las atmósferas de HYDRAD.
