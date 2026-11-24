# Reto: anticipar el próximo movimiento de precio de la competencia

Datos sintéticos para Coding Bootcamps de ESPOL. Preparado por el equipo de inteligencia de negocios de Pycca, noviembre de 2026.

**Para empezar:** abre los notebooks `01_datos.ipynb` (qué hay en los datos y qué patrones tienen) y `02_baseline.ipynb` (la tarea, la métrica y el baseline). Vienen ejecutados, con gráficos y resultados; se pueden volver a correr con `pip install pandas pyarrow scikit-learn matplotlib jupyter`.

## El problema de negocio

Pycca es una cadena de retail ecuatoriana (hogar, electro, papelería, juguetes, mascotas). Compite con comercios que publican sus precios en la web y los cambian todo el tiempo: ofertas de fin de semana, inicio de mes, Black Friday, Navidad, liquidaciones.

Hoy Pycca **reacciona** cuando el competidor ya bajó el precio. Queremos **anticiparnos**: saber qué producto va a bajar, en qué comercio y **en qué fecha**, para preparar el precio antes.

## Los datos (carpeta `datos/`)

**Son sintéticos.** Ningún precio, producto ni comercio es real. Los datos están **calibrados con lo real**: medimos cómo se mueven los precios de 13 competidores en lecturas reales de sus sitios web (octubre y noviembre de 2026) y simulamos 3 años diarios que reproducen esas tasas. Comercios y productos van con códigos (`C01`, `P00001`).

| Archivo | Qué tiene |
|---|---|
| `precios_diarios.parquet` | Una fila por día × comercio × producto, del 01/01/2023 al **30/06/2025**. Unos 3,3 millones de filas y 3.616 series (producto × comercio). |
| `productos.csv` | `producto_id` y `division` (Electro, Hogar, Papelería, Juguetes, Mascotas…). |
| `comercios.csv` | `comercio_id`, `tipo` (electro con crédito, departamental, ferretería y hogar…) y `tachado_permanente`, que indica si siempre muestra un precio tachado más alto como "doble precio". |
| `calendario.csv` | Días de eventos comerciales (Black Friday, Cyber, Navidad, liquidaciones, Día de la Madre/Padre, regreso a clases Costa y Sierra), con las divisiones afectadas. Llega hasta **diciembre de 2025**: el calendario se conoce de antemano y se puede usar para predecir. |

Columnas de `precios_diarios.parquet`:

| Columna | Descripción |
|---|---|
| `fecha` | Día de la lectura |
| `comercio_id`, `producto_id` | La serie |
| `precio_vigente` | Precio que cobra el comercio ese día, con IVA. Vacío si ese día no se pudo leer la web (~2 %, como en un scraping real) |
| `precio_normal` | Precio tachado o regular |
| `en_oferta` | El precio vigente está bajo el normal por una oferta |
| `disponible` | Tenía stock ese día |

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

### Qué tan parecido es a lo real (`validacion.csv`)

Para cada comercio se comparan las tasas medidas en la web real (22/10–09/11/2026) con las de la sintética en la misma ventana de 2025:

| | Correlación real vs sintética (13 comercios) |
|---|---|
| Probabilidad diaria de cambio de precio | 0,80 |
| Parte de productos en oferta | 0,98 |
| Descuento mediano de las ofertas | 0,91 |
| Contagio: si otro comercio bajó el mismo producto, ¿baja este? | real 9,0 % vs 6,0 %; sintético 18,5 % vs 7,0 % (más marcado a propósito: es el supuesto de líder y seguidores) |

## Las dos tareas

Las dos predicen una baja de **al menos 5 %** del precio vigente frente al de hoy. El objetivo está en `variables.py`, en la función `objetivo`, y el horizonte se elige con la variable de entorno `HORIZONTE`.

