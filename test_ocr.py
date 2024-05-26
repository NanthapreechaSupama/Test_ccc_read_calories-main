import easyocr
import numpy as np
def dist(p,q):
    return ((p[0]-q[0])**2 + (p[1]-q[1])**2)**0.5

def dist_x(p,q):
    return (((p[0]-q[0])*4)**2 + (p[1]-q[1])**2)**0.5
reader = easyocr.Reader(['th','en']) # this needs to run only once to load the model into memory
result = reader.readtext('images/ced0389bbacb884a9557fa20f0a49d8b.jpg')
points=[]
for d in result:
    x, y = (d[0][0][0]+d[0][2][0])/2, (d[0][0][1]+d[0][2][1])/2
    points.append([[x,y],d[1]])
pairs=[]
used_points=[]
for n in range(len(points)):
    print(points[n])
    short=1000
    temp=[]
    for i in range(len(points)-1):
        for j in range(i+1,len(points)):
            if i in used_points or j in used_points:
                continue
            if dist(points[i][0],points[j][0])<short:
                short=dist(points[i][0],points[j][0])
                temp=[i,j]
    if temp!=[]:
        used_points.append(temp[0])
        used_points.append(temp[1])
        pairs.append([temp,short])
#print(pairs)
for p in pairs:
    print(points[p[0][0]][1],"=",points[p[0][1]][1])
    