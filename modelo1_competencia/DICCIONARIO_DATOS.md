# Diccionario de datos: próximo movimiento de precio de la competencia

Todos los datos son **sintéticos**: ningún precio, producto ni comercio es real. Los precios están en dólares con IVA. Una **serie** es una combinación producto × comercio.

## `datos/precios_diarios.parquet`

Precio diario de cada producto en cada comercio, del 01/01/2023 al 30/06/2025. Una fila por fecha, comercio y producto (3.616 series: no todo producto está en todos los comercios). **3.297.792 filas.**

| Columna | Tipo | Descripción | Rango o valores | Vacíos | Ejemplo |
| --- | --- | --- | --- | --- | --- |
| `fecha` | fecha | Día de la lectura del precio. | 01/01/2023 a 30/06/2025 |  | 2023-01-01 |
| `comercio_id` | texto | Código del comercio (C01 a C13). Se une con comercios.csv. | 13 valores distintos |  | C03 |
| `producto_id` | texto | Código del producto (P00001 a P01500). Se une con productos.csv. | 1.500 valores distintos |  | P00001 |
| `precio_vigente` | decimal | Precio que cobra el comercio ese día, con IVA. Vacío si ese día no se pudo leer la web (~2 % de los días, como en un scraping real). | 0,04 a 18.680,56 | 2% | 18,85 |
| `precio_normal` | decimal | Precio tachado o regular, con IVA. Sin oferta suele ser igual a precio_vigente; en comercios con tachado permanente siempre es mayor. | 0,11 a 18.680,56 | 2% | 22,31 |
| `en_oferta` | booleano | Verdadero si el precio vigente está bajo el normal por una oferta. | 13% verdadero | 2% | True |
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

## `validacion.csv`

Comparación por comercio entre lo medido en las webs reales (22/10 al 09/11/2026) y la sintética en la misma ventana de 2025. Sufijo _real = medido; _sint = sintético. **13 filas.**

| Columna | Tipo | Descripción | Rango o valores | Vacíos | Ejemplo |
| --- | --- | --- | --- | --- | --- |
| `comercio` | texto | Código del comercio. | 13 valores distintos |  | C01 |
| `cambio_diario_real` | decimal | Probabilidad de que el precio cambie de un día al siguiente, medida en la web real. | 0,00 a 0,04 |  | 0,01 |
| `cambio_diario_sint` | decimal | Lo mismo en la sintética. | 0,01 a 0,12 |  | 0,02 |
| `bajas_en_cambios_real` | decimal | De los cambios de precio, qué parte fueron bajas (real). | 0,01 a 0,69 |  | 0,12 |
| `bajas_en_cambios_sint` | decimal | Lo mismo en la sintética. | 0,38 a 0,64 |  | 0,41 |
| `en_oferta_real` | decimal | Parte del catálogo en oferta (real). | 0,00 a 1,00 |  | 0,04 |
| `en_oferta_sint` | decimal | Lo mismo en la sintética. | 0,04 a 1,00 |  | 0,06 |
| `descuento_real` | decimal | Descuento mediano de las ofertas frente al precio normal (real). | 0,00 a 0,53 |  | 0,15 |
| `descuento_sint` | decimal | Lo mismo en la sintética. | 0,05 a 0,49 |  | 0,16 |

**Variable objetivo** (no viene en los archivos; la calcula `objetivo()` en `variables.py`): vale 1 si el precio más bajo de los próximos días de la ventana es menor o igual al 95 % del precio_vigente de hoy, aunque luego vuelva a subir. Ventana de 7 días en la tarea A (`HORIZONTE=7`) y de 1 día en la B (`HORIZONTE=1`). Queda vacía si hoy no hay precio o si la ventana tiene pocas lecturas (menos de 4 en la A; en la B, si falta la de mañana).
