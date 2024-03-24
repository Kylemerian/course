import os
import sys
import yaml
import re

output = open("output", "w")
output.write("-\n")

frames = dict()
cpus = dict()
frame_num = 0

def todo():
    return "todo: "

# возвращает тип строки (pc counter str [pc]/ memory trace [mem]/ [unk] for other) 
def instype(s):
    s = s.split()
    if s[3].strip(':') == "pc":
        return "pc"
    if s[3] == "Invoke":
        return "unk"
    return "mem"


tidFlag = 1


def parsePC(s):
    global tidFlag
    global output, frame_num
    s = s.replace(']', '').replace('[', '')
    s = s.split()
    tid = s[1]
    cmd = s[6:]
    
    
    frame_num += 1

    if tid in cpus:
        tid = cpus[tid]
    else:
        cpus[tid] = len(cpus)
        tid = cpus[tid]  

    output.write("-\n")
    output.write("\t" + "cpu: " + str(tid) + "\n")
    output.write("\tunique_frame: " + str(frame_num) + "\n")
    
    tidFlag = 1

    print(cmd)
    # res = "\t" + " ".join(cmd) + "\n"
    for i in range(len(cmd)):
        cmd[i] = cmd[i].replace(',', '')
    output.write("\tevent: " + cmd[0] + "\n")
    for i in range(len(cmd) - 1):
        output.write("\t" + todo() + cmd[i + 1] + "\n")
    output.write("-\n")


def parseMem(s):
    global output, tidFlag
    
    s = s.replace(']', '').replace('[', '')
    s = s.split()
    tid = s[1]
    reg = s[3]
    value = s[6]
    

    if tid in cpus:
        tid = cpus[tid]
    else:
        cpus[tid] = len(cpus)
        tid = cpus[tid] 

    
    if tidFlag:
        output.write("\t" + "cpu: " + str(tid) + "\n")
    tidFlag = 0
    output.write("\t" + reg + ": " + value + "\n")
    


def separateMemFrame():
    pass


def adapt(tracefile):
    with open(tracefile, "r") as file:
        s = file.readline()
        while s:
            typ = instype(s)
            if typ == "pc":
                parsePC(s)
            elif typ == "mem":
                parseMem(s)
            else:
                print("unk")
            s = file.readline()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("python3 adapter.py TRACEFILE")
    else:
        # print(sys.argv[1])
        adapt(sys.argv[1])