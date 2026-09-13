"""
toolbox_ml.eda
==============

Funciones de Análisis Exploratorio de Datos (EDA) y selección de features.
"""

from toolbox_ml.eda.core import (
    describe_df,
    tipifica_variables,
    get_features_num_regression,
    plot_features_num_regression,
    get_features_cat_regression,
    plot_features_cat_regression,
    detect_outliers,
)

__all__ = [
    "describe_df",
    "tipifica_variables",
    "get_features_num_regression",
    "plot_features_num_regression",
    "get_features_cat_regression",
    "plot_features_cat_regression",
    "detect_outliers",
]
