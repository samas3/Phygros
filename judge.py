import note
import util
class JudgeManager:
    def __init__(self, note_list, options):
        self.note_list = note_list
        self.combo = 0
        self.options = options
    def check(self, screen, time):
        if not self.note_list:
            return
        time = util.secToTime(self.note_list[0].line.bpm, time)
        while self.note_list[0].time + self.note_list[0].holdTime <= time:
            self.combo += 1
            n = self.note_list[0]
            if n.type != 3:
                note.hit(screen, *n.pos, n.deg, n.type, self.options)
            n.scored = 1
            self.note_list.pop(0)
            if not self.note_list:
                return