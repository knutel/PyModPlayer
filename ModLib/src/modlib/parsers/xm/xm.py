from __future__ import with_statement
from construct import *
from construct.macros import BitField

class ChannelDataAdapter(Adapter):
    def _decode(self, obj, context):
        delattr(obj, "effect_parameter_follows")
        delattr(obj, "effect_type_follows")
        delattr(obj, "volume_column_follows")
        delattr(obj, "instrument_follows")
        delattr(obj, "note_follows")
        delattr(obj, "packed")
        return obj

version = Struct("version", Byte("minor"), Byte("major"))

flags = BitStruct("flags", Padding(15), Bit("frequency_table"))

pattern_order = StrictRepeater(256, Byte("pattern_order"))

channel_data = ChannelDataAdapter(Struct("channel_data",
             Embed(BitStruct(None,
                             Bit("packed"),
                             Embed(IfThenElse(None,
                                        lambda ctx: ctx.packed == 0,
                                        Struct(None, BitField("note", 7),
                                               Value("effect_parameter_follows", 1),
                                               Value("effect_type_follows", 1),
                                               Value("volume_column_follows", 1),
                                               Value("instrument_follows", 1),
                                               Value("note_follows", 1)),
                                        Struct(None, 
                                               Padding(2),
                                               Bit("effect_parameter_follows"),
                                               Bit("effect_type_follows"),
                                               Bit("volume_column_follows"),
                                               Bit("instrument_follows"),
                                               Bit("note_follows"))))
                             )),
                             If(lambda ctx: ctx.note_follows,
                                Byte("note")),
                             If(lambda ctx: ctx.instrument_follows,
                                Byte("instrument")),
                             If(lambda ctx: ctx.volume_column_follows,
                                Byte("volume_column")),
                             If(lambda ctx: ctx.effect_type_follows,
                                Byte("effect_type")),
                             If(lambda ctx: ctx.effect_parameter_follows,
                                Byte("effect_parameter"))))

row = MetaRepeater(lambda ctx: ctx._.number_of_channels,
                   channel_data)

pattern = Struct("pattern",
                 ULInt32("pattern_header_length"),
                 Const(Byte("packing_type"), 0),
                 ULInt16("number_of_rows_in_pattern"),
                 ULInt16("packed_pattern_data_size"),
                 MetaRepeater(lambda ctx: ctx.number_of_rows_in_pattern, row)
                 )

patterns = MetaRepeater(lambda ctx: ctx.number_of_patterns,
                        pattern)

envelope_point = Struct("envelope_point",
                        ULInt16("x"),
                        ULInt16("y"))

sample_info = Struct("sample_info",
                     ULInt32("header_size"),
                     StrictRepeater(96, Byte("sample_number_vs_note")),
                     StrictRepeater(12, Rename("volume_envelope", envelope_point)),
                     StrictRepeater(12, Rename("panning_envelope", envelope_point)),
                     Byte("number_of_volume_points"),
                     Byte("number_of_panning_points"),
                     Byte("volume_sustain_point"),
                     Byte("volume_loop_start_point"),
                     Byte("volume_loop_end_point"),
                     Byte("panning_sustain_point"),
                     Byte("panning_loop_start_point"),
                     Byte("panning_loop_end_point"),
                     Byte("volume_type"), #bits...
                     Byte("panning_type"), #bits...
                     Byte("vibrato_type"),
                     Byte("vibrato_sweep"),
                     Byte("vibrato_depth"),
                     Byte("vibrato_rate"),
                     ULInt16("volume_fadeout"),
                     Padding(11 * 2))

sample = Struct("sample",
                ULInt32("length"),
                ULInt32("loop_start"),
                ULInt32("loop_length"),
                Byte("volume"),
                SLInt8("finetune"),
                BitStruct("type",
                          Padding(3),
                          Bit("is_16_bit"),
                          Padding(2),
                          BitField("loop_type", 2)),
                Byte("panning"),
                SLInt8("relative_note_number"),
                Padding(1),
                String("name", 22),
                String("data", lambda ctx: ctx.length * (ctx.type.is_16_bit + 1))
                )

instrument = Struct("instrument",
                    ULInt32("size"),
                    String("name", 22),
                    Byte("type"),
                    ULInt16("number_of_samples"),
                    If(lambda ctx: ctx.number_of_samples > 0,
                       Struct("samples",
                              sample_info)),
                    MetaRepeater(lambda ctx: ctx.number_of_samples,
                                 sample))

instruments = MetaRepeater(14, #lambda ctx: ctx.number_of_instruments,
                           instrument)

xm = Struct("xm", 
            String("id", 17),
            String("name", 20, padchar=" "),
            Const(Byte(None), 0x1a),
            String("tracker_name", 20, padchar=" "),
            version,
            ULInt32("header_size"),
            ULInt16("song_length"),
            ULInt16("restart_position"),
            ULInt16("number_of_channels"),
            ULInt16("number_of_patterns"),
            ULInt16("number_of_instruments"),
            flags,
            ULInt16("default_tempo"),
            ULInt16("default_bpm"),
            pattern_order,
            patterns,
            instruments
            )

if __name__ == "__main__":
    import sys
    with file(sys.argv[1], "rb") as f:
        xmodule = xm.parse_stream(f)
        
    print xmodule