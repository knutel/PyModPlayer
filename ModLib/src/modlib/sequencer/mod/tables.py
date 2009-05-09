from bisect import bisect_left, bisect_right

class PeriodTable(object):
    def __init__(self):
        self.notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        self.notes.reverse()
    
        self.periods = [856, 808, 762, 720, 678, 640, 604, 570, 538, 508, 480, 453,
                        428, 404, 381, 360, 339, 320, 302, 285, 269, 254, 240, 226,
                        214, 202, 190, 180, 170, 160, 151, 143, 135, 127, 120, 113]
        self.periods.reverse()

    def __getitem__(self, key):
        if key == 0:
            return "    "
        index = (bisect_right(self.periods, key) + bisect_left(self.periods, key)) / 2
        #print key, index
        octave = index / 12 + 1
        note = self.notes[index % 12]
        return "%s-%i" % (note, octave)
    
    def finetune(self, key, value):
        index = (bisect_right(self.periods, key) + bisect_left(self.periods, key)) / 2 - value
        if index < 0:
            index = 0
        return self.periods[index]
        
        
period_table = PeriodTable()

_half_sine_table = [0, 24, 49, 74, 97,120,141,161,
              180,197,212,224,235,244,250,253,
              255,253,250,244,235,224,212,197,
              180,161,141,120, 97, 74, 49, 24]

sine_table = _half_sine_table + [-value for value in _half_sine_table]