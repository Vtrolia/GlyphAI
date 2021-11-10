import the_libs.language_processor as nlp
import the_libs.speech_recognition as sr
import the_libs.voice_modulator as voice
import the_libs.helpers as h
import getopt
import sys


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "m:h")
        for opt, arg in opts:
            if opt == "-h":
                print("Usage: glyphai.py [-m|--command-model] [\"reload\", \"retrain\"]")
                return 0

            if opt == "-m":
                if arg == "reload":
                    nlp.LanguageProcessor.reload_model("the_libs/lib_resources/command_vectorizer.pkl",
                                                       "the_libs/lib_resources/command_model.pkl",
                                                       "the_libs/lib_resources/command_t.txt",
                                                       "the_libs/lib_resources/command_f.txt")
                    return 0
                elif arg == "retrain":
                    nlp.LanguageProcessor.train_model("the_libs/lib_resources/command_vectorizer.pkl",
                                                      "the_libs/lib_resources/command_model.pkl",
                                                      "the_libs/lib_resources/command_t.txt")
                else:
                    print("Usage: glyphai.py [-m|--command-model] [\"reload\", \"retrain\"]")
                    return -1

    except getopt.GetoptError:
        return -2

    voice_engine = voice.init_voice("Karen")
    word_parser = sr.Listener("the_libs/lib_resources/deepspeech-0.9.3-models.pbmm",
                              "the_libs/lib_resources/deepspeech-0.9.3-models.scorer")
    language_processor = nlp.LanguageProcessor("the_libs/lib_resources/command_vectorizer.pkl",
                                               "the_libs/lib_resources/command_model.pkl")
    print("==============Glyph Loaded==============\n")
    cur_text = ""
    while True:
        if word_parser.check_for_greeting(voice_engine):
            cur_text = word_parser.read_command()
            print(language_processor.eval_text(cur_text))
        else:
            continue

        if "weather" in cur_text:
            voice.say("Ok, I'll check the weather for you. One moment please.", voice_engine)
            print("Ok, I'll check the weather for you:\n")
            weather_string = h.get_weather(h.get_location("http://ipinfo.io/json"), "7425713b1652372ddd33a4e35976d304")
            print(weather_string)
            voice.say(weather_string, voice_engine)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
