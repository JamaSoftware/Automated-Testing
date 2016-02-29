import datetime
import random
import time
import sys


def run_test(item_id, step_number):
    time.sleep(random.randrange(0, 10))  # May take some time to run
    test_result = random.choice(["Pass", "Fail"])
    f = open("results---{}".format(datetime.datetime.now()), 'w')
    # Write formatted results to file
    f.write("Item ID: {}\nStep #: {}\nResult: {}".format(item_id, step_number, test_result))


if __name__ == "__main__":
    run_test(sys.argv[1], sys.argv[2])
