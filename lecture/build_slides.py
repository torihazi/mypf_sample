#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
【ゼロから学ぶ】Claude Code × Cursor 完全入門 ─ スライド生成スクリプト
python-pptx で .pptx を生成。Google Slides にインポートして仕上げる想定。

実行:
  ./.venv/bin/python build_slides.py
出力:
  claude-cursor-lecture.pptx
"""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

# ─────────────── デザイントークン ───────────────
ACCENT  = RGBColor(0x4F, 0x7C, 0xFF)   # 青
ACCENT2 = RGBColor(0x8B, 0x5C, 0xF6)   # 紫
INK     = RGBColor(0x1F, 0x29, 0x33)
MUTED   = RGBColor(0x6B, 0x72, 0x80)
WHITE   = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT   = RGBColor(0xF4, 0xF5, 0xF7)
DARK    = RGBColor(0x14, 0x17, 0x1C)
SOFTBLUE= RGBColor(0xE8, 0xEE, 0xFF)
FONT    = "Meiryo"   # 日本語が表示できる代表的なフォント（Google Slides で代替されてもOK）

# ─────────────── 共通ヘルパ ───────────────
prs = Presentation()
prs.slide_width  = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]

def _style_run(run, size, bold, color):
    """run に サイズ・太字・色・フォント（latin+ea）を設定。"""
    f = run.font
    f.size = Pt(size)
    f.bold = bold
    f.color.rgb = color
    f.name = FONT
    rPr = f._rPr
    ea = rPr.find(qn('a:ea'))
    if ea is None:
        ea = rPr.makeelement(qn('a:ea'), {})
        rPr.append(ea)
    ea.set('typeface', FONT)

def add_box(slide, l, t, w, h):
    box = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.05)
    tf.margin_top = tf.margin_bottom = Inches(0.02)
    return tf

def para(tf, runs, align=PP_ALIGN.LEFT, space_after=8, space_before=0,
         first=False, line=1.15):
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.alignment = align
    p.space_after = Pt(space_after)
    p.space_before = Pt(space_before)
    try:
        p.line_spacing = line
    except Exception:
        pass
    if first:
        # clear default empty run if present
        if p.runs:
            for r in list(p.runs):
                r.text = ""
    for (text, size, bold, color) in runs:
        r = p.add_run()
        r.text = text
        _style_run(r, size, bold, color)
    return p

def add_rect(slide, l, t, w, h, fill, shape=MSO_SHAPE.RECTANGLE, line=False):
    sp = slide.shapes.add_shape(shape, Inches(l), Inches(t), Inches(w), Inches(h))
    sp.fill.solid()
    sp.fill.fore_color.rgb = fill
    if not line:
        sp.line.fill.background()
    sp.shadow.inherit = False
    return sp

def set_notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text

slide_no = 0
def footer_num(slide):
    global slide_no
    slide_no += 1
    tf = add_box(slide, 12.3, 6.95, 0.9, 0.4)
    para(tf, [(str(slide_no), 11, False, MUTED)], align=PP_ALIGN.RIGHT, first=True)

# ─────────────── スライド種別ビルダ ───────────────
MARKERS = ("⚠", "✅", "☐", "🎬", "①", "②", "③", "④", "⑤", "❶", "❷", "❸")

def title_slide(d):
    s = prs.slides.add_slide(BLANK)
    add_rect(s, -0.1, -0.1, 13.6, 7.7, DARK)
    add_rect(s, 0, 6.85, 13.333, 0.1, ACCENT)
    add_rect(s, 0, 6.95, 13.333, 0.1, ACCENT2)
    # kicker
    tf = add_box(s, 1.0, 1.9, 11.3, 0.6)
    para(tf, [("オンライン講座 ／ AI駆動開発 はじめの一歩",
               18, True, RGBColor(0x8B, 0xA8, 0xFF))],
         align=PP_ALIGN.CENTER, first=True)
    # main title (2 lines)
    tf = add_box(s, 0.8, 2.7, 11.7, 2.5)
    para(tf, [(d["title_l1"], 42, True, WHITE)], align=PP_ALIGN.CENTER,
         first=True, line=1.25, space_after=4)
    para(tf, [(d["title_l2"], 42, True, WHITE)], align=PP_ALIGN.CENTER,
         line=1.25, space_after=4)
    # subtitle
    tf = add_box(s, 1.0, 5.4, 11.3, 0.6)
    para(tf, [(d["subtitle"], 20, False, RGBColor(0xC9, 0xD1, 0xE5))],
         align=PP_ALIGN.CENTER, first=True)
    # presenter placeholder
    tf = add_box(s, 1.0, 6.15, 11.3, 0.5)
    para(tf, [("講師名／日付（差し替えてください）", 13, False, MUTED)],
         align=PP_ALIGN.CENTER, first=True)
    set_notes(s, d["notes"])
    return s

def section_slide(d):
    s = prs.slides.add_slide(BLANK)
    add_rect(s, -0.1, -0.1, 13.6, 7.7, LIGHT)
    add_rect(s, 0, 0, 0.5, 7.5, ACCENT)
    add_rect(s, 0, 7.0, 13.333, 0.06, ACCENT2)
    tf = add_box(s, 1.4, 2.4, 10.5, 0.9)
    para(tf, [(d["num"], 26, True, ACCENT)], first=True)
    tf = add_box(s, 1.4, 3.05, 11.0, 1.8)
    para(tf, [(d["title"], 44, True, INK)], first=True, line=1.2)
    tf = add_box(s, 1.4, 4.75, 11.0, 0.9)
    para(tf, [(d["subtitle"], 22, False, MUTED)], first=True)
    footer_num(s)
    set_notes(s, d["notes"])
    return s

def _line_has_marker(text):
    s = text.lstrip()
    return any(s.startswith(m) for m in MARKERS)

def content_slide(d):
    s = prs.slides.add_slide(BLANK)
    # title
    tf = add_box(s, 0.7, 0.45, 12.0, 1.0)
    para(tf, [(d["title"], 30, True, INK)], first=True)
    add_rect(s, 0.75, 1.42, 3.4, 0.07, ACCENT)
    # bullets
    tf = add_box(s, 0.9, 1.95, 11.6, 4.8)
    for i, b in enumerate(d["bullets"]):
        runs = []
        if not _line_has_marker(b):
            runs.append(("●  ", 18, True, ACCENT))
        runs.append((b, 20, False, INK))
        para(tf, runs, first=(i == 0), space_after=12, line=1.25)
    footer_num(s)
    set_notes(s, d["notes"])
    return s

def demo_slide(d):
    s = prs.slides.add_slide(BLANK)
    # title
    tf = add_box(s, 0.7, 0.45, 9.0, 1.0)
    para(tf, [(d["title"], 28, True, INK)], first=True)
    add_rect(s, 0.75, 1.42, 3.4, 0.07, ACCENT)
    # badge top-right (rounded rectangle)
    badge = add_rect(s, 9.95, 0.55, 2.85, 0.65, ACCENT,
                     shape=MSO_SHAPE.ROUNDED_RECTANGLE)
    btf = badge.text_frame
    btf.word_wrap = False
    btf.margin_left = btf.margin_right = Inches(0.05)
    para(btf, [("🎬  画面収録デモ", 14, True, WHITE)],
         align=PP_ALIGN.CENTER, first=True)
    btf.vertical_anchor = MSO_ANCHOR.MIDDLE
    # panel background
    add_rect(s, 0.85, 1.95, 11.6, 4.8, LIGHT)
    add_rect(s, 0.85, 1.95, 0.12, 4.8, ACCENT2)  # left accent stripe on panel
    # steps
    tf = add_box(s, 1.25, 2.2, 11.05, 4.3)
    para(tf, [("操作の流れ", 14, True, MUTED)], first=True, space_after=8)
    for i, step in enumerate(d["steps"]):
        runs = [(f"{i+1}.  ", 19, True, ACCENT2),
                (step, 19, False, INK)]
        para(tf, runs, space_after=12, line=1.25)
    footer_num(s)
    set_notes(s, d["notes"])
    return s

# ─────────────── スライド内容 ───────────────
SLIDES = [
    # ===== 第0章 オープニング =====
    {
        "type": "title",
        "title_l1": "【ゼロから学ぶ】",
        "title_l2": "Claude Code × Cursor 完全入門",
        "subtitle": "── AI駆動開発 はじめの一歩 ──",
        "notes": (
            "【話す要点】\n"
            "・講義の冒頭。挨拶と自己紹介。\n"
            "・この講義は、プログラミングが初めての方でも、AIの力でWebサイトをゼロから作り、"
            "インターネット公開まで一通り体験できるようになることを目指す、と宣言。\n"
            "・所要時間は約90分。チャプターごとに止めて、自分のペースで進められると伝える。\n"
            "・「コードは一行も書けなくて大丈夫」と最初に安心させる。"
        ),
    },
    {
        "type": "content",
        "title": "この講義のゴール",
        "bullets": [
            "① AIツール（Claude Code・Cursor）を自分のパソコンに導入する",
            "② AIに指示して、ポートフォリオサイトをゼロから作る",
            "③ 作ったサイトを GitHub Pages でインターネットに公開する",
            "終わるころには「AIと一緒に開発する」体験が一通りできるようになります",
        ],
        "notes": (
            "【話す要点】\n"
            "・ゴールは3つに分解。最初に明示することで、受講者が現在地を見失わないように。\n"
            "・「コードを1行も書けなくても大丈夫。今日やることはこの3つです」とはっきり言う。\n"
            "・最後の一文で「体験できる」ことが目的だと強調（完璧を求めない）。"
        ),
    },
    {
        "type": "demo",
        "title": "まずは『完成形』を見てみましょう",
        "steps": [
            "公開済みのポートフォリオサイトをブラウザで開く",
            "自己紹介・スキル・作品・連絡先 のセクションを順に見せる",
            "ダークモード切替やスマホ表示など、動きも実演",
            "「これを今日、ゼロから作って公開します」と宣言する",
        ],
        "notes": (
            "【話す要点】\n"
            "・完成イメージを最初に見せるのは初心者向け講義の鉄則。ゴールを「絵」で共有する。\n"
            "・URL もしっかり画面に映す。「90分後にはあなた自身のサイトのURLがここに表示されます」。\n"
            "【収録メモ】\n"
            "・このデモは本講義の第5章で実際に公開したサイトを使う（編集時に冒頭へ配置）。\n"
            "・所要 30〜60秒。サイトを動かしてワクワク感を伝える。"
        ),
    },
    {
        "type": "content",
        "title": "そもそも『AI駆動開発』ってなに？",
        "bullets": [
            "これまで: 人がコードを1行ずつ手で書いていた",
            "これから: 人は「やりたいこと」を伝える → AIがコードを書く・直す・動かす",
            "人は「何を作るか」を考え、AIは「どう作るか」を担当する",
            "コードが書けない人にも書ける人にも、開発のスピードと自由度が大きく広がる",
        ],
        "notes": (
            "【話す要点】\n"
            "・専門用語を避け、対比でやさしく説明。\n"
            "・料理に例える: レシピを考える＝人／実際に手を動かして作る＝AI。\n"
            "・「自分にもできそう」と思ってもらうのが目的。"
        ),
    },
    {
        "type": "content",
        "title": "今日の流れ（全6章・約90分）",
        "bullets": [
            "第1章 Claude Code と Cursor とは（10分）",
            "第2章 環境構築 ─ インストールと準備（24分）",
            "第3章 Cursor をさわってみる（8分）",
            "第4章 Claude Code でポートフォリオを作る（26分）",
            "第5章 GitHub Pages で公開する（12分）",
            "第6章 うまく使うコツ・次の一歩（4分）",
        ],
        "notes": (
            "【話す要点】\n"
            "・アジェンダ提示。各章が動画チャプターになっているので、自分のペースで止めながら見てOK、と案内。\n"
            "・「第2章の環境構築が一番つまづきやすいので、特に丁寧にやります」と予告して身構えてもらう。"
        ),
    },

    # ===== 第1章 =====
    {
        "type": "section",
        "num": "第 1 章",
        "title": "Claude Code と Cursor とは",
        "subtitle": "2つのツールの正体と関係を知ろう（10分）",
        "notes": (
            "【話す要点】\n"
            "・章導入。「まずは今日使う2つの道具が何者なのかをはっきりさせます」。\n"
            "・名前が似ていて混乱しやすいので、ここでしっかり区別する、と前置き。"
        ),
    },
    {
        "type": "content",
        "title": "そもそも『コードを書く場所』＝エディタとは",
        "bullets": [
            "Webサイトは「コード」というテキストでできている",
            "コードを書く専用アプリのことを「コードエディタ」と呼ぶ",
            "メモ帳でも書けるが、エディタは色分け・補完・エラー表示で圧倒的に便利",
            "今日使う『Cursor』は、このコードエディタの一種です",
        ],
        "notes": (
            "【話す要点】\n"
            "・超初心者向け。「エディタ」という言葉を初めて聞く人のために。\n"
            "・例え:「Wordが文章を書くアプリなら、コードエディタはコードを書くアプリ」。\n"
            "・後で実際の画面を見せるので、今はイメージだけでOKと伝える。"
        ),
    },
    {
        "type": "content",
        "title": "Cursor とは？",
        "bullets": [
            "「VS Code」という定番エディタをベースに作られた AIコードエディタ",
            "見た目・操作は VS Code とほぼ同じ。VS Codeの拡張機能や設定もそのまま使える",
            "最初から AI機能（コード補完など）が組み込まれている",
            "今日は『コードを書く・見る・整える作業場』として使います",
        ],
        "notes": (
            "【話す要点】\n"
            "・公式の位置づけは「the best way to code with AI」。\n"
            "・VS Code を知らない人には『定番のコードエディタにAIが乗ったもの』と説明。\n"
            "・⚠️ Cursor と VS Code は見た目そっくりだが別アプリ。後で起動する時に取り違えないよう注意。"
        ),
    },
    {
        "type": "content",
        "title": "Claude Code とは？",
        "bullets": [
            "Anthropic 社が作った『エージェント型コーディングツール』",
            "指示すると、ファイルを読む・書く・コマンドを実行する まで自分でやってくれる",
            "チャットAIが『答えるだけ』なのに対し、Claude Codeは『手を動かす』",
            "今日の主役。これにポートフォリオサイトを作ってもらいます",
        ],
        "notes": (
            "【話す要点】\n"
            "・エージェント型＝自律的に作業を進めるAIだと強調。\n"
            "・「ChatGPTのようなチャットAIは答えを返すだけ。Claude Codeは実際にあなたのパソコンでファイルを作ったり直したりしてくれる」。\n"
            "・今日の主役だと明言。"
        ),
    },
    {
        "type": "content",
        "title": "チャット型AI と エージェント型AI のちがい",
        "bullets": [
            "チャット型AI: 質問に答える／コードの例を「教えてくれる」→ コピペは自分",
            "エージェント型AI（Claude Code）: ファイルを直接作成・編集し、動作確認まで「やってくれる」",
            "だから『お願い → 確認 → 修正のお願い』の繰り返しで開発が進む",
            "コピペ作業や、調べてつなぎ合わせる手間がぐっと減る",
        ],
        "notes": (
            "【話す要点】\n"
            "・2タイプの違いを対比で。受講者がこれまで触れたAIとの違いを実感できるように。\n"
            "・「お願いベースで開発が進む」のが核心。"
        ),
    },
    {
        "type": "content",
        "title": "Cursor と Claude Code の関係",
        "bullets": [
            "Cursor ＝ 作業場（コードを書く・見る・確認するエディタ）",
            "Claude Code ＝ その作業場の中で働いてくれるAIエージェント",
            "今日のやり方: Cursor に Claude Code を『拡張機能』として入れて使う",
            "役割分担: 指示はあなた → 作業はClaude Code → 結果を確認するのはCursor上で",
        ],
        "notes": (
            "【話す要点】\n"
            "・最重要スライド。2つは競合ではなく協働。\n"
            "・例え: 「Cursorというオフィスに、Claude Codeという優秀なアシスタントを迎え入れるイメージ」。\n"
            "・「どっち使えばいいの？」という疑問にここで答える＝両方、役割が違う。"
        ),
    },
    {
        "type": "content",
        "title": "用語ミニ辞典（今日出てくる言葉）",
        "bullets": [
            "ターミナル: パソコンに文字で命令を出す画面",
            "拡張機能（extension）: エディタに後から足せる追加機能",
            "リポジトリ: プロジェクトのファイル一式を入れる『箱』",
            "GitHub: そのリポジトリをインターネット上に置けるサービス",
            "GitHub Pages: GitHubの機能。サイトを無料で一般公開できる",
        ],
        "notes": (
            "【話す要点】\n"
            "・後の章で出る用語を先に軽く紹介。完璧に覚える必要はない。\n"
            "・「出てきたらここに戻ればOK」と伝えて、受講者の不安を下げる。"
        ),
    },

    # ===== 第2章 =====
    {
        "type": "section",
        "num": "第 2 章",
        "title": "環境構築 ── インストールと準備",
        "subtitle": "ここが一番の山場（24分）",
        "notes": (
            "【話す要点】\n"
            "・「ここが今日いちばんの山場です。でも一つずつやれば必ずできます」と励ます。\n"
            "・つまづきやすいポイントは先回りして説明する、と予告。"
        ),
    },
    {
        "type": "content",
        "title": "必要なのは『3つのアカウント』",
        "bullets": [
            "① Cursor アカウント …… エディタ Cursor を使うため（この章で作る）",
            "② Claude（Anthropic）アカウント …… Claude Code を使うため（この章で作る）",
            "③ GitHub アカウント …… 作ったサイトを公開するため（第5章で作る）",
            "⚠️ ①と② は別物。ここを混同しやすいので、最初に意識しておく",
        ],
        "notes": (
            "【話す要点】\n"
            "・全体像。「なぜ3つも？」に答える＝それぞれ役割が違うから。\n"
            "・①②はこの章、③は公開する第5章で作る、と段取りを示す。\n"
            "・⚠️ ①Cursorのログインと②Claudeのログインが別であることを最初に予告（後でつまづかないため）。"
        ),
    },
    {
        "type": "demo",
        "title": "Cursor をインストールしよう",
        "steps": [
            "ブラウザで cursor.com を開く",
            "「Download」をクリック（OS自動判別）",
            "【Mac】.dmg を開き、Cursor アイコンを Applications フォルダへドラッグ",
            "【Windows】.exe を実行し、画面の指示に従ってインストール",
        ],
        "notes": (
            "【話す要点】\n"
            "・cursor.com からダウンロード→インストールまで実演。\n"
            "・要件: macOS 12 以降 / Windows 10 以降。\n"
            "【収録メモ】Mac で実演し、画面に Windows 補足のテキストオーバーレイを入れる。\n"
            "⚠️ Windowsで .exe を開いた時に SmartScreen 警告が出ても、提供元（Anthropic 社の場合は Cursor 社）を確認した上で進める。"
        ),
    },
    {
        "type": "demo",
        "title": "Cursor を起動してサインイン",
        "steps": [
            "Cursor.app（または Cursor）を起動する",
            "初回はサインイン画面が出る → 新規アカウントを作成（＝Cursorアカウント①）",
            "メールアドレス等で登録し、画面の案内に沿って進める",
            "プランは Hobby（無料）でOK。クレジットカード不要",
        ],
        "notes": (
            "【話す要点】\n"
            "・サインアップは初回起動フロー内で完結する。\n"
            "・⚠️ ここで作るのは『Cursorアカウント①』。次に出てくる Claude Code のサインインとは別物だと再強調。"
        ),
    },
    {
        "type": "content",
        "title": "（補足）VS Code 経験者は設定インポート",
        "bullets": [
            "これまで VS Code を使っていた人は、設定を Cursor にそのまま引き継げる",
            "Cursor Settings（Cmd/Ctrl + Shift + J）→ Account → 「VS Code Import」",
            "拡張機能・テーマ・キーバインドが転送される",
            "VS Code が初めての人は、このスライドは飛ばして大丈夫",
        ],
        "notes": (
            "【話す要点】\n"
            "・補足スライド。VS Code 経験者だけ向け。\n"
            "・初心者は「自分には関係ない」と分かるように明示。"
        ),
    },
    {
        "type": "content",
        "title": "料金の話 ① ── Cursor は無料でOK",
        "bullets": [
            "Cursor には無料プラン（Hobby）がある。クレジットカード不要で始められる",
            "無料でも『普通のコードエディタ』として問題なく使える",
            "今日 Cursor のAIは『タブ補完』を少し触る程度 → 無料枠で足りる想定",
            "もっと Cursor のAIを使いたくなったら Pro（$20/月）にアップグレードできる",
        ],
        "notes": (
            "【話す要点】\n"
            "・お金の話を最初に1つ消す: Cursor は無料で進められる。\n"
            "・⚠️ 価格は変わることがあるため、最新は cursor.com/pricing で要確認、と一言。"
        ),
    },
    {
        "type": "content",
        "title": "料金の話 ② ── Claude Code は有料プランが必要",
        "bullets": [
            "Claude Code を使うには Claude の有料プランへの加入が必要（無料プランでは使えない）",
            "入口は『Claude Pro』: 月払い $20／年契約なら実質 $17/月",
            "このプラン1つで Claude Code も Claude（チャット）も使える",
            "⚠️ 為替で円換算は変動。最新は claude.com/pricing で必ず確認",
        ],
        "notes": (
            "【話す要点】\n"
            "・正直に伝える: 今日のために最低限かかるのは Claude Pro の月$20、と明言。\n"
            "・GitHub も Cursor も無料なので、コストはここだけ。\n"
            "・Max という上位プランもあるが初心者は Pro で十分、と補足。"
        ),
    },
    {
        "type": "demo",
        "title": "Cursor に『Claude Code 拡張機能』を入れる",
        "steps": [
            "Cursor 左サイドの拡張機能アイコンをクリック（Cmd/Ctrl + Shift + X）",
            "検索ボックスに『Claude Code』と入力",
            "Anthropic 提供の『Claude Code』を選び「Install」",
            "これで Cursor の中で Claude Code が使える状態になる",
        ],
        "notes": (
            "【話す要点・重要】\n"
            "・この拡張機能には Claude Code 本体（CLI）も同梱されるため、Node.js のインストールやターミナルでのコマンド入力は不要。\n"
            "・⚠️ 拡張が見つからない／インストール後にパネルが出ない時は、ウィンドウを再読み込み（後のつまづきスライドで詳述）。"
        ),
    },
    {
        "type": "demo",
        "title": "Claude Code にサインイン（Claude Pro に加入）",
        "steps": [
            "Cursor 内の Claude Code パネルを開く",
            "「Sign in」を押すと自動でブラウザが開く",
            "Claude アカウント② を作成 → Claude Pro プランに加入",
            "Cursor に戻ると Claude Code が使える状態に",
        ],
        "notes": (
            "【話す要点・最重要つまづき】\n"
            "・ここでのサインインは『Claude アカウント②』。さっきの Cursor アカウント① とは完全に別物。\n"
            "・このタイミングで Claude Pro の課金手続きを行う。\n"
            "・一度ログインすれば認証情報は保存され、次回から再ログイン不要。"
        ),
    },
    {
        "type": "content",
        "title": "⚠️ 環境構築でよくあるつまづき",
        "bullets": [
            "⚠️ サインインが2種類:『Cursorのログイン①』と『Claude Codeのログイン②』は別物",
            "⚠️ 拡張機能が反応しない → ウィンドウ再読み込み（Cmd/Ctrl+Shift+P → 「Reload Window」）",
            "⚠️ Cursor と VS Code を取り違える → 起動するアプリのアイコン・名前を確認",
            "⚠️ Mac と Windows でインストーラ形式（.dmg / .exe）が違う",
        ],
        "notes": (
            "【話す要点】\n"
            "・つまづき対策まとめ。特に『2種類のサインイン』は何度も繰り返す。\n"
            "・「うまくいかない時は焦らず、このスライドに戻ってください」と案内。\n"
            "・コマンドパレットの開き方（Cmd/Ctrl + Shift + P）も覚えてもらうと便利。"
        ),
    },
    {
        "type": "content",
        "title": "ここまでのチェックリスト ✅",
        "bullets": [
            "☐ Cursor をインストールして起動できた",
            "☐ Cursor にサインインできた（アカウント①）",
            "☐ Claude Code 拡張機能を入れた",
            "☐ Claude Code にサインインできた（アカウント②／Claude Pro）",
            "全部チェックできたら、いよいよ実際に触っていきます",
        ],
        "notes": (
            "【話す要点】\n"
            "・受講者が自分の進捗を確認できる節目。\n"
            "・「ここまでが一番大変なところ。お疲れさまでした」とねぎらう。\n"
            "・1つでも未完了なら動画を止めて戻るよう案内。"
        ),
    },

    # ===== 第3章 =====
    {
        "type": "section",
        "num": "第 3 章",
        "title": "Cursor をさわってみる",
        "subtitle": "エディタの基本＋タブ補完を体験（8分）",
        "notes": (
            "【話す要点】\n"
            "・「環境が整ったので、まずは Cursor に少し慣れましょう。Claude Code を使う前の準備運動です」。"
        ),
    },
    {
        "type": "demo",
        "title": "フォルダを開いて、画面の見方を知る",
        "steps": [
            "「フォルダを開く」で作業用フォルダを開く",
            "左：ファイル一覧（エクスプローラー）",
            "中央：エディタ（コードを書く場所）",
            "下：ターミナル（あとで使う）",
        ],
        "notes": (
            "【話す要点】\n"
            "・画面構成を 3エリアでゆっくり指し示す。\n"
            "・「今は名前だけ覚えればOK、後で全部使います」。"
        ),
    },
    {
        "type": "demo",
        "title": "タブ補完（Tab）を体験してみる",
        "steps": [
            "簡単なファイルにコードを打ち始める",
            "AIが続きを『グレーの文字（ゴーストテキスト）』で予測表示する",
            "良ければ Tab キーで確定、いらなければ Esc",
            "これが Cursor のAIで一番手軽に使う機能",
        ],
        "notes": (
            "【話す要点】\n"
            "・山場の一つ。タイプするだけで予測が出る『魔法感』を見せる。\n"
            "・Tab で承認／Esc で却下、という操作の手軽さを強調。\n"
            "・⚠️ 補完が邪魔に感じたら画面右下から一時停止できる、と補足。\n"
            "・「今日 Cursor 自身のAIで使うのはほぼこれだけ。あとは Claude Code が主役です」と整理。"
        ),
    },
    {
        "type": "content",
        "title": "Cursor の他のAI機能（今日は紹介だけ）",
        "bullets": [
            "Ask: 選んだコードについて AI に質問できる",
            "Agent: Cursor版のAIエージェント（Claude Codeと似た役割）",
            "Cmd-K: その場でコードを書き換えるAI機能",
            "今日は『Claude Code』を主役にするので、これらは存在を知ればOK",
        ],
        "notes": (
            "【話す要点】\n"
            "・Cursorにも色々あるが今日は深入りしない。\n"
            "・⚠️ 特に Agent は Claude Code と役割が被るので、混乱を避けるため『今日は Claude Code を使う』と割り切る。"
        ),
    },
    {
        "type": "demo",
        "title": "ターミナルの開き方（後で使います）",
        "steps": [
            "メニューまたはショートカット（Ctrl + `）でターミナルを開く",
            "黒い画面に文字を打って命令する場所",
            "第5章の『公開』で少しだけ使う",
            "今は『ここにあるんだ』と知っておくだけでOK",
        ],
        "notes": (
            "【話す要点】\n"
            "・ターミナルの場所だけ見せる。\n"
            "・初心者はターミナルに苦手意識があるので「怖くない、必要なところだけ使う」と安心させる。"
        ),
    },

    # ===== 第4章 =====
    {
        "type": "section",
        "num": "第 4 章",
        "title": "Claude Code でポートフォリオを作る",
        "subtitle": "いよいよ本番。AIに指示してゼロから制作（26分）",
        "notes": (
            "【話す要点】\n"
            "・章導入。「ここからが本番。Claude Code に話しかけて、冒頭で見せた完成形を作っていきます」。"
        ),
    },
    {
        "type": "demo",
        "title": "作業フォルダを用意して Cursor で開く",
        "steps": [
            "デスクトップなどに空のフォルダを作る（例: my-portfolio）",
            "Cursor で「フォルダを開く」からそのフォルダを開く",
            "中身は空っぽ。ここに AI がファイルを作っていく",
        ],
        "notes": (
            "【話す要点】\n"
            "・まっさらな状態からのスタートを見せる。\n"
            "・⚠️ フォルダ名は半角英数がおすすめ（日本語名やスペースを避ける）。"
        ),
    },
    {
        "type": "content",
        "title": "指示（プロンプト）のコツ",
        "bullets": [
            "親切な同僚に話しかけるように、自然な日本語でOK",
            "「何を／どんな風に」を具体的に書くほど、思った通りになる",
            "悪い例:「サイト作って」 → 何のサイトか分からず的外れになりがち",
            "良い例:「自己紹介・スキル・作品・連絡先のあるポートフォリオサイトを、HTML/CSS/JSだけで作って」",
        ],
        "notes": (
            "【話す要点】\n"
            "・公式ベストプラクティスの最重要ポイント＝具体性。\n"
            "・「指示が雑だと、AIも雑なものを作る」。\n"
            "・難しく考えず、まず話しかけてみることが大事。"
        ),
    },
    {
        "type": "demo",
        "title": "Claude Code に最初の指示を出す",
        "steps": [
            "Claude Code のパネルに指示文を入力",
            "例:「HTML・CSS・JavaScriptだけで、架空の人物のポートフォリオサイトを作って。自己紹介・スキル・作品・連絡先のセクションを入れて」",
            "Enter で送信し、Claude Code の返答・動きを見る",
            "ここから先は AI が動く。私たちは見守って、確認していく",
        ],
        "notes": (
            "【話す要点】\n"
            "・実際に指示を送って Claude Code が考え始める様子を見せる。\n"
            "・「ここから先は AI が動きます」とモードチェンジを宣言。"
        ),
    },
    {
        "type": "demo",
        "title": "いきなり作らせない ──『プランモード』",
        "steps": [
            "作り始める前に「まず計画を見せて」と頼める（プランモード）",
            "Claude Code が『何をどう作るか』の計画を提示",
            "計画を読んで、OK なら承認・違えば修正を伝える",
            "『探索 → 計画 → 実装』の順で進めると失敗が減る",
        ],
        "notes": (
            "【話す要点・最重要習慣】\n"
            "・初心者に最も伝えたい習慣＝『いきなり全部作らせず、まず計画を確認する』。\n"
            "・間違った方向に突き進むのを防げる。計画段階なら軌道修正がラク。\n"
            "・公式の『Explore → Plan → Implement』の考え方。"
        ),
    },
    {
        "type": "demo",
        "title": "『権限の確認』というしくみ",
        "steps": [
            "Claude Code はファイル作成やコマンド実行の前に確認を求める",
            "『許可しますか？』に対して、内容を見てOKを出す",
            "勝手に何かされる心配がない＝安心して使える",
            "慣れてきたら自動承認に切り替えることもできる（最初はそのままがおすすめ）",
        ],
        "notes": (
            "【話す要点】\n"
            "・初心者の「AIが勝手に変なことをしないか」という不安をここで解消。\n"
            "・「確認が出るのは安全装置。怖がらず、内容を見てOKを出せばいい」。\n"
            "・デフォルトは都度確認モード。"
        ),
    },
    {
        "type": "demo",
        "title": "できたサイトをブラウザで確認する",
        "steps": [
            "生成された index.html をブラウザで開く",
            "実際のサイトの見た目・動きを確認",
            "AIに作らせたら『必ず自分の目で見る』",
        ],
        "notes": (
            "【話す要点】\n"
            "・公式ベストプラクティス『検証手段を持つ』。AIの作業結果は必ず確認する。\n"
            "・初めて『自分のサイト』が形になって見える感動ポイント。"
        ),
    },
    {
        "type": "demo",
        "title": "対話で仕上げる ① ── 機能を追加する",
        "steps": [
            "見て気になったところを、続けてお願いする",
            "例:「ダークモード切替ボタンを付けて」",
            "例:「全体の配色をもう少し落ち着いた色に」",
            "お願い → 確認 → またお願い、の繰り返しで完成に近づく",
        ],
        "notes": (
            "【話す要点】\n"
            "・追加の指示を出して育てていく様子を見せる。\n"
            "・「一回で完璧を狙わない。会話しながら少しずつ良くする」のが基本。\n"
            "・『対話で開発する』感覚を体感させる。"
        ),
    },
    {
        "type": "demo",
        "title": "対話で仕上げる ② ── うまくいかない時",
        "steps": [
            "途中で止めたい: Esc キーで停止",
            "結果が気に入らない:「さっきの変更は元に戻して」と伝える",
            "もっと前に戻したい: /rewind コマンドで過去の状態に巻き戻し",
            "同じ失敗が続く: /clear して仕切り直す（指示を見直す）",
        ],
        "notes": (
            "【話す要点】\n"
            "・⚠️ 初心者は『失敗したらどうしよう』と不安。戻す手段がいくつもあるので大丈夫、と伝える。\n"
            "・コツは『怒らず、具体的に伝え直す』。\n"
            "・/rewind は会話とコードの両方を過去の状態に戻せる Claude Code のチェックポイント機能。"
        ),
    },
    {
        "type": "demo",
        "title": "プロジェクトのルールを覚えさせる（CLAUDE.md）",
        "steps": [
            "/init コマンドで『CLAUDE.md』のひな型を自動生成",
            "CLAUDE.md ＝ Claude Code が毎回読む『プロジェクトのメモ』",
            "例:「HTML/CSS/JSだけで作る」「ライブラリは使わない」等のルールを書く",
            "毎回同じ説明をしなくて済むようになる",
        ],
        "notes": (
            "【話す要点】\n"
            "・CLAUDE.md ＝『AIに同じことを何度も言わなくて済むメモ帳』。\n"
            "・/init で自動生成できる。長く書きすぎないのがコツ（長いと守られなくなる）。\n"
            "・初心者は『こういう仕組みがある』と知れば十分、深掘りしない。"
        ),
    },
    {
        "type": "content",
        "title": "話が長くなったら /clear で仕切り直し",
        "bullets": [
            "AIは会話が長くなると、だんだん混乱しやすくなる",
            "別の作業に移るときは /clear で会話をリセット",
            "リセットしても作ったファイルは消えない（会話だけ新しくなる）",
            "『1つの会話で1つのテーマ』に絞るのが快適に使うコツ",
        ],
        "notes": (
            "【話す要点】\n"
            "・コンテキスト管理の話。『会話が長いとAIが疲れる』イメージで。\n"
            "・⚠️ /clear はファイルを消さない点を強調（不安にさせない）。\n"
            "・区切りのいいところでリセットする習慣を勧める。"
        ),
    },
    {
        "type": "demo",
        "title": "完成！ ポートフォリオサイトができた",
        "steps": [
            "完成したサイトをブラウザで通して見せる",
            "ダークモードなど追加した機能も動かす",
            "「コードを手で書かずに、ここまで作れた」と振り返る",
        ],
        "notes": (
            "【話す要点】\n"
            "・第4章の成果を見せる。達成感の演出。\n"
            "・「あとはこれを世界に公開するだけです」と第5章へつなぐ。"
        ),
    },

    # ===== 第5章 =====
    {
        "type": "section",
        "num": "第 5 章",
        "title": "GitHub Pages で公開する",
        "subtitle": "作ったサイトを世界へ（12分）",
        "notes": (
            "【話す要点】\n"
            "・「せっかく作ったサイト、自分のパソコンの中だけではもったいない。誰でも見られるようにインターネットに公開しましょう」。"
        ),
    },
    {
        "type": "demo",
        "title": "GitHub アカウントを作る（3つ目のアカウント）",
        "steps": [
            "ブラウザで github.com を開く",
            "「Sign up」からアカウントを作成（無料）",
            "ユーザー名・メール・パスワードを登録",
            "これが3つ目のアカウント③",
        ],
        "notes": (
            "【話す要点】\n"
            "・GitHub のサインアップを実演。完全無料。\n"
            "・⚠️ ユーザー名は公開URL の一部になるので、それなりの名前にすると良い。\n"
            "・これで 3アカウント（Cursor／Claude／GitHub）が揃う。"
        ),
    },
    {
        "type": "content",
        "title": "Git と GitHub って何？（ざっくり）",
        "bullets": [
            "Git: ファイルの変更を記録・管理するしくみ",
            "GitHub: その記録をインターネット上に置けるサービス",
            "ブランチ＝作業を枝分かれさせるしくみ（今日は深入りしません）",
            "今日は枝分かれせず、『main』という1本の流れだけで進めます",
        ],
        "notes": (
            "【話す要点】\n"
            "・⚠️ Gitは奥が深いが、今日は最小限。\n"
            "・「ブランチ」は言葉だけ紹介し、『今日は main 1本でいくので気にしなくてOK』と明言。\n"
            "・深追いしない、と最初に約束。"
        ),
    },
    {
        "type": "demo",
        "title": "サイトを GitHub にアップする",
        "steps": [
            "Claude Code に「このサイトを GitHub に公開して」と頼む",
            "あるいはターミナルで手順を実行（リポジトリ作成→アップロード）",
            "公開（Public）リポジトリにする",
            "main ブランチにファイルが上がればOK",
        ],
        "notes": (
            "【話す要点】\n"
            "・Claude Code に GitHub 公開を任せるのが初心者にはラク（gh コマンドや git 操作を AI が実行）。\n"
            "・⚠️ リポジトリは Public にしないと無料の GitHub Pages が使えない。\n"
            "・ターミナルを少しだけ使う場面。main ブランチのみ。"
        ),
    },
    {
        "type": "demo",
        "title": "GitHub Pages を有効にする",
        "steps": [
            "GitHubのリポジトリページで「Settings」→「Pages」",
            "Source を『Deploy from a branch』に設定",
            "ブランチ「main」、フォルダ「/(root)」を選んで Save",
            "数分待つと公開URLが表示される",
        ],
        "notes": (
            "【話す要点】\n"
            "・GitHub Pages の ON 手順を画面でしっかり指し示す。\n"
            "・main / /(root) を選ぶ。\n"
            "・保存後すぐには見られないことを予告（次スライド）。"
        ),
    },
    {
        "type": "demo",
        "title": "公開URLにアクセスしてみる！",
        "steps": [
            "表示された https://ユーザー名.github.io/リポジトリ名/ を開く",
            "自分の作ったポートフォリオがインターネットに公開された",
            "スマホからも、友達のパソコンからも見られる",
        ],
        "notes": (
            "【話す要点】\n"
            "・クライマックス。冒頭で見せた完成形が、今度は『自分が作って公開したもの』として表示される。\n"
            "・「これであなたのサイトが世界中から見られます」と達成感を最大化。"
        ),
    },
    {
        "type": "content",
        "title": "⚠️ 公開でよくあるつまづき",
        "bullets": [
            "⚠️ すぐ表示されない → 反映に数分かかることがある。少し待つ",
            "⚠️ 古い表示のまま → ブラウザのキャッシュが原因",
            "対処: ハードリロード（Mac: Cmd+Shift+R ／ Win: Ctrl+Shift+R）",
            "それでもダメ → シークレットウィンドウで開いて確認",
        ],
        "notes": (
            "【話す要点】\n"
            "・『公開したのに変わらない！』はキャッシュが原因のことが多い。\n"
            "・ハードリロードの操作を教える。\n"
            "・実体験として「これは本当によくある」と伝えると親近感。"
        ),
    },

    # ===== 第6章 =====
    {
        "type": "section",
        "num": "第 6 章",
        "title": "うまく使うコツ・次の一歩",
        "subtitle": "ベストプラクティスと、もっとできること（4分）",
        "notes": (
            "【話す要点】\n"
            "・「最後に、これから AI と開発していくためのコツと、もっとできることを紹介します」。"
        ),
    },
    {
        "type": "content",
        "title": "AIとうまく開発する 5つのコツ",
        "bullets": [
            "① 具体的に指示する（何を／どうしたいかを明確に）",
            "② いきなり作らせず、まず計画させる（プランモード）",
            "③ 確認手段を持つ（ブラウザで見る・動かしてみる）",
            "④ うまくいかなければ早めに軌道修正・/clear",
            "⑤ CLAUDE.md にルールを書いて、少しずつ育てる",
        ],
        "notes": (
            "【話す要点】\n"
            "・公式 Claude Code Best Practices に基づく要約。\n"
            "・今日の講義で実際にやったことの振り返りにもなっている。\n"
            "・「この5つを意識するだけで、AI がぐっと頼れる相棒になります」。"
        ),
    },
    {
        "type": "content",
        "title": "次の一歩（こんなこともできる）",
        "bullets": [
            "スキル: よく使う作業を AI に手順として覚えさせる",
            "サブエージェント: 別の作業を分担させる",
            "MCP: 外部サービス（デザインツール・DB・Slackなど）とつなぐしくみ",
            "Hooks: 決まったタイミングで自動処理を走らせる",
            "今日は名前だけ。まずは基本に慣れてから少しずつ",
        ],
        "notes": (
            "【話す要点】\n"
            "・発展トピックは『存在紹介のみ』。\n"
            "・⚠️ 初心者がいきなり手を出す必要はない、と明言。\n"
            "・「もっと知りたくなったら公式ドキュメントへ」と次の学びを促す。"
        ),
    },
    {
        "type": "content",
        "title": "まとめ ── 今日できるようになったこと",
        "bullets": [
            "✅ Claude Code と Cursor を導入できた",
            "✅ AIに指示して、ポートフォリオサイトをゼロから作れた",
            "✅ GitHub Pages でインターネットに公開できた",
            "これが『AI駆動開発 はじめの一歩』。あとは作りながら慣れていくだけ",
        ],
        "notes": (
            "【話す要点】\n"
            "・ゴール（第0章 S2）の3つを『できた』形で振り返る。\n"
            "・受講者の達成を確認。\n"
            "・「今日のあなたは、AIと一緒に開発する第一歩を踏み出しました」。"
        ),
    },
    {
        "type": "content",
        "title": "おわりに ── 次にやってみよう",
        "bullets": [
            "作ったポートフォリオを、自分の内容に書き換えてみよう",
            "小さな変更からでOK。AIに頼みながら少しずつ",
            "公式ドキュメント: code.claude.com／cursor.com",
            "お疲れさまでした！ また次の動画で",
        ],
        "notes": (
            "【話す要点】\n"
            "・締め。次のアクションを促す（架空の人物→自分の内容に書き換える）。\n"
            "・エールで終わる。\n"
            "・学習リンクを画面に映す。"
        ),
    },

    # ===== 付録 =====
    {
        "type": "content",
        "title": "付録 A1 ── よくあるつまづき一覧",
        "bullets": [
            "⚠️ 2種類のサインインを混同（Cursorアカウント①／Claudeアカウント②）",
            "⚠️ Claude Code 拡張が出ない → ウィンドウ再読み込み（Reload Window）",
            "⚠️ Cursor のAIが急に止まる → 無料枠の上限。時間をおく or Proへ",
            "⚠️ 公開サイトが古いまま → ハードリロード（Cmd/Ctrl+Shift+R）",
            "⚠️ Cursor を起動したつもりが VS Code → アプリのアイコンと名前を確認",
        ],
        "notes": (
            "【用途】\n"
            "・配布資料／動画概要欄のリンク先用。\n"
            "・動画本編では使わなくてもよい（受講者が後で見返せるトラブル集）。"
        ),
    },
    {
        "type": "content",
        "title": "付録 A2 ── 用語集",
        "bullets": [
            "エディタ: コードを書く専用アプリ",
            "拡張機能: エディタに後から足せる追加機能",
            "ターミナル: 文字で命令を出す画面",
            "リポジトリ: プロジェクトのファイル一式の『箱』",
            "プロンプト: AIへの指示文",
            "コミット／プッシュ: 変更を記録し、GitHubへ送ること",
        ],
        "notes": (
            "【用途】\n"
            "・配布資料用の用語早見表。\n"
            "・動画ではあえて全部覚えさせない（必要な時に戻れる場所として置く）。"
        ),
    },
    {
        "type": "content",
        "title": "付録 A3 ── 参考リンク（公式）",
        "bullets": [
            "Claude Code 公式ドキュメント: code.claude.com/docs",
            "Claude 料金ページ: claude.com/pricing",
            "Cursor 公式: cursor.com／cursor.com/docs",
            "Cursor 料金: cursor.com/pricing",
            "GitHub Pages ドキュメント: docs.github.com（Pages の項）",
        ],
        "notes": (
            "【用途】\n"
            "・一次情報源。\n"
            "・⚠️ 価格や手順は変わる。必ず公式ページで最新を確認するよう案内。"
        ),
    },
]

# ─────────────── レンダリング ───────────────
TYPE_MAP = {
    "title":   title_slide,
    "section": section_slide,
    "content": content_slide,
    "demo":    demo_slide,
}

def main():
    for d in SLIDES:
        TYPE_MAP[d["type"]](d)
    out = "claude-cursor-lecture.pptx"
    prs.save(out)
    print(f"OK: 全{len(SLIDES)}枚を {out} に出力しました")

if __name__ == "__main__":
    main()
