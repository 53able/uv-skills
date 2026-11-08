# uv 外部連携

実環境のPython、uv、OS、アクセラレータに合わせる。バージョン例は固定推奨の例であり、常に最新版を意味しない。クラウドへの投入・公開はユーザーの依頼範囲で行う。

<a id="p14"></a>
## 連携の選択

実行基盤ならDocker/CI、対話分析ならJupyter/marimo、GPUならPyTorch、配布元なら各private registry、更新自動化ならRenovate/Dependabotの節を読む。連携先固有の認証とuvの依存管理を分けて設定する。

<a id="p15"></a>
## Docker

- Pythonを含む派生イメージか、既存Pythonイメージへdistrolessから`/uv /uvx`をコピーする。再現性が必要ならuvの版またはdigestを固定する。
- `.dockerignore`で`.venv`を除外する。ホストの仮想環境は持ち込まない。開発時も`.venv`を別volumeにする。
- BuildKit cache mountと`UV_LINK_MODE=copy`でfilesystem境界を越えるhardlink警告を避ける。cacheなしでは`--no-cache`で容量を減らせる。

```dockerfile
FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:0.13.7 /uv /uvx /bin/
ENV UV_LINK_MODE=copy UV_COMPILE_BYTECODE=1
WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    uv sync --frozen --no-install-project --no-dev
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv uv sync --locked --no-dev
ENV PATH="/app/.venv/bin:$PATH"
```

最初の層はlockのみなので`--frozen`、ソースとmetadataが揃った後は`--locked`で整合性を検査する。workspaceなら初回を`--no-install-workspace`にする。multi-stageで`.venv`だけコピーする場合は`--no-editable`、同じPythonと互換OS・同じ環境パスを使う。Python downloadを止めて両stageのsystem Pythonを使う方式もある。Compose watchはソース同期から`.venv`を除き、metadata変更でrebuildする。`uv tool dir --bin`でツールのPATHを確認。必要時は`gh attestation verify --owner astral-sh oci://ghcr.io/astral-sh/uv:<version>`で公式イメージの来歴を検証する。

<a id="p16"></a>
## Jupyter

プロジェクトのimportだけなら`uv run --with jupyter jupyter lab`。notebookから環境を変更するならkernelを明示する。

```sh
uv add --dev ipykernel
uv run ipython kernel install --user --env VIRTUAL_ENV "$PWD/.venv" --name=project
uv run --with jupyter jupyter lab
```

`project` kernelを選ぶ。`!uv add pydantic`はmetadata/lockにも記録、`!uv pip install pydantic`は環境だけ変更する。kernelなしの`!uv pip install`は一時的なJupyter環境を対象にし得る。`%pip`が必要なら事前に`uv venv --seed`でpipを用意するが、pipでの変更はlockに記録されない。VS Codeでは`ipykernel`を入れた`.venv`のPythonをkernelに指定する。単発利用は`uv tool run jupyter lab`、非projectは`uv venv --seed`と`uv pip install jupyterlab`の後に`.venv/bin/jupyter lab`（WindowsはScripts）を実行する。

<a id="p17"></a>
## marimo

単発は`uvx marimo edit`。自己完結notebookは`uv add --script notebook.py numpy`でPEP 723 metadataを追加し、`uvx marimo edit --sandbox notebook.py`で編集する。sandbox UIから追加した依存はscript metadataへ記録される。`uv run notebook.py`なら通常のPython scriptとして動く。

projectではmarimoを依存にして`uv run marimo edit notebook.py`、UIの追加も`uv add`に反映する。`uv run --with marimo marimo edit notebook.py`も可能だがUIの追加はprojectに永続化されない。非projectは`uv venv`、`uv pip install marimo numpy`から実行し、UIの追加は環境への`uv pip install`になる。

<a id="p18"></a>
## GitHub Actions

