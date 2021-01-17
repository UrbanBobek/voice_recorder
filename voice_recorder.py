import kivy
from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, StringProperty
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen

from recorder import Recorder
from py_audio_settings import PyAduioSettings
from utils import *

import threading
import mute_alsa

import os.path
from os import path

Builder.load_file('voicerecorder.kv')


# Set app size
# Window.size = (500, 700)

class StartLayout(Screen):
    font_size_ui = ObjectProperty(32)

    def __init__(self, **kwargs):
        super(StartLayout, self).__init__(**kwargs)

        settings = read_settings_file()
        self.font_size_ui = int(settings[2])
    
    def on_enter(self, *args):
        settings = read_settings_file()
        self.font_size_ui = int(settings[2])


class RecordScreen(Screen):
    next_rec = ObjectProperty(None)
    text_to_read = StringProperty()
    prog_indic = StringProperty()
    font_size_ui = ObjectProperty(32)

    # Create Recorder object
    recorder = Recorder()
    rec = None

     # Store text lines to read
    txt = return_text_from_xlsx("text/Artur-B-G0042.xlsx")
    # f = open("text/text.txt")
    # for i, line in enumerate(f):
    #     txt.append(line[0:-1])
    # f.close()
    

    def __init__(self, **kwargs):
        super(RecordScreen, self).__init__(**kwargs)
        Window.bind(on_key_down=self._on_keyboard_down)
        Window.bind(on_key_up=self._on_keyboard_up)
        self.rec_file_name = "initial_file_name"
        self.text_id = 0
        self.last_rec_id = 0
        self.enable_keyboard_flag = False

        settings = read_settings_file()
        self.font_size_ui = int(settings[2])

    def on_enter(self, *args):
        self.enable_keyboard(True)

        self.curr_user, self.code = self.return_user_data()
        f = open("user_data/{}".format(self.curr_user))
        file_data = f.readlines()
        if len(file_data) > 5:
            self.text_to_read = self.txt[len(file_data)-5]
            self.text_id = len(file_data)-5
            self.last_rec_id = len(file_data)-5
        else:
            self.text_to_read = "Pritisnite gumb 'Naslednji' (enter/space) in pričnite brati tekst na ekranu"
            self.text_id = 0
            self.last_rec_id = 0

        self.prog_indic = "0/{}".format(len(self.txt))
        self.key_up = True

        settings = read_settings_file()
        self.font_size_ui = int(settings[2])

        print(read_settings_file())

    def on_leave(self, *args):
        self.enable_keyboard(False)

    # Button shortcuts
    def _on_keyboard_down(self, instance, keyboard, keycode, text, modifiers):
        # print(keycode)
        if self.enable_keyboard_flag and self.key_up:
            self.key_up = False
            if  keycode == 40 or keycode == 44:  # 40 - Enter key pressed, 44 - spacebar, 79 - right arrow key
                self.next_recording()
            if  keycode == 82:  # 82 - up key
                self.playback_rec()
            if  keycode == 79 and self.text_id + 1 < self.last_rec_id:  # 79 - right arrow key
                self.one_text_foward()
            if  keycode == 80:  # 80 - left key
                self.one_text_back()
            if  keycode == 224:  # 224 - lctrl
                self.redo_rec()

    def _on_keyboard_up(self, instance, keyboard, keycode):
        self.key_up = True

    # Read user code from file
    def return_user_data(self):
        with open("temp/curr_user_data.txt") as f:
            t = f.read()
            t = t.split()
            if len(t) > 1:
                curr_user = t[0]
                code = t[-1]
            else:
                curr_user = "noUser"
                code = "NoCode"
            f.close()
        return curr_user, code

    def next_recording(self):
        if self.text_id > len(self.txt):
            print("konec!")
            self.fp.close()

        if self.rec is not None:
            self.rec.stop_recording()
            self.rec.close()
            self.rec = None
            self.toggle_rec_dot(False)

        self.curr_user, self.code = self.return_user_data()
        self.rec_file_name = "{}_{}.wav".format(self.code, str(self.text_id).zfill(5))

        # Check if recording already exists
        file_name = "recordings/{}".format(self.rec_file_name)
        if not path.exists(file_name):
            self.last_rec_id +=1

        self.rec = self.recorder.open(file_name)
        self.rec.start_recording()
        self.toggle_rec_dot(True)

        with open("user_data/{}".format(self.curr_user), "a+") as fp:
            fp.write("['{}', '{}']\n".format(self.rec_file_name, self.txt[self.text_id]))
        # print(self.txt[self.text_id])
        self.change_text( str(self.txt[self.text_id]) )
        self.text_id += 1
  
    
    def change_text(self, text):
        self.text_to_read = text
        self.prog_indic = "{}/{}".format(self.text_id+1,len(self.txt))

        # disable "1 foward" button in case no new records are ahead
        if self.text_id + 1 >= self.last_rec_id:
            self.ids["1_foward"].disabled = True
        else:
            self.ids["1_foward"].disabled = False


    # playback the audio file of currrent text
    def playback_rec(self):
        if self.rec is not None:
            self.rec.stop_recording()
            self.rec.close()
            self.rec = None
            self.toggle_rec_dot(False)
        file_name = "recordings/{}".format(self.rec_file_name)
        if path.exists(file_name):
            self.rec = self.recorder.open(file_name, mode="rb")
            self.rec.playback_file()
        else:
            pass
        
    # Record the current text again (overrides the previous entry)
    def redo_rec(self):
        if self.rec is not None:
            self.rec.stop_recording()
            self.rec.close()
            self.rec = None
            self.toggle_rec_dot(False)
            
        # curr_user, code = self.return_user_data()
        self.rec_file_name = "{}_{}.wav".format(self.code, str(self.text_id - 1).zfill(5))
        self.rec = self.recorder.open(str("recordings/"+self.rec_file_name))
        self.rec.start_recording()
        self.toggle_rec_dot(True)

    # Display the previous text
    def one_text_back(self):
        if (self.text_id - 1) < 0:
            self.text_id = 0
        else:
            self.text_id -= 1

        if self.rec is not None:
            self.rec.stop_recording()
            self.rec.close()
            self.rec = None
            self.toggle_rec_dot(False)

        self.change_text( str(self.txt[self.text_id]) )
        self.rec_file_name = "{}_{}.wav".format(self.code, str(self.text_id).zfill(5))

    # Display the next text
    def one_text_foward(self):
        if self.text_id > len(self.txt):
            print("konec!")
            self.fp.close()
        else:
            self.text_id += 1

        self.change_text( str(self.txt[self.text_id]) )
        self.rec_file_name = "{}_{}.wav".format(self.code, str(self.text_id).zfill(5))
        # self.next_recording()
    
    def enable_keyboard(self, value):
        self.enable_keyboard_flag = value

    def toggle_rec_dot(self, value):
        if value:
            self.ids["rec_circle_img"].size_hint = (0.05, 0.05)
            print("Light ON")
        else:
            self.ids["rec_circle_img"].size_hint = (0.05, 0.0)
            print("Light OFF")
            file_name = "recordings/{}".format(self.rec_file_name)
            file_name_trimmed = "recordings/trimmed/{}".format(self.rec_file_name)
            audio_trimmed = trim_and_silence_audio_file(file_name)
            audio_trimmed.export(file_name_trimmed, format="wav")
    
    def return_button_clicked(self):
        if self.rec is not None:
            self.rec.stop_recording()
            self.rec.close()
            self.rec = None
            self.toggle_rec_dot(False)
    
