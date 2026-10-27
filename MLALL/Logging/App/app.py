import logging

logger=logging.getLogger("ArithmeticApp")
logger.setLevel(logging.DEBUG)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s-%(name)s-%(levelname)s-%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('app1.log'),
        logging.StreamHandler(),
    ]
)

def add(a,b):
    logger.debug("the addition operation is taking place")
    return a+b
logger.debug("the addition function is called")
add(3,5)
def subs(a,b):
    logger.debug("substraction function is running")
    return a-b
logger.debug("the substraction is been calling")
subs(5,3)
def multiply(a,b):
    logger.debug("multiplier function is runnig")
    return a*b
logger.debug("multiplier function is been calling")
multiply(2,3)
def division(a,b):
    logger.debug("division funtion is running ")
    return a/b
logger.debug("the division is been called")
division(10,2)
