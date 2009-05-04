from __future__ import with_statement

from construct import *

sample_info = Struct("sample_info",
                String("name", 22, padchar="\x00"),
                UBInt16("length"),
                Embed(
                BitStruct(None,
                          Padding(4),
                          Nibble("fine_tune"))),
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
                    arpeggio = 0,
                    slide_up = 1,
                    slide_down = 2,
                    slide_to_note = 3,
                    vibrato = 4,
                    continue_slide_to_note_plus_volume_slide = 5,
                    continue_vibrato_plus_volume_slide = 6,
                    tremolo = 7,
                    set_sample_offset = 9,
                    volume_slide = 10,
                    position_jump = 11,
                    set_volume = 12,
                    pattern_break = 13,
                    extended_effect = 14,
                    set_speed = 15)

extended_effect = Enum(Nibble("extended_effect"),
                       toggle_filter = 0,
                       fineslide_up = 1,
                       fineslide_down = 2,
                       toggle_glissando = 3,
                       set_vibrato_waveform = 4,
                       set_finetune_value = 5,
                       loop_pattern = 6,
                       set_tremolo_waveform = 7,
                       retrigger_sample = 9,
                       fine_volume_slide_up = 10,
                       fine_volume_slide_down = 11,
                       cut_sample = 12,
                       delay_sample = 13,
                       delay_pattern = 14,
                       invert_loop = 15)
    
channel_data = BitStruct("channel_data",
                         Nibble("sample_hi"),
                         BitField("period", 12),
                         Nibble("sample_lo"),
                         major_effect,
                         Embed(IfThenElse(None, 
                                    lambda ctx: ctx.major_effect == "extended_effect",
                                    Struct(None, extended_effect, Nibble("x")),
                                    Struct(None, Nibble("x"), Nibble("y")))),
                         Value("sample", lambda ctx: ctx.sample_hi << 4 | ctx.sample_lo)
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
    with file("/Volumes/Stuff/old_backup_cds/cd2/SCENE/Mod/AASULV.MOD", "rb") as f:
          print mod.parse_stream(f)

