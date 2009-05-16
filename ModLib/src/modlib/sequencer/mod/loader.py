from __future__ import with_statement
from modlib.parsers.mod.mod import mod
from modlib.sequencer.mod.module import Note, Division, Pattern, Module
from modlib.sequencer.mod.effect import effect_factory
from modlib.sequencer.mod.sample import Sample

def extract_patterns(module):
    patterns = []
    for pattern in module.patterns:
        divisions = []
        for division in pattern.channel_data:
            channels = []
            for channel in division:
                note = Note(channel.sample, channel.period, effect_factory(channel.effect, channel.x, channel.y))
                channels.append(note)
            divisions.append(Division(channels))
        patterns.append(Pattern(divisions))
    return patterns
                
def extract_samples(module):
    samples = []
    for index in range(31):
        info = module.sample_info[index]
        sample = Sample(info.name, info.length, info.finetune, info.volume, info.repeat_offset, info.repeat_length, module.samples[index])
        samples.append(sample)
    return samples

def load(filename):
    with file(filename, "rb") as f:
        module = mod.parse_stream(f)
        patterns = extract_patterns(module)
        samples = extract_samples(module)
        pattern_order = module.pattern_table
        return Module(module.title, module.num_positions, module.num_channels, patterns, samples, pattern_order)
