from curses.ascii import isdigit
from enum import unique
from pyparsing import empty
import yaml
import copy
import re
import os
import sys
from eliot import log_call, to_file

BIT8_DIV = 128
MAX_INT8 = 127
MIN_INT8 = -128

BIT16_DIV = 32768
MAX_INT16 = 32767
MIN_INT16 = -32768

BIT32_DIV = 2147483648
MAX_INT32 = 2147483647
MIN_INT32 = -2147483648

BIT64_DIV = 9223372036854775808
MAX_INT64 = 9223372036854775807
MIN_INT64 = -9223372036854775808



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
        self.constpool = list()
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

class Object:
    def __init__(self, name):
        self.objattr = dict()
        self.name = name

class Fgraph:
    def __init__(self, name):
        self.actions = list()
        self.guards = list()
        self.wds = list()
        self.name = name

class Event:
    def __init__(self, u_frame, cpu, l_frame, event, obj, frame):
        self.unique_frame = u_frame
        self.cpu = cpu
        self.local_frame = l_frame
        self.event = event
        self.obj = obj
        self.frame = frame

vm = VM()
fgraphs = dict()
events = dict()
objects = dict()
types = list()

s = ""
doc = ""
correct = False

def getline(file):
    global s
    s = file.readline().strip("\n").split(":")

def typeParse(file):
    if s != [''] and s[0] == "type":
        types.append(s[1])
        getline(file)
        print("#type :", s[1])
        typeParse(file)

def objattrParse(file, obj):
    if s != [''] and s[0] == "  objattr":
        obj.objattr[(s[1])] = 0
        print("objattr = ", s[1])
        getline(file)
        objattrParse(file, obj)

def objParse(file):
    if s != [''] and s[0] == "object":
        tmp = Object(s[1])
        name = s[1]
        print("name =", s[1])
        getline(file)
        objattrParse(file, tmp)
        objects[name] = tmp
        objParse(file)

def guardParse(file, tmp):
    global s
    if s != [''] and s[0] != "wds":
        s = s[0]
        s = s.replace("≥", ">=")
        s = s.replace("≤", "<=")
        s = s.split("и")
        for i in range(len(s)):
            s[i] = s[i].split(" ")
            s[i] = list(filter(lambda x : x, s[i]))
        
        # print("s = ", s, " len = ", len(s[0]))
        if len(s[0]) == 3:
            print("#guard = ", s)
            tmp.guards.append(s)

        getline(file)
        guardParse(file, tmp)


def wdsParse(file, tmp):
    if s != [''] and s[0] != "actions":
        getline(file)
        print("#wds = ", s)
        wdsParse(file, tmp)


def actionParse(file, tmp):
    if s != [''] and s[0] != "fgraph":
        arr = list()
        arr.append(s[0].strip(" "))
        #print("action before parsed=", arr)
        #print("s = ", s)
        if len(s) > 1:
            arr.append(s[1].strip("=").strip(" "))
        else:
            0 # print("action with simple text not added")
        tmp.actions.append(arr)
        print("#action = ", arr)
        getline(file)
        actionParse(file, tmp)


def nodeParse(file):
    if s != [''] and s[0] == "fgraph":
        tmp = Fgraph(s[1])
        name = s[1]
        print("TO PARSE EVENT = ", name)
        getline(file)
        getline(file)
        getline(file)
        guardParse(file, tmp)
        # print("guardParse OK")
        getline(file)
        wdsParse(file, tmp)
        # print("wdsParse OK")
        getline(file)
        actionParse(file, tmp)
        # print("actionParse OK")
        fgraphs[name] = tmp
        # print("event = ", name)
        nodeParse(file)


def parse(rekaFile):
    with open(rekaFile, "r") as file:
        getline(file)
        typeParse(file)
        print("#########")
        objParse(file)
        print("#########")
        nodeParse(file)


def fillEvents(doc):
    for elem in doc:
        #print("elem = ", elem)
        frame_id = elem["unique_frame"]
        cpu = elem["cpu"]
        if not(cpu in events):
            events[cpu] = dict()
            events[cpu]["cur"] = int(frame_id)
            events[cpu]["max"] = int(frame_id)
        if(events[cpu]["max"] < int(frame_id)):
            events[cpu]["max"] = int(frame_id)
        

def convertStrToValue(s):
    if s == "True":
        return True
    if s == "False":
        return False
    return int(s)


