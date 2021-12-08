import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
import os
import glob
from datetime import datetime, timedelta
from mineData import write_to_csv,write_to_csv_with_average_DMM_and_comments


# Takes batch data for batch sizes less than 30 and compiles it into monthly (30 days) data and stores monthly data in
# csv's outside the working directory
# Make sure data_end_date that is passed in is a naive datetime object
def make_batch_data_monthly(nameOfRepo, batch_size, data_end_date):
    dir_name_for_glob = 'Data/Batch Data/' + nameOfRepo + ' Batches/Batch Size ' + str(batch_size.days) + '/*.csv'
    dir_name_for_monthly_csv = 'Data/Batch Data/' + nameOfRepo + ' Batches/'

    # Don't know if recursive needs to be true for glob. Don't know if files will be sorted when using glob
    # assume recursive = false and glob returns sorted list
    file_list = glob.glob(dir_name_for_glob)
    # Checking if file_list is sorted with print statement
    # print(file_list)
    if not file_list:
        print('No csv files in repos directory')
    # print(len('Data/Batch Data/babylonjs_batch Batches/Batch Size 10\\'))
    #
    # file_dict = pd.read_csv(file_list[0], header=0, index_col = 0).to_dict('index')
    # print(file_dict)

    running_batch_total = 0
    monthly_batch_start_date = 0
    new_monthly_batch = True
    monthly_contributor_dict = {}

    for file in file_list:
        # print('new file: ' + file)

        file_start_date = datetime(int(file[-28:-24]), int(file[-23:-21]), int(file[-20:-18]), 0, 0, 0)
        file_end_date = datetime(int(file[-14:-10]), int(file[-9:-7]), int(file[-6:-4]), 0, 0, 0)
        # Check if file goes backwards in time, skip if so
        if (file_end_date - file_start_date).days < 0:
            continue
            # os.remove('Data/Batch Data/' + nameOfRepo + ' Batches/Batch Size ' + str(batch_size.days) + '/' + file)

        if new_monthly_batch:
            monthly_batch_start_date = file_start_date
            monthly_contributor_dict = {}
            monthly_email_to_name_dict = {}
            new_monthly_batch = False

        file_dict = pd.read_csv(file, header=0, index_col = 0).to_dict('index')

        for name in file_dict:
            # labels and productivity = 0 until writing to csv
            email = file_dict[name]['emails']
            churn = file_dict[name]['churn']
            num_commits = file_dict[name]['num commits']
            first_commit = file_dict[name]['first commit']
            last_commit = file_dict[name]['last commit']
            num_owned_files = file_dict[name]['num owned files']
            dmm_comp_sum = file_dict[name]['sum of dmm complexities']
            commits_with_dmm = file_dict[name]['commits with dmm complexity present']
            comments = file_dict[name]['num comments added/removed']
            # Person could have diff name but same email, if so put data in for the name thats already in the dict
            # Handling above later
            # if name is in dict, but email isnt, treat as new dev
            # and email not in monthly_email_to_name_dict
            if name not in monthly_contributor_dict:
                monthly_contributor_dict[name] = [email, 0, 0, churn, num_commits, first_commit, last_commit, 0, 0,
                                                  num_owned_files, dmm_comp_sum, commits_with_dmm, comments, 0, 0]
            else:
                monthly_contributor_dict[name][3] += churn
                monthly_contributor_dict[name][4] += num_commits
                monthly_contributor_dict[name][6] = last_commit
                monthly_contributor_dict[name][9] += num_owned_files
                monthly_contributor_dict[name][10] += dmm_comp_sum
                monthly_contributor_dict[name][11] += commits_with_dmm
                monthly_contributor_dict[name][12] += comments

        # print(monthly_contributor_dict)
        # if running_batch_total == 30 or (file_end_date - data_end_date).days == 0
        # put data in a monthly csv, outside of current directory
        # if file_end_date is greater than or equal to data_end_date
        # or
        # the difference between file_end_date and monthly_batch_start_date is greater than or equal to 30 days
        # put data in a monthly csv, outside of current directory, calculate productivity and labels
        # set new_monthly_batch = True
        # set monthly_contributor_dict = {}
        # print(str((file_end_date - monthly_batch_start_date).days))
        if not file_end_date < data_end_date or (file_end_date - monthly_batch_start_date).days >= 30:
            # Put data in csv
            # print('Making new csv')
            filename = dir_name_for_monthly_csv + monthly_batch_start_date.strftime("%Y-%m-%d") + ' to ' \
                       + file_end_date.strftime("%Y-%m-%d") + '.csv'

            # Calculate productivity and labels
            total_monthly_churn_prod = 0
            total_monthly_commit_prod = 0
            for name in monthly_contributor_dict:
                churn = monthly_contributor_dict[name][3]
                commits = monthly_contributor_dict[name][4]
                first = datetime.strptime(monthly_contributor_dict[name][5], "%Y-%m-%d %H:%M:%S")
                last = datetime.strptime(monthly_contributor_dict[name][6], "%Y-%m-%d %H:%M:%S")
                tenure = abs((last - first).days) / 7
                churn_prod = 0
                commit_prod = 0
                if tenure != 0:
                    churn_prod = churn / tenure
                    commit_prod = commits / tenure
                monthly_contributor_dict[name][7] = churn_prod
                monthly_contributor_dict[name][8] = commit_prod
                total_monthly_churn_prod += churn_prod
                total_monthly_commit_prod += commit_prod
                # Calculate average DMM and average commits
                averageComments = 0
                if monthly_contributor_dict[name][4] != 0:
                    averageComments = monthly_contributor_dict[name][12] / monthly_contributor_dict[name][4]
                averageDMM = 0
                if monthly_contributor_dict[name][11] != 0:
                    averageDMM = monthly_contributor_dict[name][10] / monthly_contributor_dict[name][11]
                monthly_contributor_dict[name][13] = averageDMM
                monthly_contributor_dict[name][14] = averageComments
            # NOW LABEL THE 10x ENGINEERS
            average_churn_prod = -1
            average_commit_prod = -1
            if len(monthly_contributor_dict) != 0:
                average_churn_prod = total_monthly_churn_prod / len(monthly_contributor_dict)
                average_commit_prod = total_monthly_commit_prod / len(monthly_contributor_dict)

            for name in monthly_contributor_dict:
                if monthly_contributor_dict[name][7] >= 10*average_churn_prod:
                    monthly_contributor_dict[name][1] = 1
                if monthly_contributor_dict[name][8] >= 10*average_commit_prod:
                    monthly_contributor_dict[name][2] = 1

            # print(filename)
            write_to_csv_with_average_DMM_and_comments(monthly_contributor_dict, filename)
            new_monthly_batch = True


