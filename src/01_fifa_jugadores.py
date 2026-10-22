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

# %%
# (el bloque de configuración común se inserta aquí)
#@@COMUN@@

# %% [markdown]
# ## 1. Carga y limpieza
# El CSV usa `;` como separador. Trae columnas "basura" (`Unnamed: ...`) que vienen de índices guardados al exportar
# y de las celdas vacías tras altura y peso.

# %%
df = cargar("all_players_dani.csv", sep=";")
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
# ### 🕵️ Primer misterio: ¿por qué el Liverpool tiene 66 jugadores?

# %%
print("Jugadores con Team == 'Liverpool':", (df["Team"] == "Liverpool").sum())
df[df["Team"] == "Liverpool"].groupby("League").agg(n=("Name", "size"), altura_mediana=("Height_cm", "median"))

# %% [markdown]
# Bajo el nombre "Liverpool" hay **tres equipos distintos**: el masculino (Premier League), el **femenino** (Barclays WSL)
# y el **Liverpool de Montevideo** (Uruguay, Copa Libertadores). Si agrupamos solo por `Team`, los mezclamos.
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
# Clave de equipo única: equipo + liga (separa los tres Liverpool)
df["equipo"] = df["Team"] + " (" + df["League"] + ")"
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
histograma_con_centros(df["OVR"], "Distribución de la valoración global (OVR)", bins=range(40, 100, 2))
plt.xlabel("OVR"); plt.show()

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
# **Sturges** ($k \approx 1 + \log_2 n$) dan un punto de partida: aquí $1 + \log_2(17000) \approx 15$.
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
print(f"RIC          : {x.quantile(.75) - x.quantile(.25)}")
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
# Una función `resumen()` (definida arriba) aplicada a todas las columnas con `.apply()`.

# %%
tabla = df[cuantitativas].apply(resumen).T
(tabla.style.format("{:,.2f}")
     .background_gradient(subset=["asimetria_Fisher"], cmap="RdBu_r", vmin=-1.5, vmax=1.5)
     .background_gradient(subset=["CV_%"], cmap="Oranges"))

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
    histograma_con_centros(df[attr], f"{attr}  (asim. = {df[attr].skew():.2f})", bins=range(0, 101, 4), ax=ax)
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
# ## 7. Datos anómalos

# %%
li, ls = limites_tukey(df["OVR"])
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
    li, ls = limites_tukey(g["Height_cm"])
    filas.append({"sexo": sexo, "valla_inf": li, "valla_sup": ls,
                  "atipicos_dentro_del_grupo": ((g["Height_cm"] < li) | (g["Height_cm"] > ls)).sum()})
li, ls = limites_tukey(df["Height_cm"])
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

# %%
def ficha_jugador(nombre):
    """Valor, z y percentil de un jugador en las seis medias y en OVR."""
    fila = df.loc[df["Name"] == nombre]
    if fila.empty:
        print("No encontrado. Prueba con:", df["Name"].head(10).tolist()); return
    fila = fila.iloc[0]
    out = []
    for v in ["OVR"] + seis + ["Age", "Height_cm"]:
        out.append({"variable": v, "valor": fila[v],
                    "z": (fila[v] - df[v].mean()) / df[v].std(),
                    "percentil": stats.percentileofscore(df[v], fila[v])})
    print(f"{fila['Name']} · {fila['Position']} · {fila['Team']}")
    return pd.DataFrame(out).set_index("variable")

ficha_jugador(df.loc[df["OVR"].idxmax(), "Name"])

# %% [markdown]
# 👉 Probad con vuestro jugador favorito: `ficha_jugador("Pedri")`, `ficha_jugador("Lamine Yamal")`…

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
                   RIC=lambda s: s.quantile(.75) - s.quantile(.25),
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
# ## 11. ¿Regla empírica o Chebyshev?

# %%
m, s = df["OVR"].mean(), df["OVR"].std()
pd.DataFrame({
    "observado_%": [100 * df["OVR"].between(m - k*s, m + k*s).mean() for k in (1, 2, 3)],
    "si_fuera_normal_%": [68.27, 95.45, 99.73],
    "Chebyshev_minimo_%": [0, 75, 88.9],
}, index=pd.Index([1, 2, 3], name="k (desviaciones)"))

# %% [markdown]
# ## 🚀 Retos
# 1. Repite la tabla de ligas usando la **mediana** para ordenar. ¿Cambia el top 5?
# 2. ¿Qué equipo tiene más jugadores **atípicos por arriba** (según Tukey) en su plantilla?
# 3. Construye el **"once ideal"**: el mejor jugador (mayor OVR) de cada posición con `groupby("Position")["OVR"].idxmax()`.
# 4. ¿Qué equipo **femenino** tiene el OVR medio más alto? ¿Y la liga femenina más igualada?
# 5. ¿Qué nacionalidad (con n ≥ 50) es la más **homogénea** en OVR? ¿Y la más desigual?
# 6. Elige tú una pregunta y respóndela con un `groupby` y un gráfico. ¡La mejor se enseña en clase!
