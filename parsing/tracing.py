# def checkTrace(traceFile):
#     global doc
#     with open(traceFile, 'r') as file:
#         doc = yaml.safe_load(file)
#     f = open("cacheObj", "w")
#     f.write("-\n")
#     f.close()
#     fillEvents(doc)
#     checkSeq(events)
#     os.remove("cacheObj")
    
    
import yaml


class EventMap:
    def __init__(self, file):
        self.file = file
        self.events = dict()
    
    def setObjects(self, objs):
        self.objs = objs
    
    def fillEvents(self):
        
        with open(self.file, 'r') as file:
            q = yaml.safe_load(file)
            for elem in q:
                print(elem)
                

                frame_id = elem["unique_frame"]
                cpu = elem["cpu"]
                # print(cpu, frame_id)
                if not(cpu in self.events):
                    self.events[cpu] = dict()
                    self.events[cpu]["cur"] = int(frame_id)
                    self.events[cpu]["max"] = int(frame_id)
                if self.events[cpu]["max"] < int(frame_id):
                    self.events[cpu]["max"] = int(frame_id)
    
    def getEventSequence(self):
        return self.events

    def print(self):
        for x in self.events.keys():
            print(f'||{x}| {self.events[x]}')