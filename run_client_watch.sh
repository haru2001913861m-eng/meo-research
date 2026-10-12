#!/bin/zsh
# 契約店の見回り（週1回だけ実走・ISO週で済みを記録）。launchd: com.hitotsunagi.meo-client-watch
cd "$HOME/meo-research" || exit 1
WEEK=$(date +%G-W%V); DONE="$HOME/meo-research/logs/client_watch_done"
[[ -f "$DONE" && "$(cat $DONE)" == "$WEEK" ]] && exit 0
export GMAPS_PROFILE="$HOME/meo-research/.gprofile_watch"
caffeinate -i /usr/bin/env python3 -u client_watch.py && echo "$WEEK" > "$DONE"
