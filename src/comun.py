# %%
# ============================================================
# 0. Librerías, estilo y funciones de apoyo
# ============================================================
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

pd.set_option("display.max_columns", None)
pd.set_option("display.float_format", lambda v: f"{v:,.4g}" if v != 0 and abs(v) < 0.01 else f"{v:,.3f}")

sns.set_theme(style="whitegrid", context="notebook")
AZUL, NARANJA, VERDE, AMARILLO = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
plt.rcParams.update({"figure.figsize": (10, 4), "axes.titleweight": "bold"})

# Los datos se leen del repositorio de GitHub, así el notebook funciona
# igual en Colab, en Jupyter local o en VS Code sin subir nada a mano.
URL_DATOS = "https://raw.githubusercontent.com/DANIFUZZY1975/estadistica-descriptiva-python/main/data/"

def cargar(nombre, **kwargs):
    """Busca el CSV en local (../data o carpeta actual); si no está, lo baja de GitHub."""
    for ruta in (os.path.join("..", "data", nombre), os.path.join("data", nombre), nombre):
        if os.path.exists(ruta):
            return pd.read_csv(ruta, **kwargs)
    return pd.read_csv(URL_DATOS + nombre, **kwargs)


def moda(x, bins="sturges"):
    """Moda:
    - variable discreta (pocos valores distintos) -> valor más repetido;
    - variable continua -> moda INTERPOLADA dentro de la clase modal del histograma:
          Mo = L + d1 / (d1 + d2) * a
      con L = extremo inferior de la clase modal, a = su amplitud,
          d1 = n_i - n_(i-1)  (diferencia con la clase de la izquierda),
          d2 = n_i - n_(i+1)  (diferencia con la clase de la derecha).
      Es el punto donde se cortan las rectas que unen, en cruz, las esquinas superiores
      de la barra modal con las de sus vecinas: si la vecina izquierda es más alta,
      la moda se desplaza a la izquierda, y al revés. Siempre queda dentro de la clase modal."""
    x = pd.Series(x).dropna()
    if x.nunique() <= 30:
        return x.mode().iloc[0]
    frec, bordes = np.histogram(x, bins=bins)
    i = frec.argmax()
    n_izq = frec[i - 1] if i > 0 else 0
    n_der = frec[i + 1] if i < len(frec) - 1 else 0
    d1, d2 = frec[i] - n_izq, frec[i] - n_der
    L, a = bordes[i], bordes[i + 1] - bordes[i]
    if d1 + d2 == 0:          # meseta: las tres barras iguales -> punto medio
        return L + a / 2
    return L + d1 / (d1 + d2) * a


def limites_tukey(x, k=1.5):
    """Vallas de Tukey: [Q1 - k·IQR , Q3 + k·IQR] (las del diagrama de caja)."""
    q1, q3 = np.nanquantile(x, [0.25, 0.75])
    iqr = q3 - q1
    return q1 - k * iqr, q3 + k * iqr


def resumen(x):
    """Todas las medidas descriptivas de una variable cuantitativa en una Serie."""
    x = pd.Series(x).dropna().astype(float)
    q1, me, q3 = x.quantile([0.25, 0.50, 0.75])
    li, ls = limites_tukey(x)
    return pd.Series({
        # --- tamaño
        "n": x.size,
        # --- medidas de posición central
        "media": x.mean(),
        "mediana": me,
        "moda": moda(x),
        "media_recortada_5%": stats.trim_mean(x, 0.05),  # quita el 5 % de CADA cola
        # --- medidas de posición no central
        "min": x.min(), "Q1": q1, "Q3": q3, "max": x.max(),
        # --- medidas de dispersión
        "rango": x.max() - x.min(),
        "IQR": q3 - q1,
        "varianza": x.var(),          # cuasivarianza (divide entre n-1)
        "desv_tipica": x.std(),       # cuasidesviación típica (n-1)
        "CV_%": 100 * x.std() / abs(x.mean()) if x.mean() != 0 else np.nan,
        "MAD": stats.median_abs_deviation(x),  # mediana de |x - mediana|
        # --- medidas de forma
        "asimetria_Fisher": x.skew(),
        "asimetria_Pearson": 3 * (x.mean() - me) / x.std(),
        "curtosis_exceso": x.kurt(),  # 0 = como la normal
        # --- anómalos
        "n_atipicos_Tukey": int(((x < li) | (x > ls)).sum()),
    })


def histograma_con_centros(x, titulo="", bins="sturges", ax=None, color=AZUL):
    """Histograma + KDE con media, mediana y moda marcadas."""
    x = pd.Series(x).dropna()
    ax = ax or plt.gca()
    sns.histplot(x, bins=bins, kde=True, color=color, alpha=0.35, ax=ax)
    for valor, etiqueta, estilo in [(x.mean(), "media", "-"),
                                    (x.median(), "mediana", "--"),
                                    (moda(x, bins=bins), "moda", ":")]:
        ax.axvline(valor, color="#333333", ls=estilo, lw=2,
                   label=f"{etiqueta} = {valor:,.2f}")
    ax.set_title(titulo or x.name)
    ax.legend(frameon=False)
    return ax


