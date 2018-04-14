import pandas as pd
import numpy as np

__author__ = "Abdulelah Alshehri"
__email__ = "asaalshehr@gmail.com"

# Define file to read
xlf = 'Network Planning Data.xlsx'
# Read Data
Plants = pd.read_excel(xlf, sheet_name='Plants')
Customers = pd.read_excel(xlf, sheet_name='Customers')
Product = pd.read_excel(xlf, sheet_name='Product')
AnnualDemand = pd.read_excel(xlf, sheet_name='Annual Demand')
ProductionCapacity = pd.read_excel(xlf, sheet_name='Production Capacity')
DistancesP2C = pd.read_excel(xlf, sheet_name='DistancesP2C')
DistancesC2C = pd.read_excel(xlf, sheet_name='DistancesC2C')
Setups = pd.read_excel(xlf, sheet_name='Setupsedited')
PPlc = pd.read_excel(xlf, sheet_name='Production Totals')

'''Scalars from problem statement'''
# Overtime Production Cost (+50%)
alpha = 1.5  # factor
# setup cost ($/Day)
SC = 5000  # $/day
# Max Regular Production Time (hrs/qtr) (240 hrs/month)
MxRT = 720  # hr/QTR
# Max Overtime Production Time (hrs/qtr) (120 hrs/month)
MxOT = 360  # hr/QTR
# Daily Working Time (hrs/day
WR = 8
# Max Truck Load
MTL = 10  # tons/truck
# Shipping Cost
Ship = 2.0  # $/truck/mile
# Number of Plants i
PlantSet = 4;
# Number of customers j
CustomerSet = 50;
# Number of products n
ProductSet = 5;
# Time set t (quarters)
tSet = 4
# Number of candidate warehouses w
WHSet = 50
# Plant i production rate
PR = np.array([100, 50, 50, 50])  # tons/hour
# At least 80% of the demand within 500 miles
Cov = 0.8
