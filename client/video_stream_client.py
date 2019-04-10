import time
import argparse
from multiprocessing import Queue, Pool
import json
import requests
import cv2
import numpy as np


# python2 video_stream_client.py -i videos/Li165C-DN.mp4 -w 20 -q-size 150

LOCAL_URL = 'http://localhost:5000/process'
SERVER_URL = 'http://192.168.215.21:7700/process'
HEADERS = {'content-type': 'image/jpeg'}


def worker(url, input_q, output_q):
    while True:
        n_frame, frame = input_q.get()

        _, img_encoded = cv2.imencode('.jpg', frame)

        response = requests.post(
            url, data=img_encoded.tostring(), headers=HEADERS)

        output_q.put((n_frame, response))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", type=int, default=1,
                        help="Whether or not responses should be printed. (1)")
    # TODO fix bug on display 0 where client reads too less frames
    parser.add_argument("-d", "--display", type=int, default=1,
                        help="Whether or not frames should be displayed. (1)")
    parser.add_argument("-u", "--url", dest="url", type=str, default="local",
                        help="Server URL to send frames to. If \"local\": localhost:5000/process; "
                        "If \"server\": http://192.168.215.21:7700/process; Else use URL argument.")
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

    if args["url"].lower() == 'local':
        url = LOCAL_URL
    elif args["url"].lower() == 'server':
        url = SERVER_URL
    else:
        url = args["url"]

    # Multiprocessing: Init input and output Queue, and a Pool of workers
    input_q = Queue(maxsize=args["queue_size"])
    output_q = Queue(maxsize=args["queue_size"])
    pool = Pool(args["num_workers"], worker, (url, input_q, output_q))

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

    count_read_frames = 0
    count_treated_frames = 0
    count_missed_frames = 0
    count_skipped_frames = 0

    min_elapsed_time = 1./args["request_rate"]
    prev_time = 0
    stopped = False

    classes = ["aeroplane", "bicycle", "bird", "boat", "bottle", "bus", "car", "cat", "chair", "cow",
               "diningtable", "dog", "horse", "motorbike", "person", "pottedplant", "sheep", "sofa", "train", "tvmonitor"]

    COLORS = dict()
    for k in classes:
        COLORS[k] = np.random.uniform(0, 255, size=(1, 3))[0]

    prev_frame = -1
    frames_to_display = dict()
    responses_to_display = dict()

    while True:

        if not stopped:
            # Read frame and try to store in input queue
            ret, frame = video.read()

            time_elapsed = time.time() - prev_time

            if time_elapsed > min_elapsed_time and ret:
                prev_time = time.time()

                # Check input queue is not full
                if not input_q.full():
                    input_q.put((count_read_frames, frame))
                    if args["display"] > 0:
                        frames_to_display[count_read_frames] = frame
                    count_read_frames += 1
                else:
                    count_missed_frames += 1

        # Check output queue is not empty
        if not output_q.empty():
            # Recover treated frame in output queue
            n_frame, response = output_q.get()
            count_treated_frames += 1

            if args["verbose"] > 0:
                print("{}\n".format(response.text))

            if args["display"] > 0 and response.status_code == 200:
                responses_to_display[n_frame] = response

        if args["display"] > 0:
            for k_frame in sorted(list(responses_to_display.keys())):
                if prev_frame > k_frame:
                    count_skipped_frames += 1
                    if args["verbose"] > 0:
                        print("Skipped Frame: {}. Current: {}".format(
                            k_frame, prev_frame))
                    del responses_to_display[k_frame]
                    del frames_to_display[k_frame]
                    continue

                prev_frame = k_frame

                output_frame = frames_to_display[k_frame]
                response = responses_to_display[k_frame]

                json_data = json.loads(response.text)

                for result in json_data['results']:
                    color = COLORS[result['class']]

                    coords = result['[x,y,w,h]']
                    w = int(coords[2])
                    h = int(coords[3])
                    x = int(coords[0]) - w / 2
                    y = int(coords[1]) - h / 2

                    cv2.rectangle(output_frame, (x, y),
                                  (x+w, y+h), color, 4)
                    cv2.putText(output_frame, result['class'], (x-10, y-10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

                # output_frame = cv2.resize(output_frame, (720, 540))
                cv2.imshow('frame', output_frame)

                del frames_to_display[k_frame]
                del responses_to_display[k_frame]

                # only process the first valid frame, to wait min delay time to show image
                break

        if cv2.waitKey(delay) & 0xFF == ord('q'):
            print("Stopping...\nWaiting for all workers to finish.\n")
            print("-- Current Counts -- ")
            print("Read Frames: {}\nTreated Frames: {}\n".format(
                count_read_frames, count_treated_frames))
            stopped = True

        if (stopped or not ret) and input_q.empty() and output_q.empty() and count_treated_frames == count_read_frames:
            print("\nVideo finished or stopped.\nAll queues are empty.")
            break

    print("\n -- Parameters -- ")
    print("FPS: {} (OpenCV v{})\nDelay (wait key time): {} ms".format(
        fps, major_ver, delay))
    print("Requests per second: {}\nQueue max size: {}\nProcesses: {}".format(
        args["request_rate"], input_q._maxsize, pool._processes))

    print("\n -- Results -- ")
    print("Read Frames: {}\nTreated Frames: {}".format(
        count_read_frames, count_treated_frames))
    print("Missed Frames: {}\nSkipped Frames: {}\n".format(
        count_missed_frames, count_skipped_frames))

    # When everything done, release the capture
    video.release()
    pool.terminate()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
