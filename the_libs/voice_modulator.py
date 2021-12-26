"""
Voice modulator makes usage of festival to read tts
"""
import os


def say(words):
    """ queries festival for tts functionality """
    return os.system("echo " + words + " | festival --tts")


# debug testing purposes
if __name__ == "__main__":
    while True:
        text = input("Enter some words for me to say: ")
        say(text)
