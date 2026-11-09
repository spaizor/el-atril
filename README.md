# El Atril

*[English version](README.en.md)*

Lector de Markdown para Windows. Abres una carpeta y El Atril te enseña todas sus hojas `.md`
con formato, en tema oscuro, con un panel lateral para saltar de una a otra, buscador y
navegación atrás / adelante, como si fuera una pequeña web de documentación.

Está pensado para leer documentación: la de un proyecto, unos apuntes, una guía repartida en
varios ficheros que se enlazan entre sí. Solo lee; para editar los `.md` sigue usando tu editor
de siempre: El Atril enseña los cambios en cuanto guardas.

## Características

- **Abre cualquier carpeta** con el botón *Abrir* (o Ctrl+O). Recorre también las subcarpetas.
- **Carpetas recientes**: al arrancar, el panel lateral muestra las últimas carpetas que has
  abierto para volver a ellas con un clic (la × las quita de la lista). El botón *Cerrar* (o Ctrl+W) cierra la carpeta abierta y vuelve
  a esa lista.
- **Panel lateral** con todas las hojas, agrupadas por carpeta y con el título de cada una
  (el primer `# Título` del fichero).
- **Índice de la hoja**: debajo de la hoja abierta, en el panel, salen sus títulos para saltar a
  cada apartado. Se resalta el apartado que estás leyendo.
- **Arranca en la portada**: si hay un `README.md`, `LEEME.md` o `index.md` en la raíz, empieza
  por ahí.
- **Sigues donde lo dejaste**: al volver a una carpeta, abre la última hoja que leíste y a la
  misma altura.
- **Tamaño de letra** ajustable con los botones *A−* y *A+*, con Ctrl+rueda o con Ctrl+ +/−
  (Ctrl+0 lo deja normal). Se recuerda para la próxima vez.
- **Enlaces entre hojas**: un enlace a otro `.md` de la carpeta lo abre dentro de El Atril,
  incluidos los enlaces a un apartado (`hoja.md#apartado`). Los enlaces a webs se abren en tu
  navegador.
- **Enlaces a otros ficheros** de la carpeta (PDF, imágenes, documentos...): se abren con su
  programa de Windows, y los enlaces a una carpeta, en el Explorador. Llevan una flechita ↗. Por
  seguridad, los programas y scripts (`.exe`, `.bat`, `.ps1`, `.py`...) no se abren nunca y salen
  en gris.
- **Tema claro y oscuro**: la bombilla de arriba a la derecha cambia de uno a otro. Se recuerda
  para la próxima vez.
- **Atrás y adelante** como en un navegador (Alt+← y Alt+→).
- **Buscador** en la hoja que estás leyendo, que resalta las coincidencias sin distinguir
  mayúsculas ni tildes, y **búsqueda en todas las hojas** con un trocito de contexto de cada
  resultado.
- **Se actualiza solo**: si editas la hoja abierta en otro programa y guardas, El Atril la
  actualiza en un segundo sin moverte de donde estabas. Las hojas nuevas, renombradas o borradas
  también aparecen o desaparecen solas del panel. Solo mira las fechas de los ficheros (no vuelve
  a leer nada hasta que algo cambia), así que no carga el ordenador.
