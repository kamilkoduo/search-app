import ast
import glob
import os
import shutil
import time

from engine import preprocess
from pathlib import Path

from engine.data import Collection, LineStream


class InvertedIndex:
    def __init__(self, limit=50, path='data/index'):
        self.index_path = Path(path)
        self.limit = limit
        self.index = {}

    def index_batch(self, batch):
        for doc, doc_id, line in batch:
            for w in preprocess.preprocess(doc):
                if w not in self.index:
                    self.index[w] = set()
                self.index[w].add((doc_id, line))

    def clean(self):
        shutil.rmtree(self.index_path)
        self.index_path.mkdir()

    def save(self):
        for token in self.index.keys():
            self.save_posting(token)

    def save_posting(self, token):
        with open(os.path.join(self.index_path, token), "w+") as file:
            file.write(str(self.index[token]) + '\n')

    def load_posting(self, token):
        postings = set()
        try:
            file = open(os.path.join(self.index_path, token), "r")
            sets = file.readlines()
            parsed = tuple(ast.literal_eval(s) for s in sets)
            if len(parsed) > 0:
                postings = set.union(*parsed)
        except FileNotFoundError:
            pass
        return postings

    def __getitem__(self, item):
        postings = self.load_posting(item)
        combined = postings.union(self.index[item])
        return combined

    def __contains__(self, key):
        return key in self.index


    def reload(self):
        for tokenfile in tuple(sorted(glob.glob(os.path.join(self.index_path, '*')))):
            token = os.path.basename(tokenfile)
            postings = self.load_posting(token)
            already = self.index[token] if token in self.index else set()
            self.index[token] = already.union(postings)
