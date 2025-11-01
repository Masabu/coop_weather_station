#!/usr/bin/env bash

# Minimal uploader: loop over main.py and monitor.py
for f in main.py monitor.py secret.py utilities.py bme280.py ; do
	if [ -f "$f" ]; then
		mpremote cp "$f" ":$f"
	else
		echo "Skipping missing file: $f" >&2
	fi
done



