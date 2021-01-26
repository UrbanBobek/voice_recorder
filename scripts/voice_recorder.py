import kivy
from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, StringProperty
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout

from recorder import Recorder
from py_audio_settings import PyAduioSettings
from utils import *

import threading
import mute_alsa

import os.path
from os import path

Builder.load_file('voicerecorder_layout.kv')


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
    settings = read_settings_file()
    rec = recorder.open("../temp/test.wav", channels=1, rate=44100, input_dev=int(settings[1]))
    timer = None

    def __init__(self, **kwargs):
        super(SettingScreen, self).__init__(**kwargs)
        
        self.output_devices = self.pSetting.return_output_devices()
        self.input_devices = self.pSetting.return_input_devices()

        # If settings file does not exist, create it and set input/output device to default
        if not os.path.isfile('../temp/settings.txt'):
            def_in = self.pSetting.find_default_device(self.input_devices, 1)
            def_out = self.pSetting.find_default_device(self.output_devices, 1)
            
            f = open("../temp/settings.txt", "w")
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
        self.font_sizes = ["8", "9", "10", "11", "12", "14", "18", "24", "30", "36", "48", "60"]
        num_of_channels = 1
        samp_rate = 44100
    
    def on_enter(self):
        self.pSetting = PyAduioSettings()
        self.recorder = Recorder()
        self.settings = read_settings_file()
        self.rec = self.recorder.open("../temp/test.wav", channels=1, rate=44100, input_dev=int(self.settings[1]))

    def spinner_clicked(self, setting, value):
        self.edit_settings_file(setting, value)
    
    def edit_settings_file(self, setting, value):
        f = open("../temp/settings.txt", "r")
        lines = f.readlines()
        if setting == "output_dev":
            line = lines[0]
            idx = line.find(":")
            line = line[:idx+2] 

            txt = self.pSetting.find_number_by_device( self.output_devices, str(value) )
            if txt >= 0:
                line += str(txt)
            else:
                line += self.pSetting.find_default_device(self.output_devices,1)
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
                line += self.pSetting.find_default_device(self.input_devices, 1)

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
            self.font_size_ui = int(value)

        f.close()
        f = open("../temp/settings.txt", "w") 
        for line in lines:
            f.write(line)
        f.close()

    # Function that records user audio for n seconds and than replays the recording
    def timer_callback(self):
        self.rec.stop_recording()
        self.rec.close()
        self.toggle_rec_dot(False)
        
        sett = read_settings_file()
        self.rec = self.recorder.open("../temp/test.wav", mode="rb", output_dev=int(sett[0]))
        self.rec.playback_file()
        self.timer = threading.Timer(self.rec_time, self.timer_callback_close)
        self.timer.start()
    
    def timer_callback_close(self):
        self.rec.close()
        self.timer = None

    def test_audio(self):
        if self.rec._stream is not None:
            self.rec.close()
        
        if self.timer is not None:
            self.timer.cancel()
            self.rec.close()
        
        settings = read_settings_file()
        self.rec = self.recorder.open("../temp/test.wav", channels=1, rate=44100, input_dev=int(self.settings[1]) )
        self.rec.start_recording()
        self.toggle_rec_dot(True)
        self.timer = threading.Timer(self.rec_time, self.timer_callback)
        self.timer.start()

    def toggle_rec_dot(self, value):
        if value:
            self.ids["rec_circle_img"].size_hint = (0.05, 0.05)
            # print("Light ON")
        else:
            self.ids["rec_circle_img"].size_hint = (0.05, 0.0)
            # print("Light OFF")

    def return_button_clicked(self):
        if self.rec is not None:
            self.rec.stop_recording()
            self.rec.close()
            self.timer.cancel()
            self.toggle_rec_dot(False)



