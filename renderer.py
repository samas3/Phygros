import csv
import pygame
import chart as ch
import rpe
import util
import json
import os
from tinytag import TinyTag
from PIL import Image, ImageFilter, ImageEnhance
def get_duration(file_path):
    tag = TinyTag.get(file_path)
    duration = tag.duration
    return duration
class Renderer():
    def __init__(self, chart, music, bg, info, options=''):
        if os.path.isfile(info):
            if info.endswith('.json'):
                self.info = json.load(open(info, encoding='utf-8'))
            else:
                self.info = self.parseCSV(open(info, encoding='utf-8'))
        else:
            self.info = json.load(open('samplejson'))
        self.music = music
        self.bg = bg
        self.options = util.parse(options)
        self.chartjson = json.load(open(chart, encoding='utf-8'))
        if 'META' in self.chartjson:
            self.chart = rpe.RPE(self.chartjson)
            self.info = self.chart.info
        else:
            self.chart = ch.Chart(self.chartjson, self.info, self.options)
    def parseCSV(self, file):
        info = {}
        with file as f:
            reader = csv.reader(f)
            infos = []
            for i in reader:
                infos.append(list(i))
            for i in range(len(infos[0])):
                info[infos[0][i]] = infos[1][i]
        return {'name': info['Name'], 'level': info['Level'], 'composer': info['Artist'], 'charter': info['Charter'], 'illustration': info['Illustrator']}
    def play(self):
        global scr
        pygame.init()
        rate = 2048 / 1080
        min_width = float(self.options.get('minwidth', 500))
        screen = pygame.display.set_mode((min_width * rate, min_width))
        if self.bg:
            bgimg = Image.open(self.bg).filter(ImageFilter.GaussianBlur(radius=6))
            enhancer = ImageEnhance.Brightness(bgimg)
            bgimg = enhancer.enhance(0.5)
            bg = pygame.image.fromstring(bgimg.tobytes(), bgimg.size, bgimg.mode).convert_alpha()
            width, height = bg.get_size()
            rate = width / height
            screen = pygame.display.set_mode((min_width * rate, min_width))
            bg = pygame.transform.scale(bg, (min_width * rate, min_width))
        screen2 = screen.convert_alpha()
        width, height = (min_width * rate, min_width)
        util.init(width, height)
        pygame.display.set_caption('Phygros')
        pygame.mixer.music.load(self.music)
        music_on = False
        pause = False
        timer = pygame.time.get_ticks() / 1000
        passed = 0
        tot = get_duration(self.music)
        font = util.font(24)
        fps_font = util.font(15)
        clock = pygame.time.Clock()
        while True:
            if pause:
                timer = pygame.time.get_ticks() / 1000
                passed = tm
            else:
                tm = passed + pygame.time.get_ticks() / 1000 - timer
            tm2 = tm
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    break
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        pause = not pause
                        if pause:
                            pygame.mixer.music.pause()
                        else:
                            pygame.mixer.music.unpause()
            else:
                if self.bg:
                    screen2.blit(bg, (0, 0))
                else:
                    screen2.fill((0, 0, 0))
                if tm >= 3 or 'notrans' in self.options:
                    if not music_on:
                        pygame.mixer.music.play(1)
                        if self.chart.offset > 0:
                            pygame.mixer.music.set_pos(self.chart.offset)
                        music_on = True
                    tm2 = tm - 3
                    if 'notrans' in self.options:
                        tm2 += 3
                    if 'speed' in self.options:
                        tm2 *= float(self.options['speed'])
                    self.chart.render(tm2, screen2, self.options)
                    fps_text = fps_font.render('{:.0f}'.format(clock.get_fps()), False, util.TEXT_COLOR)
                    screen2.blit(fps_text, (width - fps_text.get_width() - 10, height / 2 - fps_text.get_height() / 2))
                    time_text = font.render(util.ftime(min(tm2, tot)) + '/' + util.ftime(tot) + (' (PAUSED)' if pause else ''), False, util.TEXT_COLOR)
                    if tm2 > tot + 3:
                        pygame.quit()
                        break
                    pygame.draw.line(screen2, (127, 127, 127, 127), (0, 0), (pygame.mixer.music.get_pos() / 1000 / tot * width, 0), int(0.02 * height))
                    screen2.blit(time_text, (10, 10))
                else:
                    name = self.info.get('name', 'Untitled')
                    lvl = self.info.get('level', 'SP Lv.?')
                    charter = self.info.get('charter', '?')
                    composer = self.info.get('composer', '?')
                    illustration = self.info.get('illustration', '?')
                    name_text = font.render(name, False, util.TEXT_COLOR)
                    lvl_text = font.render(lvl, False, util.TEXT_COLOR)
                    charter_text = font.render('Chart by ' + charter, False, util.TEXT_COLOR)
                    composer_text = font.render('Composed by ' + composer, False, util.TEXT_COLOR)
                    illustration_text = font.render('Illustrated by ' + illustration, False, util.TEXT_COLOR)
                    screen2.blit(name_text, (width / 2 - name_text.get_width() / 2, height / 2 - 90))
                    screen2.blit(lvl_text, (width / 2 - lvl_text.get_width() / 2, height / 2 - 50))
                    screen2.blit(charter_text, (width / 2 - charter_text.get_width() / 2, height / 2 + 15))
                    screen2.blit(composer_text, (width / 2 - composer_text.get_width() / 2, height / 2 + 55))
                    screen2.blit(illustration_text, (width / 2 - illustration_text.get_width() / 2, height / 2 + 95))
                    pygame.draw.line(screen2, util.LINE_COLOR, (width / 2 * (1 - tm2 / 3), height / 2), (width / 2 * (1 + tm2 / 3), height / 2), int(0.0075 * height))
                screen.blit(screen2, (0, 0))
                pygame.display.flip()
                clock.tick(float(self.options['maxfps']) if 'maxfps' in self.options else 60)
                continue
            break
if __name__ == '__main__':
    name = '1'
    Renderer(f'{name}.json', f'{name}.wav', f'{name}.png', '', 'notrans').play()