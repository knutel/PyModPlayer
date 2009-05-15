from audioop import ratecv, mul, add, bias, tostereo, lin2lin
import pyglet
from pyglet.media import StreamingSource, AudioFormat, AudioData
from modlib.sequencer.mod.sequencer import Sequencer
from modlib.sequencer.mod.loader import load

def mix(samples, depth):
    result = samples[0]
    for sample in samples[1:]:
        result = add(result, sample, depth)
    return result

class SequencerSource(StreamingSource):
    def __init__(self, filename, sequence_index=0):
        self.audio_format = AudioFormat(2, 16, 44100)
        self.sequencer = Sequencer(load(filename))
        self.sequencer.debug_print_division = False
        self.sequencer.debug_print_tick = False
        while self.sequencer.sequence_index < sequence_index - 1:
            self.sequencer.tick()
        self.sequencer.debug_print_division = True
        self.sequencer.debug_print_tick = False
        while self.sequencer.sequence_index < sequence_index:
            self.sequencer.tick()

        self.ratecv_state = [None for n in range(self.sequencer.module.num_channels)]
        for n in range(self.sequencer.module.num_channels):
            dummy, self.ratecv_state[n] = ratecv("\x80"*100, 1, 1, 100*50, 44100, self.ratecv_state[n])
        self.timestamp = 0.0
        self.muted = []
        
    def _get_audio_data(self, num_bytes):
        output = [None for n in range(self.sequencer.module.num_channels)]
        sound = self.sequencer.tick()
        tick_time = self.sequencer.tick_time
        if sound is None:
            pyglet.app.exit()
            return
        for n in range(self.sequencer.module.num_channels):
            if n in self.muted:
                sound[n] = "\x80"*100
        for n in range(self.sequencer.module.num_channels):
            sound[n] = lin2lin(sound[n], 1, 2)
            while True:
                output[n], self.ratecv_state[n] = ratecv(sound[n], 2, 1, int(len(sound[n]) / tick_time) / 2, 44100, self.ratecv_state[n])
                if len(output[n]) == int(round(44100 * tick_time * 2)):
                    break
            output[n] = mul(output[n], 2, 1.0 / (self.sequencer.module.num_channels / 2))
            output[n] = tostereo(output[n], 2, n % 2, (n + 1) % 2)
        left = mix([output[n] for n in range(0, self.sequencer.module.num_channels, 2)] , 2)
        right = mix([output[n] for n in range(1, self.sequencer.module.num_channels, 2)] , 2)
        stereo = add(left, right, 2)
        audio = AudioData(stereo, int(2 * 2 * 44100 * tick_time), self.timestamp, tick_time)
        self.timestamp += tick_time
        return audio 
    
    def mute(self, channels):
        self.muted = channels
        
if __name__ == "__main__":
    #s = SequencerSource("/Volumes/Stuff/old_backup_cds/cd2/SCENE/Mod/MOUSEMOD.MOD")
    #s = SequencerSource("/Volumes/Stuff/old_backup_cds/cd2/SCENE/Mod/NIM.MOD")
    #s = SequencerSource("/Volumes/Stuff/old_backup_cds/cd2/SCENE/Mod/NOWHAT.MOD")
    #s = SequencerSource("/Volumes/Stuff/old_backup_cds/cd2/SCENE/Mod2/OCEAN2ND.MOD")
    #s = SequencerSource("/Volumes/Stuff/old_backup_cds/cd2/SCENE/Mod2/OCEAN.MOD")
    #s = SequencerSource("/Volumes/Stuff/old_backup_cds/cd2/SCENE/Mod/CREATURE.MOD")
    #s = SequencerSource("/Volumes/Stuff/old_backup_cds/cd2/SCENE/Mod/ASSASIN.MOD")
    #s = SequencerSource("/Volumes/Stuff/old_backup_cds/cd2/SCENE/Mod2/COMIC3.MOD")
    #s = SequencerSource("/Volumes/Stuff/old_backup_cds/cd2/SCENE/Mod2/PARALLAX.MOD")
    #s = SequencerSource("/Volumes/Stuff/old_backup_cds/cd2/SCENE/Mod/RAINYDAY.MOD")
    #s = SequencerSource("/Volumes/Stuff/old_backup_cds/cd2/SCENE/Mod/GUITARSL.MOD", 9) #Tremolo
    #Something fishy s = SequencerSource("/Volumes/Stuff/old_backup_cds/cd2/SCENE/Mod/SHOCK.MOD") #Tremolo
    #s = SequencerSource("/Volumes/Stuff/old_backup_cds/cd2/SCENE/Mod/BRASSCON.MOD") #FLT4
    #s = SequencerSource("/Volumes/Stuff/old_backup_cds/cd2/SCENE/Mod/BUD.MOD") #6CHN
    # ecco sounds strange s = SequencerSource("/Volumes/Stuff/old_backup_cds/cd2/SCENE/Mod/ANTARES.MOD") #8CHN
    #s = SequencerSource("/Volumes/Stuff/old_backup_cds/cd2/SCENE/Mod/PAINTRO.MOD") #8CHN
    #s = SequencerSource("/Volumes/Stuff/old_backup_cds/cd2/SCENE/Mod/SIMPACT.MOD") #8CHN
    #s = SequencerSource("/Volumes/Stuff/old_backup_cds/cd2/SCENE/Mod/WAIT7.MOD") #8CHN
    #s = SequencerSource("/Volumes/Stuff/old_backup_cds/cd2/SCENE/Mod4/CHIME94.MOD") #8CHN
    #s = SequencerSource("/Volumes/Stuff/old_backup_cds/cd2/SCENE/Mod/SARA.MOD") #12CH
    s = SequencerSource("/Volumes/Stuff/old_backup_cds/cd2/SCENE/Mod/DOPE.MOD") #28CH
    #s = SequencerSource("/Volumes/Stuff/old_backup_cds/cd2/SCENE/Mod/SW-OPUS1.MOD") #28CH
    # does not load: s = SequencerSource("/Volumes/Stuff/old_backup_cds/cd2/SCENE/Mod/STARDME.MOD")
    #s.mute((0, 2, 3))
    s.play()
    pyglet.app.run()