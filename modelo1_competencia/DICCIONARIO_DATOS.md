# Diccionario de datos: próximo movimiento de precio de la competencia

Todos los datos son **sintéticos**: ningún precio, producto ni comercio es real. Los precios están en dólares con IVA. Una **serie** es una combinación producto × comercio.

## `datos/precios_diarios.parquet`

Precio diario de cada producto en cada comercio, del 01/01/2023 al 30/06/2025. Una fila por fecha, comercio y producto (3.616 series: no todo producto está en todos los comercios). **3.297.792 filas.**

| Columna | Tipo | Descripción | Rango o valores | Vacíos | Ejemplo |
| --- | --- | --- | --- | --- | --- |
| `fecha` | fecha | Día de la lectura del precio. | 01/01/2023 a 30/06/2025 |  | 2023-01-01 |
| `comercio_id` | texto | Código del comercio (C01 a C13). Se une con comercios.csv. | 13 valores distintos |  | C03 |
| `producto_id` | texto | Código del producto (P00001 a P01500). Se une con productos.csv. | 1.500 valores distintos |  | P00001 |
| `precio_vigente` | decimal | Precio que cobra el comercio ese día, con IVA. Vacío si ese día no se pudo leer la web (~2 % de los días, como en un scraping real). | 0,09 a 386.205,97 | 2% | 22,31 |
| `precio_normal` | decimal | Precio tachado o regular, con IVA. Sin oferta suele ser igual a precio_vigente; en comercios con tachado permanente siempre es mayor. | 0,09 a 386.205,97 | 2% | 22,31 |
| `en_oferta` | booleano | Verdadero si el precio vigente está bajo el normal por una oferta. | 13% verdadero | 2% | False |
| `disponible` | booleano | Verdadero si el producto tenía stock ese día. | 90% verdadero | 2% | True |

## `datos/productos.csv`

Un producto por fila. **1.500 filas.**

| Columna | Tipo | Descripción | Rango o valores | Vacíos | Ejemplo |
| --- | --- | --- | --- | --- | --- |
| `producto_id` | texto | Código del producto. | 1.500 valores distintos |  | P00001 |
| `division` | texto | División comercial del producto (ELECTRO, HOGAR, PAPELERIA & REGALERIA, JUGUETES, MASCOTAS, etc.). Se cruza con la columna divisiones del calendario. | CALZADO, ELECTRO, HOGAR, INFANTIL, JUGUETES, MASCOTAS, MUEBLES, NAVIDAD, PAPELERIA & REGALERIA, SALUD |  | HOGAR |

## `datos/comercios.csv`

Un comercio por fila. **13 filas.**

| Columna | Tipo | Descripción | Rango o valores | Vacíos | Ejemplo |
| --- | --- | --- | --- | --- | --- |
| `comercio_id` | texto | Código del comercio. | 13 valores distintos |  | C01 |
| `tipo` | texto | Tipo de comercio (electro con crédito, departamental, ferretería y hogar, hipermercado, etc.). | departamental, electro con credito, ferreteria y hogar, hipermercado, hogar, moda y hogar, papeleria y hogar, tecnologia |  | hipermercado |
| `tachado_permanente` | booleano | Verdadero si el comercio siempre muestra un precio tachado más alto ("doble precio"): en él, estar en oferta no significa una rebaja real. | 15% verdadero |  | False |

## `datos/calendario.csv`

Un día de evento comercial por fila, hasta el 31/12/2025. Se conoce de antemano, así que se puede usar para predecir. **435 filas.**

| Columna | Tipo | Descripción | Rango o valores | Vacíos | Ejemplo |
| --- | --- | --- | --- | --- | --- |
| `fecha` | fecha | Día del evento. | 15/03/2023 a 31/12/2025 |  | 2023-11-17 |
| `evento` | texto | Nombre del evento (Black Friday + Cyber Monday, Navidad, Regreso a clases Costa, etc.). | Black Friday + Cyber Monday, Black Week, Cyber Days, Dia de la Madre, Dia del Padre, Liquidacion de fin de año, Liquidacion de medio año, Navidad, Regreso a clases Costa, Regreso a clases Sierra |  | Black Week |
| `divisiones` | texto | Divisiones a las que afecta, separadas por coma, o TODAS. | CALZADO,HOGAR,INFANTIL,MUEBLES, ELECTRO, ELECTRO,HERRAMIENTAS Y MANTENIMIENTO, ELECTRO,HOGAR,MUEBLES, JUGUETES,ELECTRO,HOGAR,NAVIDAD, PAPELERIA & REGALERIA,INFANTIL, TODAS |  | TODAS |

## `datos/tabla_series.csv`

