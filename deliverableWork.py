from pydriller import *
from pydriller.metrics.process.contributors_experience import ContributorsExperience
from datetime import datetime
import lizard
from lizard_languages.python import PythonReader
from lizard_languages.javascript import JavaScriptReader
import sys
import numpy as np
import statsmodels.api as sm
import csv
import matplotlib.pyplot as plt

# pip install numpy
# pip install statsmodels

sys.setrecursionlimit(100000)

# Returns number of comments from source code, works for python repos only
def get_num_comments_python(source_code):
    comCount = 0
    tokens = PythonReader.generate_tokens(source_code)

    for token in tokens:
        if len(token) > 1 and token[0] == '#':
            comCount += 1
    return comCount

# Returns number of comments from source code, works for javascript repos only
def get_num_comments_javascript(source_code):
    comCount = 0
    tokens = JavaScriptReader.generate_tokens(source_code)

    for token in tokens:
        if len(token) > 2 and token[0] == '/' and token[1] == '/':
            comCount += 1
    return comCount

# Returns dictionary of [post, pre] complexities, keys are method names
# If pre complexity is -1 that means it was a new method
def get_pre_and_post_complexities(modified_file):
    complexDict = {}
    for changed_method in modified_file.changed_methods:
        complexDict[changed_method.long_name] = [changed_method.complexity, -1]

    for old_method in modified_file.methods_before:
        if old_method.long_name in complexDict:
            complexDict[old_method.long_name][1] = old_method.complexity
    return complexDict


# For a given repo, returns a dictionary of {path: [owner name, percent of file owned]}
def get_file_owners(repo):
    renamed_files = {}
    files = {}
    emailToNameDict = {}
    for commit in repo.traverse_commits():
        for modified_file in commit.modified_files:

            filepath = renamed_files.get(modified_file.new_path,
                                         modified_file.new_path)

            if modified_file.change_type == ModificationType.RENAME:
                renamed_files[modified_file.old_path] = filepath

            author = commit.author.email.strip()
            emailToNameDict[author] = commit.author.name
            lines_authored = modified_file.added_lines + modified_file.deleted_lines

            files[filepath] = files.get(filepath, {})
            files[filepath][author] = files[filepath].get(author, 0) + lines_authored

    for path, contributions in list(files.items()):
        owner = emailToNameDict[max(contributions, key=contributions.get)]
        total = sum(contributions.values())
        if total == 0:
            del files[path]
        else:
            files[path] = [owner, round(100 * max(contributions.values()) / total, 2)]
    return files


# Calculates the number of files a contributor owns and stores in dict {name, number of files owned}
# Input is the output of get_file_owners
def calc_num_owned_files(files):
    numOwnedFiles = {}
    for values in files.values():
        if values[0] not in numOwnedFiles:
            numOwnedFiles[values[0]] = 1
        else:
            numOwnedFiles[values[0]] += 1
    return numOwnedFiles


# Takes in the contributor dictionary and average churn productivity and returns a dict, name is key, value is 0 if not 10x, 1 if is 10x
def label_10x_engineers_churn(contribDict, aveProd):
    for contributor in contribDict:
        if contribDict[contributor][7] >= 10*aveProd:
            contribDict[contributor][1] = 1

def label_10x_engineers_commits(contribDict, aveProd):
    for contributor in contribDict:
        if contribDict[contributor][8] >= 10*aveProd:
            contribDict[contributor][2] = 1

url = ['https://github.com/ishepard/pydriller.git', 'https://github.com/terryyin/lizard',
       'https://github.com/BabylonJS/Babylon.js', 'https://github.com/mrdoob/three.js',
       'https://github.com/KhronosGroup/WebGL']

localPaths = ['../three.js', '../WebGL', '../velocity', '../toolkit']

# branch = ['dev']
# Third date is for WebGL
dates = [datetime(2017, 3, 17, 0, 0, 0), datetime(2017, 3, 18, 0, 0, 0), datetime(2017, 7, 10, 0, 0, 0)]
# dt1 = datetime(2021, 1, 1, 0, 0, 0)
# dt2 = datetime(2021, 11, 5, 0, 0, 0)

# curRepo = Repository(url[3], since=dt1, to=dt2)
# curRepo = Repository(localPaths[1], since=dates[2], to=dates[1])
curRepo = Repository(localPaths[2], since=dates[0], to=dates[2])

# keep track of number of comments added: Need this so we can find average number of comments added per
# commit for each contributor
# Keep track of cyclomatic complexity of changed methods
# Keep track of number of owned files

contributorDict = {}

# dicts to get ownership
renamed_files = {}
files = {}
emailToName = {}

commitCount = 0

# contributor dict takes name as key:
# [[emails], 10x label churn, 10x label commits, churn, number of commits, date of first commit, date of last commit, churn productivity, commit productivity, number of owned files,
# sum of contributors DMM complexities, number of commits where there is a DMM complexity, number of comments added/removed]

