# CLI・設定・環境変数

<a id="p64"></a>
## Referenceの使い分け

操作はCommands、永続設定はSettings、一時的な実行条件やCI秘密値はEnvironment variablesで確認する。Storageはファイルの所在、Installer optionsは導入時だけの設定。実行時設定とinstallerの環境変数を混同しない。

<a id="p65"></a>
## Commands

まず `uv help`、詳細は `uv help <command>`、ネストした操作は `uv python install --help` のように調べる。Webでは `#uv-sync`、`#uv-pip-compile` 等の見出しを検索し、オプションの対象コマンド、default、競合条件を確認する。以下は選択用で、全オプションの複製ではない。

|目的|操作と判断|
|---|---|
|プロジェクト作成|`uv init`。アプリと `--lib`、パッケージ化、build backendを選ぶ|
|依存の宣言|`uv add` / `uv remove`。dev/group/optional、URL/Git/pathのsourcesを区別|
|version管理|`uv version`。設定するversionと現在値の表示を区別しbackendの対応確認|
|ロックと環境|`uv lock` は解決、`uv sync` は環境反映、`uv run` は実行前整備。`--locked` と `--frozen` は同義でない|
|依存確認|`uv tree`。pip環境の場合は `uv pip tree/list/show/check/freeze`|
|外部形式|`uv export`。requirements等のformat、groups/extras、hashes、editableの相手側対応を確認|
|単独ツール|`uv tool run` (`uvx`)、永続導入は `uv tool install`、更新は `uv tool upgrade`。プロジェクトの環境とは分離|
|Python|`uv python list/install/find/pin/dir/uninstall`。バージョンと実装、管理対象を確認|
|pip互換処理|`uv venv` と `uv pip install/uninstall/compile/sync`。プロジェクトlockとは別系統|
|成果物|`uv build` と `uv publish`。sdistとwheel、公開先、認証を確認|
|保守|`uv cache dir/clean/prune`、`uv tool dir`、`uv self update`。インストール方式によって更新方法が異なる|
|認証|`uv auth` の対象serviceと `--help` を確認。値をログに露出しない|

共通の `--directory` は作業ディレクトリを変える。`--project` はプロジェクト発見先を指定するため、相対パスが関係する場合は同一視しない。`--offline` は既存cacheで成立する場合のみ成功する。`--no-config`、`--isolated` はコマンドによる意味の違いをhelpで確認する。`--preview` が必要な操作は安定機能として無条件に導入しない。

<a id="p66"></a>
## Settings

`pyproject.toml` の `[tool.uv]` と `uv.toml` のトップレベル設定を区別する。`[tool.uv.pip]` はpip専用で、projectコマンドに適用されるとは限らない。CLI・環境変数・プロジェクト/ユーザー/system設定の優先順位は configuration-files の参照を読む。

- `constraint-dependencies` は既に要求された依存を制約する。追加インストールの要求ではない。`override-dependencies` は要求を置換するため、依存元の互換性確認が必要。
- `build-constraint-dependencies` はbuild依存用でruntime制約とは別。これらroot専用設定をworkspace memberやuv.tomlに置いて効いたと判断しない。
- `environments` は解決対象のmarkers、`required-environments` はwheel利用可能性の要件に関係する。`requires-python` を狭める代用として無造作に設定しない。
- `conflicts` は排他的extras/groupsを宣言し、同時有効化を不可能にする。根拠なくresolverエラーを隠す用途にはしない。
- `sources` / `workspace` / `index` で取得元を指定する。`explicit = true` のindexは明示したパッケージに限定する。`index-strategy` の変更はdependency confusionの影響を評価する。
- `resolution`、`prerelease`、`fork-strategy`、`exclude-newer`、`dependency-metadata` はそれぞれ選択戦略・許容範囲・メタデータの前提を変える。lock diffとサポート環境で検証する。
- `no-build-isolation` と `extra-build-dependencies` を区別する。build環境を共有すると必要なbuild依存を事前に用意する責任が生じる。

例: 制約を宣言してから `uv lock`、`uv sync --locked` で解決・反映を分けて確認する。

```toml
[tool.uv]
constraint-dependencies = ["urllib3<3"]
```

設定表の型・default・環境変数対応を読んでから編集する。名前だけからTOMLの階層やCLIフラグを推測しない。

<a id="p67"></a>
## Environment variables

CIの一時条件や秘密値の注入に利用する。`added in` を参照してローカル版との互換性を確認する。値は子プロセスに継承されるので必要な範囲に限定する。

|分類|主な変数と用途|
|---|---|
|キャッシュ・環境|`UV_CACHE_DIR`、`UV_PROJECT_ENVIRONMENT`、`UV_PYTHON`。対象環境を確認しcacheとvenvを区別|
|Python取得|`UV_PYTHON_INSTALL_DIR`、`UV_PYTHON_INSTALL_MIRROR`。管理本体の保存先とdownload元|
|再現性|`UV_NO_SYNC`、`UV_FROZEN`、`UV_LOCKED`。skipと検証の差を保持|
|index|`UV_DEFAULT_INDEX`、`UV_INDEX`、`UV_INDEX_<NAME>_USERNAME` / `UV_INDEX_<NAME>_PASSWORD`。named indexの正規化規則は公式を確認|
|認証|`UV_PUBLISH_TOKEN` 等はsecret storeから注入。lockや成果物へ埋め込まない|
|通信|`UV_OFFLINE`、`UV_HTTP_TIMEOUT`、proxy/証明書設定。原因のないTLS無効化は避ける|
|供給元mirror|`UV_ASTRAL_MIRROR_URL`。全体mirrorより個別Python mirror等の設定が優先|
|build|`UV_BUILD_CONSTRAINT`、`UV_NO_BUILD_ISOLATION`。build依存とruntime依存を混同しない|

`VIRTUAL_ENV` はpip系とproject系で扱いが異なる場合がある。`uv run` のactive環境利用は `--active` 等のhelpを確認する。`UV_BREAK_SYSTEM_PACKAGES` はsystem環境変更を許可するため、通常のプロジェクト修復には使わない。列挙外の変数は元ページで対応CLI・値形式を確認する。
