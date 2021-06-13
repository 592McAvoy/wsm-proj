from db import DBManager
import config

def main():
    db = DBManager(page_db=config.demo_page_db, index_db=config.demo_index_db)
    # db = DBManager(page_db=config.page_db, index_db=config.index_db)s
    print(f'Page size: {db.get_current_max_page_id()+1}')    
    pages = db.read_pages(ids=list(range(3)))
    for page in pages:
        print(f'ID: {page[0]}')
        print(f'Title: {page[1]}')
        print(f'{page[2]}\n')

    print(f'Terms size: {db.get_vocabs_size()}')
    postings = db.read_postings(terms=['hell', 'flow'])
    for p in postings:
        print(f'Term: \'{p[0]}\'')
        print(f'List of [Doc ID|TF]:\n{p[1]}\n')

    


if __name__ == "__main__":
    main()