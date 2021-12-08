from pydriller import *
from datetime import datetime, timedelta
import csv
# from mineData import mine_repo, mine
from mineData import mine
import sys
from playsound import playsound
from analyzeData import make_batch_data_monthly

sys.setrecursionlimit(1000)
startTime = datetime.utcnow()

# ================================ IMPORTANT ===============================

# IF USING URLS INSTEAD OF LOCAL PATHS MAKE SURE TO UNCOMMENT THIS AND PUT CORRECT URL AS FIRST PARAMETER OF "mine(...)"
# url = ['https://github.com/ishepard/pydriller.git', 'https://github.com/terryyin/lizard',
#        'https://github.com/BabylonJS/Babylon.js', 'https://github.com/mrdoob/three.js',
#        'https://github.com/KhronosGroup/WebGL', 'https://github.com/julianshapiro/velocity',
#        'https://github.com/titon/toolkit']


localPaths = ['../pydriller', '../velocity', '../toolkit', '../WebGL', '../Babylon.js', '../three.js']

# end_date = datetime(2021, 12, 1, 0, 0, 0)
end_date = datetime.fromisoformat('2021-12-01T00:00:00+00:00')
# pydriller_start = datetime(2018, 3, 21, 0, 0, 0)
pydriller_start = datetime.fromisoformat('2018-03-21T00:00:00+00:00')
# threejs_start = datetime(2015, 6, 21, 0, 0, 0)
threejs_start = datetime.fromisoformat('2015-06-21T00:00:00+00:00')
# webGL_start = datetime(2012, 8, 21, 0, 0, 0)
webGL_start = datetime.fromisoformat('2012-08-21T00:00:00+00:00')
# velocity_start = datetime(2014, 4, 9, 0, 0, 0)
velocity_start = datetime.fromisoformat('2014-04-09T00:00:00+00:00')
# toolkit_start = datetime(2011, 10, 25, 0, 0, 0)
toolkit_start = datetime.fromisoformat('2011-10-25T00:00:00+00:00')
# babylonjs_start = datetime(2016, 11, 20, 0, 0, 0)
babylonjs_start = datetime.fromisoformat('2016-11-20T00:00:00+00:00')

# Testing batches
# test_start_date = datetime(2021, 10, 1)
# test_start_date = pydrillerStart
# test_end_date = datetime(2021, 12, 1)
# test_end_date = datetime(21, 12, 1, 0, 0, 0)
# mine(localPaths[0], 'Python', test_start_date, test_end_date, 'pydriller_batch_test', batch_size)
# repo = Repository(localPaths[2], since=test_start_date, to=datetime(2017, 5, 1, 0, 0, 0))
# mine_repo(repo, 'JavaScript', 'Data/Batch Data/WebGL_batch_test_diff_tenure Batches/First 4 Batches.csv')
# -------------- WARNING MINING FOR THE REPOS WILL TAKE A VERY LONG TIME --------------

batch_size = timedelta(days=10)

# print('Starting to mine pydriller...\n')
# mineStartTime = datetime.utcnow()
# mine(localPaths[0], 'Python', pydriller_start, end_date, 'pydriller_batch', batch_size)
# mineEndTime = datetime.utcnow()
#
# timeElapsed = mineEndTime - mineStartTime
# playsound('Okaaayyyyy lets go.mp3')
# print('Done with pydriller... Process took ' + str(timeElapsed.seconds) + ' seconds')
# print('Starting to mine velocity\n')
#
# mineStartTime = datetime.utcnow()
# mine(localPaths[1], 'JavaScript', velocity_start, end_date, 'velocity_batch', batch_size)
# mineEndTime = datetime.utcnow()
# timeElapsed = mineEndTime - mineStartTime
#
# print('Done with velocity... Process took ' + str(timeElapsed.seconds) + ' seconds')
# print('Starting to mine toolkit\n')
#
# mineStartTime = datetime.utcnow()
# mine(localPaths[2], 'JavaScript', toolkit_start, end_date, 'toolkit_batch', batch_size)
# mineEndTime = datetime.utcnow()
# timeElapsed = mineEndTime - mineStartTime
#
# print('Done with toolkit... Process took ' + str(timeElapsed.seconds) + ' seconds')
# print('Starting to mine WebGL\n')
#
# mineStartTime = datetime.utcnow()
# mine(localPaths[3], 'JavaScript', webGL_start, end_date, 'webgl_batch', batch_size)
# mineEndTime = datetime.utcnow()
# timeElapsed = mineEndTime - mineStartTime
#
# print('Done with WebGL... Process took ' + str(timeElapsed.seconds) + ' seconds')
# print('Starting to mine Babylon.js\n')
#
# # stopped at 2017-06-18
# # date_babylon_stopped_at = datetime(2017, 6, 18, 0, 0, 0)
# # date_babylon_stopped_at_second = datetime(2017, 6, 28, 0, 0, 0)
# date_babylon_stopped_at_second = datetime.fromisoformat('2017-03-30T00:00:00+00:00')
# test_end_date = date_babylon_stopped_at_second + batch_size
#
# mineStartTime = datetime.utcnow()
# mine(localPaths[4], 'JavaScript', date_babylon_stopped_at_second, end_date, 'babylonjs_batch', batch_size)
# # mine(localPaths[4], 'JavaScript', date_babylon_stopped_at_second, test_end_date, 'babylonjs_batch', batch_size)
# mineEndTime = datetime.utcnow()
# timeElapsed = mineEndTime - mineStartTime
#
# print('Done with Babylon.js... Process took ' + str(timeElapsed.seconds) + ' seconds')

