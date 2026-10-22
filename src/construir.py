"""Genera los notebooks de /notebooks a partir de los .py (formato jupytext percent) de /src.
Uso: python src/construir.py [--ejecutar] [nombre ...]"""
import sys, pathlib, jupytext, nbformat
from nbclient import NotebookClient

RAIZ = pathlib.Path(__file__).resolve().parent.parent
REPO = "DANIFUZZY1975/estadistica-descriptiva-python"
comun = (RAIZ / "src" / "comun.py").read_text(encoding="utf-8").replace("# %%\n", "", 1)

ejecutar = "--ejecutar" in sys.argv
nombres = [a for a in sys.argv[1:] if not a.startswith("--")]
fuentes = sorted((RAIZ / "src").glob("0*.py"))
if nombres:
    fuentes = [f for f in fuentes if any(n in f.stem for n in nombres)]

for f in fuentes:
    texto = f.read_text(encoding="utf-8").replace("# (el bloque de configuración común se inserta aquí)\n#@@COMUN@@\n", comun)
    nb = jupytext.reads(texto, fmt="py:percent")
    badge = (f"[![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)]"
             f"(https://colab.research.google.com/github/{REPO}/blob/main/notebooks/{f.stem}.ipynb)\n\n")
    nb.cells[0].source = badge + nb.cells[0].source
    nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
    nb.metadata["colab"] = {"provenance": []}
    if ejecutar:
        NotebookClient(nb, timeout=600, kernel_name="python3",
                       resources={"metadata": {"path": str(RAIZ / "notebooks")}}).execute()
    salida = RAIZ / "notebooks" / f"{f.stem}.ipynb"
    nbformat.write(nb, salida)
    print("OK", salida.name, f"{salida.stat().st_size/1e6:.1f} MB")
