# %% [markdown]
# # ⚽ Estadística descriptiva con 17.000 futbolistas de EA Sports FC
#
# **Estadística Descriptiva · 1.º Grado en Ciencia de Datos · UCM** — Prof. Daniel Gómez
#
# Cada fila es un **jugador** del videojuego, con su valoración global (`OVR`), sus seis medias
# (`PAC` ritmo, `SHO` tiro, `PAS` pase, `DRI` regate, `DEF` defensa, `PHY` físico), decenas de atributos
# detallados, y datos como edad, altura, posición, liga, equipo y nacionalidad.
#
# Preguntas que vamos a responder:
# - ¿Cómo es el jugador "típico"? ¿Media, mediana o moda?
# - ¿Qué **liga** es mejor… y cuál es más **igualada**?
# - ¿A qué **edad** alcanza un futbolista su pico?
# - ¿Quién es el jugador más **anómalo** (excepcional) en cada atributo?
# - ¿Por qué algunos histogramas tienen **dos jorobas**?
#
# > 💡 Ejecuta las celdas en orden. Donde veas **🤔**, para y piensa antes de seguir.
#
# **Plan de trabajo (3 sesiones de 2 h):**
# - 🕐 Sesión 1 · Conocer los datos y describir una variable (apartados 1–6)
# - 🕐 Sesión 2 · Atípicos, tipificación y comparación de grupos (7–9)
# - 🕐 Sesión 3 · Dos variables: correlación y regresión (10–12)

# %%
# (el bloque de configuración común se inserta aquí)
#@@COMUN@@

# %% [markdown]
# ---
# # 🕐 Sesión 1 de 3 · Conocer los datos y describir una variable
# **Objetivos:** limpiar el dataset, descubrir problemas de agrupación, tablas de frecuencias, medidas de posición, dispersión y forma.  
# **Apartados:** 1 a 6 · **Duración orientativa:** 2 horas

# %% [markdown]
# ## 1. Carga y limpieza
# El CSV usa `;` como separador. Trae columnas "basura" (`Unnamed: ...`) que vienen de índices guardados al exportar
# y de las celdas vacías tras altura y peso.

# %%
df = pd.read_csv(URL_DATOS + "all_players_dani.csv", sep=";")
print("Dimensiones originales:", df.shape)
df = df.loc[:, ~df.columns.str.startswith("Unnamed")]   # fuera TODAS las columnas Unnamed de una vez
df = df.rename(columns={"Height": "Height_cm", "Weight": "Weight_kg"})
print("Dimensiones tras limpiar:", df.shape)
df.head()

# %%
df.info()

# %%
print("Valores faltantes por columna (solo las que tienen):")
print(df.isna().sum()[lambda s: s > 0])
print("\n¿Jugadores duplicados (mismo nombre, equipo y edad)?", df.duplicated(["Name", "Team", "Age"]).sum())

# %% [markdown]
# ### 🕵️ Primer análisis: ¿cuántos jugadores tiene cada equipo?
# Antes de comparar equipos, conviene saber **cuántos datos tiene cada grupo**. Creamos una variable nueva,
# `plantilla` = número de jugadores por equipo, y la describimos como cualquier otra variable cuantitativa.
# (Ojo: ahora la unidad estadística ya no es el jugador, es el **equipo**.)

# %%
plantilla = df["Team"].value_counts().rename("plantilla")
print("Número de equipos:", plantilla.size)
# Las mismas medidas que para cualquier variable: posición, dispersión y forma
print(plantilla.describe().round(2))
print(f"IQR        : {plantilla.quantile(0.75) - plantilla.quantile(0.25)}")
print(f"CV         : {100 * plantilla.std() / plantilla.mean():.1f} %")
print(f"Asimetría  : {plantilla.skew():.2f}")
print(f"Curtosis   : {plantilla.kurt():.2f}")

# %%
fig, axes = plt.subplots(1, 2, figsize=(15, 4), gridspec_kw={"width_ratios": [3, 1]})
sns.histplot(plantilla, bins=range(0, 72, 2), color=AZUL, ax=axes[0])
axes[0].axvline(plantilla.median(), color="#333333", ls="--", label=f"mediana = {plantilla.median():.0f}")
axes[0].set_title("Jugadores por equipo (agrupando por Team)"); axes[0].set_xlabel("jugadores en la plantilla")
axes[0].legend(frameon=False)
sns.boxplot(y=plantilla, color="#cde2fb", width=0.4, ax=axes[1]); axes[1].set_title("Diagrama de caja")
plt.tight_layout(); plt.show()

# %% [markdown]
# 🤔 La mayoría de equipos tiene entre 22 y 28 jugadores (lo normal en una plantilla)… pero hay una **segunda joroba** entre 45 y 68,
# y la caja marca muchos **atípicos**. ¿Quiénes son?

# %%
# Regla de Tukey: atípico si está fuera de [Q1 - 1.5·IQR , Q3 + 1.5·IQR]
q1, q3 = plantilla.quantile(0.25), plantilla.quantile(0.75)
iqr = q3 - q1
li, ls = q1 - 1.5 * iqr, q3 + 1.5 * iqr
grandes = plantilla[plantilla > ls]
print(f"Vallas de Tukey: [{li:.1f}, {ls:.1f}] -> {len(grandes)} equipos atípicos por arriba")
grandes.head(15).to_frame()

# %% [markdown]
# Everton 68, Liverpool 66, Chelsea 65… ¿Tienen el triple de jugadores que el resto?
#
# ### 🔍 Investigamos: el Everton frente a un equipo "normal" (el Real Madrid)
# Si el Everton fuera simplemente una plantilla grande, sus jugadores deberían parecerse físicamente a los de cualquier otro equipo
# de primera. Comparemos la **altura** y el **peso** de los dos equipos.

# %%
everton = df[df["Team"] == "Everton"]
madrid = df[df["Team"] == "Real Madrid"]

for nombre, eq in [("Everton", everton), ("Real Madrid", madrid)]:
    print(f"\n--- {nombre} ({len(eq)} jugadores) ---")
    print(eq[["Height_cm", "Weight_kg"]].agg(["mean", "median", "std", "min", "max"]).round(1))

# %% [markdown]
# 🤔 Las **medias** se parecen bastante (179 cm frente a 181). Si solo miráramos la media, no veríamos nada raro.
# Pero fíjate en la **desviación típica** y en el **mínimo**: el Everton tiene jugadores de 1,60 m y mucha más dispersión. Dibujemos:

