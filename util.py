import math
import pygame
import numpy as np
pygame.display.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)
w = 0
h = 0
TEXT_COLOR = (255, 255, 255)
LINE_COLOR = (254, 255, 169)
HL_COLOR = (0, 127, 0)
FONT = 'src/font.ttf'
def loadRes(name, x=0, y=0):
    img = pygame.image.load(f'src/{name}.png').convert_alpha()
    if x or y:
        img = pygame.transform.scale(img, (x, y))
    return img
res = [None, loadRes('Tap'), loadRes('Drag'), loadRes('Hold'), loadRes('Flick'), loadRes('TapHL'), loadRes('DragHL'), None, loadRes('FlickHL')]
def displayRes(id, pos, size, deg, alpha=255, color=None):
    img = res[id]
    img = pygame.transform.scale(img, size)
    img.set_alpha(alpha)
    if color:
        img.fill(color, None, pygame.BLEND_RGBA_MULT)
    #img = rotate_image(img, deg)
    img = pygame.transform.rotate(img, deg)
    rect = img.get_rect()
    rect.center = pos
    return [img, rect]
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
def toXYUnitRPE(x, y):
    return [x / 1350 * w, y * 3 / 5 * h]
def secToTime(bpm, time):
    return time * bpm / 1.875
def timeToSec(bpm, time):
    return time * 1.875 / bpm
def rotate(cx, cy, x, y, deg):
    rad = math.radians(deg)
    sindeg = math.sin(rad)
    cosdeg = math.cos(rad)
    newx = cosdeg * (x - cx) - sindeg * (y - cy) + cx
    newy = sindeg * (x - cx) + cosdeg * (y - cy) + cy
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
    if fv == -1: # rpe
        linePos = toChartPos(note.line.x, note.line.y, 3)
    x, y = toXYUnit(note.positionX, yDist)
    rad = math.radians(note.deg)
    if fv == -1:
        rad = math.radians(-note.deg)
    if not note.isAbove:
        y = -y
    sindeg = math.sin(rad)
    cosdeg = math.cos(rad)
    if abs(cosdeg) < 1e-5:
        cosdeg = cosdeg / abs(cosdeg) * 1e-5
    tandeg = sindeg / cosdeg
    linePos[1] += y * cosdeg - x * sindeg
    linePos[0] += x / cosdeg + (y - x * tandeg) * sindeg
    linePos = toPygamePos(*linePos)
    return linePos
def intersect(lux1, luy1, rdx1, rdy1, lux2, luy2, rdx2, rdy2):
    # 判断前4个坐标构成的矩形是否与后4个坐标构成的矩形相交
    return abs(lux2 + rdx2 - lux1 - rdx1) <= (rdx1 - lux1 + rdx2 - lux2) and abs(luy2 + rdy2 - luy1 - rdy1) <= (rdy1 - luy1 + rdy2 - luy2)