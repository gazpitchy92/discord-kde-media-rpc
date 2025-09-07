#!/bin/bash

base_dir="$(dirname "$0")"

> "$base_dir/playing.txt"

python3 "$base_dir/set.py" &
pid=$!

while true; do
    if ! kill -0 $pid 2>/dev/null; then
        python3 "$base_dir/set.py" &
        pid=$!
    fi

    artist=$(playerctl metadata --format '{{ artist }}' 2>/dev/null)
    title=$(playerctl metadata --format '{{ title }}' 2>/dev/null)

    if [[ -n "$artist" && -n "$title" ]]; then
        echo "$artist - $title" > "$base_dir/playing.txt"
    elif [[ -n "$artist" ]]; then
        echo "$artist" > "$base_dir/playing.txt"
    elif [[ -n "$title" ]]; then
        echo "$title" > "$base_dir/playing.txt"
    else
        > "$base_dir/playing.txt"
    fi

    sleep 5
done