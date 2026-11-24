# Reto: anticipar el próximo movimiento de precio de la competencia

Material del reto de machine learning que el equipo de inteligencia de negocios de Pycca propone a Coding Bootcamps de ESPOL (noviembre de 2026).

**Todos los datos son sintéticos.** Ningún precio, producto ni comercio es real.

## Por dónde empezar

1. Lee [`LEEME.md`](LEEME.md): el problema, los datos, las dos tareas, las métricas y lo que se espera de cada equipo.
2. Abre los notebooks, que vienen ejecutados:
   - `01_datos.ipynb`: qué hay en los datos y qué patrones tienen;
   - `02_baseline.ipynb`: la tarea, la métrica y el baseline.
3. Corre el baseline:

   ```
   pip install pandas pyarrow scikit-learn matplotlib jupyter
   python baseline.py                          # tarea A: ¿baja en los próximos 7 días?
   set HORIZONTE=1 && python baseline.py       # tarea B en Windows: ¿baja mañana?
   HORIZONTE=1 python baseline.py              # tarea B en Linux o Mac
   ```

## Contenido

| Archivo | Qué es |
| --- | --- |
| `LEEME.md` | El reto completo |
| `01_datos.ipynb`, `02_baseline.ipynb` | Notebooks ejecutados, con gráficos |
| `variables.py` | El objetivo (qué cuenta como baja) y las 23 variables del baseline |
| `baseline.py` | El modelo a superar |
| `estilo.py` | Estilo de los gráficos |
| `validacion.csv` | Comparación real frente a sintético por comercio |
| `datos/` | `precios_diarios.parquet`, `productos.csv`, `comercios.csv` y `calendario.csv` |

Los meses de prueba (julio a diciembre de 2025) no están aquí: con ellos se evalúan los modelos entregados.
