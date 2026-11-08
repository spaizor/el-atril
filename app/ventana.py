"""Ventana de El Atril (pywebview) y funciones que la pagina puede llamar desde JavaScript."""
import os

import webview

from . import APP_VERSION
from .biblioteca import Biblioteca

NOMBRE_APP = 'El Atril'

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
            .replace('__APP_VERSION__', APP_VERSION))


class Api:
    """Lo que ve la pagina como pywebview.api.

    Solo se exponen los metodos publicos: los atributos van con '_' delante para que
    pywebview no intente recorrerlos.
    """

    def __init__(self, carpeta=None):
        self._ventana = None
        self._biblio = None
        if carpeta and os.path.isdir(carpeta):
            self._biblio = Biblioteca(carpeta)

    def _estado(self):
        b = self._biblio
        if not b:
            return None
        indice = b.listar()
        return {'nombre': b.nombre, 'ruta': b.raiz, 'indice': indice,
                'inicio': b.inicio(indice), 'truncada': b.truncada}

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
        self._biblio = Biblioteca(carpeta)
        self._poner_titulo()
        return self._estado()

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
        """Abre un Excel con su programa."""
        return self._biblio.abrir_externo(ruta) if self._biblio else False


def iniciar(carpeta=None):
    """Crea la ventana y se queda en ella hasta que se cierra."""
    api = Api(carpeta)
    # La ventana se guarda despues de crearla porque necesita la Api; no puede ser un metodo
    # publico de Api, porque pywebview lo dejaria llamar desde la pagina.
    api._ventana = webview.create_window(  # pylint: disable=protected-access
        NOMBRE_APP, html=pagina(), js_api=api, width=1380, height=860,
        background_color='#16181d', min_size=(900, 560))
    webview.start()