# %%
fig, axes = plt.subplots(1, 2, figsize=(15, 4.5))
for ax, v, etiqueta in [(axes[0], "Height_cm", "Altura (cm)"), (axes[1], "Weight_kg", "Peso (kg)")]:
    bins = range(158, 203, 3) if v == "Height_cm" else range(50, 100, 3)      # mismos intervalos para los dos equipos
    sns.histplot(everton[v], bins=bins, color=NARANJA, alpha=0.5, label="Everton", stat="percent", ax=ax)
    sns.histplot(madrid[v], bins=bins, color=AZUL, alpha=0.5, label="Real Madrid", stat="percent", ax=ax)
    ax.axvline(everton[v].median(), color=NARANJA, ls="--", lw=2)
    ax.axvline(madrid[v].median(), color=AZUL, ls="--", lw=2)
    ax.set_xlabel(etiqueta); ax.legend(frameon=False)
axes[0].set_title("Altura: Everton frente a Real Madrid")
axes[1].set_title("Peso: Everton frente a Real Madrid")
plt.tight_layout(); plt.show()

# %%
fig, ax = plt.subplots(figsize=(9, 4))
sns.boxplot(data=pd.concat([everton.assign(equipo_="Everton"), madrid.assign(equipo_="Real Madrid")]),
            x="Height_cm", y="equipo_", hue="equipo_", palette=[NARANJA, AZUL], legend=False, width=0.5, ax=ax)
sns.stripplot(data=pd.concat([everton.assign(equipo_="Everton"), madrid.assign(equipo_="Real Madrid")]),
              x="Height_cm", y="equipo_", color="#333333", size=4, alpha=0.6, ax=ax)
ax.set_title("Altura de cada jugador"); ax.set_xlabel("Altura (cm)"); ax.set_ylabel("")
plt.show()

# %% [markdown]
# 🎯 El Everton tiene una **cola de jugadores bajos y ligeros** (entre 1,60 y 1,70 m, por debajo de 60 kg) que en el Real Madrid
# apenas existe: allí solo un jugador baja de 1,70 m. Contémoslos:

# %%
for nombre, eq in [("Everton", everton), ("Real Madrid", madrid)]:
    print(f"{nombre:12s}: {(eq['Height_cm'] < 170).sum():2d} de {len(eq)} jugadores miden menos de 1,70 m "
          f"({100 * (eq['Height_cm'] < 170).mean():.0f} %)")

# %% [markdown]
# Además, la desviación típica del Everton es mayor (8,7 cm frente a 7,6) aunque la media sea casi igual.
# Sospecha: **estamos mezclando
# poblaciones distintas**. ¿Cuáles? Miramos en qué liga juega cada jugador del "Everton":

# %%
everton.groupby("League").agg(n=("Name", "size"), altura_media=("Height_cm", "mean"),
                              altura_mediana=("Height_cm", "median"), peso_mediano=("Weight_kg", "median")).round(1)

# %% [markdown]
# 💥 **¡Acabamos de dar con el problema!** Bajo el nombre "Everton" hay **tres equipos distintos**:
# - el Everton masculino (Premier League),
# - el Everton **femenino** (Barclays WSL): ¡14 cm más bajas de media que el masculino! Ellas forman la cola izquierda,
# - el **Everton de Viña del Mar** (Chile, Copa Sudamericana).
#
# Con el Liverpool pasa lo mismo (masculino, femenino y el **Liverpool de Montevideo**, de Uruguay). Compruébalo cambiando
# `"Everton"` por `"Liverpool"` en las celdas anteriores.
#
# Los atípicos no eran equipos enormes: eran **varios equipos con el mismo nombre**. Y lo hemos descubierto
# describiendo dos variables (altura y peso) y comparando su **distribución**, no solo su media.
#
# **Solución:** identificar cada equipo por *nombre + liga* y repetir la descripción.

# %%
df["equipo"] = df["Team"] + " (" + df["League"] + ")"
plantilla2 = df["equipo"].value_counts().rename("plantilla")
comparacion = pd.DataFrame({
    "por Team": plantilla.agg(["count", "mean", "median", "std", "min", "max", "skew", "kurt"]),
    "por equipo + liga": plantilla2.agg(["count", "mean", "median", "std", "min", "max", "skew", "kurt"]),
})
comparacion.round(2)

# %%
fig, ax = plt.subplots(figsize=(12, 4))
sns.histplot(plantilla, bins=range(0, 72, 2), color="#9aa0a6", alpha=0.5, label="por Team", ax=ax)
sns.histplot(plantilla2, bins=range(0, 72, 2), color=AZUL, alpha=0.6, label="por equipo + liga", ax=ax)
ax.set_title("Jugadores por equipo: antes y después de separar homónimos"); ax.set_xlabel("jugadores")
ax.legend(frameon=False); plt.show()

q1_2, q3_2 = plantilla2.quantile(0.25), plantilla2.quantile(0.75)
iqr2 = q3_2 - q1_2
li2, ls2 = q1_2 - 1.5 * iqr2, q3_2 + 1.5 * iqr2
print(f"Atípicos ahora: {((plantilla2 < li2) | (plantilla2 > ls2)).sum()} (antes: {((plantilla < li) | (plantilla > ls)).sum()})")
plantilla2.head(8).to_frame()

# %% [markdown]
# 🤔 La segunda joroba ha desaparecido y la desviación típica ha bajado mucho. Pero **Racing Club** sigue con 55 jugadores en la
# Sudamericana… ¿Cuántos "Racing Club" conoces en Sudamérica? Y los equipos coreanos (K League) tienen 38: ¿error o plantillas más largas?
#
# El dataset incluye **ligas femeninas**. ¿Cómo las encontramos sin leer los 56 nombres? Con estadística:
# la **mediana de altura** por liga separa claramente dos grupos.

# %%
alt_liga = df.groupby("League")["Height_cm"].median().sort_values()
ax = alt_liga.plot.barh(figsize=(9, 13), color=np.where(alt_liga < 174, NARANJA, AZUL))
ax.axvline(174, color="#333333", ls="--")
ax.set_title("Mediana de altura por liga: dos grupos muy separados"); ax.set_xlabel("cm")
plt.tight_layout(); plt.show()

# %%
ligas_femeninas = alt_liga[alt_liga < 174].index.tolist()
print("Ligas femeninas:", ligas_femeninas)
df["sexo"] = np.where(df["League"].isin(ligas_femeninas), "Femenino", "Masculino")
df.groupby("sexo")[["OVR", "Height_cm", "Weight_kg", "Age"]].agg(["size", "mean", "median"]).round(1).T

