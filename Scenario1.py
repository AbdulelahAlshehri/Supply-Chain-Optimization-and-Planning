from gurobipy import *
import math
from DataPrep import *

__author__ = "Abdulelah Alshehri"
__email__ = "asaalshehr@gmail.com"

'''Model Start'''
S1 = Model()
S1.Params.MIPGap = 10 ** -6

'''Model Variables'''
# y=Build warehouse or not
y = {}
for w in range(1, WHSet + 1):
    y[(w)] = S1.addVar(lb=0, vtype=GRB.BINARY, name="Y%d" % (w))
# Z=Flow of product n from warehouse w to customer j (tons/year)
Z = {}
for w in range(1, WHSet + 1):
    for j in range(1, CustomerSet + 1):
        for n in range(1, ProductSet + 1):
            Z[(w, j, n)] = S1.addVar(lb=0, vtype=GRB.CONTINUOUS, name="Z%d,%d,%d" % (w, j, n))
# X=Flow of product n from plant i to warehouse w (tons/year)
X = {}
for i in range(1, PlantSet + 1):
    for w in range(1, WHSet + 1):
        for n in range(1, ProductSet + 1):
            X[(i, w, n)] = S1.addVar(lb=0, vtype=GRB.CONTINUOUS, name="X%d,%d,%d" % (i, w, n))
"""Objective"""
# Minimize # of warehouses
S1.setObjective(sum(y[w] for w in range(1, WHSet + 1)), GRB.MINIMIZE)

'''Constraint:At least 80% of the demand must be satisfied by a facility within 500 miles of the customer'''
S1.addConstr(sum(Iwj[w, j] * Z[(w, j, n)] for j in range(1, CustomerSet + 1)
                 for n in range(1, ProductSet + 1)
                 for w in range(1, WHSet + 1)) >= Cov * TD)

''' Constraint: Supply-Demand Balance'''
for j in range(1, CustomerSet + 1):
    for n in range(1, ProductSet + 1):
        S1.addConstr(sum(Z[w, j, n] for w in range(1, WHSet + 1)) == Djn[j, n])

''' Constraint: Balance on Warehouses .. OUT = IN'''
for w in range(1, WHSet + 1):
    for n in range(1, ProductSet + 1):
        S1.addConstr(sum(Z[w, j, n] for j in range(1, CustomerSet + 1))
                     == sum(X[i, w, n] for i in range(1, PlantSet + 1)))

'''(Balance on plants) Flow out = Production'''
for n in range(1, ProductSet + 1):
    for i in range(1, PlantSet + 1):
        S1.addConstr(sum(X[i, w, n] for w in range(1, CustomerSet + 1)) == In[n - 1, i - 1])

# M (large enough ~ close to total demand)
M = 10 ** 6
''' Constraint 3: Big-M: a warehouse can only ship/receive products if it is built'''
for w in range(1, WHSet + 1):
    for i in range(1, PlantSet + 1):
        for j in range(1, CustomerSet + 1):
            S1.addConstr(sum(Z[w, j, n] for n in range(1, ProductSet + 1)) <= M * y[w])

''' Constraint 4: If a warehouse is built in customer j location, it ships products to customer j
(in case two warehouses are located within 500 miles of each other)'''
for w in range(1, WHSet + 1):
    for n in range(1, ProductSet + 1):
        for i in range(1, PlantSet + 1):
            S1.addConstr(Z[w, w, n] >= y[w] * Djn[w, n])

'''Solve'''
S1.optimize()

'''Calculate transportation Costs to warehouses and average miles traveled'''
# Number of trucks required
Tiwn = {}

# Transportation costs from plants to warehouses and average miles traveled by ton
TCpc = sum(Ship * Distpc[i, w] * tSet * math.ceil((X[(i, w, n)].x / tSet) / MTL) for w in range(1, WHSet + 1)
           for i in range(1, PlantSet + 1)
           for n in range(1, ProductSet + 1))

# Transportation costs from warehouses to customers
TCcc = sum(Ship * Dist[w, j] * tSet * math.ceil((Z[(w, j, n)].x / tSet) / MTL) for w in range(1, WHSet + 1)
           for j in range(1, CustomerSet + 1)
           for i in range(1, PlantSet + 1)
           for n in range(1, ProductSet + 1))
# Average miles traveled by a ton
Avgtrav = (sum(Distpc[i, w] * X[(i, w, n)].x for w in range(1, WHSet + 1)
               for i in range(1, PlantSet + 1)
               for n in range(1, ProductSet + 1)) +
           sum(Dist[w, j] * Z[(w, j, n)].x
               for w in range(1, WHSet + 1)
               for j in range(1, CustomerSet + 1)
               for i in range(1, PlantSet + 1)
               for n in range(1, ProductSet + 1))) / TD

# Total transportation cost
TCS1 = TCpc + TCcc

# Percentage of demand  fulfilled by a warehouse within 500 miles
Coverage = (sum(sum(Iwj[w, j] * Z[(w, j, n)].x for j in range(1, CustomerSet + 1)
                    for w in range(1, WHSet + 1)) for n in range(1, ProductSet + 1))) / TD
# Warehouses list
Wlist = []
for i in range(1, WHSet + 1):
    if y[(i)].x == 1:
        Wlist.append(i)

'''Export solution'''

ysoln = {}
for w in range(1, WHSet + 1):
    ysoln[(w)] = y[(w)].x

# Create solution lists
xi = [];xw = [];xn = [];xsoln = []
for i in range(1, PlantSet + 1):
    for w in range(1, WHSet + 1):
        for n in range(1, ProductSet + 1):
            xsoln.append(X[(i, w, n)].x);xi.append(i);xw.append(w);xn.append(n)

zw = [];zj = [];zn = [];zsoln = []
for w in range(1, WHSet + 1):
    for j in range(1, CustomerSet + 1):
        for n in range(1, ProductSet + 1):
            zsoln.append(Z[(w, j, n)].x);zw.append(w);zj.append(j);zn.append(n);

# Stack lists into dataframes
xdf = pd.DataFrame(np.column_stack([xi, xw, xn, xsoln]),
                   columns=['Plant ID', 'Warehouse ID', 'Product ID', 'Shipment (ton)'])
zdf = pd.DataFrame(np.column_stack([zw, zj, zn, zsoln]),
                   columns=['Warehouse ID', 'Customer ID', 'Product ID', 'Shipment Size (ton)'])
ydf = pd.DataFrame(ysoln.items(), columns=['Y_w', 'Level(Binary)'])
Tcdf = pd.DataFrame(np.column_stack([TCpc, TCcc, TCS1, Coverage]),
                    columns=['To warehouses', 'To customers', 'Total', 'Coverage'])

# Define file
writer = pd.ExcelWriter('Scenario 1 Solution.xlsx', engine='xlsxwriter')
# Write & save
Tcdf.to_excel(writer, 'Costs & coverage', index=False);
ydf.to_excel(writer, 'Warehouse Assignment', index=False);
xdf.to_excel(writer, 'Flow to Warehouses', index=False);
zdf.to_excel(writer, 'Flow to Customers', index=False)
writer.save()
