import nltk
import re

def extract_terms_from_sentence(sentence, stop_words, stemer):
    def valid_word(w):
        w = w.lower()
        return w.isalnum() and \
            (w not in stop_words)

    def word2term(word):
        word = word.lower()
        word = stemer.stem(word)
        return word

    tokenizer = nltk.RegexpTokenizer(r"\w+")
    words = tokenizer.tokenize(sentence)
    terms = [word2term(word) for word in words if valid_word(word)]

    return terms

def wash_text(text):
    out = re.sub(r'(<|{).*(>|})', '', text)

    return out.strip()
