
# coding: utf-8

# In[1]:


import pandas as pd
import math  
from itertools import product
from sys import stdout as out
from mip import Model, xsum, minimize, BINARY, OptimizationStatus
import numpy as np


# In[2]:


def calculateDistance(x1, y1, x2, y2):
    dist = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return dist

def circle_line_segment_intersection(circle_center, circle_radius, pt1, pt2):
    A, B, C, r = pt1, pt2, circle_center, circle_radius

    # Each vector as a complex number.
    OA = complex(*A)
    OB = complex(*B)
    OC = complex(*C)

    # Now let's translate into a coordinate system where A is the origin
    AB = OB - OA
    AC = OC - OA

    # if either A or B is actually in the circle,  then mark it as a detection
    BC = OC - OB
    if abs(BC) < r or abs(AC) < r: return True

    # Project C onto the line to find P, the point on the line that is closest to the circle centre
    AB_normalized = AB / abs(AB)
    AP_distance = AC.real * AB_normalized.real + AC.imag * AB_normalized.imag  # dot product (scalar result)
    AP = AP_distance * AB_normalized  # actual position of P relative to A (vector result)

    # If AB intersects the circle, and neither A nor B itself is in the circle,
    # then P, the point on the extended line that is closest to the circle centre, must be...

    # (1) ...within the segment AB:
    AP_proportion = AP_distance / abs(AB)  # scalar value: how far along AB is P?
    in_segment = 0 <= AP_proportion <= 1

    # ...and (2) within the circle:
    CP = AP - AC
    in_circle = abs(CP) < r

    detected = in_circle and in_segment
    return detected


def storm_check(ax, ay, bx, by, cx, cy, cr):
    storm_arr = circle_line_segment_intersection((cx, cy), cr, (ax, ay), (bx, by))
    if not storm_arr:
        return False
    return True


# In[3]:

