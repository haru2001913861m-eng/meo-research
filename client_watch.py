# -*- coding: utf-8 -*-
"""契約店の見回り（Mac・週1）。狙う言葉での位置と、新しい口コミ（本文つき）を読み、Notion の台帳「観測JSON」へ書く。
Railway（sales-automation の meo_ops_run）が毎朝それを取り込み、返信文・週の順位報告を店へ送る。

実行: python3 client_watch.py [--dry] [--only 店ID]
  --dry   : Notion に書かず、読んだ結果を表示だけ
入力: Notion「🏪 MEO 契約店の台帳」の active / onboarding の店（台帳JSON の keywords / place_url / cid）
決まり: 店ごとに別々に読む（ある店の結果を別の店の行に書かない＝client_id を観測に入れ、Railway 側でも照合）。
        口コミの本文は「契約店の自分の口コミ」だけ読む（返信文を作るため）。調査用の detail.py は本文を保存しない。
間隔 2〜5 秒・制限表示が出たら休む（common.py）。ログイン済みプロファイル推奨（GMAPS_PROFILE）。
"""
from __future__ import annotations
import json, os, re, sys, time
from common import accept_consent, blocked, browser, nap, on_block, rel_days, sync_playwright

SA = os.path.expanduser("~/sales-automation")
sys.path.insert(0, SA)
os.chdir(SA)   # config が .env を読む
import config  # noqa: E402
from src.notion_client import get_client  # noqa: E402

DRY = "--dry" in sys.argv
ONLY = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else ""
MAX_RANK = 60


def clients() -> list[dict]:
    n = get_client(); out = []; cursor = None
    while True:
        kw = {"database_id": config.MEO_CLIENTS_DB_ID, "page_size": 100}
        if cursor:
            kw["start_cursor"] = cursor
        res = n.databases.query(**kw)
        for p in res["results"]:
            raw = "".join(t["plain_text"] for t in p["properties"]["台帳JSON"]["rich_text"])
            try:
                c = json.loads(raw)
            except Exception:
                continue
            if c.get("status") in ("active", "onboarding") and (not ONLY or c["client_id"] == ONLY):
                out.append({"page": p["id"], **c})
        if not res.get("has_more"):
            break
        cursor = res["next_cursor"]
    return out


TOP: list = []   # 直前の検索の上位（周辺店の比較用・プレミアム）


def rank_of(pg, kw: str, cid: str, name: str, lang: str = "ja") -> int | None:
    pg.goto("https://www.google.com/maps/search/" + kw + f"?hl={lang}", wait_until="domcontentloaded", timeout=40000)
    accept_consent(pg)
    if blocked(pg):
        on_block(pg, "watch"); return None
    try:
        pg.wait_for_selector("div[role='feed']", timeout=20000)
    except Exception:
        return None
    feed = pg.locator("div[role='feed']"); last = -1
    TOP.clear()
    try:
        from frame import parse_card
        from frame_inbound import parse_card as parse_card_l
        items = pg.locator("div[role='feed'] a[href*='/maps/place/']")
        for i in range(min(5, items.count())):
            rc = parse_card(items.nth(i)) if lang == "ja" else parse_card_l(items.nth(i), lang)
            if not ((cid and cid == rc.get("cid")) or rc.get("name") == name):
                TOP.append({"name": rc["name"], "rating": rc.get("rating"), "reviews": rc.get("reviews"), "rank": i + 1})
    except Exception:
        pass
    for _ in range(10):
        items = pg.locator("div[role='feed'] a[href*='/maps/place/']")
        for i in range(items.count()):
            href = items.nth(i).get_attribute("href") or ""
            al = (items.nth(i).get_attribute("aria-label") or "").strip()
            if (cid and cid in href) or (not cid and name and al == name):
                return i + 1
        if items.count() >= MAX_RANK or items.count() == last:
            break
        last = items.count()
        feed.evaluate("el => el.scrollBy(0, 5000)"); time.sleep(1.1)
    return None


