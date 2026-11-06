"""El Atril: lector de Markdown para Windows.

Uso:
    python main.py              abre la ventana vacia, con el boton para elegir carpeta
    python main.py <carpeta>    abre directamente esa carpeta

Con el .exe vale lo mismo: tambien se puede arrastrar una carpeta encima del ejecutable.
"""
import sys

from el_atril.ventana import iniciar


def main():
    carpeta = sys.argv[1] if len(sys.argv) > 1 else None
    iniciar(carpeta)


if __name__ == '__main__':
    main()
