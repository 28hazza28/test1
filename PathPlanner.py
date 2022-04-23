from asyncio.windows_events import NULL
from audioop import cross
from cmath import sqrt
from operator import sub
from pickle import TRUE
import numpy as np
import matplotlib.pyplot as plt
from scipy import interpolate
import random
from opengl2_viewer import Paint_in_GL, Point3D, PrimitiveType,GLWidget,QtWidgets
import sys

from polygon import Mesh3D, Polygon3D

def plane_equation (normal: Point3D, vector_x: Point3D, point: Point3D):
    x1 = normal.x + point.x
    y1 = normal.y+ point.y
    z1 = normal.z + point.z
    x2 = vector_x.x + point.x
    y2 = vector_x.y + point.y
    z2 = vector_x.z + point.z
    x3 = point.x
    y3 = point.y
    z3 = point.z
    znamenatel = x1*y2*z3-x1*y3*z2-x2*y1*z3+x2*y3*z1+x3*y1*z2-x3*y2*z1
    if znamenatel == 0:
        print("znam==0")
        return Point3D(0,0,1)
    else:
        x = -(y1*z2-y2*z1-y1*z3+y3*z1+y2*z3-y3*z2)/(x1*y2*z3-x1*y3*z2-x2*y1*z3+x2*y3*z1+x3*y1*z2-x3*y2*z1)

        y = (x1*z2-x2*z1-x1*z3+x3*z1+x2*z3-x3*z2)/(x1*y2*z3-x1*y3*z2-x2*y1*z3+x2*y3*z1+x3*y1*z2-x3*y2*z1)

        z = -(x1*y2-x2*y1-x1*y3+x3*y1+x2*y3-x3*y2)/(x1*y2*z3-x1*y3*z2-x2*y1*z3+x2*y3*z1+x3*y1*z2-x3*y2*z1)
        print("znam==1")
        return Point3D(x,y,z)

def correct_normal(normal: Point3D, vector_x: Point3D, point: Point3D):
    n = plane_equation (normal, vector_x, point)
    A = n.x
    B = n.y
    C = n.z
    D = 1
    ax = vector_x.x
    ay = vector_x.y
    az = vector_x.z

    by = -(A*az - C*ax - D*ax + D*az)/(A*ay-A*az-B*ax+B*az+C*ax-C*ay)
    bz = (D*ax-A*ay*by+B*ax*by)/(A*az-C*ax)
    bx = -(ay*by+az*bz)/ax
    return Point3D(bx, by, bz).normalyse()

def distance(p1: Point3D, p2: Point3D):
    dist3 = (p1.x-p2.x)**2+(p1.y-p2.y)**2+(p1.z-p2.z)**2
    return np.sqrt(dist3)

def area_around_point(mesh: Mesh3D, p: Point3D, r_area: float):
    polygons_array = []
    for i in range (len(mesh.polygons)):
        dist = distance(p, mesh.polygons[i].vert_arr[0])
        if dist < r_area:
            polygons_array.append(mesh.polygons[i]) 
    return polygons_array

def comp_normal_in_area(pol_list: list[Polygon3D]):
    if pol_list != NULL:
        if len(pol_list) != 0:
            sum_norm = Point3D(0, 0, 0)
            for i in range (len(pol_list)):
                sum_norm += pol_list[i].n
            return sum_norm.normalyse()
        else:
            return Point3D(0, 0, 1)
    else:
        return Point3D(0, 0, 1)


def createFrame(matrix,dim:float):
    p1 = Point3D(matrix[0][3],matrix[1][3],matrix[2][3])
    p2 = Point3D(dim*matrix[0][0],dim*matrix[0][1],dim*matrix[0][2])
    p3 = Point3D(dim*matrix[1][0],dim*matrix[1][1],dim*matrix[1][2])
    p4 = Point3D(dim*matrix[2][0],dim*matrix[2][1],dim*matrix[2][2])
    ps = []
    ps.append(p1) 
    ps.append(p1+p2)
    ps.append(p1) 
    ps.append(p1+p3)
    ps.append(p1) 
    ps.append(p1+p4) 
    return ps
def computeYvector(rx:Point3D,rz:Point3D):
    x = rz.y*rx.z-rz.z*rx.y
    y = rz.z*rx.x-rz.x*rx.z
    z = rz.x*rx.y-rz.y*rx.x
    return Point3D(x,y,z)

def computeXvector(p1:Point3D,p2:Point3D):
    pd = p2-p1
    pd = pd.normalyse()
    return pd

