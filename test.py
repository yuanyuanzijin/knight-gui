from path import *
import time

atime = time.time()
result = search_path(size=8, history=[[0,0]])
btime = time.time()
print(result, btime-atime)