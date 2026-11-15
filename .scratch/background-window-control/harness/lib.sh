#!/usr/bin/env bash
# Shared harness for the real-application acceptance cases.
#
# Every case runs against a nested niri instance so the user's own session is
# never the thing under test; the harness only reads the user's session to prove
# it did not change.
set -uo pipefail
export HOME=/home/sx PATH=/usr/local/bin:/usr/bin:/bin XDG_RUNTIME_DIR=/run/user/1000
unset DISPLAY

NIRI_BIN=${NIRI_BIN:-/home/sx/projects/niri/target/debug/niri}
PROBE=${PROBE:-/home/sx/projects/agent-seat-probe/target/debug/agent-seat-probe}
TARGET=${TARGET:-/home/sx/projects/agent-seat-probe/target/debug/scoped-target}
SHOT=${SHOT:-/home/sx/projects/agent-seat-probe/target/debug/scoped-shot}
HARNESS=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
APPS=$HARNESS/apps
POC=${POC:-/tmp/poc}
mkdir -p "$POC"

start_nested() { # $1 = log prefix, $2 = config (default $POC/poc.kdl)
    local prefix=${1:-case} config=${2:-$POC/poc.kdl}
    rm -f "$POC/$prefix-nested.log" "$POC/bind-fired"
    WAYLAND_DISPLAY=wayland-1 "$NIRI_BIN" -c "$config" > "$POC/$prefix-nested.log" 2>&1 &
    NEST=$!
    SOCK=""
    for _ in $(seq 1 80); do
        SOCK=$(grep -o 'listening on Wayland socket: .*' "$POC/$prefix-nested.log" | tail -1 | sed 's/.*socket: //')
        [ -n "$SOCK" ] && break
        sleep 0.25
    done
    if [ -z "$SOCK" ]; then
        echo "NESTED_START_FAILED"
        return 1
    fi
    export WAYLAND_DISPLAY="$SOCK"
    export NIRI_SOCKET=$(ls -t /run/user/1000/niri."$SOCK".*.sock 2>/dev/null | head -1)
    return 0
}

stop_nested() {
    [ -n "${NEST:-}" ] && kill "$NEST" 2>/dev/null
    sleep 0.4
    [ -n "${NEST:-}" ] && kill -9 "$NEST" 2>/dev/null
    wait 2>/dev/null
    return 0
}

win_id() { # $1 = app id, $2 = attempts (default 40)
    local app=$1 attempts=${2:-40} id=""
    for _ in $(seq 1 "$attempts"); do
        id=$(niri msg -j windows 2>/dev/null | grep -o "{\"id\":[0-9]*[^}]*\"app_id\":\"$app\"" | head -1 | grep -o '"id":[0-9]*' | cut -d: -f2)
        [ -n "$id" ] && { echo "$id"; return 0; }
        sleep 0.3
    done
    echo ""
    return 1
}

pin() { "$TARGET" "$1" > /dev/null 2>&1; }
unpin() { "$TARGET" none > /dev/null 2>&1; }

# The reply now waits for the PNG to hit disk, so one attempt is the honest check;
# retrying would have hidden the old "Handled before written" bug.
shot() { # $1 = window id, $2 = path, $3 = attempts (default 1)
    local wid=$1 path=$2 attempts=${3:-1} attempt=1
    rm -f "$path"
    while [ "$attempt" -le "$attempts" ]; do
        "$SHOT" "$wid" "$path" >> "$POC/shot-attempts.log" 2>&1
        [ -s "$path" ] && { echo "shot ok attempt=$attempt"; return 0; }
        attempt=$((attempt + 1))
        sleep 0.6
    done
    echo "shot FAILED after $attempts attempts"
    return 1
}

wait_ready() { # $1 = log file, $2 = pattern, $3 = attempts
    local log=$1 pattern=$2 attempts=${3:-60}
    for _ in $(seq 1 "$attempts"); do
        [ -f "$log" ] && grep -q "$pattern" "$log" 2>/dev/null && return 0
        sleep 0.3
    done
    return 1
}

focus_state() { niri msg -j focused-window 2>/dev/null | tr -d '\n'; }
clip_state() { wl-paste --list-types 2>/dev/null | tr '\n' ',' ; }

invariant_before() { # $1 = evidence dir
    focus_state > "$1/focus-before.txt"
    clip_state > "$1/clip-before.txt"
    rm -f "$POC/bind-fired"
}

invariant_after() {
    focus_state > "$1/focus-after.txt"
    clip_state > "$1/clip-after.txt"
    if [ -f "$POC/bind-fired" ]; then echo "invariant_binds=FIRED"; else echo "invariant_binds=not_fired"; fi
    if [ "$(cat "$1/focus-before.txt")" = "$(cat "$1/focus-after.txt")" ]; then
        echo "invariant_focus=unchanged"
    else
        echo "invariant_focus=CHANGED"
    fi
    if [ "$(cat "$1/clip-before.txt")" = "$(cat "$1/clip-after.txt")" ]; then
        echo "invariant_clipboard=unchanged"
    else
        echo "invariant_clipboard=CHANGED"
    fi
}
