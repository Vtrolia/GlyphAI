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
            code = language_processor.eval_text(cur_text)
            if code == 0:
                voice.say("You didn't say anything! Goodbye", voice_engine)
            elif code == 1:
                voice.say("Let me check that for you.", voice_engine)
                voice.say(language_processor.solve_text(cur_text, 1), voice_engine)
            elif code == 2:
                voice.say("Right away", voice_engine)
                voice.say(language_processor.solve_text(cur_text, 2), voice_engine)
            elif code == 3:
                voice.say(language_processor.solve_text(cur_text, 3), voice_engine)
            else:
                voice.say("Error in reading text", voice_engine)
        else:
            continue


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
