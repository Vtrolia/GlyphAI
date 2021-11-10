import pyttsx3


def init_voice(name):
    engine = pyttsx3.init()
    for voice in engine.getProperty("voices"):
        if voice.name == "Karen":
            engine.setProperty("voice", voice.id)
            return engine
    return None


def say(words, engine):
    engine.say(words)
    engine.runAndWait()
    return True
