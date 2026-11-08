# uvの日常操作・プロジェクト設計


<a id="p0"></a>
## uv全体像

uvはPython本体、プロジェクト依存、単独スクリプト、CLIツールを扱う。それぞれ環境の境界が違う。`pyproject.toml` のある開発では `uv add` / `uv run` / `uv sync`、単独スクリプトではPEP 723、プロジェクトから独立したCLIでは `uvx`、既存requirements運用では `uv pip` を選ぶ。`uv pip install` で追加した依存はプロジェクト宣言に保存されない。

<a id="p1"></a>
## Getting startedの読み分け

未導入なら次節、導入済みなら `uv --version` と `uv --help` で実体を確認する。最初の作業手順は本資料のガイド節、設定の意味は概念節、全オプションは公式Referenceへ進む。最初から手動venv管理を導入する必要はない。

<a id="p2"></a>
## インストール・更新・削除

既存の導入経路を確認してから更新する。standalone版は `uv self update`、Homebrew等の版は元のパッケージマネージャーで更新する。standaloneインストーラーは `https://astral.sh/uv/install.sh`（Unix）と `https://astral.sh/uv/install.ps1`（Windows）。固定版はURLの `uv/` と `install` の間にバージョンを挿入する。PyPIなら独立環境への `pipx install uv`、Homebrewなら `brew install uv` も選べる。Cargo導入はRustビルドが必要。

補完は `uv generate-shell-completion zsh` 等で生成し、利用シェルの設定に組み込む。uvxは別途 `uvx --generate-shell-completion zsh`。自己更新時のPATH変更を避けるなら `UV_NO_MODIFY_PATH=1`。削除時は導入元と `uv cache dir` / `uv python dir` / `uv tool dir` を調べる。Pythonやツール保存領域の削除はそれらを使う環境も壊し得るため、バイナリ削除と一括データ消去を同一視しない。

<a id="p3"></a>
## 最初の動作確認

`uv` 単独実行でヘルプが表示されることを確認する。見つからない場合は再インストールより先にPATHと実行ファイルの場所を確認する。以後は目的に応じてプロジェクト、スクリプト、ツールのいずれかの手順へ進む。

<a id="p4"></a>
## コマンド群の選択

- Python: `uv python install/list/find/pin/uninstall`。
- プロジェクト: `uv init/add/remove/lock/sync/run/tree/build/publish`。
- スクリプト: `uv run`、`uv add --script`、`uv remove --script`。
- ツール: `uvx`、`uv tool install/list/upgrade/uninstall/update-shell`。
- 手動環境: `uv venv`、`uv pip install/sync/compile/list/check/tree`。
- 状態: `uv cache dir/prune/clean`、`uv self update`。

pip互換は完全同一動作という意味ではない。既存CIの単純な文字列置換は互換性資料と照合する。

<a id="p5"></a>
## ヘルプ・診断情報

`uv <command> --help` は短い説明、`uv help <command>` は詳細説明。診断には `uv sync -v`、必要なら `-vv` を使い、ログを共有する前に認証情報を除く。uv本体の版は `uv self version` / `uv --version`。`uv version` は現在はプロジェクトの版であり、uv本体の版と混同しない。再現条件と版を揃え、公式troubleshootingと既知issueを確認してから報告する。

<a id="p6"></a>
## ガイドの入口

Python導入、単独スクリプト、CLI、プロジェクト、配布の順に必要な節だけ読む。Docker、CI、GPUパッケージ等の環境固有手順はintegration資料へ進み、一般的な `uv sync` 例をそのまま転用しない。

<a id="p7"></a>
## Pythonを導入する

`uv python install 3.12` で系列を指定し、複数なら `uv python install 3.11 3.12`。一覧は `uv python list`。通常は必要時に自動ダウンロードするので、事前導入は必須ではない。CPython配布はAstralのpython-build-standalone由来。既存Pythonを使うなら通常は自動検出され、managed版を使わせない場合は `--no-managed-python`。

既定ではバージョン付き実行ファイルを配置する。`python` / `python3` の配置は実験的な `--default`。同一系列のpatch更新は `uv python upgrade 3.12`、再導入は `uv python install --reinstall`。minorを上げる変更とは分けて検証する。

<a id="p8"></a>
## 単独スクリプトとPEP 723

