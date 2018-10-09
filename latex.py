import os
import sys
from plasTeX.TeX import TeX
from plasTeX.Tokenizer import BeginGroup, EndGroup

# TODO write function to render paper (and possibly equation too)
#   latexmk -outdir=output -pdf file.tex

def maybe_add_extension(filename):
    """add .tex extension if needed"""
    if os.path.exists(filename):
        return filename
    elif os.path.exists(filename + '.tex'):
        return filename + '.tex'

def read_group(tokens):
    """read the content of a tex group, i.e., the text surrounded by curly brackets"""
    s = ''
    assert isinstance(next(tokens), BeginGroup)
    while True:
        t = next(tokens)
        if isinstance(t, EndGroup):
            break
        s += t.data
    return s

def tokenize(filename):
    """read tex tokens, including imported files"""
    tex = TeX(file=filename)
    tokens = tex.itertokens()
    try:
        while True:
            token = next(tokens)
            if token.data == 'input':
                fname = maybe_add_extension(read_group(tokens))
                for t in tokenize(fname):
                    yield t
            elif token.data == 'import':
                # TODO handle \subimport, and also \import* and \subimport*
                path = read_group(tokens)
                name = read_group(tokens)
                fname = maybe_add_extension(os.path.join(path, name))
                for t in tokenize(fname):
                    yield t
            elif token.data == 'include':
                # TODO be aware of \includeonly
                fname = maybe_add_extension(read_group(tokens))
                for t in tokenize(fname):
                    yield t
            else:
                yield token
    except StopIteration:
        pass

if __name__ == '__main__':
    for t in tokenize(sys.argv[1]):
        print type(t), repr(t)
