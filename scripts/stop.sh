#!/bin/bash

if ps -ef | grep "[/]opt/BotWave/scripts/wtt/main.py" > /dev/null; then
    touch /tmp/killwtt
    echo "WTT stopped"
fi
