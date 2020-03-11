import re
import time

from engine.preprocess import normalize, tokenize, remove_stop_words, lemmatize
from engine.data import Collection, LineStream
from engine.index_bigram import bound, k_grams, unbound, BigramIndex
from engine.index_inverted import InvertedIndex
from engine.index_soundex import soundex, SoundexIndex


def is_wildcard(token, wild='*'):
    return wild in token


def leven_dist(a, b):
    """dynamic programming algorithm"""
    n, m = len(a), len(b)
    dp = [[0 for i in range(m + 1)] for j in range(n + 1)]
    for i in range(n + 1):
        dp[i][0] = i
    for i in range(m + 1):
        dp[0][i] = i
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            t = int(a[i - 1] != b[j - 1])
            dp[i][j] = min(dp[i - 1][j - 1] + t, dp[i - 1][j] + 1, dp[i][j - 1] + 1)
    return dp[n][m]

def reformat_cnf(cnf):
    res = []
    for a in cnf:
        res.append('|'.join(a))

    return '&'.join(res)

class SearchEngine:
    def __init__(self, collection, stream, inverted_ind, bigram_ind, soundex_ind):
        self.collection = collection
        self.stream = stream
        self.inverted_ind = inverted_ind
        self.bigram_ind = bigram_ind
        self.soundex_ind = soundex_ind


    def reindex(self, ram_only=True):
        print(f'Reindex started')
        counter = 0
        if ram_only:
            self.inverted_ind.reload()
        while True:
            # if counter > 10:
            #     break
            # counter += 1
            batch = self.stream()
            if batch is None:
                break
            if not ram_only:
                self.inverted_ind.index_batch(batch)
                if len(self.inverted_ind.index) > self.inverted_ind.limit:
                    self.inverted_ind.save()
            self.bigram_ind.index_batch(batch)
            self.soundex_ind.index_batch(batch)
            # time.sleep(2)
        print(f'Reindex finished')

    def wild_words(self, token, wild='*'):
        check_re = re.compile(token.replace('*', '[a-z]*'))

        token = bound(token)
        tokens = token.split(wild)
        bigrams = k_grams(tokens, k=2)
        word_ll = [self.bigram_ind[bg] for bg in bigrams]
        word_l = word_ll[0].intersection(*word_ll)
        unbounded = [unbound(t) for t in word_l]
        checked = [t for t in unbounded if check_re.match(t)]
        return checked

    def spell_options(self, token, dist_func=leven_dist):
        def dist(x):
            return dist_func(x, token)

        s = soundex(token)
        if s not in self.soundex_ind:
            return []
        options = self.soundex_ind[s]
        mindist = dist(min(options, key=lambda x: dist(x)))
        return tuple(filter(lambda x: dist(x) <= mindist, options))

    def buildCNF(self, query):
        CNF_model = list()
        q_tokens = tokenize(normalize(query))
        for qt in q_tokens:
            if is_wildcard(qt):
                # wildcards
                CNF_model.append(remove_stop_words(lemmatize(self.wild_words(qt, self.bigram_ind))))
                continue
            ql = remove_stop_words(lemmatize([qt]))
            if len(ql) == 0:
                # stopword
                continue
            ql = ql[0]
            if ql in self.inverted_ind.index:
                # normal word
                CNF_model.append([ql])
                continue
            # soundex goes here
            CNF_model.append(
                remove_stop_words(
                    lemmatize(
                        self.spell_options(qt)
                    )
                )
            )
        return CNF_model

    def solve_df(self, df):
        postings = [set()]
        postings.extend([self.inverted_ind[t] for t in df])
        return set.union(*postings)

    def solve_cnf(self, cnf):
        dfs = [self.solve_df(df) for df in cnf]
        return dfs[0].intersection(*dfs) if len(dfs)>0 else set()

    def search(self, query):
        print(f'Searching {query}',f'building CNF')
        cnf = self.buildCNF(query)
        print(f'Solving CNF {reformat_cnf(cnf)}')
        return self.solve_cnf(cnf)


if __name__ == '__main__':
    query = 'food aid'  # change for something else if you are searching song lyrics

    col = Collection()
    stream = LineStream(col.paths())
    stream.open()
    inverted_ind = InvertedIndex()
    bigram_ind = BigramIndex()
    soundex_ind = SoundexIndex()

    print('done')

    engine = SearchEngine(col, stream, inverted_ind, bigram_ind, soundex_ind)

    print('done')
    engine.reindex()

    print('done')
    relevant = engine.search(query)
    print('done')
    print(relevant)
    print(len(relevant))
