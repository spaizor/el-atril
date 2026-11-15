"""Lee el sensor BME280 una vez y escribe la lectura. Ejemplo para la guia de Cierzo."""
from cierzo import Estacion

estacion = Estacion(puerto="COM4")
print(estacion.leer())
