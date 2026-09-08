#!/bin/bash

BW_INSTALL="/opt/BotWave"

if [ "$EUID" -ne 0 ]; then
    echo "Error: This script must be run as root. Try using 'sudo'."
    exit 1
fi

mkdir -p "$BW_INSTALL/scripts/wtt"
mkdir -p "$BW_INSTALL/handlers"

cp scripts/* "$BW_INSTALL/scripts/wtt/"
chmod +x "$BW_INSTALL/scripts/wtt/"*.sh

cp handlers/* "$BW_INSTALL/handlers/"

read -p "Do you want to auto-start WTT? [Y/n]: " autostart

if [[ "${autostart,,}" != "n" ]]; then
    echo "wtt" > "$BW_INSTALL/handlers/l_onready_wtt_start.shdl"
    echo "wtt" > "$BW_INSTALL/handlers/s_onready_wtt_start.shdl"
fi

read -p "Do you want to auto-start the remote cmd on port 9939? [Y/n]" autoremote

if [[ "${autoremote,,}" != "n" ]]; then
    cat >> "$BW_INSTALL/.env" << EOF

# bw_wtt settings start
REMOTE_CMD_PORT=immutable(9939)
# bw_wtt settings end
EOF
fi

echo "Installed."