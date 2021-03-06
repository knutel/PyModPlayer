from modlib.sequencer.mod.tables import period_table, sine_table

class ExtendedEffect(object):
    def __init__(self, x, channel, sequencer):
        self.x = x
        self.channel = channel
        self.sequencer = sequencer
        
    def tick(self):
        pass
    
    def __str__(self):
        return "%X%X%X" % (14, self.id, self.x)
        
class Effect(ExtendedEffect):
    def __init__(self, x, y, channel, sequencer):
        super(Effect, self).__init__(x, channel, sequencer)
        self.y = y

    def __str__(self):
        return "%X%X%X" % (self.id, self.x, self.y)
        
class Arpeggio(Effect):
    id = 0
    
    def tick(self):
        if self.x != 0 and self.y != 0:
            if self.channel.original_period != 0:
                if self.sequencer.master_tick_counter % 3 == 0:
                    self.channel.period = self.channel.original_period
                if self.sequencer.master_tick_counter % 3 == 1:
                    self.channel.period = period_table.finetune(self.channel.original_period, self.x)
                elif self.sequencer.master_tick_counter % 3 == 2:
                    self.channel.period = period_table.finetune(self.channel.original_period, self.y) 

class SlideUp(Effect):
    id = 1
    
    def tick(self):
        if self.sequencer.tick_counter != 0:
            self.channel.period -= self.x * 16 + self.y

class SlideDown(Effect):
    id = 2

    def tick(self):
        if self.sequencer.tick_counter != 0:
            self.channel.period += self.x * 16 + self.y

class SlideToNote(Effect):
    id = 3

    def __init__(self, x, y, channel, sequencer):
        super(SlideToNote, self).__init__(x, y, channel, sequencer)
        slide_to_note_speed = x * 16 + y
        if slide_to_note_speed != 0:
            self.channel.slide_to_note_speed = slide_to_note_speed

    def tick(self):
        if self.channel.period < self.channel.original_period:
            if self.channel.period + self.channel.slide_to_note_speed > self.channel.original_period:
                self.channel.period = self.channel.original_period
            else:
                self.channel.period += self.channel.slide_to_note_speed
        else:
            if self.channel.period - self.channel.slide_to_note_speed < self.channel.original_period:
                self.channel.period = self.channel.original_period
            else:
                self.channel.period -= self.channel.slide_to_note_speed

class Vibrato(Effect):
    id = 4
    
    def __init__(self, x, y, channel, sequencer):
        super(Vibrato, self).__init__(x, y, channel, sequencer)
        if x > 0 and y > 0:
            self.channel.vibrato_speed = x
            self.channel.vibrato_depth = y
            self.channel.vibrato_position = 0
        
    def tick(self):
        self.channel.period = self.channel.original_period + sine_table[self.channel.vibrato_position % len(sine_table)] * self.channel.vibrato_depth / 128
        self.channel.vibrato_position += self.channel.vibrato_speed
        

class ContinueSlideToNotePlusVolumeSlide(Effect):
    id = 5

    def __init__(self, x, y, channel, sequencer):
        super(ContinueSlideToNotePlusVolumeSlide, self).__init__(x, y, channel, sequencer)
        self.slide_to_note = SlideToNote(0, 0, channel, sequencer)
        self.volume_slide = VolumeSlide(x, y, channel, sequencer)
        
    def tick(self):
        self.slide_to_note.tick()
        self.volume_slide.tick()

class ContinueVibratoPlusVolumeSlide(Effect):
    id = 6

    def __init__(self, x, y, channel, sequencer):
        super(ContinueVibratoPlusVolumeSlide, self).__init__(x, y, channel, sequencer)
        self.vibrato = Vibrato(0, 0, channel, sequencer)
        self.volume_slide = VolumeSlide(x, y, channel, sequencer)
        
    def tick(self):
        self.vibrato.tick()
        self.volume_slide.tick()

