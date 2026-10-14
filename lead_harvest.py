# -*- coding: utf-8 -*-
"""営業リストを24時間作り続ける（会長 2026-10-14「リストが尽きることはない。常に生成し続けて。DM・メール・Facebook も」）。

業種×市区（sales-automation の config.OUTREACH_INDUSTRIES × OUTREACH_CITIES・18業種×約300市区）を順に回し、
Googleマップの一覧（60位まで）→ 店のページで公式サイト・電話・住所 → 公式サイトから Instagram・Facebook・公開メールを拾う。
公式サイトの欄が Instagram／Facebook そのものの店も多い（地方の186軒では 152軒中29軒が Instagram）。

出力: data/leads/leads.jsonl（1店1行・cid で重複なし・途中から再開）
      data/leads/queries_done.json（済んだ 業種×市区）
送らない。DM は dm_daily.py が1日30件を選び、会長の LINE にコピペできる形で届ける。メールは Railway の営業メール（outreach_auto）が別に送る。
実行: launchd com.hitotsunagi.lead-harvest（KeepAlive・ログインした Chrome プロファイル .gprofile_harvest）
"""
from __future__ import annotations
import json, os, re, sys, time
from urllib.parse import urljoin, urlparse

import requests

from common import accept_consent, blocked, browser, sync_playwright
from frame_inbound import parse_card

sys.path.insert(0, os.path.expanduser("~/sales-automation"))
import config  # noqa: E402  業種・市区・チェーンの正本
from src.lead_filter import is_excluded_chain  # noqa: E402

DIR = "data/leads"
LEADS = f"{DIR}/leads.jsonl"
DONE = f"{DIR}/queries_done.json"
TOPN = 60
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129 Safari/537.36"}
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
JUNK = re.compile(r"(^u00|example\.|sentry|wixpress|\.png|\.jpg|\.gif|\.webp|\.svg|@2x|domain\.|yourname|xxx@|sample@)", re.I)
IG = re.compile(r"https?://(?:www\.)?instagram\.com/([A-Za-z0-9._]{2,30})/?", re.I)
FB = re.compile(r"https?://(?:www\.|m\.|ja-jp\.)?facebook\.com/((?:profile\.php\?id=\d+)|[A-Za-z0-9.\-]{3,60})/?", re.I)
IG_BAD = {"p", "explore", "accounts", "reel", "reels", "stories", "share", "sharer", "direct", "about", "legal", "developer", "tv"}
FB_BAD = {"sharer", "sharer.php", "plugins", "tr", "dialog", "share", "share.php", "login", "help", "policies", "watch",
          "groups", "events", "pages", "hashtag", "photo.php", "permalink.php", "story.php", "l.php", "privacy", "business"}
CONTACT = re.compile(r"(contact|inquiry|toiawase|otoiawase|access|company|about|shop|info|問い合わせ|問合せ|会社概要|店舗情報|アクセス)", re.I)


def queries() -> list[tuple[str, str]]:
    return [(c, ind) for c in config.OUTREACH_CITIES for ind in config.OUTREACH_INDUSTRIES]   # 市区ごとに全業種（DM の業種が偏らない）


def load_json(p, d):
    try:
        return json.load(open(p, encoding="utf-8"))
    except Exception:
        return d


def known_cids() -> set:
    if not os.path.exists(LEADS):
        return set()
    return {json.loads(l)["cid"] for l in open(LEADS, encoding="utf-8") if l.strip()}


def social_from_url(url: str) -> dict:
    out = {"instagram": "", "facebook": ""}
    m = IG.match(url or "")
    if m and m.group(1).lower() not in IG_BAD:
        out["instagram"] = f"https://www.instagram.com/{m.group(1)}/"
    m = FB.match(url or "")
    if m and m.group(1).lower().split("?")[0] not in FB_BAD:
        out["facebook"] = f"https://www.facebook.com/{m.group(1)}"
    return out


