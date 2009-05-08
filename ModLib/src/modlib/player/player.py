from audioop import ratecv, mul, add, bias, tostereo
import pyglet
from pyglet.media import StreamingSource, AudioFormat, AudioData
from modlib.sequencer.mod.sequencer import Sequencer
from modlib.sequencer.mod.loader import load

class SequencerSource(StreamingSource):
    def __init__(self, filename):
        self.audio_format = AudioFormat(2, 8, 44100)
        self.sequencer = Sequencer(load(filename))
        self.ratecv_state = [None, None, None, None]
        for n in range(4):
            dummy, self.ratecv_state[n] = ratecv("\x80"*100, 1, 1, 100*50, 44100, self.ratecv_state[n])
        self.timestamp = 0.0
        
    def _get_audio_data(self, num_bytes):
        output = ["", "", "", ""]
        sound = self.sequencer.tick()
        if sound is None:
            return None
        for n in range(4):
            while True:
                output[n], self.ratecv_state[n] = ratecv(sound[n], 1, 1, len(sound[n])*50, 44100, self.ratecv_state[n])
                if len(output[n]) == 44100 / 50:
                    break
            output[n] = mul(output[n], 1, 0.5)
            output[n] = tostereo(output[n], 1, n % 2, (n + 1) % 2)
        left = add(output[0], output[2], 1)
        right = add(output[1], output[3], 1)
        stereo = add(left, right, 1)
        audio = AudioData(bias(stereo, 1, 128), 2 * 44100 / 50, self.timestamp, 1.0 / 50)
        self.timestamp += 1.0 / 50
        return audio 
    
        
if __name__ == "__main__":
    #s = SequencerSource("/Volumes/Stuff/old_backup_cds/cd2/SCENE/Mod/MOUSEMOD.MOD")
    #s = SequencerSource("/Volumes/Stuff/old_backup_cds/cd2/SCENE/Mod/NIM.MOD")
    s = SequencerSource("/Volumes/Stuff/old_backup_cds/cd2/SCENE/Mod/NOWHAT.MOD")
    s.play()
    pyglet.app.run()