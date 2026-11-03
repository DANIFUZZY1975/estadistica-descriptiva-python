# Estadística Descriptiva con Python 📊

Material de prácticas de **Estadística Descriptiva** · 1.º del Grado en Ciencia de Datos · Universidad Complutense de Madrid
Prof. Daniel Gómez

Seis notebooks que cubren el temario de descriptiva con datos reales y preguntas que dan ganas de responder.
Se abren directamente en Google Colab: no hace falta instalar nada ni subir ficheros a mano.

| Notebook | Datos | Preguntas | Abrir |
|---|---|---|---|
| **01 · Futbolistas EA Sports FC** | 17.737 jugadores y jugadoras | ¿Cuántos jugadores tiene cada equipo (y por qué el Liverpool tiene 66)? ¿Qué liga es mejor y cuál más igualada? ¿A qué edad se alcanza el pico? ¿Por qué `DEF` tiene dos jorobas? | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DANIFUZZY1975/estadistica-descriptiva-python/blob/main/notebooks/01_fifa_jugadores.ipynb) |
| **02 · Felicidad mundial** | 149 países (World Happiness Report 2021) | ¿De qué depende la felicidad? ¿Da el dinero la felicidad? ¿Qué región es más desigual? ¿Dónde está España? | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DANIFUZZY1975/estadistica-descriptiva-python/blob/main/notebooks/02_felicidad_mundial.ipynb) |
| **03 · Géneros musicales** | 50.000 canciones de Spotify | ¿Qué género es más bailable? ¿Rap y Hip-Hop son lo mismo? ¿Canciones de 80 minutos? ¿Se puede fabricar un éxito? | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DANIFUZZY1975/estadistica-descriptiva-python/blob/main/notebooks/03_generos_musicales.ipynb) |
| **04 · Las trampas de la media** | Anscombe, Datasaurus, Berkeley 1973, Star Wars | ¿Qué pasa con la media cuando Bill Gates entra en un bar? ¿Cuál de estos 13 conjuntos es un dinosaurio? ¿Discriminaba Berkeley a las mujeres? ¿Cuánto pesa Jabba? | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DANIFUZZY1975/estadistica-descriptiva-python/blob/main/notebooks/04_trampas_de_la_media.ipynb) |
| **05 · Películas** | 10.000 películas de TMDB | ¿Lo que gusta es lo que se ve? ¿El cine de antes era mejor? ¿Los remakes son peores? | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DANIFUZZY1975/estadistica-descriptiva-python/blob/main/notebooks/05_peliculas.ipynb) |
| **06 · NBA 2021-22** | 605 jugadores | ¿Quién anota más por minuto? ¿Un 100 % en triples es buena señal? ¿Hay gangas en el banquillo? | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DANIFUZZY1975/estadistica-descriptiva-python/blob/main/notebooks/06_nba.ipynb) |

## 💼 Cada notebook es un encargo

Los análisis se plantean como un trabajo real para un cliente, y terminan con un informe que hay que redactar:

| Notebook | El cliente | La pregunta |
|---|---|---|
| 01 · Fútbol | Un club con poco presupuesto | ¿En qué ligas y a qué edad buscar jugadores? ¿Son fiables los datos? |
| 02 · Felicidad | Un ministerio o una ONG | ¿De qué depende la felicidad de un país? ¿Qué se puede (y qué no) concluir? |
| 03 · Música | Una discográfica | ¿Tienen receta las canciones de éxito? |
| 05 · Películas | Una plataforma de streaming | ¿Qué géneros y qué épocas compramos? ¿Compramos remakes? |
| 06 · NBA | Un director deportivo | ¿A quién fichamos? ¿Hay jugadores infravalorados? |

## Qué se trabaja

