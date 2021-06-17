demo_page_db='data/db/demo-pages.db'
demo_index_db='data/db/demo-index.db'

page_db='data/db/pages.db'
index_db='data/db/index.db'

# search hyper params
max_docs_per_term = 1000
max_return_docs = 5 # make sure max_docs_per_term >> max_return_docs
max_return_docs_firststep = max_return_docs * 10 # at the first step of search, maintain more docs than final docs number

# weighted zone weights
w_title = 0.8
w_body = 0.2 # w_title + w_page = 1