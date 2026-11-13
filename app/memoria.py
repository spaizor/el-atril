"""Lo que El Atril recuerda entre sesiones, en %APPDATA%\\El Atril\\memoria.json:

- el tamano de letra elegido (en %, 100 = normal);
- el tema: el de Windows (por defecto), oscuro o claro;
- de cada carpeta, la ultima hoja que se leyo y por donde iba (scroll de 0 a 1).

Va en un fichero aparte de recientes.json para no cambiar el formato de ese.
"""
import json
import os
import threading

from .recientes import FICHERO as _RECIENTES, clave

FICHERO = os.path.join(os.path.dirname(_RECIENTES), 'memoria.json')

LETRA_MIN, LETRA_MAX, LETRA_NORMAL = 70, 200, 100
MAX_CARPETAS = 100   # se olvidan las carpetas mas antiguas para que el fichero no crezca sin fin

# pywebview atiende cada llamada de la pagina en su propio hilo: el cerrojo evita que dos
# escrituras a la vez se pisen el fichero.
_cerrojo = threading.Lock()


def _leer():
    try:
        with open(FICHERO, encoding='utf-8') as f:
            datos = json.load(f)
        return datos if isinstance(datos, dict) else {}
    except (OSError, ValueError):
        return {}


def _guardar(datos):
    try:
        os.makedirs(os.path.dirname(FICHERO), exist_ok=True)
        with open(FICHERO, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=1)
    except OSError:
        pass  # si no se puede guardar, el programa sigue funcionando sin recordar


def letra():
    v = _leer().get('letra')
    return v if isinstance(v, int) and LETRA_MIN <= v <= LETRA_MAX else LETRA_NORMAL


def poner_letra(valor):
    try:
        v = max(LETRA_MIN, min(LETRA_MAX, int(valor)))
    except (TypeError, ValueError):
        v = LETRA_NORMAL
    with _cerrojo:
        datos = _leer()
        datos['letra'] = v
        _guardar(datos)
    return v


TEMAS = ('oscuro', 'claro')
MODOS = ('sistema',) + TEMAS   # 'sistema' = el que tenga Windows (aplicaciones claras u oscuras)


def tema_windows():
    """'claro' u 'oscuro', segun el modo de las aplicaciones de Windows (Configuracion >
    Personalizacion > Colores). Si no se puede leer, 'claro', que es el de Windows de serie."""
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            r'Software\Microsoft\Windows\CurrentVersion\Themes\Personalize') as k:
            valor, _ = winreg.QueryValueEx(k, 'AppsUseLightTheme')
        return 'claro' if valor else 'oscuro'
    except (ImportError, OSError):
        return 'claro'


def tema():
    """Modo elegido: 'sistema', 'oscuro' o 'claro'."""
    v = _leer().get('tema')
    return v if v in MODOS else MODOS[0]


def tema_efectivo(modo=None):
    """El tema que toca ahora: el elegido, o el de Windows si se sigue al sistema."""
    modo = modo or tema()
    return tema_windows() if modo == 'sistema' else modo


def poner_tema(valor):
    v = valor if valor in MODOS else MODOS[0]
    with _cerrojo:
        datos = _leer()
        datos['tema'] = v
        _guardar(datos)
    return v


def posicion(carpeta):
    """{hoja, scroll} de la ultima visita a la carpeta, o None."""
    c = _leer().get('carpetas')
    p = c.get(clave(carpeta)) if isinstance(c, dict) else None
    if not isinstance(p, dict) or not isinstance(p.get('hoja'), str):
        return None
    s = p.get('scroll')
    return {'hoja': p['hoja'], 'scroll': s if isinstance(s, (int, float)) and 0 <= s <= 1 else 0}


def recordar(carpeta, hoja, scroll):
    """Apunta la hoja y el scroll de la carpeta (la deja la ultima, como la mas reciente)."""
    if not (isinstance(carpeta, str) and isinstance(hoja, str)):
        return
    try:
        scroll = round(max(0.0, min(1.0, float(scroll))), 4)
    except (TypeError, ValueError):
        scroll = 0
    with _cerrojo:
        datos = _leer()
        c = datos.get('carpetas')
        if not isinstance(c, dict):
            c = {}
        k = clave(carpeta)
        c.pop(k, None)
        c[k] = {'hoja': hoja, 'scroll': scroll}
        datos['carpetas'] = dict(list(c.items())[-MAX_CARPETAS:])
        _guardar(datos)