# %% [markdown]
# 🤔 **¿Por qué las jugadoras tienen un OVR medio 7 puntos mayor?** Mirad qué ligas hay de cada grupo: de hombres están también
# la 2.ª, 3.ª y 4.ª división inglesa, la 3. Liga alemana…; de mujeres, solo las primeras divisiones. **Los grupos no se han
# seleccionado igual**, así que comparar sus medias no compara lo mismo. Además, el juego calibra el `OVR` dentro de cada fútbol.
#
# Altura y peso sí son medidas físicas comparables, y eso afectará a los atípicos (apartado 7).

# %% [markdown]
# ### Tipos de variables
# | Variable | Tipo |
# |---|---|
# | `Name`, `Team`, `Nation`, `League`, `Position`, `Preferred foot` | cualitativas nominales |
# | `Weak foot`, `Skill moves` (1 a 5 estrellas) | cualitativas **ordinales** (o cuantitativas discretas) |
# | `OVR`, `PAC`…`PHY`, atributos | cuantitativas discretas (enteros 0–99) que tratamos como continuas |
# | `Age` | cuantitativa discreta |
# | `Height_cm`, `Weight_kg` | cuantitativas continuas (redondeadas) |
#
# 🤔 *`Rank` es un número… ¿tiene sentido calcular su media?*

# %%
seis = ["PAC", "SHO", "PAS", "DRI", "DEF", "PHY"]
atributos = df.loc[:, "Acceleration":"Aggression"].columns.tolist()
cuantitativas = ["OVR"] + seis + ["Age", "Height_cm", "Weight_kg"]
cualitativas = ["Position", "Preferred foot", "League", "Nation", "Team"]

# %% [markdown]
# ## 2. Variables cualitativas: tablas de frecuencias

# %%
fig, axes = plt.subplots(1, 2, figsize=(15, 6))
df["League"].value_counts().head(20).sort_values().plot.barh(ax=axes[0], color=AZUL)
axes[0].set_title("Top 20 ligas por número de jugadores"); axes[0].set_xlabel("Jugadores")
df["Nation"].value_counts().head(20).sort_values().plot.barh(ax=axes[1], color=NARANJA)
axes[1].set_title("Top 20 nacionalidades por número de jugadores"); axes[1].set_xlabel("Jugadores")
plt.tight_layout(); plt.show()

# %% [markdown]
# ### Variable nominal: `Position`

# %%
tabla_pos = df["Position"].value_counts().to_frame("n_i")
tabla_pos["f_i_%"] = 100 * tabla_pos["n_i"] / len(df)
tabla_pos

# %% [markdown]
# ### Variable ordinal: `Skill moves` — aquí las frecuencias **acumuladas** sí tienen sentido

# %%
tabla_sm = df["Skill moves"].value_counts().sort_index().to_frame("n_i")
tabla_sm["f_i"] = tabla_sm["n_i"] / tabla_sm["n_i"].sum()
tabla_sm["N_i"] = tabla_sm["n_i"].cumsum()
tabla_sm["F_i"] = tabla_sm["f_i"].cumsum()
tabla_sm

# %% [markdown]
# 🤔 ¿Qué porcentaje de jugadores tiene **3 estrellas o menos** en filigranas? ¿Cuál es la **mediana** de `Skill moves`?
# (pista: el primer valor con `F_i ≥ 0.5`)

# %%
zurdos = 100 * (df["Preferred foot"] == "Left").mean()
print(f"Zurdos: {zurdos:.1f} %   (en la población general se estima un ~10 %)")

# %% [markdown]
# ## 3. Medidas de posición de la valoración global `OVR`

# %%
x = df["OVR"]
print(f"Media                 : {x.mean():.2f}")
print(f"Mediana               : {x.median():.2f}")
print(f"Moda                  : {x.mode().tolist()}")
print(f"Media recortada al 5% : {stats.trim_mean(x, 0.05):.2f}   (quita el 5% de cada cola = 10% de los datos)")
print("Cuartiles             :", x.quantile([.25, .5, .75]).tolist())
print("Deciles               :", x.quantile(np.arange(.1, 1, .1)).round(1).tolist())
print(f"Para estar en el top 1 % necesitas OVR ≥ {x.quantile(.99):.0f}")

# %%
x = df["OVR"]
sns.histplot(x, bins=range(40, 100, 2), kde=True, color=AZUL, alpha=0.35)
plt.axvline(x.mean(), color="#333333", ls="-", lw=2, label=f"media = {x.mean():.2f}")
plt.axvline(x.median(), color="#333333", ls="--", lw=2, label=f"mediana = {x.median():.2f}")
plt.axvline(x.mode()[0], color="#333333", ls=":", lw=2, label=f"moda = {x.mode()[0]}")
plt.title("Distribución de la valoración global (OVR)"); plt.xlabel("OVR"); plt.legend(frameon=False)
plt.show()

# %% [markdown]
# ### ¿Cuántas barras pongo en el histograma? El número de clases cambia la historia

# %%
fig, axes = plt.subplots(1, 3, figsize=(16, 4))
for ax, b in zip(axes, [5, 20, 80]):
    sns.histplot(df["OVR"], bins=b, ax=ax, color=AZUL)
    ax.set_title(f"{b} clases")
plt.tight_layout(); plt.show()

# %% [markdown]
# 🤔 Con 5 clases no se ve nada; con 80 aparecen "huecos" porque OVR solo toma valores enteros. Reglas como
# **Sturges** dan un punto de partida:
# $$k \approx 1 + 3{,}322\,\log_{10} n \;=\; 1 + \log_2 n$$
# (son la misma fórmula: $\log_2 n = \log_{10} n / \log_{10} 2 \approx 3{,}322\,\log_{10} n$). Aquí $1 + 3{,}322\,\log_{10}(17737) \approx 15$ clases.
#
# La **densidad estimada (KDE)** es la versión "suavizada" del histograma:

# %%
sns.kdeplot(data=df, x="OVR", fill=True, alpha=0.4, color=AZUL)
plt.title("Densidad estimada de OVR"); plt.ylabel("Densidad"); plt.show()

# %% [markdown]
# ## 4. Medidas de dispersión

# %%
x = df["OVR"]
print(f"Rango        : {x.max() - x.min()}   ({x.min()} a {x.max()})")
print(f"IQR (rango intercuartílico): {x.quantile(.75) - x.quantile(.25)}")
print(f"Varianza     : pandas (n-1) = {x.var():.3f} | numpy (n) = {np.var(x):.3f}")
print(f"Desv. típica : pandas (n-1) = {x.std():.3f} | numpy (n) = {np.std(x):.3f}")
print(f"CV           : {100 * x.std() / x.mean():.1f} %")
print(f"MAD          : {stats.median_abs_deviation(x):.2f}")

