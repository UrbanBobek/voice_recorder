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
    pass
    
class SettingScreen(Screen):
    pass

class TestingScreen(Screen):
    # TODO: Dodaj vizualizacijo zvočnega posnetka - razvidno mora biti ali je glas dovolj jasen in glasen
    rec_time = 3
    recorder = Recorder()
    rec = None
    timer = None
    # def __init__(self, rec_time=3):
    #     self.rec_time = rec_time
    #     self.recorder = Recorder()
    #     self.rec = None
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



class VoiceRecorderApp(App):   
    font_size = 32
    def build(self):
        Window.clearcolor = (1,1,1,1)
        return screen_manager

if __name__ == '__main__':
    VoiceRecorderApp().run()
    
    