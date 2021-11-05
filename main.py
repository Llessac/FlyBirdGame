#!/usr/bin/env python
# -*- coding: utf-8 -*-

from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from luma.core.render import canvas
import PIL.Image as im
import time
import _thread
import random
import RPi.GPIO as GPIO


class OledShow:
    def __init__(self):
        self.serial = i2c(port=1, address=0x3c)
        self.device = ssd1306(self.serial)

        self.self = im.open("self.png").convert("1")

        self.v = 0
        self.up = -1
        self.upflag = 0
        self.g = 0.20
        self.y = 32
        self.yl = self.y

        self.wall_x = [60, 100, 140]
        self.wall_y = [int(random.random() * 64), int(random.random() * 64), int(random.random() * 64)]
        self.wall_halfwidth = [int(random.random() * 16 + 10), int(random.random() * 16 + 10), int(random.random() * 16 + 10)]
        self.wall_v = 0.8

        self.end = 0


        GPIO.setmode(GPIO.BCM)
        GPIO.setup(21, GPIO.IN)

    def show(self):
        try:
            while True:
                self.v += self.g
                self.yl += self.v
                self.y = int(self.yl)
                for i in range(len(self.wall_x)):
                    self.wall_x[i] -= self.wall_v
                with canvas(self.device) as draw:
                    draw.bitmap((20, self.y - 5), self.self, fill=1)
                    for i in range(len(self.wall_x)):
                        draw.polygon(((int(self.wall_x[i]), 64), (int(self.wall_x[i]), self.wall_y[i] + self.wall_halfwidth[i]), (int(self.wall_x[i]) + 10, self.wall_y[i] + self.wall_halfwidth[i]), (int(self.wall_x[i]) + 10, 64)), fill=1)
                        draw.polygon(((int(self.wall_x[i]), 0), (int(self.wall_x[i]), self.wall_y[i] - self.wall_halfwidth[i]), (int(self.wall_x[i]) + 10, self.wall_y[i] - self.wall_halfwidth[i]), (int(self.wall_x[i]) + 10, 0)), fill=1)

                if self.wall_x[0] < 30 and self.wall_x[0] > 10:
                    if self.y - 5 < self.wall_y[0] - self.wall_halfwidth[0] or self.y + 5 > self.wall_y[0] + self.wall_halfwidth[0]:
                        break
                elif self.wall_x[0] <= -10:
                    self.wall_x.pop(0)
                    self.wall_y.pop(0)
                    self.wall_halfwidth.pop(0)
                    self.wall_x.append(self.wall_x[-1] + 40)
                    self.wall_y.append(int(random.random() * 64))
                    self.wall_halfwidth.append(int(random.random() * 16 + 10))
            
            print("lose")
            with canvas(self.device) as draw:
                draw.text((32, 16), "GAME OVER", fill=1)

        except KeyboardInterrupt:
            pass

    def control(self):
        try:
            while True:
                if(GPIO.input(21)) == 0:
                    if self.upflag == 0:
                        self.v = self.up
                        self.upflag = 1
                        time.sleep(0.1)
                        if (GPIO.input(21)) == 0:
                            self.v = self.up
                elif self.upflag == 1:
                    self.upflag = 0
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    try:
        oledshow = OledShow()
        _thread.start_new_thread(oledshow.show, ())
        _thread.start_new_thread(oledshow.control, ())
        input()
    except KeyboardInterrupt:
        pass