依存なしなら `uv run example.py arg`。プロジェクト配下では通常その環境を使うため、独立実行は `uv run --no-project example.py`。一時依存は `uv run --with 'rich>=13' example.py`。uv用フラグはスクリプト名より前に置く。

共有するスクリプトは宣言を保存する:

```sh
uv init --script example.py --python 3.12
uv add --script example.py requests rich
uv lock --script example.py
uv run example.py
```

PEP 723ブロックは `# /// script` と `# ///` で囲み、`dependencies = []` は空でも必須。`requires-python` も指定できる。inline metadata付きのスクリプトはプロジェクト配下でもプロジェクト依存を無視する。lockは自動作成されず、上の明示操作で隣接する `example.py.lock` を作る。作成後のrun/add/export/treeはlockを再利用し、必要時更新する。

Unix実行ファイルには `#!/usr/bin/env -S uv run --script` と実行権限を使える。`uv run -` はstdin実行。代替indexは `uv add --index URL --script example.py PACKAGE` でinline設定に保存できる。公開日時制限にはinline `[tool.uv]` の `exclude-newer`（RFC 3339日時）を使う。Windowsの `.pyw` はpythonwでGUI実行される。

<a id="p9"></a>
## CLIツールを実行・常設する

一度使うCLIは `uvx ruff check .`。パッケージとコマンド名が違えば `uvx --from httpie http`。固定版は `uvx --from 'ruff==0.6.0' ruff check .`、最新確認は `uvx ruff@latest check .`。範囲制約やextras、Git URLは `--from` に渡す。pluginは `uvx --with mkdocs-material mkdocs --help`。

他プログラムからPATH上で呼ぶ必要があれば `uv tool install ruff`、PATH設定は `uv tool update-shell`。更新は `uv tool upgrade ruff` / `--all`。更新は導入時の範囲制約を維持し、制約そのものを変えるなら `uv tool install 'ruff>=0.6'`。Pythonを指定するならrun/install/upgradeに `--python 3.12` を付ける。

プロジェクトのimportや依存が必要なpytest/mypyは `uv run` を使う。tool installはプロジェクトへのimport可用性を提供しない。依存側CLIも公開したい場合は `--with-executables-from` を使い、単なる `--with` と区別する。

<a id="p10"></a>
## プロジェクトを動かす

```sh
uv init example
cd example
uv add requests
uv add --dev pytest
uv run python -c 'import requests; print(requests.__version__)'
uv run pytest
```

`pyproject.toml` は要求、`uv.lock` は解決結果、`.python-version` は実行Pythonの選択、`.venv` はローカルの実体。前二者はバージョン管理し、lockは手編集しない。`uv add/remove` は宣言・lock・環境を更新する。`uv run` は実行前にlockと環境を確認するので通常activate不要。エディター向けには `uv sync` で環境を作り、そのPythonを選ぶ。

依存更新は `uv lock --upgrade-package requests`、配布物は `uv build`。プロジェクト版確認は `uv version --short` または `uv version --output-format json`。`uv run` は既定で余剰パッケージを残す点に注意する。

<a id="p11"></a>
## ビルド・版更新・公開

`[build-system]` を明示し、公開前に `uv build --no-sources` でuv固有の開発ソース指定なしでもビルドできるか確認する。`uv build` は `dist/` にsdistとwheelを出す。別ディレクトリは `uv build PATH`、workspaceは `uv build --package NAME`。

版変更は `uv version 1.0.0` または `uv version --bump patch`。`--dry-run` で確認でき、既定でlock/syncも行う。`--no-sync` はsyncのみ、`--frozen` はlockとsyncを止める。pre-releaseから安定版には `--bump stable`。

公開が依頼されている場合に `uv publish` を実行する。PyPIはtokenまたはTrusted Publishingを使い、パスワード認証を前提にしない。カスタムindexは `[[tool.uv.index]]` に `url` と `publish-url` を設定し `uv publish --index NAME`。この方法はpyprojectを必要とする。途中失敗の再試行は同一artifactで行い、他registryでは `--check-url` のindex URLで既存ファイル同一性を照合する。

attestationは別途生成が必要で、uv publishは対応する `.publish.attestation` を発見してuploadする。非対応registryでは `--no-attestations`。公開後のimport確認は `uv run --no-project --with PACKAGE python -c 'import MODULE'` とし、ローカルcheckoutを誤って検証しない。

