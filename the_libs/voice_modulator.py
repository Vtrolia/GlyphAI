import os


def say(words):
    return os.system("echo " + words + " | festival --tts")


if __name__ == "__main__":
    while True:
        text = input("Enter some words for me to say: ")
        say(text)
