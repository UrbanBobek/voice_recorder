from pydub import AudioSegment,silence
import pyaudio
import wave


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

# Returns the time of the begging and end of periods of silence in milliseconds
def return_silence_start_and_stop(filename):
    myaudio = intro = AudioSegment.from_wav(filename) 
    song_duration = round(myaudio.duration_seconds*1000)
    dBFS=myaudio.dBFS
    sil = silence.detect_silence(myaudio, min_silence_len=500, silence_thresh=dBFS-16)

    sil = [((start),(stop)) for start,stop in sil] #in millisec
    # print(sil)
    if len(sil) > 2:
        sil = [sil[0], sil[-1]]

    # handle exceptions:
    if len(sil) == 1:
        # The silence in in the begging or in the middle of the audio file
        if sil[0][1] < song_duration:
            sil = [sil[0], (song_duration, song_duration)]
        else:
            sil = [(0,0),sil[0]]

    if len(sil) == 0:
        sil = [(0,0), (song_duration, song_duration)]

    print(sil)
    padding = 200 # milliseconds
    if sil[0][1] > padding:
        sil[0] = (sil[0][0], sil[0][1] - padding)
    if sil[1][0] < (song_duration - padding):
        sil[1] = (sil[1][0] + padding, sil[1][1])
    print(sil)
    return sil

def trim_and_silence_audio_file(filename):
    trim_time = return_silence_start_and_stop(filename)
    audio = AudioSegment.from_wav(filename)
    audio_trimmed = audio[trim_time[0][1]:trim_time[1][0]]
    silent_audio = AudioSegment.silent(duration=300) # 500 milliseconds of silence
    audio_trimmed = silent_audio + audio_trimmed + silent_audio

    return audio_trimmed

audio_trimmed = trim_and_silence_audio_file("recordings/trimmed/69_00002.wav")
audio_trimmed.export("test.wav", format="wav")
