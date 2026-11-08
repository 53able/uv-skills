# 公式ドキュメントの対応表

取得日: 2026-11-08。ego-browserで公式ページを取得し、サイトマップと照合。

## 計測定義

分母は公式 `https://docs.astral.sh/uv/sitemap.xml` に列挙された重複なしの84ページ。索引・policy・internalsも除外しない。分子は監査表で元URLと専用アンカーが対応し、選択基準・操作・注意点または索引としての案内を記述したページ。**84/84ページ = 100%**（要求85%以上）。

これはページ単位のガイダンス対応率であり、全見出し・全オプション・全文の85%以上を再現したという意味ではない。特にCLI、Settings、Environmentは選択ガイドと公式詳細の検索手順を提供し、巨大な仕様一覧は複製していない。意味の正確性を自動計測した数値でもない。

再計測: `python3 scripts/check_coverage.py`。同梱sitemapは取得時点の固定スナップショット。更新時は公式sitemapを再取得し、追加・削除・変更ページを読み直してmanifestと参照を更新する。content SHA-256は抽出本文の指紋であり署名ではない。ネットワーク再取得・鮮度確認はこの検証スクリプトでは実施しない。

| ID | 公式ページ | ローカルガイダンス |
|---|---|---|
| 0 | [Introduction](https://docs.astral.sh/uv/) | [参照](../../skills/uv/references/projects.md#p0) |
| 1 | [getting-started/](https://docs.astral.sh/uv/getting-started/) | [参照](../../skills/uv/references/projects.md#p1) |
| 2 | [getting-started/installation/](https://docs.astral.sh/uv/getting-started/installation/) | [参照](../../skills/uv/references/projects.md#p2) |
| 3 | [getting-started/first-steps/](https://docs.astral.sh/uv/getting-started/first-steps/) | [参照](../../skills/uv/references/projects.md#p3) |
| 4 | [getting-started/features/](https://docs.astral.sh/uv/getting-started/features/) | [参照](../../skills/uv/references/projects.md#p4) |
| 5 | [getting-started/help/](https://docs.astral.sh/uv/getting-started/help/) | [参照](../../skills/uv/references/projects.md#p5) |
| 6 | [guides/](https://docs.astral.sh/uv/guides/) | [参照](../../skills/uv/references/projects.md#p6) |
| 7 | [guides/install-python/](https://docs.astral.sh/uv/guides/install-python/) | [参照](../../skills/uv/references/projects.md#p7) |
| 8 | [guides/scripts/](https://docs.astral.sh/uv/guides/scripts/) | [参照](../../skills/uv/references/projects.md#p8) |
| 9 | [guides/tools/](https://docs.astral.sh/uv/guides/tools/) | [参照](../../skills/uv/references/projects.md#p9) |
| 10 | [guides/projects/](https://docs.astral.sh/uv/guides/projects/) | [参照](../../skills/uv/references/projects.md#p10) |
| 11 | [guides/package/](https://docs.astral.sh/uv/guides/package/) | [参照](../../skills/uv/references/projects.md#p11) |
| 12 | [guides/migration/](https://docs.astral.sh/uv/guides/migration/) | [参照](../../skills/uv/references/projects.md#p12) |
| 13 | [guides/migration/pip-to-project/](https://docs.astral.sh/uv/guides/migration/pip-to-project/) | [参照](../../skills/uv/references/projects.md#p13) |
| 14 | [guides/integration/](https://docs.astral.sh/uv/guides/integration/) | [参照](../../skills/uv/references/integrations.md#p14) |
| 15 | [guides/integration/docker/](https://docs.astral.sh/uv/guides/integration/docker/) | [参照](../../skills/uv/references/integrations.md#p15) |
| 16 | [guides/integration/jupyter/](https://docs.astral.sh/uv/guides/integration/jupyter/) | [参照](../../skills/uv/references/integrations.md#p16) |
| 17 | [guides/integration/marimo/](https://docs.astral.sh/uv/guides/integration/marimo/) | [参照](../../skills/uv/references/integrations.md#p17) |
| 18 | [guides/integration/github/](https://docs.astral.sh/uv/guides/integration/github/) | [参照](../../skills/uv/references/integrations.md#p18) |
| 19 | [guides/integration/gitlab/](https://docs.astral.sh/uv/guides/integration/gitlab/) | [参照](../../skills/uv/references/integrations.md#p19) |
| 20 | [guides/integration/pre-commit/](https://docs.astral.sh/uv/guides/integration/pre-commit/) | [参照](../../skills/uv/references/integrations.md#p20) |
| 21 | [guides/integration/pytorch/](https://docs.astral.sh/uv/guides/integration/pytorch/) | [参照](../../skills/uv/references/integrations.md#p21) |
| 22 | [guides/integration/fastapi/](https://docs.astral.sh/uv/guides/integration/fastapi/) | [参照](../../skills/uv/references/integrations.md#p22) |
| 23 | [guides/integration/bazel/](https://docs.astral.sh/uv/guides/integration/bazel/) | [参照](../../skills/uv/references/integrations.md#p23) |
| 24 | [guides/integration/azure/](https://docs.astral.sh/uv/guides/integration/azure/) | [参照](../../skills/uv/references/integrations.md#p24) |
| 25 | [guides/integration/google/](https://docs.astral.sh/uv/guides/integration/google/) | [参照](../../skills/uv/references/integrations.md#p25) |
| 26 | [guides/integration/aws/](https://docs.astral.sh/uv/guides/integration/aws/) | [参照](../../skills/uv/references/integrations.md#p26) |
| 27 | [guides/integration/jfrog/](https://docs.astral.sh/uv/guides/integration/jfrog/) | [参照](../../skills/uv/references/integrations.md#p27) |
| 28 | [guides/integration/renovate/](https://docs.astral.sh/uv/guides/integration/renovate/) | [参照](../../skills/uv/references/integrations.md#p28) |
| 29 | [guides/integration/dependabot/](https://docs.astral.sh/uv/guides/integration/dependabot/) | [参照](../../skills/uv/references/integrations.md#p29) |
| 30 | [guides/integration/aws-lambda/](https://docs.astral.sh/uv/guides/integration/aws-lambda/) | [参照](../../skills/uv/references/integrations.md#p30) |
| 31 | [guides/integration/coiled/](https://docs.astral.sh/uv/guides/integration/coiled/) | [参照](../../skills/uv/references/integrations.md#p31) |
| 32 | [concepts/](https://docs.astral.sh/uv/concepts/) | [参照](../../skills/uv/references/projects.md#p32) |
| 33 | [concepts/projects/](https://docs.astral.sh/uv/concepts/projects/) | [参照](../../skills/uv/references/projects.md#p33) |
| 34 | [concepts/projects/layout/](https://docs.astral.sh/uv/concepts/projects/layout/) | [参照](../../skills/uv/references/projects.md#p34) |
| 35 | [concepts/projects/init/](https://docs.astral.sh/uv/concepts/projects/init/) | [参照](../../skills/uv/references/projects.md#p35) |
| 36 | [concepts/projects/dependencies/](https://docs.astral.sh/uv/concepts/projects/dependencies/) | [参照](../../skills/uv/references/projects.md#p36) |
| 37 | [concepts/projects/run/](https://docs.astral.sh/uv/concepts/projects/run/) | [参照](../../skills/uv/references/projects.md#p37) |
| 38 | [concepts/projects/sync/](https://docs.astral.sh/uv/concepts/projects/sync/) | [参照](../../skills/uv/references/projects.md#p38) |
| 39 | [concepts/projects/config/](https://docs.astral.sh/uv/concepts/projects/config/) | [参照](../../skills/uv/references/projects.md#p39) |
| 40 | [concepts/projects/build/](https://docs.astral.sh/uv/concepts/projects/build/) | [参照](../../skills/uv/references/projects.md#p40) |
| 41 | [concepts/projects/export/](https://docs.astral.sh/uv/concepts/projects/export/) | [参照](../../skills/uv/references/projects.md#p41) |
| 42 | [concepts/projects/workspaces/](https://docs.astral.sh/uv/concepts/projects/workspaces/) | [参照](../../skills/uv/references/projects.md#p42) |
| 43 | [concepts/tools/](https://docs.astral.sh/uv/concepts/tools/) | [参照](../../skills/uv/references/projects.md#p43) |
| 44 | [concepts/python-versions/](https://docs.astral.sh/uv/concepts/python-versions/) | [参照](../../skills/uv/references/projects.md#p44) |
| 45 | [concepts/configuration-files/](https://docs.astral.sh/uv/concepts/configuration-files/) | [参照](../../skills/uv/references/advanced.md#p45) |
| 46 | [concepts/indexes/](https://docs.astral.sh/uv/concepts/indexes/) | [参照](../../skills/uv/references/advanced.md#p46) |
| 47 | [concepts/resolution/](https://docs.astral.sh/uv/concepts/resolution/) | [参照](../../skills/uv/references/advanced.md#p47) |
| 48 | [concepts/build-backend/](https://docs.astral.sh/uv/concepts/build-backend/) | [参照](../../skills/uv/references/advanced.md#p48) |
| 49 | [concepts/authentication/](https://docs.astral.sh/uv/concepts/authentication/) | [参照](../../skills/uv/references/advanced.md#p49) |
| 50 | [concepts/authentication/cli/](https://docs.astral.sh/uv/concepts/authentication/cli/) | [参照](../../skills/uv/references/advanced.md#p50) |
| 51 | [concepts/authentication/http/](https://docs.astral.sh/uv/concepts/authentication/http/) | [参照](../../skills/uv/references/advanced.md#p51) |
| 52 | [concepts/authentication/git/](https://docs.astral.sh/uv/concepts/authentication/git/) | [参照](../../skills/uv/references/advanced.md#p52) |
| 53 | [concepts/authentication/certificates/](https://docs.astral.sh/uv/concepts/authentication/certificates/) | [参照](../../skills/uv/references/advanced.md#p53) |
| 54 | [concepts/authentication/third-party/](https://docs.astral.sh/uv/concepts/authentication/third-party/) | [参照](../../skills/uv/references/advanced.md#p54) |
| 55 | [concepts/cache/](https://docs.astral.sh/uv/concepts/cache/) | [参照](../../skills/uv/references/advanced.md#p55) |
| 56 | [concepts/preview/](https://docs.astral.sh/uv/concepts/preview/) | [参照](../../skills/uv/references/advanced.md#p56) |
| 57 | [pip/](https://docs.astral.sh/uv/pip/) | [参照](../../skills/uv/references/advanced.md#p57) |
| 58 | [pip/environments/](https://docs.astral.sh/uv/pip/environments/) | [参照](../../skills/uv/references/advanced.md#p58) |
| 59 | [pip/packages/](https://docs.astral.sh/uv/pip/packages/) | [参照](../../skills/uv/references/advanced.md#p59) |
| 60 | [pip/inspection/](https://docs.astral.sh/uv/pip/inspection/) | [参照](../../skills/uv/references/advanced.md#p60) |
| 61 | [pip/dependencies/](https://docs.astral.sh/uv/pip/dependencies/) | [参照](../../skills/uv/references/advanced.md#p61) |
| 62 | [pip/compile/](https://docs.astral.sh/uv/pip/compile/) | [参照](../../skills/uv/references/advanced.md#p62) |
| 63 | [pip/compatibility/](https://docs.astral.sh/uv/pip/compatibility/) | [参照](../../skills/uv/references/advanced.md#p63) |
| 64 | [reference/](https://docs.astral.sh/uv/reference/) | [参照](../../skills/uv/references/command-reference.md#p64) |
| 65 | [reference/cli/](https://docs.astral.sh/uv/reference/cli/) | [参照](../../skills/uv/references/command-reference.md#p65) |
| 66 | [reference/settings/](https://docs.astral.sh/uv/reference/settings/) | [参照](../../skills/uv/references/command-reference.md#p66) |
| 67 | [reference/environment/](https://docs.astral.sh/uv/reference/environment/) | [参照](../../skills/uv/references/command-reference.md#p67) |
| 68 | [reference/storage/](https://docs.astral.sh/uv/reference/storage/) | [参照](../../skills/uv/references/advanced.md#p68) |
| 69 | [reference/installer/](https://docs.astral.sh/uv/reference/installer/) | [参照](../../skills/uv/references/advanced.md#p69) |
| 70 | [reference/troubleshooting/](https://docs.astral.sh/uv/reference/troubleshooting/) | [参照](../../skills/uv/references/advanced.md#p70) |
| 71 | [reference/troubleshooting/build-failures/](https://docs.astral.sh/uv/reference/troubleshooting/build-failures/) | [参照](../../skills/uv/references/advanced.md#p71) |
| 72 | [reference/troubleshooting/reproducible-examples/](https://docs.astral.sh/uv/reference/troubleshooting/reproducible-examples/) | [参照](../../skills/uv/references/advanced.md#p72) |
| 73 | [reference/contributing/](https://docs.astral.sh/uv/reference/contributing/) | [参照](../../skills/uv/references/advanced.md#p73) |
| 74 | [reference/internals/](https://docs.astral.sh/uv/reference/internals/) | [参照](../../skills/uv/references/advanced.md#p74) |
| 75 | [reference/internals/resolver/](https://docs.astral.sh/uv/reference/internals/resolver/) | [参照](../../skills/uv/references/advanced.md#p75) |
| 76 | [reference/internals/metadata/](https://docs.astral.sh/uv/reference/internals/metadata/) | [参照](../../skills/uv/references/advanced.md#p76) |
| 77 | [reference/benchmarks/](https://docs.astral.sh/uv/reference/benchmarks/) | [参照](../../skills/uv/references/advanced.md#p77) |
| 78 | [reference/policies/](https://docs.astral.sh/uv/reference/policies/) | [参照](../../skills/uv/references/advanced.md#p78) |
| 79 | [reference/policies/versioning/](https://docs.astral.sh/uv/reference/policies/versioning/) | [参照](../../skills/uv/references/advanced.md#p79) |
| 80 | [reference/policies/platforms/](https://docs.astral.sh/uv/reference/policies/platforms/) | [参照](../../skills/uv/references/advanced.md#p80) |
| 81 | [reference/policies/python/](https://docs.astral.sh/uv/reference/policies/python/) | [参照](../../skills/uv/references/advanced.md#p81) |
| 82 | [reference/policies/rust/](https://docs.astral.sh/uv/reference/policies/rust/) | [参照](../../skills/uv/references/advanced.md#p82) |
| 83 | [reference/policies/license/](https://docs.astral.sh/uv/reference/policies/license/) | [参照](../../skills/uv/references/advanced.md#p83) |
