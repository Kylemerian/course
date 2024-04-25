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
# vm.threads[0].frames[vm.threads[0].currentFrame].registers['acc'] = 5
# vm.threads[0].frames[vm.threads[0].currentFrame].registers['r1'] = 10
t.checkSequence(t.events)