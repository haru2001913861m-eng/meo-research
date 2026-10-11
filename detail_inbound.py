# -*- coding: utf-8 -*-
"""インバウンド調査・店ごとの詳細（英語画面 hl=en で読む）。実行: python3 detail_inbound.py [--workers 3] [--limit N] [--shard i/n]
入力: data/inb_frame.jsonl（日英どちらかの上位に入った店）   出力: data/inb_detail*.jsonl（cid 単位で再開可）
読むもの（公開画面・ログインなし・口コミ本文は保存しない）:
  name_en（英語画面での店名）/ latin_name / website / phone / photos / has_posts / has_menu / editorial（紹介文）/ unclaimed / reserve
  hours_days / rv_n（最新最大20件）/ rv_translated（Google翻訳表示＝原文が英語でない口コミの数）/ rv_replies / rv_reply_latin（英語で返した返信の数）
  rv_days（何日前）/ about_flags（About タブの決済・言語などのフラグ。英語の文言に含まれる語だけ）
"""
from __future__ import annotations
import json, os, re, sys, time
from concurrent.futures import ThreadPoolExecutor
from common import DATA, Blocked, accept_consent, append_jsonl, blocked, browser, nap, on_block, read_jsonl, sync_playwright

FRAME = os.path.join(DATA, os.getenv("INB_FRAME_OUT", "inb_frame.jsonl"))
OUT = os.path.join(DATA, os.getenv("INB_DETAIL_OUT", "inb_detail.jsonl"))
ABOUT_WORDS = ["Credit cards", "Debit cards", "NFC mobile payments", "Cash only", "Reservations required", "Accepts reservations",
               "Wi-Fi", "English", "Vegetarian", "Vegan", "Halal", "Wheelchair", "Good for tourists", "Tourists", "LGBTQ"]


def rel_days_en(s: str) -> int | None:
    m = re.search(r"(\d+|a|an)\s+(day|week|month|year)s?\s+ago", s)
    if not m:
        return None
    n = 1 if m.group(1) in ("a", "an") else int(m.group(1))
    return n * {"day": 1, "week": 7, "month": 30, "year": 365}[m.group(2)]


def read_reviews(pg) -> dict:
    out = {"rv_n": 0, "rv_days": [], "rv_translated": 0, "rv_replies": 0, "rv_reply_latin": 0, "rv_reply_translated": 0}
    tab = pg.locator("button[role='tab']", has_text="Reviews")
    if not tab.count():
        return out
    tab.first.click(timeout=5000)
    time.sleep(1.5)
    try:
        srt = pg.locator("button", has_text="Sort")
        if srt.count():
            srt.first.click(timeout=3000); time.sleep(0.6)
            new = pg.locator("[role='menuitemradio']", has_text="Newest")
            if new.count():
                new.first.click(timeout=3000); time.sleep(1.2)
    except Exception:
        pass

    def _cards():
        seen, res = set(), []
        cs = pg.locator("[data-review-id]")
        for i in range(cs.count()):
            c = cs.nth(i)
            rid = c.get_attribute("data-review-id") or str(i)
            if rid in seen:
                continue
            try:
                t = c.inner_text()
            except Exception:
                continue
            if " ago" not in t:
                continue
            seen.add(rid); res.append(t)
        return res
    texts = _cards()
    for _ in range(8):
        if len(texts) >= 20:
            break
        try:
            pg.locator("[data-review-id]").last.scroll_into_view_if_needed(timeout=3000)
        except Exception:
            pg.mouse.wheel(0, 4000)
        time.sleep(1.0)
        texts = _cards()
    texts = texts[:20]
    out["rv_n"] = len(texts)
    for t in texts:
        d = rel_days_en(t)
        if d is not None:
            out["rv_days"].append(d)
        body, _, rep = t.partition("Response from the owner")
        if "Translated by Google" in body:
            out["rv_translated"] += 1
        if rep:
            out["rv_replies"] += 1
            if "Translated by Google" in rep:
                out["rv_reply_translated"] += 1
            else:
                letters = re.findall(r"[A-Za-z]", rep); cjk = re.findall(r"[぀-ヿ一-鿿]", rep)
                if len(letters) > 20 and len(letters) > len(cjk) * 2:
                    out["rv_reply_latin"] += 1
    return out


def read_store(pg, href: str) -> dict:
    href = re.sub(r"[?&]hl=[a-z-]+", "", href)
    pg.goto(href + ("&" if "?" in href else "?") + "hl=en", wait_until="domcontentloaded", timeout=40000)
    accept_consent(pg)
    if blocked(pg):
        on_block(pg, "inb_detail")
        raise RuntimeError("blocked")
    pg.wait_for_selector("h1", timeout=20000)
    time.sleep(1.2)
    body = pg.locator("body").inner_text()
    name = pg.locator("h1").first.inner_text()[:80]
    rec = {"name_en": name, "latin_name": bool(re.search(r"[A-Za-z]{3,}", name)),
           "cjk_name": bool(re.search(r"[぀-ヿ一-鿿]", name))}
    rec["website"] = ("Website" in body) or bool(re.search(r"\n[\w.-]+\.(jp|com|net|co\.jp|info|biz|shop|tokyo|me)\b", body))
    rec["phone"] = bool(re.search(r"\+81|0\d{1,4}-\d{1,4}-\d{3,4}", body))
    rec["unclaimed"] = "Own this business" in body
    rec["has_posts"] = ("Updates" in body) or ("From the owner" in body) or ("Latest updates" in body)
    rec["has_menu"] = pg.locator("button[role='tab']", has_text="Menu").count() > 0
    ms = [int(x.replace(",", "")) for x in re.findall(r"([\d,]+)\s+[Pp]hotos", body)]
    rec["photos"] = max(ms) if ms else None   # 口コミ側の「3 photos」を拾わないよう最大値（店の総数）を取る
    rec["reserve"] = bool(re.search(r"Reserve a table|Reservations|Book online|Order online", body))
    head = body.split("Directions")[0]
    rec["editorial"] = bool(re.search(r"\n[^\n·]{15,120}\n", head))
    rec["editorial_latin"] = bool(re.search(r"\n[A-Za-z][^\n·]{14,120}\n", head))
    rec["hours_days"] = None
    try:
        h = pg.locator("[aria-label*='Hours'], [aria-label*='hours']").first
        h.click(timeout=3000); time.sleep(0.8)
        tbl = pg.locator("table").first.inner_text() if pg.locator("table").count() else ""
        rec["hours_days"] = len(set(re.findall(r"(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)", tbl)))
        rec["closed_days"] = tbl.count("Closed")
    except Exception:
        pass
    rec["about_flags"] = []
    try:
        ab = pg.locator("button[role='tab']", has_text="About")
        if ab.count():
            ab.first.click(timeout=3000); time.sleep(1.0)
            abtxt = pg.locator("body").inner_text()
            rec["about_flags"] = [w for w in ABOUT_WORDS if w in abtxt]
    except Exception:
        pass
    rec.update(read_reviews(pg))
    return rec


