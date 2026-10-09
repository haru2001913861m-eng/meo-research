# -*- coding: utf-8 -*-
"""集計: 7つの調査（A〜G）を業種別・順位帯別の中央値で出す。実行: python3 analyze.py > 結果.md
すべて「ある時点で数えた相関」。順位・売上・来店は約束しない（本文の注記は固定で出す）。"""
from __future__ import annotations
import os, re, statistics as st
from collections import defaultdict
from common import DATA, read_jsonl

FRAME = os.path.join(DATA, "frame.jsonl")
DETAIL = os.path.join(DATA, "detail.jsonl")
PLACE_WORDS = ("駅", "本店", "店", "区", "市", "町", "通り", "前")
HYPE_WORDS = ("人気", "No.1", "No1", "NO.1", "おすすめ", "安い", "激安", "口コミ", "評判", "名店", "有名", "最高", "格安", "予約")


def med(xs):
    xs = [x for x in xs if x is not None]
    return round(st.median(xs), 1) if xs else None


def pace_per_month(days: list[int]) -> float | None:
    """最新n件が何日で埋まったか → 月あたり件数（n/日数×30）。日付が2件未満なら None。"""
    d = sorted(x for x in days if x is not None)
    if len(d) < 2:
        return None
    span = max(d[-1], 1)
    return round(len(d) / span * 30, 2)


def name_stuffing(name: str, city: str, category: str | None) -> dict:
    n = name or ""
    core_city = re.sub(r"(市|区|町|村).*$", "", city)
    has_place = bool(core_city and core_city in n) or any(w in n for w in ("駅前", "駅", "通り", "本店"))
    cat_words = ("カフェ", "喫茶", "珈琲", "コーヒー", "美容室", "美容院", "ヘア", "整体", "整骨", "鍼灸", "マッサージ", "ラーメン", "らーめん", "居酒屋", "酒場")
    has_cat = any(w in n for w in cat_words)
    has_hype = any(w in n for w in HYPE_WORDS)
    sep = bool(re.search(r"[｜|/／【】\[\]（）()〜~・]", n)) and len(n) >= 12
    return {"place": has_place, "cat": has_cat, "hype": has_hype, "long": len(n) >= 15, "sep": sep}


