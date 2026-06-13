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

echo "$PLUGIN_NAME uninstalled."
