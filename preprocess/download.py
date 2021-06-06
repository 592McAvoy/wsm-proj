
import requests
from bs4 import BeautifulSoup
from timeit import default_timer as timer
import os
# from keras.utils import get_files
import urllib

def main():
    base_url = 'https://dumps.wikimedia.org/enwiki/'
    index = requests.get(base_url).text
    soup_index = BeautifulSoup(index, 'html.parser')

    # Find the links that are dates of dumps
    dumps = [a['href'] for a in soup_index.find_all('a') if 
            a.text == '20210601/']

    dump_url = base_url + dumps[0]

    # Retrieve the html
    dump_html = requests.get(dump_url).text
    # print(dump_html)

    # Convert to a soup
    soup_dump = BeautifulSoup(dump_html, 'html.parser')

    files = []
    for f in soup_dump.find_all('li', {'class': 'file'}):
        text = f.text
        if 'pages-articles.xml.bz2' in text:# and 'index' not in text:
            files.append((text.split()[0], text.split()[1:]))

    print(f'{len(files)}')
            
    files_to_download = files #[f[0] for f in files if '.xml-p' in f[0]]
    print(f'There are {len(files_to_download)} files to download.')
    # print(files_to_download)

    # data_paths = []

    start = timer()
    for f in files_to_download:
        url = dump_url + f[0]
        # download(url, os.path.join('data', f))
        os.system(f'wget {url} -P data')
 
        
    end = timer()
    print(f'{round(end - start)} total seconds elapsed.')

if __name__ == '__main__':
    main()
    
