---
name: plan-doe
description: Latin Hypercube Samplingで実験計画を生成し、カバレッジを確認する
agent: optimizer
---

# plan-doe: 実験計画生成

## いつ使うか

- `define-problem` で問題定義が完了した後
- DOE実行前のサンプル確認として

## 参照ドキュメント

- `docs/optimizer-api.md` — `generate_lhs`, `format_doe_table` の仕様

## 入力

- `problem.py`（問題定義）

## 手順

### 1. LHSサンプル生成

```python
import sys
sys.path.insert(0, ".")

# problem.py から問題定義を読み込む（execで実行）
exec(open("experiments/<実験ディレクトリ>/problem.py").read())

from optimizer import generate_lhs, format_doe_table

# サンプル数の目安: 変数の数 × 10 以上
n_samples = max(30, problem.n_var * 10)
samples = generate_lhs(problem, n_samples=n_samples, seed=42)

# サンプル表の生成
table = format_doe_table(problem, samples)
print(f"## DOE計画: {n_samples}サンプル\n")
print(table)
```

### 2. カバレッジ確認

サンプルの分布を確認する。

```python
import numpy as np

print("\n## 変数カバレッジ\n")
for i, var in enumerate(problem.variables):
    col = samples[:, i]
    print(f"- **{var.name}**: min={col.min():.4f}, max={col.max():.4f}, "
          f"range=[{var.lower_bound:.4f}, {var.upper_bound:.4f}]")
```

## 出力

実験ディレクトリに `doe_plan.md` として保存する:
- サンプル数
- LHSシード値
- 全サンプルのMarkdown表
- 各変数のカバレッジ情報

## 判断ゲート

- サンプル数が変数数の5倍未満 → サンプル追加を提案
- 変数範囲が狭すぎる場合（上限/下限の差が小さい） → 範囲の見直しを提案
- ユーザーにサンプル数の承認を得てから `run-doe` に進む

## 注意事項

- このスキルではシミュレーションは実行しない（計画のみ）
- `seed` を固定することで再現性を確保
- 整数変数（`fin_count`等）は自動的に丸められる
