# -*- coding: utf-8 -*-
"""自社の AIO の基準線（会長 2026-10-27「AI検索に引っかかる工夫」）。
店主が打つ言葉（hq businesses/meo/aio/queries.json）で ChatGPT（ウェブ検索つき）に聞き、引用された先（ドメイン）と、
ひとつなぎが出たかを数える。聞き方・値段は ai_visibility と同じ。結果 data/aio_baseline.jsonl（続きから）・要約 data/aio_baseline.md
"""
from __future__ import annotations
import json, os, random, sys
from collections import Counter
from datetime import datetime
from urllib.parse import urlparse

from ai_visibility import ask, cost, key

HERE = os.path.dirname(os.path.abspath(__file__))
Q = os.path.expanduser("~/sales-automation/data/aio_queries.json")
OUT = os.path.join(HERE, "data", "aio_baseline.jsonl")
MD = os.path.join(HERE, "data", "aio_baseline.md")
MODEL = "gpt-5-mini"
OURS = ("hitotsunagi", "ひとつなぎ", "皆川")


def pick(seed: int = 7) -> list[tuple[str, str, str]]:
    d = json.load(open(Q, encoding="utf-8"))
    out = [("共通", p["who"], q) for p in d["generic"] for q in p["q"]]
    rnd = random.Random(seed)
    for ind, ps in d["industries"].items():
        qs = [(ind, p["who"], q) for p in ps for q in p["q"]]
        out += rnd.sample(qs, 2)
    return out


def run(budget: float) -> None:
    done = set()
    if os.path.exists(OUT):
        done = {json.loads(l)["q"] for l in open(OUT, encoding="utf-8")}
    k, spent = key(), 0.0
    with open(OUT, "a", encoding="utf-8") as fp:
        for ind, who, q in pick():
            if q in done:
                continue
            if spent >= budget:
                print("予算で止めた", spent); break
            prompt = f"{q}。日本のお店の店主として知りたいです。参考になる情報源も教えてください。"
            r = ask(prompt, MODEL, k)
            usd = cost(r, MODEL); spent += usd
            doms = list(dict.fromkeys(urlparse(u).netloc.replace("www.", "") for u in r["urls"] if u))
            hit = any(w in (r["text"] + " ".join(r["urls"])) for w in OURS)
            fp.write(json.dumps({"at": datetime.now().isoformat(timespec="seconds"), "ind": ind, "who": who, "q": q,
                                 "doms": doms, "hit": hit, "usd": round(usd, 4), "text": r["text"][:1500]}, ensure_ascii=False) + "\n")
            fp.flush()
            print(ind, q, len(doms), hit, round(usd, 3), flush=True)
    summarize()


def summarize() -> None:
    rows = [json.loads(l) for l in open(OUT, encoding="utf-8")]
    c = Counter(d for r in rows for d in set(r["doms"]))
    lines = [f"# AIの答えの引用先（{len(rows)}問・ChatGPT gpt-5-mini ウェブ検索つき・{datetime.now():%Y-%m-%d}）", "",
             f"- ひとつなぎが出た問: {sum(r['hit'] for r in rows)}/{len(rows)}",
             f"- 1問あたりの引用先の数（中央値）: {sorted(len(r['doms']) for r in rows)[len(rows)//2]}", "",
             "## 引用された回数の多いドメイン（上位40）", "| ドメイン | 問の数 |", "|---|---|"]
    lines += [f"| {d} | {n} |" for d, n in c.most_common(40)]
    lines += ["", "## 問ごと", "| 業種 | 言葉 | 引用先 |", "|---|---|---|"]
    lines += [f"| {r['ind']} | {r['q']} | {'・'.join(r['doms'][:6])} |" for r in rows]
    open(MD, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("\n".join(lines[:50]))


if __name__ == "__main__":
    if sys.argv[1:] == ["--sum"]:
        summarize()
    else:
        run(float(sys.argv[1]) if sys.argv[1:] else 2.5)
