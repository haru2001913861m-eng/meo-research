# -*- coding: utf-8 -*-
"""インバウンド調査の集計。実行: python3 analyze_inbound.py > data/inb_result_latest.md
問い1: 英語検索の上位20と日本語検索の上位20は、どれだけ重なるか（都市×業種ごと）
問い2: 「英語だけで出る店」「日本語だけで出る店」「両方で出る店」は何が違うか（英語画面の店名・口コミ件数・口コミの言語・返信・写真・投稿・紹介文）
すべて「ある時点で数えた相関」。順位・売上・来店は約束しない。"""
from __future__ import annotations
import glob, json, os, statistics as st
from collections import defaultdict
from common import DATA, read_jsonl

frame = read_jsonl(os.path.join(DATA, "inb_frame.jsonl"))
detail = []
for fn in sorted(glob.glob(os.path.join(DATA, "inb_detail*.jsonl"))):
    detail += [r for r in read_jsonl(fn) if r.get("cid") and not r.get("error")]


def med(xs):
    xs = [x for x in xs if x is not None]
    return round(st.median(xs), 1) if xs else None


def pct(xs):
    xs = [x for x in xs if x is not None]
    return f"{round(100 * sum(1 for x in xs if x) / len(xs))}%" if xs else "-"


print(f"# インバウンド調査 結果（検索 {len(set((r['lang'], r['query']) for r in frame))} 件／店 {len(detail)} 店／英語画面で取得）\n")
print("※ すべて「ある時点で数えた相関」。順位（一覧での位置）はその検索・その時点のもの。順位・売上・来店は約束しません。\n")

# 問い1: 重なり
pairs = defaultdict(lambda: {"ja": {}, "en": {}})
for r in frame:
    if r.get("cid"):
        pairs[(r["city"], r["industry"])][r["lang"]].setdefault(r["cid"], r["rank"])
ov_all, ov_ind = [], defaultdict(list)
for (city, ind), d in pairs.items():
    if d["ja"] and d["en"]:
        ja10 = {c for c, k in d["ja"].items() if k <= 10}; en10 = {c for c, k in d["en"].items() if k <= 10}
        o = len(ja10 & en10)
        ov_all.append(o); ov_ind[ind].append(o)
print("### 1. 日本語の上位10と英語の上位10が重なる店の数（都市×業種ごとの中央値）")
print("| 業種 | 組数 | 重なり（10店中） |\n|---|---|---|")
for ind, xs in ov_ind.items():
    print(f"| {ind} | {len(xs)} | {med(xs)} |")
print(f"| 全業種 | {len(ov_all)} | {med(ov_all)} |\n")

# 問い2: 3群の比較
groups = {"英語だけで出る": [], "日本語だけで出る": [], "両方で出る": []}
for r in detail:
    g = "両方で出る" if (r.get("in_ja") and r.get("in_en")) else ("英語だけで出る" if r.get("in_en") else "日本語だけで出る")
    groups[g].append(r)


def row(name, rs):
    n = len(rs)
    if not n:
        return f"| {name} | 0 | | | | | | | | | |"
    tr = [(r["rv_translated"] / r["rv_n"]) if r.get("rv_n") else None for r in rs]
    rp = [(r["rv_replies"] / r["rv_n"]) if r.get("rv_n") else None for r in rs]
    en_rep = [(r["rv_reply_latin"] / r["rv_replies"]) if r.get("rv_replies") else None for r in rs]
    return (f"| {name} | {n} | {pct([r.get('latin_name') for r in rs])} | {med([r.get('list_reviews') for r in rs])} | "
            f"{med([r.get('list_rating') for r in rs])} | {round(100 * (1 - st.median([x for x in tr if x is not None])))}% | "
            f"{round(100 * st.median([x for x in rp if x is not None]))}% | {pct([ (x or 0) > 0 for x in en_rep]) if any(x is not None for x in en_rep) else '-'} | "
            f"{med([r.get('photos') for r in rs])} | {pct([r.get('has_posts') for r in rs])} | {pct([r.get('editorial_latin') for r in rs])} |")


print("### 2. 「英語だけで出る店」「日本語だけで出る店」「両方で出る店」の違い（中央値・割合）")
print("| 群 | 店数 | 英語画面で英字の店名 | 口コミ件数 | 星 | 最新20件のうち英語で書かれた口コミ | 返信率 | 英語で返信している店 | 写真 | 投稿あり | 紹介文に英語 |")
print("|---|---|---|---|---|---|---|---|---|---|---|")
for g, rs in groups.items():
    print(row(g, rs))
print()

print("### 3. 業種別（英語だけで出る店 vs 日本語だけで出る店）")
print("| 業種 | 群 | 店数 | 英字の店名 | 口コミ件数 | 英語口コミの割合 | 返信率 | 写真 | 投稿あり |")
print("|---|---|---|---|---|---|---|---|---|")
by_ind = defaultdict(lambda: defaultdict(list))
for g, rs in groups.items():
    for r in rs:
        by_ind[r["industry"]][g].append(r)
for ind, gd in by_ind.items():
    for g in ("英語だけで出る", "日本語だけで出る", "両方で出る"):
        rs = gd.get(g, [])
        if not rs:
            continue
        tr = [(r["rv_translated"] / r["rv_n"]) if r.get("rv_n") else None for r in rs]
        rp = [(r["rv_replies"] / r["rv_n"]) if r.get("rv_n") else None for r in rs]
        trv = [x for x in tr if x is not None]; rpv = [x for x in rp if x is not None]
        print(f"| {ind} | {g} | {len(rs)} | {pct([r.get('latin_name') for r in rs])} | {med([r.get('list_reviews') for r in rs])} | "
              f"{round(100 * (1 - st.median(trv))) if trv else '-'}% | {round(100 * st.median(rpv)) if rpv else '-'}% | "
              f"{med([r.get('photos') for r in rs])} | {pct([r.get('has_posts') for r in rs])} |")
print()

print("### 4. About タブのフラグ（英語画面で出る語・店の割合）")
flags = defaultdict(lambda: defaultdict(int))
for g, rs in groups.items():
    for r in rs:
        for f in r.get("about_flags") or []:
            flags[f][g] += 1
print("| 語 | 英語だけで出る | 日本語だけで出る | 両方で出る |\n|---|---|---|---|")
for f, d in sorted(flags.items(), key=lambda kv: -sum(kv[1].values())):
    print(f"| {f} | " + " | ".join(f"{round(100 * d[g] / len(groups[g]))}%" if groups[g] else "-" for g in groups) + " |")