`astral-sh/setup-uv`で導入しuv版を固定する。action自体も検証済みcommitへpinする。Pythonは`uv python install`（project pinに従う）または`setup-python`を使う。`.python-version`を読む指定と、`pyproject.toml`の互換範囲から選ぶ指定を区別する。matrixはsetup-uvの`python-version`または`UV_PYTHON`でproject pinを上書きできる。

```yaml
# checkout / setup-uv 後のsteps
- run: uv sync --locked --all-extras --dev
- run: uv run --locked --all-extras pytest tests
```

`--all-extras`は全extraが両立するprojectで使う。setup-uvの`enable-cache: true`を優先し、手動cacheならOSと`uv.lock`をkeyにし、終了時に`uv cache prune --ci`。pip方式ならrequirementsをkeyにする。self-hosted runnerではcacheの無制限増加に注意する。private Git依存はread権限tokenをsecretからGit credential helperへ渡す。PyPI Trusted Publishingはbuild jobと`id-token: write`のpublish jobを分け、artifactを引き継ぎ`uv publish`する。wheel/sdistのsmoke testも行う。

<a id="p19"></a>
## GitLab CI/CD

Python同梱のuvイメージ（例`ghcr.io/astral-sh/uv:0.13.7-python3.12-trixie-slim`）を使い、別mountのbuild directoryには`UV_LINK_MODE: copy`を設定する。distroless uvイメージだけではPython/OSツールが揃わない点を確認する。

```yaml
variables:
  UV_LINK_MODE: copy
  UV_CACHE_DIR: .uv-cache
check:
  image: ghcr.io/astral-sh/uv:0.13.7-python3.12-trixie-slim
  cache:
    key:
      files: [uv.lock]
    paths: [.uv-cache]
  script:
    - uv sync --locked
    - uv run --locked pytest
  after_script:
    - uv cache prune --ci
```

pip方式はvenvを作るか、隔離したCI環境で`UV_SYSTEM_PYTHON: 1`を明示する。keyもrequirements/pyprojectへ合わせる。

<a id="p20"></a>
## pre-commit

`astral-sh/uv-pre-commit`のrevをuv版へ固定する。metadata変更後のlock更新は`uv-lock`、lockからrequirements同期は`uv-export`、requirements.inから解決は`pip-compile`を選ぶ。

```yaml
repos:
  - repo: https://github.com/astral-sh/uv-pre-commit
    rev: 0.13.7
    hooks:
      - id: uv-lock
      - id: uv-export
```

`pip-compile`なら`args: [requirements.in, -o, requirements.txt]`。複数inputはhook entryを分け、各`files`正規表現も変更する。exportとcompileは異なる依存管理方式なので目的に合わせて選ぶ。

<a id="p21"></a>
## PyTorchとGPU

OS・Python・driver・CPU/CUDA/ROCm/XPUの目標を確認する。PyPIのtorchはOSごとにbackendが異なる。固定backendは専用indexを`explicit = true`にし、torch/torchvisionを`tool.uv.sources`で紐付ける。

```toml
[[tool.uv.index]]
name = "pytorch-cpu"
url = "https://download.pytorch.org/whl/cpu"
explicit = true

[tool.uv.sources]
torch = { index = "pytorch-cpu" }
torchvision = { index = "pytorch-cpu" }
```

CUDA indexはmacOSへ適用しないよう`marker = "sys_platform == 'linux' or sys_platform == 'win32'"`を使い、ROCmはLinuxに限定する。XPU/ROCmは対応Triton依存も同indexへ設定する。既存のtorchをCPU/CUDA extraへ移す場合は、元のversion制約を保って`project.dependencies`から両方の`project.optional-dependencies`へ移し、二重宣言を残さない。CPU/CUDAをextraで切り替えるならextraごとのsourcesに加えて`tool.uv.conflicts`で排他を宣言し、`uv sync --extra cpu`等で選ぶ。GPU extraは非対応OSで失敗する。選択したextraは`uv sync --locked --extra cpu`と`uv run --locked --extra cpu ...`の両方へ渡す。Dockerでも両sync層で同じ選択を行う。排他的extrasには`--all-extras`を使わない。

