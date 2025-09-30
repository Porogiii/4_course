#!/bin/sh
if [ $# -eq 0 ]; then
	echo "Name file"
	exit 1
fi

gcc -o ${1%.*} $1 2> eroors.txt

if [ $? -eq 0 ]; then
	./${1%.*}
else
	vi eroors.txt
fi
