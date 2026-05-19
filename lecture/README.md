# 講義スライド ── 【ゼロから学ぶ】Claude Code × Cursor 完全入門

AI駆動開発の初心者向け 約90分の収録型講義動画のスライド成果物。

## 中身

| ファイル | 役割 |
|---|---|
| `build_slides.py` | スライドを生成する Python スクリプト。文言・スピーカーノートはこの中の `SLIDES` リストで編集 |
| `claude-cursor-lecture.pptx` | 生成済みの PowerPoint（全 55 枚 / スピーカーノート付き） |
| `plan.md` | 講義の構成プラン（章立て・ねらい・つまづき対策・調査の一次ソース） |

## Google Slides で開く

1. Google ドライブに `claude-cursor-lecture.pptx` をアップロード
2. 右クリック → 「アプリで開く」→「Google スライド」
3. 「ファイル」→「Google スライドとして保存」で永続化
4. お好みで本文フォント（Meiryo）を `Noto Sans JP` 等に置換

## スライドを再生成する

`build_slides.py` の `SLIDES` リストを編集して以下を実行（Python 3.10+ 想定）。

```bash
cd lecture
python3 -m venv .venv
./.venv/bin/pip install python-pptx
./.venv/bin/python build_slides.py
```

`claude-cursor-lecture.pptx` が上書きされる。
`.venv/` はリポジトリには含めない（`.gitignore` で除外済み）。

## 収録前のチェック

- 価格は変動するため、収録当日に [claude.com/pricing](https://claude.com/pricing) /
  [cursor.com/pricing](https://cursor.com/pricing) で再確認し、S18・S19 を更新
- Mac で「インストール → 拡張 → 生成 → 公開」を一度通しでリハーサル
- スライドを通し読みして 90 分内に収まるかタイムキーピング
