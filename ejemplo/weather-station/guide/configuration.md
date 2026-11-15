# Configuration

Cierzo is configured with a `cierzo.json` file in the folder it is launched from. If there is
none, it uses the default values.

## Sample file

```json
{
  "port": "COM4",
  "interval_seconds": 300,
  "units": "metric",
  "output": {
    "csv": "readings.csv",
    "sqlite": null
  },
  "warnings": {
    "frost": true,
    "frost_threshold_c": 2.0
  }
}
```

## Options

| Option | Type | Default | What it does |
|---|---|---|---|
| `port` | text | *automatic* | Port of the board (`COM4`, `/dev/ttyACM0`...) |
| `interval_seconds` | number | `300` | How often it measures |
| `units` | text | `"metric"` | `"metric"` (°C, mm) or `"imperial"` (°F, in) |
| `output.csv` | text | `"readings.csv"` | CSV file the readings are appended to |
| `output.sqlite` | text | `null` | SQLite database, if you want one |
| `warnings.frost` | yes / no | `false` | Warns when the temperature drops below the threshold |

### Reading interval

With the default value (300 seconds) you get **288 readings a day**, about 20 KB of CSV. Going
below 10 seconds is not much use: the BME280 takes a while to notice changes.

### Units

~~Units used to be chosen on each command with `--units`.~~ Since version 1.2 they are only
chosen here.

## Saving to SQLite

If you give a name in `output.sqlite`, the readings also go to a `readings` table. Then you can
query them with SQL:

```sql
SELECT date(time) AS day,
       round(min(temperature_c), 1) AS lowest,
       round(max(temperature_c), 1) AS highest,
       sum(rain_mm) AS rain
FROM readings
GROUP BY day
ORDER BY day DESC
LIMIT 7;
```

## On the board

The board has its own configuration, in YAML, which is copied over with `cierzo install`:

```yaml
wifi:
  network: "MyHome"
  password: "change-this-password"
sensors:
  bme280: { sda: 4, scl: 5 }
  rain: { pin: 15, mm_per_tip: 0.28 }
  light: { pin: 26 }
```

What each sensor means is in [Sensors](../reference/sensors.md).
