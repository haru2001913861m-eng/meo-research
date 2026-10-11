# -*- coding: utf-8 -*-
"""インバウンド調査・母集団: 観光地×業種を「日本語の検索」と「英語の検索（hl=en）」で引き、上位の店を集める。
問い: 英語で探す人に出てくる店は、日本語で探す人に出てくる店と同じか。違うなら何が違うか。
実行: python3 frame_inbound.py [--limit N]   出力: data/inb_frame.jsonl（再開可）
閲覧のみ・ログインなし・2〜5秒間隔・口コミ本文は保存しない（common.py の決まり）。"""
from __future__ import annotations
import json, os, re, sys, time
from common import DATA, Blocked, accept_consent, append_jsonl, blocked, browser, nap, on_block, sync_playwright

# (日本語の地名, 英語の地名)。英語側は都市名を足して曖昧さを消す（9/24: 「三条」が新潟の三条市になった）
CITIES = [("東京 新宿", "Shinjuku Tokyo"), ("東京 渋谷", "Shibuya Tokyo"), ("東京 浅草", "Asakusa Tokyo"), ("東京 銀座", "Ginza Tokyo"),
          ("東京 池袋", "Ikebukuro Tokyo"), ("東京 秋葉原", "Akihabara Tokyo"), ("東京 上野", "Ueno Tokyo"), ("東京 六本木", "Roppongi Tokyo"),
          ("鎌倉", "Kamakura"), ("横浜 中華街", "Yokohama Chinatown"), ("箱根湯本", "Hakone-Yumoto"), ("日光", "Nikko"),
          ("金沢", "Kanazawa"), ("高山", "Takayama Gifu"), ("松本", "Matsumoto Nagano"), ("京都 祇園", "Gion Kyoto"),
          ("京都 河原町", "Kawaramachi Kyoto"), ("京都 嵐山", "Arashiyama Kyoto"), ("大阪 道頓堀", "Dotonbori Osaka"), ("大阪 難波", "Namba Osaka"),
          ("大阪 梅田", "Umeda Osaka"), ("奈良", "Nara"), ("神戸 三宮", "Sannomiya Kobe"), ("広島", "Hiroshima"),
          ("宮島", "Miyajima"), ("福岡 博多", "Hakata Fukuoka"), ("札幌 すすきの", "Susukino Sapporo"), ("小樽", "Otaru"),
          ("那覇 国際通り", "Kokusai Street Naha"), ("別府", "Beppu"), ("長崎", "Nagasaki"), ("名古屋 栄", "Sakae Nagoya")]
INDUSTRIES = [("ラーメン", "ramen"), ("寿司", "sushi"), ("居酒屋", "izakaya"), ("カフェ", "cafe"), ("焼肉", "yakiniku"), ("マッサージ", "massage")]
OUT = os.path.join(DATA, os.getenv("INB_FRAME_OUT", "inb_frame.jsonl"))
DONE = os.path.join(DATA, os.getenv("INB_FRAME_DONE", "inb_frame_done.json"))
TOPN = 20

RE_JA = re.compile(r"(\d\.\d) つ星 クチコミ ([\d,]+) 件")
RE_EN = re.compile(r"(\d\.\d) stars ([\d,]+) [Rr]eviews")


