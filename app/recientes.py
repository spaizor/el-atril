"""Lista de las ultimas carpetas abiertas, guardada en %APPDATA%\\El Atril\\recientes.json.

Se guarda fuera del programa para que valga igual como script y como .exe, y para que la
lista de cada usuario no acabe dentro del proyecto.
"""
import json
import os

MAXIMO = 10
FICHERO = os.path.join(os.environ.get('APPDATA') or os.path.expanduser('~'),
                       'El Atril', 'recientes.json')


def _clave(ruta):
    """Para comparar rutas sin que importen mayusculas ni barras."""
    return os.path.normcase(os.path.abspath(ruta))


def _leer():
    try:
        with open(FICHERO, encoding='utf-8') as f:
            datos = json.load(f)
        return [r for r in datos if isinstance(r, str)]
    except (OSError, ValueError):
        return []


def _guardar(rutas):
    try:
        os.makedirs(os.path.dirname(FICHERO), exist_ok=True)
        with open(FICHERO, 'w', encoding='utf-8') as f:
            json.dump(rutas, f, ensure_ascii=False, indent=1)
    except OSError:
        pass  # si no se puede guardar, el programa sigue funcionando sin recientes


def listar():
    """[{nombre, ruta, existe}] de la mas reciente a la mas antigua."""
    return [{'nombre': os.path.basename(r.rstrip('\\/')) or r, 'ruta': r,
             'existe': os.path.isdir(r)} for r in _leer()]


def anotar(ruta):
    """Pone la carpeta la primera de la lista."""
    ruta = os.path.abspath(ruta)
    rutas = [r for r in _leer() if _clave(r) != _clave(ruta)]
    _guardar([ruta] + rutas[:MAXIMO - 1])


def quitar(ruta):
    _guardar([r for r in _leer() if _clave(r) != _clave(ruta)])
