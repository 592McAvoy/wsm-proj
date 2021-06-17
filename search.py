import csv
import os
from db import DBManager
import config
import nltk
from multiprocessing import Pool
from timeit import default_timer as timer
import enchant
from fnmatch import fnmatch
from utils import extract_terms_from_sentence, wash_text, cosine_similarity, split, \
    cal_norm_tf_idf, extarct_id_tf, merge_scores, fast_cosine_similarity, weighted_zone, \
    cal_entropy_tf_f, cal_tf_idf

def process_term_posting(packed_params, total_pages=21229916, rank_mode = 1):
    """
    Calculate normed query tf-idf and doc tf-idf for term 

    Args:
        posting (tuple): (term, docs)
        terms (list): list of term frequency in query
        total_pages (int): the amount of pages

    Returns:
        normed query tf-idf 
        and a dictionary of doc tf-idf {docid: tf-idf}
    """
    if len(packed_params) == 1:
        # print(packed_params)       
        postings, tf_query = packed_params[0][0], packed_params[0][1]
        postings = [postings]
        tf_query = [tf_query]
        # print(postings)
    else:
        postings, tf_query = packed_params
    # print(postings)
    n_unique_terms = len(postings)
    query_vec = [0]*n_unique_terms

    doc_vecs = {}
    doc_tf = {}

    for i, (term, docs) in enumerate(postings):
        if len(docs) > 0:         
            docid_tf = extarct_id_tf(docs)

            if rank_mode == 3:# use entropy to calculate idf
                df = cal_entropy_tf_f(docid_tf, total_pages)
            else:
                df = len(docid_tf)

            if rank_mode == 1: # use unnormalized tf-idf
                query_vec[i] = cal_tf_idf(tf=tf_query[i], df=df, N_doc=total_pages)
            else:
                query_vec[i] = cal_norm_tf_idf(tf=tf_query[i], df=df, N_doc=total_pages)

            # sort by tf
            docid_tf = sorted(docid_tf, key=lambda d: d[1], reverse=True)
            for doc_id, tf in docid_tf[:config.max_docs_per_term]:
                if doc_id not in doc_vecs.keys():
                    doc_vecs[doc_id] = [0] * n_unique_terms
                doc_vecs[doc_id][i] = cal_norm_tf_idf(tf, df, total_pages)

    return query_vec, doc_vecs

