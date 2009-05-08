        
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

class SlideUp(Effect):
    id = 1
    
    def tick(self):
        if self.sequencer.tick_counter != 0:
            self.channel.period -= self.x * 16 + self.y
            if self.channel.period < 113:
                self.channel.period = 113

class SlideDown(Effect):
    id = 2

class SlideToNote(Effect):
    id = 3

class Vibrato(Effect):
    id = 4

class ContinueSlideToNotePlusVolumeSlide(Effect):
    id = 5

class ContinueVibratoPlusVolumeSlide(Effect):
    id = 6

class Tremolo(Effect):
    id = 7

class SetSampleOffset(Effect):
    id = 9

class VolumeSlide(Effect):
    id = 10

    def tick(self):
        if self.sequencer.tick_counter != 0:
            if self.x > 0:
                self.channel.volume = min((64, self.channel.volume + self.x))
            else:
                self.channel.volume = max((0, self.channel.volume - self.y))

class PositionJump(Effect):
    id = 11

class SetVolume(Effect):
    id = 12

class PatternBreak(Effect):
    id = 13

class SetSpeed(Effect):
    id = 15
    
    def __init__(self, x, y, channel, sequencer):
        super(SetSpeed, self).__init__(x, y, channel, sequencer)
        speed = x * 16 + y
        if speed <= 32:
            sequencer.ticks_per_division = speed

class ToggleFilter(ExtendedEffect):
    id = 0

class FineslideUp(ExtendedEffect):
    id = 1
    
class FineslideDown(ExtendedEffect):
    id = 2

class ToggleGlissando(ExtendedEffect):
    id = 3

class SetVibratoWaveform(ExtendedEffect):
    id = 4

class SetFinetuneValue(ExtendedEffect):
    id = 5

class LoopPattern(ExtendedEffect):
    id = 6

class SetTremoloWaveform(ExtendedEffect):
    id = 7

class RetriggerSample(ExtendedEffect):
    id = 9

class FineVolumeSlideUp(ExtendedEffect):
    id = 10

class FineVolumeSlideDown(ExtendedEffect):
    id = 11

class CutSample(ExtendedEffect):
    id = 12

class DelaySample(ExtendedEffect):
    id = 13

class DelayPattern(ExtendedEffect):
    id = 14

class InvertLoop(ExtendedEffect):
    id = 15

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