import json
import nltk
# nltk.download('stopwords')
# nltk.download('punkt')

from db import DBManager

import config
from utils import extract_terms_from_sentence, wash_text, split, merge_dics, process_lines
from multiprocessing import Pool
import os
from timeit import default_timer as timer
import itertools


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

        if self.db.exist_page(lines[0][0]):
            print('Processed before')
            return 

        if DEBUG:
            lines = lines[:1000]

        start = timer()
        if not concurrent:
            pages, dic = process_lines(lines)
            print(f'Sequenctial processing uses {timer()-start} s')
        else:
            n_cpu = os.cpu_count()//2
            # print(f'{n_cpu} CPUs')
            pool = Pool(processes=n_cpu)
            n_part_lines = split(lines, n_cpu)
            results = pool.map(process_lines, n_part_lines)

            pool.close()
            pool.join()

            page_list, dic_list = zip(*results)
            pages = list(itertools.chain(*page_list))

            dic = merge_dics(dic_list)

        
        self.db.write_pages_to_db(pages)
        self.db.write_postings_to_db(dic)
            
            

        # if DEBUG:
        #     self.db.read_pages([0])
        #     self.db.read_postings(['cliniod'])

        print(
            f"File:{self.file_path.split('/')[-1]}:\t{len(pages)} pages processed in {timer()-start} s\n")


def read_data(path='data/wiki/partitions/test.ndjson'):
    data = []
    # Read in list of pages
    with open(path, 'rt') as fin:
        for l in fin.readlines():
            data.append(json.loads(l))
    return data

import sys
print(sys.getrecursionlimit())
sys.setrecursionlimit(1500)
if __name__ == "__main__":
    """
    Processing 941,373 pages in 811s
    Processing 21,229,916 pages needs around 18289.7s (5.1h)
    """
    # text = '<ref> test <ref>'
    # text = wash_text(text)
    # print(text)
    # exit()
    wiki_dir = 'data/wiki/partitions'
    parts = sorted(os.listdir(wiki_dir))
    current = 'p20460153p20570392'
    for part in parts:
        if current is not None:
            if current not in part:
                continue
            else:
                current = None
        
        fn = os.path.join(wiki_dir, part)
        # fn = 'data/wiki/partitions/test.ndjson'
        proc = ReversePostingListConstuctor(file_path=fn)
        proc.run(DEBUG=False, concurrent=True)