# %% [markdown]
# ### ¿Qué varía más entre jugadores: la edad, la altura o el peso?
# Están en unidades distintas (años, cm, kg): comparar desviaciones típicas no tiene sentido → **coeficiente de variación**.

# %%
cv = pd.DataFrame({
    "media": df[["Age", "Height_cm", "Weight_kg", "OVR"]].mean(),
    "desv_tipica": df[["Age", "Height_cm", "Weight_kg", "OVR"]].std(),
})
cv["CV_%"] = 100 * cv["desv_tipica"] / cv["media"]
cv.sort_values("CV_%")

# %% [markdown]
# ## 5. Tabla resumen de las variables cuantitativas
# Con `.agg()` calculamos muchas medidas a la vez para todas las columnas; luego añadimos las que no vienen hechas.

# %%
tabla = df[cuantitativas].agg(["count", "mean", "median", "min", "max", "var", "std", "skew", "kurt"]).T
tabla["Q1"] = df[cuantitativas].quantile(0.25)
tabla["Q3"] = df[cuantitativas].quantile(0.75)
tabla["rango"] = tabla["max"] - tabla["min"]
tabla["IQR"] = tabla["Q3"] - tabla["Q1"]
tabla["CV_%"] = 100 * tabla["std"] / tabla["mean"]
(tabla.style.format("{:,.2f}")
     .background_gradient(subset=["skew"], cmap="RdBu_r", vmin=-1.5, vmax=1.5)
     .background_gradient(subset=["CV_%"], cmap="Oranges"))

# %% [markdown]
# `skew` es la asimetría de Fisher y `kurt` la curtosis (en exceso: 0 = como la normal). Ojo: `var` y `std` de pandas dividen entre $n-1$.

# %% [markdown]
# ## 6. Medidas de forma: ¿por qué hay histogramas con dos jorobas?

# %%
forma = pd.DataFrame({"asimetria": df[atributos].skew(), "curtosis": df[atributos].kurt()}).sort_values("asimetria")
fig, ax = plt.subplots(figsize=(10, 9))
colores = np.where(forma["asimetria"] < 0, AZUL, NARANJA)
ax.barh(forma.index, forma["asimetria"], color=colores)
ax.axvline(0, color="#333333", lw=1)
ax.set_title("Asimetría de cada atributo (azul = cola a la izquierda, naranja = a la derecha)")
plt.tight_layout(); plt.show()

# %%
fig, axes = plt.subplots(2, 3, figsize=(15, 8))
for ax, attr in zip(axes.flat, seis):
    sns.histplot(df[attr], bins=range(0, 101, 4), kde=True, color=AZUL, alpha=0.35, ax=ax)
    ax.axvline(df[attr].mean(), color="#333333", ls="-", lw=2, label=f"media = {df[attr].mean():.1f}")
    ax.axvline(df[attr].median(), color="#333333", ls="--", lw=2, label=f"mediana = {df[attr].median():.1f}")
    ax.set_title(f"{attr}  (asim. = {df[attr].skew():.2f})")
    ax.set_xlabel(""); ax.legend(fontsize=8, frameon=False)
plt.suptitle("Las seis medias principales", fontweight="bold")
plt.tight_layout(); plt.show()

# %% [markdown]
# 🤔 `DEF` (y atributos como `Sliding Tackle` o `Standing Tackle`) tienen **dos jorobas** (distribución bimodal).
# ¿Por qué? Hipótesis: hay dos "poblaciones" mezcladas, **defensas** y **no defensas**. Lo comprobamos separando por grupo:

# %%
df["rol"] = np.select(
    [df["Position"] == "GK",
     df["Position"].isin(["CB", "LB", "RB", "LWB", "RWB"]),
     df["Position"].isin(["CDM", "CM", "CAM", "LM", "RM"])],
    ["Portero", "Defensa", "Centrocampista"], default="Delantero")
orden_rol = ["Portero", "Defensa", "Centrocampista", "Delantero"]
paleta_rol = dict(zip(orden_rol, ["#9aa0a6", AZUL, VERDE, NARANJA]))

fig, axes = plt.subplots(1, 2, figsize=(15, 4))
sns.histplot(df, x="Sliding Tackle", bins=range(0, 101, 3), ax=axes[0], color="#9aa0a6")
axes[0].set_title("Sliding Tackle: todos juntos")
sns.kdeplot(data=df, x="Sliding Tackle", hue="rol", hue_order=orden_rol, palette=paleta_rol,
            common_norm=True, fill=True, alpha=0.25, ax=axes[1], cut=0)
axes[1].set_title("Sliding Tackle: separando por rol")
plt.tight_layout(); plt.show()

# %% [markdown]
# 🎯 **Lección:** una distribución bimodal suele avisar de que estamos mezclando grupos distintos.
# Y en ese caso la media (que cae en el "valle" entre las dos jorobas) **no representa a nadie**.
#
# ### 🕵️ Segundo misterio: ¿los porteros tiran tan bien como los delanteros?

# %%
df.groupby("Position")[seis].mean().round(0).loc[["GK", "CB", "ST"]]

# %% [markdown]
# Un portero con `SHO` = 64 de media, casi como un delantero (66), no tiene sentido futbolístico. Lo que pasa es que en las cartas de portero
# esas seis columnas guardan **otras medias** (estirada, blocaje, saque, reflejos, velocidad, colocación). Es la misma columna con
# **otro significado** según la fila. Por eso, en los análisis de las seis medias **quitamos a los porteros**:

# %%
campo = df[df["Position"] != "GK"]
print(f"DEF media con porteros: {df['DEF'].mean():.2f} | sin porteros: {campo['DEF'].mean():.2f}")
print(f"SHO media con porteros: {df['SHO'].mean():.2f} | sin porteros: {campo['SHO'].mean():.2f}")

# %% [markdown]
# ### 🚀 Retos de la sesión 1
# 1. Haz la tabla de frecuencias de `Weak foot` con frecuencias acumuladas. ¿Cuál es su mediana?
# 2. Calcula media, mediana y moda de `Age` y dibuja su histograma con las tres marcadas (`plt.axvline`). ¿Qué asimetría tiene?
# 3. ¿Qué atributo (de la lista `atributos`) tiene el **mayor** coeficiente de variación? ¿Y el menor? ¿Por qué crees que es así?
# 4. Busca otro atributo con dos jorobas, además de `DEF` y `Sliding Tackle`, y explica qué grupos se mezclan.
#
# ---
# ✅ **Fin de la sesión 1.**

