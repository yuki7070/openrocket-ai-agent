# FlightDataType 一覧

## 概要

`FlightDataType` は OpenRocket のシミュレーション結果から取得できる時系列データの種類を定義する。`orhelper.FlightDataType` として利用可能。目的関数（`ObjectiveFunction`）や制約（`Constraint`）の `flight_data_type` フィールドに文字列で指定する（例: `"TYPE_ALTITUDE"`）。

## データ取得方法

```python
from orhelper import FlightDataType

# シミュレーション後にデータ取得
data = orh.get_timeseries(sim, [FlightDataType.TYPE_TIME, FlightDataType.TYPE_ALTITUDE])
altitude_series = data[FlightDataType.TYPE_ALTITUDE]  # numpy array
```

## スカラー抽出方法（Extraction）

目的関数や制約で使用する場合、時系列からスカラーを抽出する。

| Extraction | 説明 | 使用例 |
|---|---|---|
| `MAX` | 時系列の最大値 | 最高高度、最大速度 |
| `MIN` | 時系列の最小値 | 最小安定余裕 |
| `FINAL` | 最終値（着地時） | 着地速度、最終位置 |
| `MEAN` | 平均値 | 平均安定余裕 |

## カテゴリ別 FlightDataType 一覧

### 位置

| FlightDataType | 説明 | 単位 | 主な用途 |
|---|---|---|---|
| `TYPE_ALTITUDE` | 高度 | m | 目的関数（最高高度） |
| `TYPE_POSITION_X` | 水平位置X | m | ドリフト距離 |
| `TYPE_POSITION_Y` | 水平位置Y | m | ドリフト距離 |
| `TYPE_POSITION_XY` | 水平距離(sqrt(x^2+y^2)) | m | 着地ドリフト |
| `TYPE_POSITION_DIRECTION` | 水平方向角度 | rad | - |
| `TYPE_LATITUDE` | 緯度 | deg | - |
| `TYPE_LONGITUDE` | 経度 | deg | - |

### 速度

| FlightDataType | 説明 | 単位 | 主な用途 |
|---|---|---|---|
| `TYPE_VELOCITY_Z` | 垂直速度 | m/s | 上昇・降下速度 |
| `TYPE_VELOCITY_XY` | 水平速度 | m/s | - |
| `TYPE_VELOCITY_TOTAL` | 合計速度 | m/s | 最大速度（目的/制約） |
| `TYPE_ACCELERATION_Z` | 垂直加速度 | m/s^2 | - |
| `TYPE_ACCELERATION_XY` | 水平加速度 | m/s^2 | - |
| `TYPE_ACCELERATION_TOTAL` | 合計加速度 | m/s^2 | 最大G制約 |
| `TYPE_MACH_NUMBER` | マッハ数 | - | 亜音速制約 |

### 安定性

| FlightDataType | 説明 | 単位 | 主な用途 |
|---|---|---|---|
| `TYPE_STABILITY` | 安定余裕（キャリバー） | cal | 安定性制約（≥1.5） |
| `TYPE_CP_LOCATION` | 風圧中心位置 | m | - |
| `TYPE_CG_LOCATION` | 重心位置 | m | - |

### 空力

