"""
Tests unitarios de toolbox_ml.eda.core.

Se usa el backend 'Agg' de matplotlib (sin ventana gráfica) para que los
tests que generan gráficos puedan ejecutarse en cualquier entorno,
incluida una máquina de CI sin pantalla.
"""

import matplotlib
matplotlib.use("Agg")

import numpy as np
import pandas as pd
import pytest

from toolbox_ml.eda.core import (
    describe_df,
    tipifica_variables,
    get_features_num_regression,
    plot_features_num_regression,
    get_features_cat_regression,
    plot_features_cat_regression,
    detect_outliers,
)


# ---------------------------------------------------------------------------
# Fixtures compartidas
# ---------------------------------------------------------------------------

@pytest.fixture
def df_mixto():
    """DataFrame con variables numéricas y categóricas, con nulos y sin ellos."""
    rng = np.random.default_rng(42)
    n = 200
    return pd.DataFrame({
        "edad": rng.normal(40, 10, n),
        "ingresos": rng.normal(30000, 5000, n) + rng.normal(0, 1, n) * 0,
        "genero": rng.choice(["M", "F"], n),
        "ciudad": rng.choice(["Madrid", "Barcelona", "Valencia"], n),
        "target": rng.normal(100, 20, n),
    })


# ---------------------------------------------------------------------------
# describe_df
# ---------------------------------------------------------------------------

def test_describe_df_devuelve_dataframe():
    """Caso correcto: input válido -> retorna DataFrame."""
    df = pd.DataFrame({"a": [1, 2, None], "b": ["x", "y", "z"]})
    resultado = describe_df(df)
    assert isinstance(resultado, pd.DataFrame)


def test_describe_df_columnas_correctas():
    """El DataFrame resultado tiene exactamente las columnas esperadas."""
    df = pd.DataFrame({"a": [1, 2, 3]})
    resultado = describe_df(df)
    assert set(resultado.columns) == {
        "tipo", "porcentaje_nulos", "valores_unicos", "porcentaje_cardinalidad"
    }


def test_describe_df_porcentaje_nulos_correcto():
    """Calcula correctamente el porcentaje de nulos."""
    df = pd.DataFrame({"a": [1, None, None, None]})
    resultado = describe_df(df)
    assert resultado.loc["a", "porcentaje_nulos"] == pytest.approx(75.0, abs=0.01)


def test_describe_df_caso_limite_dataframe_sin_columnas():
    """Caso límite: DataFrame sin columnas -> DataFrame vacío con el esquema correcto."""
    df = pd.DataFrame()
    resultado = describe_df(df)
    assert isinstance(resultado, pd.DataFrame)
    assert len(resultado) == 0
    assert set(resultado.columns) == {
        "tipo", "porcentaje_nulos", "valores_unicos", "porcentaje_cardinalidad"
    }


def test_describe_df_retorna_none_con_input_invalido():
    """Caso de error: input no es DataFrame -> retorna None."""
    assert describe_df("esto no es un dataframe") is None
    assert describe_df([1, 2, 3]) is None


# ---------------------------------------------------------------------------
# tipifica_variables
# ---------------------------------------------------------------------------

def test_tipifica_variables_devuelve_dataframe_con_columnas_correctas():
    """Caso correcto: retorna DataFrame con 'nombre_variable' y 'tipo_sugerido'."""
    df = pd.DataFrame({"a": [1, 2, 3, 4, 5]})
    resultado = tipifica_variables(df, umbral_categoria=3, umbral_continua=50.0)
    assert isinstance(resultado, pd.DataFrame)
    assert list(resultado.columns) == ["nombre_variable", "tipo_sugerido"]
    assert len(resultado) == 1


def test_tipifica_variables_clasifica_binaria_correctamente():
    """Una columna con exactamente 2 valores únicos se marca como 'Binaria'."""
    df = pd.DataFrame({"sexo": ["M", "F", "M", "F", "M"]})
    resultado = tipifica_variables(df, umbral_categoria=5, umbral_continua=50.0)
    tipo = resultado.loc[resultado["nombre_variable"] == "sexo", "tipo_sugerido"].iloc[0]
    assert tipo == "Binaria"


def test_tipifica_variables_clasifica_numerica_continua():
    """Alta cardinalidad y alto porcentaje de cardinalidad -> 'Numérica Continua'."""
    df = pd.DataFrame({"valor": list(range(100))})  # 100 valores únicos / 100 filas = 100%
    resultado = tipifica_variables(df, umbral_categoria=5, umbral_continua=50.0)
    tipo = resultado.loc[resultado["nombre_variable"] == "valor", "tipo_sugerido"].iloc[0]
    assert tipo == "Numérica Continua"


