# -*- coding: utf-8 -*-
"""LINE の「英語の順位」依頼を拾って調べ、LINE で返す（Mac・launchd で10分ごと）。
依頼の置き場: Notion「💬 MEO LINE 状態」の状態JSON の en_req（Railway の meo_bot が書く）。
  en_req = {"status": "pending", "id": "<日時>", "text": "店名 町", "industry": "寿司", "town": "町"}
済んだ依頼は data/en_rank_done.json に id で残す（同じ依頼に2回返さない）。結果は data/en_rank_log.jsonl。
実行: python3 en_rank_watch.py [--dry]   … --dry は LINE に送らず表示だけ
"""
from __future__ import annotations
import fcntl, json, os, sys, time
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("GMAPS_PROFILE", os.path.join(HERE, ".gprofile"))
import en_rank  # noqa: E402
SA = os.path.expanduser("~/sales-automation")
sys.path.insert(0, SA); os.chdir(SA)
import config  # noqa: E402
import requests  # noqa: E402
from src.notion_client import get_client  # noqa: E402

DRY = "--dry" in sys.argv
DONE = os.path.join(HERE, "data", "en_rank_done.json")
LOG = os.path.join(HERE, "data", "en_rank_log.jsonl")
LOCK = os.path.join(HERE, "data", "en_rank_watch.lock")


def pending() -> list[tuple[str, dict]]:
    n = get_client(); since = (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()
    out, cursor = [], None
    while True:
        kw = {"database_id": config.MEO_STATE_DB_ID, "page_size": 100,
              "filter": {"property": "更新", "date": {"on_or_after": since}}}
        if cursor:
            kw["start_cursor"] = cursor
        res = n.databases.query(**kw)
        for p in res["results"]:
            uid = "".join(t["plain_text"] for t in p["properties"]["ユーザーID"]["title"])
            raw = "".join(t["plain_text"] for t in p["properties"]["状態JSON"]["rich_text"])
            try:
                s = json.loads(raw)
            except Exception:
                continue
            q = s.get("en_req") or {}
            if q.get("status") == "pending" and q.get("text"):
                out.append((uid, q))
            q = s.get("screens_req") or {}   # 無料点検の残り2つの画面（英語の地図・AI）・2026-10-17
            if q.get("status") == "pending" and q.get("text"):
                out.append((uid, {**q, "kind": "screens"}))
        if not res.get("has_more"):
            return out
        cursor = res["next_cursor"]


def push(uid: str, text: str) -> bool:
    if DRY:
        print(f"--- {uid[:8]}\n{text}"); return True
    r = requests.post("https://api.line.me/v2/bot/message/push", timeout=20,
                      headers={"Authorization": f"Bearer {config.MEO_LINE_CHANNEL_ACCESS_TOKEN}", "Content-Type": "application/json"},
                      json={"to": uid, "messages": [{"type": "text", "text": text[:4900]}]})
    return r.status_code == 200


def notify_ceo_once(text: str) -> None:
    """同じ日に同じ知らせは1回だけ（会長の LINE）。"""
    mark = os.path.join(HERE, "data", "ceo_notice_" + datetime.now().strftime("%Y%m%d") + ".txt")
    if os.path.exists(mark) and text[:30] in open(mark, encoding="utf-8").read():
        return
    open(mark, "a", encoding="utf-8").write(text[:30] + "\n")
    if DRY:
        print("[ceo]", text); return
    try:
        from src import line_notifier
        line_notifier.send(text)
    except Exception as e:
        print(f"[en_rank_watch] 会長通知失敗: {e}")


def main():
    os.makedirs(os.path.dirname(DONE), exist_ok=True)
    lk = open(LOCK, "w")
    try:
        fcntl.flock(lk, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        print("[en_rank_watch] 前の回がまだ動いている"); return
    done = set(json.load(open(DONE))) if os.path.exists(DONE) else set()
    todo = [(u, q) for u, q in pending() if f"{u}|{q.get('id')}" not in done]
    print(f"[en_rank_watch] {datetime.now():%m-%d %H:%M} 依頼 {len(todo)} 件", flush=True)
    for uid, q in todo:
        if q.get("kind") == "screens":
            import screens
            try:
                r = screens.check(q["text"], q.get("industry", ""), who=uid[:10])
            except Exception as e:
                r = {"ok": False, "why": str(e)[:100]}
            if r.get("ok") and not (r.get("ai") or {}).get("ok"):
                notify_ceo_once(f"【MEO 要確認】無料点検の ChatGPT に聞けませんでした（{(r.get('ai') or {}).get('why')}）。聞かない版で返しています。OpenAI の残高を確認してください")
            ok = push(uid, screens.message(r, f"「{q.get('shop') or r.get('name_ja') or 'お店'}」"))
        else:
            try:
                r = en_rank.report(q["text"], q.get("industry") or "その他", q.get("town", ""))
            except Exception as e:
                r = {"ok": False, "why": str(e)[:100]}
            label = q["text"].split()[0] if r.get("ok") else "お店"
            ok = push(uid, en_rank.message(r, f"「{label}」"))
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps({"uid": uid[:10], "req": q, "res": r, "sent": ok}, ensure_ascii=False) + "\n")
        if ok and not DRY:
            done.add(f"{uid}|{q.get('id')}"); json.dump(sorted(done), open(DONE, "w"))
        time.sleep(3)


if __name__ == "__main__":
    main()
