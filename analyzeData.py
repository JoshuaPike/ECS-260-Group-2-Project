import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
import os
import glob
from datetime import datetime, timedelta

def make_batch_data_monthly(nameOfRepo, batch_size, data_end_date):
    dir_name = 'Data/Batch Data/' + nameOfRepo + ' Batches/Batch Size ' + str(batch_size.days) + '/*.csv'
    # Don't know if recursive needs to be true for glob. Don't know if files will be sorted when using glob
    # assume recursive = false and glob returns sorted list
    file_list = glob.glob(dir_name)
    if not file_list:
        print('No csv files in repos directory')

    # file could be empty
    # Example file name: 2016-11-20 to 2016-12-20.csv
    running_batch_total = 0
    for file in file_list:
        file_start_date = datetime(int(file[0:4]), int(file[5:7]), int(file[8:10]), 0, 0, 0)
        file_end_date = datetime(int(file[0:4]), int(file[5:7]), int(file[8:10]), 0, 0, 0)



        # if running_batch_total == 30 or (file_end_date - data_end_date).days == 0
        # put data in a monthly csv, outside of current directory

# Read in all data
pydrillerData = pd.read_csv('pydrillerData.csv', encoding = "ISO-8859-1")
threejsData = pd.read_csv('threejsData.csv', encoding = "ISO-8859-1")
webGLData = pd.read_csv('webGLData.csv', encoding = "ISO-8859-1")
velocityData = pd.read_csv('velocityData.csv', encoding = "ISO-8859-1")
toolkitData = pd.read_csv('toolkitData.csv', encoding = "ISO-8859-1")

df = pd.concat([pydrillerData, threejsData, webGLData, velocityData, toolkitData])

# We are simply concatenating all of our data, not filtering at all other than for DMM complexity
# We are not even looking to see if a name is used multiple times in the data
# In the future we need to only do the analysis on similar projects ie just graphics libraries
# Also determine how we are filtering out any extraneous data
# Also need to look at a 10x engineers contributions across projects and see if their label holds

# Does simple linear regression on some independent and dependent variables
def simple_linear_regression(X, y):
    XX = X.to_numpy().reshape(-1, 1)
    ols = sm.OLS(y, X).fit()
    return ols, ols.summary()

# --------------------- Linear regression on ownership ---------------------
X = df["num owned files"]
y = df["10x label churn"]
X = sm.add_constant(X)
ols, summary = simple_linear_regression(X, y)
print(summary)

# plt.rc('figure', figsize=(8, 4.5))
# plt.text(0.01, 0.05, str(summary), {'fontsize': 10}, fontproperties = 'monospace') # approach improved by OP -> monospace!
# plt.axis('off')
# plt.tight_layout()
# plt.savefig('ownershipSummary.png')

# --------------------- Linear regression on DMM ---------------------
df_ = df[["average DMM complexity", "10x label churn"]].dropna()

X = df_["average DMM complexity"]
y = df_["10x label churn"]
X = sm.add_constant(X)
ols, summary = simple_linear_regression(X, y)
print(summary)

plt.rc('figure', figsize=(8, 4.5))
plt.text(0.01, 0.05, str(summary), {'fontsize': 10}, fontproperties = 'monospace') # approach improved by OP -> monospace!
plt.axis('off')
plt.tight_layout()
plt.savefig('dmmSummary.png')

# --------------------- Linear regression on comments ---------------------
X = df["average comments added"]
y = df["10x label churn"]
X = sm.add_constant(X)
ols, summary = simple_linear_regression(X, y)
print(summary)

# plt.rc('figure', figsize=(8, 4.5))
# plt.text(0.01, 0.05, str(summary), {'fontsize': 10}, fontproperties = 'monospace') # approach improved by OP -> monospace!
# plt.axis('off')
# plt.tight_layout()
# plt.savefig('commentsSummary.png')

# --------------------- Trying Multiple regression ---------------------
X = []
for index, row in df.iterrows():
    if not pd.isnull(row['average DMM complexity']):
        X.append([row['num owned files'], row['average DMM complexity'], row['average comments added']])

# X = df_[['num owned files', 'average DMM complexity', 'average comments added']]
# y = df_["10x label churn"]
# X = sm.add_constant(X)
#
# ols = sm.OLS(y, X).fit()
# print(ols.summary())