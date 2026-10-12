#!/bin/zsh
# 契約店の見回り（毎日1回・契約日の曜日の店だけを読む）。launchd: com.hitotsunagi.meo-client-watch
cd "$HOME/meo-research" || exit 1
DAY=$(date +%F); DONE="$HOME/meo-research/logs/client_watch_done"
[[ -f "$DONE" && "$(cat $DONE)" == "$DAY" ]] && exit 0
export GMAPS_PROFILE="$HOME/meo-research/.gprofile_watch"
caffeinate -i /usr/bin/env python3 -u client_watch.py && echo "$DAY" > "$DONE"
