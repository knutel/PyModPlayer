from construct import Adapter

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
