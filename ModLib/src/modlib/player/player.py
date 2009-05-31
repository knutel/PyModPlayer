from audioop import ratecv, mul, add, bias, tostereo, lin2lin
import pyglet
from pyglet.media import StreamingSource, AudioFormat, AudioData
from modlib.sequencer.mod.sequencer import Sequencer, dummy_sample
from modlib.sequencer.mod.loader import load

def mix(samples, depth):
    result = samples[0]
    for sample in samples[1:]:
        result = add(result, sample, depth)
    return result

class SequencerSource(StreamingSource):
    def __init__(self, filename, sequence_index=0):
        self.channels = 2
        self.bits = 16
        self.bytes = self.bits / 8
        self.rate = 44100
        self.audio_format = AudioFormat(self.channels, self.bits, self.rate)
        self.sequencer = Sequencer(load(filename))
        self.sequencer.debug_print_division = False
        self.sequencer.debug_print_tick = False
        while self.sequencer.sequence_index < sequence_index - 1:
            self.sequencer.tick()
        self.sequencer.debug_print_division = True
        self.sequencer.debug_print_tick = False
        while self.sequencer.sequence_index < sequence_index:
            self.sequencer.tick()

        self.ratecv_state = [None] * self.sequencer.module.num_channels
        self._ratecv([dummy_sample] * self.sequencer.module.num_channels)
        self.timestamp = 0.0
        self.muted = []
        
    def _get_tick_time(self):
        return self.sequencer.tick_time
    tick_time = property(_get_tick_time)
    
    def _mute(self, sound):
        for n in range(len(sound)):
            if n in self.muted:
                sound[n] = dummy_sample
    
    def _ratecv(self, sounds):
        output = []
        for n, (sound, state) in enumerate(zip(sounds, self.ratecv_state)):
            while True:
                o, state = ratecv(sound, self.bytes, 1, 
                              int(round(len(sound) / self.tick_time) / self.bytes), 
                              self.rate, 
                              state)
                #Length may be off by one, so process until OK
                if len(o) == int(round(self.rate * self.tick_time * self.bytes)):
                    break
            output.append(o)
            self.ratecv_state[n] = state
        return output
    
    def _get_audio_length(self):
        return int(self.channels * self.bytes * self.rate * self.tick_time)
    audio_length = property(_get_audio_length)
    
    def _scale(self, output):
        return [mul(o, self.bytes, 1.0 / (len(output) / self.channels)) for o in output]
    
    def _tostereo(self, output):
        return [tostereo(o, self.bytes, n % 2, (n + 1) % 2) for n, o in enumerate(output)]
        
    def _get_audio_data(self, num_bytes):
        sound = self.sequencer.tick()
        if sound is None:
            pyglet.app.exit()
            return
        self._mute(sound)
        sound = [lin2lin(s, 1, self.bytes) for s in sound]
        output = self._ratecv(sound)
        output = self._scale(output)
        output = self._tostereo(output)
        left = mix(output[::2], self.bytes)
        right = mix(output[1::2], self.bytes)
        stereo = add(left, right, self.bytes)
        audio = AudioData(stereo, self.audio_length, self.timestamp, self.tick_time)
        self.timestamp += self.tick_time
        return audio 
    
    def mute(self, channels):
        self.muted = channels
        
if __name__ == "__main__":
    import sys
    s = SequencerSource(sys.argv[1])
    #s.mute((0, 2, 3))
    s.play()
    pyglet.app.run()