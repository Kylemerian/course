from pyparsing import empty
import yaml
import re


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

def fillEvents(doc):
    for dict in doc:
        frame_id = dict["unique_frame"]
        cpu = dict["cpu"]
        local_frame = dict["local_frame"]
        event = dict["event"]
        obj = dict["object"]
        tmp = Object(event)
        for attr in objects[event + "_Frame"].objattr.items():
            tmp.objattr[attr[0].replace("frame.", "")] = dict["frame." + attr[0]]

        ev = Event(frame_id, cpu, local_frame, event, obj, tmp)
        if not(cpu in events):
            events[cpu] = list()    
        events[cpu].append(ev)

def checkGuards(event, objects):
    res = 1
    for gd in fgraphs[event.event].guards:
        for gdn in gd:
            if gdn[1] == "=":
                if gdn[0].startswith("frame."):
                    s = gdn[0].replace("frame.", "")
                    if not(event.frame.objattr[s] == int(gdn[2])):
                        res = 0
                else:
                    if not(objects[event.obj].objattr[gdn[0]] == int(gdn[2])):
                        res = 0
            elif gdn[1] == "<=":
                if gdn[0].startswith("frame."):
                    s = gdn[0].replace("frame.", "")
                    if not(event.frame.objattr[s] <= int(gdn[2])):
                        res = 0
                else:
                    if not(objects[event.obj].objattr[gdn[0]] <= int(gdn[2])):
                        res = 0
            elif gdn[1] == ">=":
                if gdn[0].startswith("frame."):
                    s = gdn[0].replace("frame.", "")
                    if not(event.frame.objattr[s] >= int(gdn[2])):
                        res = 0
                else:
                    if not(objects[event.obj].objattr[gdn[0]] >= int(gdn[2])):
                        res = 0
            elif gdn[1] == ">":
                if gdn[0].startswith("frame."):
                    s = gdn[0].replace("frame.", "")
                    if not(event.frame.objattr[s] > int(gdn[2])):
                        res = 0
                else:
                    if not(objects[event.obj].objattr[gdn[0]] > int(gdn[2])):
                        res = 0
            elif gdn[1] == "<":
                if gdn[0].startswith("frame."):
                    s = gdn[0].replace("frame.", "")
                    if not(event.frame.objattr[s] < int(gdn[2])):
                        res = 0
                else:
                    if not(objects[event.obj].objattr[gdn[0]] < int(gdn[2])):
                        res = 0
            else:
                print("wrong")
    return res



def findSuitEvents(tmpEvents, tmpObjs):
    res = list()
    for cpu in tmpEvents.items():
        if checkGuards(cpu[1][0], tmpObjs):
            res.append(cpu[1][0])
    return res

def doActions(event, objs):
    #
    print()

def checkSeq(evs, objs):
    tmpEvents = evs
    tmpObjs = objs
    step = findSuitEvents(tmpEvents, tmpObjs)
    if len(step) == 0:
        print("end of events OR error in trace")
    for ev in step:
        stepObjs = tmpObjs
        doActions(ev, tmpObjs)
        #delete event
        checkSeq(evs, stepObjs)

def checkTrace():
    with open('example.yaml', 'r') as file:
        doc = yaml.safe_load(file)
    
    fillEvents(doc)
    checkSeq(events, objects)


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

    # for cpu in events.items():
    #     for ev in cpu[1]:
    #         print(ev.unique_frame, ev.cpu, ev.local_frame, ev.event, ev.obj)
    #         for attr in ev.frame.objattr.items():
    #             print(attr)