| Tarea | Pregunta | Para qué le sirve a Pycca | Tasa de 1 |
|---|---|---|---|
| **A** (`HORIZONTE=7`, por defecto) | ¿Bajará en algún día de los **próximos 7**? | Lista semanal de productos a vigilar | ~9 % |
| **B** (`HORIZONTE=1`) | ¿Bajará **mañana**? | Saber la fecha exacta para preparar el precio a tiempo | ~1,3 % |

- **Cortes de tiempo** (siempre por fecha, nunca al azar):
  - Entrenamiento: 01/01/2023 a 31/12/2024.
  - Validación: 01/01/2025 a 30/06/2025.
  - **Prueba (no incluida):** 01/07/2025 a 24/12/2025, con Cyber Days, regreso a clases Sierra, Black Friday y Navidad. Con ella Pycca evaluará los modelos.
- **Regla de oro:** para predecir el día *t* solo se puede usar información hasta *t* y el calendario. Un modelo que mire el futuro no sirve en producción.

### Métricas

- **AP** (área bajo la curva precision-recall). Es la principal, porque los 1 son pocos.
- **AUC.**
- **Brier**, que mide qué tan bien calibradas están las probabilidades.
- **Precisión en el 5 % de mayor riesgo:** de las alertas más probables, ¿cuántas aciertan? Es la que más le importa al negocio.

## Baseline a superar (`baseline.py`)

`variables.py` arma 23 variables, solo con el pasado:
- historia del precio: descuento actual, cambios a 1, 7 y 30 días, días sin cambio, ofertas en los últimos 90 días;
- el mismo producto en otros comercios: bajas recientes y precio frente a la mediana;
- calendario general: días al próximo evento y a Black Friday, día de la semana y del mes.

`baseline.py` entrena un `HistGradientBoostingClassifier` (scikit-learn). Corre en unos 3 minutos en una laptop.

| Tarea | Modelo | Validación AP | Prueba AP | Prueba AUC | Prueba: precisión en el 5 % de mayor riesgo |
|---|---|---|---|---|---|
| A (7 días) | Regla: tasa histórica del comercio por mes | 0,155 | 0,214 | 0,715 | 30 % |
| A (7 días) | **Baseline** | **0,330** | **0,402** | **0,800** | **51 %** |
| B (mañana) | Regla | 0,023 | 0,033 | 0,704 | 4,6 % |
| B (mañana) | **Baseline** | **0,112** | **0,182** | **0,838** | **11,8 %** |

**Dónde hay margen de mejora:**
- **En la tarea B, sobre todo.** El simulador tiene patrones de fecha que el baseline casi no usa:
  - el rezago fijo con que un comercio copia la baja de otro;
  - la duración fija de las ofertas de cada comercio y cuándo vuelve a abrir la siguiente;
  - el calendario **por división**: un evento solo mueve a las divisiones que afecta;
  - la presión competitiva frente al comercio más barato.
- **En la tarea A, la mejora posible es menor.** En una ventana de 7 días, el "algo va a pasar" ya lo captura bien el baseline.

## Qué esperamos del bootcamp

1. Modelos que superen al baseline en **AP** y en **precisión en el 5 % de mayor riesgo** en la prueba, en las dos tareas. La B es la más valiosa.
2. El código como una función `predecir(historia_hasta_t, calendario) -> probabilidad por serie`, para correrlo sobre la prueba oculta.
3. Si es posible, **cuánto** bajará (regresión), para preparar el precio exacto.
4. Una explicación simple de qué señales usa el modelo, para que el equipo comercial confíe en él.

## Cómo correr el baseline

```
pip install pandas pyarrow scikit-learn
python baseline.py                  # tarea A
set HORIZONTE=1 && python baseline.py     # tarea B (Windows; en Linux/Mac: HORIZONTE=1 python baseline.py)
```

Genera `resultados_baseline.json` (y `_h1.json` para la tarea B). Con este paquete se evalúa solo en validación, porque la prueba la guarda Pycca. Las cifras de validación pueden diferir un poco de la tabla: al cortar los datos el 30/06, los últimos días de junio quedan sin objetivo.
