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

import threading
import mute_alsa

import os.path
from os import path

Builder.load_file('voicerecorder.kv')


# Set app size
# Window.size = (500, 700)

class StartLayout(Screen):
    pass


class RecordScreen(Screen):
    # TODO: dodaj kolko je še za prebrat, dodaj lucko ki nakaže ali se snema ali ne, disable-aj next button če naprej še ni posneto, polepšaj zadeve
    next_rec = ObjectProperty(None)
    text_to_read = StringProperty()

    # Create Recorder object
    recorder = Recorder()
    rec = None

    txt = []
    # Store text lines to read
    f = open("text/text.txt")
    for i, line in enumerate(f):
        txt.append(line[0:-1])
    f.close()
    

    def __init__(self, **kwargs):
        super(RecordScreen, self).__init__(**kwargs)
        Window.bind(on_key_down=self._on_keyboard_down)
        self.rec_file_name = ""
        self.text_id = 0
        self.last_rec_id = 0

        self.enable_keyboard_flag = False

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

    def on_leave(self, *args):
        self.enable_keyboard(False)

    # Button shortcuts
    def _on_keyboard_down(self, instance, keyboard, keycode, text, modifiers):
        # print(keycode)
        if self.enable_keyboard_flag:
            if  keycode == 40 or keycode == 44:  # 40 - Enter key pressed, 44 - spacebar, 79 - right arrow key
                self.next_recording()
            if  keycode == 82:  # 82 - up key
                self.playback_rec()
            if  keycode == 79:  # 79 - right arrow key
                self.one_text_foward()
            if  keycode == 80:  # 80 - left key
                self.one_text_back()
            if  keycode == 224:  # 224 - lctrl
                self.redo_rec()

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

        self.curr_user, self.code = self.return_user_data()
        self.rec_file_name = "{}_{}.wav".format(self.code, str(self.text_id).zfill(5))

        # Chech if recording already exists
        file_name = "recordings/{}".format(self.rec_file_name)
        if not path.exists(file_name):
            self.last_rec_id +=1

        self.rec = self.recorder.open(file_name)
        self.rec.start_recording()

        with open("user_data/{}".format(self.curr_user), "a+") as fp:
            fp.write("['{}', '{}']\n".format(self.rec_file_name, self.txt[self.text_id]))
        # print(self.txt[self.text_id])
        self.text_to_read = str(self.txt[self.text_id])
        self.text_id += 1

        print("text id: {}    las rec id: {}".format(self.text_id, self.last_rec_id))
        
    # playback the audio file of currrent text
    def playback_rec(self):
        # TODO: preveri, če posnetek obstaja
        if self.rec is not None:
            self.rec.stop_recording()
            self.rec.close()
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
            
        # curr_user, code = self.return_user_data()
        self.rec_file_name = "{}_{}.wav".format(self.code, str(self.text_id - 1).zfill(5))
        self.rec = self.recorder.open(str("recordings/"+self.rec_file_name))
        self.rec.start_recording()

    # Display the previous text
    def one_text_back(self):
        if (self.text_id - 2) < 0:
            self.text_id = 0
        else:
            self.text_id -= 2

        self.text_to_read = str(self.txt[self.text_id])
        self.rec_file_name = "{}_{}.wav".format(self.code, str(self.text_id).zfill(5))

    # Display the next text
    def one_text_foward(self):
        if self.text_id > len(self.txt):
            print("konec!")
            self.fp.close()
        else:
            self.text_id += 1

        self.text_to_read = str(self.txt[self.text_id])
        self.rec_file_name = "{}_{}.wav".format(self.code, str(self.text_id).zfill(5))
        # self.next_recording()
    
    def enable_keyboard(self, value):
        self.enable_keyboard_flag = value
    
class UserDataScreen(Screen):
    # TODO: dodaj handlanje neizpoljenih obrazcev (popups) in shranjevanje v datoteke z drugačnimi imeni
    male = ObjectProperty(False)
    female = ObjectProperty(False)

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
    pass

class TestingScreen(Screen):
    # TODO: Dodaj vizualizacijo zvočnega posnetka - razvidno mora biti ali je glas dovolj jasen in glasen
    rec_time = 3
    recorder = Recorder()
    rec = None
    timer = None

    # Function that records user audio for n seconds and than replays the recording
    def timer_callback(self):
        self.rec.stop_recording()
        self.rec.close()

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
        self.timer = threading.Timer(self.rec_time, self.timer_callback)
        self.timer.start()

    

class AboutScreen(Screen):
    pass

# Screen manager for managing changin screens
screen_manager = ScreenManager()

screen_manager.add_widget(StartLayout(name="start_screen"))
screen_manager.add_widget(RecordScreen(name="record_screen"))
screen_manager.add_widget(SettingScreen(name="settings_screen"))
screen_manager.add_widget(TestingScreen(name="testing_screen"))
screen_manager.add_widget(AboutScreen(name="about_screen"))
screen_manager.add_widget(UserDataScreen(name="user_data_screen"))



class VoiceRecorderApp(App):   
    font_size = 32
    def build(self):
        Window.clearcolor = (1,1,1,1)
        return screen_manager

if __name__ == '__main__':
    VoiceRecorderApp().run()
    
    