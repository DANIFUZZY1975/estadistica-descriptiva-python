# %% [markdown]
# # 🎬 ¿Qué películas compraría una plataforma de streaming? Estadística descriptiva con 10.000 películas
#
# **Estadística Descriptiva · 1.º Grado en Ciencia de Datos · UCM**
#
# ### 💼 El encargo
# Trabajáis en el equipo de datos de una plataforma de streaming. La dirección va a comprar los derechos de varios cientos de
# películas y os pregunta:
# - ¿Qué **géneros** compramos? ¿Los mejor **valorados** o los más **vistos**? ¿Es lo mismo?
# - ¿**Clásicos** o películas **recientes**?
# - ¿Merece la pena comprar un **remake** si ya tenemos la original?
#
# Los datos son las 10.000 películas mejor valoradas de la web *The Movie Database* (TMDB) con al menos 200 votos:
# título, géneros, fecha de estreno, **nota media** de los usuarios (0–10), **número de votos** y **popularidad**
# (un índice de TMDB que mide cuánto se está buscando y viendo la película *ahora*).
#
# **Plan de trabajo (2 sesiones de 2 h):**
# - 🕐 Sesión 1 · Limpieza, géneros y una variable: nota y popularidad (apartados 1–4)
# - 🕐 Sesión 2 · Comparar grupos, épocas, relaciones entre variables y el informe para la dirección (5–8)

# %%
# (el bloque de configuración común se inserta aquí)
#@@COMUN@@

# %% [markdown]
# ---
# # 🕐 Sesión 1 de 2 · Limpieza, géneros y una variable
# **Objetivos:** preparar los datos (fechas, listas dentro de una columna), frecuencias de una variable con varias categorías por fila,
# posición, dispersión y forma de la nota y de la popularidad, atípicos.
# **Apartados:** 1 a 4 · **Duración orientativa:** 2 horas

# %% [markdown]
# ## 1. Carga y limpieza

# %%
pelis = pd.read_csv(URL_DATOS + "peliculas.csv")
print("Dimensiones:", pelis.shape)
pelis.head()

# %%
pelis.info()

# %% [markdown]
# Tres cosas que arreglar:
# 1. `Unnamed: 0` es un índice que se guardó por error al exportar: fuera.
# 2. `release_date` es **texto**; la convertimos en fecha y sacamos el **año**.
# 3. `genre_ids` parece una lista (`[18, 80]`), pero en realidad es **texto** con corchetes. Hay que convertirlo en una lista de verdad
#    y traducir los códigos a nombres de género.

# %%
pelis = pelis.drop(columns=["Unnamed: 0"])
pelis["fecha"] = pd.to_datetime(pelis["release_date"])
pelis["año"] = pelis["fecha"].dt.year
print(type(pelis.loc[0, "genre_ids"]), "->", pelis.loc[0, "genre_ids"])

# %%
# Códigos de género de TMDB
generos_tmdb = {28: "Acción", 12: "Aventura", 16: "Animación", 35: "Comedia", 80: "Crimen", 99: "Documental",
                18: "Drama", 10751: "Familiar", 14: "Fantasía", 36: "Historia", 27: "Terror", 10402: "Música",
                9648: "Misterio", 10749: "Romance", 878: "Ciencia ficción", 10770: "Película de TV",
                53: "Suspense", 10752: "Bélica", 37: "Western"}

# "[18, 80]" -> quitamos los corchetes, separamos por comas y traducimos cada número
pelis["generos"] = (pelis["genre_ids"].str.strip("[]").str.split(",")
                    .apply(lambda lista: [generos_tmdb[int(c)] for c in lista if c.strip() != ""]))
pelis["n_generos"] = pelis["generos"].str.len()
pelis[["title", "año", "genre_ids", "generos", "n_generos"]].head()

# %% [markdown]
# ### ¿Hay películas repetidas?

# %%
print("Mismo id repetido:", pelis["id"].duplicated().sum())
print("Mismo título repetido:", pelis["title"].duplicated().sum())
pelis[pelis["title"].duplicated(keep=False)].sort_values(["title", "año"])[["title", "año", "vote_average", "vote_count"]].head(10)

# %% [markdown]
# 🤔 No hay ids repetidos, pero sí **335 filas con un título repetido** (305 títulos distintos). ¿Son errores? No: muchos son **remakes** (*12 Angry Men* de 1957 y de 1997)
# y otros, películas distintas que comparten título (*9*). Lo aprovecharemos en el apartado 8.

# %% [markdown]
# ## 2. Variable cualitativa con varias categorías por fila: los géneros
# Una película puede tener varios géneros a la vez. ¿Cuántos tiene cada película?

