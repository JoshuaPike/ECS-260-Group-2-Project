from pydriller import *
from datetime import datetime
import csv
from mineData import mine_repo
import sys

sys.setrecursionlimit(10000)

url = ['https://github.com/ishepard/pydriller.git', 'https://github.com/terryyin/lizard',
       'https://github.com/BabylonJS/Babylon.js', 'https://github.com/mrdoob/three.js',
       'https://github.com/KhronosGroup/WebGL', 'https://github.com/julianshapiro/velocity',
       'https://github.com/titon/toolkit']

localPaths = ['../pydriller', '../three.js', '../WebGL', '../velocity', '../toolkit']

# branch = ['dev']

# dates for three.js, webGL
dates = [datetime(2021, 3, 1, 0, 0, 0), datetime(2021, 11, 5, 0, 0, 0), datetime(2017, 1, 1, 0, 0, 0)]

pydrillerRepo = Repository(localPaths[0])

threejsRepo = Repository(localPaths[1], since=dates[0], to=dates[1])


webGLRepo = Repository(localPaths[2], since=dates[2], to=dates[1])

# Velocity has 895 total commits
velocityRepo = Repository(localPaths[3])

# toolkit has 1678 total commits
toolkitRepo = Repository(localPaths[4])

# -------------- WARNING MINING FOR THE REPOS WILL TAKE A VERY LONG TIME --------------


print('Starting to mine pydriller...')
mine_repo(pydrillerRepo, 'Python', 'pydrillerData.csv')

print('Done with pydriller... Starting to mine threejs')
# From 2/1/2021 to 11/5/2021
mine_repo(threejsRepo, 'JavaScript', 'threejsData.csv')

print('Done with threejs... Starting to mine webGL')
# From 10/5/2020 to 11/5/2021
mine_repo(webGLRepo, 'JavaScript', 'webGLData.csv')

print('Done with webGL... Starting to mine velocity')
mine_repo(velocityRepo, 'JavaScript', 'velocityData.csv')

print('Done with velocity... Starting to mine toolkit')
mine_repo(toolkitRepo, 'JavaScript', 'toolkitData.csv')

print('Finished mining')