def main():
    spreadsheet_file = pd.ExcelFile('data.xlsx')
    worksheets = spreadsheet_file.sheet_names

    print("all the worksheets " , worksheets)


    # In[4]:


    island_coordinates = []
    storm_coordinates_radius = []
    road_material = {}
    materialToCost = {"Asphalt" : 100 , "Concrete" : 65 , "Gravel" : 35}
    road_time = {}
    time_matrix = []

    print("extracting data...")

    locationDF = pd.read_excel('data.xlsx' , sheet_name = "Locations" , header = None, skiprows=1)
    for index,row  in locationDF.iterrows():
        # print("++" ,type(row[1]))
        island_coordinates.append( (row[1], row[2]) )


    stormDF = pd.read_excel('data.xlsx' , sheet_name = "Storms" , header = None, skiprows=2)
    for index,row  in stormDF.iterrows():
        storm_coordinates_radius.append( (row[0], row[1], row[2]) )




    roadMaterialDF = pd.read_excel('data.xlsx' , sheet_name = "Road Material" , header = None, skiprows=1)
    for index,row in roadMaterialDF.iterrows():
        key = f'{row[0]} {row[1]}'
        value = row[2]
        road_material[key] = value

    print("extracting data is done.")


    # In[5]:


    print(island_coordinates)
    print(len(island_coordinates))


    # In[6]:


    print(storm_coordinates_radius)
    print(len(storm_coordinates_radius))


    # In[7]:


    print("\npreprocessing...")

    for i in range(len(island_coordinates)):
        time_matrix.append([])
        for j in range(len(island_coordinates)):
            if i == j:
                time_matrix[i].append(0)
            else:
                island1 = island_coordinates[i]
                island2 = island_coordinates[j]
                distance = calculateDistance(island1[0], island1[1], island2[0], island2[1])
                roadType = road_material[f'{i + 1} {j + 1}']
                time_matrix[i].append(distance / materialToCost[roadType])

    #print(time_matrix)



    dists = []
    for i in range(len(island_coordinates)):
        dists.append([])
        for j in range(i + 1, len(island_coordinates)):
                island1 = island_coordinates[i]
                island2 = island_coordinates[j]
                distance = calculateDistance(island1[0], island1[1], island2[0], island2[1])
                roadType = road_material[f'{i + 1} {j + 1}']
                dists[i].append(distance / materialToCost[roadType])


    storms = []
    for i in range(len(island_coordinates)):
        storms.append([])
        for j in range(len(island_coordinates)):
            island1 = island_coordinates[i]
            island2 = island_coordinates[j]
            is_stormy = False
            for k in range(len(storm_coordinates_radius)):
                if i == j:
                    storms[i].append(0)
                    break

                else:
                    island1 = island_coordinates[i]
                    island2 = island_coordinates[j]
                    stormInfo = storm_coordinates_radius[k]
                    cx, cy, cradius = stormInfo[0], stormInfo[1], stormInfo[2]

                    if storm_check(island1[0], island1[1], island2[0], island2[1], cx, cy, cradius):
                        # print("--- Storm #", k + 1, " found between island ", i + 1, " and island ", j + 1)
                        is_stormy = True
                        storms[i].append(0)
                        break

            if i != j and not is_stormy:
                storms[i].append(1)

    print(storms)
    print("preprocessing is done.")


    print(storms)
    print("preprocessing is done.")


    # In[8]:


    places = [f'island {i}' for i in range(1,31)]

    n, V = len(dists), set(range(len(dists)))


    model = Model()

    # binary variables indicating if arc (i,j) is used on the route or not
    x = [[model.add_var(var_type=BINARY) for j in V] for i in V]

    # continuous variable to prevent subtours: each city will have a
    # different sequential id in the planned route except the first one
    y = [model.add_var() for i in V]


    # objective function: minimize the distance
    model.objective = minimize(xsum(time_matrix[i][j]*x[i][j] for i in V for j in V))

    # constraint : leave each city only once
    for i in V:
        model += xsum(x[i][j] for j in V - {i}) == 1

    # constraint : enter each city only once
    for i in V:
        model += xsum(x[j][i] for j in V - {i}) == 1

    # constraint : storm
    for i in V:
         for j in V:
             model += (x[i][j]*storms[i][j] == x[i][j])


    # subtour elimination
    for (i, j) in product(V - {0}, V - {0}):
        if i != j:
            model += y[i] - (n+1)*x[i][j] >= y[j]-n


    # optimizing
    status = model.optimize(max_seconds=6000)
    if status == OptimizationStatus.OPTIMAL:
        print('optimal solution cost {} found'.format(model.objective_value))
    elif status == OptimizationStatus.FEASIBLE:
        print('sol.cost {} found, best possible: {}'.format(model.objective_value, model.objective_bound))
    elif status == OptimizationStatus.NO_SOLUTION_FOUND:
        print('no feasible solution found, lower bound is: {}'.format(model.objective_bound))
    if status == OptimizationStatus.OPTIMAL or status == OptimizationStatus.FEASIBLE:
        print('solution:')
        for v in model.vars:
           if abs(v.x) > 1e-6: # only printing non-zeros
              print('{} : {}'.format(v.name, v.x))

    # In[17]:


    # checking if a solution was found
    if model.num_solutions:
        out.write('route with total distance %g found: %s'
                  % (model.objective_value, places[0]))
        path = places[0]
        nc = 0
        while True:
            nc = [i for i in V if x[nc][i].x >= 0.99][0]
            out.write(' -> %s' % places[nc])

            path = path + ' -> %s' % places[nc]

            if nc == 0:
                break
        out.write('\n')


        arr = np.array(x)
        arr = arr.astype(str)


        file = open("data.txt", "w")
        file.write(path + "\n")
        file.write(str(model.objective_value))
        file.write("\n")

        for i in range(len(arr)):
            line = ""
            for j in range(len(arr[i])):
                line = line + str(x[i][j].x)
                if j != len(arr[i]) - 1:
                    line = line + ","

            file.write(line + "\n")
        file.close()

    else:
        print("no solution")

if __name__ == '__main__':
    main()
