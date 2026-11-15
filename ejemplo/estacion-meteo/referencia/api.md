# API de Python

Todo lo que hace la orden `cierzo` se puede hacer también desde tu código.

## Estacion

```python
class Estacion:
    """Una estación Cierzo conectada por USB."""

    def __init__(self, puerto: str | None = None, intervalo: int = 300):
        self.puerto = puerto or buscar_puerto()
        self.intervalo = intervalo

    def leer(self) -> Lectura:
        """Pide una lectura a la placa y la devuelve."""
        ...

    def registrar(self, salida: str, horas: float | None = None) -> int:
        """Guarda lecturas en un CSV. Devuelve cuántas ha guardado."""
        ...
```

| Método | Devuelve | Qué hace |
|---|---|---|
| `leer()` | `Lectura` | Una lectura, ahora |
| `registrar(salida, horas)` | `int` | Guarda lecturas cada `intervalo` segundos |
| `cerrar()` | nada | Suelta el puerto |

## Lectura

Cada lectura es un objeto con estos campos:

| Campo | Tipo | Unidad |
|---|---|---|
| `fecha` | `datetime` | hora local |
| `temperatura` | `float` | °C |
| `humedad` | `float` | % |
| `presion` | `float` | hPa |
| `lluvia` | `float` | mm desde la lectura anterior |
| `luz` | `int` | 0 a 100 |

## Ejemplos

### La temperatura máxima del día

```python
import csv

with open("lecturas.csv", encoding="utf-8") as f:
    lecturas = list(csv.DictReader(f))

maxima = max(lecturas, key=lambda l: float(l["temperatura_c"]))
print(f"Máxima: {maxima['temperatura_c']} °C a las {maxima['fecha'][11:16]}")
```

### Avisar si va a helar

```python
from cierzo import Estacion

UMBRAL = 2.0  # grados

with Estacion() as estacion:
    for lectura in estacion.seguir():
        if lectura.temperatura < UMBRAL:
            print(f"{lectura.fecha:%H:%M}  ¡Helada! {lectura.temperatura:.1f} °C")
```

### Desde JavaScript

El panel web publica la última lectura en `/api/ultima`:

```javascript
const r = await fetch("http://cierzo.local/api/ultima");
const lectura = await r.json();
console.log(`${lectura.temperatura} °C, ${lectura.humedad} %`);
```

## Errores

| Excepción | Cuándo salta |
|---|---|
| `PlacaNoEncontrada` | No hay ninguna placa en los puertos USB |
| `SensorNoResponde` | Un sensor no contesta (cable suelto) |
| `LecturaInvalida` | La placa manda un valor imposible |

Las opciones de la estación están en [Configuración](../guia/configuracion.md).
