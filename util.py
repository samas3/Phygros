from math import *
import pygame
pygame.display.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME | pygame.HIDDEN)
w = 0
h = 0
TEXT_COLOR = (255, 255, 255)
LINE_COLOR = (254, 255, 169)
HL_COLOR = (0, 127, 0)
pygame.init()
def font(size):
    return pygame.font.Font('src/font.ttf', size)
def loadRes(name, x=0, y=0):
    img = pygame.image.load(f'src/{name}.png').convert_alpha()
    if x or y:
        img = pygame.transform.scale(img, (x, y))
    return img
res = [None, loadRes('Tap'), loadRes('Drag'), loadRes('Hold'), loadRes('Flick'), 
       loadRes('TapHL'), loadRes('DragHL'), loadRes('HoldHL'), loadRes('FlickHL'), 
       loadRes('HoldHead'), loadRes('HoldHeadHL'), loadRes('HoldEnd')]
def displayRes(id, pos, size, deg, alpha=255, color=None):
    img = res[id]
    img = pygame.transform.smoothscale(img, size)
    img.set_alpha(alpha)
    if color:
        img.fill(color, None, pygame.BLEND_RGBA_MULT)
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
    if a == b:
        return x
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
    rad = radians(deg)
    sindeg = sin(rad)
    cosdeg = cos(rad)
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
    rad = radians(note.deg)
    if fv == -1:
        rad = radians(-note.deg)
    if not note.isAbove:
        y = -y
    sindeg = sin(rad)
    cosdeg = cos(rad)
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
'''tween = [None, lambda x: x,
                      lambda x: sin(x * pi / 2),
                      lambda x: 1 - cos(x * pi / 2),
                      lambda x: 1 - (x - 1) ** 2,
                      lambda x: x ** 2,
                      lambda x: (1 - cos(x * pi)) / 2,
                      lambda x: (lambda y: y ** 2 if y < 1 else -((y - 2) ** 2 - 2) / 2)(x * 2),
                      lambda x: 1 + (x - 1) ** 3,
                      lambda x: x ** 3,
                      lambda x: 1 - (x - 1) ** 4,
                      lambda x: x ** 4,
                      lambda x: (lambda y: y ** 3 if y < 1 else ((y - 2) ** 3 + 2) / 2)(x * 2),
                      lambda x: (lambda y: y ** 4 if y < 1 else -((y - 2) ** 4 - 2) / 2)(x * 2),
                      lambda x: 1 + (x - 1) ** 5,
                      lambda x: x ** 5,
                      lambda x: 1 - 2 ** (-10 * x),
                      lambda x: 2 ** (10 * (x - 1)),
                      lambda x: sqrt(1 - (x - 1) ** 2),
                      lambda x: 1 - sqrt(1 - x ** 2),
                      lambda x: (2.70158 * x - 1) * (x - 1) ** 2 + 1,
                      lambda x: (2.70158 * x - 1.70158) * x ** 2,
                      lambda x: (lambda y: 1 - sqrt(1 - y ** 2) if y < 1 else sqrt(1 - (y - 2) ** 2) + 1)(x * 2),
                      lambda x: (14.379638 * x - 5.189819) * x ** 2 if x < 0.5 else (14.379638 * x - 9.189819) * (x - 1) ** 2 + 1,
                      lambda x: 1 - 2 ** (-10 * x)  * cos(x * pi / 0.15),
                      lambda x: 2 ** (10 * (x - 1)) * cos((x - 1) * pi / 0.15),
                      lambda x: (lambda y: y ** 2 if y < 4 else ((y - 6) ** 2) + 12 if y < 8 else ((y - 9) ** 2 + 15 if y < 10 else (y - 10.5) ** 2 + 15.75))(x * 4),
                      lambda x: 1 - tween[26](1 - x),
                      lambda x: (lambda y: tween[26](y) / 2 if y < 1 else tween[27](x - 1) / 2 + 0.5)(x * 2),
                      lambda x: 2 ** (20 * x - 11) * sin((160 * x + 1) * pi / 18) if x < 0.5 else 1 - 2 ** (9 - 20 * x) * sin((160 * x + 1) * pi / 18)]
                      '''