def matrix_of_rotation(traj:list[Point3D],normals:list[Point3D], mesh: Mesh3D):
    matr_arr = []
    for i in range(len(traj)-1):
        rx = computeXvector(traj[i],traj[i+1])
        rz = comp_normal_in_area(area_around_point(mesh, traj[i], 1.5))
        rz = correct_normal(rz, rx, traj[i])
        ry = computeYvector(rx,rz)
        matr = [[rx.x,rx.y,rx.z,traj[i].x],[ry.x,ry.y,ry.z,traj[i].y],[rz.x,rz.y,rz.z,traj[i].z],[0,0,0,1]]
        matr_arr.append(matr)
    return matr_arr

def projection(mesh: Mesh3D, traj: Mesh3D)->tuple[list[Point3D],list[Point3D]]:
    traj_proj_arr_:list[Point3D] = []
    traj_proj_arr_n:list[Point3D] = []
    for i in range (len(traj.polygons)):
        p,n = point_on_triangle(mesh, traj.polygons[i])
        p.z+=2
        traj_proj_arr_.append(p)
        traj_proj_arr_n.append(n)
    return traj_proj_arr_,traj_proj_arr_n

def point_on_triangle(mesh: Mesh3D, polygon: Polygon3D)->tuple[Point3D,Point3D]:
    p = polygon.vert_arr[0]
    for i in range (len(mesh.polygons)):
        detect = mesh.polygons[i].affilationPoint(p)
        if detect == TRUE:
            return mesh.polygons[i].project_point(p), mesh.polygons[i].n
    

def GenerateContour(n: int)->list[Point3D]:
    step = 2*np.pi/n
    a = 0
    contour = []
    for a in range (n):
        l = random.uniform(5, 7)
        x = l*np.cos(a*step)
        y = l*np.sin(a*step)
        contour.append(Point3D(x, y, 0))
    return contour

def divideTraj(s: list[Point3D], step: float):
    cont_traj = []
    for i in range(len(s)-1):
        cont_traj.append(s[i])
        dist2 = (s[i+1].x-s[i].x)**2+(s[i+1].y-s[i].y)**2+(s[i+1].z-s[i].z)**2
        dist = np.sqrt(dist2)
        
        if(2*dist>step):
            n = int(dist/step)
            for j in range(n):
                x = s[i].x +(step*j*(s[i+1].x - s[i].x))/dist
                y = s[i].y +(step*j*(s[i+1].y - s[i].y))/dist
                z = s[i].z +(step*j*(s[i+1].z - s[i].z))/dist
                cont_traj.append(Point3D(x,y,z))

    return cont_traj

def FindPoints_for_line(contour: list[Point3D], y: float):
    p1: Point3D
    p2: Point3D
    ps: list[Point3D]
    ps = []
    for i in range(0, len(contour)):
        if((y >= contour[i].y and y <contour[i-1].y or (y >= contour[i-1].y and y <contour[i].y))):
            ps.append(contour[i-1] ) 
            ps.append(contour[i] ) 
    #print(len(ps))
    if(len(ps)>3):
        
        if(ps[0].x<ps[2].x):
            return ps
        else:
            ps2: list[Point3D]
            ps2 = []
            ps2.append(ps[2])
            ps2.append(ps[3])
            ps2.append(ps[0])
            ps2.append(ps[1])
            return ps2
    else:
        return []


def FindCross_for_line(p: list[Point3D] ,y: float):

    x = p[0].x+(p[1].x-p[0].x)*(y-p[0].y)/(p[1].y-p[0].y)
    p1 = Point3D(x,y,0)

    x = p[2].x+(p[3].x-p[2].x)*(y-p[2].y)/(p[3].y-p[2].y)
    p2 = Point3D(x,y,0)
    return p1,p2
            

def GeneratePositionTrajectory(contour: list[Point3D], step: float):
    # нахождение нижней точки
    y_min:float = 10000.
    i_min = 0.
    y_max:float = -10000.
    i_max = 0.
    for i in range(len(contour)):
        if(contour[i].y < y_min):
            y_min = contour[i].y
            i_min = i
        if(contour[i].y>y_max):
            y_max = contour[i].y
            i_max = i
    p_min = contour[i_min]
    p_max = contour[i_max]
    traj = []
    #добавление линии
    y = p_min.y
    flagRL = 0
    while y<p_max.y:
        ps = FindPoints_for_line(contour,y)
        if(len(ps)==4) and flagRL == 0:
            p1,p2 = FindCross_for_line(ps,y)
            traj.append(p2)
            traj.append(p1)
            flagRL =1
        elif(len(ps)==4) and flagRL == 1:
            p1,p2 = FindCross_for_line(ps,y)
            traj.append(p1)
            traj.append(p2)
            flagRL =0
    
        y+=step

    #for i in range(len(traj)):
        #print(str(traj[i].x)+" "+str(traj[i].y)+" "+str(traj[i].z)+" ")
    #добавление точки слева
    return traj

   