def parse_card(a, lang: str) -> dict:
    al = a.get_attribute("aria-label") or ""
    href = a.get_attribute("href") or ""
    card = a.locator("xpath=..")
    txt = card.inner_text() if card.count() else ""
    rec = {"name": al.strip()[:80], "href": href, "cid": None, "rating": None, "reviews": None, "category": None, "status": None}
    m = re.search(r"!1s(0x[0-9a-f]+:0x[0-9a-f]+)", href)
    rec["cid"] = m.group(1) if m else None
    for up in ("..", "../..", "../../..", "../../../.."):
        lab = a.locator(f"xpath={up}").locator("[aria-label*='クチコミ'], [aria-label*='eviews']")
        found = False
        for i in range(min(3, lab.count())):
            s = lab.nth(i).get_attribute("aria-label") or ""
            m = RE_JA.search(s) or RE_EN.search(s)
            if m:
                rec["rating"] = float(m.group(1)); rec["reviews"] = int(m.group(2).replace(",", "")); found = True
                break
        if found:
            break
    if rec["reviews"] is None:
        m = re.search(r"(\d\.\d)\s*\(\s*([\d,]+)\s*\)", txt)
        if m:
            rec["rating"] = float(m.group(1)); rec["reviews"] = int(m.group(2).replace(",", ""))
    for l in [x.strip() for x in txt.split("\n") if x.strip()]:
        if "·" in l and rec["category"] is None and not re.search(r"営業|閉店|Open|Closed", l):
            parts = [x.strip() for x in l.split("·") if x.strip()]
            if parts:
                rec["category"] = parts[0][:30]
        elif re.search(r"営業中|営業時間外|閉業|Open|Closed|Permanently", l):
            rec["status"] = l[:40]
    rec["latin_name"] = bool(re.search(r"[A-Za-z]{3,}", rec["name"]))
    return rec


def run(limit: int | None = None):
    done = set(json.load(open(DONE))) if os.path.exists(DONE) else set()
    todo = []
    for (cj, ce) in CITIES:
        for (ij, ie) in INDUSTRIES:
            for lang, q in (("ja", f"{ij} {cj}"), ("en", f"{ie} {ce}")):
                if f"{lang}|{q}" not in done:
                    todo.append((lang, q, cj, ij))
    if limit:
        todo = todo[:limit]
    print(f"[inb_frame] 検索 {len(todo)} 件（済 {len(done)}）", flush=True)
    with sync_playwright() as p:
        b, ctx = browser(p)
        pg = ctx.new_page()
        for n, (lang, q, city, ind) in enumerate(todo, 1):
            t0 = time.time()
            if n % 40 == 0:
                try:
                    b.close()
                except Exception:
                    pass
                b, ctx = browser(p)
                pg = ctx.new_page()
            try:
                pg.goto("https://www.google.com/maps/search/" + q + f"?hl={lang}", wait_until="domcontentloaded", timeout=40000)
                accept_consent(pg)
                if blocked(pg):
                    on_block(pg, "inb_frame")
                    continue
                pg.wait_for_selector("div[role='feed']", timeout=25000)
                feed = pg.locator("div[role='feed']")
                last = -1
                for _ in range(4):
                    feed.evaluate("el => el.scrollBy(0, 5000)")
                    time.sleep(1.1)
                    cnt = pg.locator("div[role='feed'] a[href*='/maps/place/']").count()
                    if cnt == last or cnt >= TOPN:
                        break
                    last = cnt
                items = pg.locator("div[role='feed'] a[href*='/maps/place/']")
                k = 0
                for i in range(min(items.count(), TOPN)):
                    try:
                        rec = parse_card(items.nth(i), lang)
                    except Exception:
                        continue
                    if not rec["name"]:
                        continue
                    rec.update({"lang": lang, "query": q, "city": city, "industry": ind, "rank": i + 1, "at": time.strftime("%Y-%m-%d %H:%M")})
                    append_jsonl(OUT, rec)
                    k += 1
                done.add(f"{lang}|{q}")
                json.dump(sorted(done), open(DONE, "w"), ensure_ascii=False)
                print(f"[inb_frame] {n}/{len(todo)} [{lang}] {q}: {k}店 {round(time.time() - t0, 1)}s", flush=True)
            except Blocked:
                raise SystemExit(2)
            except Exception as e:
                print(f"[inb_frame] 失敗 [{lang}] {q}: {str(e)[:80]}", flush=True)
            nap()
        b.close()


if __name__ == "__main__":
    lim = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    run(lim)
