

class VM:
    def __init__(self):
        self.classes = list()
        self.methods = list()
        self.fields = list()
        self.threads = [Thread()] * 64

        # self.currentThread = 0
        # self.threads.append(Thread())

class Thread:
    def __init__(self):
        self.currentFrame = 0

        self.frames = [Frame()] * 64
        self.constPool = list()
        self.exception = 0
        # self.frames.append(Frame())

class Frame:
    def __init__(self):
        self.registers = dict()
        self.registers['acc'] = 0 #Register()
        self.registers['pc'] = 0 #Register()
        for i in range(32):
            self.registers['v' + str(i)] = 0 #Register()

# class Register:
#         def __init__(self):
#             self.value = 0
#             self._type = 0