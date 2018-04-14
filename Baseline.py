from gurobipy import *
from DataPrep import *


__author__ = "Abdulelah Alshehri"
__email__ = "asaalshehr@gmail.com"


'''Model Start'''
Base = Model()

'''Model Variables'''
# Regular Production Time required (hrs/qtr)
RT = {}
# Overtime Production Time required (hrs/qtr)
OT = {}
for i in range(1, PlantSet + 1):
    for n in range(1, ProductSet + 1):
        for t in range(1, tSet + 1):
            RT[(i, n, t)] = Base.addVar(lb=0, vtype=GRB.CONTINUOUS, name="RT%d,%d,%d" % (i, n, t))

for i in range(1, PlantSet + 1):
    for n in range(1, ProductSet + 1):
        for t in range(1, tSet + 1):
            OT[(i, n, t)] = Base.addVar(lb=0, vtype=GRB.INTEGER, name="OT%d,%d,%d" % (i, n, t))

# X=Flow of product n from plant i to customer j for each time period t ( in tons)
X = {}
for i in range(1, PlantSet + 1):
    for j in range(1, CustomerSet + 1):
        for n in range(1, ProductSet + 1):
            for t in range(1, tSet + 1):
                X[(i, j, n, t)] = Base.addVar(lb=0, vtype=GRB.CONTINUOUS, name="X%d,%d,%d,%d" % (i, j, n, t))

"""Objective"""
# Set objective (min production costs)
Base.setObjective(sum((RT[i, n, t] + alpha * OT[i, n, t]) * PC[i, n] * PR[i - 1]
                      for i in range(1, PlantSet + 1)
                      for n in range(1, ProductSet + 1)
                      for t in range(1, tSet + 1)) + BSC, GRB.MINIMIZE)

'''Constraint 1: Supply-Demand Balance '''
for j in range(1, CustomerSet + 1):
    for n in range(1, ProductSet + 1):
        for t in range(1, tSet + 1):
            Base.addConstr(sum(X[i, j, n, t] for i in range(1, PlantSet + 1)) == Dqjn[j, n])

'''Constraint 2: Production at a node = Flow out of a node'''
# (Balance on plant i) Production = Flow out
for i in range(1, PlantSet + 1):
    for n in range(1, ProductSet + 1):
        for t in range(1, tSet + 1):
            Base.addConstr((RT[i, n, t] + OT[i, n, t]) * Iin[i - 1, n - 1] * PR[i - 1] ==
                           sum(X[i, j, n, t] for j in range(1, CustomerSet + 1)))

'''Constraint 3: Production at a node i does not exceed its capacity'''
for i in range(1, PlantSet + 1):
    for n in range(1, ProductSet + 1):
        for t in range(1, tSet + 1):
            Base.addConstr((RT[i, n, t] + OT[i, n, t]) * Iin[i - 1, n - 1] * PR[i - 1] <= QC[i, n])

'''Constraint 4: Maximum Regular Time Production Capacity'''
for i in range(1, PlantSet + 1):
    for t in range(1, tSet + 1):
        Base.addConstr(sum(RT[i, n, t] for n in range(1, ProductSet + 1)) <= MxRT -
                       sum(Switch[n - 1, k - 1, i - 1, t - 1] * Snk[n, k]
                           for n in range(1, ProductSet + 1)
                           for k in range(1, ProductSet + 1)))

'''Constraint 5: Maximum Overtime Production Capacity'''
for i in range(1, PlantSet + 1):
    for t in range(1, tSet + 1):
        Base.addConstr(sum(OT[i, n, t] for n in range(1, ProductSet + 1)) <= MxOT)
'''Solve'''
Base.optimize()

'''Export solution'''
RTi = [];RTn = [];RTt = [];RTsoln = []
for i in range(1, PlantSet + 1):
    for n in range(1, ProductSet + 1):
        for t in range(1, tSet + 1):
            RTsoln.append(RT[(i, n, t)].x);RTi.append(i);RTn.append(n);RTt.append(t)

OTi = [];OTn = [];OTt = [];
OTsoln = []
for i in range(1, PlantSet + 1):
    for n in range(1, ProductSet + 1):
        for t in range(1, tSet + 1):
            OTsoln.append(OT[(i, n, t)].x);OTi.append(i);OTn.append(n);OTt.append(t);

xsoln = [];xi = [];xj = [];xn = [];xt = [];
for i in range(1, PlantSet + 1):
    for j in range(1, CustomerSet + 1):
        for n in range(1, ProductSet + 1):
            for t in range(1, tSet + 1):
                xsoln.append(X[(i, j, n, t)].x);xi.append(i);xj.append(j);xn.append(n);xt.append(t);
# Change format to Dataframe
RTdf = pd.DataFrame(np.column_stack([RTi, RTn, RTt, RTsoln]),
                    columns=['Plant ID', 'Product ID', 'Time Period', 'Regular Time (hr)'])
OTdf = pd.DataFrame(np.column_stack([OTi, OTn, OTt, OTsoln]),
                    columns=['Plant ID', 'Product ID', 'Time Period', 'Overtime (hr)'])
Xdf = pd.DataFrame(np.column_stack([xi, xj, xn, xt, xsoln]),
                   columns=['Plant ID', 'Customer ID', 'Product ID', 'Time Period', 'Demand Satisfied at end of t (ton)'])
objv = pd.DataFrame({"objVal": Base.objVal}.items(), columns=['', 'Objective value ($/year)'])
# Define file
writer = pd.ExcelWriter('Baseline Solution.xlsx', engine='xlsxwriter')
# Write & save
objv.to_excel(writer, 'Objective', index=False);RTdf.to_excel(writer, 'Regular Time', index=False);
OTdf.to_excel(writer, 'Overtime', index=False);Xdf.to_excel(writer, 'Demand Satisfied ', index=False);
writer.save()