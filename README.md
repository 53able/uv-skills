<img src="assets/icon.svg" width="64" height="64" alt="">

# uv-skills

uv公式ドキュメントに基づく日本語エージェントスキル。

- スキル: [skills/uv/SKILL.md](skills/uv/SKILL.md)
- 公式84ページの対応表と計測定義: [coverage.md](docs/coverage/coverage.md)
- 検証: `python3 scripts/check_coverage.py` / `python3 -m unittest discover -s tests -v`

## インストール

[Vercel Skills CLI](https://github.com/vercel-labs/skills) の[スキル形式・検出規則](https://github.com/vercel-labs/skills/blob/main/docs/creating-skills.md)に対応。Node.js 22.20以上で実行する。

このリポジトリ内で内容を確認する:

```sh
npx skills add . --list
```

利用先プロジェクトのディレクトリから導入する:

```sh
npx skills add 53able/uv-skills --skill uv -a codex
```

全プロジェクトで利用する場合は `-g`、Claude Code向けは `-a claude-code` を指定する。導入先とリンク方式はCLIに任せる。ローカルから導入する場合は `53able/uv-skills` の代わりにリポジトリのパスを指定する。

Codexでは `$uv` で呼び出せる。通常の自動選択にも対応する。本体はエージェント共通の `SKILL.md` と相対パスの参照で完結し、`agents/openai.yaml` はCodex向けの補助メタデータとしてのみ使用する。

## 互換性・検証

`skills/uv/SKILL.md` に必須の `name` / `description` を定義し、公式の標準探索先 `skills/<name>/` に配置している。独自の探索設定やnpmパッケージ化は不要。Skills CLI 1.7.6で検出および一時プロジェクトへのインストールと参照ファイルの同梱を確認済み。

2026-11-08時点の公式サイトマップ84ページ中84ページにガイダンスを用意（ページ対応率100%）。全CLIオプション・全文の網羅率ではない。出典と計測資料は `docs/coverage/` に分離し、スキルには同梱しない。

検証環境: macOS arm64、uv 0.13.5。一時プロジェクトでofflineのinit/lock/sync/run、古いlockの拒否、frozenでの鮮度確認省略を検証。GPU・クラウド・Docker・公開操作は実環境では未検証。独立したシナリオレビューでCI・CPU/CUDA extras・Dockerの選択を確認した。

## License

[MIT](LICENSE) © 2026 Go Tadano
