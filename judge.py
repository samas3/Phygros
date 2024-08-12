import note
import util
class JudgeManager:
    def __init__(self, note_list):
        self.note_list = note_list
        self.combo = 0
    def check(self, screen, time):
        if not self.note_list:
            return
        time = util.secToTime(self.note_list[0].line.bpm, time)
        while self.note_list[0].time + self.note_list[0].holdTime <= time:
            self.combo += 1
            if self.note_list[0].type != 3:
                note.hit(screen, *self.note_list[0].pos, self.note_list[0].deg)
            self.note_list[0].scored = 1
            self.note_list.pop(0)