# %% [markdown]
# ---
# # 🕐 Sesión 2 de 3 · Atípicos, tipificación y comparación de grupos
# **Objetivos:** detectar atípicos (Tukey y z), comparar observaciones con z-scores y percentiles, comparar grupos con `groupby`.  
# **Apartados:** 7 a 9 · **Duración orientativa:** 2 horas
# > 💡 Si abres el notebook en una sesión nueva, ejecuta antes todas las celdas anteriores: menú *Entorno de ejecución → Ejecutar las celdas anteriores* (Ctrl+F8).

# %% [markdown]
# ## 7. Datos anómalos

# %%
q1, q3 = df["OVR"].quantile(0.25), df["OVR"].quantile(0.75)
iqr = q3 - q1
li, ls = q1 - 1.5 * iqr, q3 + 1.5 * iqr
print(f"Q1 = {q1}, Q3 = {q3}, IQR = {iqr}")
print(f"Vallas de Tukey para OVR: [{li:.1f}, {ls:.1f}]")
cracks = df[df["OVR"] > ls]
print(f"{len(cracks)} jugadores son 'atípicos por arriba':")
cracks[["Name", "OVR", "Position", "Age", "Team"]].head(20)

# %%
fig, axes = plt.subplots(1, 4, figsize=(16, 4))
for ax, v in zip(axes, ["OVR", "Age", "Height_cm", "Weight_kg"]):
    sns.boxplot(y=df[v], ax=ax, color="#cde2fb", width=0.4)
    ax.set_title(v)
plt.tight_layout(); plt.show()

# %%
for v in ["Age", "Height_cm", "Weight_kg"]:
    print(f"\n--- {v}: extremos ---")
    print(pd.concat([df.nsmallest(3, v), df.nlargest(3, v)])[["Name", v, "Position", "Team"]].to_string(index=False))

# %% [markdown]
# 🤔 **¿Error o crack?** Un atípico no es automáticamente un error. Un portero de 2,06 m es raro pero real;
# una jugadora de 1,49 m es atípica entre **todos** los jugadores… pero ¿lo es dentro de su liga?
# **Un atípico lo es respecto a un grupo de referencia.** Repetimos la regla de Tukey separando por sexo:

# %%
filas = []
for sexo, g in df.groupby("sexo"):
    q1, q3 = g["Height_cm"].quantile(0.25), g["Height_cm"].quantile(0.75)
    li, ls = q1 - 1.5 * (q3 - q1), q3 + 1.5 * (q3 - q1)
    filas.append({"sexo": sexo, "valla_inf": li, "valla_sup": ls,
                  "atipicos_dentro_del_grupo": ((g["Height_cm"] < li) | (g["Height_cm"] > ls)).sum()})
q1, q3 = df["Height_cm"].quantile(0.25), df["Height_cm"].quantile(0.75)
li, ls = q1 - 1.5 * (q3 - q1), q3 + 1.5 * (q3 - q1)
print(f"Todos juntos: vallas [{li:.1f}, {ls:.1f}] -> {((df['Height_cm'] < li) | (df['Height_cm'] > ls)).sum()} atípicos")
pd.DataFrame(filas).set_index("sexo")

# %% [markdown]
# **Antes de borrar un dato, hay que entenderlo.**

# %% [markdown]
# ## 8. Tipificación (z-scores): ¿quién es el más excepcional?
# $$ z = \frac{x - \bar x}{s} $$
# Es "a cuántas desviaciones típicas de la media" está un jugador. Así comparamos atributos con medias y dispersiones distintas.

# %%
Z = (campo[seis] - campo[seis].mean()) / campo[seis].std()   # sin porteros
extremos = pd.DataFrame({
    "jugador": [campo.loc[Z[a].idxmax(), "Name"] for a in seis],
    "valor": [campo.loc[Z[a].idxmax(), a] for a in seis],
    "z_max": [Z[a].max() for a in seis],
}, index=seis)
extremos

# %% [markdown]
# 🤔 Un 97 en ritmo y un 90 en defensa: ¿cuál es **más** excepcional? El que tenga mayor z.

# %% [markdown]
# ### La ficha de un jugador: valor, z y percentil en cada variable
# 👉 Cambia el nombre por tu jugador favorito: `"Pedri"`, `"Lamine Yamal"`, `"Aitana Bonmatí"`…

# %%
jugador = "Kylian Mbappé"
fila = df[df["Name"] == jugador].iloc[0]
print(f"{fila['Name']} · {fila['Position']} · {fila['Team']}")
for v in ["OVR"] + seis + ["Age", "Height_cm"]:
    z = (fila[v] - df[v].mean()) / df[v].std()
    percentil = 100 * (df[v] <= fila[v]).mean()          # % de jugadores con un valor menor o igual
    print(f"{v:10s} valor = {fila[v]:6.1f}   z = {z:+.2f}   percentil = {percentil:5.1f}")

# %% [markdown]
# ## 9. 🏆 Comparación por grupos con `groupby`
# ### 9.1 Por posición

# %%
por_pos = (df.groupby("Position")["OVR"]
             .agg(n="size", media="mean", mediana="median", desv="std",
                  Q1=lambda s: s.quantile(.25), Q3=lambda s: s.quantile(.75), maximo="max")
             .sort_values("mediana", ascending=False))
por_pos.style.format("{:.2f}").background_gradient(subset=["media"], cmap="Blues")

# %%
orden = por_pos.index
fig, ax = plt.subplots(figsize=(12, 5))
sns.boxplot(data=df, x="Position", y="OVR", order=orden, color="#cde2fb", ax=ax)
ax.set_title("OVR por posición (ordenadas por mediana)"); ax.set_xlabel("")
plt.show()

# %% [markdown]
# ### Perfil de cada posición (medias de las seis medias)

# %%
perfil = campo.groupby("Position")[seis].mean().loc[[p for p in orden if p != "GK"]]
plt.figure(figsize=(9, 7))
sns.heatmap(perfil, annot=True, fmt=".0f", cmap="Blues", linewidths=2, linecolor="white")
plt.title("Media de cada atributo por posición (jugadores de campo)"); plt.ylabel(""); plt.show()

# %% [markdown]
# ### 9.2 Por liga: ¿la mejor… y la más igualada?

# %%
por_liga = (df.groupby("League")["OVR"]
              .agg(n="size", media="mean", mediana="median", desv="std",
                   IQR=lambda s: s.quantile(.75) - s.quantile(.25),
                   top=lambda s: (s >= 85).sum())
              .assign(CV=lambda t: 100 * t["desv"] / t["media"])
              .query("n >= 100")
              .sort_values("media", ascending=False))
