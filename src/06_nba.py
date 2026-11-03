# %% [markdown]
# # 🏀 ¿A quién fichamos? Estadística descriptiva con los jugadores de la NBA (temporada 2021-22)
#
# **Estadística Descriptiva · 1.º Grado en Ciencia de Datos · UCM**
#
# ### 💼 El encargo
# Sois el departamento de análisis de un equipo de la NBA. El director deportivo os pide:
# - ¿Quiénes son los mejores **anotadores**? ¿Y los que más anotan **por minuto jugado**?
# - ¿Hay **gangas**: jugadores que juegan pocos minutos pero rinden mucho cuando juegan?
# - ¿Qué **perfil** tiene cada posición? ¿Conviene un jugador joven o veterano?
#
# Los datos son las estadísticas **por partido** de cada jugador en la temporada regular 2021-22 (de basketball-reference.com):
# partidos (`G`), minutos (`MP`), puntos (`PTS`), rebotes (`TRB`), asistencias (`AST`), tiros de campo, triples y tiros libres
# (intentados `A` y porcentaje `%`), robos, tapones, pérdidas…
#
# **Plan de trabajo (2 sesiones de 2 h):**
# - 🕐 Sesión 1 · Datos sucios, una variable y atípicos (apartados 1–4)
# - 🕐 Sesión 2 · Grupos, porcentajes engañosos, regresión y el informe de fichajes (5–8)

# %%
# (el bloque de configuración común se inserta aquí)
#@@COMUN@@

# %% [markdown]
# ---
# # 🕐 Sesión 1 de 2 · Datos sucios, una variable y atípicos
# **Objetivos:** leer un fichero con otra codificación y separador, detectar filas duplicadas, describir los puntos, los minutos
# y la edad, y encontrar atípicos.
# **Apartados:** 1 a 4 · **Duración orientativa:** 2 horas

# %% [markdown]
# ## 1. Carga: separador y codificación
# El fichero usa `;` como separador y una codificación antigua (`latin-1`) en lugar de la habitual `utf-8`.
# Si no se lo decimos, `pd.read_csv` falla con un `UnicodeDecodeError`. Pruébalo quitando `encoding="latin-1"`.

# %%
nba = pd.read_csv(URL_DATOS + "nba_2021_22.csv", sep=";", encoding="latin-1")
print("Dimensiones:", nba.shape)
nba.head()

# %%
nba.info()

# %% [markdown]
# 🤔 Busca a Luka Dončić o a Nikola Jokić:

# %%
nba[nba["Player"].str.contains("Luka|Nikola Jok")][["Player", "Tm", "PTS"]]

# %% [markdown]
# Las letras `č` y `ć` **no existen** en `latin-1` y al guardar el fichero se convirtieron en `?`. Esa información **se ha perdido**:
# ya no se puede recuperar desde el CSV. Moraleja: la codificación importa.

# %% [markdown]
# ## 2. 🕵️ ¿Cuántos jugadores hay? Filas duplicadas
# Hay 812 filas… pero `Rk` (el número de jugador) solo llega a 605. Algo se repite:

# %%
print("Filas:", len(nba), " |  valores distintos de Rk:", nba["Rk"].nunique(), " |  jugadores distintos:", nba["Player"].nunique())
nba[nba["Player"] == "Nickeil Alexander-Walker"][["Rk", "Player", "Tm", "G", "MP", "PTS"]]

# %% [markdown]
# Alexander-Walker fue **traspasado** a mitad de temporada: aparece una fila por cada equipo (NOP y UTA) y una fila `TOT` con el **total**
# de la temporada. Si no hacemos nada, contaremos tres veces al mismo jugador. Es el mismo tipo de problema que el "Liverpool"
# del notebook de fútbol.
#
# **Solución:** nos quedamos con una fila por jugador. Como la fila `TOT` aparece siempre la **primera**, basta con quedarnos
# con la primera fila de cada `Rk`.

# %%
print("Equipos (columna Tm):", nba["Tm"].nunique(), " -> incluye 'TOT', que no es un equipo")
print("Filas TOT:", (nba["Tm"] == "TOT").sum())

jug = nba.drop_duplicates(subset="Rk", keep="first").copy()
print("Jugadores tras quitar duplicados:", len(jug))

# %% [markdown]
# ¿Cuánto cambia el resultado si no quitamos los duplicados?

# %%
print(f"Puntos por partido, media con duplicados : {nba['PTS'].mean():.2f}")
print(f"Puntos por partido, media sin duplicados : {jug['PTS'].mean():.2f}")

# %% [markdown]
# ## 3. Variables cualitativas: posición
# Algunos jugadores tienen dos posiciones (`SG-SF`). Nos quedamos con la primera.