def worker(rows: list[dict], wid: int) -> int:
    done = 0
    with sync_playwright() as p:
        b, ctx = browser(p)
        pg = ctx.new_page()
        try:
            pg.goto("https://www.google.com/maps?hl=en", wait_until="domcontentloaded", timeout=30000)
            time.sleep(2.0)
        except Exception:
            pass
        for k, r in enumerate(rows, 1):
            t0 = time.time()
            if k % 60 == 0:
                try:
                    b.close()
                except Exception:
                    pass
                b, ctx = browser(p)
                pg = ctx.new_page()
            try:
                rec = read_store(pg, r["href"])
                if rec["rv_n"] == 0 and (r.get("reviews") or 0) > 0:   # 口コミ欄が遅れて出ることがある
                    time.sleep(2.0)
                    rec = read_store(pg, r["href"])
                rec.update({"cid": r["cid"], "industry": r["industry"], "city": r["city"], "name_list": r["name"],
                            "list_rating": r["rating"], "list_reviews": r["reviews"], "in_ja": r.get("in_ja"), "in_en": r.get("in_en"),
                            "rank_ja": r.get("rank_ja"), "rank_en": r.get("rank_en"),
                            "at": time.strftime("%Y-%m-%d %H:%M"), "sec": round(time.time() - t0, 1)})
                append_jsonl(OUT, rec)
                done += 1
                print(f"[inb{wid}] {r['industry']} {r['city']} ja{r.get('rank_ja')} en{r.get('rank_en')} {rec['name_en'][:16]} rv{rec['rv_n']} tr{rec['rv_translated']} {rec['sec']}s", flush=True)
            except Blocked:
                raise SystemExit(2)
            except RuntimeError:
                print(f"[inb{wid}] ブロック後の再試行待ち", flush=True)
            except Exception as e:
                append_jsonl(OUT, {"cid": r["cid"], "error": str(e)[:80], "industry": r["industry"], "city": r["city"]})
                print(f"[inb{wid}] 失敗 {r['name'][:16]}: {str(e)[:60]}", flush=True)
            nap()
        b.close()
    return done


def targets() -> list[dict]:
    """日英の上位から店を1つにまとめる（cid 単位）。rank_ja／rank_en／in_ja／in_en を持たせる"""
    by = {}
    for r in read_jsonl(FRAME):
        if not r.get("cid"):
            continue
        key = (r["cid"], r["city"], r["industry"])
        d = by.setdefault(key, {**r, "in_ja": False, "in_en": False, "rank_ja": None, "rank_en": None})
        if r["lang"] == "ja":
            d["in_ja"] = True; d["rank_ja"] = r["rank"] if d["rank_ja"] is None else min(d["rank_ja"], r["rank"])
        else:
            d["in_en"] = True; d["rank_en"] = r["rank"] if d["rank_en"] is None else min(d["rank_en"], r["rank"])
    out, seen = [], set()
    for (cid, _, _), d in by.items():
        if cid in seen:
            continue
        seen.add(cid); out.append(d)
    return out


def main():
    args = sys.argv
    workers = int(args[args.index("--workers") + 1]) if "--workers" in args else 3
    limit = int(args[args.index("--limit") + 1]) if "--limit" in args else None
    shard = args[args.index("--shard") + 1] if "--shard" in args else None
    done_ids = set()
    for fn in os.listdir(DATA):
        if fn.startswith("inb_detail") and fn.endswith(".jsonl"):
            done_ids |= {r["cid"] for r in read_jsonl(os.path.join(DATA, fn)) if r.get("cid")}
    todo = [r for r in targets() if r["cid"] not in done_ids]
    if shard:
        i, n = (int(x) for x in shard.split("/"))
        todo = [r for k, r in enumerate(todo) if k % n == i]
    if limit:
        todo = todo[:limit]
    print(f"[inb_detail] 対象 {len(todo)} 店（済 {len(done_ids)}）workers={workers}", flush=True)
    chunks = [todo[i::workers] for i in range(workers)]
    with ThreadPoolExecutor(max_workers=workers) as ex:
        total = sum(ex.map(lambda a: worker(*a), [(c, i) for i, c in enumerate(chunks)]))
    print(f"[inb_detail] 完了 {total} 店", flush=True)


if __name__ == "__main__":
    main()
