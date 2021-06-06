import sqlite3
import os

class DBManager:
    def __init__(self, page_db, index_db):
        self.page_db = page_db
        self.index_db = index_db

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
                        df INTEGER,
                        docs TEXT)''')
            conn.commit()
            conn.close()       
        

    def write_pages_to_db(self, pages):
        conn = sqlite3.connect(self.page_db)
        c = conn.cursor()
        
        for page in pages:
            t = (page.id, page.title, page.text)
            c.execute("INSERT INTO pages VALUES (?, ?, ?)", t) # term, df, doc-list

        conn.commit()
        conn.close()

    def write_postings_to_db(self, postings_lists):
        """
        [summary]

        Args:
            postings_lists:  Dic of {term, Posting}
        """
        conn = sqlite3.connect(self.index_db)
        c = conn.cursor()

        for term, p in postings_lists.items():
            postings = p.get_postings()
            posting_str = ','.join(map(str, postings))
            item = (term, len(postings), posting_str)
            try:
                c.execute("INSERT INTO postings VALUES (?, ?, ?)", item) # term, df, doc-list
            except: # Existing term
                ret = c.execute('SELECT * FROM postings WHERE term=?', (term,))
                for row in ret:
                    df = row[1]
                    df += len(postings)
                    posting_str_before = row[2]
                    posting_str = posting_str_before+','+posting_str
                    c.execute('UPDATE postings SET df=?, docs=? WHERE term=?', (df, posting_str, term))
                    break
            # break

        conn.commit()
        conn.close()

    def read_page(self, iid):
        conn = sqlite3.connect(self.page_db)
        c = conn.cursor()

        ret = c.execute('SELECT * FROM pages WHERE id=?', (iid,))
        for row in ret:
            print(row)
        conn.close()
        
    
    def read_posting(self, term):
        conn = sqlite3.connect(self.index_db)
        c = conn.cursor()

        ret = c.execute('SELECT * FROM postings WHERE term=?', (term,))
        for row in ret:
            print(row)

        conn.close()
        return row

    def get_current_max_page_id(self):
        conn = sqlite3.connect(self.page_db)
        c = conn.cursor()

        ret = c.execute('SELECT max(id) from pages')
        for row in ret:
            current_id = row[0]
        conn.close()
        
        if current_id is None:
            current_id = -1
        return current_id

