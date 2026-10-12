# -*- coding: utf-8 -*-
"""全国MEO調査の共通部品（Playwright・ログインなし・閲覧のみ）。
決まり: 口コミ本文は保存しない（分類の結果＝件数だけ残す）。投稿者名も保存しない。店名・住所・公開の数字だけ。
負荷: 1リクエストごとに2〜5秒の間隔。ブロックの兆候があれば止める（CI では即終了してログに残す）。"""
from __future__ import annotations
import json, os, random, re, time
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
IN_CI = os.getenv("CI") == "true"


class Blocked(RuntimeError):
    pass


def browser(p, headless=True, profile: str | None = None):
    # 10/12: ログインなし・画面なしだと Google マップが「機能を絞った表示」（口コミ5件・言語不明）になる。
    # 調査用アカウントでログインした Chrome プロファイルを、画面ありで画面の外に置いて使うと普通の表示になる（実測）。
    profile = profile or os.getenv("GMAPS_PROFILE")
    if profile:
        ctx = p.chromium.launch_persistent_context(
            profile, channel="chrome", headless=False, viewport={"width": 1280, "height": 1000}, locale="en-US",
            ignore_default_args=["--use-mock-keychain", "--enable-automation"],
            args=["--window-position=-3000,-3000", "--window-size=1280,1000"])
        return ctx, ctx   # b.close() も ctx.close() で閉じる
    kw = {"headless": headless}
    if not IN_CI:
        kw["channel"] = "chrome"   # Mac ではシステムの Chrome、CI では同梱 Chromium
    b = p.chromium.launch(**kw)
    ctx = b.new_context(locale="ja-JP", viewport={"width": 1280, "height": 1000}, user_agent=UA,
                        extra_http_headers={"Accept-Language": "ja,en;q=0.8"})
    return b, ctx


def nap(a=2.0, b=5.0):
    time.sleep(random.uniform(a, b))


def accept_consent(pg) -> None:
    """同意画面（consent.google.com）が出たら「すべて同意」を押す。出なければ何もしない。"""
    try:
        if "consent.google" in pg.url or pg.locator("form[action*='consent']").count():
            for label in ("すべて同意", "Accept all", "同意する", "I agree"):
                btn = pg.locator("button", has_text=label)
                if btn.count():
                    btn.first.click(timeout=3000)
                    time.sleep(1.5)
                    return
    except Exception:
        pass


def blocked(pg) -> bool:
    if "/sorry/" in pg.url:
        return True
    head = pg.content()[:4000]
    return ("unusual traffic" in head) or ("通常と異なるトラフィック" in head)


def on_block(pg, where: str) -> None:
    """ブロック時の扱い: CI では終了コード2で止める（分かった時点でMacに切替）。Mac では30分待つ。"""
    print(f"[{where}] ブロック検知 url={pg.url[:80]}", flush=True)
    if IN_CI:
        raise Blocked(where)
    time.sleep(1800)


def append_jsonl(path: str, rec: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def read_jsonl(path: str) -> list[dict]:
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def rel_days(s: str | None) -> int | None:
    """'3 週間前' → 21。None なら None。"""
    if not s:
        return None
    if "今日" in s:
        return 0
    if "昨日" in s:
        return 1
    m = re.search(r"(\d+)\s*(日|週間|か月|カ月|ヶ月|年)", s)
    if not m:
        return None
    n, u = int(m.group(1)), m.group(2)
    return n * {"日": 1, "週間": 7, "か月": 30, "カ月": 30, "ヶ月": 30, "年": 365}[u]
