from curses.ascii import isdigit
from enum import unique
from pyparsing import empty
import yaml
import copy
import re
import os
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

def topObj():
    global s
    f = open("cacheObj", "r")
    f.readline()
    getline(f)
    # print(s)
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
    # print(val)
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
    #print("act enter: ", s)
    if s != [''] and s[0] != "fgraph":
        arr = list()
        arr.append(s[0].strip(" "))
        arr.append(s[1].strip("=").strip(" "))
        tmp.actions.append(arr)
        getline(file)
        actionParse(file, tmp)

def nodeParse(file):
    #print("node enter", s)
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

def parse():
    with open("kettle.txt", "r") as file:
        getline(file)
        typeParse(file)
        objParse(file)
        nodeParse(file)

# def fillEvents(doc):
#     for dict in doc:
#         frame_id = dict["unique_frame"]
#         cpu = dict["cpu"]
#         local_frame = dict["local_frame"]
#         event = dict["event"]
#         obj = dict["object"]
#         tmp = Object(event)
#         for attr in objects[event + "_Frame"].objattr.items():
#             tmp.objattr[attr[0].replace("frame.", "")] = dict["frame." + attr[0]]

#         ev = Event(frame_id, cpu, local_frame, event, obj, tmp)
#         if not(cpu in events):
#             events[cpu] = list()    
#         events[cpu].append(ev)


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
    print("CHECKING GDS")
    res = 1
    for gd in fgraphs[event.event].guards:
        for gdn in gd:
            #print(gdn)
            if gdn[1] == "=":
                #print("guard=")
                if gdn[0].startswith("frame."):
                    s = gdn[0].replace("frame.", "")
                    if not(event.frame.objattr[s] == convertStrToValue(gdn[2])):
                        res = 0
                else:
                    if not(objects[event.obj].objattr[gdn[0]] == convertStrToValue(gdn[2])):
                        res = 0
            elif gdn[1] == "<=":
                #print("guard<=")
                if gdn[0].startswith("frame."):
                    s = gdn[0].replace("frame.", "")
                    if not(event.frame.objattr[s] <= convertStrToValue(gdn[2])):
                        res = 0
                else:
                    if not(objects[event.obj].objattr[gdn[0]] <= convertStrToValue(gdn[2])):
                        res = 0
            elif gdn[1] == ">=":
                #print("guard>=")
                if gdn[0].startswith("frame."):
                    s = gdn[0].replace("frame.", "")
                    if not(event.frame.objattr[s] >= convertStrToValue(gdn[2])):
                        res = 0
                else:
                    if not(objects[event.obj].objattr[gdn[0]] >= convertStrToValue(gdn[2])):
                        res = 0
            elif gdn[1] == ">":
                #print("guard>")
                if gdn[0].startswith("frame."):
                    s = gdn[0].replace("frame.", "")
                    if not(event.frame.objattr[s] > convertStrToValue(gdn[2])):
                        res = 0
                else:
                    if not(objects[event.obj].objattr[gdn[0]] > convertStrToValue(gdn[2])):
                        res = 0
            elif gdn[1] == "<":
                #print("guard<")
                if gdn[0].startswith("frame."):
                    s = gdn[0].replace("frame.", "")
                    if not(event.frame.objattr[s] < convertStrToValue(gdn[2])):
                        res = 0
                else:
                    if not(objects[event.obj].objattr[gdn[0]] < convertStrToValue(gdn[2])):
                        res = 0
            else:
                print("wrong")
    print("      passgd = ", res)
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
            #print(frame_id, cpu, local_frame, event, obj, tmp, "SDFSIFFF")
            if checkGuards(ev, objects):
                res.append(ev)


    return res

def isValue(s):
    return s.isdigit() or s in ["True", "False"]

