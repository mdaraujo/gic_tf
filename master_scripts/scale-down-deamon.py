import schedule
import time
import subprocess


def job():
    print("Down scaling..")
    subprocess.run(["./scale-down.sh"])


schedule.every().day.at("05:00").do(job)

while 1:
    schedule.run_pending()
    time.sleep(1)