pip方式は`uv pip install torch --torch-backend=auto`でdriver等から選択、または`--torch-backend=cu130`のように固定できる。このflagはproject interfaceには使えない。GPU拡張は`uv add flash-attn --index astral-cu128=https://wheels.astral.sh/simple/cu128/`などの公式Astral GPU indexも利用できるが、wheelのCUDA/PyTorch/Python/platformの組合せを合わせる。

<a id="p22"></a>
## FastAPI

`uv init`から`uv add 'fastapi[standard]'`、`uv run fastapi dev`で開発する。`uv run`は依存解決・lock・venv準備も行う。app構造に応じてentrypointを指定する。

配布ではDocker内でlockから同期し、`/app/.venv/bin/fastapi run app/main.py --port 80 --host 0.0.0.0`を起動する。開発用`dev`と本番用`run`を区別し、コンテナportと公開portを対応させる。Docker節のcache分割、uv pin、`.venv`除外も適用する。

<a id="p23"></a>
## Bazel

Bazel 7以降のcredential helperへuv保存認証を渡せる。`uv auth login https://packages.example.com`後、`.bazelrc`に`common --credential_helper=packages.example.com=%workspace%/bazel/uv-auth-helper`を追加する。indexと実ファイルのhostが違えば両方を書く。

```sh
#!/usr/bin/env bash
exec uv --preview-features auth-helper auth helper --protocol=bazel "$@"
```

wrapperを実行可能にする。この機能はpreviewなので現行uvの対応を確認する。一般的なbuild統合はrules_py/rules_pythonのuv対応ガイドへ進む。

<a id="p24"></a>
## Azure Artifacts

index `private-registry`を`https://pkgs.dev.azure.com/<ORG>/<PROJECT>/_packaging/<FEED>/pypi/simple/`へ設定する。PAT方式は`UV_INDEX_PRIVATE_REGISTRY_USERNAME=dummy`とpasswordへtokenを渡す。keyring方式は公開PyPIから`uv tool install keyring --with artifacts-keyring`、`UV_KEYRING_PROVIDER=subprocess`、usernameは`VssSessionToken`にする。

公開先`publish-url`は同feedの`/pypi/upload/`。`UV_PUBLISH_USERNAME=dummy`、`UV_PUBLISH_PASSWORD`を設定して`uv publish --index private-registry`。keyring認証とは設定を区別する。index名のハイフンは環境変数ではアンダースコアになる。秘密をpyprojectへ埋めない。

<a id="p25"></a>
## Google Artifact Registry

indexは`https://<REGION>-python.pkg.dev/<PROJECT>/<REPOSITORY>/simple/`。認証済みgcloudから`gcloud auth application-default print-access-token`を取得し、`UV_INDEX_PRIVATE_REGISTRY_USERNAME=oauth2accesstoken`、passwordへtokenを渡す。usernameを別名にしない。

更新をkeyringに任せるなら`uv tool install keyring --with keyrings.google-artifactregistry-auth`と`UV_KEYRING_PROVIDER=subprocess`を使う。pluginはprivate index以外から先に導入する。publish-urlは`https://<REGION>-python.pkg.dev/<PROJECT>/<REPOSITORY>/`（simpleなし）。publish用usernameも`oauth2accesstoken`、passwordをtokenにして`uv publish --index private-registry`。

<a id="p26"></a>
## AWS CodeArtifact

indexは`https://<DOMAIN>-<ACCOUNT_ID>.d.codeartifact.<REGION>.amazonaws.com/pypi/<REPOSITORY>/simple/`。認証済みawscliで`aws codeartifact get-authorization-token --domain <DOMAIN> --domain-owner <ACCOUNT_ID> --query authorizationToken --output text`を取得する。必要に応じregionを指定する。

usernameは`aws`固定、tokenを`UV_INDEX_PRIVATE_REGISTRY_PASSWORD`に渡す。短期token更新を委ねるなら`uv tool install keyring --with keyrings.codeartifact`と`UV_KEYRING_PROVIDER=subprocess`を使う。publish-urlは同URLから`simple/`を除いたもの。`UV_PUBLISH_USERNAME=aws`とpasswordへtokenを設定し`uv publish --index private-registry`。期限切れを依存解決エラーと取り違えない。

