# %% [markdown]
# # 🎵 ¿Qué hace que una canción suene a *rap*, a *clásica* o a *country*? Estadística descriptiva con 50.000 canciones de Spotify
#
# **Estadística Descriptiva · 1.º Grado en Ciencia de Datos · UCM**
#
# Cada fila es una **canción** con las variables de audio que calcula Spotify (bailabilidad, energía, volumen, tempo…)
# y su **género**. Hay 10 géneros con 5.000 canciones cada uno.
#
# Este dataset es **sucio a propósito** (como los de verdad): tiene filas vacías, interrogantes en vez de números,
# duraciones de −1 ms, artistas llamados `empty_field`… Antes de calcular una sola media hay que **limpiar**.
#
# Preguntas que vamos a responder:
# - ¿Qué género es el más **bailable**? ¿Y el más **popular**? ¿Media o mediana?
# - ¿Por qué la media de popularidad de la clásica está **por debajo** de su mediana?
# - ¿Existen canciones de **80 minutos**? (spoiler: sí, pero no son canciones)
# - ¿Rap y Hip-Hop son, estadísticamente, el mismo género?

# %%
# (el bloque de configuración común se inserta aquí)
#@@COMUN@@

# %% [markdown]
# ## 1. Primer vistazo (y primeros sustos)

# %%
df = cargar("music_genre.csv")
print("Dimensiones:", df.shape)
df.head()

# %%
df.info()

# %% [markdown]
# 🤔 **Detectives de datos.** Mirad la salida de `info()`:
# - `tempo` es una variable numérica… ¿por qué pandas la ha leído como **texto** (`object`/`str`)?
# - Hay 50.005 filas pero solo 50.000 valores no nulos: ¿qué pasa con las otras 5?

# %%
print("Filas completamente vacías:", df.isna().all(axis=1).sum())
print("Valores de tempo que no son números:", df.loc[pd.to_numeric(df["tempo"], errors="coerce").isna() & df["tempo"].notna(), "tempo"].unique())
print("Duraciones negativas:", (df["duration_ms"] < 0).sum(), "→ valores:", df.loc[df["duration_ms"] < 0, "duration_ms"].unique())
print("Artistas 'empty_field':", (df["artist_name"] == "empty_field").sum())

# %% [markdown]
# ## 2. Limpieza: los datos faltantes disfrazados
# `?` y `-1` son **códigos de dato faltante**. Si los dejamos, `-1` entraría en la media de duración y la estropearía.
# Los convertimos en `NaN`, que pandas ignora automáticamente al calcular medias, medianas, etc.

# %%
df = df.dropna(how="all")                                        # quitamos las 5 filas vacías
df["tempo"] = pd.to_numeric(df["tempo"].replace("?", np.nan))     # '?' -> NaN y a número
df["duracion_min"] = df["duration_ms"].replace(-1, np.nan) / 60000  # -1 -> NaN y a minutos
df["artist_name"] = df["artist_name"].replace("empty_field", np.nan)
df = df.drop(columns=["instance_id", "obtained_date", "duration_ms"])

print(df.shape)
df.isna().sum()[lambda s: s > 0]

# %% [markdown]
# ### ¿Cuánto cambia la media si NO limpiamos?

# %%
crudo = cargar("music_genre.csv").dropna(how="all")
print(f"Duración media SIN limpiar : {crudo['duration_ms'].mean() / 60000:.3f} min")
print(f"Duración media limpiando   : {df['duracion_min'].mean():.3f} min")
print(f"Mediana SIN limpiar        : {crudo['duration_ms'].median() / 60000:.3f} min")
print(f"Mediana limpiando          : {df['duracion_min'].median():.3f} min")

# %% [markdown]
# 🤔 ¿Cuál de las dos medidas se ha visto más afectada por los `-1`? ¿Por qué la mediana es más **robusta**?

# %% [markdown]
# ### Variables del dataset
# | Variable | Tipo | Qué mide |
# |---|---|---|
# | `music_genre` | cualitativa nominal | género (10 categorías) |
# | `key` | cualitativa nominal | tonalidad (C, C#, D…) |
# | `mode` | cualitativa dicotómica | Major / Minor |
# | `popularity` | cuantitativa discreta (0–100) | popularidad en Spotify |
# | `danceability`, `energy`, `valence`, `acousticness`, `instrumentalness`, `speechiness`, `liveness` | cuantitativas continuas (0–1) | rasgos de audio |
# | `loudness` | continua (dB, negativa) | volumen medio |
# | `tempo` | continua (pulsaciones por minuto) | velocidad |
# | `duracion_min` | continua | duración |

