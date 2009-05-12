class Sample(object):
    def __init__(self, name, length, finetune, volume, repeat_offset, repeat_length, data):
        self.name = name
        self.length = length
        self.finetune = finetune
        self.volume = volume
        self.repeat_offset = repeat_offset
        self.repeat_length = repeat_length
        self.data = data
        
    def get_data(self, offset, length):
        data = []
        if self.length > 0:
            if offset < self.length:
                if offset + length < self.length:
                    part = self.data[offset:offset + length]
                else:
                    part = self.data[offset:]
                data.append(part)
                length -= len(part)
                offset += len(part)
            if self.repeat_length > 0 and length > 0:
                offset -= self.length
                while length > 0:
                    offset %= self.repeat_length
                    if offset + length < self.repeat_length:
                        part = self.data[self.repeat_offset + offset:self.repeat_offset + offset + length]
                    else:
                        part = self.data[self.repeat_offset + offset:self.repeat_offset + self.repeat_length]
                    data.append(part)
                    length -= len(part)
                    offset += len(part)

        if len(data) == 0:
            data.append("\x80" * 100)

        return "".join(data)
    
if __name__ == "__main__":
    s = Sample("Jalla", 10, 0, 64, 4, 3, "aaaarepbbb")
    print s.get_data(0, 5)
    print s.get_data(5, 10)
    print s.get_data(15, 22)
        