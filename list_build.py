# -*- coding: utf-8 -*-
"""営業リストを作る v2（会長 2026-11-01「リストに問題がある。リスト作ってと言った時の質を上げて。仕組みを変えておいて。実行まで作らないで」）.

旧 lead_harvest.py（10/14〜10/26）の問題と、この版の直し方:
  ページの「〇〇@〇〇」を全部拾った（instagram@…・example@…）       → 送る時と同じ検査 outreach_list.find_published_email（ドメイン一致・見本・営業お断り）
  紹介サイトの記事・制作会社・運営会社の1ページのアドレスを店の物にした → 「ウェブサイト」欄の種類を見分け、店のサイトの時だけメール・フォームを探す
  一覧の上から60店を全部入れた（口コミ5件の店も1,000件の店も）        → 口コミ30〜500件だけ（狙う店の設計 v2）
  チェーンは店名でしか外さなかった                                     → 店名・支店名・アドレス・サイトで外す（送る時と同じ）
  フォーム・求人・返事の割合を作る時に見なかった                       → 店のサイトで 問い合わせフォーム・求人の目印、店のページで新しい口コミ20件の返事を控える
  何が入ったか誰も見ていなかった                                       → 1回ごとに 外した理由の内訳・道（メール/フォーム/Instagram/Facebook）の数・見本10店を報告

出力: data/leads/leads.jsonl に1店1行（v=2・送る側 need_to_stock.list_pool がそのまま読む）。報告 data/leads/list_build_report_<日時>.md
実行（会長の「リスト作って」の時だけ。定期では動かさない）:
  python3 list_build.py --n 300            … 新しく入れる店の上限
  python3 list_build.py --dry --q 3        … 3検索だけ試す（書かない）
読む: ログインした Chrome プロファイル（.gprofile_harvest・口コミが20件まで見える）
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from collections import Counter
from datetime import datetime
from urllib.parse import urlparse

import requests

from common import accept_consent, blocked, browser, sync_playwright
from maps_list import list_shops, place, queries, social_from_url, fresh_page

sys.path.insert(0, os.path.expanduser("~/sales-automation"))
import config  # noqa: E402,F401
from src import outreach_list as L  # noqa: E402
from src.lead_filter import is_excluded_chain  # noqa: E402
from src.outreach_list import is_branch_name, is_existing_customer  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DIR = os.path.join(HERE, "data", "leads")
LEADS = os.path.join(DIR, "leads.jsonl")
DONE = os.path.join(DIR, "queries_done.json")
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129 Safari/537.36"}

RV_MIN, RV_MAX = 30, 500
PORTAL_HOSTS = ("hotpepper.jp", "tabelog.com", "gnavi.co.jp", "retty.me", "ikyu.com", "epark.jp", "minimodel.jp", "rakuten.co.jp",
                "jalan.net", "ozmall.co.jp", "beauty-park.jp", "rasysa.com", "coubic.com", "reserva.be", "airrsv.net", "toreta.in",
                "tablecheck.com", "omakase.in", "ekiten.jp", "hitosara.com", "goo.ne.jp", "yahoo.co.jp", "line.me", "lin.ee", "linktr.ee",
                "lit.link", "peraichi.com", "google.com", "g.page", "business.site", "uber.com", "demae-can.com", "wolt.com")
SNS_HOSTS = ("instagram.com", "facebook.com", "twitter.com", "x.com", "tiktok.com", "youtube.com", "ameblo.jp", "note.com", "threads.net")
ARTICLE_RE = re.compile(r"[?&](story_id|article_id|id|p|post|entry)=|/(story|article|articles|news|blog|blogs|post|posts|entry|archives|detail|column|report|topics|feature|interview)s?/", re.I)
COMPANY_PAGE_RE = re.compile(r"https?://[^/]+/(brand|brands|shop|shops|store|stores|tenpo|restaurant|salon)s?/[^/]+", re.I)
FORM_ADDR_RE = re.compile(r"^(webform|form|noreply|no-reply|donotreply|do-not-reply|mailer|system|auto)[._-]?[^@]*@", re.I)
HIRE_RE = re.compile(r"求人|採用情報|リクルート|recruit|スタッフ募集|アルバイト募集|パート募集|アルバイト・パート|一緒に働|募集要項", re.I)
FORM_HINT_RE = re.compile(r"お問い?合わ?せ|問合せ|contact|inquiry|toiawase|form", re.I)


def site_kind(url: str) -> str:
    """「ウェブサイト」欄の種類: own（店のサイト）／portal／sns／article（紹介サイトの記事）／company（運営会社の1ページ）／none"""
    if not url or not url.startswith("http"):
        return "none"
    host = urlparse(url).netloc.lower()
    if any(h in host for h in SNS_HOSTS):
        return "sns"
    if any(h in host for h in PORTAL_HOSTS):
        return "portal"
    if ARTICLE_RE.search(url):
        return "article"
    if COMPANY_PAGE_RE.match(url):
        return "company"
    return "own"


def fetch(url: str):
    """(本文テキスト＋mailto, [(href, リンク文字)])。送る側の outreach_stock.fetch_page と同じ形"""
    r = requests.get(url, headers=UA, timeout=12)
    r.encoding = r.apparent_encoding or r.encoding
    html = r.text[:600000]
    links = [(h, re.sub("<[^>]+>", "", t).strip()) for h, t in re.findall(r"<a[^>]+href=[\"']([^\"'#]+)[\"'][^>]*>(.*?)</a>", html, re.S | re.I)]
    text = re.sub(r"<script.*?</script>|<style.*?</style>", " ", html, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text) + " " + " ".join(re.findall(r"mailto:[^\"'?>\s]+", html))
    time.sleep(0.8)
    return re.sub(r"\s+", " ", text), links


def read_site(url: str, fetch_page=fetch) -> dict:
    """店のサイトから 確かめたメール・問い合わせフォーム・求人の目印・Instagram・Facebook・営業お断り"""
    texts, links = [], []

    def rec(u):
        t, ls = fetch_page(u)
        texts.append(t + " " + " ".join(f"{a} {b}" for a, b in ls))
        links.extend(ls)
        return t, ls
    m = L.find_published_email(url, rec)
    out = {"email": "", "email_page": "", "form": "", "hire": "", "instagram": "", "facebook": "", "no_sales": m["status"] == "refusal",
           "mail_status": m["status"]}
    if m["status"] == "ok" and not FORM_ADDR_RE.match(m["email"]):
        out["email"], out["email_page"] = m["email"].lower(), m.get("source_url", "")
    elif m["status"] == "ok":
        out["mail_status"] = "フォーム用のアドレス"
    host = L.registrable_domain(urlparse(url).netloc)
    for href, text in links:
        full = L.urljoin(url, href)
        same = L.registrable_domain(urlparse(full).netloc) == host
        if not out["form"] and same and FORM_HINT_RE.search(full + " " + (text or "")) and not full.startswith("mailto:"):
            out["form"] = full.split("#")[0]
        s = social_from_url(full)
        out["instagram"] = out["instagram"] or s["instagram"]
        out["facebook"] = out["facebook"] or s["facebook"]
    for t in texts:
        h = HIRE_RE.search(t)
        if h:
            out["hire"] = h.group(0)
            break
    return out


def read_replies(pg) -> dict:
    """店のページ（開いた状態）で新しい口コミ20件の数と返事の数（detail.read_reviews）。読めなければ {}"""
    try:
        import detail
        d = detail.read_reviews(pg)
        return {"rv_n": d.get("rv_n", 0), "rv_replies": d.get("rv_replies", 0), "rv_days": d.get("rv_days", [])[:20]}
    except Exception:
        return {}


def judge(card: dict, p: dict, site: dict, rv: dict) -> tuple[str, dict]:
    """("" か 外す理由, 道)。道 = 送れる手段の一覧"""
    name = card.get("name") or ""
    if p.get("closed"):
        return "閉業", {}
    if is_excluded_chain(name, site.get("email", ""), p.get("website", ""))[0] or is_branch_name(name):
        return "チェーン・支店", {}
    if is_existing_customer(name, (p.get("website") or "") + " " + site.get("email", "")):
        return "既存顧客", {}
    if site.get("no_sales"):
        return "営業お断り", {}
    ways = {k: site.get(k) for k in ("email", "form", "instagram", "facebook") if site.get(k)}
    if not ways:
        return "連絡の道なし", {}
    if rv.get("rv_n", 0) >= 3 and rv["rv_replies"] / rv["rv_n"] >= 0.8:
        return "口コミのほとんどに返事をしている（もう自分でやっている）", {}
    return "", ways


class Limited(RuntimeError):
    """ログインが切れて、口コミが5件に絞られた表示（返事の割合を間違えるので止まる）"""


def build_shop(pg, card: dict, city: str, ind: str, fetch_page=fetch) -> tuple[str, dict]:
    p = place(pg, card["href"])
    body = pg.locator("body").inner_text()[:6000] if pg.locator("body").count() else ""
    if "表示が制限されています" in body or "機能を絞った" in body:
        raise Limited("口コミが5件に絞られた表示（.gprofile_harvest のログインが切れている）")
    kind = site_kind(p.get("website", ""))
    rv = read_replies(pg)
    if rv and rv.get("rv_n", 0) <= 5 and int(card.get("reviews") or 0) > 8:
        raise Limited(f"口コミが{rv.get('rv_n')}件しか読めない（{card.get('reviews')}件ある店）＝ログインが切れている疑い")
    site = {"instagram": "", "facebook": ""}
    soc = social_from_url(p.get("website", ""))
    site.update({k: v for k, v in soc.items() if v})
    if kind == "own":
        try:
            site.update({k: v for k, v in read_site(p["website"], fetch_page).items() if v or k not in site})
        except Exception as e:
            site["err_site"] = str(e)[:60]
    why, ways = judge(card, p, site, rv)
    rec = {"v": 2, "cid": card["cid"], "name": card["name"], "industry": ind, "city": city, "rank": card.get("rank"),
           "rating": card.get("rating"), "reviews": card.get("reviews"), "maps": card["href"].split("?")[0],
           "website": p.get("website", ""), "site_kind": kind, "phone": p.get("phone", ""), "address": p.get("address", ""),
           "closed": p.get("closed", False), "emails": [site["email"]] if site.get("email") else [],
           "email_pages": [site["email_page"]] if site.get("email_page") else [], "mail_status": site.get("mail_status", kind),
           "form": site.get("form", ""), "hire": site.get("hire", ""), "instagram": site.get("instagram", ""),
           "facebook": site.get("facebook", ""), "no_sales": bool(site.get("no_sales")), **rv,
           "ways": sorted(ways), "drop": why, "at": time.strftime("%Y-%m-%d %H:%M")}
    return why, rec


def report(stats: Counter, kept: list[dict], path: str, n_cards: int) -> str:
    ways = Counter(w for r in kept for w in r["ways"])
    lines = [f"# リスト作り v2 の報告（{datetime.now():%Y-%m-%d %H:%M}）", "",
             f"- 一覧で見た店 {n_cards} → 入れた店 **{len(kept)}**", "",
             "## 入れた店の道", "| 道 | 店 |", "|---|---|"]
    lines += [f"| {k} | {v} |" for k, v in (("メール（確かめた）", ways["email"]), ("問い合わせフォーム", ways["form"]),
                                           ("Instagram", ways["instagram"]), ("Facebook", ways["facebook"]))]
    lines += ["", f"- 求人の目印あり {sum(1 for r in kept if r['hire'])}／返事が3割未満 "
              f"{sum(1 for r in kept if r.get('rv_n', 0) >= 3 and r['rv_replies'] / r['rv_n'] < 0.3)}", "",
              "## 外した理由", "| 理由 | 店 |", "|---|---|"]
    lines += [f"| {k} | {v} |" for k, v in stats.most_common()]
    lines += ["", "## 見本10店（目で確かめる用）", "| 店 | 業種・市区 | 口コミ | 返事 | 道 | 求人 | メールの出どころ |", "|---|---|---|---|---|---|---|"]
    for r in kept[:10]:
        lines.append(f"| {r['name'][:20]} | {r['industry']}・{r['city']} | {r['reviews']} | {r.get('rv_replies', '?')}/{r.get('rv_n', '?')} | "
                     f"{'・'.join(r['ways'])} | {r['hire'] or '—'} | {(r['email_pages'] or [''])[0][:50]} |")
    txt = "\n".join(lines) + "\n"
    open(path, "w", encoding="utf-8").write(txt)
    return txt


def main():
    n_max = int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else 300
    q_max = int(sys.argv[sys.argv.index("--q") + 1]) if "--q" in sys.argv else 10**6
    dry = "--dry" in sys.argv
    os.makedirs(DIR, exist_ok=True)
    done = json.load(open(DONE, encoding="utf-8")) if os.path.exists(DONE) else {}
    have = {json.loads(x)["cid"] for x in open(LEADS, encoding="utf-8") if x.strip()} if os.path.exists(LEADS) else set()
    todo = [qc for qc in queries() if f"{qc[1]}|{qc[0]}" not in done]
    if not todo:   # 一巡したら、前に回った日の古い順にやり直す（店は入れ替わる）
        todo = sorted(queries(), key=lambda qc: done.get(f"{qc[1]}|{qc[0]}", ""))
    todo = todo[:q_max]
    stats, kept, n_cards = Counter(), [], 0
    print(f"[LIST] 残り {len(todo)} 検索・既知 {len(have)} 店・今回の上限 {n_max} 店" + ("（ドライラン）" if dry else ""), flush=True)
    with sync_playwright() as pw:
        b, ctx = browser(pw)
        pg = ctx.new_page()
        try:
            for city, ind in todo:
                if len(kept) >= n_max or any(k.startswith("止まった") for k in stats):
                    break
                try:
                    cards = list_shops(pg, f"{ind} {city}")
                except Exception as e:
                    print(f"[LIST][ERR] {ind} {city}: {str(e)[:80]}", flush=True)
                    pg = fresh_page(ctx, pg)
                    continue
                for c in cards:
                    if not c.get("cid") or c["cid"] in have:
                        continue
                    n_cards += 1
                    rv_list = int(c.get("reviews") or 0)
                    if not (RV_MIN <= rv_list <= RV_MAX):
                        stats[f"口コミ{RV_MIN}〜{RV_MAX}件の外"] += 1; have.add(c["cid"]); continue
                    if is_excluded_chain(c.get("name") or "")[0] or is_branch_name(c.get("name") or ""):
                        stats["チェーン・支店"] += 1; have.add(c["cid"]); continue
                    try:
                        why, rec = build_shop(pg, c, city, ind)
                    except Limited as e:
                        print(f"[LIST] 止めます: {e}。hitotsunagi861 で .gprofile_harvest の Chrome にログインし直してから、もう一度「リスト作って」", flush=True)
                        stats["止まった: " + str(e)[:40]] += 1
                        todo = []
                        break
                    except Exception as e:
                        stats["店のページが読めない"] += 1
                        print(f"[LIST][ERR] {c.get('name')}: {str(e)[:60]}", flush=True)
                        pg = fresh_page(ctx, pg)
                        continue
                    have.add(c["cid"])
                    if why:
                        stats[why] += 1
                        continue
                    kept.append(rec)
                    if not dry:
                        with open(LEADS, "a", encoding="utf-8") as f:
                            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    if len(kept) >= n_max:
                        break
                    time.sleep(1.2)
                if not dry:
                    done[f"{ind}|{city}"] = time.strftime("%Y-%m-%d %H:%M")
                    json.dump(done, open(DONE, "w", encoding="utf-8"), ensure_ascii=False)
                print(f"[LIST] {ind} {city}: 入れた {len(kept)}", flush=True)
        finally:
            b.close()
    path = os.path.join(DIR, f"list_build_report_{datetime.now():%Y%m%d_%H%M}.md")
    print(report(stats, kept, path, n_cards))


if __name__ == "__main__":
    os.environ.setdefault("GMAPS_PROFILE", os.path.join(HERE, ".gprofile_harvest"))
    main()