def own_reviews(pg, href: str) -> dict:
    pg.goto(href if "hl=" in href else href + ("&" if "?" in href else "?") + "hl=ja", wait_until="domcontentloaded", timeout=40000)
    accept_consent(pg)
    pg.wait_for_selector("h1", timeout=20000); time.sleep(1.2)
    out = {"name": pg.locator("h1").first.inner_text()[:80], "reviews": []}
    m = re.search(r"!19s(ChIJ[\w-]+)", pg.url)   # 口コミ用 QR（writereview?placeid=）に要る place_id（2026-10-12）
    if m:
        out["place_id"] = m.group(1)
    m = re.search(r"(\d\.\d)\s*\n?\s*\(?([\d,]+)\)?", pg.locator("body").inner_text()[:3000])
    if m:
        out["rating"] = float(m.group(1)); out["review_count"] = int(m.group(2).replace(",", ""))
    tab = pg.locator("button[role='tab']", has_text="クチコミ")
    if not tab.count():
        return out
    tab.first.click(timeout=5000); time.sleep(1.5)
    try:
        pg.locator("button", has_text="並べ替え").first.click(timeout=3000); time.sleep(0.6)
        pg.locator("[role='menuitemradio']", has_text="新しい順").first.click(timeout=3000); time.sleep(1.2)
    except Exception:
        pass
    cards = pg.locator("div[data-review-id][aria-label]")
    if not cards.count():
        cards = pg.locator("[data-review-id]")
    seen = set()
    for i in range(min(cards.count(), 30)):
        c = cards.nth(i)
        rid = c.get_attribute("data-review-id") or ""
        if not rid or rid in seen:
            continue
        seen.add(rid)
        try:
            more = c.locator("button", has_text="もっと見る")
            if more.count():
                more.first.click(timeout=1500)
            t = c.inner_text()
        except Exception:
            continue
        star = c.locator("[role='img'][aria-label*='つ星']")
        rating = None
        if star.count():
            m = re.search(r"(\d)", star.first.get_attribute("aria-label") or "")
            rating = int(m.group(1)) if m else None
        translated = bool(re.search(r"Google による翻訳|（翻訳）|原文を表示|原文を見る", t))
        if translated:   # 外国語の口コミ（日本語の画面では訳が出る）→ 原文を開いて読む（返信の言葉を決めるため・2026-10-17）
            try:
                c.locator("button", has_text=re.compile("原文")).first.click(timeout=1500); time.sleep(0.4)
                t = c.inner_text()
            except Exception:
                pass
        lines = [l for l in t.split("\n") if l.strip()]
        author = (c.get_attribute("aria-label") or (lines[0] if lines else ""))[:40]
        body = t.split("オーナーからの返信")[0]
        owner_reply = ""
        if "オーナーからの返信" in t:
            owner_reply = re.sub(r"\d+\s*(?:分|時間|日|週間|か月|カ月|ヶ月|年)前|昨日|今日", "", t.split("オーナーからの返信", 1)[1]).strip()[:300]
        md = re.search(r"(\d+\s*(?:分|時間|日|週間|か月|カ月|ヶ月|年)前|昨日|今日)", body)
        text = body.split(md.group(1), 1)[1] if md else body
        days = (0 if re.search(r"分|時間|今日", md.group(1)) else rel_days(md.group(1))) if md else None
        text = re.split(r"食事の種類|食事:|1 人あたりの料金|おすすめの料理|Meal type", text)[0]
        text = re.sub(r"(もっと見る|いいね|共有|新規|ローカルガイド.*|Google による翻訳|原文を表示|翻訳を表示|（翻訳）.*)", "", text).strip()[:600]
        out["reviews"].append({"key": rid, "author": author, "rating": rating, "text": text,
                               "days": days, "has_reply": "オーナーからの返信" in t, "owner_reply": owner_reply,
                               **({"lang": "foreign"} if translated else {})})
        if len(out["reviews"]) >= 20:
            break
    return out


def write(c: dict, obs: dict) -> None:
    txt = json.dumps(obs, ensure_ascii=False)
    parts = [txt[i:i + 1900] for i in range(0, len(txt), 1900)][:100]
    get_client().pages.update(page_id=c["page"], properties={"観測JSON": {"rich_text": [{"type": "text", "text": {"content": p}} for p in parts]}})


