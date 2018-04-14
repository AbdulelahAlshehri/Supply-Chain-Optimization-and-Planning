from DataPrep import *
from ReadAllData import *
from gurobipy import *

__author__ = "Abdulelah Alshehri"
__email__ = "asaalshehr@gmail.com"

'''Model Start'''
S2 = Model()
S2.Params.MIPGap = 10 ** -8

'''Model Variables'''
# Regular Production Time required (hrs/qtr)
RT = {}
# Overtime Production Time required (hrs/qtr)
OT = {}
for i in range(1, PlantSet + 1):
    for n in range(1, ProductSet + 1):
        for t in range(1, tSet + 1):
            RT[(i, n, t)] = S2.addVar(lb=0, vtype=GRB.CONTINUOUS, name="RT%d,%d,%d" % (i, n, t))

for i in range(1, PlantSet + 1):
    for n in range(1, ProductSet + 1):
        for t in range(1, tSet + 1):
            OT[(i, n, t)] = S2.addVar(lb=0, vtype=GRB.INTEGER, name="OT%d,%d, %d" % (i, n, t))

# Flow of product n from plant i to customer j for each time period t ( in tons)
X = {}
for i in range(1, PlantSet + 1):
    for j in range(1, CustomerSet + 1):
        for n in range(1, ProductSet + 1):
            for t in range(1, tSet + 1):
                X[(i, j, n, t)] = S2.addVar(lb=0, vtype=GRB.CONTINUOUS, name="X%d,%d,%d,%d" % (i, j, n, t))

# Whether to a changeover from n to k is selected
YS = {}
for n in range(1, ProductSet + 1):
    for k in range(1, ProductSet + 1):
        for i in range(1, PlantSet + 1):
            YS[(n, k, i)] = S2.addVar(lb=0, vtype=GRB.BINARY, name="YS%d,%d, %d" % (n, k, i))
uni = {}
for n in range(1, ProductSet + 1):
    for i in range(1, PlantSet + 1):
        uni[(n, i)] = S2.addVar(lb=2, ub=5, vtype=GRB.CONTINUOUS, name="uni%d, %d" % (n, i))

# Setup Costs
S2SC = S2.addVar(lb=0, vtype=GRB.CONTINUOUS, name="S2SC")

S2MC = S2.addVar(lb=0, vtype=GRB.CONTINUOUS, name="S2MC")

# Prdocution costs
S2TC = S2.addVar(lb=0, vtype=GRB.CONTINUOUS, name="S2TC")

"""Objective"""
S2.setObjective(S2TC + S2MC + S2SC, GRB.MINIMIZE)

"""Objective Components"""
# Manufacturing Costs
S2.addConstr(S2MC == sum((RT[i, n, t] + alpha * OT[i, n, t]) * PC[i, n] * PR[i - 1] for i in range(1, PlantSet + 1)
                         for n in range(1, ProductSet + 1)
                         for t in range(1, tSet + 1)))
# Setup costs
S2.addConstr(S2SC == 4 * sum(SC * sum(YS[n, k, i] * SDnk[n, k]
                                      for n in range(1, ProductSet + 1)
                                      for k in range(1, ProductSet + 1))
                             for i in range(1, PlantSet + 1)))
# Transportation costs
S2.addConstr(S2TC == sum(0.2 * Distpc[i, j] * X[i, j, n, t] for j in range(1, CustomerSet + 1)
                         for i in range(1, PlantSet + 1)
                         for n in range(1, ProductSet + 1)
                         for t in range(1, tSet + 1)))

'''Constraint: Supply-Demand Balance '''
for j in range(1, CustomerSet + 1):
    for n in range(1, ProductSet + 1):
        for t in range(1, tSet + 1):
            S2.addConstr(sum(X[i, j, n, t] for i in range(1, PlantSet + 1)) == Dqjn[j, n])

'''Constraint: Production at a node = Flow out of a node'''
for i in range(1, PlantSet + 1):
    for n in range(1, ProductSet + 1):
        for t in range(1, tSet + 1):
            S2.addConstr(
                (RT[i, n, t] + OT[i, n, t]) * PR[i - 1] == sum(X[i, j, n, t] for j in range(1, CustomerSet + 1)))

'''Constraint: Production at a node i does not exceed its capacity'''
for i in range(1, PlantSet + 1):
    for n in range(1, ProductSet + 1):
        for t in range(1, tSet + 1):
            S2.addConstr((RT[i, n, t] + OT[i, n, t]) * PR[i - 1] <= QC[i, n])

