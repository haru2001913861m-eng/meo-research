# -*- coding: utf-8 -*-
"""店の問い合わせフォームから営業の1通を送る（会長 2026-11-01「問い合わせフォームでも送れるなら送って」）.

いつもの Chrome（Claude in Chrome・maps_chrome と同じ claude -p --chrome・同じ鍵 chrome.lock）でフォームを開き、入力して送る。
送らない: 店自身のフォームでない（予約サイト・制作会社など）／「営業お断り」「セールスお断り」「営業目的のご連絡はご遠慮」の表示／
          ロボット確認（reCAPTCHA など）／必須の欄が埋められない（住所・生年月日など）／ファイルの添付が必須
返り値: {"result": "sent"|"refusal"|"captcha"|"no_form"|"not_shop"|"failed", "note": ...}。読めない時は {}
呼び出し: sales-automation scripts/need_to_stock.py（メールが確かめられない店）
"""
from __future__ import annotations

import re

import maps_chrome

TOOLS = ",".join("mcp__claude-in-chrome__" + t for t in (
    "tabs_context_mcp", "tabs_create_mcp", "navigate", "get_page_text", "read_page", "find", "form_input", "computer", "tabs_close_mcp"))

PROMPT = """ブラウザで次の URL を新しいタブで開く。お店（{shop}）の問い合わせのページのはず。
{url}
このページ（または、そこから1回のリンクでたどれる「お問い合わせ」のページ）の問い合わせフォームから、下の内容を1回だけ送る。

送らずに終える場合（当てはまったら、その行だけ出力してタブを閉じる）:
- フォームが無い → RESULT no_form
- {shop} 自身のフォームではない（予約サイト・ポータル・ホームページ制作会社・本部やグループ会社の共通フォームなど）→ RESULT not_shop
- 「営業お断り」「セールスお断り」「営業目的のご連絡はご遠慮ください」など、営業の連絡を断る表示がある → RESULT refusal
- 「私はロボットではありません」などのロボット確認・画像認証がある → RESULT captcha
- 必須の欄に、下に無い情報（住所・生年月日・予約日・人数・会員番号など）が要る／ファイルの添付が必須 → RESULT failed 必須の欄が埋められない

入力する内容（欄がある物だけ。無い欄は飛ばす。必須でない欄は空のまま）:
- 会社名・店名: ひとつなぎcompany
- お名前: 皆川遥一（ふりがな: みながわはるい／カナ: ミナガワハルイ）
- メールアドレス（確認の欄も同じ）: {email}
- 電話番号: 必須の時だけ {phone}
- 種別・お問い合わせの種類: 「その他」か一番近い物（「求人への応募」「予約」は選ばない）
- 件名: {subject}
- 本文（お問い合わせ内容）: 次の「本文ここから」から「本文ここまで」の間を、改行もそのまま入れる
本文ここから
{body}
本文ここまで
- 「個人情報の取り扱いに同意」などの同意のチェックは入れる。メールマガジンの登録のチェックは入れない

入力したら送信のボタンを押す。確認の画面が出たら、中身を確かめて送信を押す。送った後の画面（「送信しました」「ありがとうございました」など）を確かめる。
開いたタブを閉じる。
出力は次の行だけ。前置き・説明は書かない。
RESULT sent（送った後の画面を確かめた時）／RESULT failed <理由>（押しても送れなかった時）
NOTE <送った後の画面の言葉、または理由を1行>
ほかのページへの書き込み・ログイン・買い物・予約など、このフォームを送る以外の操作はしない。"""


def parse(raw: str) -> dict:
    m = re.search(r"^RESULT\s+(sent|refusal|captcha|no_form|not_shop|failed)\b(.*)$", raw or "", re.M)
    if not m:
        return {}
    n = re.search(r"^NOTE\s*(.+)$", raw or "", re.M)
    return {"result": m.group(1), "note": ((n.group(1) if n else "") or m.group(2)).strip()[:200]}


def send(url: str, shop: str, subject: str, body: str, email: str, phone: str, tag: str) -> dict:
    """1回だけ動かす（maps_chrome.run_claude は読めないと別のモデルでやり直す＝フォームでは二重に送るおそれ）"""
    import os
    import subprocess
    from datetime import datetime
    prompt = PROMPT.format(url=url, shop=shop, subject=subject, body=body, email=email, phone=phone)
    lk = maps_chrome._chrome_lock()
    if lk is None:
        return {}
    try:
        try:
            raw = subprocess.run(["claude", "-p", prompt, "--chrome", "--model", maps_chrome.MODELS[0], "--max-turns", "40",
                                  "--allowedTools", TOOLS], capture_output=True, text=True, timeout=480, cwd=maps_chrome.HERE,
                                 env={k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}).stdout
        except (subprocess.TimeoutExpired, FileNotFoundError):
            raw = ""
        os.makedirs(maps_chrome.RAW, exist_ok=True)
        open(os.path.join(maps_chrome.RAW, f"{datetime.now():%F_%H%M}_{tag}_form.txt"), "w", encoding="utf-8").write(raw)
        r = parse(raw)
        return r or ({"result": "unknown", "note": "結果の行が無い（送れたか分からない）"} if raw else {})
    finally:
        lk.close()
