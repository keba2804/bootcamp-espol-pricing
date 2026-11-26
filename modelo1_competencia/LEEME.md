# Reto: anticipar el próximo movimiento de precio de la competencia

Datos sintéticos para Coding Bootcamps de ESPOL. Preparado por el equipo de inteligencia de negocios de Pycca, noviembre de 2026.

**Para empezar:** abre los notebooks, que vienen ejecutados, con gráficos y resultados:
1. `01_datos.ipynb`: qué hay en los datos y qué patrones tienen.
2. `02_clusters.ipynb`: **parte 1**, agrupar las series (clustering).
3. `03_clasificacion.ipynb`: **parte 2**, predecir la baja (clasificación).

Se pueden volver a correr con `pip install pandas pyarrow scikit-learn matplotlib jupyter`.

## El problema de negocio

Pycca es una cadena de retail ecuatoriana (hogar, electro, papelería, juguetes, mascotas). Compite con comercios que publican sus precios en la web y los cambian todo el tiempo: ofertas de fin de semana, inicio de mes, Black Friday, Navidad, liquidaciones.

Hoy Pycca **reacciona** cuando el competidor ya bajó el precio. Queremos **anticiparnos**: saber qué producto va a bajar, en qué comercio y **en qué fecha**, para preparar el precio antes.

## El reto en dos partes

| | Parte 1 · Clustering | Parte 2 · Clasificación |
|---|---|---|
| Pregunta | ¿Qué tipo de serie es cada una? | ¿Bajará el precio al menos 5 %? |
| Qué se hace | Agrupar las 3.616 series (producto × comercio) según cómo se mueve su precio. Sin etiquetas: el número de grupos lo deciden ustedes | Clase 1 si baja, 0 si no, en dos horizontes: próximos 7 días y mañana |
| Tabla lista | `datos/tabla_series.csv` | `datos/tabla_clasificacion.parquet` |
| Métodos | K-means, jerárquico, DBSCAN, mezclas gaussianas… | Regresión logística, árboles, random forest, boosting… |
| Se califica con | ARI frente a perfiles ocultos | AP en la prueba oculta |

Las dos partes se conectan: el grupo de cada serie (parte 1) puede entrar como una variable más del clasificador (parte 2).

## Los datos (carpeta `datos/`)

**Son sintéticos.** Ningún precio, producto ni comercio es real. Los datos están **calibrados con lo real**: medimos cómo se mueven los precios de 13 competidores en lecturas reales de sus sitios web (octubre y noviembre de 2026) y simulamos 3 años diarios que reproducen esas tasas. Comercios y productos van con códigos (`C01`, `P00001`). Cada columna está descrita en `DICCIONARIO_DATOS.md`.

| Archivo | Qué tiene |
|---|---|
| `precios_diarios.parquet` | Una fila por día × comercio × producto, del 01/01/2023 al **30/06/2025**. Unos 3,3 millones de filas y 3.616 series (producto × comercio). |
| `productos.csv` | `producto_id` y `division` (Electro, Hogar, Papelería, Juguetes, Mascotas…). |
| `comercios.csv` | `comercio_id`, `tipo` (electro con crédito, departamental, ferretería y hogar…) y `tachado_permanente`, que indica si siempre muestra un precio tachado más alto como "doble precio". |
| `calendario.csv` | Días de eventos comerciales (Black Friday, Cyber, Navidad, liquidaciones, Día de la Madre/Padre, regreso a clases Costa y Sierra), con las divisiones afectadas. Llega hasta **diciembre de 2025**: el calendario se conoce de antemano y se puede usar para predecir. |
| `tabla_series.csv` | **Parte 1.** Una fila por serie con su comportamiento en el entrenamiento (2023–2024): cambios por mes, días en oferta, ofertas por año, duración y descuento de las ofertas, bajas por año, parte de las bajas en eventos y días sin stock. |
| `tabla_clasificacion.parquet` | **Parte 2.** La tabla `X, y`: una fila por serie y día (una de cada 7 fechas), con las 23 variables del baseline y las etiquetas `baja_7d` y `baja_1d`. |

Las dos tablas las arma `tablas.py` a partir de los cuatro primeros archivos; se pueden rehacer o ampliar.

### Cómo se comportan los comercios en la simulación