class UserDataScreen(Screen):
    # TODO: dodaj handlanje neizpoljenih obrazcev (popups) in shranjevanje v datoteke z drugačnimi imeni
    male = ObjectProperty(False)
    female = ObjectProperty(False)
    font_size_ui = ObjectProperty(32)

    def __init__(self, **kwargs):
        super(UserDataScreen, self).__init__(**kwargs)

        settings = read_settings_file()
        self.font_size_ui = int(settings[2])
    
    def on_enter(self, *args):
        settings = read_settings_file()
        self.font_size_ui = int(settings[2])

    def sex_clicked(self, instance, value):
        if value is True:
            self.male = True
            self.female = False
        else:
            self.male = False
            self.female = True
        print("Male: {}   Female {} ".format(self.male, self.female ))
        

    def spinner_clicked(self, text):
        print(text)
    
    def save_user_data(self, name, surname, code, region):
        name.replace(" ", "")
        surname.replace(" ", "")
        code.replace(" ", "")
        print("Male: {}   Female {} ".format(self.male, self.female ))
        print("Name: {}   Surname: {}    Code: {}   Region: {}".format(name, surname, code, region))
        user_data_filename = "{}{}{}.txt".format(name, surname, code)

        if self.male is True:
            sex = "m"
        else:
            sex = "z"

        data = 'Ime: {}\nPriimek: {}\nSpol: {}\nRegija: {}\nKoda: {}\n'.format(name, surname, sex, region, code)
        f = open("user_data/{}".format(user_data_filename), "w")
        f.write(data)
        f.close()
        
        # Save who is the current subject to temp folder
        f = open("temp/curr_user_data.txt", "w")
        f.write("{}\n".format(user_data_filename))
        f.write(data)
    

