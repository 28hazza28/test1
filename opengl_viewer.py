#from socket import *
import socket
import sys
import time
import serial
import math
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QWidget, QPushButton,QSlider, QLineEdit, QOpenGLWidget,QTextEdit,
    QInputDialog, QApplication,QGridLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
from PyQt5.QtGui import QBrush, QColor, QPainter, QPen, QPolygon
from PyQt5.QtCore import (pyqtProperty, pyqtSignal, pyqtSlot, QPoint, QSize,
        Qt, QTime, QTimer)
import OpenGL.GL as gl






class Viewer3D(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Графики")
               
        self.build()
    def build(self):
        self.glWidget = GLWidget()
        mainLayout1 = QGridLayout()
        mainLayout1.addWidget(self.glWidget,0,0,1,1)
        self.setLayout(mainLayout1)
    
class GLWidget(QOpenGLWidget):
    xRotationChanged = pyqtSignal(int)
    yRotationChanged = pyqtSignal(int)
    zRotationChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super(GLWidget, self).__init__(parent)
        
        self.object = 0
        self.xRot = 2200
        self.yRot = 0
        self.zRot = 1200
        self.offx=0.0
        self.offy=0.0
        self.lastPos = QPoint()
        self.zoom=0.1
        self.trolltechGreen = QColor.fromCmykF(1.0, 0.5, 0.5, 0.0)
        self.trolltechGreen1 = QColor.fromCmykF(1.0, 0.7, 0.7, 0.0)
        self.trolltechRed = QColor.fromCmykF(0.0, 1.0, 1.0, 0.0)
        self.trolltechPurple = QColor.fromCmykF(0.0, 0.0, 0.0, 0.0)
        self.l2=[]
        self.resize(1400, 800) 
    def getOpenglInfo(self):
        info = """
            Vendor: {0}
            Renderer: {1}
            OpenGL Version: {2}
            Shader Version: {3}
        """.format(
            gl.glGetString(gl.GL_VENDOR),
            gl.glGetString(gl.GL_RENDERER),
            gl.glGetString(gl.GL_VERSION),
            gl.glGetString(gl.GL_SHADING_LANGUAGE_VERSION)
        )

        return info

    def minimumSizeHint(self):
        return QSize(50, 50)

    def sizeHint(self):
        return QSize(400, 400)

    def setXRotation(self, angle):
        #angle = self.normalizeAngle(angle)
        if angle != self.xRot:
            self.xRot = angle
            self.xRotationChanged.emit(angle)
            self.update()

    def setYRotation(self, angle):
        #angle = self.normalizeAngle(angle)
        if angle != self.yRot:
            self.yRot = angle
            self.yRotationChanged.emit(angle)
            self.update()

    def setZRotation(self, angle):
        #angle = self.normalizeAngle(angle)
        if angle != self.zRot:
            self.zRot = angle
            self.zRotationChanged.emit(angle)
            self.update()

    def initializeGL(self):
        #print(self.getOpenglInfo())

        self.setClearColor(self.trolltechPurple)
        #self.object = self.makeObject()
        gl.glShadeModel(gl.GL_FLAT)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_CULL_FACE)
        self.resizeGL(400,400)
    def koordList(self,l1):
        self.l2=l1
    
    
    
    def paintGL(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glLoadIdentity()
        gl.glTranslated(0.0,0.0,-10.0)
        gl.glScalef(self.zoom,self.zoom,1)
        gl.glRotated(self.xRot / 16.0, 1.0, 0.0, 0.0)
        gl.glRotated(self.yRot / 16.0, 0.0, 1.0, 0.0)
        gl.glRotated(self.zRot / 16.0, 0.0, 0.0, 1.0)
#--------Lines-------------------------
        
        
        genList = gl.glGenLists(1)
        gl.glNewList(genList, gl.GL_COMPILE)       
        gl.glLineWidth(1.0)
        gl.glBegin(gl.GL_TRIANGLES)
        self.setColor(self.trolltechGreen)
        for i in range(2,len(self.l2)-1):
            if self.l2[i-1][3]==1:
                self.setColor(self.trolltechGreen)
            else:
                self.setColor(self.trolltechRed)
            gl.glVertex3d(self.l2[i-1][0]+self.offx, self.l2[i-1][1]+self.offy, self.l2[i-1][2])
            gl.glVertex3d(self.l2[i][0]+self.offx, self.l2[i][1]+self.offy, self.l2[i][2])
        gl.glEnd()
        gl.glEndList()
        gl.glCallList(genList)

#--------Points-------------------------
        genList = gl.glGenLists(1)
        gl.glNewList(genList, gl.GL_COMPILE)
        gl.glPointSize(1.8)
        gl.glBegin(gl.GL_POINTS)
        self.setColor(self.trolltechGreen1)
        
        for i in range(1,len(self.l2)):
            gl.glVertex3d(self.l2[i-1][0]+self.offx, self.l2[i-1][1]+self.offy, self.l2[i-1][2])
            gl.glVertex3d(self.l2[i][0]+self.offx, self.l2[i][1]+self.offy, self.l2[i][2])
        gl.glEnd()
        gl.glEndList()
        gl.glCallList(genList)


        self.update()

        

    def resizeGL(self, width, height):
        side = min(width, height)
        if side < 0:
            return

        gl.glViewport((width - side) // 2, (height - side) // 2, side,
                           side)

        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(-0.5, +0.5, +0.5, -0.5, -1000, 1000.0)
        gl.glMatrixMode(gl.GL_MODELVIEW)
    def wheelEvent(self, event):
        wheelcounter = event.angleDelta()
        if wheelcounter.y() / 120 == -1:
            if self.zoom<0.02:
                self.zoom==self.zoom
            else:
                self.zoom*=0.7
        elif wheelcounter.y() / 120 == 1:
            self.zoom*=1.3
        self.update()
    def mousePressEvent(self, event):
        self.lastPos = event.pos()

    def mouseMoveEvent(self, event):
        dx = event.x() - self.lastPos.x()
        dy = event.y() - self.lastPos.y()

        if event.buttons() & Qt.LeftButton:
            self.setXRotation(self.xRot + 8 * dy)
            #self.setYRotation(self.yRot + 8 * dx)
            self.setZRotation(self.zRot + 8 * dx)
        elif event.buttons() & Qt.RightButton:
            self.offx+=dx/360#зависит от угла и масштаба ещё
            self.offy+=dy/360

        self.lastPos = event.pos()
        self.update()

    def quad(self, x1, y1, x2, y2, x3, y3, x4, y4):
        self.setColor(self.trolltechGreen)

        gl.glVertex3d(x1, y1, -0.5)
        gl.glVertex3d(x2, y2, -0.5)
        gl.glVertex3d(x3, y3, -0.5)
        gl.glVertex3d(x4, y4, -0.5)

        gl.glVertex3d(x4, y4, +0.05)
        gl.glVertex3d(x3, y3, +0.05)
        gl.glVertex3d(x2, y2, +0.05)
        gl.glVertex3d(x1, y1, +0.05)


    def normalizeAngle(self, angle):
        while angle < 0:
            angle += 360 * 16
        while angle > 360 * 16:
            angle -= 360 * 16
        return angle

    def setClearColor(self, c):
        gl.glClearColor(c.redF(), c.greenF(), c.blueF(), c.alphaF())

    def setColor(self, c):
        gl.glColor4f(c.redF(), c.greenF(), c.blueF(), c.alphaF())  
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Viewer3D()
    window.show()
    sys.exit(app.exec_())
