# Reto: ¿qué pasa con la venta y el margen si cambio el precio?

Datos sintéticos para Coding Bootcamps de ESPOL. Preparado por el equipo de inteligencia de negocios de Pycca, noviembre de 2026.

**Para empezar:** abre los notebooks `01_datos.ipynb` (los datos y la trampa de la elasticidad) y `02_baseline.ipynb` (las tareas, las métricas, el baseline y cómo se entregan los escenarios). Vienen ejecutados, con gráficos y resultados; se pueden volver a correr con `pip install pandas pyarrow scikit-learn matplotlib jupyter`.

## El problema de negocio

Pycca cambia precios cada semana: iguala a la competencia, hace promociones y ajusta por margen. Antes de enviar los precios al punto de venta, el líder de categoría necesita saber **qué le pasará a la venta y al margen de cada SKU** si cambia su precio. Así decide qué ajustes convienen y cuáles no.

Hay una trampa: en los datos de venta, las bajas de precio coinciden con otras cosas que también mueven la venta:
- la publicidad de las promociones;
- la temporada (Navidad, Black Friday);
- la liquidación de productos que ya están saliendo del catálogo;
- lo que hace la competencia.

Si se mide la relación precio–venta "tal cual", la elasticidad sale equivocada. El reto es separar el efecto del precio de todo lo demás.

## Los datos (carpeta `datos/`)

**Son sintéticos.** Ningún SKU, precio ni venta es real. Los datos están **calibrados con lo real**: se midió la venta semanal de los 3.000 SKU más vendidos de Pycca (2023–2026) y el simulador reproduce sus agregados por división.

| Archivo | Qué tiene |
|---|---|
| `ventas_semanales.parquet` | Una fila por SKU y semana con venta, del 02/01/2023 al **30/06/2025**. Un SKU aparece solo mientras está en el catálogo. |
| `skus.csv` | `sku`, `division` (Electro, Hogar, Juguetes, Muebles, Navidad) y `categoria` |
| `calendario.csv` | `semana` y `semana_del_año` |
| `escenarios_prueba.csv` | Los 600 casos de la tarea 2: SKU, semana, precio actual, precio propuesto (−15 %, −5 %, +5 %, +15 %) y costo |

Columnas de `ventas_semanales.parquet`:

| Columna | Descripción |
|---|---|
| `semana`, `sku` | La serie (semana que empieza el lunes) |
| `precio` | Precio efectivo cobrado en la semana, sin IVA (incluye descuentos en caja) |
| `precio_regular` | Precio sin promoción |
| `en_promocion` | Semana con promoción o liquidación |
| `precio_competencia` | Precio del mismo producto en la competencia (índice) |
| `unidades` | Unidades vendidas en todas las tiendas |
| `costo_unitario` | Costo sin IVA |

### Qué tan parecido es a lo real (`validacion.csv`)

Por división, la sintética reproduce:
- **Frecuencia de promociones:** 21–56 % de las semanas.
- **Profundidad de las promociones:** 16–29 %.
- **Estacionalidad semanal:** correlación de 0,82 a 0,98 con la real.
- **Nivel de venta y parte de semanas con venta:** el ciclo de vida de los SKU.
- **Elasticidad mediana medida SKU por SKU**, cercana a la real en Electro, Juguetes y Muebles. La excepción es Navidad: en lo real sale positiva, por el remate de enero.

**Supuestos (no medibles sin experimentos):**
- la publicidad de la promoción suma venta además del precio;
- el precio de la competencia mueve la venta de Pycca (elasticidad cruzada);
- en 2025 ~40 % de los SKU tuvieron un cambio de precio permanente de −15 % a +15 % (los ajustes del motor de precios).

## Las dos tareas

**Cortes de tiempo** (siempre por fecha, nunca al azar):
- Entrenamiento: enero 2023 a diciembre 2024.
- Validación: enero a junio 2025.
- **Prueba (no incluida):** julio a diciembre 2025. Con ella Pycca evaluará los modelos.

| Tarea | Pregunta | Métrica |
|---|---|---|
| **1. Pronóstico** | ¿Cuántas unidades venderá el SKU la semana *t*, con el precio planificado para *t*? (el precio de la semana se conoce antes; todo lo demás, solo hasta *t − 1*) | **WAPE** = error absoluto / unidades reales, y sesgo |
| **2. Escenarios** | Para cada caso de `escenarios_prueba.csv`: ¿cuánto cambian las unidades con el precio propuesto? ¿Conviene el cambio, es decir, sube la contribución = unidades × (precio − costo)? | **Error medio del cambio % de unidades** (principal) y acierto en "conviene" |

La tarea 2 es la que más le importa al negocio. Pycca conoce la respuesta exacta de cada escenario, porque los datos son simulados con elasticidades conocidas por SKU. Por eso se puede medir quién estima mejor el efecto del precio, no solo quién pronostica mejor.

## Baseline a superar (`baseline.py`)

El baseline usa **una elasticidad por división, medida tal cual**: log-log con efectos fijos de SKU y de semana. No separa la promoción, la temporada, la liquidación ni la competencia.

| | Validación | Prueba |
|---|---|---|
| Pronóstico: WAPE | 52,2 % | 52,3 % |
| Escenarios: error medio del cambio de unidades | — | **5,8 puntos** |
| Escenarios: acierto en "conviene" | — | 97,9 % |

**Cómo leer estas cifras:**
- Con márgenes de 35–45 % y elasticidades cercanas a −1, subir el precio casi siempre sube la contribución en el corto plazo. Por eso "conviene" se acierta fácil y **lo que separa un buen modelo de uno regular es el error en el cambio de unidades**.
- La venta semanal por SKU es chica y tiene mucho ruido: ningún modelo baja mucho de ~47 % de WAPE.

**Dónde hay margen:**
- Separar el efecto de la promoción del efecto del precio.
- Controlar la estacionalidad por división y la competencia.
- No confundir la liquidación de fin de vida con elasticidad.
- Estimar una elasticidad **por SKU**, acercándola a la de su categoría o división cuando el SKU tiene pocos datos (modelos jerárquicos o bayesianos).

## Qué esperamos del bootcamp

1. Un modelo que baje el **error del cambio de unidades** en los escenarios frente al baseline, y que no empeore el WAPE.
2. Para cada caso de `escenarios_prueba.csv`: `cambio_unidades` (por ejemplo, −0,12 = 12 % menos unidades) y `conviene` (sí o no).
3. La **elasticidad estimada por SKU**, con su incertidumbre si es posible.
4. Una explicación simple de cómo separan el precio de la promoción y la temporada.

## Cómo correr el baseline

```
pip install pandas pyarrow
python baseline.py
```

Con este paquete se evalúa solo el pronóstico en validación, porque la prueba la guarda Pycca.