por_liga.head(15).style.format("{:.2f}").background_gradient(subset=["media"], cmap="Blues").background_gradient(subset=["CV"], cmap="Oranges")

# %%
top10 = por_liga.index[:10]
fig, ax = plt.subplots(figsize=(12, 6))
sns.boxplot(data=df[df["League"].isin(top10)], y="League", x="OVR", order=top10, color="#cde2fb", ax=ax)
ax.axvline(df["OVR"].median(), color="#333333", ls="--", label="mediana global")
ax.set_title("Las 10 ligas con mayor OVR medio"); ax.set_ylabel(""); ax.legend(frameon=False)
plt.show()

# %% [markdown]
# 🤔 1. ¿Qué liga tiene **menor CV**? ¿Significa que es la más "igualada"?
# 2. ¿Hay ligas donde la media y la mediana se separan mucho? ¿Qué te dice eso de sus estrellas?

# %% [markdown]
# ### 9.3 La trampa de los grupos pequeños: ranking de nacionalidades

# %%
fig, axes = plt.subplots(1, 2, figsize=(16, 7))
sin_filtro = df.groupby("Nation")["OVR"].agg(["mean", "size"]).sort_values("mean", ascending=False).head(15)
axes[0].barh(sin_filtro.index[::-1], sin_filtro["mean"][::-1], color="#9aa0a6")
for i, (m, n) in enumerate(zip(sin_filtro["mean"][::-1], sin_filtro["size"][::-1])):
    axes[0].text(m + 0.3, i, f"{m:.1f}  (n={n})", va="center", fontsize=9)
axes[0].set_title("SIN filtrar: top 15 países por OVR medio"); axes[0].set_xlim(50, 90)

con_filtro = df.groupby("Nation")["OVR"].agg(["mean", "size"]).query("size >= 50").sort_values("mean", ascending=False).head(15)
axes[1].barh(con_filtro.index[::-1], con_filtro["mean"][::-1], color=AZUL)
for i, (m, n) in enumerate(zip(con_filtro["mean"][::-1], con_filtro["size"][::-1])):
    axes[1].text(m + 0.3, i, f"{m:.1f}  (n={n})", va="center", fontsize=9)
axes[1].set_title("Con al menos 50 jugadores"); axes[1].set_xlim(50, 90)
plt.tight_layout(); plt.show()

# %% [markdown]
# 🎯 **Lección:** un país con 1 jugador muy bueno "gana" el ranking de medias. Una media calculada con **n = 1** no describe a ningún grupo.
# Siempre que hagáis un `groupby`, **mirad también el tamaño de cada grupo** (`size`).

# %% [markdown]
# ### 9.4 Por equipo: los mejores… y los más desiguales

# %%
por_equipo = (df.groupby("equipo")["OVR"]
                .agg(n="size", media="mean", mediana="median", desv="std", maximo="max", minimo="min",
                     estrellas=lambda s: (s >= 85).sum())
                .query("n >= 18"))
top = por_equipo.sort_values("media", ascending=False).head(20)
fig, ax = plt.subplots(figsize=(11, 8))
eq = top.index[::-1]
ax.hlines(eq, top["minimo"][::-1], top["maximo"][::-1], color="#cde2fb", lw=6, label="rango (mín–máx)")
ax.scatter(top["media"][::-1], eq, color=AZUL, zorder=3, s=60, label="media")
ax.scatter(top["mediana"][::-1], eq, color=NARANJA, zorder=3, s=40, marker="D", label="mediana")
ax.set_title("Top 20 equipos por OVR medio: media, mediana y rango"); ax.set_xlabel("OVR")
ax.legend(frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.08))
plt.tight_layout(); plt.show()

# %%
print("Los 10 equipos más DESIGUALES (mayor desviación típica de OVR):")
por_equipo.sort_values("desv", ascending=False).head(10)

# %% [markdown]
# ### 9.5 ¿A qué edad se alcanza el pico?

# %%
por_edad = df.groupby("Age")["OVR"].agg(n="size", media="mean", mediana="median",
                                         p90=lambda s: s.quantile(.9)).query("n >= 30")
fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(por_edad.index, por_edad["media"], marker="o", color=AZUL, lw=2, label="media")
ax.plot(por_edad.index, por_edad["mediana"], marker="s", color=NARANJA, lw=2, ls="--", label="mediana")
ax.plot(por_edad.index, por_edad["p90"], marker="^", color=VERDE, lw=2, ls=":", label="percentil 90 (los buenos)")
ax.set_xlabel("Edad"); ax.set_ylabel("OVR"); ax.set_title("OVR según la edad (edades con al menos 30 jugadores)")
ax.legend(frameon=False); plt.show()
print("Edad con mayor OVR medio:", por_edad["media"].idxmax())

# %% [markdown]
# 🤔 ¿La curva baja a partir de cierta edad porque los jugadores **empeoran**… o porque solo los muy buenos **siguen jugando**?
# (Esto se llama *sesgo de supervivencia*.)

# %% [markdown]
# ### 9.6 Dos cualitativas: ¿en qué posiciones juegan los zurdos?

# %%
tc = pd.crosstab(df["Position"], df["Preferred foot"], normalize="index").mul(100).sort_values("Left")
ax = tc["Left"].plot.barh(color=AZUL, figsize=(9, 6))
ax.axvline(zurdos, color="#333333", ls="--", label=f"total ({zurdos:.0f}%)")
ax.set_title("% de zurdos en cada posición"); ax.set_xlabel("%"); ax.legend(frameon=False)
plt.show()

# %% [markdown]
# ### 🚀 Retos de la sesión 2
# 1. Repite la tabla de ligas usando la **mediana** para ordenar. ¿Cambia el top 5?
# 2. ¿Qué equipo tiene más jugadores **atípicos por arriba** (según Tukey) en su plantilla?
# 3. Construye el **"once ideal"**: el mejor jugador (mayor OVR) de cada posición con `groupby("Position")["OVR"].idxmax()`.
# 4. ¿Qué equipo **femenino** tiene el OVR medio más alto? ¿Y la liga femenina más igualada?
# 5. ¿Qué nacionalidad (con n ≥ 50) es la más **homogénea** en OVR? ¿Y la más desigual?
# 6. Elige tú una pregunta y respóndela con un `groupby` y un gráfico. ¡La mejor se enseña en clase!
#
# ---
# ✅ **Fin de la sesión 2.**