**Parte 1 (clustering).** Una fila por serie (producto × comercio), con su comportamiento de precio en el entrenamiento (01/01/2023 al 31/12/2024). La arma `tablas.py` desde precios_diarios.parquet; es un punto de partida. **3.616 filas.**

| Columna | Tipo | Descripción | Rango o valores | Vacíos | Ejemplo |
| --- | --- | --- | --- | --- | --- |
| `comercio_id` | texto | Código del comercio. | 13 valores distintos |  | C01 |
| `producto_id` | texto | Código del producto. | 1.500 valores distintos |  | P00003 |
| `division` | texto | División comercial del producto. | CALZADO, ELECTRO, HOGAR, INFANTIL, JUGUETES, MASCOTAS, MUEBLES, NAVIDAD, PAPELERIA & REGALERIA, SALUD |  | PAPELERIA & REGALERIA |
| `precio_mediano` | decimal | Precio vigente mediano de la serie, con IVA. | 0,11 a 11.948,31 |  | 11,94 |
| `cambios_por_mes` | decimal | Cambios de precio por mes (días en que el precio cambió más de 0,5 % frente al día anterior × 30 / días). | 0,00 a 6,28 |  | 1,27 |
| `parte_dias_en_oferta` | decimal | Parte de los días en que la serie estuvo en oferta. | 0,00 a 0,76 |  | 0,18 |
| `ofertas_por_año` | decimal | Ofertas que empezaron por año. | 0,00 a 37,53 |  | 5,50 |
| `dias_por_oferta` | decimal | Días en oferta divididos para las ofertas que empezaron (duración media; 0 si nunca tuvo oferta). | 0,00 a 26,00 |  | 11,64 |
| `descuento_medio_oferta` | decimal | Descuento medio frente al precio normal en los días en oferta. Vacío si nunca tuvo oferta. | 0,03 a 0,77 | 10% | 0,37 |
| `bajas_5pct_por_año` | decimal | Días por año en que el precio bajó 5 % o más frente al día anterior. | 0,00 a 30,02 |  | 5,00 |
| `parte_bajas_en_evento` | decimal | De esas bajas, qué parte cayó en un día con evento del calendario que afecta a la división del producto. Vacío si no tuvo bajas. | 0,00 a 1,00 | 7% | 0,40 |
| `parte_dias_sin_stock` | decimal | Parte de los días sin stock. | 0,00 a 0,64 |  | 0,55 |

## `datos/tabla_clasificacion.parquet`

**Parte 2 (clasificación).** La tabla lista para entrenar: una fila por serie y día, con las 23 variables del baseline (calculadas solo con información hasta ese día, más el calendario) y las dos etiquetas. Trae una de cada 7 fechas de cada serie, con un desfase propio por serie para que estén todos los días de la semana. La arma `tablas.py`. **459.611 filas.**

