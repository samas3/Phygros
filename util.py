import math
w = 0
h = 0
TEXT_COLOR = (200, 200, 200, 200)
LINE_COLOR = (254, 255, 169)
FONT = 'src/font.ttf'
def init(w_, h_):
    global w, h
    w = w_
    h = h_
def eq(a, b, eps=1e-2):
    return abs(a - b) < eps
def rng(val, a, b, x, y):
    return (val - a) / (b - a) * (y - x) + x
def inrng(val, a, b):
    return a <= val <= b
def toChartPos(x, y, fv):
    if fv == 1:
        x /= 880
        y /= 520
    if fv == 1 or fv == 3:
        x *= w
        y *= h
    else:
        x *= 0.1 * h + 0.5 * w
        y *= 0.1 * h + 0.5 * h
    return [x, y]
def toPygamePos(x, y):
    return [x, h - y]
def toXYUnit(x, y):
    return [x * 9 / 160 * w, y * 3 / 5 * h]
def secToTime(bpm, time):
    return time * bpm / 1.875
def timeToSec(bpm, time):
    return time * 1.875 / bpm
def rotate(cx, cy, x, y, deg):
    newx = math.cos(math.radians(deg)) * (x - cx) - math.sin(math.radians(deg)) * (y - cy) + cx
    newy = math.sin(math.radians(deg)) * (x - cx) + math.cos(math.radians(deg)) * (y - cy) + cy
    return [newx, newy]
def ftime(tm):
    return f'{int(tm // 60)}:{f"0{int(tm % 60)}"[-2:]}'
def parse(st):
    lst = st.split(';')
    opt = {}
    for i in lst:
        if '=' in i:
            tmp = i.split('=')
            opt[tmp[0]] = tmp[1]
        else:
            opt[i] = 'True'
    return opt
def clamp(val, x, y):
    return x if val < x else (y if val > y else val)
def calcNotePos(note, yDist, fv):
    linePos = toChartPos(note.line.x, note.line.y, fv)
    noteOffset = toXYUnit(note.positionX, yDist)
    x, y = noteOffset
    y *= (1 if note.isAbove else -1)
    tandeg = math.tan(math.radians(note.deg))
    linePos[1] += (y - x * tandeg) * math.cos(math.radians(note.deg))
    cosdeg = math.cos(math.radians(note.deg))
    if abs(cosdeg) < 1e-5:
        cosdeg = cosdeg / abs(cosdeg) * 1e-5
    if abs(tandeg) > 1e5:
        tandeg = tandeg / abs(tandeg) * 1e5
    linePos[0] += x / cosdeg + (y - x * tandeg) * math.sin(math.radians(note.deg))
    linePos = toPygamePos(*linePos)
    return linePos
def onScreen(x, y):
    return inrng(x, 0, w) and inrng(y, 0, h)
def intersect(lux1, luy1, rdx1, rdy1, lux2, luy2, rdx2, rdy2):
    # 判断前4个坐标构成的矩形是否与后4个坐标构成的矩形相交
    return abs(lux2 + rdx2 - lux1 - rdx1) <= (rdx1 - lux1 + rdx2 - lux2) and abs(luy2 + rdy2 - luy1 - rdy1) <= (rdy1 - luy1 + rdy2 - luy2)