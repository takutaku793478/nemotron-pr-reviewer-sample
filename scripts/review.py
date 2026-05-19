"""Call NVIDIA Nemotron via OpenRouter to review a unified diff."""
from __future__ import annotations

import os
import sys

import requests

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "nvidia/llama-3.1-nemotron-70b-instruct"
MAX_DIFF_CHARS = 60_000

SYSTEM_PROMPT = (
    "あなたは経験豊富なシニアソフトウェアエンジニアです。"
    "与えられたコード差分(unified diff)を読み、"
    "プロジェクト品質と保守性の観点で実用的なレビューを行います。"
    "出力は日本語のMarkdownで、簡潔かつ具体的に記述してください。"
)

USER_PROMPT_TEMPLATE = """以下のPull Requestの差分をレビューしてください。

## チェック観点
- バグ・ロジックエラー
- セキュリティリスク (SQLインジェクション / 認証情報のハードコード / 入力検証不足 など)
- 命名規則・コーディング規約の違反
- 関数の複雑度・可読性・テスタビリティ

## 出力フォーマット
1行目に総評(1-2文)を書き、続けて以下のセクションを順に出力してください。
存在しないセクションは省略してOKです。

### 重要な指摘 (High)
- `path/to/file.py:42` 指摘内容 / 修正案

### 改善提案 (Medium)
- `path/to/file.py:88` 指摘内容 / 修正案

### 軽微・スタイル (Low)
- `path/to/file.py:120` 指摘内容 / 修正案

### 良かった点
- 簡潔に1-3個

## 差分

```diff
{diff}
```
"""


def review(diff: str, *, model: str, api_key: str) -> str:
    if len(diff) > MAX_DIFF_CHARS:
        diff = diff[:MAX_DIFF_CHARS] + "\n\n... (truncated)\n"

    response = requests.post(
        OPENROUTER_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/takutaku793478/nemotron-pr-reviewer-sample",
            "X-Title": "Nemotron PR Reviewer Sample",
        },
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": USER_PROMPT_TEMPLATE.format(diff=diff)},
            ],
            "temperature": 0.2,
        },
        timeout=120,
    )
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"].strip()


def main() -> int:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("OPENROUTER_API_KEY is not set", file=sys.stderr)
        return 1

    model = os.environ.get("NEMOTRON_MODEL", DEFAULT_MODEL)
    diff = sys.stdin.read().strip()
    if not diff:
        print("(差分が空のためレビューをスキップしました)")
        return 0

    body = review(diff, model=model, api_key=api_key)

    print("## :robot_face: Automated Review (Nemotron via OpenRouter)")
    print()
    print(f"> モデル: `{model}`")
    print()
    print(body)
    return 0


if __name__ == "__main__":
    sys.exit(main())