def pass_array(array, x_w, y_w):
    row_len = len(array)
    col_len = len(array[0])
    mov_aver_array = empty_ar(row_len, col_len)
    
    for i in range (0,row_len-x_w+1):
        for j in range (0,col_len-y_w+1):
            mov_aver_array[i][j] = eval_aver_array(take_small_window(array, x_w, y_w, i, j))
    return mov_aver_array       


def take_small_window(ar, x_w, y_w, x_st, y_st):
    tiny_arr = empty_ar(x_w, y_w)
    for i in range(0,x_w):
        for j in range(0,y_w):
            tiny_arr[i][j] = ar[i+x_st][j+y_st]
    return tiny_arr
#_________________________________________________________________
# ищет количество столбцов и строк двухмерного массива
def size_of_2dim_array(array):
    return len(array), len(array[0])

def cut_array(array, offset):
    row_len, col_len  = size_of_2dim_array(array) # ищет количество столбцов и строк двухмерного массива
    cutted_array = empty_ar(row_len - 2*offset, col_len - 2*offset) # создаем пустой вырезанный массив
    cutted_row, cutted_col = size_of_2dim_array(cutted_array)
    for i in range (0, cutted_row):
        for j in range(0, cutted_col):
            cutted_array[i][j] = array[i+offset][j+offset]
    return cutted_array 

#нужна для прохождения массива без краёв, которые неизвестны (центр ядра)    
#на вход - массив, размеры окна, возвращает - сглаженный массив
def pass_array_center(array, x_window, y_window):
    row_len, col_len  = size_of_2dim_array(array) #вычисляем размер входного массива
    offset_window_x = int((x_window - 1)/2) # расстояние от центра до края массива (ещё одна характеристика размеров окна)
    offset_window_y = int((y_window - 1)/2)
    mov_aver_array = empty_ar(row_len, col_len) # создаём пустой массив под средние
   
   #заполнение пустого массива средними:
   # начало и конец массива средних относительно несглаженного массива (отнимаем от количества строк и столбцов оффсеты)
   
    for i in range (offset_window_x,row_len-offset_window_x):
        for j in range (offset_window_y,col_len-offset_window_y):
            window = take_small_window_center(array, x_window, y_window, i, j)
            mov_aver_array[i][j] = eval_aver_array(window)
        print("i: "+str(i))
    
    return mov_aver_array      

# взять подмассив с размерами окна и центром в точке x_start, y_start из большого массива
def take_small_window_center(ar, x_window, y_window, x_start, y_start):
    offset_window_x = int((x_window - 1)/2) # расстояние от центра до края массива (ещё одна характеристика размеров окна)
    offset_window_y = int((y_window - 1)/2)
    tiny_arr = empty_ar(x_window, y_window)
    for i in range(0,x_window):
        for j in range(0,y_window):
            tiny_arr[i][j] = ar[i+x_start-offset_window_x][j+y_start-offset_window_y]
    return tiny_arr

# находим среднее арифметическое значений окна
def eval_aver_array(array):
    sum = 0
    for i in range(len(array)):
        for j in range(len(array[i])):
            sum = sum+array[i][j]
    size = len(array)*len(array[0])
    return float(sum)/float(size)

# создание пустого массива
def empty_ar(rows, columns):

    b = columns*[0.]
    ar = rows *[0.]
    for i in range(len(ar)):
        ar[i] = np.array(b)
    return np.array(ar)

# массив заполненный значениями k
def empty_ar_k(rows, columns, k):
    b = columns*[k]
    ar = rows *[k]
    for i in range(len(ar)):
        ar[i] = np.array(b)
    return np.array(ar)

#____________________________________________-