<a id="p12"></a>
## 移行方針

requirements運用を維持する `uv pip` への置換と、`pyproject.toml` / `uv.lock` のプロジェクト運用への移行を分ける。現行の公式移行ガイドは後者のpip/pip-toolsからの移行を扱う。既存の入力requirementsと生成されたpin一覧を区別してから次節へ進む。

<a id="p13"></a>
## pip / pip-toolsからプロジェクトへ

既存アプリの実行方法と入力依存を確認し、必要なら `uv init --bare` で最小pyprojectを作る。直接依存を宣言する `.in` を優先し、生成済み `.txt` はバージョン維持のconstraintに使う:

```sh
uv add -r requirements.in -c requirements.txt
uv add --dev -r requirements-dev.in -c requirements-dev.txt
uv sync
```

開発用入力に `-r requirements.in` が含まれる場合、通常依存をdevへ重複登録しないよう内容を整理する。`.txt` しかなければ `uv add -r requirements.txt` も可能だが、推移依存まで直接依存として固定されることを説明する。必要なら後で真の直接依存を特定して緩和する。既存手動venvのfreezeを無条件に正解としない。

プロジェクト操作ではactivateから `uv run` に置き換え、テストとエントリポイントを確認する。requirementsにしか表現されていないindex、editable、constraints等はpyprojectの対応設定へ移す。生成物への依存が残る間は旧ファイルを削除せず、CIやDockerも移行したうえで一本化する。

<a id="p32"></a>
## Conceptsの入口

操作が期待と違う場合は、プロジェクト、Python選択、設定探索、index、resolver、認証、cacheのどの境界か切り分ける。単に再installせず、対象概念の資料を参照する。

<a id="p33"></a>
## Projectsの概念

最初にlayout、init、依存宣言、run、lock/syncを確認する。配布するならconfig/build/export、複数パッケージならworkspaceを追加で読む。単なるフォルダの集合と単一lockを共有するworkspaceを区別する。

<a id="p34"></a>
## ファイル構造とlock

`pyproject.toml` に標準metadataと依存、`[tool.uv]` にuv設定を置く。`.venv` は通常プロジェクト直下に作られ、共有やcommitの対象にしない。`uv.lock` はOS/Python分岐を含むuniversal lockであり、現在の環境にすべての記録パッケージをinstallするわけではない。別ツールとの受け渡しはlock手編集でなく `uv export` を用いる。

<a id="p35"></a>
## 初期化の選択肢

取得時のuvでは `uv init` はbuild systemを持つpackaged projectを作る。古いuvの生成構造を前提にしない。ライブラリは `uv init --lib NAME`、flatな非packageアプリは `uv init --no-package NAME`、既存ファイルを活かす最小metadataは `uv init --bare`。`--bare` はREADME/source/版pin/Git初期化等を省略する。

拡張moduleは `uv init --build-backend maturin NAME`（Rust）またはscikit-build-core（C/C++等）を選ぶ。`--build-backend` はpackageを含意する。backendが実際の配布ファイル・editable挙動を決める。native source変更がcache keyに含まれず反映されない場合はkey設定を見直し、必要な対象だけ `--reinstall` する。

<a id="p36"></a>
## 依存宣言とソース

依存の所属を先に決める:

| 用途 | 保存先 | 例 |
| --- | --- | --- |
| 実行時・公開必須 | `project.dependencies` | `uv add httpx` |
| 利用者が選ぶ機能 | `project.optional-dependencies` | `uv add --optional network httpx` |
| 開発時のみ | `dependency-groups` | `uv add --dev pytest` / `uv add --group lint ruff` |
| 開発中の取得元 | `tool.uv.sources` | Git、URL、path、workspace、index |

`uv add 'httpx>=0.27,<1'` で範囲を変更しても既存lockが条件内なら更新されない。最新版が目的なら `--upgrade-package httpx` を併用する。削除も同じ `--dev` / `--group` / `--optional` を指定して所属を合わせる。markerは依存自体の条件（例 `"jax; sys_platform == 'linux'"`）と取得元のみの条件を区別する。

ソースの例:

```toml
[tool.uv.sources]
httpx = { git = "https://github.com/encode/httpx", rev = "COMMIT" }
local-lib = { path = "../local-lib", editable = true }
member = { workspace = true }
```

path依存は既定ではeditableではなく、workspace memberはeditable。Gitは `--tag` / `--branch` / `--rev` とsubdirectoryを使い分け、再現性が必要ならcommitを指定する。LFS利用は `--lfs` またはsourceの `lfs = true` とGit LFSの導入が必要。URLはwheel/sdistを指定する。index指定は名前付き `[[tool.uv.index]]` とsourceの `{ index = "name" }` を組み合わせ、専用indexは `explicit = true` で他packageへの波及を制限する。

sourcesはuv固有で公開標準metadataにはならない。配布互換確認には `uv lock --no-sources` / `uv build --no-sources`。複数sourceは重複しないmarker、extra、group条件で分ける。非packageを依存の束として使うvirtual dependencyはsourceの `package = false` を検討する。

devは既定で含まれ、他groupは `--group NAME` 等で選ぶ。`tool.uv.default-groups` で既定を変更でき、無効化は `--no-default-groups`。group内の `{ include-group = "lint" }` で再利用できる。全group/extrasは通常まとめて解決されるため、同時に使わないだけでは矛盾を回避できない。意図的な排他関係は `tool.uv.conflicts` で宣言する。groupだけ新しいPythonを要するなら `[tool.uv.dependency-groups]` にgroupの `requires-python` を指定する。旧 `tool.uv.dev-dependencies` より標準groupを使う。

<a id="p37"></a>
## プロジェクト内の実行

プロジェクト依存を使うPython、CLI、shell scriptは `uv run python ...` / `uv run CLI ...` / `uv run bash scripts/task.sh` で実行する。`uv run --with 'httpx==0.27.0' python ...` はその呼出し用の依存を重ね、宣言を書き換えない。要求した版はプロジェクト側の版と異なっていても使用できるため、通常テスト結果と混同しない。

PEP 723 scriptは独立環境となる。Windowsのlegacy scriptは `.ps1` / `.cmd` / `.bat` に対応し、コマンド名のみでもこの順に探索する。uvは子processにシグナルを転送するsupervisorなので、process置換と同一とは考えない。UnixのSIGKILL等は転送されず、WindowsのCtrl-C処理は子に委ねる。

<a id="p38"></a>
## lock・sync・更新の違い

| 操作 | 目的・重要な差 |
| --- | --- |
| `uv lock` | 宣言を解決してlockを作成・更新。通常は既存pinを優先 |
| `uv lock --check` | 宣言とlockの整合性検証。新releaseの存在は不整合ではない |
| `uv sync --locked` | lockの古さを検査し、更新が必要なら失敗。CI向け |
| `uv sync --frozen` | 宣言との古さ検査を省略して既存lockを使用 |
| `uv run --no-sync ...` | 環境の同期を省く。環境整合性は呼出し側の責任 |
| `uv lock --upgrade-package NAME` | 指定依存のcompatibleな更新を要求 |
| `uv lock --upgrade` | 全依存を宣言範囲内で更新 |

`--frozen` は「古いlockならエラー」の代用ではない。`uv run` と `uv tree` も既定でlockを更新し得る。CIで宣言とlockの不一致を検出したいなら `--locked` を選ぶ。

`uv sync` は既定で余剰packageを削除するexact同期、`uv run` は余剰を残すinexact同期。前者を緩めるなら `--inexact`、後者を厳格にするなら `--exact`。projectとworkspace memberは通常editableで、配布用は `--no-editable`。

extrasは既定で未選択、`--extra NAME` / `--all-extras` で含める。devは既定で選択。`--no-dev` はdev除外、`--only-dev` はprojectと通常依存を除きdevのみ、`--only-group NAME` は既定groupも除く。group除外は包含より優先する。

Docker等の段階installには `--no-install-project` / `--no-install-workspace` / `--no-install-package NAME`。除外対象の依存はなおinstallされるが、最終環境に必要なpackageを戻す工程を忘れない。Git branchも既存lockのcommitが優先され、追従更新はupgrade指定が必要。取得時点のmalware-checkはpreviewで、`audit.malware-check = true` または `UV_MALWARE_CHECK=1` でOSV照合できる。