# ============================================================
# Regresión: lineal, potencial y exponencial
# ============================================================
def r2(y_obs, y_pred):
    """Coeficiente de determinación: 1 - SCresidual / SCtotal."""
    y_obs, y_pred = np.asarray(y_obs, float), np.asarray(y_pred, float)
    return 1 - np.sum((y_obs - y_pred) ** 2) / np.sum((y_obs - y_obs.mean()) ** 2)


def recta_minimos_cuadrados(x, y):
    """Recta de regresión de y sobre x:  y = a + b·x,
    b = S_xy / S_x^2   y   a = media(y) - b·media(x)."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    sxy = np.mean((x - x.mean()) * (y - y.mean()))
    sx2 = np.mean((x - x.mean()) ** 2)
    b = sxy / sx2
    a = y.mean() - b * x.mean()
    return a, b


def regresiones(x, y):
    """Ajusta los tres modelos por mínimos cuadrados.
    - Lineal:      y = a + b·x
    - Potencial:   y = a·x^b      ->  ln y = ln a + b·ln x   (exige x > 0 e y > 0)
    - Exponencial: y = a·e^(b·x)  ->  ln y = ln a + b·x      (exige y > 0)
    Devuelve (tabla, modelos), donde modelos[nombre] es una función que predice y."""
    datos = pd.DataFrame({"x": x, "y": y}).dropna()
    x, y = datos["x"].to_numpy(float), datos["y"].to_numpy(float)
    filas, modelos = [], {}

    a, b = recta_minimos_cuadrados(x, y)
    modelos["lineal"] = lambda t, a=a, b=b: a + b * np.asarray(t, float)
    filas.append({"modelo": "lineal", "ecuación": f"y = {a:,.4g} + {b:,.4g}·x", "a": a, "b": b,
                  "R2 (escala del ajuste)": r2(y, modelos["lineal"](x)),
                  "R2 (escala original)": r2(y, modelos["lineal"](x))})

    if (x > 0).all() and (y > 0).all():
        A, b = recta_minimos_cuadrados(np.log(x), np.log(y))
        a = np.exp(A)
        modelos["potencial"] = lambda t, a=a, b=b: a * np.asarray(t, float) ** b
        filas.append({"modelo": "potencial", "ecuación": f"y = {a:,.4g}·x^{b:,.4g}", "a": a, "b": b,
                      "R2 (escala del ajuste)": r2(np.log(y), A + b * np.log(x)),
                      "R2 (escala original)": r2(y, modelos["potencial"](x))})
    else:
        filas.append({"modelo": "potencial", "ecuación": "no aplicable: necesita x > 0 e y > 0"})

    if (y > 0).all():
        A, b = recta_minimos_cuadrados(x, np.log(y))
        a = np.exp(A)
        modelos["exponencial"] = lambda t, a=a, b=b: a * np.exp(b * np.asarray(t, float))
        filas.append({"modelo": "exponencial", "ecuación": f"y = {a:,.4g}·e^({b:,.4g}·x)", "a": a, "b": b,
                      "R2 (escala del ajuste)": r2(np.log(y), A + b * x),
                      "R2 (escala original)": r2(y, modelos["exponencial"](x))})
    else:
        filas.append({"modelo": "exponencial", "ecuación": "no aplicable: necesita y > 0"})

    return pd.DataFrame(filas).set_index("modelo"), modelos


COLOR_MODELO = {"lineal": AZUL, "potencial": NARANJA, "exponencial": VERDE}


def dibujar_regresiones(x, y, modelos, ax=None, n_puntos=3000, xlabel=None, ylabel=None, titulo=""):
    """Nube de puntos + las curvas ajustadas (si hay muchos puntos, se dibuja una muestra)."""
    datos = pd.DataFrame({"x": x, "y": y}).dropna()
    muestra = datos.sample(min(n_puntos, len(datos)), random_state=1)
    ax = ax or plt.gca()
    ax.scatter(muestra["x"], muestra["y"], s=10, alpha=0.3, color="#9aa0a6")
    xs = np.linspace(datos["x"].min(), datos["x"].max(), 300)
    for nombre, f in modelos.items():
        ax.plot(xs, f(xs), lw=2.5, color=COLOR_MODELO[nombre], label=nombre)
    ax.set_xlabel(xlabel or getattr(x, "name", "x")); ax.set_ylabel(ylabel or getattr(y, "name", "y"))
    ax.set_title(titulo); ax.legend(frameon=False)
    return ax
