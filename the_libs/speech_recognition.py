"""
speech recognition utilizes Mozilla's DeepSpeech library to take voice data from an input source and turn it into
a parsible string to be interpreted and responded to by GlyphAI.
"""

# internal imports
import the_libs.helpers as h
import the_libs.voice_modulator as vm

# external imports
import deepspeech as ds
import numpy as np
import pyaudio


class Listener(object):
    def __init__(self, model_path, scorer_path, chunk_size=1024, listen_time=3):
        """
        A Listener object opens both a speech-to-text engine and a listening stream in order for GlyphAI to listen for a
        users voice and then transform it into a interpretable string, which can then be processed and responded to. Will
        listening perpetually as long as the instance of GlyphAI is running and address the user when it is called upon.
        :param model_path: path the DeepSpeech model file
        :param scorer_path: path to DeepSpeech word scorer file
        :param chunk_size: size to store voice audio
        :param listen_time: how long at a time glyph should listen for each command
        """

        # load DeepSpeeh files
        self.ds_model = ds.Model(model_path)
        try:
            self.ds_model.enableExternalScorer(scorer_path)
        except RuntimeError:
            h.record_error("Speech Recognition", "Unable to load scorer, results may not be accurate")
        if not self.ds_model.setBeamWidth(2000) == 0:
            h.record_error("Speech Recognition", "Unable to set beam width to recomended size")

        # load PyAudio
        self.chunk_size = chunk_size
        self.listen_time = listen_time
        self.sample_format = pyaudio.paInt16
        self.sample_rate = self.ds_model.sampleRate()
        self.text = ''
        self.audio_if = pyaudio.PyAudio()
        self.record_stream = self.audio_if.open(format=self.sample_format, channels=1, rate=self.sample_rate,
                                                frames_per_buffer=self.chunk_size, input=True)

    def set_listen_time(self, new_time):
        """ Edit the listening time """
        self.listen_time = new_time
        return True

    def get_listen_time(self):
        """ get current listening time """
        return self.listen_time

    def set_chunk_size(self, new_size):
        """ edit chunk size """
        self.chunk_size = new_size
        return True

    def get_chunk_size(self):
        """ get current chunk size """
        return self.chunk_size

    def record_audio(self):
        """ Record an audio sample from an input device for listening time seconds """
        audio_frames = b''
        for i in range(0, int(self.sample_rate / self.chunk_size * self.listen_time)):
            # have the input stream silently fail and return nothing if audio cannot be recorded
            audio_frames += self.record_stream.read(self.chunk_size, exception_on_overflow=False)
        return audio_frames

    def transcribe_audio(self, raw_data):
        """ Use the recorded audio from pyAudio and turn into a string from a guess from the DeepSpeech model """
        formatted_data = np.frombuffer(raw_data, np.int16)
        return self.ds_model.stt(formatted_data)

    def check_for_greeting(self):
        """ Listen for input, and determine if the user is trying to activate GlyphAI, as you can see no audio is
            recorded
        """
        self.record_stream.start_stream()
        data = self.record_audio()
        self.record_stream.stop_stream()
        self.text = self.transcribe_audio(data)

        # stt is not always the most accurate so an approximation in Glyph's name can be detected as well
        if "gliff" in self.text or "cliff" in self.text:
            h.play_glyph_in("in")
            vm.say(h.proper_greeting() + " How can I help you?")
            return True
        return False

    def read_command(self):
        """ Once a user has activated GlyphAI, listen for a command and store the text for interpretation """
        h.play_glyph_in("in")
        self.record_stream.start_stream()
        self.set_listen_time(5)
        data = self.record_audio()
        self.record_stream.stop_stream()
        h.play_glyph_in("out")
        self.set_listen_time(3)
        return self.transcribe_audio(data)


# debug testing purposes
if __name__ == "__main__":
    ls = Listener("lib_resources/deepspeech-0.9.3-models.pbmm", "lib_resources/deepspeech-0.9.3-models.scorer")
    print("==============Glyph Loaded==============\n")

    while True:
        audio = ls.record_audio()
        print(ls.transcribe_audio(audio))
