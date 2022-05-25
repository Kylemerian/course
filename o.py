from curses.ascii import isdigit
from enum import unique
from pyparsing import empty
import yaml
import copy
import re
import os
import sys
from eliot import log_call, to_file
to_file(open("out.log", "w"))


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


objects = dict()
fgraphs = dict()
types = list()
events = dict()

s = ""
doc = ""
correct = False

def topObj():
    global s
    f = open("cacheObj", "r")
    f.readline()
    getline(f)
    while s != [''] and s[0] != "-":
        name = s[1]
        getline(f)
        while s != [''] and s[0] != "Object":
            if s!= ['']:
                objects[name].objattr[s[0]] = convertStrToValue(s[1])
            getline(f)

        
def popObj():
    tmp = open("tmp", "w")
    f = open("cacheObj", "r")
    f.readline()
    line = f.readline()
    while line != "-\n":
        line = f.readline()
    while line:
        tmp.write(line)
        line = f.readline()
    f.close()
    os.remove("cacheObj")
    os.rename("tmp", "cacheObj")


def pushObj(val):
    f = open("cacheObj", "r")
    outfile = open("newObj", "a+")
    outfile.write("-\n")
    for obj in val.items():
        if (obj[0].endswith("_Frame")):
           continue
        outfile.write("Object:" + obj[0] + "\n")
        for attr in obj[1].objattr.items():
            outfile.write(attr[0] + ":" + str(attr[1]) + "\n")
    outfile.write("\n")
    for line in f:
        outfile.write(line)
    f.close()
    os.remove("cacheObj")
    os.rename("newObj", "cacheObj")

def typeParse(file):
    if s != [''] and s[0] == "type":
        types.append(s[1])
        getline(file)
        typeParse(file)

def objattrParse(file, obj):
    if s != [''] and s[0] == "  objattr":
        obj.objattr[(s[1])] = 0
        getline(file)
        objattrParse(file, obj)

def objParse(file):
    if s != [''] and s[0] == "object":
        tmp = Object(s[1])
        name = s[1]
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
        tmp.guards.append(s)
        getline(file)
        guardParse(file, tmp)


def wdsParse(file, tmp):
    if s != [''] and s[0] != "actions":
        getline(file)
        wdsParse(file, tmp)

def actionParse(file, tmp):
    if s != [''] and s[0] != "fgraph":
        arr = list()
        arr.append(s[0].strip(" "))
        arr.append(s[1].strip("=").strip(" "))
        tmp.actions.append(arr)
        getline(file)
        actionParse(file, tmp)

def nodeParse(file):
    if s != [''] and s[0] == "fgraph":
        tmp = Fgraph(s[1])
        name = s[1]
        getline(file)
        getline(file)
        getline(file)
        guardParse(file, tmp)
        getline(file)
        wdsParse(file, tmp)
        getline(file)
        actionParse(file, tmp)
        fgraphs[name] = tmp
        nodeParse(file)


def getline(file):
    global s
    s = file.readline().strip("\n").split(":")


def parse(rekaFile):
    with open(rekaFile, "r") as file:
        getline(file)
        typeParse(file)
        objParse(file)
        nodeParse(file)


def fillEvents(doc):
    for elem in doc:
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
            if gdn[1] == "=":
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
                tmp.objattr[attr[0].replace("frame.", "")] = doc[item[1]["cur"]]["frame." + attr[0]]
            ev = Event(frame_id, cpu, local_frame, event, obj, tmp)
            if checkGuards(ev, objects):
                res.append(ev)


    return res


def isValue(s):
    return s.isdigit() or s in ["True", "False"]


def doActions(event, objs):
    for act in fgraphs[event.event].actions:
        if act[0].startswith("frame."):
            t = act[0].replace("frame.", "")
            tt = act[1].replace("frame.", "")
            event.frame.objattr[t] = eval(tt, {}, {**event.frame.objattr, **objs[event.obj].objattr})
        else:
            tt = act[1].replace("frame.", "")
            objs[event.obj].objattr[act[0]] = eval(tt, {}, {**event.frame.objattr, **objs[event.obj].objattr})


def lenEvents(evs):
    res = 0
    for it in evs.items():
        res += len(it[1])
    return res


def setNextEvent(cpu, local, stepEvs):
    for d in doc:
        if d["cpu"] == cpu and local + 1 == d["local_frame"]:
            stepEvs[cpu]["cur"] = d["unique_frame"]


def checkSeq(evs):
    global correct
    global objects
    
    step = findSuitEvents(evs)
    pushObj(objects)

    if len(step) == 0:
        if lenEvents(evs) == 0:
            correct = True
    for ev in step:
        if correct:
            break
        stepEvents = copy.deepcopy(evs)
        topObj()
        doActions(ev, objects)
        if stepEvents[ev.cpu]["cur"] == stepEvents[ev.cpu]["max"]:
            del stepEvents[ev.cpu]
        for it in stepEvents.items():
            if ev.unique_frame == it[1]["cur"]:
                setNextEvent(ev.cpu, ev.local_frame, stepEvents)
        checkSeq(stepEvents)
    popObj()


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
        print("USAGE: python3 o.py REKAFILE TRACEFILE")
    else:
        parse(sys.argv[1])
        checkTrace(sys.argv[2])
        print("Is correct trace :", correct > 0)