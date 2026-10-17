# -*- coding: utf-8 -*-
"""店1軒が ChatGPT（ウェブ検索つき）の答えに出るかを数える（無料点検の③AI・月額の月報で使う・会長 2026-10-17「実際に聞く版で」）。

聞き方は調査（ai_visibility.py・75回・533店）と同じ文・同じモデル。店が出たかの判定も同じ（mentioned）。
お金の上限: 1か月の合計が AI_ASK_MONTHLY_USD（既定 $15）を超えたら聞かない（{"ok": False, "why": "budget"}）。
残高切れ（insufficient_quota）も ok=False で返す → 呼び出し側は「聞かない版」（地図の上位10・口コミ・英語の手入れ）で返す。
"""
from __future__ import annotations
import json, os, re
from collections import Counter
from datetime import datetime
from urllib.parse import urlparse

from ai_visibility import PROMPT, ask, cost, key, mentioned

HERE = os.path.dirname(os.path.abspath(__file__))
SPEND = os.path.join(HERE, "data", "ai_ask_spend.json")
LOG = os.path.join(HERE, "data", "ai_ask_log.jsonl")
MODEL = os.getenv("AI_VIS_MODEL", "gpt-5-mini")
CAP = float(os.getenv("AI_ASK_MONTHLY_USD", "15"))

# 業種（日本語の検索語）→ (日本語・英語・中国語・韓国語)
IND4 = {"ラーメン": ("ラーメン店", "ramen shops", "拉面店", "라멘 가게"), "寿司": ("寿司店", "sushi restaurants", "寿司店", "스시 가게"),
        "居酒屋": ("居酒屋", "izakaya", "居酒屋", "이자카야"), "カフェ": ("カフェ", "cafes", "咖啡馆", "카페"),
        "焼肉": ("焼肉店", "yakiniku restaurants", "烤肉店", "야키니쿠 가게"), "そば": ("そば屋", "soba restaurants", "荞麦面店", "소바 가게"),
        "うどん": ("うどん屋", "udon restaurants", "乌冬面店", "우동 가게"), "天ぷら": ("天ぷら店", "tempura restaurants", "天妇罗店", "덴푸라 가게"),
        "とんかつ": ("とんかつ店", "tonkatsu restaurants", "炸猪排店", "돈카츠 가게"), "焼き鳥": ("焼き鳥店", "yakitori restaurants", "烤鸡串店", "야키토리 가게"),
        "和食": ("和食店", "Japanese restaurants", "日本料理店", "일식당"), "イタリアン": ("イタリアン", "Italian restaurants", "意大利餐厅", "이탈리안 레스토랑"),
        "中華": ("中華料理店", "Chinese restaurants", "中餐厅", "중식당"), "カレー": ("カレー店", "curry restaurants", "咖喱店", "카레 가게"),
        "バー": ("バー", "bars", "酒吧", "바"), "パン屋": ("パン屋", "bakeries", "面包店", "빵집"),
        "美容室": ("美容室", "hair salons", "美发店", "미용실"), "ネイルサロン": ("ネイルサロン", "nail salons", "美甲店", "네일숍"),
        "整体": ("整体院", "massage places", "按摩店", "마사지 가게"), "マッサージ": ("マッサージ店", "massage places", "按摩店", "마사지 가게")}
LANGS = ("ja", "en", "zh", "ko")


def ind4(industry: str) -> tuple:
    for k, v in IND4.items():
        if k in (industry or ""):
            return v
    return ("お店", "restaurants", "餐厅", "식당")


def _month() -> str:
    return datetime.now().strftime("%Y-%m")


def spent() -> float:
    try:
        return float(json.load(open(SPEND)).get(_month(), 0))
    except Exception:
        return 0.0


def _add(usd: float) -> None:
    try:
        d = json.load(open(SPEND))
    except Exception:
        d = {}
    d[_month()] = round(float(d.get(_month(), 0)) + usd, 4)
    os.makedirs(os.path.dirname(SPEND), exist_ok=True)
    json.dump(d, open(SPEND, "w"))


def domain(u: str) -> str:
    h = urlparse(u or "").netloc.lower()
    return re.sub(r"^(www\.|s\.|m\.)", "", h)


def check(name_ja: str, name_en: str, area_ja: str, city_en: str, industry: str, langs=("ja", "en"), runs: int = 1, who: str = "") -> dict:
    """戻り値 {ok, asked, hit, by_lang:{ja:{asked,hit}}, sources:[(domain,n)], usd, answers:[...]}"""
    est = 0.07 * len(langs) * runs
    if spent() + est > CAP:
        return {"ok": False, "why": "budget", "spent": spent()}
    try:
        k = key()
    except SystemExit as e:
        return {"ok": False, "why": str(e)}
    shop = {"name_list": name_ja, "name_en": name_en}
    t4 = ind4(industry)
    by, src, answers, usd = {}, Counter(), [], 0.0
    for lg in langs:
        i = LANGS.index(lg)
        city = area_ja if lg == "ja" else (city_en or area_ja)
        prompt = PROMPT[lg].format(city=city, ind=t4[0], city_en=city, ind_en=t4[1], ind_zh=t4[2], ind_ko=t4[3])
        b = by.setdefault(lg, {"asked": 0, "hit": 0})
        for _ in range(runs):
            try:
                res = ask(prompt, MODEL, k)
            except Exception as e:
                msg = str(e)
                return {"ok": False, "why": "quota" if "insufficient_quota" in msg or "429" in msg else msg[:120], "by_lang": by, "usd": usd}
            c_ = cost(res, MODEL); usd += c_; _add(c_)
            got = mentioned(res["text"], shop)
            b["asked"] += 1; b["hit"] += int(got)
            src.update(domain(u) for u in res["urls"] if u)
            answers.append({"lang": lg, "hit": got, "prompt": prompt})
            with open(LOG, "a", encoding="utf-8") as f:
                f.write(json.dumps({"at": datetime.now().isoformat(timespec="seconds"), "who": who, "lang": lg, "prompt": prompt, "hit": got,
                                    "urls": res["urls"][:10], "usd": round(c_, 4)}, ensure_ascii=False) + "\n")
    return {"ok": True, "asked": sum(v["asked"] for v in by.values()), "hit": sum(v["hit"] for v in by.values()), "by_lang": by,
            "sources": [(d, n) for d, n in src.most_common(6) if d], "usd": round(usd, 4), "answers": answers,
            "at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+09:00")}