- **Tablas, listas de tareas, tachado y bloques de código**, además del Markdown normal.
- **Colores en el código**: los bloques que dicen su lenguaje (` ```python `, ` ```powershell `,
  ` ```json `...) salen coloreados, en los dos temas. Los bloques sin lenguaje salen sin colores.
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
| Ctrl+W | Cerrar la carpeta y volver a las recientes |
| Ctrl+F | Ir al buscador |
| Intro / Mayús+Intro | Coincidencia siguiente / anterior (también F3 / Mayús+F3) |
| Ctrl+Intro | Buscar en todas las hojas |
| Esc | Borrar la búsqueda |
| Alt+← / Alt+→ | Atrás / adelante |
| F5 o Ctrl+R | Recargar a mano la carpeta y la hoja actual (ya lo hace solo) |
| Ctrl+rueda o Ctrl+ +/− | Letra más grande / más pequeña |
| Ctrl+0 | Letra a su tamaño normal |

## Privacidad

El Atril no se conecta a internet y solo lee los ficheros de la carpeta que abres. Lo único que
guarda, en `%APPDATA%\El Atril`, es:

- `recientes.json`: la lista de las últimas carpetas abiertas (sus rutas, nada de su contenido).
- `memoria.json`: el tamaño de letra, el tema y, de cada carpeta, el nombre de la última hoja leída y por
  dónde ibas.

Si borras esos ficheros, El Atril empieza de cero.

Los enlaces a webs que haya dentro de tus documentos solo se abren, en tu navegador, si haces
clic en ellos.

## Limitaciones conocidas

- **Las imágenes de los `.md` todavía no se ven.**
- No entra en carpetas ocultas (las que empiezan por `.`) ni en `node_modules`, `__pycache__`,
  `venv` o `site-packages`, que suelen estar llenas de documentación ajena.
- En carpetas muy grandes muestra como mucho las primeras 2000 hojas, para no quedarse colgado.
- La interfaz solo está en español.
- Solo se ha probado en Windows 11.

## Cómo funciona por dentro

Es una ventana de [pywebview](https://pywebview.flowrl.com/) que muestra una página HTML; el
Markdown se convierte a HTML con [mistune](https://github.com/lepture/mistune) y los bloques de
código se colorean con [Pygments](https://pygments.org/).

| Fichero | Qué hace |
|---|---|
| `main.py` | Arranque: crea la ventana, con la carpeta que se le pase o sin ninguna |
| `app/biblioteca.py` | Recorre la carpeta, convierte cada hoja a HTML y busca en ellas (Python puro, sin ventana) |
| `app/recientes.py` | La lista de las últimas carpetas abiertas |
| `app/memoria.py` | Lo que se recuerda entre sesiones: tamaño de letra, tema y última hoja de cada carpeta |
| `app/ventana.py` | La ventana y las funciones que la página llama desde JavaScript |
| `app/web/` | La página: `index.html`, `estilo.css` y `app.js` |
| `build.spec` | Receta de PyInstaller para compilar el `.exe` |

## Historial de versiones

- **0.5** (06-11-2026): primera version. Boton Abrir (o Ctrl+O) para elegir una carpeta y leer sus hojas .md con panel lateral, enlaces entre hojas, atras y adelante, buscador en la hoja y en todas las hojas, recargar con F5 y los Excel de la carpeta para abrirlos aparte. La carpeta tambien se puede pasar al arrancar o arrastrar encima del .exe.
- **0.6** (08-11-2026): al arrancar, el panel lateral muestra las ultimas carpetas abiertas para volver a ellas con un clic (se guardan en %APPDATA%\El Atril\recientes.json; las que ya no existen salen en gris y la x las quita de la lista). Boton rojo Cerrar (o Ctrl+W) para cerrar la carpeta abierta y volver a esa lista. El codigo pasa de la carpeta el_atril a app.
- **0.7** (09-11-2026): indice de la hoja en el panel para saltar a cada apartado. Al volver a una carpeta abre la ultima hoja leida y a la misma altura. Tamano de letra ajustable (botones A- y A+, Ctrl+rueda, Ctrl +/- y Ctrl+0). Los enlaces a otros ficheros de la carpeta (PDF, imagenes...) se abren con su programa de Windows; los programas y scripts no se abren nunca. Tema claro y oscuro con el boton de la bombilla. Colores en los bloques de codigo que indican su lenguaje (Pygments). La hoja y el panel se actualizan solos cuando los .md cambian en disco y se quita el boton de recargar (F5 sigue funcionando). Letra, tema y ultima hoja de cada carpeta se guardan en %APPDATA%\El Atril\memoria.json.

## Licencia

[MIT](LICENSE): puedes usarlo, copiarlo, cambiarlo y repartirlo libremente, manteniendo el aviso
de la licencia.