class StartLayout(Screen):
    font_size_ui = ObjectProperty(32)

    print(Window.size)
    def __init__(self, **kwargs):
        super(StartLayout, self).__init__(**kwargs)

        settings = read_settings_file()
        self.font_size_ui = int(settings[2])
    
    def on_enter(self, *args):
        settings = read_settings_file()
        self.font_size_ui = int(settings[2])
    
    def can_continue(self):
        curr_user, code = return_user_data()

        if path.exists("../user_data/{}".format(curr_user)):
            screen_manager.transition.direction = 'left'
            screen_manager.current = "record_screen"
        else:
            self.show_popup("Datoteke ni na voljo")
    
    class Pop_up(Popup):
        settings = read_settings_file()
        font_size_ui = int(settings[2])
        f_size_ui = ObjectProperty(font_size_ui)
        pass

    def show_popup(self, txt):
        the_popup = self.Pop_up()
        the_popup.title = txt
        the_popup.open()


class RecordScreen(Screen):
    # TODO: spremeni, da je ime datoteke s tekstom koda govorca 
    next_rec = ObjectProperty(None)
    text_to_read = StringProperty()
    prog_indic = StringProperty()
    font_size_ui = ObjectProperty(32)
    redo_text = StringProperty()
    next_text = StringProperty()
    playback_text = StringProperty()
    back_text = StringProperty()
    foward_text = StringProperty()

    # Create Recorder object
    recorder = Recorder()
    rec = None

    # Read user settings
    settings = read_settings_file()

    def __init__(self, **kwargs):
        super(RecordScreen, self).__init__(**kwargs)
        Window.bind(on_key_down=self._on_keyboard_down)
        Window.bind(on_key_up=self._on_keyboard_up)
        self.rec_file_name = "initial_file_name"
        self.txt = []
        self.text_id = 0
        self.last_rec_id = 0
        self.enable_keyboard_flag = False
        self.pause_ended = False
        self.show_tutorial = True

        settings = read_settings_file()
        self.font_size_ui = int(settings[2])

    def on_enter(self, *args):
        self.enable_keyboard(True)

        self.curr_user, self.code = return_user_data()
        f = open("../user_data/{}".format(self.curr_user))
        file_data = f.readlines()

        # Store text lines to read
        if not self.code == -1:
            self.txt = return_text_from_xlsx("../text/{}.xlsx".format(self.code)) 
        else:
            self.txt = []
        # self.txt = return_text_from_xlsx("../text/Artur-B-G0042.xlsx") 
        
        # print(len(file_data))

        if len(file_data) > 5:
            self.text_to_read = self.txt[len(file_data)-5]
            self.text_id = len(file_data)-5
            self.last_rec_id = len(file_data)-5

            self.next_text = ""
            self.redo_text = ""
            self.playback_text = ""
            self.back_text = ""
            self.foward_text = ""
            self.show_tutorial = False
            
        else:
            self.text_to_read = "[i]Pritisnite gumb 'Naslednji' in pričnite brati tekst na ekranu [/i]"
            self.text_id = 0
            self.last_rec_id = 0

            # tutorial text
            self.next_text = "naslednji tekst\n([i]space/enter[/i])"
            self.redo_text = "ponovi snemanje\n([i]lctrl[/i])"
            self.playback_text = u"poslušaj posnetek\n([i]gor[/i])"
            self.back_text = "1 tekst nazaj\n([i]levo[/i])"
            self.foward_text = "1 tekst naprej\n([i]desno[/i])"
            self.show_tutorial = True

        # self.prog_indic = "0/{}".format(len(self.txt))
        self.prog_indic = "0/{}".format(10)
        self.key_up = True

        self.settings = read_settings_file()
        self.font_size_ui = int(self.settings[2])

        self.pause_ended = True

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


    def next_recording(self):
        # Check if there is any more text to read - if not, display the end screen
        if self.text_id >= len(self.txt):
            screen_manager.current = "end_screen"
            return 1
        
        # print(self.text_id)
        if self.show_tutorial:
            self.next_text = ""
            self.redo_text = ""
            self.playback_text = ""
            self.back_text = ""
            self.foward_text = ""
            self.show_tutorial = False

        if self.rec is not None:
            self.rec.stop_recording()
            self.rec.close()
            self.rec = None
            self.toggle_rec_dot(False)
        
        if (self.text_id)%10 or self.pause_ended:
            if (self.text_id)%10:
                self.pause_ended = False

            self.curr_user, self.code = return_user_data()
            self.rec_file_name = "{}_{}.wav".format(self.code, str(self.text_id).zfill(5))

            # Check if recording already exists
            file_name = "../recordings/{}".format(self.rec_file_name)
            if not path.exists(file_name):
                self.last_rec_id +=1
                with open("../user_data/{}".format(self.curr_user), "a+") as fp:
                    fp.write("['{}', '{}']\n".format(self.rec_file_name, self.txt[self.text_id]))

            self.rec = self.recorder.open(file_name, channels=1, rate=44100, input_dev=int(self.settings[1]))
            self.rec.start_recording()
            self.toggle_rec_dot(True)

            # print(self.txt[self.text_id])
            self.change_text( str(self.txt[self.text_id]) )
            self.text_id += 1
        else:
            screen_manager.transition.direction = 'left'
            screen_manager.current = "pause_screen"
            
  
    
    def change_text(self, text):
        
        self.text_to_read = text
        # self.prog_indic = "{}/{}".format(self.text_id+1,len(self.txt))
        self.prog_indic = "{}/{}".format((self.text_id)%10+1,10)

        # disable "1 foward" button in case no new records are ahead
        if self.text_id + 1 >= self.last_rec_id:
            self.ids["1_foward"].disabled = True
            self.ids["checkmark_img"].size_hint = (0.0, 0.05)
        else:
            self.ids["1_foward"].disabled = False
            self.ids["checkmark_img"].size_hint = (0.06, 0.06)



    # playback the audio file of currrent text
    def playback_rec(self):
        if self.rec is not None:
            self.rec.stop_recording()
            self.rec.close()
            self.rec = None
            self.toggle_rec_dot(False)
        file_name = "../recordings/{}".format(self.rec_file_name)
        if path.exists(file_name):
            settings = read_settings_file()
            self.rec = self.recorder.open(file_name, mode="rb", channels=1, rate=44100, output_dev=int(self.settings[0]))
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
        self.rec = self.recorder.open(str("../recordings/"+self.rec_file_name), channels=1, rate=44100, input_dev=int(self.settings[1]))
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
    
    def enable_keyboard(self, value):
        self.enable_keyboard_flag = value

    def toggle_rec_dot(self, value):
        if value:
            self.ids["rec_circle_img"].size_hint = (0.05, 0.05)
            # print("Light ON")
        else:
            self.ids["rec_circle_img"].size_hint = (0.05, 0.0)
            # print("Light OFF")
            file_name = "../recordings/{}".format(self.rec_file_name)
            file_name_trimmed = "../recordings/trimmed/{}".format(self.rec_file_name)
            audio_trimmed = trim_and_silence_audio_file(file_name)
            audio_trimmed.export(file_name_trimmed, format="wav")
    
    def return_button_clicked(self):
        if self.rec is not None:
            self.rec.stop_recording()
            self.rec.close()
            self.rec = None
            self.toggle_rec_dot(False)
    
