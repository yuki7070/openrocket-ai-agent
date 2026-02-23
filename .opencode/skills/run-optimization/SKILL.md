---
name: run-optimization
description: NSGA-IIでパレート最適化を実行し、top3候補を選出する
agent: optimizer
---

# run-optimization: NSGA-II最適化実行

## いつ使うか

- `build-surrogate` でサロゲートモデルの品質が acceptable 以上のとき
- パレートフロントからtop3候補を選出したいとき

## 参照ドキュメント

- `docs/optimizer-api.md` — `run_nsga2`, `select_top3`, `format_results_table` の仕様

## 入力

- `problem.py`（問題定義）
- `raw/doe_results.json`（DOE結果 → サロゲート構築用）

## 手順

```python
import json, sys
sys.path.insert(0, ".")

exec(open("experiments/<実験ディレクトリ>/problem.py").read())

from optimizer import (
    SurrogateModel, run_nsga2, select_top3, format_results_table,
    plot_pareto_front, plot_doe_summary, plot_candidate_comparison,
)
import matplotlib
matplotlib.use("Agg")  # GUIなし
import matplotlib.pyplot as plt

# DOE結果読み込み + サロゲート構築
with open("experiments/<実験ディレクトリ>/raw/doe_results.json") as f:
    doe_results = json.load(f)

model = SurrogateModel()
model.fit(doe_results, problem)

# NSGA-II実行
pareto = run_nsga2(model, problem, pop_size=100, n_gen=200, seed=42)
print(f"Pareto solutions: {len(pareto['X'])}")

# top3候補選出
top3 = select_top3(pareto, problem)

# 結果テーブル
table = format_results_table(top3, problem)
print(table)

# --- 可視化 ---
exp_dir = "experiments/<実験ディレクトリ>"

# パレートフロント
fig1 = plot_pareto_front(pareto, problem, top3)
fig1.savefig(f"{exp_dir}/pareto_front.png", dpi=150, bbox_inches="tight")
print(f"Saved pareto_front.png")

# DOEサマリー
fig2 = plot_doe_summary(doe_results, problem)
fig2.savefig(f"{exp_dir}/doe_summary.png", dpi=150, bbox_inches="tight")
print(f"Saved doe_summary.png")

# 候補比較
fig3 = plot_candidate_comparison(top3, problem)
fig3.savefig(f"{exp_dir}/candidate_comparison.png", dpi=150, bbox_inches="tight")
print(f"Saved candidate_comparison.png")

plt.close("all")
```

## 出力

実験ディレクトリに以下を保存:
- `results.md` — top3候補のMarkdown表 + パレート解の数
- `pareto_front.png` — パレートフロント散布図（dpi=150）
- `doe_summary.png` — DOE散布図行列（dpi=150）
- `candidate_comparison.png` — 候補比較棒グラフ（dpi=150）

## 判断ゲート

- **パレート解が少ない（< 10）** → pop_size を増やす or n_gen を増やす
- **top3の目的関数値がベースラインとほぼ同じ** → 変数範囲の拡大を検討
- **top3の設計値が全て境界上** → 変数範囲の拡大を検討
- 結果をユーザーに提示し、`verify-candidates` に進むか確認

## 注意事項

- `matplotlib.use("Agg")` で GUI バックエンドを無効化（`plt.show()` は使用しない）
- 画像は `dpi=150` で PNG 保存
- NSGA-IIはサロゲート上で動作するため高速（数秒）
- `plt.close("all")` でメモリ解放
