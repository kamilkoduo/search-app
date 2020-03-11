import re

from engine import preprocess


def soundex(word):
    # substitution map
    costs = {
        '0': 'aeiouhwy',
        '1': 'bfpv',
        '2': 'cgjkqsxz',
        '3': 'dt',
        '4': 'l',
        '5': 'mn',
        '6': 'r',
    }
    subs = {}
    for c, ll in costs.items():
        subs.update({l: c for l in ll})

    # retain the first letter of the word
    head = word[0].upper()
    tail = word[1:].lower()

    # substitute
    tail = ''.join([subs[t] if t in subs.keys() else t for t in tail])

    # remove all pairs of consecutive digits
    tail = re.sub(r'(.)\1+', r'\1', tail)

    # remove all zeros from the resulting string.
    tail = re.sub(r'0', '', tail)

    # pad with trailing zeros and return head and first 3 positions
    tail = tail[0:3]
    tail = tail + "0" * (3 - len(tail))
    return head + tail


class SoundexIndex:
    def __init__(self, k=2):
        self.k = k
        self.index = {}

    def index_batch(self, batch):
        for doc, doc_id, line in batch:
            for w in preprocess.tokenize(preprocess.normalize(doc)):
                s = soundex(w)
                if s not in self.index:
                    self.index[s] = set()
                self.index[s].add(w)

    def __getitem__(self, item):
        return self.index[item]

    def __contains__(self, key):
        return key in self.index
