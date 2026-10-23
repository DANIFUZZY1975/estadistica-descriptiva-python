# %% [markdown]
# # 😊 ¿Dónde se vive más feliz? Estadística descriptiva con el *World Happiness Report 2021*
#
# **Estadística Descriptiva · 1.º Grado en Ciencia de Datos · UCM**
#
# Cada fila es un **país** (149). La variable estrella es el **Ladder score**: la puntuación media (0–10)
# que dan los habitantes a la pregunta *"imagina una escalera donde 10 es la mejor vida posible y 0 la peor: ¿en qué peldaño estás?"*.
#
# En este notebook vamos a responder preguntas como:
# - ¿Cuál es el país "típico"? ¿Media o mediana?
# - ¿Qué región del mundo es más feliz… y cuál es más **desigual**?
# - ¿Hay países **anómalos**? (felices siendo pobres, o infelices siendo ricos)
# - ¿Dónde está **España**?
#
# > 💡 Ejecuta las celdas en orden (`Shift + Enter`). Donde veas **🤔**, para y piensa antes de seguir.

# %%
# (el bloque de configuración común se inserta aquí)
#@@COMUN@@

# %% [markdown]
# ## 1. Cargamos y miramos los datos
# Antes de calcular nada: **¿cuántas filas, qué columnas, de qué tipo, hay huecos?**

# %%
df = cargar("world-happiness-report-2021.csv")
print("Dimensiones:", df.shape)
df.head()

# %%
df.info()

# %% [markdown]
# Las columnas `Explained by: ...`, `upperwhisker`, `lowerwhisker`, `Dystopia...` son resultados de un modelo de los autores.
# Nos quedamos con las variables "en bruto" y les ponemos nombres cortos en castellano.

# %%
df = df.rename(columns={
    "Country name": "pais", "Regional indicator": "region", "Ladder score": "felicidad",
    "Logged GDP per capita": "log_PIB", "Social support": "apoyo_social",
    "Healthy life expectancy": "esperanza_vida", "Freedom to make life choices": "libertad",
    "Generosity": "generosidad", "Perceptions of corruption": "corrupcion",
})[["pais", "region", "felicidad", "log_PIB", "apoyo_social", "esperanza_vida",
    "libertad", "generosidad", "corrupcion"]]

# El PIB viene en logaritmo: recuperamos el PIB per cápita en dólares para ver la diferencia
df["PIB_pc"] = np.exp(df["log_PIB"])
cuantitativas = ["felicidad", "PIB_pc", "log_PIB", "apoyo_social", "esperanza_vida",
                 "libertad", "generosidad", "corrupcion"]
df.head()

# %% [markdown]
# ### Tipos de variables
# | Variable | Tipo |
# |---|---|
# | `pais` | cualitativa nominal (identificador) |
# | `region` | cualitativa nominal |
# | `felicidad`, `PIB_pc`, `esperanza_vida`… | cuantitativas continuas |
#
# 🤔 *¿Tiene sentido calcular la "media" de `region`? ¿Y su moda?*

# %% [markdown]
# ## 2. Variable cualitativa: tabla de frecuencias de `region`

# %%
frec = df["region"].value_counts().to_frame("n_i")
frec["f_i"] = frec["n_i"] / frec["n_i"].sum()
frec["N_i"] = frec["n_i"].cumsum()
frec["F_i"] = frec["f_i"].cumsum()
frec

# %% [markdown]
# Las frecuencias acumuladas `N_i` y `F_i` aquí se pueden calcular… pero **no significan nada**,
# porque las regiones no tienen un orden natural. Solo tienen sentido en variables **ordinales** o cuantitativas.

# %%
ax = df["region"].value_counts(ascending=True).plot.barh(color=AZUL)
ax.set_title("Número de países por región")
ax.set_xlabel("Países")
for i, v in enumerate(df["region"].value_counts(ascending=True)):
    ax.text(v + 0.3, i, str(v), va="center")
plt.show()
print("Moda de region:", df["region"].mode()[0])

# %% [markdown]
# ## 3. Medidas de posición: ¿cuál es el país "típico"?