# %%
print(jug["Pos"].value_counts().to_string())
jug["Posicion"] = jug["Pos"].str.split("-").str[0]
nombres_pos = {"PG": "Base", "SG": "Escolta", "SF": "Alero", "PF": "Ala-pívot", "C": "Pívot"}
jug["Posicion"] = jug["Posicion"].map(nombres_pos)

tabla_pos = jug["Posicion"].value_counts().to_frame("n_i")
tabla_pos["f_i_%"] = 100 * tabla_pos["n_i"] / len(jug)
tabla_pos

# %% [markdown]
# ## 4. Una variable: puntos, minutos y edad

# %%
tabla = jug[["PTS", "MP", "G", "Age"]].agg(["count", "mean", "median", "std", "min", "max", "skew", "kurt"]).T
tabla["Q1"] = jug[["PTS", "MP", "G", "Age"]].quantile(0.25)
tabla["Q3"] = jug[["PTS", "MP", "G", "Age"]].quantile(0.75)
tabla["IQR"] = tabla["Q3"] - tabla["Q1"]
tabla["CV_%"] = 100 * tabla["std"] / tabla["mean"]
tabla.round(2)

# %%
fig, axes = plt.subplots(1, 3, figsize=(16, 4))
for ax, v, titulo in [(axes[0], "PTS", "Puntos por partido"), (axes[1], "MP", "Minutos por partido"), (axes[2], "Age", "Edad")]:
    sns.histplot(jug[v], bins=25, color=AZUL, alpha=0.5, ax=ax)
    ax.axvline(jug[v].mean(), color="#333333", lw=2, label=f"media = {jug[v].mean():.1f}")
    ax.axvline(jug[v].median(), color="#333333", ls="--", lw=2, label=f"mediana = {jug[v].median():.1f}")
    ax.set_title(f"{titulo} (asimetría = {jug[v].skew():.2f})"); ax.legend(frameon=False, fontsize=9)
plt.tight_layout(); plt.show()

# %% [markdown]
# 🤔 Los **puntos** tienen asimetría positiva: muchos jugadores anotan poco y unos pocos anotan muchísimo. ¿Y los **minutos**?
# Son casi simétricos. ¿Qué te dice eso de cómo reparten los entrenadores los minutos y de cómo se reparten los puntos?
#
# ### Atípicos: las estrellas

# %%
q1, q3 = jug["PTS"].quantile(0.25), jug["PTS"].quantile(0.75)
iqr = q3 - q1
ls = q3 + 1.5 * iqr
print(f"Q1 = {q1}, Q3 = {q3}, IQR = {iqr:.1f}  ->  valla superior = {ls:.1f} puntos")
estrellas = jug[jug["PTS"] > ls].sort_values("PTS", ascending=False)
print(f"{len(estrellas)} jugadores anotan más de {ls:.1f} puntos por partido:")
estrellas[["Player", "Posicion", "Tm", "Age", "MP", "PTS"]].head(15)

# %%
sns.boxplot(x=jug["PTS"], color="#cde2fb", width=0.4)
plt.title("Puntos por partido: los atípicos son las estrellas"); plt.xlabel("puntos por partido")
plt.show()

# %% [markdown]
# Aquí el atípico **no es un error**: es exactamente lo que el director deportivo busca. En el negocio del deporte, **el valor está en la cola**.

# %% [markdown]
# ### 🚀 Retos de la sesión 1
# 1. ¿Cuántos jugadores jugaron en **3 o más equipos** esa temporada? (pista: cuenta las filas de cada `Rk` en `nba`)
# 2. Describe los **rebotes** (`TRB`) y las **asistencias** (`AST`): media, mediana, asimetría. ¿Quién es atípico en cada una?
# 3. ¿Qué jugador jugó **más partidos**? ¿Cuántos jugaron los 82?
# 4. Tipifica los puntos: ¿cuántas desviaciones típicas por encima de la media está Joel Embiid?
#
# ---
# ✅ **Fin de la sesión 1.**

# %% [markdown]
# ---
# # 🕐 Sesión 2 de 2 · Grupos, porcentajes engañosos, regresión y fichajes
# **Objetivos:** comparar posiciones y edades con `groupby`, desconfiar de porcentajes y medias con pocos datos, regresión lineal
# de los puntos sobre los minutos y uso de los residuos para encontrar "gangas".
# **Apartados:** 5 a 8 · **Duración orientativa:** 2 horas
# > 💡 Si abres el notebook en una sesión nueva, ejecuta antes todas las celdas anteriores: menú *Entorno de ejecución → Ejecutar las celdas anteriores* (Ctrl+F8).

# %% [markdown]
# ## 5. 🏆 El perfil de cada posición

# %%
stats_pos = ["PTS", "TRB", "AST", "STL", "BLK", "3PA", "FG%"]
jug.groupby("Posicion")[stats_pos].mean().round(2)

