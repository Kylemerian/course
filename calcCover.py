from parsing.parse import parseFile
import sys

o = parseFile("modl.txt")



ins = set()
with open("cover") as f:
    for line in f:
        ins.add(line.replace("\n", ""))
print("Coverage:", len(ins), "/" ,len(o.getEvents()), ":", float(100 * len(ins)/len(o.getEvents())), "%\n\n")
for x in o.getEvents():
    t = x.replace("_Frame", "")
    # print(ins)
    # print(t)
    # break
    if t in ins:
        print("+++\t" + t)
    else:
        print("---\t" + t)