## voice_recorder
A simple Python voice recording program for database generation inspired by [ProRec](https://www.phon.ucl.ac.uk/resource/prorec/).

The GUI is made using the cross platform Python framework [Kivy](https://kivy.org/#home) (v1.11.1). For the sound recording and playback the latest version of the Python library [pyAudio](https://pypi.org/project/PyAudio/) was used. 

The software was developed for a seminar project at my university. The main goal of the software is to simplify the process of recording speech for a speech recognition application. The text that the user has to read is stored in `.xlsx` files in the `test` folder.

Recorded audio is stored in `wav` files in the `recordings` folder. Inside is another folder called `trimmed` that containes the same audio files but with silence removed from the front and back. The audio is recorded at 44.1kHz mono with 16bit sampling.


As you may note, the text is writen in slovene language. That is because the software was meant for Slovenian users. Changing the language would simply mean changing the text of the labels inside the `scripts/voicerecorder_layout.kv` file.

![alt text](https://github.com/UrbanBobek/voice_recorder/blob/main/images/start.png?raw=true)

![alt text](https://github.com/UrbanBobek/voice_recorder/blob/main/images/data.png?raw=true)

![alt text](https://github.com/UrbanBobek/voice_recorder/blob/main/images/info.png?raw=true)

![alt text](https://github.com/UrbanBobek/voice_recorder/blob/main/images/text.png?raw=true)
