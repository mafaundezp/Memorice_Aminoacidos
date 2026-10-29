from pathlib import Path
import sys

import fitz  # PyMuPDF
from PIL import Image, ImageChops

# Resolución de referencia de la página del PDF que compartiste.
REF_W, REF_H = 2736, 1342

# Recortes aproximados: (x inicial, y inicial, x final, y final)
RECORTES = [
    (45, 20, 370, 205),
    (565, 20, 885, 205),
    (1000, 15, 1330, 205),
    (1870, 15, 2110, 215),
    (2160, 25, 2430, 215),
    (40, 290, 270, 500),
    (365, 290, 660, 505),
    (780, 290, 1050, 505),
    (1710, 315, 2070, 515),
    (2240, 290, 2530, 515),
    (120, 620, 475, 820),
    (540, 620, 865, 830),
    (940, 610, 1200, 835),
    (1760, 610, 2090, 835),
    (2280, 550, 2670, 760),
    (2080, 785, 2460, 970),
]

def main():
    if len(sys.argv) < 2:
        print('Uso: python3 separar_png.py "imagenes.pdf"')
        return

    pdf = Path(sys.argv[1]).resolve()
    if not pdf.exists():
        raise FileNotFoundError(f"No se encontró el PDF: {pdf}")

    salida = pdf.parent / f"{pdf.stem}_PNG"
    salida.mkdir(exist_ok=True)

    documento = fitz.open(pdf)
    pagina = documento[0]

    # Renderiza la página a alta resolución.
    pix = pagina.get_pixmap(matrix=fitz.Matrix(3, 3), alpha=False)
    imagen = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    escala_x = imagen.width / REF_W
    escala_y = imagen.height / REF_H

    for i, (x1, y1, x2, y2) in enumerate(RECORTES, start=1):
        caja = (
            round(x1 * escala_x),
            round(y1 * escala_y),
            round(x2 * escala_x),
            round(y2 * escala_y),
        )
        recorte = imagen.crop(caja)

        # Recorta el espacio blanco sobrante y deja un pequeño margen.
        diferencia = ImageChops.difference(
            recorte, Image.new("RGB", recorte.size, "white")
        )
        mascara = diferencia.convert("L").point(lambda p: 255 if p > 18 else 0)
        limites = mascara.getbbox()

        if limites:
            recorte = recorte.crop(limites)
            margen = 18
            lienzo = Image.new(
                "RGB",
                (recorte.width + 2 * margen, recorte.height + 2 * margen),
                "white",
            )
            lienzo.paste(recorte, (margen, margen))
            recorte = lienzo

        recorte.save(salida / f"estructura_{i:02d}.png")

    print(f"Se guardaron {len(RECORTES)} PNG en: {salida}")

if __name__ == "__main__":
    main()