for commit in curRepo.traverse_commits():
    print('Commit #: ', commitCount)
    commitCount+=1
    name = commit.author.name
    email = commit.author.email.strip()
    lines = commit.lines
    commitTime = commit.committer_date.strftime("%m/%d/%Y")

    if email not in emailToName:
        emailToName[email] = name

    if name not in contributorDict:
        contributorDict[name] = [[email], 0, 0, lines, 1, commitTime, commitTime, 0, 0, 0, 0, 0, 0]
    else:
        contributorDict[name][3] += lines
        contributorDict[name][4] += 1
        contributorDict[name][6] = commitTime
    if email not in contributorDict[name][0]:
        contributorDict[name][0].append(email)

    # print('Done with contributorDict')
    dmmComp = commit.dmm_unit_complexity
    if dmmComp:
        contributorDict[name][10] += dmmComp
        contributorDict[name][11] += 1

    totalCommentsAddedThisCommit = 0
    for modified_file in commit.modified_files:
        # Ownership
        filepath = renamed_files.get(modified_file.new_path,
                                     modified_file.new_path)

        if modified_file.change_type == ModificationType.RENAME:
            renamed_files[modified_file.old_path] = filepath

        lines_authored = modified_file.added_lines + modified_file.deleted_lines

        files[filepath] = files.get(filepath, {})
        files[filepath][email] = files[filepath].get(email, 0) + lines_authored

        # Get comments, only looking at javascript right now
        source_code = modified_file.source_code
        source_code_before = modified_file.source_code_before
        commentCountPre = 0
        commentCountPost = 0
        if source_code:
            commentCountPost = get_num_comments_javascript(source_code)
        if source_code_before:
            commentCountPre = get_num_comments_javascript(source_code_before)

        commentsAdded = commentCountPost - commentCountPre
        totalCommentsAddedThisCommit += commentsAdded
    contributorDict[name][12] += totalCommentsAddedThisCommit

print('Done getting data from repo')

# Put num of owned files in contributor dict
for path, contributions in list(files.items()):
    owner = max(contributions, key=contributions.get)
    total = sum(contributions.values())
    if total == 0:
        del files[path]
    else:
        # add one owned file to contributor dict
        contributorDict[emailToName[owner]][9] += 1

totalChurn = 0
totalCommits = 0
for name in contributorDict:
    churn = contributorDict[name][3]
    commits = contributorDict[name][4]
    totalChurn += churn
    totalCommits += commits
    first = datetime.strptime(contributorDict[name][5], "%m/%d/%Y")
    last = datetime.strptime(contributorDict[name][6], "%m/%d/%Y")
    tenure = abs((last - first).days) / 7
    productivityChurn = 0
    productivityCommit = 0
    if tenure != 0:
        productivityChurn = churn/tenure
        productivityCommit = commits/tenure
    contributorDict[name][7] = productivityChurn
    contributorDict[name][8] = productivityCommit

prodChurnTotal = 0
prodCommitTotal = 0
# Calculate average productivity
for values in contributorDict.values():
    prodChurnTotal += values[7]
    prodCommitTotal += values[8]
prodChurnAve = prodChurnTotal / len(contributorDict)
prodCommitAve = prodCommitTotal / len(contributorDict)

# Now we label who is a 10x engineer as those who have a productivity metric 10x greater than the average
# I have it where we make an entirely new dict, just add it to contributor dict
label_10x_engineers_churn(contributorDict, prodChurnAve)
label_10x_engineers_commits(contributorDict, prodCommitAve)

# print('Contributor Dict: ', contributorDict)

fields = ['name', 'emails', '10x label churn', '10x label commits', 'churn', 'num commits', 'first commit',
          'last commit', 'churn productivity', 'commit productivity', 'num owned files', 'sum of dmm complexities',
          'commits with dmm complexity present', 'num comments added/removed']

csvDict = []

for name in contributorDict:
    csvDict.append({'name': name,
                    'emails': '#'.join(contributorDict[name][0]),
                    '10x label churn': contributorDict[name][1],
                    '10x label commits': contributorDict[name][2],
                    'churn': contributorDict[name][3],
                    'num commits': contributorDict[name][4],
                    'first commit': contributorDict[name][5],
                    'last commit': contributorDict[name][6],
                    'churn productivity': contributorDict[name][7],
                    'commit productivity': contributorDict[name][8],
                    'num owned files': contributorDict[name][9],
                    'sum of dmm complexities': contributorDict[name][10],
                    'commits with dmm complexity present': contributorDict[name][11],
                    'num comments added/removed': contributorDict[name][12]})

# print(csvDict)
with open('Data/Date Tests/dateTestTotalSecond.csv', 'w+', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fields)
    writer.writeheader()
    writer.writerows(csvDict)