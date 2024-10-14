import util
import pygame
from math import *
from scipy.optimize import bisect
class RPE:
    def __init__(self, chart):
        self.BPMList = BPMList(chart['BPMList'])
        self.meta = chart['META']
        self.info = {k: self.meta[k] for k in self.meta if k in ['name', 'charter', 'composer', 'illustration']}
        self.info['lvl'] = self.meta['level']
        self.offset = float(self.meta['offset']) * 1000
        self.judgeLineList = chart['judgeLineList']
        self.lineList = []
        self.parseLine()
        self.all_notes = []
        for i in self.lineList:
            self.all_notes += filter(lambda x: not x['isFake'], i.noteList)
        self.notes = len(self.all_notes)
        self.all_notes.sort(key=lambda x: x.startTime)
        self.jm = RPEJudgeManager(self.all_notes)
    def parseLine(self):
        for i, line in enumerate(self.judgeLineList):
            self.lineList.append(Line(line, self, i))
    def highlight(self):
        notes = sorted(self.all_notes, key=lambda x: x.realTime)
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
    def render(self, time, screen, _):
        for i in self.all_notes:
            chartTime = util.secToTime(i.line.bpm, time)
            if i.endTime >= chartTime:
                i.render(chartTime, screen)
        for i in self.lineList:
            i.render(time, screen)
        font = pygame.font.Font(util.FONT, 20)
        combo_font = pygame.font.Font(util.FONT, 16)
        combo_font2 = pygame.font.Font(util.FONT, 26)
        name = font.render(self.info['name'], False, util.TEXT_COLOR)
        lvl = font.render(self.info['lvl'], False, util.TEXT_COLOR)
        width, height = screen.get_size()
        screen.blit(name, (10, height - 30))
        screen.blit(lvl, (width - lvl.get_width() - 10, height - 30))
        self.jm.check(screen, time)
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
        for i in line['eventLayers']:
            for j, k in i.items():
                self.events[j] += k
        self.extended = line['extended']
        self.notes = line.get('notes', [])
        self.noteList = []
        self.parseNote()
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
        self.floorPosition = 0
        self.x = 0
        self.y = 0
        self.deg = 0
        self.alpha = 0
    def parseNote(self):
        for note in self.noteList:
            self.noteList.append(Note(note, self))
    def convertSpeedEvent(self):
        speedEvents = []
        for i in self.events['speedEvents']:
            speedEvents.append(Event(i, self))
        events = []
        for i in speedEvents:
            ease = Easing(i)
            for j in range(int(ease.startTime), int(ease.endTime) + 1):
                events.append({'time': j, 'value': ease.getValue(j)})
        self.speedEvents = sorted(events, key=lambda x: x['time'])
    def parseEvent(self):
        self.convertSpeedEvent()
        floorPos = 0
        for i, j in enumerate(self.speedEvents):
            start = max(0, j['time'])
            end = self.speedEvents[i + 1]['time'] if i + 1 < len(self.speedEvents) else 1e9
            val = j['value'] * 11 / 45
            pos = floorPos
            floorPos += round((end - start) * val / self.bpm * 1.875)
            j['floorPosition'] = pos
            j['startTime'] = start
            j['endTime'] = end
            j['value'] = val
        for i, j in enumerate(self.events['moveXEvents']):
            j['start'] = (j['start'] + 675) / 1350
            j['end'] = (j['end'] + 675) / 1350
            self.moveXEvents.append(Event(j, self))
        for i, j in enumerate(self.events['moveYEvents']):
            j['start'] = (j['start'] + 450) / 900
            j['end'] = (j['end'] + 450) / 900
            self.moveYEvents.append(Event(j, self))
        for i, j in enumerate(self.events['rotateEvents']):
            self.rotateEvents.append(Event(j, self))
        for i, j in enumerate(self.events['alphaEvents']):
            self.alphaEvents.append(Event(j, self))
    def render(self, time, screen):
        time = util.secToTime(self.bpm, time)
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
                #self.alphaEvents.remove(i)
                continue
            if time < i.startTime:
                break
            self.alpha = Easing(i).getValue(time)
            if self.id == 0:
                print(self.alpha, time)
            break
        for i in self.moveXEvents:
            if time > i.endTime:
                self.moveXEvents.remove(i)
                continue
            if time < i.startTime:
                break
            self.x = Easing(i).getValue(time)
            break
        for i in self.moveYEvents:
            if time > i.endTime:
                self.moveYEvents.remove(i)
                continue
            if time < i.startTime:
                break
            self.y = Easing(i).getValue(time)
            break
        for i in self.rotateEvents:
            if time > i.endTime:
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
        #alpha = util.clamp(self.alpha, 0, 255)
        alpha = self.alpha
        color = (*util.LINE_COLOR, alpha)
        pygame.draw.line(screen, color, left, right, int(0.0075 * height))
        font = pygame.font.Font(util.FONT, 20)
        #lineId = font.render(str(self.id), False, (255, 0, 0))
        #screen.blit(lineId, originalPos)
        if self.id == 0:
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
        #if alpha > 0:
            #pygame.draw.line(screen, color, left, right, int(0.0075 * height))
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
        self.tween = [None, lambda x: x,
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
                      lambda x: 1 - self.tween[26](1 - x),
                      lambda x: (lambda y: self.tween[26](y) / 2 if y < 1 else self.tween[27](x - 1) / 2 + 0.5)(x * 2),
                      lambda x: 2 ** (20 * x - 11) * sin((160 * x + 1) * pi / 18) if x < 0.5 else 1 - 2 ** (9 - 20 * x) * sin((160 * x + 1) * pi / 18)]
    def getValue(self, time):
        if time < self.startTime:
            return self.start
        elif time > self.endTime:
            return self.end
        else:
            if self.easingType == -1: # bezier curve
                return self.bezier(time)
            t = (time - self.startTime) / (self.endTime - self.startTime) * (self.easingRight - self.easingLeft) + self.easingLeft
            return self.tween[self.easingType](t) * (self.end - self.start) + self.start
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
        if isinstance(event['startTime'], list):
            self.startTime = line.chart.BPMList.calc(toBeat(event['startTime']))
            self.endTime = line.chart.BPMList.calc(toBeat(event['endTime']))
        else:
            self.startTime = event['startTime']
            self.endTime = event['endTime']
