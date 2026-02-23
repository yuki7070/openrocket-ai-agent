# openrocket-ai-agent

OpenRocketをPythonから操作し、ロケット設計のシミュレーションと多目的最適化を行うエージェントリポジトリです。

## Requirements

- Python 3.12 (`uv` で依存管理)
- Java 17 (`sdk env install`)
- `OpenRocket-15.03.jar`（リポジトリルート）

## Quick Start

```bash
uv sync
uv run python examples/main.py
```

## Repository Structure

- `optimizer/` - 最適化ワークフロー本体（DOE / サロゲート / NSGA-II / 可視化）
- `docs/` - API・設計変数・制約・FlightDataのリファレンス
- `examples/` - 実行サンプル（旧ルート直下の `main/lazy/monte_carlo`）
- `experiments/` - 実験結果の出力先（通常はGit管理しない）
- `simple.ork` - デフォルトのロケット設計

## Agent Guidance

- `AGENTS.md` - OpenCode向け運用指示（ワークフロー/ガバナンス）
- `CLAUDE.md` - Claude向け開発ガイド

## Notes

- JPypeのJVMは1プロセスで1回のみ起動可能なため、DOEや検証は1つの実行ブロックで完結させてください。
- JVM使用時は `plt.show()` を避け、`matplotlib.use("Agg")` で画像保存ベースの運用を推奨します。
