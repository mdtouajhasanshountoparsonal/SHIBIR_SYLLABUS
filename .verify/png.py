import sys, zlib, struct

TARGET = (190, 61, 84)
TOL = 28


def load_png(path):
    data = open(path, 'rb').read()
    assert data[:8] == b'\x89PNG\r\n\x1a\n', path
    pos = 8
    width = height = bitdepth = colortype = None
    idat = bytearray()
    while pos < len(data):
        (length,) = struct.unpack('>I', data[pos:pos + 4])
        ctype = data[pos + 4:pos + 8]
        chunk = data[pos + 8:pos + 8 + length]
        pos += 12 + length
        if ctype == b'IHDR':
            width, height, bitdepth, colortype = struct.unpack('>IIBB', chunk[:10])
        elif ctype == b'IDAT':
            idat += chunk
        elif ctype == b'IEND':
            break
    assert bitdepth == 8 and colortype in (2, 6), (bitdepth, colortype)
    bpp = 3 if colortype == 2 else 4
    raw = zlib.decompress(bytes(idat))
    stride = width * bpp
    out = bytearray(height * stride)
    prev = bytearray(stride)
    pos = 0
    for y in range(height):
        f = raw[pos]; pos += 1
        line = bytearray(raw[pos:pos + stride]); pos += stride
        if f == 1:
            for i in range(bpp, stride):
                line[i] = (line[i] + line[i - bpp]) & 0xFF
        elif f == 2:
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 0xFF
        elif f == 3:
            for i in range(stride):
                a = line[i - bpp] if i >= bpp else 0
                line[i] = (line[i] + ((a + prev[i]) >> 1)) & 0xFF
        elif f == 4:
            for i in range(stride):
                a = line[i - bpp] if i >= bpp else 0
                b = prev[i]
                c = prev[i - bpp] if i >= bpp else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (line[i] + pr) & 0xFF
        out[y * stride:(y + 1) * stride] = line
        prev = line
    return width, height, bpp, out


def highlight(path, target=TARGET, tol=TOL, ymin=0, ymax=10 ** 9):
    w, h, bpp, px = load_png(path)
    tr, tg, tb = target
    count = 0
    sx = sy = 0
    minx = miny = 10 ** 9
    maxx = maxy = -1
    for y in range(max(0, ymin), min(h, ymax + 1)):
        row = y * w * bpp
        for x in range(w):
            i = row + x * bpp
            r, g, b = px[i], px[i + 1], px[i + 2]
            if abs(r - tr) <= tol and abs(g - tg) <= tol and abs(b - tb) <= tol:
                count += 1
                sx += x; sy += y
                if x < minx: minx = x
                if x > maxx: maxx = x
                if y < miny: miny = y
                if y > maxy: maxy = y
    if count == 0:
        return dict(n=0)
    return dict(n=count, cx=round(sx / count, 1), cy=round(sy / count, 1),
                bbox=(minx, miny, maxx, maxy))


if __name__ == '__main__':
    ymin = int(sys.argv[1]) if len(sys.argv) > 2 else 0
    for p in sys.argv[2:]:
        print(p, highlight(p, ymin=ymin))