# %%
x = df["felicidad"]
print(f"Media              : {x.mean():.3f}")
print(f"Mediana            : {x.median():.3f}")
print(f"Moda (x.mode())    : {x.mode().tolist()[:5]} ...  ({x.mode().size} valores!)")
print(f"Moda (interpolada) : {moda(x):.3f}")
print(f"Media recortada 5% : {stats.trim_mean(x, 0.05):.3f}")

# %% [markdown]
# 🤔 **¿Por qué `x.mode()` da dos valores raros?** En una variable continua casi ningún valor se repite: aquí solo
# coinciden por casualidad dos parejas de países (Rusia y Hong Kong con 5.477; Argentina y Portugal con 5.929).
# Eso no describe "el valor más habitual".
#
# ### La moda de una variable continua
# Para continuas agrupamos en intervalos (aquí con Sturges: $k \approx 1 + 3{,}322\,\log_{10} n$), buscamos la **clase modal**
# (la de mayor frecuencia) y, dentro de ella, **interpolamos**:
# $$ Mo = L_i + \frac{d_1}{d_1 + d_2}\, a_i, \qquad d_1 = n_i - n_{i-1}, \quad d_2 = n_i - n_{i+1}$$
# Geométricamente es el punto donde se **cortan las rectas que unen en cruz** las esquinas de la barra modal con las de sus vecinas.
# Si la barra de la izquierda es más alta que la de la derecha, la moda se desplaza hacia la izquierda (y al revés).

# %%
frec, bordes = np.histogram(x, bins="sturges")
i = frec.argmax()
L, a = bordes[i], bordes[i + 1] - bordes[i]
n_izq, n_mod, n_der = frec[i - 1], frec[i], frec[i + 1]
Mo = moda(x)
print(f"Clase modal: [{L:.3f}, {L + a:.3f})  con n_i = {n_mod}  (izquierda: {n_izq}, derecha: {n_der})")
print(f"d1 = {n_mod - n_izq},  d2 = {n_mod - n_der}  ->  Mo = {L:.3f} + {n_mod - n_izq}/{(n_mod - n_izq) + (n_mod - n_der)} · {a:.3f} = {Mo:.3f}")

fig, ax = plt.subplots(figsize=(10, 5))
ax.bar(bordes[:-1], frec, width=np.diff(bordes), align="edge", color="#cde2fb", edgecolor="white")
ax.bar(L, n_mod, width=a, align="edge", color=AZUL, alpha=0.6, edgecolor="white", label="clase modal")
# Rectas en cruz dentro de la clase modal:
#   (L, n_mod) -> (L+a, n_der): esquina sup. izquierda de la modal con la altura de la vecina derecha
#   (L, n_izq) -> (L+a, n_mod): altura de la vecina izquierda con la esquina sup. derecha de la modal
ax.plot([L, L + a], [n_mod, n_der], color=NARANJA, lw=2)
ax.plot([L, L + a], [n_izq, n_mod], color=NARANJA, lw=2)
ax.axvline(Mo, color="#333333", ls=":", lw=2, label=f"moda interpolada = {Mo:.3f}")
ax.axvline(L + a / 2, color="#9aa0a6", ls="--", lw=1.5, label=f"punto medio de la clase = {L + a / 2:.3f}")
ax.set_title("Moda de una variable continua: intersección de las rectas en cruz")
ax.set_xlabel("felicidad"); ax.set_ylabel("número de países"); ax.legend(frameon=False, loc="upper left")
plt.show()

# %% [markdown]
# 🤔 ¿Hacia qué lado se ha desplazado la moda respecto al punto medio de la clase? ¿Qué barra vecina "tira" más de ella?
# Cambia `bins="sturges"` por `bins=6` o `bins=15`: **la moda de una continua depende de cómo agrupemos**.

# %%
histograma_con_centros(df["felicidad"], "Felicidad (Ladder score) de 149 países")
plt.xlabel("Puntuación 0-10"); plt.show()

# %% [markdown]
# ### Cuantiles, deciles y percentiles

# %%
print(df["felicidad"].quantile([0.10, 0.25, 0.50, 0.75, 0.90]).round(3))

# %% [markdown]
# ### ¿Y España? Posición relativa: percentil y puntuación tipificada (z)
# $$ z = \frac{x - \bar x}{s} $$
# z indica **a cuántas desviaciones típicas** de la media está un país. Sirve para comparar variables con unidades distintas.

