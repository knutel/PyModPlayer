from __future__ import with_statement

from construct import *

__version__ = "$Id$"

class WordsToBytesAdapter(Adapter):
    def _decode(self, obj, ctx):
        return obj * 2
    
    def _encode(self, obj, ctx):
        return obj / 2

def sample_length(ctx):
    if not hasattr(ctx, "_sample_counter"):
        ctx._sample_counter = 0
    length = ctx.sample_info[ctx._sample_counter].length
    ctx._sample_counter += 1
    if ctx._sample_counter > len(ctx.sample_info):
        delattr(ctx, "_sample_counter")
    return length

signature_vs_channels = {"M.K.": 4, 
                         "M!K!": 4, 
                         "6CHN": 6, 
                         "8CHN": 8, 
                         "12CH": 12, 
                         "28CH": 28, 
                         "FLT4": 4,
                        }

sample_info = Struct("sample_info",
                String("name", 22, padchar="\x00"),
                WordsToBytesAdapter(UBInt16("length")),
                Embed(BitStruct(None,
                          Padding(4),
                          BitField("finetune", 4, signed=True))),
                UBInt8("volume"),
                WordsToBytesAdapter(UBInt16("repeat_offset")),
                WordsToBytesAdapter(UBInt16("repeat_length")))
     
           
major_effect = Enum(Nibble("major_effect"),
                    Arpeggio = 0,
                    SlideUp = 1,
                    SlideDown = 2,
                    SlideToNote = 3,
                    Vibrato = 4,
                    ContinueSlideToNotePlusVolumeSlide = 5,
                    ContinueVibratoPlusVolumeSlide = 6,
                    Tremolo = 7,
                    SetSampleOffset = 9,
                    VolumeSlide = 10,
                    PositionJump = 11,
                    SetVolume = 12,
                    PatternBreak = 13,
                    extended_effect = 14, #This is never seen outside parser
                    SetSpeed = 15)

extended_effect = Enum(Nibble("extended_effect"),
                       ToggleFilter = 0,
                       FineslideUp = 1,
                       FineslideDown = 2,
                       ToggleGlissando = 3,
                       SetVibratoWaveform = 4,
                       SetFinetuneValue = 5,
                       LoopPattern = 6,
                       SetTremoloWaveform = 7,
                       RetriggerSample = 9,
                       FineVolumeSlideUp = 10,
                       FineVolumeSlideDown = 11,
                       CutSample = 12,
                       DelaySample = 13,
                       DelayPattern = 14,
                       InvertLoop = 15)
    
channel_data = BitStruct("channel_data",
                         Nibble("sample_hi"),
                         BitField("period", 12),
                         Nibble("sample_lo"),
                         major_effect,
                         Embed(IfThenElse(None, 
                                    lambda ctx: ctx.major_effect == "extended_effect",
                                    Struct(None, extended_effect, Nibble("x"), Value("y", lambda ctx: None), Alias("effect", "extended_effect")),
                                    Struct(None, Nibble("x"), Nibble("y"), Alias("effect", "major_effect")))),
                         Value("sample", lambda ctx: ctx.sample_hi << 4 | ctx.sample_lo),
                        )

patterns = Struct("patterns",
                 StrictRepeater(64,
                                MetaRepeater(lambda ctx: ctx._.num_channels, channel_data)))           
           
mod = Struct("mod", 
             String("title", 20, padchar="\x00"),
             StrictRepeater(31, sample_info),
             UBInt8("num_positions"),
             Padding(1),
             StrictRepeater(128, ULInt8("pattern_table")),
             OneOf(String("signature", 4), signature_vs_channels.keys()),
             Value("num_channels", lambda ctx: signature_vs_channels[ctx.signature]),
             MetaRepeater(lambda ctx: int(max(ctx.pattern_table)) + 1,
                          patterns),
             MetaRepeater(lambda ctx: len(ctx.sample_info),
                          Bytes("samples", sample_length))
             )


if __name__ == "__main__":
    with file("/Volumes/Stuff/old_backup_cds/cd2/SCENE/Mod/MOUSEMOD.MOD", "rb") as f:
          print mod.parse_stream(f)