# %% [markdown]
# ---
# # 🕐 Sesión 3 de 3 · Dos variables: correlación y regresión
# **Objetivos:** covarianza y correlación, recta de regresión, modelos potencial y exponencial, residuos y predicción.  
# **Apartados:** 10 a 12 · **Duración orientativa:** 2 horas
# > 💡 Si abres el notebook en una sesión nueva, ejecuta antes todas las celdas anteriores: menú *Entorno de ejecución → Ejecutar las celdas anteriores* (Ctrl+F8).

# %% [markdown]
# ## 10. Dos variables cuantitativas: covarianza y correlación

# %%
fig, axes = plt.subplots(1, 2, figsize=(15, 5))
sns.scatterplot(data=df.sample(min(3000, len(df)), random_state=1), x="Height_cm", y="Weight_kg",
                hue="rol", hue_order=orden_rol, palette=paleta_rol, s=15, alpha=0.6, ax=axes[0])
axes[0].set_title(f"Altura vs peso (r = {df['Height_cm'].corr(df['Weight_kg']):.2f})")
sns.scatterplot(data=df.sample(min(3000, len(df)), random_state=1), x="PAC", y="DEF",
                hue="rol", hue_order=orden_rol, palette=paleta_rol, s=15, alpha=0.6, ax=axes[1])
axes[1].set_title(f"Ritmo vs defensa (r = {df['PAC'].corr(df['DEF']):.2f})")
plt.tight_layout(); plt.show()

# %%
corr = df[["OVR"] + seis + ["Age", "Height_cm", "Weight_kg"]].corr()
mask = np.triu(np.ones_like(corr, dtype=bool))
plt.figure(figsize=(9, 7))
sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap="RdBu_r", center=0, vmin=-1, vmax=1, linewidths=2, linecolor="white")
plt.title("Matriz de correlaciones"); plt.show()

# %% [markdown]
# ## 11. 📈 Regresión: ¿podemos predecir el peso a partir de la altura?
# Vamos a ajustar tres modelos por **mínimos cuadrados** para explicar el peso ($y$) a partir de la altura ($x$):
#
# | Modelo | Ecuación | Cómo se ajusta |
# |---|---|---|
# | Lineal | $y = a + b\,x$ | directamente |
# | Potencial | $y = a\,x^{b}$ | tomando logaritmos: $\ln y = \ln a + b\,\ln x$ |
# | Exponencial | $y = a\,e^{b x}$ | tomando logaritmos: $\ln y = \ln a + b\,x$ |
#
# ### 11.1 La recta de regresión, paso a paso
# $$ b = \frac{S_{xy}}{S_x^2}, \qquad a = \bar y - b\,\bar x, \qquad R^2 = r^2 = \left(\frac{S_{xy}}{S_x S_y}\right)^2 $$

# %%
x, y = df["Height_cm"], df["Weight_kg"]
media_x, media_y = x.mean(), y.mean()
Sx2 = ((x - media_x) ** 2).mean()                  # varianza de x (dividiendo entre n)
Sy2 = ((y - media_y) ** 2).mean()
Sxy = ((x - media_x) * (y - media_y)).mean()        # covarianza
b = Sxy / Sx2
a = media_y - b * media_x
r = Sxy / np.sqrt(Sx2 * Sy2)
print(f"media altura = {media_x:.2f} cm   media peso = {media_y:.2f} kg")
print(f"S_x^2 = {Sx2:.3f}   S_y^2 = {Sy2:.3f}   S_xy = {Sxy:.3f}")
print(f"b = S_xy / S_x^2 = {b:.4f} kg por cada cm")
print(f"a = media_y - b·media_x = {a:.3f}")
print(f"Recta de y sobre x:  peso = {a:.2f} + {b:.4f}·altura")
print(f"r = {r:.4f}   ->   R^2 = {r**2:.4f}  (la altura explica el {100*r**2:.1f} % de la variabilidad del peso)")

# %% [markdown]
# 🤔 **Interpretación:** por cada centímetro más de altura, el peso aumenta de media unos `b` kg. ¿Y qué significa `a`?
# (Sería el peso de un jugador de 0 cm… **no tiene sentido**: fuera del rango de los datos la recta no vale.)
#
# ### 11.2 Las dos rectas de regresión
# La recta de **y sobre x** (predecir el peso con la altura) **no es la misma** que la de **x sobre y** (predecir la altura con el peso).
# Las dos se cortan en el **centro de gravedad** $(\bar x, \bar y)$, y cuanto más se parecen, mayor es $|r|$.

# %%
# Recta de x sobre y: se intercambian los papeles -> b' = S_xy / S_y^2
b_xy = Sxy / Sy2
a_xy = media_x - b_xy * media_y                    # altura = a' + b'·peso
print(f"Recta de x sobre y:  altura = {a_xy:.2f} + {b_xy:.4f}·peso")
print(f"Comprobación: b · b' = {b * b_xy:.4f} = r^2 = {r**2:.4f}")

fig, ax = plt.subplots(figsize=(9, 6))
m = df.sample(3000, random_state=1)
ax.scatter(m["Height_cm"], m["Weight_kg"], s=10, alpha=0.3, color="#9aa0a6")
xs = np.linspace(x.min(), x.max(), 100)
ax.plot(xs, a + b * xs, color=AZUL, lw=2.5, label="y sobre x (peso según altura)")
ys = np.linspace(y.min(), y.max(), 100)
ax.plot(a_xy + b_xy * ys, ys, color=NARANJA, lw=2.5, label="x sobre y (altura según peso)")
ax.scatter([media_x], [media_y], s=120, color="#333333", zorder=5, label="centro de gravedad")
ax.set_xlabel("Altura (cm)"); ax.set_ylabel("Peso (kg)"); ax.set_title("Las dos rectas de regresión")
ax.legend(frameon=False); plt.show()

# %% [markdown]
# ### 11.3 Modelos potencial y exponencial: linealizar con logaritmos
# Si $y = a\,x^b$, entonces $\ln y = \ln a + b \ln x$: **en escala log-log los puntos deberían quedar en una recta**.
# Si $y = a\,e^{bx}$, entonces $\ln y = \ln a + b\,x$: **en escala semilogarítmica** deberían quedar en una recta.
# Así que ajustar estos modelos es simplemente ajustar una recta… a los datos transformados.

# %%
fig, axes = plt.subplots(1, 3, figsize=(16, 4.5))
axes[0].scatter(m["Height_cm"], m["Weight_kg"], s=8, alpha=0.3, color=AZUL); axes[0].set_title("Original: x, y")
axes[1].scatter(np.log(m["Height_cm"]), np.log(m["Weight_kg"]), s=8, alpha=0.3, color=NARANJA); axes[1].set_title("Log-log: ln x, ln y  (potencial)")
axes[2].scatter(m["Height_cm"], np.log(m["Weight_kg"]), s=8, alpha=0.3, color=VERDE); axes[2].set_title("Semilog: x, ln y  (exponencial)")
plt.tight_layout(); plt.show()

