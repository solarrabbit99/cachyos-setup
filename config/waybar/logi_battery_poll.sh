#!/usr/bin/env bash

DEVICE="PRO X"
ICON="󰋎"

while true; do
    # Extract battery percentage from Solaar
    PCT=$(solaar show "$DEVICE" 2>/dev/null \
        | grep -i "Battery:" \
        | head -n1 \
        | sed -E 's/.*Battery:[[:space:]]*([0-9]+)%.*/\1/')

    # Only print if PCT is a valid number (0–100)
    if [[ "$PCT" =~ ^[0-9]+$ ]]; then
        echo "{\"text\": \"$ICON $PCT%\"}"
    else
        echo "{\"text\": \"$ICON N/A\"}"
    fi

    sleep 5
done

