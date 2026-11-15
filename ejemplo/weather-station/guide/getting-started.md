# Getting started

With the station [already built](../assembly.md), you will have your first reading in ten
minutes.

## Install

You need Python 3.11 or later. In PowerShell:

```powershell
# Create a separate environment and install Cierzo
py -m venv .venv
.venv\Scripts\python -m pip install cierzo

# Check that it sees the board
.venv\Scripts\cierzo ports
```

If all is well, the last command answers something like this:

```text
COM4   Raspberry Pi Pico W   (Cierzo 1.2)
```

## Your first reading

```python
from cierzo import Station

station = Station(port="COM4")
reading = station.read()

print(f"Temperature: {reading.temperature:.1f} °C")
print(f"Humidity:    {reading.humidity:.0f} %")

if reading.temperature < 2:
    print("Careful, it may freeze!")
```

## Logging readings all day

To leave it measuring, use the `log` command. How often it measures is set in the
[configuration](configuration.md#reading-interval).

```powershell
.venv\Scripts\cierzo log --output readings.csv
```

The result is a file like [readings.csv](../data/readings.csv), which opens in any
spreadsheet.

## If something goes wrong

| What happens | Likely cause | Fix |
|---|---|---|
| `Board not found` | The cable is charge-only | Use a USB data cable |
| Temperature reads `-140` | The BME280 is wired wrong | Check SDA and SCL in the [diagram](../assembly.md#wiring-diagram) |
| Rain is always `0` | The bucket is stuck | Clean it and check that it tips |
| Humidity stays at 100 % | Water got into the sensor | Let it dry for a day |

## Next step

- Adjust the station to your taste in [Configuration](configuration.md).
- See what you can do from your code in the [Python API](../reference/api.md).