| Columna | Tipo | Descripción | Rango o valores | Vacíos | Ejemplo |
| --- | --- | --- | --- | --- | --- |
| `fecha` | fecha | Día *t* de la predicción. | 01/01/2023 a 26/06/2025 |  | 2023-01-01 |
| `corte` | texto | entrenamiento (2023–2024) o validacion (enero a junio de 2025). | entrenamiento, validacion |  | entrenamiento |
| `comercio_id` | texto | Código del comercio. | 13 valores distintos |  | C01 |
| `producto_id` | texto | Código del producto. | 1.500 valores distintos |  | P00003 |
| `comercio_cod` | entero | Código numérico del comercio (C01 = 0, C02 = 1…). Es una categoría, no un número. | 0 a 12 |  | 0 |
| `division_cod` | entero | Código numérico de la división, en orden alfabético. Es una categoría. | 0 a 9 |  | 8 |
| `tachado` | entero | 1 si el comercio tiene tachado permanente (doble precio). | 0 a 1 |  | 0 |
| `desc_actual` | decimal | Descuento de hoy: 1 − precio_vigente / precio_normal. Vacío si hoy no hubo lectura. | 0,00 a 0,77 |  | 0,00 |
| `en_oferta_hoy` | decimal | 1 si hoy está en oferta. Vacío si hoy no hubo lectura. | 0,00 a 1,00 |  | 0,00 |
| `cambio_1d` | decimal | Variación del último precio leído frente al de 1 día antes. | -0,72 a 2,80 | 0% |  |
| `cambio_7d` | decimal | Lo mismo frente a 7 días antes. | -0,73 a 2,79 | 1% |  |
| `cambio_30d` | decimal | Lo mismo frente a 30 días antes. | -0,74 a 3,55 | 3% |  |
| `vs_max_30d` | decimal | Precio frente al máximo de los últimos 30 días (0 = está en el máximo). | -0,74 a 0,00 |  | 0,00 |
| `vs_min_90d` | decimal | Precio frente al mínimo de los últimos 90 días (0 = está en el mínimo). | 0,00 a 5,91 |  | 0,00 |
| `dias_sin_cambio` | entero | Días seguidos sin un cambio de precio de más de 0,5 %. | 0 a 906 |  | 0 |
| `ofertas_90d` | decimal | Días en oferta en los últimos 90. | 0,00 a 83,00 |  | 0,00 |
| `inicios_oferta_365d` | decimal | Ofertas que empezaron en los últimos 365 días. | 0,00 a 42,00 |  | 0,00 |
| `bajas_prod_7d` | decimal | Bajas de 5 % o más del mismo producto en todos los comercios en los últimos 7 días (incluye este comercio). | 0,00 a 9,00 |  | 0,00 |
| `bajas_otros_7d` | decimal | Lo mismo, sin contar este comercio: si otro comercio ya bajó. | 0,00 a 8,00 |  | 0,00 |
| `vs_mediana_comercios` | decimal | Precio frente a la mediana del mismo producto en los comercios que lo venden ese día. | -0,99 a 108,36 |  | -0,00 |
| `n_comercios` | entero | Comercios que venden el producto ese día. | 1 a 9 |  | 2 |
| `evento_activo` | entero | 1 si hoy hay algún evento del calendario (de cualquier división). | 0 a 1 |  | 0 |
| `dias_a_evento` | decimal | Días hasta el próximo día con evento (tope 90). | 0,00 a 90,00 |  | 73,00 |
| `dias_a_black_friday` | entero | Días hasta el próximo Black Friday. | 0 a 370 |  | 327 |
| `dia_semana` | entero | Día de la semana: 0 = lunes, 6 = domingo. | 0 a 6 |  | 6 |
| `dia_mes` | entero | Día del mes. | 1 a 31 |  | 1 |
| `mes` | entero | Mes (1 a 12). | 1 a 12 |  | 1 |
| `baja_7d` | decimal | **Etiqueta de la tarea A:** 1 si el precio baja al menos 5 % frente al de hoy en algún día de los próximos 7. | 0,00 a 1,00 |  | 0,00 |
| `baja_1d` | decimal | **Etiqueta de la tarea B:** 1 si baja al menos 5 % mañana. Vacío si mañana no hubo lectura. | 0,00 a 1,00 | 2% | 0,00 |

## `validacion.csv`

Comparación por comercio entre lo medido en las webs reales (22/10 al 09/11/2026) y la sintética en la misma ventana de 2025. Sufijo _real = medido; _sint = sintético. **13 filas.**

| Columna | Tipo | Descripción | Rango o valores | Vacíos | Ejemplo |
| --- | --- | --- | --- | --- | --- |
| `comercio` | texto | Código del comercio. | 13 valores distintos |  | C01 |
| `cambio_diario_real` | decimal | Probabilidad de que el precio cambie de un día al siguiente, medida en la web real. | 0,00 a 0,04 |  | 0,01 |
| `cambio_diario_sint` | decimal | Lo mismo en la sintética. | 0,01 a 0,09 |  | 0,02 |
| `bajas_en_cambios_real` | decimal | De los cambios de precio, qué parte fueron bajas (real). | 0,01 a 0,69 |  | 0,12 |
| `bajas_en_cambios_sint` | decimal | Lo mismo en la sintética. | 0,40 a 0,62 |  | 0,48 |
| `en_oferta_real` | decimal | Parte del catálogo en oferta (real). | 0,00 a 1,00 |  | 0,04 |
| `en_oferta_sint` | decimal | Lo mismo en la sintética. | 0,04 a 1,00 |  | 0,08 |
| `descuento_real` | decimal | Descuento mediano de las ofertas frente al precio normal (real). | 0,00 a 0,53 |  | 0,15 |
| `descuento_sint` | decimal | Lo mismo en la sintética. | 0,08 a 0,50 |  | 0,15 |

**Variable objetivo de la parte 2** (viene lista en tabla_clasificacion.parquet como `baja_7d` y `baja_1d`; para todos los días la calcula `objetivo()` en `variables.py`): vale 1 si el precio más bajo de los próximos días de la ventana es menor o igual al 95 % del precio_vigente de hoy, aunque luego vuelva a subir. Ventana de 7 días en la tarea A (`HORIZONTE=7`) y de 1 día en la B (`HORIZONTE=1`). Queda vacía si hoy no hay precio o si la ventana tiene pocas lecturas (menos de 4 en la A; en la B, si falta la de mañana).

**Parte 1:** los grupos no vienen en los datos. Se entregan en un CSV con `comercio_id`, `producto_id` y `grupo` (como `grupos_baseline.csv`, que deja `baseline_clusters.py`).
