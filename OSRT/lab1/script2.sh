#!/bin/sh
if [$# -lt 1]; then
	echo "Process: $0"
	exit 1
fi
PROC="$1"
pidin | grep "$PROC" 