class SettingScreen(Screen):
    in_dev = ObjectProperty([""])
    out_dev = ObjectProperty([""])
    font_sizes = ObjectProperty([""])
    font_size_ui = ObjectProperty(72)

    def_in_dev = StringProperty()
    def_out_dev = StringProperty()
    def_font_size = StringProperty()

    output_devices = []
    input_devices = []
    pSetting = PyAduioSettings()

    rec_time = 3
    recorder = Recorder()
    rec = None
    timer = None

    def __init__(self, **kwargs):
        super(SettingScreen, self).__init__(**kwargs)
        
        self.output_devices = self.pSetting.return_output_devices()
        self.input_devices = self.pSetting.return_input_devices()

        # If settings file does not exist, create it and set input/output device to default
        if not os.path.isfile('temp/settings.txt'):
            def_in = self.pSetting.find_default_device(self.input_devices)
            def_out = self.pSetting.find_default_device(self.output_devices)
            
            f = open("temp/settings.txt", "w")
            f.write("out_dev: {}\nin_dev: {}\nfont_size: {}\nnum_of_channels: {}\nsamp_rate: {}".format(def_in, def_out, 32, 1, 44100))
            f.close()

            def_settings = read_settings_file()
            
            self.def_out_dev = self.pSetting.find_device_by_number(self.output_devices, def_settings[0])
            self.def_in_dev = self.pSetting.find_device_by_number(self.input_devices, def_settings[1])
            self.def_font_size = def_settings[2]

        # If a settings file exists, set the settings value to the values in file
        else:
            def_settings = read_settings_file()

            self.def_out_dev = self.pSetting.find_device_by_number(self.output_devices, def_settings[0])
            self.def_in_dev = self.pSetting.find_device_by_number(self.input_devices, def_settings[1])
            self.def_font_size = def_settings[2]

        # Create list of input and output devices
        self.in_dev = [i[0] for i in self.input_devices]
        self.out_dev = [i[0] for i in self.output_devices]
        
        # Create list of font sizes, input channels and sampling rates
        self.font_sizes = ["8", "9", "10", "11", "12", "14", "18", "24", "30", "36", "48", "60", "72", "96"]
        num_of_channels = 1
        samp_rate = 44100
        
    def spinner_clicked(self, setting, value):
        self.edit_settings_file(setting, value)
    
    def edit_settings_file(self, setting, value):
        f = open("temp/settings.txt", "r")
        lines = f.readlines()
        if setting == "output_dev":
            line = lines[0]
            idx = line.find(":")
            line = line[:idx+2] 

            txt = self.pSetting.find_number_by_device( self.output_devices, str(value) )
            if txt >= 0:
                line += str(txt)
            else:
                line += self.pSetting.find_default_device(self.output_devices)
            line += "\n"
            lines[0] = line

        elif setting == "input_dev":
            line = lines[1]
            idx = line.find(":")
            line = line[:idx+2]
            
            txt = self.pSetting.find_number_by_device( self.input_devices, str(value) )
            if txt >= 0:
                line += str(txt)
            else:
                line += self.pSetting.find_default_device(self.input_devices)

            line += "\n"
            lines[1] = line

        elif setting == "font_size":
            line = lines[2]
            idx = line.find(":")
            line = line[:idx+2]
            line += str(value)
            line += "\n"
            lines[2] = line

            # Change the font size
            print(value)
            self.font_size_ui = int(value)

        f.close()
        f = open("temp/settings.txt", "w") 
        for line in lines:
            f.write(line)
            # print(line)
        f.close()

    # Function that records user audio for n seconds and than replays the recording
    def timer_callback(self):
        self.rec.stop_recording()
        self.rec.close()
        self.toggle_rec_dot(False)

        self.rec = self.recorder.open("temp/test.wav", mode="rb")
        self.rec.playback_file()
        self.timer = threading.Timer(self.rec_time, self.timer_callback_close)
        self.timer.start()
    
    def timer_callback_close(self):
        self.rec.close()
        self.timer = None

    def test_audio(self):
        if self.rec is not None:
            self.rec.close()
        
        if self.timer is not None:
            self.timer.cancel()
            self.rec.close()

        self.rec = self.recorder.open("temp/test.wav")
        self.rec.start_recording()
        self.toggle_rec_dot(True)
        self.timer = threading.Timer(self.rec_time, self.timer_callback)
        self.timer.start()

    def toggle_rec_dot(self, value):
        if value:
            self.ids["rec_circle_img"].size_hint = (0.05, 0.05)
            print("Light ON")
        else:
            self.ids["rec_circle_img"].size_hint = (0.05, 0.0)
            print("Light OFF")

    def return_button_clicked(self):
        if self.rec is not None:
            self.rec.stop_recording()
            self.rec.close()
            self.timer.cancel()
            self.toggle_rec_dot(False)