'''Constraint: Maximum Regular Time Production Capacity'''
for i in range(1, PlantSet + 1):
    for t in range(1, tSet + 1):
        S2.addConstr(sum(RT[i, n, t] + sum(YS[n, k, i] * Snk[n, k] for k in range(1, ProductSet + 1))
                         for n in range(1, ProductSet + 1)) <= MxRT)

'''Constraint: Maximum Overtime Production Capacity'''
for i in range(1, PlantSet + 1):
    for t in range(1, tSet + 1):
        S2.addConstr(sum(OT[i, n, t] for n in range(1, ProductSet + 1)) <= MxOT)

'''Constraint: Exactly  one predecessor for each changeover'''
for n in range(1, ProductSet + 1):
    for i in range(1, PlantSet + 1):
        S2.addConstr(sum(YS[n, k, i] for k in range(1, ProductSet + 1)) == 1)

'''Constraint: Exactly one successor for each changeover'''
for k in range(1, ProductSet + 1):
    for i in range(1, PlantSet + 1):
        S2.addConstr(sum(YS[n, k, i] for n in range(1, ProductSet + 1)) == 1)

'''Constraint: Flow preservation/ subtour elimination'''
for i in range(1, PlantSet + 1):
    for k in range(1, ProductSet + 1):
        for n in range(1, ProductSet + 1):
            S2.addConstr(uni[n, i] - uni[k, i] + 5 * YS[n, k, i] <= 5)

''' Constraint: Logic cut constraint'''
for k in range(1, ProductSet + 1):
    for n in range(1, ProductSet + 1):
        for i in range(1, PlantSet + 1):
            for l in range(1, ProductSet + 1):
                S2.addConstr(uni[l, i] >= 1 + YS[n, k, i] + YS[k, l, i] - YS[1, k, i])

'''Constraint: n != k'''
for n in range(1, ProductSet + 1):
    for i in range(1, PlantSet + 1):
        S2.addConstr(YS[n, n, i] == 0)


'''Solve'''
S2.optimize()
'''Export solution'''

RTi = [];RTn = [];RTt = [];RTsoln = []
for i in range(1, PlantSet + 1):
    for n in range(1, ProductSet + 1):
        for t in range(1, tSet + 1):
            RTsoln.append(RT[(i, n, t)].x);RTi.append(i);RTn.append(n);RTt.append(t);

OTi = [];OTn = [];OTt = [];OTsoln = [];
for i in range(1, PlantSet + 1):
    for n in range(1, ProductSet + 1):
        for t in range(1, tSet + 1):
            OTsoln.append(OT[(i, n, t)].x);OTi.append(i);OTn.append(n);OTt.append(t);

xsoln = [];xi = [];xj = [];xt = [];xn = [];
for i in range(1, PlantSet + 1):
    for j in range(1, CustomerSet + 1):
        for n in range(1, ProductSet + 1):
            for t in range(1, tSet + 1):
                xsoln.append(X[(i, j, n, t)].x);xi.append(i);xj.append(j);xn.append(n);xt.append(t);

ysoln = [];yn = [];yk = [];yi = [];
for n in range(1, ProductSet + 1):
    for k in range(1, ProductSet + 1):
        for i in range(1, PlantSet + 1):
            ysoln.append(YS[(n, k, i)].x);yn.append(n);yk.append(k);yi.append(i);

# Change format to Dataframe
RTdf = pd.DataFrame(np.column_stack([RTi, RTn, RTt, RTsoln]),
                    columns=['Plant ID', 'Product ID', 'Time Period', 'Regular Time (hr)'])
OTdf = pd.DataFrame(np.column_stack([OTi, OTn, OTt, OTsoln]),
                    columns=['Plant ID', 'Product ID', 'Time Period', 'Overtime (hr)'])
Xdf = pd.DataFrame(np.column_stack([xi, xj, xn, xt, xsoln]),
                   columns=['Plant ID', 'Customer ID', 'Product ID', 'Time Period',
                            'Demand Satisfied at end of t (ton)'])
objv = pd.DataFrame({"objVal": S2.objVal}.items(), columns=['', 'Objective value ($/year)'])

YSdf = pd.DataFrame(np.column_stack([yn, yk, yi, ysoln]),
                    columns=['Product From ID', 'Product To ID', 'Plant ID', 'Value (Binary)'])
# Define file
writer = pd.ExcelWriter('Scenario 2 Solution.xlsx', engine='xlsxwriter')
# Write & save
objv.to_excel(writer, 'Objective', index=False);
RTdf.to_excel(writer, 'Regular Time', index=False)
OTdf.to_excel(writer, 'Overtime', index=False);
Xdf.to_excel(writer, 'Demand Satisfied ', index=False);
YSdf.to_excel(writer, 'Changeovers', index=False);
writer.save()
