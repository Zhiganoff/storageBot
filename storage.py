# -*- coding: utf-8 -*-

import pymorphy2
import stop_words

PYMORPHY_CACHE = {}

def convert2unicode(f):
    def tmp(text):
        if not isinstance(text, str): text = text.decode('utf8')
        return f(text)
    return tmp


def convert2lower(f):
    def tmp(text):        
        return f(text.lower())
    return tmp

def easy_tokenizer(text):
    word = str()
    for symbol in text:
        if symbol.isalnum(): word += symbol
        elif word:
            yield word
            word = str()
    if word: yield word


@convert2lower
@convert2unicode
def pymorphy_tokenizer(text):
    global PYMORPHY_CACHE
    for word in easy_tokenizer(text):
        if word not in stop_words.get_stop_words('russian') and word not in stop_words.get_stop_words('english'):
            word_hash = hash(word)
            if word_hash not in PYMORPHY_CACHE:
                PYMORPHY_CACHE[word_hash] = pymorphy2.MorphAnalyzer().parse(word)[0].normal_form            
            yield PYMORPHY_CACHE[word_hash]


def add_message_to_term(storage, term, message):
    set_for_term = storage.setdefault(term, set())
    set_for_term.add(message)


def handle_form(storage, form):
    # map(add_message_to_term, pymorphy_tokenizer(form['description']), list(form['message']))
    # print(list(pymorphy_tokenizer(form['description'])))
    # map(lambda term: print(term))
    # map(lambda term: add_message_to_term(storage, term, form['message']),
    #     list(pymorphy_tokenizer(form['description'])))
    for term in pymorphy_tokenizer(form['description']):
        add_message_to_term(storage, term, form['message'])


def search(storage, descr):
    res = set()
    for term in pymorphy_tokenizer(descr):
        if storage.get(term) != None:
            res = res & storage(term) if res else storage[term]
    return res