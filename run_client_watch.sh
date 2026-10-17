#!/bin/zsh
# 契約店の見回り（毎日1回・契約日の曜日の店だけを読む）。launchd: com.hitotsunagi.meo-client-watch
cd "$HOME/meo-research" || exit 1
# 2026-10-17: Business Profile API の承認（ケース 4-5844000041982）を毎日確かめ、下りた日に Railway の GBP_ENABLED=true を入れる（軽い・承認後は何もしない）
/Library/Frameworks/Python.framework/Versions/3.13/bin/python3 -u gbp_approve_watch.py >> logs/gbp_approve_watch.out.log 2>&1
# 2026-10-17: 本番の事故（Railway の [INCIDENT]・launchd の失敗）を拾って hitotsunagi-hq/TASKS の fix に積む（無人ワーカーが原因を調べ、立ち会いの回で直す）
/Library/Frameworks/Python.framework/Versions/3.13/bin/python3 -u "$HOME/hitotsunagi-hq/ops/mac_jobs_health.py" >> logs/mac_jobs_health.log 2>&1
# 2026-10-17: Instagram ストーリー3本を毎朝作る（画像＋文→ iCloud Drive「MEOストーリー」と会長 LINE。1日1回は make_stories.py 側で判定）
/Library/Frameworks/Python.framework/Versions/3.13/bin/python3 -u "$HOME/hitotsunagi-hq/businesses/meo/stories/make_stories.py" >> logs/stories.log 2>&1
DAY=$(date +%F); DONE="$HOME/meo-research/logs/client_watch_done"
[[ -f "$DONE" && "$(cat $DONE)" == "$DAY" ]] && exit 0
export GMAPS_PROFILE="$HOME/meo-research/.gprofile_watch"
caffeinate -i /Library/Frameworks/Python.framework/Versions/3.13/bin/python3 -u client_watch.py && echo "$DAY" > "$DONE"
