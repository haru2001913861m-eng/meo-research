# -*- coding: utf-8 -*-
"""店ごとの詳細を読む（調査A・B・D・E・Gの材料）。実行: python3 detail.py [--workers 3] [--limit N] [--industry カフェ]
入力: data/frame.jsonl   出力: data/detail.jsonl（cid 単位で再開可）
標本調査（13業種×10都市）: FRAME_OUT=ind_frame.jsonl DETAIL_OUT=ind_detail.jsonl DETAIL_REDO=1 DETAIL_MAX_RANK=20 python3 detail.py --workers 2
  （DETAIL_REDO=1 で既存 detail_*.jsonl の済みを無視＝整体と接骨院のように重なる店も新業種として取り直す）
読むもの（公開画面・ログインなし）:
  website / phone / hours_days（曜日の数）/ hours_break（休憩あり）/ special_hours（祝日の「時間変更の可能性」表示）
  photos（写真枚数）/ has_posts（最新情報）/ has_menu / unclaimed（オーナー未確認）/ editorial（紹介文）
  口コミ: 最新最大20件の「何日前」→ 月あたり口コミ数 / オーナー返信の数と返信までの日数 / ローカルガイドの比率 /
         本文の分類フラグの件数（品名・人・行き方）※本文は保存しない
"""
from __future__ import annotations
import json, os, re, sys, time
from concurrent.futures import ThreadPoolExecutor
from common import DATA, Blocked, accept_consent, append_jsonl, blocked, browser, nap, on_block, read_jsonl, rel_days, sync_playwright

FRAME = os.path.join(DATA, os.getenv("FRAME_OUT", "frame.jsonl"))
OUT = os.path.join(DATA, os.getenv("DETAIL_OUT", "detail.jsonl"))
COOLDOWN = int(os.getenv("DETAIL_COOLDOWN", "1800"))   # 制限表示が出たら全員で休む秒数
PAUSE = {"until": 0.0, "hits": 0}


class Limited(Exception):
    pass


KW_ITEM = re.compile(r"美味|おいし|うま|食べ|飲|ケーキ|コーヒー|珈琲|ラーメン|麺|スープ|餃子|ビール|刺身|焼|カット|カラー|パーマ|トリートメント|施術|マッサージ|整体|矯正|メニュー|ランチ|セット|デザート|パン")
KW_PEOPLE = re.compile(r"店員|スタッフ|店主|マスター|オーナー|先生|さんが|さんの|対応|接客|親切|丁寧|優しい|笑顔|説明")
KW_ACCESS = re.compile(r"階段|分かりにく|わかりにく|迷|場所が|駐車|駅から|入口|入り口|看板")


def read_reviews(pg) -> dict:
    out = {"rv_n": 0, "rv_days": [], "rv_replies": 0, "rv_reply_lag": [], "rv_localguide": 0,
           "rv_item": 0, "rv_people": 0, "rv_access": 0, "rv_reply_len": [], "rv_reply_dup": 0}
    tab = pg.locator("button[role='tab']", has_text="クチコミ")
    if not tab.count():
        return out
    tab.first.click(timeout=5000)
    time.sleep(1.5)
    # 口コミの並びを「新しい順」にできれば
    try:
        srt = pg.locator("button", has_text="並べ替え")
        if srt.count():
            srt.first.click(timeout=3000); time.sleep(0.6)
            new = pg.locator("[role='menuitemradio']", has_text="新しい順")
            if new.count():
                new.first.click(timeout=3000); time.sleep(1.2)
    except Exception:
        pass
    def _unique_cards():
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
            if "前" not in t and "今日" not in t:
                continue
            seen.add(rid)
            res.append(t)
        return res
    texts = _unique_cards()
    for _ in range(8):
        if len(texts) >= 20:
            break
        try:
            pg.locator("[data-review-id]").last.scroll_into_view_if_needed(timeout=3000)
        except Exception:
            pg.mouse.wheel(0, 4000)
        time.sleep(1.0)
        texts = _unique_cards()
    texts = texts[:20]
    out["rv_n"] = len(texts)
    replies = []
    for t in texts:
        m = re.search(r"(\d+\s*(?:日|週間|か月|カ月|ヶ月|年)前|昨日|今日)", t)
        d = rel_days(m.group(1)) if m else None
        if d is not None:
            out["rv_days"].append(d)
        if "ローカルガイド" in t:
            out["rv_localguide"] += 1
        body = t.split("オーナーからの返信")[0]
        if KW_ITEM.search(body): out["rv_item"] += 1
        if KW_PEOPLE.search(body): out["rv_people"] += 1
        if KW_ACCESS.search(body): out["rv_access"] += 1
        if "オーナーからの返信" in t:
            out["rv_replies"] += 1
            rep = t.split("オーナーからの返信", 1)[1]
            m2 = re.search(r"(\d+\s*(?:日|週間|か月|カ月|ヶ月|年)前|昨日|今日)", rep)
            d2 = rel_days(m2.group(1)) if m2 else None
            if d is not None and d2 is not None:
                out["rv_reply_lag"].append(max(0, d - d2))
            rep_body = re.sub(r"\d+\s*(?:日|週間|か月|カ月|ヶ月|年)前|昨日|今日", "", rep).strip()
            out["rv_reply_len"].append(len(rep_body))
            replies.append(rep_body[:80])
    if replies:
        out["rv_reply_dup"] = len(replies) - len(set(replies))
    return out