class PauseScreen(Screen):
    font_size_ui = ObjectProperty(32)
    progress = ObjectProperty(0)

    curr_user, code = return_user_data()
    if not code == -1:
        txt = return_text_from_xlsx("../text/{}.xlsx".format(code)) 
    else:
        txt = []
    # txt = return_text_from_xlsx("../text/Artur-B-G0042.xlsx") 

    def on_enter(self):
        settings = read_settings_file()
        self.font_size_ui = int(settings[2])

        curr_user, code = return_user_data()
        f = open("../user_data/{}".format(curr_user))
        file_data = f.readlines()
        if len(file_data) > 5:
            text_id = len(file_data)-5
            self.progress = float(text_id+1)/len(self.txt)*100

class UserDataScreen(Screen):
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

    def sex_clicked(self, instance, value, sex):
        if value is True:
            if sex == "m":
                self.male = True
                self.female = False
            elif sex == "z":
                self.male = False
                self.female = True
        else:
            self.male = False
            self.female = True
        
    def spinner_clicked(self, text):
        pass
    
    def save_user_data(self, name, surname, code, region):
        # Remove empty spaces
        name.replace(" ", "")
        surname.replace(" ", "")
        code.replace(" ", "")

        user_data_filename = "{}{}{}.txt".format(name, surname, code)
        
        sex = ""
        if self.male is True:
            sex = "m"
        elif self.female is True:
            sex = "z"
        
        # Check if all the data was submited by user - if not, show a popup screen
        all_data_submited = True
        if not self.male and not self.female:
            popup_text = "Manjka spol" 
            all_data_submited = False
        if region == "Izberi regijo":
            popup_text = "Manjka regija" 
            all_data_submited = False
        if not code:
            popup_text = "Manjka koda"
            all_data_submited = False 
        if not surname:
            popup_text = "Manjka priimek"
            all_data_submited = False
        if not name:
            popup_text = "Manjka ime"
            all_data_submited = False 
        # Check if the code is valid:
        if not path.exists("../text/{}.xlsx".format(code)):
            popup_text = "Koda ni veljavna"
            all_data_submited = False 

        # Uncomment this for the code to work
        # all_data_submited = True 
        
        if all_data_submited:
            data = 'Ime: {}\nPriimek: {}\nSpol: {}\nRegija: {}\nKoda: {}\n'.format(name, surname, sex, region, code)
            f = open("../user_data/{}".format(user_data_filename), "w")
            f.write(data)
            f.close()
        
            # Save who is the current subject to temp folder
            f = open("../temp/curr_user_data.txt", "w")
            f.write("{}\n".format(user_data_filename))
            f.write(data)
            
            # Go to record screen
            screen_manager.transition.direction = 'left'
            screen_manager.current = "record_screen"
        else:
            self.show_popup(popup_text)
        
    
    class Pop_up(Popup):
        settings = read_settings_file()
        font_size_ui = int(settings[2])
        f_size_ui = ObjectProperty(font_size_ui)
        pass

    def show_popup(self, txt):
        the_popup = self.Pop_up()
        the_popup.title = txt
        the_popup.open()
    


class AboutScreen(Screen):
    font_size_ui = ObjectProperty(32)

    def __init__(self, **kwargs):
        super(AboutScreen, self).__init__(**kwargs)

        settings = read_settings_file()
        self.font_size_ui = int(settings[2])

    pass
class EndScreen(Screen):
    font_size_ui = ObjectProperty(32)

    def __init__(self, **kwargs):
        super(EndScreen, self).__init__(**kwargs)

        settings = read_settings_file()
        self.font_size_ui = int(settings[2])

    pass

# Screen manager for managing changin screens
screen_manager = ScreenManager()

screen_manager.add_widget(StartLayout(name="start_screen"))
screen_manager.add_widget(SettingScreen(name="settings_screen"))
screen_manager.add_widget(RecordScreen(name="record_screen"))
screen_manager.add_widget(PauseScreen(name="pause_screen"))
screen_manager.add_widget(AboutScreen(name="about_screen"))
screen_manager.add_widget(UserDataScreen(name="user_data_screen"))
screen_manager.add_widget(EndScreen(name="end_screen"))



class VoiceRecorderApp(App):   
    def build(self):  
        Window.clearcolor = (1,1,1,1)
        return screen_manager

if __name__ == '__main__':
    VoiceRecorderApp().run()
    
    