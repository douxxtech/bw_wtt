#!/bin/bash

# uninstall.sh: removes wtt from BotWave.
# Run as root: sudo bash uninstall.sh

PLUGIN_NAME="wtt"
BW_INSTALL="/opt/BotWave"

if [ "$EUID" -ne 0 ]; then
    echo "Error: run as root (sudo bash uninstall.sh)"
    exit 1
fi

# Remove scripts
rm -rf "$BW_INSTALL/scripts/$PLUGIN_NAME"

# Remove handlers (only the ones we installed)
for f in handlers/*; do
    rm -f "$BW_INSTALL/handlers/$(basename $f)"
done

# Remove auto-start handlers
rm -f "$BW_INSTALL/handlers/l_onready_wtt_start.shdl"
rm -f "$BW_INSTALL/handlers/s_onready_wtt_start.shdl"


# Remove the eventual .env file modifications
sed -i '/# bw_wtt settings start/,/# bw_wtt settings end/d' "$BW_INSTALL/.env" 2>/dev/null

echo "$PLUGIN_NAME uninstalled."
