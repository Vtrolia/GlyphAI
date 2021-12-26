"""
Language processor class that interprets read words and returns in integer as a meaning
"""

# internal imports
import the_libs.helpers as h

# external imports
import joblib as j
import sys
# machine learning imports
import sklearn.feature_extraction.text as t
from sklearn.linear_model import SGDClassifier as SGD


class LanguageProcessor(object):
    # words that mean it's a question, duh
    question_keywords = ["who", "what", "when", "where", "how", "do", "am", "is", "are", "were", "have",
                         "has", "did", "was", "will", "can", "should", "would", "which", "if", "won't",
                         "don't", "whose", "whom"]

    # text codes for quicker interpretation
    text_codes = {0: "none", 1: "question", 2: "command", 3: "conversation"}

    def __init__(self, command_vector_file, command_model_file):
        """
        A language processor object is an AI engine that aims to separate text input captured from a user
        into different categories and then create an appropriate response. This technology is built upon scikit's text
        prediction technology and was built from a previous iteration of the Glyph AI, modified and refined for more 
        accurate results. The model is always evolving however, and can be edited and tweaked to allow for more 
        accurate results to come in the future
        :param command_vector_file: file used for parsing text
        :param command_model_file: file used for parsing text
        """
        self.vector = j.load(command_vector_file)
        self.model = j.load(command_model_file)

    def eval_text(self, text):
        """ Returns the text code for input text """
        
        # empty
        if not text or len(text) == 0:
            return 0
        
        # question
        for word in LanguageProcessor.question_keywords:
            if word in text.split(' ')[0]:
                return 1

        # command
        text_vector = [text]
        text_vector = self.vector.transform(text_vector)
        guess = self.model.predict(text_vector)[0]
        if guess == 1:
            return 2
        
        # unknown text
        return 3

    def solve_text(self, text, text_code):
        """ Takes a text code and passes an appropriate method to handle it """
        if text_code == 0:
            return "No input"
        elif text_code == 1:
            return h.ask_wolfram(text)
        elif text_code == 2:
            return "Commands coming soon!"
        elif text_code == 3:
            return "Conversation coming probably never!"
        else:
            return "Improper format usage"

    @staticmethod
    def reload_model(vectorize_file, model_file, command_positive, command_negative):
        """
        Over time, the working text model may no longer be sufficiently accurate tp correctly process commands, because
        of this, there is the need to rebuild the models that the text prediction is based on. This is a static method
        so that if the model has been retrained and refined, it will be rebuilt to reflect the changes and have moree
        accurate results
        :param vectorize_file: modeling files
        :param model_file: modeling files
        :param command_positive: examples of commands
        :param command_negative: examples of not commands
        :return: 0
        """

        # read each of the positive and negative examples and separate them into lists
        positive = open(command_positive, 'r')
        negative = open(command_negative, 'r')
        pos = []
        for line in positive.readlines():
            pos.append(line[:-1])
        neg = []
        for line in negative.readlines():
            neg.append(line[:-1])
        positive.close()
        negative.close()
        pos_labels = (1 for _ in range(len(pos)))
        neg_labels = (0 for _ in range(len(neg)))

        examples = []
        labels = []
        examples.extend(pos)
        labels.extend(pos_labels)
        examples.extend(neg)
        labels.extend(neg_labels)

        # recreate the models, and save them to be used later
        vector = t.TfidfVectorizer(stop_words='english', ngram_range=(1, 4))
        examples = vector.fit_transform(examples)
        j.dump(vector, vectorize_file)
        gradient = SGD(loss="hinge", penalty="l1")
        gradient.fit(examples, labels)
        j.dump(gradient, model_file)
        return 0

    @staticmethod
    def train_model(vector_file, model_file, command_positive):
        """
        In addition to reloading an updated model, the need to keep improving the models and adding new positive and
        negative examples is obvious. This static method makes sure that GlyphAI's internal model can be independently
        called and trained outside a running instance
        :param vector_file: model file
        :param model_file: model file
        :param command_positive: positives to add
        """
        model = j.load(model_file)
        vector = j.load(vector_file)

        # run until keyboard interrupt is called
        while True:
            text = input("try me (type exit to end): ")
            if text == "exit":
                sys.exit()

            # make a guess upon the input text
            text_vec = [text]
            text_vec = vector.transform(text_vec)
            guess = model.predict(text_vec)[0]
            if guess == 1:
                print("That's a command!")

            else:
                # if the guess was incorrect, add it to the positive or negative examples, allowing it to be retrained
                correction = input("That's no command, sir!, was i right? (y or n): ")
                while correction not in ['y', 'n']:
                    correction = input("Retry: ")
                if correction == 'n':
                    file = open(command_positive, 'a')
                    file.write(text + '\n')
                    file.close()

    @staticmethod
    def get_typestring(code):
        """ return a typestring code integer """
        if code < 4:
            return LanguageProcessor.text_codes[code]
