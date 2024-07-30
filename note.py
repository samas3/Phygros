import pygame
import util
import math
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
    def render(self, screen, time, fv, options):
        self.deg = -self.line.deg
        if self.type != 3:
            yDist = self.speed * (self.floorPosition - self.line.floorPosition)
            if yDist < 0:
                return
            linePos = util.calcNotePos(self, yDist, fv)
            note(screen, *linePos, self.deg, self.type)
            if util.eq(self.time, time, eps=5):
                if not self.scored:
                    hit(screen, *linePos, self.deg)
                self.scored = 1
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
            hold(screen, *headPos, *endPos, self.deg)
            if time > self.time + self.holdTime:
                self.scored = 1
            if util.inrng(time, self.time, self.time + self.holdTime):
                if not self.scored:
                    hitPos = util.calcNotePos(self, 0, fv)
                    hit(screen, *hitPos, self.deg)
def note(screen, x, y, deg, type):
    width, height = screen.get_size()
    if not util.inrng(x, 0, width) or not util.inrng(y, 0, height):
        return
    left = util.rotate(x, y, x - 0.07 * height, y, deg)
    right = util.rotate(x, y, x + 0.07 * height, y, deg)
    color = [None, (10, 195, 255), (240, 237, 105), None, (254, 67, 101)]
    pygame.draw.line(screen, color[type], left, right, int(0.01 * height))
def hold(screen, headX, headY, endX, endY, deg):
    width, height = screen.get_size()
    if not util.inrng(headX, 0, width) or not util.inrng(headY, 0, height):
        return
    scr = pygame.Surface((0.14 * height, math.sqrt((headX - endX) ** 2 + (headY - endY) ** 2)), pygame.SRCALPHA)
    scr.fill((10, 195, 255))
    midX = (headX + endX) / 2
    midY = (headY + endY) / 2
    rotated = pygame.transform.rotate(scr, deg)
    rect = rotated.get_rect(center=(midX, midY))
    screen.blit(rotated, rect)
def hit(screen, x, y, deg):
    color = (254, 255, 169)
    scr = pygame.Surface((20, 20), pygame.SRCALPHA)
    scr.fill(color)
    rotated = pygame.transform.rotate(scr, deg)
    rect = rotated.get_rect(center=(x, y))
    screen.blit(rotated, rect)