# %%
cuantitativas = ["popularity", "danceability", "energy", "valence", "acousticness", "instrumentalness",
                 "speechiness", "liveness", "loudness", "tempo", "duracion_min"]

# %% [markdown]
# ## 3. Variables cualitativas: tonalidad y modo

# %%
frec = df["key"].value_counts().to_frame("n_i")
frec["f_i_%"] = 100 * frec["n_i"] / frec["n_i"].sum()
ax = frec["n_i"].sort_values().plot.barh(color=AZUL, figsize=(8, 5))
ax.set_title("¿En qué tonalidad están las canciones?"); ax.set_xlabel("Número de canciones")
plt.show()
print("Moda de key:", df["key"].mode()[0], " | moda de mode:", df["mode"].mode()[0])

# %% [markdown]
# ### Tabla de contingencia: ¿qué géneros usan más el modo **menor** (sonido "triste")?

# %%
tabla_modo = pd.crosstab(df["music_genre"], df["mode"], normalize="index").mul(100).sort_values("Minor")
ax = tabla_modo.plot.barh(stacked=True, color=[AZUL, NARANJA], figsize=(9, 5), width=0.75, edgecolor="white")
ax.set_title("% de canciones en modo mayor / menor por género"); ax.set_xlabel("%"); ax.set_ylabel("")
ax.legend(title="", frameon=False, ncol=2, loc="lower center", bbox_to_anchor=(0.5, 1.02))
ax.set_title("% de canciones en modo mayor / menor por género", pad=28)
for i, v in enumerate(tabla_modo["Minor"]):
    ax.text(100 - v + 1, i, f"{v:.0f}%", va="center", color="white", fontweight="bold")
plt.show()

# %% [markdown]
# ## 4. Medidas de posición de una variable: **popularidad**

# %%
x = df["popularity"]
print(f"Media              : {x.mean():.2f}")
print(f"Mediana            : {x.median():.2f}")
print(f"Moda               : {x.mode().tolist()}")
print(f"Media recortada 5% : {stats.trim_mean(x, 0.05):.2f}")
print("Cuartiles:", x.quantile([.25, .5, .75]).tolist())
print("Percentil 99 (el 1 % más popular empieza en):", x.quantile(.99))

# %%
histograma_con_centros(df["popularity"], "Popularidad de 50.000 canciones", bins=range(0, 101, 2))
plt.xlabel("popularity (0-100)"); plt.show()

# %% [markdown]
# 🤔 ¿Ves el **pico en 0**? ¿Son canciones que nadie escucha… o un dato faltante disfrazado? Ahora lo investigamos por género.

# %% [markdown]
# ## 5. Dispersión y forma: todas las variables de un vistazo

# %%
fig, axes = plt.subplots(3, 4, figsize=(16, 10))
for ax, v in zip(axes.flat, cuantitativas):
    sns.histplot(df[v], bins=40, ax=ax, color=AZUL, alpha=0.6)
    ax.set_title(f"{v}\nasimetría = {df[v].skew():.2f}", fontsize=10)
    ax.set_xlabel(""); ax.set_ylabel("")
axes.flat[-1].axis("off")
plt.suptitle("Distribuciones: simétricas, asimétricas, bimodales, en forma de J…", fontweight="bold")
plt.tight_layout(); plt.show()

# %% [markdown]
# 🎯 **Zoo de formas:**
# - `speechiness`, `liveness`, `instrumentalness`: asimetría **positiva** fuerte (en forma de J): casi todo cerca de 0 y una cola larga.
# - `loudness`: asimetría **negativa** (cola a la izquierda: las canciones muy bajitas, clásica sobre todo).
# - `instrumentalness` y `acousticness`: **bimodales** (dos picos). ¿Qué crees que hay en cada pico?
# - `duracion_min`: asimetría enorme por unas pocas "canciones" larguísimas.

