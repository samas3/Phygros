import pygame
import util
import sound
SHOW_ID = False
class Note():
    def __init__(self, noteJson, line, isAbove):
        self.type = int(noteJson['type'])
        self.time = float(noteJson['time'])
        self.positionX = float(noteJson['positionX'])
        self.holdTime = float(noteJson.get('holdTime', 0))
        self.speed = float(noteJson['speed'])
        self.floorPosition = float(noteJson['floorPosition'])
        self.line = line
        self.isAbove = isAbove
        self.scale = 1

        self.x = 0
        self.y = 0
        self.deg = 0
        self.scored = 0
        self.id = 0
        self.hl = False
        self.pos = []
        self.hit = False
        self.realTime = util.timeToSec(self.line.bpm, self.time)
        if SHOW_ID:
            self.id_text = util.font(20).render(f'{self.line.id},{self.id}', False, (255, 0, 0))
    def __repr__(self):
        return f'{[None, "Tap", "Drag", "Hold", "Flick"][self.type]}[id={self.line.id},{self.id}]'
    def render(self, screen, time, fv, options):
        self.deg = -self.line.deg
        if 'notescale' in options:
            note.scale *= float(options['notescale'])
        if self.type != 3:
            yDist = self.speed * (self.floorPosition - self.line.floorPosition)
            linePos = util.calcNotePos(self, yDist, fv)
            self.pos = linePos
            note(screen, *linePos, self)
            if SHOW_ID:
                screen.blit(self.id_text, linePos)
        else:
            yDist = self.floorPosition - self.line.floorPosition
            headPos = util.calcNotePos(self, max(0, yDist), fv)
            if time <= self.time:
                yDistEnd = yDist + self.speed * util.timeToSec(self.line.bpm, self.holdTime)
            elif self.time < time <= self.time + self.holdTime:
                yDistEnd = self.speed * util.timeToSec(self.line.bpm, self.time + self.holdTime - time)
            else:
                yDistEnd = 0
            endPos = util.calcNotePos(self, yDistEnd, fv)
            hold(screen, *headPos, *endPos, self)
            if util.inrng(time, self.time, self.time + self.holdTime):
                if not self.hit:
                    self.hit = True
                    sound.play(0, options)
                hitPos = util.calcNotePos(self, 0, fv)
                hit(screen, *hitPos, self.deg, 3, options)
def note(screen, x, y, note):
    scale = note.scale
    width, height = screen.get_size()
    lu = [x - 0.07 * height * scale, y - 0.005 * height]
    rd = [x + 0.07 * height * scale, y + 0.005 * height]
    if not util.intersect(*lu, *rd, 0, 0, width, height):
        return
    spirit, rect = util.displayRes(note.type + (4 if note.hl else 0), (x, y), (int(0.14 * height * scale), int(0.01 * height)), -note.deg)
    screen.blit(spirit, rect)
def hold(screen, headX, headY, endX, endY, note):
    width, height = screen.get_size()
    scale = note.scale
    lux = min(headX, endX)
    luy = min(headY, endY)
    rdx = max(headX, endX)
    rdy = max(headY, endY)
    if not util.intersect(lux, luy, rdx, rdy, 0, 0, width, height):
        return
    s_head, r_head = util.displayRes((10 if note.hl else 9), (headX, headY), (int(0.14 * height * scale), int(0.01 * height)), -note.deg)
    screen.blit(s_head, r_head)
    s_body, r_body = util.displayRes((7 if note.hl else 3), ((headX + endX) / 2, (headY + endY) / 2), (int(0.14 * height * scale), abs(endY - headY)), -note.deg)
    screen.blit(s_body, r_body)
    s_end, r_end = util.displayRes(11, (endX, endY - int(0.005 * height * scale)), (int(0.13 * height * scale), int(0.01 * height)), -note.deg)
    screen.blit(s_end, r_end)
    #pygame.draw.line(screen, (255, 255, 255), (headX, headY), (endX, endY), int(0.01 * height)) # holdBody
def hit(screen, x, y, deg, type, options):
    scr = pygame.Surface((20, 20), pygame.SRCALPHA)
    scr.fill(util.LINE_COLOR)
    rotated = pygame.transform.rotate(scr, deg)
    rect = rotated.get_rect(center=(x, y))
    screen.blit(rotated, rect)
    if type != 3:
        sound.play([1, 2, 4].index(type), options)