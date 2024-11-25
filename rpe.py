import util
import pygame
import sound
from math import *
from scipy.optimize import bisect
DEBUG = False
DEBUG_NOTE = False
class RPE:
    def __init__(self, chart):
        self.BPMList = BPMList(chart['BPMList'])
        self.meta = chart['META']
        self.info = {k: self.meta[k] for k in self.meta if k in ['name', 'level', 'charter', 'composer', 'illustration']}
        self.offset = self.meta['offset'] / 1000
        self.judgeLineList = chart['judgeLineList']
        self.lineList = []
        self.parseLine()
        self.all_notes = []
        for i in self.lineList:
            self.all_notes += filter(lambda x: not x.isFake, i.noteList)
        self.notes = len(self.all_notes)
        self.all_notes.sort(key=lambda x: x.endTime)
        self.highlight()
        self.jm = RPEJudgeManager(self.all_notes)
    def parseLine(self):
        for i, line in enumerate(self.judgeLineList):
            self.lineList.append(Line(line, self, i))
    def highlight(self):
        notes = self.all_notes
        hl = []
        start = 0
        for end in range(len(notes)):
            while start < end and notes[end].realTime - notes[start].realTime > 0.01:
                start += 1
            if start == end:
                continue
            hl += notes[start: end + 1]
        for i in hl:
            i.hl = True
    def render(self, time, screen, options):
        for i in self.all_notes:
            chartTime = util.secToTime(i.line.bpm, time)
            if i.endTime >= chartTime:
                i.render(chartTime, screen)
        for i in self.lineList:
            i.render(time, screen)
        font = util.font(20)
        combo_font = util.font(16)
        combo_font2 = util.font(26)
        name = font.render(self.info['name'], False, util.TEXT_COLOR)
        lvl = font.render(self.info['level'], False, util.TEXT_COLOR)
        width, height = screen.get_size()
        screen.blit(name, (10, height - 30))
        screen.blit(lvl, (width - lvl.get_width() - 10, height - 30))
        self.jm.check(time, screen)
        combo_num = combo_font2.render(str(self.jm.combo), False, util.TEXT_COLOR)
        combo_text = combo_font.render('AUTOPLAY', False, util.TEXT_COLOR)
        if self.jm.combo > 2:
            screen.blit(combo_num, (width / 2 - combo_num.get_width() / 2, 10))
            screen.blit(combo_text, (width / 2 - combo_text.get_width() / 2, 40))
        try:
            score_num = combo_font2.render(str(round(self.jm.combo / self.notes * 1e6)).zfill(7), False, util.TEXT_COLOR)
        except:
            score_num = combo_font2.render('0000000', False, util.TEXT_COLOR)
        screen.blit(score_num, (width - score_num.get_width() - 10, 10))