# %% [markdown]
# Las variables están en escalas muy distintas (puntos frente a tapones). Para comparar perfiles, **tipificamos** cada variable
# y calculamos la media de las puntuaciones z por posición:

# %%
z = (jug[stats_pos] - jug[stats_pos].mean()) / jug[stats_pos].std()
perfil = z.groupby(jug["Posicion"]).mean().loc[["Base", "Escolta", "Alero", "Ala-pívot", "Pívot"]]
plt.figure(figsize=(9, 4.5))
sns.heatmap(perfil, annot=True, fmt=".2f", cmap="RdBu_r", center=0, vmin=-1, vmax=1, linewidths=2, linecolor="white")
plt.title("Perfil de cada posición (media de z; rojo = por encima de la media)"); plt.ylabel("")
plt.show()

# %% [markdown]
# 🤔 ¿Qué posición da más **asistencias**? ¿Cuál coge más **rebotes** y pone más **tapones**? ¿Cuál tira más **triples**?
# ¿Y por qué los pívots tienen el mejor **porcentaje de tiro** (`FG%`)? (pista: ¿desde dónde tiran?)
#
# ### ¿Joven o veterano? Puntos por edad

# %%
por_edad = jug.groupby("Age")["PTS"].agg(n="size", media="mean", mediana="median")
por_edad.round(1).T

# %% [markdown]
# ⚠️ ¡Los jugadores de **37 años** anotan de media 21,8 puntos, el triple que los de 24! ¿Los veteranos son los mejores?
# Mira la columna `n`: solo hay **2 jugadores de 37 años**… y uno de ellos es LeBron James.

# %%
jug[jug["Age"] >= 37][["Player", "Age", "G", "MP", "PTS"]]

# %%
d = por_edad[por_edad["n"] >= 15]
fig, ax = plt.subplots(figsize=(11, 4))
ax.plot(por_edad.index, por_edad["media"], marker="o", color="#9aa0a6", lw=1, label="todas las edades")
ax.plot(d.index, d["media"], marker="o", color=AZUL, lw=2.5, label="edades con al menos 15 jugadores")
ax.set_xlabel("edad"); ax.set_ylabel("puntos por partido (media)"); ax.legend(frameon=False)
ax.set_title("Puntos según la edad: cuidado con los grupos pequeños")
plt.show()

# %% [markdown]
# ## 6. ⚠️ Porcentajes y "por minuto" con pocos datos
# El director deportivo pide **el mejor tirador de triples**. Ordenamos por `3P%`:

# %%
jug.nlargest(5, "3P%")[["Player", "G", "3PA", "3P%"]]

# %% [markdown]
# ¡Jakob Poeltl, un pívot, con un **100 %** en triples! Pero su `3PA` (triples intentados por partido) es 0,0: en toda la temporada
# intentó apenas uno o dos triples y los metió. Un porcentaje calculado sobre 1 intento no dice nada. Exigimos un mínimo de intentos:

# %%
tiradores = jug[(jug["3PA"] >= 3) & (jug["G"] >= 40)]
print(f"Jugadores con al menos 3 triples intentados por partido y 40 partidos: {len(tiradores)}")
tiradores.nlargest(8, "3P%")[["Player", "Tm", "G", "3PA", "3P%"]]

# %% [markdown]
# Lo mismo pasa con los **puntos por 36 minutos** (una forma habitual de comparar a jugadores que juegan minutos distintos):

# %%
jug["PTS_36"] = jug["PTS"] / jug["MP"] * 36
print("Sin filtrar:")
print(jug.nlargest(5, "PTS_36")[["Player", "G", "MP", "PTS", "PTS_36"]].to_string(index=False))
print("\nCon al menos 40 partidos y 20 minutos por partido:")
print(jug[(jug["G"] >= 40) & (jug["MP"] >= 20)].nlargest(5, "PTS_36")[["Player", "G", "MP", "PTS", "PTS_36"]].to_string(index=False))

# %% [markdown]
# 🎯 Ahmad Caver jugó **un partido de un minuto** y anotó 2 puntos: "72 puntos por 36 minutos". Es la misma trampa que la media
# de un país con un solo futbolista o los veteranos de 37 años: **un resumen calculado con muy pocos datos no es fiable**.

# %% [markdown]
# ## 7. 📈 ¿Cuántos puntos "vale" un minuto? Regresión de los puntos sobre los minutos

# %%
x, y = jug["MP"], jug["PTS"]
print(f"Correlación minutos–puntos: r = {x.corr(y):.3f}")

Sxy = ((x - x.mean()) * (y - y.mean())).mean()
Sx2 = ((x - x.mean()) ** 2).mean()
b = Sxy / Sx2
a = y.mean() - b * x.mean()
r2 = 1 - ((y - (a + b * x)) ** 2).sum() / ((y - y.mean()) ** 2).sum()
print(f"Recta: puntos = {a:.2f} + {b:.3f}·minutos      R² = {r2:.3f}")
print(f"Cada minuto más de juego se asocia a {b:.2f} puntos más por partido")