class Tremolo(Effect):
    id = 7

    def __init__(self, x, y, channel, sequencer):
        print "Tremolo"
        super(Tremolo, self).__init__(x, y, channel, sequencer)
        if x > 0 and y > 0:
            self.channel.tremolo_speed = x
            self.channel.tremolo_depth = y
            self.channel.tremolo_position = 0
        
    def tick(self):
        self.channel.volume = self.channel.original_volume + sine_table[self.channel.tremolo_position % len(sine_table)] * self.channel.tremolo_depth / 64
        self.channel.tremolo_position += self.channel.tremolo_speed

class SetSampleOffset(Effect):
    id = 9
    
    def __init__(self, x, y, channel, sequencer):
        super(SetSampleOffset, self).__init__(x, y, channel, sequencer)
        channel.sample_offset = (x * 4096 + y * 256) * 2

class VolumeSlide(Effect):
    id = 10

    def tick(self):
        if self.sequencer.tick_counter != 0:
            if self.x > 0:
                self.channel.volume = self.channel.volume + self.x
            else:
                self.channel.volume = self.channel.volume - self.y

class PositionJump(Effect):
    id = 11

    def tick(self):
        if self.sequencer.tick_counter == (self.sequencer.ticks_per_division - 1):
            self.sequencer.sequence_index = self.x * 16 + self.y - 1
            self.sequencer.division_index = 63
             
class SetVolume(Effect):
    id = 12

    def __init__(self, x, y, channel, sequencer):
        super(SetVolume, self).__init__(x, y, channel, sequencer)
        channel.volume = x * 16 + y

class PatternBreak(Effect):
    id = 13

    def tick(self):
        if self.sequencer.tick_counter == (self.sequencer.ticks_per_division - 1):
            self.sequencer.division_index = self.x * 10 + self.y - 1
            if self.sequencer.division_index < 0:
                self.sequencer.division_index = 63
            else:
                self.sequencer.sequence_index += 1

class SetSpeed(Effect):
    id = 15
    
    def __init__(self, x, y, channel, sequencer):
        super(SetSpeed, self).__init__(x, y, channel, sequencer)
        speed = x * 16 + y
        if speed <= 32:
            sequencer.ticks_per_division = speed
        else:
            sequencer.tick_time = 1.0 / ((speed * 4 * 6) / 60)

class ToggleFilter(ExtendedEffect):
    id = 0
    
    #This will never be implemented

class FineslideUp(ExtendedEffect):
    id = 1
    
    def __init__(self, x, channel, sequencer):
        super(FineslideUp, self).__init__(x, channel, sequencer)
        self.channel.period -= self.x
    
class FineslideDown(ExtendedEffect):
    id = 2

    def __init__(self, x, channel, sequencer):
        super(FineslideDown, self).__init__(x, channel, sequencer)
        self.channel.period += self.x

class ToggleGlissando(ExtendedEffect):
    id = 3

    def tick(self):
        raise NotImplementedError()

class SetVibratoWaveform(ExtendedEffect):
    id = 4

    def tick(self):
        raise NotImplementedError()

class SetFinetuneValue(ExtendedEffect):
    id = 5

    def tick(self):
        raise NotImplementedError()

class LoopPattern(ExtendedEffect):
    id = 6
    
    def __init__(self, x, channel, sequencer):
        super(LoopPattern, self).__init__(x, channel, sequencer)
        if self.x == 0:
            self.channel.loop_pattern_division_start = self.sequencer.division_index - 1
        elif self.channel.loop_pattern_counter == 0:
            self.channel.loop_pattern_counter = self.x
            self.channel.loop_pattern_division_stop = self.sequencer.division_index
        elif self.channel.loop_pattern_division_stop == self.sequencer.division_index:
            self.channel.loop_pattern_counter -= 1
            
    def tick(self):
        if self.x > 0 and self.sequencer.tick_counter == (self.sequencer.ticks_per_division - 1):
            if self.channel.loop_pattern_counter > 0 and self.channel.loop_pattern_division_stop == self.sequencer.division_index:
                self.sequencer.division_index = self.channel.loop_pattern_division_start
        

