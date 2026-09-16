"""Place strands and blobs deliberately straddling each edge/corner and check the
ink reappears on the opposite side, i.e. the tile really wraps."""
import sys, subprocess, struct
sys.path.insert(0,'.')
from wrap import W, offsets
M='/opt/homebrew/bin/magick'

cases = {
 'right edge'  : [(1016,500),(1030,500),(1044,500)],
 'left edge'   : [(8,300),(-6,300),(-20,300)],
 'bottom edge' : [(500,1016),(500,1030),(500,1044)],
 'top edge'    : [(300,8),(300,-6),(300,-20)],
 'corner BR'   : [(1016,1016),(1030,1030),(1044,1044)],
 'corner TL'   : [(8,8),(-6,-6),(-20,-20)],
}
lines=['fill none','stroke-linecap round','stroke #ffffff','stroke-width 3','stroke-opacity 1']
for pts in cases.values():
    for dx,dy in offsets(pts, 5):
        lines.append("path 'M %.1f,%.1f Q %.1f,%.1f %.1f,%.1f'" %
                     (pts[0][0]+dx,pts[0][1]+dy,pts[1][0]+dx,pts[1][1]+dy,pts[2][0]+dx,pts[2][1]+dy))
open('/tmp/tw.mvg','w').write('\n'.join(lines)+'\n')
subprocess.run([M,'-size','1024x1024','xc:black','-draw','@/tmp/tw.mvg','-colorspace','Gray','/tmp/tw.png'],check=True)
o=subprocess.run([M,'/tmp/tw.png','-depth','8','gray:-'],capture_output=True).stdout
px=[o[y*W:(y+1)*W] for y in range(W)]

def ink(x0,x1,y0,y1):
    return max(px[y][x] for y in range(y0,y1) for x in range(x0,x1))

checks = [
 ('right->left  ', ink(0,28,480,520)),
 ('left->right  ', ink(996,1023,280,320)),
 ('bottom->top  ', ink(480,520,0,28)),
 ('top->bottom  ', ink(280,320,996,1023)),
 ('cornerBR->TL ', ink(0,28,0,28)),
 ('cornerTL->BR ', ink(996,1023,996,1023)),
]
ok=True
for name,v in checks:
    good = v > 100
    ok &= good
    print('  %s wrapped ink=%3d  %s' % (name, v, 'OK' if good else 'MISSING'))
print('WRAP TEST:', 'PASS' if ok else 'FAIL')
