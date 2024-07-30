import json
import line
import util
import pygame
class Chart():
    def __init__(self, chart, info={}, options={}):
        chart = json.load(open(chart))
        self.options = options
        self.fv = int(chart['formatVersion'])
        self.offset = float(chart['offset'])
        self.lines = []
        for i, j in enumerate(chart['judgeLineList']):
            self.lines.append(line.Line(j, i))
        self.all_notes = []
        for i in self.lines:
            self.all_notes += i.notesAbove + i.notesBelow
            for j, k in enumerate(i.speedEvents):
                if j == 0:
                    i.speedEvents[j].floorPosition = 0
                else:
                    i.speedEvents[j].floorPosition = i.speedEvents[j - 1].floorPosition + i.speedEvents[j - 1].value * (k.startTime - i.speedEvents[j - 1].startTime) * 1.875 / i.bpm
        self.all_notes.sort(key=lambda x: x.time)
        id = 0
        for i in self.all_notes:
            for j in self.lines:
                for k in j.notesAbove:
                    if i.time == k.time:
                        k.id = id
                        id += 1
                for k in j.notesBelow:
                    if i.time == k.time:
                        k.id = id
                        id += 1
        self.check_line()
        self.name = info.get('name', 'Untitled')
        self.lvl = info.get('lvl', 'SP Lv.?')
        self.numOfNotes = self.notes()
    def scored(self):
        res = 0
        for i in self.lines:
            res += i.scored()
        return res
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
    def notes(self):
        cnt = 0
        for i in self.lines:
            cnt += i.notes()
        self.notes = cnt
        return self.notes
    def render(self, time, screen, options):
        for i in self.lines:
            i.render(time, screen, (254, 255, 169), self.fv, options)
        # 后渲染界面，要不然会被挡
        font = pygame.font.Font('font.ttf', 25)
        combo_font = pygame.font.Font('font.ttf', 20)
        combo_font2 = pygame.font.Font('font.ttf', 35)
        name = font.render(self.name, False, util.TEXT_COLOR)
        lvl = font.render(self.lvl, False, util.TEXT_COLOR)
        width, height = screen.get_size()
        screen.blit(name, (10, height - 30))
        screen.blit(lvl, (width - lvl.get_width() - 10, height - 30))
        combo_num = combo_font2.render(str(self.scored()), False, util.TEXT_COLOR)
        screen.blit(combo_num, (width / 2 - combo_num.get_width() / 2, 0))
        combo_text = combo_font.render('AUTOPLAY', False, util.TEXT_COLOR)
        screen.blit(combo_text, (width / 2 - combo_text.get_width() / 2, 40))
        score_num = combo_font2.render(str(round(self.scored() / self.notes * 1e6)).zfill(7), False, util.TEXT_COLOR)
        screen.blit(score_num, (width - score_num.get_width() - 10, 10))