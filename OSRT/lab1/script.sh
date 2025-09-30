#!/bin/sh
echo "Kol-vo parametrov: $#"
echo "Parametry: $@"
for param in "$@"; do
	echo "Parametr: $param"
done