# принимает на вход размер ядра свёртки, возвращает массив координат сгенерированной зашумлённой повверхности, 
def surface(kernelSize:int = 3): 
    # function for Z values
    def f(x, y):
        noise = random.uniform(-5,5)
        vyr = 0.5*(((x**2)/20) - ((y**2)/4))+0.5*x+noise
        return vyr

    # x and y values
    #создаём "случайную" поверхность"
    x = np.linspace(-10, 10, 40) # нижний предел, верхний предел, кол-во - с одинаковым шагом
    y = np.linspace(-10, 10, 40)

    X, Y = np.meshgrid(x, y)
  
    Z = f(X, Y)
    for i in range(len(X)):
        for j in range(len(X[0])):
            Z[i][j] = f(X[i][j], Y[i][j])

   # оффсет это отступ от краёв изначального массива 
   # для получения результирующего (после применения функции скользящего среднего) массива
    offset = int((kernelSize - 1)/2) 
    ar = pass_array_center(Z, kernelSize,kernelSize)
    ax = plt.axes(projection='3d')
    X_cutted = cut_array(X, offset) # удаление невычисленных значений для соблюдения размеров массивов для построения пов-ти
    Y_cutted = cut_array(Y, offset)
    ar_cutted = cut_array(ar, offset)
    Z_cutted = cut_array(Z, offset)
    #print("z0:" + str(Z[0][0]))
    #print("ar_cutted0:" + str(ar_cutted[0][0]))
    #сгенерированная сетка, сглаженная сетка
    return [X,Y,Z],[X_cutted,Y_cutted,ar_cutted]

def arrayViewer(X,Y,Z):
    koords = []
    for i in range(len(X)):
        for j in range(len(X[0])):
            koords.append([X[i][j],Y[i][j],Z[i][j],1])
    return koords

def arrayViewer_GL(X,Y,Z):
    koords:list[Point3D] = []
    for i in range(len(X)):
        for j in range(len(X[0])):
            koords.append(Point3D(X[i][j],Y[i][j],Z[i][j]))
    return koords

def arrayViewer_GL_2d(X,Y,Z,off_y:float = 0.)->list[list[Point3D]]:
    koords:list[list[Point3D]] = []
    print("Z0:" + str(Z[0][0]))
    for i in range(len(X)):
        sub_koords: list[Point3D] = []
        for j in range(len(X[0])):
            sub_koords.append(Point3D(X[i][j],Y[i][j]+off_y,Z[i][j]))
        koords.append(sub_koords)
    return koords

def draw_frame(matr: list[Point3D], windowGL: GLWidget):
    points = createFrame(matr, 1)
    frame1 = Mesh3D( points[0:2] ,PrimitiveType.lines)
    frame2 = Mesh3D( points[2:4],PrimitiveType.lines)
    frame3 = Mesh3D( points[4:6] ,PrimitiveType.lines)

    windowGL.paint_objs.append(Paint_in_GL(0,1,1.0,4,PrimitiveType.lines,frame1))
    windowGL.paint_objs.append(Paint_in_GL(1.0,0,1.0,4,PrimitiveType.lines,frame2))
    windowGL.paint_objs.append(Paint_in_GL(1.0,1,0,4,PrimitiveType.lines,frame3))

def main():
    # позволяет оконному приложени работать (почитать про это)
    app =QtWidgets.QApplication(sys.argv)
    window = GLWidget() # создание графического окна
    
    #koords = arrayViewer_GL(x,y,z)   
    #window.paint_objs.append(Paint_in_GL(0,1,0,2,1,koords,PrimitiveType.lines))

    #orig,smooth1 = surface(3)
    orig,smooth2 = surface(9)
    #из трёх отдельных двухмерных массив создаём общий двухмерный масиив точек
    koords3 = arrayViewer_GL_2d(smooth2[0],smooth2[1],smooth2[2], 0)
    
    #создание объектов из массива координат (расчет нормалей и создание треугольников)
    mesh3=  window.gridToTriangleMesh(koords3)

    cont = GenerateContour(20) 
    traj = GeneratePositionTrajectory(cont,1)
    div_tr = divideTraj(traj,0.3)

    mesh3d_1 = Mesh3D(div_tr,PrimitiveType.lines)
    mesh3d_2 = Mesh3D(mesh3,PrimitiveType.triangles)

    proj_traj,normal_arr = projection(mesh3d_2,  mesh3d_1)
    matrs =  matrix_of_rotation(proj_traj,normal_arr, mesh3d_2)
    for i in range (int(len(matrs)/10)):
        draw_frame(matrs[i*10], window)
    mesh3d_3 = Mesh3D(proj_traj,PrimitiveType.lines)
    window.paint_objs.append(Paint_in_GL(0.5,1,0.5,5,PrimitiveType.lines,mesh3d_3))

  
    #mesh2.save("mesh2")
    #отрисовка объектов
    #window.paint_objs.append(Paint_in_GL(1,0,0,1,PrimitiveType.lines,mesh3d_1))
    window.paint_objs.append(Paint_in_GL(0,1,0,1,PrimitiveType.triangles,mesh3d_2))
    
    window.show()
    sys.exit(app.exec_())
    

if __name__ == "__main__":
    main()

