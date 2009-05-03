from __future__ import with_statement

from construct import *
from construct.macros import ULInt16, ULInt8
from construct.macros import BitField

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
           

class EffectAdapter(Adapter):
    def _decode(self, obj, context):
        return obj

channel_data = BitStruct("channel_data",
                         Nibble("w"),
                         BitField("x", 12),
                         Nibble("y"),
                         BitField("z", 12),
                        )

patterns = Struct("patterns",
                 StrictRepeater(64,
                                StrictRepeater(4, EffectAdapter(channel_data))))           
           
mod = Struct("mod", 
             String("title", 20, padchar="\x00"),
             StrictRepeater(31, sample_info),
             UBInt8("num_positions"),
             Padding(1),
             StrictRepeater(128, ULInt8("pattern_table")),
             String("signature", 4),
             MetaRepeater(lambda ctx: int(max(ctx.pattern_table)) + 1,
                          patterns),
             MetaRepeater(lambda ctx: len(ctx.sample_info),
                          Bytes("samples", sample_length))
             )


if __name__ == "__main__":
    with file("/Volumes/Stuff/old_backup_cds/cd2/SCENE/Mod/MOUSEMOD.MOD", "rb") as f:
         print mod.parse_stream(f)