class Line:
    def __init__(self, line, chart, id):
        self.chart = chart
        self.id = id
        self.bpm = self.chart.BPMList.baseBPM
        #self.anchor = line['anchor']
        self.events = line['eventLayers'][0]
        '''for i, j in enumerate(line['eventLayers']):
            if i == 0 or not j:
                continue
            for k, l in j.items():
                self.events[k] += l''' # fuck eventLayers
        #self.extended = line['extended']
        self.notes = line.get('notes', [])
        self.noteList = []
        self.speedEvents = []
        self.moveXEvents = []
        self.moveYEvents = []
        self.rotateEvents = []
        self.alphaEvents = []
        '''self.colorEvents = []
        self.scaleXEvents = []
        self.scaleYEvents = []
        self.textEvents = []'''
        self.parseEvent()
        self.parseNote()
        self.floorPosition = 0
        self.x = 0
        self.y = 0
        self.deg = 0
        self.alpha = 0
        if DEBUG:
            self.id_text = util.font(20).render(f'{self.id}', False, (255, 0, 255))
    def parseNote(self):
        id = 0
        for note in self.notes:
            self.noteList.append(Note(note, self, id))
            id += 1
    def convertSpeedEvent(self):
        speedEvents = []
        for i in self.events['speedEvents']:
            speedEvents.append(Event(i, self))
        events = []
        for i in speedEvents:
            events.append({'time': i.startTime, 'value': i.start})
            if i.startTime != i.endTime and i.start != i.end:
                t1 = (i.end - i.start) / (i.endTime - i.startTime)
                for j in range(int(i.startTime), int(i.endTime)):
                    events.append({'time': j + 1, 'value': i.start + t1 * (j + 1 - i.startTime)})
            if i.start == i.end:
                events.append({'time': i.endTime, 'value': i.end})
        self.speedEvents = sorted(events, key=lambda x: x['time'])
    def parseEvent(self):
        self.convertSpeedEvent()
        floorPos = 0
        events = []
        for i, j in enumerate(self.speedEvents):
            start = max(0, j['time'])
            end = self.speedEvents[i + 1]['time'] if i + 1 < len(self.speedEvents) else 1e9
            if start == end:
                continue
            val = j['value'] * 11 / 45
            pos = floorPos
            floorPos += (end - start) * val / self.bpm * 1.875
            events.append({'startTime': start, 'endTime': end, 'value': val, 'floorPosition': pos})
        self.speedEvents = events
        self.speedEvents.sort(key=lambda x: x['startTime'])
        for i, j in enumerate(self.events['moveXEvents']):
            j['start'] = (j['start'] + 675) / 1350
            j['end'] = (j['end'] + 675) / 1350
            self.moveXEvents.append(Event(j, self))
        self.moveXEvents.sort(key=lambda x: x.startTime)
        for i, j in enumerate(self.events['moveYEvents']):
            j['start'] = (j['start'] + 450) / 900
            j['end'] = (j['end'] + 450) / 900
            self.moveYEvents.append(Event(j, self))
        self.moveYEvents.sort(key=lambda x: x.startTime)
        for i in self.moveYEvents:
            print(i.startTime, i.endTime, i.start, i.end)
        for i, j in enumerate(self.events['rotateEvents']):
            self.rotateEvents.append(Event(j, self))
        self.rotateEvents.sort(key=lambda x: x.startTime)
        for i, j in enumerate(self.events['alphaEvents']):
            self.alphaEvents.append(Event(j, self))
        self.alphaEvents.sort(key=lambda x: x.startTime)
    def render(self, time, screen):
        time = util.secToTime(self.bpm, time)
        for i in self.noteList:
            i.render(time, screen)
        for i in self.speedEvents:
            if time > i['endTime']:
                self.speedEvents.remove(i)
                continue
            if time < i['startTime']:
                break
            self.floorPosition = i['floorPosition'] + i['value'] * util.timeToSec(self.bpm, time - i['startTime'])
            break
        for i in self.alphaEvents:
            if time > i.endTime:
                self.alpha = Easing(i).getValue(i.endTime)
                self.alphaEvents.remove(i)
                continue
            if time < i.startTime:
                break
            self.alpha = Easing(i).getValue(time)
            break
        for i in self.moveXEvents:
            if time > i.endTime:
                self.x = Easing(i).getValue(i.endTime)
                self.moveXEvents.remove(i)
                continue
            if time < i.startTime:
                break
            self.x = Easing(i).getValue(time)
            break
        for i in self.moveYEvents:
            if time > i.endTime:
                self.y = Easing(i).getValue(i.endTime)
                self.moveYEvents.remove(i)
                continue
            if time < i.startTime:
                break
            self.y = Easing(i).getValue(time)
            print(time, self.y)
            break
        for i in self.rotateEvents:
            if time > i.endTime:
                self.deg = Easing(i).getValue(i.endTime)
                self.rotateEvents.remove(i)
                continue
            if time < i.startTime:
                break
            self.deg = Easing(i).getValue(time)
            break
        width, height = screen.get_size()
        cx = self.x
        cy = self.y
        deg = self.deg
        originalPos = util.toPygamePos(*util.toChartPos(cx, cy, 3))
        pos = originalPos[:]
        pos[0] -= 2.88 * height
        left = util.rotate(*originalPos, *pos, deg)
        pos[0] += 5.76 * height
        right = util.rotate(*originalPos, *pos, deg)
        alpha = util.clamp(self.alpha, 0, 255)
        color = (*util.LINE_COLOR, alpha)
        if alpha > 0:
            pygame.draw.line(screen, color, left, right, int(0.0075 * height))
        if self.id == 0 and DEBUG:
            screen.blit(self.id_text, util.toPygamePos(*util.toChartPos(cx, cy, 3)))
            font = util.font(20)
            lineInfo = font.render(f'ID: {int(self.id)}', False, (255, 255, 255))
            screen.blit(lineInfo, (10, 50))
            lineInfo = font.render(f'Time: {int(time)}', False, (255, 255, 255))
            screen.blit(lineInfo, (10, 65))
            lineInfo = font.render(f'FloorPos: {int(self.floorPosition)}', False, (255, 255, 255))
            screen.blit(lineInfo, (10, 80))
            lineInfo = font.render(f'Rotation: {int(self.deg)} deg', False, (255, 255, 255))
            screen.blit(lineInfo, (10, 95))
            lineInfo = font.render(f'Alpha: {int(alpha)}', False, (255, 255, 255))
            screen.blit(lineInfo, (10, 110))
            lineInfo = font.render(f'XY: {round(cx, 2)} {round(cy, 2)}', False, (255, 255, 255))
            screen.blit(lineInfo, (10, 125))
