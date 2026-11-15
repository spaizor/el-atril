"""Reads the BME280 sensor once and prints the reading. Example for the Cierzo guide."""
from cierzo import Station

station = Station(port="COM4")
print(station.read())