# %%
tabla_ng = pelis["n_generos"].value_counts().sort_index().to_frame("n_i")
tabla_ng["f_i_%"] = 100 * tabla_ng["n_i"] / len(pelis)
tabla_ng["F_i_%"] = tabla_ng["f_i_%"].cumsum()
tabla_ng

# %% [markdown]
# Para contar géneros usamos `explode()`: convierte cada película con 3 géneros en **3 filas**, una por género.

# %%
por_genero = pelis.explode("generos").dropna(subset=["generos"]).reset_index(drop=True)
print(f"De {len(pelis)} películas pasamos a {len(por_genero)} filas película-género")
print("(las 3 películas sin ningún género se quedan fuera; reset_index numera de nuevo las filas, que se habían repetido)")
frec_gen = por_genero["generos"].value_counts().to_frame("n_i")
frec_gen["% de películas"] = 100 * frec_gen["n_i"] / len(pelis)
frec_gen

# %% [markdown]
# 🤔 Si sumas la columna `% de películas`, ¿da 100 %? ¿Por qué no? (Una película cuenta en varios géneros.)
# Por eso las frecuencias relativas de una variable **multirrespuesta** no suman 1.

# %%
ax = frec_gen["n_i"].sort_values().plot.barh(color=AZUL, figsize=(9, 6))
ax.set_title("Número de películas de cada género"); ax.set_xlabel("películas")
plt.show()

# %% [markdown]
# ## 3. La nota media de los usuarios (`vote_average`)

# %%
x = pelis["vote_average"]
print(f"Media    : {x.mean():.3f}")
print(f"Mediana  : {x.median():.3f}")
print(f"Moda     : {x.mode().tolist()}")
print(f"Mínimo   : {x.min()}   Máximo: {x.max()}")
print(f"Desv. típica: {x.std():.3f}   IQR: {x.quantile(0.75) - x.quantile(0.25):.2f}")
print(f"Asimetría: {x.skew():.3f}   Curtosis: {x.kurt():.3f}")

# %%
sns.histplot(x, bins=np.arange(5.6, 8.9, 0.1), color=AZUL, alpha=0.6)
plt.axvline(x.mean(), color="#333333", lw=2, label=f"media = {x.mean():.2f}")
plt.axvline(x.median(), color="#333333", ls="--", lw=2, label=f"mediana = {x.median():.2f}")
plt.title("Nota media de las películas"); plt.xlabel("nota (0-10)"); plt.legend(frameon=False)
plt.show()

# %% [markdown]
# 🤔 **¿No hay ninguna película con menos de un 5,7?** El histograma está **cortado** a la izquierda. ¿Es que no existen películas malas?
# No: este dataset son las 10.000 películas **mejor valoradas**. Es una **muestra seleccionada**, no "todas las películas".
# Cualquier conclusión vale solo para este catálogo de películas buenas. Fíjate también en que la nota tiene muy poca dispersión
# (desviación típica 0,64): casi todas están entre 6 y 7,5.
#
# Las mejor y peor valoradas del catálogo:

# %%
pd.concat([pelis.nlargest(5, "vote_average"), pelis.nsmallest(5, "vote_average")])[["title", "año", "vote_average", "vote_count"]]

# %% [markdown]
# ## 4. La popularidad: una variable muy asimétrica

# %%
p = pelis["popularity"]
print(f"Media    : {p.mean():.2f}")
print(f"Mediana  : {p.median():.2f}")
print(f"Máximo   : {p.max():.2f}")
print(f"Desv. típica: {p.std():.2f}  (¡mayor que la media!)   CV = {100 * p.std() / p.mean():.0f} %")
print(f"Asimetría: {p.skew():.2f}")

# %%
fig, axes = plt.subplots(1, 2, figsize=(15, 4))
sns.histplot(p, bins=60, color=AZUL, ax=axes[0])
axes[0].set_title(f"Popularidad (asimetría = {p.skew():.1f})")
sns.histplot(np.log10(p), bins=40, color=VERDE, ax=axes[1])
axes[1].set_title(f"log10(popularidad) (asimetría = {np.log10(p).skew():.2f})")
axes[1].set_xlabel("log10(popularidad):  1 = 10, 2 = 100, 3 = 1000")
plt.tight_layout(); plt.show()

# %% [markdown]
# 🎯 La popularidad tiene una **cola larguísima** a la derecha: la media (21,5) casi duplica a la mediana (12,4). En una variable así,
# la **media no representa** a la película típica. Con logaritmos la forma se vuelve mucho más manejable.
#
# ### Atípicos: ¿quién está tan por encima?

