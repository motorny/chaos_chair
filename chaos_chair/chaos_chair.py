#!/usr/bin/env python3

import random
import math
import numpy as np
from tkinter import Tk, Canvas, PhotoImage



paramDict = {"n_count": 3,"percent" : 1.0, "restrict" : -1}
stepDict = {"n_count": 1,"percent" : -0.05, "restrict" : 1}
paramCur = 0


width = 1000
height = 1000
window = Tk()
canvas = Canvas(window, width=width, height=height, bg="#000000")
canvas.pack()
img = PhotoImage(width=width, height=height)
canvas.create_image((width // 2, height // 2), image=img, state="normal")
base_points = []
current = np.array([width / 2,height / 2], float)
def setup() :
    base_points_cnt = paramDict["n_count"]

    global base_points
    base_points = []
    for i in range(base_points_cnt):
        angle = i * math.pi * 2/ base_points_cnt
        v = np.array([math.cos(angle) * width / 2, math.sin(angle) * height / 2], float)
        v = v + np.array([width/2, height/2],float)
        base_points.append(v)

def reset_image():
    global img
    setup()
    img = PhotoImage(width=width, height=height)
    canvas.create_image((width // 2, height // 2), image=img, state="normal")




def lerp(v1, v2, d):
    return v1 * (1 - d) + v2 * d


previousInd = 0
def draw():
    global previousInd
    global current

    for i in range(500):
        #nextInd = (previousInd + random.randint(-1, 1)) % len(base_points)
        nextInd = random.randint(0,len(base_points) - 1)

        dif = min(abs(nextInd - previousInd), paramDict["n_count"] - abs(nextInd - previousInd))
        if dif > paramDict["restrict"]:
            next = base_points[nextInd]
            current = lerp(current, next, paramDict["percent"])
            img.put("#ffffff", (int(current[0]), int(current[1])))
            #canvas.create_oval(int(current[0]), int(current[1]), int(current[0]), int(current[1]), width=0, fill='white')
        previousInd = nextInd

max_frame = 3000
setup()
count = 0


lastChange = None

def mouse_wheel(event):
    if event.num == 5 or event.delta == -120:
        change = -1
    if event.num == 4 or event.delta == 120:
        change = 1

    global count
    global lastChange
    global paramCur
    if lastChange is None:
        lastChange = change

    if lastChange != change:
        paramCur += 1
        paramCur = paramCur % len(paramDict)


    key = list(paramDict.keys())[paramCur]


    paramDict[key] += stepDict[key]
    if key == "percent" and paramDict[key] <=0:
        paramDict["percent"] = 1.0

    if key == "restrict" and paramDict[key] >= paramDict["n_count"] // 2:
        paramDict["restrict"] = -1

    print(key,paramDict[key])
    lastChange = change
    reset_image()

window.bind("<MouseWheel>", mouse_wheel)
# with Linux OS
window.bind("<Button-4>", mouse_wheel)
window.bind("<Button-5>", mouse_wheel)


#for frame in range(max_frame):
while True:
    draw()
    window.update_idletasks()
    window.update()

#img.write('some_name.png', format='png')