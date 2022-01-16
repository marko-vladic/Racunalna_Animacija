import numpy as np
import math

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


class Objekt:
    def __init__(self, path):
        self.scale_factor = 10
        self.vertices = []
        self.edges = set()
        self.center = [0, 0, 0]
        self.starting_direction = [0, 0, 1]
        self.angle = 90
        self.axis = [0, 0, 0]
        self.ucitaj(path)

    def iscrtaj_objekt(self):
        glBegin(GL_LINES)
        for edge in self.edges:
            for vertex in edge:
                glVertex3fv(self.vertices[vertex])
        glEnd()

    def ucitaj(self, path):
        with open(path, 'r') as file:
            for line in file.readlines():
                line = line.rstrip().split(" ")
                if line[0] == 'v':
                    self.vertices.append((self.scale_factor * float(line[1]), self.scale_factor * float(line[2]),
                                          self.scale_factor * float(line[3])))
                elif line[0] == 'f':
                    self.edges.add((min(int(line[1]), int(line[2])) - 1, max(int(line[1]), int(line[2])) - 1))
                    self.edges.add((min(int(line[1]), int(line[3])) - 1, max(int(line[1]), int(line[3])) - 1))
                    self.edges.add((min(int(line[2]), int(line[3])) - 1, max(int(line[2]), int(line[3])) - 1))




class Krivulja:
    def __init__(self, path):
        self.starting_points = []
        self.points = []
        self.vectors = []
        self.draw_points = []
        self.calculated_draw = False
        self.direction = 1
        self.current_point = 0
        self.ucitaj(path)
        for i in range(len(self.starting_points) - 3):
            self.izracun_tocaka(*self.starting_points[i:i + 4])

    def ucitaj(self, path):
        with open(path, 'r') as file:
            for line in file.readlines():
                line = line.rstrip().split(" ")
                self.starting_points.append((float(line[0]), float(line[1]), float(line[2])))

    def sljedeca_tocka(self):
        self.current_point += self.direction
        try:
            return (self.points[self.current_point - 1], self.vectors[self.current_point - 1])
        except:
            self.direction *= -1
            return (self.points[self.current_point - 2], self.vectors[self.current_point - 2])

    def iscrtaj_krivulju(self):
        glBegin(GL_POINTS)
        for point in self.points:
            glVertex3fv(point)
        glEnd()

    def izracun_tocaka(self, point_0, point_1, point_2, point_3):
        t = 0
        Bi3 = 1 / 6 * np.matrix([[-1, 3, -3, 1], [3, -6, 3, 0], [-3, 0, 3, 0], [1, 4, 1, 0]])
        Rx = np.matrix([[point_0[0]], [point_1[0]], [point_2[0]], [point_3[0]]])
        Ry = np.matrix([[point_0[1]], [point_1[1]], [point_2[1]], [point_3[1]]])
        Rz = np.matrix([[point_0[2]], [point_1[2]], [point_2[2]], [point_3[2]]])
        multiply_point_x = np.matmul(Bi3, Rx)
        multiply_point_y = np.matmul(Bi3, Ry)
        multiply_point_z = np.matmul(Bi3, Rz)
        while t < 1:
            T3 = np.matrix([t ** 3, t ** 2, t, 1])
            T2 = np.matrix([3 * t ** 2, 2 * t, 1, 0])
            self.points.append((float(np.matmul(T3, multiply_point_x)), float(np.matmul(T3, multiply_point_y)),
                                float(np.matmul(T3, multiply_point_z))))
            self.vectors.append((float(np.matmul(T2, multiply_point_x)), float(np.matmul(T2, multiply_point_y)),
                                 float(np.matmul(T2, multiply_point_z))))
            t += 0.02

def jed_vektor(vector):
    return vector / np.linalg.norm(vector)


def kut_vektora(v1, v2):
    v1_u = jed_vektor(v1)
    v2_u = jed_vektor(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))


class Program:
    def __init__(self):
        self.body = None
        self.window = None
        self.krivulja = None
        self.screen_size = (800, 800)

    def render(self):
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClear(GL_COLOR_BUFFER_BIT)
        glColor3f(1, 0, 0)
        glLoadIdentity()

        gluPerspective(45, 1, 1, 1000.0)
        glTranslatef(-4, -5, -100)
        glRotatef(-90, 0, 0, 1)

        self.krivulja.iscrtaj_krivulju()

        glLoadIdentity()
        gluPerspective(45, 1, 1, 1000.0)
        glTranslatef(-4, -5, -100)
        glRotatef(-90, 0, 0, 1)
        glTranslatef(*self.body.center)
        glRotatef(self.body.angle, *self.body.axis)

        self.body.iscrtaj_objekt()

        glFlush()

    def azur_polozaj_obj(self, new_center):
        self.body.center = new_center[0]
        self.body.axis = [self.body.starting_direction[1] * new_center[1][2] - new_center[1][1] * self.body.starting_direction[2],
                          - self.body.starting_direction[0] * new_center[1][2] + new_center[1][0] * self.body.starting_direction[2],
                          self.body.starting_direction[0] * new_center[1][1] - self.body.starting_direction[1] * new_center[1][0]]
        self.body.angle = math.degrees(kut_vektora(self.body.starting_direction, new_center[1]))

    def tipka(self, the_key, mouse_x, mouse_y):
        if the_key == b'a':
            self.azur_polozaj_obj(self.krivulja.sljedeca_tocka())
        self.render()

    def main(self):
        self.body = Objekt("aircraft747.obj")
        self.krivulja = Krivulja('krivulja.txt')
        self.azur_polozaj_obj(self.krivulja.sljedeca_tocka())
        glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
        glutInitWindowSize(800, 800)
        glutInitWindowPosition(10, 10)
        glutInit()
        self.window = glutCreateWindow("OpenGL Objekt")
        glutDisplayFunc(self.render)
        glutKeyboardFunc(self.tipka)
        glutMainLoop()


if __name__ == '__main__':
    p = Program()
    p.main()


