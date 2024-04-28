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
    
    def convertStrToValue(self, s, vm, ev):
        if s == "True":
            return True
        if s == "False":
            return False
        # print(s)
        if s.isdigit():
            return int(s)
        
        s = s.replace("frame.", "").replace(".value", "")
        s = ev.frame.objAttr[s]
        return eval(s, vm.threads[ev.cpu].frames[vm.threads[ev.cpu].currentFrame].registers)
    
    
    def checkGuard(self, ev: EventForTrace, vm):
        res = True
        # print("in cGuard")
        # print(ev.event)
        for guardCond in self.eventsProt[ev.event].guards:
            # print(guardCond, len(guardCond[0]))
            if len(guardCond[0]) == 1:
                continue
            # print(guardCond)
            guardCond = guardCond[0]
            if guardCond[1] == "=":
                if guardCond[0].startswith("frame."):
                    s = guardCond[0].replace("frame.", "")
                    if not(ev.frame.objAttr[s] == self.convertStrToValue(guardCond[2], vm, ev)):
                        res = 0
                else:
                    if not(vm.threads[ev.cpu].frames[vm.threads[ev.cpu].currentFrame].registers[guardCond[0].replace(".value", "")] == self.convertStrToValue(guardCond[2], vm, ev)):
                        res = 0
            elif guardCond[1] == "<=":
                if guardCond[0].startswith("frame."):
                    s = guardCond[0].replace("frame.", "")
                    if not(ev.frame.objAttr[s] <= self.convertStrToValue(guardCond[2], vm, ev)):
                        res = 0
                else:
                    if not(vm.threads[ev.cpu].frames[vm.threads[ev.cpu].currentFrame].registers[guardCond[0].replace(".value", "")] <= self.convertStrToValue(guardCond[2], vm, ev)):
                        res = 0
            elif guardCond[1] == ">=":
                if guardCond[0].startswith("frame."):
                    s = guardCond[0].replace("frame.", "")
                    if not(ev.frame.objAttr[s] >= self.convertStrToValue(guardCond[2], vm, ev)):
                        res = 0
                else:
                    if not(vm.threads[ev.cpu].frames[vm.threads[ev.cpu].currentFrame].registers[guardCond[0].replace(".value", "")] >= self.convertStrToValue(guardCond[2], vm, ev)):
                        res = 0
            elif guardCond[1] == ">":
                if guardCond[0].startswith("frame."):
                    s = guardCond[0].replace("frame.", "")
                    if not(ev.frame.objAttr[s] > self.convertStrToValue(guardCond[2], vm, ev)):
                        res = 0
                else:
                    if not(vm.threads[ev.cpu].frames[vm.threads[ev.cpu].currentFrame].registers[guardCond[0].replace(".value", "")] > self.convertStrToValue(guardCond[2], vm, ev)):
                        res = 0
            elif guardCond[1] == "<":
                if guardCond[0].startswith("frame."):
                    s = guardCond[0].replace("frame.", "")
                    if not(ev.frame.objAttr[s] < self.convertStrToValue(guardCond[2], vm, ev)):
                        res = 0
                else:
                    if not(vm.threads[ev.cpu].frames[vm.threads[ev.cpu].currentFrame].registers[guardCond[0].replace(".value", "")] < self.convertStrToValue(guardCond[2], vm, ev)):
                        res = 0
            else:
                print("smth went wrong...")
            
        return res

    def findSuitableEvent(self, evs, vm):
        res = list() # список подходящих событий с параметрами
        # print("res = ", res)
        for ev in evs.items():
            if ev[1]["cur"] <= ev[1]["max"]:
                frame_id = self.yamldict[ev[1]["cur"]]["unique_frame"]
                cpu = ev[0]
                local_frame = self.yamldict[ev[1]["cur"]]["local_frame"]
                event_name = self.yamldict[ev[1]["cur"]]["event"]
                object_name = self.yamldict[ev[1]["cur"]]["event"]
                tmp = Object(event_name)
                for attr in self.objects[event_name + "_Frame"].objAttr.items():
                    tmp.objAttr[attr[0].replace(".frame", "")] = self.yamldict[ev[1]["cur"]]["frame." + attr[0]]

                # print(self.yamldict[ev[1]["cur"]])
                for attr in self.yamldict[ev[1]["cur"]].keys():
                    if attr.endswith(".pri"):
                        attrName = attr.replace(".pri", "")
                        tmp.objAttr[attrName] = self.yamldict[ev[1]["cur"]][attr]
                correct_event = EventForTrace(frame_id, cpu, local_frame, event_name, object_name, tmp)
                if self.checkGuard(correct_event, vm):
                    res.append(correct_event)
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

    
    def isCorrectArith(self, ev, stepVM):
        # print(ev.frame.objAttr)
        res = True
        print("check sim for cpu", ev.cpu, " id =", ev.local_frame)
        intersect = {key: value for key, value in ev.frame.objAttr.items() if key in stepVM.threads[ev.cpu].frames[stepVM.threads[ev.cpu].currentFrame].registers}
        for x in intersect:
            print(f"VM: {x} =", ev.frame.objAttr[x], f"| Sim: {x} =", stepVM.threads[ev.cpu].frames[stepVM.threads[ev.cpu].currentFrame].registers[x])
            if ev.frame.objAttr[x] != stepVM.threads[ev.cpu].frames[stepVM.threads[ev.cpu].currentFrame].registers[x]:
                if not(x == 'pc' and stepVM.threads[ev.cpu].frames[stepVM.threads[ev.cpu].currentFrame].registers[x] == 0):
                    res = False
        return res


    def checkSequence(self, evs, vm):
        # print("check seq: ", evs)
        print("^^^^^^^^^^^^^^^^^^^^^^^^^^")
        step = self.findSuitableEvent(evs, vm)
        if len(step) == 0:
            if self.lengthEvents(evs) == 0:
                self.isCorrectTrace = True
        
        # print(step)
        for ev in step:
            
            # print(ev.unique_frame)
            if self.isCorrectTrace:
                break
                
            stepEvents = copy.deepcopy(evs)
            # ev.print()
            # added copy vm
            stepVM = copy.deepcopy(vm)
            stepVM.print()
            self.doActions(ev, stepVM)
            
            if not self.isCorrectArith(ev, stepVM):
                # print(step)
                # continue
                if len(step) == 1 and self.lengthEvents(evs) == 0:
                    break
                else:
                    continue

            if stepEvents[ev.cpu]["cur"] == stepEvents[ev.cpu]["max"]:
                del stepEvents[ev.cpu]
            
            # print("^^^", stepEvents)
            for item in stepEvents.items():
                # print(":", item[1]["cur"], ": u_frame:", ev.unique_frame)
                if ev.unique_frame == item[1]["cur"]:
                    self.setNextEvent(ev.cpu, ev.local_frame, stepEvents)

            self.checkSequence(stepEvents, stepVM)

    
    def doActions(self, ev, vm):
        for action in self.eventsProt[ev.event].actions:
            # print("----------------------------------------")
            # print(f"INS: {ev.event}", "| action =", action)
            # print(f"ARGS: {ev.frame.objAttr}")
            act = action[1].replace("frame.", "").replace(".value", "")
            vm.threads[ev.cpu].frames[vm.threads[ev.cpu].currentFrame].registers['pc'] = ev.frame.objAttr['pc'] 
            if action[0] == 'acc.value' or action[0] == 'frame.acc.value':
                # print(f"THREAD #{ev.cpu}: acc =", act)
                # делаем подстановку на значения регистров
                for arg in ev.frame.objAttr.keys():
                    if arg == '$location' or arg == '$subframe':
                        continue
                    ev.frame.objAttr[arg] = eval(str(ev.frame.objAttr[arg]), vm.threads[ev.cpu].frames[vm.threads[ev.cpu].currentFrame].registers)
                
        
                # vm.threads[ev.cpu].frames[vm.threads[ev.cpu].currentFrame].registers['pc'] = ev.frame.objAttr['pc']        
                # dictForEval = {**ev.frame.objAttr, **vm.threads[0].frames[vm.threads[0].currentFrame].registers}
                
                vm.threads[ev.cpu].frames[vm.threads[ev.cpu].currentFrame].registers['acc'] = eval(act, {**ev.frame.objAttr, **vm.threads[ev.cpu].frames[vm.threads[ev.cpu].currentFrame].registers, **getDictForFuncs()})
                # print("RES: ", vm.threads[0].frames[self.vm.threads[0].currentFrame].registers['acc'])
                # vm.print()
                # print("----------------------------------------")
            else:
                reg = ev.frame.objAttr[action[0].replace("frame.", "").replace(".value", "")]
                if not reg:
                    continue

                # print(f"THREAD #{ev.cpu}:", reg, "=", act)
                # dictForEval = {**ev.frame.objAttr, **vm.threads[0].frames[vm.threads[0].currentFrame].registers}
                vm.threads[ev.cpu].frames[vm.threads[ev.cpu].currentFrame].registers[reg] = eval(act, {**ev.frame.objAttr, **vm.threads[ev.cpu].frames[vm.threads[ev.cpu].currentFrame].registers, **getDictForFuncs()})
                # vm.print()
                # print("----------------------------------------")


            #???!!!!!!!!!!!!!!!!


    def print(self):
        for x in self.events.keys():
            print(f'|cpu = {x}| {self.events[x]}')
            for q in self.yamldict:
                if q["cpu"] == x:
                    print(q)
        

