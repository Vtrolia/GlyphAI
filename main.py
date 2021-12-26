"""
Glyph AI Virtual Assistant
Copyright 2021 Vincent W. Trolia. All Rights reserved.

GlyphAI is a simple virtual assistant run locally on a user's computer that does not store information and is transparent
about when it sends information to the internet. The only data collected would be a question asked and sent to Wolfram
Alpha's API iot get an answer for a naturally asked question. Uses Mozilla's DeepSpeech and scikit's machine learning models
to interact with a user and attempt to interpret vocal input from a user. This is an improved version from an earlier,
simpler GlyphAI with more features and more robust speech synthesis and speech interpretation. GlyphAI is meant to be run
on a Raspberry Pi with future, more advanced SKUs to be available at a later date.

GlyphAI is dependant on PyAudio, Sklearn, DeepSpeech, Joblib, Scikit-learn and Numpy. An internet connection is also
required for any general knowledge questions iot find results from Wolfram Alpha's API.

External dependencies include Festival, PortAudio, etc. It was designed and tested last on Ubuntu but will soon be ported
over to Raspberry Pi OS.

This project was something I was working on for a little while in College while I was thinking of a way to enable
smart home style features without being depending on a black-box assistant from a big tech company that has unknown
levels of data collection as well as my own interest in Machine Learning and wanting to get hands-on experience with the
different techniques used for Natural Language Processing. I revisted this project a few years later and am currently
using it to kill time and do something productive whilst being on deployment in Okinawa, with a lot of downtime and
boredom being the main enemy. For updates, stay tuned on my github and for any concerns you can email me at
vtrolia@protonmail.com

"""

# internal imports
import the_libs.language_processor as nlp
import the_libs.speech_recognition as sr
import the_libs.voice_modulator as voice
import the_libs.helpers as h

# external imports
import getopt
import sys


def main():
    """
    Run an instance of the glyph AI, loading all the modules and then listening for input from the user, being
    ready to process commands
    :return: 0
    """
    try:
        # utlilizing optarg will allow for lower level control of glyph ai when it seems to not
        # correctly identify different kinds of speech, allowing it to be retrained and reloaded
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

    # load all the AI modules required
    word_parser = sr.Listener("the_libs/lib_resources/deepspeech-0.9.3-models.pbmm",
                              "the_libs/lib_resources/deepspeech-0.9.3-models.scorer")
    language_processor = nlp.LanguageProcessor("the_libs/lib_resources/command_vectorizer.pkl",
                                               "the_libs/lib_resources/command_model.pkl")

    print("==============Glyph Loaded==============\n")
    cur_text = ""

    # listen for someone to call for glyph then try to interpret what they say
    while True:
        if word_parser.check_for_greeting():
            cur_text = word_parser.read_command()
            code = language_processor.eval_text(cur_text)
            if code == 0:
                voice.say("You didn't say anything! Goodbye")
            elif code == 1:
                voice.say("Let me check that for you.")
                voice.say(language_processor.solve_text(cur_text, 1))
            elif code == 2:
                voice.say("Right away")
                voice.say(language_processor.solve_text(cur_text, 2))
            elif code == 3:
                voice.say(language_processor.solve_text(cur_text, 3))
            else:
                voice.say("Error in reading text")
        else:
            continue


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
