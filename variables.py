"""Variables (features) y objetivo del modelo 3. Todas usan solo informacion disponible hasta el dia t (sin mirar el futuro),
salvo el calendario comercial, que se conoce de antemano.

Objetivo: baja_7d = 1 si el precio vigente de esa serie (producto x comercio) baja al menos 5 % frente al de hoy en algun dia de
los proximos 7 (se exige precio leido hoy y al menos 4 lecturas en esos 7 dias)."""
import os

import numpy as np
import pandas as pd

UMBRAL = 0.05
HORIZONTE = int(os.environ.get('HORIZONTE', 7))      # dias hacia adelante (7 por defecto; 1 = ¿baja mañana?)


def cargar(carpeta):
    d = pd.read_parquet(f'{carpeta}/precios_diarios.parquet')
    p = pd.read_csv(f'{carpeta}/productos.csv')
    c = pd.read_csv(f'{carpeta}/comercios.csv')
    cal = pd.read_csv(f'{carpeta}/calendario.csv', parse_dates=['fecha'])
    d = d.merge(p, on='producto_id', how='left').merge(c[['comercio_id', 'tachado_permanente']], on='comercio_id', how='left')
    return d.sort_values(['comercio_id', 'producto_id', 'fecha']).reset_index(drop=True), cal


def objetivo(d):
    g = d.groupby(['comercio_id', 'producto_id'], sort=False).precio_vigente
    futuro = pd.concat([g.shift(-k) for k in range(1, HORIZONTE + 1)], axis=1)
    minimo = futuro.min(axis=1)
    lecturas = futuro.notna().sum(axis=1)
    y = (minimo <= d.precio_vigente * (1 - UMBRAL)).astype(float)
    return y.where(d.precio_vigente.notna() & (lecturas >= min(4, HORIZONTE)))


def variables(d, cal):
    d = d.copy()
    s = ['comercio_id', 'producto_id']
    g = d.groupby(s, sort=False)
    v = g.precio_vigente.ffill()                          # ultimo precio leido (no usa el futuro)
    d['precio_ff'] = v
    gg = d.groupby(s, sort=False).precio_ff
    d['desc_actual'] = 1 - d.precio_vigente / d.precio_normal
    d['en_oferta_hoy'] = d.en_oferta.astype('float')
    d['cambio_1d'] = v / gg.shift(1) - 1
    d['cambio_7d'] = v / gg.shift(7) - 1
    d['cambio_30d'] = v / gg.shift(30) - 1
    d['vs_max_30d'] = v / gg.transform(lambda x: x.rolling(30, min_periods=1).max()) - 1
    d['vs_min_90d'] = v / gg.transform(lambda x: x.rolling(90, min_periods=1).min()) - 1
    cambio = (d.cambio_1d.abs() > 0.005).astype(int)
    grupo = cambio.groupby([d.comercio_id, d.producto_id]).cumsum()
    d['dias_sin_cambio'] = d.groupby([d.comercio_id, d.producto_id, grupo]).cumcount()
    of = d.en_oferta.fillna(False).astype(int)
    d['ofertas_90d'] = of.groupby([d.comercio_id, d.producto_id]).transform(lambda x: x.rolling(90, min_periods=1).sum())
    inicio = ((of == 1) & (of.groupby([d.comercio_id, d.producto_id]).shift(1) == 0)).astype(int)
    d['inicios_oferta_365d'] = inicio.groupby([d.comercio_id, d.producto_id]).transform(lambda x: x.rolling(365, min_periods=1).sum())
    # mismo producto en otros comercios: bajas >= 5 % en los ultimos 7 dias y precio relativo
    baja_hoy = (d.cambio_1d < -UMBRAL).astype(int)
    d['_baja'] = baja_hoy
    por_prod = d.groupby(['producto_id', 'fecha'])._baja.sum().rename('bajas_prod_dia')
    d = d.merge(por_prod, on=['producto_id', 'fecha'], how='left')
    d['bajas_prod_7d'] = d.groupby(s, sort=False).bajas_prod_dia.transform(lambda x: x.rolling(7, min_periods=1).sum())
    d['bajas_otros_7d'] = d.bajas_prod_7d - d.groupby(s, sort=False)._baja.transform(lambda x: x.rolling(7, min_periods=1).sum())
    med = d.groupby(['producto_id', 'fecha']).precio_ff.transform('median')
    d['vs_mediana_comercios'] = d.precio_ff / med - 1
    d['n_comercios'] = d.groupby(['producto_id', 'fecha']).comercio_id.transform('nunique')
    # calendario (conocido de antemano)
    fechas = pd.Series(sorted(d.fecha.unique()))
    ev = cal.groupby('fecha').evento.first()
    activo = fechas.isin(ev.index)
    proximo = pd.Series(np.nan, index=fechas.index)
    sig = None
    for i in range(len(fechas) - 1, -1, -1):           # dias hasta el proximo dia con evento
        if activo.iloc[i]:
            sig = fechas.iloc[i]
        proximo.iloc[i] = (sig - fechas.iloc[i]).days if sig is not None else 365
    cal_d = pd.DataFrame({'fecha': fechas, 'evento_activo': activo.astype(int), 'dias_a_evento': proximo.clip(upper=90)})
    bf = cal[cal.evento.str.startswith('Black Friday')].groupby(cal.fecha.dt.year).fecha.min()
    cal_d['dias_a_black_friday'] = [min([(b - f).days for b in bf if (b - f).days >= 0] or [365]) for f in fechas]
    d = d.merge(cal_d, on='fecha', how='left')
    d['dia_semana'] = d.fecha.dt.weekday
    d['dia_mes'] = d.fecha.dt.day
    d['mes'] = d.fecha.dt.month
    d['comercio_cod'] = d.comercio_id.astype('category').cat.codes
    d['division_cod'] = d.division.astype('category').cat.codes
    d['tachado'] = d.tachado_permanente.astype(int)
    return d.drop(columns=['_baja', 'bajas_prod_dia'])


COLUMNAS = ['comercio_cod', 'division_cod', 'tachado', 'desc_actual', 'en_oferta_hoy', 'cambio_1d', 'cambio_7d', 'cambio_30d', 'vs_max_30d',
            'vs_min_90d', 'dias_sin_cambio', 'ofertas_90d', 'inicios_oferta_365d', 'bajas_prod_7d', 'bajas_otros_7d', 'vs_mediana_comercios',
            'n_comercios', 'evento_activo', 'dias_a_evento', 'dias_a_black_friday', 'dia_semana', 'dia_mes', 'mes']
CATEGORICAS = ['comercio_cod', 'division_cod']
