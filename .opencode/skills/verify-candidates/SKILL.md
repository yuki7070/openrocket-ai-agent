---
name: verify-candidates
description: top3候補を実シミュレーションで検証し、サロゲート予測との誤差を確認する
agent: optimizer
---

# verify-candidates: 候補検証シミュレーション

## いつ使うか

- `run-optimization` でtop3候補が選出された後
- サロゲート予測値と実シミュレーション値の乖離を確認するため

## 参照ドキュメント

- `docs/optimizer-api.md` — `RocketSimulator.evaluate` の仕様
- `docs/constraints-guide.md` — 制約チェック

## 入力

- `problem.py`（問題定義）
- top3候補の設計ベクトル（`run-optimization` の結果）

## 手順

### 重要: JVM制約

全候補の検証は**1つの `uv run python -c "..."` コマンド内**で完結させる。

```python
import json, sys
sys.path.insert(0, ".")

exec(open("experiments/<実験ディレクトリ>/problem.py").read())

from optimizer import RocketSimulator, check_constraints

# top3候補（run-optimizationの出力から転記）
top3 = [
    {"label": "Knee point",   "x": [0.1, 0.08, ...]},  # ← 実際の値に置換
    {"label": "Best max_altitude", "x": [0.12, 0.06, ...]},
    {"label": "Most diverse",  "x": [0.07, 0.10, ...]},
]

# 全候補を1つのSimulatorブロック内で検証
with RocketSimulator(problem.ork_file) as sim:
    print("## 検証結果\n")
    for cand in top3:
        result = sim.evaluate(problem, cand["x"])
        feasible = check_constraints(problem, result)

        print(f"### {cand['label']}")
        print(f"- 設計値: {cand['x']}")
        for name, val in result.items():
            print(f"- {name}: {val:.4f}")
        print(f"- feasible: {'Yes' if feasible else 'No'}")
        print()

        cand["verified"] = result
        cand["verified_feasible"] = feasible
```

### サロゲート予測との比較

```python
    # 予測値と実測値の比較
    print("## サロゲート vs 実測 誤差\n")
    print("| 候補 | 目的関数 | 予測値 | 実測値 | 誤差(%) |")
    print("| --- | --- | --- | --- | --- |")
    for cand in top3:
        for obj in problem.objectives:
            predicted = cand.get("f", {})  # run-optimizationでの予測値
            actual = cand["verified"].get(obj.name, float("nan"))
            # 予測値がリストの場合
            if isinstance(predicted, list):
                j = [o.name for o in problem.objectives].index(obj.name)
                pred_val = predicted[j]
            else:
                pred_val = predicted.get(obj.name, float("nan"))
            if pred_val != 0:
                error_pct = abs(actual - pred_val) / abs(pred_val) * 100
            else:
                error_pct = float("nan")
            print(f"| {cand['label']} | {obj.name} | {pred_val:.4f} | {actual:.4f} | {error_pct:.1f}% |")
```

## 出力

実験ディレクトリに `verification.md` として保存:
- 各候補の実シミュレーション結果
- feasibility判定
- サロゲート予測 vs 実測の誤差表

## 判断ゲート

| 条件 | アクション |
|---|---|
| 全候補 feasible + 誤差 < 10% | 検証成功。`write-report` に進む |
| 一部候補が infeasible | infeasible候補をレポートから除外し注記 |
| 誤差 > 20% | サロゲート品質に問題。DOE追加を検討 |
| 全候補 infeasible | `define-problem` に戻って見直し |

## 注意事項

- top3の `x` ベクトルは `run-optimization` の出力から正確にコピーする
- `plt.show()` は使用しない
- 検証は3点のみなので高速（10秒以内）
