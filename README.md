# Estadística Descriptiva con Python 📊

Material de prácticas de **Estadística Descriptiva** · 1.º del Grado en Ciencia de Datos · Universidad Complutense de Madrid
Prof. Daniel Gómez

Cuatro notebooks que cubren el temario de descriptiva con datos reales y preguntas que dan ganas de responder.
Se abren directamente en Google Colab: no hace falta instalar nada ni subir ficheros a mano.

| Notebook | Datos | Preguntas | Abrir |
|---|---|---|---|
| **01 · Futbolistas EA Sports FC** | 17.737 jugadores y jugadoras | ¿Cuántos jugadores tiene cada equipo (y por qué el Liverpool tiene 66)? ¿Qué liga es mejor y cuál más igualada? ¿A qué edad se alcanza el pico? ¿Por qué `DEF` tiene dos jorobas? | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DANIFUZZY1975/estadistica-descriptiva-python/blob/main/notebooks/01_fifa_jugadores.ipynb) |
| **02 · Felicidad mundial** | 149 países (World Happiness Report 2021) | ¿Da el dinero la felicidad? ¿Qué región es más desigual? ¿Dónde está España? | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DANIFUZZY1975/estadistica-descriptiva-python/blob/main/notebooks/02_felicidad_mundial.ipynb) |
| **03 · Géneros musicales** | 50.000 canciones de Spotify | ¿Qué género es más bailable? ¿Rap y Hip-Hop son lo mismo? ¿Canciones de 80 minutos? | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DANIFUZZY1975/estadistica-descriptiva-python/blob/main/notebooks/03_generos_musicales.ipynb) |
| **04 · Las trampas de la media** | Anscombe, Datasaurus, Berkeley 1973 | ¿Qué pasa con la media cuando Bill Gates entra en un bar? ¿Cuál de estos 13 conjuntos con los mismos estadísticos es un dinosaurio? ¿Discriminaba Berkeley a las mujeres? | [![Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DANIFUZZY1975/estadistica-descriptiva-python/blob/main/notebooks/04_trampas_de_la_media.ipynb) |

## Qué se trabaja

| Tema | 01 Fútbol | 02 Felicidad | 03 Música | 04 Trampas |
|---|:-:|:-:|:-:|:-:|
| Tipos de variables, tablas de frecuencias (absolutas, relativas, acumuladas) | ✅ | ✅ | ✅ | |
| Media, mediana, moda (y por qué `mode()` falla en continuas), media recortada | ✅ | ✅ | ✅ | ✅ |
| Cuartiles, deciles, percentiles, posición relativa | ✅ | ✅ | ✅ | |
| Rango, IQR (rango intercuartílico), varianza (n vs n−1), desviación típica, CV, MAD | ✅ | ✅ | ✅ | ✅ |
| Asimetría (Fisher y Pearson), curtosis, bimodalidad | ✅ | ✅ | ✅ | ✅ |
| Atípicos: regla de Tukey, z-scores, "¿error o crack?" | ✅ | ✅ | ✅ | ✅ |
| Tipificación y comparación entre variables | ✅ | ✅ | | |
| Comparación por grupos con `groupby` + `agg` | ✅ | ✅ | ✅ | |
| La trampa de los grupos pequeños / medias no ponderadas | ✅ | ✅ | | ✅ |
| Tablas de contingencia (`crosstab`) | ✅ | | ✅ | |
| Covarianza y correlación | ✅ | ✅ | ✅ | ✅ |
| Regla empírica vs. Chebyshev | ✅ | ✅ | | |
| Limpieza: faltantes disfrazados (`?`, `-1`), duplicados | | | ✅ | |
| Regresión lineal por mínimos cuadrados: $R^2$, residuos, predicción y extrapolación | ✅ | ✅ | ✅ | ✅ |
| Las dos rectas de regresión (y sobre x, x sobre y) y el centro de gravedad | ✅ | | | |
| Regresión potencial y exponencial (linealización con logaritmos) | ✅ | ✅ | ✅ | |
| Por qué hay que dibujar los datos (Anscombe, Datasaurus, mismo boxplot) | | | | ✅ |
| Paradoja de Simpson y medias ponderadas | | | | ✅ |

Los notebooks 01–03 están pensados para **tres sesiones de 2 horas** cada uno (el 04, para una), con **🚀 retos** al final de cada sesión.

## Estructura

```
data/        CSV de los ejemplos (los notebooks los leen desde aquí o desde GitHub)
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
- Cuarteto de Anscombe (Anscombe, *The American Statistician*, 1973), vía `seaborn-data`.
- *Datasaurus Dozen* y "mismo diagrama de caja" (Matejka y Fitzmaurice, CHI 2017), paquete `datasauRus` (licencia MIT).
- Admisiones de Berkeley 1973 (Bickel, Hammel y O'Connell, *Science*, 1975).

Se usan con fines exclusivamente docentes.
