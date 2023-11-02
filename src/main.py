import cv2
import numpy as np
import OpenGL
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from PIL import Image

from constants import *
from glyphs import Glyphs
from objloader import *
from webcam import Webcam


class Session:

    def __init__(self):
        self.webcam = Webcam()
        self.webcam.start()
        self.objs = []
        self.texture_background = None

    def _init_gl(self, w, h):
        glClearColor(0.0,0.0,0.0,0.0)
        glClearDepth(1.0)
        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        glLoadEntity()
        gluPerspective(34,1.5,0.1,100.0)
        glMatrixMode(GL_MODELVIEW)
        self.objs = OBJ('board.obj')
        glEnable(GL_TEXTURE_2D)
        self.texture_background = gkGenTextures(1)

    def _draw_scene(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadEntity()

        image = self.webcam.get_current_frame()

        bg_image = cv2.flip(image,0)
        bg_image = image.fromarray(bg_image)
        ix = bg_image.size[0]
        iy = bg_image.size[1]
        bg_image = bg_image.tobytes('raw','BGRX', 0 ,-1)

        glBindTexture(GL_TEXTURE_2D, self.texture_background)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexImage2D(GL_TEXTURE_2D, 0, 3, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, bg_image)

        # draw background
        glBindTexture(GL_TEXTURE_2D, self.texture_background)
        glPushMatrix()
        glTranslatef(0.0,0.0,-10.0)
        self._draw_background()
        glPopMatrix()

        # handle glyphs
        self._handle_glyphs(image)

        glutSwapBuffers()

        def _handle_glyphs(self, image):

        # attempt to detect glyphs
        glyphs = []

        try:
            glyphs = self.glyphs.detect(image)
        except Exception as ex:
            print(ex)

        if not glyphs:
            return

        for glyph in glyphs:

            rvecs, tvecs, glyph_name = glyph

            # build view matrix
            rmtx = cv2.Rodrigues(rvecs)[0]

            view_matrix = np.array([[rmtx[0][0],rmtx[0][1],rmtx[0][2],tvecs[0][0]],
                                    [rmtx[1][0],rmtx[1][1],rmtx[1][2],tvecs[1][0]],
                                    [rmtx[2][0],rmtx[2][1],rmtx[2][2],tvecs[2][0]],
                                    [0.0       ,0.0       ,0.0       ,1.0    ]])

            view_matrix = view_matrix * self.INVERSE_MATRIX

            view_matrix = np.transpose(view_matrix)

            # load view matrix and draw shape
            glPushMatrix()
            glLoadMatrixd(view_matrix)

            if glyph_name == SHAPE_CONE:
                glCallList(self.cone.gl_list)
            elif glyph_name == SHAPE_SPHERE:
                glCallList(self.sphere.gl_list)

            glPopMatrix()

    def _draw_background(self):
        # draw background
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 1.0); glVertex3f(-4.0, -3.0, 0.0)
        glTexCoord2f(1.0, 1.0); glVertex3f( 4.0, -3.0, 0.0)
        glTexCoord2f(1.0, 0.0); glVertex3f( 4.0,  3.0, 0.0)
        glTexCoord2f(0.0, 0.0); glVertex3f(-4.0,  3.0, 0.0)
        glEnd( )

    def main(self):
        # setup and run OpenGL
        print(bool(glutInit))
        glutInit()
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
        glutInitWindowSize(640, 480)
        glutInitWindowPosition(800, 400)
        self.window_id = glutCreateWindow("OpenGL Glyphs")
        glutDisplayFunc(self._draw_scene)
        glutIdleFunc(self._draw_scene)
        self._init_gl(640, 480)
        glutMainLoop()