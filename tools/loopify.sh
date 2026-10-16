#!/bin/bash
# usage: loopify.sh in.mp4 out.mp4 start end fade
in=$1; out=$2; s=$3; e=$4; d=$5
L=$(python3 -c "print($e-$s)")
off=$(python3 -c "print($L-2*$d)")
ffmpeg -v error -y -i "$in" -filter_complex "
[0:v]trim=start=$s:end=$e,setpts=PTS-STARTPTS,fps=24,format=yuv420p,split[a][b];
[a]trim=start=$d,setpts=PTS-STARTPTS[x];
[b]trim=end=$d,setpts=PTS-STARTPTS[y];
[x][y]xfade=transition=fade:duration=$d:offset=$off[v]" -map "[v]" -an -c:v libx264 -crf 18 "$out"
ffprobe -v error -show_entries format=duration -of csv=p=0 "$out"
