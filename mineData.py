from pydriller import *
from pydriller.metrics.process.contributors_experience import ContributorsExperience
<<<<<<< HEAD
from datetime import datetime, timedelta
=======
from datetime import datetime
>>>>>>> a23ff0db1a99e46fcb9f9fc68734156e6eddef64
import lizard
from lizard_languages.python import PythonReader
from lizard_languages.javascript import JavaScriptReader
import sys
import numpy as np
import statsmodels.api as sm
import csv
<<<<<<< HEAD
import os
import logging
=======
>>>>>>> a23ff0db1a99e46fcb9f9fc68734156e6eddef64

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
<<<<<<< HEAD
def label_10x_engineers_churn(contribDict, aveProd):
    for contributor in contribDict:
        if contribDict[contributor][7] >= 10*aveProd:
            contribDict[contributor][1] = 1

def label_10x_engineers_commits(contribDict, aveProd):
    for contributor in contribDict:
        if contribDict[contributor][8] >= 10*aveProd:
            contribDict[contributor][2] = 1


def mine(repoPath, lang, start, end, repoName, batchSize):
    most_recent_date = start
    most_recent_hash = -1
    commits_to_skip = []
    # batch_size is a timeDelta
    # tzinfo.utcoffset to get utc time for aware datetime objects
    # datetime.utcoffset()

    def mine_in_batches(path_to_repo, language, start_date, end_date, nameOfRepo, batch_size):
        nonlocal most_recent_hash, most_recent_date, commits_to_skip
        # end on the first of a month, start on first of a month
        if not (start_date < end_date):
            print('Start date is later than or the same as end date')
            return

        # Make the directory if it doesn't exist
        dir_name = 'Data/Batch Data/' + nameOfRepo + ' Batches/'
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)
        dir_name = 'Data/Batch Data/' + nameOfRepo + ' Batches/Batch Size ' + str(batch_size.days)
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)

        # log_filename = dir_name + '/' + nameOfRepo +'.log'
        # logging.basicConfig(filename=log_filename, encoding='utf-8', level=logging.ERROR)

        batch_start_date = start_date
        batch_end_date = start_date + batch_size
        most_recent_date = start_date
        while batch_start_date < end_date:
            if end_date < batch_end_date:
                batch_end_date = end_date
            # print('Batch start: ' + batch_start_date.strftime("%m-%d-%Y"))
            # print('Batch end: ' + batch_end_date.strftime("%m-%d-%Y"))
            cur_batch_repo = Repository(path_to_repo, since=batch_start_date, to=batch_end_date)
            csv_filename = dir_name + '/' + batch_start_date.strftime("%Y-%m-%d") + ' to ' + \
                           batch_end_date.strftime("%Y-%m-%d") + '.csv'

            # mineStartTime = datetime.utcnow()
            try:
                mine_repo(cur_batch_repo, language, csv_filename)
                batch_start_date = batch_end_date
                batch_end_date += batch_size
            except Exception as e:
                # if str(e) == 'maximum recursion depth exceeded while calling a Python object':
                #     print('ballsack')
                commits_to_skip.append(most_recent_hash)
                print('Exception Caught')
                # print('Pre mine most recent date: ' + most_recent_date.strftime("%Y-%m-%d %H:%M:%S"))
                # time_of_error = datetime.utcnow()
                # timeElapsed = time_of_error - mineStartTime
                # logging.error('Ran into error while trying to mine batch: ' + batch_start_date.strftime("%Y-%m-%d") +
                #               ' to ' + batch_end_date.strftime("%Y-%m-%d") + '\nError Type: ' + str(e) +
                #               '\nMining took ' + str(timeElapsed.seconds) + ' seconds\n')
                cur_batch_repo = Repository(path_to_repo, since=batch_start_date, to=most_recent_date)
                csv_filename = dir_name + '/' + batch_start_date.strftime("%Y-%m-%d") + ' to ' + \
                               most_recent_date.strftime("%Y-%m-%d") + '.csv'
                batch_start_date = most_recent_date
                mine_repo(cur_batch_repo, language, csv_filename)
                # print('Post mine most recent date: ' + most_recent_date.strftime("%Y-%m-%d %H:%M:%S"))

    # Function that mines a repo thats written in either Python or JavaScript and puts this data in a csv with given filename
    def mine_repo(repo, language, filename):
        nonlocal most_recent_hash, most_recent_date, commits_to_skip
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

        for commit in repo.traverse_commits():
            # print('Commit #: ', commitCount)
            # commitCount += 1
            most_recent_hash = commit.hash
            # print(most_recent_hash)
            if most_recent_hash in commits_to_skip:
                print('Skipping commit with hash: ' + str(most_recent_hash))
                continue
            name = commit.author.name
            email = commit.author.email.strip()
            lines = commit.lines
            most_recent_date = commit.committer_date
            utc_offset = most_recent_date.utcoffset()
            # print(str(most_recent_date))
            commitTime = (most_recent_date + utc_offset).strftime("%Y-%m-%d %H:%M:%S")
            # print(commitTime)
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
                fileType = modified_file.filename[-2:]
                if language == 'JavaScript' and fileType != 'js':
                    continue
                if language == 'Python' and fileType != 'py':
                    continue
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
            first = datetime.strptime(contributorDict[name][5], "%Y-%m-%d %H:%M:%S")
            last = datetime.strptime(contributorDict[name][6], "%Y-%m-%d %H:%M:%S")
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

    mine_in_batches(repoPath, lang, start, end, repoName, batchSize)

