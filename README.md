# Readme

- data format:
    - Page{id, title, content}
    - Posting{term, postings}
- check data content
    ```bash
    $ python check_data.py
    ID: 0
    Title: Cliniodes insignialis
    Cliniodes insignialis is a moth in the family Crambidae. It was described by James E. Hayden in 2011. ...
    ...

    Term: 'hell'
    List of [Doc ID|TF]:
    283|1,313|1,384|1,837|1,851|1,1609|1,1792|1,1917|1,1919|1,2244|7,2411|1,2427|1,2880|1,3140|1,3565|2,4436|1,4996|1,5073|1,5082|1,6401|2,7354|1,8223|1,8303|1,8306|1,9172|1,9253|1,9708|1

    ```


---
## TODO
1. (about 30% scores) Support tolerant(fuzzy) search. Users may wrongly type some
information or process wild-card queries and the system is required to do fuzzy
search.
2. (about 30% scores) Support several ranking methods. You need to implement at
least five kinds of ranking algorithms. Note that you are not allowed to use the
existing frameworks such as Lucene.
3. (about 20% scores) Speed. Given a query, you need to quickly return the ranked
list. You should show the effectiveness and search time of each ranking algorithm
you implement.
4. (about 20% scores) Provide friendly search system GUI

---
## Some references

### about the data

https://en.wikipedia.org/wiki/Wikipedia:Database_download

https://towardsdatascience.com/wikipedia-data-science-working-with-the-worlds-largest-encyclopedia-c08efbac5f5c

https://stackoverflow.com/questions/63035431/how-do-i-download-and-work-with-wikipedia-data-dumps

https://jamesthorne.co.uk/blog/processing-wikipedia-in-a-couple-of-hours/

https://dkpro.github.io/dkpro-jwpl/HowToGetWikipediaDumps/


### language processing with NLTK
http://www.nltk.org/book/ch01.html


### search engine

https://github.com/benbusby/whoogle-search

https://github.com/trein/simple-search-engine

https://github.com/01joy/news-search-engine



### TF-IDF

https://medium.com/@deangela.neves/how-to-build-a-search-engine-from-scratch-in-python-part-1-96eb240f9ecb



### fussy search

https://github.com/lingz/fast_fuzzy_search

https://github.com/seatgeek/fuzzywuzzy

https://zhuanlan.zhihu.com/p/32929522


### Multi-process programing

https://zhuanlan.zhihu.com/p/46368084


