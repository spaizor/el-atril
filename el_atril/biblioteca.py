"""Lectura de una carpeta de documentos: lista las hojas .md, las convierte a HTML y busca en ellas.

No depende de la ventana (pywebview): todo es Python puro y se puede probar por separado.
Las rutas que se intercambian con la pagina son relativas a la carpeta y con '/' como separador.
"""
import os
import re
import unicodedata

import mistune

# Carpetas que no se recorren nunca: ocultas (empiezan por '.') y las de herramientas que
# solo tienen documentacion de terceros (paquetes, entornos virtuales...).
CARPETAS_IGNORADAS = {'node_modules', '__pycache__', 'venv', 'site-packages'}

# Hoja que se abre al cargar la carpeta, por orden de preferencia (sin distinguir mayusculas).
HOJAS_INICIO = ('readme.md', 'leeme.md', 'léeme.md', '0_leeme.md', 'index.md')

EXTENSIONES_EXCEL = ('.xlsx', '.xlsm', '.xls')

# Tope de hojas por carpeta: si alguien abre una carpeta enorme (C:\, Documentos...) el
# programa no se queda colgado recorriendolo todo.
MAX_HOJAS = 2000


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
            escape=False, plugins=['table', 'strikethrough', 'task_lists', 'url'])

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
        """HTML de una hoja .md."""
        try:
            return self._md(self.texto(ruta))
        except Exception as e:
            return f'<p>No se pudo abrir <code>{ruta}</code>: {e}</p>'

    def abrir_externo(self, ruta):
        """Abre un fichero (un Excel) con el programa que tenga asociado Windows."""
        p = self.ruta_absoluta(ruta)
        if p and os.path.isfile(p):
            os.startfile(p)
            return True
        return False

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