# %%
q1, q3 = p.quantile(0.25), p.quantile(0.75)
iqr = q3 - q1
ls = q3 + 1.5 * iqr
atipicas = pelis[p > ls]
print(f"Valla superior de Tukey: {ls:.1f} -> {len(atipicas)} películas atípicas ({100 * len(atipicas) / len(pelis):.1f} %)")
print("¿De qué año son las atípicas?")
print(atipicas["año"].value_counts().head(5).to_string())
pelis.nlargest(10, "popularity")[["title", "año", "popularity", "vote_average"]]

# %% [markdown]
# 🤔 Las más populares son casi todas **estrenos recientes** (2023). La popularidad mide lo que se ve **ahora**, así que favorece
# lo nuevo. Para la plataforma esto es importante: **un estreno es popular unos meses; un clásico bien valorado, durante años**.

# %% [markdown]
# ### 🚀 Retos de la sesión 1
# 1. ¿Qué porcentaje de películas tiene **3 géneros o menos**? (usa la tabla de `n_generos`)
# 2. Calcula media, mediana y desviación típica del **número de votos** (`vote_count`). ¿Es simétrica? Dibuja su histograma con y sin logaritmos.
# 3. ¿Cuál es la película **más antigua** del catálogo? ¿Y la más reciente? ¿Cuántas hay de cada década? (pista: `(pelis["año"] // 10) * 10`)
# 4. Busca tu película favorita con `pelis[pelis["title"].str.contains("...")]`. ¿En qué percentil de nota está?
#
# ---
# ✅ **Fin de la sesión 1.**

# %% [markdown]
# ---
# # 🕐 Sesión 2 de 2 · Comparar grupos, épocas y relaciones
# **Objetivos:** comparar géneros con `groupby`, sesgo de supervivencia, correlación y regresión (lineal y potencial)
# con variables muy asimétricas, y redactar el informe para la dirección.
# **Apartados:** 5 a 8 · **Duración orientativa:** 2 horas
# > 💡 Si abres el notebook en una sesión nueva, ejecuta antes todas las celdas anteriores: menú *Entorno de ejecución → Ejecutar las celdas anteriores* (Ctrl+F8).

# %% [markdown]
# ## 5. 🏆 ¿Qué género compramos? Valoración frente a popularidad

# %%
tabla_gen = (por_genero.groupby("generos")
               .agg(n=("title", "size"),
                    nota_media=("vote_average", "mean"),
                    nota_mediana=("vote_average", "median"),
                    popularidad_mediana=("popularity", "median"),
                    votos_mediana=("vote_count", "median"))
               .sort_values("nota_media", ascending=False))
tabla_gen.round(2).style.background_gradient(subset=["nota_media"], cmap="Blues").background_gradient(subset=["popularidad_mediana"], cmap="Oranges")

# %% [markdown]
# 🤔 ¿Por qué usamos la **mediana** de la popularidad y no la media? (Recuerda el apartado 4.)

# %%
fig, ax = plt.subplots(figsize=(11, 7))
ax.scatter(tabla_gen["popularidad_mediana"], tabla_gen["nota_media"], s=tabla_gen["n"] / 6, color=AZUL, alpha=0.6, edgecolor="white")
for genero, f in tabla_gen.iterrows():
    ax.annotate(genero, (f["popularidad_mediana"], f["nota_media"]), xytext=(6, 2), textcoords="offset points", fontsize=9)
ax.axvline(pelis["popularity"].median(), color="#9aa0a6", ls="--")
ax.axhline(pelis["vote_average"].mean(), color="#9aa0a6", ls="--")
ax.set_xlabel("popularidad mediana (lo que se ve)"); ax.set_ylabel("nota media (lo que gusta)")
ax.set_title("Géneros: ¿lo que gusta es lo que se ve?  (tamaño = número de películas)")
plt.show()

# %% [markdown]
# 🎯 **Cuatro cuadrantes, cuatro estrategias:**
# - **Arriba a la derecha** (gusta y se ve): **Animación**, Fantasía, Familiar. El género "seguro".
# - **Arriba a la izquierda** (gusta, pero se ve poco): Bélica, Historia, Drama, Western. Prestigio barato: catálogo de fondo.
# - **Abajo a la derecha** (se ve mucho aunque guste menos): Acción, Aventura, Ciencia ficción. Atraen público.
# - **Abajo a la izquierda**: la Comedia, con muchísimas películas, nota baja y poca popularidad.
# - Y en medio, Suspense, Misterio y **Terror**: algo más vistos que la mediana, pero peor valorados. El Terror es el género peor
#   valorado… y aun así se ve más que el Drama.
#
# Lo que **gusta** y lo que **se ve** no son lo mismo. La plataforma tiene que decidir qué quiere.

