"""
Helpers.py adds a set of functions that are helpful project-wide for simple tasks that need to be
completed. Mostly used for errors, basic speech and other things needed by multiple modules of the project.
"""

# inports
import json
import pyaudio
import random
import time
import urllib.request
import wave

from datetime import date


def proper_greeting():
    """ When a user calls for glyph, returns a greeting for the time of the day """
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
    """
    Finds the current geolocation of the user
    :param site: website to be used to find current location
    :return: location coordinates as a list
    """
    data = urllib.request.urlopen(site)
    json_obj = json.load(data)
    return json_obj['loc'].split(",")


def play_glyph_in(glyph_sound):
    """
    Depending on the context, will play either the intro or outro sound for glyph
    :param glyph_sound: string saying weather to play glyph in or out
    :return: None
    """
    if glyph_sound == "in":
        glyph_in = wave.open("the_libs/lib_resources/Glyph In.wav", "rb")

    elif glyph_sound == "out":
        glyph_in = wave.open("the_libs/lib_resources/gylph out.wav", "rb")
    else:
        return

    # load a sound output channel
    pya = pyaudio.PyAudio()
    stream = pya.open(format=pya.get_format_from_width((glyph_in.getsampwidth())),
                      channels=2,
                      rate=glyph_in.getframerate(),
                      output=True)
    stream.start_stream()
    data = glyph_in.readframes(512)

    # write the given soundfile to the output stream, then close
    while data:
        stream.write(data)
        data = glyph_in.readframes(512)
    stream.stop_stream()
    stream.close()
    pya.terminate()


def ask_wolfram(question):
    """
    For anhy type of question, it is best to query wolfram alpha for an answer
    :param question: what the user asked
    :return: the answer sent back from wolfram alpha
    """
    new_question = question + "%3F"
    new_question = question.replace(" ", "+")
    data = urllib.request.urlopen("https://api.wolframalpha.com/v1/result?i=" +
                                  new_question + "&timeout=10%&appid=EJAAAJ-K43K732TQR")
    return str(data.read())


def record_error(error_module, error_text):
    """ Writes the time and date of an error and what occured to an error file """
    current_time = time.localtime()
    time_string = time.strftime("%H:%M:%S", current_time)

    with open("glyph_errors.txt", "a") as f:
        f.write(date.today() + ":" + time_string + ": " + error_module + " Error: " + error_text)

