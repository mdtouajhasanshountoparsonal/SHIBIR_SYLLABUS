import re, html, subprocess, time

PKG = 'com.example.shibir_syllabus_tracker'
SHOT_DIR = '/home/shanto/Flutter_desing/SHIBIR_SYLLABUS/.verify'


def sh(*args):
    return subprocess.run(args, capture_output=True, text=True).stdout


def dump():
    sh('adb', 'shell', 'uiautomator', 'dump', '/sdcard/ui.xml')
    xml = sh('adb', 'exec-out', 'cat', '/sdcard/ui.xml')
    out = []
    for m in re.finditer(
            r'content-desc="([^"]*)"[^>]*?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', xml):
        d = html.unescape(m.group(1))
        x1, y1, x2, y2 = map(int, m.groups()[1:])
        if d.strip():
            out.append((d, (x1 + x2) // 2, (y1 + y2) // 2, x1, y1, x2, y2))
    return out


def clickable():
    sh('adb', 'shell', 'uiautomator', 'dump', '/sdcard/ui.xml')
    xml = sh('adb', 'exec-out', 'cat', '/sdcard/ui.xml')
    out = []
    for m in re.finditer(r'<node[^>]*>', xml):
        n = m.group(0)
        if 'clickable="true"' not in n:
            continue
        b = re.search(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', n)
        d = re.search(r'content-desc="([^"]*)"', n)
        if not b:
            continue
        x1, y1, x2, y2 = map(int, b.groups())
        out.append((html.unescape(d.group(1)) if d else '',
                    (x1 + x2) // 2, (y1 + y2) // 2, x1, y1, x2, y2))
    return out


def find(kw, elems=None):
    for e in (elems or dump()):
        if kw in e[0]:
            return e
    return None


def tap(x, y, wait=2.0):
    sh('adb', 'shell', 'input', 'tap', str(x), str(y))
    time.sleep(wait)


def swipe(x1, y1, x2, y2, ms=400):
    sh('adb', 'shell', 'input', 'swipe', str(x1), str(y1), str(x2), str(y2), str(ms))
    time.sleep(2)


def shot(name):
    path = f'{SHOT_DIR}/{name}.png'
    with open(path, 'wb') as f:
        subprocess.run(['adb', 'exec-out', 'screencap', '-p'], stdout=f)
    return path


def start():
    sh('adb', 'shell', 'am', 'force-stop', PKG)
    sh('adb', 'shell', 'am', 'start', '-n', f'{PKG}/.MainActivity')
    time.sleep(6)
