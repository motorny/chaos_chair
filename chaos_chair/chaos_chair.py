#!/usr/bin/env python3

import random
import math
import numpy as np
from tkinter import Tk, Canvas, PhotoImage





percent = 0.5
width = 1000
height = 1000
window = Tk()
canvas = Canvas(window, width=width, height=height, bg="#000000")
canvas.pack()
img = PhotoImage(width=width, height=height)

base_points = []
current = np.array([width / 2,height / 2], float)
def setup() :
    base_points_cnt = 4

    for i in range(base_points_cnt):
        angle = i * math.pi * 2/ base_points_cnt
        v = np.array([math.cos(angle) * width / 2, math.sin(angle) * height / 2], float)
        v = v + np.array([width/2, height/2],float)
        base_points.append(v)

def reset_image():
    global img
    img = PhotoImage(width=width, height=height)
    canvas.create_image((width // 2, height // 2), image=img, state="normal")




def lerp(v1, v2, d):
    return v1 * (1 - d) + v2 * d


previousInd = 0
def draw(frame):
    if frame % 100 == 0:
        reset_image()
    global previousInd
    global current

    for i in range(1000):
        nextInd = (previousInd + random.randint(-1, 1)) % len(base_points)
        #nextInd = random.randint(0,len(base_points) - 1)
        next = base_points[nextInd]
        #if nextInd + previousInd != len(base_points):
        current = lerp(current, next, percent)
        img.put("#ffffff", (int(current[0]), int(current[1])))
            #canvas.create_oval(int(current[0]), int(current[1]), int(current[0]), int(current[1]), width=0, fill='white')
        previousInd = nextInd

max_frame = 300
setup()
print(base_points)
for frame in range(max_frame):
    draw(frame)
    window.update_idletasks()
    window.update()

img.write('some_name.png', format='png')