## Convert avi to gif

in_fn="showreal.avi"
out_fn="showreal.gif"

ffmpeg -i $in_fn -vf "fps=10,scale=1000:-1:flags=lanczos" -c:v pam -f image2pipe - | convert -delay 10 - -loop 0 -layers optimize $out_fn
