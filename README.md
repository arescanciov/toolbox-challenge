# toolbox_ml

Paquete de Python con herramientas reutilizables para el **Análisis Exploratorio de Datos (EDA)** y la **selección de features** en proyectos de Machine Learning, desarrollado como Team Challenge.

Incluye funciones para:

- Describir de un vistazo todas las columnas de un `DataFrame` (`describe_df`).
- Sugerir automáticamente el tipo de cada variable: Binaria, Categórica, Numérica Continua o Numérica Discreta (`tipifica_variables`).
- Seleccionar y visualizar las columnas numéricas más correlacionadas con un target de regresión (`get_features_num_regression`, `plot_features_num_regression`).
- Seleccionar y visualizar las columnas categóricas con relación estadísticamente significativa con un target de regresión (`get_features_cat_regression`, `plot_features_cat_regression`).
- (Bonus) Detectar outliers en variables numéricas por dos métodos distintos: IQR y Z-score (`detect_outliers`).

---

## Instalación

```bash
git clone https://github.com/vuestro-grupo/toolbox_ml.git
cd toolbox_ml
python -m venv venv
source venv/bin/activate   # Mac/Linux
# venv\Scripts\activate    # Windows (PowerShell/cmd)
pip install -r requirements.txt
pip install -e .
```

El último comando (`pip install -e .`) instala el paquete en **modo editable**: cualquier cambio que hagáis en el código de `toolbox_ml/` se refleja al momento sin tener que reinstalar nada, y podréis importar el paquete desde cualquier notebook o script sin tocar el `PYTHONPATH`.

---

## Uso rápido

```python
import pandas as pd
from toolbox_ml.eda.core import (
    describe_df,
    tipifica_variables,
    get_features_num_regression,
    plot_features_num_regression,
    get_features_cat_regression,
    plot_features_cat_regression,
    detect_outliers,
)

df = pd.read_csv("mi_dataset.csv")
```

### `describe_df`

```python
describe_df(df)
```
Devuelve un `DataFrame` con una fila por columna del original y las columnas `tipo`, `porcentaje_nulos`, `valores_unicos` y `porcentaje_cardinalidad`.

### `tipifica_variables`

```python
tipifica_variables(df, umbral_categoria=10, umbral_continua=30.0)
```
Devuelve un `DataFrame` con `nombre_variable` y `tipo_sugerido` (`"Binaria"`, `"Categórica"`, `"Numérica Continua"` o `"Numérica Discreta"`) para cada columna.

### `get_features_num_regression` / `plot_features_num_regression`

```python
get_features_num_regression(df, target_col="precio", umbral_corr=0.3, pvalue=0.05)
plot_features_num_regression(df, target_col="precio", umbral_corr=0.3, pvalue=0.05)
```
Seleccionan las columnas numéricas cuya correlación de Pearson con `target_col` supera `umbral_corr` (y, opcionalmente, es estadísticamente significativa según `pvalue`). La versión `plot_` además pinta uno o varios `pairplot` con esas columnas.

### `get_features_cat_regression` / `plot_features_cat_regression`

```python
get_features_cat_regression(df, target_col="precio", pvalue=0.05)
plot_features_cat_regression(df, target_col="precio", pvalue=0.05, with_individual_plot=False)
```
Seleccionan las columnas categóricas con relación estadísticamente significativa con `target_col` (Mann-Whitney U si la categórica es binaria, ANOVA si tiene más de 2 categorías). La versión `plot_` pinta histogramas de `target_col` agrupados por cada categórica seleccionada.

### `detect_outliers` (bonus)

```python
detect_outliers(df)
```
Devuelve un diccionario con, para cada columna numérica, el número, porcentaje e índices de outliers detectados por IQR y por Z-score.

Puedes ver una demo completa de las siete funciones sobre el dataset del Titanic en [`notebooks/demo.ipynb`](notebooks/demo.ipynb).

---

## Cómo ejecutar los tests

```bash
pytest tests/ -v
```

Todas las funciones cuentan con al menos 3 tests unitarios (caso correcto, caso límite y caso de error) en `tests/test_core.py`.

---

## Estructura del repositorio

```
toolbox_ml/
├── __init__.py
└── eda/
    ├── __init__.py
    └── core.py            # Todas las funciones del paquete
tests/
├── __init__.py
└── test_core.py           # Tests unitarios (pytest)
notebooks/
├── demo.ipynb              # Demo de todas las funciones con datos reales
└── titanic.csv             # Dataset usado en la demo
.github/workflows/
└── tests.yml                # CI: ejecuta pytest en cada push/PR (bonus)
.gitignore
README.md
requirements.txt
setup.py
```

---

## Equipo y reparto de tareas

| Integrante | Responsabilidad |
|---|---|
| _(completar)_ | Scrum Master — setup del repo, `setup.py`, `__init__.py`, integración final, notebook demo |
| _(completar)_ | `describe_df` + `tipifica_variables` + sus tests |
| _(completar)_ | `get/plot_features_num_regression` + sus tests |
| _(completar)_ | `get/plot_features_cat_regression` + sus tests + función bonus `detect_outliers` |

---

## Stack tecnológico

Python 3.10+, pandas, numpy, scipy, matplotlib, seaborn, scikit-learn, pytest, Git + GitHub. Ver [`requirements.txt`](requirements.txt) para las versiones mínimas.
