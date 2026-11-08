# uv の設定・解決・認証・pip interface・内部仕様

必要な節だけ読む。preview・対応表・版番号は実行時の uv と公式情報で確認する。

<a id="p45"></a>
## 設定ファイルの探索・優先順位


設定の効かない問題では、CLI > 環境変数 > project > user > system の順で確認する。同じディレクトリの `uv.toml` が `pyproject.toml` の `[tool.uv]` に優先する。`uv.toml` では `tool.uv` 接頭辞を付けない。配列は上位設定の要素が先になる連結であり、単純な置換ではない。

- workspace は root の設定を使い member の設定を無視する。`uv tool` はローカル設定を使わず user/system 設定を読む。
- 原因切り分けは `uv --no-config ...`。`--config-file path/to/uv.toml` は探索結果を置き換える。
- `uv run --env-file .env --env-file .env.local -- python app.py` では後のファイルが先を上書きするが、既存の環境変数には勝たない。無効化は `--no-env-file`。
- `[tool.uv.pip]` は pip interface 専用。ここで index を設定しても `uv lock` や `uv sync` に適用されない。

<a id="p46"></a>
## index と供給元の固定


追加 index は `[[tool.uv.index]]` の `name` と `url` で定義する。PyPI を置換するには `default = true`。default は常に最低優先度になる。

```toml
[tool.uv.sources]
my-package = { index = "internal" }

[[tool.uv.index]]
name = "internal"
url = "https://packages.example.com/simple"
explicit = true
```

`explicit = true` は指名したパッケージだけをその index から取得する。sources が参照する名前付き index は project の pyproject 内に定義する。既定の `first-index` はパッケージが最初に存在した index の候補だけを使う。解決失敗を理由に `unsafe-best-match` へ安易に変更すると dependency confusion の保護が弱くなる。

認証は `UV_INDEX_INTERNAL_USERNAME` / `UV_INDEX_INTERNAL_PASSWORD` を使い秘密を TOML に書かない。未認証リクエストが公開 index に転送されるサービスには `authenticate = "always"` を検討する。401/403 は通常検索停止、404 は次の index を探索する。flat wheel directory は `format = "flat"`。

<a id="p47"></a>
## 解決戦略・プラットフォーム


project の uv.lock は universal resolution で全対象 Python/OS を扱い、同じ名前の複数バージョンを marker 別に持ち得る。手元の Python で動いても `requires-python` の下限で依存が成立しなければ lock に失敗する。対応範囲を本当に狭める場合だけ `requires-python` や `[tool.uv].environments` を変更する。environments の marker は相互に重ならないようにする。

- pip compile は既定で現在の環境向け。別環境は `uv pip compile requirements.in --python-platform linux --python-version 3.12 -o requirements.txt`、共通 lock は `--universal`。
- 既存 lock は候補選択の優先になる。更新は `uv lock --upgrade-package NAME`、全体更新は `--upgrade`。解決と更新を混同しない。
- 下限検証には `--resolution lowest-direct`、全依存の下限なら `lowest`。通常は最新互換候補の `highest`。
- 制約は依存条件に追加、override は依存条件を置換する。override で解けても互換性の証明にはならず実行テストが必要。
- prerelease の既定は stable を優先し必要時に fallback。すべて候補にするなら `--prerelease allow`、除外は `disallow`。

追加の解決条件を設定する場合:

- `environments` は探索対象を狭める。一方 `required-environments` は、sdist がない package に指定 platform の wheel を要求するための設定。両者を逆にしない。
- `minimum-libc-version` は調査時 preview。必要な glibc/musl の下限と対応する required-environments を設定し、新しい libc 専用 wheel だけで下限対応と判定されないようにする。
- `--fork-strategy fewest` は複数 platform/Python 間の version 数を減らすため古い共通 version を選び得る。既定の `requires-python` は各 Python で新しい候補を優先する。
- 両立しない extras/groups は `[tool.uv].conflicts` に選択肢として宣言できる。lock に共存できても同時 sync はできない。workspace では `package` 名も指定する。

<a id="p48"></a>
## uv_build backend


`uv_build` は pure Python 用。C/Rust extension があるなら対応 backend を維持する。uv を frontend として使うために backend を変更する必要はない。

```toml
[build-system]
requires = ["uv_build>=0.13.7,<0.14"]
build-backend = "uv_build"
```

