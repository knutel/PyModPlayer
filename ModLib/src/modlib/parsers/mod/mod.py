from __future__ import with_statement

from construct import *

sample_info = Struct("sample_info",
                String("name", 22, padchar="\x00"),
                UBInt16("length"),
                Embed(
                BitStruct(None,
                          Padding(4),
                          Nibble("finetune"))),
                UBInt8("volume"),
                UBInt16("repeat_offset"),
                UBInt16("repeat_length"))
     
def sample_length(ctx):
    if not hasattr(ctx, "_sample_counter"):
        ctx._sample_counter = 0
    length = ctx.sample_info[ctx._sample_counter].length
    ctx._sample_counter += 1
    if ctx._sample_counter > len(ctx.sample_info):
        delattr(ctx, "_sample_counter")
    return length
           
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
                                StrictRepeater(4, channel_data)))           
           
mod = Struct("mod", 
             String("title", 20, padchar="\x00"),
             StrictRepeater(31, sample_info),
             UBInt8("num_positions"),
             Padding(1),
             StrictRepeater(128, ULInt8("pattern_table")),
             Const(String("signature", 4), "M.K."),
             MetaRepeater(lambda ctx: int(max(ctx.pattern_table)) + 1,
                          patterns),
             MetaRepeater(lambda ctx: len(ctx.sample_info),
                          Bytes("samples", sample_length))
             )


if __name__ == "__main__":
    with file("/Volumes/Stuff/old_backup_cds/cd2/SCENE/Mod/MOUSEMOD.MOD", "rb") as f:
          print mod.parse_stream(f)

