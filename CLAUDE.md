# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

OpenRocketのシミュレーションをPythonから操作するプロジェクト。`orhelper`ライブラリを介してOpenRocket (Java) のAPIをPythonから呼び出し、ロケットの飛行シミュレーションとデータ可視化を行う。

## 必須環境

- **Python 3.12** (`uv`でパッケージ管理)
- **Java 17** (SDKMAN経由: `sdk env install` で `.sdkmanrc` から自動インストール)
- **OpenRocket 15.03** (`OpenRocket-15.03.jar` がリポジトリルートに同梱)

## コマンド

```bash
# 依存関係インストール
uv sync

# シミュレーション実行
uv run python examples/main.py
```

## アーキテクチャ

- `orhelper.OpenRocketInstance()` がJVM (JPype経由) を起動し、`OpenRocket-15.03.jar`をロードする
- `.ork`ファイル (OpenRocketのロケット設計ファイル) を読み込み、シミュレーションを実行
- `FlightDataType`で時系列データ (時間, 高度, 速度等) を取得、`FlightEvent`でイベント (バーンアウト, 最高到達点等) を取得
- **重要**: `plt.show()` 等のUI操作は `OpenRocketInstance` のコンテキストマネージャの**外側**で行う必要がある (JVMのシャットダウン後)

## optimizer パッケージ

`optimizer/` パッケージはロケット設計の多目的最適化ワークフローを提供する。

### モジュール構成

| モジュール | 役割 |
|---|---|
| `jvm_patch.py` | `--add-opens` パッチ（import時に自動適用） |
| `design_space.py` | 設計変数・目的関数・制約のデータクラス定義 |
| `simulation.py` | `RocketSimulator` コンテキストマネージャ |
| `doe.py` | LHS実験計画 + DOE実行 |
| `surrogate.py` | RBFサロゲートモデル + LOO R^2検証 |
| `pareto.py` | NSGA-IIによる多目的最適化 + knee point抽出 |
| `visualize.py` | パレートフロント・DOE散布図・候補比較チャート |

### 使い方（対話的ワークフロー）

```python
from optimizer import *

# 1. 問題定義
problem = OptimizationProblem(
    ork_file="simple.ork",
    variables=[DesignVariable(...)],
    objectives=[ObjectiveFunction(...)],
    constraints=[Constraint(...)],
)

# 2. DOE生成 + 実行
samples = generate_lhs(problem, n_samples=30)
with RocketSimulator(problem.ork_file) as sim:
    doe_results = run_doe(sim, problem, samples)

# 3. サロゲート構築
model = SurrogateModel()
model.fit(doe_results, problem)
print(model.format_r2_report())

# 4. NSGA-II最適化
pareto = run_nsga2(model, problem)
top3 = select_top3(pareto, problem)
print(format_results_table(top3, problem))

# 5. 可視化（JVMシャットダウン後）
import matplotlib.pyplot as plt
plot_pareto_front(pareto, problem, top3)
plt.show()
```

### 注意事項

- JPypeのJVMは1プロセスで1回しか起動できない → 全DOE実行は1つの`with RocketSimulator()`ブロック内で
- 極端なパラメータでOpenRocketが失敗する場合はNaN返却（自動処理）
- `VARIABLE_CATALOG` にノーズ長・ボディチューブ長・フィン諸元等のテンプレートあり
- `list_components(orh, rocket)` で.orkファイル内の全コンポーネントを動的に発見可能
