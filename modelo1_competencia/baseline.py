"""Baseline del modelo 1: ¿bajara el precio >= 5 % en los proximos 7 dias? (variables.py define objetivo y variables)

Cortes en el tiempo (nunca al azar):
  entrenamiento 2023-01-01 a 2024-12-31 | validacion 2025-01-01 a 2025-06-30 | prueba (OCULTA para el bootcamp) 2025-07-01 a 2025-12-24
Modelos:
  1. regla: tasa historica de bajas del comercio x mes (lo que haria alguien con una tabla dinamica)
  2. arboles: HistGradientBoostingClassifier con variables de historia, calendario y contagio entre comercios
Metricas: AUC, AP (area bajo precision-recall, la mas exigente con una clase poco frecuente), Brier y precision en el 5 % de
mayor riesgo (si el lider solo revisa 5 de cada 100 alertas, cuantas aciertan).
Uso: python baseline.py [carpeta_datos=datos]"""
import json, sys, time
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score

from variables import CATEGORICAS, COLUMNAS, HORIZONTE, cargar, objetivo, variables

AQUI = Path(__file__).resolve().parent
CARPETA = sys.argv[1] if len(sys.argv) > 1 else str(AQUI / 'datos')
CORTES = {'entrenamiento': ('2023-01-01', '2024-12-31'), 'validacion': ('2025-01-01', '2025-06-30'), 'prueba': ('2025-07-01', '2025-12-24')}

t0 = time.time()
d, cal = cargar(CARPETA)
d['y'] = objetivo(d)
d = variables(d, cal)
print('variables listas', round(time.time() - t0), 's |', len(d), 'filas', flush=True)
corte = {k: d[(d.fecha >= a) & (d.fecha <= b) & d.y.notna()] for k, (a, b) in CORTES.items()}
corte = {k: x for k, x in corte.items() if len(x)}        # el paquete del bootcamp no trae la prueba
EVAL = [k for k in ('validacion', 'prueba') if k in corte]
for k, x in corte.items():
    print(k, len(x), 'filas | tasa de bajas', round(float(x.y.mean()), 4))


def precision_top(y, p, q=0.05):
    n = max(1, int(len(p) * q))
    return float(np.asarray(y)[np.argsort(-np.asarray(p))[:n]].mean())


def metricas(y, p):
    return {'AUC': round(roc_auc_score(y, p), 4), 'AP': round(average_precision_score(y, p), 4), 'Brier': round(brier_score_loss(y, p), 5),
            'precision_top5pct': round(precision_top(y, p), 4), 'tasa_base': round(float(np.mean(y)), 4)}


res = {}
# 1) regla: tasa historica del comercio por mes del año
tasa = corte['entrenamiento'].groupby(['comercio_id', 'mes']).y.mean()
glob = corte['entrenamiento'].y.mean()
for k in EVAL:
    x = corte[k]
    p = pd.Series(list(zip(x.comercio_id, x.mes))).map(tasa).fillna(glob).values
    res.setdefault(k, {})['1_regla_tasa_comercio_mes'] = metricas(x.y, p)

# 2) arboles (entrena con una muestra de 1 de cada 2 dias para ir rapido)
tr = corte['entrenamiento']
tr = tr[tr.fecha.dt.day % 2 == 0]
cat = [COLUMNAS.index(c) for c in CATEGORICAS]
m = HistGradientBoostingClassifier(max_iter=400, learning_rate=0.06, max_leaf_nodes=63, min_samples_leaf=200, l2_regularization=1.0,
                                   categorical_features=cat, early_stopping=True, validation_fraction=0.1, random_state=7)
m.fit(tr[COLUMNAS], tr.y.astype(int))
print('arboles entrenados en', round(time.time() - t0), 's | iteraciones', m.n_iter_, flush=True)
for k in EVAL:
    x = corte[k]
    res[k]['2_arboles_hgb'] = metricas(x.y, m.predict_proba(x[COLUMNAS])[:, 1])

# importancia de variables (permutacion barata: caida de AUC en validacion al barajar cada una)
x = corte['validacion'].sample(200000, random_state=7) if len(corte['validacion']) > 200000 else corte['validacion']
base_auc = roc_auc_score(x.y, m.predict_proba(x[COLUMNAS])[:, 1])
imp = {}
rng = np.random.default_rng(7)
for c in COLUMNAS:
    xx = x[COLUMNAS].copy()
    xx[c] = rng.permutation(xx[c].values)
    imp[c] = round(base_auc - roc_auc_score(x.y, m.predict_proba(xx)[:, 1]), 4)
res['importancia_variables_caida_auc'] = dict(sorted(imp.items(), key=lambda kv: -kv[1]))
(AQUI / f"resultados_baseline{'' if HORIZONTE == 7 else f'_h{HORIZONTE}'}.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding='utf8')
for k in EVAL:
    print('==', k)
    print(pd.DataFrame(res[k]).T.to_string())
print('variables que mas aportan:', list(res['importancia_variables_caida_auc'].items())[:8])
print('listo en', round(time.time() - t0), 's')