class Note:
    def __init__(self, note, line):
        self.line = line
        self.above = (note['above'] != '2')
        self.alpha = float(note['alpha'])
        self.endTime = float(note['endTime'])
        self.startTime = float(note['startTime'])
        self.isFake = (note['isFake'] == '1')
        self.positionX = float(note['positionX'])
        self.size = float(note['size'])
        self.speed = float(note['speed'])
        self.type = int(note['type'])
        self.visibleTime = float(note['visibleTime'])
        self.addFloorPosition()
    def addFloorPosition(self):
        v1 = 0
        v2 = 0
        v3 = 0
        for i in self.line.speedEvents:
            if self.startTime > i.endTime:
                continue
            if self.startTime < i.startTime:
                break
            v1 = i.floorPosition
            v2 = i.value
            v3 = self.startTime - i.startTime
        self.floorPosition = round(v1 + v2 * v3 / self.line.bpm * 1.875)
    def render(self, time, screen):
        pass
class BPMList:
    def __init__(self, bpmlist):
        self.baseBPM = bpmlist[0]['bpm']
        self.list = []
        self.accTime = 0
        self.parse(bpmlist)
    def parse(self, bpmlist):
        for i, j in enumerate(bpmlist):
            value = self.accTime
            j['startTime'] = max(0, toBeat(j['startTime']))
            if i == len(bpmlist) - 1:
                j['endTime'] = 1e9
            else:
                j['endTime'] = toBeat(bpmlist[i + 1]['startTime'])
            j['value'] = value
            value += (j['endTime'] - j['startTime']) / j['bpm']
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
    def check(self, screen, time):
        if not self.note_list:
            return
        time = util.secToTime(self.note_list[0].line.bpm, time)
        while self.note_list[0].endTime <= time:
            self.combo += 1
            n = self.note_list[0]
            n.scored = 1
            self.note_list.pop(0)
            if not self.note_list:
                return