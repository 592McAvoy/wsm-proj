import csv
import os
from db import DBManager
import config
import nltk
from multiprocessing import Pool
from timeit import default_timer as timer
import enchant
from fnmatch import fnmatch
from utils import extract_terms_from_sentence, wash_text, cosine_similarity, \
    split, cal_norm_tf_idf, extarct_id_tf, merge_scores, remove_puntuation

def process_term_posting(packed_params, total_pages=11650115):
    """
    Calculate normed query tf-idf and doc tf-idf for term 

    Args: 
        posting (tuple): (term, docs)
        tf_query (list): list of term frequency in query
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

    for i, (term, docs) in enumerate(postings):
        if len(docs) > 0:         
            docid_tf = extarct_id_tf(docs)
            df = len(docid_tf)
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
        # self.db = DBManager(page_db=config.page_db, index_db=config.index_db)
        # self.total_pages = self.db.get_current_max_page_id()+1
        self.word_freq = read_freq_word()
        self.common_words = self._init_common_word()
        self.recommender = self._init_recommender()
        self.page_buffer = None

        # print(f'Vocab size: {self.db.get_vocabs_size()}')
        # print(f'Total Docs: {self.db.get_page_size()}')
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

    def _search(self, query, concurrent=True, rank_mode='cos'):
        terms = extract_terms_from_sentence(query)
        if len(terms) == 0:
            return None

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
        if not concurrent or len(postings)<2:
            start = timer()
            query_vec, doc_vecs = process_term_posting((postings, tf_query))
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
            if rank_mode == 'cos':
                doc_scores.append((doc_id, cosine_similarity(query_vec, doc_vec)))
            else:
                # add new ranking method here
                raise NotImplementedError(rank_mode)


        # 3. return first N pages (id, score)
        doc_scores = sorted(doc_scores, key=lambda d: d[1], reverse=True)
        print(f'Searched for {len(doc_scores)} pages')

        return doc_scores[:config.max_return_docs]


    def most_frequent(self, candidates):
        ret = (candidates[0], -1)
        for s in candidates:
            if s not in self.word_freq.keys():
                continue
            if int(self.word_freq[s]) > ret[1]:
                ret = (s, int(self.word_freq[s]))
        return ret[0]

    def fuzzy_query(self, query):
        # print(common_words.__)
        new_query = query[:]
        for t in query.split():
            exist = self.recommender.check(t)
            # replace the non-exist word by the most similiar and frequently used one
            if not exist:
                suggest = self.recommender.suggest(t)[:5]
                if len(suggest) > 0:
                    # print(suggest)
                    pick = self.most_frequent(suggest)
                    new_query = new_query.replace(t, pick)

        if query != new_query:
            print(f'Do you mean \'{new_query}\'?')

        # self.search(new_query)
        return new_query

    def wildcard_query(self, query):
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

    def search(self, query, concurrent=True):
        """
        wrapper of search logic

        Args:
            query (string): the input query string
        """
        print(f"Searching for \'{query}\'")
        
        start = timer()
        query = wash_text(remove_puntuation(query))
        # print(f'washed: {query}')
        if '*' in query:
            query = self.wildcard_query(query)

        fuzzy_query = self.fuzzy_query(query)

        # exit()

        # pages, doc_scores = self._search(query, concurrent=True)
        doc_scores = self._search(query, concurrent=concurrent)
        if doc_scores is None:
            print(f'No valid input in {query}')
            return None,'', ['','']

        if fuzzy_query != query:
            doc_scores_fuzzy = self._search(fuzzy_query, concurrent=concurrent)
            if doc_scores_fuzzy is not None:
                doc_scores.extend(doc_scores_fuzzy)
                doc_scores = sorted(doc_scores, key=lambda d: d[1], reverse=True)

        # for i, page in enumerate(pages):
        page_ids = [d[0] for d in doc_scores]
        pages = self.db.read_pages(page_ids)
        self.page_buffer = pages

        time_cost = timer()-start

        page_list = [{
                'ID':page[0],
                'title':page[1],
                'content': wash_text(page[2]),
            } for page in pages]

        time_str = '{:.5f}'.format(time_cost)
        querys = [query, fuzzy_query]
        if query == fuzzy_query:
            querys[1] = None
        
        return page_list, time_str, querys
        
        # return result_dict


        # return pages, time_cost
        # for i, page in enumerate(pages):
        #     print('[ID: {:04d} | Score: {:.4f}] Title: {}'.format(
        #         page[0], doc_scores[i][1], page[1]))
        #     print(f'{wash_text(page[2][:1000])} ...\n')

    def read_page(self, page_id):
        for page in self.page_buffer:
            if page[0] == page_id:
                return {
                    'title':page[1],
                    'content': wash_text(page[2]), 
                }
        raise NotImplementedError(page_id)


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
    proc = SearchManager()

    query = 'go out for experct snacks'
    # query = input('Please input query:\n')
    proc.search(query)

