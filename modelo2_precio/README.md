# Modelo 2 · Qué pasa con la venta si cambia el precio

Material del reto de machine learning que el equipo de inteligencia de negocios de Pycca propone a Coding Bootcamps de ESPOL (noviembre de 2026).

**Todos los datos son sintéticos.** Ningún SKU, precio, costo ni venta es real.

## Por dónde empezar

1. Lee [`LEEME.md`](LEEME.md): el problema, la trampa de la elasticidad, los datos, las dos tareas, las métricas y lo que se espera de cada equipo.
2. Revisa [`DICCIONARIO_DATOS.md`](DICCIONARIO_DATOS.md): cada columna de cada archivo.
3. Abre los notebooks, que vienen ejecutados:
   - `01_datos.ipynb`: los datos y la trampa de la elasticidad;
   - `02_baseline.ipynb`: las tareas, las métricas, el baseline y cómo se entregan los escenarios.
4. Corre el baseline:

   ```
   pip install pandas pyarrow scikit-learn matplotlib jupyter
   python baseline.py
   ```

## Contenido

| Archivo | Qué es |
| --- | --- |
| `LEEME.md` | El reto completo |
| `DICCIONARIO_DATOS.md` | Cada columna de cada archivo: tipo, descripción, rango, vacíos y ejemplo |
| `01_datos.ipynb`, `02_baseline.ipynb` | Notebooks ejecutados, con gráficos |
| `comun.py` | Carga de datos, cortes de tiempo, escenarios y métricas |
| `baseline.py` | El modelo a superar: una elasticidad por división, medida tal cual |
| `estilo.py` | Estilo de los gráficos |
| `validacion.csv` | Comparación real frente a sintético por división |
| `datos/` | `ventas_semanales.parquet`, `skus.csv`, `calendario.csv` y `escenarios_prueba.csv` |

Los meses de prueba (julio a diciembre de 2025) y la respuesta de los escenarios no están aquí: con ellos se evalúan los modelos entregados.
