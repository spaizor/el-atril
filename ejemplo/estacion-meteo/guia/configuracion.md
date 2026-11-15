# Configuración

Cierzo se configura con un fichero `cierzo.json` en la carpeta desde la que se lanza. Si no
existe, usa los valores de serie.

## Fichero de ejemplo

```json
{
  "puerto": "COM4",
  "intervalo_segundos": 300,
  "unidades": "metrico",
  "salida": {
    "csv": "lecturas.csv",
    "sqlite": null
  },
  "avisos": {
    "helada": true,
    "umbral_helada_c": 2.0
  }
}
```

## Opciones

| Opción | Tipo | De serie | Qué hace |
|---|---|---|---|
| `puerto` | texto | *automático* | Puerto de la placa (`COM4`, `/dev/ttyACM0`...) |
| `intervalo_segundos` | número | `300` | Cada cuánto se mide |
| `unidades` | texto | `"metrico"` | `"metrico"` (°C, mm) o `"imperial"` (°F, in) |
| `salida.csv` | texto | `"lecturas.csv"` | Fichero CSV donde se añaden las lecturas |
| `salida.sqlite` | texto | `null` | Base de datos SQLite, si se quiere |
| `avisos.helada` | sí / no | `false` | Avisa cuando la temperatura baja del umbral |

### Intervalo de lectura

Con el valor de serie (300 segundos) salen **288 lecturas al día**, unas 20 KB en CSV. Bajarlo
de 10 segundos no sirve de mucho: el BME280 tarda en notar los cambios.

### Unidades

~~Antes las unidades se elegían en cada orden con `--unidades`.~~ Desde la versión 1.2 solo se
eligen aquí.

## Guardar en SQLite

Si das un nombre en `salida.sqlite`, las lecturas van también a una tabla `lecturas`. Así se
consultan con SQL:

```sql
SELECT date(fecha) AS dia,
       round(min(temperatura_c), 1) AS minima,
       round(max(temperatura_c), 1) AS maxima,
       sum(lluvia_mm) AS lluvia
FROM lecturas
GROUP BY dia
ORDER BY dia DESC
LIMIT 7;
```

## En la placa

La placa tiene su propia configuración, en YAML, que se copia con `cierzo instalar`:

```yaml
wifi:
  red: "MiCasa"
  clave: "cambia-esta-clave"
sensores:
  bme280: { sda: 4, scl: 5 }
  lluvia: { pin: 15, mm_por_vuelco: 0.28 }
  luz: { pin: 26 }
```

Qué significa cada sensor está en [Sensores](../referencia/sensores.md).
