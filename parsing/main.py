from parse import parseFile
from vm import *
import sys
from tracing import *
from vm import *


vm = VM()

o = parseFile(sys.argv[1])
# o.print()

t = EventMap(sys.argv[2], o.getObjs(), o.getEvents(), vm)
# t.setObjects(o.getObjs())
t.fillEvents()
# t.findSuitableEvent()
# t.print()
# t.printEventCpuMap()
t.checkSequence(t.events, vm)
print(t.isCorrectTrace)