from curses.ascii import isdigit
from enum import unique
from pyparsing import empty
import yaml
import copy
import re
import os
import sys
from eliot import log_call, to_file


def getline(file):
    tmp = file.readline().strip("\n").split(":")
    return tmp


class parseFile:
    def __init__(self, file):
        self.file = file
        with open(self.file, "r") as file:
            self.tp = typeParse(file)
            self.tp.parse()
            self.op = objParse(file)
            self.op.parse()
            self.ep = eventParse(file)
            self.ep.setBuff(self.op.getBuff())
            self.ep.parse()
        
    def getTypes(self):
        return self.tp.getTypes()
    
    def getObjs(self):
        return self.op.getObjs()
    
    def getEvents(self):
        return self.ep.getEvents()        


    def print(self):
        print("#TYPES:")
        print(self.tp.getTypes())
        print("#OBJS:")
        self.op.printObjs()
        print("#EVENTS:")
        self.ep.printEvents()

class typeParse:
    def __init__(self, file):
        self.file = file
        self.buff = getline(self.file)
        self.data = list()
        
    def parse(self):
        if self.buff != [''] and self.buff[0] == 'type':
            # print(self.buff)
            self.data.append(self.buff[1])
            self.buff = getline(self.file)
            self.parse()
            
    def getTypes(self):
        return self.data


class objParse:
    class Object:
        def __init__(self, name):
            self.objAttr = dict()
            self.name = name
            
        def print(self):
            print(self.name)
            print(f'\t{self.objAttr}')
    
    def __init__(self, file):
        self.file = file
        self.buff = getline(self.file)
        self.data = dict()
    
    def parse(self):
        if self.buff != [''] and self.buff[0] == "object":
            tmp = self.Object(self.buff[1])
            name = self.buff[1]
            # print("name =", self.buff[1])
            self.buff = getline(self.file)
            self.attrParse(tmp)
            # print(tmp)
            self.data[name] = tmp
            self.parse()
            
    def attrParse(self, obj):
        if self.buff != [''] and self.buff[0] == "  objattr":
            obj.objAttr[(self.buff[1])] = 0 # init objattr of object
            # print("objAttr = ", self.buff[1])
            self.buff = getline(self.file)
            self.attrParse(obj)
    
    def getObjs(self):
        return self.data

    def printObjs(self):
        for x in self.data.keys():
            self.data[x].print()
    
    def getBuff(self):
        return self.buff


class eventParse:
    class event:
        def __init__(self, name):
            self.name = name
            self.guards = list()
            self.wds = list()
            self.actions = list()
            
        def print(self):
            print(self.name)
            for x in self.guards:
                print(f'\t{x}')
            for x in self.wds:
                print(f'\t{x}')
            for x in self.actions:
                print(f'\t{x}')
            print('-' * 10)
    
    def __init__(self, file):
        self.file = file
        self.buff = ""
        self.data = dict()
    
    def parse(self):
        # print(self.buff)
        if self.buff != [''] and self.buff[0] == "fgraph":
            tmp = self.event(self.buff[1])
            name = self.buff[1]
            # print("TO PARSE EVENT = ", name)
            self.buff = getline(self.file)
            self.buff = getline(self.file)
            self.buff = getline(self.file)
            self.guardParse(tmp)
            # print("guardParse OK")
            self.buff = getline(self.file)
            self.wdsParse(tmp)
            # print("wdsParse OK")
            self.buff = getline(self.file)
            self.actionParse(tmp)
            # print("actionParse OK")
            self.data[name] = tmp
            # print("event = ", name)
            self.parse()
    
    def guardParse(self, ev):
        if self.buff != [''] and self.buff[0] != "wds":
            self.buff = self.buff[0]
            self.buff = self.buff.replace("≥", ">=")
            self.buff = self.buff.replace("≤", "<=")
            self.buff = self.buff.split("и")
            for i in range(len(self.buff)):
                self.buff[i] = self.buff[i].split(" ")
                self.buff[i] = list(filter(lambda x : x, self.buff[i]))
            
            # print("guard = ", self.buff)
            ev.guards.append(self.buff)
            self.buff = getline(self.file)
            self.guardParse(ev)

    
    def wdsParse(self, ev):
        if self.buff != [''] and self.buff[0] != "actions":
            self.buff = getline(self.file)
            # print("WDS = ", self.buff)
            self.wdsParse(ev)
    
    def actionParse(self, ev):
        if self.buff != [''] and self.buff[0] != "fgraph":
            arr = list()
            arr.append(self.buff[0].strip(" "))
            #print("action before parsed=", arr)
            #print("s = ", s)
            if len(self.buff) > 1:
                arr.append(self.buff[1].strip("=").strip(" "))
            else:
                0 # print("action with simple text not added")
            ev.actions.append(arr)
            # print("ACTION = ", arr)
            self.buff = getline(self.file)
            self.actionParse(ev)
    
    def printEvents(self):
        for x in self.data.keys():
            self.data[x].print()
    
    def setBuff(self, buff):
        self.buff = buff
    
    def getEvents(self):
        return self.data

    

# print(o.getObjs())