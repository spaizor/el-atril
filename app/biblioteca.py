"""Lectura de una carpeta de documentos: lista las hojas .md, las convierte a HTML y busca en ellas.

No depende de la ventana (pywebview): todo es Python puro y se puede probar por separado.
Las rutas que se intercambian con la pagina son relativas a la carpeta y con '/' como separador.
"""
import base64
import html
import os
import re
import unicodedata
from urllib.parse import unquote

import mistune
from mistune.util import safe_entity
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound

# Carpetas que no se recorren nunca: ocultas (empiezan por '.') y las de herramientas que
# solo tienen documentacion de terceros (paquetes, entornos virtuales...).
CARPETAS_IGNORADAS = {'node_modules', '__pycache__', 'venv', 'site-packages'}

# Hoja que se abre al cargar la carpeta, por orden de preferencia (sin distinguir mayusculas).
HOJAS_INICIO = ('readme.md', 'leeme.md', 'léeme.md', '0_leeme.md', 'index.md')

EXTENSIONES_EXCEL = ('.xlsx', '.xlsm', '.xls')

# Lo que no se abre nunca desde un enlace, porque abrirlo con su programa lo ejecutaria
# (programas, instaladores, scripts, accesos directos...). Salen en gris.
EXTENSIONES_BLOQUEADAS = {
    '.exe', '.com', '.scr', '.pif', '.cpl', '.msc', '.msi', '.msp', '.mst',
    '.bat', '.cmd', '.ps1', '.psm1', '.psd1', '.vbs', '.vbe', '.js', '.jse', '.wsf', '.wsh', '.ws',
    '.hta', '.jar', '.py', '.pyw', '.pyc', '.reg', '.inf', '.lnk', '.url', '.scf',
    '.application', '.appref-ms', '.appx', '.appxbundle', '.msix', '.msixbundle', '.gadget',
    '.settingcontent-ms', '.library-ms', '.search-ms', '.diagcab', '.chm',
}

# Imagenes que se ensenan dentro de las hojas. La pagina se carga como texto, sin ruta base,
# asi que cada imagen de la carpeta va metida en el HTML (data: URI en base64).
TIPOS_IMAGEN = {
    '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.gif': 'image/gif',
    '.webp': 'image/webp', '.svg': 'image/svg+xml', '.bmp': 'image/bmp', '.ico': 'image/x-icon',
    '.avif': 'image/avif',
}
MAX_IMAGEN = 15 * 1024 * 1024        # una imagen mas grande no se mete (sale el aviso)
MAX_IMAGENES_HOJA = 60 * 1024 * 1024  # entre todas las de una hoja, para que no se atasque

_IMG = re.compile(r'<img\b[^>]*>', re.I)
_SRC = re.compile(r'''(\ssrc\s*=\s*)(?:"([^"]*)"|'([^']*)'|([^\s>]+))''', re.I)
_ALT = re.compile(r'''\salt\s*=\s*(?:"([^"]*)"|'([^']*)')''', re.I)

# Tope de hojas por carpeta: si alguien abre una carpeta enorme (C:\, Documentos...) el
# programa no se queda colgado recorriendolo todo.
MAX_HOJAS = 2000


class _Renderizador(mistune.HTMLRenderer):
    """HTML de mistune, con colores en los bloques de codigo que dicen su lenguaje (```python).

    Pygments solo pone las clases de cada trozo (palabra clave, texto, comentario...); los
    colores estan en estilo.css, uno para cada tema. Sin lenguaje, el bloque sale sin colores:
    adivinarlo falla demasiado.
    """
    _formato = HtmlFormatter(nowrap=True)

    def block_code(self, code, info=None):
        lenguaje = info.strip().split(None, 1)[0] if info and info.strip() else ''
        if lenguaje:
            try:
                lexer = get_lexer_by_name(lenguaje)
            except ClassNotFound:
                lexer = None
            if lexer:
                clase = self.render_attrs({'class': 'language-' + safe_entity(lenguaje)})
                coloreado = highlight(code, lexer, self._formato)
                return f'<pre class="coloreado"><code{clase}>{coloreado}</code></pre>\n'
        return super().block_code(code, info)


def plegar(s):
    """Minusculas y sin tildes, un caracter por caracter (para buscar sin distinguir).

    Conserva la longitud del texto, asi las posiciones encontradas valen en el original.
    """
    return ''.join(unicodedata.normalize('NFD', c)[0].lower() for c in s)


