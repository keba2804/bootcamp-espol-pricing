"""Arma las dos tablas listas del modelo 1, a partir de datos/ (y las deja ahi) (las mismas funciones de variables.py).

  tabla_series.csv            PARTE 1, clustering. Una fila por serie (producto x comercio) con su comportamiento de precio
                              en el entrenamiento (2023-2024). Es un punto de partida: se pueden calcular otras variables.
  tabla_clasificacion.parquet PARTE 2, clasificacion. Una fila por serie y dia, con las 23 variables del baseline y las dos
                              etiquetas (baja_7d, baja_1d). Trae una de cada 7 fechas de cada serie (cada serie con su propio
                              desfase, para que esten todos los dias de la semana), para que pese poco y corra en una laptop.
Uso: python tablas.py [carpeta_datos=datos]"""
import sys, time
from pathlib import Path
import numpy as np
import pandas as pd

import variables as V

AQUI = Path(__file__).resolve().parent
CARPETA = Path(sys.argv[1]) if len(sys.argv) > 1 else AQUI / 'datos'
CORTES = {'entrenamiento': ('2023-01-01', '2024-12-31'), 'validacion': ('2025-01-01', '2025-06-30'), 'prueba': ('2025-07-01', '2025-12-24')}
FIN_SERIES = CORTES['entrenamiento'][1]
S = ['comercio_id', 'producto_id']


def tabla_series(d, cal):
    """Comportamiento de cada serie en el entrenamiento: cuanto cambia, cuanto vive en oferta y cuando baja."""
    x = d[d.fecha <= FIN_SERIES].copy()
    g = x.groupby(S, sort=False)
    v = g.precio_vigente.ffill()
    x['cambio'] = v / v.groupby([x.comercio_id, x.producto_id]).shift(1) - 1
    x['cambia'] = x.cambio.abs() > 0.005
    x['baja5'] = x.cambio < -V.UMBRAL
    of = x.en_oferta.fillna(False).astype(bool)
    x['inicio'] = of & ~of.groupby([x.comercio_id, x.producto_id]).shift(1, fill_value=False)
    x['desc_oferta'] = (1 - x.precio_vigente / x.precio_normal).where(of)
    # el dia tiene un evento que afecta a la division del producto
    ev = cal.assign(divisiones=cal.divisiones.str.split(',')).explode('divisiones')
    con_ev = set(zip(ev.fecha, ev.divisiones))
    todas = set(ev.fecha[ev.divisiones == 'TODAS'])
    x['evento_div'] = [f in todas or (f, dv) in con_ev for f, dv in zip(x.fecha, x.division)]
    x['sin_stock'] = x.disponible.eq(False)
    g = x.groupby(S, sort=False)
    años = (pd.Timestamp(FIN_SERIES) - x.fecha.min()).days / 365.25
    t = pd.DataFrame({
        'division': g.division.first(),
        'precio_mediano': g.precio_vigente.median().round(2),
        'cambios_por_mes': (g.cambia.mean() * 30).round(3),
        'parte_dias_en_oferta': g.apply(lambda z: z.en_oferta.fillna(False).astype(bool).mean(), include_groups=False).round(4),
        'ofertas_por_año': (g.inicio.sum() / años).round(2),
        'dias_por_oferta': (g.apply(lambda z: z.en_oferta.fillna(False).astype(bool).sum(), include_groups=False)
                            / g.inicio.sum().clip(lower=1)).round(2),
        'descuento_medio_oferta': g.desc_oferta.mean().round(4),
        'bajas_5pct_por_año': (g.baja5.sum() / años).round(2),
        'parte_bajas_en_evento': (g.apply(lambda z: z.evento_div[z.baja5].mean() if z.baja5.any() else np.nan, include_groups=False)).round(4),
        'parte_dias_sin_stock': g.sin_stock.mean().round(4),
    }).reset_index()
    return t


def tabla_clasificacion(d, cal):
    d = d.copy()
    for nombre, h in (('baja_7d', 7), ('baja_1d', 1)):
        V.HORIZONTE = h
        d[nombre] = V.objetivo(d)
    X = V.variables(d, cal)
    X = X[X.baja_7d.notna()]
    X['corte'] = ''
    for k, (a, b) in CORTES.items():
        X.loc[(X.fecha >= a) & (X.fecha <= b), 'corte'] = k
    X = X[X.corte != '']
    # una de cada 7 fechas por serie, con un desfase propio de cada serie
    desfase = X.groupby(S, sort=False).ngroup() % 7
    dia = (X.fecha - pd.Timestamp('2023-01-01')).dt.days
    X = X[(dia + desfase) % 7 == 0]
    cols = ['fecha', 'corte', *S, *V.COLUMNAS, 'baja_7d', 'baja_1d']
    X = X[cols].reset_index(drop=True)
    for c in V.COLUMNAS:
        if X[c].dtype == 'float64':
            X[c] = X[c].astype('float32')
    return X


if __name__ == '__main__':
    t0 = time.time()
    d, cal = V.cargar(CARPETA)
    ts = tabla_series(d, cal)
    ts.to_csv(CARPETA / 'tabla_series.csv', index=False)
    print('tabla_series.csv', len(ts), 'series |', round(time.time() - t0), 's', flush=True)
    tc = tabla_clasificacion(d, cal)
    tc.to_parquet(CARPETA / 'tabla_clasificacion.parquet', index=False)
    print('tabla_clasificacion.parquet', len(tc), 'filas |', tc.groupby('corte').size().to_dict(), '|',
          round((CARPETA / 'tabla_clasificacion.parquet').stat().st_size / 1e6, 1), 'MB |', round(time.time() - t0), 's')
