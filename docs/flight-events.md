# FlightEvent 一覧

## 概要

`FlightEvent` はシミュレーション中に発生する離散イベントを表す。`orhelper.FlightEvent` として利用可能。各イベントには発生時刻 (秒) が記録される。

## イベント取得方法

```python
from orhelper import FlightEvent

# シミュレーション後にイベント取得
events = orh.get_events(sim)
# events: dict[FlightEvent, list[float]]  （イベント → 発生時刻リスト）

for event, times in events.items():
    print(f"{event}: {times}")
```

## FlightEvent 一覧

| FlightEvent | 説明 | 工学的な意味 |
|---|---|---|
| `LAUNCH` | 打ち上げ（t=0） | シミュレーション開始点 |
| `IGNITION` | エンジン点火 | 推力開始 |
| `LAUNCHROD` | ランチロッド離脱 | ロケットが発射台ガイドを離れた瞬間。この時点以降にロケットは自由飛行する |
| `LIFTOFF` | 離陸 | 地面から離れた瞬間 |
| `BURNOUT` | 燃焼終了 | 推進薬が燃え尽きた瞬間。以降は慣性飛行 |
| `EJECTION_CHARGE` | 放出薬点火 | パラシュート展開のためのイジェクションチャージ発火 |
| `APOGEE` | 最高到達点 | 高度が最大になる瞬間。通常パラシュート展開のトリガー |
| `RECOVERY_DEVICE_DEPLOYMENT` | 回収装置展開 | パラシュートやストリーマーが開く瞬間 |
| `GROUND_HIT` | 着地 | ロケットが地面に到達。着地速度が安全性の指標 |
| `SIMULATION_END` | シミュレーション終了 | シミュレーションの最終時刻 |
| `TUMBLE` | タンブリング | ロケットが安定を失い回転を始めた瞬間。安定余裕不足の兆候 |
| `EXCEPTION` | 例外発生 | シミュレーション計算中にエラーが発生 |
| `SIM_ABORT` | シミュレーション中断 | シミュレーションが異常終了 |
| `STAGE_SEPARATION` | ステージ分離 | 多段ロケットのステージ分離 |

## 典型的なイベント順序（単段ロケット）

```
LAUNCH → IGNITION → LIFTOFF → LAUNCHROD → BURNOUT
  → EJECTION_CHARGE → APOGEE → RECOVERY_DEVICE_DEPLOYMENT
  → GROUND_HIT → SIMULATION_END
```

## examples/main.py での使用例

```python
events_to_annotate = {
    FlightEvent.BURNOUT: 'Motor burnout',
    FlightEvent.APOGEE: 'Apogee',
    FlightEvent.LAUNCHROD: 'Launch rod clearance',
}
```

## 注意事項

- 全イベントが必ず発生するわけではない（例: 回収装置がない場合 `RECOVERY_DEVICE_DEPLOYMENT` は発生しない）
- `TUMBLE` が発生する場合、ロケット設計の安定性に問題がある可能性が高い
- イベント時刻はリストで返される（同種のイベントが複数回発生する場合がある）