class SetTremoloWaveform(ExtendedEffect):
    id = 7

    def tick(self):
        raise NotImplementedError()

class RetriggerSample(ExtendedEffect):
    id = 9
    
    def tick(self):
        if self.x != 0 and (self.sequencer.tick_counter % self.x) == 0:
            self.channel.sample_offset = 0

class FineVolumeSlideUp(ExtendedEffect):
    id = 10

    def __init__(self, x, channel, sequencer):
        super(FineVolumeSlideUp, self).__init__(x, channel, sequencer)
        self.channel.volume += self.x

class FineVolumeSlideDown(ExtendedEffect):
    id = 11

    def __init__(self, x, channel, sequencer):
        super(FineVolumeSlideDown, self).__init__(x, channel, sequencer)
        self.channel.volume -= self.x

class CutSample(ExtendedEffect):
    id = 12

    def tick(self):
        if self.sequencer.tick_counter >= self.x:
            self.channel.volume = 0
    
class DelaySample(ExtendedEffect):
    id = 13

    def __init__(self, x, channel, sequencer):
        super(DelaySample, self).__init__(x, channel, sequencer)
        self.volume = self.channel.volume
        self.sample_offset = self.channel.sample_offset
        self.channel.volume = 0

    def tick(self):
        if self.sequencer.tick_counter == self.x:
            self.channel.sampe_offset = self.sample_offset
            self.channel.volume = self.volume

class DelayPattern(ExtendedEffect):
    id = 14

    def __init__(self, x, channel, sequencer):
        super(DelayPattern, self).__init__(x, channel, sequencer)
        self.delaying = False

    def tick(self):
        if self.sequencer.tick_counter == self.sequencer.ticks_per_division - 1:
            if not self.delaying:
                self.sequencer.ticks_per_division += self.x
                self.delaying = True
            else:
                self.sequencer.ticks_per_division -= self.x
                self.sequencer.tick_counter -= self.x


class InvertLoop(ExtendedEffect):
    id = 15

    def tick(self):
        raise NotImplementedError()

effects = dict([(klass.__name__, klass) for klass in [Arpeggio,
                                                  SlideUp,
                                                  SlideDown,
                                                  SlideToNote,
                                                  Vibrato,
                                                  ContinueSlideToNotePlusVolumeSlide,
                                                  ContinueVibratoPlusVolumeSlide,
                                                  Tremolo,
                                                  SetSampleOffset,
                                                  VolumeSlide,
                                                  PositionJump,
                                                  SetVolume,
                                                  PatternBreak,
                                                  SetSpeed,
                                                  ]])

extended_effects = dict([(klass.__name__, klass) for klass in [ToggleFilter,
                                                           FineslideUp,
                                                           FineslideDown,
                                                           ToggleGlissando,
                                                           SetVibratoWaveform,
                                                           SetFinetuneValue,
                                                           LoopPattern,
                                                           SetTremoloWaveform,
                                                           RetriggerSample,
                                                           FineVolumeSlideUp,
                                                           FineVolumeSlideDown,
                                                           CutSample,
                                                           DelaySample,
                                                           DelayPattern,
                                                           InvertLoop,
                                                           ]])

def effect_factory(effect, x, y=None):
    if y is None:
        return lambda channel, sequencer: extended_effects[effect](x, channel, sequencer)
    else:
        return lambda channel, sequencer: effects[effect](x, y, channel, sequencer)
    
if __name__ == "__main__":
    print effect_factory("Arpeggio", 0, 0)
    print effect_factory("SetSpeed", 4, 5)(None, None)
    print effect_factory("CutSample", 5)(None, None)