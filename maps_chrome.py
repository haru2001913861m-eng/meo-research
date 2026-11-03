# -*- coding: utf-8 -*-
"""送る候補の店の Googleマップを、会長のいつもの Chrome（Claude in Chrome・ログイン済み）で読む（会長 2026-10-31「作って 実行」）.

専用の Chrome（.gprofile_line）は Google のログインが通らない（10/31 2回失敗・「Signed out」）。いつもの Chrome なら
口コミを「新しい順」に並べ替えられる（10/31 一蘭 渋谷店で確認: 一番上が7時間前）。note-pv（23:40）と同じ claude -p --chrome。
読むだけ。口コミを書く・保存・共有などの操作はしない。開いたタブは閉じる。

1店ごとに claude を1回呼び、「新しい順」の上から最大10件の 相対時間（7 時間前／2 週間前／3 か月前…）と、オーナーの返信の有無を受け取る。
書く: data/leads/portal_leads.jsonl の g_last_review_days・g_recent90・g_reply_rate・g_real_at・g_real="chrome"
使い方: python3 maps_chrome.py [--n 20]   （毎晩 18:30 の com.hitotsunagi.portal-rank から）
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from urllib.parse import quote

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "data", "leads", "portal_leads.jsonl")
RAW = os.path.join(HERE, "logs", "maps_chrome_raw")
TOOLS = ",".join("mcp__claude-in-chrome__" + t for t in (
    "tabs_context_mcp", "tabs_create_mcp", "navigate", "get_page_text", "find", "computer", "tabs_close_mcp"))
MODELS = ("claude-sonnet-5-5", "claude-opus-5-5")

PROMPT = """ブラウザで次の URL を新しいタブで開く（Googleマップの1店のページ）。
{url}
1. 「クチコミ」のタブを開く。クチコミのタブが無い・口コミが0件なら、NONE とだけ出力してタブを閉じて終わる
2. 「並べ替え」を押して「新しい順」を選ぶ
3. 上から最大10件の口コミについて、投稿の時期（例「7 時間前」「2 週間前」「3 か月前」「1 年前」）と、オーナーからの返信が付いているかを読む
4. 開いたタブを閉じる
出力は次の行だけ。前置き・説明・まとめは書かない。
SORTED yes（新しい順に並べ替えられた時）または SORTED no
R <投稿の時期> <返信あり|返信なし>   （口コミ1件に1行・上から順に）
口コミを書く・保存・共有・ログインなど、読む以外の操作はしない。"""

UNIT = {"分": 0, "時間": 0, "日": 1, "週間": 7, "か月": 30, "ヶ月": 30, "カ月": 30, "年": 365}


def days_of(t: str) -> int | None:
    """「7 時間前」「2 週間前」「3 か月前」「1 年前」「1 週間前」→ 日数（だいたい）"""
    t = t.replace(" ", "")
    if re.match(r"^(1|一)?(日|週間|か月|ヶ月|カ月|年)前", t):
        t = "1" + re.sub(r"^(1|一)", "", t)
    m = re.match(r"(\d+)(分|時間|日|週間|か月|ヶ月|カ月|年)前", t)
    return int(m.group(1)) * UNIT[m.group(2)] if m else None


def parse(raw: str) -> dict:
    if re.search(r"^\s*NONE\s*$", raw, re.M):
        return {"g_last_review_days": None, "g_recent90": 0, "g_real_n": 0, "g_real_sorted": True}
    sorted_ = bool(re.search(r"^\s*SORTED\s+yes", raw, re.M))
    rows = re.findall(r"^\s*R\s+(.+?)\s+(返信あり|返信なし)\s*$", raw, re.M)
    days = [days_of(t) for t, _ in rows]
    days = [d for d in days if d is not None]
    if not rows or not days:
        return {}
    out = {"g_real_n": len(rows), "g_real_sorted": sorted_,
           "g_reply_rate": round(sum(1 for _, r in rows if r == "返信あり") / len(rows), 2)}
    if sorted_:   # 関連順の先頭は最新ではない。日付は新しい順に並んだ時だけ使う
        out.update({"g_last_review_days": min(days), "g_recent90": sum(1 for d in days if d <= 90)})
    return out


FULL_PROMPT = """ブラウザで次の URL を新しいタブで開く（Googleマップの1店のページ）。
{url}
1. 「概要」の画面で次を確かめる: 「このビジネスのオーナーですか」の表示があるか／説明文に「提供元: オーナー」とあるか／「最新情報」（オーナーの投稿）の欄があるか／写真の枚数
2. 「クチコミ」のタブを開き、「並べ替え」で「新しい順」を選ぶ（口コミが0件なら 3 は飛ばす）
3. 上から最大20件の口コミについて、投稿の時期とオーナーからの返信が付いているかを読む
4. 開いたタブを閉じる
出力は次の行だけ。前置き・説明・まとめは書かない。
OWNERQ yes|no
DESC yes|no
POSTS yes|no
PHOTOS <枚数・分からなければ ?>
SORTED yes|no
R <投稿の時期> <返信あり|返信なし>   （口コミ1件に1行・上から順に。0件なら NONE の1行）
口コミを書く・保存・共有・ログインなど、読む以外の操作はしない。"""


def _flag(raw: str, key: str):
    m = re.search(rf"^\s*{key}\s+(yes|no)\b", raw, re.M)
    return None if not m else m.group(1) == "yes"


def parse_full(raw: str) -> dict:
    """無料点検の形（line_detail の obs と同じ鍵）。数えられない物は入れない"""
    if not re.search(r"^\s*(OWNERQ|SORTED|R|NONE)\b", raw, re.M):
        return {}
    o: dict = {}
    oq, desc, posts = _flag(raw, "OWNERQ"), _flag(raw, "DESC"), _flag(raw, "POSTS")
    if oq is not None:
        o["verified"] = not oq
    if desc is not None:
        o["description_len"], o["description_src"] = (200 if desc else 0), "real"
    if posts is not None:
        o["has_posts"] = posts
    ph = re.search(r"^\s*PHOTOS\s+([\d,]+)", raw, re.M)
    if ph:
        o["photos_total"] = int(ph.group(1).replace(",", ""))
    sorted_ = _flag(raw, "SORTED")
    rows = re.findall(r"^\s*R\s+(.+?)\s+(返信あり|返信なし)\s*$", raw, re.M)
    days = [d for d in (days_of(t) for t, _ in rows) if d is not None]
    if sorted_ and days:
        o.update(latest_review_days=min(days), latest_review_src="real", reviews_30d=sum(1 for d in days if d <= 30))
    if sorted_ and len(rows) >= 3:
        rep = sum(1 for _, r in rows if r == "返信あり")
        o.update(reply_rate=round(rep / len(rows), 2), reply_sample=len(rows), reply_count=rep)
    return o


def maps_url(place_id: str, name: str) -> str:
    return f"https://www.google.com/maps/search/?api=1&query={quote(name or 'store')}&query_place_id={place_id}&hl=ja"


def run_claude(prompt: str, tag: str, parser) -> dict:
    """claude -p --chrome を1回（読めなければ別のモデルでもう1回）。全文は logs/maps_chrome_raw に残す"""
    os.makedirs(RAW, exist_ok=True)
    lk = _chrome_lock()
    if lk is None:
        print("[maps_chrome] Chrome を使う別の読み取りが終わらない（15分待った）")
        return {}
    try:
        return _run(prompt, tag, parser)
    finally:
        lk.close()


LOCK = os.path.join(HERE, "data", "chrome.lock")


def _chrome_lock(wait: int = 900, google: bool = True):
    """いつもの Chrome を同時に使えるのは1つの claude だけ（2つ目には道具が渡らない・10/31 無料点検と夜の読み取りが重なって確認）。
    1店ずつ取って放すので、夜のまとめ読みの合間に無料点検が入れる"""
    import fcntl, time
    if google and os.path.exists(os.path.expanduser("~/.config/hitotsunagi/google_hold")):   # common.GOOGLE_HOLD（2026-11-01）。Google を開かない用（note の閲覧数）は通す（2026-11-03）
        print("[chrome] hitotsunagi861 のログインが止められているので開かない", flush=True)
        return None
    os.makedirs(os.path.dirname(LOCK), exist_ok=True)
    f = open(LOCK, "w")
    end = time.time() + wait
    while True:
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return f
        except OSError:
            if time.time() > end:
                f.close()
                return None
            time.sleep(5)


def _run(prompt: str, tag: str, parser) -> dict:
    for model in MODELS:
        try:
            raw = subprocess.run(["claude", "-p", prompt, "--chrome", "--model", model, "--max-turns", "30",
                                  "--allowedTools", TOOLS], capture_output=True, text=True, timeout=360, cwd=HERE,
                                 env={k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}).stdout   # 鍵があると API のモードになり Chrome の道具が渡らない（10/31 無料点検は sales-automation の .env を読む）   # 無料点検は ~/sales-automation に居るので、ここ（meo-research）の設定で起こす（10/31 道具なしで返った）
        except (subprocess.TimeoutExpired, FileNotFoundError):
            raw = ""
        open(os.path.join(RAW, f"{datetime.now():%F_%H%M}_{tag}_{model}.txt"), "w", encoding="utf-8").write(raw)
        r = parser(raw)
        if r:
            return r
    return {}


GIFT_PROMPT = """ブラウザで次の URL を新しいタブで開く（Googleマップの1店のページ）。
{url}
1. 「クチコミ」のタブを開く。クチコミのタブが無い・口コミが0件なら、NONE とだけ出力してタブを閉じて終わる
2. 「並べ替え」を押して「新しい順」を選ぶ
3. 上から順に見て、オーナーからの返信が付いていない、★4か★5の、日本語の本文が15字以上ある口コミを1件だけ選ぶ（上から最大20件まで見る）。「もっと見る」があれば押して全文を読む
4. 開いたタブを閉じる
出力は次の3行だけ。前置き・説明・まとめは書かない。当てはまる口コミが無ければ NONE とだけ出力する。
STARS <4か5>
WHEN <投稿の時期 例: 2 週間前>
TEXT <口コミの本文を1行で。改行は空白に。書いた人の名前は入れない>
口コミを書く・返信する・保存・共有・ログインなど、読む以外の操作はしない。"""


def parse_gift(raw: str) -> dict:
    """{"rating", "days", "text"}／該当の口コミが無い {"none": True}／読めない {}"""
    st = re.search(r"^STARS\s*([45])\s*$", raw or "", re.M)
    wh = re.search(r"^WHEN\s*(.+)$", raw or "", re.M)
    tx = re.search(r"^TEXT\s*(.+)$", raw or "", re.M)
    if not (st and tx) or len(tx.group(1).strip()) < 15:
        return {"none": True} if re.search(r"^\s*NONE\s*$", raw or "", re.M) else {}   # 読めたが該当なし／読めない
    d = days_of(wh.group(1)) if wh else None
    return {"rating": int(st.group(1)), "days": d if d is not None else 9999, "text": tx.group(1).strip()[:400]}


def read_gift(rec: dict) -> dict:
    """営業の1通目「先に返事を1つ書いて渡す」の口コミ（sales-automation src/gift_mail・会長 2026-11-01）"""
    if not rec.get("place_id"):
        return {}
    return run_claude(GIFT_PROMPT.format(url=maps_url(rec["place_id"], rec.get("g_name") or rec.get("name") or "")),
                      rec["place_id"] + "_gift", parse_gift)


def read_full(place_id: str, name: str) -> dict:
    """無料点検用（line_detail.measure から）"""
    return run_claude(FULL_PROMPT.format(url=maps_url(place_id, name)), place_id + "_full", parse_full)


def read_shop(rec: dict) -> dict:
    return run_claude(PROMPT.format(url=maps_url(rec["place_id"], rec.get("g_name") or rec["name"])), rec["place_id"], parse)


def main() -> None:
    n = int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else 20
    sys.path.insert(0, os.path.expanduser("~/sales-automation"))
    from src import need_hypo
    rows = [json.loads(l) for l in open(OUT, encoding="utf-8") if l.strip()]
    todo = [(r, j) for r, j in need_hypo.judge_many([r for r in rows if r.get("portal_rank")])
            if not j["exclude"] and r.get("place_id") and r.get("g_real") != "chrome"]
    todo.sort(key=lambda x: -x[1]["score"])
    ok = ng = 0
    for r, _ in todo[:n]:
        got = read_shop(r)
        if got:
            r.update(got, g_real="chrome", g_real_at=datetime.now().strftime("%Y-%m-%d"))
            ok += 1
            print(f"[MAPS] {r['name'][:20]}｜最新 {got.get('g_last_review_days')}日前・90日 {got.get('g_recent90')}件・返信率 {got.get('g_reply_rate')}")
        else:
            ng += 1
            print(f"[MAPS] 読めない {r['name'][:20]}")
        open(OUT, "w", encoding="utf-8").write("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in rows))   # 1店ごとに保存（途中で止まっても残る）
    print(f"[MAPS] 読めた {ok}店・読めない {ng}店・残り {max(0, len(todo) - ok - ng)}店")
    if todo[:n] and ok == 0:
        sys.exit(1)   # 1店も読めない＝Chrome が起動していない・拡張が切れている → 健康診断に出す


if __name__ == "__main__":
    main()
