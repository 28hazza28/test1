from ast import alias
import sympy
from sympy import *
import trimesh

def printMatrix(matrix: alias):
    for i in range(3):
        print(str(expr1[i*3 ]) +"                 "+str(expr1[i*3+1 ]) +"            "+str(expr1[i*3 +2]) +" ")

c_A = Symbol('cos(A)')
c_B = Symbol('cos(B)')
c_C = Symbol('cos(C)')
s_A = Symbol('sin(A)')
s_B = Symbol('sin(B)')
s_C = Symbol('sin(C)')



M_z = Matrix(([c_A,-s_A,0],[s_A,c_A,0],[0,0,1]))
M_y = Matrix(([c_B,0,s_B],[0,1,0],[-s_B,0,c_B]))
M_x = Matrix(([1,0,0],[0,c_C,-s_C],[0,s_C,c_C]))
expr = M_z*M_y
expr1 = expr*M_x
printMatrix(expr1)

mesh = trimesh.load('mesh2.STL')
mesh.show()
