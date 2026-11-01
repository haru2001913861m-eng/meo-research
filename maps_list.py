# -*- coding: utf-8 -*-
"""Googleマップの一覧と店のページを読む部品（list_build.py が使う。旧 lead_harvest.py から移した・2026-11-01）"""
from __future__ import annotations
import re
import time

from common import accept_consent, blocked
from frame_inbound import parse_card

import os, sys
sys.path.insert(0, os.path.expanduser("~/sales-automation"))
import config  # noqa: E402  業種・市区の正本

TOPN = 60
IG = re.compile(r"https?://(?:www\.)?instagram\.com/([A-Za-z0-9._]{2,30})/?", re.I)
FB = re.compile(r"https?://(?:www\.|m\.|ja-jp\.)?facebook\.com/((?:profile\.php\?id=\d+)|[A-Za-z0-9.\-]{3,60})/?", re.I)
IG_BAD = {"p", "explore", "accounts", "reel", "reels", "stories", "share", "sharer", "direct", "about", "legal", "developer", "tv"}
FB_BAD = {"sharer", "sharer.php", "plugins", "tr", "dialog", "share", "share.php", "login", "help", "policies", "watch",
          "groups", "events", "pages", "hashtag", "photo.php", "permalink.php", "story.php", "l.php", "privacy", "business"}

def queries() -> list[tuple[str, str]]:
    return [(c, ind) for c in config.OUTREACH_CITIES for ind in config.OUTREACH_INDUSTRIES]   # 市区ごとに全業種（業種が偏らない）


def social_from_url(url: str) -> dict:
    out = {"instagram": "", "facebook": ""}
    m = IG.match(url or "")
    if m and m.group(1).lower() not in IG_BAD:
        out["instagram"] = f"https://www.instagram.com/{m.group(1)}/"
    m = FB.match(url or "")
    if m and m.group(1).lower().split("?")[0] not in FB_BAD:
        out["facebook"] = f"https://www.facebook.com/{m.group(1)}"
    return out



def goto(pg, url):
    for att in range(3):
        try:
            pg.goto(url, wait_until="commit", timeout=30000); return
        except Exception:
            if att == 2:
                raise
            time.sleep(5 + 5 * att)



def list_shops(pg, q: str) -> list[dict]:
    goto(pg, "https://www.google.com/maps/search/" + q + "?hl=ja")
    accept_consent(pg)
    if blocked(pg):
        raise RuntimeError("blocked")
    pg.wait_for_selector("div[role='feed']", timeout=25000)
    feed = pg.locator("div[role='feed']")
    last, still = -1, 0
    for _ in range(TOPN // 5 + 4):
        feed.evaluate("el => el.scrollBy(0, 5000)"); time.sleep(1.2)
        cnt = pg.locator("div[role='feed'] a[href*='/maps/place/']").count()
        if cnt >= TOPN:
            break
        still = still + 1 if cnt == last else 0
        if still >= 2:
            break
        last = cnt
    items = pg.locator("div[role='feed'] a[href*='/maps/place/']")
    out = []
    for i in range(min(items.count(), TOPN)):
        try:
            r = parse_card(items.nth(i), "ja"); r["rank"] = i + 1; out.append(r)
        except Exception:
            pass
    return out



def place(pg, href: str) -> dict:
    goto(pg, href)
    accept_consent(pg)
    for _ in range(30):
        if pg.locator("h1").count():
            break
        time.sleep(0.5)
    time.sleep(1.2)
    get = lambda sel, attr: (pg.locator(sel).first.get_attribute(attr) or "") if pg.locator(sel).count() else ""
    web = get("a[data-item-id='authority']", "href")
    phone = get("button[data-item-id^='phone']", "data-item-id").replace("phone:tel:", "")
    addr = get("button[data-item-id='address']", "aria-label").replace("住所:", "").strip()
    closed = bool(re.search(r"閉業|Permanently closed", pg.locator("body").inner_text()[:4000])) if pg.locator("body").count() else False
    return {"website": web, "phone": phone, "address": addr, "closed": closed}



def fresh_page(ctx, pg):
    try:
        pg.close()
    except Exception:
        pass
    return ctx.new_page()