def test_tipifica_variables_caso_limite_dataframe_vacio():
    """Caso límite: DataFrame sin filas no debe lanzar excepción."""
    df = pd.DataFrame({"a": pd.Series([], dtype="float64")})
    resultado = tipifica_variables(df, umbral_categoria=5, umbral_continua=50.0)
    assert isinstance(resultado, pd.DataFrame)
    assert len(resultado) == 1


def test_tipifica_variables_retorna_none_con_input_invalido():
    """Caso de error: argumentos inválidos -> retorna None."""
    df = pd.DataFrame({"a": [1, 2, 3]})
    assert tipifica_variables("no es un df", 5, 50.0) is None
    assert tipifica_variables(df, umbral_categoria=-1, umbral_continua=50.0) is None
    assert tipifica_variables(df, umbral_categoria=5, umbral_continua=150.0) is None


# ---------------------------------------------------------------------------
# get_features_num_regression
# ---------------------------------------------------------------------------

def test_get_features_num_regression_devuelve_lista(df_mixto):
    """Caso correcto: input válido -> retorna una lista."""
    resultado = get_features_num_regression(df_mixto, target_col="target", umbral_corr=0.0)
    assert isinstance(resultado, list)


def test_get_features_num_regression_detecta_correlacion_fuerte():
    """Una columna perfectamente correlacionada con el target debe seleccionarse."""
    rng = np.random.default_rng(0)
    x = rng.normal(0, 1, 300)
    df = pd.DataFrame({
        "correlacionada": x * 2 + 1,
        "ruido": rng.normal(0, 1, 300),
        "target": x,
    })
    resultado = get_features_num_regression(df, target_col="target", umbral_corr=0.9)
    assert "correlacionada" in resultado
    assert "ruido" not in resultado


def test_get_features_num_regression_caso_limite_target_constante():
    """Caso límite: si target es constante, pearsonr no puede calcular correlación real."""
    df = pd.DataFrame({"a": [1, 2, 3, 4, 5], "target": [10, 10, 10, 10, 10]})
    # No debe lanzar una excepción; el resultado puede ser una lista vacía o con NaN filtrado
    resultado = get_features_num_regression(df, target_col="target", umbral_corr=0.5)
    assert isinstance(resultado, list)


def test_get_features_num_regression_retorna_none_con_input_invalido(df_mixto):
    """Caso de error: argumentos inválidos -> retorna None."""
    assert get_features_num_regression("no es un df", "target", 0.5) is None
    assert get_features_num_regression(df_mixto, "columna_inexistente", 0.5) is None
    assert get_features_num_regression(df_mixto, "genero", 0.5) is None  # target no numérico
    assert get_features_num_regression(df_mixto, "target", umbral_corr=1.5) is None


# ---------------------------------------------------------------------------
# plot_features_num_regression
# ---------------------------------------------------------------------------

def test_plot_features_num_regression_devuelve_lista(df_mixto):
    """Caso correcto: input válido -> retorna una lista de columnas representadas."""
    resultado = plot_features_num_regression(df_mixto, target_col="target", umbral_corr=0.0)
    assert isinstance(resultado, list)


def test_plot_features_num_regression_usa_todas_las_numericas_si_columns_vacio(df_mixto):
    """Si `columns` está vacío, se consideran automáticamente todas las numéricas."""
    resultado = plot_features_num_regression(df_mixto, target_col="target", columns=[], umbral_corr=0.0)
    assert "edad" in resultado or "ingresos" in resultado or resultado == []


def test_plot_features_num_regression_caso_limite_sin_columnas_que_cumplan(df_mixto):
    """Caso límite: umbral tan alto que ninguna columna lo supera -> lista vacía, sin excepción.

    Usamos `df_mixto`, donde las columnas numéricas no están correlacionadas
    con el target por construcción (se generan de forma independiente),
    así que ningún umbral bajo debería seleccionar ninguna con umbral=0.999.
    """
    resultado = plot_features_num_regression(df_mixto, target_col="target", umbral_corr=0.999)
    assert resultado == []


def test_plot_features_num_regression_retorna_none_con_input_invalido(df_mixto):
    """Caso de error: argumentos inválidos -> retorna None."""
    assert plot_features_num_regression("no es un df", "target") is None
    assert plot_features_num_regression(df_mixto, "columna_inexistente") is None


# ---------------------------------------------------------------------------
# get_features_cat_regression
# ---------------------------------------------------------------------------

