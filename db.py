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
            # posting_str = ','.join(map(str, postings))
            posting_str = ','.join(postings)
            item = (term, posting_str)
            try:
                c.execute("INSERT INTO postings VALUES (?, ?)", item) # term, df, doc-list
            except: # Existing term
                cursor = c.execute('SELECT * FROM postings WHERE term=?', (term,))
                row = cursor.fetchone()
                posting_str_before = row[1]
                posting_str = posting_str_before+','+posting_str
                c.execute('UPDATE postings SET docs=? WHERE term=?', (posting_str, term))
                    
            # break

        conn.commit()
        conn.close()


    def get_vocabs(self):
        conn = sqlite3.connect(self.index_db)
        c = conn.cursor()

        cursor = c.execute('SELECT term FROM postings')
        rec = cursor.fetchall()          
            
        conn.close()
        return rec

    def read_pages(self, ids):
        conn = sqlite3.connect(self.page_db)
        c = conn.cursor()

        rec = []
        for iid in ids:
            cursor = c.execute('SELECT * FROM pages WHERE id=?', (iid,))
            row = cursor.fetchone()            
            rec.append(row)
            
        conn.close()
        return rec
        
    
    def read_postings(self, terms):
        conn = sqlite3.connect(self.index_db)
        c = conn.cursor()

        rec = []
        for term in terms:
            # print(term)
            cursor = c.execute('SELECT * FROM postings WHERE term=?', (term,))
            row = cursor.fetchone()
            if row is None:
                print(f'Term \'{term}\' does not exist')
                row = (term, '')
            rec.append(row)
            

        conn.close()
        return rec

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

