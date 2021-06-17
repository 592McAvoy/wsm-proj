import unittest

from search import SearchManager


class SearchManagerTests(unittest.TestCase):
    """
    Test case for SearchManager class.
    """

    def setUp(self):
        """
        Setup inventory that will be subjected to the tests.
        """
        self.inventory = SearchManager()

    # def test_regular_search(self):
    #     """
    #     Test searching for non wild-card query (including spell correction)
    #     """
    #     test_querys = [
    #         '',
    #         'hello',
    #         'goodbye goodbye',
    #         'sudhdiofhsodifusdoifuhsdofisdufhsasdadoieowie',
    #         '0123',
    #         ',',
    #         '<a> ohhhh <>a     ',
    #         '主语',
    #         # 'one two three four five six seven eight nine ten .... blah blah blah' # cost 91s on reading postings
    #     ]
    #     for query in test_querys:
    #         self.inventory.search(query)
    
    # def test_wildcard_search(self):
    #     """
    #     Test searching for wild-card query
    #     """
    #     test_querys = [
    #         '*',
    #         'ksdjhak* *djisdjas',
    #         'he* ball ball* in earch',
    #         '************'
    #     ]
    #     for query in test_querys:
    #         self.inventory.search(query)

    def test_speed(self):
        query = 'I like apple, banana, pear, peach and one two three'
        self.inventory.search(query, concurrent=False)
        self.inventory.search(query, concurrent=True)

    # def test_book_count(self):
    #     """
    #     Test if all books in test file are loaded to the index.
    #     """
    #     self.inventory.load_books()
    #     self.assertEqual(self.inventory.books_count(), 10)


if __name__ == '__main__':
    unittest.main()