# %%
tabla = df[cuantitativas].apply(resumen).T
(tabla.style.format("{:,.3f}")
     .background_gradient(subset=["asimetria_Fisher"], cmap="RdBu_r", vmin=-3, vmax=3)
     .background_gradient(subset=["n_atipicos_Tukey"], cmap="Oranges"))

# %% [markdown]
# 🤔 Comparad `media` y `mediana` en `instrumentalness`: 0.18 frente a casi 0. **¿Qué medida describe mejor una canción "típica"?**
# Y en `speechiness`, ¿qué os dice que la `MAD` sea tan pequeña comparada con la desviación típica?

# %% [markdown]
# ## 6. Atípicos: ¿canciones de 80 minutos?

# %%
li, ls = limites_tukey(df["duracion_min"])
atip = df[df["duracion_min"] > ls]
print(f"Vallas de Tukey: [{li:.2f}, {ls:.2f}] minutos -> {len(atip)} atípicos por arriba ({100*len(atip)/df['duracion_min'].notna().sum():.1f} %)")
df.nlargest(8, "duracion_min")[["artist_name", "track_name", "music_genre", "duracion_min"]]

# %% [markdown]
# Los récords son **mixes y mixtapes**, no canciones. Atípico ≠ error, pero aquí sí cabe preguntarse si deben estar en el análisis.

# %%
fig, axes = plt.subplots(1, 2, figsize=(14, 4))
sns.boxplot(x=df["duracion_min"], ax=axes[0], color="#cde2fb")
axes[0].set_title("Duración (todas)")
sns.boxplot(x=df.loc[df["duracion_min"] < 15, "duracion_min"], ax=axes[1], color="#cde2fb")
axes[1].set_title("Duración (< 15 min, para ver la caja)")
plt.tight_layout(); plt.show()

# %% [markdown]
# ### Tukey vs. z-score
# Con colas tan largas, la desviación típica se "infla" por los propios atípicos y la regla |z| > 3 detecta **menos**.

# %%
comparacion = []
for v in ["duracion_min", "speechiness", "liveness", "loudness", "tempo"]:
    s = df[v].dropna()
    li, ls = limites_tukey(s)
    z = (s - s.mean()) / s.std()
    comparacion.append({"variable": v, "Tukey_1.5IQR": ((s < li) | (s > ls)).sum(), "|z|>3": (z.abs() > 3).sum()})
pd.DataFrame(comparacion).set_index("variable")

# %% [markdown]
# ## 7. 🏆 Comparación por géneros con `groupby`

# %%
pop = (df.groupby("music_genre")["popularity"]
         .agg(media="mean", mediana="median", desv="std",
              Q1=lambda s: s.quantile(.25), Q3=lambda s: s.quantile(.75),
              ceros=lambda s: (s == 0).sum(), asimetria="skew")
         .sort_values("mediana", ascending=False))
pop["media_menos_mediana"] = pop["media"] - pop["mediana"]
pop.style.format("{:.2f}").background_gradient(subset=["mediana"], cmap="Blues").background_gradient(subset=["ceros"], cmap="Oranges")

# %% [markdown]
# 🔍 **¡La clásica es el único género con media < mediana!** Tiene más de 500 canciones con popularidad 0 que tiran de la media hacia abajo
# (asimetría negativa). Una sola tabla de `groupby` y ya hemos encontrado algo raro en los datos.

# %%
orden = df.groupby("music_genre")["popularity"].median().sort_values(ascending=False).index
fig, ax = plt.subplots(figsize=(12, 5))
sns.violinplot(data=df, x="music_genre", y="popularity", order=orden, color="#cde2fb", inner="quart", cut=0, ax=ax)
ax.set_title("Popularidad por género (violín: forma completa + cuartiles)"); ax.set_xlabel("")
plt.show()

# %% [markdown]
# ### Perfil sonoro de cada género (medianas)

# %%
rasgos = ["danceability", "energy", "valence", "acousticness", "instrumentalness", "speechiness", "liveness"]
perfil = df.groupby("music_genre")[rasgos].median().sort_values("energy")
plt.figure(figsize=(11, 6))
sns.heatmap(perfil, annot=True, fmt=".2f", cmap="Blues", vmin=0, vmax=1, linewidths=2, linecolor="white")
plt.title("Mediana de cada rasgo de audio por género"); plt.ylabel(""); plt.show()

