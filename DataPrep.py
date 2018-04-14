from ReadAllData import *
import math

__author__ = "Abdulelah Alshehri"
__email__ = "asaalshehr@gmail.com"

'''Reading from data frames'''
par1, par2, par3=Setups['Product ID From'].tolist(),Setups['Product ID To'].tolist(), Setups['Days'].tolist()
#Create a dictionary for Setup Cost in days
SDnk=dict(zip(zip(map(int, par1), map(int, par2)),map(int,par3)))
#0-1 Matrix for Prodcut n switching to k in t
Switch=np.zeros(shape=(5,5,4,4))
# Product 4 switches to 5 in periods 1 and 2
Switch[3,4,3,0]=1;Switch[3,4,3,2]=1
# Product 5 switches to 4 in periods 1 and 2
Switch[4,3,3,1]=1;Switch[4,3,3,3]=1


#Base Case Total Setup Costs (SC*Total days)
BSC= SC* sum(Switch[n-1,k-1,i-1,t-1]*SDnk[n,k] for n in range(1, ProductSet+1)  for k in range(1, ProductSet + 1) for i in range(1, PlantSet+1)for t in range(1, tSet+1))
#Product n produced in plant i matrix (n,i)
Iin =np.zeros(shape=(4,5))
Iin[0,0]=1;Iin[1,1]=1; Iin[2,2]=1;Iin[3,3]=1; Iin[3,4]=1;

#Exrtact: Production cost of product n ($/ton)
par1, par2,par3=ProductionCapacity['Plant ID'].tolist(),ProductionCapacity['Product ID'].tolist(), ProductionCapacity['Production Cost'].tolist()
#Create a dictionary
PC=dict(zip(zip(map(int, par1), map(int, par2)),map(float,par3)))

#Exrtact: Demand (tons/QTR) for each product
par1, par2, pard= AnnualDemand['Product ID'].tolist(), AnnualDemand['Customer ID'].tolist(), AnnualDemand['Demand (in tonnes)'].tolist()
#Create a dictionary
Dem=dict(zip(zip(map(int, par1), map(int, par2)),map(float,pard)))
ADem=np.asarray(pard)
#Initialize list
PDem=[]
for i in range(1,ProductSet+1):
    PDem.append(sum(Dem[i, j] for j in range(1,51)))
#Quarterly demand
QD=np.asarray(PDem)/4
QDi=[QD[0], QD[1],QD[2],QD[3]+QD[4]]

#Exrtact Capcity of each plant in tons/QTR
par1, par2, par3= ProductionCapacity['Plant ID'].tolist(), ProductionCapacity['Product ID'].tolist(), ProductionCapacity['Annual Production Capacity'].tolist()
par3= np.array(par3)/4
#Capcity /Q
QC=dict(zip(zip(map(int, par1), map(int, par2)),map(float,par3)))

#Distance from plant i to customer j
par1, par2, par3= DistancesP2C['Plant Id'].tolist(), DistancesP2C['Customer ID'].tolist(), DistancesP2C['Distance'].tolist()
Distpc=dict(zip(zip(map(int, par1), map(int, par2)),map(float,par3)))

#Distance
par1, par2, par3= DistancesC2C['Customer ID'].tolist(), DistancesC2C['Customer ID2'].tolist(), DistancesC2C['Distance'].tolist()
Dist=dict(zip(zip(map(int, par1), map(int, par2)),map(float,par3)))

#Construct activity matrix checking if ditance between customers<500
Ia=np.zeros(shape=(50,50))

for i in range(1,WHSet+1):
    for j in range (1, CustomerSet+1):
        if Dist[i,j]<500: #miles
            Ia[i-1,j-1]=1
        else:
            Ia[i-1, j-1] = 0
Iwj={}
for w in range(1,WHSet+1):
    for j in range (1, CustomerSet+1):
        Iwj[w,j]=Ia[w-1, j-1]

#Demand of product n from customer j
par1, par2, par3= AnnualDemand['Product ID'].tolist(), AnnualDemand['Customer ID'].tolist(), AnnualDemand['Demand (in tonnes)'].tolist()
Djn=dict(zip(zip(map(int, par2), map(int, par1)),map(float,par3)))
par4=np.asarray(par3)/tSet
Dqjn=dict(zip(zip(map(int, par2), map(int, par1)),map(float,par4)))

TD=sum(np.asarray(Djn.values()))

#Demand of product n from customer j
par1, par2, par3= PPlc['Plant ID'].tolist(), PPlc['Product ID'].tolist(), PPlc['Total Demand'].tolist()
PDin=dict(zip(zip(map(int, par1), map(int, par2)),map(float,par3)))

# product, plant(n,i)
In = np.array([[295488.7398, 0, 0, 0],
               [0, 72580.1424, 0, 0],
               [0, 0, 29797.447, 0],
               [0, 0, 0, 11922.0901],
               [0, 0, 0, 5940.2655]])

par1, par2, par3=Setups['Product ID From'].tolist(),Setups['Product ID To'].tolist(), Setups['Hours'].tolist()
#Create a dictionary for setups
Snk=dict(zip(zip(map(int, par1), map(int, par2)),map(int,par3)))