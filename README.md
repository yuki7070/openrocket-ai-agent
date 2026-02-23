# openrocket-ai-agent

OpenCodeを使ってOpenRocketのロケット設計シミュレーションと多目的最適化を対話的に実行するエージェントリポジトリです。

## Requirements

- Python 3.12 (`uv` で依存管理)
- Java 17 (`sdk env install`)
- OpenCode CLI
- `OpenRocket-15.03.jar`（リポジトリルート）

## Quick Start

```bash
sdk env install
uv sync
opencode
```

`opencode` 起動後、`AGENTS.md` のワークフローに沿って「inspect-rocket -> define-problem -> ...」の順に進めると、ロケット設計最適化を一通り実行できます。

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
