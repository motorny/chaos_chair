#!/usr/bin/env python3

import os
import random
import math
import colorsys
import numpy as np
import cv2

from chaos_chair.utils import lerp


class Canvas:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.image = np.zeros((w, h, 3), np.uint8)
        self.fill_image()

    def fill_image(self):
        self.image.fill(255)

    def draw_pixel_batch(self, batch):
        multiplier = min(self.w, self.h)
        shift = abs(self.h - self.w) / 2
        for i in range(len(batch)):
            h = 0.5 + math.atan2(batch[i, 1] - 0.5, batch[i, 0] - 0.5) / math.pi / 2
            color = tuple(round(c_i * 255) for c_i in colorsys.hsv_to_rgb(h, 1.0, 1.0))
            self.image[int(batch[i, 0] * multiplier), int(batch[i, 1] * multiplier + shift)] = color


class RandomDrawController:
    MIN_N_COUNT = 3
    MAX_N_COUNT = 12

    MIN_LERP = 0.4
    MAX_LERP = 0.85

    BASE_POINT_R = 1.1

    lerp_functions = [
        lambda x, y, l: 0.55,
        lambda x, y, l: l + 0.01,
        lambda x, y, l: x * y + 0.25,
        lambda x, y, l: x * x + 0.25,
        lambda x, y, l: 0.5,
        lambda x, y, l: math.cos(1.0 / x) + math.sin(1.0 / y),
    ]

    next_point_functions = [
        lambda c, p: any(c != p),
        lambda c, p: any(c != p),
        lambda c, p: any(c != p),
        lambda c, p: any(c != p),
        lambda c, p: not(0.05 <= np.linalg.norm(c - np.array([0.5, 0.5])) <= 0.1),
        lambda c, p: any(c != p),
    ]

    def __init__(self, base_point_number, lerp_ratio, restrict):
        self.point_number = base_point_number
        self.lerp_ratio = lerp_ratio
        self.restrict = restrict
        self.prev_point = -1
        self.current_point = np.array([0.5, 0.5], float)
        self.base_points = []
        self.create_base_points()
        self.lerp_rule_index = 0

    def create_base_points(self):
        self.base_points = [
            np.array([
                max(0,
                    min(1,
                        RandomDrawController.BASE_POINT_R * math.cos(_ + math.pi / 4) * 0.5 + 0.5)),
                max(0,
                    min(1,
                     RandomDrawController.BASE_POINT_R * math.sin(_ + math.pi / 4) * 0.5 + 0.5))],
                float)
            for _ in np.linspace(0, 2 * math.pi, self.point_number + 1)]


    def set_point_number(self, val):
        val = RandomDrawController.MIN_N_COUNT if val > RandomDrawController.MAX_N_COUNT else val
        val = RandomDrawController.MAX_N_COUNT if val < RandomDrawController.MIN_N_COUNT else val
        self.point_number = val
        self.create_base_points()
        self.lerp_ratio = 0.5


    def set_lerp_rule_index(self, val):
        val = 0 if val > len(self.lerp_functions) - 1 else val
        val = len(self.lerp_functions) - 1 if val < 0 else val
        self.lerp_rule_index = val

    def trim_ratio(self, val):
        val = RandomDrawController.MIN_LERP if val > RandomDrawController.MAX_LERP else val
        val = RandomDrawController.MAX_LERP if val < RandomDrawController.MIN_LERP else val
        return val


    def calc_next_point(self, rid):
        next_base = self.base_points[rid]
        self.lerp_ratio = self.trim_ratio(
            self.lerp_functions[int(self.lerp_rule_index)](self.current_point[0], self.current_point[1],
                                                           self.lerp_ratio))

        return lerp(self.current_point, next_base, self.lerp_ratio)

    def get_next_point(self):
        length = len(self.base_points)
        rid = random.randint(0, length - 1)
        cp = self.calc_next_point(rid)

        while not self.next_point_functions[self.lerp_rule_index](cp, self.prev_point):
            rid = random.randint(0, length - 1)
            cp = self.calc_next_point(rid)


        self.current_point = cp
        self.prev_point = rid
        return [self.current_point[0], self.current_point[1]]


W = 800
H = 1200
STEP = 500
canvas = Canvas(W, H)
controller = RandomDrawController(3, 0.5, 0)

def calc_new_batch():
    return np.array([controller.get_next_point() for _ in range(0, STEP)], np.float32)

def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_MOUSEWHEEL:
        canvas.fill_image()
        if flags > 0:
            controller.set_lerp_rule_index(controller.lerp_rule_index + 1)
        else:
            controller.set_point_number(controller.point_number + 1)

        print('Lerp = %s, N = %s' % (controller.lerp_rule_index, controller.point_number))

def main():
    WINDOW_NAME = 'DRAW_CURVE'

    cv2.namedWindow(WINDOW_NAME, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(WINDOW_NAME, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.setMouseCallback(WINDOW_NAME, mouse_callback)

    i = 0
    while (True):
        i += 1
        batch = calc_new_batch()
        canvas.draw_pixel_batch(batch)
        cv2.imshow(WINDOW_NAME, cv2.resize(canvas.image, (H, W)))
        if cv2.waitKey(20) == 27:
            break
        if cv2.waitKey(20) == 13:
            os.system('lp ./res/%s_%s.png' % (str(controller.lerp_rule_index), str(controller.point_number)))

def main_preprocess():
    for i in range(0, 5):
        for j in range(3, 12):
            print('Processing:: lerp:%s  count:%s' % (str(i), str(j)))
            controller.set_lerp_rule_index(i)
            controller.set_point_number(j)
            canvas.fill_image()
            for _ in range(0, 2000):
                batch = calc_new_batch()
                canvas.draw_pixel_batch(batch)

            cv2.imwrite('./res/%s_%s.png' % (str(controller.lerp_rule_index), str(controller.point_number)),
                        canvas.image)

if __name__ == '__main__':
    main()
