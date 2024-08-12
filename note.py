import pygame
import util
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

        self.x = 0
        self.y = 0
        self.deg = 0
        self.scored = 0
        self.id = 0
        self.hl = False
        self.pos = []
    def find_near(self, chart):
        for i in chart.all_notes:
            if util.eq(util.timeToSec(self.line.bpm, self.time), util.timeToSec(i.line.bpm, i.time), eps=0.02) and (self.id != i.id or self.line.id != i.line.id):
                self.hl = i.hl = True
    def render(self, screen, time, fv, options):
        self.deg = -self.line.deg
        if 'notescale' in options:
            scale = float(options['notescale'])
        else:
            scale = 1
        if self.type != 3:
            yDist = self.speed * (self.floorPosition - self.line.floorPosition)
            linePos = util.calcNotePos(self, yDist, fv)
            self.pos = linePos
            note(screen, *linePos, self, scale)
            '''if 'showid' in options:
                font = pygame.font.Font('font.ttf', 20)
                id_text = font.render(str(self.id), False, (255, 255, 255))
                screen.blit(id_text, linePos)'''   # 性能代价太大
        else:
            yDist = self.floorPosition - self.line.floorPosition
            headPos = util.calcNotePos(self, max(0, yDist), fv)
            if time <= self.time:
                yDistEnd = yDist + self.speed * self.holdTime * 1.875 / self.line.bpm
            elif self.time < time <= self.time + self.holdTime:
                yDistEnd = self.speed * (self.time + self.holdTime - time) * 1.875 / self.line.bpm
            else:
                yDistEnd = 0
            endPos = util.calcNotePos(self, yDistEnd, fv)
            hold(screen, *headPos, *endPos, self, scale)
            if time > self.time + self.holdTime and not self.scored:
                self.scored = 1
            if util.inrng(time, self.time, self.time + self.holdTime):
                if not self.scored:
                    hitPos = util.calcNotePos(self, 0, fv)
                    hit(screen, *hitPos, self.deg)
def note(screen, x, y, note, scale):
    width, height = screen.get_size()
    if not util.onScreen(x, y):
        return
    left = util.rotate(x, y, x - 0.07 * height * scale, y, note.deg)
    right = util.rotate(x, y, x + 0.07 * height * scale, y, note.deg)
    color = [None, (10, 195, 255), (240, 237, 105), None, (254, 67, 101)]
    pygame.draw.line(screen, color[note.type], left, right, int(0.01 * height))
    if note.hl:
        pygame.draw.circle(screen, util.LINE_COLOR, (int(x), int(y)), int(0.02 * height * scale))
def hold(screen, headX, headY, endX, endY, note, scale):
    width, height = screen.get_size()
    if not util.onScreen(headX, headY):
        return
    '''scr = pygame.Surface((0.14 * height, math.sqrt((headX - endX) ** 2 + (headY - endY) ** 2)), pygame.SRCALPHA)
    scr.fill((10, 195, 255))
    midX = (headX + endX) / 2
    midY = (headY + endY) / 2
    rotated = pygame.transform.rotate(scr, note.deg)
    rect = rotated.get_rect(center=(midX, midY))
    screen.blit(rotated, rect)''' # 同上
    pygame.draw.line(screen, (10, 195, 255), (headX, headY), (endX, endY), int(0.14 * height * scale))
    if note.hl:
        pygame.draw.circle(screen, util.LINE_COLOR, (int(headX), int(headY)), int(0.02 * height * scale))
def hit(screen, x, y, deg):
    scr = pygame.Surface((20, 20), pygame.SRCALPHA)
    scr.fill(util.LINE_COLOR)
    rotated = pygame.transform.rotate(scr, deg)
    rect = rotated.get_rect(center=(x, y))
    screen.blit(rotated, rect)