<a id="p39"></a>
## プロジェクト設定とnative build

`requires-python` はサポート範囲、`.python-version` は実行Pythonの選択であり別物。console commandは `[project.scripts]`、GUI commandは `[project.gui-scripts]`、pluginは `[project.entry-points.GROUP]` を使い、entry pointを使うprojectはpackageとしてinstallする。

`[build-system]` がない現在のprojectはsync時に自身がinstallされない。`tool.uv.package = true/false` で強制できるが、falseでも明示的な `uv build` は動く。他の依存packageにbuild-systemがなくてもlegacy setuptoolsでbuildされ得る。

環境は既定で `.venv`。`UV_PROJECT_ENVIRONMENT` の相対pathはworkspace root基準、絶対pathはその場所を直接使う。複数projectに同じ絶対pathを与えると相互に上書き・余剰削除し得る。project操作は既定で `VIRTUAL_ENV` を採用せず、採用したいときに `--active` を付ける。

PEP 517のbuild isolationを維持し、足りないbuild依存はまず補完する:

```toml
[tool.uv.extra-build-dependencies]
cchardet = ["cython"]
deepspeed = [{ requirement = "torch", match-runtime = true }]
```

`match-runtime` はstatic metadataが得られるpackageで使う。dynamic metadataが必要なら実際のbuild条件を確認し、build/runtime双方へ同じexact versionを指定するか、確実な `tool.uv.dependency-metadata` を与える。推測したmetadataを登録しない。`extra-build-variables` でpackage固有build環境も設定でき、これらの変更はcache keyに反映される。

補完で解決できない場合に限り `no-build-isolation-package = ["NAME"]` を使い、必要build依存をproject環境へ先に用意する。uvは通常のpackageを先にinstallし、その後isolation無効対象をinstallする。解決段階からbuildが必要なら `uv venv` → `uv pip install BUILD_DEPS` → `uv sync` の事前準備が必要な場合もある。全体の `--no-build-isolation` を最初の解決策にしない。

意図的なextra/group排他は `conflicts`、解決対象platformの限定は `environments`。必要なwheel提供を保証したいplatformは `required-environments` を使い、特にsdistのない依存で効く。Linuxのlibc要件は `minimum-libc-version` と併せて設定する。

<a id="p40"></a>
## 配布物のbuild条件

uvはbuild frontendであり、収録ファイルやwheel名はbackendが決める。既定の `uv build` はsdistをbuildしてから、そのsdistからwheelをbuildする。`--sdist` / `--wheel` は単独形式、`--sdist --wheel` は両方をsourceから直接buildする。

build依存の再現性が必要なら `uv build --build-constraint constraints.txt --require-hashes` を検討する。全推移build依存のhashも必須にする `--require-build-hashes` は取得時点で実験的（`build-dependency-hashes`）。exact pinまたはdirect URLとhashを用意する。project解決/install向けには `build-constraint-dependencies` も使える。isolation無効時、既存install済みpackageや既にbuild済みwheelには同じhash再検証が働くとは限らない。

PyPIへ出したくない内部packageには `classifiers = ["Private :: Do Not Upload"]` を設定できる。これはPyPIの拒否措置であり、他registryのprivacy設定ではない。公開tokenもproject単位に限定する。

<a id="p41"></a>
## exportと相互運用

```sh
uv export --format requirements.txt --output-file requirements.txt
uv export --format pylock.toml --output-file pylock.toml
uv export --format cyclonedx1.5 --output-file sbom.json
```

requirementsは相互運用用で、uv.lockの表現をすべて保持できないため二重のsource of truthにしない。pylockはPEP 751形式。ローカル相対pathは出力先基準となるので、別directoryへ出す場合はshell redirectでなく `--output-file` を指定する。CycloneDX v1.5 JSONは取得時点でpreview。componentにmarkerやworkspace pathのuv拡張propertyが含まれる。対応formatやpreview状態は利用uvのヘルプで確認する。

<a id="p42"></a>
## workspace設計

関連packageが同じ解決結果を共有すべき場合にworkspaceを使う。rootの設定例:

```toml
[tool.uv.workspace]
members = ["packages/*"]
exclude = ["packages/experiments"]

[tool.uv.sources]
shared-lib = { workspace = true }
```