class SearchManager:
    def __init__(self):
        self.db = DBManager(page_db=config.demo_page_db, index_db=config.demo_index_db)
        #self.db = DBManager(page_db=config.page_db, index_db=config.index_db)
        # self.total_pages = self.db.get_current_max_page_id()+1
        self.word_freq = read_freq_word()
        self.common_words = self._init_common_word()
        self.recommender = self._init_recommender()

        # print(f'Vocab size: {self.db.get_vocabs_size()}')
        # print(f'Total Docs: {self.total_pages}')
        # self.db.create_idx()

    def _init_common_word(self):
        with open('data/google-20k.txt', 'r') as fd:
            common_words = fd.readlines()
        common_words = [w[:-1] for w in common_words]
        return common_words

    def _init_recommender(self, additional_words=[]):
        recommender = enchant.Dict("en_US")
        for w in additional_words:
            recommender.add_to_session(w)

        return recommender

    def _search(self, query, concurrent=True, rank_mode = 1):
        terms = extract_terms_from_sentence(wash_text(query))
        unique_terms = set(terms)
        n_unique = len(unique_terms)
        if n_unique < 2:
            print(f'Warning: too few valid search terms. (only {n_unique})')

        start = timer()
        postings = self.db.read_postings(unique_terms)
        print(f'read postings in {timer()-start} s')
        # exit()

        # 1. calculate tf-idf for query and docs
        tf_query = [terms.count(t[0]) for t in postings]
        if not concurrent:
            start = timer()
            query_vec, doc_vecs = process_term_posting((postings, tf_query, rank_mode))
            print(f"Sequential process cost {timer()-start} s")
        # exit()
        else:
            start = timer()
            n_proc = min(n_unique, os.cpu_count()//2)
            pool = Pool(n_proc)
            pack = list(zip(postings, tf_query))
            n_part_params = split(pack, n_proc)
            results = pool.map(process_term_posting, n_part_params)
            pool.close()
            pool.join()
            query_vec_list, doc_vecs_list = zip(*results)
            query_vec, doc_vecs = merge_scores(
                query_vec_list, doc_vecs_list, n_unique)
            print(f"{n_proc} concurent process total cost {timer()-start} s")

        # 2. compute query-doc similarity
        doc_scores = []  # (doc_id, score)
        for doc_id, doc_vec in doc_vecs.items():
            # calculate cosine similarity
            doc_scores.append((doc_id, cosine_similarity(query_vec, doc_vec), sum(doc_vec)))

        # sort
        doc_scores = sorted(doc_scores, key=lambda d: d[1], reverse=True)
        print(len(doc_scores))

        # 3. return first N pages
        page_ids = [d[0] for d in doc_scores[:config.max_return_docs_firststep]]
        pages = self.db.read_pages(page_ids)

        if rank_mode == 4:
            doc_fast_cos_scores = []
            for doc_score, page in zip(doc_scores, pages):
                doc_fast_cos_scores.append((doc_score[0], fast_cosine_similarity(doc_score, page), page))

            doc_scores = sorted(doc_fast_cos_scores, key=lambda d: d[1], reverse=True)
            page_ids = [d[0] for d in doc_scores[:config.max_return_docs]]
            pages = [d[2] for d in doc_scores[:config.max_return_docs]]

        elif rank_mode == 5:# weighted zone
            # After sorting the top k documents, using weighted zone ranking to rerank the documents
            doc_scores = []
            for id, page in zip(page_ids, pages):
                doc_scores.append((id, weighted_zone(unique_terms, page, config.w_title, config.w_body), page))

            doc_scores = sorted(doc_scores, key=lambda d: d[1], reverse=True)
            page_ids = [d[0] for d in doc_scores[:config.max_return_docs]]
            pages = [d[2] for d in doc_scores[:config.max_return_docs]]


        #return pages, doc_weighted_zone_score
        return pages, doc_scores

    def most_frequent(self, candidates):
        ret = (candidates[0], -1)
        for s in candidates:
            if s not in self.word_freq.keys():
                continue
            if int(self.word_freq[s]) > ret[1]:
                ret = (s, int(self.word_freq[s]))
        return ret[0]

    def fuzzy_search(self, query):
        # print(common_words.__)
        new_query = query[:]
        for t in query.split():
            exist = self.recommender.check(t)
            # replace the non-exist word by the most similiar and frequently used one
            if not exist:
                suggest = self.recommender.suggest(t)[:5]
                # print(suggest)
                pick = self.most_frequent(suggest)
                new_query = new_query.replace(t, pick)

        if query != new_query:
            print(f'Do you mean \'{new_query}\'?')

        # self.search(new_query)
        return new_query

    def wildcard_search(self, query):
        """
        Support *

        Example:
            he*o -> hello, hero, ...
        """

        new_query = query[:]
        for t in query.split():
            if '*' in t:
                for word in self.common_words:
                    if fnmatch(word, t):
                        new_query = new_query.replace(t, word)
                        break

                # print(f'pattern:{t}\t results:{words}')
                # pick = self.most_frequent(words)

        if query != new_query:
            print(f'Search for \'{new_query}\'?')

        # self.search(new_query)
        return new_query

    def search(self, query, rank_mode=1):
        """
        wrapper of search logic

        Args:
            query (string): the input query string
        """
        print(f"Searching for {query}")

        if '*' in query:
            query = self.wildcard_search(query)

        query = self.fuzzy_search(query)

        pages, scores = self._search(query, concurrent=True, rank_mode = rank_mode)

        for i, page in enumerate(pages):
            #print("page:", page, "\n score", doc_weighted_zone_scores)
            print('[ID: {:04d} | Score: {:.4f}] Title: {}'.format(
                page[0], scores[i][1], page[1]))
            print(f'{wash_text(page[2][:1000])} ...\n')


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

    #query = 'har* university'
    query = 'har* university Charles Syracuse'
    proc.search(query, 4)
    # proc.fuzzy_search(query)

    # query = 'miew wo'
    # proc.wildcard_search(query)
