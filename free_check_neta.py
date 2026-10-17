# -*- coding: utf-8 -*-
"""無料点検で ChatGPT に実際に聞いた結果を、毎週ネタ帳（Threads の「AI」の日の材料）に書く（会長 2026-10-17「無料点検のネタにしていい」）.

元: data/en_rank_log.jsonl の kind=screens（en_rank_watch.py が無料点検ごとに1行）。店名は書かない（数と出典のサイトだけ）。
書く場所: Vault「ToB発信ネタ帳_MEO.md」の「#### B-18 無料点検で ChatGPT に聞いた結果」→ tob_neta が「無料点検のAI」のシリーズにする
（AI の重点の日に「AIに4言語」と一緒に出る）。5店未満の週は書かない（少なすぎる数は言い切りに使わない）。
本番へ: 新しい ID だけ tob_neta_import.py --write --new-only。実行: python3 free_check_neta.py [--import] [--days 7]
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "data", "en_rank_log.jsonl")
NETA = os.path.expanduser("~/Documents/Obsidian Vault/✍️ 思考・下書き/ToB発信ネタ帳_MEO.md")
HEAD = "#### B-18 無料点検で ChatGPT に聞いた結果（自社・LINE の無料点検ごとに日本語と英語で1回ずつ・毎週）"
CITE = "en_rank_log.jsonl（meo-research・無料点検）"
MIN_SHOPS = 5
SITE = {"tabelog.com": "食べログ", "beauty.hotpepper.jp": "ホットペッパービューティー", "hotpepper.jp": "ホットペッパー", "retty.me": "Retty",
        "instagram.com": "Instagram", "tripadvisor.com": "Tripadvisor", "tripadvisor.jp": "トリップアドバイザー"}


def rows(days: int) -> list[dict]:
    since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    out = []
    if not os.path.exists(LOG):
        return out
    for l in open(LOG, encoding="utf-8"):
        try:
            r = json.loads(l)
        except Exception:
            continue
        res = r.get("res") or {}
        if (r.get("req") or {}).get("kind") == "screens" and res.get("ok") and (res.get("ai") or {}).get("ok") and (res.get("at") or "") >= since:
            out.append(res)
    return out


def facts(days: int = 7) -> list[tuple[str, str]]:
    rs = sorted(rows(days), key=lambda r: r.get("at", ""))
    if len(rs) < MIN_SHOPS:
        return []
    a, b = rs[0]["at"][:10], rs[-1]["at"][:10]
    period = f"{int(a[5:7])}/{int(a[8:10])}〜{int(b[5:7])}/{int(b[8:10])}"
    n = len(rs)
    hit = sum(1 for r in rs if r["ai"].get("hit"))
    ja = sum(1 for r in rs if (r["ai"].get("by_lang") or {}).get("ja", {}).get("hit"))
    en = sum(1 for r in rs if (r["ai"].get("by_lang") or {}).get("en", {}).get("hit"))
    out = [(f"LINEの無料点検で{period}に点検した{n}店を、ChatGPTに日本語と英語で「その町のおすすめ」と聞くと、答えに出たのは{hit}店。日本語で出たのは{ja}店、英語では{en}店だった",
            f"{n}店／{hit}店／日本語{ja}店／英語{en}店")]
    src = Counter()
    for r in rs:
        for d, c in r["ai"].get("sources") or []:
            src[re.sub(r"^(www\.|s\.|m\.)", "", d)] += c
    g = sum(c for d, c in src.items() if "google." in d)
    named = [(SITE[d], c) for d, c in src.most_common() if d in SITE][:3]
    if named:
        out.append((f"その{n}店を聞いた ChatGPT の答えの出典で多かった口コミ・予約サイトは、" + "・".join(f"{s} {c}回" for s, c in named) + f"。Googleマップは{g}回だった",
                    "／".join(f"{s}{c}" for s, c in named) + f"／Google{g}"))
    top = [r for r in rs if (r.get("rank_ja") or 99) <= 10]
    low = [r for r in rs if (r.get("rank_ja") or 99) > 10]
    if len(top) >= 2 and len(low) >= 2:
        th, lh = sum(1 for r in top if r["ai"].get("hit")), sum(1 for r in low if r["ai"].get("hit"))
        out.append((f"その{n}店のうち、日本語の地図で上位10の店は{len(top)}店中{th}店が ChatGPT に出た。11位以下の店は{len(low)}店中{lh}店",
                    f"{len(top)}店中{th}店／{len(low)}店中{lh}店"))
    lost = [r for r in rs if r.get("rank_ja") and r["rank_ja"] <= 20 and (not r.get("rank_en") or r["rank_en"] > 10)]
    if lost:
        out.append((f"その{n}店のうち、日本語の地図で20位以内なのに、英語の地図では上位10に入っていない店が{len(lost)}店あった", f"{n}店中{len(lost)}店"))
    return out


def write(import_: bool = False, days: int = 7) -> list[str]:
    fs = facts(days)
    if not fs:
        print(f"[free_check_neta] {days}日で{MIN_SHOPS}店未満。書かない"); return []
    md = open(NETA, encoding="utf-8").read()
    nxt = max(int(x) for x in re.findall(r"\*\*N(\d{3,})\*\*", md)) + 1
    known = set(re.findall(r"^- \*\*N\d+\*\* \[B\] (.+?) ｜", md, re.M))
    new_lines, new_ids = [], []
    for fact, nums in fs:
        if fact in known:
            continue
        nid = f"N{nxt:03d}"; nxt += 1
        new_lines.append(f"- **{nid}** [B] {fact} ｜ {nums} ｜ {CITE}")
        new_ids.append(nid)
    if not new_lines:
        print("[free_check_neta] 新しい事実なし"); return []
    if HEAD in md:
        i = md.index(HEAD) + len(HEAD)
        ends = [x for x in (md.find("\n### ", i), md.find("\n#### ", i)) if x != -1]
        end = min(ends) if ends else len(md)
        md = md[:end].rstrip("\n") + "\n" + "\n".join(new_lines) + "\n" + md[end:]
    else:
        anchor = md.index("#### B-16")
        md = md[:anchor] + HEAD + "\n" + "\n".join(new_lines) + "\n\n" + md[anchor:]
    open(NETA, "w", encoding="utf-8").write(md)
    print("\n".join(new_lines))
    if import_:
        r = subprocess.run([sys.executable, "scripts/tob_neta_import.py", "--write", "--new-only", "--ids", ",".join(new_ids)],
                           cwd=os.path.expanduser("~/sales-automation-outreach"), capture_output=True, text=True)
        print(r.stdout[-600:], r.stderr[-300:])
    return new_ids


if __name__ == "__main__":
    write("--import" in sys.argv, int(sys.argv[sys.argv.index("--days") + 1]) if "--days" in sys.argv else 7)
