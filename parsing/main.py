from parse import parseFile
from vm import *
import sys
from tracing import *

o = parseFile(sys.argv[1])
# o.print()

t = EventMap(sys.argv[2], o.getObjs(), o.getEvents())
# t.setObjects(o.getObjs())
t.fillEvents()
t.findSuitableEvent()
t.print()