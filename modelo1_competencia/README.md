# Modelo 1 · Anticipar el próximo movimiento de precio de la competencia

Material del reto de machine learning que el equipo de inteligencia de negocios de Pycca propone a Coding Bootcamps de ESPOL (noviembre de 2026).

**Todos los datos son sintéticos.** Ningún precio, producto ni comercio es real.

El reto tiene dos partes:
- **Parte 1 · Clustering:** agrupar las 3.616 series (producto × comercio) según cómo se mueve su precio.
- **Parte 2 · Clasificación:** predecir si el precio va a bajar al menos 5 % en los próximos 7 días o mañana.

## Por dónde empezar

1. Lee [`LEEME.md`](LEEME.md): el problema, los datos, las dos partes, las métricas y lo que se espera de cada equipo.
2. Abre los notebooks, que vienen ejecutados:
   - `01_datos.ipynb`: qué hay en los datos y qué patrones tienen;
   - `02_clusters.ipynb`: parte 1, agrupar las series;
   - `03_clasificacion.ipynb`: parte 2, la tabla lista, cuatro modelos y la matriz de confusión.
3. Corre los baselines:

   ```
   pip install pandas pyarrow scikit-learn matplotlib jupyter
   python baseline_clusters.py                 # parte 1: deja grupos_baseline.csv
   python baseline.py                          # parte 2, tarea A: ¿baja en los próximos 7 días?
   set HORIZONTE=1 && python baseline.py       # parte 2, tarea B en Windows: ¿baja mañana?
   HORIZONTE=1 python baseline.py              # parte 2, tarea B en Linux o Mac
   ```

## Contenido

| Archivo | Qué es |
| --- | --- |
| `LEEME.md` | El reto completo |
| `DICCIONARIO_DATOS.md` | Cada columna de cada archivo: tipo, descripción, rango, vacíos y ejemplo |
| `01_datos.ipynb`, `02_clusters.ipynb`, `03_clasificacion.ipynb` | Notebooks ejecutados, con gráficos |
| `variables.py` | El objetivo (qué cuenta como baja) y las 23 variables del baseline |
| `tablas.py` | Arma las dos tablas listas a partir de los datos diarios |
| `baseline_clusters.py` | El agrupamiento a superar (parte 1) |
| `baseline.py` | El clasificador a superar (parte 2) |
| `grupos_baseline.csv` | Los grupos del baseline: el formato de entrega de la parte 1 |
| `estilo.py` | Estilo de los gráficos |
| `validacion.csv` | Comparación real frente a sintético por comercio |
| `datos/` | `precios_diarios.parquet`, `productos.csv`, `comercios.csv`, `calendario.csv` y las tablas listas `tabla_series.csv` y `tabla_clasificacion.parquet` |

Los meses de prueba (julio a diciembre de 2025) y los perfiles ocultos de las series no están aquí: con ellos se evalúan los trabajos entregados.
