import sqlite3
import os
from collections import defaultdict


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


class DBManager:
    def __init__(self, page_db, index_db):
        self.page_db = page_db
        self.index_db = index_db
    
        self.index_conn = sqlite3.connect(self.index_db, check_same_thread=False)
        self.page_conn = sqlite3.connect(self.page_db, check_same_thread=False)
        print('Database connected')

    def create_table(self):
        if not os.path.exists(self.page_db):
            conn = sqlite3.connect(self.page_db)
            c = conn.cursor()
            c.execute(''' CREATE TABLE pages(
                    id INTEGER PRIMARY KEY,
                    title TEXT,
                    content TEXT)''')
            conn.commit()
            conn.close()

        if not os.path.exists(self.index_db):
            conn = sqlite3.connect(self.index_db)
            c = conn.cursor()
            c.execute('''CREATE TABLE postings(
                        term TEXT PRIMARY KEY, 
                        docs TEXT)''')
            conn.commit()
            conn.close()

    def create_idx(self):
        try:
            conn = sqlite3.connect(self.index_db)
            c = conn.cursor()
            c.execute('''CREATE INDEX term_index ON postings (term)''')
            conn.commit()
            conn.close()

            # conn = sqlite3.connect(self.page_db)
            # c = conn.cursor()
            # c.execute(''' CREATE INDEX doc_index ON pages (id)''')
            # conn.commit()
            # conn.close()
        except:
            print('index existed')
        else:
            print('Index created')

    def write_pages_to_db(self, pages):
        # conn = sqlite3.connect(self.page_db)
        conn = self.page_conn
        c = conn.cursor()

        for page in pages:
            t = (page.id, page.title, page.text)
            # term, df, doc-list
            c.execute("INSERT INTO pages VALUES (?, ?, ?)", t)

        conn.commit()
        # conn.close()

    def write_postings_to_db(self, postings_lists):
        """
        [summary]

        Args:
            postings_lists:  Dic of {term, Posting}
        """
        # conn = sqlite3.connect(self.index_db)
        conn = self.index_conn
        c = conn.cursor()

        for term, p in postings_lists.items():
            postings = p.get_postings()
            # posting_str = ','.join(map(str, postings))
            posting_str = ','.join(postings)
            item = (term, posting_str)
            try:
                c.execute("INSERT INTO postings VALUES (?, ?)",
                          item)  # term, df, doc-list
            except:  # Existing term
                cursor = c.execute(
                    'SELECT * FROM postings WHERE term=?', (term,))
                row = cursor.fetchone()
                posting_str_before = row[1]
                posting_str = posting_str_before+','+posting_str
                c.execute('UPDATE postings SET docs=? WHERE term=?',
                          (posting_str, term))

            # break

        conn.commit()
        # conn.close()

    def get_vocabs_size(self):
        # conn = sqlite3.connect(self.index_db)
        conn = self.index_conn
        c = conn.cursor()

        cursor = c.execute('SELECT count(1) FROM postings')
        rec = cursor.fetchone()[0]

        # conn.close()
        return rec

    def exist_page(self, iid):
        conn = sqlite3.connect(self.page_db)
        conn = self.page_conn
        c = conn.cursor()

        cursor = c.execute('SELECT * FROM pages WHERE id=?', (iid,))
        row = cursor.fetchone()

        # conn.close()
        return (row is not None)

    def read_pages(self, ids):
        # conn = sqlite3.connect(self.page_db)
        conn = self.page_conn
        c = conn.cursor()

        placeholder = ','.join(['?'] * len(ids))
        query_str = f"SELECT * FROM pages WHERE id in ({placeholder})"
        # print(query_str)
        cursor = c.execute(query_str, list(ids))
        rec = cursor.fetchall()

        # conn.close()
        return rec

    def read_postings(self, terms):
        # conn = sqlite3.connect(self.index_db)
        conn = self.index_conn
        c = conn.cursor()

        placeholder = ','.join(['?'] * len(terms))
        query_str = f"SELECT * FROM postings WHERE term in ({placeholder})"
        # print(query_str)
        cursor = c.execute(query_str, list(terms))

        rec = cursor.fetchall()
        # print(rec)

        # conn.close()
        return rec

    def get_page_size(self):
        # conn = sqlite3.connect(self.page_db)
        conn = self.page_conn
        c = conn.cursor()

        ret = c.execute('SELECT count(1) from pages')
        ret = ret.fetchone()[0]
        # conn.close()

        return ret

    def delete_number_term(self):
        import re

        def match_number(item):
            expr = '^[+-]?[0-9]*([0-9]\\.|[0-9]|\\.[0-9])[0-9]*(e[+-]?[0-9]+)?$'
            return re.match(expr, item) is not None

        conn = sqlite3.connect(self.index_db)
        conn.create_function("IS_NUMBER", 1, match_number)
        c = conn.cursor()

        cursor = c.execute('''
        DELETE FROM postings 
        WHERE IS_NUMBER(term)
        ''')
        conn.commit()
        conn.close()

    def check_term_size(self, length=50):
        # conn = sqlite3.connect(self.index_db)
        conn = self.index_conn

        # def match_alpha(item):
        #     return item.isalpha()
        # conn.create_function("IS_ALPHA", 1, match_alpha)

        c = conn.cursor()

        # ret = c.execute('DELETE from postings where not IS_ALPHA(term)')
        ret = c.execute('SELECT count(1) from postings where length(term) > ?', (length, ))
        print(ret.fetchone()[0])
        ret = c.execute('SELECT term from postings where length(term) > ?', (length, ))
        ret = ret.fetchall()[-10:]
        # conn.commit()
        # conn.close()

        return ret
    
    def __del__(self):
        self.index_conn.close()
        self.page_conn.close()

        print('Database closed')