# %%
x, y = df["Height_cm"], df["Weight_kg"]

# --- Lineal: y = a + b·x  (ya calculada arriba)
pred_lin = a + b * x

# --- Potencial: ln y = A + b_pot·ln x  ->  y = e^A · x^b_pot
lx, ly = np.log(x), np.log(y)
b_pot = ((lx - lx.mean()) * (ly - ly.mean())).mean() / ((lx - lx.mean()) ** 2).mean()
a_pot = np.exp(ly.mean() - b_pot * lx.mean())
pred_pot = a_pot * x ** b_pot

# --- Exponencial: ln y = A + b_exp·x  ->  y = e^A · e^(b_exp·x)
b_exp = ((x - x.mean()) * (ly - ly.mean())).mean() / ((x - x.mean()) ** 2).mean()
a_exp = np.exp(ly.mean() - b_exp * x.mean())
pred_exp = a_exp * np.exp(b_exp * x)

# --- R² en la escala original: 1 - (suma de residuos²) / (suma de (y - media)²)
SC_total = ((y - y.mean()) ** 2).sum()
print(f"Lineal      : peso = {a:.3f} + {b:.4f}·altura          R² = {1 - ((y - pred_lin) ** 2).sum() / SC_total:.4f}")
print(f"Potencial   : peso = {a_pot:.6f}·altura^{b_pot:.4f}     R² = {1 - ((y - pred_pot) ** 2).sum() / SC_total:.4f}")
print(f"Exponencial : peso = {a_exp:.4f}·e^({b_exp:.5f}·altura)  R² = {1 - ((y - pred_exp) ** 2).sum() / SC_total:.4f}")

# %%
xs = np.linspace(x.min(), x.max(), 300)
plt.figure(figsize=(10, 5))
plt.scatter(m["Height_cm"], m["Weight_kg"], s=10, alpha=0.3, color="#9aa0a6")
plt.plot(xs, a + b * xs, color=AZUL, lw=2.5, label="lineal")
plt.plot(xs, a_pot * xs ** b_pot, color=NARANJA, lw=2.5, label="potencial")
plt.plot(xs, a_exp * np.exp(b_exp * xs), color=VERDE, lw=2.5, label="exponencial")
plt.xlabel("Altura (cm)"); plt.ylabel("Peso (kg)"); plt.title("Peso según la altura: tres modelos")
plt.legend(frameon=False); plt.show()

# %% [markdown]
# 🎯 **¡El exponente del modelo potencial sale cerca de 2!** El **índice de masa corporal** (IMC = peso / altura²) da por hecho que
# el peso crece con el **cuadrado** de la altura. Los datos dicen algo parecido. (Si el cuerpo creciera igual en las tres dimensiones,
# el exponente sería 3.)
#
# 🤔 Los tres modelos tienen un $R^2$ casi idéntico. En el rango de alturas de los futbolistas (150–206 cm) las tres curvas son
# prácticamente rectas: **cuando los datos cubren un rango estrecho, la forma del modelo importa poco**.
#
# ### 11.4 Residuos: ¿qué queda sin explicar?
# Residuo $e_i = y_i - \hat y_i$. Si el modelo es bueno, los residuos no deberían mostrar ningún patrón.

# %%
df["residuo_peso"] = df["Weight_kg"] - (a + b * df["Height_cm"])
fig, axes = plt.subplots(1, 2, figsize=(15, 4))
mm = df.sample(3000, random_state=1)
axes[0].scatter(mm["Height_cm"], mm["residuo_peso"], s=8, alpha=0.3, color=AZUL)
axes[0].axhline(0, color="#333333"); axes[0].set_title("Residuos frente a la altura"); axes[0].set_xlabel("Altura (cm)")
sns.histplot(df["residuo_peso"], bins=40, ax=axes[1], color=AZUL); axes[1].set_title("Distribución de los residuos")
plt.tight_layout(); plt.show()
print(f"Media de los residuos: {df['residuo_peso'].mean():.2e} (siempre 0 en mínimos cuadrados)")
print(f"Varianza residual: {df['residuo_peso'].var(ddof=0):.3f} = S_y^2·(1 - R^2) = {Sy2 * (1 - r**2):.3f}")
print("\nLos 5 jugadores más 'pesados para su altura':")
print(df.nlargest(5, "residuo_peso")[["Name", "Height_cm", "Weight_kg", "residuo_peso", "Position"]].to_string(index=False))

# %% [markdown]
# ### 11.5 Predecir (con cuidado)

# %%
for altura in [170, 190, 230]:
    print(f"Altura {altura} cm -> lineal: {a + b * altura:.1f} kg | "
          f"potencial: {a_pot * altura ** b_pot:.1f} kg | exponencial: {a_exp * np.exp(b_exp * altura):.1f} kg")

# %% [markdown]
# ⚠️ Para 230 cm los modelos ya no coinciden: estamos **extrapolando** fuera del rango observado (149–206 cm).
# Ningún modelo garantiza nada fuera de los datos con los que se ajustó.

# %% [markdown]
# ## 12. ¿Regla empírica o Chebyshev?

# %%
m, s = df["OVR"].mean(), df["OVR"].std()
pd.DataFrame({
    "observado_%": [100 * df["OVR"].between(m - k*s, m + k*s).mean() for k in (1, 2, 3)],
    "si_fuera_normal_%": [68.27, 95.45, 99.73],
    "Chebyshev_minimo_%": [0, 75, 88.9],
}, index=pd.Index([1, 2, 3], name="k (desviaciones)"))

# %% [markdown]
# ### 🚀 Retos de la sesión 3
# 1. Repite la regresión potencial peso ~ altura **solo con hombres** y **solo con mujeres**. ¿Sale el mismo exponente que con todos juntos? ¿Por qué?
# 2. Ajusta los tres modelos para `Sprint Speed` frente a `Acceleration` (copia y adapta las celdas del apartado 11.3). ¿Cuál gana?
# 3. ¿Qué pareja de las seis medias (`PAC`…`PHY`) tiene la correlación más alta en los jugadores de campo? Calcula su recta de regresión e interpreta la pendiente.
# 4. Calcula las dos rectas de regresión de `OVR` y `Reactions`. ¿Cuánto vale el producto de sus pendientes? ¿Por qué?
#
# ---
# 🏁 **Fin del notebook.**

