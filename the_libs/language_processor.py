# language processor class that interprets read words and returns in integer as a meaning
import joblib as j
import sys
import sklearn.feature_extraction.text as t
from sklearn.linear_model import SGDClassifier as SGD
import the_libs.helpers as h


class LanguageProcessor(object):
    question_keywords = ["who", "what", "when", "where", "how", "do", "am", "is", "are", "were", "have",
                         "has", "did", "was", "will", "can", "should", "would", "which", "if", "won't",
                         "don't", "whose", "whom"]
    text_codes = {0: "none", 1: "question", 2: "command", 3: "conversation"}

    def __init__(self, command_vector_file, command_model_file):
        self.vector = j.load(command_vector_file)
        self.model = j.load(command_model_file)

    def eval_text(self, text):
        if not text or len(text) == 0:
            return 0

        for word in LanguageProcessor.question_keywords:
            if word in text.split(' ')[0]:
                return 1

        text_vector = [text]
        text_vector = self.vector.transform(text_vector)
        guess = self.model.predict(text_vector)[0]
        if guess == 1:
            return 2

        return 3

    def solve_text(self, text, text_code):
        if text_code == 0:
            return "No input"
        elif text_code == 1:
            if "weather" in text:
                weather_string = h.get_weather(h.get_location("http://ipinfo.io/json"),
                                               "7425713b1652372ddd33a4e35976d304")
                return weather_string
            else:
                return h.ask_wolfram(text)
        elif text_code == 2:
            return "Commands coming soon!"
        elif text_code == 3:
            return "Conversation coming probably never!"
        else:
            return "Improper format usage"

    @staticmethod
    def reload_model(vectorize_file, model_file, command_positive, command_negative):
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

        vector = t.TfidfVectorizer(stop_words='english', ngram_range=(1, 4))
        examples = vector.fit_transform(examples)
        j.dump(vector, vectorize_file)

        gradient = SGD(loss="hinge", penalty="l1")
        gradient.fit(examples, labels)
        j.dump(gradient, model_file)
        return 0

    @staticmethod
    def train_model(vector_file, model_file, command_positive):
        model = j.load(model_file)
        vector = j.load(vector_file)

        while True:
            text = input("try me (type exit to end): ")
            if text == "exit":
                sys.exit()
            text_vec = [text]
            text_vec = vector.transform(text_vec)
            guess = model.predict(text_vec)[0]
            if guess == 1:
                print("That's a command!")

            else:
                correction = input("That's no command, sir!, was i right? (y or n): ")
                while correction not in ['y', 'n']:
                    correction = input("Retry: ")
                if correction == 'n':
                    file = open(command_positive, 'a')
                    file.write(text + '\n')
                    file.close()

    @staticmethod
    def get_typestring(code):
        if code < 4:
            return LanguageProcessor.text_codes[code]
