---
name: inspect-rocket
description: .orkファイルのコンポーネント構成とベースライン性能を確認する
agent: optimizer
---

# inspect-rocket: ロケット構成確認

## いつ使うか

- 最適化ワークフローの**最初のステップ**として必ず実行する
- 新しい .ork ファイルを扱うとき
- コンポーネント名を確認したいとき

## 参照ドキュメント

- `docs/simple-ork-components.md` — コンポーネント構成の説明
- `docs/flight-data-types.md` — 取得可能なデータ種類
- `docs/flight-events.md` — イベント一覧

## 入力

- `.ork` ファイルパス（デフォルト: `simple.ork`）

## 手順

以下のPythonコードを `uv run python -c "..."` で実行する。

```python
import json
from optimizer import (
    RocketSimulator, list_components, ObjectiveFunction,
    Extraction, Direction,
)

ork_file = "simple.ork"  # ← 対象ファイルに変更

with RocketSimulator(ork_file) as sim:
    # 1. コンポーネント一覧
    components = list_components(sim.orh, sim.rocket)
    print("## コンポーネント構成\n")
    for c in components:
        print(f"- **{c['name']}** ({c['type']})")

    # 2. ベースラインシミュレーション
    objectives = [
        ObjectiveFunction("max_altitude", "TYPE_ALTITUDE", Extraction.MAX, Direction.MAXIMIZE),
        ObjectiveFunction("max_speed", "TYPE_VELOCITY_TOTAL", Extraction.MAX, Direction.MAXIMIZE),
        ObjectiveFunction("max_accel", "TYPE_ACCELERATION_TOTAL", Extraction.MAX, Direction.MAXIMIZE),
        ObjectiveFunction("landing_drift", "TYPE_POSITION_XY", Extraction.FINAL, Direction.MINIMIZE),
        ObjectiveFunction("landing_speed", "TYPE_VELOCITY_TOTAL", Extraction.FINAL, Direction.MINIMIZE),
        ObjectiveFunction("stability_min", "TYPE_STABILITY", Extraction.MIN, Direction.MAXIMIZE),
        ObjectiveFunction("flight_time", "TYPE_TIME", Extraction.MAX, Direction.MAXIMIZE),
    ]
    result = sim.run_and_extract(objectives)

    print("\n## ベースライン性能\n")
    for name, value in result.items():
        print(f"- **{name}**: {value:.4f}")
```

## 出力

実験ディレクトリに `baseline.md` として保存する。内容:

1. **コンポーネントツリー**: 名前・型の一覧
2. **ベースライン性能**: デフォルト設計での主要メトリクス
   - 最高高度 (m)
   - 最大速度 (m/s)
   - 最大加速度 (m/s^2)
   - 着地ドリフト (m)
   - 着地速度 (m/s)
   - 最小安定余裕 (cal)
   - 飛行時間 (s)

## 判断ゲート

- コンポーネント名が正しく取得できない場合 → `.ork` ファイルのパスを確認
- ベースラインで `TUMBLE` イベントが発生する場合 → 元の設計に安定性の問題あり。ユーザーに報告
- 全値が NaN の場合 → JVM / Java バージョンを確認（Java 17が必要）

## 注意事項

- このスキルは**読取専用**（設計変更なし）
- JVMは `with RocketSimulator()` ブロック内でのみ有効
- `plt.show()` は使用しない
