
import json
import nltk
# nltk.download('stopwords')
# nltk.download('punkt')
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from db import DBManager
from collections import defaultdict
import config
from utils import extract_terms_from_sentence, wash_text
from multiprocessing import Pool
import os
from timeit import default_timer as timer
import itertools


def get_terms_from_page(page):        
    sentences = nltk.sent_tokenize(page.text)
    sentences.append(page.title)

    stop_words = set(stopwords.words('english'))
    stemmer = PorterStemmer()

    valid_terms = []
    for sentence in sentences:
        sentence = wash_text(sentence)
        terms = extract_terms_from_sentence(sentence, stop_words, stemmer)
        valid_terms.extend(terms)

    return valid_terms

    
def process_lines(lines):
    pages = []
    dic = {}
    for i, line in enumerate(lines):
        page = Page(line)
        pages.append(page)

        valid_terms = get_terms_from_page(page)

        for term in valid_terms:
            if term not in dic.keys():
                dic[term] = Posting(term)
            dic[term].add_doc(page.id)

        # if (i+1) % 1000 == 0:
        #     print(f'{i+1} pages processed.', end='\r')
    return pages, dic
        

class Page:
    def __init__(self, page):
        self.id = page[0]
        self.title = page[1]
        self.text = page[2]

    def __str__(self):
        return f'[ID: {self.id}]\tTitle :{self.title}\n{self.text}'


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
    
    def __str__(self):
        return self.term

def merge_dics(dics):
    def _merge_posting(p1, p2):
        p1.docs.update(p2.docs)
        return p1

    dic = dics[0]
    for d in dics[1:]:
        for term, posting in d.items():
            if term in dic.keys():
                dic[term] = _merge_posting(dic[term], posting)
            else:
                dic[term] = posting
    return dic

def split(a, n):
    k, m = divmod(len(a), n)
    return (a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))

class ReversePostingListConstuctor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.db = DBManager(page_db=config.page_db,
                            index_db=config.index_db)
        self.db.create_table()

    
    def run(self, DEBUG=True, concurrent=False):
        start = timer()
        print(f"Load json from {self.file_path}...")
        lines = read_data(self.file_path)
        print(f"Finish in {timer()-start} s")
        
        if DEBUG:
            lines = lines[:1000]

        start = timer()
        if not concurrent:
            pages, dic = process_lines(lines)

            print(f'Sequenctial processing uses {timer()-start} s')
        else:
            n_cpu = os.cpu_count()//2
            print(f'{n_cpu} CPUs')
            pool = Pool(processes=n_cpu)
            n_part_lines = split(lines, n_cpu)
            results = pool.map(process_lines, n_part_lines)

            pool.close()
            pool.join()

            page_list, dic_list = zip(*results)
            pages = list(itertools.chain(*page_list))
            # assert(len(pages) == 1000)

            dic = merge_dics(dic_list) 
            # assert(dic.keys() == dic1.keys())

            # print(f'Concurrent processing uses {timer()-start} s')

        self.db.write_pages_to_db(pages)
        self.db.write_postings_to_db(dic)

        # if DEBUG:
        #     self.db.read_pages([0])
        #     self.db.read_postings(['cliniod'])
        
        print(f"File:{self.file_path.split('/')[-1]}:\t{len(pages)} pages processed in {timer()-start} s")


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
    wiki_dir = 'data/wiki/partitions'
    for part in os.listdir(wiki_dir)[:2]:
        fn = os.path.join(wiki_dir, part)
        
        # fn = 'data/wiki/partitions/test.ndjson'
        proc = ReversePostingListConstuctor(file_path=fn)
        proc.run(DEBUG=False, concurrent=True)