# Writes data from dataToBePutInCSV dict, to a csv file with given filename
def write_to_csv(contributorDict, filename):
    # print()
    # print('Writing data to CSV')
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
=======
def label_10x_engineers_churn(contribDict, aveChurnProd):
    tenTimesDict = {}
    for contributor in contribDict:
        if contribDict[contributor][4] >= 10*aveChurnProd:
            tenTimesDict[contributor] = 1
        else:
            tenTimesDict[contributor] = 0
    return tenTimesDict


# Takes in the contributor dictionary and average commit productivity and returns a dict, name is key, value is 0 if not 10x, 1 if is 10x
def label_10x_engineers_commits(contribDict, aveCommitProd):
    tenTimesDict = {}
    for contributor in contribDict:
        if contribDict[contributor][5] >= 10 * aveCommitProd:
            tenTimesDict[contributor] = 1
        else:
            tenTimesDict[contributor] = 0
    return tenTimesDict

# Function that mines a repo thats written in either Python or JavaScript and puts this data in a csv with given filename
def mine_repo(repo, language, filename):
    # keep track of number of comments added: Need this so we can find average number of comments added per
    # commit for each contributor
    # Keep track of cyclomatic complexity of changed methods
    # Keep track of number of owned files

    # Uses name as key gives back [churn, num of commits, first commit, last commit, Churn productivity, Commit productivity]
    contributorDict = {}

    # Uses name as key gives back [[old complexity, new complexity]]
    complexityDict = {}

    # Uses name as key gives back list of the DMM complexity for each of their commits
    dmmComplexityDict = {}

    # Uses name as key gives back list of # of comments added for each commit
    commentDict = {}

    # Uses name as key gives back number of owned files
    ownerDict = calc_num_owned_files(get_file_owners(repo))

    commitCount = 0
    for commit in repo.traverse_commits():
        print(f'Number of commits traversed: ', commitCount)

        commitCount += 1
        name = commit.author.name
        lines = commit.lines
        commitTime = commit.committer_date.strftime("%m/%d/%Y")
        if name not in contributorDict:
            contributorDict[name] = [lines, 1, commitTime,
                                     commitTime]
        else:
            contributorDict[name][0] += lines
            contributorDict[name][1] += 1
            contributorDict[name][3] = commitTime
        # print('Done with contributorDict')
        dmmComp = commit.dmm_unit_complexity
        if dmmComp:
            if name not in dmmComplexityDict:
                dmmComplexityDict[name] = [dmmComp]
            else:
                dmmComplexityDict[name].append(dmmComp)
        # print('Done with dmmComplexityDict')
        totalCommentsAddedThisCommit = 0
        for modified_file in commit.modified_files:
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

            # complexities = get_pre_and_post_complexities(modified_file)
            # for c in complexities:
            #     if name not in complexityDict:
            #         complexityDict[name] = [complexities[c]]
            #     else:
            #         complexityDict[name].append(complexities[c])
        if name not in commentDict:
            commentDict[name] = [totalCommentsAddedThisCommit]
        else:
            commentDict[name].append(totalCommentsAddedThisCommit)
        # print('Done with commentDict')

    totalChurn = 0
    totalCommits = 0
    # print('Done getting data from repo')
    for name in contributorDict:
        churn = contributorDict[name][0]
        commits = contributorDict[name][1]
        totalChurn += churn
        totalCommits += commits
        first = datetime.strptime(contributorDict[name][2], "%m/%d/%Y")
        last = datetime.strptime(contributorDict[name][3], "%m/%d/%Y")
        tenure = abs((last - first).days) / 7
        productivityChurn = 0
        productivityCommit = 0
        if tenure != 0:
            productivityChurn = churn / tenure
            productivityCommit = commits / tenure
        contributorDict[name].append(productivityChurn)
        contributorDict[name].append(productivityCommit)

    # Average churn and number of commits for all contributors
    averageChurn = totalChurn / len(contributorDict)
    averageCommits = totalCommits / len(contributorDict)

    prodChurnTotal = 0
    prodCommitTotal = 0
    # Calculate average productivity
    for values in contributorDict.values():
        prodChurnTotal += values[4]
        prodCommitTotal += values[5]
    prodChurnAve = prodChurnTotal / len(contributorDict)
    prodCommitAve = prodCommitTotal / len(contributorDict)

    # Get average comments added per commit and average DMM Complexity per commit for each contributor
    # Dict where name is key, average comments added per commit is value
    averageCommentsAdded = {}

    for name in commentDict:
        aveComments = 0
        for numCommentsAdded in commentDict[name]:
            aveComments += numCommentsAdded
        aveComments = aveComments / len(commentDict[name])
        averageCommentsAdded[name] = aveComments

    # Dict where name is key, average DMM complexity is value
    averageDMMComplexity = {}
    for name in dmmComplexityDict:
        aveDMM = 0
        for dmmComp in dmmComplexityDict[name]:
            aveDMM += dmmComp
        aveDMM = aveDMM / len(dmmComplexityDict[name])
        averageDMMComplexity[name] = aveDMM

    # Now we label who is a 10x engineer as those who have a productivity metric 10x greater than the average
    # Key is name, value is 0 if not 10x engineer, 1 if is 10x engineer
    tenTimesLabelChurnDict = label_10x_engineers_churn(contributorDict, prodChurnAve)
    tenTimesLabelCommitDict = label_10x_engineers_churn(contributorDict, prodCommitAve)

    # We want name: [10x label churn, 10x label commits, churn, num commits, churn productivity, commit productivity, first commit, last commit, num owned files, average DMM complexity, average comments added]
    # Dont care about complexity right now
    # Dict of all data we want to put into csv for analysis and regression models
    dataToBePutInCSV = {}
    # print('putting data in dict for csv')
    for name in tenTimesLabelChurnDict:
        dataToBePutInCSV[name] = [tenTimesLabelChurnDict[name]]

    for name in tenTimesLabelCommitDict:
        dataToBePutInCSV[name].append(tenTimesLabelCommitDict[name])

    for name in contributorDict:
        dataToBePutInCSV[name].extend([contributorDict[name][0], contributorDict[name][1], contributorDict[name][4],
                                       contributorDict[name][5], contributorDict[name][2], contributorDict[name][3]])
        dataToBePutInCSV[name].append(0)
        dataToBePutInCSV[name].append(None)

    for name in ownerDict:
        dataToBePutInCSV[name][-2] = ownerDict[name]

    for name in averageDMMComplexity:
        dataToBePutInCSV[name][-1] = averageDMMComplexity[name]

    for name in averageCommentsAdded:
        dataToBePutInCSV[name].append(averageCommentsAdded[name])

    # print('Contributor Dict: ', contributorDict)
    # print('label churn orig: ', tenTimesLabelChurnDict)
    # print('label commit orig: ', tenTimesLabelCommitDict)
    # print('Data to be put in CSV: ', dataToBePutInCSV)

    write_to_csv(dataToBePutInCSV, filename)