<a id="p27"></a>
## JFrog Artifactory

indexを`https://<organization>.jfrog.io/artifactory/api/pypi/<repository>/simple`へ設定する。通常は`UV_INDEX_PRIVATE_REGISTRY_USERNAME/PASSWORD`、JWTならusernameを空文字、passwordをtokenにする。publish-urlは`/simple`なし。

公開認証は`UV_PUBLISH_USERNAME=""`と`UV_PUBLISH_PASSWORD="$JFROG_TOKEN"`を使い`uv publish --index private-registry`。JFrogで`--token`や`UV_PUBLISH_TOKEN`を使うとuvがusernameに`__token__`を設定し401になる。publish環境変数にはindex名を含めない。

<a id="p28"></a>
## Renovate

`uv.lock`をcommitするとuv projectとして検出され、project/optional/dev依存のpyprojectとlockが更新される。推移依存も定期更新するなら`lockFileMaintenance: { enabled: true }`を設定する。

PEP 723 scriptは`pep723.managerFilePatterns`に`docs/build.py`や`scripts/**/*.py`など対象を明示する。取得時点ではscript lock更新は未対応なのでscript lockは別途更新・検証する。uvの`exclude-newer`を使うならRenovateの`minimumReleaseAge`（例`1 week`）も揃え、botが提示した版をuvが拒否しないようにする。

<a id="p29"></a>
## Dependabot

`.github/dependabot.yml`でuv ecosystemを選ぶ。

```yaml
version: 2
updates:
  - package-ecosystem: uv
    directory: /
    schedule:
      interval: weekly
    cooldown:
      default-days: 7
```

cooldownはuvで1週間の`exclude-newer`を使う場合の例。制限に合わせる。uv.lock更新をサポートするが、全use case対応とは限らないため対象構成で生成PRのlockとCIを確認する。

<a id="p30"></a>
## AWS Lambda

image、zip、dependency layerから選ぶ。FastAPIならMangumでASGIをLambda handler（例`app.main.handler`）へ変換する。Python版とx86_64/ARMをruntimeに一致させる。

```sh
uv export --frozen --no-dev --no-editable -o requirements.txt
uv pip install --no-installer-metadata --no-compile-bytecode \
  --python-platform x86_64-manylinux2014 --python 3.13 \
  --target packages -r requirements.txt
```

zipはpackagesの中身をrootに入れ、appを追加する。ARMでは`aarch64-manylinux2014`を選ぶ。Lambdaの展開サイズ制限を確認する。layerなら`--prefix packages`を使い`packages/lib`を`python/lib`としてzipする。appとlayerを独立更新できるがruntime/architectureを合わせる。

imageではAWS Lambda Python baseと同じbaseのbuilderを使い、`${LAMBDA_TASK_ROOT}`へtarget installしてruntime stageへコピーする。cache層では`uv export --frozen --no-emit-workspace --no-dev --no-editable`で外部依存のみ、その後workspace local依存も含めてinstallする。`--no-emit-workspace`のままlocal libraryを落とさない。公開・更新時はhandler設定、IAM role、regionとimage/zipの方式を確認し、eventをinvokeしてresponseを検証する。

<a id="p31"></a>
## Coiled

scriptのPEP 723 metadataへPythonと依存を記録し、まず`uv run process.py`でローカル確認する。`uvx coiled login`後、scriptに`# COILED container ghcr.io/astral-sh/uv:debian-slim`と必要なregionを記録し、`uvx coiled batch run uv run process.py`で投入する。

regionはデータとcloud providerに合わせ、意図しないegressを避ける。batchのstatus/logsで完了を確認する。GPU/メモリ/disk/spotの指定はCoiledの設定で行う。cloud実行は課金や外部データアクセスを伴うので依頼範囲を確認して投入する。