# %%
def ficha_pais(nombre):
    fila = df.loc[df["pais"] == nombre].iloc[0]
    tabla = []
    for v in ["felicidad", "PIB_pc", "apoyo_social", "esperanza_vida", "libertad", "generosidad", "corrupcion"]:
        z = (fila[v] - df[v].mean()) / df[v].std()
        pct = stats.percentileofscore(df[v], fila[v])
        tabla.append({"variable": v, "valor": fila[v], "z": z, "percentil": pct})
    return pd.DataFrame(tabla).set_index("variable")

ficha_pais("Spain")

# %% [markdown]
# 🤔 España está en el percentil 98 de esperanza de vida… pero por debajo de la mitad en libertad percibida. Prueba con tu país favorito:
# `ficha_pais("Finland")`, `ficha_pais("Mexico")`, `ficha_pais("Japan")`...

# %% [markdown]
# ## 4. Medidas de dispersión: ¿son los países parecidos entre sí?

# %%
x = df["felicidad"]
print(f"Rango                 : {x.max() - x.min():.3f}  ({df.loc[x.idxmin(), 'pais']} → {df.loc[x.idxmax(), 'pais']})")
print(f"Rango intercuartílico : {x.quantile(.75) - x.quantile(.25):.3f}")
print(f"Varianza  (n-1)       : {x.var():.3f}     | numpy por defecto (n): {np.var(x):.3f}")
print(f"Desv. típica (n-1)    : {x.std():.3f}     | numpy por defecto (n): {np.std(x):.3f}")
print(f"Coef. de variación    : {100 * x.std() / x.mean():.1f} %")
print(f"MAD                   : {stats.median_abs_deviation(x):.3f}")

# %% [markdown]
# ⚠️ **Trampa clásica:** `pandas` divide entre $n-1$ (cuasivarianza) y `numpy` entre $n$. Con 149 datos la diferencia es pequeña;
# con 5 datos no. Mirad siempre qué fórmula usa la función.
#
# ### Coeficiente de variación: comparar dispersión de variables con unidades distintas
# ¿Qué varía más entre países: el **PIB** (dólares) o la **esperanza de vida** (años)? Comparar desviaciones típicas no tiene sentido; el CV sí.

# %%
cv = (100 * df[cuantitativas].std() / df[cuantitativas].mean().abs()).drop(["generosidad", "log_PIB"]).sort_values()
ax = cv.plot.barh(color=AZUL)
ax.set_title("Coeficiente de variación (%) entre países"); ax.set_xlabel("CV (%)")
for i, v in enumerate(cv): ax.text(v + 1, i, f"{v:.0f}%", va="center")
plt.show()

# %% [markdown]
# 🤔 `generosidad` la hemos quitado: su media es casi 0 (es un residuo, puede ser negativa). **¿Qué le pasa al CV cuando la media se acerca a 0?**

# %% [markdown]
# ## 5. Medidas de forma: asimetría y curtosis
# - Asimetría > 0 → cola a la **derecha**, normalmente media > mediana.
# - Asimetría < 0 → cola a la **izquierda**, normalmente media < mediana.
# - Curtosis (exceso) > 0 → colas más pesadas que la normal.

# %%
fig, axes = plt.subplots(1, 3, figsize=(15, 4))
for ax, v, col in zip(axes, ["PIB_pc", "log_PIB", "esperanza_vida"], [AZUL, VERDE, NARANJA]):
    histograma_con_centros(df[v], f"{v}  (asimetría = {df[v].skew():.2f})", ax=ax, color=col)
plt.tight_layout(); plt.show()

# %% [markdown]
# 🎯 **Fijaos en el truco del logaritmo:** el PIB per cápita es muy asimétrico a la derecha (pocos países muy ricos);
# al tomar logaritmos la distribución se vuelve casi simétrica. Por eso los economistas trabajan con `log_PIB`.

# %% [markdown]
# ## 6. Tabla resumen de TODAS las variables cuantitativas

# %%
tabla = df[cuantitativas].apply(resumen).T
tabla.style.format("{:,.2f}").background_gradient(subset=["asimetria_Fisher"], cmap="RdBu_r", vmin=-2, vmax=2)

