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

read -p "Do you want to auto-start WTT? [y/N]: " autostart

if [[ "${autostart,,}" == "y" ]]; then
    echo "wtt" > "$BW_INSTALL/handlers/l_onready_wtt_start.shdl"
    echo "wtt" > "$BW_INSTALL/handlers/s_onready_wtt_start.shdl"
fi

echo "Installed."