| FlightDataType | 説明 | 単位 | 主な用途 |
|---|---|---|---|
| `TYPE_AOA` | 迎角 (Angle of Attack) | rad | - |
| `TYPE_DRAG_COEFF` | 抗力係数 CD | - | - |
| `TYPE_DRAG_FORCE` | 抗力 | N | - |
| `TYPE_AXIAL_DRAG_COEFF` | 軸方向抗力係数 | - | - |
| `TYPE_FRICTION_DRAG_COEFF` | 摩擦抗力係数 | - | - |
| `TYPE_PRESSURE_DRAG_COEFF` | 圧力抗力係数 | - | - |
| `TYPE_BASE_DRAG_COEFF` | 基部抗力係数 | - | - |
| `TYPE_NORMAL_FORCE_COEFF` | 法線力係数 CN | - | - |
| `TYPE_PITCH_MOMENT_COEFF` | ピッチモーメント係数 | - | - |
| `TYPE_YAW_MOMENT_COEFF` | ヨーモーメント係数 | - | - |
| `TYPE_SIDE_FORCE_COEFF` | 側力係数 | - | - |
| `TYPE_ROLL_MOMENT_COEFF` | ロールモーメント係数 | - | - |
| `TYPE_ROLL_FORCING_COEFF` | ロール強制係数 | - | - |
| `TYPE_ROLL_DAMPING_COEFF` | ロール減衰係数 | - | - |
| `TYPE_REFERENCE_LENGTH` | 基準長さ | m | - |
| `TYPE_REFERENCE_AREA` | 基準面積 | m^2 | - |
| `TYPE_DYNAMIC_PRESSURE` | 動圧 | Pa | - |

### 回転

| FlightDataType | 説明 | 単位 | 主な用途 |
|---|---|---|---|
| `TYPE_PITCH_RATE` | ピッチレート | deg/s | - |
| `TYPE_YAW_RATE` | ヨーレート | deg/s | - |
| `TYPE_ROLL_RATE` | ロールレート | deg/s | - |
| `TYPE_ORIENTATION_THETA` | 姿勢角theta | rad | - |
| `TYPE_ORIENTATION_PHI` | 姿勢角phi | rad | - |

### 質量・推力

| FlightDataType | 説明 | 単位 | 主な用途 |
|---|---|---|---|
| `TYPE_MASS` | 総質量 | kg | - |
| `TYPE_PROPELLANT_MASS` | 推進薬質量 | kg | - |
| `TYPE_LONGITUDINAL_INERTIA` | 縦方向慣性モーメント | kg*m^2 | - |
| `TYPE_ROTATIONAL_INERTIA` | 回転慣性モーメント | kg*m^2 | - |
| `TYPE_THRUST_FORCE` | 推力 | N | - |
| `TYPE_THRUST_WEIGHT_RATIO` | 推力重量比 | - | - |

### 環境

| FlightDataType | 説明 | 単位 | 主な用途 |
|---|---|---|---|
| `TYPE_WIND_VELOCITY` | 風速 | m/s | - |
| `TYPE_AIR_TEMPERATURE` | 気温 | K | - |
| `TYPE_AIR_PRESSURE` | 気圧 | Pa | - |
| `TYPE_SPEED_OF_SOUND` | 音速 | m/s | - |
| `TYPE_GRAVITY` | 重力加速度 | m/s^2 | - |
| `TYPE_REYNOLDS_NUMBER` | レイノルズ数 | - | - |

### シミュレーション

| FlightDataType | 説明 | 単位 | 主な用途 |
|---|---|---|---|
| `TYPE_TIME` | シミュレーション時間 | s | 飛行時間 |
| `TYPE_TIME_STEP` | タイムステップ | s | - |
| `TYPE_COMPUTATION_TIME` | 計算時間 | s | - |

## よく使うパターン

### 目的関数として使用

```python
from optimizer import ObjectiveFunction, Extraction, Direction

# 最高高度を最大化
ObjectiveFunction(
    name="max_altitude",
    flight_data_type="TYPE_ALTITUDE",
    extraction=Extraction.MAX,
    direction=Direction.MAXIMIZE,
)

# 着地ドリフトを最小化
ObjectiveFunction(
    name="landing_drift",
    flight_data_type="TYPE_POSITION_XY",
    extraction=Extraction.FINAL,
    direction=Direction.MINIMIZE,
)
```

### 制約として使用

```python
from optimizer import Constraint, Extraction, ConstraintOperator

# 最大加速度 ≤ 150 m/s^2 (約15G)
Constraint(
    name="max_accel",
    flight_data_type="TYPE_ACCELERATION_TOTAL",
    extraction=Extraction.MAX,
    operator=ConstraintOperator.LE,
    threshold=150.0,
)
```
