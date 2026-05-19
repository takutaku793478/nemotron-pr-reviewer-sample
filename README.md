# Nemotron PR Reviewer Sample

GitHub の Pull Request に対して **NVIDIA Nemotron**（OpenRouter 経由）で自動コードレビューを実行し、結果をPRコメントとして投稿するサンプルプロジェクトです。

> MASC × FriSti 検証用サンプル。コードは外部サーバには送信されず、GitHub Actions のランナー上でのみ処理されます（OpenRouter API 呼び出しを除く）。

## アーキテクチャ

```
PR 作成・更新
   └─ GitHub Actions 起動 (.github/workflows/pr-review.yml)
        ├─ gh pr diff で差分取得
        ├─ scripts/review.py が OpenRouter API に Nemotron で問い合わせ
        └─ gh pr comment でレビュー結果を PR に投稿
```

| 要素 | 採用 |
| --- | --- |
| AI モデル | NVIDIA Nemotron (OpenRouter 経由) |
| ランタイム | GitHub Actions (ubuntu-latest, Python 3.12) |
| サンプル対象 | FastAPI 製の Todo API (`sample-app/`) |

## ディレクトリ構成

```
.
├── .github/workflows/pr-review.yml   # PR トリガーの GitHub Actions
├── sample-app/                       # レビュー対象のサンプル FastAPI アプリ
│   ├── main.py
│   └── requirements.txt
├── scripts/
│   ├── review.py                     # 差分を Nemotron に投げてレビュー結果を生成
│   └── requirements.txt
├── LICENSE
└── README.md
```

## セットアップ

### 1. リポジトリ Secret/Variable を登録

リポジトリの **Settings → Secrets and variables → Actions** で以下を登録します。

| 種別 | 名前 | 内容 |
| --- | --- | --- |
| Secret | `OPENROUTER_API_KEY` | OpenRouter の API キー (必須) |
| Variable | `NEMOTRON_MODEL` | 使用するモデル ID (任意。未指定なら `nvidia/llama-3.1-nemotron-70b-instruct`) |

> 利用可能な Nemotron 系モデル一覧は [OpenRouter Models](https://openrouter.ai/models?q=nemotron) を参照してください。

### 2. 動作確認

1. 任意のブランチを切る (`git checkout -b feat/test`)
2. `sample-app/main.py` 等を編集
3. GitHub に push → PR を作成
4. Actions タブで `Auto PR Review (Nemotron)` の完了を待つ
5. PR のコメント欄に Nemotron からのレビューが投稿されることを確認

## サンプルアプリをローカルで動かす

```bash
cd sample-app
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
# http://127.0.0.1:8000/docs を開いて API ドキュメントを確認
```

## レビュー内容のカスタマイズ

レビュー観点や出力フォーマットは `scripts/review.py` 内の以下を編集してください。

- `SYSTEM_PROMPT` … レビュアーのロール設定
- `USER_PROMPT_TEMPLATE` … チェック観点と出力フォーマット
- `DEFAULT_MODEL` … OpenRouter で呼ぶモデル ID
- `MAX_DIFF_CHARS` … LLM に渡す差分の最大文字数（超過分は切り詰め）

## 注意事項

- 差分が大きすぎる場合 (`MAX_DIFF_CHARS` 超過) は冒頭部分のみがレビュー対象となります。
- OpenRouter の料金体系・利用規約は [OpenRouter Pricing](https://openrouter.ai/docs#pricing) を確認してください。
- レビュー結果は AI 生成物であり、必ず人間がチェックしたうえで採用可否を判断してください。

## ライセンス

MIT License — [LICENSE](./LICENSE) を参照。