def read_store(pg, href: str) -> dict:
    pg.goto(href if "hl=" in href else href + ("&" if "?" in href else "?") + "hl=ja", wait_until="domcontentloaded", timeout=40000)
    accept_consent(pg)
    if blocked(pg):
        on_block(pg, "detail")
        raise RuntimeError("blocked")
    pg.wait_for_selector("h1", timeout=20000)
    time.sleep(1.2)
    body = pg.locator("body").inner_text()
    if "表示が制限されています" in body or "機能を絞った" in body:   # 10/12 実測: ログインなしだと口コミ5件・タブなしの表示になる
        raise Limited()
    rec = {"name": pg.locator("h1").first.inner_text()[:80]}
    rec["website"] = bool(re.search(r"\n[\w.-]+\.(jp|com|net|co\.jp|info|biz|shop|tokyo|me)\b", body)) or "ウェブサイト" in body
    rec["phone"] = bool(re.search(r"0\d{1,4}-\d{1,4}-\d{3,4}", body))
    rec["unclaimed"] = "このビジネスのオーナーですか" in body
    rec["has_posts"] = "最新情報" in body
    rec["has_menu"] = pg.locator("button[role='tab']", has_text="メニュー").count() > 0
    m = re.search(r"写真\s*([\d,]+)\s*枚", body) or re.search(r"([\d,]+)\s*枚の写真", body)
    rec["photos"] = int(m.group(1).replace(",", "")) if m else None
    rec["reserve"] = bool(re.search(r"予約|オンラインで注文", body))
    rec["recent_open"] = ("最近オープン" in body) or ("新規オープン" in body)
    head = body.split("ルート・乗換")[0]
    rec["editorial"] = bool(re.search(r"\n[^\n·]{15,80}\n", head))
    rec["hours_days"] = None; rec["hours_break"] = None; rec["special_hours"] = None
    try:
        h = pg.locator("[aria-label*='営業時間']").first
        h.click(timeout=3000); time.sleep(0.8)
        tbl = pg.locator("table").first.inner_text() if pg.locator("table").count() else ""
        rec["hours_days"] = len(set(re.findall(r"(月|火|水|木|金|土|日)曜日", tbl)))
        rec["hours_break"] = bool(re.search(r"\d{1,2}時\d{2}分～\d{1,2}時\d{2}分,\s*\d{1,2}時", tbl))
        rec["special_hours"] = ("時間変更の可能性" in tbl) or ("祝日" in tbl)
        rec["closed_days"] = tbl.count("定休日")
    except Exception:
        pass
    rec.update(read_reviews(pg))
    return rec