def main():
    cs = clients()
    # 会長 2026-10-12: 月曜に全店ぶんを溜めない → 契約日の曜日の店だけ（初回＝順位が無い店はすぐ）
    # 口コミは毎日・全店（返信は7日以内に）。順位と18項目は契約日の曜日の店だけ（初回はすぐ）
    wd = time.localtime().tm_wday
    for c in cs:
        c["_full"] = bool(ONLY) or not c.get("ranks") or c.get("rank_weekday", 0) == wd
    print(f"[watch] 店 {len(cs)}（順位も読む店 {sum(1 for c in cs if c['_full'])}）", flush=True)
    with sync_playwright() as p:
        b, ctx = browser(p, profile=os.getenv("GMAPS_PROFILE"))
        pg = ctx.new_page()
        for c in cs:
            t0 = time.time()
            obs = {"client_id": c["client_id"], "at": time.strftime("%Y-%m-%dT%H:%M:%S+09:00"), "ranks": [], "reviews": []}
            try:
                for j, kw in enumerate(c.get("keywords", []) if c.get("_full") else []):
                    obs["ranks"].append({"kw": kw, "rank": rank_of(pg, kw, c.get("cid", ""), c.get("shop", ""))}); nap()
                    if j == 0 and c.get("pack") == "プレミアム":
                        obs["competitors"] = TOP[:3]
                # 英語の地図（スタンダード以上・台帳の keywords_en / need_en_profile は Railway の meo_screens が置く）
                if c.get("need_en_profile") and c.get("place_url"):
                    import en_rank
                    shop = en_rank.find_shop(pg, c["place_url"])
                    if shop.get("cid"):
                        obs["en_profile"] = {"name_en": shop.get("name_en"), "city_en": shop.get("city_en"), "address_en": shop.get("address_en")}
                    nap()
                for j, kw in enumerate(c.get("keywords_en", []) if c.get("_full") else []):
                    obs.setdefault("ranks_en", []).append({"kw": kw, "rank": rank_of(pg, kw, c.get("cid", ""), "", "en")}); nap()
                    if j == 0 and c.get("pack") == "プレミアム":
                        obs["competitors_en"] = TOP[:3]
                job = c.get("ai_job") or {}
                if job and job.get("due", "9999") <= time.strftime("%Y-%m-%d") and job.get("area"):
                    import ai_ask
                    a = ai_ask.check(c.get("shop", ""), (c.get("en") or {}).get("name_en") or (c.get("en") or {}).get("name_en_sheet", ""),
                                     job["area"], job.get("city_en", ""), job.get("industry", ""), tuple(job["langs"]), int(job.get("runs", 3)), who=c["client_id"][:10])
                    obs["ai"] = ({k: v for k, v in a.items() if k != "answers"} if a.get("ok")
                                 else {"at": time.strftime("%Y-%m-%dT%H:%M:%S+09:00"), "error": a.get("why", "?")})
                if c.get("place_url"):
                    try:   # 月1点検の材料（公開画面の 18項目のうち見える物: サイト・電話・営業時間・写真枚数・投稿・説明・オーナー確認）
                        if not c.get("_full"):
                            raise RuntimeError("今日は口コミだけ")
                        from detail import read_store
                        st = read_store(pg, c["place_url"])
                        obs["store"] = {k: v for k, v in st.items() if k not in ("name",)}
                    except Exception as e:
                        if "口コミだけ" not in str(e):
                            obs["store_error"] = str(e)[:80]
                    r = own_reviews(pg, c["place_url"])
                    if c.get("shop") and r.get("name") and r["name"] != c["shop"]:
                        obs["name_seen"] = r["name"]   # 名前が台帳と違う → Railway 側で会長に知らせる
                    obs.update({k: v for k, v in r.items() if k != "name"})
            except Exception as e:
                obs["error"] = str(e)[:120]
            print(f"[watch] {c.get('shop')}: 順位 {[(x['kw'], x['rank']) for x in obs['ranks']]} 口コミ {len(obs['reviews'])} {round(time.time() - t0)}s", flush=True)
            if DRY:
                print(json.dumps(obs, ensure_ascii=False)[:800])
            else:
                write(c, obs)
            nap()
        b.close()


if __name__ == "__main__":
    main()
