---
name: build-surrogate
description: DOE結果からRBFサロゲートモデルを構築し、品質を検証する
agent: optimizer
---

# build-surrogate: サロゲートモデル構築

## いつ使うか

- `run-doe` でDOE結果が得られた後
- 十分なfeasible点がある場合（最低2点、推奨10点以上）

## 参照ドキュメント

- `docs/optimizer-api.md` — `SurrogateModel` の仕様

## 入力

- `problem.py`（問題定義）
- `raw/doe_results.json`（DOE結果）

## 手順

```python
import json, sys
sys.path.insert(0, ".")

exec(open("experiments/<実験ディレクトリ>/problem.py").read())

from optimizer import SurrogateModel

# DOE結果読み込み
with open("experiments/<実験ディレクトリ>/raw/doe_results.json") as f:
    doe_results = json.load(f)

# サロゲートモデル構築
model = SurrogateModel()
model.fit(doe_results, problem)

# LOO R^2品質レポート
report = model.format_r2_report()
print(report)

# 詳細スコア
scores = model.get_r2_scores()
print("\n## 詳細スコア\n")
for name, r2 in scores.items():
    print(f"- {name}: R^2 = {r2:.4f}")
```

## 出力

実験ディレクトリに `surrogate_report.md` として保存:
- 使用した学習点数
- 各目的関数のLOO R^2スコア
- 品質判定（good / acceptable / poor）

## 判断ゲート

| R^2 | 品質 | アクション |
|---|---|---|
| ≥ 0.9 | **good** | そのまま最適化に進む |
| ≥ 0.7 | **acceptable** | 注意して進む。結果の検証を重視 |
| < 0.7 | **poor** | DOEサンプルの追加を提案（`plan-doe` に戻る） |

- **全目的関数が good** → `run-optimization` に進む
- **1つでも poor** → 以下を検討:
  1. サンプル数を増やす（例: 30 → 60）
  2. 変数範囲を狭める
  3. 非線形性が高い変数を除外
- ユーザーに品質レポートを提示し、進行の判断を仰ぐ

## 注意事項

- サロゲートモデルはメモリ上にのみ存在（ファイル保存しない）
- DOE結果のNaN点は自動除外される
- 最低2点のfeasible点が必要（2点未満でエラー）
- カーネルはデフォルト `thin_plate_spline`（通常変更不要）