この範囲は調査時の例。導入する uv_build の minor に合わせ上限も設定する。既定は `src/<normalized_name>/__init__.py`。特殊配置は `[tool.uv.build-backend]` の `module-name` と `module-root` を明示する。namespace package は共有 root に `__init__.py` を置かない。`namespace = true` は安全検査を減らすので必要な場合に限る。

`uv build` 後に sdist と wheel の内容を検査する。除外は include より優先し、sdist の除外は wheel にも適用される。小さな data は module 内に置く。include glob は root から anchored、exclude は既定で unanchored という差に注意する。

<a id="p49"></a>
## 認証方式の選択


private package index の HTTP 認証は [HTTP credentials](#p51)、private Git は [Git credentials](#p52)、企業 CA は [TLS](#p53) を読む。`uv auth` の保存情報は Git の credential helper と別系統である。サービス別の設定は integrations reference へ進む。

<a id="p50"></a>
## uv auth CLI


`uv auth login example.com` で HTTPS Basic 用の認証情報を保存する。秘密は shell 履歴に埋めず、管理済み secret 入力から `--password -` / `--token -` の stdin に渡す。login 成功は認証の正しさを検証したことにならないため、対象の取得操作で確認する。

`uv auth logout example.com` はローカル情報のみ削除し、サーバ上の token を失効しない。`uv auth token` は秘密を表示するため通常ログに出さない。`uv auth helper` は外部ツールの Bazel credential-helper protocol 向けで、対話操作の代替ではない。

<a id="p51"></a>
## HTTP credentials


探索順は URL、netrc、uv store、keyring。`NETRC` または `~/.netrc` は常に対象で、keyring は既定で無効。使うなら `--keyring-provider subprocess` と実行可能な `keyring` を準備する。

uv store は調査時点では state directory の平文ファイル。OS の secure store は `native-auth` preview であり、他アプリが保存した資格情報まで自動探索しない。`uv add` は index の秘密を pyproject/lock に残さないため、CI 側にも認証を供給する必要がある。一方、直接 artifact URL の資格情報は永続化され得るため URL へ秘密を埋め込まない。

<a id="p52"></a>
## Git credentials


private Git は `git+ssh://git@host/org/repo` と既存 SSH key、または HTTPS と Git credential helper を使う。uv auth のログインでは Git 認証を用意できない。

`gh auth login --with-token` を利用する環境では、helper を構成する `gh auth setup-git` も必要となる。通常の `uv add` は Git URL の秘密を pyproject/uv.lock に保存しないので、他のマシンにも helper/key を準備する。`--raw` で資格情報を保存する回避策は選ばず、認証側を修正する。

<a id="p53"></a>
## TLS・企業 CA


既定の bundled Mozilla roots で企業 proxy の CA を検証できない場合は `--system-certs` / `UV_SYSTEM_CERTS=true` を使う。独自 CA は PEM の `SSL_CERT_FILE` または `SSL_CERT_DIR`。これらが非空なら既定の certificate source を置き換えるため、不正・空ファイルで trust roots を失わないよう確認する。DER は非対応。

mTLS は certificate、private key の順に含む PEM を `SSL_CLIENT_CERT` に渡す。`allow-insecure-host` は TLS 検証を無効化するため通常の修正として使わず、まず trust store を直す。

<a id="p54"></a>
## 外部サービス認証


Azure / Google / AWS / JFrog の index は integrations reference の該当サービスに従う。Hugging Face の private script 取得では既存 `HF_TOKEN` が huggingface.co 宛てに自動供給される。停止は `UV_NO_HF_TOKEN=1`。remote script を実行する際は依存解決の前に取得元と内容を確認する。

<a id="p55"></a>
## cache の診断・CI


cache は直接 rm/編集せず uv の command で管理する。まず `uv sync --refresh-package NAME` で対象の freshness を再検証し、インストール済み内容の問題なら `--reinstall-package NAME`、対象だけ消す必要があれば `uv cache clean NAME`。全消去を最初の対策にしない。

- Git は解決済み commit、URL は URL と HTTP headers、local archive は mtime、local directory は pyproject/setup の mtime 等に基づく。flat index で同名 wheel を差し替えた場合は refresh が必要。
- 動的 version や dependencies を読むファイルは `cache-keys` に含める。設定は既定を置換するので `{ file = "pyproject.toml" }` を残す。Git tag 依存なら `{ git = { commit = true, tags = true } }` も含める。
- CI は `uv cache prune --ci` で、再取得しやすい prebuilt wheel と metadata を除き costly build を保持する。共有 cache は並行アクセスに対応するが、外部から改変しない。
- `uv cache dir` で実パスを確認。環境と同一 filesystem が link に有利。`--no-cache` は永続 cache を使わず一時 cache を使う。

<a id="p56"></a>
## preview の扱い


preview はリリース間で変わり得る。必要な feature だけ `--preview-features NAME` / `UV_PREVIEW_FEATURES=NAME` または `preview-features = ["NAME"]` で有効にする。`--preview` は全 feature を有効にするため既定策にしない。未知の feature 名は error ではなく warning になるので、綴りを含め実際の動作を検証する。

調査時には native-auth、workspace metadata、pylock 等の実験的機能があるが、固定一覧を信じず導入バージョンの `uv help` と公式ページで状態を確認する。設定を読む前に働く feature は TOML で有効にできない場合がある。

<a id="p57"></a>
## pip interface を選ぶ条件


requirements.in/txt や既存環境の管理を維持する場合に `uv pip` を使う。project metadata/uv.lock を更新するなら `uv add` / `uv sync` にする。`uv pip install` は project 宣言や uv.lock を更新しない。環境選択 → 宣言 → compile → sync → check の順で再現性を確保する。

<a id="p58"></a>
## venv と対象 Python


`uv venv --python 3.12` で `.venv` を作成する。既定名なら activation なしで `uv pip` が探索する。POSIX shell は `source .venv/bin/activate`、PowerShell は `.venv\Scripts\activate`。

別環境を確実に選ぶには `uv pip install --python /absolute/venv/bin/python PACKAGE`。既存 `VIRTUAL_ENV` や親 directory の `.venv` により想定外の環境を選ばないよう、`uv pip list --python ...` で確認する。`--system` は system Python を変更する明示的 opt-in で、通常開発では使わない。`python -m uv` は親 interpreter の環境を既定に使う点も通常の uv executable と異なる。

<a id="p59"></a>
## pip パッケージ操作


環境を指定して `uv pip install PACKAGE`、editable は `uv pip install -e .`、宣言済み入力は `uv pip install -r requirements.txt`。pyproject の extras は `uv pip install -r pyproject.toml --extra cli`、group は `uv pip install --group test`。

group の探索元は cwd の pyproject であり、`-r elsewhere/pyproject.toml` に自動追従しない。必要なら `--group elsewhere/pyproject.toml:test` とする。削除は `uv pip uninstall NAME`。install は不要な既存 package を取り除かないので厳密な環境再現には sync を使う。

<a id="p60"></a>
## 環境の検査


`uv pip list --format json` は機械処理、`uv pip freeze` は現在の installed snapshot、`uv pip show NAME` は metadata 確認。freeze の出力を元の依存意図と混同しない。複数回の install で不整合が入り得るため `uv pip check` で missing/conflicting dependencies を確認し、実際の import/test も実行する。

<a id="p61"></a>
## 依存の宣言形式


標準 metadata は `[project].dependencies`、利用者が選ぶ extras は `[project.optional-dependencies]` に宣言する。軽量な既存運用は requirements.in の一行一要件を維持し、requirements.txt を解決結果として分離する。requirements.in は extras の定義構造を持たない。ad-hoc install の履歴だけを正とせず、宣言から再作成できるようにする。

<a id="p62"></a>
## compile / sync・制約・hash


`uv pip compile requirements.in -o requirements.txt` で lock を保存する。`-o` がなければ表示のみ。既存 output の pin は維持するため更新には `--upgrade-package NAME` / `--upgrade` を指定する。`uv pip sync requirements.txt` は不要 package を除いて合わせる。入力は推移依存まで含む compile 結果にする。

制約は `--constraint constraints.txt`、ビルド専用は `--build-constraint build-constraints.txt`。制約に名前を書いてもそれ自体をインストールするわけではない。`--override overrides.txt` は上流要件を置換するので、解決成功後に互換性テストが必要。

runtime の hash 検証は compile の `--generate-hashes` と install/sync の `--require-hashes`。build dependency 用は別に `--require-build-hashes` と hash 付き build constraints を使う。group の入力元は `--group path/pyproject.toml:GROUP` で明示できる。

<a id="p63"></a>
## pip 互換性の落とし穴


uv は pip の完全な複製ではない。移行時は次を確認する。

- `pip.conf` / `PIP_INDEX_URL` は読まない。`UV_*`、uv.toml、`[tool.uv.pip]` に移す。
- 仮想環境が既定で、複数 index は first-index。pip と同じ最良候補の合算検索を想定しない。
- PEP 517 build isolation が既定。古い package の未宣言 build dependency はまず package 更新や metadata 修正を検討する。`--no-build-isolation` を使うなら build requirements の準備を呼び出し側が引き受ける。
- registry package からの transitive URL dependency は拒否され得る。信頼できる URL を入力の direct dependency として明示する。
- prerelease は stable を優先し必要時 fallback。解決結果の差はバグと決めつけず、index、Python、marker、旧 pin を揃えて比較する。

<a id="p68"></a>
## storage の移動


パスを推測せず `uv cache dir`、`uv python dir`、`uv python dir --bin`、`uv tool dir`、`uv tool dir --bin` を使う。cache は disposable、Python/tool の実体は persistent data、実行用 symlink は bin と役割が違う。

`UV_PYTHON_INSTALL_DIR` を変更しても既存 venv の interpreter 参照は書き換わらない。移動時には venv の再作成と動作確認が必要。tool は `UV_TOOL_DIR` と `UV_TOOL_BIN_DIR`、Python の bin は `UV_PYTHON_BIN_DIR`。uv 自身の `UV_INSTALL_DIR` はこれら全体を移動する設定ではない。

<a id="p69"></a>
## installer 制御


standalone installer の設置先は `UV_INSTALL_DIR`。shell profile を変更しない場合は `UV_NO_MODIFY_PATH=1` を installer に渡す。CI の一時設置には `UV_UNMANAGED_INSTALL=/path` を使うと PATH/profile の変更と self update が無効になる。

```sh
curl -LsSf https://astral.sh/uv/install.sh | env UV_UNMANAGED_INSTALL=/tmp/uv-bin sh
```

これは取得した installer を実行する例なので、実行環境の方針に合わせ version pin / 取得物検査を行う。実行後は絶対パスか明示した PATH で `uv --version` を確認する。インストール先変更は cache/data directory の変更ではない。

<a id="p70"></a>
## troubleshooting の入口


backend error なら [build failures](#p71)、uv 固有に見える再現性のある問題は [最小再現](#p72) に進む。まず失敗した command、uv/Python version、platform、設定、完全な error を記録し、認証・解決・build・install のどの段階か分ける。

<a id="p71"></a>
## build failure の切り分け


`The build backend returned an error` の stderr は backend 側の出力。最新 Python と古い package の組合せでは対応 wheel がなく sdist build へ落ちることがある。対象 Python/OS/architecture の wheel の有無、compiler/header/system library、package の Python 対応を確認する。

uv 固有か比較する場合は使い捨て venv を `uv venv --seed` で作り、同じ Python/package version に対して `pip install --use-pep517 --no-cache --force-reinstall ...` を試す。pip でも失敗すれば upstream/build environment を調べる。無条件に isolation を外すのではなく、未宣言 build requirements には extra build dependencies 等の設定を検討する。universal lock の metadata 取得で別 platform の package を build する場合もあり、lock 中の build と install 中の build を区別する。

<a id="p72"></a>
## 再現例を作る


失敗を最小の script、pyproject と lock、または Dockerfile に削減する。uv/Python/OS/shell version、外部 index や compiler 等の必要条件、`-v` の完全ログを添える。secret と private URL は公開前に除去する。

repository 再現は branch 名だけでなく commit を固定し、clone → checkout → 実行の手順を示す。既存環境の偶然の package/cache に依存しないよう使い捨て directory で再確認する。報告自体の公開は別の外部操作である。

<a id="p73"></a>
## uv 自体への貢献


uv のソースを変更する場合は CONTRIBUTING と現行 AI policy を先に確認する。help wanted が適切な候補で、needs-design/needs-decision や未合意の新機能を独断で実装・PR 化しない。

Rust と C compiler が必要。対象テストは `cargo nextest run -E 'test(NAME)'`、ローカル CLI は `cargo run -- ...`。snapshot 変更は `cargo insta review` で意図を確認する。`cargo fmt --all`、clippy、repo の生成物検証を変更に応じて行う。test subprocess のログには通常の RUST_LOG でなく `UV_INTERNAL__TEST_RUST_LOG` を使う。公開 policy と必要 toolchain は更新されるため作業時に再読する。

<a id="p74"></a>
## 内部仕様の入口


通常の利用設定は [resolution](#p47) を優先する。solver 自体の調査は [resolver internals](#p75)、外部ツールが依存グラフを読む場合は [workspace metadata](#p76) を使い、uv.lock の内部構造を独自に固定しない。

<a id="p75"></a>
## resolver internals を診断に使う


PubGrub は部分解、要件の伝播、矛盾の学習と backtracking で互換集合を探す。metadata の取得がコストになるため、遅い解決では曖昧な広い範囲や index 応答も調べる。既存 lock の優先があるので毎回 latest を選び直すわけではない。

universal resolution は marker に従って fork し、互換な結果をまとめる。`uv lock -v` の `Splitting resolution` / `Solving split` を見て、どの Python/platform 範囲が原因か追う。複数バージョンを lock しているだけで破損と判断しない。優先順位や fork の内部実装は public CLI contract として依存しない。

<a id="p76"></a>
## workspace metadata の利用


ツール連携は `uv workspace metadata --output-version preview` の JSON を使う。script は `--script path/to/script.py`。schema は preview なので `schema.version` を検査する。`--sync` は収集前に install し、既定で unrelated packages を保持する。削除を伴う厳密同期は `--exact`。

graph は `workspace.id` / `members` / `script.id` を入口に dependency edge を辿る。node ID は opaque と扱い、cycle 対策の visited set、対象環境の marker 評価、conflicts の選択を実装する。resolution 全体から同名 package を拾って単一環境とみなすと、互いに排他的な version を混ぜてしまう。extra node は package に依存するが group node はその package 自体を含むとは限らない。実インストール状況は `environment.packages`、module ownership は `modules` を使う。

<a id="p77"></a>
## 性能の主張を検証する


公式 benchmark は upstream repository の最新手順を参照する。自分の workload を測る場合は uv version、Python、OS、network、warm/cold cache、対象 lock を固定して区別する。cache が暖かい install と初回 resolve を混ぜて速度倍率を一般化しない。

<a id="p78"></a>
## policy の確認範囲


導入・更新は versioning、platform/Python support を確認する。source build は Rust policy、再配布は license を読む。security と AI contribution policy はこの親ページからの外部参照も作業時に確認し、通常利用の手順と contribution の規則を混同しない。

<a id="p79"></a>
## versioning と更新


uv は minor で breaking changes、patch で nonbreaking fixes/enhancements を提供する独自 scheme。単純に 0.x だから不安定と判断しない。CI や環境イメージで version を固定し、更新時は changelog と lock/schema への影響を確認する。

uv.lock schema は public API で minor で変わり得る。一方 cache schema は patch でも変化し得るので cache 内部を直接読む実装をしない。多くの内部 Rust crate は安定 API ではなく、binary の互換性から Rust interface の互換性を推定しない。

<a id="p80"></a>
## platform support


対象 OS/architecture と libc を確認して official binary/wheel を選ぶ。Tier 1 は継続テスト、Tier 2 は build 保証中心、Tier 3 は best effort で保証の水準が異なる。Linux では architecture だけでなく manylinux tag が示す glibc 下限も確認する。official musl binary は static link。

調査時点の macOS 対応は 13+、Windows は 10/Server 2016+。Linux aarch64 や Windows arm64 等の tier と最低 libc は更新され得るため、このメモを永続的な対応表として使わず導入時に公式表を再確認する。

<a id="p81"></a>
## Python support


uv 自体が扱える Python と project がサポートする Python を分ける。調査時の Tier 1 は Python 3.10–3.15 と CPython。古い 3.6–3.9 は動作対象でも EOL で推奨されない。PyPy/GraalPy/Pyodide は CPython と同じ保証ではない。

実際の組合せを `uv python list` と実行テストで確認する。managed build が存在することと依存 package の wheel が存在することも別なので、代替 implementation の利用は必要な依存まで検証する。

<a id="p82"></a>
## Rust support


prebuilt uv の通常利用に Rust は不要。source から compile するときだけ upstream Cargo.toml の `[workspace.package].rust-version` を調べる。MSRV は patch でも変わり得るため、昔の値を skill に固定しない。N-2 Rust releases より新しくしない方針でも、正確な toolchain は対象 commit から取得する。

<a id="p83"></a>
## license


uv は Apache-2.0 または MIT の選択による dual license。再配布や組込みでは採用する license の notice 等を対象版の LICENSE-APACHE / LICENSE-MIT から確認する。upstream に意図して送る contribution は別指定がなければ同様の dual license となる。依存 package の license は uv 自体と別に確認する。
