import kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen

from recorder import Recorder

import threading

Builder.load_file('voicerecorder.kv')


# Set app size
# Window.size = (500, 700)

class StartLayout(Screen):
    pass
    # recorder = Recorder()
    # rec = recorder.open("test.wav")

    # def test(self):
    #     print("Ammm what?")

    # def start_recording(self):
    #     print("Snemaj!")
    #     self.rec.start_recording()

    # def stop_recording(self):
    #     print("NEHI snemat")
    #     self.rec.stop_recording()
    # rec = Recorder()

class RecordScreen(Screen):
    # Create Recorder object
    recorder = Recorder()
    rec = None

    # Read user code from file
    fp = open("user_data/user_data.txt")
    t = fp.read()
    t = t.split()
    code = t[-1]
    print(code)
    fp.close()

    with open("user_data/user_data.txt", "a") as fp:
        fp.write("Imena posnetkov:\n")

    text_id = 0
    txt = []
    f = open("text/text.txt")
    for i, line in enumerate(f):
        txt.append(line[0:-1])
    f.close()

    text_to_read = "Pritisnite gumb 'Naslednji' (enter/space) in pričnite brati tekst na ekranu"

    def next_recording(self):
        if self.text_id > len(self.txt):
            print("konec!")
            self.fp.close()

        if self.rec is not None:
            self.rec.stop_recording()
            self.rec.close()
        
        file_name = "{}_{}.wav".format(self.code, str(self.text_id).zfill(5))
        self.rec = self.recorder.open(str("recordings/"+file_name))
        self.rec.start_recording()
        with open("user_data/user_data.txt", "a") as self.fp:
            self.fp.write("['{}', '{}']\n".format(file_name, self.txt[self.text_id]))
        # print(self.txt[self.text_id])
        self.text_to_read = str(self.txt[self.text_id])
        self.text_id += 1
        
    
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

        if self.male is True:
            sex = "m"
        else:
            sex = "z"

        data = 'Ime: {}\nPriimek: {}\nSpol: {}\nRegija: {}\nKoda: {}\n'.format(name, surname, sex, region, code)
        f = open("user_data/user_data.txt", "w")
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
    
    