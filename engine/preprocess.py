import re
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords

nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')


def normalize(self, text):
    lower = text.lower()
    letters = re.sub(r'[^a-z\*]', ' ', lower)
    spaces_once = re.sub(r'\s+', ' ', letters)
    return spaces_once


def tokenize(text):
    tokens = nltk.word_tokenize(text)
    return tokens


def lemmatize(tokens):
    lemmatizer = WordNetLemmatizer()
    lemmas = [lemmatizer.lemmatize(word) for word in tokens]
    return list(set(lemmas))


def remove_stop_words(tokens):
    stopwords_set = set(stopwords.words('english'))
    sanitized = [word for word in tokens if not word in stopwords_set]
    return sanitized


def preprocess(text):
    text = normalize(text)
    tokens = tokenize(text)
    lemmas = lemmatize(tokens)
    clean = remove_stop_words(lemmas)
    return clean
