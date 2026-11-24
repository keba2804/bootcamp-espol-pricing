"""Baseline del modelo 2: UNA elasticidad por division, medida tal cual en los datos (log-log con efectos fijos de SKU y semana).

Pronostico de la semana t: nivel = promedio de las 8 semanas previas, desestacionalizado y llevado al precio promedio; luego
x estacionalidad de la semana t x (precio_t / precio promedio)^elasticidad de la division.
Escenarios: cambio de unidades = (precio nuevo / precio actual)^elasticidad de la division - 1.
Para validacion se entrena con 2023-2024; para la prueba, con 2023 a junio 2025 (como haria Pycca al usarlo).
Uso: python baseline.py [carpeta_datos=datos]"""
import json, sys
from pathlib import Path
import numpy as np
import pandas as pd

from comun import AQUI, CORTES, armar_escenarios, cargar, metricas_escenarios, metricas_pronostico, verdad_escenarios

# carpeta de datos por argumento (al importar desde un notebook, sys.argv trae argumentos del kernel: se ignoran)
CARPETA = Path(sys.argv[1]) if len(sys.argv) > 1 and Path(sys.argv[1]).is_dir() else AQUI / 'datos'
v = cargar(CARPETA)


def dos_vias(df, col, it=6):
    x = df[col].copy()
    for _ in range(it):
        x = x - x.groupby(df.sku).transform('mean')
        x = x - x.groupby(df.semana).transform('mean')
    return x


def ajustar(hasta):
    tr = v[(v.semana <= hasta) & (v.unidades > 0)].copy()
    tr['ly'], tr['lx'] = np.log(tr.unidades), np.log(tr.precio)
    eps = {}
    for d, g in tr.groupby('division'):
        x, y = dos_vias(g, 'lx'), dos_vias(g, 'ly')
        eps[d] = float((x * y).sum() / (x ** 2).sum())
    tr['rel'] = tr.unidades / tr.groupby('sku').unidades.transform('mean')
    est = tr.groupby(['division', 'semana_del_año']).rel.median()
    est = est / est.groupby(level=0).transform('mean')
    return eps, est


def pronosticar(desde, hasta, eps, est):
    d = v.copy()
    d['est'] = [est.get((a, b), 1.0) for a, b in zip(d.division, d.semana_del_año)]
    d['e'] = d.division.map(eps)
    g = d.groupby('sku')
    d['p8'] = g.precio.transform(lambda z: z.shift(1).rolling(8, min_periods=2).mean())
    d['u_aj'] = d.unidades / d.est / (d.precio / d.p8) ** d.e
    d['nivel'] = d.groupby('sku').u_aj.transform(lambda z: z.shift(1).rolling(8, min_periods=2).mean())
    d['pred'] = d.nivel * d.est * (d.precio / d.p8) ** d.e
    x = d[(d.semana >= desde) & (d.semana <= hasta) & d.pred.notna()]
    return x


if __name__ == '__main__':
    res = {}
    hay_verdad = (CARPETA / 'verdad' / 'parametros_sku.parquet').exists()
    for corte, entrena_hasta in (('validacion', CORTES['entrenamiento'][1]), ('prueba', CORTES['validacion'][1])):
        a, b = CORTES[corte]
        if not ((v.semana >= a) & (v.semana <= b)).any():
            continue                                   # el paquete del bootcamp no trae la prueba
        eps, est = ajustar(entrena_hasta)
        x = pronosticar(a, b, eps, est)
        res[corte] = {'pronostico': metricas_pronostico(x.unidades, x.pred), 'elasticidad_division': {k: round(val, 3) for k, val in eps.items()}}
        if corte == 'prueba' and hay_verdad:
            esc = armar_escenarios(v)
            e = esc.sku.map(v.drop_duplicates('sku').set_index('sku').division).map(eps)
            pred = esc.assign(cambio_unidades=(esc.precio_propuesto / esc.precio_actual) ** e - 1)
            res[corte]['escenarios'] = metricas_escenarios(pred, verdad_escenarios(esc, CARPETA))
    (AQUI / 'resultados_baseline.json').write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding='utf8')
    print(json.dumps(res, ensure_ascii=False, indent=1))
