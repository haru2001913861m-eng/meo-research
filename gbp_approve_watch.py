# -*- coding: utf-8 -*-
"""Business Profile API の承認を毎日確かめ、下りた日に Railway の GBP_ENABLED=true を入れる（会長 2026-10-17「全部やって自動で動かしていい」）.

申請: 2026-10-17 ケース ID 4-5844000041982（プロジェクト hito-sales・番号 155094317546・審査 7〜10 営業日）。
鍵: ~/.config/hitotsunagi/gbp_token.json（scripts/gbp_auth.py --yes が作る。会長が1回だけ実行）。
動き:
  鍵が無い → 10/28 以降、週1回だけ会長の LINE に「鍵を取る1行」を出す
  鍵がある → accounts 一覧を呼ぶ。200 = 承認 → railway variables --set GBP_TOKEN_JSON=… --set GBP_ENABLED=true → 会長 LINE に1回
             429／quota = 承認待ち（黙ってログだけ）。それ以外 = 会長 LINE に1日1回
終わったら data/gbp_approved.json を書き、以後は何もしない。
実行: python3 gbp_approve_watch.py [--dry]。毎日の呼び出し: run_client_watch.sh の先頭（launchd com.hitotsunagi.meo-client-watch・05:00／06:30／13:00）
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import date, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
SA = os.path.expanduser("~/sales-automation")
sys.path.insert(0, SA); os.chdir(SA)

DRY = "--dry" in sys.argv
TOKEN_FILE = os.path.expanduser("~/.config/hitotsunagi/gbp_token.json")
DONE = os.path.join(HERE, "data", "gbp_approved.json")
RAILWAY = os.path.expanduser("~/.railway/bin/railway")
ACCT = "https://mybusinessaccountmanagement.googleapis.com/v1/accounts"
SCOPE = ["https://www.googleapis.com/auth/business.manage"]
REMIND_FROM = date(2026, 10, 28)   # 審査 7 営業日の目安
CASE = "4-5844000041982"
KEY_CMD = "cd ~/sales-automation && git pull origin master && python3 scripts/gbp_auth.py --yes"


def notify_ceo_once(text: str, key: str) -> None:
    mark = os.path.join(HERE, "data", "ceo_notice_" + datetime.now().strftime("%Y%m%d") + ".txt")
    if os.path.exists(mark) and key in open(mark, encoding="utf-8").read():
        return
    open(mark, "a", encoding="utf-8").write(key + "\n")
    if DRY:
        print("[ceo]", text); return
    try:
        from src import line_notifier
        line_notifier.send(text)
    except Exception as e:
        print(f"[gbp_approve_watch] 会長通知失敗: {e}")


def check(token_json: str) -> tuple[str, str]:
    """('ok'|'wait'|'error', 詳細)"""
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    import requests
    cr = Credentials.from_authorized_user_info(json.loads(token_json), SCOPE)
    if not cr.valid:
        cr.refresh(Request())
    r = requests.get(ACCT, headers={"Authorization": f"Bearer {cr.token}"}, timeout=20)
    if r.status_code == 200:
        return "ok", r.text[:2000]
    if r.status_code == 429 or "quota" in r.text.lower():
        return "wait", f"{r.status_code} {r.text[:120]}"
    if r.status_code == 403 and ("not been used" in r.text or "disabled" in r.text):   # プロジェクトで API が未有効（承認前の状態）
        return "wait", f"403 API 未有効: {r.text[:100]}"
    return "error", f"{r.status_code} {r.text[:200]}"


def v4_enabled(token_json: str, accounts_text: str) -> bool | None:
    """v4 が有効なら True、未有効（403 not been used/disabled）なら False、判断できなければ None（止めない）。"""
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        import requests
        acct = ((json.loads(accounts_text) if accounts_text.startswith("{") else {}).get("accounts") or [{}])[0].get("name", "accounts/-")
        cr = Credentials.from_authorized_user_info(json.loads(token_json), SCOPE)
        if not cr.valid:
            cr.refresh(Request())
        r = requests.get(f"https://mybusiness.googleapis.com/v4/{acct}/locations/-/reviews",
                         headers={"Authorization": f"Bearer {cr.token}"}, timeout=20)
        if r.status_code == 403 and ("not been used" in r.text or "disabled" in r.text):
            return False
        return True
    except Exception as e:
        print(f"[gbp_approve_watch] v4 の確認ができず（止めない）: {e}")
        return None


def main() -> int:
    if os.path.exists(DONE):
        print("[gbp_approve_watch] 承認済み（何もしない）:", open(DONE, encoding="utf-8").read()[:80]); return 0
    if not os.path.exists(TOKEN_FILE):
        if date.today() >= REMIND_FROM and date.today().weekday() == 0:   # 月曜に週1回
            notify_ceo_once(f"【MEO】Google の API（ケース {CASE}）の鍵がまだです。Mac で1行:\n{KEY_CMD}\n（ブラウザで「許可」を押すだけ。承認前でも取れます）", "gbp_key")
        print("[gbp_approve_watch] 鍵なし"); return 0
    tok = open(TOKEN_FILE, encoding="utf-8").read()
    state, why = check(tok)
    print(f"[gbp_approve_watch] {state}: {why}")
    if state == "wait":
        return 0
    if state == "error":
        notify_ceo_once(f"【MEO 要確認】Google の API の確認でエラー: {why[:120]}", "gbp_err"); return 1
    # 承認が下りた。口コミ返信・投稿に使う v4（mybusiness.googleapis.com）は承認後にしかライブラリに出ないので、有効かを確かめてから切り替える
    v4 = v4_enabled(tok, why)
    if v4 is False:
        notify_ceo_once(f"【MEO 要対応】Google の API の承認が下りました（ケース {CASE}）。あと1つ、Cloud コンソールで「Google My Business API」を有効にしてください（1クリック）:\n"
                        "https://console.cloud.google.com/apis/library/mybusiness.googleapis.com?project=hito-sales\n有効にした翌朝に自動で切り替わります", "gbp_v4")
        return 0
    if not DRY:
        subprocess.run([RAILWAY, "variables", "--set", f"GBP_TOKEN_JSON={tok}", "--set", "GBP_ENABLED=true"], cwd=SA, check=True)
    json.dump({"at": datetime.now().isoformat(timespec="seconds"), "accounts": why}, open(DONE, "w", encoding="utf-8"), ensure_ascii=False)
    notify_ceo_once(f"【MEO】Google の Business Profile API の承認が下りました（ケース {CASE}）。Railway に GBP_ENABLED=true を入れました。"
                    "次のデプロイから、口コミ返信（★4〜5は自動・★1〜3は店の承認後）・お知らせ・説明文・招待の承認が自動になります。", "gbp_ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
