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
from functions import *


class EventForTrace:
    def __init__(self, u_frame, cpu, l_frame, event, obj, frame):
        self.unique_frame = u_frame
        self.cpu = cpu
        self.local_frame = l_frame
        self.event = event
        self.obj = obj
        self.frame = frame


    def print(self):
        print(f"Uframe: {self.unique_frame} cpu: {self.cpu} name: {self.event} obj: {self.obj} frame: {self.frame.print()}")

# 
class EventMap:
    def __init__(self, file, objects:dict, evs:dict, vm):
        self.vm = vm

        self.file = file
        # хранит текущие глобальные индексы событий на каждом cpu
        self.events = dict()
        # хранит список всех событий 
        self.yamldict = ""
        # прототипы объектов
        self.objects = objects
        # прототипы событий
        self.eventsProt = evs
        # print(evs)
        self.isCorrectTrace = False
    
    # def setObjects(self, objs):
    #     self.objs = objs
    def printEventCpuMap(self):
        print("EVENT MAP")
        for x in self.events.keys():
            print(x, self.events[x])
    
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
        # print("in cGuard")
        # print(self.eventsProt)
        for guardCond in self.eventsProt[ev.event].guards:
            print(guardCond)
            # CHECK GUARD
            pass
        return res

    def findSuitableEvent(self, evs):
        res = list() # список подходящих событий с параметрами
        # print("res = ", res)
        for ev in evs.items():
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
        # print(res)
        return res
    

    def setNextEvent(self, cpu, local, stepEvents):
        for x in self.yamldict:
            if x["cpu"] == cpu and local + 1 == x["local_frame"]:
                stepEvents[cpu]["cur"] = x["unique_frame"]


    def lengthEvents(self, evs):
        res = 0
        for it in evs.items():
            res += len(it[1])
        return res

    
    def checkSequence(self, evs):

        # print("check seq: ", evs)
        step = self.findSuitableEvent(evs)
        if len(step) == 0:
            if self.lengthEvents(evs) == 0:
                self.isCorrectTrace = True
                print("CORRECT2")
        
        for ev in step:
            print("acc = ", self.vm.threads[0].frames[self.vm.threads[0].currentFrame].registers['acc'])
            print("v0 = ", self.vm.threads[0].frames[self.vm.threads[0].currentFrame].registers['v0'])
            print("v1 = ", self.vm.threads[0].frames[self.vm.threads[0].currentFrame].registers['v1'])
            if self.isCorrectTrace:
                print("CORRECT")
                break
            stepEvents = copy.deepcopy(evs)
            # ev.print()
            self.doActions(ev)
            if stepEvents[ev.cpu]["cur"] == stepEvents[ev.cpu]["max"]:
                del stepEvents[ev.cpu]
            
            # print("^^^", stepEvents)
            for item in stepEvents.items():
                # print(":", item[1]["cur"], ": u_frame:", ev.unique_frame)
                if ev.unique_frame == item[1]["cur"]:
                    # print("set next")
                    self.setNextEvent(ev.cpu, ev.local_frame, stepEvents)

            
            
            self.checkSequence(stepEvents)

    
    def doActions(self, ev):
        # self.printEventCpuMap()
        # print(self.eventsProt)
        for action in self.eventsProt[ev.event].actions:
            print("##################################")
            print("ACTION: ", action)
            # print(ev.frame.objAttr)
            # 
            # print(self.vm.threads[0].frames[self.vm.threads[0].currentFrame].registers)
            
            act = action[1].replace("frame.", "").replace(".value", "")
            print("ACTION2: ", act)
            
            # print("to act: ", action)
            # print(self.vm.threads[0].frames[self.vm.threads[0].currentFrame].registers['acc'], self.vm.threads[0].frames[self.vm.threads[0].currentFrame].registers['r1'])
            # print("res = ", eval(act, {**self.vm.threads[0].frames[self.vm.threads[0].currentFrame].registers, **getDictForFuncs()}))

            # print(action[0], " to write")
            if action[0] == 'acc.value' or action[0] == 'frame.acc.value':
                # print(getDictForFuncs(), getDictForFuncs()['xor'](1, 2))
                print("EVAL: acc = ", act)
                # делаем подстановку на значения регистров
                for arg in ev.frame.objAttr.keys():
                    if arg == '$location' or arg == '$subframe':
                        continue
                    print(arg)
                    print("EVAL EER", ev.frame.objAttr[arg])
                    # print(len(ev.frame.objAttr[arg]))
                    ev.frame.objAttr[arg] = eval(str(ev.frame.objAttr[arg]), self.vm.threads[0].frames[self.vm.threads[0].currentFrame].registers)

                print("------------------")
                # print({**ev.frame.objAttr, **self.vm.threads[0].frames[self.vm.threads[0].currentFrame].registers, **getDictForFuncs()})

                self.vm.threads[0].frames[self.vm.threads[0].currentFrame].registers['acc'] = eval(act, {**ev.frame.objAttr, **self.vm.threads[0].frames[self.vm.threads[0].currentFrame].registers, **getDictForFuncs()})
                print("RES: ", self.vm.threads[0].frames[self.vm.threads[0].currentFrame].registers['acc'])
            else:
                reg = ev.frame.objAttr[action[0].replace("frame.", "").replace(".value", "")]
                
                print("EVAL: ", reg, " = ",  act)
                self.vm.threads[0].frames[self.vm.threads[0].currentFrame].registers[reg] = eval(act, {**ev.frame.objAttr, **self.vm.threads[0].frames[self.vm.threads[0].currentFrame].registers, **getDictForFuncs()})
                # print(self.vm.threads[0].frames[self.vm.threads[0].currentFrame].registers[reg])
                print("RES: ", self.vm.threads[0].frames[self.vm.threads[0].currentFrame].registers[reg])
                
                print("------------------")
                # print({**ev.frame.objAttr, **self.vm.threads[0].frames[self.vm.threads[0].currentFrame].registers, **getDictForFuncs()})


            #???!!!!!!!!!!!!!!!!


    def print(self):
        for x in self.events.keys():
            print(f'|cpu = {x}| {self.events[x]}')
            for q in self.yamldict:
                if q["cpu"] == x:
                    print(q)
        

