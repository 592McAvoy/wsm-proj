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
    def __init__(self):
        self.db = DBManager(page_db=config.page_db,
                            index_db=config.index_db)
        
        # self.db.create_table()
        self.db.create_idx()
        print(f'Vocab size: {self.db.get_vocabs_size()}')
        print(f'Total Docs: {self.db.get_page_size()}')
       
        
    def set_file(self, file_path):
        self.file_path = file_path

    def run(self, DEBUG=True, concurrent=False):
        start = timer()
        print(f"Load from {self.file_path}...")
        lines = read_data(self.file_path)
        print(f"Load {len(lines)} lines in {timer()-start} s")

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
            n_cpu = os.cpu_count()//4
            # print(f'{n_cpu} CPUs')
            pool = Pool(processes=n_cpu)
            n_part_lines = split(lines, n_cpu)
            results = pool.map(process_lines, n_part_lines)

            pool.close()
            pool.join()

            page_list, dic_list = zip(*results)
            pages = list(itertools.chain(*page_list))

            dic = merge_dics(dic_list)

        print(f'Concurrent processing uses {timer()-start} s')
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

# import sys
# print(sys.getrecursionlimit())
# sys.setrecursionlimit(1500)
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
    current = 'p15824603p17324602'
    proc = ReversePostingListConstuctor()
    
    exit()
    for part in parts:
        if 'test' in part:
            continue
        if current is not None:
            if current not in part:
                continue
            else:
                current = None
                continue
        
        fn = os.path.join(wiki_dir, part)
        proc.set_file(fn)
        # fn = 'data/wiki/partitions/test.ndjson'
        
        proc.run(DEBUG=False, concurrent=True)
