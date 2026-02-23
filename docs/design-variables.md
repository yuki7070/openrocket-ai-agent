# 設計変数リファレンス

## 概要

設計変数は `DesignVariable` データクラスで定義され、OpenRocket コンポーネントのプロパティをPythonから操作可能にする。`VARIABLE_CATALOG` にテンプレートが用意されている。

## DesignVariable データクラス

```python
@dataclass
class DesignVariable:
    name: str                        # 変数の識別名
    component_name: str              # OpenRocketコンポーネント名（.orkファイル内の名前）
    setter_method: str               # プロパティ設定メソッド名
    getter_method: str               # プロパティ取得メソッド名
    lower_bound: float               # 下限値
    upper_bound: float               # 上限値
    unit: str = ""                   # 物理単位（任意）
    is_simulation_option: bool = False  # True: シミュレーションオプション
    is_integer: bool = False         # True: 整数値変数
```

## VARIABLE_CATALOG 一覧

カタログからテンプレートを取得し、`component_name` と `lower_bound`/`upper_bound` を追加して使用する。

### 形状変数（コンポーネントプロパティ）

| カタログキー | setter | getter | 単位 | 説明 | 推奨範囲 |
|---|---|---|---|---|---|
| `nose_length` | `setLength` | `getLength` | m | ノーズコーン長さ | 0.05 - 0.30 |
| `body_tube_length` | `setLength` | `getLength` | m | ボディチューブ長さ | 0.10 - 1.00 |
| `fin_root_chord` | `setRootChord` | `getRootChord` | m | フィン根元弦長 | 0.03 - 0.20 |
| `fin_tip_chord` | `setTipChord` | `getTipChord` | m | フィン先端弦長 | 0.01 - 0.15 |
| `fin_height` | `setHeight` | `getHeight` | m | フィン高さ（スパン） | 0.02 - 0.15 |
| `fin_count` | `setFinCount` | `getFinCount` | - | フィン枚数（整数） | 3 - 6 |
| `parachute_diameter` | `setDiameter` | `getDiameter` | m | パラシュート直径 | 0.10 - 1.00 |

### シミュレーションオプション

| カタログキー | setter | getter | 単位 | 説明 | 推奨範囲 |
|---|---|---|---|---|---|
| `launch_rod_angle` | `setLaunchRodAngle` | `getLaunchRodAngle` | rad | 発射台角度（0=垂直） | 0.0 - 0.26 (≈15deg) |
| `launch_rod_length` | `setLaunchRodLength` | `getLaunchRodLength` | m | 発射台ロッド長さ | 0.5 - 2.0 |
| `wind_speed` | `setWindSpeedAverage` | `getWindSpeedAverage` | m/s | 平均風速 | 0.0 - 10.0 |

## 使い方

### カタログから変数を作成

```python
from optimizer import DesignVariable, VARIABLE_CATALOG

# カタログからテンプレートを取得し、コンポーネント名と範囲を追加
var = DesignVariable(
    name="nose_length",
    component_name="Nose cone",     # .orkファイル内のコンポーネント名
    lower_bound=0.05,
    upper_bound=0.25,
    **VARIABLE_CATALOG["nose_length"],
)
```

### カタログにない変数を作成

OpenRocket コンポーネントに対応する Java メソッドを直接指定できる。

```python
var = DesignVariable(
    name="fin_sweep",
    component_name="Trapezoidal fin set",
    setter_method="setSweep",
    getter_method="getSweep",
    lower_bound=0.0,
    upper_bound=0.05,
    unit="m",
)
```

### 現在値の確認

```python
from optimizer import RocketSimulator, get_current_values

with RocketSimulator("simple.ork") as sim:
    values = get_current_values(sim.orh, sim.sim, [var1, var2, var3])
    print(values)  # {"nose_length": 0.1, "fin_height": 0.05, ...}
```

## 変数間のカップリング（物理的制約）

設計変数の範囲を定義する際に、以下の物理的な制約関係に注意する。

| 関係 | 説明 |
|---|---|
| `fin_tip_chord <= fin_root_chord` | フィン先端弦長は根元弦長以下 |
| `fin_height > 0` | フィン高さは正の値 |
| `parachute_diameter > 0` | パラシュート直径は正の値 |
| `fin_count >= 2` | フィン枚数は2以上（通常3以上） |
| `launch_rod_angle >= 0` | 発射角度は0以上（0が垂直） |

これらのカップリングが変数範囲で満たされるように `lower_bound` / `upper_bound` を設定する。

## コンポーネントの動的発見

`.ork` ファイル内のコンポーネント名がわからない場合、`list_components()` で確認できる。

```python
from optimizer import RocketSimulator, list_components

with RocketSimulator("simple.ork") as sim:
    components = list_components(sim.orh, sim.rocket)
    for c in components:
        print(f"  {c['name']} ({c['type']})")
```
