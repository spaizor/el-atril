"""El Atril: lector de Markdown para Windows.

Uso:
    python main.py              abre la ventana vacia, con el boton para elegir carpeta
    python main.py <carpeta>    abre directamente esa carpeta
    python main.py <hoja.md>    abre la carpeta de esa hoja, por esa hoja

Con el .exe vale lo mismo: tambien se puede arrastrar una carpeta o un .md encima del
ejecutable, o abrir un .md con "Abrir con..." > El Atril.
"""
import sys

from app.ventana import iniciar


def main():
    ruta = sys.argv[1] if len(sys.argv) > 1 else None
    iniciar(ruta)


if __name__ == '__main__':
    main()
