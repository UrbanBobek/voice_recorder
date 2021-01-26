import pyaudio
import wave
class Recorder(object):
    '''A recorder class for recording audio to a WAV file.
    Records in mono by default.
    '''

    def __init__(self, channels=1, rate=44100, frames_per_buffer=1024):
        self.channels = channels
        self.rate = rate
        self.frames_per_buffer = frames_per_buffer

    def open(self, fname, mode='wb', channels = 1, rate = 44100, input_dev = 0, output_dev = 0):
        channels = self.channels
        rate = self.rate
        return RecordingFile(fname, mode, channels, rate,
                            self.frames_per_buffer, input_dev, output_dev)

class RecordingFile(object):
    def __init__(self, fname, mode, channels, 
                rate, frames_per_buffer, input_dev, output_dev):
        self.fname = fname
        self.mode = mode
        self.channels = channels
        self.rate = rate
        self.frames_per_buffer = frames_per_buffer
        self._pa = pyaudio.PyAudio()
        self.wavefile = self._prepare_file(self.fname, self.mode)
        self._stream = None
        self.input_dev = input_dev
        self.output_dev = output_dev
        # print("Input device index: {}".format(self.input_dev))

    def __enter__(self):
        return self

    def __exit__(self, exception, value, traceback):
        self.close()

    def record(self, duration):
        # Use a stream with no callback function in blocking mode
        self._stream = self._pa.open(format=pyaudio.paInt16,
                                        channels=self.channels,
                                        rate=self.rate,
                                        input=True,
                                        frames_per_buffer=self.frames_per_buffer,
                                        input_device_index=self.input_dev)
        for _ in range(int(self.rate / self.frames_per_buffer * duration)):
            audio = self._stream.read(self.frames_per_buffer)
            self.wavefile.writeframes(audio)
        return None

    def start_recording(self):
        # Use a stream with a callback in non-blocking mode
        self._stream = self._pa.open(format=pyaudio.paInt16,
                                        channels=self.channels,
                                        rate=self.rate,
                                        input=True,
                                        frames_per_buffer=self.frames_per_buffer,
                                        stream_callback=self.get_callback(),
                                        input_device_index=self.input_dev)
        self._stream.start_stream()
        return self

    def stop_recording(self):
        self._stream.stop_stream()
        return self

    def get_callback(self):
        def callback(in_data, frame_count, time_info, status):
            self.wavefile.writeframes(in_data)
            return in_data, pyaudio.paContinue
        return callback


    def close(self):
        self._stream.close()
        self._pa.terminate()
        self.wavefile.close()

    def _prepare_file(self, fname, mode='wb'):
        if mode == 'wb':
            wavefile = wave.open(fname, mode)
            wavefile.setnchannels(self.channels)
            wavefile.setsampwidth(self._pa.get_sample_size(pyaudio.paInt16))
            wavefile.setframerate(self.rate)
        elif mode == 'rb':
            wavefile = wave.open(fname, mode)
        else:
            print("prepare file error!")
        return wavefile

    def playback_file(self):
        self._stream = self._pa.open(format=self._pa.get_format_from_width(self.wavefile.getsampwidth()),
                                        channels=self.channels,
                                        rate=self.rate,
                                        output=True,
                                        frames_per_buffer=self.frames_per_buffer,
                                        output_device_index=self.output_dev,
                                        stream_callback=self.get_playback_callback())
        self._stream.start_stream()
        return self
    
    def get_playback_callback(self):
        def callback(in_data, frame_count, time_info, status):
            data = self.wavefile.readframes(frame_count)
            return (data, pyaudio.paContinue)
        return callback