# class TestingScreen(Screen):
#     # TODO: Dodaj vizualizacijo zvočnega posnetka - razvidno mora biti ali je glas dovolj jasen in glasen
#     rec_time = 3
#     recorder = Recorder()
#     rec = None
#     timer = None

#     # Function that records user audio for n seconds and than replays the recording
#     def timer_callback(self):
#         self.rec.stop_recording()
#         self.rec.close()
#         self.toggle_rec_dot(False)

#         self.rec = self.recorder.open("temp/test.wav", mode="rb")
#         self.rec.playback_file()
#         self.timer = threading.Timer(self.rec_time, self.timer_callback_close)
#         self.timer.start()
    
#     def timer_callback_close(self):
#         self.rec.close()
#         self.timer = None

#     def test_audio(self):
#         if self.rec is not None:
#             self.rec.close()
        
#         if self.timer is not None:
#             self.timer.cancel()
#             self.rec.close()

#         self.rec = self.recorder.open("temp/test.wav")
#         self.rec.start_recording()
#         self.toggle_rec_dot(True)
#         self.timer = threading.Timer(self.rec_time, self.timer_callback)
#         self.timer.start()

#     def toggle_rec_dot(self, value):
#         if value:
#             self.ids["rec_circle_img"].size_hint = (0.05, 0.05)
#             print("Light ON")
#         else:
#             self.ids["rec_circle_img"].size_hint = (0.05, 0.0)
#             print("Light OFF")

#     def return_button_clicked(self):
#         if self.rec is not None:
#             self.rec.stop_recording()
#             self.rec.close()
#             self.timer.cancel()
#             self.toggle_rec_dot(False)

class AboutScreen(Screen):
    pass

# Screen manager for managing changin screens
screen_manager = ScreenManager()

screen_manager.add_widget(StartLayout(name="start_screen"))
screen_manager.add_widget(RecordScreen(name="record_screen"))
screen_manager.add_widget(SettingScreen(name="settings_screen"))
# screen_manager.add_widget(TestingScreen(name="testing_screen"))
screen_manager.add_widget(AboutScreen(name="about_screen"))
screen_manager.add_widget(UserDataScreen(name="user_data_screen"))



class VoiceRecorderApp(App):   
    font_size = 32
    def build(self):
        Window.clearcolor = (1,1,1,1)
        return screen_manager

if __name__ == '__main__':
    VoiceRecorderApp().run()
    
    