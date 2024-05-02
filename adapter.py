import os
import sys
import yaml
import re
from parsing.parse import *

output = open("output", "w")

# local_frame-ы
frames = dict()
# маппинг между реальными thread-id и искусственными cpu-id
cpus = dict()
# unique frames cnt
cpus[-1] = -1


def printArgs(eventName, cmd):
    global output
    # print(cmd)
    evProts = o.getObjs()
    curEvent = evProts[eventName + "_Frame"]
    j = 0
    for arg in curEvent.objAttr.items():
        # pass
        if j + 1 >= len(cmd):
            value = 0
        else:
            value = cmd[j + 1]
        output.write("    frame." + str(arg[0]) + ": " + str(value) + "\n")
        j += 1

# возвращает тип строки (pc counter str [pc]/ memory trace [mem]/ [unk] for other) 
def instype(s):
    s = s.split()
    # print(s)
    if s[3].strip(':') == "pc":
        return "pc"
    if s[3] == "Invoke":
        return "unk"
    return "mem"


tidFlag = 1


def parsePC(s):
    # print(f"##### Parsing command")
    global tidFlag
    global output, frame_num, cpus, frames
    
    s = s.replace(']', '').replace('[', '')
    s = s.split()
    tid = s[1]
    cmd = s[6:]

    # print("REAL TID = ", tid)
    # print("Command = ", cmd)
    # print("KNOWN CPUS: ", cpus)
    # print("Local frames dict:", frames)
    
    # return statement
    if cmd[0] == 'return':
        return
    
    cpus[-1] += 1

    # if real thread is known then get mapped cpu id
    if tid in cpus:
        mappedCpuId = cpus[tid]
        # print("tid in cpus: ", tid)
        # print(frames)
        frames[mappedCpuId] += 1
    # else save new ID
    else:
        # print("size of known threads - 1 =", len(cpus) - 1)
        cpus[tid] = len(cpus) - 1
        # print("size of known threads - 1 =", len(cpus) - 1)
        mappedCpuId = cpus[tid]
        # print(cpus[tid])
        frames[mappedCpuId] = 0
        
    
    local_frame = frames[mappedCpuId]

    output.write("-\n")
    output.write("    " + "cpu: " + str(mappedCpuId) + "\n")
    output.write("    " + "local_frame: " + str(local_frame) + "\n")
    output.write("    unique_frame: " + str(cpus[-1]) + "\n")
    
    tidFlag = 1

    # print(cmd)
    # res = "\t" + " ".join(cmd) + "\n"
    for i in range(len(cmd)):
        cmd[i] = cmd[i].replace(',', '')

    cmd[0] = cmd[0].replace(".", "_")
    if cmd[0] == 'ret':
        cmd[0] = 'return'
    if cmd[0] == 'ret_64':
        cmd[0] = 'return_64'
    if cmd[0] == 'ret_void':
        cmd[0] = 'return_void'
    
    output.write("    event: " + cmd[0] + "\n")
    printArgs(cmd[0], cmd)
    output.write("    pc.pri: " + str(int(s[4], 16)) + "\n")
    # output.write("-\n")
    # print(f"##### End parsing cmd")


def parseMem(s):
    global output, tidFlag
    
    # print(s)

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

    
    # if tidFlag:
    #     output.write("    " + "cpu: " + str(tid) + "\n")
    tidFlag = 0
    output.write("    " + reg + ": " + value + "\n")
    


def adapt(tracefile):
    with open(tracefile, "r") as file:
        s = file.readline()
        while s.find("pc:") == -1:
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
    global o
    if len(sys.argv) != 3:
        print("python3 adapter.py TRACEFILE REKAFILE")
    else:
        o = parseFile(sys.argv[2])
        # o.print()
        adapt(sys.argv[1])
