# %%
# ============================================================
# 0. Librerías y estilo de los gráficos
# ============================================================
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

pd.set_option("display.max_columns", None)
pd.set_option("display.float_format", lambda v: f"{v:,.4g}" if v != 0 and abs(v) < 0.01 else f"{v:,.3f}")

sns.set_theme(style="whitegrid", context="notebook")
plt.rcParams.update({"figure.figsize": (10, 4), "axes.titleweight": "bold"})
AZUL, NARANJA, VERDE = "#2a78d6", "#eb6834", "#1baf7a"

# Los datos están en el repositorio de GitHub: así no hay que subir nada a Colab
URL_DATOS = "https://raw.githubusercontent.com/DANIFUZZY1975/estadistica-descriptiva-python/main/data/"
