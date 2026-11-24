"""Estilo comun de los graficos de los notebooks (paleta validada: azul, naranja, aqua en ese orden; un solo eje por grafico,
lineas finas, cuadricula tenue, texto en tinta neutra)."""
import matplotlib.pyplot as plt

AZUL, NARANJA, AQUA, AMARILLO = '#2a78d6', '#eb6834', '#1baf7a', '#eda100'
TINTA, TINTA2, GRIS, FONDO = '#0b0b0b', '#52514e', '#c3c2b7', '#fcfcfb'
SERIES = [AZUL, NARANJA, AQUA]


def aplicar():
    plt.rcParams.update({
        'figure.figsize': (10, 4), 'figure.dpi': 110, 'figure.facecolor': FONDO, 'axes.facecolor': FONDO,
        'axes.edgecolor': GRIS, 'axes.labelcolor': TINTA2, 'axes.titlecolor': TINTA, 'axes.titlesize': 12, 'axes.titleweight': 'bold',
        'axes.titlelocation': 'left', 'axes.spines.top': False, 'axes.spines.right': False, 'axes.grid': True, 'grid.color': '#e7e6e2',
        'grid.linewidth': 0.8, 'xtick.color': TINTA2, 'ytick.color': TINTA2, 'font.size': 10, 'legend.frameon': False,
        'lines.linewidth': 2, 'axes.prop_cycle': plt.cycler(color=SERIES)})


def pie(ax, texto):
    """Nota de fuente o lectura debajo del grafico."""
    ax.annotate(texto, xy=(0, -0.18), xycoords='axes fraction', fontsize=8.5, color=TINTA2, va='top')