| Tema | 01 Fútbol | 02 Felicidad | 03 Música | 04 Trampas | 05 Películas | 06 NBA |
|---|:-:|:-:|:-:|:-:|:-:|:-:|
| Carga de datos: separadores, codificación, tipos mal leídos | ✅ | | ✅ | ✅ | ✅ | ✅ |
| Limpieza: faltantes disfrazados, duplicados, grupos mezclados | ✅ | | ✅ | ✅ | ✅ | ✅ |
| Tipos de variables, tablas de frecuencias (absolutas, relativas, acumuladas) | ✅ | ✅ | ✅ | | ✅ | ✅ |
| Media, mediana, moda (y moda interpolada en continuas), media recortada | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Cuartiles, deciles, percentiles, posición relativa | ✅ | ✅ | ✅ | | ✅ | ✅ |
| Rango, IQR (rango intercuartílico), varianza (n vs n−1), desviación típica, CV, MAD | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Asimetría, curtosis, bimodalidad, transformación logarítmica | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Atípicos: regla de Tukey, z-scores, "¿error o crack?" | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Tipificación y perfiles de grupos | ✅ | ✅ | | | | ✅ |
| Comparación por grupos con `groupby` + `agg` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| La trampa de los grupos pequeños / medias no ponderadas | ✅ | ✅ | | ✅ | | ✅ |
| Tablas de contingencia (`crosstab`) y variables multirrespuesta | ✅ | | ✅ | | ✅ | |
| Covarianza y correlación (y su fragilidad ante atípicos) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Razón de correlación $\eta^2$ | | | ✅ | | | |
| Correlación ≠ causalidad, falacia ecológica, sesgo de supervivencia, muestras seleccionadas | ✅ | ✅ | ✅ | | ✅ | ✅ |
| Regla empírica vs. Chebyshev | ✅ | ✅ | | | | |
| Regresión lineal: $R^2$, residuos, predicción y extrapolación | ✅ | ✅ | ✅ | ✅ | | ✅ |
| Las dos rectas de regresión (y sobre x, x sobre y) | ✅ | | | | | |
| Regresión potencial y exponencial (linealización con logaritmos) | ✅ | ✅ | ✅ | | ✅ | |
| Paradoja de Simpson | | | ✅ | ✅ | | |

Los notebooks 01–03 están pensados para **tres sesiones de 2 horas**; el 05 y el 06, para **dos**; el 04, para **una**.
Todos tienen **🚀 retos** al final de cada sesión.

## Estructura

```
data/        Ficheros de datos (los notebooks los leen directamente desde GitHub)
notebooks/   Notebooks listos para abrir en Colab (ya ejecutados: se ven los resultados sin correr nada)
src/         Fuentes .py de los notebooks y script para regenerarlos
```

Para modificar un notebook se edita su `.py` en `src/` y se regenera:

```bash
pip install -r requirements.txt
python src/construir.py --ejecutar          # todos
python src/construir.py --ejecutar musica   # solo uno
```

## Fuentes de datos

- *World Happiness Report 2021* (Helliwell, Layard, Sachs y De Neve), versión publicada en Kaggle.
- *Music genre classification* (canciones de Spotify con rasgos de audio), Kaggle.
- Jugadores de *EA Sports FC 25* (valoraciones del videojuego), Kaggle.
- Películas mejor valoradas de *The Movie Database* (TMDB), con al menos 200 votos.
- Estadísticas por partido de la NBA, temporada regular 2021-22 (basketball-reference.com).
- Personajes de Star Wars (Star Wars API, versión del paquete `dplyr` de R).
- Cuarteto de Anscombe (Anscombe, *The American Statistician*, 1973), vía `seaborn-data`.
- *Datasaurus Dozen* y "mismo diagrama de caja" (Matejka y Fitzmaurice, CHI 2017), paquete `datasauRus` (licencia MIT).
- Admisiones de Berkeley 1973 (Bickel, Hammel y O'Connell, *Science*, 1975).

Se usan con fines exclusivamente docentes.

## 🔎 ¿Dónde encontrar más datos?

Para que cada uno busque su propio dataset y haga su propio encargo:

**Recomendados para empezar (muy bien estructurados)**
- [UCI Machine Learning Repository](https://archive.ics.uci.edu/)
- [KEEL (Universidad de Granada)](https://sci2s.ugr.es/keel/datasets.php)
- [Rdatasets](https://vincentarelbundock.github.io/Rdatasets/datasets.html)

**Comprimidos y poco explicados**
- [Vanderbilt Biostatistics datasets](http://biostat.mc.vanderbilt.edu/wiki/Main/DataSets)
- [Weka datasets (Universidad de Waikato)](https://www.cs.waikato.ac.nz/ml/weka/datasets.html)

**Complicados pero interesantes**
- [Scientific Data (Nature)](https://www.nature.com/sdata/)
- [Datasets del curso de Data Mining de la Universidad de Edimburgo](http://www.inf.ed.ac.uk/teaching/courses/dme/html/datasets0405.html)

**Concursos**
- [Kaggle](https://www.kaggle.com/)
- [DrivenData](https://www.drivendata.org/competitions/)
- [ChaLearn](http://www.chalearn.org/challenges.html)
- [KDD Cup](https://www.kdd.org/kdd-cup)
