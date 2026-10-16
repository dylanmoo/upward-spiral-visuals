#!/bin/bash
# Stitch chained zoom: seg0 + v2/seg1..7. Drop each later segment's first frame (it duplicates the previous last frame).
# Then close the loop with a short crossfade from the end back into the start.
# usage: stitch_zoom.sh <zoom_dir> <out.mp4> [loop_fade_seconds]
z=$1; out=$2; d=${3:-0.25}
inputs=(-i "$z/seg0.mp4"); chain="[0:v]fps=24,format=yuv420p,setpts=PTS-STARTPTS[s0];"; labels="[s0]"
for n in 1 2 3 4 5 6 7; do
  inputs+=(-i "$z/v2/seg$n.mp4")
  chain+="[$n:v]fps=24,format=yuv420p,trim=start_frame=1,setpts=PTS-STARTPTS[s$n];"; labels+="[s$n]"
done
tmp=$(dirname "$out")/_chain.mp4
ffmpeg -v error -y "${inputs[@]}" -filter_complex "${chain}${labels}concat=n=8:v=1[v]" -map "[v]" -c:v libx264 -crf 18 -an "$tmp"
len=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$tmp")
"$(dirname "$0")/loopify.sh" "$tmp" "$out" 0 "$len" "$d"
rm -f "$tmp"
