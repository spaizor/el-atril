# El Atril

*[English version](README.en.md)*

Lector de Markdown para Windows. Abres una carpeta y El Atril te enseña todas sus hojas `.md`
con formato, en tema oscuro, con un panel lateral para saltar de una a otra, buscador y
navegación atrás / adelante, como si fuera una pequeña web de documentación.

Está pensado para leer documentación: la de un proyecto, unos apuntes, una guía repartida en
varios ficheros que se enlazan entre sí. Solo lee; para editar los `.md` sigue usando tu editor
de siempre y pulsa F5 en El Atril para ver los cambios.

## Características

- **Abre cualquier carpeta** con el botón *Abrir* (o Ctrl+O). Recorre también las subcarpetas.
- **Panel lateral** con todas las hojas, agrupadas por carpeta y con el título de cada una
  (el primer `# Título` del fichero).
- **Arranca en la portada**: si hay un `README.md`, `LEEME.md` o `index.md` en la raíz, empieza
  por ahí.
- **Enlaces entre hojas**: un enlace a otro `.md` de la carpeta lo abre dentro de El Atril,
  incluidos los enlaces a un apartado (`hoja.md#apartado`). Los enlaces a webs se abren en tu
  navegador.
- **Atrás y adelante** como en un navegador (Alt+← y Alt+→).
- **Buscador** en la hoja que estás leyendo, que resalta las coincidencias sin distinguir
  mayúsculas ni tildes, y **búsqueda en todas las hojas** con un trocito de contexto de cada
  resultado.
- **Recargar** (F5) para ver los cambios si estás editando los `.md` a la vez.
- **Tablas, listas de tareas, tachado y bloques de código**, además del Markdown normal.
- **Excel de la carpeta** en un apartado propio del panel: se abren con Excel, fuera de El Atril.

## Requisitos

- Windows 10 u 11.
- **Microsoft Edge WebView2 Runtime**, que es lo que dibuja la ventana. Ya viene con Windows 11
  y con Windows 10 actualizado; si faltara, se descarga gratis desde la web de Microsoft.
- Para ejecutarlo desde el código: **Python 3.13**.

## Instalación

Todavía no hay un `.exe` publicado: de momento se ejecuta desde el código.

```powershell
git clone https://github.com/spaizor/el-atril.git
cd el-atril
py -3.13 -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python main.py
```

### Compilar el .exe

```powershell
.venv\Scripts\pyinstaller build.spec
```

Deja `dist\El Atril.exe`, un único fichero que funciona sin tener Python instalado.

## Uso

Al abrirlo, pulsa **Abrir carpeta…** y elige la carpeta con tus documentos. También puedes
pasarle la carpeta al arrancar, y así se abre directamente:

```powershell
.venv\Scripts\python main.py "C:\ruta\a\mis documentos"
```

Con el `.exe` vale lo mismo, y además puedes **arrastrar una carpeta encima del `.exe`**.

### Atajos de teclado

| Tecla | Qué hace |
|---|---|
| Ctrl+O | Abrir otra carpeta |
| Ctrl+F | Ir al buscador |
| Intro / Mayús+Intro | Coincidencia siguiente / anterior (también F3 / Mayús+F3) |
| Ctrl+Intro | Buscar en todas las hojas |
| Esc | Borrar la búsqueda |
| Alt+← / Alt+→ | Atrás / adelante |
| F5 o Ctrl+R | Recargar la carpeta y la hoja actual |

## Privacidad

El Atril no se conecta a internet ni guarda nada: solo lee los ficheros de la carpeta que abres,
y únicamente mientras está abierto. Los enlaces a webs que haya dentro de tus documentos solo se
abren, en tu navegador, si haces clic en ellos.

## Limitaciones conocidas

- **Las imágenes de los `.md` todavía no se ven.**
- Los enlaces a ficheros que no son `.md` (PDF, imágenes...) no se abren desde El Atril; salen en
  gris.
- No entra en carpetas ocultas (las que empiezan por `.`) ni en `node_modules`, `__pycache__`,
  `venv` o `site-packages`, que suelen estar llenas de documentación ajena.
- En carpetas muy grandes muestra como mucho las primeras 2000 hojas, para no quedarse colgado.
- La interfaz solo está en español.
- Solo se ha probado en Windows 11.

## Cómo funciona por dentro

Es una ventana de [pywebview](https://pywebview.flowrl.com/) que muestra una página HTML; el
Markdown se convierte a HTML con [mistune](https://github.com/lepture/mistune).

| Fichero | Qué hace |
|---|---|
| `main.py` | Arranque: crea la ventana, con la carpeta que se le pase o sin ninguna |
| `el_atril/biblioteca.py` | Recorre la carpeta, convierte cada hoja a HTML y busca en ellas (Python puro, sin ventana) |
| `el_atril/ventana.py` | La ventana y las funciones que la página llama desde JavaScript |
| `el_atril/web/` | La página: `index.html`, `estilo.css` y `app.js` |
| `build.spec` | Receta de PyInstaller para compilar el `.exe` |

## Historial de versiones

- **0.5** (06-11-2026): primera version. Boton Abrir (o Ctrl+O) para elegir una carpeta y leer sus hojas .md con panel lateral, enlaces entre hojas, atras y adelante, buscador en la hoja y en todas las hojas, recargar con F5 y los Excel de la carpeta para abrirlos aparte. La carpeta tambien se puede pasar al arrancar o arrastrar encima del .exe.

## Licencia

[MIT](LICENSE): puedes usarlo, copiarlo, cambiarlo y repartirlo libremente, manteniendo el aviso
de la licencia.
