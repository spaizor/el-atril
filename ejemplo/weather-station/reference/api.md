# Python API

Everything the `cierzo` command does can also be done from your code.

## Station

```python
class Station:
    """A Cierzo station connected over USB."""

    def __init__(self, port: str | None = None, interval: int = 300):
        self.port = port or find_port()
        self.interval = interval

    def read(self) -> Reading:
        """Asks the board for a reading and returns it."""
        ...

    def log(self, output: str, hours: float | None = None) -> int:
        """Saves readings to a CSV. Returns how many it saved."""
        ...
```

| Method | Returns | What it does |
|---|---|---|
| `read()` | `Reading` | One reading, now |
| `log(output, hours)` | `int` | Saves readings every `interval` seconds |
| `close()` | nothing | Releases the port |

## Reading

Each reading is an object with these fields:

| Field | Type | Unit |
|---|---|---|
| `time` | `datetime` | local time |
| `temperature` | `float` | °C |
| `humidity` | `float` | % |
| `pressure` | `float` | hPa |
| `rain` | `float` | mm since the previous reading |
| `light` | `int` | 0 to 100 |

## Examples

### The highest temperature of the day

```python
import csv

with open("readings.csv", encoding="utf-8") as f:
    readings = list(csv.DictReader(f))

highest = max(readings, key=lambda r: float(r["temperature_c"]))
print(f"Highest: {highest['temperature_c']} °C at {highest['time'][11:16]}")
```

### Warning when it is going to freeze

```python
from cierzo import Station

THRESHOLD = 2.0  # degrees

with Station() as station:
    for reading in station.follow():
        if reading.temperature < THRESHOLD:
            print(f"{reading.time:%H:%M}  Frost! {reading.temperature:.1f} °C")
```

### From JavaScript

The web panel publishes the latest reading at `/api/latest`:

```javascript
const r = await fetch("http://cierzo.local/api/latest");
const reading = await r.json();
console.log(`${reading.temperature} °C, ${reading.humidity} %`);
```

## Errors

| Exception | When it is raised |
|---|---|
| `BoardNotFound` | There is no board on the USB ports |
| `SensorNotResponding` | A sensor does not answer (loose wire) |
| `InvalidReading` | The board sends an impossible value |

The station options are in [Configuration](../guide/configuration.md).
