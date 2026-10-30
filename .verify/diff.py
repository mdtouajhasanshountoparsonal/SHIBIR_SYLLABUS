import sys
from png import load_png


def diff(a, b, thresh=30):
    wa, ha, bpp, pa = load_png(a)
    wb, hb, bpp2, pb = load_png(b)
    w, h = wa, ha
    count = 0
    minx = miny = 10 ** 9
    maxx = maxy = -1
    rows = {}
    for y in range(h):
        row = y * w * bpp
        for x in range(w):
            i = row + x * bpp
            d = abs(pa[i] - pb[i]) + abs(pa[i + 1] - pb[i + 1]) + abs(pa[i + 2] - pb[i + 2])
            if d > thresh:
                count += 1
                if x < minx: minx = x
                if x > maxx: maxx = x
                if y < miny: miny = y
                if y > maxy: maxy = y
                rows[y] = rows.get(y, 0) + 1
    print(f'{a} vs {b}: changed={count} bbox={(minx, miny, maxx, maxy) if count else None}')
    # print row bands with many changes
    bands = []
    cur = None
    for y in sorted(rows):
        if cur and y == cur[1] + 1:
            cur = (cur[0], y)
        else:
            if cur: bands.append(cur)
            cur = (y, y)
    if cur: bands.append(cur)
    for y1, y2 in bands:
        n = sum(rows[y] for y in range(y1, y2 + 1))
        print(f'  rows {y1}-{y2}: {n} px')


if __name__ == '__main__':
    diff(sys.argv[1], sys.argv[2])
