#!/usr/bin/env python3
import sys
import math
import numpy as np

from glfw.GLFW import *

from OpenGL.GL import *
from OpenGL.GLU import *

# Liczba podziałów siatki wzdłuż każdej z osi (siatka N x N)
N = 30

# Tablice przechowujące współrzędne wierzchołków oraz składowe kolorów RGB
vertices = np.zeros((N, N, 3), np.float32)
colors = np.zeros((N, N, 3), np.float32)

# Aktualny tryb rysowania: 1 - ocena 3.0, 2 - 3.5, 3 - 4.0, 4 - 4.5
current_mode = 4

def calculate_egg():
    """Wyznaczenie współrzędnych wierzchołków oraz statycznych kolorów modelu."""
    global vertices, colors
    u_values = np.linspace(0.0, 1.0, N)
    v_values = np.linspace(0.0, 1.0, N)

    for i in range (N):
        u = u_values[i]

        # Wielomiany definiujące promień oraz wysokość y przekroju poprzecznego
        radius = (-90 * (u**5) + 225 * (u**4) - 270 * (u**3) + 180 * (u**2) - 45 * u)
        y_value = 160 * (u**4) - 320 * (u**3) + 160 * (u**2) - 5

        for j in range (N):
            v = v_values[j]
            x_value = radius * math.cos(math.pi * v)
            z_value = radius * math.sin(math.pi * v)

            # Zapisanie współrzędnych przestrzennych (x, y, z)
            vertices[i, j] = [x_value, y_value, z_value]

            # Losowanie koloru raz przy starcie, aby uniknąć efektu migotania klatek
            colors[i, j] = [
                np.random.random(),
                np.random.random(),
                np.random.random(),
            ]
    # Wyrównanie kolorów na szwie (dla v = 0 oraz v = 1), aby wyeliminować artefakty łączenia
    for i in range(N):
        colors[i, N - 1] = colors[i, 0]

def spin(angle):
    """Złożony obrót wokół trzech osi układu współrzędnych."""
    glRotatef(angle, 1.0, 0.0, 0.0)
    glRotatef(angle, 0.0, 1.0, 0.0)
    glRotatef(angle, 0.0, 0.0, 1.0)

# --- Zadanie na ocenę 3.0: Model punktowy (chmura punktów) ---
def draw_egg_points():
    glPointSize(3.0) # Ustalenie rozmiaru rastrowanego punktu na 3x3 piksele
    glBegin(GL_POINTS)
    glColor3f(1.0, 1.0, 0.0) # Jednolity żółty kolor

    for i in range(N):
        for j in range(N):
            glVertex3fv(vertices[i, j])
    glEnd()

# --- Zadanie na ocenę 3.5: Model krawędziowy (siatka linii) ---
def draw_egg_lines():
    glBegin(GL_LINES)
    glColor3f(0.5, 0.0, 0.5)

    for i in range(N):
        for j in range(N):
            # Łączenie z sąsiadem pionowym wzdłuż parametru u
            if i + 1 < N:
                glVertex3fv(vertices[i, j])
                glVertex3fv(vertices[i + 1, j])

            # Łączenie z sąsiadem poziomym wzdłuż parametru v
            if j + 1 < N:
                glVertex3fv(vertices[i, j])
                glVertex3fv(vertices[i, j + 1])
    glEnd()

# --- Zadanie na ocenę 4.0: Model powierzchniowy (trójkąty) ---
def draw_egg_triangles():
    glBegin(GL_TRIANGLES)
    glColor3f(0.75, 0.5, 0.0)

    # Iteracja do N - 1 zapobiega wyjściu poza zakres tablicy dla indeksu + 1
    for i in range(N - 1):
        for j in range(N - 1):
            # Pierwszy trójkąt komórki siatki
            glColor3fv(colors[i, j])
            glVertex3fv(vertices[i, j])

            glColor3fv(colors[i + 1, j])
            glVertex3fv(vertices[i + 1, j])

            glColor3fv(colors[i, j + 1])
            glVertex3fv(vertices[i, j + 1])

            # Drugi trójkąt dopełniający komórkę siatki
            glColor3fv(colors[i, j + 1])
            glVertex3fv(vertices[i, j + 1])

            glColor3fv(colors[i + 1, j])
            glVertex3fv(vertices[i + 1, j])

            glColor3fv(colors[i + 1, j + 1])
            glVertex3fv(vertices[i + 1, j + 1])
    glEnd()

