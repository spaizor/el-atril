# Primeros pasos

Con la estación [ya montada](../montaje.md), en diez minutos tendrás la primera lectura.

## Instalar

Hace falta Python 3.11 o posterior. En PowerShell:

```powershell
# Crear un entorno aparte e instalar Cierzo
py -m venv .venv
.venv\Scripts\python -m pip install cierzo

# Comprobar que ve la placa
.venv\Scripts\cierzo puertos
```

Si todo va bien, la última orden contesta algo así:

```text
COM4   Raspberry Pi Pico W   (Cierzo 1.2)
```

## La primera lectura

```python
from cierzo import Estacion

estacion = Estacion(puerto="COM4")
lectura = estacion.leer()

print(f"Temperatura: {lectura.temperatura:.1f} °C")
print(f"Humedad:     {lectura.humedad:.0f} %")

if lectura.temperatura < 2:
    print("¡Cuidado, puede helar!")
```

## Guardar lecturas todo el día

Para dejarla midiendo, usa la orden `registrar`. Cada cuánto mide se decide en la
[configuración](configuracion.md#intervalo-de-lectura).

```powershell
.venv\Scripts\cierzo registrar --salida lecturas.csv
```

El resultado es un fichero como [lecturas.csv](../datos/lecturas.csv), que se abre con
cualquier hoja de cálculo.

## Si algo falla

| Lo que pasa | Causa probable | Solución |
|---|---|---|
| `No se encuentra la placa` | El cable solo es de carga | Usa un cable USB de datos |
| La temperatura marca `-140` | El BME280 está mal conectado | Repasa SDA y SCL en el [esquema](../montaje.md#esquema-de-conexiones) |
| La lluvia siempre es `0` | El balancín está atascado | Límpialo y comprueba que bascula |
| La humedad no baja del 100 % | Ha entrado agua en el sensor | Déjalo secar un día |

## Siguiente paso

- Ajusta la estación a tu gusto en [Configuración](configuracion.md).
- Mira qué puedes hacer desde tu código en la [API de Python](../referencia/api.md).
