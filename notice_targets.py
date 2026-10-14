# -*- coding: utf-8 -*-
"""地方で「日本語の検索では上位10なのに、英語の検索では60位までに出ない」店（186軒）の、公開されている連絡先を集める。
会長 2026-10-14「メールも集めていいよ」。集めるだけで、送らない（送るのは会長の承認のあと・特定電子メール法の条件を守る）。

1. data/inb_frame60.jsonl から186軒を出す（三大都市圏を除く・同じ町×業種で日本語上位10・英語60位に無い）
2. 店の Googleマップのページから公式サイトの URL を取る
3. 公式サイトのトップと「お問い合わせ」らしいページ（同じドメイン・3ページまで）から、公開されているメールアドレスを拾う
出力: data/notice_targets.jsonl（1店1行・途中から再開できる）／data/notice_targets.csv
実行: GMAPS_PROFILE=~/meo-research/.gprofile python3 notice_targets.py
"""
from __future__ import annotations
import csv, json, os, re, sys, time
from collections import defaultdict
from urllib.parse import urljoin, urlparse

import requests

from common import accept_consent, browser, sync_playwright

OUT = "data/notice_targets.jsonl"
CSV = "data/notice_targets.csv"
METRO = ("京都", "名古屋", "大阪", "東京", "横浜", "神戸", "箱根", "鎌倉")   # 三大都市圏（箱根・鎌倉＝神奈川）
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
JUNK = re.compile(r"(example\.|sentry|wixpress|\.png|\.jpg|\.gif|\.webp|\.svg|@2x|domain\.|yourname|xxx@|sample@)", re.I)
CONTACT = re.compile(r"(contact|inquiry|toiawase|otoiawase|form|access|company|about|info|問い合わせ|問合せ|お問合|会社概要|店舗情報|アクセス)", re.I)
SKIP_HOST = ("instagram.com", "facebook.com", "twitter.com", "x.com", "tabelog.com", "hotpepper.jp", "gnavi.co.jp",
             "retty.me", "line.me", "google.com", "linktr.ee", "tiktok.com", "youtube.com")
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129 Safari/537.36"}


def targets() -> list[dict]:
    rows = [json.loads(l) for l in open("data/inb_frame60.jsonl", encoding="utf-8")]
    en, ja = defaultdict(set), defaultdict(list)
    for r in rows:
        k = (r["city"], r["industry"])
        if r["lang"] == "en":
            en[k].add(r["cid"])
        elif r["rank"] <= 10:
            ja[k].append(r)
    out, seen = [], set()
    for k, lst in ja.items():
        if k[0].startswith(METRO) or k not in en:
            continue
        for r in lst:
            if r["cid"] not in en[k] and r["cid"] not in seen:
                seen.add(r["cid"]); out.append(r)
    return out


def site_of(pg, href: str) -> dict:
    pg.goto(href, wait_until="commit", timeout=30000)
    accept_consent(pg)
    for _ in range(30):
        if pg.locator("h1").count():
            break
        time.sleep(0.5)
    time.sleep(1.5)
    a = pg.locator("a[data-item-id='authority']")
    url = a.first.get_attribute("href") if a.count() else ""
    ph = pg.locator("button[data-item-id^='phone']")
    phone = (ph.first.get_attribute("data-item-id") or "").replace("phone:tel:", "") if ph.count() else ""
    return {"website": url or "", "phone": phone}


def emails_from(url: str) -> tuple[list[str], list[str]]:
    """公式サイトのトップ＋お問い合わせらしいページ（同じドメイン・3ページまで）から、公開されているアドレス"""
    host = urlparse(url).netloc
    if not host or any(host.endswith(h) for h in SKIP_HOST):
        return [], []
    seen_pages, found, where = [], {}, []
    queue = [url]
    while queue and len(seen_pages) < 4:
        u = queue.pop(0)
        if u in seen_pages:
            continue
        seen_pages.append(u)
        try:
            r = requests.get(u, headers=UA, timeout=15)
            r.encoding = r.apparent_encoding or r.encoding
            html = r.text
        except Exception:
            continue
        for m in re.findall(r"mailto:([^\"'?>\s]+)", html) + EMAIL.findall(html):
            m = m.strip().strip(".").lower()
            if EMAIL.fullmatch(m) and not JUNK.search(m) and m not in found:
                found[m] = u
        if u == url:
            for href, text in re.findall(r"<a[^>]+href=[\"']([^\"'#]+)[\"'][^>]*>(.*?)</a>", html, re.S | re.I):
                full = urljoin(u, href)
                if urlparse(full).netloc == host and CONTACT.search(href + " " + re.sub("<[^>]+>", "", text)):
                    if full not in queue and full not in seen_pages:
                        queue.append(full)
        time.sleep(1)
    return list(found), [found[e] for e in found]


def main():
    ts = targets()
    done = set()
    if os.path.exists(OUT):
        done = {json.loads(l)["cid"] for l in open(OUT, encoding="utf-8")}
    todo = [r for r in ts if r["cid"] not in done]
    print(f"186軒中 {len(ts)}軒・済み {len(done)}・残り {len(todo)}", flush=True)
    if todo:
        with sync_playwright() as p:
            b, ctx = browser(p)
            pg = ctx.new_page()
            try:
                for i, r in enumerate(todo, 1):
                    rec = {"cid": r["cid"], "name": r["name"], "city": r["city"], "industry": r["industry"],
                           "rank_ja": r["rank"], "reviews": r.get("reviews"), "maps": r["href"].split("?")[0]}
                    try:
                        rec.update(site_of(pg, r["href"]))
                    except Exception as e:
                        rec.update(website="", phone="", err=str(e)[:80])
                    mails, pages = emails_from(rec["website"]) if rec.get("website") else ([], [])
                    rec.update(emails=mails, email_pages=pages, at=time.strftime("%Y-%m-%d %H:%M"))
                    with open(OUT, "a", encoding="utf-8") as f:
                        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    print(f"{i}/{len(todo)} {r['name'][:20]} site={'有' if rec.get('website') else '無'} mail={len(mails)}", flush=True)
                    time.sleep(2)
            finally:
                b.close()
    recs = [json.loads(l) for l in open(OUT, encoding="utf-8")]
    with open(CSV, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["店名", "町", "業種", "日本語の順位", "口コミ数", "公式サイト", "メール", "メールが載っていたページ", "電話", "Googleマップ"])
        for x in recs:
            w.writerow([x["name"], x["city"], x["industry"], x["rank_ja"], x.get("reviews"), x.get("website", ""),
                        " ".join(x.get("emails", [])), " ".join(x.get("email_pages", [])), x.get("phone", ""), x["maps"]])
    n_site = sum(1 for x in recs if x.get("website")); n_mail = sum(1 for x in recs if x.get("emails"))
    print(f"完了: {len(recs)}軒・公式サイトあり {n_site}・公開メールあり {n_mail} → {CSV}")


if __name__ == "__main__":
    os.environ.setdefault("GMAPS_PROFILE", os.path.expanduser("~/meo-research/.gprofile"))
    main()
