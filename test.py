import unittest
import numpy as np

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
        querys = [
            "It is a truth", 
            "universally acknowledged",
            "that a single mn in",
            "possession",
            "of a g* fortune",
            "must be in want of a woe",
            "However little",
            "known the feelings or views",
            "of such a man",
            "may be on his",
            " first entering a ",
            "neighbourhood", 
            "this trath is so w*",
            "fixed in the minds",
            "of the sudrounding",
            "families",
            "that he is considered the",
            "rightful",
            "property",
            "of some one",
            " or other of thei",
            " daughters",
            "They attacked h*",
            "in various ways—with",
            "barefaced questions", 
            "ingous suppositions", 
            "and *ant",
            "surmises",
            "but he eluded",
            "the s* of them all", 
            "and tey",
            "were at* ",
            "last oiged",
            "to accept",
            "th* second-hand",
            "intelligence",
            "of their neibour",
            "Lady Lucas",
            "Her report",
            "was highly favourable."
        ]
        print(len(querys))
        fd = open('test_log.txt', 'w')
        for rank_mode in range(1,6):
            time = []
            for case in querys[:]:
                t = self.inventory.search(case, rank_mode=rank_mode, concurrent=True)
                time.append(t)
            time = np.array(time)
            print(time)
            print('Mode {}: max:{:.4f}\tmin:{:.4}\tavg:{:.4}\tstd:{:.4}'.format(
                rank_mode, np.max(time), np.min(time), np.mean(time), np.std(time)
            ), file=fd)
        fd.close()
        
    # def test_book_count(self):
    #     """
    #     Test if all books in test file are loaded to the index.
    #     """
    #     self.inventory.load_books()
    #     self.assertEqual(self.inventory.books_count(), 10)


if __name__ == '__main__':
    unittest.main()