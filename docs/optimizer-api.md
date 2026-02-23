# optimizer パッケージ API リファレンス

## インポート

```python
from optimizer import *  # 全公開APIをインポート
```

または個別インポート:

```python
from optimizer import (
    # データ構造
    DesignVariable, ObjectiveFunction, Constraint, OptimizationProblem,
    Extraction, Direction, ConstraintOperator,
    VARIABLE_CATALOG, list_components, get_current_values,
    # シミュレーション
    RocketSimulator,
    # DOE
    generate_lhs, format_doe_table, run_doe, check_constraints, format_doe_results_table,
    # サロゲート
    SurrogateModel,
    # パレート最適化
    run_nsga2, find_knee_point, select_top3,
    # 可視化
    plot_pareto_front, plot_doe_summary, plot_candidate_comparison, format_results_table,
)
```

---

## Enums

### `Extraction(str, Enum)`
時系列からスカラーを抽出する方法。

| 値 | 説明 |
|---|---|
| `MAX` | 最大値 |
| `MIN` | 最小値 |
| `FINAL` | 最終値 |
| `MEAN` | 平均値 |

### `Direction(str, Enum)`
最適化方向。

| 値 | 説明 |
|---|---|
| `MAXIMIZE` | 最大化 |
| `MINIMIZE` | 最小化 |

### `ConstraintOperator(str, Enum)`
制約の比較演算子。

| 値 | 説明 |
|---|---|
| `GE` | `>=` |
| `LE` | `<=` |
| `EQ` | `==`（rel_tol=1e-6） |

---

## データクラス

### `DesignVariable`
```python
DesignVariable(
    name: str,
    component_name: str,
    setter_method: str,
    getter_method: str,
    lower_bound: float,
    upper_bound: float,
    unit: str = "",
    is_simulation_option: bool = False,
    is_integer: bool = False,
)
```

### `ObjectiveFunction`
```python
ObjectiveFunction(
    name: str,
    flight_data_type: str,           # FlightDataType属性名（例: "TYPE_ALTITUDE"）
    extraction: Extraction = Extraction.MAX,
    direction: Direction = Direction.MAXIMIZE,
)
```

### `Constraint`
```python
Constraint(
    name: str,
    flight_data_type: str,
    extraction: Extraction,
    operator: ConstraintOperator,
    threshold: float,
)
```

### `OptimizationProblem`
```python
OptimizationProblem(
    ork_file: str,
    variables: list[DesignVariable] = [],
    objectives: list[ObjectiveFunction] = [],
    constraints: list[Constraint] = [],
)
```

**プロパティ:**
- `n_var: int` — 変数の数
- `n_obj: int` — 目的関数の数
- `n_constr: int` — 制約の数
- `lower_bounds: list[float]` — 全変数の下限
- `upper_bounds: list[float]` — 全変数の上限

---

## `VARIABLE_CATALOG: dict[str, dict]`

設計変数のテンプレート辞書。キー: テンプレート名、値: `DesignVariable` のキーワード引数（`name`, `component_name`, `lower_bound`, `upper_bound` を除く）。

```python
var = DesignVariable(
    name="nose_length",
    component_name="Nose cone",
    lower_bound=0.05, upper_bound=0.25,
    **VARIABLE_CATALOG["nose_length"],
)
```

---

## ユーティリティ関数

### `list_components(orh, rocket) -> list[dict]`
ロケットのコンポーネントツリーを走査し、全コンポーネント情報を返す。

**戻り値**: `[{"name": str, "type": str, "class_name": str}, ...]`

### `get_current_values(orh, sim, variables) -> dict[str, float]`
シミュレーション/ロケットから設計変数の現在値を読み取る。

**戻り値**: `{"variable_name": current_value, ...}`

---

## RocketSimulator

コンテキストマネージャ。JVMライフサイクルを管理する。

```python
with RocketSimulator(ork_file: str) as sim:
    ...
```

### プロパティ
- `sim.orh: orhelper.Helper` — orhelperインスタンス
- `sim.sim` — OpenRocketシミュレーションオブジェクト
- `sim.rocket` — ロケットコンポーネント

### メソッド

#### `apply_design(variables, values) -> None`
設計変数の値をロケット/シミュレーションオプションに適用する。

#### `run_and_extract(objectives, constraints=None) -> dict[str, float]`
シミュレーションを実行し、目的関数・制約の値を抽出する。

#### `evaluate(problem, x) -> dict[str, float] | None`
設計ベクトル `x` について `apply_design` → `run_and_extract` を一括実行。失敗時は全値 `NaN` の辞書を返す。

---

## DOE 関数

### `generate_lhs(problem, n_samples=30, seed=None) -> np.ndarray`
Latin Hypercube Sampling でサンプル点を生成。

**戻り値**: `(n_samples, n_var)` 配列。整数変数は丸められる。

### `run_doe(simulator, problem, samples) -> list[dict]`
全DOEサンプル点をシミュレーション実行。

**戻り値**: `[{"x": [...], "obj_name": value, "feasible": bool}, ...]`

### `format_doe_table(problem, samples) -> str`
DOEサンプルをMarkdown表形式で出力。

### `format_doe_results_table(problem, results) -> str`
DOE結果をMarkdown表形式で出力。

### `check_constraints(problem, outcome) -> bool`
全制約が満たされるか判定。

---

## SurrogateModel

RBFサロゲートモデル。目的関数ごとに1つの `RBFInterpolator` を構築。

### `fit(doe_results, problem, kernel="thin_plate_spline") -> None`
DOE結果からモデルをフィッティング。NaN点は除外。最低2点必要。

### `predict(X: np.ndarray) -> dict[str, np.ndarray]`
複数点の予測。`X` shape: `(n, n_var)` → `{name: (n,) array}`。

### `predict_single(x) -> dict[str, float]`
1点の予測。

### `get_r2_scores() -> dict[str, float]`
Leave-One-Out R^2スコア。1.0に近いほど高品質。

### `format_r2_report() -> str`
R^2品質レポート（Markdown文字列）。閾値: ≥0.9 good, ≥0.7 acceptable, <0.7 poor。

---

## パレート最適化

### `run_nsga2(surrogate, problem, pop_size=100, n_gen=200, seed=42) -> dict`
NSGA-IIをサロゲート上で実行。

**戻り値**:
```python
{
    "X": np.ndarray,          # (n_pareto, n_var) 設計ベクトル
    "F": np.ndarray,          # (n_pareto, n_obj) 目的値（元スケール）
    "F_minimized": np.ndarray, # (n_pareto, n_obj) pymoo最小化スケール
}
```

### `find_knee_point(F: np.ndarray) -> int`
パレートフロントの膝点インデックス。2目的: 最大垂直距離、3+目的: 正規化和最小。

### `select_top3(pareto_result, problem) -> list[dict]`
代表3候補を選出: 膝点、各目的のベスト、最多様点。

**戻り値**: `[{"index": int, "x": [...], "f": [...], "label": str}, ...]`

---

## 可視化

全 `plot_*` 関数は `matplotlib.figure.Figure` を返す。`plt.show()` は JVM シャットダウン後に呼ぶこと。

### `plot_pareto_front(pareto_result, problem, top3=None) -> Figure`
パレートフロント散布図（2目的）。top3があればマーカー付き。

### `plot_doe_summary(doe_results, problem) -> Figure`
散布図行列: 各設計変数 × 各目的関数。feasible/infeasible を色分け。

### `plot_candidate_comparison(top3, problem) -> Figure`
top3候補の目的関数値を棒グラフで比較。

### `format_results_table(top3, problem) -> str`
top3候補をMarkdown表で出力。