# ============================ CODE TO MINE THREE.JS BELOW ======================================
threejs_end_1 = datetime.fromisoformat('2016-06-21T00:00:00+00:00')
threejs_end_2 = datetime.fromisoformat('2017-06-21T00:00:00+00:00')
threejs_end_3 = datetime.fromisoformat('2018-06-21T00:00:00+00:00')
threejs_end_4 = datetime.fromisoformat('2019-06-21T00:00:00+00:00')
threejs_end_5 = datetime.fromisoformat('2020-06-21T00:00:00+00:00')

# ------------------- UNCOMMENT BELOW THIS LINE TO MINE DATA FOR ALL OF THREE.JS ------------------------------------
# print('Starting to mine three.js\n')
# mineStartTime = datetime.utcnow()
# # UNCOMMENT LINE BELOW TO MINE USING LOCAL REPO.. HAVE TO PULL THREE.JS TO LOCAL
# mine(localPaths[5], 'JavaScript', threejs_start, end_date, 'threejs_batch', batch_size)
# # UNCOMMENT LINE BELOW TO MINE USING URL.. HAVE TO UNCOMMENT "url" VARIABLE AT THE TOP... DONT RECOMMEND USING URL
# mine(url[3], 'JavaScript', threejs_start, end_date, 'threejs_batch', batch_size)
# mineEndTime = datetime.utcnow()
# timeElapsed = mineEndTime - mineEndTime
# print('Finished mining all of three.js')
# print('Process took ' + str(timeElapsed.seconds) + ' seconds')

# ------------------- UNCOMMENT BELOW THIS LINE TO MINE FIRST YEAR OF THREE.JS -----------------------------------
# ------------------- TY IS RUNNING THIS ------------------------------------

# print('Starting to mine first year of three.js\n')
# threejs_end_1 = datetime.fromisoformat('2016-06-21T00:00:00+00:00')
# mineStartTime = datetime.utcnow()
# # UNCOMMENT LINE BELOW TO MINE USING LOCAL REPO.. HAVE TO PULL THREE.JS TO LOCAL
# mine(localPaths[5], 'JavaScript', threejs_start, threejs_end_1, 'threejs_batch', batch_size)
# # UNCOMMENT LINE BELOW TO MINE USING URL.. HAVE TO UNCOMMENT "url" VARIABLE AT THE TOP... DONT RECOMMEND USING URL
# mine(url[3], 'JavaScript', threejs_start, threejs_end_1, 'threejs_batch', batch_size)
# mineEndTime = datetime.utcnow()
# timeElapsed = mineEndTime - mineEndTime
# print('Finished mining first year of three.js')
# print('Process took ' + str(timeElapsed.seconds) + ' seconds')

# ------------------- UNCOMMENT BELOW THIS LINE TO MINE SECOND YEAR OF THREE.JS -----------------------------------
# ------------------- RONG CHING-CHANG IS RUNNING THIS ------------------------------------

# print('Starting to mine second year of three.js\n')
# threejs_end_2 = datetime.fromisoformat('2017-06-21T00:00:00+00:00')
# mineStartTime = datetime.utcnow()
# # UNCOMMENT LINE BELOW TO MINE USING LOCAL REPO.. HAVE TO PULL THREE.JS TO LOCAL
# mine(localPaths[5], 'JavaScript', threejs_end_1, threejs_end_2, 'threejs_batch', batch_size)
# # UNCOMMENT LINE BELOW TO MINE USING URL.. HAVE TO UNCOMMENT "url" VARIABLE AT THE TOP... DONT RECOMMEND USING URL
# mine(url[3], 'JavaScript', threejs_end_1, threejs_end_2, 'threejs_batch', batch_size)
# mineEndTime = datetime.utcnow()
# timeElapsed = mineEndTime - mineEndTime
# print('Finished mining second year of three.js')
# print('Process took ' + str(timeElapsed.seconds) + ' seconds')

# ------------------- UNCOMMENT BELOW THIS LINE TO MINE THIRD YEAR OF THREE.JS -----------------------------------
# ------------------- ERIC IS RUNNING THIS ------------------------------------

# print('Starting to mine third year of three.js\n')
# threejs_end_3 = datetime.fromisoformat('2018-06-21T00:00:00+00:00')
# mineStartTime = datetime.utcnow()
# # UNCOMMENT LINE BELOW TO MINE USING LOCAL REPO.. HAVE TO PULL THREE.JS TO LOCAL
# mine(localPaths[5], 'JavaScript', threejs_end_2, threejs_end_3, 'threejs_batch', batch_size)
# # UNCOMMENT LINE BELOW TO MINE USING URL.. HAVE TO UNCOMMENT "url" VARIABLE AT THE TOP... DONT RECOMMEND USING URL
# mine(url[3], 'JavaScript', threejs_end_2, threejs_end_3, 'threejs_batch', batch_size)
# mineEndTime = datetime.utcnow()
# timeElapsed = mineEndTime - mineEndTime
# print('Finished mining third year of three.js')
# print('Process took ' + str(timeElapsed.seconds) + ' seconds')

