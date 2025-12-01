from math import cos, pi, sin, sqrt

import pygame
from config import *


class Geometry:
    def __init__(self, color, pos, width=3):
        self.color = color
        self.width = width
        self.x, self.y = pos

    def get_center(self):
        return (self.x, self.y)

    def set_center(self, pos):
        self.x, self.y = pos

    def get_width(self):
        return self.width

    def set_width(self, width):
        self.width = width

    def get_color(self):
        return self.color

    def set_color(self, color):
        self.color = color


class Circle(Geometry):
    def __init__(self, color, radius, pos):
        super().__init__(color, pos)
        self.radius = radius

    def draw(self, screen):
        pygame.draw.circle(
            screen, self.color, (self.x, self.y), self.radius, self.width
        )

    def get_radius(self):
        return self.radius

    def set_radius(self, r):
        self.radius = r

    def collide(self, obj):
        ox, oy = obj
        dist = sqrt((self.x - ox) ** 2 + (self.y - oy) ** 2)
        if dist < self.radius:
            return True
        return False


class Parallelogram(Geometry):
    def __init__(self, color, side1, side2, pos):
        super().__init__(color, pos)
        self.side1 = side1
        if not side2:
            self.side2 = side1
        else:
            self.side2 = side2

    def draw(self, screen):
        pygame.draw.rect(
            screen,
            self.color,
            (
                (self.x - self.side1 / 2, self.y - self.side2 / 2),
                (self.side1, self.side2),
            ),
            self.width,
        )

    def get_center(self):
        return (self.x, self.y)

    def collide(self, obj):
        ox, oy = obj

        if ox > (self.x - self.side1 / 2) and ox < (self.x + self.side1 / 2):
            if oy > self.y - self.side2 / 2 and oy < (self.y + self.side2 / 2):
                return True

        return False


class Triangle(Geometry):
    def __init__(self, color, height, pos):
        super().__init__(color, pos)
        self.height = height
        self.color = color
        self.width = 3
        self.radius = (2 * self.height) / 3
        self.v1 = (
            self.x + self.radius * cos(0.5 * pi),
            self.y - self.radius * sin(0.5 * pi),
        )
        self.v2 = (
            self.x + self.radius * cos(210 * pi / 180),
            self.y - self.radius * sin(210 * pi / 180),
        )
        self.v3 = (
            self.x + self.radius * cos(330 * pi / 180),
            self.y - self.radius * sin(330 * pi / 180),
        )

    def draw(self, screen):
        pygame.draw.polygon(
            screen, self.color, [self.v2, self.v3, self.v1], self.width
        )

    def get_height(self):
        return self.height

    def set_height(self, height):
        self.height = height

    def collide(self, obj):
        area = calcArea(self.v1, self.v2, self.v3)
        a1 = calcArea(obj, self.v1, self.v2)
        a2 = calcArea(obj, self.v1, self.v3)
        a3 = calcArea(obj, self.v2, self.v3)

        sum = a1 + a2 + a3
        if int(area) == int(sum):
            return True
        return False


class Root:
    def __init__(self, size, pos):
        self.image = pygame.image.load("Source\Assets\Repetea_Figuras\pe3.png")
        self.size = size
        self.x, self.y = pos
        self.image = pygame.transform.scale(self.image, (self.size, self.size))
        self.circles = []

    def draw(self, screen):

        circle = Circle(GREEN, self.size * 0.60, (self.x, self.y))
        screen.blit(
            self.image, (self.x - self.size / 2, self.y - self.size / 2)
        )
        circle.draw(screen)
        for i in self.circles:
            i.draw(screen)

    def collide(self, obj):
        ox, oy = obj

        if ox > (self.x - self.size / 2) and ox < (self.x + self.size / 2):
            if oy > self.y - self.size / 2 and oy < (self.y + self.size / 2):
                return True

        return False

    def remove_circles(self):
        self.circles.clear()

    def add_circle(self):
        if self.circles == []:
            c1 = Circle(GREEN, self.size * 0.65, (self.x, self.y))
            self.circles.append(c1)

        elif self.circles != []:
            c2 = Circle(GREEN, self.size * 0.70, (self.x, self.y))
            self.circles.append(c2)

    def get_pos(self):
        return (self.x, self.y)

    def get_size(self):
        return self.size


# Aux Function
def calcArea(v1, v2, v3):
    x1, y1 = v1
    x2, y2 = v2
    x3, y3 = v3

    area = abs((x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2)) / 2)

    return area