tween = [None, lambda t: t, # linear - 1
  lambda t: sin((t * pi) / 2), # out sine - 2
  lambda t: 1 - cos((t * pi) / 2), # in sine - 3
  lambda t: 1 - (1 - t) * (1 - t), # out quad - 4
  lambda t: t ** 2, # in quad - 5
  lambda t: -(cos(pi * t) - 1) / 2, # io sine - 6
  lambda t: 2 * (t ** 2) if t < 0.5 else 1 - (-2 * t + 2) ** 2 / 2, # io quad - 7
  lambda t: 1 - (1 - t) ** 3, # out cubic - 8
  lambda t: t ** 3, # in cubic - 9
  lambda t: 1 - (1 - t) ** 4, # out quart - 10
  lambda t: t ** 4, # in quart - 11
  lambda t: 4 * (t ** 3) if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2, # io cubic - 12
  lambda t: 8 * (t ** 4) if t < 0.5 else 1 - (-2 * t + 2) ** 4 / 2, # io quart - 13
  lambda t: 1 - (1 - t) ** 5, # out quint - 14
  lambda t: t ** 5, # in quint - 15
  lambda t: 1 if t == 1 else 1 - 2 ** (-10 * t), # out expo - 16
  lambda t: 0 if t == 0 else 2 ** (10 * t - 10), # in expo - 17
  lambda t: (1 - (t - 1) ** 2) ** 0.5, # out circ - 18
  lambda t: 1 - (1 - t ** 2) ** 0.5, # in circ - 19
  lambda t: 1 + 2.70158 * ((t - 1) ** 3) + 1.70158 * ((t - 1) ** 2), # out back - 20
  lambda t: 2.70158 * (t ** 3) - 1.70158 * (t ** 2), # in back - 21
  lambda t: (1 - (1 - (2 * t) ** 2) ** 0.5) / 2 if t < 0.5 else (((1 - (-2 * t + 2) ** 2) ** 0.5) + 1) / 2, # io circ - 22
  lambda t: ((2 * t) ** 2 * ((2.5949095 + 1) * 2 * t - 2.5949095)) / 2 if t < 0.5 else ((2 * t - 2) ** 2 * ((2.5949095 + 1) * (t * 2 - 2) + 2.5949095) + 2) / 2, # io back - 23
  lambda t: 0 if t == 0 else (1 if t == 1 else 2 ** (-10 * t) * sin((t * 10 - 0.75) * (2 * pi / 3)) + 1), # out elastic - 24
  lambda t: 0 if t == 0 else (1 if t == 1 else - 2 ** (10 * t - 10) * sin((t * 10 - 10.75) * (2 * pi / 3))), # in elastic - 25
  lambda t: 7.5625 * (t ** 2) if (t < 1 / 2.75) else (7.5625 * (t - (1.5 / 2.75)) * (t - (1.5 / 2.75)) + 0.75 if (t < 2 / 2.75) else (7.5625 * (t - (2.25 / 2.75)) * (t - (2.25 / 2.75)) + 0.9375 if (t < 2.5 / 2.75) else (7.5625 * (t - (2.625 / 2.75)) * (t - (2.625 / 2.75)) + 0.984375))), # out bounce - 26
  lambda t: 1 - (7.5625 * ((1 - t) ** 2) if ((1 - t) < 1 / 2.75) else (7.5625 * ((1 - t) - (1.5 / 2.75)) * ((1 - t) - (1.5 / 2.75)) + 0.75 if ((1 - t) < 2 / 2.75) else (7.5625 * ((1 - t) - (2.25 / 2.75)) * ((1 - t) - (2.25 / 2.75)) + 0.9375 if ((1 - t) < 2.5 / 2.75) else (7.5625 * ((1 - t) - (2.625 / 2.75)) * ((1 - t) - (2.625 / 2.75)) + 0.984375)))), # in bounce - 27
  lambda t: (1 - (7.5625 * ((1 - 2 * t) ** 2) if ((1 - 2 * t) < 1 / 2.75) else (7.5625 * ((1 - 2 * t) - (1.5 / 2.75)) * ((1 - 2 * t) - (1.5 / 2.75)) + 0.75 if ((1 - 2 * t) < 2 / 2.75) else (7.5625 * ((1 - 2 * t) - (2.25 / 2.75)) * ((1 - 2 * t) - (2.25 / 2.75)) + 0.9375 if ((1 - 2 * t) < 2.5 / 2.75) else (7.5625 * ((1 - 2 * t) - (2.625 / 2.75)) * ((1 - 2 * t) - (2.625 / 2.75)) + 0.984375))))) / 2 if t < 0.5 else (1 +(7.5625 * ((2 * t - 1) ** 2) if ((2 * t - 1) < 1 / 2.75) else (7.5625 * ((2 * t - 1) - (1.5 / 2.75)) * ((2 * t - 1) - (1.5 / 2.75)) + 0.75 if ((2 * t - 1) < 2 / 2.75) else (7.5625 * ((2 * t - 1) - (2.25 / 2.75)) * ((2 * t - 1) - (2.25 / 2.75)) + 0.9375 if ((2 * t - 1) < 2.5 / 2.75) else (7.5625 * ((2 * t - 1) - (2.625 / 2.75)) * ((2 * t - 1) - (2.625 / 2.75)) + 0.984375))))) / 2, # io bounce - 28
  lambda t: 0 if t == 0 else (1 if t == 0 else (-2 ** (20 * t - 10) * sin((20 * t - 11.125) * ((2 * pi) / 4.5))) / 2 if t < 0.5 else (2 ** (-20 * t + 10) * sin((20 * t - 11.125) * ((2 * pi) / 4.5))) / 2 + 1) # io elastic - 29
  ]