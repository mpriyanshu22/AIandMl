import multiprocessing
import math
import sys
import time
sys.set_int_max_str_digits(100000)

def compute_factorial(number):
    print(f"computing factorial of {number}")
    result=math.factorial(number)
    print(f"factorial of{number} is {result}")
    return result
if __name__=="__main__":
    numbers=[5000,6000,7000,8000]
    start_time=time.time()

    with multiprocessing.Pool() as pool:
        results=pool.map(compute_factorial,numbers)

    endtime=time.time()
    print(f"results:{results}")
    print(f"time taken:{endtime-start_time} seconds")   