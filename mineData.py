from pydriller import *
from pydriller.metrics.process.contributors_experience import ContributorsExperience
from datetime import datetime, timedelta
import lizard
from lizard_languages.python import PythonReader
from lizard_languages.javascript import JavaScriptReader
import sys
import numpy as np
import statsmodels.api as sm
import csv
import os

# pip install numpy
# pip install statsmodels

# sys.setrecursionlimit(10000)

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
            files[filepath][author] = files[filepath].get(author, 0) + \
                                      lines_authored

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

# batch_size is a timeDelta
def mine_in_batches(path_to_repo, language, start_date, end_date, nameOfRepo, batch_size):
    # end on the first of a month, start on first of a month
    if start_date >= end_date:
        print('Start date is later than or the same as end date')

    # Make the directory if it doesn't exist
    dir_name = 'Data/Batch Data/' + nameOfRepo + ' Batches'
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)

    batch_start_date = start_date
    batch_end_date = start_date + batch_size    
    while batch_start_date < end_date:
        if end_date < batch_end_date:
            batch_end_date = end_date
        # print('Batch start: ' + batch_start_date.strftime("%m-%d-%Y"))
        # print('Batch end: ' + batch_end_date.strftime("%m-%d-%Y"))
        cur_batch_repo = Repository(path_to_repo, since=batch_start_date, to=batch_end_date)
        csv_filename = dir_name + '/' + nameOfRepo + ' ' + batch_start_date.strftime("%Y-%m-%d") + ' to ' + \
                       batch_end_date.strftime("%Y-%m-%d") + '.csv'

        mine_repo(cur_batch_repo, language, csv_filename)

        batch_start_date += batch_size
        batch_end_date += batch_size


# Function that mines a repo thats written in either Python or JavaScript and puts this data in a csv with given filename
def mine_repo(repo, language, filename):
    # keep track of number of comments added: Need this so we can find average number of comments added per
    # commit for each contributor
    # Keep track of cyclomatic complexity of changed methods
    # Keep track of number of owned files

    contributorDict = {}

    # dicts to get ownership
    renamed_files = {}
    files = {}
    emailToName = {}

    # commitCount = 0

    # contributor dict takes name as key:
    # [[emails], 10x label churn, 10x label commits, churn, number of commits, date of first commit, date of last commit, churn productivity, commit productivity, number of owned files,
    # sum of contributors DMM complexities, number of commits where there is a DMM complexity, number of comments added/removed]

    for commit in repo.traverse_commits():
        # print('Commit #: ', commitCount)
        # commitCount += 1
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
                if language == 'JavaScript':
                    commentCountPost = get_num_comments_javascript(source_code)
                elif language == 'Python':
                    commentCountPost = get_num_comments_python(source_code)
                else:
                    print('NOT USING JAVASCRIPT OR PYTHON TO GET COMMENTS')
            if source_code_before:
                if language == 'JavaScript':
                    commentCountPre = get_num_comments_javascript(source_code_before)
                elif language == 'Python':
                    commentCountPre = get_num_comments_python(source_code_before)
                else:
                    print('NOT USING JAVASCRIPT OR PYTHON TO GET COMMENTS')

            commentsAdded = commentCountPost - commentCountPre
            totalCommentsAddedThisCommit += commentsAdded
        contributorDict[name][12] += totalCommentsAddedThisCommit

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
    # print('Done getting data from repo')
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
            productivityChurn = churn / tenure
            productivityCommit = commits / tenure
        contributorDict[name][7] = productivityChurn
        contributorDict[name][8] = productivityCommit

    prodChurnTotal = 0
    prodCommitTotal = 0
    # Calculate average productivity
    for values in contributorDict.values():
        prodChurnTotal += values[7]
        prodCommitTotal += values[8]

    prodChurnAve = -1
    prodCommitAve = -1
    if len(contributorDict) != 0:
        prodChurnAve = prodChurnTotal / len(contributorDict)
        prodCommitAve = prodCommitTotal / len(contributorDict)

    # Now we label who is a 10x engineer as those who have a productivity metric 10x greater than the average
    # I have it where we make an entirely new dict, just add it to contributor dict
    label_10x_engineers_churn(contributorDict, prodChurnAve)
    label_10x_engineers_commits(contributorDict, prodCommitAve)



    write_to_csv(contributorDict, filename)

# Writes data from dataToBePutInCSV dict, to a csv file with given filename
def write_to_csv(contributorDict, filename):
    print()
    print('Writing data to CSV')
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

    with open(filename, 'w+', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(csvDict)
