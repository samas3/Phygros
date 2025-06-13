import pygame
import note
import util
class Line:
    def __init__(self, lineJson, id=0):
        self.bpm = float(lineJson['bpm'])
        self.notesAboveNoHold = []
        self.notesAboveHold = []
        for i in lineJson['notesAbove']:
            tmp = note.Note(i, self, True)
            if tmp.type == 3:
                self.notesAboveHold.append(tmp)
            else:
                self.notesAboveNoHold.append(tmp)
        self.notesAbove = self.notesAboveNoHold + self.notesAboveHold
        self.notesBelowNoHold = []
        self.notesBelowHold = []
        for i in lineJson['notesBelow']:
            tmp = note.Note(i, self, False)
            if tmp.type == 3:
                self.notesBelowHold.append(tmp)
            else:
                self.notesBelowNoHold.append(tmp)
        self.notesBelow = self.notesBelowNoHold + self.notesBelowHold
        self.speedEvents = []
        for i in lineJson['speedEvents']:
            self.speedEvents.append(SpeedEvent(i))
        self.speedEvents.sort()
        self.disappearEvents = []
        for i in lineJson['judgeLineDisappearEvents']:
            self.disappearEvents.append(LineEvent(i))
        self.disappearEvents.sort()
        self.moveEvents = []
        for i in lineJson['judgeLineMoveEvents']:
            moveEvt = LineEvent(i)
            moveEvt.toFV3()
            self.moveEvents.append(moveEvt)
        self.moveEvents.sort()
        self.rotateEvents = []
        for i in lineJson['judgeLineRotateEvents']:
            self.rotateEvents.append(LineEvent(i))
        self.rotateEvents.sort()

        self.x = 0
        self.y = 0
        self.deg = 0
        self.alpha = 0
        self.id = id
        self.floorPosition = 0
    def __repr__(self):
        return f'JudgeLine[id={self.id}, Notes={len(self.notesAbove) + len(self.notesBelow)}, BPM={self.bpm}, Events={len(self.speedEvents) + len(self.disappearEvents) + len(self.moveEvents) + len(self.rotateEvents)}]'
    def notes(self):
        return len(self.notesAbove) + len(self.notesBelow)
    def render(self, time, screen, color, fv, options):
        time = util.secToTime(self.bpm, time)
        for i in self.speedEvents:
            if time > i.endTime:
                self.speedEvents.remove(i)
                continue
            if time < i.startTime:
                break
            self.floorPosition = i.floorPosition + i.value * util.timeToSec(self.bpm, time - i.startTime)
            break
        for i in self.disappearEvents:
            if time > i.endTime:
                self.disappearEvents.remove(i)
                self.alpha = i.end
                continue
            if time < i.startTime:
                break
            self.alpha = util.rng(time, i.startTime, i.endTime, i.start, i.end) # 为什么0是透明1是不透明
            break
        for i in self.moveEvents:
            if time > i.endTime:
                self.moveEvents.remove(i)
                self.x = i.end
                self.y = i.end2
                continue
            if time < i.startTime:
                break
            self.x = util.rng(time, i.startTime, i.endTime, i.start, i.end)
            self.y = util.rng(time, i.startTime, i.endTime, i.start2, i.end2)
            break
        for i in self.rotateEvents:
            if time > i.endTime:
                self.rotateEvents.remove(i)
                self.deg = i.end
                continue
            if time < i.startTime:
                break
            self.deg = util.rng(time, i.startTime, i.endTime, i.start, i.end)
            break
        width, height = screen.get_size()
        cx = self.x
        cy = self.y
        deg = -self.deg # 旋转后坐标再转换？
        originalPos = util.toPygamePos(*util.toChartPos(cx, cy, fv))
        pos = originalPos[:]
        pos[0] -= 2.88 * height
        left = util.rotate(*originalPos, *pos, deg)
        pos[0] += 5.76 * height
        right = util.rotate(*originalPos, *pos, deg)
        if 'mirror' in options:
            left = (width - left[0], left[1])
            right = (width - right[0], right[1])
        alpha = util.clamp(self.alpha, 0, 1) * 255
        color = (*color, alpha)
        font = util.font(20)
        if 'showid' in options:
            lineId = font.render(str(self.id), False, (255, 0, 0))
            screen.blit(lineId, util.toPygamePos(*util.toChartPos(cx, cy, fv)))
        if 'showinfo' in options and self.id == int(options['showinfo']):
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
        if alpha > 0:
            pygame.draw.line(screen, color, left, right, int(0.0075 * height))
class Event:
    def __init__(self, evtJson):
        self.startTime = int(evtJson['startTime'])
        self.endTime = int(evtJson['endTime'])
    def __repr__(self):
        return '{}[Time={:.2f}-{:.2f}]'.format(self.__class__.__name__, self.startTime, self.endTime)
    def __lt__(self, other):
        return self.startTime < other.startTime
class SpeedEvent(Event):
    def __init__(self, evtJson):
        super().__init__(evtJson)
        self.value = float(evtJson['value'])
class LineEvent(Event):
    def __init__(self, evtJson):
        super().__init__(evtJson)
        self.start = float(evtJson['start'])
        self.end = float(evtJson['end'])
        if 'start2' in evtJson:
            self.start2 = float(evtJson['start2'])
            self.end2 = float(evtJson['end2'])
    def toFV3(self):
        if 'start2' in self.__dict__:
            return
        self.start2 = self.start % 1000
        self.start //= 1000
        self.end2 = self.end % 1000
        self.end //= 1000