from pydub import AudioSegment
import pyaudio
import wave
import contextlib
import audioop
import numpy as np
import matplotlib.pyplot as plt
import math
import sys
from pylab import *
# Returns current settings in seting file
def read_settings_file():
    f = open("temp/settings.txt", "r")
    lines = f.readlines()
    res = []
    for line in lines:
        idx = line.find(":")
        res.append(line[idx+2:-1])
    f.close()
    
    return res

# p = pyaudio.PyAudio()

# CHUNK = 1024
# FORMAT = pyaudio.paInt16
# CHANNELS = 1
# RATE = 44100
# WAVE_OUTPUT_FILENAME = "silenced.wav"
# RECORD_SECONDS = 0
# with contextlib.closing(wave.open("recordings/007_00003.wav",'r')) as f:
#     frames = f.getnframes()
#     rate = f.getframerate()
#     RECORD_SECONDS = frames / float(rate)


# stream = p.open(format=FORMAT,
#                 channels=CHANNELS,
#                 rate=RATE,
#                 input=True,
#                 frames_per_buffer=CHUNK)

# rms = []
# for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
#     data = stream.read(CHUNK)
#     rms.append(audioop.rms(data, 2))    # here's where you calculate the volume

# stream.stop_stream()
# stream.close()
# p.terminate()

# rms =[20*math.log(r, 10) for r in rms]
# plt.plot(rms[1:])
# plt.ylabel('some numbers')
# plt.show()


spf = wave.open("recordings/007_00003.wav",'r')
sound_info = spf.readframes(-1)
sound_info = fromstring(sound_info, 'Int16')

plt.plot(sound_info/30000)
plt.ylabel('some numbers')
plt.show()


# song = AudioSegment.from_wav("recordings/007_00000.wav")

# print(song.duration_seconds)
# second = 1 * 2000

# first_second = song[:second]

# ending = song[-2000:]

# beginning = first_second + 6
# end = ending - 3
# without_the_middle = beginning + end

# without_the_middle.export("mashup.wav", format="wav")