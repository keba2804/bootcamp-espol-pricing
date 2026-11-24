"""Comun al modelo 2: carga, cortes de tiempo, escenarios de cambio de precio y metricas.

Tarea 1 (pronostico): unidades de la semana t con el precio de la semana t (el precio planificado se conoce antes) y todo lo
  demas hasta la semana t-1. Metricas: WAPE (error absoluto / unidades reales) y sesgo.
Tarea 2 (escenarios): para casos (sku, semana) de la prueba, cuanto cambian las unidades si el precio cambia -15 %, -5 %, +5 % y
  +15 %, y si el cambio CONVIENE (sube la contribucion = unidades x (precio - costo)). La respuesta correcta sale de la
  elasticidad verdadera de la simulacion (datos/verdad), que no se entrega. Metricas: error absoluto medio del cambio % de
  unidades y acierto en "conviene / no conviene"."""
from pathlib import Path
import numpy as np
import pandas as pd

AQUI = Path(__file__).resolve().parent
CORTES = {'entrenamiento': ('2023-01-02', '2024-12-30'), 'validacion': ('2025-01-06', '2025-06-30'), 'prueba': ('2025-07-07', '2025-12-29')}
CAMBIOS = (-0.15, -0.05, 0.05, 0.15)


def cargar(carpeta=AQUI / 'datos'):
    v = pd.read_parquet(Path(carpeta) / 'ventas_semanales.parquet')
    k = pd.read_csv(Path(carpeta) / 'skus.csv')
    v = v.merge(k, on='sku', how='left').sort_values(['sku', 'semana']).reset_index(drop=True)
    v['semana_del_año'] = v.semana.dt.isocalendar().week.astype(int).clip(upper=52)
    v['edad'] = v.groupby('sku').cumcount()                     # semanas desde que el SKU aparece
    return v


def armar_escenarios(v, n=600, semilla=5):
    """Casos (sku, semana) de la prueba, sin promocion, con 4 cambios de precio cada uno."""
    a, b = CORTES['prueba']
    base = v[(v.semana >= a) & (v.semana <= b) & ~v.en_promocion].sample(n, random_state=semilla)
    filas = [dict(caso=i, sku=r.sku, semana=r.semana, precio_actual=r.precio, cambio=c, precio_propuesto=round(r.precio * (1 + c), 2),
                  costo_unitario=r.costo_unitario) for i, r in enumerate(base.itertuples()) for c in CAMBIOS]
    return pd.DataFrame(filas)


def verdad_escenarios(esc, carpeta=AQUI / 'datos'):
    """Cambio % verdadero de unidades = (precio nuevo / precio actual)^elasticidad - 1; conviene si sube la contribucion."""
    par = pd.read_parquet(Path(carpeta) / 'verdad' / 'parametros_sku.parquet').set_index('sku')
    e = esc.sku.map(par.elasticidad)
    ratio = esc.precio_propuesto / esc.precio_actual
    out = esc.copy()
    out['cambio_unidades_real'] = ratio ** e - 1
    out['conviene_real'] = ratio ** e * (esc.precio_propuesto - esc.costo_unitario) > (esc.precio_actual - esc.costo_unitario)
    return out


def wape(y, p):
    y, p = np.asarray(y, float), np.asarray(p, float)
    return float(np.abs(y - p).sum() / y.sum())


def metricas_pronostico(y, p):
    return {'WAPE': round(wape(y, p), 4), 'sesgo': round(float((np.sum(p) - np.sum(y)) / np.sum(y)), 4)}


def metricas_escenarios(pred, verdad):
    """pred: caso, cambio, cambio_unidades (estimado). Devuelve el error del cambio % y el acierto en 'conviene'."""
    m = verdad.merge(pred[['caso', 'cambio', 'cambio_unidades']], on=['caso', 'cambio'])
    ratio = m.precio_propuesto / m.precio_actual
    conviene = (1 + m.cambio_unidades) * (m.precio_propuesto - m.costo_unitario) > (m.precio_actual - m.costo_unitario)
    return {'error_medio_cambio_unidades_pts': round(float((m.cambio_unidades - m.cambio_unidades_real).abs().mean() * 100), 2),
            'acierto_conviene': round(float((conviene == m.conviene_real).mean()), 4),
            'acierto_conviene_cambios_15pct': round(float((conviene == m.conviene_real)[m.cambio.abs() > 0.1].mean()), 4),
            'casos': int(m.caso.nunique())}
