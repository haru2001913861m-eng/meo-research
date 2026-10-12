#!/usr/bin/env python3
# 上位10%の物差し（2026-10-12）: 同じ都市×業種の一覧の先頭1割の中央値（口コミ件数・月あたり・返信率・星）
# 出力: ~/sales-automation/data/meo_top10_yardstick.json  {"by_city": {"札幌市中央区|カフェ": {...}}, "by_industry": {"カフェ": {...}}, "all": {...}}
import json, glob, math, statistics as st, collections, os
rows = {}
for f in sorted(glob.glob(os.path.join(os.path.dirname(__file__), "data", "detail_*.jsonl"))):
    for line in open(f):
        try: d = json.loads(line)
        except Exception: continue
        if d.get("cid") and d.get("rank") is not None: rows[(d["cid"], d.get("query"))] = d
rows = list(rows.values())
def vel(d):
    days = d.get("rv_days") or []; n = d.get("rv_n") or 0
    return n / max(max(days) if days else 1, 1) * 30 if n else 0.0
def rr(d):
    n = d.get("rv_n") or 0; return (d.get("rv_replies") or 0) / n if n else 0.0
def summary(lst):
    return {"n": len(lst), "reviews": round(st.median([d.get("list_reviews") or 0 for d in lst])),
            "per_month": round(st.median([vel(d) for d in lst]), 1), "reply_rate": round(sum(rr(d) for d in lst) / len(lst), 2),
            "star": round(st.median([d.get("list_rating") or 0 for d in lst]), 1)}
groups = collections.defaultdict(list)
for d in rows: groups[(d["city"], d["industry"])].append(d)
out = {"by_city": {}, "by_industry": {}, "all": {}, "made": "2026-10-12", "source": "全国14,504店（同じ都市×業種の一覧の先頭1割・中央値）"}
top_all, top_ind = [], collections.defaultdict(list)
for (city, ind), lst in groups.items():
    if len(lst) < 10: continue
    lst.sort(key=lambda d: d["rank"]); k = max(1, math.ceil(len(lst) * 0.1)); top = lst[:k]
    out["by_city"][f"{city}|{ind}"] = summary(top); top_all += top; top_ind[ind] += top
for ind, lst in top_ind.items(): out["by_industry"][ind] = summary(lst)
out["all"] = summary(top_all)
path = os.path.expanduser("~/sales-automation/data/meo_top10_yardstick.json")
json.dump(out, open(path, "w"), ensure_ascii=False, indent=0)
print(path, len(out["by_city"]), "組", out["by_industry"])
