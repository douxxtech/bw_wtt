#!/bin/bash

if [ -z "$REMOTE_CMD_PORT" ]; then
    echo "[ERROR] REMOTE_CMD_PORT environment variable is not set. Did you start your server with --rc <port>?"
    exit 1
fi
REMOTE_CMD_PORT=$(echo "$REMOTE_CMD_PORT" | sed 's/^immutable(\(.*\))$/\1/')

if [ -z "$WTT_PORT" ]; then
    if [ -n "$1" ]; then
        # Try to parse ARGV1 as integer
        if [[ "$1" =~ ^[0-9]+$ ]]; then
            WTT_PORT="$1"
        else
            echo "[WARN] WTT_PORT argument '$1' is not a valid port number, using default 9940"
            WTT_PORT=9940
        fi
    else
        echo "[WARN] WTT_PORT not set and no argument provided, using default 9940"
        WTT_PORT=9940
    fi
fi

# start the script
nohup /opt/BotWave/venv/bin/python3 /opt/BotWave/scripts/wtt/main.py "$WTT_PORT" "$REMOTE_CMD_PORT" "$WTT_NEWLINE" > /dev/null 2>&1 &

echo "WS To TCP (probably) started."
echo "See full logs in /opt/BotWave/scripts/wtt/logs.txt"

exit 0