# simple.ork コンポーネント構成

## 概要

`simple.ork` はこのプロジェクトのデフォルトロケット設計ファイル。基本的な単段ロケットの構成で、最適化のベースラインとして使用する。

## コンポーネントの確認方法

```python
from optimizer import RocketSimulator, list_components

with RocketSimulator("simple.ork") as sim:
    components = list_components(sim.orh, sim.rocket)
    for c in components:
        print(f"  {c['name']} ({c['type']})")
```

## コンポーネントツリー（想定構成）

以下は `list_components()` で取得される典型的な構成。実際の名前は `.ork` ファイルの内容に依存する。

```
Rocket (Rocket)
└── Sustainer (Stage)
    ├── Nose cone (NoseCone)
    ├── Body tube (BodyTube)
    │   ├── Trapezoidal fin set (TrapezoidalFinSet)
    │   ├── Inner tube (InnerTube)
    │   │   └── Motor (Motor)
    │   └── Parachute (Parachute)
    └── ...
```

**注意**: 正確なコンポーネント名は `list_components()` で確認すること。最適化の `component_name` にはここで確認した名前を使用する。

## 設計変数として使えるプロパティ

各コンポーネントで操作可能な主なプロパティ:

### Nose cone (NoseCone)

| プロパティ | カタログキー | メソッド | 単位 |
|---|---|---|---|
| 長さ | `nose_length` | `setLength` / `getLength` | m |

### Body tube (BodyTube)

| プロパティ | カタログキー | メソッド | 単位 |
|---|---|---|---|
| 長さ | `body_tube_length` | `setLength` / `getLength` | m |

### Trapezoidal fin set (TrapezoidalFinSet)

| プロパティ | カタログキー | メソッド | 単位 |
|---|---|---|---|
| 根元弦長 | `fin_root_chord` | `setRootChord` / `getRootChord` | m |
| 先端弦長 | `fin_tip_chord` | `setTipChord` / `getTipChord` | m |
| 高さ | `fin_height` | `setHeight` / `getHeight` | m |
| 枚数 | `fin_count` | `setFinCount` / `getFinCount` | - |

### Parachute (Parachute)

| プロパティ | カタログキー | メソッド | 単位 |
|---|---|---|---|
| 直径 | `parachute_diameter` | `setDiameter` / `getDiameter` | m |

## ベースライン性能の取得

デフォルト値でのシミュレーション結果を取得するコード:

```python
from optimizer import (
    RocketSimulator, ObjectiveFunction, Extraction, Direction,
    list_components, get_current_values, DesignVariable, VARIABLE_CATALOG,
)

with RocketSimulator("simple.ork") as sim:
    # コンポーネント一覧
    components = list_components(sim.orh, sim.rocket)
    for c in components:
        print(f"  {c['name']} ({c['type']})")

    # ベースラインシミュレーション
    objectives = [
        ObjectiveFunction("max_altitude", "TYPE_ALTITUDE", Extraction.MAX, Direction.MAXIMIZE),
        ObjectiveFunction("max_speed", "TYPE_VELOCITY_TOTAL", Extraction.MAX, Direction.MAXIMIZE),
        ObjectiveFunction("landing_drift", "TYPE_POSITION_XY", Extraction.FINAL, Direction.MINIMIZE),
    ]
    result = sim.run_and_extract(objectives)
    for name, value in result.items():
        print(f"  {name}: {value:.2f}")
```

## 注意事項

- `.ork` ファイルはバイナリ形式（ZIP圧縮XML）のため直接読めない
- コンポーネント名はOpenRocket GUI上で変更可能なので、`list_components()` で確認が必須
- デフォルト設計は最適化されていないため、改善余地が大きい
