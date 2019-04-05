import numpy as np
import cv2
import time
import requests
import argparse
from multiprocessing import Queue, Pool

# python2 video_stream_client.py -i videos/Li165C-DN.mp4 -w 20 -q-size 150

URL = 'http://localhost:5000/process'
HEADERS = {'content-type': 'image/jpeg'}


def worker(input_q, output_q):
    while True:
        frame = input_q.get()

        _, img_encoded = cv2.imencode('.jpg', frame)

        response = requests.post(
            URL, data=img_encoded.tostring(), headers=HEADERS)

        output_q.put(response)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--display", type=int, default=1,
                        help="Whether or not frames should be displayed. (1)")
    parser.add_argument("-I", "--input-device", type=int, default=0,
                        help="Device number input. (0)")
    parser.add_argument("-i", "--input-video-file", type=str, default="",
                        help="Path to videos input, overwrite device input if used.")
    parser.add_argument('-r', '--request-rate', dest='request_rate', type=int,
                        default=5, help='Number of requests per second. (5)')
    parser.add_argument('-w', '--num-workers', dest='num_workers', type=int,
                        default=4, help='Number of workers. (4)')
    parser.add_argument('-q-size', '--queue-size', dest='queue_size', type=int,
                        default=10, help='Size of the queue. (10)')
    args = vars(parser.parse_args())

    # Multiprocessing: Init input and output Queue, and a Pool of workers
    input_q = Queue(maxsize=args["queue_size"])
    output_q = Queue(maxsize=args["queue_size"])
    pool = Pool(args["num_workers"], worker, (input_q, output_q))

    # Create video stream
    if args["input_video_file"] == "":
        video = cv2.VideoCapture(args["input_device"])
    else:
        video = cv2.VideoCapture(args["input_video_file"])

    # Find OpenCV version
    (major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')

    if int(major_ver) < 3:
        fps = video.get(cv2.cv.CV_CAP_PROP_FPS)
    else:
        fps = video.get(cv2.CAP_PROP_FPS)

    if fps > 0:
        delay = int((1 / fps) * 1000)
    else:
        delay = 1

    # Start reading and treating the video stream
    if args["display"] > 0:
        print("\n=====================================================================")
        print("Starting video acquisition. Press 'q' (on the video windows) to stop.")
        print("=====================================================================\n")

    countReadFrames = 0
    countTreatedFrames = 0
    countMissedFrames = 0

    min_elapsed_time = 1./args["request_rate"]
    prev_time = 0

    stopped = False

    while True:

        if not stopped:
            # Read frame and try to store in input queue
            ret, frame = video.read()

            time_elapsed = time.time() - prev_time

            if time_elapsed > min_elapsed_time and ret:
                prev_time = time.time()

                if args["display"] > 0:
                    cv2.imshow('frame', frame)

                # Check input queue is not full
                if not input_q.full():
                    input_q.put(frame)
                    countReadFrames += 1
                else:
                    countMissedFrames += 1

        # Check output queue is not empty
        if not output_q.empty():
            # Recover treated frame in output queue
            response = output_q.get()
            countTreatedFrames += 1
            print("{}\n".format(response.text))

        if cv2.waitKey(delay) & 0xFF == ord('q'):
            print("Stopping...\nWaiting for all workers to finish.\n")
            stopped = True

        if (stopped or not ret) and input_q.empty() and output_q.empty() and countTreatedFrames == countReadFrames:
            print("\nVideo finished or stopped.\nAll queues are empty.")
            break

    print("\n -- Parameters -- ")
    print("FPS: {} (OpenCV v{})\nDelay (wait key time): {} ms".format(
        fps, major_ver, delay))
    print("Requests per second: {}\nQueue max size: {}\nProcesses: {}".format(
        args["request_rate"], input_q._maxsize, pool._processes))

    print("\n -- Results -- ")
    print("Read Frames: {}\nTreated Frames: {}\nMissed Frames: {}\n".format(
          countReadFrames, countTreatedFrames, countMissedFrames))

    # When everything done, release the capture
    video.release()
    pool.terminate()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
