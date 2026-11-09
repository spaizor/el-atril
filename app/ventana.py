"""Ventana de El Atril (pywebview) y funciones que la pagina puede llamar desde JavaScript."""
import os

import webview

from . import APP_VERSION, memoria, recientes
from .biblioteca import Biblioteca

NOMBRE_APP = 'El Atril'

# Color de la ventana mientras carga la pagina (el --fondo de cada tema en estilo.css), para
# que el tema claro no arranque con un fogonazo oscuro.
FONDOS = {'oscuro': '#16181d', 'claro': '#ffffff'}

# Carpeta con la pagina (HTML, CSS y JS). Funciona igual como script y dentro del .exe,
# porque el .spec copia la carpeta 'web' junto al paquete.
CARPETA_WEB = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web')


def pagina():
    """HTML completo con el CSS y el JS dentro (se carga como texto, sin servidor)."""
    def leer(nombre):
        with open(os.path.join(CARPETA_WEB, nombre), encoding='utf-8') as f:
            return f.read()
    return (leer('index.html')
            .replace('/*__CSS__*/', leer('estilo.css'))
            .replace('/*__JS__*/', leer('app.js'))
            .replace('__APP_VERSION__', APP_VERSION)
            .replace('__TEMA__', memoria.tema()))   # asi la pagina ya nace con su tema


class Api:
    """Lo que ve la pagina como pywebview.api.

    Solo se exponen los metodos publicos: los atributos van con '_' delante para que
    pywebview no intente recorrerlos.
    """

    def __init__(self, carpeta=None):
        self._ventana = None
        self._biblio = None
        if carpeta and os.path.isdir(carpeta):
            self._usar(carpeta)

    def _usar(self, carpeta):
        """Abre la carpeta y la anota en las recientes."""
        self._biblio = Biblioteca(carpeta)
        recientes.anotar(carpeta)
        self._poner_titulo()
        return self._estado()

    def _estado(self):
        b = self._biblio
        if not b:
            return None
        indice = b.listar()
        # Si ya se habia leido esta carpeta, se vuelve a la ultima hoja y por donde se iba.
        inicio, scroll = b.inicio(indice), 0
        p = memoria.posicion(b.raiz)
        if p and any(f['ruta'] == p['hoja'] and f['tipo'] == 'md' for f in indice):
            inicio, scroll = p['hoja'], p['scroll']
        return {'nombre': b.nombre, 'ruta': b.raiz, 'indice': indice,
                'inicio': inicio, 'scroll': scroll, 'truncada': b.truncada}

    def _poner_titulo(self):
        if self._ventana:
            titulo = f'{self._biblio.nombre} · {NOMBRE_APP}' if self._biblio else NOMBRE_APP
            self._ventana.set_title(titulo)

    def estado(self):
        """La carpeta abierta al arrancar (si se paso por la linea de comandos), o None."""
        self._poner_titulo()
        return self._estado()

    def abrir_carpeta(self):
        """Pide una carpeta con el dialogo de Windows. None si se cancela."""
        inicial = self._biblio.raiz if self._biblio else ''
        elegida = self._ventana.create_file_dialog(webview.FileDialog.FOLDER, directory=inicial)
        if not elegida:
            return None
        carpeta = elegida[0] if isinstance(elegida, (list, tuple)) else elegida
        return self._usar(carpeta)

    def cerrar(self):
        """Cierra la carpeta abierta (la pagina vuelve a la portada con las recientes)."""
        self._biblio = None
        self._poner_titulo()

    def recientes(self):
        """Ultimas carpetas abiertas: [{nombre, ruta, existe}]."""
        return recientes.listar()

    def abrir_reciente(self, ruta):
        """Abre una carpeta de la lista de recientes. None si ya no existe."""
        if not os.path.isdir(ruta):
            return None
        return self._usar(ruta)

    def quitar_reciente(self, ruta):
        """Quita una carpeta de la lista y devuelve la lista nueva."""
        recientes.quitar(ruta)
        return recientes.listar()

    def listar(self):
        """Indice de la carpeta abierta (para recargar)."""
        return self._biblio.listar() if self._biblio else []

    def leer(self, ruta):
        """HTML de una hoja."""
        return self._biblio.leer(ruta) if self._biblio else ''

    def buscar(self, q):
        """Busqueda en todas las hojas."""
        return self._biblio.buscar(q) if self._biblio else []

    def abrir(self, ruta):
        """Abre un fichero de la carpeta (Excel, PDF, imagen...) con su programa."""
        return self._biblio.abrir_externo(ruta) if self._biblio else False

    def vigilar(self, hoja, con_carpeta):
        """Firmas para saber si algo ha cambiado en disco: la de la hoja abierta (siempre) y
        la de la carpeta (solo si se pide, porque cuesta algo mas)."""
        b = self._biblio
        if not b:
            return {}
        return {'hoja': b.firma_hoja(hoja) if isinstance(hoja, str) else None,
                'carpeta': b.firma_carpeta() if con_carpeta else None}

    def enlaces(self, rutas):
        """Estado de varios enlaces de una hoja: {ruta: 'fichero'|'carpeta'|'bloqueado'|'falta'}."""
        if not self._biblio or not isinstance(rutas, list):
            return {}
        return {r: self._biblio.estado_enlace(r) for r in rutas if isinstance(r, str)}

    def tema(self):
        """Tema guardado: 'oscuro' o 'claro'."""
        return memoria.tema()

    def poner_tema(self, valor):
        """Guarda el tema y devuelve el que queda."""
        return memoria.poner_tema(valor)

    def letra(self):
        """Tamano de letra guardado (en %)."""
        return memoria.letra()

    def poner_letra(self, valor):
        """Guarda el tamano de letra y devuelve el que queda (dentro de los limites)."""
        return memoria.poner_letra(valor)

    def recordar(self, carpeta, hoja, scroll):
        """Apunta la hoja que se esta leyendo en la carpeta y por donde va (0 a 1)."""
        memoria.recordar(carpeta, hoja, scroll)


def iniciar(carpeta=None):
    """Crea la ventana y se queda en ella hasta que se cierra."""
    api = Api(carpeta)
    # La ventana se guarda despues de crearla porque necesita la Api; no puede ser un metodo
    # publico de Api, porque pywebview lo dejaria llamar desde la pagina.
    api._ventana = webview.create_window(  # pylint: disable=protected-access
        NOMBRE_APP, html=pagina(), js_api=api, width=1380, height=860,
        background_color=FONDOS[memoria.tema()], min_size=(900, 560))
    webview.start()
