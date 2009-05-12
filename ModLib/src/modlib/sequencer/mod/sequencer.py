from audioop import mul
from modlib.sequencer.mod.tables import period_table
from modlib.sequencer.mod.effect import SlideToNote, ContinueSlideToNotePlusVolumeSlide, SetSampleOffset
from modlib.sequencer.mod.effect import SlideToNote
from modlib.sequencer.mod.effect import ContinueSlideToNotePlusVolumeSlide
from modlib.sequencer.mod.effect import SetSampleOffset

def clip(min_, value, max_):
    return min((max_, max((value, min_))))

class Channel(object):
    def __init__(self, sequencer):
        self.note = None
        self.sample = None
        self.sequencer = sequencer
        self.effect = None
        self.sample_offset = 0

        self._volume = 64
        self._period = 0
        self.original_period = 0
        
        #Effects related
        self.vibrato_position = 0
        self.vibrato_speed = 0
        self.vibrato_depth = 0

        self.tremolo_speed = 0
        self.tremolo_depth = 0
        self.tremolo_position = 0

        self.loop_pattern_counter = 0
        self.loop_pattern_division_start = 0
        self.loop_pattern_division_stop = 0
        
        self.slide_to_note_speed = 0
        
    def _set_volume(self, volume):
        self._volume = clip(0, volume, 64)
    volume = property(lambda self: self._volume, _set_volume)
    
    def _set_period(self, period):
        self._period = clip(113, period, 856)
    period = property(lambda self: self._period, _set_period)
    
    tuned_period = property(lambda self: self.period * pow(2, -self.sample.finetune * 1.0 / (12 * 8)))    
    
    original_volume = property(lambda self: self.sample.volume)
    
    def samples_per_tick(self):
        if self.period == 0:
            return 0
        else:
            return int(self.sequencer.tick_time * self.sequencer.system_clock / (2.0 * self.tuned_period))

    def tick(self):
        self.effect.tick()
        if self.period == 0 or self.sample is None:
            return "\x80" * 100
        else:
            data = self.sample.get_data(self.sample_offset, self.samples_per_tick())
            self.sample_offset += self.samples_per_tick()
            return mul(data, 1, self.volume / 64.0) 

    def new_note(self, note):
        self.note = note
        if note.sample_id != 0:
            self.sample = self.sequencer.module.samples[note.sample_id - 1]
            self.sample_offset = 0
            self.volume = self.sample.volume
        self.effect = note.effect(self, self.sequencer)
        if note.period != 0:
            if not isinstance(self.effect, SetSampleOffset):
                self.sample_offset = 0
            if not (isinstance(self.effect, SlideToNote) or isinstance(self.effect, ContinueSlideToNotePlusVolumeSlide)):
                self.period = note.period
            self.original_period = note.period
            
            
    def __str__(self):
        return "%4s %2x %s" % (period_table[self.note.period], self.note.sample_id, self.effect)
        
class Sequencer(object):
    def __init__(self, module, sequence_index = 0):
        self.module = module
        self.sequence_index = sequence_index - 1
        self.division_index = 63
        self.master_tick_counter = -1
        self.tick_counter = 5
        self.position_counter = -1
        
        self.system_clock = 7093789.2 #PAL for now
        #self.system_clock = 7159090.5 #NTSC
        self.tick_time = 1.0 / 50 #PAL for now, intial value only
        #self.tick_time = 1.0 / 60 #NTSC
        self.ticks_per_division = 6
        
        self.channels = [Channel(self) for n in range(4)]

        self.ended = False
        
        self.debug_print_division = True
        self.debug_print_tick = True
        
    pattern_index = property(lambda self: self.module.pattern_sequence[self.sequence_index])
    pattern = property(lambda self: self.module.patterns[self.pattern_index])
        
    def tick(self):
        self.update_state()
        if not self.ended:
            data = [channel.tick() for channel in self.channels]
            #print [len(d) for d in data]
            if self.ticks_per_division == 0:
                self.ended = True
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
                    if self.position_counter > self.module.num_positions:
                        self.ended = True
                        return
                    self.loop_pattern_counter = 0
                    self.loop_pattern_division_start = 0
                    self.loop_pattern_division_stop = 0
                for index, channel in enumerate(self.channels):
                    channel.new_note(self.pattern.divisions[self.division_index].channel_data[index])
                    
                if self.debug_print_division:
                    print "Position: %3i/%3i, Sequence: %3i, Pattern: %3i, Division: %2i, %s" % (self.position_counter, self.module.num_positions, self.sequence_index, self.pattern_index, self.division_index, [str(channel) for channel in self.channels])
            if self.debug_print_tick:
                print "Tick counter: %2i, Period: %s, Volume: %s" % (self.tick_counter, 
                                                                 ", ".join(["%3i" % (channel.period,) for channel in self.channels]),
                                                                 ", ".join(["%3i" % (channel.volume,) for channel in self.channels]))
            
if __name__ == "__main__":
    from modlib.sequencer.mod.loader import load
    import glob
    
    #filenames = ["/Volumes/Stuff/old_backup_cds/cd2/SCENE/Mod/MOUSEMOD.MOD",
    #    "/Volumes/Stuff/old_backup_cds/cd2/SCENE/Mod/NIM.MOD",
    #    "/Volumes/Stuff/old_backup_cds/cd2/SCENE/Mod/NOWHAT.MOD",
    #    "/Volumes/Stuff/old_backup_cds/cd2/SCENE/Mod2/OCEAN2ND.MOD",
    #    "/Volumes/Stuff/old_backup_cds/cd2/SCENE/Mod2/OCEAN.MOD",
    #    "/Volumes/Stuff/old_backup_cds/cd2/SCENE/Mod/CREATURE.MOD",
    #    "/Volumes/Stuff/old_backup_cds/cd2/SCENE/Mod/ASSASIN.MOD",
    #    "/Volumes/Stuff/old_backup_cds/cd2/SCENE/Mod2/COMIC3.MOD",
    #    "/Volumes/Stuff/old_backup_cds/cd2/SCENE/Mod2/PARALLAX.MOD",
    #    "/Volumes/Stuff/old_backup_cds/cd2/SCENE/Mod/RAINYDAY.MOD"]
    
    filenames = (glob.glob("/Volumes/Stuff/old_backup_cds/cd2/SCENE/Mod/*.MOD") +
                glob.glob("/Volumes/Stuff/old_backup_cds/cd2/SCENE/Mod2/*.MOD") +
                glob.glob("/Volumes/Stuff/old_backup_cds/cd2/SCENE/Mod3/*.MOD") + 
                glob.glob("/Volumes/Stuff/old_backup_cds/cd2/SCENE/Mod4/*.MOD"))
    for filename in filenames:
        print filename
        try:
            seq = Sequencer(load(filename))
            while seq.tick():
                pass
        except Exception, e:
            print "%s failed with error: %s" % (filename, e)
