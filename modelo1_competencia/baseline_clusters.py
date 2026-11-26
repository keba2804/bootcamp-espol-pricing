"""Baseline de la PARTE 1 del modelo 1: agrupar las series (producto x comercio) segun como se mueve su precio.

Lo mas simple que haria cualquiera: K-means sobre las variables de datos/tabla_series.csv, estandarizadas, eligiendo el numero
de grupos con el coeficiente de silueta (k de 2 a 8).
Salida: grupos_baseline.csv (comercio_id, producto_id, grupo), que es el formato de entrega de la parte 1, y en pantalla el
perfil promedio de cada grupo.
Uso: python baseline_clusters.py [carpeta_datos=datos]"""
import sys
from pathlib import Path
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

AQUI = Path(__file__).resolve().parent
CARPETA = Path(sys.argv[1]) if len(sys.argv) > 1 else AQUI / 'datos'
VARIABLES = ['cambios_por_mes', 'parte_dias_en_oferta', 'ofertas_por_año', 'dias_por_oferta', 'descuento_medio_oferta',
             'bajas_5pct_por_año', 'parte_bajas_en_evento', 'parte_dias_sin_stock']

t = pd.read_csv(CARPETA / 'tabla_series.csv')
X = t[VARIABLES].fillna(t[VARIABLES].median())          # series sin ofertas o sin bajas: valor tipico
Z = StandardScaler().fit_transform(X)
sil = {}
for k in range(2, 9):
    sil[k] = silhouette_score(Z, KMeans(k, n_init=10, random_state=7).fit_predict(Z))
k = max(sil, key=sil.get)
t['grupo'] = KMeans(k, n_init=10, random_state=7).fit_predict(Z)
t[['comercio_id', 'producto_id', 'grupo']].to_csv(AQUI / 'grupos_baseline.csv', index=False)
print('silueta por k:', {kk: round(v, 3) for kk, v in sil.items()})
print(f'k elegido: {k} | series por grupo:', t.grupo.value_counts().sort_index().to_dict())
print(t.groupby('grupo')[VARIABLES].mean().round(3).T.to_string())
print('series de cada comercio en cada grupo (si un grupo es casi un comercio, el modelo encontro comercios, no perfiles):')
print(pd.crosstab(t.comercio_id, t.grupo).to_string())