# Writes data from dataToBePutInCSV dict, to a csv file with given filename
def write_to_csv(dataToBePutInCSV, filename):
    print()
    print('Writing data to CSV')
    fields = ['name', '10x label churn', '10x label commits', 'churn', 'num commits', 'churn productivity',
              'commit productivity', 'first commit', 'last commit', 'num owned files', 'average DMM complexity',
              'average comments added']
    csvDict = []

    for name in dataToBePutInCSV:
        csvDict.append({'name': name,
                        '10x label churn': dataToBePutInCSV[name][0],
                        '10x label commits': dataToBePutInCSV[name][1],
                        'churn': dataToBePutInCSV[name][2],
                        'num commits': dataToBePutInCSV[name][3],
                        'churn productivity': dataToBePutInCSV[name][4],
                        'commit productivity': dataToBePutInCSV[name][5],
                        'first commit': dataToBePutInCSV[name][6],
                        'last commit': dataToBePutInCSV[name][7],
                        'num owned files': dataToBePutInCSV[name][8],
                        'average DMM complexity': dataToBePutInCSV[name][9],
                        'average comments added': dataToBePutInCSV[name][10]})

    with open(filename, 'w+') as csvfile:
>>>>>>> a23ff0db1a99e46fcb9f9fc68734156e6eddef64
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(csvDict)