def checkGuards(event, objects):
    res = 1
    for gd in fgraphs[event.event].guards:
        for gdn in gd:
            if len(gdn) < 2:
                print("TODO guard = ", gdn)
            elif gdn[1] == "=":
                if gdn[0].startswith("frame."):
                    s = gdn[0].replace("frame.", "")
                    if not(event.frame.objattr[s] == convertStrToValue(gdn[2])):
                        res = 0
                else:
                    if not(objects[event.obj].objattr[gdn[0]] == convertStrToValue(gdn[2])):
                        res = 0
            elif gdn[1] == "<=":
                if gdn[0].startswith("frame."):
                    s = gdn[0].replace("frame.", "")
                    if not(event.frame.objattr[s] <= convertStrToValue(gdn[2])):
                        res = 0
                else:
                    if not(objects[event.obj].objattr[gdn[0]] <= convertStrToValue(gdn[2])):
                        res = 0
            elif gdn[1] == ">=":
                if gdn[0].startswith("frame."):
                    s = gdn[0].replace("frame.", "")
                    if not(event.frame.objattr[s] >= convertStrToValue(gdn[2])):
                        res = 0
                else:
                    if not(objects[event.obj].objattr[gdn[0]] >= convertStrToValue(gdn[2])):
                        res = 0
            elif gdn[1] == ">":
                if gdn[0].startswith("frame."):
                    s = gdn[0].replace("frame.", "")
                    if not(event.frame.objattr[s] > convertStrToValue(gdn[2])):
                        res = 0
                else:
                    if not(objects[event.obj].objattr[gdn[0]] > convertStrToValue(gdn[2])):
                        res = 0
            elif gdn[1] == "<":
                if gdn[0].startswith("frame."):
                    s = gdn[0].replace("frame.", "")
                    if not(event.frame.objattr[s] < convertStrToValue(gdn[2])):
                        res = 0
                else:
                    if not(objects[event.obj].objattr[gdn[0]] < convertStrToValue(gdn[2])):
                        res = 0
            else:
                print("smth went wrong...")
    return res


def findSuitEvents(tmpEvents):
    global objects
    global doc
    res = list()
    for item in tmpEvents.items():
        if item[1]["cur"] <= item[1]["max"]:
            frame_id = doc[item[1]["cur"]]["unique_frame"]
            cpu = item[0]
            local_frame = doc[item[1]["cur"]]["local_frame"]
            event = doc[item[1]["cur"]]["event"]
            obj = doc[item[1]["cur"]]["object"]
            tmp = Object(event)
            for attr in objects[event + "_Frame"].objattr.items():
                print("tmp = ", tmp.name)
                print("attr = ", tmp.objattr)

                tmp.objattr[attr[0].replace("frame.", "")] = doc[item[1]["cur"]]["frame." + attr[0]]
            ev = Event(frame_id, cpu, local_frame, event, obj, tmp)
            if checkGuards(ev, objects):
                res.append(ev)


    return res


def lenEvents(evs):
    res = 0
    for it in evs.items():
        res += len(it[1])
    return res


def isValue(s):
    return s.isdigit() or s in ["True", "False"]


def doActions(event, objs):
    for act in fgraphs[event.event].actions:
        # globaldict = dict()
        # acc = vm.threads[0].frames[0].acc
        # print(vm.threads[0].frames[0].acc.value, " =acc")
        # globaldict['acc'] = acc
        print("ACC = ", vm.threads[0].frames[0].registers['acc'].value)

        if act[0].startswith("frame."):
            t = act[0].replace("frame.", "")
            tt = act[1].replace("frame.", "")
            print("to ACT =", t, " ", tt)
            print("Attributes:", event.frame.objattr)
            print("All objs:", objs[event.obj].objattr)
            print("t = ", t)
            event.frame.objattr[t] = eval(tt, vm.threads[0].frames[0].registers, {**event.frame.objattr, **objs[event.obj].objattr})
        else:
            print(act[1])
            tt = act[1].replace("frame.", "")
            tt = tt.replace(".value", "")
            tt = tt.replace("acc", "acc.value")
            print("doACTION = ", tt)
            print("OBJS", {**event.frame.objattr, **objs[event.obj].objattr})
            # print("REWRITE", objs[event.obj].objattr[act[0]] )
            print("QQQ = ", vm.threads[0].frames[0].registers[act[0].replace(".value", "")])
            # objs[event.obj].objattr[act[0]] = eval(tt, vm.threads[0].frames[0].registers, {**event.frame.objattr, **objs[event.obj].objattr})
            vm.threads[0].frames[0].registers[act[0].replace(".value", "")].value = eval(tt, vm.threads[0].frames[0].registers, {**event.frame.objattr, **objs[event.obj].objattr})



def setNextEvent(cpu, local, stepEvs):
    for d in doc:
        if d["cpu"] == cpu and local + 1 == d["local_frame"]:
            stepEvs[cpu]["cur"] = d["unique_frame"]


def checkSeq(evs):
    global correct
    global objects
    
    step = findSuitEvents(evs)
    #pushObj(objects)

    if len(step) == 0:
        if lenEvents(evs) == 0:
            correct = True
    for ev in step:
        if correct:
            break
        stepEvents = copy.deepcopy(evs)
    #   topObj()
        doActions(ev, objects)
        if stepEvents[ev.cpu]["cur"] == stepEvents[ev.cpu]["max"]:
            del stepEvents[ev.cpu]
        for it in stepEvents.items():
            if ev.unique_frame == it[1]["cur"]:
                setNextEvent(ev.cpu, ev.local_frame, stepEvents)
        checkSeq(stepEvents)
    #popObj()

def checkTrace(traceFile):
    global doc
    with open(traceFile, 'r') as file:
        doc = yaml.safe_load(file)
    f = open("cacheObj", "w")
    f.write("-\n")
    f.close()
    fillEvents(doc)
    checkSeq(events)
    os.remove("cacheObj")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("python3 neworacle.py REKA TRACE")
    else:
        parse(sys.argv[1])
        checkTrace(sys.argv[2])
        print("Is correct trace :", correct > 0)