- **Medido en lo real**, por comercio:
  - cuánto cambia el precio por día;
  - qué parte de los cambios son bajas y de cuánto;
  - qué parte del catálogo está en oferta, con qué descuento y cuánto duran las ofertas;
  - si usa tachado permanente;
  - en cuántos comercios está cada producto y cuánto varía su precio entre comercios.
- **Supuestos** (con dos semanas de lecturas reales no se puede medir un año; están puestos para parecerse al retail ecuatoriano y para que haya algo que aprender):
  - **Calendario anual:** cada evento tiene una fuerza distinta según la división.
  - **Ritmo de cada comercio:** fin de semana, quincena o inicio de mes.
  - **Ofertas de duración fija** por comercio, como un folleto.
  - **Presión competitiva:** un comercio que quedó más de 15 % sobre el más barato baja con más probabilidad.
  - **Líder y seguidores:** en cada producto, algunos comercios copian la baja de otro con un rezago fijo de días.
  - **Tipos de serie:** dentro de un mismo comercio, no todas las series se comportan igual. Es lo que busca la parte 1.

### Qué tan parecido es a lo real (`validacion.csv`)

Para cada comercio se comparan las tasas medidas en la web real (22/10–09/11/2026) con las de la sintética en la misma ventana de 2025:

| | Correlación real vs sintética (13 comercios) |
|---|---|
| Probabilidad diaria de cambio de precio | 0,85 |
| Parte de productos en oferta | 0,98 |
| Descuento mediano de las ofertas | 0,90 |
| Contagio: si otro comercio bajó el mismo producto, ¿baja este? | real 9,0 % vs 6,0 %; sintético 19,2 % vs 7,1 % (más marcado a propósito: es el supuesto de líder y seguidores) |

## Parte 1: agrupar las series (clustering)

No todas las series se comportan igual: unas casi nunca cambian de precio, otras viven en oferta, otras solo bajan en ciertas épocas, otras siguen lo que hace otro comercio. Si Pycca sabe qué tipo de serie es cada una, puede vigilarla de forma distinta.

- **La tarea:** agrupar las 3.616 series con un método no supervisado. Ustedes deciden cuántos grupos y con qué variables; `tabla_series.csv` es un punto de partida.
- **Cómo se evalúa:** el simulador le dio a cada serie un perfil de comportamiento que **no viene en los datos**. Pycca compara sus grupos con esos perfiles usando el **ARI** (índice de Rand ajustado): 0 es como agrupar al azar y 1 es recuperarlos exactamente. No importa cómo llamen a los grupos.
- **Baseline a superar (`baseline_clusters.py`):** K-means sobre las 8 variables de `tabla_series.csv`, estandarizadas, con el número de grupos elegido por el coeficiente de silueta. Obtiene un **ARI de 0,09**.
- **Una advertencia:** cada comercio tiene su propio nivel (unos siempre muestran un precio tachado, otros casi no hacen ofertas). Si sus grupos se parecen demasiado a los comercios, encontraron comercios, no tipos de serie. El notebook `02_clusters.ipynb` muestra cómo revisarlo.
- **Entrega:** un CSV con `comercio_id`, `producto_id` y `grupo` para las 3.616 series (como `grupos_baseline.csv`) y una descripción en palabras de cada grupo: qué hace ese tipo de serie y cómo conviene vigilarla.

## Parte 2: ¿bajará el precio? (clasificación)

Las dos tareas predicen una baja de **al menos 5 %** del precio vigente frente al de hoy. En `tabla_clasificacion.parquet` las etiquetas vienen listas; para todos los días, el objetivo está en `variables.py` (función `objetivo`) y el horizonte se elige con la variable de entorno `HORIZONTE`.

| Tarea | Etiqueta | Pregunta | Para qué le sirve a Pycca | Clase 1 |
|---|---|---|---|---|
| **A** (`HORIZONTE=7`, por defecto) | `baja_7d` | ¿Bajará en algún día de los **próximos 7**? | Lista semanal de productos a vigilar | ~8 % |
| **B** (`HORIZONTE=1`) | `baja_1d` | ¿Bajará **mañana**? | Saber la fecha exacta para preparar el precio a tiempo | ~1,2 % |

