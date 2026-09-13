"""
toolbox_ml.eda.core
====================

Funciones de Análisis Exploratorio de Datos (EDA) y de selección de
features numéricas y categóricas para problemas de regresión.

Todas las funciones devuelven ``None`` (imprimiendo el motivo por pantalla)
cuando los argumentos de entrada no son válidos, en lugar de lanzar una
excepción, para que puedan usarse de forma segura dentro de un pipeline
interactivo de EDA.
"""

from typing import Optional

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats


# ---------------------------------------------------------------------------
# describe_df
# ---------------------------------------------------------------------------

def describe_df(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """
    Genera un resumen descriptivo de cada columna de un DataFrame.

    Argumentos:
        df (pd.DataFrame): DataFrame a analizar.

    Retorna:
        pd.DataFrame: DataFrame con una fila por columna del input (el
        nombre de cada columna original se usa como índice) y las columnas
        'tipo', 'porcentaje_nulos', 'valores_unicos' y
        'porcentaje_cardinalidad'.
        Retorna None si el input no es un DataFrame válido.
    """
    # Comprobación de entrada: el argumento debe ser un DataFrame de pandas
    if not isinstance(df, pd.DataFrame):
        print(f"Error en describe_df: se esperaba un pandas.DataFrame y se recibió {type(df)}.")
        return None

    columnas_resultado = ["tipo", "porcentaje_nulos", "valores_unicos", "porcentaje_cardinalidad"]

    # Caso límite: DataFrame sin columnas -> devolvemos un DataFrame vacío
    # pero con el esquema de columnas correcto, en lugar de fallar.
    if df.shape[1] == 0:
        return pd.DataFrame(columns=columnas_resultado)

    n_filas = len(df)
    filas = {}

    for columna in df.columns:
        serie = df[columna]

        tipo = str(serie.dtype)

        # Porcentaje de nulos sobre el total de filas (0.0 si el df está vacío)
        pct_nulos = (serie.isna().sum() / n_filas * 100) if n_filas > 0 else 0.0

        # Número de valores únicos, sin contar los nulos
        n_unicos = int(serie.nunique(dropna=True))

        # Cardinalidad relativa: proporción de valores únicos sobre el total de filas
        pct_cardinalidad = (n_unicos / n_filas * 100) if n_filas > 0 else 0.0

        filas[columna] = {
            "tipo": tipo,
            "porcentaje_nulos": round(pct_nulos, 2),
            "valores_unicos": n_unicos,
            "porcentaje_cardinalidad": round(pct_cardinalidad, 2),
        }

    resultado = pd.DataFrame(filas).T
    resultado.index.name = None

    # Al construir el DataFrame a partir de un diccionario de diccionarios y
    # transponer, pandas puede inferir tipos 'object' para todo; forzamos
    # los tipos numéricos correctos.
    resultado["porcentaje_nulos"] = resultado["porcentaje_nulos"].astype(float)
    resultado["valores_unicos"] = resultado["valores_unicos"].astype(int)
    resultado["porcentaje_cardinalidad"] = resultado["porcentaje_cardinalidad"].astype(float)

    return resultado[columnas_resultado]


# ---------------------------------------------------------------------------
# tipifica_variables
# ---------------------------------------------------------------------------

def tipifica_variables(
    df: pd.DataFrame,
    umbral_categoria: int,
    umbral_continua: float,
) -> Optional[pd.DataFrame]:
    """
    Sugiere un tipo de variable para cada columna de un DataFrame en base a
    su cardinalidad y a su porcentaje de cardinalidad.

    La sugerencia se calcula en cascada:
        - Cardinalidad == 2                                    -> 'Binaria'
        - Cardinalidad < umbral_categoria                       -> 'Categórica'
        - Cardinalidad >= umbral_categoria y
          porcentaje_cardinalidad >= umbral_continua             -> 'Numérica Continua'
        - Cardinalidad >= umbral_categoria y
          porcentaje_cardinalidad < umbral_continua              -> 'Numérica Discreta'

    Argumentos:
        df (pd.DataFrame): DataFrame a analizar.
        umbral_categoria (int): umbral de cardinalidad que separa variables
            categóricas de numéricas.
        umbral_continua (float): umbral de porcentaje de cardinalidad
            (entre 0 y 100) que separa numéricas continuas de discretas.

    Retorna:
        pd.DataFrame: DataFrame con las columnas 'nombre_variable' y
        'tipo_sugerido', una fila por cada columna del DataFrame de entrada.
        Retorna None si algún argumento de entrada no es válido.
    """
    # --- Comprobaciones de entrada ---
    if not isinstance(df, pd.DataFrame):
        print(f"Error en tipifica_variables: 'df' debe ser un pandas.DataFrame, se recibió {type(df)}.")
        return None

    if isinstance(umbral_categoria, bool) or not isinstance(umbral_categoria, (int, np.integer)) or umbral_categoria <= 0:
        print("Error en tipifica_variables: 'umbral_categoria' debe ser un entero positivo.")
        return None

    if isinstance(umbral_continua, bool) or not isinstance(umbral_continua, (int, float, np.floating, np.integer)) or not (0 <= umbral_continua <= 100):
        print("Error en tipifica_variables: 'umbral_continua' debe ser un float entre 0 y 100.")
        return None

    n_filas = len(df)
    filas_resultado = []

    for columna in df.columns:
        cardinalidad = df[columna].nunique(dropna=True)
        pct_cardinalidad = (cardinalidad / n_filas * 100) if n_filas > 0 else 0.0

        # Lógica en cascada, tal como pide el enunciado
        if cardinalidad == 2:
            tipo_sugerido = "Binaria"
        elif cardinalidad < umbral_categoria:
            tipo_sugerido = "Categórica"
        elif pct_cardinalidad >= umbral_continua:
            tipo_sugerido = "Numérica Continua"
        else:
            tipo_sugerido = "Numérica Discreta"

        filas_resultado.append({"nombre_variable": columna, "tipo_sugerido": tipo_sugerido})

    return pd.DataFrame(filas_resultado)


# ---------------------------------------------------------------------------
# Utilidades internas compartidas por las funciones de selección de features
# ---------------------------------------------------------------------------

def _validar_df_target_numerico(nombre_funcion: str, df: pd.DataFrame, target_col: str) -> bool:
    """Comprobaciones comunes de 'df' y 'target_col' numérico. Imprime el error si falla."""
    if not isinstance(df, pd.DataFrame):
        print(f"Error en {nombre_funcion}: 'df' debe ser un pandas.DataFrame, se recibió {type(df)}.")
        return False

    if target_col not in df.columns:
        print(f"Error en {nombre_funcion}: la columna '{target_col}' no existe en el DataFrame.")
        return False

    if not pd.api.types.is_numeric_dtype(df[target_col]):
        print(f"Error en {nombre_funcion}: '{target_col}' debe ser una columna numérica.")
        return False

    return True


def _validar_float_en_rango(nombre_funcion: str, nombre_arg: str, valor, minimo: float, maximo: float, permite_none: bool = False) -> bool:
    """Comprobación común de que un argumento es float/int dentro de [minimo, maximo]."""
    if valor is None:
        if permite_none:
            return True
        print(f"Error en {nombre_funcion}: '{nombre_arg}' no puede ser None.")
        return False

    if isinstance(valor, bool) or not isinstance(valor, (int, float, np.integer, np.floating)):
        print(f"Error en {nombre_funcion}: '{nombre_arg}' debe ser un valor numérico.")
        return False

    if not (minimo <= valor <= maximo):
        print(f"Error en {nombre_funcion}: '{nombre_arg}' debe estar entre {minimo} y {maximo}.")
        return False

    return True


def _test_categorica_vs_numerica(subset: pd.DataFrame, col: str, target_col: str):
    """
    Aplica Mann-Whitney U (2 categorías) o ANOVA de un factor (>2 categorías)
    entre una columna categórica y una columna numérica objetivo.

    Retorna (p_valor, n_categorias) o (None, n_categorias) si no se puede
    calcular el test (p. ej. algún grupo sin observaciones suficientes).
    """
    categorias = subset[col].unique()
    n_categorias = len(categorias)

    if n_categorias < 2:
        return None, n_categorias

    grupos = [subset.loc[subset[col] == cat, target_col] for cat in categorias]
    if any(len(g) < 1 for g in grupos):
        return None, n_categorias

    try:
        if n_categorias == 2:
            _, p = stats.mannwhitneyu(grupos[0], grupos[1])
        else:
            _, p = stats.f_oneway(*grupos)
    except ValueError:
        # p. ej. todos los valores son idénticos dentro de un grupo
        return None, n_categorias

    return p, n_categorias


# ---------------------------------------------------------------------------
# get_features_num_regression
# ---------------------------------------------------------------------------

def get_features_num_regression(
    df: pd.DataFrame,
    target_col: str,
    umbral_corr: float,
    pvalue: float = None,
) -> Optional[list]:
    """
    Selecciona las columnas numéricas de un DataFrame cuya correlación de
    Pearson con `target_col` supera, en valor absoluto, un umbral dado.

    Argumentos:
        df (pd.DataFrame): DataFrame con los datos.
        target_col (str): nombre de la columna objetivo (debe ser numérica).
        umbral_corr (float): umbral de correlación en valor absoluto (0-1).
        pvalue (float, opcional): si se indica, exige además que la
            correlación sea estadísticamente significativa
            (p-valor < pvalue). Por defecto None (no se aplica este filtro).

    Retorna:
        list: nombres de las columnas numéricas que cumplen los criterios.
        Retorna None si algún argumento de entrada no es válido.
    """
    # --- Comprobaciones de entrada ---
    if not _validar_df_target_numerico("get_features_num_regression", df, target_col):
        return None
    if not _validar_float_en_rango("get_features_num_regression", "umbral_corr", umbral_corr, 0, 1):
        return None
    if not _validar_float_en_rango("get_features_num_regression", "pvalue", pvalue, 0, 1, permite_none=True):
        return None

    # Candidatas: todas las columnas numéricas salvo el propio target
    columnas_numericas = [c for c in df.select_dtypes(include=np.number).columns if c != target_col]

    columnas_seleccionadas = []
    for col in columnas_numericas:
        # Eliminamos filas donde falte alguno de los dos valores para que
        # pearsonr no falle con NaN
        pareja = df[[col, target_col]].dropna()
        if len(pareja) < 2:
            continue  # no hay datos suficientes para calcular una correlación

        corr, p = stats.pearsonr(pareja[col], pareja[target_col])

        if abs(corr) > umbral_corr and (pvalue is None or p < pvalue):
            columnas_seleccionadas.append(col)

    return columnas_seleccionadas


# ---------------------------------------------------------------------------
# plot_features_num_regression
# ---------------------------------------------------------------------------

def plot_features_num_regression(
    df: pd.DataFrame,
    target_col: str = "",
    columns: list = [],
    umbral_corr: float = 0,
    pvalue: float = None,
) -> Optional[list]:
    """
    Pinta uno o varios pairplots con las columnas numéricas de `columns`
    que superan los criterios de correlación con `target_col` (misma
    lógica que `get_features_num_regression`), y devuelve la lista de
    columnas efectivamente representadas.

    Si la lista de columnas que superan el filtro tiene más de 5 elementos,
    se reparte en grupos de como mucho 4 columnas cada uno, añadiendo
    siempre `target_col` a cada grupo (es decir, cada pairplot muestra como
    máximo 5 columnas en total).

    Argumentos:
        df (pd.DataFrame): DataFrame con los datos.
        target_col (str): columna objetivo (numérica).
        columns (list): columnas candidatas a evaluar. Si está vacía, se
            usan automáticamente todas las columnas numéricas del
            DataFrame (excepto target_col).
        umbral_corr (float): umbral de correlación en valor absoluto (0-1).
        pvalue (float, opcional): nivel de significación exigido.

    Retorna:
        list: columnas que cumplen los criterios y han sido representadas.
        Retorna None si algún argumento de entrada no es válido.
    """
    # --- Comprobaciones de entrada (mismas que get_features_num_regression) ---
    if not _validar_df_target_numerico("plot_features_num_regression", df, target_col):
        return None
    if not _validar_float_en_rango("plot_features_num_regression", "umbral_corr", umbral_corr, 0, 1):
        return None
    if not _validar_float_en_rango("plot_features_num_regression", "pvalue", pvalue, 0, 1, permite_none=True):
        return None

    # Si no se especifican columnas candidatas, usamos todas las numéricas
    candidatas = columns if columns else [
        c for c in df.select_dtypes(include=np.number).columns if c != target_col
    ]

    columnas_validas = []
    for col in candidatas:
        if col not in df.columns or col == target_col:
            continue
        if not pd.api.types.is_numeric_dtype(df[col]):
            continue

        pareja = df[[col, target_col]].dropna()
        if len(pareja) < 2:
            continue

        corr, p = stats.pearsonr(pareja[col], pareja[target_col])
        if abs(corr) > umbral_corr and (pvalue is None or p < pvalue):
            columnas_validas.append(col)

    if not columnas_validas:
        print("plot_features_num_regression: ninguna columna cumple los criterios de correlación indicados.")
        return []

    # Agrupamos de 4 en 4 (+ target_col = máximo 5 columnas por pairplot)
    TAMANO_GRUPO = 4
    grupos = [columnas_validas[i:i + TAMANO_GRUPO] for i in range(0, len(columnas_validas), TAMANO_GRUPO)]

    for grupo in grupos:
        sns.pairplot(df[[target_col] + grupo].dropna())
        plt.show()

    return columnas_validas


# ---------------------------------------------------------------------------
# get_features_cat_regression
# ---------------------------------------------------------------------------

def get_features_cat_regression(
    df: pd.DataFrame,
    target_col: str,
    pvalue: float = 0.05,
) -> Optional[list]:
    """
    Selecciona las columnas categóricas de un DataFrame cuya relación
    estadística con `target_col` es significativa al nivel `pvalue`.

    Selecciona automáticamente el test más adecuado según la cardinalidad
    de cada variable categórica: Mann-Whitney U si tiene exactamente 2
    categorías, ANOVA de un factor si tiene más de 2.

    Argumentos:
        df (pd.DataFrame): DataFrame con los datos.
        target_col (str): columna objetivo, debe ser numérica.
        pvalue (float): nivel de significación exigido (0-1). Por defecto 0.05.

    Retorna:
        list: nombres de las columnas categóricas con relación significativa.
        Retorna None si algún argumento de entrada no es válido.
    """
    # --- Comprobaciones de entrada ---
    if not _validar_df_target_numerico("get_features_cat_regression", df, target_col):
        return None
    if not _validar_float_en_rango("get_features_cat_regression", "pvalue", pvalue, 0, 1):
        return None

    columnas_categoricas = [
        c for c in df.select_dtypes(include=["object", "category", "bool"]).columns if c != target_col
    ]

    columnas_seleccionadas = []
    for col in columnas_categoricas:
        subset = df[[col, target_col]].dropna()
        p, _ = _test_categorica_vs_numerica(subset, col, target_col)

        if p is not None and p < pvalue:
            columnas_seleccionadas.append(col)

    return columnas_seleccionadas


# ---------------------------------------------------------------------------
# plot_features_cat_regression
# ---------------------------------------------------------------------------

def plot_features_cat_regression(
    df: pd.DataFrame,
    target_col: str = "",
    columns: list = [],
    pvalue: float = 0.05,
    with_individual_plot: bool = False,
) -> Optional[list]:
    """
    Para cada columna categórica de `columns` cuya relación con
    `target_col` sea estadísticamente significativa (misma lógica que
    `get_features_cat_regression`), pinta un histograma de `target_col`
    agrupado por cada categoría, y devuelve la lista de columnas
    representadas.

    Argumentos:
        df (pd.DataFrame): DataFrame con los datos.
        target_col (str): columna objetivo, debe ser numérica.
        columns (list): columnas categóricas candidatas. Si está vacía, se
            usan automáticamente todas las columnas categóricas del
            DataFrame.
        pvalue (float): nivel de significación exigido (0-1).
        with_individual_plot (bool): si es True, cada variable se pinta en
            su propia figura. Si es False (por defecto), todas las
            variables comparten una única figura con subplots.

    Retorna:
        list: columnas categóricas que cumplen el test y han sido
        representadas. Retorna None si algún argumento de entrada no es
        válido.
    """
    # --- Comprobaciones de entrada ---
    if not _validar_df_target_numerico("plot_features_cat_regression", df, target_col):
        return None
    if not _validar_float_en_rango("plot_features_cat_regression", "pvalue", pvalue, 0, 1):
        return None

    candidatas = columns if columns else [
        c for c in df.select_dtypes(include=["object", "category", "bool"]).columns if c != target_col
    ]

    columnas_validas = []
    for col in candidatas:
        if col not in df.columns or col == target_col:
            continue

        subset = df[[col, target_col]].dropna()
        p, _ = _test_categorica_vs_numerica(subset, col, target_col)

        if p is not None and p < pvalue:
            columnas_validas.append(col)

    if not columnas_validas:
        print("plot_features_cat_regression: ninguna columna categórica cumple el criterio de significación indicado.")
        return []

    if with_individual_plot:
        for col in columnas_validas:
            plt.figure(figsize=(7, 5))
            sns.histplot(data=df, x=target_col, hue=col, multiple="stack")
            plt.title(f"{target_col} agrupado por {col}")
            plt.tight_layout()
            plt.show()
    else:
        n = len(columnas_validas)
        cols_grid = min(2, n)
        rows_grid = int(np.ceil(n / cols_grid))
        fig, axes = plt.subplots(rows_grid, cols_grid, figsize=(7 * cols_grid, 5 * rows_grid))
        axes = np.array(axes).reshape(-1)  # aplanamos por si hay una única fila/columna

        for ax, col in zip(axes, columnas_validas):
            sns.histplot(data=df, x=target_col, hue=col, multiple="stack", ax=ax)
            ax.set_title(f"{target_col} agrupado por {col}")

        # Ocultamos ejes sobrantes si el número de variables es impar
        for ax in axes[n:]:
            ax.axis("off")

        plt.tight_layout()
        plt.show()

    return columnas_validas


# ---------------------------------------------------------------------------
# BONUS: detect_outliers
# ---------------------------------------------------------------------------

def detect_outliers(df: pd.DataFrame, columns: list = None) -> Optional[dict]:
    """
    Detecta outliers en columnas numéricas de un DataFrame usando dos
    métodos: rango intercuartílico (IQR) y Z-score.

    Argumentos:
        df (pd.DataFrame): DataFrame a analizar.
        columns (list, opcional): columnas numéricas a analizar. Si es
            None (por defecto), se analizan todas las columnas numéricas
            del DataFrame.

    Retorna:
        dict: un diccionario con una entrada por columna analizada. Cada
        entrada es a su vez un diccionario con las claves 'iqr' y
        'zscore', cada una con 'n_outliers' (int), 'porcentaje' (float) e
        'indices' (list de índices del DataFrame original).
        Retorna None si el input no es válido.
    """
    if not isinstance(df, pd.DataFrame):
        print(f"Error en detect_outliers: 'df' debe ser un pandas.DataFrame, se recibió {type(df)}.")
        return None

    if columns is None:
        columnas_a_analizar = list(df.select_dtypes(include=np.number).columns)
    else:
        columnas_invalidas = [c for c in columns if c not in df.columns]
        if columnas_invalidas:
            print(f"Error en detect_outliers: columnas no encontradas en el DataFrame: {columnas_invalidas}")
            return None
        columnas_a_analizar = [c for c in columns if pd.api.types.is_numeric_dtype(df[c])]

    resultado = {}
    n_total = len(df)

    for col in columnas_a_analizar:
        serie = df[col].dropna()

        # --- Método IQR ---
        q1, q3 = serie.quantile(0.25), serie.quantile(0.75)
        iqr = q3 - q1
        limite_inf, limite_sup = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        idx_iqr = serie[(serie < limite_inf) | (serie > limite_sup)].index.tolist()

        # --- Método Z-score (|z| > 3) ---
        media, std = serie.mean(), serie.std()
        if std == 0 or pd.isna(std):
            idx_zscore = []
        else:
            zscores = (serie - media) / std
            idx_zscore = serie[zscores.abs() > 3].index.tolist()

        resultado[col] = {
            "iqr": {
                "n_outliers": len(idx_iqr),
                "porcentaje": round(len(idx_iqr) / n_total * 100, 2) if n_total > 0 else 0.0,
                "indices": idx_iqr,
            },
            "zscore": {
                "n_outliers": len(idx_zscore),
                "porcentaje": round(len(idx_zscore) / n_total * 100, 2) if n_total > 0 else 0.0,
                "indices": idx_zscore,
            },
        }

    return resultado
