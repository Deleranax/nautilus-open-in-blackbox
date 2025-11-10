#!/bin/bash

# Create parent folder and symlink
if [ -v XDG_DATA_HOME ]
then
	mkdir -p "$XDG_DATA_HOME/nautilus-python/extensions"
	cp "$(pwd)/nautilus-open-in-blackbox.py" "$XDG_DATA_HOME/nautilus-python/extensions/nautilus-open-in-blackbox.py"
else
	mkdir -p "$HOME/.local/share/nautilus-python/extensions"
	cp "$(pwd)/nautilus-open-in-blackbox.py" "$HOME/.local/share/nautilus-python/extensions/nautilus-open-in-blackbox.py"
fi

# Restart nautilus
nautilus -q
