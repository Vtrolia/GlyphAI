import random
import time
import urllib.request
import json
import wave
import pyaudio


def proper_greeting():
    chance = random.randint(1, 5)
    if chance > 4:
        return "What's up, Dude?"
    else:
        time_now = int(time.strftime("%H"))
        if time_now < 12:
            return "Good Morning!"
        elif time_now == 12 or time_now < 18:
            return "Good Afternoon!"
        else:
            return "Good Evening"


def get_location(site):
    data = urllib.request.urlopen(site)
    json_obj = json.load(data)
    return json_obj['loc'].split(",")


def play_glyph_in(glyph_sound):
    if glyph_sound == "in":
        glyph_in = wave.open("the_libs/lib_resources/Glyph In.wav", "rb")

    elif glyph_sound == "out":
        glyph_in = wave.open("the_libs/lib_resources/gylph out.wav", "rb")
    else:
        return
    pya = pyaudio.PyAudio()
    stream = pya.open(format=pya.get_format_from_width((glyph_in.getsampwidth())),
                      channels=2,
                      rate=glyph_in.getframerate(),
                      output=True)
    stream.start_stream()
    data = glyph_in.readframes(512)
    while data:
        stream.write(data)
        data = glyph_in.readframes(512)
    stream.stop_stream()
    stream.close()
    pya.terminate()


def ask_wolfram(question):
    new_question = question + "%3F"
    new_question = question.replace(" ", "+")

    data = urllib.request.urlopen("https://api.wolframalpha.com/v1/result?i=" +
                                  new_question + "&timeout=10%&appid=EJAAAJ-K43K732TQR")

    return str(data.read())


