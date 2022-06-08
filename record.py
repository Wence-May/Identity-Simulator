import wave
import threading
import pyaudio
import cv2
from os import remove, mkdir, removedirs, listdir
from os.path import exists, splitext, basename, join
from datetime import datetime
from time import sleep
from shutil import rmtree
from PIL import ImageGrab
from numpy import array
from moviepy.editor import *

CHUNK_SIZE = 1024
CHANNELS = 2
FORMAT = pyaudio.paInt16
RATE = 48000
allowRecording = True



def record_audio():
    p = pyaudio.PyAudio()
    event.wait()
    sleep(3)
    # create input stream
    stream = p.open(format=FORMAT, channels=1, rate=RATE,
                    input=True, frames_per_buffer=CHUNK_SIZE)
    wf = wave.open(audio_filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    while allowRecording:
        # read data from audio-recording device and directly write into wav file
        data = stream.read(CHUNK_SIZE)
        wf.writeframes(data)
    wf.close()
    stream.stop_stream()
    stream.close()
    p.terminate()


# def record_screen():
#     event.wait()
#     sleep(3)
#     im = ImageGrab.grab()
#     video = cv2.VideoWriter(screen_video_filename,
#                              cv2.VideoWriter_fourcc(*'XVID'), 25, im.size)
#     while allowRecording:
#         im = ImageGrab.grab()
#         im = cv2.cvtColor(array(im), cv2.COLOR_RGB2BGR)
#         video.write(im)
#     video.release()


def record_webcam():
    # parameter 0 means using laptop webcam
    cap = cv2.VideoCapture(0)
    event.set()
    sleep(3)
    aviFile = cv2.VideoWriter(
        webcam_video_filename, cv2.VideoWriter_fourcc(*'MJPG'), 25, (640, 480))
    # capture the present image, ret=True means success
    while allowRecording and cap.isOpened():
        ret, frame = cap.read()
        if ret:
            aviFile.write(frame)
    aviFile.release()
    cap.release()


now = str(datetime.now())[:19].replace(':', '_')
audio_filename = f'{now}.mp3'
webcam_video_filename = f'data/webcam-{now}.mov'
# screen_video_filename = f'screen-{now}.mov'
video_filename = f'data/{now}.mov'

# create 2 threads for audio and screen
t1 = threading.Thread(target=record_audio)
# t2 = threading.Thread(target=record_screen)
t3 = threading.Thread(target=record_webcam)

# build time for multi-threads to sync, to start recording at the same time
event = threading.Event()
event.clear()
for t in (t1, t3):
    t.start()

# wait for camera to be ready & alert user to be recording in 3 sec
event.wait()
print("start recording after 3 seconds... pre Q to quit")
while True:
    if input() == 'q':
        break
allowRecording = False
for t in (t1, t3):
    t.join()


# combine audio and screen to video file
audio = AudioFileClip(audio_filename)
# video1 = VideoFileClip(screen_video_filename)
# ratio1 = audio.duration/video1.duration
# video1 = (video1.fl_time(lambda t:t/ratio1,
#           apply_to=['video']).set_end(audio.duration))

video2 = VideoFileClip(webcam_video_filename)
ratio2 = audio.duration/video2.duration
video2 = (video2.fl_time(lambda t: t/ratio2).set_end(audio.duration))
video = CompositeVideoClip(video2).set_audio(audio)
video.write_videofile(video_filename, fps=25)

# delete temporary files
remove(audio_filename)
remove(screen_video_filename)
remove(webcam_video_filename)