class Biblioteca:
    """Una carpeta abierta en El Atril."""

    def __init__(self, raiz):
        self.raiz = os.path.normpath(os.path.abspath(raiz))
        self.nombre = os.path.basename(self.raiz) or self.raiz
        self.truncada = False
        self._md = mistune.create_markdown(
            escape=False, renderer=_Renderizador(escape=False),
            plugins=['table', 'strikethrough', 'task_lists', 'url'])

    # --- Recorrido de la carpeta ---------------------------------------------------------

    def _recorrer(self, extensiones, tope=None):
        """Rutas relativas de los ficheros con esas extensiones, saltando las carpetas ignoradas."""
        res = []
        for d, subs, fs in os.walk(self.raiz):
            subs[:] = sorted(s for s in subs if not s.startswith('.') and s.lower() not in CARPETAS_IGNORADAS)
            for f in sorted(fs, key=str.lower):
                if f.lower().endswith(extensiones) and not f.startswith('~$'):
                    res.append(os.path.relpath(os.path.join(d, f), self.raiz).replace('\\', '/'))
                    if tope and len(res) >= tope:
                        return res, True
        return res, False

    def hojas(self):
        """Hojas .md: primero las de la raiz, luego las de cada subcarpeta."""
        res, self.truncada = self._recorrer(('.md',), MAX_HOJAS)
        res.sort(key=lambda r: (r.count('/'), os.path.dirname(r).lower(), r.lower()))
        return res

    def excels(self):
        res, _ = self._recorrer(EXTENSIONES_EXCEL, MAX_HOJAS)
        return res

    # --- Acceso a un fichero -------------------------------------------------------------

    def ruta_absoluta(self, ruta):
        """Ruta absoluta de una ruta relativa, o None si se sale de la carpeta."""
        p = os.path.normpath(os.path.join(self.raiz, ruta))
        try:
            if os.path.commonpath([p, self.raiz]) != self.raiz:
                return None
        except ValueError:  # otra unidad
            return None
        return p

    # --- Vigilar cambios en disco (sin leer ningun fichero, solo fechas y tamanos) ------

    def firma_hoja(self, ruta):
        """Fecha y tamano de una hoja, o None si no existe. Cambia al guardarla."""
        p = self.ruta_absoluta(ruta)
        try:
            st = os.stat(p) if p else None
        except OSError:
            return None
        return f'{st.st_mtime_ns}-{st.st_size}' if st else None

    def firma_carpeta(self):
        """Huella de las hojas y Excel de la carpeta: cambia si alguno se crea, se borra, se
        renombra o se modifica. Usa os.scandir, que en Windows da la fecha de cada fichero sin
        abrirlo, asi que es rapida incluso con cientos de hojas."""
        datos, pila = [], [self.raiz]
        while pila and len(datos) <= MAX_HOJAS * 2:
            try:
                entradas = list(os.scandir(pila.pop()))
            except OSError:
                continue
            for e in entradas:
                try:
                    if e.is_dir(follow_symlinks=False):
                        if not e.name.startswith('.') and e.name.lower() not in CARPETAS_IGNORADAS:
                            pila.append(e.path)
                    elif (e.name.lower().endswith(('.md',) + EXTENSIONES_EXCEL)
                          and not e.name.startswith('~$')):
                        st = e.stat()
                        datos.append((e.path, st.st_mtime_ns, st.st_size))
                except OSError:
                    pass
        return str(hash(tuple(sorted(datos))))

    def texto(self, ruta):
        p = self.ruta_absoluta(ruta)
        if not p:
            return ''
        with open(p, encoding='utf-8-sig', errors='replace') as f:
            return f.read()

    # --- Lo que pide la pagina -----------------------------------------------------------

    def listar(self):
        """Indice para el panel lateral: las hojas .md con su titulo y luego los Excel."""
        out = []
        for r in self.hojas():
            try:
                t = self.texto(r)
            except OSError:
                t = ''
            m = re.search(r'^#\s+(.+)$', t, re.M)
            titulo = re.sub(r'[*_`]', '', m.group(1)).strip() if m else os.path.basename(r)
            out.append(dict(ruta=r, titulo=titulo, grupo=os.path.dirname(r), tipo='md'))
        for r in self.excels():
            out.append(dict(ruta=r, titulo=os.path.basename(r), grupo='Excel (se abren aparte)', tipo='xlsx'))
        return out

    def inicio(self, indice):
        """Hoja que se abre al cargar la carpeta: un README/LEEME de la raiz, o la primera."""
        raiz = {f['ruta'].lower(): f['ruta'] for f in indice if f['tipo'] == 'md' and '/' not in f['ruta']}
        for nombre in HOJAS_INICIO:
            if nombre in raiz:
                return raiz[nombre]
        hojas = [f['ruta'] for f in indice if f['tipo'] == 'md']
        return hojas[0] if hojas else None

    def leer(self, ruta):
        """HTML de una hoja .md, con sus imagenes dentro."""
        try:
            return self._imagenes(ruta, self._md(self.texto(ruta)))
        except Exception as e:
            return f'<p>No se pudo abrir <code>{html.escape(ruta)}</code>: {html.escape(str(e))}</p>'

    def _imagenes(self, ruta, codigo):
        """Cambia el src de las imagenes de la carpeta por su contenido (data: URI).

        Vale para las de Markdown (![](foto.png)) y las de HTML (<img src="foto.png">). Las
        rutas son relativas a la hoja, como los enlaces. Las de internet (https:) no se cargan,
        para no conectarse a nada. Esas, y las que no se encuentran, se salen de la carpeta o
        son demasiado grandes, se cambian por un aviso con su texto alternativo.
        """
        base = os.path.dirname(ruta)
        gastado = 0

        def cambiar(m):
            nonlocal gastado
            etiqueta = m.group(0)
            s = _SRC.search(etiqueta)
            if not s:
                return etiqueta
            src = html.unescape(next(g for g in s.groups()[1:] if g is not None)).strip()
            if not src or src.lower().startswith('data:'):
                return etiqueta
            a = _ALT.search(etiqueta)
            alt = html.unescape(next((g for g in a.groups() if g is not None), '')) if a else ''
            if re.match(r'^https?:', src, re.I):
                # Las de internet no se cargan (El Atril no se conecta a nada): queda el aviso
                # con su texto. Si la imagen esta dentro de un enlace (las insignias de los
                # README), el enlace sigue funcionando.
                return (f'<span class="img-rota" title="Imagen de internet (no se carga): '
                        f'{html.escape(src)}">🖼 {html.escape(alt or "Imagen de internet")}</span>')
            motivo = None
            if re.match(r'^[a-z][a-z0-9+.-]*:', src, re.I) or src.startswith(('/', '\\')):
                motivo = 'Solo se enseñan imágenes de esta carpeta'
            else:
                rel = unquote(src.split('#', 1)[0].split('?', 1)[0])
                p = self.ruta_absoluta(os.path.join(base, rel))
                tipo = TIPOS_IMAGEN.get(os.path.splitext(rel)[1].lower())
                if not p or not os.path.isfile(p):
                    motivo = 'No se encuentra esta imagen en la carpeta'
                elif not tipo:
                    motivo = 'Este tipo de imagen no se puede enseñar'
                else:
                    tam = os.path.getsize(p)
                    if tam > MAX_IMAGEN or gastado + tam > MAX_IMAGENES_HOJA:
                        motivo = 'Imagen demasiado grande para enseñarla aquí'
                    else:
                        try:
                            with open(p, 'rb') as f:
                                datos = base64.b64encode(f.read()).decode('ascii')
                        except OSError:
                            motivo = 'No se pudo leer esta imagen'
                        else:
                            gastado += tam
                            return (etiqueta[:s.start()] + f'{s.group(1)}"data:{tipo};base64,{datos}"'
                                    + etiqueta[s.end():])
            return (f'<span class="img-rota" title="{html.escape(motivo)}: {html.escape(src)}">'
                    f'🖼 {html.escape(alt or os.path.basename(src) or src)}</span>')

        return _IMG.sub(cambiar, codigo)

    def estado_enlace(self, ruta):
        """Que pasa al pinchar un enlace a un fichero de la carpeta que no es una hoja:

        'fichero' o 'carpeta' si se puede abrir, 'bloqueado' si es un programa o script,
        'falta' si no existe o se sale de la carpeta.
        """
        p = self.ruta_absoluta(ruta)
        if not p:
            return 'falta'
        if os.path.isdir(p):
            return 'carpeta'
        if not os.path.isfile(p):
            return 'falta'
        if os.path.splitext(p)[1].lower() in EXTENSIONES_BLOQUEADAS:
            return 'bloqueado'
        return 'fichero'

    def abrir_externo(self, ruta):
        """Abre un fichero (o una carpeta, en el Explorador) con el programa que tenga
        asociado Windows. Nunca abre programas ni scripts: abrir un documento no debe
        poder ejecutar nada."""
        if self.estado_enlace(ruta) not in ('fichero', 'carpeta'):
            return False
        os.startfile(self.ruta_absoluta(ruta))
        return True

    def buscar(self, q):
        """Busca q en todas las hojas. Devuelve por hoja el total y hasta 3 trozos de contexto.

        En los trozos, la coincidencia va entre los caracteres \\x01 y \\x02 para que la pagina
        la resalte sin tener que escapar HTML aqui.
        """
        fq = plegar(q)
        if not fq:
            return []
        res = []
        for it in self.listar():
            if it['tipo'] != 'md':
                continue
            try:
                t = self.texto(it['ruta'])
            except OSError:
                continue
            ft = plegar(t)
            total = ft.count(fq)
            if not total:
                continue
            trozos = []
            i = ft.find(fq)
            while i >= 0 and len(trozos) < 3:
                a, b = max(0, i - 45), min(len(t), i + len(fq) + 55)
                s = t[a:b].replace('\n', ' ')
                k = i - a
                s = s[:k] + '\x01' + s[k:k + len(fq)] + '\x02' + s[k + len(fq):]
                trozos.append(('…' if a else '') + s + ('…' if b < len(t) else ''))
                i = ft.find(fq, i + 200)
            res.append(dict(ruta=it['ruta'], titulo=it['titulo'], total=total, trozos=trozos))
        res.sort(key=lambda x: -x['total'])
        return res
