# -*- coding: utf-8 -*-
"""都市×業種の実測（答えのページ /guide/city 用・2026-10-27 会長「AI検索に引っかかる工夫」）。
全国調査の詳細（data/detail_*.jsonl・同じ店は cid で1つ）を「市区×業種」で集計し、
sales-automation/data/aio_city.json に書く（ページの数字はこのファイルだけから引く＝手で書かない）。
15店未満の組は出さない。数字は中央値・割合。原因と結果ではなく相関。
"""
from __future__ import annotations
import glob, json, os, statistics as st
from collections import defaultdict
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.expanduser("~/sales-automation/data/aio_city.json")
MIN_N = 15


def load() -> list[dict]:
    by = {}
    for p in sorted(glob.glob(os.path.join(HERE, "data", "detail_[0-9].jsonl"))) + sorted(glob.glob(os.path.join(HERE, "data", "detail_new_*.jsonl"))):
        for l in open(p, encoding="utf-8"):
            try:
                d = json.loads(l)
            except ValueError:
                continue
            if d.get("error") or not d.get("city") or not d.get("industry") or not d.get("cid"):
                continue
            by[(d["cid"], d["city"], d["industry"])] = d
    return list(by.values())


def med(xs):
    xs = [x for x in xs if isinstance(x, (int, float))]
    return round(st.median(xs), 1) if xs else None


def share(rows, f):
    rs = [r for r in rows if f(r) is not None]
    return round(100 * sum(1 for r in rs if f(r)) / len(rs)) if rs else None


def build() -> dict:
    g = defaultdict(list)
    for r in load():
        g[(r["city"], r["industry"])].append(r)
    out = []
    for (city, ind), rows in sorted(g.items()):
        if len(rows) < MIN_N:
            continue
        top = [r for r in rows if isinstance(r.get("rank"), int) and r["rank"] <= 10]
        low = [r for r in rows if isinstance(r.get("rank"), int) and r["rank"] > 10]
        rep = lambda r: (r.get("rv_replies") or 0) > 0 if r.get("rv_n") else None
        out.append({"city": city, "ind": ind, "n": len(rows),
                    "top_reviews": med([r.get("list_reviews") for r in top]), "low_reviews": med([r.get("list_reviews") for r in low]),
                    "top_photos": med([r.get("photos") for r in top]), "low_photos": med([r.get("photos") for r in low]),
                    "top_reply": share(top, rep), "low_reply": share(low, rep),
                    "post_share": share(rows, lambda r: bool(r.get("has_posts"))),
                    "reply_share": share(rows, rep)})
    return {"built": date.today().isoformat(), "source": "meo-research/data/detail_*.jsonl（全国調査・cid で重複除き）→ aio_city_build.py",
            "note": "上位10＝その検索の一覧で1〜10番目。中央値。15店未満の組は出さない", "rows": out}


if __name__ == "__main__":
    d = build()
    json.dump(d, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print(len(d["rows"]), "組", OUT)
    print(d["rows"][0])