# --- Zadanie na ocenę 4.5: Model zoptymalizowany (paski trójkątów) ---
def draw_egg_triangle_strip():
    # Rysowanie bryły pasami poziomymi łączącymi warstwy i oraz i + 1
    for i in range(N - 1):
        glBegin(GL_TRIANGLE_STRIP)
        # Przejście przez pełen zakres N domyka pas i eliminuje pionową szczelinę
        for j in range(N):
            glColor3fv(colors[i, j])
            glVertex3fv(vertices[i, j])

            glColor3fv(colors[i + 1, j])
            glVertex3fv(vertices[i + 1, j])
        glEnd()

def key_callback(window, key, scancode, action, mods):
    """Obsługa zdarzeń klawiatury - przełączanie trybów wyświetlania klawiszami 1-4."""
    global current_mode
    if action == GLFW_PRESS:
        if key == GLFW_KEY_1:
            current_mode = 1
        elif key == GLFW_KEY_2:
            current_mode = 2
        elif key == GLFW_KEY_3:
            current_mode = 3
        elif key == GLFW_KEY_4:
            current_mode = 4

def startup():
    update_viewport(None, 400, 400)
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST) # Włączenie bufora Z do poprawnego przesłaniania powierzchni

    # Jednorazowa inicjalizacja geometrii i kolorów
    calculate_egg()


def shutdown():
    pass


def axes():
    """Rysowanie osi układu współrzędnych: X (czerwona), Y (zielona), Z (niebieska)."""
    glBegin(GL_LINES)

    glColor3f(1.0, 0.0, 0.0)
    glVertex3f(-5.0, 0.0, 0.0)
    glVertex3f(5.0, 0.0, 0.0)

    glColor3f(0.0, 1.0, 0.0)
    glVertex3f(0.0, -5.0, 0.0)
    glVertex3f(0.0, 5.0, 0.0)

    glColor3f(0.0, 0.0, 1.0)
    glVertex3f(0.0, 0.0, -5.0)
    glVertex3f(0.0, 0.0, 5.0)

    glEnd()


def render(time):
    # Czyszczenie bufora koloru oraz bufora głębokości
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # Ciągła animacja rotacji dla trybów od 3.5 w górę
    if current_mode > 1:
        spin(time * 180.0 / math.pi)

    axes()

    if current_mode == 1:
        draw_egg_points()
    elif current_mode == 2:
        draw_egg_lines()
    elif current_mode == 3:
        draw_egg_triangles()
    elif current_mode == 4:
        draw_egg_triangle_strip()

    glFlush()


def update_viewport(window, width, height):
    if width == 0:
        width = 1
    if height == 0:
        height = 1
    aspect_ratio = width / height

    glMatrixMode(GL_PROJECTION)
    glViewport(0, 0, width, height)
    glLoadIdentity()

    if width <= height:
        glOrtho(-7.5, 7.5, -7.5 / aspect_ratio, 7.5 / aspect_ratio, 7.5, -7.5)
    else:
        glOrtho(-7.5 * aspect_ratio, 7.5 * aspect_ratio, -7.5, 7.5, 7.5, -7.5)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def main():
    if not glfwInit():
        sys.exit(-1)

    window = glfwCreateWindow(400, 400, __file__, None, None)
    if not window:
        glfwTerminate()
        sys.exit(-1)

    glfwMakeContextCurrent(window)
    glfwSetFramebufferSizeCallback(window, update_viewport)
    glfwSetKeyCallback(window, key_callback)
    glfwSwapInterval(1)

    startup()
    while not glfwWindowShouldClose(window):
        render(glfwGetTime())
        glfwSwapBuffers(window)
        glfwPollEvents()
    shutdown()

    glfwTerminate()


if __name__ == '__main__':
    main()