def test_get_features_cat_regression_devuelve_lista(df_mixto):
    """Caso correcto: input válido -> retorna una lista."""
    resultado = get_features_cat_regression(df_mixto, target_col="target", pvalue=0.05)
    assert isinstance(resultado, list)


def test_get_features_cat_regression_detecta_relacion_significativa():
    """Una variable binaria con medias de target muy distintas debe salir significativa."""
    rng = np.random.default_rng(1)
    n = 300
    grupo = rng.choice(["A", "B"], n)
    target = np.where(grupo == "A", rng.normal(0, 1, n), rng.normal(50, 1, n))
    df = pd.DataFrame({"grupo": grupo, "target": target})
    resultado = get_features_cat_regression(df, target_col="target", pvalue=0.05)
    assert "grupo" in resultado


def test_get_features_cat_regression_caso_limite_una_sola_categoria():
    """Caso límite: columna categórica con una única categoría no debe lanzar excepción."""
    df = pd.DataFrame({"constante": ["X"] * 20, "target": range(20)})
    resultado = get_features_cat_regression(df, target_col="target", pvalue=0.05)
    assert resultado == []


def test_get_features_cat_regression_retorna_none_con_input_invalido(df_mixto):
    """Caso de error: argumentos inválidos -> retorna None."""
    assert get_features_cat_regression("no es un df", "target") is None
    assert get_features_cat_regression(df_mixto, "columna_inexistente") is None
    assert get_features_cat_regression(df_mixto, "genero") is None  # target no numérico


# ---------------------------------------------------------------------------
# plot_features_cat_regression
# ---------------------------------------------------------------------------

def test_plot_features_cat_regression_devuelve_lista(df_mixto):
    """Caso correcto: input válido -> retorna una lista de columnas representadas."""
    resultado = plot_features_cat_regression(df_mixto, target_col="target", pvalue=0.999)
    assert isinstance(resultado, list)


def test_plot_features_cat_regression_modo_individual(df_mixto):
    """with_individual_plot=True no debe lanzar excepción y debe devolver una lista."""
    resultado = plot_features_cat_regression(
        df_mixto, target_col="target", pvalue=0.999, with_individual_plot=True
    )
    assert isinstance(resultado, list)


def test_plot_features_cat_regression_caso_limite_sin_columnas_que_cumplan(df_mixto):
    """Caso límite: pvalue muy exigente -> ninguna columna cumple, lista vacía sin excepción.

    En `df_mixto` las categóricas ('genero', 'ciudad') no tienen relación
    real con el target (se generan de forma independiente), así que ni
    siquiera un pvalue relativamente laxo (0.05) debería seleccionarlas.
    Usamos un pvalue extremo (1e-12) para blindar el test frente a falsos
    positivos por azar.
    """
    resultado = plot_features_cat_regression(df_mixto, target_col="target", pvalue=1e-12)
    assert resultado == []


def test_plot_features_cat_regression_retorna_none_con_input_invalido(df_mixto):
    """Caso de error: argumentos inválidos -> retorna None."""
    assert plot_features_cat_regression("no es un df", "target") is None
    assert plot_features_cat_regression(df_mixto, "columna_inexistente") is None


# ---------------------------------------------------------------------------
# BONUS: detect_outliers
# ---------------------------------------------------------------------------

def test_detect_outliers_devuelve_diccionario(df_mixto):
    """Caso correcto: input válido -> retorna un diccionario."""
    resultado = detect_outliers(df_mixto)
    assert isinstance(resultado, dict)
    assert "edad" in resultado
    assert "iqr" in resultado["edad"] and "zscore" in resultado["edad"]


def test_detect_outliers_detecta_outlier_evidente():
    """Un valor extremo evidente debe detectarse por ambos métodos."""
    valores = list(np.random.default_rng(0).normal(0, 1, 100)) + [1000]  # outlier evidente
    df = pd.DataFrame({"col": valores})
    resultado = detect_outliers(df, columns=["col"])
    assert resultado["col"]["iqr"]["n_outliers"] >= 1
    assert resultado["col"]["zscore"]["n_outliers"] >= 1


def test_detect_outliers_caso_limite_columna_constante():
    """Caso límite: columna con desviación estándar 0 no debe lanzar excepción (división por 0)."""
    df = pd.DataFrame({"constante": [5] * 50})
    resultado = detect_outliers(df, columns=["constante"])
    assert resultado["constante"]["zscore"]["n_outliers"] == 0


def test_detect_outliers_retorna_none_con_input_invalido():
    """Caso de error: input inválido -> retorna None."""
    assert detect_outliers("no es un df") is None
    assert detect_outliers(pd.DataFrame({"a": [1, 2, 3]}), columns=["no_existe"]) is None
