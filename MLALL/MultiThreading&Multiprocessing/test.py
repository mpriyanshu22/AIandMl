import multiprocessing
import time

def sq_num():
    for i in range(5):
        print(f"square:{i*i}", flush=True)

def cube_num():
    for i in range(5):
        print(f"cube:{i*i*i}", flush=True)

if __name__ == "__main__":
    p1 = multiprocessing.Process(target=sq_num)
    p2 = multiprocessing.Process(target=cube_num)

    t = time.time()
    p1.start()
    p2.start()
    p1.join()
    p2.join()

    finished_time = time.time() - t
    print(finished_time)