def enrich_site(url: str) -> dict:
    """公式サイト（トップ＋お問い合わせらしいページ3つまで）から Instagram・Facebook・公開メール（出典ページつき）"""
    res = {"instagram": "", "facebook": "", "emails": [], "email_pages": [], "no_sales": False}
    host = urlparse(url).netloc
    if not host:
        return res
    queue, seen, found = [url], [], {}
    while queue and len(seen) < 4:
        u = queue.pop(0)
        if u in seen:
            continue
        seen.append(u)
        try:
            r = requests.get(u, headers=UA, timeout=12)
            r.encoding = r.apparent_encoding or r.encoding
            html = r.text[:600000]
        except Exception:
            continue
        if re.search(r"営業(の)?(メール|電話|目的).{0,12}(お断り|ご遠慮|禁止)|セールス.{0,8}(お断り|ご遠慮)", html):
            res["no_sales"] = True
        for href in re.findall(r"href=[\"']([^\"']+)[\"']", html):
            s = social_from_url(href)
            res["instagram"] = res["instagram"] or s["instagram"]
            res["facebook"] = res["facebook"] or s["facebook"]
        for m in re.findall(r"mailto:([^\"'?>\s]+)", html) + EMAIL.findall(html):
            m = m.strip().strip(".").lower()
            if EMAIL.fullmatch(m) and not JUNK.search(m) and m not in found:
                found[m] = u
        if u == url:
            for href, text in re.findall(r"<a[^>]+href=[\"']([^\"'#]+)[\"'][^>]*>(.*?)</a>", html, re.S | re.I):
                full = urljoin(u, href)
                if urlparse(full).netloc == host and CONTACT.search(href + " " + re.sub("<[^>]+>", "", text)) \
                        and full not in queue and full not in seen:
                    queue.append(full)
        time.sleep(0.8)
    res["emails"], res["email_pages"] = list(found), [found[e] for e in found]
    return res


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


def run_query(pg, city: str, ind: str, have: set) -> int:
    q = f"{ind} {city}"
    shops = list_shops(pg, q)
    added = 0
    for s in shops:
        if not s.get("cid") or s["cid"] in have:
            continue
        if is_excluded_chain(s.get("name") or "")[0]:
            have.add(s["cid"]); continue
        try:
            p = place(pg, s["href"])
        except Exception as e:
            p = {"website": "", "phone": "", "address": "", "closed": False, "err": str(e)[:60]}
        rec = {"cid": s["cid"], "name": s["name"], "industry": ind, "city": city, "rank": s["rank"],
               "rating": s.get("rating"), "reviews": s.get("reviews"), "category": s.get("category"),
               "maps": s["href"].split("?")[0], **p}
        soc = social_from_url(p.get("website", ""))
        rec.update(soc, emails=[], email_pages=[], no_sales=False)
        if p.get("website") and not (soc["instagram"] or soc["facebook"]):
            e = enrich_site(p["website"])
            rec["instagram"] = rec["instagram"] or e["instagram"]
            rec["facebook"] = rec["facebook"] or e["facebook"]
            rec.update(emails=e["emails"], email_pages=e["email_pages"], no_sales=e["no_sales"])
        rec["at"] = time.strftime("%Y-%m-%d %H:%M")
        with open(LEADS, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        have.add(s["cid"]); added += 1
        time.sleep(1.5)
    return added


def main():
    os.makedirs(DIR, exist_ok=True)
    done = load_json(DONE, {})
    have = known_cids()
    todo = [qc for qc in queries() if f"{qc[1]}|{qc[0]}" not in done]
    if not todo:                      # 一巡したら、古い順にやり直す（店は入れ替わる）
        done = {}; todo = queries()
    print(f"[HARVEST] 残り {len(todo)} 検索・既知 {len(have)} 店", flush=True)
    with sync_playwright() as p:
        b, ctx = browser(p)
        pg = ctx.new_page()
        fails = 0
        try:
            for city, ind in todo:
                t0 = time.time()
                try:
                    n = run_query(pg, city, ind, have)
                    fails = 0
                except Exception as e:
                    fails += 1
                    print(f"[HARVEST][ERR] {ind} {city}: {str(e)[:100]}", flush=True)
                    if fails >= 5:
                        print("[HARVEST] 5回続けて失敗。30分休んで終了（launchd が再起動）", flush=True)
                        time.sleep(1800); return
                    time.sleep(60); continue
                done[f"{ind}|{city}"] = time.strftime("%Y-%m-%d %H:%M")
                json.dump(done, open(DONE, "w", encoding="utf-8"), ensure_ascii=False)
                print(f"[HARVEST] {ind} {city}: +{n}（{int(time.time() - t0)}秒・計 {len(have)}）", flush=True)
        finally:
            b.close()


if __name__ == "__main__":
    os.environ.setdefault("GMAPS_PROFILE", os.path.expanduser("~/meo-research/.gprofile_harvest"))
    main()