# ------------------- UNCOMMENT BELOW THIS LINE TO MINE FOURTH YEAR OF THREE.JS -----------------------------------
# ------------------- ERIC IS RUNNING THIS IF HE CAN ------------------------------------
# print('Starting to mine fourth year of three.js\n')
# threejs_end_4 = datetime.fromisoformat('2019-06-21T00:00:00+00:00')
# mineStartTime = datetime.utcnow()
# # UNCOMMENT LINE BELOW TO MINE USING LOCAL REPO.. HAVE TO PULL THREE.JS TO LOCAL
# mine(localPaths[5], 'JavaScript', threejs_end_3, threejs_end_4, 'threejs_batch', batch_size)
# # UNCOMMENT LINE BELOW TO MINE USING URL.. HAVE TO UNCOMMENT "url" VARIABLE AT THE TOP... DONT RECOMMEND USING URL
# mine(url[3], 'JavaScript', threejs_end_3, threejs_end_4, 'threejs_batch', batch_size)
# mineEndTime = datetime.utcnow()
# timeElapsed = mineEndTime - mineEndTime
# print('Finished mining fourth year of three.js')
# print('Process took ' + str(timeElapsed.seconds) + ' seconds')

# ------------------- UNCOMMENT BELOW THIS LINE TO MINE FIFTH YEAR OF THREE.JS -----------------------------------
# ------------------- WILLIAM IS RUNNING ------------------------------------
# threejs_end_5 = datetime.fromisoformat('2020-06-21T00:00:00+00:00')
# print('Starting to mine fifth year of three.js\n')
# mineStartTime = datetime.utcnow()
# # UNCOMMENT LINE BELOW TO MINE USING LOCAL REPO.. HAVE TO PULL THREE.JS TO LOCAL
# mine(localPaths[5], 'JavaScript', threejs_end_4, threejs_end_5, 'threejs_batch', batch_size)
# # UNCOMMENT LINE BELOW TO MINE USING URL.. HAVE TO UNCOMMENT "url" VARIABLE AT THE TOP
# mine(url[3], 'JavaScript', threejs_end_4, threejs_end_5, 'threejs_batch', batch_size)
# mineEndTime = datetime.utcnow()
# timeElapsed = mineEndTime - mineEndTime
# print('Finished mining fifth year of three.js')
# print('Process took ' + str(timeElapsed.seconds) + ' seconds')

# ------------------- UNCOMMENT BELOW THIS LINE TO MINE SIXTH/LAST YEAR OF THREE.JS -----------------------------------
# print('Starting to mine sixth year of three.js\n')
# mineStartTime = datetime.utcnow()
# # UNCOMMENT LINE BELOW TO MINE USING LOCAL REPO.. HAVE TO PULL THREE.JS TO LOCAL
# mine(localPaths[5], 'JavaScript', threejs_end_5, end_date, 'threejs_batch', batch_size)
# # UNCOMMENT LINE BELOW TO MINE USING URL.. HAVE TO UNCOMMENT "url" VARIABLE AT THE TOP
# mine(url[3], 'JavaScript', threejs_end_5, end_date, 'threejs_batch', batch_size)
# mineEndTime = datetime.utcnow()
# timeElapsed = mineEndTime - mineEndTime
# print('Finished mining sixth year of three.js')
# print('Process took ' + str(timeElapsed.seconds) + ' seconds')

# endTime = datetime.utcnow()
# timeElapsed = endTime - startTime
# print('Finished mining')
# print('Process took ' + str(timeElapsed.seconds) + ' seconds')
# playsound('Okaaayyyyy lets go.mp3')



# --------------------------- Get batch data into monthly format ---------------------------------------
# babylon_name = 'babylonjs_batch'
# # babylon_end_date = datetime.fromisoformat('2018-07-03T00:00:00+00:00')
# babylon_end_date = datetime(2018, 7, 3, 0, 0, 0)
# make_batch_data_monthly(babylon_name, batch_size, babylon_end_date)

pydriller_name = 'pydriller_batch'
velocity_name = 'velocity_batch'
toolkit_name = 'toolkit_batch'
webgl_name = 'webgl_batch'
threejs_name = 'threejs_batch'

end_date_for_monthly = datetime(2021, 12, 1, 0, 0, 0)

make_batch_data_monthly(pydriller_name, batch_size, end_date_for_monthly)
make_batch_data_monthly(velocity_name, batch_size, end_date_for_monthly)
make_batch_data_monthly(toolkit_name, batch_size, end_date_for_monthly)
make_batch_data_monthly(webgl_name, batch_size, end_date_for_monthly)
make_batch_data_monthly(threejs_name, batch_size, end_date_for_monthly)