def doActions(event, objs):
    print("DOACTIONS")
    for act in fgraphs[event.event].actions:
        if act[0].startswith("frame."):
            t = act[0].replace("frame.", "")
            tt = act[1].replace("frame.", "")
            #print("    ", act[0], event.frame.objattr[t])
            event.frame.objattr[t] = eval(tt, {}, {**event.frame.objattr, **objs[event.obj].objattr})
            #print("    ", act[0], event.frame.objattr[t])
            # if isValue(act[1].replace("-", "")):
            #     #print(event.frame[t], int(act[1]))
            #     event.frame.objattr[t] = convertStrToValue(act[1])
            # else:
            #     event.frame.objattr[t] = event.frame.objattr[act[1].replace("frame.", "")]
        else:
            
            # if isValue(act[1].replace("-", "")):
            #     objs[event.obj].objattr[act[0]] = convertStrToValue(act[1])
            # else:
            #     objs[event.obj].objattr[act[0]] = event.frame.objattr[act[1].replace("frame.", "")]
            print("    ", act[0], objs[event.obj].objattr[act[0]])
            tt = act[1].replace("frame.", "")
            objs[event.obj].objattr[act[0]] = eval(tt, {}, {**event.frame.objattr, **objs[event.obj].objattr})
            print("    ", act[0], objs[event.obj].objattr[act[0]])


def lenEvents(evs):
    res = 0
    for it in evs.items():
        res += len(it[1])
    return res

def setNextEvent(cpu, local, stepEvs):
    print("MARK", stepEvs)

    for d in doc:
        if d["cpu"] == cpu and local + 1 == d["local_frame"]:
            stepEvs[cpu]["cur"] = d["unique_frame"]

correct = 0

@log_call
def checkSeq(evs):
    global correct
    #print events
    global objects
    print("##############################CHECKING SEQ#######################")
    for cpu in evs.items():
        print(cpu, "CPUUUU")
        print(cpu[0], "----------------------------------------------")
        print("     ", end = "")
        #for q in cpu[1].items():
         #   print() #print(str(q[1]), "EWREER", end = " ")
    print("-----------------------------------------------")
    pushObj(objects)
    step = findSuitEvents(evs)
    
    print("!!!!!!!!!!STEP : ")
    for i in step:
        print("id=", i.unique_frame, "cpu=", i.cpu, i.event)
    print("!!!!!!!!!!")

    if len(step) == 0:
        if lenEvents(evs) == 0:
            correct += 1
    for ev in step:
        if correct > 0:
            break
        stepEvents = copy.deepcopy(evs)
        # print(ev.event)
        topObj()
        doActions(ev, objects)
        if stepEvents[ev.cpu]["cur"] == stepEvents[ev.cpu]["max"]:
            del stepEvents[ev.cpu]
        #delete event
        for it in stepEvents.items():
            # print(it[1]["cur"], "ITITITITIT", ev.unique_frame)
            if ev.unique_frame == it[1]["cur"]:
                setNextEvent(ev.cpu, ev.local_frame, stepEvents)

        
        checkSeq(stepEvents)
    popObj()

def checkTrace():
    global doc
    with open('example.yaml', 'r') as file:
        doc = yaml.safe_load(file)
    
    fillEvents(doc)
    #print(events)
    checkSeq(events)


if __name__ == "__main__":
    parse()

    # for i in types:
    #     print(i)
    
    # for i in objects.items():
    #     print(i[0])
    #     for j in i[1].objattr.items():
    #         print("  attr:", j[0], "=", j[1])

    # for i in fgraphs.items():
    #     print(i[0])
    #     for j in i[1].guards:
    #         print("  guard: ", j)
    #     for j in i[1].wds:
    #         print("  wds: ", j)
    #     for j in i[1].actions:
    #         print("  action: ", j)

    checkTrace()
    print("Is correct trace :", correct > 0)
    # for cpu in events.items():
    #     for ev in cpu[1]:
    #         print(ev.unique_frame, ev.cpu, ev.local_frame, ev.event, ev.obj)
    #         for attr in ev.frame.objattr.items():
    #             print(attr)