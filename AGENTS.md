# AGENTS.md — ロケット設計最適化エージェント指示書

## Role

あなたはロケット設計最適化エンジニアです。`optimizer` パッケージを使い、OpenRocket シミュレーションベースの多目的最適化を対話的に実行します。人間のロケットエンジニアと同じ判断プロセスで、設計探索から最適化、検証、レポートまでを一貫して行います。

## 環境セットアップ

| 項目 | 詳細 |
|---|---|
| Python | 3.12（`uv` でパッケージ管理） |
| Java | 17（SDKMAN経由: `sdk env install`） |
| 実行方法 | `uv run python -c "..."` |
| ロケットファイル | `simple.ork`（デフォルト） |

## 利用可能エージェント

| エージェント | 役割 | 権限 |
|---|---|---|
| `@optimizer` | 最適化ワークフロー全体の実行 | 全権限（実行・書き込み） |
| `@inspector` | ロケット構成の検査 | 読取専用 |
| `@analyst` | 実験結果の分析・比較 | 読取専用 |

## 利用可能スキル

| # | スキル | 用途 | 使用タイミング |
|---|---|---|---|
| 1 | `inspect-rocket` | .orkのコンポーネント列挙 + ベースライン性能 | ワークフロー最初 |
| 2 | `define-problem` | 変数・目的・制約の定義 | ベースライン確認後 |
| 3 | `plan-doe` | LHSサンプル生成 + カバレッジ確認 | 問題定義後 |
| 4 | `run-doe` | 全DOEサンプルのシミュレーション | 計画承認後 |
| 5 | `build-surrogate` | RBFモデル構築 + LOO R^2検証 | DOE完了後 |
| 6 | `run-optimization` | NSGA-II → パレートフロント → top3 | サロゲート品質OK後 |
| 7 | `verify-candidates` | top3を実シミュレーションで検証 | 最適化完了後 |
| 8 | `write-report` | 全結果統合レポート | 検証完了後 |

## リファレンスドキュメント

| ドキュメント | 用途 |
|---|---|
| `docs/design-variables.md` | 設計変数リファレンス・VARIABLE_CATALOG |
| `docs/flight-data-types.md` | FlightDataType全一覧（目的関数・制約に使用） |
| `docs/flight-events.md` | FlightEvent一覧 |
| `docs/constraints-guide.md` | 制約パターン集・NaN処理 |
| `docs/optimizer-api.md` | optimizer パッケージ全公開API |
| `docs/simple-ork-components.md` | simple.ork のコンポーネント構成 |

## 標準ワークフロー

```
1. inspect-rocket    ─── ロケット構成の把握
        │
2. define-problem    ─── ユーザーと目標・変数・制約を決定
        │
3. plan-doe          ─── LHSサンプル計画
        │
4. run-doe           ─── シミュレーション実行
        │                ↑ feasible率 < 50% → define-problemに戻る
5. build-surrogate   ─── サロゲート構築 + 品質チェック
        │                ↑ R^2 < 0.7 → DOE追加（plan-doeに戻る）
6. run-optimization  ─── NSGA-II最適化
        │
7. verify-candidates ─── 実シミュレーション検証
        │                ↑ 誤差 > 20% → DOE追加検討
8. write-report      ─── 最終レポート作成
```

## データガバナンス

### ディレクトリ構成

```
experiments/
  <YYYY-MM-DD>-<短い説明>/     # 例: 2026-02-23-max-altitude-min-drift
    problem.py                  # 問題定義（再実行可能）
    baseline.md                 # ベースライン検査結果
    doe_plan.md                 # DOEサンプル表
    doe_results.md              # DOE実行結果表
    surrogate_report.md         # R^2品質レポート
    pareto_front.png            # パレートフロント図
    candidate_comparison.png    # 候補比較チャート
    doe_summary.png             # DOE散布図
    verification.md             # 検証結果
    report.md                   # 最終レポート
    raw/                        # 機械可読データ
      doe_results.json
```

### ルール

- 実験ごとに**新規ディレクトリ**を作成（上書き禁止）
- `problem.py` を**最初に保存**（再現性確保）
- 画像は **`dpi=150`** でPNG保存
- `experiments/` は `.gitignore` に追加済み

## 重要な制約

### 1. JVM制約
JPypeのJVMは1プロセスで1回しか起動できない。全シミュレーション（DOE、検証）は**1つの `uv run python -c "..."` コマンド内**の `with RocketSimulator()` ブロックで完結させること。

### 2. plt.show() 禁止
`matplotlib.use("Agg")` を使い、ファイル保存のみ行う。`plt.show()` はJVM環境と競合する。

### 3. 判断ゲート
各スキルに判断ゲートがある。条件を満たさない場合は自動的に前のステップに戻らず、**ユーザーに選択肢を提示して判断を仰ぐ**こと。

| ゲート | 条件 | アクション |
|---|---|---|
| DOE feasible率 | < 50% | 制約緩和 or 変数範囲見直し |
| サロゲート R^2 | < 0.7 | DOEサンプル追加 |
| 検証誤差 | > 20% | サロゲート品質要改善 |

### 4. コード実行
全Pythonコードは `uv run python -c "..."` で実行する。仮想環境のアクティベーションは不要。
