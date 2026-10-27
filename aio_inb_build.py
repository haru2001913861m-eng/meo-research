# -*- coding: utf-8 -*-
"""観光地×業種のインバウンドの実測（答えのページ /guide/inbound 用・2026-10-27 会長「インバウンドも同様に」）。
入力: data/inb_frame60.jsonl（同じ検索語を日本語と英語の Googleマップで60位まで）・data/inb_detail60.jsonl（英語の画面の店の中身）
出力: ~/sales-automation/data/aio_inbound.json（ページの数字はここだけから引く）
- ja10_lost: 日本語で上位10に入る店のうち、英語の画面では上位10に入らなかった店（同じ観光地×業種・同じ時点）
- reply_latin: 最近の口コミに英語（ローマ字）で返事を付けている店の割合
- foreign_rv: 最近の口コミ20件のうち、翻訳の表示が付いた（日本語以外で書かれた）口コミの割合の中央値
- latin_name / post_latin: 英字の店名・英語のお知らせのある店の割合
"""
from __future__ import annotations
import json, os, statistics as st
from collections import defaultdict
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.expanduser("~/sales-automation/data/aio_inbound.json")


def rd(p):
    out = []
    for l in open(os.path.join(HERE, "data", p), encoding="utf-8"):
        try:
            out.append(json.loads(l))
        except ValueError:
            pass
    return out


def pct(xs):
    xs = [x for x in xs if x is not None]
    return round(100 * sum(1 for x in xs if x) / len(xs)) if xs else None


def build() -> dict:
    top = defaultdict(lambda: {"ja": set(), "en": set()})
    for r in rd("inb_frame60.jsonl"):
        if r.get("lang") in ("ja", "en") and isinstance(r.get("rank"), int) and r["rank"] <= 10 and r.get("cid"):
            top[(r["city"], r["industry"])][r["lang"]].add(r["cid"])
    det = defaultdict(dict)
    for r in rd("inb_detail60.jsonl"):
        if r.get("cid") and not r.get("error"):
            det[(r["city"], r["industry"])][r["cid"]] = r
    rows = []
    for key in sorted(set(top) | set(det)):
        city, ind = key
        t = top.get(key, {"ja": set(), "en": set()})
        ds = list(det.get(key, {}).values())
        if len(t["ja"]) < 8 or len(ds) < 15:
            continue
        lost = len(t["ja"] - t["en"])
        fr = [(r["rv_translated"] / r["rv_n"]) for r in ds if r.get("rv_n")]
        rows.append({"city": city, "ind": ind, "n": len(ds), "ja10": len(t["ja"]), "ja10_lost": lost,
                     "reply_latin": pct([(r.get("rv_reply_latin") or 0) > 0 if r.get("rv_n") else None for r in ds]),
                     "reply_any": pct([(r.get("rv_replies") or 0) > 0 if r.get("rv_n") else None for r in ds]),
                     "foreign_rv": round(100 * st.median(fr)) if fr else None,
                     "latin_name": pct([bool(r.get("latin_name")) for r in ds]),
                     "post_latin": pct([bool(r.get("owner_post_latin")) for r in ds])})
    tot_ja = sum(r["ja10"] for r in rows)
    tot_lost = sum(r["ja10_lost"] for r in rows)
    return {"built": date.today().isoformat(), "source": "meo-research/data/inb_frame60.jsonl・inb_detail60.jsonl → aio_inb_build.py",
            "note": "日本語と英語の Googleマップで同じ検索語を60位まで。相関で、原因と結果ではない",
            "total": {"areas": len({r['city'] for r in rows}), "pairs": len(rows), "stores": sum(r["n"] for r in rows),
                      "ja10": tot_ja, "ja10_lost": tot_lost, "ja10_lost_pct": round(100 * tot_lost / tot_ja) if tot_ja else None},
            "rows": rows}


if __name__ == "__main__":
    d = build()
    json.dump(d, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print(d["total"]); print(d["rows"][0])