# %% [markdown]
# 🤔 Con esta tabla, ¿podrías **adivinar el género** de una canción sabiendo solo su `energy` y su `instrumentalness`? (Esto, en segundo, se llamará *clasificación*.)

# %% [markdown]
# ### ¿Rap y Hip-Hop son el mismo género?

# %%
fig, axes = plt.subplots(1, 4, figsize=(16, 4))
for ax, v in zip(axes, ["danceability", "speechiness", "energy", "popularity"]):
    for g, c in [("Rap", AZUL), ("Hip-Hop", NARANJA), ("Classical", "#9aa0a6")]:
        sns.kdeplot(df.loc[df["music_genre"] == g, v], ax=ax, label=g, color=c, fill=True, alpha=0.15, cut=0)
    ax.set_title(v); ax.set_ylabel("")
axes[0].legend(frameon=False)
plt.suptitle("Rap vs Hip-Hop (y Clásica como referencia)", fontweight="bold")
plt.tight_layout(); plt.show()
df[df["music_genre"].isin(["Rap", "Hip-Hop"])].groupby("music_genre")[rasgos + ["popularity"]].agg(["mean", "median"]).round(3).T

# %% [markdown]
# ### ¿Qué género es más **homogéneo**? Dispersión por grupo

# %%
disp = df.groupby("music_genre")[["danceability", "energy", "tempo"]].agg(lambda s: 100 * s.std() / s.mean()).round(1)
disp.columns = [f"CV_{c}_%" for c in disp.columns]
disp.sort_values("CV_energy_%").style.background_gradient(cmap="Oranges")

# %% [markdown]
# ## 8. Dos variables cuantitativas: energía, volumen y acústica

# %%
muestra = df.sample(3000, random_state=1)
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
sns.scatterplot(data=muestra, x="energy", y="loudness", s=12, alpha=0.4, color=AZUL, ax=axes[0])
axes[0].set_title(f"energy vs loudness  (r = {df['energy'].corr(df['loudness']):.2f})")
sns.scatterplot(data=muestra, x="acousticness", y="energy", s=12, alpha=0.4, color=NARANJA, ax=axes[1])
axes[1].set_title(f"acousticness vs energy  (r = {df['acousticness'].corr(df['energy']):.2f})")
plt.tight_layout(); plt.show()

# %%
corr = df[cuantitativas].corr()
mask = np.triu(np.ones_like(corr, dtype=bool))
plt.figure(figsize=(10, 8))
sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap="RdBu_r", center=0, vmin=-1, vmax=1, linewidths=1.5, linecolor="white")
plt.title("Correlaciones entre rasgos de audio"); plt.show()

# %% [markdown]
# ## 9. Calidad de datos: duplicados
# Una misma canción puede aparecer **varias veces** (y en géneros distintos). ¿Cuántas?

# %%
claves = df.dropna(subset=["artist_name"])
dup = claves[claves.duplicated(["artist_name", "track_name"], keep=False)]
print("Filas con canción repetida:", len(dup))
generos_por_cancion = dup.groupby(["artist_name", "track_name"])["music_genre"].nunique()
print("Canciones repetidas en MÁS DE UN género:", (generos_por_cancion > 1).sum())
pd.crosstab(dup["music_genre"], "repeticiones").sort_values("repeticiones", ascending=False).T

# %% [markdown]
# 🤔 Si una canción está a la vez en *Rap* y en *Hip-Hop*, ¿qué hace eso con las comparaciones del apartado 7?

# %% [markdown]
# ## 🚀 Retos
# 1. ¿Qué **artista** con al menos 20 canciones tiene la mayor popularidad mediana? (`groupby("artist_name")` + `filter` o `agg` con `size`).
# 2. Repite la tabla de popularidad por género **quitando las popularidades 0**. ¿Cambia el ranking? ¿Cambia la media de la clásica?
# 3. Crea una variable `tempo_cat` con `pd.cut` (lento < 90, medio 90-130, rápido > 130) y cruza con el género. ¿Qué género es el más rápido?
# 4. Calcula la tonalidad **moda** de cada género (`groupby(...)["key"].agg(lambda s: s.mode()[0])`).
# 5. Busca la canción más "anómala" del dataset: la que tenga la mayor suma de |z| en todos los rasgos.
