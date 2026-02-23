---
name: run-doe
description: DOEサンプル全点をシミュレーション実行し、結果を収集する
agent: optimizer
---

# run-doe: DOE実行

## いつ使うか

- `plan-doe` でサンプル計画が承認された後
- サロゲートモデル構築前のデータ収集として

## 参照ドキュメント

- `docs/optimizer-api.md` — `run_doe`, `format_doe_results_table` の仕様
- `docs/constraints-guide.md` — 制約チェックの仕組み

## 入力

- `problem.py`（問題定義）
- DOEサンプル数・シード（`plan-doe` で決定済み）

## 手順

### 重要: JVM制約

全DOEサンプルの実行は**1つの `uv run python -c "..."` コマンド内**で完結させる。JPypeのJVMは1プロセスで1回しか起動できない。

```python
import json, sys
sys.path.insert(0, ".")

exec(open("experiments/<実験ディレクトリ>/problem.py").read())

from optimizer import (
    RocketSimulator, generate_lhs, run_doe,
    format_doe_results_table,
)

# DOEサンプル生成（plan-doeと同じシード）
n_samples = 30  # ← plan-doeで決めた数
samples = generate_lhs(problem, n_samples=n_samples, seed=42)

# 全サンプルを1つのSimulatorブロック内で実行
with RocketSimulator(problem.ork_file) as sim:
    doe_results = run_doe(sim, problem, samples)

# 結果テーブル
table = format_doe_results_table(problem, doe_results)
print(table)

# feasible率
n_feasible = sum(1 for r in doe_results if r["feasible"])
print(f"\nFeasible: {n_feasible}/{len(doe_results)} ({100*n_feasible/len(doe_results):.0f}%)")

# JSON保存
with open("experiments/<実験ディレクトリ>/raw/doe_results.json", "w") as f:
    json.dump(doe_results, f, indent=2)
print("Saved raw/doe_results.json")
```

## 出力

実験ディレクトリに以下を保存:
- `doe_results.md` — 結果のMarkdown表 + feasible率サマリー
- `raw/doe_results.json` — 機械可読な生データ

## 判断ゲート

- **feasible率 < 50%** → 制約が厳しすぎる可能性。変数範囲の見直しを提案
- **feasible率 < 20%** → `define-problem` に戻って制約を緩和
- **NaN率 > 30%** → 変数範囲に極端な値が含まれている可能性。範囲を狭める
- **全点infeasible** → 制約の閾値を確認。ベースラインすら制約を満たさない可能性

## 注意事項

- 実行時間はサンプル数に比例（1点あたり数秒）
- 極端なパラメータでOpenRocketが失敗する場合は自動的にNaN返却
- `plt.show()` は使用しない
- `raw/` ディレクトリがない場合は事前に作成する
