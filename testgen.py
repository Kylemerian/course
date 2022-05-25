from enum import unique
import os
import random


def addEvent(file, frame_id, cpu, local_frame, event, object, delta = 0):
    file.write("-\n")
    file.write("    unique_frame: " + str(frame_id) + "\n")
    file.write("    cpu: " + str(cpu) + "\n")
    file.write("    local_frame: " + str(local_frame) + "\n")
    file.write("    event: " + str(event) + "\n")
    file.write("    object: " + str(object) + "\n")
    if event == "AddWater":
        file.write("    frame.delta: " + str(delta) + "\n")
    file.write("    frame.$location: 0" + "\n")
    file.write("    frame.$subframe: 0" + "\n")
    

def genCorrectTrace(path, Ord, cpuNum):
    file = open(path, "w+")
    local_ids = dict()
    unique_id = 0
    for i in range(0, cpuNum):
        local_ids[i] = 0
    
    randCpus = [random.randint(0, cpuNum - 1) for _ in range(len(Ord))]
    for i in range(0, len(randCpus)):
        addEvent(file, unique_id, randCpus[i], local_ids[randCpus[i]], Ord[i], "Kettle", random.randint(1, 99))
        local_ids[randCpus[i]] += 1
        unique_id += 1
    #os.remove(path)


def genPositiveTests(posPath, numTests):
    correctOrd = ["AddWater", "SwitchOn"] + ["Ticking"] * 9 + ["SwitchOff", "RemoveWater"]
    for i in [2, 4, 8, 16]:
        for j in range(numTests):
            genCorrectTrace(posPath + str(i) + "/test" + str(j) + ".yaml", correctOrd, i)


def genNegativeTests(negPath, numTests):
    incorrectOrd1 = ["SwitchOn"] + ["Ticking"] * 9 + ["SwitchOff", "RemoveWater"]
    incorrectOrd2 = ["AddWater"] + ["Ticking"] * 9 + ["SwitchOff", "RemoveWater"]
    # incorrectOrd3 = ["AddWater", "SwitchOn"] + ["Ticking"] * 9 + ["RemoveWater"] INCORR model
    incorrectOrd3 = ["AddWater", "SwitchOn"] + ["Ticking"] * 9 + ["AddWater"]
    incorrectOrd4 = ["AddWater", "SwitchOn"] + ["Ticking"] * 3 + ["SwitchOff", "RemoveWater"]
    incorrectOrd5 = ["AddWater", "SwitchOn"] + ["Ticking"] * 3 + ["SwitchOff", "RemoveWater", "Ticking"]
    for i in [2, 4, 8]:
        for j in range(numTests):
            genCorrectTrace(negPath + str(i) + "/test" + str(j) + ".yaml", incorrectOrd1, i)
            genCorrectTrace(negPath + str(i) + "/test" + str(j + 20) + ".yaml", incorrectOrd2, i)
            genCorrectTrace(negPath + str(i) + "/test" + str(j + 40) + ".yaml", incorrectOrd3, i)
            genCorrectTrace(negPath + str(i) + "/test" + str(j + 60) + ".yaml", incorrectOrd4, i)
            genCorrectTrace(negPath + str(i) + "/test" + str(j + 80) + ".yaml", incorrectOrd5, i)

if __name__ == "__main__":
    negPath = "./tests/negative/"
    posPath = "./tests/positive/"
    genPositiveTests(posPath, 100)
    genNegativeTests(negPath, 100 // 5)
    
    