def table(title: str, rows: list[tuple], header: tuple) -> str:
    out = [f"\n### {title}", "| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    for r in rows:
        out.append("| " + " | ".join("" if v is None else str(v) for v in r) + " |")
    return "\n".join(out)


def main():
    frame = [r for r in read_jsonl(FRAME) if r.get("cid")]
    detail = {}
    for fn in sorted(os.listdir(DATA)):
        if fn.startswith("detail") and fn.endswith(".jsonl"):
            for r in read_jsonl(os.path.join(DATA, fn)):
                if r.get("cid") and not r.get("error"):
                    detail[r["cid"]] = r
    uniq = {}
    for r in frame:
        uniq.setdefault(r["cid"], r)
    print(f"# 全国調査 結果（母集団 {len(uniq)}店／詳細 {len(detail)}店／取得 {frame[0]['at'][:10] if frame else ''}〜）")
    print("\n※すべて「ある時点で数えた相関」です。順位（一覧での位置）はその検索・その時点のもので、場所で変わります。順位・売上・来店は約束しません。")
    inds = sorted({r["industry"] for r in uniq.values()})

    # ── F: 店名の盛り方（母集団全体で可能）
    rows = []
    for ind in inds + ["全業種"]:
        rs = [r for r in uniq.values() if ind == "全業種" or r["industry"] == ind]
        if not rs:
            continue
        flags = [name_stuffing(r["name"], r["city"], r["category"]) for r in rs]
        def grp(key):
            a = [r for r, f in zip(rs, flags) if f[key]]
            b = [r for r, f in zip(rs, flags) if not f[key]]
            return len(a), med([r["rating"] for r in a]), med([r["reviews"] for r in a]), med([r["rank"] for r in a]), \
                   len(b), med([r["rating"] for r in b]), med([r["reviews"] for r in b]), med([r["rank"] for r in b])
        for key, lab in (("place", "地名・駅名入り"), ("cat", "業種語入り"), ("hype", "売り文句入り"), ("long", "15字以上")):
            g = grp(key)
            rows.append((ind, lab, f"{g[0]}店", g[1], g[2], g[3], f"{g[4]}店", g[5], g[6], g[7]))
    print(table("F. 店名の「盛り方」× 星・口コミ件数・一覧の位置（中央値）", rows,
                ("業種", "店名の特徴", "該当", "星", "口コミ", "位置", "非該当", "星", "口コミ", "位置")))

    if not detail:
        print("\n（詳細データ未取得のため A〜E・G は未集計）")
        return
    D = []
    for cid, d in detail.items():
        f = uniq.get(cid, {})
        d = dict(d)
        d["pace"] = pace_per_month(d.get("rv_days", []))
        d["reviews"] = f.get("reviews") or d.get("list_reviews")
        d["rating"] = f.get("rating") or d.get("list_rating")
        d["rank"] = f.get("rank") or d.get("rank")
        d["care"] = sum(1 for k in ("website", "phone", "has_posts", "has_menu", "reserve", "editorial") if d.get(k)) + (1 if (d.get("photos") or 0) >= 10 else 0)
        D.append(d)

    def split(key_fn, labels):
        out = []
        for ind in inds + ["全業種"]:
            rs = [d for d in D if ind == "全業種" or d["industry"] == ind]
            for lab, pred in labels:
                g = [d for d in rs if pred(d)]
                out.append((ind, lab, f"{len(g)}店", med([d["pace"] for d in g]), med([d["reviews"] for d in g]), med([d["rating"] for d in g]), med([d["rank"] for d in g])))
        return out

    hdr = ("業種", "区分", "店数", "月あたり口コミ", "口コミ件数", "星", "一覧の位置")
    # A: 投稿
    print(table("A. 投稿（最新情報）の有無 × 口コミ・位置（中央値）", split(None, [("投稿あり", lambda d: d.get("has_posts")), ("投稿なし", lambda d: not d.get("has_posts"))]), hdr))
    # B: 手入れの数
    print(table("B. 手入れの数（サイト・電話・投稿・メニュー・予約・紹介文・写真10枚以上）× 口コミ", split(None, [
        ("0〜2個", lambda d: d["care"] <= 2), ("3〜4個", lambda d: 3 <= d["care"] <= 4), ("5個以上", lambda d: d["care"] >= 5)]), hdr))
    # C: 口コミの速度と星
    print(table("C. 口コミの速度（月あたり）× 星（速度で分けたときの星の中央値）", split(None, [
        ("月1件未満", lambda d: d["pace"] is not None and d["pace"] < 1), ("月1〜5件", lambda d: d["pace"] is not None and 1 <= d["pace"] < 5),
        ("月5件以上", lambda d: d["pace"] is not None and d["pace"] >= 5)]), hdr))
    # D: 口コミの中身
    rows = []
    for ind in inds + ["全業種"]:
        rs = [d for d in D if (ind == "全業種" or d["industry"] == ind) and d.get("rv_n")]
        fast = [d for d in rs if d["pace"] is not None and d["pace"] >= 3]
        slow = [d for d in rs if d["pace"] is not None and d["pace"] < 1]
        def share(g, k):
            tot = sum(d["rv_n"] for d in g)
            return round(100 * sum(d[k] for d in g) / tot, 1) if tot else None
        rows.append((ind, f"速い店（月3件以上）{len(fast)}店", share(fast, "rv_item"), share(fast, "rv_people"), share(fast, "rv_access"), share(fast, "rv_localguide")))
        rows.append((ind, f"遅い店（月1件未満）{len(slow)}店", share(slow, "rv_item"), share(slow, "rv_people"), share(slow, "rv_access"), share(slow, "rv_localguide")))
    print(table("D. 口コミの中身（最新20件に占める％）", rows, ("業種", "区分", "品名・味", "人・接客", "行き方", "ローカルガイド")))
    # E: 返信の速さと書き方
    rows = []
    for ind in inds + ["全業種"]:
        rs = [d for d in D if (ind == "全業種" or d["industry"] == ind) and d.get("rv_n")]
        rep = [d for d in rs if d["rv_replies"] > 0]
        norep = [d for d in rs if d["rv_replies"] == 0]
        fast = [d for d in rep if d["rv_reply_lag"] and st.median(d["rv_reply_lag"]) <= 7]
        slow = [d for d in rep if d["rv_reply_lag"] and st.median(d["rv_reply_lag"]) > 30]
        dup = [d for d in rep if d["rv_reply_dup"] > 0]
        longr = [d for d in rep if d["rv_reply_len"] and st.median(d["rv_reply_len"]) >= 80]
        for lab, g in (("返信あり", rep), ("返信なし", norep), ("返信が7日以内", fast), ("返信が30日超", slow), ("定型文（同文あり）", dup), ("返信80字以上", longr)):
            rows.append((ind, lab, f"{len(g)}店", med([d["pace"] for d in g]), med([d["reviews"] for d in g]), med([d["rating"] for d in g]), med([d["rank"] for d in g])))
    print(table("E. 口コミ返信の「速さ」「書き方」× 口コミの速度（中央値）", rows, hdr))
    # G: 営業時間の細かさ
    print(table("G. 営業時間の設定 × 口コミ（中央値）", split(None, [
        ("7曜日すべて設定", lambda d: d.get("hours_days") == 7), ("曜日が欠けている", lambda d: d.get("hours_days") is not None and 0 < d["hours_days"] < 7),
        ("祝日の特別営業時間あり", lambda d: d.get("special_hours")), ("祝日の設定なし", lambda d: d.get("special_hours") is False),
        ("休憩時間あり", lambda d: d.get("hours_break")), ("オーナー未確認", lambda d: d.get("unclaimed"))]), hdr))


if __name__ == "__main__":
    main()