def make_total_data_from_monthly(nameOfRepo, filename):

    dir_of_monthly_data = 'Data/Batch Data/' + nameOfRepo + ' Batches/*.csv'
    file_list = glob.glob(dir_of_monthly_data)
    # Checking if file_list is sorted with print statement
    # print(file_list)
    if not file_list:
        print('No csv files in repos directory')

    total_contrib_dict = {}

    for file in file_list:
        file_dict = pd.read_csv(file, header=0, index_col=0).to_dict('index')

        for name in file_dict:
            # labels and productivity = 0 until writing to csv
            email = file_dict[name]['emails']
            churn = file_dict[name]['churn']
            num_commits = file_dict[name]['num commits']
            first_commit = file_dict[name]['first commit']
            last_commit = file_dict[name]['last commit']
            num_owned_files = file_dict[name]['num owned files']
            dmm_comp_sum = file_dict[name]['sum of dmm complexities']
            commits_with_dmm = file_dict[name]['commits with dmm complexity present']
            comments = file_dict[name]['num comments added/removed']

            if name not in total_contrib_dict:
                total_contrib_dict[name] = [email, 0, 0, churn, num_commits, first_commit, last_commit, 0, 0,
                                                  num_owned_files, dmm_comp_sum, commits_with_dmm, comments, 0, 0]
            else:
                total_contrib_dict[name][3] += churn
                total_contrib_dict[name][4] += num_commits
                total_contrib_dict[name][6] = last_commit
                total_contrib_dict[name][9] += num_owned_files
                total_contrib_dict[name][10] += dmm_comp_sum
                total_contrib_dict[name][11] += commits_with_dmm
                total_contrib_dict[name][12] += comments

    # Calculate productivity and labels
    total_monthly_churn_prod = 0
    total_monthly_commit_prod = 0
    for name in total_contrib_dict:
        churn = total_contrib_dict[name][3]
        commits = total_contrib_dict[name][4]
        first = datetime.strptime(total_contrib_dict[name][5], "%Y-%m-%d %H:%M:%S")
        last = datetime.strptime(total_contrib_dict[name][6], "%Y-%m-%d %H:%M:%S")
        tenure = abs((last - first).days) / 7
        churn_prod = 0
        commit_prod = 0
        if tenure != 0:
            churn_prod = churn / tenure
            commit_prod = commits / tenure
        total_contrib_dict[name][7] = churn_prod
        total_contrib_dict[name][8] = commit_prod
        total_monthly_churn_prod += churn_prod
        total_monthly_commit_prod += commit_prod
        # Calculate average DMM and average commits
        averageComments = 0
        if total_contrib_dict[name][4] != 0:
            averageComments = total_contrib_dict[name][12]/total_contrib_dict[name][4]
        averageDMM = 0
        if total_contrib_dict[name][11] != 0:
            averageDMM = total_contrib_dict[name][10]/total_contrib_dict[name][11]
        total_contrib_dict[name][13] = averageDMM
        total_contrib_dict[name][14] = averageComments


    # NOW LABEL THE 10x ENGINEERS
    average_churn_prod = -1
    average_commit_prod = -1
    if len(total_contrib_dict) != 0:
        average_churn_prod = total_monthly_churn_prod / len(total_contrib_dict)
        average_commit_prod = total_monthly_commit_prod / len(total_contrib_dict)

    for name in total_contrib_dict:
        if total_contrib_dict[name][7] >= 10 * average_churn_prod:
            total_contrib_dict[name][1] = 1
        if total_contrib_dict[name][8] >= 10 * average_commit_prod:
            total_contrib_dict[name][2] = 1

    path = 'Data/' + filename
    write_to_csv_with_average_DMM_and_comments(total_contrib_dict, path)