class Easing:
    def __init__(self, event):
        self.easingType = event.easingType
        self.start = event.start
        self.end = event.end
        self.startTime = event.startTime
        self.endTime = event.endTime
        self.points = event.bezierPoints
        self.easingLeft = event.easingLeft
        self.easingRight = event.easingRight
        if event.bezier:
            self.easingType = -1
    def getValue(self, time):
        if time < self.startTime:
            return self.start
        elif time > self.endTime:
            return self.end
        else:
            if self.easingType == -1: # bezier curve
                return self.bezier(time)
            t = (time - self.startTime) / (self.endTime - self.startTime) * (self.easingRight - self.easingLeft) + self.easingLeft
            return util.tween[self.easingType](t) * (self.end - self.start) + self.start
    def bezier(self, time):
        t = (time - self.startTime) / (self.endTime - self.startTime)
        p1, p2, p3, p4 = self.points
        def bezierX(t, p1, p2, p3, p4):
            return 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3
        def bezierY(t, p1, p2, p3, p4):
            return 3 * (1 - t) ** 2 * t * p2 + 3 * (1 - t) * t ** 2 * p4 + t ** 3
        def eq(x):
            return bezierX(x, p1, p2, p3, p4) - t
        x = bisect(eq, 0, 1)
        x = bezierY(x, p1, p2, p3, p4)
        return x * (self.end - self.start) + self.start
class Event:
    def __init__(self, event, line):
        self.line = line
        self.bezier = bool(event.get('bezier', 0))
        self.bezierPoints = event.get('bezierPoints', [0, 0, 0, 0])
        self.easingLeft = event.get('easingLeft', 0)
        self.easingRight = event.get('easingRight', 1)
        self.easingType = event.get('easingType', 1)
        self.start = event['start']
        self.end = event['end']
        self.startTime = line.chart.BPMList.calc(toBeat(event['startTime']))
        self.endTime = line.chart.BPMList.calc(toBeat(event['endTime']))
