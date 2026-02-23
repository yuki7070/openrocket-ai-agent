---
name: define-problem
description: ユーザーと相談して最適化問題（変数・目的・制約）を定義する
agent: optimizer
---

# define-problem: 最適化問題定義

## いつ使うか

- `inspect-rocket` でベースライン確認後
- ユーザーの最適化目標が明確になったとき

## 参照ドキュメント

- `docs/design-variables.md` — 設計変数リファレンス・VARIABLE_CATALOG
- `docs/flight-data-types.md` — FlightDataType一覧（目的関数・制約に使用）
- `docs/constraints-guide.md` — 制約定義ガイド・よく使うパターン
- `docs/simple-ork-components.md` — コンポーネント名の確認

## 入力

- ベースライン結果（`baseline.md`）
- ユーザーの最適化目標（対話で確認）

## 手順

### 1. ユーザーと目標を確認

以下を対話で明確にする:
- **何を最大化/最小化したいか**: 例「最高高度を最大化しつつ着地ドリフトを最小化」
- **どのパラメータを変えてよいか**: 例「フィンの形状とパラシュート直径」
- **守るべき制約**: 例「安定余裕1.5cal以上、着地速度5m/s以下」

### 2. 問題定義コードを生成

`inspect-rocket` で確認したコンポーネント名を使って、`problem.py` を作成する。

```python
from optimizer import (
    DesignVariable, ObjectiveFunction, Constraint,
    OptimizationProblem, VARIABLE_CATALOG,
    Extraction, Direction, ConstraintOperator,
)

# --- 設計変数 ---
variables = [
    DesignVariable(
        name="fin_root_chord",
        component_name="Trapezoidal fin set",  # ← inspect-rocketで確認した名前
        lower_bound=0.05,
        upper_bound=0.15,
        **VARIABLE_CATALOG["fin_root_chord"],
    ),
    DesignVariable(
        name="fin_height",
        component_name="Trapezoidal fin set",
        lower_bound=0.03,
        upper_bound=0.12,
        **VARIABLE_CATALOG["fin_height"],
    ),
    # ... 他の変数
]

# --- 目的関数 ---
objectives = [
    ObjectiveFunction(
        name="max_altitude",
        flight_data_type="TYPE_ALTITUDE",
        extraction=Extraction.MAX,
        direction=Direction.MAXIMIZE,
    ),
    ObjectiveFunction(
        name="landing_drift",
        flight_data_type="TYPE_POSITION_XY",
        extraction=Extraction.FINAL,
        direction=Direction.MINIMIZE,
    ),
]

# --- 制約 ---
constraints = [
    Constraint(
        name="stability",
        flight_data_type="TYPE_STABILITY",
        extraction=Extraction.MIN,
        operator=ConstraintOperator.GE,
        threshold=1.5,
    ),
    Constraint(
        name="landing_speed",
        flight_data_type="TYPE_VELOCITY_TOTAL",
        extraction=Extraction.FINAL,
        operator=ConstraintOperator.LE,
        threshold=5.0,
    ),
]

# --- 問題定義 ---
problem = OptimizationProblem(
    ork_file="simple.ork",
    variables=variables,
    objectives=objectives,
    constraints=constraints,
)
```

### 3. 現在値を確認

```python
from optimizer import RocketSimulator, get_current_values

with RocketSimulator(problem.ork_file) as sim:
    current = get_current_values(sim.orh, sim.sim, problem.variables)
    print("## 現在値\n")
    for name, val in current.items():
        print(f"- {name}: {val:.4f}")
```

### 4. ユーザーに確認

定義内容をサマリーとして提示し、承認を得る:
- 変数の数と範囲
- 目的関数（最大化/最小化）
- 制約条件
- 現在値が変数範囲内に含まれるか

## 出力

実験ディレクトリに `problem.py` として保存する。再実行可能なPythonファイル。

## 判断ゲート

- 変数範囲が現在値を含まない → 警告（ベースラインがfeasibleにならない可能性）
- `fin_tip_chord` の上限が `fin_root_chord` の下限より大きい → カップリング注意
- 目的関数が1つだけ → 単目的最適化で十分（NSGA-IIは不要の可能性）
- 目的関数が3つ以上 → 可視化が困難になる旨を伝達

## 注意事項

- `component_name` は `inspect-rocket` で確認した**正確な文字列**を使用
- `flight_data_type` は文字列で指定（例: `"TYPE_ALTITUDE"`）
- `problem.py` は後続の全スキルで読み込んで使用する
