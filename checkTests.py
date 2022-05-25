import os
import subprocess


if __name__ == "__main__":
    negPath = "./tests/negative/"
    posPath = "./tests/positive/"
    for c in [2, 4, 8, 16]:
        cnt = 0
        tests = os.listdir(posPath + str(c))
        for test in tests:
            res = subprocess.run(["python3", "./o.py", "kettle.txt", posPath + str(c) + "/" + test], capture_output=True)
            if res.stdout == b'Is correct trace : True\n':
                cnt += 1
            else:
                print(posPath + str(c) + "/" + test, "failed")
        print(cnt, "of", len(tests), "tests passed in" + posPath + str(c))

    
    for c in [2, 4, 8]:
        cnt = 0
        tests = os.listdir(negPath + str(c))
        for test in tests:
            res = subprocess.run(["python3", "./o.py", "kettle.txt", negPath + str(c) + "/" + test], capture_output=True)
            if res.stdout == b'Is correct trace : False\n':
                cnt += 1
            else:
                print(negPath + str(c) + "/" + test, "failed")
        print(cnt, "of", len(tests), "tests passed in" + negPath + str(c))

