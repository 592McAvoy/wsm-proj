import csv
from db import DBManager
import config
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import math
import enchant


def cosine_similarity(v1, v2):
    "compute cosine similarity of v1 to v2: (v1 dot v2)/{||v1||*||v2||)"
    sumxx, sumxy, sumyy = 0, 0, 0
    for x, y in zip(v1, v2):
        sumxx += x*x
        sumyy += y*y
        sumxy += x*y

    return sumxy/math.sqrt(sumxx*sumyy)


class SearchManager:
    def __init__(self):
        self.db = DBManager(page_db=config.page_db, index_db=config.index_db)
        self.total_docs = self.db.get_current_max_page_id()+1
        self.common_words = enchant.Dict("en_US")
        self.word_freq = read_freq_word()

    def get_terms_from_query(self, query):
        en_stops = set(stopwords.words('english'))
        ps = PorterStemmer()

        def valid_word(w):
            w = w.lower()
            # return w.isalnum() and \
            return w.isalpha() and\
                (w not in en_stops)

        def word2term(word):
            word = word.lower()
            word = ps.stem(word)
            return word

        tokenizer = nltk.RegexpTokenizer(r"\w+")
        words = tokenizer.tokenize(query)
        terms = [word2term(word) for word in words if valid_word(word)]

        return terms

    def cal_norm_tf_idf(self, tf, df):
        if tf != 0:
            # TF_norm = 1 + \log(TF)
            tf = 1+math.log(tf)
        idf = 1+math.log(df/self.total_docs)

        return tf*idf

    def search(self, query, ret_N=3):
        terms = self.get_terms_from_query(query)
        unique_terms = set(terms)

        postings = self.db.read_postings(unique_terms)

        # query vector
        query_vec = [0]*len(unique_terms)

        doc_vecs = {}
        for i, (term, docs) in enumerate(postings):
            if len(docs) == 0:
                continue

            docs = docs.split(',')
            df = len(docs)

            query_vec[i] = self.cal_norm_tf_idf(tf=terms.count(term), df=df)
            for doc in docs:
                doc = doc.split('|')
                doc_id, tf = int(doc[0]), int(doc[1])
                if doc_id not in doc_vecs.keys():
                    doc_vecs[doc_id] = [0] * len(unique_terms)
                doc_vecs[doc_id][i] = self.cal_norm_tf_idf(tf, df)

        # calculate cosine similarity
        doc_scores = []
        for doc_id, doc_vec in doc_vecs.items():
            doc_scores.append((doc_id, cosine_similarity(query_vec, doc_vec)))

        # sort
        doc_scores = sorted(doc_scores, key=lambda d: d[1], reverse=True)

        # return first N pages
        page_ids = [d[0] for d in doc_scores[:ret_N]]
        pages = self.db.read_pages(page_ids)
        for i, page in enumerate(pages):
            print('[ID: {:04d} | Score: {:.4f}] Title: {}'.format(
                page[0], doc_scores[i][1], page[1]))
            print(f'{page[2][:300]} ...\n')

    def fuzzy_search(self, query):
        new_query = query[:]
        for t in query.split():
            exist = self.common_words.check(t)
            # print(f"{t}, {exist}")
            if not exist:
                suggest = self.common_words.suggest(t)[:5]
                cand = (None, -1)
                for s in suggest:
                    # print(s)
                    if s not in self.word_freq.keys():
                        continue
                    # print(self.word_freq[s])
                    if int(self.word_freq[s]) > cand[1]:
                        cand = (s, int(self.word_freq[s]))
                # print(cand)
                new_query = new_query.replace(t, cand[0])
                # print(new_query)
        if query != new_query:
            print(f'Do you mean \'{new_query}\'?')

        self.search(new_query)

    def wildcard_search(self):
        pass



def read_freq_word():
    freq_dic = {}
    with open('data/unigram_freq.csv', 'rt') as f:
        cr = csv.reader(f)
        for i, row in enumerate(cr):
            if i == 0:
                continue
            freq_dic[row[0]] = row[1]
    return freq_dic


if __name__ == "__main__":
    # read_freq_word()
    # exit()
    proc = SearchManager()
    print(f'Total Docs: {proc.total_docs}')
    query = 'holy molly'
    print(query)
    # proc.search(query)
    proc.fuzzy_search(query)