# %% [markdown]
# ## 7. Datos anómalos (atípicos)
# **Regla de Tukey** (la del diagrama de caja): es atípico todo lo que esté fuera de
# $[Q_1 - 1.5\,RIC,\; Q_3 + 1.5\,RIC]$.

# %%
fig, axes = plt.subplots(1, 4, figsize=(15, 4))
for ax, v in zip(axes, ["felicidad", "PIB_pc", "apoyo_social", "corrupcion"]):
    sns.boxplot(y=df[v], ax=ax, color=AZUL, width=0.4, fliersize=6)
    ax.set_title(v)
plt.tight_layout(); plt.show()

# %%
for v in ["felicidad", "apoyo_social", "corrupcion", "esperanza_vida"]:
    li, ls = limites_tukey(df[v])
    at = df.loc[(df[v] < li) | (df[v] > ls), ["pais", "region", v]]
    print(f"\n--- {v}: vallas [{li:.2f}, {ls:.2f}] -> {len(at)} atípicos")
    print(at.to_string(index=False))

# %% [markdown]
# 🤔 Mirad `corrupcion`: los "atípicos" son los países nórdicos, Singapur… ¡con **muy poca** corrupción percibida!
# Lo raro en el mundo es no tener corrupción.
#
# Un atípico **no es un error**: Afganistán es realmente el país menos feliz del informe.
# ¿Qué haríais con él si quisierais describir a "un país típico"? ¿Lo quitaríais?
#
# ### Atípicos "relacionales": felicidad que no cuadra con la riqueza
# Ajustamos una recta felicidad ~ log_PIB y miramos los países que más se alejan (residuos).

# %%
pend, ord_, r, *_ = stats.linregress(df["log_PIB"], df["felicidad"])
df["residuo"] = df["felicidad"] - (ord_ + pend * df["log_PIB"])

fig, ax = plt.subplots(figsize=(11, 6))
sns.scatterplot(data=df, x="log_PIB", y="felicidad", color="#9aa0a6", s=40, ax=ax)
xs = np.linspace(df["log_PIB"].min(), df["log_PIB"].max(), 50)
ax.plot(xs, ord_ + pend * xs, color="#333333", lw=2, label=f"recta (r = {r:.2f})")
extremos = pd.concat([df.nlargest(5, "residuo"), df.nsmallest(5, "residuo")])
sns.scatterplot(data=extremos, x="log_PIB", y="felicidad", hue=np.where(extremos["residuo"] > 0, "más feliz de lo esperado", "menos feliz de lo esperado"),
                palette=[VERDE, NARANJA], s=90, ax=ax)
for _, f in extremos.iterrows():
    ax.annotate(f["pais"], (f["log_PIB"], f["felicidad"]), xytext=(5, 4), textcoords="offset points", fontsize=9)
ax.set_title("¿Da el dinero la felicidad? Países que se salen de la tendencia")
ax.legend(frameon=False); plt.show()

# %% [markdown]
# ## 8. 🏆 Comparación por grupos con `groupby`: ¿qué región es más feliz… y más desigual?

# %%
por_region = (df.groupby("region")["felicidad"]
                .agg(n="size", media="mean", mediana="median", desv="std",
                     minimo="min", maximo="max",
                     RIC=lambda s: s.quantile(.75) - s.quantile(.25))
                .assign(CV=lambda t: 100 * t["desv"] / t["media"])
                .sort_values("mediana", ascending=False))
por_region.style.format("{:.2f}").background_gradient(subset=["mediana"], cmap="Blues").background_gradient(subset=["CV"], cmap="Oranges")

# %%
orden = por_region.index
fig, ax = plt.subplots(figsize=(11, 6))
sns.boxplot(data=df, y="region", x="felicidad", order=orden, color="#cde2fb", width=0.6, fliersize=0, ax=ax)
sns.stripplot(data=df, y="region", x="felicidad", order=orden, color=AZUL, size=5, alpha=0.8, ax=ax)
ax.axvline(df["felicidad"].median(), color="#333333", ls="--", lw=1.5, label="mediana mundial")
ax.set_title("Felicidad por región (ordenadas por mediana)"); ax.set_ylabel(""); ax.legend(frameon=False)
plt.show()

