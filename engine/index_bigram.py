from engine import preprocess


def bound(token, wild='*', bound='$'):
    if token[0] == wild:
        return token + bound
    if token[-1] == wild:
        return bound + token
    return "".join([bound, token, bound])


def unbound(token, bound='$'):
    if token[0] == bound:
        token = token[1:]
    if token[-1] == bound:
        token = token[:-1]
    return token


def k_grams(tokens, k=2):
    res = []
    for t in tokens:
        res.extend([t[i:i + k] for i in range(len(t) - k + 1)])
    return res


class BigramIndex:
    def __init__(self, k=2):
        self.k = k
        self.index = {}

    def index_batch(self, batch):
        for doc, doc_id, line in batch:
            for w in preprocess.tokenize(preprocess.normalize(doc)):
                b = bound(w)
                for kg in k_grams([b], k=self.k):
                    if kg not in self.index:
                        self.index[kg] = set()
                    self.index[kg].add(b)
