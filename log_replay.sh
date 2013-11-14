#!/bin/sh
inp="${1:-flight_data.csv}"
out="${2:-test.csv}"
> "$out"
while :
do
	tail -n+50 "$inp" | head -600
done |
while read -r x
do
	sleep .5
	echo "$x" >> "$out"
done
