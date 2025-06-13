import line
import util
import judge
class Chart:
    def __init__(self, chart, info={}, options={}):
        self.options = options
        self.fv = int(chart['formatVersion'])
        self.offset = float(chart['offset'])
        self.lines = []
        self.all_notes = []
        for i, j in enumerate(chart['judgeLineList']):
            self.lines.append(line.Line(j, i))
        for i in self.lines:
            i = number_notes(i)
            self.all_notes += i.notesAbove + i.notesBelow
            for j, k in enumerate(i.speedEvents):
                if j == 0:
                    i.speedEvents[j].floorPosition = 0
                else:
                    i.speedEvents[j].floorPosition = i.speedEvents[j - 1].floorPosition + i.speedEvents[j - 1].value * util.timeToSec(i.bpm, k.startTime - i.speedEvents[j - 1].startTime)
        self.all_notes.sort(key=lambda x: x.time + x.holdTime)
        self.notes = len(self.all_notes)
        self.jm = judge.JudgeManager(self.all_notes, self.options)
        self.check_line()
        if 'nohl' not in options:
            self.highlight()
        self.name = info.get('name', 'Untitled')
        self.lvl = info.get('level', 'SP Lv.?')
    def __repr__(self):
        return f'Phigros Chart[Notes={self.notes}, Lines={len(self.lines)}]'
    def print(self, str):
        if 'printlog' in self.options:
            print(str)
    def check_line_event(self, line, evt, isSpeed=False):
        flag = 1
        for i, j in enumerate(evt):
            if i == 0 and j.startTime >= 0 and not isSpeed:
                self.print(f'Warning: JudgeLine{line.id}.Event[0].startTime >= 0')
                flag = 0
            elif i == 0 and j.startTime != 0 and isSpeed:
                self.print(f'Warning: JudgeLine{line.id}.Event[0].startTime != 0')
                j.startTime = 0
                flag = 0
            elif i > 0:
                if j.startTime != evt[i - 1].endTime:
                    self.print(f'Warning: JudgeLine{line.id}.Event[{i}].startTime != JudgeLine{line.id}.Event[{i - 1}].endTime')
                    flag = 0
            elif i == len(evt) - 1 and j.endTime <= 1e7:
                self.print(f'Warning: JudgeLine{line.id}.Event[{i}].endTime <= 1e7')
                flag = 0
        return flag
    def check_line(self):
        self.print('Check speedEvent')
        flag = 1
        for i in self.lines:
            if not self.check_line_event(i, i.speedEvents, True):
                flag = 0
        if flag:
            self.print('OK')
        self.print('Check disappearEvent')
        flag = 1
        for i in self.lines:
            if not self.check_line_event(i, i.disappearEvents):
                flag = 0
        if flag:
            self.print('OK')
        self.print('Check moveEvent')
        flag = 1
        for i in self.lines:
            if not self.check_line_event(i, i.moveEvents):
                flag = 0
        if flag:
            self.print('OK')
        self.print('Check rotateEvent')
        flag = 1
        for i in self.lines:
            if not self.check_line_event(i, i.rotateEvents):
                flag = 0
        if flag:
            self.print('OK')
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
    def render(self, time, screen, options):
        for i in self.all_notes:
            chartTime = util.secToTime(i.line.bpm, time)
            i.render(screen, chartTime, self.fv, options)
        for i in self.lines:
            i.render(time, screen, util.LINE_COLOR, self.fv, options)
        # 后渲染界面，要不然会被挡
        font = util.font(20)
        combo_font = util.font(16)
        combo_font2 = util.font(26)
        name = font.render(self.name, False, util.TEXT_COLOR)
        lvl = font.render(self.lvl, False, util.TEXT_COLOR)
        width, height = screen.get_size()
        screen.blit(name, (10, height - 30))
        screen.blit(lvl, (width - lvl.get_width() - 10, height - 30))
        self.jm.check(screen, time)
        combo_num = combo_font2.render(str(self.jm.combo), False, util.TEXT_COLOR)
        combo_text = combo_font.render('AUTOPLAY', False, util.TEXT_COLOR)
        if self.jm.combo > 2:
            screen.blit(combo_num, (width / 2 - combo_num.get_width() / 2, 10))
            screen.blit(combo_text, (width / 2 - combo_text.get_width() / 2, 40))
        score_num = combo_font2.render(str(round(self.jm.combo / self.notes * 1e6)).zfill(7), False, util.TEXT_COLOR)
        screen.blit(score_num, (width - score_num.get_width() - 10, 10))
def number_notes(line):
    line.notesAbove.sort(key=lambda x: x.time)
    line.notesBelow.sort(key=lambda x: x.time)
    for i, j in enumerate(line.notesAbove):
        j.id = i
    for i, j in enumerate(line.notesBelow):
        j.id = i
    line.speedEvents.sort(key=lambda x: x.startTime)
    line.disappearEvents.sort(key=lambda x: x.startTime)
    line.moveEvents.sort(key=lambda x: x.startTime)
    line.rotateEvents.sort(key=lambda x: x.startTime)
    return line