class Note:
    def __init__(self, note, line, id):
        self.line = line
        self.id = id
        self.isAbove = (note['above'] == 1) # != 2?
        self.alpha = util.clamp(note['alpha'], 0, 255)
        self.endTime = line.chart.BPMList.calc(toBeat(note['endTime']))
        self.startTime = line.chart.BPMList.calc(toBeat(note['startTime']))
        self.isFake = (note['isFake'] == 1)
        self.positionX = note['positionX'] / 75.375
        self.size = note['size']
        self.speed = note['speed']
        self.type = [0, 1, 3, 4, 2][note['type']]
        self.visibleTime = note['visibleTime']
        self.addFloorPosition()
        self.scored = False
        self.realTime = util.timeToSec(self.line.bpm, self.startTime)
        self.hl = False
        self.hit = False
        if DEBUG_NOTE:
            self.id_text = util.font(20).render(f'{self.line.id},{self.id}', False, (255, 0, 0))
    def addFloorPosition(self):
        v1 = 0
        v2 = 0
        v3 = 0
        for i in self.line.speedEvents:
            if self.startTime > i['endTime']:
                continue
            if self.startTime < i['startTime']:
                break
            v1 = i['floorPosition']
            v2 = i['value']
            v3 = self.startTime - i['startTime']
        self.floorPosition = v1 + v2 * v3 / self.line.bpm * 1.875
        if self.type == 3:
            self.speed *= v2
    def render(self, time, screen):
        realTime = util.timeToSec(self.line.bpm, time)
        if self.scored or self.line.alpha < 0:
            return
        if self.realTime - realTime > self.visibleTime or realTime - util.timeToSec(self.line.bpm, self.endTime) > self.visibleTime:
            return
        self.deg = -self.line.deg
        yDist = self.floorPosition - self.line.floorPosition
        if self.type != 3:
            yDist *= self.speed
            linePos = util.calcNotePos(self, yDist, -1)
            self.pos = linePos
            self.note(screen, *linePos)
            if DEBUG_NOTE:
                screen.blit(self.id_text, linePos)
        else:
            headPos = util.calcNotePos(self, max(0, yDist), -1)
            if time <= self.startTime:
                yDistEnd = yDist + self.speed * util.timeToSec(self.line.bpm, self.endTime - self.startTime)
            elif self.startTime < time <= self.endTime:
                yDistEnd = self.speed * util.timeToSec(self.line.bpm, self.endTime - time)
            else:
                yDistEnd = 0
            endPos = util.calcNotePos(self, yDistEnd, -1)
            self.hold(screen, *headPos, *endPos)
            if util.inrng(time, self.startTime, self.endTime):
                if not self.hit:
                    self.hit = True
                    sound.play(0)
                hitPos = util.calcNotePos(self, 0, -1)
                hit(screen, *hitPos, self.deg, 3)
    def note(self, screen, x, y):
        width, height = screen.get_size()
        lu = [x - 0.07 * height * self.size, y - 0.005 * height]
        rd = [x + 0.07 * height * self.size, y + 0.005 * height]
        if not util.intersect(*lu, *rd, 0, 0, width, height):
            return
        spirit, rect = util.displayRes(self.type + (4 if self.hl else 0), (x, y), (int(0.14 * height), int(0.01 * height)), self.deg, self.alpha)
        screen.blit(spirit, rect)
    def hold(self, screen, headX, headY, endX, endY):
        width, height = screen.get_size()
        lux = min(headX, endX)
        luy = min(headY, endY)
        rux = max(headX, endX)
        ruy = max(headY, endY)
        if not util.intersect(lux, luy, rux, ruy, 0, 0, width, height):
            return
        spirit, rect = util.displayRes((5 if self.hl else 1), (headX, headY), (int(0.14 * height * self.size), int(0.01 * height)), self.deg, self.alpha)
        screen.blit(spirit, rect) # holdHead
        pygame.draw.line(screen, (255, 255, 255, self.alpha), (headX, headY), (endX, endY), int(0.01 * height)) # holdBody
class BPMList:
    def __init__(self, bpmlist):
        self.baseBPM = bpmlist[0]['bpm']
        self.list = []
        self.acctime = 0
        self.parse(bpmlist)
    def parse(self, bpmlist):
        for i, j in enumerate(bpmlist):
            value = self.acctime
            j['startTime'] = max(0, toBeat(j['startTime']))
            if i == len(bpmlist) - 1:
                j['endTime'] = 1e9
            else:
                j['endTime'] = toBeat(bpmlist[i + 1]['startTime'])
            j['value'] = value
            self.acctime += (j['endTime'] - j['startTime']) / j['bpm']
            self.list.append(j)
    def calc(self, beat):
        pgr = 0
        for i in self.list:
            if beat > i['endTime']:
                continue
            if beat < i['startTime']:
                break
            pgr = round(((beat - i['startTime']) / i['bpm'] + i['value']) * self.baseBPM * 32)
        return pgr
def toBeat(beat):
    return beat[0] + beat[1] / beat[2]
class RPEJudgeManager():
    def __init__(self, note_list):
        self.note_list = note_list
        self.combo = 0
    def check(self, time, screen):
        if not self.note_list:
            return
        time = util.secToTime(self.note_list[0].line.bpm, time)
        while self.note_list[0].endTime <= time:
            self.combo += 1
            n = self.note_list[0]
            if n.type != 3:
                hit(screen, *n.pos, n.deg, n.type)
            n.scored = 1
            self.note_list.pop(0)
            if not self.note_list:
                return
def hit(screen, x, y, deg, type):
    scr = pygame.Surface((20, 20), pygame.SRCALPHA)
    scr.fill(util.LINE_COLOR)
    rotated = pygame.transform.rotate(scr, deg)
    rect = rotated.get_rect(center=(x, y))
    screen.blit(rotated, rect)
    if type != 3:
        sound.play([1, 2, 4].index(type))