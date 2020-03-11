import re
import ssl

import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from engine.utils import ssl_fix

ssl_fix()
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')


def normalize(text):
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
