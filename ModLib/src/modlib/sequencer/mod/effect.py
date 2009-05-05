        
class ExtendedEffect(object):
    def __init__(self, x):
        self.x = x
        
class Effect(ExtendedEffect):
    def __init__(self, x, y):
        super(Effect, self).__init__(x)
        self.y = y
        
class Arpeggio(Effect):
    pass

class SlideUp(Effect):
    pass

class SlideDown(Effect):
    pass

class SlideToNote(Effect):
    pass

class Vibrato(Effect):
    pass

class ContinueSlideToNotePlusVolumeSlide(Effect):
    pass

class ContinueVibratoPlusVolumeSlide(Effect):
    pass

class Tremolo(Effect):
    pass

class SetSampleOffset(Effect):
    pass

class VolumeSlide(Effect):
    pass

class PositionJump(Effect):
    pass

class SetVolume(Effect):
    pass

class PatternBreak(Effect):
    pass

class SetSpeed(Effect):
    pass

class ToggleFilter(ExtendedEffect):
    pass

class FineslideUp(ExtendedEffect):
    pass

class FineslideDown(ExtendedEffect):
    pass

class ToggleGlissando(ExtendedEffect):
    pass

class SetVibratoWaveform(ExtendedEffect):
    pass

class SetFinetuneValue(ExtendedEffect):
    pass

class LoopPattern(ExtendedEffect):
    pass

class SetTremoloWaveform(ExtendedEffect):
    pass

class RetriggerSample(ExtendedEffect):
    pass

class FineVolumeSlideUp(ExtendedEffect):
    pass

class FineVolumeSlideDown(ExtendedEffect):
    pass

class CutSample(ExtendedEffect):
    pass

class DelaySample(ExtendedEffect):
    pass

class DelayPattern(ExtendedEffect):
    pass

class InvertLoop(ExtendedEffect):
    pass

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
    if effect == "Arpeggio" and x == 0 and y == 0:
        return None
    if y is None:
        return extended_effects[effect](x)
    else:
        return effects[effect](x, y)
    
if __name__ == "__main__":
    print effect_factory("Arpeggio", 0, 0)
    print effect_factory("SetSpeed", 4, 5)
    print effect_factory("CutSample", 5)