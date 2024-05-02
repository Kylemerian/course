import sys
import os

for file in os.listdir("./tests2"):
    print("FILENAME: " + file)
    os.system("python3 adapter.py ./tests2/" + file + " modl.txt")
    os.system("python3 ./parsing/main.py modl.txt output > ./ress2/RES_" + file)