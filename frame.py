# -*- coding: utf-8 -*-
"""母集団づくり: 都市×業種で検索し、一覧から店（名前・評価・口コミ件数・業種・住所・順位・営業状態・紹介文）を集める。
実行: python3 frame.py [--limit N]   出力: data/frame.jsonl（再開可・同じ検索は飛ばす）
17_全国5000店調査_計画 §0。閲覧のみ・ログインなし・2〜5秒間隔。"""
from __future__ import annotations
import json, os, re, sys, time
from common import DATA, Blocked, accept_consent, append_jsonl, blocked, browser, nap, on_block, sync_playwright

CITIES = ["札幌市中央区", "旭川市", "函館市", "青森市", "盛岡市", "仙台市青葉区", "秋田市", "山形市", "福島市", "郡山市",
          "水戸市", "宇都宮市", "高崎市", "さいたま市大宮区", "川越市", "千葉市中央区", "船橋市", "新宿区", "渋谷区", "世田谷区",
          "吉祥寺", "立川市", "横浜市西区", "川崎市", "藤沢市", "新潟市中央区", "富山市", "金沢市", "福井市", "甲府市",
          "長野市", "松本市", "岐阜市", "静岡市葵区", "浜松市", "名古屋市中区", "名古屋市千種区", "岡崎市", "津市", "大津市",
          "京都市中京区", "京都市左京区", "大阪市北区", "大阪市中央区", "堺市", "神戸市中央区", "姫路市", "奈良市", "和歌山市", "鳥取市",
          "松江市", "岡山市北区", "広島市中区", "福山市", "山口市", "徳島市", "高松市", "松山市", "高知市", "福岡市中央区",
          "北九州市小倉北区", "佐賀市", "長崎市", "熊本市中央区", "大分市", "宮崎市", "鹿児島市", "那覇市"]
INDUSTRIES = ["カフェ", "美容室", "整体", "ラーメン", "居酒屋"]
OUT = os.path.join(DATA, "frame.jsonl")
DONE = os.path.join(DATA, "frame_done.json")


def parse_card(a) -> dict:
    al = a.get_attribute("aria-label") or ""
    href = a.get_attribute("href") or ""
    card = a.locator("xpath=..")
    txt = card.inner_text() if card.count() else ""
    lines = [l.strip() for l in txt.split("\n") if l.strip()]
    rec = {"name": al.strip()[:80], "href": href, "cid": None, "rating": None, "reviews": None, "category": None,
           "address": None, "status": None, "editorial": None, "price": None}
    m = re.search(r"!1s(0x[0-9a-f]+:0x[0-9a-f]+)", href)
    rec["cid"] = m.group(1) if m else None
    for up in ("..", "../..", "../../..", "../../../.."):
        lab = a.locator(f"xpath={up}").locator("[aria-label*='クチコミ']")
        found = False
        for i in range(min(3, lab.count())):
            m = re.search(r"(\d\.\d) つ星 クチコミ ([\d,]+) 件", lab.nth(i).get_attribute("aria-label") or "")
            if m:
                rec["rating"] = float(m.group(1))
                rec["reviews"] = int(m.group(2).replace(",", ""))
                found = True
                break
        if found:
            break
    if rec["reviews"] is None:
        m = re.search(r"(\d\.\d)\s*\(\s*([\d,]+)\s*\)", txt)
        if m:
            rec["rating"] = float(m.group(1))
            rec["reviews"] = int(m.group(2).replace(",", ""))
    for l in lines:
        if "·" in l and rec["category"] is None and not re.search(r"営業|閉店|開始|終了", l):
            parts = [x.strip() for x in l.split("·") if x.strip()]
            if parts:
                rec["category"] = parts[0][:30]
                if len(parts) > 1 and re.search(r"[０-９0-9]", parts[-1]):
                    rec["address"] = parts[-1][:60]
                for x in parts:
                    if "￥" in x or "¥" in x:
                        rec["price"] = x[:12]
        elif re.search(r"営業中|営業時間外|営業開始|営業終了|閉業|臨時休業", l):
            rec["status"] = l[:40]
        elif 12 <= len(l) <= 80 and rec["editorial"] is None and l != rec["name"] and not re.search(r"\d\.\d", l) and "·" not in l:
            rec["editorial"] = l[:80]
    return rec


def run(limit: int | None = None):
    done = set(json.load(open(DONE))) if os.path.exists(DONE) else set()
    todo = [(c, i) for c in CITIES for i in INDUSTRIES if f"{i} {c}" not in done]
    if limit:
        todo = todo[:limit]
    print(f"[frame] 検索 {len(todo)} 件（済 {len(done)}）", flush=True)
    with sync_playwright() as p:
        b, ctx = browser(p)
        pg = ctx.new_page()
        for n, (city, ind) in enumerate(todo, 1):
            q = f"{ind} {city}"
            t0 = time.time()
            if n % 40 == 0:   # メモリ対策: 40検索ごとにブラウザを作り直す
                try:
                    b.close()
                except Exception:
                    pass
                b, ctx = browser(p)
                pg = ctx.new_page()
            try:
                pg.goto("https://www.google.com/maps/search/" + q + "?hl=ja", wait_until="domcontentloaded", timeout=40000)
                accept_consent(pg)
                if blocked(pg):
                    on_block(pg, "frame")
                    continue
                pg.wait_for_selector("div[role='feed']", timeout=25000)
                feed = pg.locator("div[role='feed']")
                last = -1
                for _ in range(8):
                    feed.evaluate("el => el.scrollBy(0, 5000)")
                    time.sleep(1.1)
                    cnt = pg.locator("div[role='feed'] a[href*='/maps/place/']").count()
                    if cnt == last:
                        break
                    last = cnt
                items = pg.locator("div[role='feed'] a[href*='/maps/place/']")
                k = 0
                for i in range(items.count()):
                    try:
                        rec = parse_card(items.nth(i))
                    except Exception:
                        continue
                    if not rec["name"]:
                        continue
                    rec.update({"query": q, "city": city, "industry": ind, "rank": i + 1, "at": time.strftime("%Y-%m-%d %H:%M")})
                    append_jsonl(OUT, rec)
                    k += 1
                done.add(q)
                json.dump(sorted(done), open(DONE, "w"), ensure_ascii=False)
                print(f"[frame] {n}/{len(todo)} {q}: {k}店 {round(time.time() - t0, 1)}s", flush=True)
            except Blocked:
                raise SystemExit(2)
            except Exception as e:
                print(f"[frame] 失敗 {q}: {str(e)[:80]}", flush=True)
            nap()
        b.close()


if __name__ == "__main__":
    lim = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    run(lim)
