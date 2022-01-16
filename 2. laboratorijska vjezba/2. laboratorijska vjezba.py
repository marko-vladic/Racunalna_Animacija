import math
import random
from math import acos
from typing import List, Any

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import pygame

WIDTH = 512
HEIGHT = 512


class Vrh:
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z

    def copy(self):
        return Vrh(self.x, self.y, self.z)


class Izvor:
    def __init__(self, vrh, c, size):
        self.pos = vrh
        self.c_r = c[0]
        self.c_g = c[1]
        self.c_b = c[2]
        self.size = size


class Cestica:
    def __init__(self, direction, v, izvor: Izvor):
        self.izvor = izvor
        self.pos = izvor.pos.copy()
        self.r = izvor.c_r
        self.g = izvor.c_g
        self.b = izvor.c_b
        self.v = v
        self.t = random.randint(70, 90)
        self.sx = direction.x
        self.sy = direction.y
        self.sz = direction.z
        self.osx = 0
        self.osy = 0
        self.osz = 0
        self.kut = 0
        self.size = izvor.size

    def nacrtaj_cesticu(self):
        glColor3f(self.r, self.g, self.b)
        glTranslatef(self.pos.x, self.pos.y, self.pos.z)
        glRotatef(self.kut, self.osx, self.osy, self.osz)

        glBegin(GL_QUADS)
        glTexCoord2d(0.0, 0.0)
        glVertex3f(-self.size, -self.size, 0.0)
        glTexCoord2d(1.0, 0.0)
        glVertex3f(self.size, -self.size, 0.0)
        glTexCoord2d(1.0, 1.0)
        glVertex3f(self.size, self.size, 0.0)
        glTexCoord2d(0.0, 1.0)
        glVertex3f(-self.size, self.size, 0.0)
        glEnd()

        glRotatef(-self.kut, self.osx, self.osy, self.osz)
        glTranslatef(-self.pos.x, -self.pos.y, -self.pos.z)

    def promijeni_poziciju_cestice(self):
        self.pos.x += self.v * self.sx
        self.pos.y += self.v * self.sy
        self.pos.z += self.v * self.sz

    def promijeni_boju_i_velicinu(self):
        if self.b < 1:
            self.b += 0.01
        self.size += 0.03

    def postavi_os(self, os):
        self.osx = os.x
        self.osy = os.y
        self.osz = os.z

    def postavi_kut(self, kut):
        self.kut = kut / (2 * math.pi) * 360


class SustavCestica:
    def __init__(self, program, izvor, ociste):
        self.program = program
        self.current_time = 0
        self.past_time = 0
        self.izvor = izvor
        self.cestice: List[Cestica] = []
        self.ociste = ociste
        self.iteration = 0

    def update(self):
        self.current_time = glutGet(GLUT_ELAPSED_TIME)
        if self.current_time - self.past_time > 20:
            self.iteration += 1
            self.stvori_cestice()
            self.osvjezi_cestice()
            self.past_time = self.current_time
        self.program.my_display()

    def stvori_cestice(self):
        for j in range(3):
            y = random.uniform(-1, 1)
            x = random.uniform(-1, 1)
            z = random.uniform(-1, 1)
            norm = (x ** 2 + y ** 2 + z ** 2) ** 0.5
            x /= norm
            y /= norm
            z /= norm
            self.cestice.append(Cestica(Vrh(x, y, z), 0.5, self.izvor))

    def osvjezi_cestice(self):
        for cestica in self.cestice:
            os, kut = self.izracunaj_podatke_o_cestici(cestica)
            cestica.postavi_kut(kut)
            cestica.postavi_os(os)
            cestica.promijeni_poziciju_cestice()
            cestica.t -= 1
            cestica.promijeni_boju_i_velicinu()
            self.zavrsi_zivot_cestice(cestica)

    def izracunaj_podatke_o_cestici(self, cestica):
        s = Vrh(0, 0, 1)
        e = Vrh(cestica.pos.x - self.ociste.x, cestica.pos.y - self.ociste.y, cestica.pos.z - self.ociste.z)
        os = Vrh(s.y * e.z - e.y * s.z, e.x * s.z - s.x * e.z, s.x * e.y - s.y * e.x)
        s_norm = (s.x ** 2 + s.y ** 2 + s.z ** 2) ** 0.5
        e_norm = (e.x ** 2 + e.y ** 2 + e.z ** 2) ** 0.5
        se = s.x * e.x + s.y * e.y + s.z * e.z
        kut = acos(se / (s_norm * e_norm))
        return os, kut

    def zavrsi_zivot_cestice(self, cestica):
        if cestica.t <= 0:
            self.cestice.remove(cestica)

    def nacrtaj_cestice(self):
        for cestica in self.cestice:
            cestica.nacrtaj_cesticu()


def load_texture(filename):
    surface = pygame.image.load(filename)
    data = pygame.image.tostring(surface, "RGB")
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    gluBuild2DMipmaps(GL_TEXTURE_2D, 3, surface.get_width(), surface.get_height(), GL_RGB, GL_UNSIGNED_BYTE, data)
    return texture


class Program:
    def __init__(self):
        self.ociste = Vrh(0, 0, 50)
        self.izvor = Izvor(Vrh(0, 0, 0), (1, 0, 0), 1)
        self.sustav_cestica = SustavCestica(self, self.izvor, self.ociste)

    def my_display(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(self.ociste.x, self.ociste.y, -self.ociste.z)
        self.sustav_cestica.nacrtaj_cestice()
        glutSwapBuffers()

    def my_reshape(self, w, h):
        global WIDTH, HEIGHT
        WIDTH = w
        HEIGHT = h
        glViewport(0, 0, WIDTH, HEIGHT)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, WIDTH / HEIGHT, 0.1, 150)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glLoadIdentity()
        glClearColor(0, 0, 0, 0)
        glClear(GL_COLOR_BUFFER_BIT)
        glPointSize(1)
        glColor3f(0, 0, 0)

    def main(self):
        glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
        glutInitWindowSize(WIDTH, HEIGHT)
        glutInitWindowPosition(10, 10)
        glutInit()
        self.window = glutCreateWindow("2. labos")
        glutReshapeFunc(self.my_reshape)
        glutDisplayFunc(self.my_display)
        glutIdleFunc(self.sustav_cestica.update)
        self.texture = load_texture("cestica.bmp")
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        glEnable(GL_BLEND)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glutMainLoop()


if __name__ == '__main__':
    p = Program()
    p.main()
