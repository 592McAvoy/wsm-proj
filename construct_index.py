import json
import nltk
# nltk.download('stopwords')
# nltk.download('punkt')
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from db import DBManager
from collections import defaultdict
import config


class Page:
    def __init__(self, page, iid=0):
        self.id = iid
        self.title = page[0]
        self.text = page[1]
        # self.wikilinks = page[2]
        # self.exlinks = pape[3]

    def __str__(self):
        return f'[ID: {self.id}]\tTitle:{self.title}\n{self.text}'


class Posting:
    def __init__(self, term):
        self.term = term
        self.docs = defaultdict(int)  # {doc_id: term frequency}

    def add_doc(self, doc_id):
        self.docs[doc_id] += 1

    def get_postings(self):
        # print(self.docs)
        postings = []
        for doc_id in self.docs.keys():
            # conbine TF with DOC_ID
            tf = self.docs[doc_id]
            doc_id = '|'.join(map(str, [doc_id, tf]))
            postings.append(doc_id)

        return postings


class ReversePostingListConstuctor:
    def __init__(self, file_path, id_start):
        self.dic = {}
        self.file_path = file_path
        self.db = DBManager(page_db=config.page_db,
                            index_db=config.index_db)
        self.db.create_table()
        self.id_start = self.db.get_current_max_page_id()+1
        
    
    def get_terms_from_page(self, page):
        en_stops = set(stopwords.words('english'))
        ps = PorterStemmer()

        def valid_word(w):
            w = w.lower()

            return w.isalnum() and \
                (w not in en_stops)

        def word2term(word):
            word = word.lower()
            word = ps.stem(word)
            return word

        # print(page.text)
        # print(washed_text)
        # exit()
        sentences = nltk.sent_tokenize(page.text)
        sentences.append(page.title)
        tokenizer = nltk.RegexpTokenizer(r"\w+")
        # tokenizer = get_tokenizer("en_US",chunkers=(HTMLChunker,))
        valid_terms = []
        
        for sentence in sentences:
            # print(sentence)
            sentence = wash_text(sentence)
            words = tokenizer.tokenize(sentence)
            # words = [w[0] for w in tokenizer(sentence)]
            
            # print(words)

            terms = [word2term(word) for word in words if valid_word(word)]
            valid_terms.extend(terms)
            # print(terms)
            # print('')

        return valid_terms

    def run(self, DEBUG=True):
        lines = read_data(self.file_path)
        iid = self.id_start
        pages = []
        if DEBUG:
            lines = lines[:1000]

        for i, line in enumerate(lines):
            page = Page(line, iid)
            pages.append(page)

            valid_terms = self.get_terms_from_page(page)
            # print(f'Title: {page.title}')
            # print(valid_terms)

            for term in valid_terms:
                if term not in self.dic.keys():
                    self.dic[term] = Posting(term)
                self.dic[term].add_doc(iid)

            if (i+1) % 1000 == 0:
                print(f'{i+1} pages processed.', end='\r')

            # doc id increment
            iid += 1

        self.db.write_pages_to_db(pages)
        self.db.write_postings_to_db(self.dic)

        if DEBUG:
            self.db.read_pages([0])
            self.db.read_postings(['cliniod'])

def wash_text(text):
    out = ''
    skip = False
    for ch in text:
        if ch in ['<', '{']:
            skip = True
            continue
        if ch in ['>', '}']:
            skip = False
            continue
        if not skip:
            out = out + ch
    return out.strip()
        
            

def read_data(path='data/wiki/partitions/test.ndjson'):
    data = []
    # Read in list of pages
    with open(path, 'rt') as fin:
        for l in fin.readlines():
            data.append(json.loads(l))
    return data


if __name__ == "__main__":
    # text = '<ref> test <ref>'
    # text = wash_text(text)
    # print(text)
    # exit()
    proc = ReversePostingListConstuctor(
        'data/wiki/partitions/test.ndjson', id_start=0)
    proc.run()
