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
from parse import *


class EventForTrace:
    def __init__(self, u_frame, cpu, l_frame, event, obj, frame):
        self.unique_frame = u_frame
        self.cpu = cpu
        self.local_frame = l_frame
        self.event = event
        self.obj = obj
        self.frame = frame

# 
class EventMap:
    def __init__(self, file, objects:dict, evs:dict):
        self.file = file
        # хранит текущие глобальные индексы событий на каждом cpu
        self.events = dict()
        # хранит список всех событий 
        self.yamldict = ""
        # прототипы объектов
        self.objects = objects
        # прототипы событий
        self.eventsProt = evs
    
    # def setObjects(self, objs):
    #     self.objs = objs
    
    def fillEvents(self):
        
        with open(self.file, 'r') as file:
            self.yamldict = yaml.safe_load(file)
            for elem in self.yamldict:
                # print(elem)
                

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
    
    def checkGuard(self, ev: EventForTrace):
        res = True
        print("in cGuard")
        for guardCond in self.eventsProt[ev.event].guards:
            print(guardCond)

    def findSuitableEvent(self):
        res = list() # список подходящих событий с параметрами
        # print("in fSuitEv")
        for ev in self.events.items():
            # print("in fSuitEv")
            if ev[1]["cur"] <= ev[1]["max"]:
                # print("in fSuitEv")
                frame_id = self.yamldict[ev[1]["cur"]]["unique_frame"]
                cpu = ev[0]
                local_frame = self.yamldict[ev[1]["cur"]]["local_frame"]
                event_name = self.yamldict[ev[1]["cur"]]["event"]
                object_name = self.yamldict[ev[1]["cur"]]["event"]
                tmp = Object(event_name)
                for attr in self.objects[event_name + "_Frame"].objAttr.items():
                    tmp.objAttr[attr[0].replace(".frame", "")] = self.yamldict[ev[1]["cur"]]["frame." + attr[0]]
                correct_event = EventForTrace(frame_id, cpu, local_frame, event_name, object_name, tmp)
                if self.checkGuard(correct_event):
                    res.append(correct_event)
        return res

    def print(self):
        for x in self.events.keys():
            print(f'|cpu = {x}| {self.events[x]}')
            for q in self.yamldict:
                if q["cpu"] == x:
                    print(q)
        

