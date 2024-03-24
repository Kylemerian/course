

class VM:
    def __init__(self):
        self.classes = list()
        self.methods = list()
        self.fields = list()
        self.threads = list()
        self.threads.append(Thread())

class Thread:
    def __init__(self):
        self.frames = list()
        self.constPool = list()
        self.exception = 0
        self.frames.append(Frame())

class Frame:
    def __init__(self):
        self.registers = dict()
        self.registers['acc'] = Register()
        self.registers['pc'] = Register()
        for i in range(256):
            self.registers['r' + str(i)] = Register()

class Register:
        def __init__(self):
            self.value = 0
            self._type = 0