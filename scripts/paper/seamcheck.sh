#!/bin/zsh
# Roll the tile by half its size, then compare the mean |gradient| across the
# join line with the image average. ~1.0 means seamless; a real seam scores >2.
setopt shwordsplit
M=${MAGICK:-/opt/homebrew/bin/magick}
IMG=$1; T=$(mktemp -d)
W=$($M identify -format '%w' "$IMG"); H=$($M identify -format '%h' "$IMG")
HW=$((W/2)); HH=$((H/2))
$M "$IMG" -colorspace Gray -roll +${HW}+${HH} $T/r.png
$M $T/r.png \( +clone -roll -1+0 \) -compose Difference -composite $T/gx.png
$M $T/r.png \( +clone -roll +0-1 \) -compose Difference -composite $T/gy.png
gxj=$($M $T/gx.png -crop 1x${H}+$((HW-1))+0 +repage -format '%[fx:mean*255]' info:)
gxa=$($M $T/gx.png -format '%[fx:mean*255]' info:)
gyj=$($M $T/gy.png -crop ${W}x1+0+$((HH-1)) +repage -format '%[fx:mean*255]' info:)
gya=$($M $T/gy.png -format '%[fx:mean*255]' info:)
printf '%-18s gx join=%.3f avg=%.3f ratio=%.3f | gy join=%.3f avg=%.3f ratio=%.3f\n' \
  "$(basename $IMG)" $gxj $gxa $(echo "$gxj/$gxa"|bc -l) $gyj $gya $(echo "$gyj/$gya"|bc -l)
rm -rf $T
