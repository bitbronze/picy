import os, time

retry_delay = 5

while True:
    os.system("python producer_test.py")
    time.sleep(retry_delay)
