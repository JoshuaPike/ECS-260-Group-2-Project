from pydriller import *
from datetime import datetime, timedelta
import csv
from mineData import mine_repo, mine_in_batches
import sys

sys.setrecursionlimit(10000)
startTime = datetime.utcnow()
# url = ['https://github.com/ishepard/pydriller.git', 'https://github.com/terryyin/lizard',
#        'https://github.com/BabylonJS/Babylon.js', 'https://github.com/mrdoob/three.js',
#        'https://github.com/KhronosGroup/WebGL', 'https://github.com/julianshapiro/velocity',
#        'https://github.com/titon/toolkit']


localPaths = ['../pydriller', '../velocity', '../toolkit', '../WebGL', '../Babylon.js', '../three.js']

end_date = datetime(2021, 12, 1, 0, 0, 0)

pydriller_start = datetime(2018, 3, 21, 0, 0, 0)

threejs_start = datetime(2015, 6, 21, 0, 0, 0)

webGL_start = datetime(2012, 8, 21, 0, 0, 0)

velocity_start = datetime(2014, 4, 9, 0, 0, 0)

toolkit_start = datetime(2011, 10, 25, 0, 0, 0)

babylonjs_start = datetime(2016, 11, 20, 0, 0, 0)

# Testing batches
# test_start_date = datetime(2021, 10, 1)
# test_start_date = pydrillerStart
# test_end_date = datetime(2021, 12, 1)
# test_end_date = datetime(21, 12, 1, 0, 0, 0)
# mine_in_batches(localPaths[0], 'Python', test_start_date, test_end_date, 'pydriller_batch_test', batch_size)
# repo = Repository(localPaths[2], since=test_start_date, to=datetime(2017, 5, 1, 0, 0, 0))
# mine_repo(repo, 'JavaScript', 'Data/Batch Data/WebGL_batch_test_diff_tenure Batches/First 4 Batches.csv')
# -------------- WARNING MINING FOR THE REPOS WILL TAKE A VERY LONG TIME --------------

batch_size = timedelta(days=30)

print('Starting to mine pydriller...')
mineStartTime = datetime.utcnow()
mine_in_batches(localPaths[0], 'Python', pydriller_start, end_date, 'pydriller_batch', batch_size)
mineEndTime = datetime.utcnow()

timeElapsed = mineEndTime - mineStartTime

print('Done with pydriller... Process took ' + str(timeElapsed.seconds) + ' seconds')
print('Starting to mine velocity')

mineStartTime = datetime.utcnow()
mine_in_batches(localPaths[1], 'JavaScript', velocity_start, end_date, 'velocity_batch', batch_size)
mineEndTime = datetime.utcnow()
timeElapsed = mineEndTime - mineStartTime

print('Done with velocity... Process took ' + str(timeElapsed.seconds) + ' seconds')
print('Starting to mine toolkit')

mineStartTime = datetime.utcnow()
mine_in_batches(localPaths[2], 'JavaScript', toolkit_start, end_date, 'toolkit_batch', batch_size)
mineEndTime = datetime.utcnow()
timeElapsed = mineEndTime - mineStartTime

print('Done with toolkit... Process took ' + str(timeElapsed.seconds) + ' seconds')
print('Starting to mine WebGL')

mineStartTime = datetime.utcnow()
mine_in_batches(localPaths[3], 'JavaScript', webGL_start, end_date, 'webgl_batch', batch_size)
mineEndTime = datetime.utcnow()
timeElapsed = mineEndTime - mineStartTime

print('Done with WebGL... Process took ' + str(timeElapsed.seconds) + ' seconds')
print('Starting to mine Babylon.js')

mineStartTime = datetime.utcnow()
mine_in_batches(localPaths[4], 'JavaScript', babylonjs_start, end_date, 'babylonjs_batch', batch_size)
mineEndTime = datetime.utcnow()
timeElapsed = mineEndTime - mineStartTime

print('Done with Babylon.js... Process took ' + str(timeElapsed.seconds) + ' seconds')
print('Starting to mine three.js')

mineStartTime = datetime.utcnow()
mine_in_batches(localPaths[5], 'JavaScript', threejs_start, end_date, 'threejs_batch', batch_size)
mineEndTime = datetime.utcnow()


endTime = datetime.utcnow()
timeElapsed = endTime - startTime
print('Finished mining')
print('Process took ' + str(timeElapsed.seconds) + ' seconds')