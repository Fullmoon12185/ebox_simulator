from multiprocessing.pool import ThreadPool as Pool
import time 
# from multiprocessing import Pool

pool_size = 5  # your "parallelness"

# define worker function before a Pool is instantiated
def worker(item):
    try:
        while(True): 
            print(item)
            time.sleep(1)
    except:
        print('error with item')



try:
    pool = Pool(pool_size)

    for item in range(0,5):
        pool.apply_async(worker, (item,))
    while True:
        time.sleep(2)
except KeyboardInterrupt:
    pool.close()
    pool.join()