# Diccionario de datos: efecto del cambio de precio en la venta y el margen

Todos los datos son **sintéticos**: ningún SKU, precio, costo ni venta es real. Los precios y costos están en dólares **sin IVA**. Las semanas empiezan el lunes.

## `datos/ventas_semanales.parquet`

Venta semanal de cada SKU, del 02/01/2023 al 30/06/2025. Un SKU aparece solo mientras está en el catálogo. **87.389 filas.**

| Columna | Tipo | Descripción | Rango o valores | Vacíos | Ejemplo |
| --- | --- | --- | --- | --- | --- |
| `semana` | fecha | Lunes de la semana. | 02/01/2023 a 30/06/2025 |  | 2023-01-30 |
| `sku` | texto | Código del SKU (S00001 a S01200). Se une con skus.csv. | 1.200 valores distintos |  | S00001 |
| `precio` | decimal | Precio efectivo cobrado en la semana, sin IVA (incluye descuentos en caja). | 0,87 a 7.634,76 |  | 224,00 |
| `precio_regular` | decimal | Precio sin promoción, sin IVA. | 1,09 a 7.046,47 |  | 269,18 |
| `en_promocion` | booleano | Verdadero si la semana tuvo promoción o liquidación. | 30% verdadero |  | True |
| `precio_competencia` | decimal | Precio del mismo producto en la competencia, en la misma unidad que precio. Tiene sus propias promociones. | 0,83 a 8.308,25 |  | 289,92 |
| `unidades` | entero | Unidades vendidas en la semana, en todas las tiendas. | 0 a 1.722 |  | 3 |
| `costo_unitario` | decimal | Costo del SKU sin IVA. | 0,64 a 4.413,57 |  | 173,21 |

## `datos/skus.csv`

Un SKU por fila. **1.200 filas.**

| Columna | Tipo | Descripción | Rango o valores | Vacíos | Ejemplo |
| --- | --- | --- | --- | --- | --- |
| `sku` | texto | Código del SKU. | 1.200 valores distintos |  | S00001 |
| `division` | texto | División comercial (ELECTRO, HOGAR, JUGUETES, MUEBLES, NAVIDAD). | ELECTRO, HOGAR, JUGUETES, MUEBLES, NAVIDAD |  | ELECTRO |
| `categoria` | texto | Categoría dentro de la división, con código (ELE-03, HOG-07…). | 39 valores distintos |  | ELE-03 |

## `datos/calendario.csv`

Una semana por fila. **157 filas.**

| Columna | Tipo | Descripción | Rango o valores | Vacíos | Ejemplo |
| --- | --- | --- | --- | --- | --- |
| `semana` | fecha | Lunes de la semana. | 02/01/2023 a 29/12/2025 |  | 2023-01-02 |
| `semana_del_año` | entero | Número de semana ISO (1 a 53). Sirve para la estacionalidad. | 1 a 52 |  | 1 |

## `datos/escenarios_prueba.csv`

Los 600 casos de la tarea 2, cada uno con 4 cambios de precio (2.400 filas), en semanas de la prueba (julio a diciembre de 2025). **2.400 filas.**

| Columna | Tipo | Descripción | Rango o valores | Vacíos | Ejemplo |
| --- | --- | --- | --- | --- | --- |
| `caso` | entero | Número del caso (0 a 599). Un caso = un SKU en una semana. | 0 a 599 |  | 0 |
| `sku` | texto | Código del SKU. | 297 valores distintos |  | S00183 |
| `semana` | fecha | Semana en la que se aplicaría el cambio. | 07/07/2025 a 29/12/2025 |  | 2025-12-01 |
| `precio_actual` | decimal | Precio antes del cambio, sin IVA. | 1,22 a 6.298,40 |  | 4,28 |
| `cambio` | decimal | Cambio propuesto: −0,15, −0,05, +0,05 o +0,15 (−15 % a +15 %). | -0,15 a 0,15 |  | -0,15 |
| `precio_propuesto` | decimal | precio_actual × (1 + cambio). | 1,04 a 7.243,16 |  | 3,64 |
| `costo_unitario` | decimal | Costo del SKU sin IVA, para calcular si conviene: contribución = unidades × (precio − costo). | 0,64 a 3.589,10 |  | 1,76 |

## `validacion.csv`

Comparación por división entre lo medido en la venta real y la sintética, con el mismo método. Sufijo _real = medido; _sint = sintético. **5 filas.**

| Columna | Tipo | Descripción | Rango o valores | Vacíos | Ejemplo |
| --- | --- | --- | --- | --- | --- |
| `division` | texto | División comercial. | ELECTRO, HOGAR, JUGUETES, MUEBLES, NAVIDAD |  | ELECTRO |
| `elasticidad_obs_real` | decimal | Elasticidad medida tal cual (log-log) en la venta real: sale sesgada a propósito del reto. | -1,06 a 1,83 |  | -0,75 |
| `elasticidad_obs_sint` | decimal | Lo mismo en la sintética. | -2,09 a -0,95 |  | -0,98 |
| `elast_sku_mediana_real` | decimal | Mediana de la elasticidad medida SKU por SKU (real). | -2,71 a 1,06 |  | -0,78 |
| `elast_sku_mediana_sint` | decimal | Lo mismo en la sintética. | -2,39 a -0,16 |  | -0,96 |
| `elasticidad_VERDADERA_sint` | decimal | Elasticidad promedio con que se simuló la división. | -2,04 a -0,79 |  | -0,79 |
| `promo_real` | decimal | Parte de las semanas en promoción (real). | 0,19 a 0,53 |  | 0,34 |
| `promo_sint` | decimal | Lo mismo en la sintética. | 0,21 a 0,56 |  | 0,34 |
| `prof_real` | decimal | Profundidad media de la promoción (real). | 0,13 a 0,27 |  | 0,13 |
| `prof_sint` | decimal | Lo mismo en la sintética. | 0,16 a 0,29 |  | 0,16 |
| `semanas_con_venta_real` | decimal | Parte de las semanas con venta (ciclo de vida, real). | 0,17 a 0,59 |  | 0,26 |
| `semanas_con_venta_sint` | decimal | Lo mismo en la sintética. | 0,21 a 0,71 |  | 0,31 |
| `unidades_log_real` | decimal | Nivel de venta: promedio del logaritmo de unidades semanales (real). | 1,38 a 3,72 |  | 1,38 |
| `unidades_log_sint` | decimal | Lo mismo en la sintética. | 1,52 a 3,35 |  | 1,52 |
| `corr_estacionalidad` | decimal | Correlación entre la estacionalidad semanal real y la sintética. | 0,82 a 0,98 |  | 0,87 |

**Qué se predice** (no viene en los archivos): en la tarea 1, `unidades` de la semana *t* con el precio planificado para *t* (todo lo demás solo hasta *t − 1*). En la tarea 2, para cada fila de escenarios_prueba.csv, `cambio_unidades` (por ejemplo −0,12 = 12 % menos unidades) y `conviene` (si sube la contribución).
