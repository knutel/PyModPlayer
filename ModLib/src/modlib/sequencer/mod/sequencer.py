from audioop import mul
from modlib.sequencer.mod.tables import period_table

class Channel(object):
    def __init__(self, sequencer):
        self.note = None
        self.volume = 64
        self.sample_id = 0
        self.sample = None
        self.period = 0
        self.sequencer = sequencer
        self.effect = None
        self.sample_offset = 0
        
    def samples_per_tick(self):
        if self.period == 0:
            return 0
        else:
            return int(self.sequencer.tick_time * self.sequencer.system_clock / (2.0 * self.period))
        
    def tick(self):
        self.effect.tick()
        if self.period == 0:
            return "\x80" * 100
        else:
            data = self.sample.get_data(self.sample_offset, self.samples_per_tick())
            self.sample_offset += self.samples_per_tick()
            return mul(data, 1, self.volume / 64.0) 

    def new_note(self, note):
        self.note = note
        self.effect = note.effect(self, self.sequencer)
        if note.sample_id != 0:
            self.sample = self.sequencer.module.samples[note.sample_id - 1]
            self.period = note.period
            self.sample_offset = 0
            self.volume = self.sample.volume
            
    def __str__(self):
        return "%4s %2x %s" % (period_table[self.note.period], self.note.sample_id, self.effect)
        
class Sequencer(object):
    def __init__(self, module):
        self.module = module
        self.sequence_index = -1
        self.division_index = 63
        self.pattern_index = self.module.pattern_sequence[self.sequence_index]
        self.master_tick_counter = -1
        self.tick_counter = 5
        self.position_counter = -1
        
        self.system_clock = 7093789.2 #PAL for now
        self.tick_time = 0.02 #PAL for now
        self.ticks_per_division = 6
        
        self.channels = [Channel(self) for n in range(4)]

        self.ended = False
        
        #Effects related
        self.loop_pattern_counter = 0
        self.loop_pattern_division_start = 0
        self.loop_pattern_division_stop = 0
        
    def tick(self):
        self.update_state()
        if not self.ended:
            data = [channel.tick() for channel in self.channels]
            #print [len(d) for d in data]
            return data
    
    def update_state(self):
        if not self.ended:
            self.tick_counter += 1
            self.master_tick_counter += 1
            if self.tick_counter == self.ticks_per_division:
                self.tick_counter = 0
                self.division_index += 1
                if self.division_index == 64:
                    self.division_index = 0
                    self.sequence_index += 1
                    self.position_counter += 1
                    if self.position_counter == self.module.num_positions:
                        self.ended = True
                        return
                    self.pattern_index = self.module.pattern_sequence[self.sequence_index]
                    self.loop_pattern_counter = 0
                    self.loop_pattern_division_start = 0
                    self.loop_pattern_division_stop = 0
                for index, channel in enumerate(self.channels):
                    channel.new_note(self.module.patterns[self.pattern_index].divisions[self.division_index].channel_data[index])
                    
                print "Sequence: %3i/%3i, Pattern: %3i, Division: %2i, %s" % (self.sequence_index, self.module.num_positions, self.pattern_index, self.division_index, [str(channel) for channel in self.channels])
            
if __name__ == "__main__":
    from modlib.sequencer.mod.loader import load
    from audioop import ratecv, mul, tostereo, add, bias
    import wave
    
    seq = Sequencer(load("/Volumes/Stuff/old_backup_cds/cd2/SCENE/Mod/MOUSEMOD.MOD"))
    import time
    f = wave.open("/tmp/test.wav", "wb")
    f.setnchannels(1)
    f.setsampwidth(1)
    f.setframerate(44100)
    state = None
    output = ["", "", "", ""]
    state = [None, None, None, None]
    for n in range(4):
        dummy, state[n] = ratecv("\x80"*100, 1, 1, 100*50, 44100, state[n])
    print time.clock()
    while True:
        try:
            sound = seq.tick()
        except:
            pass
        if sound is None:
            break
        for n in range(4):
            while True:
                output[n], state[n] = ratecv(sound[n], 1, 1, len(sound[n])*50, 44100, state[n])
                if len(output[n]) == 44100 / 50:
                    break
            output[n] = mul(output[n], 1, 0.25)
            #output[n] = mul(output[n], 1, 0.5)
            #output[n] = tostereo(output[n], 1, n % 2, (n + 1) % 2)
        #left = add(output[0], output[2], 1)
        #right = add(output[1], output[3], 1)
        #stereo = add(left, right, 1)
        #f.writeframes(stereo)
        f.writeframes(bias(add(add(output[0], output[1], 1), add(output[2], output[3], 1), 1), 1, 128))
        #f.writeframes(bias(output[0], 1, 128))
    print time.clock()
    f.close()
