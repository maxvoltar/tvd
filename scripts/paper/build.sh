#!/bin/zsh
# Seamless 1024x1024 newsprint / off-black paper tiles for the site background
# (img/paper-light.jpg, img/paper-dark.jpg). Needs ImageMagick 7 and python3.
#   ./build.sh            -> uses params.env next to this script
#   VAR=... ./build.sh    -> override any single parameter
# Intermediates go to ./work (gitignored). Output is deterministic for a given SEED.
set -e
setopt shwordsplit
M=${MAGICK:-/opt/homebrew/bin/magick}
HERE=${0:a:h}
D=${WORK:-$HERE/work}
mkdir -p $D
S=1024
VP="-virtual-pixel tile"
[ -f $HERE/params.env ] && source $HERE/params.env

# ---------------- parameters ----------------
: ${SEED:=41}
# surface relief (goes through the raking light)
: ${TOOTH_BLUR:=0.55}   ; : ${TOOTH_W:=0.72}
: ${GRAIN_BLUR:=1.6}    ; : ${GRAIN_W:=0.30}
: ${COARSE_BLUR:=5.0}   ; : ${COARSE_W:=0.08}
: ${ROUGH_BLUR:=40}     ; : ${ROUGH_W:=0.30}
: ${FIB_N:=900}         ; : ${FIB_LMIN:=10} ; : ${FIB_LMAX:=36}
: ${FIB_OP:=0.60}       ; : ${FIB_W:=1.20}  ; : ${FIB_BLUR:=0.40}
: ${AZ:=118}            ; : ${EL:=24}
# tone layers (added after the light, so they read as density not relief)
: ${W_RELIEF:=0.50}
: ${MOTTLE_BLUR:=32}    ; : ${MOTTLE_W:=0.28}
: ${MOTTLE2_BLUR:=11}   ; : ${MOTTLE2_W:=0.11}
: ${FIBT_N:=2400}       ; : ${FIBT_LMIN:=6}  ; : ${FIBT_LMAX:=30}
: ${FIBT_OP:=0.85}      ; : ${FIBT_W:=0.80}  ; : ${FIBT_BLUR:=0.38}
: ${FIBT_WMIN:=0.55}     ; : ${FIBT_WMAX:=1.45}
: ${FIBT_WHITE:=0.42}
: ${FIBT_LONGFRAC:=0.09}; : ${FIBT_LONGMAX:=80} ; : ${FIBT_CLUSTER:=0.55}
: ${MK_FLECK:=55} ; : ${MK_PIT:=70} ; : ${MK_BLOTCH:=14} ; : ${MK_STREAK:=7} ; : ${MK_CREASE:=2}
: ${SHARP_W:=0.55}      ; : ${SHARP_BLUR:=0.40}
: ${SOFT_W:=0.80}       ; : ${SOFT_BLUR:=8}
: ${CREASE_W:=0.55}     ; : ${CREASE_BLUR:=1.1}
# tint
: ${A_LIGHT:=0.139}     ; : ${K_DARK:=0.115}
: ${LIGHT_HEX:=#eae6de} ; : ${DARK_HEX:=#181817}
: ${CHROMA_W:=0.022}    ; : ${CHROMA_GRAIN:=0.042}
: ${OUT_L:=$HERE/../../img/paper-light.jpg}
: ${OUT_D:=$HERE/../../img/paper-dark.jpg}

# seamless normalised noise: -virtual-pixel tile makes the blur wrap
n() { $M -size ${S}x${S} xc:gray50 -seed $1 +noise Random -colorspace Gray \
         $VP -blur 0x$2 -auto-level -depth 16 "$3" ; }
# seamless layer from an MVG draw script
mvg() { $M -size ${S}x${S} xc:gray50 -draw "@$1" -colorspace Gray $VP -blur 0x$2 -depth 16 "$3" ; }
# signed deviation of a layer, scaled  (Q16-HDRI keeps the negatives)
dev() { echo "( $1 -evaluate subtract 50% -evaluate multiply $2 )" ; }

# ---------------- relief ----------------
n $((SEED+1)) $TOOTH_BLUR   $D/L_tooth.png
n $((SEED+2)) $GRAIN_BLUR   $D/L_grain.png
n $((SEED+3)) $COARSE_BLUR  $D/L_coarse.png
n $((SEED+6)) $ROUGH_BLUR   $D/L_rough.png

# where the pulp is lumpy the tooth bites harder - kills the uniform-pebble look
$M $D/L_rough.png -evaluate subtract 50% -evaluate multiply $(echo "2*$ROUGH_W"|bc -l) \
   -evaluate add 100% -depth 16 $D/mod.png
for L in tooth grain; do
  $M $D/L_$L.png -evaluate subtract 50% $D/mod.png -compose Multiply -composite \
     -evaluate add 50% -clamp -depth 16 $D/L_${L}m.png
done

python3 $HERE/fibres.py $((SEED+11)) $FIB_N $D/fib.mvg $FIB_LMIN $FIB_LMAX 0.50 1.15 $FIB_OP 0.05 60 0.5
mvg $D/fib.mvg $FIB_BLUR $D/L_fib.png

$M -size ${S}x${S} xc:gray50 -depth 16 \
   $(dev $D/L_toothm.png $TOOTH_W)  -compose Plus -composite \
   $(dev $D/L_grainm.png $GRAIN_W)  -compose Plus -composite \
   $(dev $D/L_coarse.png $COARSE_W) -compose Plus -composite \
   $(dev $D/L_fib.png    $FIB_W)    -compose Plus -composite \
   -clamp -depth 16 $D/height.png

$M $D/height.png -colorspace Gray $VP -shade ${AZ}x${EL} \
   -linear-stretch 0.3%x0.3% -depth 16 $D/relief.png

# ---------------- tone ----------------
n $((SEED+4)) $MOTTLE_BLUR  $D/L_mottle.png
n $((SEED+5)) $MOTTLE2_BLUR $D/L_mottle2.png

python3 $HERE/fibres.py $((SEED+13)) $FIBT_N $D/fibt.mvg $FIBT_LMIN $FIBT_LMAX $FIBT_WMIN $FIBT_WMAX \
        $FIBT_OP $FIBT_LONGFRAC $FIBT_LONGMAX $FIBT_CLUSTER $FIBT_WHITE
mvg $D/fibt.mvg $FIBT_BLUR $D/L_fibt.png

python3 $HERE/marks.py $((SEED+17)) $D/sharp.mvg $D/soft.mvg $D/crease.mvg \
        $MK_FLECK $MK_PIT $MK_BLOTCH $MK_STREAK $MK_CREASE
mvg $D/sharp.mvg $SHARP_BLUR $D/L_sharp.png
mvg $D/soft.mvg  $SOFT_BLUR  $D/L_soft.png
mvg $D/crease.mvg $CREASE_BLUR $D/L_crease.png

$M -size ${S}x${S} xc:gray50 -depth 16 \
   $(dev $D/relief.png    $W_RELIEF)  -compose Plus -composite \
   $(dev $D/L_mottle.png  $MOTTLE_W)  -compose Plus -composite \
   $(dev $D/L_mottle2.png $MOTTLE2_W) -compose Plus -composite \
   $(dev $D/L_fibt.png    $FIBT_W)    -compose Plus -composite \
   $(dev $D/L_sharp.png   $SHARP_W)   -compose Plus -composite \
   $(dev $D/L_soft.png    $SOFT_W)    -compose Plus -composite \
   $(dev $D/L_crease.png  $CREASE_W)  -compose Plus -composite \
   -clamp -depth 16 $D/tone.png
TM=$($M $D/tone.png -format '%[fx:mean]' info:)
echo "tone mean=$TM std=$($M $D/tone.png -format '%[fx:standard_deviation]' info:)"

# ---------------- chroma ----------------
n $((SEED+21)) 22 $D/L_chr.png
$M $D/L_chr.png          -evaluate subtract 50% -evaluate multiply $CHROMA_W -evaluate add 50% -depth 16 $D/c_R.png
$M -size ${S}x${S} xc:black -evaluate set 50% -depth 16 $D/c_G.png
$M $D/L_chr.png -negate  -evaluate subtract 50% -evaluate multiply $CHROMA_W -evaluate add 50% -depth 16 $D/c_B.png
$M $D/c_R.png $D/c_G.png $D/c_B.png -combine -colorspace sRGB -depth 16 $D/c_drift.png
$M -size ${S}x${S} xc:gray50 -seed $((SEED+22)) +noise Random $VP -blur 0x0.5 -depth 16 $D/c_grain.png
$M $D/c_drift.png $(dev $D/c_grain.png $CHROMA_GRAIN) -compose Plus -composite \
   -clamp -depth 16 $D/chroma.png

# ---------------- tint ----------------
# Mathematics: result = a*Sc*Dc + b*Sc + c*Dc + d   (Sc = tone, Dc = base tint)
# light: base * (1 + A*(tone - mean))   dark: base + K*(tone - mean)
$M -size ${S}x${S} xc:$LIGHT_HEX -depth 16 $D/tone.png \
   -compose Mathematics -define compose:args="$A_LIGHT,0,$(echo "1-$A_LIGHT*$TM"|bc -l),0" -composite \
   $D/chroma.png -compose Mathematics -define compose:args="0,1,1,-0.5" -composite \
   -clamp -colorspace sRGB -type TrueColor -strip -quality 88 -sampling-factor 1x1 "$OUT_L"

$M -size ${S}x${S} xc:$DARK_HEX -depth 16 $D/tone.png \
   -compose Mathematics -define compose:args="0,$K_DARK,1,$(echo "-1*$K_DARK*$TM"|bc -l)" -composite \
   $D/chroma.png -compose Mathematics -define compose:args="0,1,1,-0.5" -composite \
   -clamp -colorspace sRGB -type TrueColor -strip -quality 88 -sampling-factor 1x1 "$OUT_D"

for f in "$OUT_L" "$OUT_D"; do
  $M identify -format '%f %wx%h %[colorspace] %[type] colours=%k ' "$f"
  $M "$f" -colorspace Gray -format 'lum_mean=%[fx:mean*255] lum_std=%[fx:standard_deviation*255]\n' info:
done
