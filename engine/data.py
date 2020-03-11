import ssl
from pathlib import Path
import fileinput
import glob

import nltk
import os
import re

from nltk.corpus import reuters


class Collection():
    def __init__(self, raw=Path('data/raw'), path=Path('data/collection')):
        self.raw = raw
        self.path = path
        self.path_list = tuple(sorted(glob.glob(os.path.join(self.raw, '*'))))

    def paths(self):
        return self.path_list

    def download(self):
        try:
            _create_unverified_https_context = ssl._create_unverified_context
        except AttributeError:
            pass
        else:
            ssl._create_default_https_context = _create_unverified_https_context
        nltk.download('reuters')

        for id, doc_id in enumerate(reuters.fileids()):
            with open(os.path.join(self.raw, str(id)), 'w+') as file:
                file.write(reuters.raw(doc_id))


class Stream(object):
    def __init__(self):
        pass


class LineStream(Stream):
    def __init__(self, paths, batch_len=10):
        super().__init__()
        self.batch_len = batch_len
        self.paths = paths
        self.file_input = None
        self.lines = None

    def open(self):
        self.file_input = fileinput.FileInput(self.paths)
        self.lines = self.lines_gen()

    def close(self):
        if isinstance(self.file_input, fileinput.FileInput):
            self.file_input.close()
            self.file_input = None

    def lines_gen(self):
        if self.file_input is not None:
            for line in self.file_input:
                yield line, int(os.path.basename(self.file_input.filename())), self.file_input.filelineno()
        yield None

    def next_line(self):
        try:
            return next(self.lines)
        except StopIteration:
            return None

    def __call__(self, *args, **kwargs):
        batch = []
        for i in range(self.batch_len):
            batch.append(self.next_line())
        return tuple(batch)


if __name__ == '__main__':
    # import ssl
    #
    col = Collection()
    stream = LineStream(col.paths())
    stream.open()
    for i in range(10):
        print(stream())
