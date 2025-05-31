class ndarray(list):
    def tolist(self):
        return list(self)

    def __getitem__(self, item):
        result = super().__getitem__(item)
        if isinstance(item, slice):
            return ndarray(result)
        return result

    def astype(self, dtype):
        return self

uint8 = 'uint8'

def array(seq):
    return ndarray(seq)

def frombuffer(buf, dtype=None):
    return ndarray(buf)





