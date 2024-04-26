

class VM:
    def __init__(self):
        self.classes = list()
        self.methods = list()
        self.fields = list()
        self.threads = [Thread() for _ in range(64)]

    def print(self):
        # for th in self.threads:
        #     th.print()
        self.threads[0].print()

class Thread:
    def __init__(self):
        self.currentFrame = 0

        self.frames = [Frame() for _ in range(64)]
        self.constPool = list()
        self.exception = 0
        # self.frames.append(Frame())
    
    def print(self):
        # for fr in self.frames:
            # fr.print()
        self.frames[0].print()

class Frame:
    def __init__(self):
        self.registers = dict()
        self.registers['acc'] = 0 #Register()
        self.registers['pc'] = 0 #Register()
        for i in range(32):
            self.registers['v' + str(i)] = 0 #Register()

    def print(self):
        # print("Amount of regs = ", len(self.registers))
        for x in self.registers.keys():
            if x != "__builtins__":
                print(x, "=", self.registers[x], end = "|")
        print("")

# class Register:
#         def __init__(self):
#             self.value = 0
#             self._type = 0