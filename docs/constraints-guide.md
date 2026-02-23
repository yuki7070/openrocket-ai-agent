# 制約定義ガイド

## 概要

制約は `Constraint` データクラスで定義し、シミュレーション結果が指定条件を満たすかを判定する。実行不可能な設計点（制約違反）はサロゲートモデル構築時に除外される。

## Constraint データクラス

```python
@dataclass
class Constraint:
    name: str                        # 制約の識別名
    flight_data_type: str            # FlightDataType属性名（例: "TYPE_STABILITY"）
    extraction: Extraction           # 時系列からのスカラー抽出方法
    operator: ConstraintOperator     # 比較演算子
    threshold: float                 # 閾値
```

## ConstraintOperator

| 演算子 | 値 | 意味 |
|---|---|---|
| `GE` | `">="` | 以上 |
| `LE` | `"<="` | 以下 |
| `EQ` | `"=="` | 等しい（相対許容差 1e-6） |

## よく使う制約パターン

### 安定性制約

```python
# 安定余裕 ≥ 1.5 キャリバー（推奨最小値）
Constraint(
    name="stability",
    flight_data_type="TYPE_STABILITY",
    extraction=Extraction.MIN,     # 飛行中の最小安定余裕
    operator=ConstraintOperator.GE,
    threshold=1.5,
)
```

**解説**: 安定余裕（静的余裕）は CP と CG の距離をボディ直径で割った値。1.0〜2.0 cal が一般的に安全。1.0 未満は不安定飛行のリスクがある。

### 最大加速度制約

```python
# 最大加速度 ≤ 150 m/s^2（約15G）
Constraint(
    name="max_accel",
    flight_data_type="TYPE_ACCELERATION_TOTAL",
    extraction=Extraction.MAX,
    operator=ConstraintOperator.LE,
    threshold=150.0,
)
```

**解説**: 電子機器やペイロードの耐G性能に応じて設定。一般的な模型ロケットでは10-20Gが目安。

### 着地速度制約

```python
# 着地速度 ≤ 5 m/s
Constraint(
    name="landing_speed",
    flight_data_type="TYPE_VELOCITY_TOTAL",
    extraction=Extraction.FINAL,    # 着地時の速度
    operator=ConstraintOperator.LE,
    threshold=5.0,
)
```

**解説**: 安全な回収のため着地速度を制限。5 m/s以下が一般的な基準。パラシュート直径に大きく依存。

### マッハ数制約

```python
# マッハ数 ≤ 0.8（亜音速飛行）
Constraint(
    name="subsonic",
    flight_data_type="TYPE_MACH_NUMBER",
    extraction=Extraction.MAX,
    operator=ConstraintOperator.LE,
    threshold=0.8,
)
```

**解説**: 遷音速領域（Ma 0.8-1.2）では空力特性が急変し、シミュレーション精度が低下する。設計上避けるのが一般的。

### 最大高度制約

```python
# 最大高度 ≤ 500 m（安全規制）
Constraint(
    name="max_altitude",
    flight_data_type="TYPE_ALTITUDE",
    extraction=Extraction.MAX,
    operator=ConstraintOperator.LE,
    threshold=500.0,
)
```

**解説**: 飛行場の規制や航空法に基づく高度制限。

### 着地ドリフト制約

```python
# 着地ドリフト ≤ 200 m
Constraint(
    name="max_drift",
    flight_data_type="TYPE_POSITION_XY",
    extraction=Extraction.FINAL,
    operator=ConstraintOperator.LE,
    threshold=200.0,
)
```

**解説**: 回収エリアの制約。風速条件と合わせて考慮する。

## NaN の取り扱い

- シミュレーションが失敗した場合、全出力値が `NaN` になる
- `check_constraint()` は `NaN` を常に**制約違反**として扱う
- DOE結果の `feasible` フラグは全制約を満たす場合のみ `True`

```python
# check_constraint の動作
import math
check_constraint(constraint, float("nan"))  # → False（常に違反）
check_constraint(constraint, 2.0)           # → GE, threshold=1.5 → True
```

## DOE時の制約チェック

```python
from optimizer import check_constraints

# DOE結果の各点について制約チェック
feasible = check_constraints(problem, outcome)
# outcome: {"stability": 1.8, "max_accel": 120.0, ...}
# → 全制約を満たせば True
```

## 制約設計のコツ

1. **保守的に始める**: 範囲を広めに設定し、feasible率を確認してから絞る
2. **feasible率チェック**: DOE結果のfeasible率が50%未満なら制約が厳しすぎる可能性
3. **物理的に不可能な制約を避ける**: 例えば安定余裕とフィンサイズは強く相関する
4. **Extraction の選択**: 安定余裕は `MIN`（飛行中の最悪条件）、加速度は `MAX`