# %%
xs = np.linspace(0, x.max(), 100)
plt.figure(figsize=(10, 6))
plt.scatter(x, y, s=15, alpha=0.4, color="#9aa0a6")
plt.plot(xs, a + b * xs, color=AZUL, lw=2.5, label="recta de regresión")
for nombre, desplaz in [("Joel Embiid", (-80, 10)), ("LeBron James", (10, -2)), ("Kevin Love", (-75, 12))]:
    f = jug[jug["Player"] == nombre].iloc[0]
    plt.scatter(f["MP"], f["PTS"], s=50, color=NARANJA, zorder=3)
    plt.annotate(nombre, (f["MP"], f["PTS"]), xytext=desplaz, textcoords="offset points", fontsize=9)
plt.xlabel("minutos por partido"); plt.ylabel("puntos por partido"); plt.legend(frameon=False)
plt.title("Puntos frente a minutos")
plt.show()

# %% [markdown]
# 🤔 Mira la forma de la nube: ¿es una recta o **se curva hacia arriba** a partir de 30 minutos? Las estrellas juegan más minutos
# **y además** anotan más por minuto. (Prueba un modelo potencial en los retos.)
#
# 🤔 ¿Tiene sentido la ordenada en el origen negativa? (Un jugador con 0 minutos anotaría puntos negativos…)
# La recta solo vale **dentro** del rango de los datos.
#
# 🤔 Y ojo con la causalidad: ¿los jugadores anotan más **porque** juegan más minutos, o juegan más minutos **porque** anotan mucho?
#
# ### Los residuos: ¿quién anota más de lo que "le toca" por sus minutos?
# El residuo $e_i = y_i - \hat y_i$ mide cuántos puntos anota un jugador **por encima o por debajo** de lo esperable para sus minutos.

# %%
jug["residuo"] = jug["PTS"] - (a + b * jug["MP"])
fiables = jug[jug["G"] >= 40]
print("Los que más anotan por encima de lo esperado (al menos 40 partidos):")
print(fiables.nlargest(6, "residuo")[["Player", "Tm", "G", "MP", "PTS", "residuo"]].to_string(index=False))

# %% [markdown]
# Son las estrellas: no son una sorpresa (y no son baratas). Busquemos **gangas**: jugadores con **pocos minutos** (menos de 25)
# que anotan por encima de lo esperado.

# %%
gangas = fiables[fiables["MP"] < 25].nlargest(8, "residuo")
gangas[["Player", "Posicion", "Tm", "Age", "G", "MP", "PTS", "residuo"]]

# %% [markdown]
# ## 8. 📝 El informe de fichajes
# Con lo que hemos visto, redactad (en 5 líneas) vuestra recomendación al director deportivo. Lo que dicen los datos:
# 1. **Los puntos están muy concentrados** en unas pocas estrellas (asimetría positiva, atípicos por arriba). Son las de siempre.
# 2. **Los minutos explican mucho** de los puntos ($R^2 \approx 0{,}78$), pero los **residuos** señalan a jugadores de banquillo que rinden
#    más de lo que sus minutos predicen (Kevin Love, DeMarcus Cousins, Moritz Wagner…): candidatos a más minutos o a fichaje barato.
# 3. **Desconfiad de los porcentajes y medias con pocos datos** (100 % en triples, 72 puntos por 36 minutos, los "veteranos de 37 años").
# 4. **Cada posición tiene su perfil**: comparad a cada jugador con los de su posición, no con todos.
# 5. **Lo que no sabemos**: el salario de cada jugador, su defensa, las lesiones… Sin el salario no podemos hablar de verdaderas "gangas".

# %% [markdown]
# ### 🚀 Retos de la sesión 2
# 1. Repite la regresión para los **rebotes** frente a los minutos, solo con los pívots. ¿Quién es la "ganga" reboteadora?
# 2. ¿Qué **equipo** tiene más puntos sumando a todos sus jugadores? (¡cuidado con las filas `TOT`! ¿Qué tabla usarías, `nba` o `jug`?)
# 3. Calcula el **porcentaje de tiros libres** (`FT%`) medio por posición. ¿Los pívots tiran peor los libres?
# 4. Busca el mejor **pasador por 36 minutos** (asistencias), con filtros razonables de partidos y minutos.
# 5. ¿Hay relación entre la **edad** y los puntos? Calcula la correlación y dibuja la nube de puntos.
# 6. Ajusta un modelo **potencial** $\text{PTS} = a \cdot \text{MP}^b$ (quita antes los jugadores con 0 puntos: ¿por qué?). ¿Sale $b > 1$? ¿Qué significa?
#
# ---
# 🏁 **Fin del notebook.**