# Read in all data
# pydrillerData = pd.read_csv('pydrillerData.csv', encoding = "ISO-8859-1")
# threejsData = pd.read_csv('threejsData.csv', encoding = "ISO-8859-1")
# webGLData = pd.read_csv('webGLData.csv', encoding = "ISO-8859-1")
# velocityData = pd.read_csv('velocityData.csv', encoding = "ISO-8859-1")
# toolkitData = pd.read_csv('toolkitData.csv', encoding = "ISO-8859-1")
#
# df = pd.concat([pydrillerData, threejsData, webGLData, velocityData, toolkitData])
#
# # We are simply concatenating all of our data, not filtering at all other than for DMM complexity
# # We are not even looking to see if a name is used multiple times in the data
# # In the future we need to only do the analysis on similar projects ie just graphics libraries
# # Also determine how we are filtering out any extraneous data
# # Also need to look at a 10x engineers contributions across projects and see if their label holds
#
# Does simple linear regression on some independent and dependent variables
def simple_linear_regression(X, y):
    XX = X.to_numpy().reshape(-1, 1)
    ols = sm.OLS(y, X).fit()
    return ols, ols.summary()

# # --------------------- Linear regression on ownership ---------------------
# X = df["num owned files"]
# y = df["10x label churn"]
# X = sm.add_constant(X)
# ols, summary = simple_linear_regression(X, y)
# print(summary)
#
# # plt.rc('figure', figsize=(8, 4.5))
# # plt.text(0.01, 0.05, str(summary), {'fontsize': 10}, fontproperties = 'monospace') # approach improved by OP -> monospace!
# # plt.axis('off')
# # plt.tight_layout()
# # plt.savefig('ownershipSummary.png')
#
# # --------------------- Linear regression on DMM ---------------------
# df_ = df[["average DMM complexity", "10x label churn"]].dropna()
#
# X = df_["average DMM complexity"]
# y = df_["10x label churn"]
# X = sm.add_constant(X)
# ols, summary = simple_linear_regression(X, y)
# print(summary)
#
# plt.rc('figure', figsize=(8, 4.5))
# plt.text(0.01, 0.05, str(summary), {'fontsize': 10}, fontproperties = 'monospace') # approach improved by OP -> monospace!
# plt.axis('off')
# plt.tight_layout()
# plt.savefig('dmmSummary.png')
#
# # --------------------- Linear regression on comments ---------------------
# X = df["average comments added"]
# y = df["10x label churn"]
# X = sm.add_constant(X)
# ols, summary = simple_linear_regression(X, y)
# print(summary)
#
# # plt.rc('figure', figsize=(8, 4.5))
# # plt.text(0.01, 0.05, str(summary), {'fontsize': 10}, fontproperties = 'monospace') # approach improved by OP -> monospace!
# # plt.axis('off')
# # plt.tight_layout()
# # plt.savefig('commentsSummary.png')
#
# # --------------------- Trying Multiple regression ---------------------
# X = []
# for index, row in df.iterrows():
#     if not pd.isnull(row['average DMM complexity']):
#         X.append([row['num owned files'], row['average DMM complexity'], row['average comments added']])
#
# # X = df_[['num owned files', 'average DMM complexity', 'average comments added']]
# # y = df_["10x label churn"]
# # X = sm.add_constant(X)
# #
# # ols = sm.OLS(y, X).fit()
# # print(ols.summary())