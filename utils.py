import nltk
import re
from db import Page, Posting
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import math


def extract_terms_from_sentence(sentence, stop_words=None, stemmer=None):
    if stop_words is None:
        stop_words = set(stopwords.words('english'))
    if stemmer is None:
        stemmer = PorterStemmer()

    def valid_word(w):
        w = w.lower()
        return w.isalnum() and \
            (w not in stop_words)

    def word2term(word):
        if len(word) > 50:  # strange case (cause Recursion Error)
            word = word[:50]
        word = word.lower()
        word = stemmer.stem(word)
        return word

    tokenizer = nltk.RegexpTokenizer(r"\w+")
    words = tokenizer.tokenize(sentence)
    terms = [word2term(word) for word in words if valid_word(word)]

    return terms


def wash_text(text):
    out = re.sub(r'(<|{).*(>|})', '', text)

    return out.strip()


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
    """
    Split the list into N chunks with nearly equal size

    Args:
        a ([list]): the list to be split
        n ([int]): the number of chunks

    Returns:
        [list]: list of N chunks
    """
    k, m = divmod(len(a), n)
    ret = [a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n)]
    return ret

def fast_cosine_similarity(doc_score, page):
    "need to divide the length of document"
    wtf = doc_score[2]
    return wtf/(len(page[1].split()) + len(page[2].split()))


def cosine_similarity(v1, v2):
    "compute cosine similarity of v1 to v2: (v1 dot v2)/{||v1||*||v2||)"
    sumxx, sumxy, sumyy = 0, 0, 0
    for x, y in zip(v1, v2):
        sumxx += x*x
        sumyy += y*y
        sumxy += x*y

    return sumxy/math.sqrt(sumxx*sumyy)

def weighted_zone(terms, page, w_title, w_body):
    "page[1] - title"
    "page[2] - body"
    title_sum = 0
    body_sum = 0

    for term in terms:
        for word in page[1].split():
            if term in word.lower():
                title_sum += 1
                break

        for word in page[2].split():
            if term in word.lower():
                body_sum += 1
                break

    return w_title * title_sum + w_body * body_sum

def cal_norm_tf_idf(tf, df, N_doc):
    if tf != 0:
        # TF_norm = 1 + \log(TF)
        tf = 1+math.log(tf)
    idf = 1+math.log(df/N_doc)

    return tf*idf

def cal_tf_idf(tf, df, N_doc):
    idf = 1 + math.log(df / N_doc)
    return tf * idf

def cal_entropy_tf_f(docid_tf, N_doc):
    f = sum(docid_tf[:][1])
    entropy_sum = 0
    for doc_id, tf in docid_tf:
        entropy_sum += f/tf * math.log(tf/f)

    return 1 - entropy_sum/math.log(N_doc)


def merge_scores(query_vec_list, doc_vecs_list, n_unique):
    query_vec = [0]*n_unique
    i = 0
    for q_vec in query_vec_list:
        for j, s in enumerate(q_vec):
            query_vec[i+j] = s
        i += len(q_vec)
    assert(i == n_unique)

    doc_vecs = {}
    i = 0
    for d_vec in doc_vecs_list:
        for doc_id, vec in d_vec.items():
            if doc_id not in doc_vecs.keys():
                doc_vecs[doc_id] = [0] * n_unique
            for j, s in enumerate(vec):
                doc_vecs[doc_id][i+j] = s
        i += len(vec)

    return query_vec, doc_vecs


def extarct_id_tf(docs):
    """
    extract [(Doc ID, TF)...] list from string

    Args:
        docs ([str]): 'id|tf,id|tf,...'
    """

    if len(docs) == 0:
        return []
    docs = docs.split(',')
    ret = []
    for doc in docs:
        doc = doc.split('|')
        # doc_id, tf
        ret.append((int(doc[0]), int(doc[1])))
    return ret
