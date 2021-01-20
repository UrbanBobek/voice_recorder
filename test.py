from recorder import Recorder
from py_audio_settings import PyAduioSettings
from utils import *
import mute_alsa

pSetting = PyAduioSettings()
# output_devices = pSetting.return_output_devices()
input_devices = pSetting.return_input_devices()



# test = Recorder()
# # # rec = test.open("temp/test.wav", mode="wb")
# rec = test.open("temp/test.wav", input_dev=2)
# rec.record(3)
# rec.playback_file()
# while True:
#     print("audio playin?")