member側にもpyprojectが必要で、依存する側の標準dependenciesへ名前を記載する。workspace sourceはeditable。rootもmemberに含まれ、全体で単一uv.lockと互換な `requires-python` の共通範囲を使う。`uv lock` は全体、`uv run/sync` は既定でrootを対象とし、member指定は `--package NAME`。

rootのsourcesは各memberに適用されるが、memberが同じ名前のsourceを定義するとその名前についてroot定義を置き換える。member側markerが現在platformに不一致でもroot定義へ戻るわけではない。別workspaceのmember参照には `{ workspace = "../other-workspace" }` も使える。

衝突する依存や別venvが必要ならworkspaceにまとめず、独立projectとpath依存を選ぶ。workspaceはpackageごとのimport隔離を保証せず、別memberの依存を誤importできる。各memberが宣言した依存だけで動く検証は別途必要。

<a id="p43"></a>
## tool環境・cache・更新の意味

uvxはcache内の使い捨て環境、tool installはtool保存領域の永続環境を使う。どちらもprojectと独立し、環境をpipで直接改変せず、`uv tool install/upgrade` で再構成する。実行のみなら通常uvxで十分で、外部からPATHで呼ぶ用途にinstallを選ぶ。

uvxは初回に選んだ版をcacheから再利用し、毎回最新ではない。tool install済みなら既定でその版を使う。`@latest` は最新確認とcache refresh、`uvx --isolated TOOL` はinstall済み版を無視するがcache refreshの指定ではない。

`uv tool upgrade black --upgrade-package click` は対象環境の一依存更新、`--reinstall-package click` は再install。元の制約・設定を維持する。`--with` は依存だけ追加し、`--with-executables-from` は依存の実行ファイルもPATHへ公開する。衝突する実行ファイルを `--force` で置換する前に所有者を確認する。

toolのPython選択は非global `.python-version` とprojectの `requires-python` を無視するため、必要なら `--python` を明示する。toolが参照するPythonをuninstallするとtool環境も壊れ得る。

<a id="p44"></a>
## Python選択・更新・配布の詳細

managedはuvが導入したPython、systemはOS・Homebrew・pyenv等それ以外のPythonを指す。`--python 3.12`、`--python '>=3.11,<3.13'`、interpreterのpathで指定できる。`.python-version` は親directoryを探索するがproject/workspace境界を越えず、user設定directoryも参照する。`uv python pin 3.12` はローカル、`--global` はuser既定。`--no-config` で版file探索を止められる。

`uv python list --only-installed` で導入済み、`--all-versions` / `--all-platforms` で候補拡張。`uv python find` はvenvも優先し得るため、system探査は `uv python find --system`。managed候補は新しい版を優先、system候補は最初の互換実体を使う。既定は既存managed、既存system、自動downloadの順を基本とする。`--managed-python` / `--no-managed-python` または `python-preference` で選択を絞れる。

`--no-python-downloads` は自動downloadを止め、`python-downloads = "manual"` は明示installだけ許す。取得可能Python一覧はuv releaseに固定され、新しいPythonにはuv更新が必要な場合がある。`.python-versions` は複数版のinstall要求に使える。

`uv python upgrade 3.12` はmanaged CPythonのpatch更新で、minor更新やPyPy/GraalPy/Pyodideの同じ処理ではない。旧patchは参照中venvのため残り、minor版linkで作ったvenvは自動追従するがexact patchを要求したvenvは追従しない。別toolがlinkをcanonicalizeした場合も追従しない。

free-threadedは `3.13t` / `3.13+freethreaded`、debugは `3.13d` / `3.13+debug`。3.13のfree-threadedは明示指定が必要、3.14以降は探索順により選ばれ得る。GIL必須は `+gil`。debug版は一般用途より遅い。pre-release/debugは通常stableを優先するが、既存で条件に合うものしかない場合は選ばれ得る。

CPython/PyPy/GraalPy/Pyodideに対応する。aarch64上のx86_64 emulationでは `UV_PYTHON_ARCH=x86_64` または完全なrequestを指定できるが、Pythonとwheelのarchitectureを一致させる。CPython managed配布はpython-build-standalone由来のため、OS標準配布と同じ特性とは限らない。Windowsではmanaged PythonをPEP 514 registryへ登録し、py launcherから選択できる。
