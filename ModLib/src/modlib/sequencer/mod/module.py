
class Note(object):
    def __init__(self, sample_id, period, effect=None):
        self.sample_id = sample_id
        self.period = period
        self.effect = effect

class Division(object):
    def __init__(self, channel_data):
        self.channel_data = channel_data

class Pattern(object):
    def __init__(self, divisions):
        self.divisions = divisions
        
class Module(object):
    def __init__(self, title, num_positions, num_channels, patterns, samples, pattern_sequence):
        self.title = title
        self.num_positions = num_positions
        self.num_channels = num_channels
        self.patterns = patterns
        self.samples = samples
        self.pattern_sequence = pattern_sequence