# %% [markdown]
# 🤔 **Preguntas:**
# 1. ¿Qué región tiene la **mayor dispersión**? ¿Y la menor? (mira `RIC` y `CV`)
# 2. "North America and ANZ" solo tiene **4 países**. ¿Te fiarías de su media para compararla con África (36 países)?
# 3. ¿En qué región la media y la mediana se separan más? ¿Por qué?

# %% [markdown]
# ### Perfil de cada región en todas las variables (tipificadas)
# Tipificamos cada variable (z) para poder ponerlas en la misma escala y pintamos un mapa de calor.

# %%
vars_perfil = ["felicidad", "log_PIB", "apoyo_social", "esperanza_vida", "libertad", "generosidad", "corrupcion"]
z = (df[vars_perfil] - df[vars_perfil].mean()) / df[vars_perfil].std()
perfil = z.groupby(df["region"]).mean().loc[orden]
plt.figure(figsize=(11, 6))
sns.heatmap(perfil, annot=True, fmt=".1f", cmap="RdBu_r", center=0, vmin=-2, vmax=2, linewidths=2, linecolor="white")
plt.title("Media de las variables tipificadas por región (azul = por debajo, rojo = por encima)")
plt.ylabel(""); plt.show()

# %% [markdown]
# ### ⚠️ La media de los países NO es la media del mundo
# Hemos tratado igual a India (1.400 millones) que a Islandia (370.000). La media de esta tabla es la del
# "país típico", **no la de la persona típica**. Para eso necesitaríamos una **media ponderada** por población.

# %% [markdown]
# ## 9. Dos variables a la vez: covarianza y correlación

# %%
corr = df[vars_perfil].corr()
mask = np.triu(np.ones_like(corr, dtype=bool))
plt.figure(figsize=(8, 6))
sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap="RdBu_r", center=0, vmin=-1, vmax=1, linewidths=2, linecolor="white")
plt.title("Matriz de correlaciones (Pearson)"); plt.show()

# %%
print("Covarianza felicidad–esperanza_vida :", round(df["felicidad"].cov(df["esperanza_vida"]), 3))
print("Covarianza felicidad–log_PIB         :", round(df["felicidad"].cov(df["log_PIB"]), 3))
print("Correlación felicidad–esperanza_vida :", round(df["felicidad"].corr(df["esperanza_vida"]), 3))
print("Correlación felicidad–log_PIB        :", round(df["felicidad"].corr(df["log_PIB"]), 3))

# %% [markdown]
# 🤔 La covarianza con esperanza de vida es mucho mayor que con log_PIB, pero la correlación es menor. **¿Por qué?**
# (pista: unidades). Y recordad: **correlación no implica causalidad**.

# %% [markdown]
# ## 10. ¿Se parece a una normal? Regla empírica vs. desigualdad de Chebyshev
# - Normal: ~68 % de datos en $\bar x \pm s$, ~95 % en $\bar x \pm 2s$, ~99.7 % en $\bar x \pm 3s$.
# - Chebyshev (vale para **cualquier** distribución): al menos $1 - 1/k^2$ en $\bar x \pm ks$.

# %%
def regla_empirica(x):
    x = pd.Series(x).dropna(); m, s = x.mean(), x.std()
    return pd.DataFrame({
        "k": [1, 2, 3],
        "observado_%": [100 * x.between(m - k*s, m + k*s).mean() for k in (1, 2, 3)],
        "normal_%": [68.27, 95.45, 99.73],
        "Chebyshev_min_%": [0, 75, 88.9],
    }).set_index("k")

print("Felicidad:"); print(regla_empirica(df["felicidad"]))
print("\nPIB per cápita (muy asimétrico):"); print(regla_empirica(df["PIB_pc"]))

# %% [markdown]
# ## 🚀 Retos
# 1. Calcula la tabla de `resumen()` **por región** para `esperanza_vida`: `df.groupby("region")["esperanza_vida"].apply(resumen).unstack()`.
# 2. Crea una variable cualitativa ordinal `nivel_felicidad` con `pd.cut` (baja / media / alta) y haz una tabla de contingencia con `region` (`pd.crosstab(..., normalize="index")`).
# 3. ¿Qué país europeo es el más "anómalo" según su residuo? ¿Y el latinoamericano?
# 4. Repite el análisis de atípicos con z-scores ( |z| > 2.5 ). ¿Salen los mismos países que con Tukey?