# %% [markdown]
# ### ¿Los géneros son homogéneos? Dispersión por grupo

# %%
orden = tabla_gen.index
fig, ax = plt.subplots(figsize=(12, 7))
sns.boxplot(data=por_genero, y="generos", x="vote_average", order=orden, color="#cde2fb", fliersize=2, ax=ax)
ax.axvline(pelis["vote_average"].median(), color="#333333", ls="--", label="mediana global")
ax.set_title("Nota por género (ordenados por nota media)"); ax.set_ylabel(""); ax.legend(frameon=False)
plt.show()

# %% [markdown]
# ## 6. ¿Clásicos o recientes? El sesgo de supervivencia

# %%
pelis["decada"] = (pelis["año"] // 10) * 10
por_decada = pelis.groupby("decada").agg(n=("title", "size"), nota_media=("vote_average", "mean"),
                                         nota_mediana=("vote_average", "median"),
                                         popularidad_mediana=("popularity", "median"))
por_decada.round(2)

# %%
d = por_decada[por_decada["n"] >= 20]
fig, axes = plt.subplots(1, 2, figsize=(15, 4.5))
axes[0].plot(d.index, d["nota_media"], marker="o", color=AZUL, lw=2)
axes[0].set_title("Nota media por década (décadas con ≥ 20 películas)"); axes[0].set_xlabel("década")
axes[1].bar(d.index, d["n"], width=7, color=NARANJA)
axes[1].set_title("Número de películas de cada década en el catálogo"); axes[1].set_xlabel("década")
plt.tight_layout(); plt.show()

# %% [markdown]
# 🤔 **¿El cine de antes era mejor?** Las películas de los años 20 a 60 tienen notas más altas… pero hay **muchas menos**.
# De los años 50 sobreviven en el catálogo 186 películas; de los 2010, casi 3.700. De la época antigua **solo ha llegado hasta hoy lo mejor**:
# las películas malas de 1950 nadie las vota ya y no pasan el filtro de 200 votos. Esto es el **sesgo de supervivencia**.
# No podemos concluir que el cine antiguo fuera mejor: estamos comparando **lo mejor de antes** con **casi todo lo de ahora**.
#
# 🤔 ¿Y por qué **sube** la nota en los años 2020? Pista: las películas recién estrenadas las votan primero sus fans.

# %% [markdown]
# ## 7. Relaciones entre variables: ¿más votos = más popularidad?

# %%
print("Correlación votos–popularidad              :", round(pelis["vote_count"].corr(pelis["popularity"]), 3))
print("Correlación log(votos)–log(popularidad)    :", round(np.log(pelis["vote_count"]).corr(np.log(pelis["popularity"])), 3))
print("Correlación nota–popularidad               :", round(pelis["vote_average"].corr(pelis["popularity"]), 3))
print("Correlación nota–log(votos)                :", round(pelis["vote_average"].corr(np.log(pelis["vote_count"])), 3))

# %%
fig, axes = plt.subplots(1, 2, figsize=(15, 5))
axes[0].scatter(pelis["vote_count"], pelis["popularity"], s=6, alpha=0.3, color=AZUL)
axes[0].set_xlabel("número de votos"); axes[0].set_ylabel("popularidad"); axes[0].set_title("Escala original")
axes[1].scatter(np.log(pelis["vote_count"]), np.log(pelis["popularity"]), s=6, alpha=0.3, color=NARANJA)
axes[1].set_xlabel("ln(votos)"); axes[1].set_ylabel("ln(popularidad)"); axes[1].set_title("Escala log-log")
plt.tight_layout(); plt.show()

# %% [markdown]
# 🎯 En escala original la correlación es solo 0,14: la nube está aplastada contra los ejes por unas pocas películas enormes.
# En escala **log-log** la relación aparece clara ($r \approx 0{,}60$). Con variables tan asimétricas, el coeficiente de Pearson
# en escala original engaña. Ajustemos un modelo **potencial** $\text{popularidad} = a \cdot \text{votos}^b$:

# %%
x, y = pelis["vote_count"], pelis["popularity"]
lx, ly = np.log(x), np.log(y)

b_pot = ((lx - lx.mean()) * (ly - ly.mean())).mean() / ((lx - lx.mean()) ** 2).mean()
a_pot = np.exp(ly.mean() - b_pot * lx.mean())
r2_log = 1 - ((ly - (np.log(a_pot) + b_pot * lx)) ** 2).sum() / ((ly - ly.mean()) ** 2).sum()
print(f"popularidad = {a_pot:.3f} · votos^{b_pot:.3f}     R² (en logaritmos) = {r2_log:.3f}")
print(f"Si una película tiene el doble de votos, su popularidad se multiplica por 2^{b_pot:.3f} = {2 ** b_pot:.2f}")

xs = np.linspace(np.log(x.min()), np.log(x.max()), 100)
plt.scatter(lx, ly, s=6, alpha=0.3, color="#9aa0a6")
plt.plot(xs, np.log(a_pot) + b_pot * xs, color=NARANJA, lw=2.5, label="recta en log-log = modelo potencial")
plt.xlabel("ln(votos)"); plt.ylabel("ln(popularidad)"); plt.legend(frameon=False); plt.title("Modelo potencial")
plt.show()

# %% [markdown]
# 🤔 Y la **nota** casi no tiene relación con la popularidad ($r \approx 0{,}09$). **Que una película sea buena no hace que se vea más.**

# %% [markdown]
# ## 8. ¿Compramos remakes? Original frente a nueva versión
# Tomamos los títulos que aparecen más de una vez y comparamos la **primera** versión con la **última**.
# (Ojo: algunos títulos repetidos no son remakes sino películas distintas con el mismo nombre. Es una aproximación.)

# %%
repetidas = pelis[pelis["title"].duplicated(keep=False)].sort_values(["title", "año"])
versiones = repetidas.groupby("title").agg(n_versiones=("año", "size"),
                                           año_original=("año", "first"), nota_original=("vote_average", "first"),
                                           año_ultima=("año", "last"), nota_ultima=("vote_average", "last"))
versiones["diferencia"] = versiones["nota_original"] - versiones["nota_ultima"]
print(f"Títulos con varias versiones: {len(versiones)}")
print(f"La original tiene MÁS nota en el {100 * (versiones['diferencia'] > 0).mean():.0f} % de los casos")
print(f"Diferencia media: {versiones['diferencia'].mean():+.2f} puntos   |   mediana: {versiones['diferencia'].median():+.2f}")
versiones.sort_values("diferencia", ascending=False).head(8)

# %%
sns.histplot(versiones["diferencia"], bins=30, color=AZUL)
plt.axvline(0, color="#333333", lw=1.5)
plt.axvline(versiones["diferencia"].mean(), color=NARANJA, lw=2, ls="--", label=f"media = {versiones['diferencia'].mean():+.2f}")
plt.title("Nota de la original menos nota de la última versión"); plt.xlabel("diferencia de nota"); plt.legend(frameon=False)
plt.show()

# %% [markdown]
# 🤔 La original suele estar mejor valorada (en torno a 6 de cada 10 veces), pero ¡cuidado! Ya hemos visto que las películas antiguas
# que siguen en el catálogo son **supervivientes**. ¿Puede eso explicar parte de la diferencia?

# %% [markdown]
# ## 📝 El informe para la dirección
# Con lo que hemos visto, redactad (en 5 líneas) vuestra recomendación de compra. Algunas ideas de lo que los datos dicen:
# 1. **Lo que gusta y lo que se ve no coinciden.** La Animación es el único género grande que destaca en las dos cosas.
# 2. **La popularidad es efímera y muy desigual**: unas pocas películas (los estrenos) se llevan la atención. La mediana, no la media,
#    describe a la película típica.
# 3. **Los clásicos están bien valorados**, pero en parte por el sesgo de supervivencia: compradlos por su valor, no porque "antes se hiciera mejor cine".
# 4. **Los remakes suelen valorarse peor** que la original; si ya tenemos la original, el remake aporta poco en nota.
# 5. **Lo que no sabemos**: el precio de cada película, cuánto la ven nuestros usuarios… Sin esos datos no podemos calcular la rentabilidad.

# %% [markdown]
# ### 🚀 Retos de la sesión 2
# 1. Repite la tabla de géneros quitando las películas posteriores a 2020. ¿Cambia el cuadrante de algún género?
# 2. ¿Qué género tiene la **mayor dispersión** de nota (desviación típica e IQR)? ¿Y la menor?
# 3. Calcula el porcentaje de películas de **Terror** en cada década. ¿Cada vez se hace más terror?
# 4. ¿Las películas con **más géneros** tienen más o menos nota? Calcula la nota media según `n_generos` (solo grupos con n ≥ 50).
# 5. Ajusta un modelo lineal para la nota en función de `ln(vote_count)`. ¿Cuánto vale el $R^2$? Interprétalo.
#
# ---
# 🏁 **Fin del notebook.**
