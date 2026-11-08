---
name: uv
description: uvによるPythonプロジェクト・依存関係・Python本体・ツール・スクリプトの管理、pipからの移行、CIやDockerとの統合、解決やビルド失敗の診断を行う。uvのコマンドや設定を選び、変更と検証まで実施するときに使う。
---

# uv

依頼に合うuvの管理方式を選び、宣言ファイル・ロック・実行環境の整合性を保って作業する。説明と報告はユーザーの言語に合わせる。

## 最初に判断する

- `uv --version` と対象コマンドの `--help` を確認する。新しい設定やpreview機能はインストール版との差を確認する。
- `pyproject.toml`、`uv.toml`、`uv.lock`、`.python-version`、requirements、workspaceルート、CI、既存の運用規約を読む。秘密情報を出力しない。
- プロジェクトの継続管理は `uv add/remove/lock/sync/run`、単発スクリプトはPEP 723、外部CLIは `uvx` / `uv tool`、requirements中心の既存環境は `uv pip`。依頼なく方式を移行しない。
- Pythonのサポート範囲 `requires-python` とローカル選択 `.python-version` を区別する。仮想環境をactivateせず `uv run` で実行できる。

## 必要な参照だけ読む

- [プロジェクト・Python・ツール・スクリプト](references/projects.md): 導入、PEP 723、依存追加、extras/groups、sources、workspace、lock/sync、build/export/publish、pipからの移行。
- [統合](references/integrations.md): Docker、CI、Jupyter/marimo、PyTorch、FastAPI、クラウドindex、Lambda、依存更新。
- [設定・解決・認証・pip・診断](references/advanced.md): index優先順位、証明書、キャッシュ、preview、pip互換性、障害調査、内部構造、サポートポリシー。
- [CLI・設定・環境変数の選択](references/command-reference.md): コマンド群、設定の適用場所、環境変数、詳細仕様の検索方法。

## 変更の原則

- 依存追加は `uv add`、開発用は `uv add --dev`、用途別は `uv add --group test` などで宣言とlockを更新する。`uv pip install` だけでプロジェクト依存を追加したことにしない。
- 通常 `uv run` はlock確認と環境同期を行う。CIで鮮度を保証するなら `uv sync --locked`。`--frozen` はlock鮮度を検証しない。`--no-sync` は環境の整合性を呼び出し側が保証できる場合に限る。
- `uv sync` のexact同期は不要パッケージを除去し得る。対象環境を確認する。`--system` やsystem Pythonへの変更を既定にしない。
- private indexはパッケージとindexを明示的に結び、認証は環境変数やcredential provider等に分離する。接続失敗の回避にTLS検証無効化や無条件のindex混合を選ばない。
- build/publishでは `uv build --no-sources` 等で開発用sourcesへの依存を検査する。公開先・成果物を確認し、公開はユーザーの依頼範囲内でのみ行う。
- preview、プラットフォーム依存、editable、非パッケージプロジェクトの違いは対応する参照で確認する。uv.lockを手編集して解決結果を捏造しない。

## 検証して報告する

変更に応じてlock鮮度、選択したPython、インポート、既存テスト・lint/buildを最小範囲で検証する。CI設定はそこで実行するコマンドと同じ条件で確認する。依存解決が失敗したらPython範囲、markers、groups/extras、index認証、build依存の順に切り分け、理由を修正する。

報告には変更ファイル、採用したコマンド、検証結果、未検証の環境条件を含める。ネットワーク・認証不足で検証できなければ成功と扱わない。