- **Cortes de tiempo** (siempre por fecha, nunca al azar):
  - Entrenamiento: 01/01/2023 a 31/12/2024.
  - Validación: 01/01/2025 a 30/06/2025.
  - **Prueba (no incluida):** 01/07/2025 a 24/12/2025, con Cyber Days, regreso a clases Sierra, Black Friday y Navidad. Con ella Pycca evaluará los modelos.
- **Regla de oro:** para predecir el día *t* solo se puede usar información hasta *t* y el calendario. Un modelo que mire el futuro no sirve en producción.

### Métricas

Las clases están desbalanceadas: un modelo que diga "nunca baja" acierta más del 90 % y no sirve.

- **AP** (área bajo la curva precision-recall). Es la principal.
- **AUC.**
- **Brier**, que mide qué tan bien calibradas están las probabilidades.
- **Precisión en el 5 % de mayor riesgo:** de las alertas más probables, ¿cuántas aciertan? Es la que más le importa al negocio. El notebook la muestra también como matriz de confusión.

### Baseline a superar (`baseline.py`)

`variables.py` arma 23 variables, solo con el pasado:
- historia del precio: descuento actual, cambios a 1, 7 y 30 días, días sin cambio, ofertas en los últimos 90 días;
- el mismo producto en otros comercios: bajas recientes y precio frente a la mediana;
- calendario general: días al próximo evento y a Black Friday, día de la semana y del mes.

`baseline.py` entrena un `HistGradientBoostingClassifier` (scikit-learn) con todos los días. Corre en unos 3 minutos en una laptop. El notebook `03_clasificacion.ipynb` compara además una regresión logística y un árbol de decisión sobre la tabla lista.

| Tarea | Modelo | Validación AP | Prueba AP | Prueba AUC | Prueba: precisión en el 5 % de mayor riesgo |
|---|---|---|---|---|---|
| A (7 días) | Regla: tasa histórica del comercio por mes | 0,130 | 0,171 | 0,679 | 25 % |
| A (7 días) | **Baseline** | **0,379** | **0,430** | **0,823** | **54 %** |
| B (mañana) | Regla | 0,022 | 0,029 | 0,680 | 4,1 % |
| B (mañana) | **Baseline** | **0,153** | **0,196** | **0,849** | **12,0 %** |

**Dónde hay margen de mejora:**
- **En la tarea B, sobre todo.** El simulador tiene patrones de fecha que el baseline casi no usa:
  - el rezago fijo con que un comercio copia la baja de otro;
  - la duración fija de las ofertas de cada comercio y cuándo vuelve a abrir la siguiente;
  - el calendario **por división**: un evento solo mueve a las divisiones que afecta;
  - la presión competitiva frente al comercio más barato.
- **El tipo de serie de la parte 1**, usado como variable. Con los grupos del baseline de clustering, la AP de la tarea A casi no cambia (0,433 frente a 0,430 en la prueba); con un agrupamiento mejor, sí sube.
- **En la tarea A, la mejora posible es menor.** En una ventana de 7 días, el "algo va a pasar" ya lo captura bien el baseline.

## Qué esperamos del bootcamp

1. **Parte 1:** grupos que superen al baseline en ARI, con una descripción de cada grupo.
2. **Parte 2:** modelos que superen al baseline en **AP** y en **precisión en el 5 % de mayor riesgo** en la prueba, en las dos tareas. La B es la más valiosa.
3. El código como una función `predecir(historia_hasta_t, calendario) -> probabilidad por serie`, para correrlo sobre la prueba oculta.
4. Una explicación simple de qué señales usa el modelo, para que el equipo comercial confíe en él.
5. Opcional: **cuánto** bajará (regresión), para preparar el precio exacto.

## Cómo correr los baselines

```
pip install pandas pyarrow scikit-learn
python baseline_clusters.py               # parte 1: deja grupos_baseline.csv
python baseline.py                        # parte 2, tarea A
set HORIZONTE=1 && python baseline.py     # parte 2, tarea B (Windows; en Linux/Mac: HORIZONTE=1 python baseline.py)
set GRUPOS=grupos_baseline.csv && python baseline.py   # tarea A usando el grupo como variable
```

`baseline.py` genera `resultados_baseline.json` (y `_h1.json` para la tarea B). Con este paquete se evalúa solo en validación, porque la prueba la guarda Pycca. Las cifras de validación pueden diferir un poco de la tabla: al cortar los datos el 30/06, los últimos días de junio quedan sin objetivo.