def worker(rows: list[dict], wid: int) -> int:
    done = 0
    base = os.getenv("GMAPS_PROFILE_BASE")   # 例 ~/meo-research/.gprofile_wsample → 並列ごとに _w0, _w1 を使う（ログイン済みのコピー）
    prof = os.path.expanduser(f"{base}_w{wid}") if base else None
    with sync_playwright() as p:
        b, ctx = browser(p, profile=prof)
        pg = ctx.new_page()
        try:   # 最初の1ページ目が読めない現象の対策（ウォームアップ）
            pg.goto("https://www.google.com/maps?hl=ja", wait_until="domcontentloaded", timeout=30000)
            time.sleep(2.0)
        except Exception:
            pass
        k, queue = 0, list(rows)
        while queue:
            r = queue[0]; k += 1
            if time.time() < PAUSE["until"]:
                time.sleep(PAUSE["until"] - time.time() + 5)
                k = 0
            t0 = time.time()
            if k % 60 == 0:   # メモリ対策: 60店ごとにブラウザを作り直す（休んだ後も）
                try:
                    b.close()
                except Exception:
                    pass
                b, ctx = browser(p, profile=prof)
                pg = ctx.new_page()
            try:
                rec = read_store(pg, r["href"])
                if rec["rv_n"] == 0 and (r.get("reviews") or 0) > 0:
                    time.sleep(2.0)
                    rec = read_store(pg, r["href"])
                rec.update({"cid": r["cid"], "query": r["query"], "industry": r["industry"], "city": r["city"], "rank": r["rank"],
                            "list_rating": r["rating"], "list_reviews": r["reviews"], "list_category": r["category"],
                            "at": time.strftime("%Y-%m-%d %H:%M"), "sec": round(time.time() - t0, 1)})
                append_jsonl(OUT, rec)
                done += 1; queue.pop(0)
                print(f"[detail{wid}] {r['industry']} {r['city']} #{r['rank']} {rec['name'][:16]} rv{rec['rv_n']} {rec['sec']}s", flush=True)
            except Blocked:
                raise SystemExit(2)
            except Limited:
                if time.time() >= PAUSE["until"]:
                    PAUSE["until"] = time.time() + COOLDOWN; PAUSE["hits"] += 1
                    print(f"[detail{wid}] 制限表示 → {COOLDOWN // 60}分休む（{PAUSE['hits']}回目・ここまで {done} 店）", flush=True)
                continue
            except RuntimeError:
                queue.pop(0)
                print(f"[detail{wid}] ブロック後の再試行待ち", flush=True)
            except Exception as e:
                queue.pop(0)
                append_jsonl(OUT, {"cid": r["cid"], "error": str(e)[:80], "query": r["query"], "industry": r["industry"], "city": r["city"], "rank": r["rank"]})
                print(f"[detail{wid}] 失敗 {r['name'][:16]}: {str(e)[:60]}", flush=True)
            nap()
        b.close()
    return done


def main():
    args = sys.argv
    workers = int(args[args.index("--workers") + 1]) if "--workers" in args else 3
    limit = int(args[args.index("--limit") + 1]) if "--limit" in args else None
    ind = args[args.index("--industry") + 1] if "--industry" in args else None
    shard = args[args.index("--shard") + 1] if "--shard" in args else None   # 例 "2/4"
    max_reviews = int(os.getenv("DETAIL_MAX_REVIEWS", "0") or 0)             # 例 40 → 口コミ40件以下の店だけ（開業直後の候補）
    redo = os.getenv("DETAIL_REDO", "") == "1"                                # 1 → 他の detail_*.jsonl の済みを無視（自分の出力だけ再開に使う）
    max_rank = int(os.getenv("DETAIL_MAX_RANK", "0") or 0)                   # 例 20 → 一覧の上位20位まで（標本調査）
    done_ids = {r["cid"] for r in read_jsonl(OUT) if r.get("cid") and not r.get("error")}   # 自分の出力（detail で始まらない名前でも再開できる）
    for fn in os.listdir(DATA):
        if fn.startswith("detail") and fn.endswith(".jsonl"):
            if redo and fn != os.path.basename(OUT):
                continue
            done_ids |= {r["cid"] for r in read_jsonl(os.path.join(DATA, fn)) if r.get("cid")}
    frame = [r for r in read_jsonl(FRAME) if r.get("cid") and r["cid"] not in done_ids and (not ind or r["industry"] == ind)
             and (not max_reviews or (r.get("reviews") or 0) <= max_reviews) and (not max_rank or (r.get("rank") or 999) <= max_rank)]
    seen = set(); todo = []
    for r in frame:
        if r["cid"] in seen:
            continue
        seen.add(r["cid"]); todo.append(r)
    if shard:
        i, n = (int(x) for x in shard.split("/"))
        todo = [r for k, r in enumerate(todo) if k % n == i]
    if limit:
        todo = todo[:limit]
    print(f"[detail] 対象 {len(todo)} 店（済 {len(done_ids)}）workers={workers}", flush=True)
    chunks = [todo[i::workers] for i in range(workers)]
    with ThreadPoolExecutor(max_workers=workers) as ex:
        total = sum(ex.map(lambda a: worker(*a), [(c, i) for i, c in enumerate(chunks)]))
    print(f"[detail] 完了 {total} 店", flush=True)


if __name__ == "__main__":
    main()
